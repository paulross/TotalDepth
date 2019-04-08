"""
Scans a RP66V1 file an prints out the summary.
"""
import argparse
import collections
import contextlib
import logging
import os
import pprint
import sys
import time
import typing

import colorama

import TotalDepth.RP66V1.core.File
from TotalDepth.RP66V1.core.LogicalRecord.Encryption import LogicalRecordSegmentEncryptionPacket
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR
from TotalDepth.RP66V1.core.LogicalRecord.LogPass import LogPass
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
                                   width: int = STANDARD_TEXT_WIDTH, os: typing.TextIO = sys.stdout):
    s = colorama.Fore.GREEN + f' {header} '.center(width, fillchar) + '\n'
    os.write(s)
    yield
    s = colorama.Fore.GREEN + f' END {header} '.center(width, fillchar) + '\n'
    os.write(s)


def _colorama_note(msg: str):
    return colorama.Back.YELLOW + f'NOTE: {msg}'


class MinMax:
    def __init__(self):
        self.count = 0
        self._min = 0
        self._max = 0

    def add(self, value):
        if isinstance(value, list):
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
                self.count += 1

    @property
    def min(self):
        if self.count == 0:
            raise AttributeError('No minimum when there is no data.')
        return self._min

    @property
    def max(self):
        if self.count == 0:
            raise AttributeError('No maximum when there is no data.')
        return self._max


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
            f'Logical record types [{len(self.lr_type_map)}]:',
        ]
        for k in sorted(self.lr_type_map):
            ret.append(f'{k:3d} : {self.lr_type_map[k]:8,d}')
        ret.append(f'Labels [{len(self.label_total_size_map)}]:')
        fw = max(len(str(k)) for k in self.label_total_size_map)
        for k in sorted(self.label_total_size_map.keys()):
            ret.append(f'{str(k):{fw}} count {self.label_count_map[k]:8,d} total bytes {self.label_total_size_map[k]:8,d}')
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
        self.frame_range_map: typing.Dict[bytes, MinMax] = {}

    def add(self, fld: TotalDepth.RP66V1.core.File.FileLogicalData) -> None:
        assert not fld.lr_is_eflr
        if fld.lr_is_encrypted:
            lr = LogicalRecordSegmentEncryptionPacket(fld.logical_data)
            self._add(fld, b'', lr.size)
        else:
            iflr = IFLR.IndirectlyFormattedLogicalRecord(fld.lr_type, fld.logical_data)
            ob_name_ident = iflr.object_name.I
            len_bytes = len(iflr.bytes)
            self._add(fld, ob_name_ident, len_bytes)
            # Frame numbers
            if ob_name_ident not in self.frame_range_map:
                self.frame_range_map[ob_name_ident] = MinMax()
            self.frame_range_map[ob_name_ident].add(iflr.frame_number)
        fld.logical_data.rewind()

    def __str__(self) -> str:
        ret = self._str_lines()
        # TODO: Add frame range, means __init__(), add() and __str__(). Or create _str_lines():
        ret.append('Frame ranges:')
        for k in sorted(self.frame_range_map.keys()):
            if self.frame_range_map[k].count > 0:
                ret.append(f'{str(k):12} : count: {self.frame_range_map[k].count:12,d}'
                           f' min: {self.frame_range_map[k].min:8,d} max: {self.frame_range_map[k].max:8,d}')
        return '\n'.join(ret)


class EFLRDataSummary(DataSummaryBase):

    def add(self, fld: TotalDepth.RP66V1.core.File.FileLogicalData) -> None:
        assert fld.lr_is_eflr
        if fld.lr_is_encrypted:
            lr = LogicalRecordSegmentEncryptionPacket(fld.logical_data)
            self._add(fld, b'', lr.size)
        else:
            eflr = EFLR.ExplicitlyFormattedLogicalRecord(fld.lr_type, fld.logical_data)
            ob_name_ident = eflr.set.type
            len_bytes = len(fld.logical_data)
            self._add(fld, ob_name_ident, len_bytes)
        fld.logical_data.rewind()


class LogicalFileContentsSummary:
    """
    Captures a high level view of the logical File with information such as date of survey, well name and log summary.
    There may be several Logical Files in a RP66V1 physical file.
    """
    ORIGIN_KEYS = (b'FILE-ID', b'FILE-TYPE', b'CREATION-TIME', b'WELL-NAME', b'FIELD-NAME', b'COMPANY')

    def __init__(self, eflr_file_header: EFLR.ExplicitlyFormattedLogicalRecord):
        assert eflr_file_header.set.type == b'FILE-HEADER'
        self.sequence_number = int(eflr_file_header.objects[0][b'SEQUENCE-NUMBER'].value[0])
        self.id = eflr_file_header.objects[0][b'ID'].value[0].strip()
        self.origin = {}
        # self.channels: typing.List[ObjectName] = []
        self.eflr_channels: typing.Union[None, EFLR.ExplicitlyFormattedLogicalRecord] = None
        self.eflr_frame: typing.Union[None, EFLR.ExplicitlyFormattedLogicalRecord] = None
        self.log_pass: typing.Union[None, LogPass] = None
        # Dict off {FrameObject.ObjectName: {FrameChannel.ObjectName: MinMax, ...}, ...}
        self.object_channel_data_map: typing.Dict[ObjectName, typing.Dict[ObjectName, MinMax]] = {}
        self.eflr_data_summary: EFLRDataSummary = EFLRDataSummary()
        self.iflr_data_summary: IFLRDataSummary = IFLRDataSummary()


    def add_eflr(self, eflr: EFLR.ExplicitlyFormattedLogicalRecord) -> None:
        # TODO: Capture data from EFLRs such as date, lat/long.
        if eflr.set.type == b'ORIGIN':
            assert len(self.origin) == 0
            for k in self.ORIGIN_KEYS:
                if eflr.objects[0][k].value is not None:
                    self.origin[k] = eflr.objects[0][k].value[0]
                else:
                    self.origin[k] = eflr.objects[0][k].value
        elif eflr.set.type == b'CHANNEL':
            assert self.eflr_channels is None
            self.eflr_channels = eflr
        elif eflr.set.type == b'FRAME':
            assert self.eflr_frame is None
            self.eflr_frame = eflr
        if self.eflr_channels is not None and self.eflr_frame is not None:
            if self.log_pass is not None:
                print('DUPLICATE LogPass, WAS:')
                print(self.log_pass)
            # assert self.log_pass is None
            self.log_pass = LogPass(self.eflr_frame, self.eflr_channels)
            self.eflr_frame = None
            self.eflr_channels = None

    def add_iflr(self, iflr: IFLR.IndirectlyFormattedLogicalRecord) -> None:
        assert self.log_pass is not None
        logger.debug(f'add_iflr(): {iflr}')
        object_name = iflr.object_name
        if object_name not in self.object_channel_data_map:
            self.object_channel_data_map[object_name] = {}
        if len(iflr.bytes):
            data = []
            self.log_pass.append(iflr, data)
            # Load the data
            for c, channel in enumerate(self.log_pass[object_name].channels):
                if channel.object_name not in self.object_channel_data_map[object_name]:
                    self.object_channel_data_map[object_name][channel.object_name] = MinMax()
                self.object_channel_data_map[object_name][channel.object_name].add(data[c])
        else:
            logger.warning('Ignoring empty IFLR.')

    def dump(self, os: typing.TextIO=sys.stdout) -> None:
        os.write(f'SEQUENCE NUMBER: {self.sequence_number:d} ID: {self.id}\n')
        os.write('ORIGIN:\n')
        for k in sorted(self.origin.keys()):
            os.write(f'  {str(k):16} : {self.origin[k]}\n')
        os.write(f'{self.log_pass}\n')
        os.write('Frame Data:\n')
        for frame_object_name in sorted(self.object_channel_data_map.keys()):
            os.write(f'  {frame_object_name}:\n')
            for channel_object_name in self.object_channel_data_map[frame_object_name].keys():
                min_max = self.object_channel_data_map[frame_object_name][channel_object_name]
                os.write(f'    {str(channel_object_name):32} :')
                os.write(f' count: {min_max.count:12,d} min: {min_max.min:12.3f} max: {min_max.max:12.3f}')
                os.write('\n')


def _scan_RP66V1_file(fobj: typing.BinaryIO, **kwargs):
    with _output_section_header_trailer('RP66V1 File Summary', '*'):
        encrypted_records: bool = kwargs.get('encrypted_records', False)
        if not encrypted_records:
            print(_colorama_note('Encrypted records omitted. Use -e to show them.'))
        verbose: int = kwargs.get('verbose', 0)
        eflr_set_type = kwargs.get('eflr_set_type', [])
        iflr_set_type = kwargs.get('iflr_set_type', [])
        iflr_dump = kwargs['iflr_dump']
        eflr_dump = kwargs['eflr_dump']
        rp66_file = TotalDepth.RP66V1.core.File.FileRead(fobj)
        # print(rp66_file)
        print(rp66_file.sul)
        # iflr_data_summary: IFLRDataSummary = IFLRDataSummary()
        # eflr_data_summary: EFLRDataSummary = EFLRDataSummary()
        file_contents_summaries: typing.List[LogicalFileContentsSummary] = []
        for lr_index, file_logical_data in enumerate(rp66_file.iter_logical_records()):
            # print('TRACE:', lr_index, file_logical_data)
            if file_logical_data.lr_is_eflr:
                lr_text_summary = ''
                if file_logical_data.lr_is_encrypted:
                    if encrypted_records:
                        lrsep = LogicalRecordSegmentEncryptionPacket(file_logical_data.logical_data)
                        lr_text_summary = f'EFLR {lrsep}'
                else:
                    eflr = EFLR.ExplicitlyFormattedLogicalRecord(
                        file_logical_data.lr_type, file_logical_data.logical_data,
                    )
                    if eflr.set.type == b'FILE-HEADER':
                        file_contents_summaries.append(LogicalFileContentsSummary(eflr))
                    else:
                        assert len(file_contents_summaries) > 0
                        file_contents_summaries[-1].add_eflr(eflr)
                    if eflr.set.type in eflr_set_type or '*' in eflr_set_type:
                        logger.debug(
                            f'EFLR bytes [{len(file_logical_data.logical_data.bytes)}]:'
                            f' {file_logical_data.logical_data.bytes}'
                        )
                        lr_text_summary = f'LR type: {eflr.lr_type:3d} {str(eflr)}'
                    elif eflr_dump:
                        lr_text_summary = f'LR type: {eflr.lr_type:3d} {str(eflr.set)}' \
                            f' Template size: {len(eflr.template)} Objects: {len(eflr.objects)}'
                if lr_text_summary:
                    if verbose:
                        print(f'[{lr_index:4d}] {file_logical_data.position} {lr_text_summary}')
                    else:
                        print(f'[{lr_index:4d}] {lr_text_summary}')
                assert len(file_contents_summaries) > 0
                file_logical_data.logical_data.rewind()
                file_contents_summaries[-1].eflr_data_summary.add(file_logical_data)
            else:
                iflr = IFLR.IndirectlyFormattedLogicalRecord(
                    file_logical_data.lr_type,
                    file_logical_data.logical_data,
                )
                file_logical_data.logical_data.rewind()
                if iflr_dump:
                    if iflr.object_name.I in iflr_set_type or '*' in iflr_set_type or len(iflr_set_type) == 0:
                        logger.debug(
                            f'IFLR bytes [{len(file_logical_data.logical_data.bytes)}]:'
                            f' {file_logical_data.logical_data.bytes}'
                        )
                        lr_text_summary = f'{iflr}'
                        if verbose:
                            print(f'[{lr_index:4d}] {file_logical_data.position} {lr_text_summary}')
                        else:
                            print(f'[{lr_index:4d}] {lr_text_summary}')
                assert len(file_contents_summaries) > 0
                file_contents_summaries[-1].add_iflr(iflr)
                file_logical_data.logical_data.rewind()
                file_contents_summaries[-1].iflr_data_summary.add(file_logical_data)
        # Finished iteration
        with _output_section_header_trailer('Summary', '='):
            for summary in file_contents_summaries:
                with _output_section_header_trailer(
                        f'Logical File Contents Summary Number: {summary.sequence_number} ID: {summary.id}', '-'
                ):
                    summary.dump()
                with _output_section_header_trailer('EFLR Summary', '-'):
                    print(summary.eflr_data_summary)
                with _output_section_header_trailer('IFLR Summary', '-'):
                    print(summary.iflr_data_summary)


def scan_file_logical_records(path: str, **kwargs) -> int:
    with open(path, 'rb') as fobj:
        bin_file_type = binary_file_type(fobj)
        if bin_file_type == 'RP66V1':
            # print(f'File: {bin_file_type} at {path}')
            logger.info(f'Procesing file type "{bin_file_type:{BINARY_FILE_TYPE_CODE_WIDTH}}" at {path}')
            try:
                _scan_RP66V1_file(fobj, **kwargs)
                return os.path.getsize(path)
            except Exception:
                logger.error(f'Exception at file position {fobj.tell():d} 0x{fobj.tell():08x}')
                logger.exception(f'{path}')
                return 0
        else:
            logger.info(f' Ignoring file type "{bin_file_type:{BINARY_FILE_TYPE_CODE_WIDTH}}" at {path}')
    return 0


def scan_file_or_dir_logical_records(path: str, recurse: bool, **kwargs) -> typing.Tuple[int, int]:
    files = 0
    file_bytes = 0
    if os.path.isfile(path):
        file_bytes += scan_file_logical_records(path, **kwargs)
    elif os.path.isdir(path):
        # Process the files in the directory, and sub-directories if recursive
        for name in os.listdir(path):
            child_path = os.path.join(path, name)
            if os.path.isfile(child_path):
                b = scan_file_logical_records(child_path, **kwargs)
                if b > 0:
                    files += 1
                    file_bytes += b
            elif os.path.isdir(child_path):
                if recurse:
                    f, b = scan_file_or_dir_logical_records(child_path, recurse, **kwargs)
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
        help='Output encrypted records as well. [default: %(default)s]',
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
    args = parser.parse_args()
    # print('args:', args)

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
    # scan_file_logical_records(
    #     args.path,
    #     # kwargs
    #     verbose=args.verbose, encrypted=args.encrypted, keep_going=args.keep_going,
    #     eflr_set_type=[bytes(v, 'ascii') for v in args.eflr_set_type],
    #     iflr_set_type=[bytes(v, 'ascii') for v in args.iflr_set_type],
    #     iflr_dump=args.IFLR,
    #     eflr_dump=args.EFLR,
    # )
    file_count, file_bytes = scan_file_or_dir_logical_records(
        args.path,
        args.recurse,
        # kwargs
        verbose=args.verbose, encrypted=args.encrypted, keep_going=args.keep_going,
        eflr_set_type=[bytes(v, 'ascii') for v in args.eflr_set_type],
        iflr_set_type=[bytes(v, 'ascii') for v in args.iflr_set_type],
        iflr_dump=args.IFLR,
        eflr_dump=args.EFLR,
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
