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
"""Tests RepCode
"""
import pytest

__author__  = 'Paul Ross'
__date__    = '2 Nov 2010'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2010 Paul Ross.'

import os
import sys
import time
import logging
import random
import io
import math

# Generic methods, these choose between Python and Cython
from TotalDepth.LIS.core import RepCode
# Python reference methods
from TotalDepth.LIS.core import pRepCode
## Cython methods
from TotalDepth.LIS.core import cRepCode
# For testing read operations
from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import PhysRec

######################
# Section: Unit tests.
######################
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import BaseTestClasses

#class TestRepCodeBase(BaseTestClasses.TestBase):
#    def randBits(self, theBits):
#        """Return a random integer of theBits number of bits."""
#        return random.getrandbits(theBits)
#    
#    def randWord(self, s, e, m):
#        """Return a random word with s, e and m number of bits set randomly."""
#        w = self.randBits(s)
#        w <<= e
#        w |= self.randBits(e)
#        w <<= m
#        w |= self.randBits(m)
#        return w
#    
#    def randInt(self, theMin, theMax):
#        return random.randint(theMin, theMax)
#    
#    def roundToDecimalSigDigits(self, v, s):
#        #print 'TRACE: roundToDecimalSigDigits() 0:', v, s
#        m, exp = math.frexp(v)
#        #print 'TRACE: roundToDecimalSigDigits() 1:', m, exp
#        # m is 0.5 <= m < 1.0, make it 0 <= m < 1.0
#        m = m * 2.0 - 1.0
#        m *= 10**s
#        m = float(int(m))
#        #print 'TRACE: roundToDecimalSigDigits() 2:', m, exp
#        m /= 10**s
#        m = (m + 1.0) / 2.0
#        #print 'TRACE: roundToDecimalSigDigits() 3:', m, exp
#        r = math.ldexp(m, exp)
#        #print 'TRACE: roundToDecimalSigDigits() 4:', r
#        return r
#
#    def writeTimeToStdErr(self, start, rc, numWords):
#        tE = time.perf_counter() - start
#        siz = numWords * RepCode.lisSize(rc)
#        print('Time: {:.3f} Rate {:8.0f} words/S '.format(tE, numWords/tE))
#        print(' Cost: {:.3f} (ms/MB)'.format((tE*1024)/(siz/(1024*1024))))
        

#class TestRepCodeFrom49(BaseTestClasses.TestRepCodeBase):
#    """Tests ..."""
#    def test_size(self):
#        """TestRepCodeFrom49.test_size(): word length of 2."""
#        self.assertEqual(RepCode.lisSize(49), 2)
#
#    def test_minmax(self):
#        """TestRepCodeFrom49.test_minmax(): min/max."""
#        #print
#        #print RepCode.minMaxValue(49)
#        print(str(RepCode.minMaxValue(49)))
#        print(' ')
#        self.assertEqual(RepCode.minMaxValue(49), (-32768.0, 32752.0))
#
#    def test_01(self):
#        """TestRepCodeFrom49.test_01(): from49(0x4C88) -> 153.0."""
#        self.assertEqual(RepCode.from49(0x4C88), 153.0)
#
#    def test_02(self):
#        """TestRepCodeFrom49.test_02(): from49(0xB388) -> -153.0."""
#        self.assertEqual(RepCode.from49(0xB388), -153.0)
#
#    def test_11(self):
#        """TestRepCodeFrom49.test_11(): to49(153.0) -> 0x4C88."""
#        #print
#        #print 'RepCode.to49(153.0): 0x%x' % RepCode.to49(153.0)
#        self.assertEqual(RepCode.to49(153.0), 0x4C88)
#
#    def test_12(self):
#        """TestRepCodeFrom49.test_12(): to49(153.0) -> 0xB388."""
#        #print
#        #print 'RepCode.to49(-153.0): 0x%x' % RepCode.to49(-153.0)
#        self.assertEqual(RepCode.to49(-153.0), 0xB388)
#
#    def test_21(self):
#        """TestRepCodeFrom49.test_21(): to49(min) -32768.0 -> 0x800F."""
#        myMin = RepCode.minValue(49)
#        self.assertEqual(myMin, -32768.0)
#        self.assertEqual(RepCode.to49(myMin), 0x800F)
#        return
#        print()
#
#    def test_22(self):
#        """TestRepCodeFrom49.test_22(): to49(max) -> 0x7FFF."""
#        myMax = RepCode.maxValue(49)
##        print
##        print 'RepCode.to49(max): 0x%x' % RepCode.to49(myMax)
##        print 'RepCode.to49(max): 0x7FFF %f' % RepCode.from49(0x7FFF)
##        print 'RepCode.to49(max): 32752.0 0x%x' % RepCode.to49(32752.0)
##        print 'RepCode.to49(max): 2 * 32752.0 0x%x' % RepCode.to49(2 * 32752.0)
#        self.assertEqual(RepCode.to49(myMax), 0x7FFF)
#
#    def test_30(self):
#        """TestRepCodeFrom49.test_12(): SPV: 0x0010 <-> 1/2048.0."""
#        self.assertEqual(RepCode.from49(0x0010), 1/2048.0)
#        print()
#        print(('0x%x' % RepCode.to49(1/2048.0)))
#        self.assertEqual(RepCode.to49(1/2048.0), 0x0010)

class TestRepCodeFrom49(BaseTestClasses.TestRepCodeBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom49.test_00(): tests setUp() and tearDown()."""
        pass

    def test_size(self):
        """TestRepCodeFrom49.test_size(): word length of 4."""
        self.assertEqual(RepCode.lisSize(49), 2)

    def test_minmax(self):
        """TestRepCodeFrom49.test_minmax(): min/max."""
        #print
        #print RepCode.minMaxValue(49)
        print(str(RepCode.minMaxValue(49)))
        print(' ')
        self.assertEqual(RepCode.minMaxValue(49), (-32768.0, 32752.0))

    def test_min(self):
        """TestRepCodeFrom49.test_min(): min by bit stuffing."""
        myWord = 0x800F
        #self.assertEqual(RepCode.from49(myWord), RepCode.minValue(49))
        #self.assertEqual(pRepCode.from49(myWord), RepCode.minValue(49))
        self.assertEqual(cRepCode.from49(myWord), RepCode.minValue(49))

    def test_max(self):
        """TestRepCodeFrom49.test_max(): max by bit stuffing."""
        myWord = 0x7FFF
        f = RepCode.from49(myWord)
        #m,e = math.frexp(f)
        #print
        #print 'Max:', f
        #print 'm,e:', m,e
        #print 'm:      shifted 23', m * (1<<23)
        #print 'm: 1.0 / (1.0 - m)', 1.0 / (1.0 - m)
        #print '             2**23', 2**23
        #print '             1<<23', 1<<23
        #print('dir(RepCode)')
        #print(dir(RepCode))
        self.assertEqual(RepCode.from49(myWord), RepCode.maxValue(49))
        self.assertEqual(cRepCode.from49(myWord), RepCode.maxValue(49))
        self.assertEqual(pRepCode.from49(myWord), RepCode.maxValue(49))

    def test_01(self):
        """TestRepCodeFrom49.test_01__(): from49(0x4C88) -> 153.0."""
        self.assertEqual(RepCode.from49(0x4C88), 153.0)

    def test_01_c(self):
        """TestRepCodeFrom49.test_01_c(): from49(0x4C88) -> 153.0 Cython."""
        self.assertEqual(cRepCode.from49(0x4C88), 153.0)

    def test_01_p(self):
        """TestRepCodeFrom49.test_01_p(): from49(0x4C88) -> 153.0 Python."""
        self.assertEqual(pRepCode.from49(0x4C88), 153.0)

    def test_02(self):
        """TestRepCodeFrom49.test_02__(): from49(0xB388) -> -153.0."""
        self.assertEqual(RepCode.from49(0xB388), -153.0)

    def test_02_c(self):
        """TestRepCodeFrom49.test_02_c(): from49(0xB388) -> -153.0 Cython."""
        self.assertEqual(cRepCode.from49(0xB388), -153.0)

    def test_02_p(self):
        """TestRepCodeFrom49.test_02_p(): from49(0xB388) -> -153.0 Python."""
        self.assertEqual(pRepCode.from49(0xB388), -153.0)
        
    def test_04(self):
        """TestRepCodeFrom49.test_04__(): from49(0x0000) -> 0.0."""
        self.assertEqual(RepCode.from49(0x0000), 0.0)

    def test_04_c(self):
        """TestRepCodeFrom49.test_04_c(): from49(0x0000) -> 0.0 Cython."""
        self.assertEqual(cRepCode.from49(0x0000), 0.0)

    def test_04_p(self):
        """TestRepCodeFrom49.test_04_p(): from49(0x0000) -> 0.0 Python."""
        self.assertEqual(pRepCode.from49(0x0000), 0.0)

    def test_11(self):
        """TestRepCodeFrom49.test_11(): read49(0x4C88) -> 153.0."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 2) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x4c\x88' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(pRepCode.read49(myFile), 153.0)
        self.assertFalse(myFile.hasLd())

    def test_12(self):
        """TestRepCodeFrom49.test_12(): read49(0xB388) -> -153.0."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 2) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\xb3\x88' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(pRepCode.read49(myFile), -153.0)
        self.assertFalse(myFile.hasLd())


@pytest.mark.slow
class TestRepCodeFrom49Time(BaseTestClasses.TestRepCodeBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom49.test_00(): tests setUp() and tearDown()."""
        pass

    def test_time_00(self):
        """TestRepCodeFrom49.test_time_00(): tests conversion of 1e6 of same word - Cython code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from49(0x4C88)
            i += 1
        self.writeTimeToStdErr(tS, 49, num)
        
    def test_time_01(self):
        """TestRepCodeFrom49.test_time_01(): tests conversion of 1e6 of same word - Python code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            pRepCode.from49(0x4C88)
            i += 1
        self.writeTimeToStdErr(tS, 49, num)
        
    def test_time_02(self):
        """TestRepCodeFrom49.test_time_00(): tests conversion of 1e6 of same word - Cython time c.f. Python: """
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from49(0x4C88)
            i += 1
        tE_C = time.perf_counter() - tS
        #print 'C time: %.3f rate %8.0f words/S' % (tE_C, num/tE_C)
        i = 0
        tS = time.perf_counter()
        while i < num:
            pRepCode.from49(0x4C88)
            i += 1
        tE_P = time.perf_counter() - tS
        #print 'Python time: %.3f rate %8.0f words/S' % (tE_P, num/tE_P)
        #print('Cython: %.3f% ' % tE_C)
        #print('Python: %.3f% ' % tE_P)
        print('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))
        
    def test_time_10(self):
        """TestRepCodeFrom49.test_time_10(): tests conversion of 1e5 random words - Cython code."""
        i = 0
        num = 1e5
        tS = time.perf_counter()
        while i < num:
            cRepCode.from49(self.randWord(1, 7, 8))
            i += 1
        self.writeTimeToStdErr(tS, 49, num)
        
    def test_time_11(self):
        """TestRepCodeFrom49.test_time_11(): tests conversion of 1e5 random words - Python code."""
        i = 0
        num = 1e5
        tS = time.perf_counter()
        while i < num:
            pRepCode.from49(self.randWord(1, 7, 8))
            i += 1
        self.writeTimeToStdErr(tS, 49, num)

    def test_time_20(self):
        """TestRepCodeFrom49.test_time_20(): 2e5 word conversion from FileRead: """
        i = 0
        numWords = 2e5
        myWord = b'\x4c\x88'
        wordsInPr = int((PhysRec.PR_MAX_LENGTH - PhysRec.PR_PRH_LENGTH)/  len(myWord))
        # Suc no Pre: 1
        # Pre no Suc: 2
        # Suc and Pre: 3
        prContStart = PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        prContBody = PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(3) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        prContEnd = PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(2) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        # How many physical records
        numPr = int(numWords/wordsInPr)
        numPrBody = numPr - 2
        assert(numPrBody >= 0)
        # Python code first
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            pRepCode.read49(myFile)
            i += 1
        tE_P = time.perf_counter() - tS
        self.assertFalse(myFile.hasLd())
        print('Python: %.3f %8.0f words/S ' % (tE_P, numWords/tE_P))
        # Now Cython code
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            RepCode.read49(myFile)
            i += 1
        tE_C = time.perf_counter() - tS
        self.assertFalse(myFile.hasLd())
        print('Cython: %.3f %8.0f words/S ' % (tE_C, numWords/tE_C))
        print('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))

class TestRepCodeFrom50(BaseTestClasses.TestRepCodeBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom50.test_00(): tests setUp() and tearDown()."""
        pass

    def test_size(self):
        """TestRepCodeFrom50.test_size(): word length of 4."""
        self.assertEqual(RepCode.lisSize(50), 4)

    def test_minmax(self):
        """TestRepCodeFrom50.test_minmax(): min/max."""
        #print
        #print RepCode.minMaxValue(50)
        print(str(RepCode.minMaxValue(50)))
        print(' ')
        self.assertEqual(
            RepCode.minMaxValue(50),
            (-8.98846567431158e+307, 8.98819136810814e+307)
        )

    def test_min(self):
        """TestRepCodeFrom50.test_min(): min by bit stuffing."""
        # NOTE: We don't use exponent 0x8000... as that will cause
        # an overflow on IEEE-754 doubles
        myWord = 0x7FFF8000
        self.assertEqual(RepCode.from50(myWord), RepCode.minValue(50))
        self.assertEqual(cRepCode.from50(myWord), RepCode.minValue(50))
        self.assertEqual(pRepCode.from50(myWord), RepCode.minValue(50))

    def test_max(self):
        """TestRepCodeFrom50.test_max(): max by bit stuffing."""
        # NOTE: We don't use exponent 0x8000... as that will cause
        # an overflow on IEEE-754 doubles
        myWord = 0x7FFF7FFF
        self.assertEqual(RepCode.from50(myWord), RepCode.maxValue(50))
        self.assertEqual(cRepCode.from50(myWord), RepCode.maxValue(50))
        self.assertEqual(pRepCode.from50(myWord), RepCode.maxValue(50))

    def test_01(self):
        """TestRepCodeFrom50.test_01__(): from50(0x00084C80) -> 153.0."""
        self.assertEqual(RepCode.from50(0x00084C80), 153.0)

    def test_01_c(self):
        """TestRepCodeFrom50.test_01_c(): from50(0x00084C80) -> 153.0 Cython."""
        self.assertEqual(cRepCode.from50(0x00084C80), 153.0)

    def test_01_p(self):
        """TestRepCodeFrom50.test_01_p(): from50(0x00084C80) -> 153.0 Python."""
        self.assertEqual(pRepCode.from50(0x00084C80), 153.0)

    def test_02(self):
        """TestRepCodeFrom50.test_02__(): from50(0x0008B380) -> -153.0."""
        self.assertEqual(RepCode.from50(0x0008B380), -153.0)

    def test_02_c(self):
        """TestRepCodeFrom50.test_02_c(): from50(0x0008B380) -> -153.0 Cython."""
        self.assertEqual(cRepCode.from50(0x0008B380), -153.0)

    def test_02_p(self):
        """TestRepCodeFrom50.test_02_p(): from50(0x0008B380) -> -153.0 Python."""
        self.assertEqual(pRepCode.from50(0x0008B380), -153.0)
        
    def test_04(self):
        """TestRepCodeFrom50.test_04__(): from50(0x00000000) -> 0.0."""
        self.assertEqual(RepCode.from50(0x00000000), 0.0)

    def test_04_c(self):
        """TestRepCodeFrom50.test_04_c(): from50(0x00000000) -> 0.0 Cython."""
        self.assertEqual(cRepCode.from50(0x00000000), 0.0)

    def test_04_p(self):
        """TestRepCodeFrom50.test_04_p(): from50(0x00000000) -> 0.0 Python."""
        self.assertEqual(pRepCode.from50(0x00000000), 0.0)

    def test_11(self):
        """TestRepCodeFrom50.test_11(): read50(0x00084C80) -> 153.0."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 4) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x00\x08\x4c\x80' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(pRepCode.read50(myFile), 153.0)
        self.assertFalse(myFile.hasLd())

    def test_12(self):
        """TestRepCodeFrom50.test_12(): read50(0x0008B380) -> -153.0."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 4) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x00\x08\xb3\x80' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(pRepCode.read50(myFile), -153.0)
        self.assertFalse(myFile.hasLd())


@pytest.mark.slow
class TestRepCodeFrom50Time(BaseTestClasses.TestRepCodeBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom50.test_00(): tests setUp() and tearDown()."""
        pass

    def test_time_00(self):
        """TestRepCodeFrom50.test_time_00(): tests conversion of 1e6 of same word - Cython code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from50(0xBBB38000)
            i += 1
        self.writeTimeToStdErr(tS, 50, num)
        
    def test_time_01(self):
        """TestRepCodeFrom50.test_time_01(): tests conversion of 1e6 of same word - Python code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            pRepCode.from50(0xBBB38000)
            i += 1
        self.writeTimeToStdErr(tS, 50, num)
        
    def test_time_02(self):
        """TestRepCodeFrom50.test_time_00(): tests conversion of 1e6 of same word - Cython time c.f. Python: """
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from50(0xBBB38000)
            i += 1
        tE_C = time.perf_counter() - tS
        #print 'C time: %.3f rate %8.0f words/S' % (tE_C, num/tE_C)
        i = 0
        tS = time.perf_counter()
        while i < num:
            pRepCode.from50(0xBBB38000)
            i += 1
        tE_P = time.perf_counter() - tS
        #print 'Python time: %.3f rate %8.0f words/S' % (tE_P, num/tE_P)
        #print('Cython: %.3f% ' % tE_C)
        #print('Python: %.3f% ' % tE_P)
        print('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))
        
    def test_time_10(self):
        """TestRepCodeFrom50.test_time_10(): tests conversion of 1e5 random words - Cython code."""
        i = 0
        num = 1e5
        tS = time.perf_counter()
        while i < num:
            cRepCode.from50(self.randWord(1, 8, 23))
            i += 1
        self.writeTimeToStdErr(tS, 50, num)
        
    def test_time_20(self):
        """TestRepCodeFrom50.test_time_20(): 1e5 word conversion from FileRead: """
        i = 0
        numWords = 1e5
        myWord = b'\x44\x4c\x80\x00'
        wordsInPr = int((PhysRec.PR_MAX_LENGTH - PhysRec.PR_PRH_LENGTH)/ len(myWord))
        # Suc no Pre: 1
        # Pre no Suc: 2
        # Suc and Pre: 3
        prContStart = PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        prContBody = PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(3) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        prContEnd = PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(2) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        # How many physical records
        numPr = int(numWords/wordsInPr)
        numPrBody = numPr - 2
        assert(numPrBody >= 0)
        # Python code first
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            pRepCode.read50(myFile)
            i += 1
        tE_P = time.perf_counter() - tS
        self.assertFalse(myFile.hasLd())
        print('Python: %.3f %8.0f words/S ' % (tE_P, numWords/tE_P))
        # Now Cython code
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            RepCode.read50(myFile)
            i += 1
        tE_C = time.perf_counter() - tS
        self.assertFalse(myFile.hasLd())
        print('Cython: %.3f %8.0f words/S ' % (tE_C, numWords/tE_C))
        print('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))

class TestRepCodeFrom56(BaseTestClasses.TestRepCodeBase):
    """Tests repCode 56"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom56.test_00(): tests setUp() and tearDown()."""
        pass

    def test_size(self):
        """TestRepCodeFrom56.test_size(): word length of 2."""
        self.assertEqual(RepCode.lisSize(56), 1)

    def test_minmax(self):
        """TestRepCodeFrom56.test_minmax(): min/max."""
        print(str(RepCode.minMaxValue(56)))
        print(' ')
        self.assertEqual(RepCode.minMaxValue(56), (-128, 127))

    def test_min(self):
        """TestRepCodeFrom56.test_min(): min by bit stuffing."""
        myWord = -0x80
        self.assertEqual(RepCode.from56(myWord), RepCode.minValue(56))
        self.assertEqual(pRepCode.from56(myWord), RepCode.minValue(56))

    def test_max(self):
        """TestRepCodeFrom56.test_max(): max by bit stuffing."""
        myWord = 0x7F
        self.assertEqual(RepCode.from56(myWord), RepCode.maxValue(56))
        self.assertEqual(pRepCode.from56(myWord), RepCode.maxValue(56))

    def test_01(self):
        """TestRepCodeFrom56.test_01__(): from56(0x59) -> 89"""
        self.assertEqual(RepCode.from56(0x59), 89)

    def test_01_c(self):
        """TestRepCodeFrom56.test_01_c(): from56(0x59) -> 89 Cython."""
        self.assertEqual(cRepCode.from56(0x59), 89)

    def test_01_p(self):
        """TestRepCodeFrom56.test_01_p(): from56(0x59) -> 89 Python."""
        self.assertEqual(pRepCode.from56(0x59), 89)

    def test_02(self):
        """TestRepCodeFrom56.test_02__(): from56(0xA7) -> -89"""
        self.assertEqual(RepCode.from56(-89), -89)

    def test_02_c(self):
        """TestRepCodeFrom56.test_02_c(): from56(0xA7) -> -89 Cython."""
        self.assertEqual(cRepCode.from56(-89), -89)

    def test_02_p(self):
        """TestRepCodeFrom56.test_02_p(): from56(0xA7) -> -89 Python."""
        self.assertEqual(pRepCode.from56(-89), -89)

    def test_04(self):
        """TestRepCodeFrom56.test_04__(): from56(0x00) -> 0"""
        self.assertEqual(RepCode.from56(0x00), 0)

    def test_04_c(self):
        """TestRepCodeFrom56.test_04_p(): from56(0x00) -> 0 Cython."""
        self.assertEqual(cRepCode.from56(0x00), 0)

    def test_04_p(self):
        """TestRepCodeFrom56.test_04_p(): from56(0x00) -> 0 Python."""
        self.assertEqual(pRepCode.from56(0x00), 0)

    def test_11(self):
        """TestRepCodeFrom56.test_11(): read56(0x59) -> 89"""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 1) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x59' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(pRepCode.read56(myFile), 89)
        self.assertFalse(myFile.hasLd())

    def test_12(self):
        """TestRepCodeFrom56.test_12(): read56(0xA7) -> -89"""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 1) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\xa7' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(pRepCode.read56(myFile), -89)
        self.assertFalse(myFile.hasLd())


@pytest.mark.slow
class TestRepCodeFrom56Time(BaseTestClasses.TestRepCodeBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom56.test_00(): tests setUp() and tearDown()."""
        pass

    def test_time_00(self):
        """TestRepCodeFrom56.test_time_00(): tests conversion of 1e6 of same word - Cython code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from56(89)#0x99)
            i += 1
        self.writeTimeToStdErr(tS, 56, num)
        
    def test_time_01(self):
        """TestRepCodeFrom56.test_time_01(): tests conversion of 1e6 of same word - Python code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            pRepCode.from56(89)#0x99)
            i += 1
        self.writeTimeToStdErr(tS, 56, num)
        
    def test_time_02(self):
        """TestRepCodeFrom56.test_time_00(): tests conversion of 1e6 of same word - Cython time c.f. Python: """
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from56(89)#0x99)
            i += 1
        tE_C = time.perf_counter() - tS
        #print 'C time: %.3f rate %8.0f words/S' % (tE_C, num/tE_C)
        i = 0
        tS = time.perf_counter()
        while i < num:
            pRepCode.from56(0x0099)
            i += 1
        tE_P = time.perf_counter() - tS
        #print 'Python time: %.3f rate %8.0f words/S' % (tE_P, num/tE_P)
        #print('Cython: %.3f% ' % tE_C)
        #print('Python: %.3f% ' % tE_P)
        print('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))
        
    def test_time_10(self):
        """TestRepCodeFrom56.test_time_10(): tests conversion of 1e5 random words - Cython code."""
        i = 0
        num = 1e5
        myMin, myMax = RepCode.minMaxValue(56)
        tS = time.perf_counter()
        while i < num:
            cRepCode.from56(self.randInt(myMin, myMax))
            i += 1
        self.writeTimeToStdErr(tS, 56, num)
        
    def test_time_11(self):
        """TestRepCodeFrom56.test_time_11(): tests conversion of 1e5 random words - Python code."""
        i = 0
        num = 1e5
        myMin, myMax = RepCode.minMaxValue(56)
        tS = time.perf_counter()
        while i < num:
            pRepCode.from56(self.randInt(myMin, myMax))
            i += 1
        self.writeTimeToStdErr(tS, 56, num)

    def test_time_20(self):
        """TestRepCodeFrom56.test_time_20(): 2e5 word conversion from FileRead: """
        i = 0
        numWords = 2e5
        myWord = b'\x59'
        wordsInPr = int((PhysRec.PR_MAX_LENGTH - PhysRec.PR_PRH_LENGTH)/ len(myWord))
        # Suc no Pre: 1
        # Pre no Suc: 2
        # Suc and Pre: 3
        prContStart = \
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        prContBody = \
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(3) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        prContEnd = \
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(2) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        # How many physical records
        numPr = int(numWords/wordsInPr)
        numPrBody = numPr - 2
        assert(numPrBody >= 0)
#        print('\nlen={:d} wordsInPr={:d} numPr={:d} numPrBody={:d} loops={:d}'.format(
#                    len(myWord),
#                    wordsInPr,
#                    numPr,
#                    numPrBody,
#                    wordsInPr * numPr,
#                )
#        )
        # Python code first
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            pRepCode.read56(myFile)
            i += 1
        tE_P = time.perf_counter() - tS
        self.assertFalse(myFile.hasLd())
        print('Python: %.3f %8.0f words/S ' % (tE_P, numWords/tE_P))
        # Now Cython code
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            RepCode.read56(myFile)
            i += 1
        tE_C = time.perf_counter() - tS
        self.assertFalse(myFile.hasLd())
        print('Cython: %.3f %8.0f words/S ' % (tE_C, numWords/tE_C))
        print('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))

class TestRepCodeFrom66(BaseTestClasses.TestRepCodeBase):
    """Tests repCode 66"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom66.test_00(): tests setUp() and tearDown()."""
        pass

    def test_size(self):
        """TestRepCodeFrom66.test_size(): word length of 2."""
        self.assertEqual(RepCode.lisSize(66), 1)

    def test_minmax(self):
        """TestRepCodeFrom66.test_minmax(): min/max."""
        print(str(RepCode.minMaxValue(66)))
        print(' ')
        self.assertEqual(RepCode.minMaxValue(66), (0, 255))

    def test_min(self):
        """TestRepCodeFrom66.test_min(): min by bit stuffing."""
        myWord = 0x00
        self.assertEqual(RepCode.from66(myWord), RepCode.minValue(66))
        self.assertEqual(pRepCode.from66(myWord), RepCode.minValue(66))

    def test_max(self):
        """TestRepCodeFrom66.test_max(): max by bit stuffing."""
        myWord = 0xFF
        self.assertEqual(RepCode.from66(myWord), RepCode.maxValue(66))
        self.assertEqual(pRepCode.from66(myWord), RepCode.maxValue(66))

    def test_01(self):
        """TestRepCodeFrom66.test_01__(): from66(0x99) -> 153"""
        self.assertEqual(RepCode.from66(0x99), 153)

    def test_01_p(self):
        """TestRepCodeFrom66.test_01_p(): from66(0x99) -> 153 Python."""
        self.assertEqual(pRepCode.from66(0x99), 153)

    def test_04(self):
        """TestRepCodeFrom66.test_04__(): from66(0x00) -> 0"""
        self.assertEqual(RepCode.from66(0x00), 0)

    def test_04_p(self):
        """TestRepCodeFrom66.test_04_p(): from66(0x00) -> 0 Python."""
        self.assertEqual(pRepCode.from66(0x00), 0)

    def test_11(self):
        """TestRepCodeFrom66.test_11(): read66(0x99) -> 153"""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 1) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x99' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(pRepCode.read66(myFile), 153)
        self.assertFalse(myFile.hasLd())


@pytest.mark.slow
class TestRepCodeFrom66Time(BaseTestClasses.TestRepCodeBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom66.test_00(): tests setUp() and tearDown()."""
        pass

    def test_time_00(self):
        """TestRepCodeFrom66.test_time_00(): tests conversion of 1e6 of same word - Cython code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from66(0x99)
            i += 1
        self.writeTimeToStdErr(tS, 66, num)
        
    def test_time_01(self):
        """TestRepCodeFrom66.test_time_01(): tests conversion of 1e6 of same word - Python code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            pRepCode.from66(0x99)
            i += 1
        self.writeTimeToStdErr(tS, 66, num)
        
    def test_time_02(self):
        """TestRepCodeFrom66.test_time_00(): tests conversion of 1e6 of same word - Cython time c.f. Python: """
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from66(0x99)
            i += 1
        tE_C = time.perf_counter() - tS
        #print 'C time: %.3f rate %8.0f words/S' % (tE_C, num/tE_C)
        i = 0
        tS = time.perf_counter()
        while i < num:
            pRepCode.from66(0x99)
            i += 1
        tE_P = time.perf_counter() - tS
        #print 'Python time: %.3f rate %8.0f words/S' % (tE_P, num/tE_P)
        #print('Cython: %.3f% ' % tE_C)
        #print('Python: %.3f% ' % tE_P)
        print('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))
        
    def test_time_10(self):
        """TestRepCodeFrom66.test_time_10(): tests conversion of 1e5 random words - Cython code."""
        i = 0
        num = 1e5
        myMin, myMax = RepCode.minMaxValue(66)
        tS = time.perf_counter()
        while i < num:
            cRepCode.from66(self.randInt(myMin, myMax))
            i += 1
        self.writeTimeToStdErr(tS, 66, num)
        
    def test_time_11(self):
        """TestRepCodeFrom66.test_time_11(): tests conversion of 1e5 random words - Python code."""
        i = 0
        num = 1e5
        myMin, myMax = RepCode.minMaxValue(66)
        tS = time.perf_counter()
        while i < num:
            pRepCode.from66(self.randInt(myMin, myMax))
            i += 1
        self.writeTimeToStdErr(tS, 66, num)

    def test_time_20(self):
        """TestRepCodeFrom66.test_time_20(): 4e5 word conversion from FileRead: """
        i = 0
        numWords = 4e5
        myWord = b'\x99'
        wordsInPr = int((PhysRec.PR_MAX_LENGTH - PhysRec.PR_PRH_LENGTH)/ len(myWord))
        # Suc no Pre: 1
        # Pre no Suc: 2
        # Suc and Pre: 3
        prContStart = \
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        prContBody = \
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(3) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        prContEnd = \
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(2) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        # How many physical records
        numPr = int(numWords/wordsInPr)
        numPrBody = numPr - 2
        assert(numPrBody >= 0)
#        print('\nlen={:d} wordsInPr={:d} numPr={:d} numPrBody={:d} loops={:d}'.format(
#                    len(myWord),
#                    wordsInPr,
#                    numPr,
#                    numPrBody,
#                    wordsInPr * numPr,
#                )
#        )
        # Python code first
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            pRepCode.read66(myFile)
            i += 1
        tE_P = time.perf_counter() - tS
#        print('\ni =', i)
#        i = 0
#        while myFile.hasLd():
#            pRepCode.read66(myFile)
#            i += 1
#        print('i increment =', i)
        self.assertFalse(myFile.hasLd())
        print('Python: %.3f %8.0f words/S ' % (tE_P, numWords/tE_P))
        # Now Cython code
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            RepCode.read66(myFile)
            i += 1
        tE_C = time.perf_counter() - tS
        self.assertFalse(myFile.hasLd())
        print('Cython: %.3f %8.0f words/S ' % (tE_C, numWords/tE_C))
        print('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))

class TestRepCodeFrom70(BaseTestClasses.TestRepCodeBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom70.test_00(): tests setUp() and tearDown()."""
        pass

    def test_size(self):
        """TestRepCodeFrom70.test_size(): word length of 4."""
        self.assertEqual(RepCode.lisSize(70), 4)

    def test_minmax(self):
        """TestRepCodeFrom70.test_minmax(): min/max."""
        #print
        #print RepCode.minMaxValue(70)
        print(str(RepCode.minMaxValue(70)))
        print(' ')
        self.assertEqual(
            RepCode.minMaxValue(70),
            (-32768.0, 32767.99998474121)
        )

    def test_min(self):
        """TestRepCodeFrom70.test_min(): min by bit stuffing."""
        # 0 exponent
        myWord = 0x80000000
        #print 
        #print RepCode.from70(myWord)
        self.assertEqual(RepCode.from70(myWord), RepCode.minValue(70))
        self.assertEqual(pRepCode.from70(myWord), RepCode.minValue(70))
        self.assertEqual(cRepCode.from70(myWord), RepCode.minValue(70))

    def test_max(self):
        """TestRepCodeFrom70.test_max(): max by bit stuffing."""
        myWord = 0x7FFFFFFF
        self.assertEqual(RepCode.from70(myWord), RepCode.maxValue(70))
        self.assertEqual(cRepCode.from70(myWord), RepCode.maxValue(70))
        self.assertEqual(pRepCode.from70(myWord), RepCode.maxValue(70))

    def test_01(self):
        """TestRepCodeFrom70.test_01__(): from70(0x00994000) -> 153.25"""
        self.assertEqual(RepCode.from70(0x00994000), 153.25)

    def test_01_c(self):
        """TestRepCodeFrom70.test_01_c(): from70(0x00994000) -> 153.25 Cython."""
        self.assertEqual(cRepCode.from70(0x00994000), 153.25)

    def test_01_p(self):
        """TestRepCodeFrom70.test_01_p(): from70(0x00994000) -> 153.25 Python."""
        self.assertEqual(pRepCode.from70(0x00994000), 153.25)

    def test_02(self):
        """TestRepCodeFrom70.test_02__(): from70(0xFF66C000) -> -153.25"""
        self.assertEqual(RepCode.from70(0xFF66C000), -153.25)

    def test_02_c(self):
        """TestRepCodeFrom70.test_02_c(): from70(0xFF66C000) -> -153.25 Cython."""
        self.assertEqual(cRepCode.from70(0xFF66C000), -153.25)

    def test_02_p(self):
        """TestRepCodeFrom70.test_02_p(): from70(0xFF66C000) -> -153.25 Python."""
        self.assertEqual(pRepCode.from70(0xFF66C000), -153.25)
        

    def test_04(self):
        """TestRepCodeFrom70.test_04__(): from70(0x00000000) -> 0.0."""
        self.assertEqual(RepCode.from70(0x00000000), 0.0)

    def test_04_c(self):
        """TestRepCodeFrom70.test_04_c(): from70(0x40000000) -> 0.0 Cython."""
        self.assertEqual(cRepCode.from70(0x00000000), 0.0)

    def test_04_p(self):
        """TestRepCodeFrom70.test_04_p(): from70(0x00000000) -> 0.0 Python."""
        self.assertEqual(pRepCode.from70(0x00000000), 0.0)

    def test_11(self):
        """TestRepCodeFrom70.test_11(): read70(0x00994000) -> 153.25"""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 4) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x00\x99\x40\x00' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(pRepCode.read70(myFile), 153.25)
        self.assertFalse(myFile.hasLd())

    def test_12(self):
        """TestRepCodeFrom70.test_12(): read70(0xFF66C000) -> -153.25"""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 4) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\xff\x66\xc0\x00' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(pRepCode.read70(myFile), -153.25)
        self.assertFalse(myFile.hasLd())


@pytest.mark.slow
class TestRepCodeFrom70Time(BaseTestClasses.TestRepCodeBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom70.test_00(): tests setUp() and tearDown()."""
        pass

    def test_time_00(self):
        """TestRepCodeFrom70.test_time_00(): tests conversion of 1e6 of same word - Cython code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from70(0xBBB38000)
            i += 1
        self.writeTimeToStdErr(tS, 70, num)
        
    def test_time_01(self):
        """TestRepCodeFrom70.test_time_01(): tests conversion of 1e6 of same word - Python code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            pRepCode.from70(0xBBB38000)
            i += 1
        self.writeTimeToStdErr(tS, 70, num)
        
    def test_time_02(self):
        """TestRepCodeFrom70.test_time_00(): tests conversion of 1e6 of same word - Cython time c.f. Python: """
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from70(0xBBB38000)
            i += 1
        tE_C = time.perf_counter() - tS
        #print 'C time: %.3f rate %8.0f words/S' % (tE_C, num/tE_C)
        i = 0
        tS = time.perf_counter()
        while i < num:
            pRepCode.from70(0xBBB38000)
            i += 1
        tE_P = time.perf_counter() - tS
        #print 'Python time: %.3f rate %8.0f words/S' % (tE_P, num/tE_P)
        #print('Cython: %.3f% ' % tE_C)
        #print('Python: %.3f% ' % tE_P)
        print('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))
        
    def test_time_10(self):
        """TestRepCodeFrom70.test_time_10(): tests conversion of 1e5 random words - Cython code."""
        i = 0
        num = 1e5
        tS = time.perf_counter()
        while i < num:
            cRepCode.from70(self.randWord(1, 8, 23))
            i += 1
        self.writeTimeToStdErr(tS, 70, num)
        
    def test_time_11(self):
        """TestRepCodeFrom70.test_time_11(): tests conversion of 1e5 random words - Python code."""
        i = 0
        num = 1e5
        tS = time.perf_counter()
        while i < num:
            pRepCode.from70(self.randWord(1, 8, 23))
            i += 1
        self.writeTimeToStdErr(tS, 70, num)

    def test_time_20(self):
        """TestRepCodeFrom70.test_time_20(): 1e5 word conversion from FileRead: """
        i = 0
        numWords = 1e5
        myWord = b'\x44\x4c\x80\x00'
        wordsInPr = int((PhysRec.PR_MAX_LENGTH - PhysRec.PR_PRH_LENGTH)/ len(myWord))
        # Suc no Pre: 1
        # Pre no Suc: 2
        # Suc and Pre: 3
        prContStart = PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        prContBody = PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(3) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        prContEnd = PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(2) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        # How many physical records
        numPr = int(numWords/wordsInPr)
        numPrBody = numPr - 2
        assert(numPrBody >= 0)
        # Python code first
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            pRepCode.read70(myFile)
            i += 1
        tE_P = time.perf_counter() - tS
        self.assertFalse(myFile.hasLd())
        print('Python: %.3f %8.0f words/S ' % (tE_P, numWords/tE_P))
        # Now Cython code
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            RepCode.read70(myFile)
            i += 1
        tE_C = time.perf_counter() - tS
        self.assertFalse(myFile.hasLd())
        print('Cython: %.3f %8.0f words/S ' % (tE_C, numWords/tE_C))
        print('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))

class TestRepCodeFrom73(BaseTestClasses.TestRepCodeBase):
    """Tests repCode 73"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom73.test_00(): tests setUp() and tearDown()."""
        pass

    def test_size(self):
        """TestRepCodeFrom73.test_size(): word length of 4."""
        self.assertEqual(RepCode.lisSize(73), 4)

    def test_minmax(self):
        """TestRepCodeFrom73.test_minmax(): min/max."""
        print(str(RepCode.minMaxValue(73)))
        print(' ')
        self.assertEqual(
            RepCode.minMaxValue(73),
            (-2147483648, 2147483647)
        )

    def test_min(self):
        """TestRepCodeFrom73.test_min(): min by bit stuffing."""
        myWord = -0x80000000
        self.assertEqual(RepCode.from73(myWord), RepCode.minValue(73))
        self.assertEqual(pRepCode.from73(myWord), RepCode.minValue(73))

    def test_max(self):
        """TestRepCodeFrom73.test_max(): max by bit stuffing."""
        myWord = 0x7FFFFFFF
        self.assertEqual(RepCode.from73(myWord), RepCode.maxValue(73))
        self.assertEqual(pRepCode.from73(myWord), RepCode.maxValue(73))

    def test_01(self):
        """TestRepCodeFrom73.test_01__(): from73(0x00000099) -> 153"""
        self.assertEqual(RepCode.from73(0x00000099), 153)

    def test_01_p(self):
        """TestRepCodeFrom73.test_01_p(): from73(0x00000099) -> 153 Python."""
        self.assertEqual(pRepCode.from73(0x00000099), 153)

    def test_02(self):
        """TestRepCodeFrom73.test_02__(): from73(0xFFFFFF67) -> -153"""
        self.assertEqual(RepCode.from73(-153), -153)

    def test_02_p(self):
        """TestRepCodeFrom73.test_02_p(): from73(0xFFFFFF67) -> -153 Python."""
        self.assertEqual(pRepCode.from73(-153), -153)

    def test_04(self):
        """TestRepCodeFrom73.test_04__(): from73(0x00000000) -> 0"""
        self.assertEqual(RepCode.from73(0x00000000), 0)

    def test_04_p(self):
        """TestRepCodeFrom73.test_04_p(): from73(0x00000000) -> 0 Python."""
        self.assertEqual(pRepCode.from73(0x00000000), 0)

    def test_11(self):
        """TestRepCodeFrom73.test_11(): read73(0x00000099) -> 153"""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 4) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x00\x00\x00\x99' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(pRepCode.read73(myFile), 153)
        self.assertFalse(myFile.hasLd())

    def test_12(self):
        """TestRepCodeFrom73.test_12(): read73(0xFFFFFF67) -> -153"""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 4) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\xff\xff\xff\x67' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(pRepCode.read73(myFile), -153)
        self.assertFalse(myFile.hasLd())


@pytest.mark.slow
class TestRepCodeFrom73Time(BaseTestClasses.TestRepCodeBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom73.test_00(): tests setUp() and tearDown()."""
        pass

    def test_time_00(self):
        """TestRepCodeFrom73.test_time_00(): tests conversion of 1e6 of same word - Cython code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from73(0x00000099)
            i += 1
        self.writeTimeToStdErr(tS, 73, num)
        
    def test_time_01(self):
        """TestRepCodeFrom73.test_time_01(): tests conversion of 1e6 of same word - Python code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            pRepCode.from73(0x00000099)
            i += 1
        self.writeTimeToStdErr(tS, 73, num)
        
    def test_time_02(self):
        """TestRepCodeFrom73.test_time_00(): tests conversion of 1e6 of same word - Cython time c.f. Python: """
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from73(0x00000099)
            i += 1
        tE_C = time.perf_counter() - tS
        #print 'C time: %.3f rate %8.0f words/S' % (tE_C, num/tE_C)
        i = 0
        tS = time.perf_counter()
        while i < num:
            pRepCode.from73(0x00000099)
            i += 1
        tE_P = time.perf_counter() - tS
        #print 'Python time: %.3f rate %8.0f words/S' % (tE_P, num/tE_P)
        #print('Cython: %.3f% ' % tE_C)
        #print('Python: %.3f% ' % tE_P)
        print('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))
        
    def test_time_10(self):
        """TestRepCodeFrom73.test_time_10(): tests conversion of 1e5 random words - Cython code."""
        i = 0
        num = 1e5
        myMin, myMax = RepCode.minMaxValue(73)
        tS = time.perf_counter()
        while i < num:
            cRepCode.from73(self.randInt(myMin, myMax))
            i += 1
        self.writeTimeToStdErr(tS, 73, num)
        
    def test_time_11(self):
        """TestRepCodeFrom73.test_time_11(): tests conversion of 1e5 random words - Python code."""
        i = 0
        num = 1e5
        myMin, myMax = RepCode.minMaxValue(73)
        tS = time.perf_counter()
        while i < num:
            pRepCode.from73(self.randInt(myMin, myMax))
            i += 1
        self.writeTimeToStdErr(tS, 73, num)

    def test_time_20(self):
        """TestRepCodeFrom73.test_time_20(): 1e5 word conversion from FileRead: """
        i = 0
        numWords = 1e5
        myWord = b'\x00\x00\x00\x99'
        wordsInPr = int((PhysRec.PR_MAX_LENGTH - PhysRec.PR_PRH_LENGTH)/ len(myWord))
        # Suc no Pre: 1
        # Pre no Suc: 2
        # Suc and Pre: 3
        prContStart = PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        prContBody = PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(3) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        prContEnd = PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(2) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        # How many physical records
        numPr = int(numWords/wordsInPr)
        numPrBody = numPr - 2
        assert(numPrBody >= 0)
        # Python code first
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            pRepCode.read73(myFile)
            i += 1
        tE_P = time.perf_counter() - tS
        self.assertFalse(myFile.hasLd())
        print('Python: %.3f %8.0f words/S ' % (tE_P, numWords/tE_P))
        # Now Cython code
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            RepCode.read73(myFile)
            i += 1
        tE_C = time.perf_counter() - tS
        self.assertFalse(myFile.hasLd())
        print('Cython: %.3f %8.0f words/S ' % (tE_C, numWords/tE_C))
        print('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))

class TestRepCodeFrom77(BaseTestClasses.TestRepCodeBase):
    """Tests repCode 77"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom77.test_00(): tests setUp() and tearDown()."""
        pass

    def test_size(self):
        """TestRepCodeFrom77.test_size(): word length of 2."""
        self.assertEqual(RepCode.lisSize(77), 1)

    def test_minmax(self):
        """TestRepCodeFrom77.test_minmax(): min/max."""
        print(str(RepCode.minMaxValue(77)))
        print(' ')
        self.assertEqual(RepCode.minMaxValue(77), (0, 255))

    def test_min(self):
        """TestRepCodeFrom77.test_min(): min by bit stuffing."""
        myWord = 0x00
        self.assertEqual(RepCode.from77(myWord), RepCode.minValue(77))
        self.assertEqual(pRepCode.from77(myWord), RepCode.minValue(77))

    def test_max(self):
        """TestRepCodeFrom77.test_max(): max by bit stuffing."""
        myWord = 0xFF
        self.assertEqual(RepCode.from77(myWord), RepCode.maxValue(77))
        self.assertEqual(pRepCode.from77(myWord), RepCode.maxValue(77))

    def test_01(self):
        """TestRepCodeFrom77.test_01__(): from77(0x99) -> 153"""
        self.assertEqual(RepCode.from77(0x99), 153)

    def test_01_p(self):
        """TestRepCodeFrom77.test_01_p(): from77(0x99) -> 153 Python."""
        self.assertEqual(pRepCode.from77(0x99), 153)

    def test_04(self):
        """TestRepCodeFrom77.test_04__(): from77(0x00) -> 0"""
        self.assertEqual(RepCode.from77(0x00), 0)

    def test_04_p(self):
        """TestRepCodeFrom77.test_04_p(): from77(0x00) -> 0 Python."""
        self.assertEqual(pRepCode.from77(0x00), 0)

    def test_11(self):
        """TestRepCodeFrom77.test_11(): read77(0x99) -> 153"""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 1) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x99' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(pRepCode.read77(myFile), 153)
        self.assertFalse(myFile.hasLd())


@pytest.mark.slow
class TestRepCodeFrom77Time(BaseTestClasses.TestRepCodeBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom77.test_00(): tests setUp() and tearDown()."""
        pass

    def test_time_00(self):
        """TestRepCodeFrom77.test_time_00(): tests conversion of 1e6 of same word - Cython code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from77(0x99)
            i += 1
        self.writeTimeToStdErr(tS, 77, num)
        
    def test_time_01(self):
        """TestRepCodeFrom77.test_time_01(): tests conversion of 1e6 of same word - Python code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            pRepCode.from77(0x99)
            i += 1
        self.writeTimeToStdErr(tS, 77, num)
        
    def test_time_02(self):
        """TestRepCodeFrom77.test_time_00(): tests conversion of 1e6 of same word - Cython time c.f. Python: """
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from77(0x99)
            i += 1
        tE_C = time.perf_counter() - tS
        #print 'C time: %.3f rate %8.0f words/S' % (tE_C, num/tE_C)
        i = 0
        tS = time.perf_counter()
        while i < num:
            pRepCode.from77(0x99)
            i += 1
        tE_P = time.perf_counter() - tS
        #print 'Python time: %.3f rate %8.0f words/S' % (tE_P, num/tE_P)
        #print('Cython: %.3f% ' % tE_C)
        #print('Python: %.3f% ' % tE_P)
        print('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))
        
    def test_time_10(self):
        """TestRepCodeFrom77.test_time_10(): tests conversion of 1e5 random words - Cython code."""
        i = 0
        num = 1e5
        myMin, myMax = RepCode.minMaxValue(77)
        tS = time.perf_counter()
        while i < num:
            cRepCode.from77(self.randInt(myMin, myMax))
            i += 1
        self.writeTimeToStdErr(tS, 77, num)
        
    def test_time_11(self):
        """TestRepCodeFrom77.test_time_11(): tests conversion of 1e5 random words - Python code."""
        i = 0
        num = 1e5
        myMin, myMax = RepCode.minMaxValue(77)
        tS = time.perf_counter()
        while i < num:
            pRepCode.from77(self.randInt(myMin, myMax))
            i += 1
        self.writeTimeToStdErr(tS, 77, num)

    def test_time_20(self):
        """TestRepCodeFrom77.test_time_20(): 4e5 word conversion from FileRead: """
        i = 0
        numWords = 4e5
        myWord = b'\x99'
        wordsInPr = int((PhysRec.PR_MAX_LENGTH - PhysRec.PR_PRH_LENGTH)/ len(myWord))
        # Suc no Pre: 1
        # Pre no Suc: 2
        # Suc and Pre: 3
        prContStart = \
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        prContBody = \
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(3) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        prContEnd = \
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(2) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        # How many physical records
        numPr = int(numWords/wordsInPr)
        numPrBody = numPr - 2
        assert(numPrBody >= 0)
#        print('\nlen={:d} wordsInPr={:d} numPr={:d} numPrBody={:d} loops={:d}'.format(
#                    len(myWord),
#                    wordsInPr,
#                    numPr,
#                    numPrBody,
#                    wordsInPr * numPr,
#                )
#        )
        # Python code first
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            pRepCode.read77(myFile)
            i += 1
        tE_P = time.perf_counter() - tS
#        print('\ni =', i)
#        i = 0
#        while myFile.hasLd():
#            pRepCode.read77(myFile)
#            i += 1
#        print('i increment =', i)
        self.assertFalse(myFile.hasLd())
        print('Python: %.3f %8.0f words/S ' % (tE_P, numWords/tE_P))
        # Now Cython code
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            RepCode.read77(myFile)
            i += 1
        tE_C = time.perf_counter() - tS
        self.assertFalse(myFile.hasLd())
        print('Cython: %.3f %8.0f words/S ' % (tE_C, numWords/tE_C))
        print('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))

class TestRepCodeFrom79(BaseTestClasses.TestRepCodeBase):
    """Tests repCode 79"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom79.test_00(): tests setUp() and tearDown()."""
        pass

    def test_size(self):
        """TestRepCodeFrom79.test_size(): word length of 2."""
        self.assertEqual(RepCode.lisSize(79), 2)

    def test_minmax(self):
        """TestRepCodeFrom79.test_minmax(): min/max."""
        print(str(RepCode.minMaxValue(79)))
        print(' ')
        self.assertEqual(RepCode.minMaxValue(79), (-32768, 32767))

    def test_min(self):
        """TestRepCodeFrom79.test_min(): min by bit stuffing."""
        myWord = -0x8000
        self.assertEqual(RepCode.from79(myWord), RepCode.minValue(79))
        self.assertEqual(pRepCode.from79(myWord), RepCode.minValue(79))

    def test_max(self):
        """TestRepCodeFrom79.test_max(): max by bit stuffing."""
        myWord = 0x7FFF
        self.assertEqual(RepCode.from79(myWord), RepCode.maxValue(79))
        self.assertEqual(pRepCode.from79(myWord), RepCode.maxValue(79))

    def test_01(self):
        """TestRepCodeFrom79.test_01__(): from79(0x0099) -> 153"""
        self.assertEqual(RepCode.from79(0x0099), 153)

    def test_01_c(self):
        """TestRepCodeFrom79.test_01_c(): from79(0x0099) -> 153 Python."""
        self.assertEqual(cRepCode.from79(0x0099), 153)

    def test_01_p(self):
        """TestRepCodeFrom79.test_01_p(): from79(0x0099) -> 153 Python."""
        self.assertEqual(pRepCode.from79(0x0099), 153)

    def test_02(self):
        """TestRepCodeFrom79.test_02__(): from79(0xFF67) -> -153"""
        self.assertEqual(RepCode.from79(-153), -153)

    def test_02_c(self):
        """TestRepCodeFrom79.test_02_c(): from79(0xFF67) -> -153 Cython."""
        self.assertEqual(cRepCode.from79(-153), -153)

    def test_02_p(self):
        """TestRepCodeFrom79.test_02_p(): from79(0xFF67) -> -153 Python."""
        self.assertEqual(pRepCode.from79(-153), -153)

    def test_04(self):
        """TestRepCodeFrom79.test_04__(): from79(0x0000) -> 0"""
        self.assertEqual(RepCode.from79(0x0000), 0)

    def test_04_c(self):
        """TestRepCodeFrom79.test_04_c(): from79(0x0000) -> 0 Cython."""
        self.assertEqual(cRepCode.from79(0x0000), 0)

    def test_04_p(self):
        """TestRepCodeFrom79.test_04_p(): from79(0x0000) -> 0 Python."""
        self.assertEqual(pRepCode.from79(0x0000), 0)

    def test_11(self):
        """TestRepCodeFrom79.test_11(): read79(0x0099) -> 153"""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 2) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x00\x99' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(pRepCode.read79(myFile), 153)
        self.assertFalse(myFile.hasLd())

    def test_12(self):
        """TestRepCodeFrom79.test_12(): read79(0xFF67) -> -153"""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 2) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\xff\x67' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(pRepCode.read79(myFile), -153)
        self.assertFalse(myFile.hasLd())


@pytest.mark.slow
class TestRepCodeFrom79Time(BaseTestClasses.TestRepCodeBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom79.test_00(): tests setUp() and tearDown()."""
        pass

    def test_time_00(self):
        """TestRepCodeFrom79.test_time_00(): tests conversion of 1e6 of same word - Cython code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from79(0x0099)
            i += 1
        self.writeTimeToStdErr(tS, 79, num)
        
    def test_time_01(self):
        """TestRepCodeFrom79.test_time_01(): tests conversion of 1e6 of same word - Python code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            pRepCode.from79(0x0099)
            i += 1
        self.writeTimeToStdErr(tS, 79, num)
        
    def test_time_02(self):
        """TestRepCodeFrom79.test_time_00(): tests conversion of 1e6 of same word - Cython time c.f. Python: """
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from79(0x0099)
            i += 1
        tE_C = time.perf_counter() - tS
        #print 'C time: %.3f rate %8.0f words/S' % (tE_C, num/tE_C)
        i = 0
        tS = time.perf_counter()
        while i < num:
            pRepCode.from79(0x0099)
            i += 1
        tE_P = time.perf_counter() - tS
        #print 'Python time: %.3f rate %8.0f words/S' % (tE_P, num/tE_P)
        #print('Cython: %.3f% ' % tE_C)
        #print('Python: %.3f% ' % tE_P)
        print('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))
        
    def test_time_10(self):
        """TestRepCodeFrom79.test_time_10(): tests conversion of 1e5 random words - Cython code."""
        i = 0
        num = 1e5
        myMin, myMax = RepCode.minMaxValue(79)
        tS = time.perf_counter()
        while i < num:
            cRepCode.from79(self.randInt(myMin, myMax))
            i += 1
        self.writeTimeToStdErr(tS, 79, num)
        
    def test_time_11(self):
        """TestRepCodeFrom79.test_time_11(): tests conversion of 1e5 random words - Python code."""
        i = 0
        num = 1e5
        myMin, myMax = RepCode.minMaxValue(79)
        tS = time.perf_counter()
        while i < num:
            pRepCode.from79(self.randInt(myMin, myMax))
            i += 1
        self.writeTimeToStdErr(tS, 79, num)

    def test_time_20(self):
        """TestRepCodeFrom79.test_time_20(): 1e5 word conversion from FileRead: """
        i = 0
        numWords = 1e5
        myWord = b'\x00\x99'
        wordsInPr = int((PhysRec.PR_MAX_LENGTH - PhysRec.PR_PRH_LENGTH)/ len(myWord))
        # Suc no Pre: 1
        # Pre no Suc: 2
        # Suc and Pre: 3
        prContStart = \
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(1) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        prContBody = \
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(3) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        prContEnd = \
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myWord)*wordsInPr) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(2) \
            + (myWord * wordsInPr)
            # Absent Physical Record trailer
        # How many physical records
        numPr = int(numWords/wordsInPr)
        numPrBody = numPr - 2
        assert(numPrBody >= 0)
#        print('\nlen={:d} wordsInPr={:d} numPr={:d} numPrBody={:d} loops={:d}'.format(
#                    len(myWord),
#                    wordsInPr,
#                    numPr,
#                    numPrBody,
#                    wordsInPr * numPr,
#                )
#        )
        # Python code first
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            pRepCode.read79(myFile)
            i += 1
        tE_P = time.perf_counter() - tS
#        print('\ni =', i)
#        i = 0
#        while myFile.hasLd():
#            pRepCode.read79(myFile)
#            i += 1
#        print('i increment =', i)
        self.assertFalse(myFile.hasLd())
        print('Python: %.3f %8.0f words/S ' % (tE_P, numWords/tE_P))
        # Now Cython code
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            RepCode.read79(myFile)
            i += 1
        tE_C = time.perf_counter() - tS
        self.assertFalse(myFile.hasLd())
        print('Cython: %.3f %8.0f words/S ' % (tE_C, numWords/tE_C))
        print('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))

class TestRepCodeIndirect(BaseTestClasses.TestRepCodeBase):
    """Tests indirect repcode functionality."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeIndirect.test_00(): tests setUp() and tearDown()."""
        pass

    def test_from_00(self):
        """TestRepCodeIndirect.test_from_00(): fromRepCode()"""
        self.assertEqual(RepCode.fromRepCode(49, 0x4C88),       153.0)
        self.assertEqual(RepCode.fromRepCode(50, 0x00084C80),   153.0)
        self.assertEqual(RepCode.fromRepCode(56, 0x59),         89)
        self.assertEqual(RepCode.fromRepCode(66, 0x99),         153)
        self.assertEqual(RepCode.fromRepCode(70, 0x00994000),   153.25)
        self.assertEqual(RepCode.fromRepCode(73, 0x00000099),   153)
        self.assertEqual(RepCode.fromRepCode(77, 0x99),         153)
        self.assertEqual(RepCode.fromRepCode(79, 0x0099), 153)
        
    def test_from_01(self):
        """TestRepCodeIndirect.test_from_00(): fromRepCode() fails"""
        self.assertRaises(RepCode.ExceptionRepCodeUnknown, RepCode.fromRepCode, 0, 0x4C88)

    def test_read_00(self):
        """TestRepCodeIndirect.test_read_00(): fromRepCode()"""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 2) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x00\x99' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(RepCode.readRepCode(79, myFile), 153)
        self.assertFalse(myFile.hasLd())

    def test_read_01(self):
        """TestRepCodeIndirect.test_read_00(): fromRepCode() fails."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 2) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x00\x99' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertRaises(RepCode.ExceptionRepCodeUnknown, RepCode.readRepCode, 0, myFile)

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    # Type 49
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom49))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom49Time))
    # Type 50
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom50))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom50Time))
    # Type 56
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom56))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom56Time))
    # Type 66
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom66))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom66Time))
    # Type 68 is in its own test module
    # Type 70
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom70))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom70Time))
    # Type 73
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom73))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom73Time))
    # Type 77
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom77))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom77Time))
    # Type 79
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom79))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom79Time))
    # Misc. tests
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeIndirect))
    #
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Test the RepCode module."""
    print("""TestRepCode.py - A module that tests the RepCode module.
Usage:
python TestRepCode.py [-lh --help]

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
