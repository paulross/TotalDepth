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
"""Represents logical data, i.e. the concatenation of logical record segments

Created on Oct 12, 2011

@author: paulross

00000050: 20 00 FF 01 00 7C 80 00 F0 0B 46 49 4C 45 2D 48      ....|....FILE-H
00000060: 45 41 44 45 52 34 0F 53 45 51 55 45 4E 43 45 2D     EADER4.SEQUENCE-
00000070: 4E 55 4D 42 45 52 14 34 02 49 44 14 70 64 00 01     NUMBER.4.ID.pd..
00000080: 31 21 0A 20 20 20 20 20 20 20 20 20 31 21 41 46     1!.         1!AF
00000090: 4C 49 50 5F 30 30 33 20 20 20 20 20 20 20 20 20     LIP_003         
000000A0: 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20                     
000000B0: 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20                     
000000C0: 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20                     
000000D0: 04 20 80 01 F0 06 4F 52 49 47 49 4E 3C 07 46 49     . ....ORIGIN<.FI
000000E0: 4C 45 2D 49 44 01 14 3C 0D 46 49 4C 45 2D 53 45     LE-ID..<.FILE-SE
000000F0: 54 2D 4E 41 4D 45 01 13 3C 0F 46 49 4C 45 2D 53     T-NAME..<.FILE-S

Visible record header, version 1:
00000050: 20 00 FF 01

Logical segment header, version 1:
00000050:             00 7C 80 00 F0 0B 46 49 4C 45 2D 48         .|....FILE-H
00000060: 45 41 44 45 52 34 0F 53 45 51 55 45 4E 43 45 2D     EADER4.SEQUENCE-
00000070: 4E 55 4D 42 45 52 14 34 02 49 44 14 70 64 00 01     NUMBER.4.ID.pd..
00000080: 31 21 0A 20 20 20 20 20 20 20 20 20 31 21 41 46     1!.         1!AF
00000090: 4C 49 50 5F 30 30 33 20 20 20 20 20 20 20 20 20     LIP_003         
000000A0: 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20                     
000000B0: 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20                     
000000C0: 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20                     

Segment is 0x007c long 124 bytes.
Attributes: 0x80
But this looks like an EFLR so when the spec says bit 1 does that mean the MSB, bit 7?
Hmm yes as v2 of the spec calls the MSB byte 1 bit 8
Type: 0x00 so Appendix A of RP66v1 says this is a FILE-HEADER

0x58: 0xF00B    'FILE-HEADER' - 0x0B is len()
0x65: 0x340F    'SEQUENCE-NUMBER' - 0x0F is len()

Then at 0x76: 14 34 02 49 44 14 70 64???
0x76: 0x1434
0x78: 0x02     'ID'
0x7B: 14 70 64???

0x7E: 0x0001    '1'
0x81: 0x210A    '         1'
0x8d: 0x2141    'FLIP_003' and 9+48=59 spaces
8+9+48 = 65 or 0x41

000000D0: 04 20 80 01 F0 06 4F 52 49 47 49 4E 3C 07 46 49     . ....ORIGIN<.FI
000000E0: 4C 45 2D 49 44 01 14 3C 0D 46 49 4C 45 2D 53 45     LE-ID..<.FILE-SE
000000F0: 54 2D 4E 41 4D 45 01 13 3C 0F 46 49 4C 45 2D 53     T-NAME..<.FILE-S

"""

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

from TotalDepth.RP66 import ExceptionTotalDepthRP66
import TotalDepth.RP66.core.RepCode as RepCode
import TotalDepth.RP66.core.VisiRec as VisiRec
import TotalDepth.RP66.core.Encryption as Encryption

class ExceptionLogiData(ExceptionTotalDepthRP66):
    pass

class ExceptionLogiDataEndData(ExceptionLogiData):
    pass

class LogiDataBase(object):
    """Represents logical data, i.e. the contents of a Logical Record."""
    # Length of the segment including encryption, header and trailer
    segLen = 0
    # Segment attributes
    segAttr = None
    # Type of Logical record (version 1 only). Otherwise reserved bits in v2.
    lrType = None
    # An Encryption.EncryptionPacketBase
    encryptPkt = None
    # Length of the available data in a particular segment
    # This includes the padding bytes (if any).
    dataLen = 0
    # Current position in the segment
    segPos = 0
    # File position given by tell() on the stream at start of the header of the first segment
    filePos = 0
    # Optional fields in the trailer
    padCount = None
    checksum = None
    segLenTrail = None
    # {version : { field : bit_mask, ...}, ...}
    VERSION_ATTR_MAP = {
        1 : {
             7 : 0x80,
             6 : 0x40,
             5 : 0x20,
             4 : 0x10,
             3 : 0x08,
             2 : 0x04,
             1 : 0x02,
             0 : 0x01,
        },
        2 : {
             7 : 0x8000,
             6 : 0x4000,
             5 : 0x2000,
             4 : 0x1000,
             3 : 0x0800,
             2 : 0x0400,
             1 : 0x0200,
             0 : 0x0100,
        },
    }
    def __init__(self, thePath):
        self.path = thePath
        
    def __str__(self):
        if self.version == 1:
            return '{0:s} Length={1:8d} [0x{1:08x}] Version={2:d} attr=0x{3:02x} [{3:8b}] tell=0x{4:08x}'.format(
                repr(self),
                self.segLen,
                self.version,
                self.segAttr,
                self.filePos,
            )
        return '{:s} Length={1:8d} [0x{1:08x}] Version={2:d} attr=0x{3:04x} [{3:16b}] tell=0x{4:08x}'.format(
            repr(self),
            self.segLen,
            self.version,
            self.segAttr,
            self.filePos,
        )
    
    @property
    def version(self):
        assert(self._stream is not None)
        v = self._stream.version
        assert(v in self.VERSION_ATTR_MAP)
        return v
        
    def _checkSegAttr(self, n):
        """Returns True if the Nth bit is set."""
        assert(self.segAttr is not None)
        return self.segAttr & self.VERSION_ATTR_MAP[self.version][n] != 0
        
    @property
    def isIFLR(self):
        return self._checkSegAttr(7)

    @property
    def hasPredecessor(self):
        """True if the segment has a predecessor segment."""
        return self._checkSegAttr(6)

    @property
    def hasSuccessor(self):
        """True if the segment has a successor segment."""
        return self._checkSegAttr(5)

    @property
    def isEncrypted(self):
        return self._checkSegAttr(3)

    @property
    def hasChecksum(self):
        return self._checkSegAttr(2)

    @property
    def hasTrailingLength(self):
        return self._checkSegAttr(1)

    @property
    def hasPadding(self):
        return self._checkSegAttr(0)
    
    @property
    def hasTrailer(self):
        return self.hasPadding or self.hasChecksum or self.hasTrailingLength
    
    @property
    def lenTrailer(self):
        r = 0
        if self.hasPadding:
            r += 4 # ULONG
        if self.hasChecksum:
            r += 2 # UNORM
        if self.hasTrailingLength:
            r += 4 # ULONG
        return r
    
    @property
    def remaining(self):
        return self.dataLen - self.segPos

    @property
    def hasRemaining(self):
        return self.remaining > 0 or self.hasSuccessor

class LogiDataRead(LogiDataBase):
    def __init__(self, thePath):
        super().__init__(thePath)
        self._stream = VisiRec.VisibleRecordRead(self.path)
        self._readHeader()

    @property
    def strOfFile(self):
        """The description of the file stream object."""
        return self._stream.strOfFile
    
    def _checkAndSetAttrs(self, newAttr):
        """Attribute error checking, consistency checking against self.segAttr."""
        # TODO: 
        self.segAttr = newAttr
    
    def _readHeader(self):
        myFilePos = self._stream.tell()
        if self.version == 1:
            self.segLen = RepCode.readUNORM(self._stream)
            myAttr = RepCode.readUSHORT(self._stream)
            self.lrType = RepCode.readUSHORT(self._stream)
            # Magic number 4 is length of UNORM + USHORT + USHORT
            self.dataLen = self.segLen - 4
        else:
            self.segLen = RepCode.readULONG(self._stream)
            myAttr = RepCode.readUNORM(self._stream)
            self.lrType = None
            # Magic number 6 is length of ULONG + UNORM
            self.dataLen = self.segLen - 6
        # Attribute error checking, consistency checking
        self._checkAndSetAttrs(myAttr)
        self.dataLen -= self.lenTrailer
        self.segPos = 0
        if self.version == 1:
            print('TRACE: LogiData._readHeader(): tell=0x{0:08x} length={1:6d} [0x{1:04x}] attr=0x{2:2x} [{2:8b}] type={3:d}'.format(
                    myFilePos,
                    self.segLen,
                    self.segAttr,
                    self.lrType,
                )
            )
        else:
            print('TRACE: LogiData._readHeader(): tell=0x{0:08x} length={1:6d} [0x{1:04x}] attr=0x{2:2x} [{2:8b}]'.format(
                    myFilePos,
                    self.segLen,
                    self.segAttr,
                )
            )
        if not self.hasPredecessor:
            # First segment
            self.filePos = myFilePos
        # Handle encryption
        if self.isEncrypted:
            self.encryptPkt = Encryption.EncryptionPacketRead(self._stream)
            self.dataLen -= len(self.encryptPkt)
        else:
            self.encryptPkt = None
        if self.dataLen < 0:
            raise ExceptionLogiData('Illegal negative data length of {:d}'.format(self.dataLen))
        return True

    def _readTrailer(self):
        if self.hasTrailer:
            if self.hasPadding:
                self.padCount = RepCode.readULONG(self._stream)
            else:
                self.padCount = None
            if self.hasChecksum:
                self.checksum = RepCode.readUNORM(self._stream)
            else:
                self.checksum = None
            if self.hasTrailingLength:
                self.segLenTrail = RepCode.readULONG(self._stream)
            else:
                self.segLenTrail = None

    def read(self, n):
        """Reads n bytes and returns them. If n < 1 then all remaining bytes
        in this visible record are read, including the trailer.
        Raises ExceptionVisRecEOF if n bytes can not be read."""
        r = bytearray()
        try:
            while n < 0 or n > len(r):
                if n < 0:
                    toRead = self.remaining
                else:
                    toRead = n - len(r)
                if self.remaining <= toRead:
                    # Read all of this segment
                    print('Reading all of the segment', self.remaining)
                    if self.remaining > 0:
                        r.extend(self._stream.read(self.remaining))
                    self._readTrailer()
                    if self.hasSuccessor:
                        self._readHeader()
                    else:
                        # End of record
                        break
                else:
                    # Partial read of this segment
                    print('Reading part of the segment', toRead)
                    r.extend(self._stream.read(toRead))
                self.segPos += toRead
        except VisiRec.ExceptionVisRecEOF as err:
            raise ExceptionLogiDataEndData('Logical data.read(): {:s}'.format(str(err)))
        return bytes(r)
    
    def skipToNextRecord(self):
        """Skips to the next segment, returns the number of bytes
        consumed or -1 on EOF."""
        r = len(self.read(-1))
        print('skipToNextRecord', r)
        if r <= 0:
            return -1
        self._readHeader()
        return r

