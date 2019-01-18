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
"""Tests ...
"""

__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

import os
import sys
import time
import logging
import math
import random
import pprint

from TotalDepth.LIS.core import RepCode
from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import Mnem
from TotalDepth.util.plot import Stroke
from TotalDepth.util.plot import FILMCfg
from TotalDepth.util.plot import PRESCfg

######################
# Section: Unit tests.
######################
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import BaseTestClasses

class TestLineTrans(unittest.TestCase):
    """Tests line transformation."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestLineTrans.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestLineTrans.test_01(): Base class LineTransBase()."""
        myT = PRESCfg.LineTransBase(0.0, 100.0, 200.0, 1000.0, PRESCfg.BACKUP_ALL)
        self.assertEqual(0.0, myT._lP)
        self.assertEqual(100.0, myT._rP)
        self.assertEqual(200.0, myT._lL)
        self.assertEqual(1000.0, myT._rL)
        self.assertEqual(200.0, myT.leftL)
        self.assertEqual(1000.0, myT.rightL)
        self.assertEqual(PRESCfg.BACKUP_ALL, myT._bu)
        self.assertRaises(NotImplementedError, myT.L2P, None)
        self.assertRaises(NotImplementedError, myT.wrapPos, None)
        # Test stringify
        str(myT)
        
    def test_02(self):
        """TestLineTrans.test_02(): Linear identity transformation."""
        myT = PRESCfg.LineTransLin(0.0, 100.0, 0.0, 100.0)
        self.assertEqual(0.0, myT.L2P(0.0))
        self.assertEqual(100.0, myT.L2P(100.0))
        self.assertEqual(-1.0, myT.L2P(-1.0))
        self.assertEqual(1000.0, myT.L2P(1000.0))
        
    def test_03(self):
        """TestLineTrans.test_03(): Linear scale=x4 transformation."""
        myT = PRESCfg.LineTransLin(0.0, 100.0, 0.0, 400.0)
        self.assertEqual(0.0, myT.L2P(0.0))
        self.assertEqual(25.0, myT.L2P(100.0))
        self.assertEqual(-0.25, myT.L2P(-1.0))
        self.assertEqual(100.0, myT.L2P(400.0))
        self.assertEqual(250.0, myT.L2P(1000.0))
        
    def test_04(self):
        """TestLineTrans.test_04(): Linear offset=10.0 transformation."""
        myT = PRESCfg.LineTransLin(0.0, 100.0, 10.0, 110.0)
        self.assertEqual(-10.0, myT.L2P(0.0))
        self.assertEqual(0.0, myT.L2P(10.0))
        self.assertEqual(90.0, myT.L2P(100.0))
        self.assertEqual(100.0, myT.L2P(110.0))
        self.assertEqual(990.0, myT.L2P(1000.0))
        
    def test_05(self):
        """TestLineTrans.test_05(): Linear scale=x4 offset=10.0 transformation."""
        myT = PRESCfg.LineTransLin(0.0, 100.0, 40.0, 440.0)
        self.assertEqual(0.0, myT.L2P(40.0))
        self.assertEqual(100.0, myT.L2P(440.0))
        self.assertEqual(-10.0, myT.L2P(0.0))
        self.assertEqual(15.0, myT.L2P(100.0))
        self.assertEqual(240.0, myT.L2P(1000.0))
        
    def test_06(self):
        """TestLineTrans.test_06(): Linear identity transformation, physical offset=10.0."""
        myT = PRESCfg.LineTransLin(10.0, 110.0, 0.0, 100.0)
        self.assertEqual(10.0, myT.L2P(0.0))
        self.assertEqual(110.0, myT.L2P(100.0))
        self.assertEqual(9.0, myT.L2P(-1.0))
        self.assertEqual(1010.0, myT.L2P(1000.0))
        
    def test_07(self):
        """TestLineTrans.test_07(): Linear scale=x4 offset=10.0 transformation using wrapPos()."""
        myT = PRESCfg.LineTransLin(0.0, 100.0, 40.0, 440.0)
        self.assertEqual(0.0, myT.L2P(40.0))
        self.assertEqual(100.0, myT.L2P(440.0))
        self.assertEqual(-10.0, myT.L2P(0.0))
        self.assertEqual(15.0, myT.L2P(100.0))
        self.assertEqual(240.0, myT.L2P(1000.0))
        self.assertEqual((-1, 0.0), myT.wrapPos(-360.0))
        self.assertEqual((-1, 25.0), myT.wrapPos(-260.0))
        self.assertEqual((0, 0.0), myT.wrapPos(40.0))
        self.assertEqual((1, 0.0), myT.wrapPos(440.0))
        self.assertEqual((1, 25.0), myT.wrapPos(540.0))
        
    def test_10(self):
        """TestLineTrans.test_10(): Log identity transformation."""
        myT = PRESCfg.LineTransLog10(0.0, 100.0, 1.0, 10.0)
        self.assertEqual(0.0, myT.L2P(1.0))
        self.assertEqual(100.0, myT.L2P(10.0))
        self.assertEqual(-100.0, myT.L2P(0.1))
        self.assertEqual(200.0, myT.L2P(100.0))
        self.assertEqual(100.0*math.log10(2.0), myT.L2P(2.0))
        
    def test_11(self):
        """TestLineTrans.test_11(): Log identity transformation, 4 decades."""
        myT = PRESCfg.LineTransLog10(0.0, 100.0, 1.0, 10000.0)
        self.assertEqual(0.0, myT.L2P(1.0))
        self.assertEqual(100.0, myT.L2P(10000.0))
        self.assertEqual(-25.0, myT.L2P(0.1))
        self.assertEqual(125.0, myT.L2P(10*10000.0))
        
    def test_12(self):
        """TestLineTrans.test_12(): Log identity transformation, 4 decades, offset=0.2."""
        myT = PRESCfg.LineTransLog10(0.0, 100.0, 0.2, 2000.0)
        self.assertEqual(0.0, myT.L2P(0.2))
        self.assertEqual(100.0, myT.L2P(2000.0))
        self.assertEqual(25.0, myT.L2P(2.0))
        self.assertEqual(50.0, myT.L2P(20.0))
        self.assertEqual(75.0, myT.L2P(200.0))
        self.assertEqual(125.0, myT.L2P(10*2000.0))
        
    def test_20(self):
        """TestLineTrans.test_20(): Log identity transformation, 4 decades, offset=0.2, physical offset=10.0."""
        myT = PRESCfg.LineTransLog10(10.0, 110.0, 0.2, 2000.0)
        self.assertEqual(10.0, myT.L2P(0.2))
        self.assertEqual(110.0, myT.L2P(2000.0))
        self.assertEqual(35.0, myT.L2P(2.0))
        self.assertEqual(60.0, myT.L2P(20.0))
        self.assertEqual(85.0, myT.L2P(200.0))
        self.assertEqual(135.0, myT.L2P(10*2000.0))

    def test_21(self):
        """TestLineTrans.test_21(): Log identity transformation, 4 decades, offset=0.2, physical offset=10.0 with wrapPos()."""
        myT = PRESCfg.LineTransLog10(10.0, 110.0, 0.2, 2000.0)
#        print()
#        print('myT.wrapPos(0.2)', myT.wrapPos(0.2))
#        print('myT.wrapPos(2.0)', myT.wrapPos(2.0))
        self.assertEqual((0, 10.0), myT.wrapPos(0.2))
        self.assertEqual((0, 35.0), myT.wrapPos(2.0))
        self.assertEqual((0, 60.0), myT.wrapPos(20.0))
        self.assertEqual((0, 85.0), myT.wrapPos(200.0))
        self.assertEqual((1, 10.0), myT.wrapPos(2000.0))
        self.assertEqual((-1, 85.0), myT.wrapPos(0.02))
        self.assertEqual((1, 35.0), myT.wrapPos(20000.0))
        
    def test_30_00(self):
        """TestLineTrans.test_30_00(): Linear identity transformation, wrapPos(), no backup trace."""
        myT = PRESCfg.LineTransLin(0.0, 100.0, 0.0, 100.0, backup=PRESCfg.BACKUP_NONE)
        self.assertEqual((0, 0.0), myT.wrapPos(0.0))
        self.assertEqual((0, 99.99), myT.wrapPos(99.99))
        self.assertEqual((-1, 0.0), myT.wrapPos(-100.0))
        self.assertEqual((1, 0.0), myT.wrapPos(100.0))

    def test_30_01(self):
        """TestLineTrans.test_30_01(): Linear identity transformation, offScale(), no backup trace."""
        myT = PRESCfg.LineTransLin(0.0, 100.0, 0.0, 100.0, backup=PRESCfg.BACKUP_NONE)
        self.assertEqual(0, myT.offScale(0))
        self.assertEqual(-1, myT.offScale(-1))
        self.assertEqual(1, myT.offScale(1))
        self.assertEqual(-1, myT.offScale(-2))
        self.assertEqual(1, myT.offScale(2))
        self.assertEqual(-1, myT.offScale(-3))
        self.assertEqual(1, myT.offScale(3))
        
    def test_30_02(self):
        """TestLineTrans.test_30_02(): Linear identity transformation, isOffScaleLeft()/isOffScaleRight(), no backup trace."""
        myT = PRESCfg.LineTransLin(0.0, 100.0, 0.0, 100.0, backup=PRESCfg.BACKUP_NONE)
        self.assertFalse(myT.isOffScaleLeft(0))
        self.assertFalse(myT.isOffScaleRight(0))
        self.assertFalse(myT.isOffScaleLeft(1))
        self.assertTrue(myT.isOffScaleRight(1))
        self.assertTrue(myT.isOffScaleLeft(-1))
        self.assertFalse(myT.isOffScaleRight(-1))
        
    def test_31_00(self):
        """TestLineTrans.test_31_00(): Linear identity transformation, wrapPos(), single backup trace."""
        myT = PRESCfg.LineTransLin(0.0, 100.0, 0.0, 100.0, backup=PRESCfg.BACKUP_ONCE)
        self.assertEqual((0, 0.0), myT.wrapPos(0.0))
        self.assertEqual((0, 99.99), myT.wrapPos(99.99))
        self.assertEqual((-1, 0.0), myT.wrapPos(-100.0))
        self.assertEqual((1, 0.0), myT.wrapPos(100.0))
        self.assertEqual((-2, 0.0), myT.wrapPos(-200.0))
        self.assertEqual((2, 0.0), myT.wrapPos(200.0))

    def test_31_01(self):
        """TestLineTrans.test_31_01(): Linear identity transformation, offScale(), single backup trace."""
        myT = PRESCfg.LineTransLin(0.0, 100.0, 0.0, 100.0, backup=PRESCfg.BACKUP_ONCE)
        self.assertEqual(0, myT.offScale(0))
        self.assertEqual(0, myT.offScale(-1))
        self.assertEqual(0, myT.offScale(1))
        self.assertEqual(-1, myT.offScale(-2))
        self.assertEqual(1, myT.offScale(2))
        self.assertEqual(-1, myT.offScale(-3))
        self.assertEqual(1, myT.offScale(3))

    def test_31_02(self):
        """TestLineTrans.test_31_02(): Linear identity transformation, isOffScaleLeft()/isOffScaleRight(), single backup trace."""
        myT = PRESCfg.LineTransLin(0.0, 100.0, 0.0, 100.0, backup=PRESCfg.BACKUP_ONCE)
        self.assertFalse(myT.isOffScaleLeft(0))
        self.assertFalse(myT.isOffScaleRight(0))
        self.assertFalse(myT.isOffScaleLeft(1))
        self.assertFalse(myT.isOffScaleRight(1))
        self.assertFalse(myT.isOffScaleLeft(-1))
        self.assertFalse(myT.isOffScaleRight(-1))
        # Now is off scale
        self.assertFalse(myT.isOffScaleLeft(2))
        self.assertTrue(myT.isOffScaleRight(2))
        self.assertTrue(myT.isOffScaleLeft(-2))
        self.assertFalse(myT.isOffScaleRight(-2))
        
    def test_32(self):
        """TestLineTrans.test_31_00(): Linear identity transformation, wrapPos(), two backup traces."""
        myT = PRESCfg.LineTransLin(0.0, 100.0, 0.0, 100.0, backup=PRESCfg.BACKUP_TWICE)
        self.assertEqual((0, 0.0), myT.wrapPos(0.0))
        self.assertEqual((0, 99.99), myT.wrapPos(99.99))
        self.assertEqual((-1, 0.0), myT.wrapPos(-100.0))
        self.assertEqual((1, 0.0), myT.wrapPos(100.0))
        self.assertEqual((-2, 0.0), myT.wrapPos(-200.0))
        self.assertEqual((2, 0.0), myT.wrapPos(200.0))
        self.assertEqual((-3, 0.0), myT.wrapPos(-300.0))
        self.assertEqual((3, 0.0), myT.wrapPos(300.0))

    def test_32_01(self):
        """TestLineTrans.test_31_01(): Linear identity transformation, offScale(), two backup traces."""
        myT = PRESCfg.LineTransLin(0.0, 100.0, 0.0, 100.0, backup=PRESCfg.BACKUP_TWICE)
        self.assertEqual(0, myT.offScale(0))
        self.assertEqual(0, myT.offScale(-1))
        self.assertEqual(0, myT.offScale(1))
        self.assertEqual(0, myT.offScale(-2))
        self.assertEqual(0, myT.offScale(2))
        self.assertEqual(-1, myT.offScale(-3))
        self.assertEqual(1, myT.offScale(3))

    def test_32_02(self):
        """TestLineTrans.test_32_02(): Linear identity transformation, isOffScaleLeft()/isOffScaleRight(), two backup trace."""
        myT = PRESCfg.LineTransLin(0.0, 100.0, 0.0, 100.0, backup=PRESCfg.BACKUP_TWICE)
        self.assertFalse(myT.isOffScaleLeft(0))
        self.assertFalse(myT.isOffScaleRight(0))
        self.assertFalse(myT.isOffScaleLeft(1))
        self.assertFalse(myT.isOffScaleRight(1))
        self.assertFalse(myT.isOffScaleLeft(-1))
        self.assertFalse(myT.isOffScaleRight(-1))
        self.assertFalse(myT.isOffScaleLeft(2))
        self.assertFalse(myT.isOffScaleRight(2))
        self.assertFalse(myT.isOffScaleLeft(-2))
        self.assertFalse(myT.isOffScaleRight(-2))
        # Now is off scale
        self.assertFalse(myT.isOffScaleLeft(3))
        self.assertTrue(myT.isOffScaleRight(3))
        self.assertTrue(myT.isOffScaleLeft(-3))
        self.assertFalse(myT.isOffScaleRight(-3))
        
    def test_33(self):
        """TestLineTrans.test_33(): Linear identity transformation, isOffScaleLeft()/isOffScaleRight(), unlimited wrap, random input."""
        myT = PRESCfg.LineTransLin(0.0, 100.0, 0.0, 100.0, backup=PRESCfg.BACKUP_ALL)
        for i in range(1024*8):
            w = random.randint(-64*1024, 64*1024)
            self.assertFalse(myT.isOffScaleLeft(w))
            self.assertFalse(myT.isOffScaleRight(w))

    def test_40_00(self):
        """TestLineTrans.test_40_00(): Linear identity transformation, wrapPos(), physical 0->8, logical scale 0->64."""
        myT = PRESCfg.LineTransLin(0.0, 8.0, 0.0, 64.0, backup=PRESCfg.BACKUP_ONCE)
        self.assertEqual((0, 0.0), myT.wrapPos(0.0))
        self.assertEqual((1, 0.0), myT.wrapPos(64.0))
        self.assertEqual((2, 0.0), myT.wrapPos(128.0))
        self.assertEqual((-1, 0.0), myT.wrapPos(-64.0))
        self.assertEqual((3, 0.0), myT.wrapPos(192.0))
        self.assertEqual((-2, 0.0), myT.wrapPos(-128.0))

    def test_40_01(self):
        """TestLineTrans.test_40_01(): Linear identity transformation, wrapPos(), physical 8->0, logical scale 0->64 raises ExceptionLineTransBase."""
        self.assertRaises(PRESCfg.ExceptionLineTransBase, PRESCfg.LineTransLin, 8.0, 0.0, 0.0, 64.0, backup=PRESCfg.BACKUP_ONCE)

    def test_40_02(self):
        """TestLineTrans.test_40_02(): Linear identity transformation, wrapPos(), physical 0->8, logical scale 64->0."""
        myT = PRESCfg.LineTransLin(0.0, 8.0, 64.0, 0.0, backup=PRESCfg.BACKUP_ONCE)
        self.assertEqual((1, 0.0), myT.wrapPos(0.0))
        self.assertEqual((0, 0.0), myT.wrapPos(64.0))
        self.assertEqual((-1, 0.0), myT.wrapPos(128.0))
        self.assertEqual((2, 0.0), myT.wrapPos(-64.0))
        self.assertEqual((-2, 0.0), myT.wrapPos(192.0))
        self.assertEqual((3, 0.0), myT.wrapPos(-128.0))

    def test_40_03(self):
        """TestLineTrans.test_40_03(): Linear identity transformation, wrapPos(), physical 8->0, logical scale 64->0 raises ExceptionLineTransBase."""
        self.assertRaises(PRESCfg.ExceptionLineTransBase, PRESCfg.LineTransLin, 8.0, 0.0, 64.0, 0.0, backup=PRESCfg.BACKUP_ONCE)

class TestPRESRead(BaseTestClasses.TestBaseFile):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        # Create a film table, log and linear plots
        myByFilm = b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1   ' \
                    + b'EA\x04\x00GCOD    E20 ' \
                    + b'EA\x04\x00GDEC    -4--' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    2   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D200'
        myFi = self._retFileSinglePr(myByFilm)
        myFc = FILMCfg.FilmCfgLISRead(LogiRec.LrTableRead(myFi))
        self.assertEqual(2, len(myFc))
        self.assertEqual([b'1   ', b'2   '], sorted(list(myFc.keys())))
#        print()
#        print(myFc[b'1\x00\x00\x00'])
#        print(myFc[b'1\x00\x00\x00'].name)
#        print(myFc[b'1\x00\x00\x00'].xScale)
#        print(len(myFc[b'1\x00\x00\x00']))
        self.assertEqual(b'1   ', myFc[Mnem.Mnem(b'1   ')].name)
        self.assertEqual(200, myFc[Mnem.Mnem(b'1   ')].xScale)
        self.assertEqual(4, len(myFc[Mnem.Mnem(b'1   ')]))
#        print('left', myFc[b'1\x00\x00\x00'][0].left)
#        print('right', myFc[b'1\x00\x00\x00'][0].right)
#        self.assertEqual(Coord.Dim(0.0, 'in'), myFc[b'1\x00\x00\x00'][0].left)
#        self.assertEqual(Coord.Dim(2.4, 'in'), myFc[b'1\x00\x00\x00'][0].right)
#        self.assertEqual(Coord.Dim(2.4, 'in'), myFc[b'1\x00\x00\x00'][1].left)
#        self.assertEqual(Coord.Dim(3.2, 'in'), myFc[b'1\x00\x00\x00'][1].right)
#        self.assertEqual(Coord.Dim(3.2, 'in'), myFc[b'1\x00\x00\x00'][2].left)
#        self.assertEqual(Coord.Dim(5.6, 'in'), myFc[b'1\x00\x00\x00'][2].right)
#        self.assertEqual(Coord.Dim(5.6, 'in'), myFc[b'1\x00\x00\x00'][3].left)
#        self.assertEqual(Coord.Dim(8.0, 'in'), myFc[b'1\x00\x00\x00'][3].right)
        # Create a PRES table        
        myByPres = bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    SP\x00\x00'
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
            + b'\x00A\x04\x00MNEM    CALI'
                + b'EA\x04\x00OUTP    CALI'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LDAS'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDGIN  A\xd0\x00\x00'
                + b'ED\x04\x00REDGIN  Bx\x00\x00'
            + b'\x00A\x04\x00MNEM    MINV'
                + b'EA\x04\x00OUTP    MINV'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDG    B\xf8\x00\x00'
                + b'ED\x04\x00REDG    \x00\x00\x00\x00'
            + b'\x00A\x04\x00MNEM    MNOR'
                + b'EA\x04\x00OUTP    MNOR'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LDAS'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDG    B\xf8\x00\x00'
                + b'ED\x04\x00REDG    \x00\x00\x00\x00'
            + b'\x00A\x04\x00MNEM    LLD\x00'
                + b'EA\x04\x00OUTP    LLD '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T23 '
                + b'EA\x04\x00CODI    LDAS'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    GRAD'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDGOHMM?fff'
                + b'ED\x04\x00REDGOHMME\xfd\x00\x00'
            + b'\x00A\x04\x00MNEM    LLDB'
                + b'EA\x04\x00OUTP    LLD '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HDAS'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    GRAD'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDGOHMME\xfd\x00\x00'
                + b'ED\x04\x00REDGOHMMIa\xa8\x00'
            + b'\x00A\x04\x00MNEM    LLG\x00'
                + b'EA\x04\x00OUTP    LLG '
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T23 '
                + b'EA\x04\x00CODI    LDAS'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    GRAD'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDGOHMM?fff'
                + b'ED\x04\x00REDGOHMME\xfd\x00\x00'
            + b'\x00A\x04\x00MNEM    LLGB'
                + b'EA\x04\x00OUTP    LLG '
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HDAS'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    GRAD'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDGOHMME\xfd\x00\x00'
                + b'ED\x04\x00REDGOHMMIa\xa8\x00'
            + b'\x00A\x04\x00MNEM    LLS\x00'
                + b'EA\x04\x00OUTP    LLS '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T23 '
                + b'EA\x04\x00CODI    LSPO'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    GRAD'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDGOHMM?fff'
                + b'ED\x04\x00REDGOHMME\xfd\x00\x00'
            + b'\x00A\x04\x00MNEM    LLSB'
                + b'EA\x04\x00OUTP    LLS '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T2  '
                + b'EA\x04\x00CODI    HSPO'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    GRAD'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDGOHMME\xfd\x00\x00'
                + b'ED\x04\x00REDGOHMMIa\xa8\x00'
            + b'\x00A\x04\x00MNEM    MSFL'
                + b'EA\x04\x00OUTP    MSFL'
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T23 '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    GRAD'
                + b'ED\x04\x00FILT    @@\x00\x00'
                + b'ED\x04\x00LEDGOHMM?fff'
                + b'ED\x04\x00REDGOHMME\xfd\x00\x00'
            + b'\x00A\x04\x00MNEM    11\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    12\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    13\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    14\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    15\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    16\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    17\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    18\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
            + b'\x00A\x04\x00MNEM    19\x00\x00'
                + b'EA\x04\x00OUTP    DUMM'
                + b'EA\x04\x00STAT    DISA'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    NB  '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDG    ' + RepCode.writeBytes(-80.0, 68)#\x00\x00\x00\x00'
                + b'ED\x04\x00REDG    ' + RepCode.writeBytes(20.0, 68)#@\xc0\x00\x00'
        )
        myFi = self._retFileSinglePr(myByPres)
        self._pclr = PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), myFc)

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPRESRead.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestPRESRead.test_01(): access APIs."""
        #print()
        #print(self._pclr._destOutpToCurveIdMap)
        self.assertEqual(
            { Mnem.Mnem(b'1   ') :
                {
                    Mnem.Mnem(b'LLS ') : [b'LLS\x00', b'LLSB'],
                    Mnem.Mnem(b'MSFL') : [b'MSFL'],
                    Mnem.Mnem(b'MNOR') : [b'MNOR'],
                    Mnem.Mnem(b'LLD ') : [b'LLD\x00', b'LLDB'],
                    Mnem.Mnem(b'CALI') : [b'CALI'],
                    Mnem.Mnem(b'SP  ') : [b'SP\x00\x00'],
                    Mnem.Mnem(b'LLG ') : [b'LLG\x00', b'LLGB'],
                    Mnem.Mnem(b'MINV') : [b'MINV'],
                },
            },
            self._pclr._destOutpToCurveIdMap,
        )
        #print()
        #print('list(self._pclr.keys())', list(self._pclr.keys()))
        self.assertEqual(
            sorted([
                b'LLS\x00',
                b'MSFL',
                b'LLSB',
                b'MNOR',
                b'LLD\x00',
                b'CALI',
                b'LLDB',
                b'SP\x00\x00',
                b'LLG\x00',
                b'LLGB',
                b'MINV',
            ]),
            sorted(list(self._pclr.keys()))
        )
        self.assertEqual(11, len(self._pclr))
#        print()
#        print("self._pclr[b'MSFL']", self._pclr[b'MSFL'])
        self.assertEqual(b'MSFL', self._pclr[b'MSFL'].mnem)
        self.assertTrue(b'MSFL' in self._pclr)
        self.assertEqual(
            sorted([
                b'LLS ', b'MSFL', b'MNOR', b'LLD ', b'CALI', b'SP  ', b'LLG ', b'MINV',
            ]),
            sorted(list(self._pclr.outpChIDs(Mnem.Mnem(b'1   '))))
        )
        self.assertEqual(
            sorted([
                b'LLS\x00', b'LLSB'
            ]),
            sorted(list(self._pclr.outpCurveIDs(Mnem.Mnem(b'1   '), Mnem.Mnem(b'LLS '))))
        )
        self.assertTrue(self._pclr.usesOutpChannel(Mnem.Mnem(b'1   '), Mnem.Mnem(b'LLS ')))
        self.assertFalse(self._pclr.usesOutpChannel(Mnem.Mnem(b'1   '), Mnem.Mnem(b'UNKN')))
    
    def test_02(self):
        """TestPRESRead.test_02(): tracValueFunction b'SP\x00\x00'."""
        # Try converting values
        myFunc = self._pclr[b'SP\x00\x00'].tracValueFunction(Mnem.Mnem(b'1')).wrapPos
#        print('myFunc', myFunc)
#        print()
#        print(myFunc(-80.0))
#        print(myFunc(0.0))
#        print(myFunc(20.0))
        self.assertEqual((0, 0.0), myFunc(-80.0))
        self.assertEqual((0, 1.92), myFunc(0.0))
        self.assertEqual((1, 0.0), myFunc(20.0))
        
    def test_03(self):
        """TestPRESRead.test_03(): tracValueFunction b'LLD\x00'."""
        # Try converting values
        myFunc = self._pclr[b'LLD\x00'].tracValueFunction
#        print()
#        print(self._pclr[b'LLD\x00'].trac)
#        print(myFunc(0.2))
#        print(myFunc(2.0))
#        print(myFunc(20.0))
#        print(myFunc(200.0))
#        print(myFunc(2000.0-1e-8))
#        print(myFunc(2000.0))
#        print(myFunc(0.02))
#        print(myFunc(20000.0))

class TestPRESReadMultiFilm(BaseTestClasses.TestBaseFile):
    """Tests PRES tables where the curves have BOTH, NEIT, ALL etc."""
    def setUp(self):
        """Set up."""
        myByFilm = b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1   ' \
                    + b'EA\x04\x00GCOD    E20 ' \
                    + b'EA\x04\x00GDEC    -4--' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    2   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D200'
        myFi = self._retFileSinglePr(myByFilm)
        self._filmCfg = FILMCfg.FilmCfgLISRead(LogiRec.LrTableRead(myFi))
        self.assertEqual(2, len(self._filmCfg))
        self.assertEqual([b'1   ', b'2   '], sorted(list(self._filmCfg.keys())))
        self.assertEqual(b'1   ', self._filmCfg[Mnem.Mnem(b'1   ')].name)
        self.assertEqual(200, self._filmCfg[Mnem.Mnem(b'1   ')].xScale)
        self.assertEqual(4, len(self._filmCfg[Mnem.Mnem(b'1   ')]))
        # Check we can get the film destinations
        self.assertEqual(sorted([Mnem.Mnem(b'2'), Mnem.Mnem(b'1')]), sorted(self._filmCfg.retAllFILMDestS(b'BOTH')))
        self.assertEqual(sorted([Mnem.Mnem(b'2'), Mnem.Mnem(b'1')]), sorted(self._filmCfg.retAllFILMDestS(b'ALL')))
        self.assertEqual(sorted([Mnem.Mnem(b'1'), Mnem.Mnem(b'2')]), sorted(self._filmCfg.retAllFILMDestS(b'12')))
        self.assertEqual([], self._filmCfg.retAllFILMDestS(b'NEIT'))
        # Create a FILM table with alphanumeric labels
        myByFilm = b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    A   ' \
                    + b'EA\x04\x00GCOD    E20 ' \
                    + b'EA\x04\x00GDEC    -4--' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    B   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D500'
        myFi = self._retFileSinglePr(myByFilm)
        self._filmCfgAlpha = FILMCfg.FilmCfgLISRead(LogiRec.LrTableRead(myFi))
        self.assertEqual(2, len(self._filmCfgAlpha))
        self.assertEqual([b'A   ', b'B   '], sorted(list(self._filmCfgAlpha.keys())))
        self.assertEqual(b'A   ', self._filmCfgAlpha[Mnem.Mnem(b'A   ')].name)
        self.assertEqual(200, self._filmCfgAlpha[Mnem.Mnem(b'A   ')].xScale)
        self.assertEqual(500, self._filmCfgAlpha[Mnem.Mnem(b'B   ')].xScale)
        self.assertEqual(4, len(self._filmCfgAlpha[Mnem.Mnem(b'A   ')]))
        # Check we can get the film destinations
        self.assertEqual(sorted([Mnem.Mnem(b'B'), Mnem.Mnem(b'A')]), sorted(self._filmCfgAlpha.retAllFILMDestS(b'BOTH')))
        self.assertEqual(sorted([Mnem.Mnem(b'B'), Mnem.Mnem(b'A')]), sorted(self._filmCfgAlpha.retAllFILMDestS(b'ALL')))
        self.assertEqual(sorted([Mnem.Mnem(b'B'), Mnem.Mnem(b'A')]), sorted(self._filmCfgAlpha.retAllFILMDestS(b'BA')))
        self.assertEqual(sorted([Mnem.Mnem(b'A'), Mnem.Mnem(b'B')]), sorted(self._filmCfgAlpha.retAllFILMDestS(b'AB')))
        self.assertEqual([], self._filmCfgAlpha.retAllFILMDestS(b'NEIT'))

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPRESReadMultiFilm.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestPRESReadMultiFilm.test_01(): Curve uses film destination b'BOTH'."""
        # Create a PRES table        
        myByPres = bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    SP\x00\x00'
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    BOTH'
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
        )
        myFi = self._retFileSinglePr(myByPres)
        myPclr = PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), self._filmCfg)
        # Map of (Mnem.Mnem(dest) : {Mnem.Mnem(output_channel_id) : [curve_id, ...], ...}, ...}
#        print('_destOutpToCurveIdMap')
#        print(myPclr._destOutpToCurveIdMap)
        self.assertEqual(
            {
                Mnem.Mnem(b'2'): {
                    Mnem.Mnem(b'SP') : [Mnem.Mnem(b'SP'),],
                },
                Mnem.Mnem(b'1') : {
                    Mnem.Mnem(b'SP') : [Mnem.Mnem(b'SP')],
                },
            },
            myPclr._destOutpToCurveIdMap,
        )
        #print()
        #print('list(self._pclr.keys())', list(self._pclr.keys()))
        self.assertEqual(
            [
                Mnem.Mnem(b'SP\x00\x00'),
            ],
            list(myPclr.keys())
        )
        self.assertEqual(1, len(myPclr))
#        print()
#        print("self._pclr[b'MSFL']", self._pclr[b'MSFL'])
        self.assertEqual(b'SP\x00\x00', myPclr[Mnem.Mnem(b'SP')].mnem)
        self.assertTrue(b'SP\x00\x00' in myPclr)
        self.assertEqual(
            [
                Mnem.Mnem(b'SP  '),
            ],
            list(myPclr.outpChIDs(Mnem.Mnem(b'1   ')))
        )
        self.assertEqual(
            [
                Mnem.Mnem(b'SP  '),
            ],
            list(myPclr.outpCurveIDs(Mnem.Mnem(b'1   '), Mnem.Mnem(b'SP')))
        )
        self.assertTrue(myPclr.usesOutpChannel(Mnem.Mnem(b'1   '), Mnem.Mnem(b'SP ')))
        self.assertFalse(myPclr.usesOutpChannel(Mnem.Mnem(b'1   '), b'UNKN'))

    def test_02(self):
        """TestPRESReadMultiFilm.test_02(): Curve use film destination: b'NEIT'."""
        # Create a PRES table        
        myByPres = bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    CNEI'
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
        )
        myFi = self._retFileSinglePr(myByPres)
        myPclr = PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), self._filmCfg)
        # Map of (Mnem.Mnem(dest) : {Mnem.Mnem(output_channel_id) : [curve_id, ...], ...}, ...}
#        print('_destOutpToCurveIdMap')
#        print(myPclr._destOutpToCurveIdMap)
        self.assertEqual(
            {
            },
            myPclr._destOutpToCurveIdMap,
        )
    
    def test_03(self):
        """TestPRESReadMultiFilm.test_03(): Curve use film destination: b'ALL '."""
        # Create a PRES table        
        myByPres = bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    CALL'
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    ALL '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
        )
        myFi = self._retFileSinglePr(myByPres)
        myPclr = PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), self._filmCfg)
        # Map of (Mnem.Mnem(dest) : {Mnem.Mnem(output_channel_id) : [curve_id, ...], ...}, ...}
#        print('_destOutpToCurveIdMap')
#        print(myPclr._destOutpToCurveIdMap)
        self.assertEqual(
            {
                Mnem.Mnem(b'2'): {
                    Mnem.Mnem(b'SP') : [Mnem.Mnem(b'CALL'),],
                },
                Mnem.Mnem(b'1') : {
                    Mnem.Mnem(b'SP') : [Mnem.Mnem(b'CALL')],
                },
            },
            myPclr._destOutpToCurveIdMap,
        )
    
    def test_04(self):
        """TestPRESReadMultiFilm.test_04(): Curve use film destination: b'12  '."""
        # Create a PRES table        
        myByPres = bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    C12 '
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    12  '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
        )
        myFi = self._retFileSinglePr(myByPres)
        myPclr = PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), self._filmCfg)
        # Map of (Mnem.Mnem(dest) : {Mnem.Mnem(output_channel_id) : [curve_id, ...], ...}, ...}
#        print('_destOutpToCurveIdMap')
#        print(myPclr._destOutpToCurveIdMap)
        self.assertEqual(
            {
                Mnem.Mnem(b'2'): {
                    Mnem.Mnem(b'SP') : [Mnem.Mnem(b'C12'),],
                },
                Mnem.Mnem(b'1') : {
                    Mnem.Mnem(b'SP') : [Mnem.Mnem(b'C12')],
                },
            },
            myPclr._destOutpToCurveIdMap,
        )
    
    def test_05(self):
        """TestPRESReadMultiFilm.test_05(): Curve uses film destination: b'1   '."""
        # Create a PRES table        
        myByPres = bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    C1  '
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
        )
        myFi = self._retFileSinglePr(myByPres)
        myPclr = PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), self._filmCfg)
        # Map of (Mnem.Mnem(dest) : {Mnem.Mnem(output_channel_id) : [curve_id, ...], ...}, ...}
#        print('_destOutpToCurveIdMap')
#        print(myPclr._destOutpToCurveIdMap)
        self.assertEqual(
            {
                Mnem.Mnem(b'1') : {
                    Mnem.Mnem(b'SP') : [Mnem.Mnem(b'C1')],
                },
            },
            myPclr._destOutpToCurveIdMap,
        )
    
    def test_06(self):
        """TestPRESReadMultiFilm.test_06(): Curve uses alphanumeric film destination: b'B   '."""
        # Create a PRES table        
        myByPres = bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    CB  '
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    B   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
        )
        myFi = self._retFileSinglePr(myByPres)
        myPclr = PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), self._filmCfgAlpha)
        # Map of (Mnem.Mnem(dest) : {Mnem.Mnem(output_channel_id) : [curve_id, ...], ...}, ...}
#        print('_destOutpToCurveIdMap')
#        print(myPclr._destOutpToCurveIdMap)
        self.assertEqual(
            {
                Mnem.Mnem(b'B') : {
                    Mnem.Mnem(b'SP') : [Mnem.Mnem(b'CB')],
                },
            },
            myPclr._destOutpToCurveIdMap,
        )
    
    def test_10(self):
        """TestPRESReadMultiFilm.test_10(): Curves use film destinations: BOTH, NEIT, ALL, 12, 1, 2."""
        # Create a PRES table        
        myByPres = bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    CBOT'
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    BOTH'
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
            + b'\x00A\x04\x00MNEM    CNEI'
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    NEIT'
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
            + b'\x00A\x04\x00MNEM    CALL'
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    ALL '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
            + b'\x00A\x04\x00MNEM    C12 '
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    12  '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
            + b'\x00A\x04\x00MNEM    C1  '
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
            + b'\x00A\x04\x00MNEM    C2  '
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    2   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
        )
        myFi = self._retFileSinglePr(myByPres)
        myPclr = PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), self._filmCfg)
        # Map of (Mnem.Mnem(dest) : {Mnem.Mnem(output_channel_id) : [curve_id, ...], ...}, ...}
#        print('_destOutpToCurveIdMap')
#        print(myPclr._destOutpToCurveIdMap)
#        pprint.pprint(myPclr._destOutpToCurveIdMap)
        self.assertEqual(
            {
                Mnem.Mnem(b'1\x00\x00\x00'): {
                    Mnem.Mnem(b'SP\x00\x00'): [
                        Mnem.Mnem(b'CBOT'),
                        Mnem.Mnem(b'CALL'),
                        Mnem.Mnem(b'C12\x00'),
                        Mnem.Mnem(b'C1\x00\x00'),
                    ]
                },
                Mnem.Mnem(b'2\x00\x00\x00'): {
                    Mnem.Mnem(b'SP\x00\x00'): [
                        Mnem.Mnem(b'CBOT'),
                        Mnem.Mnem(b'CALL'),
                        Mnem.Mnem(b'C12\x00'),
                        Mnem.Mnem(b'C2\x00\x00'),
                    ]
                },
            },
            myPclr._destOutpToCurveIdMap,
        )
        
class TestPRESReadFail(BaseTestClasses.TestBaseFile):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass
    
    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPRESReadFail.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestPRESReadFail.test_01(): nonexistent FILM MNEM (should warn)."""
        # Create a film table, log and linear plots
        myByFilm = b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1   ' \
                    + b'EA\x04\x00GCOD    E20 ' \
                    + b'EA\x04\x00GDEC    -4--' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    2   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D200'
        myFi = self._retFileSinglePr(myByFilm)
        myFc = FILMCfg.FilmCfgLISRead(LogiRec.LrTableRead(myFi))
        # Create a PRES table        
        myByPres = bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    SP\x00\x00'
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    7   ' # Wrong!
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
        )
        myFi = self._retFileSinglePr(myByPres)
        self._pclr = PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), myFc)
#        print('self._pclr', self._pclr)
#        print(self._pclr._destOutpToCurveIdMap)
#        self.assertRaises(PRESCfg.ExceptionCurveCfg, PRESCfg.PresCfgLISRead, LogiRec.LrTableRead(myFi), myFc)
            
    def test_02(self):
        """TestPRESReadFail.test_02(): out of range MODE entry (should warn)."""
        # Create a film table, log and linear plots
        myByFilm = b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1   ' \
                    + b'EA\x04\x00GCOD    E20 ' \
                    + b'EA\x04\x00GDEC    -4--' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    2   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D200'
        myFi = self._retFileSinglePr(myByFilm)
        myFc = FILMCfg.FilmCfgLISRead(LogiRec.LrTableRead(myFi))
        # Create a PRES table        
        myByPres = bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    SP\x00\x00'
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    1   '
                # Weird MODE entry
                + b'EA\x04\x00MODE    WTF '
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
        )
        myFi = self._retFileSinglePr(myByPres)
#        self._pclr = PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), myFc)
        # Should issue a warning here
        PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), myFc)
            
    def test_03(self):
        """TestPRESReadFail.test_03(): out of range CODI entry (should warn)."""
        # Create a film table, log and linear plots
        myByFilm = b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1   ' \
                    + b'EA\x04\x00GCOD    E20 ' \
                    + b'EA\x04\x00GDEC    -4--' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    2   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D200'
        myFi = self._retFileSinglePr(myByFilm)
        myFc = FILMCfg.FilmCfgLISRead(LogiRec.LrTableRead(myFi))
        # Create a PRES table        
        myByPres = bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    SP\x00\x00'
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                # Weird LLIN entry
                + b'EA\x04\x00CODI    WTF '
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
        )
        myFi = self._retFileSinglePr(myByPres)
#        self._pclr = PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), myFc)
        # Should issue a warning here
        PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), myFc)
            
    def test_04(self):
        """TestPRESReadFail.test_04(): duplicate curve entry (should warn)."""
        # Create a film table, log and linear plots
        myByFilm = b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1   ' \
                    + b'EA\x04\x00GCOD    E20 ' \
                    + b'EA\x04\x00GDEC    -4--' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    2   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D200'
        myFi = self._retFileSinglePr(myByFilm)
        myFc = FILMCfg.FilmCfgLISRead(LogiRec.LrTableRead(myFi))
        # Create a PRES table        
        myByPres = bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    PRES'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    SP\x00\x00'
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    SP\x00\x00'
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
        )
        myFi = self._retFileSinglePr(myByPres)
#        self._pclr = PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), myFc)
        # Should issue a warning here
        PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), myFc)

    def test_05(self):
        """TestPRESReadFail.test_05(): bad PRES logical record type (raises)."""
        # Create a film table, log and linear plots
        myByFilm = b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1   ' \
                    + b'EA\x04\x00GCOD    E20 ' \
                    + b'EA\x04\x00GDEC    -4--' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    2   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D200'
        myFi = self._retFileSinglePr(myByFilm)
        myFc = FILMCfg.FilmCfgLISRead(LogiRec.LrTableRead(myFi))
        # Create a PRES table
        # Type 34 is '"', 32 is ' ', 39 is "'"
        myByPres = bytes(
            b' \x00'
            + b'IA\x04\x00TYPE    PRES'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    SP\x00\x00'
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    7   ' # Wrong!
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
        )
        myFi = self._retFileSinglePr(myByPres)
#        self._pclr = PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), myFc)
        self.assertRaises(PRESCfg.ExceptionPRESCfgLISRead, PRESCfg.PresCfgLISRead, LogiRec.LrTableRead(myFi), myFc)
            
    def test_06(self):
        """TestPRESReadFail.test_06(): not PRES table (raises)."""
        # Create a film table, log and linear plots
        myByFilm = b'"\x00' \
            + b'IA\x04\x00TYPE    FILM' \
                + b'\x00A\x04\x00MNEM    1   ' \
                    + b'EA\x04\x00GCOD    E20 ' \
                    + b'EA\x04\x00GDEC    -4--' \
                    + b'EA\x04\x00DEST    PF1 ' \
                    + b'EA\x04\x00DSCA    D200' \
                + b'\x00A\x04\x00MNEM    2   ' \
                    + b'EA\x04\x00GCOD    EEE ' \
                    + b'EA\x04\x00GDEC    ----' \
                    + b'EA\x04\x00DEST    PF2 ' \
                    + b'EA\x04\x00DSCA    D200'
        myFi = self._retFileSinglePr(myByFilm)
        myFc = FILMCfg.FilmCfgLISRead(LogiRec.LrTableRead(myFi))
        # Create a PRES table
        # Type 34 is '"', 32 is ' ', 39 is "'"
        myByPres = bytes(
            b'"\x00'
            + b'IA\x04\x00TYPE    WTF?'
            #SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
            + b'\x00A\x04\x00MNEM    SP\x00\x00'
                + b'EA\x04\x00OUTP    SP  '
                + b'EA\x04\x00STAT    ALLO'
                + b'EA\x04\x00TRAC    T1  '
                + b'EA\x04\x00CODI    LLIN'
                + b'EA\x04\x00DEST    1   '
                + b'EA\x04\x00MODE    SHIF'
                + b'ED\x04\x00FILT    ' + RepCode.writeBytes(0.5, 68)#@@\x00\x00'
                + b'ED\x04\x00LEDGMV  ' + RepCode.writeBytes(-80.0, 68)#\xbc0\x00\x00'
                + b'ED\x04\x00REDGMV  ' + RepCode.writeBytes(20.0, 68)#B\xd0\x00\x00'
        )
        myFi = self._retFileSinglePr(myByPres)
#        self._pclr = PRESCfg.PresCfgLISRead(LogiRec.LrTableRead(myFi), myFc)
        self.assertRaises(PRESCfg.ExceptionPRESCfgLISRead, PRESCfg.PresCfgLISRead, LogiRec.LrTableRead(myFi), myFc)

class TestPRESColour(BaseTestClasses.TestBaseFile):
    """Tests color from COLO attribute"""
    def setUp(self):
        """Set up."""
        pass
    
    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestPRESColo.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestPRESColo.test_01(): Mapping of COLO atribute by name."""
        self.assertEqual('black', PRESCfg.lisColo(Mnem.Mnem(b'BLAC')))
        self.assertEqual('aqua', PRESCfg.lisColo(Mnem.Mnem(b'AQUA')))
        self.assertEqual('blue', PRESCfg.lisColo(Mnem.Mnem(b'BLUE')))
        self.assertEqual('green', PRESCfg.lisColo(Mnem.Mnem(b'GREE')))
        self.assertEqual('red', PRESCfg.lisColo(Mnem.Mnem(b'RED')))

    def test_02(self):
        """TestPRESColo.test_02(): Mapping of COLO atribute by number."""
        self.assertEqual('rgb(0,0,0)', PRESCfg.lisColo(Mnem.Mnem(b'000')))
        self.assertEqual('rgb(255,255,255)', PRESCfg.lisColo(Mnem.Mnem(b'444')))
        
    def test_03(self):
        """TestPRESColo.test_03(): Replacement of Stroke."""
        myS = Stroke.StrokeBlackSolid
        myNewS = PRESCfg.coloStroke(myS, Mnem.Mnem(b'RED'))
        print()
        print('myS', myS, 'myNewS', myNewS)

class Special(unittest.TestCase):
    """Special tests."""
    pass


def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLineTrans))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPRESRead))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPRESReadMultiFilm))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPRESReadFail))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPRESColour))
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
    clkStart = time.perf_counter()
    unitTest()
    clkExec = time.perf_counter() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')

if __name__ == "__main__":
    main()
