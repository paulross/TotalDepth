"""
Scans a RP66V1 file an prints out the summary.
"""
import argparse
import collections
import logging
import pprint
import sys
import time
import typing

import TotalDepth.RP66V1.core.File
from TotalDepth.RP66V1.core.LogicalRecord.Encryption import LogicalRecordSegmentEncryptionPacket
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR

from TotalDepth.util.bin_file_type import format_bytes

__author__  = 'Paul Ross'
__date__    = '2019-03-21'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


logger = logging.getLogger(__file__)


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

    def __str__(self) -> str:
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
                ret.append(f'Size distribution for {str(k):{fw}} (size : count):')
                for s in sorted(self.label_size_set[k].keys()):
                    ret.append(f'  {s:8,d} : {self.label_size_set[k][s]}')
        return '\n'.join(ret)


class IFLRDataSummary(DataSummaryBase):

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
        fld.logical_data.rewind()


class EFLRDataSummary(DataSummaryBase):

    def add(self, fld: TotalDepth.RP66V1.core.File.FileLogicalData) -> None:
        assert fld.lr_is_eflr
        if fld.lr_is_encrypted:
            lr = LogicalRecordSegmentEncryptionPacket(fld.logical_data)
            self._add(fld, b'', lr.size)
        else:
            eflr = EFLR.ExplicitlyFormattedLogicalRecord(fld.logical_data)
            ob_name_ident = eflr.set.type
            len_bytes = len(fld.logical_data)
            self._add(fld, ob_name_ident, len_bytes)
        fld.logical_data.rewind()


def scan_file_logical_records(path: str, verbose: int, keep_going: bool) -> None:
    with open(path, 'rb') as fobj:
        rp66_file = TotalDepth.RP66V1.core.File.FileRead(fobj)
        print(rp66_file)
        _write_storage_unit_label(rp66_file.sul)
        # print('Logical Data:')
        # lr_type_count = {
        #     'EFLR': collections.Counter(),
        #     'EFLR_encrypted': collections.Counter(),
        #     'IFLR': collections.Counter(),
        #     'IFLR_encrypted': collections.Counter(),
        # }
        # # dict of {set_type : count, }
        # eflr_set_types: typing.Dict[bytes, int] = collections.Counter()
        # dict of {OBNAME.I : total_number_of_bytes, ...}
        iflr_data_summary: IFLRDataSummary = IFLRDataSummary()
        eflr_data_summary: EFLRDataSummary = EFLRDataSummary()
        for l, file_logical_data in enumerate(rp66_file.iter_logical_records()):
            # print(file_logical_data)
            if file_logical_data.lr_is_eflr:
                eflr_data_summary.add(file_logical_data)
                if file_logical_data.lr_is_encrypted:
                    # lr_type_count['EFLR_encrypted'].update([file_logical_data.lr_type])
                    lrsep = LogicalRecordSegmentEncryptionPacket(file_logical_data.logical_data)
                    print(f'{file_logical_data}')
                    print(f'EFLR {lrsep}')
                else:
                    # lr_type_count['EFLR'].update([file_logical_data.lr_type])
                    lr = EFLR.ExplicitlyFormattedLogicalRecord(file_logical_data.logical_data)
                    if lr.set.type in (b'FILE-HEADER', b'ORIGIN'):#b'440-OP-CHANNEL':#b'FRAME':
                        print(file_logical_data)
                        print(lr)
                    else:
                        print(file_logical_data)
                        print(lr.set)
                    # eflr_set_types.update([lr.set.type])
            else:
                iflr_data_summary.add(file_logical_data)
                # if file_logical_data.lr_is_encrypted:
                #     lr_type_count['IFLR_encrypted'].update([file_logical_data.lr_type])
                #     lr = LogicalRecordSegmentEncryptionPacket(file_logical_data.logical_data)
                # else:
                #     lr_type_count['IFLR'].update([file_logical_data.lr_type])
                #     lr = IFLR.IndirectlyFormattedLogicalRecord(file_logical_data.logical_data)
                # ob_name_ident = lr.object_name.I
                # if ob_name_ident not in iflr_data_map:
                #     iflr_data_map[ob_name_ident] = 0
                # iflr_data_map[ob_name_ident] += len(lr.bytes)
                # print(lr)
        # print(lr_type_count)
        print('EFLR Summary:')
        print(eflr_data_summary)
        # for k in sorted(eflr_set_types.keys()):
        #     # set_type = k.decode('ascii')
        #     print(f'{str(k):32} : {eflr_set_types[k]:4,d}')
        print('IFLR Summary:')
        print(iflr_data_summary)
        # for k in sorted(iflr_data_map.keys()):
        #     # channel = k.decode('ascii')
        #     print(f'{str(k):32} : {iflr_data_map[k]:12,d}')
        print()
        # for k in sorted(lr_type_count.keys()):
        #     if len(lr_type_count[k]) > 0:
        #         print(f'{k}:')
        #         for lr_code in sorted(lr_type_count[k].keys()):
        #             print(f'{lr_code:3d} {lr_type_count[k][lr_code]:8,d}')



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
    args = parser.parse_args()
    print(args)

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
        scan_file_logical_records(args.path, args.verbose, args.keep_going)#, retIntDumpList(opts.dump))
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
