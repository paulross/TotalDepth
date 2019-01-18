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
"""Tests ...

Created on Dec 14, 2011

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

import sys
import os
import logging
import time
import unittest
#import pprint
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

from TotalDepth.LIS.core import Mnem
from TotalDepth.util.plot import FILMCfg
from TotalDepth.util.plot import FILMCfgXML
from TotalDepth.util.plot import Coord

XML_CONTENT_MAP = {}
__d = os.path.join(os.path.dirname(__file__), 'formats')
for __fp in os.listdir(__d):
    with open(os.path.join(__d, __fp)) as f:
        XML_CONTENT_MAP[__fp] = f.read()

class TestPhysFilmCfgXMLRead(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """TestPhysFilmCfgXMLRead.test_00(): Test setUp() and tearDown()"""
        pass
    
    def test_01(self):
        """TestPhysFilmCfgXMLRead.test_01(): Test reading a single track."""
        root = etree.fromstring("""<LgFormat UniqueId="TestOneTrack" xmlns="x-schema:LgSchema2.xml">
    <LgVerticalScale UniqueId="VerticalScale">
        <IndexScaler>100</IndexScaler>
        <IndexUnit>Ft</IndexUnit>
        <PaperScaler>5</PaperScaler>
        <PaperUnit>LG_PAPER_INCH</PaperUnit>
    </LgVerticalScale>
    <LgTrack UniqueId="track1">
        <Description>Track 1</Description>
        <RightPosition>2.4</RightPosition>
        <LgLinearGrid UniqueId="minorGrid1">
            <Color>818181</Color>
            <LineCount>11</LineCount>
        </LgLinearGrid>
        <LgLinearGrid UniqueId="majorGrid11">
            <Color>818181</Color>
            <LineCount>3</LineCount>
            <Thickness>2</Thickness>
        </LgLinearGrid>
        <LgCurve UniqueId="BS_7">
            <ChannelName>BS</ChannelName>
            <LeftLimit>6</LeftLimit>
            <RightLimit>16</RightLimit>
            <LineStyle>LG_LONG_DASH_LINE</LineStyle>
            <Thickness>2</Thickness>
            <WrapCount>0</WrapCount>
        </LgCurve>
        <LgCurve UniqueId="CALI_8">
            <ChannelName>CALI</ChannelName>
            <Color>FF0000</Color>
            <LeftLimit>6</LeftLimit>
            <RightLimit>16</RightLimit>
            <LineStyle>LG_DASH_LINE</LineStyle>
            <Thickness>1.6</Thickness>
            <WrapCount>1</WrapCount>
        </LgCurve>
        <LgCurve UniqueId="SP_10">
            <ChannelName>SP</ChannelName>
            <Color>0000FF</Color>
            <LeftLimit>-160</LeftLimit>
            <RightLimit>40</RightLimit>
            <Thickness>1.75</Thickness>
        </LgCurve>
        <LgCurve UniqueId="GR_9">
            <ChannelName>GR</ChannelName>
            <Color>008000</Color>
            <RightLimit>150</RightLimit>
            <Thickness>1.75</Thickness>
        </LgCurve>
    </LgTrack>
</LgFormat>""")
        myFcxr = FILMCfgXML.PhysFilmCfgXMLRead(root)
        self.assertEqual(1, len(myFcxr))
        self.assertEqual('TestOneTrack', myFcxr.name)
        self.assertEqual(100, myFcxr.xScale)
        self.assertEqual(
            (Coord.Dim(value=0.0, units='in'), Coord.Dim(value=2.4, units='in'), 0, 2),
            myFcxr.interpretTrac('track1')
        )
#        self.assertEqual(
#            (Coord.Dim(value=1.2, units='in'), Coord.Dim(value=2.4, units='in'), 1, 1),
#            myFcxr.interpretTrac(b'RHT1')
#        )
        self.assertRaises(FILMCfg.ExceptionFILMCfg, myFcxr.interpretTrac, b'T2  ')
        # Get the track object
#        print(myFcxr[0])
        self.assertEqual(Coord.Dim(value=0.0, units='in'), myFcxr[0].left)
        self.assertEqual(Coord.Dim(value=2.4, units='in'), myFcxr[0].right)

    def test_02(self):
        """TestPhysFilmCfgXMLRead.test_02(): Test reading a single track, log scale OK."""
        root = etree.fromstring("""<LgFormat UniqueId="TestOneTrack" xmlns="x-schema:LgSchema2.xml">
    <LgVerticalScale UniqueId="VerticalScale">
        <IndexScaler>100</IndexScaler>
        <IndexUnit>Ft</IndexUnit>
        <PaperScaler>5</PaperScaler>
        <PaperUnit>LG_PAPER_INCH</PaperUnit>
    </LgVerticalScale>
    <LgTrack UniqueId="track23">
        <Description>Track 23</Description>
        <LeftPosition>3.2</LeftPosition>
        <RightPosition>8</RightPosition>
        <LgLogarithmicGrid UniqueId="logGrid3">
            <Color>818181</Color>
            <Decade>4</Decade>
            <LogScale>LG_LOG_2</LogScale>
        </LgLogarithmicGrid>
        <LgCurve UniqueId="ATR">
            <ChannelName>ATR</ChannelName>
            <Color>FF0000</Color>
            <LeftLimit>0.2</LeftLimit>
            <RightLimit>2000</RightLimit>
            <LineStyle>LG_DASH_LINE</LineStyle>
            <Thickness>2</Thickness>
            <Transform>LG_LOGARITHMIC</Transform>
            <WrapCount>0</WrapCount>
        </LgCurve>
    </LgTrack>
</LgFormat>""")
        myFcxr = FILMCfgXML.PhysFilmCfgXMLRead(root)
        self.assertEqual(1, len(myFcxr))
        self.assertEqual('TestOneTrack', myFcxr.name)
        self.assertEqual(100, myFcxr.xScale)
        # This does nto work as interpret track needs track 2 and three to interpret T23
#        self.assertEqual(
#            (Coord.Dim(value=0.0, units='in'), Coord.Dim(value=2.4, units='in'), 0, 2),
#            myFcxr.interpretTrac(b'T23 ')
#        )
        self.assertRaises(FILMCfg.ExceptionFILMCfg, myFcxr.interpretTrac, b'T2  ')
        # Get the track object
#        print(myFcxr[0])
        self.assertEqual(Coord.Dim(value=3.2, units='in'), myFcxr[0].left)
        self.assertEqual(Coord.Dim(value=8.0, units='in'), myFcxr[0].right)
        self.assertTrue(myFcxr[0].plotXLines)
        self.assertFalse(myFcxr[0].plotXAlpha)
        
    def test_03(self):
        """TestPhysFilmCfgXMLRead.test_03(): Test reading a single track, bad log scale fails."""
        root = etree.fromstring("""<LgFormat UniqueId="TestOneTrack" xmlns="x-schema:LgSchema2.xml">
    <LgVerticalScale UniqueId="VerticalScale">
        <IndexScaler>100</IndexScaler>
        <IndexUnit>Ft</IndexUnit>
        <PaperScaler>5</PaperScaler>
        <PaperUnit>LG_PAPER_INCH</PaperUnit>
    </LgVerticalScale>
    <LgTrack UniqueId="track23">
        <Description>Track 23</Description>
        <LeftPosition>3.2</LeftPosition>
        <RightPosition>8</RightPosition>
        <LgLogarithmicGrid UniqueId="logGrid3">
            <Color>818181</Color>
            <Decade>4</Decade>
            <LogScale>LG_LOG_4</LogScale>
        </LgLogarithmicGrid>
        <LgCurve UniqueId="ATR">
            <ChannelName>ATR</ChannelName>
            <Color>FF0000</Color>
            <LeftLimit>0.2</LeftLimit>
            <RightLimit>2000</RightLimit>
            <LineStyle>LG_DASH_LINE</LineStyle>
            <Thickness>2</Thickness>
            <Transform>LG_LOGARITHMIC</Transform>
            <WrapCount>0</WrapCount>
        </LgCurve>
    </LgTrack>
</LgFormat>""")
        try:
            FILMCfgXML.PhysFilmCfgXMLRead(root)
            self.fail('FILMCfgXML.ExceptionFILMCfgXMLRead not raised')
        except FILMCfgXML.ExceptionFILMCfgXMLRead:
            pass
        
    def test_04(self):
        """TestPhysFilmCfgXMLRead.test_04(): Test reading a single depth track."""
        root = etree.fromstring("""<LgFormat UniqueId="TestOneTrack" xmlns="x-schema:LgSchema2.xml">
    <LgVerticalScale UniqueId="VerticalScale">
        <IndexScaler>100</IndexScaler>
        <IndexUnit>Ft</IndexUnit>
        <PaperScaler>5</PaperScaler>
        <PaperUnit>LG_PAPER_INCH</PaperUnit>
    </LgVerticalScale>
    <LgTrack UniqueId="depthTrack">
        <Description>Depth Track</Description>
        <IndexLinesVisible>0</IndexLinesVisible>
        <IndexNumbersVisible>1</IndexNumbersVisible>
        <LeftPosition>2.4</LeftPosition>
        <RightPosition>3.2</RightPosition>
        <LgCurve UniqueId="DensityStandoff">
            <ChannelName>DSOZ</ChannelName>
            <Color>FF00FF</Color>
            <LeftLimit>2.5</LeftLimit>
            <RightLimit>0</RightLimit>
            <Thickness>2</Thickness>
        </LgCurve>
        <LgCurve UniqueId="ResistivityStandoff">
            <ChannelName>RSOZ</ChannelName>
            <Color>00FF00</Color>
            <LeftLimit>2.5</LeftLimit>
            <LineStyle>LG_DASH_LINE</LineStyle>
            <RightLimit>0</RightLimit>
            <Thickness>1.5</Thickness>
        </LgCurve>
    </LgTrack>
</LgFormat>""")
        myFcxr = FILMCfgXML.PhysFilmCfgXMLRead(root)
        self.assertEqual(1, len(myFcxr))
        self.assertEqual(Coord.Dim(value=2.4, units='in'), myFcxr[0].left)
        self.assertEqual(Coord.Dim(value=3.2, units='in'), myFcxr[0].right)
        self.assertFalse(myFcxr[0].plotXLines)
        self.assertTrue(myFcxr[0].plotXAlpha)
        
    def test_05(self):
        """TestPhysFilmCfgXMLRead.test_05(): Test reading track1 with no x Axis lines/alpha absent in XML."""
        root = etree.fromstring("""<LgFormat UniqueId="TestOneTrack" xmlns="x-schema:LgSchema2.xml">
    <LgVerticalScale UniqueId="VerticalScale">
        <IndexScaler>100</IndexScaler>
        <IndexUnit>Ft</IndexUnit>
        <PaperScaler>5</PaperScaler>
        <PaperUnit>LG_PAPER_INCH</PaperUnit>
    </LgVerticalScale>
    <LgTrack UniqueId="Track1">
        <Description>Depth Track</Description>
        <!-- <IndexLinesVisible>0</IndexLinesVisible>
        <IndexNumbersVisible>1</IndexNumbersVisible> -->
        <RightPosition>2.4</RightPosition>
    </LgTrack>
</LgFormat>""")
        myFcxr = FILMCfgXML.PhysFilmCfgXMLRead(root)
        self.assertEqual(1, len(myFcxr))
        self.assertEqual(Coord.Dim(value=0.0, units='in'), myFcxr[0].left)
        self.assertEqual(Coord.Dim(value=2.4, units='in'), myFcxr[0].right)
        self.assertFalse(myFcxr[0].hasGrid)
        self.assertTrue(myFcxr[0].plotXLines)
        self.assertFalse(myFcxr[0].plotXAlpha)
        
    def test_06(self):
        """TestPhysFilmCfgXMLRead.test_06(): Test reading track1 with no x Axis lines, no Y grid."""
        root = etree.fromstring("""<LgFormat UniqueId="TestOneTrack" xmlns="x-schema:LgSchema2.xml">
    <LgVerticalScale UniqueId="VerticalScale">
        <IndexScaler>100</IndexScaler>
        <IndexUnit>Ft</IndexUnit>
        <PaperScaler>5</PaperScaler>
        <PaperUnit>LG_PAPER_INCH</PaperUnit>
    </LgVerticalScale>
    <LgTrack UniqueId="Track1">
        <Description>Depth Track</Description>
        <IndexLinesVisible>0</IndexLinesVisible>
        <IndexNumbersVisible>0</IndexNumbersVisible>
        <RightPosition>2.4</RightPosition>
    </LgTrack>
</LgFormat>""")
        myFcxr = FILMCfgXML.PhysFilmCfgXMLRead(root)
        self.assertEqual(1, len(myFcxr))
        self.assertEqual(Coord.Dim(value=0.0, units='in'), myFcxr[0].left)
        self.assertEqual(Coord.Dim(value=2.4, units='in'), myFcxr[0].right)
        self.assertFalse(myFcxr[0].hasGrid)
        self.assertFalse(myFcxr[0].plotXLines)
        self.assertFalse(myFcxr[0].plotXAlpha)
        
    def test_07(self):
        """TestPhysFilmCfgXMLRead.test_07(): Test reading track1 with no x Axis lines but with Y grid."""
        root = etree.fromstring("""<LgFormat UniqueId="TestOneTrack" xmlns="x-schema:LgSchema2.xml">
    <LgVerticalScale UniqueId="VerticalScale">
        <IndexScaler>100</IndexScaler>
        <IndexUnit>Ft</IndexUnit>
        <PaperScaler>5</PaperScaler>
        <PaperUnit>LG_PAPER_INCH</PaperUnit>
    </LgVerticalScale>
    <LgTrack UniqueId="Track1">
        <Description>Depth Track</Description>
        <IndexLinesVisible>0</IndexLinesVisible>
        <IndexNumbersVisible>0</IndexNumbersVisible>
        <RightPosition>2.4</RightPosition>
        <LgLinearGrid UniqueId="minorGrid1">
            <Color>818181</Color>
            <LineCount>11</LineCount>
        </LgLinearGrid>
        <LgLinearGrid UniqueId="majorGrid11">
            <Color>818181</Color>
            <LineCount>3</LineCount>
            <Thickness>2</Thickness>
        </LgLinearGrid>
    </LgTrack>
</LgFormat>""")
        myFcxr = FILMCfgXML.PhysFilmCfgXMLRead(root)
        self.assertEqual(1, len(myFcxr))
        self.assertEqual(Coord.Dim(value=0.0, units='in'), myFcxr[0].left)
        self.assertEqual(Coord.Dim(value=2.4, units='in'), myFcxr[0].right)
        self.assertTrue(myFcxr[0].hasGrid)
        self.assertFalse(myFcxr[0].plotXLines)
        self.assertFalse(myFcxr[0].plotXAlpha)

class TestFILMCfgXML(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """TestFILMCfgXML.test_00(): Test setUp() and tearDown()"""
        pass
    
    def test_01(self):
        """TestFILMCfgXML.test_01(): Test construction."""
        myFcxr = FILMCfgXML.FilmCfgXMLRead()
        self.assertEqual(29, len(myFcxr))

    def test_02(self):
        """TestFILMCfgXML.test_02(): Test construction, dump output."""
        myFcxr = FILMCfgXML.FilmCfgXMLRead()
        self.assertEqual(29, len(myFcxr))
        self.assertTrue("Micro_Resistivity_3Track.xml" in myFcxr)
#        print()
#        for k in sorted(myFcxr.keys()):
#            print('{:50s}: {:s}'.format(k, str(myFcxr[k])))

    def test_03(self):
        """TestFILMCfgXML.test_03(): Test construction has key "Micro_Resistivity_3Track.xml"."""
        myFcxr = FILMCfgXML.FilmCfgXMLRead()
        self.assertEqual(29, len(myFcxr))
        self.assertTrue("Micro_Resistivity_3Track.xml" in myFcxr)

    def test_04(self):
        """TestFILMCfgXML.test_04(): "Micro_Resistivity_3Track.xml" tracks."""
        myFcxr = FILMCfgXML.FilmCfgXMLRead()
        self.assertEqual(29, len(myFcxr))
        self.assertTrue("Micro_Resistivity_3Track.xml" in myFcxr)
#        print()
#        print('Micro Res:', myFcxr["Micro_Resistivity_3Track.xml"])
        # Four tracks
        self.assertEqual(4, len(myFcxr["Micro_Resistivity_3Track.xml"]))
#        for i, t in enumerate(myFcxr["Micro_Resistivity_3Track.xml"].genTracks()):
#            print(i, t)
#        print(myFcxr["Micro_Resistivity_3Track.xml"][0].left)
        self.assertEqual(Coord.Dim(0, 'in'), myFcxr["Micro_Resistivity_3Track.xml"][0].left)
        leftRight = [(t.left, t.right) for t in myFcxr["Micro_Resistivity_3Track.xml"].genTracks()]
#        print(leftRight)
        expResult = [
            (Coord.Dim(value=0.0, units='in'), Coord.Dim(value=2.4, units='in')),
            (Coord.Dim(value=2.4, units='in'), Coord.Dim(value=3.2, units='in')),
            (Coord.Dim(value=3.2, units='in'), Coord.Dim(value=5.6, units='in')),
            (Coord.Dim(value=5.6, units='in'), Coord.Dim(value=8.0, units='in')),
        ]
        self.assertEqual(expResult, leftRight)

    def test_10(self):
        """TestFILMCfgXML.test_10(): "Resistivity_3Track_Logrithmic.xml" tracks chOutpMnemInFilmId()."""
        myFcxr = FILMCfgXML.FilmCfgXMLRead()
        self.assertEqual(29, len(myFcxr))
        myFilmID = 'Resistivity_3Track_Logrithmic.xml'
#        print()
#        pprint.pprint(myFcxr._chOutpMnemFilmMap)
        self.assertTrue(myFilmID in myFcxr)
        for aCuOutp in (Mnem.Mnem(c, len_mnem=-Mnem.LEN_MNEM) for c in (
                'BS', 'ROP5', 'CALI', 'PCAL', 'HCAL', 'SP', 'GR', 'ATR', 'PSR',
                'AHT10', 'AHT20', 'AHT30', 'AHT60', 'AHT90',
                'AHO10', 'AHO20', 'AHO30', 'AHO60', 'AHO90',
                'AHF10', 'AHF20', 'AHF30', 'AHF60', 'AHF90',
                'RLA0', 'RLA1', 'RLA2', 'RLA3', 'RLA4', 'RLA5',
                'SFL', 'ILM', 'ILD', 'MSFL', 'RXO', 'LLM', 'LLD',
                'A22H', 'A34H', 'P16H_RT', 'P28H_RT', 'P34H_RT', 'TENS',
                )
            ):
            self.assertTrue(myFcxr.chOutpMnemInFilmId(aCuOutp, myFilmID), 'aCuOutp="{!r:s}"'.format(aCuOutp))
            
    def test_11(self):
        """TestFILMCfgXML.test_12(): "Resistivity_3Track_Logrithmic.xml" tracks chOutpMnemInFilmId() returns False."""
        myFcxr = FILMCfgXML.FilmCfgXMLRead()
        self.assertEqual(29, len(myFcxr))
        myFilmID = 'Resistivity_3Track_Logrithmic.xml'
#        print()
#        pprint.pprint(myFcxr._chOutpMnemFilmMap)
        self.assertTrue(myFilmID in myFcxr)
        # Not a Mnem.Mnem object
        self.assertFalse(myFcxr.chOutpMnemInFilmId('NOTBS', myFilmID))

    def test_12(self):
        """TestFILMCfgXML.test_12(): "Resistivity_3Track_Logrithmic.xml" exercise longStr()."""
        myFcxr = FILMCfgXML.FilmCfgXMLRead()
        self.assertEqual(29, len(myFcxr))
        myFcxr.longStr()

    def test_13(self):
        """TestFILMCfgXML.test_13(): "Resistivity_3Track_Logrithmic.xml" test rootNode()."""
        myFcxr = FILMCfgXML.FilmCfgXMLRead()
        self.assertEqual(29, len(myFcxr))
        self.assertTrue(myFcxr.rootNode("Resistivity_3Track_Logrithmic.xml") is not None)

    def test_14(self):
        """TestFILMCfgXML.test_14(): "Resistivity_3Track_Logrithmic.xml" test rootNode() returns None."""
        myFcxr = FILMCfgXML.FilmCfgXMLRead()
        self.assertEqual(29, len(myFcxr))
        self.assertRaises(KeyError, myFcxr.rootNode, "")

    def test_15(self):
        """TestFILMCfgXML.test_15(): "Resistivity_3Track_Logrithmic.xml" test retAllFILMDestS()."""
        myFcxr = FILMCfgXML.FilmCfgXMLRead()
        self.assertEqual(29, len(myFcxr))
#        print('')
#        pprint.pprint(myFcxr._chOutpMnemFilmMap)
        self.assertEqual(
            [
                 'Azimuthal_Density_3Track.xml',
                 'Azimuthal_Resistivity_3Track.xml',
                 'Micro_Resistivity_3Track.xml',
                 'Porosity_GR_3Track',
                 'Resistivity_3Track_Correlation.xml',
                 'Resistivity_3Track_Logrithmic.xml',
                 'Resistivity_Investigation_Image.xml',
                 'Sonic_3Track.xml',
                 'Triple_Combo',
            ],
            sorted(myFcxr.retAllFILMDestS(Mnem.Mnem('BS'))),
        )

    def test_16(self):
        """TestFILMCfgXML.test_16(): "Resistivity_3Track_Logrithmic.xml" test retAllFILMDestS() fails."""
        myFcxr = FILMCfgXML.FilmCfgXMLRead()
        self.assertEqual(29, len(myFcxr))
#        print(myFcxr._chOutpMnemFilmMap)
        self.assertRaises(FILMCfgXML.ExceptionFILMCfgXMLReadLookUp, myFcxr.retAllFILMDestS, Mnem.Mnem('NOTBS', len_mnem=0))

    def test_17(self):
        """TestFILMCfgXML.test_17(): "Resistivity_3Track_Logrithmic.xml" test retFILMDest()."""
        myFcxr = FILMCfgXML.FilmCfgXMLRead()
        self.assertEqual(29, len(myFcxr))
        self.assertTrue(myFcxr.retFILMDest("Resistivity_3Track_Logrithmic.xml", Mnem.Mnem('BS')) is not None)

    def test_18(self):
        """TestFILMCfgXML.test_18(): "Resistivity_3Track_Logrithmic.xml" test retFILMDest() fails."""
        myFcxr = FILMCfgXML.FilmCfgXMLRead()
        self.assertEqual(29, len(myFcxr))
        self.assertRaises(
            FILMCfgXML.ExceptionFILMCfgXMLReadLookUp,
            myFcxr.retFILMDest,
            "Resistivity_3Track_Logrithmic.xml",
            Mnem.Mnem('NOTBS', len_mnem=0),
        )

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPhysFilmCfgXMLRead))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFILMCfgXML))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Test ..."""
    print("""Test.py - A module that tests ...
Usage:
python Test....py [-lh --help]

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
    print(('Test....py script version "%s", dated %s' % (__version__, __date__)))
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
