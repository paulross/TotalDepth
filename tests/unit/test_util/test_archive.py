

from TotalDepth.util import archive

import pytest


@pytest.mark.parametrize(
    'by, expected',
    (
        # Physical record type 1
        (b'\x00\xFF\x40\x00\x80\x00', 10),
        # First PR has predecessor
        (b'\x00\xFF\x00\x02\x80\x00', 20),
        # Checksum flags are 10
        (b'\x00\xFF\x20\x00\x80\x00', 30),
        # Checksum flags are both set
        (b'\x00\xFF\x30\x00\x80\x00', 40),
        # Length check with no PRT
        (b'\x00\x04\x00\x00\x80\x00', 50),
        # Length check with checksum
        (b'\x00\x06\x10\x00\x80\x00', 50),
        # Length check with record number
        (b'\x00\x06\x04\x00\x80\x00', 50),
        # Length check with file number
        (b'\x00\x06\x02\x00\x80\x00', 50),
        # Length check with checksum, record and file number
        (b'\x00\x0A\x16\x00\x80\x00', 50),
        # Length check passes with checksum, record and file number
        (b'\x00\x0B\x16\x00\x80\x00', 0),
        # Logical record type is 0
        (b'\x00\xFF\x00\x00\x00\x00', 60),
        # Logical record attributes are non-zero
        (b'\x00\xFF\x00\x00\x80\x01', 70),
        # Test reserved/unused bits set and return code is 0
        (b'\x00\x80\x85\x9c\x80\x00', 0),
    )
)
def test__lis(by: bytes, expected: int):
    result = archive._lis(by)
    assert result == expected


# Example of a correct initial Phyisical Record and Logical Record Header
LIS_PR_GOOD_BYTES  =b'\x00\x3e\x00\x00\x80\x00'


@pytest.mark.parametrize(
    'by, expected',
    (
        # Typical TIF OK
        (b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x4a\x00\x00\x00' + LIS_PR_GOOD_BYTES, 0),
        # TIF word[0] bad
        (b'\x00\x00\x00\x01' + b'\x00\x00\x00\x00' + b'\x4a\x00\x00\x00' + LIS_PR_GOOD_BYTES, 1),
        # TIF word[1] bad
        (b'\x00\x00\x00\x00' + b'\x00\x00\x00\x01' + b'\x4a\x00\x00\x00' + LIS_PR_GOOD_BYTES, 2),
        # TIF word[2] Too large
        (b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\xff\xff\x0d\x00' + LIS_PR_GOOD_BYTES, 3),
        # TIF word[2] mismatch with PRL, TIF can be greater because of padding but not smaller.
        (b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x49\x00\x00\x00' + LIS_PR_GOOD_BYTES, 4),
    )
)
def test__lis_tif(by: bytes, expected: int):
    result = archive._lis_tif(by)
    assert result == expected


@pytest.mark.parametrize(
    'by, expected',
    (
        # Typical TIF reversed OK
        (b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x00\x00\x00\x4a' + LIS_PR_GOOD_BYTES, 0),
        # TIF word[0] bad
        (b'\x00\x00\x00\x01' + b'\x00\x00\x00\x00' + b'\x00\x00\x00\x4a' + LIS_PR_GOOD_BYTES, 1),
        # TIF word[1] bad
        (b'\x00\x00\x00\x00' + b'\x00\x00\x00\x01' + b'\x00\x00\x00\x4a' + LIS_PR_GOOD_BYTES, 2),
        # TIF word[2] too big
        (b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x00\x0D\xFF\xFF' + LIS_PR_GOOD_BYTES, 3),
        # TIF word[2] mismatch with PRL
        (b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x00\x00\x00\x49' + LIS_PR_GOOD_BYTES, 4),
    )
)
def test__lis_tif_r(by: bytes, expected: int):
    result = archive._lis_tif_r(by)
    assert result == expected


@pytest.mark.parametrize(
    'by, expected',
    (
        # Success
        (
            b'\n'.join(
                [
                    b'~VERSION INFORMATION',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            ),
            0
        ),
        (
            b'\n'.join(
                [
                    b'~Version Information',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            ),
            0
        ),
        (
            b'\n'.join(
                [
                    b'~Version Information Section',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            ),
            0
        ),
        (
            b'\n'.join(
                [
                    b'~V',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            ),
            0
        ),
        # Comment line
        (
            b'\n'.join(
                [
                    b'# Some comment or other',
                    b'~VERSION INFORMATION',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            ),
            0
        ),
        # Blank lines
        (
            b'\n'.join(
                [
                    b'   ',
                    b'~VERSION INFORMATION',
                    b'',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            ),
            0
        ),
        # Failure
        (
            b'\n'.join(
                [
                    b'~NOT VERSION INFORMATION',
                ]
            ),
            1
        ),
        (
            b'\n'.join(
                [
                    b'~VERSION INFORMATION',
                ]
            ),
            2
        ),
        (
            b'\n'.join(
                [
                    b'~V',
                    b' NOTVERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            ),
            3
        ),
        (
            b'\n'.join(
                [
                    b'~V',
                    b' VERS.',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            ),
            4
        ),
        (
            b'\n'.join(
                [
                    b'~V',
                    b' VERS.                 1.9:   CWLS LOG ASCII STANDARD -VERSION 1.9',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            ),
            5
        ),
    )
)
def test__las(by: bytes, expected: int):
    result = archive._las(by, (b'1.2:', b'1.2'))
    assert result == expected


@pytest.mark.parametrize(
    'by, expected',
    (
        # Success
        (
            b'\n'.join(
                [
                    b'~VERSION INFORMATION',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            ),
            0
        ),
    )
)
def test__las12(by: bytes, expected: int):
    result = archive._lasv12(by)
    assert result == expected


@pytest.mark.parametrize(
    'by, expected',
    (
        # Success
        (
            b'\n'.join(
                [
                    b'~VERSION INFORMATION',
                    b' VERS.                 2.0:   CWLS LOG ASCII STANDARD -VERSION 2.0',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            ),
            0
        ),
    )
)
def test__las20(by: bytes, expected: int):
    result = archive._lasv20(by)
    assert result == expected


@pytest.mark.parametrize(
    'by, expected',
    (
        # Success
        (
            b'\n'.join(
                [
                    b'~VERSION INFORMATION',
                    b' VERS.                 3.0:   CWLS LOG ASCII STANDARD -VERSION 3.0',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            ),
            0
        ),
    )
)
def test__las30(by: bytes, expected: int):
    result = archive._lasv30(by)
    assert result == expected


# Typical RP66v1
# 00000000: 2020 2031 5631 2e30 3052 4543 4f52 4420     1V1.00RECORD
# 00000010: 3831 3932 4465 6661 756c 7420 5374 6f72  8192Default Stor
# 00000020: 6167 6520 5365 7420 2020 2020 2020 2020  age Set
# 00000030: 2020 2020 2020 2020 2020 2020 2020 2020
# 00000040: 2020 2020 2020 2020 2020 2020 2020 2020
# 00000050: 1ffc ff01 007c 8000 f00b 4649 4c45 2d48  .....|....FILE-H


@pytest.mark.parametrize(
    'by, expected',
    (
        (
            # Good example
            b''.join(
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
            ),
            0,
        ),
        (
            # Missing sequence number, byte[3]
            b''.join(
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
            ),
            1,
        ),
        (
            # Bad version, initial bytes are not 'V1.'
            b''.join(
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
            ),
            2,
        ),
        (
            # Bad version, minor number is spaces
            b''.join(
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
            ),
            2,
        ),
        (
            # Storage unit structure is not b'RECORD'
            b''.join(
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
            ),
            3,
        ),
        (
            # Maximum Record Length is not a number, (last byte is a space)
            b''.join(
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
            ),
            4,
        ),
        (
            # Storage Set Identifier - too short (last field)
            b''.join(
                [
                    b'\x20\x20\x20\x31',  # Storage Unit Sequence Number, 4 bytes
                    b'\x56\x31\x2e\x30\x30',  # DLIS version, 5 bytes
                    b'\x52\x45\x43\x4f\x52\x44',  # Storage unit structure, 6 bytes, b'RECORD'
                    b'\x20\x38\x31\x39\x32',  # Maximum record length, 5 bytes
                    # Storage set identifier, 60 bytes, b'Default Storage Set...'
                    b'\x44\x65\x66\x61\x75\x6c\x74\x20\x53\x74\x6f\x72',
                    b'\x61\x67\x65\x20\x53\x65\x74\x20\x20\x20\x20\x20\x20\x20\x20\x20',
                    b'\x20' * 16,
                    b'\x20' * 15,
                ]
            ),
            5,
        ),
        (
            # Storage Set Identifier - non-printable bytes (last field)
            b''.join(
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
            ),
            6,
        ),
    )
)
def test__rp66v1(by: bytes, expected: int):
    result = archive._rp66v1(by)
    assert result == expected


@pytest.mark.parametrize(
    'by, expected',
    (
        (
            # Good example
            b''.join(
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
            ),
            0,
        ),
    )
)
def test__rp66v1_tif(by: bytes, expected: int):
    result = archive._rp66v1_tif(by)
    assert result == expected


@pytest.mark.parametrize(
    'by, expected',
    (
        (
            # Good example
            b''.join(
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
            ),
            0,
        ),
    )
)
def test__rp66v1_tif_r(by: bytes, expected: int):
    result = archive._rp66v1_tif_r(by)
    assert result == expected


@pytest.mark.parametrize(
    'by, expected',
    (
        (b'', 0),
        (b'PK', 0),
    )
)
def test__ascii(by: bytes, expected: int):
    result = archive._ascii(by)
    assert result == expected


@pytest.mark.parametrize(
    'by, expected',
    (
        # Typical ZIP OK
        (b'PK\x03\x04', 0),
        # ZIP bad
        (b'PK\x03\x05', 1),
    )
)
def test__zip(by: bytes, expected: int):
    result = archive._zip(by)
    assert result == expected


@pytest.mark.parametrize(
    'by, expected',
    (
        # Typical PDF OK
        (b'%PDF-', 0),
        # PDF bad
        (b'%PDFX', 1),
    )
)
def test__pdf(by: bytes, expected: int):
    result = archive._pdf(by)
    assert result == expected


@pytest.mark.parametrize(
    'by, expected',
    (
        (b'PK\x03\x04', 'ZIP'),
        (b'%PDF-', 'PDF'),
        # Need extra bytes so that TIF can be tested as well.
        (b'\x00\x80\x85\x9c\x80\x00' + b'\x00' * 12, 'LIS'),
        (b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x4a\x00\x00\x00' + LIS_PR_GOOD_BYTES, 'LISt'),
        (b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x00\x00\x00\x4a' + LIS_PR_GOOD_BYTES, 'LIStr'),
        (
            b'\n'.join(
                [
                    b'~VERSION INFORMATION',
                    b' VERS.                 1.2:   CWLS LOG ASCII STANDARD -VERSION 1.2',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            ),
            'LAS1.2',
        ),
        (
            b'\n'.join(
                [
                    b'~VERSION INFORMATION',
                    b' VERS.                 2.0:   CWLS LOG ASCII STANDARD -VERSION 2.0',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            ),
            'LAS2.0',
        ),
        (
            b'\n'.join(
                [
                    b'~VERSION INFORMATION',
                    b' VERS.                 3.0:   CWLS LOG ASCII STANDARD -VERSION 3.0',
                    b' WRAP.                  NO:   ONE LINE PER DEPTH STEP',
                ]
            ),
            'LAS3.0',
        ),
        (
            b''.join(
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
            ),
            'RP66V1',
        ),
        (
            # RP66V1 with a TIF marker.
            b''.join(
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
            ),
            'RP66V1t',
        ),
        (
            # RP66V1 with a reversed TIF marker.
            b''.join(
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
            ),
            'RP66V1tr',
        ),
    )
)
def test_binary_file_type_from_bytes(by: bytes, expected: str):
    result = archive.binary_file_type_from_bytes(by)
    assert result == expected



# TIF encoded RP66V1:
# Storage Unit Label is from 0xC to 0xC + 80 = 92 (0x5c)
# 00000000: 0000 0000 0000 0000 5c00 0000 2020 2031  ........\...   1
# 00000010: 5631 2e30 3052 4543 4f52 4420 3831 3932  V1.00RECORD 8192
# 00000020: 4445 4641 554c 5420 2020 2020 2020 2020  DEFAULT
# 00000030: 2020 2020 2020 2020 2020 2020 2020 2020
# 00000040: 2020 2020 2020 2020 2020 2020 2020 2020
# 00000050: 2020 2020 2020 2020 2020 2020 0000 0000              ....
# 00000060: 0000 0000 6820 0000 2000 ff01 007c 8000  ....h .. ....|..
# 00000070: f00b 4649 4c45 2d48 4541 4445 5234 0f53  ..FILE-HEADER4.S
# 00000080: 4551 5545 4e43 452d 4e55 4d42 4552 1434  EQUENCE-NUMBER.4
# 00000090: 0249 4414 7010 0001 3321 0a20 2020 2020  .ID.p...3!.
# 000000a0: 2020 2020 3921 4144 5353 5442 202e 3030      9!ADSSTB .00
# 000000b0: 3920 2020 2020 2020 2020 2020 2020 2020  9
# 000000c0: 2020 2020 2020 2020 2020 2020 2020 2020
# 000000d0: 2020 2020 2020 2020 2020 2020 2020 2020
# 000000e0: 2020 2020 2020 2020 0280 8101 f806 4f52          ......OR
# 000000f0: 4947 494e 0130 3407 4649 4c45 2d49 4414  IGIN.04.FILE-ID.
# 00000100: 340d 4649 4c45 2d53 4554 2d4e 414d 4513  4.FILE-SET-NAME.


# Example of RP66V1 without the Storage Unit Label
# Looks like this is TIF encoded.
# Note the common run:
# 2000 ff01 007c 8000 f00b 4649 4c45 2d48 4541 4445
# Petrologic/CD1/DLIS/200003.D15
# 00000000: 0000 0000 0000 0000 0c20 0000 2000 ff01  ......... .. ...
# 00000010: 007c 8000 f00b 4649 4c45 2d48 4541 4445  .|....FILE-HEADE
# 00000020: 5234 0f53 4551 5545 4e43 452d 4e55 4d42  R4.SEQUENCE-NUMB
# 00000030: 4552 1434 0249 4414 702e 0001 3921 0a20  ER.4.ID.p...9!.
# 00000040: 2020 2020 2020 2031 3521 414e 4754 4420         15!ANGTD
# 00000050: 202e 3030 3920 2020 2020 2020 2020 2020   .009
# 00000060: 2020 2020 2020 2020 2020 2020 2020 2020
# 00000070: 2020 2020 2020 2020 2020 2020 2020 2020
# 00000080: 2020 2020 2020 2020 2020 2020 02fc 8001              ....
# 00000090: f806 4f52 4947 494e 0130 3407 4649 4c45  ..ORIGIN.04.FILE
# 000000a0: 2d49 4414 340d 4649 4c45 2d53 4554 2d4e  -ID.4.FILE-SET-N
# 000000b0: 414d 4513 340f 4649 4c45 2d53 4554 2d4e  AME.4.FILE-SET-N
# Proposal: Ignore this as it is so far from the standard: missing SUL _and_ spurious TIF encoding.
