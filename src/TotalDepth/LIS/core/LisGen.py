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
"""Generates arbitrary sized LIS files.

Created on 10 Feb 2011

@author: p2ross
"""
__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

#import time
#import sys
import io
import logging
import collections
#from optparse import OptionParser

import math
#import struct
import random

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import PhysRec
from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import Units
from TotalDepth.LIS.core import RepCode
from TotalDepth.LIS.core import LogiRec

random.seed()

class ExceptionLisGen(ExceptionTotalDepthLIS):
    """Specialisation of exception for LIS generator."""
    pass

############################
# Section: Global functions.
############################
def randomBytes(len=None):
    """Returns a bytes() object of specified length that contains random data
    of length theLen. If theLen is absent a random length of 0<=len<=32kB is
    chosen."""
    if len is None:
        len = random.randint(0, 32*1024)
    return bytes([random.choice(range(256)) for l in range(len)])

def randomUnit():
    """Returns a random unit mnemonic."""
    return random.choice(Units.units(theCat=None))

def randomMnem():
    """Returns a random mnemonic using uppercase ASCII."""
    return bytes(random.sample(range(ord('A'), ord('Z')+1), 4))

RANDOM_STRING_CHARS = b'AAABCDEFGHIJKLMNOPQRSTUVWXYZ :;,.'
RANDOM_STRING_DEFAULT_MAX_LENGTH = 255

def randomString(len=None):
    """Returns a bytes() object of specified length that contains random data
    of A-Z + b' :;,.'. If theLen is absent a random length of 0<=len<=255 is
    chosen."""
    if len is None:
        len = random.randint(0, RANDOM_STRING_DEFAULT_MAX_LENGTH)
    return bytes([random.choice(RANDOM_STRING_CHARS) for l in range(len)])

def randomAllo():
    """Returns b'ALLO' or b'DISA' randomly."""
    if random.randint(0, 1):
        return b'ALLO'
    return b'DISA'

def retSinglePr(theB):
    """Given a bytes() object this returns a bytes object encapsulated in a single Physical Record."""
    return retPrS(theB, len(theB)+PhysRec.PR_PRH_LENGTH)

def retPrS(theB, prLen=1024):
    """Returns a bytearray that is theB split into Physical Records of
    maximum length prLen. These Physical Records have no trailer records."""
    r = bytearray()
    ofs = 0
    while ofs < len(theB):
        myPayLoad = theB[ofs:ofs+prLen]
        r.extend(PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myPayLoad)))
        a = 0
        if ofs+prLen < len(theB):
            # Has successor
            a |= 1
        if ofs > 0:
            # Has predecessor
            a |= 2
        r.extend(PhysRec.PR_PRH_ATTR_FORMAT.pack(a))
        r.extend(myPayLoad)
        ofs += prLen
    return r

def retFileFromBytes(theB, theId='MyFile', flagKg=False):
    """Returns bytes object wrapped as a File.FileRead object."""
    return File.FileRead(theFile=io.BytesIO(theB), theFileId=theId, keepGoing=flagKg)

############################
# End: Global functions.
############################

##########################
# Section: Specific EFLRs.
##########################

#=========================
# Section: File/Tape/Reel.
#=========================
class FileHeadTail(collections.namedtuple(
    'FileHeadTail',
    'fileName serviceSubLevel version date maxPrLen fileType contName')):
    __slots__ = ()
    @property
    def lisBytes(self):
        """The byte array without header, not encapsulated as a PR."""
        return LogiRec.STRUCT_LR_FILE_HEAD_TAIL.pack(
            # File name, 10 bytes, 6.3 format
            self.fileName,
            # Service sub-level name, 6 bytes
            self.serviceSubLevel,
            # Version, 8 bytes
            self.version,
            # Date, yy/mm/dd
            self.date,
            # Max PR len, 5 bytes, alphanumeric
            self.maxPrLen,
            # File type, 2 bytes
            self.fileType,
            # Previous/next name, 10 bytes.
            self.contName
        )
    
    @property
    def lrBytesFileHead(self):
        """The Logical Record bytes for a Tape Head, not encapsulated as a PR."""
        return b'\x80\x00' + self.lisBytes
        
    @property
    def lrBytesFileTail(self):
        """The Logical Record bytes for a Tape Tail, not encapsulated as a PR."""
        return b'\x81\x00' + self.lisBytes

FileHeadTailDefault = FileHeadTail(
    # File name 6.3 format
    b'RUNOne.lis',
    # Service sub-level name
    b'SubLev',
    # Version number
    b'Vers num',
    # Date
    b'78/03/15',
    # Max Physical record length
    b' 1024',
    # File Type
    b'\x41\x42',
    # Previous file name
    b'Prev name.'
)

class TapeReelHeadTail(collections.namedtuple(
    'TapeReelHeadTail',
    'serviceName date origin tapeName contNum contName comments')):
    __slots__ = ()
    @property
    def lisBytes(self):
        """The byte array without header, not encapsulated as a PR."""
        return LogiRec.STRUCT_LR_REEL_TAPE_HEAD_TAIL.pack(
            # Service name, 6 bytes
            self.serviceName,
            # Date, yy/mm/dd
            self.date,
            # Origin, 4 bytes
            self.origin,
            # Name, 8 bytes
            self.tapeName,
            # Continuation number, 2 bytes
            self.contNum,
            # Continuation name, 8 bytes
            self.contName,
            # Comments, 74 bytes
            self.comments
        )
    
    @property
    def lrBytesTapeHead(self):
        """The Logical Record bytes for a Tape Head, not encapsulated as a PR."""
        return b'\x82\x00' + self.lisBytes
        
    @property
    def lrBytesTapeTail(self):
        """The Logical Record bytes for a Tape Tail, not encapsulated as a PR."""
        return b'\x83\x00' + self.lisBytes
        
    @property
    def lrBytesReelHead(self):
        """The Logical Record bytes for a Reel Head, not encapsulated as a PR."""
        return b'\x84\x00' + self.lisBytes
        
    @property
    def lrBytesReelTail(self):
        """The Logical Record bytes for a Reel Tail, not encapsulated as a PR."""
        return b'\x85\x00' + self.lisBytes

TapeReelHeadTailDefault = TapeReelHeadTail(
    # Service name, 6 bytes
    b'SERVCE',
    # Date, yy/mm/dd
    b'79/06/15',
    # Origin, 4 bytes
    b'ORGN',
    # Name, 8 bytes
    b'TAPENAME',
    # Continuation number, 2 bytes
    b'01',
    # Continuation name, 8 bytes
    b'PrevName',
    # Comments, 74 bytes
    b'_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123'
)
#=========================
# End: File/Tape/Reel.
#=========================

#===========================
# Section: Table generators.
#===========================
class TableGen(object):
    def __init__(self, theLrType, theName, theColTitles, theTable=None):
        """Construct a Logical Record table."""
        assert(theLrType in LogiRec.LR_TYPE_TABLE_DATA)
        if theTable is not None:
            for row in theTable:
                assert(len(row) == len(theColTitles))
        self._type = theLrType
        self._name = theName
        self._colTitles = theColTitles
        self._table = theTable
        
    def lrBytes(self):
        """Returns the Logical Record bytes that make up this table record."""
        if self._table is None:
            raise ExceptionLisGen('TableGen.lisBytes() on None table.')
        b = bytearray([self._type, 0])
        b.extend(
            self._retCbBytes(
                LogiRec.COMPONENT_BLOCK_TABLE,
                b'TYPE',
                b'    ',
                self._name
            )
        )
        for row in self._table:
            for i in range(len(self._colTitles)):
                if i == 0:
                    t = LogiRec.COMPONENT_BLOCK_DATUM_BLOCK_START
                else:
                    t = LogiRec.COMPONENT_BLOCK_DATUM_BLOCK_ENTRY
                if isinstance(row[i], tuple):
                    v, u = row[i]
                else:
                    v, u = row[i], b'    '
                b.extend(self._retCbBytes(t, self._colTitles[i], v, u))
        return b

    def _retCbBytes(self, typ, mnem, v, units):
        myCb = LogiRec.CbEngVal()
        myCb.type = typ
        myCb.category = 0
        myCb.mnem = mnem
        myCb.units = units
        if isinstance(v, int):
            # Convert to type 73, 32bit integer
            myCb.rc = 73
            myCb.size = 4
        elif isinstance(v, float):
            # Convert to type 68
            myCb.rc = 68
            myCb.size = 4
        else:
            # Treat as bytes and use type 65
            if not isinstance(v, bytes):
                # Stringify and byteify
                v = bytes(str(v), 'ascii')
            # Treat as type 65, 'string'
            myCb.rc = 65
            myCb.size = len(v)
        myCb.setValue(v)
        #print('myCb', myCb)
        return myCb.lisBytes()

class TableGenRandom(TableGen):
    def __init__(self, theLrType, theName, theColTitles, numRows):
        super().__init__(theLrType, theName, theColTitles=theColTitles, theTable=None)
        self._numRows = numRows
        self._despatch = {
            b'MNEM' : randomMnem,
            b'ALLO' : randomAllo,
            b'PUNI' : randomUnit,
            b'TUNI' : randomUnit,
            b'VALU' : self._randValue,
        }
    
    def _randValue(self):
        # Do random integer, float or string
        c = random.randint(0, 2)
        if c == 0:
            # Integer
            return random.randint(-64*1024, 64*1024), randomUnit()
        elif c == 1:
            # Float
            return 1e6*(random.random()-0.5), randomUnit()
        else:
            # String
            return randomString(32) 
    
    def lrBytes(self):
        # Populate the table with values then call super().lrBytes()
        self._table = []
        for r in range(self._numRows):
            myRow = []
            for c in range(len(self._colTitles)):
                try:
                    myRow.append(self._despatch[self._colTitles[c]]())
                except KeyError:
                    myRow.append(b'    ')
            self._table.append(myRow)
        return super().lrBytes()

class TableGenRandomCONS(TableGenRandom):
    def __init__(self, numRows):
        super().__init__(34, b'CONS', [b'MNEM', b'ALLO', b'PUNI', b'TUNI', b'VALU'], numRows)

#===========================
# End: Table generators.
#===========================

##########################
# End: Specific EFLRs.
##########################

##########################################################
# Section: Value value generators (random, sin, cos etc.).
##########################################################
class ChValsBase(object):
    def __init__(self, noise=None):
        self._noise = noise
    
    def val(self, f, s=0):
        raise NotImplementedError
    
    def noise(self):
        if self._noise is not None:
            return (random.random() - 0.5) * self._noise
        return 0.0

class ChValsXaxis(ChValsBase):
    """Value generator that produces X axis values evenly spread by frame.
    May have noise.""" 
    def __init__(self, xStart, frameSpacing, xDec, rc=68, noise=None):
        super().__init__(noise)
        """Constructor of X axis generator.
        xStart - X for frame number 0.
        frameSpacing - Incremental X per frame as a number.
        xDec - If True X decreases with increasing frame number, otherwise increases.
        noise - If not None then randomly +/- half this value will be added."""
        assert(frameSpacing is not None)
        self._xStart = xStart
        self._fSpace = frameSpacing
        self._xDec = xDec
        self.rc = rc
        if self._fSpace < 0:
            logging.warning('ChValsXaxis has -ve frame spacing (left uncorrected).')
        
    def val(self, f, s=0):
        assert(s == 0), 'ChValsXaxis.val() called with non-zero sample index.'
        d = (self._fSpace * f) + self.noise()
        if self._xDec:
            r = self._xStart - d
        else:
            r = self._xStart + d
        if RepCode.isInt(self.rc):
            r = int(r + 0.5)
        return r
    
class ChValsFrameBase(ChValsBase):
    """Base class for frame related generators."""
    def __init__(self, fOffs=0, waveLen=1, mid=0, amp=1, numSa=1, noise=None):
        super().__init__(noise)
        self._fOffs = fOffs
        self._waveLen = waveLen
        self._mid = mid
        self._amp = amp
        self._numSa = numSa
        self._noise = noise
        
    def __str__(self):
#        print('HI', self._fOffs, self._waveLen, self._mid, self._amp, self._numSa, str(self._noise))
        return 'ChValsFrameBase: fOffs={:g}, waveLen={:g}, mid={:g}, amp={:g}, numSa={:g}, noise={:g}'.format(
            self._fOffs, self._waveLen, self._mid, self._amp, self._numSa, self._noise,
        )
    
    def fr(self, f, s=0):
        """Returns a frame number subtracting the offset and fractionating for samples."""
        if self._numSa == 1:
            return f - self._fOffs
        return f - self._fOffs - (1 - (s + 1) / self._numSa)

    def _amplify(self, val):
        #print('_amplify(val)', val)
        return self.noise() + self._mid + self._amp * val

#=================================
# Section: Frame invariant values.
#=================================
class ChValsConst(ChValsFrameBase):
    """Constant value for the channel, may have noise."""
    def val(self, f, s=0):
        return self._mid + self.noise()

class ChValsRand(ChValsFrameBase):
    """Random value for the channel, may have noise."""
    def val(self, f, s=0):
        return self._amplify(random.random())

class ChValsRandNormal(ChValsFrameBase):
    """Random value for the channel, normal distribution. mid is treated as the
    mean and amplitude is treated as the standard deviation, may have noise."""
    def val(self, f, s=0):
        return self.noise() + random.normalvariate(mu=self._mid, sigma=self._amp)

class ChValsRandLogNormal(ChValsFrameBase):
    """Random value for the channel, log-normal distribution. mid is treated as the
    mean and amplitude is treated as the standard deviation, may have noise."""
    def val(self, f, s=0):
        return self.noise() + random.lognormvariate(mu=self._mid, sigma=self._amp)

#=================================
# End: Frame invariant values.
#=================================

#=================================
# Section: Frame dependent values.
#=================================
class ChValsFrameDepend(ChValsFrameBase):
    """Base class for frame dependent channel, may have noise."""
    pass

class ChValsTrig(ChValsFrameDepend):
    """Base class for trigonometric values for the channel, may have noise."""
    def _trigVal(self, func, f, s=0):
        #print('self.fr(f,s)', self.fr(f,s))
        #print('func(2 * math.pi * self.fr(f,s) / self._waveLen)', func(2 * math.pi * self.fr(f,s) / self._waveLen))
        return self._amplify(func(2 * math.pi * self.fr(f,s) / self._waveLen))

class ChValsSin(ChValsTrig):
    """sin() value for the channel, may have noise."""
    def val(self, f, s=0):
        return self._trigVal(math.sin, f, s)

class ChValsCos(ChValsTrig):
    """sin() value for the channel, may have noise."""
    def val(self, f, s=0):
        return self._trigVal(math.cos, f, s)

class ChValsSaw(ChValsFrameDepend):
    """Saw tooth value for the channel, may have noise."""
    def val(self, f, s=0):
        return self._amplify((self.fr(f,s) % self._waveLen) / self._waveLen)

class ChValsTriangular(ChValsFrameDepend):
    """Triangular shaped value for the channel."""
    def val(self, f, s=0):
        ofs = self.fr(f,s) % self._waveLen
        # TODO: Should this be >= like square wave?
        if ofs > self._waveLen / 2:
            ofs = self._waveLen - ofs
        return self._amplify(ofs / (self._waveLen / 2))

class ChValsSquare(ChValsFrameDepend):
    """Square wave shaped value for the channel."""
    def val(self, f, s=0):
        ofs = self.fr(f,s) % self._waveLen
        if ofs >= self._waveLen / 2:
            return self._amplify(1.0)
        return self._amplify(-1.0)

class ChValsSpecialSeqSqRoot(ChValsFrameDepend):
    """A progressive sequence that generates a particular signature on 2/4/8 etc. frames.
    For example: 0.0, 1.0, 2.0, 2.0, 3.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 4.0,
    4.0, 4.0, 4.0, 4.0, ...
    This is useful for checking plotting where a regular stair step could be
    mistaken if both the x and y offset wrong.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Frame interval to increase 
        # [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
        self._frSeq = [2**r for r in range(10)]
        
    def val(self, f, s=0):
        # NOTE: Sample is ignored
        assert(len(self._frSeq) > 0)
        frInt = f % self._frSeq[-1]
        i = 0
        while i < len(self._frSeq):
            if frInt < self._frSeq[i]:
                break
            i += 1
        return self._amplify(i)

#class ChValsSpecialSeqSquare(ChValsFrameDepend):
#    """A progressive sequence that generates a particular signature on 2/4/8 etc. frames.
#    For example: 0.0, 1.0, 2.0, 2.0, 3.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 4.0,
#    4.0, 4.0, 4.0, 4.0, ...
#    This is useful for checking plotting where a regular stair step could be
#    mistaken if both the x and y offset wrong.
#    """
#    def val(self, f, s=0):
#        # NOTE: Sample is ignored
#        return self._amplify((f % 16)**2)

#=================================
# End: Frame dependent values.
#=================================
##########################################################
# End: Value value generators (random, sin, cos etc.).
##########################################################

##########################################################
# Section: DFSR and Channel value generators.
##########################################################
#===================================
# Section: Channel value generators.
#===================================
class ChannelSpec(collections.namedtuple(
    'ChannelSpec',
    'name servId servOrd units api fileNo chLen sa rc')):
    __slots__ = ()
    @property
    def dsbBytes(self):
        #print(self)
        return LogiRec.STRUCT_DSB.pack(
            self.name,
            self.servId,
            self.servOrd,
            self.units,
            self.api,
            self.fileNo,
            self.chLen,
            self.sa,
            self.rc,
            )

class Channel(object):
    """Encapsulates a channel with a ChannelSpec and an object that
    derives from ChValsFrameBase and used to generate the channel values."""
    def __init__(self, chSpec, chGen):
        self._chSpec = chSpec
        self._chGen = chGen
    
    @property
    def dsbBytes(self):
        return self._chSpec.dsbBytes
    
    def val(self, f, s):
        """Returns the value for the frame and sample."""
        return self._chGen.val(f, s)

    def frameBytes(self, f):
        """Returns the bytes for the frame."""
        r = bytearray()
        for s in range(self._chSpec.sa):
            r.extend(RepCode.writeBytes(self.val(f,s), self._chSpec.rc))
        return r

#-------------------------------------------------
# Section: Channel value generators for Dipmeters.
#-------------------------------------------------
class ChGenBase(object):
    pass

    def _packListWithStruct(self, theStruct, *args):
        """Returns bytes packed with a struct. When called with a list the
        convention is: self._packListWithStruct(myStruct, *myList)."""
        #>>> def f(*args):
        #...   print(args)
        #...   print(*args)
        #...   return struct.pack('2B', *args)
        #...
        #>>> f(*[1,2])
        #(1, 2)
        #1 2
        #b'\x01\x02'
        #print('_packListWithStruct()', len(args))
        return theStruct.pack(*args)
        
class ChGenDipmenter(ChGenBase):
    def __init__(self, n, r, l, curveTypes):
        super().__init__()
        self._name = n
        self._rc = r
        self._lisLen = l
        self._curveTypeFast, self._curveTypeSlow = curveTypes

    @property
    def dsbBytes(self):
        """Returns a Datum Spec Block for a dipmeter."""
        myCh = ChannelSpec(
            self._name,
            b'servID',
            b'servOrdr',
            b'    ',
            45310011,
            256,
            self._lisLen,
            1,
            self._rc
        )
        return myCh.dsbBytes

    def frameBytes(self, f):
        raise NotImplementedError
    
    def fastChannels(self, theF):
        """Returns a list of fast channels for a frame number."""
        if self._curveTypeFast == 'random':
            return [random.randint(0,255) for i in range(RepCode.DIPMETER_SIZE_FAST_CHANNELS)]
        elif self._curveTypeFast == 'constant':
            return [0,50,100,150,200] * RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES
        elif self._curveTypeFast == 'linear':
            def linF(sc, sa):
                return (sc * 50 + sa * 16) % 256
            return self._fastChannels(linF)
        elif self._curveTypeFast == 'sin':
            def sinF(sc, sa):
                return int(127.5+127.5*math.sin(2 * math.pi * (sa - 3 * sc) / RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES))
            return self._fastChannels(sinF)
        raise ExceptionLisGen('ChGenDipmenter.fastChannels(): Unknown curve function {:s}'.format(str(self._curveTypeFast)))
    
    def _fastChannels(self, func):
        """func takes a sub-channel and sample number."""
        myL = []
        for sa in range(RepCode.DIPMETER_FAST_CHANNEL_SUPER_SAMPLES):
            for sc in range(RepCode.DIPMETER_NUM_FAST_CHANNELS):
                myL.append(func(sc, sa))
        #print('_fastChannels()', myL)
        return myL

    def slowChannels(self, theF):
        """Returns a list of slow channels for a frame number."""
        if self._curveTypeSlow == 'random':
            return [random.randint(0,255) for i in range(RepCode.DIPMETER_NUM_SLOW_CHANNELS)]
        elif self._curveTypeSlow == 'constant':
            return [0,25,50,75,100,125,150,175,200,225]
        raise ExceptionLisGen('ChGenDipmenter.slowChannels(): Unknown curve function {:s}'.format(str(self._curveTypeSlow)))
    
class ChGenDip130(ChGenDipmenter):
    def __init__(self, curveType):
        super().__init__(
            RepCode.DIPMETER_130_CHANNEL_NAME,
            RepCode.DIPMETER_EDIT_TAPE_REP_CODE,
            RepCode.DIPMETER_LIS_SIZE_130,
            (curveType, None),
        )
        
    def frameBytes(self, theF):
        """Return frame bytes for a single frame number theF."""
        myStruct = RepCode.STRUCT_RC_UINT_1
        myL = self.fastChannels(theF)
        return self._packListWithStruct(RepCode.STRUCT_RC_DIPMETER_EDIT_TAPE, *myL)
        
class ChGenDip234(ChGenDipmenter):
    def __init__(self, curveTypes):
        super().__init__(
            RepCode.DIPMETER_234_CHANNEL_NAME,
            RepCode.DIPMETER_CSU_FIELD_TAPE_REP_CODE,
            RepCode.DIPMETER_LIS_SIZE_234,
            curveTypes,
        )
        
    def frameBytes(self, theF):
        """Return frame bytes for a single frame number theF."""
        myStruct = RepCode.STRUCT_RC_UINT_1
        myL = self.fastChannels(theF) + self.slowChannels(theF)
        return self._packListWithStruct(RepCode.STRUCT_RC_DIPMETER_CSU_FIELD_TAPE, *myL)

#---------------------------------------------
# End: Channel value generators for Dipmeters.
#---------------------------------------------
#===============================
# End: Channel value generators.
#===============================

#=============================
# Section: LogPass generators.
#=============================
#class LisGenBase(object):
#    """Generates arbitrary LIS files."""
#    def __init__(self):
#        self._b = bytearray()

class LogPassGen(object):
    def __init__(self, ebSet, chList, xStart, xRepCode, xNoise):
        """Constructor.
        ebsBytes  - a EntryBlockSet object.
        chList - a list of Channel objects or objects derived from ChGenBase.
        (xStart, xRepCode, xNoise) control X axis generation. An X axis value
        generator (ChValsXaxis) is created from this + the ebSet.frameSpacing
        + ebSet.upDown."""
        # Need numeric frame spacing
        if ebSet.frameSpacing is None:
            raise ExceptionLisGen('LogPassGen.__init__() must have non-None frame spacing.')
        self._ebs = ebSet
        self._chXVal = ChValsXaxis(
            xStart,
            self._ebs.frameSpacing,
            xDec=not self._ebs.xInc,
            rc=xRepCode,
            noise=xNoise,
        )
        if self._ebs.recordingMode == 0:
            # Direct X, prepend an Xaxis channel and chValsX
            if self._ebs.optLogScale == 0:
                xName = b'TIME'
            else:
                xName = b'DEPT'
            self._chS = [
                Channel(
                    ChannelSpec(
                        xName, b'ServID', b'ServOrdN', self._ebs.frameSpacingUnits,
                        45310011, 256, RepCode.lisSize(self._chXVal.rc), 1, self._chXVal.rc
                    ),
                    self._chXVal,
                ),
            ]
            self._chS += chList
        else:
            # Indirect X axis so we generate our own X values
            self._chS = chList
    
    @property
    def isDirectX(self):
        return self._ebs.recordingMode == 0
    
    def lrBytesDFSR(self):
        """Returns the Logical Data bytes of the DFSR."""
        r = bytearray([LogiRec.LR_TYPE_DATA_FORMAT, 0])
        r.extend(self._ebs.lisBytes())
        for c in self._chS:
            r.extend(c.dsbBytes)
        return r
    
    def _normalAlternateData(self, fFrom, numFrames):
        """Returns frame data for consecutive frames f: fFrom <= f < fTo.
        This does not prepend indirect X axis value."""
        if numFrames < 0:
            raise ExceptionLisGen('LogPassGen._normalAlternateData(): to negative number of frames: {:d}'.format(numFrames))
        r = bytearray()
        i = 0
        f = fFrom
        for i in range(numFrames):
            for c in self._chS:
                r.extend(c.frameBytes(f))
            f += 1
        return r

    def lrBytes(self, fFrom, numFrames):
        """The Logical Record bytes for the frame range."""
        # Start with LRH
        myB = bytearray(bytes([self._ebs.dataType, 0]))
        if not self.isDirectX:
            # Generate indirect X value
            xVal = self._chXVal.val(fFrom)
            #print('LogPassGen.lrBytes()', xVal)
            myB.extend(RepCode.writeBytes(xVal, self._chXVal.rc))
        # Add frame data
        myB.extend(self._normalAlternateData(fFrom, numFrames))
        return myB
    
#==========================
# End: DFSR generators.
#==========================

##########################################################
# End: DFSR and Channel value generators.
##########################################################
