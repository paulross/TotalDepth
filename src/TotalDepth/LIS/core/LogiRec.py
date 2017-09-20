#!/usr/bin/env python
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 1999-2011 Paul Ross
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
"""Handles LIS Logical Records.


"""



__author__  = 'Paul Ross'
__date__    = '29 Dec 2010'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'

import struct
import logging
import collections

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import Units
from TotalDepth.LIS.core import EngVal
from TotalDepth.LIS.core import RepCode
from TotalDepth.LIS.core import Mnem
from TotalDepth.LIS.core.File import ExceptionFileRead

class ExceptionLr(ExceptionTotalDepthLIS):
    """Specialisation of exception for Logical Records."""
    pass

class ExceptionLrNotImplemented(ExceptionLr):
    """Logical Records that have no implementation here."""
    pass

class ExceptionCbWrite(ExceptionLr):
    """Raised when creating a component block with Python native types that has illogical or conflicting data."""
    pass

# Logical Record Header Information
# =================================
LR_HEADER_LENGTH = 2
#
# Logical Record Types
# ====================
#
# Group 0 - Data records
# ----------------------
LR_TYPE_NORMAL_DATA             = 0    #: Normal data record containing log data
LR_TYPE_ALTERNATE_DATA          = 1    #: Alternate data.
#
# Group 1 Information records
# ---------------------------
LR_TYPE_JOB_ID                  = 32    #: Job identification
LR_TYPE_WELL_DATA               = 34    #: Well site data
LR_TYPE_TOOL_INFO               = 39    #: Tool string info
LR_TYPE_ENCRYPTED_TABLE         = 42    #: Encrypted table dump
LR_TYPE_TABLE_DUMP              = 47    #: Table dump
#
# Group 2 Data format specification records
# -----------------------------------------
LR_TYPE_DATA_FORMAT             = 64    #: Data format specification record
LR_TYPE_DATA_DESCRIPTOR         = 65    #: Data descriptor (not defined in the LIS79 Description Reference Manual)
#
# Group 3 Program records (CSU only)
# ----------------------------------
LR_TYPE_TU10_BOOT               = 95    #: TU10 software boot
LR_TYPE_BOOTSTRAP_LOADER        = 96    #: Bootstrap loader
LR_TYPE_CP_KERNEL               = 97    #: CP-kernel loader boot
LR_TYPE_PROGRAM_FILE_HEAD       = 100    #: Program file header
LR_TYPE_PROGRAM_OVER_HEAD       = 101    #: Program overlay header
LR_TYPE_PROGRAM_OVER_LOAD       = 102    #: Program overlay load
#
# Group 4 Delimiters
# ------------------
LR_TYPE_FILE_HEAD               = 128    #: File header
LR_TYPE_FILE_TAIL               = 129    #: File trailer
LR_TYPE_TAPE_HEAD               = 130    #: Tape header
LR_TYPE_TAPE_TAIL               = 131    #: Tape trailer
LR_TYPE_REEL_HEAD               = 132    #: Reel header
LR_TYPE_REEL_TAIL               = 133    #: Reel trailer
LR_TYPE_EOF                     = 137    #: Logical EOF (end of file)
LR_TYPE_BOT                     = 138    #: Logical BOT (beginning of tape)
LR_TYPE_EOT                     = 139    #: Logical EOT (end of tape)
LR_TYPE_EOM                     = 141    #: Logical EOM (end of medium)
#
# Group 7 Miscellaneous records
# -----------------------------
LR_TYPE_OPERATOR_INPUT          = 224    #: Operator command inputs
LR_TYPE_OPERATOR_RESPONSE       = 225    #: Operator response inputs
LR_TYPE_SYSTEM_OUTPUT           = 227    #: System outputs to operator
LR_TYPE_FLIC_COMMENT            = 232    #: FLIC comment
LR_TYPE_BLANK_RECORD            = 234    #: Blank record/CSU comment
LR_TYPE_PICTURE                 = 85     #: Picture
LR_TYPE_IMAGE                   = 86     #: Image
#
# Collections
# -----------
#: All possible Logical Records Types
LR_TYPE_ALL = (
    LR_TYPE_NORMAL_DATA,
    LR_TYPE_ALTERNATE_DATA,
    LR_TYPE_JOB_ID,
    LR_TYPE_WELL_DATA,
    LR_TYPE_TOOL_INFO,
    LR_TYPE_ENCRYPTED_TABLE,
    LR_TYPE_TABLE_DUMP,
    LR_TYPE_DATA_FORMAT,
    LR_TYPE_DATA_DESCRIPTOR,
    LR_TYPE_TU10_BOOT,
    LR_TYPE_BOOTSTRAP_LOADER,
    LR_TYPE_CP_KERNEL,
    LR_TYPE_PROGRAM_FILE_HEAD,
    LR_TYPE_PROGRAM_OVER_HEAD,
    LR_TYPE_PROGRAM_OVER_LOAD,
    LR_TYPE_FILE_HEAD,
    LR_TYPE_FILE_TAIL,
    LR_TYPE_TAPE_HEAD,
    LR_TYPE_TAPE_TAIL,
    LR_TYPE_REEL_HEAD,
    LR_TYPE_REEL_TAIL,
    LR_TYPE_EOF,
    LR_TYPE_BOT,
    LR_TYPE_EOT,
    LR_TYPE_EOM,
    LR_TYPE_OPERATOR_INPUT,
    LR_TYPE_OPERATOR_RESPONSE,
    LR_TYPE_SYSTEM_OUTPUT,
    LR_TYPE_FLIC_COMMENT,
    LR_TYPE_BLANK_RECORD,
    LR_TYPE_PICTURE,
    LR_TYPE_IMAGE,
)
#: Logical Records Types for Log data
LR_TYPE_LOG_DATA = (LR_TYPE_NORMAL_DATA, LR_TYPE_ALTERNATE_DATA)
#: Logical Records Types for Table data
LR_TYPE_TABLE_DATA = (LR_TYPE_JOB_ID, LR_TYPE_WELL_DATA, LR_TYPE_TOOL_INFO)

#: Logical Records Types for delimiter start records.
LR_TYPE_DELIMITER_START = (LR_TYPE_REEL_HEAD, LR_TYPE_TAPE_HEAD, LR_TYPE_FILE_HEAD)
#: Logical Records Types for delimiter end records.
LR_TYPE_DELIMITER_END = (LR_TYPE_REEL_TAIL, LR_TYPE_TAPE_TAIL, LR_TYPE_FILE_TAIL)
#: Logical Records Types for all delimiter records.
#: Delimeter records 'bookend' dynamic and static data that makes up a LIS file.
LR_TYPE_DELIMITER = LR_TYPE_DELIMITER_START + LR_TYPE_DELIMITER_END
#: Logical Records Types for all marker records.
#: Marker records terminate original physical media such as a tape.
LR_TYPE_MARKER = (LR_TYPE_EOF, LR_TYPE_BOT, LR_TYPE_EOT, LR_TYPE_EOM)
#: Logical Records Types for all delimiter and marker records.
LR_TYPE_DELIMITER_MARKER = LR_TYPE_DELIMITER + LR_TYPE_MARKER

# Global function for detecting delimiter records
def isDelimiter(theType):
    """Returns True if the Logical Record Type is a Delimiter record."""
    return theType in LR_TYPE_DELIMITER

#: Logical Records Types with no known format so just treat these as unformatted binary data
LR_TYPE_UNKNOWN_INTERNAL_FORMAT = (
    LR_TYPE_ENCRYPTED_TABLE,
    LR_TYPE_TABLE_DUMP,
    LR_TYPE_TU10_BOOT,
    LR_TYPE_BOOTSTRAP_LOADER,
    LR_TYPE_CP_KERNEL,
    LR_TYPE_PROGRAM_FILE_HEAD,
    LR_TYPE_PROGRAM_OVER_HEAD,
    LR_TYPE_PROGRAM_OVER_LOAD,
    LR_TYPE_OPERATOR_INPUT,
    LR_TYPE_OPERATOR_RESPONSE,
    LR_TYPE_SYSTEM_OUTPUT,
    LR_TYPE_FLIC_COMMENT,
    LR_TYPE_BLANK_RECORD,
    LR_TYPE_PICTURE,
    LR_TYPE_IMAGE,
)

#: Map of {Logical Records Type : description, ...}
LR_DESCRIPTION_MAP = {
    # Group 0 - Data records
    0 : 'Normal data record containing log data',
    1 : 'Alternate data.',
    # Group 1 Information records
    32 : 'Job identification',
    34 : 'Well site data',
    39 : 'Tool string info',
    42 : 'Encrypted table dump',
    47 : 'Table dump',
    # Group 2 Data format specification records
    64 : 'Data format specification record',
    65 : 'Data descriptor (not defined in the LIS79 Description Reference Manual)',
    # Group 3 Program records (CSU only)
    95 : 'TU10 software boot',
    96 : 'Bootstrap loader',
    97 : 'CP-kernel loader boot',
    100 : 'Program file header',
    101 : 'Program overlay header',
    102 : 'Program overlay load',
    # Group 4 Delimiters
    128 : 'File header',
    129 : 'File trailer',
    130 : 'Tape header',
    131 : 'Tape trailer',
    132 : 'Reel header',
    133 : 'Reel trailer',
    137 : 'Logical EOF (end of file)',
    138 : 'Logical BOT (beginning of tape)',
    139 : 'Logical EOT (end of tape)',
    141 : 'Logical EOM (end of medium)',
    # Group 7 Miscellaneous records
    224 : 'Operator command inputs',
    225 : 'Operator response inputs',
    227 : 'System outputs to operator',
    232 : 'FLIC comment',
    234 : 'Blank record/CSU comment',
    85 : 'Picture',
    86 : 'Image',
}

#: Description string for unknown Logical Records Type
LR_DESCRIPTION_UNKNOWN = 'Unknown Logical Record type.'

#####################################################
# Section: Struct declarations for reading from file.
#####################################################
#: Logical Record header (type and attributes)
STRUCT_LR_HEAD = struct.Struct('BB')
# 2 bytes, 2 fields
assert(STRUCT_LR_HEAD.size == LR_HEADER_LENGTH)
assert(len(STRUCT_LR_HEAD.unpack(b' ' * STRUCT_LR_HEAD.size)) == 2)

#: Logical Record field interpretation via the struct module
STRUCT_LR_FILE_HEAD_TAIL = struct.Struct('10s2x6s8s8s1x5s2x2s2x10s')
# 56 bytes, 7 fields
assert(STRUCT_LR_FILE_HEAD_TAIL.size == 58 - LR_HEADER_LENGTH)
assert(len(STRUCT_LR_FILE_HEAD_TAIL.unpack(b' ' * STRUCT_LR_FILE_HEAD_TAIL.size)) == 7)

#: Logical Record reel/tape head/tail via the struct module
STRUCT_LR_REEL_TAPE_HEAD_TAIL = struct.Struct('6s6x8s2x4s2x8s2x2s2x8s2x74s')
# 128 bytes, 7 fields
assert(STRUCT_LR_REEL_TAPE_HEAD_TAIL.size == 128 - LR_HEADER_LENGTH), 'Size is {:d}'.format(STRUCT_LR_REEL_TAPE_HEAD_TAIL.size)
assert(len(STRUCT_LR_REEL_TAPE_HEAD_TAIL.unpack(b' ' * STRUCT_LR_REEL_TAPE_HEAD_TAIL.size)) == 7)

#: Component Block preamble as a struct.Struct()
STRUCT_COMPONENT_BLOCK_PREAMBLE = struct.Struct('4B4s4s')
# 12 bytes, 6 fields
assert(STRUCT_COMPONENT_BLOCK_PREAMBLE.size == 12)
assert(len(STRUCT_COMPONENT_BLOCK_PREAMBLE.unpack(b' ' * STRUCT_COMPONENT_BLOCK_PREAMBLE.size)) == 6)

#: Entry Block preamble as a struct.Struct()
STRUCT_ENTRY_BLOCK_PREAMBLE = struct.Struct('BBB')
# 3 bytes, 3 fields
assert(STRUCT_ENTRY_BLOCK_PREAMBLE.size == 3)
assert(len(STRUCT_ENTRY_BLOCK_PREAMBLE.unpack(b' ' * STRUCT_ENTRY_BLOCK_PREAMBLE.size)) == 3)

#: Datum Specification Block structure.
#: NOTE: Due to the funny way API codes are done we read then as a single
#: 32 bit unsigned integer and then do a decimal masking operation to
#: extract the four sub-fields
STRUCT_DSB = struct.Struct('>4s6s8s4sI2h3x2B5x')
# 40 bytes, 9 fields (17 fields if process indicator bytes are included)
assert(STRUCT_DSB.size == 40)
assert(len(STRUCT_DSB.unpack(b' ' * STRUCT_DSB.size)) == 9)

#####################################################
# End: Struct declarations for reading from file.
#####################################################

class LrBase(object):
    """Base class for Logical Records.
    Constructed with and integer type and integer attributes."""
    def __init__(self, theType, theAttr):
        """Base class constructor, theType and theAttr are bytes."""
        self.type = theType
        self.attr = theAttr
        
    def init(self, theLen):
        """Returns a string of spaces of the supplied length."""
        return b' ' * theLen
    
    def __str__(self):
        """String representation."""
        return '{:s}: "{:s}"'.format(repr(self), self.desc)
    
    @property
    def desc(self):
        """Description ot the LR type."""
        try:
            myType = LR_DESCRIPTION_MAP[self.type]
        except KeyError:
            myType = LR_DESCRIPTION_UNKNOWN
        return myType
    
    def _typeAttrUnpack(self, theFile):
        """Unpacks and returns type and attribute as a pair from a File."""
        return theFile.unpack(STRUCT_LR_HEAD)

########################################
# Section: Fixed Format Logical Records.
########################################

#================================================
# Section: Marker records such as EOF BOT EOT EOM
#================================================
class LrMarker(LrBase):
    """A marker record such as EOF BOT EOT EOM."""  
    def __init__(self, theType, theAttr):
        super(LrMarker, self).__init__(theType, theAttr)
        assert(self.type in LR_TYPE_MARKER), \
            'Illegal LR type of %d for a LrMarker' % self.type

class LrEOF(LrMarker):
    """A EOF marker record."""  
    def __init__(self, attr=0):
        super(LrEOF, self).__init__(LR_TYPE_EOF, attr)

class LrEOFRead(LrEOF):
    """A EOF marker record read from a file."""  
    def __init__(self, theFile):
        t, a = self._typeAttrUnpack(theFile)
        assert(t == LR_TYPE_EOF), \
            'Illegal LR type of %d for a LrMarker' % t
        super(LrEOFRead, self).__init__(a)

class LrBOT(LrMarker):
    """A BOT marker record."""  
    def __init__(self, attr=0):
        super(LrBOT, self).__init__(LR_TYPE_BOT, attr)

class LrBOTRead(LrBOT):
    """A BOT marker record read from a file."""  
    def __init__(self, theFile):
        t, a = self._typeAttrUnpack(theFile)
        assert(t == LR_TYPE_BOT), \
            'Illegal LR type of %d for a LrMarker' % t
        super(LrBOTRead, self).__init__(a)

class LrEOT(LrMarker):
    """A EOT marker record."""  
    def __init__(self, attr=0):
        super(LrEOT, self).__init__(LR_TYPE_EOT, attr)

class LrEOTRead(LrEOT):
    """A EOT marker record read from a file."""  
    def __init__(self, theFile):
        t, a = self._typeAttrUnpack(theFile)
        assert(t == LR_TYPE_EOT), \
            'Illegal LR type of %d for a LrMarker' % t
        super(LrEOTRead, self).__init__(a)

class LrEOM(LrMarker):
    """A EOM marker record."""  
    def __init__(self, attr=0):
        super(LrEOM, self).__init__(LR_TYPE_EOM, attr)

class LrEOMRead(LrEOM):
    """A EOM marker record read from a file."""  
    def __init__(self, theFile):
        t, a = self._typeAttrUnpack(theFile)
        assert(t == LR_TYPE_EOM), \
            'Illegal LR type of %d for a LrMarker' % t
        super(LrEOMRead, self).__init__(a)

#================================================
# End: Marker records such as EOF BOT EOT EOM
#================================================

class LrWithDateField(LrBase):
    """ABC for classes that have the YY/MM/DD date field.""" 
    def __init__(self, theType, theAttr):
        super(LrWithDateField, self).__init__(theType, theAttr)
    
    @property
    def ymd(self):
        """Returns the YY/MM/DD date field to a year, month, day tuple or None."""
        # http://en.wikipedia.org/wiki/Schlumberger
        # The company recorded the first-ever electrical resistivity well log
        # in Merkwiller-Pechelbronn, France in 1927.
        # So our Y2k fix is:
        # 0-26 is 2000-2026
        # 27-99 is 1927-1999
        try:
            # Unpack and int() may raise ValueError
            # int() might raise UnicodeEncodeError on b'\x00'
            y, m, d = self.date.decode().split('/')
            y = int(y)
            m = int(m)
            d = int(d)
        except ValueError or UnicodeEncodeError:
            pass
        else:
            #print('ymd', y, m, d)
            if y < 27:
                y += 100
            y += 1900
            #print('ymd', y, m, d)
            return y, m, d

#===============================================
# Section: File head and tail (trailer) records.
#===============================================
class LrFileHeadTail(LrWithDateField):
    """Parent class of FileHead, FileTail that have identical structure.""" 
    def __init__(self, theType, theAttr):
        super(LrFileHeadTail, self).__init__(theType, theAttr)
        assert(self.type in (LR_TYPE_FILE_HEAD, LR_TYPE_FILE_TAIL)), \
            'Illegal LR type of %d for a Logical Record File head/tail' % self.type
        self.fileName           = self.init(10)
        self.serviceSubLevel    = self.init(6)
        self.version            = self.init(8)
        self.date               = self.init(8)
        self.maxPrLength        = self.init(5)
        self.fileType           = self.init(2)
        # This can be previous file name or next file name
        # See concrete class properties
        self._contFileName       = self.init(10)
            
    def read(self, theFile):
        """Read from a LIS physical file."""
        (
            self.fileName,
            self.serviceSubLevel,
            self.version,
            self.date,
            self.maxPrLength,
            self.fileType,
            self._contFileName) = theFile.unpack(STRUCT_LR_FILE_HEAD_TAIL)

    @property
    def contFileName(self):
        """Continuation file name."""
        return self._contFileName

class LrFileHead(LrFileHeadTail):
    """Specific class of File Head."""
    def __init__(self, theType, theAttr):
        super(LrFileHead, self).__init__(theType, theAttr)
        assert(self.type == LR_TYPE_FILE_HEAD), \
            'Illegal LR type of %d for a LrFileHead' % self.type

    @property
    def prevFileName(self):
        """Previous file name."""
        return self._contFileName

class LrFileHeadRead(LrFileHead):
    """Specific class of File head read from a file."""
    def __init__(self, theFile):
        t, a = self._typeAttrUnpack(theFile)
        super(LrFileHeadRead, self).__init__(t, a)
        self.read(theFile)

class LrFileTail(LrFileHeadTail):
    """Specific class of File Tail."""
    def __init__(self, theType, theAttr):
        super(LrFileTail, self).__init__(theType, theAttr)
        assert(self.type == LR_TYPE_FILE_TAIL), \
            'Illegal LR type of %d for a LrFileTail' % self.type

    @property
    def nextFileName(self):
        """Next file name."""
        return self._contFileName

class LrFileTailRead(LrFileTail):
    """Specific class of File tail read from a file."""
    def __init__(self, theFile):
        t, a = self._typeAttrUnpack(theFile)
        super(LrFileTailRead, self).__init__(t, a)
        self.read(theFile)

#===============================================
# End: File head and tail (trailer) records.
#===============================================


#========================================================
# Section: Reel and Tape head and tail (trailer) records.
#========================================================
class LrReelTapeHeadTail(LrWithDateField):
    """Parent class of Reel/Tape Head/Tail that have identical structure.""" 
    def __init__(self, theType, theAttr):
        super(LrReelTapeHeadTail, self).__init__(theType, theAttr)
        assert(self.type in (LR_TYPE_TAPE_HEAD,
                               LR_TYPE_TAPE_TAIL,
                               LR_TYPE_REEL_HEAD,
                               LR_TYPE_REEL_TAIL)), \
            'Illegal LR type of %d for a LrReelTapeHeadTail' % self.type
        self.serviceName        = self.init(6)
        self.date               = self.init(8)
        self.origin             = self.init(4)
        self.name               = self.init(8)
        self.contNumber         = self.init(2)
        self._contName          = self.init(8)
        self.comments           = self.init(74)
        
    def read(self, theFile):
        (
            self.serviceName,
            self.date,
            self.origin,
            self.name,
            self.contNumber,
            self._contName,
            self.comments) = theFile.unpack(STRUCT_LR_REEL_TAPE_HEAD_TAIL)
        
class LrTapeHeadTail(LrReelTapeHeadTail):
    """Tape head or tail Logical Record."""
    def __init__(self, theType, theAttr):
        super(LrTapeHeadTail, self).__init__(theType, theAttr)
        assert(self.type in (LR_TYPE_TAPE_HEAD, LR_TYPE_TAPE_TAIL)), \
            'Illegal LR type of %d for a LrTapeHeadTail' % self.type

class LrTapeHead(LrTapeHeadTail):
    """Tape head Logical Record."""
    def __init__(self, theType, theAttr):
        super(LrTapeHead, self).__init__(theType, theAttr)
        assert(self.type == LR_TYPE_TAPE_HEAD), \
            'Illegal LR type of %d for a LrTapeHead' % self.type

    @property
    def prevTapeName(self):
        """Previous tape name."""
        return self._contName

class LrTapeHeadRead(LrTapeHead):
    """Specific class of Tape head read from a file."""
    def __init__(self, theFile):
        t, a = self._typeAttrUnpack(theFile)
        super(LrTapeHeadRead, self).__init__(t, a)
        self.read(theFile)

class LrTapeTail(LrTapeHeadTail):
    """Tape tail Logical Record."""
    def __init__(self, theType, theAttr):
        super(LrTapeTail, self).__init__(theType, theAttr)
        assert(self.type == LR_TYPE_TAPE_TAIL), \
            'Illegal LR type of %d for a LrTapeTail' % self.type

    @property
    def nextTapeName(self):
        """Next tape name."""
        return self._contName

class LrTapeTailRead(LrTapeTail):
    """Specific class of Tape tail read from a file."""
    def __init__(self, theFile):
        t, a = self._typeAttrUnpack(theFile)
        super(LrTapeTailRead, self).__init__(t, a)
        self.read(theFile)

class LrReelHeadTail(LrReelTapeHeadTail):
    """Reel head or tail Logical Record."""
    def __init__(self, theType, theAttr):
        super(LrReelHeadTail, self).__init__(theType, theAttr)
        assert(self.type in (LR_TYPE_REEL_HEAD, LR_TYPE_REEL_TAIL)), \
            'Illegal LR type of %d for a LrReelHeadTail' % self.type

class LrReelHead(LrReelHeadTail):
    """Reel head Logical Record."""
    def __init__(self, theType, theAttr):
        super(LrReelHead, self).__init__(theType, theAttr)
        assert(self.type == LR_TYPE_REEL_HEAD), \
            'Illegal LR type of %d for a LrReelHead' % self.type

    @property
    def prevReelName(self):
        """Previous reel name."""
        return self._contName

class LrReelHeadRead(LrReelHead):
    """Specific class of Reel head read from a file."""
    def __init__(self, theFile):
        t, a = self._typeAttrUnpack(theFile)
        super(LrReelHeadRead, self).__init__(t, a)
        self.read(theFile)

class LrReelTail(LrReelHeadTail):
    """Reel tail Logical Record."""
    def __init__(self, theType, theAttr):
        super(LrReelTail, self).__init__(theType, theAttr)
        assert(self.type == LR_TYPE_REEL_TAIL), \
            'Illegal LR type of %d for a LrReelTail' % self.type

    @property
    def nextReelName(self):
        """Next reel name."""
        return self._contName

class LrReelTailRead(LrReelTail):
    """Specific class of Reel tail read from a file."""
    def __init__(self, theFile):
        t, a = self._typeAttrUnpack(theFile)
        super(LrReelTailRead, self).__init__(t, a)
        self.read(theFile)

#========================================================
# End: Reel and Tape head and tail (trailer) records.
#========================================================

########################################
# End: Fixed Format Logical Records.
########################################

############################################################################
# Section: Misc Logical records - these have no interpreted internal format.
############################################################################
class LrMisc(LrBase):
    """Miscellaneous Logical Record."""
    def __init__(self, theType, theAttr):
        super().__init__(theType, theAttr)
        assert(self.type in LR_TYPE_UNKNOWN_INTERNAL_FORMAT), \
            'Illegal LR type of %d for a LrMisc' % self.type
        self.bytes = b''
    
class LrMiscRead(LrMisc):
    """Miscellaneous Logical Record read from a LIS file."""
    def __init__(self, theFile):
        t, a = self._typeAttrUnpack(theFile)
        super().__init__(t, a)
        self.bytes = theFile.readLrBytes()  

############################################################################
# End: Misc Logical records - these have no interpreted internal format.
############################################################################

################################
# Section: Table EFLRs
# These are type 32, 34, 39.
# 32 : 'Job identification',
# 34 : 'Well site data',
# 39 : 'Tool string info',
################################
"""
Typical Table, file is 200099.S07

Name:            TOOL
Has columns:    MNEM STAT HEIG VOLU WEIG PRES TEMP
Row mnemonics:    MEST NGTC 1A   AMS 

  Type  Code  Size   Cat  Mnem Units  Value
  ----  ----  ----   ---  ---- -----  --------------------------------
    73    65     4     0  TYPE        TOOL

     0    65     4     0  MNEM        MEST
    69    65     4     0  STAT        ALLO
    69    68     4     0  HEIG  IN    41.73
    69    68     4     0  VOLU  F3    1.77
    69    68     4     0  WEIG  LB    442
    69    68     4     0  PRES  PSIA  0
    69    68     4     0  TEMP  DEGF  347

     0    65     4     0  MNEM        NGTC
    69    65     4     0  STAT        ALLO
    69    68     4     0  HEIG  IN    395.02
    69    68     4     0  VOLU  F3    0.573001
    69    68     4     0  WEIG  LB    157
    69    68     4     0  PRES  PSIA  0
    69    68     4     0  TEMP  DEGF  150

     0    65     4     0  MNEM        1A  
    69    65     4     0  STAT        ALLO
    69    68     4     0  HEIG  IN    498.02
    69    68     4     0  VOLU  F3    0.19
    69    68     4     0  WEIG  LB    48
    69    68     4     0  PRES  PSIA  0
    69    68     4     0  TEMP  DEGF  -3.92914e-05

     0    65     4     0  MNEM        AMS 
    69    65     4     0  STAT        ALLO
    69    68     4     0  HEIG  IN    534.02
    69    68     4     0  VOLU  F3    0.520001
    69    68     4     0  WEIG  LB    130
    69    68     4     0  PRES  PSIA  0
    69    68     4     0  TEMP  DEGF  350


Other typical tables:
Name: CONS
Columns: MNEM ALLO PUNI TUNI VALU

Name: PRES
Columns: MNEM STAT TRAC CODE MODE LEDG REDG SCAL

Typical range of table record types [sort | uniq]
Table record (type 34) type: #SCR
Table record (type 34) type: ANNO
Table record (type 34) type: AREA
Table record (type 34) type: AVER
Table record (type 34) type: CMEA
Table record (type 34) type: CMPU
Table record (type 34) type: CONS
Table record (type 34) type: CTIM
Table record (type 34) type: CURV
Table record (type 34) type: DHEQ
Table record (type 34) type: DPL
Table record (type 34) type: DRI
Table record (type 34) type: ELEM
Table record (type 34) type: EQUI
Table record (type 34) type: EXPR
Table record (type 34) type: FILM
Table record (type 34) type: INCL
Table record (type 34) type: INDE
Table record (type 34) type: INPU
Table record (type 34) type: ISEC
Table record (type 34) type: LIMI
Table record (type 34) type: LPRE
Table record (type 34) type: NAKD
Table record (type 34) type: OUTP
Table record (type 34) type: PIP
Table record (type 34) type: PLOT
Table record (type 34) type: POIN
Table record (type 34) type: PRES
Table record (type 34) type: QPL
Table record (type 34) type: SKET
Table record (type 34) type: SONI
Table record (type 34) type: SPL
Table record (type 34) type: SRI
Table record (type 34) type: TOOL
Table record (type 34) type: VDL
Table record (type 34) type: WARN
Table record (type 34) type: WAVE
Table record (type 34) type: XNAM
Table record (type 34) type: XYPL
Table record (type 34) type: ZONE

"""

# Table Logical Records
#: Type of first Component Blocks in the table
COMPONENT_BLOCK_TABLE               = 73
#: Type of first Component Blocks in the Datum Block i.e. row
COMPONENT_BLOCK_DATUM_BLOCK_START   = 0
#: Component Block type that describes an entry in a Datum Block i.e. a cell
COMPONENT_BLOCK_DATUM_BLOCK_ENTRY   = 69

class ExceptionLrTable(ExceptionLr):
    """Specialisation of exception for Table Logical Records."""
    pass

class ExceptionLrTableInit(ExceptionLrTable):
    """Table __init__() issues."""
    pass

class ExceptionLrTableInternaStructuresCorrupt(ExceptionLrTable):
    """Raised when there are inconsistencies with the IR of the table."""
    pass

class ExceptionLrTableCompose(ExceptionLrTable):
    """Table creation (not from file) issues."""
    pass

class ExceptionLrTableRow(ExceptionLrTable):
    """TableRow issues."""
    pass

class ExceptionLrTableRowInit(ExceptionLrTableRow):
    """TableRow __init__() issues."""
    pass

class ExceptionCbEngValInit(ExceptionLrTable):
    """CbEngVal.__init__() issues such as unknown rep code."""
    pass

class CbEngVal(object):
    """Contains the data from a Component Block and has an EngVal"""
    #: Allowable Component Block types
    CB_TYPES = (73, 0, 69)
    def __init__(self):
        self.type       = None # 73, 0, 69
        self.rc         = None
        self.size       = None
        self.category   = None
        self.mnem       = None
        self.units      = None
        self.engVal     = None

    def __str__(self):
        return 'CB: type={:s} rc={:s} size={:s} mnem={:s} {:s}'.format(
            str(self.type),
            str(self.rc),
            str(self.size),
            str(self.mnem),
            str(self.engVal),
        )

    def setValue(self, v):
        """Sets the value to v."""
        if v is None:
            self.engVal = None
        else:
            self.engVal = EngVal.EngValRc(v, self.units, self.rc)

    def lisBytes(self):
        """Return a bytes() array from the internal representation."""
        r = STRUCT_COMPONENT_BLOCK_PREAMBLE.pack(
            self.type,
            self.rc,
            self.size,
            self.category,
            self.mnem,
            self.units)
        if self.engVal is not None:
            return r + RepCode.writeBytes(self.engVal.value, self.engVal.rc)
        return r

    @property
    def value(self):
        """The value of the Component Block or None."""
        if self.engVal is not None:
            return self.engVal.value
        
    @property
    def status(self):
        """Returns True if the value is b'ALLO', False otherwise."""
        return self.value == b'ALLO'

class CbEngValRead(CbEngVal):
    """Contains the data from a Component Block and has an EngVal read from a file."""
    def __init__(self, theFile):
        """Initialise. This will raise a TypeError if theFile.unpack returns None
        i.e. when not enough data to create a Component Block."""
        super(CbEngValRead, self).__init__()
        try:
            (
                self.type,
                self.rc,
                self.size,
                self.category,
                self.mnem,
                self.units) = theFile.unpack(STRUCT_COMPONENT_BLOCK_PREAMBLE)
            if self.rc == RepCode.RC_TYPE_TEXT:
                myVal = RepCode.readRepCode(self.rc, theFile, self.size)
            else:
                myVal = RepCode.readRepCode(self.rc, theFile)
            self.setValue(myVal)
        except (RepCode.ExceptionRepCode, TypeError) as err:
            # RepCode.ExceptionRepCode caused by rep code 105 for example
            # TypeError will happen when the struct unpack is given None
            # as the logical record is incomplete            
            raise ExceptionCbEngValInit(str(err))

class CbEngValWrite(CbEngVal):
    """A Component Block and has an EngVal created directly."""
    def __init__(self, t, v, m, **kwargs):
        """Initialise component block with type, value, mnemonic and optional key words."""
        super().__init__()
        # Set the type repcode etc according to the kwargs. Will set None if absent.
        self.type = t
        self.mnem = m
        if self.type not in self.CB_TYPES:
            raise ExceptionCbWrite('CbEngValWrite type {:d} not in {:s}'.format(self.type, str(self.CB_TYPES)))
#        self.rc         = kwargs.get('rc')
#        self.size       = kwargs.get('size')
        self.category   = kwargs.get('category') or 0
        self.units      = kwargs.get('units') or Units.MT_UNIT
        # Now check and set rc/size according to the native type of v
        # only bytes/float/int acceptable
        # Change the rc and size regardless of what is passed in on the kwargs
        if type(v) == bytes:
            self.rc = 65
            self.size = len(v)
        elif type(v) == float:
            self.rc = 68
            self.size = RepCode.RC_68_SIZE
        elif type(v) == int:
            # Try rep code 66, one byte
            if v >= RepCode.RC_66_MIN and v <= RepCode.RC_66_MAX:
                self.rc = 66
                self.size = RepCode.RC_66_SIZE
            elif v >= RepCode.RC_79_MIN and v <= RepCode.RC_79_MAX:
                self.rc = 79
                self.size = RepCode.RC_79_SIZE
            elif v >= RepCode.RC_73_MIN and v <= RepCode.RC_73_MAX:
                self.rc = 73
                self.size = RepCode.RC_73_SIZE
            else:
                raise ExceptionCbWrite('CbEngValWrite integer {:d} out of range'.format(v))
        else:
            raise ExceptionCbWrite('CbEngValWrite unsupported value type {:s}'.format(type(v)))
        self.setValue(v)
        
class TableRow(object):
    """Represents a row of a table and consists of CbEngVal objects."""
    def __init__(self, theCb):
        if theCb.type != COMPONENT_BLOCK_DATUM_BLOCK_START:
            raise ExceptionLrTableRowInit(
                'Component block type {:d} not a COMPONENT_BLOCK_DATUM_BLOCK_START'.format(theCb.type)
            )
        # List of CbEngValRead
        self._blocks = [theCb]
        # Lazily initialised on __getitem__
        # Otherwise a map {menmonic : index, ...]
        self._cellMnemMap = None
    
    def genCells(self):
        """yields each CbEngVal."""
        for b in self._blocks:
            yield b
    
    def __len__(self):
        """The number of cells in the row."""
        return len(self._blocks)
    
    @property
    def value(self):
        """The name of the row i.e. the value of block 0."""
        return self._blocks[0].value
    
    def _getByLable(self, theB):
        """Returns the index of the block whose mnemonic is theB.
        May raise KeyError on no match."""
        assert(isinstance(theB, bytes))
        if self._cellMnemMap is None:
            self._cellMnemMap = {}
            for i, c in enumerate(self._blocks):
                if c.mnem in self._cellMnemMap:
                    logging.error('Ignoring duplicate mnemonic {!s:s}'
                                  ' in row {!s:s}'.format(c.mnem, self._blocks[0].mnem))
                else:
                    self._cellMnemMap[c.mnem] = i
        # Could raise KeyError here
        return self._cellMnemMap[theB]
    
    def addCb(self, theCb):
        """Adds a component block onto the end of the row.
        Returns the mnemonic field from the component block."""
        if theCb.type != COMPONENT_BLOCK_DATUM_BLOCK_ENTRY:
            raise ExceptionLrTableRow(
                'Component block type {:d} not a COMPONENT_BLOCK_DATUM_BLOCK_ENTRY'.format(theCb.type)
            )
        self._blocks.append(theCb)
        return theCb.mnem
        
    def __getitem__(self, key):
        """If key is an integer or slice this returns a CbEngVal by index(es).
        If key is a bytes() object then this returns a CbEngVal by label.
        May raise a KeyError or IndexError."""
        if isinstance(key, int) or isinstance(key, slice):
            return self._blocks[key]
        elif isinstance(key, bytes):
            return self._blocks[self._getByLable(key)]
            
    def __contains__(self, key):
        """Returns True if this row has a column named key."""
        try:
            self._getByLable(key)
            return True
        except KeyError:
            pass
        return False
            
class LrTable(LrBase):
    """Table-like Logical Record."""
    def __init__(self, theType, theAttr):
        """Base class constructor. theType, theAttr are byte objects i.e. integers 0 to 255"""
        super(LrTable, self).__init__(theType, theAttr)
        assert(self.type in LR_TYPE_TABLE_DATA), \
            'Illegal LR type of %d for a Logical Record Table' % self.type
        self.tableCbEv = None
        # List of TableRow
        self._rows = []
        # {row_name : index, ...}
        self._tableRowIndex = {}
        # Map of rows that have b'MNEM' column
        # {Mnem.Mnem() : index, ...}
        self._mnemRowIndex = {}
        # Ordered dict of { mnem : ref_count, ...}
        self._colMnemS = collections.OrderedDict()
        
    def genRows(self):
        """yields each TableRow.
        TODO: parameter to sort or reverse."""
        for r in self._rows:
            yield r
    
    def genRowNames(self, sort=0):
        """yields each TableRow name.
        If sort > 0 then the results are sorted. If sort < 0 the results are reverse sorted"""
        if sort == 0:
            for r in self._rows:
                yield r.value
        else:
            valS = [r.value for r in self._rows]
            valS.sort(reverse=(sort<0))
            for v in valS:
                yield v

    def retRowByMnem(self, m):
        """Returns the TableRow from a Mnem.Mnem object. i.e. the table row that has a b'MNEM'
        column whose value matches m.
        May raise a KeyError. Note: an IndexError would mean that self.__mnemRowIndex is corrupt."""
        try:
            return self._rows[self._mnemRowIndex[m]]
        except IndexError as err:
            raise ExceptionLrTableInternaStructuresCorrupt('self._mnemRowIndex[m] is index {:d} but number of rows is {:d}'.format(self._mnemRowIndex[m], len(self._rows)))
    
    @property
    def isSingleParam(self):
        """True it this table is a list of single parameters (i.e. type 0 blocks)."""
        return self.tableCbEv == None
    
    @property
    def value(self):
        """The name of the table or None i.e. the value of the first block."""
        if self.tableCbEv is not None:
            return self.tableCbEv.value
    
    def __getitem__(self, key):
        """If key is an integer or slice this returns block by index(es).
        If key is a bytes() object then this returns row by label.
        May raise a KeyError or IndexError."""
#        print('TRACE: __getitem__()', repr(key))
        if isinstance(key, int) or isinstance(key, slice):
            return self._rows[key]
        elif isinstance(key, bytes):
            return self._rows[self._tableRowIndex[key]]
        elif isinstance(key, Mnem.Mnem):
            return self._mnemRowIndex[key]
        raise KeyError('LrTable no key: {:s}'.format(repr(key)))

    def __contains__(self, key):
        """Returns True if this row has a row named key."""
        try:
            self[key]
            return True
        except KeyError as err:
            pass
        return False
    
    def __len__(self):
        """Number of rows in the table."""
        return len(self._rows)
            
    def _incColMnem(self, theMnem):
        """Increment the reference count of the column mnemonic."""
        if theMnem in self._colMnemS:
            self._colMnemS[theMnem] += 1
        else:
            self._colMnemS[theMnem] = 1

    def rowLabels(self):
        """Returns dictionary view of row values (unordered)."""
        return self._tableRowIndex.keys()

    def rowMnems(self):
        """Returns dictionary view of row Mnem.Mnem objects (unordered)."""
        return self._mnemRowIndex.keys()

    def colLabels(self):
        """Returns ordered super-set of column values. Not all rows have these."""
        return self._colMnemS.keys()

    def startNewRow(self, theCbEv):
        """Starts a new row from the component block. Returns theCbEv.mnem value."""
        if theCbEv.type != COMPONENT_BLOCK_DATUM_BLOCK_START:
            raise ExceptionLrTableCompose(
                'Initial row component block not type COMPONENT_BLOCK_DATUM_BLOCK_START but {:d}'.format(theCbEv.type)
            )
        self._rows.append(TableRow(theCbEv))
        self._incColMnem(theCbEv.mnem)
        
    def addDatumBlock(self, theCbEv):
        """Adds a component block to the last row. Returns theCbEv value."""
        if theCbEv.type != COMPONENT_BLOCK_DATUM_BLOCK_ENTRY:
            raise ExceptionLrTableCompose(
                'Component block entry not type COMPONENT_BLOCK_DATUM_BLOCK_ENTRY but {:d}'.format(theCbEv.type))
        if self.isSingleParam:
            raise ExceptionLrTableCompose('COMPONENT_BLOCK_DATUM_BLOCK_ENTRY not allowed in single parameter table.')
        if len(self._rows) == 0:
            raise ExceptionLrTableCompose(
                'COMPONENT_BLOCK_DATUM_BLOCK_ENTRY with no COMPONENT_BLOCK_DATUM_BLOCK_START in table Logical Record.')
        # Add new cell and add name to column super-set
        self._incColMnem(self._rows[-1].addCb(theCbEv))
        
    def _indexLastRowOrDiscard(self):
        # Check if the last row is unique, if not discard it
        if len(self._rows) > 0:
            if self._rows[-1].value in self._tableRowIndex:
                myRow = self._rows.pop()
                logging.warning(
                'LrTableRead(): Discarding duplicate row {:s} in table {:s}'.format(
                    str(myRow.value), str(self.value)
                ))
            else:
                # Add last row to index
                self._tableRowIndex[self._rows[-1].value] = len(self._rows) - 1
                # If last row has a b'MNEM' column then add the value to the Mnem map
                try:
                    myMnem = Mnem.Mnem(self._rows[-1][b'MNEM'].value)
                except KeyError:
                    pass
                else:
                    self._mnemRowIndex[myMnem] = len(self._rows) - 1

    def genRowValuesInColOrder(self, theRow):
        """Yields table cells in a particular row in column order."""
        myR = self[theRow]
        if myR:
            for aColMnem in self._colMnemS.keys():
                try:
                    yield myR[aColMnem]
                except KeyError:
                    yield None
    
    def genLisBytes(self):
        """Yields chunks of binary LIS data (actually each component block)."""
        if self.tableCbEv is not None:
            yield self.tableCbEv.lisBytes()
        for r in range(len(self._rows)):
            for cell in self.genRowValuesInColOrder(r):
                if cell is not None:
                    yield cell.lisBytes()
        
class LrTableRead(LrTable):
    """A table-like Logical Record read from a LIS file."""
    def __init__(self, theFile):
        t, a = self._typeAttrUnpack(theFile)
        super(LrTableRead, self).__init__(t, a)
        myCbEv = CbEngValRead(theFile)
        if myCbEv.type != COMPONENT_BLOCK_TABLE:
            # If the type 73 block is absent then only type 0 blocks can be present
            if myCbEv.type == COMPONENT_BLOCK_DATUM_BLOCK_START:
                self.startNewRow(myCbEv)
            else:
                raise ExceptionLrTableInit('No initial COMPONENT_BLOCK_TABLE in table Logical Record.')
        else:
            self.tableCbEv = myCbEv
        while theFile.hasLd():
            try:
                myCbEv = CbEngValRead(theFile)
            except ExceptionCbEngValInit as err:
                logging.error('LrTableRead.__init__(): Can not construct CB block: {:s}'.format(str(err)))
                break
            except ExceptionFileRead as err:
                # Will happen if there is spurious extra bytes not enough to
                # create a block
                logging.warning('LrTableRead.__init__(): Tell: 0x{:x} LD index: 0x{:x} Error: {:s}'.format(theFile.tellLr(), theFile.ldIndex(), str(err)))
                break
            else:
                if myCbEv.type == COMPONENT_BLOCK_DATUM_BLOCK_START:
                    self._indexLastRowOrDiscard()
                    # Start new row in any case
                    self.startNewRow(myCbEv)
                elif myCbEv.type == COMPONENT_BLOCK_DATUM_BLOCK_ENTRY:
                    try:
                        self.addDatumBlock(myCbEv)
                    except ExceptionLrTableCompose as err:
                        raise ExceptionLrTableInit(str(err))
                else:
                    raise ExceptionLrTableInit('Unknown Component block type {:d}'.format(myCbEv.type))
        # Index the last row
        self._indexLastRowOrDiscard()
        
class LrTableWrite(LrTable):
    """Creates a table from internal Python data structures.
    
    theType is the table type e.g. b'FILM'
    
    theMnemS is the list of column names, theTable members must fit this size.
    
    If an element of the table is a tuple or a list it is assumed to be (value, units).
    """
    def __init__(self, theType, theName, theMnemS, theTable):
        """Construct a table from internal data that must be bytes/float/int.
        theType is the table type e.g. b'FILM'
        theMnemS is the list of column names, theTable members must fit this size.
        If an element of the table is a tuple or a list it is assumed to be (value, units).
        """
        if theType not in LR_TYPE_TABLE_DATA:
            raise ExceptionLrTableInit('Unacceptable table type {:d}'.format(theType))
        super().__init__(theType, 0)
        self.tableCbEv = CbEngValWrite(73, theName, b'TYPE', units=b'    ')
        for row in theTable:
            if len(row) != len(theMnemS):
                raise ExceptionLrTableCompose('LrTableWrite: Row length {:d} does not match MNEM list length {:d}'.format(len(row), len(theMnemS)))
            for c, val in enumerate(row):
                if isinstance(val, tuple) or isinstance(val, list):
                    val, uom = val
                else:
                    uom = Units.MT_UNIT
                if c == 0:
                    myType = 0
                else:
                    myType = 69
                myCbEv = CbEngValWrite(myType, val, theMnemS[c], units=uom)
                if c == 0:
                    self.startNewRow(myCbEv)
                else:
                    self.addDatumBlock(myCbEv)
            self._indexLastRowOrDiscard()
#        print('TRACE:', self._rows)

############################
# End: Table logical records
############################

#########################################
# Section: DFSR and Normal/Alternate data
#########################################

#=======================
# Section: Entry Blocks.
#=======================
# Entry block types for Logical Record DFSR
EB_SET_SIZE = 16+1
EB_TYPE_RANGE = tuple(range(EB_SET_SIZE))
EB_TYPE_TERMINATOR                 = 0
EB_TYPE_DATA_TYPE                  = 1
EB_TYPE_DSB_TYPE                   = 2
EB_TYPE_FRAME_SIZE                 = 3
EB_TYPE_UP_DOWN_FLAG               = 4
EB_TYPE_OPTICAL_DEPTH_UNITS        = 5
EB_TYPE_REF_POINT                  = 6
EB_TYPE_REF_POINT_UNITS            = 7
EB_TYPE_FRAME_SPACE                = 8
EB_TYPE_FRAME_SPACE_UNITS          = 9
EB_TYPE_UNDEFINED_10               = 10
EB_TYPE_MAX_FRAMES_PER_REC         = 11
EB_TYPE_ABSENT_VALUE               = 12
EB_TYPE_RECORD_MODE                = 13
EB_TYPE_DEPTH_UNITS                = 14
EB_TYPE_DEPTH_REP_CODE             = 15
EB_TYPE_DSB_SUB_TYPE               = 16

class ExceptionEntryBlock(ExceptionLr):
    """Specialisation of exception for Entry Blocks."""
    pass

class ExceptionEntryBlockSetInit(ExceptionLr):
    """Exception for EntryBlockSet.__init__()."""
    pass

#: An entry block that contains a type, size, representation code and a value
class EntryBlock(collections.namedtuple('EntryBlock', 'type size repCode value')):
    __slots__= ()
    def lisBytes(self):
        """Returns the LIS bytes for the Entry Block."""
        r = bytearray(STRUCT_ENTRY_BLOCK_PREAMBLE.pack(self.type, self.size, self.repCode))
        if self.value is not None:
            r.extend(RepCode.writeBytes(self.value, self.repCode))
        return r

class EntryBlockRead(EntryBlock):
    """An entry block read from a LIS file."""
    def __new__(self, theFile):
        t, s, r = theFile.unpack(STRUCT_ENTRY_BLOCK_PREAMBLE)
        if s == 0:
            # Special case when size is 0
            return super(EntryBlockRead, self).__new__(self, t, s, r, None)
        return super(EntryBlockRead, self).__new__(self, t, s, r, RepCode.readRepCode(r, theFile, s))

class EntryBlockSet(object):
    """Represents the set of Entry Blocks in a DFSR."""
    #: Map of supported attributes i.e. those that are 'interesting'
    ATTR_MAP = {
        # Normal/Alternate data
        'dataType'              : 1,    # Block 1
        'dsbType'               : 2,    # Block 2
        # Blocks 4, 8 and 9 are significant for indirect depth.
        'upDown'                : 4,    # Block 4
        'optLogScale'           : 5,    # Block 5
        'frameSpacing'          : 8,    # Block 8
        'frameSpacingUnits'     : 9,    # Block 9
        'absentValue'           : 12,   # Block 12
        # If 1 this is indirect depth, 0 is explicit depth
        # If 1 then entries in blocks 4, 8 and 9 and 14 and 15 are significant.
        # If this is 1 and block 9 != block 14 then
        # unit conversion is required from 14->9.
        'recordingMode'         : 13,   # Block 13
        # Strictly speaking these are not 'depth' but could be time
        'depthUnits'            : 14,   # Block 14
        'depthRepCode'          : 15    # Block 15
    }
    #: Documentation about each Entry Block
    EB_DOC = {
        0   : 'Terminator, size is chosen to make total size even.',
        1   : 'Data Record Type. The type of the IFLR (0 | 1) that this describes.',
        2   : 'Datum Spec Block Type. How to interpret the DSBs. Only 0 is defined.',
        3   : 'Data Frame Size. Not required.',
        4   : 'Up/Down. 1=up, 255=down, 0=neither.',
        5   : 'Optical Log Scale. 1=Feet, 255=Meters, 0=Time.',
        6   : 'Data Reference Point. The distance of the data reference point above the tool reference point. Essentially add this to depth to find the depth axis of un-memorised data such as tension.',
        7   : 'Units for Data Reference Point.',
        8   : 'Frame Spacing.',
        9   : 'Units for Frame Spacing.',
        10  : 'Undefined.',
        11  : 'Maximum Frames per Record.',
        12  : 'Absent value.',
        13  : 'Depth Recording Mode. 1=Indirect X, 0=Direct X',
        14  : 'Units of Depth when depth Recording Mode=1',
        15  : 'Representation Code for depth when Depth Recording Mode=1',
        16  : 'Datum Spec Block sub-Type. How to interpret the DSBs (0 | 1)',
    }
    #: List of block numbers that are not written out, also _setLisSizeEven()
    #: and lisSize() ignore these.
    BLOCKS_TO_SKIP = (10,)
    def __init__(self):
        # Set defaults
        self._ebS = [
            EntryBlock(EB_TYPE_TERMINATOR,              0, 66, None),       # 0
            EntryBlock(EB_TYPE_DATA_TYPE,               1, 66, 0),          # 1
            EntryBlock(EB_TYPE_DSB_TYPE,                1, 66, 0),          # 2
            # Default not specified in LIS79 specification so assumed here
            EntryBlock(EB_TYPE_FRAME_SIZE,              1, 66, 0),          # 3
            EntryBlock(EB_TYPE_UP_DOWN_FLAG,            1, 66, 1),          # 4
            EntryBlock(EB_TYPE_OPTICAL_DEPTH_UNITS,     1, 66, 1),          # 5
            # Default not specified in LIS79 specification so assumed here
            EntryBlock(EB_TYPE_REF_POINT,               0, 66, None),       # 6
            EntryBlock(EB_TYPE_REF_POINT_UNITS,         4, 65, b'.1IN'),    # 7
            # Default not specified in LIS79 specification so assumed here
#            EntryBlock(EB_TYPE_FRAME_SPACE,             1, 66, 60),         # 8
#            EntryBlock(EB_TYPE_FRAME_SPACE_UNITS,       4, 65, b'.1IN'),    # 9
            EntryBlock(EB_TYPE_FRAME_SPACE,             0, 66, None),         # 8
            EntryBlock(EB_TYPE_FRAME_SPACE_UNITS,       0, 65, None),    # 9
            # Default not specified in LIS79 specification so assumed here
            EntryBlock(EB_TYPE_UNDEFINED_10,            0, 66, None),       # 10
            # Default not specified in LIS79 specification so assumed here
            EntryBlock(EB_TYPE_MAX_FRAMES_PER_REC,      0, 66, None),       # 11
            EntryBlock(EB_TYPE_ABSENT_VALUE,            4, 68, -999.25),    # 12
            EntryBlock(EB_TYPE_RECORD_MODE,             1, 66, 0),          # 13
            EntryBlock(EB_TYPE_DEPTH_UNITS,             4, 65, b'.1IN'),    # 14
            # Default not specified in LIS79 specification so an impossible 0 assumed here
            EntryBlock(EB_TYPE_DEPTH_REP_CODE,          1, 66, 0),          # 15
            EntryBlock(EB_TYPE_DSB_SUB_TYPE,            1, 66, 0),          # 16
        ]
        self._setLisSizeEven()
        assert(self._checkIntegrity() == 0), \
            'Integrity failure of default values [{:d}:\n{:s}'.format(
                self._checkIntegrity(),
                str(self._ebS),
                )
    
    def __str__(self):
        return 'EntryBlockSet [{:d} bytes]:\n'.format(self.lisSize()) \
            + '\n'.join([str(e) for e in self._ebS])
    
    def __getattr__(self, name):
        """Returns the Entry Block corresponding to the name."""
        try:
            return self._ebS[self.ATTR_MAP[name]].value
        except KeyError or IndexError as err:
            raise AttributeError(str(err))
    
    def __getitem__(self, key):
        """This returns an Entry block by integer index."""
        return self._ebS[key]

    @property
    def logUp(self):
        """True if the logging direction is up (X decreasing).
        Note: not logUp and not logDown is possible to be True e.g. time log."""
        return self.upDown == 1

    @property
    def logDown(self):
        """True if the logging direction is down (X increasing).
        Note: not logUp and not logDown is possible to be True e.g. time log."""
        return self.upDown == 255
    
    @property
    def xInc(self):
        """True if the logging X increases (down or time log)."""
        return not self.logUp
    
    @property
    def opticalLogScale(self):
        """Returns the Units corresponding to Entry Block 5: 'Optical Log Scale'
        This will be a LENG or TIME unit or empty if undefined."""
        # 5   : 'Optical Log Scale. 1=Feet, 255=Meters, 0=Time.',
        # EntryBlock(EB_TYPE_OPTICAL_DEPTH_UNITS,     1, 66, 1),          # 5
        val = self._ebS[EB_TYPE_OPTICAL_DEPTH_UNITS].value
        if val == 1:
            return Units.OPTICAL_FEET
        elif val == 255:
            return Units.OPTICAL_METERS
        elif val == 0:
            return Units.OPTICAL_TIME
        return Units.MT_UNIT
    
    def lisSize(self):
        """Returns the totla size of the Entry Block set."""
        return sum([e.size for e in self._ebS if e.type not in self.BLOCKS_TO_SKIP])
    
    def _checkIntegrity(self):
        if len(self._ebS) != EB_SET_SIZE:
            return 1
        for i, eb in enumerate(self._ebS):
            if eb.type != i:
                return 2
            # If value None then size should be 0 and visa versa
            if eb.size == 0 and eb.value is not None:
                return 3
            # If value None then size should be 0 and visa versa
            if eb.value is None and eb.size != 0:
                return 4
        return 0
    
    def _setLisSizeEven(self):
        """Sets the total LIS size of the Entry Block set to be even by
        adjusting the size of the terminator block."""
        assert(self._checkIntegrity() == 0)
        # Set terminator block zero size
        self._ebS[0] = EntryBlock(EB_TYPE_TERMINATOR, 0, 66, None)
        if self.lisSize() % 2:
            # Set terminator block size 1
            self._ebS[0] = EntryBlock(EB_TYPE_TERMINATOR, 1, 66, 1)
    
    def setEntryBlock(self, theEb):
        """Sets an Entry Block."""
        assert(self._checkIntegrity() == 0)
        if theEb.type not in EB_TYPE_RANGE:
            raise ExceptionEntryBlock(
                'EntryBlockSet.setEntryBlock(): type {:s} not in range'.format(str(theEb.type)))
        if theEb.type in self.BLOCKS_TO_SKIP:
            raise ExceptionEntryBlock(
                'EntryBlockSet.setEntryBlock(): type {:s} excluded from EntryBlockSet value: {:s}'.format(str(theEb.type), str(theEb)))
        self._ebS[theEb.type] = theEb
        self._setLisSizeEven()
        assert(self._checkIntegrity() == 0)

    def readFromFile(self, theFile):
        """Reads from a File object. NOTE: theFile.hasLd() must be True so
        the Logical Record Header must have been read already."""
        while theFile.hasLd():
            eb = EntryBlockRead(theFile)
            try:
                self.setEntryBlock(eb)
            except ExceptionEntryBlock as err:
                logging.warning('EntryBlockSet.readFromFile(): File.tellLr= 0x{:x} error: {:s}'.format(theFile.tellLr(), str(err)))
            if eb.type == 0:
                break
        self._setLisSizeEven()
        
    def lisBytes(self):
        """Returns the Entry Block set as an array of bytes."""
        return b''.join(self.lisByteList())
    
    def lisByteList(self):
        "Returns a list of bytes() objects, one for each entry block."""
        self._setLisSizeEven()
        r = []
        for e in self._ebS:
            if e.type not in self.BLOCKS_TO_SKIP \
            and e.type != EB_TYPE_TERMINATOR:
                r.append(e.lisBytes())
        # Add terminator Entry Block
        r.append(self._ebS[EB_TYPE_TERMINATOR].lisBytes())
        return r
        
#=======================
# End: Entry Blocks.
#=======================

#=====================================
# Section: Datum Specification Blocks.
#=====================================
class ExceptionDatumSpecBlock(ExceptionLr):
    """Specialisation of exception for Datum Specification Blocks."""
    pass

class DatumSpecBlock(object):
    """This represents as Datum Specification Block."""
    def __init__(self):
        self.mnem           = None
        self.servId         = None
        self.servOrd        = None
        self.units          = None
        self.apiLogType     = None
        self.apiCurveType   = None
        self.apiCurveClass  = None
        self.apiModifier    = None
        self.fileNumber     = None
        self.size           = None
        # Note: use samples()
        self._samples        = None
        self.repCode        = None
        # Computed bursts and sub channels
        # bursts are invariant over sub-channels
        self._bursts        = None
        self.subChannels    = None
    
    @property
    def isNull(self):
        """True if this block is compromised in any way and should be ignored
        when composing a DFSR. The critical test is whether the data from this
        channel will be in the frame."""
        return self.size == 0 
    
    def _setBurstsSubChannels(self):
        """Calculates the number of sub-channels and bursts."""
        # Dipmeter data is specially treated
        if self.repCode == RepCode.DIPMETER_EDIT_TAPE_REP_CODE:
            self.subChannels = RepCode.DIPMETER_NUM_FAST_CHANNELS
            self._bursts = 1
        elif self.repCode == RepCode.DIPMETER_CSU_FIELD_TAPE_REP_CODE:
            self.subChannels = RepCode.DIPMETER_NUM_FAST_CHANNELS + RepCode.DIPMETER_NUM_SLOW_CHANNELS
            self._bursts = 1
        else:
            # If size == 0 set self.subChannels, self._bursts = 0
            if self.size > 0:
                self.subChannels = 1
                myRepCodeSize = RepCode.lisSize(self.repCode)
                # Test exact modulo
                if (self.size % (myRepCodeSize * self._samples)) != 0:
                    raise ExceptionDatumSpecBlock(
                        'DatumSpecBlock._setBurstsSubChannels(): Fractional bursts from size={:s}, rcSize={:s}, samples={:s}'.format(
                            str(self.size), str(myRepCodeSize), str(self._samples)
                        )
                    )
                self._bursts = self.size // (myRepCodeSize * self._samples)
            else:
                logging.warning('DatumSpecBlock MNEM={!s:s} has zero length.'.format(self.mnem))
                self.subChannels = 0
                self._bursts = 0

    def samples(self, theSc):
        """Returns the number of samples in a sub-channel."""
        if theSc < 0 or theSc >= self.subChannels:
            raise IndexError('Index out of range.')
        if self.repCode == RepCode.DIPMETER_EDIT_TAPE_REP_CODE:
            return RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES
        elif self.repCode == RepCode.DIPMETER_CSU_FIELD_TAPE_REP_CODE:
            if theSc < RepCode.DIPMETER_NUM_FAST_CHANNELS:
                return RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES
            return 1
        return self._samples
    
    def bursts(self, theSc):
        """Returns the (samples, burst) for a sub-channel (bursts are invariant over sub-channels)."""
        # bursts are invariant over sub-channels
        return self._bursts
    
    def values(self):
        """Returns the total number of discrete values per frame for a single channel."""
        if self.repCode == RepCode.DIPMETER_EDIT_TAPE_REP_CODE:
            return RepCode.DIPMETER_SIZE_FAST_CHANNELS
        elif self.repCode == RepCode.DIPMETER_CSU_FIELD_TAPE_REP_CODE:
            return RepCode.DIPMETER_SIZE_FAST_CHANNELS + RepCode.DIPMETER_NUM_SLOW_CHANNELS
        return self._samples * self._bursts

    def _unpackApiInt(self, theInt):
        """Unpacks the API codes so that an integer value 45310011 returns
        (45, 310, 01, 1)."""
        return (
            (theInt // 1000000),
            (theInt % 1000000) // 1000,
            (theInt % 1000) // 10,
            theInt % 10,
            )
        
    def _unpackApiCodes(self, theInt):
        """Unpacks the API codes so that an integer value 45310011 sets
        (45, 310, 01, 1)."""
        (
            self.apiLogType,
            self.apiCurveType,
            self.apiCurveClass,
            self.apiModifier,) = self._unpackApiInt(theInt)
    
    def subChMnem(self, theSc):
        """Returns the curve Mnemonic for a particular sub-channel or None if unknown."""
        if self.subChannels == 1:
            return self.mnem
        if self.repCode in RepCode.DIPMETER_REP_CODES:
            return RepCode.DIPMETER_SUB_CHANNEL_SHORT_LONG_NAMES[theSc][0]
        
class DatumSpecBlockRead(DatumSpecBlock):
    """This represents as Datum Specification Block read from a file."""
    def __init__(self, theF):
        super(DatumSpecBlockRead, self).__init__()
        (
            self.mnem,
            self.servId,
            self.servOrd,
            self.units,
            myApiInt,
            self.fileNumber,
            self.size,
            self._samples,
            self.repCode,
            ) = theF.unpack(STRUCT_DSB)
        # Fix API codes
        self._unpackApiCodes(myApiInt)
        # Set bursts and sub-channels
        self._setBurstsSubChannels()
#=====================================
# End: Datum Specification Blocks.
#=====================================

#============================================
# Section: Datum Format Specification Record.
#============================================
class LrDFSR(LrBase):
    """Data Format Specification Record."""
    def __init__(self, theType, theAttr):
        super(LrDFSR, self).__init__(theType, theAttr)
        assert(self.type == LR_TYPE_DATA_FORMAT), \
            'Illegal LR type of %d for a Logical Record DFSR' % self.type
        self.ebs = EntryBlockSet()
        # Ordered list of [DatumSpecBlock, ...]
        self.dsbBlocks = []

#    def __getitem__(self, key):
#        """This returns an Entry block by integer index."""
#        return self.dsbBlocks[key]
            
    def frameSize(self):
        return sum([d.size for d in self.dsbBlocks])
    
class LrDFSRRead(LrDFSR):
    """Data Format Specification Record read from a file."""
    def __init__(self, theFile):
        t, a = self._typeAttrUnpack(theFile)
        super(LrDFSRRead, self).__init__(t, a)
        self.ebs.readFromFile(theFile)
        if self.ebs.dsbType != 0:
            raise ExceptionLr('LrDFSRRead: Can not read DSB blocks of type {:d}'.format(self.ebs.dsbType))
        while theFile.hasLd():
            myDsbr = DatumSpecBlockRead(theFile)
            if not myDsbr.isNull:
                self.dsbBlocks.append(myDsbr)
            else:
                logging.warning('LrDFSRRead.__init__(): Ignoring NULL Datum Spec. Block')
#============================================
# End: Datum Format Specification Record.
#============================================

#==========================================================================
# Section: Normal and Alternate data, these are supported 'by other means'.
#==========================================================================
class LrNormalAlternateData(LrBase):
    """Class for Normal and Alternate data i.e. curve data."""
    def __init__(self, theType, theAttr):
        super(LrNormalAlternateData, self).__init__(theType, theAttr)
        assert(self.type in (LR_TYPE_NORMAL_DATA, LR_TYPE_ALTERNATE_DATA)), \
            'Illegal LR type of %d for a Logical Record Normal/Alternate Data' % self.type
        raise ExceptionLrNotImplemented('Logical Record Normal/Alternate Data not implemented.')

class LrNormalAlternateDataRead(LrNormalAlternateData):
    """Class for Normal and Alternate data i.e. curve data."""
    def __init__(self, theFile):
        t, a = self._typeAttrUnpack(theFile)
        super(LrNormalAlternateDataRead, self).__init__(t, a)
#==========================================================================
# End: Normal and Alternate data, these are supported 'by other means'.
#==========================================================================

#########################################
# End: DFSR and Normal/Alternate data
#########################################

###################################
# Section: Indirect Logical Records
###################################
class LrFactory(object):
    """Provides a despatch mechanism for generating Logical Records.
    This can be sub-classed to create different sets of Logical Records.
    For example the Indexer creates minimal logical records."""
    def __init__(self):
        self._lrMap = {}
        # Log data
        for t in LR_TYPE_LOG_DATA:
            self._lrMap[t] = LrNormalAlternateData
        # Table records
        for t in LR_TYPE_TABLE_DATA:
            self._lrMap[t] = LrTable
        # DFSR
        self._lrMap[LR_TYPE_DATA_FORMAT] = LrDFSR
        # Delimiter records
        self._lrMap[LR_TYPE_FILE_HEAD] = LrFileHead
        self._lrMap[LR_TYPE_FILE_TAIL] = LrFileTail
        self._lrMap[LR_TYPE_TAPE_HEAD] = LrTapeHead
        self._lrMap[LR_TYPE_TAPE_TAIL] = LrTapeTail
        self._lrMap[LR_TYPE_REEL_HEAD] = LrReelHead
        self._lrMap[LR_TYPE_REEL_TAIL] = LrReelTail
        # Marker records
        self._lrMap[LR_TYPE_EOF] = LrEOF
        self._lrMap[LR_TYPE_BOT] = LrBOT
        self._lrMap[LR_TYPE_EOT] = LrEOT
        self._lrMap[LR_TYPE_EOM] = LrEOM
        # Unknown internal format
        for t in LR_TYPE_UNKNOWN_INTERNAL_FORMAT:
            self._lrMap[t] = LrMisc

class LrFactoryRead(LrFactory):
    """A factory for generating complete Logical Records from a file."""
    def __init__(self):
        super(LrFactoryRead, self).__init__()
        # Specialise despatch map
        # Log data
        for t in LR_TYPE_LOG_DATA:
            self._lrMap[t] = None#LrNormalAlternateDataRead
        # Table records
        for t in LR_TYPE_TABLE_DATA:
            self._lrMap[t] = LrTableRead
        # DFSR
        self._lrMap[LR_TYPE_DATA_FORMAT] = LrDFSRRead
        # Delimiter records
        self._lrMap[LR_TYPE_FILE_HEAD] = LrFileHeadRead
        self._lrMap[LR_TYPE_FILE_TAIL] = LrFileTailRead
        self._lrMap[LR_TYPE_TAPE_HEAD] = LrTapeHeadRead
        self._lrMap[LR_TYPE_TAPE_TAIL] = LrTapeTailRead
        self._lrMap[LR_TYPE_REEL_HEAD] = LrReelHeadRead
        self._lrMap[LR_TYPE_REEL_TAIL] = LrReelTailRead
        # Marker records
        self._lrMap[LR_TYPE_EOF] = LrEOFRead
        self._lrMap[LR_TYPE_BOT] = LrBOTRead
        self._lrMap[LR_TYPE_EOT] = LrEOTRead
        self._lrMap[LR_TYPE_EOM] = LrEOMRead
        # Unknown internal format
        for t in LR_TYPE_UNKNOWN_INTERNAL_FORMAT:
            self._lrMap[t] = LrMiscRead
    
    def retLrFromFile(self, theFile):
        """Given a LIS file this reads one Logical Record, and returns the
        appropriate Logical Record object or None."""
        # Read from file
        # First read a single byte
        myLtype = theFile.readLrBytes(1)[0]
        # Now rewind and re-read. This causes duplicate PR readHead() calls.
        #print('Logical record type', myLtype)
        t = self._lrMap[myLtype]
        if t is not None:
            theFile.seekCurrentLrStart()
            return self._lrMap[myLtype](theFile)

###################################
# End: Indirect Logical Records
###################################
