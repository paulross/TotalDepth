import re
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1


class ExceptionFile(ExceptionTotalDepthRP66V1):
    pass


class ExceptionEOF(ExceptionFile):
    """Premature EOF."""
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


# Some constants
LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE = 16


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
    """RP66V1 visible records. See See [RP66V1] 2.3.6"""
    VERSION = 0xff01
    NUMBER_OF_BYTES = 4
    MIN_LENGTH = LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE + NUMBER_OF_BYTES

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
        self.position, self.length, self.attributes, self.record_type = self._read(fobj)

    def _read(self, fobj: typing.BinaryIO) -> typing.Tuple[int, int, int, int]:
        position = fobj.tell()
        try:
            length = read_two_bytes_big_endian(fobj)
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
        """Returns a long string of the attributes."""
        # ret = [
        #     'EFLR' if self.is_eflr else 'IFLR',
        #     'first' if self.is_first else '!first',
        #     'last' if self.is_last else '!last',
        #     'encrypted' if self.is_encrypted else 'plain',
        #     'enc_pkt' if self.has_encryption_packet else 'no_enc_pkt',
        #     'chksum' if self.has_checksum else 'no_chksum',
        #     'trailing' if self.has_trailing_length else 'no_trail',
        #     'padding' if self.has_pad_bytes else 'no_padding',
        # ]
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


class FileRead:
    def __init__(self, file: typing.BinaryIO):
        self.file = file
        self.file.seek(0)
        # Do we have TIF markers?
        # The first one must be StorageUnitLabel.SIZE + TIF_SIZE = 92 or 0x5c little endian
        # 0000 0000 0000 0000 5c00 0000
        TIF_PREFIX = b'\x00' * 8 + b'x5c\x00\x00\x00'
        # Read the Storage Unit Label, see [RP66V1] 2.3.2
        self.sul = StorageUnitLabel(self.file.read(StorageUnitLabel.SIZE))
        self.visible_record = VisibleRecord(self.file)

    def _set_file_and_read_first_visible_record(self) -> None:
        self.file.seek(self.sul.SIZE)
        self.visible_record.read(self.file)

    def iter_visible_records(self) -> typing.Sequence[VisibleRecord]:
        """Iterate across the file yielding the Visible Records as VisibleRecord objects."""
        self._set_file_and_read_first_visible_record()
        try:
            while True:
                # Caller could possibly mess with this so make a copy.
                vr = VisibleRecord(None)
                vr.position = self.visible_record.position
                vr.length = self.visible_record.length
                vr.version = self.visible_record.version
                yield vr
                self.file.seek(self.visible_record.position)
                self.visible_record.read_next(self.file)
        except ExceptionVisibleRecordEOF:
            pass

    # def iter_logical_record_segments(self) -> typing.Sequence[LogicalRecordSegmentHeader]:
    #     """Iterate across the file yielding the Logical Record Segments as LogicalRecordSegmentHeader objects."""
    #     self._set_file_and_read_first_visible_record()
    #     try:
    #         while True:
    #             lrsh = LogicalRecordSegmentHeader(self.file)
    #             next_position = lrsh.next_position
    #             yield lrsh
    #             self.file.seek(next_position)
    #             if next_position == self.visible_record.next_position:
    #                 self.visible_record.read_next(self.file)
    #     except (ExceptionVisibleRecordEOF, ExceptionLogicalRecordSegmentHeaderEOF):
    #         pass

    def iter_logical_record_segments(self, vr_given: VisibleRecord) -> typing.Sequence[LogicalRecordSegmentHeader]:
        """
        Iterate across the Visible Record yielding the Logical Record Segments as LogicalRecordSegmentHeader objects.
        """
        self.file.seek(vr_given.position)
        vr = VisibleRecord(self.file)
        assert vr == vr_given
        try:
            while True:
                lrsh = LogicalRecordSegmentHeader(self.file)
                next_position = lrsh.next_position
                yield lrsh
                self.file.seek(next_position)
                if next_position == vr.next_position:
                    break
        except (ExceptionVisibleRecordEOF, ExceptionLogicalRecordSegmentHeaderEOF):
            pass

