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
"""Python module for translating raw LIS to an appropriate internal type for LIS
Representation Codes ('RepCodes').

Created on 11 Nov 2010

@author: p2ross
"""

__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

import logging
import math
import struct

from TotalDepth.LIS import ExceptionTotalDepthLIS

class ExceptionRepCode(ExceptionTotalDepthLIS):
    """Specialisation of exception for Representation codes."""
    pass

class ExceptionRepCodeUnknown(ExceptionRepCode):
    """Specialisation of exception for unknown Representation codes."""
    pass

# Integer constants created by anonymous enumerators
# Identifier for text Representation Codes
RC_TYPE_TEXT      = 65
# Sizes of LIS79 data in bytes:
RC_49_SIZE        = 2    # Rep code 0x31, 16bit floating point representation
RC_50_SIZE        = 4    # Rep code 0x32, 32bit floating point representation
RC_56_SIZE        = 1    # Rep code 0x38, signed char representation
# Rep code 65 is a string so 0 means any length is allowed
RC_65_SIZE        = 0    # Rep code 0x41, Alphanumeric (allows zero length strings)
RC_66_SIZE        = 1    # Rep code 0x42, unsigned byte
RC_68_SIZE        = 4    # Rep code 0x44, 32bit floating point representation
RC_70_SIZE        = 4    # Rep code 0x46, 32bit fixed point
RC_73_SIZE        = 4    # Rep code 0x49, 32bit signed integer
RC_77_SIZE        = 1    # Rep code 0x4D, 8bit mask
RC_79_SIZE        = 2    # Rep code 0x4F, 16bit signed integer

#######################################################
# Section: Dipmeter Representation Codes and structure.
#######################################################
RC_130_SIZE       = 80   # Dipmeter HDT edit tape rep code
RC_234_SIZE       = 90   # Dipmeter HDT CSU Field Tape rep codes
DIPMETER_EDIT_TAPE_REP_CODE         = 130
DIPMETER_CSU_FIELD_TAPE_REP_CODE    = 234
DIPMETER_REP_CODES                  = (
                                       DIPMETER_EDIT_TAPE_REP_CODE,
                                       DIPMETER_CSU_FIELD_TAPE_REP_CODE
                                       )
DIPMETER_NUM_FAST_CHANNELS          = 5
# Rep Code 234 only
DIPMETER_NUM_SLOW_CHANNELS          = 10
DIPMETER_FAST_CHANNEL_SUPER_SAMPLES = 16
DIPMETER_SIZE_FAST_CHANNELS = DIPMETER_NUM_FAST_CHANNELS * DIPMETER_FAST_CHANNEL_SUPER_SAMPLES
DIPMETER_SIZE_SLOW_CHANNELS = DIPMETER_NUM_SLOW_CHANNELS * 1
# LIS Sizes
DIPMETER_LIS_SIZE_130 = DIPMETER_SIZE_FAST_CHANNELS
DIPMETER_LIS_SIZE_234 = DIPMETER_SIZE_FAST_CHANNELS + DIPMETER_SIZE_SLOW_CHANNELS
# Dipmeter Channel Names
#
# Raw HDT Pass 1.
DIPMETER_130_CHANNEL_NAME           = b"RPS1"
# Raw HDT
DIPMETER_234_CHANNEL_NAME           = b"RHDT"
# Five fast channels for codes 130/234
# Ten extra slow channels for code 234 only
DIPMETER_SUB_CHANNEL_SHORT_LONG_NAMES = (
    (b"FC0 ", 'Fast channel 0'),
    (b"FC1 ", 'Fast channel 1'),
    (b"FC2 ", 'Fast channel 2'),
    (b"FC3 ", 'Fast channel 3'),
    (b"FC4 ", 'Fast channel 4'),
    (b"STAT", 'Status'),
    (b"REF ", 'Reference'),
    (b"REFC", 'Reference check'),
    (b"EMEX", 'Emex scale'),
    (b"PADP", 'Pad pressure'),
    (b"TEMP", 'Temperature'),
    (b"FEP1", 'Far electrode potential 1'),
    (b"FEP2", 'Far electrode potential 2'),
    (b"RAC1", 'Raw calliper 1'),
    (b"RAC2", 'Raw calliper 2'),
)

# Dipmeter structs
# Code 130
STRUCT_RC_DIPMETER_EDIT_TAPE = struct.Struct('>80B')
# 80 bytes, 80 fields.
assert(STRUCT_RC_DIPMETER_EDIT_TAPE.size == DIPMETER_LIS_SIZE_130)
assert(len(STRUCT_RC_DIPMETER_EDIT_TAPE.unpack(b' ' * STRUCT_RC_DIPMETER_EDIT_TAPE.size)) == DIPMETER_LIS_SIZE_130)

# Code 234
STRUCT_RC_DIPMETER_CSU_FIELD_TAPE = struct.Struct('>90B')
# 90 bytes, 90 fields.
assert(STRUCT_RC_DIPMETER_CSU_FIELD_TAPE.size == DIPMETER_LIS_SIZE_234)
assert(len(STRUCT_RC_DIPMETER_CSU_FIELD_TAPE.unpack(b' ' * STRUCT_RC_DIPMETER_CSU_FIELD_TAPE.size)) == DIPMETER_LIS_SIZE_234)

# Dipmeter fast sub-channel offset ranges
DIPMETER_FAST_SUB_CHANNEL_RANGES = [
    range(sc, DIPMETER_SIZE_FAST_CHANNELS, DIPMETER_NUM_FAST_CHANNELS)
        for sc in range(DIPMETER_NUM_FAST_CHANNELS)
]

# NOTE: Sc=5 corresponds to index 0 in this list
DIPMETER_SLOW_SUB_CHANNEL_RANGES = [
    range(sc+DIPMETER_FAST_CHANNEL_SUPER_SAMPLES*DIPMETER_NUM_FAST_CHANNELS,
          sc+1+DIPMETER_FAST_CHANNEL_SUPER_SAMPLES*DIPMETER_NUM_FAST_CHANNELS,
          1)
        for sc in range(DIPMETER_NUM_SLOW_CHANNELS)
]

# NOTE: Slow sub channels in their correct index position
DIPMETER_SUB_CHANNEL_RANGES = DIPMETER_FAST_SUB_CHANNEL_RANGES + DIPMETER_SLOW_SUB_CHANNEL_RANGES

# Dipmeter fast sub-channel offset slices
DIPMETER_FAST_SUB_CHANNEL_SLICES = [
    slice(sc, DIPMETER_SIZE_FAST_CHANNELS, DIPMETER_NUM_FAST_CHANNELS)
        for sc in range(DIPMETER_NUM_FAST_CHANNELS)
]

# NOTE: Index 0 is Sc=5 in this list
DIPMETER_SLOW_SUB_CHANNEL_SLICES = [
    slice(sc+DIPMETER_FAST_CHANNEL_SUPER_SAMPLES*DIPMETER_NUM_FAST_CHANNELS,
          sc+1+DIPMETER_FAST_CHANNEL_SUPER_SAMPLES*DIPMETER_NUM_FAST_CHANNELS,
          1)
        for sc in range(DIPMETER_NUM_SLOW_CHANNELS)
]

# NOTE: Slow sub channels in their correct index position
DIPMETER_SUB_CHANNEL_SLICES = DIPMETER_FAST_SUB_CHANNEL_SLICES + DIPMETER_SLOW_SUB_CHANNEL_SLICES

#print()
#print('DIPMETER_FAST_SUB_CHANNEL_RANGES', DIPMETER_FAST_SUB_CHANNEL_RANGES)
#print('DIPMETER_SLOW_SUB_CHANNEL_RANGES', DIPMETER_SLOW_SUB_CHANNEL_RANGES)
#print('DIPMETER_SUB_CHANNEL_RANGES', DIPMETER_SUB_CHANNEL_RANGES)

# This maps each ordinal value to the (suCh, sa, bu)
# (
#     (0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0), (4, 0, 0),
#     (0, 1, 0), (1, 1, 0), (2, 1, 0), (3, 1, 0), (4, 1, 0),
#     ...
#     (0, 15, 0), (1, 15, 0), (2, 15, 0), (3, 15, 0), (4, 15, 0),
#     (5, 0, 0), (6, 0, 0), (7, 0, 0), (8, 0, 0), (9, 0, 0), (10, 0, 0), (11, 0, 0), (12, 0, 0), (13, 0, 0), (14, 0, 0)
# )
DIPMETER_VALUE_MAPPER = tuple(
    [(sc, sa, 0) for sa in range(DIPMETER_FAST_CHANNEL_SUPER_SAMPLES) for sc in range(DIPMETER_NUM_FAST_CHANNELS)]
    + [(sc, 0, 0) for sc in range(DIPMETER_NUM_FAST_CHANNELS, DIPMETER_NUM_FAST_CHANNELS+DIPMETER_NUM_SLOW_CHANNELS)]
)
assert(len(DIPMETER_VALUE_MAPPER) == 90)
#for r in DIPMETER_FAST_SUB_CHANNEL_RANGES:
#    print(list(r))

#Sanity checks
assert(len(DIPMETER_FAST_SUB_CHANNEL_RANGES) == DIPMETER_NUM_FAST_CHANNELS)
assert(list(DIPMETER_FAST_SUB_CHANNEL_RANGES[0]) == [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75])
assert(list(DIPMETER_FAST_SUB_CHANNEL_RANGES[1]) == [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56, 61, 66, 71, 76])
assert(list(DIPMETER_FAST_SUB_CHANNEL_RANGES[2]) == [2, 7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 72, 77])
assert(list(DIPMETER_FAST_SUB_CHANNEL_RANGES[3]) == [3, 8, 13, 18, 23, 28, 33, 38, 43, 48, 53, 58, 63, 68, 73, 78])
assert(list(DIPMETER_FAST_SUB_CHANNEL_RANGES[4]) == [4, 9, 14, 19, 24, 29, 34, 39, 44, 49, 54, 59, 64, 69, 74, 79])
# Slow channels, note index starts at 0
assert(len(DIPMETER_SLOW_SUB_CHANNEL_RANGES) == DIPMETER_NUM_SLOW_CHANNELS)
assert(list(DIPMETER_SLOW_SUB_CHANNEL_RANGES[0]) == [80,])
assert(list(DIPMETER_SLOW_SUB_CHANNEL_RANGES[1]) == [81,])
assert(list(DIPMETER_SLOW_SUB_CHANNEL_RANGES[2]) == [82,])
assert(list(DIPMETER_SLOW_SUB_CHANNEL_RANGES[3]) == [83,])
assert(list(DIPMETER_SLOW_SUB_CHANNEL_RANGES[4]) == [84,])
assert(list(DIPMETER_SLOW_SUB_CHANNEL_RANGES[5]) == [85,])
assert(list(DIPMETER_SLOW_SUB_CHANNEL_RANGES[6]) == [86,])
assert(list(DIPMETER_SLOW_SUB_CHANNEL_RANGES[7]) == [87,])
assert(list(DIPMETER_SLOW_SUB_CHANNEL_RANGES[8]) == [88,])
assert(list(DIPMETER_SLOW_SUB_CHANNEL_RANGES[9]) == [89,])
# All channels, ranges
assert(len(DIPMETER_SUB_CHANNEL_RANGES) == DIPMETER_NUM_FAST_CHANNELS+DIPMETER_NUM_SLOW_CHANNELS)
assert(list(DIPMETER_SUB_CHANNEL_RANGES[0]) == [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75])
assert(list(DIPMETER_SUB_CHANNEL_RANGES[1]) == [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56, 61, 66, 71, 76])
assert(list(DIPMETER_SUB_CHANNEL_RANGES[2]) == [2, 7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 72, 77])
assert(list(DIPMETER_SUB_CHANNEL_RANGES[3]) == [3, 8, 13, 18, 23, 28, 33, 38, 43, 48, 53, 58, 63, 68, 73, 78])
assert(list(DIPMETER_SUB_CHANNEL_RANGES[4]) == [4, 9, 14, 19, 24, 29, 34, 39, 44, 49, 54, 59, 64, 69, 74, 79])
assert(list(DIPMETER_SUB_CHANNEL_RANGES[5]) == [80,])
assert(list(DIPMETER_SUB_CHANNEL_RANGES[6]) == [81,])
assert(list(DIPMETER_SUB_CHANNEL_RANGES[7]) == [82,])
assert(list(DIPMETER_SUB_CHANNEL_RANGES[8]) == [83,])
assert(list(DIPMETER_SUB_CHANNEL_RANGES[9]) == [84,])
assert(list(DIPMETER_SUB_CHANNEL_RANGES[10]) == [85,])
assert(list(DIPMETER_SUB_CHANNEL_RANGES[11]) == [86,])
assert(list(DIPMETER_SUB_CHANNEL_RANGES[12]) == [87,])
assert(list(DIPMETER_SUB_CHANNEL_RANGES[13]) == [88,])
assert(list(DIPMETER_SUB_CHANNEL_RANGES[14]) == [89,])
# All channels, slices
assert(len(DIPMETER_SUB_CHANNEL_SLICES) == DIPMETER_NUM_FAST_CHANNELS+DIPMETER_NUM_SLOW_CHANNELS)
for __i in range(DIPMETER_NUM_FAST_CHANNELS+DIPMETER_NUM_SLOW_CHANNELS):
    assert(
        list(range(
                DIPMETER_SUB_CHANNEL_SLICES[__i].start,
                DIPMETER_SUB_CHANNEL_SLICES[__i].stop,
                DIPMETER_SUB_CHANNEL_SLICES[__i].step
            )) == list(DIPMETER_SUB_CHANNEL_RANGES[__i])
    )

#######################################################
# End: Dipmeter Representation Codes and structure.
#######################################################


# Repcode min and max values.
# ===========================
# Integer rep codes
RC_56_MIN    = -128
RC_56_MAX    = 127

RC_66_MIN    = 0
RC_66_MAX    = 255

# RepCode 70 is 32 bits with a 16 bit integer and a 16 bit
# fractional part
RC_70_MIN    = -32768.0    # 0x80000000
# max code 70 is max +int plus fractional part = 1 - 2^-16
# i.e. 0x7FFFFFFF
RC_70_MAX    = 32767.0 + (1.0 - 1.0 / 65536.0)

# This is a wield way of doing it but
# cdef const int RC_73_MIN    = -2147483648L
# generates a warning about C90
RC_73_MIN    = -2147483647 - 1
RC_73_MAX    = 2147483647

RC_77_MIN    = 0
RC_77_MAX    = 255

RC_79_MIN    = -32768
RC_79_MAX    = 32767

# Floating point rep codes
# Given Bm mantissa (significand) bits and E the largest exponent:
# Min: ldexp(-1, E)
# Max: ldexp(1 - 1.0 /(1 << (Bm-1)), E)

# Equivalent to 0x800F
RC_49_MIN = -32768.0 # ldexp(-0.5, 16) or ldexp(-1, 15)
RC_49_MIN = math.ldexp(-0.5, 16) #or ldexp(-1, 15)
# Equivalent to 0x7FFF
RC_49_MAX = 32752.0 # ldexp(1-1.0/(1<<11), 15) or ldexp(1-1.0/2048, 15)
RC_49_MAX = math.ldexp(1 - 1.0/ (1 << 11), 15) #or ldexp( 1 - 1.0/2048, 15)

# This is smallest double: -8.98846567431158e+307
# Encodes as 0x7FFF8000
RC_50_MIN =  math.ldexp(-0.5, 1024)
# This is largest double: 8.98819136810814e+307
# Encodes as 0x7FFF7FFF
RC_50_MAX =  math.ldexp(0.4999847412109375, 1024)

# Equivalent to 0xFFC00000
RC_68_MIN = math.ldexp(-1.0, 127)
# Equivalent to 0x7FFFFFFF
RC_68_MAX = math.ldexp(1 - 1.0 / (1 << 23), 127)

RC_68_CODE_MIN = 0xFFC00000
RC_68_CODE_MAX = 0x7FFFFFFF
RC_68_CODE_ZERO = 0x40000000

# Smallest non-zero values
# ------------------------
# The very smallest value is 0x00000001 that has just one bit of mantissa set.
# This converts to 3.503246160812043e-46
# Then evaluating that gives:
# >>> math.frexp(3.503246160812043e-46)
# (0.5, -150)
# or (1.0, -151)
# So that is OK but anything with an exponent -151 or less we treat as zero
# i.e. exponent from math.frexp() <= -(128+23)
# Absolute smallest possible positive value with just a single bit of mantissa
# 3.503246160812043e-46
RC_68_SPV = math.ldexp(1, -(128+23))
# Absolute smallest possible negative value with just a single bit of mantissa
# -3.503246160812043e-46
RC_68_SNV = math.ldexp(-1, -(128+23))
# Incidentally the smallest value with a full resolution mantissa is exp=-128

RC_SIZE_MAP = {
    49 : RC_49_SIZE,
    50 : RC_50_SIZE,
    56 : RC_56_SIZE,
    65 : RC_65_SIZE,
    66 : RC_66_SIZE,
    68 : RC_68_SIZE,
    70 : RC_70_SIZE,
    73 : RC_73_SIZE,
    77 : RC_77_SIZE,
    79 : RC_79_SIZE,
    130 : RC_130_SIZE,
    234 : RC_234_SIZE,
}

RC_MIN_MAP = {
    49 : RC_49_MIN,
    50 : RC_50_MIN,
    56 : RC_56_MIN,
    66 : RC_66_MIN,
    68 : RC_68_MIN,
    70 : RC_70_MIN,
    73 : RC_73_MIN,
    77 : RC_77_MIN,
    79 : RC_79_MIN,
}

RC_MAX_MAP = {
    49 : RC_49_MAX,
    50 : RC_50_MAX,
    56 : RC_56_MAX,
    66 : RC_66_MAX,
    68 : RC_68_MAX,
    70 : RC_70_MAX,
    73 : RC_73_MAX,
    77 : RC_77_MAX,
    79 : RC_79_MAX,
}

#######################################################
# Section: Struct for unpacking byte() arrays to words.
# Note: For floats these pull out signed integer words.
#######################################################

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

STRUCT_RC_49 = STRUCT_RC_INT_2
STRUCT_RC_50 = STRUCT_RC_INT_4
STRUCT_RC_56 = STRUCT_RC_INT_1
STRUCT_RC_66 = STRUCT_RC_UINT_1
STRUCT_RC_68 = STRUCT_RC_UINT_4 # Must match the return type of the Cython code: cdef unsigned int
STRUCT_RC_70 = STRUCT_RC_INT_4
STRUCT_RC_73 = STRUCT_RC_INT_4
STRUCT_RC_77 = STRUCT_RC_UINT_1
STRUCT_RC_79 = STRUCT_RC_INT_2

###################################################
# End: Struct for unpacking byte() arrays to words.
###################################################

def isInt(r):
    """Returns True if the Rep Code is represented by an integer."""
    return r in (56, 66, 73, 77, 79)

def lisSize(r):
    """Returns the size in bytes for a single instance of a representation code.
    Zero means variable length. May raise ExceptionRepCodeUnknown."""
    try:
        return RC_SIZE_MAP[r]
    except KeyError:
        raise ExceptionRepCodeUnknown('Unknown representation code: {:s}'.format(str(r)))

def wordLength(r):
    """Returns the word length in bytes used by a representation code.
    NOTE: This is subtly different from lisSize as it take into account dipmeter
    sub-channels
    Zero means variable length. May raise ExceptionRepCodeUnknown."""
    if r == DIPMETER_EDIT_TAPE_REP_CODE or r == DIPMETER_CSU_FIELD_TAPE_REP_CODE:
        return 1
    return lisSize(r)

def maxValue(r):
    """Returns the maximum value for various representation codes.
    May raise ExceptionRepCodeUnknown."""
    try:
        return RC_MAX_MAP[r]
    except KeyError:
        raise ExceptionRepCodeUnknown('Unknown representation code: {:s}'.format(str(r)))
    
def minValue(r):
    """Returns the minimum value for various representation codes.
    May raise ExceptionRepCodeUnknown."""
    try:
        return RC_MIN_MAP[r]
    except KeyError:
        raise ExceptionRepCodeUnknown('Unknown representation code: {:s}'.format(str(r)))

def minMaxValue(r):
    """Returns a pair; (minimum value, maximum value) for various
    representation codes. May raise ExceptionRepCodeUnknown."""
    return minValue(r), maxValue(r)

################################
# Section: Python reference code
################################

#============================================================
# Section: Representation Code 49, 0x31, 16bit floating point
#============================================================
def from49(theWord):
    """Returns a double from Rep code 49 0x31, 16bit floating point representation.
    Value +153 is 0100 1100 1000 1000 or 0x4C88.
    Value -153 is 1011 0011 1000 1000 or 0xB388.
    """
    m = theWord & 0xFFF0
    if theWord & 0x8000:
        # Negative
        m -= 0x10000
    # Divisor is 2^15 as right 4 bits are zero i.e. 2^11 * 2^4
    return math.ldexp(m / (1.0 * (1<<15)), theWord & 0xF)

def to49(theVal):
    """Converts a double to Rep code 49 0x31, 16bit floating point representation.
    Value +153 is 0100 1100 1000 1000 or 0x4C88.
    Value -153 is 1011 0011 1000 1000 or 0xB388.
    """
    assert(0)
#===============================================================================
#    # TODO: Check this
#    # TODO: Overflow and underflow
#    w = 0
#    m, e = math.frexp(theVal)
#    #print
#    #print 'to49()', m, e
#    #m = m * 2 + 1
#    #print 'to49()', m, e
#    m *= 1 << 11
#    #print 'to49()', m, e
#    #print 'to49() 0x%x' % m
#    #m = int(m)
#    w = 0
#    #print
#    if e > 15:
#        m *= 2
#        e -= 1
#    #print 'to49(%f)' % theVal, m, e
#    #print 'to49(%f) 0x%X 0x%X' % (theVal, m, e)
#    w |= int(m) & 0xFFF
#    #print 'w 0x%X' % w
#    w <<= 4
#    #print 'w 0x%X' % w
#    w |= e & 0xF
#    #print 'w 0x%X' % w
#    return w
#===============================================================================

def read49(theFile):
    """Returns a Representation Code 49 value from a File object."""
    return from49(theFile.unpack(STRUCT_RC_49)[0])
#============================================================
# End: Representation Code 49, 0x31, 16bit floating point
#============================================================
    
#============================================================
# Section: Representation Code 50, 0x32, 32bit floating point
#============================================================
def from50(theWord):
    """Returns a double from Rep code 0x32, 32bit floating point representation.
    Value +153 is 0x00084C80
    Value -153 is 0x0008B380"""
    #mant = float(theWord & 0xFFFF) / (1 << 15)
    #exp = (theWord >> 16 )& 0xFFFF
    # Or:
    mant = theWord & 0xFFFF
    # Only take 10 bits of exponent as significant as IEEE-754
    exp = (theWord >> 16 )& 0x03FF
    # Need to divide mantissa by 1 << 15 or 32768 but
    # instead we reduce the exponent by 15
    exp -= 15
    if theWord & 0x8000:
        mant -= 0x10000
    if theWord & 0x80000000:
        exp -= 0x10000
    return math.ldexp(mant, exp)

def to50(theVal):
    """Converts a double to Rep code 0x32, 32bit floating point representation."""
    # TODO: Finish this
    # TODO: Overflow and underflow
    assert(0)
    return 0.0

def read50(theFile):
    """Returns a Representation Code 50 value from a File object."""
    return from50(theFile.unpack(STRUCT_RC_50)[0])
#============================================================
# End: Representation Code 50, 0x32, 32bit floating point
#============================================================
    
#===================================================
# Section: Representation Code 56, 0x38, signed char
#===================================================
def from56(theWord):
    """Returns an integer from Rep code 0x38, signed char representation."""
    if theWord & 0x80:
        # Negative
        return (theWord & 0xFF) - 0x100
    # Positive
    return theWord & 0xFF

def to56(theVal):
    """Converts a double to Rep code 0x38, signed char representation."""
    # TODO: Finish this
    # TODO: Overflow and underflow
    assert(0)
    return 0.0

def read56(theFile):
    """Returns a Representation Code 56 value from a File object."""
    return theFile.unpack(STRUCT_RC_56)[0]
#===================================================
# End: Representation Code 56, 0x38, signed char
#===================================================
    
#=====================================================
# Section: Representation Code 66, 0x42, unsigned byte
#=====================================================
def from66(theWord):
    """Returns a Rep code 0x42, unsigned byte from theWord, expected to be an integer."""
    return theWord & 0xFF

def to66(theVal):
    """Converts theVal to representation code 66 integer from theWord."""
    return theVal
    #return int(theVal) & 0xff

def read66(theFile):
    """Returns a Representation Code 66 value from a File object."""
    return theFile.unpack(STRUCT_RC_66)[0]
#=====================================================
# End: Representation Code 66, 0x42, unsigned byte
#=====================================================

#============================================================
# Section: Representation Code 68, 0x44, 32bit floating point
#============================================================
def from68(theWord):
    """Returns a double from a Rep code 68 word (a 32 bit integer)."""
    #>>> v = 0xBBB38000
    #>>> m = v & 0x80000000
    #>>> if m:
    #...   m = -m
    #...
    #>>> m >>= 8
    #>>> m |= v & 0x007FFFFF
    #>>> e = v & 0x7F800000
    #>>> e >>= 23
    #>>> e = 104-e
    #>>> math.ldexp(m, e)
    #-153.0
    mant = theWord & 0x80000000
    isNeg = mant != 0
    if isNeg:
        mant *= -1
    mant >>= 8
    mant |= theWord & 0x007FFFFF
    exp = theWord & 0x7F800000
    exp >>= 23
    #print('pRepCode() was:', '0x{:X}'.format(mant), '0x{:X}'.format(exp))
    # NOTE: At this stage the mantissa is an integer
    # and needs to be divided by 2^23 to get the fractional value.
    # For efficiency we do not do this but instead adjust the exponent.
    # If the mantissa was the correct fractional value the next line
    # should be exp = (mant & 0x80000000) ? (127 - exp) : (exp - 128);
    # instead we use the numbers 104 and 151 i.e. subtracting 23
    if isNeg:
        exp = 104 - exp
    else:
        exp -= 151
    #print('pRepCode() now:', '0x{:X}'.format(mant), '0x{:X}'.format(exp))
    return math.ldexp(mant, exp)

def to68(v):
    """Returns Representation code 68 as a 32 bit integer from a double."""
    #logging.debug('pRepCode.to68({:g})'.format(v))
    mant, exp = math.frexp(v)
    #print('\nto68() v=%g, mant=%f, exp=%f' % (v, mant, exp))    
    logging.debug('pRepCode.to68() v=%g, mant=%f, exp=%f' % (v, mant, exp))    
    # Overflow and underflow control
    if exp <= -(128+23):
        #print('to68(): exp<0: v=%g, mant=%f, exp=%f' % (v, mant, exp))
        logging.debug('pRepCode.to68() clamping to zero.') 
        # Set zero
        return RC_68_CODE_ZERO
    elif exp > 127:
        #print('to68(): exp>255: v=%g, mant=%f, exp=%f' % (v, mant, exp)) 
        # Set minimum or maximum
        if v < 0:
            logging.debug('pRepCode.to68() clamping to maximum -ve.') 
            return RC_68_CODE_MIN
        logging.debug('pRepCode.to68() clamping to maximum +ve.') 
        return RC_68_CODE_MAX
    # If exponent is <128 then reduce mantissa by excess 128
    if exp < -128:
        mant /= 2**(-128 - exp)
        logging.debug('pRepCode.to68() depressing mantissa by 2**{:d} to {:g}'.format(-128-exp, mant)) 
        exp = -128
    # Set exponent as excess 128
    if v < 0.0:
        exp = 127 - exp
        # Set sign bit
        w = 1
    else:
        exp -= 128
        w = 0
    # Shift for exponent
    w <<= 8
    assert(exp <= 0xFF)
    w |= exp & 0xFF
    # Shift for mantissa
    w <<= 23
    mant *= 1<<23
    m = (int(mant)) & 0x007FFFFF
    w |= m
    #print 'to68(): exp=0x%X, m=0x%X, w=0x%X' % (exp, m, w)
    logging.debug('pRepCode.to68() returning 0x{:08x}'.format(w)) 
    return w

def read68(theFile):
    """Returns a Representation Code 68 value from a File object."""
    return from68(theFile.unpack(STRUCT_RC_68)[0])
#============================================================
# End: Representation Code 68, 0x44, 32bit floating point
#============================================================
    
#=========================================================
# Section: Representation Code 70, 0x46, 32bit fixed point
#=========================================================
def from70(theWord):
    """Returns a double from a Rep code 0x46, 32bit fixed point."""
    retVal = (theWord >> 16) & 0xFFFF
    retVal += float(theWord & 0xFFFF) / (1 << 16)
    if theWord & 0x80000000:
        retVal -= 0x10000
    return retVal

def to70(v):
    """Returns Rep code 0x46, 32bit fixed point from an int or double."""
    # TODO: Finish this
    # TODO: Overflow and underflow
    assert(0)
    return 0.0

def read70(theFile):
    """Returns a Representation Code 70 value from a File object."""
    return from70(theFile.unpack(STRUCT_RC_70)[0])
#=========================================================
# Section: Representation Code 70, 0x46, 32bit fixed point
#=========================================================

#============================================================
# Section: Representation Code 73, 0x49, 32bit signed integer
#============================================================
def from73(theWord):
    """Returns a integer from a Rep code 0x49, 32bit signed integer."""
    #if theWord & 0x80000000:
    #    return theWord
    return theWord# & 0xFFFFFFFF

def to73(v):
    """Returns Rep code 0x49, 32bit signed integer from an int or double."""
    # TODO: Finish this
    # TODO: Overflow and underflow
    return v

def read73(theFile):
    """Returns a Representation Code 73 value from a File object."""
    return theFile.unpack(STRUCT_RC_73)[0]
#============================================================
# End: Representation Code 73, 0x49, 32bit signed integer
#============================================================

#=================================================
# Section: Representation Code 77, 0x4D, 8bit mask
#=================================================
def from77(theWord):
    """Returns a Rep code 0x4D, 8bit mask from theWord, expected to be an integer."""
    return theWord & 0xFF

def to77(theVal):
    """Converts theVal to Rep code 0x4D, 8bit mask from theVal."""
    return int(theVal) & 0xff

def read77(theFile):
    """Returns a Representation Code 77 value from a File object."""
    return theFile.unpack(STRUCT_RC_77)[0]
#=================================================
# Section: Representation Code 77, 0x4D, 8bit mask
#=================================================

#============================================================
# Section: Representation Code 79, 0x4F, 16bit signed integer
#============================================================
def from79(theWord):
    """Returns an integer from Rep code 0x4F, 16bit signed integer."""
    #if theWord > 0x7FFF:
    #    # Negative
    #    return (theWord & 0xFFFF) - 0x10000
    ## Positive
    return theWord# & 0xFFFF

def to79(theVal):
    """Converts a double to Rep code 0x4F, 16bit signed integer."""
    # TODO: Finish this
    # TODO: Overflow and underflow
    assert(0)
    return 0.0

def read79(theFile):
    """Returns a Representation Code 79 value from a File object."""
    return theFile.unpack(STRUCT_RC_79)[0]
#============================================================
# End: Representation Code 79, 0x4F, 16bit signed integer
#============================================================

#############################
# End: Python reference code.
#############################
