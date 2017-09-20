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
    Plot uses LogPass.frameSet.genChScValues(ch, sc) to plot individual curves.
    
Lacunae
=======
Area plotting.
Caching (e.g. SVG fragments - is this worth it?)
    
PlotConfig
==========

PlotTracks
----------
Typically a three track (+depth) have these dimensions in inches::

    Track    Left    Right    Width
    1        0       2.4      2.4
    Depth    2.4     3.2      0.8
    2        3.2     5.6      2.4
    3        5.6     8.0      2.4

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
    
    Table record (type 34) type: FILM
    
    MNEM  GCOD  GDEC  DEST  DSCA
    -----------------------------
    
    1     EEE   ----  PF2   D200
    2     EEE   ----  PF1   DM


Other FILM Table Examples::

    Table record (type 34) type: FILM
    
    MNEM  GCOD  GDEC  DEST  DSCA
    -----------------------------
    1     EEB   ----  PF1   D200
    2     EEB   ----  PF2   DM
    
    Table record (type 34) type: FILM
    
    MNEM  GCOD  GDEC  DEST  DSCA
    -----------------------------
    1     E20   -4--  PF1   D200
    2     EEE   ----  PF2   D200
    
    MNEM  GCOD  GDEC  DEST  DSCA
    -----------------------------
    1     EEE   ----  PF1   D200
    2     E1E   -4-   PF2   D200
    
    Table record (type 34) type: FILM
    
    MNEM  GCOD  GDEC  DEST  DSCA
    -----------------------------
    
    D     E3E   -3-   PFD   D200
    E     E3E   -3-   PFE   D500
    5     EB0   ---   PF5   D200
    6     EEB   ---   PF6   D200
    
    Table record (type 34) type: FILM
    
    MNEM  GCOD  GDEC  DEST  DSCA
    -----------------------------
    
    8     EB0   ---   PF8   D200
    A     LLLL  1111  PFA   DM
    E     E4E   -4-   PFE   D200
    K     E4E   -4-   PFK   D500
    
    Table record (type 34) type: FILM
    
    MNEM      CINT      GCOD  GDEC  DEST  DSCA
    -------------------------------------------
    
    1          0.00000  E2E   -2-   PF1   D200
    2          0.00000  E2E   -1-   PF2   D500
    3          0.00000  EEE   ----  NEIT  S5
    4          0.00000  EEE   ----  NEIT  S5
    
    Table record (type 34) type: FILM
    
    MNEM      CINT      GCOD  GDEC  DEST  DSCA
    -------------------------------------------
    
    1          300.000  E2E   -2-   PF1   D200
    2          300.000  E2E   -2-   PF2   D500
    3          300.000  EEE   ----  NEIT  S5
    4          300.000  EEE   ----  NEIT  S5
    
    Table record (type 34) type: FILM
    
    MNEM      CINT      GCOD  GDEC  DEST  DSCA
    -------------------------------------------
    
    1          50.0000  EEE   ----  PF1   D200
    2          0.00000  EEE   ----  PF2   D200
    3          0.00000  EEE   ----  NEIT  D200
    4          0.00000  EEE   ----  NEIT  D200

Minimal, but not complete interpretation::

    Ignore GDEC as dupe.
    E - Equi-spaced (linear).
    n - Log with number of decades.
    B - Blank.
    L - ?


What to do with 0 (continuation?).
Examples: E20   -4-- means 4 decades over track 23.

"""
__author__  = 'Paul Ross'
__date__    = '2011-02-28'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

import math
import functools

from TotalDepth.util.plot import ExceptionTotalDepthLISPlot
from TotalDepth.util.plot import Coord
from TotalDepth.util.plot import Stroke
from TotalDepth.util.plot import SVGWriter

class ExceptionTotalDepthLISPlotTrack(ExceptionTotalDepthLISPlot):
    """Exception for plotting tracks."""
    pass

#################################################################
# Section: Track grid generators and line transforms to the grid.
#################################################################
def genLinear10(l, r):
    """Generate a linear series of 10 track grid lines as (Stroke, position)."""
    slc = (r - l) / 10.0
    p = l
    for i in range(0, 11):
        if i % 10 == 0:
            yield Stroke.StrokeBlackSolid._replace(width=0.75), p
        elif i == 5:
            yield Stroke.StrokeBlackSolid._replace(width=0.5), p
        else:
            yield Stroke.StrokeBlackSolid._replace(width=0.25), p
        p += slc

def genLog10(l, r, cycles=1, start=1):
    """Generate a log10 series of track grid lines as (Stroke, position).
    cycles is the number of log cycles to split the track up into.
    start is the start position of the scale e.g. 2 for common resistivity curves.
    So cycles=2, start=2 would give log grid 2 to 20000 i.e. to plot
    resistivity in the range 0.2 to 2000."""
    slc = (r - l) / cycles
    posStart = l
    xOffs = math.log10(start)
    for c in range(cycles):
        for i in range(9):
            if c == 0 and i == 0:
                yield Stroke.StrokeBlackSolid._replace(width=0.75), l
            else:
                p = posStart + slc * (math.log10(1 + i + (start-1)) - xOffs)
                if (start == 1 and i == 0) \
                or i == 9 - (start - 1):
                    yield Stroke.StrokeBlackSolid._replace(width=0.75), p
                else:
                    yield Stroke.StrokeBlackSolid._replace(width=0.25), p
        posStart += slc
    yield Stroke.StrokeBlackSolid._replace(width=0.75), r

# Was:
#def genLog10Decade2(l, r):
#    for a in genLog10(l, r, cycles=2, start=1):
#        yield a

#: Generator for 2 decades of log base 10
genLog10Decade2 = functools.partial(genLog10, cycles=2, start=1)
#: Generator for 3 decades of log base 10
genLog10Decade3 = functools.partial(genLog10, cycles=3, start=1)
#: Generator for 4 decades of log base 10
genLog10Decade4 = functools.partial(genLog10, cycles=4, start=1)
#: Generator for 5 decades of log base 10
genLog10Decade5 = functools.partial(genLog10, cycles=5, start=1)

#: Generator for 1 decade of log base 10 starting at 2
genLog10Decade1Start2 = functools.partial(genLog10, cycles=1, start=2)
#: Generator for 2 decades of log base 10 starting at 2
genLog10Decade2Start2 = functools.partial(genLog10, cycles=2, start=2)

#############################################################
# End: Track grid generators and line transforms to the grid.
#############################################################

class Track(object):
    """Class that represents a single track. The track, as a structural
    graphical element, is merely a grid.
    The actual curves are plotted on panes that are independent from
    a single track (can span multiple tracks for example).
    
    leftPos - A Coord.Dim() object that is the left edge.
    
    rightPos- A Coord.Dim() object that is the right edge.
    
    gridGn - A generator of line positions, None for blank track.
    
    plotXLines - If True then plot X Axis information (depth lines) in this track.
    
    plotXAlpha - If True then plot X Axis information (depth numbers) in this track.
    """
    #: Space for plotting the scale for each curve
    DEPTH_PER_CH = Coord.Dim(0.25, 'in')
    def __init__(self, leftPos, rightPos, gridGn, plotXLines=True, plotXAlpha=False):
        """The track, as a structural graphical element, is merely a grid.
        The actual curves are plotted on panes that are independent from
        a single track (can span multiple tracks for example).
        leftPos - A Coord.Dim() object that is the left edge.
        rightPos- A Coord.Dim() object that is the right edge.
        gridGn - A generator of line positions, None for blank track.
        plotXLines - If True then plot X Axis information (depth lines) in this track.
        plotXAlpha - If True then plot X Axis information (depth numbers) in this track.
        """
        # TODO: We need to add additional information as to whether we plot xAxis lines, this
        # is different to whether we plot a (Y axis) grid
        if leftPos < Coord.Dim(0.0, leftPos.units):
            raise ExceptionTotalDepthLISPlotTrack(
                'Track left edge {:s} less than zero'.format(str(leftPos))
            )
        if leftPos >= rightPos:
            raise ExceptionTotalDepthLISPlotTrack(
                'Track left edge {:s} >= right edge {:s}'.format(str(leftPos), str(rightPos))
            )
        self._lP = leftPos
        self._rP = rightPos
        self._gridGn = gridGn
        self.plotXLines = plotXLines
        self.plotXAlpha = plotXAlpha
        
    def __str__(self):
        return '{:s}: left={:s} right={:s} gridGen={:s} plotXLines={:s} plotXAlpha={:s}'.format(
            repr(self),
            str(self._lP),
            str(self._rP),
            str(self._gridGn),
            str(self.plotXLines),
            str(self.plotXAlpha),
        )
    
    @property
    def left(self):
        """The left edge as a Coord.Dim()."""
        return self._lP
    
    @property
    def right(self):
        """The left edge as a Coord.Dim()."""
        return self._rP
    
    @property
    def hasGrid(self):
        """True if ther is a grid to be generated for this track."""
        return self._gridGn is not None
    
    def plotSVG(self, topLeft, depth, theSVGWriter):
        """Plot the track gridlines.
        topLeft - A Coord.Pt() object that is the top left of the canvas.
        depth - A Coord.Dim() object that is the total depth of the grid below topLeft.
        drive - The plot driver."""
        if self._gridGn is not None:
            botLeft = Coord.newPt(topLeft, incY=depth)
            for stroke, pos in self._gridGn(self._lP.value, self._rP.value):
                # Compute the line position
                topP = Coord.newPt(topLeft, incX=Coord.Dim(pos, self._lP.units))
                botP = Coord.newPt(botLeft, incX=Coord.Dim(pos, self._lP.units))
                with SVGWriter.SVGLine(
                        theSVGWriter,
                        topP,
                        botP,
                        attrs=Stroke.retSVGAttrsFromStroke(stroke)
                    ):
                    pass
