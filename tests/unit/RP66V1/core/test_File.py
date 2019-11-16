import io

import pytest

from TotalDepth.RP66V1.core import File

from . import test_data
# from tests.unit.RP66V1.core import test_data


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
    'by, position, length, attributes, record_type',
    (
        (b'\x01\x00\xff\x01', 0, 256, 255, 1,),
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
    assert lrsh.is_first == is_first
    assert lrsh.is_last == is_last
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
    assert lrsh.has_checksum == has_checksum
    assert lrsh.has_trailing_length == has_trailing_length
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
    assert lrsh.is_encrypted == is_encrypted
    assert lrsh.has_pad_bytes == has_pad_bytes
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
    assert lrsh.has_encryption_packet== has_encryption_packet
    assert fobj.read() == b''


@pytest.mark.parametrize(
    'by, position, length, attributes, record_type',
    (
        (b'\x01\x00\xff\x01', 0, 256, 255, 1,),
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
    assert lrsh.attribute_str() == expected
    assert fobj.read() == b''


def test_LogicalRecordPosition_ctor():
    fobj = io.BytesIO(
        b''.join([
            b'\x00' * File.StorageUnitLabel.SIZE,  # Simulated Storage Unit Label
            b'\x01\x00\xff\x01',  # Visible record: position=0, length=256, type=0xff01),
            b'\x00\x80\x9f\x01',  # LRSH: position=4, length=128, attributes=0x9f, type=1
        ])
    )
    sul = fobj.read(File.StorageUnitLabel.SIZE)
    vr = File.VisibleRecord(fobj)
    lrsh = File.LogicalRecordSegmentHeader(fobj)
    assert fobj.read() == b''
    lrp = File.LogicalRecordPosition(vr, lrsh)
    assert lrp.vr_position == 80
    assert lrp.lrsh_position == 84


@pytest.mark.parametrize(
    'sul_length, vr_bytes, lrsh_bytes, expected',
    (
        # VR Prior to SUL
        (79, b'\x01\x00\xff\x01', b'\x00\x80\x9f\x01', 'VisibleRecord at 0x53 must be >= 0x50'),
        # TODO: Remove VR/LRSH checks, replace by asserts.
        # (None, b'\x00\x0f\xff\x01', b'\x00\x80\x9f\x01', 'VisibleRecord at 0x53 must be >= 0x50'),
    )
)
def test_LogicalRecordPosition_ctor_raises(sul_length, vr_bytes, lrsh_bytes, expected):
    if sul_length is None:
        sul_length = File.StorageUnitLabel.SIZE
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
        (b'\x01\x00\xff\x01', 4),
    )
)
def test_logical_data_ctor(by, length):
    ld = File.LogicalData(by)
    assert ld.index == 0
    assert ld.remain == length
