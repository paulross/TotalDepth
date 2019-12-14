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

import os
import sys
import time
import logging
#import math
import pprint
import io
import random
#import collections
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

import pytest

from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import RepCode
from TotalDepth.LIS.core import LisGen
from TotalDepth.LIS.core import FileIndexer
from TotalDepth.LIS.core import EngVal
from TotalDepth.LIS.core import Mnem
# LAS
from TotalDepth.LAS.core import LASRead
# Plot
from TotalDepth.util.plot import Coord
#from TotalDepth.util.plot import XGrid
from TotalDepth.util.plot import Plot
from TotalDepth.util.plot import PlotConstants
from TotalDepth.util.plot import FILMCfgXML
from TotalDepth.util.plot import PRESCfgXML
from TotalDepth.util import XmlWrite
from TotalDepth.util import ExecTimer

######################
# Section: Unit tests.
######################
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__)))
import TestPlotShared
import TestLogHeader
import TestPlotLASData
import TestLgFormatXMLData
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import BaseTestClasses

#=================================================
# Section: Managing where our test SVG is written.
#=================================================
# This is a global map that has a (sortable) key, typically and int to a
# file location and description
TEST_SVG_FILE_MAP_LIS = {
#    0 : TestPlotShared.SVGTestOutput('test_plot_00.svg', 'Test plot')
    1   : TestPlotShared.SVGTestOutput(
            'SP_sin.svg',
            "TestPlotReadLIS_SingleSinCurve.test_01(): Sinusoidal SP plotted on a number of different scales."
        ),
    2   : TestPlotShared.SVGTestOutput(
            'SP_square_lowfreq.svg',
            "TestPlotReadLIS_SingleSquareCurveLowFreq.test_01(): Square wave with 4' spacing to check wrap interpolation."
        ),
    3   : TestPlotShared.SVGTestOutput(
            'SP_square_highfreq.svg',
            "TestPlotReadLIS_SingleSquareCurveHighFreq.test_01(): Square wave with 0.5' spacing to check wrap interpolation."
        ),
    3.1   : TestPlotShared.SVGTestOutput(
            'SP_square_superhighfreq.svg',
            "TestPlotReadLIS_SingleSquareCurveSuperHighFreq.test_01(): Square wave with 0.5' spacing to check super high wrap interpolation."
        ),
    4   : TestPlotShared.SVGTestOutput(
            'HDT_00.svg',
            "TestPlotReadLIS_HDT.test_01(): 50 feet of HDT on a 1:200 scale."
        ),
    4.1   : TestPlotShared.SVGTestOutput(
            'HDT_01.svg',
            "TestPlotReadLIS_HDT_20.test_01(): 50 feet of HDT on a 1:20 scale."
        ),
    4.2   : TestPlotShared.SVGTestOutput(
            'HDT_02.svg',
            "TestPlotReadLIS_HDT_40.test_01(): 50 feet of HDT on a 1:40 scale."
        ),
    5   : TestPlotShared.SVGTestOutput(
            'SuperSampled.svg',
            "TestPlotReadLIS_SuperSampled.test_01(): Channels at 4' frame spacing, single, x8, x32 super-sampling."
        ),
    6   : TestPlotShared.SVGTestOutput(
            'COLOName.svg',
            "TestPlotReadLIS_COLO_Named.test_01(): Sinusoidal SP plotted on a number of different named colours."
        ),
    7   : TestPlotShared.SVGTestOutput(
            'COLONumber.svg',
            "TestPlotReadLIS_COLO_Numbered.test_01(): Numbered colours 400 (red), 040 (green), 004 (blue)."
        ),
    8   : TestPlotShared.SVGTestOutput(
            'COLONumber_Comp.svg',
            "TestPlotReadLIS_COLO_Numbered_Comp.test_01(): Numbered colours 440 (yellow), 404 (magenta), 044 (cyan)."
        ),
    9   : TestPlotShared.SVGTestOutput(
            'Performance_00_01.svg',
            "TestPlotReadLIS_Perf_00.test_01(): Film 1 2000' of 10 curves, linear scale."
        ),
    10  : TestPlotShared.SVGTestOutput(
            'Performance_00_02.svg',
            "TestPlotReadLIS_Perf_00.test_02(): Film 2 2000' of 10 curves, linear and log scale."
        ),
    # Format from XML LgFormat files
    20  : TestPlotShared.SVGTestOutput(
            'Triple_Combo_00_LIS.svg',
            "LgFormat: \"Triple_Combo_00\" 2000 of 10 curves, linear and log scale."
        ),
    21  : TestPlotShared.SVGTestOutput(
            'Resistivity_3Track_Logrithmic.xml_00_LIS.svg',
            "LgFormat: \"Resistivity_3Track_Logrithmic.xml_00\" 2000' of 10 curves, linear and log scale."
        ),
    22  : TestPlotShared.SVGTestOutput(
            'HDT_Example.svg',
            "LgFormat: \"HDT_Example.svg\" 25' of example HDT on 1:40 scale with API header."
        ),
    # With API Header
    30   : TestPlotShared.SVGTestOutput(
            'SP_sin_api.svg',
            "TestPlotReadLIS_SingleSinCurve.test_01(): Sinusoidal SP plotted on a number of different scales with API header."
        ),
}

# LAS data
TEST_SVG_FILE_MAP_LAS = {
    # Format from XML LgFormat files and LAS data
    # test_01
    40  : TestPlotShared.SVGTestOutput(
            'Triple_Combo_40_LAS.svg',
            "LgFormat: \"Triple_Combo\" 200 of 15 curves, linear and log scale from LAS file, DOWN log, no header."
        ),
    41  : TestPlotShared.SVGTestOutput(
            'Resistivity_3Track_Logrithmic.xml_41_LAS.svg',
            "LgFormat: \"Resistivity_3Track_Logrithmic.xml\" 200' of 15 curves, linear and log scale from LAS file, DOWN log, no header."
        ),
    # test_02
    42  : TestPlotShared.SVGTestOutput(
            'Triple_Combo_42_LAS.svg',
            "LgFormat: \"Triple_Combo\" 200 of 10 curves, linear and log scale from LAS file, DOWN log, with header."
        ),
    43  : TestPlotShared.SVGTestOutput(
            'Resistivity_3Track_Logrithmic.xml_43_LAS.svg',
            "LgFormat: \"Resistivity_3Track_Logrithmic.xml\" 200' of 15 curves, linear and log scale from LAS file, DOWN log, with header."
        ),
    # test_03
    44  : TestPlotShared.SVGTestOutput(
            'Triple_Combo_44_LAS.svg',
            "LgFormat: \"Triple_Combo\" 200 of 15 curves, linear and log scale from LAS file, UP log, no header."
        ),
    45  : TestPlotShared.SVGTestOutput(
            'Resistivity_3Track_Logrithmic.xml_45_LAS.svg',
            "LgFormat: \"Resistivity_3Track_Logrithmic.xml\" 200' of 15 curves, linear and log scale from LAS file, UP log, no header."
        ),
    # test_04
    46  : TestPlotShared.SVGTestOutput(
            'Triple_Combo_46_LAS.svg',
            "LgFormat: \"Triple_Combo\" 200 of 15 curves, linear and log scale from LAS file, UP log, with header."
        ),
    47  : TestPlotShared.SVGTestOutput(
            'Resistivity_3Track_Logrithmic.xml_47_LAS.svg',
            "LgFormat: \"Resistivity_3Track_Logrithmic.xml\" 200' of 15 curves, linear and log scale from LAS file, UP log, with header."
        ),
    # test_10
    48  : TestPlotShared.SVGTestOutput(
            'Triple_Combo_48_LAS.svg',
            "LgFormat: \"Triple_Combo\" 1000 of 15 curves, linear and log scale from LAS file, large down log, with header."
        ),
    49  : TestPlotShared.SVGTestOutput(
            'Resistivity_3Track_Logrithmic.xml_49_LAS.svg',
            "LgFormat: \"Resistivity_3Track_Logrithmic.xml\" 1000' of 15 curves, linear and log scale from LAS file, large down log, with header."
        ),
    # test_11
    50  : TestPlotShared.SVGTestOutput(
            'Triple_Combo_50_LAS.svg',
            "LgFormat: \"Triple_Combo\" 100 feet of 5 gamma ray curves."
        ),
    51  : TestPlotShared.SVGTestOutput(
            'Resistivity_3Track_Logrithmic.xml_51_LAS.svg',
            "LgFormat: \"Resistivity_3Track_Logrithmic.xml\" 100 feet of 5 gamma ray curves."
        ),
    # test_12
    52  : TestPlotShared.SVGTestOutput(
            'Porosity_GR_3Track_52_LAS.svg',
            "LgFormat: \"Porosity_GR_3Track\" 100 feet of Density, porosity and 5 gamma ray curves."
        ),
}

def writeTestSVGIndex():
    """Write the TEST_SVG_FILE_MAP_LIS as an index.html."""
    if not os.path.isdir(TestPlotShared.outPath('')):
        os.makedirs(TestPlotShared.outPath(''))
    with XmlWrite.XhtmlStream(open(TestPlotShared.outPath('index.html'), 'w')) as xS:
        with XmlWrite.Element(xS, 'h1', {}):
            xS.characters('API Headers')
        with XmlWrite.Element(xS, 'ol'):
            for k in sorted(TestLogHeader.TEST_SVG_FILE_MAP_HDR.keys()):
                with XmlWrite.Element(xS, 'li'):
                    with XmlWrite.Element(xS, 'a', {'href' : TestLogHeader.TEST_SVG_FILE_MAP_HDR[k].fileName}):
                        xS.characters('link')
                    xS.characters(' ')
                    xS.characters(TestLogHeader.TEST_SVG_FILE_MAP_HDR[k].description)
        with XmlWrite.Element(xS, 'h1', {}):
            xS.characters('Plots from LIS files')
        with XmlWrite.Element(xS, 'ol'):
            for k in sorted(TEST_SVG_FILE_MAP_LIS.keys()):
                with XmlWrite.Element(xS, 'li'):
                    with XmlWrite.Element(xS, 'a', {'href' : TEST_SVG_FILE_MAP_LIS[k].fileName}):
                        xS.characters('link')
                    xS.characters(' ')
                    xS.characters(TEST_SVG_FILE_MAP_LIS[k].description)
        with XmlWrite.Element(xS, 'h1', {}):
            xS.characters('Plots from LAS files')
        with XmlWrite.Element(xS, 'ol'):
            for k in sorted(TEST_SVG_FILE_MAP_LAS.keys()):
                with XmlWrite.Element(xS, 'li'):
                    with XmlWrite.Element(xS, 'a', {'href' : TEST_SVG_FILE_MAP_LAS[k].fileName}):
                        xS.characters('link')
                    xS.characters(' ')
                    xS.characters(TEST_SVG_FILE_MAP_LAS[k].description)
#=================================================
# End: Managing where our test SVG is written.
#=================================================

class TestPlotRollStatic(unittest.TestCase):
    """Simple arrangement of PlotRoll."""
    def setUp(self):
        """Set up."""
        self._plotRoll = Plot.PlotRoll(
            EngVal.EngVal(1000.0, b'FEET'),
            EngVal.EngVal(900.0, b'FEET'),
            200,
            Coord.Dim(2.0, 'in'),
            plotUp=True)

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotRollStatic.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestPlotRollStatic.test_01(): viewBox."""
#        print()
#        print(myPr.viewBox)
        self.assertEqual(
            Coord.Box(
                Coord.Dim(8.5, 'in'),
                Coord.Dim(.25+2.0+12*(1000.0-900.0)/200.0+2.0+.25, 'in'),
                ),
            self._plotRoll.viewBox,
        )

    def test_02(self):
        """TestPlotRollStatic.test_02(): width/depth."""
        self.assertEqual(8.5, self._plotRoll.width)
        self.assertEqual(10.5, self._plotRoll.depth)

    def test_03(self):
        """TestPlotRollStatic.test_03(): header pane, top=True."""
        self.assertEqual(
            (
                Coord.Pt(
                    Coord.Dim(.25, 'in'),
                    Coord.Dim(.25, 'in'),
                ),
                Coord.Box(
                    Coord.Dim(8.0, 'in'),
                    Coord.Dim(2.0, 'in'),
                    ),
            ),
            self._plotRoll.retLegendPane(isTop=True),
        )

    def test_04(self):
        """TestPlotRollStatic.test_04(): header pane, top=False."""
        self.assertEqual(
            (
                Coord.Pt(
                    Coord.Dim(0.25, 'in'),
                    Coord.Dim(8.25, 'in'),
                ),
                Coord.Box(
                    Coord.Dim(8.0, 'in'),
                    Coord.Dim(2.0, 'in'),
                    ),
            ),
            self._plotRoll.retLegendPane(isTop=False),
        )
        
    def test_05(self):
        """TestPlotRollStatic.test_05(): main pane."""
        self.assertEqual(
            (
                Coord.Pt(
                    Coord.Dim(0.25, 'in'),
                    Coord.Dim(2.25, 'in'),
                ),
                Coord.Box(
                    Coord.Dim(8.0, 'in'),
                    Coord.Dim(6.0, 'in'),
                    ),
            ),
            self._plotRoll.retMainPane(),
        )

    def test_06(self):
        """TestPlotRollStatic.test_06(): widthDim()."""
        self.assertEqual(Coord.Dim(8.5, 'in'), self._plotRoll.widthDim)
    
    def test_07(self):
        """TestPlotRollStatic.test_07(): depthDim()."""
        self.assertEqual(Coord.Dim(10.5, 'in'), self._plotRoll.depthDim)
    
    def test_08(self):
        """TestPlotRollStatic.test_08(): property trackTopLeft."""
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(0.25, 'in'),
                Coord.Dim(2.25, 'in'),
            ),
            self._plotRoll.trackTopLeft
        )
    
    def test_09(self):
        """TestPlotRollStatic.test_09(): property mainPanePlotDepth."""
        self.assertEqual(
            Coord.Dim(6.0, 'in'),
            self._plotRoll.mainPanePlotDepth
        )
    
    def test_10(self):
        """TestPlotRollStatic.test_10(): retMainPaneStart()."""
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(0.25, 'in'),
                Coord.Dim(8.25, 'in'),
            ),
            self._plotRoll.retMainPaneStart()
        )
    
class TestPlotRoll(unittest.TestCase):
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotRoll.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_02(self):
        """TestPlotRoll.test_02(): X axis tests (up plot)."""
        myPr = Plot.PlotRoll(
            EngVal.EngVal(1000.0, b'FEET'),
            EngVal.EngVal(900.0, b'FEET'),
            200,
            Coord.Dim(2.0, 'in'),
            plotUp=True)
#        print()
#        print(myPr.viewBox)
        self.assertEqual(
            Coord.Box(Coord.Dim(8.5, 'in'), Coord.Dim(10.5, 'in')),
            myPr.viewBox
        )
#        print('myPr.retMainPane()', myPr.retMainPane())
        self.assertEqual(
            (
                Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(2.25, 'in')),
                Coord.Box(Coord.Dim(8.0, 'in'), Coord.Dim(6.0, 'in')),
            ),
            myPr.retMainPane(),
        )
#        print()
#        print('myPr.xDepth(1000.0)', myPr.xDepth(1000.0))
#        print('myPr.xDepth( 950.0)', myPr.xDepth(950.0))
#        print('myPr.xDepth( 900.0)', myPr.xDepth(900.0))
        self.assertEqual(Coord.Dim(8.25, 'in'), myPr.xDepth(1000.0))
        self.assertEqual(Coord.Dim(5.25, 'in'), myPr.xDepth(950.0))
        self.assertEqual(Coord.Dim(2.25, 'in'), myPr.xDepth(900.0))

    def test_03(self):
        """TestPlotRoll.test_03(): X axis tests (down plot)."""
        myPr = Plot.PlotRoll(
            EngVal.EngVal(1000.0, b'FEET'),
            EngVal.EngVal(900.0, b'FEET'),
            200,
            Coord.Dim(2.0, 'in'),
            plotUp=False)
#        print()
#        print(myPr.viewBox)
        self.assertEqual(
            Coord.Box(Coord.Dim(8.5, 'in'), Coord.Dim(10.5, 'in')),
            myPr.viewBox
        )
#        print('myPr.retMainPane()', myPr.retMainPane())
        self.assertEqual(
            (
                Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(2.25, 'in')),
                Coord.Box(Coord.Dim(8.0, 'in'), Coord.Dim(6.0, 'in')),
            ),
            myPr.retMainPane(),
        )
#        print()
#        print('myPr.xDepth(1000.0)', myPr.xDepth(1000.0))
#        print('myPr.xDepth( 950.0)', myPr.xDepth(950.0))
#        print('myPr.xDepth( 900.0)', myPr.xDepth(900.0))
        self.assertEqual(Coord.Dim(2.25, 'in'), myPr.xDepth(1000.0))
        self.assertEqual(Coord.Dim(5.25, 'in'), myPr.xDepth(950.0))
        self.assertEqual(Coord.Dim(8.25, 'in'), myPr.xDepth(900.0))

    def test_04(self):
        """TestPlotRoll.test_04(): X axis tests (up plot), mixed X units takes X start units."""
        myPr = Plot.PlotRoll(
            EngVal.EngVal(200.0, b'FEET'),
            EngVal.EngVal(0.0, b'M   '),
            200,
            Coord.Dim(2.0, 'in'),
            plotUp=True)
#        print()
#        print(myPr.viewBox)
        self.assertEqual(
            Coord.Box(Coord.Dim(8.5, 'in'), Coord.Dim(16.5, 'in')),
            myPr.viewBox
        )
#        print('myPr.retMainPane()', myPr.retMainPane())
        self.assertEqual(
            (
                Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(2.25, 'in')),
                Coord.Box(Coord.Dim(8.0, 'in'), Coord.Dim(12.0, 'in')),
            ),
            myPr.retMainPane(),
        )
#        print()
#        print('myPr.xDepth(1000.0)', myPr.xDepth(1000.0))
#        print('myPr.xDepth( 950.0)', myPr.xDepth(950.0))
#        print('myPr.xDepth( 900.0)', myPr.xDepth(900.0))
        self.assertEqual(Coord.Dim(14.25, 'in'), myPr.xDepth(200.0))
        self.assertEqual(Coord.Dim(11.25, 'in'), myPr.xDepth(150.0))
        self.assertEqual(Coord.Dim(8.25, 'in'), myPr.xDepth(100.0))
        self.assertEqual(Coord.Dim(5.25, 'in'), myPr.xDepth(50.0))
        self.assertEqual(Coord.Dim(2.25, 'in'), myPr.xDepth(0.0))

    def test_05(self):
        """TestPlotRoll.test_05(): X axis tests (up plot), mixed X units takes X start units, xDepth with an EngVal."""
        myPr = Plot.PlotRoll(
            EngVal.EngVal(200.0, b'FEET'),
            # We use zero since floating point conversions make exact testing a little tedious
            EngVal.EngVal(0.0, b'M   '),
            200,
            Coord.Dim(2.0, 'in'),
            plotUp=True)
        self.assertEqual(
            Coord.Box(Coord.Dim(8.5, 'in'), Coord.Dim(16.5, 'in')),
            myPr.viewBox
        )
#        print('myPr.retMainPane()', myPr.retMainPane())
        self.assertEqual(
            (
                Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(2.25, 'in')),
                Coord.Box(Coord.Dim(8.0, 'in'), Coord.Dim(12.0, 'in')),
            ),
            myPr.retMainPane(),
        )
#        print()
#        print('myPr.xDepth(1000.0)', myPr.xDepth(1000.0))
#        print('myPr.xDepth( 950.0)', myPr.xDepth(950.0))
#        print('myPr.xDepth( 900.0)', myPr.xDepth(900.0))
        self.assertEqual(Coord.Dim(14.25, 'in'), myPr.xDepth(200.0))
        self.assertEqual(Coord.Dim(14.25, 'in'), myPr.xDepth(EngVal.EngVal(200.0, b'FEET')))
        self.assertEqual(Coord.Dim(11.25, 'in'), myPr.xDepth(150.0))
        self.assertEqual(Coord.Dim(11.25, 'in'), myPr.xDepth(EngVal.EngVal(150.0, b'FEET')))
        self.assertEqual(Coord.Dim(8.25, 'in'), myPr.xDepth(100.0))
        self.assertEqual(Coord.Dim(8.25, 'in'), myPr.xDepth(EngVal.EngVal(100.0, b'FEET')))
        self.assertEqual(Coord.Dim(8.25, 'in'), myPr.xDepth(EngVal.EngVal(100.0*0.3048, b'M   ')))
        self.assertEqual(Coord.Dim(5.25, 'in'), myPr.xDepth(50.0))
        self.assertEqual(Coord.Dim(5.25, 'in'), myPr.xDepth(EngVal.EngVal(50.0, b'FEET')))
        self.assertEqual(Coord.Dim(2.25, 'in'), myPr.xDepth(0.0))
        self.assertEqual(Coord.Dim(2.25, 'in'), myPr.xDepth(EngVal.EngVal(0.0, b'FEET')))
        self.assertEqual(Coord.Dim(2.25, 'in'), myPr.xDepth(EngVal.EngVal(0.0, b'M   ')))

    def test_06(self):
        """TestPlotRoll.test_06(): polyLinePlot() with an EngVal."""
        myPr = Plot.PlotRoll(
            EngVal.EngVal(200.0, b'FEET'),
            # We use zero since floating point conversions make exact testing a little tedious
            EngVal.EngVal(0.0, b'M   '),
            200,
            Coord.Dim(2.0, 'in'),
            plotUp=True)
        self.assertEqual(
            Coord.Box(Coord.Dim(8.5, 'in'), Coord.Dim(16.5, 'in')),
            myPr.viewBox
        )
#        print('myPr.retMainPane()', myPr.retMainPane())
        self.assertEqual(
            (
                Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(2.25, 'in')),
                Coord.Box(Coord.Dim(8.0, 'in'), Coord.Dim(12.0, 'in')),
            ),
            myPr.retMainPane(),
        )
        self.assertEqual(Coord.Dim(8.25, 'in'), myPr.xDepth(100.0))
        # TODO: Eh? Surely these should be in 'px' not 'in'
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(0.25*PlotConstants.VIEW_BOX_UNITS_PER_PLOT_UNITS, 'in'),
                Coord.Dim(8.25*PlotConstants.VIEW_BOX_UNITS_PER_PLOT_UNITS, 'in')),
            myPr.polyLinePt(100.0, 0.0),
        )

    def test_10(self):
        """TestPlotRoll.test_10(): Header, no tail."""
        myPr = Plot.PlotRoll(
            EngVal.EngVal(1000.0, b'FEET'),
            EngVal.EngVal(900.0, b'FEET'),
            200,
            Coord.Dim(2.0, 'in'), # Legend
            theHeadDepth=Coord.Dim(4.5, 'in'),
        )
        self.assertEqual(
            Coord.Box(Coord.Dim(8.5, 'in'), Coord.Dim(15.0, 'in')),
            myPr.viewBox
        )
        self.assertEqual(
            (
                Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(6.75, 'in')),
                Coord.Box(Coord.Dim(8.0, 'in'), Coord.Dim(6.0, 'in')),
            ),
            myPr.retMainPane(),
        )
        self.assertEqual(
            (
                Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(0.25, 'in')),
                Coord.Box(Coord.Dim(8.0, 'in'), Coord.Dim(4.5, 'in')),
            ),
            myPr.retHeadPane(),
        )
        self.assertEqual(
            (
                Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(14.75, 'in')),
                Coord.Box(Coord.Dim(8.0, 'in'), Coord.Dim(0.0, 'in')),
            ),
            myPr.retTailPane(),
        )

    def test_11(self):
        """TestPlotRoll.test_11(): Tail, no header."""
        myPr = Plot.PlotRoll(
            EngVal.EngVal(1000.0, b'FEET'),
            EngVal.EngVal(900.0, b'FEET'),
            200,
            Coord.Dim(2.0, 'in'), # Legend
            theTailDepth=Coord.Dim(4.5, 'in'),
        )
        self.assertEqual(
            Coord.Box(Coord.Dim(8.5, 'in'), Coord.Dim(15.0, 'in')),
            myPr.viewBox
        )
        self.assertEqual(
            (
                Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(2.25, 'in')),
                Coord.Box(Coord.Dim(8.0, 'in'), Coord.Dim(6.0, 'in')),
            ),
            myPr.retMainPane(),
        )
        self.assertEqual(
            (
                Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(0.25, 'in')),
                Coord.Box(Coord.Dim(8.0, 'in'), Coord.Dim(0, 'in')),
            ),
            myPr.retHeadPane(),
        )
        self.assertEqual(
            (
                Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(10.25, 'in')),
                Coord.Box(Coord.Dim(8.0, 'in'), Coord.Dim(4.5, 'in')),
            ),
            myPr.retTailPane(),
        )

    def test_20(self):
        """TestPlotRoll.test_20(): Failure when empty units."""
        try:
            Plot.PlotRoll(
                EngVal.EngVal(1000.0, b'    '),
                EngVal.EngVal(900.0, b'    '),
                200,
                Coord.Dim(2.0, 'in'),
                plotUp=True,
            )
            self.fail('Plot.ExceptionTotalDepthPlotRoll not raised.')
        except Plot.ExceptionTotalDepthPlotRoll:
            pass

class TestPlotBase(BaseTestClasses.TestBaseFile):
    pass

class TestPlotBase_00(TestPlotBase):
    """Base class that has a typical FILM and PRES table."""
    def retFilmBytes(self):
        return b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1   ' \
                    + b'EA\x04\x00GCOD    E20 ' \
                    + b'EA\x04\x00GDEC    -4--' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    2   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D200'

    def retPresBytes(self):
        return bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    SP  '
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
            + b'\x00A\x04\x00MNEM    CALI'
                + b'EA\x04\x00OUTP    CALI'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LDAS'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDGIN  A\xd0\x00\x00'
                + b'ED\x04\x00REDGIN  Bx\x00\x00'
            + b'\x00A\x04\x00MNEM    MINV'
                + b'EA\x04\x00OUTP    MINV'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDG    B\xf8\x00\x00'
                + b'ED\x04\x00REDG    \x00\x00\x00\x00'
            + b'\x00A\x04\x00MNEM    MNOR'
                + b'EA\x04\x00OUTP    MNOR'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LDAS'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDG    B\xf8\x00\x00'
                + b'ED\x04\x00REDG    \x00\x00\x00\x00'
            + b'\x00A\x04\x00MNEM    LLD\x00'
                + b'EA\x04\x00OUTP    LLD '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T23 '
                + b'EA\x04\x00CODI    LDAS'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    GRAD'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDGOHMM?fff'
                + b'ED\x04\x00REDGOHMME\xfd\x00\x00'
            + b'\x00A\x04\x00MNEM    LLDB'
                + b'EA\x04\x00OUTP    LLD '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HDAS'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    GRAD'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDGOHMME\xfd\x00\x00'
                + b'ED\x04\x00REDGOHMMIa\xa8\x00'
            + b'\x00A\x04\x00MNEM    LLG\x00'
                + b'EA\x04\x00OUTP    LLG '
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T23 '
                + b'EA\x04\x00CODI    LDAS'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    GRAD'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDGOHMM?fff'
                + b'ED\x04\x00REDGOHMME\xfd\x00\x00'
            + b'\x00A\x04\x00MNEM    LLGB'
                + b'EA\x04\x00OUTP    LLG '
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HDAS'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    GRAD'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDGOHMME\xfd\x00\x00'
                + b'ED\x04\x00REDGOHMMIa\xa8\x00'
            + b'\x00A\x04\x00MNEM    LLS\x00'
                + b'EA\x04\x00OUTP    LLS '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T23 '
                + b'EA\x04\x00CODI    LSPO'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    GRAD'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDGOHMM?fff'
                + b'ED\x04\x00REDGOHMME\xfd\x00\x00'
            + b'\x00A\x04\x00MNEM    LLSB'
                + b'EA\x04\x00OUTP    LLS '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HSPO'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    GRAD'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDGOHMME\xfd\x00\x00'
                + b'ED\x04\x00REDGOHMMIa\xa8\x00'
            + b'\x00A\x04\x00MNEM    MSFL'
                + b'EA\x04\x00OUTP    MSFL'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T23 '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    GRAD'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDGOHMM?fff'
                + b'ED\x04\x00REDGOHMME\xfd\x00\x00'
            + b'\x00A\x04\x00MNEM    11\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    12\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    13\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    14\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    15\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    16\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    17\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    18\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    19\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
        )

#    def retFileAndFileIndex_ShortSP(self):
#        """Returns a File and a FileIndexer.FileIndex of DEPt plus a single SP
#        curve.
#        Log is 100 ft, 0.5 ft spacing. SP is a sine curve -80 to 20 mV with a
#        wavelength of 20 feet. i.e. 5 waves."""
#        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortSP():')
#        myEbs = LogiRec.EntryBlockSet()
#        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4))
#        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 68, 0.5))
#        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'FEET'))
#        #print('myEbs.lisByteList()')
#        #pprint.pprint(myEbs.lisByteList())
#        # Create a direct X axis log with b'DEPT' and b'SP  '
#        myLpGen = LisGen.LogPassGen(
#            myEbs,
#            # Output list
#            [
#                LisGen.Channel(
#                    LisGen.ChannelSpec(
#                        b'SP  ', b'ServID', b'ServOrdN', b'MV  ',
#                        45310011, 256, 4, 1, 68
#                    ),
#                    LisGen.ChValsSin(fOffs=0, waveLen=40.0, mid=-30.0, amp=50.0, numSa=1, noise=None),
##                    LisGen.ChValsSpecialSeqSqRoot(fOffs=0, waveLen=20.0, mid=-80.0, amp=100.0, numSa=1, noise=None),
#                ),
#            ],
#            xStart=1000.0,
#            xRepCode=68,
#            xNoise=None,
#        )
#        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortSP(): creating DFSR...')
#        # File Header
#        myData = LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileHead)
#        # Create a File with the DFSR plus some frames
#        myData.extend(self.retPrS(myLpGen.lrBytesDFSR()))
#        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortSP(): creating frames...')
#        framesPerLr = 8
#        numFrames = 201
#        for fNum in range(0, numFrames, framesPerLr):
#            myData.extend(self.retPrS(myLpGen.lrBytes(fNum, framesPerLr)))
#        myData.extend(LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileTail))
#        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortSP(): creating File length={:d} ...'.format(len(myData)))
#        myFile = self._retFileFromBytes(myData, theId='MyFile', flagKg=False)
#        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortSP(): creating FileIndex...')
#        # Create a file index
#        myFileIndex = FileIndexer.FileIndex(myFile)
#        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortSP(): returning File and FileIndex.')
#        return myFile, myFileIndex
        
class TestPlotLowLevelCurvePlotScale(TestPlotBase_00):
    """Tests low level functionality of Plot, generally where no LogPass is initialised."""
    def setUp(self):
        """Set up."""
        myByFilm = self.retFilmBytes()
        myByPres = self.retPresBytes()
        self._prl = Plot.PlotReadLIS(
            LogiRec.LrTableRead(self._retFileSinglePr(myByFilm)),
            LogiRec.LrTableRead(self._retFileSinglePr(myByPres)),
        )

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotLowLevelCurvePlotScale.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPlotLowLevelCurvePlotScale.test_01(): Sort order of CurvePlotScale with pair of same named items."""
        myL = [
            Plot.CurvePlotScale(name=b'NAME',    halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=b'NAME',    halfTrackStart=1, halfTracks=4),
        ]
#        print()
#        pprint.pprint(myL)
#        pprint.pprint(sorted(myL))
        self.assertEqual(
            [
                Plot.CurvePlotScale(name=b'NAME',    halfTrackStart=1, halfTracks=4),
                Plot.CurvePlotScale(name=b'NAME',    halfTrackStart=0, halfTracks=2),
            ],
            sorted(myL),
        )
        
    def test_02(self):
        """TestPlotLowLevelCurvePlotScale.test_02(): Sort order of CurvePlotScale with several same named items."""
        myL = [
            Plot.CurvePlotScale(name=b'NAME',    halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=b'NAME',    halfTrackStart=9, halfTracks=1),
            Plot.CurvePlotScale(name=b'NAME',    halfTrackStart=2, halfTracks=3),
            Plot.CurvePlotScale(name=b'NAME',    halfTrackStart=7, halfTracks=4),
        ]
#        print()
#        pprint.pprint(myL)
        self.assertEqual(
            [
                Plot.CurvePlotScale(name=b'NAME',    halfTrackStart=7, halfTracks=4),
                Plot.CurvePlotScale(name=b'NAME',    halfTrackStart=2, halfTracks=3),
                Plot.CurvePlotScale(name=b'NAME',    halfTrackStart=0, halfTracks=2),
                Plot.CurvePlotScale(name=b'NAME',    halfTrackStart=9, halfTracks=1),
            ],
            sorted(myL),
        )
            
    def test_03(self):
        """TestPlotLowLevelCurvePlotScale.test_03(): Sort order of CurvePlotScale with several different named items."""
        myL = [
            Plot.CurvePlotScale(name=b'A   ',    halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=b'B   ',    halfTrackStart=0, halfTracks=4),
        ]
#        print('\nmyL and sorted myL')
#        pprint.pprint(myL)
#        pprint.pprint(sorted(myL))
        self.assertEqual(
            [
                Plot.CurvePlotScale(name=b'B   ',    halfTrackStart=0, halfTracks=4),
                Plot.CurvePlotScale(name=b'A   ',    halfTrackStart=0, halfTracks=2),
            ],
            sorted(myL),
        )
            
    def test_04(self):
        """TestPlotLowLevelCurvePlotScale.test_04(): Sort order of CurvePlotScale with several different named items."""
        myL = [
            Plot.CurvePlotScale(name=b'B   ',    halfTrackStart=0, halfTracks=4),
            Plot.CurvePlotScale(name=b'B   ',    halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=b'A   ',    halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=b'A   ',    halfTrackStart=0, halfTracks=4),
        ]
#        print('myL and sorted myL')
#        pprint.pprint(myL)
#        print()
#        pprint.pprint(sorted(myL))
        self.assertEqual(
            [
                Plot.CurvePlotScale(name=b'A   ',    halfTrackStart=0, halfTracks=4),
                Plot.CurvePlotScale(name=b'B   ',    halfTrackStart=0, halfTracks=4),
                Plot.CurvePlotScale(name=b'A   ',    halfTrackStart=0, halfTracks=2),
                Plot.CurvePlotScale(name=b'B   ',    halfTrackStart=0, halfTracks=2),
            ],
            sorted(myL),
        )
            
    def test_05(self):
        """TestPlotLowLevelCurvePlotScale.test_05(): Sort order of CurvePlotScale with 4 items - 100 random tests."""
        myL = [
            Plot.CurvePlotScale(name=b'B   ',    halfTrackStart=0, halfTracks=4),
            Plot.CurvePlotScale(name=b'B   ',    halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=b'A   ',    halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=b'A   ',    halfTrackStart=0, halfTracks=4),
        ]
#        print('myL and sorted myL')
#        pprint.pprint(myL)
#        print()
#        pprint.pprint(sorted(myL))
        for i in range(100):
            random.shuffle(myL)
            self.assertEqual(
                [
                    Plot.CurvePlotScale(name=b'A   ',    halfTrackStart=0, halfTracks=4),
                    Plot.CurvePlotScale(name=b'B   ',    halfTrackStart=0, halfTracks=4),
                    Plot.CurvePlotScale(name=b'A   ',    halfTrackStart=0, halfTracks=2),
                    Plot.CurvePlotScale(name=b'B   ',    halfTrackStart=0, halfTracks=2),
                ],
                sorted(myL),
            )
            
    def test_10(self):
        """TestPlotLowLevelCurvePlotScale.test_10(): Sort CurvePlotScale scales from FILM/PRES table."""
#        print()
##        print(b'1   ', self._prl._retCurvePlotScales(Mnem.Mnem(b'1   '), theLp=None))
#        pprint.pprint(self._prl._retCurvePlotScales(Mnem.Mnem(b'1   '), theLp=None))
        self.assertEqual(
            [
                Plot.CurvePlotScale(name=b'LLD\x00',    halfTrackStart=4, halfTracks=4),
                Plot.CurvePlotScale(name=b'LLG\x00',    halfTrackStart=4, halfTracks=4),
                Plot.CurvePlotScale(name=b'LLS\x00',    halfTrackStart=4, halfTracks=4),
                Plot.CurvePlotScale(name=b'MSFL',       halfTrackStart=4, halfTracks=4),
                Plot.CurvePlotScale(name=b'CALI',       halfTrackStart=0, halfTracks=2),
                Plot.CurvePlotScale(name=b'LLDB',       halfTrackStart=4, halfTracks=2),
                Plot.CurvePlotScale(name=b'LLGB',       halfTrackStart=4, halfTracks=2),
                Plot.CurvePlotScale(name=b'LLSB',       halfTrackStart=4, halfTracks=2),
                Plot.CurvePlotScale(name=b'MINV',       halfTrackStart=0, halfTracks=2),
                Plot.CurvePlotScale(name=b'MNOR',       halfTrackStart=0, halfTracks=2),
                Plot.CurvePlotScale(name=b'SP  ',       halfTrackStart=0, halfTracks=2),
            ],
            self._prl._retCurvePlotScales(Mnem.Mnem(b'1   '), theLp=None),
        )
    
    def test_15(self):
        """TestPlotLowLevelCurvePlotScale.test_15(): Plot.CurvePlotScaleSlotMap() from internal data."""
        # This comes from  problem we were having with plotting density/porosity LAS curves
        myCpsS = [
            # From left but in unsorted order
            Plot.CurvePlotScale(name=Mnem.Mnem(b'Cali'), halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'DensityPorosity'), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'NeutronPorosity'), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'RHOB'), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'DRHO'), halfTrackStart=6, halfTracks=2),
        ]
        myCpssm = Plot.CurvePlotScaleSlotMap(myCpsS)
#        print()
#        print('myCpssm._htIdxSet', myCpssm._htIdxSet)
#        print('myCpssm._htIdxMap', myCpssm._htIdxMap)
#        for v in myCpssm.genScaleSliceCurve():
#            print(v)
        self.assertEqual(
            [
                Plot.ScaleSliceCurve(slice=0, curveName=Mnem.Mnem(b'Dens'), start=4, span=4),
                Plot.ScaleSliceCurve(slice=0, curveName=Mnem.Mnem(b'Cali'), start=0, span=2),
                Plot.ScaleSliceCurve(slice=1, curveName=Mnem.Mnem(b'Neut'), start=4, span=4),
                Plot.ScaleSliceCurve(slice=2, curveName=Mnem.Mnem(b'RHOB'), start=4, span=4),
                Plot.ScaleSliceCurve(slice=3, curveName=Mnem.Mnem(b'DRHO'), start=6, span=2),
            ],
            [v for v in myCpssm.genScaleSliceCurve()],
        )

    def test_20(self):
        """TestPlotLowLevelCurvePlotScale.test_20(): Plot.CurvePlotScaleSlotMap() from FILM/PRES table, simple canFit()."""
        myCpssm = Plot.CurvePlotScaleSlotMap(self._prl._retCurvePlotScales(Mnem.Mnem(b'1   '), theLp=None))
#        print()
#        print('myCpssm._htIdxSet', myCpssm._htIdxSet)
#        print('myCpssm._htIdxMap', myCpssm._htIdxMap)
        self.assertTrue(myCpssm.canFit(Plot.CurvePlotScale(name=b'SP  ', halfTrackStart=0, halfTracks=2)))
        
    def test_21(self):
        """TestPlotLowLevelCurvePlotScale.test_21(): Plot.CurvePlotScaleSlotMap() from FILM/PRES table, simple canFit(), fit() and canFit()."""
        myCpssm = Plot.CurvePlotScaleSlotMap(self._prl._retCurvePlotScales(Mnem.Mnem(b'1   '), theLp=None))
#        print()
#        print('myCpssm._htIdxSet', myCpssm._htIdxSet)
#        print('myCpssm._htIdxMap', myCpssm._htIdxMap)
        self.assertTrue(myCpssm.canFit(Plot.CurvePlotScale(name=b'SP  ', halfTrackStart=0, halfTracks=2)))
        myCpssm.fit(Plot.CurvePlotScale(name=b'SP  ', halfTrackStart=0, halfTracks=2))
        self.assertFalse(myCpssm.canFit(Plot.CurvePlotScale(name=b'SP  ', halfTrackStart=0, halfTracks=2)))
        
    def test_22(self):
        """TestPlotLowLevelCurvePlotScale.test_22(): Plot.CurvePlotScaleSlotMap() from FILM/PRES table, simple canFit(), fit(), reset() and repeat."""
        myCpssm = Plot.CurvePlotScaleSlotMap(self._prl._retCurvePlotScales(Mnem.Mnem(b'1   '), theLp=None))
#        print()
#        print('myCpssm._htIdxSet', myCpssm._htIdxSet)
#        print('myCpssm._htIdxMap', myCpssm._htIdxMap)
        self.assertTrue(myCpssm.canFit(Plot.CurvePlotScale(name=b'SP  ', halfTrackStart=0, halfTracks=2)))
        myCpssm.fit(Plot.CurvePlotScale(name=b'SP  ', halfTrackStart=0, halfTracks=2))
        self.assertFalse(myCpssm.canFit(Plot.CurvePlotScale(name=b'SP  ', halfTrackStart=0, halfTracks=2)))
        myCpssm.reset()
        self.assertTrue(myCpssm.canFit(Plot.CurvePlotScale(name=b'SP  ', halfTrackStart=0, halfTracks=2)))
        myCpssm.fit(Plot.CurvePlotScale(name=b'SP  ', halfTrackStart=0, halfTracks=2))
        self.assertFalse(myCpssm.canFit(Plot.CurvePlotScale(name=b'SP  ', halfTrackStart=0, halfTracks=2)))
        
    def test_23(self):
        """TestPlotLowLevelCurvePlotScale.test_23(): Plot.CurvePlotScaleSlotMap() from FILM/PRES table, looping canFit(), fit(), reset()."""
        myCpssm = Plot.CurvePlotScaleSlotMap(self._prl._retCurvePlotScales(Mnem.Mnem(b'1   '), theLp=None))
#        print()
#        print('myCpssm._htIdxSet', myCpssm._htIdxSet)
#        print('myCpssm._htIdxMap', myCpssm._htIdxMap)
        for aCps in self._prl._retCurvePlotScales(Mnem.Mnem(b'1   '), theLp=None):
            if not myCpssm.canFit(aCps):
#                print('myCpssm._htIdxMap slice full:', myCpssm._htIdxMap)
                myCpssm.reset()
            myCpssm.fit(aCps)
#        print('myCpssm._htIdxMap slice full:', myCpssm._htIdxMap)
        
    def test_30(self):
        """TestPlotLowLevelCurvePlotScale.test_30(): _retCurvePlotScaleOrder() from FILM/PRES table."""
        myCpso = self._prl._retCurvePlotScaleOrder(Mnem.Mnem(b'1   '), theLp=None)
#        print()
#        print(myCpso)
#        pprint.pprint(myCpso)
        self.assertEqual(
            [
                Plot.ScaleSliceCurve(slice=0, curveName=b'LLD\x00', start=4, span=4),
                Plot.ScaleSliceCurve(slice=0, curveName=b'CALI', start=0, span=2),
                Plot.ScaleSliceCurve(slice=1, curveName=b'LLG\x00', start=4, span=4),
                Plot.ScaleSliceCurve(slice=1, curveName=b'MINV', start=0, span=2),
                Plot.ScaleSliceCurve(slice=2, curveName=b'LLS\x00', start=4, span=4),
                Plot.ScaleSliceCurve(slice=2, curveName=b'MNOR', start=0, span=2),
                Plot.ScaleSliceCurve(slice=3, curveName=b'MSFL', start=4, span=4),
                Plot.ScaleSliceCurve(slice=3, curveName=b'SP  ', start=0, span=2),
                Plot.ScaleSliceCurve(slice=4, curveName=b'LLDB', start=4, span=2),
                Plot.ScaleSliceCurve(slice=5, curveName=b'LLGB', start=4, span=2),
                Plot.ScaleSliceCurve(slice=6, curveName=b'LLSB', start=4, span=2),
            ],
            myCpso,
        )

    def test_31(self):
        """TestPlotLowLevelCurvePlotScale.test_31(): _retCurvePlotScaleOrder() from FILM/PRES table test number of slices."""
        myCpso = self._prl._retCurvePlotScaleOrder(Mnem.Mnem(b'1   '), theLp=None)
        self.assertEqual(6, max(s.slice for s in myCpso))

class TestPlotLowLevelCurvePlotScaleXML(TestPlotBase_00):
    """Tests low level functionality of Plot for LgFormat XML descriptions."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotLowLevelCurvePlotScaleXML.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPlotLowLevelCurvePlotScaleXML.test_01(): _retCurvePlotScales()."""
        myPrx = Plot.PlotReadXML('Porosity_GR_3Track')
#        print()
#        pprint.pprint(sorted(myPrx._retCurvePlotScales('Porosity_GR_3Track', theLp=None)))
        expResult = [
            Plot.CurvePlotScale(name=Mnem.Mnem(b'APS_CorrectedDolomitePorosity', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'APS_CorrectedLimestinePorosity', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'APS_CorrectedSandstonePorosity', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'CMR_FreeFluidPorosity', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'CMR_POROSITY', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'DPHB', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'DPOR_CDN', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'DensityPorosity', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'EpithermalPorosity', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'NeutronPorosity', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'OLDESTNeutronPorosity', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'OLDNeutronPorosity', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'RHOB', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'RHOZ', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'SIDEWALLNEUTRONPorosity', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'SonicPorosity', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'StdResDensityPorosity', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'TNPB', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'TNPH_CDN', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'TPHI_15', len_mnem=0), halfTrackStart=4, halfTracks=4),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'BitSize', len_mnem=0), halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'C1', len_mnem=0), halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'C2', len_mnem=0), halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'CALI_CDN', len_mnem=0), halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'Cali', len_mnem=0), halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'DRHO', len_mnem=0), halfTrackStart=6, halfTracks=2),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'GammaRay', len_mnem=0), halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'HILTCaliper', len_mnem=0), halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'PCAL', len_mnem=0), halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'ROP5', len_mnem=0), halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'SP', len_mnem=0), halfTrackStart=0, halfTracks=2),
            Plot.CurvePlotScale(name=Mnem.Mnem(b'Tension', len_mnem=0), halfTrackStart=6, halfTracks=2),
        ]
        self.assertEqual(expResult, sorted(myPrx._retCurvePlotScales('Porosity_GR_3Track', theLp=None)))


class TestPlotLowLevel_wrap(TestPlotBase_00):
    """Tests Plot._retInterpolateWrapPoints()."""
    def setUp(self):
        """Set up."""
        myByFilm = self.retFilmBytes()
#        myByPres = self.retPresBytes()
        myByPres = bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    NB  '
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
            + b'\x00A\x04\x00MNEM    SHIF'
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
            + b'\x00A\x04\x00MNEM    WRAP'
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
        )
        self._prl = Plot.PlotReadLIS(
            LogiRec.LrTableRead(self._retFileSinglePr(myByFilm)),
            LogiRec.LrTableRead(self._retFileSinglePr(myByPres)),
        )

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotLowLevel_wrap.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPlotLowLevel_wrap.test_01(): Both wraps off scale left, no backup."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[Mnem.Mnem(b'NB  ')].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[Mnem.Mnem(b'NB  ')].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(5.0, 'in'),
                    wrapPrev=-2,
                    wrapNow=-1,
                )
#        print()
#        print(myPts)
        self.assertEqual((None, [], []), myPts)

    def test_02(self):
        """TestPlotLowLevel_wrap.test_01(): Both wraps off scale right, no backup."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[Mnem.Mnem(b'NB  ')].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[Mnem.Mnem(b'NB  ')].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(5.0, 'in'),
                    wrapPrev=1,
                    wrapNow=2,
                )
#        print()
#        print(myPts)
        self.assertEqual((None, [], []), myPts)

    def test_03(self):
        """TestPlotLowLevel_wrap.test_03(): Both wraps off scale left, SHIF backup."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[b'SHIF'].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[b'SHIF'].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(5.0, 'in'),
                    wrapPrev=-2,
                    wrapNow=-3,
                )
#        print()
#        print(myPts)
        self.assertEqual((None, [], []), myPts)

    def test_04(self):
        """TestPlotLowLevel_wrap.test_04(): Both wraps off scale right, SHIF backup."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[b'SHIF'].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[b'SHIF'].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(5.0, 'in'),
                    wrapPrev=2,
                    wrapNow=3,
                )
#        print()
#        print(myPts)
        self.assertEqual((None, [], []), myPts)

    def test_10(self):
        """TestPlotLowLevel_wrap.test_10(): Simple NB no backup that wraps centreline to right edge."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[Mnem.Mnem(b'NB  ')].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[Mnem.Mnem(b'NB  ')].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=0,
                    wrapNow=1,
                )
#        print()
#        print(myPts)
        self.assertEqual(
            (
                (1005.0, Coord.Dim(value=2.4, units='in')),
                [],
                [],
            ),
            myPts,
        )

    def test_11(self):
        """TestPlotLowLevel_wrap.test_11(): Simple NB no backup that wraps centreline to left edge."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[Mnem.Mnem(b'NB  ')].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[Mnem.Mnem(b'NB  ')].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=0,
                    wrapNow=-1,
                )
#        print()
#        print(myPts)
        self.assertEqual(
            (
                (1005.0, Coord.Dim(value=0.0, units='in')),
                [],
                [],
            ),
            myPts,
        )

    def test_12(self):
        """TestPlotLowLevel_wrap.test_12(): Simple NB no backup, both wraps off-scale right."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[Mnem.Mnem(b'NB  ')].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[Mnem.Mnem(b'NB  ')].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=1,
                    wrapNow=2,
                )
#        print()
#        print(myPts)
        self.assertEqual((None, [], []), myPts)

    def test_13(self):
        """TestPlotLowLevel_wrap.test_13(): Simple NB no backup, both wraps off-scale left."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[Mnem.Mnem(b'NB  ')].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[Mnem.Mnem(b'NB  ')].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=-1,
                    wrapNow=-2,
                )
#        print()
#        print(myPts)
        self.assertEqual((None, [], []), myPts)

    def test_14(self):
        """TestPlotLowLevel_wrap.test_14(): Simple NB no backup, comes back on-scale from right."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[Mnem.Mnem(b'NB  ')].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[Mnem.Mnem(b'NB  ')].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=1,
                    wrapNow=0,
                )
#        print()
#        print(myPts)
        self.assertEqual(
            (
                None,
                [],
                [
                    (1005.0, Coord.Dim(value=2.4, units='in')),
                    (1000.0, Coord.Dim(value=1.2, units='in')),
                ],
             ),
            myPts,
        )

    def test_15(self):
        """TestPlotLowLevel_wrap.test_15(): Simple NB no backup, comes back on-scale from left."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[Mnem.Mnem(b'NB  ')].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[Mnem.Mnem(b'NB  ')].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=-1,
                    wrapNow=0,
                )
#        print()
#        print(myPts)
        self.assertEqual(
            (
                None,
                [],
                [
                    (1005.0, Coord.Dim(value=0.0, units='in')),
                    (1000.0, Coord.Dim(value=1.2, units='in')),
                 ],
            ),
            myPts,
        )

    def test_16(self):
        """TestPlotLowLevel_wrap.test_16(): Simple SHIF backup, centreline-centreline to right."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[b'SHIF'].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[b'SHIF'].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=0,
                    wrapNow=1,
                )
#        print()
#        print(myPts)
        self.assertEqual(
            (
                (1005.0, Coord.Dim(value=2.4, units='in')),
                [],
                [
                    (1005.0, Coord.Dim(value=0.0, units='in')),
                    (1000.0, Coord.Dim(value=1.2, units='in')),
                ],
             ),
            myPts,
        )

    def test_17(self):
        """TestPlotLowLevel_wrap.test_17(): Simple SHIF backup, centreline-centreline to left."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[b'SHIF'].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[b'SHIF'].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=0,
                    wrapNow=-1,
                )
#        print()
#        print(myPts)
        self.assertEqual(
            (
                (1005.0, Coord.Dim(value=0.0, units='in')),
                [],
                [
                    (1005.0, Coord.Dim(value=2.4, units='in')),
                    (1000.0, Coord.Dim(value=1.2, units='in')),
                ],
             ),
            myPts,
        )

    def test_18(self):
        """TestPlotLowLevel_wrap.test_18(): Simple SHIF backup, centreline to off-scale right."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[b'SHIF'].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[b'SHIF'].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=0,
                    wrapNow=2,
                )
    #        print()
    #        print(myPts)
        self.assertEqual(
            (
                (1007.5, Coord.Dim(value=2.4, units='in')),
                [
                    (1007.5, Coord.Dim(value=0.0, units='in')),
                    (1002.5, Coord.Dim(value=2.4, units='in')),
                ],
                [],
             ),
            myPts,
        )

    def test_19(self):
        """TestPlotLowLevel_wrap.test_19(): Simple SHIF backup, centreline to off-scale left."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[b'SHIF'].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[b'SHIF'].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=0,
                    wrapNow=-2,
                )
#        print()
#        print(myPts)
        self.assertEqual(
            (
                (1007.5, Coord.Dim(value=0.0, units='in')),
                [
                    (1007.5, Coord.Dim(value=2.4, units='in')),
                    (1002.5, Coord.Dim(value=0.0, units='in')),
                ],
                [],
             ),
            myPts,
        )

    def test_20(self):
        """TestPlotLowLevel_wrap.test_20(): Simple SHIF backup, comes back on-scale from right."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[b'SHIF'].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[b'SHIF'].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=2,
                    wrapNow=0,
                )
#        print()
#        print(myPts)
        self.assertEqual(
            (
                None,
                [
                    (1007.5, Coord.Dim(value=2.4, units='in')),
                    (1002.5, Coord.Dim(value=0.0, units='in')),
                ],
                [
                    (1002.5, Coord.Dim(value=2.4, units='in')),
                    (1000.0, Coord.Dim(value=1.2, units='in')),
                ],
            ),
            myPts,
        )

    def test_21(self):
        """TestPlotLowLevel_wrap.test_21(): Simple SHIF backup, comes back on-scale from right."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[b'SHIF'].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[b'SHIF'].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=-2,
                    wrapNow=0,
                )
#        print()
#        print(myPts)
        self.assertEqual(
            (
                None,
                [
                    (1007.5, Coord.Dim(value=0.0, units='in')),
                    (1002.5, Coord.Dim(value=2.4, units='in')),
                ],
                [
                    (1002.5, Coord.Dim(value=0.0, units='in')),
                    (1000.0, Coord.Dim(value=1.2, units='in')),
                ],
            ),
            myPts,
        )

    def test_22(self):
        """TestPlotLowLevel_wrap.test_22(): Simple WRAP backup, centreline-centreline to right."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[b'WRAP'].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[b'WRAP'].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=0,
                    wrapNow=1,
                )
#        print()
#        print(myPts)
        self.assertEqual(
            (
                (1005.0, Coord.Dim(value=2.4, units='in')),
                [],
                [
                    (1005.0, Coord.Dim(value=0.0, units='in')),
                    (1000.0, Coord.Dim(value=1.2, units='in')),
                ],
             ),
            myPts,
        )

    def test_23(self):
        """TestPlotLowLevel_wrap.test_23(): Simple WRAP backup, centreline-centreline to left."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[b'WRAP'].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[b'WRAP'].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=0,
                    wrapNow=-1,
                )
#        print()
#        print(myPts)
        self.assertEqual(
            (
                (1005.0, Coord.Dim(value=0.0, units='in')),
                [],
                [
                    (1005.0, Coord.Dim(value=2.4, units='in')),
                    (1000.0, Coord.Dim(value=1.2, units='in')),
                ],
             ),
            myPts,
        )

    def test_24(self):
        """TestPlotLowLevel_wrap.test_24(): Simple WRAP backup, centreline-centreline wrap right from 0 to 5."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[b'WRAP'].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[b'WRAP'].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=0,
                    wrapNow=5,
                )
#        print()
#        pprint.pprint(myPts)
        self.assertEqual(
            (
                (1009.0, Coord.Dim(value=2.4, units='in')),
                [
                    (1009.0, Coord.Dim(value=0.0, units='in')),
                    (1007.0, Coord.Dim(value=2.4, units='in')),
                    (1007.0, Coord.Dim(value=0.0, units='in')),
                    (1005.0, Coord.Dim(value=2.4, units='in')),
                    (1005.0, Coord.Dim(value=0.0, units='in')),
                    (1003.0, Coord.Dim(value=2.4, units='in')),
                    (1003.0, Coord.Dim(value=0.0, units='in')),
                    (1001.0, Coord.Dim(value=2.4, units='in')),
                ],
                [
                    (1001.0, Coord.Dim(value=0.0, units='in')),
                    (1000.0, Coord.Dim(value=1.2, units='in')),
                ],
             ),
            myPts,
        )

    def test_25(self):
        """TestPlotLowLevel_wrap.test_25(): Simple WRAP backup, centreline-centreline wrap left from 0 to -5."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[b'WRAP'].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[b'WRAP'].tracValueFunction(Mnem.Mnem(b'1')),
                    xPrev=1010.0,
                    xNow=1000.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=0,
                    wrapNow=-5,
                )
#        print()
#        pprint.pprint(myPts)
        self.assertEqual(
            (
                (1009.0, Coord.Dim(value=0.0, units='in')),
                [
                    (1009.0, Coord.Dim(value=2.4, units='in')),
                    (1007.0, Coord.Dim(value=0.0, units='in')),
                    (1007.0, Coord.Dim(value=2.4, units='in')),
                    (1005.0, Coord.Dim(value=0.0, units='in')),
                    (1005.0, Coord.Dim(value=2.4, units='in')),
                    (1003.0, Coord.Dim(value=0.0, units='in')),
                    (1003.0, Coord.Dim(value=2.4, units='in')),
                    (1001.0, Coord.Dim(value=0.0, units='in')),
                ],
                [
                    (1001.0, Coord.Dim(value=2.4, units='in')),
                    (1000.0, Coord.Dim(value=1.2, units='in')),
                ],
             ),
            myPts,
        )

    @pytest.mark.xfail(reason='need to investigate this.')
    def test_27(self):
        """TestPlotLowLevel_wrap.test_27(): Huge WRAP backup, centreline-centreline wrap left from 0 to 100."""
        myPts = self._prl._retInterpolateWrapPoints(
                    self._prl._presCfg[b'WRAP'].tracWidthData(Mnem.Mnem(b'1')),
                    self._prl._presCfg[b'WRAP'].tracValueFunction(Mnem.Mnem(b'1')),
                    # Highly exagerated X step
                    xPrev=16.0,
                    xNow=0.0,
                    pNow=Coord.Dim(1.2, 'in'),
                    wrapPrev=0,
                    wrapNow=64,
                )
        print()
        pprint.pprint(myPts)
        self.assertEqual(2*Plot.Plot.MAX_BACKUP_TRACK_CROSSING_LINES, len(myPts[1]))
        expResult = (
            (15.875, Coord.Dim(value=2.4, units='in')),
            [
                (15.875, Coord.Dim(value=0.0, units='in')),
                (15.625, Coord.Dim(value=2.4, units='in')),
                (13.875, Coord.Dim(value=0.0, units='in')),
                (13.625, Coord.Dim(value=2.4, units='in')),
                (11.875, Coord.Dim(value=0.0, units='in')),
                (11.625, Coord.Dim(value=2.4, units='in')),
                (9.875, Coord.Dim(value=0.0, units='in')),
                (9.625, Coord.Dim(value=2.4, units='in')),
                (7.875, Coord.Dim(value=0.0, units='in')),
                (7.625, Coord.Dim(value=2.4, units='in')),
                (6.125, Coord.Dim(value=0.0, units='in')),
                (5.875, Coord.Dim(value=2.4, units='in')),
                (4.125, Coord.Dim(value=0.0, units='in')),
                (3.875, Coord.Dim(value=2.4, units='in')),
                (2.125, Coord.Dim(value=0.0, units='in')),
                (1.875, Coord.Dim(value=2.4, units='in')),
            ],
            [
                (0.125, Coord.Dim(value=0.0, units='in')),
                (0.0, Coord.Dim(value=1.2, units='in'))
            ]
        )
        self.assertEqual(expResult, myPts)


@pytest.mark.slow
class TestPlotReadLIS_SingleSinCurve(TestPlotBase_00):
    """Tests plotting a LIS file."""
    def retPresBytes_TEST(self):
        """Returns the PRES logical record with curves from output TEST on various scales and tracks."""
        return bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #40    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      -40.0000       40.0000
            + b'\x00A\x04\x00MNEM    40  '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-40.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(40.0, 68)#B\xd0\x00\x00'
            #20    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      -20.0000       20.0000
            + b'\x00A\x04\x00MNEM    20  '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HDAS'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-20.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
            #10    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      -10.0000       10.0000
            + b'\x00A\x04\x00MNEM    10  '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T3  '
                + b'EA\x04\x00CODI    LGAP'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-10.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(10.0, 68)#B\xd0\x00\x00'
            # Scale -5 to 5
            + b'\x00A\x04\x00MNEM    5   '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HSPO'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-5.0, 68)
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(5.0, 68)
            # Scale -2.5 to 2.5
            + b'\x00A\x04\x00MNEM    2.5 '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T3  '
                + b'EA\x04\x00CODI    LSPO'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-2.5, 68)
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(2.5, 68)
            )

    def retFileAndFileIndex_ShortTEST(self):
        """Returns a File and a FileIndexer.FileIndex of DEPt plus a single curve.
        Log is 100 ft, 0.5 ft spacing. SP is a sine curve -80 to 20 mV with a
        wavelength of 20 feet. i.e. 5 waves."""
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST():')
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 68, 0.5))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'FEET'))
        #print('myEbs.lisByteList()')
        #pprint.pprint(myEbs.lisByteList())
        # Create a direct X axis log with b'DEPT' and b'SP  '
        myLpGen = LisGen.LogPassGen(
            myEbs,
            # Output list
            [
                LisGen.Channel(
                    LisGen.ChannelSpec(
                        b'TEST', b'ServID', b'ServOrdN', b'MV  ',
                        45310011, 256, 4, 1, 68
                    ),
                    LisGen.ChValsSin(fOffs=0, waveLen=160.0, mid=0.0, amp=40.0, numSa=1, noise=None),
#                    LisGen.ChValsSpecialSeqSqRoot(fOffs=0, waveLen=20.0, mid=-80.0, amp=100.0, numSa=1, noise=None),
                ),
            ],
            xStart=1000.0,
            xRepCode=68,
            xNoise=None,
        )
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): creating DFSR...')
        # File Header
        myData = LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileHead)
        # Create a File with the DFSR plus some frames
        myData.extend(self.retPrS(myLpGen.lrBytesDFSR()))
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): creating frames...')
        framesPerLr = 8
        numFrames = 201
        for fNum in range(0, numFrames, framesPerLr):
            myData.extend(self.retPrS(myLpGen.lrBytes(fNum, framesPerLr)))
        myData.extend(LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileTail))
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): creating File length={:d} ...'.format(len(myData)))
        myFile = self._retFileFromBytes(myData, theId='MyFile', flagKg=False)
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): creating FileIndex...')
        # Create a file index
        myFileIndex = FileIndexer.FileIndex(myFile)
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): returning File and FileIndex.')
        return myFile, myFileIndex
        
    def setUp(self):
        """Set up."""
        myByFilm = self.retFilmBytes()
        myByPres = self.retPresBytes_TEST()
        self._prl = Plot.PlotReadLIS(
            LogiRec.LrTableRead(self._retFileSinglePr(myByFilm)),
            LogiRec.LrTableRead(self._retFileSinglePr(myByPres)),
        )
        self._lisFile, self._lisFileIndex = self.retFileAndFileIndex_ShortTEST()

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotReadLIS_SingleSinCurve.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """{:s}""".format(TEST_SVG_FILE_MAP_LIS[1].description)
        for anIlp in self._lisFileIndex.genLogPasses():
            myFout = io.StringIO()
#            myXStart = EngVal.EngVal(9900.0, b'FEET')
#            myXStop = EngVal.EngVal(9600.0, b'FEET')
            myXStart = EngVal.EngVal(1000.0, b'FEET')
            myXStop = EngVal.EngVal(900.0, b'FEET')
            myTimerS = ExecTimer.TimerList()
            self._prl.plotLogPassLIS(
                self._lisFile,
                anIlp.logPass,
                myXStart,
                myXStop,
                Mnem.Mnem(b'2   '),
                TestPlotShared.outPath(TEST_SVG_FILE_MAP_LIS[1].fileName),
                frameStep=1,
                title=TEST_SVG_FILE_MAP_LIS[1].description,
                timerS=myTimerS)
            sys.stderr.write(str(myTimerS))
            sys.stderr.write('\n')
            sys.stderr.flush()


@pytest.mark.slow
class TestPlotReadLIS_SingleSquareCurveLowFreq(TestPlotBase_00):
    """Tests plotting a square wave with a low frequency (4 foot spacing) to illustrate wrapping."""
    TEST_SVG_FILE_MAP_ENTRY = 2
    def retPresBytes_TEST(self):
        """Returns the PRES logical record with curves from output TEST on various scales and tracks."""
        return bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #40    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      -40.0000       40.0000
            + b'\x00A\x04\x00MNEM    40  '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-40.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(40.0, 68)#B\xd0\x00\x00'
            #20    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      -20.0000       20.0000
            + b'\x00A\x04\x00MNEM    20  '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HDAS'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-20.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
            #10    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      -10.0000       10.0000
            + b'\x00A\x04\x00MNEM    8   '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T3  '
                + b'EA\x04\x00CODI    LGAP'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-8.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(8.0, 68)#B\xd0\x00\x00'
            )

    def retFileAndFileIndex(self):
        """Returns a File and a FileIndexer.FileIndex of DEPT plus a single curve.
        Log is 100 ft, 5 ft spacing. SP is a square wave -40 to 40 mV with a
        wavelength of 16 frames feet. i.e. 40 feet."""
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 68, 4.0))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'FEET'))
        #print('myEbs.lisByteList()')
        #pprint.pprint(myEbs.lisByteList())
        # Create a direct X axis log with b'DEPT' and b'SP  '
        myLpGen = LisGen.LogPassGen(
            myEbs,
            # Output list
            [
                LisGen.Channel(
                    LisGen.ChannelSpec(
                        b'TEST', b'ServID', b'ServOrdN', b'MV  ',
                        45310011, 256, 4, 1, 68
                    ),
                    LisGen.ChValsSquare(fOffs=0, waveLen=8.0, mid=0.0, amp=30.0, numSa=1, noise=None),
                ),
            ],
            xStart=1000.0,
            xRepCode=68,
            xNoise=None,
        )
        # File Header
        myData = LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileHead)
        # Create a File with the DFSR plus some frames
        myData.extend(self.retPrS(myLpGen.lrBytesDFSR()))
        framesPerLr = 8
        numFrames = 26
        for fNum in range(0, numFrames, framesPerLr):
            myData.extend(self.retPrS(myLpGen.lrBytes(fNum, framesPerLr)))
        myData.extend(LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileTail))
        myFile = self._retFileFromBytes(myData, theId='MyFile', flagKg=False)
        # Create a file index
        myFileIndex = FileIndexer.FileIndex(myFile)
        return myFile, myFileIndex
        
    def setUp(self):
        """Set up."""
        myByFilm = self.retFilmBytes()
        myByPres = self.retPresBytes_TEST()
        self._prl = Plot.PlotReadLIS(
            LogiRec.LrTableRead(self._retFileSinglePr(myByFilm)),
            LogiRec.LrTableRead(self._retFileSinglePr(myByPres)),
        )
        self._lisFile, self._lisFileIndex = self.retFileAndFileIndex()

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotReadLIS_SingleSquareCurve.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """{:s}""".format(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description)
        for anIlp in self._lisFileIndex.genLogPasses():
            myXStart = EngVal.EngVal(1000.0, b'FEET')
            myXStop = EngVal.EngVal(900.0, b'FEET')
            myTimerS = ExecTimer.TimerList()
            self._prl.plotLogPassLIS(
                self._lisFile,
                anIlp.logPass,
                myXStart,
                myXStop,
                Mnem.Mnem(b'2   '),
                TestPlotShared.outPath(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].fileName),
                frameStep=1,
                title=TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description,
                timerS=myTimerS)
            sys.stderr.write(str(myTimerS))
            sys.stderr.write('\n')
            sys.stderr.flush()


@pytest.mark.slow
class TestPlotReadLIS_SingleSquareCurveHighFreq(TestPlotBase_00):
    """Tests plotting a square wave with a high frequency (0.5 foot spacing) to illustrate wrapping."""
    TEST_SVG_FILE_MAP_ENTRY = 3
    def retPresBytes_TEST(self):
        """Returns the PRES logical record with curves from output TEST on various scales and tracks."""
        return bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #40    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      -40.0000       40.0000
            + b'\x00A\x04\x00MNEM    40  '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-40.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(40.0, 68)#B\xd0\x00\x00'
            #20    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      -20.0000       20.0000
            + b'\x00A\x04\x00MNEM    20  '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HDAS'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-20.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
            #10    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      -10.0000       10.0000
            + b'\x00A\x04\x00MNEM    8   '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T3  '
                + b'EA\x04\x00CODI    LGAP'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(8.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(-8.0, 68)#B\xd0\x00\x00'
            )

    def retFileAndFileIndex(self):
        """Returns a File and a FileIndexer.FileIndex of DEPT plus a single curve.
        Log is 100 ft, .5 ft spacing. SP is a square wave -40 to 40 mV with a
        wavelength of 16 frames feet. i.e. 40 feet."""
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 68, 0.5))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'FEET'))
        #print('myEbs.lisByteList()')
        #pprint.pprint(myEbs.lisByteList())
        # Create a direct X axis log with b'DEPT' and b'SP  '
        myLpGen = LisGen.LogPassGen(
            myEbs,
            # Output list
            [
                LisGen.Channel(
                    LisGen.ChannelSpec(
                        b'TEST', b'ServID', b'ServOrdN', b'MV  ',
                        45310011, 256, 4, 1, 68
                    ),
                    LisGen.ChValsSquare(fOffs=0, waveLen=4*8.0, mid=0.0, amp=30.0, numSa=1, noise=None),
                ),
            ],
            xStart=1000.0,
            xRepCode=68,
            xNoise=None,
        )
        # File Header
        myData = LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileHead)
        # Create a File with the DFSR plus some frames
        myData.extend(self.retPrS(myLpGen.lrBytesDFSR()))
        framesPerLr = 8
        numFrames = 201
        for fNum in range(0, numFrames, framesPerLr):
            myData.extend(self.retPrS(myLpGen.lrBytes(fNum, framesPerLr)))
        myData.extend(LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileTail))
        myFile = self._retFileFromBytes(myData, theId='MyFile', flagKg=False)
        # Create a file index
        myFileIndex = FileIndexer.FileIndex(myFile)
        return myFile, myFileIndex
        
    def setUp(self):
        """Set up."""
        myByFilm = self.retFilmBytes()
        myByPres = self.retPresBytes_TEST()
        self._prl = Plot.PlotReadLIS(
            LogiRec.LrTableRead(self._retFileSinglePr(myByFilm)),
            LogiRec.LrTableRead(self._retFileSinglePr(myByPres)),
        )
        self._lisFile, self._lisFileIndex = self.retFileAndFileIndex()

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotReadLIS_SingleSquareCurveHighFreq.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """{:s}""".format(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description)
        for anIlp in self._lisFileIndex.genLogPasses():
            myXStart = EngVal.EngVal(1000.0, b'FEET')
            myXStop = EngVal.EngVal(900.0, b'FEET')
            myTimerS = ExecTimer.TimerList()
            self._prl.plotLogPassLIS(
                self._lisFile,
                anIlp.logPass,
                myXStart,
                myXStop,
                Mnem.Mnem(b'2   '),
                TestPlotShared.outPath(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].fileName),
                frameStep=1,
                title=TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description,
                timerS=myTimerS)
            sys.stderr.write(str(myTimerS))
            sys.stderr.write('\n')
            sys.stderr.flush()


@pytest.mark.slow
class TestPlotReadLIS_SingleSquareCurveSuperHighFreq(TestPlotBase_00):
    """Tests plotting a square wave with a high frequency (0.5 foot spacing) to illustrate wrapping."""
    TEST_SVG_FILE_MAP_ENTRY = 3.1

    def retFilmBytes(self):
        return b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D20 ' \
                + b'\x00A\x04\x00MNEM    2   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D20 '

    def retPresBytes_TEST(self):
        """Returns the PRES logical record with curves from output TEST on various scales and tracks."""
        return bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #40    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      -40.0000       40.0000
            + b'\x00A\x04\x00MNEM    40  '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-40.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(40.0, 68)#B\xd0\x00\x00'
            #20    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      -20.0000       20.0000
            + b'\x00A\x04\x00MNEM    20  '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HDAS'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-20.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
            #10    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      -10.0000       10.0000
            + b'\x00A\x04\x00MNEM    8   '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T3  '
                + b'EA\x04\x00CODI    LGAP'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(8.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(-8.0, 68)#B\xd0\x00\x00'
            )

    def retFileAndFileIndex(self):
        """Returns a File and a FileIndexer.FileIndex of DEPT plus a single curve.
        Log is 100 ft, .5 ft spacing. SP is a square wave -40 to 40 mV with a
        wavelength of 16 frames feet. i.e. 40 feet."""
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 68, 0.5))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'FEET'))
        #print('myEbs.lisByteList()')
        #pprint.pprint(myEbs.lisByteList())
        # Create a direct X axis log with b'DEPT' and b'SP  '
        myLpGen = LisGen.LogPassGen(
            myEbs,
            # Output list
            [
                LisGen.Channel(
                    LisGen.ChannelSpec(
                        b'TEST', b'ServID', b'ServOrdN', b'MV  ',
                        45310011, 256, 4, 1, 68
                    ),
                    LisGen.ChValsSquare(fOffs=0, waveLen=4*8.0, mid=0.0, amp=300.0, numSa=1, noise=None),
                ),
            ],
            xStart=1000.0,
            xRepCode=68,
            xNoise=None,
        )
        # File Header
        myData = LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileHead)
        # Create a File with the DFSR plus some frames
        myData.extend(self.retPrS(myLpGen.lrBytesDFSR()))
        framesPerLr = 8
        numFrames = 201
        for fNum in range(0, numFrames, framesPerLr):
            myData.extend(self.retPrS(myLpGen.lrBytes(fNum, framesPerLr)))
        myData.extend(LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileTail))
        myFile = self._retFileFromBytes(myData, theId='MyFile', flagKg=False)
        # Create a file index
        myFileIndex = FileIndexer.FileIndex(myFile)
        return myFile, myFileIndex

    def setUp(self):
        """Set up."""
        myByFilm = self.retFilmBytes()
        myByPres = self.retPresBytes_TEST()
        self._prl = Plot.PlotReadLIS(
            LogiRec.LrTableRead(self._retFileSinglePr(myByFilm)),
            LogiRec.LrTableRead(self._retFileSinglePr(myByPres)),
        )
        self._lisFile, self._lisFileIndex = self.retFileAndFileIndex()

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotReadLIS_SingleSquareCurveHighFreq.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """{:s}""".format(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description)
        for anIlp in self._lisFileIndex.genLogPasses():
            myXStart = EngVal.EngVal(1000.0, b'FEET')
            myXStop = EngVal.EngVal(975.0, b'FEET')
            myTimerS = ExecTimer.TimerList()
            self._prl.plotLogPassLIS(
                self._lisFile,
                anIlp.logPass,
                myXStart,
                myXStop,
                Mnem.Mnem(b'2   '),
                TestPlotShared.outPath(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].fileName),
                frameStep=1,
                title=TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description,
                timerS=myTimerS)
            sys.stderr.write(str(myTimerS))
            sys.stderr.write('\n')
            sys.stderr.flush()

class TestPlotReadLIS_HDTBase(TestPlotBase_00):
    """Base class for plotting HDT data."""
    # A list of ((PRES row bytes, ...), LisGenChannel)
    PRES_CHANNEL_DATA = [
        #BS    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      6.0000       16.0000
        (
            (
                b'\x00A\x04\x00MNEM    BS  '
                    + b'EA\x04\x00OUTP    BS  '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T1  '
                    + b'EA\x04\x00CODI    HLIN'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    NB  '
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGINCH' + RepCode.writeBytes(6.0, 68)
                    + b'ED\x04\x00REDGINCH' + RepCode.writeBytes(16.0, 68),
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'BS  ', b'ServID', b'ServOrdN', b'INCH',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsConst(mid=8.0, numSa=1, noise=None),
            ),
        ),
        #GR    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      0.0000       150.0000
        (
            (
                b'\x00A\x04\x00MNEM    GR  '
                    + b'EA\x04\x00OUTP    GR  '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T1  '
                    + b'EA\x04\x00CODI    LLIN'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    WRAP'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGGAPI' + RepCode.writeBytes(0.0, 68)
                    + b'ED\x04\x00REDGGAPI' + RepCode.writeBytes(150.0, 68),
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'GR  ', b'ServID', b'ServOrdN', b'GAPI',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsSin(fOffs=0, waveLen=16*8.0, mid=50.0, amp=40.0, numSa=1, noise=2.0),
            ),
        ),
        #AZIM  ALLO  AZIM  T1    LLIN  BOTH  NB        0.500000      -40.0000       360.000 
        (
            (
                b'\x00A\x04\x00MNEM    AZIM'
                    + b'EA\x04\x00OUTP    AZIM'
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T1  '
                    + b'EA\x04\x00CODI    LLIN'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    NB  '
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGGAPI' + RepCode.writeBytes(-40.0, 68)
                    + b'ED\x04\x00REDGGAPI' + RepCode.writeBytes(360.0, 68),
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'AZIM', b'ServID', b'ServOrdN', b'DEG ',
                    45310011, 256, 4, 1, 68
                ),
                # Wavelength is 100' of 3.2" frames = 375
                LisGen.ChValsSaw(fOffs=10, waveLen=375.0, mid=0.0, amp=360.0, numSa=1, noise=4.0),
            ),
         ),
        #RB    ALLO  RB    T1    LDAS  BOTH  NB        0.500000      -40.0000       360.000 
        (
            (
                b'\x00A\x04\x00MNEM    RB  '
                    + b'EA\x04\x00OUTP    RB  '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T1  '
                    + b'EA\x04\x00CODI    LDAS'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    NB  '
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGGAPI' + RepCode.writeBytes(-40.0, 68)
                    + b'ED\x04\x00REDGGAPI' + RepCode.writeBytes(360.0, 68),
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'RB  ', b'ServID', b'ServOrdN', b'DEG ',
                    45310011, 256, 4, 1, 68
                ),
                # Wavelength is 100' of 3.2" frames = 375
                LisGen.ChValsSaw(fOffs=100, waveLen=375.0, mid=0.0, amp=360.0, numSa=1, noise=4.0),
            ),
         ),
        #DEVI  ALLO  DEVI  T1    LSPO  BOTH  NB        0.500000      -1.00000       9.00000 
        (
            (
                b'\x00A\x04\x00MNEM    DEVI'
                    + b'EA\x04\x00OUTP    DEVI'
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T1  '
                    + b'EA\x04\x00CODI    LLIN'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    NB  '
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGINCH' + RepCode.writeBytes(-1.0, 68)
                    + b'ED\x04\x00REDGINCH' + RepCode.writeBytes(9.0, 68),
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'DEVI', b'ServID', b'ServOrdN', b'INCH',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsConst(mid=7.0, numSa=1, noise=1.0),
            ),
        ),
        #C1    ALLO  C1    T1    LDAS  BOTH  NB        0.500000       6.0000       26.00000 
        (
            (
                b'\x00A\x04\x00MNEM    C1  '
                    + b'EA\x04\x00OUTP    C1  '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T1  '
                    + b'EA\x04\x00CODI    LLIN'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    NB  '
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGINCH' + RepCode.writeBytes(6.0, 68)
                    + b'ED\x04\x00REDGINCH' + RepCode.writeBytes(16.0, 68),
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'C1  ', b'ServID', b'ServOrdN', b'INCH',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsConst(mid=8.0, numSa=1, noise=1.0),
            ),
        ),
        #C2    ALLO  C2    T1    LLIN  BOTH  NB        0.500000       6.0000       26.00000 
        (
            (
                b'\x00A\x04\x00MNEM    C2  '
                    + b'EA\x04\x00OUTP    C2  '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T1  '
                    + b'EA\x04\x00CODI    LDAS'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    NB  '
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGINCH' + RepCode.writeBytes(6.0, 68)
                    + b'ED\x04\x00REDGINCH' + RepCode.writeBytes(16.0, 68),
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'C2  ', b'ServID', b'ServOrdN', b'INCH',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsConst(mid=8.0, numSa=1, noise=1.0),
            ),
        ),
        #FC0   ALLO  FC0   LHT2  LLIN  BOTH  NB        0.500000       0.0000       256.00000 
        (
            (
                b'\x00A\x04\x00MNEM    FC0 '
                    + b'EA\x04\x00OUTP    FC0 '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    LHT2'
                    + b'EA\x04\x00CODI    SFDA'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    NB  '
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGINCH' + RepCode.writeBytes(0.0, 68)
                    + b'ED\x04\x00REDGINCH' + RepCode.writeBytes(255.0, 68),
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'FC0 ', b'ServID', b'ServOrdN', b'    ',
                    45310011, 256, 4*16, 16, 68,
                ),
                LisGen.ChValsConst(mid=127.0, numSa=16, noise=128.0),
            ),
        ),
        #FC1   ALLO  FC1   LHT2  LLIN  BOTH  NB        0.500000       0.0000       256.00000 
        (
            (
                b'\x00A\x04\x00MNEM    FC1 '
                    + b'EA\x04\x00OUTP    FC1 '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    LHT2'
                    + b'EA\x04\x00CODI    SFLN'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    NB  '
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGINCH' + RepCode.writeBytes(0.0, 68)
                    + b'ED\x04\x00REDGINCH' + RepCode.writeBytes(255.0, 68),
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'FC1 ', b'ServID', b'ServOrdN', b'    ',
                    45310011, 256, 4*16, 16, 68,
                ),
                LisGen.ChValsConst(mid=127.0, numSa=16, noise=128.0),
            ),
        ),
        #FC2   ALLO  FC2   RHT2  LLIN  BOTH  NB        0.500000       0.0000       256.00000 
        (
            (
                b'\x00A\x04\x00MNEM    FC2 '
                    + b'EA\x04\x00OUTP    FC2 '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    RHT2'
                    + b'EA\x04\x00CODI    SFLN'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    NB  '
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGINCH' + RepCode.writeBytes(0.0, 68)
                    + b'ED\x04\x00REDGINCH' + RepCode.writeBytes(255.0, 68),
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'FC2 ', b'ServID', b'ServOrdN', b'    ',
                    45310011, 256, 4*16, 16, 68,
                ),
                LisGen.ChValsConst(mid=127.0, numSa=16, noise=128.0),
            ),
        ),
        #FC3   ALLO  FC3   LHT3  LLIN  BOTH  NB        0.500000       0.0000       256.00000 
        (
            (
                b'\x00A\x04\x00MNEM    FC3 '
                    + b'EA\x04\x00OUTP    FC2 '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    LHT3'
                    + b'EA\x04\x00CODI    SFLN'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    NB  '
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGINCH' + RepCode.writeBytes(0.0, 68)
                    + b'ED\x04\x00REDGINCH' + RepCode.writeBytes(255.0, 68),
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'FC3 ', b'ServID', b'ServOrdN', b'    ',
                    45310011, 256, 4*16, 16, 68,
                ),
                LisGen.ChValsConst(mid=127.0, numSa=16, noise=128.0),
            ),
        ),
        #FC4   ALLO  FC4   RHT3  LLIN  BOTH  NB        0.500000       0.0000       256.00000 
        (
            (
                b'\x00A\x04\x00MNEM    FC4 '
                    + b'EA\x04\x00OUTP    FC4 '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    RHT3'
                    + b'EA\x04\x00CODI    SFLN'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    NB  '
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGINCH' + RepCode.writeBytes(0.0, 68)
                    + b'ED\x04\x00REDGINCH' + RepCode.writeBytes(255.0, 68),
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'FC4 ', b'ServID', b'ServOrdN', b'    ',
                    45310011, 256, 4*16, 16, 68,
                ),
                LisGen.ChValsConst(mid=127.0, numSa=16, noise=128.0),
            ),
        ),
    ]
    def retFilmBytes(self):
        return b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    2   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D200'

    def retPresBytes(self):
        """Returns the PRES logical record with curves from output TEST on various scales and tracks."""
        retVal = bytearray(b'"\x00' + b'IA\x04\x00TYPE    PRES')
        for pS, lgc in self.PRES_CHANNEL_DATA:
            for p in pS:
                retVal.extend(p)
        return retVal

    def retFileAndFileIndex(self):
        """Returns a File and a FileIndexer. Read the code!"""
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 73, 32))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'.1IN'))
        #print('myEbs.lisByteList()')
        #pprint.pprint(myEbs.lisByteList())
        # Create a direct X axis log with b'DEPT' and b'SP  '
        myLpGen = LisGen.LogPassGen(
            myEbs,
            # Output list
            [a[1] for a in self.PRES_CHANNEL_DATA],
            # 5000 feet in tenth inches
            xStart=5000.0*12*10,
            xRepCode=68,
            xNoise=None,
        )
        # File Header
        myData = LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileHead)
        # Create a File with the DFSR plus some frames
        myData.extend(self.retPrS(myLpGen.lrBytesDFSR()))
        framesPerLr = 8
        # 2000 feet at 3.2 inches per frame
        numFrames = int(1 + 2000 * 12 / 3.2)
        for fNum in range(0, numFrames, framesPerLr):
            myData.extend(self.retPrS(myLpGen.lrBytes(fNum, framesPerLr)))
#            print('Stuff')
#            print(myData)
#            print()
        myData.extend(LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileTail))
        myFile = self._retFileFromBytes(myData, theId='MyFile', flagKg=False)
        # Create a file index
        myFileIndex = FileIndexer.FileIndex(myFile)
        return myFile, myFileIndex


@pytest.mark.slow
class TestPlotReadLIS_HDT(TestPlotReadLIS_HDTBase):
    """Tests plotting HDT data."""
    TEST_SVG_FILE_MAP_ENTRY = 4

    def setUp(self):
        """Set up."""
        myByFilm = self.retFilmBytes()
        myByPres = self.retPresBytes()
        self._prl = Plot.PlotReadLIS(
            LogiRec.LrTableRead(self._retFileSinglePr(myByFilm)),
            LogiRec.LrTableRead(self._retFileSinglePr(myByPres)),
        )
        self._lisFile, self._lisFileIndex = self.retFileAndFileIndex()

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotReadLIS_SingleSquareCurveHighFreq.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """{:s}""".format(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description)
        for anIlp in self._lisFileIndex.genLogPasses():
            myXStart = EngVal.EngVal(5000.0, b'FEET')
            myXStop = EngVal.EngVal(4950.0, b'FEET')
            myTimerS = ExecTimer.TimerList()
            self._prl.plotLogPassLIS(
                self._lisFile,
                anIlp.logPass,
                myXStart,
                myXStop,
                Mnem.Mnem(b'1   '),
                TestPlotShared.outPath(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].fileName),
                frameStep=1,
                title=TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description,
                timerS=myTimerS)
            sys.stderr.write(str(myTimerS))
            sys.stderr.write('\n')
            sys.stderr.flush()


@pytest.mark.slow
class TestPlotReadLIS_HDT_20(TestPlotReadLIS_HDTBase):
    """Tests plotting HDT data on a 1:20 scale."""
    TEST_SVG_FILE_MAP_ENTRY = 4.1

    def retFilmBytes(self):
        return b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D20 ' \
                + b'\x00A\x04\x00MNEM    2   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D20 '

    def setUp(self):
        """Set up."""
        myByFilm = self.retFilmBytes()
        myByPres = self.retPresBytes()
        self._prl = Plot.PlotReadLIS(
            LogiRec.LrTableRead(self._retFileSinglePr(myByFilm)),
            LogiRec.LrTableRead(self._retFileSinglePr(myByPres)),
            theScale=20,
        )
        self._lisFile, self._lisFileIndex = self.retFileAndFileIndex()

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotReadLIS_SingleSquareCurveHighFreq.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """{:s}""".format(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description)
        for anIlp in self._lisFileIndex.genLogPasses():
            myXStart = EngVal.EngVal(5000.0, b'FEET')
            myXStop = EngVal.EngVal(4950.0, b'FEET')
            myTimerS = ExecTimer.TimerList()
            self._prl.plotLogPassLIS(
                self._lisFile,
                anIlp.logPass,
                myXStart,
                myXStop,
                Mnem.Mnem(b'1   '),
                TestPlotShared.outPath(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].fileName),
                frameStep=1,
                title=TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description,
                timerS=myTimerS)
            sys.stderr.write(str(myTimerS))
            sys.stderr.write('\n')
            sys.stderr.flush()


@pytest.mark.slow
class TestPlotReadLIS_HDT_40(TestPlotReadLIS_HDTBase):
    """Tests plotting HDT data on a 1:40 scale."""
    TEST_SVG_FILE_MAP_ENTRY = 4.2

    def retFilmBytes(self):
        return b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D40 ' \
                + b'\x00A\x04\x00MNEM    2   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D40 '

    def setUp(self):
        """Set up."""
        myByFilm = self.retFilmBytes()
        myByPres = self.retPresBytes()
        self._prl = Plot.PlotReadLIS(
            LogiRec.LrTableRead(self._retFileSinglePr(myByFilm)),
            LogiRec.LrTableRead(self._retFileSinglePr(myByPres)),
            theScale=40,
        )
        self._lisFile, self._lisFileIndex = self.retFileAndFileIndex()

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotReadLIS_SingleSquareCurveHighFreq.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """{:s}""".format(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description)
        for anIlp in self._lisFileIndex.genLogPasses():
            myXStart = EngVal.EngVal(5000.0, b'FEET')
            myXStop = EngVal.EngVal(4950.0, b'FEET')
            myTimerS = ExecTimer.TimerList()
            self._prl.plotLogPassLIS(
                self._lisFile,
                anIlp.logPass,
                myXStart,
                myXStop,
                Mnem.Mnem(b'1   '),
                TestPlotShared.outPath(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].fileName),
                frameStep=1,
                title=TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description,
                timerS=myTimerS)
            sys.stderr.write(str(myTimerS))
            sys.stderr.write('\n')
            sys.stderr.flush()


@pytest.mark.slow
class TestPlotReadLIS_SuperSampled(TestPlotBase_00):
    """Tests plotting a square wave with a low frequency (4 foot spacing) to illustrate super sampling."""
    TEST_SVG_FILE_MAP_ENTRY = 5
    # A list of ((PRES row bytes, ...), LisGenChannel)
    PRES_CHANNEL_DATA = [
        (
            (
                b'\x00A\x04\x00MNEM    1   '
                    + b'EA\x04\x00OUTP    1   '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T1  '
                    + b'EA\x04\x00CODI    LLIN'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    NB  '
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGINCH' + RepCode.writeBytes(-40.0, 68)
                    + b'ED\x04\x00REDGINCH' + RepCode.writeBytes(40.0, 68),
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'1   ', b'ServID', b'ServOrdN', b'INCH',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsSquare(fOffs=0, waveLen=8.0, mid=0.0, amp=30.0, numSa=1, noise=4.0),
            ),
        ),
        (
            (
                b'\x00A\x04\x00MNEM    8   '
                    + b'EA\x04\x00OUTP    8   '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T2  '
                    + b'EA\x04\x00CODI    LLIN'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    WRAP'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGINCH' + RepCode.writeBytes(-40.0, 68)
                    + b'ED\x04\x00REDGINCH' + RepCode.writeBytes(40.0, 68),
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'8   ', b'ServID', b'ServOrdN', b'INCH',
                    45310011, 256, 4*8, 8, 68
                ),
                LisGen.ChValsSquare(fOffs=0, waveLen=8.0, mid=0.0, amp=30.0, numSa=8, noise=4.0),
            ),
        ),
        (
            (
                b'\x00A\x04\x00MNEM    32  '
                    + b'EA\x04\x00OUTP    32  '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T3  '
                    + b'EA\x04\x00CODI    LLIN'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    WRAP'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGINCH' + RepCode.writeBytes(-40.0, 68)
                    + b'ED\x04\x00REDGINCH' + RepCode.writeBytes(40.0, 68),
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'32  ', b'ServID', b'ServOrdN', b'INCH',
                    45310011, 256, 4*32, 32, 68
                ),
                LisGen.ChValsSquare(fOffs=0, waveLen=8.0, mid=0.0, amp=30.0, numSa=32, noise=4.0),
            ),
        ),
    ]

    def retFilmBytes(self):
        return b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    2   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D200'

    def retPresBytes(self):
        """Returns the PRES logical record with curves from output TEST on various scales and tracks."""
        retVal = bytearray(b'"\x00' + b'IA\x04\x00TYPE    PRES')
        for pS, lgc in self.PRES_CHANNEL_DATA:
            for p in pS:
                retVal.extend(p)
        return retVal

    def retFileAndFileIndex(self):
        """Returns a File and a FileIndexer. Read the code!"""
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 68, 4.0))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'FEET'))
        #print('myEbs.lisByteList()')
        #pprint.pprint(myEbs.lisByteList())
        # Create a direct X axis log with b'DEPT' and b'SP  '
        myLpGen = LisGen.LogPassGen(
            myEbs,
            # Output list
            [a[1] for a in self.PRES_CHANNEL_DATA],
            # 5000 feet in tenth inches
            xStart=1000.0,
            xRepCode=68,
            xNoise=None,
        )
        # File Header
        myData = LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileHead)
        # Create a File with the DFSR plus some frames
        myData.extend(self.retPrS(myLpGen.lrBytesDFSR()))
        framesPerLr = 8
        numFrames = 26
        for fNum in range(0, numFrames, framesPerLr):
            myData.extend(self.retPrS(myLpGen.lrBytes(fNum, framesPerLr)))
        myData.extend(LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileTail))
        myFile = self._retFileFromBytes(myData, theId='MyFile', flagKg=False)
        # Create a file index
        myFileIndex = FileIndexer.FileIndex(myFile)
        return myFile, myFileIndex
        
    def setUp(self):
        """Set up."""
        myByFilm = self.retFilmBytes()
        myByPres = self.retPresBytes()
        self._prl = Plot.PlotReadLIS(
            LogiRec.LrTableRead(self._retFileSinglePr(myByFilm)),
            LogiRec.LrTableRead(self._retFileSinglePr(myByPres)),
        )
        self._lisFile, self._lisFileIndex = self.retFileAndFileIndex()

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotReadLIS_SuperSampled.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """{:s}""".format(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description)
        for anIlp in self._lisFileIndex.genLogPasses():
            myXStart = EngVal.EngVal(1000.0, b'FEET')
            myXStop = EngVal.EngVal(900.0, b'FEET')
            myTimerS = ExecTimer.TimerList()
            self._prl.plotLogPassLIS(
                self._lisFile,
                anIlp.logPass,
                myXStart,
                myXStop,
                Mnem.Mnem(b'1   '),
                TestPlotShared.outPath(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].fileName),
                frameStep=1,
                title=TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description,
                timerS=myTimerS)
            sys.stderr.write(str(myTimerS))
            sys.stderr.write('\n')
            sys.stderr.flush()


@pytest.mark.slow
class TestPlotReadLIS_COLO_Named(TestPlotBase_00):
    """Tests plotting a LIS file with colours."""
    TEST_SVG_FILE_MAP_ENTRY = 6
    def retPresBytes_TEST(self):
        """Returns the PRES logical record with curves from output TEST on various scales and tracks."""
        return bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            + b'\x00A\x04\x00MNEM    BLAC'
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-40.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(40.0, 68)#B\xd0\x00\x00'
                + b'EA\x04\x00COLO    BLAC'
            + b'\x00A\x04\x00MNEM    BLUE'
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HDAS'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-20.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
                + b'EA\x04\x00COLO    BLUE'
            + b'\x00A\x04\x00MNEM    AQUA'
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T3  '
                + b'EA\x04\x00CODI    LGAP'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-10.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(10.0, 68)#B\xd0\x00\x00'
                + b'EA\x04\x00COLO    AQUA'
            + b'\x00A\x04\x00MNEM    GREE'
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HSPO'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-5.0, 68)
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(5.0, 68)
                + b'EA\x04\x00COLO    GREE'
            + b'\x00A\x04\x00MNEM    RED '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T3  '
                + b'EA\x04\x00CODI    LSPO'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-2.5, 68)
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(2.5, 68)
                + b'EA\x04\x00COLO    RED '
            )

    def retFileAndFileIndex_ShortTEST(self):
        """Returns a File and a FileIndexer.FileIndex of DEPt plus a single curve.
        Log is 100 ft, 0.5 ft spacing. SP is a sine curve -80 to 20 mV with a
        wavelength of 20 feet. i.e. 5 waves."""
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST():')
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 68, 0.5))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'FEET'))
        #print('myEbs.lisByteList()')
        #pprint.pprint(myEbs.lisByteList())
        # Create a direct X axis log with b'DEPT' and b'SP  '
        myLpGen = LisGen.LogPassGen(
            myEbs,
            # Output list
            [
                LisGen.Channel(
                    LisGen.ChannelSpec(
                        b'TEST', b'ServID', b'ServOrdN', b'MV  ',
                        45310011, 256, 4, 1, 68
                    ),
                    LisGen.ChValsSin(fOffs=0, waveLen=160.0, mid=0.0, amp=40.0, numSa=1, noise=None),
#                    LisGen.ChValsSpecialSeqSqRoot(fOffs=0, waveLen=20.0, mid=-80.0, amp=100.0, numSa=1, noise=None),
                ),
            ],
            xStart=1000.0,
            xRepCode=68,
            xNoise=None,
        )
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): creating DFSR...')
        # File Header
        myData = LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileHead)
        # Create a File with the DFSR plus some frames
        myData.extend(self.retPrS(myLpGen.lrBytesDFSR()))
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): creating frames...')
        framesPerLr = 8
        numFrames = 201
        for fNum in range(0, numFrames, framesPerLr):
            myData.extend(self.retPrS(myLpGen.lrBytes(fNum, framesPerLr)))
        myData.extend(LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileTail))
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): creating File length={:d} ...'.format(len(myData)))
        myFile = self._retFileFromBytes(myData, theId='MyFile', flagKg=False)
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): creating FileIndex...')
        # Create a file index
        myFileIndex = FileIndexer.FileIndex(myFile)
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): returning File and FileIndex.')
        return myFile, myFileIndex
        
    def setUp(self):
        """Set up."""
        myByFilm = self.retFilmBytes()
        myByPres = self.retPresBytes_TEST()
        self._prl = Plot.PlotReadLIS(
            LogiRec.LrTableRead(self._retFileSinglePr(myByFilm)),
            LogiRec.LrTableRead(self._retFileSinglePr(myByPres)),
        )
        self._lisFile, self._lisFileIndex = self.retFileAndFileIndex_ShortTEST()

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotReadLIS_COLOCurve_Name.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """{:s}""".format(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description)
        for anIlp in self._lisFileIndex.genLogPasses():
#            myXStart = EngVal.EngVal(9900.0, b'FEET')
#            myXStop = EngVal.EngVal(9600.0, b'FEET')
            myXStart = EngVal.EngVal(1000.0, b'FEET')
            myXStop = EngVal.EngVal(900.0, b'FEET')
            myTimerS = ExecTimer.TimerList()
            self._prl.plotLogPassLIS(
                self._lisFile,
                anIlp.logPass,
                myXStart,
                myXStop,
                Mnem.Mnem(b'2   '),
                TestPlotShared.outPath(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].fileName),
                frameStep=1,
                title=TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description,
                timerS=myTimerS)
            sys.stderr.write(str(myTimerS))
            sys.stderr.write('\n')
            sys.stderr.flush()


@pytest.mark.slow
class TestPlotReadLIS_COLO_Numbered(TestPlotBase_00):
    """Tests plotting a LIS file with numbered colours."""
    TEST_SVG_FILE_MAP_ENTRY = 7
    def retPresBytes_TEST(self):
        """Returns the PRES logical record with curves from output TEST on various scales and tracks."""
        return bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            + b'\x00A\x04\x00MNEM    000 '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-40.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(40.0, 68)#B\xd0\x00\x00'
                + b'EA\x04\x00COLO    000 '
            + b'\x00A\x04\x00MNEM    333 '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HDAS'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-20.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
                + b'EA\x04\x00COLO    333 '
            + b'\x00A\x04\x00MNEM    400 '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T3  '
                + b'EA\x04\x00CODI    LGAP'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-10.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(10.0, 68)#B\xd0\x00\x00'
                + b'EA\x04\x00COLO    400 '
            + b'\x00A\x04\x00MNEM    040 '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HSPO'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-5.0, 68)
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(5.0, 68)
                + b'EA\x04\x00COLO    040 '
            + b'\x00A\x04\x00MNEM    004 '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T3  '
                + b'EA\x04\x00CODI    LSPO'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-2.5, 68)
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(2.5, 68)
                + b'EA\x04\x00COLO    004 '
            )

    def retFileAndFileIndex_ShortTEST(self):
        """Returns a File and a FileIndexer.FileIndex of DEPt plus a single curve.
        Log is 100 ft, 0.5 ft spacing. SP is a sine curve -80 to 20 mV with a
        wavelength of 20 feet. i.e. 5 waves."""
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST():')
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 68, 0.5))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'FEET'))
        #print('myEbs.lisByteList()')
        #pprint.pprint(myEbs.lisByteList())
        # Create a direct X axis log with b'DEPT' and b'SP  '
        myLpGen = LisGen.LogPassGen(
            myEbs,
            # Output list
            [
                LisGen.Channel(
                    LisGen.ChannelSpec(
                        b'TEST', b'ServID', b'ServOrdN', b'MV  ',
                        45310011, 256, 4, 1, 68
                    ),
                    LisGen.ChValsSin(fOffs=0, waveLen=160.0, mid=0.0, amp=40.0, numSa=1, noise=None),
#                    LisGen.ChValsSpecialSeqSqRoot(fOffs=0, waveLen=20.0, mid=-80.0, amp=100.0, numSa=1, noise=None),
                ),
            ],
            xStart=1000.0,
            xRepCode=68,
            xNoise=None,
        )
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): creating DFSR...')
        # File Header
        myData = LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileHead)
        # Create a File with the DFSR plus some frames
        myData.extend(self.retPrS(myLpGen.lrBytesDFSR()))
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): creating frames...')
        framesPerLr = 8
        numFrames = 201
        for fNum in range(0, numFrames, framesPerLr):
            myData.extend(self.retPrS(myLpGen.lrBytes(fNum, framesPerLr)))
        myData.extend(LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileTail))
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): creating File length={:d} ...'.format(len(myData)))
        myFile = self._retFileFromBytes(myData, theId='MyFile', flagKg=False)
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): creating FileIndex...')
        # Create a file index
        myFileIndex = FileIndexer.FileIndex(myFile)
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): returning File and FileIndex.')
        return myFile, myFileIndex
        
    def setUp(self):
        """Set up."""
        myByFilm = self.retFilmBytes()
        myByPres = self.retPresBytes_TEST()
        self._prl = Plot.PlotReadLIS(
            LogiRec.LrTableRead(self._retFileSinglePr(myByFilm)),
            LogiRec.LrTableRead(self._retFileSinglePr(myByPres)),
        )
        self._lisFile, self._lisFileIndex = self.retFileAndFileIndex_ShortTEST()

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotReadLIS_COLOCurve_Numbered.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """{:s}""".format(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description)
        for anIlp in self._lisFileIndex.genLogPasses():
#            myXStart = EngVal.EngVal(9900.0, b'FEET')
#            myXStop = EngVal.EngVal(9600.0, b'FEET')
            myXStart = EngVal.EngVal(1000.0, b'FEET')
            myXStop = EngVal.EngVal(900.0, b'FEET')
            myTimerS = ExecTimer.TimerList()
            self._prl.plotLogPassLIS(
                self._lisFile,
                anIlp.logPass,
                myXStart,
                myXStop,
                Mnem.Mnem(b'2   '),
                TestPlotShared.outPath(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].fileName),
                frameStep=1,
                title=TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description,
                timerS=myTimerS)
            sys.stderr.write(str(myTimerS))
            sys.stderr.write('\n')
            sys.stderr.flush()


@pytest.mark.slow
class TestPlotReadLIS_COLO_Numbered_Comp(TestPlotBase_00):
    """Tests plotting a LIS file with numbered complimentary colours."""
    TEST_SVG_FILE_MAP_ENTRY = 8
    def retPresBytes_TEST(self):
        """Returns the PRES logical record with curves from output TEST on various scales and tracks."""
        return bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            + b'\x00A\x04\x00MNEM    000 '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-40.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(40.0, 68)#B\xd0\x00\x00'
                + b'EA\x04\x00COLO    000 '
            + b'\x00A\x04\x00MNEM    333 '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HDAS'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-20.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
                + b'EA\x04\x00COLO    333 '
            + b'\x00A\x04\x00MNEM    044 '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T3  '
                + b'EA\x04\x00CODI    LGAP'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-10.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(10.0, 68)#B\xd0\x00\x00'
                + b'EA\x04\x00COLO    044 '
            + b'\x00A\x04\x00MNEM    440 '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HSPO'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-5.0, 68)
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(5.0, 68)
                + b'EA\x04\x00COLO    440 '
            + b'\x00A\x04\x00MNEM    404 '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T3  '
                + b'EA\x04\x00CODI    LSPO'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-2.5, 68)
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(2.5, 68)
                + b'EA\x04\x00COLO    404 '
            )

    def retFileAndFileIndex_ShortTEST(self):
        """Returns a File and a FileIndexer.FileIndex of DEPt plus a single curve.
        Log is 100 ft, 0.5 ft spacing. SP is a sine curve -80 to 20 mV with a
        wavelength of 20 feet. i.e. 5 waves."""
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST():')
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 68, 0.5))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'FEET'))
        #print('myEbs.lisByteList()')
        #pprint.pprint(myEbs.lisByteList())
        # Create a direct X axis log with b'DEPT' and b'SP  '
        myLpGen = LisGen.LogPassGen(
            myEbs,
            # Output list
            [
                LisGen.Channel(
                    LisGen.ChannelSpec(
                        b'TEST', b'ServID', b'ServOrdN', b'MV  ',
                        45310011, 256, 4, 1, 68
                    ),
                    LisGen.ChValsSin(fOffs=0, waveLen=160.0, mid=0.0, amp=40.0, numSa=1, noise=None),
#                    LisGen.ChValsSpecialSeqSqRoot(fOffs=0, waveLen=20.0, mid=-80.0, amp=100.0, numSa=1, noise=None),
                ),
            ],
            xStart=1000.0,
            xRepCode=68,
            xNoise=None,
        )
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): creating DFSR...')
        # File Header
        myData = LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileHead)
        # Create a File with the DFSR plus some frames
        myData.extend(self.retPrS(myLpGen.lrBytesDFSR()))
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): creating frames...')
        framesPerLr = 8
        numFrames = 201
        for fNum in range(0, numFrames, framesPerLr):
            myData.extend(self.retPrS(myLpGen.lrBytes(fNum, framesPerLr)))
        myData.extend(LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileTail))
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): creating File length={:d} ...'.format(len(myData)))
        myFile = self._retFileFromBytes(myData, theId='MyFile', flagKg=False)
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): creating FileIndex...')
        # Create a file index
        myFileIndex = FileIndexer.FileIndex(myFile)
        logging.info('TestPlotBase_00.retFileAndFileIndex_ShortTEST(): returning File and FileIndex.')
        return myFile, myFileIndex
        
    def setUp(self):
        """Set up."""
        myByFilm = self.retFilmBytes()
        myByPres = self.retPresBytes_TEST()
        self._prl = Plot.PlotReadLIS(
            LogiRec.LrTableRead(self._retFileSinglePr(myByFilm)),
            LogiRec.LrTableRead(self._retFileSinglePr(myByPres)),
        )
        self._lisFile, self._lisFileIndex = self.retFileAndFileIndex_ShortTEST()

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotReadLIS_COLOCurve_Numbered.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """{:s}""".format(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description)
        for anIlp in self._lisFileIndex.genLogPasses():
#            myXStart = EngVal.EngVal(9900.0, b'FEET')
#            myXStop = EngVal.EngVal(9600.0, b'FEET')
            myXStart = EngVal.EngVal(1000.0, b'FEET')
            myXStop = EngVal.EngVal(900.0, b'FEET')
            myTimerS = ExecTimer.TimerList()
            self._prl.plotLogPassLIS(
                self._lisFile,
                anIlp.logPass,
                myXStart,
                myXStop,
                Mnem.Mnem(b'2   '),
                TestPlotShared.outPath(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].fileName),
                frameStep=1,
                title=TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY].description,
                timerS=myTimerS)
            sys.stderr.write(str(myTimerS))
            sys.stderr.write('\n')
            sys.stderr.flush()


@pytest.mark.slow
class TestPlotReadLIS_Perf_00(TestPlotBase_00):
    """Tests plotting performance, 2000' of 10 curves."""
    TEST_SVG_FILE_MAP_ENTRY_MAP = {
                b'1   ' : 9,
                b'2   ' : 10,
    }
    # A list of ((PRES row bytes, ...), LisGenChannel) for ten channels
    # We have four OUTP/ five curves in T1, one in TD, these go to both films
    # In film 1 we have 2 in T2 and 2 in T3
    # In film 2 we have 4 in T23
    PRES_CHANNEL_DATA = [
        # Four OUTP/5 curves in T1 that go to both films
        (
            (
                b'\x00A\x04\x00MNEM    ONE '
                    + b'EA\x04\x00OUTP    ONE '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T1  '
                    + b'EA\x04\x00CODI    LLIN'
                    + b'EA\x04\x00DEST    BOTH'
                    + b'EA\x04\x00MODE    NB  '
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGINCH' + RepCode.writeBytes(-5.0, 68)
                    + b'ED\x04\x00REDGINCH' + RepCode.writeBytes(5.0, 68)
                    + b'EA\x04\x00COLO    RED ',
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'ONE ', b'ServID', b'ServOrdN', b'INCH',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsSin(fOffs=0, waveLen=80, mid=0, amp=4, numSa=1, noise=None),
            ),
        ),
        (
            (
                b'\x00A\x04\x00MNEM    TWO '
                    + b'EA\x04\x00OUTP    TWO '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T1  '
                    + b'EA\x04\x00CODI    LLIN'
                    + b'EA\x04\x00DEST    BOTH'
                    + b'EA\x04\x00MODE    WRAP'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGMM  ' + RepCode.writeBytes(-5.0, 68)
                    + b'ED\x04\x00REDGMM  ' + RepCode.writeBytes(5.0, 68)
                    + b'EA\x04\x00COLO    GREE',
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'TWO ', b'ServID', b'ServOrdN', b'MM  ',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsCos(fOffs=0, waveLen=80, mid=0, amp=4, numSa=1, noise=None),
            ),
        ),
        (
            (
                b'\x00A\x04\x00MNEM    THRE'
                    + b'EA\x04\x00OUTP    THRE'
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T1  '
                    + b'EA\x04\x00CODI    LDAS'
                    + b'EA\x04\x00DEST    BOTH'
                    + b'EA\x04\x00MODE    WRAP'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGINCH' + RepCode.writeBytes(-10.0, 68)
                    + b'ED\x04\x00REDGINCH' + RepCode.writeBytes(10.0, 68)
                    + b'EA\x04\x00COLO    BLAC',
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'THRE', b'ServID', b'ServOrdN', b'INCH',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsSin(fOffs=10, waveLen=80, mid=0, amp=8, numSa=1, noise=None),
            ),
        ),
        (
            (
                b'\x00A\x04\x00MNEM    thre'
                    + b'EA\x04\x00OUTP    THRE'
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T1  '
                    + b'EA\x04\x00CODI    LDAS'
                    + b'EA\x04\x00DEST    BOTH'
                    + b'EA\x04\x00MODE    WRAP'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGINCH' + RepCode.writeBytes(-5.0, 68)
                    + b'ED\x04\x00REDGINCH' + RepCode.writeBytes(5.0, 68)
                    + b'EA\x04\x00COLO    BLUE',
            ),
            None,
        ),
        (
            (
                b'\x00A\x04\x00MNEM    FOUR'
                    + b'EA\x04\x00OUTP    FOUR'
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T1  '
                    + b'EA\x04\x00CODI    LGAP'
                    + b'EA\x04\x00DEST    BOTH'
                    + b'EA\x04\x00MODE    WRAP'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGDEG ' + RepCode.writeBytes(-5.0, 68)
                    + b'ED\x04\x00REDGDEG ' + RepCode.writeBytes(45.0, 68)
                    + b'EA\x04\x00COLO    BLAC',
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'FOUR', b'ServID', b'ServOrdN', b'DEG ',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsTriangular(fOffs=10, waveLen=80, mid=0, amp=40, numSa=1, noise=None),
            ),
        ),
        (
            (
                b'\x00A\x04\x00MNEM    TENS'
                    + b'EA\x04\x00OUTP    TENS'
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    TD  '
                    + b'EA\x04\x00CODI    LDAS'
                    + b'EA\x04\x00DEST    BOTH'
                    + b'EA\x04\x00MODE    WRAP'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGLBF ' + RepCode.writeBytes(0.0, 68)
                    + b'ED\x04\x00REDGLBF ' + RepCode.writeBytes(5000.0, 68)
                    + b'EA\x04\x00COLO    BLAC',
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'TENS', b'ServID', b'ServOrdN', b'LBF ',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsConst(fOffs=0, waveLen=0, mid=4000, amp=0, numSa=1, noise=500),
            ),
        ),
        (
            (
                b'\x00A\x04\x00MNEM    CORS'
                    + b'EA\x04\x00OUTP    T2  '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T2  '
                    + b'EA\x04\x00CODI    LLIN'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    WRAP'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGMMHO' + RepCode.writeBytes(-50.0, 68)
                    + b'ED\x04\x00REDGMMHO' + RepCode.writeBytes(50.0, 68)
                    + b'EA\x04\x00COLO    BLUE',
            ),
            None,
        ),
        (
            (
                b'\x00A\x04\x00MNEM    FINE'
                    + b'EA\x04\x00OUTP    T2  '
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T2  '
                    + b'EA\x04\x00CODI    LLIN'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    WRAP'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGMMHO' + RepCode.writeBytes(10.0, 68)
                    + b'ED\x04\x00REDGMMHO' + RepCode.writeBytes(-10.0, 68)
                    + b'EA\x04\x00COLO    BLAC',
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'T2  ', b'ServID', b'ServOrdN', b'MMHO',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsSin(fOffs=10, waveLen=80, mid=0, amp=25, numSa=1, noise=None),
            ),
        ),
        (
            (
                b'\x00A\x04\x00MNEM    T3C1'
                    + b'EA\x04\x00OUTP    T3F1'
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T3  '
                    + b'EA\x04\x00CODI    HLIN'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    WRAP'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGDEGC' + RepCode.writeBytes(0.0, 68)
                    + b'ED\x04\x00REDGDEGC' + RepCode.writeBytes(100.0, 68)
                    + b'EA\x04\x00COLO    CYAN',
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'T3F1', b'ServID', b'ServOrdN', b'DEGC',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsRandNormal(fOffs=0, waveLen=0, mid=50, amp=5, numSa=1, noise=None),
            ),
        ),
        (
            (
                b'\x00A\x04\x00MNEM    T3C2'
                    + b'EA\x04\x00OUTP    T3F1'
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T3  '
                    + b'EA\x04\x00CODI    LLIN'
                    + b'EA\x04\x00DEST    1   '
                    + b'EA\x04\x00MODE    WRAP'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGDEGC' + RepCode.writeBytes(40.0, 68)
                    + b'ED\x04\x00REDGDEGC' + RepCode.writeBytes(60.0, 68)
                    + b'EA\x04\x00COLO    MAGE',
            ),
            None,
        ),
        # Now four curves (T23A, T23B, T23C, T23D) that appear on FILM 2 in T23
        (
            (
                b'\x00A\x04\x00MNEM    T23A'
                    + b'EA\x04\x00OUTP    T23A'
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T23 '
                    + b'EA\x04\x00CODI    LLIN'
                    + b'EA\x04\x00DEST    2   '
                    + b'EA\x04\x00MODE    GRAD'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGOHMM' + RepCode.writeBytes(0.2, 68)
                    + b'ED\x04\x00REDGOHMM' + RepCode.writeBytes(2000.0, 68)
                    + b'EA\x04\x00COLO    BLAC',
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'T23A', b'ServID', b'ServOrdN', b'OHMM',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsSin(fOffs=0, waveLen=100, mid=1000, amp=999, numSa=1, noise=0),
            ),
        ),
        (
            (
                b'\x00A\x04\x00MNEM    T23B'
                    + b'EA\x04\x00OUTP    T23B'
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T23 '
                    + b'EA\x04\x00CODI    LSPO'
                    + b'EA\x04\x00DEST    2   '
                    + b'EA\x04\x00MODE    GRAD'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGOHMM' + RepCode.writeBytes(0.2, 68)
                    + b'ED\x04\x00REDGOHMM' + RepCode.writeBytes(2000.0, 68)
                    + b'EA\x04\x00COLO    RED ',
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'T23B', b'ServID', b'ServOrdN', b'OHMM',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsSin(fOffs=5, waveLen=100, mid=1000, amp=899, numSa=1, noise=100),
            ),
        ),
        (
            (
                b'\x00A\x04\x00MNEM    T23C'
                    + b'EA\x04\x00OUTP    T23C'
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T23 '
                    + b'EA\x04\x00CODI    LDAS'
                    + b'EA\x04\x00DEST    2   '
                    + b'EA\x04\x00MODE    GRAD'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGOHMM' + RepCode.writeBytes(0.2, 68)
                    + b'ED\x04\x00REDGOHMM' + RepCode.writeBytes(2000.0, 68)
                    + b'EA\x04\x00COLO    BLUE',
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'T23C', b'ServID', b'ServOrdN', b'OHMM',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsSin(fOffs=-5, waveLen=100, mid=1000, amp=799, numSa=1, noise=200),
            ),
        ),
        (
            (
                b'\x00A\x04\x00MNEM    T23D'
                    + b'EA\x04\x00OUTP    T23D'
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T23 '
                    + b'EA\x04\x00CODI    LLIN'
                    + b'EA\x04\x00DEST    2   '
                    + b'EA\x04\x00MODE    GRAD'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGOHMM' + RepCode.writeBytes(0.2, 68)
                    + b'ED\x04\x00REDGOHMM' + RepCode.writeBytes(2000.0, 68)
                    + b'EA\x04\x00COLO    GREE',
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'T23D', b'ServID', b'ServOrdN', b'OHMM',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsSin(fOffs=0, waveLen=100, mid=1000, amp=700, numSa=1, noise=0),
            ),
        ),
        (
            (
                b'\x00A\x04\x00MNEM    T23E'
                    + b'EA\x04\x00OUTP    T23E'
                    + b'EA\x04\x00STAT    ALLO'
                    + b'EA\x04\x00TRAC    T23 '
                    + b'EA\x04\x00CODI    LGAP'
                    + b'EA\x04\x00DEST    2   '
                    + b'EA\x04\x00MODE    GRAD'
                    + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                    + b'ED\x04\x00LEDGOHMM' + RepCode.writeBytes(0.2, 68)
                    + b'ED\x04\x00REDGOHMM' + RepCode.writeBytes(2000.0, 68)
                    + b'EA\x04\x00COLO    GREE',
            ),
            LisGen.Channel(
                LisGen.ChannelSpec(
                    b'T23E', b'ServID', b'ServOrdN', b'OHMM',
                    45310011, 256, 4, 1, 68
                ),
                LisGen.ChValsSin(fOffs=0, waveLen=100, mid=1000, amp=700, numSa=1, noise=299),
            ),
        ),
    ]
    def retFilmBytes(self):
        return b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    2   ' \
                    + b'EA\x04\x00GCOD    E20 ' \
                    + b'EA\x04\x00GDEC    -4--' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D200'

    def retPresBytes(self):
        """Returns the PRES logical record with curves from output TEST on various scales and tracks."""
        retVal = bytearray(b'"\x00' + b'IA\x04\x00TYPE    PRES')
        for pS, lgc in self.PRES_CHANNEL_DATA:
            for p in pS:
                retVal.extend(p)
        return retVal

    def retFileAndFileIndex(self):
        """Returns a File and a FileIndexer. Read the code!"""
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 73, 60))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'.1IN'))
        #print('myEbs.lisByteList()')
        #pprint.pprint(myEbs.lisByteList())
        # Create a direct X axis log with b'DEPT'
        myLpGen = LisGen.LogPassGen(
            myEbs,
            # Output list
            [a[1] for a in self.PRES_CHANNEL_DATA if a[1] is not None],
            # 5000 feet in tenth inches
            xStart=5000.0*12*10,
            xRepCode=68,
            xNoise=None,
        )
        # File Header
        myData = LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileHead)
        # Create a File with the DFSR plus some frames
        myData.extend(self.retPrS(myLpGen.lrBytesDFSR()))
        framesPerLr = 8
        # 2000 feet at 6 inches per frame
        numFrames = int(1 + 2000 * 12 / 6)
        for fNum in range(0, numFrames, framesPerLr):
            myData.extend(self.retPrS(myLpGen.lrBytes(fNum, framesPerLr)))
#            print('Stuff')
#            print(myData)
#            print()
        myData.extend(LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileTail))
        myFile = self._retFileFromBytes(myData, theId='MyFile', flagKg=False)
        # Create a file index
        myFileIndex = FileIndexer.FileIndex(myFile)
        return myFile, myFileIndex
        
    def setUp(self):
        """Set up."""
        myByFilm = self.retFilmBytes()
        myByPres = self.retPresBytes()
        self._prl = Plot.PlotReadLIS(
            LogiRec.LrTableRead(self._retFileSinglePr(myByFilm)),
            LogiRec.LrTableRead(self._retFileSinglePr(myByPres)),
        )
        self._lisFile, self._lisFileIndex = self.retFileAndFileIndex()

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotReadLIS_SingleSquareCurveHighFreq.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """{:s} FILM 1""".format(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY_MAP[b'1   ']].description)
        for anIlp in self._lisFileIndex.genLogPasses():
            myXStart = EngVal.EngVal(5000.0, b'FEET')
            myXStop = EngVal.EngVal(4000.0, b'FEET')
            myTimerS = ExecTimer.TimerList()
            self._prl.plotLogPassLIS(
                self._lisFile,
                anIlp.logPass,
                myXStart,
                myXStop,
                Mnem.Mnem(b'1   '),
                TestPlotShared.outPath(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY_MAP[b'1   ']].fileName),
                frameStep=1,
                title=TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY_MAP[b'1   ']].description,
                timerS=myTimerS)
            sys.stderr.write(str(myTimerS))
            sys.stderr.write('\n')
            sys.stderr.flush()

    def test_02(self):
        """{:s} FILM 2""".format(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY_MAP[b'2   ']].description)
        for anIlp in self._lisFileIndex.genLogPasses():
            myXStart = EngVal.EngVal(5000.0, b'FEET')
            myXStop = EngVal.EngVal(4000.0, b'FEET')
            myTimerS = ExecTimer.TimerList()
            self._prl.plotLogPassLIS(
                self._lisFile,
                anIlp.logPass,
                myXStart,
                myXStop,
                Mnem.Mnem(b'2   '),
                TestPlotShared.outPath(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY_MAP[b'2   ']].fileName),
                frameStep=1,
                title=TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY_MAP[b'2   ']].description,
                timerS=myTimerS)
            sys.stderr.write(str(myTimerS))
            sys.stderr.write('\n')
            sys.stderr.flush()


@pytest.mark.slow
class TestPlotReadLIS_XML_LgFormat(TestPlotBase_00):
    """Tests plotting of 1000' of curves from "Triple_Combo" LgFormat XML file."""
    PLOT_START_IN_FEET = 5000.0
    PLOT_LENGTH_IN_FEET = 200.0
    TEST_SVG_FILE_MAP_ENTRY_MAP = {
                'Triple_Combo'                      : 20,
                'Resistivity_3Track_Logrithmic.xml' : 21,
    }
    # Tuple of LisGen.Channel() objects
    CHANNEL_DATA = (
        LisGen.Channel(
            LisGen.ChannelSpec(
                b'BS  ', b'ServID', b'ServOrdN', b'INCH',
                45310011, 256, 4, 1, 68
            ),
            LisGen.ChValsConst(fOffs=0, waveLen=0, mid=7.5, amp=0, numSa=1, noise=None),
        ),
        LisGen.Channel(
            LisGen.ChannelSpec(
                b'CALI', b'ServID', b'ServOrdN', b'INCH',
                45310011, 256, 4, 1, 68
            ),
            LisGen.ChValsConst(fOffs=0, waveLen=0, mid=7.1, amp=0, numSa=1, noise=1.0),
        ),
        LisGen.Channel(
            LisGen.ChannelSpec(
                b'SP  ', b'ServID', b'ServOrdN', b'MV  ',
                45310011, 256, 4, 1, 68
            ),
            LisGen.ChValsSin(fOffs=0, waveLen=80, mid=-60, amp=100, numSa=1, noise=None),
        ),
        LisGen.Channel(
            LisGen.ChannelSpec(
                b'GR  ', b'ServID', b'ServOrdN', b'GAPI',
                45310011, 256, 4, 1, 68
            ),
            LisGen.ChValsCos(fOffs=10, waveLen=80, mid=80, amp=40, numSa=1, noise=None),
        ),
        LisGen.Channel(
            LisGen.ChannelSpec(
                b'ILD ', b'ServID', b'ServOrdN', b'MMHO',
                45310011, 256, 4, 1, 68
            ),
            LisGen.ChValsSin(fOffs=0, waveLen=80, mid=1000, amp=800, numSa=1, noise=None),
        ),
        LisGen.Channel(
            LisGen.ChannelSpec(
                b'ILM ', b'ServID', b'ServOrdN', b'MMHO',
                45310011, 256, 4, 1, 68
            ),
            LisGen.ChValsSin(fOffs=0, waveLen=80, mid=1000, amp=700, numSa=1, noise=None),
        ),
        LisGen.Channel(
            LisGen.ChannelSpec(
                b'LLD ', b'ServID', b'ServOrdN', b'MMHO',
                45310011, 256, 4, 1, 68
            ),
            LisGen.ChValsSin(fOffs=20, waveLen=80, mid=1000, amp=500, numSa=1, noise=None),
        ),
        LisGen.Channel(
            LisGen.ChannelSpec(
                b'LLM ', b'ServID', b'ServOrdN', b'MMHO',
                45310011, 256, 4, 1, 68
            ),
            LisGen.ChValsSin(fOffs=20, waveLen=80, mid=1000, amp=600, numSa=1, noise=None),
        ),
        # Porosity
        LisGen.Channel(
            LisGen.ChannelSpec(
                b'TNPH', b'ServID', b'ServOrdN', b'V/V ',
                45310011, 256, 4, 1, 68
            ),
            LisGen.ChValsTriangular(fOffs=0, waveLen=80, mid=.25, amp=.15, numSa=1, noise=0),
        ),
        LisGen.Channel(
            LisGen.ChannelSpec(
                b'DPHI', b'ServID', b'ServOrdN', b'V/V ',
                45310011, 256, 4, 1, 68
            ),
            LisGen.ChValsTriangular(fOffs=0, waveLen=80, mid=.2, amp=.15, numSa=1, noise=0),
        ),
    )
    
    def retFileAndFileIndex(self):
        """Returns a File and a FileIndexer. Read the code!"""
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 73, 60))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'.1IN'))
        #print('myEbs.lisByteList()')
        #pprint.pprint(myEbs.lisByteList())
        # Create a direct X axis log with b'DEPT'
        myLpGen = LisGen.LogPassGen(
            myEbs,
            # Output list
            self.CHANNEL_DATA,
            # Plot start in tenth inches
            xStart=self.PLOT_START_IN_FEET * 12 * 10,
            xRepCode=68,
            xNoise=None,
        )
        # File Header
        myData = LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileHead)
        # Create a File with the DFSR plus some frames
        myData.extend(self.retPrS(myLpGen.lrBytesDFSR()))
        framesPerLr = 8
        # 2000 feet at 6 inches per frame
        numFrames = int(1 + self.PLOT_LENGTH_IN_FEET * 12 / 6)
        for fNum in range(0, numFrames, framesPerLr):
            myData.extend(self.retPrS(myLpGen.lrBytes(fNum, framesPerLr)))
#            print('Stuff')
#            print(myData)
#            print()
        myData.extend(LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileTail))
        myFile = self._retFileFromBytes(myData, theId='MyFile', flagKg=False)
        # Create a file index
        myFileIndex = FileIndexer.FileIndex(myFile)
        return myFile, myFileIndex
        
    def setUp(self):
        """Set up."""
        self._prlMap = {}
        for k in self.TEST_SVG_FILE_MAP_ENTRY_MAP:
            self._prlMap[k] = Plot.PlotReadXML(k)
        self._lisFile, self._lisFileIndex = self.retFileAndFileIndex()

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotReadLIS_XML_LgFormat.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPlotReadLIS_XML_LgFormat.test_00(): Plot from XML LgFormat files."""
        for anIlp in self._lisFileIndex.genLogPasses():
            myXStart = EngVal.EngVal(self.PLOT_START_IN_FEET, b'FEET')
            myXStop = EngVal.EngVal(self.PLOT_START_IN_FEET-self.PLOT_LENGTH_IN_FEET, b'FEET')
            myTimerS = ExecTimer.TimerList()
            for lgFormat in self._prlMap:
                fp = TestPlotShared.outPath(TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY_MAP[lgFormat]].fileName)
                self._prlMap[lgFormat].plotLogPassLIS(
                    self._lisFile,
                    anIlp.logPass,
                    myXStart,
                    myXStop,
                    lgFormat,
                    fp,
                    frameStep=1,
                    title=TEST_SVG_FILE_MAP_LIS[self.TEST_SVG_FILE_MAP_ENTRY_MAP[lgFormat]].description,
                    timerS=myTimerS)
            sys.stderr.write(str(myTimerS))
            sys.stderr.write('\n')
            sys.stderr.flush()


@pytest.mark.slow
class TestPlotReadLIS_HDT_Example(TestPlotBase_00):
    """Example of a plot of HDT data extracted from real LIS file."""
    def _logicalRecords(self):
        return [
            b'\x80\x00HDT   .001                          1024                ',
            # DFSR
            b'@\x00\x01\x01B\x00\x02\x01B\x00\x03\x02O\x00v\x04\x01B\x01\x08\x04I\x00\x00\x00\x1e\t\x04A.1IN\n\x02O\x00\x00\x0b\x01B\x08\r\x01B\x01\x0e\x04A.1IN\x0f\x01BI\x10\x01B\x00\x00\x00BRHDTHDT               \x00\x00\x00\x00\x00\x01\x00Z\x00\x00\x00\x01\xea\x00\x00\x00\x00\x00P1AZHDT           DEG \x00\x00\x00\x00\x00\x01\x00\x04\x00\x00\x00\x01D\x00\x00\x00\x00\x00DEVIHDT           DEG \x00\x00\x00\x00\x00\x01\x00\x04\x00\x00\x00\x01D\x00\x00\x00\x00\x00HAZIHDT           DEG \x00\x00\x00\x00\x00\x01\x00\x04\x00\x00\x00\x01D\x00\x00\x00\x00\x00C1  HDT           INCH\x00\x00\x00\x00\x00\x01\x00\x04\x00\x00\x00\x01D\x00\x00\x00\x00\x00C2  HDT           INCH\x00\x00\x00\x00\x00\x01\x00\x04\x00\x00\x00\x01D\x00\x00\x00\x00\x00FEP HDT           VOLT\x00\x00\x00\x00\x00\x01\x00\x04\x00\x00\x00\x01D\x00\x00\x00\x00\x00RB  HDT           DEG \x00\x00\x00\x00\x00\x01\x00\x04\x00\x00\x00\x01D\x00\x00\x00\x00\x00',
            # Log data as type 0 records
            b'\x00\x00\x00\x16\x89L&4684%1474&1766%.586\'/286%.496%.4;6&.4<6%/5<7#-7=8$-6=6"/:=8$17>8$29=7"/:=7"1<?7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd2Y\x99@\xd9\x99\x9aD\xc1\xb2\xcdBM\x99\x99BK\xeb\x85CJ\x00\x00C\xc2\x99\x99%28<5"1;=5"2<=2%4==4&69<2%5992\'38;0&5880)4891)2770\'3681\'2582)/4:4&.382&04:5&04<3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd3\xb33@\xe6ffD\xc2\x99\x1cBM\x99\x99BK\xeb\x85CB\x00\x00C\xc4ff%.5<3&/4?7%-2=7&.4>6%.6?8\'06B7%05C8%/7D9&-5B6".7D6$38E5&38C5%28C5#58C5$6:?6$67=6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f@\xd9\x99\x9aD\x7f\xcc(BL\xcc\xcdBK\xeb\x85CJ\x00\x00C\xc8\x00\x00$68:3"7882!6974\x1d2:63\x191;34\x17.<43\x12.9/3\x0f(826\x08(4,3\x06&2\'4\x04#-*4\x03",)4\x02 &%7\x02$)&5\x03"$$:\x02 %\':\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd2\xcc\xcc@\xcc\xcc\xceD\xc2&\x1aBM\x99\x99BK\xeb\x85CD\x00\x00C\xc2\x99\x99\x02"#%:\x02!$\';\x01\x1e$&;\x04"$\'8\x02!$&:\x04"$(8\x04#"(9\x03$"+:\x03& *9\x02$\x1e,9\x05%"-;\x05\'\x1e,=\x04&\x1f,<\x02&\x1e.=\x04(\x1c-=\x04)\x1d.<\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd2\xcc\xcc@\xcc\xcc\xceD\xc1\xb2\xecBL\xcc\xcdBK\xeb\x85CD\x00\x00C\xc4ff\x04\'\x1b-<\x04\'\x1d-?\x04\'\x19/A\x05%\x1a+B\x06$\x1a.A\x05$\x1b-C\x05%\x17-B\x06&\x17-E\x07$\x1a.E\x07#\x19.D\x08%\x18/G\x08&\x17/F\n$\x19,D\x0b$\x19.C\x0b\'\x1a2E\t$\x17.C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f@\xcc\xcc\xceD\xc1?\xb4BK\xeb\x85BK\xeb\x85CJ\x00\x00C\xc2\x99\x99\t&\x191?\n$\x1a.?\n%\x190;\x0c(\x1b-<\x0b&\x1a/:\n\'\x18/7\r(\x1a+7\x0e&\x19,5\x0b$\x18+7\r&\x1a+2\r&\x19)2\r!\x18,1\x0c"\x19)-\x0b \x16*,\n!\x16*(\x0c\x1c\x16+$\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd2\xcc\xcc@\xc0\x00\x00D\xc1\xb3\x02BK\xeb\x85BK\xeb\x85CD\x00\x00C\xc4ff\x0c\x19\x11+!\x0b\x12\x0c.\x1b\n\x0b\t,\x13\n\x03\x08\'\x0f\x08\x02\x06\x15\x10\x08\x00\x05\x0b\x12\x08\x00\x06\x08\x12\x0c\x01\x08\x08\r\x07\x00\n\x08\x0c\x06\x01\x0b\x08\x0b\n\x06\x11\t\x0c\n\n\x0f\r\x0e\n\x0b\x0f\x16\x12\x0b\x0b\x10%\x16\n\t\r-\x19\x08\x06\x0c.\x1b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f@\xc0\x00\x00D\xc1\xb2\xfcBK\xeb\x85BK\xeb\x85CJ\x00\x00C\xc0\xcc\xcc',
            b'\x00\x00\x00\x16\x88\\\x08\t\t0\x1e\x07\x05\x0b3(\x08\x06\x0b6+\x06\n\n7)\x07\t\x0f:$\n\x06\x0f6\x1b\x0f\x06\x08;\x1a\x17\n\x0b@(\x15\x08\x0e<0*\x05\n/.6\x04\r\x1a*2\x03\n\x12",\x04\n\x10\x1b#\x02\x0b\x0f\x16\x1f\x02\n\x12\x18\x1b\x06\x0c\x10\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd2\xcc\xcc@\xc0\x00\x00D\xc3\x0c\x92BK\xeb\x85BL\xcc\xcdCF\x00\x00C~\x00\x00\x16\x07\x0c\x0e\x1d\x15\n\x0b\n \x14\x0c\x0b\x0c%\x12\r\x0b\x0b*\x11\x11\x0b\x112\x10\x11\x10\x170\x11\x12\x13!,\x12\x17\x15$*\x16 \x14\x1e&\x1a$\x14\x1a)\x1b*\x1d\x1c/\x1f/(*3"2232%0:>2)*AF3)%E?1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f@\xc0\x00\x00D\xc0\xcc\x9cBK\xeb\x85BK\xeb\x85CF\x00\x00C\xc4ff0\x1eG6-/\x17B&)-\x17;"%0\x155\x1e\x1d5\x0f)\x1c\x1d2\x0e)\x1d\x1e2\x12*\x1c"1\x152",0\x1a<"23\x1dB&65\x1dA*4.\x1d:+/&!6--+\'4).(%4).(\'2*-\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1s3@ffhD\xc1?\xddBK\n=BK\xeb\x85CL\x00\x00C\xc0\xcc\xcc&*4++$+2+($,1-(!+2+)"*1+\' .1+$!.2)$"+0)% ,2&%\x1f+2$$\x1e*2"" ,4\x1f"\x1f-6\x1d#"03\x1c& /2\x1d# -4\x1d%\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd2Y\x99@ffhD\xc1\xb3\x11BJ(\xf6BK\xeb\x85C@\x00\x00C\xc2\x99\x99!-2\x1b% *4\x1c&",2\x1c&!*1\x1d&\x1e*1\x1f\' ,0\x1f\'\x1e-2\x1f\'\x1f+0\x1e(\x1e-2\x1e(\x1d+4\x1f* -/\x1f(\x1d.2\x1d\'\x1f-2\x1e)\x1f-0\x1e)\x1d//\x1b("-.\x1d*\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1s3@ffhD\x7f\xcc\x92BJ(\xf6BK\xeb\x85CH\x00\x00C\xc633$-5\x1d+/5*#-0/%(+2)!(&3(#%%3%""&4\x1e&\x1f\'.\x1d%\x1b\',\x1e%\x18++\x1d&\x1a+,\x1d%\x1a-/\x1d&\x17.0\x1f\'\x1a./\x1d&\x1a0.\x1e(\x1821\x1c*\x1b2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd2Y\x99@ffhD\xc2\x99tBK\n=BK\n=CD\x00\x00C~\x00\x005\x1e-\x1c47\x1f.\x1d6;%5\x1e5@)6&7E-4\'4B-052B/<>7B/<=1@46?.A15;-?,;8+?)>5+>*B2+>,?7+>-<5,=0A5/\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f@ffhD\xc1?\xdeBK\n=BK\xeb\x85CD\x00\x00C\xc2\x99\x99B/=21A8>4/A8C32C=A24>>A06;B?46@C?;8BDC=8?CB=:@@B=:?=C>;@BD?==@?>99>C965;@:6.;B@5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\x00\x00@L\xcc\xccD\x7f\xcc\xaaBJ(\xf6BJ(\xf6CL\x00\x00C\xc4ff',
            b'\x00\x00\x00\x16\x87v#AFF2\x1b@BE4\x18BAA5\x1f=*22 :2*.\x1e7/** 5.*, :1(*\x1f7/%+$4/&+&0/$*\'\'*$\',"\'$%)\x1d""&+\x1d\x1f#%*\x1d\x1f #\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f@L\xcc\xccD\xc1\xb3\x1fBJ(\xf6BIG\xaeCD\x00\x00C\xc0\xcc\xcc)\x1a\x1e!"\'\x15\x1a$ %\x16\x17%\x1e*\x19\x17(\x1b*\x1a\x14(\x1b*\x1d\x16%\x1b+\x1b\x14 \x1b-\x1c\x17\x1d\x1b2\x1d\x16\x1f\x1a4\x1e\x13\x1a\x1b7$\x15\x1a\x188&\x1f\x16\x17<&$\x1e\x1a<&1\x1c\x19<)7\x1d\x1a<\'3\x1d\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f@L\xcc\xccD\xc0Y\x89BK\xeb\x85BK\n=CJ\x00\x00C\xc633A+,\x1c\x1c@.%\x1d\x1aA23"\x17==:+$@=E6B??@XAE:=<FG?:<DH=8=CF<5@DF=8:DEA<6FI>=8JF=?7JE??:LC=B>P\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\x00\x00@ffhD~\xe6,BK\xeb\x85BK\xeb\x85CH\x00\x00C\xc633=>E=OABK>LABM=PADP?HICSCE?CTED7@WF>6CRF>@GVG99KIA>=LMA>?HJDD>AJGB@>IB>B8C>9E5:98\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f@L\xcc\xccD\xc1\xb3\x1fBL\xcc\xcdBL\xcc\xcdCD\x00\x00C\xc0\xcc\xccA7887E=975H=878F?757F<:78J>:7:F89:<H51B;E57B<C59<8C7A@8B:@?6>4@?7@==C9@@>I=AA:N4\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@L\xcc\xccD}\xff\xddBK\xeb\x85BL\xcc\xcdCJ\x00\x00C\xc4ff9D?W.?IJ\\/@BJ`3CGIW9HGGW@RC@TBMG;Q>QE9M>RE?Q?@HNU:NMGX<UMHP=NOHN=L;LK>HMMCDHGEED\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@ffhD~\xe6#BK\xeb\x85BK\xeb\x85B\xfc\x00\x00C\xc2\x99\x99BB>BBB?;E<:=@=>1:@B=2:?E;25FD=+2<J6+*<=:-,<<9+5=54)6B44*5B42,4;23*5:31,3514,.621\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f@L\xcc\xccD\x7f\xcc\xaeBK\xeb\x85BK\xeb\x85CD\x00\x00C\xc8\x00\x00/.0.231.-/32\'+0*,\x19&//-\x1c)/2)".53.)+7:-/&5.\x1e1)47(5"/#,:&-429,3*-=;5,*;<82+<A=0/H?;\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x8c\xcc@L\xcc\xccD\xc0Y\x85BJ(\xf6BK\xeb\x85CH\x00\x00C\xc0\xcc\xcc',
            b'\x00\x00\x00\x16\x86\x86">7:>\'-E<=-\'A96\'*?;616@;5/19<5+)3:1+-5<2$,8=/"4:?+ 0*6,\x1f\'#6*5\x1f#:(L\x1f!$#^\x1e! %W\x1b\x1f"#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x8c\xcc@L\xcc\xccD~\xe6BBK\xeb\x85BK\xeb\x85B\xf8\x00\x00C\xc4ffR\x1a ""J\x1b\x1f"!C\x1a "":\x19 $"5\x19!#!/\x1a $!+\x18"$!&\x1a$&\x1f"\x1d#%\x1e"\x1f&\'\x1f\x1e\x1f%%\x1f\x1f%"& \x1f(%\'"\x1f+"&!\x1e5\x1f%"\x1fE ("\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99?\xe6fhD}\xff\xf0BO\\)BM\x99\x99C@\x00\x00C\xc4ff\x1fO 1\x1e!Y 3\x1f\x1b["\'\x1e\x17U!$ \x15P"!\x1f\x12D#\x1e\x1d\x129"\x1d \x142!\x19!\x15&\x1f\x1a#\x15$\x1d\x17#\x13\x1e\x1d $\x14\x1b\x1e \x1f\x15\x1b\x1d#\x1d\x13\x1c\x1d"\x17\x14\x1d\x1d&\x19\x15\x1d\x1f!\x1d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1s3?\xe6fhD\xc1?\xf7BO\\)BNz\xe1B\xf8\x00\x00C\xc0\xcc\xcc\x17\x17 $"\x14\x12 ""\x12\x0f ""\x16\x11\x1d\x1d\x1c\x13\r\x1b\x15\x16\x14\x13\x1a\x0f\x15\x13\x12\x1c\x0e\x14\x13\x11\x1c\x12\x19\x12\x11\x1b\x11\x16\x0f\x12\x1c\x14\x17\x10\x14\x1b\x11\x17\x0f\x14\x1a\x0f\x18\x0f\x11\x1a\x10\x18\x0e\x12\x1a\x10\x17\r\x12\x19\x10\x16\x10\x13\x17\x0f\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\x00\x00?\xe6fhD\x7f\xcc\xbdBO\\)BNz\xe1B\xf4\x00\x00C\xc4ff\x0e\x13\x17\r\x19\x0b\x12\x15\x10\x16\n\x11\x16\x10\x17\n\x10\x17\x0f\x16\x0c\x12\x15\x0e\x17\x0b\x12\x15\x0e\x17\r\x0f\x14\x0e\x18\r\x12\x14\x10\x1a\r\x12\x14\r\x17\r\x10\x15\r\x1a\x0e\x10\x14\x0f\x17\x0c\x12\n\x0e\x16\x12\x12\x13\r\x16\x16\x12\x15\x0e\x17\x1e\x13\x16\x0e\x15+\x11\x12\x0e\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x8c\xcc@L\xcc\xccD\x7f\xcc\xa6BO\\)BM\x99\x99CB\x00\x00C\xc2\x99\x99F\x0f\x14\r\x15_\r\x0e\x10\x15q\x0b\x0f>\x12z\t\x1e\xba\x12{\x08d\xce\rw\x17l\xd2\x15nOh\xd07\\nc\xcemHz[\xc5k+\x85U\xbc\\\x1c\x83Q\xa9U\x11}F\x8fZ\x0fz<d[\x13l*NL\x13b\x1d$;\x12L\x16\x14\'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1s3?\xe6fhD\xc1\xb3)BO\\)BNz\xe1B\xf4\x00\x00C~\x00\x00\x165\x18\x17\x18\x15\x15\x15\x17\x17\x15\x0b\x15\x14\x1b\x15\n\x16\x12\x18\x18\x0e\x17\x13\x15\x17\x0f\x1a\x15\x17\x19\x0f\x1c\x16\x1a\x18\x10\x1d\x17\x1c\x19\x12\x1f\x18\x1d\x1b\x14\x1d\x16\x1c&\x14\x1e\x1a\x1b*\x15\x1e\x1d%$\x14\x1f"\x1e\x1f\x15 \x1e\x1a\x1b\x17%\x1c\x1a\x1b\x1a)\x1c\x1b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x8c\xcc?\xe6fhD~\xe6VBO\\)BNz\xe1B\xfc\x00\x00C\xc4ff"\x17/ \x1d!\x1b4\'\x1d$\x1e7+\x1e&$2-!%***").!!\'(* \x1f\'*\x1f\x1d\x18"+\x1a!\x19\x1e*\x1a"\x1c\x1d*\x1d"\x1d\x1b(\x1c#\x1c\x1e\'\x1b$\x1f\x1e%\x1b$ !(\x1c#"#)\x1d#&$\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x8c\xcc@L\xcc\xccD\xc0Y\x85BM\x99\x99BNz\xe1B\xf8\x00\x00C\xc0\xcc\xcc',
            b'\x00\x00\x00\x16\x85\x96%\x1c#%&&\x1f%#%%\x1f&%%%\x1f+%%$$2\'%&&&&%+#**(+%.(&,)-*\',\'\'*#,&*(\'-\'. %*)+%&-,+0&/*-))/)-&)\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f@L\xcc\xccD\xc1\xb3\x1fBL\xcc\xcdBL\xcc\xcdB\xf0\x00\x00C\xc0\xcc\xcc1++-)3)**,5&)-)4\'%,,6&--*6(..,.&,-+ *1&--\'-6.+&%4.+("(-&/*.-%4*1*#\x19*/)$\'*.\'"\'*)*\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\x00\x00@L\xcc\xccD~\xe6EBK\n=BK\xeb\x85B\xf8\x00\x00C\xc633\x1e$(1#\x1a$&*%\x1a&%&\x1e\x1a"#("\x1a ") \x17!\x1f&\x1d\x16\x1b\x1f$\x1d\x15\x1b\x1d"\x15\x12$\x1d\x19\x18\x16\x14\x17\x18\x16\x16\x14\x1b\x1b\x16\x18\x12\x1a\x16\x11\x18\x0c\x16\x14\r\x16\x0e\x19\x16\x0c\x1a\x0c\x16\x18\x12!\x11\x16\x17\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\x00\x00?\xe6fhD\x7f\xcc\xbdBK\xeb\x85BK\xeb\x85B\xe8\x00\x00C\xc4ff*\x12\x17\x15\x14%\x0e\x16\x16).\x0b\x15 BE\x10\x15/Oh\x17".T\x89\x1d/\x1fa\x9f"(\x14v\xb3\x1a\x01\n\x8f\xbe\x1e\r\n\xa0\xc4-\r\n\xb2\xc8S\x08\x0c\xb8\xcfu\x06\x19\xc1\xd2\x8a\x02,\xc3\xd1\x9f\x07[\xc7\xd7\xb1\x06\x7f\xc5\xdc\xbc\r\x92\xc8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1s3@L\xcc\xccD\xc0Y\x88BNz\xe1BO\\)B\xe8\x00\x00C\xc4ff\xdb\xc6&\xa6\xc7\xde\xccO\xae\xc5\xdd\xcea\xb9\xca\xe6\xd7k\xba\xc7\xdf\xd2t\xc1\xcb\xdf\xd2\x82\xc4\xcd\xe1\xd2\x88\xc8\xcf\xdf\xd0\x94\xcb\xd2\xdb\xd2\x9d\xcc\xd2\xda\xce\xa2\xd1\xd7\xda\xcd\xa7\xd2\xd5\xd7\xcd\xb4\xd5\xd8\xd1\xce\xb5\xd9\xd9\xce\xd0\xbb\xd7\xd7\xbd\xd0\xc2\xd9\xd6\xa2\xce\xc1\xdc\xda\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x8c\xcc@L\xcc\xccD{L\xb2BQ\x1e\xb8BO\\)B\xe4\x00\x00C\xcb\x99\x99[\xcb\xc8\xda\xd21\xce\xcf\xdd\xd3\x12\xce\xcf\xde\xcf\x0c\xd0\xcf\xdb\xc5\x15\xd0\xcd\xda\xc0\x19\xd2\xd0\xdb\xa8\x1d\xd0\xd0\xd8\x87\x1e\xd0\xcf\xd6:$\xca\xcf\xd1\x16&\xb5\xca\xc2\x04&\x8b\xcc\xb2\x06*r\xcb\x90\x05,C\xc6y\x04.#\xc2Q\x072\x11\xbf4\x002\n\xb9\x16\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\x00\x00@L\xcc\xccD}\xff\xe1BP=pBO\\)B\xdc\x00\x00C\xc8\x00\x005\n\xb9\t\x0e8\x10\xb1\x05\x15;\x12\xab\x05\x1a=\x17\xaa\x02 ;\x13\xaa\x05";\x14\xab\x07%:\x16\xac\x05%8\x16\xab\x04&8\x16\xb1\x02&:\x18\xaf\x05&6\x1a\xaf\x02(9\x1c\xb3\x05(5\x17\xb0\x07*6\x1d\xb2\x0b*3\x1d\xb1\x06+1\x1d\xb2\x14+\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f?\xe6fhD\xc0Y\x92BP=pBQ\x1e\xb8B\xec\x00\x00C\xc6335%\xaf\x19+2"\xa9\x1a-0$\xa2\x1e//&\x9d$-.\'\x95#,*%\x8c&-((\x89(/&(\x82*."&s*0\x17)e-2\x10,Q/2\t+J44\n-E65\x020D:4\x01/G;6\x022E<2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\x00\x00@L\xcc\xccD\x7f\xcc\xaaBP=pBQ\x1e\xb8B\xe0\x00\x00C\xc4ff',
            b'\x00\x00\x00\x16\x84\xa6\x032H=4\x022J=2\x012K?/\x023N>0\x014O?.\x027P@/\x015QB,\x029T?)\x02:U@$\x02<U>"\x02?Y=#\x039X>"\x02=W>\x1f\x03=V<\x1f\x02:T8\x1d\x02:T7\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1s3@L\xcc\xccD~\xe6HBQ\x1e\xb8BQ\x1e\xb8B\xd8\x00\x00C\xc8\x00\x00\x02:Q7\x1a\x03;N:\x18\x034M5\x0f\x020K5\x0b\x06*J5\x05\x0c"F7\x07\x1b\x13?5\x03\x1d\x0862\x03!\x00"/\x00$\x00\x13\x1c\x0c%\x00\t\x0e\x04%\x00\x05\x02\x00%\x00\x03\x01\x00\'\x00\x02\x01\x02)\x00\x02\x02\x03)\x00\x02\x02\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x8c\xcc@L\xcc\xccD}\xff\xdeBQ\x1e\xb8BO\\)B\xe8\x00\x00C\xc633)\x00\x02\x01\x04*\x00\x01\x00\x05)\x00\x02\x01\x04*\x00\x02\x02\x05-\x00\x03\x03\x04.\x00\x03\x04\x05.\x00\x02\x08\x071\x05\x03\r\x0e/\r\x02\x11\x18/\x16\x02\x17 3\x12\x03\x17&1\x16\x03\x1c+0\x19\t\x1e2/\x1d\x13 8/\x1b\x18%>/#\x1e$?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f@L\xcc\xccD\xc0\xcc\xbbBQ\x1e\xb8BO\\)B\xe0\x00\x00C\xc4ff.$#*E/&&*F*(+,F+\'*-F*#+0J\'\'*0G&(.2G))/5J*,/1H()12G%+24H\'*/4C\'-22C)-54E(-24A)-26B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x8c\xcc@L\xcc\xccD}\x19zBS\xc2\x8fBO\\)B\xe8\x00\x00C\xc8\x00\x00(.32>(./1>)/20>*.2.>*,01?*./.=$-/1A\'+//B&,.0A"*.1>",-2A"+./=\x1e+-2> +.3@\x1d).3B\x1b*.1@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\x00\x00@L\xcc\xccD\x7f\xcc\xaaBR\x00\x00BO\\)B\xe8\x00\x00C\xc4ff\x1a*23?\x15(/5?\x15(22=\x12*32=\x10-22=\x0f+209\r,427\r+4/5\n.3/5\x0805+5\x07+2+4\x07-2*2\x05-2*2\x05/2*4\x05+.)4\x02,/)5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f@ffhD\xc1?\xdeBR\x00\x00BO\\)B\xd8\x00\x00C\xc2\x99\x99\x05,/*3\x02).\'6\x04*-\'5\x04\'%&3\x03$\x12 -\x15\x1e\n\x1d\x1f\n\x19\x0b\x15\t\x1d\n\r\x12\x05#\x03\n\t\x06(\x00\t\x06\t-\x00\x07\x06\x08/\x01\x05\x08\x11/\x03\x06\x0b$1\t\n\x11.0\r\x19\x1f<4"=\x00B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x8c\xcc?\xe6fhD~\xe6VBQ\x1e\xb8BO\\)B\xe8\x00\x00C\xc4ff1*:2K&1FSK$2B[K\x1a.BV>\x13"\x11\x10\x02\x0e\x1f\x02\x00\x07\x01\t\x0e\t\x08\n\x11\x17\x15\x1eB\x00\x01\x17\tV\x00\x03<\x05r*\x135:\x7fF6:_\x8fg]Rw\x8dhco\x90\x8dwpv\x9e\x90\x80t\x7f\x97\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1s3@ffhD\xc0\xcc\xabBQ\x1e\xb8BO\\)B\xd8\x00\x00C\xc2\x99\x99',
            b'\x00\x00\x00\x16\x83\xb6\x81|u\x82\x98\x85{v\x86\x8d\x81|s\x90Yzq{\x8b2pso\x87Fsrz\x86qpuw\x8amdyr\x86o\x1dzo\x89j\x0bwm\x89b;L`}\n{\x00#\xc3\t\x96\x04\r(B\xb3abvz\xbe\x8c\x83\x92\x9c\xc0\xaf\xa1\xa1\xb0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f?\xe6fhD\x7f\xcc\xbfBX\xf5\xc2BR\xe1GB\xd8\x00\x00C\xc8\x00\x00\xd4\xc5\xae\xa9\xc5\xd8\xce\xbb\xab\xc8\xdd\xd3\xba\xb1\xd0\xd7\xd9\xc4\xbd\xd5\xd9\xd9\xc6\xbe\xd6\xd5\xde\xc2\xbd\xdc\xd5\xda\xbf\xc4\xe1\x9f\xdf\xbc\xcf\xda#\xd8\xba\xc9\xd5B\xd5\x9e\xc56N\x85-\xbf\x03K\x06\x02\xb7\x1e8;\x1f\xae)$?3\x8bZ/A>xL-<DY=\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f?\xe6fhD}\xff\xf5B]\\)BS\xc2\x8fB\xe4\x00\x00C\xcb\x99\x99@%4G5A$37-E6*@.M?)H6JF(E;KC,JDLL3KKOL:KRTP?TKVR=SJTT?UMXW?TLYR>SRWR?ONXQ?RTYO?PW\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd3@\x00?\xe6fhD\xc0Y\x94B]\\)BW33B\xd8\x00\x00C\xcb\x99\x99WM>RVXMBRZVM?T[RJAV]RJCYZTKCX^PJDY^PLC[^PMG[\\OJB]^MNG][KQJ^]PNJ]ZNOJ]ZLQJ^\\NRJZX\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd3\xb33?\xe6fhD\x7f\xcc\xc4BY\xd7\nBVffB\xe8\x00\x00C\xcf33OSN[XPTNZWTUN[WUTNUVRTMVVVUMUWUUJVXVRMUWWSLUZTQLV[TRNU^UONV]RJMWbQKNZaQNMY`RJN[b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd2\xcc\xcc@\xe6ffD~\xe5\xc9BX\xf5\xc2BW33B\xdc\x00\x00C\xcdffQJNZaMLP`dNJQ]bLMO_bNMPbbKQPcbLNRbaNRSb_LSRb^OUR_\\NURa^RVR_YSTO^ZTWR^ZVXR\\ZWSNZY\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd3\xb33@\xd9\x99\x9aD\xc0Y^BW33BW33B\xe0\x00\x00C\xcdffTVNZ[VWNWYWTNZ^VSPY[VVOZ_VQM\\`SQL[_RPP_dTQR^cRNO^fRNS`gQLV^jMNS`gOOWbfMNWbgNRZgf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd3\xb33@\xcc\xcc\xceD\xc0YmBW33BU\x85\x1eB\xe4\x00\x00C\xcdffOR]eeOR^dePQ]gbOW_e_NV_f`RW`e`OX_b^OW^e\\RV]c_TZ^b]U]`^]V[^d]X][`^VW]^cVV\\]eRSZ^d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd3@\x00@\xcc\xcc\xceD~\xe6\x1aBU\x85\x1eBS\xc2\x8fB\xd8\x00\x00C\xcf33',
            b'\x00\x00\x00\x16\x82\xc6RRZ_iTX]chRX_clRVcalOUlbnIRkerDTmdo6Upho"Rqes\x04Tqen\x00Tueb\x00PreR\x01Ptb-\x02Fs`\x1e\x01.r]\x19\x01\tY[\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd3\xb33@\xcc\xcc\xceD}\xff\xcdBT\xa3\xd7BQ\x1e\xb8B\xe4\x00\x00C\xd2\xcc\xcc\x03\x01 S\x06\x12\x00\x167\x06 \x00\x04\x02\x01\x1e\x00\x00\x00\x021\x00\x02\x02\x057\x00\x02\x00\x03C\x08\x03\x02\x03L\x19\x02\x16"Z!\x02\x1d5`)\x10*Ag623He:7<T]MFAZQUMH^JZSObOWZMh\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd3\xb33@\xcc\xcc\xceD\xc0\xcc\x9bBS\xc2\x8fBO\\)B\xe4\x00\x00C\xcb\x99\x99XZ^Tg^LbUj_DeYhgMlZhdRobfh`tebjavg`hevl]nhumZmoxqYmrup_oy{r]lxzrbqwsrax\x82sqdlt}nj\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd3\xb33@\xcc\xcc\xceD~\xe6&BT\xa3\xd7BO\\)B\xd8\x00\x00C\xd1\x00\x00jr|wfnnwwdkqvwgmqvsghnvyjmnuxjikv}jglw}pgfw~oeg|\x82jbi}\x82q_gy\x82qbex\x84r]iz\x87r\\j|\x85m^m{\x83l\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd4&f@\xc0\x00\x00D\x7f\xcc\xa1BX\x14{BS\xc2\x8fB\xe4\x00\x00C\xd1\x00\x00Zpy\x81jUot\x81_Mqq|U\x14|cuD\x0e|Wh6\x1fgCX+/e9=\x1aD`#2\x17Z[\x1a+\x1atG\x1a%\x15~.!#\r\x86\x14\x1e\x1e\x03\x91\x12\x0c\x14\x05\x95 \x0e\x11\x06\x9c*\x11\x0f\x07\xa3D\x0f\x0f\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd4\x99\x99@\xc0\x00\x00D\xc0Y\x83BW33BR\x00\x00B\xd8\x00\x00C\xd1\x00\x00\xa4Y\x15\x14\r\xa5d\x08d\x0c\xa5q\x05l\x0f\xa7|\r{\x0e\xa4\x86H\x84\'\xa4\x8ed\x90g\xa5\x9cz\x93~\xa0\x9f\x84\x97\x95\x9d\xaa\x93\x9f\x97\x96\xaf\x9e\xa2\xa0\x8e\xb4\xaa\xa3\xa7\x81\xb6\xb5\xa1\xabh\xbf\xba\xa6\xabF\xc3\xbe\xa4\xaf)\xc4\xbf\xa2\xae\x14\xc4\xbf\xa2\xb4\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd5\x0c\xcc@\xc0\x00\x00D\x7f\xcc\xb1BU\x85\x1eBR\x00\x00B\xd8\x00\x00C\xd4\x99\x99\x10\xc4\xc0\xa1\xb7\x0f\xbc\xbe\xa0\xba\x0e\xb4\xbb\xa3\xbc\x0b\xa6\xbc\xa0\xbf\n\x99\xb7\xa4\xc3\x0b\x84\xb6\xa5\xc4\nq\xb4\xa8\xc8\x0bM\xa7\xab\xcd\t7\x98\xad\xcd\n\x1bg\xaf\xcc\x0c\x127\xb1\xcc\r\x0f\x10\xb2\xca\x14\x0b\x0e\xae\xc7\x15\t\x05\xae\xc5\x15\t\x01\xaa\xba\x12\x07\x00\xa5\xb1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd4\x99\x99@ffhD~\xe6UBT\xa3\xd7BR\x00\x00B\xec\x00\x00C\xd4\x99\x99\r\x08&\x9c\x92\x0c\n\t\x94q\x0b\r\x0c\x8eB\t\x0b\x10\x88\'\x08\x06\x10~\x12\x07\x08\x0fv\x0e\x0c\r\x0fl\x15\x16\x0e\x0fZ\x0e \x12\x0fP &\x13\x0f9\x0e.\x11\x0f+\r/\x0e\x10\x18\r8\x0b\x08\x11\r=\t\x0f\x0f\x0c?\t\x10\r\x10D\n\x0c\x0c\x13\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd5\x80\x00@ffhD\xc0\xcc\xc1BS\xc2\x8fBR\x00\x00B\xdc\x00\x00C\xd2\xcc\xcc',
            b'\x00\x00\x00\x16\x81\xe0D\x06\r\n\x12F\x05\r\x0c\rH\x04\x10\x0e\x0fM\x07\x10\x0b\x12L\x0c\x10\x0c\x0bM\x16\x13\x08\nN\x1e\x14\x05\x14M*\x18\x08\x1dT.\x1a\x05\x1eW; \t\x17V; \x0c\x14UA"\x17\x13ZE&\x1b\x14]L+\x1f\x15_M*%\x12bR0(\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd4\x99\x99@ffhD~\xe6UBR\x00\x00BQ\x1e\xb8B\xe8\x00\x00C\xd4\x99\x99bT4/\nfZ52\tfZ:5\x07hZ88\tjZ:>\x0ch];?\x18f]=D2e[>CBb\\?IR_ZBJWNZ@O`:XATd\x15ZETc\x07ZDVg\x16\\E\\g\x02aDZg\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd4\x99\x99@ffhD\x7f\xcc\xb6BR\x00\x00BQ\x1e\xb8B\xe8\x00\x00C\xd2\xcc\xcc\x07_G^g\x01aJ_i\x01bK_f\x00cL_e\x01eJac\x01eJbb\x00dJ`b\x07fL_]\x08cH`[\x12TI]W\x1b:HYQ\x1c\rFZ"\x1d\x02DT\x04\x1b\x00=P \x19\x00;I\x04\x11\x009D\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd5\x80\x00@\xc0\x00\x00D\xc0\xcc\xbbBP=pBR\x00\x00B\xe0\x00\x00C\xd2\xcc\xcc\r\x006=\x03\t\x0076\x04\n\x002+\x04\x06\x00+%\x02\r\x00"\x02\x02\x0f\x01\r\x00\x04\r\x02\n\x02\x07\r\x12\x02\x01\x08\x15\x16\x02\x00\x10\x12\x17\x04\x00\x14\x06\x1b\t\x02\x1e\x0b\x19\x14\x01\x1f\x12\x17\x1a\x02"\x0b\x14\x1b\x0e\x1f\x0e\x12\x19\x19\x1d\x13\x18\x1b&\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd5\x80\x00@\xc0\x00\x00D\x7f\xcc\xbbBP=pBR\x00\x00B\xec\x00\x00C\xd6ff\x1b\x01"(\x11\x1d\x08&$\x12\x1f\x12.\x1f\x10\x1e\x0b,\x14\x16#\x0e0\x10\x166\x132\x0c\x12<\x001\x0c\x12H\x0b1\x11\x10L\x142\x13\x10Y\x0f2\x1a\x15[\x115\x1b\x1af\x10:\x1d\x1en\x1c:\x1f\x1dr\x1aA%\x1av\x19E.\x1bw\x17L2\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd4\x99\x99@L\xcc\xccD\x7f\xcc\xc0BP=pBR\x00\x00B\xdc\x00\x00C\xd2\xcc\xccw\x1cT;\x1ez(ZE"v2_K,v:dL4uAhR>sIpUBtQq\\Jw]u_PwdzbUuozdUty\x7ffXn\x7f}f[d\x82\x7fg_R\x88\x7ffa,\x8a\x82hef\x86{if\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd5\xf33@L\xcc\xccD\xc1?\xf9BP=pBQ\x1e\xb8B\xe0\x00\x00C\xd2\xcc\xcc\t\x85zgf\x0e\x86yij\x1d\x82xhm"\x7fwjm$\x82vip%}vmr$|tkq!vxou\x1ewvoy\x1ctuou!rwrt$qyuw\x1fkwuv![vvu Ovwo 6swn\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd5\x80\x00@ffhD~\xe6aBP=pBR\x00\x00B\xf0\x00\x00C\xd833$\'oui$\x1bqtk%\x13itf#\x0eeog"\x0c_na\x17\x0fTkd\t\x1bLd`\x05%Ec^\x03$>^b\x05\x1e6Z_\x13\x1f-U_\x12"*V]\x05\x1d\x1cUY\x02\x1f TY\x02!\x1bUU\x00$\x17VN\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd5\x0c\xcc@ffhD\xc0\xcc\xbeBP=pBS\xc2\x8fB\xe4\x00\x00C\xd1\x00\x00',
            b'\x00\x00\x00\x16\x80\xf0\x02"\x1aXK\x01!\x1dWF\x0c" Z=\x17""\\*-\x1b\x1f[\x1eL\r"Y\x14X\x01%Z\re\x01$V\x02j\x02"X\x06m\x12 N\rq\n\x1aI\x1er\x02\x1e;\x13s\x00\x1a*\x06p\x02\x1a\x1d\x05r\x14\x1a\x0f\ro7\x1d\n\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd5\x80\x00@ffhD\xc1?\xf1BO\\)BR\x00\x00B\xe8\x00\x00C\xd1\x00\x00kP#\x1b$gh0&/ds>35W\x7fS(;D\x81b\n<\x19\x80l\x057\x07\x82t\x1a3\x07\x7f}%(\x05y~1\x10\x06t\x83:\x03\x03p\x86A\x14\x08g\x88B\r\x06d\x8c;\r\x05_\x8d6\r\x07V\x8e1\x0c\tU\x8d%\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd5\x80\x00@ffhD\xc1\xb3"BO\\)BR\x00\x00B\xf4\x00\x00C\xcf33\x06H\x8a\x1f\r\x07;\x82\x17\x10\x07\x16c\x11\x0f\t\t8\x08\x0e\t\x04\x0e\t\x0b\t\x02\x05\x08\r\n\x02\x18\x08\r\x0b\x05\x01\t\x0e\x0b\x05\x06\x08\x16\r\x04\x08\x0b\x13\x10\x06\x08\x0c\x0e\r\x06\x08\x0b\x0e\x0c\x07\x0b\r\x11\x0f\x0b\x05\x0b\x11\r\t\x07\x0b\x0f\x10\x06\t\x0f\x11\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd4\x99\x99@ffhD\xc0Y\x8bBP=pBO\\)B\xe8\x00\x00C\xd1\x00\x00\x10\x0b\n\x01\x12\x0f\n\x0b\r\x16\x0f\x0b\x08\n\x15\x13\x0c\n\t\x16\x11\n\n\r\x16\x0e\n\x07\x0b\x14\x0e\x0e\x08\x0b\x1a\x0b\x0b\n\x0c\x1b\x10\n\x0b\x0e\x17\x0f\x0f\x0e\r\x18\x0f\x0f\r\t\x16\x0b\x0f\x08\x0b\x14\r\r\n\x0b\x16\x0b\r\x08\x0b\x16\x10\x0f\n\n\x12\x0f\x0f\n\x07\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd4&f@ffhD\xc0Y\x88BQ\x1e\xb8BQ\x1e\xb8B\xf8\x00\x00C\xcf33\x0e\r\n\x08\x17\x0c\x0c\t\x08\x11\x0c\x0e\x0b\x0b\n\t\x0c\x0b\x0f\x12\x0c\r\x0c\x0e\x10\x0b\x11\x0b\x11\x14\n\x0c\x0b\x16\x15\x0b\x0b\t\x14\x1e\n\x0c\x07\x0e!\t\x0b\x07\x13"\n\r\x08)+\n\t\x08I6\x08\x06\t\\;\x08\x06\ts:\x06\t\n\x80>\x07\x07\x08\x90T\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd5\xf33@ffhD\xc2&UBP=pBQ\x1e\xb8B\xf8\x00\x00C\xcf33\x08\x08\x08\x99o\x08\x07\x04\xa0\x8c\t\x02\n\xa6\xa1\n\x07\x12\xa8\xab\x08\x06\x16\xae\xb5\x0c\t\x13\xae\xb6\n\t\x0c\xb2\xb9\x0b\x04\x07\xb4\xb7\r\x06\x06\xaf\xa3\x0e\x05\x05\xadM\x0f\x07\n4\x05\x10\x08\x07\x03\x00\x0f\x06\x08\x04\n\r\x08\x05\x05\x0b\x0e\x08\x11\x02\x07\x0e\r\x06\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd4\x99\x99@L\xcc\xccD\x7f\xcc\xc0BQ\x1e\xb8BQ\x1e\xb8B\xf0\x00\x00C\xd2\xcc\xcc\x11\x0f\r\x00\x19\x0b\x0f\x11\x02\t\x0b\x0f\x07\x05\x0e\t\r\x0b\x04\x0b\t\x0b\r\x04\x0c\x07\r\r\x04\x0b\x07\x0e\x08\x03\n\x05\t\x08\x03\n\n\x1b\n\x04\t\x1e\x0b\n\x02\nW\x06\n\x08\n}\x06\n*\x07\x8e\x06\x06H\x07\x9e\x04\x0f^\x08\xa0\x05<j\x12\xa6\x10ivP\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd4&f@L\xcc\xccD\xc0\xcc\xc2BQ\x1e\xb8BR\x00\x00B\xfc\x00\x00C\xcdff\xa63\x97z{\xa9s\xa9|\x92\xa5\x92\xb4|\x99\x9e\xa9\xbf{\x9e\x99\xb2\xbdu\xa0x\xbc\xbfr\xa2Z\xc0\xbfj\xa4)\xbf\xb6d\xa5(\xbc\xadT\xa2%\xb3\x8eL\xa1&\xa4]A\xa4(\x94!:\x9f1\x83\x15-\xa05`\x0c%\xa2-B\n%\x9d+0\n+\x9c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd5\x0c\xcc@ffhD\xc1\xb3\x1fBS\xc2\x8fBR\x00\x00B\xec\x00\x00C\xcdff',
            b'\x00\x00\x00\x16\x80\x002"\x158\x8e4\x1d\x1aE|3!*O\\4&/\\H/-7_*-%=e 0(Jk)0-Oo282Ut\';2Zv$>1[w"D1^s*B8bp\x1d=?bo 5J`j0\x17I`i?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd4&f@ffhD\x7f\xcc\xb0BS\xc2\x8fBR\xe1GB\xf8\x00\x00C\xd1\x00\x00\x8bK[eB\x11MZXC\rFTQF\x14;F?/\x1a%-,\x16\x17\x06\x07\x1a&\x14\x02\x05\x06\x0f\n\x00\x0c\x06\x0e\x04\x14\x0e\n\x11\x10\x17\x0c\x12\x16$\x16\x07\x0b\x1a3\x11\r\x06\x12%\x1b\x07\x12\x17\x1c\x03\x16%\x19\x1c\rD6:\x1a"\\BM\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd4&f@ffhD\xc0Y\x88BQ\x1e\xb8BR\x00\x00B\xfc\x00\x00C\xcf33\x1a0TN_\x17%BO`\x17\x1cHQ`\x10\x1dBP]\x12\x1eMFZ\x19"6:P\x18\x17\x16-G\x14\x15\x14\x1a5\x1e\x13\x12\x12(:\x16\x1a\x14\x1fn\x13\x1a\x17\x1a\x91\x15\x17\x14\x1c\xaa\x1d\x17\x16\x1b\xa0\x11\x16\x15\x1aj\x13\x18\x1f\x17(\'*U*\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd5\x0c\xcc@ffhD\xc1\xb3\x1fBQ\x1e\xb8BR\xe1GB\xf8\x00\x00C\xcdff\x16^T\xacW\x1d\x84o\xc2\x88&\x9a`\xc2\x85\x1fz2m/&O\x18\x1c\x1f#\x1a\x1b\x17"&\x15&\x1d"( &!$("%#(* *))* 2)+(%/,-*&0+-+%4/++&32.--,1.\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd3\xb33@ffhD\x7f\xcc\xaaBP=pBR\x00\x00CF\x00\x00C\xcf33.+.32-+/1(+-/6-)--./*-0*-*/,5=)--2,\'.*2:*)*26+%(2:*\'+26*%+36."+75. -640#0640$5;5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd4&f@ffhD\xc0Y\x88BO\\)BO\\)CD\x00\x00C\xcf33/%4=42%5=52&7@24&3>/1(5A23.8B/0,=A.30<B051;;.//<<122<:245<;157::1559545485495568\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd4&f@L\xcc\xccD\xc0Y\x90BNz\xe1BO\\)CB\x00\x00C\xcf33665864436:/359?/059:+289:-069?0/67*.03=;1/4?=0*2>;-*4>9-)7<5/\'4>:-%4=:.(1?7,(6B:\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd3\xb33@ffhD~\xe6IBL\xcc\xcdBO\\)CH\x00\x00C\xd1\x00\x00/*9A83.:>:4/<A622;>54/=>45-DA641:>35.7?57.9>77.8>47/8<8919>98/-:5=04>3;37?2:25>5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd4&f@ffhD\xc0Y\x88BL\xcc\xcdBO\\)B\xfc\x00\x00C\xcf33',
            b'\x00\x00\x00\x16\x7f\x10=/5>9=2;>::26A=<06E?:27C@908EA407D?4/<GB5-;DB4/;DA23>IA/6@G?57AK=3:@H>1:=J=*9?E:\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd3\xb33@ffhD\xc0\xcc\xb7BK\xeb\x85BM\x99\x99CD\x00\x00C\xcb\x99\x994:<F<7:=E:6::B87;;@87:<>6:8<?;99;;<;28A?735?@945>>=34@B902A<822>;6/4?>704?A:/4=D\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd3\xb33@ffhD\xc0\xcc\xb7BK\xeb\x85BM\x99\x99CD\x00\x00C\xcb\x99\x99606>F709?F607BG90:@D5/<BC32:BD71@BD52>E?42>G?75>@B55BCA46<AA56@A?7::?B67=>@79>=>\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd2\xcc\xcc@L\xcc\xccD~\xe6PBK\xeb\x85BL\xcc\xcdCB\x00\x00C\xcdff96>>?<8?;>;5=>?=8:;B=7:>==49<:<4:>:=5;;>;59>>;36<D728>B829?B:7:AD759EE728EE958GD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd3\xb33@\xc0\x00\x00D\xc0\xcc\xaaBK\n=BL\xcc\xcdCH\x00\x00C\xcb\x99\x9986=HC55:GC64<FB65<ED66<I?68;FA98=D>::<I;99;E=<:;D<?:<B<;=<A<<:>?:<<:><=9:A:?97?@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd2\xcc\xcc@ffhD\x7f\xcc\xa0BK\xeb\x85BL\xcc\xcdB\xfc\x00\x00C\xcb\x99\x99?58A>:66=?=66?A:8:>B=68@E;7:@D866AC;69BB:3:AE:58DE769DF77=EB6;:DD68<BD68=B?87>DA\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f@\xc0\x00\x00D}\x19\\BK\n=BK\xeb\x85CD\x00\x00C\xcdff:;>FB;8>DC<:>B@:<:B;@:;B>=:;:>>:9@@=;7??:<6>?:96==:55<C;<9=@:77=B977@D:59AG:47BE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd2Y\x99@ffhD\xc0Y~BJ(\xf6BK\xeb\x85CB\x00\x00C\xc8\x00\x00:59BD72;D=44;C<52;DA42:CB52:DB45<D=44;C<66:@=89=B=68<?9:;<?;88;=:96<>:89<=989<;9\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f@L\xcc\xccD\x7f\xcc\xaeBK\n=BK\xeb\x85C@\x00\x00C\xc8\x00\x00',
            b'\x00\x00\x00\x16~ <:?;<:9:9:8:9:;997:=867:=557:<566:=525;?544;?214=@453<A225=A336AD216AE226BA309@@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x8c\xcc@ffhD~\xe6&BK\n=BK\xeb\x85CD\x00\x00C\xc4ff5.:C?31<?@40;>@6/9>=718><61:>=74;<;868>9:57=:;66:=967;:=74=:=64;<<63<=>64;>>66<@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\xe6f@L\xcc\xccD\xc1\xb3\x1fBK\n=BK\xeb\x85B\xf8\x00\x00C\xc0\xcc\xcc@65<@?75<>>55>?@45?=>54>==46@?:16A?84:?>55;A@57=C@55=E@45=B@17>F?7;>D@4:?E>6;BB<\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@ffhD~\xe6#BJ(\xf6BK\xeb\x85CH\x00\x00C\xc2\x99\x9979DB;9:CD;6<DB;7:?F5:9?A6=7>>7>8=?8;79>6989=7:8:=9;8:;6<99;7:87:6:6789;56=8:49>9\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@ffhD~\xe6#BJ(\xf6BK\xeb\x85CB\x00\x00C\xc2\x99\x99737:972:A:536=:30:@924??925A?744>?725@?636>>416==516<=449;;4268:527:922:;9267<72\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1s3@L\xcc\xccD\xc0\xcc\xbaBIG\xaeBK\xeb\x85CD\x00\x00C\xc2\x99\x994898245772549846257571576545583-1655-1845-274/.2:50/395&0395+/2:4*0795(.993*-972\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@ffhD}\xff\xc1BIG\xaeBK\xeb\x85CJ\x00\x00C\xc4ff(1871&&664%(64/ ,62.\x1d+600\x1c160-#.7--(05**(+2(,*+1"*\'#0&*%\'0*(!\x1d,)(!\x1a+&$\x1e"*"# &\'!$\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@L\xcc\xccD~\xe6@BHffBK\xeb\x85B\xf8\x00\x00C\xc2\x99\x99"%%"%\x1d"/$&  #$&\x1d\x1b$ *\x1b\x1a"\x1e)\x1a\x1a-\x1f)\x19\x1b#\x1f$\x19\x1c$\x1f&\x17\x1b$!\'\x17\x1c" $\x14\x1d\x1f"\x1e\x14\x1b" "\x12\x18\x1f\x1d\x1f\x15\x1c\x1d\x1d!\x1a\x1b\x1f\x1e\x1e\x1b\x18\x1b\x19 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\x00\x00@L\xcc\xccD\xc0Y\x86BK\xeb\x85BL\xcc\xcdCF\x00\x00C\xc2\x99\x99',
            b'\x00\x00\x00\x16}0\x1d\x19\x1a\x19\x1b%\x17\x1b\x17\x1c4\x13\x19\x16\x1dG\x11\x16\x15\x19n\x10\x15\x13\x19\x92\x0e\x11\x13\x15\xc0\x10\x12\x11\x12\xd4\x12\x15\x0f\x10\xe4\x12\x14\x11\x11\xe6\x16\x19\x0f\r\xee\x1b$\x10\x10\xf0"6\x12\x12\xf07P\x15\x11\xefIj\x1d\x19\xedr\x8a"$\xe6\x89\x9e5?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@L\xcc\xccD\xc0Y\x85BM\x99\x99BO\\)CD\x00\x00C~\x00\x00\xdd\xb3\xbaMb\xcc\xd0\xcc\x7f\x8f\xbb\xd8\xd2\xab\xa6\x99\xe1\xdb\xd2\xba\x7f\xe8\xdf\xe3\xc2e\xec\xe2\xe8\xc6W\xef\xe6\xee\xc4L\xf4\xec\xf2\xbfJ\xf5\xeb\xf7\xb9H\xf6\xec\xf5\xb2J\xf6\xec\xf5\xa6L\xf6\xe9\xf4\xa6P\xf4\xea\xf2\x9fW\xf1\xe8\xf0\xa4^\xee\xe8\xf1\xa9b\xe2\xe5\xea\xae\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@L\xcc\xccD~\xe6@BO\\)BNz\xe1CD\x00\x00C\xc2\x99\x99j\xdc\xe1\xe6\xbcl\xd0\xe0\xe2\xc2s\xba\xda\xd9\xcax\xa4\xd7\xd0\xcf|\x8b\xd5\xba\xd6||\xd1\x95\xdb}o\xd0z\xdd~j\xd0d\xe0z]\xceP\xe4zW\xce:\xe2{T\xd16\xe5zR\xd0,\xe5vQ\xd1\'\xe2xP\xd2\x1f\xe2wM\xd1\x1c\xe5xO\xd1\x17\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf\xa6f@L\xcc\xccD}\x19vBO\\)BO\\)CH\x00\x00C\xc4ffzN\xd5\x16\xdf{O\xd4\x10\xe1zL\xd1\x0f\xdd}K\xce\r\xdc\x84K\xcb\x0b\xdc\x85G\xc6\n\xda\x85F\xc5\x0b\xd9\x88F\xbc\x0b\xdc\x8aF\xb0\n\xdb\x8eD\x9e\n\xdc\x8fE\x8f\x0f\xdd\x8bGw\x14\xde\x89El\x1b\xde\x8cM_"\xdf\x89KV*\xe2\x82PR.\xdf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@ffhD\xc0YtBP=pBQ\x1e\xb8B\xfc\x00\x00C~\x00\x00\x80QS6\xdf\x80TR=\xe1zVT>\xdew\\VB\xddu`\\E\xddte[H\xdboi`K\xd9lkcL\xd7hohM\xd1bvqR\xcfU~{S\xcbM\x81}R\xc7D\x88\x84U\xc2;\x8a\x87R\xbb\'\x8b\x85Q\xb9\x1b\x8d\x87S\xaf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@L\xcc\xccD\x7f\xcc\xa5BQ\x1e\xb8BO\\)B\xfc\x00\x00C\xc0\xcc\xcc\x0e\x8e\x89W\xad\x06\x8c\x85W\xab\x04\x8b\x7fX\xa6\x01\x86}Z\xa6\x04\x85{[\xa4\x02\x80|Z\xa2\x04zw[\x9e\x04rtZ\x9b\x03`gW\x8f\x16ITWz=9=N`^\x1c\x19H+k\x05\x08:\x10r\x01\x060\x07v\x00\x08\x11\x03z\x00\n\n\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf\xa6f@L\xcc\xccD~\xe6?BO\\)BR\x00\x00CH\x00\x00C\xc0\xcc\xcc~\x04\x07\x04\x06\x7f\x00\x08\x08\n\x80\x00\x052\n\x86*\x0b.\x05\x8aU\x16\x06\x04\x8cu2\n\x06\x91\x7fN,\x0b\x8d\x89yG"~\x95\x8dnTi\x97\xa0\x88v7\x99\xaa\xa2\x97\x14\x9e\xad\xb0\xa3\x02\x9d\xaf\xb9\xad\x02\x9f\xaf\xc0\xb7\x02\x9a\xab\xc2\xba\x03\x99\xad\xc4\xbf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@ffhD\xc0\xcc\xa6BP=pBO\\)C@\x00\x00Czff\x02\x95\xac\xc6\xc3\x03\x8a\xa6\xca\xc4\x02o\xa1\xcb\xc4\x03T\x94\xcb\xbf\x04!J\xcd\xbd\x04\x07\x15\xc4\x9a\x05\x00\x05\x9an\x04\x00\x05\r2\x05\x00\x04\x05\x19\x06\x00\x06\n\x0f\x04\x01\x05\x0b\n\x04\x00\t\n\x07\x04\x02\x08\x0b\x08\x06\x02\t\x0b\x08\x05\x00\n\x08\x0e\x05\x03\t\x0b\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf33@ffhD|2\xf4BP=pBO\\)CF\x00\x00C\xc4ff',
            b'\x00\x00\x00\x16|J\x04\x03\t\r\x0e\x05\x01\x08\x0b\r\t\x03\t\r\x12\x0e\x02\n\x0c\x15\x12\x02\x0b\r\x1d\x0f\x03\x0b\x0e!\x07\x02\x0b\x10 \x08\x02\x0b\x10 \r\x04\x18\x11$\n\x03+\x12!\x06*/"&\x07\x0b62"\x08\x0e//$\x07\t0.$\t\x042(\x1d\x07\x05<1#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xce\xc0\x00@ffhD~\xe6\x19BO\\)BO\\)CF\x00\x00Czff\n\x089.)\n\x03>+#\x04\x0481\x1a\x08\x07=/\x14\x06\x06C*\x11\t\x06-0\x12\x06\x06%,\x11\x08\x06"%\r\n\x07\x1d*\r\x07\x05!\x1f\x0e\x07\x06%\'\x16\x08\x062&\x15\x05\x06--\r\n\x05",\r\x08\x06\x1c+\r\n\x05\x18(\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf\xa6f@ffhD\xc0YsBP=pBQ\x1e\xb8B\xfc\x00\x00Czff\x07\x05\x1b&\t\x07\x07\x14%\r\t\x05\x14&\x0b\n\x05\x1e\'\r\x07\x05#(\x0b\x05\x05 +\r\x06\x05\x12$\n\x05\x04\x10&\r\x07\x05\x0f&\x0b\x06\x04\x12$\x11\x06\x04\x14-\n\x05\x04\x12)\x0b\x05\x0c\x12%\x0b\x06\x07\x12$\t\x04\x06\x10 \x0b\x04\x04\x10\x17\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xceL\xcc@ffhD{L\x88BO\\)BO\\)CF\x00\x00C\xc2\x99\x99\x05\x10\x10\x17\t\t\x04\x0b\x15\t\x06\x02\t\x13\x06\r\x02\x0c\x11\t\x11\x04\x13\x11\x06\x12\x03\x0f\x0b\x08\r\x04\x0c\x0e\x06\x05\x03\n\x0c\t\x03\x02\r\x10\n\x08\x04\x13\r\x07\x07\x04\x0f\x08\x06\x07\x02\t\n\x08\x05\x02\x06\n\t\x04\x06\x00\n\x06\x06\x03\x07\x0f\x08\x07\x07\r\x08\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf\xa6f@L\xcc\xccD\xc0Y\x83BP=pBO\\)B\xf8\x00\x00Czff\x08\x0e\x11\x0b\x07\t\x0b\x13\r\t\t\x05\x1b\x1a\x0b$\n\x19\x1a\x086\x03\x0e\x1e\x08/\x04\x1f\r\r\x1f\x03\x19\x11\x0f1\x04\x14\x16\x17h\x05\x17\x18\x15\x81\x04\x1a\x1a\x12\x92\x1d"\x16\x16\x985\x1f\x0c\x14\x9206\x1e\x14\x84\x1f=\x18\x16]4J\x1d\x14?WR-\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@L\xcc\xccD\xc0Y\x85BP=pBO\\)C@\x00\x00C~\x00\x00 \x86P)\x14\x18\x97D\x1a\x16\x15\xa57\x17\x1e\x10\xa55 P\x08\x9a9\x1fo\x06\x8c>\'\x86\x08fC1\x8e\x01FD.\x93\x02"</\x92\x01\x1560\x94\x01\x1290\x8e\x01\x10-,\x7f\x02\n &h\x06\x04\x1a!6\x04\x03\x0f"\x1c\x02\x01\n\x1d$\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf33@L\xcc\xccD|3\x10BO\\)BO\\)C@\x00\x00C\xc4ff\x01\x00\n"\x1f\x06\x00\x001\x11\r\x00\n4\n\x12\x00\x0f6\x08\x15\x00\x145\x10\x14\x00\x1d8\x17\x1b\x00\x13E&\x1b\x02\x19J3\x12\x02\x19M;\r\x00\x0eD>\x06\x00\x0f56\x07\x01\x17!*\x0e\r\x12\x0f\x15\x0e\x10\x0f\x0b\x0e\x0c"\x05\n\x12\x16\x17\x08\r\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf33@L\xcc\xccD\x7f\xcc\xa1BO\\)BO\\)B\xf4\x00\x00Czff\x13\x14\x0b\r\x0f\x14\n\x0e\x10\x17\x14\x06\x0c\x166\x13\x05\r\x11j\x16\r\x0f\x10o\x13\x0e\x13\x14D\x15\x12\x13\x17$\x17\x11\x1d\x17\x11\x12\x15\x1b\x18\x13\x12\x12\x17\x11\x18\x12.\x15\x1a\x1c"\x1f\x15\r %\x10\x15\x11\x1a\x12\x14\x13\x13\x122\x12\x15\x16\x16\x05\x16\x17\x11\x11\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf\xa6f@ffhD\xc0YsBO\\)BQ\x1e\xb8CD\x00\x00Czff',
            b'\x00\x00\x00\x16{Z\x19\x12\x16\x15\x16\x93\x12\x18\x16\x0e\xe2\x12\x1d\x16\x17\xee\x17\x1d\x14\x19\xf2%\x1f$\x19\xf1\x1c3\x10\r\xe5\x16\x1e\n\x05\xad$A\x05\x1aM\x17^\x1e\n"\x08\x93P\x1f\x14&\xb2\x95w\x15\x7f\xc2\xb6\xb1\x17\xdf\xc0\xc5\xe0\x1b\xea\xb1\xcd\xea\x17\xed\x98\xd5\xf2\x1b\xe8\x85\xd4\xf4\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xce\xc0\x00@L\xcc\xccD~\xe6:BP=pBO\\)B\xf8\x00\x00Czff!\xd2b\xcf\xed\x1d\x88A\xc3\xcf\x16(\x18\x94v\x19\x10\x15(("\x0f\x18\x16#\x1e\x12!\x14\x1d!\x18"\x16\x1c&\x1b%\x15\x1d\'\x19 \x1b\x1a*\x1a"\x1b\x19-\x18"\x18\x1b"\x1b$\x1b\x19\x1a"+ \x1a)\x1d%\x1c\x1d+&,!\x1e0$3%!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@L\xcc\xccD~\xe6@BO\\)BO\\)B\xf8\x00\x00C\xc2\x99\x996&B\x1d$4$*\x1d!2\x1e%\x1d.+\x1e+\x1f:+\x1e.!T.$.(W4#//J5*1.:2&05.1*02-1\'42-1&13.1&5942)5=21*8@0*.48/\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xce\xc0\x00@L\xcc\xccD}\xff\xd6BO\\)BO\\)C@\x00\x00C~\x00\x00 455/\x172<30\x175713\x164645\x157A25\x106A.6\x132++=\x15+%#8\x11\x18\x1a*7\x0f\x12\x1a>\x1e\x14\x14!7\x17\x13\x13\x17.\x19\x17\x0e(\'\x19\x19\x0e%$\x1a\x16\x0c\x0e\x1b\x1b\x15\x0e\r\x14\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@L\xcc\xccD\xc0\xcc\xb7BNz\xe1BO\\)B\xf8\x00\x00Czff\x12\r\x14\x15\x1c\x1a\r\x1b\x17\x17\x1d\x11"\x1a\x16\x1f\x17$  \x1a\x11 $$\x17\x11\x1e"\x1f\x1b\x0e\x1c\x1e\x1e\x1a\x1a"\x1e\x1a\x19\x1b"\x1a \x17\x17 \x18$%\x1d!\x15$4\x1b\x1e\x1d";\x1d \x1e#2!!\x1e"\x1e\x1d\x1f%$ \x18\x1d."\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf33?\xe6fhD}\xff\xefBL\xcc\xcdBO\\)B\xf4\x00\x00C\xc0\xcc\xcc"\x1b!5! .&1 \x1eD\x1e\'\x1f\x1dB\x1b\x1f($"\x1a\x1a%!\x1d\x1d\x17&\x1d \x16\x19#!\x1d\x1a\x1b\x1d \x1a#\x1b\x1c#\x17\x1e$\x1e\x1f\x1b"*\x1f!\x1e"2%\x1d\x1e"-+\x1c\x1a%*.\x1a\x1a$/1\x1c\x1d&+0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xce\xc0\x00@ffhD~\xe6\x19BM\x99\x99BO\\)B\xf8\x00\x00Czff\x1d"(&2\x1a\x1f#(1\x1b\x0b%+.\x17\x1a*+,\x1b\x1d--+\x1a\x1b+**\x1b\x1d(&%\x16\x1b"+$\x0e\x1d\x1f-&\r\x1d\x1c,)\x0b\x1c\x1a&*\x08\x1a\x1d\x1e+\n\x1c\x18\x1b4\x11\x1c\x1d\x15>\x1a\x14\x13\x12?(\x0c\x0f\x180\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf\xa6f@\xf334D\xc0X\xd6BP=pBO\\)B\xe8\x00\x00CzffG\r\x16\x17\x1cW\t\x1a\x18\x15l\t\x18\x1a\x12v\x08\x17\x19\x10\x84\t\x17\x17\x11\x88\x06\x1a\x15\x12\x8f\x076\x16\x16\x94\x04\x15\x13\'\x93\n\x11\x15>\x98\x0c\x10\x1f_\x97\x12\x1b+m\x96\x1e+Hz\x95;E]\x7f\x90ZUu\x86\x89jh~\x87\x84{x\x86\x8b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xce\xc0\x00@\xe6ffD}\x18\x7fBR\x00\x00BR\xe1GB\xec\x00\x00C\xc0\xcc\xcc',
            b"\x00\x00\x00\x16zj~\x87\x7f\x8d\x8ef\x8d\x84\x8c\x93T\x97\x89\x91\x97Q\x9b\x8a\x92\x98U\x9f\x85\x94\x9ad\x9c\x82\x94\x9bm\x9a\x82\x95\x9bp\x94v\x97\xa0r\x91q\x96\x9dn\x8a_\x95\xa0n\x7fP\x95\x9fgu@\x95\x9efd4\x9a\x9fbP+\x99\xa0]@5\x97\x99X>C\x98\x9c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf\xa6f@\xd9\x99\x9aD\xc0Y#BS\xc2\x8fBS\xc2\x8fB\xec\x00\x00CzffVBM\x97\x98QKW\x95\x90UQ^\x98\x8eVRb\x99\x89YUg\x95\x82\\[i\x95|_]o\x91sj_n\x8fipbo\x8dfwaq\x8b]zaj\x8aZ\x85ei\x89O\x8chg\x83N\x8dbb\x82M\x90fc\x7fE\x99b`\x7fE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf\xa6f@\xd9\x99\x9aD\xc0Y#BS\xc2\x8fBS\xc2\x8fB\xe8\x00\x00Czff\x9a`]~A\x9e^\\y=\x9f^Y}8\xa5WT}7\xa2WUw2\xa6VSw2\xa9TS}2\xa8SOw.\xaaPK|,\xafLG~.\xadG@\x823\xafG=\x849\xb5I:\x85:\xb2I4\x8a5\xb7M4\x912\xbaV3\x950\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf33@\xd9\x99\x9aD}\xff(BT\xa3\xd7BS\xc2\x8fB\xf0\x00\x00C\xc0\xcc\xcc\xbfa4\x96.\xbdh6\x9e4\xc1pB\x9c7\xc3uF\xa5=\xc8\x81Q\xa3?\xc8\x84U\xa7C\xcc\x8a]\xa7E\xcc\x94b\xa7G\xd0\x9ai\xa8I\xd4\x9do\xaeM\xd1\x9e{\xadT\xd5\xa5\x86\xafb\xd7\xaa\x8d\xb8t\xd5\xae\x96\xb9{\xd7\xb1\x9c\xbe\x8a\xda\xb3\xa3\xc2\x96\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@\xcc\xcc\xceD\xc0\xccvBT\xa3\xd7BS\xc2\x8fB\xe4\x00\x00Czff\xd9\xaf\xa7\xc6\x9b\xd7\xab\xaa\xc6\x9e\xd5\xae\xab\xcb\xa5\xd2\xab\xaf\xcd\xa9\xd0\xad\xb4\xce\xae\xce\xaf\xbe\xcf\xae\xce\xb2\xbf\xd4\xb6\xcd\xb5\xc8\xd5\xb4\xcc\xb6\xcc\xd8\xb8\xcd\xb9\xd0\xdb\xba\xc8\xbd\xd4\xd8\xba\xca\xc1\xd8\xdd\xbb\xce\xc3\xda\xdd\xc6\xcb\xc5\xda\xdb\xbf\xcd\xca\xdc\xdd\xbf\xcd\xcd\xdf\xdd\xbe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf\xa6f@\xcc\xcc\xceD\xc0YBBR\x00\x00BT\xa3\xd7B\xf0\x00\x00Czff\xcb\xca\xdd\xda\xbe\xce\xd0\xdf\xda\xbf\xd2\xd2\xe2\xda\xbf\xd1\xd1\xe1\xd9\xbf\xd0\xd1\xe2\xda\xbf\xd2\xd4\xe1\xd9\xc1\xd2\xd2\xde\xd9\xc6\xd1\xd4\xe0\xd7\xc5\xcc\xd4\xe0\xd7\xc7\xc4\xcf\xda\xd7\xc8\xaf\xcf\xd8\xce\xcc{\xca\xc5\xc2\xcde\xc8\x9d\x82\xd1[\xc6UO\xd0]\xc4/!\xd2`\xbf\x13\x1a\xd4\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf\xa6f@\xcc\xcc\xceD\xc0YBBQ\x1e\xb8BS\xc2\x8fB\xe8\x00\x00CzffR\xb7\x12\x0c\xd8:\x9a\x12\x11\xd4$\x86 \x1f\xcf\x1ekB&\xce(bH;\xc7%TJC\xc4\x1aUJH\xb9\x1bS>H\xb1\x12A*3\x9b\x19,\x14\x12\x8c\x10\x1d\x0b\x07Y\x05.\x0b\x0b&U+@\x04&U\x1b4\x06\x16i\x15*\r5p\x18$!'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x8c\xcc@\xc0\x00\x00D\xc1?\xc3BP=pBR\x00\x00B\xe8\x00\x00Czffk\x0c\x07\x0b\x19U\x08\x18\x0f\x14:83\x15\x1b\x1fU3\x14((j9,3gm=Z*}fEmF\x8aQM\x88W\x8aE]\x942f\x0ed\x9f(#\x1ef\xa62 ]m\xa7b\x04vk\xaa\x8a\x07~o\xa7\x98\x05\x7fo\xa6\xa5\nQb\xa4\xa6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf33@ffhD~\xe6\x1cBO\\)BS\xc2\x8fB\xf0\x00\x00C~\x00\x00",
            b'\x00\x00\x00\x16yz\x0c `\x8d\x9d\x15!Vg\x8c\x10\x04F\x14\x1a#\x05\x1a\x00\x004\x05\x15\x05\r9\x06&\r\x01B\t.\x05\x04F\x134\x12\x07N\x10:\x1a\x14P\x16=\x15"V-?#4Y7?+=_A:"EdD8$OdK5(ScK1\x19W\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xce\xc0\x00@\xc0\x00\x00D~\xe5\xedBO\\)BR\x00\x00B\xe4\x00\x00CzffdR)\x16YcR2\x15]ZR:\x0ebMV3\x08f"X3\x16e\x05W1>i\x01X4Jj\x02^2Rj\x02V,Rk\x02U!Lc\x02L\x115W\x04"\x03\x10/\x03\x03\x06\x15\x12\x02\x00\x04\x19\x05\x02\x05\n\r\x05\x0c\x04\x05\x04\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@ffhD~\xe6#BO\\)BR\x00\x00B\xec\x00\x00C\xc2\x99\x99\x15\x00\x05\x05\x02%\x00\n\x03\x040\x00\n\x02\x06=\x06\x10\x05\x05C\x00\x0c\x07\x02N\x00\t\x07\x06V\x00\x0e\x07\x04\\\x08\x05\x07\x0e^\x17\x07\x0b\x1fb \x02\x06,i/\x06\x08<i1\x00\x10Gf:\x1b\x1eOiB\x15+VkA!7`gG+;b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@ffhD\xc0\xcc\xa6BO\\)BO\\)B\xec\x00\x00CzffiP7AfhR:HlmW?Jjk\\AOkjbIPgjaIRhmhNSiqjOWjrmRWkumTXluoYZjtr[Zjvt\\YhvuaZnzt]Xqws^Vs\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@ffhD~\xe6#BQ\x1e\xb8BQ\x1e\xb8B\xdc\x00\x00C\xc2\x99\x99vq`Xtwn_Wvum^WzsnbY\x81pmbZ\x83li\\Z\x87jgZ\\\x8ajg^`\x8abb][\x8ead^]\x8dahc]\x90^fb^\x91bhb]\x8ebjb]\x8a`la^\x8a]jb_\x89\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@ffhD\x7f\xcc\x87BS\xc2\x8fBS\xc2\x8fB\xf0\x00\x00C\xc0\xcc\xcc^ne`\x86^neb\x83\\ne^\x81^pf]~^ncc\x80`rfe|cqde|andd|_ldd~^lbj{^mak~Xg^e|Wedk~PdZp\x83IbWm\x81>]`r{\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@\xc0\x00\x00D\xc0\xcc\x90BS\xc2\x8fBT\xa3\xd7B\xe0\x00\x00Czff3^Vt\x7f(VYv\x84&WYz\x8a"UY~\x87\x18RW\x84\x82\x10TZ\x82\x81\x07UZ\x87~\tRZ\x88\x81\x10R[\x89}\x14S\\\x8c\x7f"QZ\x8e}7OX\x8cwXHZ\x8c{uIY\x8dw\x8dBV\x8bu\xa2=V\x89u\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf\xa6f@ffhD}\xff\xbdBR\x00\x00BX\x14{B\xe8\x00\x00C\xc2\x99\x99\xbc5T\x88y\xc9.R\x85t\xd0(P\x84x\xd7&R\x83{\xdb!M\x80~\xde\x16P\x7fy\xe1\x0bR\x84~\xe4\x05V\x87\x82\xe4\x12W\x89\x86\xe6\x19{\x8b\x8b\xe04\x8e\x92\x95\xe4o\xa6\x94\x97\xe4\x92\xb3\x9e\xa2\xe2\xbc\xc4\xa1\xa7\xde\xca\xca\xa8\xaa\xd7\xd5\xd3\xaf\xb0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xce\xc0\x00@ffhD}\x19SBR\x00\x00BVffB\xe8\x00\x00C\xc0\xcc\xcc',
            b'\x00\x00\x00\x16x\x8a\xcd\xd9\xda\xb5\xb4\xbc\xdc\xde\xb9\xb2\x90\xe1\xe3\xbd\xb6n\xe5\xeb\xbf\xb9U\xe7\xe7\xc0\xb6J\xe7\xe6\xc0\xb4=\xea\xeb\xc4\xaf=\xe8\xe7\xbf\xb2:\xe7\xe8\xbe\xb07\xe9\xe8\xbe\xae5\xe4\xe2\xbd\xab5\xe2\xdb\xb8\xa75\xd0\xba\xb2\xa60\xb2o\xad\xa5+vB\xa4\xa2$b3\x95\xa1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x8c\xccAl\xcc\xcdD\xc1=EBP=pBT\xa3\xd7B\xe0\x00\x00Czff&J\x1a\x85\x9d\x1d>\x0bV\x9c\x1f7\x1a4\x9a\x151\x17\x0f\x95\x0f1\x1e\x0b\x8e\x10,!\x11\x8a\x10)"\r\x81\x1a\x12$\x11z%\x1d(\x0ek/$7\x18_0\x187\x13N1\x17\'\x16@*\x15\x1a!&%\x0b\x14$ \x15\x0e\x16 \x15\x0c\x10\x1a\r\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf33A\xdc\xcc\xcdD}\x0b\xe7BQ\x1e\xb8BR\xe1GB\xf4\x00\x00C\xc2\x99\x99\x12*\x1d\x1fp\x1a2\x1f\x17\x1a\x171*\x17*\x1d+$\x1e-\x1f$3!*\x13\x1b6\x15$\x17\r$\x15"\x18\x1a\x1e\x16%\x16\x13\x1c\x1b%\x0f\x1a\x1f\x17*\x13\x1c"+,\x17\x16!\x15.\x1c\x16\x1f\x18+#\x12 \x19(\x1a\x0e\x1c\x18->\r\x1a\x17-\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xcf\xa6fA\xd333D\xc0S9BP=pBR\x00\x00B\xe4\x00\x00CzffZ\x10 \x15*}\x14\x1a\x15$\x92\x10\x1a\x16\x1f\xa8>\x1a\x12-\xac\x1f\x17\x0f*\xb7#"\x160\xb85\x1f#<\xb3Z\x1d&B\xabn"84\xa0\x92#>/\x8e\xa5\x1fJ,p\xba\x1eT6\xba\xc2#glI\xc45v\x92e\xbeF\x86\xb8k\xb2K\x8f\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99A\xc6fgD\xc0\xc8<BO\\)BR\x00\x00B\xf4\x00\x00Czffz\x90S\x94\xc7\x7fjS\x96\xc6\x8cbW\x92\xc6\x91P^\x8a\xc3\x97cg\x85\xb8\x99mry\xac\x99r{r\xa1\x9aw\x83n\x9a\x9cz\x90m\x8f\x9c{\x95j|\x99\x81\x9eit\x95|\xa4ff\x92|\xaaiY\x90\x82\xb1cV\x8f\x83\xb4bZ\x8b\x85\xb8c_\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99A\xc0\x00\x00D~\xdf\xe2BS\xc2\x8fBS\xc2\x8fB\xf0\x00\x00C\xc2\x99\x99\x89\x84\xc0`_\x86\x87\xbfZe\x86\x8b\xc5Xg\x84\x8d\xc9Qi\x82\x8e\xccOj\x82\x92\xcfMj\x84\x95\xcdMm\x83\x95\xccNo\x83\x97\xccSp\x81\x9a\xc9[p\x83\x9d\xc8_o\x85\x9c\xc6ho\x81\x9d\xbenn\x80\x9a\xbapn|\x96\xb5to{\x94\xaduu\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99As33D\x7f\xc79BR\x00\x00BS\xc2\x8fB\xec\x00\x00C\xc0\xcc\xccv\x8d\xa8vto\x8f\x98zwm\x88\x85~zi\x84{{va|f~y\\{^~yVtM}yTsI\x81{SrE\x84}LpE\x85~LrH\x86~JrH\x87{IrI\x8a|KuH\x89}JtK\x8dwJsH\x8aw\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\x00\x00Al\xcc\xcdD\xc0\xcaPBO\\)BR\x00\x00B\xf8\x00\x00C\xc0\xcc\xccFtK\x89vHwI\x86sHyE\x8arGvD\x84pEu>\x82nEr/\x7foDv+~j?v$|l=r!|n=q%yl:n\x1ewl5j/vl/f\x1axn)aZvo\x1d]7to\x18WDwm\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99AY\x99\x9aD\x7f\xc9mBP=pBR\x00\x00B\xe4\x00\x00C\xc0\xcc\xcc',
            b'\x00\x00\x00\x16w\x9a\x12R@rk\x0bM;si\x08B<nh\n97eb\n.7]^\x11"8QW\x16\x199JR\x19\x12<=F\r\n?5@\n\x05G+1\x11\nK%%\x1a\x08J\x19\x11"\x02?\x1a\x038\n5\x1e\t.\n\x1f\x15\x08\x12\x0f\x18\xf4\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99AY\x99\x9aD~\xe35BO\\)BO\\)B\xf4\x00\x00C\xc2\x99\x99\x0e\x12\x1e,\x0e\x12\x14\x0b\x11\x0b\x0f\x02\x19\x15\x13\x12=6@"x<*\'\x1d\x11\x08\x1c\x0f\x15\x0c\x14%\t\x0e\x13\x15%\x1a\x0e\x12\r\x10\n\x19\x0f\r\x16\x10\x1a\x0f\x01\x12\x19\x0f\x0f\r\x12\x1e\x12\x19\x0b\x1a\x1e\x15\x1d\x0e \x1f\x18\x1d\n\x1f\r\x08\x1a\r"\x0e\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99AFfgD~\xe4nBM\x99\x99BO\\)B\xf8\x00\x00C\xc2\x99\x99\x1b\r!\x1b\x11\x1d\x12\x1f\x1d\n\x1a\x1fC\x15\x11\x0f\x1b`\x080\x03\x1c{\x04o\x04\x1cb\x02\x8b\x12\x1b\x06\x02\x91"\x15\x06\x18\x9b4\x00\x04A\x99=\x05\nY\x9cD\x0e\r`\x97J\x1f\x16f\x95O28e\x8eZ;J^\x7fd@QUjnHV/C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1s3A@\x00\x00D\xc1?#BNz\xe1BO\\)B\xe8\x00\x00C\xc0\xcc\xccqL_\x1c8zU`\x1a4z[g\x18*\x7f\\j"6wfl1Htps8Kpms>Jbmv=IYnu<GHjy>G8izA>\x1cgr?@\x0f_m68\x02Xd17\x06NT(3\x0c@6%.\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99A@\x00\x00D}\xfexBO\\)BR\xe1GB\xf8\x00\x00C\xc4ff\x11"\x1a%0\x0f\x16"(*\x10\x12\x0f\x1a"\x15\x00\x0e\x04 \x1d\x08\x13\x01\x19\x1e\r\x0f\n\x18$\r\x12\n\x1a.\x0c\r""E\x0f\x13-#O\x11\x1552Z\x16\x1e87b\x1d%?Fl!1DOq(7K\\r5Awdp@FYz\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@\xf334D~\xe5\x15BO\\)BS\xc2\x8fB\xec\x00\x00C\xc2\x99\x99nJUi\x7fmTWh\x84k]^m~d_fn\x83^biw\x84Wjmv{WkpuoQjovoJmmqfFnnre>mkhh7gebe2g`Zf+fXY^\'dSRZ%ZKM[\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd1\x00\x00@\xf334D\xc0X\xf1BP=pBU\x85\x1eB\xf4\x00\x00C\xc2\x99\x99\x1e[EEZ\x1aU;D\\\x1bM8>Z\x18G19W\x11A-7X\r7+2V-4,2S\r/(2T\x10-).U\x16+*\'P\x1b%(*Q\x1b#,\'J\x1e".%J"\x1d/%I&\x1b3 D-\x1a3\x1bB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@\xf334D}\xfe\xc3BP=pBW33B\xfc\x00\x00C\xc4ff2\x165\x1dA6\x1a4\x1a<=\x199\x1a:A\x17>\x1b6H\x15=\x186O\nD 4T\x08H\x1f3]\x00K!2a\x00M"2f\x0fN&2j\x17O&3m\x19T*5m\x1dU\'5p!U*:n\'U.;n0Z1?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\xd0\x19\x99@\xe6ffD~\xe5[BO\\)BU\x85\x1eB\xf0\x00\x00C\xc2\x99\x99',
            # File trailer
            b'\x81\x00HDT   .001                          1024                ',
        ]

    def _consRecord(self):
        # Mnem/value/uom where value is bytes/float/int
        myData = [
            # Basic
            (b'CN  ', b'Company name',                      None),
            (b'FN  ', b'Field name',                      None),
            (b'COUN', b'Rig name',                      None),
            (b'WN  ', b'Well name',                      None),
            (b'NATI', b'Nation',                      None),
    #            (b'STAT', b'State',                      None),
            # Three field location records
            (b'FL  ', b'Field location one',                      None),
            (b'FL1 ', b'Field location two',                      None),
            (b'FL2 ', b'Field location three',                      None),
            # Dynamic header
            (b'HIDE', b'High Resolution Dipmeter', None),
            (b'HID1', b'Log Title ONE',                      None),
            (b'HID2', b'Log Title TWO',                      None),
            # Deviation and Lat/Long
            (b'MHD ', 8.7,   b'DEG '),
            (b'LATI', b'52 31\' 47.369"N',   None),
            (b'LONG', b'2 12\' 12.196"W',   None),
            # Fine column of 24 rows
            (b'DATE', b'2012-01-05', None),
            (b'RUN ', b'Run number',                      None),
            (b'TDD ', 12521.0,   b'FEET'),
            (b'TDL ', 12518.5,   b'FEET'),
            (b'BLI ', 12511.0,   b'FEET'),
            (b'TLI ', 11192.5,   b'FEET'),
            (b'CSIZ', 8.0,      b'IN  '),
            (b'CD  ', 11190.5,  b'FEET'),
            (b'CBLO', 11192.5,  b'FEET'),
            (b'BS  ', 6.5,      b'IN  '),
            (b'DFT ', b'KCL Polymer Glycol PHPA',      None),
            
            
            (b'MSS ', b'Flowline',      None),
            # Mud stuff
            (b'RMS ', 0.196,    b'OHMM'),
            (b'RMFS', 0.0797,   b'OHMM'),
            (b'RMCS', 0.266,    b'OHMM'),
            (b'MST ', 16.0,     b'DEGC'),
            (b'MFST', 16.0,     b'DEGC'),
            (b'MCST', 16.0,     b'DEGC'),
            (b'RMB ', 0.0368,   b'OHMM'),
            (b'RMFB', 0.0329,   b'OHMM'),
            (b'MRT ', 183.6,    b'DEGC'),
            (b'TCS ', b'22:35 2012-01-04',    None),
            (b'TLAB', b'09:50 2012-01-05',    None),
            
            # Datums
            (b'PDAT', b'Permanent datum', None),
            (b'EKB ', 21.0,   b'FT  '),
            (b'EDF ', 20.0,   b'FT  '),
            (b'EGL ', 3.0,   b'FT  '),
            (b'LMF ', b'DF  ', None),
            (b'APD ', 17.0, b'FT  '),
            (b'DMF ', b'DF  ', None),
            
            # Location etc
            (b'ENGI', b'Paul Ross', None),
            (b'WITN', b'Son of Godzilla', None),
            (b'LUL ', b'Logging unit location', None),
            # Other services
            (b'OS1 ', b'ABC-DEF-GHI', None),
            (b'OS2 ', b'JKL-MNO', None),
            (b'OS3 ', b'PQR-STU', None),
            (b'OS4 ', b'VW', None),
            (b'OS5 ', b'XYZ', None),
            (b'OS6 ', b'123-456-7890', None),
        ]
        return TestLogHeader._hdrTrippleToLogicalRecord(myData)

    def test_01(self):
        myFile = self._retFileFromListOfLogicalRecords(self._logicalRecords(), theId='MyFile', flagKg=False)
        # Create a file index
        myFileIndex = FileIndexer.FileIndex(myFile)
        for anIlp in myFileIndex.genLogPasses():
            myTimerS = ExecTimer.TimerList()
            fp = TestPlotShared.outPath(TEST_SVG_FILE_MAP_LIS[22].fileName)
            myPlot = Plot.PlotReadXML('HDT', theScale=40)
            myPlot.plotLogPassLIS(
                myFile,
                anIlp.logPass,
                anIlp.logPass.xAxisFirstEngVal,
                anIlp.logPass.xAxisLastEngVal,
                'HDT',
                fp,
                frameStep=1,
                title=TEST_SVG_FILE_MAP_LIS[22].description,
                lrCONS=[self._consRecord(),],
                timerS=myTimerS)
            sys.stderr.write(str(myTimerS))
            sys.stderr.write('\n')
            sys.stderr.flush()
            break


@pytest.mark.slow
class TestPlotReadLIS_SingleSinCurve_API(TestPlotReadLIS_SingleSinCurve):
    """Tests plotting a LIS file."""

    def setUp(self):
        """Set up."""
        myByFilm = self.retFilmBytes()
        myByPres = self.retPresBytes_TEST()
        self._prl = Plot.PlotReadLIS(
            LogiRec.LrTableRead(self._retFileSinglePr(myByFilm)),
            LogiRec.LrTableRead(self._retFileSinglePr(myByPres)),
        )
        self._lisFile, self._lisFileIndex = self.retFileAndFileIndex_ShortTEST()

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPlotReadLIS_SingleSinCurve_API.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """{:s}""".format(TEST_SVG_FILE_MAP_LIS[30].description)
        for anIlp in self._lisFileIndex.genLogPasses():
#            myFout = io.StringIO()
#            myXStart = EngVal.EngVal(9900.0, b'FEET')
#            myXStop = EngVal.EngVal(9600.0, b'FEET')
            myXStart = EngVal.EngVal(1000.0, b'FEET')
            myXStop = EngVal.EngVal(900.0, b'FEET')
            myTimerS = ExecTimer.TimerList()
            self._prl.plotLogPassLIS(
                self._lisFile,
                anIlp.logPass,
                myXStart,
                myXStop,
                Mnem.Mnem(b'2   '),
                TestPlotShared.outPath(TEST_SVG_FILE_MAP_LIS[30].fileName),
                frameStep=1,
                title=TEST_SVG_FILE_MAP_LIS[1].description,
                lrCONS=[TestLogHeader.headerLogicalRecordLIS(),],
                timerS=myTimerS)
            sys.stderr.write(str(myTimerS))
            sys.stderr.write('\n')
            sys.stderr.flush()


@pytest.mark.slow
class TestPlotReadLAS_XML_LgFormat(TestPlotBase_00):
    """Tests plotting of 200' of curves from "Triple_Combo" LgFormat XML file from LAS."""

    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass
    
    def test_00(self):
        """TestPlotReadLAS_XML_LgFormat.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def _plotLAS(self, theLasFile, fIdxMap, plotHeader):
        """TestPlotReadLAS_XML_LgFormat.test_00(): Plot from XML LgFormat files - down log, no header."""
        myTimerS = ExecTimer.TimerList()
        for lgFormat in fIdxMap:
            fp = TestPlotShared.outPath(TEST_SVG_FILE_MAP_LAS[fIdxMap[lgFormat]].fileName)
            myPlot = Plot.PlotReadXML(lgFormat)
            myPlot.plotLogPassLAS(
                theLasFile,
                theLasFile.xAxisStart,
                theLasFile.xAxisStop,
                lgFormat,
                fp,
                frameStep=1,
                title=TEST_SVG_FILE_MAP_LAS[fIdxMap[lgFormat]].description,
                plotHeader=plotHeader,
                timerS=myTimerS)
        sys.stderr.write(str(myTimerS))
        sys.stderr.write('\n')
        sys.stderr.flush()

    def test_01(self):
        """TestPlotReadLAS_XML_LgFormat.test_00(): Plot from XML LgFormat files - down log, no header."""
        self._plotLAS(
            LASRead.LASRead(io.StringIO(TestPlotLASData.LAS_00_200_FEET_DOWN)),
            {
                'Triple_Combo'                      : 40,
                'Resistivity_3Track_Logrithmic.xml' : 41,
            },
            False,
        )            

    def test_02(self):
        """TestPlotReadLAS_XML_LgFormat.test_00(): Plot from XML LgFormat files - down log, with header."""
        self._plotLAS(
            LASRead.LASRead(io.StringIO(TestPlotLASData.LAS_00_200_FEET_DOWN)),
            {
                'Triple_Combo'                      : 42,
                'Resistivity_3Track_Logrithmic.xml' : 43,
            },
            True,
        )            

    def test_03(self):
        """TestPlotReadLAS_XML_LgFormat.test_03(): Plot from XML LgFormat files - up log, no header."""
        self._plotLAS(
            LASRead.LASRead(io.StringIO(TestPlotLASData.LAS_01_200_FEET_UP)),
            {
                'Triple_Combo'                      : 44,
                'Resistivity_3Track_Logrithmic.xml' : 45,
            },
            False,
        )            

    def test_04(self):
        """TestPlotReadLAS_XML_LgFormat.test_04(): Plot from XML LgFormat files - up log, with header."""
        self._plotLAS(
            LASRead.LASRead(io.StringIO(TestPlotLASData.LAS_01_200_FEET_UP)),
            {
                'Triple_Combo'                      : 46,
                'Resistivity_3Track_Logrithmic.xml' : 47,
            },
            True,
        )            


    def test_10(self):
        """TestPlotReadLAS_XML_LgFormat.test_10(): Plot from XML LgFormat files - large down log, with header."""
        self._plotLAS(
            LASRead.LASRead(io.StringIO(TestPlotLASData.LAS_02_1000FT_DOWN)),
            {
                'Triple_Combo'                      : 48,
                'Resistivity_3Track_Logrithmic.xml' : 49,
            },
            True,
        )            

    def test_11(self):
        """TestPlotReadLAS_XML_LgFormat.test_11(): Plot from XML LgFormat files - multiple gamma ray curves."""
        self._plotLAS(
            LASRead.LASRead(io.StringIO(TestPlotLASData.LAS_03_MULTI_GR)),
            {
                'Triple_Combo'                      : 50,
                'Resistivity_3Track_Logrithmic.xml' : 51,
            },
            True,
        )            

    def test_12(self):
        """TestPlotReadLAS_XML_LgFormat.test_12(): Plot from XML LgFormat files - density, porosity and multiple gamma ray curves."""
        self._plotLAS(
            LASRead.LASRead(io.StringIO(TestPlotLASData.LAS_03_DENS_PORO_MULTI_GR)),
            {
                'Porosity_GR_3Track'                 : 52,
            },
            True,
        )            

class SpecialUnused(unittest.TestCase):
    """Special tests."""
    pass

    def test_10(self):
        """SpecialUnused.test_10(): Extract outputs from XML."""
        myFc = FILMCfgXML.FilmCfgXMLRead()
        print()
        print(myFc.longStr())
        # Map of {Mnem : set{UniqueId, ...}, ...}
        myMnemUniqueIDMap = {}
        for uid in sorted(myFc.uniqueIdS()):
            # Create a PRESCfgXML
            print(' {:s} START '.format(uid).center(75, '='))
            myPc = PRESCfgXML.PresCfgXMLRead(myFc, uid)
#            pprint.pprint(myPc._destOutpToCurveIdMap)
#            print(myPc._destOutpToCurveIdMap.items())
            for uid in myPc._destOutpToCurveIdMap:
                for m, uS in myPc._destOutpToCurveIdMap[uid].items():
                    for u in uS:
                        try:
                            myMnemUniqueIDMap[m].add(u)
                        except KeyError:
                            myMnemUniqueIDMap[m] = set([u,])
#            print(myPc.outpChIDs(uid))
            print(' {:s} END '.format(uid).center(75, '='))
#        pprint.pprint(myMnemUniqueIDMap)
        print(' OUTP : UniqueId(s) START '.center(75, '='))
        for k in sorted(myMnemUniqueIDMap.keys()):
            theID = '"{!r:s}"'.format(k.pStr(strip=True))
            print('{:12s} : {!r:s},'.format(theID, [v.pStr(strip=True) for v in myMnemUniqueIDMap[k]]))
        print(' OUTP : UniqueId(s) END '.center(75, '='))



class TestWriteTestSVGIndex(unittest.TestCase):

    def test_00(self):
        writeTestSVGIndex()

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotRollStatic))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotRoll))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotLowLevelCurvePlotScale))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotLowLevelCurvePlotScaleXML))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotLowLevel_wrap))
    # This is Plot testing that may write SVG files to disc
    # First write index.html
    writeTestSVGIndex()
    # API Headers are included in this test
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogHeader.TestLogHeaderLIS))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogHeader.TestLogHeaderLAS))
    # LIS plots
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotBase_00))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotReadLIS_SingleSinCurve))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotReadLIS_SingleSquareCurveLowFreq))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotReadLIS_SingleSquareCurveHighFreq))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotReadLIS_HDT))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotReadLIS_HDT_20))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotReadLIS_HDT_40))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotReadLIS_SuperSampled))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotReadLIS_COLO_Named))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotReadLIS_COLO_Numbered))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotReadLIS_COLO_Numbered_Comp))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotReadLIS_Perf_00))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotReadLIS_XML_LgFormat))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotReadLIS_HDT_Example))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotReadLIS_SingleSinCurve_API))
    # LAS plots
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotReadLAS_XML_LgFormat))

#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(SpecialUnused))
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
    logLevel = logging.ERROR
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
