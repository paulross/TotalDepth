#!/usr/bin/env python
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 1999-2012 Paul Ross
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# 
# Paul Ross: apaulross@gmail.com
"""TODO: We need to come up with, basically, an encoding design that allows us
to read from a stream and convert to an internal type or vice versa. The stream
interface in both cases is bytes.

Created on Aug 3, 2011

@author: paulross
"""

#import logging
import collections
import struct
import string
import time
import datetime

class ExceptionRepCode(Exception):
    pass

class ExceptionRepCodeEndOfStream(ExceptionRepCode):
    """Raised if a partial read occurs when a premature EOF is encountered."""
    pass

class ExceptionRepCodeWriteToStream(ExceptionRepCode):
    """Raised when a write fails."""
    pass

class ExceptionRepCodeCodeNumberOutOfRange(ExceptionRepCode):
    pass

class ExceptionRepCodeUnknownSymbolicName(ExceptionRepCode):
    pass

class ExceptionRepCodePascalLikeBase(ExceptionRepCode):
    """Raised for PascalLikeBase objects such as STRING, IDENT etc."""
    pass

class ExceptionRepCodeFixedLength(ExceptionRepCode):
    """Raised when a call to lenFixedCode() is made with a variable length rep code."""
    pass

class ExceptionRepCodeUVARI(ExceptionRepCode):
    pass

class ExceptionRepCodeIDENT(ExceptionRepCode):
    pass

class ExceptionRepCodeASCII(ExceptionRepCode):
    pass

class ExceptionRepCodeBINARY(ExceptionRepCode):
    pass

#######################################################
# Section: Struct for unpacking byte() arrays to words.
# Note: For floats these pull out signed integer words.
#######################################################

# TODO: Put this in utils and merge with LIS equivalent

# Generic unsigned integers
# Generic 1 byte unsigned integer
STRUCT_RC_UINT_1 = struct.Struct('>B')
# 1 bytes, 1 field.
assert(STRUCT_RC_UINT_1.size == 1)
assert(len(STRUCT_RC_UINT_1.unpack(b' ' * STRUCT_RC_UINT_1.size)) == 1)
# Generic 2 byte unsigned integer
STRUCT_RC_UINT_2 = struct.Struct('>H')
# 2 bytes, 1 field.
assert(STRUCT_RC_UINT_2.size == 2)
assert(len(STRUCT_RC_UINT_2.unpack(b' ' * STRUCT_RC_UINT_2.size)) == 1)
# Generic 4 byte unsigned integer
STRUCT_RC_UINT_4 = struct.Struct('>I')
# 4 bytes, 1 field.
assert(STRUCT_RC_UINT_4.size == 4)
assert(len(STRUCT_RC_UINT_4.unpack(b' ' * STRUCT_RC_UINT_4.size)) == 1)

# Generic signed integers
# Generic 1 byte signed integer
STRUCT_RC_INT_1 = struct.Struct('>b')
# 1 bytes, 1 field.
assert(STRUCT_RC_INT_1.size == 1)
assert(len(STRUCT_RC_INT_1.unpack(b' ' * STRUCT_RC_INT_1.size)) == 1)
# Generic 2 byte signed integer
STRUCT_RC_INT_2 = struct.Struct('>h')
# 2 bytes, 1 field.
assert(STRUCT_RC_INT_2.size == 2)
assert(len(STRUCT_RC_INT_2.unpack(b' ' * STRUCT_RC_INT_2.size)) == 1)
# Generic 4 byte signed integer
STRUCT_RC_INT_4 = struct.Struct('>i')
# 4 bytes, 1 field.
assert(STRUCT_RC_INT_4.size == 4)
assert(len(STRUCT_RC_INT_4.unpack(b' ' * STRUCT_RC_INT_4.size)) == 1)
#######################################################
# End: Struct for unpacking byte() arrays to words.
#######################################################

###################################
# Section: Simple Rep Code structs.
###################################
#1    FSHORT    Low precision floating point    NUMBER    S    2
#2    FSINGL    IEEE single precision floating point    NUMBER    S    4
#5    ISINGL    IBM single precision floating point    NUMBER    S    4
#6    VSINGL    VAX single precision floating point    NUMBER    S    4
#7    FDOUBL    IEEE double precision floating point    NUMBER    S    8
#12    SSHORT    Short signed integer    NUMBER    S    1
#13    SNORM    Normal signed integer    NUMBER    S    2
#14    SLONG    Long signed integer    NUMBER    S    4
#15    USHORT    Short unsigned integer    NUMBER    S    1
#16    UNORM    Normal unsigned integer    NUMBER    S    2
#17    ULONG    Long unsigned integer    NUMBER    S    4
#18    UVARI    Variable-length unsigned integer    NUMBER    S    1, 2, or 4
#19    IDENT    Variable-length identifier    STRING    S    V
#20    ASCII    Variable-length ASCII character string    STRING    S    V
#22    ORIGIN    Origin reference    ORIGIN    S    V
#26    STATUS    Boolean status    STATUS    S    1
#27    UNITS    Units expression    UNIT    S    V
#30    ISNORM    Inverted order normal signed integer    NUMBER    S    2
#31    ISLONG    Inverted order long signed integer    NUMBER    S    4
#32    IUNORM    Inverted order normal unsigned integer    NUMBER    S    2
#33    IULONG    Inverted order long unsigned integer    NUMBER    S    4
#39    LOGICL    Logical    STATUS    S    1
#40    BINARY    Binary    BINARY    S    V

#============================================
# Section: Fixed length representation codes.
#============================================
#1    FSHORT    Low precision floating point    NUMBER    S    2
STRUCT_RC_FSHORT = STRUCT_RC_INT_2 # Needs further interpretation
#2    FSINGL    IEEE single precision floating point    NUMBER    S    4
STRUCT_RC_FSINGL = struct.Struct('>f')

#5    ISINGL    IBM single precision floating point    NUMBER    S    4
STRUCT_RC_ISINGL = STRUCT_RC_INT_4 # Needs further interpretation
#6    VSINGL    VAX single precision floating point    NUMBER    S    4
STRUCT_RC_VSINGL = STRUCT_RC_INT_4 # Needs further interpretation
#7    FDOUBL    IEEE double precision floating point    NUMBER    S    8
STRUCT_RC_FDOUBL = struct.Struct('>d')

#12    SSHORT    Short signed integer    NUMBER    S    1
STRUCT_RC_SSHORT = STRUCT_RC_INT_1
#13    SNORM    Normal signed integer    NUMBER    S    2
STRUCT_RC_SNORM = STRUCT_RC_INT_2
#14    SLONG    Long signed integer    NUMBER    S    4
STRUCT_RC_SLONG = STRUCT_RC_INT_4
#15    USHORT    Short unsigned integer    NUMBER    S    1
STRUCT_RC_USHORT = STRUCT_RC_UINT_1
#16    UNORM    Normal unsigned integer    NUMBER    S    2
STRUCT_RC_UNORM = STRUCT_RC_UINT_2
#17    ULONG    Long unsigned integer    NUMBER    S    4
STRUCT_RC_ULONG = STRUCT_RC_UINT_4

#26    STATUS    Boolean status    STATUS    S    1
STRUCT_RC_STATUS = STRUCT_RC_UINT_1

#30    ISNORM    Inverted order normal signed integer    NUMBER    S    2
STRUCT_RC_ISNORM = struct.Struct('<h')
#31    ISLONG    Inverted order long signed integer    NUMBER    S    4
STRUCT_RC_ISLONG = struct.Struct('<i')
#32    IUNORM    Inverted order normal unsigned integer    NUMBER    S    2
STRUCT_RC_IUNORM = struct.Struct('<H')
#33    IULONG    Inverted order long unsigned integer    NUMBER    S    4
STRUCT_RC_IULONG = struct.Struct('<I')
#39    LOGICL    Logical    STATUS    S    1
STRUCT_RC_LOGICL = STRUCT_RC_UINT_1

## TODO: Move to unit testing
## Sanity check for structs not defined with integer structs
#assert(STRUCT_RC_FSINGL.size == RC_TABLE[1].Size)
#assert(len(STRUCT_RC_FSINGL.unpack(b' ' * STRUCT_RC_FSINGL.size)) == 1)
#
#assert(STRUCT_RC_FSINGL.size == RC_TABLE[8].Size)
#assert(len(STRUCT_RC_FSINGL.unpack(b' ' * STRUCT_RC_FSINGL.size)) == 1)
#
#assert(STRUCT_RC_ISNORM.size == 2)
#assert(len(STRUCT_RC_ISNORM.unpack(b' ' * STRUCT_RC_ISNORM.size)) == 1)
#assert(STRUCT_RC_ISLONG.size == 4)
#assert(len(STRUCT_RC_ISLONG.unpack(b' ' * STRUCT_RC_ISLONG.size)) == 1)
#assert(STRUCT_RC_IUNORM.size == 2)
#assert(len(STRUCT_RC_IUNORM.unpack(b' ' * STRUCT_RC_IUNORM.size)) == 1)
#assert(STRUCT_RC_IULONG.size == 4)
#assert(len(STRUCT_RC_IULONG.unpack(b' ' * STRUCT_RC_IULONG.size)) == 1)
#assert(STRUCT_RC_LOGICL.size == 1)
#assert(len(STRUCT_RC_LOGICL.unpack(b' ' * STRUCT_RC_LOGICL.size)) == 1)

def _read(theStream, theStruct):
    """Reads a from theStream theStruct.size bytes and returns them.
    May raise ExceptionRepCodeEndOfStream if not enough on the stream to read."""
    b = theStream.read(theStruct.size)
    if len(b) != theStruct.size:
        raise ExceptionRepCodeEndOfStream('EOF: Got {:d} bytes but expected {:d} bytes.'.format(len(b), theStruct.size))
    return b

def _readStruct(theStream, theStruct):
    """Reads a from theStream which must have read(n) implemented that returns bytes.
    May raise ExceptionRepCodeEndOfStream if not enough on the stream to read."""
    return theStruct.unpack(_read(theStream, theStruct))

def _writeStruct(theVal, theStream, theStruct):
    """Writes theVal to theStream using theStruct to encode it.
    theStream must have write(bytes) implemented."""
    l = theStream.write(theStruct.pack(theVal))
    if l != theStruct.size:
        raise ExceptionRepCodeWriteToStream('Only able to write {:d} bytes but expected to write {:d} bytes'.format(l, theStruct.size))
    return l

#======================================
# Section: Specific Read/Write methods.
#======================================

#1    FSHORT    Low precision floating point    NUMBER    S    2
def readFSHORT(theS):
    b = _readStruct(theS, STRUCT_RC_FSHORT)
    # TODO: munge the bytes
    
def writeFSHORT(theV, theS):
    # TODO: munge the bytes
    return _writeStruct(theV, theS, STRUCT_RC_FSHORT)
    
#2    FSINGL    IEEE single precision floating point    NUMBER    S    4
def readFSINGL(theS):
    return _readStruct(theS, STRUCT_RC_FSINGL)[0]

def writeFSINGL(theV, theS):
    return _writeStruct(theV, theS, STRUCT_RC_FSINGL)

#5    ISINGL    IBM single precision floating point    NUMBER    S    4
def readISINGL(theS):
    b = _readStruct(theS, STRUCT_RC_ISINGL)
    # TODO: munge the bytes

def writeISINGL(theV, theS):
    # TODO: munge the bytes
    return _writeStruct(theV, theS, STRUCT_RC_ISINGL)

#6    VSINGL    VAX single precision floating point    NUMBER    S    4
def readVSINGL(theS):
    b = _readStruct(theS, STRUCT_RC_VSINGL)
    # TODO: munge the bytes

def writeVSINGL(theV, theS):
    # TODO: munge the bytes
    return _writeStruct(theV, theS, STRUCT_RC_VSINGL)

#7    FDOUBL    IEEE double precision floating point    NUMBER    S    8
def readFDOUBL(theS):
    return _readStruct(theS, STRUCT_RC_FDOUBL)[0]

def writeFDOUBL(theV, theS):
    return _writeStruct(theV, theS, STRUCT_RC_FDOUBL)

#12    SSHORT    Short signed integer    NUMBER    S    1
def readSSHORT(theS):
    r = _readStruct(theS, STRUCT_RC_SSHORT)[0]
    return r

def writeSSHORT(theV, theS):
    return _writeStruct(theV, theS, STRUCT_RC_SSHORT)

#13    SNORM    Normal signed integer    NUMBER    S    2
def readSNORM(theS):
    return _readStruct(theS, STRUCT_RC_SNORM)[0]

def writeSNORM(theV, theS):
    return _writeStruct(theV, theS, STRUCT_RC_SNORM)

#14    SLONG    Long signed integer    NUMBER    S    4
def readSLONG(theS):
    return _readStruct(theS, STRUCT_RC_SLONG)[0]

def writeSLONG(theV, theS):
    return _writeStruct(theV, theS, STRUCT_RC_SLONG)

#15    USHORT    Short unsigned integer    NUMBER    S    1
def readUSHORT(theS):
    return _readStruct(theS, STRUCT_RC_USHORT)[0]

def writeUSHORT(theV, theS):
    return _writeStruct(theV, theS, STRUCT_RC_USHORT)

#16    UNORM    Normal unsigned integer    NUMBER    S    2
def readUNORM(theS):
    return _readStruct(theS, STRUCT_RC_UNORM)[0]

def writeUNORM(theV, theS):
    return _writeStruct(theV, theS, STRUCT_RC_UNORM)

#17    ULONG    Long unsigned integer    NUMBER    S    4
def readULONG(theS):
    return _readStruct(theS, STRUCT_RC_ULONG)[0]

def writeULONG(theV, theS):
    return _writeStruct(theV, theS, STRUCT_RC_ULONG)

#26    STATUS    Boolean status    STATUS    S    1
def readSTATUS(theS):
    return _readStruct(theS, STRUCT_RC_STATUS)[0]

def writeSTATUS(theV, theS):
    return _writeStruct(theV, theS, STRUCT_RC_STATUS)

#30    ISNORM    Inverted order normal signed integer    NUMBER    S    2
def readISNORM(theS):
    return _readStruct(theS, STRUCT_RC_ISNORM)[0]

def writeISNORM(theV, theS):
    return _writeStruct(theV, theS, STRUCT_RC_ISNORM)

#31    ISLONG    Inverted order long signed integer    NUMBER    S    4
def readISLONG(theS):
    return _readStruct(theS, STRUCT_RC_ISLONG)[0]

def writeISLONG(theV, theS):
    return _writeStruct(theV, theS, STRUCT_RC_ISLONG)

#32    IUNORM    Inverted order normal unsigned integer    NUMBER    S    2
def readIUNORM(theS):
    return _readStruct(theS, STRUCT_RC_IUNORM)[0]

def writeIUNORM(theV, theS):
    return _writeStruct(theV, theS, STRUCT_RC_IUNORM)

#33    IULONG    Inverted order long unsigned integer    NUMBER    S    4
def readIULONG(theS):
    return _readStruct(theS, STRUCT_RC_IULONG)[0]

def writeIULONG(theV, theS):
    return _writeStruct(theV, theS, STRUCT_RC_IULONG)

#39    LOGICL    Logical    STATUS    S    1
def readLOGICL(theS):
    return _readStruct(theS, STRUCT_RC_LOGICL)[0]

def writeLOGICL(theV, theS):
    return _writeStruct(theV, theS, STRUCT_RC_LOGICL)

#============================================
# End: Fixed length representation codes.
#============================================

###################################################
# Section: Representation code general information.
###################################################
# Fields (note camel case names come from the standard):
# Code - An unique integer as a USHORT i.e. >=0 and <256.
# SymbolicName - ASCII uppercase name.
# Description - A string.
# Class - Some kind of taxonomy going on here.
# Type - 'S' fo r'simple rep code, 'C' for a compound rep code composed of more than one simple rep codes.
# Size - Either:
#        Number of bytes as an integer, -1 means variable length.
#        Tuple of integer possible sizes.
RcTableEntry = collections.namedtuple('RcTableEntry', 'Code SymbolicName Description Class Type Size')

# Based on http://w3.energistics.org/RP66/V2/rp66v2_sec2.html#11_2
RC_TABLE_HEADER = RcTableEntry('Code', 'Symbolic Name', 'Short Description', 'Class', 'Type', 'Size in Bytes'),
RC_TABLE = [
    None, # Padding to make ordinal match
    RcTableEntry(1, 'FSHORT', 'Low precision floating point', 'NUMBER', 'S', 2),
    RcTableEntry(2, 'FSINGL', 'IEEE single precision floating point', 'NUMBER', 'S', 4),
    RcTableEntry(3, 'FSING1', 'Validated single precision floating point', 'BALANCED-INTERVAL', 'C', 8),
    RcTableEntry(4, 'FSING2', 'Two-way validated single precision floating point', 'UNBALANCED-INTERVAL', 'C', 12),
    RcTableEntry(5, 'ISINGL', 'IBM single precision floating point', 'NUMBER', 'S', 4),
    RcTableEntry(6, 'VSINGL', 'VAX single precision floating point', 'NUMBER', 'S', 4),
    RcTableEntry(7, 'FDOUBL', 'IEEE double precision floating point', 'NUMBER', 'S', 8),
    RcTableEntry(8, 'FDOUB1', 'Validated double precision floating point', 'BALANCED-INTERVAL', 'C', 16),
    RcTableEntry(9, 'FDOUB2', 'Two-way validated double precision floating point', 'UNBALANCED-INTERVAL', 'C', 24),
    RcTableEntry(10, 'CSINGL', 'Single precision complex', 'COMPLEX', 'C', 8),
    RcTableEntry(11, 'CDOUBL', 'Double precision complex', 'COMPLEX', 'C', 16),
    RcTableEntry(12, 'SSHORT', 'Short signed integer', 'NUMBER', 'S', 1),
    RcTableEntry(13, 'SNORM', 'Normal signed integer', 'NUMBER', 'S', 2),
    RcTableEntry(14, 'SLONG', 'Long signed integer', 'NUMBER', 'S', 4),
    RcTableEntry(15, 'USHORT', 'Short unsigned integer', 'NUMBER', 'S', 1),
    RcTableEntry(16, 'UNORM', 'Normal unsigned integer', 'NUMBER', 'S', 2),
    RcTableEntry(17, 'ULONG', 'Long unsigned integer', 'NUMBER', 'S', 4),
    RcTableEntry(18, 'UVARI', 'Variable-length unsigned integer', 'NUMBER', 'S', (1, 2, 4)),
    RcTableEntry(19, 'IDENT', 'Variable-length identifier', 'STRING', 'S', -1),
    RcTableEntry(20, 'ASCII', 'Variable-length ASCII character string', 'STRING', 'S', -1),
    RcTableEntry(21, 'DTIME', 'Date and time', 'TIME', 'C', 8),
    RcTableEntry(22, 'ORIGIN', 'Origin reference', 'ORIGIN', 'S', -1),
    RcTableEntry(23, 'OBNAME', 'Object name', 'REFERENCE', 'C', -1),
    RcTableEntry(24, 'OBJREF', 'Object reference', 'REFERENCE', 'C', -1),
    RcTableEntry(25, 'ATTREF', 'Attribute reference', 'ATTRIBUTE', 'C', -1),
    RcTableEntry(26, 'STATUS', 'Boolean status', 'STATUS', 'S', 1),
    RcTableEntry(27, 'UNITS', 'Units expression', 'UNIT', 'S', -1),
    RcTableEntry(28, 'RNORM', 'Rational', 'RATIO', 'C', 4),
    RcTableEntry(29, 'RLONG', 'Long rational', 'RATIO', 'C', 8),
    RcTableEntry(30, 'ISNORM', 'Inverted order normal signed integer', 'NUMBER', 'S', 2),
    RcTableEntry(31, 'ISLONG', 'Inverted order long signed integer', 'NUMBER', 'S', 4),
    RcTableEntry(32, 'IUNORM', 'Inverted order normal unsigned integer', 'NUMBER', 'S', 2),
    RcTableEntry(33, 'IULONG', 'Inverted order long unsigned integer', 'NUMBER', 'S', 4),
    RcTableEntry(34, 'IRNORM', 'Inverted order rational', 'RATIO', 'C', 4),
    RcTableEntry(35, 'IRLONG', 'Inverted order long rational', 'RATIO', 'C', 8),
    RcTableEntry(36, 'TIDENT', 'Tagged IDENT', 'TAG-STRING', 'C', -1),
    RcTableEntry(37, 'TUNORM', 'Tagged UNORM', 'TAG-NUMBER', 'C', (3, 4, 6)),
    RcTableEntry(38, 'TASCII', 'Tagged ASCII', 'TAG-STRING', 'C', -1),
    RcTableEntry(39, 'LOGICL', 'Logical', 'STATUS', 'S', 1),
    RcTableEntry(40, 'BINARY', 'Binary', 'BINARY', 'S', -1),
    RcTableEntry(41, 'FRATIO', 'Floating point ratio', 'RATIO', 'C', 8),
    RcTableEntry(42, 'DRATIO', 'Double precision ratio', 'RATIO', 'C', 16),
]

LEN_RC_TABLE = len(RC_TABLE)

# Sanity checks
assert(LEN_RC_TABLE == 43)
for __i, __aVal in enumerate(RC_TABLE):
    if __aVal is not None:
        assert(__i == __aVal.Code)
        # TODO: More sanity checking of RC_TABLE
    
# Create reverse lookup of {symbolic_name : code, ...} as code->symbolic name
# is catered for by RC_TABLE[code].SymbolicName
SYMBOLIC_NAME_TO_INTEGER_CODE_MAP = {}
for __aVal in RC_TABLE:
    if __aVal is not None:
        assert(__aVal.SymbolicName not in SYMBOLIC_NAME_TO_INTEGER_CODE_MAP)
        SYMBOLIC_NAME_TO_INTEGER_CODE_MAP[__aVal.SymbolicName] = __aVal.Code

def codeToName(c):
    _checkRepCodeInRange(c)
    return RC_TABLE[c].SymbolicName

def nameToCode(name):
    try:
        return SYMBOLIC_NAME_TO_INTEGER_CODE_MAP[name]
    except KeyError:
        raise ExceptionRepCodeUnknownSymbolicName('Unknown representation code {:s}'.format(str(name)))
    
def lenFixedCode(c):
    _checkRepCodeInRange(c)
    l = RC_TABLE[c].Size
    if isinstance(l, int) and l > 0:
        return l
    raise ExceptionRepCodeFixedLength('lenFixedCode(): code {:d} is variable length'.format(c))

def lenFixedName(name):
    return lenFixedCode(nameToCode(name))

###################################################
# End: Representation code general information.
###################################################

#===============================================
# Section: Variable length representation codes.
#===============================================
#18    UVARI    Variable-length unsigned integer    NUMBER    S    1, 2, or 4
#19    IDENT    Variable-length identifier    STRING    S    V
#20    ASCII    Variable-length ASCII character string    STRING    S    V
#22    ORIGIN   Origin reference    ORIGIN    S    V
#27    UNITS    Units expression    UNIT    S    V
#40    BINARY   Binary    BINARY    S    V

def readUVARI(theS):
    """Reads a UVARI from theS which must have read(n) implemented that returns bytes."""
    b = theS.read(1)[0]
    if b & 0x80:
        if b & 0x40:
            b &= 0x3F
            for i in range(3):
                b <<= 8
                b |= theS.read(1)[0]
        else:
            b &= 0x7F
            b <<= 8
            b |= theS.read(1)[0]
    return b

def writeUVARI(v, theS):
    """Side effects s by writing v (an integer) to s using UVARI (big-endian)
    format. theS must have write(bytes) implemented."""
    by = bytearray()
    l = 0
    # 2**7 - 1 is 127
    if v > 127:
        # 2**14 - 1 is 16383
        if v > 16383:
            # 4 bytes, set upper two bits
            l = 4
            by.append(0xC0 | ((v>>24) & 0x3F))
            by.append((v>>16) & 0xFF)
            by.append((v>>8) & 0xFF)
            by.append(v & 0xFF)
        else:
            # 2 bytes
            l = 2
            by.append(0x80 | (v>>8) & 0x7F)
            by.append(v & 0xFF)
    else:
        # 1 byte
        l = 1
        by.append(v & 0x7F)
    theS.write(by)

def lenUVARI(v):
    """Returns the length of a UVARI value when represented in bytes."""
    # 2**7 - 1 is 127
    if v > 127:
        # 2**14 - 1 is 16383
        if v > 16383:
            return 4
        else:
            return 2
    return 1

def readORIGIN(theS):
    """Reads a ORIGIN from theS which must have read(n) implemented that returns a single unsigned byte."""
    return readUVARI(theS)

def writeORIGIN(v, theS):
    """Side effects s by writing v (an integer) to s using ORIGIN (big-endian)
    format. theS must have write(bytes) implemented."""
    return writeUVARI(v, theS)

def lenORIGIN(v):
    """Returns the length of a ORIGIN value when represented in bytes."""
    return lenUVARI(v)

class PascalLikeBase(object):
    """Represents a variable length rep code that has a length and a payload
    with an optional padding number."""
#    CODE = 0
    def __init__(self, theLen, theBytes, thePad=0):
        self._len = theLen
        # Payload is a bytes, bytearray or string object
        self._payload = theBytes
        # Number of bits of padding
        self._pad = thePad
        self._checkValidChars()
        
    def __str__(self):
        return str(self.sigPayload)
        
    def write(self, theS):
        """Write me to a stream, oh write me to a stream.
        Sub-classes at least to think about how the represent self._len."""
        raise NotImplementedError('PascalLikeBase.write(): not implemented.')

    def _checkValidChars(self):
        """Can be implemented by child classes. Default is to do nothing."""
        pass
    
    def _nullValue(self):
        if isinstance(self._payload, str):
            return '\x00'
        elif isinstance(self._payload, bytes) or isinstance(self._payload, bytearray):
            return b'\x00'
        else:
            raise ExceptionRepCodePascalLikeBase('_nullValue(): unrecognised internal type {:s}'.format(type(self._payload)))
    
    @property
    def payload(self):
        if self._len > len(self._payload):
            return self._payload + self._nullValue() * (self._len - len(self._payload))
        return self._payload 

    @property
    def sigPayload(self):
        """Returns the significant bytes i.e. those preceding \x00."""
#        print('TRACE: sigPayload():', self._payload, type(self._payload), 'done')
        f = self._payload.find(self._nullValue())
        if f != -1:
            return self._payload[:f]
        return self._payload
    
    def __eq__(self, other):
#        print('TRACE: PascalLikeBase.__eq__():', self, other)
#        print('TRACE: PascalLikeBase.__eq__():', self.sigPayload, other.sigPayload)
        return self.sigPayload == other.sigPayload

    def __len__(self):
        raise NotImplementedError('PascalLikeBase.__len__(): not implemented.')
                
class IDENTBase(PascalLikeBase):
    """A variable-length character string consisting of N characters from a
    subset of the 7-bit ASCII character set, immediately preceded by the number
    N represented as a USHORT. The number N may be any value representable as a
    USHORT.
    The valid character subset consists of null (0) plus the codes 33 0x21 (!) to
    96 0x60 (`) and from 123 0x7b ({) to 126 0x7e (~) inclusive. This excludes all
    control characters, all "white space", and the lower-case alphabet.
    Two IDENT values match if and only if they have the same number of
    characters and the corresponding characters match.
    If a null character (0) is present, then only those characters that precede
    the first null are considered to be part of the actual string value."""
    CODE = 19
    
    def _checkValidChars(self):
        for i, b in enumerate(self._payload):
#            o = ord(c)
            if b == 0:
                break
            if b < 33 \
            or (b > 96 and b < 123) \
            or b > 126:
#                logging.warning('Illegal character ord: {:d} in position {:d}'.format(b, i))
                raise ExceptionRepCodeIDENT('Illegal character ord: {:d} in position {:d}'.format(b, i))
    
    def write(self, theS):
        # Single byte for length
        theS.write(bytes((self._len & 0xFF,)))
        theS.write(self._payload[:0xFF])
    
    def __len__(self):
        return 1 + len(self._payload)
    
class IDENTString(IDENTBase):
    def __init__(self, theStr):
        super().__init__(len(theStr), theStr)
        
class IDENTStream(IDENTBase):
    def __init__(self, theStream):
        l = theStream.read(1)[0]
        b = theStream.read(l)
        super().__init__(l, b)

def readIDENT(theS):
    return IDENTStream(theS)

def writeIDENT(v, theS):
    v.write(theS)
        
class ASCIIBase(PascalLikeBase):
    """A variable-length character string consisting of N characters from the
    7-bit ASCII (ANSI X3.4) or the ISO 8859-1 character sets, preceded by the
    number N represented as a UVARI. The number N may be any value representable
    as a UVARI. If a null character (0) is present, then only those characters
    that precede the first null are considered to be part of the actual string
    value."""
    ASCII_CHARS = set(string.ascii_letters + string.digits + string.punctuation + string.whitespace)
    CODE = 19
    
    def _checkValidChars(self):
#        print(self._payload, self.ASCII_CHARS)
        for i, c in enumerate(self._payload):
            if isinstance(c, int):
                c = chr(c)
            if c not in self.ASCII_CHARS:
#                print(c, type(c))
                raise ExceptionRepCodeASCII('Illegal character ord: {:c} in position {:d}'.format(c, i))
    
    def write(self, theS):
        # Single byte for length
        theS.write(bytes((self._len & 0xFF,)))
        theS.write(bytes(self._payload[:0xFF], 'ascii'))

    def __len__(self):
        return lenUVARI(self._len) + len(self._payload)
    
class ASCIIString(ASCIIBase):
    def __init__(self, theStr):
        super().__init__(len(theStr), theStr)
        
class ASCIIStream(ASCIIBase):
    def __init__(self, theStream):
        l = readUVARI(theStream)
        b = theStream.read(l)
#        print('ASCIIStream.__init__():', 'b:', b, 'b.decode():', b.decode())
        super().__init__(l, b)

def readASCII(theS):
    return ASCIIStream(theS)

def writeASCII(v, theS):
    v.write(theS)
        
class UNITSString(ASCIIString):
    CODE = 27
    """Identical to ASCII."""
    pass
        
class UNITSStream(ASCIIStream):
    CODE = 27
    """Identical to ASCII."""
    pass

def readUNITS(theS):
    return UNITSStream(theS)

def writeUNITS(v, theS):
    v.write(theS)
        
class BINARYBase(PascalLikeBase):
    """A variable-length bit string. The bits are written in N - 1 bytes
(when N > 1), starting at bit 8 of the first byte. The last byte contains
P < 8 trailing pad bits that are not part of the bit string. The number of
pad bits, P, is recorded immediately preceding the first bit string byte.
The total number of bytes N used to record P and the bit string is recorded
immediately preceding P. The value N = 0 corresponds to the null bit string
(no bits), in which case the byte containing P is omitted. The value N = 1 is
invalid, since it would represent an alternate null value. The total number of
bits in the bit string is:

#bits = 8 * (N - 1) - P, when N > 1.

Since P < 8, a bit string is written in the minimum number of bytes."""
    CODE = 40
    
    # TODO: implement write()
    
    @property
    def bits(self):
        """An integer representing the valid bits i.e. padding is removed."""
        r = 0
        for b in self._payload:
            r <<= 8
            r |= b
        # Remove padding
        r >>= self._pad
        return r

    def __len__(self):
        return lenUVARI(self._len) + len(self._payload)
    
class BINARYString(BINARYBase):
    def __init__(self, theStr):
        """Constructor from a bytes, it is assumed that this is already padded."""
        super().__init__(len(theStr), theStr)
        
class BINARYStream(BINARYBase):
    def __init__(self, theStream):
        """Constructor from a stream."""
        l = readUVARI(theStream)
        p = theStream.read(1)
        if p >= 8:
            raise ExceptionRepCodeBINARY('BINARY padding {:d} >= 8'.format(p))
        b = theStream.read(l)
        super().__init__(l, b, p)

def readBINARY(theS):
    return BINARYStream(theS)

def writeBINARY(v, theS):
    v.write(theS)

#===============================================
# End: Variable length representation codes.
#===============================================

############################
# End: Simple Rep Codes.
############################

#########################################
# Section: Compound Representation Codes.
#########################################
class CompoundBase(object):
    
    def write(self, theStream):
        """Writes the object to the stream."""
        raise NotImplementedError('CompoundBase.write(): Not implemented.')
        
    def read(self, theStream):
        """Reads the internals of this object from the stream."""
        raise NotImplementedError('CompoundBase.read(): Not implemented.')

class ATTREFBase(CompoundBase):
    """A value acts as a reference to an attribute in an object of the given
    object type. The object need not be present in the same logical file.
    However, the ORIGIN objects referenced by the tag and origin subfields must
    be present."""
    CODE = 25
    NAME = 'ATTREF'
    type = None
    origin = None
    copy = None
    identifier = None
    label = None
    
    def write(self, theStream):
        writeIDENT(self.type, theStream)
        writeORIGIN(self.origin, theStream)
        writeUVARI(self.copy, theStream)
        writeIDENT(self.identifier, theStream)
        writeIDENT(self.label, theStream)
        
    def read(self, theStream):
        self.type = IDENTStream(theStream)
        self.origin = readORIGIN(theStream)
        self.copy = readUVARI(theStream)
        self.identifier = IDENTStream(theStream)
        self.label = IDENTStream(theStream)
    
    def __len__(self):
        return len(self.type) + len(self.origin) + lenUVARI(self.copy) + len(self.identifier) + len(self.label)
    
class ATTREFInternal(ATTREFBase):
    def __init__(self, theType, theOrigin, theCopy, theId, theLabel):
        """Constructor from internal data."""
        super().__init__()
        self.type = theType
        self.origin = theOrigin
        self.copy = theCopy
        self.identifier = theId
        self.label = theLabel
        
class ATTREFStream(ATTREFBase):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readATTREF(theS):
    return ATTREFStream(theS)

def writeATTREF(v, theS):
    v.write(theS)

class FSING1Base(CompoundBase):
    """This is the representation of a balanced interval having its midpoint as
    a nominal single precision value. The assignment of meaning to the interval
    is delegated to the producer."""
    CODE = 3
    NAME = 'FSING1'
    # FSINGL, Nominal value V of interval [V - B, V + B].
    value = None
    # FSINGL, Interval bound, B (>= 0).
    bound = None
    STRUCT_RC_FSINGL1 = struct.Struct('>ff')
    
    def write(self, theStream):
#        print('TRACE: FSING1Base.write():', self.value, self.bound)
        theStream.write(self.STRUCT_RC_FSINGL1.pack(self.value, self.bound))
        
    def read(self, theStream):
        self.value, self.bound = self.STRUCT_RC_FSINGL1.unpack(theStream.read(self.STRUCT_RC_FSINGL1.size))
    
    def __eq__(self, other):
        return self.value == other.value and self.bound == other.bound
    
    def __len__(self):
        return self.STRUCT_RC_FSINGL1.size
    
class FSING1Internal(FSING1Base):
    def __init__(self, theValue, theBound):
        """Constructor from internal data."""
        super().__init__()
        self.value = theValue
        self.bound = theBound
        
class FSING1Stream(FSING1Base):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readFSING1(theS):
    return FSING1Stream(theS)

def writeFSING1(v, theS):
    v.write(theS)

class FSING2Base(CompoundBase):
    """This is the representation of a balanced interval having its midpoint as
    a nominal single precision value. The assignment of meaning to the interval
    is delegated to the producer."""
    CODE = 4
    NAME = 'FSING2'
    # FSINGL, Nominal value V of interval [V - A, V + B].
    value = None
    # FSINGL, Interval lower bound, A (>= 0)).
    lower = None
    # FSINGL, Interval upper bound, B (>= 0).
    upper = None
    STRUCT_RC_FSINGL2 = struct.Struct('>fff')
    
    def write(self, theStream):
        theStream.write(self.STRUCT_RC_FSINGL2.pack(self.value, self.lower, self.upper))
        
    def read(self, theStream):
        self.value, self.lower, self.upper = self.STRUCT_RC_FSINGL2.unpack(theStream.read(self.STRUCT_RC_FSINGL2.size))
    
    def __eq__(self, other):
        return self.value == other.value \
            and self.lower == other.lower \
            and self.upper == other.upper

    def __len__(self):
        return self.STRUCT_RC_FSINGL2.size
    
class FSING2Internal(FSING2Base):
    def __init__(self, theValue, theLower, theUpper):
        """Constructor from internal data."""
        super().__init__()
        self.value = theValue
        self.lower = theLower
        self.upper = theUpper
        
class FSING2Stream(FSING2Base):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readFSING2(theS):
    return FSING2Stream(theS)

def writeFSING2(v, theS):
    v.write(theS)

class FDOUB1Base(CompoundBase):
    """This is the representation of a balanced interval having its midpoint as
    a nominal double precision value. The assignment of meaning to the interval
    is delegated to the producer."""
    CODE = 8
    NAME = 'FDOUB1'
    # FDOUBL, Nominal value V of interval [V - B, V + B].
    value = None
    # FDOUBL, Interval bound, B (>= 0).
    bound = None
    STRUCT_RC_FDOUBL1 = struct.Struct('>dd')
    
    def write(self, theStream):
        theStream.write(self.STRUCT_RC_FDOUBL1.pack(self.value, self.bound))
        
    def read(self, theStream):
        self.value, self.bound = self.STRUCT_RC_FDOUBL1.unpack(theStream.read(self.STRUCT_RC_FDOUBL1.size))
    
    def __eq__(self, other):
        return self.value == other.value and self.bound == other.bound
    
    def __len__(self):
        return self.STRUCT_RC_FDOUBL1.size
    
class FDOUB1Internal(FDOUB1Base):
    def __init__(self, theValue, theBound):
        """Constructor from internal data."""
        super().__init__()
        self.value = theValue
        self.bound = theBound
        
class FDOUB1Stream(FDOUB1Base):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readFDOUB1(theS):
    return FDOUB1Stream(theS)

def writeFDOUB1(v, theS):
    v.write(theS)

class FDOUB2Base(CompoundBase):
    """This is the representation of a balanced interval having its midpoint as
    a nominal double precision value. The assignment of meaning to the interval
    is delegated to the producer."""
    CODE = 9
    NAME = 'FDOUB2'
    # FDOUBL, Nominal value V of interval [V - A, V + B].
    value = None
    # FDOUBL, Interval lower bound, A (>= 0)).
    lower = None
    # FDOUBL, Interval upper bound, B (>= 0).
    upper = None
    STRUCT_RC_FDOUBL2 = struct.Struct('>ddd')
    
    def write(self, theStream):
        theStream.write(self.STRUCT_RC_FDOUBL2.pack(self.value, self.lower, self.upper))
        
    def read(self, theStream):
        self.value, self.lower, self.upper = self.STRUCT_RC_FDOUBL2.unpack(theStream.read(self.STRUCT_RC_FDOUBL2.size))
    
    def __eq__(self, other):
        return self.value == other.value \
            and self.lower == other.lower \
            and self.upper == other.upper

    def __len__(self):
        return self.STRUCT_RC_FDOUBL2.size
    
class FDOUB2Internal(FDOUB2Base):
    def __init__(self, theValue, theLower, theUpper):
        """Constructor from internal data."""
        super().__init__()
        self.value = theValue
        self.lower = theLower
        self.upper = theUpper
        
class FDOUB2Stream(FDOUB2Base):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readFDOUB2(theS):
    return FDOUB2Stream(theS)

def writeFDOUB2(v, theS):
    v.write(theS)

class CSINGLBase(CompoundBase):
    """This is the representation of a balanced interval having its midpoint as
    a nominal single precision value. The assignment of meaning to the interval
    is delegated to the producer."""
    CODE = 10
    NAME = 'CSINGL'
    # A complex() builtin that has real, imag properties
    value = None
    STRUCT_RC_CSINGL = struct.Struct('>ff')
    
    def write(self, theStream):
        theStream.write(self.STRUCT_RC_CSINGL.pack(self.value.real, self.value.imag))
        
    def read(self, theStream):
        self.value = complex(self.STRUCT_RC_CSINGL.unpack(theStream.read(self.STRUCT_RC_CSINGL.size)))
    
    def __len__(self):
        return self.STRUCT_RC_CSINGL.size
    
class CSINGLInternal(CSINGLBase):
    def __init__(self, theValue):
        """Constructor from and internal complex() type."""
        super().__init__()
        self.value = theValue
        
class CSINGLStream(CSINGLBase):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readCSINGL(theS):
    return CSINGLStream(theS)

def writeCSINGL(v, theS):
    v.write(theS)

class CDOUBLBase(CompoundBase):
    """This is the representation of a balanced interval having its midpoint as
    a nominal single precision value. The assignment of meaning to the interval
    is delegated to the producer."""
    CODE = 11
    NAME = 'CDOUBL'
    # A complex() builtin that has properties: real, imag
    value = None
    STRUCT_RC_CDOUBL = struct.Struct('>dd')
    
    def write(self, theStream):
        theStream.write(self.STRUCT_RC_CDOUBL.pack(self.value.real, self.value.imag))
        
    def read(self, theStream):
        self.value = complex(self.STRUCT_RC_CDOUBL.unpack(theStream.read(self.STRUCT_RC_CDOUBL.size)))
    
    def __len__(self):
        return self.STRUCT_RC_CDOUBL.size
    
class CDOUBLInternal(CDOUBLBase):
    def __init__(self, theValue):
        """Constructor from and internal complex() type."""
        super().__init__()
        self.value = theValue
        
class CDOUBLStream(CDOUBLBase):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readCDOUBL(theS):
    return CDOUBLStream(theS)

def writeCDOUBL(v, theS):
    v.write(theS)

class DTIMEBase(object):
    """Represents date and time.
Fields are:
1    year    USHORT    Years since 1900.
2    timezone    4-bit unsigned integer    Time zone: 0=local standard time, 1=local daylight savings time, 2 = Universal Coordinated Time (Greenwich Mean Time).
3    month    4-bit unsigned integer    Month of the year (1 to 12).
4    day    USHORT    Day of the month (1 to 31).
5    hour    USHORT    Hours since midnight (0 to 3 (sic. assume 23)).
6    minute    USHORT    Minutes past the hour (0 to 59).
7    second    USHORT    Seconds past the minute (0 to 59).
8    millisecond    UNORM    Milliseconds past the second (0 to 999).

Internally this is represented as a struct_time object plus integer milliseconds and timezone.
"""
    CODE = 21
    NAME = 'DTIME'
    # A datetime.datetime object
    _time = None
    # 0 = local standard time, 1 = local daylight savings time, 2 = Universal Coordinated Time (Greenwich Mean Time).
    _tzone = None
    # B is USHORT, H is UNORM
    STRUCT_RC_DTIME = struct.Struct('>BBBBBBH')
    # RP66 uses an epoch of 1900, sigh.
    YEAR_OFFSET = 1900
    
    def __len__(self):
        return self.STRUCT_RC_DTIME.size
    
    def write(self, theStream):
        tz_m = (self._tzone & 0xF)
        tz_m <<= 4
        tz_m |= self._time.month & 0xF
#        print('TRACE: _time', self._time)
#        print(dir(self._time))
        theStream.write(self.STRUCT_RC_DTIME.pack(
                (self._time.year - self.YEAR_OFFSET) & 0xFF, # Year as USHORT
                tz_m, # Suitably munged
                self._time.day & 0xFF,
                self._time.hour & 0xFF,
                self._time.minute & 0xFF,
                self._time.second & 0xFF,
                # NOTE: Truncate use otherwise 999500 could be 1000 ms and this has to be 0 to 999
                int(self._time.microsecond / 1000.0) & 0xFFFF,
            )
        )
        
    def read(self, theStream):
        y, tz_m, d, h, min, s, ms = self.STRUCT_RC_DTIME.unpack(theStream.read(self.STRUCT_RC_DTIME.size))
        # Now fix various fields
        y += self.YEAR_OFFSET
        mon = tz_m & 0xF
        self._tzone = (tz_m >> 4)
#        print('TRACE: ms', ms)
        self._time = datetime.datetime(y, mon, d, h, min, s, ms*1000)
        
    def mktime(self):
        """Returns time in seconds since the epoch, this uses the time module
        that is based on the C library."""
#        print('TRACE: self._time', str(self._time))
        ts = time.struct_time(
            (
                self._time.year,
                self._time.month,
                self._time.day,
                self._time.hour,
                self._time.minute,
                self._time.second,
                0,
                0,
                0,
            ),
        )
        secs = time.mktime(ts)
        secs += self._time.microsecond / 1000000.0
        return secs

class DTIMEInternal(DTIMEBase):
    def __init__(self, theDateTime, theTimeZone=0):
        """Constructor from a datetime.datetime object and an integer representing
        the time zone, 0 = local standard time, 1 = local daylight savings time,
        2 = Universal Coordinated Time (Greenwich Mean Time)."""
        super().__init__()
        self._time = theDateTime
#        print('TRACE: self._time', self._time)
        self._tzone = theTimeZone
        
class DTIMEStream(DTIMEBase):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readDTIME(theS):
    return DTIMEStream(theS)

def writeDTIME(v, theS):
    v.write(theS)

class OBNAMEBase(CompoundBase):
    """A value acts as a reference to an object. The object need not be present
    in the same logical file. However, the ORIGIN object referenced by the
    origin subfield must be present."""
    CODE = 23
    NAME = 'OBNAME'
    origin = None
    copy = None
    identifier = None
    
    def write(self, theStream):
        writeORIGIN(self.origin, theStream)
        writeUVARI(self.copy, theStream)
        writeIDENT(self.identifier, theStream)
        
    def read(self, theStream):
        self.origin = readORIGIN(theStream)
        self.copy = readUVARI(theStream)
        self.identifier = IDENTStream(theStream)
    
    def __len__(self):
        return lenORIGIN(self.origin) + lenUVARI(self.copy) + len(self.identifier)
    
class OBNAMEInternal(OBNAMEBase):
    def __init__(self, theType, theOrigin, theCopy, theId, theLabel):
        """Constructor from internal data."""
        super().__init__()
        self.origin = theOrigin
        self.copy = theCopy
        self.identifier = theId
        
class OBNAMEStream(OBNAMEBase):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readOBNAME(theS):
    return OBNAMEStream(theS)

def writeOBNAME(v, theS):
    v.write(theS)

class OBJREFBase(CompoundBase):
    """"A value acts as a reference to an object having a given type.
    The object need not be present in the same logical file. However, the
    ORIGIN objects referenced by the origin subfield must be present."""
    CODE = 24
    NAME = 'OBJREF'
    type = None
    origin = None
    copy = None
    identifier = None
    
    def write(self, theStream):
        writeIDENT(self.type, theStream)
        writeORIGIN(self.origin, theStream)
        writeUVARI(self.copy, theStream)
        writeIDENT(self.identifier, theStream)
        
    def read(self, theStream):
        self.type = IDENTStream(theStream)
        self.origin = readORIGIN(theStream)
        self.copy = readUVARI(theStream)
        self.identifier = IDENTStream(theStream)
    
    def __len__(self):
        return len(self.type) + len(self.origin) + lenUVARI(self.copy) + len(self.identifier)
    
class OBJREFInternal(OBJREFBase):
    def __init__(self, theType, theOrigin, theCopy, theId, theLabel):
        """Constructor from internal data."""
        super().__init__()
        self.type = theType
        self.origin = theOrigin
        self.copy = theCopy
        self.identifier = theId
        
class OBJREFStream(OBJREFBase):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readOBJREF(theS):
    return OBJREFStream(theS)

def writeOBJREF(v, theS):
    v.write(theS)

# Rational number representations
class RNORMBase(CompoundBase):
    """This is the representation of a rational number, represented by normal
    precision numerator and denominator."""
    CODE = 28
    NAME = 'RNORM'
    # Numerator of ratio.
    # SNORM i.e. signed two byte integer
    numerator = None
    # Denominator of ratio (> 0).
    # UNORM i.e. unsigned two byte integer
    denominator = None
    # TODO: Refactor this to use struct as above rather than two calls to read/write?
    
    def __len__(self):
        return 4
    
    def write(self, theStream):
        writeSNORM(self.numerator, theStream)
        writeUNORM(self.denominator, theStream)
        
    def read(self, theStream):
        self.numerator = readSNORM(theStream)
        self.denominator = readUNORM(theStream)
    
class RNORMInternal(RNORMBase):
    def __init__(self, theNum, theDenom):
        """Constructor from internal data."""
        super().__init__()
        self.numerator = theNum
        self.denominator = theDenom
        
class RNORMStream(RNORMBase):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readRNORM(theS):
    return RNORMStream(theS)

def writeRNORM(v, theS):
    v.write(theS)

class RLONGBase(CompoundBase):
    """This is the representation of a rational number, represented by long
    precision numerator and denominator."""
    CODE = 29
    NAME = 'RLONG'
    # Numerator of ratio.
    # SLONG i.e. signed four byte integer
    numerator = None
    # Denominator of ratio (> 0).
    # ULONG i.e. unsigned four byte integer
    denominator = None
    
    def __len__(self):
        return 8
    
    def write(self, theStream):
        writeSLONG(self.numerator, theStream)
        writeULONG(self.denominator, theStream)
        
    def read(self, theStream):
        self.numerator = readSLONG(theStream)
        self.denominator = readULONG(theStream)
    
class RLONGInternal(RLONGBase):
    def __init__(self, theNum, theDenom):
        """Constructor from internal data."""
        super().__init__()
        self.numerator = theNum
        self.denominator = theDenom
        
class RLONGStream(RLONGBase):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readRLONG(theS):
    return RLONGStream(theS)

def writeRLONG(v, theS):
    v.write(theS)

class IRNORMBase(CompoundBase):
    """This is the representation of a rational number, represented by normal
    precision numerator and denominator, in inverted byte order."""
    CODE = 34
    NAME = 'IRNORM'
    # Numerator of ratio.
    # ISNORM i.e. signed two byte integer in inverted order
    numerator = None
    # Denominator of ratio (> 0).
    # IUNORM i.e. unsigned two byte integer in inverted order
    denominator = None
    
    def __len__(self):
        return 4
    
    def write(self, theStream):
        writeISNORM(self.numerator, theStream)
        writeIUNORM(self.denominator, theStream)
        
    def read(self, theStream):
        self.numerator = readISNORM(theStream)
        self.denominator = readIUNORM(theStream)
    
class IRNORMInternal(IRNORMBase):
    def __init__(self, theNum, theDenom):
        """Constructor from internal data."""
        super().__init__()
        self.numerator = theNum
        self.denominator = theDenom
        
class IRNORMStream(IRNORMBase):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readIRNORM(theS):
    return IRNORMStream(theS)

def writeIRNORM(v, theS):
    v.write(theS)

class IRLONGBase(CompoundBase):
    """This is the representation of a rational number, represented by long
    precision numerator and denominator, in inverted byte order."""
    CODE = 35
    NAME = 'IRLONG'
    # Numerator of ratio.
    # SLONG i.e. signed four byte integer
    numerator = None
    # Denominator of ratio (> 0).
    # ULONG i.e. unsigned four byte integer
    denominator = None
    
    def __len__(self):
        return 8
    
    def write(self, theStream):
        writeISLONG(self.numerator, theStream)
        writeIULONG(self.denominator, theStream)
        
    def read(self, theStream):
        self.numerator = readISLONG(theStream)
        self.denominator = readIULONG(theStream)
    
class IRLONGInternal(IRLONGBase):
    def __init__(self, theNum, theDenom):
        """Constructor from internal data."""
        super().__init__()
        self.numerator = theNum
        self.denominator = theDenom
        
class IRLONGStream(IRLONGBase):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readIRLONG(theS):
    return IRLONGStream(theS)

def writeIRLONG(v, theS):
    v.write(theS)

# TODO: Merge these 'T' classes to use some common base class?

class TIDENTBase(CompoundBase):
    """The tag subfield references an ORIGIN object in the same logical file.
    The use of this ORIGIN may differ from value to value and must be specified
    when the entity (e.g., object type, attribute, etc.) is defined."""
    CODE = 36
    NAME = 'TIDENT'
    # ORIGIN i.e. UVARI
    tag = None
    # IDENT
    identifier = None
    
    def __len__(self):
        return lenORIGIN(self.tag) + len(self.identifier)
    
    def write(self, theStream):
        writeORIGIN(self.tag, theStream)
        writeIDENT(self.identifier, theStream)
        
    def read(self, theStream):
        self.tag = readORIGIN(theStream)
        self.identifier = readIDENT(theStream)
    
class TIDENTInternal(TIDENTBase):
    def __init__(self, theTag, theIdentifier):
        """Constructor from internal data."""
        super().__init__()
        self.tag = theTag
        self.identifier = theIdentifier
        
class TIDENTStream(TIDENTBase):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readTIDENT(theS):
    return TIDENTStream(theS)

def writeTIDENT(v, theS):
    v.write(theS)

class TUNORMBase(CompoundBase):
    """The tag     subfield references an ORIGIN object in the same logical file.
    The use of this ORIGIN may differ from value to value and must be specified
    when the entity is defined."""
    CODE = 37
    NAME = 'TUNORM'
    # ORIGIN i.e. UVARI
    tag = None
    # UNORM
    value = None
    
    def __len__(self):
        return lenORIGIN(self.tag) + 2
    
    def write(self, theStream):
        writeORIGIN(self.tag, theStream)
        writeUNORM(self.value, theStream)
        
    def read(self, theStream):
        self.tag = readORIGIN(theStream)
        self.value = readUNORM(theStream)
    
class TUNORMInternal(TUNORMBase):
    def __init__(self, theTag, theValue):
        """Constructor from internal data."""
        super().__init__()
        self.tag = theTag
        self.value = theValue
        
class TUNORMStream(TUNORMBase):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readTUNORM(theS):
    return TUNORMStream(theS)

def writeTUNORM(v, theS):
    v.write(theS)

class TASCIIBase(CompoundBase):
    """The tag subfield references an ORIGIN object in the same logical file.
    The use of this ORIGIN may differ from value to value and must be specified
    when the entity is defined."""
    CODE = 38
    NAME = 'TASCII'
    # ORIGIN i.e. UVARI
    tag = None
    # ASCII
    string = None
    
    def __len__(self):
        return lenORIGIN(self.tag) + len(self.identifier)
    
    def write(self, theStream):
        writeORIGIN(self.tag, theStream)
        writeASCII(self.string, theStream)
        
    def read(self, theStream):
        self.tag = readORIGIN(theStream)
        self.string = readASCII(theStream)
    
class TASCIIInternal(TASCIIBase):
    def __init__(self, theTag, theValue):
        """Constructor from internal data."""
        super().__init__()
        self.tag = theTag
        self.value = theValue
        
class TASCIIStream(TASCIIBase):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readTASCII(theS):
    return TASCIIStream(theS)

def writeTASCII(v, theS):
    v.write(theS)

class FRATIOBase(CompoundBase):
    """This is the representation of a ratio, represented by its single
    precision numerator and denominator."""
    # TODO: Read/write with own struct e.g. '>ff' ???
    CODE = 41
    NAME = 'FRATIO'
    # Numerator of ratio.
    # FSINGL
    numerator = None
    # Denominator of ratio (> 0).
    # FSINGL
    denominator = None
    
    def __len__(self):
        return 8
    
    def write(self, theStream):
        writeFSINGL(self.numerator, theStream)
        writeFSINGL(self.denominator, theStream)
        
    def read(self, theStream):
        self.numerator = readFSINGL(theStream)
        self.denominator = readFSINGL(theStream)
    
class FRATIOInternal(FRATIOBase):
    def __init__(self, theNum, theDenom):
        """Constructor from internal data."""
        super().__init__()
        self.numerator = theNum
        self.denominator = theDenom
        
class FRATIOStream(FRATIOBase):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readFRATIO(theS):
    return FRATIOStream(theS)

def writeFRATIO(v, theS):
    v.write(theS)

class DRATIOBase(CompoundBase):
    """This is the representation of a ratio, represented by its double
    precision numerator and denominator."""
    CODE = 42
    NAME = 'DRATIO'
    # Numerator of ratio.
    # FDOUBL
    numerator = None
    # Denominator of ratio (> 0).
    # FDOUBL
    denominator = None
    
    def __len__(self):
        return 16
    
    def write(self, theStream):
        writeFDOUBL(self.type, theStream)
        writeFDOUBL(self.origin, theStream)
        
    def read(self, theStream):
        self.numerator = readFDOUBL(theStream)
        self.denominator = readFDOUBL(theStream)
    
class DRATIOInternal(DRATIOBase):
    def __init__(self, theNum, theDenom):
        """Constructor from internal data."""
        super().__init__()
        self.numerator = theNum
        self.denominator = theDenom
        
class DRATIOStream(DRATIOBase):
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.read(theStream)

def readDRATIO(theS):
    return DRATIOStream(theS)

def writeDRATIO(v, theS):
    v.write(theS)


## Fields (note names come from the standard):
## Name - attribute name as a string.
## Code - ASCII uppercase name.
## Description - A string.
#CompStruct = collections.namedtuple('CompStruct', 'Name Code Description')
#
#COMPOUND_TABLE = {
#    'ATTREF' :  (
#        'A value acts as a reference to an attribute in an object of the given object type. The object need not be present in the same logical file. However, the ORIGIN objects referenced by the tag and origin subfields must be present.',
#        (
#            CompStruct('type',          'IDENT',    'Object type name.'),
#            CompStruct('origin',        'ORIGIN',   'Origin containing schema code and identifier namespace code.'),
#            CompStruct('copy',          'UVARI',    'Copy number.'),
#            CompStruct('identifier',    'IDENT',    'Object identifier.'),
#            CompStruct('label',         'IDENT',    'Attribute label.'),
#        ),
#     ),
#    'CDOUBL' : (
#        'This is the representation of a complex number, represented by its double precision real and imaginary parts.',
#        (
#            CompStruct('real',          'FDOUBL', 'Real part.'),
#            CompStruct('imaginary',     'FDOUBL', 'Imaginary part.'),
#        ),
#    ),
#    'CSINGL' : (
#        'This is the representation of a complex number, represented by its single precision real and imaginary parts.',
#        (
#            CompStruct('real',          'FSINGL', 'Real part.'),
#            CompStruct('imaginary',     'FSINGL', 'Imaginary part.'),
#        ),
#    ),
#    'DRATIO' : (
#        'This is the representation of a ratio, represented by its double precision numerator and denominator.',
#        (
#            CompStruct('numerator',     'FDOUBL', 'Numerator of ratio.'),
#            CompStruct('denominator',   'FDOUBL', 'Denominator of ratio (> 0).'),
#        ),
#    ),
#}

#####################################
# End: Compound Representation Codes.
#####################################

###########################################
# Section: Dynamic despatch table creation.
###########################################
#import pprint
#pprint.pprint(globals())
#print(__name__)
#assert(callable(locals()['readLOGICL']))
#getattr(__name__, 'readLOGICL')

# A tuple of functions that can read a rep code, ordinal is rep code integer code.
# Function takes a single argument a readable stream and returns a rep code value.
RC_INDIRECT_READ = tuple(
    [globals()['read'+o.SymbolicName] if o is not None else None for o in RC_TABLE]
)
# A tuple of functions that can write a rep code, ordinal is rep code integer code.
# Function takes a two arguments a rep code value and a readable stream.
RC_INDIRECT_WRITE = tuple(
    [globals()['write'+o.SymbolicName] if o is not None else None for o in RC_TABLE]
)

def _checkRepCodeInRange(c):
    """Given an integer code this may raise and ExceptionRepCodeCodeNumberOutOfRange if c out of range."""
    if c < 1 or c >= LEN_RC_TABLE:
        raise ExceptionRepCodeCodeNumberOutOfRange('Code number {:d} out of range 0 < c < {:d}'.format(c, LEN_RC_TABLE))

def readIndirectRepCode(c, theS):
    """Given an integer code this reads a single instance of that code off the
    stream if a struct exists for it.
    May raise and ExceptionRepCodeCodeNumberOutOfRange if c out of range."""
    _checkRepCodeInRange(c)
    f = RC_INDIRECT_READ[c]
    assert(f is not None)
    return f(theS)
        
def writeIndirectRepCode(c, v, theS):
    """Given an integer code this writes the value, v, to the
    stream if a struct exists for it.
    May raise and ExceptionRepCodeCodeNumberOutOfRange if c out of range."""
    _checkRepCodeInRange(c)
    f = RC_INDIRECT_WRITE[c]
    assert(f is not None)
    return f(v, theS)

#######################################
# End: Dynamic despatch table creation.
#######################################

