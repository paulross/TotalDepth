import copy
import hashlib
import io
import logging
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
# from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core.StorageUnitLabel import StorageUnitLabel, ExceptionStorageUnitLabel
from TotalDepth.util.bin_file_type import format_bytes


logger = logging.getLogger(__file__)


class ExceptionFile(ExceptionTotalDepthRP66V1):
    pass


class ExceptionEOF(ExceptionFile):
    """Premature EOF."""
    pass


class ExceptionTIF(ExceptionFile):
    pass


class ExceptionTIFEOF(ExceptionTIF):
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


# ---------------- Low Level File Read Functions ------------------


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


def read_n_bytes(fobj: typing.BinaryIO, length: int) -> bytes:
    by: bytes = fobj.read(length)
    if len(by) != length:
        raise ExceptionEOF('Premature EOF.')
    return by


# def read_UVARI(fobj: typing.BinaryIO) -> bytes:
#     # Will raise
#     by: bytes = read_n_bytes(fobj, 1)
#     length = RepCode.UVARI_len(by, 0)
#     assert length != 0
#     if length != 1:
#         return by + read_n_bytes(fobj, length - 1)
#     return by
#
#
# def read_IDENT(fobj: typing.BinaryIO) -> bytes:
#     # Will raise
#     by: bytes = read_n_bytes(fobj, 1)
#     length = RepCode.IDENT_len(by, 0)
#     assert length > 0
#     if length != 1:
#         return by + read_n_bytes(fobj, length - 1)
#     return by
#
#
# def read_OBNAME(fobj: typing.BinaryIO) -> bytes:
#     parts: typing.List[bytes] = [
#         read_UVARI(fobj),
#         # Count as a USHORT
#         read_n_bytes(fobj, 1),
#         read_IDENT(fobj),
#     ]
#     return b''.join(parts)
#
#
# def read_IFLR_obname_frame_and_first_channel(fobj: typing.BinaryIO) -> bytes:
#     parts: typing.List[bytes] = [
#         read_OBNAME(fobj),
#         # Frame number as a UVARI
#         read_UVARI(fobj),
#         # First channel is X axis as a scalar.
#         read_n_bytes(fobj, RepCode.LENGTH_LARGEST_INDEX_CHANNEL_CODE),
#     ]
#     return b''.join(parts)

# ---------------- END: Low Level File Read Functions ------------------


# Some constants
LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE = 16


class VisibleRecord:
    """
    RP66V1 visible records. See [RP66V1 Section 2.3.6]
    (sic) - Place marker for error in the standard in this case
    """
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
    """RP66V1 Logical Record Segment Header. See See [RP66V1 2.2.2.1]"""
    HEAD_LENGTH = 4
    # MIN_LENGTH = LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE

    def __init__(self, fobj: typing.BinaryIO):
        self.position, self.length, self.attributes, self.record_type = self._read(fobj)

    def _read(self, fobj: typing.BinaryIO) -> typing.Tuple[int, int, int, int]:
        position = fobj.tell()
        try:
            length = read_two_bytes_big_endian(fobj)
            # TODO: Raise on minimum length. Maybe make this a read/write property or descriptor
            attributes = read_one_byte(fobj)
            # TODO: Raise on attribute conflicts, for example:
            # If encryption packet then encryption must be set
            # Compare successors with previous - trailing length must be all or nothing, encryption all or nothing.
            record_type = read_one_byte(fobj)
        except ExceptionEOF:
            raise ExceptionLogicalRecordSegmentHeaderEOF(f'LogicalRecordSegmentHeader EOF at 0x{position:x}')
        return position, length, attributes, record_type

    def read(self, fobj: typing.BinaryIO) -> None:
        """Read a new Logical Record Segment Header.
        This may throw a ExceptionVisibleRecord."""
        self.position, self.length, self.attributes, self.record_type = self._read(fobj)

    def __format__(self, format_spec) -> str:
        return '<LogicalRecordSegmentHeader: position=0x{:08x} length=0x{:04x}' \
               ' attributes=0x{:02x} LR type={:3d}>'.format(
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
        """File position of the start of the next Logical Record Segment Header."""
        return self.position + self.length

    @property
    def logical_data_position(self) -> int:
        """File position of the start of the Logical Data."""
        return self.position + self.HEAD_LENGTH

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
        ret = self.length - self.HEAD_LENGTH
        if self.has_checksum:
            ret -= 2
        if self.has_trailing_length:
            ret -= 2
        return ret


class LogicalRecordPosition:
    def __init__(self, vr: VisibleRecord, lrsh: LogicalRecordSegmentHeader):
        # Check VisibleRecord
        if vr.position < StorageUnitLabel.SIZE:
            raise ValueError(f'VisibleRecord at 0x{lrsh.position:x} must be >= 0x{StorageUnitLabel.SIZE:x}')
        if vr.length < LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE:
            raise ValueError(
                f'VisibleRecord at 0x{vr.position:x} length 0x{vr.length:x}'
                f' must be >= 0x{LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE:x}'
            )
        if vr.length > VisibleRecord.MAX_LENGTH:
            raise ValueError(
                f'VisibleRecord at 0x{vr.position:x} length 0x{vr.length:x} must be <= 0x{VisibleRecord.MAX_LENGTH:x}'
            )
        # Check LogicalRecordSegmentHeader
        if lrsh.position < StorageUnitLabel.SIZE + VisibleRecord.NUMBER_OF_BYTES:
            raise ValueError(
                f'LogicalRecordSegmentHeader at 0x{lrsh.position:x} must be'
                f' >= 0x{StorageUnitLabel.SIZE + VisibleRecord.NUMBER_OF_BYTES:x}'
            )
        if lrsh.position > vr.position + vr.length - LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE:
            raise ValueError(
                f'LogicalRecordSegmentHeader at 0x{lrsh.position:x} must be'
                f' <= 0x{vr.position + vr.length - LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE:x}'
            )
        if lrsh.length < LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE:
            raise ValueError(
                f'LogicalRecordSegmentHeader at 0x{lrsh.position:x} length 0x{lrsh.length:x} must be'
                f' >= 0x{LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE:x}'
            )
        if lrsh.length > vr.length - VisibleRecord.NUMBER_OF_BYTES:
            raise ValueError(
                f'LogicalRecordSegmentHeader at 0x{lrsh.position:x} length 0x{lrsh.length:x} must be'
                f' <= 0x{vr.length - VisibleRecord.NUMBER_OF_BYTES:x}'
            )
        if not lrsh.is_first:
            raise ValueError(
                f'LogicalRecordSegmentHeader at 0x{lrsh.position:x} must be the first in the sequence of segments.'
            )
        self.vr_position: int = vr.position
        self.lrsh_position: int = lrsh.position

    def __str__(self):
        return f'VR: 0x{self.vr_position:08x} LRSH 0x{self.lrsh_position:08x}'


class LogicalData:
    """Class that holds data bytes and can successively read them."""
    def __init__(self, by: bytes):
        # TODO: Performance, make this a list of bytes like a rope???
        self.bytes: bytes = by
        self.index: int = 0
        self._sha1: typing.Union[hashlib.sha1, None] = None

    def peek(self) -> int:
        """Return the next bytes without incrementing the index."""
        # raise IndexError(f'IndexError: index out of range {self.index} on length {len(self.bytes)}')
        return self.bytes[self.index]

    def read(self) -> int:
        """Return the next bytes and increment the index."""
        ret = self.bytes[self.index]
        self.index += 1
        return ret

    def chunk(self, length: int) -> bytes:
        """Return the next length bytes and increment the index."""
        ret = self.bytes[self.index:self.index + length]
        self.index += length
        return ret

    @property
    def remain(self) -> int:
        if len(self.bytes) > self.index:
            return len(self.bytes) - self.index
        return 0

    @property
    def sha1(self) -> hashlib.sha1:
        if self._sha1 is None:
            self._sha1 = hashlib.sha1(self.bytes)
        return self._sha1

    def rewind(self) -> None:
        self.index = 0

    def __bool__(self):
        return self.remain > 0

    def __len__(self):
        return len(self.bytes)

    def __getitem__(self, item):
        return self.bytes[item]

    def __str__(self) -> str:
        return f'<LogicalData Len: 0x{len(self.bytes):0x} Idx: 0x{self.index:0x} Bytes: {format_bytes(self.bytes[:16])}>'


class FileLogicalData:
    """
    Class that contains information about a Logical Record within a physical file.
    This is lazily evaluated with only the VisibleRecord and LogicalRecordSegmentHeader
    provided to the constructor.
    Eager evaluation is done with one or more add()'s followed by a seal().
    """
    def __init__(self, vr: VisibleRecord, lrsh: LogicalRecordSegmentHeader):
        self.position = LogicalRecordPosition(vr, lrsh)
        # self.visible_records = [vr]
        self.lr_type: int = lrsh.record_type
        self.lr_is_eflr: bool = lrsh.is_eflr
        self.lr_is_encrypted: bool = lrsh.is_encrypted
        self._bytes: typing.Union[None, bytearray] = bytearray()
        self.logical_data: typing.Union[None, LogicalData] = None

    def _invariants(self) -> bool:
        return (self._bytes is None) != (self.logical_data is None)

    def add_bytes(self, by: bytes) -> None:
        assert self._invariants()
        self._bytes.extend(by)

    def truncate(self, index: int) -> None:
        assert self._invariants()
        # TODO: Specialise the exceptions?
        if self._bytes is None:
            raise ValueError('FileLogicalData: Can not truncate after seal()')
        if index > len(self._bytes):
            raise IndexError(f'FileLogicalData: Can not truncate to index {index} when length of bytes is {len(self._bytes)}')
        self._bytes = self._bytes[:index]

    def seal(self):
        assert self._invariants()
        if self.is_sealed():
            raise ValueError('FileLogicalData: Can not seal() after seal()')
        # TODO: Review the cost of this copy. Maybe a list of bytes, like a rope.
        self.logical_data = LogicalData(bytes(self._bytes))
        self._bytes = None

    def is_sealed(self) -> bool:
        assert self._invariants()
        return self._bytes is None

    def __len__(self) -> int:
        assert self._invariants()
        if self._bytes is None:
            return len(self.logical_data)
        return len(self._bytes)

    def __str__(self) -> str:
        assert self._invariants()
        DUMP_BYTE_LEN = 16
        lr_is_eflr = 'E' if self.lr_is_eflr else 'I'
        lr_is_encrypted = 'y' if self.lr_is_encrypted else 'n'
        position = str(self.position)
        if self.logical_data is None:
            return f'<FileLogicalData {position} LR type {self.lr_type:3d} {lr_is_eflr} {lr_is_encrypted}' \
                f' PARTIAL READ: len 0x{len(self._bytes):04x} Idx 0x{self.logical_data.index:04x}' \
                f'  {format_bytes(bytes(self._bytes[:DUMP_BYTE_LEN]))}>'
        return f'<FileLogicalData {position} LR type {self.lr_type:3d} {lr_is_eflr} {lr_is_encrypted}' \
            f' len 0x{len(self.logical_data):04x} Idx 0x{self.logical_data.index:04x}' \
            f'  {format_bytes(self.logical_data.bytes[:DUMP_BYTE_LEN])}>'


class FileRead:
    def __init__(self, file: typing.BinaryIO):
        self.file = file
        self.file.seek(0)
        # Read the Storage Unit Label, see [RP66V1] 2.3.2
        try:
            self.sul = StorageUnitLabel(self.file.read(StorageUnitLabel.SIZE))
        except ExceptionStorageUnitLabel as err:
            raise ExceptionFileRead(str(err))
        self.visible_record = VisibleRecord(self.file)
        self.logical_record_segment_header = LogicalRecordSegmentHeader(self.file)
        if not self.logical_record_segment_header.is_first:
            raise ExceptionFileRead('TODO: Error message')

    def _current_vr_lr_position(self) -> LogicalRecordPosition:
        return LogicalRecordPosition(self.visible_record, self.logical_record_segment_header)

    def _set_file_and_read_first_visible_record(self) -> None:
        self.file.seek(self.sul.SIZE)
        self.visible_record.read(self.file)

    def _set_file_and_read_first_logical_record_segment_header(self) -> None:
        self._set_file_and_read_first_visible_record()
        self.logical_record_segment_header.read(self.file)
        if not self.logical_record_segment_header.is_first:
            raise ExceptionFileRead('TODO: Error message')

    # def _move_to_next_visible_and_logical_record_segment(self, vr_position: int, lrsh_position: int) -> None:
    #     """Sets the file up to read a LRSH within a Visible Record. It is up to the caller to make sure that
    #     the values of vr_position and Logical Record Segment Header position are valid, usually as they have
    #     been created by one of the iteration methods of this class."""
    #     assert vr_position > 0
    #     assert lrsh_position > 0
    #     assert vr_position < lrsh_position
    #     self.file.seek(vr_position)
    #     self.visible_record.read_next(self.file)
    #     self.file.seek(lrsh_position)
    #     self.logical_record_segment_header = LogicalRecordSegmentHeader(self.file)
    #     if not self.logical_record_segment_header.is_first:
    #         raise ExceptionFileRead('TODO: Error message')

    # def iter_logical_record_segments(self) -> typing.Sequence[LogicalRecordSegmentHeader]:
    #     """Iterate across the file yielding the Logical Record Segments as LogicalRecordSegmentHeader objects."""
    #     self._set_file_and_read_first_logical_record()
    #     try:
    #         while True:
    #             # Caller could possibly mess with this so make a copy.
    #             yield copy.copy(self.logical_record_segment_header)
    #             self._seek_and_read_next_logical_record_segment()
    #     except (ExceptionVisibleRecordEOF, ExceptionLogicalRecordSegmentHeaderEOF):
    #         pass

    def iter_visible_records(self) -> typing.Sequence[VisibleRecord]:
        """
        Iterate across the file yielding the Visible Records as VisibleRecord objects.
        The iteration cann be further divided by calling iter_LRSHs_for_VR()
        """
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

    def iter_LRSHs_for_visible_record(self, vr_given: VisibleRecord) -> typing.Sequence[LogicalRecordSegmentHeader]:
        """
        Iterate across the Visible Record yielding the Logical Record Segments as LogicalRecordSegmentHeader objects.
        This leaves the file positioned at the next Visible Record or EOF.
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

    def _seek_and_read_next_logical_record_segment_header(self):
        """Seeks to the next Logical Record Segment Header and reads the header data into
        self.logical_record_segment_header. This also updates self.visible_record if necessary."""
        next_position = self.logical_record_segment_header.next_position
        self.file.seek(next_position)
        if next_position == self.visible_record.next_position:
            self.visible_record.read_next(self.file)
        self.logical_record_segment_header.read(self.file)
        # is_first has been checked by __init__

    def _read_full_logical_data(self) -> bytes:
        """
        Reads from the current file position the complete Logical Record Segment and returns it.
        """
        tell: int = self.file.tell()
        assert tell == self.logical_record_segment_header.position + self.logical_record_segment_header.HEAD_LENGTH
        by: bytes = self.file.read(self.logical_record_segment_header.logical_data_length)
        if len(by) != self.logical_record_segment_header.logical_data_length:
            raise ExceptionFileReadEOF(
                f'Premature EOF reading at {self._current_vr_lr_position()}'
                f' of {self.logical_record_segment_header.logical_data_length} bytes'
            )
        if self.logical_record_segment_header.must_strip_padding:
            pad_len = by[-1]
            # The next line is removed as pad lengths of 10 have been seen (!)
            # assert 0 < pad_len < 4, f'Pad length is {pad_len}'
            assert len(by) >= 1
            assert len(by) >= pad_len
            by = by[:-pad_len]
            logger.debug(f'FileRead._read_full_logical_data(): tell=0x{self.file.tell():08x} read 0x{len(by):0x} pad={pad_len}')
        else:
            logger.debug(f'FileRead._read_full_logical_data(): tell=0x{self.file.tell():08x} read 0x{len(by):0x}')
        return by

    # def _read_partial_logical_data(self, size: int) -> bytes:
    #     """
    #     Reads from the current file position the requested number of bytes.
    #     The number of bytes returned will be <= size.
    #     This leaves self.file in an indeterminate position, caller must handle this.
    #     """
    #     if size >= self.logical_record_segment_header.logical_data_length:
    #         return self._read_full_logical_data()
    #     tell: int = self.file.tell()
    #     assert tell == self.logical_record_segment_header.position + self.logical_record_segment_header.HEAD_LENGTH
    #     # Partial read. If there is padding we must figure out how much we can read.
    #     if self.logical_record_segment_header.must_strip_padding:
    #         self.file.seek(self.logical_record_segment_header.logical_data_length - 1)
    #         pad_len = read_one_byte(self.file)
    #         self.file.seek(tell, io.SEEK_SET)
    #         if self.logical_record_segment_header.length - pad_len < size:
    #             return self._read_full_logical_data()
    #     return self.file.read(size)

    def iter_logical_records(self) -> typing.Sequence[FileLogicalData]:
        """Iterate across the file from the beginning yielding FileLogicalData objects."""
        self._set_file_and_read_first_logical_record_segment_header()
        try:
            while True:
                file_logical_data = FileLogicalData(self.visible_record, self.logical_record_segment_header)
                file_logical_data.add_bytes(self._read_full_logical_data())
                while not self.logical_record_segment_header.is_last:
                    self._seek_and_read_next_logical_record_segment_header()
                    file_logical_data.add_bytes(self._read_full_logical_data())
                file_logical_data.seal()
                yield file_logical_data
                self._seek_and_read_next_logical_record_segment_header()
                if not self.logical_record_segment_header.is_first:
                    raise ExceptionLogicalRecordSegmentHeader(
                        'First Logical Record Segment Header is not marked as is_first.'
                    )
        except (ExceptionVisibleRecordEOF, ExceptionLogicalRecordSegmentHeaderEOF):
            pass

    def iter_logical_records_minimal(self, lr_codes: typing.Set[int]) -> typing.Sequence[FileLogicalData]:
        """Iterate across the file from the beginning yielding FileLogicalData objects which contain the minimal
        record information.

        For EFLRs this is the Set Type, Representation Code IDENT [RP66V1 Section 3 Figure 3-3].
        For IFLRs this is the Data Descriptor Referenced, Representation Code OBNAME plus the number of bytes that
        make up the index channel. References:
            [RP66V1 Section 3.3 Indirectly Formatted Logical Record]
            [RP66V1 Section 3.3.1 IFLR: Specific Structure]
            [RP66V1 Section 5.7.1 Frame Objects, Figure 5-8. Attributes of Frame Object, Comment 2]

        The rest of the data is seek()'d over leaving the file at the next initial LRSH.
        """
        # TODO: Remove asserts for production
        self._set_file_and_read_first_logical_record_segment_header()
        try:
            while True:
                file_logical_data = FileLogicalData(self.visible_record, self.logical_record_segment_header)
                # TODO: What if the self.logical_record_segment_header.logical_data_length is < the required EFLR/IFLR data?
                # Hmm, so a crude policy would be to do a 'raw' read of the minimal EFLR/IFLR which does not respect the
                # Visible Record and Logical Record Segment boundaries. Then if the read data exceeds the logical
                # segment length then rewind the file and read the logical record segment and try again.
                if file_logical_data.lr_type in lr_codes:
                    file_logical_data.add_bytes(self._read_full_logical_data())
                    while not self.logical_record_segment_header.is_last:
                        self._seek_and_read_next_logical_record_segment_header()
                        file_logical_data.add_bytes(self._read_full_logical_data())
                else:
                    tell_logical_data_start = self.file.tell()
                    if file_logical_data.lr_is_eflr:
                        # logger.info(
                        #     f'iter_logical_records_minimal(): EFLR first read {self.logical_record_segment_header.logical_data_length}')
                        by: bytes = read_OBNAME(self.file)
                    else:
                        # logger.info(
                        #     f'iter_logical_records_minimal(): IFLR first read {self.logical_record_segment_header.logical_data_length}')
                        by: bytes = read_IFLR_obname_frame_and_first_channel(self.file)
                    len_required_bytes = len(by)
                    # Explain that this assumes we are not going to encroach on the pad bytes.
                    if self.logical_record_segment_header.logical_data_length < len_required_bytes:
                        # Rewind
                        self.file.seek(tell_logical_data_start)
                        by = self._read_full_logical_data()
                    file_logical_data.add_bytes(by)
                    while not self.logical_record_segment_header.is_last:
                        # Loop for each subsequent segment
                        # See if we have enough data
                        required_bytes: int = len_required_bytes - len(file_logical_data)
                        if required_bytes > 0:
                            # Must read complete Logical Segment
                            # We can't do a partial read as we  padding, it is possible that
                            if self.logical_record_segment_header.logical_data_length <= required_bytes \
                                    or self.logical_record_segment_header.must_strip_padding:
                                file_logical_data.add_bytes(self._read_full_logical_data())
                            else:
                                # Only read partial Logical Segment
                                by = self.file.read(required_bytes)
                                file_logical_data.add_bytes(by)
                        self._seek_and_read_next_logical_record_segment_header()
                    # Could have over-read and this will give problems with the EFLR where it will try and read the
                    # template beyond the OBNAME.
                    # file_logical_data.truncate(len_required_bytes)
                file_logical_data.seal()
                yield file_logical_data
                self._seek_and_read_next_logical_record_segment_header()
                assert self.logical_record_segment_header.is_first
        except (ExceptionVisibleRecordEOF, ExceptionLogicalRecordSegmentHeaderEOF):
            pass
