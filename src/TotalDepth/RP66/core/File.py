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
'''
Created on Aug 8, 2011

@author: paulross
'''

import time
import io
from TotalDepth.RP66 import ExceptionTotalDepthRP66

class ExceptionFile(ExceptionTotalDepthRP66):
    pass

class ExceptionFileRead(ExceptionFile):
    pass

class ExceptionFileReadInit(ExceptionFileRead):
    pass

class ExceptionFileReadData(ExceptionFileRead):
    pass

class ExceptionFileReadEOF(ExceptionFileRead):
    pass

class FileBase(object):
    """Base class for RP66 file operations."""
    # "Storage Unit Label" length in bytes for each version,
    # this also defines which versions are supported
    SUL_VERSION_AND_LENGTH = {
        1 : 80,
        2 : 128,
    }
    # Storage unit structure
    SUS_ENUM = (b'RECORD', b'FIXREC', b'RECSTM', b'FIXSTM')
    def __init__(self, path):
        """Constructor."""
        self._path = path
        self._fs = None
        #===> Common fields for all versions
        # Storage unit sequence number. An integer.
        self._susn = -1
        # Current support for version 1 and 2. An integer.
        self._version = 0
        # Format from the Storage Unit Label 00 to 99. An integer.
        self._format = -1
        # Storage Unit Structure, one of b'RECORD', b'FIXREC', b'RECSTM', b'FIXSTM'
        self._sus = None
        # Maximum visible record length. An integer.
        self._maxVisLen = -1
        # Storage Set Identifier: 60 bytes
        self._ssi = None
        #===> Additional fields for v2, set to nonsense for v1
        # Binding edition for v2: 1->999
        self._bindEd = -1
        # Producer code for v2:
        self._prodCode = None
        # Creation date for v2:
        self._createDate = None
        # Serial number for v2:
        self._serialNum = None
        
    def __str__(self):
        r = ['RP66 file: {:s}'.format(self._path),]
        r.append('SUSN={:d} Vers.={:d} Format={:d} SUS={:s} Max. Len.={:d}'.format(
                self._susn,
                self._version,
                self._format,
                str(self._sus),
                self._maxVisLen,
            )
        )
        r.append(str(self._ssi))
        # TODO: Version 2 information
        return '\n'.join(r)
        
    def read(self, n):
        """Reads exactly n bytes and returns them. Raises ExceptionFileReadEOF
        if exactly n bytes can not be read."""
        assert(n > 0) 
        r = self._fs.read(n)
        if len(r) != n:
            raise ExceptionFileReadEOF('Can not read {:d} bytes only {:d}'.format(n, len(r)))
        return r
    
    def _readAsInteger(self, n, raiseOnValError=True):
        """Reads n bytes and returns them as an integer by using int().
        Raises ExceptionFileReadData if n bytes can not be read or not an integer.
        If raiseOnValError is True then int() conversion can raise ExceptionFileReadData
        otherwise int() conversion failure returns None."""
        assert(n > 0) 
        b = self._fs.read(n)
        if len(b) != n:
            raise ExceptionFileReadData('Can not read {:d} bytes only {:d}'.format(n, len(b)))
        try:
            r = int(b)
        except ValueError:
            if raiseOnValError:
                raise ExceptionFileReadData('Can not determine integer RP66 version number from {:s}'.format(b))
            r = None
        return r
    
    def _skip(self, n):
        """seek() n bytes from current position and discard. n can be negative"""
        self._fs.seek(n, io.SEEK_CUR)
    
    def tell(self):
        """Returns current stream position."""
        return self._fs.tell()
    
    @property
    def version(self):
        assert(self._version in self.SUL_VERSION_AND_LENGTH)
        return self._version
    
class FileRead(FileBase):
    def __init__(self, path):
        super().__init__(path)
        try:
            self._fs = open(self._path, 'rb')
        except IOError as err:
            raise ExceptionFileReadInit('Can not open stream with: {:s}'.format(str(err)))
        # Read "Storage Unit Label", this determines which version of RP66 is in use.
        # Example for version 1: b'   1V1.00RECORD 8192Default Storage Set                                         '
        # Has these fields:
        #(
        #    b'   1',
        #    b'V1.00',
        #    b'RECORD',
        #    b' 8192',
        #    b'Default Storage Set                                         ',
        #)
        # First 4 bytes are Storage unit sequence number
        v = self.read(4)
        try:
            self._susn = int(v)
        except ValueError:
            raise ExceptionFileReadInit('Can not determine integer Storage unit sequence number from {:s}'.format(v))
        # Next 5 bytes are RP66 version and format edition in the form "VN.nn".
        # Where N is '1' or '2' and nn is the format edition, "00".
        v = self.read(5)
        # Apply semantic tests
        if chr(v[0]) != 'V' or not v[1:2].isdigit() or not v[2] == ord('.') or not v[3:5].isdigit():
            raise ExceptionFileReadInit('Can not interpret RP66 version and format edition {:s}'.format(v))
        try:
            self._version = int(v[1:2])
        except ValueError:
            raise ExceptionFileReadInit('Can not determine integer RP66 version number from {:s}'.format(v))
        if self._version not in self.SUL_VERSION_AND_LENGTH:
            raise ExceptionFileReadInit('RP66 version number {:d} not supported'.format(self._version))            
        try:
            self._format = int(v[3:5])
        except ValueError:
            raise ExceptionFileReadInit('Can not determine integer RP66 format number from {:s}'.format(v))
        # Next 6 bytes is the Storage unit structure e.g. "RECORD"
        self._sus = self.read(6)
        if self._sus not in self.SUS_ENUM:
            raise ExceptionFileReadInit('Storate Unit Structure {:s} not in {:s}'.format(self._sus, str(self.SUS_ENUM)))
        # Now we switch according to version 1 or 2 of the standard
        if self._version == 1:
            # Read the max record length (5 bytes)
            self._maxVisLen = self._readAsInteger(5)
        elif self._version == 2:
            # Version 2 additional fields
            self._bindEd = self._readAsInteger(4)
            if self._bindEd < 1 or self._bindEd > 999:
                raise ExceptionFileReadInit('RP66 binding edition {:d} out of range'.format(self._bindEd))
            self._maxVisLen = self._readAsInteger(10)
            # Producer code can be blank, we interpret this as None
            self._prodCode = self._readAsInteger(10, raiseOnValError=False)
            # Creation date
            # TODO: Catch ValueError (and any others) as this field could be blank
            self._createDate = time.strptime(self.read(11).decode('ascii').lower(), "%d-%b-%Y")
            self._serialNum = self.read(12)
            self._skip(6)
        # Finally the Storage Set Identifier (60 bytes) that is common to both versions
        self._ssi = self.read(60)
        assert(self._fs is not None and self._version in self.SUL_VERSION_AND_LENGTH)
        # This might raise and error but how to test it?
        assert(self.SUL_VERSION_AND_LENGTH[self._version] == self._fs.tell())

    def seekStartOfData(self):
        """Seeks the file to the byte following the end of the Storage Unit Lable."""
        assert(self._version in self.SUL_VERSION_AND_LENGTH)
        assert(self._fs is not None)
        self._fs.seek(self.SUL_VERSION_AND_LENGTH[self._version], io.SEEK_SET)

        
        