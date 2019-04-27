import collections
import contextlib
import io
import logging
import math
import sys
import typing

import colorama

from TotalDepth.RP66V1.core import File
from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core.LogicalFile import LogicalFileBase, LogicalFileSequence
from TotalDepth.RP66V1.core.LogicalRecord import Encryption
from TotalDepth.RP66V1.core.LogicalRecord import LogPass, IFLR, EFLR
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
        try:
            return math.sqrt(self.count * self._ssq - self._sum**2) / self.count
        except ValueError:
            # TODO: WTF?
            return 0.0

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

    def _add(self, fld: File.FileLogicalData, obj_name_ident: bytes, len_bytes: int) -> None:
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
        self.frame_range_map: typing.Dict[RepCode.ObjectName, MinMax] = {}
        self.object_channel_map: typing.Dict[RepCode.ObjectName, typing.Dict[bytes, MinMax]] = {}

    def add(self, fld: File.FileLogicalData, log_pass: LogPass.LogPass) -> None:
        assert not fld.lr_is_eflr
        fld.logical_data.rewind()
        if fld.lr_is_encrypted:
            lr = Encryption.LogicalRecordSegmentEncryptionPacket(fld.logical_data)
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
            frame_object: LogPass.FrameObject = log_pass[ob_name]
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

    def add(self, fld: File.FileLogicalData) -> None:
        assert fld.lr_is_eflr
        fld.logical_data.rewind()
        if fld.lr_is_encrypted:
            lr = Encryption.LogicalRecordSegmentEncryptionPacket(fld.logical_data)
            self._add(fld, b'', lr.size)
        else:
            eflr = EFLR.ExplicitlyFormattedLogicalRecord(fld.lr_type, fld.logical_data)
            ob_name_ident = eflr.set.type
            len_bytes = len(fld.logical_data)
            self._add(fld, ob_name_ident, len_bytes)


class ScanLogicalFile(LogicalFileBase):
    EFLR_ALWAYS_PRINT = set()  # {b'FILE-HEADER', b'ORIGIN'}

    def __init__(self, file_logical_data: File.FileLogicalData,
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
    def add_eflr(self, file_logical_data: File.FileLogicalData,
                 eflr: EFLR.ExplicitlyFormattedLogicalRecordBase, **kwargs) -> None:
        super().add_eflr(file_logical_data, eflr)
        if self._dump_eflr(eflr):
            print('EFLR', eflr)
        self.eflr_summary.add(file_logical_data)

    # Overload @abc.abstractmethod
    def add_iflr(self, file_logical_data: File.FileLogicalData,
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
                            file_logical_data: File.FileLogicalData,
                            eflr: EFLR.ExplicitlyFormattedLogicalRecord, **kwargs) -> LogicalFileBase:
        return ScanLogicalFile(file_logical_data, eflr, **kwargs)

    # Overload of @abc.abstractmethod
    def create_eflr(self, file_logical_data: File.FileLogicalData, **kwargs) -> EFLR.ExplicitlyFormattedLogicalRecordBase:
        return EFLR.ExplicitlyFormattedLogicalRecord(file_logical_data.lr_type, file_logical_data.logical_data)

    def dump(self, fout: io.StringIO) -> None:
        fout.write(str(self.storage_unit_label))
        fout.write('\n')
        for l, logical_file in enumerate(self.logical_files):
            # logical_file.dump()
            with _output_section_header_trailer(f'Logical File [Index {l} of {len(self.logical_files)}]', '=', os=fout):
                with _output_section_header_trailer('EFLR Summary', '-', os=fout):
                    fout.write(str(logical_file.eflr_summary))
                    fout.write('\n')
                with _output_section_header_trailer('IFLR Summary', '-', os=fout):
                    fout.write(str(logical_file.iflr_summary))
                    fout.write('\n')


def scan_RP66V1_file_visible_records(fobj: typing.BinaryIO, **kwargs) -> str:
    """Scans the file reporting Visible Records, optionally Logical Record Segments as well."""
    fout = io.StringIO()
    with _output_section_header_trailer('RP66V1 Visible Record Summary', '*', os=fout):
        lrsh_dump = kwargs['lrsh_dump']
        rp66_file = File.FileRead(fobj)
        vr_position = lr_position = 0
        for visible_record in rp66_file.iter_visible_records():
            vr_stride = visible_record.position - vr_position
            fout.write(f'{visible_record} Stride: 0x{vr_stride:08x} {vr_stride:6,d}')
            fout.write('\n')
            if lrsh_dump:
                for lrsh in rp66_file.iter_LRSHs_for_visible_record(visible_record):
                    lr_stride = lrsh.position - lr_position
                    if lrsh.is_first:
                        output = colorama.Fore.GREEN + f' {lrsh}'
                    elif lrsh.is_last:
                        output = colorama.Fore.RED + f'  --{lrsh}'
                    else:
                        output = colorama.Fore.YELLOW + f'  ..{lrsh}'
                    fout.write(f'  {output} Stride: 0x{lr_stride:08x} {lr_stride:6,d}')
                    fout.write('\n')
                    lr_position = lrsh.position
            vr_position = visible_record.position
    return fout.getvalue()


def scan_RP66V1_file_logical_data(fobj: typing.BinaryIO, **kwargs) -> str:
    """Scans the file reporting the raw Logical Data."""
    fout = io.StringIO()
    with _output_section_header_trailer('RP66V1 Logical Data Summary', '*', os=fout):
        dump_bytes = kwargs.get('dump_bytes', 0)
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
        fout.write(' '.join(header) + '\n')
        fout.write(' '.join(underline) + '\n')
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
            fout.write(' '.join(messages))
            fout.write('\n')
            vr_position = logical_data.position.vr_position
    return fout.getvalue()


def scan_RP66V1_file_logical_records(fobj: typing.BinaryIO, **kwargs) -> str:
    scan_file: ScanFile = ScanFile(fobj, kwargs['rp66v1_path'], **kwargs)
    fout = io.StringIO()
    with _output_section_header_trailer('RP66V1 File Summary', '*', os=fout):
        encrypted_records: bool = kwargs.get('encrypted_records', False)
        if not encrypted_records:
            # fout.write(_colorama_note('Encrypted records omitted. Use -e to show them.\n'))
            fout.write('Encrypted records omitted. Use -e to show them.\n')
        scan_file.dump(fout)
    return fout.getvalue()
