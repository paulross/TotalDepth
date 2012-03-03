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
# Paul Ross: cpipdev@googlemail.com
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
import math
#import decimal
#import pprint
import io

from TotalDepth.util.plot import Coord
from TotalDepth.util.plot import Track
#from TotalDepth.util.plot import Plot
from TotalDepth.util.plot import SVGWriter

######################
# Section: Unit tests.
######################
import unittest

class TestTrackGenLines(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestCLass: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestTrackGenLines.test_00(): genLinear10() line widths."""
        wS = [s.width for s, p in Track.genLinear10(4.0, 8.0)]
        #print()
        #pprint.pprint(wS)
        self.assertEqual(
            [0.75, 0.25, 0.25, 0.25, 0.25, 0.5, 0.25, 0.25, 0.25, 0.25, 0.75],
            wS,
        )

    def test_01(self):
        """TestTrackGenLines.test_01(): genLinear10() line spacing."""
        pS = [p for s, p in Track.genLinear10(40.0, 120.0)]
        #print()
        #pprint.pprint(pS)
        self.assertEqual(11, len(pS))
        self.assertEqual(
            [40.0, 48.0, 56.0, 64.0, 72.0, 80.0, 88.0, 96.0, 104.0, 112.0, 120.0],
            pS,
        )

    def test_02(self):
        """TestTrackGenLines.test_02(): genLinear10() line spacing."""
        pS = [p for s, p in Track.genLinear10(120.0, 40.0)]
        #print()
        #pprint.pprint(pS)
        self.assertEqual(11, len(pS))
        self.assertEqual(
            list(reversed([40.0, 48.0, 56.0, 64.0, 72.0, 80.0, 88.0, 96.0, 104.0, 112.0, 120.0])),
            pS,
        )

    def test_10(self):
        """TestTrackGenLines.test_10(): genLog10() line widths."""
        wS = [s.width for s, p in Track.genLog10(40.0, 120.0)]
#        print()
#        pprint.pprint(wS)
        self.assertEqual(10, len(wS))
        self.assertEqual(
            [0.75, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.75],
            wS,
        )

    def test_11(self):
        """TestTrackGenLines.test_11(): genLog10() line spacing."""
        pS = [p for s, p in Track.genLog10(40.0, 120.0)]
        #print()
        #pprint.pprint(pS)
        self.assertEqual(10, len(pS))
        self.assertEqual(
            [
                40.0,
                64.0823996531185,
                78.169700377573,
                88.164799306237,
                95.9176003468815,
                102.2521000306915,
                107.60784320114054,
                112.24719895935549,
                116.33940075514599,
                120.0,
            ],
            pS,
        )

    def test_12(self):
        """TestTrackGenLines.test_12(): genLog10() line widths."""
        wS = [s.width for s, p in Track.genLog10(40.0, 120.0, cycles=2)]
#        print()
#        pprint.pprint(wS)
        self.assertEqual(19, len(wS))
        self.assertEqual(
            [0.75, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25,
            0.75, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.75,],
            wS,
        )

    def test_13(self):
        """TestTrackGenLines.test_13(): genLog10() line spacing."""
        pS = [p for s, p in Track.genLog10(40.0, 200.0, cycles=2)]
        #print()
        #pprint.pprint(pS)
        self.assertEqual(19, len(pS))
        self.assertEqual(
            [
                40.0,
                64.0823996531185,
                78.169700377573,
                88.164799306237,
                95.9176003468815,
                102.2521000306915,
                107.60784320114054,
                112.24719895935549,
                116.33940075514599,
                120.0,
                144.0823996531185,
                158.169700377573,
                168.164799306237,
                175.9176003468815,
                182.2521000306915,
                187.60784320114055,
                192.2471989593555,
                196.339400755146,
                200.0,                
            ],
            pS,
        )

    def test_14(self):
        """TestTrackGenLines.test_14(): genLog10() line widths, two cycles, start at 2."""
        pS = [(s.width, p) for s, p in Track.genLog10(0.0, 200.0, cycles=2, start=2)]
#        print()
#        pprint.pprint(pS)
        self.assertEqual(19, len(pS))
        self.assertEqual(
            [
                (0.75, 0.0),
                (0.25, 17.609125905568124),
                (0.25, 30.10299956639812),
                (0.25, 39.79400086720376),
                (0.25, 47.712125471966246),
                (0.25, 54.40680443502757),
                (0.25, 60.20599913279623),
                (0.25, 65.32125137753437),
                (0.75, 69.89700043360187),
                (0.25, 100.0),
                (0.25, 117.60912590556812),
                (0.25, 130.10299956639813),
                (0.25, 139.79400086720375),
                (0.25, 147.71212547196626),
                (0.25, 154.40680443502757),
                (0.25, 160.20599913279622),
                (0.25, 165.32125137753437),
                (0.75, 169.89700043360187),
                (0.75, 200.0),
             ],
            pS,
        )

    def test_15(self):
        """TestTrackGenLines.test_15(): genLog10() line spacing."""
        #pS = [p for s, p in Track.genLog10(40.0, 200.0, cycles=2, start=2)]
        pS = [(s.width, p) for s, p in Track.genLog10(40.0, 200.0, cycles=2, start=2)]
#        print()
#        pprint.pprint(pS)
        self.assertEqual(19, len(pS))
        self.assertEqual(
            [
                (0.75, 40.0),
                (0.25, 54.0873007244545),
                (0.25, 64.0823996531185),
                (0.25, 71.83520069376301),
                (0.25, 78.169700377573),
                (0.25, 83.52544354802205),
                (0.25, 88.16479930623699),
                (0.25, 92.2570011020275),
                (0.75, 95.9176003468815),
                (0.25, 120.0),
                (0.25, 134.0873007244545),
                (0.25, 144.0823996531185),
                (0.25, 151.835200693763),
                (0.25, 158.169700377573),
                (0.25, 163.52544354802205),
                (0.25, 168.164799306237),
                (0.25, 172.25700110202752),
                (0.75, 175.9176003468815),
                (0.75, 200.0),
            ],
            pS,
        )

    def test_16(self):
        """TestTrackGenLines.test_16(): genLog10() line spacing."""
        pS = [math.pow(10,(p-40)/80) for s, p in Track.genLog10(40.0, 200.0, cycles=2, start=1)]
#        print()
#        pprint.pprint(pS)
        self.assertEqual(19, len(pS))
#        decimal.getcontext().prec = 6
#        print(decimal.getcontext())
#        print([decimal.Decimal(p) for p in pS])
#        expResult = [decimal.Decimal(n) for n in list(range(1,11))+list(range(20,110,10))]
        expResult = [float(n) for n in list(range(1,11))+list(range(20,110,10))]
        for e,p in zip(expResult, pS):
            self.assertAlmostEqual(e, p, 6)
#        self.assertEqual(
#            expResult,
#            [decimal.Decimal(p, decimal.getcontext()) for p in pS],
#        )

    def test_17(self):
        """TestTrackGenLines.test_17(): genLog10Decade3() line spacing."""
        pS = [(s.width, p) for s, p in Track.genLog10Decade3(0.0, 300.0)]
#        print()
#        pprint.pprint(pS)
        self.assertEqual(28, len(pS))
        expRes = [
            (0.75, 0.0),
            (0.25, 30.10299956639812),
            (0.25, 47.712125471966246),
            (0.25, 60.20599913279624),
            (0.25, 69.89700043360189),
            (0.25, 77.81512503836436),
            (0.25, 84.50980400142568),
            (0.25, 90.30899869919435),
            (0.25, 95.42425094393249),
            (0.75, 100.0),
            (0.25, 130.10299956639813),
            (0.25, 147.71212547196626),
            (0.25, 160.20599913279625),
            (0.25, 169.89700043360187),
            (0.25, 177.81512503836436),
            (0.25, 184.50980400142566),
            (0.25, 190.30899869919435),
            (0.25, 195.4242509439325),
            (0.75, 200.0),
            (0.25, 230.10299956639813),
            (0.25, 247.71212547196626),
            (0.25, 260.20599913279625),
            (0.25, 269.8970004336019),
            (0.25, 277.8151250383644),
            (0.25, 284.50980400142566),
            (0.25, 290.3089986991944),
            (0.25, 295.4242509439325),
            (0.75, 300.0),
        ]
#        self.assertEqual(expRes, pS)
        for (el, ep), (al, ap) in zip(expRes, pS):
            self.assertAlmostEqual(el, al)
            self.assertAlmostEqual(ep, ap)
        
    def test_18(self):
        """TestTrackGenLines.test_18(): genLog10Decade3() line spacing."""
        pS = [math.pow(10,p/100) for s, p in Track.genLog10Decade3(0.0, 300.0)]
        self.assertEqual(28, len(pS))
        expResult = [float(n) for n in list(range(1,11,1))+list(range(20,110,10))+list(range(200,1100,100))]
#        print()
#        pprint.pprint(expResult)
#        pprint.pprint(pS)
        for e,p in zip(expResult, pS):
            self.assertAlmostEqual(e, p)

    def test_19(self):
        """TestTrackGenLines.test_19(): genLog10Decade4() line spacing."""
        pS = [(s.width, p) for s, p in Track.genLog10Decade4(0.0, 400.0)]
#        print()
#        pprint.pprint(pS)
        self.assertEqual(37, len(pS))
        expRes = [
            (0.75, 0.0),
            (0.25, 30.10299956639812),
            (0.25, 47.712125471966246),
            (0.25, 60.20599913279624),
            (0.25, 69.89700043360189),
            (0.25, 77.81512503836436),
            (0.25, 84.50980400142568),
            (0.25, 90.30899869919435),
            (0.25, 95.42425094393249),
            (0.75, 100.0),
            (0.25, 130.10299956639813),
            (0.25, 147.71212547196626),
            (0.25, 160.20599913279625),
            (0.25, 169.89700043360187),
            (0.25, 177.81512503836436),
            (0.25, 184.50980400142566),
            (0.25, 190.30899869919435),
            (0.25, 195.4242509439325),
            (0.75, 200.0),
            (0.25, 230.10299956639813),
            (0.25, 247.71212547196626),
            (0.25, 260.20599913279625),
            (0.25, 269.8970004336019),
            (0.25, 277.8151250383644),
            (0.25, 284.50980400142566),
            (0.25, 290.3089986991944),
            (0.25, 295.4242509439325),
            (0.75, 300.0),
            (0.25, 330.1029995663981),
            (0.25, 347.71212547196626),
            (0.25, 360.20599913279625),
            (0.25, 369.8970004336019),
            (0.25, 377.8151250383644),
            (0.25, 384.50980400142566),
            (0.25, 390.3089986991944),
            (0.25, 395.4242509439325),
            (0.75, 400.0),
        ]
#        self.assertEqual(expRes, pS)
        for (el, ep), (al, ap) in zip(expRes, pS):
            self.assertAlmostEqual(el, al)
            self.assertAlmostEqual(ep, ap)
        
    def test_20(self):
        """TestTrackGenLines.test_20(): genLog10Decade4() line spacing."""
        pS = [math.pow(10,p/100) for s, p in Track.genLog10Decade4(0.0, 400.0)]
        self.assertEqual(37, len(pS))
        expResult = [float(n) for n in 
                     list(range(1,11,1))
                     +list(range(20,110,10))
                     +list(range(200,1100,100))
                     +list(range(2000,11000,1000))
                     ]
#        print()
#        pprint.pprint(expResult)
#        pprint.pprint(pS)
        for e,p in zip(expResult, pS):
            self.assertAlmostEqual(e, p)

    def test_21(self):
        """TestTrackGenLines.test_21(): genLog10Decade5() line spacing."""
        pS = [(s.width, p) for s, p in Track.genLog10Decade5(0.0, 500.0)]
#        print()
#        pprint.pprint(pS)
        self.assertEqual(46, len(pS))
        expRes = [
            (0.75, 0.0),
            (0.25, 30.10299956639812),
            (0.25, 47.712125471966246),
            (0.25, 60.20599913279624),
            (0.25, 69.89700043360189),
            (0.25, 77.81512503836436),
            (0.25, 84.50980400142568),
            (0.25, 90.30899869919435),
            (0.25, 95.42425094393249),
            (0.75, 100.0),
            (0.25, 130.10299956639813),
            (0.25, 147.71212547196626),
            (0.25, 160.20599913279625),
            (0.25, 169.89700043360187),
            (0.25, 177.81512503836436),
            (0.25, 184.50980400142566),
            (0.25, 190.30899869919435),
            (0.25, 195.4242509439325),
            (0.75, 200.0),
            (0.25, 230.10299956639813),
            (0.25, 247.71212547196626),
            (0.25, 260.20599913279625),
            (0.25, 269.8970004336019),
            (0.25, 277.8151250383644),
            (0.25, 284.50980400142566),
            (0.25, 290.3089986991944),
            (0.25, 295.4242509439325),
            (0.75, 300.0),
            (0.25, 330.1029995663981),
            (0.25, 347.71212547196626),
            (0.25, 360.20599913279625),
            (0.25, 369.8970004336019),
            (0.25, 377.8151250383644),
            (0.25, 384.50980400142566),
            (0.25, 390.3089986991944),
            (0.25, 395.4242509439325),
            (0.75, 400.0),
            (0.25, 430.1029995663981),
            (0.25, 447.71212547196626),
            (0.25, 460.20599913279625),
            (0.25, 469.8970004336019),
            (0.25, 477.8151250383644),
            (0.25, 484.50980400142566),
            (0.25, 490.3089986991944),
            (0.25, 495.4242509439325),
            (0.75, 500.0),
        ]
#        self.assertEqual(expRes, pS)
        for (el, ep), (al, ap) in zip(expRes, pS):
            self.assertAlmostEqual(el, al)
            self.assertAlmostEqual(ep, ap)
        
    def test_22(self):
        """TestTrackGenLines.test_22(): genLog10Decade5() line spacing."""
        pS = [math.pow(10,p/100) for s, p in Track.genLog10Decade5(0.0, 500.0)]
        self.assertEqual(46, len(pS))
        expResult = [float(n) for n in 
                     list(range(1,11,1))
                     +list(range(20,110,10))
                     +list(range(200,1100,100))
                     +list(range(2000,11000,1000))
                     +list(range(20000,110000, 10000))
                     ]
#        print()
#        pprint.pprint(expResult)
#        pprint.pprint(pS)
        for e,p in zip(expResult, pS):
            self.assertAlmostEqual(e, p)

    def test_31(self):
        """TestTrackGenLines.test_31(): genLog10Decade1Start2() line spacing."""
        pS = [(s.width, p) for s, p in Track.genLog10Decade1Start2(0.0, 100.0)]
#        print()
#        pprint.pprint(pS)
        self.assertEqual(10, len(pS))
        expRes = [
            # Starting at 1
#            (0.75, 0.0),
#            (0.25, 30.10299956639812),
#            (0.25, 47.712125471966246),
#            (0.25, 60.20599913279624),
#            (0.25, 69.89700043360189),
#            (0.25, 77.81512503836436),
#            (0.25, 84.50980400142568),
#            (0.25, 90.30899869919435),
#            (0.25, 95.42425094393249),
#            (0.75, 100.0),
            # Startign at 2
            (0.75, 0.0),
            (0.25, 17.609125905568124),
            (0.25, 30.10299956639812),
            (0.25, 39.79400086720376),
            (0.25, 47.712125471966246),
            (0.25, 54.40680443502757),
            (0.25, 60.20599913279623),
            (0.25, 65.32125137753437),
            (0.75, 69.89700043360187),
            (0.75, 100.0),
        ]
#        self.assertEqual(expRes, pS)
        for (el, ep), (al, ap) in zip(expRes, pS):
            self.assertAlmostEqual(el, al)
            self.assertAlmostEqual(ep, ap)
        
    def test_32(self):
        """TestTrackGenLines.test_32(): genLog10Decade1Start2() line spacing."""
        pS = [math.pow(10,p/100) for s, p in Track.genLog10Decade1Start2(0.0, 100.0)]
        self.assertEqual(10, len(pS))
        expResult = [float(n/2) for n in 
                     list(range(2,11,1))
                     +list(range(20,30,10))
                     ]
#        print()
#        pprint.pprint(expResult)
#        pprint.pprint(pS)
        for e,p in zip(expResult, pS):
            self.assertAlmostEqual(e, p)

    def test_33(self):
        """TestTrackGenLines.test_33(): genLog10Decade2Start2() line spacing."""
        pS = [(s.width, p) for s, p in Track.genLog10Decade2Start2(0.0, 200.0)]
#        print()
#        pprint.pprint(pS)
        self.assertEqual(19, len(pS))
        expRes = [
            (0.75, 0.0),
            (0.25, 17.609125905568124),
            (0.25, 30.10299956639812),
            (0.25, 39.79400086720376),
            (0.25, 47.712125471966246),
            (0.25, 54.40680443502757),
            (0.25, 60.20599913279623),
            (0.25, 65.32125137753437),
            (0.75, 69.89700043360187),
            (0.25, 100.0),
            (0.25, 117.60912590556812),
            (0.25, 130.10299956639813),
            (0.25, 139.79400086720375),
            (0.25, 147.71212547196626),
            (0.25, 154.40680443502757),
            (0.25, 160.20599913279622),
            (0.25, 165.32125137753437),
            (0.75, 169.89700043360187),
            (0.75, 200.0),
        ]
#        self.assertEqual(expRes, pS)
        for (el, ep), (al, ap) in zip(expRes, pS):
            self.assertAlmostEqual(el, al)
            self.assertAlmostEqual(ep, ap)
        
    def test_34(self):
        """TestTrackGenLines.test_34(): genLog10Decade2Start2() line spacing."""
        pS = [math.pow(10,p/100) for s, p in Track.genLog10Decade2Start2(0.0, 200.0)]
        self.assertEqual(19, len(pS))
        expResult = [float(n/2) for n in 
                     list(range(2,11,1))
                     +list(range(20,110,10))
                     +list(range(200,300,100))
                     ]
#        print()
#        pprint.pprint(expResult)
#        pprint.pprint(pS)
        for e,p in zip(expResult, pS):
            self.assertAlmostEqual(e, p)

class TestPlotTrack(unittest.TestCase):
    """Tests track plotting"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotTrack.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPlotTrack.test_01(): Construct a linear track without failure and check default values."""
        myT = Track.Track(
            leftPos=Coord.Dim(3.2, 'in'), 
            rightPos=Coord.Dim(5.6, 'in'),
            gridGn=Track.genLinear10
        )
        self.assertEquals(Coord.Dim(3.2, 'in'), myT.left)
        self.assertEquals(Coord.Dim(5.6, 'in'), myT.right)
        self.assertTrue(myT.hasGrid)
        self.assertTrue(myT.plotXLines)
        self.assertFalse(myT.plotXAlpha)
        
    def test_02(self):
        """TestPlotTrack.test_02(): Construct a linear track and plot it in SVG."""
        myT = Track.Track(
            leftPos=Coord.Dim(3.2, 'in'), 
            rightPos=Coord.Dim(5.6, 'in'),
            gridGn=Track.genLinear10
        )
#        myCnv = Plot.Canvas(Coord.Dim(6, 'in'), Coord.Dim(8, 'in'), Plot.MarginQtrInch)
#        myViewPort = Coord.Box(
#            width=myCnv.width,
#            depth=myCnv.depth,
#        )
        myViewPort = Coord.Box(
            width=Coord.Dim(6, 'in'),
            depth=Coord.Dim(8, 'in'),
        )
        myTl = Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(0.25, 'in'))
        myF = io.StringIO()
        with SVGWriter.SVGWriter(myF, myViewPort) as xS:
            myT.plotSVG(myTl, Coord.Dim(7.5, 'in'), xS)
#        print()
#        print(myF.getvalue())
#        self.maxDiff = None
        self.assertEqual("""<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="8in" version="1.1" width="6in" xmlns="http://www.w3.org/2000/svg">
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.750" x1="3.45in" x2="3.45in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="3.69in" x2="3.69in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="3.93in" x2="3.93in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="4.17in" x2="4.17in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="4.41in" x2="4.41in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.500" x1="4.65in" x2="4.65in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="4.89in" x2="4.89in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.13in" x2="5.13in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.37in" x2="5.37in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.61in" x2="5.61in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.750" x1="5.85in" x2="5.85in" y1="0.25in" y2="7.75in"/>
</svg>
""",
            myF.getvalue()
        )
        
    def test_03(self):
        """TestPlotTrack.test_03(): Construct a log track and plot it in SVG."""
        myT = Track.Track(
            leftPos=Coord.Dim(3.2, 'in'), 
            rightPos=Coord.Dim(5.6, 'in'),
            gridGn=Track.genLog10Decade2
        )
#        myCnv = Plot.Canvas(Coord.Dim(6, 'in'), Coord.Dim(8, 'in'), Plot.MarginQtrInch)
#        myViewPort = Coord.Box(
#            width=myCnv.width,
#            depth=myCnv.depth,
#        )
        myViewPort = Coord.Box(
            width=Coord.Dim(6, 'in'),
            depth=Coord.Dim(8, 'in'),
        )
        myTl = Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(0.25, 'in'))
        myF = io.StringIO()
        with SVGWriter.SVGWriter(myF, myViewPort) as xS:
            myT.plotSVG(myTl, Coord.Dim(7.5, 'in'), xS)
#        print()
#        print(myF.getvalue())
#        self.maxDiff = None
        self.assertEqual("""<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="8in" version="1.1" width="6in" xmlns="http://www.w3.org/2000/svg">
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.750" x1="3.45in" x2="3.45in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="3.8112in" x2="3.8112in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="4.0225in" x2="4.0225in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="4.1725in" x2="4.1725in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="4.2888in" x2="4.2888in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="4.3838in" x2="4.3838in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="4.4641in" x2="4.4641in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="4.5337in" x2="4.5337in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="4.5951in" x2="4.5951in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.750" x1="4.65in" x2="4.65in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.0112in" x2="5.0112in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.2225in" x2="5.2225in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.3725in" x2="5.3725in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.4888in" x2="5.4888in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.5838in" x2="5.5838in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.6641in" x2="5.6641in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.7337in" x2="5.7337in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.7951in" x2="5.7951in" y1="0.25in" y2="7.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.750" x1="5.85in" x2="5.85in" y1="0.25in" y2="7.75in"/>
</svg>
""",
            myF.getvalue()
        )

    def test_04(self):
        """TestPlotTrack.test_04(): Construct a lin/log/log track and plot it in SVG."""
        myTracks = [
            Track.Track(
                leftPos=Coord.Dim(0.0, 'in'), 
                rightPos=Coord.Dim(2.4, 'in'),
                gridGn=Track.genLinear10
            ),
            Track.Track(
                leftPos=Coord.Dim(3.2, 'in'), 
                rightPos=Coord.Dim(5.6, 'in'),
                gridGn=Track.genLog10Decade2Start2
            ),
            Track.Track(
                leftPos=Coord.Dim(5.6, 'in'), 
                rightPos=Coord.Dim(8, 'in'),
                gridGn=Track.genLog10Decade2Start2
            ),
        ]
#        myCnv = Plot.Canvas(Coord.Dim(8.5, 'in'), Coord.Dim(6, 'in'), Plot.MarginQtrInch)
#        myViewPort = Coord.Box(
#            width=myCnv.width,
#            depth=myCnv.depth,
#        )
        myViewPort = Coord.Box(
            width=Coord.Dim(6, 'in'),
            depth=Coord.Dim(8, 'in'),
        )
        myTl = Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(0.25, 'in'))
        myF = io.StringIO()
        with SVGWriter.SVGWriter(myF, myViewPort) as xS:
            for t in myTracks:
                #xS.comment(str(t))
                t.plotSVG(myTl, Coord.Dim(5.5, 'in'), xS)
#        print()
#        print(myF.getvalue())
#        self.maxDiff = None
        self.assertEqual("""<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="8in" version="1.1" width="6in" xmlns="http://www.w3.org/2000/svg">
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.750" x1="0.25in" x2="0.25in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="0.49in" x2="0.49in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="0.73in" x2="0.73in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="0.97in" x2="0.97in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="1.21in" x2="1.21in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.500" x1="1.45in" x2="1.45in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="1.69in" x2="1.69in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="1.93in" x2="1.93in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="2.17in" x2="2.17in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="2.41in" x2="2.41in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.750" x1="2.65in" x2="2.65in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.750" x1="3.45in" x2="3.45in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="3.6613in" x2="3.6613in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="3.8112in" x2="3.8112in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="3.9275in" x2="3.9275in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="4.0225in" x2="4.0225in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="4.1029in" x2="4.1029in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="4.1725in" x2="4.1725in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="4.2339in" x2="4.2339in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.750" x1="4.2888in" x2="4.2888in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="4.65in" x2="4.65in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="4.8613in" x2="4.8613in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.0112in" x2="5.0112in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.1275in" x2="5.1275in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.2225in" x2="5.2225in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.3029in" x2="5.3029in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.3725in" x2="5.3725in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="5.4339in" x2="5.4339in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.750" x1="5.4888in" x2="5.4888in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.750" x1="5.85in" x2="5.85in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.750" x1="5.85in" x2="5.85in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="6.0613in" x2="6.0613in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="6.2112in" x2="6.2112in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="6.3275in" x2="6.3275in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="6.4225in" x2="6.4225in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="6.5029in" x2="6.5029in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="6.5725in" x2="6.5725in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="6.6339in" x2="6.6339in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.750" x1="6.6888in" x2="6.6888in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="7.05in" x2="7.05in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="7.2613in" x2="7.2613in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="7.4112in" x2="7.4112in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="7.5275in" x2="7.5275in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="7.6225in" x2="7.6225in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="7.7029in" x2="7.7029in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="7.7725in" x2="7.7725in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.250" x1="7.8339in" x2="7.8339in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.750" x1="7.8888in" x2="7.8888in" y1="0.25in" y2="5.75in"/>
  <line stroke="black" stroke-opacity="1.000" stroke-width="0.750" x1="8.25in" x2="8.25in" y1="0.25in" y2="5.75in"/>
</svg>
""", myF.getvalue())

    def test_05(self):
        """TestPlotTrack.test_05(): Construct a blank track without failure."""
        myT = Track.Track(
            leftPos=Coord.Dim(3.2, 'in'), 
            rightPos=Coord.Dim(5.6, 'in'),
            gridGn=None
        )
        self.assertEquals(Coord.Dim(3.2, 'in'), myT.left)
        self.assertEquals(Coord.Dim(5.6, 'in'), myT.right)
        self.assertFalse(myT.hasGrid)
        
    def test_10(self):
        """TestPlotTrack.test_10(): Construct a linear track with left edge < 0 - fails."""
        try:
            Track.Track(
                leftPos=Coord.Dim(-3.2, 'in'), 
                rightPos=Coord.Dim(5.6, 'in'),
                gridGn=Track.genLinear10
            )
            self.fail('Track.ExceptionTotalDepthLISPlotTrack not raised')
        except Track.ExceptionTotalDepthLISPlotTrack:
            pass
        
    def test_11(self):
        """TestPlotTrack.test_11(): Construct a linear track with left edge < right edge - fails."""
        try:
            Track.Track(
                leftPos=Coord.Dim(5.6, 'in'), 
                rightPos=Coord.Dim(3.2, 'in'),
                gridGn=Track.genLinear10
            )
            self.fail('Track.ExceptionTotalDepthLISPlotTrack not raised')
        except Track.ExceptionTotalDepthLISPlotTrack:
            pass
        

     
class Special(unittest.TestCase):
    """Special tests."""
    pass


def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTrackGenLines))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotTrack))
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
    clkStart = time.clock()
    unitTest()
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')

if __name__ == "__main__":
    main()
