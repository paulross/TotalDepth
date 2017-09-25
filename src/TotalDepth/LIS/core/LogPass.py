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
"""The LogPass module contains a single class LogPass that is fundamental to the
way that TotalDepth handles LIS binary data.

A Log Pass is defined as a single continuous recording of log data. "Main Log",
"Repeat Section" are seperate examples of Log Pass(es).
"""

__author__  = 'Paul Ross'
__date__    = '2011-01-10'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

#import time
#import sys
import logging
#import collections
#import array
#import numpy
#import pprint

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import Type01Plan
from TotalDepth.LIS.core import Units
from TotalDepth.LIS.core import Rle
from TotalDepth.LIS.core import RepCode
from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import FrameSet
from TotalDepth.LIS.core import EngVal
from TotalDepth.LIS.core import Mnem

class ExceptionLogPass(ExceptionTotalDepthLIS):
    """Specialisation of exception for LogPass."""
    pass

class ExceptionLogPassCtor(ExceptionLogPass):
    """Specialisation of exception for LogPass __init__()."""
    pass

class ExceptionLogPassNoType01Data(ExceptionLogPass):
    """Raised on access when there is no frame data loaded by addType01Data()."""
    pass

class ExceptionLogPassNoFrameSet(ExceptionLogPass):
    """Raised when FrameSet access is required but there has been no call to setFrameSet()."""
    pass

class ExceptionLogPassKeyError(ExceptionLogPass):
    """Raised when and internal KeyError is raised in a FrameSet access."""
    pass

#: Event to seek to the start of a new Logical Record
EVENT_SEEK_LR       = 'seekLr'
#: Event to read bytes from  frame
EVENT_READ          = Type01Plan.EVENT_READ
#: Event to skip bytes in  frame
EVENT_SKIP          = Type01Plan.EVENT_SKIP
#: Event to extrapolate X axis
EVENT_EXTRAPOLATE   = Type01Plan.EVENT_EXTRAPOLATE

##################
# Section: LogPass
##################
class LogPass(object):
    """Contains the information about a log pass which is defined as a LIS Data
    Format Specification Record (DFSR) plus any number of Type 0/1 Logical Records.
    
    A LogPass must be created with a LIS DFSR and a LIS file ID. It can be then informed
    with addType01Data() which records the file positions of Type 0/1 records.
    When required the actual frame data can be populated with setFrameSet().
    
    theDfsr - The DFSR.

    theFileId - The ID of the file, this will be checked against any File object passed to me.

    xAxisIndex - The index of the DSB block that describes the X axis, if indirect X this is ignored.
    """
    def __init__(self, theDfsr, theFileId, xAxisIndex=0):
        """Constructed with an EFLR i.e. a DFSR
        
        theDfsr - The DFSR.
    
        theFileId - The ID of the file, this will be checked against any File object passed to me.
    
        xAxisIndex - The index of the DSB block that describes the X axis, if indirect X this is ignored.
        """
        # Check input. We take a strict view here of what a LogPass can support
        # The DFSR must have at least one DSB even if indirect X otherwise
        # a LogPass does not make a lot of sense when there are zero channels.
        if len(theDfsr.dsbBlocks) == 0:
            raise ExceptionLogPassCtor('LogPass.__init__(): xAxisIndex no channels to process')
        if xAxisIndex < 0 or xAxisIndex >= len(theDfsr.dsbBlocks):
            raise ExceptionLogPassCtor('LogPass.__init__(): xAxisIndex {:s} out of range when number of DSB blocks={:d}'.format(str(xAxisIndex), len(theDfsr.dsbBlocks)))
        self._dfsr = theDfsr
        self._fileId = theFileId
        self._plan = Type01Plan.FrameSetPlan(self._dfsr)
        self._xAxisIndex = xAxisIndex
        # This is a map of {MNEM : (extCh, sub_ch), ...}
        # Warnings are produced for duplicates which are ignored. In principle
        # as a PRES table (for example) can only identify a channel by MNEM
        # then we assume here that the MNEM is unique.
        self._chMap = self._retChMap()
        # A map of {Mnem.Mnem(MNEM) : Mnem.Mnem(UNITS), ...} from the DFSR
        self._unitMap = self._retUnitMap()
        # Populated by setFrameSet() when the time comes
        self._frameSet = None
        # Set up RLE object
        if self.isIndirectX:
            self._rle = Rle.RLEType01(self._dfsr.ebs.depthUnits)
        else:
            assert(self._xAxisIndex >= 0 and self._xAxisIndex < len(self._dfsr.dsbBlocks))
            self._rle = Rle.RLEType01(self._dfsr.dsbBlocks[self._xAxisIndex].units)

    def _retChMap(self):
        """Returns a map of {Mnem.Mnem(MNEM) : (extCh, sub_ch), ...}
        Warnings are produced for duplicates which are ignored. In principle
        as a PRES table (for example) can only identify a channel by MNEM
        then we assume here that the MNEM is unique."""
        retMap = {}
        for ch, b in enumerate(self._dfsr.dsbBlocks):
            for sc in range(b.subChannels):
                m = b.subChMnem(sc)
                if m is None:
                    logging.warning('LogPass._retChMap() unknown mnemonic: for channel {:d}, sub-channel {:d}'.format(ch, sc))
                elif m in retMap:
                    logging.warning('LogPass._retChMap() ignoring duplicate mnemonic: {:s}'.format(str(m)))
                else:
                    retMap[Mnem.Mnem(m)] = (ch, sc)
        return retMap

    def _retUnitMap(self):
        """Returns a map of {Mnem.Mnem(MNEM) : Mnem.Mnem(UNITS), ...}
        Warnings are produced for duplicates which are ignored. In principle
        as a PRES table (for example) can only identify a channel by MNEM
        then we assume here that the MNEM is unique."""
        retMap = {}
#        for aDsb in self._dfsr.dsbBlocks:
#            m = Mnem.Mnem(aDsb.mnem)
#            if m in retMap:
#                logging.warning('LogPass._retUnitMap() ignoring duplicate mnemonic: {:s}'.format(str(m)))
#            else:
#                retMap[m] = Mnem.Mnem(aDsb.units)
        for ch, aDsb in enumerate(self._dfsr.dsbBlocks):
            # All sub-channels take the same units
            u = aDsb.units
            for sc in range(aDsb.subChannels):
                m = aDsb.subChMnem(sc)
                if m is None:
                    logging.warning('LogPass._retUnitMap() unknown mnemonic: for channel {:d}, sub-channel {:d}'.format(ch, sc))
                elif m in retMap:
                    logging.warning('LogPass._retUnitMap() ignoring duplicate mnemonic: {:s}'.format(str(m)))
                else:
                    retMap[Mnem.Mnem(m)] = u#Mnem.Mnem(u)
        return retMap

    @property
    def dfsr(self):
        """The DFSR used for construction."""
        return self._dfsr
    
    @property
    def type01Plan(self):
        """The Frame plan, a Type01Plan.FrameSetPlan() object."""
        return self._plan
    
    @property
    def rle(self):
        """The Logical Record Run Length Encoding as a Rle.RLEType01() object."""
        return self._rle
    
    @property
    def frameSet(self):
        """The Frame Set as a FrameSet.FrameSet() object or None if not initialised."""
        return self._frameSet
    
    @property
    def iflrType(self):
        """Returns the IFLR type that this LogPass describes."""
        return self._dfsr.ebs.dataType
    
    @property
    def xAxisIndex(self):
        """The channel index that corresponds to the X axis."""
        # TODO: Return None if indirect X???
        return self._xAxisIndex

    @property
    def isIndirectX(self):
        """True if indirect X axis, False if explicit X axis channel."""
        retVal = self._dfsr.ebs.recordingMode == 1
        assert(self._frameSet is None or self._frameSet.isIndirectX == retVal)
        return retVal
    
    @property
    def numBytes(self):
        """The number of bytes in the underlying frame set (i.e. LIS) representation for the curve data.
        Returns None if the frame set is not initialised."""
        if self._frameSet is None:
            return None
        return self._frameSet.lisSize
    
    @property
    def nullValue(self):
        """The NULL or absent value as specified in the DFSR."""
        return self.dfsr.ebs.absentValue

    def longStr(self):
        """Returns a long (multiline) descriptive string."""
        strS = ['{:s}: '.format(repr(self)),]
        strS.append('       DFSR: {:s}'.format(str(self._dfsr)))
        strS.append(' Frame plan: {:s}'.format(str(self._plan)))
        if len(self._dfsr.dsbBlocks) > 8:
            strS.append(
                '   Channels: {:s}'.format(
                    str(
                        '['
                        + ', '.join(
                            [
                                str(b.mnem) for b in self._dfsr.dsbBlocks[:6]
                            ]
                        )
                        + ', .... '
                        + str(self._dfsr.dsbBlocks[-1].mnem)
                        + ']'
                    )
                )
            )
        else:
            strS.append('   Channels: {:s}'.format(str([b.mnem for b in self._dfsr.dsbBlocks])))
        strS.append('        RLE: {:s}'.format(str(self._rle)))
        if self._rle.hasXaxisData:
#            strS.append('     X axis: first={:.3f} last={:.3f} frames={:d} overall spacing={:.4f} units={:s}'.format(
#                        self._rle.xAxisFirst(),
#                        self._rle.xAxisLast(),
#                        self._rle.totalFrames(),
#                        self._rle.frameSpacing(),
#                        self._rle.xAxisUnits,
#                        ))
            strS.append('     X axis: first={:.3f} last={:.3f} frames={:d} overall spacing={:.4f} in optical units={!s:s} (actual units={!s:s})'.format(
                        self.xAxisFirstValOptical,
                        self.xAxisLastValOptical,
                        self._rle.totalFrames(),
                        self.xAxisSpacingOptical,
                        self.xAxisUnitsOptical,
                        self._rle.xAxisUnits,
                        ))
        else:
            strS.append('     X axis: No data.')
        strS.append('  Frame set: {:s}'.format(str(self._frameSet)))
        return '\n'.join(strS)
    
    __str__ = longStr
    
    def frameSetLongStr(self):
        """Returns a long (multiline) descriptive string of the Frame Set or N/A if not initialised."""
        if self._frameSet is None:
            return 'N/A'
        return self._frameSet.longStr()
    
    def curveUnitsAsStr(self, chMnem):
        """Given a curve as a Mnem.Mnem() this returns the units as a string."""
        return self._toAscii(self.curveUnits(chMnem))
    
    def curveUnits(self, chMnem):
        """Given a curve as a Mnem.Mnem() this returns the units as a bytes object."""
        try:
            return self._unitMap[chMnem]
        except KeyError as err:
            raise ExceptionLogPassKeyError('LogPass.curveUnitsAsStr(): {:s}'.format(str(err)))
    
    #===========================================================================
    # Section: X Axis values.
    # TODO: We need to come to some decision(s) about what
    # frame spacing really is. There are a number of candidates:
    # 1. Declared frame spacing (e.g. in the DFSR). This is a-priori. For
    #    indirect X this is all that is needed (unless LRs unordered).
    #    For direct X it is aspirational and possibly misleading.
    # 2. First/last. This takes the first X and the last X and divides it by
    #    the number of frames-1. Equivalent to the mean of all spacing between
    #    individual frame pairs. If the number of frame is 1 this is div 0.
    #    Assumes LRs are correctly ordered.
    # 3. First LR/Last LR. A variation on (2) where the 'last' frame is the
    #    first frame of the last LR. If there is one frame per LR this is
    #    identical to (2). If there is 1 LR it it div 0. This is OK for indirect
    #    X (as implicit). Not necessarily OK for direct X.
    # 4. Mean/median or some other mathematical evaluation of all frame X axis
    #    values.
    #===========================================================================
    @property
    def xAxisFirstVal(self):
        """The numerical value of the X axis of the first frame."""
        return self._rle.xAxisFirst()

    @property
    def xAxisLastVal(self):
        """The numerical value of the X axis of the last frame."""
        return self._rle.xAxisLastFrame()

    @property
    def xAxisFirstEngVal(self):
        """The EngVal (value, units) of the X axis of the first frame."""
        return EngVal.EngVal(self._rle.xAxisFirst(), self._rle.xAxisUnits)

    @property
    def xAxisLastEngVal(self):
        """The EngVal (value, units) of the X axis of the first frame."""
        return EngVal.EngVal(self._rle.xAxisLastFrame(), self._rle.xAxisUnits)

    @property
    def xAxisSpacing(self):
        """The numerical value of the X axis frame spacing. This is is the
        extreme range of X axis values divided by the number of frames - 1.
        This is +ve if the Xaxis increases, -ve if it decreases."""
        return self._rle.frameSpacing()
    
#    @property
#    def xAxisIncreases(self):
#        """Returns True if the xAxisSpacing is +ve, False otherwise.
#        See xAxisSpacing for a description of how this is determined."""
#        return self.xAxisSpacing > 0

    @property
    def xAxisUnits(self):
        """The units of the X axis."""
        return self._rle.xAxisUnits

    @property
    def totalFrames(self):
        """The total number of frames."""
        return self._rle.totalFrames()

    @property
    def xAxisFirstValOptical(self):
        """The numerical value of the X axis of the first frame in 'optical' units."""
        return Units.convert(
            self._rle.xAxisFirst(),
            self._rle.xAxisUnits,
            Units.opticalUnits(self._rle.xAxisUnits)
            #self._dfsr.ebs.opticalLogScale
        )

    @property
    def xAxisLastValOptical(self):
        """The numerical value of the X axis of the last frame in 'optical' units."""
        return Units.convert(
            self._rle.xAxisLastFrame(),
            self._rle.xAxisUnits,
            Units.opticalUnits(self._rle.xAxisUnits)
            #self._dfsr.ebs.opticalLogScale
        )
        
    @property
    def xAxisSpacingOptical(self):
        """The numerical value of the X axis frame spacing. This is is the
        extreme range of X axis values divided by the number of frames - 1."""
        return Units.convert(
            self._rle.frameSpacing(),
            self._rle.xAxisUnits,
            Units.opticalUnits(self._rle.xAxisUnits)
            #self._dfsr.ebs.opticalLogScale
        )

    @property
    def xAxisUnitsOptical(self):
        """Returns the actual units to 'optical' i.e. user friendly units.
        For example if the Xaxis was in b'.1IN' the 'optical' units would be b'FEET"."""
        return Units.opticalUnits(self._rle.xAxisUnits)
        #return self._dfsr.ebs.opticalLogScale

    def frameFromX(self, theEv):
        """Returns the estimated frame number from the X axis, and EngValue."""
        myEv = theEv.newEngValInUnits(self.xAxisUnits)
        retVal = int((myEv.value - self.xAxisFirstVal) // self.xAxisSpacing)
        if retVal < 0 or retVal >= self._rle.totalFrames():
            raise ExceptionLogPass(
                'FrameSet.frameFromX():'
                ' EngVal={!s:s} results in frame index {:d}'
                ' out of range 0->{:d}'.format(theEv, retVal, self._rle.totalFrames()))
        return retVal
    #========================
    # End: X Axis values.
    #========================

    
    #=============================================
    # Section: Mapping of MNEM to channel indices.
    #=============================================
    def _mnemToChSc(self, theMnem):
        """Returns a tuple of (extCh, subCh) for a given MNEM.
        May raise a ExceptionLogPassKeyError."""
        try:
            return self._chMap[theMnem]
        except KeyError as err:
            raise ExceptionLogPassKeyError('LogPass._mnemToChSc(): {:s}'.format(str(err)))
        
    def hasOutpMnem(self, theMnem):
        """Returns True is theMnem is in this LogPass (i.e. is in the DFSR)."""
        return theMnem in self._chMap
            
    def outpMnemS(self):
        """Returns all of the OUTP Mnems in this LogPass (i.e. is in the DFSR)."""
        return self._chMap.keys()
            
    def retExtChIndexList(self, theMnemS):
        """Returns a sorted, unique list of external channel indexes for a list
        of mnemonics. May raise a ExceptionLogPassKeyError."""
        logging.debug('LogPass.retExtChIndexList() self._chMap={:s}'.format(str(self._chMap)))
        mySet = set()
        for m in theMnemS:
#            try:
#                c = self._mnemToChSc(m)
#            except ExceptionLogPassKeyError:
#                logging.warning('LogPass.retChList(): No channel for mnem={:s}'.format(m))
#            else:
#                mySet.add(c[0])
            c = self._mnemToChSc(m)
            mySet.add(c[0])
        return sorted(list(mySet))
    
    def genFrameSetHeadings(self):
        """This generates a name and units for each value in a frame in the
        current frame set. It is useful for heading up a frame dump."""
        if self._frameSet is None:
            raise ExceptionLogPassNoFrameSet('LogPass has no FrameSet')
        for extChIdx in self._frameSet.genExtChIndexes():
            myDsb = self._dfsr.dsbBlocks[extChIdx]
            if myDsb.repCode in RepCode.DIPMETER_REP_CODES:
                # Dipmeter is a special case
                for valIdx in range(myDsb.values()):
                    #print('valIdx', valIdx)
                    sc, sa, bu = RepCode.DIPMETER_VALUE_MAPPER[valIdx]
                    yield '{!s:s} ({:d}, {:d})'.format(
                            RepCode.DIPMETER_SUB_CHANNEL_SHORT_LONG_NAMES[sc][0],
                            sa,
                            bu), myDsb.units
            else: 
                for aScIdx in range(myDsb.subChannels):
                    mnem = myDsb.subChMnem(aScIdx)
                    units = myDsb.units
                    sa = myDsb.samples(aScIdx)
                    bu = myDsb.bursts(aScIdx)
                    if sa * bu > 1:
                        for s in range(sa):
                            for b in range(bu):
                                yield '{!s:s} ({:d}, {:d})'.format(mnem, s, b), units
                    else:
                        yield mnem, units
        
    def _toAscii(self, b):
        """Converts bytes to ASCII."""
        return b.decode('ascii').replace('\x00', ' ')
    
    def genFrameSetScNameUnit(self, toAscii=True):
        """This generates a name and units for sub-channel in a frame in the
        current frame set. It is useful for heading up a accumulate() dump."""
        if self._frameSet is None:
            raise ExceptionLogPassNoFrameSet('LogPass has no FrameSet')
        for extChIdx in self._frameSet.genExtChIndexes():
            myDsb = self._dfsr.dsbBlocks[extChIdx]
            if myDsb.repCode in RepCode.DIPMETER_REP_CODES:
                # Dipmeter is a special case
                # Type 130
                numVals = RepCode.DIPMETER_NUM_FAST_CHANNELS
                if myDsb.repCode == RepCode.DIPMETER_CSU_FIELD_TAPE_REP_CODE:
                    # Type 234
                    numVals += RepCode.DIPMETER_NUM_SLOW_CHANNELS
                for i in range(numVals):
                    if toAscii:
                        yield self._toAscii(RepCode.DIPMETER_SUB_CHANNEL_SHORT_LONG_NAMES[i][0]), \
                            self._toAscii(myDsb.units)
                    else:
                        yield RepCode.DIPMETER_SUB_CHANNEL_SHORT_LONG_NAMES[i][0], \
                            myDsb.units
            else: 
                for aScIdx in range(myDsb.subChannels):
                    if toAscii:
                        yield self._toAscii(myDsb.subChMnem(aScIdx)), \
                            self._toAscii(myDsb.units)
                    else:
                        yield myDsb.subChMnem(aScIdx), myDsb.units
        
    #=============================================
    # End: Mapping of MNEM to channel indices.
    #=============================================

    def addType01Data(self, tellLr, lrType, lrLen, xAxisVal):
        """Add an Type 0/1 logical record entry.
        
        tellLr - the Logical Record start position in the file.
        
        lrType - the type of the IFLR. Will raise an ExceptionLogPass if this does not match the DFSR.
        
        lrLen - the length of the Logical record, not including the LRH.
        
        xAxisVal - the value of the X Axis of the first frame of the Logical Record.
        """
        #logging.debug('LogPass.addType01Data(0x{:x} {:d} {:d} {:f}'.format(tellLr, lrType, lrLen, xAxisVal))
        if self.iflrType != lrType:
            raise ExceptionLogPass('LogPass.setFrameSet(): mismatched IFLR type expected: {:s} got: {:s}'.format(str(self.iflrType), str(lrType)))
        # Add to RLE
        self._rle.add(tellLr, self._plan.numFrames(lrLen), xAxisVal)
    
    def setFrameSetChX(self, theFi, theChS, Xstart, Xstop, frStep=1):
        """Loads a FramesSet using 'external' values from a File object.
        theChS is a list of channel mnemonics or None for all channels.
        Xstart, Xstop are EngVal of the start stop.
        frStep is not number of frames to step over, default means all frames.
        """
        # Convert channel mnem to extChIndexes
        if theChS is None:
            myChIdxS = None
        else:
            myChIdxS = self.retExtChIndexList(theChS)
        # Convert X values to frame numbers.
        myFrSl = slice(self.frameFromX(Xstart), self.frameFromX(Xstop), frStep)
        # Populate the FrameSet
        return self.setFrameSet(theFi, theFrSl=myFrSl, theChList=myChIdxS)
    
    def setFrameSet(self, theFile, theFrSl=None, theChList=None):
        """Populates the frames set.
        
        theFile - The File object. Will raise an ExceptionLogPass is the file ID
        does not match that in the constructor.
        
        theFrSl - A slice object that describes when LogPass frames are to be used (default all).
        Will raise an ExceptionLogPass is there are no frames to load
        i.e. addType01Data() has not been called.
        
        theChList - A list of external channel indexes (i.e. DSB block indexes)
        to populate the frame set with (default all).
        """
        if self._fileId != theFile.fileId:
            raise ExceptionLogPass('LogPass.setFrameSet(): mismatched file ID was: {:s} now: {:s}'.format(self._fileId, theFile.fileId))
        # Default the inputs
        #print('self._rle.totalFrames()', self._rle.totalFrames())
        if self._rle.totalFrames() == 0:
            raise ExceptionLogPass('LogPass.setFrameSet(): no frames to load.')
        myFrSl = theFrSl or slice(0, self._rle.totalFrames(), 1)
        # Create a new FrameSet
        # TODO: Resize rather than brute force delete?
        del self._frameSet
        self._frameSet = FrameSet.FrameSet(
            self._dfsr,
            myFrSl,
            theChList,
            self._xAxisIndex,
        )
        if self._frameSet.numFrames == 0:
            return
        # Iterate through frame plane for this LR
        xVal = None
        #print('setFrameSet.setFrameSet():')
        # Note: We take the list of channel indexes from the frameSet as the
        # frameSet is free to add mandatory channels such as the X axis
        for ty, siz, frInt, chFrom, chTo in self._genFrameSetEvents(myFrSl, list(self._frameSet.genExtChIndexes())):
            #print('LogPass.setFrameSet(): type={:s} siz={:s} frInt={:s} chFrom={:s} chTo={:s}'.format(ty, str(siz), str(frInt), str(chFrom), str(chTo)))
            #print('LogPass.setFrameSet(): type={:s} frInt={:s}'.format(ty, str(frInt)))
            # Note: fr is frame number in this LR
            if ty == EVENT_SEEK_LR:
                theFile.seekLr(siz)
                # Consume LRH
                myLrh = theFile.readLrBytes(LogiRec.LR_HEADER_LENGTH)
                if myLrh[0] != self._dfsr.ebs.dataType:
                    raise ExceptionLogPass(
                        'LogPass.setFrameSet() record at 0x{:x} is type {:d}, not type {:d}'.format(siz, myLrh[0], self._dfsr.ebs.dataType,
                    ))
            elif ty == EVENT_EXTRAPOLATE:
                # We have to pick up a previous X value and extrapolate it.
                # If frInt > 0 then we read frInt-1, if frInt == 0 we take
                # the [0] value, previously read, extrapolate and write it back.
                # The latter can happen if we specify slice(>1, ..., ...).
                assert(frInt >= 0), 'frInt={:d}'.format(frInt)
                if frInt == 0:
                    xVal = self._frameSet.xAxisValue(frInt)
                else:
                    xVal = self._frameSet.xAxisValue(frInt-1)
                xVal += self._frameSet.xAxisStep(siz)
                self._frameSet.setIndirectX(frInt, xVal)
            elif ty == EVENT_SKIP:
                theFile.skipLrBytes(siz)
            else:
                assert(ty == EVENT_READ)
                self._frameSet.setFrameBytes(theFile.readLrBytes(siz), frInt, chFrom, chTo)

    def _rangeFromSlice(self, theSl):
        """Given a slice object this returns an iterable range object."""
        return range(theSl.start or 0, theSl.stop, theSl.step or 1)

    def _sliceFromList(self, theL):
        """Returns a slice object from a list of integers. Only the length of
        the list and the first and last elements are treated as significant."""
        if len(theL) == 0:
            raise ExceptionLogPass('LogPass._sliceFromList(): on empty list.')
        if len(theL) == 1:
            return slice(theL[0], theL[0]+1, 1)
        myMin = theL[0]
        myMax = theL[-1]+1
        myStep = (myMax - 1 - myMin) // (len(theL) - 1)
        assert((myMax - 1 - myMin) % myStep == 0), 'LogPass._sliceFromList(): myMax={:d} myMin={:d} myStep={:d}'.format(myMax, myMin,  myStep)
        retVal = slice(myMin, myMax, myStep)
        return retVal

    def _retFrameSetMap(self, theFrSl):
        """Returns a map {seek : slice, ...}."""
        rMap = {}
        myFrSl = theFrSl or slice(0, self._rle.totalFrames(), 1)
        for fNum in self._rangeFromSlice(myFrSl):
            lrSeek, fOffs = self._rle.tellLrForFrame(fNum)
            try:
                rMap[lrSeek].append(fOffs)
            except KeyError:
                rMap[lrSeek] = [fOffs,]
        return rMap
    
    def _genFrameSetEvents(self, theFrSl, theChList):
        """Generate events that iterate through a frame slice and channel list.
        Events are a 5 member event tuple."""
        mySeFrMap = self._retFrameSetMap(theFrSl)
        frInt = 0
        for lrSeek in sorted(mySeFrMap.keys()):
            myBuf = mySeFrMap[lrSeek]
            #logging.debug('LogPass._genFrameSetEvents(): A lrBuffer={:s}'.format(myBuf))
            #logging.debug('LogPass._genFrameSetEvents(): A type="{:s}" siz={:d}'.format(EVENT_SEEK_LR, lrSeek))
            yield (EVENT_SEEK_LR, lrSeek, None, None, None)
            myFrIntInLr = 0
            for ty, siz, frInLr, chFrom, chTo in self._plan.genEvents(self._sliceFromList(myBuf), theChList):
                #logging.debug('LogPass._genFrameSetEvents(): A type="{:s}" siz={:s} frInLr={:s} chFrom={:s} chTo={:s}'.format(
                #    ty, str(siz), str(frInLr), str(chFrom), str(chTo))
                #)
                if myFrIntInLr+1 < len(myBuf) \
                and myBuf[myFrIntInLr+1] == frInLr:
                    myFrIntInLr += 1
                yield ty, siz, frInt+myFrIntInLr, chFrom, chTo
            frInt += len(myBuf)
            
    def genOutpPoints(self, theMnem):
        """Wrapper around the frameset generator, in fact this returns exactly that generator."""
        fsCh, fsSc = self._mnemToChSc(theMnem)
        return self._frameSet.genChScPoints(fsCh, fsSc, chIsExt=True)

    def jsonObject(self):
        """Return an Python object that can be JSON encoded."""
        d = {
            # TODO: Expand the DFSR.
            'DFSR' : str(self._dfsr),
            'Plan' : {
                'IndirectSize' : self._plan.indirectSize,
                'FrameSize' : self._plan.frameSize,
                'NumChannels' : self._plan.numChannels,
                'ChannelSizes' : [self._plan.channelSize(i) for i in range(self._plan.numChannels)]
            },
            'Channels' : [str(b.mnem) for b in self._dfsr.dsbBlocks],
            # TODO: add datum, stride, repeat
            'RLE' : repr(self._rle),
        }
        if self._rle.hasXaxisData:
            d['Xaxis'] = {
                'FirstValOptical' : self.xAxisFirstValOptical,
                'LastValOptical' : self.xAxisLastValOptical,
                'TotalFrames' : self._rle.totalFrames(),
                'SpacingOptical' : self.xAxisSpacingOptical,
                'UnitsOptical' : repr(self.xAxisUnitsOptical),
                'Units' : repr(self._rle.xAxisUnits),
            }
        else:
            d['Xaxis'] = None
        return d

##############
# End: LogPass
##############
