import pytest

from TotalDepth.RP66V1.core import File
from TotalDepth.RP66V1.core.LogicalRecord import Encryption


ENCRYPTION_EXAMPLE_BYTES = (
    b'\x00\x04'  # UNORM size
    b'\x01\xb8'  # UNORM Producer code 440
    b'\x00\x00\x00\x00'  # Encryption information, length iof size
    b'\x00\x00'  # Payload, remaining
)


def test_logical_record_segment_encryption_packet_ctor():
    ld = File.LogicalData(ENCRYPTION_EXAMPLE_BYTES)
    lrsep  = Encryption.LogicalRecordSegmentEncryptionPacket(ld)
    assert lrsep.size == 4
    assert lrsep.producer_code == 440
    assert lrsep.encryption_information == b'\x00\x00\x00\x00'
    assert lrsep.bytes == b'\x00\x00'
    assert ld.remain == 0


def test_logical_record_segment_encryption_packet_str():
    ld = File.LogicalData(ENCRYPTION_EXAMPLE_BYTES)
    lrsep  = Encryption.LogicalRecordSegmentEncryptionPacket(ld)
    assert str(lrsep) == "EncryptionPacket: size: 0x0004 producer: 440 code length: 4 data length: 2"
