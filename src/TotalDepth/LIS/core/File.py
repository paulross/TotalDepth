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
""" Reads or writes LIS data to a physical file.

Created on 14 Nov 2010

"""

__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

#import time
#import sys
#import logging
#from optparse import OptionParser

import struct

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import PhysRec

class ExceptionFile(ExceptionTotalDepthLIS):
    """Specialisation of exception for Physical files."""
    pass

class ExceptionFileRead(ExceptionFile):
    """Specialisation of exception for reading Physical files."""
    pass


class ExceptionFileWrite(ExceptionFile):
    """Specialisation of exception for writing Physical files."""
    pass

class FileBase(object):
    """LIS file handler. This handles Physical Records (and TIF records)."""
    def __init__(self, theFile, theFileId, mode, keepGoing):
        assert(mode in ('r', 'w'))
        self.file = theFile
        self.fileId = theFileId
        self.mode = mode
        self.keepGoing = keepGoing

class FileRead(FileBase):
    """LIS file reader, this offers the caller a number of incremental
    read operations. This handles Physical Records (and TIF records).

    theFile - A file like object or string, if the latter it assumed to be a path.

    theFileId - File identifier, this could be a path for example. If None the RawStream will try and cope with it.

    keepGoing - If True we do our best to keep going.
    """
    def __init__(self, theFile, theFileId=None, keepGoing=False):
        """Constructor with:
        theFile - A file like object or string, if the latter it assumed to be a path.
        theFileId - File identifier, this could be a path for example. If None the RawStream will try and cope with it.
        keepGoing - If True we do our best to keep going.
        """
        super(FileRead, self).__init__(theFile, theFileId, 'r', keepGoing)
        try:
            self._prh = PhysRec.PhysRecRead(self.file, self.fileId, self.keepGoing)
        except PhysRec.ExceptionPhysRec as e:
            raise ExceptionFileRead('FileRead.__init__(): error "%s"' % str(e))

    def readLrBytes(self, theLen=-1):
        """Reads theLen LogicalData bytes and returns it or None if nothing
        left to read for this logical record.
        If theLen is -1 all the remaining Logical data is read."""
        try:
            return self._prh.readLrBytes(theLen)
        except PhysRec.ExceptionPhysRec as e:
            raise ExceptionFileRead('LisFileRead.read() PR error "%s"' % e)
    
    def skipLrBytes(self, theLen=-1):
        """Skips logical data and returns a count of skipped bytes.
        If theLen is -1 all the remaining Logical data is read."""
        try:
            return self._prh.skipLrBytes(theLen)
        except PhysRec.ExceptionPhysRec as e:
            raise ExceptionFileRead('LisFileRead.skip() PR error "%s"' % e)

    def seekCurrentLrStart(self):
        """Setting the file position directly to the beginning of
        a PRH or TIF marker (if present) for the current Logical Record."""
        try:
            return self._prh.seekCurrentLrStart()
        except PhysRec.ExceptionPhysRec as e:
            raise ExceptionFileRead('LisFileRead.seekCurrentLrStart() PR error "%s"' % e)
    
    def skipToNextLr(self):
        """Skips the rest of the current Logical Data and positions the file at
        the start of the next Logical Record."""
        try:
            return self._prh.skipToNextLr()
        except PhysRec.ExceptionPhysRec as e:
            raise ExceptionFileRead('LisFileRead.skipToNextLr() PR error "%s" tell: 0x%x' % (e, self._prh.stream.tell()))

    def tellLr(self):
        """Returns the absolute file position of the start current Logical
        record. This value can be safely used in seekLr."""
        return self._prh.tellLr()
    
    def tell(self):
        """Returns the absolute position of the file."""
        return self._prh.tell()
        
    def ldIndex(self):
        """Returns the index position in the current logical data."""
        return self._prh.ldIndex()

    def seekLr(self, offset):
        """External setting of file position directly to the beginning of
        a PRH or TIF marker (if present). The caller is fully responsible
        for getting this right!"""
        return self._prh.seekLr(offset)
        
    def hasLd(self):
        """Returns True if there is logical data to be read, False otherwise.
        NOTE: This will return False on file initialisation and only return
        True once the Physical Record Header (i.e. one or more logical bytes)
        has been read."""
        return self._prh.hasLd()
    
    def rewind(self):
        """Sets the file position to the beginning of file."""
        return self.seekLr(0)
    
    @property
    def isEOF(self):
        """True if at EOF."""
        return self._prh.isEOF
    
    #########################
    # Section: Reading words.
    #########################
    def unpack(self, theStruct):
        """Unpack some logical bytes using the supplied format.
        format ~ a struct.Struct object.
        Returns a tuple of the number of objects specified by the format or None."""
        try:
            myB = self.readLrBytes(theStruct.size)
            if myB is None or len(myB) != theStruct.size:
                # print('WTF')
                # print(type(myB), myB)
                # print(type(theStruct.size), theStruct.size)
                # # TODO: Why do the broken down lines work when the one liner does not?
                # msg = 'FileRead.unpack(): Bytes: {} not enough for struct that needs: {:d} bytes.'.format(myB, theStruct.size)
                # msg = 'FileRead.unpack(): Bytes: '
                # msg += '{}'.format(myB)
                # msg += ' not enough for struct that needs: '
                # msg += '{:d} bytes.'.format(theStruct.size)
                # logging.error(msg)
                raise ExceptionFileRead(
                    'FileRead.unpack(): Bytes: {} not enough for struct that needs: {:d} bytes.'.format(myB, theStruct.size)
                )
            return theStruct.unpack(myB)
        except struct.error as err:
            raise ExceptionFileRead('Bytes: {:s} error: {:s}'.format(myB, str(err)))
        
    #####################
    # End: Reading words.
    #####################

class FileWrite(FileBase):
    """LIS file writer. This handles Physical Records (and TIF records).

    theFile - A file like object or string, if the latter it assumed to be a path.

    theFileId - File identifier, this could be a path for example. If None the RawStream will try and cope with it.

    keepGoing - If True we do our best to keep going.

    hasTif - Insert TIF markers or not.

    thePrLen - Max Physical Record length, defaults to the maximum possible length.

    thePrt - Physical Records Trailer settings (defaults to PhysRec.PhysRecTail()).
    """
    def __init__(self,
            theFile,
            theFileId=None,
            keepGoing=False,
            hasTif=False,
            thePrLen=PhysRec.PR_MAX_LENGTH,
            thePrt=PhysRec.PhysRecTail(),
        ):
        """Constructor with:
        theFile - A file like object or string, if the latter it assumed to be a path.
        theFileId - File identifier, this could be a path for example. If None the RawStream will try and cope with it.
        keepGoing - If True we do our best to keep going.
        hasTif - Insert TIF markers or not.
        thePrLen - Max Physical Record length, defaults to the maximum possible length.
        thePrt - Physical Records Trailer settings (defaults to PhysRec.PhysRecTail()).
        """
        super().__init__(theFile, theFileId, 'w', keepGoing)
        try:
            self._prh = PhysRec.PhysRecWrite(
                self.file,
                self.fileId,
                self.keepGoing,
                hasTif,
                thePrLen,
                thePrt,
            )
        except PhysRec.ExceptionPhysRec as e:
            raise ExceptionFileWrite('FileWrite.__init__(): error "%s"' % str(e))

    def write(self, theLr):
        """Writes the Logical Record to the file. Returns the tell() of the
        start of the LR."""
        return self._prh.writeLr(theLr)
    
    def close(self):
        """Closes the file."""
        self._prh.close()                
