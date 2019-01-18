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
"""Tests ...
"""

__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

#import pprint
import sys
import time
import logging
#import math
import pprint
#import io

from TotalDepth.LIS.core import EngVal
from TotalDepth.util.plot import Coord
from TotalDepth.util.plot import Stroke
from TotalDepth.util.plot import XGrid
#from TotalDepth.util.plot import Plot

######################
# Section: Unit tests.
######################
import unittest

class TestXGrid(unittest.TestCase):
    """Tests XGrid plotting"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestXGrid.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestXGrid.test_01(): Constructor."""
        myXs = XGrid.XGrid(200)

    def test_01_00(self):
        """TestXGrid.test_01_00(): Constructor with float, string etc. i.e. non-integer fails."""
        self.assertRaises(XGrid.ExceptionPlotXGrid, XGrid.XGrid, 200.0)
        self.assertRaises(XGrid.ExceptionPlotXGrid, XGrid.XGrid, "200")

    def test_02(self):
        """TestXGrid.test_02(): genEvents() with 2/5/10/25, xInc=False."""
        #print()
        myXs = XGrid.XGrid(200)
        v = 0
        eventS = []
        for e in myXs._genEvents(
                xFrom=0,
                xInc=True,
                eMap = {
                    2   : 'two',
                    5   : 'five',
                    10  : 'ten',
                    25  : 'twenty five',
                },
            ):
            #print(e)
            eventS.append(e)
            v += 1
            if v > 25:
                break
        #print()
        #pprint.pprint(eventS)
        self.assertEqual(
            [
                (0, 'twenty five'),
                (2, 'two'),
                (4, 'two'),
                (5, 'five'),
                (6, 'two'),
                (8, 'two'),
                (10, 'ten'),
                (12, 'two'),
                (14, 'two'),
                (15, 'five'),
                (16, 'two'),
                (18, 'two'),
                (20, 'ten'),
                (22, 'two'),
                (24, 'two'),
                (25, 'twenty five'),
                (26, 'two'),
                (28, 'two'),
                (30, 'ten'),
                (32, 'two'),
                (34, 'two'),
                (35, 'five'),
                (36, 'two'),
                (38, 'two'),
                (40, 'ten'),
                (42, 'two')
            ],
            eventS
        )
        
    def test_03(self):
        """TestXGrid.test_03(): genEvents() with 2/5/10/25, xInc=False."""
        #print()
        myXs = XGrid.XGrid(200)
        v = 0
        eventS = []
        for e in myXs._genEvents(
                xFrom=0,
                xInc=False,
                eMap = {
                    2   : 'two',
                    5   : 'five',
                    10  : 'ten',
                    25  : 'twenty five',
                },
            ):
            #print(e)
            eventS.append(e)
            v += 1
            if v > 25:
                break
        #print()
        #pprint.pprint(eventS)
        self.assertEqual(
            [
                (0, 'twenty five'),
                (-2, 'two'),
                (-4, 'two'),
                (-5, 'five'),
                (-6, 'two'),
                (-8, 'two'),
                (-10, 'ten'),
                (-12, 'two'),
                (-14, 'two'),
                (-15, 'five'),
                (-16, 'two'),
                (-18, 'two'),
                (-20, 'ten'),
                (-22, 'two'),
                (-24, 'two'),
                (-25, 'twenty five'),
                (-26, 'two'),
                (-28, 'two'),
                (-30, 'ten'),
                (-32, 'two'),
                (-34, 'two'),
                (-35, 'five'),
                (-36, 'two'),
                (-38, 'two'),
                (-40, 'ten'),
                (-42, 'two')
            ],
            eventS
        )
        
    def test_04(self):
        """TestXGrid.test_04(): ctor uses default _setInterval(), test _getInterval()."""
        #print()
        myXs = XGrid.XGrid(200)
        #print(myXs._getInterval(b'FEET'))
        self.assertEqual(
            {
                2   : Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0),
                10  : Stroke.Stroke(width=0.5, colour='black', coding=None, opacity=1.0),
                50  : Stroke.Stroke(width=0.75, colour='black', coding=None, opacity=1.0),
                100 : Stroke.Stroke(width=1.0, colour='black', coding=None, opacity=1.0),
            },
            myXs._getInterval(b'FEET'),
        )

    def test_05(self):
        """TestXGrid.test_05(): ctor uses default _setInterval(), test _getInterval() defaults."""
        #print()
        myXs = XGrid.XGrid(200)
        self.assertEqual(XGrid.XGrid.DEFAULT_INTERVAL_MAP, myXs._getInterval(b'    '))

    def test_06(self):
        """TestXGrid.test_06(): _setInterval() fails."""
        #print()
        myXs = XGrid.XGrid(200)
        self.assertRaises(XGrid.ExceptionPlotXGrid, myXs._setInterval, 'in', 200.0, {})

        
    def test_07(self):
        """TestXGrid.test_07(): ctor uses default _setInterval(), test _getIntervalText()."""
        #print()
        myXs = XGrid.XGrid(200)
        #print(myXs._getInterval(b'FEET'))
        self.assertEqual(100, myXs._getIntervalText(b'FEET'))

    def test_08(self):
        """TestXGrid.test_08(): ctor uses default _setInterval(), test _getInterval() defaults."""
        #print()
        myXs = XGrid.XGrid(200)
        self.assertEqual(XGrid.XGrid.DEFAULT_INTERVAL_TEXT, myXs._getIntervalText(b'    '))

    def test_09(self):
        """TestXGrid.test_09(): _setIntervalText() fails."""
        #print()
        myXs = XGrid.XGrid(200)
        self.assertRaises(XGrid.ExceptionPlotXGrid, myXs._setIntervalText, 'in', 200.0, {})

    def test_10(self):
        """TestXGrid.test_10(): genXAxisStroke() plotting UP with FEET and 1/200."""
        #print()
        myXs = XGrid.XGrid(200)
        v = 0
        eventS = []
        for e in myXs._genXAxisStroke(xFrom=4307.5, xInc=False, units=b'FEET'):
            #print(e)
            eventS.append(e)
            v += 1
            if v > 30:
                break
        #pprint.pprint(eventS)
        self.assertEqual(
            [
                (4306, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4304, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4302, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4300, Stroke.Stroke(width=1.0, colour='black', coding=None, opacity=1.0)),
                (4298, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4296, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4294, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4292, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4290, Stroke.Stroke(width=0.5, colour='black', coding=None, opacity=1.0)),
                (4288, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4286, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4284, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4282, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4280, Stroke.Stroke(width=0.5, colour='black', coding=None, opacity=1.0)),
                (4278, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4276, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4274, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4272, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4270, Stroke.Stroke(width=0.5, colour='black', coding=None, opacity=1.0)),
                (4268, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4266, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4264, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4262, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4260, Stroke.Stroke(width=0.5, colour='black', coding=None, opacity=1.0)),
                (4258, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4256, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4254, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4252, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4250, Stroke.Stroke(width=0.75, colour='black', coding=None, opacity=1.0)),
                (4248, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (4246, Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
            ],
            eventS
        )
     
    def test_11(self):
        """TestXGrid.test_11(): genXPosStroke() plotting UP with FEET and 1/200."""
        #print()
        myXs = XGrid.XGrid(200)
        v = 0
        eventS = []
        for e in myXs.genXPosStroke(xFrom=4307.5, xInc=False, units=b'FEET'):
            #print(e)
            eventS.append(e)
            v += 1
            if v > 30:
                break
        #pprint.pprint(eventS)
        self.assertEqual(
            [
                (Coord.Dim(value=-0.09000000000000002, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.21, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.33, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.45, units='in'),
                 Stroke.Stroke(width=1.0, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.57, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.6900000000000002, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.81, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.93, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-1.05, units='in'),
                 Stroke.Stroke(width=0.5, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-1.17, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-1.29, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-1.4100000000000004, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-1.53, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-1.65, units='in'),
                 Stroke.Stroke(width=0.5, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-1.77, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-1.8900000000000003, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-2.0100000000000002, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-2.1300000000000003, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-2.25, units='in'),
                 Stroke.Stroke(width=0.5, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-2.37, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-2.49, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-2.61, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-2.7300000000000004, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-2.8500000000000005, units='in'),
                 Stroke.Stroke(width=0.5, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-2.97, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-3.09, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-3.21, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-3.33, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-3.45, units='in'),
                 Stroke.Stroke(width=0.75, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-3.57, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-3.69, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
            ],
            eventS
        )

class TestXText(unittest.TestCase):
    """Tests XText plotting"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestXGrid.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestXGrid.test_01(): genXAxisText() 5 values from 4307.5 upwards."""
        myXs = XGrid.XGrid(200)
        #print()
        v = 0
        eventS = []
        for e in myXs._genXAxisText(xFrom=4307.5, xInc=False, units=b'FEET'):
            eventS.append(e)
            v += 1
            if v > 4:
                break
        #pprint.pprint(eventS)
        self.assertEqual([4300, 4200, 4100, 4000, 3900,], eventS)

    def test_02(self):
        """TestXGrid.test_02(): genXPosText() 5 values from 4307.5 upwards."""
        myXs = XGrid.XGrid(200)
        #print()
        v = 0
        eventS = []
        for e in myXs._genXPosText(xFrom=4307.5, xInc=False, units=b'FEET'):
            eventS.append(e)
            v += 1
            if v > 4:
                break
        #pprint.pprint(eventS)
        self.assertEqual(
            [
                (Coord.Dim(value=-0.45, units='in'), 4300),
                (Coord.Dim(value=-6.45, units='in'), 4200),
                (Coord.Dim(value=-12.45, units='in'), 4100),
                (Coord.Dim(value=-18.45, units='in'), 4000),
                (Coord.Dim(value=-24.45, units='in'), 3900),
            ],
            eventS
        )

class TestXGridRange(unittest.TestCase):
    """Tests XGrid plotting across an X axis range."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestXGridRange.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestXGridRange.test_01(): genXAxisRange()."""
        myXs = XGrid.XGrid(200)
        myVals = [v for v in myXs.genXAxisRange(
                                    EngVal.EngVal(4001.0, b'FEET'),
                                    EngVal.EngVal(3987.0, b'FEET')
                                    )
                                ]
        #print()
        #pprint.pprint(myVals)
        self.assertEqual(
            [
                (Coord.Dim(value=-0.06000000000000001, units='in'),
                 Stroke.Stroke(width=1.0, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.18000000000000005, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.3, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.42, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.54, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.66, units='in'),
                 Stroke.Stroke(width=0.5, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.78, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
            ],
            myVals,
        )

    def test_02(self):
        """TestXGridRange.test_02(): genXAxisRange() with unit change."""
        myXs = XGrid.XGrid(200)
        myVals = [v for v in myXs.genXAxisRange(
                        EngVal.EngVal(4001.0, b'FEET'),
                        EngVal.EngVal(3987.0, b'FEET').newEngValInUnits(b'M   ')
                        )
                    ]
        #print()
        #pprint.pprint(myVals)
        self.assertEqual(
            [
                (Coord.Dim(value=-0.06000000000000001, units='in'),
                 Stroke.Stroke(width=1.0, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.18000000000000005, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.3, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.42, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.54, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.66, units='in'),
                 Stroke.Stroke(width=0.5, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.78, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
            ],
            myVals,
        )

    def test_10(self):
        """TestXGridRange.test_10(): genXAxisTextRange()."""
        myXs = XGrid.XGrid(200)
        myVals = [v for v in myXs.genXAxisTextRange(
                                    EngVal.EngVal(4001.0, b'FEET'),
                                    EngVal.EngVal(3499.0, b'FEET')
                                    )
                                ]
        #print()
        #pprint.pprint(myVals)
        self.assertEqual(
            [
                (Coord.Dim(value=-0.06000000000000001, units='in'), 4000),
                (Coord.Dim(value=-6.06, units='in'), 3900),
                (Coord.Dim(value=-12.06, units='in'), 3800),
                (Coord.Dim(value=-18.06, units='in'), 3700),
                (Coord.Dim(value=-24.06, units='in'), 3600),
                (Coord.Dim(value=-30.060000000000006, units='in'), 3500),
            ],
            myVals,
        )

    def test_11(self):
        """TestXGridRange.test_11(): genXAxisTextRange() with unit change."""
        myXs = XGrid.XGrid(200)
        myVals = [v for v in myXs.genXAxisTextRange(
                    EngVal.EngVal(4001.0, b'FEET'),
                    EngVal.EngVal(3499.0, b'FEET').newEngValInUnits(b'M   ')
                    )
                ]
        #print()
        #pprint.pprint(myVals)
        self.assertEqual(6, len(myVals))
        self.assertEqual(
            [
                (Coord.Dim(value=-0.06000000000000001, units='in'), 4000),
                (Coord.Dim(value=-6.06, units='in'), 3900),
                (Coord.Dim(value=-12.06, units='in'), 3800),
                (Coord.Dim(value=-18.06, units='in'), 3700),
                (Coord.Dim(value=-24.06, units='in'), 3600),
                (Coord.Dim(value=-30.060000000000006, units='in'), 3500),
            ],
            myVals,
        )

    def test_20(self):
        """TestXGridRange.test_20(): genXAxisRange() with 'non-optical' units b'.1IN'."""
        myXs = XGrid.XGrid(200)
        myVals = [v for v in myXs.genXAxisRange(
                        EngVal.EngVal(4001.0, b'FEET').newEngValInUnits(b'.1IN'),
                        EngVal.EngVal(3987.0, b'FEET').newEngValInUnits(b'.1IN'),
                        )
                    ]
        self.assertEqual(7, len(myVals))
#        print()
#        pprint.pprint(myVals)
        self.assertEqual(
#            [
#                (Coord.Dim(value=-0.06000000000000001, units='in'),
#                 Stroke.Stroke(width=1.0, colour='black', coding=None, opacity=1.0)),
#                (Coord.Dim(value=-0.18000000000000005, units='in'),
#                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
#                (Coord.Dim(value=-0.3, units='in'),
#                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
#                (Coord.Dim(value=-0.42, units='in'),
#                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
#                (Coord.Dim(value=-0.54, units='in'),
#                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
#                (Coord.Dim(value=-0.66, units='in'),
#                 Stroke.Stroke(width=0.5, colour='black', coding=None, opacity=1.0)),
#                (Coord.Dim(value=-0.78, units='in'),
#                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
#            ],
            [
                (Coord.Dim(value=-0.060000000000027295, units='in'),
                 Stroke.Stroke(width=1.0, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.18000000000002728, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.3000000000000273, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.4200000000000273, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.5400000000000273, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.6600000000000272, units='in'),
                 Stroke.Stroke(width=0.5, colour='black', coding=None, opacity=1.0)),
                (Coord.Dim(value=-0.7800000000000273, units='in'),
                 Stroke.Stroke(width=0.25, colour='black', coding=None, opacity=1.0)),
            ],
            myVals,
        )

    def test_21(self):
        """TestXGridRange.test_21(): genXAxisTextRange() with 'non-optical' units b'.1IN'."""
        myXs = XGrid.XGrid(200)
        myVals = [v for v in myXs.genXAxisTextRange(
                    EngVal.EngVal(4001.0, b'FEET').newEngValInUnits(b'.1IN'),
                    EngVal.EngVal(3499.0, b'FEET').newEngValInUnits(b'.1IN'),
                    )
                ]
        self.assertEqual(6, len(myVals))
#        print()
#        pprint.pprint(myVals)
        self.assertEqual(
#            [
#                (Coord.Dim(value=-0.06000000000000001, units='in'), 4000),
#                (Coord.Dim(value=-6.06, units='in'), 3900),
#                (Coord.Dim(value=-12.06, units='in'), 3800),
#                (Coord.Dim(value=-18.06, units='in'), 3700),
#                (Coord.Dim(value=-24.06, units='in'), 3600),
#                (Coord.Dim(value=-30.060000000000006, units='in'), 3500),
#            ],
            [
                (Coord.Dim(value=-0.060000000000027295, units='in'), 4000),
                (Coord.Dim(value=-6.060000000000027, units='in'), 3900),
                (Coord.Dim(value=-12.060000000000029, units='in'), 3800),
                (Coord.Dim(value=-18.060000000000027, units='in'), 3700),
                (Coord.Dim(value=-24.060000000000027, units='in'), 3600),
                (Coord.Dim(value=-30.06000000000003, units='in'), 3500),
            ],
            myVals,
        )

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestXGrid))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestXText))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestXGridRange))
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
    print('TestClass.py script version "%s", dated %s' % (__version__, __date__))
    print('Author: %s' % __author__)
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
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')

if __name__ == "__main__":
    main()
