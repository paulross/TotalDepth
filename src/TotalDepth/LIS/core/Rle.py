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
"""The RLE module provides Run Length Encoding suitable for recording the file
positions of a set of LIS Logical Records that represent frame data.

Created on 5 Jan 2011

class RLEItem()
=================

A generic item in a Run Length Encoding list.

class RLE()
=================

A generic Run Length Encoding list.

class RLEItemType01()
======================

A specialised item in a Run Length Encoding list for type 0/1 LIS Logical Records.

class RLEType01()
======================

A specialised Run Length Encoding list for type 0/1 LIS Logical Records.

API Reference
===============

"""
from TotalDepth.common.Rle import RLEItem, RLE

__author__  = 'Paul Ross'
__date__    = '2011-01-05'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'


class RLEItemType01(RLEItem):
    """Specialisation of an RLEItem for type 0 and type 1 LIS Logical Records.
    This is a RLEItem for the Logical Record but within we have a RLE() object
    for the X axis values.
    
    tellLrPos - the position in the LIS file of the start of the Logical Record.
    
    numFrameS - integer number of frames in this Logical Record.
    
    xAxisValue - The value of the X axis of the first frame in the Logical Record."""
    def __init__(self, tellLrPos, numFrameS, xAxisValue):
        #logging.debug('RLEItemType01.__init__({:d}, {:d}, {:f})'.format(tellLrPos, numFrameS, xAxisValue))
        super(RLEItemType01, self).__init__(tellLrPos)
        self._numFrames = numFrameS
        self._rleXaxis = RLE()
        self._rleXaxis.add(xAxisValue)
        
    def __str__(self):
        """String representation."""
        return '<RLEItemType01: ' + super().__str__() + ' frames={:d}'.format(self._numFrames)
        
    @property
    def numFrames(self):
        """Total number of frames."""
        return self._numFrames
    
    def add(self, tellLrPos, numFrameS, xAxisValue):
        """Returns True if v has been absorbed in this entry. False means a
        new entry is required. A new entry is required if the tellLrPos is
        not regular or numFrameS is different than before."""
        #logging.debug('RLEItemType01.add({:d}, {:d}, {:f})'.format(tellLrPos, numFrameS, xAxisValue))
        #logging.debug('RLEItemType01: {:s}'.format(self))
        #
        # Note: Do all eliminating local tests first before calling super()
        # as super() will add if possible. If super() adds then our local test
        # causes False to be returned the data will be in two RLEItem objects.
        if numFrameS != self._numFrames \
        or not super(RLEItemType01, self).add(tellLrPos):
            #logging.debug('RLEItemType01.add() returns False')
            return False
        self._rleXaxis.add(xAxisValue)
        #logging.debug('RLEItemType01.add() returns True')
        return True
    
    def values(self):
        """Generates ordered tuples of (value, number of frames, xaxis value)."""
        for i, v in enumerate(super(RLEItemType01, self).values()):
            yield v, self._numFrames, self._rleXaxis.value(i)
    
    def value(self, i):
        """Returns the i'th tuple of (i, (value, number of frames, xaxis value))."""
        i, v = super(RLEItemType01, self).value(i)
        if v is None:
            return i, None
        return i, (v, self._numFrames, self._rleXaxis.value(i))

    def totalFrames(self):
        """Returns the total number of frames in this RLE item."""
        return self._numFrames * (self.repeat + 1)

    def tellLrForFrame(self, fNum):
        """Returns the Logical Record position that contains the integer frame number."""
        assert(fNum >= 0)
        totalF = self.totalFrames()
        if fNum <= totalF:
            return fNum % self._numFrames, self.value(fNum // self._numFrames)[1]
        return fNum - totalF, None
        
    def xAxisFirst(self):
        """Returns the first X-axis value loaded."""
        return self._rleXaxis.first()

    def xAxisLast(self):
        """Returns the first X-axis value loaded."""
        return self._rleXaxis.last()

class RLEType01(RLE):
    """Class that represents Run Length Encoding for type 0/1 logical records.
    
    theXUnits - the X axis units."""
    def __init__(self, theXUnits, *args):
        super().__init__(*args)
        self._xUnits = theXUnits
        #logging.debug('RLEType01.__init__({:s}) {:s}'.format(theXUnits, repr(self)))
        
    def __str__(self):
        """String representation."""
        #return 'RLEType01: func={:s}\n  '.format(str(self._func)) \
        #    + '\n  '.join([str(r) for r in self._rleS])
        return '{:s}: func={:s}: '.format(self.__class__.__name__, str(self.function)) \
               + '[' + ', '.join([str(r) for r in self.rle_items]) + ']'
    
    @property
    def xAxisUnits(self):
        """X axis units."""
        return self._xUnits
    
    @property
    def hasXaxisData(self):
        """True if there is X axis data."""
        return len(self) > 0
    
    def add(self, tellLrPos, numFrameS, xAxisValue):
        """Adds a value to this RLE object."""
        #logging.debug('RLEType01.add(0x{:x}, {:d}, {:f})'.format(tellLrPos, numFrameS, xAxisValue))
        if self.function is not None:
            tellLrPos = self.function(tellLrPos)
        # NOTE: Side effect in second test
        #logging.debug('RLEType01.add(): self._rleS={:s}'.format(self._rleS))
        if len(self.rle_items) == 0 \
        or not self.rle_items[-1].add(tellLrPos, numFrameS, xAxisValue):
            #logging.debug('RLEType01.add(...) new RLEItemType01')
            self.rle_items.append(RLEItemType01(tellLrPos, numFrameS, xAxisValue))
            #logging.debug('RLEType01.add(...) self._rleS now={:s}'.format(self))

    def tellLrForFrame(self, fNum):
        """Returns the (lr_seek, frame_offset) i.e. the Logical Record position
        that contains the integer frame number and the number of excess frames."""
        #logging.debug('RLEType01.tellLrForFrame({:d})'.format(fNum))
        if fNum < 0:
            raise IndexError('list index out of range')
        for r in self.rle_items:
            fNum, v = r.tellLrForFrame(fNum)
            if v is not None:
                return v[0], fNum
        raise IndexError('list index out of range')

    def totalFrames(self):
        """Returns the total number of frames in this RLE object."""
        #logging.debug('RLEType01.totalFrames() self._rleS={:s}'.format(self))
        return sum([r.totalFrames() for r in self.rle_items])

    def xAxisFirst(self):
        """Returns the first X-axis value loaded or None if nothing loaded."""
        if len(self.rle_items) > 0:
            return self.rle_items[0].xAxisFirst()

    def xAxisLast(self):
        """Returns the last X-axis value at the satart of the last Logical Record loaded or None if nothing loaded."""
        if len(self.rle_items) > 0:
            return self.rle_items[-1].xAxisLast()
        
    def xAxisLastFrame(self):
        """Returns the last X-axis value of the last frame loaded or None if nothing loaded."""
        frame_spacing = self.frameSpacing()
        if len(self.rle_items) > 0 and frame_spacing is not None:
            return self.rle_items[-1].xAxisLast() + (self.rle_items[-1].numFrames - 1) * frame_spacing
        
    def _numFramesInLast(self):
        """Returns the number of frames in the last entry or None if nothing loaded.
        This is useful for subtracting from the totalFrames for the frame spacing."""
        if len(self.rle_items) > 0:
            return self.rle_items[-1].numFrames
        
    def frameSpacing(self):
        """Returns the frame spacing from the first/last entries, or None if nothing loaded.
        Returned value is -ve for decreasing X (up logs), +ve for increasing X
        (down and time logs)."""
        totalFrames = self.totalFrames()
        divisor = totalFrames - self._numFramesInLast()
        if len(self.rle_items) > 0 and totalFrames > 1 and divisor != 0:
            return (self.xAxisLast() - self.xAxisFirst()) / divisor
