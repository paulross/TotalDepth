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
"""Tests Units module.
"""

__author__  = 'Paul Ross'
__date__    = '2 Nov 2010'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2010 Paul Ross.'

#import pprint
import sys
import time
import logging
import random

from TotalDepth.LIS.core import Units

######################
# Section: Unit tests.
######################
import unittest

class TestInternals(unittest.TestCase):
    """Tests the internals of the Units module."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestInternals: Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestInternals(): __UNIT_MAP."""
        #print
        #print Units.unitCategories()
        self.assertEqual(
            sorted(Units.unitCategories()),
            sorted(
                [
                    b'VELO',
                    b'CURR',
                    b'ACCE',
                    b'VISC',
                    b'COND',
                    b'ENER',
                    b'TTIM',
                    b'V/LE',
                    b'DFRA',
                    b'TEMP',
                    b'HTRA',
                    b'DENS',
                    b'PERM',
                    b'ATTE',
                    b'MASS',
                    b'ROTA',
                    b'EGR ',
                    b'T/L ',
                    b'POWE',
                    b'UNKN',
                    b'LENG',
                    b'DIME',
                    b'FORC',
                    b'ILEN',
                    b'VOLU',
                    b'RESI',
                    b'C/T ',
                    b'M/L ',
                    b'PLEN',
                    b'FREQ',
                    b'IMAS',
                    b'ERES',
                    b'EPOT',
                    b'RVEL',
                    b'AREA',
                    b'TIME',
                    b'A/L ',
                    b'PRES',
                ]
            ),
        )

class TestUnitsBasic(unittest.TestCase):
    """Simple tests for Units module."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestUnitsBasic: Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestUnitsBasic.test_01(): Convert metres to feet."""
        self.assertEqual(Units.convert(1.0, b"M   ", b"FEET"), 1.0 / 0.3048)

class TestUnitsMultiple(unittest.TestCase):
    """Tests Units module multiple times."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestUnitsRandom: Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestUnitsBasic.test_01(): 1e5 random units converted to and fro and tested to 10 Sig. Fig."""
        myCats = Units.unitCategories()
        cCount = 0
        random.seed()
        tS = time.perf_counter()
        while cCount < 1e2:
            # Choose a category at random
            iC = random.randint(0, len(myCats)-1)
            myUnits = Units.units(myCats[iC])
            #print 'Category: %s' % myCats[iC]
            #print '   Units: %s' % ', '.join(myUnits)
            uCount = 0
            while uCount < 1e3:
                iU_1 = random.randint(0, len(myUnits)-1)
                iU_2 = random.randint(0, len(myUnits)-1)
                val = random.random()
                newVal = Units.convert(val, myUnits[iU_1], myUnits[iU_2])
                oldVal = Units.convert(newVal, myUnits[iU_2], myUnits[iU_1])
                #print
                #print(oldVal)
                self.assertAlmostEqual(oldVal, val, places=10)
                #self.assertAlmostEqual(oldVal, val)
                uCount +=1
            cCount +=1
        tE = time.perf_counter() - tS
        sys.stderr.write('Time: %8.3f rate %10.3f k/S ' % (tE, (cCount * uCount)/(1024*tE)))

    def test_03(self):
        """TestUnitsBasic.test_03(): 1e5  fixed units converted to and fro and tested to 10 Sig. Fig."""
        myCats = Units.unitCategories()
        cCount = 0
        random.seed()
        tS = time.perf_counter()
        while cCount < 1e2:
            # Choose a category at random
            iC = random.randint(0, len(myCats)-1)
            myUnits = Units.units(myCats[iC])
            iU_1 = random.randint(0, len(myUnits)-1)
            iU_2 = random.randint(0, len(myUnits)-1)
            val = random.random()
            uCount = 0
            while uCount < 1e3:
                newVal = Units.convert(val, myUnits[iU_1], myUnits[iU_2])
                self.assertAlmostEqual(
                    Units.convert(newVal, myUnits[iU_2], myUnits[iU_1]),
                    val,
                    places=10,
                )
                uCount +=1
            cCount +=1
        tE = time.perf_counter() - tS
        sys.stderr.write('Time: %8.3f rate %10.3f k/S ' % (tE, (cCount * uCount)/(1024*tE)))

    def test_04(self):
        """TestUnitsBasic.test_04(): 1e5  fixed units converted to and fro untested."""
        myCats = Units.unitCategories()
        cCount = 0
        random.seed()
        tS = time.perf_counter()
        while cCount < 1e1:
            # Choose a category at random
            iC = random.randint(0, len(myCats)-1)
            myUnits = Units.units(myCats[iC])
            iU_1 = random.randint(0, len(myUnits)-1)
            iU_2 = random.randint(0, len(myUnits)-1)
            val = random.random()
            uCount = 0
            while uCount < 1e4:
                newVal = Units.convert(val, myUnits[iU_1], myUnits[iU_2])
                uCount +=1
            cCount +=1
        tE = time.perf_counter() - tS
        sys.stderr.write('Time: %8.3f rate %10.3f k/S ' % (tE, (cCount * uCount)/(1024*tE)))

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestInternals))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUnitsBasic))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUnitsMultiple))
    myResult = unittest.TextTestRunner(descriptions=True, verbosity=theVerbosity).run(suite)
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
