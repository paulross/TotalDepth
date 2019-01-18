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

Created on Jan 21, 2012

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2012 Paul Ross.'

import sys
import os
import logging
import time
import unittest
import io
import pprint

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

from TotalDepth.LAS.core import LASRead
from TotalDepth.LIS.core import Mnem
from TotalDepth.LIS.core import LogPass
from TotalDepth.LIS.core import LogiRec
from TotalDepth.util.plot import XMLMatches
from TotalDepth.util.plot import FILMCfgXML

from . import TestLgFormatXMLData
from . import TestPlotLASData

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import BaseTestClasses

class TestXMLMatches(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """TestXMLMatches.test_00(): Test setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestXMLMatches.test_01(): Which XML LgFormat files can plot LAS file, single TripleCombo XML file."""
        myLasFile = LASRead.LASRead(io.StringIO(TestPlotLASData.LAS_00_200_FEET_DOWN))
        # Assume the formats/ directory relative to this module
        d = os.path.join(os.path.dirname(__file__), 'formats')
        filmMap = XMLMatches.fileCurveMap(myLasFile, d)
        # Actual curves in this LAS file:
        # ['BMIN', 'BMNO', 'CALI', 'DEPT', 'DPHI', 'DRHO', 'GR', 'ILD', 'ILM', 'NPHI', 'PEF', 'RHOB', 'SFLU', 'SP', 'TNPH']
        #
        # In XML file:
        # ['AHT10', 'AHT20', 'AHT30', 'AHT60', 'AHT90', 'APDC', 'APLC', 'APSC', 'ATR', 'BS', 'C1', 'C2', 'CALI', 'CMFF', 'CMRP', 'DPHB', 'DPHI', 'DPHZ', 'DPOR_CDN', 'DSOZ', 'ENPH', 'GR', 'HCAL', 'HMIN', 'HMNO', 'ILD', 'ILM', 'LLD', 'LLM', 'MSFL', 'NPHI', 'NPOR', 'PCAL', 'PEFZ', 'PSR', 'RLA0', 'RLA1', 'RLA2', 'RLA3', 'RLA4', 'RLA5', 'ROP5', 'RSOZ', 'RXO', 'RXOZ', 'SFL', 'SNP', 'SP', 'SPHI', 'TENS', 'TNPB', 'TNPH', 'TNPH_CDN', 'TPHI']
        #
        # Alleged result:
        # ['CALI', 'DPHI', 'GR  ', 'ILD ', 'ILM ', 'NPHI', 'SP  ', 'TNPH']
        #
        # Formated, sorted.
        # -----------------
        # Actual curves in this LAS file:
        # ['BMIN', 'BMNO', 'CALI', 'DEPT', 'DPHI', 'DRHO', 'GR', 'ILD', 'ILM',
        # 'NPHI', 'PEF', 'RHOB', 'SFLU', 'SP', 'TNPH']
        #
        # In XML file:
        # ['AHT10', 'AHT20', 'AHT30', 'AHT60', 'AHT90', 'APDC', 'APLC', 'APSC',
        # 'ATR', 'BS', 'C1', 'C2', 'CALI', 'CMFF', 'CMRP', 'DPHB', 'DPHI', 'DPHZ',
        # 'DPOR_CDN', 'DSOZ', 'ENPH', 'GR', 'HCAL', 'HMIN', 'HMNO', 'ILD', 'ILM',
        # 'LLD', 'LLM', 'MSFL', 'NPHI', 'NPOR', 'PCAL', 'PEFZ', 'PSR', 'RLA0',
        # 'RLA1', 'RLA2', 'RLA3', 'RLA4', 'RLA5', 'ROP5', 'RSOZ', 'RXO', 'RXOZ',
        # 'SFL', 'SNP', 'SP', 'SPHI', 'TENS', 'TNPB', 'TNPH', 'TNPH_CDN', 'TPHI']
        #
        # Result, note SFL is achieved by substitution of an alternate:
        # ['CALI', 'DPHI', 'GR  ', 'ILD ', 'ILM ', 'NPHI', 'SFL ', 'SP  ', 'TNPH']
        print()
        pprint.pprint(filmMap)
        self.assertEqual(1, len(filmMap))
        self.assertTrue('Triple_Combo' in filmMap)
#        pprint.pprint(sorted([m.pStr() for m in filmMap['Triple_Combo']]))
        self.assertEqual(
            [Mnem.Mnem(o) for o in ['CALI', 'DPHI', 'GR  ', 'ILD ', 'ILM ', 'NPHI', 'SFL ', 'SP  ', 'TNPH']],
            sorted(filmMap['Triple_Combo']),
        )

class TestXMLMatchesHDT(BaseTestClasses.TestBaseFile):
    """Tests whether XML matches can be made with RHDT channel and a LIS LogPass."""
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """TestXMLMatches.test_00(): Test setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestXMLMatchesRHDT.test_01(): Which XML LgFormat files with RHDT (RepCode 234, 90 bytes) channel and a LIS LogPass."""
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 4, up/down value 0 (down)
            + bytes([4, 1, 66, 0])
            # EB 12, absent value -153.0
            + bytes([12, 4, 68])+b'\xbb\xb3\x80\x00'
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 1
            + b'RHDT' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 90]) + b'000' + b'\x01'+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 2
            + b'P1AZ' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 3
            + b'DEVI' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 4
            + b'HAZI' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 5
            + b'C1  ' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 6
            + b'C2  ' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 7
            + b'FEP ' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 8
            + b'RB  ' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        myLp = LogPass.LogPass(LogiRec.LrDFSRRead(myF), 'FileID')
        myFilmCfg = FILMCfgXML.FilmCfgXMLRead('')
        myFilmCfg.addXMLRoot(etree.fromstring(TestLgFormatXMLData.LGFORMAT_HDT))
        filmMap = XMLMatches.fileCurveMapFromFILM(myLp, myFilmCfg)
#        print()
#        print('myLp._chMap:')
#        pprint.pprint(myLp._chMap)
#        print(myLp.longStr())
#        pprint.pprint(sorted(myLp.outpMnemS()))
#        print('filmMap:')
#        pprint.pprint(filmMap)
#        pprint.pprint(sorted(filmMap['HDT']))
        self.assertEqual(
            [
                Mnem.Mnem(b'C1\x00\x00'),
                Mnem.Mnem(b'C2\x00\x00'),
                Mnem.Mnem(b'DEPT'),
                Mnem.Mnem(b'DEVI'),
                Mnem.Mnem(b'EMEX'),
                Mnem.Mnem(b'FC0\x00'),
                Mnem.Mnem(b'FC1\x00'),
                Mnem.Mnem(b'FC2\x00'),
                Mnem.Mnem(b'FC3\x00'),
                Mnem.Mnem(b'FC4\x00'),
                Mnem.Mnem(b'FEP\x00'),
                Mnem.Mnem(b'FEP1'),
                Mnem.Mnem(b'FEP2'),
                Mnem.Mnem(b'HAZI'),
                Mnem.Mnem(b'P1AZ'),
                Mnem.Mnem(b'PADP'),
                Mnem.Mnem(b'RAC1'),
                Mnem.Mnem(b'RAC2'),
                Mnem.Mnem(b'RB\x00\x00'),
                Mnem.Mnem(b'REF\x00'),
                Mnem.Mnem(b'REFC'),
                Mnem.Mnem(b'STAT'),
                Mnem.Mnem(b'TEMP'),
            ],
            sorted(myLp.outpMnemS()),
        )
        self.assertEqual(1, len(filmMap))
        self.assertTrue('HDT' in filmMap)
        self.assertEqual(
            [
                Mnem.Mnem(b'C1\x00\x00'),
                Mnem.Mnem(b'C2\x00\x00'),
                Mnem.Mnem(b'DEVI'),
                Mnem.Mnem(b'FC0\x00'),
                Mnem.Mnem(b'FC1\x00'),
                Mnem.Mnem(b'FC2\x00'),
                Mnem.Mnem(b'FC3\x00'),
                Mnem.Mnem(b'FC4\x00'),
                Mnem.Mnem(b'HAZI'),
                Mnem.Mnem(b'P1AZ'),
                Mnem.Mnem(b'RB\x00\x00'),
            ],
            sorted(filmMap['HDT'])
        )
                
    def test_02(self):
        """TestXMLMatchesRHDT.test_01(): Which XML LgFormat files with RPS1 (RepCode 130, 80 bytes) channel and a LIS LogPass."""
        # DIPMETER_EDIT_TAPE_REP_CODE
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 4, up/down value 0 (down)
            + bytes([4, 1, 66, 0])
            # EB 12, absent value -153.0
            + bytes([12, 4, 68])+b'\xbb\xb3\x80\x00'
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 1
            + b'RPS1' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 80]) + b'000' + b'\x01'+ bytes([130,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 2
            + b'P1AZ' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 3
            + b'DEVI' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 4
            + b'HAZI' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 5
            + b'C1  ' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 6
            + b'C2  ' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 7
            + b'FEP ' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 8
            + b'RB  ' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        myLp = LogPass.LogPass(LogiRec.LrDFSRRead(myF), 'FileID')
        myFilmCfg = FILMCfgXML.FilmCfgXMLRead('')
        myFilmCfg.addXMLRoot(etree.fromstring(TestLgFormatXMLData.LGFORMAT_HDT))
        filmMap = XMLMatches.fileCurveMapFromFILM(myLp, myFilmCfg)
#        print()
#        print('myLp._chMap:')
#        pprint.pprint(myLp._chMap)
#        print(myLp.longStr())
#        pprint.pprint(sorted(myLp.outpMnemS()))
#        print('filmMap:')
#        pprint.pprint(filmMap)
#        pprint.pprint(sorted(filmMap['HDT']))
        self.assertEqual(
            [
                Mnem.Mnem(b'C1\x00\x00'),
                Mnem.Mnem(b'C2\x00\x00'),
                Mnem.Mnem(b'DEPT'),
                Mnem.Mnem(b'DEVI'),
#                Mnem.Mnem(b'EMEX'),
                Mnem.Mnem(b'FC0\x00'),
                Mnem.Mnem(b'FC1\x00'),
                Mnem.Mnem(b'FC2\x00'),
                Mnem.Mnem(b'FC3\x00'),
                Mnem.Mnem(b'FC4\x00'),
                Mnem.Mnem(b'FEP\x00'),
#                Mnem.Mnem(b'FEP1'),
#                Mnem.Mnem(b'FEP2'),
                Mnem.Mnem(b'HAZI'),
                Mnem.Mnem(b'P1AZ'),
#                Mnem.Mnem(b'PADP'),
#                Mnem.Mnem(b'RAC1'),
#                Mnem.Mnem(b'RAC2'),
                Mnem.Mnem(b'RB\x00\x00'),
#                Mnem.Mnem(b'REF\x00'),
#                Mnem.Mnem(b'REFC'),
#                Mnem.Mnem(b'STAT'),
#                Mnem.Mnem(b'TEMP'),
            ],
            sorted(myLp.outpMnemS()),
        )
        self.assertEqual(1, len(filmMap))
        self.assertTrue('HDT' in filmMap)
        self.assertEqual(
            [
                Mnem.Mnem(b'C1\x00\x00'),
                Mnem.Mnem(b'C2\x00\x00'),
                Mnem.Mnem(b'DEVI'),
                Mnem.Mnem(b'FC0\x00'),
                Mnem.Mnem(b'FC1\x00'),
                Mnem.Mnem(b'FC2\x00'),
                Mnem.Mnem(b'FC3\x00'),
                Mnem.Mnem(b'FC4\x00'),
                Mnem.Mnem(b'HAZI'),
                Mnem.Mnem(b'P1AZ'),
                Mnem.Mnem(b'RB\x00\x00'),
            ],
            sorted(filmMap['HDT'])
        )
                
class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestXMLMatches))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestXMLMatchesHDT))
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
