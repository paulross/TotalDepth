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
"""Tests LogiRec module.
"""

__author__  = 'Paul Ross'
__date__    = '29 Dec 2010'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'

import os
import sys
import time
import logging
import io
import pprint
import random

from TotalDepth.LIS.core import PhysRec
from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import EngVal
from TotalDepth.LIS.core import RepCode
from TotalDepth.LIS.core import Units
from TotalDepth.LIS.core import Mnem

######################
# Section: Unit tests.
######################
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import BaseTestClasses

#class TestLrBase(unittest.TestCase):
#    def _retFileSinglePr(self, theB):
#        """Given a bytes() object this returns a file with them encapsulated in a single Physical Record."""
#        myBy = io.BytesIO(
#            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(theB)) \
#            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
#            + theB
#            # Absent Physical Record trailer
#        )
#        return File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)

class TestLrBase(BaseTestClasses.TestBaseFile):
    pass

class TestLrBaseClass(TestLrBase):
    """Tests LrBase class."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestLrBaseClass.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestLrBaseClass.test_01(): basic API."""
        for lrType in LogiRec.LR_TYPE_ALL:
            myLr = LogiRec.LrBase(lrType, 0)
            self.assertEqual(lrType, myLr.type)
            self.assertEqual(0, myLr.attr)
            self.assertEqual(LogiRec.LR_DESCRIPTION_MAP[lrType], myLr.desc)
            str(myLr)
        
    def test_02(self):
        """TestLrBaseClass.test_02(): random unknown LR types."""
        for i in range(1024):
            lrType = random.randint(0, 255)
            if lrType not in LogiRec.LR_TYPE_ALL:
                myLr = LogiRec.LrBase(lrType, 0)
                self.assertEqual(lrType, myLr.type)
                self.assertEqual(0, myLr.attr)
                self.assertEqual(LogiRec.LR_DESCRIPTION_UNKNOWN, myLr.desc)
                str(myLr)

class TestLrMarker(unittest.TestCase):
    """Tests Marker logical records (EOF BOT EOT EOM)"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestLrMarker: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestLrMarker.test_00(): EOF."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 2) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x89\x00' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrEOFRead(myFile)
        self.assertEqual(myLr.desc, 'Logical EOF (end of file)')

    def test_01(self):
        """TestLrMarker.test_01(): BOT."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 2) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x8A\x00' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrBOTRead(myFile)
        self.assertEqual(myLr.desc, 'Logical BOT (beginning of tape)')

    def test_02(self):
        """TestLrMarker.test_02(): EOT."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 2) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x8B\x00' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrEOTRead(myFile)
        self.assertEqual(myLr.desc, 'Logical EOT (end of tape)')

    def test_03(self):
        """TestLrMarker.test_03(): EOM."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 2) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x8D\x00' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrEOMRead(myFile)
        self.assertEqual(myLr.desc, 'Logical EOM (end of medium)')

class TestLrWithDateField(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestCLass: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestLrWithDateField.test_00(): LrFileHead.ymd blank field fails."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 58) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x80\x00RUNOne.lis\x00\x00SubLevVers num' \
            # Date
            + b'        ' \
            + b'\x00 1024\x00\x00\x41\x42\x00\x00Prev name.'
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrFileHeadRead(myFile)
        self.assertEqual(myLr.date, b'        ')
        self.assertTrue(myLr.ymd is None)

    def test_01(self):
        """TestLrWithDateField.test_01(): LrFileHead.ymd '  /  /  ' fails."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 58) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x80\x00RUNOne.lis\x00\x00SubLevVers num' \
            # Date
            + b'  /  /  ' \
            + b'\x00 1024\x00\x00\x41\x42\x00\x00Prev name.'
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrFileHeadRead(myFile)
        self.assertEqual(myLr.date, b'  /  /  ')
        self.assertTrue(myLr.ymd is None)

    def test_02(self):
        """TestLrWithDateField.test_02(): LrFileHead.ymd with garbage characters fails."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 58) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x80\x00RUNOne.lis\x00\x00SubLevVers num' \
            # Date
            + b'\x00\x00/\x00\x00/\x00\x00' \
            + b'\x00 1024\x00\x00\x41\x42\x00\x00Prev name.'
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrFileHeadRead(myFile)
        self.assertEqual(myLr.date, b'\x00\x00/\x00\x00/\x00\x00')
        self.assertTrue(myLr.ymd is None)

    def test_10(self):
        """TestLrWithDateField.test_10(): LrFileHead.ymd 78 is 1978."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 58) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x80\x00RUNOne.lis\x00\x00SubLevVers num' \
            # Date
            + b'78/03/15' \
            + b'\x00 1024\x00\x00\x41\x42\x00\x00Prev name.'
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrFileHeadRead(myFile)
        self.assertEqual(myLr.date, b'78/03/15')
        self.assertEqual(myLr.ymd, (1978, 3, 15))

    def test_11(self):
        """TestLrWithDateField.test_11(): LrFileHead.ymd 00 is 2000."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 58) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x80\x00RUNOne.lis\x00\x00SubLevVers num' \
            # Date
            + b'00/03/15' \
            + b'\x00 1024\x00\x00\x41\x42\x00\x00Prev name.'
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrFileHeadRead(myFile)
        self.assertEqual(myLr.date, b'00/03/15')
        self.assertEqual(myLr.ymd, (2000, 3, 15))

    def test_12(self):
        """TestLrWithDateField.test_11(): LrFileHead.ymd 26 is 2026."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 58) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x80\x00RUNOne.lis\x00\x00SubLevVers num' \
            # Date
            + b'26/03/15' \
            + b'\x00 1024\x00\x00\x41\x42\x00\x00Prev name.'
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrFileHeadRead(myFile)
        self.assertEqual(myLr.date, b'26/03/15')
        self.assertEqual(myLr.ymd, (2026, 3, 15))

    def test_13(self):
        """TestLrWithDateField.test_13(): LrFileHead.ymd 27 is 1927."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 58) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x80\x00RUNOne.lis\x00\x00SubLevVers num' \
            # Date
            + b'27/03/15' \
            + b'\x00 1024\x00\x00\x41\x42\x00\x00Prev name.'
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrFileHeadRead(myFile)
        self.assertEqual(myLr.date, b'27/03/15')
        self.assertEqual(myLr.ymd, (1927, 3, 15))

    def test_14(self):
        """TestLrWithDateField.test_14(): LrFileHead.ymd 28 is 1928."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 58) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x80\x00RUNOne.lis\x00\x00SubLevVers num' \
            # Date
            + b'28/03/15' \
            + b'\x00 1024\x00\x00\x41\x42\x00\x00Prev name.'
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrFileHeadRead(myFile)
        self.assertEqual(myLr.date, b'28/03/15')
        self.assertEqual(myLr.ymd, (1928, 3, 15))

    def test_15(self):
        """TestLrWithDateField.test_14(): LrFileHead.ymd 99 is 1999."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 58) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x80\x00RUNOne.lis\x00\x00SubLevVers num' \
            # Date
            + b'99/03/15' \
            + b'\x00 1024\x00\x00\x41\x42\x00\x00Prev name.'
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrFileHeadRead(myFile)
        self.assertEqual(myLr.date, b'99/03/15')
        self.assertEqual(myLr.ymd, (1999, 3, 15))

class TestLrFileHeadTail(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestCLass: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestLrFileHeadTail.test_00(): File head."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 58) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x80\x00' \
            # File name 6.3 format
            + b'RUNOne.lis' \
            # Two blanks
            + b'\x00\x00' \
            # Service sub-level name
            + b'SubLev' \
            # Version number
            + b'Vers num' \
            # Date
            + b'78/03/15' \
            # One blank
            + b'\x00' \
            # Max Physical record length
            + b' 1024' \
            # Two blanks
            + b'\x00\x00' \
            # File Type
            + b'\x41\x42' \
            # Two blanks
            + b'\x00\x00' \
            # Previous file name
            + b'Prev name.'
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrFileHeadRead(myFile)
        self.assertEqual(myLr.desc, 'File header')
        self.assertEqual(myLr.fileName, b'RUNOne.lis')
        self.assertEqual(myLr.serviceSubLevel, b'SubLev')
        self.assertEqual(myLr.version, b'Vers num')
        self.assertEqual(myLr.date, b'78/03/15')
        self.assertEqual(myLr.ymd, (1978, 3, 15))
        self.assertEqual(myLr.maxPrLength, b' 1024')
        self.assertEqual(myLr.fileType, b'AB')
        self.assertEqual(myLr.prevFileName, b'Prev name.')

    def test_10(self):
        """TestLrFileHeadTail.test_00(): File tail."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 58) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x81\x00' \
            # File name 6.3 format
            + b'RUNOne.lis' \
            # Two blanks
            + b'\x00\x00' \
            # Service sub-level name
            + b'SubLev' \
            # Version number
            + b'Vers num' \
            # Date
            + b'78/03/15' \
            # One blank
            + b'\x00' \
            # Max Physical record length
            + b' 1024' \
            # Two blanks
            + b'\x00\x00' \
            # File Type
            + b'\x41\x42' \
            # Two blanks
            + b'\x00\x00' \
            # Previous file name
            + b'Next name.'
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrFileTailRead(myFile)
        self.assertEqual(myLr.desc, 'File trailer')
        self.assertEqual(myLr.fileName, b'RUNOne.lis')
        self.assertEqual(myLr.serviceSubLevel, b'SubLev')
        self.assertEqual(myLr.version, b'Vers num')
        self.assertEqual(myLr.date, b'78/03/15')
        self.assertEqual(myLr.ymd, (1978, 3, 15))
        self.assertEqual(myLr.maxPrLength, b' 1024')
        self.assertEqual(myLr.fileType, b'AB')
        self.assertEqual(myLr.nextFileName, b'Next name.')

class TestLrTapeHeadTail(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestLrTapeHeadTail: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestLrTapeHeadTail.test_00(): Tape head."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 128) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x82\x00' \
            # Service name
            + b'SERVCE' \
            # 
            + b'\x00\x00\x00\x00\x00\x00' \
            # 
            + b'79/06/15' \
            # 
            + b'\x00\x00' \
            # Origin
            + b'ORGN' \
            # 
            + b'\x00\x00' \
            # Tape name
            + b'TAPENAME' \
            # 
            + b'\x00\x00' \
            # Tape continuation number
            + b'01' \
            # 
            + b'\x00\x00' \
            # Previous tape name
            + b'PrevName' \
            # 
            + b'\x00\x00' \
            # Comments, 74 characters
            + b'_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123'
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrTapeHeadRead(myFile)
        self.assertEqual(myLr.desc, 'Tape header')
        self.assertEqual(myLr.serviceName, b'SERVCE')
        self.assertEqual(myLr.date, b'79/06/15')
        self.assertEqual(myLr.ymd, (1979, 6, 15))
        self.assertEqual(myLr.origin, b'ORGN')
        self.assertEqual(myLr.name, b'TAPENAME')
        self.assertEqual(myLr.contNumber, b'01')
        self.assertEqual(myLr.prevTapeName, b'PrevName')
        self.assertEqual(myLr.comments, b'_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123')

    def test_10(self):
        """TestLrTapeHeadTail.test_00(): Tape tail."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 128) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x83\x00' \
            # Service name
            + b'SERVCE' \
            # 
            + b'\x00\x00\x00\x00\x00\x00' \
            # 
            + b'79/06/15' \
            # 
            + b'\x00\x00' \
            # Origin
            + b'ORGN' \
            # 
            + b'\x00\x00' \
            # Tape name
            + b'TAPENAME' \
            # 
            + b'\x00\x00' \
            # Tape continuation number
            + b'01' \
            # 
            + b'\x00\x00' \
            # Next tape name
            + b'NextName' \
            # 
            + b'\x00\x00' \
            # Comments, 74 characters
            + b'_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123'
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrTapeTailRead(myFile)
        self.assertEqual(myLr.desc, 'Tape trailer')
        self.assertEqual(myLr.serviceName, b'SERVCE')
        self.assertEqual(myLr.date, b'79/06/15')
        self.assertEqual(myLr.ymd, (1979, 6, 15))
        self.assertEqual(myLr.origin, b'ORGN')
        self.assertEqual(myLr.name, b'TAPENAME')
        self.assertEqual(myLr.contNumber, b'01')
        self.assertEqual(myLr.nextTapeName, b'NextName')
        self.assertEqual(myLr.comments, b'_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123')

class TestLrReelHeadTail(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestLrReelHeadTail: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestLrReelHeadTail.test_00(): Reel head."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 128) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x84\x00' \
            # Service name
            + b'SERVCE' \
            # 
            + b'\x00\x00\x00\x00\x00\x00' \
            # 
            + b'79/06/15' \
            # 
            + b'\x00\x00' \
            # Origin
            + b'ORGN' \
            # 
            + b'\x00\x00' \
            # Reel name
            + b'REELNAME' \
            # 
            + b'\x00\x00' \
            # Reel continuation number
            + b'01' \
            # 
            + b'\x00\x00' \
            # Previous reel name
            + b'PrevName' \
            # 
            + b'\x00\x00' \
            # Comments, 74 characters
            + b'_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123'
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrReelHeadRead(myFile)
        self.assertEqual(myLr.desc, 'Reel header')
        self.assertEqual(myLr.serviceName, b'SERVCE')
        self.assertEqual(myLr.date, b'79/06/15')
        self.assertEqual(myLr.ymd, (1979, 6, 15))
        self.assertEqual(myLr.origin, b'ORGN')
        self.assertEqual(myLr.name, b'REELNAME')
        self.assertEqual(myLr.contNumber, b'01')
        self.assertEqual(myLr.prevReelName, b'PrevName')
        self.assertEqual(myLr.comments, b'_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123')

    def test_10(self):
        """TestLrReelHeadTail.test_00(): Reel tail."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 128) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x85\x00' \
            # Service name
            + b'SERVCE' \
            # 
            + b'\x00\x00\x00\x00\x00\x00' \
            # 
            + b'79/06/15' \
            # 
            + b'\x00\x00' \
            # Origin
            + b'ORGN' \
            # 
            + b'\x00\x00' \
            # Reel name
            + b'REELNAME' \
            # 
            + b'\x00\x00' \
            # Reel continuation number
            + b'01' \
            # 
            + b'\x00\x00' \
            # Previous reel name
            + b'NextName' \
            # 
            + b'\x00\x00' \
            # Comments, 74 characters
            + b'_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123'
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        myLr = LogiRec.LrReelTailRead(myFile)
        self.assertEqual(myLr.desc, 'Reel trailer')
        self.assertEqual(myLr.serviceName, b'SERVCE')
        self.assertEqual(myLr.date, b'79/06/15')
        self.assertEqual(myLr.ymd, (1979, 6, 15))
        self.assertEqual(myLr.origin, b'ORGN')
        self.assertEqual(myLr.name, b'REELNAME')
        self.assertEqual(myLr.contNumber, b'01')
        self.assertEqual(myLr.nextReelName, b'NextName')
        self.assertEqual(myLr.comments, b'_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123')
        # File is consumed
        self.assertFalse(myFile.hasLd())

class TestLrMisc(TestLrBase):
    """Tests misc logical records."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestLrMisc: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestLrMisc.test_00(): All LR_TYPE_UNKNOWN_INTERNAL_FORMAT with random bytes."""
        for lrType in LogiRec.LR_TYPE_UNKNOWN_INTERNAL_FORMAT:
            myPayload = self.randomBytes()
            myFi = self._retFilePrS(bytes([lrType, 0]) + myPayload)
            myLr = LogiRec.LrMiscRead(myFi)
            self.assertEqual(LogiRec.LR_DESCRIPTION_MAP[lrType] , myLr.desc)
            self.assertEqual(len(myPayload), len(myLr.bytes))
            self.assertEqual(myPayload, myLr.bytes)

class TestCbEngValRead(TestLrBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestCbEngValRead: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestCbEngValRead.test_00(): Read string component block."""
        myB = bytes([73, 65, 4, 0]) \
            + bytes('TYPE', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('FILM', 'ascii')
        myF = self._retFileSinglePr(myB)
        myCbev = LogiRec.CbEngValRead(myF)
        self.assertEqual(myCbev.type, 73)
        self.assertEqual(myCbev.rc, 65)
        self.assertEqual(myCbev.size, 4)
        self.assertEqual(myCbev.category, 0)
        self.assertEqual(myCbev.mnem, b'TYPE')
        self.assertEqual(myCbev.units, b'    ')
        self.assertEqual(myCbev.engVal.value, b'FILM')
        self.assertEqual(myCbev.engVal.uom, b'    ')
        self.assertEqual(myCbev.engVal.rc, 65)
        self.assertEqual(myCbev.engVal, EngVal.EngValRc(b'FILM', b'    ', 65))
        # Check file is consumed
        self.assertFalse(myF.hasLd())
        
    def test_01(self):
        """TestCbEngValRead.test_01(): Read Component block with repcode 68 and unit conversion."""
        myB = bytes([69, 68, 4, 0]) \
            + bytes('LENG', 'ascii') \
            + bytes('M   ', 'ascii') \
            + b'\x44\x4c\x80\x00'
        myF = self._retFileSinglePr(myB)
        myCbev = LogiRec.CbEngValRead(myF)
        self.assertEqual(myCbev.type, 69)
        self.assertEqual(myCbev.rc, 68)
        self.assertEqual(myCbev.size, 4)
        self.assertEqual(myCbev.category, 0)
        self.assertEqual(myCbev.mnem, b'LENG')
        self.assertEqual(myCbev.units, b'M   ')
        self.assertEqual(myCbev.engVal.value, 153.0)
        self.assertEqual(myCbev.engVal.uom, b'M   ')
        self.assertEqual(myCbev.engVal.rc, 68)
        self.assertEqual(myCbev.engVal, EngVal.EngValRc(153.0, b'M   ', 68))
        #print()
        #print(EngVal.EngValRc(153.0*0.3048, b'FT  ', 68))
        self.assertTrue(myCbev.engVal == EngVal.EngValRc(153.0 / 0.3048, b'FT  ', 68))
        # Check file is consumed
        self.assertFalse(myF.hasLd())
        
class TestCbEngValWrite(TestLrBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestCbEngValWrite: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestCbEngValWrite.test_00(): Create a component block with bytes."""
        myCbev = LogiRec.CbEngValWrite(69, b'E2E ', b'GCOD')
#        print('')
#        print(myCbev)
        self.assertEqual(69, myCbev.type)
        self.assertEqual(65, myCbev.rc)
        self.assertEqual(4, myCbev.size)
        self.assertEqual(b'E2E ', myCbev.value)
        self.assertEqual(b'GCOD', myCbev.mnem)
        self.assertEqual(b'    ', myCbev.units)

    def test_01(self):
        """TestCbEngValWrite.test_01(): Create a component block dimensionless float."""
        myCbev = LogiRec.CbEngValWrite(69, -999.25, b'ABSV')
#        print('')
#        print(myCbev)
        self.assertEqual(69, myCbev.type)
        self.assertEqual(68, myCbev.rc)
        self.assertEqual(4, myCbev.size)
        self.assertEqual(-999.25, myCbev.value)
        self.assertEqual(b'ABSV', myCbev.mnem)
        self.assertEqual(b'    ', myCbev.units)

    def test_02(self):
        """TestCbEngValWrite.test_02(): Create a component block dimensioned float."""
        myCbev = LogiRec.CbEngValWrite(69, 42., b'LENG', units=b'INCH')
#        print('')
#        print(myCbev)
        self.assertEqual(69, myCbev.type)
        self.assertEqual(68, myCbev.rc)
        self.assertEqual(4, myCbev.size)
        self.assertEqual(42.0, myCbev.value)
        self.assertEqual(b'LENG', myCbev.mnem)
        self.assertEqual(b'INCH', myCbev.units)

    def test_03(self):
        """TestCbEngValWrite.test_03(): Create a component block dimensionless int=0."""
        myCbev = LogiRec.CbEngValWrite(69, 0, b'LENG')
#        print('')
#        print(myCbev)
        self.assertEqual(69, myCbev.type)
        self.assertEqual(66, myCbev.rc)
        self.assertEqual(1, myCbev.size)
        self.assertEqual(0, myCbev.value)
        self.assertEqual(b'LENG', myCbev.mnem)
        self.assertEqual(b'    ', myCbev.units)

    def test_04(self):
        """TestCbEngValWrite.test_04(): Create a component block dimensionless int=256."""
        myCbev = LogiRec.CbEngValWrite(69, 256, b'LENG')
#        print('')
#        print(myCbev)
        self.assertEqual(69, myCbev.type)
        self.assertEqual(79, myCbev.rc)
        self.assertEqual(2, myCbev.size)
        self.assertEqual(256, myCbev.value)
        self.assertEqual(b'LENG', myCbev.mnem)
        self.assertEqual(b'    ', myCbev.units)

    def test_05(self):
        """TestCbEngValWrite.test_05(): Create a component block dimensionless int=-1."""
        myCbev = LogiRec.CbEngValWrite(69, -1, b'LENG')
#        print('')
#        print(myCbev)
        self.assertEqual(69, myCbev.type)
        self.assertEqual(79, myCbev.rc)
        self.assertEqual(2, myCbev.size)
        self.assertEqual(-1, myCbev.value)
        self.assertEqual(b'LENG', myCbev.mnem)
        self.assertEqual(b'    ', myCbev.units)

    def test_06(self):
        """TestCbEngValWrite.test_06(): Create a component block dimensionless int=2**16."""
        myCbev = LogiRec.CbEngValWrite(69, 2**16, b'LENG')
#        print('')
#        print(myCbev)
        self.assertEqual(69, myCbev.type)
        self.assertEqual(73, myCbev.rc)
        self.assertEqual(4, myCbev.size)
        self.assertEqual(2**16, myCbev.value)
        self.assertEqual(b'LENG', myCbev.mnem)
        self.assertEqual(b'    ', myCbev.units)

    def test_07(self):
        """TestCbEngValWrite.test_07(): Create a component block dimensionless int=-2**16."""
        myCbev = LogiRec.CbEngValWrite(69, -(2**16), b'LENG')
#        print('')
#        print(myCbev)
        self.assertEqual(69, myCbev.type)
        self.assertEqual(73, myCbev.rc)
        self.assertEqual(4, myCbev.size)
        self.assertEqual(-(2**16), myCbev.value)
        self.assertEqual(b'LENG', myCbev.mnem)
        self.assertEqual(b'    ', myCbev.units)

class TestTableRow(TestLrBase):
    """Tests LogiRec.TableRow"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestTableRow: Tests setUp() and tearDown()."""
        pass

    def _retCbEngValFromBytes(self, theB):
        myF = self._retFileSinglePr(theB)
        myCbev = LogiRec.CbEngValRead(myF)
        # Check file is consumed
        self.assertFalse(myF.hasLd())
        return myCbev

    def test_00(self):
        """TestTableRow.test_00(): Test the construction of a TableRow."""
        myB = bytes([0, 65, 4, 0]) \
            + bytes('MNEM', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('1   ', 'ascii')
        myCbEv = self._retCbEngValFromBytes(myB)
        myTr = LogiRec.TableRow(myCbEv)
        self.assertEqual(myTr.value, b'1   ')
        self.assertEqual(len(myTr), 1)
        myB = bytes([69, 65, 4, 0]) \
            + bytes('GCOD', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('E2E ', 'ascii')
        myCbEv = self._retCbEngValFromBytes(myB)
        myTr.addCb(myCbEv)
        self.assertEqual(len(myTr), 2)
        myB = bytes([69, 65, 4, 0]) \
            + bytes('GDEC', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('2   ', 'ascii')
        myCbEv = self._retCbEngValFromBytes(myB)
        myTr.addCb(myCbEv)
        self.assertEqual(len(myTr), 3)
        myB = bytes([69, 65, 4, 0]) \
            + bytes('DEST', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('PF1 ', 'ascii')
        myCbEv = self._retCbEngValFromBytes(myB)
        myTr.addCb(myCbEv)
        self.assertEqual(len(myTr), 4)
        myB = bytes([69, 65, 4, 0]) \
            + bytes('DSCA', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('S5  ', 'ascii')
        myCbEv = self._retCbEngValFromBytes(myB)
        myTr.addCb(myCbEv)
        self.assertEqual(len(myTr), 5)
        self.assertEqual(myTr.value, b'1   ')
        # Try get by lable
        myCbEv = myTr[b'DEST']
        self.assertEqual(myCbEv.type, 69)
        self.assertEqual(myCbEv.rc, 65)
        self.assertEqual(myCbEv.size, 4)
        self.assertEqual(myCbEv.category, 0)
        self.assertEqual(myCbEv.mnem, b'DEST')
        self.assertEqual(myCbEv.units, b'    ')
        self.assertEqual(myCbEv.engVal.value, b'PF1 ')
        self.assertEqual(myCbEv.engVal.uom, b'    ')
        self.assertEqual(myCbEv.engVal.rc, 65)
        self.assertEqual(myCbEv.engVal, EngVal.EngValRc(b'PF1 ', b'    ', 65))

    def test_01(self):
        """TestTableRow.test_01(): TableRow fails starting with type 1 block."""
        myB = bytes([1, 65, 4, 0]) \
            + bytes('MNEM', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('1   ', 'ascii')
        myCbEv = self._retCbEngValFromBytes(myB)
        self.assertRaises(LogiRec.ExceptionLrTableRowInit, LogiRec.TableRow, myCbEv)

    def test_02(self):
        """TestTableRow.test_02(): TableRow fails with entry that is a type 1 block."""
        myB = bytes([0, 65, 4, 0]) \
            + bytes('MNEM', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('1   ', 'ascii')
        myCbEv = self._retCbEngValFromBytes(myB)
        myTr = LogiRec.TableRow(myCbEv)
        self.assertEqual(myTr.value, b'1   ')
        self.assertEqual(len(myTr), 1)
        myB = bytes([1, 65, 4, 0]) \
            + bytes('GCOD', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('E2E ', 'ascii')
        myCbEv = self._retCbEngValFromBytes(myB)
        self.assertRaises(LogiRec.ExceptionLrTableRow, myTr.addCb, myCbEv)
        self.assertEqual(len(myTr), 1)

    def test_03(self):
        """TestTableRow.test_03(): TableRow __getitem__ failures."""
        myB = bytes([0, 65, 4, 0]) \
            + bytes('MNEM', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('1   ', 'ascii')
        myCbEv = self._retCbEngValFromBytes(myB)
        myTr = LogiRec.TableRow(myCbEv)
        self.assertEqual(myTr.value, b'1   ')
        self.assertEqual(len(myTr), 1)
        myB = bytes([69, 65, 4, 0]) \
            + bytes('GCOD', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('E2E ', 'ascii')
        myCbEv = self._retCbEngValFromBytes(myB)
        myTr.addCb(myCbEv)
        self.assertEqual(len(myTr), 2)
        # Try get by non-existent lable
        try:
            myTr[b'FOO ']
            self.fail('KeyError not raised.')
        except KeyError:
            pass
        # Try get by non-existent index
        try:
            myTr[7]
            self.fail('IndexError not raised.')
        except IndexError:
            pass
        # Get non-existent slice
        self.assertEqual(myTr[5:7], [])

    def test_05(self):
        """TestTableRow.test_05(): Duplicate cell in a TableRow."""
        myB = bytes([0, 65, 4, 0]) \
            + bytes('MNEM', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('1   ', 'ascii')
        myCbEv = self._retCbEngValFromBytes(myB)
        myTr = LogiRec.TableRow(myCbEv)
        self.assertEqual(myTr.value, b'1   ')
        self.assertEqual(len(myTr), 1)
        myB = bytes([69, 65, 4, 0]) \
            + bytes('GCOD', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('XXXX', 'ascii')
        myCbEv = self._retCbEngValFromBytes(myB)
        myTr.addCb(myCbEv)
        self.assertEqual(len(myTr), 2)
        myB = bytes([69, 65, 4, 0]) \
            + bytes('GCOD', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('YYYY', 'ascii')
        myCbEv = self._retCbEngValFromBytes(myB)
        myTr.addCb(myCbEv)
        self.assertEqual(len(myTr), 3)
        # This access should output an error
        myCbEv = myTr[b'GCOD']
        self.assertEqual(myCbEv.type, 69)
        self.assertEqual(myCbEv.rc, 65)
        self.assertEqual(myCbEv.size, 4)
        self.assertEqual(myCbEv.category, 0)
        self.assertEqual(myCbEv.mnem, b'GCOD')
        self.assertEqual(myCbEv.units, b'    ')
        # Not b'YYYY'
        self.assertEqual(myCbEv.engVal.value, b'XXXX')
        self.assertEqual(myCbEv.engVal.uom, b'    ')
        self.assertEqual(myCbEv.engVal.rc, 65)
        self.assertEqual(myCbEv.engVal, EngVal.EngValRc(b'XXXX', b'    ', 65))

    def test_06(self):
        """TestTableRow.test_07(): TableRow __contains__"""
        myB = bytes([0, 65, 4, 0]) \
            + bytes('MNEM', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('1   ', 'ascii')
        myCbEv = self._retCbEngValFromBytes(myB)
        myTr = LogiRec.TableRow(myCbEv)
        self.assertEqual(myTr.value, b'1   ')
        self.assertEqual(len(myTr), 1)
        myB = bytes([69, 65, 4, 0]) \
            + bytes('GCOD', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('E2E ', 'ascii')
        myCbEv = self._retCbEngValFromBytes(myB)
        myTr.addCb(myCbEv)
        self.assertEqual(len(myTr), 2)
        self.assertTrue(b'MNEM' in myTr)
        self.assertTrue(b'GCOD' in myTr)
        self.assertFalse(b'????' in myTr)

class TestLrTableSimple(TestLrBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        myB = bytes([34, 0]) \
            + bytes([73, 65, 4, 0]) \
            + bytes('TYPE', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('FILM', 'ascii') \
            + bytes([0, 65, 4, 0]) \
            + bytes('MNEM', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('1   ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('GCOD', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('E2E ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('GDEC', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('2   ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('DEST', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('PF1 ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('DSCA', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('S5  ', 'ascii') \
            + bytes([0, 65, 4, 0]) \
            + bytes('MNEM', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('2   ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('GCOD', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('BBB ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('GDEC', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('____', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('DEST', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('PF2 ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('DSCA', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('S5  ', 'ascii')
        myF = self._retFileSinglePr(myB)
        self._lrTable = LogiRec.LrTableRead(myF)

    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestLrTableSimple: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestLrTableSimple.test_00(): Two row table - construction and access."""
        self.assertEqual(self._lrTable.value, b'FILM')
        self.assertEqual(len(self._lrTable), 2)
        self.assertFalse(self._lrTable.isSingleParam)
        self.assertEqual(list(self._lrTable.rowLabels()), [b'1   ', b'2   '])
        self.assertEqual(self._lrTable.colLabels(), {b'MNEM', b'DEST', b'DSCA', b'GDEC', b'GCOD'})
        self.assertTrue(self._lrTable[b'1   '] is not None)
        self.assertEqual(len(self._lrTable[b'1   ']), 5)
        self.assertTrue(self._lrTable[b'2   '] is not None)
        self.assertEqual(len(self._lrTable[b'2   ']), 5)
        
    def test_01(self):
        """TestLrTableSimple.test_01(): Two row table - __contains__ using bytes object."""
        self.assertEqual(self._lrTable.value, b'FILM')
        self.assertEqual(len(self._lrTable), 2)
        self.assertFalse(self._lrTable.isSingleParam)
        self.assertTrue(b'1   ' in self._lrTable)
        self.assertTrue(b'2   ' in self._lrTable)
        self.assertFalse(b'3   ' in self._lrTable)

    def test_02(self):
        """TestLrTableSimple.test_02(): Two row table - __contains__ using Mnem.Mnem object."""
        self.assertEqual(self._lrTable.value, b'FILM')
        self.assertEqual(len(self._lrTable), 2)
        self.assertFalse(self._lrTable.isSingleParam)
        self.assertTrue(Mnem.Mnem(b'1   ') in self._lrTable)
        self.assertTrue(Mnem.Mnem(b'2   ') in self._lrTable)
        self.assertTrue(Mnem.Mnem(b'1\x00\x00\x00') in self._lrTable)
        self.assertTrue(Mnem.Mnem(b'2\x00\x00\x00') in self._lrTable)
        self.assertFalse(Mnem.Mnem(b'3   ') in self._lrTable)

    def test_03(self):
        """TestLrTableSimple.test_03(): Two row table - getRowByMnem() using Mnem.Mnem object."""
        self.assertEqual(self._lrTable.value, b'FILM')
        self.assertEqual(len(self._lrTable), 2)
        self.assertFalse(self._lrTable.isSingleParam)
        self.assertTrue(self._lrTable.retRowByMnem(Mnem.Mnem(b'1   ')) is not None)
        self.assertTrue(self._lrTable.retRowByMnem(Mnem.Mnem(b'2   ')) is not None)
        self.assertTrue(self._lrTable.retRowByMnem(Mnem.Mnem(b'1\x00\x00\x00')) is not None)
        self.assertTrue(self._lrTable.retRowByMnem(Mnem.Mnem(b'2\x00\x00\x00')) is not None)
        self.assertFalse(Mnem.Mnem(b'3   ') in self._lrTable)
        self.assertRaises(KeyError, self._lrTable.retRowByMnem, Mnem.Mnem(b'3   '))

    def test_04(self):
        """TestLrTableSimple.test_04(): Two row table - rowLabels() and rowMnems()."""
        self.assertEqual(self._lrTable.value, b'FILM')
        self.assertEqual(len(self._lrTable), 2)
        self.assertFalse(self._lrTable.isSingleParam)
        l = [b'1   ', b'2   ']
        self.assertEqual(l, sorted(self._lrTable.rowLabels()))
        self.assertEqual([Mnem.Mnem(v) for v in l], sorted(self._lrTable.rowMnems()))

    def test_10(self):
        """TestLrTableSimple.test_00(): Two row table - access failure."""
        try:
            self._lrTable[b'FOO ']
            self.fail('KeyError not raised.')
        except KeyError:
            pass
        # Try get by non-existent index
        try:
            self._lrTable[7]
            self.fail('IndexError not raised.')
        except IndexError:
            pass
        # Get non-existent slice
        self.assertEqual(self._lrTable[5:7], [])

class TestLrTableDupeRow(TestLrBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        myB = bytes([34, 0]) \
            + bytes([73, 65, 4, 0]) \
            + bytes('TYPE', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('FILM', 'ascii') \
            + bytes([0, 65, 4, 0]) \
            + bytes('MNEM', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('1   ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('GCOD', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('E2E ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('GDEC', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('2   ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('DEST', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('PF1 ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('DSCA', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('S5  ', 'ascii') \
            + bytes([0, 65, 4, 0]) \
            + bytes('MNEM', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('1   ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('GCOD', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('BBB ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('GDEC', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('____', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('DEST', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('PF2 ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('DSCA', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('S5  ', 'ascii')
        myF = self._retFileSinglePr(myB)
        self._lrTable = LogiRec.LrTableRead(myF)

    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestLrTableDupeRow: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestLrTableDupeRow.test_00(): Two row table with duplicate row - construction and access."""
        self.assertEqual(self._lrTable.value, b'FILM')
        self.assertEqual(len(self._lrTable), 1)
        self.assertFalse(self._lrTable.isSingleParam)
        self.assertEqual(list(self._lrTable.rowLabels()), [b'1   '])
        self.assertEqual(self._lrTable.colLabels(), {b'MNEM', b'DEST', b'DSCA', b'GDEC', b'GCOD'})
        self.assertTrue(self._lrTable[b'1   '] is not None)
        self.assertEqual(len(self._lrTable[b'1   ']), 5)
        try:
            self._lrTable[b'2   ']
            self.fail('KeyError not raised.')
        except KeyError:
            pass
        # Try get by non-existent second row
        try:
            self._lrTable[2]
            self.fail('IndexError not raised.')
        except IndexError:
            pass
        
    def test_10(self):
        """TestLrTableDupeRow.test_00(): Two row table with duplicate row - access failure."""
        try:
            self._lrTable[b'FOO ']
            self.fail('KeyError not raised.')
        except KeyError:
            pass
        # Try get by non-existent index
        try:
            self._lrTable[7]
            self.fail('IndexError not raised.')
        except IndexError:
            pass
        # Get non-existent slice
        self.assertEqual(self._lrTable[5:7], [])

class TestLrTableBadBlocks(TestLrBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestLrTableBadBlocks: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestLrTableBadBlocks.test_00(): Bad initial block type 99 raises LogiRec.ExceptionLrTableInit."""
        myB = bytes([34, 0]) \
            + bytes([99, 65, 4, 0]) \
            + bytes('TYPE', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('FILM', 'ascii')
        myF = self._retFileSinglePr(myB)
        self.assertRaises(LogiRec.ExceptionLrTableInit, LogiRec.LrTableRead, myF)
        
    def test_01(self):
        """TestLrTableBadBlocks.test_01(): Bad start row block type 12 raises LogiRec.ExceptionLrTableInit."""
        myB = bytes([34, 0]) \
            + bytes([73, 65, 4, 0]) \
            + bytes('TYPE', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('FILM', 'ascii') \
            + bytes([12, 65, 4, 0]) \
            + bytes('MNEM', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('1   ', 'ascii')
        myF = self._retFileSinglePr(myB)
        self.assertRaises(LogiRec.ExceptionLrTableInit, LogiRec.LrTableRead, myF)

    def test_02(self):
        """TestLrTableBadBlocks.test_02(): Missing start row block type 0 raises LogiRec.ExceptionLrTableInit."""
        myB = bytes([34, 0]) \
            + bytes([73, 65, 4, 0]) \
            + bytes('TYPE', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('FILM', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('GCOD', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('E2E ', 'ascii')
        myF = self._retFileSinglePr(myB)
        self.assertRaises(LogiRec.ExceptionLrTableInit, LogiRec.LrTableRead, myF)

    def test_03(self):
        """TestLrTableBadBlocks.test_03(): Spurious trailing bytes warns but does not raise."""
        myB = bytes([34, 0]) \
            + bytes([73, 65, 4, 0]) \
            + bytes('TYPE', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('FILM', 'ascii') \
            + bytes([0, 65, 4, 0]) \
            + bytes('MNEM', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('1   ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('GCOD', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('E2E ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('GDEC', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('2   ', 'ascii') \
            + bytes([0])
        myF = self._retFileSinglePr(myB)
        myLr = LogiRec.LrTableRead(myF)
        self.assertEqual(myLr.value, b'FILM')
        self.assertEqual(len(myLr), 1)
        self.assertFalse(myLr.isSingleParam)
        self.assertEqual(list(myLr.rowLabels()), [b'1   '])
        self.assertEqual(myLr.colLabels(), {b'MNEM', b'GDEC', b'GCOD'})
        self.assertTrue(myLr[b'1   '] is not None)
        self.assertEqual(len(myLr[b'1   ']), 3)

class TestLrTableSingleParameter(TestLrBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        myB = bytes([34, 0]) \
            + bytes([0, 65, 4, 0]) \
            + bytes('MNEM', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('1   ', 'ascii') \
            + bytes([0, 65, 4, 0]) \
            + bytes('MNEM', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('2   ', 'ascii')
        myF = self._retFileSinglePr(myB)
        self._lrTable = LogiRec.LrTableRead(myF)

    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestLrTableSingleParameter: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestLrTableSingleParameter.test_00(): Two row table - construction and access."""
        self.assertTrue(self._lrTable.value is None)
        self.assertEqual(len(self._lrTable), 2)
        self.assertTrue(self._lrTable.isSingleParam)
        self.assertEqual(list(self._lrTable.rowLabels()), [b'1   ', b'2   '])
        self.assertEqual(1, len(self._lrTable.colLabels()) )
        self.assertTrue(self._lrTable[b'1   '] is not None)
        self.assertEqual(len(self._lrTable[b'1   ']), 1)
        self.assertTrue(self._lrTable[b'2   '] is not None)
        self.assertEqual(len(self._lrTable[b'2   ']), 1)

    def test_01(self):
        """TestLrTableSingleParameter.test_01(): Two row table - construction and access failure."""
        try:
            self._lrTable[b'FOO ']
            self.fail('KeyError not raised.')
        except KeyError:
            pass
        # Try get by non-existent seventh row
        try:
            self._lrTable[7]
            self.fail('IndexError not raised.')
        except IndexError:
            pass
        # Get non-existent slice
        self.assertEqual(self._lrTable[5:7], [])

class TestLrTableSingleParameterIllFormed(TestLrBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass
    
    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestLrTableSingleParameterIllFormed: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestLrTableSingleParameterIllFormed.test_00(): Late type 69 block."""
        myB = bytes([34, 0]) \
            + bytes([0, 65, 4, 0]) \
            + bytes('MNEM', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('1   ', 'ascii') \
            + bytes([69, 65, 4, 0]) \
            + bytes('MNEM', 'ascii') \
            + bytes('    ', 'ascii') \
            + bytes('2   ', 'ascii')
        myF = self._retFileSinglePr(myB)
        #LogiRec.LrTableRead(myF)
        self.assertRaises(LogiRec.ExceptionLrTableInit, LogiRec.LrTableRead, myF)

class TestLrTableSpecific(TestLrBase):
    """Class to test specific tables."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestLrTableSpecific: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestLrTableSpecific.test_00(): PRES table."""
        myBy = b'"\x00' \
            + b'IA\x04\x00TYPE    PRES' \
                + b'\x00A\x04\x00MNEM    SP\x00\x00' \
                    + b'EA\x04\x00OUTP    SP  ' \
                    + b'EA\x04\x00STAT    ALLO' \
                    + b'EA\x04\x00TRAC    T1  ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    BOTH' \
                    + b'EA\x04\x00MODE    SHIF' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDGMV  \xbc0\x00\x00' \
                    + b'ED\x04\x00REDGMV  B\xd0\x00\x00' \
                + b'\x00A\x04\x00MNEM    SFLU' \
                    + b'EA\x04\x00OUTP    SFLU' \
                    + b'EA\x04\x00STAT    ALLO' \
                    + b'EA\x04\x00TRAC    T23 ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    1   ' \
                    + b'EA\x04\x00MODE    GRAD' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDGOHMM?fff' \
                    + b'ED\x04\x00REDGOHMME\xfd\x00\x00' \
                + b'\x00A\x04\x00MNEM    ILM\x00' \
                    + b'EA\x04\x00OUTP    ILM ' \
                    + b'EA\x04\x00STAT    ALLO' \
                    + b'EA\x04\x00TRAC    T23 ' \
                    + b'EA\x04\x00CODI    LSPO' \
                    + b'EA\x04\x00DEST    1   ' \
                    + b'EA\x04\x00MODE    GRAD' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDGOHMM?fff' \
                    + b'ED\x04\x00REDGOHMME\xfd\x00\x00' \
                + b'\x00A\x04\x00MNEM    ILDG' \
                    + b'EA\x04\x00OUTP    ILD ' \
                    + b'EA\x04\x00STAT    ALLO' \
                    + b'EA\x04\x00TRAC    T23 ' \
                    + b'EA\x04\x00CODI    LDAS' \
                    + b'EA\x04\x00DEST    1   ' \
                    + b'EA\x04\x00MODE    GRAD' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDGOHMM?fff' \
                    + b'ED\x04\x00REDGOHMME\xfd\x00\x00' \
                + b'\x00A\x04\x00MNEM    4\x00\x00\x00' \
                    + b'EA\x04\x00OUTP    DUMM' \
                    + b'EA\x04\x00STAT    DISA' \
                    + b'EA\x04\x00TRAC    T1  ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    NEIT' \
                    + b'EA\x04\x00MODE    NB  ' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDG    \x00\x00\x00\x00' \
                    + b'ED\x04\x00REDG    @\xc0\x00\x00' \
                + b'\x00A\x04\x00MNEM    5\x00\x00\x00' \
                    + b'EA\x04\x00OUTP    DUMM' \
                    + b'EA\x04\x00STAT    DISA' \
                    + b'EA\x04\x00TRAC    T1  ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    NEIT' \
                    + b'EA\x04\x00MODE    NB  ' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDG    \x00\x00\x00\x00' \
                    + b'ED\x04\x00REDG    @\xc0\x00\x00' \
                + b'\x00A\x04\x00MNEM    6\x00\x00\x00' \
                    + b'EA\x04\x00OUTP    DUMM' \
                    + b'EA\x04\x00STAT    DISA' \
                    + b'EA\x04\x00TRAC    T1  ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    NEIT' \
                    + b'EA\x04\x00MODE    NB  ' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDG    \x00\x00\x00\x00' \
                    + b'ED\x04\x00REDG    @\xc0\x00\x00' \
                + b'\x00A\x04\x00MNEM    7\x00\x00\x00' \
                    + b'EA\x04\x00OUTP    DUMM' \
                    + b'EA\x04\x00STAT    DISA' \
                    + b'EA\x04\x00TRAC    T1  ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    NEIT' \
                    + b'EA\x04\x00MODE    NB  ' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDG    \x00\x00\x00\x00' \
                    + b'ED\x04\x00REDG    @\xc0\x00\x00' \
                + b'\x00A\x04\x00MNEM    SFLA' \
                    + b'EA\x04\x00OUTP    SFLA' \
                    + b'EA\x04\x00STAT    ALLO' \
                    + b'EA\x04\x00TRAC    T2  ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    2   ' \
                    + b'EA\x04\x00MODE    X10 ' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDGOHMM\x00\x00\x00\x00' \
                    + b'ED\x04\x00REDGOHMMBP\x00\x00' \
                + b'\x00A\x04\x00MNEM    ASFA' \
                    + b'EA\x04\x00OUTP    SFLA' \
                    + b'EA\x04\x00STAT    ALLO' \
                    + b'EA\x04\x00TRAC    T2  ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    2   ' \
                    + b'EA\x04\x00MODE    NB  ' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDGOHMM\x00\x00\x00\x00' \
                    + b'ED\x04\x00REDGOHMMA@\x00\x00' \
                + b'\x00A\x04\x00MNEM    ILDE' \
                    + b'EA\x04\x00OUTP    ILD ' \
                    + b'EA\x04\x00STAT    ALLO' \
                    + b'EA\x04\x00TRAC    T2  ' \
                    + b'EA\x04\x00CODI    LDAS' \
                    + b'EA\x04\x00DEST    2   ' \
                    + b'EA\x04\x00MODE    X10 ' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDGOHMM\x00\x00\x00\x00' \
                    + b'ED\x04\x00REDGOHMMBP\x00\x00' \
                + b'\x00A\x04\x00MNEM    CILD' \
                    + b'EA\x04\x00OUTP    CILD' \
                    + b'EA\x04\x00STAT    ALLO' \
                    + b'EA\x04\x00TRAC    T3  ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    2   ' \
                    + b'EA\x04\x00MODE    SHIF' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDGMMHOE\xfd\x00\x00' \
                    + b'ED\x04\x00REDGMMHO\x00\x00\x00\x00' \
                + b'\x00A\x04\x00MNEM    12\x00\x00' \
                    + b'EA\x04\x00OUTP    DUMM' \
                    + b'EA\x04\x00STAT    DISA' \
                    + b'EA\x04\x00TRAC    T1  ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    NEIT' \
                    + b'EA\x04\x00MODE    NB  ' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDG    \x00\x00\x00\x00' \
                    + b'ED\x04\x00REDG    @\xc0\x00\x00' \
                + b'\x00A\x04\x00MNEM    13\x00\x00' \
                    + b'EA\x04\x00OUTP    DUMM' \
                    + b'EA\x04\x00STAT    DISA' \
                    + b'EA\x04\x00TRAC    T1  ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    NEIT' \
                    + b'EA\x04\x00MODE    NB  ' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDG    \x00\x00\x00\x00' \
                    + b'ED\x04\x00REDG    @\xc0\x00\x00' \
                + b'\x00A\x04\x00MNEM    14\x00\x00' \
                    + b'EA\x04\x00OUTP    DUMM' \
                    + b'EA\x04\x00STAT    DISA' \
                    + b'EA\x04\x00TRAC    T1  ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    NEIT' \
                    + b'EA\x04\x00MODE    NB  ' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDG    \x00\x00\x00\x00' \
                    + b'ED\x04\x00REDG    @\xc0\x00\x00' \
                + b'\x00A\x04\x00MNEM    15\x00\x00' \
                    + b'EA\x04\x00OUTP    DUMM' \
                    + b'EA\x04\x00STAT    DISA' \
                    + b'EA\x04\x00TRAC    T1  ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    NEIT' \
                    + b'EA\x04\x00MODE    NB  ' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDG    \x00\x00\x00\x00' \
                    + b'ED\x04\x00REDG    @\xc0\x00\x00' \
                + b'\x00A\x04\x00MNEM    16\x00\x00' \
                    + b'EA\x04\x00OUTP    DUMM' \
                    + b'EA\x04\x00STAT    DISA' \
                    + b'EA\x04\x00TRAC    T1  ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    NEIT' \
                    + b'EA\x04\x00MODE    NB  ' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDG    \x00\x00\x00\x00' \
                    + b'ED\x04\x00REDG    @\xc0\x00\x00' \
                + b'\x00A\x04\x00MNEM    17\x00\x00' \
                    + b'EA\x04\x00OUTP    DUMM' \
                    + b'EA\x04\x00STAT    DISA' \
                    + b'EA\x04\x00TRAC    T1  ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    NEIT' \
                    + b'EA\x04\x00MODE    NB  ' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDG    \x00\x00\x00\x00' \
                    + b'ED\x04\x00REDG    @\xc0\x00\x00' \
                + b'\x00A\x04\x00MNEM    18\x00\x00' \
                    + b'EA\x04\x00OUTP    DUMM' \
                    + b'EA\x04\x00STAT    DISA' \
                    + b'EA\x04\x00TRAC    T1  ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    NEIT' \
                    + b'EA\x04\x00MODE    NB  ' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDG    \x00\x00\x00\x00' \
                    + b'ED\x04\x00REDG    @\xc0\x00\x00' \
                + b'\x00A\x04\x00MNEM    19\x00\x00' \
                    + b'EA\x04\x00OUTP    DUMM' \
                    + b'EA\x04\x00STAT    DISA' \
                    + b'EA\x04\x00TRAC    T1  ' \
                    + b'EA\x04\x00CODI    LLIN' \
                    + b'EA\x04\x00DEST    NEIT' \
                    + b'EA\x04\x00MODE    NB  ' \
                    + b'ED\x04\x00FILT    @@\x00\x00' \
                    + b'ED\x04\x00LEDG    \x00\x00\x00\x00' \
                    + b'ED\x04\x00REDG    @\xc0\x00\x00'
        myF = self._retFileSinglePr(myBy)
        myT = LogiRec.LrTableRead(myF)
        self.assertEqual(b'PRES', myT.value)
        #print()
        for r in myT.genRows():
            for c in r.genCells():
                pass
                #print(c.engVal, '\t', end="")
            #print('\n')
        self.assertEqual(len(myT), 20)
        self.assertFalse(myT.isSingleParam)
        #print(sorted(list(myT.rowLabels())))
        self.assertEqual(
            [
                 b'12\x00\x00',
                 b'13\x00\x00',
                 b'14\x00\x00',
                 b'15\x00\x00',
                 b'16\x00\x00',
                 b'17\x00\x00',
                 b'18\x00\x00',
                 b'19\x00\x00',
                 b'4\x00\x00\x00',
                 b'5\x00\x00\x00',
                 b'6\x00\x00\x00',
                 b'7\x00\x00\x00',
                 b'ASFA',
                 b'CILD',
                 b'ILDE',
                 b'ILDG',
                 b'ILM\x00',
                 b'SFLA',
                 b'SFLU',
                 b'SP\x00\x00'
             ],                         
             sorted(list(myT.rowLabels())),
        )
        #print(myT.colLabels())
        self.assertEqual(
            {b'OUTP', b'STAT', b'TRAC', b'FILT', b'DEST', b'CODI', b'MNEM', b'REDG', b'MODE', b'LEDG'},
            myT.colLabels(),
        )
        self.assertTrue(myT[b'CILD'] is not None)
        self.assertEqual(len(myT[b'CILD']), 10)
        self.assertTrue(myT[b'ILDE'] is not None)
        self.assertEqual(len(myT[b'ILDE']), 10)
#        print()
#        pprint.pprint(myT._mnemRowIndex)
        self.assertEqual(
            {
                Mnem.Mnem(b'12\x00\x00'): 12,
                Mnem.Mnem(b'13\x00\x00'): 13,
                Mnem.Mnem(b'14\x00\x00'): 14,
                Mnem.Mnem(b'15\x00\x00'): 15,
                Mnem.Mnem(b'16\x00\x00'): 16,
                Mnem.Mnem(b'17\x00\x00'): 17,
                Mnem.Mnem(b'18\x00\x00'): 18,
                Mnem.Mnem(b'19\x00\x00'): 19,
                Mnem.Mnem(b'4\x00\x00\x00'): 4,
                Mnem.Mnem(b'5\x00\x00\x00'): 5,
                Mnem.Mnem(b'6\x00\x00\x00'): 6,
                Mnem.Mnem(b'7\x00\x00\x00'): 7,
                Mnem.Mnem(b'ASFA'): 9,
                Mnem.Mnem(b'CILD'): 11,
                Mnem.Mnem(b'ILDE'): 10,
                Mnem.Mnem(b'ILDG'): 3,
                Mnem.Mnem(b'ILM\x00'): 2,
                Mnem.Mnem(b'SFLA'): 8,
                Mnem.Mnem(b'SFLU'): 1,
                Mnem.Mnem(b'SP\x00\x00'): 0,
            },
            myT._mnemRowIndex,
        )
    
    def test_01(self):
        """TestLrTableSpecific.test_00(): CONS table."""
        # Mnem/value/uom where value is bytes/float/int
        myData = [
            (b'HIDE', b'MAIN LOG',  None),
#            (b'TDD ', RepCode.writeBytes(3000.0, 68),   b'M   '),
#            (b'TDL ', RepCode.writeBytes(2989.5, 68),   b'M   '),
            (b'TDD ', 3000.0,       b'M   '),
            (b'TDL ', 2989.5,       b'M   '),
        ]
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
        for m, v, u in myData:
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
        myF = self._retFilePrS(b''.join(myB))
        myLr = LogiRec.LrTableRead(myF)
        self.assertEqual(b'CONS', myLr.value)
#        print()
#        for r in myLr.genRows():
#            for c in r.genCells():
#                pass
#                print(c.engVal, '\t', end="")
#            print('\n')
        self.assertEqual(len(myLr), 3)
        self.assertFalse(myLr.isSingleParam)
        #print(sorted(list(myLr.rowLabels())))
        self.assertEqual(
            [
                 b'HIDE',
                 b'TDD ',
                 b'TDL ',
             ],                         
             sorted(list(myLr.rowLabels())),
        )
        #print(myT.colLabels())
        self.assertEqual(
            {b'MNEM', b'STAT', b'PUNI', b'TUNI', b'VALU'},
            myLr.colLabels(),
        )
        self.assertTrue(myLr[b'HIDE'] is not None)
        self.assertEqual(5, len(myLr[b'HIDE']))
        self.assertEqual(b'MAIN LOG', myLr[b'HIDE'][b'VALU'].value)
        self.assertEqual(3000.0, myLr[b'TDD '][b'VALU'].value)
        try:
            myLr[b'wtf']
            self.fail('KeyError not raised.')
        except KeyError:
            pass
#        print()
#        print(myLr._mnemRowIndex)
        self.assertEqual(
            {
                Mnem.Mnem(b'TDD\x00'): 1,
                Mnem.Mnem(b'TDL\x00'): 2,
                Mnem.Mnem(b'HIDE'): 0,
            },
            myLr._mnemRowIndex,
        )
    
class TestLrTableWrite(TestLrBase):
    """Class to test direct creation of tables."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestLrTableSpecific: Tests setUp() and tearDown()."""
        pass
    
    def _retAllBytes(self, theR):
        ba = bytearray([34, 0])
        for b in theR.genLisBytes():
            ba += b
        return bytes(ba)
    
    def _checkByteLists(self, bA, bB):
        for i, (a, b) in enumerate(map(lambda *args: args, bA, bB)):
            if a != b:
                print('%4d: %s -> %s' % (i, a, b))

    def test_00(self):
        """TestLrTableWrite.test_00(): Simple FILM table from the LIS manual."""
        myT = LogiRec.LrTableWrite(
            34,
            b'FILM',
            (b'MNEM', b'GCOD', b'GDEC', b'DEST', b'DSCA',),
            (
                (b'1   ', b'E2E ', b'2   ', b'PF1 ', b'S5  ',),
                (b'2   ', b'BBB ', b'-   ', b'PF2 ', b'S5  ',),
            ),
        )
#        print()
#        print(myT)
        self.assertEqual(myT.value, b'FILM')
        self.assertEqual(len(myT), 2)
        self.assertFalse(myT.isSingleParam)
        self.assertEqual(list(myT.rowLabels()), [b'1   ', b'2   '])
        self.assertEqual(myT.colLabels(), {b'MNEM', b'DEST', b'DSCA', b'GDEC', b'GCOD'})
        self.assertTrue(myT[b'1   '] is not None)
        self.assertEqual(len(myT[b'1   ']), 5)
        self.assertTrue(myT[b'2   '] is not None)
        self.assertEqual(len(myT[b'2   ']), 5)
        expBytes = (b'IA\x04\x00TYPE    FILM'
            + b'\x00A\x04\x00MNEM    1   '
            + b'EA\x04\x00GCOD    E2E '
            + b'EA\x04\x00GDEC    2   '
            + b'EA\x04\x00DEST    PF1 '
            + b'EA\x04\x00DSCA    S5  '
            + b'\x00A\x04\x00MNEM    2   '
            + b'EA\x04\x00GCOD    BBB '
            + b'EA\x04\x00GDEC    -   '
            + b'EA\x04\x00DEST    PF2 '
            + b'EA\x04\x00DSCA    S5  '
        )
        ba = bytearray()
#        print()
        for b in myT.genLisBytes():
#            print(b)
            ba += b
#        print(ba)
        self.assertEqual(expBytes, ba)
        
        
    def test_01(self):
        """TestLrTableWrite.test_01(): Simple FILM table from the TestPlotExample."""
        myT = LogiRec.LrTableWrite(
            34,
            b'FILM',
            (b'MNEM', b'GCOD', b'GDEC', b'DEST', b'DSCA',),
            (
                (b'1   ', b'E20 ', b'-4--', b'PF1 ', b'D200',),
                (b'2   ', b'EEE ', b'----', b'PF2 ', b'D200',),
            ),
        )
#        print()
#        print(myT)
        expBytes = b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1   ' \
                    + b'EA\x04\x00GCOD    E20 ' \
                    + b'EA\x04\x00GDEC    -4--' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    2   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D200'
        actBytes = self._retAllBytes(myT)
#        print()
#        print(expBytes)
#        print(actBytes)
#        print(len(expBytes))
        self._checkByteLists(expBytes, actBytes)
        self.assertEqual(expBytes, actBytes)

    def test_02(self):
        """TestLrTableWrite.test_02(): Small PRES table from the TestPlotExample."""
        myT = LogiRec.LrTableWrite(
            34,
            b'PRES',
            (b'MNEM', b'OUTP', b'STAT', b'TRAC', b'CODI', b'DEST', b'MODE', b'FILT', b'LEDG', b'REDG',),
            (
                (b'SP  ', b'SP  ', b'ALLO', b'T1  ', b'LLIN', b'1   ', b'SHIF', 0.5, (-80.0, b'MV  '), (20.0, b'MV  ')),
            ),
        )
#        print()
#        print(myT)
        expBytes = (b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    SP  '
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
        )
        actBytes = self._retAllBytes(myT)
#        print()
#        print(expBytes)
#        print(actBytes)
#        print(len(expBytes))
        self._checkByteLists(expBytes, actBytes)
        self.assertEqual(expBytes, actBytes)

    def test_03(self):
        """TestLrTableWrite.test_03(): Larger PRES table from the TestPlotExample."""
        myT = LogiRec.LrTableWrite(
            34,
            b'PRES',
            (b'MNEM', b'OUTP', b'STAT', b'TRAC', b'CODI', b'DEST', b'MODE', b'FILT', b'LEDG', b'REDG',),
            (
                (b'40  ', b'TEST', b'ALLO', b'T1  ', b'LLIN', b'2   ', b'SHIF', 0.5, (-40.0, b'MV  '), (40.0, b'MV  ')),
                (b'20  ', b'TEST', b'ALLO', b'T2  ', b'HDAS', b'2   ', b'SHIF', 0.5, (-20.0, b'MV  '), (20.0, b'MV  ')),
                (b'10  ', b'TEST', b'ALLO', b'T3  ', b'LGAP', b'2   ', b'WRAP', 0.5, (-10.0, b'MV  '), (10.0, b'MV  ')),
                (b'5   ', b'TEST', b'ALLO', b'T2  ', b'HSPO', b'2   ', b'WRAP', 0.5, (-5.0, b'MV  '), (5.0, b'MV  ')),
                (b'2.5 ', b'TEST', b'ALLO', b'T3  ', b'LSPO', b'2   ', b'WRAP', 0.5, (-2.5, b'MV  '), (2.5, b'MV  ')),
            ),
        )
#        print()
#        print(myT)
        expBytes = (b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #40    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      -40.0000       40.0000
            + b'\x00A\x04\x00MNEM    40  '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-40.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(40.0, 68)#B\xd0\x00\x00'
            #20    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      -20.0000       20.0000
            + b'\x00A\x04\x00MNEM    20  '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HDAS'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-20.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
            #10    TEST  ALLO  T1    LLIN  1     SHIF      0.500000      -10.0000       10.0000
            + b'\x00A\x04\x00MNEM    10  '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T3  '
                + b'EA\x04\x00CODI    LGAP'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-10.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(10.0, 68)#B\xd0\x00\x00'
            # Scale -5 to 5
            + b'\x00A\x04\x00MNEM    5   '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HSPO'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-5.0, 68)
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(5.0, 68)
            # Scale -2.5 to 2.5
            + b'\x00A\x04\x00MNEM    2.5 '
                + b'EA\x04\x00OUTP    TEST'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T3  '
                + b'EA\x04\x00CODI    LSPO'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    WRAP'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-2.5, 68)
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(2.5, 68)
        )
        actBytes = self._retAllBytes(myT)
#        print()
#        print(expBytes)
#        print(actBytes)
#        print(len(expBytes))
        self._checkByteLists(expBytes, actBytes)
        self.assertEqual(expBytes, actBytes)

class TestEntryBlock(TestLrBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass
    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestEntryBlock: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestEntryBlock.test_00(): Simple test."""
        myF = self._retFileSinglePr(bytes([4, 1, 66, 1]))
        myEb = LogiRec.EntryBlockRead(myF)
        self.assertEqual(myEb.type, 4)
        self.assertEqual(myEb.size, 1)
        self.assertEqual(myEb.repCode, 66)
        self.assertEqual(myEb.value, 1)

    def test_01(self):
        """TestEntryBlock.test_01(): Absent value = -999.25."""
        #print(RepCode.write68(-999.25))
        myF = self._retFileSinglePr(
            bytes([12, 4, 68]) + b'\xba\x83\x18\x00'
        )
        myEb = LogiRec.EntryBlockRead(myF)
        self.assertEqual(myEb.type, 12)
        self.assertEqual(myEb.size, 4)
        self.assertEqual(myEb.repCode, 68)
        self.assertEqual(myEb.value, -999.25)
        self.assertEqual(
            str(myEb),
            'EntryBlockRead(type=12, size=4, repCode=68, value=-999.25)',
        )

    def test_02(self):
        """TestEntryBlock.test_02(): Zero size."""
        myF = self._retFileSinglePr(bytes([0, 0, 66]))
        myEb = LogiRec.EntryBlockRead(myF)
        self.assertEqual(myEb.type, 0)
        self.assertEqual(myEb.size, 0)
        self.assertEqual(myEb.repCode, 66)
        self.assertTrue(myEb.value is None)
        self.assertEqual(
            str(myEb),
            'EntryBlockRead(type=0, size=0, repCode=66, value=None)'
        )

class TestEntryBlockSet(TestLrBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass
    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestEntryBlockSet: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestEntryBlockSet.test_00(): Test defaults."""
        myEbs = LogiRec.EntryBlockSet()
        #print()
        #print(myEbs)
        self.maxDiff = None
        self.assertEqual(str(myEbs), """EntryBlockSet [20 bytes]:
EntryBlock(type=0, size=0, repCode=66, value=None)
EntryBlock(type=1, size=1, repCode=66, value=0)
EntryBlock(type=2, size=1, repCode=66, value=0)
EntryBlock(type=3, size=1, repCode=66, value=0)
EntryBlock(type=4, size=1, repCode=66, value=1)
EntryBlock(type=5, size=1, repCode=66, value=1)
EntryBlock(type=6, size=0, repCode=66, value=None)
EntryBlock(type=7, size=4, repCode=65, value=b'.1IN')
EntryBlock(type=8, size=0, repCode=66, value=None)
EntryBlock(type=9, size=0, repCode=65, value=None)
EntryBlock(type=10, size=0, repCode=66, value=None)
EntryBlock(type=11, size=0, repCode=66, value=None)
EntryBlock(type=12, size=4, repCode=68, value=-999.25)
EntryBlock(type=13, size=1, repCode=66, value=0)
EntryBlock(type=14, size=4, repCode=65, value=b'.1IN')
EntryBlock(type=15, size=1, repCode=66, value=0)
EntryBlock(type=16, size=1, repCode=66, value=0)""")
        #print('myEbs.lisByteList()')
        #pprint.pprint(myEbs.lisByteList())
        expByList = [
            bytearray(b'\x01\x01B\x00'),
            bytearray(b'\x02\x01B\x00'),
            bytearray(b'\x03\x01B\x00'),
            bytearray(b'\x04\x01B\x01'),
            bytearray(b'\x05\x01B\x01'),
            bytearray(b'\x06\x00B'),
            bytearray(b'\x07\x04A.1IN'),
            bytearray(b'\x08\x00B'),
            bytearray(b'\t\x00A'),
            bytearray(b'\x0b\x00B'),
            bytearray(b'\x0c\x04D\xba\x83\x18\x00'),
            bytearray(b'\r\x01B\x00'),
            bytearray(b'\x0e\x04A.1IN'),
            bytearray(b'\x0f\x01B\x00'),
            bytearray(b'\x10\x01B\x00'),
            bytearray(b'\x00\x00B'),
        ]
        self.assertEqual(
            expByList,
            myEbs.lisByteList(),
        )
        #print('myEbs.lisBytes()', myEbs.lisBytes())
        expBy = b'\x01\x01B\x00' \
            + b'\x02\x01B\x00' \
            + b'\x03\x01B\x00' \
            + b'\x04\x01B\x01' \
            + b'\x05\x01B\x01' \
            + b'\x06\x00B' \
            + b'\x07\x04A.1IN' \
            + b'\x08\x00B' \
            + b'\t\x00A' \
            + b'\x0b\x00B' \
            + b'\x0c\x04D\xba\x83\x18\x00' \
            + b'\r\x01B\x00' \
            + b'\x0e\x04A.1IN' \
            + b'\x0f\x01B\x00' \
            + b'\x10\x01B' \
            + b'\x00\x00\x00B'
        self.assertEqual(expBy, myEbs.lisBytes())
        self.assertFalse(myEbs.xInc)
        self.assertFalse(myEbs.logDown)
        self.assertTrue(myEbs.logUp)

    def test_01(self):
        """TestEntryBlockSet.test_01(): Simple setting of a block that sets an down log."""
        myEbs = LogiRec.EntryBlockSet()
        myEb = LogiRec.EntryBlock(4, 1, 66, 255)
        myEbs.setEntryBlock(myEb)
        #print()
        #print(myEbs)
        self.maxDiff = None
        self.assertEqual(str(myEbs), """EntryBlockSet [20 bytes]:
EntryBlock(type=0, size=0, repCode=66, value=None)
EntryBlock(type=1, size=1, repCode=66, value=0)
EntryBlock(type=2, size=1, repCode=66, value=0)
EntryBlock(type=3, size=1, repCode=66, value=0)
EntryBlock(type=4, size=1, repCode=66, value=255)
EntryBlock(type=5, size=1, repCode=66, value=1)
EntryBlock(type=6, size=0, repCode=66, value=None)
EntryBlock(type=7, size=4, repCode=65, value=b'.1IN')
EntryBlock(type=8, size=0, repCode=66, value=None)
EntryBlock(type=9, size=0, repCode=65, value=None)
EntryBlock(type=10, size=0, repCode=66, value=None)
EntryBlock(type=11, size=0, repCode=66, value=None)
EntryBlock(type=12, size=4, repCode=68, value=-999.25)
EntryBlock(type=13, size=1, repCode=66, value=0)
EntryBlock(type=14, size=4, repCode=65, value=b'.1IN')
EntryBlock(type=15, size=1, repCode=66, value=0)
EntryBlock(type=16, size=1, repCode=66, value=0)""")
        self.assertTrue(myEbs.xInc)
        self.assertTrue(myEbs.logDown)
        self.assertFalse(myEbs.logUp)

    def test_02(self):
        """TestEntryBlockSet.test_02(): Simple setting of an illegal block."""
        myEbs = LogiRec.EntryBlockSet()
        # Try block 99
        try:
            myEbs.setEntryBlock(LogiRec.EntryBlock(99, 1, 66, 0))
            self.fail('LogiRec.ExceptionEntryBlock not raised')
        except LogiRec.ExceptionEntryBlock:
            pass
        # Try undefined block 10
        try:
            myEbs.setEntryBlock(LogiRec.EntryBlock(10, 1, 66, 0))
            self.fail('LogiRec.ExceptionEntryBlock not raised')
        except LogiRec.ExceptionEntryBlock:
            pass
        
    def test_03(self):
        """TestEntryBlockSet.test_03(): Set bad block."""
        myEbs = LogiRec.EntryBlockSet()
        myEb = LogiRec.EntryBlock(99, 1, 66, 0)
        self.assertRaises(LogiRec.ExceptionEntryBlock, myEbs.setEntryBlock, myEb)

    def test_04(self):
        """TestEntryBlockSet.test_04(): Get attributes."""
        myEbs = LogiRec.EntryBlockSet()
        self.assertEqual(myEbs.dataType,        0)
        self.assertEqual(myEbs.absentValue,     -999.25)
        self.assertEqual(myEbs.recordingMode,   0)
        self.assertEqual(myEbs.depthUnits,      b'.1IN')
        self.assertEqual(myEbs.depthRepCode,    0)

    def test_05(self):
        """TestEntryBlockSet.test_05(): Get attribute that fails."""
        myEbs = LogiRec.EntryBlockSet()
        try:
            myEbs.spam
            self.fail('AttributeError not raised.')
        except AttributeError:
            pass
        #self.assertRaises(AttributeError, myEbs.spam)

    def test_10(self):
        """TestEntryBlockSet.test_10(): Read from file."""
        myEbs = LogiRec.EntryBlockSet()
        myF = self._retFileSinglePr(
            # Logical record header for DFSR
            bytes([64, 0])
            # Entry block 4, value 0
            +bytes([4, 1, 66, 0])
            # Entry block 12, value -153.0
            + bytes([12, 4, 68])
            + b'\xbb\xb3\x80\x00'
        )
        self.assertEqual(myF.readLrBytes(2), b'@\x00')
        myEbs.readFromFile(myF)
        self.assertEqual(myEbs[4].value, 0)
        self.assertEqual(myEbs.absentValue, -153.0)
        
    def test_11(self):
        """TestEntryBlockSet.test_11(): Read from file raises with spurious bytes."""
        myEbs = LogiRec.EntryBlockSet()
        myF = self._retFileSinglePr(
            # Logical record header for DFSR
            bytes([64, 0])
            # Entry block 4, value 0
            +bytes([4, 1, 66, 0])
            # Entry block 12, value -153.0
            + bytes([12, 4, 68])
            + b'\xbb\xb3\x80\x00'
            # Spurious bytes
            + bytes([1, 2])
        )
        self.assertEqual(myF.readLrBytes(2), b'@\x00')
        # Should read and raise and exception
        self.assertRaises(File.ExceptionFileRead, myEbs.readFromFile, myF)
        self.assertEqual(myEbs[4].value, 0)
        self.assertEqual(myEbs.absentValue, -153.0)
        
    def test_12(self):
        """TestEntryBlockSet.test_12(): Read from file with spurious bytes masked by type 0 block."""
        myEbs = LogiRec.EntryBlockSet()
        myF = self._retFileSinglePr(
            # Logical record header for DFSR
            bytes([64, 0])
            # Entry block 4, value 0
            + bytes([4, 1, 66, 0])
            # Entry block 12, value -153.0
            + bytes([12, 4, 68])
            + b'\xbb\xb3\x80\x00'
            # Entry block 0, value None terminates read
            +bytes([0, 1, 66, 0])
            # Spurious bytes
            + bytes([1, 2])
        )
        self.assertEqual(myF.readLrBytes(2), b'@\x00')
        myEbs.readFromFile(myF)
        self.assertEqual(myEbs[4].value, 0)
        self.assertEqual(myEbs.absentValue, -153.0)
        
    def test_13(self):
        """TestEntryBlockSet.test_13(): Undefined entry block type 10 produces warning but does not raise."""
        myEbs = LogiRec.EntryBlockSet()
        myF = self._retFileSinglePr(
            # Logical record header for DFSR
            bytes([64, 0])
            # Entry block 4, value 0
            +bytes([10, 1, 66, 0])
            # Entry block 12, value -153.0
            + bytes([12, 4, 68])
            + b'\xbb\xb3\x80\x00'
        )
        self.assertEqual(myF.readLrBytes(2), b'@\x00')
        myEbs.readFromFile(myF)
        self.assertEqual(myEbs.absentValue, -153.0)
        
    def test_20(self):
        """TestEntryBlockSet.test_20(): Test optical X units are FEET by default."""
        myEbs = LogiRec.EntryBlockSet()
        #print()
        #print(myEbs)
        self.assertEqual(Units.OPTICAL_FEET, myEbs.opticalLogScale)

    def test_21(self):
        """TestEntryBlockSet.test_21(): Test optical X units are FEET  with entry block 5 value 1."""
        myEbs = LogiRec.EntryBlockSet()
        myEb = LogiRec.EntryBlock(5, 1, 66, 1)
        self.assertEqual(Units.OPTICAL_FEET, myEbs.opticalLogScale)

    def test_22(self):
        """TestEntryBlockSet.test_22(): Test optical X units are set to b'M   ' with entry block 5 value 255."""
        myEbs = LogiRec.EntryBlockSet()
        myEb = LogiRec.EntryBlock(5, 1, 66, 255)
        myEbs.setEntryBlock(myEb)
        self.assertEqual(Units.OPTICAL_METERS, myEbs.opticalLogScale)
        
    def test_23(self):
        """TestEntryBlockSet.test_23(): Test optical X units are set to b'S   ' with entry block 5 value 0."""
        myEbs = LogiRec.EntryBlockSet()
        myEb = LogiRec.EntryBlock(5, 1, 66, 0)
        myEbs.setEntryBlock(myEb)
        self.assertEqual(Units.OPTICAL_TIME, myEbs.opticalLogScale)

class TestDatumSpecBlock(TestLrBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass
    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestDatumSpecBlock: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestDatumSpecBlock.test_00(): Unpack API codes."""
        myDsb = LogiRec.DatumSpecBlock()
        self.assertEqual(myDsb._unpackApiInt(45310011), (45, 310, 1, 1))
        myDsb._unpackApiCodes(45310011)
        self.assertEqual(myDsb.apiLogType,      45)        
        self.assertEqual(myDsb.apiCurveType,    310)        
        self.assertEqual(myDsb.apiCurveClass,   1)        
        self.assertEqual(myDsb.apiModifier,     1)        

    def test_10(self):
        """TestDatumSpecBlock.test_10(): Read from file."""
        # Logical record header for DFSR
        myB = bytes([64, 0])
        # Mnemonic
        myB += b'GR  '
        # Service ID
        myB += b'ServID'
        # Service order number
        myB += b'ServOrdN'
        # Units
        myB += b'GAPI'
        # API codes 45, 310, 01, 1
        # Decimal 45310011 is 0x02b3603b
        myB += b'\x02\xb3\x60\x3b'
        # File number: 256
        myB += bytes([1, 0])
        # LIS size in bytes: 4 samples * 6 burst smples * 4 bytes = 96 bytes
        myB += bytes([0, 96])
        # Padding '0'
        myB += b'000'
        # Samples: 4 super samples
        myB += bytes([4,])
        # Representation code
        myB += bytes([68,])
        # Process indicators
        myB += bytes([0, 1, 2, 3, 4])
        myF = self._retFileSinglePr(myB)
        self.assertEqual(myF.readLrBytes(2), b'@\x00')
        myDsb = LogiRec.DatumSpecBlockRead(myF)
        self.assertEqual(myDsb.mnem,            b'GR  ')
        self.assertEqual(myDsb.servId,          b'ServID')
        self.assertEqual(myDsb.servOrd,         b'ServOrdN')
        self.assertEqual(myDsb.units,           b'GAPI')
        self.assertEqual(myDsb.apiLogType,      45)
        self.assertEqual(myDsb.apiCurveType,    310)
        self.assertEqual(myDsb.apiCurveClass,   1)        
        self.assertEqual(myDsb.apiModifier,     1)
        self.assertEqual(myDsb.fileNumber,      256)
        self.assertEqual(myDsb.size,            96)        
        self.assertEqual(myDsb._samples,        4)
        self.assertEqual(myDsb.repCode,         68)
        self.assertEqual(myDsb.subChannels,     1)
        self.assertEqual(myDsb.bursts(0),       6)
        self.assertEqual(myDsb.samples(0),      4)
        self.assertRaises(IndexError, myDsb.samples, -1)
        self.assertRaises(IndexError, myDsb.samples, 2)

    def test_11(self):
        """TestDatumSpecBlock.test_11(): Read from file - dipmeter code 130."""
        # Logical record header for DFSR
        myB = bytes([64, 0])
        # Mnemonic
        myB += b'HDT '
        # Service ID
        myB += b'ServID'
        # Service order number
        myB += b'ServOrdN'
        # Units
        myB += b'    '
        # API codes 45, 310, 01, 1
        # Decimal 45310011 is 0x02b3603b
        myB += b'\x02\xb3\x60\x3b'
        # File number: 256
        myB += bytes([1, 0])
        # LIS size in bytes: 5 sub-channles * 16 samples * 1 burst smples * 1 byte = 80 bytes
        myB += bytes([0, 80])
        # Padding '0'
        myB += b'000'
        # Samples: 4 super samples
        myB += bytes([1,])
        # Representation code
        myB += bytes([130,])
        # Process indicators
        myB += bytes([0, 1, 2, 3, 4])
        myF = self._retFileSinglePr(myB)
        self.assertEqual(myF.readLrBytes(2), b'@\x00')
        myDsb = LogiRec.DatumSpecBlockRead(myF)
        self.assertEqual(myDsb.mnem,            b'HDT ')
        self.assertEqual(myDsb.servId,          b'ServID')
        self.assertEqual(myDsb.servOrd,         b'ServOrdN')
        self.assertEqual(myDsb.units,           b'    ')
        self.assertEqual(myDsb.apiLogType,      45)
        self.assertEqual(myDsb.apiCurveType,    310)
        self.assertEqual(myDsb.apiCurveClass,   1)        
        self.assertEqual(myDsb.apiModifier,     1)
        self.assertEqual(myDsb.fileNumber,      256)
        self.assertEqual(myDsb.size,            80)        
        self.assertEqual(myDsb._samples,        1)
        self.assertEqual(myDsb.repCode,         130)
        self.assertEqual(myDsb.subChannels,     5)
        self.assertEqual(myDsb.bursts(0),       1)
        self.assertEqual(myDsb.bursts(1),       1)
        self.assertEqual(myDsb.bursts(2),       1)
        self.assertEqual(myDsb.bursts(3),       1)
        self.assertEqual(myDsb.bursts(4),       1)
        self.assertEqual(myDsb.samples(0),      16)
        self.assertEqual(myDsb.samples(1),      16)
        self.assertEqual(myDsb.samples(2),      16)
        self.assertEqual(myDsb.samples(3),      16)
        self.assertEqual(myDsb.samples(4),      16)
        self.assertRaises(IndexError, myDsb.samples, -1)
        self.assertRaises(IndexError, myDsb.samples, 5)

    def test_12(self):
        """TestDatumSpecBlock.test_12(): Read from file - dipmeter code 234."""
        # Logical record header for DFSR
        myB = bytes([64, 0])
        # Mnemonic
        myB += b'HDT '
        # Service ID
        myB += b'ServID'
        # Service order number
        myB += b'ServOrdN'
        # Units
        myB += b'    '
        # API codes 45, 310, 01, 1
        # Decimal 45310011 is 0x02b3603b
        myB += b'\x02\xb3\x60\x3b'
        # File number: 256
        myB += bytes([1, 0])
        # LIS size in bytes: 5*16 + 10*1 = 90 bytes
        myB += bytes([0, 90])
        # Padding '0'
        myB += b'000'
        # Samples: 1 super samples
        myB += bytes([1,])
        # Representation code
        myB += bytes([234,])
        # Process indicators
        myB += bytes([0, 1, 2, 3, 4])
        myF = self._retFileSinglePr(myB)
        self.assertEqual(myF.readLrBytes(2), b'@\x00')
        myDsb = LogiRec.DatumSpecBlockRead(myF)
        self.assertEqual(myDsb.mnem,            b'HDT ')
        self.assertEqual(myDsb.servId,          b'ServID')
        self.assertEqual(myDsb.servOrd,         b'ServOrdN')
        self.assertEqual(myDsb.units,           b'    ')
        self.assertEqual(myDsb.apiLogType,      45)
        self.assertEqual(myDsb.apiCurveType,    310)
        self.assertEqual(myDsb.apiCurveClass,   1)        
        self.assertEqual(myDsb.apiModifier,     1)
        self.assertEqual(myDsb.fileNumber,      256)
        self.assertEqual(myDsb.size,            90)        
        self.assertEqual(myDsb._samples,        1)
        self.assertEqual(myDsb.repCode,         234)
        self.assertEqual(myDsb.subChannels,     15)
        self.assertEqual(myDsb.bursts(0),       1)
        self.assertEqual(myDsb.bursts(1),       1)
        self.assertEqual(myDsb.bursts(2),       1)
        self.assertEqual(myDsb.bursts(3),       1)
        self.assertEqual(myDsb.bursts(4),       1)
        self.assertEqual(myDsb.bursts(5),       1)
        self.assertEqual(myDsb.bursts(6),       1)
        self.assertEqual(myDsb.bursts(7),       1)
        self.assertEqual(myDsb.bursts(8),       1)
        self.assertEqual(myDsb.bursts(9),       1)
        self.assertEqual(myDsb.bursts(10),       1)
        self.assertEqual(myDsb.bursts(11),       1)
        self.assertEqual(myDsb.bursts(12),       1)
        self.assertEqual(myDsb.bursts(13),       1)
        self.assertEqual(myDsb.bursts(14),       1)
        self.assertEqual(myDsb.samples(0),      16)
        self.assertEqual(myDsb.samples(1),      16)
        self.assertEqual(myDsb.samples(2),      16)
        self.assertEqual(myDsb.samples(3),      16)
        self.assertEqual(myDsb.samples(4),      16)
        self.assertEqual(myDsb.samples(5),      1)
        self.assertEqual(myDsb.samples(6),      1)
        self.assertEqual(myDsb.samples(7),      1)
        self.assertEqual(myDsb.samples(8),      1)
        self.assertEqual(myDsb.samples(9),      1)
        self.assertEqual(myDsb.samples(10),     1)
        self.assertEqual(myDsb.samples(11),     1)
        self.assertEqual(myDsb.samples(12),     1)
        self.assertEqual(myDsb.samples(13),     1)
        self.assertEqual(myDsb.samples(14),     1)
        self.assertRaises(IndexError, myDsb.samples, -1)
        self.assertRaises(IndexError, myDsb.samples, 15)

    def test_20(self):
        """TestDatumSpecBlock.test_20(): Read from file with bad Rep Code 1 and zero LIS length."""
        # Logical record header for DFSR
        myB = bytes([64, 0])
        # Mnemonic
        myB += b'GR  '
        # Service ID
        myB += b'ServID'
        # Service order number
        myB += b'ServOrdN'
        # Units
        myB += b'GAPI'
        # API codes 45, 310, 01, 1
        # Decimal 45310011 is 0x02b3603b
        myB += b'\x02\xb3\x60\x3b'
        # File number: 256
        myB += bytes([1, 0])
        # LIS size in bytes: 0
        myB += bytes([0, 0])
        # Padding '0'
        myB += b'000'
        # Samples: 4 super samples
        myB += bytes([0,])
        # Representation code
        myB += bytes([1,])
        # Process indicators
        myB += bytes([0, 1, 2, 3, 4])
        myF = self._retFileSinglePr(myB)
        self.assertEqual(myF.readLrBytes(2), b'@\x00')
        myDsb = LogiRec.DatumSpecBlockRead(myF)
        self.assertEqual(myDsb.mnem,            b'GR  ')
        self.assertEqual(myDsb.servId,          b'ServID')
        self.assertEqual(myDsb.servOrd,         b'ServOrdN')
        self.assertEqual(myDsb.units,           b'GAPI')
        self.assertEqual(myDsb.apiLogType,      45)
        self.assertEqual(myDsb.apiCurveType,    310)
        self.assertEqual(myDsb.apiCurveClass,   1)        
        self.assertEqual(myDsb.apiModifier,     1)
        self.assertEqual(myDsb.fileNumber,      256)
        self.assertEqual(myDsb.size,            0)        
        self.assertEqual(myDsb._samples,        0)
        self.assertEqual(myDsb.repCode,         1)
        self.assertEqual(myDsb.subChannels,     0)
        self.assertEqual(myDsb.bursts(0),       0)
        self.assertRaises(IndexError, myDsb.samples, 0)
        self.assertRaises(IndexError, myDsb.samples, -1)
        self.assertRaises(IndexError, myDsb.samples, 1)

class TestDFSR(TestLrBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass
    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestDFSR: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestDFSR.test_00(): LogiRec.LrDFSR() construction."""
        myF = self._retFileSinglePr(
            # Logical record header for DFSR
            bytes([64, 0])
            # Entry block 4, value 0
            + bytes([4, 1, 66, 0])
            # Entry block 12, value -153.0
            + bytes([12, 4, 68])
            + b'\xbb\xb3\x80\x00'
            # Entry block 0, value None terminates read
            + bytes([0, 1, 66, 0])
            # Sensor 0
            # Mnemonic
            + b'DEPT'
            # Service ID
            + b'ServID'
            # Service order number
            + b'ServOrdN'
            # Units
            + b'FEET'
            # API codes 45, 310, 01, 1
            # Decimal 45310011 is 0x02b3603b
            + b'\x02\xb3\x60\x3b'
            # File number: 256
            + bytes([1, 0])
            # LIS size in bytes: 4 bytes
            + bytes([0, 4])
            # Padding '0'
            + b'000'
            # Samples: 1 super samples
            + b'\x01'
            # Representation code
            + bytes([68,])
            # Process indicators
            + bytes([0, 1, 2, 3, 4])
            # Sensor 1
            # Mnemonic
            + b'GR  '
            # Service ID
            + b'ServID'
            # Service order number
            + b'ServOrdN'
            # Units
            + b'GAPI'
            # API codes 45, 310, 01, 1
            # Decimal 45310011 is 0x02b3603b
            + b'\x02\xb3\x60\x3b'
            # File number: 256
            + bytes([1, 0])
            # LIS size in bytes: 4 samples * 6 burst samples * 4 bytes = 96 bytes
            + bytes([0, 96])
            # Padding '0'
            + b'000'
            # Samples: 4 super samples
            + bytes([4,])
            # Representation code
            + bytes([68,])
            # Process indicators
            + bytes([0, 1, 2, 3, 4])
        )
        myLr = LogiRec.LrDFSRRead(myF)
        self.assertEqual(len(myLr.dsbBlocks), 2)
        self.assertEqual(myLr.frameSize(), 100)

class TestNormalAltData(TestLrBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass
    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestNormalAltData: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestNormalAltData.test_00(): LogiRec.LrNormalAlternateData() construction fails."""
        self.assertRaises(LogiRec.ExceptionLrNotImplemented, LogiRec.LrNormalAlternateData, 0, 0)
    
    def test_01(self):
        """TestNormalAltData.test_00(): LogiRec.LrNormalAlternateDataRead() construction fails."""
        myF = self._retFileSinglePr(bytes([0, 0]))
        self.assertRaises(LogiRec.ExceptionLrNotImplemented, LogiRec.LrNormalAlternateDataRead, myF)

class TestLrFactory(TestLrBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass
    def tearDown(self):
        """Tear down."""
        pass

    def test_SetUpTearDown(self):
        """TestLrFactory: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestLrFactory.test_00(): LogiRec.LrFactory() construction."""
        myLrf = LogiRec.LrFactory()
        #print(myLrf)
        #print(myLrf._lrMap)
        
    def test_01(self):
        """TestLrFactory.test_00(): LogiRec.LrFactoryRead() construction of a single DFSR."""
        myF = self._retFileSinglePr(
            # Logical record header for DFSR
            bytes([64, 0])
            # Entry block 4, value 0
            + bytes([4, 1, 66, 0])
            # Entry block 12, value -153.0
            + bytes([12, 4, 68])
            + b'\xbb\xb3\x80\x00'
            # Entry block 0, value None terminates read
            + bytes([0, 1, 66, 0])
            # Sensor 0
            # Mnemonic
            + b'DEPT'
            # Service ID
            + b'ServID'
            # Service order number
            + b'ServOrdN'
            # Units
            + b'FEET'
            # API codes 45, 310, 01, 1
            # Decimal 45310011 is 0x02b3603b
            + b'\x02\xb3\x60\x3b'
            # File number: 256
            + bytes([1, 0])
            # LIS size in bytes: 4 bytes
            + bytes([0, 4])
            # Padding '0'
            + b'000'
            # Samples: 1 super samples
            + b'\x01'
            # Representation code
            + bytes([68,])
            # Process indicators
            + bytes([0, 1, 2, 3, 4])
            # Sensor 1
            # Mnemonic
            + b'GR  '
            # Service ID
            + b'ServID'
            # Service order number
            + b'ServOrdN'
            # Units
            + b'GAPI'
            # API codes 45, 310, 01, 1
            # Decimal 45310011 is 0x02b3603b
            + b'\x02\xb3\x60\x3b'
            # File number: 256
            + bytes([1, 0])
            # LIS size in bytes: 4 samples * 6 burst smples * 4 bytes = 96 bytes
            + bytes([0, 96])
            # Padding '0'
            + b'000'
            # Samples: 4 super samples
            + bytes([4,])
            # Representation code
            + bytes([68,])
            # Process indicators
            + bytes([0, 1, 2, 3, 4])
        )
        myLrfr = LogiRec.LrFactoryRead()
        #print(myLrfr)
        #print(myLrfr._lrMap)
        myLr = myLrfr.retLrFromFile(myF)
        #print(myLr)
        self.assertEqual(myLr.desc, 'Data format specification record')
        self.assertEqual(len(myLr.dsbBlocks), 2)
      
class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLrBaseClass))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLrMarker))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLrWithDateField))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLrFileHeadTail))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLrTapeHeadTail))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLrReelHeadTail))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLrMisc))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCbEngValRead))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCbEngValWrite))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTableRow))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLrTableSimple))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLrTableDupeRow))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLrTableBadBlocks))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLrTableSingleParameter))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLrTableSingleParameterIllFormed))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLrTableSpecific))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLrTableWrite))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEntryBlock))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEntryBlockSet))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDatumSpecBlock))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDFSR))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestNormalAltData))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLrFactory))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print(
"""TestClass.py - A module that tests something.
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
