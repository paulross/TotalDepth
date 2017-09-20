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
"""RP66 Visible Records

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

"""

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

import collections
from TotalDepth.RP66 import ExceptionTotalDepthRP66
from TotalDepth.RP66.core import RepCode
from TotalDepth.RP66.core import File

class ExceptionVisRec(ExceptionTotalDepthRP66):
    pass

class ExceptionVisRecEOF(ExceptionVisRec):
    pass

VisiRecInfo = collections.namedtuple('VisiRecInfo', 'maxLen hdrLen')

class VisibleRecordBase(object):
    """Visible record base class. From RP66v2:
    
Table 1 - Visible Record Header Fields
*Note    Field    Size in Bytes    Representation Code
1    Length    4    ULONG
2    The value FF16    1    USHORT
3    Format version    1    USHORT
4    File sequence number    4    ULONG
5    File section number    2    UNORM
"""
    # Version and data map, this also determines what versions are supported
    VERSION_DATA_MAP = {
        # 1: UNORM max, (UNORM, USHORT, USHORT)
        1 : VisiRecInfo(2**16, 2+1+1),
        # 2: ULONG max, (ULONG, USHORT, USHORT, ULONG, UNORM),
        2 : VisiRecInfo(2**32, 4+1+1+4+2),
    }
    # Header attributes
    # Rep code ULONG, 17
    length = None
    # Rep code USHORT, 15
    valueFF = None
    FIXED_VALUE = 0xFF
    # Rep code USHORT, 15
    version = None
    # Rep code ULONG, 17. Not RP66v1.
    fileSeq = None
    # Rep code UNORM, 16. Not RP66v1.
    fileSect = None
    # An RP66 File object
    _stream = None
    # File position given by tell() on the stream at start of the header
    filePos = 0
    # Read position in the visible record
    buffPos = 0
    def __init__(self, thePath):
        self.path = thePath
    
    def __str__(self):
        if self.version == 1:
            return '{0:s} Length={1:8d} [0x{1:x}] Version={2:d} tell=0x{3:08x}'.format(
                repr(self),
                self.length,
                self.version,
                self.filePos,
            )
        return '{0:s} Length={1:8d} [0x{1:x}] Vers={2:d} File seq={3:d} File sect={4:d} tell=0x{5:08x}'.format(
            repr(self),
            self.length,
            self.version,
            self.fileSeq,
            self.fileSect,
            self.filePos,
        )
    
    @property
    def remaining(self):
        return self.length - self.buffPos
    
    def tell(self):
        return self._stream.tell()
        
class VisibleRecordRead(VisibleRecordBase):
    def __init__(self, thePath):
        super().__init__(thePath)
        self._stream = File.FileRead(self.path)
        self._stream.seekStartOfData()
        self._readHeader()
    
    @property
    def strOfFile(self):
        """The description of the file stream object."""
        return str(self._stream)
    
    @property
    def version(self):
        v = self._stream.version
        assert(v in self.VERSION_DATA_MAP)
        return v
    
    def _readHeader(self):
        """Reads the Visible Record header."""
#        # If something has been read and not thing more to read
#        if self.length is not None and self.remaining == 0:
#            self._readTrailer()
        self.filePos = self._stream.tell()
        try:
            # Version dependent, this is UNORM in version 1
            if self.version == 1:
                self.length = RepCode.readUNORM(self._stream)
            else:
                self.length = RepCode.readULONG(self._stream)
        except File.ExceptionFileReadEOF:
            return False
        self.valueFF = RepCode.readUSHORT(self._stream)
        if self.FIXED_VALUE != self.valueFF:
            raise ExceptionVisRec(
                'VisibleRecord.readHeader(): tell=0x{:x} expected fixed value of 0x{:x}, got 0x{:x}'.format(
                    self._stream.tell(),
                    self.FIXED_VALUE,
                    self.valueFF,
                )
            )
        myV = RepCode.readUSHORT(self._stream)
        if self.version != myV:
            raise ExceptionVisRec(
                'VisibleRecord.readHeader(): tell=0x{:x} expected version {:d}, got {:d}'.format(
                    self._stream.tell(),
                    self.version,
                    myV,
                )
            )
        # Version dependent, these do not exist in version 1
        if self.version != 1:
            self.fileSeq = RepCode.readULONG(self._stream)
            self.fileSect = RepCode.readUNORM(self._stream)
        self.buffPos = self._stream.tell() - self.filePos
        return True
            
    def _readTrailer(self):
        """Reads the Visible Record Trailer - not in version 1."""
        assert(self.length is not None)
        if self.version != 1:
            myLength = RepCode.readULONG(self._stream)
            if self.length != myLength:
                raise ExceptionVisRec('VisibleRecord.readTrailer(): expected length of {:d}, got {:d}'.format(self.length, myLength))
    
    def read(self, n):
        """Reads n bytes and returns them. If n < 1 then all remaining bytes
        in this visible record are read, including the trailer.
        Raises ExceptionVisRecEOF if n bytes can not be read."""
        if n < 0:
            n = self.remaining
        r = bytearray()
        try:
            while n > 0:
                left = self.remaining
                if n > left:
                    r.extend(self._stream.read(left))
                    self.buffPos += left
                    self._readTrailer()
                    if not self._readHeader():
                        # EOF
                        break
                    n -= left
                else:
                    r.extend(self._stream.read(n))
                    self.buffPos += n
                    n = 0
        except File.ExceptionFileRead as err:
            raise ExceptionVisRecEOF('Visible Record.read(): {:s}'.format(str(err)))
        return bytes(r)
    
    def skipToNextRecord(self):
        """Skips to the next Visible Record, returns the number of bytes
        consumed or -1 on EOF."""
        r = len(self.read(-1))
        if r <= 0:
            return -1
        self._readHeader()
        return r
