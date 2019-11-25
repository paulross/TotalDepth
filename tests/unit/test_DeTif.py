import io

import pytest

from TotalDepth import DeTif


TIF_EMPTY_FILE = b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x0c\x00\x00\x00' \
    + b'\x01\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x18\x00\x00\x00' \
    + b'\x01\x00\x00\x00' + b'\x0c\x00\x00\x00' + b'\x24\x00\x00\x00'


TIF_EIGHT_BYTES_FILE = b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x14\x00\x00\x00' \
    + b'\x01\x02\x03\x04\x05\x06\x07\x08' \
    + b'\x01\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x20\x00\x00\x00' \
    + b'\x01\x00\x00\x00' + b'\x14\x00\x00\x00' + b'\x2c\x00\x00\x00'


@pytest.mark.parametrize(
    'file_in, has_tif',
    (
        (io.BytesIO(TIF_EMPTY_FILE), True),
        (io.BytesIO(TIF_EIGHT_BYTES_FILE), True),
        (io.BytesIO(b''), False),
    )
)
def test_has_tif_file(file_in, has_tif):
    file_out  =io.BytesIO()
    result = DeTif.has_tif_file(file_in)
    assert result == has_tif


def test_scan_empty_file():
    fobj = io.BytesIO(TIF_EMPTY_FILE)
    tifs = DeTif.tif_scan_file_object(fobj)
    # print(tifs)
    expected = [
        DeTif.TifMarker(0, 0, 0, 12),
        DeTif.TifMarker(12, 1, 0, 24),
        DeTif.TifMarker(24, 1, 12, 36),
    ]
    assert tifs == expected


def test_scan_empty_file_and_stringify():
    fobj = io.BytesIO(TIF_EMPTY_FILE)
    tifs = DeTif.tif_scan_file_object(fobj)
    result = '\n'.join(str(t) for t in tifs)
    # print(tifs)
    expected = """TifMarker: 0x00000000 Type: 0x00000000 Prev: 0x00000000 Next: 0x0000000c
TifMarker: 0x0000000c Type: 0x00000001 Prev: 0x00000000 Next: 0x00000018
TifMarker: 0x00000018 Type: 0x00000001 Prev: 0x0000000c Next: 0x00000024"""
    assert result == expected


def test_tif_too_short_error():
    fobj = io.BytesIO(b'')
    with pytest.raises(DeTif.DeTifExceptionRead) as err:
        DeTif.tif_scan_file_object(fobj)
    assert err.value.args[0].startswith('Could not read TIF marker: ')


def test_is_tif_start_error():
    fobj = io.BytesIO(b'\x01\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x0c\x00\x00\x00')
    with pytest.raises(DeTif.DeTifExceptionRead) as err:
        DeTif.tif_scan_file_object(fobj)
    exp = 'Initial TIF marker is wrong type: TifMarker: 0x00000000 Type: 0x00000001 Prev: 0x00000000 Next: 0x0000000c'
    assert err.value.args[0] == exp



@pytest.mark.parametrize(
    'file_in, expected_bytes_written, expected_tif_markers_stripped',
    (
        (io.BytesIO(TIF_EMPTY_FILE), 0, 3),
        (io.BytesIO(TIF_EIGHT_BYTES_FILE), 8, 3),
    )
)
def test_strip_tif(file_in, expected_bytes_written, expected_tif_markers_stripped):
    file_out = io.BytesIO()
    tif_markers_stripped, bytes_written = DeTif.strip_tif(file_in, file_out)
    assert bytes_written == expected_bytes_written
    assert tif_markers_stripped == expected_tif_markers_stripped
    assert len(file_out.getvalue()) == bytes_written


@pytest.mark.parametrize(
    'file_in, file_size, expected_errors',
    (
        (io.BytesIO(TIF_EMPTY_FILE), 3 * 12, []),
        (io.BytesIO(TIF_EIGHT_BYTES_FILE), 3 * 12 + 8, []),
    )
)
def test_get_errors(file_in, file_size, expected_errors):
    tifs = DeTif.tif_scan_file_object(file_in)
    result = DeTif.get_errors(tifs, file_size)
    # print(result)
    assert result == expected_errors

