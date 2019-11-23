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

Created on Dec 17, 2011

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

import sys
import logging
import time
import unittest
import pprint

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

import pytest

from TotalDepth.LIS.core import Mnem
from TotalDepth.util.plot import Stroke
from TotalDepth.util.plot import FILMCfgXML
from TotalDepth.util.plot import PRESCfgXML


@pytest.mark.slow
class TestCurveCfgXMLRead(unittest.TestCase):

    def setUp(self):
        self._fcxr = FILMCfgXML.FilmCfgXMLRead()
        self.assertEqual(29, len(self._fcxr))

    def tearDown(self):
        pass

    def test_00(self):
        """CurveCfgXMLRead.test_00(): tests setUp() and tearDown()."""
        pass

    def test_00_01(self):
        """CurveCfgXMLRead.test_00_01(): tests low-level: _retBackup() LG_LEFT_WRAPPED."""
        # Say in <LgTrack UniqueId="track1">
        xStr = """<LgCurve UniqueId="Cali" xmlns="x-schema:LgSchema2.xml">
    <ChannelName>CALI</ChannelName>
    <Color>FF0000</Color>
    <LeftLimit>6</LeftLimit>
    <LineStyle>LG_DASH_LINE</LineStyle>
    <RightLimit>16</RightLimit>
    <Thickness>2</Thickness>
    <WrapCount>1</WrapCount>
</LgCurve>"""
        root = etree.fromstring(xStr)
        myCcxr = PRESCfgXML.CurveCfgXMLRead(root, "track1", self._fcxr)
        myB = myCcxr._retBackup(etree.fromstring("""<LgCurve xmlns="x-schema:LgSchema2.xml">
    <WrapMode>LG_LEFT_WRAPPED</WrapMode>
</LgCurve>"""))
        self.assertEqual((0, -1), myB)
        
    def test_00_02(self):
        """CurveCfgXMLRead.test_00_02(): tests low-level: _retBackup() UNKNOWN."""
        # Say in <LgTrack UniqueId="track1">
        xStr = """<LgCurve UniqueId="Cali" xmlns="x-schema:LgSchema2.xml">
    <ChannelName>CALI</ChannelName>
    <Color>FF0000</Color>
    <LeftLimit>6</LeftLimit>
    <LineStyle>LG_DASH_LINE</LineStyle>
    <RightLimit>16</RightLimit>
    <Thickness>2</Thickness>
    <WrapCount>1</WrapCount>
</LgCurve>"""
        root = etree.fromstring(xStr)
        myCcxr = PRESCfgXML.CurveCfgXMLRead(root, "track1", self._fcxr)
        myB = myCcxr._retBackup(etree.fromstring("""<LgCurve xmlns="x-schema:LgSchema2.xml">
    <WrapMode>UNKNOWN</WrapMode>
</LgCurve>"""))
        self.assertEqual((0,0), myB)
        
    def test_00_11(self):
        """CurveCfgXMLRead.test_00_11(): tests low-level: _retCoding()."""
        # Say in <LgTrack UniqueId="track1">
        xStr = """<LgCurve UniqueId="Cali" xmlns="x-schema:LgSchema2.xml">
    <ChannelName>CALI</ChannelName>
    <Color>FF0000</Color>
    <LeftLimit>6</LeftLimit>
    <LineStyle>LG_DASH_LINE</LineStyle>
    <RightLimit>16</RightLimit>
    <Thickness>2</Thickness>
    <WrapCount>1</WrapCount>
</LgCurve>"""
        root = etree.fromstring(xStr)
        myCcxr = PRESCfgXML.CurveCfgXMLRead(root, "track1", self._fcxr)
        myV = myCcxr._retCoding(etree.fromstring("""<LgCurve xmlns="x-schema:LgSchema2.xml">
    <Color>FF0000</Color>
    <LineStyle>LG_DASH_LINE</LineStyle>
</LgCurve>"""))
        self.assertEqual(Stroke.Stroke(width=0.5, colour='rgb(255,0,0)', coding=(4, 4), opacity=1.0), myV)
        
    def test_00_12(self):
        """CurveCfgXMLRead.test_00_12(): tests low-level: _retColour()."""
        # Say in <LgTrack UniqueId="track1">
        xStr = """<LgCurve UniqueId="Cali" xmlns="x-schema:LgSchema2.xml">
    <ChannelName>CALI</ChannelName>
    <Color>FF0000</Color>
    <LeftLimit>6</LeftLimit>
    <LineStyle>LG_DASH_LINE</LineStyle>
    <RightLimit>16</RightLimit>
    <Thickness>2</Thickness>
    <WrapCount>1</WrapCount>
</LgCurve>"""
        root = etree.fromstring(xStr)
        myCcxr = PRESCfgXML.CurveCfgXMLRead(root, "track1", self._fcxr)
        myV = myCcxr._retColour(etree.fromstring("""<LgCurve xmlns="x-schema:LgSchema2.xml">
    <Color>FF0000</Color>
</LgCurve>"""))
        self.assertEqual('rgb(255,0,0)', myV)
        
    def test_01(self):
        """CurveCfgXMLRead.test_01(): tests single channel read."""
        # Say in <LgTrack UniqueId="track1">
        xStr = """<LgCurve UniqueId="Cali" xmlns="x-schema:LgSchema2.xml">
    <ChannelName>CALI</ChannelName>
    <Color>FF0000</Color>
    <LeftLimit>6</LeftLimit>
    <LineStyle>LG_DASH_LINE</LineStyle>
    <RightLimit>16</RightLimit>
    <Thickness>2</Thickness>
    <WrapCount>1</WrapCount>
</LgCurve>"""
        root = etree.fromstring(xStr)
        myCcxr = PRESCfgXML.CurveCfgXMLRead(root, "track1", self._fcxr)
#        print()
#        print('myCcxr._filmTrackWidthMap [{:d}]'.format(len(myCcxr._filmTrackWidthMap)))
#        pprint.pprint(myCcxr._filmTrackWidthMap)
#        print()
#        print('myCcxr._filmTrackFnMap [{:d}]'.format(len(myCcxr._filmTrackFnMap)))
#        pprint.pprint(myCcxr._filmTrackFnMap)
        self.assertEqual('Cali', myCcxr.mnem)
        self.assertEqual('CALI', myCcxr.outp)
        self.assertEqual(True, myCcxr.stat)
        self.assertEqual('track1', myCcxr.trac)
        self.assertEqual(
            Stroke.Stroke(width=0.5, colour='rgb(255,0,0)', coding=(4, 4), opacity=1.0),
            myCcxr.codiStroke,
        )

    def test_02(self):
        """CurveCfgXMLRead.test_02(): tests single channel read fails when missing <ChannelName>."""
        # Say in <LgTrack UniqueId="track1">
        xStr = """<LgCurve UniqueId="Cali" xmlns="x-schema:LgSchema2.xml">
    <!-- <ChannelName>CALI</ChannelName> -->
    <Color>FF0000</Color>
    <LeftLimit>6</LeftLimit>
    <LineStyle>LG_DASH_LINE</LineStyle>
    <RightLimit>16</RightLimit>
    <Thickness>2</Thickness>
    <WrapCount>1</WrapCount>
</LgCurve>"""
        root = etree.fromstring(xStr)
        self.assertRaises(
            PRESCfgXML.ExceptionCurveCfgXMLRead,
            PRESCfgXML.CurveCfgXMLRead, 
            root, "track1", self._fcxr,
        )

    def test_03(self):
        """CurveCfgXMLRead.test_03(): tests single channel read fails when unsupported track name."""
        # Say in <LgTrack UniqueId="track1">
        xStr = """<LgCurve UniqueId="Cali" xmlns="x-schema:LgSchema2.xml">
    <ChannelName>CALI</ChannelName>
    <Color>FF0000</Color>
    <LeftLimit>6</LeftLimit>
    <LineStyle>LG_DASH_LINE</LineStyle>
    <RightLimit>16</RightLimit>
    <Thickness>2</Thickness>
    <WrapCount>1</WrapCount>
</LgCurve>"""
        root = etree.fromstring(xStr)
        self.assertRaises(
            PRESCfgXML.ExceptionCurveCfgXMLRead,
            PRESCfgXML.CurveCfgXMLRead, 
            root, "Not track1", self._fcxr,
        )

    def test_04(self):
        """CurveCfgXMLRead.test_04(): tests single channel read fails when unknown track in film."""
        # Say in <LgTrack UniqueId="track1">
        xStr = """<LgCurve UniqueId="Caliper" xmlns="x-schema:LgSchema2.xml">
    <ChannelName>CALIPER</ChannelName>
    <Color>FF0000</Color>
    <LeftLimit>6</LeftLimit>
    <LineStyle>LG_DASH_LINE</LineStyle>
    <RightLimit>16</RightLimit>
    <Thickness>2</Thickness>
    <WrapCount>1</WrapCount>
</LgCurve>"""
        root = etree.fromstring(xStr)
        self.assertRaises(
            PRESCfgXML.ExceptionCurveCfgXMLRead,
            PRESCfgXML.CurveCfgXMLRead, 
            root, "track1", self._fcxr,
        )

    def test_05(self):
        """CurveCfgXMLRead.test_05(): tests single channel mode is linear."""
        # Say in <LgTrack UniqueId="track1">
        xStr = """<LgCurve UniqueId="Caliper" xmlns="x-schema:LgSchema2.xml">
    <ChannelName>CALI</ChannelName>
    <Color>FF0000</Color>
    <LeftLimit>6</LeftLimit>
    <LineStyle>LG_DASH_LINE</LineStyle>
    <RightLimit>16</RightLimit>
    <Thickness>2</Thickness>
    <WrapCount>1</WrapCount>
</LgCurve>"""
        root = etree.fromstring(xStr)
        myCcxr = PRESCfgXML.CurveCfgXMLRead(root, "track1", self._fcxr)
        self.assertTrue(myCcxr.mode is None)

    def test_06(self):
        """CurveCfgXMLRead.test_06(): tests single channel read logarithmic."""
        # Say in <LgTrack UniqueId="track1">
        xStr = """<LgCurve UniqueId="PSR" xmlns="x-schema:LgSchema2.xml">
            <ChannelName>PSR</ChannelName>
            <Color>00C000</Color>
            <LeftLimit>0.2</LeftLimit>
            <RightLimit>2000</RightLimit>
            <Thickness>2</Thickness>
            <Transform>LG_LOGARITHMIC</Transform>
            <WrapCount>0</WrapCount>
</LgCurve>"""
        root = etree.fromstring(xStr)
        myCcxr = PRESCfgXML.CurveCfgXMLRead(root, "track1", self._fcxr)
        self.assertFalse(myCcxr.mode is None)

    def test_07(self):
        """CurveCfgXMLRead.test_07(): tests single channel wrap mode LG_LEFT_WRAPPED."""
        # Say in <LgTrack UniqueId="track1">
        xStr = """<LgCurve UniqueId="ROP5" xmlns="x-schema:LgSchema2.xml">
    <ChannelName>ROP5</ChannelName>
    <Color>0000FF</Color>
    <LeftLimit>500</LeftLimit>
    <RightLimit>0</RightLimit>
    <LineStyle>LG_DASH_LINE</LineStyle>
    <Thickness>1.75</Thickness>
    <WrapMode>LG_LEFT_WRAPPED</WrapMode>
</LgCurve>"""
        root = etree.fromstring(xStr)
        myCcxr = PRESCfgXML.CurveCfgXMLRead(root, "track1", self._fcxr)
#        self.assertTrue(myCcxr.mode is None)
        
    def test_08(self):
        """CurveCfgXMLRead.test_08(): tests single channel wrap mode UNKNOWN."""
        # Say in <LgTrack UniqueId="track1">
        xStr = """<LgCurve UniqueId="ROP5" xmlns="x-schema:LgSchema2.xml">
    <ChannelName>ROP5</ChannelName>
    <Color>0000FF</Color>
    <LeftLimit>500</LeftLimit>
    <RightLimit>0</RightLimit>
    <LineStyle>LG_DASH_LINE</LineStyle>
    <Thickness>1.75</Thickness>
    <WrapMode>UNKNOWN</WrapMode>
</LgCurve>"""
        root = etree.fromstring(xStr)
        myCcxr = PRESCfgXML.CurveCfgXMLRead(root, "track1", self._fcxr)
#        self.assertTrue(myCcxr.mode is None)

    def test_09(self):
        """CurveCfgXMLRead.test_09(): tests single channel coding OK."""
        # Say in <LgTrack UniqueId="track1">
        xStr = """<LgCurve UniqueId="ROP5" xmlns="x-schema:LgSchema2.xml">
    <ChannelName>ROP5</ChannelName>
    <Color>0000FF</Color>
    <LeftLimit>500</LeftLimit>
    <RightLimit>0</RightLimit>
    <LineStyle>LG_DASH_LINE</LineStyle>
    <Thickness>1.75</Thickness>
    <WrapMode>LG_LEFT_WRAPPED</WrapMode>
</LgCurve>"""
        root = etree.fromstring(xStr)
        myCcxr = PRESCfgXML.CurveCfgXMLRead(root, "track1", self._fcxr)
        self.assertEqual(
            Stroke.Stroke(width=0.5, colour='rgb(0,0,255)', coding=(4, 4), opacity=1.0),
            myCcxr.codiStroke,
        )
        
    def test_10(self):
        """CurveCfgXMLRead.test_10(): tests single channel coding substitutes default when rubbish encountered."""
        # Say in <LgTrack UniqueId="track1">
        xStr = """<LgCurve UniqueId="ROP5" xmlns="x-schema:LgSchema2.xml">
    <ChannelName>ROP5</ChannelName>
    <Color>0000FF</Color>
    <LeftLimit>500</LeftLimit>
    <RightLimit>0</RightLimit>
    <LineStyle>WASHING_LINE</LineStyle>
    <Thickness>1.75</Thickness>
    <WrapMode>LG_LEFT_WRAPPED</WrapMode>
</LgCurve>"""
        root = etree.fromstring(xStr)
        myCcxr = PRESCfgXML.CurveCfgXMLRead(root, "track1", self._fcxr)
        self.assertEqual(
            Stroke.Stroke(width=0.5, colour='rgb(0,0,255)', coding=None, opacity=1.0),
            myCcxr.codiStroke,
        )
        
    def test_11(self):
        """CurveCfgXMLRead.test_11(): tests single colour OK."""
        # Say in <LgTrack UniqueId="track1">
        xStr = """<LgCurve UniqueId="ROP5" xmlns="x-schema:LgSchema2.xml">
    <ChannelName>ROP5</ChannelName>
    <Color>0000FF</Color>
    <LeftLimit>500</LeftLimit>
    <RightLimit>0</RightLimit>
    <LineStyle>LG_DASH_LINE</LineStyle>
    <Thickness>1.75</Thickness>
    <WrapMode>LG_LEFT_WRAPPED</WrapMode>
</LgCurve>"""
        root = etree.fromstring(xStr)
        myCcxr = PRESCfgXML.CurveCfgXMLRead(root, "track1", self._fcxr)
        self.assertEqual(
            Stroke.Stroke(width=0.5, colour='rgb(0,0,255)', coding=(4, 4), opacity=1.0),
            myCcxr.codiStroke,
        )
        
    def test_12(self):
        """CurveCfgXMLRead.test_12(): tests single colour substitutes default when rubbish encountered."""
        # Say in <LgTrack UniqueId="track1">
        xStr = """<LgCurve UniqueId="ROP5" xmlns="x-schema:LgSchema2.xml">
    <ChannelName>ROP5</ChannelName>
    <!-- Missing text -->
    <Color/>
    <LeftLimit>500</LeftLimit>
    <RightLimit>0</RightLimit>
    <LineStyle>LG_DASH_LINE</LineStyle>
    <Thickness>1.75</Thickness>
    <WrapMode>LG_LEFT_WRAPPED</WrapMode>
</LgCurve>"""
        root = etree.fromstring(xStr)
        myCcxr = PRESCfgXML.CurveCfgXMLRead(root, "track1", self._fcxr)
        self.assertEqual(
            Stroke.Stroke(width=0.5, colour='rgb(0,0,0)', coding=(4, 4), opacity=1.0),
            myCcxr.codiStroke,
        )


@pytest.mark.slow
class TestPresCfgXMLRead(unittest.TestCase):
    TEST_FILM_ID = 'Resistivity_3Track_Logrithmic.xml'

    def setUp(self):
        self._fcxr = FILMCfgXML.FilmCfgXMLRead()
        self.assertEqual(29, len(self._fcxr))
        self.assertTrue(self.TEST_FILM_ID in self._fcxr)

    def tearDown(self):
        pass

    def test_00(self):
        """PresCfgXMLRead.test_00(): tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """PresCfgXMLRead.test_01(): create a PRESCfgXML.PresCfgXMLRead() from "Resistivity_3Track_Logrithmic.xml"."""
        PRESCfgXML.PresCfgXMLRead(
            self._fcxr,
            "Resistivity_3Track_Logrithmic.xml",
        )

    def test_02(self):
        """PresCfgXMLRead.test_02(): create a PRESCfgXML.PresCfgXMLRead() from "Resistivity_3Track_Logrithmic.xml" number of curves."""
        myPcxr = PRESCfgXML.PresCfgXMLRead(
            self._fcxr,
            "Resistivity_3Track_Logrithmic.xml",
        )
#        print('')
#        pprint.pprint(self._fcxr._chOutpMnemFilmMap)
#        print(myPcxr.keys())
        self.assertEqual(43, len(myPcxr))

    def test_03(self):
        """PresCfgXMLRead.test_03(): create a PRESCfgXML.PresCfgXMLRead() from "Resistivity_3Track_Logrithmic.xml" correct curves."""
        myPcxr = PRESCfgXML.PresCfgXMLRead(
            self._fcxr,
            "Resistivity_3Track_Logrithmic.xml",
        )
        self.assertEqual(
            sorted([Mnem.Mnem(v, len_mnem=0) for v in 
                    ['PCAL', 'ILD', 'AHT60_8', 'MSFL', 'ILM', 'AHO90_9', 'ATR',
                    'AHF90_9', 'AHF30_7', 'A34H_ARC', 'AHT10_6', 'AHF60_8',
                    'RXO', 'AHT90_9', 'LLM', 'RLA1', 'AHT30_7', 'RLA3', 'RLA2',
                    'RLA5', 'RLA4', 'P34H_ARC', 'LLD', 'ROP5', 'A22H_ARC',
                    'AHO60_8', 'AHF20_5', 'BS_7', 'RLA0', 'AHO30_7', 'AHT20_5',
                    'P28H_ARC', 'SP_10', 'GR_9', 'AHO10_6', 'HiltCaliper',
                    'AHF10_6', 'TENS_6', 'SFL', 'P16H_ARC', 'AHO20_5', 'PSR',
                    'CALI_8',
                    ]
                    ]),
            sorted(myPcxr.keys()),
        )
        self.assertTrue('BS_7' in myPcxr)

    def test_04(self):
        """PresCfgXMLRead.test_04(): create a PRESCfgXML.PresCfgXMLRead() from "Resistivity_3Track_Logrithmic.xml" outputs for destination."""
        myPcxr = PRESCfgXML.PresCfgXMLRead(
            self._fcxr,
            "Resistivity_3Track_Logrithmic.xml",
        )
        self.assertTrue(myPcxr.hasCurvesForDest("Resistivity_3Track_Logrithmic.xml"))
#        print()
#        print(sorted(myPcxr.outpChIDs("Resistivity_3Track_Logrithmic.xml")))
#        pprint.pprint(sorted(myPcxr.outpChIDs("Resistivity_3Track_Logrithmic.xml")))
        self.assertEqual(43, len(myPcxr.outpChIDs("Resistivity_3Track_Logrithmic.xml")))
        exp = [
                Mnem.Mnem(m) for m in [
                    'A22H', 'A34H', 'AHF10', 'AHF20', 'AHF30', 'AHF60', 'AHF90',
                    'AHO10', 'AHO20', 'AHO30', 'AHO60', 'AHO90', 'AHT10', 'AHT20',
                    'AHT30', 'AHT60', 'AHT90', 'ATR', 'BS', 'CALI', 'GR', 'HCAL',
                    'ILD', 'ILM', 'LLD', 'LLM', 'MSFL', 'P16H_RT', 'P28H_RT',
                    'P34H_RT', 'PCAL', 'PSR', 'RLA0', 'RLA1', 'RLA2', 'RLA3',
                    'RLA4', 'RLA5', 'ROP5', 'RXO', 'SFL', 'SP', 'TENS',
                ]
            ]
        act = sorted([str(v) for v in myPcxr.outpChIDs("Resistivity_3Track_Logrithmic.xml")])
        self.assertEqual(exp, act)

    def test_05(self):
        """PresCfgXMLRead.test_05(): create a PRESCfgXML.PresCfgXMLRead() from "Resistivity_3Track_Logrithmic.xml" outputs for destination."""
        myPcxr = PRESCfgXML.PresCfgXMLRead(
            self._fcxr,
            "Resistivity_3Track_Logrithmic.xml",
        )
        self.assertEqual(
            1,
            len(myPcxr.outpCurveIDs("Resistivity_3Track_Logrithmic.xml", Mnem.Mnem('BS'))),
        )
        self.assertEqual(
            ['BS_7',],
            myPcxr.outpCurveIDs("Resistivity_3Track_Logrithmic.xml", Mnem.Mnem('BS')),
        )
        
    def test_06(self):
        """PresCfgXMLRead.test_06(): create a PRESCfgXML.PresCfgXMLRead() from "Resistivity_3Track_Logrithmic.xml" outputs for destination."""
        myPcxr = PRESCfgXML.PresCfgXMLRead(
            self._fcxr,
            "Resistivity_3Track_Logrithmic.xml",
        )
        self.assertTrue(myPcxr.usesOutpChannel("Resistivity_3Track_Logrithmic.xml", Mnem.Mnem('BS')))
        self.assertFalse(myPcxr.usesOutpChannel("Resistivity_3Track_Logrithmic.xml", Mnem.Mnem('NOTBS')))
        self.assertFalse(myPcxr.usesOutpChannel("Resistivity_3Track_Logrithmic.xml", 'BS'))
        
    def test_15(self):
        """PresCfgXMLRead.test_15(): create a PRESCfgXML.PresCfgXMLRead() fails with wrong root node."""
#        xStr = """<LgFormatNOT UniqueId="NOT" xmlns="x-schema:LgSchema2.xml"/>
#"""
#        root = etree.fromstring(xStr)
        self.assertRaises(PRESCfgXML.ExceptionPresCfgXMLRead, PRESCfgXML.PresCfgXMLRead, self._fcxr, 'WTF')

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCurveCfgXMLRead))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPresCfgXMLRead))
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
