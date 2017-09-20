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
"""Provides a 'look ahead' file buffer where the caller can inspect bytes ahead
of the current position.

Created on Oct 26, 2011
"""

__author__  = 'Paul Ross'
__date__    = '2011-10-26'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

class ExceptionFileBuffer(Exception):
    """Specialisation of Exception for the FileBuffer module."""
    pass

class ExceptionFileBufferEOF(ExceptionFileBuffer):
    """Specialisation of Exception for the FileBuffer EOF."""
    pass

class FileBuffer(object):
    """Provides a buffer interface to a file where the user can look ahead
    any distance from the current position."""
    def __init__(self, f):
        self._file = f
        # List of bytes in the current buffer
        self._buf = []
        # Current file position
        self._tell = self._file.tell()
        
    def tell(self):
        """Current file position."""
        return self._tell
        
    def step(self):
        """Increment the file position by one byte, returns the byte just read."""
        b = self._file.read(1)
        self._tell += 1
        # NOTE: Do not raise EOF if nothing read as caller may still want to
        # access bytes with the current buffer.
        if len(b) > 0:
            self._buf.append(b)
        elif len(self._buf) == 0:
            # Nothing to read, nothing to access
            raise ExceptionFileBufferEOF()
        return self._buf.pop(0)

    def _expandBuffer(self, to):
        while len(self._buf) <= to:
            b = self._file.read(1)
            if len(b) == 0:
                raise IndexError('EOF on index {:d}'.format(to))
            self._buf.append(b)
        
    def __getitem__(self, i):
        """Get an arbitrary byte or slice."""
        if isinstance(i, int):
            self._expandBuffer(i)
            return self._buf[i][0]
        elif isinstance(i, slice):
            # Handle a slice object. Sadly we do not get a lot of help here from python!
#            print('TRACE: xxx', i)
            minIdx = i.start if i.start is not None and i.start >= 0 else 0
            maxIdx = i.stop if i.stop is not None and i.stop >= 0 else len(self._buf)-1
            try:
                self._expandBuffer(max(minIdx, maxIdx))
            except IndexError:
                # Ignore out of range errors as normal slices do
                pass
            return b''.join(self._buf[i])
        else:
            raise TypeError('{:s} not an integer'.format(repr(i)))
