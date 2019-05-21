"""
References:
RP66V1: http://w3.energistics.org/rp66/v1/rp66v1.html
Specifically Appendix B: http://w3.energistics.org/rp66/v1/rp66v1_appb.html

NOTE: Some test data is taken from RP66V2:
http://w3.energistics.org/rp66/v2/rp66v2.html
Specifically: http://w3.energistics.org/rp66/v2/rp66v2_sec2.html#11
"""
import pytest

from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core.File import LogicalData


@pytest.mark.parametrize(
    'ld, expected',
    (
        # Examples from [RP66V1 Appendix B Section B.2]
        (LogicalData(b'\x43\x19\x00\x00'), 153.0),
        (LogicalData(b'\xc3\x19\x00\x00'), -153.0),
        # Example from RP66V2
        (LogicalData(b'\x00\x00\x00\x00'), 0.0),
    )
)
def test_FSINGL(ld, expected):
    result = RepCode.FSINGL(ld)
    assert result == expected
    assert ld.remain == 0


@pytest.mark.parametrize(
    'ld, expected',
    (
        # Examples from [RP66V1 Appendix B Section B.7 NOTE: These are only 4 byte examples, RP66V2 has better examples]
        (LogicalData(b'\x40\x63\x20\x00\x00\x00\x00\x00'), 153.0),
        (LogicalData(b'\xc0\x63\x20\x00\x00\x00\x00\x00'), -153.0),
        (LogicalData(b'\x00\x00\x00\x00\x00\x00\x00\x00'), 0.0),
    )
)
def test_FDOUBL(ld, expected):
    result = RepCode.FDOUBL(ld)
    assert result == expected
    assert ld.remain == 0


@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b'\x00'), 0),
        (LogicalData(b'\x59'), 89),
        (LogicalData(b'\x7f'), 127),
        (LogicalData(b'\x80'), -128),
        (LogicalData(b'\xa7'), -89),
        (LogicalData(b'\xff'), -1),
    )
)
def test_SSHORT(ld, expected):
    result = RepCode.SSHORT(ld)
    assert result == expected
    assert ld.remain == 0


@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b'\x00\x00'), 0),
        (LogicalData(b'\x00\x99'), 153),
        (LogicalData(b'\xff\x67'), -153),
    )
)
def test_SNORM(ld, expected):
    result = RepCode.SNORM(ld)
    assert result == expected
    assert ld.remain == 0


@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b'\x00\x00\x00\x00'), 0),
        (LogicalData(b'\x00\x00\x00\x99'), 153),
        (LogicalData(b'\xff\xff\xff\x67'), -153),
    )
)
def test_SLONG(ld, expected):
    result = RepCode.SLONG(ld)
    assert result == expected
    assert ld.remain == 0


@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b'\x00'), 0),
        (LogicalData(b'\xd9'), 217),  # RP66V2 example.
        (LogicalData(b'\xff'), 255),
    )
)
def test_USHORT(ld, expected):
    result = RepCode.USHORT(ld)
    assert result == expected
    assert ld.remain == 0


@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b'\x00\x00'), 0),
        (LogicalData(b'\x80\x99'), 32921),
        (LogicalData(b'\x00\x99'), 153),  # RP66V2 example.
    )
)
def test_UNORM(ld, expected):
    result = RepCode.UNORM(ld)
    assert result == expected
    assert ld.remain == 0


@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b'\x00\x00\x00\x00'), 0),
        (LogicalData(b'\x00\x00\x00\x99'), 153),
    )
)
def test_ULONG(ld, expected):
    result = RepCode.ULONG(ld)
    assert result == expected
    assert ld.remain == 0


@pytest.mark.parametrize(
    'ld, expected',
    (
        # One byte examples
        (LogicalData(b'\x00'), 0),
        (LogicalData(b'\x01'), 1),
        (LogicalData(b'\x7e'), 2**7 - 2),
        (LogicalData(b'\x7F'), 2**7 - 1),
        # Two byte examples
        (LogicalData(b'\x80\x80'), 2**7),
        (LogicalData(b'\x80\x81'), 2**7 + 1),
        (LogicalData(b'\xbf\xfe'), 2**14 - 2),
        (LogicalData(b'\xbf\xff'), 2**14 - 1),
        # Four byte examples
        (LogicalData(b'\xc0\x00\x40\x00'), 2**14),
        (LogicalData(b'\xc0\x00\x40\x01'), 2**14 + 1),
        (LogicalData(b'\xff\xff\xff\xfe'), 2**30 - 2),
        (LogicalData(b'\xff\xff\xff\xff'), 2**30 - 1),
    )
)
def test_UVARI(ld, expected):
    result = RepCode.UVARI(ld)
    assert result == expected
    assert ld.remain == 0


UVARI_len_EXAMPLES = (
    # Zero byte examples
    (LogicalData(b''), 0),
    # One byte examples
    (LogicalData(b'\x00'), 1),
    (LogicalData(b'\x01'), 1),
    (LogicalData(b'\x7e'), 1),
    (LogicalData(b'\x7F'), 1),
    # Two byte examples
    (LogicalData(b'\x80\x80'), 2),
    (LogicalData(b'\x80\x81'), 2),
    (LogicalData(b'\xbf\xfe'), 2),
    (LogicalData(b'\xbf\xff'), 2),
    (LogicalData(b'\x80'), 2),
    (LogicalData(b'\x80'), 2),
    (LogicalData(b'\xbf'), 2),
    (LogicalData(b'\xbf'), 2),
    # Four byte examples
    (LogicalData(b'\xc0\x00\x40\x00'), 4),
    (LogicalData(b'\xc0\x00\x40\x01'), 4),
    (LogicalData(b'\xff\xff\xff\xfe'), 4),
    (LogicalData(b'\xff\xff\xff\xff'), 4),
    (LogicalData(b'\xc0'), 4),
    (LogicalData(b'\xc0\x00'), 4),
    (LogicalData(b'\xc0\x00\x40'), 4),
    (LogicalData(b'\xc0'), 4),
    (LogicalData(b'\xff'), 4),
    (LogicalData(b'\xff'), 4),
)


@pytest.mark.parametrize('ld, expected', UVARI_len_EXAMPLES)
def test_UVARI_len(ld, expected):
    result = RepCode.UVARI_len(ld.bytes, 0)
    assert result == expected


@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b'\x00'), b''),
        (LogicalData(b'\x03ABC'), b'ABC'),
        (LogicalData(b'\x05TYPE1'), b'TYPE1'),  # RP66V2 example.
    )
)
def test_IDENT(ld, expected):
    result = RepCode.IDENT(ld)
    assert result == expected
    assert ld.remain == 0


@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b''), 0),  # Error condition
        (LogicalData(b'\x00'), 1),
        (LogicalData(b'\x03ABC'), 4),
        (LogicalData(b'\x03'), 4),
        (LogicalData(b'\x05TYPE1'), 6),  # RP66V2 example.
    )
)
def test_IDENT_len(ld, expected):
    result = RepCode.IDENT_len(ld.bytes, 0)
    assert result == expected


@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b'\x00'), b''),
        (LogicalData(b'\x03A\x0ab'), b'A\x0ab'),
        (LogicalData(b'\x05\x24 / \xa3'), b'\x24 / \xa3'),  # RP66V2 example.
    )
)
def test_ASCII(ld, expected):
    result = RepCode.ASCII(ld)
    assert result == expected
    assert ld.remain == 0


# TODO: Test DTIME out of range.
@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b'\x57\x14\x13\x15\x14\x0f\x02\x6c'), '1987-04-19 21:20:15.620'),
        # RP66V2 example from the printed standard. The website is in error as it uses all nulls.
        # http://w3.energistics.org/rp66/v2/rp66v2_sec2.html#11_4_2
        (LogicalData(b'\x00\x01\x01\x00\x00\x00\x00\x00'), '1900-01-01 00:00:00.000'),
    )
)
def test_DTIME(ld, expected):
    result = RepCode.DTIME(ld)
    assert str(result) == expected
    assert ld.remain == 0


@pytest.mark.parametrize(
    'ld, expected',
    (
        # One byte examples
        (LogicalData(b'\x00'), 0),
        (LogicalData(b'\x01'), 1),
        (LogicalData(b'\x7e'), 2**7 - 2),
        (LogicalData(b'\x7F'), 2**7 - 1),
        # Two byte examples
        (LogicalData(b'\x80\x80'), 2**7),
        (LogicalData(b'\x80\x81'), 2**7 + 1),
        (LogicalData(b'\xbf\xfe'), 2**14 - 2),
        (LogicalData(b'\xbf\xff'), 2**14 - 1),
        # Four byte examples
        (LogicalData(b'\xc0\x00\x40\x00'), 2**14),
        (LogicalData(b'\xc0\x00\x40\x01'), 2**14 + 1),
        (LogicalData(b'\xff\xff\xff\xfe'), 2**30 - 2),
        (LogicalData(b'\xff\xff\xff\xff'), 2**30 - 1),
    )
)
def test_ORIGIN(ld, expected):
    result = RepCode.ORIGIN(ld)
    assert result == expected
    assert ld.remain == 0


@pytest.mark.parametrize('ld, expected', UVARI_len_EXAMPLES)
def test_ORIGIN_len(ld, expected):
    result = RepCode.ORIGIN_len(ld.bytes, 0)
    assert result == expected


@pytest.mark.parametrize(
    'args, expected',
    (
        ((1, 2, b''), RepCode.ObjectName(1, 2, b'')),
    )
)
def test_ObjectName_ctor_eq(args, expected):
    object_name = RepCode.ObjectName(*args)
    assert object_name == expected


@pytest.mark.parametrize(
    'args, expected',
    (
        ((1, 2, b'123'), "OBNAME: O: 1 C: 2 I: b'123'"),
    )
)
def test_ObjectName_str(args, expected):
    object_name = RepCode.ObjectName(*args)
    assert str(object_name) == expected


@pytest.mark.parametrize(
    'args, fmt, expected',
    (
        ((1, 2, b'123'), '', "OBNAME: O: 1 C: 2 I: b'123'"),
        ((1, 2, b'123'), '10', "OBNAME: O: 1 C: 2 I: b'123'    "),
        ((1, 2, b'123'), '>10', "OBNAME: O: 1 C: 2 I:     b'123'"),
    )
)
def test_ObjectName_format(args, fmt, expected):
    object_name = RepCode.ObjectName(*args)
    assert f'{object_name:{fmt}}' == expected


@pytest.mark.parametrize(
    'args_0, args_1, expected_0_1, expected_1_0',
    (
        ((1, 2, b'123'), (1, 2, b'123'), False, False),
        # Same I, C diffferent O
        ((1, 2, b'123'), (2, 2, b'123'), True, False),
        # Same I, O diffferent C
        ((1, 2, b'123'), (1, 3, b'123'), True, False),
        # Different I
        ((1, 2, b'123'), (1, 2, b'234'), True, False),
    )
)
def test_ObjectName_lt(args_0, args_1, expected_0_1, expected_1_0):
    object_0 = RepCode.ObjectName(*args_0)
    object_1 = RepCode.ObjectName(*args_1)
    assert (object_0 < object_1) == expected_0_1
    assert (object_1 < object_0) == expected_1_0


@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b'\x00' + b'\x01' + b'\x03ABC'), RepCode.ObjectName(0, 1, b'ABC')),
    )
)
def test_OBNAME(ld, expected):
    result = RepCode.OBNAME(ld)
    assert result == expected
    assert ld.remain == 0


@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b''), 0),  # Error as empty
        # Error as UVARI One byte examples
        (LogicalData(b'\x00'), 0),
        (LogicalData(b'\x01'), 0),
        (LogicalData(b'\x7e'), 0),
        (LogicalData(b'\x7F'), 0),
        # Error as UVARI Two byte examples
        (LogicalData(b'\x80\x80'), 0),
        (LogicalData(b'\x80\x81'), 0),
        (LogicalData(b'\xbf\xfe'), 0),
        (LogicalData(b'\xbf\xff'), 0),
        # Error as UVARI Four byte examples
        (LogicalData(b'\xc0\x00\x40\x00'), 0),
        (LogicalData(b'\xc0\x00\x40\x01'), 0),
        (LogicalData(b'\xff\xff\xff\xfe'), 0),
        (LogicalData(b'\xff\xff\xff\xff'), 0),
        # Error as no Copy as a USHORT
        (LogicalData(b'\x00'), 0),
        # Error as not enough IDENT data
        (LogicalData(b'\x00' + b'\x01'), 0),
        # Success
        (LogicalData(b'\x00' + b'\x01' + b'\x03'), 6),
        (LogicalData(b'\x00' + b'\x01' + b'\x03AB'), 6),
        (LogicalData(b'\x00' + b'\x01' + b'\x03ABC'), 6),
        (LogicalData(b'\x00' + b'\x01' + b'\x03ABCDEF'), 6),
        # Success with short bytes
        (LogicalData(b'\x00' + b'\x01' + b'\x03'), 6),
    )
)
def test_OBNAME_len(ld, expected):
    # TODO: index != 0, index -ve. Also for other _len functions.
    result = RepCode.OBNAME_len(ld.bytes, 0)
    assert result == expected


@pytest.mark.parametrize(
    'ld, expected',
    (
        (
            LogicalData(
                b'\x0512345' + b'\x00' + b'\x01' + b'\x03ABC'
            ),
            RepCode.ObjectReference(
                RepCode.IDENT(LogicalData(b'\x0512345')),
                RepCode.ObjectName(0, 1, b'ABC'),
            ),
        ),
    )
)
def test_OBJREF(ld, expected):
    result = RepCode.OBJREF(ld)
    assert result == expected
    assert ld.remain == 0


@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b'\x00'), 0),
        (LogicalData(b'\x01'), 1),
    )
)
def test_STATUS(ld, expected):
    result = RepCode.STATUS(ld)
    assert result == expected
    assert ld.remain == 0


# TODO: Test: UNITS
# UNITS must be in ASCII [RP66V1 Appendix B, B.27 Code UNITS: Units Expression]
# So .decode("ascii") must be OK.
# Syntactically, Representation Code UNITS is similar to Representation Codes IDENT and ASCII.
# However, upper case and lower case are considered distinct (e.g., "A" and "a" for Ampere and annum, respectively),
# and permissible characters are restricted to the following ASCII codes:
# lower case letters [a, b, c, ..., z]
# upper case letters [A, B, C, ..., Z]
# digits [0, 1, 2, ..., 9]
# blank [ ]
# hyphen or minus sign [-] dot or period [.]
# slash [/]
# parentheses [(, )]


# TODO: Test code_read()

