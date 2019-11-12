import io

import pytest

from TotalDepth.RP66V1.core import File


def test_read_one_bytes():
    fobj = io.BytesIO(b'\x0f')
    assert File.read_one_byte(fobj) == 0xF


def test_read_one_bytes_raises():
    fobj = io.BytesIO(b'')
    with pytest.raises(File.ExceptionEOF) as err:
        File.read_one_byte(fobj)
    assert err.value.args[0] == 'Premature EOF.'


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


@pytest.mark.parametrize('by', (b'', b'\x00',))
def test_read_two_bytes_big_endian_raises(by):
    fobj = io.BytesIO(by)
    with pytest.raises(File.ExceptionEOF) as err:
        File.read_two_bytes_big_endian(fobj)
    assert err.value.args[0] == 'Premature EOF.'


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




