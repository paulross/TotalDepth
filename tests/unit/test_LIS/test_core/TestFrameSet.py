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
"""Test FrameSet module."""
import pytest

__author__  = 'Paul Ross'
__date__    = '10 Jan 2011'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'

import os
import sys
import time
import logging
import pprint

import numpy

from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import FrameSet
from TotalDepth.LIS.core import cFrameSet
from TotalDepth.LIS.core import RepCode

######################
# Section: Unit tests.
######################
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import BaseTestClasses

class TestFrameSet_SuChArTe(BaseTestClasses.TestBaseFile):
    """Tests FrameSet SuChArTe class"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSet_SuChArTe: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSet_SuChArTe.test_00(): SuChArTe construction."""
        myScat = FrameSet.SuChArTe(samples=12, bursts=5)
        self.assertEqual(myScat.samples, 12)
        self.assertEqual(myScat.bursts, 5)
        self.assertEqual(myScat.numValues, 60)

    def test_01(self):
        """TestFrameSet_SuChArTe.test_01(): SuChArTe construction, one sample, one burst."""
        myScat = FrameSet.SuChArTe(samples=1, bursts=1)
        self.assertEqual(myScat.samples, 1)
        self.assertEqual(myScat.bursts, 1)
        self.assertEqual(myScat.numValues, 1)
        self.assertEqual(myScat.index(0, 0), 0)
        self.assertEqual(myScat.index(-1, 0), 0)
        self.assertEqual(myScat.index(0, -1), 0)
        self.assertRaises(IndexError, myScat.index, 1, 0)
        self.assertRaises(IndexError, myScat.index, 0, 1)
        self.assertRaises(IndexError, myScat.index, -2, 0)
        self.assertRaises(IndexError, myScat.index, 0, -2)

    def test_02(self):
        """TestFrameSet_SuChArTe.test_02(): SuChArTe construction, two samples, four bursts."""
        myScat = FrameSet.SuChArTe(samples=2, bursts=4)
        self.assertEqual(myScat.samples, 2)
        self.assertEqual(myScat.bursts, 4)
        self.assertEqual(myScat.numValues, 8)
        self.assertEqual(myScat.index(theS=0, theB=0), 0)
        self.assertEqual(myScat.index(0, 1), 1)
        self.assertEqual(myScat.index(0, 2), 2)
        self.assertEqual(myScat.index(0, 3), 3)
        self.assertRaises(IndexError, myScat.index, 0, 4)
        self.assertEqual(myScat.index(0, -1), 3)
        self.assertEqual(myScat.index(0, -2), 2)
        self.assertEqual(myScat.index(0, -3), 1)
        self.assertEqual(myScat.index(0, -4), 0)
        self.assertRaises(IndexError, myScat.index, 0, -5)
        self.assertEqual(myScat.index(theS=1, theB=0), 4)
        self.assertEqual(myScat.index(1, 1), 5)
        self.assertEqual(myScat.index(1, 2), 6)
        self.assertEqual(myScat.index(1, 3), 7)
        self.assertRaises(IndexError, myScat.index, 2, 0)
        self.assertEqual(myScat.index(-1, -1), 7)
        self.assertEqual(myScat.index(-1, -2), 6)
        self.assertEqual(myScat.index(-1, -3), 5)
        self.assertEqual(myScat.index(-1, -4), 4)
        self.assertRaises(IndexError, myScat.index, 0, -5)
        self.assertRaises(IndexError, myScat.index, -1, -5)
        self.assertRaises(IndexError, myScat.index, -3, 0)
        self.assertRaises(IndexError, myScat.index, 0, 4)

class TestFrameSet_ChArTe(BaseTestClasses.TestBaseFile):
    """Tests FrameSet.ChArTe class"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSet_ChArTe: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSet_ChArTe.test_00(): ChArTe construction."""
        # Logical record header for DFSR
        # Logical record header for DFSR
        myB = bytes([64, 0])
        # Mnemonic       Service ID  Service ord   Units   API codes            File number: 256
        myB += b'XXXX' + b'ServID' + b'ServOrdN' + b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
        # LIS size in bytes:
        # single value RC 68   Pad      Samples: 1   Representation code
        myB += bytes([0, 4]) + b'000' + bytes([1,]) + bytes([68,])
        # Process indicators
        myB += bytes([0, 1, 2, 3, 4])
        myF = self._retFileSinglePr(myB)
        self.assertEqual(myF.readLrBytes(2), b'@\x00')
        myDsb = LogiRec.DatumSpecBlockRead(myF)
        myCat = FrameSet.ChArTe(myDsb)
        self.assertEqual(myCat.numSubChannels, 1)
        self.assertEqual(myCat.numValues, 1)
        self.assertEqual(myCat.lisSize, 4)
        self.assertEqual(myCat[0].bursts, 1)
        self.assertEqual(myCat[0].samples, 1)
        self.assertEqual(myCat[0].numValues, 1)
        self.assertEqual(myCat.index(0, 0, 0), 0)
        #                                          Sc Sa Bu
        self.assertRaises(IndexError, myCat.index, 1, 0, 0)
        self.assertRaises(IndexError, myCat.index, 0, 1, 0)
        self.assertRaises(IndexError, myCat.index, 0, 0, 1)

    def test_01(self):
        """TestFrameSet_ChArTe.test_01(): ChArTe construction, 3 samples 4 bursts."""
        # Logical record header for DFSR
        myB = bytes([64, 0])
        # Mnemonic       Service ID  Service ord   Units   API codes            File number: 256
        myB += b'XXXX' + b'ServID' + b'ServOrdN' + b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
        # LIS size in bytes:
        # 3 * 4 * RC 68        Pad      Samples: 3   Representation code
        myB += bytes([0, 3*4*4]) + b'000' + bytes([3,]) + bytes([68,])
        # Process indicators
        myB += b'\x00\x00\x00\x00\x00' #bytes([0, 1, 2, 3, 4])
        myF = self._retFileSinglePr(myB)
        self.assertEqual(myF.readLrBytes(2), b'@\x00')
        myDsb = LogiRec.DatumSpecBlockRead(myF)
        myCat = FrameSet.ChArTe(myDsb)
        self.assertEqual(myCat.numSubChannels, 1)
        self.assertEqual(myCat.numValues, 3*4)
        self.assertEqual(myCat.lisSize, 3*4*4)
        self.assertEqual(myCat[0].bursts, 4)
        self.assertEqual(myCat[0].samples, 3)
        self.assertEqual(myCat[0].numValues, 3*4)
        self.assertEqual(myCat.index(0, 0, 0), 0)
        self.assertEqual(myCat.index(0, 0, 1), 1)
        self.assertEqual(myCat.index(0, 0, 2), 2)
        self.assertEqual(myCat.index(0, 0, 3), 3)
        self.assertEqual(myCat.index(0, 1, 0), 4)
        self.assertEqual(myCat.index(0, 1, 1), 5)
        self.assertEqual(myCat.index(0, 1, 2), 6)
        self.assertEqual(myCat.index(0, 1, 3), 7)
        self.assertEqual(myCat.index(0, 2, 0), 8)
        self.assertEqual(myCat.index(0, 2, 1), 9)
        self.assertEqual(myCat.index(0, 2, 2), 10)
        self.assertEqual(myCat.index(0, 2, 3), 11)
        self.assertRaises(IndexError, myCat.index, 1, 0, 0)
        self.assertRaises(IndexError, myCat.index, 0, 3, 0)
        self.assertRaises(IndexError, myCat.index, 0, 0, 4)
        # Offsets
        self.assertEqual(list(range(12)), list(myCat.subChOffsRange(0)))

class TestFrameSet_ChArTe_Dipmeter(BaseTestClasses.TestBaseFile):
    """Tests FrameSet.ChArTe class for Dipmeter data."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSet_ChArTe: Tests setUp() and tearDown()."""
        pass

    def _retCat_130(self):
        """Returns a ChArTe for representation code 130."""
        # Logical record header for DFSR
        myB = bytes([64, 0])
        # Mnemonic       Service ID  Service ord    Units   API codes            File number: 256
        myB += b'XXXX' + b'ServID' + b'ServOrdN' + b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
        # LIS size in bytes:
        # RC 130 so 80 bytes     Pad      Samples: 1   Representation code
        myB += bytes([0, 80]) + b'000' + bytes([1,]) + bytes([130,])
        # Process indicators
        myB += b'\x00\x00\x00\x00\x00' #bytes([0, 1, 2, 3, 4])
        myF = self._retFileSinglePr(myB)
        self.assertEqual(myF.readLrBytes(2), b'@\x00')
        myDsb = LogiRec.DatumSpecBlockRead(myF)
        return FrameSet.ChArTe(myDsb)

    def _retCat_234(self):
        """Returns a ChArTe for representation code 234."""
        # Logical record header for DFSR
        myB = bytes([64, 0])
        # Mnemonic       Service ID  Service ord    Units   API codes            File number: 256
        myB += b'XXXX' + b'ServID' + b'ServOrdN' + b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
        # LIS size in bytes:
        # RC 130 so 90 bytes     Pad      Samples: 1   Representation code
        myB += bytes([0, 90]) + b'000' + bytes([1,]) + bytes([234,])
        # Process indicators
        myB += b'\x00\x00\x00\x00\x00' #bytes([0, 1, 2, 3, 4])
        myF = self._retFileSinglePr(myB)
        self.assertEqual(myF.readLrBytes(2), b'@\x00')
        myDsb = LogiRec.DatumSpecBlockRead(myF)
        return FrameSet.ChArTe(myDsb)

    def test_130_00(self):
        """TestFrameSet_ChArTe_Dipmeter.test_130_00(): ChArTe ctor, Representation Code 130 - basic."""
        myCat = self._retCat_130()
        self.assertEqual(myCat.numSubChannels, 5)
        self.assertEqual(myCat.numValues, 5*16)
        self.assertEqual(myCat.lisSize, 80)

    def test_130_01(self):
        """TestFrameSet_ChArTe_Dipmeter.test_130_01(): ChArTe ctor, Representation Code 130 - fast channels."""
        myCat = self._retCat_130()
        for sc in range(5):
            self.assertEqual(myCat[sc].bursts, 1)
            self.assertEqual(myCat[sc].samples, 16)
            self.assertEqual(myCat[sc].numValues, 16)

    def test_130_02(self):
        """TestFrameSet_ChArTe_Dipmeter.test_130_02(): ChArTe ctor, Representation Code 130 - fast channels IndexErrors."""
        myCat = self._retCat_130()
        try:
            myCat[5].bursts
            self.fail('IndexError not raised')
        except IndexError:
            pass
        try:
            myCat[5].samples
            self.fail('IndexError not raised')
        except IndexError:
            pass
        try:
            myCat[5].numValues
            self.fail('IndexError not raised')
        except IndexError:
            pass
        self.assertEqual(myCat[-1].bursts, 1)
        self.assertEqual(myCat[-1].samples, 16)
        self.assertEqual(myCat[-1].numValues, 16)

    def test_130_03(self):
        """TestFrameSet_ChArTe_Dipmeter.test_130_03(): ChArTe ctor, Representation Code 130, index(+ve), _index(+ve)."""
        myCat = self._retCat_130()
        #print()
        #print(myCat)
        for i in range(80):
            sc = i % 5
            sa = i // 5
            #print(i, sc, sa, myCat.index(sc, sa, 0))
            self.assertEqual(myCat.index(sc, sa, 0), i)
            self.assertEqual(myCat._index(sc, sa, 0), i)
        self.assertRaises(IndexError, myCat.index, 0, 0, 1)
        self.assertRaises(IndexError, myCat.index, 0, 16, 0)
        self.assertRaises(IndexError, myCat.index, 5, 0, 0)
        # Sub-channel 0 samples, bursts out of range
        self.assertRaises(IndexError, myCat.index, 0, 0, 1)
        self.assertRaises(IndexError, myCat.index, 0, 16, 0)
        # Sub-channel 5 samples, bursts out of range
        self.assertRaises(IndexError, myCat.index, 5, 0, 1)
        self.assertRaises(IndexError, myCat.index, 5, 1, 0)
        # Sub-channel out of range
        self.assertRaises(IndexError, myCat.index, 15, 0, 0)

    def test_130_04(self):
        """TestFrameSet_ChArTe_Dipmeter.test_130_04(): ChArTe ctor, Representation Code 130, index(-ve), _index(-ve)."""
        myCat = self._retCat_130()
        for i in range(80):
            sc = (i % 5) - 5
            sa = (i // 5) - 16
            #print(i, sc, sa, myCat.index(sc, sa, 0))
            self.assertEqual(myCat.index(sc, sa, 0), i)
            self.assertEqual(myCat._index(sc, sa, 0), i)
        # Sub-channel 0 samples, bursts out of range
        self.assertRaises(IndexError, myCat.index, 0, 0, 1)
        self.assertRaises(IndexError, myCat.index, 0, 16, 0)
        # Sub-channel 5 samples, bursts out of range
        self.assertRaises(IndexError, myCat.index, 5, 0, 1)
        self.assertRaises(IndexError, myCat.index, 5, 1, 0)
        # Sub-channel out of range
        self.assertRaises(IndexError, myCat.index, 6, 0, 0)

    def test_130_05(self):
        """TestFrameSet_ChArTe_Dipmeter.test_130_05(): ChArTe ctor, Representation Code 130 - sub-channel offsets."""
        myCat = self._retCat_130()
        for i in range(5):
            self.assertEqual(list(range(i,i+80, 5)), list(myCat.subChOffsRange(i)))
            
    def test_234_00(self):
        """TestFrameSet_ChArTe_Dipmeter.test_234_00(): ChArTe ctor, Representation Code 234 - basic."""
        myCat = self._retCat_234()
        self.assertEqual(myCat.numSubChannels, 15)
        self.assertEqual(myCat.numValues, 5*16+10)
        self.assertEqual(myCat.lisSize, 90)

    def test_234_01(self):
        """TestFrameSet_ChArTe_Dipmeter.test_234_01(): ChArTe ctor, Representation Code 234 - fast channels."""
        myCat = self._retCat_234()
        for sc in range(5):
            self.assertEqual(myCat[sc].bursts, 1)
            self.assertEqual(myCat[sc].samples, 16)
            self.assertEqual(myCat[sc].numValues, 16)

    def test_234_02(self):
        """TestFrameSet_ChArTe_Dipmeter.test_234_02(): ChArTe ctor, Representation Code 234 - slow channels."""
        myCat = self._retCat_234()
        for sc in range(5, 15, 1):
            self.assertEqual(myCat[sc].bursts, 1)
            self.assertEqual(myCat[sc].samples, 1)
            self.assertEqual(myCat[sc].numValues, 1)

    def test_234_03(self):
        """TestFrameSet_ChArTe_Dipmeter.test_234_03(): ChArTe ctor, Representation Code 234 - slow channels, IndexErrors."""
        myCat = self._retCat_234()
        try:
            myCat[15].bursts
            self.fail('IndexError not raised')
        except IndexError:
            pass
        try:
            myCat[15].samples
            self.fail('IndexError not raised')
        except IndexError:
            pass
        try:
            myCat[15].numValues
            self.fail('IndexError not raised')
        except IndexError:
            pass
        self.assertEqual(myCat[-1].bursts, 1)
        self.assertEqual(myCat[-1].samples, 1)
        self.assertEqual(myCat[-1].numValues, 1)

    def test_234_04(self):
        """TestFrameSet_ChArTe_Dipmeter.test_234_04(): ChArTe construction, Representation Code 234 - __str__()."""
        myCat = self._retCat_234()
        #print()
        #print(myCat)
        self.assertEqual(str(myCat), """ChArTe lisSize=90 rc=234 wordLength=1 subChannels=15:
  SuChArTe(samples=16, bursts=1, values=16)
  SuChArTe(samples=16, bursts=1, values=16)
  SuChArTe(samples=16, bursts=1, values=16)
  SuChArTe(samples=16, bursts=1, values=16)
  SuChArTe(samples=16, bursts=1, values=16)
  SuChArTe(samples=1, bursts=1, values=1)
  SuChArTe(samples=1, bursts=1, values=1)
  SuChArTe(samples=1, bursts=1, values=1)
  SuChArTe(samples=1, bursts=1, values=1)
  SuChArTe(samples=1, bursts=1, values=1)
  SuChArTe(samples=1, bursts=1, values=1)
  SuChArTe(samples=1, bursts=1, values=1)
  SuChArTe(samples=1, bursts=1, values=1)
  SuChArTe(samples=1, bursts=1, values=1)
  SuChArTe(samples=1, bursts=1, values=1)""")

    def test_234_05(self):
        """TestFrameSet_ChArTe_Dipmeter.test_234_05(): ChArTe ctor, Representation Code 234 - index(+ve), _index(+ve)."""
        myCat = self._retCat_234()
        for i in range(80):
            sc = i % 5
            sa = i // 5
            #print(i, sc, sa, myCat.index(sc, sa, 0))
            self.assertEqual(myCat.index(sc, sa, 0), i)
            self.assertEqual(myCat._index(sc, sa, 0), i)
        for i in range(10):
            self.assertEqual(myCat.index(i+5, 0, 0), 80+i)
            self.assertEqual(myCat._index(i+5, 0, 0), 80+i)
        # Sub-channel 0 samples, bursts out of range
        self.assertRaises(IndexError, myCat.index, 0, 0, 1)
        self.assertRaises(IndexError, myCat.index, 0, 16, 0)
        # Sub-channel 5 samples, bursts out of range
        self.assertRaises(IndexError, myCat.index, 5, 0, 1)
        self.assertRaises(IndexError, myCat.index, 5, 1, 0)
        # Sub-channel out of range
        self.assertRaises(IndexError, myCat.index, 15, 0, 0)

    def test_234_06(self):
        """TestFrameSet_ChArTe_Dipmeter.test_234_06(): ChArTe ctor, Representation Code 234 - index(-ve), _index(-ve)."""
        myCat = self._retCat_234()
        for i in range(80):
            sc = (i % 5) - 15
            sa = (i // 5) - 16
            #print(i, sc, sa, myCat.index(sc, sa, 0))
            self.assertEqual(myCat.index(sc, sa, 0), i)
            self.assertEqual(myCat._index(sc, sa, 0), i)
        for i in range(10):
            self.assertEqual(myCat.index((i+5)-15, 0, 0), 80+i)
            self.assertEqual(myCat._index((i+5)-15, 0, 0), 80+i)
        # Sub-channel 0 samples, bursts out of range
        self.assertRaises(IndexError, myCat.index, 0, 0, 1)
        self.assertRaises(IndexError, myCat.index, 0, 16, 0)
        # Sub-channel 5 samples, bursts out of range
        self.assertRaises(IndexError, myCat.index, 5, 0, 1)
        self.assertRaises(IndexError, myCat.index, 5, 1, 0)
        # Sub-channel out of range
        self.assertRaises(IndexError, myCat.index, 15, 0, 0)
        
    def test_234_07(self):
        """TestFrameSet_ChArTe_Dipmeter.test_234_07(): ChArTe ctor, Representation Code 234 - sub-channel offsets."""
        myCat = self._retCat_234()
        for i in range(5):
            self.assertEqual(list(range(i, i+80, 5)), list(myCat.subChOffsRange(i)))
        # Slow channels
        for i in range(5,15,1):
            self.assertEqual(list(range(80+(i-5),80+(i-5)+1)), list(myCat.subChOffsRange(i)))
            
class TestFrameSetStaticData(BaseTestClasses.TestBaseFile):
    """Tests FrameSet constructor with various DFSRs (no channels) and its
    static attributes."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSetStaticData: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSetStaticData.test_00(): Construction, DFSR defaults."""
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
        )
        myDfsr = LogiRec.LrDFSRRead(myF)
        myFs = FrameSet.FrameSet(myDfsr, slice(0))
        self.assertEqual(0, myFs.numChannels)
        #print()
        #print(dir(myFs))
        #print(myFs._xAxisDecl)
        self.assertTrue(myFs._xAxisDecl.isLogUp)
        self.assertFalse(myFs._xAxisDecl.isLogDown)
        self.assertFalse(myFs.isIndirectX)
        self.assertTrue(myFs._frameSpacing is None)
        self.assertEqual(0, myFs.numFrames)

    def test_01(self):
        """TestFrameSetStaticData.test_01(): Construction, DFSR indirect X, units equal."""
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 8, Frame spacing
            + bytes([8, 1, 66, 60])
            # EB 9, Frame spacing units
            + bytes([9, 4, 65])+b'.1IN'
            # EB 13, recording mode 1
            + bytes([13, 1, 66, 1])
            # EB 14, X axis units
            + bytes([14, 4, 65])+b'.1IN'
            # EB 15, indirect Rep Code 73
            + bytes([15, 1, 66, 73])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
        )
        myDfsr = LogiRec.LrDFSRRead(myF)
        myFs = FrameSet.FrameSet(myDfsr, slice(0))
        self.assertEqual(0, myFs.numChannels)
        #print()
        #print(dir(myFs))
        #print(myFs._xAxisDecl)
        self.assertTrue(myFs._xAxisDecl.isLogUp)
        self.assertFalse(myFs._xAxisDecl.isLogDown)
        self.assertTrue(myFs.isIndirectX)
        self.assertEqual(-60, myFs._frameSpacing)
        self.assertEqual(0, myFs.numFrames)

    def test_02(self):
        """TestFrameSetStaticData.test_02(): Construction, DFSR indirect X, units need conversion."""
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 8, Frame spacing
            + bytes([8, 1, 66, 60])
            # EB 9, Frame spacing units
            + bytes([9, 4, 65])+b'.1IN'
            # EB 13, recording mode 1
            + bytes([13, 1, 66, 1])
            # EB 14, X axis units
            + bytes([14, 4, 65])+b'FT  '
            # EB 15, indirect Rep Code 73
            + bytes([15, 1, 66, 73])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
        )
        myDfsr = LogiRec.LrDFSRRead(myF)
        myFs = FrameSet.FrameSet(myDfsr, slice(0))
        self.assertEqual(0, myFs.numChannels)
        #print()
        #print(dir(myFs))
        #print(myFs._xAxisDecl)
        self.assertTrue(myFs._xAxisDecl.isLogUp)
        self.assertFalse(myFs._xAxisDecl.isLogDown)
        self.assertTrue(myFs.isIndirectX)
        self.assertEqual(-0.5, myFs._frameSpacing)
        self.assertEqual(0, myFs.numFrames)

    def test_03(self):
        """TestFrameSetStaticData.test_03(): Construction, DFSR indirect X, units do not match."""
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 8, Frame spacing
            + bytes([8, 1, 66, 60])
            # EB 9, Frame spacing units
            + bytes([9, 4, 65])+b'.1IN'
            # EB 13, recording mode 1
            + bytes([13, 1, 66, 1])
            # EB 14, X axis units
            + bytes([14, 4, 65])+b'S   '
            # EB 15, indirect Rep Code 73
            + bytes([15, 1, 66, 73])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
        )
        myDfsr = LogiRec.LrDFSRRead(myF)
        self.assertRaises(FrameSet.ExceptionFrameSet, FrameSet.FrameSet, myDfsr, slice(0))

class TestFrameSet(BaseTestClasses.TestBaseFile):
    """Tests FrameSet"""
    def setUp(self):
        """Set up."""
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 12, absent value -153.0
            + bytes([12, 4, 68])+b'\xbb\xb3\x80\x00'
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0 (sc=1, sa=1, bu=1)
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 1 (sc=1, sa=1, bu=1)
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'GR  ' + b'ServID' + b'ServOrdN'+ b'GAPI' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 2 (sc=1, sa=4, bu=1)
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'SUPE' + b'ServID' + b'ServOrdN'+ b'MMHO' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 16 LIS bytes     Pad      4 super  Rep code     Process indicators
            + bytes([0, 16]) + b'000' + b'\x04'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 3 (sc=1, sa=1, bu=8)
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'SMAL' + b'ServID' + b'ServOrdN'+ b'INCH' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 16 LIS bytes     Pad      1 sample Rep code     Process indicators
            + bytes([0, 16]) + b'000' + b'\x01'+ bytes([79,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 4 (sc=1, sa=2, bu=1)
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'BS  ' + b'ServID' + b'ServOrdN'+ b'MM  ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 8 LIS bytes     Pad      2 super  Rep code     Process indicators
            + bytes([0, 8]) + b'000' + b'\x02'+ bytes([73,]) + bytes([0, 1, 2, 3, 4])
        )
        self._dfsr = LogiRec.LrDFSRRead(myF)
        self.assertEqual(48, self._dfsr.frameSize())

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSet: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSet.test_00(): Construction."""
        myFs = FrameSet.FrameSet(self._dfsr, slice(0))
        self.assertEqual(5, myFs.numChannels)
        #print()
        #print(myFs)
        str(myFs)
        myFs.longStr()

    def test_01(self):
        """TestFrameSet.test_01(): Construction, check sub-channels."""
        myFs = FrameSet.FrameSet(self._dfsr, slice(0))
        self.assertEqual(5, myFs.numChannels)
        self.assertEqual(1, myFs.numSubChannels(0))
        self.assertEqual(1, myFs.numSubChannels(1))
        self.assertEqual(1, myFs.numSubChannels(2))
        self.assertEqual(1, myFs.numSubChannels(3))
        self.assertEqual(1, myFs.numSubChannels(4))

    def test_02(self):
        """TestFrameSet.test_02(): Construction, check samples."""
        myFs = FrameSet.FrameSet(self._dfsr, slice(0))
        self.assertEqual(5, myFs.numChannels)
        self.assertEqual(1, myFs.numSamples(0, 0))
        self.assertEqual(1, myFs.numSamples(1, 0))
        self.assertEqual(4, myFs.numSamples(2, 0))
        self.assertEqual(1, myFs.numSamples(3, 0))
        self.assertEqual(2, myFs.numSamples(4, 0))

    def test_03(self):
        """TestFrameSet.test_03(): Construction, check bursts."""
        myFs = FrameSet.FrameSet(self._dfsr, slice(0))
        self.assertEqual(1, myFs.numBursts(0, 0))
        self.assertEqual(1, myFs.numBursts(1, 0))
        self.assertEqual(1, myFs.numBursts(2, 0))
        self.assertEqual(8, myFs.numBursts(3, 0))
        self.assertEqual(1, myFs.numBursts(4, 0))

    def test_10(self):
        """TestFrameSet.test_10(): Construction, channels [1,3]."""
        myFs = FrameSet.FrameSet(self._dfsr, slice(0), theChS=[1,3], xAxisIndex=1)
        #print()
        #print(myFs.longStr())
        self.assertEqual(2, myFs.numChannels)
        self.assertRaises(IndexError, myFs.internalChIdx, 0)
        self.assertEqual(0, myFs.internalChIdx(1))
        self.assertRaises(IndexError, myFs.internalChIdx, 2)
        self.assertEqual(1, myFs.internalChIdx(3))
        self.assertRaises(IndexError, myFs.internalChIdx, 4)
        self.assertRaises(IndexError, myFs.internalChIdx, 5)
        self.assertRaises(IndexError, myFs.internalChIdx, -1)
        self.assertEqual(1, myFs.internalChIdx(-2))
        self.assertRaises(IndexError, myFs.internalChIdx, -3)
        self.assertEqual(0, myFs.internalChIdx(-4))
        self.assertRaises(IndexError, myFs.internalChIdx, -5)
        self.assertRaises(IndexError, myFs.internalChIdx, -6)
        
    def test_11(self):
        """TestFrameSet.test_11(): Construction, slice(128) intFrameNum(), extFrameNum()."""
        myFs = FrameSet.FrameSet(self._dfsr, slice(128))
        #print()
        #print(myFs.longStr())
        #print('nbytes', myFs.nbytes)
        self.assertEqual(128, myFs.numFrames)
        self.assertEqual(0, myFs.intFrameNum(0))
        self.assertEqual(0, myFs.extFrameNum(0))
        self.assertEqual(127, myFs.intFrameNum(127))
        self.assertEqual(127, myFs.extFrameNum(127))
        self.assertRaises(IndexError, myFs.intFrameNum, -1)
        self.assertRaises(IndexError, myFs.intFrameNum, 128)
        
    def test_12(self):
        """TestFrameSet.test_12(): Construction, slice(59, 128, 4) intFrameNum(), extFrameNum()."""
        mySlice = slice(59, 128, 4)
        myFs = FrameSet.FrameSet(self._dfsr, mySlice)
        #print()
        #print(myFs.longStr())
        #print('nbytes', myFs.nbytes)
        self.assertEqual(18, myFs._totalNumFrames(mySlice))
        self.assertEqual(1+(128-59)//4, myFs.numFrames)
        for e in range(mySlice.start, mySlice.stop, mySlice.step):
            self.assertEqual(e, myFs.extFrameNum(myFs.intFrameNum(e)))
        #
        self.assertEqual(0, myFs.intFrameNum(59))
        self.assertEqual(59, myFs.extFrameNum(0))
        self.assertEqual(1, myFs.intFrameNum(63))
        self.assertEqual(127, myFs.extFrameNum(17))
        self.assertRaises(IndexError, myFs.intFrameNum, 128)
        self.assertRaises(IndexError, myFs.intFrameNum, 55)
        self.assertRaises(IndexError, myFs.intFrameNum, -1)
        self.assertRaises(IndexError, myFs.intFrameNum, 1)
        
        
    def test_14(self):
        """TestFrameSet.test_14(): Construction, slice(0, -128, -4) intFrameNum(), extFrameNum()."""
        myFs = FrameSet.FrameSet(self._dfsr, slice(0, -128, -4))
        #print()
        #print(myFs.longStr())
        #print('nbytes', myFs.nbytes)
        self.assertEqual(32, myFs.numFrames)
        self.assertEqual(0, myFs.intFrameNum(0))
        self.assertEqual(0, myFs.extFrameNum(0))
        self.assertEqual(1, myFs.intFrameNum(-4))
        self.assertEqual(-4, myFs.extFrameNum(1))
        self.assertEqual(31, myFs.intFrameNum(-124))
        self.assertEqual(124, myFs.extFrameNum(-31))
        self.assertRaises(IndexError, myFs.intFrameNum, -1)
        self.assertRaises(IndexError, myFs.intFrameNum, 1)

    def test_15(self):
        """TestFrameSet.test_15(): Construction, _intChValIdxS."""
        myFs = FrameSet.FrameSet(self._dfsr, slice(1))
        #print()
        #print(myFs.longStr())
        #print('nbytes', myFs.nbytes)
        self.assertEqual([0, 1, 2, 6, 14], myFs._intChValIdxS)

    def test_16(self):
        """TestFrameSet.test_16(): Construction, _offsetTree."""
        # Sensor 0 (sc=1, sa=1, bu=1)
        # Sensor 1 (sc=1, sa=1, bu=1)
        # Sensor 2 (sc=1, sa=4, bu=1)
        # Sensor 3 (sc=1, sa=1, bu=8)
        # Sensor 4 (sc=1, sa=2, bu=1)
        myFs = FrameSet.FrameSet(self._dfsr, slice(1))
#        print()
#        pprint.pprint(myFs._offsetTree)
        self.assertEqual(
            {
                0: {
                        0: {
                                0: {
                                        0: 0,
                                    }
                            }
                    },
                1: {
                        0: {
                                0: {
                                        0: 1,
                                    }
                            }
                    },
                2: {
                        0: {
                                0: {
                                        0: 2,
                                    },
                                1: {
                                        0: 3,
                                    },
                                2: {
                                        0: 4,
                                    },
                                3: {
                                        0: 5,
                                    }
                            }
                    },
                3: {
                        0: {
                                0: {
                                        0: 6,
                                        1: 7,
                                        2: 8,
                                        3: 9,
                                        4: 10,
                                        5: 11,
                                        6: 12,
                                        7: 13,
                                    }
                            }
                    },
                4: {
                        0: {
                                0: {
                                        0: 14,
                                    },
                                1: {
                                        0: 15,
                                    }
                            }
                    }
             },
            myFs._offsetTree,
        )
        # Now with frameIdx()
        self.assertEqual(0, myFs.valueIdxInFrame(0, 0, 0, 0))
        self.assertEqual(1, myFs.valueIdxInFrame(1, 0, 0, 0))
        self.assertEqual(2, myFs.valueIdxInFrame(2, 0, 0, 0))
        self.assertEqual(3, myFs.valueIdxInFrame(2, 0, 1, 0))
        self.assertEqual(4, myFs.valueIdxInFrame(2, 0, 2, 0))
        self.assertEqual(5, myFs.valueIdxInFrame(2, 0, 3, 0))
        self.assertEqual(6, myFs.valueIdxInFrame(3, 0, 0, 0))
        self.assertEqual(7, myFs.valueIdxInFrame(3, 0, 0, 1))
        self.assertEqual(8, myFs.valueIdxInFrame(3, 0, 0, 2))
        self.assertEqual(9, myFs.valueIdxInFrame(3, 0, 0, 3))
        self.assertEqual(10, myFs.valueIdxInFrame(3, 0, 0, 4))
        self.assertEqual(11, myFs.valueIdxInFrame(3, 0, 0, 5))
        self.assertEqual(12, myFs.valueIdxInFrame(3, 0, 0, 6))
        self.assertEqual(13, myFs.valueIdxInFrame(3, 0, 0, 7))
        self.assertEqual(14, myFs.valueIdxInFrame(4, 0, 0, 0))
        self.assertEqual(15, myFs.valueIdxInFrame(4, 0, 1, 0))

    def test_17(self):
        """TestFrameSet.test_17(): Construction, xAxisIndex out of range failures."""
        self.assertTrue(FrameSet.FrameSet(self._dfsr, slice(1), xAxisIndex=0) is not None)
        self.assertTrue(FrameSet.FrameSet(self._dfsr, slice(1), xAxisIndex=1) is not None)
        self.assertTrue(FrameSet.FrameSet(self._dfsr, slice(1), xAxisIndex=2) is not None)
        self.assertTrue(FrameSet.FrameSet(self._dfsr, slice(1), xAxisIndex=3) is not None)
        self.assertTrue(FrameSet.FrameSet(self._dfsr, slice(1), xAxisIndex=4) is not None)
        self.assertTrue(FrameSet.FrameSet(self._dfsr, slice(1), xAxisIndex=-1) is not None)
        self.assertTrue(FrameSet.FrameSet(self._dfsr, slice(1), xAxisIndex=-2) is not None)
        self.assertTrue(FrameSet.FrameSet(self._dfsr, slice(1), xAxisIndex=-3) is not None)
        self.assertTrue(FrameSet.FrameSet(self._dfsr, slice(1), xAxisIndex=-4) is not None)
        self.assertTrue(FrameSet.FrameSet(self._dfsr, slice(1), xAxisIndex=-5) is not None)
        self.assertRaises(FrameSet.ExceptionFrameSet, FrameSet.FrameSet, self._dfsr, slice(1), xAxisIndex=-6)
        self.assertRaises(FrameSet.ExceptionFrameSet, FrameSet.FrameSet, self._dfsr, slice(1), xAxisIndex=5)
        self.assertRaises(FrameSet.ExceptionFrameSet, FrameSet.FrameSet, self._dfsr, slice(1), xAxisIndex=6)

class TestFrameSet_offsetTree(BaseTestClasses.TestBaseFile):
    """Tests FrameSet"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSet: Tests setUp() and tearDown()."""
        pass
    
    def _retMultiChFrameSet(self):
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 12, absent value -153.0
            + bytes([12, 4, 68])+b'\xbb\xb3\x80\x00'
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0 (sc=1, sa=1, bu=1)
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 1 (sc=1, sa=1, bu=1)
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'GR  ' + b'ServID' + b'ServOrdN'+ b'GAPI' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 2 (sc=1, sa=4, bu=1)
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'SUPE' + b'ServID' + b'ServOrdN'+ b'MMHO' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 16 LIS bytes     Pad      4 super  Rep code     Process indicators
            + bytes([0, 16]) + b'000' + b'\x04'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 3 (sc=1, sa=1, bu=8)
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'SMAL' + b'ServID' + b'ServOrdN'+ b'INCH' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 16 LIS bytes     Pad      1 sample Rep code     Process indicators
            + bytes([0, 16]) + b'000' + b'\x01'+ bytes([79,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 4 (sc=1, sa=2, bu=1)
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'BS  ' + b'ServID' + b'ServOrdN'+ b'MM  ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 8 LIS bytes     Pad      2 super  Rep code     Process indicators
            + bytes([0, 8]) + b'000' + b'\x02'+ bytes([73,]) + bytes([0, 1, 2, 3, 4])
        )
        myDfsr = LogiRec.LrDFSRRead(myF)
        self.assertEqual(48, myDfsr.frameSize())
        # Sensor 0 (sc=1, sa=1, bu=1)
        # Sensor 1 (sc=1, sa=1, bu=1)
        # Sensor 2 (sc=1, sa=4, bu=1)
        # Sensor 3 (sc=1, sa=1, bu=8)
        # Sensor 4 (sc=1, sa=2, bu=1)
        return FrameSet.FrameSet(myDfsr, slice(1))

    def _retDeptAndHDTFrameSet(self):
        myB = (
            bytes([64, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        # Sensor 0
        myB += (
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            b"RHDT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(90) + b'000' + bytes([1,])+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 1
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        dep = 1000.0
        v = 0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            for b in range(90):
                fBy.extend(RepCode.writeBytes66(v % 256))
                v += 1
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= 0.5
        myFs = FrameSet.FrameSet(myDfsr, slice(1))
        return myFs
    
    def test_01(self):
        """TestFrameSet_offsetTree.test_01(): Construction, _offsetTree, single and multisampled."""
        # Sensor 0 (sc=1, sa=1, bu=1)
        # Sensor 1 (sc=1, sa=1, bu=1)
        # Sensor 2 (sc=1, sa=4, bu=1)
        # Sensor 3 (sc=1, sa=1, bu=8)
        # Sensor 4 (sc=1, sa=2, bu=1)
        myFs = self._retMultiChFrameSet()
#        print()
#        pprint.pprint(myFs._offsetTree)
        self.assertEqual(
            #   ch      sc     sa      bu
            {   # Sensor 0 (sc=1, sa=1, bu=1)
                0: {
                        0: {
                                0: {
                                        0: 0,
                                    }
                            }
                    },
                # Sensor 1 (sc=1, sa=1, bu=1)
                1: {
                        0: {
                                0: {
                                        0: 1,
                                    }
                            }
                    },
                # Sensor 2 (sc=1, sa=4, bu=1)
                2: {
                        0: {
                                0: {
                                        0: 2,
                                    },
                                1: {
                                        0: 3,
                                    },
                                2: {
                                        0: 4,
                                    },
                                3: {
                                        0: 5,
                                    }
                            }
                    },
                # Sensor 3 (sc=1, sa=1, bu=8)
                3: {
                        0: {
                                0: {
                                        0: 6,
                                        1: 7,
                                        2: 8,
                                        3: 9,
                                        4: 10,
                                        5: 11,
                                        6: 12,
                                        7: 13,
                                    }
                            }
                    },
                # Sensor 4 (sc=1, sa=2, bu=1)
                4: {
                        0: {
                                0: {
                                        0: 14,
                                    },
                                1: {
                                        0: 15,
                                    }
                            }
                    }
             },
            myFs._offsetTree,
        )
        # Now with frameIdx()
        self.assertEqual(0, myFs.valueIdxInFrame(0, 0, 0, 0))
        self.assertEqual(1, myFs.valueIdxInFrame(1, 0, 0, 0))
        self.assertEqual(2, myFs.valueIdxInFrame(2, 0, 0, 0))
        self.assertEqual(3, myFs.valueIdxInFrame(2, 0, 1, 0))
        self.assertEqual(4, myFs.valueIdxInFrame(2, 0, 2, 0))
        self.assertEqual(5, myFs.valueIdxInFrame(2, 0, 3, 0))
        self.assertEqual(6, myFs.valueIdxInFrame(3, 0, 0, 0))
        self.assertEqual(7, myFs.valueIdxInFrame(3, 0, 0, 1))
        self.assertEqual(8, myFs.valueIdxInFrame(3, 0, 0, 2))
        self.assertEqual(9, myFs.valueIdxInFrame(3, 0, 0, 3))
        self.assertEqual(10, myFs.valueIdxInFrame(3, 0, 0, 4))
        self.assertEqual(11, myFs.valueIdxInFrame(3, 0, 0, 5))
        self.assertEqual(12, myFs.valueIdxInFrame(3, 0, 0, 6))
        self.assertEqual(13, myFs.valueIdxInFrame(3, 0, 0, 7))
        self.assertEqual(14, myFs.valueIdxInFrame(4, 0, 0, 0))
        self.assertEqual(15, myFs.valueIdxInFrame(4, 0, 1, 0))

    def test_02(self):
        """TestFrameSet_offsetTree.test_02(): Construction, _offsetTree, DEPT+dipmeter (RHDT)."""
        myFs = self._retDeptAndHDTFrameSet()
#        print()
#        pprint.pprint(myFs._offsetTree)
        # ch, sc, sa, bu -> offset
        expTree = {
        #   ch  sc  sa  bu: offset
             0: {0: {0: {0: 0}}},
             1: {0: {0: {0: {0: 1},
                         1: {0: 6},
                         2: {0: 11},
                         3: {0: 16},
                         4: {0: 21},
                         5: {0: 26},
                         6: {0: 31},
                         7: {0: 36},
                         8: {0: 41},
                         9: {0: 46},
                         10: {0: 51},
                         11: {0: 56},
                         12: {0: 61},
                         13: {0: 66},
                         14: {0: 71},
                         15: {0: 76}}},
                 1: {1: {0: {0: 2},
                         1: {0: 7},
                         2: {0: 12},
                         3: {0: 17},
                         4: {0: 22},
                         5: {0: 27},
                         6: {0: 32},
                         7: {0: 37},
                         8: {0: 42},
                         9: {0: 47},
                         10: {0: 52},
                         11: {0: 57},
                         12: {0: 62},
                         13: {0: 67},
                         14: {0: 72},
                         15: {0: 77}}},
                 2: {2: {0: {0: 3},
                         1: {0: 8},
                         2: {0: 13},
                         3: {0: 18},
                         4: {0: 23},
                         5: {0: 28},
                         6: {0: 33},
                         7: {0: 38},
                         8: {0: 43},
                         9: {0: 48},
                         10: {0: 53},
                         11: {0: 58},
                         12: {0: 63},
                         13: {0: 68},
                         14: {0: 73},
                         15: {0: 78}}},
                 3: {3: {0: {0: 4},
                         1: {0: 9},
                         2: {0: 14},
                         3: {0: 19},
                         4: {0: 24},
                         5: {0: 29},
                         6: {0: 34},
                         7: {0: 39},
                         8: {0: 44},
                         9: {0: 49},
                         10: {0: 54},
                         11: {0: 59},
                         12: {0: 64},
                         13: {0: 69},
                         14: {0: 74},
                         15: {0: 79}}},
                 4: {4: {0: {0: 5},
                         1: {0: 10},
                         2: {0: 15},
                         3: {0: 20},
                         4: {0: 25},
                         5: {0: 30},
                         6: {0: 35},
                         7: {0: 40},
                         8: {0: 45},
                         9: {0: 50},
                         10: {0: 55},
                         11: {0: 60},
                         12: {0: 65},
                         13: {0: 70},
                         14: {0: 75},
                         15: {0: 80}}},
                 5: {5: {0: {0: 81}}},
                 6: {6: {0: {0: 82}}},
                 7: {7: {0: {0: 83}}},
                 8: {8: {0: {0: 84}}},
                 9: {9: {0: {0: 85}}},
                 10: {10: {0: {0: 86}}},
                 11: {11: {0: {0: 87}}},
                 12: {12: {0: {0: 88}}},
                 13: {13: {0: {0: 89}}},
                 14: {14: {0: {0: 90}}}}}
        self.assertEqual(expTree, myFs._offsetTree)

    def test_10(self):
        """TestFrameSet_offsetTree.test_02(): Construction, _retDipSubChannelOffsetBranch(), DEPT+dipmeter (RHDT)."""
        myFs = self._retDeptAndHDTFrameSet()
#        print()
#        pprint.pprint(myFs._retDipSubChannelOffsetBranch(5, 0))
        #   sc  sa  bu: offset
        self.assertEqual(
            {0: {0: {0: 0},
                 1: {0: 5},
                 2: {0: 10},
                 3: {0: 15},
                 4: {0: 20},
                 5: {0: 25},
                 6: {0: 30},
                 7: {0: 35},
                 8: {0: 40},
                 9: {0: 45},
                 10: {0: 50},
                 11: {0: 55},
                 12: {0: 60},
                 13: {0: 65},
                 14: {0: 70},
                 15: {0: 75}}},
            myFs._retDipSubChannelOffsetBranch(0, 0))
        self.assertEqual(
            {4: {0: {0: 4},
                 1: {0: 9},
                 2: {0: 14},
                 3: {0: 19},
                 4: {0: 24},
                 5: {0: 29},
                 6: {0: 34},
                 7: {0: 39},
                 8: {0: 44},
                 9: {0: 49},
                 10: {0: 54},
                 11: {0: 59},
                 12: {0: 64},
                 13: {0: 69},
                 14: {0: 74},
                 15: {0: 79}}},
            myFs._retDipSubChannelOffsetBranch(4, 0))
        self.assertEqual(
            {0: {0: {0: 4},
                 1: {0: 9},
                 2: {0: 14},
                 3: {0: 19},
                 4: {0: 24},
                 5: {0: 29},
                 6: {0: 34},
                 7: {0: 39},
                 8: {0: 44},
                 9: {0: 49},
                 10: {0: 54},
                 11: {0: 59},
                 12: {0: 64},
                 13: {0: 69},
                 14: {0: 74},
                 15: {0: 79}}},
            myFs._retDipSubChannelOffsetBranch(0, 4))
        self.assertEqual({5: {0: {0: 81}}}, myFs._retDipSubChannelOffsetBranch(5, 1))
        self.assertEqual({6: {0: {0: 82}}}, myFs._retDipSubChannelOffsetBranch(6, 1))
        self.assertEqual({14: {0: {0: 90}}}, myFs._retDipSubChannelOffsetBranch(14, 1))

    def test_20(self):
        """TestFrameSet_offsetTree.test_20(): Construction, _sliceTree, single and multisampled."""
        # Sensor 0 (sc=1, sa=1, bu=1) 1
        # Sensor 1 (sc=1, sa=1, bu=1) 1
        # Sensor 2 (sc=1, sa=4, bu=1) 4
        # Sensor 3 (sc=1, sa=1, bu=8) 8
        # Sensor 4 (sc=1, sa=2, bu=1) 2
        myFs = self._retMultiChFrameSet()
#        print()
#        pprint.pprint(myFs._sliceTree)
        self.assertEqual(
            #   ch      sc  slice
            {
                0: {0: slice(0, 1, 1)},
                1: {0: slice(1, 2, 1)},
                2: {0: slice(2, 6, 1)},
                3: {0: slice(6, 14, 1)},
                4: {0: slice(14, 16, 1)},
            },
            myFs._sliceTree,
        )

    def test_21(self):
        """TestFrameSet_offsetTree.test_21(): Construction, _sliceTree, HDT."""
        myFs = self._retDeptAndHDTFrameSet()
#        print()
#        pprint.pprint(myFs._sliceTree)
        self.assertEqual(
            #   ch      sc  slice
            {
                0: {0: slice(0, 1, 1)},
                1: {0: slice(1, 81, 5),
                    1: slice(2, 81, 5),
                    2: slice(3, 81, 5),
                    3: slice(4, 81, 5),
                    4: slice(5, 81, 5),
                    5: slice(81, 82, 1),
                    6: slice(82, 83, 1),
                    7: slice(83, 84, 1),
                    8: slice(84, 85, 1),
                    9: slice(85, 86, 1),
                    10: slice(86, 87, 1),
                    11: slice(87, 88, 1),
                    12: slice(88, 89, 1),
                    13: slice(89, 90, 1),
                    14: slice(90, 91, 1)}
            },
            myFs._sliceTree,
        )

    
class TestFrameSet_setFrameBytes(BaseTestClasses.TestBaseFile):
    """Tests FrameSet"""
    def setUp(self):
        """Set up."""
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
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
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'GR  ' + b'ServID' + b'ServOrdN'+ b'GAPI' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 2
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'SUPE' + b'ServID' + b'ServOrdN'+ b'MMHO' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 16 LIS bytes     Pad      4 super  Rep code     Process indicators
            + bytes([0, 16]) + b'000' + b'\x04'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 3
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'SMAL' + b'ServID' + b'ServOrdN'+ b'INCH' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 16 LIS bytes     Pad      1 sample Rep code     Process indicators
            + bytes([0, 16]) + b'000' + b'\x01'+ bytes([79,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 4
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'BS  ' + b'ServID' + b'ServOrdN'+ b'MM  ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 8 LIS bytes     Pad      2 super  Rep code     Process indicators
            + bytes([0, 8]) + b'000' + b'\x02'+ bytes([73,]) + bytes([0, 1, 2, 3, 4])
        )
        self._dfsr = LogiRec.LrDFSRRead(myF)
        self.assertEqual(48, self._dfsr.frameSize())

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSet: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSet_setFrameBytes.test_00(): setFrameBytes() all channels."""
        myFs = FrameSet.FrameSet(self._dfsr, slice(1))
        self.assertEqual([0, 1, 2, 6, 14], myFs._intChValIdxS)
        self.assertEqual(1, myFs.numFrames)
        self.assertEqual(16, myFs.valuesPerFrame)
        self.assertEqual(128, myFs.nbytes)
        #print()
        #print(myFs.longStr())
        #print('nbytes', myFs.nbytes)
        by = b'\x44\x4C\x80\x00' * 6 \
            + b'\x00\x00\x00\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\x06\x00\x07' \
            + b'\x00\x00\x01\x00\x00\x00\x01\x01'
        myFs.setFrameBytes(by, 0, 0, 4)
        #print('myFs.frame(0)\n', myFs.frame(0), type(myFs.frame(0)))
        expVal = numpy.array(
            [
                153., 153., 153., 153., 153., 153.,
                0., 1., 2., 3., 4., 5., 6., 7., 
                256., 257.,
            ]
        )
        self.assertTrue((expVal == myFs.frame(0)).all())

    def test_01(self):
        """TestFrameSet_setFrameBytes.test_01(): setFrameBytes() fails on channel None."""
        myFs = FrameSet.FrameSet(self._dfsr, slice(1))
        self.assertRaises(FrameSet.ExceptionFrameSet, myFs.setFrameBytes, b'', 0, None, 4)

    def test_02(self):
        """TestFrameSet_setFrameBytes.test_02(): setFrameBytes() fails on buffer under-run."""
        myFs = FrameSet.FrameSet(self._dfsr, slice(1))
        self.assertRaises(FrameSet.ExceptionFrameSet, myFs.setFrameBytes, b'', 0, 0, 0)

    def test_03(self):
        """TestFrameSet_setFrameBytes.test_03(): setFrameBytes() fails on buffer over-run."""
        myFs = FrameSet.FrameSet(self._dfsr, slice(1))
        self.assertRaises(FrameSet.ExceptionFrameSet, myFs.setFrameBytes, b'\x00\x00\x00\x00\x00', 0, 0, 0)

class TestFrameSet_setFrameBytes_Indirect(BaseTestClasses.TestBaseFile):
    """Tests FrameSet"""
    def setUp(self):
        """Set up."""
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 8, Frame spacing
            + bytes([8, 1, 66, 60])
            # EB 9, Frame spacing units
            + bytes([9, 4, 65])+b'.1IN'
            # EB 13, recording mode 1
            + bytes([13, 1, 66, 1])
            # EB 14, X axis units
            + bytes([14, 4, 65])+b'.1IN'
            # EB 15, indirect Rep Code 73
            + bytes([15, 1, 66, 73])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'GR  ' + b'ServID' + b'ServOrdN'+ b'GAPI' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 1
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'SUPE' + b'ServID' + b'ServOrdN'+ b'MMHO' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 16 LIS bytes     Pad      4 super  Rep code     Process indicators
            + bytes([0, 16]) + b'000' + b'\x04'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 2
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'SMAL' + b'ServID' + b'ServOrdN'+ b'INCH' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 16 LIS bytes     Pad      1 sample Rep code     Process indicators
            + bytes([0, 16]) + b'000' + b'\x01'+ bytes([79,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 3
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'BS  ' + b'ServID' + b'ServOrdN'+ b'MM  ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 8 LIS bytes     Pad      2 super  Rep code     Process indicators
            + bytes([0, 8]) + b'000' + b'\x02'+ bytes([73,]) + bytes([0, 1, 2, 3, 4])
        )
        self._dfsr = LogiRec.LrDFSRRead(myF)
        self.assertEqual(44, self._dfsr.frameSize())
        
    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSet_setFrameBytes_Indirect: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSet_setFrameBytes_Indirect.test_00(): setFrameBytes() all channels, indirect X axis."""
        myFs = FrameSet.FrameSet(self._dfsr, slice(1))
        self.assertEqual([0, 1, 5, 13], myFs._intChValIdxS)
        self.assertEqual(1, myFs.numFrames)
        self.assertEqual(15, myFs.valuesPerFrame)
        self.assertEqual(120, myFs.nbytes)
        #print()
        #print(myFs.longStr())
        by = b'\x00\x01\x00\x00' \
            + b'\x44\x4C\x80\x00' * 5 \
            + b'\x00\x00\x00\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\x06\x00\x07' \
            + b'\x00\x00\x01\x00\x00\x00\x01\x01'
        myFs.setFrameBytes(by, 0, None, 3)
        #print('myFs.frame(0)\n', myFs.frame(0))
        expVal = numpy.array(
            [
                153., 153., 153., 153., 153.,
                0., 1., 2., 3., 4., 5., 6., 7., 
                256., 257.,
            ]
        )
        #print((expVal == myFs.frame(0)))
        self.assertEqual(expVal.shape, myFs.frame(0).shape)
        self.assertTrue((expVal == myFs.frame(0)).all())
        self.assertEqual(65536.0, myFs.xAxisValue(0))

    def test_01(self):
        """TestFrameSet_setFrameBytes_Indirect.test_01(): setFrameBytes() indirect X axis channel only."""
        myFs = FrameSet.FrameSet(self._dfsr, slice(1))
        self.assertEqual([0, 1, 5, 13], myFs._intChValIdxS)
        self.assertEqual(1, myFs.numFrames)
        self.assertEqual(15, myFs.valuesPerFrame)
        self.assertEqual(120, myFs.nbytes)
        #print()
        #print(myFs.longStr())
        by = b'\x00\x01\x00\x00'
        myFs.setFrameBytes(by, 0, None, None)
        self.assertEqual(65536.0, myFs.xAxisValue(0))

    def test_02(self):
        """TestFrameSet_setFrameBytes_Indirect.test_02(): setFrameBytes() indirect X axis channel only, under-run."""
        myFs = FrameSet.FrameSet(self._dfsr, slice(1))
        by = b'\x00\x01\x00'
        self.assertRaises(FrameSet.ExceptionFrameSet, myFs.setFrameBytes, by, 0, None, None)

    def test_03(self):
        """TestFrameSet_setFrameBytes_Indirect.test_03(): setFrameBytes() indirect X axis channel only, over-run."""
        myFs = FrameSet.FrameSet(self._dfsr, slice(1))
        by = b'\x00\x01\x00\x00\x00'
        self.assertRaises(FrameSet.ExceptionFrameSet, myFs.setFrameBytes, by, 0, None, None)

class TestFrameSetAccumulate(BaseTestClasses.TestBaseLogPass):
    """Test the FrameSet accumulate()."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSetAccumulate: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSetAccumulate.test_00(): 8 frames of 5 channels, using accumulate() max/min/mean."""
        numCh = 5
        numFr = 8
        myFile = self._createFileDFSROnly(numCh, 1, 1)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        v = 0.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray()
            for ch in range(numCh):
                fBy.extend(RepCode.writeBytes68(v))
                v += 1.0
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=numCh-1)
        #[FrameSet.AccMax, FrameSet.AccMin, FrameSet.AccMean])
        myArray = myFs.accumulate([FrameSet.AccMin, FrameSet.AccMean, FrameSet.AccMax])
        #print()
        #print(myFs.frame(0))
        #print()
        #print(myFs._frames)
        expVal = numpy.array(
            [
                [  0.,   1.,   2.,   3.,   4.,],
                [  5.,   6.,   7.,   8.,   9.,],
                [ 10.,  11.,  12.,  13.,  14.,],
                [ 15.,  16.,  17.,  18.,  19.,],
                [ 20.,  21.,  22.,  23.,  24.,],
                [ 25.,  26.,  27.,  28.,  29.,],
                [ 30.,  31.,  32.,  33.,  34.,],
                [ 35.,  36.,  37.,  38.,  39.,],
            ]
        )
        self.assertEqual(expVal.shape, myFs.frames.shape)
        self.assertTrue((expVal == myFs.frames).all())
        #print()
        #pprint.pprint(myArray)
        expVal = numpy.array(
            [
                [0.,    17.5,   35.,],
                [1.,    18.5,   36.,],
                [2.,    19.5,   37.,],
                [3.,    20.5,   38.,],
                [4.,    21.5,   39.,],
             ]
        )
        #print((expVal == myFs.frame(0)))
        self.assertEqual(expVal.shape, myArray.shape)
        self.assertTrue((expVal == myArray).all())

    def test_01(self):
        """TestFrameSetAccumulate.test_01(): 1 frame of DEPT + Dipmeter 243, using accumulate() max/min/mean."""
        myB = (
            bytes([64, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        # Sensor 0
        myB += (
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            b"RHDT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(90) + b'000' + bytes([1,])+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 1
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        dep = 1000.0
        v = 0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            for b in range(90):
                fBy.extend(RepCode.writeBytes66(v % 256))
                v += 1
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= 0.5
        #print()
        #pprint.pprint(myFs._frames)
        expVal = numpy.array(
            [
                [1000.,     0.,     1.,     2.,     3.,     4.,     5.,     6.,
                  7.,     8.,     9.,    10.,    11.,    12.,    13.,    14.,
                 15.,    16.,    17.,    18.,    19.,    20.,    21.,    22.,
                 23.,    24.,    25.,    26.,    27.,    28.,    29.,    30.,
                 31.,    32.,    33.,    34.,    35.,    36.,    37.,    38.,
                 39.,    40.,    41.,    42.,    43.,    44.,    45.,    46.,
                 47.,    48.,    49.,    50.,    51.,    52.,    53.,    54.,
                 55.,    56.,    57.,    58.,    59.,    60.,    61.,    62.,
                 63.,    64.,    65.,    66.,    67.,    68.,    69.,    70.,
                 71.,    72.,    73.,    74.,    75.,    76.,    77.,    78.,
                 79.,    80.,    81.,    82.,    83.,    84.,    85.,    86.,
                 87.,    88.,    89.]
            ]
        )
        self.assertEqual(expVal.shape, myFs._frames.shape)
        self.assertTrue((expVal == myFs._frames).all())
        # Create accumulator array
        myArray = myFs.accumulate([FrameSet.AccMin, FrameSet.AccMean, FrameSet.AccMax])
        #print()
        #print(myArray)
        #pprint.pprint(myArray)
        expVal = numpy.array(
            [
                [ 1000. ,  1000. ,  1000. ],
                [    0. ,    37.5,    75. ],
                [    1. ,    38.5,    76. ],
                [    2. ,    39.5,    77. ],
                [    3. ,    40.5,    78. ],
                [    4. ,    41.5,    79. ],
                [   80. ,    80. ,    80. ],
                [   81. ,    81. ,    81. ],
                [   82. ,    82. ,    82. ],
                [   83. ,    83. ,    83. ],
                [   84. ,    84. ,    84. ],
                [   85. ,    85. ,    85. ],
                [   86. ,    86. ,    86. ],
                [   87. ,    87. ,    87. ],
                [   88. ,    88. ,    88. ],
                [   89. ,    89. ,    89. ],
            ]
        )
        self.assertEqual(expVal.shape, myArray.shape)
        self.assertTrue((expVal == myArray).all())

    def test_02(self):
        """TestFrameSetAccumulate.test_02(): 256 frames of DEPT + Dipmeter 243, using accumulate() max/min/mean."""
        myB = (
            bytes([64, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        # Sensor 0
        myB += (
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            b"RHDT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(90) + b'000' + bytes([1,])+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 256
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        dep = 1000.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            for b in range(90):
                fBy.extend(RepCode.writeBytes66(f % 256))
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= 0.5
        #print()
        #pprint.pprint(myFs._frames)
        self.assertEqual((numFr, 91), myFs._frames.shape)
        #self.assertTrue((expVal == myFs._frames).all())
        # Create accumulator array
        myArray = myFs.accumulate([FrameSet.AccMin, FrameSet.AccMean, FrameSet.AccMax])
        #print()
        #print(myArray)
        #pprint.pprint(myArray)
        expVal = numpy.array(
            [
                [  872.5 ,   936.25,  1000. ],
                [    0.  ,   127.5 ,   255.  ],
                [    0.  ,   127.5 ,   255.  ],
                [    0.  ,   127.5 ,   255.  ],
                [    0.  ,   127.5 ,   255.  ],
                [    0.  ,   127.5 ,   255.  ],
                [    0.  ,   127.5 ,   255.  ],
                [    0.  ,   127.5 ,   255.  ],
                [    0.  ,   127.5 ,   255.  ],
                [    0.  ,   127.5 ,   255.  ],
                [    0.  ,   127.5 ,   255.  ],
                [    0.  ,   127.5 ,   255.  ],
                [    0.  ,   127.5 ,   255.  ],
                [    0.  ,   127.5 ,   255.  ],
                [    0.  ,   127.5 ,   255.  ],
                [    0.  ,   127.5 ,   255.  ],
            ]
        )
        self.assertEqual(expVal.shape, myArray.shape)
        self.assertTrue((expVal == myArray).all())

    def test_03(self):
        """TestFrameSetAccumulate.test_03(): indirect DEPT, 4 frames of Dipmeter 243, using accumulate() max/min/mean."""
        xAxisRc = 73
        myB = (
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 8, Frame spacing
            + bytes([8, 1, 66, 60])
            # EB 9, Frame spacing units
            + bytes([9, 4, 65])+b'.1IN'
            # EB 13, recording mode 1
            + bytes([13, 1, 66, 1])
            # EB 14, X axis units
            + bytes([14, 4, 65])+b'.1IN'
            # EB 15, indirect Rep Code 73
            + bytes([15, 1, 66, xAxisRc])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
        )
        # Sensor 0
        myB += (
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            b"RHDT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(90) + b'000' + bytes([1,])+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 4
        #print()
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        dep = 1000 * 120 # 1000 feet at 0.1 inch
        v = 0
        # Load the first frame set with the indirect depth
        fBy = bytearray(RepCode.writeBytes(dep, xAxisRc))
        for b in range(90):
            fBy.extend(RepCode.writeBytes66(v % 255))
            v += 1
        dep -= 60
        myFs.setFrameBytes(by=fBy, fr=0, chFrom=None, chTo=0)
        # Now load the rest of the FrameSet with only the channel data
        for f in range(1, numFr):
            fBy = bytearray()
            for b in range(90):
                fBy.extend(RepCode.writeBytes66(v % 255))
                v += 1
            # Set frame
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=0)
            # Set indirect depth directly
            myFs.setIndirectX(f, dep)
            dep -= 60
        #print()
        #pprint.pprint(myFs._frames)
        expVal = numpy.array(
            [
                [   0.,    1.,    2.,    3.,    4.,    5.,    6.,    7.,    8.,
                     9.,   10.,   11.,   12.,   13.,   14.,   15.,   16.,   17.,
                    18.,   19.,   20.,   21.,   22.,   23.,   24.,   25.,   26.,
                    27.,   28.,   29.,   30.,   31.,   32.,   33.,   34.,   35.,
                    36.,   37.,   38.,   39.,   40.,   41.,   42.,   43.,   44.,
                    45.,   46.,   47.,   48.,   49.,   50.,   51.,   52.,   53.,
                    54.,   55.,   56.,   57.,   58.,   59.,   60.,   61.,   62.,
                    63.,   64.,   65.,   66.,   67.,   68.,   69.,   70.,   71.,
                    72.,   73.,   74.,   75.,   76.,   77.,   78.,   79.,   80.,
                    81.,   82.,   83.,   84.,   85.,   86.,   87.,   88.,   89.],
                 [  90.,   91.,   92.,   93.,   94.,   95.,   96.,   97.,   98.,
                    99.,  100.,  101.,  102.,  103.,  104.,  105.,  106.,  107.,
                   108.,  109.,  110.,  111.,  112.,  113.,  114.,  115.,  116.,
                   117.,  118.,  119.,  120.,  121.,  122.,  123.,  124.,  125.,
                   126.,  127.,  128.,  129.,  130.,  131.,  132.,  133.,  134.,
                   135.,  136.,  137.,  138.,  139.,  140.,  141.,  142.,  143.,
                   144.,  145.,  146.,  147.,  148.,  149.,  150.,  151.,  152.,
                   153.,  154.,  155.,  156.,  157.,  158.,  159.,  160.,  161.,
                   162.,  163.,  164.,  165.,  166.,  167.,  168.,  169.,  170.,
                   171.,  172.,  173.,  174.,  175.,  176.,  177.,  178.,  179.],
                 [ 180.,  181.,  182.,  183.,  184.,  185.,  186.,  187.,  188.,
                   189.,  190.,  191.,  192.,  193.,  194.,  195.,  196.,  197.,
                   198.,  199.,  200.,  201.,  202.,  203.,  204.,  205.,  206.,
                   207.,  208.,  209.,  210.,  211.,  212.,  213.,  214.,  215.,
                   216.,  217.,  218.,  219.,  220.,  221.,  222.,  223.,  224.,
                   225.,  226.,  227.,  228.,  229.,  230.,  231.,  232.,  233.,
                   234.,  235.,  236.,  237.,  238.,  239.,  240.,  241.,  242.,
                   243.,  244.,  245.,  246.,  247.,  248.,  249.,  250.,  251.,
                   252.,  253.,  254.,    0.,    1.,    2.,    3.,    4.,    5.,
                     6.,    7.,    8.,    9.,   10.,   11.,   12.,   13.,   14.],
                 [  15.,   16.,   17.,   18.,   19.,   20.,   21.,   22.,   23.,
                    24.,   25.,   26.,   27.,   28.,   29.,   30.,   31.,   32.,
                    33.,   34.,   35.,   36.,   37.,   38.,   39.,   40.,   41.,
                    42.,   43.,   44.,   45.,   46.,   47.,   48.,   49.,   50.,
                    51.,   52.,   53.,   54.,   55.,   56.,   57.,   58.,   59.,
                    60.,   61.,   62.,   63.,   64.,   65.,   66.,   67.,   68.,
                    69.,   70.,   71.,   72.,   73.,   74.,   75.,   76.,   77.,
                    78.,   79.,   80.,   81.,   82.,   83.,   84.,   85.,   86.,
                    87.,   88.,   89.,   90.,   91.,   92.,   93.,   94.,   95.,
                    96.,   97.,   98.,   99.,  100.,  101.,  102.,  103.,  104.]
             ]
        )
        self.assertEqual(expVal.shape, myFs._frames.shape)
        self.assertTrue((expVal == myFs._frames).all())
        # Create accumulator array
        myArray = myFs.accumulate([FrameSet.AccMin, FrameSet.AccMean, FrameSet.AccMax])
        #print()
        ##print(myArray)
        #pprint.pprint(myArray)
        expVal = numpy.array(
            [
                [   0.      ,  104.765625,  250.      ],
                [   1.      ,  105.765625,  251.      ],
                [   2.      ,  106.765625,  252.      ],
                [   3.      ,  107.765625,  253.      ],
                [   4.      ,  108.765625,  254.      ],
                [   5.      ,   87.5     ,  170.      ],
                [   6.      ,   88.5     ,  171.      ],
                [   7.      ,   89.5     ,  172.      ],
                [   8.      ,   90.5     ,  173.      ],
                [   9.      ,   91.5     ,  174.      ],
                [  10.      ,   92.5     ,  175.      ],
                [  11.      ,   93.5     ,  176.      ],
                [  12.      ,   94.5     ,  177.      ],
                [  13.      ,   95.5     ,  178.      ],
                [  14.      ,   96.5     ,  179.      ]
            ]
        )
        self.assertEqual(expVal.shape, myArray.shape)
        self.assertTrue((expVal == myArray).all())
        #print()
        #pprint.pprint(myFs._indrXVector)
        expVal = numpy.array([ 120000.,  119940.,  119880.,  119820.])
        self.assertEqual(expVal.shape, myFs._indrXVector.shape)
        self.assertTrue((expVal == myFs._indrXVector).all())

    def test_10(self):
        """TestFrameSet_Perf_Read.test_10(): using accumulate() max/min/mean on empty frameset raises."""
        numCh = 4
        numSa = 1
        numBu = 1
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        numFr = 0
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        try:
            myFs.accumulate([FrameSet.AccMax, FrameSet.AccMin, FrameSet.AccMean])
            self.fail('FrameSet.ExceptionFrameSetEmpty not raised')
        except FrameSet.ExceptionFrameSetEmpty:
            pass

    def test_11(self):
        """TestFrameSet_Perf_Read.test_11(): using accumulate() with empty list of accumulators returns None."""
        numCh = 5
        numFr = 8
        myFile = self._createFileDFSROnly(numCh, 1, 1)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        v = 0.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray()
            for ch in range(numCh):
                fBy.extend(RepCode.writeBytes68(v))
                v += 1.0
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=numCh-1)
        self.assertTrue(myFs.accumulate([]) is None)

    def test_20(self):
        """TestFrameSetAccumulate.test_21(): 8 frames of 5 channels, using accumulate() dec/eq/inc - all decreasing."""
        numCh = 5
        numFr = 8
        myFile = self._createFileDFSROnly(numCh, 1, 1)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        v = 0.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray()
            for ch in range(numCh):
                fBy.extend(RepCode.writeBytes68(v))
                v -= 1.0
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=numCh-1)
        #[FrameSet.AccMax, FrameSet.AccMin, FrameSet.AccMean])
        myArray = myFs.accumulate([FrameSet.AccDec, FrameSet.AccEq, FrameSet.AccInc])
        #print()
        #print(myFs.frame(0))
#        print()
#        print(myFs._frames)
        expVal = numpy.array(
            [
                [  0.,  -1.,  -2.,  -3.,  -4.,],
                [ -5.,  -6.,  -7.,  -8.,  -9.,],
                [-10., -11., -12., -13., -14.,],
                [-15., -16., -17., -18., -19.,],
                [-20., -21., -22., -23., -24.,],
                [-25., -26., -27., -28., -29.,],
                [-30., -31., -32., -33., -34.,],
                [-35., -36., -37., -38., -39.,],
            ]
        )
        self.assertEqual(expVal.shape, myFs.frames.shape)
        self.assertTrue((expVal == myFs.frames).all())
#        print()
#        pprint.pprint(myArray)
        expVal = numpy.array(
            [
                [ 7.,  0.,  0.],
                [ 7.,  0.,  0.],
                [ 7.,  0.,  0.],
                [ 7.,  0.,  0.],
                [ 7.,  0.,  0.],
             ]
        )
        #print((expVal == myFs.frame(0)))
        self.assertEqual(expVal.shape, myArray.shape)
        self.assertTrue((expVal == myArray).all())

    def test_21(self):
        """TestFrameSetAccumulate.test_21(): 8 frames of 5 channels, using accumulate() dec/eq/inc - all equal."""
        numCh = 5
        numFr = 8
        myFile = self._createFileDFSROnly(numCh, 1, 1)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        v = 0.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray()
            for ch in range(numCh):
                fBy.extend(RepCode.writeBytes68(v))
#                v += 1.0
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=numCh-1)
        #[FrameSet.AccMax, FrameSet.AccMin, FrameSet.AccMean])
        myArray = myFs.accumulate([FrameSet.AccDec, FrameSet.AccEq, FrameSet.AccInc])
        #print()
        #print(myFs.frame(0))
        #print()
        #print(myFs._frames)
        expVal = numpy.array(
            [
                [  0.,   0.,   0.,   0.,   0.,],
                [  0.,   0.,   0.,   0.,   0.,],
                [  0.,   0.,   0.,   0.,   0.,],
                [  0.,   0.,   0.,   0.,   0.,],
                [  0.,   0.,   0.,   0.,   0.,],
                [  0.,   0.,   0.,   0.,   0.,],
                [  0.,   0.,   0.,   0.,   0.,],
                [  0.,   0.,   0.,   0.,   0.,],
            ]
        )
        self.assertEqual(expVal.shape, myFs.frames.shape)
        self.assertTrue((expVal == myFs.frames).all())
#        print()
#        pprint.pprint(myArray)
        expVal = numpy.array(
            [
                [ 0.,  7.,  0.],
                [ 0.,  7.,  0.],
                [ 0.,  7.,  0.],
                [ 0.,  7.,  0.],
                [ 0.,  7.,  0.],
             ]
        )
        #print((expVal == myFs.frame(0)))
        self.assertEqual(expVal.shape, myArray.shape)
        self.assertTrue((expVal == myArray).all())

    def test_22(self):
        """TestFrameSetAccumulate.test_22(): 8 frames of 5 channels, using accumulate() dec/eq/inc - all increasing."""
        numCh = 5
        numFr = 8
        myFile = self._createFileDFSROnly(numCh, 1, 1)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        v = 0.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray()
            for ch in range(numCh):
                fBy.extend(RepCode.writeBytes68(v))
                v += 1.0
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=numCh-1)
        #[FrameSet.AccMax, FrameSet.AccMin, FrameSet.AccMean])
        myArray = myFs.accumulate([FrameSet.AccDec, FrameSet.AccEq, FrameSet.AccInc])
        #print()
        #print(myFs.frame(0))
        #print()
        #print(myFs._frames)
        expVal = numpy.array(
            [
                [  0.,   1.,   2.,   3.,   4.,],
                [  5.,   6.,   7.,   8.,   9.,],
                [ 10.,  11.,  12.,  13.,  14.,],
                [ 15.,  16.,  17.,  18.,  19.,],
                [ 20.,  21.,  22.,  23.,  24.,],
                [ 25.,  26.,  27.,  28.,  29.,],
                [ 30.,  31.,  32.,  33.,  34.,],
                [ 35.,  36.,  37.,  38.,  39.,],
            ]
        )
        self.assertEqual(expVal.shape, myFs.frames.shape)
        self.assertTrue((expVal == myFs.frames).all())
#        print()
#        pprint.pprint(myArray)
        expVal = numpy.array(
            [
                [ 0.,  0.,  7.],
                [ 0.,  0.,  7.],
                [ 0.,  0.,  7.],
                [ 0.,  0.,  7.],
                [ 0.,  0.,  7.],
             ]
        )
        #print((expVal == myFs.frame(0)))
        self.assertEqual(expVal.shape, myArray.shape)
        self.assertTrue((expVal == myArray).all())

class TestFrameSetgenChScValues(BaseTestClasses.TestBaseLogPass):
    """Test the FrameSet genChScValues()."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSetgenChScValues: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSetgenChScValues.test_00(): 8 frames of 5 channels, using genChScValues(), +ve indexes."""
        numCh = 5
        numFr = 8
        myFile = self._createFileDFSROnly(numCh, 1, 1)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        v = 0.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray()
            for ch in range(numCh):
                fBy.extend(RepCode.writeBytes68(v))
                v += 1.0
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=numCh-1)
        #print()
        actValS = [v for v in myFs.genChScValues(0, 0)]
        #print(actValS)
        baseValS = [float(x) for x in range(0, 40, 5)]
        self.assertEqual(baseValS, [v for v in myFs.genChScValues(0, 0)])
        self.assertEqual([b+1 for b in baseValS], [v for v in myFs.genChScValues(1, 0)])
        self.assertEqual([b+2 for b in baseValS], [v for v in myFs.genChScValues(2, 0)])
        self.assertEqual([b+3 for b in baseValS], [v for v in myFs.genChScValues(3, 0)])
        self.assertEqual([b+4 for b in baseValS], [v for v in myFs.genChScValues(4, 0)])
        # Indexing out of range
        try:
            [v for v in myFs.genChScValues(0, 1)]
        except IndexError:
            pass
        try:
            [v for v in myFs.genChScValues(5, 0)]
        except IndexError:
            pass
        # Negative indexing
        self.assertEqual(baseValS, [v for v in myFs.genChScValues(-5, 0)])
        self.assertEqual([b+1 for b in baseValS], [v for v in myFs.genChScValues(-4, 0)])
        self.assertEqual([b+2 for b in baseValS], [v for v in myFs.genChScValues(-3, 0)])
        self.assertEqual([b+3 for b in baseValS], [v for v in myFs.genChScValues(-2, 0)])
        self.assertEqual([b+4 for b in baseValS], [v for v in myFs.genChScValues(-1, 0)])

    def test_01(self):
        """TestFrameSetgenChScValues.test_01(): 8 frames of 5 channels, using genChScValues(), -ve indexes."""
        numCh = 5
        numFr = 8
        myFile = self._createFileDFSROnly(numCh, 1, 1)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        v = 0.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray()
            for ch in range(numCh):
                fBy.extend(RepCode.writeBytes68(v))
                v += 1.0
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=numCh-1)
        # Negative indexing
        baseValS = [float(x) for x in range(0, 40, 5)]
        self.assertEqual(baseValS, [v for v in myFs.genChScValues(-5, 0)])
        self.assertEqual([b+1 for b in baseValS], [v for v in myFs.genChScValues(-4, 0)])
        self.assertEqual([b+2 for b in baseValS], [v for v in myFs.genChScValues(-3, 0)])
        self.assertEqual([b+3 for b in baseValS], [v for v in myFs.genChScValues(-2, 0)])
        self.assertEqual([b+4 for b in baseValS], [v for v in myFs.genChScValues(-1, 0)])

    def test_02(self):
        """TestFrameSetgenChScValues.test_02(): 8 frames of 5 channels, using genChScValues(), indexes out of range."""
        numCh = 5
        numFr = 8
        myFile = self._createFileDFSROnly(numCh, 1, 1)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        v = 0.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray()
            for ch in range(numCh):
                fBy.extend(RepCode.writeBytes68(v))
                v += 1.0
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=numCh-1)
        # Indexing out of range
        try:
            [v for v in myFs.genChScValues(0, 1)]
            self.fail('IndexError not raised')
        except IndexError:
            pass
        try:
            [v for v in myFs.genChScValues(5, 0)]
            self.fail('IndexError not raised')
        except IndexError:
            pass
        try:
            [v for v in myFs.genChScValues(-6, 0)]
            self.fail('IndexError not raised')
        except IndexError:
            pass

    def test_03(self):
        """TestFrameSetgenChScValues.test_03(): 1 frame of DEPT + Dipmeter 243, using using genChScValues()."""
        myB = (
            bytes([64, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        # Sensor 0
        myB += (
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            b"RHDT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(90) + b'000' + bytes([1,])+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 1
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        dep = 1000.0
        v = 0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            for b in range(90):
                fBy.extend(RepCode.writeBytes66(v % 256))
                v += 1
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= 0.5
        baseValS = [float(x) for x in range(0, 80, 5)]
        #print()
        #print([v for v in myFs.genChScValues(0, 0)])
        self.assertEqual([1000.0], [v for v in myFs.genChScValues(0, 0)])
        self.assertEqual([b+0 for b in baseValS], [v for v in myFs.genChScValues(1, 0)])
        self.assertEqual([b+1 for b in baseValS], [v for v in myFs.genChScValues(1, 1)])
        self.assertEqual([b+2 for b in baseValS], [v for v in myFs.genChScValues(1, 2)])
        self.assertEqual([b+3 for b in baseValS], [v for v in myFs.genChScValues(1, 3)])
        self.assertEqual([b+4 for b in baseValS], [v for v in myFs.genChScValues(1, 4)])
        self.assertEqual([80.0], [v for v in myFs.genChScValues(1, 5)])
        self.assertEqual([81.0], [v for v in myFs.genChScValues(1, 6)])
        self.assertEqual([82.0], [v for v in myFs.genChScValues(1, 7)])
        self.assertEqual([83.0], [v for v in myFs.genChScValues(1, 8)])
        self.assertEqual([84.0], [v for v in myFs.genChScValues(1, 9)])
        self.assertEqual([85.0], [v for v in myFs.genChScValues(1, 10)])
        self.assertEqual([86.0], [v for v in myFs.genChScValues(1, 11)])
        self.assertEqual([87.0], [v for v in myFs.genChScValues(1, 12)])
        self.assertEqual([88.0], [v for v in myFs.genChScValues(1, 13)])
        self.assertEqual([89.0], [v for v in myFs.genChScValues(1, 14)])

    def test_04(self):
        """TestFrameSetgenChScValues.test_04(): 256 frames of DEPT + Dipmeter 243, using genChScValues()."""
        myB = (
            bytes([64, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        # Sensor 0
        myB += (
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            b"RHDT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(90) + b'000' + bytes([1,])+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 256
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        dep = 1000.0
        v = 0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            for b in range(90):
                fBy.extend(RepCode.writeBytes66(v % 256))
                v += 1
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= 0.5
        #print()
        #print([v for v in myFs.genChScValues(1, 0)])
        #self.assertEqual([1000.0], [v for v in myFs.genChScValues(0, 0)])

    def test_05(self):
        """TestFrameSetgenChScValues.test_05(): indirect DEPT, 4 frames of Dipmeter 243, using genChScValues()."""
        xAxisRc = 73
        myB = (
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 8, Frame spacing
            + bytes([8, 1, 66, 60])
            # EB 9, Frame spacing units
            + bytes([9, 4, 65])+b'.1IN'
            # EB 13, recording mode 1
            + bytes([13, 1, 66, 1])
            # EB 14, X axis units
            + bytes([14, 4, 65])+b'.1IN'
            # EB 15, indirect Rep Code 73
            + bytes([15, 1, 66, xAxisRc])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
        )
        # Sensor 0
        myB += (
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            b"RHDT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(90) + b'000' + bytes([1,])+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 4
        #print()
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        dep = 1000 * 120 # 1000 feet at 0.1 inch
        v = 0
        # Load the first frame set with the indirect depth
        fBy = bytearray(RepCode.writeBytes(dep, xAxisRc))
        for b in range(90):
            fBy.extend(RepCode.writeBytes66(v % 255))
            v += 1
        dep -= 60
        myFs.setFrameBytes(by=fBy, fr=0, chFrom=None, chTo=0)
        # Now load the rest of the FrameSet with only the channel data
        for f in range(1, numFr):
            fBy = bytearray()
            for b in range(90):
                fBy.extend(RepCode.writeBytes66(v % 255))
                v += 1
            # Set frame
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=0)
            # Set indirect depth directly
            myFs.setIndirectX(f, dep)
            dep -= 60
        baseValS = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 90.0, 95.0, 100.0, 105.0, 110.0, 115.0, 120.0, 125.0, 130.0, 135.0, 140.0, 145.0, 150.0, 155.0, 160.0, 165.0, 180.0, 185.0, 190.0, 195.0, 200.0, 205.0, 210.0, 215.0, 220.0, 225.0, 230.0, 235.0, 240.0, 245.0, 250.0, 0.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0]
        baseSlowValS = [80.0, 170.0, 5.0, 95.0]
        #print()
        #print([v for v in myFs.genChScValues(0, 0)])
        #print([v for v in myFs.genChScValues(0, 1)])
        self.assertEqual([b+0 for b in baseValS], [v for v in myFs.genChScValues(0, 0)])
        self.assertEqual([b+1 for b in baseValS], [v for v in myFs.genChScValues(0, 1)])
        self.assertEqual([b+2 for b in baseValS], [v for v in myFs.genChScValues(0, 2)])
        self.assertEqual([b+3 for b in baseValS], [v for v in myFs.genChScValues(0, 3)])
        self.assertEqual([b+4 for b in baseValS], [v for v in myFs.genChScValues(0, 4)])
        self.assertEqual([b+0 for b in baseSlowValS], [v for v in myFs.genChScValues(0, 5)])
        self.assertEqual([b+1 for b in baseSlowValS], [v for v in myFs.genChScValues(0, 6)])
        self.assertEqual([b+2 for b in baseSlowValS], [v for v in myFs.genChScValues(0, 7)])
        self.assertEqual([b+3 for b in baseSlowValS], [v for v in myFs.genChScValues(0, 8)])
        self.assertEqual([b+4 for b in baseSlowValS], [v for v in myFs.genChScValues(0, 9)])
        self.assertEqual([b+5 for b in baseSlowValS], [v for v in myFs.genChScValues(0, 10)])
        self.assertEqual([b+6 for b in baseSlowValS], [v for v in myFs.genChScValues(0, 11)])
        self.assertEqual([b+7 for b in baseSlowValS], [v for v in myFs.genChScValues(0, 12)])
        self.assertEqual([b+8 for b in baseSlowValS], [v for v in myFs.genChScValues(0, 13)])
        self.assertEqual([b+9 for b in baseSlowValS], [v for v in myFs.genChScValues(0, 14)])

class TestFrameSetgenChScPoints_LowLevel(BaseTestClasses.TestBaseLogPass):
    """Test the FrameSet genChScPoints() low level support."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSetgenChScPoints_LowLevel: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSetgenChScPoints_LowLevel.test_00(): 2 frames, direct X, declared frame spacing=0.5 (up), _retFirstXaxisFrameSpacing()."""
        myB = (
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 8, Frame spacing
            + bytes([8, 1, 68])+RepCode.writeBytes68(0.5)
            # EB 9, Frame spacing units
            + bytes([9, 4, 65])+b'FEET'
            # EB 13, recording mode 0 i.e. direct
            + bytes([13, 1, 66, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 1
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b"GR  " + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(4) + b'000' + bytes([1,])+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 2
#        myFile = self._retFileFromBytes(self._retSinglePr(myB))
#        myDfsr = LogiRec.LrDFSRRead(myFile)
#        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        myFs = FrameSet.FrameSet(
                LogiRec.LrDFSRRead(
                    self._retFileFromBytes(self._retSinglePr(myB))
                ),
                slice(numFr)
        )
        dep = 1000.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            fBy.extend(RepCode.writeBytes68(57.0))
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= 0.5
#        print()
#        print(myFs._retFirstXaxisFrameSpacing(1))
        self.assertEqual((1000.0, -0.5), myFs._retFirstXaxisFrameSpacing(1))
        self.assertEqual((1000.5, -0.5), myFs._retFirstXaxisFrameSpacing(2))
        self.assertEqual((1000.5, -0.5), myFs._retFirstXaxisFrameSpacing(4))

    def test_01(self):
        """TestFrameSetgenChScPoints_LowLevel.test_01(): 2 frames, direct X, declared frame spacing=0.5 (down), _retFirstXaxisFrameSpacing()."""
        myB = (
            bytes([64, 0])
            # EB 4, up/down value 0 (down)
            + bytes([4, 1, 66, 0])
            # EB 8, Frame spacing
            + bytes([8, 1, 68])+RepCode.writeBytes68(0.5)
            # EB 9, Frame spacing units
            + bytes([9, 4, 65])+b'FEET'
            # EB 13, recording mode 0 i.e. direct
            + bytes([13, 1, 66, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 1
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b"GR  " + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(4) + b'000' + bytes([1,])+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 2
#        myFile = self._retFileFromBytes(self._retSinglePr(myB))
#        myDfsr = LogiRec.LrDFSRRead(myFile)
#        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        myFs = FrameSet.FrameSet(
                LogiRec.LrDFSRRead(
                    self._retFileFromBytes(self._retSinglePr(myB))
                ),
                slice(numFr)
        )
        dep = 1000.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            fBy.extend(RepCode.writeBytes68(57.0))
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep += 0.5
#        print()
#        print(myFs._retFirstXaxisFrameSpacing(1))
        self.assertEqual((1000.0, 0.5), myFs._retFirstXaxisFrameSpacing(1))
        self.assertEqual((999.5, 0.5), myFs._retFirstXaxisFrameSpacing(2))
        self.assertEqual((999.5, 0.5), myFs._retFirstXaxisFrameSpacing(4))

    def test_02(self):
        """TestFrameSetgenChScPoints_LowLevel.test_02(): 2 frames, direct X, NO declared frame spacing (up), _retFirstXaxisFrameSpacing()."""
        myB = (
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 13, recording mode 0 i.e. direct
            + bytes([13, 1, 66, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 1
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b"GR  " + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(4) + b'000' + bytes([1,])+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 2
#        myFile = self._retFileFromBytes(self._retSinglePr(myB))
#        myDfsr = LogiRec.LrDFSRRead(myFile)
#        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        myFs = FrameSet.FrameSet(
                LogiRec.LrDFSRRead(
                    self._retFileFromBytes(self._retSinglePr(myB))
                ),
                slice(numFr)
        )
        dep = 1000.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            fBy.extend(RepCode.writeBytes68(57.0))
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= 0.5
#        print()
#        print(myFs._retFirstXaxisFrameSpacing(1))
        self.assertEqual((1000.0, -0.5), myFs._retFirstXaxisFrameSpacing(1))
        self.assertEqual((1000.5, -0.5), myFs._retFirstXaxisFrameSpacing(2))
        self.assertEqual((1000.5, -0.5), myFs._retFirstXaxisFrameSpacing(4))

    def test_03(self):
        """TestFrameSetgenChScPoints_LowLevel.test_03(): 1 frame, direct X, NO declared frame spacing (up), _retFirstXaxisFrameSpacing() fails with samples>1."""
        myB = (
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 13, recording mode 0 i.e. direct
            + bytes([13, 1, 66, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 1
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b"GR  " + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(4) + b'000' + bytes([1,])+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 1
#        myFile = self._retFileFromBytes(self._retSinglePr(myB))
#        myDfsr = LogiRec.LrDFSRRead(myFile)
#        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        myFs = FrameSet.FrameSet(
                LogiRec.LrDFSRRead(
                    self._retFileFromBytes(self._retSinglePr(myB))
                ),
                slice(numFr)
        )
        dep = 1000.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            fBy.extend(RepCode.writeBytes68(57.0))
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= 0.5
#        print()
#        print(myFs._retFirstXaxisFrameSpacing(1))
        self.assertEqual((1000.0, 0.0), myFs._retFirstXaxisFrameSpacing(1))
        self.assertRaises(FrameSet.ExceptionFrameSetNULLSpacing, myFs._retFirstXaxisFrameSpacing, 2)
        self.assertRaises(FrameSet.ExceptionFrameSetNULLSpacing, myFs._retFirstXaxisFrameSpacing, 4)

    def test_04(self):
        """TestFrameSetgenChScPoints_LowLevel.test_04(): 1 frames, direct X, declared frame spacing=0.5 (up), _retFirstXaxisFrameSpacing()."""
        myB = (
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 8, Frame spacing, note this is negative as up log
            + bytes([8, 1, 68])+RepCode.writeBytes68(-0.5)
            # EB 9, Frame spacing units
            + bytes([9, 4, 65])+b'FEET'
            # EB 13, recording mode 0 i.e. direct
            + bytes([13, 1, 66, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 1
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b"GR  " + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(4) + b'000' + bytes([1,])+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 1
#        myFile = self._retFileFromBytes(self._retSinglePr(myB))
#        myDfsr = LogiRec.LrDFSRRead(myFile)
#        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        myFs = FrameSet.FrameSet(
                LogiRec.LrDFSRRead(
                    self._retFileFromBytes(self._retSinglePr(myB))
                ),
                slice(numFr)
        )
        dep = 1000.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            fBy.extend(RepCode.writeBytes68(57.0))
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= 0.5
#        print()
#        print(myFs._retFirstXaxisFrameSpacing(1))
        self.assertEqual((1000.0, 0.0), myFs._retFirstXaxisFrameSpacing(1))
        self.assertEqual((1000.5, -0.5), myFs._retFirstXaxisFrameSpacing(2))
        self.assertEqual((1000.5, -0.5), myFs._retFirstXaxisFrameSpacing(4))

    def test_10(self):
        """TestFrameSetgenChScPoints_LowLevel.test_10(): 2 frames, indirect X, declared frame spacing=60 (up), _retFirstXaxisFrameSpacing()."""
        myB = (
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 8, Frame spacing
            + bytes([8, 1, 66, 60])
            # EB 9, Frame spacing units
            + bytes([9, 4, 65])+b'.1IN'
            # EB 13, recording mode 1 i.e. indirect
            + bytes([13, 1, 66, 1])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b"GR  " + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(4) + b'000' + bytes([1,])+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 2
#        myFile = self._retFileFromBytes(self._retSinglePr(myB))
#        myDfsr = LogiRec.LrDFSRRead(myFile)
#        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        myFs = FrameSet.FrameSet(
                LogiRec.LrDFSRRead(
                    self._retFileFromBytes(self._retSinglePr(myB))
                ),
                slice(numFr)
        )
        dep = 1000.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(57.0))
            myFs.setIndirectX(f, dep)
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=0)
            dep -= 60.0
#        print()
#        print(myFs._retFirstXaxisFrameSpacing(1))
        self.assertEqual((1000.0, -60), myFs._retFirstXaxisFrameSpacing(1))
        self.assertEqual((1060.0, -60), myFs._retFirstXaxisFrameSpacing(2))
        self.assertEqual((1060.0, -60), myFs._retFirstXaxisFrameSpacing(4))

    def test_11(self):
        """TestFrameSetgenChScPoints_LowLevel.test_11(): 2 frames, indirect X, declared frame spacing=60 (down), _retFirstXaxisFrameSpacing()."""
        myB = (
            bytes([64, 0])
            # EB 4, up/down value 0 (down)
            + bytes([4, 1, 66, 0])
            # EB 8, Frame spacing
            + bytes([8, 1, 66, 60])
            # EB 9, Frame spacing units
            + bytes([9, 4, 65])+b'.1IN'
            # EB 13, recording mode 1 i.e. indirect
            + bytes([13, 1, 66, 1])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b"GR  " + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(4) + b'000' + bytes([1,])+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 2
#        myFile = self._retFileFromBytes(self._retSinglePr(myB))
#        myDfsr = LogiRec.LrDFSRRead(myFile)
#        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        myFs = FrameSet.FrameSet(
                LogiRec.LrDFSRRead(
                    self._retFileFromBytes(self._retSinglePr(myB))
                ),
                slice(numFr)
        )
        dep = 1000.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(57.0))
            myFs.setIndirectX(f, dep)
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=0)
            dep += 60.0
#        print()
#        print(myFs._retFirstXaxisFrameSpacing(1))
        self.assertEqual((1000.0, 60.0), myFs._retFirstXaxisFrameSpacing(1))
        self.assertEqual((940.0, 60.0), myFs._retFirstXaxisFrameSpacing(2))
        self.assertEqual((940.0, 60.0), myFs._retFirstXaxisFrameSpacing(4))

    def test_20(self):
        """TestFrameSetgenChScPoints_LowLevel.test_20(): 2 frames, indirect X, no declared frame spacing, FrameSet.__init__() fails."""
        myB = (
            bytes([64, 0])
            # EB 4, up/down value 0 (down)
            + bytes([4, 1, 66, 0])
#            # EB 8, Frame spacing
#            + bytes([8, 1, 66, 60])
#            # EB 9, Frame spacing units
#            + bytes([9, 4, 65])+b'.1IN'
            # EB 13, recording mode 1 i.e. indirect
            + bytes([13, 1, 66, 1])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b"GR  " + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(4) + b'000' + bytes([1,])+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 2
#        myFile = self._retFileFromBytes(self._retSinglePr(myB))
#        myDfsr = LogiRec.LrDFSRRead(myFile)
#        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        self.assertRaises(FrameSet.ExceptionFrameSet, FrameSet.FrameSet,
                LogiRec.LrDFSRRead(
                    self._retFileFromBytes(self._retSinglePr(myB))
                ),
                slice(numFr)
        )

    def test_40(self):
        """TestFrameSetgenChScPoints_LowLevel.test_40(): 1 frame of DEPT + Dipmeter 243, _retFirstXaxisFrameSpacing()."""
        myB = (
            bytes([64, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        # Sensor 0
        myB += (
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            b"RHDT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(90) + b'000' + bytes([1,])+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 1
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        dep = 1000.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            fBy.extend(list(range(5))*16+list(range(5,15,1)))
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= 0.5
#        print()
#        print(myFs._retFirstXaxisFrameSpacing(1))
        self.assertEqual((1000.0, 0.0), myFs._retFirstXaxisFrameSpacing(1))
        self.assertRaises(FrameSet.ExceptionFrameSetNULLSpacing, myFs._retFirstXaxisFrameSpacing, 2)


class TestFrameSetgenChScPoints(BaseTestClasses.TestBaseLogPass):
    """Test the FrameSet genChScPoints() low level support."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSetgenChScPoints: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSetgenChScPoints.test_00(): 8 frames of 5 channels, using genChScPoints(), +ve indexes."""
        numCh = 5
        numFr = 8
        myFile = self._createFileDFSROnly(numCh, 1, 1)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        v = 0.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray()
            for ch in range(numCh):
                fBy.extend(RepCode.writeBytes68(v))
                v += 1.0
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=numCh-1)
        actValS = [v for v in myFs.genChScPoints(0, 0)]
        #print()
        #print(actValS)
        baseValS = [(float(x), float(x)) for x in range(0, 40, 5)]
        self.assertEqual(baseValS, [v for v in myFs.genChScPoints(0, 0)])
        self.assertEqual([(d, v+1) for d,v in baseValS], [v for v in myFs.genChScPoints(1, 0)])
        self.assertEqual([(d, v+2) for d,v in baseValS], [v for v in myFs.genChScPoints(2, 0)])
        self.assertEqual([(d, v+3) for d,v in baseValS], [v for v in myFs.genChScPoints(3, 0)])
        self.assertEqual([(d, v+4) for d,v in baseValS], [v for v in myFs.genChScPoints(4, 0)])
        # Indexing out of range
        try:
            [v for v in myFs.genChScPoints(0, 1)]
        except IndexError:
            pass
        try:
            [v for v in myFs.genChScPoints(5, 0)]
        except IndexError:
            pass
        # Negative indexing
        self.assertEqual(baseValS, [v for v in myFs.genChScPoints(-5, 0)])
        self.assertEqual([(d, v+1) for d,v in baseValS], [v for v in myFs.genChScPoints(-4, 0)])
        self.assertEqual([(d, v+2) for d,v in baseValS], [v for v in myFs.genChScPoints(-3, 0)])
        self.assertEqual([(d, v+3) for d,v in baseValS], [v for v in myFs.genChScPoints(-2, 0)])
        self.assertEqual([(d, v+4) for d,v in baseValS], [v for v in myFs.genChScPoints(-1, 0)])

    def test_01(self):
        """TestFrameSetgenChScPoints.test_01(): 8 frames of 5 channels, using genChScPoints(), -ve indexes."""
        numCh = 5
        numFr = 8
        myFile = self._createFileDFSROnly(numCh, 1, 1)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        v = 0.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray()
            for ch in range(numCh):
                fBy.extend(RepCode.writeBytes68(v))
                v += 1.0
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=numCh-1)
        # Negative indexing
        baseValS = [(float(x), float(x)) for x in range(0, 40, 5)]
        self.assertEqual(baseValS, [v for v in myFs.genChScPoints(-5, 0)])
        self.assertEqual([(d, v+1) for d,v in baseValS], [v for v in myFs.genChScPoints(-4, 0)])
        self.assertEqual([(d, v+2) for d,v in baseValS], [v for v in myFs.genChScPoints(-3, 0)])
        self.assertEqual([(d, v+3) for d,v in baseValS], [v for v in myFs.genChScPoints(-2, 0)])
        self.assertEqual([(d, v+4) for d,v in baseValS], [v for v in myFs.genChScPoints(-1, 0)])

    def test_02(self):
        """TestFrameSetgenChScPoints.test_02(): 8 frames of 5 channels, using genChScPoints(), indexes out of range."""
        numCh = 5
        numFr = 8
        myFile = self._createFileDFSROnly(numCh, 1, 1)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        v = 0.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray()
            for ch in range(numCh):
                fBy.extend(RepCode.writeBytes68(v))
                v += 1.0
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=numCh-1)
        # Indexing out of range
        try:
            [v for v in myFs.genChScPoints(0, 1)]
            self.fail('IndexError not raised')
        except IndexError:
            pass
        try:
            [v for v in myFs.genChScPoints(5, 0)]
            self.fail('IndexError not raised')
        except IndexError:
            pass
        try:
            [v for v in myFs.genChScPoints(-6, 0)]
            self.fail('IndexError not raised')
        except IndexError:
            pass

    def test_03(self):
        """TestFrameSetgenChScPoints.test_03(): 1 frame of DEPT + Dipmeter 243, using using genChScPoints()."""
        myB = (
            bytes([64, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        # Sensor 0
        myB += (
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            b"RHDT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(90) + b'000' + bytes([1,])+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 1
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        dep = 1000.0
        v = 0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            fBy.extend(list(range(5))*16+list(range(5,15,1)))
#            for b in range(90):
#                fBy.extend(RepCode.writeBytes66(v % 256))
#                v += 1
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= 0.5
        #baseValS = [(float(x), float(x)) for x in range(0, 80, 5)]
        #print()
        #print('(0,0)', [v for v in myFs.genChScPoints(0, 0)])
        try:
            [v for v in myFs.genChScPoints(1, 0)]
            self.fail('FrameSet.ExceptionFrameSetNULLSpacing not raised.')
        except FrameSet.ExceptionFrameSetNULLSpacing:
            pass

    def test_04(self):
        """TestFrameSetgenChScPoints.test_04(): 4 frames of DEPT + Dipmeter 243, using genChScPoints()."""
        myB = (
            bytes([64, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        # Sensor 0
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
        myB += (
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            b"RHDT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(90) + b'000' + bytes([1,])+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 4
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        depStart = 2000.0
        depInterval = 4.0
        dep = depStart
#        v = 0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            fBy.extend(list(range(5))*16+list(range(5,15,1)))
#            for b in range(90):
#                fBy.extend(RepCode.writeBytes66(v % 256))
#                v += 1
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= depInterval
        #baseValS = [(float(x), float(x)) for x in range(0, 80, 5)]
        #print()
        #print('(0,0)', [v for v in myFs.genChScPoints(0, 0)])

        #print()
        #print([v for v in myFs.genChScPoints(1, 0)])
        #self.assertEqual([1000.0], [v for v in myFs.genChScPoints(0, 0)])
#        print('(0,0)', [v for v in myFs.genChScPoints(0, 0)])
        # Ch/Sc 0/0 - depth
        expResult = [         
            (2000.0, 2000.0),
            (1996.0, 1996.0),
            (1992.0, 1992.0),
            (1988.0, 1988.0)
        ]
        self.assertEqual(
            expResult,
            [v for v in myFs.genChScPoints(0, 0)],
        )
#        print('(1,0)', [v for v in myFs.genChScPoints(1, 0)])
#        print('(1,1)', [v for v in myFs.genChScPoints(1, 1)])
#        print('(1,2)', [v for v in myFs.genChScPoints(1, 2)])
#        print('(1,3)', [v for v in myFs.genChScPoints(1, 3)])
#        print('(1,4)', [v for v in myFs.genChScPoints(1, 4)])
        # Ch/Sc 1/0 - FC0
        expResult = [(depStart+depInterval-x/numFr,0.0) for x in range(1,1+4*16)]
        self.assertEqual(
            expResult,
            [v for v in myFs.genChScPoints(1, 0)],
        )
        # Ch/Sc 1/1 - FC1
        expResult = [(depStart+depInterval-x/numFr,1.0) for x in range(1,1+4*16)]
        self.assertEqual(
            expResult,
            [v for v in myFs.genChScPoints(1, 1)],
        )
        # Ch/Sc 1/2 - FC2
        expResult = [(depStart+depInterval-x/numFr,2.0) for x in range(1,1+4*16)]
        self.assertEqual(
            expResult,
            [v for v in myFs.genChScPoints(1, 2)],
        )
        # Ch/Sc 1/3 - FC3
        expResult = [(depStart+depInterval-x/numFr,3.0) for x in range(1,1+4*16)]
        self.assertEqual(
            expResult,
            [v for v in myFs.genChScPoints(1, 3)],
        )
        # Ch/Sc 1/4 - FC4
        expResult = [(depStart+depInterval-x/numFr,4.0) for x in range(1,1+4*16)]
        self.assertEqual(
            expResult,
            [v for v in myFs.genChScPoints(1, 4)],
        )
        # Slow channels
        #print('(1,5)', [v for v in myFs.genChScPoints(1, 5)])
        # Ch/Sc 1/5 - SC0
        expResult = [(2000.0, 5.0), (1996.0, 5.0), (1992.0, 5.0), (1988.0, 5.0)]
        self.assertEqual(expResult, [v for v in myFs.genChScPoints(1, 5)])
        for sc in range(5, 15, 1):
            expResult = [(2000.0, sc), (1996.0, sc), (1992.0, sc), (1988.0, sc)]
            self.assertEqual(expResult, [v for v in myFs.genChScPoints(1, sc)])

    def test_05(self):
        """TestFrameSetgenChScPoints.test_05(): indirect DEPT, 4 frames of Dipmeter 243, using genChScPoints()."""
        xAxisRc = 73
        myB = (
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 8, Frame spacing
            + bytes([8, 1, 73])+RepCode.writeBytes(480, 73)
            # EB 9, Frame spacing units
            + bytes([9, 4, 65])+b'.1IN'
            # EB 13, recording mode 1
            + bytes([13, 1, 66, 1])
            # EB 14, X axis units
            + bytes([14, 4, 65])+b'.1IN'
            # EB 15, indirect Rep Code 73
            + bytes([15, 1, 66, xAxisRc])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
        )
        # Sensor 0
        myB += (
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            b"RHDT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(90) + b'000' + bytes([1,])+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 4
        #print()
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        dep = 1000 * 120 # 1000 feet at 0.1 inch
        # Load the first frame set with the indirect depth
        fBy = bytearray(RepCode.writeBytes(dep, xAxisRc))
        fBy.extend(list(range(5))*16+list(range(5,15,1)))
        dep -= 480
        myFs.setFrameBytes(by=fBy, fr=0, chFrom=None, chTo=0)
        # Now load the rest of the FrameSet with only the channel data
        for f in range(1, numFr):
            fBy = bytearray()
            fBy.extend(list(range(5))*16+list(range(5,15,1)))
            # Set frame
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=0)
            # Set indirect depth directly
            myFs.setIndirectX(f, dep)
            dep -= 480
#        print()
#        print(' (0, 0) '.center(75, '='))
#        print([v for v in myFs.genChScPoints(0, 0)])
#        print(' END '.center(75, '='))
#        print(' (0, 1) '.center(75, '='))
#        print([v for v in myFs.genChScPoints(0, 1)])
#        print(' END '.center(75, '='))
        self.assertEqual(
            [(120*1000+450-30*s,0) for s in range(numFr*16)],
            [v for v in myFs.genChScPoints(0, 0)],
        )
        self.assertEqual(
            [(120*1000+450-30*s,1) for s in range(numFr*16)],
            [v for v in myFs.genChScPoints(0, 1)],
        )
        self.assertEqual(
            [(120*1000+450-30*s,2) for s in range(numFr*16)],
            [v for v in myFs.genChScPoints(0, 2)],
        )
        self.assertEqual(
            [(120*1000+450-30*s,3) for s in range(numFr*16)],
            [v for v in myFs.genChScPoints(0, 3)],
        )
        self.assertEqual(
            [(120*1000+450-30*s,4) for s in range(numFr*16)],
            [v for v in myFs.genChScPoints(0, 4)],
        )
#        print()
#        print(' (0, 5) '.center(75, '='))
#        print([v for v in myFs.genChScPoints(0, 5)])
#        print(' END '.center(75, '='))
        self.assertEqual(
            [(120*1000-480*s,5) for s in range(numFr)],
            [v for v in myFs.genChScPoints(0, 5)],
        )
        self.assertEqual(
            [(120*1000-480*s,6) for s in range(numFr)],
            [v for v in myFs.genChScPoints(0, 6)],
        )
        self.assertEqual(
            [(120*1000-480*s,7) for s in range(numFr)],
            [v for v in myFs.genChScPoints(0, 7)],
        )
        self.assertEqual(
            [(120*1000-480*s,8) for s in range(numFr)],
            [v for v in myFs.genChScPoints(0, 8)],
        )
        self.assertEqual(
            [(120*1000-480*s,9) for s in range(numFr)],
            [v for v in myFs.genChScPoints(0, 9)],
        )
        self.assertEqual(
            [(120*1000-480*s,10) for s in range(numFr)],
            [v for v in myFs.genChScPoints(0, 10)],
        )
        self.assertEqual(
            [(120*1000-480*s,11) for s in range(numFr)],
            [v for v in myFs.genChScPoints(0, 11)],
        )
        self.assertEqual(
            [(120*1000-480*s,12) for s in range(numFr)],
            [v for v in myFs.genChScPoints(0, 12)],
        )
        self.assertEqual(
            [(120*1000-480*s,13) for s in range(numFr)],
            [v for v in myFs.genChScPoints(0, 13)],
        )
        self.assertEqual(
            [(120*1000-480*s,14) for s in range(numFr)],
            [v for v in myFs.genChScPoints(0, 14)],
        )

    def test_10(self):
        """TestFrameSetgenChScPoints.test_10(): 8 frames of DEPT+1 channel with 4 samples, 1 burst, no declared spacing, using genChScPoints()."""
        numCh = 2
        numSa = 4
        numBu = 1
        numFr = 8
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        v = 0.0
        dep = 1000.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray()
            for ch in range(numCh):
                if ch == 1:
                    for s in range(numSa):
                        fBy.extend(RepCode.writeBytes68(v))
                        v += 1.0
                else:
                    fBy.extend(RepCode.writeBytes68(dep))
                    dep -= 0.5
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=numCh-1)
#        print()
#        print('Ch 0:', [v for v in myFs.genChScPoints(0, 0)])
#        print('Ch 1:', [v for v in myFs.genChScPoints(1, 0)])
        expChValS = [
                        [
                (1000.0, 1000.0),
                (999.5, 999.5),
                (999.0, 999.0),
                (998.5, 998.5),
                (998.0, 998.0),
                (997.5, 997.5),
                (997.0, 997.0),
                (996.5, 996.5),
             ],
            [
                (1000.375, 0.0), (1000.25, 1.0), (1000.125, 2.0), (1000.0, 3.0),
                (999.875, 4.0), (999.75, 5.0), (999.625, 6.0), (999.5, 7.0),
                (999.375, 8.0), (999.25, 9.0), (999.125, 10.0), (999.0, 11.0),
                (998.875, 12.0), (998.75, 13.0), (998.625, 14.0), (998.5, 15.0),
                (998.375, 16.0), (998.25, 17.0), (998.125, 18.0), (998.0, 19.0),
                (997.875, 20.0), (997.75, 21.0), (997.625, 22.0), (997.5, 23.0),
                (997.375, 24.0), (997.25, 25.0), (997.125, 26.0), (997.0, 27.0),
                (996.875, 28.0), (996.75, 29.0), (996.625, 30.0), (996.5, 31.0),
            ],
        ]
        self.assertEqual(expChValS[0], [v for v in myFs.genChScPoints(0, 0)])
        self.assertEqual(expChValS[1], [v for v in myFs.genChScPoints(1, 0)])
        # Indexing out of range
        try:
            [v for v in myFs.genChScPoints(0, 1)]
        except IndexError:
            pass
        try:
            [v for v in myFs.genChScPoints(2, 0)]
        except IndexError:
            pass
        # Negative indexing
        self.assertEqual(expChValS[0], [v for v in myFs.genChScPoints(-2, 0)])
        self.assertEqual(expChValS[1], [v for v in myFs.genChScPoints(-1, 0)])

    def test_11(self):
        """TestFrameSetgenChScPoints.test_11(): 3 frames of DEPT+1 channel with 4 samples, 6 bursts, no declared spacing, using genChScPoints()."""
        numCh = 2
        numSa = 4
        numBu = 6
        numFr = 3
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        v = 0.0
        dep = 1000.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray()
            for ch in range(numCh):
                if ch != 0:
                    for sb in range(numSa*numBu):
                        fBy.extend(RepCode.writeBytes68(v))
                        v += 1.0
                else:
                    fBy.extend(RepCode.writeBytes68(dep))
                    dep -= 0.5
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=numCh-1)
#        print()
#        print('Ch 0:', [v for v in myFs.genChScPoints(0, 0)])
#        print('Ch 1:', [v for v in myFs.genChScPoints(1, 0)])
        expChValS = [
                        [
                (1000.0, 1000.0),
                (999.5, 999.5),
                (999.0, 999.0),
             ],
            [
                (1000.375, 0.0), (1000.375, 1.0), (1000.375, 2.0), (1000.375, 3.0), (1000.375, 4.0), (1000.375, 5.0),
                (1000.25, 6.0), (1000.25, 7.0), (1000.25, 8.0), (1000.25, 9.0), (1000.25, 10.0), (1000.25, 11.0),
                (1000.125, 12.0), (1000.125, 13.0), (1000.125, 14.0), (1000.125, 15.0), (1000.125, 16.0), (1000.125, 17.0),
                (1000.0, 18.0), (1000.0, 19.0), (1000.0, 20.0), (1000.0, 21.0), (1000.0, 22.0), (1000.0, 23.0),
                (999.875, 24.0), (999.875, 25.0), (999.875, 26.0), (999.875, 27.0), (999.875, 28.0), (999.875, 29.0),
                (999.75, 30.0), (999.75, 31.0), (999.75, 32.0), (999.75, 33.0), (999.75, 34.0), (999.75, 35.0),
                (999.625, 36.0), (999.625, 37.0), (999.625, 38.0), (999.625, 39.0), (999.625, 40.0), (999.625, 41.0),
                (999.5, 42.0), (999.5, 43.0), (999.5, 44.0), (999.5, 45.0), (999.5, 46.0), (999.5, 47.0),
                (999.375, 48.0), (999.375, 49.0), (999.375, 50.0), (999.375, 51.0), (999.375, 52.0), (999.375, 53.0),
                (999.25, 54.0), (999.25, 55.0), (999.25, 56.0), (999.25, 57.0), (999.25, 58.0), (999.25, 59.0),
                (999.125, 60.0), (999.125, 61.0), (999.125, 62.0), (999.125, 63.0), (999.125, 64.0), (999.125, 65.0),
                (999.0, 66.0), (999.0, 67.0), (999.0, 68.0), (999.0, 69.0), (999.0, 70.0), (999.0, 71.0),
            ],
        ]
        self.assertEqual(expChValS[0], [v for v in myFs.genChScPoints(0, 0)])
        self.assertEqual(expChValS[1], [v for v in myFs.genChScPoints(1, 0)])
        # Indexing out of range
        try:
            [v for v in myFs.genChScPoints(0, 1)]
        except IndexError:
            pass
        try:
            [v for v in myFs.genChScPoints(2, 0)]
        except IndexError:
            pass
        # Negative indexing
        self.assertEqual(expChValS[0], [v for v in myFs.genChScPoints(-2, 0)])
        self.assertEqual(expChValS[1], [v for v in myFs.genChScPoints(-1, 0)])

    def test_12(self):
        """TestFrameSetgenChScPoints.test_12(): 8 frames of DEPT+1 channel with 1 sample, 1 burst, no declared spacing, frame step=16 using genChScPoints()."""
        numCh = 2
        numSa = 1
        numBu = 1
        numFr = 8
        numFrStep = 16
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(0, numFr*4, 4))
        v = 0.0
        dep = 1000.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray()
            for ch in range(numCh):
                if ch == 1:
                    for s in range(numSa):
                        fBy.extend(RepCode.writeBytes68(v))
                        v += 1.0
                else:
                    fBy.extend(RepCode.writeBytes68(dep))
                    dep -= numFrStep * 0.5
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=numCh-1)
#        print()
#        print('Ch 0:', [v for v in myFs.genChScPoints(0, 0)])
#        print('Ch 1:', [v for v in myFs.genChScPoints(1, 0)])
        expChValS = [
            [
                (1000.0, 1000.0),
                (992.0, 992.0),
                (984.0, 984.0),
                (976.0, 976.0),
                (968.0, 968.0),
                (960.0, 960.0),
                (952.0, 952.0),
                (944.0, 944.0),
            ],
            [
                (1000.0, 0.0),
                (992.0, 1.0),
                (984.0, 2.0),
                (976.0, 3.0),
                (968.0, 4.0),
                (960.0, 5.0),
                (952.0, 6.0),
                (944.0, 7.0),
            ],
        ]
        self.assertEqual(expChValS[0], [v for v in myFs.genChScPoints(0, 0)])
        self.assertEqual(expChValS[1], [v for v in myFs.genChScPoints(1, 0)])
        # Indexing out of range
        try:
            [v for v in myFs.genChScPoints(0, 1)]
        except IndexError:
            pass
        try:
            [v for v in myFs.genChScPoints(2, 0)]
        except IndexError:
            pass
        # Negative indexing
        self.assertEqual(expChValS[0], [v for v in myFs.genChScPoints(-2, 0)])
        self.assertEqual(expChValS[1], [v for v in myFs.genChScPoints(-1, 0)])

    def test_13(self):
        """TestFrameSetgenChScPoints.test_13(): 8 frames of DEPT+1 channel with 4 samples, 1 burst, no declared spacing, frame step=16 using genChScPoints()."""
        numCh = 2
        numSa = 4
        numBu = 1
        numFr = 8
        numFrStep = 16
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(0, numFr*4, 4))
        v = 0.0
        dep = 1000.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray()
            for ch in range(numCh):
                if ch == 1:
                    for s in range(numSa):
                        fBy.extend(RepCode.writeBytes68(v))
                        v += 1.0
                else:
                    fBy.extend(RepCode.writeBytes68(dep))
                    dep -= numFrStep * 0.5
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=numCh-1)
#        print()
#        print('Ch 0:', [v for v in myFs.genChScPoints(0, 0)])
#        print('Ch 1:', [v for v in myFs.genChScPoints(1, 0)])
        expChValS = [
            [
                (1000.0, 1000.0),
                (992.0, 992.0),
                (984.0, 984.0),
                (976.0, 976.0),
                (968.0, 968.0),
                (960.0, 960.0),
                (952.0, 952.0),
                (944.0, 944.0),
            ],
            [
                (1001.5, 0.0), (1001.0, 1.0), (1000.5, 2.0), (1000.0, 3.0),
                (993.5, 4.0), (993.0, 5.0), (992.5, 6.0), (992.0, 7.0),
                (985.5, 8.0), (985.0, 9.0), (984.5, 10.0), (984.0, 11.0),
                (977.5, 12.0), (977.0, 13.0), (976.5, 14.0), (976.0, 15.0),
                (969.5, 16.0), (969.0, 17.0), (968.5, 18.0), (968.0, 19.0),
                (961.5, 20.0), (961.0, 21.0), (960.5, 22.0), (960.0, 23.0),
                (953.5, 24.0), (953.0, 25.0), (952.5, 26.0), (952.0, 27.0),
                (945.5, 28.0), (945.0, 29.0), (944.5, 30.0), (944.0, 31.0),
            ],
        ]
        self.assertEqual(expChValS[0], [v for v in myFs.genChScPoints(0, 0)])
        self.assertEqual(expChValS[1], [v for v in myFs.genChScPoints(1, 0)])
        # Indexing out of range
        try:
            [v for v in myFs.genChScPoints(0, 1)]
        except IndexError:
            pass
        try:
            [v for v in myFs.genChScPoints(2, 0)]
        except IndexError:
            pass
        # Negative indexing
        self.assertEqual(expChValS[0], [v for v in myFs.genChScPoints(-2, 0)])
        self.assertEqual(expChValS[1], [v for v in myFs.genChScPoints(-1, 0)])

    def test_14(self):
        """TestFrameSetgenChScPoints.test_14(): 8 frames of DEPT+1 channel with 1 sample, 4 bursts, no declared spacing, using genChScPoints()."""
        numCh = 2
        numSa = 1
        numBu = 4
        numFr = 8
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        v = 0.0
        dep = 1000.0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray()
            for ch in range(numCh):
                if ch == 1:
                    for s in range(numSa*numBu):
                        fBy.extend(RepCode.writeBytes68(v))
                        v += 1.0
                else:
                    fBy.extend(RepCode.writeBytes68(dep))
                    dep -= 0.5
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=numCh-1)
#        print()
#        print('Ch 0:', [v for v in myFs.genChScPoints(0, 0)])
#        print('Ch 1:', [v for v in myFs.genChScPoints(1, 0)])
        expChValS = [
                        [
                (1000.0, 1000.0),
                (999.5, 999.5),
                (999.0, 999.0),
                (998.5, 998.5),
                (998.0, 998.0),
                (997.5, 997.5),
                (997.0, 997.0),
                (996.5, 996.5),
             ],
            [
                (1000.0, 0.0),  (1000.0, 1.0),  (1000.0, 2.0),  (1000.0, 3.0),
                (999.5, 4.0),   (999.5, 5.0),   (999.5, 6.0),   (999.5, 7.0),
                (999.0, 8.0),   (999.0, 9.0),   (999.0, 10.0),  (999.0, 11.0),
                (998.5, 12.0),  (998.5, 13.0),  (998.5, 14.0),  (998.5, 15.0),
                (998.0, 16.0),  (998.0, 17.0),  (998.0, 18.0),  (998.0, 19.0),
                (997.5, 20.0),  (997.5, 21.0),  (997.5, 22.0),  (997.5, 23.0),
                (997.0, 24.0),  (997.0, 25.0),  (997.0, 26.0),  (997.0, 27.0),
                (996.5, 28.0),  (996.5, 29.0),  (996.5, 30.0),  (996.5, 31.0),
            ],             
        ]
        self.assertEqual(expChValS[0], [v for v in myFs.genChScPoints(0, 0)])
        self.assertEqual(expChValS[1], [v for v in myFs.genChScPoints(1, 0)])
        # Indexing out of range
        try:
            [v for v in myFs.genChScPoints(0, 1)]
        except IndexError:
            pass
        try:
            [v for v in myFs.genChScPoints(2, 0)]
        except IndexError:
            pass
        # Negative indexing
        self.assertEqual(expChValS[0], [v for v in myFs.genChScPoints(-2, 0)])
        self.assertEqual(expChValS[1], [v for v in myFs.genChScPoints(-1, 0)])

    def test_15(self):
        """TestFrameSetgenChScPoints.test_15(): 4 frames of Dipmeter 243 + DEPT at ch=1, using genChScPoints()."""
        myB = (
            bytes([64, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b"RHDT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(90) + b'000' + bytes([1,])+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 1
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 4
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr), xAxisIndex=1)
        depStart = 2000.0
        depInterval = 4.0
        dep = depStart
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(list(range(5))*16+list(range(5,15,1)))
            fBy.extend(RepCode.writeBytes68(dep))
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= depInterval
        #print()
        #print([v for v in myFs.genChScPoints(1, 0)])
        #self.assertEqual([1000.0], [v for v in myFs.genChScPoints(0, 0)])
#        print('(0,0)', [v for v in myFs.genChScPoints(0, 0)])
        # Ch/Sc 0/0 - FC0
        expResult = [(depStart+depInterval-x/numFr,0.0) for x in range(1,1+4*16)]
        self.assertEqual(
            expResult,
            [v for v in myFs.genChScPoints(0, 0)],
        )
        # Ch/Sc 0/1 - FC1
        expResult = [(depStart+depInterval-x/numFr,1.0) for x in range(1,1+4*16)]
        self.assertEqual(
            expResult,
            [v for v in myFs.genChScPoints(0, 1)],
        )
        # Ch/Sc 0/2 - FC2
        expResult = [(depStart+depInterval-x/numFr,2.0) for x in range(1,1+4*16)]
        self.assertEqual(
            expResult,
            [v for v in myFs.genChScPoints(0, 2)],
        )
        # Ch/Sc 0/3 - FC3
        expResult = [(depStart+depInterval-x/numFr,3.0) for x in range(1,1+4*16)]
        self.assertEqual(
            expResult,
            [v for v in myFs.genChScPoints(0, 3)],
        )
        # Ch/Sc 0/4 - FC4
        expResult = [(depStart+depInterval-x/numFr,4.0) for x in range(1,1+4*16)]
        self.assertEqual(
            expResult,
            [v for v in myFs.genChScPoints(0, 4)],
        )
        # Slow channels
        for sc in range(5, 15, 1):
            expResult = [(2000.0, sc), (1996.0, sc), (1992.0, sc), (1988.0, sc)]
            self.assertEqual(expResult, [v for v in myFs.genChScPoints(0, sc)])
        # Ch/Sc 1/0 - depth
        expResult = [         
            (2000.0, 2000.0),
            (1996.0, 1996.0),
            (1992.0, 1992.0),
            (1988.0, 1988.0)
        ]
        self.assertEqual(
            expResult,
            [v for v in myFs.genChScPoints(1, 0)],
        )

    def test_16(self):
        """TestFrameSetgenChScPoints.test_16(): indirect DEPT, 3 frames of channel with 1 sample, 4 bursts, using genChScPoints()."""
        xAxisRc = 73
        numFr = 3
        numBu = 4
        myB = (
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 8, Frame spacing
            + bytes([8, 1, 73])+RepCode.writeBytes(480, 73)
            # EB 9, Frame spacing units
            + bytes([9, 4, 65])+b'.1IN'
            # EB 13, recording mode 1
            + bytes([13, 1, 66, 1])
            # EB 14, X axis units
            + bytes([14, 4, 65])+b'.1IN'
            # EB 15, indirect Rep Code 73
            + bytes([15, 1, 66, xAxisRc])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
        )
        # Sensor 0
        myB += (
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            b"BRST" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(4*numBu) + b'000' + bytes([1,])+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        #print()
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        dep = 1000 * 120 # 1000 feet at 0.1 inch
        v = 0.0
        # Load the first frame set with the indirect depth
        fBy = bytearray(RepCode.writeBytes(dep, xAxisRc))
        for b in range(numBu):
#            print('v',v,RepCode.writeBytes(v, 68))
            fBy.extend(RepCode.writeBytes(v, 68))
            v += 0.25
        dep -= 480
#        print('fBy', len(fBy), fBy, list(fBy))
        myFs.setFrameBytes(by=fBy, fr=0, chFrom=None, chTo=0)
        # Now load the rest of the FrameSet with only the channel data
        for f in range(1, numFr):
            fBy = bytearray()
            for b in range(numBu):
                fBy.extend(RepCode.writeBytes(v, 68))
                v += 0.25
            # Set frame
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=0)
            # Set indirect depth directly
            myFs.setIndirectX(f, dep)
            dep -= 480
#        print()
#        print(' Frames '.center(75, '='))
#        pprint.pprint(myFs.frames)
#        print(' END '.center(75, '='))
#        print(' Indirect X '.center(75, '='))
#        pprint.pprint(myFs._indrXVector)
#        print(' END '.center(75, '='))
#        print(' (0, 0) '.center(75, '='))
#        print([v for v in myFs.genChScPoints(0, 0)])
#        print(' END '.center(75, '='))
        self.assertEqual(
            [
             (120000.0, 0.0), (120000.0, 0.25), (120000.0, 0.5), (120000.0, 0.75),
             (119520.0, 1.0), (119520.0, 1.25), (119520.0, 1.5), (119520.0, 1.75),
             (119040.0, 2.0), (119040.0, 2.25), (119040.0, 2.5), (119040.0, 2.75)
             ],
            [v for v in myFs.genChScPoints(0, 0)],
        )

class TestFrameSetgenAll(BaseTestClasses.TestBaseLogPass):
    """Test the FrameSet genAll()."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSetgenAll: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSetgenAll.test_00(): 2 frames of DEPT + Dipmeter 243, using genAll()."""
        myB = (
            bytes([64, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 1
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b"RHDT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(90) + b'000' + bytes([1,])+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 2
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        depStart = 2000.0
        depInterval = 4.0
        dep = depStart
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            fBy.extend(list(range(5))*16+list(range(5,15,1)))
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= depInterval
        #print()
        #print('genAll():', [v for v in myFs.genAll()])
        myRes = [v for v in myFs.genAll()]
        #pprint.pprint(myRes)
        self.assertEqual(
            [
                (0, 0, 0, 0, 0, 2000.0),
                # Fr, Ch, Sc, Sa, Bu, Val
                (0, 1, 0, 0, 0, 0.0),
                (0, 1, 0, 1, 0, 1.0),
                (0, 1, 0, 2, 0, 2.0),
                (0, 1, 0, 3, 0, 3.0),
                (0, 1, 0, 4, 0, 4.0),
                (0, 1, 0, 5, 0, 0.0),
                (0, 1, 0, 6, 0, 1.0),
                (0, 1, 0, 7, 0, 2.0),
                (0, 1, 0, 8, 0, 3.0),
                (0, 1, 0, 9, 0, 4.0),
                (0, 1, 0, 10, 0, 0.0),
                (0, 1, 0, 11, 0, 1.0),
                (0, 1, 0, 12, 0, 2.0),
                (0, 1, 0, 13, 0, 3.0),
                (0, 1, 0, 14, 0, 4.0),
                (0, 1, 0, 15, 0, 0.0),
                (0, 1, 1, 0, 0, 1.0),
                (0, 1, 1, 1, 0, 2.0),
                (0, 1, 1, 2, 0, 3.0),
                (0, 1, 1, 3, 0, 4.0),
                (0, 1, 1, 4, 0, 0.0),
                (0, 1, 1, 5, 0, 1.0),
                (0, 1, 1, 6, 0, 2.0),
                (0, 1, 1, 7, 0, 3.0),
                (0, 1, 1, 8, 0, 4.0),
                (0, 1, 1, 9, 0, 0.0),
                (0, 1, 1, 10, 0, 1.0),
                (0, 1, 1, 11, 0, 2.0),
                (0, 1, 1, 12, 0, 3.0),
                (0, 1, 1, 13, 0, 4.0),
                (0, 1, 1, 14, 0, 0.0),
                (0, 1, 1, 15, 0, 1.0),
                (0, 1, 2, 0, 0, 2.0),
                (0, 1, 2, 1, 0, 3.0),
                (0, 1, 2, 2, 0, 4.0),
                (0, 1, 2, 3, 0, 0.0),
                (0, 1, 2, 4, 0, 1.0),
                (0, 1, 2, 5, 0, 2.0),
                (0, 1, 2, 6, 0, 3.0),
                (0, 1, 2, 7, 0, 4.0),
                (0, 1, 2, 8, 0, 0.0),
                (0, 1, 2, 9, 0, 1.0),
                (0, 1, 2, 10, 0, 2.0),
                (0, 1, 2, 11, 0, 3.0),
                (0, 1, 2, 12, 0, 4.0),
                (0, 1, 2, 13, 0, 0.0),
                (0, 1, 2, 14, 0, 1.0),
                (0, 1, 2, 15, 0, 2.0),
                (0, 1, 3, 0, 0, 3.0),
                (0, 1, 3, 1, 0, 4.0),
                (0, 1, 3, 2, 0, 0.0),
                (0, 1, 3, 3, 0, 1.0),
                (0, 1, 3, 4, 0, 2.0),
                (0, 1, 3, 5, 0, 3.0),
                (0, 1, 3, 6, 0, 4.0),
                (0, 1, 3, 7, 0, 0.0),
                (0, 1, 3, 8, 0, 1.0),
                (0, 1, 3, 9, 0, 2.0),
                (0, 1, 3, 10, 0, 3.0),
                (0, 1, 3, 11, 0, 4.0),
                (0, 1, 3, 12, 0, 0.0),
                (0, 1, 3, 13, 0, 1.0),
                (0, 1, 3, 14, 0, 2.0),
                (0, 1, 3, 15, 0, 3.0),
                (0, 1, 4, 0, 0, 4.0),
                (0, 1, 4, 1, 0, 0.0),
                (0, 1, 4, 2, 0, 1.0),
                (0, 1, 4, 3, 0, 2.0),
                (0, 1, 4, 4, 0, 3.0),
                (0, 1, 4, 5, 0, 4.0),
                (0, 1, 4, 6, 0, 0.0),
                (0, 1, 4, 7, 0, 1.0),
                (0, 1, 4, 8, 0, 2.0),
                (0, 1, 4, 9, 0, 3.0),
                (0, 1, 4, 10, 0, 4.0),
                (0, 1, 4, 11, 0, 0.0),
                (0, 1, 4, 12, 0, 1.0),
                (0, 1, 4, 13, 0, 2.0),
                (0, 1, 4, 14, 0, 3.0),
                (0, 1, 4, 15, 0, 4.0),
                (0, 1, 5, 0, 0, 5.0),
                (0, 1, 6, 0, 0, 6.0),
                (0, 1, 7, 0, 0, 7.0),
                (0, 1, 8, 0, 0, 8.0),
                (0, 1, 9, 0, 0, 9.0),
                (0, 1, 10, 0, 0, 10.0),
                (0, 1, 11, 0, 0, 11.0),
                (0, 1, 12, 0, 0, 12.0),
                (0, 1, 13, 0, 0, 13.0),
                (0, 1, 14, 0, 0, 14.0),
                (1, 0, 0, 0, 0, 1996.0),
                (1, 1, 0, 0, 0, 0.0),
                (1, 1, 0, 1, 0, 1.0),
                (1, 1, 0, 2, 0, 2.0),
                (1, 1, 0, 3, 0, 3.0),
                (1, 1, 0, 4, 0, 4.0),
                (1, 1, 0, 5, 0, 0.0),
                (1, 1, 0, 6, 0, 1.0),
                (1, 1, 0, 7, 0, 2.0),
                (1, 1, 0, 8, 0, 3.0),
                (1, 1, 0, 9, 0, 4.0),
                (1, 1, 0, 10, 0, 0.0),
                (1, 1, 0, 11, 0, 1.0),
                (1, 1, 0, 12, 0, 2.0),
                (1, 1, 0, 13, 0, 3.0),
                (1, 1, 0, 14, 0, 4.0),
                (1, 1, 0, 15, 0, 0.0),
                (1, 1, 1, 0, 0, 1.0),
                (1, 1, 1, 1, 0, 2.0),
                (1, 1, 1, 2, 0, 3.0),
                (1, 1, 1, 3, 0, 4.0),
                (1, 1, 1, 4, 0, 0.0),
                (1, 1, 1, 5, 0, 1.0),
                (1, 1, 1, 6, 0, 2.0),
                (1, 1, 1, 7, 0, 3.0),
                (1, 1, 1, 8, 0, 4.0),
                (1, 1, 1, 9, 0, 0.0),
                (1, 1, 1, 10, 0, 1.0),
                (1, 1, 1, 11, 0, 2.0),
                (1, 1, 1, 12, 0, 3.0),
                (1, 1, 1, 13, 0, 4.0),
                (1, 1, 1, 14, 0, 0.0),
                (1, 1, 1, 15, 0, 1.0),
                (1, 1, 2, 0, 0, 2.0),
                (1, 1, 2, 1, 0, 3.0),
                (1, 1, 2, 2, 0, 4.0),
                (1, 1, 2, 3, 0, 0.0),
                (1, 1, 2, 4, 0, 1.0),
                (1, 1, 2, 5, 0, 2.0),
                (1, 1, 2, 6, 0, 3.0),
                (1, 1, 2, 7, 0, 4.0),
                (1, 1, 2, 8, 0, 0.0),
                (1, 1, 2, 9, 0, 1.0),
                (1, 1, 2, 10, 0, 2.0),
                (1, 1, 2, 11, 0, 3.0),
                (1, 1, 2, 12, 0, 4.0),
                (1, 1, 2, 13, 0, 0.0),
                (1, 1, 2, 14, 0, 1.0),
                (1, 1, 2, 15, 0, 2.0),
                (1, 1, 3, 0, 0, 3.0),
                (1, 1, 3, 1, 0, 4.0),
                (1, 1, 3, 2, 0, 0.0),
                (1, 1, 3, 3, 0, 1.0),
                (1, 1, 3, 4, 0, 2.0),
                (1, 1, 3, 5, 0, 3.0),
                (1, 1, 3, 6, 0, 4.0),
                (1, 1, 3, 7, 0, 0.0),
                (1, 1, 3, 8, 0, 1.0),
                (1, 1, 3, 9, 0, 2.0),
                (1, 1, 3, 10, 0, 3.0),
                (1, 1, 3, 11, 0, 4.0),
                (1, 1, 3, 12, 0, 0.0),
                (1, 1, 3, 13, 0, 1.0),
                (1, 1, 3, 14, 0, 2.0),
                (1, 1, 3, 15, 0, 3.0),
                (1, 1, 4, 0, 0, 4.0),
                (1, 1, 4, 1, 0, 0.0),
                (1, 1, 4, 2, 0, 1.0),
                (1, 1, 4, 3, 0, 2.0),
                (1, 1, 4, 4, 0, 3.0),
                (1, 1, 4, 5, 0, 4.0),
                (1, 1, 4, 6, 0, 0.0),
                (1, 1, 4, 7, 0, 1.0),
                (1, 1, 4, 8, 0, 2.0),
                (1, 1, 4, 9, 0, 3.0),
                (1, 1, 4, 10, 0, 4.0),
                (1, 1, 4, 11, 0, 0.0),
                (1, 1, 4, 12, 0, 1.0),
                (1, 1, 4, 13, 0, 2.0),
                (1, 1, 4, 14, 0, 3.0),
                (1, 1, 4, 15, 0, 4.0),
                (1, 1, 5, 0, 0, 5.0),
                (1, 1, 6, 0, 0, 6.0),
                (1, 1, 7, 0, 0, 7.0),
                (1, 1, 8, 0, 0, 8.0),
                (1, 1, 9, 0, 0, 9.0),
                (1, 1, 10, 0, 0, 10.0),
                (1, 1, 11, 0, 0, 11.0),
                (1, 1, 12, 0, 0, 12.0),
                (1, 1, 13, 0, 0, 13.0),
                (1, 1, 14, 0, 0, 14.0),
            ],
            myRes,
        )

    def test_01(self):
        """TestFrameSetgenAll.test_01(): 2 frames of DEPT + 5 Sample, 4 burst, using genAll()."""
        myB = (
            bytes([64, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 1
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b"MULT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(4*4*5) + b'000' + bytes([5,])+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 2
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        depStart = 2000.0
        depInterval = 4.0
        dep = depStart
        v = 0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            for s in range(5):
                for b in range(4):
                    fBy.extend(RepCode.writeBytes68(v))
                    v += 0.25
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= depInterval
#        print()
        myRes = [v for v in myFs.genAll()]
        #print('genAll():', myRes)
#        pprint.pprint(myRes)
        self.assertEqual(
            [
                # Fr, Ch, Sc, Sa, Bu, Val
                (0, 0, 0, 0, 0, 2000.0),
                (0, 1, 0, 0, 0, 0.0),
                (0, 1, 0, 0, 1, 0.25),
                (0, 1, 0, 0, 2, 0.5),
                (0, 1, 0, 0, 3, 0.75),
                (0, 1, 0, 1, 0, 1.0),
                (0, 1, 0, 1, 1, 1.25),
                (0, 1, 0, 1, 2, 1.5),
                (0, 1, 0, 1, 3, 1.75),
                (0, 1, 0, 2, 0, 2.0),
                (0, 1, 0, 2, 1, 2.25),
                (0, 1, 0, 2, 2, 2.5),
                (0, 1, 0, 2, 3, 2.75),
                (0, 1, 0, 3, 0, 3.0),
                (0, 1, 0, 3, 1, 3.25),
                (0, 1, 0, 3, 2, 3.5),
                (0, 1, 0, 3, 3, 3.75),
                (0, 1, 0, 4, 0, 4.0),
                (0, 1, 0, 4, 1, 4.25),
                (0, 1, 0, 4, 2, 4.5),
                (0, 1, 0, 4, 3, 4.75),
                (1, 0, 0, 0, 0, 1996.0),
                (1, 1, 0, 0, 0, 5.0),
                (1, 1, 0, 0, 1, 5.25),
                (1, 1, 0, 0, 2, 5.5),
                (1, 1, 0, 0, 3, 5.75),
                (1, 1, 0, 1, 0, 6.0),
                (1, 1, 0, 1, 1, 6.25),
                (1, 1, 0, 1, 2, 6.5),
                (1, 1, 0, 1, 3, 6.75),
                (1, 1, 0, 2, 0, 7.0),
                (1, 1, 0, 2, 1, 7.25),
                (1, 1, 0, 2, 2, 7.5),
                (1, 1, 0, 2, 3, 7.75),
                (1, 1, 0, 3, 0, 8.0),
                (1, 1, 0, 3, 1, 8.25),
                (1, 1, 0, 3, 2, 8.5),
                (1, 1, 0, 3, 3, 8.75),
                (1, 1, 0, 4, 0, 9.0),
                (1, 1, 0, 4, 1, 9.25),
                (1, 1, 0, 4, 2, 9.5),
                (1, 1, 0, 4, 3, 9.75),
             ],
            myRes,
        )


@pytest.mark.slow
class TestFrameSet_Perf_Ctor(BaseTestClasses.TestBaseLogPass):
    """Test the preformance of a FrameSet."""
    NUMBER_OF_CTOR = 1
    
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSet_Perf: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSet_Perf_Ctor.test_00(): FrameSet ctor, 128 frames  128 LIS bytes long."""
        myFile = self._createFileDFSROnly(128//4, 1, 1)
        myDfsr =  LogiRec.LrDFSRRead(myFile)
        lisLen = myDfsr.frameSize()
        numBytes = 0
        tS = time.perf_counter()
        for i in range(self.NUMBER_OF_CTOR):
            myFs = FrameSet.FrameSet(myDfsr, slice(128))
            if i == 0:
                lisLen *= myFs.numFrames
            numBytes += myFs.nbytes
        self.writeCostToStderr(tS, lisLen*self.NUMBER_OF_CTOR, 'LIS MB', lisLen // (1024**2))

    def test_01(self):
        """TestFrameSet_Perf_Ctor.test_01(): FrameSet ctor,  1k frames  128 LIS bytes long."""
        myFile = self._createFileDFSROnly(128//4, 1, 1)
        myDfsr =  LogiRec.LrDFSRRead(myFile)
        lisLen = myDfsr.frameSize()
        numBytes = 0
        tS = time.perf_counter()
        for i in range(self.NUMBER_OF_CTOR):
            myFs = FrameSet.FrameSet(myDfsr, slice(1*1024))
            if i == 0:
                lisLen *= myFs.numFrames
            numBytes += myFs.nbytes
        self.writeCostToStderr(tS, lisLen*self.NUMBER_OF_CTOR, 'LIS MB', lisLen // (1024**2))

    def test_02(self):
        """TestFrameSet_Perf_Ctor.test_02(): FrameSet ctor,  8k frames  128 LIS bytes long."""
        myFile = self._createFileDFSROnly(128//4, 1, 1)
        myDfsr =  LogiRec.LrDFSRRead(myFile)
        lisLen = myDfsr.frameSize()
        #print()
        #print('lisLen', lisLen)
        numBytes = 0
        tS = time.perf_counter()
        for i in range(self.NUMBER_OF_CTOR):
            myFs = FrameSet.FrameSet(myDfsr, slice(8*1024))
            if i == 0:
                lisLen *= myFs.numFrames
                #print('myFs.numFrames', myFs.numFrames)
            numBytes += myFs.nbytes
        self.writeCostToStderr(tS, lisLen*self.NUMBER_OF_CTOR, 'LIS MB', lisLen // (1024**2))

    def test_10(self):
        """TestFrameSet_Perf_Ctor.test_10(): FrameSet ctor, 128 frames 1024 LIS bytes long."""
        myFile = self._createFileDFSROnly(1024//4, 1, 1)
        myDfsr =  LogiRec.LrDFSRRead(myFile)
        lisLen = myDfsr.frameSize()
        numBytes = 0
        tS = time.perf_counter()
        for i in range(self.NUMBER_OF_CTOR):
            myFs = FrameSet.FrameSet(myDfsr, slice(128))
            if i == 0:
                lisLen *= myFs.numFrames
            numBytes += myFs.nbytes
        self.writeCostToStderr(tS, lisLen*self.NUMBER_OF_CTOR, 'LIS MB', lisLen // (1024**2))

    def test_11(self):
        """TestFrameSet_Perf_Ctor.test_11(): FrameSet ctor,  1k frames 1024 LIS bytes long."""
        myFile = self._createFileDFSROnly(1024//4, 1, 1)
        myDfsr =  LogiRec.LrDFSRRead(myFile)
        lisLen = myDfsr.frameSize()
        numBytes = 0
        tS = time.perf_counter()
        for i in range(self.NUMBER_OF_CTOR):
            myFs = FrameSet.FrameSet(myDfsr, slice(1024))
            if i == 0:
                lisLen *= myFs.numFrames
            numBytes += myFs.nbytes
        self.writeCostToStderr(tS, lisLen*self.NUMBER_OF_CTOR, 'LIS MB', lisLen // (1024**2))

    def test_12(self):
        """TestFrameSet_Perf_Ctor.test_12(): FrameSet ctor,  8k frames 1024 LIS bytes long."""
        myFile = self._createFileDFSROnly(1024//4, 1, 1)
        myDfsr =  LogiRec.LrDFSRRead(myFile)
        lisLen = myDfsr.frameSize()
        numBytes = 0
        tS = time.perf_counter()
        for i in range(self.NUMBER_OF_CTOR):
            myFs = FrameSet.FrameSet(myDfsr, slice(64*1024))
            if i == 0:
                lisLen *= myFs.numFrames
            numBytes += myFs.nbytes
        self.writeCostToStderr(tS, lisLen*self.NUMBER_OF_CTOR, 'LIS MB', lisLen // (1024**2))

    def test_20(self):
        """TestFrameSet_Perf_Ctor.test_20(): FrameSet ctor, 128 frames 8096 LIS bytes long."""
        myFile = self._createFileDFSROnly(1024//4, 8, 1)
        myDfsr =  LogiRec.LrDFSRRead(myFile)
        lisLen = myDfsr.frameSize()
        numBytes = 0
        tS = time.perf_counter()
        for i in range(self.NUMBER_OF_CTOR):
            myFs = FrameSet.FrameSet(myDfsr, slice(128))
            if i == 0:
                lisLen *= myFs.numFrames
            numBytes += myFs.nbytes
        self.writeCostToStderr(tS, lisLen*self.NUMBER_OF_CTOR, 'LIS MB', lisLen // (1024**2))

    def test_21(self):
        """TestFrameSet_Perf_Ctor.test_21(): FrameSet ctor,  1k frames 8096 LIS bytes long."""
        myFile = self._createFileDFSROnly(1024//4, 8, 1)
        myDfsr =  LogiRec.LrDFSRRead(myFile)
        lisLen = myDfsr.frameSize()
        numBytes = 0
        tS = time.perf_counter()
        for i in range(self.NUMBER_OF_CTOR):
            myFs = FrameSet.FrameSet(myDfsr, slice(1024))
            if i == 0:
                lisLen *= myFs.numFrames
            numBytes += myFs.nbytes
        self.writeCostToStderr(tS, lisLen*self.NUMBER_OF_CTOR, 'LIS MB', lisLen // (1024**2))

    def test_22(self):
        """TestFrameSet_Perf_Ctor.test_22(): FrameSet ctor,  8k frames 8096 LIS bytes long."""
        myFile = self._createFileDFSROnly(1024//4, 8, 1)
        myDfsr =  LogiRec.LrDFSRRead(myFile)
        lisLen = myDfsr.frameSize()
        numBytes = 0
        tS = time.perf_counter()
        for i in range(self.NUMBER_OF_CTOR):
            myFs = FrameSet.FrameSet(myDfsr, slice(8*1024))
            if i == 0:
                lisLen *= myFs.numFrames
            numBytes += myFs.nbytes
        self.writeCostToStderr(tS, lisLen*self.NUMBER_OF_CTOR, 'LIS MB', lisLen // (1024**2))


@pytest.mark.slow
class TestFrameSet_Perf_Load(BaseTestClasses.TestBaseLogPass):
    """Test the preformance of a FrameSet loading data."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSet_Perf_Load: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSet_Perf_Load.test_00(): load 1024 frames of 1024 bytes."""
        numCh = 1024//4
        myFile = self._createFileDFSROnly(numCh, 1, 1)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(1024))
        by = b'\x44\x4C\x80\x00' * (numCh)
        lisLen = 0
        tS = time.perf_counter()
        for i in range(1024):
            myFs.setFrameBytes(by, i, 0, numCh-1)
            lisLen += len(by)
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))

    def test_01(self):
        """TestFrameSet_Perf_Load.test_01(): load   32 frames of 128 bytes of 'real' data."""
        numCh = 128//4
        numFr = 32
        myFile = self._createFileDFSROnly(numCh, 1, 1)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        val = 1.0
        tS = time.perf_counter()
        lisLen = 0
        for fr in range(numFr):
            by = bytearray()
            for ch in range(numCh):
                by.extend(RepCode.STRUCT_RC_68.pack(RepCode.to68(val)))
                val += 1.0
                lisLen += 4
            myFs.setFrameBytes(by, fr, 0, numCh-1)
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))
        #print()
        #print('TestFrameSet_Perf_Load.test_01() array:\n', myFs._frames)


@pytest.mark.slow
class TestFrameSet_Perf_Read(BaseTestClasses.TestBaseLogPass):
    """Test the preformance of a FrameSet loading data then reading."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSet_Perf_Load: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSet_Perf_Read.test_00(): read 1024 frames of 1024 bytes using value()."""
        numCh = 1024//4
        numSa = 1
        numBu = 1
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (numCh * numSa * numBu)
        lisLen = 0
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        for fr in range(numFr):
            for ch in range(numCh):
                myFs.value(fr, ch, 0, 0, 0)
                lisLen += 4
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))


@pytest.mark.slow
class TestFrameSet_Perf_Read_Gen(BaseTestClasses.TestBaseLogPass):
    """Test the preformance of a FrameSet loading data then reading using generators."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSet_Perf_Load: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSet_Perf_Read.test_00(): 1024 frames of 1024 bytes, using genChScValues()."""
        numCh = 1024//4
        numSa = 1
        numBu = 1
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (numCh * numSa * numBu)
        lisLen = 0
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        for ch in range(numCh):
            for v in myFs.genChScValues(ch, 0):
                lisLen += 4
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))

    def test_01(self):
        """TestFrameSet_Perf_Read.test_01(): 8192 frames of 1024 bytes, using genChScValues()."""
        numCh = 1024//4
        numSa = 1
        numBu = 1
        numFr = 1024 * 8
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        self.assertEqual(256, len(myDfsr.dsbBlocks))
        #print('myDfsr.dsbBlocks[0]', myDfsr.dsbBlocks[0].samples(0))
        self.assertEqual(4 * (1 + ((numCh - 1) * numSa * numBu)), myDfsr.frameSize())
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (1 + ((numCh - 1) * numSa * numBu))
        lisLen = 0
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        for ch in range(numCh):
            for v in myFs.genChScValues(ch, 0):
                lisLen += 4
        self.writeCostToStderr(tS, lisLen, 'LIS MB', (lisLen + 512*1024) // (1024**2))

    def test_02(self):
        """TestFrameSet_Perf_Read.test_02(): 1024 frames of 8192 bytes, using genChScValues()."""
        numCh = 1024//4
        numSa = 1
        numBu = 8
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        self.assertEqual(256, len(myDfsr.dsbBlocks))
        #print('myDfsr.dsbBlocks[0]', myDfsr.dsbBlocks[0].samples(0))
        self.assertEqual(4 * (1 + ((numCh - 1) * numSa * numBu)), myDfsr.frameSize())
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (1 + ((numCh - 1) * numSa * numBu))
        lisLen = 0
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        for ch in range(numCh):
            for v in myFs.genChScValues(ch, 0):
                lisLen += 4
        self.writeCostToStderr(tS, lisLen, 'LIS MB', (lisLen + 512*1024) // (1024**2))

    def test_03(self):
        """TestFrameSet_Perf_Read.test_03(): 1024 frames of  128 bytes, using genChScValues()."""
        numCh = 128//4
        numSa = 1
        numBu = 1
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        self.assertEqual(4 * (1 + ((numCh - 1) * numSa * numBu)), myDfsr.frameSize())
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (1 + ((numCh - 1) * numSa * numBu))
        lisLen = 0
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        for ch in range(numCh):
            for v in myFs.genChScValues(ch, 0):
                lisLen += 4
        self.writeCostToStderr(tS, lisLen, 'LIS MB', (lisLen + 512*1024) // (1024**2))


@pytest.mark.slow
class TestFrameSet_Perf_Read_GenAll(BaseTestClasses.TestBaseLogPass):
    """Test the preformance of a FrameSet loading data then reading using generators."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSet_Perf_Load: Tests setUp() and tearDown()."""
        pass
    
    def test_10(self):
        """TestFrameSet_Perf_Read.test_10(): 1024 frames of 1024 bytes, using genAll()."""
        numCh = 1024//4
        numSa = 1
        numBu = 1
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (numCh * numSa * numBu)
        lisLen = 0
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        for t in myFs.genAll():
            lisLen += 4
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))

    def test_10_01(self):
        """TestFrameSet_Perf_Read.test_10_01():   32 frames of 32 bytes, using genAll()."""
        numCh = 32//4
        numSa = 1
        numBu = 1
        numFr = 32
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (numCh * numSa * numBu)
        lisLen = 0
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        for t in myFs.genAll():
            #print(t)
            lisLen += 4
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))


@pytest.mark.slow
class TestFrameSet_Perf_Read_GenPoints(BaseTestClasses.TestBaseLogPass):
    """Test the preformance of a FrameSet loading data then reading using genChScPoints.
    genChScPoints() is used for plotting"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSet_Perf_Read_GenPoints: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSet_Perf_Read_GenPoints.test_00(): 1024 frames of 1024 bytes, using genChScPoints()."""
        numCh = 1024//4
        numSa = 1
        numBu = 1
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (numCh * numSa * numBu)
        lisLen = 0
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        for ch in range(numCh):
            for v in myFs.genChScPoints(ch, 0):
                lisLen += 4
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))

    def test_01(self):
        """TestFrameSet_Perf_Read_GenPoints.test_01(): 8192 frames of 1024 bytes, using genChScPoints()."""
        numCh = 1024//4
        numSa = 1
        numBu = 1
        numFr = 1024 * 8
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        self.assertEqual(256, len(myDfsr.dsbBlocks))
        #print('myDfsr.dsbBlocks[0]', myDfsr.dsbBlocks[0].samples(0))
        self.assertEqual(4 * (1 + ((numCh - 1) * numSa * numBu)), myDfsr.frameSize())
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (1 + ((numCh - 1) * numSa * numBu))
        lisLen = 0
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        for ch in range(numCh):
            for v in myFs.genChScPoints(ch, 0):
                lisLen += 4
        self.writeCostToStderr(tS, lisLen, 'LIS MB', (lisLen + 512*1024) // (1024**2))

    def test_02(self):
        """TestFrameSet_Perf_Read_GenPoints.test_02(): 1024 frames of 8192 bytes, using genChScPoints()."""
        numCh = 1024//4
        numSa = 1
        numBu = 8
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        self.assertEqual(256, len(myDfsr.dsbBlocks))
        #print('myDfsr.dsbBlocks[0]', myDfsr.dsbBlocks[0].samples(0))
        self.assertEqual(4 * (1 + ((numCh - 1) * numSa * numBu)), myDfsr.frameSize())
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (1 + ((numCh - 1) * numSa * numBu))
        lisLen = 0
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        for ch in range(numCh):
            for v in myFs.genChScPoints(ch, 0):
                lisLen += 4
        self.writeCostToStderr(tS, lisLen, 'LIS MB', (lisLen + 512*1024) // (1024**2))

    def test_03(self):
        """TestFrameSet_Perf_Read_GenPoints.test_03(): 1024 frames of  128 bytes, using genChScPoints()."""
        numCh = 128//4
        numSa = 1
        numBu = 1
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        self.assertEqual(4 * (1 + ((numCh - 1) * numSa * numBu)), myDfsr.frameSize())
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (1 + ((numCh - 1) * numSa * numBu))
        lisLen = 0
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        for ch in range(numCh):
            for v in myFs.genChScPoints(ch, 0):
                lisLen += 4
        self.writeCostToStderr(tS, lisLen, 'LIS MB', (lisLen + 512*1024) // (1024**2))

    def test_04(self):
        """TestFrameSet_Perf_Read_GenPoints.test_04(): 8*1024 frames of Dipmeter 243, using genChScPoints()."""
        myB = (
            bytes([64, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        # Sensor 0
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
        myB += (
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            b"RHDT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(90) + b'000' + bytes([1,])+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 8*1024
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        depStart = 20000.0
        depInterval = 4.0
        dep = depStart
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            fBy.extend(list(range(5))*16+list(range(5,15,1)))
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= depInterval
        lisLen = 0
        tS = time.perf_counter()
#        # Ch/Sc 0/0 - depth
#        for v in myFs.genChScPoints(0, 0):
#            lisLen += 4
        # Dipmeter
        for sc in range(0, 15, 1):
            for v in myFs.genChScPoints(1, sc):
                lisLen += 1
        self.writeCostToStderr(tS, lisLen, 'LIS MB', (lisLen + 512*1024) // (1024**2))

    def test_05(self):
        """TestFrameSet_Perf_Read_GenPoints.test_05(): 1024 frames of  128 bytes, 8 samples, using genChScPoints()."""
        numCh = 128//4
        numSa = 8
        numBu = 1
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        self.assertEqual(4 * (1 + ((numCh - 1) * numSa * numBu)), myDfsr.frameSize())
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (1 + ((numCh - 1) * numSa * numBu))
        lisLen = 0
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        for ch in range(numCh):
            for v in myFs.genChScPoints(ch, 0):
                lisLen += 4
        self.writeCostToStderr(tS, lisLen, 'LIS MB', (lisLen + 512*1024) // (1024**2))

    def test_06(self):
        """TestFrameSet_Perf_Read_GenPoints.test_06(): 1024 frames of  128 bytes, 8 bursts, using genChScPoints()."""
        numCh = 128//4
        numSa = 1
        numBu = 8
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        self.assertEqual(4 * (1 + ((numCh - 1) * numSa * numBu)), myDfsr.frameSize())
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (1 + ((numCh - 1) * numSa * numBu))
        lisLen = 0
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        for ch in range(numCh):
            for v in myFs.genChScPoints(ch, 0):
                lisLen += 4
        self.writeCostToStderr(tS, lisLen, 'LIS MB', (lisLen + 512*1024) // (1024**2))

    def test_07(self):
        """TestFrameSet_Perf_Read_GenPoints.test_07(): 1024 frames of  128 bytes, 8 samples, 8 bursts, using genChScPoints()."""
        numCh = 128//4
        numSa = 8
        numBu = 8
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        self.assertEqual(4 * (1 + ((numCh - 1) * numSa * numBu)), myDfsr.frameSize())
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (1 + ((numCh - 1) * numSa * numBu))
        lisLen = 0
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        for ch in range(numCh):
            for v in myFs.genChScPoints(ch, 0):
                lisLen += 4
        self.writeCostToStderr(tS, lisLen, 'LIS MB', (lisLen + 512*1024) // (1024**2))


@pytest.mark.slow
class TestFrameSet_Perf_Accumulate(BaseTestClasses.TestBaseLogPass):
    """Test the preformance of a FrameSet loading data then using accumulate()."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestFrameSet_Perf_Load: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestFrameSet_Perf_Read.test_00(): 1024 fr of 256 ch, accumulate() mean."""
        numCh = 1024//4
        numSa = 1
        numBu = 1
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (numCh * numSa * numBu)
        lisLen = 1024**2
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        myArray = myFs.accumulate([FrameSet.AccMean])
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))
        #print()
        #print(myArray)

    def test_01(self):
        """TestFrameSet_Perf_Read.test_01(): 1024 fr of 256 ch, accumulate() min/mean/max."""
        numCh = 1024//4
        numSa = 1
        numBu = 1
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (numCh * numSa * numBu)
        lisLen = 1024**2
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        myArray = myFs.accumulate([FrameSet.AccMin, FrameSet.AccMax, FrameSet.AccMean])
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))
        #print()
        #print(myArray)

    def test_02(self):
        """TestFrameSet_Perf_Read.test_02(): DEPT, Dipmeter 243, 16 sub-ch accumulate() min/mean/max."""
        myB = (
            bytes([64, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        # Sensor 0
        myB += (
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            b"RHDT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(90) + b'000' + bytes([1,])+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 16*1024
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        dep = 10000.0
        v = 0
        lisLen = 0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            for b in range(90):
                fBy.extend(RepCode.writeBytes66(v % 256))
                v += 1
            lisLen += 4+90
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= 0.5
        tS = time.perf_counter()
        myArray = myFs.accumulate([FrameSet.AccMin, FrameSet.AccMean, FrameSet.AccMax])
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))
        #print()
        #pprint.pprint(myArray)

    def test_10(self):
        """TestFrameSet_Perf_Read.test_10(): 1024 fr of 256 ch, numpy mean."""
        numCh = 1024//4
        numSa = 1
        numBu = 1
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (numCh * numSa * numBu)
        lisLen = 1024**2
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        myArrayNp = []
        for ch in range(numCh):
            myArrayNp.append(
                [
                    myFs.frames[:,ch].mean(),
                ]
            )
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))
        myArray = numpy.array(myFs.accumulate([FrameSet.AccMean,]))
#        print()
#        print(myArray)
#        print(myArrayNp)
        self.assertTrue((myArray == myArrayNp).all())

    def test_11(self):
        """TestFrameSet_Perf_Read.test_11(): 1024 fr of 256 ch, numpy min/mean/max."""
        numCh = 1024//4
        numSa = 1
        numBu = 1
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (numCh * numSa * numBu)
        lisLen = 1024**2
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        myArrayNp = []
        for ch in range(numCh):
            myArrayNp.append(
                [
                    myFs.frames[:,ch].min(),
                    myFs.frames[:,ch].mean(),
                    myFs.frames[:,ch].max(),
                ]
            )
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))
        myArray = numpy.array(myFs.accumulate([FrameSet.AccMin, FrameSet.AccMax, FrameSet.AccMean]))
#        print()
#        print(myArray)
#        print(myArrayNp)
        self.assertTrue((myArray == myArrayNp).all())

    def test_12(self):
        """TestFrameSet_Perf_Read.test_12(): 1024 fr of 256 ch, numpy min/mean/max etc. (8 ops)."""
        numCh = 1024//4
        numSa = 1
        numBu = 1
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (numCh * numSa * numBu)
        lisLen = 1024**2
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        myArrayNp = []
        for ch in range(numCh):
            myArrayNp.append(
                [
                    myFs.frames[:,ch].min(),
                    myFs.frames[:,ch].mean(),
                    myFs.frames[:,ch].max(),
                    myFs.frames[:,ch].std(),
                    myFs.frames[:,ch].var(),
                    myFs.frames[:,ch].ptp(),
                    myFs.frames[:,ch].argmax(),
                    myFs.frames[:,ch].argmax(),
                ]
            )
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))
#        myArray = numpy.array(myFs.accumulate([FrameSet.AccMin, FrameSet.AccMax, FrameSet.AccMean]))
#        print()
#        print(myArray)
#        print(myArrayNp)
#        self.assertTrue((myArray == myArrayNp).all())

    def test_15(self):
        """TestFrameSet_Perf_Read.test_15(): 1024 fr of 256 ch, numpy frameView().min/mean/max etc. (8 ops)."""
        numCh = 1024//4
        numSa = 1
        numBu = 1
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (numCh * numSa * numBu)
        lisLen = 1024**2
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        myArrayNp = []
        for ch in range(numCh):
            npView = myFs.frameView(ch, 0)
            myArrayNp.append(
                [
                    npView.min(),
                    npView.mean(),
                    npView.max(),
                    npView.std(),
                    npView.var(),
                    npView.ptp(),
                    npView.argmin(),
                    npView.argmax(),
                ]
            )
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))
#        myArray = numpy.array(myFs.accumulate([FrameSet.AccMin, FrameSet.AccMax, FrameSet.AccMean]))
#        print()
#        print(myArray)
#        print(myArrayNp)
#        self.assertTrue((myArray == myArrayNp).all())

    def test_17(self):
        """TestFrameSet_Perf_Read.test_17(): DEPT, Dipmeter 243, 16 sub-ch frameView() min/mean/max."""
        myB = (
            bytes([64, 0])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        # Sensor 0
        myB += (
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            b"RHDT" + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes      Pad      samples      Rep code        Process indicators
            + self._twoBytes(90) + b'000' + bytes([1,])+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        numFr = 16*1024
        myFile = self._retFileFromBytes(self._retSinglePr(myB))
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        dep = 10000.0
        v = 0
        lisLen = 0
        # Load the FrameSet
        for f in range(numFr):
            fBy = bytearray(RepCode.writeBytes68(dep))
            for b in range(90):
                fBy.extend(RepCode.writeBytes66(v % 256))
                v += 1
            lisLen += 4+90
            myFs.setFrameBytes(by=fBy, fr=f, chFrom=0, chTo=1)
            dep -= 0.5
        tS = time.perf_counter()
        myArrayNp = []
        for ch in range(myFs.numChannels):
            myScArray = []
            for sc in range(myFs.numSubChannels(ch)):
                npView = myFs.frameView(ch, sc)
                myScArray.append(
                    [
                        npView.min(),
                        npView.mean(),
                        npView.max(),
                    ]
                )
            myArrayNp.append(myScArray)
#        myArray = myFs.accumulate([FrameSet.AccMin, FrameSet.AccMean, FrameSet.AccMax])
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))
#        print()
#        pprint.pprint(myArrayNp)

    def test_21(self):
        """TestFrameSet_Perf_Read.test_21(): 1024 fr of 256 ch, numpy dec/eq/inc with frameView()."""
        numCh = 1024//4
        numSa = 1
        numBu = 1
        numFr = 1024
        myFile = self._createFileDFSROnly(numCh, numSa, numBu)
        myDfsr = LogiRec.LrDFSRRead(myFile)
        myFs = FrameSet.FrameSet(myDfsr, slice(numFr))
        by = b'\x44\x4C\x80\x00' * (numCh * numSa * numBu)
        lisLen = 1024**2
        for i in range(numFr):
            myFs.setFrameBytes(by, i, 0, numCh-1)
        tS = time.perf_counter()
        myArrayNp = []
        for ch in range(numCh):
            npView = myFs.frameView(ch, 0)
            myArrayNp.append(
                cFrameSet.decEqInc(npView),
            )
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))
#        myArray = numpy.array(myFs.accumulate([FrameSet.AccMin, FrameSet.AccMax, FrameSet.AccMean]))
#        print()
#        print(myArray)
#        print(myArrayNp)
#        self.assertTrue((myArray == myArrayNp).all())


class Special(BaseTestClasses.TestBaseFile):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSet_SuChArTe))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSet_ChArTe))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSet_ChArTe_Dipmeter))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSetStaticData))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSet))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSet_offsetTree))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSet_setFrameBytes))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSet_setFrameBytes_Indirect))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSetAccumulate))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSetgenChScValues))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSetgenChScPoints_LowLevel))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSetgenChScPoints))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSetgenAll))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSet_Perf_Ctor))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSet_Perf_Load))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSet_Perf_Read))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSet_Perf_Read_Gen))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSet_Perf_Read_GenAll))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSet_Perf_Read_GenPoints))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFrameSet_Perf_Accumulate))
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
    print(('TestClass.py script version "%s", dated %s' % (__version__, __date__)))
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
