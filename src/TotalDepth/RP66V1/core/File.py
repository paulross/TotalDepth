import copy
import re
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1


class ExceptionFile(ExceptionTotalDepthRP66V1):
    pass


class ExceptionEOF(ExceptionFile):
    """Premature EOF."""
    pass


class ExceptionTIF(ExceptionFile):
    pass


class ExceptionTIFEOF(ExceptionTIF):
    pass


class ExceptionStorageUnitLabel(ExceptionFile):
    pass


class ExceptionVisibleRecord(ExceptionFile):
    pass


class ExceptionVisibleRecordEOF(ExceptionVisibleRecord):
    pass


class ExceptionLogicalRecordSegmentHeader(ExceptionFile):
    pass


class ExceptionLogicalRecordSegmentHeaderEOF(ExceptionLogicalRecordSegmentHeader):
    pass


class ExceptionFileRead(ExceptionFile):
    pass

class ExceptionFileReadEOF(ExceptionFileRead):
    pass


# Some constants
LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE = 16
# The first one must be StorageUnitLabel.SIZE + TIF_SIZE = 92 or 0x5c little endian
# 0000 0000 0000 0000 5c00 0000
TIF_FILE_PREFIX = b'\x00' * 4 + b'\x00' * 4 + b'x5c\x00\x00\x00'


class StorageUnitLabel:
    """The Storage Unit Label that must be at the beginning of a file. See [RP66V1] 2.3.2"""
    SIZE = 80
    RE_STORAGE_UNIT_SEQUENCE_NUMBER = re.compile(b'^[0 ]*([1-9]+)$')
    RE_DLIS_VERSION                 = re.compile(b'^(V1.\\d\\d)$')
    RE_STORAGE_UNIT_STRUCTURE       = re.compile(b'^(RECORD)$')
    RE_MAXIMUM_RECORD_LENGTH        = re.compile(b'^[0 ]*([1-9]+)$')
    # FIELDS = (
    #     ('RE_STORAGE_UNIT_SEQUENCE_NUMBER', re.compile(b'^[0 ]*([1-9]+)$'), 4),
    #     ('RE_DLIS_VERSION'                , re.compile(b'^(V1.\\d\\d)$'), 5),
    #     ('RE_STORAGE_UNIT_STRUCTURE'      , re.compile(b'^(RECORD)$'), 6),
    #     ('RE_MAXIMUM_RECORD_LENGTH'       , re.compile(b'^[0 ]*([1-9]+)$'), 5),
    # )

    def __init__(self, by: bytes):
        if len(by) != self.SIZE:
            raise ExceptionStorageUnitLabel(f'Expected {self.SIZE} bytes, got {len(by)}')
        # We do not support TIF markers.
        if by[len(TIF_FILE_PREFIX):] == TIF_FILE_PREFIX:
            raise ExceptionStorageUnitLabel(f'This file appears to have TIF markers, de-TIF the file to read it.')
        m = self.RE_STORAGE_UNIT_SEQUENCE_NUMBER.match(by[:4])
        if m is None:
            raise ExceptionStorageUnitLabel(f'Can not match RE_STORAGE_UNIT_SEQUENCE_NUMBER on {by}')
        self.storage_unit_sequence_number = int(m.group(1))
        m = self.RE_DLIS_VERSION.match(by[4:9])
        if m is None:
            raise ExceptionStorageUnitLabel(f'Can not match RE_DLIS_VERSION on {by}')
        self.dlis_version = m.group(1)
        m = self.RE_STORAGE_UNIT_STRUCTURE.match(by[9:15])
        if m is None:
            raise ExceptionStorageUnitLabel(f'Can not match RE_STORAGE_UNIT_STRUCTURE on {by}')
        self.storage_unit_structure = m.group(1)
        m = self.RE_MAXIMUM_RECORD_LENGTH.match(by[15:20])
        if m is None:
            raise ExceptionStorageUnitLabel(f'Can not match RE_MAXIMUM_RECORD_LENGTH on {by}')
        self.maximum_record_length = int(m.group(1))
        # TODO: Currently no enforcement here. Could check that this is printable ASCII.
        self.storage_set_identifier = by[20:]

    def as_bytes(self) -> bytes:
        ret = b''.join(
            [
                bytes('{:4d}'.format(self.storage_unit_sequence_number), 'ascii'),
                # TODO: Finish this
            ]
        )
        assert len(ret) == self.SIZE
        return ret


def read_one_byte(fobj: typing.BinaryIO) -> int:
    by: bytes = fobj.read(1)
    if len(by) != 1:
        raise ExceptionEOF('Premature EOF.')
    return by[0]


def read_two_bytes_big_endian(fobj: typing.BinaryIO) -> int:
    by: bytes = fobj.read(2)
    if len(by) != 2:
        raise ExceptionEOF('Premature EOF.')
    return by[0] << 8 | by[1]


class VisibleRecord:
    """RP66V1 visible records. See [RP66V1] 2.3.6"""
    VERSION = 0xff01
    NUMBER_OF_BYTES = 4
    MIN_LENGTH = LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE + NUMBER_OF_BYTES
    # [RP66V1] 2.3.6.5 Maximum Visible Record Length is 16,384
    MAX_LENGTH = 0x4000

    def __init__(self, fobj: typing.Union[typing.BinaryIO, None]):
        if fobj is not None:
            self.position, self.length, self.version = self._read(fobj)
        else:
            self.position = self.length = self.version = 0

    def _read(self, fobj: typing.BinaryIO) -> typing.Tuple[int, int, int]:
        position = fobj.tell()
        try:
            length = read_two_bytes_big_endian(fobj)
            version = read_two_bytes_big_endian(fobj)
        except ExceptionEOF:
            raise ExceptionVisibleRecordEOF(f'Visible Record EOF at 0x{position:x}')
        if version != self.VERSION:
            raise ExceptionVisibleRecord(
                f'Visible Record at 0x{position:x} is 0x{version:x}. Was expecting 0x{self.VERSION:x}'
            )
        if length < self.MIN_LENGTH:
            raise ExceptionVisibleRecord(
                f'Visible Record length {length} but minimum is {self.MIN_LENGTH}'
            )
        if length > self.MAX_LENGTH:
            raise ExceptionVisibleRecord(
                f'Visible Record length {length} but maximum is {self.MAX_LENGTH}'
            )
        return position, length, version

    @property
    def next_position(self) -> int:
        return self.position + self.length

    def expects_visible_record(self, fobj: typing.BinaryIO):
        return fobj.tell() == self.pos + self.len

    def read(self, fobj: typing.BinaryIO) -> None:
        """Read a new Visible Record and check it.
        This may throw a ExceptionVisibleRecord."""
        self.position, self.length, self.version = self._read(fobj)

    def read_next(self, fobj: typing.BinaryIO) -> None:
        """Move to next Visible Record and read it.
        This may throw a ExceptionVisibleRecord."""
        fobj.seek(self.next_position)
        self.read(fobj)

    def __format__(self, format_spec) -> str:
        return '<VisibleRecord: position=0x{:08x} length=0x{:04x} version=0x{:04x}>'.format(
            self.position, self.length, self.version
        )

    def __eq__(self, other):
        if other.__class__ == self.__class__:
            return self.position == other.position and self.length == other.length and self.version == other.version
        return NotImplemented


class LogicalRecordSegmentHeader:
    """RP66V1 Logical Record Segment Header. See See [RP66V1] 2.2.2.1"""
    # NUMBER_OF_BYTES = 4
    # MIN_LENGTH = LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE

    def __init__(self, fobj: typing.BinaryIO):
        if fobj is not None:
            self.position, self.length, self.attributes, self.record_type = self._read(fobj)
        else:
            self.position, self.length, self.attributes, self.record_type = 0

    def _read(self, fobj: typing.BinaryIO) -> typing.Tuple[int, int, int, int]:
        position = fobj.tell()
        try:
            length = read_two_bytes_big_endian(fobj)
            # TODO: Raise on minimum length. Maybe make this a read/write property or descriptor
            attributes = read_one_byte(fobj)
            record_type = read_one_byte(fobj)
        except ExceptionEOF:
            raise ExceptionLogicalRecordSegmentHeaderEOF(f'LogicalRecordSegmentHeader EOF at 0x{position:x}')
        return position, length, attributes, record_type

    def read(self, fobj: typing.BinaryIO) -> None:
        """Read a new Logical Record Segment Header.
        This may throw a ExceptionVisibleRecord."""
        self.position, self.length, self.attributes, self.record_type = self._read(fobj)

    def __format__(self, format_spec) -> str:
        return '<LogicalRecordSegmentHeader: position=0x{:08x} length=0x{:04x} attributes=0x{:02x} LR type={:3d}>'.format(
            self.position, self.length, self.attributes, self.record_type
        )

    def attribute_str(self) -> str:
        """Returns a long string of the important attributes."""
        ret = [
            'EFLR' if self.is_eflr else 'IFLR',
        ]
        if self.is_first:
            ret.append('first')
        if self.is_last:
            ret.append('last')
        if self.is_encrypted:
            ret.append('encrypted')
        if self.has_checksum:
            ret.append('checksum')
        if self.has_trailing_length:
            ret.append('trailing length')
        if self.has_pad_bytes:
            ret.append('padding')
        return '-'.join(ret)

    @property
    def next_position(self) -> int:
        return self.position + self.length

    # Attribute access
    @property
    def is_eflr(self) -> bool:
        return self.attributes & 0x80 != 0

    @property
    def is_first(self) -> bool:
        return self.attributes & 0x40 == 0

    @property
    def is_last(self) -> bool:
        return self.attributes & 0x20 == 0

    @property
    def is_encrypted(self) -> bool:
        return self.attributes & 0x10 != 0

    @property
    def has_encryption_packet(self) -> bool:
        return self.attributes & 0x08 != 0

    @property
    def has_checksum(self) -> bool:
        return self.attributes & 0x04 != 0

    @property
    def has_trailing_length(self) -> bool:
        return self.attributes & 0x02 != 0

    @property
    def has_pad_bytes(self) -> bool:
        """Note: Pad bytes will not be visible if the record is encrypted."""
        return self.attributes & 0x01 != 0

    @property
    def must_strip_padding(self) -> bool:
        return self.has_pad_bytes and not self.is_encrypted

    @property
    def logical_data_length(self):
        """Returns the length of the logical data, including padding but excluding the tail."""
        ret = self.length
        if self.has_trailing_length:
            ret -= 2
        if self.has_checksum:
            ret -= 2
        return ret


class FileRead:
    def __init__(self, file: typing.BinaryIO):
        self.file = file
        self.file.seek(0)
        # Read the Storage Unit Label, see [RP66V1] 2.3.2
        self.sul = StorageUnitLabel(self.file.read(StorageUnitLabel.SIZE))
        self.visible_record = VisibleRecord(self.file)
        self.logical_record_segment_header = LogicalRecordSegmentHeader(self.file)
        if not self.logical_record_segment_header.is_first:
            raise ExceptionFileRead('TODO: Error message')

    def _set_file_and_read_first_visible_record(self) -> None:
        self.file.seek(self.sul.SIZE)
        self.visible_record.read(self.file)

    def _set_file_and_read_first_logical_record(self) -> None:
        self._set_file_and_read_first_visible_record()
        self.logical_record_segment_header.read(self.file)

    def _move_to_next_visible_and_logical_record_segment(self, vr_position: int, lrsh_position: int) -> None:
        """Sets the file up to read a LRSH within a Visible Record. It is up to the caller to make sure that
        the values of vr_position and Logical Record Segment Header position are valid, usually as they have
        been created by one of the iteration methods of this class."""
        assert vr_position > 0
        assert lrsh_position > 0
        assert vr_position < lrsh_position
        self.file.seek(vr_position)
        self.visible_record.read_next(self.file)
        self.file.seek(lrsh_position)
        self.logical_record_segment_header = LogicalRecordSegmentHeader(self.file)
        if not self.logical_record_segment_header.is_first:
            raise ExceptionFileRead('TODO: Error message')

    def iter_visible_records(self) -> typing.Sequence[VisibleRecord]:
        """Iterate across the file yielding the Visible Records as VisibleRecord objects."""
        self._set_file_and_read_first_visible_record()
        try:
            while True:
                # Caller could possibly mess with this so make a copy.
                vr = copy.copy(self.visible_record)
                yield vr
                self.file.seek(self.visible_record.position)
                self.visible_record.read_next(self.file)
        except ExceptionVisibleRecordEOF:
            pass

    def _seek_and_read_next_logical_record_segment(self):
        next_position = self.logical_record_segment_header.next_position
        self.file.seek(next_position)
        if next_position == self.visible_record.next_position:
            self.visible_record.read_next(self.file)
        self.logical_record_segment_header.read(self.file)
        # is_first has been checked by __init__

    def iter_logical_record_segments(self) -> typing.Sequence[LogicalRecordSegmentHeader]:
        """Iterate across the file yielding the Logical Record Segments as LogicalRecordSegmentHeader objects."""
        self._set_file_and_read_first_logical_record()
        try:
            while True:
                # Caller could possibly mess with this so make a copy.
                yield copy.copy(self.logical_record_segment_header)
                self._seek_and_read_next_logical_record_segment()
        except (ExceptionVisibleRecordEOF, ExceptionLogicalRecordSegmentHeaderEOF):
            pass

    def iter_visible_record_logical_record_segments(self, vr_given: VisibleRecord) -> typing.Sequence[LogicalRecordSegmentHeader]:
        """
        Iterate across the Visible Record yielding the Logical Record Segments as LogicalRecordSegmentHeader objects.
        TODO: This leaves the file positioned at the next Visible Record.
        """
        self.file.seek(vr_given.position)
        self.visible_record.read(self.file)
        assert self.visible_record == vr_given
        try:
            while True:
                self.logical_record_segment_header.read(self.file)
                yield copy.copy(self.logical_record_segment_header)
                next_position = self.logical_record_segment_header.next_position
                if next_position == self.visible_record.next_position:
                    break
                self.file.seek(next_position)
        except (ExceptionVisibleRecordEOF, ExceptionLogicalRecordSegmentHeaderEOF):
            pass

    def iter_logical_records(self) -> typing.Sequence[typing.Tuple[int, int, bytes]]:
        self._set_file_and_read_first_logical_record()
        try:
            while True:
                # Loop for each yield
                by_array: bytearray = bytearray()
                position = self.logical_record_segment_header.position
                lr_type = self.logical_record_segment_header.record_type
                while True:
                    # Loop for each segment
                    by: bytes = self.file.read(self.logical_record_segment_header.logical_data_length)
                    if len(by) != self.logical_record_segment_header.logical_data_length:
                        raise ExceptionFileReadEOF(
                            f'Premature EOF reading {self.logical_record_segment_header.length} bytes from LRSH at'
                            f' {self.logical_record_segment_header.position}'
                        )
                    # print(f'TRACE read {len(by)} bytes')
                    if self.logical_record_segment_header.must_strip_padding:
                        by = by[:-by[-1]]
                    by_array.extend(by)
                    if self.logical_record_segment_header.is_last:
                        yield position, lr_type, by_array
                        break
                    # FIXME:
                    next_position = self.logical_record_segment_header.next_position
                    self.file.seek(next_position)
                    if next_position == self.visible_record.next_position:
                        self.visible_record.read_next(self.file)
                    self.logical_record_segment_header = LogicalRecordSegmentHeader(self.file)
        except (ExceptionVisibleRecordEOF, ExceptionLogicalRecordSegmentHeaderEOF):
            pass
