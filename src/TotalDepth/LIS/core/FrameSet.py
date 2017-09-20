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
"""The FrameSet module provides a means of representing LIS frame data.

Created on 10 Jan 2011

"""

__author__  = 'Paul Ross'
__date__    = '2011-01-10'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

#import time
import sys
import math
#import logging
import collections
#import array
import numpy

from TotalDepth.LIS import ExceptionTotalDepthLIS
#from TotalDepth.LIS.core import Type01Plan
#from TotalDepth.LIS.core import Rle
from TotalDepth.LIS.core import RepCode
#from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import Units

class ExceptionFrameSet(ExceptionTotalDepthLIS):
    """Specialisation of exception for FrameSet."""
    pass

class ExceptionFrameSetEmpty(ExceptionFrameSet):
    """Raised when an illegal operation is performed on a FrameSet."""
    pass

class ExceptionFrameSetNULLSpacing(ExceptionFrameSet):
    """Raised when FrameSet depends on a frame spacing that can not be determined."""
    pass

class ExceptionFrameSetMixedChannels(ExceptionFrameSet):
    """Raised when generating values for multiple channels where the channels are not of the same shape i.e. number of samples, butsts."""
    pass

############################################################
# Section: Global functions for checking indexes and raising
############################################################
def chkIdx(i, l, msg):
    """Global function for checking indexes and raising an IndexError.
    msg is expected to have two format fields that take i and l respectively."""
    if i < 0:
        myI = l + i
    else:
        myI = i
    if myI < 0 or myI >= l:
        raise IndexError(msg.format(i, l))
    return myI

def sliceDefaults(theSl):
    """Returns a new slice with start=None as 0 and step=None as 1."""
    return slice(theSl.start or 0, theSl.stop, theSl.step or 1)
########################################################
# End: Global functions for checking indexes and raising
########################################################

class DataSeqBase(object):
    """Base class for a sequence of objects."""
    def __init__(self):
        # List of some type of objects
        self._data = []

    def __getitem__(self, key):
        return self._data[key]

#    def clear(self):
#        self._data = []
#
#    def append(self, theObj):
#        self._data.append(theObj)

#############################################
# Section: Sub-channel and channel templates.
#############################################
class SuChArTe(collections.namedtuple('SuChArTe', 'samples bursts')):
    """Sub-channel Array Template."""
    __slots__ = ()
    @property
    def numValues(self):
        """The total number of values in this sub-channel."""
        return self.samples * self.bursts
    
    def index(self, theS, theB):
        """Returns the index of a particular sample or channel with bounds checking.
        
        WARNING: This not correct for Dipmeter sub-channels."""
        myS = chkIdx(theS, self.samples, 'SuChArTe.index(): sample {:d} not in array length {:d}')
        myB = chkIdx(theB, self.bursts, 'SuChArTe.index(): burst {:d} not in array length {:d}')
        return self._index(myS, myB)
    
    def _index(self, theS, theB):
        """Returns the index of a particular sample or channel, NO bounds checking.
        
        WARNING: This not correct for Dipmeter sub-channels."""
        return theB + self.bursts * theS

    def __str__(self):
        """String representation."""
        return 'SuChArTe(samples={:s}, bursts={:s}, values={:s})'.format(
            str(self.samples),
            str(self.bursts),
            str(self.numValues),
        )

class ChArTe(DataSeqBase):
    """Channel Array Template. Constructed with a DatumSpecBlock object.
    
    **Implementation note:**
    ``_index()`` and ``_dipmeterIndex()`` have no bounds checking but are
    significantly faster for those routines that access then with
    pre-checked limits. 
    """
    def __init__(self, theDsb):
        """Constructor with a DatumSpecBlock object."""
        super(ChArTe, self).__init__()
        self.repCode = theDsb.repCode
        self.wordLength = RepCode.wordLength(self.repCode)
        self._lisSize = 0
        myScOffset = 0
        # List of starting offsets for sub channels
        # WARNING: Not for dipmeter channels
        self._scOffsetS = []
        for sc in range(theDsb.subChannels):
            sa = theDsb.samples(sc)
            bu = theDsb.bursts(sc)
            siz = sa * bu
            self._data.append(SuChArTe(sa, bu))
            self._lisSize += self.wordLength * siz
            self._scOffsetS.append(myScOffset)
            myScOffset += siz
        self.numValues = sum([sc.numValues for sc in self._data])
        self.subChMnems = [theDsb.subChMnem(sc) for sc in range(theDsb.subChannels)]

    def __str__(self):
        """String representation."""
        return 'ChArTe lisSize={:d} rc={:d} wordLength={:d} subChannels={:d}:\n'.format(
                    self._lisSize, self.repCode, self.wordLength, self.numSubChannels
            ) \
            + '  ' \
            + '\n  '.join([str(d) for d in self._data])

    @property
    def numSubChannels(self):
        """Number of sub-channels."""
        return len(self._data)

    @property
    def lisSize(self):
        """Number of bytes per frame in the LIS representation."""
        return self._lisSize
    
    def subChOffsRange(self, sc):
        """Returns a range object that is the sub-channel offset in the frame
        relative to the start of the channel."""
        sc = chkIdx(sc,
                      self.numSubChannels,
                      'ChArTe.subChOffsRange(): sub-channel {:d} not in array length {:d}',
                      )
        if self.repCode in RepCode.DIPMETER_REP_CODES:
            return RepCode.DIPMETER_SUB_CHANNEL_RANGES[sc]
        if sc == self.numSubChannels - 1:
            return range(self._scOffsetS[sc], self.numValues, 1)
        return range(self._scOffsetS[sc], self._scOffsetS[sc+1], 1)

    def subChOffsSlice(self, sc, chOfs=0):
        """Returns a slice object that is the sub-channel offset in the frame
        relative to the start of the channel."""
        sc = chkIdx(sc,
                      self.numSubChannels,
                      'ChArTe.subChOffsRange(): sub-channel {:d} not in array length {:d}',
                      )
        if self.repCode in RepCode.DIPMETER_REP_CODES:
            mySlice = RepCode.DIPMETER_SUB_CHANNEL_SLICES[sc]
            return slice(chOfs + mySlice.start, chOfs + mySlice.stop, mySlice.step)
        if sc == self.numSubChannels - 1:
            return slice(chOfs + self._scOffsetS[sc], chOfs + self.numValues, 1)
        return slice(chOfs + self._scOffsetS[sc], chOfs + self._scOffsetS[sc+1], 1)

    # Implementation note:
    # _index() and _dipmeterIndex() have no bounds checking but are
    # significantly faster for those routines that access then with
    # pre-checked limits. 
    def index(self, theSc, theSa, theBu):
        """Returns the index of a particular sub-channel, sample and burst.
        Order is (fastest changing first): burst, sample.
        For those with sub-channels: sub-channel, sample
        This has bounds checking."""
        theSc = chkIdx(theSc,
                      self.numSubChannels,
                      'ChArTe.index(): sub-channel {:d} not in array length {:d}',
                      )
        if self.repCode in RepCode.DIPMETER_REP_CODES:
            return self.dipmeterIndex(theSc, theSa, theBu)
        return self._data[theSc].index(theSa, theBu)
        
    def _index(self, theSc, theSa, theBu):
        """Returns the index of a particular sub-channel, sample and burst.
        Order is (fastest changing first): burst, sample.
        For those with sub-channels: sub-channel, sample.
        NO bounds checking. Typically 20-25% faster than index() if your loops
        are already bounded."""
        if self.repCode in RepCode.DIPMETER_REP_CODES:
            return self._dipmeterIndex(theSc, theSa, theBu)
        else:
            # Single sub-channel, this may raise index error
            return self._data[theSc]._index(theSa, theBu)

    def dipmeterIndex(self, theSc, theSa, theBu):
        """Returns dipmeter data index. Bounds checking is performed."""
        if self.repCode not in RepCode.DIPMETER_REP_CODES:
            raise ExceptionFrameSet('FrameSet.dipmeterIndex() called on non-dipmeter channel.')
        mySc = chkIdx(theSc,
                      self.numSubChannels,
                      'ChArTe.index(): sub-channel {:d} not in array length {:d}',
                      )
        # Note sub-channel range check has been done above
        if theBu not in (0, -1):
            raise IndexError(
                'ChArTe.index(): Dipmeter burst index {:d} out of range'.format(theBu))
        # Now behave according to rep code that decides the layout
        if mySc < RepCode.DIPMETER_NUM_FAST_CHANNELS:
            # Fast channel data
            mySa = chkIdx(
                theSa,
                RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES,
                'ChArTe.index(): Dipmeter fast channel sample index {:d} not in array length {:d}'
            )
            return mySa * RepCode.DIPMETER_NUM_FAST_CHANNELS + mySc
        # Only representation codes 130, 234 are valid
        assert(self.repCode == 234)
        # Slow channel data
        chkIdx(theSa, 1, 'ChArTe.index(): Dipmeter slow channel sample index {:d} not in array length {:d}')
        return RepCode.DIPMETER_SIZE_FAST_CHANNELS + mySc - RepCode.DIPMETER_NUM_FAST_CHANNELS

    def _dipmeterIndex(self, theSc, theSa, theBu):
        """Returns dipmeter data index. Bounds checking is NOT done.
        Typically 20-25% faster than dipmeterIndex() if your loops are already
        bounded."""
        #assert(self.repCode in RepCode.DIPMETER_REP_CODES)
        if theSc < 0:
            theSc = self.numSubChannels + theSc
        #assert(theSc >= 0  and theSc < self.numSubChannels), '_dipmeterIndex() theSc={:d}'.format(theSc)
        # Now behave according to rep code that decides the layout
        if theSc < RepCode.DIPMETER_NUM_FAST_CHANNELS:
            # Fast channel data
            # Fix negative sample indexing from end
            if theSa < 0:
                theSa = RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES + theSa
            #assert(theSa >= 0  and theSa < RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES)
            return theSa * RepCode.DIPMETER_NUM_FAST_CHANNELS + theSc
        # Only representation codes 130, 234 are valid
        #assert(self.repCode == 234)
        # Slow channel data
        #assert(theSa in (0, -1))
        return RepCode.DIPMETER_SIZE_FAST_CHANNELS + theSc - RepCode.DIPMETER_NUM_FAST_CHANNELS

#########################################
# End: Sub-channel and channel templates.
#########################################

#############################
# Section: FrameSet container
#############################

#: Contains information about declared X axis.
#: This is essential for indirect X axis.
#: Names are identical to the DFSR EntryBlockSet
class XAxisDecl(collections.namedtuple(
            'XAxisDecl',
            'upDown frameSpacing frameSpacingUnits recordingMode depthUnits depthRepCode'
        )
    ):
    __slots__ = ()
    @property
    def isLogUp(self):
        """True if "up" log (x decreasing)."""
        return self.upDown == 1

    @property
    def isLogDown(self):
        """True if "down" log (x decreasing)."""
        return self.upDown == 255
    
    @property
    def isIndirectX(self):
        """True if has indirect X axis."""
        return self.recordingMode == 1

class FrameSet(object):
    """Contains the representation of a list of Frames and thus a
    representation of and 'matrix' (non literal) of:
    (frame, channel, sub-channel, sample, burst).
    Commonly shortened to: (fr, ch, sc, sa, bu)
    Effectively this is a wrapper around a numpy 2-D array that we treat
    specially to get our 5-D array (LIS channels are not homogeneous).
    
    Constructed with a DFSR, a slice of frame indexes and an optional
    list of external channel indexes (defaults to all channels).
    Duplicates in the theChS will be removed and it will be sorted.
    
    xAxisIndex is the external channel index of the X axis (ignored if indirect X).    
    """
    #: Data type used in the underlying numpy array.
    NUMPY_DATA_TYPE = 'float64'
    def __init__(self, theDfsr, theFrameSlice, theChS=None, xAxisIndex=0):
        """Constructed with a DFSR, a slice of frame indexes and an optional
        list of external channel indexes (defaults to all channels).
        Duplicates in the theChS will be removed and it will be sorted.
        xAxisIndex is the external channel index of the X axis (ignored if
        indirect X)."""
        # Capture the declared X information from the DFSR
        self._xAxisDecl = XAxisDecl(
            # 1 is up, 255 is down, 0 is neither
            theDfsr.ebs.upDown,
            theDfsr.ebs.frameSpacing,
            theDfsr.ebs.frameSpacingUnits,
            theDfsr.ebs.recordingMode,
            theDfsr.ebs.depthUnits,
            theDfsr.ebs.depthRepCode,
        )
        # Absent value
        self._absentValue = theDfsr.ebs.absentValue
        self._numExtChannels = len(theDfsr.dsbBlocks)
        # This is used to map external frame number to internal ones
        self._frameSlice = sliceDefaults(theFrameSlice)
        # Always include the xAxis in the channel set if not indirect X
        if theChS is not None and not self._xAxisDecl.isIndirectX:
            theChS.append(xAxisIndex)
        #print('self._frameSlice', self._frameSlice)
        # Set self._chIdxIntExt that maps internal array positions to external
        # channels indexes.
        # i.e. external_index = self._chIdxIntExt[internal_index] 
        if theChS is None:
            # All channels are in this FrameSet
            self._chIdxIntExt = list(range(self._numExtChannels))
            # All channels so self._chIdxExtIntMap is one-to-one mapping
            self._chIdxExtIntMap = None
        else:
            # Only a subset of external channels are in this FrameSet
            # self._chIdxIntExt is a list of external channel indexes
            # i.e. E = self._chIdxIntExt[I] where I is the internal
            # channel number and E the external one.
            self._chIdxIntExt = sorted(list(set(theChS)))
            # self._chIdxExtIntMap maps external channel index to internal location
            # i.e. internal_index = self._chIdxExtIntMap[external_index]
            self._chIdxExtIntMap = {}
            for i in range(len(self._chIdxIntExt)):
                # Get the external channel number
                e = self._chIdxIntExt[i]
                self._chIdxExtIntMap[e] = i
        # Set up Channel Array Templates
        self._catS = [ChArTe(theDfsr.dsbBlocks[e]) for e in self._chIdxIntExt]
        # Figure out LIS size in bytes for this FrameSet
        self._frameSize = sum([c.lisSize for c in self._catS])
        self._valuesPerFrame = sum([c.numValues for c in self._catS])
        # List that maps internal channel number start to offset in frame.
        self._intChValIdxS = []
        myIdxVal = 0
        for c in self._catS:
            self._intChValIdxS.append(myIdxVal)
            myIdxVal += c.numValues
        # Will be initialised to a two dimensional numpy array of, usually, 'float64'
        # Indirect X axis, this is a separately maintained 1D array
        if self._xAxisDecl.recordingMode:
            self._indrXVector = numpy.empty((0), self.NUMPY_DATA_TYPE)
            if self._xAxisDecl.frameSpacingUnits != self._xAxisDecl.depthUnits:
                try:
                    # Convert frame spacing units to depth units
                    self._frameSpacing = Units.convert(
                                self._xAxisDecl.frameSpacing,
                                self._xAxisDecl.frameSpacingUnits,
                                self._xAxisDecl.depthUnits
                    )
                except Units.ExceptionUnits as err:
                    raise ExceptionFrameSet('FrameSet.__init__() can not convert units: {:s}'.format(str(err)))
            else:
                self._frameSpacing = self._xAxisDecl.frameSpacing
            # Allow for up/down
            self._frameSpacing = abs(self._frameSpacing)
            if self._xAxisDecl.isLogUp:
                self._frameSpacing = -1 * abs(self._frameSpacing)
        else:
            self._indrXVector = None
            self._frameSpacing = None
        self._frames = None#numpy.empty((0), self.NUMPY_DATA_TYPE)
        self._setFrames(self._totalNumFrames(self._frameSlice))
        # Create the offset tree
        self._offsetTree = self._retOffsetTree()
        # Create the slice tree
        # self._sliceTree[ch][sc] is a slice object for frame positions
        self._sliceTree = self._retSliceTree()
        # Selective X axis stuff - only relevant if explicit X.
        # The internal channel index of the X axis, not used if indirect depth
        # or no channels.
        self._xAxisIdxInt = None
        # Frame offset for the value of the xAxis
        self._xAxisFrOffs = None
        if not self._xAxisDecl.isIndirectX and self._numExtChannels > 0:
            # Range check
            try:
                myXAxisIndex = chkIdx(
                    xAxisIndex,
                    self._numExtChannels,
                    'X axis index  {:d} out of range: 0 >= x < {:d}')
            except IndexError as err:
                raise ExceptionFrameSet(str(err))
            self._xAxisIdxInt = self.internalChIdx(myXAxisIndex)
            self._xAxisFrOffs = self._intChValIdxS[self._xAxisIdxInt]

    def _retOffsetTree(self):
        """Creates a tree like structure that can rapidly determine the value
        offset in a frame of a ch, sc, sa, bu.
        ch is _internal_."""
        retMap = {}
        ofs = 0
        for ch in range(len(self._catS)):
            scMap = {}
            if self._catS[ch].repCode in RepCode.DIPMETER_REP_CODES:
                if self._catS[ch].repCode == RepCode.DIPMETER_EDIT_TAPE_REP_CODE:
                    # Fast channels only
                    for sc in range(RepCode.DIPMETER_NUM_FAST_CHANNELS):
                        scMap[sc] = self._retDipSubChannelOffsetBranch(sc, ofs)
                    ofs += RepCode.DIPMETER_NUM_FAST_CHANNELS * RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES
                elif self._catS[ch].repCode == RepCode.DIPMETER_CSU_FIELD_TAPE_REP_CODE:
                    # Fast + slow
                    for sc in range(RepCode.DIPMETER_NUM_FAST_CHANNELS + RepCode.DIPMETER_NUM_SLOW_CHANNELS):
                        scMap[sc] = self._retDipSubChannelOffsetBranch(sc, ofs)
                    ofs += RepCode.DIPMETER_NUM_FAST_CHANNELS * RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES \
                            + RepCode.DIPMETER_NUM_SLOW_CHANNELS
                else:
#                    print('Help:', self._catS[ch].repCode)
                    assert(0)
            else:
                for sc in range(self._catS[ch].numSubChannels):
                    saMap = {}
                    for sa in range(self._catS[ch][sc].samples):
                        buMap = {}
                        for bu in range(self._catS[ch][sc].bursts):
                            buMap[bu] = ofs
                            ofs += 1
                        saMap[sa] = buMap
                    scMap[sc] = saMap
            retMap[ch] = scMap
        return retMap
    
    def _retDipSubChannelOffsetBranch(self, theScCh, theBaseOffs):
        """Returns a sub-tree of the offset tree for a fast dipmeter sub-channel.
        theScCh is the sub channel (0-4) and theBaseOffs the start of the
        Dipmeter data in the frame."""
        assert(theScCh in range(RepCode.DIPMETER_NUM_FAST_CHANNELS + RepCode.DIPMETER_NUM_SLOW_CHANNELS))
        r = {theScCh : {}}
        if theScCh in range(RepCode.DIPMETER_NUM_FAST_CHANNELS):
            #   ch  sc  sa  bu: offset
            #        0: {
            #            0: {0: 0+theBaseOffs,},
            #            1: {0: 5+theBaseOffs,},
            #            ...
            #            15: {0: 75+theBaseOffs}
            #        }
            for sa in range(RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES):
                r[theScCh][sa] = {0 : theBaseOffs + theScCh + RepCode.DIPMETER_NUM_FAST_CHANNELS * sa}
        else:
            r[theScCh][0] = {
                0 : theBaseOffs \
                    + RepCode.DIPMETER_NUM_FAST_CHANNELS * RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES \
                    + theScCh - RepCode.DIPMETER_NUM_FAST_CHANNELS,
            }
        return r

    def _retSliceTree(self):
        """Creates a tree like structure that can rapidly determine the numpy
        slice in a frame that correspond to all ordered values of a ch, sc.
        ch is _internal_."""
        retMap = {}
        ofs = 0
        for ch in range(len(self._catS)):
            scMap = {}
            for sc in range(self._catS[ch].numSubChannels):
                scMap[sc] = self._catS[ch].subChOffsSlice(sc, chOfs=ofs)
            retMap[ch] = scMap
            ofs += self._catS[ch].numValues
        return retMap

    def __str__(self):
        """String representation."""
        if self._frames is None:
            return '{:s}: Array={:s}'.format(repr(self), str(self._frames))
        return '{:s}: Array={:s}'.format(repr(self), str(self._frames.shape))
    
    def longStr(self):
        """Returns a long string that describes me."""
        return '\n'.join(
            [
                '>>>>_chIdxIntExt: {:s}'.format(str(self._chIdxIntExt)),
                '>_chIdxExtIntMap: {:s}'.format(str(self._chIdxExtIntMap)),
                #'      _chOffset: {:s}'.format(str(self._chOffset)),
                '>>>>>>>>>>>_catS: {:s}'.format('\n '+str('\n '.join([str(c) for c in self._catS]))),
                '>_valuesPerFrame: {:s}'.format(str(self._valuesPerFrame)),
                '>>>>>_frameSlice: {!s:s}'.format(self._frameSlice),
            ]
        )
        
    def dumpFrames(self, theS=sys.stdout):
        """Dump the frames to the stream."""
        if self.numFrames > 0:
            mnemS = []
            for aCat in self._catS:
                mnemS.extend(aCat.subChMnems)
            theS.write('\t'.join([str(m) for m in mnemS]))
            theS.write('\n')
            for f in range(self.numFrames):
                theS.write('\t'.join(['{:g}'.format(v) for v in self._frames[f]]))
                theS.write('\n')
    
    @property
    def nbytes(self):
        """Returns the number of bytes in the underlying array implementation."""
        return self._frames.nbytes
    
    #====================================================
    # Section: Frame information, access and manipulation
    #====================================================
    @property
    def lisSize(self):
        """The number of LIS bytes that make up this FrameSet."""
        return self._frameSize * len(self._frames)
    
    @property
    def numFrames(self):
        """The number of frames currently in this FrameSet."""
        if self._indrXVector is not None:
            assert(len(self._indrXVector) == len(self._frames))
        return len(self._frames)
    
    @property
    def valuesPerFrame(self):
        """The number of values in each frame currently in this FrameSet."""
        return self._valuesPerFrame

    @property
    def numValues(self):
        """The total number of values in the array."""
        return self.numFrames * self.valuesPerFrame
    
    @property
    def frames(self):
        """Gives access to the raw numpy array."""
        return self._frames

    def frame(self, fr):
        """Returns a specific frame."""
        return self._frames[fr]

#    def frameStride(self):
#        """Returns the value of the inter-frame spacing for this partial frame
#        set. This takes into account the frame slice step. +ve/-ve depending
#        on direction. Returns None on direct X logs."""
#        if self._frameSpacing is not None:
#            return self._frameSpacing * self._frameSlice.step

    def xAxisValue(self, fr):
        """Returns the X axis value for the frame when indirect X is used or None."""
        if self.isIndirectX:
            assert(self._indrXVector is not None)
            return self._indrXVector[fr]
        # Direct X axis return chosen channel
        return self._frames[fr, self._xAxisFrOffs]

    def xAxisStep(self, numFr):
        """The distance stepped by numFr."""
        return numFr * self._frameSpacing

    def _setFrames(self, numFrames):
        """Sets the internals to an uninitialised array of values for numFrames."""
        if self._frames is None:
            self._frames = numpy.empty((numFrames, self._valuesPerFrame), self.NUMPY_DATA_TYPE)
        elif self._frames.shape != (numFrames, self._valuesPerFrame):
            self._frames.resize()
        if self._xAxisDecl.recordingMode:
            self._indrXVector = numpy.empty((numFrames,), self.NUMPY_DATA_TYPE)
    
#    def clear(self):
#        """Removes all frames."""
#        self._setFrames(0)

    def _totalNumFrames(self, s):
        """Returns the actual number of internal frames from a slice object.""" 
        return len(range(s.start or 0, s.stop, s.step or 1))
    
    def intFrameNum(self, theExtFrameNum):
        """Given an external frame number this returns the internal frame number.
        Will raise an IndexError if the internal frame number is out of
        range or the external frame number is not in the caller specified
        slice object."""
        span = theExtFrameNum - self._frameSlice.start
        if span % self._frameSlice.step != 0:
            raise IndexError('FrameSet.intFrameNum(): external frame number {:d} not in slice.'.format(theExtFrameNum))
        retIdx = span // self._frameSlice.step
        if retIdx >= len(self._frames):
            raise IndexError('FrameSet.intFrameNum(): external frame number {:d} over range.'.format(theExtFrameNum))
        if retIdx < 0:
            raise IndexError('FrameSet.intFrameNum(): external frame number {:d} under range.'.format(theExtFrameNum))
        return retIdx

    def extFrameNum(self, theIntFrameNum):
        """Given an internal frame number this returns the external frame number.
        This does _not_ test that the internal frame number exists."""
        return theIntFrameNum * self._frameSlice.step + self._frameSlice.start 
    #====================================================
    # End: Frame information, access and manipulation
    #====================================================
    
    #=============================
    # Section: Channel information
    #=============================
    @property
    def numChannels(self):
        """The number of _internal_ channels."""
        return len(self._catS)
    
    def numSubChannels(self, theChExt):
        """Number of sub-channels for an external channel."""
        return self._catS[self.internalChIdx(theChExt)].numSubChannels
    
    def numSamples(self, theChExt, theSc):
        """Number of samples for the external channel, sub-channel."""
        return self._catS[self.internalChIdx(theChExt)][theSc].samples
    
    def numBursts(self, theChExt, theSc):
        """Number of bursts for the external channel, sub-channel."""
        return self._catS[self.internalChIdx(theChExt)][theSc].bursts
    #=============================
    # End: Channel information
    #=============================

    #================================
    # Section: Indirect X information
    #================================
    @property
    def isIndirectX(self):
        """True if there is an indirect X axis, False otherwise."""
        return self._xAxisDecl.isIndirectX
    
    @property
    def xAxisDecl(self):
        """The XAxisDecl object created from the DFSR."""
        return self._xAxisDecl
    #================================
    # End: Indirect X information
    #================================

    #===========================
    # Section: Populating values
    #===========================
    def setFrameBytes(self, by, fr, chFrom, chTo):
        """Given bytes, convert from Rep Codes to 'float64' and populates the
        appropriate frame and channel(s). This has random write access so the
        caller needs to be sensitive to the frame and channel location.
        fr is the internal frame position to write the data to.
        chFrom, chTo are inclusive and represent external channel indices.
        
        **WARNING:** It is rare to use this API directly, instead a FrameSet object
        is usually a member of a LogPass object and that uses this API as a LogPass is
        capable of finding and reading bytes objects in a file (a LogPass uses
        RLE and Type01Plan objects to do this efficiently).
        """
        assert(chFrom is None or chFrom <= chTo)
        assert(by is not None)
        #print('FrameSet.setFrameBytes():', by, fr, chFrom, chTo)
        byOfs = 0
        # If chFrom is None this is indirect depth
        if chFrom is None:
            if not self.isIndirectX:
                raise ExceptionFrameSet('FrameSet.setFrameBytes() chFrom is None when direct Xaxis')
            # The first word of by is the actual indirect X value
            byOfsEnd = RepCode.wordLength(self._xAxisDecl.depthRepCode)
            try:
                self.setIndirectX(fr, RepCode.readBytes(self._xAxisDecl.depthRepCode, by[:byOfsEnd]))
            except RepCode.ExceptionRepCode as err:
                raise ExceptionFrameSet(str(err))
            # Otherwise more consecutive channels to come, chFrom 0 follows None
            byOfs = byOfsEnd
            chFrom = 0
        # chTo as None means just a single read of the indirect X channel
        if chTo is not None:
            arrayPos = self.valueIdxStartExtCh(chFrom)
            chInt = self.internalChIdx(chFrom)
            #print('range(chFrom, chTo+1)', range(chFrom, chTo+1))
            for chExt in range(chFrom, chTo+1):
                #assert(arrayPos == self.valueIdxStartExtCh(chExt))
                myCat = self._catS[chInt]
                # TODO: Possible optimisation here, treat multi-sampled channels
                # (or all channels) as we do reading dipmeter channels i.e.
                # RepCode.readBytes() reads all values and returns a list
                for i in range(myCat.numValues):
#                    # For the moment be a bit clunky and treat dipmeter codes
#                    # separately.
#                    if myCat.repCode in RepCode.DIPMETER_REP_CODES:
#                        byOfsEnd = byOfs + myCat.lisSize
#                    else:
#                        byOfsEnd = byOfs + myCat.wordLength
                    byOfsEnd = byOfs + myCat.wordLength
                    # Note: RepCode.readBytes() returns a single value
                    # except with dipmeter codes when it returns a list of values.
                    try:
                        val = RepCode.readBytes(myCat.repCode, by[byOfs:byOfsEnd])
                    except RepCode.ExceptionRepCode as err:
                        raise ExceptionFrameSet(str(err))
                    else:
                        if isinstance(val, list):
                            # Set numpy slice, for example
                            #>>> y = np.array([[0, 1, 2, 3, 4,], [5, 6, 7, 8, 9]])
                            #>>> y
                            #array([[0, 1, 2, 3, 4],
                            #       [5, 6, 7, 8, 9]])
                            #>>> y[1, 1:4] = [1,4,6]
                            #>>> y
                            #array([[0, 1, 2, 3, 4],
                            #       [5, 1, 4, 6, 9]])
                            self._frames[fr, arrayPos:arrayPos+len(val)] = val
                            arrayPos += len(val)
                        else:
                            self._frames[fr, arrayPos] = val
                            arrayPos += 1
                    byOfs = byOfsEnd
                chInt += 1
        if byOfs != len(by):
            raise ExceptionFrameSet('FrameSet.setFrameBytes() length missmatch byOfs={:d} len(by)={:d}'.format(byOfs, len(by)))

    def setIndirectX(self, fr, val):
        """Sets an indirect X axis value directly, for example with an EXTRAPOLATE event."""
        assert(self._indrXVector is not None)
        #print('FrameSet.setIndirectX({:d}, {:g})'.format(fr, val))
        self._indrXVector[fr] = val
    #===========================
    # Section: Populating values
    #===========================
    
    #===================================
    # Section: Indexing and value access
    #===================================
    def internalChIdx(self, chIdxExt):
        """Return the internal channel index from the external one."""
        if self._chIdxExtIntMap is None:
            # In this case self._chIdxIntExt is a list(range(numExtCh)) so
            # is the identity list i.e. i = self._chIdxIntExt[i]
            # We use it 'in reverse' to provokes an IndexError and handle
            # negative indexes
            return self._chIdxIntExt[chIdxExt]
        try:
            # Figure out negative indexes
            if chIdxExt < 0:
                chIdxExt = self._numExtChannels + chIdxExt
            return self._chIdxExtIntMap[chIdxExt]
        except KeyError as err:
            raise IndexError(str(err))

    def valueIdxStartExtCh(self, ch):
        """The index in the frame of the first value for external channel."""
        return self._intChValIdxS[self.internalChIdx(ch)]

    def valueIdxInFrame(self, ch, sc, sa, bu):
        """The index in the frame of the value for (external channel, sub-channel, sample, burst).
        TODO: Provide an API that returns a numpy view of a ch/sc on the frameset."""
        #chInt = self.internalChIdx(ch)
        #return self._intChValIdxS[chInt] + self._catS[chInt].index(sc, sa, bu)
        try:
            return self._offsetTree[self.internalChIdx(ch)][sc][sa][bu]
        except KeyError as err:
            raise IndexError(str(err))
    
    def value(self, fr, ch, sc, sa, bu):
        """Returns a single value from an: internal fr, external ch, sc, sa, bu.
        This is very good at random access but can be quite slow for iteration
        compared to the generators."""
#        chInt = self.internalChIdx(ch)
#        i = self._intChValIdxS[chInt]
#        i += self._catS[chInt]._index(sc, sa, bu)
        return self._frames[fr, self.valueIdxInFrame(ch, sc, sa, bu)]
    
    def frameView(self, chIdxExt, sc):
        """Returns a numpy array that is a view of the current frame set for an
        external channel and sub channel."""
        chIdxInt = self.internalChIdx(chIdxExt)
        return self._frames[:,self._sliceTree[chIdxInt][sc]]
    
#    def _value(self, fr, chInt, sc, sa, bu):
#        """Returns a single value from an: internal fr, external ch, sc, sa, bu."""
#        i = self._intChValIdxS[chInt]
#        i += self._catS[chInt]._index(sc, sa, bu)
#        return self._frames[fr, i]
    
    def _retFirstXaxisFrameSpacing(self, theSamples):
        """Returns a pair (initial X, frame spacing) as floats given the 
        number of samples from an internal channel index.
        The initial X reflects the number of samples, if >1 then will be the
        extrapolated frame prior to the first actual X axis reading.
        The frame spacing may be 0.0 if a single frame and direct X and single
        sampled i.e. X axis extrapolation does not matter.
        May raise an ExceptionFrameSet if computation not possible, for example
        when there is one frame, no declared spacing and multiple samples."""
        if self.isIndirectX:
            # Indirect X
            assert(len(self._indrXVector) == self.numFrames)
            # raise if indirect X has no frame spacing as this is illegal in LIS
            assert(self._frameSpacing is not None), 'Can not extrapolate X axis when indirect X and no declared spacing in the DFSR. FrameSet.__init__() should have raised exception.'
            myFrSp = self._frameSpacing
            myX = self._indrXVector[0]
        else:
            # Direct X, we have to make a few choices about frame spacing here
            myX = self._frames[0, self._xAxisFrOffs]
            if self.numFrames > 1:
                # Here we take the extreme X values and divide by the 
                # total number of frames (including ones stepped over).
                xDiff = self._frames[-1, self._xAxisFrOffs] - self._frames[0, self._xAxisFrOffs]
                assert(self._frameSlice.step > 0)
                myFrSp = xDiff / ((self.numFrames -1) * self._frameSlice.step)
            else:
                # Single frame, if the number of samples of the ch,sc > 1 and
                # there is no declared frame spacing then we raise as we can
                # not interpolate the Xaxis for the samples
                if theSamples > 1:
                    if self._xAxisDecl.frameSpacing is None:
                        # Multiple samples, single frame and no spacing
                        # information so raise
                        raise ExceptionFrameSetNULLSpacing('FrameSet can not extrapolate X axis when there is one frame, no declared spacing in the DFSR and multiple samples.')
                    else:
                        # Have declared frame spacing so use it
                        myFrSp = self._xAxisDecl.frameSpacing
                else:
                    # Single frame but single sampled, don't have to interpolate
                    myFrSp = 0.0
        # We estimate the previous frame X from the frame spacing
        if theSamples > 1:
            # Extrapolate to previous frame
            myX -= myFrSp
        return myX, myFrSp
    
    def genExtChIndexes(self):
        """Generates an ordered list of external channel indexes for this
        (possibly) partial frameset."""
        for i in range(len(self._chIdxIntExt)):
            yield self._chIdxIntExt[i]
    
    def genChScValues(self, ch, sc=0, chIsExternal=True):
        """Generates values for the external channel and sub channel.
        sc is ignored unless the channel has > 1 sub-channels.
        If chIsExternal is True then ch is the external channel index otherwise
        it is the internal index.
        The value order is sample/burst."""
        if self.numFrames > 0:
            # We optimise for two common use cases to minimise looping constructs:
            # - Single sub-channel, single value. Yield each frame value.
            # - Single sub-channel, multiple values. Yield all frame values.
            if chIsExternal:
                # Internalise channel indes
                ch = self.internalChIdx(ch)
            myCat = self._catS[ch]
            # Range check sub-channel index and fix negative indexing
            if sc != 0:
                sc = chkIdx(sc, myCat.numSubChannels, 'FrameSet.genChScValues(): sub-channel {:d} not in array length {:d}')
            fOfsStart = self._intChValIdxS[ch]
            if myCat.numValues == 1:
                # Single sub-channel, single value
                for f in range(self.numFrames):
                    yield self._frames[f, fOfsStart]
            elif myCat.numSubChannels == 1:
                # Single sub-channel, multiple values
                myRange = range(myCat.numValues)
                for f in range(self.numFrames):
                    for vIdx in myRange:
                        yield self._frames[f, fOfsStart+vIdx]
            else:
                # Non-optimised version that does the whole thing
                # Multiple values and multiple sub-channels,
                # this can (should) only be dipmeter data
                assert(myCat.repCode in RepCode.DIPMETER_REP_CODES), 'Rep Code {:d} not a dipmeter code'.format(myCat.repCode)
                # Fast or slow channel?
                if sc < RepCode.DIPMETER_NUM_FAST_CHANNELS:
                    # Fast
                    myRange = RepCode.DIPMETER_FAST_SUB_CHANNEL_RANGES[sc]
                    for f in range(self.numFrames):
                        for vIdx in myRange:
                            yield self._frames[f, fOfsStart+vIdx]
                else:
                    # Slow
                    myOfs = fOfsStart \
                            + RepCode.DIPMETER_SIZE_FAST_CHANNELS \
                            + (sc - RepCode.DIPMETER_NUM_FAST_CHANNELS)
                    for f in range(self.numFrames):
                        yield self._frames[f, myOfs]

    def _genChScPointsSingle(self, frOfs):
        """Yield (x, v) floats for a single value at the supplied offset.
        This is for a channel that has a single sub-channel, single value."""
        assert(self.numFrames > 0)
        assert(frOfs >=0 and frOfs < self.valuesPerFrame)
        if self.isIndirectX:
            # Indirect X
            assert(len(self._indrXVector) == self.numFrames)
            for f in range(self.numFrames):
                yield self._indrXVector[f], self._frames[f, frOfs]
        else:
            # Direct X
            for f in range(self.numFrames):
                yield self._frames[f, self._xAxisFrOffs], self._frames[f, frOfs]

    def _genChScPointsBurstOnly(self, chInt):
        """Yield (x, v) floats for all the values for the internal channel.
        This is for channels that have a single sub-channel and single sample
        assert(self.numFrames > 0)
        This is burst data only so all values are 'aligned' with the X value."""
        assert(self._catS[chInt].numSubChannels == 1)
        myRange = range(self._catS[chInt].numValues)
        frOfs = self._intChValIdxS[chInt]
        if self.isIndirectX:
            # Indirect X
            assert(len(self._indrXVector) == self.numFrames)
            for f in range(self.numFrames):
                myX = self._indrXVector[f]
                for vIdx in myRange:
                    yield myX, self._frames[f, frOfs+vIdx]
        else:
            # Direct X
            for f in range(self.numFrames):
                myX = self._frames[f, self._xAxisFrOffs]
                for vIdx in myRange:
                    yield myX, self._frames[f, frOfs+vIdx]

    def _geChScPointsAll(self, chInt, sc):
        """Yield (x, v) floats for all the samples of a channel/sub-channel.
        The X axis is interpolated for each sample."""
        assert(self.numFrames > 0)
        #assert(self._catS[chInt].numSubChannels > 1), str(self._catS[chInt])
        # Super-sampled channels need fractional X axis values.
        # The formulae is:
        # X(n,ch,s,b) = X[fn-1] - (1+s)*(X[fn-1] - X[fn]) / sa
        # Where:
        # X(n,sc,s,b) ~ The X value for a frame, sub-channel, sample, burst.
        # X[fn-1] ~ X axis for the previous frame.
        # X[fn] ~ X axis for the current frame.
        # s ~ The sample number 0 <= s < sa
        # sa ~ The number of samples for this sub-channel.
        # This is implemented as applying a difference.
        # dx/ds = (X[fn] - X[fn-1]) / sa
        #
        myCat = self._catS[chInt]
        # Compute the frame spacing
        myX, myFrSp = self._retFirstXaxisFrameSpacing(myCat[sc].samples)
        # Caluculae incremental X per sample
        mySaSp = myFrSp / myCat[sc].samples
        myBursts = myCat[sc].bursts
        myRange = myCat.subChOffsRange(sc)
        #print('myCat.subChOffsRange({:d})'.format(sc), myCat.subChOffsRange(sc))
        chFrOfs = self._intChValIdxS[chInt]
        if self.isIndirectX:
            # Indirect X
            assert(len(self._indrXVector) == self.numFrames)
            for f in range(self.numFrames):
                for vIdx in myRange:
                    if vIdx % myBursts == 0:
                        myX += mySaSp
                    yield myX, self._frames[f, chFrOfs+vIdx]
                myX = self._indrXVector[f]
        else:
            # Direct X
            for f in range(self.numFrames):
                for vIdx in myRange:
                    if vIdx % myBursts == 0:
                        myX += mySaSp
                    yield myX, self._frames[f, chFrOfs+vIdx]
                # If self._frameSlice.step == 1 we can use this frame for
                # X the next time around
                if self._frameSlice.step == 1:
                    myX = self._frames[f, self._xAxisFrOffs]
                else:
                    # We have to estimate myX as to what would be immediately
                    # before the next frame
                    if f+1 < self.numFrames:
                        myX = self._frames[f+1, self._xAxisFrOffs] - myFrSp
                    else:
                        # Force myX to be unusable at end of loop
                        myX = None
    
    def genChScPoints(self, ch, sc=0, chIsExt=True):
        """Generates (xAxis, values) as numbers for the external channel and
        sub-channel. sc is ignored unless the channel has > 1 sub-channels.
        If chIsExt is True then ch is the external channel index otherwise
        it is the internal index."""
        if self.numFrames > 0:
            # We optimise for two common use cases to minimise looping constructs:
            # - Single sub-channel, single value. Yield each frame value.
            # - Single sub-channel, multiple values. Yield all frame values.
            if chIsExt:
                # Internalise channel index
                ch = self.internalChIdx(ch)
            myCat = self._catS[ch]
            # Range check sub-channel index and fix negative indexing
            if sc != 0:
                sc = chkIdx(sc, myCat.numSubChannels, 'FrameSet.genChScValues(): sub-channel {:d} not in array length {:d}')
            if myCat.numValues == 1:
                # Single sub-channel, single value
                for p in self._genChScPointsSingle(self._intChValIdxS[ch]):
                    yield p
            elif myCat.numSubChannels == 1:
                # Single sub-channel, multiple values
                if myCat[0].samples == 1:
                    # Simplified code for single sampled curves, all values are 'aligned'
                    for p in self._genChScPointsBurstOnly(ch):
                        yield p
                else:
                    for p in self._geChScPointsAll(ch, sc):
                        yield p                
            else:
                # Non-optimised version that does the whole thing
                # Multiple values and multiple sub-channels,
                # this can (should) only be dipmeter data
                assert(myCat.repCode in RepCode.DIPMETER_REP_CODES), 'Rep Code {:d} not a dipmeter code'.format(myCat.repCode)
                # Fast or slow channel?
                if sc < RepCode.DIPMETER_NUM_FAST_CHANNELS:
                    for p in self._geChScPointsAll(ch, sc):
                        yield p                
                else:
                    # Slow channel so treat as a single sampled sub-channel
                    frOfs = self._intChValIdxS[ch] \
                            + RepCode.DIPMETER_SIZE_FAST_CHANNELS \
                            + (sc - RepCode.DIPMETER_NUM_FAST_CHANNELS)
                    for p in self._genChScPointsSingle(frOfs):
                        yield p

    def _checkShapes(self, theIntChScS):
        """Checks a non-empty list of (ch,sc) and returns the tuple of
        shape (samples, bursts).
        Raises an ExceptionFrameSetMixedChannels if all intCh/sc channels
        are not of the same form i.e. number of samples and bursts."""
        assert(len(theIntChScS) > 0)
        saBu = None
        for ch, sc in theIntChScS:
            mySaBu = (self._catS[ch][sc].samples, self._catS[ch][sc].bursts)
            if saBu is None:
                saBu = mySaBu
            elif saBu != mySaBu:
                raise ExceptionFrameSetMixedChannels('FrameSet._checkShapes(): Shape missmatch: {:s} does not match {:s}'.format(mySaBu, saBu))
        return saBu
    
    def _retChScOffsets(self, theIntChScS):
        """Given a list of (ch, sc) this returns a list of integers that are
        the (partial) frame offsets of the start of that (internal) ch/sc."""
        try:
            return [self._offsetTree[ch][sc][0][0] for ch,sc in theIntChScS]
        except KeyError as err:
            raise IndexError(str(err))

    def _genMultipleChScPointsSingle(self, frOfsS):
        """Yield (x, (v, ...)) floats for a single value at the supplied offset.
        This is for a channel that has a single sub-channel, single value.
        NOTE: (v...) is a generator object."""
        assert(self.numFrames > 0)
        assert(frOfs >=0 and frOfs < self.valuesPerFrame for frOfs in frOfsS)
        if self.isIndirectX:
            # Indirect X
            assert(len(self._indrXVector) == self.numFrames)
            for f in range(self.numFrames):
                yield self._indrXVector[f], (self._frames[f, frOfs] for frOfs in frOfsS)
        else:
            # Direct X
            for f in range(self.numFrames):
                yield self._frames[f, self._xAxisFrOffs], (self._frames[f, frOfs] for frOfs in frOfsS)

    def genMultipleChScPoints(self, theChScS, chIsExt=True):
        """Generates (xAxis, (values, ...)) as numbers for the list of
        (channel, sub-channel) indexes.
        An ExceptionFrameSetMixedChannels will be raised if all ch/sc channels
        are not of the same form i.e. number of samples and bursts.
        If chIsExt is True then ch is the external channel index otherwise
        it is the internal index."""
        assert(0)
        if self.numFrames > 0 and len(theChScS) > 0:
            if chIsExt:
                # Internalise channel index
                myChScS = [(self.internalChIdx(cs[0]), cs[1]) for cs in theChScS]
            else:
                myChScS = theChScS
            # This might raise
            mySa, myBu = self._checkShapes(myChScS)
            # We optimise for two common use cases to minimise looping constructs:
            # - Single sub-channel, single value. Yield each frame value.
            # - Single sub-channel, multiple values. Yield all frame values.
            #
            # If a single sample then number of sub-channels is 1
            if mySa * myBu == 1:
                # Compute offsets for each channel
                myFrOffs = self._retChScOffsets(myChScS)
            else:
                assert(0)
    
    def genAll(self):
        """Yields 6 item tuples (fr ext, ch ext, sc, sa, bu value)."""
        for frInt in range(self.numFrames):
            frExt = self.extFrameNum(frInt)
            fOfs = 0
            for chInt, cat in enumerate(self._catS):
                chExt = self._chIdxIntExt[chInt]
                # Optimise for the common uses cases of:
                # - Single sub-channel, single sample and single burst
                if cat.numSubChannels == 1 \
                and cat[0].numValues == 1:
                    # Single sub-channel, single sample, single burst optimisation 
                    yield frExt, chExt, 0, 0, 0, self._frames[frInt, fOfs]
                    fOfs += 1
                else:
                    # Multiple sub-channels/samples or bursts so do the whole thing
                    for sc in range(cat.numSubChannels):
                        myBursts = cat[sc].bursts
                        scOffs = 0
                        for v in range(cat[sc].numValues):
                            sa = scOffs // myBursts
                            bu = scOffs % myBursts
                            yield frExt, chExt, sc, sa, bu, self._frames[frInt, fOfs]
                            fOfs += 1
                            scOffs += 1

#    def genAlignedValues(self):
#        """Yields 2 item pair (fr ext, (sub-channel values, ...)) where each
#        sub-channel value is the one aligned with the frame i.e. the first burst
#        of the last 
#        sample."""
#        for frInt in range(self.numFrames):
#            frExt = self.extFrameNum(frInt)
#            fOfs = 0
#            for chInt, cat in enumerate(self._catS):
#                pass

    #===================================
    # End: Indexing and value access
    #===================================
    
    #==================================================
    # Section: Mutation and functional programming etc.
    #==================================================
    def _raiseOnEmpty(self):
        """Will raise a ExceptionFrameSetEmpty if there are no values to analyse."""
        if self.numFrames < 1 or self.numChannels < 1:
            raise ExceptionFrameSetEmpty(
                'FrameSet.accumulate(): empty with numFrames={:d} numChannels={:d}'.format(
                    self.numFrames,
                    self.numChannels,
                )
            )
    
    def _retAccumulatorArray(self, theAccs):
        """Returns a 2D list of accumulator objects, length being the total
        number of sub-channels, width being the number of accumulator classes."""
        accArray = [] 
        for chInt in range(self.numChannels):
            for sc in range(self._catS[chInt].numSubChannels):
                accArray.append([a() for a in theAccs])
        return accArray
    
    def _retAccumulatorValues(self, theAccArray):
        """Extract values from accumulators by invoking value() on each.
        theAccArray length being the total number of sub-channels, width being 
        the number of accumulator classes.
        Returns a numpy array of (numSubCh, len(theAccs))
        """
        numSubCh = len(theAccArray)
        assert(numSubCh > 0)
        numAccs = len(theAccArray[0])
        assert(numAccs > 0)
        # Now extract values
        retArr = numpy.empty((numSubCh, numAccs), self.NUMPY_DATA_TYPE)
        scOfs = 0
        for chInt in range(self.numChannels):
            for sc in range(self._catS[chInt].numSubChannels):
                for a in range(numAccs):
                    retArr[scOfs, a] = theAccArray[scOfs][a].value()
                scOfs += 1
        return retArr
    
    def accumulate(self, theAccs):
        """Calls .add() on every accumulator (with a unary function) for every
        internal channel and returns an numpy array of (numSubCh, len(theAccs))
        doubles. Each accumulator is expected to have __init__(), add() and
        value() that returns a double implemented.
        Will raise a ExceptionFrameSetEmpty if there are no values to analyse.
        Will return None if theAccs is zero length."""
        self._raiseOnEmpty()
        if len(theAccs) == 0:
            return None
        # Create array of accumulator objects (num sub-channels, num accumulators)
        accArray = self._retAccumulatorArray(theAccs)
        # Check length is total number of sub-channels
        assert(len(accArray) == sum([c.numSubChannels for c in self._catS]))
        accArrayOffs = 0
        for chInt in range(self.numChannels):
            for sc in range(self._catS[chInt].numSubChannels):
                for v in self.genChScValues(chInt, sc, chIsExternal=False):
                    if v != self._absentValue:
                        for a in range(len(theAccs)):
                            accArray[accArrayOffs][a].add(v)
                accArrayOffs += 1
        return self._retAccumulatorValues(accArray)    
    #==================================================
    # End: Mutation and functional programming etc.
    #==================================================
#############################
# End: FrameSet container
#############################

#########################################
# Section: FrameSet accumulator functions
#########################################
class AccMin(object):
    """Accumulates the minimum value."""
    def __init__(self):
        self.min = None
    
    def add(self, v):
        """Add a new value."""
        if self.min is None or v < self.min:
            self.min = v

    def value(self):
        """Return the result."""
        return self.min

class AccMax(object):
    """Accumulates the maximum value."""
    def __init__(self):
        self.max = None
    
    def add(self, v):
        """Add a new value."""
        if self.max is None or v > self.max:
            self.max = v

    def value(self):
        """Return the result."""
        return self.max

class AccMean(object):
    """Accumulates the mean value."""
    def __init__(self):
        self.sum = 0.0
        self.cntr = 0
    
    def add(self, v):
        """Add a new value."""
        self.sum += v
        self.cntr += 1

    def value(self):
        """Return the result."""
        if self.cntr > 0:
            return self.sum / self.cntr

class AccStDev(object):
    """Accumulates the standard deviation."""
    def __init__(self):
        self.sum = 0.0
        self.sumSq = 0.0
        self.cntr = 0
    
    def add(self, v):
        """Add a new value."""
        self.sum += v
        self.sumSq += v**2
        self.cntr += 1

    def value(self):
        """Return the result."""
        if self.cntr > 1:
            # From http://en.wikipedia.org/wiki/Standard_deviation
            num = self.cntr * self.sumSq - self.sum**2
            if num > 0:
                den = self.cntr * (self.cntr - 1)
                return math.sqrt(num / den)

class AccCount(object):
    """Accumulates the number of values."""
    def __init__(self):
        self.cntr = 0
    
    def add(self, v):
        """Add a new value."""
        self.cntr += 1

    def value(self):
        """Return the result."""
        return self.cntr


class AccDelta(object):
    """Base class for acumulating a count of first order differences."""
    def __init__(self):
        self.cntr = 0
        self.prev = None
    
    def add(self, v):
        """Add a new value."""
        raise NotImplementedError

    def value(self):
        """Return the result."""
        return self.cntr


class AccInc(AccDelta):
    """Counting how many values are an increase from the previous value."""
    def add(self, v):
        """Add a new value."""
        if self.prev is None:
            self.prev = v
        elif self.prev < v:
            self.cntr += 1
        self.prev = v


class AccEq(AccDelta):
    """Counting how many values are equal to the previous value."""
    def add(self, v):
        """Add a new value."""
        if self.prev is None:
            self.prev = v
        elif self.prev == v:
            self.cntr += 1
        self.prev = v


class AccDec(AccDelta):
    """Counting how many values are less than the previous value."""    
    def add(self, v):
        """Add a new value."""
        if self.prev is None:
            self.prev = v
        elif self.prev > v:
            self.cntr += 1
        self.prev = v


class AccBias(AccDelta):
    """Measures increment, equal, decrement and computes bias which is:
    (inc - dec) / total."""
    def __init__(self):
        super().__init__()
        self.cntrInc = self.cntrEq = self.cntrDec = 0
    
    def add(self, v):
        """Add a new value."""
        if self.prev is None:
            self.prev = v
        elif self.prev > v:
            self.cntrInc += 1
        elif self.prev == v:
            self.cntrEq += 1
        elif self.prev < v:
            self.cntrDec += 1
        self.prev = v

    def value(self):
        """Return the result."""
        return (self.cntrInc - self.cntrDec) / (self.cntrInc + self.cntrEq + self.cntrDec)

class AccDrift(AccDelta):
    """Measures drift i.e. the movement between the first and the last value."""
    def __init__(self):
        super().__init__()
        self.first = None
        self.last = None
    
    def add(self, v):
        """Add a new value."""
        if self.first is None:
            self.first = v
        self.last = v
        self.cntr += 1

    def value(self):
        """Return the result."""
        if self.first is not None and self.last is not None:
            return (self.last - self.first) / self.cntr
        return 0

class AccActivity(AccDelta):
    """Measures curve activity."""
    def __init__(self):
        super().__init__()
        self.prevExp = None
        self.actSum = 0.0
    
    def add(self, v):
        """Add a new value."""
        myMant, exp = math.frexp(v)
        myExp = exp + (2 * myMant) - 1.0
        if self.cntr > 0:
            self.actSum += (myExp - self.prevExp)**2
        self.prevExp = myExp
        self.cntr += 1

    def value(self):
        """Return the result."""
        if self.cntr > 0:
            return math.sqrt(self.actSum / self.cntr)
        return 0

#########################################
# Section: FrameSet accumulator functions
#########################################
