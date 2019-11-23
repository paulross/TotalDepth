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
"""Unit tests for the LIS File module.
"""
import pytest

__author__  = 'Paul Ross'
__date__    = '8 Nov 2010'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2010 Paul Ross.'

import io
import os
import sys
import time
import logging

from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import RepCode

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import BaseTestClasses

######################
# Section: Unit tests.
######################
import unittest

class TestFileLowLevel(BaseTestClasses.TestBaseFile):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestFileLowLevel.test_00(): Tests setUp() and tearDown()."""
        pass


@pytest.mark.slow
class TestFileType0Base(BaseTestClasses.TestBaseFile):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        # 1024 LR * 8 frames = 8192 frames
        # 256 ch * 1 * 4 bytes = 1024 byte frame length
        # Total: 8192 * 1024 = 8MB
        # Values: 2*1024*1024 = 2097152
        self_bytes = self._retLr0Bytes(lr=1024, fr=8, ch=256, sa=1, bu=1)
        #self_bytes = self._retLr0Bytes(lr=1, fr=2, ch=256, sa=1, bu=1)
        #print()
        #print('len(myB)', len(myB))
        self._file = self._retFileFromBytes(self_bytes, theId='MyFile', flagKg=False)

    def tearDown(self):
        """Tear down."""
        pass

    def _ReadFileWithBufferSizeRepCode(self, bufSiz):
        """Reads a file with a particular buffer size."""
        tS = time.perf_counter()
        # Iterate through file
        wordCntr = 0
        while not self._file.isEOF:
            lrh = self._file.readLrBytes(2)
            while self._file.hasLd():
                b = self._file.readLrBytes(bufSiz)
                for i in range(0, bufSiz, 4):
                    v = RepCode.readBytes68(b[i:i+4])
                    wordCntr += 1
        self.writeCostToStderr(tS, 4*wordCntr, 'Words', wordCntr)
    
    def _ReadFileWithBufferSize(self, bufSiz):
        """Reads a file with a particular buffer size."""
        tS = time.perf_counter()
        # Iterate through file
        byteCntr = 0
        while not self._file.isEOF:
            lrh = self._file.readLrBytes(2)
            #print('lrh', lrh)
            while self._file.hasLd():
                b = self._file.readLrBytes(bufSiz)
                byteCntr += len(b)
        self.writeCostToStderr(tS, byteCntr, 'Words', byteCntr//4)


@pytest.mark.slow
class TestFileType0(TestFileType0Base):
    """Tests ..."""
    def test_00(self):
        """TestFileType0.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def _ReadFileWithBufferSizeRepCode(self, bufSiz):
        """Reads a file with a particular buffer size."""
        tS = time.perf_counter()
        # Iterate through file
        wordCntr = 0
        while not self._file.isEOF:
            lrh = self._file.readLrBytes(2)
            while self._file.hasLd():
                b = self._file.readLrBytes(bufSiz)
                for i in range(0, bufSiz, 4):
                    v = RepCode.readBytes68(b[i:i+4])
                    wordCntr += 1
        self.writeCostToStderr(tS, 4*wordCntr, 'Words', wordCntr)
    
    def _ReadFileWithBufferSize(self, bufSiz):
        """Reads a file with a particular buffer size."""
        tS = time.perf_counter()
        # Iterate through file
        byteCntr = 0
        while not self._file.isEOF:
            lrh = self._file.readLrBytes(2)
            while self._file.hasLd():
                b = self._file.readLrBytes(bufSiz)
                byteCntr += len(b)
        self.writeCostToStderr(tS, byteCntr, 'Words', byteCntr//4)
    
    def test_01(self):
        """TestFileType0.test_01(): 8MB Type 0 data Repcode 68,    4 byte reads."""
        tS = time.perf_counter()
        # Iterate through file
        wordCntr = 0
        while not self._file.isEOF:
            lrh = self._file.readLrBytes(2)
            while self._file.hasLd():
                v = RepCode.read68(self._file)
                wordCntr += 1
        self.writeCostToStderr(tS, 4*wordCntr, 'Words', wordCntr)

    def test_02(self):
        """TestFileType0.test_02(): 8MB Type 0 data Repcode 68,    8 byte reads."""
        self._ReadFileWithBufferSizeRepCode(8)
    
    def test_03(self):
        """TestFileType0.test_03(): 8MB Type 0 data Repcode 68,   16 byte reads."""
        self._ReadFileWithBufferSizeRepCode(16)
    
    def test_04(self):
        """TestFileType0.test_04(): 8MB Type 0 data Repcode 68,   32 byte reads."""
        self._ReadFileWithBufferSizeRepCode(32)
    
    def test_05(self):
        """TestFileType0.test_05(): 8MB Type 0 data Repcode 68,   64 byte reads."""
        self._ReadFileWithBufferSizeRepCode(64)
    
    def test_06(self):
        """TestFileType0.test_06(): 8MB Type 0 data Repcode 68,  128 byte reads."""
        self._ReadFileWithBufferSizeRepCode(128)
    
    def test_07(self):
        """TestFileType0.test_07(): 8MB Type 0 data Repcode 68,  256 byte reads."""
        self._ReadFileWithBufferSizeRepCode(256)
    
    def test_08(self):
        """TestFileType0.test_08(): 8MB Type 0 data Repcode 68,  512 byte reads."""
        self._ReadFileWithBufferSizeRepCode(512)
    
    def test_09(self):
        """TestFileType0.test_09(): 8MB Type 0 data Repcode 68, 1024 byte reads."""
        self._ReadFileWithBufferSizeRepCode(1024)
    
    def test_10_00(self):
        """TestFileType0.test_10(): 8MB Type 0 data,    1 byte reads."""
        self._ReadFileWithBufferSize(1)
    
    def test_10_01(self):
        """TestFileType0.test_10(): 8MB Type 0 data,    2 byte reads."""
        self._ReadFileWithBufferSize(2)
    
    def test_10_02(self):
        """TestFileType0.test_10(): 8MB Type 0 data,    4 byte reads."""
        self._ReadFileWithBufferSize(4)
    
    def test_11(self):
        """TestFileType0.test_11(): 8MB Type 0 data,    8 byte reads."""
        self._ReadFileWithBufferSize(8)
    
    def test_12(self):
        """TestFileType0.test_12(): 8MB Type 0 data,   16 byte reads."""
        self._ReadFileWithBufferSize(16)
    
    def test_13(self):
        """TestFileType0.test_13(): 8MB Type 0 data,   32 byte reads."""
        self._ReadFileWithBufferSize(32)
    
    def test_14(self):
        """TestFileType0.test_14(): 8MB Type 0 data,   64 byte reads."""
        self._ReadFileWithBufferSize(64)
    
    def test_15(self):
        """TestFileType0.test_15(): 8MB Type 0 data,  128 byte reads."""
        self._ReadFileWithBufferSize(128)
    
    def test_16(self):
        """TestFileType0.test_16(): 8MB Type 0 data,  256 byte reads."""
        self._ReadFileWithBufferSize(256)
    
    def test_17(self):
        """TestFileType0.test_17(): 8MB Type 0 data,  512 byte reads."""
        self._ReadFileWithBufferSize(512)
    
    def test_18(self):
        """TestFileType0.test_18(): 8MB Type 0 data, 1024 byte reads."""
        self._ReadFileWithBufferSize(1024)


@pytest.mark.slow
class TestFileType0_Profile(TestFileType0Base):
    """Special tests."""
    
    def test_00(self):
        """TestFileType0_Profile.test_00(): 8MB Type 0 data,    4 byte reads."""
        self._ReadFileWithBufferSize(4)
        

@pytest.mark.slow
class Special(unittest.TestCase):
    pass


@pytest.mark.slow
class SpecialType0(TestFileType0Base):
    """Special tests."""
    def test_10_00(self):
        """TestFileType0.test_10(): 8MB Type 0 data,    1 byte reads."""
        self._ReadFileWithBufferSize(1)
    
    def test_10_01(self):
        """TestFileType0.test_10(): 8MB Type 0 data,    2 byte reads."""
        self._ReadFileWithBufferSize(2)
    
    def test_10_02(self):
        """TestFileType0.test_10(): 8MB Type 0 data,    4 byte reads."""
        self._ReadFileWithBufferSize(4)
        

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileLowLevel))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileType0))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileType0_Profile))
    #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(SpecialType0))
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
