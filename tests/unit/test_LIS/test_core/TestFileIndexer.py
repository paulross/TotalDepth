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
"""Tests the file indexer.
"""

__author__  = 'Paul Ross'
__date__    = '10 Feb 2011'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'

import os
import sys
import time
import logging

from TotalDepth.LIS.core import FileIndexer
from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import LisGen

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import BaseTestClasses
######################
# Section: Unit tests.
######################
import unittest


class TestPlotRecordSet(unittest.TestCase):
    """Tests PlotRecordSet."""
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_00(self):
        """TestPlotRecordSet.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestPlotRecordSet.test_01(): Construction."""
        myPrs = FileIndexer.PlotRecordSet()
        self.assertFalse(myPrs.canPlotFromInternalRecords())
        self.assertFalse(myPrs.canPlotFromExternalRecords())

    def test_02(self):
        """TestPlotRecordSet.test_02(): tellFilm setter and getter."""
        myPrs = FileIndexer.PlotRecordSet()
        self.assertFalse(myPrs.canPlotFromInternalRecords())
        self.assertFalse(myPrs.canPlotFromExternalRecords())
        self.assertTrue(myPrs.tellFilm is None)
        myPrs.tellFilm = 1
        self.assertEqual(1, myPrs.tellFilm)
        self.assertFalse(myPrs.canPlotFromInternalRecords())
        self.assertFalse(myPrs.canPlotFromExternalRecords())

    def test_03(self):
        """TestPlotRecordSet.test_03(): tellPres setter and getter."""
        myPrs = FileIndexer.PlotRecordSet()
        self.assertFalse(myPrs.canPlotFromInternalRecords())
        self.assertFalse(myPrs.canPlotFromExternalRecords())
        self.assertTrue(myPrs.tellPres is None)
        myPrs.tellPres = 1
        self.assertEqual(1, myPrs.tellPres)
        self.assertFalse(myPrs.canPlotFromInternalRecords())
        self.assertFalse(myPrs.canPlotFromExternalRecords())

    def test_04(self):
        """TestPlotRecordSet.test_04(): tellArea setter and getter."""
        myPrs = FileIndexer.PlotRecordSet()
        self.assertFalse(myPrs.canPlotFromInternalRecords())
        self.assertFalse(myPrs.canPlotFromExternalRecords())
        self.assertTrue(myPrs.tellArea is None)
        myPrs.tellArea = 1
        self.assertEqual(1, myPrs.tellArea)
        self.assertFalse(myPrs.canPlotFromInternalRecords())
        self.assertFalse(myPrs.canPlotFromExternalRecords())

    def test_05(self):
        """TestPlotRecordSet.test_05(): tellPip setter and getter."""
        myPrs = FileIndexer.PlotRecordSet()
        self.assertFalse(myPrs.canPlotFromInternalRecords())
        self.assertFalse(myPrs.canPlotFromExternalRecords())
        self.assertTrue(myPrs.tellPip is None)
        myPrs.tellPip = 1
        self.assertEqual(1, myPrs.tellPip)
        self.assertFalse(myPrs.canPlotFromInternalRecords())
        self.assertFalse(myPrs.canPlotFromExternalRecords())

    def test_06(self):
        """TestPlotRecordSet.test_06(): logPass setter and getter."""
        myPrs = FileIndexer.PlotRecordSet()
        self.assertFalse(myPrs.canPlotFromInternalRecords())
        self.assertFalse(myPrs.canPlotFromExternalRecords())
        self.assertTrue(myPrs.logPass is None)
        myPrs.logPass = '1'
        self.assertEqual('1', myPrs.logPass)
        self.assertFalse(myPrs.canPlotFromInternalRecords())
        self.assertTrue(myPrs.canPlotFromExternalRecords())

    def test_10(self):
        """TestPlotRecordSet.test_10(): value()."""
        myPrs = FileIndexer.PlotRecordSet()
        self.assertFalse(myPrs.canPlotFromInternalRecords())
        self.assertFalse(myPrs.canPlotFromExternalRecords())
        myPrs.tellFilm = 1
        myPrs.tellPres = 1
        myPrs.logPass = '1'
        self.assertTrue(myPrs)

    def test_11(self):
        """TestPlotRecordSet.test_11(): value() and clear()."""
        myPrs = FileIndexer.PlotRecordSet()
        self.assertFalse(myPrs.canPlotFromInternalRecords())
        self.assertFalse(myPrs.canPlotFromExternalRecords())
        myPrs.tellFilm = 1
        myPrs.tellPres = 1
        myPrs.logPass = '1'
        self.assertTrue(myPrs)
        myPrs.clear()
        self.assertFalse(myPrs.canPlotFromInternalRecords())
        self.assertFalse(myPrs.canPlotFromExternalRecords())

class TestFileIndexerBase(BaseTestClasses.TestBaseLogPass):
    """Base class to create LIS files to index."""
    def _retFileHead(self):
        """Returns a single Physical Record encapsulating as File Head."""
        return self._retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileHead)
    
    def _retFileTail(self):
        """Returns a single Physical Record encapsulating as File Tail."""
        return self._retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileTail)
        
    def _retTapeHead(self):
        """Returns a single Physical Record encapsulating as Tape Head."""
        return self._retSinglePr(LisGen.TapeReelHeadTailDefault.lrBytesTapeHead)

    def _retTapeTail(self):
        """Returns a single Physical Record encapsulating as Tape Tail."""
        return self._retSinglePr(LisGen.TapeReelHeadTailDefault.lrBytesTapeTail)

    def _retReelHead(self):
        """Returns a single Physical Record encapsulating as Reel Head."""
        return self._retSinglePr(LisGen.TapeReelHeadTailDefault.lrBytesReelHead)

    def _retReelTail(self):
        """Returns a single Physical Record encapsulating as Reel Tail."""
        return self._retSinglePr(LisGen.TapeReelHeadTailDefault.lrBytesReelTail)
    
    def _retLrRandom(self, theLrType, theLen=None):
        """Returns a Logical Record with random content of specified type and
        length of theLen. If theLen is absent a random length of up to 32kB is
        chosen."""
        #print('_retLrRandom()', theLrType)
        return bytes([theLrType, 0]) + LisGen.randomBytes(theLen)
    
class TestFileIndexerCtor(TestFileIndexerBase):
    """Tests FileIndex construction."""
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
        """TestFileIndexer.test_00(): Empty file."""
        myF = self._retFileFromBytes(b'')
        myIdx = FileIndexer.FileIndex(myF)
        
class TestIndexDelimiter(TestFileIndexerBase):
    """Tests FileIndex with EFLR records that are delimiter."""
    def test_00(self):
        """TestIndexEflrHeadTail.test_00(): File head and tail."""
        myFile = self._retFileFromBytes(self._retFileHead()+self._retFileTail())
        myIdx = FileIndexer.FileIndex(myFile)
        #print()
        #print(myIdx._idx)
        self.assertEqual(2, len(myIdx))
        self.assertEqual([128, 129], myIdx.lrTypeS)

    def test_01(self):
        """TestIndexEflrHeadTail.test_01(): Tape head and tail."""
        myFile = self._retFileFromBytes(self._retTapeHead()+self._retTapeTail())
        myIdx = FileIndexer.FileIndex(myFile)
        #print()
        #print(myIdx._idx)
        self.assertEqual(2, len(myIdx))
        self.assertEqual([130, 131], myIdx.lrTypeS)

    def test_02(self):
        """TestIndexEflrHeadTail.test_02(): Reel head and tail."""
        myFile = self._retFileFromBytes(self._retReelHead()+self._retReelTail())
        myIdx = FileIndexer.FileIndex(myFile)
        #print()
        #print(myIdx._idx)
        self.assertEqual(2, len(myIdx))
        self.assertEqual([132, 133], myIdx.lrTypeS)

    def test_03(self):
        """TestIndexEflrHeadTail.test_03(): Reel/Tape/File head and tail."""
        myFile = self._retFileFromBytes(
            self._retReelHead()
            + self._retTapeHead()
            + self._retFileHead()
            + self._retFileTail()
            + self._retTapeTail()
            + self._retReelTail()
        )
        myIdx = FileIndexer.FileIndex(myFile)
        #print()
        #print(myIdx._idx)
        self.assertEqual(6, len(myIdx))
        #print(myIdx.lrTypeS)
        self.assertEqual([132, 130, 128, 129, 131, 133], myIdx.lrTypeS)

class TestIndexMarker(TestFileIndexerBase):
    """Tests indexing of marker records such as EOM etc."""
    def test_00(self):
        """TestIndexMarker.test_00(): All marker records."""
        myFile = self._retFileFromBytes(
            self._retSinglePr(b'\x89\x00')
            + self._retSinglePr(b'\x8A\x00')
            + self._retSinglePr(b'\x8B\x00')
            + self._retSinglePr(b'\x8D\x00')
        )
        myIdx = FileIndexer.FileIndex(myFile)
        #print()
        #print(myIdx._idx)
        self.assertEqual(4, len(myIdx))
        #print(myIdx.lrTypeS)
        self.assertEqual([137, 138, 139, 141], myIdx.lrTypeS)

class TestIndexUnknownIntFormat(TestFileIndexerBase):
    """Tests indexing of Logical Records of unknown internal format."""
    def test_00(self):
        """TestIndexUnknownIntFormat.test_00(): Logical Records of unknown internal format, random lengths."""
        #print()
        #print(LogiRec.LR_TYPE_UNKNOWN_INTERNAL_FORMAT)
        myB = b''
        for aType in LogiRec.LR_TYPE_UNKNOWN_INTERNAL_FORMAT:
            myB += self._retSinglePr(self._retLrRandom(aType))
        myFile = self._retFileFromBytes(myB)
        myIdx = FileIndexer.FileIndex(myFile)
        #print(myIdx._idx)
        self.assertEqual(len(LogiRec.LR_TYPE_UNKNOWN_INTERNAL_FORMAT), len(myIdx))
        #print(myIdx.lrTypeS)
        self.assertEqual(list(LogiRec.LR_TYPE_UNKNOWN_INTERNAL_FORMAT), myIdx.lrTypeS)

class TestIndex_genPlotRecords(TestFileIndexerBase):
    """Tests indexer genPlotRecords()."""
    def _retLogPassGen(self):
        #print()
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4*4))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 66, 60))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'.1IN'))
        #print('myEbs.lisByteList()')
        #pprint.pprint(myEbs.lisByteList())
        myLp = LisGen.LogPassGen(
            myEbs,
            # Channel list
            [
                LisGen.Channel(
                    LisGen.ChannelSpec(
                        b'TEST', b'ServID', b'ServOrdN', b'FEET',
                        45310011, 256, 16, 4, 68
                    ),
                    LisGen.ChValsConst(fOffs=0, waveLen=4, mid=0.0, amp=1.0, numSa=1, noise=None),
                ),
            ],
            xStart=10000.0 * 120,
            xRepCode=68,
            xNoise=None,
        )
        return myLp

    def _retFileIndexSingleChannel(self):
        myBa = bytearray(self._retFileHead())
        # Add a log pass
        myLp = self._retLogPassGen()
        # Stick the DFSR on the array
        myBa += self.retPrS(myLp.lrBytesDFSR())
        # Add some logical records
        for i in range(4):
            myBa += self.retPrS(myLp.lrBytes(i*100, 100))
        myBa += self._retFileTail()
        myFile = self._retFileFromBytes(myBa)
        myIdx = FileIndexer.FileIndex(myFile)
        return myFile, myIdx
        
    def test_00(self):
        """TestIndex_genPlotRecords.test_00(): Test genPlotRecords()."""
        # TODO: Should add testing of Index.FileIndex generators
#        assert(0), 'Should add testing of Index.FileIndex generators'
        print('Should add testing of Index.FileIndex generators\n')
        myBa = bytearray(self._retFileHead())
        # Add a log pass
        myLp = self._retLogPassGen()
        # Stick the DFSR on the array
        myBa += self.retPrS(myLp.lrBytesDFSR())
        # Add some logical records
        for i in range(4):
            myBa += self.retPrS(myLp.lrBytes(i*100, 100))
        myBa += self._retFileTail()
        myFile, myIdx = self._retFileIndexSingleChannel()
        print('myIdx.longDesc():')
        print(myIdx.longDesc())
        self.assertEqual(3, len(myIdx))
        self.assertEqual(
            [
                LogiRec.LR_TYPE_FILE_HEAD,
                LogiRec.LR_TYPE_DATA_FORMAT,
                LogiRec.LR_TYPE_FILE_TAIL,
            ],
            myIdx.lrTypeS,
        )
        myRecs = list(myIdx.genAll())
        print('Index genAll() [{:d}]:'.format(len(myRecs)))
        print(myRecs)
        self.assertEqual(3, len(myRecs))
        myPasses = list(myIdx.genLogPasses())
        print('')
        print('Index genLogPasses() [{:d}]:'.format(len(myPasses)))
        print(myPasses)
        self.assertEqual(1, len(myPasses))
        print('')
        print('Index pass[0].tocStr():')
        print(myPasses[0].tocStr())
        print('')
        print('Index pass[0].logPass.longStr():')
        print(myPasses[0].logPass.longStr())

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotRecordSet))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileIndexerCtor))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIndexDelimiter))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIndexMarker))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIndexUnknownIntFormat))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIndex_genPlotRecords))
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
