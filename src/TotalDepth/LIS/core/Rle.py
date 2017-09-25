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

__author__  = 'Paul Ross'
__date__    = '2011-01-05'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

class RLEItem(object):
    """Class that represents a single entry in a Run Length Encoding set. v - The datum value."""
    def __init__(self, v):
        #print('RLEItem.__init__({:d})'.format(v))
        self._datum = v
        self._stride = None
        self._repeat = 0
        
    def __str__(self):
        """String representation."""
        return 'RLEItem: ' + self._propStr()
    
    def _propStr(self):
        return 'datum={:s} stride={:s} repeat={:s}'.format(
            str(self.datum),
            str(self.stride),
            str(self.repeat),
        )
    
    @property
    def datum(self):
        """The initial datum value."""
        return self._datum
    
    @property
    def stride(self):
        """The stride as a number or None if there is only one entry."""
        return self._stride
    
    @property
    def repeat(self):
        """The repeat count."""
        return self._repeat
        
    def numValues(self):
        """Total number of record values."""
        return self._repeat + 1
        
    def add(self, v):
        """Returns True if v has been absorbed in this entry. False means a
        new entry is required."""
        if self._stride is None:
            assert(self._repeat == 0)
            self._stride = v - self._datum
            self._repeat = 1
            return True
        expVal = self._datum + (self._stride * (self._repeat + 1))
        if v == expVal:
            self._repeat += 1
            return True
        return False
    
    def values(self):
        """Generates all values."""
        v = self._datum
        yield v
        for i in range(self._repeat):
            assert(self._stride is not None)
            v += self._stride
            yield v
    
    def value(self, i):
        """Returns a particular value."""
        if i >= 0:
            if i > self._repeat:
                return i - self._repeat - 1, None
            if self._stride is None:
                return i, self._datum
            return i, self._datum + i * self._stride
        # Indexing from end
        if -i > self._repeat + 1:
            return i + self._repeat + 1, None
        #if self._stride is None:
        #    return i, self._datum
        return i, self._datum + (self._repeat + i + 1) * self._stride
    
    def range(self):
        """Returns a range object that has (start, stop, step) or None if a single entry."""
        if self._stride is None:
            return range(self._datum, self._datum+1)
        return range(self._datum, self._datum + (self._stride * (self._repeat + 1)), self._stride)
        
    def first(self):
        """Returns the first value."""
        return self._datum
        
    def last(self):
        """Returns the last value."""
        if self._stride is None:
            return self._datum
        return self._datum + (self._stride * self._repeat)

class RLE(object):
    """Class that represents Run Length Encoding.
    
    theFunc - optional unary function to convert all values with.
    """
    def __init__(self, theFunc=None):
        """Constructor, optionally takes a unary function to convert all values with."""
        # List of RLEItem
        self._rleS = []
        self._func = theFunc
        
    def __str__(self):
        """String representation."""
        #return 'RLE: func={:s}\n  '.format(str(self._func)) \
        #    + '\n  '.join([str(r) for r in self._rleS])
        return 'RLE: func={:s}\n  '.format(str(self._func)) \
            + '[' + ', '.join([str(r) for r in self._rleS]) + ']'
    
    def __len__(self):
        """The number of RLEItem(s)."""
        return len(self._rleS)

    def __getitem__(self, key):
        """Returns a RLEItem."""
        return self._rleS[key]

    def numValues(self):
        """Total number of record values."""        
        return sum([r.numValues() for r in self._rleS])
        
    def add(self, v):
        """Adds a value to this RLE object."""
        if self._func is not None:
            v = self._func(v)
        # NOTE: Side effect in second test
        if len(self._rleS) == 0 \
        or not self._rleS[-1].add(v):
            self._rleS.append(RLEItem(v))

    def values(self):
        """Generates all values entered."""
        for r in self._rleS:
            for v in r.values():
                yield v
    
    def value(self, i):
        """Indexing; this returns the i'th value added."""
        if i >= 0:
            for r in self._rleS:
                i, v = r.value(i)
                if v is not None:
                    return v
        else:
            for r in reversed(self._rleS):
                i, v = r.value(i)
                if v is not None:
                    return v
        raise IndexError('list index out of range')
    
    def rangeList(self):
        """Returns a list of range() or None objects. A None object means that
        the RLEItem has a single value."""
        return [i.range() for i in self._rleS]
    
    def first(self):
        """Returns the first value or None if no values added."""
        if len(self._rleS) > 0:
            return self._rleS[0].first()
        
    def last(self):
        """Returns the last value or None if no values added."""
        if len(self._rleS) > 0:
            return self._rleS[-1].last()

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
        return 'RLEItemType01: ' \
            + self._propStr() \
            + ' frames={:d}'.format(self._numFrames)
        
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
        return self._numFrames * (self._repeat + 1)

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
        return '{:s}: func={:s}: '.format(self.__class__.__name__, str(self._func)) \
            + '[' + ', '.join([str(r) for r in self._rleS]) + ']'
    
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
        if self._func is not None:
            tellLrPos = self._func(tellLrPos)
        # NOTE: Side effect in second test
        #logging.debug('RLEType01.add(): self._rleS={:s}'.format(self._rleS))
        if len(self._rleS) == 0 \
        or not self._rleS[-1].add(tellLrPos, numFrameS, xAxisValue):
            #logging.debug('RLEType01.add(...) new RLEItemType01')
            self._rleS.append(RLEItemType01(tellLrPos, numFrameS, xAxisValue))
            #logging.debug('RLEType01.add(...) self._rleS now={:s}'.format(self))

    def tellLrForFrame(self, fNum):
        """Returns the (lr_seek, frame_offset) i.e. the Logical Record position
        that contains the integer frame number and the number of excess frames."""
        #logging.debug('RLEType01.tellLrForFrame({:d})'.format(fNum))
        if fNum < 0:
            raise IndexError('list index out of range')
        for r in self._rleS:
            fNum, v = r.tellLrForFrame(fNum)
            if v is not None:
                return v[0], fNum
        raise IndexError('list index out of range')

    def totalFrames(self):
        """Returns the total number of frames in this RLE object."""
        #logging.debug('RLEType01.totalFrames() self._rleS={:s}'.format(self))
        return sum([r.totalFrames() for r in self._rleS])

    def xAxisFirst(self):
        """Returns the first X-axis value loaded or None if nothing loaded."""
        if len(self._rleS) > 0:
            return self._rleS[0].xAxisFirst()

    def xAxisLast(self):
        """Returns the last X-axis value at the satart of the last Logical Record loaded or None if nothing loaded."""
        if len(self._rleS) > 0:
            return self._rleS[-1].xAxisLast() 
        
    def xAxisLastFrame(self):
        """Returns the last X-axis value of the last frame loaded or None if nothing loaded."""
        if len(self._rleS) > 0:
            return self._rleS[-1].xAxisLast() \
                + (self._rleS[-1].numFrames - 1) * self.frameSpacing()
        
    def _numFramesInLast(self):
        """Returns the number of frames in the last entry or None if nothing loaded.
        This is useful for subtracting from the totalFrames for the frame spacing."""
        if len(self._rleS) > 0:
            return self._rleS[-1].numFrames
        
    def frameSpacing(self):
        """Returns the frame spacing from the first/last entries, or None if nothing loaded.
        Returned value is -ve for decreasing X (up logs), +ve for increasing X
        (down and time logs)."""
        totalFrames = self.totalFrames()
        if len(self._rleS) > 0 and totalFrames > 1:
            return (self.xAxisLast() - self.xAxisFirst()) / (totalFrames - self._numFramesInLast())
