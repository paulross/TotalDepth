#!/usr/bin/env python
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 1999-2012 Paul Ross
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
"""Tests ...

Created on Oct 27, 2011

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

import sys
import logging
import time
import unittest
import io

from TotalDepth.util import FileBuffer

class TestFileBuffer(unittest.TestCase):

    def setUp(self):
        myF = io.BytesIO(b'0123456789')
        self._fileBuf = FileBuffer.FileBuffer(myF)

    def tearDown(self):
        pass

    def test_00(self):
        """TestFileBuffer.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestFileBuffer.test_01(): Tests position [0]."""
        self.assertEqual(ord('0'), self._fileBuf[0])

    def test_02(self):
        """TestFileBuffer.test_02(): Tests position [0]...[9]."""
        for i in range(10):
            self.assertEqual(i+ord('0'), self._fileBuf[i])

    def test_03(self):
        """TestFileBuffer.test_02(): Tests position [10] raises IndexError."""
        try:
            self._fileBuf[10]
            self.fail('IndexError not raised.')
        except IndexError:
            pass

    def test_10(self):
        """TestFileBuffer.test_10(): Tests tell() at start."""
        self.assertEqual(0, self._fileBuf.tell())

    def test_20(self):
        """TestFileBuffer.test_20(): Tests tell() and step() [0]...[9]."""
        for i in range(10):
            self.assertEqual(i, self._fileBuf.tell())
            s = self._fileBuf.step()
            self.assertEqual(bytes([i+ord('0'),]), s)

    def test_21(self):
        """TestFileBuffer.test_21(): Tests tell(), step() and index [0]...[9]."""
        for i in range(10):
            self.assertEqual(i, self._fileBuf.tell())
            for j in range(0, 10-i):
                self.assertEqual(i+j+ord('0'), self._fileBuf[j])
#            print('TRACE: buffer:', self._fileBuf._buf)
            s = self._fileBuf.step()
#            print('TRACE: s', s)
            self.assertEqual(bytes([i+ord('0'),]), s)

    def test_22(self):
        """TestFileBuffer.test_22(): Tests tell(), step() and correct EOF."""
        for i in range(10):
            self.assertEqual(i, self._fileBuf.tell())
            self._fileBuf.step()
        self.assertRaises(FileBuffer.ExceptionFileBufferEOF, self._fileBuf.step)
            
    def test_23(self):
        """TestFileBuffer.test_23(): Tests tell(), step(), IndexError on EOF and correct EOF."""
        for i in range(10):
            self.assertEqual(i, self._fileBuf.tell())
            self._fileBuf.step()
        try:
            self._fileBuf[0]
            self.fail('IndexError not raised.')
        except IndexError:
            pass
        self.assertRaises(FileBuffer.ExceptionFileBufferEOF, self._fileBuf.step)
            
    def test_30(self):
        """TestFileBuffer.test_30(): Tests slice [0:4]."""
        self.assertEqual(b'0123', self._fileBuf[0:4])

    def test_31(self):
        """TestFileBuffer.test_30(): Tests slice [:-1]."""
#        for i in range(4):
#            self._fileBuf.step()
        self._fileBuf[4]
#        print('TRACE: test_31(): buffer:', self._fileBuf._buf)
        self.assertEqual(b'0123', self._fileBuf[:-1])

    def test_32(self):
        """TestFileBuffer.test_32(): Tests slice [0:99]."""
        self.assertEqual(b'0123456789', self._fileBuf[0:99])

    def test_40(self):
        """TestFileBuffer.test_40(): Tests __getitem__ fails when index a string."""
        try:
            self._fileBuf['a']
            self.fail('TypeError not raised.')
        except TypeError:
            pass

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileBuffer))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Test ..."""
    print("""Test.py - A module that tests ...
Usage:
python Test....py [-lh --help]

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
    print(('Test....py script version "%s", dated %s' % (__version__, __date__)))
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
