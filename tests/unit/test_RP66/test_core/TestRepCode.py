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

Created on Aug 4, 2011

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

import os
import sys
import logging
import datetime
import time
import unittest

import pytest

import TotalDepth.RP66.core.RepCode as RepCode

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import BaseTestClasses

#class MockStreamRead(object):
#    def __init__(self, b):
#        self._b = b
#        self._p = 0
#        
#    def read(self, n=1):
#        """Get n bytes and increment the index."""
#        self._p += n
#        return self._b[self._p-n:self._p]
#        
#class MockStreamWrite(object):
#    def __init__(self):
#        self._b = bytearray()
#        # This is not used
#        self._p = 0
#    
#    @property
#    def bytes(self):
#        return self._b
#        
##    def write(self, b):
##        """Write a single byte."""
##        self._b.append(b)
##        self._p += 1
#
#    def write(self, b):
#        """Write multiple bytes."""
#        self._b += b
#        self._p += len(b)
#        return len(b)
#    
#    def clear(self):
#        self._b = bytearray()
#        self._p = 0

class TestMockStream(unittest.TestCase):
    """Tests reading and writing, mostly for failure."""
    
    def test_10(self):
        """TestMockStream.test_10(): Not enough bytes to read (input stream exhausted)."""
        self.assertRaises(
            RepCode.ExceptionRepCodeEndOfStream,
            RepCode.readSLONG,
            BaseTestClasses.MockStreamRead(b''),
        )

    def test_11(self):
        """TestMockStream.test_11(): Simulation of failing to write bytes to stream."""
        class MockStreamWriteNothing(BaseTestClasses.MockStreamWrite):
            def write(self, b):
                return 0
        self.assertRaises(
            RepCode.ExceptionRepCodeWriteToStream,
            RepCode._writeStruct,
            1,
            MockStreamWriteNothing(),
            RepCode.STRUCT_RC_SLONG,
        )

class TestRepCodeBase(unittest.TestCase):
    
    def _indirectTest(self):
        """Tests edge values write/read - indirect."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeIndirectRepCode(self.NUM, v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readIndirectRepCode(self.NUM, sIn)
            self.assertEqual(v, vR)

class TestFSINGL(TestRepCodeBase):
    """Tests the FSINGL Representation Code number 2."""
    NUM = 2
    CASES = (
        (0.0,       b'\x00\x00\x00\x00'),
        (153.0,     b'\x43\x19\x00\x00'),
        (-153.0,    b'\xc3\x19\x00\x00'),
    )
    
    def test_00(self):
        """Tests FSINGL properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('FSINGL', rte.SymbolicName)
        self.assertEquals('IEEE single precision floating point', rte.Description)
        self.assertEquals('NUMBER', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals(4, rte.Size)
        
    def test_01(self):
        """Tests FSINGL values write/read."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeFSINGL(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readFSINGL(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests FSINGL edge values write/read - indirect."""
        self._indirectTest()

class TestFSING1(TestRepCodeBase):
    """Tests the FSING1 Representation Code number 3."""
    NUM = 3
    CASES = (
        (RepCode.FSING1Internal(0.0, 0.0),          b'\x00\x00\x00\x00\x00\x00\x00\x00'),
        (RepCode.FSING1Internal(153.0, 153.0),      b'\x43\x19\x00\x00\x43\x19\x00\x00'),
        (RepCode.FSING1Internal(-153.0, -153.0),    b'\xc3\x19\x00\x00\xc3\x19\x00\x00'),
    )
    
    def test_00(self):
        """Tests FSING1 properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('FSING1', rte.SymbolicName)
        self.assertEquals('Validated single precision floating point', rte.Description)
        self.assertEquals('BALANCED-INTERVAL', rte.Class)
        self.assertEquals('C', rte.Type)
        self.assertEquals(8, rte.Size)
        
    def test_01(self):
        """Tests FSING1 values write/read."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeFSING1(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readFSING1(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests FSINGL1 edge values write/read - indirect."""
        self._indirectTest()

class TestFSING2(TestRepCodeBase):
    """Tests the FSING2 Representation Code number 4."""
    NUM = 4
    CASES = (
        (RepCode.FSING2Internal(0.0, 0.0, 0.0),             b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'),
        (RepCode.FSING2Internal(153.0, 153.0, 153.0),       b'\x43\x19\x00\x00\x43\x19\x00\x00\x43\x19\x00\x00'),
        (RepCode.FSING2Internal(-153.0, -153.0, -153.0),    b'\xc3\x19\x00\x00\xc3\x19\x00\x00\xc3\x19\x00\x00'),
        (RepCode.FSING2Internal(153.0, -153.0, 153.0),      b'\x43\x19\x00\x00\xc3\x19\x00\x00\x43\x19\x00\x00'),
    )
    
    def test_00(self):
        """Tests FSING2 properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('FSING2', rte.SymbolicName)
        self.assertEquals('Two-way validated single precision floating point', rte.Description)
        self.assertEquals('UNBALANCED-INTERVAL', rte.Class)
        self.assertEquals('C', rte.Type)
        self.assertEquals(12, rte.Size)
        
    def test_01(self):
        """Tests FSING2 values write/read."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeFSING2(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readFSING2(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests FSINGL1 edge values write/read - indirect."""
        self._indirectTest()

class TestFDOUBL(TestRepCodeBase):
    """Tests the FDOUBL Representation Code number 7."""
    NUM = 7
    CASES = (
        (0.0,       b'\x00\x00\x00\x00\x00\x00\x00\x00'),
        (153.0,     b'\x40\x63\x20\x00\x00\x00\x00\x00'),
        (-153.0,    b'\xc0\x63\x20\x00\x00\x00\x00\x00'),
    )
    
    def test_00(self):
        """Tests FDOUBL properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('FDOUBL', rte.SymbolicName)
        self.assertEquals('IEEE double precision floating point', rte.Description)
        self.assertEquals('NUMBER', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals(8, rte.Size)
        
    def test_01(self):
        """Tests FDOUBL values write/read."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeFDOUBL(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readFDOUBL(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests FDOUBL edge values write/read - indirect."""
        self._indirectTest()

class TestFDOUB1(TestRepCodeBase):
    """Tests the FDOUB1 Representation Code number 3."""
    NUM = 8
    CASES = (
        (RepCode.FDOUB1Internal(0.0, 0.0),          b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'),
        (RepCode.FDOUB1Internal(153.0, 153.0),      b'\x40\x63\x20\x00\x00\x00\x00\x00\x40\x63\x20\x00\x00\x00\x00\x00'),
        (RepCode.FDOUB1Internal(-153.0, -153.0),    b'\xc0\x63\x20\x00\x00\x00\x00\x00\xc0\x63\x20\x00\x00\x00\x00\x00'),
    )
    
    def test_00(self):
        """Tests FDOUB1 properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('FDOUB1', rte.SymbolicName)
        self.assertEquals('Validated double precision floating point', rte.Description)
        self.assertEquals('BALANCED-INTERVAL', rte.Class)
        self.assertEquals('C', rte.Type)
        self.assertEquals(16, rte.Size)
        
    def test_01(self):
        """Tests FDOUB1 values write/read."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeFDOUB1(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readFDOUB1(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests FDOUBL1 edge values write/read - indirect."""
        self._indirectTest()

class TestFDOUB2(TestRepCodeBase):
    """Tests the FDOUB2 Representation Code number 9."""
    NUM = 9
    CASES = (
        (RepCode.FDOUB2Internal(0.0, 0.0, 0.0),             b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'),
        (RepCode.FDOUB2Internal(153.0, 153.0, 153.0),       b'\x40\x63\x20\x00\x00\x00\x00\x00\x40\x63\x20\x00\x00\x00\x00\x00\x40\x63\x20\x00\x00\x00\x00\x00'),
        (RepCode.FDOUB2Internal(-153.0, -153.0, -153.0),    b'\xc0\x63\x20\x00\x00\x00\x00\x00\xc0\x63\x20\x00\x00\x00\x00\x00\xc0\x63\x20\x00\x00\x00\x00\x00'),
        (RepCode.FDOUB2Internal(153.0, -153.0, 153.0),      b'\x40\x63\x20\x00\x00\x00\x00\x00\xc0\x63\x20\x00\x00\x00\x00\x00\x40\x63\x20\x00\x00\x00\x00\x00'),
    )
    
    def test_00(self):
        """Tests FDOUB2 properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('FDOUB2', rte.SymbolicName)
        self.assertEquals('Two-way validated double precision floating point', rte.Description)
        self.assertEquals('UNBALANCED-INTERVAL', rte.Class)
        self.assertEquals('C', rte.Type)
        self.assertEquals(24, rte.Size)
        
    def test_01(self):
        """Tests FDOUB2 values write/read."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeFDOUB2(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readFDOUB2(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests FDOUBL1 edge values write/read - indirect."""
        self._indirectTest()

class TestSSHORT(TestRepCodeBase):
    """Tests the SSHORT Representation Code number 12."""
    NUM = 12
    CASES = (
        (0,     b'\x00'),
        (89,    b'\x59'),
        (-89,   b'\xA7'),
        (-128,  b'\x80'),
        (127,   b'\x7F'),
    )
    
    def test_00(self):
        """Tests SSHORT properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('SSHORT', rte.SymbolicName)
        self.assertEquals('Short signed integer', rte.Description)
        self.assertEquals('NUMBER', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals(1, rte.Size)
        
    def test_01(self):
        """Tests SSHORT values write/read."""
        for v, b in self.CASES:
#            print('TRACE: v, b:', v, b)
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeSSHORT(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readSSHORT(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests SSHORT edge values write/read - indirect."""
        self._indirectTest()

class TestSNORM(TestRepCodeBase):
    """Tests the SNORM Representation Code number 12."""
    NUM = 13
    CASES = (
        (0,         b'\x00\x00'),
        (153,       b'\x00\x99'),
        (-153,      b'\xff\x67'),
        (-32768,    b'\x80\x00'),
        (32767,     b'\x7F\xFF'),
    )
    
    def test_00(self):
        """Tests SNORM properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('SNORM', rte.SymbolicName)
        self.assertEquals('Normal signed integer', rte.Description)
        self.assertEquals('NUMBER', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals(2, rte.Size)
        
    def test_01(self):
        """Tests SNORM values write/read."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeSNORM(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readSNORM(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests SNORM edge values write/read - indirect."""
        self._indirectTest()

class TestSLONG(TestRepCodeBase):
    """Tests the SLONG Representation Code number 14."""
    NUM = 14
    CASES = (
        (0,         b'\x00\x00\x00\x00'),
        (153,       b'\x00\x00\x00\x99'),
        (-153,      b'\xff\xff\xff\x67'),
        (-2**31,    b'\x80\x00\x00\x00'),
        (2**31-1,   b'\x7f\xff\xff\xff'),
    )
    
    def test_00(self):
        """Tests SLONG properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('SLONG', rte.SymbolicName)
        self.assertEquals('Long signed integer', rte.Description)
        self.assertEquals('NUMBER', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals(4, rte.Size)
        
    def test_01(self):
        """Tests SLONG values write/read."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeSLONG(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readSLONG(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests SLONG edge values write/read - indirect."""
        self._indirectTest()

class TestUSHORT(TestRepCodeBase):
    """Tests the USHORT Representation Code number 15."""
    NUM = 15
    CASES = (
        (0,     b'\x00'),
        (217,   b'\xD9'),
        (255,   b'\xFF'),
    )
    
    def test_00(self):
        """Tests USHORT properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('USHORT', rte.SymbolicName)
        self.assertEquals('Short unsigned integer', rte.Description)
        self.assertEquals('NUMBER', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals(1, rte.Size)
        
    def test_01(self):
        """Tests USHORT values write/read."""
        for v, b in self.CASES:
#            print('TRACE: v, b:', v, b)
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeUSHORT(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readUSHORT(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests USHORT edge values write/read - indirect."""
        self._indirectTest()

class TestUNORM(TestRepCodeBase):
    """Tests the UNORM Representation Code number 12."""
    NUM = 16
    CASES = (
        (0,         b'\x00\x00'),
        (153,       b'\x00\x99'),
        (256,       b'\x01\x00'),
        (2**16-1,     b'\xFF\xFF'),
    )
    
    def test_00(self):
        """Tests UNORM properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('UNORM', rte.SymbolicName)
        self.assertEquals('Normal unsigned integer', rte.Description)
        self.assertEquals('NUMBER', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals(2, rte.Size)
        
    def test_01(self):
        """Tests UNORM values write/read."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeUNORM(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readUNORM(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests UNORM edge values write/read - indirect."""
        self._indirectTest()

class TestULONG(TestRepCodeBase):
    """Tests the ULONG Representation Code number 14."""
    NUM = 17
    CASES = (
        (0,         b'\x00\x00\x00\x00'),
        (153,       b'\x00\x00\x00\x99'),
        (2**8,      b'\x00\x00\x01\x00'),
        (2**16,     b'\x00\x01\x00\x00'),
        (2**24,     b'\x01\x00\x00\x00'),
        (2**32-1,   b'\xff\xff\xff\xff'),
    )
    
    def test_00(self):
        """Tests ULONG properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('ULONG', rte.SymbolicName)
        self.assertEquals('Long unsigned integer', rte.Description)
        self.assertEquals('NUMBER', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals(4, rte.Size)
        
    def test_01(self):
        """Tests ULONG values write/read."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeULONG(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readULONG(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests ULONG edge values write/read - indirect."""
        self._indirectTest()

class TestUVARI(TestRepCodeBase):
    """Tests the UVARI Representation Code number 18."""
    NUM = 18
    CASES = (
        (0,         b'\x00'),
        (1,         b'\x01'),
        (2**7-1,    b'\x7f'),
        (2**7,      b'\x80\x80'),
        (2**7+1,    b'\x80\x81'),
        (2**14-1,   b'\xbf\xff'),
        (2**14,     b'\xc0\x00@\x00'),
        (2**14+1,   b'\xc0\x00@\x01'),
        (2**30-1,   b'\xff\xff\xff\xff'),
    )
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """Tests UVARI properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('UVARI', rte.SymbolicName)
        self.assertEquals('Variable-length unsigned integer', rte.Description)
        self.assertEquals('NUMBER', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals((1,2,4), rte.Size)
        
#    def test_05(self):
#        """Tests UVARI read."""
#        v = RepCode.readUVARI(BaseTestClasses.MockStreamRead(b'\x00\x00\x00\x00'))
#        self.assertEquals(0, v)
    
    def test_01(self):
        """Tests UVARI edge values write/read."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeUVARI(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readUVARI(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests UVARI edge values write/read - indirect."""
        self._indirectTest()

class TestIDENT(TestRepCodeBase):
    """Tests the IDENT Representation Code number 19."""
    NUM = 19
    CASES = (
        (RepCode.IDENTString(b''),       b'\x00'),
        (RepCode.IDENTString(b'TYPE1'),  b'\x05TYPE1'),
    )
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """Tests IDENT properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('IDENT', rte.SymbolicName)
        self.assertEquals('Variable-length identifier', rte.Description)
        self.assertEquals('STRING', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals(-1, rte.Size)
        
    def test_01(self):
        """Tests IDENT edge values write/read."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeIDENT(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readIDENT(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests IDENT edge values write/read - indirect."""
        self._indirectTest()

class TestASCII(TestRepCodeBase):
    """Tests the ASCII Representation Code number 20."""
    NUM = 20
    CASES = (
        (RepCode.ASCIIString(''),       b'\x00'),
        (RepCode.ASCIIString('$ / X'),  b'$ / X'),
    )
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """Tests ASCII properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('ASCII', rte.SymbolicName)
        self.assertEquals('Variable-length ASCII character string', rte.Description)
        self.assertEquals('STRING', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals(-1, rte.Size)

    @pytest.mark.xfail(reason="RP66 is not fully supported.")
    def test_01(self):
        """Tests ASCII edge values write/read."""
        for v, b in self.CASES:
            # assert(0)
            # print('TRACE: test_01', v, b)
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeASCII(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readASCII(sIn)
            # print()
            # print(vR.ASCII_CHARS)
            self.assertEqual(v.payload, vR.payload)

    @pytest.mark.xfail(reason="RP66 is not fully supported.")
    def test_02(self):
        """Tests ASCII edge values write/read - indirect."""
        self._indirectTest()

class TestDTIME(TestRepCodeBase):
    """Tests the DTIME Representation Code number 21."""
    NUM = 21
    CASES = (
        # >>> t = 1318066299.719783
        # >>> time.gmtime(t)
        # time.struct_time(tm_year=2011, tm_mon=10, tm_mday=8, tm_hour=9, tm_min=31, tm_sec=39, tm_wday=5, tm_yday=281, tm_isdst=0)
        ((2011, 10, 8, 10, 31, 39, 719783), b"o\n\x08\n\x1f\'\x02\xcf"),
    )

    def _datetimeTupleToSeconds(self, theTu):
        """Given a datetime tuple (y,m,d,h,min,s,uS) this uses the time module
        to return the seconds from the epoc."""
        mySt = time.struct_time(theTu[:-1] + (0,0,0))
        tSecs = time.mktime(mySt) + int(theTu[-1] / 10.0**3) / 10.0**3
        return tSecs
        
    def test_00(self):
        """Tests DTIME properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('DTIME', rte.SymbolicName)
        self.assertEquals('Date and time', rte.Description)
        self.assertEquals('TIME', rte.Class)
        self.assertEquals('C', rte.Type)
        self.assertEquals(8, rte.Size)
        
    def test_01(self):
        """A saturday morning."""
        # A saturday morning
        t = datetime.datetime(*(2011, 10, 8, 10, 31, 39, 719783))
        myRc = RepCode.DTIMEInternal(t)
        sOut = BaseTestClasses.MockStreamWrite()
        RepCode.writeDTIME(myRc, sOut)
#        print('sOut.bytes', sOut.bytes)
#        print(myRc.time())
        
    def test_02(self):
        """Tests DTIME edge values write/read."""
        for v, b in self.CASES:
            myRc = RepCode.DTIMEInternal(datetime.datetime(*v))
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeDTIME(myRc, sOut)
            self.assertEqual(b, sOut.bytes)
            # Read from bytes
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            myRc = RepCode.readDTIME(sIn)
            self.assertEqual(self._datetimeTupleToSeconds(v), myRc.mktime())

    def test_12(self):
        """Tests DTIME edge values write/read - indirect."""
        # Can not use generic method as CASES does not contain DTIME objects.
        for v, b in self.CASES:
            # Fix up the microseconds to truncate to milleseconds
            myV = v[:-1] + (1000*(v[-1] // 1000),)
            rc = RepCode.DTIMEInternal(datetime.datetime(*myV))
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeIndirectRepCode(self.NUM, rc, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readIndirectRepCode(self.NUM, sIn)
            self.assertEqual(rc._time, vR._time)

class TestORIGIN(TestUVARI):
    """Tests the ORIGIN Representation Code number 22."""
    NUM = 22

    def test_00(self):
        """Tests UVARI properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('ORIGIN', rte.SymbolicName)
        self.assertEquals('Origin reference', rte.Description)
        self.assertEquals('ORIGIN', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals(-1, rte.Size)

class TestSTATUS(TestRepCodeBase):
    """Tests the STATUS Representation Code number 26."""
    NUM = 26
    CASES = (
        (0,     b'\x00'),
        (1,     b'\x01'),
    )
    
    def test_00(self):
        """Tests STATUS properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('STATUS', rte.SymbolicName)
        self.assertEquals('Boolean status', rte.Description)
        self.assertEquals('STATUS', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals(1, rte.Size)
        
    def test_01(self):
        """Tests STATUS values write/read."""
        for v, b in self.CASES:
#            print('TRACE: v, b:', v, b)
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeSTATUS(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readSTATUS(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests STATUS edge values write/read - indirect."""
        self._indirectTest()

class TestISNORM(TestRepCodeBase):
    """Tests the ISNORM Representation Code number 30."""
    NUM = 30
    CASES = (
        (0,         b'\x00\x00'),
        (153,       b'\x99\x00'),
        (-153,      b'\x67\xff'),
        (-32768,    b'\x00\x80'),
        (32767,     b'\xFF\x7F'),
    )
    
    def test_00(self):
        """Tests ISNORM properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('ISNORM', rte.SymbolicName)
        self.assertEquals('Inverted order normal signed integer', rte.Description)
        self.assertEquals('NUMBER', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals(2, rte.Size)
        
    def test_01(self):
        """Tests ISNORM values write/read."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeISNORM(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readISNORM(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests ISNORM edge values write/read - indirect."""
        self._indirectTest()

class TestISLONG(TestRepCodeBase):
    """Tests the ISLONG Representation Code number 31."""
    NUM = 31
    CASES = (
        (0,     b'\x00\x00\x00\x00'),
        (153,   b'\x99\x00\x00\x00'),
        (-153,  b'\x67\xff\xff\xff'),
    )
    
    def test_00(self):
        """Tests SLONG properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('ISLONG', rte.SymbolicName)
        self.assertEquals('Inverted order long signed integer', rte.Description)
        self.assertEquals('NUMBER', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals(4, rte.Size)
        
    def test_01(self):
        """Tests ISLONG values write/read."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeISLONG(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readISLONG(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests ISLONG edge values write/read - indirect."""
        self._indirectTest()

class TestIUNORM(TestRepCodeBase):
    """Tests the IUNORM Representation Code number 32."""
    NUM = 32
    CASES = (
        (0,         b'\x00\x00'),
        (153,       b'\x99\x00'),
        (256,       b'\x00\x01'),
        (2**16-1,     b'\xFF\xFF'),
    )
    
    def test_00(self):
        """Tests IUNORM properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('IUNORM', rte.SymbolicName)
        self.assertEquals('Inverted order normal unsigned integer', rte.Description)
        self.assertEquals('NUMBER', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals(2, rte.Size)
        
    def test_01(self):
        """Tests IUNORM values write/read."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeIUNORM(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readIUNORM(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests IUNORM edge values write/read - indirect."""
        self._indirectTest()

class TestIULONG(TestRepCodeBase):
    """Tests the IULONG Representation Code number 33."""
    NUM = 33
    CASES = (
        (0,         b'\x00\x00\x00\x00'),
        (153,       b'\x99\x00\x00\x00'),
        (2**8,      b'\x00\x01\x00\x00'),
        (2**16,     b'\x00\x00\x01\x00'),
        (2**24,     b'\x00\x00\x00\x01'),
        (2**32-1,   b'\xff\xff\xff\xff'),
    )
    
    def test_00(self):
        """Tests IULONG properties in RC_TABLE."""
        rte = RepCode.RC_TABLE[self.NUM]
        self.assertEquals(self.NUM, rte.Code)
        self.assertEquals('IULONG', rte.SymbolicName)
        self.assertEquals('Inverted order long unsigned integer', rte.Description)
        self.assertEquals('NUMBER', rte.Class)
        self.assertEquals('S', rte.Type)
        self.assertEquals(4, rte.Size)
        
    def test_01(self):
        """Tests IULONG values write/read."""
        for v, b in self.CASES:
            sOut = BaseTestClasses.MockStreamWrite()
            RepCode.writeIULONG(v, sOut)
            self.assertEqual(sOut.bytes, b)
            sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
            vR = RepCode.readIULONG(sIn)
            self.assertEqual(v, vR)

    def test_02(self):
        """Tests IULONG edge values write/read - indirect."""
        self._indirectTest()

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMockStream))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFSINGL))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFSING1))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFSING2))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFDOUBL))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFDOUB1))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFDOUB2))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSNORM))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSSHORT))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSLONG))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUNORM))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUSHORT))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestULONG))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUVARI))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIDENT))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestASCII))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDTIME))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestORIGIN))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSTATUS))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestISNORM))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestISLONG))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIUNORM))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIULONG))
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
    import time
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
    print(('CPU time = %8.3f (S)' % clkExec))
    print('Bye, bye!')

if __name__ == "__main__":
    main()
