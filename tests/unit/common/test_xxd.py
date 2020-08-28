import pytest

from TotalDepth.common import xxd


@pytest.mark.parametrize(
    'by, expected',
    (
        (b'', ''),
        (b'\x00', '0 00                                      .               '),
        (b'\x00' * 16, '00 0000 0000 0000 0000 0000 0000 0000 0000 ................'),
        (b'\x00' * 17,"""00 0000 0000 0000 0000 0000 0000 0000 0000 ................
10 00                                      .               """),
        (bytes(range(0x100)), """000 0001 0203 0405 0607 0809 0a0b 0c0d 0e0f ................
010 1011 1213 1415 1617 1819 1a1b 1c1d 1e1f ................
020 2021 2223 2425 2627 2829 2a2b 2c2d 2e2f  !"#$%&'()*+,-./
030 3031 3233 3435 3637 3839 3a3b 3c3d 3e3f 0123456789:;<=>?
040 4041 4243 4445 4647 4849 4a4b 4c4d 4e4f @ABCDEFGHIJKLMNO
050 5051 5253 5455 5657 5859 5a5b 5c5d 5e5f PQRSTUVWXYZ[\\]^_
060 6061 6263 6465 6667 6869 6a6b 6c6d 6e6f `abcdefghijklmno
070 7071 7273 7475 7677 7879 7a7b 7c7d 7e7f pqrstuvwxyz{|}~.
080 8081 8283 8485 8687 8889 8a8b 8c8d 8e8f ................
090 9091 9293 9495 9697 9899 9a9b 9c9d 9e9f ................
0a0 a0a1 a2a3 a4a5 a6a7 a8a9 aaab acad aeaf ................
0b0 b0b1 b2b3 b4b5 b6b7 b8b9 babb bcbd bebf ................
0c0 c0c1 c2c3 c4c5 c6c7 c8c9 cacb cccd cecf ................
0d0 d0d1 d2d3 d4d5 d6d7 d8d9 dadb dcdd dedf ................
0e0 e0e1 e2e3 e4e5 e6e7 e8e9 eaeb eced eeef ................
0f0 f0f1 f2f3 f4f5 f6f7 f8f9 fafb fcfd feff ................"""),
    )
)
def test_xxd(by, expected):
    result = xxd.xxd(by)
    # print(f'TRACE: "{result}"')
    assert result == expected


@pytest.mark.parametrize(
    'by, columns, expected',
    (
        (
            bytes(range(0x100)), 16, """000 0001 0203 0405 0607 0809 0a0b 0c0d 0e0f ................
010 1011 1213 1415 1617 1819 1a1b 1c1d 1e1f ................
020 2021 2223 2425 2627 2829 2a2b 2c2d 2e2f  !"#$%&'()*+,-./
030 3031 3233 3435 3637 3839 3a3b 3c3d 3e3f 0123456789:;<=>?
040 4041 4243 4445 4647 4849 4a4b 4c4d 4e4f @ABCDEFGHIJKLMNO
050 5051 5253 5455 5657 5859 5a5b 5c5d 5e5f PQRSTUVWXYZ[\\]^_
060 6061 6263 6465 6667 6869 6a6b 6c6d 6e6f `abcdefghijklmno
070 7071 7273 7475 7677 7879 7a7b 7c7d 7e7f pqrstuvwxyz{|}~.
080 8081 8283 8485 8687 8889 8a8b 8c8d 8e8f ................
090 9091 9293 9495 9697 9899 9a9b 9c9d 9e9f ................
0a0 a0a1 a2a3 a4a5 a6a7 a8a9 aaab acad aeaf ................
0b0 b0b1 b2b3 b4b5 b6b7 b8b9 babb bcbd bebf ................
0c0 c0c1 c2c3 c4c5 c6c7 c8c9 cacb cccd cecf ................
0d0 d0d1 d2d3 d4d5 d6d7 d8d9 dadb dcdd dedf ................
0e0 e0e1 e2e3 e4e5 e6e7 e8e9 eaeb eced eeef ................
0f0 f0f1 f2f3 f4f5 f6f7 f8f9 fafb fcfd feff ................"""
        ),
        (
            bytes(range(0x100)), 8, """000 0001 0203 0405 0607 ........
008 0809 0a0b 0c0d 0e0f ........
010 1011 1213 1415 1617 ........
018 1819 1a1b 1c1d 1e1f ........
020 2021 2223 2425 2627  !"#$%&'
028 2829 2a2b 2c2d 2e2f ()*+,-./
030 3031 3233 3435 3637 01234567
038 3839 3a3b 3c3d 3e3f 89:;<=>?
040 4041 4243 4445 4647 @ABCDEFG
048 4849 4a4b 4c4d 4e4f HIJKLMNO
050 5051 5253 5455 5657 PQRSTUVW
058 5859 5a5b 5c5d 5e5f XYZ[\\]^_
060 6061 6263 6465 6667 `abcdefg
068 6869 6a6b 6c6d 6e6f hijklmno
070 7071 7273 7475 7677 pqrstuvw
078 7879 7a7b 7c7d 7e7f xyz{|}~.
080 8081 8283 8485 8687 ........
088 8889 8a8b 8c8d 8e8f ........
090 9091 9293 9495 9697 ........
098 9899 9a9b 9c9d 9e9f ........
0a0 a0a1 a2a3 a4a5 a6a7 ........
0a8 a8a9 aaab acad aeaf ........
0b0 b0b1 b2b3 b4b5 b6b7 ........
0b8 b8b9 babb bcbd bebf ........
0c0 c0c1 c2c3 c4c5 c6c7 ........
0c8 c8c9 cacb cccd cecf ........
0d0 d0d1 d2d3 d4d5 d6d7 ........
0d8 d8d9 dadb dcdd dedf ........
0e0 e0e1 e2e3 e4e5 e6e7 ........
0e8 e8e9 eaeb eced eeef ........
0f0 f0f1 f2f3 f4f5 f6f7 ........
0f8 f8f9 fafb fcfd feff ........"""
         ),
        (
            bytes(range(0x100)), 32, """000 0001 0203 0405 0607 0809 0a0b 0c0d 0e0f 1011 1213 1415 1617 1819 1a1b 1c1d 1e1f ................................
020 2021 2223 2425 2627 2829 2a2b 2c2d 2e2f 3031 3233 3435 3637 3839 3a3b 3c3d 3e3f  !"#$%&'()*+,-./0123456789:;<=>?
040 4041 4243 4445 4647 4849 4a4b 4c4d 4e4f 5051 5253 5455 5657 5859 5a5b 5c5d 5e5f @ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_
060 6061 6263 6465 6667 6869 6a6b 6c6d 6e6f 7071 7273 7475 7677 7879 7a7b 7c7d 7e7f `abcdefghijklmnopqrstuvwxyz{|}~.
080 8081 8283 8485 8687 8889 8a8b 8c8d 8e8f 9091 9293 9495 9697 9899 9a9b 9c9d 9e9f ................................
0a0 a0a1 a2a3 a4a5 a6a7 a8a9 aaab acad aeaf b0b1 b2b3 b4b5 b6b7 b8b9 babb bcbd bebf ................................
0c0 c0c1 c2c3 c4c5 c6c7 c8c9 cacb cccd cecf d0d1 d2d3 d4d5 d6d7 d8d9 dadb dcdd dedf ................................
0e0 e0e1 e2e3 e4e5 e6e7 e8e9 eaeb eced eeef f0f1 f2f3 f4f5 f6f7 f8f9 fafb fcfd feff ................................"""
         ),
    ),
)
def test_xxd_columns(by, columns, expected):
    result = xxd.xxd(by, columns=columns)
    # print(f'TRACE: "{result}"')
    assert result == expected


@pytest.mark.parametrize(
    'by, expected',
    (
        (bytes(range(0x100)), """000 0001 0203 0405 0607 0809 0A0B 0C0D 0E0F ................
010 1011 1213 1415 1617 1819 1A1B 1C1D 1E1F ................
020 2021 2223 2425 2627 2829 2A2B 2C2D 2E2F  !"#$%&'()*+,-./
030 3031 3233 3435 3637 3839 3A3B 3C3D 3E3F 0123456789:;<=>?
040 4041 4243 4445 4647 4849 4A4B 4C4D 4E4F @ABCDEFGHIJKLMNO
050 5051 5253 5455 5657 5859 5A5B 5C5D 5E5F PQRSTUVWXYZ[\\]^_
060 6061 6263 6465 6667 6869 6A6B 6C6D 6E6F `abcdefghijklmno
070 7071 7273 7475 7677 7879 7A7B 7C7D 7E7F pqrstuvwxyz{|}~.
080 8081 8283 8485 8687 8889 8A8B 8C8D 8E8F ................
090 9091 9293 9495 9697 9899 9A9B 9C9D 9E9F ................
0a0 A0A1 A2A3 A4A5 A6A7 A8A9 AAAB ACAD AEAF ................
0b0 B0B1 B2B3 B4B5 B6B7 B8B9 BABB BCBD BEBF ................
0c0 C0C1 C2C3 C4C5 C6C7 C8C9 CACB CCCD CECF ................
0d0 D0D1 D2D3 D4D5 D6D7 D8D9 DADB DCDD DEDF ................
0e0 E0E1 E2E3 E4E5 E6E7 E8E9 EAEB ECED EEEF ................
0f0 F0F1 F2F3 F4F5 F6F7 F8F9 FAFB FCFD FEFF ................"""),
    )
)
def test_xxd_uppercase(by, expected):
    result = xxd.xxd(by, uppercase=True)
    # print(f'TRACE: "{result}"')
    assert result == expected


@pytest.mark.parametrize(
    'by, expected',
    (
        (bytes(range(0x100)), """000 0001 0203 0405 0607 0809 0a0b 0c0d 0e0f ................
010 1011 1213 1415 1617 1819 1a1b 1c1d 1e1f ................
020 2021 2223 2425 2627 2829 2a2b 2c2d 2e2f ................
030 3031 3233 3435 3637 3839 3a3b 3c3d 3e3f ................
040 4041 4243 4445 4647 4849 4a4b 4c4d 4e4f  .........[.<(+!
050 5051 5253 5455 5657 5859 5a5b 5c5d 5e5f &.........]$*);^
060 6061 6263 6465 6667 6869 6a6b 6c6d 6e6f -/.........,%_>?
070 7071 7273 7475 7677 7879 7a7b 7c7d 7e7f .........`:#@'="
080 8081 8283 8485 8687 8889 8a8b 8c8d 8e8f .abcdefghi......
090 9091 9293 9495 9697 9899 9a9b 9c9d 9e9f .jklmnopqr......
0a0 a0a1 a2a3 a4a5 a6a7 a8a9 aaab acad aeaf .~stuvwxyz......
0b0 b0b1 b2b3 b4b5 b6b7 b8b9 babb bcbd bebf ...........|....
0c0 c0c1 c2c3 c4c5 c6c7 c8c9 cacb cccd cecf {ABCDEFGHI......
0d0 d0d1 d2d3 d4d5 d6d7 d8d9 dadb dcdd dedf }JKLMNOPQR......
0e0 e0e1 e2e3 e4e5 e6e7 e8e9 eaeb eced eeef \\.STUVWXYZ......
0f0 f0f1 f2f3 f4f5 f6f7 f8f9 fafb fcfd feff 0123456789......"""),
    )
)
def test_xxd_ebcdic(by, expected):
    result = xxd.xxd(by, ebcdic=True)
    # print(f'TRACE: "{result}"')
    assert result == expected


@pytest.mark.parametrize(
    'by, expected',
    (
        (bytes(range(0x100)), """000 00000000 00000001 00000010 00000011 00000100 00000101 00000110 00000111 00001000 00001001 00001010 00001011 00001100 00001101 00001110 00001111 ................
010 00010000 00010001 00010010 00010011 00010100 00010101 00010110 00010111 00011000 00011001 00011010 00011011 00011100 00011101 00011110 00011111 ................
020 00100000 00100001 00100010 00100011 00100100 00100101 00100110 00100111 00101000 00101001 00101010 00101011 00101100 00101101 00101110 00101111  !"#$%&'()*+,-./
030 00110000 00110001 00110010 00110011 00110100 00110101 00110110 00110111 00111000 00111001 00111010 00111011 00111100 00111101 00111110 00111111 0123456789:;<=>?
040 01000000 01000001 01000010 01000011 01000100 01000101 01000110 01000111 01001000 01001001 01001010 01001011 01001100 01001101 01001110 01001111 @ABCDEFGHIJKLMNO
050 01010000 01010001 01010010 01010011 01010100 01010101 01010110 01010111 01011000 01011001 01011010 01011011 01011100 01011101 01011110 01011111 PQRSTUVWXYZ[\\]^_
060 01100000 01100001 01100010 01100011 01100100 01100101 01100110 01100111 01101000 01101001 01101010 01101011 01101100 01101101 01101110 01101111 `abcdefghijklmno
070 01110000 01110001 01110010 01110011 01110100 01110101 01110110 01110111 01111000 01111001 01111010 01111011 01111100 01111101 01111110 01111111 pqrstuvwxyz{|}~.
080 10000000 10000001 10000010 10000011 10000100 10000101 10000110 10000111 10001000 10001001 10001010 10001011 10001100 10001101 10001110 10001111 ................
090 10010000 10010001 10010010 10010011 10010100 10010101 10010110 10010111 10011000 10011001 10011010 10011011 10011100 10011101 10011110 10011111 ................
0a0 10100000 10100001 10100010 10100011 10100100 10100101 10100110 10100111 10101000 10101001 10101010 10101011 10101100 10101101 10101110 10101111 ................
0b0 10110000 10110001 10110010 10110011 10110100 10110101 10110110 10110111 10111000 10111001 10111010 10111011 10111100 10111101 10111110 10111111 ................
0c0 11000000 11000001 11000010 11000011 11000100 11000101 11000110 11000111 11001000 11001001 11001010 11001011 11001100 11001101 11001110 11001111 ................
0d0 11010000 11010001 11010010 11010011 11010100 11010101 11010110 11010111 11011000 11011001 11011010 11011011 11011100 11011101 11011110 11011111 ................
0e0 11100000 11100001 11100010 11100011 11100100 11100101 11100110 11100111 11101000 11101001 11101010 11101011 11101100 11101101 11101110 11101111 ................
0f0 11110000 11110001 11110010 11110011 11110100 11110101 11110110 11110111 11111000 11111001 11111010 11111011 11111100 11111101 11111110 11111111 ................"""),
    )
)
def test_xxd_binary(by, expected):
    result = xxd.xxd(by, binary=True)
    # print(f'TRACE: "{result}"')
    assert result == expected


@pytest.mark.parametrize(
    'by, length, expected',
    (
        (
            bytes(range(0x100)), 256, """000 0001 0203 0405 0607 0809 0a0b 0c0d 0e0f ................
010 1011 1213 1415 1617 1819 1a1b 1c1d 1e1f ................
020 2021 2223 2425 2627 2829 2a2b 2c2d 2e2f  !"#$%&'()*+,-./
030 3031 3233 3435 3637 3839 3a3b 3c3d 3e3f 0123456789:;<=>?
040 4041 4243 4445 4647 4849 4a4b 4c4d 4e4f @ABCDEFGHIJKLMNO
050 5051 5253 5455 5657 5859 5a5b 5c5d 5e5f PQRSTUVWXYZ[\\]^_
060 6061 6263 6465 6667 6869 6a6b 6c6d 6e6f `abcdefghijklmno
070 7071 7273 7475 7677 7879 7a7b 7c7d 7e7f pqrstuvwxyz{|}~.
080 8081 8283 8485 8687 8889 8a8b 8c8d 8e8f ................
090 9091 9293 9495 9697 9899 9a9b 9c9d 9e9f ................
0a0 a0a1 a2a3 a4a5 a6a7 a8a9 aaab acad aeaf ................
0b0 b0b1 b2b3 b4b5 b6b7 b8b9 babb bcbd bebf ................
0c0 c0c1 c2c3 c4c5 c6c7 c8c9 cacb cccd cecf ................
0d0 d0d1 d2d3 d4d5 d6d7 d8d9 dadb dcdd dedf ................
0e0 e0e1 e2e3 e4e5 e6e7 e8e9 eaeb eced eeef ................
0f0 f0f1 f2f3 f4f5 f6f7 f8f9 fafb fcfd feff ................"""
        ),
        (
            bytes(range(0x100)), 16, """00 0001 0203 0405 0607 0809 0a0b 0c0d 0e0f ................"""
         ),
    ),
)
def test_xxd_length(by, length, expected):
    result = xxd.xxd(by, length=length)
    # print(f'TRACE: "{result}"')
    assert result == expected


@pytest.mark.parametrize(
    'by, offset, expected',
    (
        (
            bytes(range(0x100)), 0, """000 0001 0203 0405 0607 0809 0a0b 0c0d 0e0f ................
010 1011 1213 1415 1617 1819 1a1b 1c1d 1e1f ................
020 2021 2223 2425 2627 2829 2a2b 2c2d 2e2f  !"#$%&'()*+,-./
030 3031 3233 3435 3637 3839 3a3b 3c3d 3e3f 0123456789:;<=>?
040 4041 4243 4445 4647 4849 4a4b 4c4d 4e4f @ABCDEFGHIJKLMNO
050 5051 5253 5455 5657 5859 5a5b 5c5d 5e5f PQRSTUVWXYZ[\\]^_
060 6061 6263 6465 6667 6869 6a6b 6c6d 6e6f `abcdefghijklmno
070 7071 7273 7475 7677 7879 7a7b 7c7d 7e7f pqrstuvwxyz{|}~.
080 8081 8283 8485 8687 8889 8a8b 8c8d 8e8f ................
090 9091 9293 9495 9697 9899 9a9b 9c9d 9e9f ................
0a0 a0a1 a2a3 a4a5 a6a7 a8a9 aaab acad aeaf ................
0b0 b0b1 b2b3 b4b5 b6b7 b8b9 babb bcbd bebf ................
0c0 c0c1 c2c3 c4c5 c6c7 c8c9 cacb cccd cecf ................
0d0 d0d1 d2d3 d4d5 d6d7 d8d9 dadb dcdd dedf ................
0e0 e0e1 e2e3 e4e5 e6e7 e8e9 eaeb eced eeef ................
0f0 f0f1 f2f3 f4f5 f6f7 f8f9 fafb fcfd feff ................"""
        ),
        (
            bytes(range(0x100)), 32, """020 0001 0203 0405 0607 0809 0a0b 0c0d 0e0f ................
030 1011 1213 1415 1617 1819 1a1b 1c1d 1e1f ................
040 2021 2223 2425 2627 2829 2a2b 2c2d 2e2f  !"#$%&'()*+,-./
050 3031 3233 3435 3637 3839 3a3b 3c3d 3e3f 0123456789:;<=>?
060 4041 4243 4445 4647 4849 4a4b 4c4d 4e4f @ABCDEFGHIJKLMNO
070 5051 5253 5455 5657 5859 5a5b 5c5d 5e5f PQRSTUVWXYZ[\\]^_
080 6061 6263 6465 6667 6869 6a6b 6c6d 6e6f `abcdefghijklmno
090 7071 7273 7475 7677 7879 7a7b 7c7d 7e7f pqrstuvwxyz{|}~.
0a0 8081 8283 8485 8687 8889 8a8b 8c8d 8e8f ................
0b0 9091 9293 9495 9697 9899 9a9b 9c9d 9e9f ................
0c0 a0a1 a2a3 a4a5 a6a7 a8a9 aaab acad aeaf ................
0d0 b0b1 b2b3 b4b5 b6b7 b8b9 babb bcbd bebf ................
0e0 c0c1 c2c3 c4c5 c6c7 c8c9 cacb cccd cecf ................
0f0 d0d1 d2d3 d4d5 d6d7 d8d9 dadb dcdd dedf ................
100 e0e1 e2e3 e4e5 e6e7 e8e9 eaeb eced eeef ................
110 f0f1 f2f3 f4f5 f6f7 f8f9 fafb fcfd feff ................"""
         ),
    ),
)
def test_xxd_offset(by, offset, expected):
    result = xxd.xxd(by, offset=offset)
    # print(f'TRACE: "{result}"')
    assert result == expected


@pytest.mark.parametrize(
    'by, seek, expected',
    (
        (
            bytes(range(0x100)), 0, """000 0001 0203 0405 0607 0809 0a0b 0c0d 0e0f ................
010 1011 1213 1415 1617 1819 1a1b 1c1d 1e1f ................
020 2021 2223 2425 2627 2829 2a2b 2c2d 2e2f  !"#$%&'()*+,-./
030 3031 3233 3435 3637 3839 3a3b 3c3d 3e3f 0123456789:;<=>?
040 4041 4243 4445 4647 4849 4a4b 4c4d 4e4f @ABCDEFGHIJKLMNO
050 5051 5253 5455 5657 5859 5a5b 5c5d 5e5f PQRSTUVWXYZ[\\]^_
060 6061 6263 6465 6667 6869 6a6b 6c6d 6e6f `abcdefghijklmno
070 7071 7273 7475 7677 7879 7a7b 7c7d 7e7f pqrstuvwxyz{|}~.
080 8081 8283 8485 8687 8889 8a8b 8c8d 8e8f ................
090 9091 9293 9495 9697 9899 9a9b 9c9d 9e9f ................
0a0 a0a1 a2a3 a4a5 a6a7 a8a9 aaab acad aeaf ................
0b0 b0b1 b2b3 b4b5 b6b7 b8b9 babb bcbd bebf ................
0c0 c0c1 c2c3 c4c5 c6c7 c8c9 cacb cccd cecf ................
0d0 d0d1 d2d3 d4d5 d6d7 d8d9 dadb dcdd dedf ................
0e0 e0e1 e2e3 e4e5 e6e7 e8e9 eaeb eced eeef ................
0f0 f0f1 f2f3 f4f5 f6f7 f8f9 fafb fcfd feff ................"""
        ),
        (
            bytes(range(0x100)), 32, """20 2021 2223 2425 2627 2829 2a2b 2c2d 2e2f  !"#$%&'()*+,-./
30 3031 3233 3435 3637 3839 3a3b 3c3d 3e3f 0123456789:;<=>?
40 4041 4243 4445 4647 4849 4a4b 4c4d 4e4f @ABCDEFGHIJKLMNO
50 5051 5253 5455 5657 5859 5a5b 5c5d 5e5f PQRSTUVWXYZ[\\]^_
60 6061 6263 6465 6667 6869 6a6b 6c6d 6e6f `abcdefghijklmno
70 7071 7273 7475 7677 7879 7a7b 7c7d 7e7f pqrstuvwxyz{|}~.
80 8081 8283 8485 8687 8889 8a8b 8c8d 8e8f ................
90 9091 9293 9495 9697 9899 9a9b 9c9d 9e9f ................
a0 a0a1 a2a3 a4a5 a6a7 a8a9 aaab acad aeaf ................
b0 b0b1 b2b3 b4b5 b6b7 b8b9 babb bcbd bebf ................
c0 c0c1 c2c3 c4c5 c6c7 c8c9 cacb cccd cecf ................
d0 d0d1 d2d3 d4d5 d6d7 d8d9 dadb dcdd dedf ................
e0 e0e1 e2e3 e4e5 e6e7 e8e9 eaeb eced eeef ................
f0 f0f1 f2f3 f4f5 f6f7 f8f9 fafb fcfd feff ................"""
         ),
    ),
)
def test_xxd_seek(by, seek, expected):
    result = xxd.xxd(by, seek=seek)
    # print(f'TRACE: "{result}"')
    assert result == expected
