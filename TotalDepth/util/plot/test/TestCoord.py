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
# Paul Ross: cpipdev@googlemail.com

__author__  = 'Paul Ross'
__date__    = '2009-09-25'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'

"""
paulross@L071183 /cygdrive/d/wip/small_projects/PlotTree/src/python
$ python c:/Python26/Lib/site-packages/coverage.py -x test/TestCoord.py
"""

#import os
import sys
import logging
#import StringIO

#sys.path.append(os.path.join(os.pardir + os.sep))
from TotalDepth.util.plot import Coord

######################
# Section: Unit tests.
######################
import unittest

# Define unit test classes
class TestCoordDim(unittest.TestCase):
    """the Coord.Dim class."""

    def testUnitRange(self):
        """Tests the units are in range."""
        self.assertEqual(
            set(Coord.units()),
            set([None, 'cm', 'in', 'mm', 'pc', 'pt', 'px']),
            )

    def testConstructor(self):
        """Dim() constructor."""
        myObj = Coord.Dim(12, 'px')
        #print myObj
        self.assertEqual(myObj.value, 12)
        self.assertEqual(myObj.units, 'px')

    def testStr(self):
        """Dim() __str__()."""
        myObj = Coord.Dim(12, 'px')
        self.assertEqual(str(myObj), 'Dim(12px)')

    def testAdd(self):
        """Dim() addition."""
        myObj_0 = Coord.Dim(1, 'in')
        myObj_1 = Coord.Dim(18, 'px')
        myResult =  myObj_0 + myObj_1
        #print myResult
        self.assertEqual(myResult.value, 1.25)
        self.assertEqual(myResult.units, 'in')

    def testSub(self):
        """Dim() subtraction."""
        myObj_0 = Coord.Dim(1, 'in')
        myObj_1 = Coord.Dim(18, 'px')
        myResult =  myObj_0 - myObj_1
        #print myResult
        self.assertEqual(myResult.value, 0.75)
        self.assertEqual(myResult.units, 'in')

    def testIadd_00(self):
        """Dim() +=."""
        myObj_0 = Coord.Dim(1, 'in')
        myObj_1 = Coord.Dim(18, 'px')
        myObj_0 += myObj_1
        #print myObj
        self.assertEqual(myObj_0.value, 1.25)
        self.assertEqual(myObj_0.units, 'in')

    def testIadd_01(self):
        """Dim() += when initial units are None."""
        myObj_0 = Coord.Dim(12, None)
        myObj_0 += Coord.Dim(18, 'px')
        self.assertEqual(myObj_0.value, 30)
        self.assertEqual(myObj_0.units, 'px')

    def testIsub_00(self):
        """Dim() -=."""
        myObj_0 = Coord.Dim(1, 'in')
        myObj_0 -= Coord.Dim(18, 'px')
        self.assertEqual(myObj_0.value, 0.75)
        self.assertEqual(myObj_0.units, 'in')

    def testIsub_01(self):
        """Dim() -= when initial units are None."""
        myObj_0 = Coord.Dim(36, None)
        myObj_0 -= Coord.Dim(12, 'px')
        self.assertEqual(myObj_0.value, 24)
        self.assertEqual(myObj_0.units, 'px')

    def testScale(self):
        """Dim() scale()."""
        myObj = Coord.Dim(12, 'px')
        myObj = myObj.scale(2.0)
        self.assertEqual(myObj.value, 24)
        self.assertEqual(myObj.units, 'px')

    def testConvert(self):
        """Dim() convert()."""
        myObj = Coord.Dim(72, 'px')
        myObj = myObj.convert('px')
        self.assertEqual(myObj.value, 72)
        self.assertEqual(myObj.units, 'px')
        myObj = myObj.convert('in')
        self.assertEqual(myObj.value, 1.0)
        self.assertEqual(myObj.units, 'in')

    def testConvertFails(self):
        """Dim() convert() fails."""
        myObj = Coord.Dim(72, 'WTF')
        self.assertRaises(
            Coord.ExceptionCoordUnitConvert,
            myObj.convert,
            'in'
            )
        myObj = Coord.Dim(72, 'px')
        self.assertRaises(
            Coord.ExceptionCoordUnitConvert,
            myObj.convert,
            'WTF'
            )

    def testCmp_00(self):
        """Dim() cmp() [00]."""
        myObj_0 = Coord.Dim(1, 'in')
        myObj_1 = Coord.Dim(72, 'px')
        #print myObj_0 == myObj_1
        self.assertEqual(myObj_0, myObj_1)
        self.assertEqual(myObj_0, myObj_1)
        self.assertTrue(myObj_0 == myObj_1)

    def testCmp_01(self):
        """Dim() cmp() [01]."""
        myObj_0 = Coord.Dim(1, 'in')
        myObj_1 = Coord.Dim(1, 'in')
        self.assertEqual(myObj_0, myObj_1)
        self.assertEqual(myObj_0, myObj_1)
        self.assertTrue(myObj_0 == myObj_1)

    def testCmp_02(self):
        """Dim() cmp() [02]."""
        myObj_0 = Coord.Dim(1, 'in')
        myObj_1 = Coord.Dim(72, 'px')
        self.assertTrue(myObj_0 == myObj_1)
        self.assertTrue(myObj_0 <= myObj_1)
        self.assertTrue(myObj_0 >= myObj_1)
        self.assertFalse(myObj_0 != myObj_1)
        self.assertFalse(myObj_0 < myObj_1)
        self.assertFalse(myObj_0 > myObj_1)

    def testCmp_03(self):
        """Dim() cmp() [03]."""
        myObj_0 = Coord.Dim(1, 'in')
        myObj_1 = Coord.Dim(73, 'px')
        self.assertFalse(myObj_0 == myObj_1)
        self.assertTrue(myObj_0 <= myObj_1)
        self.assertFalse(myObj_0 >= myObj_1)
        self.assertTrue(myObj_0 != myObj_1)
        self.assertTrue(myObj_0 < myObj_1)
        self.assertFalse(myObj_0 > myObj_1)

    def testMax_00(self):
        """Dim() max(...) [00]."""
        myObj_0 = Coord.Dim(71, 'px')
        myObj_1 = Coord.Dim(72, 'px')
        self.assertEqual(myObj_1, max(myObj_0, myObj_1))
        self.assertNotEqual(myObj_0, max(myObj_0, myObj_1))

    def testMin_00(self):
        """Dim() min(...) [00]."""
        myObj_0 = Coord.Dim(71, 'px')
        myObj_1 = Coord.Dim(72, 'px')
        self.assertEqual(myObj_0, min(myObj_0, myObj_1))
        self.assertNotEqual(myObj_1, min(myObj_0, myObj_1))

    def testSum_00(self):
        """Dim() sum(...) raises type error [00]."""
        myObj_0 = Coord.Dim(71, 'px')
        myObj_1 = Coord.Dim(72, 'px')
        try:
            sum([myObj_0, myObj_1])
            self.fail('TypeError not raised')
        except TypeError:
            pass

class TestCoordPoint(unittest.TestCase):
    """Tests the Coord.Pt class."""

    def testConstructor(self):
        """Pt() constructor."""
        myPt = Coord.Pt(
            Coord.Dim(12, 'px'),
            Coord.Dim(24, 'px'),
            )
        #print myPt
        self.assertEqual(myPt.x, Coord.Dim(12, 'px'))
        self.assertEqual(myPt.y, Coord.Dim(24, 'px'))

    def testStr(self):
        """Pt() __str__()."""
        myPt = Coord.Pt(
            Coord.Dim(12, 'px'),
            Coord.Dim(24, 'px'),
            )
        #print myPt
        self.assertEqual(str(myPt), 'Pt(x=Dim(12px), y=Dim(24px))')
        #self.assertEqual(('%s' % myPt), 'Pt(x=Dim(12px), y=Dim(24px))')

    def testCmp_00(self):
        """Pt() cmp() is 0."""
        myPt_0 = Coord.Pt(
            Coord.Dim(1, 'in'),
            Coord.Dim(2, 'in'),
            )
        myPt_1 = Coord.Pt(
            Coord.Dim(72, 'px'),
            Coord.Dim(12, 'pc'),
            )
        self.assertEqual(myPt_0, myPt_1)
        self.assertTrue(myPt_0 == myPt_1)

    def testCmp_01(self):
        """Pt() cmp() is -1 for x."""
        myPt_0 = Coord.Pt(
            Coord.Dim(1, 'in'),
            Coord.Dim(2, 'in'),
            )
        myPt_1 = Coord.Pt(
            Coord.Dim(73, 'px'),
            Coord.Dim(12, 'pc'),
            )
        self.assertTrue(myPt_0 < myPt_1)

    def testCmp_02(self):
        """Pt() cmp() is +1 for x."""
        myPt_0 = Coord.Pt(
            Coord.Dim(1, 'in'),
            Coord.Dim(2, 'in'),
            )
        myPt_1 = Coord.Pt(
            Coord.Dim(71, 'px'),
            Coord.Dim(12, 'pc'),
            )
        self.assertTrue(myPt_0 > myPt_1)

    def testCmp_03(self):
        """Pt() cmp() is -1 for y."""
        myPt_0 = Coord.Pt(
            Coord.Dim(1, 'in'),
            Coord.Dim(2, 'in'),
            )
        myPt_1 = Coord.Pt(
            Coord.Dim(72, 'px'),
            Coord.Dim(13, 'pc'),
            )
        self.assertTrue(myPt_0 < myPt_1)

    def testCmp_04(self):
        """Pt() cmp() is +1 for y."""
        myPt_0 = Coord.Pt(
            Coord.Dim(1, 'in'),
            Coord.Dim(2, 'in'),
            )
        myPt_1 = Coord.Pt(
            Coord.Dim(72, 'px'),
            Coord.Dim(11, 'pc'),
            )
        self.assertTrue(myPt_0 > myPt_1)

    def testConvert_00(self):
        """Pt() convert() [00]."""
        myPt_0 = Coord.Pt(
            Coord.Dim(1, 'in'),
            Coord.Dim(2, 'in'),
            )
        myPt_1 = Coord.Pt(
            Coord.Dim(72, 'px'),
            Coord.Dim(12, 'pc'),
            )
        myPt_1 = myPt_1.convert('in')
        #print myPt_1
        self.assertTrue(myPt_0 == myPt_1)
        
    def testConvert_01(self):
        """Pt() convert() [01]."""
        myPt_0 = Coord.Pt(
            Coord.Dim(20, 'mm'),
            Coord.Dim(10, 'mm'),
            )
        myPt_1 = Coord.Pt(
            Coord.Dim(20*72/25.4, 'px'),
            Coord.Dim(10*72/25.4, 'px'),
            )
        myPt_0 = myPt_0.convert('px')
        #print myPt_1
        self.assertEqual(myPt_0, myPt_1)
        self.assertTrue(myPt_0 == myPt_1)

    def testScale(self):
        """Pt() scale()."""
        myPt_0 = Coord.Pt(
            Coord.Dim(20, 'mm'),
            Coord.Dim(7, 'px'),
            )
        myPt_1 = myPt_0.scale(2.0)
        self.assertEqual(myPt_1.x, Coord.Dim(40, 'mm'))
        self.assertEqual(myPt_1.y, Coord.Dim(14, 'px'))
        self.assertEqual(myPt_1.x.units, 'mm')
        self.assertEqual(myPt_1.y.units, 'px')
        
#===============================================================================
#        myObj = Coord.Dim(72, 'px')
#        myObj = myObj.convert('px')
#        self.assertEqual(myObj.value, 72)
#        self.assertEqual(myObj.units, 'px')
#        myObj = myObj.convert('in')
#        self.assertEqual(myObj.value, 1.0)
#        self.assertEqual(myObj.units, 'in')
#===============================================================================

class TestCoordHelperFunctions(unittest.TestCase):
    """Tests the helper functions in the Coord module."""

    def test_baseUnitsDim(self):
        """baseUnitsDim()."""
        myDim = Coord.baseUnitsDim(147)
        self.assertEqual(147, myDim.value)
        self.assertEqual(Coord.BASE_UNITS, myDim.units)

    def test_zeroBaseUnitsDim(self):
        """zeroBaseUnitsDim()."""
        myDim = Coord.zeroBaseUnitsDim()
        self.assertEqual(0, myDim.value)
        self.assertEqual(Coord.BASE_UNITS, myDim.units)

    def test_zeroBaseUnitsBox(self):
        """zeroBaseUnitsBox()."""
        myBox = Coord.zeroBaseUnitsBox()
        #print()
        #print(myBox)
        self.assertEqual(Coord.Dim(0, Coord.BASE_UNITS), myBox.width)
        self.assertEqual(Coord.Dim(0, Coord.BASE_UNITS), myBox.depth)
        self.assertEqual('Box(width=Dim(0.0px), depth=Dim(0.0px))', str(myBox))

    def test_zeroBaseUnitsPad(self):
        """zeroBaseUnitsPad()."""
        myPad = Coord.zeroBaseUnitsPad()
        #print()
        #print(myPad)
        self.assertEqual(Coord.Dim(0, Coord.BASE_UNITS), myPad.prev)
        self.assertEqual(Coord.Dim(0, Coord.BASE_UNITS), myPad.next)
        self.assertEqual(Coord.Dim(0, Coord.BASE_UNITS), myPad.parent)
        self.assertEqual(Coord.Dim(0, Coord.BASE_UNITS), myPad.child)
        self.assertEqual(
            'Pad(prev=Dim(0.0px), next=Dim(0.0px), parent=Dim(0.0px), child=Dim(0.0px))',
            str(myPad),
        )
        
    def test_zeroBaseUnitsPt(self):
        """zeroBaseUnitsPt()."""
        myPt = Coord.zeroBaseUnitsPt()
        #print()
        #print(myPt)
        self.assertEqual(Coord.Dim(0, Coord.BASE_UNITS), myPt.x)
        self.assertEqual(Coord.Dim(0, Coord.BASE_UNITS), myPt.y)

    def test_newPt(self):
        """newPt()."""
        myPt = Coord.newPt(Coord.zeroBaseUnitsPt())
        self.assertEqual(Coord.Dim(0, Coord.BASE_UNITS), myPt.x)
        self.assertEqual(Coord.Dim(0, Coord.BASE_UNITS), myPt.y)
        myPt = Coord.newPt(Coord.zeroBaseUnitsPt(), incX=Coord.Dim(14, Coord.BASE_UNITS))
        self.assertEqual(Coord.Dim(14, Coord.BASE_UNITS), myPt.x)
        self.assertEqual(Coord.Dim(0, Coord.BASE_UNITS), myPt.y)
        myPt = Coord.newPt(Coord.zeroBaseUnitsPt(), incY=Coord.Dim(14, Coord.BASE_UNITS))
        self.assertEqual(Coord.Dim(0, Coord.BASE_UNITS), myPt.x)
        self.assertEqual(Coord.Dim(14, Coord.BASE_UNITS), myPt.y)
        myPt = Coord.newPt(
            Coord.zeroBaseUnitsPt(),
            incX=Coord.Dim(14, Coord.BASE_UNITS),
            incY=Coord.Dim(14, Coord.BASE_UNITS)
        )
        self.assertEqual(Coord.Dim(14, Coord.BASE_UNITS), myPt.x)
        self.assertEqual(Coord.Dim(14, Coord.BASE_UNITS), myPt.y)

    def test_convertPt(self):
        """convertPt()."""
        myPt = Coord.newPt(
            Coord.zeroBaseUnitsPt(),
            incX=Coord.Dim(72, 'px'),
            incY=Coord.Dim(72, 'px')
        )
        self.assertEqual('px', myPt.x.units)
        self.assertEqual('px', myPt.y.units)
        self.assertEqual(Coord.Dim(72, 'px'), myPt.x)
        self.assertEqual(Coord.Dim(72, 'px'), myPt.y)
        newPt = Coord.convertPt(myPt, 'in')
        #print()
        #print(newPt)
        self.assertEqual('in', newPt.x.units)
        self.assertEqual('in', newPt.y.units)
        self.assertEqual(Coord.Dim(1, 'in'), newPt.x)
        self.assertEqual(Coord.Dim(1, 'in'), newPt.y)

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCoordDim)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCoordPoint))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCoordHelperFunctions))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    print("""TestCoord.py - Tests the Coord module.
Usage:
python TestCoord.py [-hl: --help]

Options:
-h, --help ~ Help (this screen) and exit.
-l:        ~ set the logging level higher is quieter.
             Default is 30 (WARNING) e.g.:
                CRITICAL    50
                ERROR       40
                WARNING     30
                INFO        20
                DEBUG       10
                NOTSET      0
""")

def main():
    print('TestCoord.py script version "%s", dated %s' % (__version__, __date__))
    print('Author: %s' % __author__)
    print(__rights__)
    print()
    import getopt
    import time
    print('Command line:')
    print(' '.join(sys.argv))
    print()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:", ["help",])
    except getopt.GetoptError as myErr:
        usage()
        print('ERROR: Invalid option: %s' % str(myErr))
        sys.exit(1)
    logLevel = logging.WARNING
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif o == '-l':
            logLevel = int(a)
    if len(args) != 0:
        usage()
        print('ERROR: Wrong number of arguments[%d]!' % len(args))
        sys.exit(1)
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=logLevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    unitTest()
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')

if __name__ == "__main__":
    main()
