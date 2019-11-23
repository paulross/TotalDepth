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
## CPython methods
from TotalDepth.LIS.core import cpRepCode
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
#        sys.stderr.write('Time: {:.3f} Rate {:8.0f} words/S '.format(tE, numWords/tE))
#        sys.stderr.write(' Cost: {:.3f} (ms/MB)'.format((tE*1024)/(siz/(1024*1024))))
#    
class TestRepCode68Base(BaseTestClasses.TestRepCodeBase):
    """Rep Code 68 specific stuff."""
    
    def splitBits68(self, i):
        """Given an integer this returns the bits as a tuple of three strings: sign, exponent, mantissa."""
        b = '{:032b}'.format(i)
        return b[:1], b[1:9], b[9:]

class TestRepCodeFrom68Basic(TestRepCode68Base):
    """Tests basic Rep Code functionality."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom68.test_00(): tests setUp() and tearDown()."""
        pass

    def test_size(self):
        """TestRepCodeFrom68.test_size(): word length of 4."""
        self.assertEqual(RepCode.lisSize(68), 4)

    def test_minmax(self):
        """TestRepCodeFrom68.test_minmax(): min/max."""
        #print
        #print RepCode.minMaxValue(68)
        sys.stderr.write(str(RepCode.minMaxValue(68)))
        sys.stderr.write(' ')
        self.assertEqual(
            RepCode.minMaxValue(68),
            (
                -1.7014118346046923e+38,
                +1.7014116317805963e+38,
            )
        )

    def test_min(self):
        """TestRepCodeFrom68.test_min(): min by bit stuffing."""
        myWord = 1
        myWord <<= 8
        myWord |= 1
        myWord <<=23
        # 0 exponent
        myWord = 0x80000000
        #print 
        #print RepCode.from68(myWord)
        self.assertEqual(RepCode.from68(myWord), RepCode.minValue(68))
        self.assertEqual(pRepCode.from68(myWord), RepCode.minValue(68))
        self.assertEqual(cRepCode.from68(myWord), RepCode.minValue(68))

    def test_max(self):
        """TestRepCodeFrom68.test_max(): max by bit stuffing."""
        myWord = 0x7FFFFFFF
        f = RepCode.from68(myWord)
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
        self.assertEqual(RepCode.from68(myWord), RepCode.maxValue(68))
        self.assertEqual(cRepCode.from68(myWord), RepCode.maxValue(68))
        self.assertEqual(pRepCode.from68(myWord), RepCode.maxValue(68))

class TestRepCodeFrom68Python(TestRepCode68Base):
    """Tests reading Rep Code 68 using Python code."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom68Python.test_00(): tests setUp() and tearDown()."""
        pass

    def test_01_p(self):
        """TestRepCodeFrom68Python.test_01_p(): from68(0x444C8000) -> 153.0 Python."""
        self.assertEqual(pRepCode.from68(0x444C8000), 153.0)

    def test_02_p(self):
        """TestRepCodeFrom68Python.test_02_p(): from68(0xBBB38000) -> -153.0 Python."""
        self.assertEqual(pRepCode.from68(0xBBB38000), -153.0)        

    def test_04_p(self):
        """TestRepCodeFrom68Python.test_04_p(): from68(0x40000000) -> 0.0 Python."""
        self.assertEqual(pRepCode.from68(0x40000000), 0.0)

    def test_11_p(self):
        """TestRepCodeFrom68Python.test_11_p(): read68(0x444C8000) -> 153.0 Python."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 4) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x44\x4c\x80\x00' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(pRepCode.read68(myFile), 153.0)
        self.assertFalse(myFile.hasLd())

    def test_12_p(self):
        """TestRepCodeFrom68Python.test_12_c(): read68(0xBBB38000) -> -153.0 Python."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 4) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\xbb\xb3\x80\x00' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(pRepCode.read68(myFile), -153.0)
        self.assertFalse(myFile.hasLd())

class TestRepCodeFrom68Cython(TestRepCode68Base):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom68Cython.test_00(): tests setUp() and tearDown()."""
        pass

    def test_01_c(self):
        """TestRepCodeFrom68Cython.test_01_c(): from68(0x444C8000) -> 153.0 Cython."""
        self.assertEqual(cRepCode.from68(0x444C8000), 153.0)

    def test_02_c(self):
        """TestRepCodeFrom68Cython.test_02_c(): from68(0xBBB38000) -> -153.0 Cython."""
        self.assertEqual(cRepCode.from68(0xBBB38000), -153.0)

    def test_04_c(self):
        """TestRepCodeFrom68Cython.test_04_c(): from68(0x40000000) -> 0.0 Cython."""
        self.assertEqual(cRepCode.from68(0x40000000), 0.0)

    def test_11_c(self):
        """TestRepCodeFrom68Cython.test_11_c(): read68(0x444C8000) -> 153.0 Cython."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 4) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x44\x4c\x80\x00' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
#        self.assertEqual(cRepCode.read68(myFile), 153.0)
        try:
            assert(cRepCode.read68(myFile) == 153.0)
            self.fail('AttributeError not raised.')
        except AttributeError:
            pass
        self.assertFalse(myFile.hasLd())

    def test_12_c(self):
        """TestRepCodeFrom68Cython.test_12_c(): read68(0xBBB38000) -> -153.0 Cython."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 4) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\xbb\xb3\x80\x00' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
#        self.assertEqual(cRepCode.read68(myFile), -153.0)
        try:
            assert(cRepCode.read68(myFile) == -153.0)
            self.fail('AttributeError not raised.')
        except AttributeError:
            pass
        self.assertFalse(myFile.hasLd())

class TestRepCodeToFrom68CPython(TestRepCode68Base):
    """Tests representation code 68 converted by a CPython extension."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeToFrom68CPython.test_00(): tests setUp() and tearDown()."""
        pass

    # Equivalent to 0xFFC00000
    # RC_68_MIN = math.ldexp(-1.0, 127)
    # Equivalent to 0x7FFFFFFF
    # RC_68_MAX = math.ldexp(1 - 1.0 / (1 << 23), 127)

    def test_from_min(self):
        self.assertEqual(cpRepCode.from68(0x80700000), math.ldexp(-2.0, 123))

    def test_from_max(self):
        self.assertEqual(cpRepCode.from68(0x7FFFFFFF), math.ldexp(1 - 1.0 / (1 << 23), 127))

    def test_from_153(self):
        """TestRepCodeToFrom68CPython.test_01_c(): from68(0x444C8000) -> 153.0 CPython."""
        self.assertEqual(cpRepCode.from68(0x444C8000), 153.0)

    def test_from_minus_153(self):
        """TestRepCodeToFrom68CPython.test_02_c(): from68(0xBBB38000) -> -153.0 CPython."""
        self.assertEqual(cpRepCode.from68(0xBBB38000), -153.0)

    def test_from_zero(self):
        """TestRepCodeToFrom68CPython.test_04_c(): from68(0x40000000) -> 0.0 CPython."""
        self.assertEqual(cpRepCode.from68(0x40000000), 0.0)

    def test_to_153(self):
        """TestRepCodeToFrom68CPython.test_01_c(): to68(0x444C8000) -> 153.0 CPython."""
        self.assertEqual(cpRepCode.to68(153.0), 0x444C8000)

    def test_to_minus_153(self):
        """TestRepCodeToFrom68CPython.test_02_c(): to68(0xBBB38000) -> -153.0 CPython."""
        result = cpRepCode.to68(-153.0)
        self.assertEqual(result, 0xBBB38000)

    def test_to_zero(self):
        """TestRepCodeToFrom68CPython.test_04_c(): to68(0x40000000) -> 0.0 CPython."""
        self.assertEqual(cpRepCode.to68(0.0), 0x40000000)

    def test_to_153_int(self):
        """TestRepCodeToFrom68CPython.test_01_c(): to68(0x444C8000) -> 153.0 CPython."""
        self.assertEqual(cpRepCode.to68(153), 0x444C8000)

    def test_to_minus_153_int(self):
        """TestRepCodeToFrom68CPython.test_02_c(): to68(0xBBB38000) -> -153.0 CPython."""
        result = cpRepCode.to68(-153)
        self.assertEqual(result, 0xBBB38000)

    def test_to_zero_int(self):
        """TestRepCodeToFrom68CPython.test_04_c(): to68(0x40000000) -> 0.0 CPython."""
        self.assertEqual(cpRepCode.to68(0), 0x40000000)

class TestRepCodeFrom68(TestRepCode68Base):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom68.test_00(): tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestRepCodeFrom68.test_01(): from68(0x444C8000) -> 153.0."""
        self.assertEqual(RepCode.from68(0x444C8000), 153.0)

    def test_02(self):
        """TestRepCodeFrom68.test_02(): from68(0xBBB38000) -> -153.0."""
        self.assertEqual(RepCode.from68(0xBBB38000), -153.0)

    def test_04(self):
        """TestRepCodeFrom68.test_04(): from68(0x40000000) -> 0.0."""
        self.assertEqual(RepCode.from68(0x40000000), 0.0)

    def test_11__(self):
        """TestRepCodeFrom68.test_11__(): read68(0x444C8000) -> 153.0."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 4) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\x44\x4c\x80\x00' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(RepCode.read68(myFile), 153.0)
        self.assertFalse(myFile.hasLd())

    def test_12__(self):
        """TestRepCodeFrom68.test_12__(): read68(0xBBB38000) -> -153.0."""
        myBy = io.BytesIO(
            PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + 4) \
            + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
            + b'\xbb\xb3\x80\x00' \
            # Absent Physical Record trailer
        )
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)
        self.assertEqual(RepCode.read68(myFile), -153.0)
        self.assertFalse(myFile.hasLd())

    def test_30(self):
        """TestRepCodeFrom68.test_30(): from68(0x3fc00000) -> 0.25 (Defect found during FrameSet testing)."""
        self.assertEqual(RepCode.from68(0x40000000), 0.0)
        v = 0x3fc00000
#        print()
#        print('0x{:08x}'.format(v), self.splitBits68(v), RepCode.from68(v))
        self.assertEqual(RepCode.from68(v), 0.25)

class TestRepCodeTo68Basic(TestRepCode68Base):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test(self):
        """TestRepCodeTo68Basic.test(): tests setUp() and tearDown()."""
        pass

    def test_minmax(self):
        """TestRepCodeTo68Basic.test_minmax(): min/max."""
        myMinMax = RepCode.to68(RepCode.minMaxValue(68)[0]), RepCode.to68(RepCode.minMaxValue(68)[1])
#        print()
#        print((RepCode.minValue(68)))
#        print((RepCode.from68(0xFFC00001)))
#        print((RepCode.from68(0xFFFFFFFF)))
        #print '(0x%X, 0x%X)' % myMinMax
        sys.stderr.write('(0x%X, 0x%X)' % myMinMax)
        sys.stderr.write(' ')
        self.assertEqual(
            myMinMax,
            (0xFFC00000, 0x7FFFFFFF),
        )

class TestRepCodeTo68Python(TestRepCode68Base):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test(self):
        """TestRepCodeTo68Python.test(): tests setUp() and tearDown()."""
        pass

    def test_01_p(self):
        """TestRepCodeTo68Python.test_01_p(): to68(153.0) -> 0x444C8000 Python ."""
        self.assertEqual(pRepCode.to68(153.0), 0x444C8000)

    def test_02_p(self):
        """TestRepCodeTo68Python.test_02_p(): to68(-153.0) -> 0xBBB38000 Python."""
        self.assertEqual(pRepCode.to68(-153.0), 0xBBB38000)

    def test_03_p(self):
        """TestRepCodeTo68Python.test_03__(): to68(0.0) -> 0x40000000 Python."""
        self.assertEqual(pRepCode.to68(0.0), 0x40000000)

    def test_10_p(self):
        """TestRepCodeTo68Python.test_10_p(): to68() <3.50325e-46 is zero Python."""
        v = 3.50325e-46
#        print()
#        print('1e-40 = 0x{:08X} {:s} {:g}'.format(
#            pRepCode.to68(v),
#            self.splitBits68(pRepCode.to68(v)),
#            pRepCode.from68(pRepCode.to68(v))),
#        )
        self.assertEqual(0x00000001, pRepCode.to68(v))
        # Now reduce v slightly and we should see zero
        self.assertEqual(pRepCode.to68(0.99*v), pRepCode.to68(0.0))

    def test_11_p(self):
        """TestRepCodeTo68Python.test_11_p(): to68() -1e40 is min Python."""
#        print()
#        print('-1e40 = 0x{:08X} {:s}'.format(pRepCode.to68(-1e40), self.splitBits68(pRepCode.to68(-1e40))))
#        print('  Min = 0x{:08X} {:g}'.format(pRepCode.to68(RepCode.minValue(68)), RepCode.minValue(68)))
        self.assertEqual(pRepCode.to68(-1e40), pRepCode.to68(RepCode.minValue(68)))

    def test_12_p(self):
        """TestRepCodeTo68Python.test_12_p(): to68() +1e40 is max Python."""
        self.assertEqual(pRepCode.to68(+1e40), pRepCode.to68(RepCode.maxValue(68)))
        
class TestRepCodeTo68Cython(TestRepCode68Base):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test(self):
        """TestRepCodeTo68Cython.test(): tests setUp() and tearDown()."""
        pass

    def test_01_c(self):
        """TestRepCodeTo68Cython.test_01_c(): to68(153.0) -> 0x444C8000 Cython ."""
        self.assertEqual(cRepCode.to68(153.0), 0x444C8000)

    def test_02_c(self):
        """TestRepCodeTo68Cython.test_02_c(): to68(-153.0) -> 0xBBB38000 Cython."""
        v = -153.0
#        e = cRepCode.to68(v)
#        print()
#        print('1e-40 = 0x{:08X} {:s} {:g}'.format(
#            e,
#            self.splitBits68(cRepCode.to68(v)),
#            cRepCode.from68(cRepCode.to68(v))),
#        )
        self.assertEqual(cRepCode.to68(v), 0xBBB38000)

    def test_03_c(self):
        """TestRepCodeTo68Cython.test_03__(): to68(0.0) -> 0x40000000 Cython."""
        self.assertEqual(cRepCode.to68(0.0), 0x40000000)
        
    def test_10_c(self):
        """TestRepCodeTo68Cython.test_10_c(): to68() <3.50325e-46 is zero Cython."""
        v = 3.50325e-46
#        print()
#        print('1e-40 = 0x{:08X} {:s} {:g}'.format(
#            cRepCode.to68(v),
#            self.splitBits68(cRepCode.to68(v)),
#            cRepCode.from68(cRepCode.to68(v))),
#        )
        self.assertEqual(0x00000001, cRepCode.to68(v))
        # Now reduce v slightly and we should see zero
        self.assertEqual(cRepCode.to68(0.99*v), cRepCode.to68(0.0))

    def test_11_c(self):
        """TestRepCodeTo68Cython.test_11_c(): to68() -1e40 is min Cython."""
#        print()
#        print('-1e40 = 0x{:08X} {:s}'.format(cRepCode.to68(-1e40), self.splitBits68(cRepCode.to68(-1e40))))
#        print('  Min = 0x{:08X} {:g}'.format(cRepCode.to68(RepCode.minValue(68)), RepCode.minValue(68)))
        self.assertEqual(cRepCode.to68(-1e40), cRepCode.to68(RepCode.minValue(68)))

    def test_12_c(self):
        """TestRepCodeTo68Cython.test_12_c(): to68() +1e40 is max Cython."""
        self.assertEqual(cRepCode.to68(+1e40), cRepCode.to68(RepCode.maxValue(68)))

class TestRepCodeTo68(TestRepCode68Base):
    """Tests writing to Rep Code 68 with RepCode module that might choose either Python or Cython."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test(self):
        """TestRepCodeTo68.test(): tests setUp() and tearDown()."""
        pass

    def test_01__(self):
        """TestRepCodeTo68.test_00(): to68(153.0) -> 0x444C8000."""
        self.assertEqual(RepCode.to68(153.0), 0x444C8000)

    def test_02__(self):
        """TestRepCodeTo68.test_02__(): to68(-153.0) -> 0xBBB38000."""
        self.assertEqual(RepCode.to68(-153.0), 0xBBB38000)

    def test_03__(self):
        """TestRepCodeTo68.test_03__(): to68(0.0) -> 0x40000000."""
        self.assertEqual(RepCode.to68(0.0), 0x40000000)

    def test_10__(self):
        """TestRepCodeTo68.test_10__(): to68() <3.50325e-46 is zero."""
        v = 3.50325e-46
#        print()
#        print('1e-40 = 0x{:08X} {:s} {:g}'.format(
#            RepCode.to68(v),
#            self.splitBits68(RepCode.to68(v)),
#            RepCode.from68(RepCode.to68(v))),
#        )
        self.assertEqual(0x00000001, RepCode.to68(v))
        # Now reduce v slightly and we should see zero
        self.assertEqual(RepCode.to68(0.99*v), RepCode.to68(0.0))

    def test_11__(self):
        """TestRepCodeTo68.test_11__(): to68() -1e40 is min."""
#        print()
#        print('-1e40 = 0x{:08X} {:s}'.format(RepCode.to68(-1e40), self.splitBits68(RepCode.to68(-1e40))))
#        print('  Min = 0x{:08X} {:g}'.format(RepCode.to68(RepCode.minValue(68)), RepCode.minValue(68)))
        self.assertEqual(RepCode.to68(-1e40), RepCode.to68(RepCode.minValue(68)))

    def test_12__(self):
        """TestRepCodeTo68.test_12__(): to68() +1e40 is max."""
        self.assertEqual(RepCode.to68(+1e40), RepCode.to68(RepCode.maxValue(68)))

class TestRepCodeTo68PyCy(TestRepCode68Base):
    """Tests Python and Cython values match"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeTo68PyCy.test(): tests setUp() and tearDown()."""
        pass
        
    def test_10(self):
        """TestRepCodeTo68PyCy.test_10(): to68() -999.25 -> 0xBA831800"""        
        self.assertEqual('{:b}'.format(pRepCode.to68(-999.25)), '{:b}'.format(cRepCode.to68(-999.25)))
        self.assertEqual(pRepCode.to68(-999.25), cRepCode.to68(-999.25))
        self.assertEqual(RepCode.to68(-999.25), 0xBA831800)

class TestRepCodeTo68LowExponent(TestRepCode68Base):
    """Special tests for low exponent numbers."""

    def test_00(self):
        """TestRepCodeTo68LowExponent.test_30(): to68(0.0) -> 0x40000000 and to68(0.25) -> 0x3fc00000 (Defect found during FrameSet testing)."""
#        print()
#        print('pRepCode.to68(math.ldexp(-1, -128))', '0x{:08x}'.format(pRepCode.to68(math.ldexp(-1, -128))))
#        print('pRepCode.to68(math.ldexp(+1, -128))', '0x{:08x}'.format(pRepCode.to68(math.ldexp(1, -128))))
        self.assertEqual(RepCode.to68(0.0), 0x40000000)
        self.assertEqual(RepCode.to68(0.25), 0x3fc00000)
        self.assertEqual(RepCode.from68(0x40000000), 0.0)
#        print('0x3fc00000', RepCode.from68(0x3fc00000))
        self.assertEqual(RepCode.from68(0x3fc00000), 0.25)

    def test_02_00(self):
        """TestRepCodeTo68LowExponent.test_02_00(): from68() mantissa depression - pRepCode module."""
#        print('0x00000001', RepCode.from68(0x00000001))
        self.assertEqual((0.5, -150), math.frexp(pRepCode.from68(0x00000001)))
        self.assertEqual((0.5, -149), math.frexp(pRepCode.from68(0x00000002)))
        self.assertEqual((0.5, -148), math.frexp(pRepCode.from68(0x00000004)))
        self.assertEqual((0.5, -147), math.frexp(pRepCode.from68(0x00000008)))
        self.assertEqual((0.5, -146), math.frexp(pRepCode.from68(0x00000010)))
        self.assertEqual((0.5, -145), math.frexp(pRepCode.from68(0x00000020)))
        self.assertEqual((0.5, -144), math.frexp(pRepCode.from68(0x00000040)))
        self.assertEqual((0.5, -143), math.frexp(pRepCode.from68(0x00000080)))
        self.assertEqual((0.5, -142), math.frexp(pRepCode.from68(0x00000100)))
        self.assertEqual((0.5, -141), math.frexp(pRepCode.from68(0x00000200)))
        self.assertEqual((0.5, -140), math.frexp(pRepCode.from68(0x00000400)))
        self.assertEqual((0.5, -139), math.frexp(pRepCode.from68(0x00000800)))
        self.assertEqual((0.5, -138), math.frexp(pRepCode.from68(0x00001000)))
        self.assertEqual((0.5, -137), math.frexp(pRepCode.from68(0x00002000)))
        self.assertEqual((0.5, -136), math.frexp(pRepCode.from68(0x00004000)))
        self.assertEqual((0.5, -135), math.frexp(pRepCode.from68(0x00008000)))
        self.assertEqual((0.5, -134), math.frexp(pRepCode.from68(0x00010000)))
        self.assertEqual((0.5, -133), math.frexp(pRepCode.from68(0x00020000)))
        self.assertEqual((0.5, -132), math.frexp(pRepCode.from68(0x00040000)))
        self.assertEqual((0.5, -131), math.frexp(pRepCode.from68(0x00080000)))
        self.assertEqual((0.5, -130), math.frexp(pRepCode.from68(0x00100000)))
        self.assertEqual((0.5, -129), math.frexp(pRepCode.from68(0x00200000)))
        self.assertEqual((0.5, -128), math.frexp(pRepCode.from68(0x00400000)))
        
    def test_02_01(self):
        """TestRepCodeTo68LowExponent.test_02_01(): from68() mantissa depression - cRepCode module."""
#        print('0x00000001', RepCode.from68(0x00000001))
        self.assertEqual((0.5, -150), math.frexp(cRepCode.from68(0x00000001)))
        self.assertEqual((0.5, -149), math.frexp(cRepCode.from68(0x00000002)))
        self.assertEqual((0.5, -148), math.frexp(cRepCode.from68(0x00000004)))
        self.assertEqual((0.5, -147), math.frexp(cRepCode.from68(0x00000008)))
        self.assertEqual((0.5, -146), math.frexp(cRepCode.from68(0x00000010)))
        self.assertEqual((0.5, -145), math.frexp(cRepCode.from68(0x00000020)))
        self.assertEqual((0.5, -144), math.frexp(cRepCode.from68(0x00000040)))
        self.assertEqual((0.5, -143), math.frexp(cRepCode.from68(0x00000080)))
        self.assertEqual((0.5, -142), math.frexp(cRepCode.from68(0x00000100)))
        self.assertEqual((0.5, -141), math.frexp(cRepCode.from68(0x00000200)))
        self.assertEqual((0.5, -140), math.frexp(cRepCode.from68(0x00000400)))
        self.assertEqual((0.5, -139), math.frexp(cRepCode.from68(0x00000800)))
        self.assertEqual((0.5, -138), math.frexp(cRepCode.from68(0x00001000)))
        self.assertEqual((0.5, -137), math.frexp(cRepCode.from68(0x00002000)))
        self.assertEqual((0.5, -136), math.frexp(cRepCode.from68(0x00004000)))
        self.assertEqual((0.5, -135), math.frexp(cRepCode.from68(0x00008000)))
        self.assertEqual((0.5, -134), math.frexp(cRepCode.from68(0x00010000)))
        self.assertEqual((0.5, -133), math.frexp(cRepCode.from68(0x00020000)))
        self.assertEqual((0.5, -132), math.frexp(cRepCode.from68(0x00040000)))
        self.assertEqual((0.5, -131), math.frexp(cRepCode.from68(0x00080000)))
        self.assertEqual((0.5, -130), math.frexp(cRepCode.from68(0x00100000)))
        self.assertEqual((0.5, -129), math.frexp(cRepCode.from68(0x00200000)))
        self.assertEqual((0.5, -128), math.frexp(cRepCode.from68(0x00400000)))
        
    def test_02_02(self):
        """TestRepCodeTo68LowExponent.test_02_02(): from68() mantissa depression - RepCode module."""
#        print('0x00000001', RepCode.from68(0x00000001))
        self.assertEqual((0.5, -150), math.frexp(RepCode.from68(0x00000001)))
        self.assertEqual((0.5, -149), math.frexp(RepCode.from68(0x00000002)))
        self.assertEqual((0.5, -148), math.frexp(RepCode.from68(0x00000004)))
        self.assertEqual((0.5, -147), math.frexp(RepCode.from68(0x00000008)))
        self.assertEqual((0.5, -146), math.frexp(RepCode.from68(0x00000010)))
        self.assertEqual((0.5, -145), math.frexp(RepCode.from68(0x00000020)))
        self.assertEqual((0.5, -144), math.frexp(RepCode.from68(0x00000040)))
        self.assertEqual((0.5, -143), math.frexp(RepCode.from68(0x00000080)))
        self.assertEqual((0.5, -142), math.frexp(RepCode.from68(0x00000100)))
        self.assertEqual((0.5, -141), math.frexp(RepCode.from68(0x00000200)))
        self.assertEqual((0.5, -140), math.frexp(RepCode.from68(0x00000400)))
        self.assertEqual((0.5, -139), math.frexp(RepCode.from68(0x00000800)))
        self.assertEqual((0.5, -138), math.frexp(RepCode.from68(0x00001000)))
        self.assertEqual((0.5, -137), math.frexp(RepCode.from68(0x00002000)))
        self.assertEqual((0.5, -136), math.frexp(RepCode.from68(0x00004000)))
        self.assertEqual((0.5, -135), math.frexp(RepCode.from68(0x00008000)))
        self.assertEqual((0.5, -134), math.frexp(RepCode.from68(0x00010000)))
        self.assertEqual((0.5, -133), math.frexp(RepCode.from68(0x00020000)))
        self.assertEqual((0.5, -132), math.frexp(RepCode.from68(0x00040000)))
        self.assertEqual((0.5, -131), math.frexp(RepCode.from68(0x00080000)))
        self.assertEqual((0.5, -130), math.frexp(RepCode.from68(0x00100000)))
        self.assertEqual((0.5, -129), math.frexp(RepCode.from68(0x00200000)))
        self.assertEqual((0.5, -128), math.frexp(RepCode.from68(0x00400000)))
        
    def test_03(self):
        """TestRepCodeTo68LowExponent.test_03(): Special exponent tests."""
#        print()
        for e in (-151, -150, -129, -128, 0):
            rcWord = pRepCode.to68(math.ldexp(0.5, e))
#            print(
#                  'pRepCode.to68(math.ldexp(0.5, {:4d}))'.format(e),
#                  '0x{:08x}->{:s}'.format(rcWord, math.frexp(pRepCode.from68(rcWord)))
#            )
            #print()
        for e in (-151, -150, -129, -128, 0):
            rcWord = cRepCode.to68(math.ldexp(0.5, e))
#            print(
#                  'cRepCode.to68(math.ldexp(0.5, {:4d}))'.format(e),
#                  '0x{:08x}->{:s}'.format(rcWord, math.frexp(pRepCode.from68(rcWord)))
#            )
            #print()

    def test_04(self):
        """TestRepCodeTo68LowExponent.test_04(): Special exponent tests, full range."""
        for e in range(-150, 128, 1):
            rcWord = pRepCode.to68(math.ldexp(0.5, e))
            self.assertEqual((0.5, e), math.frexp(pRepCode.from68(rcWord)))
        for e in range(-150, 128, 1):
            rcWord = cRepCode.to68(math.ldexp(0.5, e))
            self.assertEqual((0.5, e), math.frexp(cRepCode.from68(rcWord)))
        for e in range(-150, 128, 1):
            rcWord = RepCode.to68(math.ldexp(0.5, e))
            self.assertEqual((0.5, e), math.frexp(RepCode.from68(rcWord)))
        
    def test_05(self):
        """TestRepCodeTo68LowExponent.test_02(): to68() exponent <-150 made to zero."""
        self.assertEqual(0x40000000, pRepCode.to68(math.ldexp(0.5, -151)))
        self.assertEqual(0x40000000, cRepCode.to68(math.ldexp(0.5, -151)))
        self.assertEqual(0x40000000, RepCode.to68(math.ldexp(0.5, -151)))

#    def test_10(self):
#        """TestRepCodeTo68LowExponent.test_10(): to68(0.0) -> 0x40000000 and to68(0.25) -> ??? (Defect found during FrameSet testing)."""
#        print()
#        for e in range(-128-24, 129, 1):
#            rcWord = pRepCode.to68(math.ldexp(0.5, e))
#            print(
#                  'pRepCode.to68(math.ldexp(0.5, {:4d}))'.format(e),
#                  '0x{:08x}->{:s}'.format(rcWord, math.frexp(pRepCode.from68(rcWord)))
#            )


@pytest.mark.slow
class TestRepCodeFrom68Time(TestRepCode68Base):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestRepCodeFrom68Time.test_00(): tests setUp() and tearDown()."""
        pass

    def test_time_00(self):
        """TestRepCodeFrom68Time.test_time_00(): tests conversion of 1e6 of same word - Cython code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from68(0xBBB38000)
            i += 1
        self.writeTimeToStdErr(tS, 68, num)
        
    def test_time_01(self):
        """TestRepCodeFrom68Time.test_time_01(): tests conversion of 1e6 of same word - Python code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            pRepCode.from68(0xBBB38000)
            i += 1
        self.writeTimeToStdErr(tS, 68, num)
        
    def test_time_02(self):
        """TestRepCodeFrom68Time.test_time_00(): tests conversion of 1e6 of same word - Cython time c.f. Python: """
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.from68(0xBBB38000)
            i += 1
        tE_C = time.perf_counter() - tS
        #print 'C time: %.3f rate %8.0f words/S' % (tE_C, num/tE_C)
        i = 0
        tS = time.perf_counter()
        while i < num:
            pRepCode.from68(0xBBB38000)
            i += 1
        tE_P = time.perf_counter() - tS
        #print 'Python time: %.3f rate %8.0f words/S' % (tE_P, num/tE_P)
        #sys.stderr.write('Cython: %.3f% ' % tE_C)
        #sys.stderr.write('Python: %.3f% ' % tE_P)
        sys.stderr.write('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))
        
    def test_time_03(self):
        """TestRepCodeFrom68Time.test_time_03(): tests conversion of 1e6 of same word - RepCode.from68 code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            RepCode.from68(0xBBB38000)
            i += 1
        self.writeTimeToStdErr(tS, 68, num)
        
    def test_time_10(self):
        """TestRepCodeFrom68Time.test_time_10(): tests conversion of 1e5 random words - Cython code."""
        i = 0
        num = 1e5
        tS = time.perf_counter()
        while i < num:
            cRepCode.from68(self.randWord(1, 8, 23))
            i += 1
        self.writeTimeToStdErr(tS, 68, num)
        
    def test_time_11(self):
        """TestRepCodeFrom68Time.test_time_11(): tests conversion of 1e5 random words - Python code."""
        i = 0
        num = 1e5
        tS = time.perf_counter()
        while i < num:
            pRepCode.from68(self.randWord(1, 8, 23))
            i += 1
        self.writeTimeToStdErr(tS, 68, num)

    def test_time_20(self):
        """TestRepCodeFrom68Time.test_time_20(): 1e5 word conversion from FileRead: """
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
            pRepCode.read68(myFile)
            i += 1
        tE_P = time.perf_counter() - tS
        self.assertFalse(myFile.hasLd())
        sys.stderr.write('Python: %.3f %8.0f words/S ' % (tE_P, numWords/tE_P))
        # Now Cython code
        myBy = io.BytesIO(prContStart + prContBody * numPrBody + prContEnd)
        myFile = File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=False)
        i = 0
        tS = time.perf_counter()
        while i < wordsInPr * numPr:
            RepCode.read68(myFile)
            i += 1
        tE_C = time.perf_counter() - tS
        self.assertFalse(myFile.hasLd())
        sys.stderr.write('Cython: %.3f %8.0f words/S ' % (tE_C, numWords/tE_C))
        sys.stderr.write('%.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))


@pytest.mark.slow
class TestRepCodeTo68Time(TestRepCode68Base):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test(self):
        """TestRepCodeTo68Time.test(): tests setUp() and tearDown()."""
        pass

    def test_time_00(self):
        """TestRepCodeTo68Time.test_time_00(): tests conversion of 1e6 of same word - Cython code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.to68(153.0)
            i += 1
        self.writeTimeToStdErr(tS, 68, num)
        
    def test_time_01(self):
        """TestRepCodeTo68Time.test_time_01(): tests conversion of 1e6 of same word - Python code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            pRepCode.to68(153.0)
            i += 1
        self.writeTimeToStdErr(tS, 68, num)
        
    def test_time_02(self):
        """TestRepCodeTo68Time.test_time_02(): 1e6 same word  Cython time c.f. Python:"""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            cRepCode.to68(153.0)
            i += 1
        tE_C = time.perf_counter() - tS
        sys.stderr.write(' Cython: %.3f rate %8.0f words/S' % (tE_C, num/tE_C))
        i = 0
        tS = time.perf_counter()
        while i < num:
            pRepCode.to68(153.0)
            i += 1
        tE_P = time.perf_counter() - tS
        sys.stderr.write(' Python: %.3f rate %8.f words/S' % (tE_P, num/tE_P))
        sys.stderr.write(' %.1f%% (x%.1f) ' % ((100.0 * (tE_C / tE_P)), tE_P / tE_C))
        
    def test_time_03(self):
        """TestRepCodeTo68Time.test_time_03(): tests conversion of 1e6 of same word - RepCode.to68 code."""
        i = 0
        num = 1e6
        tS = time.perf_counter()
        while i < num:
            RepCode.to68(153.0)
            i += 1
        self.writeTimeToStdErr(tS, 68, num)
        
    def test_time_10(self):
        """TestRepCodeTo68Time.test_time_10(): tests conversion of 1e5 random words - Cython code."""
        i = 0
        num = 1e5
        tS = time.perf_counter()
        myMin, myMax = RepCode.minMaxValue(68)
        while i < num:
            val = myMin + random.random() * (myMax - myMin)
            cRepCode.to68(val)
            i += 1
        self.writeTimeToStdErr(tS, 68, num)
        
    def test_time_11(self):
        """TestRepCodeTo68Time.test_time_11(): tests conversion of 1e5 random words - Python code."""
        i = 0
        num = 1e5
        tS = time.perf_counter()
        myMin, myMax = RepCode.minMaxValue(68)
        while i < num:
            val = myMin + random.random() * (myMax - myMin)
            pRepCode.to68(val)
            i += 1
        self.writeTimeToStdErr(tS, 68, num)
                
#    def test_time_21(self):
#        """TestRepCodeTo68Time.test_time_21(): write68() 1e5 words"""
#        i = 0
#        num = 1e5
#        tS = time.perf_counter()
#        while i < num:
#            RepCode.write68(-999.25)
#            i += 1
#        self.writeTimeToStdErr(tS, 68, num)

class Special(unittest.TestCase):
    """Special tests."""
    pass

    def test_to_minus_153_p(self):
        """TestRepCodeToFrom68CPython.test_02_c(): to68(0xBBB38000) -> -153.0 CPython."""
        result = pRepCode.to68(-153.0)
        self.assertEqual(result, 0xBBB38000)

    def test_to_minus_153_c(self):
        """TestRepCodeToFrom68CPython.test_02_c(): to68(0xBBB38000) -> -153.0 CPython."""
        result = cRepCode.to68(-153.0)
        self.assertEqual(result, 0xBBB38000)

    def test_to_minus_153_cp(self):
        """TestRepCodeToFrom68CPython.test_02_c(): to68(0xBBB38000) -> -153.0 CPython."""
        result = cpRepCode.to68(-153.0)
        print(result, hex(result))
        self.assertEqual(result, 0xBBB38000)


def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    # Type 68
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom68Basic))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom68Python))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom68Cython))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom68))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeTo68Basic))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeTo68Python))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeTo68Cython))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeToFrom68CPython))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeTo68))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeTo68PyCy))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeTo68LowExponent))
    # Performance tests
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeFrom68Time))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepCodeTo68Time))
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
