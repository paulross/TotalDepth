# -*- mode:python; coding:utf-8; -*-
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
"""Cython module for translating raw LIS to an appropriate internal type for LIS
Representation Codes ('RepCodes').

Internal types are double, int or string.
"""
cdef extern from "math.h":
    double ldexp(double m, int exp)
    double frexp(double v, int *exp)
    double HUGE_VAL


########################################
# Section: Specific Representation Codes
########################################

#================================
# Section: Representation Code 49
#================================
def from49(int theWord):
    cdef int mant = theWord & 0xFFF0
    if theWord & 0x8000:
        # Negative
        mant -= 0x10000
    # Divisor is 2^15 as right 4 bits are zero i.e. 2^11 * 2^4
    return ldexp (mant / 32768.0, theWord & 0x0F)
    
#============================
# End: Representation Code 49
#============================
def from50(signed long long theWord):
    """Returns a double from Rep code 0x32, 32bit floating point representation.
    Value +153 is 0x00084C80
    Value -153 is 0x0008B380"""
    cdef int mant = theWord & 0xFFFF
    # Only take 10 bits of exponent as significant as IEEE-754
    cdef int exp = (theWord >> 16 )& 0x03FF
    # Need to divide mantissa by 1 << 15 or 32768 but
    # instead we reduce the exponent by 15
    exp -= 15
    if theWord & 0x8000:
        mant -= 0x10000
    if theWord & 0x80000000:
        exp -= 0x10000
    return ldexp(mant, exp)

def from56(signed char theWord):
    """Returns a integer from a Rep code 56 word (a 8 bit signed integer)."""
    return theWord

def from66(unsigned char theWord):
    """Returns a integer from a Rep code 66 word (a 8 bit unsigned integer)."""
    return theWord

#================================
# Section: Representation Code 68
#================================
def from68(signed long long theWord):
    """Returns a double from a Rep code 68 word (a 32 bit integer)."""
    cdef signed int mant
    if (theWord & 0x80000000):
        # This is: -0x800000
        # i.e.: -2147483648 >> 8
        # i.e.: (-1 << 31) >> 8
        # i.e.: -1 << (31-8)
        # i.e.: -1 << 23
        mant = -8388608
    else:
        mant = 0
    mant |= theWord & 0x007FFFFF
    cdef int exp = theWord & 0x7F800000
    exp >>= 23
    # NOTE: At this stage the mantissa is an integer
    # and needs to be divided by 2^23 to get the fractional value.
    # For efficiency we do not do this but instead adjust the exponent.
    # If the mantissa was the correct fractional value the next line
    # should be exp = (mant & 0x80000000) ? (127 - exp) : (exp - 128);
    # instead we use the numbers 104 and 151 i.e. subtracting 23
    if (theWord & 0x80000000):
        exp = 104 - exp
    else:
        exp -= 151
    return ldexp(mant, exp)

def to68(double v):
    """Returns Representation code 68 as a 32 bit integer from a double."""
    cdef unsigned int w = 0
    cdef int exp = 0
    cdef double mant = frexp(v, &exp)
    # Overflow and underflow control
    if exp <= -(128+23):
        # Set zero
        return 0x40000000
    elif exp > 127:
        # Set minumum or maximum
        if v < 0:
            # Negative, return minimum
            return 0xFFC00000
        # Positive, return maximum
        return 0x7FFFFFFF
    # If exponent is <128 then reduce mantissa by excess 128
    if exp < -128:
        mant /= 2**(-128 - exp)
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
    w |= exp & 0xFF
    # Shift for mantissa
    w <<= 23
    w |= (<int> (mant * (1<<23))) & 0x007FFFFF
    return w
#============================
# End: Representation Code 68
#============================

def from70(unsigned int theWord):
    cdef double val = (theWord >> 16) & 0xFFFF
    val += (theWord & 0xFFFF) / 65536.0
    if theWord & 0x80000000:
        val -= 0x10000
    return val

def from73(signed int theWord):
    """Returns a integer from a Rep code 73 word (a 32 bit integer)."""
    return theWord#<signed int> theWord

def from77(unsigned char theWord):
    """Returns a integer from a Rep code 77 word (a 8 bit unsigned integer)."""
    return theWord

def from79(signed short int theWord):
    """Returns a integer from a Rep code 79 word (a 16 bit integer)."""
    return theWord

########################################
# End: Specific Representation Codes
########################################


