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
"""Unit tests for the RawStream module.
"""

__author__  = 'Paul Ross'
__date__    = '8 Nov 2010'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2010 Paul Ross.'

#import pprint
import sys
import io
import time
import logging
import random
import struct
from TotalDepth.LIS.core import RawStream

######################
# Section: Unit tests.
######################
import unittest
try:
    import io as StringIO
except ImportError:
    import io

class TestRawStream(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRawStream: Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestRawStream: ctor with empty string."""
        myS = io.StringIO('')
        RawStream.RawStream(myS, fileId='MyFile')

    def test_03(self):
        """TestRawStream: readWord() read specific word and use seek() and tell() and re-read it."""
        myS = io.BytesIO()
        myS.write(b'ABCD')
        myS.seek(0)
        myStruct = struct.Struct('>I')
        with RawStream.RawStream(myS, fileId='MyFile') as myRs:
            self.assertEqual(myRs.tell(), 0)
            self.assertEqual(myRs.readAndUnpack(myStruct), (0x41424344,))
            myRs.seek(0)
            self.assertEqual(myRs.tell(), 0)
            self.assertEqual(myRs.readAndUnpack(myStruct), (0x41424344,))
            self.assertEqual(myRs.tell(), myStruct.size)
            self.assertEqual(myRs.tell(), myRs.stream.tell())

    def test_11(self):
        """TestRawStream: write an big-endian int and read it back."""
        myIo = io.BytesIO()
        myInt = random.randint(0, 0xFFFFFFFF)
        myBytes = ''
        myStruct = struct.Struct('>L')
        self.assertEqual(myStruct.size, 4)
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            myRs.packAndWrite(myStruct, myInt)
            myBytes = myIo.getvalue()
        self.assertEqual(len(myBytes), 4)
        myIo = io.BytesIO()
        myIo.write(myBytes)
        myIo.seek(0)
        with RawStream.RawStream(myIo, fileId='MyFile') as myRs:
            self.assertEqual(myRs.readAndUnpack(myStruct), (myInt,))
            # Read at EOF
            try:
                self.assertEqual(myRs.readAndUnpack(myStruct), (myInt,))
                self.fail('ExceptionRawStream not raised at EOF')
            except RawStream.ExceptionRawStreamEOF:
                pass
        
    def test_11_01(self):
        """TestRawStream: write an little-endian int and read it back."""
        myIo = io.BytesIO()
        myInt = random.randint(0, 0xFFFFFFFF)
        myBytes = ''
        myStruct = struct.Struct('<L')
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            myRs.packAndWrite(myStruct, myInt)
            myBytes = myIo.getvalue()
            self.assertEqual(myStruct.size, 4)
        self.assertEqual(len(myBytes), 4)
        myIo = io.BytesIO()
        myIo.write(myBytes)
        myIo.seek(0)
        with RawStream.RawStream(myIo, fileId='MyFile') as myRs:
            self.assertEqual(myRs.readAndUnpack(myStruct), (myInt,))
            # Read at EOF
            try:
                self.assertEqual(myRs.readAndUnpack(myStruct), (myInt,))
                self.fail('ExceptionRawStream not raised at EOF')
            except RawStream.ExceptionRawStreamEOF:
                pass
        
    def test_12(self):
        """TestRawStream: packAndWrite()/readAndUnpack() random 32bit integer big-endian words."""
        myNum = 1024*128
        myInts = [random.randint(0, 0xFFFFFFFF) for i in range(myNum)]
        myIo = io.BytesIO()
        myBytes = ''
        myStruct = struct.Struct('>L')
        # Take tSr: time start read
        tSr = time.perf_counter()
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            for anI in myInts:
                myRs.packAndWrite(myStruct, anI)
            myBytes = myIo.getvalue()
        tE = time.perf_counter() - tSr
        sys.stderr.write('Write rate %8.1f kB/s ' \
                         % (myStruct.size * myNum/(1024*tE)))
        tSw = time.perf_counter()
        self.assertEqual(len(myBytes), 4*len(myInts))
        myIo = io.BytesIO()
        myIo.write(myBytes)
        myIo.seek(0)
        with RawStream.RawStream(myIo, fileId='MyFile') as myRs:
            for anI in myInts:
                myT = myRs.readAndUnpack(myStruct)
                #self.assertEqual(myT, (anI,))
        tE = time.perf_counter() - tSw
        sys.stderr.write('Read rate %8.1f kB/s ' \
                         % (myStruct.size * myNum/(1024*tE)))
        #sys.stderr.write('Overall %10.3f kB/s ' % (myNum/(1024*(time.perf_counter()-tSr))))
        
    def test_12_01(self):
        """TestRawStream: packAndWrite()/readAndUnpack() random 32bit integer big-endian words and test."""
        myNum = 1024*128
        myInts = [random.randint(0, 0xFFFFFFFF) for i in range(myNum)]
        myIo = io.BytesIO()
        myBytes = b''
        myStruct = struct.Struct('>L')
        LEN = 4
        self.assertEqual(myStruct.size, LEN)
        # Take time
        tS = time.perf_counter()
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            for anI in myInts:
                myRs.packAndWrite(myStruct, anI)
            myBytes = myIo.getvalue()
        #print
        #print '0x%X' % myInts[0]
        #print [hex(ord(b)) for b in myBytes]
        tE = time.perf_counter() - tS
        sys.stderr.write('Write rate %10.3f kB/s ' % (myStruct.size * myNum/(1024*tE)))
        tS = time.perf_counter()
        self.assertEqual(len(myBytes), LEN*len(myInts))
        myIo = io.BytesIO()
        myIo.write(myBytes)
        myIo.seek(0)
        with RawStream.RawStream(myIo, fileId='MyFile') as myRs:
            myIndex = 0
            for anI in myInts:
                myI = myRs.readAndUnpack(myStruct)[0]
                #mySlice = myBytes[myIndex:myIndex+LEN]
                if myI != anI:
                    print()
                    print(('Got: 0X%8x  Exp: 0X%8x Index: %d' % (myI, anI, myIndex)))
                self.assertEqual(myI, anI)
                myIndex += 1
        tE = time.perf_counter() - tS
        sys.stderr.write('Read rate %10.3f kB/s ' % (myStruct.size * myNum/(1024*tE)))

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRawStream))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestRawStream.py - A module that tests RawStream.
Usage:
python TestRawStream.py [-lh --help]

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
