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
"""Unit tests for ...

Created on May 26, 2011

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = 'May 26, 2011'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

#import pprint
import sys
import time
import logging
#import io

from TotalDepth.LIS.core import Mnem

######################
# Section: Unit tests.
######################
import unittest

class TestMnem(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestMnem.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestMnem.test_01(): Basic constructor."""
        myM = Mnem.Mnem(b'ABCD')
        self.assertEqual(b'ABCD', myM.m)

    def test_02(self):
        """TestMnem.test_02(): Truncation of >4 chars."""
        myM = Mnem.Mnem(b'ABCDDEF')
        self.assertEqual(b'ABCD', myM.m)

    def test_03(self):
        """TestMnem.test_03(): Padding of <4 chars."""
        myM = Mnem.Mnem(b'AB')
        self.assertEqual(b'AB\x00\x00', myM.m)
        myM = Mnem.Mnem(b'AB\x00')
        self.assertEqual(b'AB\x00\x00', myM.m)
        myM = Mnem.Mnem(b'AB\x00\x00')
        self.assertEqual(b'AB\x00\x00', myM.m)
        myM = Mnem.Mnem(b'AB ')
        self.assertEqual(b'AB\x00\x00', myM.m)
        myM = Mnem.Mnem(b'AB  ')
        self.assertEqual(b'AB\x00\x00', myM.m)
#        print(str(myM))
        self.assertEqual('AB\x00\x00', str(myM))

    def test_04(self):
        """TestMnem.test_04(): Padding of zero chars."""
        myM = Mnem.Mnem(b'')
        self.assertEqual(b'\x00\x00\x00\x00', myM.m)

    def test_10(self):
        """TestMnem.test_10(): Equality tests."""
        self.assertEqual(Mnem.Mnem(b'\x00\x00\x00\x00'), Mnem.Mnem(b''))
        self.assertTrue(Mnem.Mnem(b'') == b'\x00\x00\x00\x00')
        self.assertEqual(Mnem.Mnem(b'AB'), Mnem.Mnem(b'AB\x00'))
        self.assertEqual(Mnem.Mnem(b'AB'), Mnem.Mnem(b'AB  '))
        self.assertEqual(Mnem.Mnem(b'AB '), Mnem.Mnem(b'AB  '))

    def test_11(self):
        """TestMnem.test_11(): Inequality tests."""
        self.assertTrue(Mnem.Mnem(b'') != b'A\x00\x00\x00')
        self.assertTrue(Mnem.Mnem(b'') != Mnem.Mnem(b'A\x00\x00\x00'))

    def test_20(self):
        """TestMnem.test_20(): Sorting tests."""
        myL = [
            Mnem.Mnem(b'B   '),
            Mnem.Mnem(b'AB'),
        ]
#        print([M.m for M in sorted(myL)])
        self.assertEqual(
            [
                'AB\x00\x00',
                'B\x00\x00\x00',
            ],
            [str(M) for M in sorted(myL)]
        )

    def test_21(self):
        """TestMnem.test_21(): Sorting tests, mixed bytes and Mnem objects."""
        myL = [
            b'B   ',
            Mnem.Mnem(b'AB'),
        ]
#        print(sorted(myL))
#        print([M.m for M in sorted(myL)])
        self.assertEqual(
            [
                Mnem.Mnem(b'AB\x00\x00'),
                Mnem.Mnem(b'B   '),
            ],
            sorted(myL)
        )
        self.assertEqual(
            [
                'AB\x00\x00',
                "b'B   '",
            ],
            [str(M) for M in sorted(myL)]
        )

    def test_30(self):
        """TestMnem.test_30(): Hash tests."""
        myM = Mnem.Mnem(b'AB  ')
        self.assertEqual(hash(myM.m), hash(myM))
        self.assertEqual(hash(Mnem.Mnem(b'AB')), hash(myM))
        myM = Mnem.Mnem(b'AB\x00\x00')
        self.assertEqual(hash(myM.m), hash(myM))
        self.assertEqual(hash(Mnem.Mnem(b'AB')), hash(myM))
        
    def test_31(self):
        """TestMnem.test_31(): Hash map tests."""
        myMap = {
            Mnem.Mnem(b'AB')        : b'AB',
            Mnem.Mnem(b'ABCDEF')    : b'ABCDEF',
        }
#        print(myMap)
        self.assertTrue(Mnem.Mnem(b'AB') in myMap)
        self.assertTrue(Mnem.Mnem(b'AB  ') in myMap)
        self.assertTrue(Mnem.Mnem(b'ABCD') in myMap)
        
    def test_32(self):
        """TestMnem.test_32(): Hash map tests interchanging bytes and Mnem objects."""
        myMap = {
            Mnem.Mnem(b'AB')        : b'AB',
            Mnem.Mnem(b'ABCDEF')    : b'ABCDEF',
        }
#        print(myMap)
        self.assertEqual(hash(b'AB\x00\x00'), hash(Mnem.Mnem(b'AB')))
        self.assertTrue(b'AB\x00\x00' in myMap)
        self.assertTrue(b'AB\x00\x00' in myMap)
        self.assertTrue(b'ABCD' in myMap)
        
    def test_40(self):
        """TestMnem.test_40(): Iteration tests."""
        myM = Mnem.Mnem(b'ABCDEF')
#        print([v for v in myM])
#        for aVal in myM:
#            print(aVal)
        self.assertEqual([65, 66, 67, 68], [v for v in myM])
        
    def test_50(self):
        """TestMnem.test_50(): pStr()."""
        myM = Mnem.Mnem(b'ABCDEF')
        self.assertEqual('ABCD', myM.pStr())
        
    def test_51(self):
        """TestMnem.test_51(): pStr() with strip."""
        myM = Mnem.Mnem(b'AB  ')
        self.assertEqual('AB', myM.pStr(strip=True))
        
    def test_55(self):
        """TestMnem.test_55(): repr() with strip."""
        myM = Mnem.Mnem(b'AB  ')
        self.assertEqual("Mnem(b'AB\\x00\\x00')", repr(myM))

    def test_60(self):
        """TestMnem.test_60(): No truncation of chars when len_mnem is zero."""
        myM = Mnem.Mnem(b'ABCDDEF', len_mnem=0)
        self.assertEqual(b'ABCDDEF', myM.m)
        myM = Mnem.Mnem(b'AB', len_mnem=0)
        self.assertEqual(b'AB', myM.m)

    def test_61(self):
        """TestMnem.test_61(): No padding of <4 chars when len_mnem is zero."""
        myM = Mnem.Mnem(b'AB', len_mnem=0)
        self.assertEqual(b'AB', myM.m)
        myM = Mnem.Mnem(b'AB\x00', len_mnem=0)
        self.assertEqual(b'AB\x00', myM.m)
        myM = Mnem.Mnem(b'AB\x00\x00', len_mnem=0)
        self.assertEqual(b'AB\x00\x00', myM.m)
        myM = Mnem.Mnem(b'AB ', len_mnem=0)
        self.assertEqual(b'AB\x00', myM.m)
        myM = Mnem.Mnem(b'AB  ', len_mnem=0)
        self.assertEqual(b'AB\x00\x00', myM.m)
#        print(str(myM))
        self.assertEqual('AB\x00\x00', str(myM))
        
    def test_63(self):
        """TestMnem.test_63(): No truncation of chars when len_mnem is negative but pad if smaller."""
        myM = Mnem.Mnem(b'ABCDDEF', len_mnem=-4)
        self.assertEqual(b'ABCDDEF', myM.m)
        myM = Mnem.Mnem(b'AB', len_mnem=-4)
        self.assertEqual(b'AB\x00\x00', myM.m)

    def test_64(self):
        """TestMnem.test_64(): Padding of <4 chars when len_mnem is negative."""
        myM = Mnem.Mnem(b'AB', len_mnem=-4)
        self.assertEqual(b'AB\x00\x00', myM.m)
        myM = Mnem.Mnem(b'AB\x00', len_mnem=-4)
        self.assertEqual(b'AB\x00\x00', myM.m)
        myM = Mnem.Mnem(b'AB\x00\x00', len_mnem=-4)
        self.assertEqual(b'AB\x00\x00', myM.m)
        myM = Mnem.Mnem(b'AB ', len_mnem=-4)
        self.assertEqual(b'AB\x00\x00', myM.m)
        myM = Mnem.Mnem(b'AB  ', len_mnem=-4)
        self.assertEqual(b'AB\x00\x00', myM.m)
#        print(str(myM))
        self.assertEqual('AB\x00\x00', str(myM))
        
    def test_70(self):
        """TestMnem.test_70(): Construction with a string."""
        myM = Mnem.Mnem('ABCD')
        self.assertEqual(b'ABCD', myM.m)

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMnem))
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
