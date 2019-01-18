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

Created on Jan 3, 2012

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

from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import RepCode
from TotalDepth.LAS.core import LASRead
from TotalDepth.util.plot import SVGWriter
from TotalDepth.util.plot import Coord
from TotalDepth.util.plot import LogHeader

sys.path.append(os.path.join(os.path.dirname(__file__)))
import TestPlotShared
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import BaseTestClasses

def _hdrTrippleToLogicalRecord(theData):
    # Record header
    myB = [
        bytes([34, 0]),
        bytes([73, 65, 4, 0]),
        bytes('TYPE', 'ascii'),
        bytes('    ', 'ascii'),
        bytes('CONS', 'ascii'),
    ]
    # Insert record contents
    CODE_INT = 73
    CODE_FLOAT = 68
    for m, v, u in theData:
        if u is None:
            u = b'    '
        myB.append(bytes([0, 65, 4, 0]))
        myB.append(b'MNEM') # Mnem
        myB.append(b'    ') # Units
        myB.append(m)
        myB.append(bytes([69, 65, 4, 0]))
        myB.append(b'STAT')
        myB.append(b'    ')
        myB.append(b'ALLO')
        myB.append(bytes([69, 65, 4, 0]))
        myB.append(b'PUNI')
        myB.append(b'    ')
        myB.append(u)
        myB.append(bytes([69, 65, 4, 0]))
        myB.append(b'TUNI')
        myB.append(b'    ')
        myB.append(u)
        assert(type(v) in (bytes, int, float))
        if isinstance(v, bytes):
            myB.append(bytes([69, 65, len(v), 0]))
            myB.append(b'VALU')
            myB.append(u)
            myB.append(v)
        elif isinstance(v, int):
            myB.append(bytes([69, CODE_INT, RepCode.lisSize(CODE_INT), 0]))
            myB.append(b'VALU')
            myB.append(u)
            myB.append(RepCode.writeBytes(v, CODE_INT))
        elif isinstance(v, float):
            myB.append(bytes([69, CODE_FLOAT, RepCode.lisSize(CODE_FLOAT), 0]))
            myB.append(b'VALU')
            myB.append(u)
            myB.append(RepCode.writeBytes(v, CODE_FLOAT))
    # Use self._retFilePrS() as size could be large
    myBaseFile = BaseTestClasses.TestBaseFile()
    myF = myBaseFile._retFilePrS(b''.join(myB))
    return LogiRec.LrTableRead(myF)

def headerLogicalRecordLIS():
    """Returns a CONS Logical Record that contains header information."""
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
        (b'HIDE', b'Log Title',                      None),
        (b'HID1', b'Log Title ONE',                      None),
        (b'HID2', b'Log Title TWO',                      None),
        # Deviation and Lat/Long
        (b'MHD ', 12.7,   b'DEG '),
        (b'LATI', b'52 31\' 47.369"N',   None),
        (b'LONG', b'2 12\' 12.196"W',   None),
        # Fine column of 24 rows
        (b'DATE', b'2012-01-05', None),
        (b'RUN ', b'Run number',                      None),
        (b'TDD ', 3000.0,   b'M   '),
        (b'TDL ', 2989.5,   b'M   '),
        (b'BLI ', 2980.0,   b'M   '),
        (b'TLI ', 1989.5,   b'M   '),
        (b'CSIZ', 9.625,    b'IN  '),
        (b'CD  ', 1988.5,   b'M   '),
        (b'CBLO', 1989.25,  b'M   '),
        (b'BS  ', 8.0,      b'IN  '),
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
        (b'MRT ', 153.6,    b'DEGC'),
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
    return _hdrTrippleToLogicalRecord(myData)

TEST_SVG_FILE_MAP_HDR = {
    40   : TestPlotShared.SVGTestOutput(
            'APIHeader_40_LIS.svg',
            "TestLogHeaderLIS.test_05(): Empty API header from LIS data (upright)."
        ),
    41   : TestPlotShared.SVGTestOutput(
            'APIHeader_41_LIS.svg',
            "TestLogHeaderLIS.test_06(): Empty API header from LIS data (rotated)."
        ),
    45   : TestPlotShared.SVGTestOutput(
            'APIHeader_45_LIS.svg',
            "TestLogHeaderLIS.test_10(): API header with CONS information from LIS data (upright)."
        ),
    46   : TestPlotShared.SVGTestOutput(
            'APIHeader_46_LIS.svg',
            "TestLogHeaderLIS.test_11(): API header with CONS information from LIS data (rotated)."
        ),
    50   : TestPlotShared.SVGTestOutput(
            'APIHeader_50_LAS.svg',
            "TestLogHeaderLAS.test_05(): Empty API header from LAS data (upright)."
        ),
    51   : TestPlotShared.SVGTestOutput(
            'APIHeader_51_LAS.svg',
            "TestLogHeaderLAS.test_06(): Empty API header from LAS data (rotated)."
        ),
    55   : TestPlotShared.SVGTestOutput(
            'APIHeader_55_LAS.svg',
            "TestLogHeaderLAS.test_10(): API header with CONS information from LAS data (upright)."
        ),
    56   : TestPlotShared.SVGTestOutput(
            'APIHeader_56_LAS.svg',
            "TestLogHeaderLAS.test_11(): API header with CONS information from LAS data (rotated)."
        ),
}

class TestLogHeaderLIS(BaseTestClasses.TestBaseFile):

    def setUp(self):
        self._lrCONS = headerLogicalRecordLIS()

    def tearDown(self):
        pass

    def test_00(self):
        pass

    def test_01(self):
        """TestLogHeader.test_00(): CONS table."""
        self.assertEqual(LogiRec.LR_TYPE_WELL_DATA, self._lrCONS.type)
        self.assertEqual(b'CONS', self._lrCONS.value)
        #print()
#        for r in self._lrCONS.genRows():
#            for c in r.genCells():
#                print(c.engVal, '\t', end="")
#            print('')
#        self.assertEqual(len(self._lrCONS), 13)
        self.assertFalse(self._lrCONS.isSingleParam)
        #print(sorted(list(myT.rowLabels())))
#        self.assertEqual(
#            [
#                 b'SP\x00\x00'
#             ],                         
#             sorted(list(self._lrCONS.rowLabels())),
#        )
        #print(myT.colLabels())
        self.assertEqual(
            {b'MNEM', b'STAT', b'PUNI', b'TUNI', b'VALU'},
            self._lrCONS.colLabels(),
        )
        self.assertTrue(self._lrCONS[b'HIDE'] is not None)
        self.assertEqual(5, len(self._lrCONS[b'HIDE']))
        self.assertEqual(b'Log Title', self._lrCONS[b'HIDE'][b'VALU'].value)

    def test_02(self):
        """TestLogHeader.test_02(): MNEM count and LogHeader.lrDataCount()."""
        self.assertEqual(53, len(self._lrCONS))
        myLh = LogHeader.APIHeaderLIS(isTopOfLog=True)
        self.assertEqual(53, myLh.lrDataCount([self._lrCONS,]))
#        print()
#        print(myLh.missingFields([self._lrCONS,]))
        self.assertEqual((set(), set()), myLh.missingFields([self._lrCONS,]))

    def test_04(self):
        """TestLogHeader.test_04(): APIHeaderLIS.viewPort()."""
        myLh = LogHeader.APIHeaderLIS(isTopOfLog=False)
        self.assertEqual(
            Coord.Box(width=Coord.Dim(value=6.25, units='in'), depth=Coord.Dim(value=8.0, units='in')),
            myLh.size(),
        )
        tl = Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(0.5, 'in'))
        self.assertEqual(
            Coord.Box(width=Coord.Dim(value=6.5, units='in'), depth=Coord.Dim(value=8.5, units='in')),
            myLh.viewPort(tl),
        )

    def test_05(self):
        """TestLogHeader.test_05(): Plot as not top of log."""
        myLh = LogHeader.APIHeaderLIS(isTopOfLog=False)
        fp = TestPlotShared.outPath(TEST_SVG_FILE_MAP_HDR[40].fileName)
        tl = Coord.Pt(Coord.Dim(0.0, 'in'), Coord.Dim(0.0, 'in'))
        viewPort = myLh.viewPort(tl)
        with SVGWriter.SVGWriter(open(fp, 'w'), viewPort) as xS:
            myLh.plot(xS, tl)

    def test_06(self):
        """TestLogHeader.test_06(): Plot as top of log."""
        myLh = LogHeader.APIHeaderLIS(isTopOfLog=True)
        fp = TestPlotShared.outPath(TEST_SVG_FILE_MAP_HDR[41].fileName)
        tl = Coord.Pt(Coord.Dim(0.0, 'in'), Coord.Dim(0.0, 'in'))
        viewPort = myLh.viewPort(tl)
        with SVGWriter.SVGWriter(open(fp, 'w'), viewPort) as xS:
            myLh.plot(xS, tl)

    def test_10(self):
        """TestLogHeader.test_10(): Plot as not top of log with CONS data."""
        myLh = LogHeader.APIHeaderLIS(isTopOfLog=False)
        fp = TestPlotShared.outPath(TEST_SVG_FILE_MAP_HDR[45].fileName)
        tl = Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(0.5, 'in'))
        viewPort = myLh.viewPort(tl)
        with SVGWriter.SVGWriter(open(fp, 'w'), viewPort) as xS:
            myLh.plot(xS, tl, [self._lrCONS,])

    def test_11(self):
        """TestLogHeader.test_11(): Plot as top of log with CONS data."""
        myLh = LogHeader.APIHeaderLIS(isTopOfLog=True)
        fp = TestPlotShared.outPath(TEST_SVG_FILE_MAP_HDR[46].fileName)
        tl = Coord.Pt(Coord.Dim(0.5, 'in'), Coord.Dim(0.25, 'in'))
        viewPort = myLh.viewPort(tl)
        with SVGWriter.SVGWriter(open(fp, 'w'), viewPort) as xS:
            myLh.plot(xS, tl, [self._lrCONS,])

    def test_20(self):
        """TestLogHeader.test_20(): Fails with wrong Logical Record type 32."""
        myB = [
            bytes([32, 0]),
            bytes([73, 65, 4, 0]),
            bytes('TYPE', 'ascii'),
            bytes('    ', 'ascii'),
            bytes('CONS', 'ascii'),
        ]
        myB.append(bytes([0, 65, 4, 0]))
        myB.append(b'MNEM')
        myB.append(b'    ')
        myB.append(b'HIDE')
        myB.append(bytes([69, 65, 4, 0]))
        myB.append(b'VALU')
        myB.append(b'    ')
        myB.append(b'Well')
        myF = self._retFilePrS(b''.join(myB))
        myLrCONS = LogiRec.LrTableRead(myF)
        myLh = LogHeader.APIHeaderLIS(isTopOfLog=False)
        tl = Coord.Pt(Coord.Dim(0.0, 'in'), Coord.Dim(0.0, 'in'))
        self.assertRaises(LogHeader.ExceptionLogHeader, myLh.plot, None, tl, [myLrCONS,])

    def test_21(self):
        """TestLogHeader.test_21(): Fails with wrong Logical Record value 'PRES'."""
        myB = [
            bytes([34, 0]),
            bytes([73, 65, 4, 0]),
            bytes('TYPE', 'ascii'),
            bytes('    ', 'ascii'),
            bytes('PRES', 'ascii'),
        ]
        myB.append(bytes([0, 65, 4, 0]))
        myB.append(b'MNEM')
        myB.append(b'    ')
        myB.append(b'HIDE')
        myB.append(bytes([69, 65, 4, 0]))
        myB.append(b'VALU')
        myB.append(b'    ')
        myB.append(b'Well')
        myF = self._retFilePrS(b''.join(myB))
        myLrCONS = LogiRec.LrTableRead(myF)
        myLh = LogHeader.APIHeaderLIS(isTopOfLog=False)
        tl = Coord.Pt(Coord.Dim(0.0, 'in'), Coord.Dim(0.0, 'in'))
        self.assertRaises(LogHeader.ExceptionLogHeader, myLh.plot, None, tl, [myLrCONS,])

    def test_22(self):
        """TestLogHeader.test_22(): Fails with Logical Record that is missing 'MNEM' column."""
        myB = [
            bytes([34, 0]),
            bytes([73, 65, 4, 0]),
            bytes('TYPE', 'ascii'),
            bytes('    ', 'ascii'),
            bytes('CONS', 'ascii'),
        ]
        myB.append(bytes([0, 65, 4, 0]))
        myB.append(b'mnem')
        myB.append(b'    ')
        myB.append(b'HIDE')
        myB.append(bytes([69, 65, 4, 0]))
        myB.append(b'VALU')
        myB.append(b'    ')
        myB.append(b'Well')
        myF = self._retFilePrS(b''.join(myB))
        myLrCONS = LogiRec.LrTableRead(myF)
        myLh = LogHeader.APIHeaderLIS(isTopOfLog=False)
        tl = Coord.Pt(Coord.Dim(0.0, 'in'), Coord.Dim(0.0, 'in'))
        self.assertRaises(LogHeader.ExceptionLogHeader, myLh.plot, None, tl, [myLrCONS,])

    def test_23(self):
        """TestLogHeader.test_23(): Fails with Logical Record that is missing 'VALU' column."""
        myB = [
            bytes([34, 0]),
            bytes([73, 65, 4, 0]),
            bytes('TYPE', 'ascii'),
            bytes('    ', 'ascii'),
            bytes('CONS', 'ascii'),
        ]
        myB.append(bytes([0, 65, 4, 0]))
        myB.append(b'MNEM')
        myB.append(b'    ')
        myB.append(b'HIDE')
        myB.append(bytes([69, 65, 4, 0]))
        myB.append(b'valu')
        myB.append(b'    ')
        myB.append(b'Well')
        myF = self._retFilePrS(b''.join(myB))
        myLrCONS = LogiRec.LrTableRead(myF)
        myLh = LogHeader.APIHeaderLIS(isTopOfLog=False)
        tl = Coord.Pt(Coord.Dim(0.0, 'in'), Coord.Dim(0.0, 'in'))
        self.assertRaises(LogHeader.ExceptionLogHeader, myLh.plot, None, tl, [myLrCONS,])

class TestLogHeaderLAS(BaseTestClasses.TestBaseFile):

    def setUp(self):
        myFi = io.StringIO("""~VERSION INFORMATION
 VERS.                     2.0: CWLS LOG ASCII STANDARD - VERSION 2
 WRAP.                      NO: One line per depth step

~Well Information Section
#MNEM.UNIT    Data Type    Information  
#---------    -------------    ------------------------------
STRT.M                    635.0000:
STOP.M                    400.0000:
STEP.M                     -0.1250:
NULL.                      -999.25:
COMP.         ANY OIL COMPANY INC.: COMPANY
WELL.        ANY ET AL A9-16-49-20: WELL
FLD .                         EDAM: FIELD
LOC .               A9-16-49-20W3M: LOCATION
PROV.                 SASKATCHEWAN: PROVINCE
SRVC.     ANY LOGGING COMPANY INC.: SERVICE COMPANY
DATE.                    13-DEC-86: LOG DATE
UWI .             100091604920W300: UNIQUE WELL ID
LAT .                     38.53915: Latitude North (KGS,LEO3.6)
LON .                     98.95341: LONGITUDE WEST (KGS, LEO3.6)

~Parameter Information Section
#MNEM.UNIT      Value        Description
#---------   -------------   ------------------------------
 BHT .DEGC         24.0000:  Bottom Hole Temperature
 BS  .MM          222.0000:  Bit Size
 FD  .K/M3        999.9999:  Fluid Density
 MDEN.K/M3       2650.0000:  Logging Matrix Density
 MATR.              1.0000:  Neutron Matrix (1=Sand)
 FNUM.              1.0000:  Tortuosity  Constant Archie's (a)
 FEXP.              2.0000:  Cementation Exponent Archie's (m)
 DFD .K/M3       1200.0000:  Mud Weight
 DFV .S            50.0000:  Mud Viscosity
 DFL .C3            8.0000:  Mud Fluid Loss
 DFPH.             10.0000:  Mud pH
 RMFS.OHMM          2.8200:  Mud Filtrate Resistivity
 EKB .M           566.9700:  Elevation Kelly Bushing
 EGL .M           563.6799:  Elevation Ground Level
 DL  .M           635.0000:  Depth Logger
 """)
        self._lasFile = LASRead.LASRead(myFi, 'MyID')

    def tearDown(self):
        pass

    def test_00(self):
        """TestLogHeaderLAS.test_00(): Tables in LAS file."""
        pass

    def test_01(self):
        """TestLogHeaderLAS.test_01(): Tables in LAS file."""
        self.assertEqual(3, len(self._lasFile))
        
    def test_05(self):
        """TestLogHeaderLAS.test_05(): Plot as not top of log."""
        myLh = LogHeader.APIHeaderLAS(isTopOfLog=False)
        fp = TestPlotShared.outPath(TEST_SVG_FILE_MAP_HDR[50].fileName)
        tl = Coord.Pt(Coord.Dim(0.0, 'in'), Coord.Dim(0.0, 'in'))
        viewPort = myLh.viewPort(tl)
        with SVGWriter.SVGWriter(open(fp, 'w'), viewPort) as xS:
            myLh.plot(xS, tl)

    def test_06(self):
        """TestLogHeaderLAS.test_06(): Plot as top of log."""
        myLh = LogHeader.APIHeaderLAS(isTopOfLog=True)
        fp = TestPlotShared.outPath(TEST_SVG_FILE_MAP_HDR[51].fileName)
        tl = Coord.Pt(Coord.Dim(0.0, 'in'), Coord.Dim(0.0, 'in'))
        viewPort = myLh.viewPort(tl)
        with SVGWriter.SVGWriter(open(fp, 'w'), viewPort) as xS:
            myLh.plot(xS, tl)

    def test_10(self):
        """TestLogHeaderLAS.test_10(): Plot as not top of log with CONS data."""
        myLh = LogHeader.APIHeaderLAS(isTopOfLog=False)
        fp = TestPlotShared.outPath(TEST_SVG_FILE_MAP_HDR[55].fileName)
        tl = Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(0.5, 'in'))
        viewPort = myLh.viewPort(tl)
        with SVGWriter.SVGWriter(open(fp, 'w'), viewPort) as xS:
            myLh.plot(xS, tl, self._lasFile)

    def test_11(self):
        """TestLogHeaderLAS.test_11(): Plot as top of log with CONS data."""
        myLh = LogHeader.APIHeaderLAS(isTopOfLog=True)
        fp = TestPlotShared.outPath(TEST_SVG_FILE_MAP_HDR[56].fileName)
        tl = Coord.Pt(Coord.Dim(0.5, 'in'), Coord.Dim(0.25, 'in'))
        viewPort = myLh.viewPort(tl)
        with SVGWriter.SVGWriter(open(fp, 'w'), viewPort) as xS:
            myLh.plot(xS, tl, self._lasFile)
#        a, b = myLh.missingFields(self._lasFile)
#        print('Missing fields:')
#        print('Not in LAS file:\n', sorted(a))
#        print('In LAS file but can\'t be plotted:\n', sorted(b))

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogHeaderLIS))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogHeaderLAS))
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
