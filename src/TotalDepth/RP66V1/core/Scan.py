import collections
import contextlib
import io
import logging
import math
import sys
import typing

import colorama

from TotalDepth.RP66V1.core import File, LogPass, AbsentValue
from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core import LogicalFile
from TotalDepth.RP66V1.core.LogicalRecord import Encryption
from TotalDepth.RP66V1.core.LogicalRecord import IFLR, EFLR
from TotalDepth.common import Rle, data_table
from TotalDepth.util.bin_file_type import format_bytes


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


# class MinMax:
#     def __init__(self, units):
#         self.units = units
#         self.count = 0
#         self.null = 0
#         self._min = 0
#         self._max = 0
#         self._sum = 0
#         self._ssq = 0
#
#     def add(self, value: typing.Union[typing.Union[float, int], typing.Sequence[typing.Union[float, int]]]) -> None:
#         if isinstance(value, (list, tuple)):
#             for v in value:
#                 self.add(v)
#         else:
#             # TODO: Remove this hack for absent values.
#             # TODO: Huh explain this. Well -999.25 is the common LIS79 value. -999 is the closest to that for signed
#             # integers. -9999.0 has been seen for some resistivity channels that are encoded as a FSINGL.
#             if value not in (-999.25, -999, -9999.0):
#                 if self.count == 0:
#                     self._min = self._max = value
#                 else:
#                     self._min = min(self._min, value)
#                     self._max = max(self._max, value)
#                 self._sum += value
#                 self._ssq += value * value
#                 self.count += 1
#             else:
#                 self.null += 1
#
#     @property
#     def min(self):
#         if self.count == 0:
#             raise AttributeError('No minimum when there is no data.')
#         return self._min
#
#     @property
#     def mean(self):
#         if self.count == 0:
#             raise AttributeError('No mean when there is no data.')
#         return self._sum / self.count
#
#     @property
#     def stddev(self):
#         """
#         The standard deviation.
#         Reference https://en.wikipedia.org/wiki/Standard_deviation#Rapid_calculation_methods
#         """
#         if self.count == 0:
#             raise AttributeError('No stdev when there is no data.')
#         try:
#             return math.sqrt(self.count * self._ssq - self._sum**2) / self.count
#         except ValueError:
#             # TODO: WTF?
#             return 0.0
#
#     @property
#     def max(self):
#         if self.count == 0:
#             raise AttributeError('No maximum when there is no data.')
#         return self._max
#
#     @property
#     def rate(self):
#         if self.count == 0:
#             raise AttributeError('No maximum when there is no data.')
#         return (self.max - self.min) / self.count
#
#     def __str__(self) -> str:
#         if self.count:
#             return f'count: {self.count:12,d} null: {self.null:10,d}' \
#                 f' min: {self.min:12.3f}' \
#                 f' mean: {self.mean:12.3f} stddev: {self.stddev:12.3f}' \
#                 f' max: {self.max:12.3f}' \
#                 f' rate: {self.rate:12.6f}' \
#                 f' {self.units}'
#         return f'count: {self.count:12,d}'
#
#
# class DataSummaryBase:
#     def __init__(self):
#         self.count = 0
#         self.count_encrypted = 0
#         self.total_bytes = 0
#         # dict of {LR_type : total_number_of_bytes, ...}
#         self.lr_type_map: typing.Dict[int, int] = collections.defaultdict(int)
#         # dict of {OBNAME.I : total_number_of_bytes, ...}
#         self.label_total_size_map: typing.Dict[bytes, int] = collections.defaultdict(int)
#         # dict of {OBNAME.I : count_of_records, ...}
#         self.label_count_map: typing.Dict[bytes, int] = collections.defaultdict(int)
#         # dict of {OBNAME.I : set(byte_length), ...}
#         self.label_size_set: typing.Dict[bytes, collections.Counter] = collections.defaultdict(collections.Counter)
#
#     def _add(self, fld: File.FileLogicalData, obj_name_ident: bytes, len_bytes: int) -> None:
#         self.count += 1
#         self.lr_type_map[fld.lr_type] += 1
#         if fld.lr_is_encrypted:
#             self.count_encrypted += 1
#         else:
#             self.total_bytes += len_bytes
#             self.label_total_size_map[obj_name_ident] += len_bytes
#             self.label_size_set[obj_name_ident].update([len_bytes])
#             self.label_count_map[obj_name_ident] += 1
#
#     def _str_lines(self) -> typing.List[str]:
#         ret = [
#             f'Count {self.count:,d} encrypted {self.count_encrypted:,d} total bytes {self.total_bytes:,d}',
#             f'Logical record types and count of them [{len(self.lr_type_map)}]:',
#         ]
#         for k in sorted(self.lr_type_map):
#             ret.append(f'{k:3d} : {self.lr_type_map[k]:8,d}')
#         ret.append(f'Labels [{len(self.label_total_size_map)}]:')
#         if len(self.label_total_size_map) > 0:
#             fw = max(len(str(k)) for k in self.label_total_size_map)
#         else:
#             fw = 1
#         for k in sorted(self.label_total_size_map.keys()):
#             ret.append(f'{str(k):{fw}} count {self.label_count_map[k]:8,d} total bytes {self.label_total_size_map[k]:8,d}')
#         ret.append('Logical record sizes:')
#         for k in sorted(self.label_size_set.keys()):
#             if len(self.label_size_set[k]) > 1:
#                 ret.append(f'Data size distribution for {str(k):{fw}} LRs (size : count):')
#                 for s in sorted(self.label_size_set[k].keys()):
#                     ret.append(f'  {s:8,d} : {self.label_size_set[k][s]}')
#             elif len(self.label_size_set[k]) == 1:
#                 size_key = list(self.label_size_set[k].keys())[0]
#                 ret.append(f'Data size of {str(k):{fw}} LRs are all {size_key} bytes.')
#         return ret
#
#     def __str__(self) -> str:
#         ret = self._str_lines()
#         return '\n'.join(ret)
#
#
# class IFLRDataSummary(DataSummaryBase):
#     def __init__(self):
#         super().__init__()
#         self.frame_range_map: typing.Dict[RepCode.ObjectName, MinMax] = {}
#         self.object_channel_map: typing.Dict[RepCode.ObjectName, typing.Dict[bytes, MinMax]] = {}
#
#     def add(self, fld: File.FileLogicalData, log_pass: LogPass.LogPass) -> None:
#         assert not fld.lr_is_eflr
#         fld.logical_data.rewind()
#         if fld.lr_is_encrypted:
#             lr = Encryption.LogicalRecordSegmentEncryptionPacket(fld.logical_data)
#             self._add(fld, b'', lr.size)
#         else:
#             iflr = IFLR.IndirectlyFormattedLogicalRecord(fld.lr_type, fld.logical_data)
#             ob_name = iflr.object_name
#             len_bytes = len(iflr.bytes)
#             self._add(fld, ob_name, len_bytes)
#             # Frame numbers
#             if ob_name not in self.frame_range_map:
#                 self.frame_range_map[ob_name] = MinMax('')
#                 self.object_channel_map[ob_name] = {}
#             self.frame_range_map[ob_name].add(iflr.frame_number)
#             frame_object: LogPass.FrameArray = log_pass[ob_name.I]
#             channel_values = log_pass.process_IFLR(iflr)
#             for channel, values in zip(frame_object.channels, channel_values):
#                 if channel.ident not in self.object_channel_map[ob_name]:
#                     self.object_channel_map[ob_name][channel.ident] = MinMax(channel.units)
#                 self.object_channel_map[ob_name][channel.ident].add(values)
#
#     def __str__(self) -> str:
#         ret = self._str_lines()
#         # TODO: Add frame range, means __init__(), add() and __str__(). Or create _str_lines():
#         ret.append('')
#         ret.append(f'Log passes [{len(self.frame_range_map)}]:')
#         for k in sorted(self.frame_range_map.keys()):
#             if self.frame_range_map[k].count > 0:
#                 ret.append(f'    {str(k):12} : frame count: {self.frame_range_map[k].count:12,d}'
#                            f' Frame min: {self.frame_range_map[k].min:8,d} max: {self.frame_range_map[k].max:8,d}')
#             for channel in self.object_channel_map[k]:
#                 min_max = self.object_channel_map[k][channel]
#                 ret.append(f'        {str(channel):12} {min_max}')
#         return '\n'.join(ret)
#
#
# class EFLRDataSummary(DataSummaryBase):
#
#     def add(self, fld: File.FileLogicalData) -> None:
#         assert fld.lr_is_eflr
#         fld.logical_data.rewind()
#         if fld.lr_is_encrypted:
#             lr = Encryption.LogicalRecordSegmentEncryptionPacket(fld.logical_data)
#             self._add(fld, b'', lr.size)
#         else:
#             eflr = EFLR.ExplicitlyFormattedLogicalRecord(fld.lr_type, fld.logical_data)
#             ob_name_ident = eflr.set.type
#             len_bytes = len(fld.logical_data)
#             self._add(fld, ob_name_ident, len_bytes)
#
#
# class ScanLogicalFile(LogicalFile.LogicalFile):
#     EFLR_ALWAYS_DUMP = {b'FILE-HEADER', b'ORIGIN'}
#
#     def __init__(self, file_logical_data: File.FileLogicalData,
#                  fhlr: EFLR.ExplicitlyFormattedLogicalRecord, **kwargs):
#         super().__init__(file_logical_data, fhlr)
#         self.eflr_set_type = kwargs.get('eflr_set_type', [])
#         self.iflr_set_type = kwargs.get('iflr_set_type', [])
#         self.iflr_dump = kwargs.get('iflr_dump', False)
#         self.eflr_dump = kwargs.get('eflr_dump', False)
#         self.eflr_summary: EFLRDataSummary = EFLRDataSummary()
#         self.iflr_summary: IFLRDataSummary = IFLRDataSummary()
#         self.dump_strings = []
#         if self._must_dump_eflr(fhlr):
#             self.dump_strings.append(f'EFLR {str(fhlr)}')
#         self.eflr_summary.add(file_logical_data)
#
#     def _must_dump_eflr(self, eflr: EFLR.ExplicitlyFormattedLogicalRecord) -> bool:
#         if eflr.set.type in self.EFLR_ALWAYS_DUMP:
#             return True
#         return self.eflr_dump and len(self.eflr_set_type) == 0 or eflr.set.type in self.eflr_set_type
#
#     # Overload @abc.abstractmethod
#     def add_eflr(self, file_logical_data: File.FileLogicalData,
#                  eflr: EFLR.ExplicitlyFormattedLogicalRecord, **kwargs) -> None:
#         super().add_eflr(file_logical_data, eflr)
#         if self._must_dump_eflr(eflr):
#             self.dump_strings.append(f'EFLR {str(eflr)}')
#         self.eflr_summary.add(file_logical_data)
#
#     # Overload @abc.abstractmethod
#     def add_iflr(self, file_logical_data: File.FileLogicalData,
#                  iflr: IFLR.IndirectlyFormattedLogicalRecord, **kwargs) -> None:
#         super().add_iflr(file_logical_data, iflr)
#         if self.iflr_dump and len(self.iflr_set_type) == 0 or iflr.object_name in self.iflr_set_type:
#             self.dump_strings.append(f'IFLR {str(iflr)}')
#         self.iflr_summary.add(file_logical_data, self.log_pass)
#
#
# class ScanFile(LogicalFile.LogicalFileSequence):
#     # def __init__(self, *args, **kwargs):
#     #     super().__init__(*args, **kwargs)
#
#     # Overload of @abc.abstractmethod
#     def create_logical_file(self,
#                             file_logical_data: File.FileLogicalData,
#                             eflr: EFLR.ExplicitlyFormattedLogicalRecord, **kwargs) -> LogicalFile:
#         return ScanLogicalFile(file_logical_data, eflr, **kwargs)
#
#     # Overload of @abc.abstractmethod
#     def create_eflr(self, file_logical_data: File.FileLogicalData, **kwargs) -> EFLR.ExplicitlyFormattedLogicalRecord:
#         return EFLR.ExplicitlyFormattedLogicalRecord(file_logical_data.lr_type, file_logical_data.logical_data)
#
#     def dump_scan(self, fout: typing.TextIO) -> None:
#         fout.write(str(self.storage_unit_label))
#         fout.write('\n')
#         for l, logical_file in enumerate(self.logical_files):
#             with _output_section_header_trailer(f'Logical File [Index {l} of {len(self.logical_files)}]', '=', os=fout):
#                 for line in logical_file.dump_strings:
#                     fout.write(line)
#                     fout.write('\n')
#                 with _output_section_header_trailer('EFLR Summary', '-', os=fout):
#                     fout.write(str(logical_file.eflr_summary))
#                     fout.write('\n')
#                 with _output_section_header_trailer('IFLR Summary', '-', os=fout):
#                     fout.write(str(logical_file.iflr_summary))
#                     fout.write('\n')


def _write_position_rle(rle: Rle.RLE, fout: typing.TextIO) -> None:
    for r in range(len(rle)):
        rle_item = rle[r]
        fout.write(
            f'Datum: {rle_item.datum:16,d} 0x{rle_item.datum:08x}'
            f' Repeat: {rle_item.repeat:6,d}'
        )
        if rle_item.stride is None:
            fout.write(f' Stride: None')
        else:
            fout.write(f' Stride: {rle_item.stride:6,d} 0x{rle_item.stride:04x}')
        fout.write(f'\n')


def scan_RP66V1_file_visible_records(fobj: typing.BinaryIO, fout: typing.TextIO, **kwargs) -> None:
    """Scans the file reporting Visible Records, optionally Logical Record Segments as well."""
    verbose = kwargs.get('verbose', 0)
    if not verbose:
        fout.write(
            colorama.Fore.YELLOW
            + 'Use -v to see individual records, RLE of LRSH positions and length distribution of LRS.\n'
        )
    with _output_section_header_trailer('RP66V1 Visible and LRSH Records', '*', os=fout):
        lrsh_dump = kwargs['lrsh_dump']
        rp66_file = File.FileRead(fobj)
        vr_position = lr_position = 0
        count_vr = 0
        count_lrsh = 0
        count_lrsh_first = 0
        count_lrsh_type = collections.Counter()
        count_lrsh_length = collections.Counter()
        rle_visible_record_positions = Rle.RLE()
        rle_lrsh_positions = Rle.RLE()
        for visible_record in rp66_file.iter_visible_records():
            vr_stride = visible_record.position - vr_position
            rle_visible_record_positions.add(visible_record.position)
            if verbose:
                fout.write(f'{visible_record} Stride: 0x{vr_stride:08x} {vr_stride:6,d}\n')
            if lrsh_dump:
                for lrsh in rp66_file.iter_LRSHs_for_visible_record(visible_record):
                    count_lrsh_length.update([lrsh.length])
                    if lrsh.is_first:
                        rle_lrsh_positions.add(lrsh.position)
                        count_lrsh_first += 1
                        count_lrsh_type.update([lrsh.record_type])
                        output = colorama.Fore.GREEN + f' {lrsh}'
                    elif lrsh.is_last:
                        output = colorama.Fore.RED + f'  --{lrsh}'
                    else:
                        output = colorama.Fore.YELLOW + f'  ..{lrsh}'
                    if verbose:
                        lr_stride = lrsh.position - lr_position
                        fout.write(f'  {output} Stride: 0x{lr_stride:08x} {lr_stride:6,d}\n')
                    lr_position = lrsh.position
                    count_lrsh += 1
            vr_position = visible_record.position
            count_vr += 1
        with _output_section_header_trailer('Summary of Visible Records', '=', os=fout):
            fout.write(f'Visible records: {count_vr:,d}\n')
            with _output_section_header_trailer('RLE Visible Record Position', '-', os=fout):
                _write_position_rle(rle_visible_record_positions, fout)
        if lrsh_dump:
            with _output_section_header_trailer('Summary of LRSH', '=', os=fout):
                fout.write(f'LRSH: total={count_lrsh:,d} is_first={count_lrsh_first}\n')
                fout.write(f'LRSH: record types and counts (first segments only) [{len(count_lrsh_type)}]:\n')
                for record_type in sorted(count_lrsh_type.keys()):
                    fout.write(f'{record_type:3d} : {count_lrsh_type[record_type]:8,d}\n')
                fout.write(
                    f'LRSH: record lengths and counts (all segments)'
                    f' [{len(count_lrsh_length)}]'
                )
                if len(count_lrsh_length):
                    fout.write(f' range: {min(count_lrsh_length.keys())}...{max(count_lrsh_length.keys())}')
                fout.write(f'\n')
                if verbose:
                    for length in sorted(count_lrsh_length.keys()):
                        fout.write(f'{length:3d} : {count_lrsh_length[length]:8,d}\n')
                    with _output_section_header_trailer('RLE LRSH Position', '-', os=fout):
                        _write_position_rle(rle_lrsh_positions, fout)


def scan_RP66V1_file_logical_data(fobj: typing.BinaryIO, fout: typing.TextIO, **kwargs) -> None:
    """Scans the file reporting the raw Logical Data."""
    verbose = kwargs.get('verbose', 0)
    if not verbose:
        fout.write(colorama.Fore.YELLOW  + 'Use -v to see individual logical data.\n')
    dump_bytes = kwargs.get('dump_bytes', 0)
    dump_raw_bytes = kwargs.get('dump_raw_bytes', 0)
    if not dump_bytes:
        fout.write(colorama.Fore.YELLOW  + 'Use -v and --dump-bytes to see actual first n bytes.\n')
    # Both a dict of {record_type : collections.Counter(length)
    count_eflr_type_length_count = {}
    count_iflr_type_length_count = {}
    with _output_section_header_trailer('RP66V1 Logical Data Summary', '*', os=fout):
        rp66_file = File.FileRead(fobj)
        vr_position = 0
        header = [
            f'{"Visible R":10}',
            f'{"LRSH":10}',
            f'{"Typ":3}',
            f'{" "}',
            f'{"     "}',
            f'{"Length":8}',
        ]
        underline = ['-' * len(h) for h in header]
        if verbose:
            fout.write(' '.join(header) + '\n')
            fout.write(' '.join(underline) + '\n')
        for logical_data in rp66_file.iter_logical_records():
            if logical_data.lr_is_eflr:
                if logical_data.lr_type not in count_eflr_type_length_count:
                    count_eflr_type_length_count[logical_data.lr_type] = collections.Counter()
                count_eflr_type_length_count[logical_data.lr_type].update([len(logical_data)])
            else:
                if logical_data.lr_type not in count_iflr_type_length_count:
                    count_iflr_type_length_count[logical_data.lr_type] = collections.Counter()
                count_iflr_type_length_count[logical_data.lr_type].update([len(logical_data)])
            if verbose:
                messages = [
                    f'0x{logical_data.position.vr_position:08x}' if logical_data.position.vr_position != vr_position else ' ' * 10,
                    f'0x{logical_data.position.lrsh_position:08x}',
                    f'{logical_data.lr_type:3d}',
                    f'{"E" if logical_data.lr_is_eflr else "I"}',
                    f'{"Crypt" if logical_data.lr_is_encrypted else "Plain"}',
                    f'{len(logical_data.logical_data):8,d}',
                ]
                if dump_bytes:
                    if dump_bytes == -1:
                        if dump_raw_bytes:
                            messages.append(str(logical_data.logical_data.bytes))
                        else:
                            messages.append(format_bytes(logical_data.logical_data.bytes))
                    else:
                        if dump_raw_bytes:
                            messages.append(str(logical_data.logical_data.bytes[:dump_bytes]))
                        else:
                            messages.append(format_bytes(logical_data.logical_data.bytes[:dump_bytes]))
                fout.write(' '.join(messages))
                fout.write('\n')
            vr_position = logical_data.position.vr_position
        with _output_section_header_trailer('RP66V1 Logical Data EFLR Summary', '=', os=fout):
            count_total = sum(
                [
                    sum(count_eflr_type_length_count[record_type].values())
                    for record_type in count_eflr_type_length_count
                ]
            )
            fout.write(f'Total number of EFLR records: {count_total:,d}\n')
            length_total_eflr = 0
            for record_type in count_eflr_type_length_count:
                for length, count in count_eflr_type_length_count[record_type].items():
                    length_total_eflr += length * count
            fout.write(f'Total length of EFLR records: {length_total_eflr:,d}\n')
            for record_type in sorted(count_eflr_type_length_count.keys()):
                fout.write(
                    f'EFLR record type {record_type} lengths and count [{len(count_eflr_type_length_count[record_type])}]:\n'
                )
                for length in sorted(count_eflr_type_length_count[record_type]):
                    fout.write(f'{length:10,d}: {count_eflr_type_length_count[record_type][length]:10,d}\n')
        with _output_section_header_trailer('RP66V1 Logical Data IFLR Summary', '=', os=fout):
            count_total = sum(
                [
                    sum(count_iflr_type_length_count[record_type].values())
                    for record_type in count_iflr_type_length_count
                ]
            )
            fout.write(f'Total number of IFLR records: {count_total:,d}\n')
            length_total_iflr = 0
            for record_type in count_iflr_type_length_count:
                for length, count in count_iflr_type_length_count[record_type].items():
                    length_total_iflr += length * count
            fout.write(f'Total length of IFLR records: {length_total_iflr:,d}\n')
            for record_type in sorted(count_iflr_type_length_count.keys()):
                fout.write(
                    f'IFLR record type {record_type} lengths and count [{len(count_iflr_type_length_count[record_type])}]:\n'
                )
                for length in sorted(count_iflr_type_length_count[record_type]):
                    fout.write(f'{length:10,d}: {count_iflr_type_length_count[record_type][length]:10,d}\n')
        fout.write(f'Total length EFLR/IFLR: {length_total_eflr/length_total_iflr:.3%}\n')


def scan_RP66V1_file_EFLR_IFLR(fobj: typing.BinaryIO, fout: typing.TextIO, **kwargs) -> None:
    """Scans the file reporting the individual EFLR and IFLR."""
    verbose = kwargs.get('verbose', 0)
    if not verbose:
        fout.write(colorama.Fore.YELLOW  + 'Use -v to see individual logical data.\n')
    dump_eflr = kwargs.get('eflr_dump', 0)
    eflr_set_type = kwargs.get('eflr_set_type', [])
    dump_iflr = kwargs.get('iflr_dump', 0)
    iflr_set_type = kwargs.get('iflr_set_type', [])
    dump_bytes = kwargs.get('dump_bytes', 0)
    dump_raw_bytes = kwargs.get('dump_raw_bytes', 0)
    if not dump_bytes:
        fout.write(colorama.Fore.YELLOW  + 'Use -v and --dump-bytes to see actual first n bytes.\n')
    with _output_section_header_trailer('RP66V1 EFLR and IFLR Data Summary', '*', os=fout):
        rp66_file = File.FileRead(fobj)
        # TODO: use data_table.format_table
        vr_position = 0
        header = [
            f'{"Visible R":10}',
            f'{"LRSH":10}',
            f'{"Typ":3}',
            f'{" "}',
            f'{"     "}',
            f'{"Length":8}',
        ]
        underline = ['-' * len(h) for h in header]
        if verbose:
            fout.write(' '.join(header) + '\n')
            fout.write(' '.join(underline) + '\n')
        for file_logical_data in rp66_file.iter_logical_records():
            if file_logical_data.lr_is_eflr:
                if file_logical_data.lr_is_encrypted:
                    if verbose:
                        fout.write(colorama.Fore.MAGENTA + f'Encrypted EFLR: {file_logical_data}' + colorama.Style.RESET_ALL)
                    else:
                        fout.write(colorama.Fore.MAGENTA + f'Encrypted EFLR: {file_logical_data.position}' + colorama.Style.RESET_ALL)
                    fout.write('\n')
                else:
                    eflr = EFLR.ExplicitlyFormattedLogicalRecord(file_logical_data.lr_type, file_logical_data.logical_data)
                    if dump_eflr and len(eflr_set_type) == 0 or eflr.set.type in eflr_set_type:
                        lines = str(eflr).split('\n')
                        for i, line in enumerate(lines):
                            if i == 0:
                                fout.write(colorama.Fore.MAGENTA + line + colorama.Style.RESET_ALL)
                            else:
                                fout.write(line)
                            fout.write('\n')
            else:
                # IFLR
                if dump_iflr:
                    if file_logical_data.lr_is_encrypted:
                        if verbose:
                            fout.write(colorama.Fore.MAGENTA + f'Encrypted IFLR: {file_logical_data}' + colorama.Style.RESET_ALL)
                        else:
                            fout.write(colorama.Fore.MAGENTA + f'Encrypted IFLR: {file_logical_data.position}' + colorama.Style.RESET_ALL)
                        fout.write('\n')
                    else:
                        iflr = IFLR.IndirectlyFormattedLogicalRecord(file_logical_data.lr_type, file_logical_data.logical_data)
                        if len(iflr_set_type) == 0 or iflr.object_name.I in iflr_set_type:
                            fout.write(str(iflr))
                            fout.write('\n')


def _scan_log_pass_content(
        rp66_file: File.FileRead,
        visible_record_positions: LogicalFile.VisibleRecordPositions,
        logical_file: LogicalFile.LogicalFile,
        fout: typing.TextIO,
        *,
        frame_spacing) -> None:
    assert logical_file.has_log_pass
    assert frame_spacing >= 1
    lp: LogPass.LogPass = logical_file.log_pass
    frame_array: LogPass.FrameArray
    for fa, frame_array in enumerate(lp.frame_arrays):
        with _output_section_header_trailer(f'Frame Array [{fa}/{len(lp.frame_arrays)}]', '^', os=fout):
            fout.write(str(frame_array))
            fout.write('\n')
            iflrs = logical_file.iflr_position_map[frame_array.ident]
            if len(iflrs):
                if frame_spacing > 1:
                    num_frames = 1 + len(iflrs) // frame_spacing
                else:
                    num_frames = len(iflrs)
                # if num_frames == 0:
                #     num_frames = 1
                # frame_array.init_arrays(len(iflrs))
                frame_array.init_arrays(num_frames)
                interval = (iflrs[-1].x_axis - iflrs[0].x_axis) / len(iflrs)
                fout.write(
                    f'Frames [{len(iflrs)}]'
                    f' from: {float(iflrs[0].x_axis):0.3f}'
                    f' to {float(iflrs[-1].x_axis):0.3f}'
                    f' Interval: {interval:0.3f}'
                    f' {frame_array.x_axis.units}'
                )
                fout.write('\n')
                fout.write(
                    f'Frame spacing: {frame_spacing}'
                    f' number of frames: {num_frames}'
                    f' numpy size: {frame_array.sizeof_array:,d} bytes'
                )
                fout.write('\n')
                for f, (iflr_frame_number, lrsh_position, x_axis) in enumerate(iflrs):
                    # TODO: raise
                    assert f + 1 == iflr_frame_number
                    if f % frame_spacing == 0:
                        vr_position = visible_record_positions.visible_record_prior(lrsh_position)
                        fld: File.FileLogicalData = rp66_file.get_file_logical_data(vr_position, lrsh_position)
                        iflr = IFLR.IndirectlyFormattedLogicalRecord(fld.lr_type, fld.logical_data)
                        frame_array.read(iflr.logical_data, f // frame_spacing)
                frame_table = [['Channel', 'Size', 'Absent', 'Min', 'Mean', 'Std.Dev.', 'Max', 'Units', 'dtype']]
                for channel in frame_array.channels:
                    channel_ident = channel.ident.I.decode("ascii")
                    # arr = channel.array
                    arr = AbsentValue.mask_absent_values(channel.array)
                    frame_table.append(
                        [channel_ident, arr.size,
                         # NOTE: Not the masked array!
                         AbsentValue.count_of_absent_values(channel.array),
                         arr.min(), arr.mean(),
                         arr.std(), arr.max(), channel.units, arr.dtype]
                    )
                fout.write('\n'.join(data_table.format_table(frame_table, heading_underline='-', pad='   ')))
                fout.write('\n')
            else:
                fout.write('No frames.')
            fout.write('\n')


def scan_RP66V1_file_data_content(fobj: typing.BinaryIO, fout: typing.TextIO,
                                  *, rp66v1_path: str, frame_spacing: int, eflr_as_table: bool) -> None:
    """
    Scans all of every EFLR and IFLR in the file using a ScanFile object.
    """
    rp66v1_file = File.FileRead(fobj)
    logical_file_sequence = LogicalFile.LogicalFileSequence(rp66v1_file, rp66v1_path)
    if frame_spacing <= 0:
        raise ValueError(f'Frame spacing must be > 0 not {frame_spacing}')
    with _output_section_header_trailer('RP66V1 File Data Summary', '*', os=fout):
        fout.write(str(logical_file_sequence.storage_unit_label))
        fout.write('\n')
        logical_file: LogicalFile.LogicalFile
        for lf, logical_file in enumerate(logical_file_sequence.logical_files):
            with _output_section_header_trailer(f'Logical File [{lf}/{len(logical_file_sequence.logical_files)}]', '=', os=fout):
                fout.write(str(logical_file))
                fout.write('\n')
                eflr_position: LogicalFile.PositionEFLR
                for e, eflr_position in enumerate(logical_file.eflrs):
                    header = f'EFLR [{e}/{len(logical_file.eflrs)}] at {str(eflr_position.lrsh_position)}'
                    with _output_section_header_trailer(header, '-', os=fout):
                        # fout.write(str(eflr_position.eflr))
                        # fout.write('\n')
                        if eflr_as_table:
                            if eflr_position.eflr.is_key_value():
                                eflr_str_table = eflr_position.eflr.key_values(sort=True)
                            else:
                                eflr_str_table = eflr_position.eflr.table_as_strings(sort=True)
                            fout.write('\n'.join(data_table.format_table(eflr_str_table, heading_underline='-')))
                            fout.write('\n')
                        else:
                            fout.write(eflr_position.eflr.str_long())
                        fout.write('\n')
                # Now the LogPass(s)
                if logical_file.has_log_pass:
                    with _output_section_header_trailer('Log Pass', '-', os=fout):
                        _scan_log_pass_content(
                            rp66v1_file, logical_file_sequence.visible_record_positions,
                            logical_file, fout, frame_spacing=frame_spacing)
                else:
                    fout.write('NO Log Pass for this Logical Record\n')
