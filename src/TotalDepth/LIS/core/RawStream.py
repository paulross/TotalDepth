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
"""The RawStream handler provides low-level stream I/O functionality."""

__author__ = 'Paul Ross'
__date__ = '2010-11-05'
__version__ = '0.1.2'
__copyright__ = '(c) 2010 Paul Ross.'

import os
#import struct
from TotalDepth.LIS import ExceptionTotalDepthLIS

class ExceptionRawStream(ExceptionTotalDepthLIS):
    """Specialisation of exception for RawStream."""
    pass

class ExceptionRawStreamEOF(ExceptionRawStream):
    """RawStream premature EOF."""
    pass

class RawStream(object):
    """Class that creates a I/O stream from a file path or file-like object
    and provides various low level functionality on it such as unpacking.
    
    f - A file like object or string, if the latter it assumed to be a path.

    mode - The file mode, defaults to binary read.

    fileId - If f is a string is this is present then this is used as the
    file name. If f is not a string then f.name is used with
    fileId as a fallback.
    """
    def __init__(self, f, mode='rb', fileId=None):
        """Construct with:
        f - A file like object or string, if the latter it assumed to be a path.
        mode - The file mode, defaults to binary read.
        fileId - If f is a string is this is present then this is used as the
        file name. If f is not a string then f.name is used with
        fileId as a fallback.
        """ 
        if type(f) == type(''):
            # Treat as file path
            if fileId is not None:
                self._fileId = fileId
            else:
                self._fileId = f
            self._stream = open(f, mode)
        else:
            self._stream = f
            try:
                self._fileId = f.name
            except AttributeError:
                self._fileId = fileId

    def __enter__(self):
        """Context Manager support."""
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager finalisation, this closes the underlying stream."""
        #self._stream.flush()
        self.close()
        return False

    @property
    def stream(self):
        """Exposes the underlying stream."""
        return self._stream
    
    def tell(self):
        """Return the file's current position, like stdio's ftell."""
        return self._stream.tell()
    
    def seek(self, offset, whence=os.SEEK_SET):
        """Set the file's current position, like stdio's fseek. The whence
        argument is optional and defaults to os.SEEK_SET or 0 (absolute file
        positioning); other values are os.SEEK_CUR or 1 (seek relative to the
        current position) and os.SEEK_END or 2 (seek relative to the file's end).
        There is no return value.
        Not all file objects are seekable."""
        self._stream.seek(offset, whence)
        
    def read(self, theLen):
        """Reads and returns theLen bytes."""
        try:
            return self._stream.read(theLen)
        except ValueError as err:
            raise ExceptionRawStreamEOF(str(err))
        
    def write(self, theB):
        """Writes theB bytes."""
        self._stream.write(theB)
        
    def close(self):
        """Closes the underlying stream."""
        self._stream.close()
    
    def readAndUnpack(self, theStruct):
        """Reads from the stream and unpacks binary data according to the
        struct module format. This returns a tuple.
        
        theStruct - A formated instance of struct.Struct()."""
        myBuf = self._stream.read(theStruct.size)
        if len(myBuf) < theStruct.size:
            raise ExceptionRawStreamEOF('RawStream.readAndUnpack(): EOF; read %s but need %d bytes' \
                                     % (myBuf, theStruct.size))
        return theStruct.unpack(myBuf)
#===============================================================================
#        try:
#            return theStruct.unpack(myBuf)
#        except struct.error as err:
#            raise ExceptionRawStream(str(err))
#===============================================================================
        
    def packAndWrite(self, theStruct, *args):
        """Packs binary data from args and writes it to the stream.

        theStruct - A formated instance of struct.Struct().

        args - The data to write."""
        b = theStruct.pack(*args)
        self._stream.write(b)
#===============================================================================
#        try:
#            b = theStruct.pack(*args)
#            self._stream.write(b)
#        except struct.error as err:
#            raise ExceptionRawStream(str(err))
#===============================================================================
