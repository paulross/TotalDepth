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
TIF Markers
===========
These are 3x32bit little-endian integers at the beginning of each Physical Record.

Word[0]
-------
This is the TIF set type, 0 for a normal TIF set. 1 for an EOF set.

Word[1]
-------
This is the physical file location of the start of the previous set.

Word[2]
-------
This is the physical file location of the start of the next set.

A dump looks like this::

               0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
    00000000: 00 00 00 00 00 00 00 00 4A 00 00 00 00 3E 00 00
    00000010: 80 00 32 30 30 30 39 39 2E 44 41 54 20 20 20 20
    00000020: 20 20 20 20 20 20 20 20 20 20 20 20 39 39 2F 30
    00000030: 34 2F 32 39 20 20 31 30 32 34 20 20 20 20 20 20
    00000040: 20 20 20 20 20 20 2E 20 20 20 00 00 00 00 00 00
    00000050: 00 00 56 04 00 00 04 00 00 01 40 00 01 01 42 00
    00000060: 02 01 42 00 03 04 49 00 00 02 34 04 01 42 01 05
    ...
    00000450: 20 20 44 45 47 20 00 00 00 00 4A 00 00 00 62 08
    00000460: 00 00 04 00 00 03 00 00 00 00 00 00 00 04 20 20
    00000470: 00 01 44 20 20 20 20 20 31 30 41 20 20 20 20 20
    ...
    00000860: 46 4E 00 00 00 00 56 04 00 00 6E 0C 00 00 04 00
    00000870: 00 03 4F 52 20 20 20 20 20 20 20 20 20 20 20 20
    ...
    ...
    ...
    0016E770: 18 00 BA 83 18 00 00 00 00 00 30 E5 16 00 C0 E7
    0016E780: 16 00 00 3E 00 00 81 00 32 30 30 30 39 39 2E 44
    ...
    0016E7B0: 20 20 20 20 20 20 20 20 20 20 20 20 2E 20 20 20
    0016E7C0: 01 00 00 00 76 E7 16 00 CC E7 16 00 01 00 00 00
    0016E7D0: C0 E7 16 00 D8 E7 16 00                        

Or::

    tell()       TIF type           TIF back           TIF next
    00000000:    00 00 00 00        00 00 00 00        00 00 00 4A
    0000004A:    00 00 00 00        00 00 00 00        00 00 04 56
    00000456:    00 00 00 00        00 00 00 4A        00 00 08 62
    00000862:    00 00 00 00        00 00 04 56        00 00 0C 6E
    ...
    0016E776:    00 00 00 00        00 16 E5 30        00 16 E7 C0
    0016E7C0:    00 00 00 01        00 16 E7 76        00 16 E7 CC
    0016E7CC:    00 00 00 01        00 16 E7 C0        00 16 E7 D8
    0016E7D8: EOF
"""

__author__ = 'Paul Ross'
__date__ = '2010-11-05'
__version__ = '0.1.2'
__copyright__ = '(c) 2010 Paul Ross.'

import logging
import struct
from TotalDepth.LIS import ExceptionTotalDepthLIS
# TODO: This is a bit clunky as we only need the Exception from RawStream
from TotalDepth.LIS.core import RawStream

class ExceptionTifMarker(ExceptionTotalDepthLIS):
    """Specialisation of exception for Physical Records."""
    pass

# TIF Constants
#: Number of bytes in a TIF word
TIF_WORD_BYTES                  = 4 # 32 bit unsigned ints (big endian)
#: Number of words in a TIF marker
TIF_NUM_WORDS                   = 3
#: Number of bytes in a TIF marker
TIF_TOTAL_BYTES                 = TIF_WORD_BYTES * TIF_NUM_WORDS
#: struct.Struct() format for a TIF word
TIF_WORD_FORMAT                 = struct.Struct('<L')
#: struct.Struct() format for a TIF word written wrongly as little-endian
TIF_WORD_FORMAT_WRONG_SEX       = struct.Struct('>L')
#: struct.Struct() format for a TIF marker
# FIXME: This is writing in little endian but should be big endian. Glad we are ignoring TIF markers.
# FIXME: Should be > not <
TIF_WORD_ALL_FORMAT             = struct.Struct('<%dL' % TIF_NUM_WORDS)
#: struct.Struct() format for a TIF marker written wrongly as little-endian
TIF_WORD_ALL_FORMAT_WRONG_SEX   = struct.Struct('>%dL' % TIF_NUM_WORDS)
#: The maximum possible size of the first 'next' word. If larger than this then
#: the words are written wrongly as little-endian and need to be reversed
#: This is calculated as the maximum PR length + TIF bytes.
TIF_FIRST_WORD_LIMIT            = 0xFFFF + TIF_TOTAL_BYTES
# Sanity check
assert(TIF_WORD_FORMAT.size                 == TIF_WORD_BYTES)
assert(TIF_WORD_FORMAT_WRONG_SEX.size       == TIF_WORD_BYTES)
assert(TIF_WORD_ALL_FORMAT.size             == TIF_TOTAL_BYTES)
assert(TIF_WORD_ALL_FORMAT_WRONG_SEX.size   == TIF_TOTAL_BYTES)

class TifMarkerBase(object):
    """Base class for TIF markers."""
    def __init__(self, raiseOnError=True):
        """Constructor, initialises internals."""
        self.hasTif = True
        self.isReversed = False
        self.tifType = 0
        self.tifBack = 0
        self.tifNext = 0
        self.raiseOnError = raiseOnError

    def strHeader(self):
        """Header string for an ASCII dump."""
        return 'TIF %5s  :    %08s    %08s    %08s' % ('?', 'Type', 'Back', 'Next')

    def __str__(self):
        """String representation."""
        if self.isReversed:
            r = '<'
        else:
            r = '>'
        return 'TIF %5s %s:  0x%8x  0x%8x  0x%8x' % \
            (self.hasTif, r, self.tifType, self.tifBack, self.tifNext)
            
    def markers(self):
        """Current values of markers as a tuple of three integers."""
        return self.tifType, self.tifBack, self.tifNext
    
    @property
    def eof(self):
        """True if I have encountered a EOF marker."""
        return self.tifType == 1
    
    def reset(self):
        """Resets the TIF markers to all zero, this means hasPrevious is False."""
        self.tifType = 0
        self.tifBack = 0
        self.tifNext = 0
        
    def reportError(self, theMsg):
        """Reports the error. I constructed with raiseOnError as True this will
        raise a ExceptionTifMarker otherwise it will write the error to the log."""
        if self.raiseOnError:
            raise ExceptionTifMarker(theMsg)
        else:
            logging.error(theMsg)

class TifMarkerRead(TifMarkerBase):
    """Class for reading TIF markers. This will automatically determine if TIF
    markers are present and automatically correct ill-formed little-endian TIF markers.
    
    theStream - the file stream.
    
    allowPrPadding - If True this will consume spurious padding bytes after the
    Physical Record tail i.e. the TIF markers determine the Physical Record structure
    rather than the Physical Record Headers."""
    def __init__(self, theStream, allowPrPadding=False):
        """Constructor, initialises internals.
        allowPrPadding - If true this allows padding bytes after the PRT.
        """
        super().__init__()
        theStream.seek(0)
        self.previousTell = 0
        # Explore the stream to see if it looks like there is a TIF marker there
        try:
            self._readBigEndian(theStream)
        except RawStream.ExceptionRawStreamEOF:
            # Very short file, can not read 12 bytes so no TIF then
            self.hasTif = False
        else:
            if not (self.tifType == 0 and self.tifBack == 0):
                self.hasTif = False
            # Handle erroneously little-endian TIF markers
            elif self.tifNext > TIF_FIRST_WORD_LIMIT:
                self.isReversed = True
        # Reset the stream and me
        theStream.seek(0)
        self.tifType = 0
        self.tifBack = 0
        self.tifNext = 0
        self._prPad = allowPrPadding
        
    @property
    def hasPrevious(self):
        """True if a Physical Record has been read, cleared on reset()."""
        return self.previousTell is not None \
            and (self.tifType, self.tifBack, self.tifNext) != (0, 0, 0)
    
    def reset(self):
        """Calling reset() means that the caller is probably randomly
        accessing the file so we can not error check the previous marker in
        the same way that we can if we are reading the file linearly."""
        super(TifMarkerRead, self).reset()
        self.previousTell = None
    
    def read(self, theStream):
        """Read TIF markers from a RawStream object. Returns the stream tell()
        or None  of the start of the TIF marker. This is not necessarily the
        same as the stream tell() seen by the caller as we might consume PR padding."""
        if self.hasTif:
            r = self._read(theStream)
            # Check for EOF, if so read duplicate EOF marker
            if self.tifType == 1:
                self._read(theStream)
            return r

    def _read(self, theStream):
        """Read TIF markers from a RawStream object. Returns the tell() of the
        start of the TIF marker. This is not necessarily the same as the stream
        tell() seen by the caller as we might consume PR padding."""
        if self.hasTif:
            retTell = theStream.tell()
            if self.hasPrevious and self.tifNext != retTell:
                shortFall = self.tifNext - retTell
                # If PR trailing padding is allowed then seek the shortfall
                # (if positive) and continue.
                if self._prPad and shortFall > 0:
                    logging.warning(
                        'TifMarkerRead: tell 0x{:x} making up PR padding of 0x{:x} by seeking to 0x{:x}'.format(
                                retTell,
                                shortFall,
                                self.tifNext,
                        )
                    )
                    theStream.seek(self.tifNext)
                    retTell = theStream.tell()
                else:
                    self.reportError('TIF read() expected 0x%X, got tell: 0x%X, Shortfall: 0x%X' \
                        % (self.tifNext, retTell, shortFall)
                    )
            if self.isReversed:
                # Erroneously little-endian TIF markers
                self._readLittleEndian(theStream)
            else:
                # Correctly big-endian TIF markers
                self._readBigEndian(theStream)
            if self.hasPrevious and self.tifBack != self.previousTell:
                msg = 'TIF read(): tell 0x%x expected previous 0x%X, got 0x%X' \
                                         % (retTell, self.tifBack, self.previousTell)
                # Error check here
                self.reportError(msg)
            self.previousTell = retTell
            return retTell

    def _readBigEndian(self, theStream):
        """Reads from stream, does not test against state."""
        self.tifType, self.tifBack, self.tifNext = theStream.readAndUnpack(TIF_WORD_ALL_FORMAT)
        
    def _readLittleEndian(self, theStream):
        """Reads from stream with reversed markers, does not test against state."""
        self.tifType, self.tifBack, self.tifNext = theStream.readAndUnpack(TIF_WORD_ALL_FORMAT_WRONG_SEX)
        
class TifMarkerWrite(TifMarkerBase):
    """Class for writing TIF markers."""
    def __init__(self):
        """Constructor, initialises internals."""
        super().__init__()
        self.previousDiff = 0
    
    def write(self, theStream, theLen):
        """Write TIF markers to a RawStream object. theLen must be the length
        of the Physical Record including the PRH and PRT."""
        if self.hasTif:
            self.tifNext += theLen + TIF_TOTAL_BYTES
            theStream.packAndWrite(
                            TIF_WORD_ALL_FORMAT,
                            self.tifType,
                            self.tifBack,
                            self.tifNext,
                        )
            self.tifBack += self.previousDiff
            self.previousDiff = theLen + TIF_TOTAL_BYTES
    
    def close(self, theStream):
        """Write TIF EOF markers."""
        self.tifType = 1
        self.write(theStream, 0)
        self.write(theStream, 0)
