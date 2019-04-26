"""
Scans a RP66V1 file an prints out the summary.
"""
import argparse
import collections
import contextlib
import logging
import math
import os
import pprint
import sys
import time
import typing

import colorama

import TotalDepth.RP66V1.core.File
from TotalDepth.RP66V1.core.LogicalFile import LogicalFileBase, LogicalFileSequence
from TotalDepth.RP66V1.core.LogicalRecord.Encryption import LogicalRecordSegmentEncryptionPacket
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR
from TotalDepth.RP66V1.core.LogicalRecord.LogPass import LogPass, FrameObject
from TotalDepth.RP66V1.core.RepCode import ObjectName
from TotalDepth.util.bin_file_type import format_bytes, binary_file_type, BINARY_FILE_TYPE_CODE_WIDTH

colorama.init(autoreset=True)


__author__  = 'Paul Ross'
__date__    = '2019-03-21'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


logger = logging.getLogger(__file__)


STANDARD_TEXT_WIDTH = 132


@contextlib.contextmanager
def _output_section_header_trailer(header: str, fillchar: str,
                                   width: int = STANDARD_TEXT_WIDTH,
                                   os: typing.TextIO = sys.stdout):
    s = colorama.Fore.GREEN + f' {header} '.center(width, fillchar) + '\n'
    os.write(s)
    yield
    s = colorama.Fore.GREEN + f' END {header} '.center(width, fillchar) + '\n'
    os.write(s)


def _colorama_note(msg: str):
    return colorama.Back.YELLOW + f'NOTE: {msg}'


class MinMax:
    def __init__(self, units):
        self.units = units
        self.count = 0
        self.null = 0
        self._min = 0
        self._max = 0
        self._sum = 0
        self._ssq = 0

    def add(self, value: typing.Union[typing.Union[float, int], typing.Sequence[typing.Union[float, int]]]) -> None:
        if isinstance(value, (list, tuple)):
            for v in value:
                self.add(v)
        else:
            # TODO: Remove this hack for absent values.
            if value not in (-999.0, -999.25):
                if self.count == 0:
                    self._min = self._max = value
                else:
                    self._min = min(self._min, value)
                    self._max = max(self._max, value)
                self._sum += value
                self._ssq += value * value
                self.count += 1
            else:
                self.null += 1

    @property
    def min(self):
        if self.count == 0:
            raise AttributeError('No minimum when there is no data.')
        return self._min

    @property
    def mean(self):
        if self.count == 0:
            raise AttributeError('No mean when there is no data.')
        return self._sum / self.count

    @property
    def stddev(self):
        """
        The standard deviation.
        Reference https://en.wikipedia.org/wiki/Standard_deviation#Rapid_calculation_methods
        """
        if self.count == 0:
            raise AttributeError('No stdev when there is no data.')
        return math.sqrt(self.count * self._ssq - self._sum**2) / self.count

    @property
    def max(self):
        if self.count == 0:
            raise AttributeError('No maximum when there is no data.')
        return self._max

    @property
    def rate(self):
        if self.count == 0:
            raise AttributeError('No maximum when there is no data.')
        return (self.max - self.min) / self.count

    def __str__(self) -> str:
        if self.count:
            return f'count: {self.count:12,d} null: {self.null:10,d}' \
                f' min: {self.min:12.3f}' \
                f' mean: {self.mean:12.3f} stddev: {self.stddev:12.3f}' \
                f' max: {self.max:12.3f}' \
                f' rate: {self.rate:12.6f}' \
                f' {self.units}'
        return f'count: {self.count:12,d}'


class DataSummaryBase:
    def __init__(self):
        self.count = 0
        self.count_encrypted = 0
        self.total_bytes = 0
        # dict of {LR_type : total_number_of_bytes, ...}
        self.lr_type_map: typing.Dict[int, int] = collections.defaultdict(int)
        # dict of {OBNAME.I : total_number_of_bytes, ...}
        self.label_total_size_map: typing.Dict[bytes, int] = collections.defaultdict(int)
        # dict of {OBNAME.I : count_of_records, ...}
        self.label_count_map: typing.Dict[bytes, int] = collections.defaultdict(int)
        # dict of {OBNAME.I : set(byte_length), ...}
        self.label_size_set: typing.Dict[bytes, collections.Counter] = collections.defaultdict(collections.Counter)

    def _add(self, fld: TotalDepth.RP66V1.core.File.FileLogicalData, obj_name_ident: bytes, len_bytes: int) -> None:
        self.count += 1
        self.lr_type_map[fld.lr_type] += 1
        if fld.lr_is_encrypted:
            self.count_encrypted += 1
        else:
            self.total_bytes += len_bytes
            self.label_total_size_map[obj_name_ident] += len_bytes
            self.label_size_set[obj_name_ident].update([len_bytes])
            self.label_count_map[obj_name_ident] += 1

    def _str_lines(self) -> typing.List[str]:
        ret = [
            f'Count {self.count:,d} encrypted {self.count_encrypted:,d} total bytes {self.total_bytes:,d}',
            f'Logical record types and count of them [{len(self.lr_type_map)}]:',
        ]
        for k in sorted(self.lr_type_map):
            ret.append(f'{k:3d} : {self.lr_type_map[k]:8,d}')
        ret.append(f'Labels [{len(self.label_total_size_map)}]:')
        if len(self.label_total_size_map) > 0:
            fw = max(len(str(k)) for k in self.label_total_size_map)
        else:
            fw = 1
        for k in sorted(self.label_total_size_map.keys()):
            ret.append(f'{str(k):{fw}} count {self.label_count_map[k]:8,d} total bytes {self.label_total_size_map[k]:8,d}')
        ret.append('Logical record sizes:')
        for k in sorted(self.label_size_set.keys()):
            if len(self.label_size_set[k]) > 1:
                ret.append(f'Data size distribution for {str(k):{fw}} LRs (size : count):')
                for s in sorted(self.label_size_set[k].keys()):
                    ret.append(f'  {s:8,d} : {self.label_size_set[k][s]}')
            elif len(self.label_size_set[k]) == 1:
                size_key = list(self.label_size_set[k].keys())[0]
                ret.append(f'Data size of {str(k):{fw}} LRs are all {size_key} bytes.')
        return ret

    def __str__(self) -> str:
        ret = self._str_lines()
        return '\n'.join(ret)


class IFLRDataSummary(DataSummaryBase):
    def __init__(self):
        super().__init__()
        self.frame_range_map: typing.Dict[ObjectName, MinMax] = {}
        self.object_channel_map: typing.Dict[ObjectName, typing.Dict[bytes, MinMax]] = {}

    def add(self, fld: TotalDepth.RP66V1.core.File.FileLogicalData, log_pass: LogPass) -> None:
        assert not fld.lr_is_eflr
        fld.logical_data.rewind()
        if fld.lr_is_encrypted:
            lr = LogicalRecordSegmentEncryptionPacket(fld.logical_data)
            self._add(fld, b'', lr.size)
        else:
            iflr = IFLR.IndirectlyFormattedLogicalRecord(fld.lr_type, fld.logical_data)
            ob_name = iflr.object_name
            len_bytes = len(iflr.bytes)
            self._add(fld, ob_name, len_bytes)
            # Frame numbers
            if ob_name not in self.frame_range_map:
                self.frame_range_map[ob_name] = MinMax('')
                self.object_channel_map[ob_name] = {}
            self.frame_range_map[ob_name].add(iflr.frame_number)
            frame_object: FrameObject = log_pass[ob_name]
            channel_values = log_pass.process_IFLR(iflr)
            # print('TRACE: values', channel_values)
            for channel, values in zip(frame_object.channels, channel_values):
                if channel.object_name not in self.object_channel_map[ob_name]:
                    self.object_channel_map[ob_name][channel.object_name] = MinMax(channel.units)
                self.object_channel_map[ob_name][channel.object_name].add(values)


    def __str__(self) -> str:
        ret = self._str_lines()
        # TODO: Add frame range, means __init__(), add() and __str__(). Or create _str_lines():
        ret.append('Frame indexes:')
        for k in sorted(self.frame_range_map.keys()):
            if self.frame_range_map[k].count > 0:
                ret.append(f'{str(k):12} : count: {self.frame_range_map[k].count:12,d}'
                           f' Index min: {self.frame_range_map[k].min:8,d} max: {self.frame_range_map[k].max:8,d}')
            for channel in self.object_channel_map[k]:
                min_max = self.object_channel_map[k][channel]
                ret.append(f'  {channel:12} {min_max}')
        return '\n'.join(ret)


class EFLRDataSummary(DataSummaryBase):

    def add(self, fld: TotalDepth.RP66V1.core.File.FileLogicalData) -> None:
        assert fld.lr_is_eflr
        fld.logical_data.rewind()
        if fld.lr_is_encrypted:
            lr = LogicalRecordSegmentEncryptionPacket(fld.logical_data)
            self._add(fld, b'', lr.size)
        else:
            eflr = EFLR.ExplicitlyFormattedLogicalRecord(fld.lr_type, fld.logical_data)
            ob_name_ident = eflr.set.type
            len_bytes = len(fld.logical_data)
            self._add(fld, ob_name_ident, len_bytes)


class ScanLogicalFile(LogicalFileBase):
    EFLR_ALWAYS_PRINT = set()  # {b'FILE-HEADER', b'ORIGIN'}

    def __init__(self, file_logical_data: TotalDepth.RP66V1.core.File.FileLogicalData,
                 fhlr: EFLR.ExplicitlyFormattedLogicalRecord, **kwargs):
        super().__init__(file_logical_data, fhlr)
        # print('TRACE: kwargs', kwargs)
        self.eflr_set_type = kwargs.get('eflr_set_type', [])
        self.iflr_set_type = kwargs.get('iflr_set_type', [])
        self.iflr_dump = kwargs.get('iflr_dump', False)
        self.eflr_dump = kwargs.get('eflr_dump', False)
        self.eflr_summary: EFLRDataSummary = EFLRDataSummary()
        self.iflr_summary: IFLRDataSummary = IFLRDataSummary()
        # if self._dump_eflr():
        if self.eflr_dump and len(self.eflr_set_type) == 0 or fhlr.set.type in self.eflr_set_type:
            print('EFLR', fhlr)
        self.eflr_summary.add(file_logical_data)

    def _dump_eflr(self, eflr: EFLR.ExplicitlyFormattedLogicalRecordBase) -> bool:
        if eflr.set.type in self.EFLR_ALWAYS_PRINT:
            return True
        return self.eflr_dump and len(self.eflr_set_type) == 0 or eflr.set.type in self.eflr_set_type

    # Overload @abc.abstractmethod
    def add_eflr(self, file_logical_data: TotalDepth.RP66V1.core.File.FileLogicalData,
                 eflr: EFLR.ExplicitlyFormattedLogicalRecordBase, **kwargs) -> None:
        super().add_eflr(file_logical_data, eflr)
        if self._dump_eflr(eflr):
            print('EFLR', eflr)
        self.eflr_summary.add(file_logical_data)

    # Overload @abc.abstractmethod
    def add_iflr(self, file_logical_data: TotalDepth.RP66V1.core.File.FileLogicalData,
                 iflr: IFLR.IndirectlyFormattedLogicalRecord, **kwargs) -> None:
        super().add_iflr(file_logical_data, iflr)
        if self.iflr_dump and len(self.iflr_set_type) == 0 or iflr.object_name in self.iflr_set_type:
            print('IFLR', iflr)
        self.iflr_summary.add(file_logical_data, self.log_pass)

    def dump(self) -> None:
        pass


class ScanFile(LogicalFileSequence):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    # Overload of @abc.abstractmethod
    def create_logical_file(self,
                            file_logical_data: TotalDepth.RP66V1.core.File.FileLogicalData,
                            eflr: EFLR.ExplicitlyFormattedLogicalRecord, **kwargs) -> LogicalFileBase:
        return ScanLogicalFile(file_logical_data, eflr, **kwargs)

    # Overload of @abc.abstractmethod
    def create_eflr(self, file_logical_data: TotalDepth.RP66V1.core.File.FileLogicalData, **kwargs) -> EFLR.ExplicitlyFormattedLogicalRecordBase:
        return EFLR.ExplicitlyFormattedLogicalRecord(file_logical_data.lr_type, file_logical_data.logical_data)

    def dump(self) -> None:
        print(self.storage_unit_label)
        for l, logical_file in enumerate(self.logical_files):
            logical_file.dump()
            with _output_section_header_trailer(f'Logical File [Index {l} of {len(self.logical_files)}]', '='):
                with _output_section_header_trailer('EFLR Summary', '-'):
                    print(logical_file.eflr_summary)
                with _output_section_header_trailer('IFLR Summary', '-'):
                    print(logical_file.iflr_summary)


def _scan_RP66V1_file_visible_records(fobj: typing.BinaryIO, **kwargs):
    """Scans the file reporting Visible Records, optionally Logical Record Segments as well."""
    with _output_section_header_trailer('RP66V1 Visible Record Summary', '*'):
        lrsh_dump = kwargs['lrsh_dump']
        rp66_file = TotalDepth.RP66V1.core.File.FileRead(fobj)
        vr_position = lr_position = 0
        for visible_record in rp66_file.iter_visible_records():
            vr_stride = visible_record.position - vr_position
            print(f'{visible_record} Stride: 0x{vr_stride:08x} {vr_stride:6,d}')
            if lrsh_dump:
                for lrsh in rp66_file.iter_LRSHs_for_visible_record(visible_record):
                    lr_stride = lrsh.position - lr_position
                    if lrsh.is_first:
                        output = colorama.Fore.GREEN + f' {lrsh}'
                    elif lrsh.is_last:
                        output = colorama.Fore.RED + f'  --{lrsh}'
                    else:
                        output = colorama.Fore.YELLOW + f'  ..{lrsh}'
                    print(f'  {output} Stride: 0x{lr_stride:08x} {lr_stride:6,d}')
                    lr_position = lrsh.position
            vr_position = visible_record.position


def _scan_RP66V1_file_logical_data(fobj: typing.BinaryIO, **kwargs):
    """Scans the file reporting the raw Logical Data."""
    with _output_section_header_trailer('RP66V1 Logical Data Summary', '*'):
        dump_bytes = kwargs.get('dump_bytes', 0)
        rp66_file = TotalDepth.RP66V1.core.File.FileRead(fobj)
        vr_position = 0
        header = [
            f'{"Visible R":10}',
            f'{"LRSH":10}',
            f'{"Typ":3}',
            f'{" "}',
            f'{"     "}',
            f'{"Length":8}',
        ]
        undeline = ['-' * len(h) for h in header]
        print(' '.join(header))
        print(' '.join(undeline))
        for logical_data in rp66_file.iter_logical_records():
            messages = [
                f'0x{logical_data.position.vr_position:08x}' if logical_data.position.vr_position != vr_position else ' ' * 10,
                f'0x{logical_data.position.lrsh_position:08x}',
                f'{logical_data.lr_type:3d}',
                f'{"E" if logical_data.lr_is_eflr else "I"}',
                f'{"Crypt" if logical_data.lr_is_encrypted else "Plain"}',
                f'{len(logical_data.logical_data):8,d}',
            ]
            if dump_bytes:
                messages.append(format_bytes(logical_data.logical_data[:dump_bytes]))
            print(' '.join(messages))
            vr_position = logical_data.position.vr_position


def _scan_RP66V1_file_logical_records(fobj: typing.BinaryIO, **kwargs):
    scan_file: ScanFile = ScanFile(fobj, kwargs['rp66v1_path'], **kwargs)
    with _output_section_header_trailer('RP66V1 File Summary', '*'):
        encrypted_records: bool = kwargs.get('encrypted_records', False)
        if not encrypted_records:
            print(_colorama_note('Encrypted records omitted. Use -e to show them.'))
        scan_file.dump()


def scan_file(path: str, function: typing.Callable, **kwargs) -> int:
    """
    If the file in the path is a RP66V1 binary file type the given function will be called on it with the **kwargs.
    This returns the number of bytes in the file.
    """
    with open(path, 'rb') as fobj:
        bin_file_type = binary_file_type(fobj)
        if bin_file_type == 'RP66V1':
            # print(f'File: {bin_file_type} at {path}')
            logger.info(f'Procesing file type "{bin_file_type:{BINARY_FILE_TYPE_CODE_WIDTH}}" at {path}')
            try:
                function(fobj, **kwargs)
                return os.path.getsize(path)
            except Exception as err:
                logger.fatal(f'Exception at file position {fobj.tell():d} 0x{fobj.tell():08x} {str(err)}')
                logger.exception(f'{path}')
                return 0
        else:
            logger.info(f' Ignoring file type "{bin_file_type:{BINARY_FILE_TYPE_CODE_WIDTH}}" at {path}')
    return 0


def scan_file_or_dir(path: str, function: typing.Callable, recurse: bool, **kwargs) -> typing.Tuple[int, int]:
    files = 0
    file_bytes = 0
    if os.path.isfile(path):
        file_bytes += scan_file(path, function, **kwargs)
    elif os.path.isdir(path):
        # Process the files in the directory, and sub-directories if recursive
        for name in os.listdir(path):
            child_path = os.path.join(path, name)
            if os.path.isfile(child_path):
                b = scan_file(child_path, function, **kwargs)
                if b > 0:
                    files += 1
                    file_bytes += b
            elif os.path.isdir(child_path):
                if recurse:
                    f, b = scan_file_or_dir(child_path, function, recurse, **kwargs)
                    files += f
                    file_bytes += b
                else:
                    pass  # Do nothing with sub-directories
            else:
                raise Exception(f'Unknown object in path {path}')
    else:
        raise Exception(f'Unknown object in path {path}')
    return files, file_bytes


def main() -> int:
    description = """usage: %(prog)s [options] file
Scans a RP66V1 file and dumps data."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = argparse.ArgumentParser(description=description, epilog=__rights__, prog=sys.argv[0])
    parser.add_argument('path', type=str, help='Path to the file.')
    # parser.add_argument(
    #     '--version', action='version', version='%(prog)s Version: ' + __version__,
    #     help='Show version and exit.'
    # )
    parser.add_argument(
        '-r', '--recurse', action='store_true',
        help='Process files recursively. [default: %(default)s]',
    )
    parser.add_argument(
        '-e', '--encrypted', action='store_true',
        help='Output encrypted Logical Records as well. [default: %(default)s]',
    )
    parser.add_argument(
        '-k', '--keep-going', action='store_true',
        help='Keep going as far as sensible. [default: %(default)s]',
    )
    log_level_help_mapping = ', '.join(
        ['{:d}<->{:s}'.format(level, logging._levelToName[level]) for level in sorted(logging._levelToName.keys())]
    )
    log_level_help = f'Log Level as an integer or symbol. ({log_level_help_mapping}) [default: %(default)s]'
    parser.add_argument(
            "-l", "--log-level",
            # type=int,
            # dest="loglevel",
            default=30,
            help=log_level_help
        )
    parser.add_argument(
        "-v", "--verbose", action='count', default=0,
        help="Increase verbosity, additive [default: %(default)s]",
    )
    parser.add_argument(
        "--eflr-set-type", action='append', default=[],
        help="List of EFLR Set Types to output, additive. Use '*' for all. [default: %(default)s]",
    )
    parser.add_argument(
        "--iflr-set-type", action='append', default=[],
        help="List of IFLR Set Types to output, additive. Use '*' for all. [default: %(default)s]",
    )
    parser.add_argument(
        '-I', '--IFLR', action='store_true',
        help='Dump IFLRs. [default: %(default)s]',
    )
    parser.add_argument(
        '-E', '--EFLR', action='store_true',
        help='Dump EFLR Set. [default: %(default)s]',
    )
    parser.add_argument(
        '-V', '--VR', action='store_true',
        help='Dump the Visible Records. [default: %(default)s]',
    )
    parser.add_argument(
        '-L', '--LRSH', action='store_true',
        help='Dump the Visible Records and the Logical Record Segment Headers. [default: %(default)s]',
    )
    parser.add_argument(
        '-D', '--LD', action='store_true',
        help='Dump logical data. [default: %(default)s]',
    )
    parser.add_argument(
        '-R', '--LR', action='store_true',
        help='Dump Logical Records. [default: %(default)s]',
    )
    parser.add_argument(
        '-d', '--dump-bytes', type=int, default=0,
        help='Dump X leading raw bytes for certain options. [default: %(default)s]',
    )
    args = parser.parse_args()
    print('args:', args)

    # Extract log level
    if args.log_level in logging._nameToLevel:
        log_level = logging._nameToLevel[args.log_level]
    else:
        log_level = int(args.log_level)
    # print('Log level:', log_level)
    # Initialise logging etc.
    logging.basicConfig(level=log_level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        #datefmt='%y-%m-%d % %H:%M:%S',
                        stream=sys.stdout)
    clk_start = time.perf_counter()
    # return 0
    # Your code here
    if args.VR or args.LRSH:
        file_count, file_bytes = scan_file_or_dir(
            args.path,
            _scan_RP66V1_file_visible_records,
            args.recurse,
            # kwargs
            lrsh_dump=args.LRSH,
        )
    if args.LD:
        file_count, file_bytes = scan_file_or_dir(
            args.path,
            _scan_RP66V1_file_logical_data,
            args.recurse,
            # kwargs
            dump_bytes=args.dump_bytes,
        )
    if args.LR or args.EFLR or args.IFLR:
        file_count, file_bytes = scan_file_or_dir(
            args.path,
            _scan_RP66V1_file_logical_records,
            args.recurse,
            # kwargs
            verbose=args.verbose, encrypted=args.encrypted, keep_going=args.keep_going,
            eflr_set_type=[bytes(v, 'ascii') for v in args.eflr_set_type],
            iflr_set_type=[bytes(v, 'ascii') for v in args.iflr_set_type],
            iflr_dump=args.IFLR,
            eflr_dump=args.EFLR,
            rp66v1_path=args.path,
        )
    clk_exec = time.perf_counter() - clk_start
    print('Execution time = %8.3f (S)' % clk_exec)
    if file_bytes > 0:
        ms_mb = clk_exec * 1000 / (file_bytes / 1024**2)
    else:
        ms_mb = 0.0
    print(f'Processed {file_count:,d} files and {file_bytes:,d} bytes, {ms_mb:.1f} ms/Mb')
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
