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
"""
"""

__author__  = 'Paul Ross'
__date__    = '6 Dec 2010'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2010 Paul Ross.'

#import pprint
import sys
import time
import os
import logging
import struct
import io

from TotalDepth.LIS.core import RepCode
# Python reference methods
from TotalDepth.LIS.core import pRepCode
## Cython methods
from TotalDepth.LIS.core import cRepCode

######################
# Section: Unit tests.
######################
import unittest

TEST_DIR = os.path.dirname(__file__)

class TestReadClass(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestReadClass: Tests setUp() and tearDown()."""
        pass

    def _readBuf(self, bufLen):
        """TestReadClass: Read binary; buffer len     1."""
        tS = time.clock()
        byteCount = 0
        fileCount = 0
        for aFileName in os.listdir(TEST_DIR):
            fileCount += 1
            fpath = os.path.join(TEST_DIR, aFileName)
            if os.path.isfile(fpath):
                with open(os.path.join(fpath), 'rb') as f:
                    while 1:
                        b = f.read(bufLen)
                        byteCount += len(b)
                        if len(b) != bufLen:
                            break
        return fileCount, byteCount, (time.clock() - tS)
        
    def test_0001(self):
        """TestReadClass: Read binary; buffer len     1."""
        f, b, t = self._readBuf(1)
        sys.stderr.write('Read: {:8.3f} Rate {:12.1f} kB/S Cost: {:.3f} (ms/MB)'.format(t, b/(1024*t),(t*1024)/(b/(1024*1024))))

    def test_0002(self):
        """TestReadClass: Read binary; buffer len     2."""
        f, b, t = self._readBuf(2)
        sys.stderr.write('Read: {:8.3f} Rate {:12.1f} kB/S Cost: {:.3f} (ms/MB)'.format(t, b/(1024*t),(t*1024)/(b/(1024*1024))))

    def test_0004(self):
        """TestReadClass: Read binary; buffer len     4."""
        f, b, t = self._readBuf(4)
        sys.stderr.write('Read: {:8.3f} Rate {:12.1f} kB/S Cost: {:.3f} (ms/MB)'.format(t, b/(1024*t),(t*1024)/(b/(1024*1024))))

    def test_0008(self):
        """TestReadClass: Read binary; buffer len     8."""
        f, b, t = self._readBuf(8)
        sys.stderr.write('Read: {:8.3f} Rate {:12.1f} kB/S Cost: {:.3f} (ms/MB)'.format(t, b/(1024*t),(t*1024)/(b/(1024*1024))))

    def test_0016(self):
        """TestReadClass: Read binary; buffer len    16."""
        f, b, t = self._readBuf(16)
        sys.stderr.write('Read: {:8.3f} Rate {:12.1f} kB/S Cost: {:.3f} (ms/MB)'.format(t, b/(1024*t),(t*1024)/(b/(1024*1024))))

    def test_0032(self):
        """TestReadClass: Read binary; buffer len    32."""
        f, b, t = self._readBuf(32)
        sys.stderr.write('Read: {:8.3f} Rate {:12.1f} kB/S Cost: {:.3f} (ms/MB)'.format(t, b/(1024*t),(t*1024)/(b/(1024*1024))))

    def test_0064(self):
        """TestReadClass: Read binary; buffer len    64."""
        f, b, t = self._readBuf(64)
        sys.stderr.write('Read: {:8.3f} Rate {:12.1f} kB/S Cost: {:.3f} (ms/MB)'.format(t, b/(1024*t),(t*1024)/(b/(1024*1024))))

    def test_0128(self):
        """TestReadClass: Read binary; buffer len   128."""
        f, b, t = self._readBuf(128)
        sys.stderr.write('Read: {:8.3f} Rate {:12.1f} kB/S Cost: {:.3f} (ms/MB)'.format(t, b/(1024*t),(t*1024)/(b/(1024*1024))))

    def test_0256(self):
        """TestReadClass: Read binary; buffer len   256."""
        f, b, t = self._readBuf(256)
        sys.stderr.write('Read: {:8.3f} Rate {:12.1f} kB/S Cost: {:.3f} (ms/MB)'.format(t, b/(1024*t),(t*1024)/(b/(1024*1024))))

    def test_0512(self):
        """TestReadClass: Read binary; buffer len   512."""
        f, b, t = self._readBuf(512)
        sys.stderr.write('Read: {:8.3f} Rate {:12.1f} kB/S Cost: {:.3f} (ms/MB)'.format(t, b/(1024*t),(t*1024)/(b/(1024*1024))))

    def test_1024(self):
        """TestReadClass: Read binary; buffer len  1024."""
        f, b, t = self._readBuf(1024)
        sys.stderr.write('Read: {:8.3f} Rate {:12.1f} kB/S Cost: {:.3f} (ms/MB)'.format(t, b/(1024*t),(t*1024)/(b/(1024*1024))))

    def test_2048(self):
        """TestReadClass: Read binary; buffer len  2048."""
        f, b, t = self._readBuf(2048)
        sys.stderr.write('Read: {:8.3f} Rate {:12.1f} kB/S Cost: {:.3f} (ms/MB)'.format(t, b/(1024*t),(t*1024)/(b/(1024*1024))))

    def test_4096(self):
        """TestReadClass: Read binary; buffer len  4096."""
        f, b, t = self._readBuf(4096)
        sys.stderr.write('Read: {:8.3f} Rate {:12.1f} kB/S Cost: {:.3f} (ms/MB)'.format(t, b/(1024*t),(t*1024)/(b/(1024*1024))))

    def test_8192(self):
        """TestReadClass: Read binary; buffer len  8192."""
        f, b, t = self._readBuf(8192)
        sys.stderr.write('Read: {:8.3f} Rate {:12.1f} kB/S Cost: {:.3f} (ms/MB)'.format(t, b/(1024*t),(t*1024)/(b/(1024*1024))))

class TestReadStructClass(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestReadClass: Tests setUp() and tearDown()."""
        pass

    def _readStructCompiled(self, theFormat):
        # We exclude compilation time as in practice that is a one-of task
        myStruct = struct.Struct(theFormat)
        bufLen = struct.calcsize(theFormat)
        tS = time.clock()
        byteCount = 0
        fileCount = 0
        for aFileName in os.listdir(TEST_DIR):
            fpath = os.path.join(TEST_DIR, aFileName)
            if os.path.isfile(fpath):
                with open(os.path.join(fpath), 'rb') as f:
                    while 1:
                        b = f.read(bufLen)
                        byteCount += len(b)
                        if len(b) != bufLen:
                            break
                        myStruct.unpack(b)
                fileCount += 1
        return fileCount, byteCount, (time.clock() - tS)
        
    def _readStructCompiledNot(self, theFormat):
        bufLen = struct.calcsize(theFormat)
        tS = time.clock()
        byteCount = 0
        fileCount = 0
        for aFileName in os.listdir(TEST_DIR):
            fpath = os.path.join(TEST_DIR, aFileName)
            if os.path.isfile(fpath):
                with open(os.path.join(TEST_DIR, aFileName), 'rb') as f:
                    while 1:
                        b = f.read(bufLen)
                        byteCount += len(b)
                        if len(b) != bufLen:
                            break
                        struct.unpack(theFormat, b)
                fileCount += 1
        return fileCount, byteCount, (time.clock() - tS)
        
    def _readStruct(self, theFormat):
        raise NotImplementedError
        
class TestReadStructClassInteger(TestReadStructClass):
    """Base class for reading bytes as integers."""
    FORMAT_MAP = {
        1       : '>B',
        2       : '>H',
        4       : '>I',
        8       : '>2I',
        16      : '>4I',
        32      : '>8I',
        64      : '>16I',
        128     : '>32I',
        256     : '>64I',
        512     : '>128I',
        1024    : '>256I',
        2048    : '>512I',
        4096    : '>1024I',
        8192    : '>2048I',
    }

    def _readStruct(self, theFormat):
        return self._readStructCompiledNot(theFormat)

    def test_all(self):
        """TestReadStructClassInteger: Read and unpack binary; all buffer lengths."""
        print()
        for k in sorted(self.FORMAT_MAP.keys()):
            assert(k == struct.calcsize(self.FORMAT_MAP[k])), \
                'k={:d} calcsize()={:d}'.format(k, struct.calcsize(self.FORMAT_MAP[k]))
            f, b, t = self._readStruct(self.FORMAT_MAP[k])
            print('Buffer len  {:d}. Read: {:8.3f} Rate {:12.1f} kB/S'
                  ' Cost: {:.3f} (ms/MB)'.format(k, t, b/(1024*t),(t*1024)/(b/(1024*1024))))

class TestReadStructClassIntegerCompiledNot(TestReadStructClassInteger):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        sys.stderr.write('TestReadStructClassIntegerCompiledNot(): ')
        TestReadStructClass.setUp(self)

    def tearDown(self):
        """Tear down."""
        pass
        
    def _readStruct(self, theFormat):
        return self._readStructCompiledNot(theFormat)
        
class TestReadStructClassIntegerCompiled(TestReadStructClassInteger):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        sys.stderr.write('TestReadStructClassIntegerCompiled(): ')
        TestReadStructClass.setUp(self)

    def tearDown(self):
        """Tear down."""
        pass
                
    def _readStruct(self, theFormat):
        return self._readStructCompiled(theFormat)

class TestReadStructClassFloat(TestReadStructClass):
    """Base class for reading bytes as floating point numbers."""
    FORMAT_MAP = {
        4       : '>f',
        8       : '>d',
        16      : '>2d',
        32      : '>4d',
        64      : '>8d',
        128     : '>16d',
        256     : '>32d',
        512     : '>64d',
        1024    : '>128d',
        2048    : '>256d',
        4096    : '>512d',
        8192    : '>1024d',
    }

class TestReadStructClassFloatCompiledNot(TestReadStructClassFloat):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        sys.stderr.write('TestReadStructClassFloatCompiledNot(): ')
        TestReadStructClass.setUp(self)

    def tearDown(self):
        """Tear down."""
        pass
        
    def _readStruct(self, theFormat):
        return self._readStructCompiledNot(theFormat)
        
class TestReadStructClassFloatCompiled(TestReadStructClassFloat):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        sys.stderr.write('TestReadStructClassFloatCompiled(): ')
        TestReadStructClass.setUp(self)

    def tearDown(self):
        """Tear down."""
        pass
                
    def _readStruct(self, theFormat):
        return self._readStructCompiled(theFormat)

class TestSeek(unittest.TestCase):
    """Tests how long is takes to seek various buffer lengths."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestReadClass: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """Time to open a file and seek to bytes"""
        print()
        for sLen in [2**n for n in range(14)]:
            byteCount = 0
            tE = 0.0
            fileCount = 0
            for aFileName in os.listdir(TEST_DIR):
                fpath = os.path.join(TEST_DIR, aFileName)
                if os.path.isfile(fpath):
                    try:
                        with open(fpath, 'rb') as f:
                            fSize = f.seek(0, os.SEEK_END)
                            f.seek(0, os.SEEK_SET)
                            tS = time.clock()
                            numSeeks = 1 + int(fSize / sLen)
                            i = 0
                            while i < numSeeks:
                                f.seek(sLen, os.SEEK_CUR)
                                i += 1
                            tE += time.clock() - tS
                            byteCount += fSize
                        fileCount += 1
                    except IOError as err:
                        print(err)
            print('Seek len {:d} Time: {:8.3f} Rate {:8.1f} MB/S, {:8.1f} file/S Cost: {:.3f} (ms/MB) '.format(
                    sLen, tE, byteCount/(1024*1024*tE), fileCount/tE,(tE*1024)/(byteCount/(1024*1024))))
        #sys.stderr.write('Time: {:.3f} Rate {:.1f} Files/S Cost: {:.3f} (uS) '.format(
        #        tE, fileCount/tE,(tE*1024*1024)/fileCount))
        
class TestSeekEOF(unittest.TestCase):
    """Tests how long is takes to seek to EOF-256 bytes"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestReadClass: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """Time to open a file and seek to EOF bytes"""
        tS = time.clock()
        fileCount = 0
        byteCount = 0
        for aFileName in os.listdir(TEST_DIR):
            fpath = os.path.join(TEST_DIR, aFileName)
            if os.path.isfile(fpath):
                try:
                    with open(fpath, 'rb') as f:
                        byteCount += f.seek(0, io.SEEK_END)
                except IOError as err:
                    print(err)
                fileCount += 1
        tE = time.clock() - tS
        #sys.stderr.write('Time: {:.3f} Rate {:.1f} Files/S Cost: {:.3f} (uS) '.format(
        #        tE, fileCount/tE,(tE*1024*1024)/fileCount))
        sys.stderr.write('Time: {:8.3f} Rate {:8.1f} MB/S, {:8.1f} file/S Cost: {:.3f} (ms/MB) '.format(
                tE, byteCount/(1024*1024*tE), fileCount/tE,(tE*1024)/(byteCount/(1024*1024))))
        
class TestSeekEOFSimulateIndexRead(unittest.TestCase):
    """Tests how long is takes to seek to EOF-256 bytes"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestReadClass: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """Open, seek EOF, seek EOF-256, read 256, seek EOF-(2048+256), read 2048 bytes"""
        fileCount = 0
        byteCount = 0
        tS = time.clock()
        for aFileName in os.listdir(TEST_DIR):
            fpath = os.path.join(TEST_DIR, aFileName)
            if os.path.isfile(fpath):
                with open(os.path.join(fpath), 'rb') as f:
                    siz = f.seek(0, io.SEEK_END)
                    if siz > 2048+256:
                        byteCount += siz
                        f.seek(-256, io.SEEK_END)
                        f.read(256)
                        f.seek(-(256+2048), io.SEEK_END)
                        f.read(2048)
                        fileCount += 1
        tE = time.clock() - tS
        #sys.stderr.write('Time: {:.3f} Rate {:.1f} Files/S Cost: {:.3f} (uS) '.format(
        #        tE, fileCount/tE,(tE*1024*1024)/fileCount))
        sys.stderr.write('Time: {:8.3f} Rate {:8.1f} MB/S, {:8.1f} file/S Cost: {:8.3f} (ms/MB) '.format(
                tE, byteCount/(1024*1024*tE), fileCount/tE,(tE*1024)/(byteCount/(1024*1024))))
        
class TestReadStructClass_RepCode68(TestReadStructClass):
    """Base class for reading bytes as integers."""
    FORMAT_MAP = {
        4       : '>I',
        8       : '>2I',
        16      : '>4I',
        32      : '>8I',
        64      : '>16I',
        128     : '>32I',
        256     : '>64I',
        512     : '>128I',
        1024    : '>256I',
        2048    : '>512I',
        4096    : '>1024I',
        8192    : '>2048I',
    }
  
class TestReadRepCode_p68(TestReadStructClass_RepCode68):
    """Tests how long is takes to read random binary bytes to RepCode 68"""
    def setUp(self):
        """Set up."""
        sys.stderr.write('TestReadRepCode_p68(): Python code: ')
        TestReadStructClass.setUp(self)

    def _readStructCompiled_p68(self, theFormat):
        # We exclude compilation time as in practice that is a one-of task
        myStruct = struct.Struct(theFormat)
        bufLen = struct.calcsize(theFormat)
        tS = time.clock()
        byteCount = 0
        fileCount = 0
        for aFileName in os.listdir(TEST_DIR):
            fpath = os.path.join(TEST_DIR, aFileName)
            if os.path.isfile(fpath):
                with open(os.path.join(fpath), 'rb') as f:
                    while 1:
                        b = f.read(bufLen)
                        byteCount += len(b)
                        if len(b) != bufLen:
                            break
                        # Convert from RepCod 68
                        for w in myStruct.unpack(b):
                            pRepCode.from68(w)
                fileCount += 1
        return fileCount, byteCount, (time.clock() - tS)

    def _readStruct(self, theFormat):
        return self._readStructCompiled_p68(theFormat)

class TestReadRepCode_c68(TestReadStructClass_RepCode68):
    """Tests how long is takes to read random binary bytes to RepCode 68"""
    def setUp(self):
        """Set up."""
        sys.stderr.write('TestReadRepCode_c68(): Cython code: ')
        TestReadStructClass.setUp(self)

    def _readStructCompiled_c68(self, theFormat):
        # We exclude compilation time as in practice that is a one-of task
        myStruct = struct.Struct(theFormat)
        bufLen = struct.calcsize(theFormat)
        tS = time.clock()
        byteCount = 0
        fileCount = 0
        for aFileName in os.listdir(TEST_DIR):
            fpath = os.path.join(TEST_DIR, aFileName)
            if os.path.isfile(fpath):
                with open(os.path.join(fpath), 'rb') as f:
                    while 1:
                        b = f.read(bufLen)
                        byteCount += len(b)
                        if len(b) != bufLen:
                            break
                        # Convert from RepCod 68
                        for w in myStruct.unpack(b):
                            cRepCode.from68(w)
                fileCount += 1
        return fileCount, byteCount, (time.clock() - tS)

    def _readStruct(self, theFormat):
        return self._readStructCompiled_c68(theFormat)

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestReadClass))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestReadStructClassIntegerCompiledNot))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestReadStructClassIntegerCompiled))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestReadStructClassFloatCompiledNot))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestReadStructClassFloatCompiled))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestReadRepCode_p68))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestReadRepCode_c68))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSeek))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSeekEOF))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSeekEOFSimulateIndexRead))
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
    if len(args) not in (0, 1):
        usage()
        print('ERROR: Wrong number of arguments!')
        sys.exit(1)
    # Initialise logging etc.
    logging.basicConfig(level=logLevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    clkStart = time.clock()
    global TEST_DIR
    if len(args):
        TEST_DIR = args[0]
    unitTest()
    clkExec = time.clock() - clkStart
    print(('CPU time = %8.3f (S)' % clkExec))
    print('Bye, bye!')

if __name__ == "__main__":
    main()
