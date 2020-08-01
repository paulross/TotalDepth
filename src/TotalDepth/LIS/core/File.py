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
import io
import logging
import struct
import typing

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import PhysRec

__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2010-2020 Paul Ross'


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

    def __init__(self, theFile, theFileId=None, keepGoing=False, pad_modulo: int = 0, pad_non_null: bool = False):
        """Constructor with:
        theFile - A file like object or string, if the latter it assumed to be a path.
        theFileId - File identifier, this could be a path for example. If None the RawStream will try and cope with it.
        keepGoing - If True we do our best to keep going.
        """
        super(FileRead, self).__init__(theFile, theFileId, 'r', keepGoing)
        try:
            self._prh = PhysRec.PhysRecRead(self.file, self.fileId, self.keepGoing, pad_modulo, pad_non_null)
        except PhysRec.ExceptionPhysRec as e:
            raise ExceptionFileRead('FileRead.__init__(): error "%s"' % str(e))

    def readLrBytes(self, theLen=-1):
        """Reads theLen LogicalData bytes and returns it or None if nothing
        left to read for this logical record.
        If theLen is -1 all the remaining Logical data is read.
        This positions the file at the _next_ Logical Record or EOF."""
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


class PhysicalRecordSettings(typing.NamedTuple):
    """Container for the settings to read Physical Records."""
    pad_modulo: int
    pad_non_null: bool


def best_physical_record_pad_settings(file_path_or_object: typing.Union[str, io.BytesIO],
                                      pr_limit=0) -> typing.Union[None, PhysicalRecordSettings]:
    """This attempts to find the best settings to read Physical Records. It returns a PhysicalRecordSettings on
    success or None on failure.
    pr_limit limits the number of Physical Records to test if you want higher performance otherwise all Physical Records
    are read.

    Typically 38Mb file with 46276 Physical Records processed in 0.380 (s) so 10ms/Mb or 100Mb/s.
    This is proportionate so if limited to 100 records this would be around 0.001 (s)
    """
    logging.info(f'Finding best PR settings for: {file_path_or_object}')
    file_id = file_path_or_object if isinstance(file_path_or_object, str) else 'Unknown'
    # Try False first as the standard says that they should be null.
    # True means the file is more likely to be corrupt.
    for pad_non_null in (False, True):
        # 0 - No padding.
        # 4 - More likely to be reliable.
        # 2 - Might work
        for pad_modulo in (0, 4, 2):
            pr_count = 0
            try:
                phys_rec = PhysRec.PhysRecRead(
                    file_path_or_object, file_id, keepGoing=True, pad_modulo=pad_modulo, pad_non_null=pad_non_null
                )
                for _ in phys_rec.genPr():
                    pr_count += 1
                    if pr_limit and pr_count >= pr_limit:
                        break
            except PhysRec.ExceptionPhysRec:
                pass
            else:
                pr_settings = PhysicalRecordSettings(pad_modulo, pad_non_null)
                logging.info(f'Best PR settings: {pr_settings} gives PR count {pr_count}')
                return pr_settings


def file_read_with_best_physical_record_pad_settings(file_path_or_object: typing.Union[str, io.BytesIO],
                                                     file_id=None,
                                                     pr_limit=0) -> typing.Union[None, FileRead]:
    pr_settings = best_physical_record_pad_settings(file_path_or_object, pr_limit)
    if pr_settings is not None:
        return FileRead(file_path_or_object, file_id, True, *pr_settings)
