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

Created on Nov 29, 2011

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

from TotalDepth.util import Histogram

class TestHistogram(unittest.TestCase):

    def setUp(self):
        self._hist = Histogram.Histogram()

    def tearDown(self):
        pass

    def test_00(self):
        """TestHistogram.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestHistogram.test_01(): Tests add() and __getitem__()."""
        self._hist.add(10)
        self.assertEqual(1, self._hist[10])

    def test_02(self):
        """TestHistogram.test_02(): Tests __getitem__() where non-existent."""
        self.assertEqual(0, self._hist[10])

    def test_03(self):
        """TestHistogram.test_03(): Tests strRep() with single entry."""
        for x in range(1, 3):
            self._hist.add(x, x)
#        print('')
#        print(self._hist.strRep())
        result = """1 | ++++++++++++++++++++++++++++++++++++
2 | +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"""
        self.assertEqual(result, self._hist.strRep())

    def test_04(self):
        """TestHistogram.test_04(): Tests strRep() with two entries and title."""
        for x in range(1, 3):
            self._hist.add(x, x)
#        print('')
#        print(self._hist.strRep(valTitle='Integers:'))
        result = """Integers:
        1 | ++++++++++++++++++++++++++++++++
        2 | +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"""
        self.assertEqual(result, self._hist.strRep(valTitle='Integers:'))

    def test_05(self):
        """TestHistogram.test_05(): Tests strRep() with two entries, title and counts."""
        for x in range(1, 3):
            self._hist.add(x, x*10)
#        print('')
#        print(self._hist.strRep(valTitle='Integers:', inclCount=True))
        result = """Integers:
        1 [10] | +++++++++++++++++++++++++++++
        2 [20] | ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"""
        self.assertEqual(result, self._hist.strRep(valTitle='Integers:', inclCount=True))

    def test_10(self):
        """TestHistogram.test_10(): Tests strRep()."""
        for x in range(1, 12):
            self._hist.add(x, x)
#        print('')
#        print(self._hist.strRep())
        result = """ 1 | ++++++
 2 | +++++++++++++
 3 | +++++++++++++++++++
 4 | +++++++++++++++++++++++++
 5 | ++++++++++++++++++++++++++++++++
 6 | ++++++++++++++++++++++++++++++++++++++
 7 | +++++++++++++++++++++++++++++++++++++++++++++
 8 | +++++++++++++++++++++++++++++++++++++++++++++++++++
 9 | +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
10 | ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
11 | ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"""
        self.assertEqual(result, self._hist.strRep())

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestHistogram))
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
    print('')
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
