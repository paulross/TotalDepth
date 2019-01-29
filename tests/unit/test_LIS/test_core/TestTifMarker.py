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
import time
import logging
import io

from TotalDepth.LIS.core import RawStream
from TotalDepth.LIS.core import TifMarker

######################
# Section: Unit tests.
######################
import unittest

class TestTifMarker(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestTifMarker: Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestTifMarker: Initialise and write EOF."""
        myTh = TifMarker.TifMarkerWrite()
        self.assertEqual('TIF  True >:  0x       0  0x       0  0x       0', str(myTh))
    
    def test_02(self):
        """TestTifMarker: Initialise and write EOF."""
        myIo = io.BytesIO()
        myTh = TifMarker.TifMarkerWrite()
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            myTh.write(myRs, 0)
            myTh.close(myRs)
            myBytes = myIo.getvalue()
        self.assertEqual(len(myBytes), 12*3)
        self.assertEqual('TIF  True >:  0x       1  0x      18  0x      24', str(myTh))
        #print
        #print myBytes.encode('unicode-escape')
        #print ''.join(['\\x%02x' % ord(c) for c in myBytes])
        self.assertEqual(
            myBytes,
            # Opening 
            b'\x00\x00\x00\x00'+b'\x00\x00\x00\x00'+b'\x0c\x00\x00\x00'\
            # EOF
            +b'\x01\x00\x00\x00'+b'\x00\x00\x00\x00'+b'\x18\x00\x00\x00'\
            +b'\x01\x00\x00\x00'+b'\x0c\x00\x00\x00'+b'\x24\x00\x00\x00'
            )
        
    def test_03(self):
        """TestTifMarker: Initialise, write a Physical Record and write EOF."""
        myIo = io.BytesIO()
        myTh = TifMarker.TifMarkerWrite()
        myPr = b'\x40' * 19
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            myTh.write(myRs, len(myPr))
            myRs.stream.write(myPr)
            myTh.close(myRs)
            myBytes = myIo.getvalue()
        self.assertEqual(len(myBytes), len(myPr)+12*3)
        self.assertEqual('TIF  True >:  0x       1  0x      2b  0x      37', str(myTh))
        #print
        #print myBytes.encode('unicode-escape')
        #print ''.join(['\\x%02x' % ord(c) for c in myBytes])
        self.assertEqual(
            myBytes,
            # Opening 
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x1f\x00\x00\x00'\
            # PR
            +b'\x40'*19\
            # EOF
            +b'\x01\x00\x00\x00\x00\x00\x00\x00\x2b\x00\x00\x00'\
            +b'\x01\x00\x00\x00\x1f\x00\x00\x00\x37\x00\x00\x00'
        )
        
    def test_03_01(self):
        """TestTifMarker: Initialise, write two Physical Records and write EOF."""
        myIo = io.BytesIO()
        myTh = TifMarker.TifMarkerWrite()
        myPr = b'\xFF' * 12
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            myTh.write(myRs, len(myPr))
            myRs.stream.write(myPr)
            myTh.write(myRs, len(myPr))
            myRs.stream.write(myPr)
            myTh.close(myRs)
            myBytes = myIo.getvalue()
        self.assertEqual(len(myBytes), len(myPr) * 2 + 12 * 4)
        self.assertEqual('TIF  True >:  0x       1  0x      3c  0x      48', str(myTh))
        # print()
        # for i in range(0, len(myBytes), 12):
        #     print(myBytes[i:i+12])
        self.assertEqual(
            myBytes,
            # Opening 
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00'
            # PR 1
            + myPr
            # TIF for PR 2
            + b'\x00\x00\x00\x00\x00\x00\x00\x000\x00\x00\x00'
            # PR 2
            + myPr
            # EOF
            + b'\x01\x00\x00\x00\x18\x00\x00\x00<\x00\x00\x00'
            + b'\x01\x00\x00\x000\x00\x00\x00H\x00\x00\x00'
        )
        
    def test_04(self):
        """TestTifMarker: Initialise, write a Physical Record and EOF and read it back."""
        myIo = io.BytesIO()
        myTmw = TifMarker.TifMarkerWrite()
        myPrS = (b'\x40' * 19, b'\x20' * 9)
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            myTmw.write(myRs, len(myPrS[0]))
            myRs.stream.write(myPrS[0])
            myTmw.write(myRs, len(myPrS[1]))
            myRs.stream.write(myPrS[1])
            myTmw.close(myRs)
            myBytes = myIo.getvalue()
        self.assertEqual(len(myBytes), len(myPrS[0])+len(myPrS[1])+3*4*4)
        self.assertEqual('TIF  True >:  0x       1  0x      40  0x      4c', str(myTmw))
        #print
        #print myBytes.encode('unicode-escape')
        #print ''.join(['\\x%02x' % ord(c) for c in myBytes])
        self.assertEqual(
            myBytes,
             b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x1f\x00\x00\x00' \
            + b'\x40'*19 \
            + b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x34\x00\x00\x00' \
            + b'\x20'*9 \
            + b'\x01\x00\x00\x00' + b'\x1f\x00\x00\x00' + b'\x40\x00\x00\x00' \
            + b'\x01\x00\x00\x00' + b'\x34\x00\x00\x00' + b'\x4c\x00\x00\x00'
        )
        # Now read it back
        myIo = io.BytesIO(myBytes)
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            myTmr = TifMarker.TifMarkerRead(myRs)
            self.assertTrue(myTmr.hasTif)
            self.assertFalse(myTmr.isReversed)
            self.assertEqual(myTmr.markers(), (0, 0, 0))
            myTmr.read(myRs)
            self.assertEqual(myTmr.markers(), (0, 0, 0x1f))
            self.assertEqual(b'\x40'*19, myRs.stream.read(19))
            #print 'tell()', myRs.tell()
            myTmr.read(myRs)
            self.assertEqual(myTmr.markers(), (0, 0, 0x34))
            self.assertEqual(b'\x20'*9, myRs.stream.read(9))
            # This reads both type 1 markers
            myTmr.read(myRs)
            self.assertEqual(myTmr.markers(), (1, 0x34, 0x4c))
            try:
                myTmr.read(myRs)
                self.fail('RawStream.ExceptionRawStream not raised')
            except RawStream.ExceptionRawStream:
                pass
        
    def test_05(self):
        """TestTifMarker: Initialise and read reversed markers."""
        myBytes = b'\x00\x00\x00\x00'+b'\x00\x00\x00\x00'+b'\x00\x00\x00\x1f'\
            +b'\x40'*19\
            +b'\x00\x00\x00\x01'+b'\x00\x00\x00\x00'+b'\x00\x00\x00\x2b'\
            +b'\x00\x00\x00\x01'+b'\x00\x00\x00\x1f'+b'\x00\x00\x00\x37'
        # Now read it back
        myIo = io.BytesIO(myBytes)
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            myTmr = TifMarker.TifMarkerRead(myRs)
            self.assertTrue(myTmr.hasTif)
            self.assertTrue(myTmr.isReversed)
            self.assertEqual(myTmr.markers(), (0, 0, 0))
            myTmr.read(myRs)
            self.assertEqual(myTmr.markers(), (0, 0, 31))
            self.assertEqual(b'\x40'*19, myRs.stream.read(19))
            #print 'tell()', myRs.tell()
            myTmr.read(myRs)
            self.assertEqual(myTmr.markers(), (1, 31, 55))
            try:
                myTmr.read(myRs)
                self.fail('RawStream.ExceptionRawStream not raised')
            except RawStream.ExceptionRawStream:
                pass
        
    def test_06(self):
        """TestTifMarker: Initialise and read, no TIF markers."""
        myBytes = b'\x40'*19
        # Now read it back
        myIo = io.BytesIO(myBytes)
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            myTmr = TifMarker.TifMarkerRead(myRs)
            self.assertFalse(myTmr.hasTif)
            self.assertEqual(myTmr.markers(), (0, 0, 0))
            myTmr.read(myRs)
            self.assertEqual(myTmr.markers(), (0, 0, 0))
            self.assertEqual(b'\x40'*19, myRs.stream.read(19))
            myTmr.read(myRs)
            self.assertEqual(myTmr.markers(), (0, 0, 0))
        
    def test_07(self):
        """TestTifMarker: Initialise and read with bad next marker."""
        myBytes = b'\x00\x00\x00\x00\x00\x00\x00\x00\x1e\x00\x00\x00'\
            +b'\x40'*19\
            +b'\x01\x00\x00\x00\x00\x00\x00\x00\x2b\x00\x00\x00'\
            +b'\x01\x00\x00\x00\x1e\x00\x00\x00\x37\x00\x00\x00'
        myIo = io.BytesIO(myBytes)
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            myTmr = TifMarker.TifMarkerRead(myRs)
            self.assertTrue(myTmr.hasTif)
            self.assertFalse(myTmr.isReversed)
            self.assertEqual(myTmr.markers(), (0, 0, 0))
            # Now read
            myTmr.read(myRs)
            self.assertEqual(myTmr.markers(), (0, 0, 30))
            self.assertEqual(b'\x40'*19, myRs.stream.read(19))
            #print 'tell()', myRs.tell()
            try:
                myTmr.read(myRs)
                self.fail('Tif read failed to raise TifMarker.ExceptionTifMarker')
            except TifMarker.ExceptionTifMarker:
                pass
            self.assertEqual(myTmr.markers(), (0, 0, 30))
            try:
                myTmr.read(myRs)
                self.fail('TifMarker.ExceptionTifMarker not raised')
            except TifMarker.ExceptionTifMarker:
                pass
        
    def test_08(self):
        """TestTifMarker: Initialise and read two Physical records with good previous markers."""
        myBytes = b'\x00\x00\x00\x00\x00\x00\x00\x00\x1f\x00\x00\x00'\
            +b'\x40'*19\
            +b'\x00\x00\x00\x00\x00\x00\x00\x00\x34\x00\x00\x00'\
            +b'\x20'*9\
            +b'\x01\x00\x00\x00\x1f\x00\x00\x00\x40\x00\x00\x00'\
            +b'\x01\x00\x00\x00\x34\x00\x00\x00\x4c\x00\x00\x00'
        myIo = io.BytesIO(myBytes)
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            myTmr = TifMarker.TifMarkerRead(myRs)
            self.assertTrue(myTmr.hasTif)
            self.assertFalse(myTmr.isReversed)
            self.assertEqual(myTmr.markers(), (0, 0, 0))
            # Now read
            myTmr.read(myRs)
            #print myTmr
            self.assertEqual(myTmr.markers(), (0, 0, 31))
            self.assertEqual(b'\x40'*19, myRs.stream.read(19))
            myTmr.read(myRs)
            #print myTmr
            self.assertEqual(myTmr.markers(), (0, 0, 52))
            self.assertEqual(b'\x20'*9, myRs.stream.read(9))
            #print 'tell()', myRs.tell()
            # EOF
            myTmr.read(myRs)
            self.assertEqual(myTmr.markers(), (1, 52, 76))
            # Read after EOF
            try:
                myTmr.read(myRs)
                self.fail('TifMarker.ExceptionTifMarker not raised')
            except RawStream.ExceptionRawStream:
                pass
            self.assertTrue(myTmr.eof)
        
    def test_09(self):
        """TestTifMarker: Initialise and read two Physical records with bad previous markers."""
        myBytes = b'\x00\x00\x00\x00\x00\x00\x00\x00\x1f\x00\x00\x00'\
            +b'\x40'*19\
            +b'\x00\x00\x00\x00\x01\x00\x00\x00\x34\x00\x00\x00'\
            +b'\x20'*9\
            +b'\x01\x00\x00\x00\x1e\x00\x00\x00\x40\x00\x00\x00'\
            +b'\x01\x00\x00\x00\x34\x00\x00\x00\x4c\x00\x00\x00'
        myIo = io.BytesIO(myBytes)
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            myTmr = TifMarker.TifMarkerRead(myRs)
            self.assertTrue(myTmr.hasTif)
            self.assertFalse(myTmr.isReversed)
            self.assertEqual(myTmr.markers(), (0, 0, 0))
            # Now read
            myTmr.read(myRs)
            #print myTmr
            self.assertEqual(myTmr.markers(), (0, 0, 31))
            self.assertEqual(b'\x40'*19, myRs.stream.read(19))
            # Should raise as \x01 rather than correct value \x00
            try:
                myTmr.read(myRs)
                self.fail('TifMarker.ExceptionTifMarker not raised')
            except TifMarker.ExceptionTifMarker:
                pass

    def test_10(self):
        """TestTifMarker: Initialise and read two Physical records and random access + reset()."""
        myBytes = b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x1f\x00\x00\x00' \
            + b'\x40'*19 \
            + b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x34\x00\x00\x00' \
            + b'\x20'*9 \
            + b'\x01\x00\x00\x00' + b'\x1f\x00\x00\x00' + b'\x40\x00\x00\x00' \
            + b'\x01\x00\x00\x00' + b'\x34\x00\x00\x00' + b'\x4c\x00\x00\x00'
        myIo = io.BytesIO(myBytes)
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            myTmr = TifMarker.TifMarkerRead(myRs)
            self.assertTrue(myTmr.hasTif)
            self.assertFalse(myTmr.isReversed)
            self.assertEqual(myTmr.markers(), (0, 0, 0))
            myTmr.read(myRs)
            self.assertEqual(myTmr.markers(), (0, 0, 0x1f))
            self.assertEqual(b'\x40'*19, myRs.stream.read(19))
            myTmr.read(myRs)
            self.assertEqual(myTmr.markers(), (0, 0, 0x34))
            self.assertEqual(b'\x20'*9, myRs.stream.read(9))
            # This reads both type 1 markers
            myTmr.read(myRs)
            self.assertEqual(myTmr.markers(), (1, 0x34, 0x4c))
            #
            # Now seek and reset
            #
            myRs.seek(0)
            myTmr.reset()
            self.assertEqual(myTmr.markers(), (0, 0, 0))
            myTmr.read(myRs)
            self.assertEqual(myTmr.markers(), (0, 0, 0x1f))
            self.assertEqual(b'\x40'*19, myRs.stream.read(19))
            myTmr.read(myRs)
            self.assertEqual(myTmr.markers(), (0, 0, 0x34))
            self.assertEqual(b'\x20'*9, myRs.stream.read(9))
            # This reads both type 1 markers
            myTmr.read(myRs)
            self.assertEqual(myTmr.markers(), (1, 0x34, 0x4c))
            try:
                myTmr.read(myRs)
                self.fail('RawStream.ExceptionRawStream not raised')
            except RawStream.ExceptionRawStream:
                pass
        
    def test_11(self):
        """TestTifMarker: Two Physical records with padding of 6 bytes fails by default."""
        myBytes = b'\x00\x00\x00\x00\x00\x00\x00\x00\x25\x00\x00\x00'\
            +b'\x40'*(19+6)\
            +b'\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00'\
            +b'\x20'*(9+6)\
            +b'\x01\x00\x00\x00\x25\x00\x00\x00\x4c\x00\x00\x00'\
            +b'\x01\x00\x00\x00\x40\x00\x00\x00\x58\x00\x00\x00'
        myIo = io.BytesIO(myBytes)
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            myTmr = TifMarker.TifMarkerRead(myRs)
            self.assertTrue(myTmr.hasTif)
            self.assertFalse(myTmr.isReversed)
            self.assertEqual(myTmr.markers(), (0, 0, 0))
            # Now read
            myTmr.read(myRs)
            #print myTmr
            self.assertEqual(myTmr.markers(), (0, 0, 0x25))
            # Simulate reading just 19 bytes of PR when 19+6 exist.
            self.assertEqual(b'\x40'*19, myRs.stream.read(19))
            self.assertRaises(TifMarker.ExceptionTifMarker, myTmr.read, myRs)
        
    def test_12(self):
        """TestTifMarker: Two Physical records with padding of 6 bytes when allowPrPadding=False."""
        myBytes = b'\x00\x00\x00\x00\x00\x00\x00\x00\x25\x00\x00\x00'\
            +b'\x40'*(19+6)\
            +b'\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00'\
            +b'\x20'*(9+6)\
            +b'\x01\x00\x00\x00\x25\x00\x00\x00\x4c\x00\x00\x00'\
            +b'\x01\x00\x00\x00\x40\x00\x00\x00\x58\x00\x00\x00'
        myIo = io.BytesIO(myBytes)
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            myTmr = TifMarker.TifMarkerRead(myRs, allowPrPadding=False)
            self.assertTrue(myTmr.hasTif)
            self.assertFalse(myTmr.isReversed)
            self.assertEqual(myTmr.markers(), (0, 0, 0))
            # Now read
            myTmr.read(myRs)
            #print myTmr
            self.assertEqual(myTmr.markers(), (0, 0, 0x25))
            # Simulate reading just 19 bytes of PR when 19+6 exist.
            self.assertEqual(b'\x40'*19, myRs.stream.read(19))
            self.assertRaises(TifMarker.ExceptionTifMarker, myTmr.read, myRs)
        
    def test_13(self):
        """TestTifMarker: Two Physical records with padding of 6 bytes succeeds when allowPrPadding=True."""
        myBytes = b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x1f\x00\x00\x00' \
            + b'\x40'*19 \
            + b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x34\x00\x00\x00' \
            + b'\x20'*9 \
            + b'\x01\x00\x00\x00' + b'\x1f\x00\x00\x00' + b'\x40\x00\x00\x00' \
            + b'\x01\x00\x00\x00' + b'\x34\x00\x00\x00' + b'\x4c\x00\x00\x00'
        myIo = io.BytesIO(myBytes)
        with RawStream.RawStream(myIo, mode='wb', fileId='MyFile') as myRs:
            myTmr = TifMarker.TifMarkerRead(myRs, allowPrPadding=True)
            self.assertTrue(myTmr.hasTif)
            self.assertFalse(myTmr.isReversed)
            self.assertEqual(myTmr.markers(), (0, 0, 0))
            # Now read
            myTmr.read(myRs)
            #print myTmr
            self.assertEqual(myTmr.markers(), (0, 0, 0x1F))
            # Simulate reading just 13 bytes of PR when 19 exist.
            self.assertEqual(b'\x40'*13, myRs.stream.read(13))
            myTmr.read(myRs)
            #print myTmr
            self.assertEqual(myTmr.markers(), (0, 0, 0x34))
            # Simulate reading just 3 bytes of PR when 9 exist.
            self.assertEqual(b'\x20'*3, myRs.stream.read(3))
            # EOF
            myTmr.read(myRs)
            self.assertEqual(myTmr.markers(), (1, 0x34, 0x4c))
            # Read after EOF
            try:
                myTmr.read(myRs)
                self.fail('TifMarker.ExceptionTifMarker not raised')
            except RawStream.ExceptionRawStream:
                pass
            self.assertTrue(myTmr.eof)
        
class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTifMarker))
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
