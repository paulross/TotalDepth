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
"""
Physical Record Attributes
---------------------------

======    ====================================================
Bit       Description
======    ====================================================
15        Unused, reserved
14        Physical record type (only 0 is defined)
13-12     00 - No checksum, 01 - 16bit checksum, 10, 11 - Undefined
11        Unused, reserved
10        If 1 File number is present in trailer
09        If 1 Record number is present in trailer
08        Unused
07        Unused, reserved
06        If 1 then a previous parity error has occurred
05        If 1 then a previous checksum error has occurred
04        Unused
03        Unused, reserved
02        Unused
01        If 1 there is a predecessor Physical Record
00        If 1 there is a succcessor Physical Record
======    ====================================================

"""
import io

__author__ = 'Paul Ross'
__date__ = '2010-11-05'
__version__ = '0.1.2'
__copyright__ = '(c) 2010 Paul Ross.'

import struct
import os
import logging
import collections
#import traceback

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import RawStream
from TotalDepth.LIS.core import TifMarker
from TotalDepth.LIS.core import RepCode

class ExceptionPhysRec(ExceptionTotalDepthLIS):
    """Specialisation of exception for Physical Records."""
    pass

class ExceptionPhysRecEOF(ExceptionPhysRec):
    """Physical Record unexpected EOF."""
    pass

class ExceptionPhysRecUndefinedChecksum(ExceptionPhysRec):
    """Physical Record encountered undefined checksum bit."""
    pass

class ExceptionPhysRecUnknownType(ExceptionPhysRec):
    """Encountered unknown type 1 Physical Record."""
    pass

class ExceptionPhysRecWrite(ExceptionPhysRec):
    """Physical Record writing."""
    pass

class ExceptionPhysRecTail(ExceptionPhysRec):
    """Physical Record Trailer exception."""
    pass

# Physical Record Header constants
# ================================

#: PR Header 4 bytes long, two big-endian 16 bit numbers
#: The struct.Struct() format for the Physical Record Header
PR_PRH_LEN_FORMAT               = struct.Struct('>H')
#: The struct.Struct() format for the Physical Record Header attributes
PR_PRH_ATTR_FORMAT              = struct.Struct('>H')
#: The length of the Physical Record Header
PR_PRH_LENGTH                   = 4
#: Number of bits in the 2 byte attributes
PR_ATTRIBUTE_BITS               = 16
# Attribute Bit positions
# -----------------------
#: Successor bit position
PR_SUCCESSOR_ATTRIBUTE_BIT      = 0     # Set if PR has a successor
#: Predessor bit position
PR_PREDECESSOR_ATTRIBUTE_BIT    = 1     # Set if PR has a predecessor
#: Checksum error bit position
PR_OLD_CHECK_ERROR_BIT          = 5     # Set if PR has had old checksum error
#: Parity error bit position
PR_OLD_PARITY_ERROR_BIT         = 6     # Set if PR has had old parity error
#: Bit position to indicate there is a record number in the trailer
PR_RECORD_NUMBER_BIT            = 9     # Set if PR trailer has record number
#: Bit position to indicate there is a file number in the trailer
PR_FILE_NUMBER_BIT              = 10    # Set if PR trailer has file number
#: Bit position to indicate there is a 16bit checksum in the trailer
PR_CHECKSUM_BIT                 = 12    # Have 16bit checksum
#: Bit position to indicate checksum is undefined
PR_CHECKSUM_UNDEFINED_BIT       = 13    # 16bit checksum is undefined
#: Bit position to indicate Physical Record Type
PR_TYPE_BIT                     = 14    # Only type 0 is defined
#: Unused only bits - i.e. Unused but not Unused, reserved
PR_ATTRIBUTE_UNUSED_ONLY_MASK        = 0x0114
#: Unused, reserved bit mask
PR_ATTRIBUTE_UNUSED_RESERVED_MASK    = 0x8888
#: Unused and Unused, reserved bits, 0x899C
PR_ATTRIBUTE_UNUSED_MASK = PR_ATTRIBUTE_UNUSED_ONLY_MASK & PR_ATTRIBUTE_UNUSED_RESERVED_MASK
#
# Physical Record Trailer constants
# =================================
# PR trailer record number 2 bytes long
#: The struct.Struct() format for the Physical Record Trailer record number
PR_PRT_REC_NUM_FORMAT           = struct.Struct('>h')
#: The length of the Physical Record Trailer for the record number
PR_PRT_REC_NUM_LEN              = 2
#: The minimum record number
PR_PRT_REC_NUM_MIN              = RepCode.RC_79_MIN
#: The maximum record number
PR_PRT_REC_NUM_MAX              = RepCode.RC_79_MAX

#: The struct.Struct() format for the Physical Record Trailer file number
PR_PRT_FILE_NUM_FORMAT          = struct.Struct('>h')
#: The length of the Physical Record Trailer for the file number
PR_PRT_FILE_NUM_LEN             = 2
#: The minimum file number
PR_PRT_FILE_NUM_MIN              = RepCode.RC_79_MIN
#: The maximum file number
PR_PRT_FILE_NUM_MAX              = RepCode.RC_79_MAX

# PR trailer checksum 2 bytes long
#: The struct.Struct() format for the Physical Record Trailer checksum
PR_PRT_CHECKSUM_FORMAT          = struct.Struct('>H')
#: The length of the Physical Record Trailer for the checksum
PR_PRT_CHECKSUM_LEN             = 2

# Misc.
# =====
## Normal maximum Physical Record length
#PR_DEFAULT_MAX_LENGTH            = 1024
## Arbitrary really but must be greater than PRH + PRT
#PR_DEFAULT_MIN_LENGTH            = 128
#: Maximum possible Physical Record length represented by an unsigned 16 bit int
PR_MAX_LENGTH                    = 2**16 - 1

# Sanity check of struct compiled formats
assert(PR_PRH_LEN_FORMAT.size == 2)
assert(PR_PRH_ATTR_FORMAT.size == 2)
assert(PR_PRT_REC_NUM_FORMAT.size == PR_PRT_REC_NUM_LEN)
assert(PR_PRT_FILE_NUM_FORMAT.size == PR_PRT_FILE_NUM_LEN)
assert(PR_PRT_CHECKSUM_FORMAT.size == PR_PRT_CHECKSUM_LEN)

class PhysRecBase(object):
    """Base class for physical record read and write.
    TODO: Checksum reading, writing and testing."""
    def __init__(self, theFileId, keepGoing):
        """Constructor, initialise data common to child classes."""
        self.fileId = theFileId
        self.keepGoing = keepGoing
        self.stream = None
        self.tif = None
        self.prLen = 0          # Physical record size
        self.prAttr = 0         # Physical record attributes
        self.recNum = None      # Optional record number in trailer
        self.fileNum = None     # Optional file number in trailer
        self.checksum = None    # Optional checksum in trailer
        self.ldLen = 0          # Size of the Logical Data chunk for this record
        self.startOfLr = 0      # Physical file position of the beginning of the LR
                                # This is the position of the TIF marker
                                # (if present) or the position of the first PR
                                # header for the LR if TIF markers are absent.
                                # i.e. to read the LR seek to self.startOfLr
                                # then read TIF and read PR(s)
        self.startPrPos = 0     # Physical file position of the beginning of this PR
                                # This is the position of the TIF marker
                                # (if present) or the position of the PR header
                                # if TIF markers are absent.
    
    def _reset(self):
        """Resets internal state, for example when the caller makes a seek."""
        self.prLen = 0
        self.prAttr = 0
        self.recNum = None
        self.fileNum = None
        self.checksum = None
        self.ldLen = 0
        self.startOfLr = 0
        self.startPrPos = 0
    
    def close(self):
        """Close the underlying stream, further operations will raise a
        ValueError."""
        if self.stream is not None:
            self.stream.close()
    
    def strHeader(self):
        """Returns the header string to go at the top of a list of __str__()."""
        rS = []
        if self.tif is not None and self.tif.hasTif:
            rS.append(self.tif.strHeader())
            rS.append('  ')
        rS.append('PR:   %08s  %6s    %4s  %6s' \
            % ('tell()', 'Length', 'Attr', 'LD_len'))
        # PR tail values.
        rS.append('  RecNum')
        rS.append('  FilNum')
        rS.append('  ChkSum')
        return ''.join(rS)
    
    def __str__(self):
        rS = []
        if self.tif is not None and self.tif.hasTif:
            rS.append(str(self.tif))
            rS.append('  ')
        rS.append('PR: 0x%8x  %6d  0x%4x  %6d' \
            % (self.startPrPos, self.prLen, self.prAttr, self.ldLen))
        # PR tail values.
        for f in (self.recNum, self.fileNum, self.checksum):
            if f is not None:
                rS.append('  0x%04x' % f)
            else:
                rS.append('  ------')
        return ''.join(rS)
    
    #=====================================
    # Section: Attribute bit manipulation.
    #=====================================
    def _isAttrBitSet(self, theBit):
        """Returns true if a particular PRH attribute bit is clear."""
        if self.prAttr & (1 << theBit):
            return True
        return False
    
    def _isAttrBitClear(self, theBit):
        """Returns true if a particular PRH attribute bit is set."""
        return not self._isAttrBitSet(theBit)
    
    def _setAttrBit(self, theBit):
        """Sets a particular PRH attribute bit."""
        assert(theBit < PR_ATTRIBUTE_BITS)
        self.prAttr |= (1 << theBit)
    
    def _clearAttrBit(self, theBit):
        """Clears a particular PRH attribute bit."""
        assert(theBit < PR_ATTRIBUTE_BITS)
        self.prAttr &= ~(1 << theBit)
    
    def _setOrClearAttrBit(self, theBit, b):
        """If b is True sets a particular PRH attribute bit otherwise clears it."""
        if b:
            self._setAttrBit(theBit)
        else:
            self._clearAttrBit(theBit)
    
    def _hasSuccessor(self):
        """Returns true if this PR has a successor, false otherwise."""
        return self._isAttrBitSet(PR_SUCCESSOR_ATTRIBUTE_BIT)
        #return self.prAttr & (1 << PR_SUCCESSOR_ATTRIBUTE_BIT)
    
    def _hasPredecessor(self):
        """Returns true if this PR has a predecessor, false otherwise."""
        return self._isAttrBitSet(PR_PREDECESSOR_ATTRIBUTE_BIT)
        #return self.prAttr & (1 << PR_PREDECESSOR_ATTRIBUTE_BIT)
    
    def _hasRecordNumber(self):
        """Returns true if this PR has a record number, false otherwise."""
        return self._isAttrBitSet(PR_RECORD_NUMBER_BIT)
        #return self.prAttr & (1 << PR_RECORD_NUMBER_BIT)
        
    def _hasFileNumber(self):
        """Returns true if this PR has a file number, false otherwise."""
        return self._isAttrBitSet(PR_FILE_NUMBER_BIT)
        #return self.prAttr & (1 << PR_FILE_NUMBER_BIT)
    
    def _hasChecksum(self):
        """Returns true if this PR has a checksum, false otherwise."""
        if self._isAttrBitSet(PR_CHECKSUM_UNDEFINED_BIT) and not self.keepGoing:
            raise ExceptionPhysRecUndefinedChecksum('Undefined bit in checksum attribute')
        return self._isAttrBitSet(PR_CHECKSUM_BIT)
    
    def _setSuccessor(self, b=True):
        """If b is True this sets the PRH attribute bits for a successor record
        otherwise it clears it."""
        self._setOrClearAttrBit(PR_SUCCESSOR_ATTRIBUTE_BIT, b)
    
    def _setPredecessor(self, b=True):
        """If b is True this sets the PRH attribute bits for a successor record
        otherwise it clears it."""
        self._setOrClearAttrBit(PR_PREDECESSOR_ATTRIBUTE_BIT, b)
            
    def _setHasRecordNumber(self, b=True):
        """If b is True this sets the PRH attribute bit for a record number in the PRT
        otherwise it clears it."""
        self._setOrClearAttrBit(PR_RECORD_NUMBER_BIT, b)
        
    def _setHasFileNumber(self, b=True):
        """If b is True this sets the PRH attribute bit for a file number in the PRT
        otherwise it clears it."""
        self._setOrClearAttrBit(PR_FILE_NUMBER_BIT, b)

    def _setHasChecksum(self, b=True):
        """If b is True this sets the PRH attribute bits for a checksum in the PRT
        otherwise it clears it."""
        self._setOrClearAttrBit(PR_CHECKSUM_BIT, b)
    #=================================
    # End: Attribute bit manipulation.
    #=================================

class PhysRecRead(PhysRecBase):
    """Specialisation of PhysRecBase for reading streams."""
    def __init__(self, theFile, theFileId=None, keepGoing=False):
        """Constructor with a file path or file-like object.
        TODO: checksum.
        """
        super(PhysRecRead, self).__init__(theFileId, keepGoing)
        try:
            self.stream = RawStream.RawStream(theFile, mode='rb', fileId=self.fileId)
        except IOError:
            raise ExceptionPhysRec('PhysRecRead: Can not open LIS file "%s" for read' % self.fileId)
        # Rewind to start of file
        self.stream.seek(0)
        # Flag for EOF
        self.isEOF = False
        # How far we are into the logical data for this PR
        self._ldIndex = 0
        # Bytes of logical data read or skipped in this Logical Record 
        self._ldTell = 0
        # Flag set if this PR is the first of a LR
        # This does not rely on predecessor bits
        self._isLrStart = True
        # Flag to say if we must read a PRH before any read/skip operation
        self._mustReadHead = True
        self.tif = TifMarker.TifMarkerRead(self.stream, allowPrPadding=keepGoing)
        # Reset the stream self.tif may initialise TIF and read stream
        self.stream.seek(0)
        self.startOfLr = 0
        
    @property
    def isLrStart(self):
        return self._isLrStart
    
    def ldIndex(self):
        return self._ldIndex
    
    def __str__(self):
        if self.isEOF:
            return 'PR: EOF'
        return super(PhysRecRead, self).__str__()
    
    def _reset(self):
        """Resets internal state, for example when the caller makes a seek."""
        super(PhysRecRead, self)._reset()
        self.isEOF = False
        self._ldIndex = 0
        self._ldTell = 0
        self._isLrStart = True
        self._mustReadHead = True
        # Reset TIF marker too
        self.tif.reset()
    
    def _raiseOrErrorOnEOF(self, theMsg):
        self.isEOF = True
        if not self.keepGoing:
            raise ExceptionPhysRecEOF(theMsg)
        logging.error('PhysRec._raiseOnEOF(): {0:s}'.format(theMsg))
    
    def _readHead(self):
        """Read the Physical Record header and set internal state."""
        # If the previous record did not have a successor then this record is
        # the start of a logical record
        #print('_readHead()', '0x{:x}'.format(self.stream.tell()))
        #print(''.join(traceback.format_stack()))
        if not self._hasSuccessor():
            self._ldTell = 0
            self._isLrStart = True
        else:
            self._isLrStart = False
        # Take the stream position here as it will be correct if there are
        # no TIF markers (in which case PR padding is prohibited).
        self.startPrPos = self.stream.tell()
        try:
            # If there are TIF markers and PR padding is present we need to
            # take the stream postion from the TIF handler as that may have
            # moved the stream to consume PR padding.
            myTell = self.tif.read(self.stream)
            if myTell is not None:
                self.startPrPos = myTell
            self.prLen = self.stream.readAndUnpack(PR_PRH_LEN_FORMAT)[0]
            self.prAttr = self.stream.readAndUnpack(PR_PRH_ATTR_FORMAT)[0]
        except RawStream.ExceptionRawStreamEOF:
            self.isEOF = True
        else:
            # Successful read
            if self._isAttrBitSet(PR_TYPE_BIT) and not self.keepGoing:
                raise ExceptionPhysRecUnknownType('Illegal PR type of 1')
            # Logical record and logical data
            # If this is first PR in LR then set start of LR as the start of this PR 
            if self.isLrStart:
                self.startOfLr = self.startPrPos
                #print('Set start of LR:', self.startOfLr)
            if not self.isLrStart and not self._hasPredecessor():
                logging.warning('Physical record at 0x%X is successor but has no predecessor bit set.', self.startPrPos)
            # Index into logical data for this PR
            self._ldIndex = 0
            # Compute the length of logical data in _this_ PR
            self.ldLen = self.prLen - PR_PRH_LENGTH
            if self._hasRecordNumber():
                self.ldLen -= PR_PRT_REC_NUM_LEN
            if self._hasFileNumber():
                self.ldLen -= PR_PRT_FILE_NUM_LEN
            if self._hasChecksum():
                self.ldLen -= PR_PRT_CHECKSUM_LEN
            if self.ldLen < 0:
                raise ExceptionPhysRec(
                    'PhysRecRead._readHead(): Illegal negative logical data length: {:d}'.format(self.ldLen)
                )
            self._mustReadHead = False
            # Set flag to say if this is the first PR of a LR
            if self._ldTell > 0:
                self._isLrStart = False
    
    def _readTail(self):
        """Read the Physical Record trailer and set internal state."""
        #print('_readTail()', self.stream.tell())
        self._mustReadHead = True
        if self.isEOF:
            self._raiseOrErrorOnEOF('PhysRecRead._readTail() when already EOF')
        else:
            try:
                if self._hasRecordNumber():
                    self.recNum = self.stream.readAndUnpack(PR_PRT_REC_NUM_FORMAT)[0]
                if self._hasFileNumber():
                    self.fileNum = self.stream.readAndUnpack(PR_PRT_FILE_NUM_FORMAT)[0]
                if self._hasChecksum():
                    self.checksum = self.stream.readAndUnpack(PR_PRT_CHECKSUM_FORMAT)[0]
            except RawStream.ExceptionRawStreamEOF:
                self._raiseOrErrorOnEOF('PhysRecRead._readTail() encountered EOF')
    
    def __readOrSkip(self, retVal, theFunc, theSize=-1):
        """Dual purpose function for reading or skipping logical data.
        retVal is the accumulator (LogicaData for read, integer for skip).
        theFunc is the function to call to accumulate.
        theFunc takes retVal as an argument, updates it and returns it."""
        if self.isEOF:
            raise ExceptionPhysRecEOF('PhysRecRead._readOrSkip() on EOF')
        if theSize < 0:
            # Do all the remaining logical data
            while 1:
                retVal = theFunc(retVal, self.ldLen - self._ldIndex)
                self._readTail()
                if self._hasSuccessor():
                    self._readHead()
                else:
                    break
        else:
            # Partial read of theSize bytes
            bytesRead = 0
            while bytesRead < theSize:
                if (theSize - bytesRead) <= (self.ldLen - self._ldIndex):
                    # This is within this PR
                    retVal = theFunc(retVal, theSize - bytesRead)
                    break
                else:
                    # Read all of this LD chunk and the PR tail/head
                    bytesRead += self.ldLen - self._ldIndex
                    retVal = theFunc(retVal, self.ldLen - self._ldIndex)
                    if self._hasSuccessor():
                        self._readTail()
                        self._readHead()
                    else:
                        break
        #print('PhysRecRead.__readOrSkip() returning {:s}'.format(str(retVal)))
        return retVal

    def __readLdWithinPr(self, theLd, size):
        """Function for reading into logical data."""
        assert(size >= 0 and size <= (self.ldLen - self._ldIndex))
        self._ldIndex += size
        self._ldTell += size
        try:
            myLd = self.stream.read(size)
            # We take a hard line here; normally read(n) will return <=n bytes
            # at EOF. However since the physical record header specifies exactly
            # how much should be there we obey the PRH.  
            if len(myLd) != size:
                self._raiseOrErrorOnEOF(
                    'PhysRecRead.__readLdWithinPr() on EOF, wanted {0:d} got {1:d}'.format(size, len(myLd))
                )
            # Note: No else: as _raiseOrErrorOnEOF() might continue
            theLd += myLd
            return theLd
        except RawStream.ExceptionRawStreamEOF as err:
            self._raiseOrErrorOnEOF('PhysRecRead.__readLdWithinPr() on EOF')
    
    def __skipLdWithinPr(self, theCount, size):
        """Function for skipping and counting data."""
        assert(size >= 0 and size <= (self.ldLen - self._ldIndex))
        self._ldIndex += size
        self._ldTell += size
        self.stream.seek(size, 1)
        return theCount + size

    def _readOrSkipPreamble(self):
        """Prepares for a read or skip. Returns True if completed OK.
        May raise ExceptionPhysRecEOF if already at EOF."""
        #print('_readOrSkipPreamble()', '0x{:x}'.format(self.stream.tell()))
        #print(''.join(traceback.format_stack()))
        if self.isEOF:
            raise ExceptionPhysRecEOF('PhysRecRead.read() on EOF')
        if self._mustReadHead:
            self._readHead()
        if not self.hasLd():
            if not self.isEOF:
                self._readTail()
            return False
        return True
    
    def readLrBytes(self, theSize=-1, theLd=None):
        """Reads theSize logical data bytes and returns it as a bytes() object.
        If theSize is -1 all logical data for this logical record is returned.
        If theLd is not None it is extended and returned, otherwise a new
        bytes() object is created and returned.
        Returns None on end of logical record."""
        if not self._readOrSkipPreamble():
            return None
        if theLd is None:
            theLd = bytes()
        return self.__readOrSkip(theLd, self.__readLdWithinPr, theSize)

    def skipLrBytes(self, theSize=-1):
        """Skips logical data and returns a count of skipped bytes.
        If theSize is -1 all logical data for this logical record is skipped
        positioning the stream at end of this logical record (Note: not the 
        beginning of the next logical record).
        Returns 0 on end of logical record."""
        if not self._readOrSkipPreamble():
            return 0
        return self.__readOrSkip(0, self.__skipLdWithinPr, theSize)
    
    def skipToNextLr(self):
        """Skips all remaining logical data, the PR trailer, and the next PR
        header. This positions stream at the start of the next logical record.
        May raise an ExceptionPhysRecEOF if there is no further Logical or
        Physical record.
        Returns the number of Logical Data bytes skipped."""
        r = self.skipLrBytes(-1)
        # This test is because all the LD might have been consumed _and_
        # the PRT by _readOrSkipPreamble() called in skipLrBytes()
        if r != 0 and not self._mustReadHead:
            self._readTail()
        self._readHead()
        #if self.isEOF:
        #    raise ExceptionPhysRecEOF('PhysRecRead.skipToNextLr() gets EOF')
        return r

    def tellLr(self):
        """Returns the absolute file position of the start current Logical
        record. This value can be safely used in seekLr."""
        return self.startOfLr
    
    def tell(self):
        """Returns the absolute position of the file."""
        return self.stream.tell()
        
    def seekLr(self, offset):
        """External setting of file position directly to the beginning of
        a PRH or TIF marker (if present). The caller is fully responsible
        for getting this right!"""
        self.stream.seek(offset, whence=os.SEEK_SET)
        self._reset()
        return self.stream.tell()
    
    def seekCurrentLrStart(self):
        """Setting the file position directly to the beginning of
        a PRH or TIF marker (if present) for the current Logical Rcord."""
        #print('PhysRec.seekCurrentLrStart(): 0x{:8x}'.format(self.startOfLr))
        return self.seekLr(self.startOfLr)
        
    def hasLd(self):
        """Returns True if there is logical data to be read, False otherwise.
        NOTE: This will return False on file initialisation and only return
        True once the Physical Record Header has been read."""
        return (self.ldLen > self._ldIndex) or self._hasSuccessor()
    
    def ldRemaingInPr(self):
        """Returns the number of bytes remaining in this particular Physical
        Record. NOTE: The can be 0 and hasLd() be True if at the end of a
        Physical Record that has a successor record."""
        return self.ldLen - self._ldIndex
    
    def genLd(self):
        """A generator that produces a tuple of (logical data, isLrStart)
        where:
        logical data - A bytes() object for the logical data in the current PR.
        isLrStart - A boolean that is True of that LogicalData is the start of
        a logical record.
        NOTE: This rewinds the current state of this instance."""
        self.seekLr(0)
        while not self.isEOF:
            # TODO: Check for TIF EOF markers and yield (None, None)?
            self._readHead()
            if self.isEOF:
                break
            myLd = self.readLrBytes(self.ldLen)
            self._readTail()
            yield myLd, self.isLrStart

class PhysRecTail(object):
    """Represents Physical Record Tail fields."""
    def __init__(self, hasRecNum=False, fileNum=None, hasCheckSum=False):
        """These three fields are Rep Code type 79 (16 bit signed integer)."""
        self.hasRec = hasRecNum
        self._recNum = 0
        if fileNum is not None \
        and (fileNum < PR_PRT_FILE_NUM_MIN or fileNum > PR_PRT_FILE_NUM_MAX):
            self._fileNum = self._normInt(
                fileNum,
                PR_PRT_FILE_NUM_MIN,
                PR_PRT_FILE_NUM_MAX
            )
            logging.warning(
                'PhysRecTail.__init__(): File number {:d} out of range, normalising to {:d}'.format(fileNum, self._fileNum)
            )
        else:
            self._fileNum = fileNum
        self.hasCheck = hasCheckSum
        self.checkSum = 0
        # Length of PRT
        self._prtLen = 0
        # PR header attributes
        self._prhAttr = 0
        if self.hasRec:
            self._prtLen += PR_PRT_REC_NUM_LEN
            self._prhAttr |= 1 << PR_RECORD_NUMBER_BIT
        if self._fileNum is not None:
            self._prtLen += PR_PRT_FILE_NUM_LEN
            self._prhAttr |= 1 << PR_FILE_NUMBER_BIT
        if self.hasCheck:
            self._prtLen += PR_PRT_CHECKSUM_LEN
            self._prhAttr |= 1 << PR_CHECKSUM_BIT

    def __str__(self):
        return 'PhysRecTail: hasRec={:s}, fileNum={:s}, hasCheckSum={:s}'.format(
            str(self.hasRec), str(self._fileNum), str(self.hasCheck)
        )

    def _normInt(self, v, theMin, theMax):
        assert(theMin < theMax)
        return ((v - theMin) % (theMax - theMin + 1)) + theMin
    
    @property
    def recNum(self):
        return self._recNum
    
    @property
    def fileNum(self):
        return self._fileNum
    
    @property
    def prtLen(self):
        return self._prtLen
    
    @property
    def prhAttr(self):
        """Returns the PRH attributes, to be or'd with any other attributes."""
        return self._prhAttr
    
    def hasTail(self):
        """Returns True if any PRT field is present, False otherwise."""
        return self.hasRec or self._fileNum is not None or self.hasCheck
        
    def computeCheckSum(self, theB):
        """Computes the checksum of the byte stream."""
        self.checkSum = 0
        if self.hasCheck:
            for i in range(0, len(theB)-1, 2):
                t = theB[i+1] + 256 * theB[i]
                self.checkSum += t
                if self.checkSum & 0x10000:
                    self.checkSum += 1
                self.checkSum *= 2
                if self.checkSum & 0x10000:
                    self.checkSum += 1
                self.checkSum &= 0xFFFF
        
    def prtRecNum(self):
        r = b''
        if self.hasRec:
            if self._recNum < PR_PRT_REC_NUM_MIN or self._recNum > PR_PRT_REC_NUM_MAX:
                oldRecNum = self._recNum
                self._recNum = self._normInt(
                    self._recNum,
                    PR_PRT_REC_NUM_MIN,
                    PR_PRT_REC_NUM_MAX
                )
                logging.warning(
                    'PhysRecTail.__init__(): Record number {:d} out of range, normalising to {:d}'.format(oldRecNum, self._recNum)
                )
            r = PR_PRT_REC_NUM_FORMAT.pack(self._recNum)
            self._recNum +=1
        return r

    def prtFileNum(self):
        if self._fileNum is not None:
            return PR_PRT_FILE_NUM_FORMAT.pack(self._fileNum)
        return b''

    def prtCheckSum(self):
        if self.hasCheck:
            return PR_PRT_CHECKSUM_FORMAT.pack(self.checkSum)
        return b''

class PhysRecWrite(PhysRecBase):
    """Specialisation of PhysRecBase for writing to files."""
    def __init__(self,
            theFile,
            theFileId=None,
            keepGoing=False,
            hasTif=False,
            thePrLen=PR_MAX_LENGTH,
            thePrt=PhysRecTail(),
        ):
        """Constructor with:
        theFile - A file like object or string, if the latter it assumed to be a path.
        theFileId - File identifier, this could be a path for example. If None the RawStream will try and cope with it.
        keepGoing - If True we do our best to keep going.
        hasTif - Insert TIF markers or not.
        thePrLen - Max Physical Record length, defaults to the maximum possible length.
        thePrt - Physical Records Trailer settings (defaults to PhysRec.PhysRecTail())."""
        super().__init__(theFileId, keepGoing)
        #print('thePrt', thePrt)
        try:
            self.stream = RawStream.RawStream(theFile, mode='wb', fileId=self.fileId)
        except IOError:
            raise ExceptionPhysRec('PhysRecWrite: Can not open LIS file "%s" for read' % self.fileId)
        self.tif = None
        if hasTif:
            self.tif = TifMarker.TifMarkerWrite()
        self._prLen = thePrLen
        self._prt = thePrt
        # Calculate the maximum payload length
        self._maxPayloadLen = self._prLen - PR_PRH_LENGTH - self._prt.prtLen
        if self._prLen > PR_MAX_LENGTH:
            raise ExceptionPhysRecWrite(
                'PhysRecWrite PR length {:d} greater than allowed: {:d}'.format(
                    self._prLen, PR_MAX_LENGTH
                )
            )
        if self._maxPayloadLen < 1:
            raise ExceptionPhysRecWrite(
                'PhysRecWrite no space for payload in {:d} in PR length {:d}'.format(self._maxPayloadLen, self._prLen)
            )
    
    def close(self):
        """Close the Physical Record Handler and the underlying stream."""
        if self.tif is not None:
            self.tif.close(self.stream)
        self.stream.close()
    
    def writeLr(self, theLr):
        """Splits a Logical Record into into Physical Records and writes them
        to the stream. These Physical Records have trailer records if required.
        Returns the tell() of the start of the LR."""
        assert(self._maxPayloadLen > 0)
        ofs = 0
        myTell = self.stream.tell()
        while ofs < len(theLr):
            myB = bytearray()
            myPayLoad = theLr[ofs:ofs+self._maxPayloadLen]
            # Pack the PR length for the PRH
            myB.extend(PR_PRH_LEN_FORMAT.pack(
                PR_PRH_LENGTH + len(myPayLoad) + self._prt.prtLen)
            )
            # Set PRH attributes to indicate trailer (if any)
            self.prAttr = self._prt.prhAttr
            # Set successor and predecessor in PRH attributes
            if ofs + self._maxPayloadLen < len(theLr):
                # Will have a successor record next time around
                self._setSuccessor(True)
            if ofs > 0:
                # Has a predecessor record
                self._setPredecessor(True)
            myB.extend(PR_PRH_ATTR_FORMAT.pack(self.prAttr))
            # Add payload
            myB.extend(myPayLoad)
            # Add Physical record trailer (this increments PR record etc.)
            myB.extend(self._prt.prtRecNum())
            myB.extend(self._prt.prtFileNum())
            # Finally the checksum
            self._prt.computeCheckSum(myB)
            myB.extend(self._prt.prtCheckSum())
            if self.tif is not None:
                self.tif.write(self.stream, len(myB))
            self.stream.write(myB)
            ofs += len(myPayLoad)
        return myTell
