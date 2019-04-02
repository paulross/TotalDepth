"""
Python implementation the Representation Codes [RP66V1 Appendix B]

References:
RP66V1: http://w3.energistics.org/rp66/v1/rp66v1.html
Specifically Appendix B: http://w3.energistics.org/rp66/v1/rp66v1_appb.html

From: http://w3.energistics.org/rp66/v1/rp66v1_appb.html
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
import collections
import struct

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core.File import LogicalData


class ExceptionRepCode(ExceptionTotalDepthRP66V1):
    pass


REP_CODE_INT_TO_STR = {
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
REP_CODE_STR_TO_INT = {v: k for k, v in REP_CODE_INT_TO_STR.items()}


def FSINGL(ld: LogicalData) -> float:
    """Representation code 2, IEEE single precision floating point"""
    by = ld.chunk(4)
    value = struct.unpack('>f', by)
    return value[0]


def FDOUBL(ld: LogicalData) -> float:
    """Representation code 7, IEEE double precision floating point"""
    by = ld.chunk(8)
    value = struct.unpack('>d', by)
    return value[0]


def _pascal_string(ld: LogicalData) -> bytes:
    siz: int = ld.read()
    return ld.chunk(siz)


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


def IDENT(ld: LogicalData) -> bytes:
    """
    Representation code 19, Variable length identifier. Length up to 256 bytes.
    [RP66V1 Appendix B Section B.19]
    """
    return _pascal_string(ld)


def ASCII(ld: LogicalData) -> bytes:
    """
    Representation code 20, Variable length identifier. Length up to 2**30-1 bytes.
    [RP66V1 Appendix B Section B.20]
    """
    size: int = UVARI(ld)
    return ld.chunk(size)


class DateTime:
    def __init__(self, ld: LogicalData):
        # TODO: Check ranges
        self.year: int = USHORT(ld) + 1900
        v: int = ld.read()
        self.tz = (v >> 4) & 0xf
        self.month: int = v & 0xf
        self.day: int = USHORT(ld)
        self.hour: int = USHORT(ld)
        self.minute: int = USHORT(ld)
        self.second: int = USHORT(ld)
        self.millisecond: int = UNORM(ld)

    def __str__(self):
        # TODO: Timezone
        return f'{self.year}-{self.month:02d}-{self.day:02d}' \
            f' {self.hour:02d}:{self.minute:02d}:{self.second:02d}.{self.millisecond:03d}'

    __repr__ = __str__


def DTIME(ld: LogicalData) -> DateTime:
    """
    Representation code 21, Date/time.
    [RP66V1 Appendix B Section B.21]
    """
    return DateTime(ld)


def ORIGIN(ld: LogicalData) -> int:
    return UVARI(ld)


# This has three fields:
# O - Origin Reference as a ORIGIN type (UVARI).
# C - Copy number as a USHORT type.
# I - Identifier as an IDENT type.
class ObjectName(collections.namedtuple('ObjectName', 'O, C, I')):

    def __str__(self):
        return f'OBNAME: O: {self.O} C: {self.C} I: {self.I}'


def OBNAME(ld: LogicalData) -> ObjectName:
    """
    Representation code 23, Boolean status value.
    [RP66V1 Appendix B Section B.23]
    """
    o = ORIGIN(ld)
    c = USHORT(ld)
    i = IDENT(ld)
    return ObjectName(o, c, i)


# This has three fields:
# T - Object Type as a IDENT.
# N - Object Name as a OBNAME.
class ObjectReference(collections.namedtuple('ObjectReference', 'T, N')):

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


def UNITS(ld: LogicalData) -> bytes:
    ret = _pascal_string(ld)
    # TODO: Validate according to the specification
    return ret


# Map of Representation code name to functions that take a LogicalData object.
REP_CODE_MAP = {
    2: FSINGL,
    7: FDOUBL,
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
    26: STATUS,
    27: UNITS,
}


def code_read(rep_code: int, ld: LogicalData):
    return REP_CODE_MAP[rep_code](ld)
