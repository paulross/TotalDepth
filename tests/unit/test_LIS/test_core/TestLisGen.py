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
"""Tests the LIS generator.
"""
import pytest

__author__  = 'Paul Ross'
__date__    = '14 Feb 2011'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'

#import pprint
import sys
import time
import logging
import pprint

from TotalDepth.LIS.core import LisGen
from TotalDepth.LIS.core import Units
from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import RepCode

######################
# Section: Unit tests.
######################
import unittest

class TestLisGenBase(unittest.TestCase):
    """Base class for test cases in this module."""
    def _assertInRange(self, v, min, max):
        """Asserts v is in range min/max (inclusive) i.e. min <= v <= max."""
        self.assertTrue(v >= min, '{:s} not >= to {:s}'.format(str(v), str(min)))
        self.assertTrue(v <= max, '{:s} not <= to {:s}'.format(str(v), str(max)))


@pytest.mark.slow
class TestRandom(TestLisGenBase):
    """Tests ..."""
    RANDOM_TEST_COUNT = 8 * 1024
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestRandom: Tests setUp() and tearDown()."""
        pass

    def test_00_00(self):
        """TestRandom.test_00_00(): Random bytes, 8 bytes long."""
        for i in range(self.RANDOM_TEST_COUNT):
            myM = LisGen.randomBytes(8)
            self.assertEqual(8, len(myM))
            for c in myM:
                self.assertTrue(c >= 0 and c < 256)

    def test_00_01(self):
        """TestRandom.test_00_01(): Random bytes, default length."""
        for i in range(self.RANDOM_TEST_COUNT // 1024):
            myM = LisGen.randomBytes()
            self.assertTrue(len(myM) > 0 and len(myM) <= 32*1024)
            for c in myM:
                self.assertTrue(c >= 0 and c < 256)

    def test_01(self):
        """TestRandom.test_01(): Random units."""
        for i in range(self.RANDOM_TEST_COUNT):
            self.assertTrue(LisGen.randomUnit() in Units.units(theCat=None))

    def test_02(self):
        """TestRandom.test_02(): Random mnem."""
        for i in range(self.RANDOM_TEST_COUNT):
            myM = LisGen.randomMnem()
            self.assertEqual(4, len(myM))
            for c in myM:
                self.assertTrue(c >= 65 and c < 65+26)

    def test_03_00(self):
        """TestRandom.test_03_00(): Random sting with randomString()."""
        for i in range(self.RANDOM_TEST_COUNT):
            myS = LisGen.randomString()
            self.assertTrue(len(myS) <= LisGen.RANDOM_STRING_DEFAULT_MAX_LENGTH)
            for c in myS:
                self.assertTrue(c in LisGen.RANDOM_STRING_CHARS)

    def test_03_01(self):
        """TestRandom.test_03_01(): Random sting with randomString(16)."""
        for i in range(self.RANDOM_TEST_COUNT):
            myS = LisGen.randomString(16)
            self.assertTrue(len(myS) <= 16)
            for c in myS:
                self.assertTrue(c in LisGen.RANDOM_STRING_CHARS)

class TestPhysRec(TestLisGenBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestPhysRec: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestPhysRec.test_00(): retSinglePr()."""
        self.assertEqual(b'', LisGen.retSinglePr(b''))
        self.assertEqual(b'\x00\x05\x00\x00\x01', LisGen.retSinglePr(b'\x01'))

    def test_01(self):
        """TestPhysRec.test_01(): retPrS()."""
        self.assertEqual(
              b'\x00\x0c\x00\x01\x00\x01\x02\x03\x04\x05\x06\x07'
            + b'\x00\x0c\x00\x02\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f',
            LisGen.retPrS(bytes(list(range(16))), 8)
        )
        self.assertEqual(
              b'\x00\x0c\x00\x01\x00\x01\x02\x03\x04\x05\x06\x07'
            + b'\x00\x0c\x00\x03\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
            + b'\x00\x0c\x00\x02\x10\x11\x12\x13\x14\x15\x16\x17',
            LisGen.retPrS(bytes(list(range(24))), 8)
        )

class TestFileTapeReel(TestLisGenBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestPhysRec: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestPhysRec.test_00(): File Head."""
        self.assertEqual(
            b'\x00>\x00\x00\x80\x00RUNOne.lis\x00\x00SubLevVers num78/03/15\x00 1024\x00\x00AB\x00\x00Prev name.',
            LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileHead)
        )

    def test_01(self):
        """TestPhysRec.test_01(): File Tail."""
        self.assertEqual(
            b'\x00>\x00\x00\x81\x00RUNOne.lis\x00\x00SubLevVers num78/03/15\x00 1024\x00\x00AB\x00\x00Prev name.',
            LisGen.retSinglePr(LisGen.FileHeadTailDefault.lrBytesFileTail)
        )

    def test_02(self):
        """TestPhysRec.test_02(): Tape Head."""
        self.assertEqual(
            b'\x00\x84\x00\x00\x82\x00SERVCE\x00\x00\x00\x00\x00\x0079/06/15\x00\x00ORGN\x00\x00TAPENAME\x00\x0001\x00\x00PrevName\x00\x00_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123',
            LisGen.retSinglePr(LisGen.TapeReelHeadTailDefault.lrBytesTapeHead)
        )

    def test_03(self):
        """TestPhysRec.test_03(): Tape Tail."""
        self.assertEqual(
            b'\x00\x84\x00\x00\x83\x00SERVCE\x00\x00\x00\x00\x00\x0079/06/15\x00\x00ORGN\x00\x00TAPENAME\x00\x0001\x00\x00PrevName\x00\x00_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123',
            LisGen.retSinglePr(LisGen.TapeReelHeadTailDefault.lrBytesTapeTail)
        )

    def test_04(self):
        """TestPhysRec.test_04(): Reel Head."""
        self.assertEqual(
            b'\x00\x84\x00\x00\x84\x00SERVCE\x00\x00\x00\x00\x00\x0079/06/15\x00\x00ORGN\x00\x00TAPENAME\x00\x0001\x00\x00PrevName\x00\x00_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123',
            LisGen.retSinglePr(LisGen.TapeReelHeadTailDefault.lrBytesReelHead)
        )

    def test_05(self):
        """TestPhysRec.test_05(): Reel Tail."""
        self.assertEqual(
            b'\x00\x84\x00\x00\x85\x00SERVCE\x00\x00\x00\x00\x00\x0079/06/15\x00\x00ORGN\x00\x00TAPENAME\x00\x0001\x00\x00PrevName\x00\x00_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123',
            LisGen.retSinglePr(LisGen.TapeReelHeadTailDefault.lrBytesReelTail)
        )

class TestTableGenCONS(TestLisGenBase):
    """Tests CONS table generation."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestTableGenCONS: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestTableGenCONS.test_00(): Simple CONS table."""
        #print()
        myTg = LisGen.TableGen(
            34,
            b'CONS',
            [b'MNEM', b'ALLO', b'PUNI', b'TUNI', b'VALU'],
            theTable=[
                    [b'SPAM', b'ALLO', b'TINS', b'CANS', (16.0, b'TON ')],
                    [b'EGGS', b'ALLO', b'CART', b'SHED', (12.5, b'    ')],
                    [b'TEXT', b'ALLO', b'    ', b'    ', 'SOME STRING...'],
                ],
        )
        myB = myTg.lrBytes()
        #print(myB)
        self.assertEqual(
            b'\x22\x00\x49\x41\x04\x00TYPECONS    '
            + b'\x00A\x04\x00MNEM    SPAMEA\x04\x00ALLO    ALLOEA\x04\x00PUNI    TINSEA\x04\x00TUNI    CANSED\x04\x00VALUTON B\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    EGGSEA\x04\x00ALLO    ALLOEA\x04\x00PUNI    CARTEA\x04\x00TUNI    SHEDED\x04\x00VALU    Bd\x00\x00'
            + b'\x00A\x04\x00MNEM    TEXTEA\x04\x00ALLO    ALLOEA\x04\x00PUNI        EA\x04\x00TUNI        EA\x0e\x00VALU    SOME STRING...',
            myB,
        )
        myF = LisGen.retFileFromBytes(LisGen.retPrS(myB))
        myLr = LogiRec.LrTableRead(myF)
        #print(myLr)
        #print('myLr.colLabels()', myLr.colLabels())
        #print('myLr.rowLabels()', myLr.rowLabels())
        self.assertEqual(5, len(myLr.colLabels()))
        self.assertEqual(3, len(myLr.rowLabels()))

    def test_01(self):
        """TestTableGenCONS.test_01(): Simple CONS table raises on empty."""
        #print()
        myTg = LisGen.TableGen(
            34,
            b'CONS',
            [b'MNEM', b'ALLO', b'PUNI', b'TUNI', b'VALU'],
            theTable=None,
        )
        self.assertRaises(LisGen.ExceptionLisGen, myTg.lrBytes)

class TestTableGenRandomCONS(TestLisGenBase):
    """Tests random table generation."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestTableGenRandomCONS: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestTableGenRandomCONS.test_00(): 8 rows."""
        #print()
        numRows = 8
        myTg = LisGen.TableGenRandomCONS(numRows)
        myB = myTg.lrBytes()
        #print(myB)
        #self.assertEqual(b'', myB)
        myF = LisGen.retFileFromBytes(LisGen.retPrS(myB))
        myLr = LogiRec.LrTableRead(myF)
        #print(myLr)
        #print('myLr.colLabels()', myLr.colLabels())
        #print('myLr.rowLabels()', myLr.rowLabels())
        self.assertEqual(5, len(myLr.colLabels()))
        self.assertEqual(numRows, len(myLr.rowLabels()))

    def test_01(self):
        """TestTableGenRandomCONS.test_01(): 256 rows."""
        #print()
        numRows = 256
        myTg = LisGen.TableGenRandomCONS(numRows)
        myB = myTg.lrBytes()
        #print(myB)
        #self.assertEqual(b'', myB)
        myF = LisGen.retFileFromBytes(LisGen.retPrS(myB))
        myLr = LogiRec.LrTableRead(myF)
        #print(myLr)
        #print('myLr.colLabels()', myLr.colLabels())
        #print('myLr.rowLabels()', myLr.rowLabels())
        self.assertEqual(5, len(myLr.colLabels()))
        self.assertEqual({b'MNEM', b'ALLO', b'PUNI', b'TUNI', b'VALU'}, myLr.colLabels())
        # NOTE: Problem here is that we might generate duplicate row names
        # and they will be discarded on table construction. So the actual number
        # of rows, given random construction, will <= the demanded number of rows.
        self.assertTrue(len(myLr.rowLabels()) <= numRows)

    def test_02(self):
        """TestTableGenRandomCONS.test_02(): TableGenRandom() with unknown column, 8 rows."""
        #print()
        numRows = 8
        myTg = LisGen.TableGenRandom(
            34,
            b'CONS',
            [b'MNEM', b'UNKN',],
            numRows
        )
        myB = myTg.lrBytes()
        #print(myB)
        #self.assertEqual(b'', myB)
        myF = LisGen.retFileFromBytes(LisGen.retPrS(myB))
        myLr = LogiRec.LrTableRead(myF)
        #print(myLr)
        #print('myLr.colLabels()', myLr.colLabels())
        #print('myLr.rowLabels()', myLr.rowLabels())
        self.assertEqual(2, len(myLr.colLabels()))
        self.assertEqual({b'MNEM', b'UNKN'}, myLr.colLabels())
        self.assertEqual(numRows, len(myLr.rowLabels()))


@pytest.mark.slow
class TestChVals(TestLisGenBase):
    """Tests channel value generation."""
    TESTS = 1024*8
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestChVals: Tests setUp() and tearDown()."""
        myC = LisGen.ChValsBase()
        self.assertRaises(NotImplementedError, myC.val, 0)
    
    def test_00_00(self):
        """TestChVals.test_00_00(): Constant value."""
        myCv = LisGen.ChValsConst(fOffs=0, waveLen=1, mid=0, amp=1, numSa=1, noise=None)
        #myCv = LisGen.ChValsConst(0, 1, 0, 1, 1, None)
        for i in range(self.TESTS):
            self.assertEqual(0, myCv.val(i))
    
    def test_00_01(self):
        """TestChVals.test_00_01(): Constant value with noise."""
        myCv = LisGen.ChValsConst(fOffs=0, waveLen=1, mid=0, amp=1, numSa=1, noise=0.5)
        for i in range(self.TESTS):
            self._assertInRange(myCv.val(i), -0.25, +0.25)
    
    def test_01_00(self):
        """TestChVals.test_01_00(): Random value."""
        myCv = LisGen.ChValsRand(fOffs=0, waveLen=1, mid=0, amp=1, numSa=1, noise=None)
        #myCv = LisGen.ChValsConst(0, 1, 0, 1, 1, None)
        for i in range(self.TESTS):
            self._assertInRange(myCv.val(i), 0.0, 1.0)
    
    def test_02_00(self):
        """TestChVals.test_02_00(): Random normal distribution."""
        #print()
        myCv = LisGen.ChValsRandNormal(fOffs=0, waveLen=1, mid=0, amp=1, numSa=1, noise=None)
        for i in range(self.TESTS):
            v = myCv.val(i)
            #print(v)
            #self._assertInRange(v, -0.25, +0.25)
    
    def test_02_01(self):
        """TestChVals.test_02_01(): Random normal distribution with noise."""
        #print()
        myCv = LisGen.ChValsRandNormal(fOffs=0, waveLen=1, mid=0, amp=1, numSa=1, noise=0.5)
        for i in range(self.TESTS):
            v = myCv.val(i)
            #print(v)
            #self._assertInRange(v, -0.25, +0.25)
    
    def test_03_00(self):
        """TestChVals.test_02_00(): Log normal distribution."""
        #print()
        myCv = LisGen.ChValsRandLogNormal(fOffs=0, waveLen=1, mid=0, amp=1, numSa=1, noise=None)
        for i in range(self.TESTS):
            v = myCv.val(i)
            #print(v)
            #self._assertInRange(v, -0.25, +0.25)
    
    def test_03_01(self):
        """TestChVals.test_02_01(): Log normal distribution with noise."""
        #print()
        myCv = LisGen.ChValsRandLogNormal(fOffs=0, waveLen=1, mid=0, amp=1, numSa=1, noise=0.5)
        for i in range(self.TESTS):
            v = myCv.val(i)
            #print(v)
            #self._assertInRange(v, -0.25, +0.25)
    
    def test_04_00(self):
        """TestChVals.test_04_00(): sin curve."""
        #print()
        numSamples = 4
        myCv = LisGen.ChValsSin(fOffs=0, waveLen=4, mid=0.0, amp=2.0, numSa=numSamples, noise=None)
        for i in range(self.TESTS):
            for s in range(numSamples):
                v = myCv.val(i, s)
                #print(v)
                self._assertInRange(v, -2.0, 2.0)
    
    def test_04_01(self):
        """TestChVals.test_04_01(): sin curve."""
        #print()
        numSamples = 4
        myCv = LisGen.ChValsSin(fOffs=0, waveLen=4, mid=2.0, amp=2.0, numSa=numSamples, noise=None)
        for i in range(self.TESTS):
            for s in range(numSamples):
                v = myCv.val(i, s)
                #print(v)
                self._assertInRange(v, 0.0, 4.0)
    
    def test_04_02(self):
        """TestChVals.test_04_02(): sin curve, samples 1."""
        #print()
        numSamples = 1
        myCv = LisGen.ChValsSin(fOffs=0, waveLen=16, mid=2.0, amp=2.0, numSa=numSamples, noise=None)
        for i in range(self.TESTS):
            for s in range(numSamples):
                v = myCv.val(i, s)
                #print(v)
                self._assertInRange(v, 0.0, 4.0)
    
    def test_05_00(self):
        """TestChVals.test_04_00(): cos curve."""
        #print()
        numSamples = 4
        myCv = LisGen.ChValsCos(fOffs=0, waveLen=4, mid=0.0, amp=2.0, numSa=numSamples, noise=None)
        for i in range(self.TESTS):
            for s in range(numSamples):
                v = myCv.val(i, s)
                #print(v)
                self._assertInRange(v, -2.0, 2.0)
    
    def test_05_01(self):
        """TestChVals.test_05_01(): cos curve."""
        #print()
        numSamples = 4
        myCv = LisGen.ChValsCos(fOffs=0, waveLen=4, mid=2.0, amp=2.0, numSa=numSamples, noise=None)
        for i in range(self.TESTS):
            for s in range(numSamples):
                v = myCv.val(i, s)
                #print(v)
                self._assertInRange(v, 0.0, 4.0)

    def test_06_00(self):
        """TestChVals.test_06_00(): sawtooth curve."""
        #print()
        numSamples = 4
        myCv = LisGen.ChValsSaw(fOffs=0, waveLen=4, mid=1.0, amp=1.0, numSa=numSamples, noise=None)
        for i in range(self.TESTS):
            for s in range(numSamples):
                v = myCv.val(i, s)
                #print(v)
                self._assertInRange(v, 0.0, 2.0)
    
    def test_07_00(self):
        """TestChVals.test_07_00(): triangular curve."""
        #print()
        numSamples = 4
        myCv = LisGen.ChValsTriangular(fOffs=0, waveLen=4, mid=1.0, amp=1.0, numSa=numSamples, noise=None)
        for i in range(self.TESTS):
            for s in range(numSamples):
                v = myCv.val(i, s)
                #print(v)
                self._assertInRange(v, 0.0, 2.0)
    
    def test_08_00(self):
        """TestChVals.test_08_00(): square curve."""
        #print()
        numSamples = 4
        myCv = LisGen.ChValsSquare(fOffs=0, waveLen=4, mid=1.0, amp=1.0, numSa=numSamples, noise=None)
        for i in range(self.TESTS):
            for s in range(numSamples):
                v = myCv.val(i, s)
                #print(v)
                self._assertInRange(v, 0.0, 2.0)

    def test_09_00(self):
        """TestChVals.test_09_00(): special sequence using ChValsSpecialSeqSqRoot."""
#        print()
        numSamples = 1
        myCv = LisGen.ChValsSpecialSeqSqRoot(fOffs=0, waveLen=4, mid=0.0, amp=100.0, numSa=numSamples, noise=None)
#        print('myCv', myCv)
        for i in range(1024):#self.TESTS):
            for s in range(numSamples):
                v = myCv.val(i, s)
#                print(v)
                self._assertInRange(v, 0.0, 900.0)

#    def test_10_00(self):
#        """TestChVals.test_10_00(): special sequence using ChValsSpecialSeqSquare."""
#        print()
#        numSamples = 1
#        myCv = LisGen.ChValsSpecialSeqSquare(fOffs=0, waveLen=4, mid=1.0, amp=1.0, numSa=numSamples, noise=None)
#        for i in range(256):#self.TESTS):
#            for s in range(numSamples):
#                v = myCv.val(i, s)
#                print(v)
##                self._assertInRange(v, 0.0, 9.0)

    def test_20(self):
        """TestChVals.test_20(): sin curve, samples 1, __str__()."""
        myCv = LisGen.ChValsSin(fOffs=0, waveLen=16, mid=2.0, amp=2.0, numSa=1, noise=0.1)
#        print(myCv)
        self.assertEqual(
            'ChValsFrameBase: fOffs=0, waveLen=16, mid=2, amp=2, numSa=1, noise=0.1',
            str(myCv),
        )
    

@pytest.mark.slow
class TestChValsX(TestLisGenBase):
    """Tests channel value X axis generation."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestChVals: Tests setUp() and tearDown()."""
        myC = LisGen.ChValsBase()
        self.assertRaises(NotImplementedError, myC.val, 0)
    
    def test_00(self):
        """TestChValsX.test_00(): Decreasing X."""
        myCvx = LisGen.ChValsXaxis(xStart=10000.0, frameSpacing=0.5, xDec=True, noise=None)
        myValS = [myCvx.val(f) for f in range(8)]
        #print()
        #print(myValS)
        self.assertEqual(
            [10000.0, 9999.5, 9999.0, 9998.5, 9998.0, 9997.5, 9997.0, 9996.5],
            myValS
        )

    def test_01(self):
        """TestChValsX.test_00(): Increasing X."""
        myCvx = LisGen.ChValsXaxis(xStart=10000.0, frameSpacing=0.5, xDec=False, noise=None)
        myValS = [myCvx.val(f) for f in range(8)]
        #print()
        #print(myValS)
        self.assertEqual(
            [10000.0, 10000.5, 10001.0, 10001.5, 10002.0, 10002.5, 10003.0, 10003.5],
            myValS
        )
    
    def test_02(self):
        """TestChValsX.test_02(): Increasing X but negative frame spacing gives decreasing X."""
        myCvx = LisGen.ChValsXaxis(xStart=10000.0, frameSpacing=-0.5, xDec=False, noise=None)
        myValS = [myCvx.val(f) for f in range(8)]
        #print()
        #print(myValS)
        self.assertEqual(
            [10000.0, 9999.5, 9999.0, 9998.5, 9998.0, 9997.5, 9997.0, 9996.5],
            myValS
        )
       
    def test_03(self):
        """TestChValsX.test_03(): Decreasing X with noise."""
        numFrames = 1024
        noise = 0.1
        myCvx = LisGen.ChValsXaxis(xStart=10000.0, frameSpacing=0.5, xDec=True, noise=None)
        myValS = [myCvx.val(f) for f in range(numFrames)]
        myCvxN = LisGen.ChValsXaxis(xStart=10000.0, frameSpacing=0.5, xDec=True, noise=noise)
        myValNS = [myCvxN.val(f) for f in range(numFrames)]
        self.assertEqual(numFrames, len(myValS))
        self.assertEqual(numFrames, len(myValNS))
        for f in range(numFrames):
            self._assertInRange(myValNS[f], myValS[f]-noise/2, myValS[f]+noise/2)
        #print()
        #print(myValNS)
    

class TestChannel(TestLisGenBase):
    """Tests channel value generation."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestChannel: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestChannel.test_00(): Construction."""
        #print()
        numSamples = 4
        #b'TESTServIDServOrdNFEET\x02\xb3`;\x01\x00\x00\x10\x00\x00\x00\x04D\x00\x00\x00\x00\x00'
        #((b'TEST', b'ServID', b'ServOrdN', b'FEET', 45310011, 256, 16, 4, 68)
        myCh = LisGen.Channel(
            LisGen.ChannelSpec(
                b'TEST',
                b'ServID',
                b'ServOrdN',
                b'FEET',
                45310011,
                256,
                16,
                4,
                68
            ),
            LisGen.ChValsSaw(fOffs=0, waveLen=4, mid=0.0, amp=1.0, numSa=numSamples, noise=None)
        )
        #print(myCh.dsbBytes)
        self.assertEqual(
            b'TESTServIDServOrdNFEET\x02\xb3`;\x01\x00\x00\x10\x00\x00\x00\x04D\x00\x00\x00\x00\x00',
            myCh.dsbBytes
        )

    def test_01(self):
        """TestChannel.test_01(): val()."""
        #print()
        numSamples = 4
        #b'TESTServIDServOrdNFEET\x02\xb3`;\x01\x00\x00\x10\x00\x00\x00\x04D\x00\x00\x00\x00\x00'
        #((b'TEST', b'ServID', b'ServOrdN', b'FEET', 45310011, 256, 16, 4, 68)
        myCh = LisGen.Channel(
            LisGen.ChannelSpec(
                b'TEST',
                b'ServID',
                b'ServOrdN',
                b'FEET',
                45310011,
                256,
                16,
                4,
                68
            ),
            LisGen.ChValsSaw(fOffs=0, waveLen=4, mid=0.0, amp=1.0, numSa=numSamples, noise=None)
        )
        #print(myCh.dsbBytes)
        self.assertEqual(
            b'TESTServIDServOrdNFEET\x02\xb3`;\x01\x00\x00\x10\x00\x00\x00\x04D\x00\x00\x00\x00\x00',
            myCh.dsbBytes
        )
        actVals = []
        for i in range(8):
            for s in range(numSamples):
                v = myCh.val(i, s)
                #print(v)
                actVals.append(v)
        expVals = [
            0.8125,
            0.875,
            0.9375,
            0.0,
            0.0625,
            0.125,
            0.1875,
            0.25,
            0.3125,
            0.375,
            0.4375,
            0.5,
            0.5625,
            0.625,
            0.6875,
            0.75,
            0.8125,
            0.875,
            0.9375,
            0.0,
            0.0625,
            0.125,
            0.1875,
            0.25,
            0.3125,
            0.375,
            0.4375,
            0.5,
            0.5625,
            0.625,
            0.6875,
            0.75,
        ]
        self.assertEqual(expVals, actVals)

    def test_02(self):
        """TestChannel.test_02(): val()."""
        #print()
        numSamples = 4
        myCh = LisGen.Channel(
            LisGen.ChannelSpec(
                b'TEST',
                b'ServID',
                b'ServOrdN',
                b'FEET',
                45310011,
                256,
                16,
                4,
                68
            ),
            LisGen.ChValsSaw(fOffs=0, waveLen=4, mid=0.0, amp=1.0, numSa=numSamples, noise=None)
        )
        #print(myCh.dsbBytes)
        self.assertEqual(
            b'TESTServIDServOrdNFEET\x02\xb3`;\x01\x00\x00\x10\x00\x00\x00\x04D\x00\x00\x00\x00\x00',
            myCh.dsbBytes
        )
        actVals = []
        for i in range(8):
            v = myCh.frameBytes(i)
            #print(v)
            actVals.append(v)
        #print(actVals)
        expVals = [
            bytearray(b'@h\x00\x00@p\x00\x00@x\x00\x00@\x00\x00\x00'),
            bytearray(b'>\xc0\x00\x00?@\x00\x00?`\x00\x00?\xc0\x00\x00'),
            bytearray(b'?\xd0\x00\x00?\xe0\x00\x00?\xf0\x00\x00@@\x00\x00'),
            bytearray(b'@H\x00\x00@P\x00\x00@X\x00\x00@`\x00\x00'),
            bytearray(b'@h\x00\x00@p\x00\x00@x\x00\x00@\x00\x00\x00'),
            bytearray(b'>\xc0\x00\x00?@\x00\x00?`\x00\x00?\xc0\x00\x00'),
            bytearray(b'?\xd0\x00\x00?\xe0\x00\x00?\xf0\x00\x00@@\x00\x00'),
            bytearray(b'@H\x00\x00@P\x00\x00@X\x00\x00@`\x00\x00'),
        ]
        self.assertEqual(expVals, actVals)

class TestChannelDipmeter(TestLisGenBase):
    """Tests channel value generation for Dipmeter Rep Codes."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestChannelDipmeter: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestChannelDipmeter.test_00(): Construction of 130."""
        myDip = LisGen.ChGenDip130('constant')

    def test_00_00(self):
        """TestChannelDipmeter.test_00_00(): ChGenDipmenter.frameBytes() raises NotImplementedError."""
        myDip = LisGen.ChGenDipmenter(RepCode.DIPMETER_130_CHANNEL_NAME,
            RepCode.DIPMETER_EDIT_TAPE_REP_CODE,
            RepCode.DIPMETER_LIS_SIZE_130,
            (None, None),
        )
        self.assertRaises(NotImplementedError, myDip.frameBytes, 0)
        
    def test_01(self):
        """TestChannelDipmeter.test_01(): 130 DSB bytes."""
        myDip = LisGen.ChGenDip130('constant')
        self.assertEqual(
            b'RPS1servIDservOrdr    \x02\xb3`;\x01\x00\x00P\x00\x00\x00\x01\x82\x00\x00\x00\x00\x00',
            myDip.dsbBytes,
        )
        
    def test_02(self):
        """TestChannelDipmeter.test_02(): 130 frame bytes, 'constant'."""
        #print()
        myDip = LisGen.ChGenDip130('constant')
        myB = myDip.frameBytes(0)
        sc = RepCode.DIPMETER_NUM_FAST_CHANNELS
        for s in range(RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES):
            #print([x for x in myB[s*5:s*5+5]])
            self.assertEqual([0, 50, 100, 150, 200], [x for x in myB[s*sc:s*sc+sc]])
        self.assertEqual(RepCode.DIPMETER_LIS_SIZE_130, len(myB))
        #print(myB)
        self.assertEqual(
            b'\x002d\x96\xc8\x002d\x96\xc8'
            + b'\x002d\x96\xc8\x002d\x96\xc8'
            + b'\x002d\x96\xc8\x002d\x96\xc8'
            + b'\x002d\x96\xc8\x002d\x96\xc8'
            + b'\x002d\x96\xc8\x002d\x96\xc8'
            + b'\x002d\x96\xc8\x002d\x96\xc8'
            + b'\x002d\x96\xc8\x002d\x96\xc8'
            + b'\x002d\x96\xc8\x002d\x96\xc8',
            myB,
        )
        
    def test_03(self):
        """TestChannelDipmeter.test_03(): 130 frame bytes, 'sin'."""
        #print()
        myDip = LisGen.ChGenDip130('sin')
        myB = myDip.frameBytes(0)
        myV = [x for x in myB]
        numSc = RepCode.DIPMETER_NUM_FAST_CHANNELS
        numSa = RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES
        #for sa in range(numSa):
        #    print([x for x in myB[sa*numSc:sa*numSc+numSc]])
        for sa in range(RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES):
            for sc in range(numSc):
                self._assertInRange(myV[sa*numSc+sc], 0, 255)
        self.assertEqual(RepCode.DIPMETER_LIS_SIZE_130, len(myB))
        #print(myB)
        self.assertEqual(
            [127, 9, 37, 176, 255]
            + [176, 37, 9, 127, 245]
            + [217, 78, 0, 78, 217]
            + [245, 127, 9, 37, 176]
            + [255, 176, 37, 9, 127]
            + [245, 217, 78, 0, 78]
            + [217, 245, 127, 9, 37]
            + [176, 255, 176, 37, 9]
            + [127, 245, 217, 78, 0]
            + [78, 217, 245, 127, 9]
            + [37, 176, 255, 176, 37]
            + [9, 127, 245, 217, 78]
            + [0, 78, 217, 245, 127]
            + [9, 37, 176, 255, 176]
            + [37, 9, 127, 245, 217]
            + [78, 0, 78, 217, 245],
            [x for x in myB],
        )
        
    def test_04(self):
        """TestChannelDipmeter.test_04(): 130 frame bytes, 'random'."""
        #print()
        min = None
        max = None
        myDip = LisGen.ChGenDip130('random')
        for i in range(128):
            myB = myDip.frameBytes(i)
            myV = [x for x in myB]
            numSc = RepCode.DIPMETER_NUM_FAST_CHANNELS
            numSa = RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES
            #for sa in range(numSa):
            #    print([x for x in myB[sa*numSc:sa*numSc+numSc]])
            for sa in range(RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES):
                for sc in range(numSc):
                    v = myV[sa*numSc+sc]
                    if min is None:
                        min = max = v
                    else:
                        if min > v:
                            min = v
                        if max < v:
                            max = v
                    self._assertInRange(v, 0, 255)
            self.assertEqual(RepCode.DIPMETER_LIS_SIZE_130, len(myB))
        #print('Min/Max', min, max)
        self.assertEqual(0, min)
        self.assertEqual(255, max)
#        print(myB)
#        self.assertEqual(
#            [127, 9, 37, 176, 255]
#            + [176, 37, 9, 127, 245]
#            + [217, 78, 0, 78, 217]
#            + [245, 127, 9, 37, 176]
#            + [255, 176, 37, 9, 127]
#            + [245, 217, 78, 0, 78]
#            + [217, 245, 127, 9, 37]
#            + [176, 255, 176, 37, 9]
#            + [127, 245, 217, 78, 0]
#            + [78, 217, 245, 127, 9]
#            + [37, 176, 255, 176, 37]
#            + [9, 127, 245, 217, 78]
#            + [0, 78, 217, 245, 127]
#            + [9, 37, 176, 255, 176]
#            + [37, 9, 127, 245, 217]
#            + [78, 0, 78, 217, 245],
#            [x for x in myB],
#        )
        
    def test_05(self):
        """TestChannelDipmeter.test_05(): 130 frame bytes, 'linear'."""
        #print()
        min = None
        max = None
        myDip = LisGen.ChGenDip130('linear')
        for i in range(1):#28):
            myB = myDip.frameBytes(i)
            myV = [x for x in myB]
            numSc = RepCode.DIPMETER_NUM_FAST_CHANNELS
            numSa = RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES
            #for sa in range(numSa):
            #    print([x for x in myB[sa*numSc:sa*numSc+numSc]])
            for sa in range(RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES):
                for sc in range(numSc):
                    v = myV[sa*numSc+sc]
                    if min is None:
                        min = max = v
                    else:
                        if min > v:
                            min = v
                        if max < v:
                            max = v
                    self._assertInRange(v, 0, 255)
            self.assertEqual(RepCode.DIPMETER_LIS_SIZE_130, len(myB))
        #print('Min/Max', min, max)
        #self.assertEqual(0, min)
        #self.assertEqual(255, max)
        #print(myB)
        self.assertEqual(
            [0, 50, 100, 150, 200]
            + [16, 66, 116, 166, 216]
            + [32, 82, 132, 182, 232]
            + [48, 98, 148, 198, 248]
            + [64, 114, 164, 214, 8]
            + [80, 130, 180, 230, 24]
            + [96, 146, 196, 246, 40]
            + [112, 162, 212, 6, 56]
            + [128, 178, 228, 22, 72]
            + [144, 194, 244, 38, 88]
            + [160, 210, 4, 54, 104]
            + [176, 226, 20, 70, 120]
            + [192, 242, 36, 86, 136]
            + [208, 2, 52, 102, 152]
            + [224, 18, 68, 118, 168]
            + [240, 34, 84, 134, 184],
            [x for x in myB],
        )

    def test_06(self):
        """TestChannelDipmeter.test_06(): 130 frame bytes, fails on 'unknown'."""
        #print()
        myDip = LisGen.ChGenDip130('unknown')
        self.assertRaises(LisGen.ExceptionLisGen, myDip.frameBytes, 0)

    def test_10(self):
        """TestChannelDipmeter.test_00(): Construction of 234."""
        myDip = LisGen.ChGenDip234(('constant', 'constant'))

    def test_10_00(self):
        """TestChannelDipmeter.test_00_00(): ChGenDipmenter.frameBytes() 234 raises NotImplementedError."""
        myDip = LisGen.ChGenDipmenter(
            RepCode.DIPMETER_234_CHANNEL_NAME,
            RepCode.DIPMETER_CSU_FIELD_TAPE_REP_CODE,
            RepCode.DIPMETER_LIS_SIZE_234,
            (None, None),
        )
        self.assertRaises(NotImplementedError, myDip.frameBytes, 0)
        
    def test_11(self):
        """TestChannelDipmeter.test_01(): 234 DSB bytes."""
        myDip = LisGen.ChGenDip234(('constant', 'constant'))
        self.assertEqual(
            b'RHDTservIDservOrdr    \x02\xb3`;\x01\x00\x00Z\x00\x00\x00\x01\xea\x00\x00\x00\x00\x00',
            myDip.dsbBytes,
        )
        
    def test_12(self):
        """TestChannelDipmeter.test_02(): 234 frame bytes, ('constant', 'constant')."""
        #print()
        myDip = LisGen.ChGenDip234(('constant', 'constant'))
        myB = myDip.frameBytes(0)
        self.assertEqual(RepCode.DIPMETER_LIS_SIZE_234, len(myB))
        for v in myB:
            self._assertInRange(v, 0, 255)
        sc = RepCode.DIPMETER_NUM_FAST_CHANNELS
        for s in range(RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES):
            #print([x for x in myB[s*5:s*5+5]])
            self.assertEqual([0, 50, 100, 150, 200], [x for x in myB[s*sc:s*sc+sc]])
        #print([x for x in myB[80:90]])
        self.assertEqual(
            [0, 25, 50, 75, 100, 125, 150, 175, 200, 225],
            [x for x in myB[RepCode.DIPMETER_SIZE_FAST_CHANNELS:RepCode.DIPMETER_LIS_SIZE_234]],
        )
        #print(myB)
        self.assertEqual(
            b'\x002d\x96\xc8\x002d\x96\xc8'
            + b'\x002d\x96\xc8\x002d\x96\xc8'
            + b'\x002d\x96\xc8\x002d\x96\xc8'
            + b'\x002d\x96\xc8\x002d\x96\xc8'
            + b'\x002d\x96\xc8\x002d\x96\xc8'
            + b'\x002d\x96\xc8\x002d\x96\xc8'
            + b'\x002d\x96\xc8\x002d\x96\xc8'
            + b'\x002d\x96\xc8\x002d\x96\xc8'
            + b'\x00\x192Kd}\x96\xaf\xc8\xe1',
            myB,
        )
        
    def test_13(self):
        """TestChannelDipmeter.test_02(): 234 frame bytes, ('constant', 'random')."""
        #print()
        myDip = LisGen.ChGenDip234(('constant', 'random'))
        myB = myDip.frameBytes(0)
        self.assertEqual(RepCode.DIPMETER_LIS_SIZE_234, len(myB))
        for v in myB:
            self._assertInRange(v, 0, 255)
        sc = RepCode.DIPMETER_NUM_FAST_CHANNELS
        for s in range(RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES):
            #print([x for x in myB[s*5:s*5+5]])
            self.assertEqual([0, 50, 100, 150, 200], [x for x in myB[s*sc:s*sc+sc]])
        #print([x for x in myB[80:90]])
#        self.assertEqual(
#            [0, 25, 50, 75, 100, 125, 150, 175, 200, 225],
#            [x for x in myB[RepCode.DIPMETER_SIZE_FAST_CHANNELS:RepCode.DIPMETER_LIS_SIZE_234]],
#        )
#        #print(myB)
#        self.assertEqual(
#            b'\x002d\x96\xc8\x002d\x96\xc8'
#            + b'\x002d\x96\xc8\x002d\x96\xc8'
#            + b'\x002d\x96\xc8\x002d\x96\xc8'
#            + b'\x002d\x96\xc8\x002d\x96\xc8'
#            + b'\x002d\x96\xc8\x002d\x96\xc8'
#            + b'\x002d\x96\xc8\x002d\x96\xc8'
#            + b'\x002d\x96\xc8\x002d\x96\xc8'
#            + b'\x002d\x96\xc8\x002d\x96\xc8'
#            + b'\x00\x192Kd}\x96\xaf\xc8\xe1',
#            myB,
#        )

    def test_14(self):
        """TestChannelDipmeter.test_14(): 234 frame bytes, fails on ('constant', 'unknown')."""
        myDip = LisGen.ChGenDip234(('constant', 'unknown'))
        self.assertRaises(LisGen.ExceptionLisGen, myDip.frameBytes, 0)

class TestLogPassGen(TestLisGenBase):
    """Tests LogPassGen generation."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestLogPassGen: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestLogPassGen.test_00(): Construction, single channel."""
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
            xStart=10000.0,
            xRepCode=68,
            xNoise=None,
        )
        #print(lrBytesDFSR())
        expBy = (
            bytearray(b'@\x00')
            # Entry Blocks
            + bytearray(b'\x01\x01B\x00')
            + bytearray(b'\x02\x01B\x00')
            + bytearray(b'\x03\x01B\x10')
            + bytearray(b'\x04\x01B\x01')
            + bytearray(b'\x05\x01B\x01')
            + bytearray(b'\x06\x00B')
            + bytearray(b'\x07\x04A.1IN')
            + bytearray(b'\x08\x01B<')
            + bytearray(b'\t\x04A.1IN')
            + bytearray(b'\x0b\x00B')
            + bytearray(b'\x0c\x04D\xba\x83\x18\x00')
            + bytearray(b'\r\x01B\x00')
            + bytearray(b'\x0e\x04A.1IN')
            + bytearray(b'\x0f\x01B\x00')
            + bytearray(b'\x10\x01B\x00')
            + bytearray(b'\x00\x01B\x01')
            # DSB blocks
            + b'DEPTServIDServOrdN.1IN\x02\xb3`;\x01\x00\x00\x04\x00\x00\x00\x01D\x00\x00\x00\x00\x00'
            + b'TESTServIDServOrdNFEET\x02\xb3`;\x01\x00\x00\x10\x00\x00\x00\x04D\x00\x00\x00\x00\x00'
        )
        self.assertEqual(
            list(expBy),
            list(myLp.lrBytesDFSR()),
        )

    def test_01(self):
        """TestLogPassGen.test_01(): Construction, Dipmeter 130."""
        #print()
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 80))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 66, 60))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'.1IN'))
        #print('myEbs.lisByteList()')
        #pprint.pprint(myEbs.lisByteList())
        myLp = LisGen.LogPassGen(
            myEbs,
            # Channel list
            [
                LisGen.ChGenDip130('random'),
            ],
            xStart=10000.0,
            xRepCode=68,
            xNoise=None,
        )
        #print(myLp.lrBytesDFSR())
        expBy = (
            bytearray(b'@\x00')
            # Entry Blocks
            + bytearray(b'\x01\x01B\x00')
            + bytearray(b'\x02\x01B\x00')
            + bytearray(b'\x03\x01B\x50')
            + bytearray(b'\x04\x01B\x01')
            + bytearray(b'\x05\x01B\x01')
            + bytearray(b'\x06\x00B')
            + bytearray(b'\x07\x04A.1IN')
            + bytearray(b'\x08\x01B<')
            + bytearray(b'\t\x04A.1IN')
            + bytearray(b'\x0b\x00B')
            + bytearray(b'\x0c\x04D\xba\x83\x18\x00')
            + bytearray(b'\r\x01B\x00')
            + bytearray(b'\x0e\x04A.1IN')
            + bytearray(b'\x0f\x01B\x00')
            + bytearray(b'\x10\x01B\x00')
            + bytearray(b'\x00\x01B\x01')
            # DSB blocks
            + b'DEPTServIDServOrdN.1IN\x02\xb3`;\x01\x00\x00\x04\x00\x00\x00\x01D\x00\x00\x00\x00\x00'
            + b'RPS1servIDservOrdr    \x02\xb3`;\x01\x00\x00P\x00\x00\x00\x01\x82\x00\x00\x00\x00\x00'
        )
        self.assertEqual(
            expBy,
            myLp.lrBytesDFSR()
        )

    def test_02(self):
        """TestLogPassGen.test_02(): Construction, single channel, normalAlternateData(2,0) fails."""
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
                    LisGen.ChValsConst(fOffs=0, waveLen=4, mid=0.0, amp=1.0, numSa=1, noise=None)
                ),
            ],
            xStart=10000.0,
            xRepCode=68,
            xNoise=None,
        )
        # Test illogical number of frames
        self.assertRaises(LisGen.ExceptionLisGen, myLp._normalAlternateData, 2, -1)

    def test_03(self):
        """TestLogPassGen.test_03(): Construction, DEPT channel, dipmeter and two LRs."""
        #print()
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4+80))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 66, 60))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'.1IN'))
        #print('myEbs.lisByteList()')
        #pprint.pprint(myEbs.lisByteList())
        myLp = LisGen.LogPassGen(
            myEbs,
            # Channel list
            [
                LisGen.ChGenDip130('constant'),                
            ],
            xStart=10000.0,
            xRepCode=68,
            xNoise=None,
        )
        #print(myLp.lrBytesDFSR())
        expBy = (
            bytearray(b'@\x00')
            # Entry Blocks
            + bytearray(b'\x01\x01B\x00')
            + bytearray(b'\x02\x01B\x00')
            + bytearray(b'\x03\x01B\x54')
            + bytearray(b'\x04\x01B\x01')
            + bytearray(b'\x05\x01B\x01')
            + bytearray(b'\x06\x00B')
            + bytearray(b'\x07\x04A.1IN')
            + bytearray(b'\x08\x01B<')
            + bytearray(b'\t\x04A.1IN')
            + bytearray(b'\x0b\x00B')
            + bytearray(b'\x0c\x04D\xba\x83\x18\x00')
            + bytearray(b'\r\x01B\x00')
            + bytearray(b'\x0e\x04A.1IN')
            + bytearray(b'\x0f\x01B\x00')
            + bytearray(b'\x10\x01B\x00')
            + bytearray(b'\x00\x01B\x01')
            # DSB blocks
            + b'DEPTServIDServOrdN.1IN\x02\xb3`;\x01\x00\x00\x04\x00\x00\x00\x01D\x00\x00\x00\x00\x00'
            + b'RPS1servIDservOrdr    \x02\xb3`;\x01\x00\x00P\x00\x00\x00\x01\x82\x00\x00\x00\x00\x00'
        )
        self.assertEqual(
            expBy,
            myLp.lrBytesDFSR()
        )
        #print()
        #print(myLp._normalAlternateData(0,2))
        myB = myLp._normalAlternateData(0,2)
        self.assertEqual(2*(4+80), len(myB))
        #print(myB[:4])
        #print(myB[4:80])
        #print([myB[x:5+x] for x in range(4, 84, 5)])
        #for x in range(4, 84, 5):
        #    print(myB[x:5+x])
        #print(myB[84:88])
        #print(myB[84:164])
        #print([myB[x:5+x] for x in range(88, 168, 5)])
        #for x in range(88, 168, 5):
        #    print(myB[x:5+x])
        expFrBy = (
            bytearray(b'GN \x00')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'GM\xa8\x00')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
            + bytearray(b'\x002d\x96\xc8')
        )
        #for i in range(len(expFrBy)):
        #    if expFrBy[i] != myB[i]:
        #        print(i)
        self.assertEqual(expFrBy, myB)

    def test_04(self):
        """TestLogPassGen.test_04(): Construction, single channel, genNormalAlternateData(0, 1), direct X."""
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
                    LisGen.ChValsConst(fOffs=0, waveLen=4, mid=0.0, amp=1.0, numSa=1, noise=None)
                ),
            ],
            xStart=10000.0,
            xRepCode=68,
            xNoise=None,
        )
        # Test illogical number of frames
        myB = myLp.lrBytes(0, 1)
        #print()
        #print(myB)
        self.assertEqual(
            b'\x00\x00'
            + b'GN \x00'
            + b'@\x00\x00\x00'
            + b'@\x00\x00\x00'
            + b'@\x00\x00\x00'
            + b'@\x00\x00\x00',
            myB
        )

    def test_05(self):
        """TestLogPassGen.test_04(): Construction, single channel, genNormalAlternateData(0, 1), indirect X."""
        #print()
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4*4))
        # Indirect X, integer RepCode 73
        # Block 4
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_UP_DOWN_FLAG,1, 66, 1))
        # Block 8
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 66, 60))
        # Block 9
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'.1IN'))
        # Block 13
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_RECORD_MODE, 1, 66, 1))
        # Block 14
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_DEPTH_UNITS, 4, 65, b'.1IN'))
        # Block 15
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_DEPTH_REP_CODE, 1, 66, 73))
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
                    LisGen.ChValsConst(fOffs=0, waveLen=4, mid=0.0, amp=1.0, numSa=1, noise=None)
                ),
            ],
            xStart=10000*12*10,
            xRepCode=73,
            xNoise=None,
        )
        myB = myLp.lrBytes(0, 1)
        #print()
        #print(myB)
        self.assertEqual(
            b'\x00\x00'
            # 18 << 16 | 79 << 8 | 128 = 1200000
            + bytes([0, 18, 79, 128])
            + b'@\x00\x00\x00'
            + b'@\x00\x00\x00'
            + b'@\x00\x00\x00'
            + b'@\x00\x00\x00',
            myB
        )

    def test_06(self):
        """TestLogPassGen.test_06(): Construction fails with no (i.e. EBS default) frame spacing."""
        #print()
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4*4))
        #print('myEbs.lisByteList()')
        #pprint.pprint(myEbs.lisByteList())
        self.assertRaises(LisGen.ExceptionLisGen, LisGen.LogPassGen,
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
            xStart=10000.0,
            xRepCode=68,
            xNoise=None,
        )

class Special(TestLisGenBase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRandom))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPhysRec))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileTapeReel))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTableGenCONS))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTableGenRandomCONS))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestChVals))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestChValsX))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestChannel))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestChannelDipmeter))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogPassGen))
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
