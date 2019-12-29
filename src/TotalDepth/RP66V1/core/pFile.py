"""
Handles low level RP66V1 operations.

TODO: Replace this with the C/C++ implementation.
"""

import copy
import hashlib
import io
import logging
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import StorageUnitLabel
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


class ExceptionLogicalRecordSegmentHeaderAttributes(ExceptionFile):
    pass


class ExceptionLogicalRecordSegmentHeader(ExceptionFile):
    pass


class ExceptionLogicalRecordSegmentHeaderEOF(ExceptionLogicalRecordSegmentHeader):
    pass


class ExceptionLogicalRecordSegmentHeaderSequence(ExceptionLogicalRecordSegmentHeader):
    pass


class ExceptionFileRead(ExceptionFile):
    pass


class ExceptionFileReadEOF(ExceptionFileRead):
    pass


class ExceptionFileReadPositionsInconsistent(ExceptionFileRead):
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


def two_bytes_big_endian(value: int) -> bytes:
    return bytes([(value >> 8) & 0xff, value & 0xff])


def write_two_bytes_big_endian(value: int, fobj: typing.BinaryIO) -> None:
    fobj.write(two_bytes_big_endian(value))


# ---------------- END: Low Level File Read Functions ------------------


# Some constants
LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE = 16


class VisibleRecord:
    """
    RP66V1 visible records. See [RP66V1 Section 2.3.6]
    (sic) - Place marker for error in the standard in this case
    """
    VERSION = 0xff01
    NUMBER_OF_HEADER_BYTES = 4
    MIN_LENGTH = LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE + NUMBER_OF_HEADER_BYTES
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

    def as_bytes(self) -> bytes:
        """The Visible Record represented in raw bytes."""
        return two_bytes_big_endian(self.length) + two_bytes_big_endian(self.version)

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
        if format_spec:
            return '<VisibleRecord: position={:{fmt}} length={:{fmt}} version={:{fmt}}>'.format(
                self.position, self.length, self.version, fmt=format_spec
            )
        return '<VisibleRecord: position=0x{:08x} length=0x{:04x} version=0x{:04x}>'.format(
            self.position, self.length, self.version
        )

    def __eq__(self, other):
        if other.__class__ == self.__class__:
            return self.position == other.position and self.length == other.length and self.version == other.version
        return NotImplemented

    def __str__(self) -> str:
        return f'VisibleRecord: position=0x{self.position:x} length=0x{self.length:04x} version=0x{self.version:04x}'


class LogicalRecordSegmentHeaderAttributes:
    def __init__(self, attributes: int):
        if 0 <= attributes <= 0xff:
            self.attributes = attributes
        else:
            raise ExceptionLogicalRecordSegmentHeaderAttributes(
                f'Attributes must be in the range of an unsigned char not 0x{attributes:x}'
            )

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.attributes == other.attributes
        return NotImplemented

    def __str__(self) -> str:
        return f'LRSH attr: 0x{self.attributes:02x}'

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


class LogicalRecordSegmentHeader:
    """RP66V1 Logical Record Segment Header. See See [RP66V1 2.2.2.1]"""
    HEAD_LENGTH = 4
    # MIN_LENGTH = LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE

    def __init__(self, fobj: typing.BinaryIO):
        """Constructor.
        position: The file position of the start of the LRSH.

        length: The *Logical Record Segment Length* is a two-byte, unsigned integer (Representation Code UNORM) that
            specifies the length, in bytes, of the Logical Record Segment. The Logical Record Segment Length is required
            to be even. The even length ensures that 2-byte checksums can be computed, when present, and permits some
            operating systems to handle DLIS data more efficiently without degrading performance with other systems.
            There is no limitation on a Logical Record length. Logical Record Segments must contain at least sixteen
            (16) bytes. This requirement facilitates mapping the Logical Format to those Physical Formats that require a
            minimum physical record length.

        attributes: The *Logical Record Segment Attributes* consist of a one-byte bit string that specifies the
            Attributes of the Logical Record Segment. Its structure is defined in Figure 2-3. Since its structure is
            defined explicitly in Figure 2-3, no Representation Code is assigned to it.

        record_type: The *Logical Record Type* is a one-byte, unsigned integer (Representation Code USHORT) that
            specifies the Type of the Logical Record. Its value indicates the general semantic content of the Logical
            Record. The same value must be used in all Segments of a Logical Record. Logical Record Types are specified
            in Appendix A.

            IFLRs: Numeric codes 0-127 are reserved for Public IFLRs. Codes 128-255 are reserved for Private IFLRs.
            0 is Frame Data, 1 is unformatted data.

            EFLRs: Numeric codes 0-127 are reserved for Public EFLRs. Codes 128-255 are reserved for Private EFLRs.
            0 is FILE-HEADER, 1 is ORIGIN and so on.
        """
        self.position, self.length, self.attributes, self.record_type = self._read(fobj)

    def _read(self, fobj: typing.BinaryIO) -> typing.Tuple[int, int, LogicalRecordSegmentHeaderAttributes, int]:
        position = fobj.tell()
        try:
            length = read_two_bytes_big_endian(fobj)
            # TODO: Raise on minimum length. Maybe make this a read/write property or descriptor
            attributes = LogicalRecordSegmentHeaderAttributes(read_one_byte(fobj))
            # TODO: Raise on attribute conflicts, for example:
            # If encryption packet then encryption must be set
            # Compare successors with previous - trailing length must be all or nothing, encryption all or nothing.
            record_type = read_one_byte(fobj)
        except ExceptionEOF:
            raise ExceptionLogicalRecordSegmentHeaderEOF(f'LogicalRecordSegmentHeader EOF at 0x{position:x}')
        return position, length, attributes, record_type

    def read(self, fobj: typing.BinaryIO) -> None:
        """Read a new Logical Record Segment Header.
        This may throw a ExceptionVisibleRecord or ExceptionLogicalRecordSegmentHeaderEOF."""
        self.position, self.length, self.attributes, self.record_type = self._read(fobj)

    def as_bytes(self) -> bytes:
        """The LRSH represented in raw bytes."""
        return two_bytes_big_endian(self.length) + bytes([self.attributes.attributes, self.record_type])

    def __str__(self) -> str:
        return '<LogicalRecordSegmentHeader: @ 0x{:x} len=0x{:x}' \
               ' attr=0x{:x} type={:d}>'.format(
            self.position, self.length, self.attributes.attributes, self.record_type
        )

    def long_str(self) -> str:
        return f'LRSH: @ 0x{self.position:x} len=0x{self.length:x}' \
            f' type={self.record_type:d} {self.attributes.attribute_str()}'

    @property
    def next_position(self) -> int:
        """File position of the start of the next Logical Record Segment Header."""
        return self.position + self.length

    @property
    def logical_data_position(self) -> int:
        """File position of the start of the Logical Data."""
        return self.position + self.HEAD_LENGTH


    @property
    def must_strip_padding(self) -> bool:
        return self.attributes.has_pad_bytes and not self.attributes.is_encrypted

    @property
    def logical_data_length(self):
        """Returns the length of the logical data, including padding but excluding the tail."""
        ret = self.length - self.HEAD_LENGTH
        if self.attributes.has_checksum:
            ret -= 2
        if self.attributes.has_trailing_length:
            ret -= 2
        return ret


class LogicalRecordPositionBase:
    """Simple base class with little error checking."""
    def __init__(self, vr_position: int, lrsh_position: int):
        assert vr_position + VisibleRecord.NUMBER_OF_HEADER_BYTES <= lrsh_position
        self.vr_position: int = vr_position
        self.lrsh_position: int = lrsh_position

    def __str__(self):
        return f'LogicalRecordPosition: VR: 0x{self.vr_position:08x} LRSH: 0x{self.lrsh_position:08x}'

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.vr_position == other.vr_position and self.lrsh_position == other.lrsh_position
        return NotImplemented


class LogicalRecordPosition(LogicalRecordPositionBase):
    """Class that contains the file position of the Logical Record Segment Header and the immediately prior Visible
    Record."""
    def __init__(self, vr: VisibleRecord, lrsh: LogicalRecordSegmentHeader):
        # Check VisibleRecord
        if vr.position < StorageUnitLabel.StorageUnitLabel.SIZE:
            raise ValueError(
                f'VisibleRecord at 0x{lrsh.position:x} must be >= 0x{StorageUnitLabel.StorageUnitLabel.SIZE:x}'
            )
        assert vr.length >= LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE, (
            f'VisibleRecord at 0x{vr.position:x} length 0x{vr.length:x}'
            f' must be >= 0x{LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE:x}'
        )
        assert vr.length <= VisibleRecord.MAX_LENGTH, (
                f'VisibleRecord at 0x{vr.position:x} length 0x{vr.length:x} must be <= 0x{VisibleRecord.MAX_LENGTH:x}'
            )
        # Check LogicalRecordSegmentHeader
        assert lrsh.position >= StorageUnitLabel.StorageUnitLabel.SIZE + VisibleRecord.NUMBER_OF_HEADER_BYTES, (
                f'LogicalRecordSegmentHeader at 0x{lrsh.position:x} must be'
                f' >= 0x{StorageUnitLabel.StorageUnitLabel.SIZE + VisibleRecord.NUMBER_OF_HEADER_BYTES:x}'
            )
        assert lrsh.position <= vr.position + vr.length - LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE, (
                f'LogicalRecordSegmentHeader at 0x{lrsh.position:x} must be'
                f' <= 0x{vr.position + vr.length - LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE:x}'
            )
        if lrsh.length < LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE:
            raise ValueError(
                f'LogicalRecordSegmentHeader at 0x{lrsh.position:x} length 0x{lrsh.length:x} must be'
                f' >= 0x{LOGICAL_RECORD_SEGMENT_MINIMUM_SIZE:x}'
            )
        if lrsh.length > vr.length - VisibleRecord.NUMBER_OF_HEADER_BYTES:
            raise ValueError(
                f'LogicalRecordSegmentHeader at 0x{lrsh.position:x} length 0x{lrsh.length:x} must be'
                f' <= 0x{vr.length - VisibleRecord.NUMBER_OF_HEADER_BYTES:x}'
            )
        super().__init__(vr.position, lrsh.position)


class LogicalDataDescription(typing.NamedTuple):
    """At this level this describes the raw Logical Data that can be converted into a Logical Record."""
    attributes: LogicalRecordSegmentHeaderAttributes
    lr_type: int
    ld_length: int

    def __str__(self) -> str:
        return f'LogicalDataDescription {str(self.attributes)} type: {self.lr_type} len: {self.ld_length}'


class LRPosDesc(typing.NamedTuple):
    """This contains the position and description of a Logical Record suitable for an indexer.

    It contains:

        - LogicalRecordPosition: This is the absolute file position of the Visible Record and LRSH.
            This will be of interest to indexers that mean to ``use get_file_logical_data()`` as this is a required
            argument.
        - LogicalDataDescription: This provides some basic information about the Logical Data such as attributes
            Logical Record type and the Logical Data length. This will be of interest to indexers to offer up to their
            callers.

    """
    position: LogicalRecordPosition
    description: LogicalDataDescription

    def __str__(self) -> str:
        return f'LRPosDesc pos: {str(self.position)} desc: {self.description}'


class LogicalData:
    """Class that holds data bytes and can successively read them maintaining an index of what has been read."""
    def __init__(self, by: bytes):
        self.bytes: bytes = by
        self.index: int = 0
        self._sha1: typing.Union[hashlib.sha1, None] = None

    def peek(self) -> int:
        """Return the next bytes without incrementing the index.
        May raise an IndexError if there is no data left."""
        # raise IndexError(f'IndexError: index out of range {self.index} on length {len(self.bytes)}')
        return self.bytes[self.index]

    def read(self) -> int:
        """Return the next byte and increment the index.
        May raise an IndexError if there is no data left."""
        ret = self.bytes[self.index]
        self.index += 1
        return ret

    def seek(self, length: int) -> None:
        """Increments the index. There is no error checking."""
        self.index += length

    def view_remaining(self, length: int) -> bytes:
        """Read only method to return a slice of length from the current index.
        Usage ``ld.view_remaining(ld.remain)`` to see all the remaining data."""
        if length < 0:
            raise IndexError(f'view_remaining length {length} must be >= 0')
        return self.bytes[self.index:self.index+length]

    def chunk(self, length: int) -> bytes:
        """Return the next length bytes and increment the index.
        May raise an IndexError if there is not enough data."""
        if length > self.remain:
            raise IndexError(
                f'Chunk length {length} is out of range where remain is {self.remain} of length {len(self.bytes)}'
            )
        ret = self.bytes[self.index:self.index + length]
        self.index += length
        return ret

    @property
    def remain(self) -> int:
        """The number of bytes remaining."""
        if len(self.bytes) > self.index:
            return len(self.bytes) - self.index
        return 0

    @property
    def sha1(self) -> hashlib.sha1:
        """Lazy SHA1 evaluation of the complete binary data."""
        if self._sha1 is None:
            self._sha1 = hashlib.sha1(self.bytes)
        return self._sha1

    def rewind(self) -> None:
        """Reset the index to 0."""
        self.index = 0

    def __bool__(self):
        """True if there is some data remaining."""
        return self.remain > 0

    def __len__(self):
        """Total length of the binary data."""
        return len(self.bytes)

    def __getitem__(self, index):
        """Return a byte and the given index."""
        return self.bytes[index]

    def __str__(self) -> str:
        """String representation."""
        return f'<LogicalData Len: 0x{len(self.bytes):0x} Idx: 0x{self.index:0x}>'#' Bytes: {format_bytes(self.bytes[:16])}>'


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
        self.lr_is_eflr: bool = lrsh.attributes.is_eflr
        self.lr_is_encrypted: bool = lrsh.attributes.is_encrypted
        self._bytes: typing.Union[None, bytearray] = bytearray()
        self.logical_data: typing.Union[None, LogicalData] = None
        assert self._invariants()

    def _invariants(self) -> bool:
        return (self._bytes is None) != (self.logical_data is None)

    def add_bytes(self, by: bytes) -> None:
        """Add some raw data that is part of aa Logical Record."""
        assert self._invariants()
        self._bytes.extend(by)

    def seal(self):
        """All of the Logical Record has been read into this class so seal it to prevent any more data being added.
        This also creates a LogicalData object that encapsulates the logical data."""
        assert self._invariants()
        if self.is_sealed():
            raise ValueError('FileLogicalData: Can not seal() after seal()')
        # TODO: Review the cost of this copy. Maybe a list of bytes, like a rope.
        self.logical_data = LogicalData(bytes(self._bytes))
        self._bytes = None

    def is_sealed(self) -> bool:
        """Returns True if this is sealed so no more bytes can be added."""
        assert self._invariants()
        return self._bytes is None

    def __len__(self) -> int:
        """Number of bytes of data whether sealed or unsealed."""
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
            return f'<FileLogicalData {position} LR {self.lr_type:3d} {lr_is_eflr} {lr_is_encrypted}' \
                f' PARTIAL READ: len 0x{len(self._bytes):04x}' \
                f' Bytes: {format_bytes(bytes(self._bytes[:DUMP_BYTE_LEN]))}>'
        return f'<FileLogicalData {position} LR {self.lr_type:3d} {lr_is_eflr} {lr_is_encrypted} {self.logical_data}>'


class FileRead:
    """RP66V1 file reader."""
    def __init__(self, path_or_file: typing.Union[str, typing.BinaryIO]):
        if isinstance(path_or_file, str):
            self.file = None
            self.path = path_or_file
        elif isinstance(path_or_file, (io.BytesIO, io.BufferedIOBase)):
            self.file = path_or_file
            try:
                self.path = path_or_file.name
            except AttributeError:
                self.path = '<unknown>'
        else:
            raise ExceptionFileRead(f'path_or_file must be a str or a binary file not {type(path_or_file)}')
        self.must_close = self.file is None
        self.sul = None
        self.visible_record = None
        self.logical_record_segment_header = None

    def _enter(self):
        if self.file is None:
            self.file = open(self.path, 'rb')
            self.must_close = True
        else:
            self.file.seek(0)
        # Read the Storage Unit Label, see [RP66V1] 2.3.2
        try:
            self.sul = StorageUnitLabel.StorageUnitLabel(self.file.read(StorageUnitLabel.StorageUnitLabel.SIZE))
        except StorageUnitLabel.ExceptionStorageUnitLabel as err:
            raise ExceptionFileRead(f'FileRead can not construct SUL: {str(err)}')
        # TODO: It is acceptable that a file just has a SUL, no Visible or Logical records (we have one example).
        #   We need to handle that rare case.
        self.visible_record = VisibleRecord(self.file)
        self.logical_record_segment_header = LogicalRecordSegmentHeader(self.file)
        if not self.logical_record_segment_header.attributes.is_first:
            raise ExceptionFileRead('Logical Record Segment Header is not first segment.')

    def __enter__(self):
        self._enter()
        return self

    def _exit(self):
        assert self.file is not None
        if self.must_close:
            self.file.close()
        else:
            self.file.seek(0)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._exit()
        return False

    def _set_file_and_read_first_visible_record(self) -> None:
        self.file.seek(StorageUnitLabel.StorageUnitLabel.SIZE)
        self.visible_record.read(self.file)

    def _set_file_and_read_first_logical_record_segment_header(self) -> None:
        self._set_file_and_read_first_visible_record()
        self.logical_record_segment_header.read(self.file)
        assert self.logical_record_segment_header.attributes.is_first, \
            'Logical Record Segment Header is not first segment, this should have been caught by __init__'

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
                # Caller could possibly mess with this so make a copy.
                yield copy.copy(self.logical_record_segment_header)
                next_position = self.logical_record_segment_header.next_position
                if next_position == self.visible_record.next_position:
                    break
                self.file.seek(next_position)
        except (ExceptionVisibleRecordEOF, ExceptionLogicalRecordSegmentHeaderEOF):
            pass

    def iter_LRSHs_for_visible_record_and_logical_data_fragment(
            self, vr_given: VisibleRecord) -> typing.Sequence[typing.Tuple[LogicalRecordSegmentHeader, bytes]]:
        """
        Iterate across the Visible Record yielding the Logical Record Segments and the Logical Data fragment as
        (LogicalRecordSegmentHeader, bytes) objects.
        This leaves the file positioned at the next Visible Record or EOF.
        """
        self.file.seek(vr_given.position)
        self.visible_record.read(self.file)
        assert self.visible_record == vr_given
        try:
            while True:
                self.logical_record_segment_header.read(self.file)
                lrsh = copy.copy(self.logical_record_segment_header)
                by = self.file.read(self.logical_record_segment_header.length - LogicalRecordSegmentHeader.HEAD_LENGTH)
                yield lrsh, by
                next_position = self.logical_record_segment_header.next_position
                if next_position == self.visible_record.next_position:
                    break
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
            current_vr_lr_position = LogicalRecordPosition(self.visible_record, self.logical_record_segment_header)
            raise ExceptionFileReadEOF(
                f'Premature EOF reading at {current_vr_lr_position}'
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

    def iter_logical_records(self) -> typing.Sequence[FileLogicalData]:
        """Iterate across the file from the beginning yielding FileLogicalData objects."""
        self._set_file_and_read_first_logical_record_segment_header()
        try:
            while True:
                file_logical_data = FileLogicalData(self.visible_record, self.logical_record_segment_header)
                file_logical_data.add_bytes(self._read_full_logical_data())
                while not self.logical_record_segment_header.attributes.is_last:
                    self._seek_and_read_next_logical_record_segment_header()
                    file_logical_data.add_bytes(self._read_full_logical_data())
                file_logical_data.seal()
                yield file_logical_data
                self._seek_and_read_next_logical_record_segment_header()
                if not self.logical_record_segment_header.attributes.is_first:
                    raise ExceptionLogicalRecordSegmentHeader(
                        'First Logical Record Segment Header is not marked as is_first.'
                    )
        except (ExceptionVisibleRecordEOF, ExceptionLogicalRecordSegmentHeaderEOF):
            pass

    def iter_logical_record_positions(self) -> typing.Sequence[LRPosDesc]:
        """Iterate across the file from the beginning yielding a LRPosDesc which contains:

        - LogicalRecordPosition: This is the absolute file position of the Visible Record and LRSH.
            This will be of interest to indexers that mean to ``use get_file_logical_data()`` as this is a required
            argument.
        - LogicalDataDescription: This provides some basic information about the Logical Data such as attributes
            Logical Record type and the Logical Data length. This will be of interest to indexers to offer up to their
            callers.
        """
        # Set this as if there was a previous LRSH that was the last of the sequence.
        previous_lrsh_is_last: bool = True
        vr_first = lrsh_first = logical_data_length = None
        for visible_record in self.iter_visible_records():
            for lrsh in self.iter_LRSHs_for_visible_record(visible_record):
                if lrsh.attributes.is_first and not previous_lrsh_is_last:
                    raise ExceptionLogicalRecordSegmentHeaderSequence(
                        f'Current LRSH is first but previous is not last @ 0x{lrsh.position:x}'
                    )
                if previous_lrsh_is_last and not lrsh.attributes.is_first:
                    raise ExceptionLogicalRecordSegmentHeaderSequence(
                        f'Previous LRSH is last but current is not first @ 0x{lrsh.position:x}'
                    )
                if lrsh.attributes.is_first:
                    vr_first = visible_record
                    lrsh_first = lrsh
                    logical_data_length = 0
                assert logical_data_length is not None, f'Missing initial LRSH @ 0x{lrsh.position:x}'
                logical_data_length += lrsh.logical_data_length
                # TODO: Check that (some of) attributes and lrsh.record_type are consistent across all LRSHs?
                if lrsh.attributes.is_last:
                    assert lrsh_first is not None
                    assert logical_data_length is not None
                    yield LRPosDesc(
                        LogicalRecordPosition(vr_first, lrsh_first),
                        LogicalDataDescription(lrsh_first.attributes, lrsh_first.record_type, logical_data_length)
                    )
                    vr_first = lrsh_first = logical_data_length = None
                    previous_lrsh_is_last = True
                else:
                    previous_lrsh_is_last = lrsh.attributes.is_last

    def get_file_logical_data(self, position: LogicalRecordPositionBase,
                              offset: int = 0, length: int = -1) -> FileLogicalData:
        """
        Returns a FileLogicalData object from the Logic Record position (Visible Record Position and Logical Record
        Segment Header position).
        This allows random access to the file to an index that has the Logical Record Positions.
        This will leave the file at EOFF or at the beginning of the next Visible Record or LRSH.

        :param: position A LogicalRecordPosition that specifies the visible record and LRSH position of the first LRSH
            for the Logical Record data.
        :param: offset An integer offset into the Logical Record data, default 0.
        :param: length An integer length the required Logical Record data, default of -1 is all.
        """
        if offset < 0:
            raise ExceptionFileRead(f'offset must be >= 0 not {offset}')
        # Hmm, seek() always succeeds and tell() returns the current position even if > EOF.
        self.file.seek(position.vr_position)
        # May raise
        self.visible_record.read(self.file)
        self.file.seek(position.lrsh_position)
        # May raise
        self.logical_record_segment_header.read(self.file)
        # if not self.logical_record_segment_header.attributes.is_first: # pragma: no cover
        #     raise ExceptionFileRead('Logical Record Segment Header is not first segment.')
        file_logical_data = FileLogicalData(self.visible_record, self.logical_record_segment_header)
        bytes_read = 0
        logical_data_index = 0
        all_bytes = offset == 0 and length < 0
        while True:
            # If we have read enough then just seek to the next Logical Record for efficiency and to preserve
            # the file state
            if all_bytes or bytes_read != length:
                by = self._read_full_logical_data()
                if all_bytes:
                    file_logical_data.add_bytes(by)
                else:
                    index_from = max(0, offset - logical_data_index)
                    index_to = index_from + length if length >= 0 else len(by)
                    by_slice = by[index_from:index_to]
                    file_logical_data.add_bytes(by_slice)
                    bytes_read += len(by_slice)
                    logical_data_index += len(by)
            if self.logical_record_segment_header.attributes.is_last:
                break
            self._seek_and_read_next_logical_record_segment_header()
        file_logical_data.seal()
        return file_logical_data

    def validate_positions(self) -> None:
        """Iterate through the Visible Records and Logical Record Segment Headers and raise a
        ExceptionFileReadPositionsInconsistent on the first inconsistent position."""
        next_visible_record_position = next_lrsh_position = 0
        for index_visible_record, visible_record in enumerate(self.iter_visible_records()):
            if index_visible_record == 0:
                if visible_record.position != 80:
                    raise ExceptionFileReadPositionsInconsistent(
                        f'First Visible Record expected at 80 but found at {visible_record.position}'
                    )
            else:
                if visible_record.position != next_visible_record_position:
                    raise ExceptionFileReadPositionsInconsistent(
                        f'Visible Record expected at {next_visible_record_position} but found at {visible_record.position}'
                    )
            next_visible_record_position = visible_record.next_position
            for index_lrsh, lrsh in enumerate(self.iter_LRSHs_for_visible_record(visible_record)):
                if index_visible_record == 0 and index_lrsh == 0:
                    if lrsh.position != 84:
                        raise ExceptionFileReadPositionsInconsistent(
                            f'First LRSH expected at 84 but found at {lrsh.position}'
                        )
                else:
                    if lrsh.position != next_lrsh_position:
                        raise ExceptionFileReadPositionsInconsistent(
                            f'LRSH expected at {next_lrsh_position} but found at {lrsh.position}'
                        )
                next_lrsh_position = lrsh.next_position
                if next_lrsh_position == next_visible_record_position:
                    next_lrsh_position += VisibleRecord.NUMBER_OF_HEADER_BYTES
