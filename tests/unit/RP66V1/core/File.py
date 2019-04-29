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
    'by, length, expected',
    (
        (b'\x00\x01\x02\x03', 0, b''),
        (b'\x00\x01\x02\x03', 1, b'\x00'),
        (b'\x00\x01\x02\x03', 2, b'\x00\x01'),
        (b'\x00\x01\x02\x03', 3, b'\x00\x01\x02'),
        (b'\x00\x01\x02\x03', 4, b'\x00\x01\x02\x03'),
    )
)
def test_read_two_bytes_big_endian(by, length, expected):
    fobj = io.BytesIO(by)
    assert File.read_n_bytes(fobj, length) == expected


