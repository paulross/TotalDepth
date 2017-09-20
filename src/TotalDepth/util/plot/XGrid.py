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
"""Provides plotting support for the X axis grid i.e. Depth grid lines and text.

Created on 28 Feb 2011


TODO: Remove APIs that are not used by Plot or anything. Plot only appears to
use genXAxisRange() and genXAxisTextRange().
"""
__author__  = 'Paul Ross'
__date__    = '2011-02-28'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

#import time
#import sys
import logging
#import collections
import math

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import Units
from TotalDepth.util.plot import Coord
from TotalDepth.util.plot import Stroke

class ExceptionPlotXGrid(ExceptionTotalDepthLIS):
    """Exception for plotting."""
    pass

#: Definition of a grey solid stroke
#: Usage: StrokeBlackGrey._replace(width=2.0)
StrokeGreySolid = Stroke.Stroke('1', 'grey', None, 1.0)

class XGrid(object):
    """Class that can generate depth line grid and alphanumeric values.
    Constructed with integer scale.
    """
    #: Default for unknown units and scale, this is basically like
    #: simple graph paper
    DEFAULT_INTERVAL_MAP = {
        1   : Stroke.StrokeBlackSolid._replace(width=0.5),
        10  : Stroke.StrokeBlackSolid._replace(width=1.0),
    }
    #: Default position for text on the X axis
    DEFAULT_INTERVAL_TEXT = 100
    def __init__(self, scale):
        """Constructor with integer scale. We make scale a constructor argument
        as we know that up front. We don't necessarily know the X units."""
        if not isinstance(scale, int):
            raise ExceptionPlotXGrid('XGrid.__init__(): {:s} is not an integral type.'.format(str(scale)))
        self._scale = scale
        # Interval of lines and the strokes used
        # NOTE: These are in 'optical' units i.e. the callers units will
        # be converted to Units.opticalUnits() before lookup
        # Map of {units : {scale {interval : Stroke, ...}, ...}, ...}
        self._intStroke = {}
        # Set predefined values
        self._setInterval(b'FEET', 25,
            {
                1   : StrokeGreySolid._replace(width=0.25),
                5   : StrokeGreySolid._replace(width=0.5),
                10  : Stroke.StrokeBlackSolid._replace(width=0.5),
                50  : Stroke.StrokeBlackSolid._replace(width=0.75),
                100 : Stroke.StrokeBlackSolid._replace(width=1.0),
            }
        )
        self._setInterval(b'FEET', 40,
            {
                1   : StrokeGreySolid._replace(width=0.25),
                5   : StrokeGreySolid._replace(width=0.5),
                10  : Stroke.StrokeBlackSolid._replace(width=0.5),
                50  : Stroke.StrokeBlackSolid._replace(width=0.75),
                100 : Stroke.StrokeBlackSolid._replace(width=1.0),
            }
        )
        self._setInterval(b'FEET', 100,
            {
                1   : StrokeGreySolid._replace(width=0.25),
                5   : StrokeGreySolid._replace(width=0.5),
                10  : Stroke.StrokeBlackSolid._replace(width=0.5),
                50  : Stroke.StrokeBlackSolid._replace(width=0.75),
                100 : Stroke.StrokeBlackSolid._replace(width=1.0),
            }
        )
        self._setInterval(b'FEET', 200,
            {
                2   : Stroke.StrokeBlackSolid._replace(width=0.25),
                10  : Stroke.StrokeBlackSolid._replace(width=0.5),
                50  : Stroke.StrokeBlackSolid._replace(width=0.75),
                100 : Stroke.StrokeBlackSolid._replace(width=1.0),
            }
        )
        self._setInterval(b'FEET', 500,
            {
                10  : Stroke.StrokeBlackSolid._replace(width=0.75),
                50  : Stroke.StrokeBlackSolid._replace(width=1.25),
                100 : Stroke.StrokeBlackSolid._replace(width=2.0),
            }
        )
        self._setInterval(b'FEET', 1000,
            {
                20  : Stroke.StrokeBlackSolid._replace(width=0.25),
                100  : Stroke.StrokeBlackSolid._replace(width=0.75),
                200 : Stroke.StrokeBlackSolid._replace(width=1.25),
            }
        )
        self._setInterval(b'M   ', 25,
            {
                1   : Stroke.StrokeBlackSolid._replace(width=0.5),
                5   : Stroke.StrokeBlackSolid._replace(width=0.75),
                10  : Stroke.StrokeBlackSolid._replace(width=1.25),
                25  : Stroke.StrokeBlackSolid._replace(width=2.0),
            }
        )
        self._setInterval(b'M   ', 40,
            {
                1   : Stroke.StrokeBlackSolid._replace(width=0.5),
                5   : Stroke.StrokeBlackSolid._replace(width=0.75),
                10  : Stroke.StrokeBlackSolid._replace(width=1.25),
                25  : Stroke.StrokeBlackSolid._replace(width=2.0),
            }
        )
        self._setInterval(b'M   ', 100,
            {
                1   : Stroke.StrokeBlackSolid._replace(width=0.5),
                5   : Stroke.StrokeBlackSolid._replace(width=0.75),
                10  : Stroke.StrokeBlackSolid._replace(width=1.25),
                25  : Stroke.StrokeBlackSolid._replace(width=2.0),
            }
        )
        self._setInterval(b"M   ", 200,
            {
                1   : Stroke.StrokeBlackSolid._replace(width=0.5),
                5   : Stroke.StrokeBlackSolid._replace(width=0.75),
                10  : Stroke.StrokeBlackSolid._replace(width=1.25),
                25  : Stroke.StrokeBlackSolid._replace(width=2.0),
            }
        )
        self._setInterval(b"M   ", 500,
            {
                5   : Stroke.StrokeBlackSolid._replace(width=0.75),
                10  : Stroke.StrokeBlackSolid._replace(width=1.25),
                50  : Stroke.StrokeBlackSolid._replace(width=2.0),
            }
        )
        self._setInterval(b"M   ", 1000,
            {
#                10  : Stroke.StrokeBlackSolid._replace(width=0.75),
                50  : Stroke.StrokeBlackSolid._replace(width=0.75),
                100 : Stroke.StrokeBlackSolid._replace(width=1.25),
            }
        )
        # Interval of depth text.
        # NOTE: These are in 'optical' units i.e. the callers units will
        # be converted to Units.opticalUnits() before lookup
        # Map of {units : {scale {interval, ...}, ...}
        self._intText = {}
        self._setIntervalText(b'FEET', 25, 5)
        self._setIntervalText(b'FEET', 40, 10)
        self._setIntervalText(b'FEET', 100, 50)
        self._setIntervalText(b'FEET', 200, 100)
        self._setIntervalText(b'FEET', 500, 200)
        self._setIntervalText(b'FEET', 1000, 200)
        self._setIntervalText(b'M   ', 25, 2)
        self._setIntervalText(b'M   ', 40, 5)
        self._setIntervalText(b'M   ', 100, 10)
        self._setIntervalText(b'M   ', 200, 25)
        self._setIntervalText(b'M   ', 500, 50)
        self._setIntervalText(b'M   ', 1000, 100)
        
    def _makeEngValOptical(self, theEv):
        """Converts an EngVal to 'optical' units e.g. b'.1IN' goes to b'FEET'."""
        return theEv.newEngValInUnits(Units.opticalUnits(theEv.uom))
    
    def _setInterval(self, units, scale, intStrokeMap):
        """Set interval line strokes, any existing units, scale will be replaced."""
        if not isinstance(scale, int):
            raise ExceptionPlotXGrid('XGrid._setInterval(): scale {:s} is not an integral type.'.format(str(scale)))
        if units not in self._intStroke:
            self._intStroke[units] = {}
        self._intStroke[units][scale] = intStrokeMap

    def _getInterval(self, units):
        """Returns an interval line strokes map."""
        try:
            return self._intStroke[units][self._scale]
        except KeyError:
            pass
        logging.warning('XGrid._getInterval() returning default for units={!s:s}.'.format(units))
        return self.DEFAULT_INTERVAL_MAP
        
    def _setIntervalText(self, units, scale, interval):
        """Set interval text positions, any existing units, scale will be replaced."""
        if not isinstance(scale, int):
            raise ExceptionPlotXGrid('XGrid._setIntervalText(): scale {:s} is not an integral type.'.format(str(scale)))
        if units not in self._intText:
            self._intText[units] = {}
        self._intText[units][scale] = interval

    def _getIntervalText(self, units):
        """Gets the interval text position."""
        try:
            return self._intText[units][self._scale]
        except KeyError:
            pass
        logging.warning('XGrid.genIntervalText() returning default for units={!s:s}.'.format(units))
        return self.DEFAULT_INTERVAL_TEXT

    def _firstVal(self, xVal, xInterval, xInc):
        assert(xInterval > 0)
        if xInc:
            return xInterval * math.ceil(xVal / xInterval)
        return xInterval * math.floor(xVal / xInterval)

    def genXAxisRange(self, evFrom, evTo):
        """Generates a bounded series of X axis line plot positions as
        (Dim(), Stroke()). evFrom and evTo and EngVal objects."""
        logging.info('XGrid.genXAxisRange(): evFrom={!s:s}, evTo={!s:s}'.format(evFrom, evTo))
        evFrom = self._makeEngValOptical(evFrom)
        evTo = self._makeEngValOptical(evTo)
        if evFrom.uom != evTo.uom:
            evTo.convert(evFrom.uom)
        xInc = evTo > evFrom
        for xPos, stroke in self._genXAxisStroke(evFrom.value, xInc, evFrom.uom):
            if xInc and xPos > evTo \
            or not xInc and xPos < evTo:
                break
            myDim = Coord.Dim(Units.convert(xPos - evFrom.value, evFrom.uom, b'INCH'), 'in')
            yield myDim.divide(self._scale), stroke


    def genXPosStroke(self, xFrom, xInc, units):
        """Generates unbounded series of X line positions as (Dim(), Stroke()).
        
        xFrom - The starting value as a float, positions may not include this
        if fractional. First x position generated will be math.ceil()
        if xInc, math.floor() otherwise.
        
        xInc - A boolean, True if X increases.
        
        units - Units of X axis e.g. b'FEET'."""
        for xPos, stroke in self._genXAxisStroke(xFrom, xInc, units):
            myDim = Coord.Dim(Units.convert(xPos - xFrom, units, b'INCH'), 'in')
            yield myDim.divide(self._scale), stroke

    def _genXAxisStroke(self, xFrom, xInc, units):
        """Generates unbounded series of (X axis value, Stroke()).
        
        xFrom - The starting value, positions may not include this if fractional.
        First x position generated will be math.ceil() if xInc,
        math.floor() otherwise.
        
        xInc - True if X increases.
        
        units - Units of X axis."""
        xSpaceMin = min(self._getInterval(units).keys())
        xFirstPos = self._firstVal(xFrom, xSpaceMin, xInc)
        for xPos, stroke in self.genEventsUnits(xFirstPos, xInc, units):
            yield xPos, stroke

    def genEventsUnits(self, xFrom, xInc, units):
        """Generates events from/to in units."""
        for e in self._genEvents(xFrom, xInc, self._getInterval(units)):
            yield e

    def _genEvents(self, xFrom, xInc, eMap):
        l = sorted(eMap.keys(), reverse=True)
        for e in self._genEventsRec(xFrom, xInc, l, eMap):
            yield e

    def _genEventsRec(self, xFrom, xInc, l, eMap):
        """Recursive interval generator."""
        if len(l) > 0:
            assert(l[0] > 0)
            v = self._firstVal(xFrom, l[0], xInc)
            if len(l) == 1:
                # Base case
                while 1:
                    yield v, eMap[l[0]]
                    if xInc:
                        v += l[0]
                    else:
                        v -= l[0]
            else:
                for vE, e in self._genEventsRec(xFrom, xInc, l[1:], eMap):
                    if xInc and v < vE or not xInc and v > vE:
                        # Insert my event
                        yield v, eMap[l[0]]
                        if xInc:
                            v += l[0]
                        else:
                            v -= l[0]
                        yield vE, e
                    elif v == vE:
                        # Yield myself in preference
                        yield v, eMap[l[0]]
                        if xInc:
                            v += l[0]
                        else:
                            v -= l[0]
                    else:
                        yield vE, e

    def genXAxisTextRange(self, evFrom, evTo):
        """Generates a bounded series of X axis line plot positions as
        (Dim(), value). evFrom and evTo and EngVal objects."""
        logging.info('XGrid.genXAxisTextRange(): evFrom={!r:s},'
                     ' evTo={!r:s}'.format(evFrom, evTo))
        if evFrom.uom != evTo.uom:
            evTo.convert(evFrom.uom)
        evFrom = self._makeEngValOptical(evFrom)
        evTo = self._makeEngValOptical(evTo)
        xInc = evTo > evFrom
        for xPos, xVal in self._genXPosText(evFrom.value, xInc, evFrom.uom):
            if xInc and xVal > evTo \
            or not xInc and xVal < evTo:
                break
            yield xPos, xVal
#            myDim = Coord.Dim(Units.convert(xPos - evFrom.value, evFrom.uom, b'INCH'), 'in')
#            yield myDim.divide(self._scale), xVal

    def _genXPosText(self, xFrom, xInc, units):
        """Generates unbounded series of X text positions as (Dim(), value).
        xFrom - The starting value, positions may not include this if fractional.
                First x position generated will be math.ceil() if xInc,
                math.floor() otherwise.
        xInc - True if X increases.
        units - Units of X axis."""
        for xVal in self._genXAxisText(xFrom, xInc, units):
            myDim = Coord.Dim(Units.convert(xVal - xFrom, units, b'INCH'), 'in')
            yield myDim.divide(self._scale), xVal

    def _genXAxisText(self, xFrom, xInc, units):
        """Generates unbounded series of X axis values where text is to be placed.
        xFrom - The starting value, positions may not include this if fractional.
                First x position generated will be math.ceil() if xInc,
                math.floor() otherwise.
        xInc - True if X increases.
        units - Units of X axis."""
        xSpace = self._getIntervalText(units)
        xVal = self._firstVal(xFrom, xSpace, xInc)
        if not xInc:
            xSpace = -1 * xSpace
        while 1:
            yield xVal
            xVal += xSpace
