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
"""Maintains a heap like object that resembles a Swiss Cheese

Created on 28 Mar 2011

@author: p2ross
"""

__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

import time
import sys
import logging
import collections
from optparse import OptionParser

from TotalDepth.LIS import ExceptionTotalDepthLIS

class ExceptionSCHeap(ExceptionTotalDepthLIS):
    """Exception specialisation for the SCHeap module."""
    pass

Block = collections.namedtuple('Block', 'start, stop')

class SCHeap(object):
    def __init__(self):
        # List of Block objects kept in sorted order
        self._l = []
        
    def __len__(self):
        return len(self._l)
    
    def __str__(self):
        if len(self._l) > 0:
            return 'SCHeap: [{:s}]'.format(', '.join([str(v) for v in self._l]))
        return 'SCHeap:'
    
    def clear(self):
        """Remove all entries."""
        self._l = []
    
    def genBlocks(self):
        """Yields (bool, Block). bool is True if this is a full block,
        False if empty."""
        for i, b in enumerate(self._l):
            # Yield gap before this block
            if i == 0:
                if b.start > 0:
                    yield False, Block(0, b.start)
            else:
                if b.start > self._l[i-1].stop:
                    yield False, Block(self._l[i-1].stop, b.start)
            # Yield block
            yield True, b
        
    def _raiseOnError(self, start, stop):
        if start < 0:
            raise ExceptionSCHeap('ScHeap: start {:d} negative'.format(start))
        if stop <= start:
            raise ExceptionSCHeap('ScHeap: end {:d} <= than start {:d}'.format(stop, start))
    
    def retIdx(self, v):
        """Returns the lowest index of the IR that start is >= than v."""
        if len(self._l) == 0:
            return 1
        b = 0
        e = len(self._l) - 1
        logging.debug('SCHeap.retIdx({:d}):'.format(v))
        while 1:
            m = b + (e - b) // 2
            logging.debug('SCHeap.retIdx(): Loop b={:d} e={:d} m={:d}:'.format(b, e, m))
            if v > self._l[m].start:
                b = m + 1
            else:
                e = m - 1
            if self._l[m].start == v or e < b:
                logging.debug('SCHeap.retIdx(): about to return b={:d} e={:d} m={:d} self._l[m].start={:d}'.format(b, e, m, self._l[m].start))
                if self._l[m].start < v:
                    # Over-range
                    m += 1
                logging.debug('SCHeap.retIdx(): returning m={:d}'.format(m))
                return m
        
#    def binChopIntList(self, theV, theL):
#        """Binary search algorithm test."""
#        logging.debug('SCHeap.binChopIntList({:d}, {:s}):'.format(theV, theL))
#        b = 0
#        e = len(theL)-1
#        if e == 0:
#            # Zero length
#            return 1
#        while 1:
#            m = b + (e - b) // 2
#            if theV > theL[m]:
#                b = m + 1
#            else:
#                e = m - 1
#            if theL[m] == theV or e < b:
#                if theL[m] < theV:
#                    # Over-range
#                    m += 1
#                return m    
    
    def add(self, start, stop):
        """Adds a block at start, stop.
        Cases:
        A. Insert a completely new block
        B. Pre-pend to an existing block
        C. Append to an existing block
        D. Completely fill a gap (i.e. B+C)"""
        # Error check of input
        logging.debug('SCHeap.add({:d}, {:d}): list was={!s:s}'.format(start, stop, self._l))
        self._raiseOnError(start, stop)
        # Take an early bath if we can
        if len(self._l) == 0:
            self._l = [Block(start, stop)]
            logging.debug('SCHeap.add({:d}, {:d}): first entry, list now={!r:s}'.format(start, stop, self._l))
            return
        # Now down to work...
        # Find the block after start
        a = self.retIdx(start)
        #print('start', start, 'self._l', self._l, 'a', a)
        if a == len(self._l):
            # Over-range so add (case A) or append block (case C)
            logging.debug('SCHeap.add(): a={:d} appending ({:d}, {:d})'.format(a, start, stop))
            if len(self._l) > 0 \
            and start < self._l[a-1].stop:
                # Underlap on previous block
                raise ExceptionSCHeap('ScHeap.add(): start {:d} underlaps block {:d} that stops at {:d}'.format(start, a, self._l[a-1].stop))
            if self._l[a-1].stop == start:
                # Case C, append start/stop to last block
                self._l[a-1] = Block(self._l[a-1].start, stop)
            else:
                # Case A new block
                self._l.append(Block(start, stop))
            return
        if stop > self._l[a].start:
            # End overlaps existing block
            raise ExceptionSCHeap('ScHeap.add(): stop {:d} overlaps block {:d} that starts at {:d}'.format(stop, a, self._l[a].start))
        logging.debug('SCHeap.add(): mySt={:d} a={:d}'.format(self._l[a].start, a))
        if stop == self._l[a].start:
            if a > 0 \
            and start < self._l[a-1].stop:
                # Underlap on previous block
                raise ExceptionSCHeap('ScHeap.add(): start {:d} underlaps block {:d} that stops at {:d}'.format(start, a, self._l[a-1].stop))
            # Case B (prepend) or D (completely fill)
            if a == 0 or start > self._l[a-1].stop:
                # Case B (prepend)
                logging.debug('SCHeap.add(): Case B a={:d}'.format(a)) 
                self._l[a] = Block(start, self._l[a].stop)
            else:
                # Case D (completely fill), update the block [a], delete block a-1
                logging.debug('SCHeap.add(): Case D a={:d}'.format(a)) 
                self._l[a] = Block(self._l[a-1].start, self._l[a].stop)
                del self._l[a-1]
        else:
#            # Case A or C
#            if a != 0 and start == self._l[a-1].stop:
#                # Case C (append) on block a-1
#                logging.debug('SCHeap.add(): Case C a={:d}'.format(a)) 
#                self._l[a-1] = Block(self._l[a-1].start, stop)
#            else:
#                # Case A (new block)
#                logging.debug('SCHeap.add(): Case A a={:d}'.format(a)) 
#                self._l.insert(a, Block(start, stop))
            # Case A (new block)
            logging.debug('SCHeap.add(): Case A a={:d}'.format(a)) 
            self._l.insert(a, Block(start, stop))
        logging.debug('SCHeap.add({:d}, {:d}): list now={!r:s}'.format(start, stop, self._l))
    
    def need(self, start, stop):
        """Returns a list of Blocks needed to complete the
        supplied start, stop."""
        logging.debug('SCHeap.need({:d}, {:d}): list is={!s:s}'.format(start, stop, self._l)) 
        self._raiseOnError(start, stop)
        retVal = []
        if len(self._l) > 0:
            a = self.retIdx(start)
            if a > 0 and a < len(self._l):
                start = self._l[a-1].stop
            while a < len(self._l):
                logging.debug('SCHeap.need(): loop a={:d} Block={!r:s} start={:d}'.format(a, self._l[a], start))
                if self._l[a].start > stop:
                    break
                # Add gap
                if start < self._l[a].start:
                    retVal.append(Block(start, self._l[a].start))
                # Move start point up to end of current block
                start = self._l[a].stop
                a += 1
            logging.debug('SCHeap.need(): Done a={:d} retVal={!r:s}'.format(a, retVal))
            # Add trailing block if necessary
            if len(self._l) > 0 and self._l[a-1].stop < stop:
                retVal.append(Block(self._l[a-1].stop, stop))
        else:
            # Empty list case
            retVal.append(Block(start, stop))
        logging.debug('SCHeap.need(): returning retVal={!r:s}'.format(retVal))
        return retVal

#    def need(self, start, stop):
#        """Returns a list of Blocks needed to complete the
#        supplied start, stop."""
#        logging.debug('SCHeap.need({:d}, {:d}): list is={:s}'.format(start, stop, self._l)) 
#        self._raiseOnError(start, stop)
#        retVal = []
#        if len(self._l) > 0:
#            a = 0
#            while a < len(self._l):
#                logging.debug('SCHeap.need(): loop a={:d} Block={:s} start={:d}'.format(a, self._l[a], start))
#                if self._l[a].start > stop:
#                    break
#                # Add gap
#                if start < self._l[a].start:
#                    retVal.append(Block(start, self._l[a].start))
#                # Move start point up to end of current block
#                start = self._l[a].stop
#                a += 1
#            logging.debug('SCHeap.need(): Done a={:d} retVal={:s}'.format(a, retVal))
#            # Add trailing block if necessary
#            if len(self._l) > 0 and self._l[a-1].stop < stop:
#                retVal.append(Block(self._l[a-1].stop, stop))
#        else:
#            # Empty list case
#            retVal.append(Block(start, stop))
#        logging.debug('SCHeap.need(): returning retVal={:s}'.format(retVal)) 
#        return retVal


#    def add_old(self, start, stop):
#        """Adds a block at start, stop.
#        Cases:
#        A. Insert a completely new block
#        B. Pre-pend to an existing block
#        C. Append to an existing block
#        D. Completely fill a gap (i.e. B+C)"""
#        # Error check of input
#        logging.debug('SCHeap.add({:d}, {:d}): list was={:s}'.format(start, stop, self._l))
#        self._raiseOnError(start, stop)
#        # Take an early bath if we can
#        if len(self._l) == 0:
#            self._l = [Block(start, stop)]
#            logging.debug('SCHeap.add({:d}, {:d}): list now={:s}'.format(start, stop, self._l)) 
#            return
#        # Now down to work...
#        # Find the block after st
#        a = 0
#        while a < len(self._l):
#            bSt = self._l[a].start
#            bEn = self._l[a].stop
#            if bSt > start:
#                if stop > bSt:
#                    # End overlaps existing block
#                    raise ExceptionSCHeap('ScHeap.add(): end {:d} overlaps block {:d} that starts at {:d}'.format(stop, a, bSt))
#                break
#            if start < bEn:
#                # End overlaps existing block
#                raise ExceptionSCHeap('ScHeap.add(): start {:d} overlaps block {:d} that ends at {:d}'.format(start, a, bEn))
#            a += 1
#        logging.debug('SCHeap.add(): mySt={:d} a={:d}'.format(bSt, a))
#        if stop == bSt:
#            # Case B or D
#            if a == 0 or start > self._l[a-1].stop:
#                # Case B
#                logging.debug('SCHeap.add(): Case B a={:d}'.format(a)) 
#                self._l[a] = Block(start, self._l[a].stop)
#            else:
#                # Case D, update the block [a], delete block a-1
#                logging.debug('SCHeap.add(): Case D a={:d}'.format(a)) 
#                self._l[a] = Block(self._l[a-1].start, self._l[a].stop)
#                del self._l[a-1]
#        else:
#            # Case A or C
#            if a != 0 and start == self._l[a-1].stop:
#                # Case C on block a-1
#                logging.debug('SCHeap.add(): Case C a={:d}'.format(a)) 
#                self._l[a-1] = Block(self._l[a-1].start, stop)
#            else:
#                # Case A
#                logging.debug('SCHeap.add(): Case A a={:d}'.format(a)) 
#                self._l.insert(a, Block(start, stop))
#        logging.debug('SCHeap.add({:d}, {:d}): list now={:s}'.format(start, stop, self._l)) 

