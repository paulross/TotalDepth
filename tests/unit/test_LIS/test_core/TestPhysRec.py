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
"""Unit tests for the LogicalData module.
"""
import pytest

__author__  = 'Paul Ross'
__date__    = '8 Nov 2010'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2010 Paul Ross.'

import os
import sys
import time
import logging
import io

from TotalDepth.LIS.core import PhysRec

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import BaseTestClasses

######################
# Section: Unit tests.
######################
import unittest

class TestPhysRecLowLevel(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        self._pr = PhysRec.PhysRecRead(theFile=io.BytesIO(b''), theFileId='MyFile', keepGoing=False)
        self._prBits = range(PhysRec.PR_ATTRIBUTE_BITS)

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPhysRecLowLevel.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def _isAllClear(self):
        """retrusn true if all bits are clear."""
        for i in self._prBits:
            if not self._pr._isAttrBitClear(i):
                return False
        return True

    def _isAllSet(self):
        """returns true if all bits are set."""
        for i in self._prBits:
            if not self._pr._isAttrBitSet(i):
                return False
        return True

    def test_01(self):
        """TestPhysRecLowLevel.test_01(): Test all attribute bits are initially clear."""
        for i in self._prBits:
            self.assertTrue(self._pr._isAttrBitClear(i))
            self.assertFalse(self._pr._isAttrBitSet(i))
        self.assertTrue(self._isAllClear())
        self.assertFalse(self._isAllSet())

    def test_02(self):
        """TestPhysRecLowLevel.test_02(): Clear each attribute bits and test."""
        for i in self._prBits:
            #print('Was: i=', i, '{0:016b}'.format(self._pr.prAttr))
            self._pr._clearAttrBit(i)
            #print('Now: i=', i, '{0:016b}'.format(self._pr.prAttr))
            self.assertTrue(self._pr._isAttrBitClear(i))
            self.assertFalse(self._pr._isAttrBitSet(i))
        self.assertTrue(self._isAllClear())
        self.assertFalse(self._isAllSet())

    def test_03(self):
        """TestPhysRecLowLevel.test_03(): Set each attribute bits and test."""
        for i in self._prBits:
            self._pr._setAttrBit(i)
            self.assertTrue(self._pr._isAttrBitSet(i))
            self.assertFalse(self._pr._isAttrBitClear(i))
        self.assertFalse(self._isAllClear())
        self.assertTrue(self._isAllSet())

    def test_04(self):
        """TestPhysRecLowLevel.test_04(): Set, test, clear attribute bits(1)."""
        for i in self._prBits:
            self._pr._setAttrBit(i)
            self.assertTrue(self._pr._isAttrBitSet(i))
            self.assertFalse(self._pr._isAttrBitClear(i))
            self._pr._clearAttrBit(i)
            self.assertTrue(self._pr._isAttrBitClear(i))
            self.assertFalse(self._pr._isAttrBitSet(i))

    def test_05(self):
        """TestPhysRecLowLevel.test_05(): Set, test, clear attribute bits(2)."""
        for i in self._prBits:
            self._pr._setOrClearAttrBit(i, True)
            self.assertTrue(self._pr._isAttrBitSet(i))
            self.assertFalse(self._pr._isAttrBitClear(i))
            # Check all other bits clear so no side effects
            for j in self._prBits:
                if i != j:
                    self.assertFalse(self._pr._isAttrBitSet(j))
                    self.assertTrue(self._pr._isAttrBitClear(j))
            self._pr._setOrClearAttrBit(i, False)
            self.assertTrue(self._pr._isAttrBitClear(i))
            self.assertFalse(self._pr._isAttrBitSet(i))

    def test_06(self):
        """TestPhysRecLowLevel.test_06(): Clear, test, set, test, clear and test attribute bits (1)."""
        for i in self._prBits:
            self._pr._clearAttrBit(i)
            self.assertTrue(self._pr._isAttrBitClear(i))
            self.assertFalse(self._pr._isAttrBitSet(i))
            self._pr._setAttrBit(i)
            self.assertTrue(self._pr._isAttrBitSet(i))
            self.assertFalse(self._pr._isAttrBitClear(i))
            self._pr._clearAttrBit(i)
            self.assertTrue(self._pr._isAttrBitClear(i))
            self.assertFalse(self._pr._isAttrBitSet(i))

    def test_10(self):
        """TestPhysRecLowLevel.test_10(): Set, test, clear successor bit."""
        self.assertTrue(self._isAllClear())
        self.assertFalse(self._pr._hasSuccessor())
        self._pr._setAttrBit(PhysRec.PR_SUCCESSOR_ATTRIBUTE_BIT)
        self.assertTrue(self._pr._hasSuccessor())
        self._pr._clearAttrBit(PhysRec.PR_SUCCESSOR_ATTRIBUTE_BIT)
        self.assertFalse(self._pr._hasSuccessor())
        self._pr._setSuccessor(True)
        self.assertTrue(self._pr._hasSuccessor())
        self._pr._setSuccessor(False)
        self.assertFalse(self._pr._hasSuccessor())

    def test_11(self):
        """TestPhysRecLowLevel.test_11(): Set, test, clear predecessor bit."""
        self.assertTrue(self._isAllClear())
        self.assertFalse(self._pr._hasPredecessor())
        self._pr._setAttrBit(PhysRec.PR_PREDECESSOR_ATTRIBUTE_BIT)
        self.assertTrue(self._pr._hasPredecessor())
        self._pr._clearAttrBit(PhysRec.PR_PREDECESSOR_ATTRIBUTE_BIT)
        self.assertFalse(self._pr._hasPredecessor())
        self._pr._setPredecessor(True)
        self.assertTrue(self._pr._hasPredecessor())
        self._pr._setPredecessor(False)
        self.assertFalse(self._pr._hasPredecessor())

    def test_12(self):
        """TestPhysRecLowLevel.test_12(): Set, test, clear record number bit."""
        self.assertTrue(self._isAllClear())
        self.assertFalse(self._pr._hasRecordNumber())
        self._pr._setAttrBit(PhysRec.PR_RECORD_NUMBER_BIT)
        self.assertTrue(self._pr._hasRecordNumber())
        self._pr._clearAttrBit(PhysRec.PR_RECORD_NUMBER_BIT)
        self.assertFalse(self._pr._hasRecordNumber())
        self._pr._setHasRecordNumber(True)
        self.assertTrue(self._pr._hasRecordNumber())
        self._pr._setHasRecordNumber(False)
        self.assertFalse(self._pr._hasRecordNumber())

    def test_13(self):
        """TestPhysRecLowLevel.test_13(): Set, test, clear file number bit."""
        self.assertTrue(self._isAllClear())
        self.assertFalse(self._pr._hasFileNumber())
        self._pr._setAttrBit(PhysRec.PR_FILE_NUMBER_BIT)
        self.assertTrue(self._pr._hasFileNumber())
        self._pr._clearAttrBit(PhysRec.PR_FILE_NUMBER_BIT)
        self.assertFalse(self._pr._hasFileNumber())
        self._pr._setHasFileNumber(True)
        self.assertTrue(self._pr._hasFileNumber())
        self._pr._setHasFileNumber(False)
        self.assertFalse(self._pr._hasFileNumber())

    def test_14(self):
        """TestPhysRecLowLevel.test_14(): Set, test, clear checksum bit."""
        self.assertTrue(self._isAllClear())
        self.assertFalse(self._pr._hasChecksum())
        self._pr._setAttrBit(PhysRec.PR_CHECKSUM_BIT)
        self.assertTrue(self._pr._hasChecksum())
        self._pr._clearAttrBit(PhysRec.PR_CHECKSUM_BIT)
        self.assertFalse(self._pr._hasChecksum())
        self._pr._setHasChecksum(True)
        self.assertTrue(self._pr._hasChecksum())
        self._pr._setHasChecksum(False)
        self.assertFalse(self._pr._hasChecksum())

    def test_14_01(self):
        """TestPhysRecLowLevel.test_14_01(): Set, test, clear bad checksum bit."""
        self.assertTrue(self._isAllClear())
        self._pr._setAttrBit(PhysRec.PR_CHECKSUM_UNDEFINED_BIT)
        self.assertRaises(PhysRec.ExceptionPhysRecUndefinedChecksum, self._pr._hasChecksum)

class TestPhysRecSingleRead(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        myFi = io.BytesIO(b'\x00>\x00\x00\x80\x00RUNONE.R01\x00\x00DATAZE                \x00 1024\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        self._pr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPhysRecRead.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPhysRecRead.test_01(): Single physical record."""
        myLd = self._pr.readLrBytes()
        self.assertEqual(len(myLd), 58)
        self.assertEqual(myLd, b'\x80\x00RUNONE.R01\x00\x00DATAZE                \x00 1024\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
#        try:
#            self._pr.skipToNextLr()
#            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
#        except PhysRec.ExceptionPhysRecEOF:
#            pass
        self._pr.skipToNextLr()
        self.assertTrue(self._pr.isEOF)

    def test_02(self):
        """TestPhysRecRead.test_02(): Single physical record, partial read of 2 bytes."""
        myLd = self._pr.readLrBytes(2)
        self.assertEqual(len(myLd), 2)
        self.assertEqual(myLd, b'\x80\x00')

    def test_03(self):
        """TestPhysRecRead.test_03(): Single physical record __str__()."""
        myLd = self._pr.readLrBytes()
        self.assertEqual(self._pr.strHeader(), 'PR:     tell()  Length    Attr  LD_len  RecNum  FilNum  ChkSum')
        self.assertEqual(str(self._pr), 'PR: 0x       0      62  0x   0      58  ------  ------  ------')

    def test_04(self):
        """TestPhysRecRead.test_04(): Single physical record __str__() at EOF."""
        myLd = self._pr.readLrBytes()
        self.assertEqual(self._pr.strHeader(), 'PR:     tell()  Length    Attr  LD_len  RecNum  FilNum  ChkSum')
        self.assertEqual(str(self._pr), 'PR: 0x       0      62  0x   0      58  ------  ------  ------')
        self.assertTrue(self._pr.readLrBytes() is None)
        self.assertEqual(str(self._pr), 'PR: EOF')

class TestPhysRecSingleReadWithTif(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        myFi = io.BytesIO(
            # Opening TIF
            b'\x00\x00\x00\x00'+b'\x00\x00\x00\x00'+b'\x4a\x00\x00\x00' \
            + b'\x00>\x00\x00\x80\x00RUNONE.R01\x00\x00DATAZE                \x00 1024\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            # EOF
            + b'\x01\x00\x00\x00'+b'\x00\x00\x00\x00'+b'\x56\x00\x00\x00' \
            +b'\x01\x00\x00\x00'+b'\x4a\x00\x00\x00'+b'\x62\x00\x00\x00'
        )
        self._pr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPhysRecSingleReadWithTif.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPhysRecSingleReadWithTif.test_01(): Single physical record."""
        myLd = self._pr.readLrBytes()
        self.assertEqual(len(myLd), 58)
        self.assertEqual(myLd, b'\x80\x00RUNONE.R01\x00\x00DATAZE                \x00 1024\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
#        try:
#            self._pr.skipToNextLr()
#            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
#        except PhysRec.ExceptionPhysRecEOF:
#            pass
        self._pr.skipToNextLr()
        self.assertTrue(self._pr.isEOF)

    def test_03(self):
        """TestPhysRecSingleReadWithTif.test_01(): Single physical record __str__()."""
        myLd = self._pr.readLrBytes()
        #print
        #print(self._pr.strHeader())
        self.assertEqual(self._pr.strHeader(), 'TIF     ?  :        Type        Back        Next  PR:     tell()  Length    Attr  LD_len  RecNum  FilNum  ChkSum')
        #print(self._pr)
        self.assertEqual(str(self._pr), 'TIF  True >:  0x       0  0x       0  0x      4a  PR: 0x       0      62  0x   0      58  ------  ------  ------')

    def test_04(self):
        """TestPhysRecSingleReadWithTif.test_01(): Single physical record, read one byte then seekCurrentLrStart()."""
        myLd = self._pr.readLrBytes(1)
        self.assertEqual(myLd, b'\x80')
        self._pr.seekCurrentLrStart()
        myLd = self._pr.readLrBytes(1)
        self.assertEqual(myLd, b'\x80')

class TestPhysRecTrailer(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPhysRecTrailer.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPhysRecTrailer.test_01(): No trailer, no logical data."""
        myFi = io.BytesIO(
            # Length of 3 is negative logical length
            PhysRec.PR_PRH_LEN_FORMAT.pack(3) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0)
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        try:
            myLd = myPr.readLrBytes()
            self.fail('PhysRec.ExceptionPhysRec not raised.')
        except PhysRec.ExceptionPhysRec:
            pass

    def test_02(self):
        """TestPhysRecTrailer.test_02(): trailer record number."""
        myFi = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(6) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1<<9) \
            + b'\x00\xff'
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        myLd = myPr.readLrBytes()
        self.assertTrue(myPr.readLrBytes() is None)
        self.assertEqual(myPr.recNum, 255)
        self.assertTrue(myPr.fileNum is None)
        self.assertTrue(myPr.checksum is None)

    def test_03(self):
        """TestPhysRecTrailer.test_03(): trailer file number."""
        myFi = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(6) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1<<10) \
            + b'\x00\x0f'
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        myLd = myPr.readLrBytes()
        self.assertTrue(myPr.readLrBytes() is None)
        self.assertTrue(myPr.recNum is None)
        self.assertEqual(myPr.fileNum, 15)
        self.assertTrue(myPr.checksum is None)

    def test_04(self):
        """TestPhysRecTrailer.test_04(): trailer checksum."""
        myFi = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(6) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1<<12) \
            + b'\xff\xff'
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        myLd = myPr.readLrBytes()
        self.assertTrue(myPr.readLrBytes() is None)
        self.assertTrue(myPr.recNum is None)
        self.assertTrue(myPr.fileNum is None)
        self.assertEqual(myPr.checksum, 65535)

    def test_05(self):
        """TestPhysRecTrailer.test_05(): trailer record, file and checksum."""
        myFi = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(10) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(11<<9) \
            + b'\x00\x01' \
            + b'\x00\x02' \
            + b'\x00\x03'
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        self.assertTrue(myPr.readLrBytes() is None)
        self.assertEqual(myPr.recNum, 1)
        self.assertEqual(myPr.fileNum, 2)
        self.assertEqual(myPr.checksum, 3)

class TestPhysRecFail(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPhysRecFail.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPhysRecFail.test_01(): Single physical record with negative logical data length."""
        myFi = io.BytesIO(
            # Length of 3 is negative logical length
            PhysRec.PR_PRH_LEN_FORMAT.pack(3) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0)
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        try:
            myLd = myPr.readLrBytes()
            self.fail('PhysRec.ExceptionPhysRec not raised.')
        except PhysRec.ExceptionPhysRec:
            pass

    def test_02(self):
        """TestPhysRecFail.test_02(): PR with record trailer has negative logical data length."""
        myFi = io.BytesIO(
            # Length of 5 with record trailer is negative logical length
            PhysRec.PR_PRH_LEN_FORMAT.pack(5) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1<<9) \
            + b'\xff\xff'
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        try:
            myLd = myPr.readLrBytes()
            self.fail('PhysRec.ExceptionPhysRec not raised.')
        except PhysRec.ExceptionPhysRec:
            pass

    def test_03(self):
        """TestPhysRecFail.test_03(): PR with file trailer has negative logical data length."""
        myFi = io.BytesIO(
            # Length of 5 with file number trailer is negative logical length
            PhysRec.PR_PRH_LEN_FORMAT.pack(5) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1<<10) \
            + b'\xff\xff'
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        try:
            myLd = myPr.readLrBytes()
            self.fail('PhysRec.ExceptionPhysRec not raised.')
        except PhysRec.ExceptionPhysRec:
            pass

    def test_04(self):
        """TestPhysRecFail.test_04(): PR with checksum has negative logical data length."""
        myFi = io.BytesIO(
            # Length of 5 with checksum trailer is negative logical length
            PhysRec.PR_PRH_LEN_FORMAT.pack(5) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1<<12) \
            + b'\xff\xff'
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        try:
            myLd = myPr.readLrBytes()
            self.fail('PhysRec.ExceptionPhysRec not raised.')
        except PhysRec.ExceptionPhysRec:
            pass

    def test_05(self):
        """TestPhysRecFail.test_05(): Type 1 Physical Record raises exception."""
        myFi = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(4) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1<<PhysRec.PR_TYPE_BIT)
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        try:
            myLd = myPr.readLrBytes()
            self.fail('PhysRec.ExceptionPhysRec not raised.')
        except PhysRec.ExceptionPhysRecUnknownType:
            pass

    def test_10(self):
        """TestPhysRecFail.test_10(): Solitary physical records claims successor but EOF."""
        # Suc no Pre: 1
        # Pre no Suc: 2
        # Suc and Pre: 3
        myFi = io.BytesIO(
            # First PR, has a single logical byte and successor bit
            b'\x00\x05' \
            + b'\x00\x01' \
            + b'\x00'
            # No successor record
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        try:
            myLd = myPr.readLrBytes()
            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
        except PhysRec.ExceptionPhysRecEOF:
            pass

    def test_20(self):
        """TestPhysRecTrailer.test_20(): trailer record number declared but absent."""
        myFi = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(10) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1<<9) \
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        try:
            myLd = myPr.readLrBytes()
            self.fail('PhysRec.ExceptionPhysRec not raised.')
        except PhysRec.ExceptionPhysRecEOF:
            pass

    def test_30(self):
        """TestPhysRecFail.test_30(): close() followed by a read() raises ValueError."""
        myFi = io.BytesIO(
            # Length of 3 is negative logical length
            PhysRec.PR_PRH_LEN_FORMAT.pack(5) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x00'
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        self.assertEqual(b'\x00', myPr.readLrBytes())
        myPr.close()
        try:
            myPr.readLrBytes()
            self.fail('ValueError not raised after close().')
        except ValueError:
            pass

    def test_40(self):
        """TestPhysRecFail.test_40(): header says two bytes but only one there."""
        myFi = io.BytesIO(
            # Length of 3 is negative logical length
            PhysRec.PR_PRH_LEN_FORMAT.pack(6) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x00'
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        #self.assertEqual(b'\x00', myPr.readLrBytes())
        try:
            myPr.readLrBytes()
            self.fail('PhysRec.ExceptionPhysRec not raised on preamature EOF')
        except PhysRec.ExceptionPhysRecEOF:
            pass

    def test_41(self):
        """TestPhysRecFail.test_41(): header says two bytes but only one there with keepGoing=True."""
        myFi = io.BytesIO(
            # Length of 3 is negative logical length
            PhysRec.PR_PRH_LEN_FORMAT.pack(6) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x00'
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=True)
        self.assertEqual(b'\x00', myPr.readLrBytes())
        try:
            myPr.readLrBytes()
            self.fail('PhysRec.ExceptionPhysRec not raised on preamature EOF')
        except PhysRec.ExceptionPhysRecEOF:
            pass

    def test_42(self):
        """TestPhysRecFail.test_42(): header says file number in trailer but EOF, keepGoing=True."""
        myFi = io.BytesIO(
            # Length of 3 is negative logical length
            PhysRec.PR_PRH_LEN_FORMAT.pack(7) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1<<9) \
            + b'\x00'
            # Absent trailer
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=True)
        self.assertEqual(b'\x00', myPr.readLrBytes())
        try:
            myPr.readLrBytes()
            self.fail('PhysRec.ExceptionPhysRec not raised on preamature EOF')
        except PhysRec.ExceptionPhysRecEOF:
            pass

    def test_43(self):
        """TestPhysRecFail.test_43(): header says file number in trailer but EOF, keepGoing=False."""
        myFi = io.BytesIO(
            # Length of 3 is negative logical length
            PhysRec.PR_PRH_LEN_FORMAT.pack(7) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1<<9) \
            + b'\x00'
            # Absent trailer
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        try:
            myPr.readLrBytes()
            self.fail('PhysRec.ExceptionPhysRec not raised on preamature EOF')
        except PhysRec.ExceptionPhysRecEOF:
            pass

    def test_50(self):
        """TestPhysRecFail.test_50(): non-existent file."""
        try:
            PhysRec.PhysRecRead(theFile='non-existent file', theFileId='non-existent file', keepGoing=True)
            self.fail('PhysRec.ExceptionPhysRec not raised on non-existent file.')
        except PhysRec.ExceptionPhysRec:
            pass

class TestPhysRecMultipleRead(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPhysRecMultipleRead.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPhysRecMultipleRead.test_01(): Single physical record."""
        #print()
        #print(PhysRec.PR_PRH_LEN_FORMAT.pack(3))
        #print(PhysRec.PR_PRH_ATTR_FORMAT.pack(1<<PhysRec.PR_SUCCESSOR_ATTRIBUTE_BIT)
        myFi = io.BytesIO(
            # First PR, has a single logical byte
            b'\x00\x05' \
            + b'\x00\x00' \
            + b'\xff'
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        myLd = myPr.readLrBytes()
        self.assertEqual(len(myLd), 1)
        self.assertEqual(myLd, b'\xff')
#        try:
#            myPr.skipToNextLr()
#            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
#        except PhysRec.ExceptionPhysRecEOF:
#            pass
        myPr.skipToNextLr()
        self.assertTrue(myPr.isEOF)

    def test_02(self):
        """TestPhysRecMultipleRead.test_02(): Single logical data, two physical records."""
        #print()
        #print(PhysRec.PR_PRH_LEN_FORMAT.pack(3))
        #print(PhysRec.PR_PRH_ATTR_FORMAT.pack(1<<PhysRec.PR_SUCCESSOR_ATTRIBUTE_BIT)
        # Suc no Pre: 1
        # Pre no Suc: 2
        # Suc and Pre: 3
        myFi = io.BytesIO(
            # First PR, has a single logical byte
            b'\x00\x05' \
            + b'\x00\x01' \
            + b'\x00' \
            # Second PR, has a three logical bytes
            + b'\x00\x07' \
            + b'\x00\x02' \
            + b'\x01\x02\x03'
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        myLd = myPr.readLrBytes()
        self.assertEqual(len(myLd), 4)
        self.assertEqual(myLd, b'\x00\x01\x02\x03')
#        try:
#            myPr.skipToNextLr()
#            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
#        except PhysRec.ExceptionPhysRecEOF:
#            pass
        myPr.skipToNextLr()
        self.assertTrue(myPr.isEOF)

    def test_02_01(self):
        """TestPhysRecMultipleRead.test_02_01(): Single logical data, two physical records, missing predecessor bit."""
        # Suc no Pre: 1
        # Pre no Suc: 2
        # Suc and Pre: 3
        myFi = io.BytesIO(
            # First PR, has a single logical byte
            b'\x00\x05' \
            + b'\x00\x01' \
            + b'\x00' \
            # Second PR, has a three logical bytes
            + b'\x00\x07' \
            # Should be: + b'\x00\x02' \
            + b'\x00\x00' \
            + b'\x01\x02\x03'
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        myLd = myPr.readLrBytes()
        self.assertEqual(len(myLd), 4)
        self.assertEqual(myLd, b'\x00\x01\x02\x03')
#        try:
#            myPr.skipToNextLr()
#            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
#        except PhysRec.ExceptionPhysRecEOF:
#            pass
        myPr.skipToNextLr()
        self.assertTrue(myPr.isEOF)

    def test_03(self):
        """TestPhysRecMultipleRead.test_03(): Single logical data, two physical records, read one byte at a time."""
        myFi = io.BytesIO(
            # First PR, has a single logical byte
            b'\x00\x05' \
            + b'\x00\x01' \
            + b'\x00' \
            # Second PR, has a three logical bytes
            + b'\x00\x07' \
            + b'\x00\x02' \
            + b'\x01\x02\x03'
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        #print
        #for i in range(4):
        #    print(myPr.readLrBytes(1))
        #return
        #assert(0)
        myLd = bytes()
        for i in range(4):
            myLd = myPr.readLrBytes(1, myLd)
        self.assertEqual(len(myLd), 4)
        self.assertEqual(myLd, b'\x00\x01\x02\x03')
        self.assertTrue(myPr.readLrBytes() is None)
#        try:
#            myPr.skipToNextLr()
#            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
#        except PhysRec.ExceptionPhysRecEOF:
#            pass
        myPr.skipToNextLr()
        self.assertTrue(myPr.isEOF)

class TestPhysRecMultipleReadWithTif(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        #print()
        #print(PhysRec.PR_PRH_LEN_FORMAT.pack(3))
        #print(PhysRec.PR_PRH_ATTR_FORMAT.pack(1<<PhysRec.PR_SUCCESSOR_ATTRIBUTE_BIT)
        myFi = io.BytesIO(
            # Opening TIF
            b'\x00\x00\x00\x00'+b'\x00\x00\x00\x00'+b'\x11\x00\x00\x00' \
            # First PR, has a single logical byte
            + b'\x00\x05\x00\x00\xff' \
            # EOF
            + b'\x01\x00\x00\x00'+b'\x00\x00\x00\x00'+b'\x1d\x00\x00\x00' \
            +b'\x01\x00\x00\x00'+b'\x11\x00\x00\x00'+b'\x29\x00\x00\x00'
        )
        self._pr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPhysRecSingleReadWithTif.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPhysRecSingleReadWithTif.test_01(): Single physical record."""
        myLd = self._pr.readLrBytes()
        self.assertEqual(len(myLd), 1)
        self.assertEqual(myLd, b'\xff')
#        try:
#            myLd = self._pr.skipToNextLr()
#            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
#        except PhysRec.ExceptionPhysRecEOF:
#            pass
        self._pr.skipToNextLr()
        self.assertTrue(self._pr.isEOF)

class TestPhysRecGenLd(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPhysRecGenLd.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPhysRecGenLd.test_01(): Single physical record."""
        myFi = io.BytesIO(
            # Opening TIF
            b'\x00\x00\x00\x00'+b'\x00\x00\x00\x00'+b'\x11\x00\x00\x00' \
            # First PR, has a single logical byte
            + b'\x00\x05' \
            + b'\x00\x00' \
            + b'\xff' \
            # EOF
            + b'\x01\x00\x00\x00'+b'\x00\x00\x00\x00'+b'\x1d\x00\x00\x00' \
            +b'\x01\x00\x00\x00'+b'\x11\x00\x00\x00'+b'\x62\x00\x00\x00'
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        for aLd in myPr.genLd():
            #print(aLd)
            pass
        self.assertTrue(myPr.isEOF)
        try:
            myLd = myPr.readLrBytes()
            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
        except PhysRec.ExceptionPhysRecEOF:
            pass

class TestPhysRecMultipleSkip(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPhysRecMultipleSkip.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPhysRecMultipleSkip.test_01(): Single physical record."""
        myFi = io.BytesIO(
            # First PR, has a eight logical bytes
            b'\x00\x0C' \
            + b'\x00\x00' \
            + bytes(range(8))
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        self.assertEqual(2, myPr.skipLrBytes(2))
        self.assertEqual(6, myPr.skipLrBytes())
        self.assertEqual(0, myPr.skipLrBytes())
        try:
            myLd = myPr.skipToNextLr()
            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
        except PhysRec.ExceptionPhysRecEOF:
            pass

    def test_02(self):
        """TestPhysRecMultipleSkip.test_02(): Single logical data, two physical records."""
        # Suc no Pre: 1
        # Pre no Suc: 2
        # Suc and Pre: 3
        myFi = io.BytesIO(
            # First PR, has a single logical byte
            b'\x00\x0C' \
            + b'\x00\x01' \
            + bytes(range(8)) \
            # Second PR, has a six logical bytes
            + b'\x00\x0A' \
            + b'\x00\x02' \
            + bytes(range(6))
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        self.assertEqual(8, myPr.skipLrBytes(8))
        self.assertEqual(0, myPr.startPrPos)
        self.assertTrue(myPr.isLrStart)
        # Skip one more byte
        self.assertEqual(1, myPr.skipLrBytes(1))
        self.assertEqual(12, myPr.startPrPos)
        self.assertFalse(myPr.isLrStart)
        # Skip the rest
        self.assertEqual(5, myPr.skipLrBytes())
        self.assertEqual(12, myPr.startPrPos)
        self.assertFalse(myPr.isLrStart)
        self.assertEqual(0, myPr.skipLrBytes())
        try:
            myLd = myPr.skipToNextLr()
            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
        except PhysRec.ExceptionPhysRecEOF:
            pass

class TestPhysRecRandomAccessLogicalData(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        # Suc no Pre: 1
        # Pre no Suc: 2
        # Suc and Pre: 3
        myBytes = bytes(
            # First LD: 4 bytes
            # First PR, has a single logical byte
            b'\x00\x05' \
            + b'\x00\x01' \
            + b'\x00' \
            # Second PR, has a three logical bytes
            + b'\x00\x07' \
            + b'\x00\x02' \
            + b'\x01\x02\x03' \
            # Second LD starts at position 12: 14 bytes long
            # PR 1/3, has a two logical bytes
            + b'\x00\x06' \
            + b'\x00\x01' \
            + b'\x04\x05' \
            # PR 2/3, has a seven logical bytes
            + b'\x00\x0B' \
            + b'\x00\x03' \
            + bytes(range(6,6+7)) \
            # PR 3/3, has a five logical bytes
            + b'\x00\x09' \
            + b'\x00\x02' \
            + bytes(range(6+7,6+7+5)) \
            # Second LD starts at position 38: eight bytes long
            # First PR, has a eight logical bytes
            + b'\x00\x0C' \
            + b'\x00\x00' \
            + bytes(range(18,18+8))
        ) 
        myFi = io.BytesIO(myBytes)
        self._pr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPhysRecRandomAccessLogicalData.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPhysRecRandomAccessLogicalData.test_01(): Three logical records, numerous physical records: use genLd()."""
        #print()
        myLdS = [aLd for aLd in self._pr.genLd()]
        self.assertEqual(
            myLdS,
            [
                (b'\x00', True),
                (b'\x01\x02\x03', False),
                (b'\x04\x05', True),
                (b'\x06\x07\x08\t\n\x0b\x0c', False),
                (b'\r\x0e\x0f\x10\x11', False),
                (b'\x12\x13\x14\x15\x16\x17\x18\x19', True),
            ] 
        )
        self.assertTrue(self._pr.isEOF)
        try:
            myLd = self._pr.readLrBytes()
            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
        except PhysRec.ExceptionPhysRecEOF:
            pass

    def test_02(self):
        """TestPhysRecRandomAccessLogicalData.test_02(): tellLr() for each physical record."""
        #print()
        myLdS = [self._pr.tellLr() for aLd in self._pr.genLd()]
        self.assertEqual(
            myLdS,
            [0, 0, 12, 12, 12, 38] 
        )
        self.assertTrue(self._pr.isEOF)
        try:
            myLd = self._pr.readLrBytes()
            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
        except PhysRec.ExceptionPhysRecEOF:
            pass

    def test_03(self):
        """TestPhysRecRandomAccessLogicalData.test_03(): use readLrBytes() and tellLr()."""
        self.assertEqual(self._pr.tellLr(), 0)
        self.assertEqual(self._pr.readLrBytes(), bytes(range(4)))
        self.assertEqual(self._pr.tellLr(), 0)
        self.assertEqual(self._pr.readLrBytes(), bytes(range(4,4+14)))
        self.assertEqual(self._pr.tellLr(), 4*2 + 4)
        self.assertEqual(self._pr.readLrBytes(), bytes(range(4+14,4+14+8)))
        self.assertEqual(self._pr.tellLr(), 4*5 + 4 + 14)
        self.assertTrue(self._pr.readLrBytes() is None)
        self.assertEqual(self._pr.tellLr(), 4*5 + 4 + 14)
        try:
            self._pr.skipToNextLr()
            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
        except PhysRec.ExceptionPhysRecEOF:
            pass
        self.assertTrue(self._pr.isEOF)
        
    def test_04(self):
        """TestPhysRecRandomAccessLogicalData.test_04(): use skipLrBytes() and tellLr()."""
        self.assertEqual(self._pr.tellLr(), 0)
        self.assertEqual(self._pr.skipLrBytes(), 4)
        self.assertEqual(self._pr.tellLr(), 0)
        self.assertEqual(self._pr.skipLrBytes(), 14)
        self.assertEqual(self._pr.tellLr(), 4*2 + 4)
        self.assertEqual(self._pr.skipLrBytes(), 8)
        self.assertEqual(self._pr.tellLr(), 4*5 + 4 + 14)
        self.assertEqual(0, self._pr.skipLrBytes())
        self.assertEqual(self._pr.tellLr(), 4*5 + 4 + 14)
        try:
            self._pr.skipToNextLr()
            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
        except PhysRec.ExceptionPhysRecEOF:
            pass
        self.assertTrue(self._pr.isEOF)
        
    def test_05(self):
        """TestPhysRecRandomAccessLogicalData.test_05(): use readLrBytes(2), skipLrBytes() and tellLr()."""
        self.assertEqual(self._pr.tellLr(), 0)
        # First logical record
        self.assertEqual(self._pr.readLrBytes(2), bytes(range(2)))
        self.assertEqual(self._pr.skipLrBytes(), 4-2)
        self.assertEqual(self._pr.tellLr(), 0)
        self.assertEqual(self._pr.readLrBytes(2), bytes(range(4,4+2)))
        self.assertEqual(self._pr.skipLrBytes(), 14-2)
        self.assertEqual(self._pr.tellLr(), 4*2 + 4)
        self.assertEqual(self._pr.readLrBytes(2), bytes(range(4+14,4+14+2)))
        self.assertEqual(self._pr.skipLrBytes(), 8-2)
        self.assertEqual(self._pr.tellLr(), 4*5 + 4 + 14)
        self.assertTrue(self._pr.readLrBytes() is None)
        self.assertEqual(self._pr.tellLr(), 4*5 + 4 + 14)
        try:
            self._pr.skipToNextLr()
            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
        except PhysRec.ExceptionPhysRecEOF:
            pass
        self.assertTrue(self._pr.isEOF)
        
    def test_06(self):
        """TestPhysRecRandomAccessLogicalData.test_06(): use readLrBytes(2), skipToNextLr() and tellLr()."""
        self.assertEqual(self._pr.tellLr(), 0)
        # First logical record
        self.assertEqual(self._pr.readLrBytes(2), bytes(range(2)))
        self.assertEqual(self._pr.tellLr(), 0)
        self._pr.skipToNextLr()
        self.assertEqual(self._pr.readLrBytes(2), bytes(range(4,4+2)))
        self.assertEqual(self._pr.tellLr(), 4*2 + 4)
        self._pr.skipToNextLr()
        self.assertEqual(self._pr.readLrBytes(2), bytes(range(4+14,4+14+2)))
        self.assertEqual(self._pr.tellLr(), 4*5 + 4 + 14)
        self._pr.skipToNextLr()
#        try:
#            self._pr.skipToNextLr()
#            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
#        except PhysRec.ExceptionPhysRecEOF:
#            pass
        self.assertTrue(self._pr.isEOF)
        
    def test_07(self):
        """TestPhysRecRandomAccessLogicalData.test_07(): use readLrBytes(2)/skipToNextLr()/tellLr() twice with seekLr(0)."""
        self.assertEqual(self._pr.tellLr(), 0)
        # First logical record
        self.assertEqual(self._pr.readLrBytes(2), bytes(range(2)))
        self.assertEqual(self._pr.tellLr(), 0)
        self._pr.skipToNextLr()
        self.assertEqual(self._pr.readLrBytes(2), bytes(range(4,4+2)))
        self.assertEqual(self._pr.tellLr(), 4*2 + 4)
        self._pr.skipToNextLr()
        self.assertEqual(self._pr.readLrBytes(2), bytes(range(4+14,4+14+2)))
        self.assertEqual(self._pr.tellLr(), 4*5 + 4 + 14)
        self._pr.skipToNextLr()
#        try:
#            self._pr.skipToNextLr()
#            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
#        except PhysRec.ExceptionPhysRecEOF:
#            pass
        self.assertTrue(self._pr.isEOF)
        # All over again
        self._pr.seekLr(0)
        self.assertEqual(self._pr.tellLr(), 0)
        # First logical record
        self.assertEqual(self._pr.readLrBytes(2), bytes(range(2)))
        self.assertEqual(self._pr.tellLr(), 0)
        self._pr.skipToNextLr()
        self.assertEqual(self._pr.readLrBytes(2), bytes(range(4,4+2)))
        self.assertEqual(self._pr.tellLr(), 4*2 + 4)
        self._pr.skipToNextLr()
        self.assertEqual(self._pr.readLrBytes(2), bytes(range(4+14,4+14+2)))
        self.assertEqual(self._pr.tellLr(), 4*5 + 4 + 14)
        self._pr.skipToNextLr()
#        try:
#            self._pr.skipToNextLr()
#            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
#        except PhysRec.ExceptionPhysRecEOF:
#            pass
        self.assertTrue(self._pr.isEOF)


@pytest.mark.slow
class TestPhysRecWriteRead_PerfBase(BaseTestClasses.TestBase):
    """Writes a PR then times how long it takes to read it."""
    def _writeToFile(self, prLen, lrLen, lrNum):
        myFi = io.BytesIO()
        #myFi.write(b'asd')
        myPrw = PhysRec.PhysRecWrite(
            myFi,
            theFileId='WriteFile',
            keepGoing=False,
            hasTif=True,
            thePrLen=prLen,
            thePrt=PhysRec.PhysRecTail(hasRecNum=True, fileNum=42, hasCheckSum=True),
        )
        for i in range(lrNum):
            myPrw.writeLr(b'\xff' * lrLen)
        return myFi

    def _readFile(self, theFile):
        myPrr = PhysRec.PhysRecRead(theFile=theFile, theFileId='MyFile', keepGoing=False)
        lrCount = 0
        while 1:
            myLd = myPrr.readLrBytes()
            if myLd is None:
                break
            lrCount += 1
        return lrCount


@pytest.mark.slow
class TestPhysRecWriteRead_Perf(TestPhysRecWriteRead_PerfBase):
    """Writes a PR then times how long it takes to read it."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPhysRecWriteRead_Perf.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPhysRecWriteRead_Perf.test_01(): Write single logical record."""
        myFi = self._writeToFile(1024, 1024, 1)
        #myPr.close()
        #print()
        #print('myFi.getvalue()', myFi.getvalue())
        myPrr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        myLd = myPrr.readLrBytes()
        #print('myLd', myLd)
        self.assertEqual(b'\xff' * 1024, myLd)

    def test_02(self):
        """TestPhysRecWriteRead_Perf.test_02(): 1k LRs that are 1kB."""
        prLen = 1024
        lrNum = 1024
        lrSize = 1024
        myFi = self._writeToFile(prLen, lrSize, lrNum)
        tS = time.perf_counter()
        lrCount = self._readFile(myFi)
        self.assertEqual(lrNum, lrCount)
        self.writeCostToStderr(tS, lrSize*lrNum, 'PR len', prLen)

    def test_03(self):
        """TestPhysRecWriteRead_Perf.test_03(): 1k LRs that are 8kB."""
        prLen = 1024
        lrNum = 1024
        lrSize = 8 * 1024
        myFi = self._writeToFile(prLen, lrSize, lrNum)
        tS = time.perf_counter()
        lrCount = self._readFile(myFi)
        self.assertEqual(lrNum, lrCount)
        self.writeCostToStderr(tS, lrSize*lrNum, 'PR len', prLen)

    def test_03_01(self):
        """TestPhysRecWriteRead_Perf.test_03_01():  128 LRs that are 64kB, 128B PRs."""
        prLen = 128
        lrSize = 64 * 1024
        lrNum = 128
        myFi = self._writeToFile(prLen, lrSize, lrNum)
        tS = time.perf_counter()
        lrCount = self._readFile(myFi)
        self.assertEqual(lrNum, lrCount)
        self.writeCostToStderr(tS, lrSize*lrNum, 'PR len', prLen)

    def test_03_02(self):
        """TestPhysRecWriteRead_Perf.test_03_02():  128 LRs that are 64kB, 256B PRs."""
        prLen = 256
        lrSize = 64 * 1024
        lrNum = 128
        myFi = self._writeToFile(prLen, lrSize, lrNum)
        tS = time.perf_counter()
        lrCount = self._readFile(myFi)
        self.assertEqual(lrNum, lrCount)
        self.writeCostToStderr(tS, lrSize*lrNum, 'PR len', prLen)

    def test_03_03(self):
        """TestPhysRecWriteRead_Perf.test_03_03():  128 LRs that are 64kB, 512B PRs."""
        prLen = 512
        lrSize = 64 * 1024
        lrNum = 128
        myFi = self._writeToFile(prLen, lrSize, lrNum)
        tS = time.perf_counter()
        lrCount = self._readFile(myFi)
        self.assertEqual(lrNum, lrCount)
        self.writeCostToStderr(tS, lrSize*lrNum, 'PR len', prLen)

    def test_03_04(self):
        """TestPhysRecWriteRead_Perf.test_03_04():  128 LRs that are 64kB, 1kB PRs."""
        prLen = 1024
        lrSize = 64 * 1024
        lrNum = 128
        myFi = self._writeToFile(prLen, lrSize, lrNum)
        tS = time.perf_counter()
        lrCount = self._readFile(myFi)
        self.assertEqual(lrNum, lrCount)
        self.writeCostToStderr(tS, lrSize*lrNum, 'PR len', prLen)

    def test_03_05(self):
        """TestPhysRecWriteRead_Perf.test_03_05():  128 LRs that are 64kB, 2kB PRs."""
        prLen = 2 * 1024
        lrSize = 64 * 1024
        lrNum = 128
        myFi = self._writeToFile(prLen, lrSize, lrNum)
        tS = time.perf_counter()
        lrCount = self._readFile(myFi)
        self.assertEqual(lrNum, lrCount)
        self.writeCostToStderr(tS, lrSize*lrNum, 'PR len', prLen)

    def test_03_06(self):
        """TestPhysRecWriteRead_Perf.test_03_06():  128 LRs that are 64kB, 4kB PRs."""
        prLen = 4 * 1024
        lrSize = 64 * 1024
        lrNum = 128
        myFi = self._writeToFile(prLen, lrSize, lrNum)
        tS = time.perf_counter()
        lrCount = self._readFile(myFi)
        self.assertEqual(lrNum, lrCount)
        self.writeCostToStderr(tS, lrSize*lrNum, 'PR len', prLen)

    def test_03_07(self):
        """TestPhysRecWriteRead_Perf.test_03_07():  128 LRs that are 64kB, 8kB PRs."""
        prLen = 8 * 1024
        lrSize = 64 * 1024
        lrNum = 128
        myFi = self._writeToFile(prLen, lrSize, lrNum)
        tS = time.perf_counter()
        lrCount = self._readFile(myFi)
        self.assertEqual(lrNum, lrCount)
        self.writeCostToStderr(tS, lrSize*lrNum, 'PR len', prLen)

    def test_03_08(self):
        """TestPhysRecWriteRead_Perf.test_03_08():  128 LRs that are 64kB, 16kB PRs."""
        prLen = 16 * 1024
        lrSize = 64 * 1024
        lrNum = 128
        myFi = self._writeToFile(prLen, lrSize, lrNum)
        tS = time.perf_counter()
        lrCount = self._readFile(myFi)
        self.assertEqual(lrNum, lrCount)
        self.writeCostToStderr(tS, lrSize*lrNum, 'PR len', prLen)

    def test_03_09(self):
        """TestPhysRecWriteRead_Perf.test_03_09():  128 LRs that are 64kB, 32kB PRs."""
        prLen = 32 * 1024
        lrSize = 64 * 1024
        lrNum = 128
        myFi = self._writeToFile(prLen, lrSize, lrNum)
        tS = time.perf_counter()
        lrCount = self._readFile(myFi)
        self.assertEqual(lrNum, lrCount)
        self.writeCostToStderr(tS, lrSize*lrNum, 'PR len', prLen)

    def test_03_10(self):
        """TestPhysRecWriteRead_Perf.test_03_10():  128 LRs that are 64kB, 64kB PRs."""
        # TODO: Set max PR len properly
        prLen = PhysRec.PR_MAX_LENGTH
        lrSize = 64 * 1024
        lrNum = 128
        myFi = self._writeToFile(prLen, lrSize, lrNum)
        tS = time.perf_counter()
        lrCount = self._readFile(myFi)
        self.assertEqual(lrNum, lrCount)
        self.writeCostToStderr(tS, lrSize*lrNum, 'PR len', prLen)

    def test_04(self):
        """TestPhysRecWriteRead_Perf.test_04(): 8k LRs that are 8kB."""
        prLen = 1024
        lrSize = 8 * 1024
        lrNum = 8 * 1024
        myFi = self._writeToFile(prLen, lrSize, lrNum)
        tS = time.perf_counter()
        lrCount = self._readFile(myFi)
        self.assertEqual(lrNum, lrCount)
        self.writeCostToStderr(tS, lrSize*lrNum, 'PR len', prLen)


@pytest.mark.slow
class Special_Perf(TestPhysRecWriteRead_PerfBase):
    """Special tests."""
    pass

#    def test_01(self):
#        """TestPhysRecWriteRead_Perf.test_01(): Write single logical record."""
#        myFi = self._writeToFile(prLen=1024, lrLen=16, lrNum=1)
#        #myPr.close()
#        #print()
#        #print('myFi.getvalue()', myFi.getvalue())
#        #print('myFi.getvalue()', [x for x in myFi.getvalue()])
#        myPrr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
#        myLd = myPrr.readLrBytes()
#        #print('myLd', myLd)
#        self.assertEqual(b'\xff' * 16, myLd)
#
#    def test_03_01(self):
#        """TestPhysRecWriteRead_Perf.test_03_01():  128 LRs that are 8kB, 128B PRs."""
#        prLen = 128
#        lrSize = 64 * 1024
#        lrNum = 128
#        myFi = self._writeToFile(prLen, lrSize, lrNum)
#        tS = time.perf_counter()
#        lrCount = self._readFile(myFi)
#        self.assertEqual(lrNum, lrCount)
#        self.writeCostToStderr(tS, lrSize*lrNum, 'PR len', prLen)

    def test_03_10(self):
        """TestPhysRecWriteRead_Perf.test_03_10():  128 LRs that are 64kB, 64kB PRs."""
        # TODO: Set max PR len properly
        prLen = PhysRec.PR_MAX_LENGTH
        lrSize = 64 * 1024
        lrNum = 128
        myFi = self._writeToFile(prLen, lrSize, lrNum)
        tS = time.perf_counter()
        lrCount = self._readFile(myFi)
        self.assertEqual(lrNum, lrCount)
        self.writeCostToStderr(tS, lrSize*lrNum, 'PR len', prLen)

class Special(unittest.TestCase):
    """Special tests."""
    pass

    def test_03(self):
        """TestPhysRecMultipleRead.test_03(): Single logical data, two physical records, read one byte at a time."""
        myFi = io.BytesIO(
            # First PR, has a single logical byte
            b'\x00\x05' \
            + b'\x00\x01' \
            + b'\x00' \
            # Second PR, has a three logical bytes
            + b'\x00\x07' \
            + b'\x00\x02' \
            + b'\x01\x02\x03'
        )
        myPr = PhysRec.PhysRecRead(theFile=myFi, theFileId='MyFile', keepGoing=False)
        #print
        #for i in range(4):
        #    print(myPr.readLrBytes(1))
        #return
        #assert(0)
        myLd = bytes()
        for i in range(4):
            myLd = myPr.readLrBytes(1, myLd)
        self.assertEqual(len(myLd), 4)
        self.assertEqual(myLd, b'\x00\x01\x02\x03')
        self.assertTrue(myPr.readLrBytes() is None)
#        try:
#            myPr.skipToNextLr()
#            self.fail('PhysRec.ExceptionPhysRec not raised on EOF')
#        except PhysRec.ExceptionPhysRecEOF:
#            pass
        myPr.skipToNextLr()
        self.assertTrue(myPr.isEOF)

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
#    suite = unittest.TestLoader().loadTestsFromTestCase(Special_Perf)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPhysRecLowLevel))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPhysRecSingleRead))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPhysRecTrailer))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPhysRecFail))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPhysRecSingleReadWithTif))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPhysRecMultipleRead))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPhysRecMultipleReadWithTif))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPhysRecGenLd))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPhysRecMultipleSkip))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPhysRecRandomAccessLogicalData))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPhysRecWriteRead_Perf))
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
