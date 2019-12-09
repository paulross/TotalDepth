"""
Python implementation of the RP66V1 Representation Codes ('Rep Codes') [RP66V1 Appendix B]

References:
    [RP66V1: http://w3.energistics.org/rp66/v1/rp66v1.html]

Specifically:
    [RP66V1 Appendix B: http://w3.energistics.org/rp66/v1/rp66v1_appb.html]

From: http://w3.energistics.org/rp66/v1/rp66v1_appb.html ::

    Code	Name	Size in Bytes	Descirption (sic)
    1	    FSHORT	2	            Low precision floating point
    2	    FSINGL	4	            IEEE single precision floating point
    3	    FSING1	8	            Validated single precision floating point
    4	    FSING2	12	            Two-way validated single precision floating point
    5	    ISINGL	4	            IBM single precision floating point
    6	    VSINGL	4	            VAX single precision floating point
    7	    FDOUBL	8	            IEEE double precision floating point
    8	    FDOUB1	16	            Validated double precision floating point
    9	    FDOUB2	24	            Two-way validated double precision floating point
    10	    CSINGL	8	            Single precision complex
    11	    CDOUBL	16	            Double precision complex
    12	    SSHORT	1	            Short signed integer
    13	    SNORM	2	            Normal signed integer
    14	    SLONG	4	            Long signed integer
    15	    USHORT	1	            Short unsigned integer
    16	    UNORM	2	            Normal unsigned integer
    17	    ULONG	4	            Long unsigned integer
    18	    UVARI	1, 2, or 4	    Variable-length unsigned integer
    19	    IDENT	V	            Variable-length identifier
    20	    ASCII	V	            Variable-length ASCII character string
    21	    DTIME	8	            Date and time
    22	    ORIGIN	V	            Origin reference
    23	    OBNAME	V	            Object name
    24	    OBJREF	V	            Object reference
    25	    ATTREF	V	            Attribute reference
    26	    STATUS	1	            Boolean status
    27	    UNITS	V	            Units expression
"""
import datetime
import enum
import logging
import string
import struct
import typing
import warnings

import numpy as np

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core.File import LogicalData


logger = logging.getLogger(__file__)


class ExceptionRepCode(ExceptionTotalDepthRP66V1):
    """General exception for Representation Code errors."""
    pass

# TODO: Have static NULL values e.g. IDENT_null = b'' ?

#: All known Representation Codes
REP_CODES_ALL = set(range(1, 28))

#: Map of all Representation Codes to name.
REP_CODE_INT_TO_STR_ALL: typing.Dict[int, str] = {
    1: 'FSHORT',
    2: 'FSINGL',
    3: 'FSING1',
    4: 'FSING2',
    5: 'ISINGL',
    6: 'VSINGL',
    7: 'FDOUBL',
    8: 'FDOUB1',
    9: 'FDOUB2',
    10: 'CSINGL',
    11: 'CDOUBL',
    12: 'SSHORT',
    13: 'SNORM',
    14: 'SLONG',
    15: 'USHORT',
    16: 'UNORM',
    17: 'ULONG',
    18: 'UVARI',
    19: 'IDENT',
    20: 'ASCII',
    21: 'DTIME',
    22: 'ORIGIN',
    23: 'OBNAME',
    24: 'OBJREF',
    25: 'ATTREF',
    26: 'STATUS',
    27: 'UNITS',
}
assert all(_ in REP_CODE_INT_TO_STR_ALL for _ in REP_CODES_ALL)

#: Supported Representation Codes
REP_CODES_SUPPORTED = {
    # 1, # - Not found in practice.
    2,
    # 3, 4, # - Not found in practice.
    # 5, # - Antiquated types, rarely if ever found.
    6,
    7,
    # 8, 9, # - Not found in practice.
    # 10, 11, # - Not found in practice.
    12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
    # 25,  # - Not found in practice.
    26, 27}

#: Map of supported Representation Codes to name.
REP_CODE_INT_TO_STR: typing.Dict[int, str] = {
    # 1: 'FSHORT',
    2: 'FSINGL',
    # 3: 'FSING1',
    # 4: 'FSING2',
    # 5: 'ISINGL',
    6: 'VSINGL',
    7: 'FDOUBL',
    # 8: 'FDOUB1',
    # 9: 'FDOUB2',
    # 10: 'CSINGL',
    # 11: 'CDOUBL',
    12: 'SSHORT',
    13: 'SNORM',
    14: 'SLONG',
    15: 'USHORT',
    16: 'UNORM',
    17: 'ULONG',
    18: 'UVARI',
    19: 'IDENT',
    20: 'ASCII',
    21: 'DTIME',
    22: 'ORIGIN',
    23: 'OBNAME',
    24: 'OBJREF',
    # 25: 'ATTREF',
    26: 'STATUS',
    27: 'UNITS',
}
assert set(REP_CODE_INT_TO_STR.keys()) == REP_CODES_SUPPORTED

#: Map of supported Representation Code names to integer code.
REP_CODE_STR_TO_INT = {v: k for k, v in REP_CODE_INT_TO_STR.items()}
assert len(REP_CODE_INT_TO_STR) == len(REP_CODE_STR_TO_INT)
assert set(REP_CODE_STR_TO_INT.values()) == REP_CODES_SUPPORTED, \
    f'{set(REP_CODE_STR_TO_INT.values())} != {REP_CODES_SUPPORTED}'

#: Unsupported Representation Codes.
REP_CODES_UNSUPPORTED = REP_CODES_ALL - REP_CODES_SUPPORTED
#: Unsupported Representation Code names.
REP_CODES_UNSUPPORTED_NAMES = [REP_CODE_INT_TO_STR_ALL[_] for _ in REP_CODES_UNSUPPORTED]


#: [RP66V1 Section 5.7.1 Frame Objects, Figure 5-8. Attributes of Frame Object, Comment 2] says:
#: 'If there is an Index Channel, then it must appear first in the Frame and it must be scalar.'
#: but does not specify which Representation Codes are scalar. This is out best estimate:
#:
#: #. Numeric values.
#: #. Not compound values.
#: #. Fixed length representations,
#:
#: TODO: Verify these assumptions, what index Representation Codes are actually experienced in practice?
REP_CODE_SCALAR_CODES = {1, 2, 5, 6, 7, 8, 12, 13, 14, 15, 16, 17}
#: Longest Representation Code that is a scalar, FDOUBL.
LENGTH_LARGEST_INDEX_CHANNEL_CODE = 8

#: Map of Rep Code to length for fixed length RepCodes.
REP_CODE_FIXED_LENGTHS = {
    1: 2,  # Low precision floating point
    2: 4,  # IEEE single precision floating point
    3: 8,  #Validated single precision floating point
    4: 12,  #Two-way validated single precision floating point
    5: 4,  # IBM single precision floating point
    6: 4,  # VAX single precision floating point
    7: 8,  # IEEE double precision floating point
    8: 16,  # Validated double precision floating point
    9: 24,  # Two-way validated double precision floating point
    10: 8,  # Single precision complex
    11: 16,  # Double precision complex
    12: 1,  # Short signed integer
    13: 2,  # Normal signed integer
    14: 4,  # Long signed integer
    15: 1,  # Short unsigned integer
    16: 2,  # Normal unsigned integer
    17: 4,  #  Long unsigned integer
    # 18    UVARI   1, 2, or 4    Variable-length unsigned integer
    # 19    IDENT   V               Variable-length identifier
    # 20    ASCII   V               Variable-length ASCII character string
    21: 8,  # Date and time
    # 22    ORIGIN  V               Origin reference
    # 23    OBNAME  V               Object name
    # 24    OBJREF  V               Object reference
    # 25    ATTREF  V               Attribute reference
    26: 1,  # Boolean status
    # 27    UNITS   V               Units expression
}


def is_fixed_length(rc: int) -> bool:
    """True if the Representation Code is fixed length."""
    return rc in REP_CODE_FIXED_LENGTHS


def rep_code_fixed_length(rc: int) -> int:
    """Returns the length in bytes of a fixed length Rep Code.
    Will raise an ExceptionRepCode if the Rep Code is not of fixed length."""
    try:
        return REP_CODE_FIXED_LENGTHS[rc]
    except KeyError as err:
        raise ExceptionRepCode(f'Representation code {rc} is not fixed length.') from err


def FSINGL(ld: LogicalData) -> float:
    """Representation code 2, IEEE single precision floating point."""
    by = ld.chunk(4)
    value = struct.unpack('>f', by)
    return value[0]


def VSINGL(ld: LogicalData) -> float:
    """Representation code 6, VAX single precision floating point."""
    by = ld.chunk(4)
    s = (by[1] & 0x80)
    m = ((by[0] & 0x7f) << 16) | (by[3] << 8) | by[2]
    e = ((by[1] & 0x7f) << 1) | ((by[0] & 0x80) >> 7)
    if e == 0 and s == 0:
        # m is arbitrary
        return 0.0
    m = float(m) / (1 << 23)
    value = (0.5 + m) * 2**(e - 128)
    if s:
        return -value
    return value


def FDOUBL(ld: LogicalData) -> float:
    """Representation code 7, IEEE double precision floating point."""
    by = ld.chunk(8)
    value = struct.unpack('>d', by)
    return value[0]


def _pascal_string(ld: LogicalData) -> bytes:
    """Reads a Pascal like string from the LogicalData."""
    siz: int = ld.read()
    return ld.chunk(siz)


def SSHORT(ld: LogicalData) -> int:
    """
    SSHORT Representation code 12, Signed 1-byte integer.
    [RP66V1 Appendix B Section B.12]
    """
    r = ld.read()
    if r > 127:
        r -= 256
    return r

def SNORM(ld: LogicalData) -> int:
    """
    Representation code 13, Signed 2-byte integer.
    [RP66V1 Appendix B Section B.13]
    """
    by = ld.chunk(2)
    value = struct.unpack('>h', by)
    return value[0]


def SLONG(ld: LogicalData) -> int:
    """
    Representation code 14, Signed 4-byte integer.
    [RP66V1 Appendix B Section B.14]
    """
    by = ld.chunk(4)
    value = struct.unpack('>i', by)
    return value[0]


def USHORT(ld: LogicalData) -> int:
    """
    USHORT Representation code 15, Unsigned 1-byte integer.
    [RP66V1 Appendix B Section B.15]
    """
    return ld.read()


def UNORM(ld: LogicalData) -> int:
    """
    Representation code 16, Unsigned 2-byte integer.
    [RP66V1 Appendix B Section B.16]
    """
    ret = ld.read()
    ret <<= 8
    ret |= ld.read()
    return ret


def ULONG(ld: LogicalData) -> int:
    """
    Representation code 16, Unsigned 4-byte integer.
    [RP66V1 Appendix B Section B.17]
    """
    by = ld.chunk(4)
    value = struct.unpack('>I', by)
    return value[0]


def UVARI(ld: LogicalData) -> int:
    """
    Representation code 18, Variable-length unsigned integer.
    [RP66V1 Appendix B Section B.18]
    """
    value: int = ld.read()
    if value & 0xc0 == 0x80:
        # Two bytes
        value &= 0x7f
        value <<= 8
        value |= ld.read()
        # TODO: Raise if < 2**7
    elif value & 0xc0 == 0xc0:
        # Four bytes
        value &= 0x3f
        value <<= 8
        value |= ld.read()
        value <<= 8
        value |= ld.read()
        value <<= 8
        value |= ld.read()
        # TODO: Raise if < 2**14
    return value


def UVARI_len(by: typing.Union[bytes, bytearray], index: int) -> int:
    """
    Return the number of bytes that will be read as a UVARI or zero on failure.
    NOTE: This does not check that the length of the bytes object is sufficient.
    """
    if index < 0:
        raise ExceptionRepCode('Index can not be negative.')
    if len(by) <= index:
        return 0
    value: int = by[index]
    if value & 0xc0 == 0x80:
        return 2
    elif value & 0xc0 == 0xc0:
        return 4
    return 1


def IDENT(ld: LogicalData) -> bytes:
    """
    Representation code 19, Variable length identifier. Length up to 256 bytes.
    [RP66V1 Appendix B Section B.19]
    """
    return _pascal_string(ld)


def IDENT_len(by: typing.Union[bytes, bytearray], index: int) -> int:
    """
    Return the number of bytes that will be read as a IDENT or zero on failure.
    NOTE: This does not check that the length of the bytes object is sufficient.
    """
    if index < 0:
        raise ExceptionRepCode('Index can not be negative.')
    if len(by) <= index:
        return 0
    # One byte for the length plus the length
    return 1 + by[index]


def ASCII(ld: LogicalData) -> bytes:
    """
    Representation code 20, Variable length identifier. Length up to 2**30-1 bytes.
    [RP66V1 Appendix B Section B.20]
    """
    size: int = UVARI(ld)
    return ld.chunk(size)


class DateTime:
    """Representation code 21, Date/time. [RP66V1 Appendix B Section B.21]
    TZ = Time Zone (0 = Local Standard, 1 = Local Daylight Savings, 2 = Greenwich Mean Time)"""
    TZ_ABBREVIATION: typing.Dict[int, typing.Tuple[str, str]] = {
        0: ('STD', 'Local Standard'),
        1: ('DST', 'Local Daylight Savings'),
        2: ('GMT', 'Greenwich Mean Time'),
    }
    STRFTIME_FORMAT = '%y-%m-%d %H:%M:%S.%f'

    def __init__(self, ld: LogicalData):
        # TODO: Check ranges
        self.year: int = USHORT(ld) + 1900
        v: int = ld.read()
        self.tz: int = (v >> 4) & 0xf
        self.month: int = v & 0xf
        self.day: int = USHORT(ld)
        self.hour: int = USHORT(ld)
        self.minute: int = USHORT(ld)
        self.second: int = USHORT(ld)
        self.millisecond: int = UNORM(ld)

    @property
    def tz_abbreviation(self) -> str:
        """The time zone abbreviation such as 'STD', 'DST', 'GMT' or empty string if unknown."""
        try:
            return self.TZ_ABBREVIATION[self.tz][0]
        except KeyError:
            return ''

    @property
    def tz_description(self) -> str:
        """The time zone description such as 'Greenwich Mean Time' or empty string if unknown."""
        try:
            return self.TZ_ABBREVIATION[self.tz][0]
        except KeyError:
            return ''

    def __str__(self) -> str:
        return f'{self.year}-{self.month:02d}-{self.day:02d}' \
            f' {self.hour:02d}:{self.minute:02d}:{self.second:02d}.{self.millisecond:03d} {self.tz_abbreviation}'

    def __repr__(self) -> str:
        return f'<{self.__class__} {str(self)}>'

    def as_datetime(self) -> datetime.datetime:
        """Returns a (naive) Python datetime for the date and time."""
        return datetime.datetime(
            self.year, self.month, self.day, self.hour, self.minute, self.second, microsecond=self.millisecond*1000
        )


def DTIME(ld: LogicalData) -> DateTime:
    """
    Representation code 21, Date/time.
    [RP66V1 Appendix B Section B.21]
    """
    return DateTime(ld)


def ORIGIN(ld: LogicalData) -> int:
    """An ORIGIN is an alias for UVARI."""
    return UVARI(ld)


def ORIGIN_len(by: typing.Union[bytes, bytearray], index: int) -> int:
    """Return the number of bytes that will be read as a ORIGIN or zero on failure."""
    return UVARI_len(by, index)


class ObjectName(typing.NamedTuple):
    """This has three fields:

    0. O - Origin Reference as a ORIGIN type (UVARI).
    1. C - Copy number as a USHORT type.
    2. I - Identifier as an IDENT type.
    """
    O: int
    C: int
    I: bytes

    def __str__(self):
        return f'OBNAME: O: {self.O} C: {self.C} I: {self.I}'

    def __format__(self, format_spec):
        return f'OBNAME: O: {self.O} C: {self.C} I: {str(self.I):{format_spec}}'

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.O == other.O and self.C == other.C and self.I == other.I
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            # NOTE: Order of fields.
            return self.I < other.I or self.O < other.O or self.C < other.C
        return NotImplemented


def OBNAME(ld: LogicalData) -> ObjectName:
    """
    Representation code 23, Boolean status value.
    [RP66V1 Appendix B Section B.23]
    """
    o = ORIGIN(ld)
    c = USHORT(ld)
    # TODO: Raise if non-null.
    i = IDENT(ld)
    return ObjectName(o, c, i)


def OBNAME_len(by: typing.Union[bytes, bytearray], index: int) -> int:
    """Examine the bytes and determine how many bytes are needed for a OBNAME representation.
    Returns the number of bytes or zero as an error (bytes is not long enough).

    NOTE: This does not check that the length of the bytes object is sufficient.

    O: Origin Reference is a ORIGIN, a UVARI
    C: Copy is a USHORT
    I: Identifier is an IDENT
    """
    if index < 0:
        raise ExceptionRepCode('Index can not be negative.')
    # O: Origin Reference is a ORIGIN, a UVARI
    length = ORIGIN_len(by, index)
    if length:
        # C: Copy is a USHORT
        length += 1
        if len(by) >= length + index:
            # I: Identifier is an IDENT
            ident_length = IDENT_len(by, index + length)
            if ident_length:
                length += ident_length
                return length
    return 0


class ObjectReference(typing.NamedTuple):
    """This has two fields:

    0. T - Object Type as a IDENT.
    1. N - Object Name as a OBNAME.
    """
    T: IDENT
    N: OBNAME

    def __str__(self):
        return f'OBREF: O: {self.T} C: {self.N}'


def OBJREF(ld: LogicalData) -> ObjectReference:
    """
    Representation code 24, Boolean status value.
    [RP66V1 Appendix B Section B.24]
    """
    t = IDENT(ld)
    n = OBNAME(ld)
    return ObjectReference(t, n)


def STATUS(ld: LogicalData) -> int:
    """
    Representation code 26, Boolean status value.
    [RP66V1 Appendix B Section B.26]
    """
    return USHORT(ld)


#: And commonly found in actuality
UNITS_ALLOWABLE_CHARACTERS_EXTENDED: str = '%'

#: [RP66V1 Appendix B, B.27 Code UNITS: Units Expression]
#: Syntactically, Representation Code UNITS is similar to Representation Codes IDENT and ASCII.
#: However, upper case and lower case are considered distinct (e.g., "A" and "a" for Ampere and annum, respectively),
#: and permissible characters are restricted to the following ASCII codes:
#:
#: * lower case letters ``[a, b, c, ..., z]``
#: * upper case letters ``[A, B, C, ..., Z]``
#: * digits ``[0, 1, 2, ..., 9]``
#: * blank ``[ ]``
#: * hyphen or minus sign ``[-]`` dot or period ``[.]``
#: * slash ``[/]``
#: * parentheses ``[(, )]``
#:
#: In particular this allows bytes.decode('ascii')
UNITS_ALLOWABLE_CHARACTERS: typing.Set[int] = set(
    bytes(
        string.ascii_lowercase
        + string.ascii_uppercase
        + string.digits
        + ' '
        + '-.'
        + '/'
        + '()'
        + UNITS_ALLOWABLE_CHARACTERS_EXTENDED
        , 'ascii')
)
#: UNITS_ALLOWABLE_CHARACTERS as a string.
UNITS_ALLOWABLE_CHARACTERS_AS_STRING: str = ''.join(sorted(chr(v) for v in UNITS_ALLOWABLE_CHARACTERS))


def UNITS(ld: LogicalData) -> bytes:
    """Read UNITS from the LogicalData."""
    ret: bytes = _pascal_string(ld)
    # [RP66V1 Appendix B, B.27 Code UNITS: Units Expression]
    bad_chars = set(ret) - UNITS_ALLOWABLE_CHARACTERS
    if bad_chars:
        bad_chars_as_str = ''.join(sorted(chr(v) for v in bad_chars))
        msg = f'UNITS "{ret}" has characters {bad_chars} "{bad_chars_as_str}"' \
            f' that are not allowed, only "{UNITS_ALLOWABLE_CHARACTERS_AS_STRING}"' \
            f' is specified. See [RP66V1 Appendix B, B.27 Code UNITS: Units Expression]'
        # warnings.warn(msg)
        logger.warning(msg)
        # raise ExceptionRepCode(msg)
    return ret


#: Map of Representation code name to functions that take a LogicalData object.
#: Has the range 1 to 27 inclusive with some Rep Codes unsupported.
REP_CODE_MAP = {
    # 1: FSHORT,
    2: FSINGL,
    # 3: FSING1,
    # 4: FSING2,
    # 5: ISINGL,
    6: VSINGL,
    7: FDOUBL,
    # 8: FDOUB1,
    # 9: FDOUB2,
    # 10: CSINGL,
    # 11: CDOUBL,
    12: SSHORT,
    13: SNORM,
    14: SLONG,
    15: USHORT,
    16: UNORM,
    17: ULONG,
    18: UVARI,
    19: IDENT,
    20: ASCII,
    21: DTIME,
    22: ORIGIN,
    23: OBNAME,
    24: OBJREF,
    # 25: ATTREF,
    26: STATUS,
    27: UNITS,
}
assert set(REP_CODE_MAP.keys()) == REP_CODES_SUPPORTED


def code_read(rep_code: int, ld: LogicalData):
    """Read the Rep Code value from the LogicalData."""
    try:
        return REP_CODE_MAP[rep_code](ld)
    except KeyError as err:
        raise ExceptionRepCode(f'Unsupported Representation code {rep_code}') from err

# Numpy related stuff

#: Numpy dtypes, numeric Rep Codes only.
REP_CODE_NUMPY_TYPE_MAP = {
    2: np.float32,

    6: np.float32,
    7: np.float64,

    12: np.int8,
    13: np.int16,
    14: np.int32,
    15: np.uint8,
    16: np.uint16,
    17: np.uint32,
    18: np.uint64,
}
assert set(REP_CODE_NUMPY_TYPE_MAP.keys()) - REP_CODES_SUPPORTED == set()


def numpy_dtype(rep_code: int):
    """Returns the numpy dtype corresponding to the Rep Code.
    Will raise ExceptionRepCode for unsupported Rep code."""
    try:
        return REP_CODE_NUMPY_TYPE_MAP[rep_code]
    except KeyError as err:
        raise ExceptionRepCode(f'Unsupported Representation code {rep_code}') from err


class NumericCategory(enum.Enum):
    """Categories of Representation Codes. Useful for deciding absent value."""
    NONE = 0
    INTEGER = 1
    FLOAT = 2

#: Categories of Representation Codes. These should match REP_CODE_NUMPY_TYPE_MAP.
REP_CODE_CATEGORY_MAP: typing.Dict[int, NumericCategory] = {
    # 1: FSHORT,
    2: NumericCategory.FLOAT,  # FSINGL,
    # 3: NumericCategory.NONE,  # FSING1,
    # 4: NumericCategory.NONE,  # FSING2,
    # 5: NumericCategory.FLOAT,  # ISINGL,
    6: NumericCategory.FLOAT,  # VSINGL,
    7: NumericCategory.FLOAT,  # FDOUBL,
    # 8: NumericCategory.NONE,  # FDOUB1,
    # 9: NumericCategory.NONE,  # FDOUB2,
    # 10: NumericCategory.NONE,  # CSINGL,
    # 11: NumericCategory.NONE,  # CDOUBL,
    12: NumericCategory.INTEGER,  # SSHORT,
    13: NumericCategory.INTEGER,  # SNORM,
    14: NumericCategory.INTEGER,  # SLONG,
    15: NumericCategory.INTEGER,  # USHORT,
    16: NumericCategory.INTEGER,  # UNORM,
    17: NumericCategory.INTEGER,  # ULONG,
    18: NumericCategory.INTEGER,  # UVARI,
    19: NumericCategory.NONE,  # IDENT,
    20: NumericCategory.NONE,  # ASCII,
    21: NumericCategory.NONE,  # DTIME,
    22: NumericCategory.NONE,  # ORIGIN,
    23: NumericCategory.NONE,  # OBNAME,
    24: NumericCategory.NONE,  # OBJREF,
    # 25: NumericCategory.NONE,  # ATTREF,
    26: NumericCategory.NONE,  # STATUS,
    27: NumericCategory.NONE,  # UNITS,
}
assert set(REP_CODE_CATEGORY_MAP.keys()) == REP_CODES_SUPPORTED


# Sanity check
for r in REP_CODE_NUMPY_TYPE_MAP.keys():
    if np.issubdtype(REP_CODE_NUMPY_TYPE_MAP[r], np.integer):
        assert REP_CODE_CATEGORY_MAP[r] == NumericCategory.INTEGER
    elif np.issubdtype(REP_CODE_NUMPY_TYPE_MAP[r], np.floating):
        assert REP_CODE_CATEGORY_MAP[r] == NumericCategory.FLOAT
    else: # pragma: no cover
        assert 0
del r
