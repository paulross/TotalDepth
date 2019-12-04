import re
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1


class ExceptionStorageUnitLabel(ExceptionTotalDepthRP66V1):
    """Exception specialisation for this module."""
    pass


#: The first one must be StorageUnitLabel.SIZE + TIF_SIZE = 92 or 0x5c little endian
#: 0000 0000 0000 0000 5c00 0000
#: This is here just to raise and exception for TIF marked RP66V1 files.
TIF_FILE_PREFIX = b'\x00' * 4 + b'\x00' * 4 + b'x5c\x00\x00\x00'


class StorageUnitLabel:
    """
    The Storage Unit Label that must be at the beginning of a file.
    See [RP66V1 Section 2.3.2 Storage Unit Label (SUL)].

    Unique Storage Unit Labels seen in practice::

        $ grep -rIh StorageUnitLabel <XML indexes> | sort | uniq -c
          16   <StorageUnitLabel dlis_version="V1.00" maximum_record_length="16384" sequence_number="1"
                storage_set_identifier="CUSTOMER                                                    "
                storage_unit_structure="RECORD"/>
           2   <StorageUnitLabel dlis_version="V1.00" maximum_record_length="16384" sequence_number="1"
                storage_set_identifier="PRODUCER                                                    "
                storage_unit_structure="RECORD"/>
           1   <StorageUnitLabel dlis_version="V1.00" maximum_record_length="8192" sequence_number="1"
                storage_set_identifier="                                                            "
                storage_unit_structure="RECORD"/>
          34   <StorageUnitLabel dlis_version="V1.00" maximum_record_length="8192" sequence_number="1"
                storage_set_identifier="DLIS ATLAS 1                                                "
                storage_unit_structure="RECORD"/>
         537   <StorageUnitLabel dlis_version="V1.00" maximum_record_length="8192" sequence_number="1"
                storage_set_identifier="Default Storage Set                                         "
                storage_unit_structure="RECORD"/>
    """
    SIZE = 80
    RE_STORAGE_UNIT_SEQUENCE_NUMBER = re.compile(b'^[0 ]*([1-9]+)$')
    RE_DLIS_VERSION                 = re.compile(b'^(V1.\\d\\d)$')
    RE_STORAGE_UNIT_STRUCTURE       = re.compile(b'^(RECORD)$')
    RE_MAXIMUM_RECORD_LENGTH        = re.compile(b'^[0 ]*([1-9]+)$')

    def __init__(self, by: bytes):
        if len(by) != self.SIZE:
            raise ExceptionStorageUnitLabel(f'Expected {self.SIZE} bytes, got {len(by)}')
        # FIXME: Make this the responsibility of FileRead
        # We do not support TIF markers.
        if by[len(TIF_FILE_PREFIX):] == TIF_FILE_PREFIX:  # pragma: no coverage
            raise ExceptionStorageUnitLabel(f'This file appears to have TIF markers, de-TIF the file to read it.')
        # Now the fields, storage_unit_sequence_number and maximum_record_length are converted to int
        # the rest are kept as bytes.
        m = self.RE_STORAGE_UNIT_SEQUENCE_NUMBER.match(by[:4])
        if m is None:
            raise ExceptionStorageUnitLabel(f'Can not match RE_STORAGE_UNIT_SEQUENCE_NUMBER on {by[:4]}')
        self.storage_unit_sequence_number: int = int(m.group(1))
        m = self.RE_DLIS_VERSION.match(by[4:9])
        if m is None:
            raise ExceptionStorageUnitLabel(f'Can not match RE_DLIS_VERSION on {by[4:9]}')
        self.dlis_version: bytes = m.group(1)
        m = self.RE_STORAGE_UNIT_STRUCTURE.match(by[9:15])
        if m is None:
            raise ExceptionStorageUnitLabel(f'Can not match RE_STORAGE_UNIT_STRUCTURE on {by[9:15]}')
        self.storage_unit_structure: bytes = m.group(1)
        m = self.RE_MAXIMUM_RECORD_LENGTH.match(by[15:20])
        if m is None:
            raise ExceptionStorageUnitLabel(f'Can not match RE_MAXIMUM_RECORD_LENGTH on {by[15:20]}')
        self.maximum_record_length: int = int(m.group(1))
        # TODO: Currently no enforcement here. Could check that this is printable ASCII.
        # [RP66V1 Section 2.3.2 Comment 5.]
        self.storage_set_identifier: bytes = by[20:]

    def as_bytes(self) -> bytes:
        """Returns the bytes that encode this Storage Unit Label."""
        by = _create_bytes(
            self.storage_unit_sequence_number,
            self.dlis_version,
            self.maximum_record_length,
            self.storage_set_identifier,
        )
        return by

    def __str__(self) -> str:
        return '\n'.join(
            [
                'StorageUnitLabel:',
                f'  Storage Unit Sequence Number: {self.storage_unit_sequence_number}',
                f'                  DLIS Version: {self.dlis_version}',
                f'        Storage Unit Structure: {self.storage_unit_structure}',
                f'         Maximum Record Length: {self.maximum_record_length}',
                f'        Storage Set Identifier: {self.storage_set_identifier}',
            ]
        )


def _create_bytes(storage_unit_sequence_number: int,
                  dlis_version: bytes,
                  maximum_record_length: int,
                  storage_set_identifier: bytes,
                  ) -> bytes:
    """Create bytes from the given field values."""
    fields: typing.List[typing.Tuple[int, bytes]] = [
        (4, f'{storage_unit_sequence_number:04d}'.encode('ascii')),
        (5, dlis_version),
        (6, b'RECORD'),
        (5, f'{maximum_record_length:05}'.encode('ascii')),
        (60, storage_set_identifier),
    ]
    bya = bytearray()
    for length, field in fields:
        if len(field) != length:
            raise ExceptionStorageUnitLabel(f'{field} expected length {length} but got {len(field)}')
        bya.extend(field)
    assert len(bya) == StorageUnitLabel.SIZE
    return bytes(bya)


def create_storage_unit_label(storage_unit_sequence_number: int,
                              dlis_version: bytes,
                              maximum_record_length: int,
                              storage_set_identifier: bytes,
                              ) -> StorageUnitLabel:
    """Create a StorageUnitLabel from the given values."""
    by = _create_bytes(
        storage_unit_sequence_number,
        dlis_version,
        maximum_record_length,
        storage_set_identifier,
    )
    return StorageUnitLabel(by)
