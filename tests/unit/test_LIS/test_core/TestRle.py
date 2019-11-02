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

__author__  = 'Paul Ross'
__date__    = '6 Jan 2011'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'

#import pprint
import sys
import time
import logging

from TotalDepth.LIS.core import Rle

######################
# Section: Unit tests.
######################
import unittest


class TestRleType01(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestRleFunction: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestRleType01.test_00(): Basic test, single range."""
        myR = Rle.RLEType01(b'FEET')
        myInput = range(0, 3*8, 3)
        for v in myInput:
            myR.add(v, 1024, 4.2)
        self.assertEqual(len(myR), 1)
        self.assertEqual(myR.num_values(), len(myInput))
        #print([aV for aV in myR.values()])
        self.assertEqual(
            [aV for aV in myR.values()],
            [
                (0, 1024, 4.2),
                (3, 1024, 4.2),
                (6, 1024, 4.2),
                (9, 1024, 4.2),
                (12, 1024, 4.2),
                (15, 1024, 4.2),
                (18, 1024, 4.2),
                (21, 1024, 4.2)
            ]
        )
        for i, v in enumerate(myInput):
            self.assertEqual(myR.value(i)[0], v)
        # Check property access
        self.assertEqual(myR[0].datum, 0)
        self.assertEqual(myR[0].stride, 3)
        self.assertEqual(myR[0].repeat, 7)
        #print()
        #print('myR.rangeList()', myR.rangeList())
        #print('list of lists', [list(r) for r in myR.rangeList()])
        #print('First/last:', 'First', myR.first(), 'Last', myR.last())
        self.assertEqual(
            [
                [0, 3, 6, 9, 12, 15, 18, 21]
             ],
             [list(r) for r in myR.ranges()]
        )
        self.assertEqual(0, myR.first())
        self.assertEqual(21, myR.last())

    def test_00_00(self):
        """TestRleType01.test_00_00(): Basic test, single range with float() function."""
        myR = Rle.RLEType01(b'FEET', float)
        myInput = range(0, 3*8, 3)
        for v in myInput:
            myR.add(v, 1024, 4.2)
        self.assertEqual(len(myR), 1)
        self.assertEqual(myR.num_values(), len(myInput))
        #print([aV for aV in myR.values()])
        self.assertEqual(
            [aV for aV in myR.values()],
            [
                (0, 1024, 4.2),
                (3, 1024, 4.2),
                (6, 1024, 4.2),
                (9, 1024, 4.2),
                (12, 1024, 4.2),
                (15, 1024, 4.2),
                (18, 1024, 4.2),
                (21, 1024, 4.2)
            ]
        )
        for i, v in enumerate(myInput):
            self.assertEqual(myR.value(i)[0], v)
        # Check property access
        self.assertEqual(myR[0].datum, 0)
        self.assertEqual(myR[0].stride, 3)
        self.assertEqual(myR[0].repeat, 7)

    def test_01(self):
        """TestRleType01.test_01(): Basic test, single range, variable X axis value."""
        myR = Rle.RLEType01(b'FEET')
        myInput = range(0, 3*8, 3)
        for i, v in enumerate(myInput):
            myR.add(v, 1024, 4.2*i)
        self.assertEqual(len(myR), 1)
        self.assertEqual(myR.num_values(), len(myInput))
        #print([aV for aV in myR.values()])
        self.assertEqual(
            [aV for aV in myR.values()],
            [
                (0, 1024, 0.0),
                (3, 1024, 4.2),
                (6, 1024, 2*4.2),
                (9, 1024, 3*4.2),
                (12, 1024, 4*4.2),
                (15, 1024, 5*4.2),
                (18, 1024, 6*4.2),
                (21, 1024, 7*4.2)
            ]
        )
        for i, v in enumerate(myInput):
            self.assertEqual(myR.value(i)[0], v)
        # Check property access
        self.assertEqual(myR[0].datum, 0)
        self.assertEqual(myR[0].stride, 3)
        self.assertEqual(myR[0].repeat, 7)

    def test_02(self):
        """TestRleType01.test_02(): Basic test, variable frame size, variable X axis value."""
        myR = Rle.RLEType01(b'FEET')
        myInput = range(0, 3*8, 3)
        for i, v in enumerate(myInput):
            #print('test_01()', v)
            if i % 4 == 0:
                myR.add(v, 1024, 4.2*i)
            else:
                myR.add(v, 512, 4.2*i)
        self.assertEqual(len(myR), 4)
        #print()
        #print([aV for aV in myR.values()])
        self.assertEqual(myR.num_values(), len(myInput))
        self.assertEqual(
            [aV for aV in myR.values()],
            [
                (0, 1024, 0.0),
                (3, 512, 4.2),
                (6, 512, 2*4.2),
                (9, 512, 3*4.2),
                (12, 1024, 4*4.2),
                (15, 512, 5*4.2),
                (18, 512, 6*4.2),
                (21, 512, 29.400000000000006)
            ]            
        )
        for i, v in enumerate(myInput):
            self.assertEqual(myR.value(i)[0], v)
        # Check property access
        print(str(myR))
        self.assertEqual(myR[0].datum, 0)
        self.assertEqual(myR[0].stride, 0)
        self.assertEqual(myR[0].repeat, 0)
        # self.assertEqual(myR[1].datum, 3)
        # self.assertEqual(myR[1].stride, 3)
        # self.assertEqual(myR[1].repeat, 2)
        # self.assertEqual(myR[2].datum, 12)
        # self.assertEqual(myR[2].stride, None)
        # self.assertEqual(myR[2].repeat, 0)
        # self.assertEqual(myR[3].datum, 15)
        # self.assertEqual(myR[3].stride, 3)
        # self.assertEqual(myR[3].repeat, 2)

    def test_03(self):
        """TestRleType01.test_02(): Basic test, variable frame size, variable X axis value. totalFrames()."""
        myR = Rle.RLEType01(b'FEET')
        myInput = range(0, 3*8, 3)
        totalF = 0
        for i, v in enumerate(myInput):
            #print('test_01()', v)
            if i % 4 == 0:
                myR.add(v, 1024, 4.2*i)
                totalF += 1024
            else:
                myR.add(v, 512, 4.2*i)
                totalF += 512
        self.assertEqual(len(myR), 4)
        self.assertEqual(myR.totalFrames(), totalF)
        self.assertEqual(myR[0].totalFrames(), 1024)
        self.assertEqual(myR[1].totalFrames(), 3*512)
        self.assertEqual(myR[2].totalFrames(), 1024)
        self.assertEqual(myR[3].totalFrames(), 3*512)

    def test_04(self):
        """TestRleType01.test_04(): Basic test, 128 byte LR, 4 frames each. tellLrForFrame()."""
        myR = Rle.RLEType01(b'FEET')
        myInput = range(0, 512, 128)
        fTotal = 0
        for i, v in enumerate(myInput):
            myR.add(v, 4, 4*0.5*i)
            fTotal += 4
        #print()
        #print(myR)
        self.assertEqual(len(myR), 1)
        # 4 * 512 // 128 = 16
        self.assertEqual(fTotal, 16)
        self.assertEqual(myR.totalFrames(), fTotal)
        str(myR)
#        self.assertEqual(str(myR), """RLEType01: func=None
#  RLEItemType01: datum=0 stride=128 repeat=3 frames=4""")
        #for f in range(totalF):
        #    print(f, myR.tellLrForFrame(f))
        # RLEItem[0]
        self.assertEqual(myR.tellLrForFrame(0),     (0,     0))
        self.assertEqual(myR.tellLrForFrame(1),     (0,     1))
        self.assertEqual(myR.tellLrForFrame(2),     (0,     2))
        self.assertEqual(myR.tellLrForFrame(3),     (0,     3))
        self.assertEqual(myR.tellLrForFrame(4),     (128,   0))
        self.assertEqual(myR.tellLrForFrame(5),     (128,   1))
        self.assertEqual(myR.tellLrForFrame(6),     (128,   2))
        self.assertEqual(myR.tellLrForFrame(7),     (128,   3))
        self.assertEqual(myR.tellLrForFrame(8),     (2*128, 0))
        self.assertEqual(myR.tellLrForFrame(9),     (2*128, 1))
        self.assertEqual(myR.tellLrForFrame(10),    (2*128, 2))
        self.assertEqual(myR.tellLrForFrame(11),    (2*128, 3))
        self.assertEqual(myR.tellLrForFrame(12),    (3*128, 0))
        self.assertEqual(myR.tellLrForFrame(13),    (3*128, 1))
        self.assertEqual(myR.tellLrForFrame(14),    (3*128, 2))
        self.assertEqual(myR.tellLrForFrame(15),    (3*128, 3))
        # Failures
        self.assertRaises(IndexError, myR.tellLrForFrame, -1)
        self.assertRaises(IndexError, myR.tellLrForFrame, 16)

    def test_05(self):
        """TestRleType01.test_05(): Basic test, variable frame size, variable X axis value. tellLrForFrame()."""
        myR = Rle.RLEType01(b'FEET')
        myInput = range(0, 2048, 128)
        totalF = 0
        for i, v in enumerate(myInput):
            #print('test_01()', v)
            if i % 6*128 == 0:
                myR.add(v, 2, 4.2*i)
                totalF += 2
            else:
                myR.add(v, 1, 4.2*i)
                totalF += 1
        #print()
        #print(myR)
        self.assertEqual(len(myR), 6)
        self.assertEqual(myR.totalFrames(), totalF)
        str(myR)
#        self.assertEqual(str(myR), """RLEType01: func=None
#  RLEItemType01: datum=0 stride=None repeat=0 frames=2
#  RLEItemType01: datum=128 stride=128 repeat=4 frames=1
#  RLEItemType01: datum=768 stride=None repeat=0 frames=2
#  RLEItemType01: datum=896 stride=128 repeat=4 frames=1
#  RLEItemType01: datum=1536 stride=None repeat=0 frames=2
#  RLEItemType01: datum=1664 stride=128 repeat=2 frames=1""")
        #for f in range(totalF):
        #    print(f, myR.tellLrForFrame(f))
        # RLEItem[0]
        self.assertEqual(myR.tellLrForFrame(0),     (0,         0))
        self.assertEqual(myR.tellLrForFrame(1),     (0,         1))
        # RLEItem[1]
        self.assertEqual(myR.tellLrForFrame(2),     (128,       0))
        self.assertEqual(myR.tellLrForFrame(3),     (2*128,     0))
        self.assertEqual(myR.tellLrForFrame(4),     (3*128,     0))
        self.assertEqual(myR.tellLrForFrame(5),     (4*128,     0))
        self.assertEqual(myR.tellLrForFrame(6),     (5*128,     0))
        # RLEItem[2]
        self.assertEqual(myR.tellLrForFrame(7),     (6*128,     0))
        self.assertEqual(myR.tellLrForFrame(8),     (6*128,     1))
        # RLEItem[3]
        self.assertEqual(myR.tellLrForFrame(9),     (7*128,     0))
        self.assertEqual(myR.tellLrForFrame(10),    (8*128,     0))
        self.assertEqual(myR.tellLrForFrame(11),    (9*128,     0))
        self.assertEqual(myR.tellLrForFrame(12),    (10*128,    0))
        self.assertEqual(myR.tellLrForFrame(13),    (11*128,    0))
        # RLEItem[4]
        self.assertEqual(myR.tellLrForFrame(14),    (12*128,    0))
        self.assertEqual(myR.tellLrForFrame(15),    (12*128,    1))
        # RLEItem[3]
        self.assertEqual(myR.tellLrForFrame(16),    (13*128,    0))
        self.assertEqual(myR.tellLrForFrame(17),    (14*128,    0))
        self.assertEqual(myR.tellLrForFrame(18),    (15*128,    0))
        # Failures
        self.assertRaises(IndexError, myR.tellLrForFrame, -1)
        self.assertRaises(IndexError, myR.tellLrForFrame, 19)
        #print()
        #print(myR.rangeList())
        #print([list(r) for r in myR.rangeList()])
        #print('First/last:', 'First', myR.first(), 'Last', myR.last())
        self.assertEqual(
            [
                [0],
                [128, 256, 384, 512, 640],
                [768],
                [896, 1024, 1152, 1280, 1408],
                [1536],
                [1664, 1792, 1920]
             ],
             [list(r) for r in myR.ranges()]
        )
        self.assertEqual(0, myR.first())
        self.assertEqual(1920, myR.last())

class TestRleType01XAxis(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestRleFunction: Tests setUp() and tearDown()."""
        pass
    
    def test_00(self):
        """TestRleType01XAxis.test_00(): Basic test, single range, down log."""
        myR = Rle.RLEType01(b'FEET')
        myInput = range(0, 2048, 128)
        totalF = 0
        for i, v in enumerate(myInput):
            myR.add(v, 8, 8*0.5*i)
            totalF += 8
        self.assertEqual(len(myR), 1)
        self.assertEqual(myR.totalFrames(), totalF)
#        print()
#        #print(myR)
#        print('X first', myR.xAxisFirst())
#        print('X last', myR.xAxisLast())
#        print('X units', myR.xAxisUnits)
#        print('Frame spacing', myR.frameSpacing())
#        print('Total Frames', myR.totalFrames())
#        print('4.2*i', 4.2*i)
        str(myR)
        self.assertEqual(b'FEET', myR.xAxisUnits)
        self.assertTrue(myR.hasXaxisData)
        self.assertEqual(0.0, myR.xAxisFirst())
        self.assertEqual(60.0, myR.xAxisLast())
        self.assertEqual(63.5, myR.xAxisLastFrame())
        self.assertEqual(0.5, myR.frameSpacing())
        self.assertEqual(128, myR.totalFrames())

    def test_01(self):
        """TestRleType01XAxis.test_01(): Basic test, single range, up log."""
        myR = Rle.RLEType01(b'FEET')
        myInput = range(0, 2048, 128)
        totalF = 0
        for i, v in enumerate(myInput):
            myR.add(v, 8, 8*-0.5*i)
            totalF += 8
        self.assertEqual(len(myR), 1)
        self.assertEqual(myR.totalFrames(), totalF)
#        print()
#        #print(myR)
#        print('X first', myR.xAxisFirst())
#        print('X last', myR.xAxisLast())
#        print('X units', myR.xAxisUnits)
#        print('Frame spacing', myR.frameSpacing())
#        print('Total Frames', myR.totalFrames())
#        print('4.2*i', 4.2*i)
        str(myR)
        self.assertEqual(b'FEET', myR.xAxisUnits)
        self.assertEqual(0.0, myR.xAxisFirst())
        self.assertEqual(-60.0, myR.xAxisLast())
        self.assertEqual(-0.5, myR.frameSpacing())
        self.assertEqual(128, myR.totalFrames())



class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRleType01))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRleType01XAxis))
    # TODO: Performance test - time and space
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestRle.py - Tests the TotalDepth.LIS.core Rle module.
Usage:
python TestRle.py [-lh --help]

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
