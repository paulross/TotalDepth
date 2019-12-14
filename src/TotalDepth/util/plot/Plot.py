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
"""Created on 28 Feb 2011

Plotting LIS data requires these components:

* A PlotConfig object
* A data set (e.g. a LogPass with a FrameSet).
* An output driver (e.g. screen, print PDF, web SVG).

User creates a PlotConfig (this reflects a PRES table). This is reusable.

User specifies a data set (from, to, channels etc.).
    e.g. Invoke LogPass.setFrameSet(File, theFrameSlice=theFrameSlice, theChList=theChList)
User says 'plot this data set with this configuration to this output device'.
    e.g. Plot(PlotConfig, LogPass, PlotDevice)
    Plot uses LogPass.genChScValues(ch, sc) to plot individual curves.
    
Lacunae
=======
Area plotting.
Caching (e.g. SVG fragments - is this worth it?)
    
PlotConfig
==========

PlotTracks
----------
Typically a three track (+depth) have these dimensions in inches:

=====    ====    =====    =====
Track    Left    Right    Width
=====    ====    =====    =====
1        0       2.4      2.4
Depth    2.4     3.2      0.8
2        3.2     5.6      2.4
3        5.6     8.0      2.4
=====    ====    =====    =====

Track names can be split (e.g. LHT1 is left hand track 1) or merged (T23 is
spread across tracks two and three).

Examples of PRES and FILM records::

     Table record (type 34) type: PRES
    
    MNEM  OUTP  STAT  TRAC  CODI  DEST  MODE      FILT          LEDG          REDG
    -----------------------------------------------------------------------------------
    
    SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000
    CALI  CALI  ALLO  T1    LDAS  1     SHIF      0.500000       5.00000       15.0000
    MINV  MINV  DISA  T1    LLIN  1     SHIF      0.500000       30.0000       0.00000
    MNOR  MNOR  DISA  T1    LDAS  1     SHIF      0.500000       30.0000       0.00000
    LLD   LLD   ALLO  T23   LDAS  1     GRAD      0.500000      0.200000       2000.00
    LLDB  LLD   ALLO  T2    HDAS  1     GRAD      0.500000       2000.00       200000.
    LLG   LLG   DISA  T23   LDAS  1     GRAD      0.500000      0.200000       2000.00
    LLGB  LLG   DISA  T2    HDAS  1     GRAD      0.500000       2000.00       200000.
    LLS   LLS   ALLO  T23   LSPO  1     GRAD      0.500000      0.200000       2000.00
    LLSB  LLS   ALLO  T2    HSPO  1     GRAD      0.500000       2000.00       200000.
    MSFL  MSFL  ALLO  T23   LLIN  1     GRAD      0.500000      0.200000       2000.00
    
    Table record (type 34) type: FILM
    
    MNEM  GCOD  GDEC  DEST  DSCA
    -----------------------------
    
    1     E20   -4--  PF1   D200
    2     EEE   ----  PF2   D200 
    
    Table record (type 34) type: PRES
    
    MNEM  OUTP  STAT  TRAC  CODI  DEST  MODE      FILT          LEDG          REDG
    -----------------------------------------------------------------------------------
    
    NPHI  NPHI  ALLO  T23   LDAS  1     SHIF      0.500000      0.450000     -0.150000
    DRHO  DRHO  ALLO  T3    LSPO  1     NB        0.500000     -0.250000      0.250000
    PEF   PEF   ALLO  T23   LGAP  1     SHIF      0.500000       0.00000       10.0000
    SGR         DISA  T1    LLIN  1     SHIF      0.500000       0.00000       300.000
    CGR         DISA  T1    LGAP  1     SHIF      0.500000       0.00000       300.000
    TENS  TENS  DISA  T3    LGAP  1     SHIF      0.500000       14000.0       4000.00
    CAL   CALI  ALLO  T1    LSPO  1     SHIF      0.500000       5.00000       15.0000
    BS    BS    DISA  T1    LGAP  1     SHIF      0.500000       5.00000       15.0000
    FFLS  FFLS  DISA  T1    LLIN  2     NB        0.500000     -0.150000      0.150000
    FFSS  FFSS  DISA  T1    LDAS  2     NB        0.500000     -0.150000      0.150000
    LSHV  LSHV  DISA  T3    LLIN  2     WRAP      0.500000       2150.00       2250.00
    SSHV  SSHV  DISA  T3    LDAS  2     WRAP      0.500000       1950.00       2050.00
    FLS   FLS   DISA  T2    LLIN  2     SHIF      0.500000       0.00000       150.000
    FSS   FSS   DISA  T2    LDAS  2     SHIF      0.500000       0.00000       150.000
    RHOB  RHOB  ALLO  T23   LLIN  1     SHIF      0.500000       1.95000       2.95000
    PHIX  PHIX  ALLO  T1    LLIN  1     NB        0.500000      0.500000       0.00000

"""
__author__  = 'Paul Ross'
__date__    = '2011-02-28'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

#import time
#import sys
import os
import logging
import collections
import pprint
#import math
#from optparse import OptionParser

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import EngVal
from TotalDepth.LIS.core import Units

from TotalDepth.util.plot import Coord
from TotalDepth.util.plot import Stroke
from TotalDepth.util.plot import SVGWriter
from TotalDepth.util.plot import XGrid
from TotalDepth.util.plot import FILMCfg
from TotalDepth.util.plot import PRESCfg
from TotalDepth.util.plot import FILMCfgXML
from TotalDepth.util.plot import PRESCfgXML
from TotalDepth.util.plot import PlotConstants
from TotalDepth.util.plot import LogHeader

#: Allows detailed trace comments to appear in the SVG
COMMENTS_IN_SVG_TRACE = False
#: A few comments in SVG to delinialte header, Grid, Xaxis, curves etc
COMMENTS_IN_SVG_SECTION = True
#: Width of comment for sections
COMMENTS_IN_SVG_SECTION_WIDTH = 40
#: Map of section level to comment padding character
COMMENTS_IN_SVG_SECTION_LEVEL_TUPLE = ('=', '.', '^',)

# TODO: Should remove LIS from name as plotting now also covers LAS files
class ExceptionTotalDepthLISPlot(ExceptionTotalDepthLIS):
    """Exception for plotting."""
    pass

class ExceptionTotalDepthPlotRoll(ExceptionTotalDepthLISPlot):
    """Exception for plotting."""
    pass

# Describes a curve plots data, fn is the track transfer function, buffer is a
# list of Coord.Pt() and prevWrap is the previous wrap value.
class CurvePlotData(object):
    def __init__(self, theId, theFn):
        self._id = theId
        self._fn = theFn
        self.buffer = []
        self.prevWrap = None
    
    def __str__(self):
        return '{!r:s} id={!r:s} fn={!r:s}'.format(self, self._id, self._fn)
    
    @property
    def fn(self):
        return self._fn
    
    @property
    def id(self):
        return self._id
    
#############################################################################
# Section: Code that handles the curve scales (or legends) that appear at top
# and bottom of the log.
#############################################################################
class CurvePlotScale(collections.namedtuple('CurvePlotScale', 'name halfTrackStart halfTracks')):
    """Holds a minimal amount of curve plot scale and so on for the layout of
    the scale pane at each end of the log.
    
    halfTrackStart is the start of the curve for a standard three track log
    T1=0, TD=2, T2=4, T3=6
    
    halfTracks is the curve span as an integer so T23=4 LHT1=1 and so on."""
    __slots__ = ()
    def __lt__(self, other):
        """Slightly weird sort order, larger halfTracks come first then names."""
        if self.halfTracks > other.halfTracks:
            retVal = True
        elif self.halfTracks == other.halfTracks:
            retVal = self.name < other.name
        else:
            retVal = False
        return retVal

# Used to record what curve mnemonic goes into which vertical slice of
# the scale at each end of the log
# slice is an integer, curveName is a CURV MNEM, slice and span are half-track integers
ScaleSliceCurve = collections.namedtuple('ScaleSliceCurve', 'slice curveName start span')

class CurvePlotScaleSlotMap(object):
    """Keeps track of which slots are available for putting the curve scales in
    at the top and bottom of the log.
    This scale are is divided into slices that span the plot from left to right.
    These slices are subdivided into slots that correspond to a half-track in
    that slice."""
    def __init__(self, theCpsS):
        """Ctor with a list of CurvePlotScale objects (can be unsorted)."""
        self._curvePlotScaleS = sorted(theCpsS)
        # Find out which half track indexes have curves so we can create a
        # population template. We thus only know half-tracks where curves start
        self._htIdxSet = set()
        for cID, htStart, htSpan in self._curvePlotScaleS:
            for h in range(htStart, htStart+htSpan):
                self._htIdxSet.add(h)
        # Map of {htSlot : boolean, ...} as to whether a slot is filled or not
        self._htIdxMap = {}
        self.reset()

    def reset(self):
        """Clears the slot map for the current slice."""
        self._htIdxMap = {}.fromkeys(self._htIdxSet, False)
    
    def canFit(self, theCps):
        """Returns True if I can fit the CurvePlotScale object in the current slice."""
        for h in range(theCps.halfTrackStart, theCps.halfTrackStart+theCps.halfTracks):
            assert(h in self._htIdxMap)
            if self._htIdxMap[h]:
                # Slot already occupied
                return False
        return True
        
    def fit(self, theCps):
        """Populates slots from a CurvePlotScale, caller should call canFit() first."""
        assert(self.canFit(theCps))
        for h in range(theCps.halfTrackStart, theCps.halfTrackStart+theCps.halfTracks):
            assert(h in self._htIdxMap)
            assert(self._htIdxMap[h] is False)
            self._htIdxMap[h] = True
    
    def genScaleSliceCurve(self):
        """Generates a ordered list of ScaleSliceCurve objects laid out in a 'nice' fashion."""
        # The vertical slice, 0 is nearest the log itself.
        scaleSlice = 0
        myCpsS = self._curvePlotScaleS[:]
        while len(myCpsS) > 0:
            self.reset()
            # Fit a curve in the slice
            i = 0
            # First curve in this slice should always fit
            assert(self.canFit(myCpsS[0])), \
                'CurvePlotScaleSlotMap {!r:s} can not fit first curve' \
                ' remaining in list.'.format(self._htIdxMap)
            while i < len(myCpsS):
                if self.canFit(myCpsS[i]):
                    myCps = myCpsS.pop(i)
                    # Pack the slice with these curve slots
                    self.fit(myCps)
                    yield ScaleSliceCurve(scaleSlice,
                                          myCps.name,
                                          myCps.halfTrackStart,
                                          myCps.halfTracks)
                else:
                    i += 1
            scaleSlice += 1
            
#############################################################################
# End: Code that handles the curve scales (or legends) that appear at top and
# bottom of the log.
#############################################################################

class PlotRoll(object):
    """Describes the plot canvas as if it were a roll of paper.
    This can compute the various dimensions and positions of plot panes:
    
    Legend:
    
    * ``...`` - The plot within margins.
    * ``***`` - Optional headers and trailers.
    * ``+++`` - The upper and lower headers for scales (legends).
    * ``^^^`` - The main plotting area.
    
    In this diagram adjacent lines overlay::
    
        |--------------------------------------------------------------------|
        |                           Plot margin                              |
        |   ..............................................................   |
        |   .************************************************************.   |
        |   .*                                                          *.   |
        |   .*            Optional header e.g. API header               *.   |
        |   .*                                                          *.   |
        |   .************************************************************.   |
        |   .++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.   |
        |   .+                                                          +.   |
        |   .+       Scales (legends) at the top of the plot.           +.   |
        |   .+                                                          +.   |
        |   .++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.   |
        |   .^^^^^^^^^^^^^^^ -- X Stop (if up log) -- ^^^^^^^^^^^^^^^^^^^.   |
        |   .^                                                          ^.   |
        |   .^                                                          ^.   |
        |   .^                                                          ^.   |
        |   .^                  Main log plotted here                   ^.   |
        |   .^                                                          ^.   |
        |   .^                                                          ^.   |
        |   .^                                                          ^.   |
        |   .^^^^^^^^^^^^^^^^ -- X Start (if up log) -- ^^^^^^^^^^^^^^^^^.   |
        |   .++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.   |
        |   .+                                                          +.   |
        |   .+       Scales (legends) at the bottom of the plot.        +.   |
        |   .+                                                          +.   |
        |   .++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.   |
        |   .************************************************************.   |
        |   .*                                                          *.   |
        |   .*         Optional trailer e.g. calibration record         *.   |
        |   .*                                                          *.   |
        |   .************************************************************.   |
        |   ..............................................................   |
        |                           Plot margin                              |
        |--------------------------------------------------------------------|
    
    """
    def __init__(self,
            theXStart,
            theXStop,
            theScale,
            theLegendDepth,
            theHeadDepth=Coord.Dim(0, 'in'),
            theTailDepth=Coord.Dim(0, 'in'),
            plotUp=True,
            theWidth=PlotConstants.STANDARD_PAPER_WIDTH,
            theMargin=PlotConstants.MarginQtrInch):
        """Initialise with:
        
        *theXStart*
            The X start position as an ``EngVal``.
        *theXStop*
            The X stop position as an ``EngVal``.
        *theScale*
            The plot scale as a number.
        *theLegendDepth*
            A ``Coord.Dim()`` that is the depth of the scales used in
            the header and footer.
        *theHeadDepth*
            A ``Coord.Dim()`` that is the depth of any log header.
        *theTailDepth*
            A ``Coord.Dim()`` that is the depth of any log trailer.
        *plotUp, bool*
            True if X start is at the bottom of the main pane.
        *theWidth*
            The absolute width of the plot as a ``Coord.Dim()``.
        *theMargin*
            A ``Coord.Margin()`` that describes the untouchable edges of the plot.
        """
        self._xStart = theXStart
        self._xStop = theXStop
        # For traditional up log this will be negative
        self._xSpan = self._xStop - self._xStart
        self._legendDepth = theLegendDepth
        self._headDepth = theHeadDepth
        self._tailDepth = theTailDepth
        self._isUpPlot = plotUp
        self._rollWidth = theWidth
        self._rollMargin = theMargin
        # The main pane depth as a Coord.Dim() from (theXStart, theXStop) as EngVal's.
        assert(theScale != 0)
#        print(self._xSpan)
#        print(self._xSpan.uom)
#        print(self._xSpan.newEngValInUnits(PlotConstants.DEFAULT_PLOT_LIS_UNITS))
#        print(self._xSpan.newEngValInUnits(PlotConstants.DEFAULT_PLOT_LIS_UNITS).value)
        try:
            # This might raise if units are something silly like b'    '
            self._plotDepth = Coord.Dim(
                abs((self._xSpan).newEngValInUnits(PlotConstants.DEFAULT_PLOT_LIS_UNITS).value) / theScale,
                PlotConstants.DEFAULT_PLOT_UNITS,
            )
        except Units.ExceptionUnits as err:
            raise ExceptionTotalDepthPlotRoll('PlotRoll.__init__(): {:s}'.format(str(err)))
        # A Coord.Dim() for the depth of the overall plot.
        self._rollDepth = self._rollMargin.top \
                            + self._headDepth \
                            + self._legendDepth \
                            + self._plotDepth \
                            + self._legendDepth \
                            + self._tailDepth \
                            + self._rollMargin.bottom
        
    @property
    def viewBox(self):
        """The overall size of the plot."""
        return Coord.Box(self._rollWidth, self._rollDepth)
    
    @property
    def width(self):
        """The overall width as a number in PlotConstants.DEFAULT_PLOT_UNITS."""
        return self._rollWidth.convert(PlotConstants.DEFAULT_PLOT_UNITS).value
        
    @property
    def depth(self):
        """The overall width as a number in PlotConstants.DEFAULT_PLOT_UNITS."""
        return self._rollDepth.convert(PlotConstants.DEFAULT_PLOT_UNITS).value
        
    @property
    def widthDim(self):
        """The overall width as a Coord.Dim()."""
        return self._rollWidth.convert(PlotConstants.DEFAULT_PLOT_UNITS)
        
    @property
    def depthDim(self):
        """The overall width as a Coord.Dim()."""
        return self._rollDepth.convert(PlotConstants.DEFAULT_PLOT_UNITS)
    
    @property
    def trackTopLeft(self):
        """"A Coord.Pt() that is the top left of the pane that tracks are
        plotted within."""
        return Coord.Pt(
            self._rollMargin.left,
            self._rollMargin.top + self._legendDepth + self._headDepth,
        )
    
    @property
    def mainPanePlotDepth(self):
        """The depth of the plot of the main pane as a Coord.Dim()."""
        return self._plotDepth
    
    @property
    def availableWidth(self):
        """The available width inside the margins."""
        return self._rollWidth - self._rollMargin.left - self._rollMargin.right
    
    def retHeadPane(self):
        """Returns a pair of top-left Coord.Pt(), Coord.Box() for the top
        header where the header goes."""
        retPt = Coord.Pt(self._rollMargin.left, self._rollMargin.top)
        retBox = Coord.Box(self.availableWidth, self._headDepth)
        return retPt, retBox

    def retLegendPane(self, isTop):
        """Returns a pair of top-left Coord.Pt(), Coord.Box() for the top or bottom
        legend pane where the scales go."""
        if isTop:
            retPt = Coord.Pt(
                self._rollMargin.left,
                self._rollMargin.top + self._headDepth,
            )
        else:
            retPt = Coord.Pt(
                self._rollMargin.left,
                self._rollDepth - self._rollMargin.bottom - self._tailDepth - self._legendDepth,
            )
        retBox = Coord.Box(self.availableWidth, self._legendDepth)
        return retPt, retBox

    def retMainPane(self):
        """Returns a pair of top-left Coord.Pt(), Coord.Box() for the pane
        where the main log goes."""
        retBox = Coord.Box(
            # Width
            self.availableWidth,
            # Depth
            self._plotDepth,
        )
        return self.trackTopLeft, retBox

    def retTailPane(self):
        """Returns a pair of top-left Coord.Pt(), Coord.Box() for the pane
        where the trailer goes."""
        retPt = Coord.Pt(
            self._rollMargin.left,
            self._rollDepth - self._rollMargin.bottom - self._tailDepth)
        retBox = Coord.Box(
            # Width
            self.availableWidth,
            # Depth
            self._tailDepth,
        )
        return retPt, retBox

    def xDepth(self, theX):
        """Returns a Coord.Dim() on the main pane that corresponds to theX as
        a number or an EngVal. If this is a number it is expected to be in the
        units of the xStart/xStop in the constructor."""
        xProp = (theX - self._xStart) / self._xSpan
#         print('theX', theX, 'self._xStart', self._xStart, 'self._xSpan',
#               self._xSpan, 'xProp', xProp)
        # Note the contract we have with EngVal, the calculations might have
        # resulted in xProp being an EngVal.
        if self._isUpPlot:
            return self._rollMargin.top + self._headDepth \
                + self._legendDepth + self._plotDepth.scale(1.0 - xProp.value)
        return self._rollMargin.top + self._headDepth + self._legendDepth \
            + self._plotDepth.scale(xProp.value)
        
    def polyLinePt(self, theX, theTracPos):
        """Returns a Coord.Pt from theX axis value (or EngVal) and theTracPos
        that is a value in DEFAULT_PLOT_UNITS, for example given by a
        tracValueFunction.
        The Coord.Pt() will be scaled by VIEW_BOX_UNITS_PER_PLOT_UNITS."""
        tracDim = self._rollMargin.left
        tracDim += Coord.Dim(theTracPos, PlotConstants.DEFAULT_PLOT_UNITS)
        return Coord.Pt(
            tracDim.scale(PlotConstants.VIEW_BOX_UNITS_PER_PLOT_UNITS),
            self.xDepth(theX).scale(PlotConstants.VIEW_BOX_UNITS_PER_PLOT_UNITS)
        )
    
    def retMainPaneStart(self):
        """Returns the start Coord.Pt() for the pane where the main log goes.
        For and upPlot this will be pane-bottom-left, for a downPlot this will
        be pane-top-left."""
        depthDim = self._rollMargin.top + self._headDepth + self._legendDepth
        if self._isUpPlot:
            depthDim += self._plotDepth
        return Coord.Pt(self._rollMargin.left, depthDim)

class Plot(object):
    """Defines a plot configuration. The basic architecture follows the
    data. The constructor takes all the static data, typically this can
    be obtained from the PRES and FILE tables.
    The dynamic (or user selected data) is passed in to plotLogPassLIS(). This is
    intended as a single Plot object might be used multiple times (e.g. on
    'scroll up')."""
    #: Title font
    TITLE_FONT_FAMILY = "Verdana"
    #: Title font size
    TITLE_FONT_SIZE = 10
    # Constants to do with the legend (scales).
    #: How much depth to give each legend (curve scale) at the top and
    #: bottom of the log
    LEGEND_DEPTH_PER_CURVE = Coord.Dim(0.5, 'in')
    #: How much spare depth to give over the legend (curve scale) sections at
    #: the top and bottom of the log
    LEGEND_DEPTH_SPARE = Coord.Dim(0.5, 'in')
    #: Where the curve line in the legend section appears as a proportion of
    #: LEGEND_DEPTH_PER_CURVE
    LEGEND_HORIZONTAL_LINE_DEPTH_PROPORTION = 5/8
    #: Arrow heads on legend scales
    LEGEND_ARROW_DISPLAY = True
    #: Arrow head width on legend scales
    LEGEND_ARROW_WIDTH = Coord.Dim(0.08, 'in')
    #: Arrow head depth on legend scales
    LEGEND_ARROW_DEPTH = Coord.Dim(0.04, 'in')
    #: Arrow head line width on legend scales
    LEGEND_ARROW_WIDTH_PX = 0.75
    #: Legend font.
    CURVE_LEGEND_FONT_FAMILY = "Courier"
    #: Legend font family.
    CURVE_LEGEND_FONT_SIZE = 9
    #: This is just a very small margin to provide a tiny bit of whitespace
    #: between elements in certain places
    MICRO_MARGIN = Coord.Dim(0.04, 'in')
    #: Maximum number of backup lines that can cross a single track in a single X step
    #: See the source of ``_filterCrossLineList()`` for an explanation.
    MAX_BACKUP_TRACK_CROSSING_LINES = 4
    
    def __init__(self, theFilmCfg, thePresCfg, theScale=0):
        # A FILMCfg.FilmCfg() object
        self._filmCfg = theFilmCfg
        # A PRESCfg.PresCfg() object
        self._presCfg = thePresCfg
        # Scale override if non-zero
        self._scale = theScale
        if not isinstance(theScale, (int, float)):
            raise ExceptionTotalDepthLISPlot(
                'Plot.__init__(): Scale override of type {!r:s} is not'
                ' a number.'.format(type(self._scale)))
        if self._scale < 0:
            raise ExceptionTotalDepthLISPlot(
                'Plot.__init__(): Scale override {:g} is < 0'.format(self._scale))
                
    def xScale(self, theFilmID):
        """Returns the X axis scale as a number given the FILM ID."""
        if self._scale != 0:
            assert(self._scale > 0)
            return self._scale
        return self._filmCfg[theFilmID].xScale
    
    def _openOutFile(self, theFp):
        """Returns a writable file-like object. This creates the enclosing
        directory if necessary."""
        d = os.path.dirname(theFp)
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        return open(theFp, 'w')
    
    def filmIdS(self):
        """Returns an unordered list of FILM IDs."""
        return self._filmCfg.keys()

    def _insertCommentInSVG(self, xS, cmt, level):
        assert(level in range(len(COMMENTS_IN_SVG_SECTION_LEVEL_TUPLE)))
        if COMMENTS_IN_SVG_SECTION:
            myCmt = '\n%s\n' % cmt.center(COMMENTS_IN_SVG_SECTION_WIDTH,
                                          COMMENTS_IN_SVG_SECTION_LEVEL_TUPLE[level])
            xS.comment(myCmt) 
    
    #=============================
    # Section: Plotting LIS files.
    #=============================   
    def hasDataToPlotLIS(self, theLogPass, theFilmId):
        """Returns True if a call to plotLogPassLIS() is likely to lead to some
        plot data being produced."""
        if theLogPass.totalFrames == 0:
            # No frames no data...
            logging.info('Plot.hasDataToPlotLIS(): No frames no data...')
            return False
        if not self._presCfg.hasCurvesForDest(theFilmId):
            # No curves for this ID
            logging.info(
                'Plot.hasDataToPlotLIS():'
                ' No curves for destination "{:s}"'.format(str(theFilmId))
            )
            return False
        # Now get the list of OUTP and check that at least one is in LogPass
        myOutS = self._retOutputChIDs(theFilmId)
        logging.info(
            'Plot.hasDataToPlotLIS():'
            '   Available outputs: {:s}'.format(str(myOutS))
        )
        logging.info(
            'Plot.hasDataToPlotLIS():'
            ' LogPass._chMap keys: {:s}'.format(str(theLogPass._chMap.keys()))
        )
        for anO in myOutS:
#            logging.info('Plot.hasDataToPlotLIS(): Testing output "{:s}"'.format(str(anO)))
            # If an output is in the LogPass we are good to go
            if theLogPass.hasOutpMnem(anO):
                return True
        logging.info(
            'Plot.hasDataToPlotLIS():'
            ' No outputs for destination "{:s}"'.format(str(theFilmId)))
        return False
        
    def plotLogPassLIS(self,
                    theLisFile,     # LIS specific
                    theLogPass,     # LIS specific
                    theXStart,
                    theXStop,
                    theFilmId,
                    theFpOut,
                    frameStep=1,
                    title="",
                    lrCONS=None,    # LIS specific
                    timerS=None,
                ):
        """Plot a part of a LogPass and returns a list of Channel IDs plotted.
                
        *theLisFile*
            The LIS File object.
        
        *theLogPass*
            A ``LogPass`` object, the FrameSet will be populated here.
        
        *theXStart*
            The start X axis position as an ``EngVal``.
        
        *theXStop*
            The stop X axis position as an ``EngVal``.
        
        *theFilmId*
            The ID of the output device from the film table
        
        *theFpOut*
            A file path for the output SVG.
        
        *frameStep*
            Integer number of frame steps, 1 is all frames.
        
        *title*
            A string for the title that will appear in ``LEGEND_DEPTH_SPARE``
        
        *lrCONS*
            A ``CONS`` Logical Record that will be used to plot an API header in SVG.
        
        *timerS*
            Optional ``ExecTimer.ExecTimerList`` for performance measurement.
        
        TODO: If title is empty do not use the space ``self.LEGEND_DEPTH_SPARE``
        """
        retVal = (None, None)
        if not self.hasDataToPlotLIS(theLogPass, theFilmId):
            logging.info(
                'Plot.plotLogPassLIS():'
                ' Has no data to plot for destination {:s}'.format(theFilmId)
            )
            return retVal
        self._incTimers(timerS, None, 'Loading FrameSet')
        # Get the PhysFilmCfg that corresponds to theFilmId, do this first as
        # may raise KeyError.
        myPhsFiCf = self._filmCfg[theFilmId]
        myLisSize = self._loadFrameSet(theLisFile, theLogPass, theXStart,
                                       theXStop, theFilmId, frameStep)
        logging.info(
            'Plot.plotLogPassLIS(): LogPass now:\n{:s}'.format(
                theLogPass.longStr()
            )
        )
        logging.info(
            'Plot.plotLogPassLIS(): FrameSet now:\n{:s}'.format(
                theLogPass.frameSetLongStr()
            )
        )
        self._incTimers(timerS, myLisSize, 'Initialising LIS plot')
        # We need to assess the header depth which means sorting out scales
        # (legends) at each end of the plot. Get a list of ScaleSliceCurve() objects
        mySscS = self._retCurvePlotScaleOrder(theFilmId, theLogPass)
        # Create a PlotRoll that is of the overall size of the plot
        if lrCONS is not None:
            myLogHeader = LogHeader.APIHeaderLIS(isTopOfLog=True)
            myHeadDepth = myLogHeader.size().depth
        else:
            myLogHeader = None
            myHeadDepth = Coord.Dim(0.0, 'in')
        myPlRo = PlotRoll(
            theXStart,
            theXStop,
            self.xScale(theFilmId),
            # theLegendDepth
            self.LEGEND_DEPTH_SPARE+self._retPlotScaleDepth(mySscS),
            # theHeadDepth
            myHeadDepth,
            # theTailDepth
            Coord.Dim(0.0, 'in'),
            plotUp=theLogPass.dfsr.ebs.logUp,
            theWidth=PlotConstants.STANDARD_PAPER_WIDTH,
            theMargin=PlotConstants.MarginQtrInch,
        )
        logging.info(
            'Plot.plotLogPassLIS():'
            ' Plotting SVG width={!r:s} depth={!r:s} ...'.format(myPlRo.widthDim,
                                                                 myPlRo.depthDim)
        )
        # Set up viewBox and viewPort
        myRootAttrs = {
            'viewBox'  : "0 0 {:.3f} {:.3f}".format(
                PlotConstants.VIEW_BOX_UNITS_PER_PLOT_UNITS*myPlRo.width,
                PlotConstants.VIEW_BOX_UNITS_PER_PLOT_UNITS*myPlRo.depth,
            ),
        }
        myViewPort = Coord.Box(width=myPlRo.widthDim, depth=myPlRo.depthDim)
        self._incTimers(timerS, 0, None)
        with SVGWriter.SVGWriter(theFpOut, myViewPort, rootAttrs=myRootAttrs) as xS:
            # Optionally plot API header
            if myLogHeader is not None:
                assert(lrCONS is not None)
                self._insertCommentInSVG(xS, ' API Header START ', 0)
                self._incTimers(timerS, 0, 'Plotting API Header')
                logging.info('Plot.plotLogPassLIS(): Plotting Tracks...')
                myLogHeader.plot(xS, myPlRo.retHeadPane()[0], lrCONS)
                self._insertCommentInSVG(xS, ' API Header END ', 0)
            # Plot tracks
            self._incTimers(timerS, 0, 'Plotting Tracks')
            logging.info('Plot.plotLogPassLIS(): Plotting Tracks...')
            self._insertCommentInSVG(xS, ' Plot Tracks START ', 0)
            for tIdx in range(len(myPhsFiCf)):
                self._insertCommentInSVG(xS, ' Track {:d} START '.format(tIdx), 1)
                myPhsFiCf[tIdx].plotSVG(myPlRo.trackTopLeft, myPlRo.mainPanePlotDepth, xS)
                self._insertCommentInSVG(xS, ' Track {:d} END '.format(tIdx), 1)
            self._insertCommentInSVG(xS, ' Plot Tracks END ', 0)
            # Plot XGrid
            self._incTimers(timerS, 0, 'Plotting XGrid')
            logging.info('Plot.plotLogPassLIS(): Plotting XGrid...')
            self._insertCommentInSVG(xS, ' Plot X Grid START ', 0)
            self._plotXGrid(myPhsFiCf, theXStart, theXStop, xS, myPlRo.retMainPaneStart())
            self._insertCommentInSVG(xS, ' Plot X Grid END ', 0)
            # Plot scales at header and footer
            self._incTimers(timerS, 0, 'Plotting scales (legends)')
            logging.info('Plot.plotLogPassLIS(): Plotting Scales (legends)...')
            self._insertCommentInSVG(xS, ' Plot Legends START ', 0)
            self._plotScales(theFilmId, theLogPass, myPlRo, xS, mySscS, title)
            self._insertCommentInSVG(xS, ' Plot Legends END ', 0)
            # Plot Curves
            self._incTimers(timerS, 0, 'Plotting curves')
            logging.info('Plot.plotLogPassLIS(): Plotting Curves...')
            self._insertCommentInSVG(xS, ' Plot Curves START ', 0)
            retVal = self._plotCurves(theFilmId, theLogPass, myPlRo, xS)
            self._insertCommentInSVG(xS, ' Plot Curves END ', 0)
            # End timer
            self._incTimers(timerS, myLisSize, None)
        return retVal
    #=========================
    # End: Plotting LIS files.
    #=========================   
    
    #=============================
    # Section: Plotting LAS files.
    #=============================   
    def hasDataToPlotLAS(self, theLasFile, theFilmId):
        """Returns True if a call to plotLogPassLIS() is likely to lead to some
        plot data being produced."""
        if theLasFile.numFrames() == 0:
            # No frames no data...
            logging.info('Plot.hasDataToPlotLAS(): No frames no data...')
            return False
        if not self._presCfg.hasCurvesForDest(theFilmId):
            # No curves for this ID
            logging.info(
                'Plot.hasDataToPlotLAS():'
                ' No curves for destination "{:s}"'.format(str(theFilmId))
            )
            return False
        # Now get the list of OUTP and check that at least one is in LogPass
        myOutS = self._retOutputChIDs(theFilmId)
        logging.debug('Plot.hasDataToPlotLAS(): Presentation outputs:\n{:s}'.format(
            str(sorted(list(myOutS)))
        ))
        logging.debug('Plot.hasDataToPlotLAS(): Available curves:\n{:s}'.format(
            str(sorted(list(theLasFile.curveMnems())))
        ))
        for anO in myOutS:
            logging.debug(
                'Plot.hasDataToPlotLAS(): Testing output "{:s}"'.format(repr(anO))
            )
            # If an output is in the LogPass we are good to go
            if theLasFile.hasOutpMnem(anO):
                return True
        logging.info(
            'Plot.hasDataToPlotLAS():'
            ' No outputs for destination "{:s}"'.format(str(theFilmId))
        )
        return False
        
    def plotLogPassLAS(self,
                    theLasFile,     # LAS specific
                    theXStart,
                    theXStop,
                    theFilmId,
                    theFpOut,
                    frameStep=1,
                    title="",
                    plotHeader=False,
                    timerS=None,
                ):
        """Plot a part of a LogPass and returns a list of Channel IDs plotted.
        
        theLisFile - The LIS File object.
        
        theLogPass - A LogPass object, the FrameSet will be populated here.
        
        theXStart - The start X axis position as an EngVal.
        
        theXStop - The stop X axis position as an EngVal.
        
        theFilmId - The ID of the output device from the film table
        
        theFpOut - A file path for the output SVG.
        
        frameStep - Integer number of frame steps, 1 is all frames.
        
        title - A string for the title that will appear in LEGEND_DEPTH_SPARE
        
        lrCONS - A CONS Logical Record that will be used to plot an API header in SVG.
        
        timerS - Optional ExecTimer.ExecTimerList for performance measurement.
        
        TODO: If title is empty do not use the space self.LEGEND_DEPTH_SPARE
        """
        retVal = (None, None)
        if not self.hasDataToPlotLAS(theLasFile, theFilmId):
            logging.info('Plot.plotLogPassLIS(): Has no data to plot for destination {:s}'.format(theFilmId))
            return retVal
        # We use 6 to measure effective ammount of work as a compromise between
        # LIS floats (4 bytes) and IEEE floats (8 bytes) 
        self._incTimers(timerS, None, 'Initialising LAS plot: "{:s}"'.format(theFilmId))
        # Get the PhysFilmCfg that corresponds to theFilmId, do this first as
        # may raise KeyError.
        myPhsFiCf = self._filmCfg[theFilmId]
        # We need to assess the header depth which means sorting out scales
        # (legends) at each end of the plot. Get a list of ScaleSliceCurve() objects
        mySscS = self._retCurvePlotScaleOrder(theFilmId, theLasFile)
        if plotHeader:
            myLogHeader = LogHeader.APIHeaderLAS(isTopOfLog=True)
            myHeadDepth = myLogHeader.size().depth
        else:
            myLogHeader = None
            myHeadDepth = Coord.Dim(0.0, 'in')
        # Create a PlotRoll that is of the overall size of the plot
        myPlRo = PlotRoll(
            theXStart,
            theXStop,
            self.xScale(theFilmId),
            # theLegendDepth
            self.LEGEND_DEPTH_SPARE+self._retPlotScaleDepth(mySscS),
            # theHeadDepth
            myHeadDepth,
            # theTailDepth
            Coord.Dim(0.0, 'in'),
            plotUp=not theLasFile.logDown(),
            theWidth=PlotConstants.STANDARD_PAPER_WIDTH,
            theMargin=PlotConstants.MarginQtrInch)
        logging.info(
            'Plot.plotLogPassLAS(): Plotting SVG width={!r:s} depth={!r:s} ...'.format(myPlRo.widthDim, myPlRo.depthDim)
        )
        # Set up viewBox and viewPort
        myRootAttrs = {
            'viewBox'  : "0 0 {:.3f} {:.3f}".format(
                PlotConstants.VIEW_BOX_UNITS_PER_PLOT_UNITS*myPlRo.width,
                PlotConstants.VIEW_BOX_UNITS_PER_PLOT_UNITS*myPlRo.depth,
            ),
        }
        myViewPort = Coord.Box(width=myPlRo.widthDim, depth=myPlRo.depthDim)
        self._incTimers(timerS, 0, None)
        with SVGWriter.SVGWriter(self._openOutFile(theFpOut), myViewPort, rootAttrs=myRootAttrs) as xS:
            # Optionally plot API header
            if myLogHeader is not None:
                self._insertCommentInSVG(xS, ' API Header START ', 0)
                self._incTimers(timerS, 0, 'Plotting API Header')
                logging.info('Plot.plotLogPassLAS(): Plotting Tracks...')
                myLogHeader.plot(xS, myPlRo.retHeadPane()[0], theLasFile)
                self._insertCommentInSVG(xS, ' API Header END ', 0)
            # Plot tracks
            self._incTimers(timerS, 0, 'Plotting Tracks')
            logging.info('Plot.plotLogPassLAS(): Plotting Tracks...')
            self._insertCommentInSVG(xS, ' Plot Tracks START ', 0)
            for tIdx in range(len(myPhsFiCf)):
                self._insertCommentInSVG(xS, ' Track {:d} START '.format(tIdx), 1)
                myPhsFiCf[tIdx].plotSVG(myPlRo.trackTopLeft, myPlRo.mainPanePlotDepth, xS)
                self._insertCommentInSVG(xS, ' Track {:d} END '.format(tIdx), 1)
            self._insertCommentInSVG(xS, ' Plot Tracks END ', 0)
            # Plot XGrid
            self._incTimers(timerS, 0, 'Plotting XGrid')
            logging.info('Plot.plotLogPassLAS(): Plotting XGrid...')
            self._insertCommentInSVG(xS, ' Plot X Grid START ', 0)
            self._plotXGrid(myPhsFiCf, theXStart, theXStop, xS, myPlRo.retMainPaneStart())
            self._insertCommentInSVG(xS, ' Plot X Grid END ', 0)
            # Plot scales at header and footer
            self._incTimers(timerS, 0, 'Plotting scales (legends)')
            logging.info('Plot.plotLogPassLAS(): Plotting Scales (legends)...')
            self._insertCommentInSVG(xS, ' Plot Legends START ', 0)
            self._plotScales(theFilmId, theLasFile, myPlRo, xS, mySscS, title)
            self._insertCommentInSVG(xS, ' Plot Legends END ', 0)
            # Plot Curves
            self._incTimers(timerS, 0, 'Plotting curves')
            logging.info('Plot.plotLogPassLAS(): Plotting Curves...')
            self._insertCommentInSVG(xS, ' Plot Curves START ', 0)
            retVal = self._plotCurves(theFilmId, theLasFile, myPlRo, xS)
            self._insertCommentInSVG(xS, ' Plot Curves END ', 0)
            # End timer
            self._incTimers(timerS, theLasFile.numDataPoints() * 6, None)
        return retVal
    
    def _incTimers(self, theTim, theSize=0, theNewMsg=None):
        """Stop the existing timer and load another one.
        If theTim is None then this is a NOP.
        If theSize is not None then a stopTimer() is issued with that size.
        If theNewMsg is not None then a new timer is started.
        """
        if theTim is not None:
            if theSize is not None or theTim.has_active_timer:
                theTim.stop(theSize)
            if theNewMsg is not None:
                theTim.add_timer(theNewMsg)

    def _retOutputChIDs(self, theFilmId):
        """Returns a list of output mnem that are needed for plotting. May raise KeyError."""
        # Get the PhysFilmCfg that corresponds to theFilmId, may raise KeyError.
        myPhsFiCf = self._filmCfg[theFilmId]
        # Get the list of output curves from the presentation table
        # Will raise KeyError if not self._presCfg.hasCurvesForDest(myPhsFiCf.name):
        return self._presCfg.outpChIDs(myPhsFiCf.name)
    
#    def _outpCurveIDs(self, theFilmId, theOutpId):
#        # Get the PhysFilmCfg that corresponds to theFilmId, may raise KeyError.
#        myPhsFiCf = self._filmCfg[theFilmId]
#        # Get the list of output curves from the presentation table
#        return self._presCfg.outpCurveIDs(myPhsFiCf.name, theOutpId)
        
    def _loadFrameSet(self, theLisFile, theLogPass, theXStart, theXStop, theFilmId, frameStep=1):
        """Loads the LogPass FrameSet with the output channels that are needed for the plot.
        theLisFile is a File object, theLogPass is a LogPass, theXStart/Stop are
        EngVal objects, theFilmId is a Mnem.
        Returns number of LIS bytes read."""
        # Load the FrameSet
        logging.info('Plot._loadFrameSet(): Loading LogPass FrameSet...')
        myChIdS = [m for m in self._retOutputChIDs(theFilmId) if theLogPass.hasOutpMnem(m)]
        logging.info('Plot._loadFrameSet(): X axis from="{:s}" to="{:s}" frame step={:d}. Channel IDs[{:d}]:\n{:s}'.format(
                str(theXStart),
                str(theXStop),
                frameStep,
                len(myChIdS),
                pprint.pformat(list(myChIdS), indent=4, width=80),
            )
        )
        theLogPass.setFrameSetChX(theLisFile, myChIdS, theXStart, theXStop, frStep=frameStep)
        logging.info('Plot._loadFrameSet(): Loading LogPass FrameSet DONE...')
        return theLogPass.numBytes
    
    #============================================
    # Section: Plotting the X axis grid and text.
    #============================================
    def _plotXGrid(self, thePhsFiCf, xStart, xStop, xS, refPt):
        myXg = XGrid.XGrid(self.xScale(thePhsFiCf.name))#thePhsFiCf.xScale)
        self._plotXGridLines(thePhsFiCf, myXg, xStart, xStop, xS, refPt)
        self._plotXGridAlpha(thePhsFiCf, myXg, xStart, xStop, xS, refPt)
        
    def _plotXGridLines(self, thePhsFiCf, theXg, xStart, xStop, xS, refPt):
        """Plot an XCrid.XGrid() object to the SVG stream xS and start point
        startPt (Coord.Pt() object), from EngVal xStart to EngVal xStop."""
        # Plot depth lines
        #myXInc = (xStart < xStop)
#        for t in thePhsFiCf.genTracks():
#            print('TRACE: _plotXGridLines():', t, 'Grid:', t.hasGrid)
        for pos, stroke in theXg.genXAxisRange(xStart, xStop):
            for t in thePhsFiCf.genTracks():
                if t.plotXLines:
                    with SVGWriter.SVGLine(
                            xS,
                            Coord.Pt(t.left+refPt.x, refPt.y+pos),
                            Coord.Pt(t.right+refPt.x, refPt.y+pos),
                            attrs=Stroke.retSVGAttrsFromStroke(stroke)
                        ):
                        pass

    def _plotXGridAlpha(self, thePhsFiCf, theXg, xStart, xStop, xS, refPt):
        # Plot depth text
        textAttrs = {
            'text-anchor'       : 'end',
            'dominant-baseline' : 'middle',
        }
        for pos, val in theXg.genXAxisTextRange(xStart, xStop):
            for t in thePhsFiCf.genTracks():
                if t.plotXAlpha:
                    myPt = Coord.Pt(
                        t.right+refPt.x-Coord.Dim(0.05, 'in'),
                        refPt.y+pos+Coord.Dim(0.05, 'in'),
                    )
                    with SVGWriter.SVGText(xS, myPt, 'Courier', 12, textAttrs):
                        xS.characters(str(val))
    #============================================
    # End: Plotting the X axis grid and text.
    #============================================
    
    #================================================================
    # Section: Plotting the scales (legends) at each end of the plot.
    #================================================================
    def _plotScales(self, theFilmID, theLpData, thePlotRoll, xS, theSscS, title):
        #                 theFilmId, theLogPass, myPlRo, xS, mySscS, title
        """Plots the scales (legend) at the top and bottom of the log.
        theFilmID - The ID of the output film.
        theLpData is a LogPass or a LASFile. In any case it needs curveUnitsAsStr() implemented.
        thePlotRoll - A PlotRoll object.
        xS - The XML stream.
        theSscS - A list of ScaleSliceCurve objects obtained from _retCurvePlotScaleOrder().
        title - Text to put in the header and footer.
        """
        # NOTE: There is no point in reversing theSscS as that does not change
        # the actual slot values. So for plotting the top we invert the slot
        # value before plotting.
        # Plot bottom scale in the pane supplied by PlotRoll
        self._plotScale(theFilmID, theLpData, thePlotRoll, xS, theSscS, title, False)
        self._plotScale(theFilmID, theLpData, thePlotRoll, xS, theSscS, title, True)

    def _plotScale(self, theFilmID, theLpData, thePlotRoll, xS, theSliceCurveS, title, isTop):
        """Plots a scale (legend) at the top or bottom of the log.
        theLpData is a LogPass or a LASFile. In any case it needs curveUnitsAsStr() implemented."""
        # retHeaderPane() returns a pair of top-left Coord.Pt(), Coord.Box()
        myPt, myBox = thePlotRoll.retLegendPane(isTop=isTop)
        # Bounding box
        with SVGWriter.SVGRect(xS, myPt, myBox, {'fill' : "none", 'stroke' : "blue", 'stroke-width' : ".25",}):
            pass
        # Title text
        # Compute the text reference point, x is half myBox.width,
        # y depends on whether top or bottom
        textPt = Coord.newPt(myPt, incX=myBox.width.scale(0.5), incY=self.LEGEND_DEPTH_SPARE.scale(0.5))
        if not isTop:
            # Shift text point down for the lower header
            textPt = Coord.newPt(textPt, incX=None, incY=myBox.depth-self.LEGEND_DEPTH_SPARE)
        with SVGWriter.SVGText(xS, textPt, self.TITLE_FONT_FAMILY, self.TITLE_FONT_SIZE, {'text-anchor' : 'middle'}):
            xS.characters(title)
        # myNumSlices is only relevant when isTop is True, it allows us to
        # reverse the slice order
        myNumSlices = self._retPlotScaleNumSlices(theSliceCurveS)
        # Plot curve scales (legends)
        for aSsc in theSliceCurveS:
            # aSsc has slice curveName start span
            # Get the CurveCfg object
            assert(aSsc.curveName in self._presCfg)
            if COMMENTS_IN_SVG_TRACE: xS.comment(' Plot.Plot._plotScale() curve={:s} {:s} START'.format(aSsc.curveName.pStr(), str(isTop)))
            myCurvCfg = self._presCfg[aSsc.curveName]
            # myCurvCfg has leftP/rightP as Coord.Dim() objects and
            # myCurvCfg.trac.leftL, myCurvCfg.trac.rightL are the numeric values
            # of the scale edges
            if isTop:
                # Invert slice order for the top
                myIncY = self.LEGEND_DEPTH_PER_CURVE.scale(myNumSlices - 1 - aSsc.slice)
                myIncY += self.LEGEND_DEPTH_SPARE
            else:
                myIncY = self.LEGEND_DEPTH_PER_CURVE.scale(aSsc.slice)
            myTopLeft = Coord.newPt(
                myPt,
                incX=myCurvCfg.tracWidthData(theFilmID).leftP,
                incY=myIncY,
            )
            myWidth = myCurvCfg.tracWidthData(theFilmID).rightP - myCurvCfg.tracWidthData(theFilmID).leftP
            myDepth = self.LEGEND_DEPTH_PER_CURVE
            # Start with the three lines, two vertical and one horizontal
            myAttrs = Stroke.retSVGAttrsFromStroke(myCurvCfg.codiStroke)
            horizLineIncY = myDepth.scale(self.LEGEND_HORIZONTAL_LINE_DEPTH_PROPORTION)
            # Left vertical line
            with SVGWriter.SVGLine(
                    xS,
                    Coord.newPt(myTopLeft, incX=None, incY=None),
                    Coord.newPt(myTopLeft, incX=None, incY=myDepth),
                    attrs=myAttrs
                ):
                pass
            # Right vertical line
            with SVGWriter.SVGLine(
                    xS,
                    Coord.newPt(myTopLeft, incX=myWidth, incY=None),
                    Coord.newPt(myTopLeft, incX=myWidth, incY=myDepth),
                    attrs=myAttrs
                ):
                pass
            # Horizontal line
            with SVGWriter.SVGLine(
                    xS,
                    Coord.newPt(myTopLeft, incX=None, incY=horizLineIncY),
                    Coord.newPt(myTopLeft, incX=myWidth, incY=horizLineIncY),
                    attrs=myAttrs
                ):
                pass
            # Arrow head on the larger value
            if self.LEGEND_ARROW_DISPLAY:
#                myArrowAttrs = Stroke.retSVGAttrsFromStroke(myCurvCfg.codiStroke)
                myArrowAttrs = Stroke.retSVGAttrsFromStroke(
                    Stroke.StrokeBlackSolid._replace(width=self.LEGEND_ARROW_WIDTH_PX)
                )
                if myCurvCfg.tracValueFunction(theFilmID).leftL < myCurvCfg.tracValueFunction(theFilmID).rightL:
                    # left to right so arrow on right
                    ptA = Coord.newPt(myTopLeft, incX=myWidth, incY=horizLineIncY)
                    ptB = Coord.newPt(myTopLeft,
                                        incX=myWidth-self.LEGEND_ARROW_WIDTH,
                                        incY=horizLineIncY-self.LEGEND_ARROW_DEPTH)
                    with SVGWriter.SVGLine(xS, ptA, ptB, attrs=myArrowAttrs):
                        pass
                    ptA = Coord.newPt(ptB, incX=None, incY=self.LEGEND_ARROW_DEPTH.scale(2.0))
#                    with SVGWriter.SVGLine(xS, ptB, ptA, attrs=myArrowAttrs):
#                        pass
                    ptB = Coord.newPt(myTopLeft, incX=myWidth, incY=horizLineIncY)
                    with SVGWriter.SVGLine(xS, ptA, ptB, attrs=myArrowAttrs):
                        pass
                else:
                    # right to left so arrow on left
                    ptA = Coord.newPt(myTopLeft, incX=None, incY=horizLineIncY)
                    ptB = Coord.newPt(myTopLeft,
                                        incX=self.LEGEND_ARROW_WIDTH,
                                        incY=horizLineIncY-self.LEGEND_ARROW_DEPTH)
                    with SVGWriter.SVGLine(xS, ptA, ptB, attrs=myArrowAttrs):
                        pass
                    ptA = Coord.newPt(ptB, incX=None, incY=self.LEGEND_ARROW_DEPTH.scale(2.0))
#                    with SVGWriter.SVGLine(xS, ptB, ptA, attrs=myArrowAttrs):
#                        pass
                    ptB = Coord.newPt(myTopLeft, incX=None, incY=horizLineIncY)
                    with SVGWriter.SVGLine(xS, ptA, ptB, attrs=myArrowAttrs):
                        pass
            # Now do text: left/right/centre or in SVG speak start/end/middle
            with SVGWriter.SVGText(xS,
                                   Coord.newPt(myTopLeft, incX=self.MICRO_MARGIN, incY=myDepth.scale(1/2)),
                                   self.CURVE_LEGEND_FONT_FAMILY,
                                   self.CURVE_LEGEND_FONT_SIZE,
                                   {'text-anchor' : 'start'},
                                   ):
                xS.characters('{:g}'.format(myCurvCfg.tracValueFunction(theFilmID).leftL))
            with SVGWriter.SVGText(xS,
                                   Coord.newPt(myTopLeft, incX=myWidth-self.MICRO_MARGIN, incY=myDepth.scale(1/2)),
                                   self.CURVE_LEGEND_FONT_FAMILY,
                                   self.CURVE_LEGEND_FONT_SIZE,
                                   {'text-anchor' : 'end'},
                                   ):
                xS.characters('{:g}'.format(myCurvCfg.tracValueFunction(theFilmID).rightL))
            with SVGWriter.SVGText(xS,
                                   Coord.newPt(myTopLeft, incX=myWidth.scale(0.5), incY=myDepth.scale(1/2)),
                                   self.CURVE_LEGEND_FONT_FAMILY,
                                   self.CURVE_LEGEND_FONT_SIZE,
                                   {'text-anchor' : 'middle'},
                                   ):
                # Get the units from the LogPass, first find which OUTP drives
                # this curve
                myTxt = '{:s}'.format(myCurvCfg.mnem.pStr(strip=True))
                # Add units if present
                myUnits = theLpData.curveUnitsAsStr(myCurvCfg.outp)
                assert(myUnits is not None), 'None returned for curve: "{!r:s}"'.format(myCurvCfg.outp)
                if len(myUnits.strip()) > 0:
                    myTxt += ' [{!r:s}]'.format(myUnits)
                xS.characters(myTxt)            
            if COMMENTS_IN_SVG_TRACE: xS.comment(' Plot.Plot._plotScale() curve={!r:s} {!r:s} END'.format(aSsc.curveName.pStr(), isTop))

    def _retPlotScaleDepth(self, theSscS):
        """Returns a Coord.Dim() of the amount of space needed to plot the
        scales (legends) at each end of the plot."""
        return self.LEGEND_DEPTH_PER_CURVE.scale(self._retPlotScaleNumSlices(theSscS))

    def _retPlotScaleNumSlices(self, theSscS):
        """Returns the number of slices that make up the scales (legend) at each
        end of the log."""
        # TODO: Justify this test, should we return 0 or raise?
        if len(theSscS) == 0:
            return 0
        return 1 + max(s.slice for s in theSscS)

    def _retCurvePlotScaleOrder(self, theFilmID, theLp=None):
        """Returns an ordered list of ScaleSliceCurve() for plotting the end of
        log scales (i.e. legends) in a 'nice' way.
        Arguments are a FilmId and an optional LogPass.
        If provided the LogPass needs hasOutpMnem() implemented.
        This returned list is suitable for the bottom of the plot (i.e. slice
        increases downwards) and can be reversed for the scales at the top of
        the plot.
        The algorithm is as follows:
        1. Get a list of curve name sorted in the order largest track span first, then by name.
        2. Pop the first name off the list and plot it.
        3. Look for any spare track slots and pop/plot those.
        4. Repeat 3. until no more track slots or no more curve names that will fit.
        5. Repeat 2. until list is empty.
        """
        myCpsS = self._retCurvePlotScales(theFilmID, theLp)
#        print('_retCurvePlotScaleOrder(): myCpsS:', myCpsS)
        # Create a slot handler
        mySlotH = CurvePlotScaleSlotMap(myCpsS)
        # A list of ScaleSliceCurve objects
        return [v for v in mySlotH.genScaleSliceCurve()]

#        retSscS = []
#        print('_retCurvePlotScaleOrder(): mySlotH:', mySlotH)
#        scaleSlice = 0
#        while len(myCpsS) > 0:
#            mySlotH.reset()
#            # Fit a curve in the slice
#            i = 0
#            # First curve in this slice should always fit
#            assert(mySlotH.canFit(myCpsS[0])), 'CurvePlotScaleSlotMap {:s} can not fit first curve remaining in list.'.format(mySlotH._htIdxMap)
#            while i < len(myCpsS):
#                if mySlotH.canFit(myCpsS[i]):
#                    myCps = myCpsS.pop(i)
#                    retSscS.append(ScaleSliceCurve(scaleSlice, myCps.name, myCps.halfTrackStart, myCps.halfTracks))
#                    # Pack the slice with these curve slots
#                    mySlotH.fit(myCps)
#                else:
#                    i += 1
#            scaleSlice += 1
#        print('_retCurvePlotScaleOrder(): returns:', retSscS)
#        return retSscS

    def _retCurvePlotScales(self, theFilmID, theLp=None):
        """Returns a sorted list of CurvePlotScale objects given a FilmId and
        an optional LogPass. If provided the LogPass needs hasOutpMnem() implemented.
        If the LogPass is supplied then only curves that are created with OUTPs
        in the LogPass are included. If the LogPass is absent then all possible
        curves from the PRES sub-set corresponding to theFimID are included."""
        curvIdSet = set()
        for anO in self._retOutputChIDs(theFilmID):
            if self._presCfg.usesOutpChannel(theFilmID, anO):
                if theLp is None \
                or theLp.hasOutpMnem(anO):
                    for cur in self._presCfg.outpCurveIDs(theFilmID, anO):
                        curvIdSet.add(cur)
                else:
                    logging.debug(
                        'Plot._retCurvePlotScales() OUTP not available in'
                        ' LogPass: {!r:s}'.format(anO))
        logging.info(
            'Plot._retCurvePlotScales() OUTP\'s available in'
            ' LogPass: {!r:s}'.format(curvIdSet))
        # cpsSet is a set of curve IDs
        # Now create a list of CurvePlotScale objects and sort it
        cpsList = []        
        for curvId in curvIdSet:
            cpsList.append(
                CurvePlotScale(
                    curvId,
                    self._presCfg[curvId].tracWidthData(theFilmID).halfTrackStart,
                    self._presCfg[curvId].tracWidthData(theFilmID).halfTracks,
                )
            )
#        print('_retCurvePlotScales()', sorted(cpsList))
        return sorted(cpsList)
    #================================================================
    # End: Plotting the scales (legends) at each end of the plot.
    #================================================================
    
    #==============================
    # Section: Plotting the curves.
    #==============================
    def _plotCurves(self, theFilmID, theFrameHolder, thePlRo, xS):
        """Plots curves from a populated log pass to a SVG stream.
        theFilmID - An ID to look up in in the presentation table to see what outputs are to be plotted.
        theFrameHolder - A LogPass or LasFile object containing the frame data, expected to be pre-loaded with channels.
        thePlRo - A plot roll (i.e. canvas) describing the layout of the plot.
        xS - The SVG stream to write to.
        """
        curveS = []
        numPoints = 0
        for anO in self._retOutputChIDs(theFilmID):
            logging.debug('Plot._plotCurves(): Plotting Output "{!r:s}"...'.format(anO))
            self._insertCommentInSVG(xS, ' Output {:s} START '.format(anO.pStr()), 1)
            if self._presCfg.usesOutpChannel(theFilmID, anO):
                if theFrameHolder.hasOutpMnem(anO):
                    c, n = self._plotSingleOutput(theFilmID, anO, theFrameHolder, thePlRo, xS)
                    curveS += c
                    numPoints += n
                else:
                    logging.debug('Plot._plotCurves() omitting "{!r:s}" as not in LogPass'.format(anO))
            else:
                logging.warning('Plot._plotCurves() omitting OUTP "{!r:s}" as not used by PRES table.'.format(anO))
            self._insertCommentInSVG(xS, ' Output {:s} END '.format(anO.pStr()), 1)
        return curveS, numPoints
    
    def _plotSingleOutput(self, theFilmID, theOutpID, theFrameHolder, thePlRo, xS):
        """Takes a single OUTP and plots all curves that use it. Returns the curve IDs.
        theFilmID - The ID of self._filmCfg for this plot.
        theOutpID - The OUTP ID in the DFSR/PRES table, this must be in the LogPass and the PRES table.
        theFrameHolder - The LogPass of LasFile object with the channel data.
        thePlRo - The PlotRoll output configuration.
        xS - The SVG stream to write to. 
        """
        logging.info('Plot._plotSingleOutput(theFilmId={!r:s} theOutpId={!r:s}'.format(theFilmID, theOutpID))
        assert(self._presCfg.usesOutpChannel(theFilmID, theOutpID))
        assert(theFrameHolder.hasOutpMnem(theOutpID))
        # Given an output ID select all curve IDs and iterate through their
        # X/v points and scale them accordingly; X by the X axis scale and v by
        # the tracValueFunction() and the track dimensions. Finally assemble
        # into a SVG polyline in user units and send to the XML stream.
        #
        myCurvIdS = self._presCfg.outpCurveIDs(theFilmID, theOutpID)
        myCurvPlotS = [CurvePlotData(c, self._presCfg[c].tracValueFunction(theFilmID)) for c in myCurvIdS]
        logging.debug('Plot._plotSingleOutput: myCurvPlotS: {!r:s}'.format([str(c) for c in myCurvPlotS]))
        xPrev = None
        ptPrevS = [None] * len(myCurvIdS)
        numPoints = 0
        numMathErrors = 0
        if COMMENTS_IN_SVG_TRACE: xS.comment(' Plot._plotSingleOutput(theFilmId={!r:s} theOutpId={!r:s} '.format(theFilmID, theOutpID))
        for x, v in theFrameHolder.genOutpPoints(theOutpID):
            # If v is a null or absent value then flush the buffer and start again
            if v == theFrameHolder.nullValue:
                for cuPlot in myCurvPlotS:
                    self._flushPolyLineBuffer(cuPlot, xS)
                continue
            for cuIdx in range(len(myCurvIdS)):
                numPoints += 1
                # myCuPlot is a CurvePlotData object
                myCuPlot = myCurvPlotS[cuIdx]
                # Scale v by the track function
                try:
                    wr, pt = myCuPlot.fn.wrapPos(v)
                except PRESCfg.ExceptionLineTransBaseMath:
                    numMathErrors += 1
                else:
                    # print('Plot._plotSingleOutput(): x={:8.3f} v={:8.3f} wr={:4s} pt={:8.3f}'.format(x, v, str(wr), pt))
                    if wr != myCuPlot.prevWrap and xPrev is not None and ptPrevS[cuIdx] is not None:
                        # Interpolate wrapping
                        self._interpolateBackup(
                            myCuPlot,
                            xS,
                            thePlRo,
                            # theTwd and theLtb
                            self._presCfg[myCuPlot.id].tracWidthData(theFilmID),
                            self._presCfg[myCuPlot.id].tracValueFunction(theFilmID),
                            xPrev,
                            x,
                            pt,
                            myCuPlot.prevWrap,
                            wr,
                            theFrameHolder.xAxisUnits,
                        )
                    if not myCuPlot.fn.offScale(wr):
                        # Add to the buffer
                        myCuPlot.buffer.append(thePlRo.polyLinePt(EngVal.EngVal(x, theFrameHolder.xAxisUnits), pt))
                    myCuPlot.prevWrap = wr
                    ptPrevS[cuIdx] = pt
            xPrev = x
        logging.info('DONE: Plot._plotSingleOutput(theFilmId={!r:s} theOutpId={!r:s}'.format(theFilmID, theOutpID))
        if COMMENTS_IN_SVG_TRACE: xS.comment(' DONE: Plot._plotSingleOutput(theFilmId={!r:s} theOutpId={!r:s} '.format(theFilmID, theOutpID))
        for cuPlot in myCurvPlotS:
            self._flushPolyLineBuffer(cuPlot, xS)
        if numMathErrors > 0:
            logging.warning('Plot._plotSingleOutput(): {:d} maths errors plotting output {!r:s}'.format(numMathErrors,
                                                                                                        theOutpID))
        return myCurvIdS, numPoints
    
    def _flushPolyLineBuffer(self, theCurvPlotData, xS):
        """Flush buffer and plot the points."""
        if len(theCurvPlotData.buffer) > 0:
            if COMMENTS_IN_SVG_TRACE: xS.comment(' Plot._flushPolyLineBuffer() curve={:s}'.format(theCurvPlotData.id.pStr()))
            myAttrs = Stroke.retSVGAttrsFromStroke(self._presCfg[theCurvPlotData.id].codiStroke)
            myAttrs['fill'] = "none"
            with SVGWriter.SVGPolyline(
                    xS,
                    theCurvPlotData.buffer,
                    attrs=myAttrs):
                pass
            # Now flush the buffer
            theCurvPlotData.buffer = []
    
    def _interpolateBackup(self, theCuPlot, xS, thePlRo, theTwd, theLtb, xPrev, xNow, pNow, wrapPrev, wrapNow, theXUnits):
        """Handles the case where the curve is on a backup track.
        theTwd is a TrackWidthData object, theLtb is derived from LineTransBase.
        xPrev/xNow is the previous/current X axis value as a number. 
        pNow is the previous/current plot deflection as a number in plot units. 
        wrapPrev/wrapNow are integers (or None) of the wrap state for the curve.
        See notebook for 2011-05-13/15/16/17"""
        if COMMENTS_IN_SVG_TRACE:
            xS.comment(
                ' Plot._interpolateBackup(): xPrev={:s} xNow={:s} pNow={:s} wrapPrev={:s} wrapNow={:s} '.format(
                    str(xPrev),
                    str(xNow),
                    str(pNow),
                    str(wrapPrev),
                    str(wrapNow),
                )
            )
        # Interpolate wrapping
        polyEnd, wrapLines, polyStart = self._retInterpolateWrapPoints(
                theTwd,
                theLtb,
                xPrev=xPrev,
                xNow=xNow,
                pNow=pNow,
                wrapPrev=theCuPlot.prevWrap,
                wrapNow=wrapNow)
        # Sanity checks
        assert(polyEnd is None or len(polyEnd) == 2)
        assert(len(wrapLines) % 2 == 0)
        assert(len(polyStart) in (0, 2))
#        logging.debug('Plot._interpolateBackup()   polyEnd {:s}'.format(str(polyEnd)))
#        logging.debug('Plot._interpolateBackup() wrapLines {:s}'.format(str(wrapLines)))
#        logging.debug('Plot._interpolateBackup() polyStart {:s}'.format(str(polyStart)))
#        logging.debug('')
        if COMMENTS_IN_SVG_TRACE:
            xS.comment(' Plot._interpolateBackup()   polyEnd {:s} '.format(str(polyEnd)))
            xS.comment(' Plot._interpolateBackup() wrapLines {:s} '.format(str(wrapLines)))
            xS.comment(' Plot._interpolateBackup() polyStart {:s} '.format(str(polyStart)))
        # End existing polyline
        if polyEnd is not None:
            if COMMENTS_IN_SVG_TRACE: xS.comment(' Plot._interpolateBackup() appending as polyEnd is not None {:s}'.format(thePlRo.polyLinePt(polyEnd[0], polyEnd[1].value)))
            theCuPlot.buffer.append(thePlRo.polyLinePt(EngVal.EngVal(polyEnd[0], theXUnits), polyEnd[1].value))
        # Flush buffer
        self._flushPolyLineBuffer(theCuPlot, xS)
        if COMMENTS_IN_SVG_TRACE: xS.comment(' Plot.Plot._interpolateBackup() flushed polyline at wrap change ')
        theCuPlot.buffer = []
        # Handle crossing lines
        if COMMENTS_IN_SVG_TRACE: xS.comment(' Plot.Plot._interpolateBackup() writing crossing lines ')
        for c in range(0, len(wrapLines), 2):
            # Write a line from [c] to [c+1]
            if COMMENTS_IN_SVG_TRACE: xS.comment(' Plot._interpolateBackup() appending cross line[0] {:s}'.format(thePlRo.polyLinePt(wrapLines[c][0], wrapLines[c][1].value)))
            theCuPlot.buffer.append(thePlRo.polyLinePt(EngVal.EngVal(wrapLines[c][0], theXUnits), wrapLines[c][1].value))
            if COMMENTS_IN_SVG_TRACE: xS.comment(' Plot._interpolateBackup() appending cross line[1] {:s}'.format(thePlRo.polyLinePt(wrapLines[c+1][0], wrapLines[c+1][1].value)))
            theCuPlot.buffer.append(thePlRo.polyLinePt(EngVal.EngVal(wrapLines[c+1][0], theXUnits), wrapLines[c+1][1].value))
            self._flushPolyLineBuffer(theCuPlot, xS)
            theCuPlot.buffer = []
        if COMMENTS_IN_SVG_TRACE: xS.comment(' Plot.Plot._interpolateBackup() have written crossing lines ')
        # Now start of next polyline
        if len(polyStart) > 0:
            if COMMENTS_IN_SVG_TRACE: xS.comment(' Plot._interpolateBackup() starting new line[0] {:s}'.format(thePlRo.polyLinePt(polyStart[0][0], polyStart[0][1].value)))
            theCuPlot.buffer.append(thePlRo.polyLinePt(EngVal.EngVal(polyStart[0][0], theXUnits), polyStart[0][1].value))
            # Note: polyStart[1][1] is a number not a Dim()
            if COMMENTS_IN_SVG_TRACE: xS.comment(' Plot._interpolateBackup() starting new line[1] {:s}'.format(thePlRo.polyLinePt(polyStart[1][0], polyStart[1][1])))
            theCuPlot.buffer.append(thePlRo.polyLinePt(EngVal.EngVal(polyStart[1][0], theXUnits), polyStart[1][1]))

    def _retInterpolateWrapPoints(self, theTwd, theLtb, xPrev, xNow, pNow, wrapPrev, wrapNow):
        """This returns a set of generated points when a change in a 'wrap'
        occurs i.e. wrapPrev != wrapNow.
        theTwd is a TrackWidthData object, theLtb is derived from LineTransBase.
        xPrev/xNow is the previous/current X axis value as a number. 
        pNow is the previous/current plot deflection as a number in plot units. 
        wrapPrev/wrapNow are integers (or None) of the wrap state for the curve.
        See notebook for 2011-05-13/15/16/17
        Returns:
        (
            (x, Dim()) or None,
            an even number of points as an unbounded list of pairs [(x, Dim()), (x, Dim()), ...],
            [(x, Dim()), (x, value)],
        )
        The first point (if not None) can be added to the existing polyline
        which should be then flushed.
        The last two points can start a new polyline. Any intermediate points
        should be pairs that are crossing lines.
        The number of (x, pt) that are returned is either zero or:
        R + C*2 + S*2
        R - The number of points to add to the existing polyline (one).
        C - The number of track crossing lines. C >= 0.
        S - The number of points to add to the new polyline (0 or 1).
        i.e. If the length is, and (R,C,S) is:
        1, (1,0,0) - Add pair 0 to existing polyline and flush that polyline.
        3, (None,0,2) - Do not flush any existing polyline, start a new one with this (returning wrap).
        3, (1,0,2) - Add pair 0 to existing polyline and flush, start new polyline with 1,2.
        5, (1,2,2) - Add pair 0 to existing polyline and flush, crossing line with 1,2, start new polyline with 3,4.
        Then 7 (1,4,2), 9 (1,6,2) etc.

        An egrecious case is 300025.S03 where TNPH [V/V ]has these values:
        V: -0.078       1516301.25
        X: 450060.0     450000.0
        This is -2,527,168 wraps. NPOR is similar.
        This has to be fixed here in _retInterpolateWrapPoints() as the idea building a list of 2m cLineS and
        calling _filterCrossLineList() to filter them blows the memory.
        Here are the actual values:
        XAXIS [b'.1IN'] b'TNPH' [b'V/V ']   b'NPOR' [b'V/V ']
        450120.0 	    -0.0782128	        0.84
        450060.0 	    -0.0781904	        0.84
        450000.0 	    1.5163e+06	        2.42385e+08
        449940.0 	    0.608137	        230.553
        449880.0 	    0.359284	        0.166243
        449820.0 	    0.295198	        0.211552
        449760.0 	    0.427305	        0.427305
        """
        assert(wrapPrev != wrapNow)
        # print('TRACE:', '_retInterpolateWrapPoints(', theTwd, theLtb, xPrev, xNow, pNow, wrapPrev, wrapNow, ')')
        # assert abs(wrapPrev) < 10, 'Far too many wrapPrev'
        # assert abs(wrapNow) < 10, 'Far too many wrapNow'
        polyEnd = None
        crossLines = []
        polyNew = []
        # If both wraps off-scale then return nothing
        if theLtb.isOffScaleLeft(wrapPrev) and theLtb.isOffScaleLeft(wrapNow) \
        or theLtb.isOffScaleRight(wrapPrev) and theLtb.isOffScaleRight(wrapNow):
            logging.debug('All off scale.')
            return polyEnd, crossLines, polyNew
        # wrapDiff is +ve to the right
        wrapDiff = wrapNow - wrapPrev
        xInc = (xNow - xPrev) / (2 * abs(wrapDiff))
        logging.debug('Interp: wrapDiff={:d} xInc={:f}'.format(wrapDiff, xInc))
        x = xPrev + xInc
        # First what is R, the line from the previous point to the track edge
        if not theLtb.offScale(wrapPrev):
            # Point to add to polyline
            if wrapDiff > 0:
                # Line to right edge
                polyEnd = (x, theTwd.rightP)
            else:
                polyEnd = (x, theTwd.leftP)
        # Now compute C, the crossing lines
        # Limit number of wraps
        if abs(wrapDiff) > 2 * self.MAX_BACKUP_TRACK_CROSSING_LINES:
            wrapIncrement = abs(wrapDiff) // 4 * self.MAX_BACKUP_TRACK_CROSSING_LINES
            # print('TRACE: Plot._retInterpolateWrapPoints(): increasing wrapIncrement=', wrapIncrement, wrapDiff)
            logging.debug('Plot._retInterpolateWrapPoints(): increasing wrapIncrement=', wrapIncrement)
        else:
            wrapIncrement = 1
        while abs(wrapDiff) > wrapIncrement:
            if wrapDiff > 0:
                crossLines.append((x, theTwd.leftP))
                x += 2 * xInc
                crossLines.append((x, theTwd.rightP))
                wrapDiff -= wrapIncrement
            else:
                crossLines.append((x, theTwd.rightP))
                x += 2 * xInc
                crossLines.append((x, theTwd.leftP))
                wrapDiff += wrapIncrement
        # Finally S the 'incoming' line from the track edge to the new point
        if not theLtb.offScale(wrapNow):
            if wrapDiff > 0:
                # Line from left edge to final point
                polyNew.append((x, theTwd.leftP))
            else:
                polyNew.append((x, theTwd.rightP))
            # x + xInc should be the same as xNow
            x = xNow
            polyNew.append((x, pNow))
        # Note: Filters cross line list to make sure that are are not too many.
#        return polyEnd, crossLines, polyNew
        return polyEnd, self._filterCrossLineList(crossLines), polyNew

    def _filterCrossLineList(self, cLineS):
        """Takes a list of [from, to, from, to, ...] and, if the list is longer
        than 2*self.MAX_BACKUP_TRACK_CROSSING_LINES returns a subset of that list
        of length 2*self.MAX_BACKUP_TRACK_CROSSING_LINES with the first and last
        members of the supplied list and intermediate members chosen at reasonable
        intervals.
        The rationale is that poor logs can cause pathological behaviour if there
        are really spurious readings in the frame set. For example test file
        "apc.las.las" has an SP curve that has these values towards the end:
        332.724
        13716948.000
        41150204.000
        68583456.000
        96016712.000
        116591672.000
        123450000.000
        This includes a jump of 13716615.276 mV which on a scale of -20 to 80 mV means
        137,166 wrap lines crossing the track. This can turn a 1.6Mb file into a 91Mb file!
        This code cuts down those 137,166 wrap lines (mostly duplicate ones) to 8 or so.
        """
        assert(len(cLineS) % 2 == 0)
        if len(cLineS) / 2 <= self.MAX_BACKUP_TRACK_CROSSING_LINES:
            # 'Normal' return without filtering
            return cLineS
        # Filter the number of crossLines to a maximum of say 8 for a single X step
        # Slightly awkward as crossLines is even length list i.e. list treated as list of pairs
        # i, s, f must be multiplied by 2 to find the real index in crossLines
        # i is integer, s,f are floats
        i = 0
        s = (len(cLineS) / 2) / self.MAX_BACKUP_TRACK_CROSSING_LINES
        f = 0.0
        # Filtered list to be returned
        r = []
        while i < (len(cLineS) / 2) - int(s + 0.5):
            # Append from/to points
            r.append(cLineS[2*i])
            r.append(cLineS[2*i+1])
            # Increment by stride
            f += s
            # Round to nearest member
            i = int(f+0.5)
        # Last from/to point
        r.append(cLineS[2*i])
        r.append(cLineS[2*i+1])
        return r
        
    #==============================
    # End: Plotting the curves.
    #==============================

class PlotReadLIS(Plot):
    """A subclass of Plot that is configured from FILM, PRES and (optionally) AREA, PIP Logical Records."""
    def __init__(self, lrFILM, lrPRES, lrAREA=None, lrPIP=None, theScale=0):
        myFilmCfg = FILMCfg.FilmCfgLISRead(lrFILM)
        myPresCfg = PRESCfg.PresCfgLISRead(lrPRES, myFilmCfg)
        super().__init__(myFilmCfg, myPresCfg, theScale)

class PlotReadXML(Plot):
    """A subclass of Plot that is configured from XML file(s) using LgFormat."""
    def __init__(self, uniqueId, theScale=0):
        myFilmCfg = FILMCfgXML.FilmCfgXMLRead()
        myPresCfg = PRESCfgXML.PresCfgXMLRead(myFilmCfg, uniqueId)
        super().__init__(myFilmCfg, myPresCfg, theScale)
