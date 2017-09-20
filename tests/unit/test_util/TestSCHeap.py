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
"""

__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

#import pprint
import sys
import time
import logging
import random

from TotalDepth.util import SCHeap


######################
# Section: Unit tests.
######################
import unittest

#class TestSCHeapBinChopIntList(unittest.TestCase):
#    """Tests binary search for block"""
#    def setUp(self):
#        """Set up."""
#        self._sch = SCHeap.SCHeap()
#
#    def tearDown(self):
#        """Tear down."""
#        pass
#
#    def testSetUpTearDown(self):
#        """TestSCHeapFind: Tests setUp() and tearDown()."""
#        pass
#    
#    def test_00(self):
#        """TestSCHeapFind.test_00(): Binary search with binChopIntList()."""
#        myL = list(range(-4, 16, 4))
#        #print()
#        #print(myL)
#        #for i in range(-8, 16, 1):
#        #    print(i, self._sch.binChopIntList(i, myL))
#        self.assertEqual(0, self._sch.binChopIntList(-8, myL))
#        self.assertEqual(0, self._sch.binChopIntList(-7, myL))
#        self.assertEqual(0, self._sch.binChopIntList(-6, myL))
#        self.assertEqual(0, self._sch.binChopIntList(-5, myL))
#        self.assertEqual(0, self._sch.binChopIntList(-4, myL))
#        self.assertEqual(1, self._sch.binChopIntList(-3, myL))
#        self.assertEqual(1, self._sch.binChopIntList(-2, myL))
#        self.assertEqual(1, self._sch.binChopIntList(-1, myL))
#        self.assertEqual(1, self._sch.binChopIntList(0, myL))
#        self.assertEqual(2, self._sch.binChopIntList(1, myL))
#        self.assertEqual(2, self._sch.binChopIntList(2, myL))
#        self.assertEqual(2, self._sch.binChopIntList(3, myL))
#        self.assertEqual(2, self._sch.binChopIntList(4, myL))
#        self.assertEqual(3, self._sch.binChopIntList(5, myL))
#        self.assertEqual(3, self._sch.binChopIntList(6, myL))
#        self.assertEqual(3, self._sch.binChopIntList(7, myL))
#        self.assertEqual(3, self._sch.binChopIntList(8, myL))
#        self.assertEqual(4, self._sch.binChopIntList(9, myL))
#        self.assertEqual(4, self._sch.binChopIntList(10, myL))
#        self.assertEqual(4, self._sch.binChopIntList(11, myL))
#        self.assertEqual(4, self._sch.binChopIntList(12, myL))
#        self.assertEqual(5, self._sch.binChopIntList(13, myL))
#        self.assertEqual(5, self._sch.binChopIntList(14, myL))
#        self.assertEqual(5, self._sch.binChopIntList(15, myL))
        
class TestSCHeapFind(unittest.TestCase):
    """Tests binary search for block"""
    def setUp(self):
        """Set up."""
        self._sch = SCHeap.SCHeap()

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestSCHeapFind: Tests setUp() and tearDown()."""
        # Empty list
        self.assertEqual(0, len(self._sch))
        self.assertEqual(1, self._sch.retIdx(0))
    
    def test_00(self):
        """TestSCHeapFind.test_00(): Binary search."""
        for i in range(0, 12, 4):
            self._sch.add(i, i+2)
        #print()
        #print(self._sch)
        self.assertEqual(0, self._sch.retIdx(0))
        self.assertEqual(1, self._sch.retIdx(1))
        self.assertEqual(1, self._sch.retIdx(2))
        self.assertEqual(1, self._sch.retIdx(3))
        self.assertEqual(1, self._sch.retIdx(4))
        self.assertEqual(2, self._sch.retIdx(5))
        self.assertEqual(2, self._sch.retIdx(6))
        self.assertEqual(2, self._sch.retIdx(7))
        self.assertEqual(2, self._sch.retIdx(8))
        self.assertEqual(3, self._sch.retIdx(9))
        self.assertEqual(3, self._sch.retIdx(10))
        self.assertEqual(3, self._sch.retIdx(11))
        self.assertEqual(3, self._sch.retIdx(12))
        self.assertEqual(3, self._sch.retIdx(13))

    def test_01(self):
        """TestSCHeapFind.test_01(): Binary search start != 0."""
        for i in range(2, 14, 4):
            self._sch.add(i, i+2)
        #print()
        #print(self._sch)
        self.assertEqual(0, self._sch.retIdx(0))
        self.assertEqual(0, self._sch.retIdx(1))
        self.assertEqual(0, self._sch.retIdx(2))
        self.assertEqual(1, self._sch.retIdx(3))
        self.assertEqual(1, self._sch.retIdx(4))
        self.assertEqual(1, self._sch.retIdx(5))
        self.assertEqual(1, self._sch.retIdx(6))
        self.assertEqual(2, self._sch.retIdx(7))
        self.assertEqual(2, self._sch.retIdx(8))
        self.assertEqual(2, self._sch.retIdx(9))
        self.assertEqual(2, self._sch.retIdx(10))
        self.assertEqual(3, self._sch.retIdx(11))
        self.assertEqual(3, self._sch.retIdx(12))
        self.assertEqual(3, self._sch.retIdx(13))
        self.assertEqual(3, self._sch.retIdx(14))
        self.assertEqual(3, self._sch.retIdx(15))

    def test_02(self):
        """TestSCHeapFind.test_02(): Binary search add(500, 970)."""
        self._sch.add(500, 970)
        #self._sch.add(470, 500)
        #print()
        #print(self._sch)
        self.assertEqual(0, self._sch.retIdx(0))
        self.assertEqual(0, self._sch.retIdx(123))
        self.assertEqual(0, self._sch.retIdx(500))
        self.assertEqual(1, self._sch.retIdx(501))

    def test_03(self):
        """TestSCHeapFind.test_03(): Binary search add(123, 470), add(500, 970)."""
        self._sch.add(123, 470)
        self._sch.add(500, 970)
        #self._sch.add(470, 500)
        #print()
        #print(self._sch)
        self.assertEqual(0, self._sch.retIdx(0))
        self.assertEqual(0, self._sch.retIdx(123))
        self.assertEqual(1, self._sch.retIdx(124))
        self.assertEqual(1, self._sch.retIdx(470))
        self.assertEqual(1, self._sch.retIdx(500))
        self.assertEqual(2, self._sch.retIdx(501))

    def test_03(self):
        """TestSCHeapFind.test_03(): Binary search add(123, 470), add(500, 970) - reversed."""
        self._sch.add(500, 970)
        self._sch.add(123, 470)
        #self._sch.add(470, 500)
        #print()
        #print(self._sch)
        self.assertEqual(0, self._sch.retIdx(0))
        self.assertEqual(0, self._sch.retIdx(123))
        self.assertEqual(1, self._sch.retIdx(124))
        self.assertEqual(1, self._sch.retIdx(470))
        self.assertEqual(1, self._sch.retIdx(500))
        self.assertEqual(2, self._sch.retIdx(501))

class TestSCHeapAdd(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        self._sch = SCHeap.SCHeap()

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """SCHeap: Tests setUp() and tearDown() - empty ctor."""
        pass
    
    def test_00(self):
        """SCHeap.test_00(): __str__() on empty ctor."""
        #print()
        #print(self._sch)
        self.assertEqual('SCHeap:', str(self._sch))

    def test_01(self):
        """SCHeap.test_01(): __str__() single add()."""
        self._sch.add(123, 470)
        str(self._sch)
        #print()
        #print(list(self._sch.genBlocks()))
        self.assertEqual(
            [
                (False, SCHeap.Block(0, 123)),
                (True, SCHeap.Block(123, 470)),
            ],
            list(self._sch.genBlocks())
        )

    def test_02(self):
        """SCHeap.test_02(): __str__() add() two separate blocks."""
        self._sch.add(123, 470)
        self._sch.add(500, 970)
        #print()
        #print(list(self._sch.genBlocks()))
        self.assertEqual(
            [
                (False, SCHeap.Block(0, 123)),
                (True, SCHeap.Block(123, 470)),
                (False, SCHeap.Block(470, 500)),
                (True, SCHeap.Block(500, 970)),
            ],
            list(self._sch.genBlocks())
        )

    def test_03(self):
        """SCHeap.test_03(): __str__() add() two separate blocks, order reversed."""
        self._sch.add(500, 970)
        self._sch.add(123, 470)
        #print()
        #print(list(self._sch.genBlocks()))
        self.assertEqual(
            [
                (False, SCHeap.Block(0, 123)),
                (True, SCHeap.Block(123, 470)),
                (False, SCHeap.Block(470, 500)),
                (True, SCHeap.Block(500, 970)),
            ],
            list(self._sch.genBlocks())
        )
        #self.assertEqual('SCHeap:', str(self._sch))

    def test_04(self):
        """SCHeap.test_04(): __str__() add() two adjacent blocks."""
        #print()
        self._sch.add(123, 470)
        self._sch.add(470, 900)
        #print(list(self._sch.genBlocks()))
        self.assertEqual(
            [
                (False, SCHeap.Block(0, 123)),
                (True, SCHeap.Block(123, 900)),
            ],
            list(self._sch.genBlocks())
        )

    def test_05(self):
        """SCHeap.test_05(): __str__() add() two adjacent blocks, order reversed."""
        #print()
        self._sch.add(470, 900)
        self._sch.add(123, 470)
        #print(list(self._sch.genBlocks()))
        self.assertEqual(
            [
                (False, SCHeap.Block(0, 123)),
                (True, SCHeap.Block(123, 900)),
            ],
            list(self._sch.genBlocks())
        )

    def test_06(self):
        """SCHeap.test_06(): __str__() add() two separate blocks then filled."""
        #print()
        self._sch.add(123, 470)
        self._sch.add(500, 970)
        #print(list(self._sch.genBlocks()))
        self._sch.add(470, 500)
        #print(list(self._sch.genBlocks()))
        self.assertEqual(
            [
                (False, SCHeap.Block(0, 123)),
                (True, SCHeap.Block(123, 970)),
            ],
            list(self._sch.genBlocks())
        )

    def test_20(self):
        """SCHeap.test_20(): __str__() add() fails as input is wrong."""
        #print()
        self.assertRaises(SCHeap.ExceptionSCHeap, self._sch.add, -123, 470)
        self.assertRaises(SCHeap.ExceptionSCHeap, self._sch.add, 123, 122)
        self.assertRaises(SCHeap.ExceptionSCHeap, self._sch.add, 123, 123)

    def test_21(self):
        """SCHeap.test_21(): __str__() add() fails as block will not fit."""
        #print()
        #print(list(self._sch.genBlocks()))
        self._sch.add(123, 470)
        self.assertRaises(SCHeap.ExceptionSCHeap, self._sch.add, 469, 471)
        self.assertRaises(SCHeap.ExceptionSCHeap, self._sch.add, 122, 124)
        self._sch.add(500, 600)
        self.assertRaises(SCHeap.ExceptionSCHeap, self._sch.add, 469, 500)
        

class TestSCHeapNeed(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        self._sch = SCHeap.SCHeap()

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """SCHeap: Tests setUp() and tearDown() - empty ctor."""
        pass
    
    def test_00(self):
        """SCHeap.test_00(): __str__() on empty ctor."""
        #print()
        #print(self._sch)
        self.assertEqual('SCHeap:', str(self._sch))

    def test_10(self):
        """SCHeap.test_10(): __str__() need() on empty list."""
        #print()
        #print(list(self._sch.genBlocks()))
        self.assertEqual(
            [
                SCHeap.Block(150, 670),
            ],
            self._sch.need(150, 670)
        )

    def test_11(self):
        """SCHeap.test_11(): __str__() need() leading block when single block in list."""
        self._sch.add(100, 400)
        self.assertEqual([SCHeap.Block(50, 100),], self._sch.need(50, 170))

    def test_12(self):
        """SCHeap.test_12(): __str__() need() trailing block when single block in list."""
        self._sch.add(100, 400)
        self.assertEqual([SCHeap.Block(400, 450),], self._sch.need(150, 450))

    def test_13(self):
        """SCHeap.test_13(): __str__() need() spanning block when single block in list."""
        #print()
        self._sch.add(100, 400)
        #print(list(self._sch.genBlocks()))
        self.assertEqual(
            [
                SCHeap.Block(50, 100),
                SCHeap.Block(400, 450),
            ],
            self._sch.need(50, 450)
        )

    def test_14(self):
        """SCHeap.test_14(): __str__() need() single intermediate block when two blocks in list."""
        #print()
        self._sch.add(100, 200)
        self._sch.add(300, 400)
        #print(list(self._sch.genBlocks()))
        self.assertEqual(
            [
                SCHeap.Block(200, 300),
            ],
            self._sch.need(150, 350)
        )

    def test_15(self):
        """SCHeap.test_15(): __str__() need() leading + intermediate block when two blocks in list."""
        #print()
        self._sch.add(100, 200)
        self._sch.add(300, 400)
        #print(list(self._sch.genBlocks()))
        self.assertEqual(
            [
                SCHeap.Block(50, 100),
                SCHeap.Block(200, 300),
            ],
            self._sch.need(50, 350)
        )

    def test_16(self):
        """SCHeap.test_16(): __str__() need() intermediate + trailing block when two blocks in list."""
        #print()
        self._sch.add(100, 200)
        self._sch.add(300, 400)
        #print(list(self._sch.genBlocks()))
        self.assertEqual(
            [
                SCHeap.Block(200, 300),
                SCHeap.Block(400, 450),
            ],
            self._sch.need(150, 450)
        )

    def test_17(self):
        """SCHeap.test_17(): __str__() need() leading + intermediate + trailing block when two blocks in list."""
        #print()
        self._sch.add(100, 200)
        self._sch.add(300, 400)
        #print(list(self._sch.genBlocks()))
        self.assertEqual(
            [
                SCHeap.Block(50, 100),
                SCHeap.Block(200, 300),
                SCHeap.Block(400, 450),
            ],
            self._sch.need(50, 450)
        )

    def test_17(self):
        """SCHeap.test_17(): __str__() need() leading + trailing block when overlapping first of two blocks in list."""
        #print()
        self._sch.add(100, 200)
        self._sch.add(300, 400)
        #print(list(self._sch.genBlocks()))
        self.assertEqual(
            [
                SCHeap.Block(50, 100),
                SCHeap.Block(200, 250),
            ],
            self._sch.need(50, 250)
        )

class TestSCHeapRandom_Perf(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        self._sch = SCHeap.SCHeap()
        random.seed()

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestSCHeapRandom_Perf: Tests setUp() and tearDown() - empty ctor."""
        pass

    def _reportTime(self, numVals, clkStart):
        execTime = time.clock()-clkStart
        if execTime > 0.0:
            sys.stderr.write('Number={:d} Time={:f}(s) Rate={:.0f} '.format(
                numVals,
                execTime,
                numVals / execTime))
        else:
            sys.stderr.write('Number={:d} Time={:f}(s) Rate=N/A} '.format(
                numVals,
                execTime,
                ))
        
    def _timeRetIdx(self, numAdds, numTests):
        """Times retIdx() access."""
        self._randomLoad(numAdds)
        valS = [random.randint(0, 1<<30) for v in range(numTests)]
        clkStart = time.clock()
        for v in valS:
            self._sch.retIdx(v)
        self._reportTime(numTests, clkStart)

    def _timeAdd(self, numAdd, b0=30, b1=10):
        self._sch.clear()
        valS = []
        for i in range(numAdd):
            start = random.randint(0, 1 << b0)
            stop = start + random.randint(0, 1 << b1)
            valS.append((start, stop))
        clkStart = time.clock()
        for sta, sto in valS:
            try:
                self._sch.add(sta, sto)
            except SCHeap.ExceptionSCHeap:
                pass
        self._reportTime(numAdd, clkStart)
        self.assertTrue(len(self._sch) <= numAdd)
    
    def _randomLoad(self, numAdd, b0=30, b1=10):
        """Loads the SCHeap with numAdd random blocks start up to 2<<b0, length
        up to 2<<b1."""
        self._sch.clear()
        for i in range(numAdd):
            start = random.randint(0, 1 << b0)
            stop = start + random.randint(1, 1 << 8)
            try:
                self._sch.add(start, stop)
            except SCHeap.ExceptionSCHeap:
                pass
        self.assertTrue(len(self._sch) <= numAdd)
    
    def _randomNeed(self, numNeed, b0=30, b1=10):
        """Extracts need list from SCHeap numNeed times, start up to 2<<b0, length
        up to 2<<b1."""
        clkStart = time.clock()
        for i in range(numNeed):
            start = random.randint(0, 1 << b0)
            stop = start + random.randint(1, 1 << b1)
            self._sch.need(start, stop)
        self._reportTime(numNeed, clkStart)

    def _randomFill(self, numNeed, b0=30, b1=10):
        """Extracts need list from SCHeap numNeed times and adds it, start up
        to 2<<b0, length up to 2<<b1."""
        clkStart = time.clock()
        for i in range(numNeed):
            start = random.randint(0, 1 << b0)
            stop = start + random.randint(1, 1 << b1)
            for sta, sto in self._sch.need(start, stop):
                self._sch.add(sta, sto)
        self._reportTime(numNeed, clkStart)

    def test_00(self):
        """TestSCHeapRandom_Perf.test_00(): __str__() random load  1024, random retIdx()   128 times."""
        self._timeRetIdx(1024, 128)

    def test_01(self):
        """TestSCHeapRandom_Perf.test_01(): __str__() random load  1024, random retIdx()  1024 times."""
        self._timeRetIdx(1024, 1024)

    def test_02(self):
        """TestSCHeapRandom_Perf.test_02(): __str__() random load  1024, random retIdx()  8192 times."""
        self._timeRetIdx(1024, 8*1024)

    def test_03(self):
        """TestSCHeapRandom_Perf.test_03(): __str__() random load  1024, random retIdx() 65536 times."""
        self._timeRetIdx(1024, 64*1024)

    def test_04(self):
        """TestSCHeapRandom_Perf.test_04(): __str__() random load  8192, random retIdx()  8192 times."""
        self._timeRetIdx(8*1024, 8*1024)

#    def test_05(self):
#        """TestSCHeapRandom_Perf.test_05(): __str__() random load 65536, random retIdx()  8192 times."""
#        self._timeRetIdx(8*8*1024, 8*1024)

    def test_10(self):
        """TestSCHeapRandom_Perf.test_10(): __str__() random load   128 items."""
        self._timeAdd(128)

    def test_11(self):
        """TestSCHeapRandom_Perf.test_11(): __str__() random load   1024 items."""
        self._timeAdd(1024)

    def test_12(self):
        """TestSCHeapRandom_Perf.test_12(): __str__() random load   8192 items."""
        self._timeAdd(1024*8)

#    def test_13(self):
#        """TestSCHeapRandom_Perf.test_13(): __str__() random load  65536 items."""
#        self._timeAdd(1024*8*8)

    def test_20(self):
        """TestSCHeapRandom_Perf.test_20(): __str__() random load 1024, random need()   128 times."""
        self._randomLoad(1024)
        self._randomNeed(128)

    def test_21(self):
        """TestSCHeapRandom_Perf.test_21(): __str__() random load 1024, random need()  1024 times."""
        self._randomLoad(1024)
        self._randomNeed(1024)

    def test_22(self):
        """TestSCHeapRandom_Perf.test_22(): __str__() random load 1024, random need()  8192 times."""
        self._randomLoad(1024)
        self._randomNeed(1024*8)

#    def test_23(self):
#        """TestSCHeapRandom_Perf.test_23(): __str__() random load, random need() 65536 times."""
#        self._randomLoad(1024)
#        self._randomNeed(1024*8*8)

    def test_30(self):
        """TestSCHeapRandom_Perf.test_30(): __str__() random load, random need() and add()   128 times."""
        self._randomLoad(1024)
        self._randomFill(128)

    def test_31(self):
        """TestSCHeapRandom_Perf.test_31(): __str__() random load, random need() and add()  1024 times."""
        self._randomLoad(1024)
        self._randomFill(1024)

    def test_32(self):
        """TestSCHeapRandom_Perf.test_32(): __str__() random load, random need() and add()  8192 times."""
        self._randomLoad(1024)
        self._randomFill(1024*8)

#    def test_33(self):
#        """TestSCHeapRandom_Perf.test_33(): __str__() random load, random need() and add() 65536 times."""
#        self._randomLoad(1024)
#        self._randomFill(1024*8*8)

class Special(unittest.TestCase):
    """Special tests."""
    def setUp(self):
        """Set up."""
        self._sch = SCHeap.SCHeap()

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestSCHeapFind: Tests setUp() and tearDown()."""
        pass

#    def test_20(self):
#        """SCHeap.test_20(): __str__() add() fails."""
#        #print()
#        self.assertRaises(SCHeap.ExceptionSCHeap, self._sch.add, -123, 470)
#        self.assertRaises(SCHeap.ExceptionSCHeap, self._sch.add, 123, 122)
#        self.assertRaises(SCHeap.ExceptionSCHeap, self._sch.add, 123, 123)
#        self._sch.add(123, 470)
#        #self._sch.add(469, 471)
#        #print(list(self._sch.genBlocks()))
#        self.assertRaises(SCHeap.ExceptionSCHeap, self._sch.add, 469, 471)
#        self.assertRaises(SCHeap.ExceptionSCHeap, self._sch.add, 122, 124)
#        self._sch.add(500, 600)
#        #print(list(self._sch.genBlocks()))
#        #self._sch.add(469, 500)
#        #print(list(self._sch.genBlocks()))
#        self.assertRaises(SCHeap.ExceptionSCHeap, self._sch.add, 469, 500)
        
#    def test_05(self):
#        """SCHeap.test_05(): __str__() add() two adjacent blocks, order reversed."""
#        print()
#        self._sch.add(470, 900)
#        self._sch.add(123, 470)
#        #print(list(self._sch.genBlocks()))
#        self.assertEqual(
#            [
#                (False, SCHeap.Block(0, 123)),
#                (True, SCHeap.Block(123, 900)),
#            ],
#            list(self._sch.genBlocks())
#        )



def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSCHeapBinChopIntList))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSCHeapFind))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSCHeapAdd))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSCHeapNeed))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSCHeapRandom_Perf))
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
    clkStart = time.clock()
    unitTest()
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')

if __name__ == "__main__":
    main()
