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

from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import Mnem
from TotalDepth.util.plot import Coord
from TotalDepth.util.plot import FILMCfg

######################
# Section: Unit tests.
######################
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import BaseTestClasses

class TestFILMRead(BaseTestClasses.TestBaseFile):
    """Tests reading a FILM table."""
    def setUp(self):
        """Set up Typical FILM record
Table record (type 34) type: FILM
MNEM  GCOD  GDEC  DEST  DSCA
-----------------------------
1     E20   -4--  PF1   D200
2     E2E   -4--  PF2   D200
"""
        myByFilm = b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1\x00\x00\x00' \
                    + b'EA\x04\x00GCOD    E20 ' \
                    + b'EA\x04\x00GDEC    -4--' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    2\x00\x00\x00' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D200'
        myFi = self._retFileSinglePr(myByFilm)
        self._fc = FILMCfg.FilmCfgLISRead(LogiRec.LrTableRead(myFi))
        self.assertTrue(Mnem.Mnem(b'1   ') in self._fc)
        self.assertFalse(Mnem.Mnem(b'10  ') in self._fc)

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestFILMRead.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestFILMRead.test_01(): Constructor."""
        self.assertEqual(2, len(self._fc))
        self.assertEqual([b'1\x00\x00\x00', b'2\x00\x00\x00'], sorted(list(self._fc.keys())))
#        print()
#        print(self._fc[b'1\x00\x00\x00'])
#        print(self._fc[b'1\x00\x00\x00'].name)
#        print(self._fc[b'1\x00\x00\x00'].xScale)
#        print(len(self._fc[b'1\x00\x00\x00']))
        self.assertEqual(b'1\x00\x00\x00', self._fc[b'1\x00\x00\x00'].name)
        self.assertEqual(200, self._fc[b'1\x00\x00\x00'].xScale)
        self.assertEqual(4, len(self._fc[b'1\x00\x00\x00']))
#        print('left', self._fc[b'1\x00\x00\x00'][0].left)
#        print('right', self._fc[b'1\x00\x00\x00'][0].right)
        self.assertEqual(Coord.Dim(0.0, 'in'), self._fc[b'1\x00\x00\x00'][0].left)
        self.assertEqual(Coord.Dim(2.4, 'in'), self._fc[b'1\x00\x00\x00'][0].right)
        self.assertEqual(Coord.Dim(2.4, 'in'), self._fc[b'1\x00\x00\x00'][1].left)
        self.assertEqual(Coord.Dim(3.2, 'in'), self._fc[b'1\x00\x00\x00'][1].right)
        self.assertEqual(Coord.Dim(3.2, 'in'), self._fc[b'1\x00\x00\x00'][2].left)
        self.assertEqual(Coord.Dim(5.6, 'in'), self._fc[b'1\x00\x00\x00'][2].right)
        self.assertEqual(Coord.Dim(5.6, 'in'), self._fc[b'1\x00\x00\x00'][3].left)
        self.assertEqual(Coord.Dim(8.0, 'in'), self._fc[b'1\x00\x00\x00'][3].right)
#        print('gridGn', self._fc[b'1\x00\x00\x00'][0]._gridGn)
#        print('gridGn', self._fc[b'1\x00\x00\x00'][1]._gridGn)
#        print('gridGn', self._fc[b'1\x00\x00\x00'][2]._gridGn)
#        print('gridGn', self._fc[b'1\x00\x00\x00'][3]._gridGn)

    def test_02(self):
        """TestFILMRead.test_02(): PhysFilmCfg.interpretTrac(), typical three track film."""
        # 2     E2E   -4--  PF2   D200
        myPfc = self._fc[b'2\x00\x00\x00']
#        print()
#        print(myPfc.interpretTrac(b'T1  '))
        self.assertEqual(
            (
                Coord.Dim(value=0.0, units='in'),
                Coord.Dim(value=2.4, units='in'),
                0,
                2,
            ),
            myPfc.interpretTrac(b'T1  '),
        )
        self.assertEqual(
            (
                Coord.Dim(value=2.4, units='in'),
                Coord.Dim(value=3.2, units='in'),
                2,
                2,
            ),
            myPfc.interpretTrac(b'TD  '),
        )
        self.assertEqual(
            (
                Coord.Dim(value=3.2, units='in'),
                Coord.Dim(value=5.6, units='in'),
                4,
                2,
            ),
            myPfc.interpretTrac(b'T2  '),
        )
        self.assertEqual(
            (
                Coord.Dim(value=5.6, units='in'),
                Coord.Dim(value=8.0, units='in'),
                6,
                2,
            ),
            myPfc.interpretTrac(b'T3  '),
        )
#        print()
#        print(myPfc.interpretTrac(b'T23 '))
        self.assertEqual(
            (
                Coord.Dim(value=3.2, units='in'),
                Coord.Dim(value=8, units='in'),
                4,
                4,
            ),
            myPfc.interpretTrac(b'T23 '),
        )

    def test_03(self):
        """TestFILMRead.test_03(): PhysFilmCfg.interpretTrac() left/right."""
        # 2     E2E   -4--  PF2   D200
        myPfc = self._fc[b'2\x00\x00\x00']
        self.assertEqual(
            (
                Coord.Dim(value=0.0, units='in'),
                Coord.Dim(value=1.2, units='in'),
                0,
                1,
            ),
            myPfc.interpretTrac(b'LHT1'),
        )
        self.assertEqual(
            (
                Coord.Dim(value=1.2, units='in'),
                Coord.Dim(value=2.4, units='in'),
                1,
                1,
            ),
            myPfc.interpretTrac(b'RHT1'),
        )

    def test_04(self):
        """TestFILMRead.test_04(): PhysFilmCfg.genTracks() produces edge dimensions."""
        # 2     E2E   -4--  PF2   D200
        myPfc = self._fc[b'2\x00\x00\x00']
#        print()
#        print([(t.left, t.right) for t in myPfc.genTracks()])
        self.assertEqual(
            [
                (Coord.Dim(value=0.0, units='in'), Coord.Dim(value=2.4, units='in')),
                (Coord.Dim(value=2.4, units='in'), Coord.Dim(value=3.2, units='in')),
                (Coord.Dim(value=3.2, units='in'), Coord.Dim(value=5.6, units='in')),
                (Coord.Dim(value=5.6, units='in'), Coord.Dim(value=8, units='in')),
            ],
            [(t.left, t.right) for t in myPfc.genTracks()], 
        )

    def test_09(self):
        """TestFILMRead.test_09(): PhysFilmCfg.interpretTrac() fails."""
        # 2     E2E   -4--  PF2   D200
        myPfc = self._fc[b'2\x00\x00\x00']
#        print('HI', FILMCfg.ExceptionPhysFilmCfg, myPfc.interpretTrac(b''))
        self.assertRaises(FILMCfg.ExceptionPhysFilmCfg, myPfc.interpretTrac, b'')
        self.assertRaises(FILMCfg.ExceptionPhysFilmCfg, myPfc.interpretTrac, b'T9  ')
        self.assertRaises(FILMCfg.ExceptionPhysFilmCfg, myPfc.interpretTrac, b'T19 ')
        
    def test_10(self):
        """TestFILMRead.test_10(): PhysFilmCfg.retFILMDest() using curve destination b'1' and b'2'."""
        self.assertEqual(b'1\x00\x00\x00', self._fc.retFILMDest(Mnem.Mnem(b'1'), b'1').name)
        self.assertEqual(b'2\x00\x00\x00', self._fc.retFILMDest(Mnem.Mnem(b'2'), b'2').name)

    def test_11(self):
        """TestFILMRead.test_11(): PhysFilmCfg.retFILMDest() using curve destination b'BOTH'."""
#        print('myPfc', self._fc.retFILMDest(b'1', b'BOTH'))
        self.assertEqual(b'1\x00\x00\x00', self._fc.retFILMDest(Mnem.Mnem(b'1'), b'BOTH').name)
#        print('myPfc', self._fc.retFILMDest(b'1', b'BOTH'))
        self.assertEqual(b'2\x00\x00\x00', self._fc.retFILMDest(Mnem.Mnem(b'2'), b'BOTH').name)

    def test_12(self):
        """TestFILMRead.test_12(): PhysFilmCfg.retFILMDest() using curve destination b'ALL'."""
        self.assertEqual(b'1\x00\x00\x00', self._fc.retFILMDest(Mnem.Mnem(b'1'), b'ALL').name)
        self.assertEqual(b'2\x00\x00\x00', self._fc.retFILMDest(Mnem.Mnem(b'2'), b'ALL').name)

    def test_13(self):
        """TestFILMRead.test_13(): PhysFilmCfg.retFILMDest() using curve destination b'NEIT'."""
        self.assertTrue(self._fc.retFILMDest(Mnem.Mnem(b'1'), b'NEIT') is None)
        self.assertTrue(self._fc.retFILMDest(Mnem.Mnem(b'2'), b'NEIT') is None)

    def test_14(self):
        """TestFILMRead.test_14(): PhysFilmCfg.retFILMDest() using curve destination b'12'."""
        self.assertEqual(
            b'1\x00\x00\x00',
            self._fc.retFILMDest(
                Mnem.Mnem(b'1'),
                Mnem.Mnem(b'12')
            ).name
        )
        self.assertEqual(
            b'2\x00\x00\x00',
            self._fc.retFILMDest(
                Mnem.Mnem(b'2'),
                Mnem.Mnem(b'12')
            ).name
        )

    def test_15(self):
        """TestFILMRead.test_15(): PhysFilmCfg.retFILMDest() when film and specific curve destination mismatches."""
        self.assertTrue(self._fc.retFILMDest(Mnem.Mnem(b'1'), Mnem.Mnem(b'2')) is None)
        self.assertTrue(self._fc.retFILMDest(Mnem.Mnem(b'2'), Mnem.Mnem(b'1')) is None)

    def test_20(self):
        """TestFILMRead.test_20(): PhysFilmCfg.interpretTrac() using curve destination b'1' and b'2', track b'T1  '."""
        self.assertEqual(
            (
                Coord.Dim(value=0.0, units='in'),
                Coord.Dim(value=2.4, units='in'),
                0,
                2,
            ),
            self._fc.interpretTrac(Mnem.Mnem(b'1'), Mnem.Mnem(b'1'), b'T1  ')
        )
        self.assertEqual(
            (
                Coord.Dim(value=0.0, units='in'),
                Coord.Dim(value=2.4, units='in'),
                0,
                2,
            ),
            self._fc.interpretTrac(Mnem.Mnem(b'2'), Mnem.Mnem(b'2'), b'T1  ')
        )

    def test_21(self):
        """TestFILMRead.test_21(): PhysFilmCfg.interpretTrac() using curve destination b'1' and b'2' mismatches, track b'T1  '."""
        self.assertTrue(self._fc.interpretTrac(Mnem.Mnem(b'2'), Mnem.Mnem(b'1'), b'T1  ') is None)
        self.assertTrue(self._fc.interpretTrac(Mnem.Mnem(b'1'), Mnem.Mnem(b'2'), b'T1  ') is None)

    def test_30(self):
        """TestFILMRead.test_30(): PhysFilmCfgLISRead._retTracks()."""
#        print()
#        print(self._fc.keys())
#        print(self._fc[Mnem.Mnem(b'1')]._retTracks(b'EEE ', b'----'))
        self.assertEqual(4, len(self._fc[Mnem.Mnem(b'1')]._retTracks(b'EEE ', b'----')))
        self.assertEqual(4, len(self._fc[Mnem.Mnem(b'1')]._retTracks(b'EEE ', b'--- ')))
        
    def test_31(self):
        """TestFILMRead.test_31(): PhysFilmCfgLISRead._retTracks() fails with bad GCOD (raises)."""
#        self.assertTrue(self._fc[Mnem.Mnem(b'1')]._retTracks(b'WTF ', b'----') is None)
        self.assertRaises(FILMCfg.ExceptionFILMCfg, self._fc[Mnem.Mnem(b'1')]._retTracks, b'WTF ', b'----')
        
    def test_32(self):
        """TestFILMRead.test_32(): PhysFilmCfgLISRead._retTracks() fails with bad GDEC (raises)."""
#        self.assertTrue(self._fc[Mnem.Mnem(b'1')]._retTracks(b'EEE ', b'XXXX') is None)
        self.assertRaises(FILMCfg.ExceptionFILMCfg, self._fc[Mnem.Mnem(b'1')]._retTracks, b'EEE ', b'XXXX')
        
    def test_40(self):
        """TestFILMRead.test_40(): PhysFilmCfgLISRead.supportedFilmTracks()."""
#        print()
#        print(self._fc[Mnem.Mnem(b'1')].supportedFilmTracks())
        self.assertEqual(
            [
                (b'BBB ', b'----'),
                (b'E20 ', b'-4--'),
                (b'E2E ', b'-1--'),
                (b'E2E ', b'-2--'),
                (b'E3E ', b'-3--'),
                (b'E4E ', b'-4--'),
                (b'EBE ', b'----'),
                (b'EEB ', b'----'),
                (b'EEE ', b'----'),
                (b'LLLL', b'1111'),
            ],
            self._fc[Mnem.Mnem(b'1')].supportedFilmTracks(),
        )

class TestFILMReadFourTrack(BaseTestClasses.TestBaseFile):
    """Tests reading a FILM table with four tracks."""
    def setUp(self):
        """Set up Typical FILM record
Table record (type 34) type: FILM
MNEM  GCOD  GDEC  DEST  DSCA
-----------------------------
A     LLLL  1111  PFA   D200  
"""
        myByFilm = b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    A\x00\x00\x00' \
                    + b'EA\x04\x00GCOD    LLLL' \
                    + b'EA\x04\x00GDEC    1111' \
                    + b'EA\x04\x00DEST    PFA ' \
                    + b'EA\x04\x00DSCA    D200'
        myFi = self._retFileSinglePr(myByFilm)
        self._fc = FILMCfg.FilmCfgLISRead(LogiRec.LrTableRead(myFi))
        self.assertTrue(Mnem.Mnem(b'A   ') in self._fc)
        self.assertFalse(Mnem.Mnem(b'B   ') in self._fc)

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestFILMReadFourTrack.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestFILMReadFourTrack.test_01(): Constructor."""
        self.assertEqual(1, len(self._fc))
        self.assertEqual([b'A\x00\x00\x00',], sorted(list(self._fc.keys())))

    def test_02(self):
        """TestFILMReadFourTrack.test_02(): interpretTrac()."""
        myPfc = self._fc[Mnem.Mnem(b'A\x00\x00\x00')]
#        print()
#        print('FD', myPfc.interpretTrac(b'FD  '))
#        print('F1', myPfc.interpretTrac(b'F1  '))
        self.assertEqual(
            (
                Coord.Dim(value=0.0, units='in'),
                Coord.Dim(value=1.0, units='in'),
                0, # Half track start
                2, # Half track span
            ),
            myPfc.interpretTrac(b'FD  '),
        )
        self.assertEqual(
            (
                Coord.Dim(value=1.0, units='in'),
                Coord.Dim(value=2.75, units='in'),
                2, # Half track start
                2, # Half track span
            ),
            myPfc.interpretTrac(b'F1  '),
        )
        self.assertEqual(
            (
                Coord.Dim(value=2.75, units='in'),
                Coord.Dim(value=4.5, units='in'),
                4, # Half track start
                2, # Half track span
            ),
            myPfc.interpretTrac(b'F2  '),
        )
        self.assertEqual(
            (
                Coord.Dim(value=4.5, units='in'),
                Coord.Dim(value=6.25, units='in'),
                6, # Half track start
                2, # Half track span
            ),
            myPfc.interpretTrac(b'F3  '),
        )
        self.assertEqual(
            (
                Coord.Dim(value=6.25, units='in'),
                Coord.Dim(value=8.0, units='in'),
                8, # Half track start
                2, # Half track span
            ),
            myPfc.interpretTrac(b'F4  '),
        )



class TestFILMRead_Fail(BaseTestClasses.TestBaseFile):
    """Tests failing to read a FILM table."""
    def setUp(self):
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestFILMRead_Fail.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestFILMRead_Fail.test_01(): Constructor - not a type 34 Logical Record."""
        myByFilm = b' \x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1\x00\x00\x00' \
                    + b'EA\x04\x00GCOD    E20 ' \
                    + b'EA\x04\x00GDEC    -4--' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    2\x00\x00\x00' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D200'
        myFi = self._retFileSinglePr(myByFilm)
        self.assertRaises(FILMCfg.ExceptionFilmCfgLISRead, FILMCfg.FilmCfgLISRead, LogiRec.LrTableRead(myFi))

    def test_02(self):
        """TestFILMRead_Fail.test_02(): Constructor - not a FILM table."""
        myByFilm = b'"\x00' \
            + b'IA\x04\x00TYPE    NOTF' \
                + b'\x00A\x04\x00MNEM    1\x00\x00\x00' \
                    + b'EA\x04\x00GCOD    E20 ' \
                    + b'EA\x04\x00GDEC    -4--' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    2\x00\x00\x00' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D200'
        myFi = self._retFileSinglePr(myByFilm)
        self.assertRaises(FILMCfg.ExceptionFilmCfgLISRead, FILMCfg.FilmCfgLISRead, LogiRec.LrTableRead(myFi))
#        self._fc = FILMCfg.FilmCfgLISRead(LogiRec.LrTableRead(myFi))

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFILMRead))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFILMReadFourTrack))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFILMRead_Fail))
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
