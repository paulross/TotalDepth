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
"""
Created on May 23, 2011

@author: p2ross
"""
__author__  = 'Paul Ross'
__date__    = '2011-05-23'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

import time
import sys
import os
import logging
import multiprocessing
import collections
from optparse import OptionParser

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import FileIndexer
from TotalDepth.LIS.core import Units
from TotalDepth.util.plot import Plot
from TotalDepth.util.plot import FILMCfgXML
from TotalDepth.util.plot import PRESCfgXML
from TotalDepth.util import DictTree
from TotalDepth.util import DirWalk
from TotalDepth.util import XmlWrite
#from TotalDepth.util import HtmlUtils

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
IndexTableValue = collections.namedtuple('IndexTableValue', 'scale evFirst evLast curves numPoints outPath')

class PlotLogInfo(object):
    """Class that collates information about the results of plotting log passes.
    This can, for example, write out an index.html page with links to SVG pages."""
    CSS_FILE_PATH = 'index.css'
    def __init__(self):
        # So here the essential data that we have to put in the index.html is:
        # A list of tuples of:
        # (theInPath, theLpIdx, theFilmID, IndexTableValue(theScale, theEvFirst, theEvLast, theCurveS, theOutPath))
        # as: (str,     int,       str,    IndexTableValue(number,    EngVal,     EngVal,  [str, ...], str))
        self._plotS = []
        self._lisBytes = 0
        self.lisFileCntr = 0
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
                repr(self), self.lisFileCntr, self._lisBytes, self.logPassCntr, self.plotCntr, self.curvePoints)]
        for l in sorted(self._plotS):
            retL.append('{:s}'.format(str(l)))
        for anEv in self._intervalCntrS:
            retL.append('Interval*curves: {:s}'.format(anEv.newEngValInOpticalUnits().strFormat('{:.3f}')))
        return '\n'.join(retL)
        
    def __iadd__(self, other):
        self._plotS += other._plotS
        self._lisBytes += other._lisBytes
        self.lisFileCntr += other.lisFileCntr
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
        self._plotS.append(
            (
                theInPath,
                theLpIdx,
                theFilmID,
                IndexTableValue(
                    theScale,
                    theEvFirst.newEngValInOpticalUnits().strFormat('{:.1f}', incPrefix=False),
                    theEvLast.newEngValInOpticalUnits().strFormat('{:.1f}', incPrefix=False),
                    ', '.join([c.pStr() for c in theCurveS]),
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
                except Units.ExceptionUnitsMissmatchedCategory:
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
            if i == 3:
                # Curve list
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
            for aTh in ('Input', 'Pass', 'Film', 'Scale', 'From', 'To', 'Curves', 'Points', 'Plot'):
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
    def __init__(self, fpIn, fpOut, recursive=False, keepGoing=True, lgFormatS=None, apiHeader=False):
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
        self._recursive = recursive
        self._keepGoing = keepGoing
        if lgFormatS is None:
            self._lgFormatS = []
        else:
            self._lgFormatS = lgFormatS

        # FIXME: Use lgFormats
        self._apiHeader = apiHeader
        self.plotLogInfo = PlotLogInfo()
        self._processPath()

    def _processPath(self):
        if os.path.isfile(self._fpIn):
            self._processFile(self._fpIn, self._fpOut)
        elif os.path.isdir(self._fpIn):
            self._processDir(self._fpIn, self._fpOut)
    
    def _processDir(self, fpIn, fpOut):
        assert(os.path.isdir(fpIn))
        if not os.path.isdir(fpOut):
            try:
                os.makedirs(fpOut)
            except OSError:
                pass
        for myName in os.listdir(fpIn):
            myPath = os.path.join(fpIn, myName)
            outPath = os.path.join(fpOut, myName)
            if os.path.isdir(myPath) and self._recursive:
                self._processDir(myPath, outPath)
            elif os.path.isfile(myPath):
                self._processFile(myPath, outPath)
    #===============================================================
    # Sect.: Plotting using LIS Logical Records to specify the plot.
    #===============================================================
    def _retPlotFromPlotRecordSet(self, theFi, thePrs):
        """Returns a Plot.PlotReadLIS, a LogPass and a list of CONS records from the PlotRecordSet."""
        assert(thePrs)
        theFi.seekLr(thePrs.tellFilm)
        myLrFilm = LogiRec.LrTableRead(theFi)
        theFi.seekLr(thePrs.tellPres)
        myLrPres = LogiRec.LrTableRead(theFi)
        if thePrs.tellArea is not None:
            theFi.seekLr(thePrs.tellArea)
            myLrArea = LogiRec.LrTableRead(theFi)
        else:
            myLrArea = None
        if thePrs.tellPip is not None:
            theFi.seekLr(thePrs.tellPip)
            myLrPip = LogiRec.LrTableRead(theFi)
        else:
            myLrPip = None
        myPlot = Plot.PlotReadLIS(myLrFilm, myLrPres, myLrArea, myLrPip)
        return myPlot, thePrs.logPass, self._retCONSRecS(theFi, thePrs)
    
    def _retCONSRecS(self, theFi, thePrs):
        """Returns a list of CONS Logical Records or None is no API header required."""
        assert(thePrs)
        if self._apiHeader:
            consRecS = []
            for t in thePrs.tellConsS:
                theFi.seekLr(t)
                consRecS.append(LogiRec.LrTableRead(theFi))
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
        myPlot, myLogPass, myCONSRecS = self._retPlotFromPlotRecordSet(theFi, thePrs)
        for aFilmId in myPlot.filmIdS():
            logging.info('PlotLogPasses._plotUsingLISLogicalRecords(): FILM ID={:s}.'.format(aFilmId.pStr(strip=True)))
            if myPlot.hasDataToPlotLIS(myLogPass, aFilmId):
                myOutFilePath = '{:s}_{:04d}_{:s}.svg'.format(theFpOut, theLpIdx, aFilmId.pStr(strip=True))
                myFout = open(myOutFilePath, 'w')
                myCurvIDs, numPoints = myPlot.plotLogPassLIS(
                        theFi,
                        myLogPass,
                        myLogPass.xAxisFirstEngVal,
                        myLogPass.xAxisLastEngVal,
                        aFilmId,
                        myFout,
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
                    'PlotLogPasses._plotUsingLISLogicalRecords(): No data to plot for FILM ID {}'.format(aFilmId)
                )
    #=============================================================
    # End: Plotting using LIS Logical Records to specify the plot.
    #=============================================================
    
    #=====================================================
    # Sect.: Plotting using XML files to specify the plot.
    #=====================================================
    def _retPlotFromXML(self, theFi, theIdxLogPass, theUniqueId):
        assert(len(self._lgFormatS) > 0)
        assert(theUniqueId in self._lgFormatS)
        myFcfg = FILMCfgXML.FilmCfgXMLRead()
        return Plot.PlotReadXML(myFcfg[theUniqueId]), theIdxLogPass.logPass
    
    def _plotUsingLgFormats(self, theFi, theLpIdx, thePrs, theFpOut):
        """Plots a LogPass from a LIS file using the LgFormat XML files
        specify the plot.
        theFi - the LIS File object.
        theLpIdx - integer for the LogPass in the LIS File.
        thePrs - a PlotRecord Set that holds the seek positions of the appropriate
            LIS Logical Records (we only use CONS records here for the API header).
        theFpOut - Output file path for the SVG file(s), one per FILM ID.
        """
        assert(len(self._lgFormatS) > 0)
        _p, myLogPass, myCONSRecS = self._retPlotFromPlotRecordSet(theFi, thePrs)
        myFilm = FILMCfgXML.FilmCfgXMLRead()
        for aUniqueId in self._lgFormatS:
            logging.info('PlotLogPasses._plotUsingLgFormats(): UniqueId={:s}.'.format(aUniqueId))
            # Create a PRES like object from the UniqueId
            myRoot = myFilm.rootNode(aUniqueId)
            if myRoot is not None:
                myPres = PRESCfgXML.PresCfgXMLRead(myFilm, aUniqueId)
                myPlot = Plot.PlotReadXML(aUniqueId)
                if myPlot.hasDataToPlotLIS(myLogPass, aUniqueId):
                    # Create output path and plot it
                    myOutFilePath = '{:s}_{:04d}_{:s}.svg'.format(theFpOut, theLpIdx, aUniqueId)
                    myCurvIDs, numPoints = myPlot.plotLogPassLIS(
                            theFi,
                            myLogPass,
                            myLogPass.xAxisFirstEngVal,
                            myLogPass.xAxisLastEngVal,
                            aUniqueId,
                            open(myOutFilePath, 'w'),
                            frameStep=1,
                            title="Plot: {:s} LogPass: {:d} FILM ID={:s}".format(
                                os.path.abspath(myOutFilePath),
                                theLpIdx,
                                aUniqueId,
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
                        aUniqueId,
                        myPlot.xScale(aUniqueId),
                        myLogPass.xAxisFirstEngVal,
                        myLogPass.xAxisLastEngVal,
                        theCurveS=myCurvIDs,
                        ptsPlotted=numPoints)
                else:
                    logging.error('PlotLogPasses._plotUsingLgFormats(): No root node for UniqueId: "{:s}"'.format(aUniqueId))
            else:
                logging.info('PlotLogPasses._plotUsingLgFormats(): No data to plot for FILM ID {:s}'.format(aUniqueId))
    #===================================================
    # End: Plotting using XML files to specify the plot.
    #===================================================

    def _processFile(self, fpIn, fpOut):
        assert(os.path.isfile(fpIn))
        assert(os.path.exists(os.path.dirname(fpOut)))
        logging.info('PlotLogPasses._processFile(): Starting on {:s}'.format(fpIn))
        # Read LIS file and create index
        myFi = File.FileRead(fpIn, theFileId=fpIn, keepGoing=self._keepGoing)
        try:
            myIdx = FileIndexer.FileIndex(myFi)
        except ExceptionTotalDepthLIS as err:
            logging.error('Can not create index: for "{:s}", error: {:s}'.format(fpIn, err))
            return
        # Iterate through the PlotRecordSet objects
        for lpIdx, aPrs in enumerate(myIdx.genPlotRecords()):
            if len(self._lgFormatS) == 0:
                # Use internal FILM/PRES plotting specification
                self._plotUsingLISLogicalRecords(myFi, lpIdx, aPrs, fpOut)
            else:
                self._plotUsingLgFormats(myFi, lpIdx, aPrs, fpOut)
            
            
#            myPlot, myLogPass, myCONSRecS = self._retPlotFromPlotRecordSet(myFi, aPrs)
#            for aFilmId in myPlot.filmIdS():
#                logging.info('PlotLogPasses._processFile(): FILM ID={:s}.'.format(aFilmId.pStr(strip=True)))
#                if myPlot.hasDataToPlotLIS(myLogPass, aFilmId):
#                    myOutFilePath = '{:s}_{:04d}_{:s}.svg'.format(fpOut, lpIdx, aFilmId.pStr(strip=True))
#                    myFout = open(myOutFilePath, 'w')
#                    myCurvIDs, numPoints = myPlot.plotLogPassLIS(myFi,
#                            myLogPass,
#                            myLogPass.xAxisFirstEngVal,
#                            myLogPass.xAxisLastEngVal,
#                            aFilmId,
#                            myFout,
#                            frameStep=1,
#                            title="Plot: {:s} LogPass: {:d} FILM ID={:s}".format(
#                                os.path.abspath(myOutFilePath),
#                                lpIdx,
#                                aFilmId.pStr(strip=True),
#                            ),
#                            lrCONS=myCONSRecS,
#                        )
#                    assert(myCurvIDs is not None and numPoints is not None)
#                    # So here the essential data that we have to put in the index.html is:
#                    # Key: myOutFilePath or input file fp, lpIdx, aFilmId,
#                    # Value: (myPlot.xScale(aFilmId), myLogPass.xAxisFirstEngVal, myLogPass.xAxisLastEngVal, myCurvIDs)
#                    self.plotLogInfo.addPlotResult(
#                        fpIn,
#                        myOutFilePath,
#                        lpIdx,
#                        aFilmId.pStr(),
#                        myPlot.xScale(aFilmId),
#                        myLogPass.xAxisFirstEngVal,
#                        myLogPass.xAxisLastEngVal,
#                        theCurveS=myCurvIDs,
#                        ptsPlotted=numPoints)
#                else:
#                    logging.info('PlotLogPasses._processFile(): No data to plot for FILM ID {:s}'.format(aFilmId))

        # Count the number of LogPasses, files etc.
        self.plotLogInfo.logPassCntr += myIdx.numLogPasses()
        self.plotLogInfo.lisFileCntr += 1
        logging.info('PlotLogPasses._processFile(): Done with {:s}'.format(fpIn))
    
################################
# Section: Multiprocessing code.
################################
def processFile(fpIn, fpOut, keepGoing, lgFormatS, apiHeader):
    if not os.path.exists(os.path.dirname(fpOut)):
        try:
            os.makedirs(os.path.dirname(fpOut))
        except OSError:
            pass
    myPlp = PlotLogPasses(fpIn, fpOut, recursive=False, keepGoing=keepGoing, lgFormatS=lgFormatS, apiHeader=apiHeader)
    return myPlp.plotLogInfo

def plotLogPassesMP(dIn, dOut, fnMatch, recursive, keepGoing, lgFormatS, apiHeader, jobs):
    """Multiprocessing code to plot log passes. Returns a PlotLogInfo object."""
    if jobs < 1:
        jobs = multiprocessing.cpu_count()
    logging.info('plotLogPassesMP(): Setting multi-processing jobs to %d' % jobs)
    myPool = multiprocessing.Pool(processes=jobs)
    myTaskS = [
        (t.filePathIn, t.filePathOut, keepGoing, lgFormatS, apiHeader) \
            for t in DirWalk.dirWalk(dIn, dOut, fnMatch, recursive, bigFirst=True)
    ]
    retResult = PlotLogInfo()
    #print('myTaskS', myTaskS)
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
    usage = """usage: %prog [options] in out
Generates plot(s) from input LIS file or directory to an output destination."""
    print ('Cmd: %s' % ' '.join(sys.argv))
    optParser = OptionParser(usage, version='%prog ' + __version__)
    optParser.add_option("-A", "--API", action="store_true", dest="apiHeader", default=False, 
                      help="Include and API header on top of each plot. [default: %default]")
    optParser.add_option("-k", "--keep-going", action="store_true", dest="keepGoing", default=False, 
                      help="Keep going as far as sensible. [default: %default]")
    optParser.add_option("-r", "--recursive", action="store_true", dest="recursive", default=False, 
                      help="Process input recursively. [default: %default]")
    optParser.add_option(
            "-j", "--jobs",
            type="int",
            dest="jobs",
            default=-1,
            help="Max processes when multiprocessing. Zero uses number of native CPUs [%d]. -1 disables multiprocessing." \
                    % multiprocessing.cpu_count() \
                    + " [default: %default]" 
        )      
    optParser.add_option(
            "-l", "--loglevel",
            type="int",
            dest="loglevel",
            default=40,
            help="Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: %default]"
        )
    optParser.add_option("-x", "--xml", action="append", dest="LgFormat", default=[],
                      help="Add an XML LgFormat to use for plotting. Value is the UniqueId. Use -x? to see what LgFormats are available. [default: %default]")
    opts, args = optParser.parse_args()
    clkStart = time.clock()
    timStart = time.time()
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    # Your code here
    # Handle -x?
    if '?' in opts.LgFormat:
        myFg = FILMCfgXML.FilmCfgXMLRead()
        print('XML LgFormats available: [{:d}]'.format(len(myFg.keys())))
        print(myFg.longStr())
        while '?' in opts.LgFormat:
            opts.LgFormat.remove('?')
        return 1
    if len(args) != 2:
        optParser.print_help()
        optParser.error("I can't do much without an input path to LIS file(s) and an output path.")
        return 1
    if opts.jobs == -1:
        myPlp = PlotLogPasses(args[0], args[1], opts.recursive, opts.keepGoing, opts.LgFormat, opts.apiHeader)
        myResult = myPlp.plotLogInfo
    else:
        myResult = plotLogPassesMP(args[0], args[1], None, opts.recursive, opts.keepGoing, opts.LgFormat, opts.apiHeader, opts.jobs)
    myResult.writeHTML(os.path.join(args[1], 'index.html'), args[0])
    print('plotLogInfo', str(myResult))
    print('  CPU time = %8.3f (S)' % (time.clock() - clkStart))
    print('Exec. time = %8.3f (S)' % (time.time() - timStart))
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    multiprocessing.freeze_support()
    sys.exit(main())
