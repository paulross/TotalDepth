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

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core.File import LogicalData


class ExceptionRepCode(ExceptionTotalDepthRP66V1):
    pass


def _pascal_string(ld: LogicalData) -> bytes:
    siz: int = ld.read()
    return ld.chunk(siz)


def USHORT(ld: LogicalData) -> int:
    return ld.read()


def UVARI(ld: LogicalData) -> int:
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
    return _pascal_string(ld)


def ORIGIN(ld: LogicalData) -> int:
    return UVARI(ld)


ObjectName = collections.namedtuple('ObjectName', 'O, C, I')


def OBNAME(ld: LogicalData) -> ObjectName:
    o = ORIGIN(ld)
    c = USHORT(ld)
    i = IDENT(ld)
    return ObjectName(o, c, i)


def UNITS(ld: LogicalData) -> bytes:
    # TODO: Validate according to the specification
    return _pascal_string(ld)


# Map of Representation code name to functions that take a LogicalData object.
REP_CODE_MAP = {
    15: USHORT,
    18: UVARI,
    19: IDENT,
    22: ORIGIN,
    23: OBNAME,
    27: UNITS,
}


def code_read(rep_code: int, ld: LogicalData):
    return REP_CODE_MAP[rep_code](ld)
