#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation.
# Copyright (C) 2011-2021 Paul Ross
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
Created on Jun 14, 2011

@author: paulross
'''
import codecs
import logging
import multiprocessing
import os
import sys
import time
import traceback
import typing as typing
from optparse import OptionParser

import TotalDepth
from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS import ProcLISPath
from TotalDepth.LIS.core import FileIndexer
from TotalDepth.LIS.core import FrameSet
from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import Mnem
from TotalDepth.common import xxd
from TotalDepth.util import XmlWrite, archive, bin_file_type, gnuplot

__author__  = 'Paul Ross'
__date__    = '2020-08-23'
__version__ = '0.2.0'
__rights__  = 'Copyright (c) Paul Ross'


logger = logging.getLogger(__file__)


CSS_CONTENT = """body {
font-size:      12px;
font-family:    arial,helvetica,sans-serif;
margin:         6px;
padding:        6px;
}

h1 {
color:            IndianRed;
font-family:      sans-serif;
font-size:        14pt;
font-weight:      bold;
}

h2 {
color:          IndianRed;
font-family:    sans-serif;
font-size:      14pt;
font-weight:    normal;
}

h3 {
color:          Black;
font-family:    sans-serif;
font-size:      12pt;
font-weight:    bold;
}

h4 {
color:          FireBrick;
font-family:    sans-serif;
font-size:      10pt;
font-weight:    bold;
}

h5 {
color:          FireBrick;
font-family:    sans-serif;
font-size:      10pt;
}

table.filetable {
    border:         2px solid black;
    font-family:    monospace;
    color:          black;
}

th.filetable, td.filetable {
    /* border: 1px solid black; */
    border: 1px;
    border-top-style:solid;
    border-right-style:dotted;
    border-bottom-style:none;
    border-left-style:none;
    vertical-align:top;
    padding: 2px 6px 2px 6px; 
}

table.monospace {
border:            2px solid black;
border-collapse:   collapse;
font-family:       monospace;
color:             black;
}

th.monospace, td.monospace {
border:            1px solid black;
vertical-align:    top;
padding:           2px 6px 2px 6px; 
}

/* Table for well site data. */
table.wsd {
border:            2px solid black;
border-collapse:   collapse;
font-family:        sans-serif;
font-size:          10pt;
color:             black;
}

th.wsd, td.wsd {
border:            1px solid black;
vertical-align:    top;
padding:           2px 6px 2px 6px; 
}

td.wsdNone {
border:            1px solid black;
vertical-align:    top;
padding:           2px 6px 2px 6px; 
color:             red;
}

span.lrFileTell {
    color:          OrangeRed;
    font-family:    monospace;
    /* font-weight:    bold; */
    /* font-style:     italic; */
}

span.lrType {
    color:          blue;
    /* font-family:    monospace; */
    font-weight:    bold;
    /* font-style:     italic; */
}

span.lrDescription {
    color:          green;
    /* font-family:    monospace; */
    /* font-weight:    bold; */
    font-style:     italic;
}
"""

CSS_CONTENT_INDEX = """body {
font-size:      12px;
font-family:    arial,helvetica,sans-serif;
margin:         6px;
padding:        6px;
}

h1 {
color:            IndianRed;
font-family:      sans-serif;
font-size:        14pt;
font-weight:      bold;
}

h2 {
color:          IndianRed;
font-family:    sans-serif;
font-size:      14pt;
font-weight:    normal;
}


table {
    border:         2px solid black;
    /* font-family:    monospace; */
    color:          black;
}

th, td {
    /* border: 1px solid black; */
    border: 1px;
    border-top-style:solid;
    border-right-style:dotted;
    border-bottom-style:none;
    border-left-style:none;
    vertical-align:top;
    padding: 2px 6px 2px 6px; 
}
"""


class FileInfo(typing.NamedTuple):
    pathIn: str
    pathOut: str
    lisSize: int
    numLr: int
    cpuTime: float
    exception: bool

    def __str__(self):
        return 'FileInfo: "%s" -> "%s" %d (kb) LR count=%d t=%.3f' \
            % (self.pathIn, self.pathOut, self.lisSize/1024, self.numLr, self.cpuTime)


class IndexSummary(object):
    CSS_FILE_PATH = 'index.css'

    def __init__(self, f=0, b=0):
        # List of FileInfo objects
        self.file_results: typing.List[FileInfo] = []
        
    def __str__(self):
        return '\n'.join([str(f) for f in self.file_results])
    
    def __iadd__(self, other):
        self.file_results += other.file_results
        return self
    
    def __len__(self):
        return len(self.file_results)
        
    def add(self, fpIn, fpOut, numLr, cpuTime, exception):
        self.file_results.append(FileInfo(fpIn, fpOut, os.path.getsize(fpIn), numLr, cpuTime, exception))

    @property
    def lisSize(self):
        return sum([fi.lisSize for fi in self.file_results])

    @property
    def numLr(self):
        return sum([fi.numLr for fi in self.file_results])

    @property
    def cpuTime(self):
        return sum([fi.cpuTime for fi in self.file_results])

    def writeIndexHTML(self, theOutDir):
        if len(self.file_results) == 0:
            return
        os.makedirs(theOutDir, exist_ok=True)
        # Write CSS
        with open(os.path.join(theOutDir, self.CSS_FILE_PATH), 'w') as f:
            f.write(CSS_CONTENT_INDEX)
        # Now Generate the HTML
        index_html_path = os.path.join(theOutDir, 'index.html')
        logger.info(f'Writing index to {index_html_path}')
        with XmlWrite.XhtmlStream(open(index_html_path, 'w')) as myS:
            with XmlWrite.Element(myS, 'head'):
                with XmlWrite.Element(
                        myS,
                        'link',
                        {
                            'href': self.CSS_FILE_PATH,
                            'type': "text/css",
                            'rel': "stylesheet",
                        }
                ):
                    pass
                with XmlWrite.Element(myS, 'title'):
                    myS.characters('LIS as HTML')
            cmnPrefix = os.path.commonprefix([os.path.normpath(aF.pathIn) for aF in self.file_results])
            lenCmnPrefixFpIn = cmnPrefix.rfind(os.sep)+1
            with XmlWrite.Element(myS, 'body'):
                #
                with XmlWrite.Element(myS, 'table'):
                    with XmlWrite.Element(myS, 'tr', {}):
                        with XmlWrite.Element(myS, 'th'):
                            myS.characters('LIS File')
                        with XmlWrite.Element(myS, 'th'):
                            myS.characters('Size (MB)')
                        with XmlWrite.Element(myS, 'th'):
                            myS.characters('Record Entries')
                        with XmlWrite.Element(myS, 'th'):
                            myS.characters('CPU Time (s)')
                        with XmlWrite.Element(myS, 'th'):
                            myS.characters('Rate (MB/s)')
                    # Body of table
                    for aF in sorted(set(self.file_results)):
                        if not aF.exception:
                            with XmlWrite.Element(myS, 'tr'):
                                with XmlWrite.Element(myS, 'td'):
                                    with XmlWrite.Element(myS, 'a', {'href' : os.path.abspath(aF.pathOut)}):
                                        myS.characters(aF.pathIn[lenCmnPrefixFpIn:])
                                self._writeCols(myS, aF)
                    with XmlWrite.Element(myS, 'tr'):
                        with XmlWrite.Element(myS, 'td'):
                            myS.characters('Totals')
                        self._writeCols(myS, self)

    def _writeCols(self, theS, theObj):
        """Write the columns after the first one. theObj is expected to have certain attributes..."""
        with XmlWrite.Element(theS, 'td', {'align' : 'right'}):
            theS.characters('{:.3f}'.format(theObj.lisSize / 1024**2))
        with XmlWrite.Element(theS, 'td', {'align' : 'right'}):
            theS.characters('{:d}'.format(theObj.numLr))
        with XmlWrite.Element(theS, 'td', {'align' : 'right'}):
            theS.characters('{:.3f}'.format(theObj.cpuTime))
        if theObj.cpuTime != 0:
            with XmlWrite.Element(theS, 'td', {'align' : 'right'}):
                theS.characters('{:.3f}'.format(theObj.lisSize / (theObj.cpuTime * 1024**2)))
        else:
            with XmlWrite.Element(theS, 'td', {'align' : 'right'}):
                theS.characters('N/A')                             


class LisToHtml(ProcLISPath.ProcLISPathBase):
    """Takes an input path, output path and generates HTML file(s) form LIS."""    
    CSS_FILE_PATH = 'TotalDepth.LIS.css'

    def __init__(self, fpIn, fpOut, recursive, keepGoing, accCh=True):
        """Write an HTML page about a LIS file.
        If accChan is True a summary table of the data is written."""
        self.summary = IndexSummary()
        # Despatch table for LR type
        self._despatchLrType = {
            LogiRec.LR_TYPE_JOB_ID              : self._HTMLTable,
            LogiRec.LR_TYPE_WELL_DATA           : self._HTMLTable,
            LogiRec.LR_TYPE_TOOL_INFO           : self._HTMLTable,
            LogiRec.LR_TYPE_DATA_FORMAT         : self._HTMLLogPass,
            LogiRec.LR_TYPE_FILE_HEAD           : self._HTMLFileHead,
            LogiRec.LR_TYPE_FILE_TAIL           : self._HTMLFileTail,
            LogiRec.LR_TYPE_TAPE_HEAD           : self._HTMLTapeHead,
            LogiRec.LR_TYPE_TAPE_TAIL           : self._HTMLTapeTail,
            LogiRec.LR_TYPE_REEL_HEAD           : self._HTMLReelHead,
            LogiRec.LR_TYPE_REEL_TAIL           : self._HTMLReelTail,
            LogiRec.LR_TYPE_OPERATOR_INPUT      : self._HTMLVerbatim,  # Operator command inputs
            LogiRec.LR_TYPE_OPERATOR_RESPONSE   : self._HTMLVerbatim,  # Operator response inputs
            LogiRec.LR_TYPE_SYSTEM_OUTPUT       : self._HTMLVerbatim,  # System outputs to operator
            LogiRec.LR_TYPE_FLIC_COMMENT        : self._HTMLVerbatim,  # FLIC comment
            LogiRec.LR_TYPE_BLANK_RECORD        : self._HTMLVerbatim,  # Blank record/CSU comment

        }
        self._accCh = accCh
        super().__init__(fpIn, fpOut, recursive, keepGoing)
        
    def _retIndentDepth(self, theIe):
        if theIe.lrType == LogiRec.LR_TYPE_FILE_HEAD:
            return 2
        elif theIe.lrType == LogiRec.LR_TYPE_FILE_TAIL:
            return 2
        elif theIe.lrType == LogiRec.LR_TYPE_TAPE_HEAD:
            return 1
        elif theIe.lrType == LogiRec.LR_TYPE_TAPE_TAIL:
            return 1
        elif theIe.lrType == LogiRec.LR_TYPE_REEL_HEAD:
            return 0
        elif theIe.lrType == LogiRec.LR_TYPE_REEL_TAIL:
            return 0
        return 3
    
    def _writeHtmlToc(self, myFi, myIdx, theS):
        """Write the table of contents at the top of the page."""
        with XmlWrite.Element(theS, 'a', {'name' : 'toc'}):
            pass
        with XmlWrite.Element(theS, 'h1', {}):
            theS.characters('Logical records in {:s}'.format(myFi.fileId))
        for anIdx in myIdx.genAll():
            with XmlWrite.Element(theS, 'p', {}):
                theS.literal('&nbsp;' * 8 * self._retIndentDepth(anIdx))
                with XmlWrite.Element(theS, 'a', {'href' : '#{:d}'.format(anIdx.tell)}):
                    theS.characters(anIdx.tocStr())
#                    theS.characters('{:s}'.format(anIdx))

            
    def _HTMLEntryBasic(self, theIe, theS):
        """Writes the basic entry for the index entry (we treat it as an
        IndexObjBase). This includes the anchor."""
        with XmlWrite.Element(theS, 'hr'):
            pass
        with XmlWrite.Element(theS, 'a', {'name' : '{:d}'.format(theIe.tell)}):
            pass
        with XmlWrite.Element(theS, 'p', {}):
            with XmlWrite.Element(theS, 'span', {'class' : 'lrFileTell'}):
                theS.characters('0x{:x}'.format(theIe.tell))
            theS.literal('&nbsp;')
            with XmlWrite.Element(theS, 'span', {'class' : 'lrType'}):
                theS.characters('Logical Record type {:d}'.format(theIe.lrType))
            theS.literal('&nbsp;')
            with XmlWrite.Element(theS, 'span', {'class' : 'lrDescription'}):
                theS.characters(LogiRec.LR_DESCRIPTION_MAP[theIe.lrType])
            with XmlWrite.Element(theS, 'br'):
                pass

    def _HTMLLinkToTop(self, theS):
        with XmlWrite.Element(theS, 'p', {}):
            with XmlWrite.Element(theS, 'a', {'href' : '#top'}):
                theS.characters('To top')

    def _HTMLNonSpecific(self, theIe, theFi, theS):
        self._HTMLEntryBasic(theIe, theS)
        if  theIe.logicalRecord is None:
            theIe.setLogicalRecord(theFi)
        logical_record: LogiRec.LrUnkownRead = theIe.logicalRecord
        assert logical_record is not None
        with XmlWrite.Element(theS, 'p'):
            theS.characters('Verbatim bytes [{:d}]:'.format(len(logical_record.bytes)))
        with XmlWrite.Element(theS, 'pre', {'class': 'verbatim'}):
            theS.characters(xxd.xxd(logical_record.bytes, columns=32))
        self._HTMLLinkToTop(theS)

    def _HTMLVerbatim(self, theIe, theFi, theS):
        self._HTMLEntryBasic(theIe, theS)
        theIe.setLogicalRecord(theFi)
        myLr = theIe.logicalRecord
        assert(myLr is not None)
        with XmlWrite.Element(theS, 'p'):
            theS.characters('Verbatim bytes [{:d}]:'.format(len(myLr.bytes)))
        with XmlWrite.Element(theS, 'pre', {'class' : 'verbatim'}):
            theS.characters(myLr.bytes.decode('ascii', 'replace'))
        with XmlWrite.Element(theS, 'p'):
            theS.characters('EBCDIC -> ASCII:')
        # Often old LIS files have EBCDIC data as they may have been processed on an IBM mainframe.
        with XmlWrite.Element(theS, 'pre', {'class' : 'verbatim'}):
            ascii = codecs.decode(myLr.bytes, 'cp500')
            theS.characters(ascii)

    def _HTMLTable(self, theIe, theFi, theS):
        self._HTMLEntryBasic(theIe, theS)
        if theIe.logicalRecord is None:
            theIe.setLogicalRecord(theFi)
        myLr = theIe.logicalRecord
        assert(myLr is not None)
        if myLr.tableCbEv is not None:
            # Write the table name and so on from tableCbEv
            with XmlWrite.Element(theS, 'h4', {'class': 'wsd'}):
                theS.characters('Well site data table: {:s}'.format(myLr.tableCbEv.engVal.pStr()))
                # theS.characters('Table: {:s}'.format(str(myLr.tableCbEv.engVal)))
        with XmlWrite.Element(theS, 'table', {'class': 'wsd'}):
            if myLr.isSingleParam:
                with XmlWrite.Element(theS, 'tr', {}):
                    with XmlWrite.Element(theS, 'th', {'class': 'wsd'}):
                        theS.characters('MNEM')
                    with XmlWrite.Element(theS, 'th', {'class': 'wsd'}):
                        theS.characters('VALUE')
                for aRow in myLr.genRows():
                    if len(aRow) == 1:
                        with XmlWrite.Element(theS, 'tr', {}):
                            with XmlWrite.Element(theS, 'td', {'class': 'wsd'}):
                                theS.characters(aRow[0].mnem.decode('ascii'))
                            with XmlWrite.Element(theS, 'td', {'class': 'wsd'}):
                                theS.characters(aRow[0].engVal.pStr())
                    else:
                        logger.warning('Single Parameter Information Record has row length {:d}'.format(len(aRow)))
            else:
                with XmlWrite.Element(theS, 'tr', {}):
                    for aMnem in myLr.colLabels():
                        with XmlWrite.Element(theS, 'th', {'class': 'wsd'}):
                            theS.characters(aMnem.decode('ascii'))
                for aRowName in myLr.genRowNames(sort=1):
                    with XmlWrite.Element(theS, 'tr', {}):
                        for aCell in myLr.genRowValuesInColOrder(aRowName):
                            if aCell is None:
                                with XmlWrite.Element(theS, 'td', {'class': 'wsdNone'}):
                                    theS.characters('N/A')
                            elif aCell.engVal is None:
                                # TODO: This is slightly suspicious, it seems to happen with
                                # the last cell in the table where there is no EngVal.
                                with XmlWrite.Element(theS, 'td', {'class': 'wsdNone'}):
                                    theS.characters('No value')
                            else:
                                with XmlWrite.Element(theS, 'td', {'class': 'wsd'}):
                                    theS.characters('{:s}'.format(aCell.engVal.pStr()))
        self._HTMLLinkToTop(theS)
    
    def _HTMLKeyValTable(self, theS, theKv, fieldTitle='Field'):
        with XmlWrite.Element(theS, 'table', {'class' : "monospace"}):
            with XmlWrite.Element(theS, 'tr', {}):
                with XmlWrite.Element(theS, 'th', {'class' : "monospace"}):
                    theS.characters(fieldTitle)
                with XmlWrite.Element(theS, 'th', {'class' : "monospace"}):
                    theS.characters('Value')
            for k, v in theKv:
                with XmlWrite.Element(theS, 'tr', {}):
                    with XmlWrite.Element(theS, 'td', {'class' : "monospace"}):
                        theS.characters(k)
                    with XmlWrite.Element(theS, 'td', {'class' : "monospace"}):
                        theS.characters(v)        
        
    def _HTMLGeneralTable(self, theS, theTitleS, theTab):
        """Create a table. theTitleS is a list of titles, theTab is a list of lists."""
        with XmlWrite.Element(theS, 'table', {'class' : "monospace"}):
            with XmlWrite.Element(theS, 'tr', {}):
                for v in theTitleS:
                    with XmlWrite.Element(theS, 'th', {'class' : "monospace"}):
                        theS.characters(v)
            for row in theTab:
                with XmlWrite.Element(theS, 'tr', {}):
                    for v in row:
                        with XmlWrite.Element(theS, 'td', {'class' : "monospace"}):
                            theS.characters(v)
        
    def _retFileHeadTailKeyVal(self, theIe):
        myLr = theIe.logicalRecord
        assert(myLr is not None)
        return [
            ('File Name',                   myLr.fileName.decode('ascii', 'replace')),
            ('Service sub-level',           myLr.serviceSubLevel.decode('ascii', 'replace')),
            ('Version',                     myLr.version.decode('ascii', 'replace')),
            ('Date (yy/mm/dd)',             myLr.date.decode('ascii', 'replace')),
            ('Max Physical Record Length',  myLr.maxPrLength.decode('ascii', 'replace')),
            ('File type',                   myLr.fileType.decode('ascii', 'replace')),
        ]
        
    def _HTMLFileHead(self, theIe, theFi, theS):
        self._HTMLEntryBasic(theIe, theS)
        myKv = self._retFileHeadTailKeyVal(theIe)
        myKv.append(('Previous file name', theIe.logicalRecord.prevFileName.decode('ascii', 'replace')))
        self._HTMLKeyValTable(theS, myKv)
        self._HTMLLinkToTop(theS)
        
    def _HTMLFileTail(self, theIe, theFi, theS):
        self._HTMLEntryBasic(theIe, theS)
        myKv = self._retFileHeadTailKeyVal(theIe)
        myKv.append(('Next file name', theIe.logicalRecord.nextFileName.decode('ascii', 'replace')))
        self._HTMLKeyValTable(theS, myKv)
        self._HTMLLinkToTop(theS)

    def _retReelTapeHeadTailKeyVal(self, logical_record: LogiRec.LrReelTapeHeadTail):
        assert (logical_record is not None)
        return [
            ('Service Name',        logical_record.serviceName.decode('ascii', 'replace')),
            ('Date (yy/mm/dd)',     logical_record.date.decode('ascii', 'replace')),
            ('Origin',              logical_record.origin.decode('ascii', 'replace')),
            ('Name',                logical_record.name.decode('ascii', 'replace')),
            ('Continuation Number', logical_record.contNumber.decode('ascii', 'replace')),
            ('Comments',            logical_record.comments.decode('ascii', 'replace')),
        ]

    def _HTMLTapeHead(self, theIe, theFi, theS):
        self._HTMLEntryBasic(theIe, theS)
        logical_record: LogiRec.LrTapeHead = theIe.logicalRecord
        myKv = self._retReelTapeHeadTailKeyVal(logical_record)
        myKv.append(('Previous tape name', logical_record.prevTapeName.decode('ascii', 'replace')))
        self._HTMLKeyValTable(theS, myKv)
        self._HTMLLinkToTop(theS)

    def _HTMLTapeTail(self, theIe, theFi, theS):
        self._HTMLEntryBasic(theIe, theS)
        logical_record: LogiRec.LrTapeTail = theIe.logicalRecord
        myKv = self._retReelTapeHeadTailKeyVal(logical_record)
        myKv.append(('Next tape name', logical_record.nextTapeName.decode('ascii', 'replace')))
        self._HTMLKeyValTable(theS, myKv)
        self._HTMLLinkToTop(theS)

    def _HTMLReelHead(self, theIe, theFi, theS):
        self._HTMLEntryBasic(theIe, theS)
        logical_record: LogiRec.LrReelHead = theIe.logicalRecord
        myKv = self._retReelTapeHeadTailKeyVal(logical_record)
        myKv.append(('Previous reel name', logical_record.prevReelName.decode('ascii', 'replace')))
        self._HTMLKeyValTable(theS, myKv)
        self._HTMLLinkToTop(theS)

    def _HTMLReelTail(self, theIe, theFi, theS):
        self._HTMLEntryBasic(theIe, theS)
        logical_record: LogiRec.LrReelTail = theIe.logicalRecord
        myKv = self._retReelTapeHeadTailKeyVal(logical_record)
        myKv.append(('Next reel name', logical_record.nextReelName.decode('ascii', 'replace')))
        self._HTMLKeyValTable(theS, myKv)
        self._HTMLLinkToTop(theS)

    def _HTMLLogPass(self, theIe, theFi, theS):
        assert(isinstance(theIe, FileIndexer.IndexLogPass))
        with XmlWrite.Element(theS, 'hr'):
            pass
        with XmlWrite.Element(theS, 'a', {'name' : '{:d}'.format(theIe.tell)}):
            pass
#        with XmlWrite.Element(theS, 'p', {}):
#            with XmlWrite.Element(theS, 'span', {'class' : 'lrFileTell'}):
#                theS.characters('0x{:x}'.format(theIe.tell))
        with XmlWrite.Element(theS, 'h4', {}):
            theS.characters('Log Pass at 0x{:x}'.format(theIe.tell))
        myLp = theIe.logPass
#        with XmlWrite.Element(theS, 'pre', {}):
#            theS.characters(myLp.longStr())
        # Table of frame information
        with XmlWrite.Element(theS, 'h5', {}):
            theS.characters('Frame Information')
        if isinstance(myLp.dfsr.ebs.absentValue, bytes):
            absent_value = float(myLp.dfsr.ebs.absentValue)
        else:
            absent_value = myLp.dfsr.ebs.absentValue
        myFrInfo = [
            # A tad messy here as some (computed) information is easier to get
            # from the type01Plan and some is easier to get directly from the DFSR.
            # First from the type01Plan
            ('Frame length',            '{:d} bytes'.format(myLp.type01Plan.frameSize)),
            ('Number of Channels',      '{:d}'.format(myLp.type01Plan.numChannels)),
            ('Indirect X size',         '{:d} bytes'.format(myLp.type01Plan.indirectSize)),
            # From DFSR entry block set
            ('Up/Down',                 '{:g}'.format(myLp.dfsr.ebs.upDown)),
            ('Absent Value',            '{:g}'.format(absent_value)),
        ]
        if myLp.dfsr.ebs.frameSpacing is not None:
            myFrInfo.append(('Declared frame spacing',  '{:g} [{!r:s}]'.format(myLp.dfsr.ebs.frameSpacing,
                                                                               myLp.dfsr.ebs.frameSpacingUnits)))
        else:
            myFrInfo.append(('Declared frame spacing',  'None [{!r:s}]'.format(myLp.dfsr.ebs.frameSpacingUnits)))
        myFrInfo.extend(
            [
                ('Recording mode',           '{:g}'.format(myLp.dfsr.ebs.recordingMode)),
                ('X axis units',             '{!r:s}'.format(myLp.dfsr.ebs.depthUnits)),
                ('X axis Rep Code',          '{:g}'.format(myLp.dfsr.ebs.depthRepCode)),
            ]
        )
        self._HTMLKeyValTable(theS, myFrInfo, fieldTitle='Measure')
        # Now the channels and their units as a string
        with XmlWrite.Element(theS, 'h5', {}):
            theS.characters('Channels')
        myChUomS = [
            (
                Mnem.Mnem(db.mnem).pStr(strip=True),
                Mnem.Mnem(db.units).pStr(strip=True),
            )
            for db in myLp.dfsr.dsbBlocks
        ]
        myChS = []
        for m, u in myChUomS:
            if u == '':
                myChS.append(m)
            else:
                myChS.append('{:s} ({:s})'.format(m, u))
        with XmlWrite.Element(theS, 'p', {}):
            theS.characters(', '.join(myChS))
        # Write the channels as a table
        myChUomS = [
            (
                Mnem.Mnem(db.mnem).pStr(strip=True),
                db.servId.decode('ascii'),
                db.servOrd.decode('ascii'),
                Mnem.Mnem(db.units).pStr(strip=True),
                '{:02d}-{:03d}-{:02d}-{:d}'.format(db.apiLogType, db.apiCurveType, db.apiCurveClass, db.apiModifier),
                '{:d}'.format(db.fileNumber),
                '{:d}'.format(db.size),
                '{:d}'.format(db.repCode),
                '{:d}'.format(db.subChannels),
                '{:d}'.format(db.values()),
                # Minor kludge to remove '[' and ']' from ends of string
                '{:s}'.format(str([(sc, db.samples(sc), db.bursts(sc)) for sc in range(db.subChannels)])[1:-1]),
            )
            for db in myLp.dfsr.dsbBlocks
        ]
        self._HTMLGeneralTable(
            theS,
            [
                'Name',
                'Service ID',
                'Service Order',
                'Units',
                'API',
                'File',
                'Size',
                'Rep Code',
                'Sub-channels',
                'Values per frame',
                'Shape [sc, sa, bu]'
            ],
            myChUomS
        )
        # Table of Xaxis information
        with XmlWrite.Element(theS, 'h5', {}):
            theS.characters('X Axis Information')
        if myLp.totalFrames > 0:
            myOptUnitStr = Mnem.Mnem(myLp.xAxisUnitsOptical).pStr(strip=True)
            if myLp.rle.xAxisLastFrame() is not None:
                last_x_optical = f'{myLp.xAxisLastValOptical:.3f}'
                interval = f'{myLp.xAxisLastValOptical - myLp.xAxisFirstValOptical:.3f}'
                spacing_optical = f'{myLp.xAxisSpacingOptical:.3f}'
            else:
                last_x_optical = 'None'
                interval = 'None'
                spacing_optical = 'None'
            myFrInfo = [
                ('From',    '{:.3f} ({:s})'.format(myLp.xAxisFirstValOptical, myOptUnitStr)),
                ('To',    '{} ({:s})'.format(last_x_optical, myOptUnitStr)),
                ('Interval',    '{} ({:s})'.format(interval, myOptUnitStr)),
                ('Total number of frames',    '{:d}'.format(myLp.rle.totalFrames())),
                ('Overall frame spacing',    '{} ({:s})'.format(spacing_optical, myOptUnitStr)),
                ('Original recording units',    '{!r:s}'.format(myLp.xAxisUnits)),
            ]
            self._HTMLKeyValTable(theS, myFrInfo, fieldTitle='')
        else:
            with XmlWrite.Element(theS, 'p', {}):
                theS.characters('No frames')
        if self._accCh and theIe.logPass.totalFrames > 0:
            with XmlWrite.Element(theS, 'h5', {}):
                theS.characters('Frame Data')
            # Accumulate the channel data then write it out
            theIe.logPass.setFrameSet(theFi, None, None)
            myFrSet = theIe.logPass.frameSet
#            # Print the channels and units
#            hdrS = []
#            if myFrSet.isIndirectX:
#                hdrS.append('XAXIS [{:s}]'.format(myFrSet.xAxisDecl.depthUnits))
#            hdrS.extend(['{:s} [{:s}]'.format(m, u) for m,u in theIe.logPass.genFrameSetHeadings()])
#            #print('TRACE: len(hdrS)', len(hdrS))
#            print('\t'.join(hdrS))
#            for frIdx in range(myFrSet.numFrames):
#                #print('TRACE: len(frame)', len(myFrSet.frame(frIdx)))
#                if myFrSet.isIndirectX:
#                    print(myFrSet.xAxisValue(frIdx), '\t', end='')
#                print('\t'.join([str(v) for v in myFrSet.frame(frIdx)]))
            # Accumulate min/mean/max
            schNameS = list(theIe.logPass.genFrameSetScNameUnit())
            myAcc = myFrSet.accumulate(
                [
                    FrameSet.AccCount,
                    FrameSet.AccMin,
                    FrameSet.AccMean,
                    FrameSet.AccMax,
                    FrameSet.AccStDev,
                    FrameSet.AccDec,
                    FrameSet.AccEq,
                    FrameSet.AccInc,
                ]
            )
#            print()
#            print('Sc Name     Count     Min      Mean     Max     StdDev')
#            for scIdx, aRow in enumerate(myAcc):
#                print('{:s} [{:s}]'.format(*schNameS[scIdx]),
#                      '  ',
#                      '  '.join(['{:7g}'.format(v) for v in aRow]))
            myTable = []
            for scIdx, aRow in enumerate(myAcc):
                myTable.append([str(x) for x in schNameS[scIdx]] + ['{:7g}'.format(v) for v in aRow])
            self._HTMLGeneralTable(
                theS,
                ['Sc Name', 'Units', 'Count', 'Min', 'Mean', 'Max', 'StdDev', '--', '==', '++'],
                myTable,
            )
        self._HTMLLinkToTop(theS)
    
    def _writeCss(self, fpOut):
        """Writes the CSS file if it is not already there."""
        cssFp = os.path.join(os.path.dirname(fpOut), self.CSS_FILE_PATH)
#        if not os.path.exists(cssFp):
#            with open(cssFp, 'w') as f:
#                f.write(CSS_CONTENT)
        with open(cssFp, 'w') as f:
            f.write(CSS_CONTENT)

    def processFile(self, fpIn, fpOut):
        assert (os.path.isfile(fpIn))
        assert (os.path.exists(os.path.dirname(fpOut)))
        clkStart = time.perf_counter()
        try:
            myFile, myIndex = self._retLisFileAndIndex(fpIn)
        except ExceptionTotalDepthLIS as err:
            # logger.error('Can not create file and index: {!r:s}'.format(err))
            logger.exception('Can not create file and index from {}'.format(fpIn))
            self.summary.add(fpIn, fpOut, 0, time.perf_counter() - clkStart, True)
            return
        # Write the CSS is not already there
        self._writeCss(fpOut)
        numEntries = 0
        # Now Generate the HTML
        with XmlWrite.XhtmlStream(open(fpOut, 'w')) as myS:
            with XmlWrite.Element(myS, 'head'):
                with XmlWrite.Element(
                        myS,
                        'link',
                        {
                            'href': self.CSS_FILE_PATH,
                            'type': "text/css",
                            'rel': "stylesheet",
                        }
                ):
                    pass
                with XmlWrite.Element(myS, 'title'):
                    myS.characters('LIS analysis of %s' % fpIn)
            with XmlWrite.Element(myS, 'body'):
                with XmlWrite.Element(myS, 'a', {'name': 'top'}):
                    pass
                self._writeHtmlToc(myFile, myIndex, myS)
                for anIe in myIndex.genAll():
                    if anIe.lrType in self._despatchLrType:
                        self._despatchLrType[anIe.lrType](anIe, myFile, myS)
                    else:
                        self._HTMLNonSpecific(anIe, myFile, myS)
                    numEntries += 1
                with XmlWrite.Element(myS, 'hr'):
                    pass
                with XmlWrite.Element(myS, 'p', {'class': 'copyright'}):
                    myS.characters(
                        'Produced by LisToHtml version: {:s}, date: {:s}, rights: "{:s}" CPU time: {:.3f} (s)'.format(
                            __version__,
                            __date__,
                            __rights__,
                            time.perf_counter() - clkStart,
                        )
                    )
        # Update the counter
        self.summary.add(fpIn, fpOut, numEntries, time.perf_counter() - clkStart, False)
                

def processFile(fpIn, fpOut, keepGoing) -> IndexSummary:
    """Used by the multiprocessing code."""
    logger.info(f'processFile(): {fpIn} -> {fpOut}')
    if not os.path.exists(os.path.dirname(fpOut)):
        try:
            os.makedirs(os.path.dirname(fpOut))
        except OSError:
            # TODO: Check specifically for: OSError: [Errno 17] File exists: '...'
            pass
    file_type = bin_file_type.binary_file_type_from_path(fpIn)
    logger.info(f'File type: "{file_type}"')
    if bin_file_type.is_lis_file_type(file_type):
        try:
            myPlp = LisToHtml(fpIn, fpOut+'.html', recursive=False, keepGoing=keepGoing)
        except ExceptionTotalDepthLIS as err:
            logger.error('LisToHtml.processFile({:s}): {:s}'.format(fpIn, str(err)))
            logger.error(traceback.format_exc())
        except Exception as err:
            if keepGoing:
                # Log it, return None
                logger.critical('LisToHtml.processFile({:s}): {:s}'.format(fpIn, str(err)))
                logger.critical(traceback.format_exc())
            else:
                # Raise it
                raise
        else:
            return myPlp.summary

GNUPLOT_PLT = """set logscale x
set grid
set title "Reading LIS Files and Writing HTML."
# set mxtics 5
set xrange [100:1e8]
set xlabel "LIS File Size (bytes)"
# set xtics
# set format x ""

set logscale y
set ylabel "Process Time (s)"
set ytics nomirror out
# set yrange [1:1e5]
# set ytics 20
# set mytics 2
# set ytics 8,35,3

set logscale y2
set y2label "Process Rate (ms/Mb)"
# set y2range [1e-4:10]
#set my2tics
set y2tics out

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

set terminal svg size 1000,700 # choose the file format
set output "{name}_times.svg" # choose the output device

plot "{name}.dat" using 1:2 axes x1y1 title "HTML Write Time (s), left axis" lt 1 w points, \\
    "{name}.dat" using 1:($2*1000/($1/(1024*1024))) axes x1y2 title "Write HTML Rate (ms/Mb), right axis" lt 2 w points

reset
"""


def plot_gnuplot(data: IndexSummary, gnuplot_dir: str) -> None:
    # First row is header row, create it then comment out the first item.
    table = [
        ['size_input', 'time', 'Path']
    ]
    table[0][0] = f'# {table[0][0]}'
    for file_info in sorted(data.file_results):
        if file_info.lisSize > 0 and not file_info.exception:
            # table.append(list(data[k]) + [k])
            table.append(
                [
                    file_info.lisSize,
                    file_info.cpuTime,
                    file_info.pathIn
                ]
            )
    name = 'LisToHTML'
    return_code = gnuplot.invoke_gnuplot(gnuplot_dir, name, table, GNUPLOT_PLT.format(name=name))
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')
    return_code = gnuplot.write_test_file(gnuplot_dir, 'svg')
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')


def main():
    description = """usage: %prog [options] in out
Generates HTML from input LIS file or directory to an output destination."""
    print ('Cmd: %s' % ' '.join(sys.argv))
    parser = TotalDepth.common.cmn_cmd_opts.path_in_out_required(
        description, prog='TotalDepth.LIS.LisToHTML.main', version=__version__, epilog=__rights__
    )
    TotalDepth.common.cmn_cmd_opts.add_log_level(parser, level=20)
    TotalDepth.common.cmn_cmd_opts.add_multiprocessing(parser)
    # TotalDepth.common.Slice.add_frame_slice_to_argument_parser(parser, use_what=True)
    TotalDepth.common.process.add_process_logger_to_argument_parser(parser)
    gnuplot.add_gnuplot_to_argument_parser(parser)
    parser.add_argument("-g", "--glob", action="store_true", dest="glob", default=None,
                        help="File match pattern. Default: %(default)s.")
    args = parser.parse_args()
    # print(args)
    TotalDepth.common.cmn_cmd_opts.set_log_level(args)

    clkStart = time.perf_counter()
    timStart = time.time()
    # Your code here
    if TotalDepth.common.cmn_cmd_opts.multiprocessing_requested(args):
        myResult = ProcLISPath.procLISPathMP(
            args.path_in,
            args.path_out,
            args.glob,
            args.recurse,
            args.keepGoing,
            TotalDepth.common.cmn_cmd_opts.number_multiprocessing_jobs(args),
            processFile,
            resultObj=IndexSummary(),
        )
        # Write index.html
        myResult.writeIndexHTML(args.path_out)
    else:
        if os.path.isdir(args.path_in):
            myResult = ProcLISPath.procLISPathSP(
                args.path_in,
                args.path_out,
                args.glob,
                args.recurse,
                args.keepGoing,
                processFile,
                resultObj=IndexSummary(),
            )
            # Write index.html
            myResult.writeIndexHTML(args.path_out)
        else:
            myLth = LisToHtml(args.path_in, args.path_out, args.recurse, args.keepGoing)
            myResult = myLth.summary
    print('LisToHtml results:')
    print(
        f'{"LIS_Size":>16}'
        f' {"Num_LRs":>8}'
        f' {"CPU_s":>12}'
        f' {"ms/Mb":>12}'
        f' {"Fail?":>5}'
        f' {"Path"}'
    )
    total_lis_size = 0
    total_cpu_time = 0.0
    files_exception = 0
    for file_info in myResult.file_results:
        if file_info.lisSize:
            ms_mb = (file_info.cpuTime * 1000) / (file_info.lisSize / 1024**2)
        else:
            ms_mb = 0.0
        print(
            f'{file_info.lisSize:16d}'
            f' {file_info.numLr:8d}'
            f' {file_info.cpuTime:12.3f}'
            f' {ms_mb:12.3f}'
            f' {file_info.exception!r:5}'
            f' {file_info.pathIn}'
        )
        total_lis_size += file_info.lisSize
        total_cpu_time += file_info.cpuTime
        if file_info.exception:
            files_exception += 1
    if args.gnuplot:
        try:
            plot_gnuplot(myResult, args.gnuplot)
        except IOError:
            logger.exception('Plotting with gnuplot failed.')
    if total_lis_size:
        ms_mb = (total_cpu_time * 1000) / (total_lis_size / 1024 ** 2)
    else:
        ms_mb = 0.0
    print(
        f'Files processed {len(myResult.file_results)}'
        f' failed: {files_exception}'
        f' total LIS size: {total_lis_size:,d}'
        f' total CPU time: {total_cpu_time:.3f} (s)'
        f' {ms_mb:.1f} (ms/Mb)'
    )
    print('  CPU time = %8.3f (S)' % (time.perf_counter() - clkStart))
    print('Exec. time = %8.3f (S)' % (time.time() - timStart))
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
