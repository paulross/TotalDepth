"""
Scans a RP66V1 file an prints out the summary.
"""
import argparse
import collections
import contextlib
import logging
import pprint
import sys
import time
import typing

import colorama

from TotalDepth.RP66V1.core.RepCode import ObjectName

colorama.init(autoreset=True)

import TotalDepth.RP66V1.core.File
from TotalDepth.RP66V1.core.LogicalRecord.Encryption import LogicalRecordSegmentEncryptionPacket
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR

from TotalDepth.util.bin_file_type import format_bytes

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


def _write_storage_unit_label(sul: TotalDepth.RP66V1.core.File.StorageUnitLabel, os: typing.TextIO=sys.stdout) -> None:
    os.write('Storage Unit Label:\n')
    os.write(f'Storage Unit Sequence Number: {sul.storage_unit_sequence_number}\n')
    os.write(f'                DLIS Version: {sul.dlis_version}\n')
    os.write(f'      Storage Unit Structure: {sul.storage_unit_structure}\n')
    os.write(f'       Maximum Record Length: {sul.maximum_record_length}\n')
    os.write(f'      Storage Set Identifier: {sul.storage_set_identifier}\n')


def scan_file(path: str, verbose: int, keep_going: bool) -> None:
    with open(path, 'rb') as fobj:
        rp66_file = TotalDepth.RP66V1.core.File.FileRead(fobj)
        print(rp66_file)
        _write_storage_unit_label(rp66_file.sul)

        # for l, lrsh in enumerate(rp66_file.iter_logical_record_segments()):
        #     print('  [{:2d}] {} {}'.format(l, lrsh, lrsh.attribute_str()))
        #     if l > 48:
        #         break
        # print()
        # for v, vr in enumerate(rp66_file.iter_visible_records()):
        #     print('[{:8,d}] {}'.format(v, vr))
        #     for l, lrsh in enumerate(rp66_file.iter_visible_record_logical_record_segments(vr)):
        #         print('  [{:2d}] {} {}'.format(l, lrsh, lrsh.attribute_str()))
        #     if v > 10:
        #         break
        print('Logical Data:')
        for l, file_logical_data in enumerate(rp66_file.iter_logical_records()):
            # print(
            #     '[{:2d}] {} LR type {:3d} {!s:5} len 0x{:04x}    {}'.format(
            #         l, position, lr_type, is_eflr, len(by), format_bytes(by[:16])
            #     )
            # )
            print(file_logical_data)
        # print('Logical Records:')
        # for l, (position, lr_type, is_eflr, by) in enumerate(rp66_file.iter_logical_records()):
        #     if is_eflr:
        #     print(
        #         '[{:2d}] {} LR type {:3d} len 0x{:04x}    {}'.format(
        #             l, position, lr_type, len(by), format_bytes(by[:16])
        #         )
        #     )


class MinMax:
    def __init__(self):
        self.count = 0
        self._min = 0
        self._max = 0

    def add(self, value):
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
            iflr = IFLR.IndirectlyFormattedLogicalRecord(fld.logical_data)
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
                ret.append(f'{str(k):12} : count: {self.frame_range_map[k].count:8,d}'
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


class FileContentsSummary:
    """
    Captures a high level view of the file with information such as date of survey, well name and log summary.
    """
    def __init__(self):
        self.channels: typing.List[ObjectName] = []

    def add_eflr(self, eflr: EFLR.ExplicitlyFormattedLogicalRecord) -> None:
        # TODO: Capture data from EFLRs such as date, lat/long.
        if eflr.set.type == b'CHANNEL':
            assert len(self.channels) == 0
            self.channels = [v.name for v in eflr.objects]
            # print('TRACE: channels', self.channels)

    def add_iflr(self, iflr: IFLR.IndirectlyFormattedLogicalRecord) -> None:
        # TODO: Capture data from IFLRs such as start, stop.
        pass

    def __str__(self) -> str:
        # return ', '.join(str(c.I) for c in self.channels)
        return ', '.join(repr(c) for c in self.channels)
        # return '\n'.join(str(c) for c in self.channels)


def scan_file_logical_records(path: str, **kwargs) -> None:
    encrypted_records: bool = kwargs.get('encrypted_records', False)
    verbose: int = kwargs.get('verbose', 0)
    eflr_set_type = kwargs.get('eflr_set_type', [])
    iflr_set_type = kwargs.get('iflr_set_type', [])
    iflr_dump = kwargs['iflr_dump']
    eflr_dump = kwargs['eflr_dump']
    if not encrypted_records:
        print(_colorama_note('Encrypted records omitted. Use -e to show them.'))
    with open(path, 'rb') as fobj:
        rp66_file = TotalDepth.RP66V1.core.File.FileRead(fobj)
        print(rp66_file)
        _write_storage_unit_label(rp66_file.sul)
        iflr_data_summary: IFLRDataSummary = IFLRDataSummary()
        eflr_data_summary: EFLRDataSummary = EFLRDataSummary()
        file_contents_summary: FileContentsSummary = FileContentsSummary()
        for lr_index, file_logical_data in enumerate(rp66_file.iter_logical_records()):
            # print('TRACE:', lr_index, file_logical_data)
            if file_logical_data.lr_is_eflr:
                eflr_data_summary.add(file_logical_data)
                lr_text_summary = ''
                if file_logical_data.lr_is_encrypted:
                    if encrypted_records:
                        lrsep = LogicalRecordSegmentEncryptionPacket(file_logical_data.logical_data)
                        lr_text_summary = f'EFLR {lrsep}'
                else:
                    eflr = EFLR.ExplicitlyFormattedLogicalRecord(file_logical_data.lr_type, file_logical_data.logical_data)
                    file_contents_summary.add_eflr(eflr)
                    if eflr.set.type in eflr_set_type or '*' in eflr_set_type:
                        lr_text_summary = str(eflr)
                    elif eflr_dump:
                        lr_text_summary = f'LR type: {eflr.lr_type:3d} {str(eflr.set)}' \
                            f' Template size: {len(eflr.template)} Objects: {len(eflr.objects)}'
                if lr_text_summary:
                    if verbose:
                        print(f'[{lr_index:4d}] {file_logical_data.position} {lr_text_summary}')
                    else:
                        print(f'[{lr_index:4d}] {lr_text_summary}')
            else:
                iflr = IFLR.IndirectlyFormattedLogicalRecord(file_logical_data.logical_data)
                file_logical_data.logical_data.rewind()
                # print('TRACE: iflr.object_name.I', iflr.object_name.I)
                if iflr_dump and iflr.object_name.I in iflr_set_type or '*' in iflr_set_type:
                    lr_text_summary = f'{iflr}'
                    if verbose:
                        print(f'[{lr_index:4d}] {file_logical_data.position} {lr_text_summary}')
                    else:
                        print(f'[{lr_index:4d}] {lr_text_summary}')
                file_contents_summary.add_iflr(iflr)
                iflr_data_summary.add(file_logical_data)
        # Finished iteration
        with _output_section_header_trailer('Logical Record Summary', '='):
            with _output_section_header_trailer('File Contents Summary', '-'):
                print(file_contents_summary)
            with _output_section_header_trailer('EFLR Summary', '-'):
                print(eflr_data_summary)
            with _output_section_header_trailer('IFLR Summary', '-'):
                print(iflr_data_summary)



# parser.add_argument(
#         "-d", "--dump",
#         type="str",
#         dest="dump",
#         default='',
#         help="Dump complete data at these integer positions (ws separated, hex/dec). [default: %default]"
#     )


def main() -> int:
    description = """usage: %(prog)s [options] file
Scans a RP66V1 file and dumps data."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = argparse.ArgumentParser(description=description, epilog=__rights__, prog=sys.argv[0])
    parser.add_argument('path', type=str, help='Path to the file.')
    parser.add_argument(
        '--version', action='version', version='%(prog)s Version: ' + __version__,
        help='Show version and exit.'
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
    print('args:', args)

    # Extract log level
    if args.log_level in logging._nameToLevel:
        log_level = logging._nameToLevel[args.log_level]
    else:
        log_level = args.log_level
    # print('Log level:', log_level)
    # Initialise logging etc.
    logging.basicConfig(level=log_level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        #datefmt='%y-%m-%d % %H:%M:%S',
                        stream=sys.stdout)
    clk_start = time.perf_counter()
    # return 0
    if args.path:
        # Your code here
        # scan_file(args.path, args.verbose, args.keep_going)#, retIntDumpList(opts.dump))
        scan_file_logical_records(
            args.path,
            # kwargs
            verbose=args.verbose, encrypted=args.encrypted, keep_going=args.keep_going,
            eflr_set_type=[bytes(v, 'ascii') for v in args.eflr_set_type],
            iflr_set_type=[bytes(v, 'ascii') for v in args.iflr_set_type],
            iflr_dump=args.IFLR,
            eflr_dump=args.EFLR,
        )
        pass
    else:
        print(parser.format_help())
        parser.error("Wrong number of arguments, I need one only.")
        return 1
    clk_exec = time.perf_counter() - clk_start
    print('Execution time = %8.3f (S)' % clk_exec)
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
