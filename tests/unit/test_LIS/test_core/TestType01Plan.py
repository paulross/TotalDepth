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
"""Tests FramePlan for type 0/1 Logical Records.
"""
import pytest

__author__  = 'Paul Ross'
__date__    = '6 Jan 2011'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2011 Paul Ross. All rights reserved.'

import os
import sys
import time
import logging
import pprint

from TotalDepth.LIS.core import Type01Plan

######################
# Section: Unit tests.
######################
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import BaseTestClasses

# Mock classes
class MockEntryBlockSet(object):
    def __init__(self, recMode, rc):
        self.recordingMode = recMode
        self.depthRepCode = rc
        
class MockDsb(object):
    def __init__(self, s):
        self.size = s
        
class MockDFSR(object):
    def __init__(self, ebs, dsbS):
        self.ebs = ebs
        self.dsbBlocks = dsbS

class TestType01Plan(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestType01Plan: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestType01Plan.test_00(): Single channel, direct X axis."""
        myDfsr = MockDFSR(MockEntryBlockSet(0, None), [MockDsb(4), ])
        myTp = Type01Plan.FrameSetPlan(myDfsr)
        # Test numFrames()
        self.assertEqual(myTp.numFrames(1024), 256)
        self.assertRaises(Type01Plan.ExceptionFrameSetPlanNegLen, myTp.numFrames, -1024)
        self.assertRaises(Type01Plan.ExceptionFrameSetPlan, myTp.numFrames, 1023)
        # Test chOffset
        self.assertEqual(myTp.chOffset(ch=0, frame=0), 0)
        self.assertEqual(myTp.chOffset(ch=0, frame=1), 4)
        self.assertEqual(myTp.chOffset(ch=0, frame=2), 8)
        self.assertRaises(IndexError, myTp.chOffset, 0, 1)
        self.assertRaises(Type01Plan.ExceptionFrameSetPlanNegLen, myTp.chOffset, -1, 0)
        self.assertRaises(Type01Plan.ExceptionFrameSetPlanNegLen, myTp.chOffset, 0, -1)

    def test_01(self):
        """TestType01Plan.test_01(): Single channel, indirect X axis."""
        myDfsr = MockDFSR(MockEntryBlockSet(1, 68), [MockDsb(4), ])
        myTp = Type01Plan.FrameSetPlan(myDfsr)
        # Test numFrames()
        self.assertEqual(myTp.numFrames(8), 1)
        self.assertRaises(Type01Plan.ExceptionFrameSetPlanNegLen, myTp.numFrames, -1024)
        self.assertRaises(Type01Plan.ExceptionFrameSetPlan, myTp.numFrames, 1023)
        # Test chOffset
        self.assertEqual(myTp.chOffset(0, 0), 4)
        self.assertEqual(myTp.chOffset(ch=0, frame=1), 8)
        self.assertEqual(myTp.chOffset(ch=0, frame=2), 12)
        self.assertRaises(IndexError, myTp.chOffset, 0, 1)
        self.assertRaises(Type01Plan.ExceptionFrameSetPlanNegLen, myTp.chOffset, 0, -1)

    def test_02(self):
        """TestType01Plan.test_02(): Multiple channels, direct X axis."""
        myDfsr = MockDFSR(
            MockEntryBlockSet(0, None),
            [MockDsb(4), MockDsb(8), MockDsb(2), MockDsb(16), MockDsb(2)],
        )
        myTp = Type01Plan.FrameSetPlan(myDfsr)
        # 32
        self.assertEqual(myTp.frameSize, 4+8+2+16+2)
        # Test numFrames()
        self.assertEqual(myTp.numFrames(1024), 32)
        self.assertRaises(Type01Plan.ExceptionFrameSetPlanNegLen, myTp.numFrames, -1024)
        self.assertRaises(Type01Plan.ExceptionFrameSetPlan, myTp.numFrames, 1023)
        # Test chOffset
        self.assertEqual(myTp.chOffset(ch=0, frame=0), 0)
        self.assertEqual(myTp.chOffset(ch=0, frame=1), 32*1)
        self.assertEqual(myTp.chOffset(ch=0, frame=2), 32*2)
        self.assertEqual(myTp.chOffset(ch=1, frame=0), 4)
        self.assertEqual(myTp.chOffset(ch=1, frame=1), 4+32*1)
        self.assertEqual(myTp.chOffset(ch=1, frame=2), 4+32*2)
        self.assertEqual(myTp.chOffset(ch=2, frame=0), 12)
        self.assertEqual(myTp.chOffset(ch=2, frame=1), 12+32*1)
        self.assertEqual(myTp.chOffset(ch=2, frame=2), 12+32*2)
        self.assertEqual(myTp.chOffset(ch=3, frame=0), 14)
        self.assertEqual(myTp.chOffset(ch=3, frame=1), 14+32*1)
        self.assertEqual(myTp.chOffset(ch=3, frame=2), 14+32*2)
        self.assertEqual(myTp.chOffset(ch=4, frame=0), 30)
        self.assertEqual(myTp.chOffset(ch=4, frame=1), 30+32*1)
        self.assertEqual(myTp.chOffset(ch=4, frame=2), 30+32*2)
        self.assertRaises(IndexError, myTp.chOffset, 0, 5)
        self.assertRaises(Type01Plan.ExceptionFrameSetPlanNegLen, myTp.chOffset, 0, -1)
        # skipToEndOfFrame()
        self.assertEqual(myTp.skipToEndOfFrame(ch=0), 28)
        self.assertEqual(myTp.skipToEndOfFrame(ch=1), 20)
        self.assertEqual(myTp.skipToEndOfFrame(ch=2), 18)
        self.assertEqual(myTp.skipToEndOfFrame(ch=3), 2)
        self.assertEqual(myTp.skipToEndOfFrame(ch=4), 0)
        self.assertRaises(IndexError, myTp.skipToEndOfFrame, 5)
        self.assertRaises(Type01Plan.ExceptionFrameSetPlanNegLen, myTp.skipToEndOfFrame, -1)
        
    def test_03(self):
        """TestType01Plan.test_03(): Multiple channel, indirect X axis."""
        myDfsr = MockDFSR(
            MockEntryBlockSet(1, 73),
            [MockDsb(4), MockDsb(8), MockDsb(2), MockDsb(16), MockDsb(2)],
        )
        myTp = Type01Plan.FrameSetPlan(myDfsr)
        # 32
        self.assertEqual(myTp.frameSize, 4+8+2+16+2)
        # Test numFrames()
        self.assertEqual(myTp.numFrames(1028), 32)
        self.assertRaises(Type01Plan.ExceptionFrameSetPlanNegLen, myTp.numFrames, -1024)
        self.assertRaises(Type01Plan.ExceptionFrameSetPlan, myTp.numFrames, 1027)
        # Test chOffset
        self.assertEqual(myTp.chOffset(ch=0, frame=0), 4)
        self.assertEqual(myTp.chOffset(ch=0, frame=1), 4+32*1)
        self.assertEqual(myTp.chOffset(ch=0, frame=2), 4+32*2)
        self.assertEqual(myTp.chOffset(ch=1, frame=0), 8)
        self.assertEqual(myTp.chOffset(ch=1, frame=1), 8+32*1)
        self.assertEqual(myTp.chOffset(ch=1, frame=2), 8+32*2)
        self.assertEqual(myTp.chOffset(ch=2, frame=0), 16)
        self.assertEqual(myTp.chOffset(ch=2, frame=1), 16+32*1)
        self.assertEqual(myTp.chOffset(ch=2, frame=2), 16+32*2)
        self.assertEqual(myTp.chOffset(ch=3, frame=0), 18)
        self.assertEqual(myTp.chOffset(ch=3, frame=1), 18+32*1)
        self.assertEqual(myTp.chOffset(ch=3, frame=2), 18+32*2)
        self.assertEqual(myTp.chOffset(ch=4, frame=0), 34)
        self.assertEqual(myTp.chOffset(ch=4, frame=1), 34+32*1)
        self.assertEqual(myTp.chOffset(ch=4, frame=2), 34+32*2)
        self.assertRaises(IndexError, myTp.chOffset, 0, 5)
        self.assertRaises(Type01Plan.ExceptionFrameSetPlanNegLen, myTp.chOffset, 0, -1)
        # skipToEndOfFrame()
        self.assertEqual(myTp.skipToEndOfFrame(ch=0), 28)
        self.assertEqual(myTp.skipToEndOfFrame(ch=1), 20)
        self.assertEqual(myTp.skipToEndOfFrame(ch=2), 18)
        self.assertEqual(myTp.skipToEndOfFrame(ch=3), 2)
        self.assertEqual(myTp.skipToEndOfFrame(ch=4), 0)
        self.assertRaises(IndexError, myTp.skipToEndOfFrame, 5)
        self.assertRaises(Type01Plan.ExceptionFrameSetPlanNegLen, myTp.skipToEndOfFrame, -1)

    def test_04(self):
        """TestType01Plan.test_04(): Multiple channel, genOffsets()."""
        myDfsr = MockDFSR(
            MockEntryBlockSet(1, 73),
            [MockDsb(4), MockDsb(8), MockDsb(2), MockDsb(16), MockDsb(2)],
        )
        myTp = Type01Plan.FrameSetPlan(myDfsr)
        #print()
        myChS = [0, 2, 4]
        myOffS = [0, 12, 30]
        myG = myTp.genOffsets(myChS)
        for myF in range(4):
            for myCidx in range(len(myChS)):
                myTuple = next(myG)
                #print(myTuple)
                self.assertEqual(myTuple, (myF, myChS[myCidx], 4+myOffS[myCidx]+32*myF))
        myG.close()            
        
    def test_05(self):
        """TestType01Plan.test_05(): Multiple channel, genOffsets() unsorted."""
        myDfsr = MockDFSR(
            MockEntryBlockSet(1, 73),
            [MockDsb(4), MockDsb(8), MockDsb(2), MockDsb(16), MockDsb(2)],
        )
        myTp = Type01Plan.FrameSetPlan(myDfsr)
        myOrigChS = [0, 4, 2]
        myChS = sorted(myOrigChS)
        myOffS = [0, 12, 30]
        myG = myTp.genOffsets(myOrigChS)
        for myF in range(4):
            for myCidx in range(len(myChS)):
                myTuple = next(myG)
                #print(myTuple)
                self.assertEqual(myTuple, (myF, myChS[myCidx], 4+myOffS[myCidx]+32*myF))
        myG.close()            

    def test_06(self):
        """TestType01Plan.test_06(): Multiple channel, genOffsets() failures."""
        myDfsr = MockDFSR(
            MockEntryBlockSet(1, 73),
            [MockDsb(4), MockDsb(8), MockDsb(2), MockDsb(16), MockDsb(2)],
        )
        myTp = Type01Plan.FrameSetPlan(myDfsr)
        myG = myTp.genOffsets([-1, 1, 2])
        #print('There')
        try:
            next(myG)
            self.fail('Type01Plan.ExceptionFrameSetPlanNegLen not raised.')
        except Type01Plan.ExceptionFrameSetPlanNegLen:
            pass
        myG.close()
        
    def test_07(self):
        """TestType01Plan.test_07(): Multiple channels, __str__()."""
        myDfsr = MockDFSR(
            MockEntryBlockSet(1, 73),
            [MockDsb(4), MockDsb(8), MockDsb(2), MockDsb(16), MockDsb(2)],
        )
        myTp = Type01Plan.FrameSetPlan(myDfsr)
        print()
        print(str(myTp))

    def test_10(self):
        """TestType01Plan.test_10(): _checkChIdx()."""
        myDfsr = MockDFSR(
            MockEntryBlockSet(1, 73),
            [MockDsb(4), MockDsb(8), MockDsb(2), MockDsb(16), MockDsb(2)],
        )
        myTp = Type01Plan.FrameSetPlan(myDfsr)
        self.assertEqual(myTp._checkChIdx([3, 1, 2]), [1,2,3])
        self.assertRaises(Type01Plan.ExceptionFrameSetPlanNegLen, myTp._checkChIdx, [-1, 2])
        self.assertRaises(Type01Plan.ExceptionFrameSetPlanOverrun, myTp._checkChIdx, [1, 7])

    def test_11(self):
        """TestType01Plan.test_11(): _checkChIdx() two channels."""
        myDfsr = MockDFSR(
            MockEntryBlockSet(1, 73),
            [MockDsb(4), MockDsb(4)],
        )
        myTp = Type01Plan.FrameSetPlan(myDfsr)
        self.assertEqual(myTp._checkChIdx([1, 0]), [0,1])
        self.assertRaises(Type01Plan.ExceptionFrameSetPlanNegLen, myTp._checkChIdx, [-1, 1])
        self.assertRaises(Type01Plan.ExceptionFrameSetPlanOverrun, myTp._checkChIdx, [1, 2])


class TestType01PlanGenEvents_LowLevel(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        self._dfsr = MockDFSR(
            MockEntryBlockSet(0, 73),
            [MockDsb(4), MockDsb(8), MockDsb(2), MockDsb(16), MockDsb(2)],
        )
        self._tp = Type01Plan.FrameSetPlan(self._dfsr)
        # 4+8+2+16+2=32
        self.assertEqual(self._tp.frameSize, 4+8+2+16+2)

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestType01PlanGenEvents_LowLevel: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestType01PlanGenEvents_LowLevel.test_00(): Single channel[0], _retFrameEvents()."""
        expList = (
            None,
            [(Type01Plan.EVENT_READ, 4, 0, 0),],
            ('skip', 28, 1, 4),
        )
        actList = self._tp._retFrameEvents([0, ])
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_01(self):
        """TestType01PlanGenEvents_LowLevel.test_01(): Single channel[2], _retFrameEvents()."""
        expList = (
            ('skip', 12, 0, 1),
            [(Type01Plan.EVENT_READ, 2, 2, 2),],
            ('skip', 18, 3, 4),
        )
        actList = self._tp._retFrameEvents([2, ])
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_02(self):
        """TestType01PlanGenEvents_LowLevel.test_02(): Single channel[4], _retFrameEvents()."""
        expList = (
            ('skip', 30, 0, 3),
            [(Type01Plan.EVENT_READ, 2, 4, 4),],
            None,
        )
        actList = self._tp._retFrameEvents([4, ])
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_10(self):
        """TestType01PlanGenEvents_LowLevel.test_10(): Two channels[1,3], _retFrameEvents()."""
        expList = (
            ('skip', 4, 0, 0),
            [
                (Type01Plan.EVENT_READ, 8, 1, 1),
                ('skip', 2, 2, 2),
                (Type01Plan.EVENT_READ, 16, 3, 3),
            ],
            ('skip', 2, 4, 4),
        )
        actList = self._tp._retFrameEvents([1,3])
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_11(self):
        """TestType01PlanGenEvents_LowLevel.test_11(): Two channels[1,2], _retFrameEvents()."""
        expList = (
            ('skip', 4, 0, 0),
            [(Type01Plan.EVENT_READ, 10, 1, 2),],
            ('skip', 18, 3, 4),
        )
        actList = self._tp._retFrameEvents([1,2])
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_12(self):
        """TestType01PlanGenEvents_LowLevel.test_12(): Two channels[0,4], _retFrameEvents()."""
        expList = (
            None, 
            [
                (Type01Plan.EVENT_READ, 4, 0, 0),
                ('skip', 26, 1, 3),
                (Type01Plan.EVENT_READ, 2, 4, 4),
            ],
            None,
        )
        actList = self._tp._retFrameEvents([0,4])
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_20(self):
        """TestType01PlanGenEvents_LowLevel.test_20(): All channels[0,1,2,3,4], _retFrameEvents()."""
        expList = (
            None, 
            [(Type01Plan.EVENT_READ, 32, 0, 4),],
            None,
        )
        actList = self._tp._retFrameEvents([0,1,2,3,4])
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_50(self):
        """TestType01PlanGenEvents_LowLevel.test_20(): Single channel[0,], _retMergedPostFramePre()."""
        pre, eventS, post = self._tp._retFrameEvents([0,])
        #print()
        #print('_retMergedPostFramePre(1)', self._tp._retMergedPostFramePre(pre, post, 1))
        #print('_retMergedPostFramePre(4)', self._tp._retMergedPostFramePre(pre, post, 4))
        self.assertTrue(pre is None)
        self.assertEqual([(Type01Plan.EVENT_READ, 4, 0, 0),], eventS)
        self.assertEqual(post, (Type01Plan.EVENT_SKIP, 28, 1, 4))
        self.assertEqual(
            (Type01Plan.EVENT_SKIP, 28, 1, 4),
            self._tp._retMergedPostFramePre(pre, post, 1),
        )
        self.assertEqual(
            (Type01Plan.EVENT_SKIP, 28+32, 1, 4),
            self._tp._retMergedPostFramePre(pre, post, 2),
        )
        self.assertEqual(
            (Type01Plan.EVENT_SKIP, 28+2*32, 1, 4),
            self._tp._retMergedPostFramePre(pre, post, 3),
        )
        self.assertEqual(
            (Type01Plan.EVENT_SKIP, 28+3*32, 1, 4),
            self._tp._retMergedPostFramePre(pre, post, 4),
        )

    def test_51(self):
        """TestType01PlanGenEvents_LowLevel.test_20(): Single channel[2,], _retMergedPostFramePre()."""
        pre, eventS, post = self._tp._retFrameEvents([2,])
        #print()
        #print('_retFrameEvents([2,]', pre, eventS, post)
        #print('_retMergedPostFramePre(1)', self._tp._retMergedPostFramePre(pre, post, 1))
        #print('_retMergedPostFramePre(4)', self._tp._retMergedPostFramePre(pre, post, 4))
        self.assertEqual(
            (Type01Plan.EVENT_SKIP, 30, 3, 1),
            self._tp._retMergedPostFramePre(pre, post, 1),
        )
        self.assertEqual(
            (Type01Plan.EVENT_SKIP, 30+32, 3, 1),
            self._tp._retMergedPostFramePre(pre, post, 2),
        )
        self.assertEqual(
            (Type01Plan.EVENT_SKIP, 30+2*32, 3, 1),
            self._tp._retMergedPostFramePre(pre, post, 3),
        )
        self.assertEqual(
            (Type01Plan.EVENT_SKIP, 30+3*32, 3, 1),
            self._tp._retMergedPostFramePre(pre, post, 4),
        )

class TestType01PlanGenEvents(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        self._dfsr = MockDFSR(
            MockEntryBlockSet(0, 73),
            [MockDsb(4), MockDsb(8), MockDsb(2), MockDsb(16), MockDsb(2)],
        )
        self._tp = Type01Plan.FrameSetPlan(self._dfsr)
        # 4+8+2+16+2=32
        self.assertEqual(self._tp.frameSize, 4+8+2+16+2)

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestType01PlanGenEvents: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestType01PlanGenEvents.test_00(): Single channel[0], genEvents()."""
        expList = [
            (Type01Plan.EVENT_READ, 4,  0, 0, 0),
            (Type01Plan.EVENT_SKIP, 28, 1, 1, 4),
            (Type01Plan.EVENT_READ, 4,  1, 0, 0),
            (Type01Plan.EVENT_SKIP, 28, 2, 1, 4),
            (Type01Plan.EVENT_READ, 4,  2, 0, 0),
            (Type01Plan.EVENT_SKIP, 28, 3, 1, 4),
            (Type01Plan.EVENT_READ, 4,  3, 0, 0),
            (Type01Plan.EVENT_SKIP, 28, 3, 1, 4),
        ]
        actList = [e for e in self._tp.genEvents(slice(4), [0, ])]
        #print()
        #pre, lst, post = self._tp._retFrameEvents([0,])
        #print('_retFrameEvents()', pre, lst, post)
        #print('_retMergedPostFramePre()', self._tp._retMergedPostFramePre(pre, post, 1))
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)


    def test_01(self):
        """TestType01PlanGenEvents.test_01(): All channels, genEvents()."""
        expList = [
            (Type01Plan.EVENT_READ, 32, 0, 0, 4),
            (Type01Plan.EVENT_READ, 32, 1, 0, 4),
            (Type01Plan.EVENT_READ, 32, 2, 0, 4),
            (Type01Plan.EVENT_READ, 32, 3, 0, 4),
        ]
        actList = [e for e in self._tp.genEvents(slice(4), list(range(5)))]
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_02(self):
        """TestType01PlanGenEvents.test_02(): Single channel[2], genEvents()."""
        expList = [
            (Type01Plan.EVENT_SKIP, 12, 0, 0, 1),
            (Type01Plan.EVENT_READ, 2,  0, 2, 2),
            (Type01Plan.EVENT_SKIP, 30, 1, 3, 1),
            (Type01Plan.EVENT_READ, 2,  1, 2, 2),
            (Type01Plan.EVENT_SKIP, 30, 2, 3, 1),
            (Type01Plan.EVENT_READ, 2,  2, 2, 2),
            (Type01Plan.EVENT_SKIP, 30, 3, 3, 1),
            (Type01Plan.EVENT_READ, 2,  3, 2, 2),
            (Type01Plan.EVENT_SKIP, 18, 3, 3, 4),
        ]
        actList = [e for e in self._tp.genEvents(slice(4), [2, ])]
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_03(self):
        """TestType01PlanGenEvents.test_03(): Single channel[0], genEvents() frame slice(3, 7, 2)."""
        expList = [
            (Type01Plan.EVENT_SKIP, 96, 3, None, 0),
            (Type01Plan.EVENT_READ, 4,  3, 0, 0),
            (Type01Plan.EVENT_SKIP, 60, 5, 1, 4),
            (Type01Plan.EVENT_READ, 4,  5, 0, 0),
            (Type01Plan.EVENT_SKIP, 28, 5, 1, 4),
        ]
        actList = [e for e in self._tp.genEvents(slice(3, 7, 2), [0, ])]
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_04(self):
        """TestType01PlanGenEvents.test_04(): Single channel[2], genEvents() frame slice(3, 7, 2)."""
        expList = [
            (Type01Plan.EVENT_SKIP, 108, 3, 0, 1),
            (Type01Plan.EVENT_READ, 2,  3, 2, 2),
            (Type01Plan.EVENT_SKIP, 62, 5, 3, 1),
            (Type01Plan.EVENT_READ, 2,  5, 2, 2),
            (Type01Plan.EVENT_SKIP, 18, 5, 3, 4),
        ]
        actList = [e for e in self._tp.genEvents(slice(3, 7, 2), [2, ])]
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

class TestType01PlanGenEventsIndirect(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        self._dfsr = MockDFSR(
            MockEntryBlockSet(1, 73),
            [MockDsb(4), MockDsb(8), MockDsb(2), MockDsb(16), MockDsb(2)],
        )
        self._tp = Type01Plan.FrameSetPlan(self._dfsr)
        # 4+8+2+16+2=32
        self.assertEqual(self._tp.frameSize, 4+8+2+16+2)

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestType01PlanGenEventsIndirect: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestType01PlanGenEventsIndirect.test_00(): Single channel[0], genEvents()."""
        expList = [
            (Type01Plan.EVENT_READ,         8,      0,  None,   0),
            (Type01Plan.EVENT_SKIP,         28,     1,  1,      4),
            (Type01Plan.EVENT_EXTRAPOLATE,  1,      1,  None,   None),
            (Type01Plan.EVENT_READ,         4,      1,  0,      0),
            (Type01Plan.EVENT_SKIP,         28,     2,  1,      4),
            (Type01Plan.EVENT_EXTRAPOLATE,  1,      2,  None,   None),
            (Type01Plan.EVENT_READ,         4,      2,  0,      0),
            (Type01Plan.EVENT_SKIP,         28,     3,  1,      4),
            (Type01Plan.EVENT_EXTRAPOLATE,  1,      3,  None,   None),
            (Type01Plan.EVENT_READ,         4,      3,  0,      0),
            (Type01Plan.EVENT_SKIP,         28,     3,  1,      4),
        ]
        actList = [e for e in self._tp.genEvents(slice(4), [0, ])]
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_01(self):
        """TestType01PlanGenEventsIndirect.test_01(): Single channel[2], genEvents()."""
        expList = [
            (Type01Plan.EVENT_READ,         4,      None,  None,   None),
            (Type01Plan.EVENT_SKIP,         12,     0,  0,      1),
            (Type01Plan.EVENT_READ,         2,      0,  2,      2),
            (Type01Plan.EVENT_SKIP,         30,     1,  3,      1),
            (Type01Plan.EVENT_EXTRAPOLATE,  1,      1,  None,   None),
            (Type01Plan.EVENT_READ,         2,      1,  2,      2),
            (Type01Plan.EVENT_SKIP,         30,     2,  3,      1),
            (Type01Plan.EVENT_EXTRAPOLATE,  1,      2,  None,   None),
            (Type01Plan.EVENT_READ,         2,      2,  2,      2),
            (Type01Plan.EVENT_SKIP,         30,     3,  3,      1),
            (Type01Plan.EVENT_EXTRAPOLATE,  1,      3,  None,   None),
            (Type01Plan.EVENT_READ,         2,      3,  2,      2),
            (Type01Plan.EVENT_SKIP,         18,     3,  3,      4),
        ]
        actList = [e for e in self._tp.genEvents(slice(4), [2, ])]
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_02(self):
        """TestType01PlanGenEventsIndirect.test_02(): Single channel[4], genEvents()."""
        expList = [
            (Type01Plan.EVENT_READ,         4,      None,  None,   None),
            (Type01Plan.EVENT_SKIP,         30,     0,  0,      3),
            (Type01Plan.EVENT_READ,         2,      0,  4,      4),
            (Type01Plan.EVENT_SKIP,         30,     1,  0,      3),
            (Type01Plan.EVENT_EXTRAPOLATE,  1,      1,  None,   None),
            (Type01Plan.EVENT_READ,         2,      1,  4,      4),
            (Type01Plan.EVENT_SKIP,         30,     2,  0,      3),
            (Type01Plan.EVENT_EXTRAPOLATE,  1,      2,  None,   None),
            (Type01Plan.EVENT_READ,         2,      2,  4,      4),
            (Type01Plan.EVENT_SKIP,         30,     3,  0,      3),
            (Type01Plan.EVENT_EXTRAPOLATE,  1,      3,  None,   None),
            (Type01Plan.EVENT_READ,         2,      3,  4,      4),
        ]
        actList = [e for e in self._tp.genEvents(slice(4), [4, ])]
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_03(self):
        """TestType01PlanGenEventsIndirect.test_03(): All channels (unsorted), genEvents()."""
        expList = [
            (Type01Plan.EVENT_READ,         36,     0,  None,   4),
            (Type01Plan.EVENT_EXTRAPOLATE,  1,      1,  None,   None),
            (Type01Plan.EVENT_READ,         32,     1,  0,      4),
            (Type01Plan.EVENT_EXTRAPOLATE,  1,      2,  None,   None),
            (Type01Plan.EVENT_READ,         32,     2,  0,      4),
            (Type01Plan.EVENT_EXTRAPOLATE,  1,      3,  None,   None),
            (Type01Plan.EVENT_READ,         32,     3,  0,      4),
        ]
        actList = [e for e in self._tp.genEvents(slice(4), [0,3,1,2,4])]
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_04(self):
        """TestType01PlanGenEventsIndirect.test_04(): Two channels[1,3], genEvents(), slice(2, 14, 3)."""
        # First seek is 2*32 + 4 = 68
        # Then 8/2/16
        # Skip is 2 + 2*32 + 4 = 70
        expList = [
            (Type01Plan.EVENT_READ,         4,      None,  None,   None),
            (Type01Plan.EVENT_EXTRAPOLATE,  2,      2,  None,   None),
            (Type01Plan.EVENT_SKIP,         68,     2,  0,      0),
            (Type01Plan.EVENT_READ,         8,      2,  1,      1),
            (Type01Plan.EVENT_SKIP,         2,      2,  2,      2),
            (Type01Plan.EVENT_READ,         16,     2,  3,      3),
            (Type01Plan.EVENT_SKIP,         70,     5,  4,      0),
            (Type01Plan.EVENT_EXTRAPOLATE,  3,      5,  None,   None),
            (Type01Plan.EVENT_READ,         8,      5,  1,      1),
            (Type01Plan.EVENT_SKIP,         2,      5,  2,      2),
            (Type01Plan.EVENT_READ,         16,     5,  3,      3),
            (Type01Plan.EVENT_SKIP,         70,     8,  4,      0),
            (Type01Plan.EVENT_EXTRAPOLATE,  3,      8,  None,   None),
            (Type01Plan.EVENT_READ,         8,      8,  1,      1),
            (Type01Plan.EVENT_SKIP,         2,      8,  2,      2),
            (Type01Plan.EVENT_READ,         16,     8,  3,      3),
            (Type01Plan.EVENT_SKIP,         70,     11, 4,      0),
            (Type01Plan.EVENT_EXTRAPOLATE,  3,      11, None,   None),
            (Type01Plan.EVENT_READ,         8,      11, 1,      1),
            (Type01Plan.EVENT_SKIP,         2,      11, 2,      2),
            (Type01Plan.EVENT_READ,         16,     11, 3,      3),
            (Type01Plan.EVENT_SKIP,         2,      11, 4,      4),
        ]
        actList = [e for e in self._tp.genEvents(slice(2, 14, 3), [1, 3])]
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_05(self):
        """TestType01PlanGenEventsIndirect.test_05(): Single channel[0,], genEvents(), slice(2, 14, 3)."""
        actList = [e for e in self._tp.genEvents(slice(2, 14, 3), [0,])]
        expList = [
            (Type01Plan.EVENT_READ,         4,      None,  None,   None),
            (Type01Plan.EVENT_SKIP,         64,     2,  None,   0),
            (Type01Plan.EVENT_EXTRAPOLATE,  2,      2,  None,   None),
            (Type01Plan.EVENT_READ,         4,      2,  0,      0),
            (Type01Plan.EVENT_SKIP,         92,     5,  1,      4),
            (Type01Plan.EVENT_EXTRAPOLATE,  3,      5,  None,   None),
            (Type01Plan.EVENT_READ,         4,      5,  0,      0),
            (Type01Plan.EVENT_SKIP,         92,     8,  1,      4),
            (Type01Plan.EVENT_EXTRAPOLATE,  3,      8,  None,   None),
            (Type01Plan.EVENT_READ,         4,      8,  0,      0),
            (Type01Plan.EVENT_SKIP,         92,     11, 1,      4),
            (Type01Plan.EVENT_EXTRAPOLATE,  3,      11, None,   None),
            (Type01Plan.EVENT_READ,         4,      11, 0,      0),
            (Type01Plan.EVENT_SKIP,         28,     11, 1,      4),
        ]
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_06(self):
        """TestType01PlanGenEventsIndirect.test_06(): Two channels[0,4], genEvents(), slice(2, 9, 3)."""
        actList = [e for e in self._tp.genEvents(slice(2, 9, 3), [0, 4])]
        expList = [
            (Type01Plan.EVENT_READ,         4,      None,  None,   None),
            (Type01Plan.EVENT_SKIP,         64,     2,  None,      0),
            (Type01Plan.EVENT_EXTRAPOLATE,  2,      2,  None,   None),
            (Type01Plan.EVENT_READ,         4,      2,  0,      0),
            (Type01Plan.EVENT_SKIP,         26,     2,  1,      3),
            (Type01Plan.EVENT_READ,         2,      2,  4,      4),
            (Type01Plan.EVENT_SKIP,         64,     5,  None,   None),
            (Type01Plan.EVENT_EXTRAPOLATE,  3,      5,  None,   None),
            (Type01Plan.EVENT_READ,         4,      5,  0,      0),
            (Type01Plan.EVENT_SKIP,         26,     5,  1,      3),
            (Type01Plan.EVENT_READ,         2,      5,  4,      4),
            (Type01Plan.EVENT_SKIP,         64,     8,  None,   None),
            (Type01Plan.EVENT_EXTRAPOLATE,  3,      8,  None,   None),
            (Type01Plan.EVENT_READ,         4,      8,  0,      0),
            (Type01Plan.EVENT_SKIP,         26,     8,  1,      3),
            (Type01Plan.EVENT_READ,         2,      8,  4,      4),
        ]
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_10(self):
        """TestType01PlanGenEventsIndirect.test_10(): genEvents() failures."""
        try:
            actList = [e for e in self._tp.genEvents(slice(-1), [1, 3])]
            self.fail('Type01Plan.ExceptionFrameSetPlanNegLen not raised in negative slice stop')
        except Type01Plan.ExceptionFrameSetPlanNegLen:
            pass
        try:
            actList = [e for e in self._tp.genEvents(slice(-1, 3), [1, 3])]
            self.fail('Type01Plan.ExceptionFrameSetPlanNegLen not raised in negative slice start')
        except Type01Plan.ExceptionFrameSetPlanNegLen:
            pass
        try:
            # Note: slice(1, 3, 0) and slice(1, 3, None) are interpreted as slice(1, 3, 1)
            actList = [e for e in self._tp.genEvents(slice(1, 3, -1), [1, 3])]
            self.fail('Type01Plan.ExceptionFrameSetPlanNegLen not raised in slice step < 0')
        except Type01Plan.ExceptionFrameSetPlanNegLen:
            pass

    def test_20(self):
        """TestType01PlanGenEventsIndirect.test_20(): Single frame (2), all channels, genEvents()."""
        expList = [
            # Read indirect X
            (Type01Plan.EVENT_READ,         4,      None,  None,   None),
            # Skip two frames [0, 1]
            (Type01Plan.EVENT_SKIP,         64,     2,  None,   0),
            # Extrapolate two frames of X axis data [0, 1]
            (Type01Plan.EVENT_EXTRAPOLATE,  2,      2,  None,   None),
            # Read all of the next frame [2] as internal frame 1
            (Type01Plan.EVENT_READ,         32,     2,  0,      4),
        ]
        actList = [e for e in self._tp.genEvents(slice(2,4,2), list(range(5)))]
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)

    def test_21(self):
        """TestType01PlanGenEventsIndirect.test_20(): Single frame (4), all channels, genEvents()."""
        expList = [
            # Read indirect X
            (Type01Plan.EVENT_READ,         4,      None,  None,   None),
            # Skip four frames [0, 1, 2, 3]
            (Type01Plan.EVENT_SKIP,         128,    4,  None,   0),
            # Extrapolate four frames of X axis data [0, 1, 2, 3]
            (Type01Plan.EVENT_EXTRAPOLATE,  4,      4,  None,   None),
            # Read all of the next frame [4] as frame 1
            (Type01Plan.EVENT_READ,         32,     4,  0,      4),
        ]
        actList = [e for e in self._tp.genEvents(slice(4,8,4), list(range(5)))]
        #print()
        #pprint.pprint(actList)
        self.assertEqual(expList, actList)


class TestType01Plan_PerfBase(BaseTestClasses.TestBase):
    """Tests ..."""
    def _timeEvents(self, theFrameSlice, theChRange):
        """Time genEvents() from frame slice and channel range."""
        myDfsr = MockDFSR(
            MockEntryBlockSet(0, 73),
            [MockDsb(4) for i in range(8192)],
        )
        myTp = Type01Plan.FrameSetPlan(myDfsr)
        self.assertEqual(myTp.frameSize, 4*8192)
        myReadSize = 0
        numEvents = 0
        start = time.perf_counter()
        for e in myTp.genEvents(theFrameSlice, theChRange):
            if e[0] == Type01Plan.EVENT_READ:
                myReadSize += e[1]
            numEvents += 1
        self.writeCostToStderr(start, myReadSize, 'Events', numEvents)


@pytest.mark.slow
class TestType01Plan_Perf(TestType01Plan_PerfBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestType01Plan_Perf: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestType01Plan_Perf.test_00(): Construction, 8192 channels."""
        myDfsr = MockDFSR(
            MockEntryBlockSet(0, 73),
            [MockDsb(4) for i in range(8192)],
        )
        start = time.perf_counter()
        myTp = Type01Plan.FrameSetPlan(myDfsr)
        execTime = time.perf_counter() - start
        self.assertEqual(myTp.frameSize, 4*8192)
        sys.stderr.write(' Time: {:.3f} (s)'.format(execTime))
        #sys.stderr.write(' Rate: {:.3f} (MB/s)'.format(myReadSize /(1024*1024*execTime)))
        sys.stderr.write(' Cost (on frame size): {:.3f} (ms/MB)'.format((execTime*1024)/(myTp.frameSize/(1024*1024))))
        sys.stderr.write(' ')
        
    def test_01(self):
        """TestType01Plan_Perf.test_01(): Frames: 1024, Ch: 8192 step 1."""
        self._timeEvents(slice(0,1024,1), range(0, 8192, 1))

    def test_02(self):
        """TestType01Plan_Perf.test_02(): Frames: 1024, Ch: 8192 step 2."""
        self._timeEvents(slice(0,1024,1), range(0, 8192, 2))

    def test_03(self):
        """TestType01Plan_Perf.test_03(): Frames: 1024, Ch: 8192 step 4."""
        self._timeEvents(slice(0,1024,1), range(0, 8192, 4))

    def test_04(self):
        """TestType01Plan_Perf.test_04(): Frames: 1024, Ch: 8192 step 8."""
        self._timeEvents(slice(0,1024,1), range(0, 8192, 8))

    def test_05(self):
        """TestType01Plan_Perf.test_05(): Frames: 1024, Ch: 8192 step 16."""
        self._timeEvents(slice(0,1024,1), range(0, 8192, 16))

    def test_06(self):
        """TestType01Plan_Perf.test_06(): Frames: 1024, Ch: 8192 step 32."""
        self._timeEvents(slice(0,1024,1), range(0, 8192, 32))

    def test_07(self):
        """TestType01Plan_Perf.test_07(): Frames: 1024, Ch: 8192 step 64."""
        self._timeEvents(slice(0,1024,1), range(0, 8192, 64))

    def test_08(self):
        """TestType01Plan_Perf.test_08(): Frames: 1024, Ch: 8192 step 128."""
        self._timeEvents(slice(0,1024,1), range(0, 8192, 128))

    def test_09(self):
        """TestType01Plan_Perf.test_09(): Frames: 1024, Ch: 8192 step 256."""
        self._timeEvents(slice(0,1024,1), range(0, 8192, 256))

    def test_10(self):
        """TestType01Plan_Perf.test_10(): Frames: 1024, Ch: 8192 step 512."""
        self._timeEvents(slice(0,1024,1), range(0, 8192, 512))

    def test_11(self):
        """TestType01Plan_Perf.test_11(): Frames: 1024, Ch: 8192 step 1024."""
        self._timeEvents(slice(0,1024,1), range(0, 8192, 1024))

    def test_20(self):
        """TestType01Plan_Perf.test_20(): Frames: 1024 step 1, Ch: 8192 step 1."""
        self._timeEvents(slice(0,1024,1), range(0, 8192, 1))

    def test_21(self):
        """TestType01Plan_Perf.test_21(): Frames: 1024 step 2, Ch: 8192 step 1."""
        self._timeEvents(slice(0,1024,2), range(0, 8192, 1))

    def test_22(self):
        """TestType01Plan_Perf.test_22(): Frames: 1024 step 4, Ch: 8192 step 1."""
        self._timeEvents(slice(0,1024,4), range(0, 8192, 1))

    def test_23(self):
        """TestType01Plan_Perf.test_23(): Frames: 1024 step 8, Ch: 8192 step 1."""
        self._timeEvents(slice(0,1024,8), range(0, 8192, 1))

    def test_24(self):
        """TestType01Plan_Perf.test_24(): Frames: 1024 step 16, Ch: 8192 step 1."""
        self._timeEvents(slice(0,1024,16), range(0, 8192, 1))

    def test_25(self):
        """TestType01Plan_Perf.test_25(): Frames: 1024 step 32, Ch: 8192 step 1."""
        self._timeEvents(slice(0,1024,32), range(0, 8192, 1))

    def test_26(self):
        """TestType01Plan_Perf.test_26(): Frames: 1024 step 64, Ch: 8192 step 1."""
        self._timeEvents(slice(0,1024,64), range(0, 8192, 1))

    def test_27(self):
        """TestType01Plan_Perf.test_27(): Frames: 1024 step 128, Ch: 8192 step 1."""
        self._timeEvents(slice(0,1024,128), range(0, 8192, 1))

    def test_28(self):
        """TestType01Plan_Perf.test_28(): Frames: 1024 step 256, Ch: 8192 step 1."""
        self._timeEvents(slice(0,1024,256), range(0, 8192, 1))

    def test_29(self):
        """TestType01Plan_Perf.test_29(): Frames: 1024 step 512, Ch: 8192 step 1."""
        self._timeEvents(slice(0,1024,512), range(0, 8192, 1))

    def test_30(self):
        """TestType01Plan_Perf.test_30(): Frames: 1024 step 1, Ch: 8192 step 4."""
        self._timeEvents(slice(0,1024,1), range(0, 8192, 4))

    def test_31(self):
        """TestType01Plan_Perf.test_31(): Frames: 1024 step 2, Ch: 8192 step 4."""
        self._timeEvents(slice(0,1024,2), range(0, 8192, 4))

    def test_32(self):
        """TestType01Plan_Perf.test_32(): Frames: 1024 step 4, Ch: 8192 step 4."""
        self._timeEvents(slice(0,1024,4), range(0, 8192, 4))

    def test_33(self):
        """TestType01Plan_Perf.test_33(): Frames: 1024 step 8, Ch: 8192 step 4."""
        self._timeEvents(slice(0,1024,8), range(0, 8192, 4))

    def test_34(self):
        """TestType01Plan_Perf.test_34(): Frames: 1024 step 16, Ch: 8192 step 4."""
        self._timeEvents(slice(0,1024,16), range(0, 8192, 4))

    def test_35(self):
        """TestType01Plan_Perf.test_35(): Frames: 1024 step 32, Ch: 8192 step 4."""
        self._timeEvents(slice(0,1024,32), range(0, 8192, 4))

    def test_36(self):
        """TestType01Plan_Perf.test_36(): Frames: 1024 step 64, Ch: 8192 step 4."""
        self._timeEvents(slice(0,1024,64), range(0, 8192, 4))

    def test_37(self):
        """TestType01Plan_Perf.test_37(): Frames: 1024 step 128, Ch: 8192 step 4."""
        self._timeEvents(slice(0,1024,128), range(0, 8192, 4))

    def test_38(self):
        """TestType01Plan_Perf.test_38(): Frames: 1024 step 256, Ch: 8192 step 4."""
        self._timeEvents(slice(0,1024,256), range(0, 8192, 4))

    def test_39(self):
        """TestType01Plan_Perf.test_39(): Frames: 1024 step 512, Ch: 8192 step 4."""
        self._timeEvents(slice(0,1024,512), range(0, 8192, 4))

    def test_40(self):
        """TestType01Plan_Perf.test_40(): Frames: 1024 step 16, Ch: 8192 step 16."""
        self._timeEvents(slice(0, 1024, 16), range(0, 8192, 16))


@pytest.mark.slow
class TestType01Plan_Perf_Profile(TestType01Plan_PerfBase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestType01Plan_Perf: Tests setUp() and tearDown()."""
        pass

    def test_02(self):
        """TestType01Plan_Perf.test_02(): Frames: 1024, Ch: 8192 step 2."""
        self._timeEvents(slice(0,1024,1), range(0, 8192, 2))

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestType01Plan))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestType01PlanGenEvents_LowLevel))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestType01PlanGenEvents))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestType01PlanGenEventsIndirect))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestType01Plan_Perf))
    #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestType01Plan_Perf_Profile))
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
