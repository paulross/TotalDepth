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
"""Indexes LIS files.

Created on 10 Feb 2011

@author: p2ross
"""

#import time
#import sys
import logging

from TotalDepth.LIS import ExceptionTotalDepthLIS
#from TotalDepth.LIS.core import EngVal
from TotalDepth.LIS.core import RepCode
from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import LogPass

class ExceptionFileIndex(ExceptionTotalDepthLIS):
    """Specialisation of exception for the LIS file indexer."""
    pass

__author__  = 'Paul Ross'
__date__    = '2011-02-10'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

class IndexObjBase(object):
    """Base class for indexed objects.
    
    tell - The file position of the Logical Record as an integer.
    
    lrType - The Logical Record type as an integer.
    
    theF - The LIS File object. The file ID is recorded for later error checking."""
    def __init__(self, tell, lrType, theF):
        self._tell = tell
        self._typ = lrType
        self._fileId = theF.fileId
        self._lr = None
        
    def __str__(self):
        return self._strPrefix() + ' ' + self._strSuffix()
        #return 'tell: 0x{:08x} type={:3d} {:s}'.format(self._tell, self._typ, repr(self))

    def _strPrefix(self):
        return 'tell: 0x{:08x} type={:3d}'.format(self._tell, self._typ)

    def _strSuffix(self):
        return '{:s}'.format(repr(self))
    
    def tocStr(self):
        """Returns a 'pretty' string suitable for a table of contents."""
        return 'Type {:d} {:s}'.format(self.lrType, LogiRec.LR_DESCRIPTION_MAP[self.lrType])

    @property
    def tell(self):
        """The file offset of the Logical Record."""
        return self._tell
    
    @property
    def lrType(self):
        """The Logical Record type, in integer."""
        return self._typ
    
    @property
    def logicalRecord(self):
        """The underlying LogiRec object or None."""
        return self._lr
    
    @property
    def isDelimiter(self):
        """True if this represents a delimiter record e.g. File Head/Tail."""
        return LogiRec.isDelimiter(self._typ)
             
    def canAdd(self, iflrType):
        """Returns True if this can accumulate another IFLR."""
        return False

    def iflrType(self):
        """Returns the IFLR type that this EFLR can describe."""
        return -1
    
    def setLogicalRecord(self, theFile):
        """Sets the logicalRecord property to an LogiRec object from theFile."""
        raise NotImplementedError
    
    def _seekFile(self, theFile):
        """Sets theFile to the start of the Logical Record object."""
        theFile.seekLr(self.tell)

    def jsonObject(self):
        """Return an Python object that can be JSON encoded."""
        return {
            'tell' : self._tell,
            'lrtype' : self._typ,
            # 'fileID' : self._fileId,
        }

class IndexNone(IndexObjBase):
    """NULL class just takes the LR information and skips to next LR."""
    def __init__(self, tell, lrType, theF):
        super().__init__(tell, lrType, theF)
        theF.skipToNextLr()

class IndexUnknownInternalFormat(IndexObjBase):
    """Binary verbatim class for things like encrypted records, images, raw table dumps and so on."""
    def __init__(self, tell, lrType, theF):
        assert(lrType in LogiRec.LR_TYPE_UNKNOWN_INTERNAL_FORMAT)
        super().__init__(tell, lrType, theF)
        theF.skipToNextLr()

    def setLogicalRecord(self, theFile):
        """Sets the logicalRecord property to an LogiRec.LrTable() object."""
        if self._lr is None:
            self._seekFile(theFile)
            self._lr = LogiRec.LrMiscRead(theFile)
            theFile.skipToNextLr()

class IndexLrFull(IndexObjBase):
    """Takes a full LR and assigns it to self._lr.
    
    theClass is a cls that is use to instantiate a Logical Record object at the current file position."""
    def __init__(self, tell, lrType, theF, theClass):
        super().__init__(tell, lrType, theF)
        theF.seekCurrentLrStart()
        self._lr = theClass(theF)
        theF.skipToNextLr()

    def setLogicalRecord(self, theFile):
        """Sets the logicalRecord property to an LogiRec object from theFile."""
        # Nothing to do as we have already read this in full
        pass
    
class IndexFileHeadTail(IndexLrFull):
    """Indexes a File header or trailer. The full Logical record is retained."""
    def __init__(self, tell, lrType, theF, theClass):
        super().__init__(tell, lrType, theF, theClass)
        
    def tocStr(self):
        """Returns a 'pretty' string suitable for a table of contents."""
        return '{:s} Name: "{:s}"'.format(super().tocStr(), self._lr.fileName.decode('ascii'))
        
class IndexFileHead(IndexFileHeadTail):
    """Indexes a File header. The full Logical record is retained."""
    def __init__(self, tell, lrType, theF):
        super().__init__(tell, lrType, theF, LogiRec.LrFileHeadRead)
        
class IndexFileTail(IndexFileHeadTail):
    """Indexes a File trailer. The full Logical record is retained."""
    def __init__(self, tell, lrType, theF):
        super().__init__(tell, lrType, theF, LogiRec.LrFileTailRead)
        
class IndexTapeHeadTail(IndexLrFull):
    """Indexes a Tape header or trailer. The full Logical record is retained."""
    def __init__(self, tell, lrType, theF, theClass):
        super().__init__(tell, lrType, theF, theClass)
        
    def tocStr(self):
        """Returns a 'pretty' string suitable for a table of contents."""
        return '{:s} Name: "{:s}"'.format(super().tocStr(), self._lr.name.decode('ascii', 'replace'))
        
class IndexTapeHead(IndexTapeHeadTail):
    """Indexes a Tape header. The full Logical record is retained."""
    def __init__(self, tell, lrType, theF):
        super().__init__(tell, lrType, theF, LogiRec.LrTapeHeadRead)
        
class IndexTapeTail(IndexTapeHeadTail):
    """Indexes a Tape trailer. The full Logical record is retained."""
    def __init__(self, tell, lrType, theF):
        super().__init__(tell, lrType, theF, LogiRec.LrTapeTailRead)
        
class IndexReelHeadTail(IndexLrFull):
    """Indexes a Reel header or trailer. The full Logical record is retained."""
    def __init__(self, tell, lrType, theF, theClass):
        super().__init__(tell, lrType, theF, theClass)
        
    def tocStr(self):
        """Returns a 'pretty' string suitable for a table of contents."""
        return '{:s} Name: "{:s}"'.format(super().tocStr(), self._lr.name.decode('ascii', 'replace'))
        
class IndexReelHead(IndexReelHeadTail):
    """Indexes a Reel header. The full Logical record is retained."""
    def __init__(self, tell, lrType, theF):
        super().__init__(tell, lrType, theF, LogiRec.LrReelHeadRead)
        
class IndexReelTail(IndexReelHeadTail):
    """Indexes a Reel trailer. The full Logical record is retained."""
    def __init__(self, tell, lrType, theF):
        super().__init__(tell, lrType, theF, LogiRec.LrReelTailRead)
        
class IndexTable(IndexObjBase):
    """Table type logical records. Here we capture the first component block so
    that we know the name of the table."""
    def __init__(self, tell, lrType, theF):
        super().__init__(tell, lrType, theF)
        # Now read first component block
        self._cb = LogiRec.CbEngValRead(theF)
        theF.skipToNextLr()
    
    @property
    def name(self):
        """The name of the table from the first component block."""
        return self._cb.value
    
    def __str__(self):
        return self._strPrefix() \
            + ' name={:s} '.format(str(self.name)) \
            + self._strSuffix()

    def tocStr(self):
        """Returns a 'pretty' string suitable for a table of contents."""
        if isinstance(self._cb.value, bytes):
            return 'Type {:d} {:s} "{:s}"'.format(
                self.lrType,
                LogiRec.LR_DESCRIPTION_MAP[self.lrType],
                self._cb.value.decode('ascii'),
                )
        return 'Type {:d} {:s} "{:s}"'.format(
            self.lrType,
            LogiRec.LR_DESCRIPTION_MAP[self.lrType],
            str(self._cb.value),
            )

    def setLogicalRecord(self, theFile):
        """Sets the logicalRecord property to an LogiRec.LrTable() object."""
        if self._lr is None:
            self._seekFile(theFile)
            self._lr = LogiRec.LrTableRead(theFile)
            theFile.skipToNextLr()
    
    def jsonObject(self):
        """Return an Python object that can be JSON encoded."""
        d = super().jsonObject()
        d['tablename'] = repr(self.name)
        return d

class IndexLogPass(IndexObjBase):
    """The index of a Log Pass. This contains a LogPass object.
    
    xAxisIndex is the channel index that is regarded as the X axis.
    This is the indirect axis if present or defaults to channel 0."""
    def __init__(self, tell, lrType, theF, xAxisIndex=0):
        super().__init__(tell, lrType, theF)
        assert(self._typ == LogiRec.LR_TYPE_DATA_FORMAT)
        # Have to rewind for DFSR creation
        theF.seekCurrentLrStart()
        # Create a DFSR and thus a Log Pass
        self._logPass = LogPass.LogPass(LogiRec.LrDFSRRead(theF), self._fileId, xAxisIndex)
        theF.skipToNextLr()
    
    @property
    def logPass(self):
        """The LogPass object."""
        return self._logPass
        
    def __str__(self):
        return str(self._logPass).replace('\n', '\n    ')
        #+ str(self._logPass.rle.xAxisFirst()) + str(self._logPass.rle.xAxisLast())
        
    def tocStr(self):
        """Returns a 'pretty' string suitable for a table of contents."""
        if self._logPass.totalFrames > 0:
            return 'Log Pass: {:d} channels, from {:.3f} to {:.3f} ({:s})'.format(
                len(self._logPass.dfsr.dsbBlocks),
                self._logPass.xAxisFirstValOptical,
                self._logPass.xAxisLastValOptical,
                self._logPass.xAxisUnitsOptical.decode('ascii'),
            )
        return 'Log Pass: {:d} channels, no frames'.format(
            len(self._logPass.dfsr.dsbBlocks),
        )
        
    def canAdd(self, iflrType):
        """Returns the IFLR type that this EFLR can describe."""
        return iflrType == self._logPass.iflrType

    def iflrType(self):
        """Returns the IFLR type that this EFLR can describe."""
        return self._logPass.iflrType

    def add(self, tell, lrType, theF):
        """Add an IFLR."""
        assert(self.canAdd(lrType))
        #print('add()', tell, lrType, theF)
        # Read the nth word of the Logical record and treat this
        # as the X axis value.
        skip = 0
        myRm = self._logPass.dfsr.ebs.recordingMode
        if myRm:
            # Indirect X
            myXrc = self._logPass.dfsr.ebs.depthRepCode
        else:
            # Select Rep Code from the channel
            myXrc = self._logPass.dfsr.dsbBlocks[self._logPass.xAxisIndex].repCode
        if myRm == 0 and self._logPass.xAxisIndex != 0:
            # Have to skip before reading X axis
            skip += theF.skipLrBytes(
                self._logPass.type01Plan.chOffset(
                    frame=0,
                    ch=self._logPass.xAxisIndex,
                )
            )
        myLisSize = RepCode.lisSize(myXrc)
        myXval = RepCode.readBytes(myXrc, theF.readLrBytes(myLisSize))
        skip += myLisSize
        skip += theF.skipToNextLr()
        self._logPass.addType01Data(tell, lrType, skip, myXval)
        
    def jsonObject(self):
        """Return an Python object that can be JSON encoded."""
        d = super().jsonObject()
        d['LogPass'] = self._logPass.jsonObject()
        return d

class PlotRecordSet(object):
    """A POD class that can contain a set of references to the essential (plus
    optional) logical records for plotting."""
    def __init__(self):
        self.clear()
        
    def clear(self):
        # File positions of logical records, the first two are essential, the
        # second two optional.
        self.tellFilm = None
        self.tellPres = None
        self.tellArea = None
        self.tellPip = None
        # A log pass is essential
        self.logPass = None
        # File position(s) of CONS records that can be used for the API header
        self.tellConsS = []
                
    def _strVal(self, v):
        if v is None:
            return 'None'
        return '0x{:x}'.format(v)
    
    def _strValS(self, l):
        if len(l) == 0:
            return 'None'
        return '[{:s}]'.format(', '.join([self._strVal(v) for v in l]))
    
    def __str__(self):
        return 'film={:s} pres={:s} area={:s} pip={:s} cons={:s}\nLogPass={:s}'.format(
            self._strVal(self.tellFilm),
            self._strVal(self.tellPres),
            self._strVal(self.tellArea),
            self._strVal(self.tellPip),
            self._strValS(self.tellConsS),
            str(self.logPass),
        )
    
    def canPlotFromInternalRecords(self):
        """True if I have a valid value that could be yielded, i.e. the minimum
        information from the file that allows a plot. In practice this means a
        FILM, PRES record and a LogPass."""
        return self.tellFilm is not None \
            and self.tellPres is not None \
            and self.logPass is not None
    
    def canPlotFromExternalRecords(self):
        """True if I have a valid value that could be yielded, i.e. the minimum
        information from the file that allows a plot using some external definition
        of what has to be plotted. In practice this means a LogPass."""
        return self.logPass is not None
    
class FileIndex(object):
    """Create an index for the LIS file, theF is a LIS File object.
    
    xAxisIndex is the channel index that is regarded as the X axis (default 0).
    This is currently ignored in the absence of a reasonable use case."""
    def __init__(self, theF, xAxisIndex=0):
        self._fileId = theF.fileId
        self._xAxisIndex = xAxisIndex
        theF.rewind()
        # List of indexable objects that are a IndexObjBase example; an IndexLogPass
        self._idx = []
        # Indexes to log pass objects: {0 : None, 1 : None}
        self._logPassIndexMap = self._resetLogPassIndexMap()
        # Despatch table for LR type
        self._despatchLrType = {
            # The first two should be handled by the LogPass, if not
            # we ignore them as we can't interpret them
            LogiRec.LR_TYPE_NORMAL_DATA         : None,#IndexNone,
            LogiRec.LR_TYPE_ALTERNATE_DATA      : None,#IndexNone,
            LogiRec.LR_TYPE_JOB_ID              : IndexTable,
            LogiRec.LR_TYPE_WELL_DATA           : IndexTable,
            LogiRec.LR_TYPE_TOOL_INFO           : IndexTable,
            LogiRec.LR_TYPE_ENCRYPTED_TABLE     : IndexNone,
            LogiRec.LR_TYPE_TABLE_DUMP          : IndexNone,
            LogiRec.LR_TYPE_DATA_FORMAT         : IndexLogPass,
            LogiRec.LR_TYPE_DATA_DESCRIPTOR     : IndexNone,
            LogiRec.LR_TYPE_TU10_BOOT           : IndexNone,
            LogiRec.LR_TYPE_BOOTSTRAP_LOADER    : IndexNone,
            LogiRec.LR_TYPE_CP_KERNEL           : IndexNone,
            LogiRec.LR_TYPE_PROGRAM_FILE_HEAD   : IndexNone,
            LogiRec.LR_TYPE_PROGRAM_OVER_HEAD   : IndexNone,
            LogiRec.LR_TYPE_PROGRAM_OVER_LOAD   : IndexNone,
            LogiRec.LR_TYPE_FILE_HEAD           : IndexFileHead,
            LogiRec.LR_TYPE_FILE_TAIL           : IndexFileTail,
            LogiRec.LR_TYPE_TAPE_HEAD           : IndexTapeHead,
            LogiRec.LR_TYPE_TAPE_TAIL           : IndexTapeTail,
            LogiRec.LR_TYPE_REEL_HEAD           : IndexReelHead,
            LogiRec.LR_TYPE_REEL_TAIL           : IndexReelTail,
            LogiRec.LR_TYPE_EOF                 : IndexNone,
            LogiRec.LR_TYPE_BOT                 : IndexNone,
            LogiRec.LR_TYPE_EOT                 : IndexNone,
            LogiRec.LR_TYPE_EOM                 : IndexNone,
            LogiRec.LR_TYPE_OPERATOR_INPUT      : IndexUnknownInternalFormat,
            LogiRec.LR_TYPE_OPERATOR_RESPONSE   : IndexUnknownInternalFormat,
            LogiRec.LR_TYPE_SYSTEM_OUTPUT       : IndexUnknownInternalFormat,
            LogiRec.LR_TYPE_FLIC_COMMENT        : IndexUnknownInternalFormat,
            LogiRec.LR_TYPE_BLANK_RECORD        : IndexUnknownInternalFormat,
            LogiRec.LR_TYPE_PICTURE             : IndexUnknownInternalFormat,
            LogiRec.LR_TYPE_IMAGE               : IndexUnknownInternalFormat,
        }
        while not theF.isEOF:
            # Grab the file position
            t = theF.tellLr()
            # Read the LRH
            myBy = theF.readLrBytes(LogiRec.STRUCT_LR_HEAD.size)
            if not myBy:
                break
            lrTy, lrAt = LogiRec.STRUCT_LR_HEAD.unpack(myBy)
            # If this can be handled by a Log Pass then do so
            if lrTy in self._logPassIndexMap:
                if self._logPassIndexMap[lrTy] is not None:
                    # Normal/Alternate data with prior LogPass
                    self._idx[self._logPassIndexMap[lrTy]].add(t, lrTy, theF)
            else:
                # Despatch on lrTy
                fn = self._despatchLrType[lrTy]
                if fn is None:
                    logging.warning('FileIndex.__init__(): Can not handle logical record type {:d}'.format(lrTy))
                else:
                    # TODO: Use self._xAxisIndex
                    self._idx.append(fn(t, lrTy, theF))
                    # Check and fix self._logPassIndexMap
                    if LogiRec.isDelimiter(lrTy):
                        # De-index the LogPass(es)
                        self._logPassIndexMap = self._resetLogPassIndexMap()
                    elif lrTy == LogiRec.LR_TYPE_DATA_FORMAT:
                        # DFSR so update the map to point at the latest index
                        self._logPassIndexMap[self._idx[-1].iflrType()] = len(self._idx)-1

    def longDesc(self):
        """Returns a string that is the long description of this object."""
        return '{!r:s} "{!r:s}" [{:d}]:\n  '.format(
            repr(self), self._fileId, len(self._idx)) \
        + '\n  '.join([str(i) for i in self._idx])

    def __len__(self):
        return len(self._idx)

    def _resetLogPassIndexMap(self):
        return {0 : None, 1 : None}

    @property
    def lrTypeS(self):
        """Returns a list of Logical Record types (integers) that is in the index."""
        return [l.lrType for l in self._idx]
    
    def numLogPasses(self):
        """Returns the number of IndexLogPass objects in the index."""
        r = 0
        for l in self._idx:
            if isinstance(l, IndexLogPass):
                r += 1
        return r
    
    def genLogPasses(self):
        """Yields all IndexLogPass objects in the index."""
        for l in self._idx:
            if isinstance(l, IndexLogPass):
                yield l

    def genPlotRecords(self, fromInternalRecords=True):
        """This provides the minimal information for creating a Plot. It yields
        a PlotRecordSet that has (tell_FILM, tell_PRES, tell_AREA, tell_PIP, IndexLogPass) objects that are not
        separated by delimiter records.
        tell_FILM is the file offset of the FILM record.
        tell_PRES is the file offset of the PRES record.
        tell_AREA is None or the file offset of the AREA record.
        tell_PIP is None or the file offset of the PIP record.
        IndexLogPass is a IndexLogPass object.
        """
        myPlotRecSet = PlotRecordSet()
        # Flag to indicate that some contents of the PlotRecordSet must have
        # changed therefore it must be yielded. Otherwise we keep yielding the
        # same thing on spurious internal records
        prsHasChanged = False
        for iObj in self._idx:
#            print('TRACE: iObj', iObj)
            if iObj.isDelimiter:
                myPlotRecSet.clear()
            elif iObj.lrType == LogiRec.LR_TYPE_WELL_DATA:
                if iObj.name == b'FILM':
                    myPlotRecSet.tellFilm = iObj.tell
                    prsHasChanged = True
                elif iObj.name == b'PRES':
                    myPlotRecSet.tellPres = iObj.tell
                    prsHasChanged = True
                elif iObj.name == b'AREA':
                    myPlotRecSet.tellArea = iObj.tell
                    prsHasChanged = True
                elif iObj.name == b'PIP ':
                    myPlotRecSet.tellPip = iObj.tell
                    prsHasChanged = True
                elif iObj.name == b'CONS':
                    myPlotRecSet.tellConsS.append(iObj.tell)
                    prsHasChanged = True
            elif isinstance(iObj, IndexLogPass):
                myPlotRecSet.logPass = iObj.logPass
                prsHasChanged = True
#            print('TRACE: myPlotRecSet.value()', myPlotRecSet.value())
            if prsHasChanged and (
                    (fromInternalRecords and myPlotRecSet.canPlotFromInternalRecords())
                    or (not fromInternalRecords and myPlotRecSet.canPlotFromExternalRecords())
                ):
                yield myPlotRecSet
                prsHasChanged = False
                # Do not call clear() on the PlotRecord set yet as there might
                # be another DFSR (LogPass) that uses these FILM/PRES tables

    def genAll(self):
        """Generates each index object (child class of IndexObjBase)."""
        for anObj in self._idx:
            yield anObj

    def jsonObject(self):
        """Return an Python object that can be JSON encoded."""
        return {
            'FileID' : self._fileId,
            'LogicalRecords' : [obj.jsonObject() for obj in self._idx],
        }
