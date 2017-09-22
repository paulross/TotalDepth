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
"""Given a DFSR the FrameSetPlan gives offsets to any part of the Logical Record
for any frame and channel.
"""

__author__  = 'Paul Ross'
__date__    = '2011-01-06'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

#import time
#import sys
#import logging
#import collections

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import RepCode

class ExceptionFrameSetPlan(ExceptionTotalDepthLIS):
    """Specialisation of exception for FrameSetPlan."""
    pass

class ExceptionFrameSetPlanNegLen(ExceptionFrameSetPlan):
    """Specialisation of exception for negative/too small length arguments to FrameSetPlan."""
    pass

class ExceptionFrameSetPlanOverrun(ExceptionFrameSetPlan):
    """Exception channel number greater than available."""
    pass

#: Read event
EVENT_READ          = 'read'
#: Skip event
EVENT_SKIP          = 'skip'
#: Extrapolate event
EVENT_EXTRAPOLATE   = 'extrapolate'

class FrameSetPlan(object):
    """Given a DFSR the FrameSetPlan gives offsets to any part of the frame set
    within a Logical Record.
    
    NOTE: All offsets, lengths etc. are relative to the end of the LRH
    i.e. add LR_HEADER_LENGTH to get absolute Logical Data position."""            
    def __init__(self, dfsr):
        if dfsr.ebs.recordingMode:
            self._indirectSize = RepCode.lisSize(dfsr.ebs.depthRepCode)
        else:
            self._indirectSize = 0
        # Individual channel sizes
        self._channelSizes = [b.size for b in dfsr.dsbBlocks]
        # Sum the frame size
        self._frameSize = sum(self._channelSizes)
        # Set up skip lists [integer_byte_length, ...]
        # Distance from start of frame to start of channel
        self._skipToChStart = []
        # Distance end of channel to end of frame
        self._skipToFrameEnd = []
        toEnd = self._frameSize
        fromStart = 0
        for b in dfsr.dsbBlocks:
            self._skipToChStart.append(fromStart)
            toEnd -= b.size
            self._skipToFrameEnd.append(toEnd)
            fromStart += b.size
        # Integrity checks
        assert(toEnd == 0)
        assert(len(self._channelSizes) == len(self._skipToChStart))
        assert(len(self._channelSizes) == len(self._skipToFrameEnd))
        assert(sum(self._channelSizes) == self._frameSize)
        assert(fromStart == self._frameSize)
    
    def __str__(self):
        return '{:s}: indr={:d} frame length={:d} channels={:d}'.format(
            repr(self),
            self._indirectSize,
            self.frameSize,
            self.numChannels,
        )
    
    @property
    def indirectSize(self):
        """The size, in bytes of the indirect X axis value. 0 for explicit X axis."""
        return self._indirectSize
    
    @property
    def frameSize(self):
        """Frame size in bytes."""
        return self._frameSize

    @property
    def numChannels(self):
        """Number of channels."""
        return len(self._channelSizes)

    def channelSize(self, i):
        """The size of the given channel."""
        return self._channelSizes[i]

    def numFrames(self, recLen):
        """Returns the number of frames that will fit into the record length.
        May raise a ExceptionFrameSetPlan. May raise ExceptionFrameSetPlanNegLen
        if arguments are negative.
        
        NOTE: record length should not include size of LRH."""
        if recLen < 0:
            raise ExceptionFrameSetPlanNegLen('FrameSetPlan.numFrames(): recLen {:d} negative'.format(recLen))
        myLen = recLen - self._indirectSize
        if myLen % self._frameSize != 0:
            raise ExceptionFrameSetPlan(
                'Can not fit integer number of frames length {:d} into LR length {:d}, modulo {:d} [indirect size {:d}].'.format(
                        self._frameSize, myLen, myLen % self._frameSize, self._indirectSize)
                )
        return myLen // self._frameSize
    
    def _chOffset(self, f, c):
        """Returns the offset into the LR (after LRH) to the start of a
        particular channel and frame. No range checking is performed."""
        return self._indirectSize + self._skipToChStart[c] + f * self._frameSize
    
    def chOffset(self, frame, ch):
        """Returns the offset into the LR (after LRH) to the start of a particular channel and frame.
        
        Will raise ExceptionFrameSetPlanNegLen if arguments are negative or an IndexError if ch out of range."""
        if ch < 0:
            raise ExceptionFrameSetPlanNegLen('FrameSetPlan.chOffset(): channel number {:d} negative'.format(ch))
        if frame < 0:
            raise ExceptionFrameSetPlanNegLen('FrameSetPlan.chOffset(): frame number {:d} negative'.format(frame))
        return self._chOffset(frame, ch)
    
    def skipToEndOfFrame(self, ch):
        """Returns the skip distance into the LR to the end of frame after a
        particular channel."""
        if ch < 0:
            raise ExceptionFrameSetPlanNegLen('FrameSetPlan.chOffset(): channel number {:d} negative'.format(ch))
        return self._skipToFrameEnd[ch]

    def _checkChIdx(self, theList):
        """Checks the channel list. Returns the sorted list with no repeated
        items and a flag that if True means the list is non-continuous and
        may need seek events."""
        myList = sorted(list(set(theList)))
        if len(myList) and myList[0] < 0:
            raise ExceptionFrameSetPlanNegLen(
                'FrameSetPlan._checkChIdx(): Negative channels in {:s}.'.format(str(theList))
            )
        if len(myList) and myList[-1] >= self.numChannels:
            raise ExceptionFrameSetPlanOverrun(
                'FrameSetPlan._checkChIdx(): Channels out of range in {:s}.'.format(str(theList))
            )
        return myList
    
    def genOffsets(self, theChIndexS):
        """Yields an indefinite set of (frame, channel, offset) values for the
        set of channels.
        Will raise ExceptionFrameSetPlanNegLen if any channel negative.
        Will raise KeyError if any channel index is out of range."""
        f = 0
        while 1:
            for c in self._checkChIdx(theChIndexS):
                yield f, c, self.chOffset(f, c)
            f += 1

    def _raiseOnFrameSlice(self, fSlice):
        if fSlice.stop < 0:
            raise ExceptionFrameSetPlanNegLen(
                'FrameSetPlan: Negative frame stop {:s}.'.format(str(fSlice.stop))
            )
        if fSlice.start < 0:
            raise ExceptionFrameSetPlanNegLen(
                'FrameSetPlan: Negative frame start {:s}.'.format(str(fSlice.start))
            )
        if fSlice.step < 1:
            raise ExceptionFrameSetPlanNegLen(
                'FrameSetPlan: Negative frame step {:s}.'.format(str(fSlice.step))
            )
    
    def _retFrameEvents(self, theChIndexS):
        """Return a tuple of events for a frame of the form:
        (
            pre-event | None,
            [events,]
            post-event | None,
        )
        An event is of the form: (type, size, chStart, chStop)
        Where type is 'read' or 'skip', size is the number of bytes and
        chStart/chStop is the affected channels (inclusive).
        Pre and post events are (optional) skip events. The event list always
        starts ends with a read event.
        Events are concatenated where the type is the same.
        """
        assert(len(theChIndexS) > 0)
        # Now generate canned events for a single frame
        # ('read' | 'skip', siz, None, chStart, chStop
        myFevts = []
        # Skip to first channel if necessary
        if theChIndexS[0] > 0:
            myPre = (EVENT_SKIP, self._skipToChStart[theChIndexS[0]], 0, theChIndexS[0]-1)
        else:
            myPre = None
        chStart = theChIndexS[0]
        chStop = theChIndexS[0] - 1
        siz = 0
        for chIdx in theChIndexS:
            if chIdx == chStop + 1:
                # Contiguous read so just increment channel
                siz += self._channelSizes[chIdx]
                chStop = chIdx
            else:
                # Discontinuity so have to issue a read/skip
                # First add any pending read
                if chStop >= chStart:
                    myFevts.append((EVENT_READ, siz, chStart, chStop))
                # Now skip between channels
                siz = self._skipToChStart[chIdx] - self._skipToChStart[chStop+1]
                assert(siz > 0)
                myFevts.append((EVENT_SKIP, siz, chStop+1, chIdx-1))
                chStart = chIdx
                chStop = chIdx
                siz = self._channelSizes[chIdx]
        # Final read of lazily evaluated data
        if chStop >= chStart:
            myFevts.append((EVENT_READ, siz, chStart, chStop))
        # Finally an optional skip to the end of the frame
        siz = self._skipToFrameEnd[theChIndexS[-1]]
        if siz > 0:
            return myPre, myFevts, (EVENT_SKIP, siz, theChIndexS[-1]+1, self.numChannels-1)
        return myPre, myFevts, None
    
    def _retMergedPostFramePre(self, thePre, thePost, theFstep):
        # Make a merged single event that is post+pre
        siz = 0
        if theFstep > 1:
            siz += (theFstep - 1) * self.frameSize
        if thePost is not None:
            siz += thePost[1]
        if thePre is not None:
            siz += thePre[1]
        if thePost is not None:
            if thePre is not None:
                # Both post and pre
                return EVENT_SKIP, siz, thePost[2], thePre[3]
            else:
                # post only
                return EVENT_SKIP, siz, thePost[2], thePost[3]
        else:
            if thePre is not None:
                # pre ony
                return EVENT_SKIP, siz, thePre[2], thePre[3]
            else:
                # No pre or post, may have frame skip event
                if siz > 0:
                    return EVENT_SKIP, siz, None, None
    
    def genEvents(self, theFSlice, theChIndexS):
        """For a single Logical Record type 0/1 this yields an set of events.
        
        theFSlice is a frame slice object (default start=0, step=1), step 0 is interpreted as step 1.
        
        theChIndexS is as list of indexes of channels that need to be read.
        
        The events are 5 member tuples:
        (event_type, size, frame, channel_start, channel_stop)
        
        event_type is 'skip' or 'read' or 'extrapolate':
        
        skip: ('skip',        size,   frame_number, channel_start, channel_stop)
        
        read: ('read',        size,   frame_number, channel_start, channel_stop)
        
        extrapolate: ('extrapolate', frames, frame_number, None,          None)
        
        NOTE: No 'seek', 0, ... events are generated.
        
        size is the number of bytes to read or skip or, for 'extrapolate' the
        number of frames to extrapolate the implied X axis.
        
        frame_number is the frame number in the predicted Logical Record.
        
        In the case of 'skip' or 'extrapolate' its is the frame number in the
        Logical Record being moved to. The frame number can be None if there
        is no prediction, for example when reading an indirect X at the
        beginning of an LR.
        
        channel_start, channel_stop are the channel numbers (inclusive) in the
        DFSR DSB block None being the indirect X axis.
        
        Thus: ('read', size, frame_number, None, 3)
        Means read size bytes and interpret them as channels: None, 0, 1, 2, 3.
        'extrapolate' events mean project the Xaxis forward by the specified
        number of frames (this will not be bestrided with two seek events but
        preceded or followed by a single seek event (if any). 'read' and 'seek'
        events are synchronous as are 'read' and 'extrapolate'. However 'seek'
        and 'extrapolate' are asynchronous i.e. 'seek'-'extrapolate' is
        equivalent to 'extrapolate'-'seek'.
        
        Will raise ExceptionFrameSetPlanNegLen if any channel negative or fStop < fStart.
        Will raise IndexError if any channel index is out of range.
        
        Be aware: This code is tricky.
        """
        # Interpret slice defaults
        fSlice = slice(theFSlice.start or 0, theFSlice.stop, theFSlice.step or 1)
        # Check input
        myChIndexS = self._checkChIdx(theChIndexS)
        self._raiseOnFrameSlice(fSlice)
        if len(myChIndexS) > 0 \
        and fSlice.stop > fSlice.start:
            # Get the inter-frame events
            myPreEvt, myFevts, myPostEvt = self._retFrameEvents(myChIndexS)
            # Make a merged single event that is post+pre or None
            myInterFrameEvt = self._retMergedPostFramePre(myPreEvt, myPostEvt, fSlice.step)
            # First read X axis at start of LR if indirect
            myIndrReadEvt = None
            if self._indirectSize > 0:
                # If there is a pre event we have to generate a read event here
                # otherwise we can do it lazily with the first read event of the frame
                # Generate read channel None, None event
                myIndrReadEvt = EVENT_READ, self._indirectSize, None, None, None
                if myPreEvt is not None:
                    yield myIndrReadEvt
                    myIndrReadEvt = None
                    # Generate extrapolate event to update X axis
                    if fSlice.start > 0:
                        yield EVENT_EXTRAPOLATE, fSlice.start, fSlice.start, None, None
            # If necessary move to start of first frame or channel
            if myPreEvt is not None:
                # There is a skip event to first channel
                # therefore add
                # any skip to channel event
                siz = fSlice.start * self._frameSize
                # Move to the first channel
                siz += myPreEvt[1]
                yield myPreEvt[0], siz, fSlice.start, myPreEvt[2], myPreEvt[3]
            else:
                # No pre-event but possible move to start of frame
                if fSlice.start > 0:
                    if myIndrReadEvt is not None:
                        yield myIndrReadEvt
                        myIndrReadEvt = None
                    yield EVENT_SKIP, fSlice.start * self._frameSize, fSlice.start, None, 0
                    if self._indirectSize > 0:
                        yield EVENT_EXTRAPOLATE, fSlice.start, fSlice.start, None, None
            # Now we are positioned at the beginning of the first channel,
            # in the first frame of interest.
            f = fSlice.start
            while f < fSlice.stop:
                for typ, siz, chStart, chStop in myFevts:
                    if myIndrReadEvt is None:
                        yield typ, siz, f, chStart, chStop
                    else:
                        assert(self._indirectSize > 0)
                        assert(typ == EVENT_READ)
                        assert(chStart == 0)
                        assert(f == 0)
                        # Merge lazily evaluated event with this one
                        yield typ, myIndrReadEvt[1]+siz, f, None, chStop
                        myIndrReadEvt = None
                # Now at end of frame, increment to next frame
                f += fSlice.step
                if f >= fSlice.stop:
                    # Yield post event to end of frame this makes sure
                    # that the caller is not in mid-frame
                    if myPostEvt is not None:
                        yield myPostEvt[0], myPostEvt[1], f - fSlice.step, myPostEvt[2], myPostEvt[3]
                    break
                # Yield merged post+frame+pre-event
                if myInterFrameEvt is not None:
                    yield myInterFrameEvt[0], myInterFrameEvt[1], f, myInterFrameEvt[2], myInterFrameEvt[3]
                if self._indirectSize > 0:
                    yield EVENT_EXTRAPOLATE, fSlice.step, f, None, None
