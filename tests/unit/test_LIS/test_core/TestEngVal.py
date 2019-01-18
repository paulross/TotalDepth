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
"""Unit tests for the LogicalData module.
"""

__author__  = 'Paul Ross'
__date__    = '8 Nov 2010'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2010 Paul Ross.'

#import pprint
import sys
import time
import logging
import io

from TotalDepth.LIS.core import EngVal
from TotalDepth.LIS.core import Units

######################
# Section: Unit tests.
######################
import unittest

class TestEngVal(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestEngVal.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestEngVal.test_01(): Basic class functionality."""
        myEv = EngVal.EngVal(1.0, b'S   ')
        self.assertFalse(myEv.dimensionless())
        #myEv2 = EngVal.EngVal(1000.0, b'mS  ')
        
    def test_02(self):
        """TestEngVal.test_02(): __str__()."""
        myEv = EngVal.EngVal(1.0, b'S   ')
        self.assertEqual('EngVal: 1.0 (S   )', str(myEv))
        
    def test_03(self):
        """TestEngVal.test_03(): __str__() dimensionless."""
        myEv = EngVal.EngVal(1.0, EngVal.DIMENSIONLESS)
        self.assertEqual('EngVal: 1.0', str(myEv))
        
    def test_04(self):
        """TestEngVal.test_04(): strFmt()."""
        myEv = EngVal.EngVal(1.0, b'S   ')
        self.assertEqual('EngVal: 1.000 (S   )', myEv.strFormat('{:.3f}'))
        self.assertEqual('1.000 (S   )', myEv.strFormat('{:.3f}', incPrefix=False))
        
    def test_05(self):
        """TestEngVal.test_0f(): strFmt() dimensionless."""
        myEv = EngVal.EngVal(1.0, EngVal.DIMENSIONLESS)
        self.assertEqual('EngVal: 1.000', myEv.strFormat('{:.3f}'))
        
    def test_10(self):
        """TestEngVal.test_10(): Unit conversion."""
        myEv = EngVal.EngVal(1.0, b'S   ')
        myEv.convert(b'MS  ')
        #print(myEv)
        self.assertEqual(EngVal.EngVal(1.0, b'S   '), myEv)
        self.assertEqual(EngVal.EngVal(1000.0, b'MS  '), myEv)
        self.assertEqual(1000.0, myEv.getInUnits(b'MS  '))

    def test_11(self):
        """TestEngVal.test_11(): Unit conversion by getInUnits()."""
        myEv = EngVal.EngVal(1.0, b'S   ')
        self.assertEqual(1000.0, myEv.getInUnits(b'MS  '))
        myEv.convert(b'MS  ')
        self.assertEqual(1000.0, myEv.getInUnits(b'MS  '))
        
    def test_20_00(self):
        """TestEngVal.test_20_00(): add with unit conversion."""
        myEv = EngVal.EngVal(1.0, b'S   ') + EngVal.EngVal(1.0, b'S   ')
        self.assertTrue(EngVal.EngVal(2.0, b'S   ') == myEv)
        myEv = EngVal.EngVal(1000.0, b'MS  ') + EngVal.EngVal(1.0, b'S   ')
        self.assertTrue(EngVal.EngVal(2.0, b'S   ') == myEv)
    
    def test_20_01(self):
        """TestEngVal.test_20_01(): add with real numbers."""
        self.assertEqual(EngVal.EngVal(2.0, b'S   '), EngVal.EngVal(1.0, b'S   ') + 1)
        self.assertEqual(EngVal.EngVal(2.0, b'S   '), EngVal.EngVal(1.0, b'S   ') + 1.0)

    def test_20_02(self):
        """TestEngVal.test_20_02(): add fails."""
        try:
            EngVal.EngVal(1.0, b'S   ') + '1'
            self.fail('TypeError not raised.')
        except TypeError:
            pass
        try:
            EngVal.EngVal(1.0, b'S   ') + '1.0'
            self.fail('TypeError not raised.')
        except TypeError:
            pass

    def test_21_00(self):
        """TestEngVal.test_21_00(): subtract with unit conversion."""
        myEv = EngVal.EngVal(4.0, b'S   ') - EngVal.EngVal(1.0, b'S   ')
        self.assertTrue(EngVal.EngVal(3.0, b'S   ') == myEv)
        myEv = EngVal.EngVal(4000.0, b'MS  ') - EngVal.EngVal(1.0, b'S   ')
        self.assertTrue(EngVal.EngVal(3.0, b'S   ') == myEv)

    def test_21_01(self):
        """TestEngVal.test_21_01(): subtract with real numbers."""
        self.assertEqual(EngVal.EngVal(2.0, b'S   '), EngVal.EngVal(3.0, b'S   ') - 1)
        self.assertEqual(EngVal.EngVal(2.0, b'S   '), EngVal.EngVal(3.0, b'S   ') - 1.0)

    def test_21_02(self):
        """TestEngVal.test_21_02(): subtract fails."""
        try:
            EngVal.EngVal(1.0, b'S   ') - '1'
            self.fail('TypeError not raised.')
        except TypeError:
            pass
        try:
            EngVal.EngVal(1.0, b'S   ') - '1.0'
            self.fail('TypeError not raised.')
        except TypeError:
            pass

    def test_22_00(self):
        """TestEngVal.test_22_00(): += with unit conversion."""
        myEv = EngVal.EngVal(1.0, b'S   ')
        myEv += EngVal.EngVal(1.0, b'S   ')
        self.assertTrue(EngVal.EngVal(2.0, b'S   ') == myEv)
        myEv = EngVal.EngVal(1000.0, b'MS  ')
        myEv += EngVal.EngVal(1.0, b'S   ')
        self.assertTrue(EngVal.EngVal(2.0, b'S   ') == myEv)

    def test_22_01(self):
        """TestEngVal.test_22_01(): += with real numbers."""
        myEv = EngVal.EngVal(1.0, b'S   ')
        myEv += 1
        self.assertEqual(EngVal.EngVal(2.0, b'S   '), myEv)
        myEv = EngVal.EngVal(1.0, b'S   ')
        myEv += 1.0
        self.assertEqual(EngVal.EngVal(2.0, b'S   '), myEv)

    def test_22_02(self):
        """TestEngVal.test_22_02(): += fails."""
        myEv = EngVal.EngVal(1.0, b'S   ')
        try:
            myEv += '1'
            self.fail('TypeError not raised.')
        except TypeError:
            pass
        myEv = EngVal.EngVal(1.0, b'S   ')
        try:
            myEv += '1.0'
            self.fail('TypeError not raised.')
        except TypeError:
            pass

    def test_23_00(self):
        """TestEngVal.test_23_00(): -= with unit conversion."""
        myEv = EngVal.EngVal(4.0, b'S   ')
        myEv -= EngVal.EngVal(1.0, b'S   ')
        self.assertTrue(EngVal.EngVal(3.0, b'S   ') == myEv)
        myEv = EngVal.EngVal(4000.0, b'MS  ')
        myEv -= EngVal.EngVal(1.0, b'S   ')
        self.assertTrue(EngVal.EngVal(3.0, b'S   ') == myEv)

    def test_23_01(self):
        """TestEngVal.test_23_01(): -= with real numbers."""
        myEv = EngVal.EngVal(3.0, b'S   ')
        myEv -= 1
        self.assertEqual(EngVal.EngVal(2.0, b'S   '), myEv)
        myEv = EngVal.EngVal(3.0, b'S   ')
        myEv -= 1.0
        self.assertEqual(EngVal.EngVal(2.0, b'S   '), myEv)

    def test_23_02(self):
        """TestEngVal.test_23_02(): -= fails."""
        myEv = EngVal.EngVal(1.0, b'S   ')
        try:
            myEv -= '1'
            self.fail('TypeError not raised.')
        except TypeError:
            pass
        myEv = EngVal.EngVal(1.0, b'S   ')
        try:
            myEv -= '1.0'
            self.fail('TypeError not raised.')
        except TypeError:
            pass

    def test_24_00(self):
        """TestEngVal.test_24_00(): multiply with dimensionless EngVal."""
        myEv = EngVal.EngVal(4.0, b'S   ') * EngVal.EngVal(7.0, EngVal.DIMENSIONLESS)
        self.assertTrue(EngVal.EngVal(28.0, b'S   ') == myEv)
        myEv = EngVal.EngVal(4000.0, b'MS  ') * EngVal.EngVal(3.0, EngVal.DIMENSIONLESS)
        self.assertTrue(EngVal.EngVal(12.0, b'S   ') == myEv)

    def test_24_01(self):
        """TestEngVal.test_24_01(): multiply with real numbers."""
        self.assertEqual(EngVal.EngVal(6.0, b'S   '), EngVal.EngVal(3.0, b'S   ') * 2)
        self.assertEqual(EngVal.EngVal(6.0, b'S   '), EngVal.EngVal(3.0, b'S   ') * 2.0)

    def test_24_02(self):
        """TestEngVal.test_24_02(): multiply fails."""
        try:
            myEv = EngVal.EngVal(4.0, b'S   ') * EngVal.EngVal(7.0, b'S  ')
            self.fail('TypeError not raised.')
        except TypeError:
            pass
        try:
            EngVal.EngVal(1.0, b'S   ') * '1'
            self.fail('TypeError not raised.')
        except TypeError:
            pass
        try:
            EngVal.EngVal(1.0, b'S   ') * '1.0'
            self.fail('TypeError not raised.')
        except TypeError:
            pass

    def test_25_00(self):
        """TestEngVal.test_25_00(): divide with dimensionless EngVal."""
        myEv = EngVal.EngVal(4.0, b'S   ') / EngVal.EngVal(8.0, EngVal.DIMENSIONLESS)
        self.assertTrue(EngVal.EngVal(0.5, b'S   ') == myEv)
        myEv = EngVal.EngVal(4000.0, b'MS  ') / EngVal.EngVal(2.0, EngVal.DIMENSIONLESS)
        self.assertTrue(EngVal.EngVal(2.0, b'S   ') == myEv)

    def test_25_01(self):
        """TestEngVal.test_25_01(): divide with real numbers."""
        self.assertEqual(EngVal.EngVal(1.5, b'S   '), EngVal.EngVal(3.0, b'S   ') / 2)
        self.assertEqual(EngVal.EngVal(1500.0, b'MS  '), EngVal.EngVal(3.0, b'S   ') / 2.0)

    def test_25_02(self):
        """TestEngVal.test_25_02(): divide fails."""
        try:
            EngVal.EngVal(4.0, b'S   ') / EngVal.EngVal(7.0, b'M   ')
            self.fail('Units.ExceptionUnitsNoUnitInCategory not raised.')
        except Units.ExceptionUnitsNoUnitInCategory:
            pass
        try:
            EngVal.EngVal(1.0, b'S   ') / '1'
            self.fail('TypeError not raised.')
        except TypeError:
            pass
        try:
            EngVal.EngVal(1.0, b'S   ') / '1.0'
            self.fail('TypeError not raised.')
        except TypeError:
            pass

    def test_25_03(self):
        """TestEngVal.test_25_03(): divide with same category dimension produces dimensionless EngVal."""
        # Time example
        myEv = EngVal.EngVal(42.0, b'S   ') / EngVal.EngVal(7.0, b'S   ')
        self.assertTrue(EngVal.EngVal(6.0, EngVal.DIMENSIONLESS) == myEv)
        myEv = EngVal.EngVal(3600.0, b'S   ') / EngVal.EngVal(1.0, b'HR  ')
        self.assertTrue(EngVal.EngVal(1.0, EngVal.DIMENSIONLESS) == myEv)
        self.assertEqual(EngVal.EngVal(1.0, EngVal.DIMENSIONLESS), myEv)
        # Distance example
        myEv = EngVal.EngVal(1.0, b'FEET') / EngVal.EngVal(0.3048, b'M   ')
#        print()
#        print(myEv)
        self.assertTrue(EngVal.EngVal(1.0, EngVal.DIMENSIONLESS) == myEv)
        self.assertEqual(EngVal.EngVal(1.0, EngVal.DIMENSIONLESS), myEv)

    def test_26_00(self):
        """TestEngVal.test_26_00(): *= with dimensionless EngVal."""
        myEv = EngVal.EngVal(3.0, b'S   ')
        myEv *= EngVal.EngVal(5.0, EngVal.DIMENSIONLESS)
        self.assertTrue(EngVal.EngVal(15.0, b'S   ') == myEv)
        myEv = EngVal.EngVal(7000.0, b'MS  ')
        myEv *= EngVal.EngVal(3.0, EngVal.DIMENSIONLESS)
        self.assertTrue(EngVal.EngVal(21.0, b'S   ') == myEv)

    def test_26_01(self):
        """TestEngVal.test_26_01(): *= with real numbers."""
        myEv = EngVal.EngVal(7.0, b'S   ')
        myEv *= 3
        self.assertEqual(EngVal.EngVal(21.0, b'S   '), myEv)
        myEv = EngVal.EngVal(-4.0, b'S   ')
        myEv *= -5.0
        self.assertEqual(EngVal.EngVal(20.0, b'S   '), myEv)

    def test_26_02(self):
        """TestEngVal.test_26_02(): *= fails."""
        myEv = EngVal.EngVal(1.0, b'S   ')
        try:
            myEv = EngVal.EngVal(4.0, b'S   ')
            myEv *= EngVal.EngVal(7.0, b'S  ')
            self.fail('TypeError not raised.')
        except TypeError:
            pass
        try:
            myEv *= '1'
            self.fail('TypeError not raised.')
        except TypeError:
            pass
        myEv = EngVal.EngVal(1.0, b'S   ')
        try:
            myEv *= '1.0'
            self.fail('TypeError not raised.')
        except TypeError:
            pass

    def test_27_00(self):
        """TestEngVal.test_27_00(): /= with dimensionless EngVal."""
        myEv = EngVal.EngVal(15.0, b'S   ')
        myEv /= EngVal.EngVal(5.0, EngVal.DIMENSIONLESS)
        self.assertTrue(EngVal.EngVal(3.0, b'S   ') == myEv)
        myEv = EngVal.EngVal(9000.0, b'MS  ')
        myEv /= EngVal.EngVal(3.0, EngVal.DIMENSIONLESS)
        self.assertTrue(EngVal.EngVal(3.0, b'S   ') == myEv)

    def test_27_01(self):
        """TestEngVal.test_27_01(): /= with real numbers."""
        myEv = EngVal.EngVal(21.0, b'S   ')
        myEv /= 3
        self.assertEqual(EngVal.EngVal(7.0, b'S   '), myEv)
        myEv = EngVal.EngVal(-20.0, b'S   ')
        myEv /= -5.0
        self.assertEqual(EngVal.EngVal(4.0, b'S   '), myEv)

    def test_27_02(self):
        """TestEngVal.test_27_02(): /= fails."""
        myEv = EngVal.EngVal(1.0, b'S   ')
        try:
            myEv = EngVal.EngVal(4.0, b'S   ')
            myEv /= EngVal.EngVal(7.0, b'M   ')
            self.fail('Units.ExceptionUnitsNoUnitInCategory not raised.')
        except Units.ExceptionUnitsNoUnitInCategory:
            pass
        try:
            myEv /= '1'
            self.fail('TypeError not raised.')
        except TypeError:
            pass
        myEv = EngVal.EngVal(1.0, b'S   ')
        try:
            myEv /= '1.0'
            self.fail('TypeError not raised.')
        except TypeError:
            pass
    
    def test_27_03(self):
        """TestEngVal.test_27_03(): /= of same category dimensions results in dimensionless value."""
        myEv = EngVal.EngVal(1.0, b'S   ')
        myEv /= EngVal.EngVal(4.0, b'S   ')
        self.assertEqual(EngVal.EngVal(0.25, EngVal.DIMENSIONLESS), myEv)

    def test_30(self):
        """TestEngVal.test_30(): boolean equivalence."""
        # __eq__()
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') == EngVal.EngVal(1.0, b'S   '))
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') == EngVal.EngVal(1000.0, b'MS  '))
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') == 1.0)
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') == 1)
        self.assertFalse(EngVal.EngVal(1.0, b'S   ') == '1.0')
        # __ne__()
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') != EngVal.EngVal(1.1, b'S   '))
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') != EngVal.EngVal(1001.0, b'MS  '))
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') != 2.0)
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') != 2)
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') != '1.0')
        # __lt__()
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') < EngVal.EngVal(1.1, b'S   '))
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') < EngVal.EngVal(1100.0, b'MS  '))
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') < 1.0001)
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') < 2)
        try:
            EngVal.EngVal(1.0, b'S   ') < '1.0'
            self.fail('TypeError not raised.')
        except TypeError:
            pass
        # __gt__()
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') > EngVal.EngVal(0.9, b'S   '))
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') > EngVal.EngVal(900.0, b'MS  '))
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') > 0.9999)
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') > 0)
        try:
            EngVal.EngVal(1.0, b'S   ') > '1.0'
            self.fail('TypeError not raised.')
        except TypeError:
            pass
        # __le__()
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') <= EngVal.EngVal(1.1, b'S   '))
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') <= EngVal.EngVal(1100.0, b'MS  '))
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') <= 1.0001)
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') <= 1.0)
        self.assertFalse(EngVal.EngVal(1.0, b'S   ') <= 0.9999)
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') <= 2)
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') <= 1)
        self.assertFalse(EngVal.EngVal(1.0, b'S   ') <= 0)
        try:
            EngVal.EngVal(1.0, b'S   ') <= '1.0'
            self.fail('TypeError not raised.')
        except TypeError:
            pass
        # __ge__()
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') >= EngVal.EngVal(0.9, b'S   '))
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') >= EngVal.EngVal(900.0, b'MS  '))
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') >= 0.9999)
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') >= 1.0)
        self.assertFalse(EngVal.EngVal(1.0, b'S   ') >= 1.0001)
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') >= 0)
        self.assertTrue(EngVal.EngVal(1.0, b'S   ') >= 1)
        self.assertFalse(EngVal.EngVal(1.0, b'S   ') >= 2)
        try:
            EngVal.EngVal(1.0, b'S   ') >= '1.0'
            self.fail('TypeError not raised.')
        except TypeError:
            pass

    def test_40(self):
        """TestEngVal.test_40(): newEngValInUnits(), same units."""
        myEv = EngVal.EngVal(1.0, b'S   ')
        self.assertEqual(EngVal.EngVal(1.0, b'S   '), myEv)
        self.assertEqual(EngVal.EngVal(1000.0, b'MS  '), myEv)
        myNewEv = myEv.newEngValInUnits(b'S   ')
        # Check new
        self.assertEqual(1.0, myNewEv.value)
        self.assertEqual(b'S   ', myNewEv.uom)
        self.assertEqual(EngVal.EngVal(1.0, b'S   '), myNewEv)
        self.assertEqual(EngVal.EngVal(1000.0, b'MS  '), myNewEv)
        # Check original untouched
        self.assertEqual(1.0, myEv.value)
        self.assertEqual(b'S   ', myEv.uom)
        self.assertEqual(EngVal.EngVal(1.0, b'S   '), myEv)
        self.assertEqual(EngVal.EngVal(1000.0, b'MS  '), myEv)

    def test_41(self):
        """TestEngVal.test_41(): newEngValInUnits(), different units."""
        myEv = EngVal.EngVal(1.0, b'S   ')
        self.assertEqual(EngVal.EngVal(1.0, b'S   '), myEv)
        self.assertEqual(EngVal.EngVal(1000.0, b'MS  '), myEv)
        myNewEv = myEv.newEngValInUnits(b'MS  ')
        # Check new
        self.assertEqual(1000.0, myNewEv.value)
        self.assertEqual(b'MS  ', myNewEv.uom)
        self.assertEqual(EngVal.EngVal(1.0, b'S   '), myNewEv)
        self.assertEqual(EngVal.EngVal(1000.0, b'MS  '), myNewEv)
        # Check original untouched
        self.assertEqual(1.0, myEv.value)
        self.assertEqual(b'S   ', myEv.uom)
        self.assertEqual(EngVal.EngVal(1.0, b'S   '), myEv)
        self.assertEqual(EngVal.EngVal(1000.0, b'MS  '), myEv)

    def test_42(self):
        """TestEngVal.test_42(): newEngValInUnits() fails."""
        myEv = EngVal.EngVal(1.0, b'S   ')
        self.assertEqual(EngVal.EngVal(1.0, b'S   '), myEv)
        self.assertEqual(EngVal.EngVal(1000.0, b'MS  '), myEv)
        try:
            myNewEv = myEv.newEngValInUnits(b'FEET')
            self.fail('Units.ExceptionUnitsNoUnitInCategory not raised.')
        except Units.ExceptionUnitsNoUnitInCategory:
            pass
        
    def test_50(self):
        """TestEngVal.test_50(): newEngValInOpticalUnits(), same units."""
        myEv = EngVal.EngVal(1.0, b'FEET')
        myNewEv = myEv.newEngValInOpticalUnits()
        # Check new
        self.assertEqual(1.0, myNewEv.value)
        self.assertEqual(b'FEET', myNewEv.uom)

    def test_51(self):
        """TestEngVal.test_51(): newEngValInOpticalUnits(), different units."""
        myEv = EngVal.EngVal(120.0, b'.1IN')
        myNewEv = myEv.newEngValInOpticalUnits()
        # Check new
        self.assertEqual(1.0, myNewEv.value)
        self.assertEqual(b'FEET', myNewEv.uom)

    def test_60(self):
        """TestEngVal.test_60(): pStr(), general format."""
        myEv = EngVal.EngVal(120.0, b'.1IN')
        self.assertEqual('120 (.1IN)', myEv.pStr())

    def test_61(self):
        """TestEngVal.test_61(): pStr() with bytes value."""
        myEv = EngVal.EngVal(b'120.0', b'.1IN')
        self.assertEqual('120.0 (.1IN)', myEv.pStr())
        myEv = EngVal.EngVal(bytes([65,0,66,1]), b'.1IN')
        self.assertEqual('A\x00B\x01 (.1IN)', myEv.pStr())

    def test_62(self):
        """TestEngVal.test_62(): pStr() with bytes value, dimensionless."""
        myEv = EngVal.EngVal(b'120.0')
        self.assertEqual('120.0', myEv.pStr())
        myEv = EngVal.EngVal(bytes([65,0,66,1]))
        self.assertEqual('A\x00B\x01', myEv.pStr())

    def test_63(self):
        """TestEngVal.test_63(): pStr() with string value."""
        myEv = EngVal.EngVal('120.0', b'.1IN')
        self.assertEqual('120.0 (.1IN)', myEv.pStr())

    def test_64(self):
        """TestEngVal.test_64(): pStr() with string value, dimensionless."""
        myEv = EngVal.EngVal('120.0')
        self.assertEqual('120.0', myEv.pStr())

class TestEngValRc(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestEngValRc.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestEngValRc.test_01(): __str__()."""
        myEvr = EngVal.EngValRc(1.0, b'S   ', 68)
        self.assertEqual('EngValRc: 1.0 (S   )', str(myEvr))
        
    def test_02(self):
        """TestEngValRc.test_02(): __str__() dimensionless."""
        myEvr = EngVal.EngValRc(1.0, EngVal.DIMENSIONLESS, 68)
        self.assertEqual('EngValRc: 1.0', str(myEvr))
        
    def test_03(self):
        """TestEngValRc.test_03(): encode()."""
        myEvr = EngVal.EngValRc(1.0, b'S   ', 68)
        self.assertEqual(b'@\xc0\x00\x00', myEvr.encode())
        
    def test_04(self):
        """TestEngValRc.test_04(): encode() fails."""
        myEvr = EngVal.EngValRc(1.0, b'S   ', 0)
        self.assertRaises(EngVal.ExceptionEngVal, myEvr.encode)
        
class TestEngValRval(unittest.TestCase):
    """Tests using rvals that promote numbers to EngVals."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestEngValRval.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestEngValRval.test_01(): Promoting a float to an EngVal with + using __radd__()."""
        v = 8.0 + EngVal.EngVal(1.0, b'S   ')
#        print()
#        print(v)
        self.assertEqual(EngVal.EngVal(9.0, b'S   '), v)
        
    def test_02(self):
        """TestEngValRval.test_02(): Promoting a float to an EngVal with - using __rsub__()."""
        v = 8.0 - EngVal.EngVal(1.0, b'S   ')
#        print()
#        print(v)
        self.assertEqual(EngVal.EngVal(7.0, b'S   '), v)
        
    def test_03(self):
        """TestEngValRval.test_03(): Promoting a float to an EngVal with * using __rmul__()."""
        v = 8.0 * EngVal.EngVal(2.0, b'S   ')
#        print()
#        print(v)
        self.assertEqual(EngVal.EngVal(16.0, b'S   '), v)
        
    def test_04(self):
        """TestEngValRval.test_04(): Promoting a float to an EngVal with / using __rtruediv__()."""
        v = 8.0 / EngVal.EngVal(2.0, b'S   ')
#        print()
#        print(v)
        self.assertEqual(EngVal.EngVal(4.0, b'S   '), v)
        
class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEngVal))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEngValRc))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEngValRval))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestClass.py - A module that tests something.
Usage:
python TestClass.py [-lh --help]

Options:
-h, --help  Help (this screen) and exit

Options (debug):
-l:         Set the logging level higher is quieter.
             Default is 20 (INFO) e.g.:
                CRITICAL    50
                ERROR       40
                WARNING     30
                INFO        20
                DEBUG       10
                NOTSET      0
""")

def main():
    """Invoke unit test code."""
    print(('TestClass.py script version "%s", dated %s' % (__version__, __date__)))
    print(('Author: %s' % __author__))
    print(__rights__)
    print()
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:", ["help",])
    except getopt.GetoptError:
        usage()
        print('ERROR: Invalid options!')
        sys.exit(1)
    logLevel = logging.INFO
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif o == '-l':
            logLevel = int(a)
    if len(args) != 0:
        usage()
        print('ERROR: Wrong number of arguments!')
        sys.exit(1)
    # Initialise logging etc.
    logging.basicConfig(level=logLevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    clkStart = time.perf_counter()
    unitTest()
    clkExec = time.perf_counter() - clkStart
    print(('CPU time = %8.3f (S)' % clkExec))
    print('Bye, bye!')

if __name__ == "__main__":
    main()
