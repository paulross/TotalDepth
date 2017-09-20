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
"""This module handles engineering values i.e. a real numeric value
associated with a unit-of-measure.

Operator Overloading
--------------------

EngVals can be operated on by a real number or an other EngVal.

Addition and subtraction
^^^^^^^^^^^^^^^^^^^^^^^^^^

The operators ``+, -, +=, -=`` work on mixed real numbers and EngVals as expected.
If two EngVal objects then unit conversion is performed before the operation.
If the two EngVals have units in different categories an ExceptionUnit will be raised.

Division
^^^^^^^^^^

Operators ``/, /=`` are implemented.

Division of an EngVal by a real number preserves the EngVal units.

Division of an EngVal by an EngVal results in the following:

* It preserves the EngVal units if the denominator units are DIMENSIONLESS.
* The result will have DIMENSIONLESS EngVal units if the numerator and denominator
    have units that are freely convertible i.e. in the same unit category.
* An ExceptionUnit will be raised.

Multiplication
^^^^^^^^^^^^^^^^

Operators ``*, *=`` are implemented for reals and EngVals.
If an EngVal the units must be DIMENSIONLESS.

Notes
-----
rval operators are implemented and this can result in type promotion.
For example the result of 4.0 * EngVal(16, b'INCH') is an EngVal(64.0, b'INCH').

Created on 24 Nov 2010

EngVal Reference
-------------------
"""

__author__  = 'Paul Ross'
__date__    = '2010-11-24'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

#import logging
import numbers

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import RepCode
from TotalDepth.LIS.core import Units
from TotalDepth.LIS.core import Mnem

DIMENSIONLESS = Mnem.Mnem(b'    ')

class ExceptionEngVal(ExceptionTotalDepthLIS):
    pass

class EngVal(object):
    """Represents an engineering value that consists of a numeric value and a
    unit of measure (usually a string)."""
    def __init__(self, theVal, theUom=DIMENSIONLESS):
        self.value = theVal
        self.uom = theUom
    
    def dimensionless(self):
        """Returns True if the measure is dimensionless."""
        return self.uom == DIMENSIONLESS
    
    def __str__(self):
        """String representation."""
        if self.dimensionless():
            return 'EngVal: {:s}'.format(str(self.value))
        return 'EngVal: {:s} ({:s})'.format(str(self.value), self.uom.decode('ascii'))
    
    def pStr(self):
        """Returns a 'pretty' ASCII string."""
#        print(self.value, self.uom, self.dimensionless())
        if isinstance(self.value, bytes):
            myV = self.value.decode('ascii', 'replace')
        elif isinstance(self.value, str):
            myV = self.value
        else:
            myV = '{:g}'.format(self.value)
        if self.dimensionless():
            return '{:s}'.format(myV)
        return '{:s} ({:s})'.format(myV, self.uom.decode('ascii', 'replace'))
    
    def strFormat(self, theFormat, incPrefix=True):
        """Returns as as string with the value to the specified format (must be
        capable of handling floating point values."""
        if incPrefix:
            fmtStr = 'EngVal: {:s}'.format(theFormat)
        else:
            fmtStr = '{:s}'.format(theFormat)
#        print('fmtStr', fmtStr, type(self.value))
        if self.dimensionless():
            return fmtStr.format(self.value)
        fmtStr += ' ({:s})'
        return fmtStr.format(self.value, self.uom.decode('ascii'))
    
    def __add__(self, other):
        """Overload self+other, returned result has the sum of self and other.
        other can be an EngVal or a Real number.
        The units chosen are self's."""
        if isinstance(other, numbers.Real):
            myVal = other
        elif isinstance(other, EngVal):
            myVal = other.getInUnits(self.uom)
        else:
            return NotImplemented
        return EngVal(self.value + myVal, self.uom)

    def __radd__(self, other):
        """Right value addition, see __add__()."""
        return self + other

    def __sub__(self, other):
        """Overload self-other, returned result has the sum of self and other.
        The units chosen are self's."""
        if isinstance(other, numbers.Real):
            myVal = other
        elif isinstance(other, EngVal):
            myVal = other.getInUnits(self.uom)
        else:
            return NotImplemented
        return EngVal(self.value - myVal, self.uom)
    
    def __rsub__(self, other):
        """Right value subtraction, see __sub__()."""
        return (self - other) * -1

    def __mul__(self, other):
        """Overload self*other. other must be a real number or a dimensionless EngVal."""
        if isinstance(other, numbers.Real):
            return EngVal(self.value * other, self.uom)
        elif isinstance(other, EngVal) and other.uom == DIMENSIONLESS:
            return EngVal(self.value * other.value, self.uom)
        return NotImplemented
        
    def __rmul__(self, other):
        """Right value multiplication, see __mul__()."""
        return self * other

    def __truediv__(self, other):
        """Overload self/other. other must be a real number or an EngVal. If
        the units of other are dimensionless then treat as a real number.
        If the units are in the same category as me convert them and return a
        dimensionless EngVal."""
        if isinstance(other, numbers.Real):
            return EngVal(self.value / other, self.uom)
        elif isinstance(other, EngVal):
            if other.uom == DIMENSIONLESS:
                return EngVal(self.value / other.value, self.uom)
            # Try and convert other units to me and the result is then dimensionless
            return EngVal(self.value / other.getInUnits(self.uom), DIMENSIONLESS)
        return NotImplemented

    def __rtruediv__(self, other):
        """Right value true division, see __truediv__()."""
        retVal = self / other
        retVal.value = 1.0 / retVal.value
        return retVal

    def __iadd__(self, other):
        """Addition in place, other must be a real number or an EngVal where
        it is converted to my units."""
        if isinstance(other, numbers.Real):
            self.value += other
            return self
        elif isinstance(other, EngVal):
            self.value += other.getInUnits(self.uom)
            return self
        return NotImplemented

    def __isub__(self, other):
        """Subtraction in place, other must be a real number or an EngVal where
        it is converted to my units."""
        if isinstance(other, numbers.Real):
            self.value -= other
            return self
        elif isinstance(other, EngVal):
            self.value -= other.getInUnits(self.uom)
            return self
        return NotImplemented

    def __imul__(self, other):
        """Overload self \*= other. other must be a real number or a dimensionless EngVal."""
        if isinstance(other, numbers.Real):
            self.value *= other
            return self
        elif isinstance(other, EngVal) and other.uom == DIMENSIONLESS:
            self.value *= other.value
            return self
        return NotImplemented
        
    def __itruediv__(self, other):
        """Overload self /= other. other must be a real number or a dimensionless EngVal."""
        if isinstance(other, numbers.Real):
            self.value /= other
            return self
        elif isinstance(other, EngVal) and other.uom == DIMENSIONLESS:
            self.value /= other.value
            return self
        return NotImplemented
        
    def __lt__(self, other):
        """True if self < other False otherwise.
        If other is an EngVal unit conversion is performed which may raise an ExceptionUnit.
        If other is a real number then self units are ignored."""
        if isinstance(other, EngVal):
            return self.value < other.getInUnits(self.uom)
        elif isinstance(other, numbers.Real):
            return self.value < other
        return NotImplemented

    def __le__(self, other):
        """True if self <= other False otherwise.
        If other is an EngVal unit conversion is performed which may raise an ExceptionUnit.
        If other is a real number then self units are ignored."""
        if isinstance(other, EngVal):
            return self.value <= other.getInUnits(self.uom)
        elif isinstance(other, numbers.Real):
            return self.value <= other
        return NotImplemented

    def __eq__(self, other):
        """True if self == other False otherwise.
        If other is an EngVal unit conversion is performed which may raise an ExceptionUnit.
        If other is a real number then self units are ignored."""
        if isinstance(other, EngVal):
            return self.value == other.getInUnits(self.uom)
        elif isinstance(other, numbers.Real):
            return self.value == other
        return NotImplemented

    def __ne__(self, other):
        """True if self != other False otherwise.
        If other is an EngVal unit conversion is performed which may raise an ExceptionUnit.
        If other is a real number then self units are ignored."""
        if isinstance(other, EngVal):
            return self.value != other.getInUnits(self.uom)
        elif isinstance(other, numbers.Real):
            return self.value != other
        return NotImplemented

    def __gt__(self, other):
        """True if self > other False otherwise.
        If other is an EngVal unit conversion is performed which may raise an ExceptionUnit.
        If other is a real number then self units are ignored."""
        if isinstance(other, EngVal):
            return self.value > other.getInUnits(self.uom)
        elif isinstance(other, numbers.Real):
            return self.value > other
        return NotImplemented

    def __ge__(self, other):
        """True if self >= other False otherwise.
        If other is an EngVal unit conversion is performed which may raise an ExceptionUnit.
        If other is a real number then self units are ignored."""
        if isinstance(other, EngVal):
            return self.value >= other.getInUnits(self.uom)
        elif isinstance(other, numbers.Real):
            return self.value >= other
        return NotImplemented
    
    def convert(self, theUnits):
        """Convert my value to the supplied units in-place. May raise an ExceptionUnits."""
        if theUnits != self.uom:
            self.value = Units.convert(self.value, self.uom, theUnits)
            self.uom = theUnits

    def getInUnits(self, theUnits):
        """Returns my value to the supplied units. May raise an ExceptionUnits."""
        if theUnits == self.uom:
            return self.value
        return Units.convert(self.value, self.uom, theUnits)

    def newEngValInUnits(self, theUnits):
        """Returns a new EngVal converting me to the supplied units.
        May raise an ExceptionUnits."""
        if theUnits == self.uom:
            return EngVal(self.value, self.uom)
        return EngVal(Units.convert(self.value, self.uom, theUnits), theUnits)

    def newEngValInOpticalUnits(self):
        """Returns a new EngVal converting me to the 'optical' units if possible.
        For example a value in b'.1IN" will be converted to b'FEET'."""
        myUnits = Units.opticalUnits(self.uom)
        if myUnits == self.uom:
            return EngVal(self.value, self.uom)
        return EngVal(Units.convert(self.value, self.uom, myUnits), myUnits)

class EngValRc(EngVal):
    """An engineering value with a integer Representation Code."""
    def __init__(self, theVal, theUom, theRc=None):
        super().__init__(theVal, theUom)
        self.rc = theRc
    
    def __str__(self):
        """String representation."""
        if self.dimensionless():
            return 'EngValRc: {:s}'.format(str(self.value))
        return 'EngValRc: {:s} ({:s})'.format(str(self.value), self.uom.decode('ascii'))
    
    def encode(self):
        """Encode my value to my RepCode returning a bytes object. May raise an ExceptionEngVal."""
        try:
            return RepCode.writeBytes(self.value, self.rc)
            #return RepCode.toRepCode(self.rc, self.value)
        except RepCode.ExceptionRepCode as err:
            raise ExceptionEngVal('EngVal.encode(): {:s}'.format(str(err)))
