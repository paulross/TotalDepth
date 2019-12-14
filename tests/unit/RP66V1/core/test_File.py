import hashlib
import io
import pprint
import typing

import pytest

from TotalDepth.RP66V1.core import File
from TotalDepth.RP66V1.core import StorageUnitLabel

# from . import test_data
from tests.unit.RP66V1.core import test_data


def test_read_one_bytes():
    fobj = io.BytesIO(b'\x0f')
    assert File.read_one_byte(fobj) == 0xF
    assert fobj.read() == b''


def test_read_one_bytes_raises():
    fobj = io.BytesIO(b'')
    with pytest.raises(File.ExceptionEOF) as err:
        File.read_one_byte(fobj)
    assert err.value.args[0] == 'Premature EOF.'
    assert fobj.read() == b''


@pytest.mark.parametrize(
    'by, expected',
    (
        (b'\x00\x00', 0),
        (b'\x00\x01', 1),
        (b'\x00\xff', 255),
        (b'\x01\x00', 0x100),
        (b'\xff\x00', 0xff00),
        (b'\xff\xff', 0xffff),
    )
)
def test_read_two_bytes_big_endian(by, expected):
    fobj = io.BytesIO(by)
    assert File.read_two_bytes_big_endian(fobj) == expected
    assert fobj.read() == b''


@pytest.mark.parametrize('by', (b'', b'\x00',))
def test_read_two_bytes_big_endian_raises(by):
    fobj = io.BytesIO(by)
    with pytest.raises(File.ExceptionEOF) as err:
        File.read_two_bytes_big_endian(fobj)
    assert err.value.args[0] == 'Premature EOF.'


@pytest.mark.parametrize(
    'expected_by, value',
    (
        (b'\x00\x00', 0),
        (b'\x00\x01', 1),
        (b'\x00\xff', 255),
        (b'\x01\x00', 0x100),
        (b'\xff\x00', 0xff00),
        (b'\xff\xff', 0xffff),
    )
)
def test_two_bytes_big_endian(expected_by, value):
    assert File.two_bytes_big_endian(value) == expected_by


@pytest.mark.parametrize(
    'expected_by, value',
    (
        (b'\x00\x00', 0),
        (b'\x00\x01', 1),
        (b'\x00\xff', 255),
        (b'\x01\x00', 0x100),
        (b'\xff\x00', 0xff00),
        (b'\xff\xff', 0xffff),
    )
)
def test_write_two_bytes_big_endian(expected_by, value):
    fobj = io.BytesIO()
    File.write_two_bytes_big_endian(value, fobj)
    assert fobj.getvalue() == expected_by


@pytest.mark.parametrize(
    'fobj, position, length, version',
    (
        (None, 0, 0, 0),
        (io.BytesIO(b'\x01\x00\xff\x01'), 0, 256, 0xff01),
    )
)
def test_visible_record_ctor(fobj, position, length, version):
    vr = File.VisibleRecord(fobj)
    assert vr.position == position
    assert vr.length == length
    assert vr.version == version
    if fobj is not None:
        assert fobj.read() == b''


@pytest.mark.parametrize(
    'fobj, message',
    (
        (io.BytesIO(b'\x01\x00\xff'), 'Visible Record EOF at 0x0'),
        (io.BytesIO(b'\x01\x00\xff\x02'), 'Visible Record at 0x0 is 0xff02. Was expecting 0xff01'),
        (io.BytesIO(b'\x00\x00\xff\x01'), 'Visible Record length 0 but minimum is 20'),
        (io.BytesIO(b'\xff\xff\xff\x01'), 'Visible Record length 65535 but maximum is 16384'),
    )
)
def test_visible_record_ctor_raises(fobj, message):
    with pytest.raises(File.ExceptionVisibleRecord) as err:
        File.VisibleRecord(fobj)
    assert err.value.args[0] == message


@pytest.mark.parametrize(
    'fobj, expected',
    (
        (io.BytesIO(b'\x01\x00\xff\x01'), b'\x01\x00\xff\x01'),
    )
)
def test_visible_record_as_bytes(fobj, expected):
    vr = File.VisibleRecord(fobj)
    assert vr.as_bytes() == expected
    assert fobj.read() == b''


@pytest.mark.parametrize(
    'fobj, next_position',
    (
        (io.BytesIO(b'\x01\x00\xff\x01'), 256),
    )
)
def test_visible_record_next_position(fobj, next_position):
    vr = File.VisibleRecord(fobj)
    assert vr.next_position == next_position
    assert fobj.read() == b''


@pytest.mark.parametrize(
    'fobj, position, length, version',
    (
        (io.BytesIO(b'\x01\x00\xff\x01'), 0, 256, 0xff01),
    )
)
def test_visible_record_read_next(fobj, position, length, version):
    vr = File.VisibleRecord(None)
    vr.read_next(fobj)
    assert vr.position == position
    assert vr.length == length
    assert vr.version == version
    assert fobj.read() == b''


@pytest.mark.parametrize(
    'fobj, position, length, version',
    (
        (None, 0, 0, 0),
        (io.BytesIO(b'\x01\x00\xff\x01'), 0, 256, 0xff01),
    )
)
def test_visible_record_eq(fobj, position, length, version):
    vr = File.VisibleRecord(fobj)
    assert vr == vr
    assert vr != 1
    assert fobj.read() == b''


@pytest.mark.parametrize(
    'by',
    (
        b'\x01\x00\xff\x01',
    )
)
def test_visible_record_eq(by):
    fobj = io.BytesIO(by)
    vr = File.VisibleRecord(fobj)
    assert vr.as_bytes() == by
    assert fobj.read() == b''


@pytest.mark.parametrize(
    'fobj, format, expected',
    (
        (io.BytesIO(b'\x01\x00\xff\x01'), '', '<VisibleRecord: position=0x00000000 length=0x0100 version=0xff01>'),
        (io.BytesIO(b'\x01\x00\xff\x01'), 'd', '<VisibleRecord: position=0 length=256 version=65281>'),
        (io.BytesIO(b'\x01\x00\xff\x01'), '08,d', '<VisibleRecord: position=0,000,000 length=0,000,256 version=0,065,281>'),
    )
)
def test_visible_record_format(fobj, format, expected):
    vr = File.VisibleRecord(fobj)
    assert f'{vr:{format}}' == expected
    assert fobj.read() == b''


@pytest.mark.parametrize(
    'fobj_a, fobj_b, expected',
    (
        (io.BytesIO(b'\x01\x00\xff\x01'), io.BytesIO(b'\x01\x00\xff\x01'), True),
    )
)
def test_visible_record_eq(fobj_a, fobj_b, expected):
    vr_a = File.VisibleRecord(fobj_a)
    vr_b = File.VisibleRecord(fobj_b)
    assert (vr_a == vr_b) == expected
    assert vr_a != 1
    assert fobj_a.read() == b''
    assert fobj_b.read() == b''


@pytest.mark.parametrize(
    'byt, expected',
    (
        (0, 'LRSH attr: 0x00'),
        (255, 'LRSH attr: 0xff'),
    )
)
def test_logical_record_segment_header_attributes_str(byt, expected):
    result = File.LogicalRecordSegmentHeaderAttributes(byt)
    assert str(result) == expected


@pytest.mark.parametrize(
    'byt, expected',
    (
        (-1, 'Attributes must be in the range of an unsigned char not 0x-1'),
        (256, 'Attributes must be in the range of an unsigned char not 0x100'),
    )
)
def test_logical_record_segment_header_attributes_ctor_raises(byt, expected):
    with pytest.raises(File.ExceptionLogicalRecordSegmentHeaderAttributes) as err:
        File.LogicalRecordSegmentHeaderAttributes(byt)
    assert err.value.args[0] == expected


def test_logical_record_segment_header_attributes_eq():
    a = File.LogicalRecordSegmentHeaderAttributes(0)
    b = File.LogicalRecordSegmentHeaderAttributes(0)
    assert a == b
    assert a == a
    assert b == a
    assert b == b
    assert a != 0


@pytest.mark.parametrize(
    'byt, expected',
    (
        (0, False),
        (0x80, True),
        (0x7f, False),
        (0xff, True),
    )
)
def test_logical_record_segment_header_attributes_is_eflr(byt, expected):
    result = File.LogicalRecordSegmentHeaderAttributes(byt)
    assert result.is_eflr == expected


@pytest.mark.parametrize(
    'byt, expected',
    (
        (0, True),
        (0x40, False),
        (0xbf, True),
        (0xff, False),
    )
)
def test_logical_record_segment_header_attributes_is_first(byt, expected):
    result = File.LogicalRecordSegmentHeaderAttributes(byt)
    assert result.is_first == expected


@pytest.mark.parametrize(
    'byt, expected',
    (
        (0, True),
        (0x20, False),
        (0xdf, True),
        (0xff, False),
    )
)
def test_logical_record_segment_header_attributes_is_last(byt, expected):
    result = File.LogicalRecordSegmentHeaderAttributes(byt)
    assert result.is_last == expected


@pytest.mark.parametrize(
    'byt, expected',
    (
        (0, False),
        (0x10, True),
        (0xef, False),
        (0xff, True),
    )
)
def test_logical_record_segment_header_attributes_is_encrypted(byt, expected):
    result = File.LogicalRecordSegmentHeaderAttributes(byt)
    assert result.is_encrypted == expected


@pytest.mark.parametrize(
    'byt, expected',
    (
        (0, False),
        (0x08, True),
        (0xf7, False),
        (0xff, True),
    )
)
def test_logical_record_segment_header_attributes_has_encryption_packet(byt, expected):
    result = File.LogicalRecordSegmentHeaderAttributes(byt)
    assert result.has_encryption_packet == expected


@pytest.mark.parametrize(
    'byt, expected',
    (
        (0, False),
        (0x04, True),
        (0xfb, False),
        (0xff, True),
    )
)
def test_logical_record_segment_header_attributes_has_checksum(byt, expected):
    result = File.LogicalRecordSegmentHeaderAttributes(byt)
    assert result.has_checksum == expected


@pytest.mark.parametrize(
    'byt, expected',
    (
        (0, False),
        (0x02, True),
        (0xfd, False),
        (0xff, True),
    )
)
def test_logical_record_segment_header_attributes_has_trailing_length(byt, expected):
    result = File.LogicalRecordSegmentHeaderAttributes(byt)
    assert result.has_trailing_length == expected


@pytest.mark.parametrize(
    'byt, expected',
    (
        (0, False),
        (0x01, True),
        (0xfe, False),
        (0xff, True),
    )
)
def test_logical_record_segment_header_attributes_has_pad_bytes(byt, expected):
    result = File.LogicalRecordSegmentHeaderAttributes(byt)
    assert result.has_pad_bytes == expected


@pytest.mark.parametrize(
    'byt, expected',
    (
        (0, 'IFLR-first-last'),
        (0x01, 'IFLR-first-last-padding'),
        # TODO: Complete this?
        (0xfe, 'EFLR-encrypted-checksum-trailing length'),
        (0xff, 'EFLR-encrypted-checksum-trailing length-padding'),
    )
)
def test_logical_record_segment_header_attributes_attribute_str(byt, expected):
    result = File.LogicalRecordSegmentHeaderAttributes(byt)
    assert result.attribute_str() == expected


@pytest.mark.parametrize(
    'by, position, length, attributes, record_type',
    (
        (b'\x01\x00\xff\x01', 0, 256, File.LogicalRecordSegmentHeaderAttributes(255), 1,),
    )
)
def test_LRSH_ctor(by, position, length, attributes, record_type):
    fobj = io.BytesIO(by)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    assert lrsh.position == position
    assert lrsh.length == length
    assert lrsh.attributes == attributes
    assert lrsh.record_type == record_type
    assert fobj.read() == b''


def test_LRSH_ctor_raises():
    # Missing one byte
    fobj = io.BytesIO(b'\x01\x00\xff')
    with pytest.raises(File.ExceptionLogicalRecordSegmentHeaderEOF) as err:
        File.LogicalRecordSegmentHeader(fobj)
    assert err.value.args[0] == 'LogicalRecordSegmentHeader EOF at 0x0'
    assert fobj.read() == b''


@pytest.mark.parametrize(
    'by, next_position, logical_data_position',
    (
        (b'\x01\x00\xff\x01', 256, 4,),
    )
)
def test_LRSH_positions(by, next_position, logical_data_position):
    fobj = io.BytesIO(by)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    assert lrsh.next_position == next_position
    assert lrsh.logical_data_position == logical_data_position
    assert fobj.read() == b''


@pytest.mark.parametrize(
    'by, is_first, is_last',
    (
        (b'\x01\x00\x00\x01', True, True,),
        (b'\x01\x00\x60\x01', False, False,),
        (b'\x01\x00\xff\x01', False, False,),
        (b'\x01\x00\x20\x01', True, False,),
        (b'\x01\x00\x40\x01', False, True,),
        (b'\x01\x00\x00\x01', True, True,),
        (b'\x01\x00\x9f\x01', True, True,),
    )
)
def test_LRSH_is_first_last(by, is_first, is_last):
    fobj = io.BytesIO(by)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    assert lrsh.attributes.is_first == is_first
    assert lrsh.attributes.is_last == is_last
    assert fobj.read() == b''


@pytest.mark.parametrize(
    'by, has_checksum, has_trailing_length, logical_data_length',
    (
        (b'\x01\x00\xf9\x01', False, False, 252,),  # No checksum, no trailing length
        (b'\x01\x00\xfd\x01', True, False, 250,),  # Checksum, no trailing length
        (b'\x01\x00\xfb\x01', False, True, 250,),  # No checksum, has trailing length
        (b'\x01\x00\xff\x01', True, True, 248,),  # Both checksum and trailing length
    )
)
def test_LRSH_logical_data_length(by, has_checksum, has_trailing_length, logical_data_length):
    fobj = io.BytesIO(by)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    assert lrsh.attributes.has_checksum == has_checksum
    assert lrsh.attributes.has_trailing_length == has_trailing_length
    assert lrsh.logical_data_length == logical_data_length
    assert fobj.read() == b''


@pytest.mark.parametrize(
    'by, is_encrypted, has_pad_bytes, must_strip_padding',
    (
        (b'\x01\x00\xee\x01', False, False, False,),  # Not encrypted, no padding, no stripping.
        (b'\x01\x00\xfe\x01', True, False, False,),  # Encrypted, no padding, no stripping.
        (b'\x01\x00\xef\x01', False, True, True,),  # Not encrypted, with padding, must strip.
        (b'\x01\x00\xff\x01', True, True, False,),  # Encrypted, with padding, no strip.
    )
)
def test_LRSH_must_strip_padding(by, is_encrypted, has_pad_bytes, must_strip_padding):
    fobj = io.BytesIO(by)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    assert lrsh.attributes.is_encrypted == is_encrypted
    assert lrsh.attributes.has_pad_bytes == has_pad_bytes
    assert lrsh.must_strip_padding == must_strip_padding
    assert fobj.read() == b''


@pytest.mark.parametrize(
    'by, has_encryption_packet',
    (
        (b'\x01\x00\x00\x01', False,),
        (b'\x01\x00\x08\x01', True,),
    )
)
def test_LRSH_has_encryption_packet(by, has_encryption_packet):
    fobj = io.BytesIO(by)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    assert lrsh.attributes.has_encryption_packet== has_encryption_packet
    assert fobj.read() == b''


@pytest.mark.parametrize(
    'by, position, length, attributes, record_type',
    (
        (b'\x01\x00\xff\x01', 0, 256, File.LogicalRecordSegmentHeaderAttributes(255), 1,),
    )
)
def test_LRSH_ctor_then_read(by, position, length, attributes, record_type):
    fobj = io.BytesIO(by)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    fobj = io.BytesIO(by)
    lrsh.read(fobj)
    assert lrsh.position == position
    assert lrsh.length == length
    assert lrsh.attributes == attributes
    assert lrsh.record_type == record_type
    assert fobj.read() == b''


def test_LRSH_ctor_as_bytes():
    by = b'\x01\x00\xff\x01'
    fobj = io.BytesIO(by)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    assert lrsh.as_bytes() == by
    assert fobj.read() == b''


# Length is first two bytes big endian
# Attributes one byte
# Record type one byte
@pytest.mark.parametrize(
    'by, expected',
    (
        (b'\x01\x00\xff\x01', "EFLR-encrypted-checksum-trailing length-padding",),
        (b'\x01\x00\x00\x01', "IFLR-first-last",),
    )
)
def test_LRSH_attribute_str(by, expected):
    fobj = io.BytesIO(by)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    assert lrsh.attributes.attribute_str() == expected
    assert fobj.read() == b''


def test_LogicalRecordPosition_ctor():
    fobj = io.BytesIO(
        b''.join([
            b'\x00' * StorageUnitLabel.StorageUnitLabel.SIZE,  # Simulated Storage Unit Label
            b'\x01\x00\xff\x01',  # Visible record: position=0, length=256, type=0xff01),
            b'\x00\x80\x9f\x01',  # LRSH: position=4, length=128, attributes=0x9f, type=1
        ])
    )
    sul = fobj.read(StorageUnitLabel.StorageUnitLabel.SIZE)
    vr = File.VisibleRecord(fobj)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    assert fobj.read() == b''
    lrp = File.LogicalRecordPosition(vr, lrsh)
    assert lrp.vr_position == 80
    assert lrp.lrsh_position == 84


def test_LogicalRecordPosition_str():
    fobj = io.BytesIO(
        b''.join([
            b'\x00' * StorageUnitLabel.StorageUnitLabel.SIZE,  # Simulated Storage Unit Label
            b'\x01\x00\xff\x01',  # Visible record: position=0, length=256, type=0xff01),
            b'\x00\x80\x9f\x01',  # LRSH: position=4, length=128, attributes=0x9f, type=1
        ])
    )
    sul = fobj.read(StorageUnitLabel.StorageUnitLabel.SIZE)
    vr = File.VisibleRecord(fobj)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    assert fobj.read() == b''
    lrp = File.LogicalRecordPosition(vr, lrsh)
    assert str(lrp) == 'LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054'


def test_LogicalRecordPosition_eq():
    fobj = io.BytesIO(
        b''.join([
            b'\x00' * StorageUnitLabel.StorageUnitLabel.SIZE,  # Simulated Storage Unit Label
            b'\x01\x00\xff\x01',  # Visible record: position=0, length=256, type=0xff01),
            b'\x00\x80\x9f\x01',  # LRSH: position=4, length=128, attributes=0x9f, type=1
        ])
    )
    sul = fobj.read(StorageUnitLabel.StorageUnitLabel.SIZE)
    vr = File.VisibleRecord(fobj)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    assert fobj.read() == b''
    lrp_a = File.LogicalRecordPosition(vr, lrsh)
    lrp_b = File.LogicalRecordPosition(vr, lrsh)
    assert lrp_a == lrp_b
    assert lrp_a != 1


@pytest.mark.parametrize(
    'sul_length, vr_bytes, lrsh_bytes, expected',
    (
        # VR Prior to SUL
        (79, b'\x01\x00\xff\x01', b'\x00\x80\x9f\x01', 'VisibleRecord at 0x53 must be >= 0x50'),
        # TODO: Remove VR/LRSH checks, replace by asserts.
        (None, b'\x01\x00\xff\x01', b'\x00\x0f\x9f\x01',
         'LogicalRecordSegmentHeader at 0x54 length 0xf must be >= 0x10'),
        (None, b'\x01\x00\xff\x01', b'\xff\xff\x9f\x01',
         'LogicalRecordSegmentHeader at 0x54 length 0xffff must be <= 0xfc'),
        # (None, b'\x01\x00\xff\x01', b'\x00\x80\x60\x01',
        #  'LogicalRecordSegmentHeader at 0x54 must be the first in the sequence of segments.'),
    )
)
def test_LogicalRecordPosition_ctor_raises(sul_length, vr_bytes, lrsh_bytes, expected):
    if sul_length is None:
        sul_length = StorageUnitLabel.StorageUnitLabel.SIZE
    fobj = io.BytesIO(
        b''.join([
            b'\x00' * sul_length,  # Simulated Storage Unit Label
            vr_bytes, lrsh_bytes,
        ])
    )
    sul = fobj.read(sul_length)
    vr = File.VisibleRecord(fobj)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    with pytest.raises(ValueError) as err:
        File.LogicalRecordPosition(vr, lrsh)
    assert err.value.args[0] == expected
    assert fobj.read() == b''


@pytest.mark.parametrize(
    'by, length',
    (
        (b'\x00\x01\x02\x03', 4),
    )
)
def test_logical_data_ctor(by, length):
    ld = File.LogicalData(by)
    assert ld.index == 0
    assert ld.remain == length


def test_logical_data_peek():
    ld = File.LogicalData(b'\x00\x01\x02\x03')
    assert ld.peek() == 0


def test_logical_data_str():
    ld = File.LogicalData(b'\x00\x01\x02\x03')
    assert str(ld) == '<LogicalData Len: 0x4 Idx: 0x0>'


def test_logical_data_len():
    ld = File.LogicalData(b'\x00\x01\x02\x03')
    assert len(ld) == 4


def test_logical_data_sha1():
    by = b'\x00\x01\x02\x03'
    ld = File.LogicalData(by)
    sha1 = hashlib.sha1(by)
    assert ld.sha1.hexdigest() == sha1.hexdigest()


def test_logical_data_read():
    ld = File.LogicalData(b'\x00\x01\x02\x03')
    assert ld.read() == 0
    assert ld.read() == 1
    assert ld.read() == 2
    assert ld.read() == 3


def test_logical_data_view_remaining():
    ld = File.LogicalData(b'\x00\x01\x02\x03')
    assert ld.read() == 0
    assert ld.view_remaining(2) == b'\x01\x02'
    assert ld.view_remaining(3) == b'\x01\x02\x03'
    assert ld.view_remaining(99) == b'\x01\x02\x03'
    assert ld.read() == 1
    assert ld.view_remaining(2) == b'\x02\x03'
    assert ld.view_remaining(3) == b'\x02\x03'
    assert ld.view_remaining(99) == b'\x02\x03'
    assert ld.read() == 2
    assert ld.read() == 3


def test_logical_data_view_remaining_raises():
    ld = File.LogicalData(b'\x00\x01\x02\x03')
    with pytest.raises(IndexError) as err:
        ld.view_remaining(-1)
    assert err.value.args[0] == 'view_remaining length -1 must be >= 0'


@pytest.mark.parametrize(
    'reads, view_remaining',
    (
        (0, b'\x00\x01\x02\x03'),
        (1, b'\x01\x02\x03'),
        (2, b'\x02\x03'),
        (3, b'\x03'),
    )
)
def test_logical_data_view_remaining_remain(reads, view_remaining):
    ld = File.LogicalData(b'\x00\x01\x02\x03')
    for i in range(reads):
        ld.read()
    assert ld.view_remaining(ld.remain) == view_remaining


@pytest.mark.parametrize(
    'reads, len_chunk, chunk',
    (
        (0, 1, b'\x00'),
        (0, 2, b'\x00\x01'),
        (0, 3, b'\x00\x01\x02'),
        (0, 4, b'\x00\x01\x02\x03'),
        (1, 1, b'\x01'),
        (1, 2, b'\x01\x02'),
        (1, 3, b'\x01\x02\x03'),
        (2, 1, b'\x02'),
        (2, 2, b'\x02\x03'),
        (3, 1, b'\x03'),
    )
)
def test_logical_data_chunk(reads, len_chunk, chunk):
    ld = File.LogicalData(b'\x00\x01\x02\x03')
    for i in range(reads):
        ld.read()
    assert ld.chunk(len_chunk) == chunk


def test_logical_data_chunk_raises():
    ld = File.LogicalData(b'\x00\x01\x02\x03')
    ld.read()
    with pytest.raises(IndexError) as err:
        ld.chunk(4)
    assert err.value.args[0] == 'Chunk length 4 is out of range where remain is 3 of length 4'


@pytest.mark.parametrize(
    'index, item',
    (
        (0, 0xf0),
        (1, 0xf1),
        (2, 0xf2),
        (3, 0xf3),
    )
)
def test_logical_data_getitem(index, item):
    ld = File.LogicalData(b'\xf0\xf1\xf2\xf3')
    assert ld[index] == item


def test_FileLogicalData_ctor():
    fobj = io.BytesIO(
        b''.join([
            b'\x00' * StorageUnitLabel.StorageUnitLabel.SIZE,  # Simulated Storage Unit Label
            b'\x01\x00\xff\x01',  # Visible record: position=0, length=256, type=0xff01),
            # b'\x00\x80\x9f\x01',  # LRSH: position=4, length=128, attributes=0x9f, type=1
            b'\x00\x80\x80\x01',
        ])
    )
    sul = fobj.read(StorageUnitLabel.StorageUnitLabel.SIZE)
    vr = File.VisibleRecord(fobj)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    fld = File.FileLogicalData(vr, lrsh)
    assert fld.position.vr_position == 80
    assert fld.position.lrsh_position == 84
    assert fld.lr_type == 1
    assert fld.lr_is_eflr == True
    assert fld.lr_is_encrypted == False
    assert fld._bytes is not None
    assert not fld.is_sealed()
    assert fld.logical_data is None


def test_FileLogicalData_add_bytes():
    fobj = io.BytesIO(
        b''.join([
            b'\x00' * StorageUnitLabel.StorageUnitLabel.SIZE,  # Simulated Storage Unit Label
            b'\x01\x00\xff\x01',  # Visible record: position=0, length=256, type=0xff01),
            b'\x00\x80\x80\x01',  # LRSH
        ])
    )
    sul = fobj.read(StorageUnitLabel.StorageUnitLabel.SIZE)
    vr = File.VisibleRecord(fobj)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    fld = File.FileLogicalData(vr, lrsh)
    assert len(fld) == 0
    assert fld._bytes is not None
    assert not fld.is_sealed()
    assert fld.logical_data is None
    fld.add_bytes(b'\x00\x00')
    assert len(fld) == 2
    assert fld._bytes is not None
    assert not fld.is_sealed()
    assert fld.logical_data is None


def test_FileLogicalData_add_bytes_and_seal():
    fobj = io.BytesIO(
        b''.join([
            b'\x00' * StorageUnitLabel.StorageUnitLabel.SIZE,  # Simulated Storage Unit Label
            b'\x01\x00\xff\x01',  # Visible record: position=0, length=256, type=0xff01),
            b'\x00\x80\x80\x01',  # LRSH
        ])
    )
    sul = fobj.read(StorageUnitLabel.StorageUnitLabel.SIZE)
    vr = File.VisibleRecord(fobj)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    fld = File.FileLogicalData(vr, lrsh)
    assert len(fld) == 0
    assert fld._bytes is not None
    assert not fld.is_sealed()
    assert fld.logical_data is None
    fld.add_bytes(b'\x00\x00')
    assert len(fld) == 2
    assert fld._bytes is not None
    assert not fld.is_sealed()
    assert fld.logical_data is None
    fld.seal()
    assert fld._bytes is None
    assert fld.is_sealed()
    assert fld.logical_data is not None
    assert len(fld) == 2


def test_FileLogicalData_seal_raises():
    fobj = io.BytesIO(
        b''.join([
            b'\x00' * StorageUnitLabel.StorageUnitLabel.SIZE,  # Simulated Storage Unit Label
            b'\x01\x00\xff\x01',  # Visible record: position=0, length=256, type=0xff01),
            b'\x00\x80\x80\x01',  # LRSH
        ])
    )
    sul = fobj.read(StorageUnitLabel.StorageUnitLabel.SIZE)
    vr = File.VisibleRecord(fobj)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    fld = File.FileLogicalData(vr, lrsh)
    fld.add_bytes(b'\x00\x00')
    fld.seal()
    with pytest.raises(ValueError) as err:
        fld.seal()
    assert err.value.args[0] == 'FileLogicalData: Can not seal() after seal()'


def test_FileLogicalData_str():
    fobj = io.BytesIO(
        b''.join([
            b'\x00' * StorageUnitLabel.StorageUnitLabel.SIZE,  # Simulated Storage Unit Label
            b'\x01\x00\xff\x01',  # Visible record: position=0, length=256, type=0xff01),
            b'\x00\x80\x80\x01',  # LRSH
        ])
    )
    sul = fobj.read(StorageUnitLabel.StorageUnitLabel.SIZE)
    vr = File.VisibleRecord(fobj)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    fld = File.FileLogicalData(vr, lrsh)
    assert str(fld) == '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 LR   1 E n PARTIAL READ: len 0x0000 Bytes:  >'
    fld.add_bytes(b'\x00\x00')
    assert str(fld) == '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 LR   1 E n PARTIAL READ: len 0x0002 Bytes: 0000 ..>'
    fld.seal()
    assert str(fld) == '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 LR   1 E n <LogicalData Len: 0x2 Idx: 0x0>>'

# ==================== Test of FileRead ========================


@pytest.mark.parametrize(
    'file_bytes',
    (
        test_data.BASIC_FILE,
        test_data.MINIMAL_FILE,
        test_data.SMALL_FILE,
    )
)
def test_file_basic_file_ctor_with_file_object(file_bytes):
    fobj = io.BytesIO(file_bytes)
    File.FileRead(fobj)


@pytest.mark.parametrize(
    'file_bytes',
    (
        test_data.BASIC_FILE,
        test_data.MINIMAL_FILE,
        test_data.SMALL_FILE,
    )
)
def test_file_basic_file_ctor_with_path(tmpdir, file_bytes):
    file_name = 'rp66v1file.dlis'
    with open(tmpdir.join(file_name), 'wb') as temp_file:
        temp_file.write(file_bytes)
    with File.FileRead(tmpdir.join(file_name).strpath):
        pass


def test_file_basic_file_enter_on_empty_raises():
    fobj = io.BytesIO(b'')
    with pytest.raises(File.ExceptionFileRead) as err:
        with File.FileRead(fobj):
            pass
    assert err.value.args[0] == 'FileRead can not construct SUL: Expected 80 bytes, got 0'


def test_file_ctor_raises():
    with pytest.raises(File.ExceptionFileRead) as err:
        with File.FileRead(1):
            pass
    assert err.value.args[0] == "path_or_file must be a str or a binary file not <class 'int'>"


def test_file_file_ctor_raises_with_lrsh_not_first():
    fobj = io.BytesIO(test_data.FILE_WITH_FIRST_LRSH_NOT_FIRST_RECORD)
    with pytest.raises(File.ExceptionFileRead) as err:
        with File.FileRead(fobj):
            pass
    assert err.value.args[0] == 'Logical Record Segment Header is not first segment.'


@pytest.mark.parametrize(
    'file_bytes, sul_string',
    (
        (
            test_data.BASIC_FILE,
            r"""StorageUnitLabel:
  Storage Unit Sequence Number: 1
                  DLIS Version: b'V1.00'
        Storage Unit Structure: b'RECORD'
         Maximum Record Length: 8192
        Storage Set Identifier: b'              +++TIF@C:\\INSITE\\Data\\ExpFiles\\VA2456~1.DLI+++'"""
        ),
        (
            test_data.MINIMAL_FILE,
            r"""StorageUnitLabel:
  Storage Unit Sequence Number: 1
                  DLIS Version: b'V1.00'
        Storage Unit Structure: b'RECORD'
         Maximum Record Length: 8192
        Storage Set Identifier: b'              +++TIF@C:\\INSITE\\Data\\ExpFiles\\VA2456~1.DLI+++'"""
        ),
        (
            test_data.SMALL_FILE,
            r"""StorageUnitLabel:
  Storage Unit Sequence Number: 1
                  DLIS Version: b'V1.00'
        Storage Unit Structure: b'RECORD'
         Maximum Record Length: 8192
        Storage Set Identifier: b'Default Storage Set                                         '"""
        ),
    )
)
def test_file_basic_file_sul(file_bytes, sul_string):
    fobj = io.BytesIO(file_bytes)
    with File.FileRead(fobj) as file_read:
        # print(str(file_read.sul))
        assert str(file_read.sul) == sul_string


@pytest.mark.parametrize(
    'file_bytes, expected',
    (
        (
            test_data.BASIC_FILE,
            [
                'VisibleRecord: position=0x50 length=0x2000 version=0xff01',
                'VisibleRecord: position=0x2050 length=0x2000 version=0xff01',
                'VisibleRecord: position=0x4050 length=0x2000 version=0xff01',
                'VisibleRecord: position=0x6050 length=0x2000 version=0xff01',
                'VisibleRecord: position=0x8050 length=0x2000 version=0xff01',
                'VisibleRecord: position=0xa050 length=0x0f24 version=0xff01',
            ]
        ),
        (
            test_data.MINIMAL_FILE,
            ['VisibleRecord: position=0x50 length=0x2000 version=0xff01']
        ),
        (
            test_data.SMALL_FILE,
            [
                'VisibleRecord: position=0x50 length=0x1ffc version=0xff01',
                'VisibleRecord: position=0x204c length=0x03f4 version=0xff01',
            ]
        ),
    )
)
def test_file_basic_file_visible_records(file_bytes, expected):
    fobj = io.BytesIO(file_bytes)
    with File.FileRead(fobj) as file_read:
        vrs = [str(vr) for vr in file_read.iter_visible_records()]
        # print(vrs)
        assert vrs == expected


@pytest.mark.parametrize(
    'file_bytes, expected',
    (
        (
            test_data.BASIC_FILE_WITH_TWO_VISIBLE_RECORDS_NO_IFLRS,
            [
                [
                    'LRSH: @ 0x54 len=0x7c type=0 EFLR-first-last',
                    'LRSH: @ 0xd0 len=0x1fc type=1 EFLR-first-last-padding',
                    'LRSH: @ 0x2cc len=0xcc type=4 EFLR-first-last-padding',
                    'LRSH: @ 0x398 len=0xbdc type=5 EFLR-first-last',
                    'LRSH: @ 0xf74 len=0x352 type=5 EFLR-first-last',
                    'LRSH: @ 0x12c6 len=0x17e type=3 EFLR-first-last',
                    'LRSH: @ 0x1444 len=0xa2 type=128 EFLR-first-last',
                    'LRSH: @ 0x14e6 len=0x69c type=6 EFLR-first-last-padding',
                    'LRSH: @ 0x1b82 len=0x4ce type=6 EFLR-first',
                ],
                 ['LRSH: @ 0x2054 len=0x226 type=6 EFLR-last-padding']
            ]
        ),
        (
            test_data.MINIMAL_FILE,
            [
                [
                    'LRSH: @ 0x54 len=0x7c type=0 EFLR-first-last',
                    'LRSH: @ 0xd0 len=0x1fc type=1 EFLR-first-last-padding',
                ]
            ]
        ),
        (
            test_data.SMALL_FILE,
            [
                [
                    'LRSH: @ 0x54 len=0x7c type=0 EFLR-first-last',
                    'LRSH: @ 0xd0 len=0x200 type=1 EFLR-first-last-padding',
                    'LRSH: @ 0x2d0 len=0xe0c type=5 EFLR-first-last-padding',
                    'LRSH: @ 0x10dc len=0x2c0 type=3 EFLR-first-last-padding',
                    'LRSH: @ 0x139c len=0x110 type=4 EFLR-first-last',
                    'LRSH: @ 0x14ac len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x14dc len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x150c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x153c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x156c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x159c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x15cc len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x15fc len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x162c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x165c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x168c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x16bc len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x16ec len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x171c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x174c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x177c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x17ac len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x17dc len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x180c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x183c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x186c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x189c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x18cc len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x18fc len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x192c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x195c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x198c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x19bc len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x19ec len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1a1c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1a4c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1a7c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1aac len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1adc len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1b0c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1b3c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1b6c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1b9c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1bcc len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1bfc len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1c2c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1c5c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1c8c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1cbc len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1cec len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1d1c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1d4c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1d7c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1dac len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1ddc len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1e0c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1e3c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1e6c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1e9c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1ecc len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1efc len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1f2c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1f5c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1f8c len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1fbc len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x1fec len=0x30 type=0 IFLR-first-last-padding',
                    'LRSH: @ 0x201c len=0x30 type=0 IFLR-first-last-padding',
                ],
                 [
                     'LRSH: @ 0x2050 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x2080 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x20b0 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x20e0 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x2110 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x2140 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x2170 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x21a0 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x21d0 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x2200 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x2230 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x2260 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x2290 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x22c0 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x22f0 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x2320 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x2350 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x2380 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x23b0 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x23e0 len=0x30 type=0 IFLR-first-last-padding',
                     'LRSH: @ 0x2410 len=0x30 type=0 IFLR-first-last-padding',
                 ]
             ]
        ),
    )
)
def test_file_iter_LRSHs_for_visible_record(file_bytes, expected):
    fobj = io.BytesIO(file_bytes)
    with File.FileRead(fobj) as file_read:
        lrsh_list = []
        for vr in file_read.iter_visible_records():
            lrsh_list.append([])
            for lrsh in file_read.iter_LRSHs_for_visible_record(vr):
                lrsh_list[-1].append(lrsh.long_str())
        # pprint.pprint(lrsh_list)
        assert lrsh_list == expected


def test_file_iter_logical_records_small_file():
    fobj = io.BytesIO(test_data.SMALL_FILE)
    with File.FileRead(fobj) as file_read:
        lr_list = []
        for file_logical_data in file_read.iter_logical_records():
            lr_list.append(str(file_logical_data))
        # pprint.pprint(lr_list, width=150)
        expected = [
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 LR   0 E n <LogicalData Len: 0x78 Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000000d0 LR   1 E n <LogicalData Len: 0x1f9 Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000002d0 LR   5 E n <LogicalData Len: 0xe05 Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000010dc LR   3 E n <LogicalData Len: 0x2bb Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000139c LR   4 E n <LogicalData Len: 0x10c Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000014ac LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000014dc LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000150c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000153c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000156c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000159c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000015cc LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000015fc LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000162c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000165c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000168c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000016bc LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000016ec LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000171c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000174c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000177c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000017ac LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000017dc LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000180c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000183c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000186c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000189c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000018cc LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000018fc LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000192c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000195c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000198c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000019bc LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000019ec LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001a1c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001a4c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001a7c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001aac LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001adc LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001b0c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001b3c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001b6c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001b9c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001bcc LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001bfc LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001c2c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001c5c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001c8c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001cbc LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001cec LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001d1c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001d4c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001d7c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001dac LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001ddc LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001e0c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001e3c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001e6c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001e9c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001ecc LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001efc LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001f2c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001f5c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001f8c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001fbc LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001fec LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x0000201c LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x00002050 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x00002080 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x000020b0 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x000020e0 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x00002110 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x00002140 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x00002170 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x000021a0 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x000021d0 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x00002200 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x00002230 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x00002260 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x00002290 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x000022c0 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x000022f0 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x00002320 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x00002350 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x00002380 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x000023b0 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x000023e0 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
            '<FileLogicalData LogicalRecordPosition: VR: 0x0000204c LRSH: 0x00002410 LR   0 I n <LogicalData Len: 0x2a Idx: 0x0>>',
        ]
        assert lr_list == expected


def test_file_iter_logical_records_basic_file():
    fobj = io.BytesIO(test_data.BASIC_FILE)
    with File.FileRead(fobj) as file_read:
        lr_list = list(file_read.iter_logical_records())
        assert len(lr_list) == 660


def test_file_iter_logical_records_raises_not_is_first():
    fobj = io.BytesIO(test_data.FILE_WITH_SECOND_LRSH_NOT_FIRST_RECORD)
    lr_list = []
    with pytest.raises(File.ExceptionLogicalRecordSegmentHeader) as err:
        with File.FileRead(fobj) as file_read:
            for file_logical_data in file_read.iter_logical_records():
                lr_list.append(str(file_logical_data))
    assert err.value.args[0] == 'First Logical Record Segment Header is not marked as is_first.'


def test_file_iter_logical_records_raises_eof():
    fobj = io.BytesIO(test_data.MINIMAL_FILE_PREMATURE_EOF)
    lr_list = []
    with pytest.raises(File.ExceptionFileReadEOF) as err:
        with File.FileRead(fobj) as file_read:
            for file_logical_data in file_read.iter_logical_records():
                lr_list.append(str(file_logical_data))
    assert err.value.args[0] == 'Premature EOF reading at LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000000d0 of 504 bytes'


@pytest.mark.parametrize(
    'position, length, version, lrsh_expected',
    (
        (
            0x50, 0x2000, 0xff01,
            ['<LogicalRecordSegmentHeader: @ 0x54 len=0x7c attr=0x80 type=0>',
             '<LogicalRecordSegmentHeader: @ 0xd0 len=0x1fc attr=0x81 type=1>',
             '<LogicalRecordSegmentHeader: @ 0x2cc len=0xcc attr=0x81 type=4>',
             '<LogicalRecordSegmentHeader: @ 0x398 len=0xbdc attr=0x80 type=5>',
             '<LogicalRecordSegmentHeader: @ 0xf74 len=0x352 attr=0x80 type=5>',
             '<LogicalRecordSegmentHeader: @ 0x12c6 len=0x17e attr=0x80 type=3>',
             '<LogicalRecordSegmentHeader: @ 0x1444 len=0xa2 attr=0x80 type=128>',
             '<LogicalRecordSegmentHeader: @ 0x14e6 len=0x69c attr=0x81 type=6>',
             '<LogicalRecordSegmentHeader: @ 0x1b82 len=0x4ce attr=0xa0 type=6>',
             ],
        ),
        (
            0x2050, 0x2000, 0xff01,
            [
                '<LogicalRecordSegmentHeader: @ 0x2054 len=0x226 attr=0xc1 type=6>',
            ]
        ),
    )
)
def test_file_basic_file_iter_LRSHs_for_visible_record_and_logical_data_fragment(position, length, version,
                                                                                 lrsh_expected):
    fobj = io.BytesIO(test_data.BASIC_FILE_WITH_TWO_VISIBLE_RECORDS_NO_IFLRS)
    with File.FileRead(fobj) as file_read:
        visible_record = File.VisibleRecord(None)
        visible_record.position = position
        visible_record.length = length
        visible_record.version = version
        lrsh_list = []
        for lrsh, _by in file_read.iter_LRSHs_for_visible_record_and_logical_data_fragment(visible_record):
            lrsh_list.append(str(lrsh))
        # print()
        # pprint.pprint(lrsh_list)
        assert lrsh_list == lrsh_expected


@pytest.mark.parametrize(
    'by, expected_logical_record_positions',
    (
        (
            test_data.MINIMAL_FILE,
            [
                'LRPosDesc pos: LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 desc: LogicalDataDescription LRSH attr: 0x80 type: 0 len: 120',
                'LRPosDesc pos: LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000000d0 desc: LogicalDataDescription LRSH attr: 0x81 type: 1 len: 504',
            ],
        ),
        (
            test_data.BASIC_FILE_WITH_TWO_VISIBLE_RECORDS_NO_IFLRS,
            [
                'LRPosDesc pos: LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 desc: LogicalDataDescription LRSH attr: 0x80 type: 0 len: 120',
                'LRPosDesc pos: LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000000d0 desc: LogicalDataDescription LRSH attr: 0x81 type: 1 len: 504',
                'LRPosDesc pos: LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000002cc desc: LogicalDataDescription LRSH attr: 0x81 type: 4 len: 200',
                'LRPosDesc pos: LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000398 desc: LogicalDataDescription LRSH attr: 0x80 type: 5 len: 3032',
                'LRPosDesc pos: LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000f74 desc: LogicalDataDescription LRSH attr: 0x80 type: 5 len: 846',
                'LRPosDesc pos: LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000012c6 desc: LogicalDataDescription LRSH attr: 0x80 type: 3 len: 378',
                'LRPosDesc pos: LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001444 desc: LogicalDataDescription LRSH attr: 0x80 type: 128 len: 158',
                'LRPosDesc pos: LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000014e6 desc: LogicalDataDescription LRSH attr: 0x81 type: 6 len: 1688',
                'LRPosDesc pos: LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001b82 desc: LogicalDataDescription LRSH attr: 0xa0 type: 6 len: 1772',
            ],
        ),
    )
)
def test_file_iter_logical_record_positions(by, expected_logical_record_positions):
    fobj = io.BytesIO(by)
    with File.FileRead(fobj) as file_read:
        result = [str(lrp_ldd) for lrp_ldd in file_read.iter_logical_record_positions()]
        # print()
        # pprint.pprint(result, width=200)
        assert result == expected_logical_record_positions


def test_file_iter_logical_record_positions_fails_not_is_first():
    fobj = io.BytesIO(test_data.FILE_WITH_SECOND_LRSH_NOT_FIRST_RECORD)
    with pytest.raises(File.ExceptionLogicalRecordSegmentHeaderSequence) as err:
        with File.FileRead(fobj) as file_read:
            list(file_read.iter_logical_record_positions())
    assert err.value.args[0] == 'Previous LRSH is last but current is not first @ 0xd0'


@pytest.mark.parametrize(
    'by, expected_file_logical_data',
    (
        (
            test_data.MINIMAL_FILE,
            [
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 LR   0 E n <LogicalData Len: 0x78 Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000000d0 LR   1 E n <LogicalData Len: 0x1f7 Idx: 0x0>>',
            ],
        ),
        (
            test_data.BASIC_FILE_WITH_TWO_VISIBLE_RECORDS_NO_IFLRS,
            [
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 LR   0 E n <LogicalData Len: 0x78 Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000000d0 LR   1 E n <LogicalData Len: 0x1f7 Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000002cc LR   4 E n <LogicalData Len: 0xc7 Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000398 LR   5 E n <LogicalData Len: 0xbd8 Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000f74 LR   5 E n <LogicalData Len: 0x34e Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000012c6 LR   3 E n <LogicalData Len: 0x17a Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001444 LR 128 E n <LogicalData Len: 0x9e Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000014e6 LR   6 E n <LogicalData Len: 0x697 Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00001b82 LR   6 E n <LogicalData Len: 0x6eb Idx: 0x0>>'
            ],
        ),
    )
)
def test_file_get_file_logical_data(by, expected_file_logical_data):
    fobj = io.BytesIO(by)
    with File.FileRead(fobj) as file_read:
        result = list(file_read.iter_logical_record_positions())
        lrps = [v[0] for v in result]
        result = [str(file_read.get_file_logical_data(lrp)) for lrp in lrps]
        # print()
        # pprint.pprint(result, width=150)
        assert result == expected_file_logical_data


@pytest.mark.parametrize(
    'by, offset, length, expected_file_logical_data, expected_bytes',
    (
        (
            test_data.MINIMAL_FILE, 0, -1,
            [
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 LR   0 E n <LogicalData Len: 0x78 Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000000d0 LR   1 E n <LogicalData Len: 0x1f7 Idx: 0x0>>',
            ],
            [
                (
                    b'\xf0\x0bFILE-HEADER4\x0fSEQUENCE-NUMBER\x144\x02ID\x14p\x02\x00\x011!\n00000'
                    b'00001!AHES INSITE.1                                                     '
                ),
                (
                    b'\xf0\x06ORIGIN8\x07FILE-ID\x008\rFILE-SET-NAME\x008\x0fFILE-SET-NUMBER\x00'
                    b'8\x0bFILE-NUMBER\x008\tFILE-TYPE\x008\x07PRODUCT\x008\x07VERSION\x008\x08'
                    b'PROGRAMS\x008\rCREATION-TIME\x008\x0cORDER-NUMBER\x008\x0eDESCENT-NUMBER'
                    b'\x008\nRUN-NUMBER\x008\x07WELL-ID\x008\tWELL-NAME\x008\nFIELD-NAME\x008\rP'
                    b'RODUCER-CODE\x008\rPRODUCER-NAME\x008\x07COMPANY\x008\x0fNAME-SPACE-NAME'
                    b'\x008\x12NAME-SPACE-VERSION\x00p\x02\x00\x010-\x01\x14\x0cHES INSITE.1-'
                    b'\x01\x13$BURU ENERGY LIMITED/VALHALLA NORTH 1-\x01\x12\xcfV\xccU-\x01'
                    b'\x12\x01-\x01\x13\x08PLAYBACK-\x01\x14\nHES INSITE-\x01\x14\x06R5.1.4\x00-'
                    b'\x01\x15p\x03\x07\n\x001\x00\x00-\x01\x14\x079262611\x00\x00-\x01\x14\x03N'
                    b'/A-\x01\x14\x10VALHALLA NORTH 1-\x01\x14\x08VALHALLA-\x01\x10\x01\x18-'
                    b'\x01\x14\x0bHalliburton-\x01\x14\x13BURU ENERGY LIMITED\x00\x00'
                )
            ],
        ),
        (
            test_data.MINIMAL_FILE, 16, -1,
            [
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 LR   0 E n <LogicalData Len: 0x68 Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000000d0 LR   1 E n <LogicalData Len: 0x1e7 Idx: 0x0>>',
            ],
            [
                (
                    b'EQUENCE-NUMBER\x144\x02ID\x14p\x02\x00\x011!\n0000000001!AHES INSITE.1     '
                    b'                                                '
                ),
                (
                    b'D\x008\rFILE-SET-NAME\x008\x0fFILE-SET-NUMBER\x008\x0bFILE-NUMBER\x008\tFILE'
                    b'-TYPE\x008\x07PRODUCT\x008\x07VERSION\x008\x08PROGRAMS\x008\rCREATION-TIME'
                    b'\x008\x0cORDER-NUMBER\x008\x0eDESCENT-NUMBER\x008\nRUN-NUMBER\x008\x07WELL'
                    b'-ID\x008\tWELL-NAME\x008\nFIELD-NAME\x008\rPRODUCER-CODE\x008\rPRODUCER-NAME'
                    b'\x008\x07COMPANY\x008\x0fNAME-SPACE-NAME\x008\x12NAME-SPACE-VERSION\x00p\x02'
                    b'\x00\x010-\x01\x14\x0cHES INSITE.1-\x01\x13$BURU ENERGY LIMITED/VALHALLA '
                    b'NORTH 1-\x01\x12\xcfV\xccU-\x01\x12\x01-\x01\x13\x08PLAYBACK-\x01\x14\nHE'
                    b'S INSITE-\x01\x14\x06R5.1.4\x00-\x01\x15p\x03\x07\n\x001\x00\x00-\x01'
                    b'\x14\x079262611\x00\x00-\x01\x14\x03N/A-\x01\x14\x10VALHALLA NORTH 1-\x01'
                    b'\x14\x08VALHALLA-\x01\x10\x01\x18-\x01\x14\x0bHalliburton-\x01\x14\x13BURU E'
                    b'NERGY LIMITED\x00\x00'
                ),
            ],
        ),
        (
            test_data.MINIMAL_FILE, 0, 16,
            [
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 LR   0 E n <LogicalData Len: 0x10 Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000000d0 LR   1 E n <LogicalData Len: 0x10 Idx: 0x0>>',
            ],
            [
                b'\xf0\x0bFILE-HEADER4\x0fS',
                b'\xf0\x06ORIGIN8\x07FILE-I',
            ],
        ),
        (
            test_data.MINIMAL_FILE, 32, 16,
            [
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 LR   0 E n <LogicalData Len: 0x10 Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000000d0 LR   1 E n <LogicalData Len: 0x10 Idx: 0x0>>',
            ],
            [
                b'\x02ID\x14p\x02\x00\x011!\n00000',
                b'E\x008\x0fFILE-SET-NUM',
            ],
        ),
        (
            test_data.MINIMAL_FILE, 0, 0,
            [
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 LR   0 E n <LogicalData Len: 0x0 Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000000d0 LR   1 E n <LogicalData Len: 0x0 Idx: 0x0>>',
            ],
            [
                b'',
                b'',
            ],
        ),
        (
            test_data.MINIMAL_FILE, 32, 0,
            [
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 LR   0 E n <LogicalData Len: 0x0 Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000000d0 LR   1 E n <LogicalData Len: 0x0 Idx: 0x0>>',
            ],
            [
                b'',
                b'',
            ],
        ),
        (
            test_data.MINIMAL_FILE, 0x78, -1,
            [
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 LR   0 E n <LogicalData Len: 0x0 Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000000d0 LR   1 E n <LogicalData Len: 0x17f Idx: 0x0>>',
            ],
            [
                b'',
                (
                    b'TIME\x008\x0cORDER-NUMBER\x008\x0eDESCENT-NUMBER\x008\nRUN-NUMBER\x008\x07'
                    b'WELL-ID\x008\tWELL-NAME\x008\nFIELD-NAME\x008\rPRODUCER-CODE\x008\rPRODUCER-'
                    b'NAME\x008\x07COMPANY\x008\x0fNAME-SPACE-NAME\x008\x12NAME-SPACE-VERSIO'
                    b'N\x00p\x02\x00\x010-\x01\x14\x0cHES INSITE.1-\x01\x13$BURU ENERGY LIMITED/V'
                    b'ALHALLA NORTH 1-\x01\x12\xcfV\xccU-\x01\x12\x01-\x01\x13\x08PLAYBACK-\x01'
                    b'\x14\nHES INSITE-\x01\x14\x06R5.1.4\x00-\x01\x15p\x03\x07\n\x001'
                    b'\x00\x00-\x01\x14\x079262611\x00\x00-\x01\x14\x03N/A-\x01\x14\x10VALHALLA N'
                    b'ORTH 1-\x01\x14\x08VALHALLA-\x01\x10\x01\x18-\x01\x14\x0bHalliburton-\x01'
                    b'\x14\x13BURU ENERGY LIMITED\x00\x00'
                ),
            ],
        ),
        (
            test_data.MINIMAL_FILE, 0x1f7, -1,
            [
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 LR   0 E n <LogicalData Len: 0x0 Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000000d0 LR   1 E n <LogicalData Len: 0x0 Idx: 0x0>>',
            ],
            [
                b'',
                b'',
            ],
        ),
        (
            test_data.MINIMAL_FILE, 0x1f7 + 1, -1,
            [
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x00000054 LR   0 E n <LogicalData Len: 0x0 Idx: 0x0>>',
                '<FileLogicalData LogicalRecordPosition: VR: 0x00000050 LRSH: 0x000000d0 LR   1 E n <LogicalData Len: 0x0 Idx: 0x0>>',
            ],
            [
                b'',
                b'',
            ],
        ),
    )
)
def test_file_get_file_logical_data_partial(by, offset, length, expected_file_logical_data, expected_bytes):
    fobj = io.BytesIO(by)
    with File.FileRead(fobj) as file_read:
        logical_record_pos_desc = list(file_read.iter_logical_record_positions())
        result: typing.List[File.FileLogicalData] = []
        for lrp, lrd in logical_record_pos_desc:
            fld = file_read.get_file_logical_data(lrp, offset, length)
            result.append(fld)
        str_result = [str(v) for v in result]
        # print()
        # pprint.pprint(str_result, width=150)
        assert str_result == expected_file_logical_data
        actual_bytes = [fld.logical_data.bytes for fld in result]
        # pprint.pprint(actual_bytes)
        assert actual_bytes == expected_bytes


def test_file_get_file_logical_data_partial_raises_on_negative_offset():
    fobj = io.BytesIO(test_data.MINIMAL_FILE)
    with File.FileRead(fobj) as file_read:
        lrps = [lrp for lrp in file_read.iter_logical_record_positions()]
        for lrp in lrps:
            with pytest.raises(File.ExceptionFileRead) as err:
                file_read.get_file_logical_data(lrp, offset=-1)
            assert err.value.args[0] == 'offset must be >= 0 not -1'


# ==================== END: Test of FileRead ========================
