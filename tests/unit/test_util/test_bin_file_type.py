import io
import typing

import pytest

import TotalDepth.util.bin_file_type


@pytest.mark.parametrize(
    'version_line, groups',
    (
        (
            b' VERS. 2.0: CWLS Log ASCII Standard - VERSION 2.0',
            (b'2.0', b'CWLS Log ASCII Standard - VERSION 2.0'),
        ),
        (
            b'VERS. 2.0: CWLS Log ASCII Standard - VERSION 2.0',
            (b'2.0', b'CWLS Log ASCII Standard - VERSION 2.0'),
        ),
        (
            b'VERS. 2.0 : CWLS Log ASCII Standard - VERSION 2.0',
            (b'2.0', b'CWLS Log ASCII Standard - VERSION 2.0'),
        ),
        (
            b'     VERS.    2.0    :    CWLS Log ASCII Standard - VERSION 2.0   ',
            (b'2.0', b'CWLS Log ASCII Standard - VERSION 2.0'),
        ),
        (
            b' VERS.                 2.0: ',
            (b'2.0', None),
        ),
        (
            b' VERS.                 2.0:',
            (b'2.0', None),
        ),
    )
)
def test_re_las_vers_line(version_line: str, groups: typing.Tuple[str, ...]):
    result = TotalDepth.util.bin_file_type.RE_LAS_VERSION_LINE.match(version_line)
    assert result is not None
    assert result.groups() == groups


@pytest.mark.parametrize(
    'fobj, expected',
    (
        # Physical record type 1
        (io.BytesIO(b'\x00\xFF\x40\x00\x80\x00'), ''),
        # First PR has predecessor
        (io.BytesIO(b'\x00\xFF\x00\x02\x80\x00'), ''),
        # Checksum flags are 10
        (io.BytesIO(b'\x00\xFF\x20\x00\x80\x00'), ''),
        # Checksum flags are both set
        (io.BytesIO(b'\x00\xFF\x30\x00\x80\x00'), ''),
        # Length check with no PRT
        (io.BytesIO(b'\x00\x04\x00\x00\x80\x00'), ''),
        # Length check with checksum
        (io.BytesIO(b'\x00\x06\x10\x00\x80\x00'), ''),
        # Length check with record number
        (io.BytesIO(b'\x00\x06\x04\x00\x80\x00'), ''),
        # Length check with file number
        (io.BytesIO(b'\x00\x06\x02\x00\x80\x00'),''),
        # Length check with checksum, record and file number
        (io.BytesIO(b'\x00\x0A\x16\x00\x80\x00'), ''),
        # Length check passes with checksum, record and file number
        (io.BytesIO(b'\x00\x0B\x16\x00\x80\x00'), 'LIS'),
        # Logical record type is 0
        (io.BytesIO(b'\x00\xFF\x00\x00\x00\x00'), ''),
        # Logical record attributes are non-zero
        (io.BytesIO(b'\x00\xFF\x00\x00\x80\x01'), ''),
        # Test reserved/unused bits set and return code is 0
        (io.BytesIO(b'\x00\x80\x85\x9c\x80\x00'), 'LIS'),
    )
)
def test__lis(fobj: io.BytesIO, expected: int):
    result = TotalDepth.util.bin_file_type._lis(fobj)
    assert result == expected


# Example of a correct initial Phyisical Record and Logical Record Header
LIS_PR_GOOD_BYTES = b'\x00\x3e\x00\x00\x80\x00'


# b'\x00\x00\x00\x00\x00\x00\x00\x00\x90\x00\x00\x00\x00\x84\x80\x00\x83\x00EDI         81/09/22  ETJ.  20814     01            FILE SEQ:DIS-GR,FDC-GR,BHC-GR & NORMALIZED DATA                           \x00\x00\x00\x00\x00\x00\x00\x00 \x01\x00\x00\x00\x84\x80\x00\x85\x00EDI         81/09/22        ETJ20814  01            EDIT/NORM. TAPE OF D.TEXACO A.G. WELL KUDHA-1 LOGGED ON 22-JUL-81         \x01\x00\x00\x00\x90\x00\x00\x00,\x01\x00\x00\x01\x00\x00\x00 \x01\x00\x008\x01\x00\x00'
LIS_MINIMAL = (
    # PR
    b'\x00\x84\x80\x00'
    # LD
    b'\x83\x00EDI         81/09/22  ETJ.  20814     01            FILE SEQ:DIS-GR,FDC-GR,BHC-GR & NORMALIZED DATA                           '
    # PR
    b'\x00\x84\x80\x00'
    # LD
    b'\x85\x00EDI         81/09/22        ETJ20814  01            EDIT/NORM. TAPE OF D.TEXACO A.G. WELL KUDHA-1 LOGGED ON 22-JUL-81         '
)


@pytest.mark.parametrize(
    'byt, expected',
    (
        (b'\x00\x00\x00\x00\x00\x00\x00\x00\x90\x00\x00\x00', 0x90),
        # Reversed.
        (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x90', 0x90),
    )
)
def test__tif_third_word(byt, expected):
    result = TotalDepth.util.bin_file_type._tif_third_word(byt)
    assert result == expected


@pytest.mark.parametrize(
    'byt, expected',
    (
        (b'\x00\x00\x00\x00\x00\x00\x00\x00\x90\x00\x00\x00', True),
        # Reversed.
        (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x90', False),
    )
)
def test__tif_third_word_normal(byt, expected):
    result = TotalDepth.util.bin_file_type._tif_third_word_normal(byt)
    assert result == expected


LIS_TIF_MINIMAL = (
    # TIF
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x90\x00\x00\x00'
    # PR
    b'\x00\x84\x80\x00'
    # LD
    b'\x83\x00EDI         81/09/22  ETJ.  20814     01            FILE SEQ:DIS-GR,FDC-GR,BHC-GR & NORMALIZED DATA                           '
    # TIF
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x20\x01\x00\x00'
    # PR
    b'\x00\x84\x80\x00'
    # LD
    b'\x85\x00EDI         81/09/22        ETJ20814  01            EDIT/NORM. TAPE OF D.TEXACO A.G. WELL KUDHA-1 LOGGED ON 22-JUL-81         '
    # TIF EOF
    b'\x01\x00\x00\x00\x90\x00\x00\x00\x2c\x01\x00\x00'
    # TIF EOF
    b'\x01\x00\x00\x00\x20\x01\x00\x00\x38\x01\x00\x00'
)


LIS_TIF_REVERSED_MINIMAL = (
    # TIF @ 0x0
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x90'
    # PR
    b'\x00\x84\x80\x00'
    # LD
    b'\x83\x00EDI         81/09/22  ETJ.  20814     01            FILE SEQ:DIS-GR,FDC-GR,BHC-GR & NORMALIZED DATA                           '
    # TIF @ 0x90
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x20'
    # PR
    b'\x00\x84\x80\x00'
    # LD
    b'\x85\x00EDI         81/09/22        ETJ20814  01            EDIT/NORM. TAPE OF D.TEXACO A.G. WELL KUDHA-1 LOGGED ON 22-JUL-81         '
    # TIF EOF @ 0x120
    b'\x00\x00\x00\x01\x00\x00\x00\x90\x00\x00\x01\x2c'
    # TIF EOF @ 0x12c
    b'\x00\x00\x00\x01\x00\x00\x01\x20\x00\x00\x01\x38'
)


@pytest.mark.parametrize(
    'fobj, expected',
    (
        (io.BytesIO(LIS_MINIMAL), 'LIS'),
        # Typical TIF OK
        (io.BytesIO(LIS_TIF_MINIMAL), 'LISt'),
        # Typical TIF reversed
        (io.BytesIO(LIS_TIF_REVERSED_MINIMAL), 'LIStr'),
    )
)
def test__lis(fobj: io.BytesIO, expected: int):
    result = TotalDepth.util.bin_file_type._lis(fobj)
    assert result == expected


@pytest.mark.parametrize(
    'fobj, expected',
    (
        # Success
        (
            io.BytesIO(b'\n'.join(
                [
                    b'~VERSION INFORMATION',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            'LAS1.2'
        ),
        (
            io.BytesIO(b'\n'.join(
                [
                    b'~Version Information',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            'LAS1.2'
        ),
        (
            io.BytesIO(b'\n'.join(
                [
                    b'~Version Information Section',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            'LAS1.2'
        ),
        (
            io.BytesIO(b'\n'.join(
                [
                    b'~V',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            'LAS1.2'
        ),
        (
            io.BytesIO(b'\n'.join(
                [
                    b'~Version Information Block',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            'LAS1.2'
        ),
        # No space prefix and '1.2:CWLS' rather than '1.2: CWLS'
        (
            io.BytesIO(b'\n'.join(
                [
                    b'~V',
                    b'VERS. 1.2:CWLS Log ASCII Standard - VERSION 1.2',
                    b'WRAP. NO:One line per depth step',
                ]
            )),
            'LAS1.2'
        ),
        # Comment line(s)
        (
            io.BytesIO(b'\n'.join(
                [
                    b'# Some comment or other',
                    b'~VERSION INFORMATION',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            'LAS1.2'
        ),
        # Comment line(s)
        (
            io.BytesIO(b'\n'.join(
                [
                    b'# Some comment or other',
                    b'# Some comment or other',
                    b'# Some comment or other',
                    b'# Some comment or other',
                    b'# Some comment or other',
                    b'# Some comment or other',
                    b'# Some comment or other',
                    b'~VERSION INFORMATION',
                    b'# Some comment or other',
                    b'# Some comment or other',
                    b'# Some comment or other',
                    b'# Some comment or other',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            'LAS1.2'
        ),
        # Blank lines
        (
            io.BytesIO(b'\n'.join(
                [
                    b'   ',
                    b'~VERSION INFORMATION',
                    b'',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            'LAS1.2'
        ),
        # Failure
        (
            io.BytesIO(b'\n'.join(
                [
                    b'~NOT VERSION INFORMATION',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            ''
        ),
        (
            io.BytesIO(b'\n'.join(
                [
                    b'~V',
                    b' NOTVERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            ''
        ),
        (
            io.BytesIO(b'\n'.join(
                [
                    b'~V',
                    b' VERS.',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            ''
        ),
        (
            io.BytesIO(b'\n'.join(
                [
                    b'~V',
                    b' VERS.                 1.9:   CWLS LOG ASCII STANDARD -VERSION 1.9',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            ''
        ),
        (io.BytesIO(b'\n'), ''),
    )
)
def test__las(fobj: io.BytesIO, expected: int):
    result = TotalDepth.util.bin_file_type._las(fobj, b'1.2')#(b'1.2:', b'1.2'))
    assert result == expected


@pytest.mark.parametrize(
    'fobj, expected',
    (
        # Success
        (
            io.BytesIO(b'\n'.join(
                [
                    b'~VERSION INFORMATION',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            'LAS1.2'
        ),
    )
)
def test__las12(fobj: io.BytesIO, expected: int):
    result = TotalDepth.util.bin_file_type._lasv12(fobj)
    assert result == expected


@pytest.mark.parametrize(
    'fobj, expected',
    (
        # Success
        (
            io.BytesIO(b'\n'.join(
                [
                    b'~VERSION INFORMATION',
                    b' VERS.                 2.0:   CWLS LOG ASCII STANDARD -VERSION 2.0',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            'LAS2.0'
        ),
    )
)
def test__las20(fobj: io.BytesIO, expected: int):
    result = TotalDepth.util.bin_file_type._lasv20(fobj)
    assert result == expected


@pytest.mark.parametrize(
    'fobj, expected',
    (
        # Success
        (
            io.BytesIO(b'\n'.join(
                [
                    b'~VERSION INFORMATION',
                    b' VERS.                 3.0:   CWLS LOG ASCII STANDARD -VERSION 3.0',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            'LAS3.0'
        ),
    )
)
def test__las30(fobj: io.BytesIO, expected: int):
    result = TotalDepth.util.bin_file_type._lasv30(fobj)
    assert result == expected


# Typical RP66v1
# 00000000: 2020 2031 5631 2e30 3052 4543 4f52 4420     1V1.00RECORD
# 00000010: 3831 3932 4465 6661 756c 7420 5374 6f72  8192Default Stor
# 00000020: 6167 6520 5365 7420 2020 2020 2020 2020  age Set
# 00000030: 2020 2020 2020 2020 2020 2020 2020 2020
# 00000040: 2020 2020 2020 2020 2020 2020 2020 2020
# 00000050: 1ffc ff01 007c 8000 f00b 4649 4c45 2d48  .....|....FILE-H


@pytest.mark.parametrize(
    'fobj, expected',
    (
        (
            # Good example
            io.BytesIO(b''.join(
                [
                    b'\x20\x20\x20\x31', # Storage Unit Sequence Number, 4 bytes
                    b'\x56\x31\x2e\x30\x30', # DLIS version, 5 bytes
                    b'\x52\x45\x43\x4f\x52\x44', # Storage unit structure, 6 bytes, b'RECORD'
                    b'\x20\x38\x31\x39\x32', # Maximum record length, 5 bytes
                    # Storage set identifier, 60 bytes, b'Default Storage Set...'
                    b'\x44\x65\x66\x61\x75\x6c\x74\x20\x53\x74\x6f\x72',
                    b'\x61\x67\x65\x20\x53\x65\x74\x20\x20\x20\x20\x20\x20\x20\x20\x20',
                    b'\x20' * 16,
                    b'\x20' * 16,
                ]
            )),
            'RP66V1',
        ),
        (
            # Missing sequence number, byte[3]
            io.BytesIO(b''.join(
                [
                    b'\x20\x20\x20\x20', # Storage Unit Sequence Number, 4 bytes
                    b'\x56\x31\x2e\x30\x30', # DLIS version, 5 bytes
                    b'\x52\x45\x43\x4f\x52\x44', # Storage unit structure, 6 bytes, b'RECORD'
                    b'\x20\x38\x31\x39\x32', # Maximum record length, 5 bytes
                    # Storage set identifier, 60 bytes, b'Default Storage Set...'
                    b'\x44\x65\x66\x61\x75\x6c\x74\x20\x53\x74\x6f\x72',
                    b'\x61\x67\x65\x20\x53\x65\x74\x20\x20\x20\x20\x20\x20\x20\x20\x20',
                    b'\x20' * 16,
                    b'\x20' * 16,
                ]
            )),
            '',
        ),
        (
            # Bad version, initial bytes are not 'V1.'
            io.BytesIO(b''.join(
                [
                    b'\x20\x20\x20\x31',  # Storage Unit Sequence Number, 4 bytes
                    b'X\x31\x2e\x31\x31',  # DLIS version, 5 bytes
                    b'\x52\x45\x43\x4f\x52\x44',  # Storage unit structure, 6 bytes, b'RECORD'
                    b'\x20\x38\x31\x39\x32',  # Maximum record length, 5 bytes
                    # Storage set identifier, 60 bytes, b'Default Storage Set...'
                    b'\x44\x65\x66\x61\x75\x6c\x74\x20\x53\x74\x6f\x72',
                    b'\x61\x67\x65\x20\x53\x65\x74\x20\x20\x20\x20\x20\x20\x20\x20\x20',
                    b'\x20' * 16,
                    b'\x20' * 16,
                ]
            )),
            '',
        ),
        (
            # Bad version, minor number is spaces
            io.BytesIO(b''.join(
                [
                    b'\x20\x20\x20\x31',  # Storage Unit Sequence Number, 4 bytes
                    b'\x56\x31\x2e\x20\x20',  # DLIS version, 5 bytes
                    b'\x52\x45\x43\x4f\x52\x44',  # Storage unit structure, 6 bytes, b'RECORD'
                    b'\x20\x38\x31\x39\x32',  # Maximum record length, 5 bytes
                    # Storage set identifier, 60 bytes, b'Default Storage Set...'
                    b'\x44\x65\x66\x61\x75\x6c\x74\x20\x53\x74\x6f\x72',
                    b'\x61\x67\x65\x20\x53\x65\x74\x20\x20\x20\x20\x20\x20\x20\x20\x20',
                    b'\x20' * 16,
                    b'\x20' * 16,
                ]
            )),
            '',
        ),
        (
            # Storage unit structure is not b'RECORD'
            io.BytesIO(b''.join(
                [
                    b'\x20\x20\x20\x31',  # Storage Unit Sequence Number, 4 bytes
                    b'\x56\x31\x2e\x30\x30',  # DLIS version, 5 bytes
                    b'XXXXXX',  # Storage unit structure, 6 bytes, b'RECORD'
                    b'\x20\x38\x31\x39\x32',  # Maximum record length, 5 bytes
                    # Storage set identifier, 60 bytes, b'Default Storage Set...'
                    b'\x44\x65\x66\x61\x75\x6c\x74\x20\x53\x74\x6f\x72',
                    b'\x61\x67\x65\x20\x53\x65\x74\x20\x20\x20\x20\x20\x20\x20\x20\x20',
                    b'\x20' * 16,
                    b'\x20' * 16,
                ]
            )),
            '',
        ),
        (
            # Maximum Record Length is not a number, (last byte is a space)
            io.BytesIO(b''.join(
                [
                    b'\x20\x20\x20\x31',  # Storage Unit Sequence Number, 4 bytes
                    b'\x56\x31\x2e\x30\x30',  # DLIS version, 5 bytes
                    b'\x52\x45\x43\x4f\x52\x44',  # Storage unit structure, 6 bytes, b'RECORD'
                    b'\x20\x38\x31\x39\x20',  # Maximum record length, 5 bytes
                    # Storage set identifier, 60 bytes, b'Default Storage Set...'
                    b'\x44\x65\x66\x61\x75\x6c\x74\x20\x53\x74\x6f\x72',
                    b'\x61\x67\x65\x20\x53\x65\x74\x20\x20\x20\x20\x20\x20\x20\x20\x20',
                    b'\x20' * 16,
                    b'\x20' * 16,
                ]
            )),
            '',
        ),
        (
            # Storage Set Identifier - too short (last field)
            io.BytesIO(b''.join(
                [
                    b'\x20\x20\x20\x31',  # Storage Unit Sequence Number, 4 bytes
                    b'\x56\x31\x2e\x30\x30',  # DLIS version, 5 bytes
                    b'\x52\x45\x43\x4f\x52\x44',  # Storage unit structure, 6 bytes, b'RECORD'
                    b'\x20\x38\x31\x39\x32',  # Maximum record length, 5 bytes
                    # Storage set identifier, 60 bytes, b'Default Storage Set...'
                    b'\x44\x65\x66\x61\x75\x6c\x74\x20\x53\x74\x6f\x72',
                    b'\x61\x67\x65\x20\x53\x65\x74\x20\x20\x20\x20\x20\x20\x20\x20\x20',
                    b'\x20' * 16,
                    (b'\x20' * 15),
                ]
            )),
            '',
        ),
        (
            # Storage Set Identifier - non-printable bytes (last field)
            io.BytesIO(b''.join(
                [
                    b'\x20\x20\x20\x31',  # Storage Unit Sequence Number, 4 bytes
                    b'\x56\x31\x2e\x30\x30',  # DLIS version, 5 bytes
                    b'\x52\x45\x43\x4f\x52\x44',  # Storage unit structure, 6 bytes, b'RECORD'
                    b'\x20\x38\x31\x39\x32',  # Maximum record length, 5 bytes
                    # Storage set identifier, 60 bytes, b'Default Storage Set...'
                    b'\x44\x65\x66\x61\x75\x6c\x74\x20\x53\x74\x6f\x72',
                    b'\x61\x67\x65\x20\x53\x65\x74\x20\x20\x20\x20\x20\x20\x20\x20\x20',
                    b'\x20' * 16,
                    b'\x00' * 16,
                ]
            )),
            '',
        ),
    )
)
def test__rp66v1(fobj: io.BytesIO, expected: int):
    result = TotalDepth.util.bin_file_type._rp66v1(fobj)
    assert result == expected


@pytest.mark.parametrize(
    'fobj, expected',
    (
        (
            # Good example
            io.BytesIO(b''.join(
                [
                    # TIF
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x5c\x00\x00\x00'
                    # RP66V1
                    b'\x20\x20\x20\x31', # Storage Unit Sequence Number, 4 bytes
                    b'\x56\x31\x2e\x30\x30', # DLIS version, 5 bytes
                    b'\x52\x45\x43\x4f\x52\x44', # Storage unit structure, 6 bytes, b'RECORD'
                    b'\x20\x38\x31\x39\x32', # Maximum record length, 5 bytes
                    # Storage set identifier, 60 bytes, b'Default Storage Set...'
                    b'\x44\x65\x66\x61\x75\x6c\x74\x20\x53\x74\x6f\x72',
                    b'\x61\x67\x65\x20\x53\x65\x74\x20\x20\x20\x20\x20\x20\x20\x20\x20',
                    b'\x20' * 16,
                    b'\x20' * 16,
                ]
            )),
            'RP66V1t',
        ),
    )
)
def test__rp66v1_tif(fobj: io.BytesIO, expected: int):
    result = TotalDepth.util.bin_file_type._rp66v1_tif(fobj)
    assert result == expected


@pytest.mark.parametrize(
    'fobj, expected',
    (
        (
            # Good example
            io.BytesIO(b''.join(
                [
                    # TIF
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x5c'
                    # RP66V1
                    b'\x20\x20\x20\x31', # Storage Unit Sequence Number, 4 bytes
                    b'\x56\x31\x2e\x30\x30', # DLIS version, 5 bytes
                    b'\x52\x45\x43\x4f\x52\x44', # Storage unit structure, 6 bytes, b'RECORD'
                    b'\x20\x38\x31\x39\x32', # Maximum record length, 5 bytes
                    # Storage set identifier, 60 bytes, b'Default Storage Set...'
                    b'\x44\x65\x66\x61\x75\x6c\x74\x20\x53\x74\x6f\x72',
                    b'\x61\x67\x65\x20\x53\x65\x74\x20\x20\x20\x20\x20\x20\x20\x20\x20',
                    b'\x20' * 16,
                    b'\x20' * 16,
                ]
            )),
            'RP66V1tr',
        ),
    )
)
def test__rp66v1_tif_r(fobj: io.BytesIO, expected: int):
    result = TotalDepth.util.bin_file_type._rp66v1_tif_r(fobj)
    assert result == expected


SEGY_EMPTY = b''.join(
    [
        b'\xc3\xf0\xf1@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf0\xf2@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf0\xf3@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf0\xf4@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf0\xf5@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf0\xf6@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf0\xf7@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf0\xf8@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf0\xf9@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf1\xf0@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf1\xf1@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf1\xf2@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
        b'\xc3\xf1\xf3@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
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
    ])

def test_segy():
    file = io.BytesIO(SEGY_EMPTY)
    result = TotalDepth.util.bin_file_type._segy(file)
    assert result == 'SEGY'


@pytest.mark.parametrize(
    'fobj, expected',
    (
        (io.BytesIO(b''), 'ASCII'),
        (io.BytesIO(b'PK'), 'ASCII'),
    )
)
def test__ascii(fobj: io.BytesIO, expected: int):
    result = TotalDepth.util.bin_file_type._ascii(fobj)
    assert result == expected


@pytest.mark.parametrize(
    'fobj, expected',
    (
        # Typical ZIP OK
        (io.BytesIO(b'PK\x03\x04'), 'ZIP'),
        # ZIP bad
        (io.BytesIO(b'PK\x03\x05'), ''),
    )
)
def test__zip(fobj: io.BytesIO, expected: int):
    result = TotalDepth.util.bin_file_type._zip(fobj)
    assert result == expected


@pytest.mark.parametrize(
    'fobj, expected',
    (
        # Typical PDF OK
        (io.BytesIO(b'%PDF-'), 'PDF'),
        # PDF bad
        (io.BytesIO(b'%PDFX'), ''),
    )
)
def test__pdf(fobj: io.BytesIO, expected: int):
    result = TotalDepth.util.bin_file_type._pdf(fobj)
    assert result == expected


@pytest.mark.parametrize(
    'fobj, expected',
    (
            # Typical OK
            (io.BytesIO(b"""UTIM Unix Time sec
DATE Date ddmmyy
TIME Time hhmmss
WAC Wits Activity Code unitless
BDIA Bit Diameter inch
NPEN n-Pentane ppm
EPEN Neo-Pentane ppm
UTIM DATE TIME WAC BDIA NPEN EPEN
1165665017 09Dec06 11-50-17 0 8.50 0 0
"""), 'DAT'),
            # Missing frame
            (io.BytesIO(b"""UTIM Unix Time sec
DATE Date ddmmyy
TIME Time hhmmss
WAC Wits Activity Code unitless
BDIA Bit Diameter inch
NPEN n-Pentane ppm
EPEN Neo-Pentane ppm
UTIM DATE TIME WAC BDIA NPEN EPEN
"""), ''),
            # Missing channel definitions
            (io.BytesIO(b"""
UTIM DATE TIME WAC BDIA NPEN EPEN
1165665017 09Dec06 11-50-17 0 8.50 0 0
"""), ''),
            # Empty string
            (io.BytesIO(b""""""), ''),
    )
)
def test__dat(fobj: io.BytesIO, expected: int):
    result = TotalDepth.util.bin_file_type._dat(fobj)
    assert result == expected


EXAMPLE_BIT_FILE = (
    b'\x00\x00\x00\x00\x00\x00\x00\x00 \x01\x00\x00\x00\x00\x00\x00OCCIDENTAL P'
    b'ETROLEUM                                                    \x00\x02\x00\x06'
    b'\x00U  15/17-12                                                            '
    b'    \x00\x07\x00\x17\x008  \x00\x11\x00\x00SSN LSN SSD LSD CAL TEN SPD THZ '
    b'UZ  KZ  GR  DEN CORRCN  TH  U   K               D.\x8c\x00\x00\x00\x00\x00'
    b'@@\x00\x00\x00\x00\x00\x00B \x00\x00X 227D 8\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\xac\t\x00\x00C\x11o\x8eC\x11o\xbfC\x11p\xcbC\x11s&C\x11v\x8fC\x11z\xbc'
    b'C\x11~\xf5C\x11\x82\x1fC\x11\x83\tC\x11\x81\x99C\x11~iC\x11zVC\x11v\xd3'
    b'C\x11u\xa6C\x11w\xdaC\x11}\x16C\x11\x84\\C\x11\x8c\xaaC\x11\x94\x8d'
    b'C\x11\x9b\x19C\x11\xa0fC\x11\xa4\xabC\x11\xa8VC\x11\xab\xe4C\x11\xae\xfe'
    b'C\x11\xb0;C\x11\xae\x84C\x11\xa8\xe1C\x11\x9f\xacC\x11\x95\rC\x11\x8b\xa8'
    b'C\x11\x85\xd2B\x95\xfc)B\x95\xfc)B\x95\xfc)B\x95\xfc)B\x95\xf7\xa1'
    b'B\x95\xce\x9eB\x95?(B\x94/\xb8B\x92\xe3\xbdB\x91\xc8\xd5B\x919\x9aB\x91Y\xdc'
    b'B\x92!\\B\x93D\xdeB\x94U\x8fB\x95\x01\xbdB\x957SB\x951\xccB\x95\t8'
    b'B\x94\xb9\x8dB\x94mWB\x94K\x08B\x94T\xffB\x94`IB\x94L^B\x94\x06\xf6B\x93xK'
    b'B\x92\x9f\xc4B\x91\x9a\xa7B\x90\xaa\xb4B\x90\x17\xfcB\x8f\xf6YB\xf9\xf9\x9c'
    b'B\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9c'
    b'B\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9c'
    b'B\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9c'
    b'B\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9c'
    b'B\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9c'
    b'B\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9cB\xf9\xf9\x9c'
    b'B\xf9\xf9\x9cBl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7'
    b'Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7'
    b'Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7Bl\xfd7'
    b'Bl\xfd7Bl\xfd7Bl\xfd7A0\xc1\x11A0\xc1\x11A0\xc1\x11A0\xc1\x11A0\xc1\x11'
)

@pytest.mark.parametrize(
    'fobj, expected',
    (
        # Typical OK
        (io.BytesIO(EXAMPLE_BIT_FILE), 'BIT'),
        # Empty string
        (io.BytesIO(b""""""), ''),
    )
)
def test__bit(fobj: io.BytesIO, expected: int):
    result = TotalDepth.util.bin_file_type._bit(fobj)
    assert result == expected


@pytest.mark.parametrize(
    'fobj, expected',
    (
        (io.BytesIO(b'PK\x03\x04'), 'ZIP'),
        (io.BytesIO(b'%PDF-'), 'PDF'),
        # Need extra bytes so that TIF can be tested as well.
        (io.BytesIO(LIS_MINIMAL), 'LIS'),
        (io.BytesIO(LIS_TIF_MINIMAL), 'LISt'),
        (io.BytesIO(LIS_TIF_REVERSED_MINIMAL), 'LIStr'),
        (
            io.BytesIO(b'\n'.join(
                [
                    b'~VERSION INFORMATION',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            'LAS1.2',
        ),
        (
            io.BytesIO(b'\n'.join(
                [
                    b'~VERSION INFORMATION',
                    b' VERS.                 2.0:   CWLS LOG ASCII STANDARD -VERSION 2.0',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            'LAS2.0',
        ),
        (
            io.BytesIO(b'\n'.join(
                [
                    b'~VERSION INFORMATION',
                    b' VERS.                 3.0:   CWLS LOG ASCII STANDARD -VERSION 3.0',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            )),
            'LAS3.0',
        ),
        (
            io.BytesIO(b''.join(
                [
                    b'\x20\x20\x20\x31',  # Storage Unit Sequence Number, 4 bytes
                    b'\x56\x31\x2e\x30\x30',  # DLIS version, 5 bytes
                    b'\x52\x45\x43\x4f\x52\x44',  # Storage unit structure, 6 bytes, b'RECORD'
                    b'\x20\x38\x31\x39\x32',  # Maximum record length, 5 bytes
                    # Storage set identifier, 60 bytes, b'Default Storage Set...'
                    b'\x44\x65\x66\x61\x75\x6c\x74\x20\x53\x74\x6f\x72',
                    b'\x61\x67\x65\x20\x53\x65\x74\x20\x20\x20\x20\x20\x20\x20\x20\x20',
                    b'\x20' * 16,
                    b'\x20' * 16,
                ],
            )),
            'RP66V1',
        ),
        (
            # RP66V1 with a TIF marker.
            io.BytesIO(b''.join(
                [
                    # TIF
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x5c\x00\x00\x00'
                    # RP66V1
                    b'\x20\x20\x20\x31',  # Storage Unit Sequence Number, 4 bytes
                    b'\x56\x31\x2e\x30\x30',  # DLIS version, 5 bytes
                    b'\x52\x45\x43\x4f\x52\x44',  # Storage unit structure, 6 bytes, b'RECORD'
                    b'\x20\x38\x31\x39\x32',  # Maximum record length, 5 bytes
                    # Storage set identifier, 60 bytes, b'Default Storage Set...'
                    b'\x44\x65\x66\x61\x75\x6c\x74\x20\x53\x74\x6f\x72',
                    b'\x61\x67\x65\x20\x53\x65\x74\x20\x20\x20\x20\x20\x20\x20\x20\x20',
                    b'\x20' * 16,
                    b'\x20' * 16,
                ]
            )),
            'RP66V1t',
        ),
        (
            # RP66V1 with a reversed TIF marker.
            io.BytesIO(b''.join(
                [
                    # TIF
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x5c'
                    # RP66V1
                    b'\x20\x20\x20\x31',  # Storage Unit Sequence Number, 4 bytes
                    b'\x56\x31\x2e\x30\x30',  # DLIS version, 5 bytes
                    b'\x52\x45\x43\x4f\x52\x44',  # Storage unit structure, 6 bytes, b'RECORD'
                    b'\x20\x38\x31\x39\x32',  # Maximum record length, 5 bytes
                    # Storage set identifier, 60 bytes, b'Default Storage Set...'
                    b'\x44\x65\x66\x61\x75\x6c\x74\x20\x53\x74\x6f\x72',
                    b'\x61\x67\x65\x20\x53\x65\x74\x20\x20\x20\x20\x20\x20\x20\x20\x20',
                    b'\x20' * 16,
                    b'\x20' * 16,
                ]
            )),
            'RP66V1tr',
        ),
        (
            # Short DAT file.
            io.BytesIO(b"""UTIM Unix Time sec
DATE Date ddmmyy
TIME Time hhmmss
WAC Wits Activity Code unitless
BDIA Bit Diameter inch
NPEN n-Pentane ppm
EPEN Neo-Pentane ppm
UTIM DATE TIME WAC BDIA NPEN EPEN
1165665017 09Dec06 11-50-17 0 8.50 0 0
"""),
            'DAT',
        ),
        (io.BytesIO(SEGY_EMPTY), 'SEGY',),
        (io.BytesIO(EXAMPLE_BIT_FILE), 'BIT'),
    )
)
def test_binary_file_type_from_bytes(fobj: io.BytesIO, expected: str):
    result = TotalDepth.util.bin_file_type.binary_file_type(fobj)
    assert result == expected
