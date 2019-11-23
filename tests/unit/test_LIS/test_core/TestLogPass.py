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
"""Tests various classes for use by the preprocessor for keeping track of the
location in a set of files.
"""
import pytest

__author__  = 'Paul Ross'
__date__    = '10 Jan 2011'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'

import os
import sys
import time
import logging
import collections

import numpy

from TotalDepth.LIS.core import RepCode
from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import LogPass
from TotalDepth.LIS.core import EngVal
from TotalDepth.LIS.core import Mnem

######################
# Section: Unit tests.
######################
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import BaseTestClasses

class TestLogPass_LowLevel(BaseTestClasses.TestBaseFile):
    """Tests LogPass"""
    def setUp(self):
        """Set up."""
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 4, up/down value 0 (down)
            + bytes([4, 1, 66, 0])
            # EB 12, absent value -153.0
            + bytes([12, 4, 68])+b'\xbb\xb3\x80\x00'
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            # One sensor to avoid raises
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        myDfsr = LogiRec.LrDFSRRead(myF)
        self._lp = LogPass.LogPass(myDfsr, 'FileID')

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestLogPass_LowLevel: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestLogPass_LowLevel.test_00(): Construction."""
        self.assertEqual(len(self._lp._dfsr.dsbBlocks), 1)
        self.assertEqual(self._lp._dfsr.frameSize(), 4)
        
    def test_01(self):
        """TestLogPass_LowLevel.test_01(): _sliceFromList()."""
        self.assertRaises(LogPass.ExceptionLogPass, self._lp._sliceFromList, [])
        self.assertEqual(self._lp._sliceFromList([0,]), slice(0,1,1))
        self.assertEqual(self._lp._sliceFromList([7,]), slice(7,8,1))
        self.assertEqual(self._lp._sliceFromList([0,1,2]), slice(0, 3, 1))
        self.assertEqual(self._lp._sliceFromList([1,2]), slice(1, 3, 1))
        self.assertEqual(self._lp._sliceFromList([0,2]), slice(0, 3, 2))

    def test_02(self):
        """TestLogPass_LowLevel.test_02(): exercise various properties."""
        pass
        #print(self._lp.type01Plan)
        
    def test_10(self):
        """TestLogPass_LowLevel.test_10(): nullValue()."""
        self.assertEqual(-153.0, self._lp.nullValue)
        
class TestLogPassCtorRaises(BaseTestClasses.TestBaseFile):
    """Tests LogPass"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestLogPassNoSensors: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestLogPassCtorRaises: ctor raises when no sensors."""
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 4, up/down value 0 (down)
            + bytes([4, 1, 66, 0])
            # EB 12, absent value -153.0
            + bytes([12, 4, 68])+b'\xbb\xb3\x80\x00'
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            # No sensors
        )
        myDfsr = LogiRec.LrDFSRRead(myF)
        self.assertRaises(LogPass.ExceptionLogPassCtor, LogPass.LogPass, myDfsr, 'FileID')
    
    def test_01(self):
        """TestLogPassCtorRaises: ctor raises when xAxisIndex out of range."""
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 4, up/down value 0 (down)
            + bytes([4, 1, 66, 0])
            # EB 12, absent value -153.0
            + bytes([12, 4, 68])+b'\xbb\xb3\x80\x00'
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            # One sensor to avoid raises
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        myDfsr = LogiRec.LrDFSRRead(myF)
        self.assertRaises(LogPass.ExceptionLogPassCtor, LogPass.LogPass, myDfsr, 'FileID', xAxisIndex=-1)
        self.assertRaises(LogPass.ExceptionLogPassCtor, LogPass.LogPass, myDfsr, 'FileID', xAxisIndex=1)

class TestLogPassBadDFSR(BaseTestClasses.TestBaseFile):
    """Tests LogPass"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestLogPassBadDFSR: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestLogPassBadDFSR: single sensor with zero LIS length."""
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 4, up/down value 0 (down)
            + bytes([4, 1, 66, 0])
            # EB 12, absent value -153.0
            + bytes([12, 4, 68])+b'\xbb\xb3\x80\x00'
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            # Sensor 0 is zero length
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 0 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 0]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        myDfsr = LogiRec.LrDFSRRead(myF)
        self.assertRaises(LogPass.ExceptionLogPassCtor, LogPass.LogPass, myDfsr, 'FileID')
        #print()
        #print('myLp._dfsr.dsbBlocks', myLp._dfsr.dsbBlocks)
        #print('myLp._retChMap()', myLp._retChMap())
    
    def test_00_01(self):
        """TestLogPassBadDFSR: two sensors, second sensor with zero LIS length."""
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 4, up/down value 0 (down)
            + bytes([4, 1, 66, 0])
            # EB 12, absent value -153.0
            + bytes([12, 4, 68])+b'\xbb\xb3\x80\x00'
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 1 is zero length
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'GR  ' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 0 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 0]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        myDfsr = LogiRec.LrDFSRRead(myF)
        myLp = LogPass.LogPass(myDfsr, 'FileID')
#        print()
#        print('myLp._dfsr.dsbBlocks', myLp._dfsr.dsbBlocks)
#        print('myLp._retChMap()', myLp._retChMap())
#        print('myLp.longStr()\n', myLp.longStr())
        myLp.longStr()
    
    def test_01(self):
        """TestLogPassBadDFSR: two sensors with same name."""
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 4, up/down value 0 (down)
            + bytes([4, 1, 66, 0])
            # EB 12, absent value -153.0
            + bytes([12, 4, 68])+b'\xbb\xb3\x80\x00'
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 0 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 1
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 0 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        myDfsr = LogiRec.LrDFSRRead(myF)
        myLp = LogPass.LogPass(myDfsr, 'FileID')

class TestLogPassFromTestBase(BaseTestClasses.TestBaseLogPass):
    """Tests LogPass ctor and some internal functionality"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestLogPassBasic: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestLogPassFromBaseTestClasses.test_00(): Nine channels."""
        myF = self._retFileSinglePr(self._retDFSRBytes(9, 1, 1))
        myLp = LogPass.LogPass(LogiRec.LrDFSRRead(myF), 'FileID')
        self.assertEqual(len(myLp.dfsr.dsbBlocks), 9)
        self.assertEqual(myLp.dfsr.frameSize(), 4*9)
        str(myLp)

class TestLogPassStatic(BaseTestClasses.TestBaseFile):
    """Tests LogPass ctor and some internal functionality"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestLogPassStatic: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestLogPassStatic.test_00(): Five channels."""
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
            # 2 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 2]) + b'000' + b'\x01'+ bytes([79,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 4
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'BS  ' + b'ServID' + b'ServOrdN'+ b'MM  ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 8 LIS bytes     Pad      2 super  Rep code     Process indicators
            + bytes([0, 8]) + b'000' + b'\x02'+ bytes([73,]) + bytes([0, 1, 2, 3, 4])
        )
        myLp = LogPass.LogPass(LogiRec.LrDFSRRead(myF), 'FileID')
        self.assertEqual(len(myLp.dfsr.dsbBlocks), 5)
        self.assertEqual(myLp.dfsr.frameSize(), 34)
        #print()
        #print(myLp._chMap)
        self.assertEqual(
            {
                Mnem.Mnem(b'DEPT') : (0, 0),
                Mnem.Mnem(b'GR  ') : (1, 0),
                Mnem.Mnem(b'SUPE') : (2, 0),
                Mnem.Mnem(b'SMAL') : (3, 0),
                Mnem.Mnem(b'BS  ') : (4, 0),
            },
            myLp._chMap,
        )
        # Note we can get away with calling myLp._mnemToChSc() with a bytes
        # object if there is no trailing whitespace 
        self.assertEqual((0, 0), myLp._mnemToChSc(b'DEPT'))
        self.assertEqual((1, 0), myLp._mnemToChSc(Mnem.Mnem(b'GR  ')))
        self.assertEqual((2, 0), myLp._mnemToChSc(b'SUPE'))
        self.assertEqual((3, 0), myLp._mnemToChSc(b'SMAL'))
        self.assertEqual((4, 0), myLp._mnemToChSc(Mnem.Mnem(b'BS  ')))
        try:
            myLp._mnemToChSc(b'    ')
            self.fail('TotalDepth.LIS.core.LogPass.ExceptionLogPassKeyError not raised')
        except LogPass.ExceptionLogPassKeyError:
            pass
        # genFrameSetHeadings should raise as we have no FrameSet yet
        try:
            list(myLp.genFrameSetHeadings())
            self.fail('LogPass.ExceptionLogPassNoFrameSet not raised')
        except LogPass.ExceptionLogPassNoFrameSet:
            pass

    def test_10(self):
        """TestLogPassStatic.test_10(): DEPT and 234 Dipmeter."""
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
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'RHDT' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes      Pad      1 super  Rep code     Process indicators
            + bytes([0, 90]) + b'000' + b'\x01'+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        myLp = LogPass.LogPass(LogiRec.LrDFSRRead(myF), 'FileID')
        self.assertEqual(len(myLp.dfsr.dsbBlocks), 2)
        self.assertEqual(myLp.dfsr.frameSize(), 94)
        #print()
        #print(myLp._chMap)
        #pprint.pprint(myLp._chMap)
        self.assertEqual(
            {
                Mnem.Mnem(b'DEPT') : (0, 0),
                Mnem.Mnem(b'FC0 ') : (1, 0),
                Mnem.Mnem(b'FC1 ') : (1, 1),
                Mnem.Mnem(b'FC2 ') : (1, 2),
                Mnem.Mnem(b'FC3 ') : (1, 3),
                Mnem.Mnem(b'FC4 ') : (1, 4),
                Mnem.Mnem(b'STAT') : (1, 5),
                Mnem.Mnem(b'REF ') : (1, 6),
                Mnem.Mnem(b'REFC') : (1, 7),
                Mnem.Mnem(b'EMEX') : (1, 8),
                Mnem.Mnem(b'PADP') : (1, 9),
                Mnem.Mnem(b'TEMP') : (1, 10),
                Mnem.Mnem(b'FEP1') : (1, 11),
                Mnem.Mnem(b'FEP2') : (1, 12),
                Mnem.Mnem(b'RAC1') : (1, 13),
                Mnem.Mnem(b'RAC2') : (1, 14),
            },
            myLp._chMap,
        )
        # Note we can get away with calling myLp._mnemToChSc() with a bytes
        # object if there is no trailing whitespace 
        self.assertEqual((0, 0), myLp._mnemToChSc(b'DEPT'))
        self.assertEqual((1, 0), myLp._mnemToChSc(Mnem.Mnem(b'FC0 ')))
        self.assertEqual((1, 1), myLp._mnemToChSc(Mnem.Mnem(b'FC1 ')))
        self.assertEqual((1, 2), myLp._mnemToChSc(Mnem.Mnem(b'FC2 ')))
        self.assertEqual((1, 3), myLp._mnemToChSc(Mnem.Mnem(b'FC3 ')))
        self.assertEqual((1, 4), myLp._mnemToChSc(Mnem.Mnem(b'FC4 ')))
        self.assertEqual((1, 5), myLp._mnemToChSc(b'STAT'))
        self.assertEqual((1, 6), myLp._mnemToChSc(Mnem.Mnem(b'REF ')))
        self.assertEqual((1, 7), myLp._mnemToChSc(b'REFC'))
        self.assertEqual((1, 8), myLp._mnemToChSc(b'EMEX'))
        self.assertEqual((1, 9), myLp._mnemToChSc(b'PADP'))
        self.assertEqual((1, 10), myLp._mnemToChSc(b'TEMP'))
        self.assertEqual((1, 11), myLp._mnemToChSc(b'FEP1'))
        self.assertEqual((1, 12), myLp._mnemToChSc(b'FEP2'))
        self.assertEqual((1, 13), myLp._mnemToChSc(b'RAC1'))
        self.assertEqual((1, 14), myLp._mnemToChSc(b'RAC2'))        
        try:
            myLp._mnemToChSc(b'    ')
            self.fail('TotalDepth.LIS.core.LogPass.ExceptionLogPassKeyError not raised')
        except LogPass.ExceptionLogPassKeyError:
            pass
        # genFrameSetHeadings should raise as we have no FrameSet yet
        try:
            list(myLp.genFrameSetHeadings())
            self.fail('LogPass.ExceptionLogPassNoFrameSet not raised')
        except LogPass.ExceptionLogPassNoFrameSet:
            pass
        # Test units
        self.assertEqual('FEET', myLp.curveUnitsAsStr(b'DEPT'))
        self.assertEqual('    ', myLp.curveUnitsAsStr(Mnem.Mnem(b'FC0 ')))
        self.assertEqual('    ', myLp.curveUnitsAsStr(Mnem.Mnem(b'FC1 ')))
        self.assertEqual('    ', myLp.curveUnitsAsStr(Mnem.Mnem(b'FC2 ')))
        self.assertEqual('    ', myLp.curveUnitsAsStr(Mnem.Mnem(b'FC3 ')))
        self.assertEqual('    ', myLp.curveUnitsAsStr(Mnem.Mnem(b'FC4 ')))
        self.assertEqual('    ', myLp.curveUnitsAsStr(Mnem.Mnem(b'REF ')))
        self.assertEqual('    ', myLp.curveUnitsAsStr(b'STAT'))
        self.assertEqual('    ', myLp.curveUnitsAsStr(b'REFC'))
        self.assertEqual('    ', myLp.curveUnitsAsStr(b'EMEX'))
        self.assertEqual('    ', myLp.curveUnitsAsStr(b'PADP'))
        self.assertEqual('    ', myLp.curveUnitsAsStr(b'TEMP'))
        self.assertEqual('    ', myLp.curveUnitsAsStr(b'FEP1'))
        self.assertEqual('    ', myLp.curveUnitsAsStr(b'FEP2'))
        self.assertEqual('    ', myLp.curveUnitsAsStr(b'RAC1'))
        self.assertEqual('    ', myLp.curveUnitsAsStr(b'RAC2'))
        try:
            myLp.curveUnitsAsStr(b'????')
            self.fail('TotalDepth.LIS.core.LogPass.ExceptionLogPassKeyError not raised')
        except LogPass.ExceptionLogPassKeyError:
            pass

class TestLogPassStaticUpDirect(BaseTestClasses.TestBaseFile):
    """Tests LogPass static data functionality with a up log and direct X axis"""
    def setUp(self):
        """Set up."""
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
            # 2 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 2]) + b'000' + b'\x01'+ bytes([79,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 4
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'BS  ' + b'ServID' + b'ServOrdN'+ b'MM  ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 8 LIS bytes     Pad      2 super  Rep code     Process indicators
            + bytes([0, 8]) + b'000' + b'\x02'+ bytes([73,]) + bytes([0, 1, 2, 3, 4])
        )
        self._lp = LogPass.LogPass(LogiRec.LrDFSRRead(myF), 'FileID')
        self.assertEqual(len(self._lp.dfsr.dsbBlocks), 5)
        self.assertEqual(self._lp.dfsr.frameSize(), 34)

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestLogPassStaticUpDirect: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestLogPassStaticUpDirect.test_00(): retExtChIndexList()"""
        #print()
        #print('self.retExtChIndexList', self._lp.retExtChIndexList([Mnem.Mnem(b'BS  '), b'SMAL',]))
        # Note: need to use Mnem.Mnem() if trailing spaces
        self.assertEqual([3,4], self._lp.retExtChIndexList([Mnem.Mnem(b'BS  '), b'SMAL',]))

    def test_01(self):
        """TestLogPassStaticUpDirect.test_01(): retExtChIndexList() raises with b'DONTKNOW'."""
        # Note: need to use Mnem.Mnem() if trailing spaces
        try:
            self._lp.retExtChIndexList([Mnem.Mnem(b'BS  '), b'SMAL', b'DONTKNOW',])
            self.fail('TotalDepth.LIS.core.LogPass.ExceptionLogPassKeyError not raised')
        except LogPass.ExceptionLogPassKeyError:
            pass

class TestLogPassEventBase(BaseTestClasses.TestBaseFile):
    """Base class for event testing."""
    def _genEvents(self, theTellLrS, theLrSize, theFrames, theChannels, theNumChannelsInFrame):
        myDict = collections.defaultdict(int)
        tellLr = 0
        myEvts = []
        for evt in self._lp._genFrameSetEvents(theFrames, theChannels):
            #print('evt', evt)
            myEvts.append(evt)
            myDict[evt[0]] += 1
            if evt[0] == LogPass.EVENT_SEEK_LR:
                self.assertTrue(evt[1] in theTellLrS)
                tellLr = 0
            elif evt[0] in (LogPass.EVENT_SKIP, LogPass.EVENT_READ):
                #if not (tellLr >= 0 and tellLr < theLrSize):
                #    print('tellLr={:d} theLrSize={:d}'.format(tellLr, theLrSize))
                self.assertTrue(tellLr >= 0 and tellLr < theLrSize)
                if evt[0]  == LogPass.EVENT_READ:
                    # Read channels must be in theChannels
                    self.assertTrue(evt[3] is None or evt[3] in theChannels)
                    self.assertTrue(evt[4] is None or evt[4] in theChannels)
                else:
                    # Skip must be in range(theNumChannelsInFrame+1)
                    self.assertTrue(evt[3] is None or evt[3] in range(theNumChannelsInFrame+1))
                    self.assertTrue(evt[4] is None or evt[4] in range(theNumChannelsInFrame+1))
                tellLr += evt[1]
        return myEvts, myDict

class TestLogPass_Events_DownDirect(TestLogPassEventBase):
    """Tests LogPass"""
    def setUp(self):
        """Set up."""
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
            # 2 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 2]) + b'000' + b'\x01'+ bytes([79,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 4
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'BS  ' + b'ServID' + b'ServOrdN'+ b'MM  ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 8 LIS bytes     Pad      2 super  Rep code     Process indicators
            + bytes([0, 8]) + b'000' + b'\x02'+ bytes([73,]) + bytes([0, 1, 2, 3, 4])
        )
        myDfsr = LogiRec.LrDFSRRead(myF)
        self._lp = LogPass.LogPass(myDfsr, 'FileID')
        # 6 logical records, 8 frames/record (272 bytes each)
        # 48 frames
        # Note: Down log
        #Add: 1152 272 1000.0
        #Add: 1424 272 1004.0
        #Add: 1696 272 1008.0
        #Add: 1968 272 1012.0
        #Add: 2240 272 1016.0
        #Add: 2512 272 1020.0        
        #print()
        self._tellLrS = []
        self._lrSize = 34*8
        for lIdx in range(6):
            # 128 bytes of padding |-| logical records
            tellLr = 1024+128+lIdx*34*8
            self._tellLrS.append(tellLr)
            x = 1000.0 + 0.5*8*lIdx
            #print('Add:', tellLr, self._lrSize, x)
            self._lp.addType01Data(tellLr, 0, self._lrSize, x)

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestLogPass_DownDirect: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestLogPass_DownDirect.test_00(): Construction."""
        self.assertEqual(len(self._lp._dfsr.dsbBlocks), 5)
        self.assertEqual(self._lp._dfsr.frameSize(), 34)

    def test_01(self):
        """TestLogPass_DownDirect.test_01(): Iterate, all channels, first LR only, two frames."""
        myFrames = slice(2,4,1)
        myChannels = list(range(5))
        myEvts, myDict = self._genEvents(self._tellLrS, self._lrSize, myFrames, myChannels, 5)
        #print()
        #pprint.pprint(myEvts)
        self.assertEqual(
            [
                # First Logical record
                (LogPass.EVENT_SEEK_LR, 1152, None, None, None),
                # Skip two frames
                (LogPass.EVENT_SKIP, 68, 0, None, 0),
                (LogPass.EVENT_READ, 34, 0, 0, 4),
                (LogPass.EVENT_READ, 34, 1, 0, 4),
            ],
            myEvts,
        )
        #print(myDict)
        self.assertEqual(myDict[LogPass.EVENT_SEEK_LR], 1)
        self.assertEqual(myDict[LogPass.EVENT_READ], 2)
        self.assertEqual(myDict[LogPass.EVENT_SKIP], 1)

    def test_10(self):
        """TestLogPass_DownDirect.test_10(): Iterate, all channels, first LR only."""
        myFrames = slice(0,8,1)
        myChannels = list(range(5))
        myEvts, myDict = self._genEvents(self._tellLrS, self._lrSize, myFrames, myChannels, 5)
        #print()
        #pprint.pprint(myEvts)
        self.assertEqual(
            [
                # First Logical record
                (LogPass.EVENT_SEEK_LR, 1152, None, None, None),
                (LogPass.EVENT_READ, 34, 0, 0, 4),
                (LogPass.EVENT_READ, 34, 1, 0, 4),
                (LogPass.EVENT_READ, 34, 2, 0, 4),
                (LogPass.EVENT_READ, 34, 3, 0, 4),
                (LogPass.EVENT_READ, 34, 4, 0, 4),
                (LogPass.EVENT_READ, 34, 5, 0, 4),
                (LogPass.EVENT_READ, 34, 6, 0, 4),
                (LogPass.EVENT_READ, 34, 7, 0, 4),
            ],
            myEvts,
        )
        #print(myDict)
        self.assertEqual(myDict[LogPass.EVENT_SEEK_LR], 1)
        self.assertEqual(myDict[LogPass.EVENT_READ], 8)
        self.assertEqual(myDict[LogPass.EVENT_SKIP], 0)

    def test_11(self):
        """TestLogPass_DownDirect.test_11(): Iterate, all channels, first and second LR, frames=range(0,12,1)."""
        myFrames = slice(0,12,1)
        myChannels = list(range(5))
        myEvts, myDict = self._genEvents(self._tellLrS, self._lrSize, myFrames, myChannels, 5)
        #print(myDict)
        #print()
        #pprint.pprint(myEvts)
        self.assertEqual(
            [
                # First Logical record
                (LogPass.EVENT_SEEK_LR, 1152, None, None, None),
                (LogPass.EVENT_READ, 34, 0, 0, 4),
                (LogPass.EVENT_READ, 34, 1, 0, 4),
                (LogPass.EVENT_READ, 34, 2, 0, 4),
                (LogPass.EVENT_READ, 34, 3, 0, 4),
                (LogPass.EVENT_READ, 34, 4, 0, 4),
                (LogPass.EVENT_READ, 34, 5, 0, 4),
                (LogPass.EVENT_READ, 34, 6, 0, 4),
                (LogPass.EVENT_READ, 34, 7, 0, 4),
                (LogPass.EVENT_SEEK_LR, 1424, None, None, None),
                (LogPass.EVENT_READ, 34, 8, 0, 4),
                (LogPass.EVENT_READ, 34, 9, 0, 4),
                (LogPass.EVENT_READ, 34, 10, 0, 4),
                (LogPass.EVENT_READ, 34, 11, 0, 4),
            ],
            myEvts,
        )
        #print(myDict)
        self.assertEqual(myDict[LogPass.EVENT_SEEK_LR], 2)
        self.assertEqual(myDict[LogPass.EVENT_READ], 12)
        self.assertEqual(myDict[LogPass.EVENT_SKIP], 0)
        self.assertEqual(myDict[LogPass.EVENT_EXTRAPOLATE], 0)

    def test_12(self):
        """TestLogPass_DownDirect.test_12(): Iterate, all channels, first and second LR, frames=range(3,12,2)."""
        myFrames = slice(3,12,2)
        myChannels = list(range(5))
        myEvts, myDict = self._genEvents(self._tellLrS, self._lrSize, myFrames, myChannels, 5)
        #print(myDict)
        #print()
        #pprint.pprint(myEvts)
        self.assertEqual(
            [
                # First Logical record
                (LogPass.EVENT_SEEK_LR,    1152,   None,   None,   None),
                (LogPass.EVENT_SKIP,       102,    0,      None,   0),
                (LogPass.EVENT_READ,       34,     0,      0,      4),
                (LogPass.EVENT_SKIP,       34,     1,      None,   None),
                (LogPass.EVENT_READ,       34,     1,      0,      4),
                (LogPass.EVENT_SKIP,       34,     2,      None,   None),
                (LogPass.EVENT_READ,       34,     2,      0,      4),
                (LogPass.EVENT_SEEK_LR,    1424,   None,   None,   None),
                (LogPass.EVENT_SKIP,       34,     3,      None,   0),
                (LogPass.EVENT_READ,       34,     3,      0,      4),
                (LogPass.EVENT_SKIP,       34,     4,      None,   None),
                (LogPass.EVENT_READ,       34,     4,      0,      4),
            ],
            myEvts,
        )
        #print(myDict)
        self.assertEqual(myDict[LogPass.EVENT_SEEK_LR], 2)
        self.assertEqual(myDict[LogPass.EVENT_READ], 5)
        self.assertEqual(myDict[LogPass.EVENT_SKIP], 5)
        self.assertEqual(myDict[LogPass.EVENT_EXTRAPOLATE], 0)

    def test_13(self):
        """TestLogPass_DownDirect.test_13(): Iterate, ch[1,3], first and second LR, frames=range(3,12,2)."""
        myFrames = slice(3,12,2)
        myChannels = [1,3]
        myEvts, myDict = self._genEvents(self._tellLrS, self._lrSize, myFrames, myChannels, 5)
        #print(myDict)
        #print()
        #pprint.pprint(myEvts)
        self.assertEqual(
            [
                (LogPass.EVENT_SEEK_LR,    1152,   None,   None,   None),
                (LogPass.EVENT_SKIP,       106,    0,      0,      0),
                (LogPass.EVENT_READ,       4,      0,      1,      1),
                (LogPass.EVENT_SKIP,       16,     0,      2,      2),
                (LogPass.EVENT_READ,       2,      0,      3,      3),
                (LogPass.EVENT_SKIP,       46,     1,      4,      0),
                (LogPass.EVENT_READ,       4,      1,      1,      1),
                (LogPass.EVENT_SKIP,       16,     1,      2,      2),
                (LogPass.EVENT_READ,       2,      1,      3,      3),
                (LogPass.EVENT_SKIP,       46,     2,      4,      0),
                (LogPass.EVENT_READ,       4,      2,      1,      1),
                (LogPass.EVENT_SKIP,       16,     2,      2,      2),
                (LogPass.EVENT_READ,       2,      2,      3,      3),
                (LogPass.EVENT_SKIP,       8,      2,      4,      4),
                (LogPass.EVENT_SEEK_LR,    1424,   None,   None,   None),
                (LogPass.EVENT_SKIP,       38,     3,      0,      0),
                (LogPass.EVENT_READ,       4,      3,      1,      1),
                (LogPass.EVENT_SKIP,       16,     3,      2,      2),
                (LogPass.EVENT_READ,       2,      3,      3,      3),
                (LogPass.EVENT_SKIP,       46,     4,      4,      0),
                (LogPass.EVENT_READ,       4,      4,      1,      1),
                (LogPass.EVENT_SKIP,       16,     4,      2,      2),
                (LogPass.EVENT_READ,       2,      4,      3,      3),
                (LogPass.EVENT_SKIP,       8,      4,      4,      4),
            ],
            myEvts,
        )
        #print(myDict)
        self.assertEqual(myDict[LogPass.EVENT_SEEK_LR], 2)
        self.assertEqual(myDict[LogPass.EVENT_READ], 10)
        self.assertEqual(myDict[LogPass.EVENT_SKIP], 12)
        self.assertEqual(myDict[LogPass.EVENT_EXTRAPOLATE], 0)

#    def test_20(self):
#        """TestLogPass_DownDirect.test_20(): X axis information."""
#        print()
#        print('xAxisFirstVal', self._lp.xAxisFirstVal)
#        print('xAxisLastVal', self._lp.xAxisLastVal)
#        print('xAxisSpacing', self._lp.xAxisSpacing)
#        print('xAxisUnits', self._lp.xAxisUnits)
#        print('totalFrames', self._lp.totalFrames)
#        print('xAxisFirstValOptical', self._lp.xAxisFirstValOptical)
#        print('xAxisLastValOptical', self._lp.xAxisLastValOptical)
#        print('xAxisSpacingOptical', self._lp.xAxisSpacingOptical)
#        print('xAxisUnitsOptical', self._lp.xAxisUnitsOptical)
        
    def test_30(self):
        """TestLogPass_DownDirect.test_30(): X axis to frame number, native units."""
        # 6 logical records, 8 frames/record (272 bytes each)
        # 48 frames
        # Note: Down log
        #Add: 1152 272 1000.0
        #Add: 1424 272 1004.0
        #Add: 1696 272 1008.0
        #Add: 1968 272 1012.0
        #Add: 2240 272 1016.0
        #Add: 2512 272 1020.0
        self.assertEqual(48, self._lp.totalFrames)
        self.assertEqual(0, self._lp.frameFromX(EngVal.EngVal(1000.0, b'FEET')))
        self.assertEqual(1, self._lp.frameFromX(EngVal.EngVal(1000.5, b'FEET')))
        self.assertEqual(8, self._lp.frameFromX(EngVal.EngVal(1004.0, b'FEET')))
        self.assertEqual(40, self._lp.frameFromX(EngVal.EngVal(1020.0, b'FEET')))
        self.assertEqual(47, self._lp.frameFromX(EngVal.EngVal(1023.5, b'FEET')))

    def test_31(self):
        """TestLogPass_DownDirect.test_31(): X axis to frame number, converted units."""
        self.assertEqual(48, self._lp.totalFrames)
        self.assertEqual(0, self._lp.frameFromX(EngVal.EngVal(12*1000.0, b'INCH')))
        self.assertEqual(1, self._lp.frameFromX(EngVal.EngVal(12*1000.5, b'INCH')))
        self.assertEqual(8, self._lp.frameFromX(EngVal.EngVal(12*1004.0, b'INCH')))
        self.assertEqual(40, self._lp.frameFromX(EngVal.EngVal(12*1020.0, b'INCH')))
        self.assertEqual(47, self._lp.frameFromX(EngVal.EngVal(12*1023.5, b'INCH')))

    def test_32(self):
        """TestLogPass_DownDirect.test_32(): X axis to frame number out of range."""
        self.assertEqual(48, self._lp.totalFrames)
        self.assertRaises(LogPass.ExceptionLogPass, self._lp.frameFromX, EngVal.EngVal(999.5, b'FEET'))
        self.assertRaises(LogPass.ExceptionLogPass, self._lp.frameFromX, EngVal.EngVal(1024.0, b'FEET'))

    def test_33(self):
        """TestLogPass_DownDirect.test_33(): X axis to frame number, floor() match."""
        self.assertEqual(48, self._lp.totalFrames)
        self.assertEqual(0, self._lp.frameFromX(EngVal.EngVal(1000.0, b'FEET')))
        self.assertEqual(0, self._lp.frameFromX(EngVal.EngVal(1000.25, b'FEET')))
        self.assertEqual(1, self._lp.frameFromX(EngVal.EngVal(1000.5, b'FEET')))
        self.assertEqual(1, self._lp.frameFromX(EngVal.EngVal(1000.75, b'FEET')))
        self.assertEqual(47, self._lp.frameFromX(EngVal.EngVal(1023.5, b'FEET')))
        self.assertEqual(47, self._lp.frameFromX(EngVal.EngVal(1023.75, b'FEET')))
        self.assertEqual(47, self._lp.frameFromX(EngVal.EngVal(1023.999, b'FEET')))

class TestLogPass_Events_UpIndirect(TestLogPassEventBase):
    """Tests LogPass"""
    def setUp(self):
        """Set up."""
        myF = self._retFileSinglePr(
            # LRH for DFSR
            bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 8, frame spacing value
            + bytes([8, 4, 73, 0, 0, 0, 60])
            # EB 9, frame spacing units
            + bytes([9, 4, 65,]) + b'.1IN'
            # EB 13, mode 1 (indirect)
            + bytes([13, 1, 66, 1])
            # EB 14, x-axis units
            + bytes([14, 4, 65,]) + b'.1IN'
            # EB 15, x-axis rep code
            + bytes([15, 1, 66, 73])
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
            # 2 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 2]) + b'000' + b'\x01'+ bytes([79,]) + bytes([0, 1, 2, 3, 4])
            # Sensor 4
            # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
            + b'BS  ' + b'ServID' + b'ServOrdN'+ b'MM  ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 8 LIS bytes     Pad      2 super  Rep code     Process indicators
            + bytes([0, 8]) + b'000' + b'\x02'+ bytes([73,]) + bytes([0, 1, 2, 3, 4])
        )
        myDfsr = LogiRec.LrDFSRRead(myF)
        self._lp = LogPass.LogPass(myDfsr, 'FileID')
        # 6 logical records, 8 frames/record (272 bytes each) + 4 bytes for indirect depth
        # 48 frames
        #Add: 1152 276 1000.0
        #Add: 1428 276 996.0
        #Add: 1704 276 992.0
        #Add: 1980 276 988.0
        #Add: 2256 276 984.0
        #Add: 2532 276 980.0
        #print()
        self._tellLrS = []
        self._lrSize = 4+34*8
        for lIdx in range(6):
            # 128 bytes of padding |-| logical records
            tellLr = 1024+128+lIdx*(4+34*8)
            self._tellLrS.append(tellLr)
            x = 120*1000.0 - 120*0.5*8*lIdx
            #print('Add:', tellLr, self._lrSize, x)
            self._lp.addType01Data(tellLr, 0, self._lrSize, x)

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestLogPass_Events_UpIndirect: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestLogPass_Events_UpIndirect.test_00(): Construction."""
        self.assertEqual(len(self._lp._dfsr.dsbBlocks), 5)
        self.assertEqual(self._lp._dfsr.frameSize(), 34)

    def test_01(self):
        """TestLogPass_Events_UpIndirect.test_01(): Iterate, all channels, first LR only, two frames."""
        myFrames = slice(2,4,1)
        myChannels = list(range(5))
        myEvts, myDict = self._genEvents(self._tellLrS, self._lrSize, myFrames, myChannels, 5)
        #print()
        #pprint.pprint(myEvts)
        self.assertEqual(
            [
                # First Logical record
                (LogPass.EVENT_SEEK_LR,         1152,   None,   None,   None),
                (LogPass.EVENT_READ,            4,      0,      None,   None),
                # Skip two frames
                (LogPass.EVENT_SKIP,            68,     0,      None,   0),
                (LogPass.EVENT_EXTRAPOLATE,     2,      0,      None,   None),
                # Read all first frame, i.e. number 2 in the LR
                (LogPass.EVENT_READ,            34,     0,      0,      4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      1,      None,   None),
                # Read all second frame, i.e. number 3 in the LR
                (LogPass.EVENT_READ,            34,     1,      0,      4),
            ],
            myEvts
        )
        #print(myDict)
        self.assertEqual(myDict[LogPass.EVENT_SEEK_LR], 1)
        self.assertEqual(myDict[LogPass.EVENT_READ], 3)
        self.assertEqual(myDict[LogPass.EVENT_SKIP], 1)
        self.assertEqual(myDict[LogPass.EVENT_EXTRAPOLATE], 2)

    def test_10(self):
        """TestLogPass_Events_UpIndirect.test_10(): Iterate, all channels, first LR only."""
        #print()
        myFrames = slice(8)
        myChannels = list(range(5))
        myEvts, myDict = self._genEvents(self._tellLrS, self._lrSize, myFrames, myChannels, 5)
        #print()
        #pprint.pprint(myEvts)
        self.assertEqual(
            [
                # First Logical record
                (LogPass.EVENT_SEEK_LR,         1152,   None,   None,   None),
                (LogPass.EVENT_READ,            38,     0,      None,   4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      1,      None,   None),
                (LogPass.EVENT_READ,            34,     1,      0,      4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      2,      None,   None),
                (LogPass.EVENT_READ,            34,     2,      0,      4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      3,      None,   None),
                (LogPass.EVENT_READ,            34,     3,      0,      4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      4,      None,   None),
                (LogPass.EVENT_READ,            34,     4,      0,      4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      5,      None,   None),
                (LogPass.EVENT_READ,            34,     5,      0,      4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      6,      None,   None),
                (LogPass.EVENT_READ,            34,     6,      0,      4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      7,      None,   None),
                (LogPass.EVENT_READ,            34,     7,      0,      4),
            ],
            
            myEvts
        )
        #print(myDict)
        self.assertEqual(myDict[LogPass.EVENT_SEEK_LR], 1)
        self.assertEqual(myDict[LogPass.EVENT_READ], 8)
        self.assertEqual(myDict[LogPass.EVENT_SKIP], 0)
        self.assertEqual(myDict[LogPass.EVENT_EXTRAPOLATE], 7)

    def test_11(self):
        """TestLogPass_Events_UpIndirect.test_11(): Iterate, all channels, first and second LR, frames=range(0,12,1)."""
        myFrames = slice(12)
        myChannels = list(range(5))
        myEvts, myDict = self._genEvents(self._tellLrS, self._lrSize, myFrames, myChannels, 5)
        #print()
        #pprint.pprint(myEvts)
        self.assertEqual(
            [
                # First Logical record
                (LogPass.EVENT_SEEK_LR,         1152,   None,   None,   None),
                (LogPass.EVENT_READ,            38,     0,      None,   4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      1,      None,   None),
                (LogPass.EVENT_READ,            34,     1,      0,      4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      2,      None,   None),
                (LogPass.EVENT_READ,            34,     2,      0,      4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      3,      None,   None),
                (LogPass.EVENT_READ,            34,     3,      0,      4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      4,      None,   None),
                (LogPass.EVENT_READ,            34,     4,      0,      4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      5,      None,   None),
                (LogPass.EVENT_READ,            34,     5,      0,      4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      6,      None,   None),
                (LogPass.EVENT_READ,            34,     6,      0,      4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      7,      None,   None),
                (LogPass.EVENT_READ,            34,     7,      0,      4),
                (LogPass.EVENT_SEEK_LR,         1428,   None,   None,   None),
                (LogPass.EVENT_READ,            38,     8,      None,   4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      9,      None,   None),
                (LogPass.EVENT_READ,            34,     9,      0,      4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      10,      None,   None),
                (LogPass.EVENT_READ,            34,     10,      0,      4),
                (LogPass.EVENT_EXTRAPOLATE,     1,      11,      None,   None),
                (LogPass.EVENT_READ,            34,     11,      0,      4),
            ],
            myEvts
        )
        #print(myDict)
        self.assertEqual(myDict[LogPass.EVENT_SEEK_LR], 2)
        self.assertEqual(myDict[LogPass.EVENT_READ], 12)
        self.assertEqual(myDict[LogPass.EVENT_SKIP], 0)
        self.assertEqual(myDict[LogPass.EVENT_EXTRAPOLATE], 10)

    def test_12(self):
        """TestLogPass_Events_UpIndirect.test_12(): Iterate, channels [1,3], first and second LR, frames=range(8,20,2)."""
        myFrames = slice(8, 20, 2)
        myChannels = [1, 3]
        myEvts, myDict = self._genEvents(self._tellLrS, self._lrSize, myFrames, myChannels, 5)
        #print()
        #pprint.pprint(myEvts)
        self.assertEqual(
            [
                # Event                        Size    Frame    chFrom  chTo
                (LogPass.EVENT_SEEK_LR,         1428,   None,   None,   None),
                (LogPass.EVENT_READ,            4,      0,      None,   None),
                (LogPass.EVENT_SKIP,            4,      0,      0,      0),
                (LogPass.EVENT_READ,            4,      0,      1,      1),
                (LogPass.EVENT_SKIP,            16,     0,      2,      2),
                (LogPass.EVENT_READ,            2,      0,      3,      3),
                (LogPass.EVENT_SKIP,            46,     1,      4,      0),
                (LogPass.EVENT_EXTRAPOLATE,     2,      1,      None,   None),
                (LogPass.EVENT_READ,            4,      1,      1,      1),
                (LogPass.EVENT_SKIP,            16,     1,      2,      2),
                (LogPass.EVENT_READ,            2,      1,      3,      3),
                (LogPass.EVENT_SKIP,            46,     2,      4,      0),
                (LogPass.EVENT_EXTRAPOLATE,     2,      2,      None,   None),
                (LogPass.EVENT_READ,            4,      2,      1,      1),
                (LogPass.EVENT_SKIP,            16,     2,      2,      2),
                (LogPass.EVENT_READ,            2,      2,      3,      3),
                (LogPass.EVENT_SKIP,            46,     3,      4,      0),
                (LogPass.EVENT_EXTRAPOLATE,     2,      3,      None,   None),
                (LogPass.EVENT_READ,            4,      3,      1,      1),
                (LogPass.EVENT_SKIP,            16,     3,      2,      2),
                (LogPass.EVENT_READ,            2,      3,      3,      3),
                (LogPass.EVENT_SKIP,            8,      3,      4,      4),
                (LogPass.EVENT_SEEK_LR,         1704,   None,   None,   None),
                (LogPass.EVENT_READ,            4,      4,      None,   None),
                (LogPass.EVENT_SKIP,            4,      4,      0,      0),
                (LogPass.EVENT_READ,            4,      4,      1,      1),
                (LogPass.EVENT_SKIP,            16,     4,      2,      2),
                (LogPass.EVENT_READ,            2,      4,      3,      3),
                (LogPass.EVENT_SKIP,            46,     5,      4,      0),
                (LogPass.EVENT_EXTRAPOLATE,     2,      5,      None,   None),
                (LogPass.EVENT_READ,            4,      5,      1,      1),
                (LogPass.EVENT_SKIP,            16,     5,      2,      2),
                (LogPass.EVENT_READ,            2,      5,      3,      3),
                (LogPass.EVENT_SKIP,            8,      5,      4,      4),
            ],
            myEvts,
        )
        #print(myDict)
        self.assertEqual(myDict[LogPass.EVENT_SEEK_LR], 2)
        self.assertEqual(myDict[LogPass.EVENT_READ], 14)
        self.assertEqual(myDict[LogPass.EVENT_SKIP], 14)
        self.assertEqual(myDict[LogPass.EVENT_EXTRAPOLATE], 4)

    def test_20(self):
        """TestLogPass_Events_UpIndirect.test_20(): X axis information."""
        #print()
        #print('xAxisFirstVal', self._lp.xAxisFirstVal)
        #print('xAxisLastVal', self._lp.xAxisLastVal)
        #print('xAxisSpacing', self._lp.xAxisSpacing)
        #print('xAxisUnits', self._lp.xAxisUnits)
        #print('totalFrames', self._lp.totalFrames)
        #print('xAxisFirstValOptical', self._lp.xAxisFirstValOptical)
        #print('xAxisLastValOptical', self._lp.xAxisLastValOptical)
        #print('xAxisSpacingOptical', self._lp.xAxisSpacingOptical)
        #print('xAxisUnitsOptical', self._lp.xAxisUnitsOptical)
        #
        self.assertEqual(120*1000.0, self._lp.xAxisFirstVal)
        self.assertEqual(120*976.5, self._lp.xAxisLastVal)
        self.assertEqual(-60.0, self._lp.xAxisSpacing)
        self.assertEqual(b'.1IN', self._lp.xAxisUnits)
        self.assertEqual(48, self._lp.totalFrames)
        self.assertEqual(1000.0, self._lp.xAxisFirstValOptical)
        self.assertEqual(976.5, self._lp.xAxisLastValOptical)
        self.assertEqual(-0.5, self._lp.xAxisSpacingOptical)
        self.assertEqual(b'FEET', self._lp.xAxisUnitsOptical)

class TestLogPass_UpDirect_Dipmeter(BaseTestClasses.TestBaseLogPass):
    """Tests LogPass"""
    def setUp(self):
        """Set up."""
        myDfsrBy = (
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
                + b'DEPT' + b'ServID' + b'ServOrdN'+ b'IN  ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
                # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
                + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
                # Sensor 1
                # Mnemonic  Service ID  Serv ord No    Units     API 45,310,01,1       File No: 256
                + b'RHDT' + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
                # 4 LIS bytes      Pad      1 super  Rep code     Process indicators
                + bytes([0, 90]) + b'000' + b'\x01'+ bytes([234,]) + bytes([0, 1, 2, 3, 4])
        )
        #print('\nmyDfsrBy', myDfsrBy)
        myPrBy = self.retPrS(myDfsrBy)
        # 10000 feet in inches
        depth = 10000 * 12
        val = 0
        for l in range(12):
            # LR header
            lrBytes = bytearray(bytes([0, 0]))
            #print('lrBytes', lrBytes)
            for f in range(8):
                # Direct depth
                lrBytes.extend(RepCode.writeBytes(depth, 68))
                for ch in range(RepCode.DIPMETER_LIS_SIZE_234):
                    lrBytes.extend(RepCode.writeBytes(val % 256, 66))
                    val += 1
                # Frame spacing 3.0 inches
                depth -= 3.0
            myPrBy.extend(self.retPrS(lrBytes))
        #print('\nmyPrBy', myPrBy)
        self._file = self._retFileFromBytes(myPrBy)
        # Now read DFSR from the file
        self._lp = LogPass.LogPass(LogiRec.LrDFSRRead(self._file), self._file.fileId)
        self._file.skipToNextLr()
        # Check DFSR
        self.assertEqual(len(self._lp.dfsr.dsbBlocks), 2)
        self.assertEqual(self._lp.dfsr.frameSize(), 94)
        # Test log pass is empty and any attempt to setFrameSet() raises
        # as we have made no calls to addType01Data()
        self.assertEqual(0, self._lp.totalFrames)
        self.assertRaises(LogPass.ExceptionLogPass, self._lp.setFrameSet, self._file, None, None)
        # Now load the type 0/1 data
        while not self._file.isEOF:
            tell = self._file.tellLr()
            # LRH
            lrType, lrAttr = self._file.readLrBytes(2)
            skip = 0
            myRm = self._lp.dfsr.ebs.recordingMode
            if myRm:
                # Indirect X
                myXrc = self._lp.dfsr.ebs.depthRepCode
                self.fail('Ooops, should be direct X axis.')
            else:
                # Select Rep Code from the 0th channel
                myXrc = self._lp.dfsr.dsbBlocks[0].repCode
            #if myRm == 0 and self._xAxisIndex != 0:
            #    # Have to skip before reading X axis
            #    skip += theF.skipLrBytes(self._lp.type01Plan.chOffset(frame=0, ch=self._xAxisIndex))
            myLisSize = RepCode.lisSize(myXrc)
            myXval = RepCode.readBytes(myXrc, self._file.readLrBytes(myLisSize))
            #print('myXval', myXval)
            skip += myLisSize
            skip += self._file.skipToNextLr()
            self._lp.addType01Data(tell, lrType, skip, myXval)
        self._file.rewind()

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestLogPass_UpDirect_Dipmeter: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestLogPass_UpDirect_Dipmeter.test_00(): DEPT and 234 Dipmeter, X axis data."""
        #self._lp.setFrameSet(self._file, theFrSl=None, theChList=None)
#        print()
#        print('xAxisFirstVal', self._lp.xAxisFirstVal)
#        print('xAxisLastVal', self._lp.xAxisLastVal)
#        print('xAxisSpacing', self._lp.xAxisSpacing)
#        print('xAxisUnits', self._lp.xAxisUnits)
#        print('totalFrames', self._lp.totalFrames)
#        print('xAxisFirstValOptical', self._lp.xAxisFirstValOptical)
#        print('xAxisLastValOptical', self._lp.xAxisLastValOptical)
#        print('xAxisSpacingOptical', self._lp.xAxisSpacingOptical)
#        print('xAxisUnitsOptical', self._lp.xAxisUnitsOptical)
        self.assertEqual(12*10000.0, self._lp.xAxisFirstVal)
        self.assertEqual(119715.0, self._lp.xAxisLastVal)
        self.assertEqual(-3.0, self._lp.xAxisSpacing)
        self.assertEqual(b'IN  ', self._lp.xAxisUnits)
        self.assertEqual(96, self._lp.totalFrames)
        self.assertEqual(10000.0, self._lp.xAxisFirstValOptical)
        self.assertEqual(9976.25, self._lp.xAxisLastValOptical)
        #self.assertEqual(-0.25, self._lp.xAxisSpacingOptical)
        self.assertAlmostEqual(-0.25, self._lp.xAxisSpacingOptical)
        self.assertEqual(b'FEET', self._lp.xAxisUnitsOptical)

    def test_01(self):
        """TestLogPass_UpDirect_Dipmeter.test_01(): DEPT and 234 Dipmeter, setFrameSet()."""
        self._lp.setFrameSet(self._file, theFrSl=None, theChList=None)
        #print()
        #print(self._lp.frameSet)
        self.assertEqual(96, self._lp.frameSet.numFrames)
        self.assertEqual(91, self._lp.frameSet.valuesPerFrame)

    def test_10(self):
        """TestLogPass_UpDirect_Dipmeter.test_10(): DEPT and 234 Dipmeter, genFrameSetHeadings() fails."""
        # genFrameSetHeadings should raise as we have no FrameSet yet
        try:
            list(self._lp.genFrameSetHeadings())
            self.fail('LogPass.ExceptionLogPassNoFrameSet not raised')
        except LogPass.ExceptionLogPassNoFrameSet:
            pass

    def test_11(self):
        """TestLogPass_UpDirect_Dipmeter.test_11(): DEPT and 234 Dipmeter, genFrameSetHeadings()."""
        self._lp.setFrameSet(self._file, theFrSl=None, theChList=None)
        expHdgS = [
            (b'DEPT', b'IN  '),
            ("b'FC0 ' (0, 0)", b'    '),
            ("b'FC1 ' (0, 0)", b'    '),
            ("b'FC2 ' (0, 0)", b'    '),
            ("b'FC3 ' (0, 0)", b'    '),
            ("b'FC4 ' (0, 0)", b'    '),
            ("b'FC0 ' (1, 0)", b'    '),
            ("b'FC1 ' (1, 0)", b'    '),
            ("b'FC2 ' (1, 0)", b'    '),
            ("b'FC3 ' (1, 0)", b'    '),
            ("b'FC4 ' (1, 0)", b'    '),
            ("b'FC0 ' (2, 0)", b'    '),
            ("b'FC1 ' (2, 0)", b'    '),
            ("b'FC2 ' (2, 0)", b'    '),
            ("b'FC3 ' (2, 0)", b'    '),
            ("b'FC4 ' (2, 0)", b'    '),
            ("b'FC0 ' (3, 0)", b'    '),
            ("b'FC1 ' (3, 0)", b'    '),
            ("b'FC2 ' (3, 0)", b'    '),
            ("b'FC3 ' (3, 0)", b'    '),
            ("b'FC4 ' (3, 0)", b'    '),
            ("b'FC0 ' (4, 0)", b'    '),
            ("b'FC1 ' (4, 0)", b'    '),
            ("b'FC2 ' (4, 0)", b'    '),
            ("b'FC3 ' (4, 0)", b'    '),
            ("b'FC4 ' (4, 0)", b'    '),
            ("b'FC0 ' (5, 0)", b'    '),
            ("b'FC1 ' (5, 0)", b'    '),
            ("b'FC2 ' (5, 0)", b'    '),
            ("b'FC3 ' (5, 0)", b'    '),
            ("b'FC4 ' (5, 0)", b'    '),
            ("b'FC0 ' (6, 0)", b'    '),
            ("b'FC1 ' (6, 0)", b'    '),
            ("b'FC2 ' (6, 0)", b'    '),
            ("b'FC3 ' (6, 0)", b'    '),
            ("b'FC4 ' (6, 0)", b'    '),
            ("b'FC0 ' (7, 0)", b'    '),
            ("b'FC1 ' (7, 0)", b'    '),
            ("b'FC2 ' (7, 0)", b'    '),
            ("b'FC3 ' (7, 0)", b'    '),
            ("b'FC4 ' (7, 0)", b'    '),
            ("b'FC0 ' (8, 0)", b'    '),
            ("b'FC1 ' (8, 0)", b'    '),
            ("b'FC2 ' (8, 0)", b'    '),
            ("b'FC3 ' (8, 0)", b'    '),
            ("b'FC4 ' (8, 0)", b'    '),
            ("b'FC0 ' (9, 0)", b'    '),
            ("b'FC1 ' (9, 0)", b'    '),
            ("b'FC2 ' (9, 0)", b'    '),
            ("b'FC3 ' (9, 0)", b'    '),
            ("b'FC4 ' (9, 0)", b'    '),
            ("b'FC0 ' (10, 0)", b'    '),
            ("b'FC1 ' (10, 0)", b'    '),
            ("b'FC2 ' (10, 0)", b'    '),
            ("b'FC3 ' (10, 0)", b'    '),
            ("b'FC4 ' (10, 0)", b'    '),
            ("b'FC0 ' (11, 0)", b'    '),
            ("b'FC1 ' (11, 0)", b'    '),
            ("b'FC2 ' (11, 0)", b'    '),
            ("b'FC3 ' (11, 0)", b'    '),
            ("b'FC4 ' (11, 0)", b'    '),
            ("b'FC0 ' (12, 0)", b'    '),
            ("b'FC1 ' (12, 0)", b'    '),
            ("b'FC2 ' (12, 0)", b'    '),
            ("b'FC3 ' (12, 0)", b'    '),
            ("b'FC4 ' (12, 0)", b'    '),
            ("b'FC0 ' (13, 0)", b'    '),
            ("b'FC1 ' (13, 0)", b'    '),
            ("b'FC2 ' (13, 0)", b'    '),
            ("b'FC3 ' (13, 0)", b'    '),
            ("b'FC4 ' (13, 0)", b'    '),
            ("b'FC0 ' (14, 0)", b'    '),
            ("b'FC1 ' (14, 0)", b'    '),
            ("b'FC2 ' (14, 0)", b'    '),
            ("b'FC3 ' (14, 0)", b'    '),
            ("b'FC4 ' (14, 0)", b'    '),
            ("b'FC0 ' (15, 0)", b'    '),
            ("b'FC1 ' (15, 0)", b'    '),
            ("b'FC2 ' (15, 0)", b'    '),
            ("b'FC3 ' (15, 0)", b'    '),
            ("b'FC4 ' (15, 0)", b'    '),
            ("b'STAT' (0, 0)", b'    '),
            ("b'REF ' (0, 0)", b'    '),
            ("b'REFC' (0, 0)", b'    '),
            ("b'EMEX' (0, 0)", b'    '),
            ("b'PADP' (0, 0)", b'    '),
            ("b'TEMP' (0, 0)", b'    '),
            ("b'FEP1' (0, 0)", b'    '),
            ("b'FEP2' (0, 0)", b'    '),
            ("b'RAC1' (0, 0)", b'    '),
            ("b'RAC2' (0, 0)", b'    '),
        ]
        #print()
        #pprint.pprint(list(self._lp.genFrameSetHeadings()))
        self.assertEqual(expHdgS, list(self._lp.genFrameSetHeadings()))
        
    def test_20(self):
        """TestLogPass_UpDirect_Dipmeter.test_20(): DEPT and 234 Dipmeter, genFrameSetScNameUnit() fails."""
        # genFrameSetHeadings should raise as we have no FrameSet yet
        try:
            list(self._lp.genFrameSetScNameUnit())
            self.fail('LogPass.ExceptionLogPassNoFrameSet not raised')
        except LogPass.ExceptionLogPassNoFrameSet:
            pass

    def test_21(self):
        """TestLogPass_UpDirect_Dipmeter.test_21(): DEPT and 234 Dipmeter, genFrameSetScNameUnit()."""
        self._lp.setFrameSet(self._file, theFrSl=None, theChList=None)
        expHdgS = [
            ('DEPT', 'IN  '),
            ('FC0 ', '    '),
            ('FC1 ', '    '),
            ('FC2 ', '    '),
            ('FC3 ', '    '),
            ('FC4 ', '    '),
            ('STAT', '    '),
            ('REF ', '    '),
            ('REFC', '    '),
            ('EMEX', '    '),
            ('PADP', '    '),
            ('TEMP', '    '),
            ('FEP1', '    '),
            ('FEP2', '    '),
            ('RAC1', '    '),
            ('RAC2', '    '),
        ]
        #print()
        #pprint.pprint(list(self._lp.genFrameSetScNameUnit()))
        self.assertEqual(expHdgS, list(self._lp.genFrameSetScNameUnit()))

    def test_22(self):
        """TestLogPass_UpDirect_Dipmeter.test_22(): DEPT and 234 Dipmeter, genFrameSetScNameUnit(toAscii=False)."""
        self._lp.setFrameSet(self._file, theFrSl=None, theChList=None)
        expHdgS = [
            (b'DEPT', b'IN  '),
            (b'FC0 ', b'    '),
            (b'FC1 ', b'    '),
            (b'FC2 ', b'    '),
            (b'FC3 ', b'    '),
            (b'FC4 ', b'    '),
            (b'STAT', b'    '),
            (b'REF ', b'    '),
            (b'REFC', b'    '),
            (b'EMEX', b'    '),
            (b'PADP', b'    '),
            (b'TEMP', b'    '),
            (b'FEP1', b'    '),
            (b'FEP2', b'    '),
            (b'RAC1', b'    '),
            (b'RAC2', b'    '),
        ]
        #print()
        #pprint.pprint(list(self._lp.genFrameSetScNameUnit()))
        self.assertEqual(expHdgS, list(self._lp.genFrameSetScNameUnit(toAscii=False)))

    def test_23(self):
        """TestLogPass_UpDirect_Dipmeter.test_23(): DEPT and 234 Dipmeter, genFrameSetScNameUnit(toAscii=True)."""
        self._lp.setFrameSet(self._file, theFrSl=None, theChList=None)
        expHdgS = [
            ('DEPT', 'IN  '),
            ('FC0 ', '    '),
            ('FC1 ', '    '),
            ('FC2 ', '    '),
            ('FC3 ', '    '),
            ('FC4 ', '    '),
            ('STAT', '    '),
            ('REF ', '    '),
            ('REFC', '    '),
            ('EMEX', '    '),
            ('PADP', '    '),
            ('TEMP', '    '),
            ('FEP1', '    '),
            ('FEP2', '    '),
            ('RAC1', '    '),
            ('RAC2', '    '),
        ]
        #print()
        #pprint.pprint(list(self._lp.genFrameSetScNameUnit()))
        self.assertEqual(expHdgS, list(self._lp.genFrameSetScNameUnit(toAscii=True)))

    def test_31(self):
        """TestLogPass_UpDirect_Dipmeter.test_21(): DEPT and 234 Dipmeter, genFrameSetScNameUnit()."""
        #self._lp.setFrameSet(self._file, theFrSl=None, theChList=None)
        self.assertEqual(10000.0, self._lp.xAxisFirstValOptical)
        self.assertEqual(9976.25, self._lp.xAxisLastValOptical)
        self.assertAlmostEqual(-0.25, self._lp.xAxisSpacingOptical)
        myXstart = EngVal.EngVal(9999.0, b'FEET')
        myXstop = EngVal.EngVal(9980.0, b'FEET')
        self._lp.setFrameSetChX(self._file, theChS=None, Xstart=myXstart, Xstop=myXstop, frStep=3)
        #print()
        #print(self._lp.frameSet)
        # X = 9999.0 - 9980.0 == 19 feet
        # 19 feet / 0.25 == 76
        # 76 / 3 == 25.3333
        # Round up to 26
        numFrames = int(1 + ((9999.0 - 9980.0) / (3 * 0.25)))
        self.assertEqual(numFrames, self._lp.frameSet.numFrames)
        self.assertEqual(91, self._lp.frameSet.valuesPerFrame)

class TestLogPass_UpIndirect(BaseTestClasses.TestBaseLogPass):
    """Tests LogPass"""
    def setUp(self):
        """Set up. 3 LRs, 5 frames, 4 channels"""
        shape = (3, 5, 4)
        myPrS = [self._retSinglePr(self._retDFSRBytesIndirect(ch=shape[2], sa=1, bu=1))]
        # 1000 feet at .1 inch
        depth = 1000 * 12 * 10
        val = 0.0
        for l in range(shape[0]):
            # LR header
            lrBytes = bytearray(bytes([0, 0]))
            # Indirect depth
            lrBytes.extend(RepCode.writeBytes(depth, 73))
            #print('lrBytes', lrBytes)
            for f in range(shape[1]):
                for ch in range(shape[2]):
                    lrBytes.extend(RepCode.writeBytes(val, 68))
                    val += 1.0
                depth -= 60
            myPrS.append(self._retSinglePr(lrBytes))
        self._file = self._retFileFromBytes(b''.join(myPrS))
        # Now read the file
        self._logPass = LogPass.LogPass(LogiRec.LrDFSRRead(self._file), self._file.fileId)
        self._file.skipToNextLr()
        # Test log pass is empty and any attempt to setFrameSet() raises as no
        # addType01Data() called
        self.assertEqual(0, self._logPass.totalFrames)
        self.assertRaises(LogPass.ExceptionLogPass, self._logPass.setFrameSet, self._file, None, None)
        # Now load the type 0/1 data
        while not self._file.isEOF:
            tell = self._file.tellLr()
            # LRH
            lrType, lrAttr = self._file.readLrBytes(2)
            skip = 0
            myRm = self._logPass.dfsr.ebs.recordingMode
            if myRm:
                # Indirect X
                myXrc = self._logPass.dfsr.ebs.depthRepCode
            else:
                # Select Rep Code from the channel
                myXrc = self._logPass.dfsr.dsbBlocks[self._xAxisIndex].repCode
            #if myRm == 0 and self._xAxisIndex != 0:
            #    # Have to skip before reading X axis
            #    skip += theF.skipLrBytes(self._logPass.type01Plan.chOffset(frame=0, ch=self._xAxisIndex))
            myLisSize = RepCode.lisSize(myXrc)
            myXval = RepCode.readBytes(myXrc, self._file.readLrBytes(myLisSize))
            #print('myXval', myXval)
            skip += myLisSize
            skip += self._file.skipToNextLr()
            self._logPass.addType01Data(tell, lrType, skip, myXval)
        self._file.rewind()

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestLogPass_UpIndirect: Tests setUp() and tearDown()."""
        pass
        #print()
        #print(self._logPass)
    
    def test_00(self):
        """TestLogPass_UpIndirect.test_00(): 3 LR, 5 fr, 4 ch. setFrameSet() All."""
        #print(self._logPass._retFrameSetMap(None).keys())
        self._logPass.setFrameSet(self._file, theFrSl=None, theChList=None)
        #print()
        #print(self._logPass)
        #print(self._logPass.frameSet.longStr())
        #pprint.pprint(self._logPass.frameSet._frames)
        #pprint.pprint(self._logPass.frameSet._indrXVector)
        expVal = numpy.array(
            [
                [  0.,   1.,   2.,   3.],
                [  4.,   5.,   6.,   7.],
                [  8.,   9.,  10.,  11.],
                [ 12.,  13.,  14.,  15.],
                [ 16.,  17.,  18.,  19.],
                [ 20.,  21.,  22.,  23.],
                [ 24.,  25.,  26.,  27.],
                [ 28.,  29.,  30.,  31.],
                [ 32.,  33.,  34.,  35.],
                [ 36.,  37.,  38.,  39.],
                [ 40.,  41.,  42.,  43.],
                [ 44.,  45.,  46.,  47.],
                [ 48.,  49.,  50.,  51.],
                [ 52.,  53.,  54.,  55.],
                [ 56.,  57.,  58.,  59.],
            ]
        )
        self.assertTrue((expVal == self._logPass.frameSet._frames).all())
        expVal = numpy.array(
            [
                120000.,  119940.,  119880.,  119820.,  119760.,  119700.,
                119640.,  119580.,  119520.,  119460.,  119400.,  119340.,
                119280.,  119220.,  119160.,
            ]
        )
        self.assertTrue((expVal == self._logPass.frameSet._indrXVector).all())

    def test_01(self):
        """TestLogPass_UpIndirect.test_01(): 3 LR, 5 fr, 4 ch. setFrameSet() theFrSl=slice(0,16,2)."""
        #print()
        myFrameSlice = slice(0,16,2)
        myChList = None
        #pprint.pprint(self._logPass._retFrameSetMap(myFrameSlice))
        self._logPass.setFrameSet(self._file, theFrSl=myFrameSlice, theChList=myChList)
        #print(self._logPass)
        #print(self._logPass.frameSet.longStr())
        #pprint.pprint(self._logPass.frameSet._frames)
        #pprint.pprint(self._logPass.frameSet._indrXVector)
        expVal = numpy.array(
            [
                [  0.,   1.,   2.,   3.],
                [  8.,   9.,  10.,  11.],
                [ 16.,  17.,  18.,  19.],
                [ 24.,  25.,  26.,  27.],
                [ 32.,  33.,  34.,  35.],
                [ 40.,  41.,  42.,  43.],
                [ 48.,  49.,  50.,  51.],
                [ 56.,  57.,  58.,  59.],
            ]
        )
        self.assertTrue((expVal == self._logPass.frameSet._frames).all())
        expVal = numpy.array(
            [ 120000.,  119880.,  119760.,  119700.,  119580.,  119400.,
                119280.,  119160.]
        )
        self.assertTrue((expVal == self._logPass.frameSet._indrXVector).all())

    def test_02(self):
        """TestLogPass_UpIndirect.test_02(): 3 LR, 5 fr, 4 ch. setFrameSet() theFrSl=slice(2,4,2)."""
        #print()
        myFrameSlice = slice(2,4,2)
        myChList = None
        #pprint.pprint(self._logPass._retFrameSetMap(myFrameSlice))
        self._logPass.setFrameSet(self._file, theFrSl=myFrameSlice, theChList=myChList)
        #print(self._logPass)
        #print(self._logPass.frameSet.longStr())
        #pprint.pprint(self._logPass.frameSet._frames)
        #pprint.pprint(self._logPass.frameSet._indrXVector)
        expVal = numpy.array(
            [
                [  8.,   9.,  10.,  11.],
            ]
        )
        self.assertTrue((expVal == self._logPass.frameSet._frames).all())
        expVal = numpy.array(
            [ 119880., ]
        )
        self.assertTrue((expVal == self._logPass.frameSet._indrXVector).all())

    def test_03(self):
        """TestLogPass_UpIndirect.test_03(): 3 LR, 5 fr, 4 ch. setFrameSet() theFrSl=slice(1,5,2)."""
        #print()
        myFrameSlice = slice(1,5,2)
        myChList = None
        #pprint.pprint(self._logPass._retFrameSetMap(myFrameSlice))
        self._logPass.setFrameSet(self._file, theFrSl=myFrameSlice, theChList=myChList)
        #print(self._logPass)
        #print(self._logPass.frameSet.longStr())
        #pprint.pprint(self._logPass.frameSet._frames)
        #pprint.pprint(self._logPass.frameSet._indrXVector)
        expVal = numpy.array(
            [
                [  4.,   5.,   6.,   7.],
                [ 12.,  13.,  14.,  15.],
            ]
        )
        self.assertTrue((expVal == self._logPass.frameSet._frames).all())
        expVal = numpy.array(
            [
                119940.,  119820.,
            ]
        )
        self.assertTrue((expVal == self._logPass.frameSet._indrXVector).all())

    def test_10(self):
        """TestLogPass_UpIndirect.test_10(): genFrameSetHeadings()"""
        self._logPass.setFrameSet(self._file, theFrSl=None, theChList=None)
        #print()
        #print(list(self._logPass.genFrameSetHeadings()))
        self.assertEqual(
            [
                (b'0000', b'    '),
                (b'0001', b'    '),
                (b'0002', b'    '),
                (b'0003', b'    '),
            ],
            list(self._logPass.genFrameSetHeadings())
        )


@pytest.mark.slow
class TestLogPass_PerfBase(BaseTestClasses.TestBaseFile):
    """Tests LogPass performance."""

    def _loadLogPass(self, num):
        """Loads logical record positions and returns file size."""
        myFramesPerRecord = 8
        self._lrSize = myFramesPerRecord*(4+8*1024)
        numFrames = 0
        for lIdx in range(num):
            # 128 bytes of padding |-| logical records
            tellLr = 1024+128+lIdx*self._lrSize
            x = 30e3 - 0.5 * myFramesPerRecord * lIdx
            #print('Add:', tellLr, self._lrSize, x)
            self._lp.addType01Data(tellLr, 0, self._lrSize, x)
            numFrames += myFramesPerRecord
        return tellLr + self._lrSize, numFrames

    def _runIterTestAllFrames(self, num, theChannels):
        """Time iterate all frames, given channels."""
        mySize, myNumFrames = self._loadLogPass(num)
        myReadSize = 0
        numEvents = 0
        start = time.perf_counter()
        for evt in self._lp._genFrameSetEvents(slice(myNumFrames), theChannels):
            numEvents += 1
            if evt[0] == 'read':
                myReadSize += evt[1]
        self.writeCostToStderr(start, myReadSize, 'Events', numEvents)

    def _runIterTestSomeFrames(self, num, theFrSl, theChannels):
        """Time iterate all frames, given channels."""
        mySize, myNumFrames = self._loadLogPass(num)
        myReadSize = 0
        numEvents = 0
        start = time.perf_counter()
        for evt in self._lp._genFrameSetEvents(theFrSl, theChannels):
            numEvents += 1
            if evt[0] == 'read':
                myReadSize += evt[1]
        self.writeCostToStderr(start, myReadSize, 'Events', numEvents)
        
    def setUp(self):
        """Set up."""
        # LRH for DFSR
        myB = (bytes([64, 0])
#            # EB 4, up/down value 0 (down)
#            + bytes([4, 1, 66, 0])
#            # EB 12, absent value -153.0
#            + bytes([12, 4, 68])+b'\xbb\xb3\x80\x00'
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        for i in range(1024):
            myName = bytes('{:04d}'.format(i), 'ascii')
            # Sensor i
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            myB += (myName + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 8 LIS bytes     Pad      2 super  Rep code     Process indicators
            + bytes([0, 8]) + b'000' + b'\x02'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            )
        myF = self._retFileSinglePr(myB)
        myDfsr = LogiRec.LrDFSRRead(myF)
        #print('len(myB)', len(myB), 'Frame length:', myDfsr.lisSize())
        self._lp = LogPass.LogPass(myDfsr)


@pytest.mark.slow
class TestLogPass_Perf(TestLogPass_PerfBase):
    """Tests LogPass performance."""

    def setUp(self):
        """Set up."""
        # LRH for DFSR
        myB = (bytes([64, 0])
#            # EB 4, up/down value 0 (down)
#            + bytes([4, 1, 66, 0])
#            # EB 12, absent value -153.0
#            + bytes([12, 4, 68])+b'\xbb\xb3\x80\x00'
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        for i in range(1024):
            myName = bytes('{:04d}'.format(i), 'ascii')
            # Sensor i
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            myB += (myName + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 8 LIS bytes     Pad      2 super  Rep code     Process indicators
            + bytes([0, 8]) + b'000' + b'\x02'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            )
        myF = self._retFileSinglePr(myB)
        myDfsr = LogiRec.LrDFSRRead(myF)
        #print('len(myB)', len(myB), 'Frame length:', myDfsr.lisSize())
        self._lp = LogPass.LogPass(myDfsr, 'FileID')

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestLogPass_Perf: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestLogPass_Perf.test_00(): Construction."""
        self.assertEqual(len(self._lp._dfsr.dsbBlocks), 1025)
        self.assertEqual(self._lp._dfsr.frameSize(), 8196)
        
    def test_01(self):
        """TestLogPass_Perf.test_01(): Load LogPass."""
        num = 100000
        start = time.perf_counter()
        mySize, myFrames = self._loadLogPass(num)
        self.writeCostToStderr(start, mySize, 'Frames', myFrames)
        
    def test_10(self):
        """TestLogPass_Perf.test_10(): Iterate all 8000 frames, channel step 1."""
        self._runIterTestAllFrames(1000, list(range(1025)))

    def test_11(self):
        """TestLogPass_Perf.test_11(): Iterate all 8000 frames, channel step 2."""
        self._runIterTestAllFrames(1000, list(range(0, 1025, 2)))

    def test_12(self):
        """TestLogPass_Perf.test_12(): Iterate all 8000 frames, channel step 4."""
        self._runIterTestAllFrames(1000, list(range(0, 1025, 4)))

    def test_13(self):
        """TestLogPass_Perf.test_13(): Iterate all 8000 frames, channel step 8."""
        self._runIterTestAllFrames(1000, list(range(0, 1025, 8)))

    def test_14(self):
        """TestLogPass_Perf.test_14(): Iterate all 8000 frames, channel step 16."""
        self._runIterTestAllFrames(1000, list(range(0, 1025, 16)))

    def test_15(self):
        """TestLogPass_Perf.test_15(): Iterate all 8000 frames, channel step 32."""
        self._runIterTestAllFrames(1000, list(range(0, 1025, 32)))

    def test_16(self):
        """TestLogPass_Perf.test_16(): Iterate all 8000 frames, channel step 64."""
        self._runIterTestAllFrames(1000, list(range(0, 1025, 64)))

    def test_17(self):
        """TestLogPass_Perf.test_17(): Iterate all 8000 frames, channel step 128."""
        self._runIterTestAllFrames(1000, list(range(0, 1025, 128)))

    def test_18(self):
        """TestLogPass_Perf.test_18(): Iterate all 8000 frames, channel step 256."""
        self._runIterTestAllFrames(1000, list(range(0, 1025, 256)))

    def test_19(self):
        """TestLogPass_Perf.test_19(): Iterate all 8000 frames, channel step 512."""
        self._runIterTestAllFrames(1000, list(range(0, 1025, 512)))

    def test_20(self):
        """TestLogPass_Perf.test_20(): Iterate all 8000 frames, channel step 1024."""
        self._runIterTestAllFrames(1000, list(range(0, 1025, 1024)))

    def test_21(self):
        """TestLogPass_Perf.test_21(): Iterate all 8000 frames, single channel  ."""
        self._runIterTestAllFrames(1000, [0,])

    def test_30(self):
        """TestLogPass_Perf.test_30(): channel step 1, 8000 frames step 1."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 1), list(range(0, 1025, 1)))

    def test_31(self):
        """TestLogPass_Perf.test_31(): channel step 1, 8000 frames step 2."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 2), list(range(0, 1025, 1)))

    def test_32(self):
        """TestLogPass_Perf.test_32(): channel step 1, 8000 frames step 4."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 4), list(range(0, 1025, 1)))

    def test_33(self):
        """TestLogPass_Perf.test_33(): channel step 1, 8000 frames step 8."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 8), list(range(0, 1025, 1)))

    def test_34(self):
        """TestLogPass_Perf.test_34(): channel step 1, 8000 frames step 16."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 16), list(range(0, 1025, 1)))

    def test_35(self):
        """TestLogPass_Perf.test_35(): channel step 1, 8000 frames step 32."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 32), list(range(0, 1025, 1)))

    def test_36(self):
        """TestLogPass_Perf.test_36(): channel step 1, 8000 frames step 64."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 64), list(range(0, 1025, 1)))

    def test_37(self):
        """TestLogPass_Perf.test_37(): channel step 1, 8000 frames step 128."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 128), list(range(0, 1025, 1)))

    def test_38(self):
        """TestLogPass_Perf.test_38(): channel step 1, 8000 frames step 256."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 256), list(range(0, 1025, 1)))

    def test_39(self):
        """TestLogPass_Perf.test_39(): channel step 1, 8000 frames step 512."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 512), list(range(0, 1025, 1)))

    def test_40(self):
        """TestLogPass_Perf.test_40(): channel step 1, 8000 frames step 1024."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 1024), list(range(0, 1025, 1)))
    
    def test_50(self):
        """TestLogPass_Perf.test_50(): channel step 1, 8000 frames step 1."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 1), list(range(0, 1025, 1)))

    def test_51(self):
        """TestLogPass_Perf.test_51(): channel step 2, 8000 frames step 2."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 2), list(range(0, 1025, 2)))

    def test_52(self):
        """TestLogPass_Perf.test_52(): channel step 4, 8000 frames step 4."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 4), list(range(0, 1025, 4)))

    def test_53(self):
        """TestLogPass_Perf.test_53(): channel step 8, 8000 frames step 8."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 8), list(range(0, 1025, 8)))

    def test_54(self):
        """TestLogPass_Perf.test_54(): channel step 16, 8000 frames step 16."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 16), list(range(0, 1025, 16)))

    def test_55(self):
        """TestLogPass_Perf.test_55(): channel step 32, 8000 frames step 32."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 32), list(range(0, 1025, 32)))

    def test_56(self):
        """TestLogPass_Perf.test_56(): channel step 64, 8000 frames step 64."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 64), list(range(0, 1025, 64)))

    def test_57(self):
        """TestLogPass_Perf.test_57(): channel step 128, 8000 frames step 128."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 128), list(range(0, 1025, 128)))

    def test_58(self):
        """TestLogPass_Perf.test_58(): channel step 256, 8000 frames step 256."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 256), list(range(0, 1025, 256)))

    def test_59(self):
        """TestLogPass_Perf.test_59(): channel step 512, 8000 frames step 512."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 512), list(range(0, 1025, 512)))

    def test_60(self):
        """TestLogPass_Perf.test_60(): channel step 1024, 8000 frames step 1024."""
        self._runIterTestSomeFrames(1000, slice(0, 8000, 1024), list(range(0, 1025, 1024)))


@pytest.mark.slow
class TestLogPass_Type0_Base(BaseTestClasses.TestBaseLogPass):
    """Reading binary data."""
    
    def _createLogPass(self, theF):
        """Given an io.BytesIO complete with a DFSR and LR type 0 of the
        specified number and dimensions, scans it into a LogPass and
        returns the LogPass."""
        # Read, iterate and add to LogPass
        t = theF.tellLr()
        myDfsr = LogiRec.LrDFSRRead(theF)
        s = theF.skipToNextLr()
        myLp = LogPass.LogPass(myDfsr, 'MyFile')
        while not theF.isEOF:
            t = theF.tellLr()
            lrType, lrAttr = theF.readLrBytes(2)
            s = theF.skipToNextLr()
            myLp.addType01Data(t, lrType, s, 1.0)
        return myLp

    def _createFileLogPass(self, numLr, frPerLr, numCh, numSa, numBu):
        """Create an io.BytesIO complete with a DFSR and LR type 0 of the
        specified number and dimensions, scans it into a LogPass and returns both."""
        myF = self._createFile(numLr, frPerLr, numCh, numSa, numBu)
        return myF, self._createLogPass(myF)

    def _iterateUsingValue(self, theFs):
        retCount = 0
        #print('_iterateUsingValue()', theFs.numFrames, theFs.numChannels)
        for fr in range(theFs.numFrames):
            for ch in range(theFs.numChannels):
                for sc in range(theFs.numSubChannels(ch)):
                    for sa in range(theFs.numSamples(ch, sc)):
                        for bu in range(theFs.numBursts(ch, sc)):
                            #print(myLp.frameSet.value(fr, ch, sc, sa, bu))
                            theFs.value(fr, ch, sc, sa, bu)
                            retCount += 1
        return retCount

    def _iterateUsingGen(self, theFs):
        retCount = 0
        #print('_iterateUsingGen()', theFs.numFrames, theFs.numChannels)
        for ch in range(theFs.numChannels):
            for sc in range(theFs.numSubChannels(ch)):
                for v in theFs.genChScValues(ch, sc):
                    retCount += 1
        return retCount


@pytest.mark.slow
class TestLogPass_Type0(TestLogPass_Type0_Base):
    """Reading binary data."""
    
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestLogPass_Type0: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestLogPass_Type0.test_00(): Internals."""
        #print()
        #print(self._retLr0Bytes(1,1,1,1,1))
        self.assertEqual(self._retLr0Bytes(1,1,1,1,1), b'\x00\n\x00\x00\x00\x00DL\x80\x00')
        myDb = self._retDFSRBytes(1, 1, 1)
        self.assertEqual(myDb, b'@\x00\x00\x01B\x00DEPTServIDServOrdNFEET\x02\xb3`;\x01\x00\x00\x04000\x01D\x00\x01\x02\x03\x04')
        myDfsr = LogiRec.LrDFSRRead(self._retFileSinglePr(myDb))
        #print(self._retDFSRBytes(1, 1, 1))
        #print(self._retDFSRBytes(3, 4, 8))
        self.assertEqual(
            self._retDFSRBytes(3, 4, 8),
            b'@\x00\x00\x01B\x00'
            + b'DEPTServIDServOrdNFEET\x02\xb3`;\x01\x00\x00\x04000\x01D\x00\x01\x02\x03\x04' \
            + b'0000ServIDServOrdN    \x02\xb3`;\x01\x00\x00\x80000\x04D\x00\x01\x02\x03\x04' \
            + b'0001ServIDServOrdN    \x02\xb3`;\x01\x00\x00\x80000\x04D\x00\x01\x02\x03\x04',
        )

    def test_01(self):
        """TestLogPass_Type0.test_01(): Simple file: lr,fr,ch,sa,bu=(4, 8, 2, 1, 1)"""
        lr, fr, ch, sa, bu = (4, 8, 2, 1, 1)
        myBd = self._retSinglePr(self._retDFSRBytes(ch, sa, bu))
        myBl = self._retLr0Bytes(lr, fr, ch, sa, bu)
        #print()
        #print('len(myBl)', len(myBl))
        myF = self._retFileFromBytes(myBd+myBl)
        evtS = []
        while not myF.isEOF:
            t = myF.tellLr()
            b = myF.readLrBytes(2)
            s = myF.skipToNextLr()
            evtS.append((t, b, s))
        #print(evtS)
        self.assertEqual(
            evtS,
            [
                (0, b'@\x00', 84),
                (90, b'\x00\x00', 64),
                (160, b'\x00\x00', 64),
                (230, b'\x00\x00', 64),
                (300, b'\x00\x00', 64),
            ]
        )
        
    def test_02(self):
        """TestLogPass_Type0.test_02(): Simple file: lr,fr,ch,sa,bu=(4, 8, 2, 1, 1), construct LogPass."""
        lr, fr, ch, sa, bu = (4, 8, 2, 1, 1)
        myBd = self._retSinglePr(self._retDFSRBytes(ch, sa, bu))
        myBl = self._retLr0Bytes(lr, fr, ch, sa, bu)
        print()
        print('len(myBl)', len(myBl))
        myF = self._retFileFromBytes(myBd+myBl)
        t = myF.tellLr()
        myDfsr = LogiRec.LrDFSRRead(myF)
        s = myF.skipToNextLr()
        print('tell DFSR:', t, 'skip:', s)
        myLp = LogPass.LogPass(myDfsr, 'MyFile')
        print(
            'File length:', len(myBd)+len(myBl),
            'Data length:', len(myBl),
            'Channels:', len(myDfsr.dsbBlocks),
            'Frame size:', myDfsr.frameSize(),
        )
        while not myF.isEOF:
            t = myF.tellLr()
            lrType, lrAttr = myF.readLrBytes(2)
            s = myF.skipToNextLr()
            print(t, lrType, s)
            myLp.addType01Data(t, lrType, s, 1.0)
        print(myLp)
        myLp.setFrameSet(myF)
        print(myLp)
        valCount = 0
        for fr in range(32):
            for ch in range(2):
                for sc in range(1):
                    for sa in range(1):
                        for bu in range(1):
                            #print(myLp.frameSet.value(fr, ch, sc, sa, bu))
                            valCount += 1
        print('valCount', valCount)
        
    def test_03_00(self):
        """TestLogPass_Type0.test_03_00(): lr,fr,ch,sa,bu=(256,8,128,1,1)=1MB, create file."""
        # 256 LR * 8 frames = 2048 frames
        # 128 ch * 4 bytes = 512 byte frame length
        # Total: 2048 * 512 = 1MB
        tS = time.perf_counter()
        numLr, frPerLr, numCh, numSa, numBu = (256, 8, 128, 1, 1)
        self._createFile(numLr, frPerLr, numCh, numSa, numBu)
        sys.stderr.write(' Time: {:8.3f} '.format(time.perf_counter()-tS))
    
    def test_03_01(self):
        """TestLogPass_Type0.test_03_01(): lr,fr,ch,sa,bu=(256,8,128,1,1)=1MB, populate LogPass."""
        numLr, frPerLr, numCh, numSa, numBu = (256, 8, 128, 1, 1)
        lisLen = 4 * numLr * frPerLr * numCh * numSa * numBu
        myF = self._createFile(numLr, frPerLr, numCh, numSa, numBu)
        tS = time.perf_counter()
        myLp = self._createLogPass(myF)
        #print(myF, myLp)
        #sys.stderr.write(' Time: {:8.3f} '.format(time.perf_counter()-tS))
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))

    def test_03_02(self):
        """TestLogPass_Type0.test_03_02(): lr,fr,ch,sa,bu=(256,8,128,1,1)=1MB, setFrameSet() all frames."""
        numLr, frPerLr, numCh, numSa, numBu = (256, 8, 128, 1, 1)
        lisLen = 4 * numLr * frPerLr * numCh * numSa * numBu
        myF, myLp = self._createFileLogPass(numLr, frPerLr, numCh, numSa, numBu)
        tS = time.perf_counter()
        myLp.setFrameSet(myF)
        #sys.stderr.write(' Time: {:8.3f} '.format(time.perf_counter()-tS))
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))

    def test_03_03(self):
        """TestLogPass_Type0.test_03_03(): lr,fr,ch,sa,bu=(256,8,128,1,1)=1MB, all value()."""
        numLr, frPerLr, numCh, numSa, numBu = (256, 8, 128, 1, 1)
        lisLen = 4 * numLr * frPerLr * numCh * numSa * numBu
        myF, myLp = self._createFileLogPass(numLr, frPerLr, numCh, numSa, numBu)
        myLp.setFrameSet(myF)
        #print('test_03_03(): LogPass', myLp)
        tS = time.perf_counter()
        valCount = self._iterateUsingValue(myLp.frameSet)
        #print('valCount', valCount)
        self.assertEqual(1024*1024//4, valCount)
        #sys.stderr.write(' Time: {:8.3f} '.format(time.perf_counter()-tS))
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))

    def test_03_04(self):
        """TestLogPass_Type0.test_03_04(): lr,fr,ch,sa,bu=(256,8,128,1,1)=1MB, all genChScValues()."""
        numLr, frPerLr, numCh, numSa, numBu = (256, 8, 128, 1, 1)
        lisLen = 4 * numLr * frPerLr * numCh * numSa * numBu
        myF, myLp = self._createFileLogPass(numLr, frPerLr, numCh, numSa, numBu)
        myLp.setFrameSet(myF)
        #print('test_03_03(): LogPass', myLp)
        tS = time.perf_counter()
        valCount = self._iterateUsingGen(myLp.frameSet)
        #print('valCount', valCount)
        self.assertEqual(1024*1024//4, valCount)
        #sys.stderr.write(' Time: {:8.3f} '.format(time.perf_counter()-tS))
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))


@pytest.mark.slow
class TestLogPass_Type0_8MB(TestLogPass_Type0_Base):
    def test_04_00(self):
        """TestLogPass_Type0.test_04_00(): lr,fr,ch,sa,bu=(1024,8,256,1,1)=8MB, create file."""
        # 1024 LR * 8 frames = 8192 frames
        # 256 ch * 1 * 4 bytes = 1024 byte frame length
        # Total: 8192 * 1024 = 8MB
        # Values: 2*1024*1024 = 2097152
        tS = time.perf_counter()
        numLr, frPerLr, numCh, numSa, numBu = (1024, 8, 256, 1, 1)
        myF = self._createFile(numLr, frPerLr, numCh, numSa, numBu)
        #print('test_04_00', myF, dir(myF))
        sys.stderr.write(' Time: {:8.3f} '.format(time.perf_counter()-tS))
    
    def test_04_01(self):
        """TestLogPass_Type0.test_04_01(): lr,fr,ch,sa,bu=(1024,8,256,1,1)=8MB, create LogPass."""
        numLr, frPerLr, numCh, numSa, numBu = (1024, 8, 256, 1, 1)
        lisLen = 4 * numLr * frPerLr * numCh * numSa * numBu
        myF = self._createFile(numLr, frPerLr, numCh, numSa, numBu)
        tS = time.perf_counter()
        myLp = self._createLogPass(myF)
        #print(myF, myLp)
        #sys.stderr.write(' Time: {:8.3f} '.format(time.perf_counter()-tS))
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))

    def test_04_02(self):
        """TestLogPass_Type0.test_04_02(): lr,fr,ch,sa,bu=(1024,8,256,1,1)=8MB, setFrameSet() all frames."""
        numLr, frPerLr, numCh, numSa, numBu = (1024, 8, 256, 1, 1)
        lisLen = 4 * numLr * frPerLr * numCh * numSa * numBu
        myF, myLp = self._createFileLogPass(numLr, frPerLr, numCh, numSa, numBu)
        tS = time.perf_counter()
        myLp.setFrameSet(myF)
        #sys.stderr.write(' Time: {:8.3f} '.format(time.perf_counter()-tS))
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))

    def test_04_03(self):
        """TestLogPass_Type0.test_04_03(): lr,fr,ch,sa,bu=(1024,8,256,1,1)=8MB, all value()."""
        numLr, frPerLr, numCh, numSa, numBu = (1024, 8, 256, 1, 1)
        lisLen = 4 * numLr * frPerLr * numCh * numSa * numBu
        myF, myLp = self._createFileLogPass(numLr, frPerLr, numCh, numSa, numBu)
        myLp.setFrameSet(myF)
        #print('test_04_03(): LogPass', myLp)
        tS = time.perf_counter()
        valCount = self._iterateUsingValue(myLp.frameSet)
        #print('valCount', valCount)
        self.assertEqual(1024*1024*2, valCount)
        #sys.stderr.write(' Time: {:8.3f} '.format(time.perf_counter()-tS))
        self.writeCostToStderr(tS, lisLen, 'LIS MB', lisLen // (1024**2))


@pytest.mark.slow
class TestLogPass_Type0_LargeBurst(TestLogPass_Type0_Base):
    def test_05_00(self):
        """TestLogPass_Type0_LargeBurst.test_05_00(): lr,fr,ch,sa,bu=(512,2,2,2,1024)=8MB, create file."""
        # 512 LR * 2 frames = 1024 frames
        # 2 ch: 0ch * 4 bytes + 1 ch * 2 sa * 1024 bu * 4 bytes = 8196 byte frame length
        # Total: 1024 * 8196 = 8.004MB
        # Values: 2049 per frame * 1024 frames
        tS = time.perf_counter()
        numLr, frPerLr, numCh, numSa, numBu = (512, 2, 2, 2, 1024)
        myF = self._createFile(numLr, frPerLr, numCh, numSa, numBu)
        #print('test_04_00', myF, dir(myF))
        sys.stderr.write(' Time: {:8.3f} '.format(time.perf_counter()-tS))
    
    def test_05_01(self):
        """TestLogPass_Type0_LargeBurst.test_05_01(): lr,fr,ch,sa,bu=(512,2,2,2,1024)=8MB, populate LogPass."""
        numLr, frPerLr, numCh, numSa, numBu = (512, 2, 2, 2, 1024)
        myF = self._createFile(numLr, frPerLr, numCh, numSa, numBu)
        tS = time.perf_counter()
        myLp = self._createLogPass(myF)
        #print('test_05_01()', myF, myLp)
        sys.stderr.write(' Time: {:8.3f} '.format(time.perf_counter()-tS))

    def test_05_02(self):
        """TestLogPass_Type0_LargeBurst.test_05_02(): lr,fr,ch,sa,bu=(512,2,2,2,1024)=8MB, setFrameSet() all frames."""
        numLr, frPerLr, numCh, numSa, numBu = (512, 2, 2, 2, 1024)
        myF, myLp = self._createFileLogPass(numLr, frPerLr, numCh, numSa, numBu)
        #print('test_05_02()', myLp)
        tS = time.perf_counter()
        myLp.setFrameSet(myF)
        sys.stderr.write(' Time: {:8.3f} '.format(time.perf_counter()-tS))

    def test_05_03(self):
        """TestLogPass_Type0_LargeBurst.test_05_03(): lr,fr,ch,sa,bu=(512,2,2,2,1024)=8MB, all value()."""
        numLr, frPerLr, numCh, numSa, numBu = (512, 2, 2, 2, 1024)
        myF, myLp = self._createFileLogPass(numLr, frPerLr, numCh, numSa, numBu)
        myLp.setFrameSet(myF)
        #print('test_04_03(): LogPass', myLp)
        tS = time.perf_counter()
        valCount = self._iterateUsingValue(myLp.frameSet)
        #print('valCount', valCount)
        self.assertEqual(2049*1024, valCount)
        sys.stderr.write(' Time: {:8.3f} '.format(time.perf_counter()-tS))


@pytest.mark.slow
class TestLogPass_Type0_Profile(TestLogPass_Type0_Base):
    """Profile preocessing of Type 0 Logical Records."""
    def test_04_03(self):
        """TestLogPass_Type0.test_04_03(): lr,fr,ch,sa,bu=(256,8,128,1,1)=1MB, all values iteration 1."""
        numLr, frPerLr, numCh, numSa, numBu = (256, 8, 128, 1, 1)
        tS = time.perf_counter()
        myF, myLp = self._createFileLogPass(numLr, frPerLr, numCh, numSa, numBu)
        sys.stderr.write(' _createFileLogPass() time: {:8.3f} '.format(time.perf_counter()-tS))
        tS = time.perf_counter()
        myLp.setFrameSet(myF)
        #tS = time.perf_counter()
        #valCount = self._iterateUsingValue(myLp.frameSet)
        #self.assertEqual(1024*1024//4, valCount)
        sys.stderr.write(' setFrameSet() time: {:8.3f} '.format(time.perf_counter()-tS))

class Special(BaseTestClasses.TestBaseFile):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogPass_LowLevel))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogPassCtorRaises))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogPassBadDFSR))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogPassFromTestBase))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogPassStatic))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogPassStaticUpDirect))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogPass_Events_DownDirect))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogPass_Events_UpIndirect))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogPass_UpDirect_Dipmeter))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogPass_UpIndirect))

#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogPass_Perf))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogPass_Type0))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogPass_Type0_8MB))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogPass_Type0_LargeBurst))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogPass_Type0_Profile))
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
