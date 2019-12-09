"""
References:
RP66V1: http://w3.energistics.org/rp66/v1/rp66v1.html
Specifically Appendix B: http://w3.energistics.org/rp66/v1/rp66v1_appb.html

NOTE: Some test data is taken from RP66V2:
http://w3.energistics.org/rp66/v2/rp66v2.html
Specifically: http://w3.energistics.org/rp66/v2/rp66v2_sec2.html#11
"""
import datetime

import numpy as np
import pytest

from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core.File import LogicalData


@pytest.mark.parametrize(
    'rc, expected',
    (
        (1, True,),  # Low precision floating point
        (2, True,),  # IEEE single precision floating point
        (3, True,),  # Validated single precision floating point
        (4, True,),  # Two-way validated single precision floating point
        (5, True,),  # IBM single precision floating point
        (6, True,),  # VAX single precision floating point
        (7, True,),  # IEEE double precision floating point
        (8, True,),  # Validated double precision floating point
        (9, True,),  # Two-way validated double precision floating point
        (10, True,),  # Single precision complex
        (11, True,),  # Double precision complex
        (12, True,),  # Short signed integer
        (13, True,),  # Normal signed integer
        (14, True,),  # Long signed integer
        (15, True,),  # Short unsigned integer
        (16, True,),  # Normal unsigned integer
        (17, True,),  # Long unsigned integer
        (18, False), # UVARI	1, 2, or 4	    Variable-length unsigned integer
        (19, False), # IDENT	V	            Variable-length identifier
        (20, False), # ASCII	V	            Variable-length ASCII character string
        (21, True,),  # Date and time
        (22, False), # ORIGIN	V	            Origin reference
        (23, False), # OBNAME	V	            Object name
        (24, False), # OBJREF	V	            Object reference
        (25, False), # ATTREF	V	            Attribute reference
        (26, True,),  # Boolean status
        (27, False), # UNITS	V	            Units expression
    )
)
def test_rep_code_is_fixed_length(rc, expected):
    result = RepCode.is_fixed_length(rc)
    assert result == expected


@pytest.mark.parametrize(
    'rc, expected',
    (
        (1, 2,),  # Low precision floating point
        (2, 4,),  # IEEE single precision floating point
        (3, 8,),  # Validated single precision floating point
        (4, 12,),  # Two-way validated single precision floating point
        (5, 4,),  # IBM single precision floating point
        (6, 4,),  # VAX single precision floating point
        (7, 8,),  # IEEE double precision floating point
        (8, 16,),  # Validated double precision floating point
        (9, 24,),  # Two-way validated double precision floating point
        (10, 8,),  # Single precision complex
        (11, 16,),  # Double precision complex
        (12, 1,),  # Short signed integer
        (13, 2,),  # Normal signed integer
        (14, 4,),  # Long signed integer
        (15, 1,),  # Short unsigned integer
        (16, 2,),  # Normal unsigned integer
        (17, 4,),  # Long unsigned integer
        # 18	    UVARI	1, 2, or 4	    Variable-length unsigned integer
        # 19	    IDENT	V	            Variable-length identifier
        # 20	    ASCII	V	            Variable-length ASCII character string
        (21, 8,),  # Date and time
        # 22	    ORIGIN	V	            Origin reference
        # 23	    OBNAME	V	            Object name
        # 24	    OBJREF	V	            Object reference
        # 25	    ATTREF	V	            Attribute reference
        (26, 1,),  # Boolean status
        # 27	    UNITS	V	            Units expression
    )
)
def test_rep_code_fixed_length(rc, expected):
    result = RepCode.rep_code_fixed_length(rc)
    assert result == expected


@pytest.mark.parametrize(
    'rc',
    (
        18,  #   UVARI	1, 2, or 4	    Variable-length unsigned integer
        19,  #   IDENT	V	            Variable-length identifier
        20,  #   ASCII	V	            Variable-length ASCII character string
        22,  #   ORIGIN	V	            Origin reference
        23,  #   OBNAME	V	            Object name
        24,  #   OBJREF	V	            Object reference
        25,  #   ATTREF	V	            Attribute reference
        27,  #   UNITS	V	            Units expression
    )
)
def test_rep_code_fixed_length_raises(rc):
    with pytest.raises(RepCode.ExceptionRepCode) as err:
        RepCode.rep_code_fixed_length(rc)
    assert err.value.args[0] == f'Representation code {rc} is not fixed length.'


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
        # Examples from [RP66V2 Section 11.3.23]
        (LogicalData(b'\x00\x00\x00\x00'), 0.0),
        (LogicalData(b'\x0c\x44\x00\x80'), 153.0),
        (LogicalData(b'\x0c\xc4\x00\x80'), -153.0),
    )
)
def test_VSINGL(ld, expected):
    result = RepCode.VSINGL(ld)
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


def test_UVARI_len_raises():
    with pytest.raises(RepCode.ExceptionRepCode) as err:
        RepCode.UVARI_len(b'', -1)
    assert err.value.args[0] == 'Index can not be negative.'


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


def test_IDENT_len_raises():
    with pytest.raises(RepCode.ExceptionRepCode) as err:
        RepCode.IDENT_len(b'', -1)
    assert err.value.args[0] == 'Index can not be negative.'


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
        (LogicalData(b'\x57\x14\x13\x15\x14\x0f\x02\x6c'), '1987-04-19 21:20:15.620 DST'),
        # RP66V2 example from the printed standard. The website is in error as it uses all nulls.
        # http://w3.energistics.org/rp66/v2/rp66v2_sec2.html#11_4_2
        (LogicalData(b'\x00\x01\x01\x00\x00\x00\x00\x00'), '1900-01-01 00:00:00.000 STD'),
    )
)
def test_DTIME_str(ld, expected):
    result = RepCode.DTIME(ld)
    assert ld.remain == 0
    assert str(result) == expected


@pytest.mark.parametrize(
    'ld, expected',
    (
        (
            LogicalData(b'\x57\x14\x13\x15\x14\x0f\x02\x6c'),
            "<<class 'TotalDepth.RP66V1.core.RepCode.DateTime'> 1987-04-19 21:20:15.620 DST>",
        ),
        # RP66V2 example from the printed standard. The website is in error as it uses all nulls.
        # http://w3.energistics.org/rp66/v2/rp66v2_sec2.html#11_4_2
        (
            LogicalData(b'\x00\x01\x01\x00\x00\x00\x00\x00'),
            "<<class 'TotalDepth.RP66V1.core.RepCode.DateTime'> 1900-01-01 00:00:00.000 STD>",
        ),
    )
)
def test_DTIME_repr(ld, expected):
    result = RepCode.DTIME(ld)
    assert ld.remain == 0
    assert repr(result) == expected


def test_DTIME_invalid_tz_abbreviation():
    ld = LogicalData(b'\x57\x34\x13\x15\x14\x0f\x02\x6c')
    #                        ^
    result = RepCode.DTIME(ld)
    assert result.tz_abbreviation == ''


def test_DTIME_invalid_tz_description():
    ld = LogicalData(b'\x57\x34\x13\x15\x14\x0f\x02\x6c')
    #                        ^
    result = RepCode.DTIME(ld)
    assert result.tz_description== ''


@pytest.mark.parametrize(
    'ld, expected',
    (
        (
            LogicalData(b'\x57\x14\x13\x15\x14\x0f\x02\x6c'),
            datetime.datetime(1987, 4, 19, 21, 20, 15, 620000),
        ),
        # RP66V2 example from the printed standard. The website is in error as it uses all nulls.
        # http://w3.energistics.org/rp66/v2/rp66v2_sec2.html#11_4_2
        (
            LogicalData(b'\x00\x01\x01\x00\x00\x00\x00\x00'),
            datetime.datetime(1900, 1, 1, 0, 0, 0, 0),
        ),
    )
)
def test_DTIME_as_datetime(ld, expected):
    result = RepCode.DTIME(ld)
    assert ld.remain == 0
    assert result.as_datetime() == expected


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


def test_ObjectName_ctor_eq_false():
    object_name = RepCode.ObjectName(1, 2, b'')
    assert not object_name == 1
    assert not 1 == object_name


def test_ObjectName_ctor_lt_false():
    object_name = RepCode.ObjectName(1, 2, b'')
    with pytest.raises(TypeError) as err:
        object_name < 1
    assert err.value.args[0] == "'<' not supported between instances of 'ObjectName' and 'int'"
    with pytest.raises(TypeError) as err:
        1 < object_name
    assert err.value.args[0] == "'<' not supported between instances of 'int' and 'ObjectName'"


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


def test_OBNAME_len_raises():
    ld = LogicalData(b'\x00' + b'\x01' + b'\x03')
    with pytest.raises(RepCode.ExceptionRepCode) as err:
        RepCode.OBNAME_len(ld.bytes, -1)
    assert err.value.args[0] == 'Index can not be negative.'


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
        (
            LogicalData(b'\x0512345' + b'\x00' + b'\x01' + b'\x03ABC'),
            "OBREF: O: b'12345' C: OBNAME: O: 0 C: 1 I: b'ABC'",
        ),
    )
)
def test_OBJREF_str(ld, expected):
    result = RepCode.OBJREF(ld)
    assert str(result) == expected
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


@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b'\x00'), b''),
        (LogicalData(b'\x01A'), b'A'),
        (LogicalData(b'\x01a'), b'a'),
        (LogicalData(b'\x011'), b'1'),
        (LogicalData(b'\x1AABCDEFGHIJKLMNOPQRSTUVWXYZ'), b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
        (LogicalData(b'\x1Aabcdefghijklmnopqrstuvwxyz'), b'abcdefghijklmnopqrstuvwxyz'),
        (LogicalData(b'\x0A1234567890'), b'1234567890'),
        (LogicalData(b'\x06 -./()'), b' -./()'),
    )
)
def test_UNITS(ld, expected):
    result = RepCode.UNITS(ld)
    assert result == expected
    assert ld.remain == 0


@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b'\x01_'), b'_'),
    )
)
def test_UNITS_bad_chars(ld, expected):
    result = RepCode.UNITS(ld)
    assert result == expected
    assert ld.remain == 0

@pytest.mark.parametrize(
    'rc, ld, expected',
    (
        # Examples from [RP66V1 Appendix B Section B.2]
        # FSINGL
        (2, LogicalData(b'\x43\x19\x00\x00'), 153.0),
        (2, LogicalData(b'\xc3\x19\x00\x00'), -153.0),
        # Example from RP66V2
        (2, LogicalData(b'\x00\x00\x00\x00'), 0.0),
        # FDOUBLE
        (7, LogicalData(b'\x40\x63\x20\x00\x00\x00\x00\x00'), 153.0),
        (7, LogicalData(b'\xc0\x63\x20\x00\x00\x00\x00\x00'), -153.0),
        (7, LogicalData(b'\x00\x00\x00\x00\x00\x00\x00\x00'), 0.0),
        # SSHORT
        (12, LogicalData(b'\x00'), 0),
        (12, LogicalData(b'\x59'), 89),
        (12, LogicalData(b'\x7f'), 127),
        (12, LogicalData(b'\x80'), -128),
        (12, LogicalData(b'\xa7'), -89),
        (12, LogicalData(b'\xff'), -1),
        # SNORM
        (13, LogicalData(b'\x00\x00'), 0),
        (13, LogicalData(b'\x00\x99'), 153),
        (13, LogicalData(b'\xff\x67'), -153),
        # SLONG
        (14, LogicalData(b'\x00\x00\x00\x00'), 0),
        (14, LogicalData(b'\x00\x00\x00\x99'), 153),
        (14, LogicalData(b'\xff\xff\xff\x67'), -153),
        # USHORT
        (15, LogicalData(b'\x00'), 0),
        (15, LogicalData(b'\xd9'), 217),  # RP66V2 example.
        (15, LogicalData(b'\xff'), 255),
        # UNORM
        (16, LogicalData(b'\x00\x00'), 0),
        (16, LogicalData(b'\x80\x99'), 32921),
        (16, LogicalData(b'\x00\x99'), 153),  # RP66V2 example.
        # ULONG
        (17, LogicalData(b'\x00\x00\x00\x00'), 0),
        (17, LogicalData(b'\x00\x00\x00\x99'), 153),
        # UVARI
        # One byte examples
        (18, LogicalData(b'\x00'), 0),
        (18, LogicalData(b'\x01'), 1),
        (18, LogicalData(b'\x7e'), 2**7 - 2),
        (18, LogicalData(b'\x7F'), 2**7 - 1),
        # Two byte examples
        (18, LogicalData(b'\x80\x80'), 2**7),
        (18, LogicalData(b'\x80\x81'), 2**7 + 1),
        (18, LogicalData(b'\xbf\xfe'), 2**14 - 2),
        (18, LogicalData(b'\xbf\xff'), 2**14 - 1),
        # Four byte examples
        (18, LogicalData(b'\xc0\x00\x40\x00'), 2**14),
        (18, LogicalData(b'\xc0\x00\x40\x01'), 2**14 + 1),
        (18, LogicalData(b'\xff\xff\xff\xfe'), 2**30 - 2),
        (18, LogicalData(b'\xff\xff\xff\xff'), 2**30 - 1),
        # IDENT
        (19, LogicalData(b'\x00'), b''),
        (19, LogicalData(b'\x03ABC'), b'ABC'),
        (19, LogicalData(b'\x05TYPE1'), b'TYPE1'),  # RP66V2 example.
        # ASCII
        (20, LogicalData(b'\x00'), b''),
        (20, LogicalData(b'\x03A\x0ab'), b'A\x0ab'),
        (20, LogicalData(b'\x05\x24 / \xa3'), b'\x24 / \xa3'),  # RP66V2 example.
        # ORIGIN
        # One byte examples
        (22, LogicalData(b'\x00'), 0),
        (22, LogicalData(b'\x01'), 1),
        (22, LogicalData(b'\x7e'), 2 ** 7 - 2),
        (22, LogicalData(b'\x7F'), 2 ** 7 - 1),
        # Two byte examples
        (22, LogicalData(b'\x80\x80'), 2 ** 7),
        (22, LogicalData(b'\x80\x81'), 2 ** 7 + 1),
        (22, LogicalData(b'\xbf\xfe'), 2 ** 14 - 2),
        (22, LogicalData(b'\xbf\xff'), 2 ** 14 - 1),
        # Four byte examples
        (22, LogicalData(b'\xc0\x00\x40\x00'), 2 ** 14),
        (22, LogicalData(b'\xc0\x00\x40\x01'), 2 ** 14 + 1),
        (22, LogicalData(b'\xff\xff\xff\xfe'), 2 ** 30 - 2),
        (22, LogicalData(b'\xff\xff\xff\xff'), 2 ** 30 - 1),
        # OBNAME
        (23, LogicalData(b'\x00' + b'\x01' + b'\x03ABC'), RepCode.ObjectName(0, 1, b'ABC')),
        # STATUS
        (26, LogicalData(b'\x00'), 0),
        (26, LogicalData(b'\x01'), 1),
        # UNITS
        (27, LogicalData(b'\x00'), b''),
        (27, LogicalData(b'\x01A'), b'A'),
        (27, LogicalData(b'\x01a'), b'a'),
        (27, LogicalData(b'\x011'), b'1'),
        (27, LogicalData(b'\x1AABCDEFGHIJKLMNOPQRSTUVWXYZ'), b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
        (27, LogicalData(b'\x1Aabcdefghijklmnopqrstuvwxyz'), b'abcdefghijklmnopqrstuvwxyz'),
        (27, LogicalData(b'\x0A1234567890'), b'1234567890'),
        (27, LogicalData(b'\x06 -./()'), b' -./()'),
    )
)
def test_code_read(rc, ld, expected):
    assert RepCode.code_read(rc, ld) == expected


def test_code_read_raises():
    with pytest.raises(RepCode.ExceptionRepCode) as err:
        RepCode.code_read(0, None)
    assert err.value.args[0] == 'Unsupported Representation code 0'


@pytest.mark.parametrize(
    'rc, expected',
    (
        (2, np.float32),
        (7, np.float64),
    )
)
def test_numpy_dtype(rc, expected):
    assert RepCode.numpy_dtype(rc) == expected


def test_numpy_dtype_raises():
    with pytest.raises(RepCode.ExceptionRepCode) as err:
        RepCode.numpy_dtype(0)
    assert err.value.args[0] == 'Unsupported Representation code 0'
