import re

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1


class ExceptionStorageUnitLabel(ExceptionTotalDepthRP66V1):
    pass


# The first one must be StorageUnitLabel.SIZE + TIF_SIZE = 92 or 0x5c little endian
# 0000 0000 0000 0000 5c00 0000
# This is here just to raise and exception for TIF marked RP66V1 files.
TIF_FILE_PREFIX = b'\x00' * 4 + b'\x00' * 4 + b'x5c\x00\x00\x00'


class StorageUnitLabel:
    """
    The Storage Unit Label that must be at the beginning of a file.
    See [RP66V1 Section 2.3.2 Storage Unit Label (SUL)].
    """
    SIZE = 80
    RE_STORAGE_UNIT_SEQUENCE_NUMBER = re.compile(b'^[0 ]*([1-9]+)$')
    RE_DLIS_VERSION                 = re.compile(b'^(V1.\\d\\d)$')
    RE_STORAGE_UNIT_STRUCTURE       = re.compile(b'^(RECORD)$')
    RE_MAXIMUM_RECORD_LENGTH        = re.compile(b'^[0 ]*([1-9]+)$')

    def __init__(self, by: bytes):
        if len(by) != self.SIZE:
            raise ExceptionStorageUnitLabel(f'Expected {self.SIZE} bytes, got {len(by)}')
        # We do not support TIF markers.
        if by[len(TIF_FILE_PREFIX):] == TIF_FILE_PREFIX:
            raise ExceptionStorageUnitLabel(f'This file appears to have TIF markers, de-TIF the file to read it.')
        # Now the fields, storage_unit_sequence_number and maximum_record_length are converted to int
        # the rest are kept as bytes.
        m = self.RE_STORAGE_UNIT_SEQUENCE_NUMBER.match(by[:4])
        if m is None:
            raise ExceptionStorageUnitLabel(f'Can not match RE_STORAGE_UNIT_SEQUENCE_NUMBER on {by}')
        self.storage_unit_sequence_number: int = int(m.group(1))
        m = self.RE_DLIS_VERSION.match(by[4:9])
        if m is None:
            raise ExceptionStorageUnitLabel(f'Can not match RE_DLIS_VERSION on {by}')
        self.dlis_version: bytes = m.group(1)
        m = self.RE_STORAGE_UNIT_STRUCTURE.match(by[9:15])
        if m is None:
            raise ExceptionStorageUnitLabel(f'Can not match RE_STORAGE_UNIT_STRUCTURE on {by}')
        self.storage_unit_structure: bytes = m.group(1)
        m = self.RE_MAXIMUM_RECORD_LENGTH.match(by[15:20])
        if m is None:
            raise ExceptionStorageUnitLabel(f'Can not match RE_MAXIMUM_RECORD_LENGTH on {by}')
        self.maximum_record_length: int = int(m.group(1))
        # TODO: Currently no enforcement here. Could check that this is printable ASCII.
        # [RP66V1 Section 2.3.2 Comment 5.]
        self.storage_set_identifier: bytes = by[20:]

    def as_bytes(self) -> bytes:
        ret = b''.join(
            [
                bytes('{:4d}'.format(self.storage_unit_sequence_number), 'ascii'),
                # TODO: Finish this
            ]
        )
        assert len(ret) == self.SIZE
        return ret

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
