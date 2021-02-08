import collections
import string

import pytest

from TotalDepth.util import EBCDIC

EBCDIC_SEGY_EXAMPLE = b''.join(
    [
        b'\xc3\xf0\xf1\xc3\x96\x94\x97\x81\x95\xa8@@z@\xc1\x97\x81\x83\x88\x85@\xc5\x95\x85\x99\x87\xa8@\xd3\xa3\x84K@@z@@\xe3\x81\x97\x85@\xc4\x81\xa3\x85@z@\xf0\xf5K\xf0\xf5K\xf2\xf0\xf0\xf0@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf0\xf2\xc3\xd6\xd5\xe3\xd9\xc1\xc3\xe3\xd6\xd9@z@\xc3\xc7\xc7@@@\xd7\xd9\xd6\xc3\xc5\xe2\xe2\xc9\xd5\xc7@z@\xe2\xa8\x95\xa3\x88\x85\xa3\x89\x83@\xe2\x85\x89\xa2\x94\x96\x87\x99\x81\x94K@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf0\xf3\xc3\xd9\xc5\xc1\xe3\xc5\xc4@\xc2\xe8@\xc7\xc5\xd6\xe5\xc5\xc3\xe3\xc5\xe4\xd9N@\xc9\xd5@\xe2\xc5\xc7\xe8@\xc9\xd5@\xc9\xd5\xc4\xd6\xd5\xc5\xe2\xc9\xc1@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf0\xf4\xe6\xc5\xd3\xd3@z@\xc2\xc1\xd2\xc5\xd9`\xf1@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf0\xf5\xd4\xc1\xd9\xc9\xd5\xc5@@\xe6\xc5\xd3\xd3@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf0\xf6\xe2\xd6\xe4\xd9\xc3\xc5@z@\xe2\x93\x85\x85\xa5\x85@\xc7\xa4\x95@\xc1\x99\x99\x81\xa8K@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf0\xf7K@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf0\xf8\xe2\xd6\xe4\xd9\xc3\xc5@\xd4\xd6\xd5\xc9\xe3\xd6\xd9@\xc1\xe3@\xf4\xd4@\xc2\xc5\xd3\xd6\xe6@\xc1\xc8\xc4@z@@\xe6\xc1\xe3\xc5\xd9@\xc4\xc5\xd7\xe3\xc8@z@\xf3\xf0K\xf1\xd4@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf0\xf9\xe6\xc5\xd3\xd3@\xd3\xd6\xc3\xc1\xe3\xc9\xd6\xd5@z@\xf1\xf1\xf5\xc4\xc5\xc7@\xf4\xf4}@\xf2\xf9K\xf5\xf9\xf0\x7f@\xc5\x81\xa2\xa3@^@\xf2\xf0\xc4\xc5\xc7@\xf3\xf9}@\xf2\xf3K\xf4\xf4\xf5\x7f@\xe2\x96\xa4\xa3\x88K@@@@@@@@@@@',
        b'\xc3\xf1\xf0\xd9\xc5\xc6\xc5\xd9\xc5\xd5\xc3\xc5@\xd3\xc5\xe5\xc5\xd3@z@\xd9\xe3@\xc1\xe3@\xf3\xf2K\xf9\xd4@\xc1\xc2\xd6\xe5\xc5@\xc1\xc8\xc4K@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf1\xf1\xc6\xc9\xd3\xc5\xe2@\xd6\xd5@\xc4\xc9\xe2\xc3z@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf1\xf2\xc6\xc9\xd3\xc5@\xf1@z@\xe2\xa8\x95\xa3\x88\x85\xa3\x89\x83@\xe3\x99\x81\x83\x85@M\xd7\xe6\xe3\xd3]@\x83\x96\x95\xa5\x96\x93\xa5\x85\x84@\xa6\x89\xa3\x88@\xf2\xf5@\xc8@@\xe9\xd7@\xd9\x89\x83\x92\x85\x99@@@@@@@@@@@@@@@',
        b'\xc3\xf1\xf3K@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf1\xf4@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf1\xf5@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf1\xf6@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf1\xf7@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf1\xf8@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf1\xf9@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf2\xf0@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf2\xf1@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf2\xf2@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf2\xf3@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf2\xf4@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf2\xf5@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf2\xf6@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf2\xf7@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf2\xf8@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf2\xf9@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf3\xf0@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf3\xf1@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf3\xf2@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf3\xf3@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf3\xf4@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf3\xf5@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf3\xf6@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf3\xf7@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf3\xf8@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf3\xf9@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf4\xf0@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
    ]
)


def test_segy_example_histogram():
    counter = collections.Counter(EBCDIC_SEGY_EXAMPLE)
    expected = {64: 2716, 195: 52, 197: 31, 240: 21, 242: 20, 241: 19, 243: 18, 217: 15, 193: 14, 211: 14, 227: 14,
                214: 14, 122: 13, 133: 13, 75: 13, 226: 13, 213: 11, 201: 11, 245: 10, 244: 10, 163: 9, 196: 9, 129: 8,
                199: 8, 249: 8, 149: 6, 131: 6, 153: 6, 230: 6, 150: 5, 168: 5, 136: 5, 137: 5, 212: 5, 215: 4, 194: 4,
                246: 4, 247: 4, 248: 4, 200: 4, 148: 3, 151: 3, 229: 3, 228: 3, 165: 3, 198: 3, 135: 2, 132: 2, 162: 2,
                232: 2, 147: 2, 164: 2, 125: 2, 127: 2, 78: 1, 210: 1, 96: 1, 94: 1, 77: 1, 93: 1, 166: 1, 233: 1,
                146: 1}
    # print(counter)
    # for k in sorted(counter.keys()):
    #     print(f'{k:3d} : {counter[k]:4d},')
    assert counter == expected


def test_segy_example_ascii_histogram():
    ascii_str = EBCDIC.ebcdic_to_ascii(EBCDIC_SEGY_EXAMPLE)
    counter = collections.Counter(ascii_str)
    expected = {' ': 2716, 'C': 52, 'E': 31, '0': 21, '2': 20, '1': 19, '3': 18, 'R': 15, 'A': 14, 'L': 14, 'T': 14,
                'O': 14, ':': 13, 'e': 13, '.': 13, 'S': 13, 'N': 11, 'I': 11, '5': 10, '4': 10, 't': 9, 'D': 9, 'a': 8,
                'G': 8, '9': 8, 'n': 6, 'c': 6, 'r': 6, 'W': 6, 'o': 5, 'y': 5, 'h': 5, 'i': 5, 'M': 5, 'P': 4, 'B': 4,
                '6': 4, '7': 4, '8': 4, 'H': 4, 'm': 3, 'p': 3, 'V': 3, 'U': 3, 'v': 3, 'F': 3, 'g': 2, 'd': 2, 's': 2,
                'Y': 2, 'l': 2, 'u': 2, "'": 2, '"': 2, '+': 1, 'K': 1, '-': 1, ';': 1, '(': 1, ')': 1, 'w': 1, 'Z': 1,
                'k': 1}
    # print(counter)
    # for k in sorted(counter.keys()):
    #     print(f'{k:} : {counter[k]:4d},')
    assert counter == expected


def test_segy_example_ebcdic_printable():
    result = EBCDIC.ebcdic_all_printable(EBCDIC_SEGY_EXAMPLE)
    assert result


def test_all_bytes_to_ascii():
    byt = bytes(i for i in range(256))
    ascii_str = EBCDIC.ebcdic_to_ascii(byt)
    # print(ascii_str)
    assert len(ascii_str) == 256


def test_ebcdic_to_ascii_round_trip_ascii_to_ebcdic():
    byt = bytes(i for i in range(256))
    ascii_str = EBCDIC.ebcdic_to_ascii(byt)
    # print(ascii_str)
    assert len(ascii_str) == 256
    result = EBCDIC.ascii_to_ebcdic(ascii_str)
    assert result == byt


def test_ascii_printable_to_ebcdic_printable():
    # ebcdic_printable_chars = EBCDIC.ascii_to_ebcdic(string.printable)
    # print()
    # print(set(ebcdic_printable_chars))
    # for char in ebcdic_chars:
    #     assert char in EBCDIC.EBCDIC_PRINTABLE
    # print(string.printable)
    for ascii_char in string.printable:
        ebcdic_char = EBCDIC.ascii_to_ebcdic(ascii_char)[0]
        print(f'ASCII={ord(ascii_char)} "{ascii_char}" EBCDIC={ebcdic_char}')
        assert ebcdic_char in EBCDIC.EBCDIC_PRINTABLE


def test_ebcdic_printable_to_ascii_printable():
    # ebcdic_printable_chars = EBCDIC.ascii_to_ebcdic(string.printable)
    # print()
    # print(set(ebcdic_printable_chars))
    # for char in ebcdic_chars:
    #     assert char in EBCDIC.EBCDIC_PRINTABLE
    # print(string.printable)
    for ebcdic_char in EBCDIC.EBCDIC_PRINTABLE:
        ascii_char = EBCDIC.ebcdic_to_ascii(bytes([ebcdic_char]))[0]
        print(f'ASCII={ord(ascii_char)} "{ascii_char}" EBCDIC={ebcdic_char}')
        assert ascii_char in string.printable


@pytest.mark.parametrize(
    'ebcdic_bytes, expected',
    (
        (b'\x00', '0'),
        (b'\x41', '65'),
        (b'\xc1', '193'),
    )
)
def test_ebcdic_ascii_description_decimal_str(ebcdic_bytes, expected):
    result = EBCDIC.ebcdic_ascii_description(ebcdic_bytes)
    assert result.decimal_str == expected


@pytest.mark.parametrize(
    'ebcdic_bytes, expected',
    (
        (b'\x00', '00'),
        (b'\x41', '41'),
        (b'\xc1', 'C1'),
    )
)
def test_ebcdic_ascii_description_hex_str(ebcdic_bytes, expected):
    result = EBCDIC.ebcdic_ascii_description(ebcdic_bytes)
    assert result.hex_str == expected


@pytest.mark.parametrize(
    'ebcdic_bytes, expected',
    (
        (b'\x00', 'Ctrl-@'),
        (b'\x41', ''),
        (b'\xc1', ''),
    )
)
def test_ebcdic_ascii_description_ctrl_char(ebcdic_bytes, expected):
    result = EBCDIC.ebcdic_ascii_description(ebcdic_bytes)
    assert result.ctrl_char == expected


@pytest.mark.parametrize(
    'ebcdic_bytes, expected',
    (
        (b'\x00', 'NUL'),
        (b'\x41', 'A'),
        (b'\xc1', ''),
    )
)
def test_ebcdic_ascii_description_ascii(ebcdic_bytes, expected):
    result = EBCDIC.ebcdic_ascii_description(ebcdic_bytes)
    assert result.ascii == expected


@pytest.mark.parametrize(
    'ebcdic_bytes, expected',
    (
        (b'\x00', 'null'),
        (b'\x41', ''),
        (b'\xc1', ''),
    )
)
def test_ebcdic_ascii_description_ascii_meaning(ebcdic_bytes, expected):
    result = EBCDIC.ebcdic_ascii_description(ebcdic_bytes)
    assert result.ascii_meaning == expected


@pytest.mark.parametrize(
    'ebcdic_bytes, expected',
    (
        (b'\x00', 'NUL'),
        (b'\x41', ''),
        (b'\xc1', 'A'),
    )
)
def test_ebcdic_ascii_description_ebcdic(ebcdic_bytes, expected):
    result = EBCDIC.ebcdic_ascii_description(ebcdic_bytes)
    assert result.ebcdic == expected


@pytest.mark.parametrize(
    'ebcdic_bytes, expected',
    (
        (b'\x00', 'null'),
        (b'\x41', ''),
        (b'\xc1', ''),
    )
)
def test_ebcdic_ascii_description_ebcdic_meaning(ebcdic_bytes, expected):
    result = EBCDIC.ebcdic_ascii_description(ebcdic_bytes)
    assert result.ebcdic_meaning == expected


@pytest.mark.parametrize(
    'ebcdic_bytes, expected',
    (
        (b'\x00', 0),
        (b'\x41', 65),
        (b'\xc1', 193),
    )
)
def test_ebcdic_ascii_description_value(ebcdic_bytes, expected):
    result = EBCDIC.ebcdic_ascii_description(ebcdic_bytes)
    assert result.value == expected


@pytest.mark.parametrize(
    'ebcdic_bytes, expected',
    (
        (b'\x00', True),
        (b'\x41', False),
        (b'\xc1', False),
    )
)
def test_ebcdic_ascii_description_is_ctrl(ebcdic_bytes, expected):
    result = EBCDIC.ebcdic_ascii_description(ebcdic_bytes)
    assert result.is_ctrl == expected


@pytest.mark.parametrize(
    'ebcdic_bytes, expected',
    (
        (b'\x00', '@'),
        (b'\x41', ''),
        (b'\xc1', ''),
    )
)
def test_ebcdic_ascii_description_ctrl_symbol(ebcdic_bytes, expected):
    result = EBCDIC.ebcdic_ascii_description(ebcdic_bytes)
    assert result.ctrl_symbol == expected


@pytest.mark.parametrize(
    'ebcdic_bytes, expected',
    (
        (b'\x00', False),
        (b'\x41', False),
        (b'\xc1', True),
    )
)
def test_ebcdic_ascii_description_ebcdic_printable(ebcdic_bytes, expected):
    result = EBCDIC.ebcdic_ascii_description(ebcdic_bytes)
    assert result.ebcdic_printable == expected





