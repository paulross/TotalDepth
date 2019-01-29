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
"""Module for translating raw LIS to an appropriate internal type for LIS
Representation Codes ('RepCodes').

This aggregates pRepCode and cRepCode with the latter overwriting the former.

Created on 11 Nov 2010

@author: p2ross
"""

__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

# Import the Python reference methods
from TotalDepth.LIS.core.pRepCode import *
# Now overlay with any implemented in Cython
from TotalDepth.LIS.core.cRepCode import *
# Now overlay with any implemented in CPython
try:
    from TotalDepth.LIS.core.cpRepCode import *
except ImportError:
    # cpRepCode does not exist yet
    pass

class ExceptionRepCodeRead(ExceptionRepCode):
    """Exception for unknown Representation codes in look up tables."""
    pass

class ExceptionRepCodeWrite(ExceptionRepCode):
    """Exception for unknown Representation codes in look up tables."""
    pass

class ExceptionRepCodeNoLength(ExceptionRepCode):
    """Exception for indeterminate length when using Rep Code 65."""
    pass

##################
# Section: Reading
# Regex:
#49
#50
#56
#66
#68
#70
#73
#77
#79
#
#Search for: (\d+)
#
# Replace:
#def read\1(theFile):
#    """Returns a Representation Code \1 value from a File object."""
#    return from\1(theFile.unpack(STRUCT_RC_\1)[0])
#
#def readBytes\1(arg):
#    """Returns a Representation Code \1 value from a bytes object."""
#    return from\1(STRUCT_RC_\1.unpack(arg)[0])
##################
def read49(theFile):
    """Returns a Representation Code 49 value from a File object."""
    return from49(theFile.unpack(STRUCT_RC_49)[0])

def readBytes49(arg):
    """Returns a Representation Code 49 value from a bytes object."""
    return from49(STRUCT_RC_49.unpack(arg)[0])

def read50(theFile):
    """Returns a Representation Code 50 value from a File object."""
    return from50(theFile.unpack(STRUCT_RC_50)[0])

def readBytes50(arg):
    """Returns a Representation Code 50 value from a bytes object."""
    return from50(STRUCT_RC_50.unpack(arg)[0])

def read56(theFile):
    """Returns a Representation Code 56 value from a File object."""
    return from56(theFile.unpack(STRUCT_RC_56)[0])

def readBytes56(arg):
    """Returns a Representation Code 56 value from a bytes object."""
    return from56(STRUCT_RC_56.unpack(arg)[0])

def read66(theFile):
    """Returns a Representation Code 66 value from a File object."""
    return from66(theFile.unpack(STRUCT_RC_66)[0])

def readBytes66(arg):
    """Returns a Representation Code 66 value from a bytes object."""
    return from66(STRUCT_RC_66.unpack(arg)[0])

def writeBytes66(v):
    """Converts a value to a Rep Code 66 and returns the bytes."""
    return bytes([v,])

def read68(theFile):
    """Returns a Representation Code 68 value from a File object."""
    return from68(theFile.unpack(STRUCT_RC_68)[0])

def readBytes68(arg):
    """Returns a Representation Code 68 value from a bytes object."""
    return from68(STRUCT_RC_68.unpack(arg)[0])

def writeBytes68(v):
    """Converts a value to a Rep Code 68 and returns the bytes."""
    w = to68(v)
    #print('writeBytes68()', w)
    try:
        return STRUCT_RC_68.pack(w)
    except struct.error as err:
        raise ExceptionRepCodeWrite('RepCode.writeBytes68(): value={:s} w={:s} error: {:s}'.format(str(v), str(w), str(err)))

def read70(theFile):
    """Returns a Representation Code 70 value from a File object."""
    return from70(theFile.unpack(STRUCT_RC_70)[0])

def readBytes70(arg):
    """Returns a Representation Code 70 value from a bytes object."""
    return from70(STRUCT_RC_70.unpack(arg)[0])

def read73(theFile):
    """Returns a Representation Code 73 value from a File object."""
    return from73(theFile.unpack(STRUCT_RC_73)[0])

def readBytes73(arg):
    """Returns a Representation Code 73 value from a bytes object."""
    return from73(STRUCT_RC_73.unpack(arg)[0])

def writeBytes73(v):
    """Converts a value to a Rep Code 73 and returns the bytes."""
    #print('writeBytes73(v)', v)
    return STRUCT_RC_73.pack(to73(v))

def read77(theFile):
    """Returns a Representation Code 77 value from a File object."""
    return from77(theFile.unpack(STRUCT_RC_77)[0])

def readBytes77(arg):
    """Returns a Representation Code 77 value from a bytes object."""
    return from77(STRUCT_RC_77.unpack(arg)[0])

def read79(theFile):
    """Returns a Representation Code 79 value from a File object."""
    return from79(theFile.unpack(STRUCT_RC_79)[0])

def readBytes79(arg):
    """Returns a Representation Code 79 value from a bytes object."""
    return from79(STRUCT_RC_79.unpack(arg)[0])

def readBytes130(by):
    """Reads Dipmeter RepCode 130 and returns a list of (integer) values."""
    return by[0]
    if len(by) < DIPMETER_LIS_SIZE_130:
        raise ExceptionRepCodeRead('readBytes130(): Not enough data to read RepCode, only {:d} bytes'.format(len(by)))
    return list(by[:DIPMETER_LIS_SIZE_130])

def readBytes234(by):
    """Reads Dipmeter RepCode 234 and returns a list of (integer) values."""
    return by[0]
    if len(by) < DIPMETER_LIS_SIZE_234:
        raise ExceptionRepCodeRead('readBytes234(): Not enough data to read RepCode, only {:d} bytes'.format(len(by)))
    return list(by[:DIPMETER_LIS_SIZE_234])

##################
# End: Reading
##################

# Map of Representation Code to from... function
FROM_DESPATCH_MAP = {
    49 : from49,
    50 : from50,
    56 : from56,
    66 : from66,
    68 : from68,
    70 : from70,
    73 : from73,
    77 : from77,
    79 : from79,
}

# Map of Representation Code to read... function
READ_FILE_DESPATCH_MAP = {
    49 : read49,
    50 : read50,
    56 : read56,
    66 : read66,
    68 : read68,
    70 : read70,
    73 : read73,
    77 : read77,
    79 : read79,
}

# Map of Representation Code to readBytes... function
READ_BYTES_DESPATCH_MAP = {
    49 : readBytes49,
    50 : readBytes50,
    56 : readBytes56,
    66 : readBytes66,
    68 : readBytes68,
    70 : readBytes70,
    73 : readBytes73,
    77 : readBytes77,
    79 : readBytes79,
    # Dipmeter codes, these return a list of values rather than a single value
    130 : readBytes130,
    234 : readBytes234,
}

# Map of Representation Code to writeBytes... function
WRITE_BYTES_DESPATCH_MAP = {
    #49 : writeBytes49,
    #50 : writeBytes50,
    #56 : writeBytes56,
    66 : writeBytes66,
    68 : writeBytes68,
    #70 : writeBytes70,
    73 : writeBytes73,
    #77 : writeBytes77,
    #79 : writeBytes79,
}


# Map of Representation Code to to... function
TO_DESPATCH_MAP = {
    49 : to49,
    50 : to50,
    56 : to56,
    66 : to66,
    68 : to68,
    70 : to70,
    73 : to73,
    77 : to77,
    79 : to79,
}

def fromRepCode(theRc, theWord):
    try:
        return FROM_DESPATCH_MAP[theRc](theWord)
    except KeyError:
        raise ExceptionRepCodeUnknown('fromRepCode(): Unsupported representation code %s' % theRc)

def readRepCode(theRc, theFile, theLen=None):
    """Reads a Representation Code from the file and returns a value.
    If theRc is 65 (string) then theLen must be supplied, up to that length of
    bytes will be returned."""
    if theRc == RC_TYPE_TEXT:
        if theLen is None:
            raise ExceptionRepCodeNoLength('readRepCode(): No length given for representation code %s' % theRc)
        return theFile.readLrBytes(theLen)
    try:
        return READ_FILE_DESPATCH_MAP[theRc](theFile)
    except KeyError:
        raise ExceptionRepCodeUnknown('readRepCode(): Unsupported representation code %s' % theRc)

def readBytes(theRc, theB, theLen=None):
    """Reads a Representation Code from the a bytes() object. If theRc is 65
    (string) then theLen must be supplied, up to that length of bytes will be
    returned."""
    if theRc == RC_TYPE_TEXT:
        if theLen is None:
            raise ExceptionRepCodeNoLength('readBytes(): No length given for representation code %s' % theRc)
        return theB[:theLen]
    try:
        return READ_BYTES_DESPATCH_MAP[theRc](theB)
    except struct.error as err:
        raise ExceptionRepCodeRead('RepCode.readBytes(): rc={:s} error: {:s}'.format(str(theRc), str(err)))
    except KeyError:
        raise ExceptionRepCodeUnknown('readBytes(): Unsupported representation code %s' % theRc)

def writeBytes(v, r):
    """Takes a value v and a Representation Code r and converts this to a
    bytes() object."""
    if r == RC_TYPE_TEXT:
        return v
    try:
        return WRITE_BYTES_DESPATCH_MAP[r](v)
    except struct.error as err:
        raise ExceptionRepCodeWrite('RepCode.writeBytes(): value={:s} rc={:s} error: {:s}'.format(str(v), str(r), str(err)))
    except KeyError:
        raise ExceptionRepCodeUnknown('RepCode.writeBytes(): Unsupported representation code %s' % r)
#===============================================================================
# def toRepCode(theRc, theValue):
#    try:
#        return TO_DESPATCH_MAP[theRc](theValue)
#    except KeyError:
#        raise ExceptionRepCodeUnknown('toRepCode(): Unsupported representation code %s' % theRc)
#===============================================================================
