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
"""
Created on Jan 24, 2012

@author: p2ross
"""
__author__  = 'Paul Ross'
__date__    = '2012-01-24'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

import time
import sys
import os
import logging
import multiprocessing
import collections
import traceback
#from optparse import OptionParser

# LIS support
from TotalDepth.LIS import ExceptionTotalDepthLIS
import TotalDepth.LIS.core.File
#import TotalDepth.LIS.core.Mnem
import TotalDepth.LIS.core.LogiRec
import TotalDepth.LIS.core.FileIndexer
import TotalDepth.LIS.core.Units
# LAS support
from TotalDepth.LAS import ExceptionTotalDepthLAS
import TotalDepth.LAS.core.LASRead
# Utilities - plotting
from TotalDepth.util.plot import Plot
from TotalDepth.util.plot import FILMCfgXML
#from TotalDepth.util.plot import PRESCfgXML
from TotalDepth.util.plot import XMLMatches
# Utilities - general
from TotalDepth.util import DictTree
from TotalDepth.util import DirWalk
from TotalDepth.util import XmlWrite
from TotalDepth.common import cmn_cmd_opts

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

# The field names are not (yet) used.
IndexTableValue = collections.namedtuple('IndexTableValue', 'scale evFirst evLast evInterval curves numPoints outPath')

class PlotLogInfo(object):
    """Class that collates information about the results of plotting log passes.
    This can, for example, write out an index.html page with links to SVG pages."""
    CSS_FILE_PATH = 'index.css'
    def __init__(self):
        # So here the essential data that we have to put in the index.html is:
        # A list of tuples of:
        # (theInPath, theLpIdx, theFilmID, IndexTableValue(theScale, theEvFirst, theEvLast, evInterval, theCurveS, theOutPath))
        # as: (str,     int,       str,    IndexTableValue(number,    EngVal,     EngVal,  [str, ...], str))
        self._plotS = []
        self._lisBytes = 0
        self.lisFileCntr = 0
        self.lasFileCntr = 0
        self.logPassCntr = 0
        self.plotCntr = 0
        self.curvePoints = 0
        # List of EngVal objects that accumulate the number of 'curve feet'
        self._intervalCntrS = []
        
    @property
    def intervals(self):
        return self._intervalCntrS
        
    def __str__(self):
        retL = ['PlotLogInfo {:s} Files={:d} Bytes={:d} LogPasses={:d} Plots={:d} Curve points={:d}'.format(
                repr(self),
                self.lisFileCntr+self.lasFileCntr,
                self._lisBytes,
                self.logPassCntr,
                self.plotCntr,
                self.curvePoints
            )
        ]
        for l in sorted(self._plotS):
            retL.append('{:s}'.format(str(l)))
        for anEv in self._intervalCntrS:
            retL.append('Interval*curves: {:s}'.format(anEv.newEngValInOpticalUnits().strFormat('{:.3f}')))
        return '\n'.join(retL)
        
    def __iadd__(self, other):
        self._plotS += other._plotS
        self._lisBytes += other._lisBytes
        self.lisFileCntr += other.lisFileCntr
        self.lasFileCntr += other.lasFileCntr
        self.logPassCntr += other.logPassCntr
        self.plotCntr += other.plotCntr
        self.curvePoints += other.curvePoints
        for anI in other.intervals:
            self._addInterval(anI)
        return self
    
    def addPlotResult(self, theInPath, theOutPath, theLpIdx, theFilmID, theScale, theEvFirst, theEvLast, theCurveS, ptsPlotted):
        """Adds a successful plot.
        theInPath - The file path to the input file.
        theOutPath - The file path to the output file.
        theLpIdx - Integer index of the LogPass in the input file.
        theFilmID - The FILM ID as a Mnem.
        theScale - Plot scale as an number.
        theEvFirst - The first X axis as an EngVal.
        theEvLast - The last X axis as an EngVal.
        theCurveS - A list of Mnem of the curves plotted.
        ptsPlotted - Number of points plotted.
        """
        myInterval = theEvLast - theEvFirst
        self._plotS.append(
            (
                theInPath,
                theLpIdx,
                theFilmID,
                IndexTableValue(
                    theScale,
                    theEvFirst.newEngValInOpticalUnits().strFormat('{:.1f}', incPrefix=False),
                    theEvLast.newEngValInOpticalUnits().strFormat('{:.1f}', incPrefix=False),
                    myInterval.newEngValInOpticalUnits().strFormat('{:.1f}', incPrefix=False),
                    ', '.join(sorted([c.pStr() for c in theCurveS])),
                    ptsPlotted,
                    theOutPath,
                )
            )
        )
        try:
            self._lisBytes += os.path.getsize(theInPath)
        except OSError:
            # No file exists
            pass
        self.plotCntr += 1
        self.curvePoints += ptsPlotted
        # Add interval counter
        if theEvFirst > theEvLast:
            # Decreasing log
            myInterval = theEvFirst - theEvLast
        else:
            myInterval = theEvLast - theEvFirst
        myInterval *= len(theCurveS)
        self._addInterval(myInterval)
    
    def _addInterval(self, theInterval):
        if len(self._intervalCntrS) == 0:
            self._intervalCntrS.append(theInterval)
        else:
            for aCntr in self._intervalCntrS:
                try:
                    aCntr += theInterval
                    break
                except TotalDepth.LIS.core.Units.ExceptionUnitsMissmatchedCategory:
                    pass
            else:
                # No break; Add a new interval
                self._intervalCntrS.append(theInterval)
            
    def writeHTML(self, theFilePath, theDesc):
        """Write the index.html table.""" 
        lenCmnPref = os.path.commonprefix([t[0] for t in self._plotS]).rfind(os.sep)+1
        # Put the plot summary data into a DictTree
        myTree = DictTree.DictTreeHtmlTable()
        for aPlt in self._plotS:
            key = (aPlt[0][lenCmnPref:],) + aPlt[1:3]
            myTree.add([str(s) for s in key], aPlt[3])
        # Write CSS
        with open(os.path.join(os.path.dirname(theFilePath), self.CSS_FILE_PATH), 'w') as f:
            f.write(CSS_CONTENT_INDEX)
        # Write the index
        with XmlWrite.XhtmlStream(open(theFilePath, 'w')) as myS:
            with XmlWrite.Element(myS, 'head'):
                with XmlWrite.Element(
                        myS,
                        'link',
                        {
                            'href'  : self.CSS_FILE_PATH,
                            'type'  : "text/css",
                            'rel'   : "stylesheet",
                        }
                    ):
                    pass
                with XmlWrite.Element(myS, 'title'):
                    myS.characters('LIS plots in SVG')
            with XmlWrite.Element(myS, 'h1'):
                myS.characters('PlotLogPasses: {:s}'.format(theDesc))
            with XmlWrite.Element(myS, 'table', {'border' : '1'}):
                self._writeHTMLTh(myS)
                self._writeIndexTableRows(myS, myTree, theFilePath)
            # Write: </table>

    def _writeIndexTableRows(self, theS, theTrie, theFilePath):
        # Write the rowspan/colspan data
        for anEvent in theTrie.genColRowEvents():
            if anEvent == theTrie.ROW_OPEN:
                # Write out the '<tr>' element
                theS.startElement('tr', {})
            elif anEvent == theTrie.ROW_CLOSE:
                # Write out the '</tr>' element
                theS.endElement('tr')
            else:
                #print 'TRACE: anEvent', anEvent
                k, v, r, c = anEvent
                # Write '<td rowspan="%d" colspan="%d">%s</td>' % (r, c, txt[-1])
                myTdAttrs = {}
                if r > 1:
                    myTdAttrs['rowspan'] = "%d" % r
                if c > 1:
                    myTdAttrs['colspan'] = "%d" % c
                with XmlWrite.Element(theS, 'td', myTdAttrs):
                    theS.characters(str(k[-1]))
                if v is not None:
                    self._writeValues(theS, v, theFilePath)

    def _writeValues(self, theS, theVal, theFilePath):
        assert(theVal is not None)
        for i, aVal in enumerate(theVal):
            myValAttrs = {}
            if i in (4, 6):
                # Curve list and link
                myValAttrs = {'align' : 'left'}
            else:
                myValAttrs = {'align' : 'right'}
            with XmlWrite.Element(theS, 'td', myValAttrs):
                if i == len(theVal)-1:
                    with XmlWrite.Element(theS, 'a', {'href' : self.retRelPath(os.path.dirname(theFilePath), aVal)}):
                        theS.characters(os.path.basename(aVal))
                else:
                    theS.characters(str(aVal))

    def _writeHTMLTh(self, theS):
        with XmlWrite.Element(theS, 'tr'):
            for aTh in ('Input', 'Pass', 'Film', 'Scale', 'From', 'To', 'Interval', 'Curves', 'Points', 'Plot'):
                with XmlWrite.Element(theS, 'th'):
                    theS.characters(aTh)
    
    def retRelPath(self, d, f):
        """Given directory d and file path of f this returns relative path to f from d."""
        # Make absolute and normalise to remove pesky ../ and so on.
        d = os.path.abspath(d)
        f = os.path.abspath(f)
        pref = os.path.commonprefix([d, os.path.dirname(f)])
        lPref = pref.rfind(os.sep)+1
        dS = d[lPref:].split(os.sep)
        fS = f[lPref:].split(os.sep)
        r = [os.pardir,] * len(dS)
        r += fS
        return os.path.join(*r)        
    
class PlotLogPasses(object):
    """Takes an input path, output path and generates SVG file(s) from LIS."""
    EXCLUDE_FILE_NAMES = ('.DS_Store',)
    def __init__(self, fpIn, fpOut, opts):
        """Constructor.

        fpIn and fpOut are file or directory paths. fpOut will be created if necessary.

        recursive is a flag to control directory recursion.

        keepGoing is a flag passed to the LIS File.FileRead object.

        lgFormatS is a list of strings the correspond to the LgFormat UniqueId XML attribute.
            If absent the LIS file FILM/PRES etc. tables are used.

        apiHeader is a flag to control whether a API header is extracted from CONS tables
            is to be plotted on the top of the log.
        """
        self._fpIn = fpIn
        self._fpOut = fpOut
        self._recursive = opts.recurse
        self._keepGoing = opts.keepGoing
        if opts.LgFormat is None:
            self._lgFormatS = []
        else:
            self._lgFormatS = opts.LgFormat
        self._apiHeader = opts.apiHeader
        self._lgFormatMinCurves = opts.LgFormat_min
        self._scale = opts.scale
        self.plotLogInfo = PlotLogInfo()
        self._processPath(self._fpIn, self._fpOut)
        
    @property
    def usesInternalRecords(self):
        """True if we are going to use the internal records of a file to describe
        the plot. False if we are going to use external records, such as LgFormat XML
        files to describe the plot."""
        return len(self._lgFormatS) == 0 and self._lgFormatMinCurves == 0

    def _processPath(self, fpIn, fpOut):
        if os.path.isfile(fpIn):
            if os.path.basename(fpIn) not in self.EXCLUDE_FILE_NAMES:
                self._processFile(fpIn, fpOut)
        elif os.path.isdir(fpIn):
            self._processDir(fpIn, fpOut)
    
    def _processDir(self, fpIn, fpOut):
        assert(os.path.isdir(fpIn))
        if not os.path.isdir(fpOut):
            os.makedirs(fpOut, exist_ok=True)
        for myName in os.listdir(fpIn):
            myPath = os.path.join(fpIn, myName)
            outPath = os.path.join(fpOut, myName)
            if os.path.isfile(myPath) \
            or (os.path.isdir(myPath) and self._recursive):
                self._processPath(myPath, outPath)

    def _processFile(self, fpIn, fpOut):
        assert(os.path.isfile(fpIn))
        if not os.path.isdir(os.path.dirname(fpOut)):
            os.makedirs(os.path.dirname(fpOut), exist_ok=True)
        assert(os.path.exists(os.path.dirname(fpOut)))
        logging.info('PlotLogPasses._processFile(): Starting on {:s}'.format(fpIn))
        for fn in (self._processFileLIS, self._processFileLAS):
            if fn(fpIn, fpOut):
                break
        else:
            logging.error('PlotLogPasses._processFile(): Can not process "{:s}" successfully'.format(fpIn))
        logging.info('PlotLogPasses._processFile(): Done with {:s}'.format(fpIn))
        
    def _processFileLIS(self, fpIn, fpOut):
        logging.info('PlotLogPasses._processFileLIS(): Starting LIS file {:s}'.format(fpIn))
        assert(os.path.isfile(fpIn))
        assert(os.path.exists(os.path.dirname(fpOut)))
        try:
            # Try to read as LIS file
            myFi = TotalDepth.LIS.core.File.FileRead(fpIn, theFileId=fpIn, keepGoing=self._keepGoing)
            myIdx = TotalDepth.LIS.core.FileIndexer.FileIndex(myFi)
        except ExceptionTotalDepthLIS as err:
            # Failed to read file of create index so not a LIS file
            logging.error('PlotLogPasses._processFileLIS(): Failed with error {!r:s}'.format(err))
            return False
        except Exception as err:
            # Failed to read file of create index so not a LIS file
            logging.critical('PlotLogPasses._processFileLIS(): Failed with error {!r:s}'.format(err))
            return False
        try:
            self.plotLogInfo.logPassCntr += myIdx.numLogPasses()
            # Iterate through the PlotRecordSet objects
            for lpIdx, aPrs in enumerate(myIdx.genPlotRecords(fromInternalRecords=self.usesInternalRecords)):
#                print('lpIdx:', lpIdx)
#                print(' aPrs:', aPrs)
                if self.usesInternalRecords:
                    # Use internal FILM/PRES plotting specification
                    self._plotUsingLISLogicalRecords(myFi, lpIdx, aPrs, fpOut)
                else:
                    # Plot using external plot specification
                    self._plotLISUsingLgFormats(myFi, lpIdx, aPrs, fpOut)
        except ExceptionTotalDepthLIS as err:
            logging.error(
                'PlotLogPasses._processFileLIS(): Can not process as LIS: "{!r:s}", error: {!r:s}'.format(fpIn, err)
            )
            logging.error(traceback.format_exc())
            return False
        except Exception as err:
            logging.critical(
                'PlotLogPasses._processFileLIS(): In "{!r:s}", error type {!r:s}: {!r:s}'.format(fpIn, type(err), err)
            )
            logging.critical(traceback.format_exc())
            return False
        self.plotLogInfo.lisFileCntr += 1
        logging.info('PlotLogPasses._processFileLIS(): Done LIS file {:s}'.format(fpIn))
        return True

    def _processFileLAS(self, fpIn, fpOut):
        logging.info('PlotLogPasses._processFileLAS(): Starting LAS file {:s}'.format(fpIn))
        assert(os.path.isfile(fpIn))
        assert(os.path.exists(os.path.dirname(fpOut)))
        if not TotalDepth.LAS.core.LASRead.hasLASExtension(fpIn):
            return False
        if self.usesInternalRecords:
            # LAS logs do not have internal records that can describe plots
            return False
        try:
            myLasFile = TotalDepth.LAS.core.LASRead.LASRead(fpIn)
            self._plotLASUsingLgFormats(myLasFile, fpOut)
            self.plotLogInfo.logPassCntr += 1 # Only one pass per file in LAS, well LAS 1.2 2.0 anyway
        except ExceptionTotalDepthLAS as err:
            logging.error(
                'PlotLogPasses._processFileLAS(): Can not process as LAS: "{:s}", error: {:s}'.format(fpIn, err)
            )
            return False
        except Exception as err:
            logging.critical('PlotLogPasses._processFileLAS(): In "{:s}", error: {:s}'.format(fpIn, err))
            logging.critical(traceback.format_exc())
            return False
        self.plotLogInfo.lasFileCntr += 1
        logging.info('PlotLogPasses._processFileLAS(): Done LAS file {:s}'.format(fpIn))
        return True
    
    #===================================================================
    # Sect.: Plotting LIS using LIS Logical Records to specify the plot.
    #===================================================================
    def _retPlotFromIntPlotRecordSet(self, theFi, thePrs):
        """Returns a Plot.PlotReadLIS, a LogPass and a list of CONS records from the PlotRecordSet.
        This creates the plot using internal records such as FILM and PRES records."""
        assert(thePrs)
        assert(self.usesInternalRecords)
        theFi.seekLr(thePrs.tellFilm)
        myLrFilm = TotalDepth.LIS.core.LogiRec.LrTableRead(theFi)
        theFi.seekLr(thePrs.tellPres)
        myLrPres = TotalDepth.LIS.core.LogiRec.LrTableRead(theFi)
        if thePrs.tellArea is not None:
            theFi.seekLr(thePrs.tellArea)
            myLrArea = TotalDepth.LIS.core.LogiRec.LrTableRead(theFi)
        else:
            myLrArea = None
        if thePrs.tellPip is not None:
            theFi.seekLr(thePrs.tellPip)
            myLrPip = TotalDepth.LIS.core.LogiRec.LrTableRead(theFi)
        else:
            myLrPip = None
        myPlot = Plot.PlotReadLIS(myLrFilm, myLrPres, myLrArea, myLrPip, self._scale)
        return myPlot, thePrs.logPass, self._retCONSRecS(theFi, thePrs)
    
    def _retCONSRecS(self, theFi, thePrs):
        """Returns a list of CONS Logical Records or None is no API header required."""
        assert(thePrs)
        if self._apiHeader:
            consRecS = []
            for t in thePrs.tellConsS:
                theFi.seekLr(t)
                consRecS.append(TotalDepth.LIS.core.LogiRec.LrTableRead(theFi))
            return consRecS
    
    def _plotUsingLISLogicalRecords(self, theFi, theLpIdx, thePrs, theFpOut):
        """Plots a LogPass from a LIS file using the LIS Logical Records to
        specify the plot.
        theFi - the LIS File object.
        theLpIdx - integer for the LogPass in the LIS File.
        thePrs - a PlotRecord Set that holds the seek positions of the appropriate
            LIS Logical Records.
        theFpOut - Output file path for the SVG file(s), one per FILM ID.
        """
        myPlot, myLogPass, myCONSRecS = self._retPlotFromIntPlotRecordSet(theFi, thePrs)
        for aFilmId in myPlot.filmIdS():
            logging.info('PlotLogPasses._plotUsingLISLogicalRecords(): FILM ID={:s}.'.format(aFilmId.pStr(strip=True)))
            if myPlot.hasDataToPlotLIS(myLogPass, aFilmId):
                myOutFilePath = '{:s}_{:04d}_{:s}.svg'.format(theFpOut, theLpIdx, aFilmId.pStr(strip=True))
#                myFout = open(myOutFilePath, 'w')
                myCurvIDs, numPoints = myPlot.plotLogPassLIS(
                        theFi,
                        myLogPass,
                        myLogPass.xAxisFirstEngVal,
                        myLogPass.xAxisLastEngVal,
                        aFilmId,
                        myOutFilePath,
#                        myFout,
                        frameStep=1,
                        title="Plot: {:s} LogPass: {:d} FILM ID={:s}".format(
                            os.path.abspath(myOutFilePath),
                            theLpIdx,
                            aFilmId.pStr(strip=True),
                        ),
                        lrCONS=myCONSRecS,
                    )
                assert(myCurvIDs is not None and numPoints is not None)
                # So here the essential data that we have to put in the index.html is:
                # Key: myOutFilePath or input file fp, lpIdx, aFilmId,
                # Value: (myPlot.xScale(aFilmId), myLogPass.xAxisFirstEngVal, myLogPass.xAxisLastEngVal, myCurvIDs)
                self.plotLogInfo.addPlotResult(
                    theFi.fileId,
                    myOutFilePath,
                    theLpIdx,
                    aFilmId.pStr(),
                    myPlot.xScale(aFilmId),
                    myLogPass.xAxisFirstEngVal,
                    myLogPass.xAxisLastEngVal,
                    theCurveS=myCurvIDs,
                    ptsPlotted=numPoints)
            else:
                logging.info(
                    'PlotLogPasses._plotUsingLISLogicalRecords(): No data to plot for FILM ID {!r:s}'.format(aFilmId)
                )
    #=================================================================
    # End: Plotting LIS using LIS Logical Records to specify the plot.
    #=================================================================
    
    #===============================================
    # Sect.: Plotting using XML files - common code.
    #===============================================
    def _retPlotFromXML(self, theFi, theIdxLogPass, theUniqueId):
        assert(len(self._lgFormatS) > 0)
        assert(theUniqueId in self._lgFormatS)
        myFcfg = FILMCfgXML.FilmCfgXMLRead()
        return Plot.PlotReadXML(myFcfg[theUniqueId], self._scale), theIdxLogPass.logPass
    
    def _retOutPathTitle(self, theFpOut, theLpIdx, aUniqueId):
        fp = '{:s}_{:04d}_{:s}.svg'.format(theFpOut, theLpIdx, aUniqueId)
        return (
            fp,
            "Plot: {:s} LogPass: {:d} FILM ID={:s}".format(
#                os.path.abspath(fp),
                os.path.basename(fp),
                theLpIdx,
                aUniqueId,
            ),
        )
    
    def _retUniqueIdS(self, theLpOrLasFile):
        """Returns a list of UniqueID strings depending on my constructor."""
        assert(not self.usesInternalRecords)
        if self._lgFormatMinCurves > 0:
            # Filter out those that have fewer curves than self._lgFormatMinCurves
            myMap = XMLMatches.fileCurveMap(theLpOrLasFile)
            myLgUidS = []
            for u,i in myMap.items():
                if len(i) > self._lgFormatMinCurves \
                and (len(self._lgFormatS) == 0 or u in self._lgFormatS):
                    myLgUidS.append(u)
            return myLgUidS 
        return self._lgFormatS
            
    #=============================================
    # End: Plotting using XML files - common code.
    #=============================================
    
    #=========================================================
    # Sect.: Plotting LIS using XML files to specify the plot.
    #=========================================================
    def _plotLISUsingLgFormats(self, theFi, theLpIdx, thePrs, theFpOut):
        """Plots a LogPass from a LIS file using the LgFormat XML files
        specify the plot.
        theFi - the LIS File object.
        theLpIdx - integer for the LogPass in the LIS File.
        thePrs - a PlotRecord Set that holds the seek positions of the appropriate
            LIS Logical Records (we only use CONS records here for the API header).
        theFpOut - Output file path for the SVG file(s), one per FILM ID.
        """
        assert(not self.usesInternalRecords)
        logging.debug('PlotLogPasses._plotLISUsingLgFormats(): PlotRecords={:s}.'.format(str(thePrs)))
        myCONSRecS = self._retCONSRecS(theFi, thePrs)
        for aUniqueId in self._retUniqueIdS(thePrs.logPass):
            logging.info('PlotLogPasses._plotLISUsingLgFormats(): UniqueId={:s}.'.format(aUniqueId))
            myPlot = Plot.PlotReadXML(aUniqueId, self._scale)
            if myPlot.hasDataToPlotLIS(thePrs.logPass, aUniqueId):
                # Create output path and plot it
                myOutFilePath, myTitle = self._retOutPathTitle(theFpOut, theLpIdx, aUniqueId)
                myCurvIDs, numPoints = myPlot.plotLogPassLIS(
                        theFi,
                        thePrs.logPass,
                        thePrs.logPass.xAxisFirstEngVal,
                        thePrs.logPass.xAxisLastEngVal,
                        aUniqueId,
                        myOutFilePath,
                        frameStep=1,
                        title=myTitle,
                        lrCONS=myCONSRecS,
                    )
                assert(myCurvIDs is not None and numPoints is not None)
                # So here the essential data that we have to put in the index.html is:
                # Key: myOutFilePath or input file fp, lpIdx, aFilmId,
                # Value: (myPlot.xScale(aFilmId), myLogPass.xAxisFirstEngVal, myLogPass.xAxisLastEngVal, myCurvIDs)
                self.plotLogInfo.addPlotResult(
                    theFi.fileId,
                    myOutFilePath,
                    theLpIdx,
                    aUniqueId,
                    myPlot.xScale(aUniqueId),
                    thePrs.logPass.xAxisFirstEngVal,
                    thePrs.logPass.xAxisLastEngVal,
                    theCurveS=myCurvIDs,
                    ptsPlotted=numPoints)
            else:
                logging.info('PlotLogPasses._plotLISUsingLgFormats(): No data to plot for FILM ID {:s}'.format(aUniqueId))
    #=======================================================
    # End: Plotting LIS using XML files to specify the plot.
    #=======================================================

    #=========================================================
    # Sect.: Plotting LAS using XML files to specify the plot.
    #=========================================================
    def _plotLASUsingLgFormats(self, theLasFile, theFpOut):
        """Plots a LogPass from a LAS file using the LgFormat XML files
        specify the plot.
        theFi - the LASFile object.
        theFpOut - Output file path for the SVG file(s), one per XML UniqueId.
        """
        assert(not self.usesInternalRecords)
        for aUniqueId in self._retUniqueIdS(theLasFile):
            logging.info('PlotLogPasses._plotLASUsingLgFormats(): UniqueId={:s}.'.format(aUniqueId))
            # Note: Only one log pass per LAS file so index 0
            myOutFilePath, myTitle = self._retOutPathTitle(theFpOut, 0, aUniqueId)
            myPlot = Plot.PlotReadXML(aUniqueId, self._scale)
            if myPlot.hasDataToPlotLAS(theLasFile, aUniqueId):
                myCurvIDs, numPoints = myPlot.plotLogPassLAS(
                    theLasFile,
                    theLasFile.xAxisStart,
                    theLasFile.xAxisStop,
                    aUniqueId,
                    myOutFilePath,
                    frameStep=1,
                    title=myTitle,
                    plotHeader=self._apiHeader,
                )
#                logging.fatal('Plot curves: {:s} and points: {:s}'.format(str(myCurvIDs), str(numPoints)))
                assert(myCurvIDs is not None and numPoints is not None)
                # So here the essential data that we have to put in the index.html is:
                # Key: myOutFilePath or input file fp, lpIdx, aFilmId,
                # Value: (myPlot.xScale(aFilmId), myLogPass.xAxisFirstEngVal, myLogPass.xAxisLastEngVal, myCurvIDs)
                self.plotLogInfo.addPlotResult(
                    theLasFile.id,
                    myOutFilePath,
                    0,
                    aUniqueId,
                    myPlot.xScale(aUniqueId),
                    theLasFile.xAxisStart,
                    theLasFile.xAxisStop,
                    theCurveS=myCurvIDs,
                    ptsPlotted=numPoints)
    #=======================================================
    # End: Plotting LAS using XML files to specify the plot.
    #=======================================================
    
################################
# Section: Multiprocessing code.
################################
def processFile(fpIn, fpOut, opts):
    if not os.path.exists(os.path.dirname(fpOut)):
        try:
            os.makedirs(os.path.dirname(fpOut))
        except OSError:
            pass
    myPlp = PlotLogPasses(fpIn, fpOut, opts)
    return myPlp.plotLogInfo

def plotLogPassesMP(dIn, dOut, opts):
    """Multiprocessing code to plot log passes. Returns a PlotLogInfo object."""
    if opts.jobs < 1:
        jobs = multiprocessing.cpu_count()
    else:
        jobs = opts.jobs
    logging.info('plotLogPassesMP(): Setting multi-processing jobs to %d' % jobs)
    myPool = multiprocessing.Pool(processes=jobs)
    myTaskS = [
        (t.filePathIn, t.filePathOut, opts) \
            for t in DirWalk.dirWalk(dIn, dOut, opts.glob, opts.recurse, bigFirst=True)
    ]
    retResult = PlotLogInfo()
    myResults = [
        r.get() for r in [
            myPool.apply_async(processFile, t) for t in myTaskS
        ]
    ]
    for r in myResults:
        # r is a PlotLogInfo object
        retResult += r
    return retResult
################################
# End: Multiprocessing code.
################################

def main():
    print ('Cmd: %s' % ' '.join(sys.argv))
    # TODO: Option to treat files with -f, --format as LAS, LIS, AUTO
    # TODO: Depth scale overrides -s, --scale ?
    parser = cmn_cmd_opts.path_in_out(
        'Generates SVG plot(s) from input LIS & LAS file/directory to an output file/directory.',
        prog=None,
        version=__version__,
    )
    cmn_cmd_opts.add_log_level(parser)
    cmn_cmd_opts.add_multiprocessing(parser)
    parser.add_argument("-A", "--API", action="store_true", dest="apiHeader", default=False,
                      help="Put an API header on each plot. [default: False]")
    parser.add_argument("-x", "--xml", action="append", dest="LgFormat", default=[],
                      help="Use XML LgFormat UniqueId to use for plotting (additive)." \
                      +" Use -x? to see what LgFormats (UniqueID+Description) are available." \
                      +" Use -x?? to see what curves each format can plot. See also -X. [default: []]")
    parser.add_argument(
            "-X", "--XML", type=int, dest="LgFormat_min", default=0,
            help="Use any LgFormat XML plots that use n or more outputs. If -x option present limited by those LgFormats [default: 0]" 
        )
    parser.add_argument("-g", "--glob", action="store_true", dest="glob", default=None,
                      help="File match pattern. Default: %(default)s.")
    # parser.add_argument("-f", "--file-type", choices=['LAS', 'LIS', 'AUTO'],
    #        help="File format to assume for the input, AUTO will do it's best. [default: \"AUTO\"].")
    parser.add_argument("-s", "--scale", action="append", type=int, dest="scale", default=0,
            help="Scale of X axis to use (an integer). [default: 0].")
    args = parser.parse_args()
    # Initialise logging etc.
    cmn_cmd_opts.set_log_level(args)
    # print('args', args)
    # return 0
    start_clock = time.clock()
    start_time = time.time()
    # Your code here
    if '?' in ''.join(args.LgFormat):
        # Handle -x? here and exit
        myFg = FILMCfgXML.FilmCfgXMLRead()
        print('XML LgFormats available: [{:d}]'.format(len(myFg.keys())))
        print(myFg.longStr(''.join(args.LgFormat).count('?')))
        return 1
    if cmn_cmd_opts.multiprocessing_requested(args):
        myPlp = PlotLogPasses(
            args.path_in,
            args.path_out,
            args,
        )
        myResult = myPlp.plotLogInfo
    else:
        myResult = plotLogPassesMP(
            args.path_in,
            args.path_out,
            args,
        )
    if os.path.isdir(args.path_out):
        myResult.writeHTML(os.path.join(args.path_out, 'index.html'), args.path_in)
    print('plotLogInfo', str(myResult))
    print('  CPU time = %8.3f (S)' % (time.clock() - start_clock))
    print('Exec. time = %8.3f (S)' % (time.time() - start_time))
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
