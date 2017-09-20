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
"""Drivers for plotting. NOT USED.

Created on 2 Mar 2011
@author: p2ross
"""
__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

import logging

from TotalDepth.util.plot import Coord
from TotalDepth.util.plot import SVGWriter

class PlotDriverBase(object):
    def plotText(self, thePoint, theFont, theSize, theText):
        """Plots text.
        thePoint - Coord.Pt
        theFont - string.
        theSize - integer.
        theText - string"""
        raise NotImplementedError()
    
    def plotLine(self, ptFrom, ptTo, theStroke):
        """Plots a line. Points are Coord.Pt objects. theStroke is a Plot.Stroke object."""
        raise NotImplementedError()
    
    def plotPolyLine(self, ptS, theStroke):
        """Plots a line. Points are Coord.Pt objects. theStroke is a Plot.Stroke object."""
        raise NotImplementedError()
    
class PlotDriverSVG(PlotDriverBase):
    def __init__(self, theS):
        """SVG constructor initialised with an output (file-like or path) and
        a Plot.Canvas object."""
        super().__init__()
        self._svg = theS
    
    def _retSVGAttrsFromStroke(self, stroke):
        """Returns SVG attributes from Plot.Stroke properties."""
        r = {
            'stroke-width'          : '{:f}'.format(stroke.width),
            'stroke'                : str(stroke.colour),
            'stroke-opacity'        : '{:f}'.format(stroke.opacity),
        }
        if stroke.coding:
            r['stroke-dasharray'] = stroke.coding
        return r
    
    def plotLine(self, ptFrom, ptTo, stroke):
        """Plots a line. Points are Coord.Pt objects. theStroke is a Plot.Stroke object."""
        with SVGWriter.SVGLine(self._svg, ptFrom, ptTo, attrs=self._retSVGAttrsFromStroke(stroke)):
            pass
    
    def plotPolyLine(self, ptS, theStroke):
        """Plots a polyline. ptS are a list of Coord.Pt objects. theStroke is a Plot.Stroke object."""
        with SVGWriter.SVGPolyline(self._svg, ptS, attrs=self._retSVGAttrsFromStroke(stroke)):
            pass
        
    def plotText(self, thePoint, theFont, theSize, theText):
        """Plots text.
        thePoint - Coord.Pt
        theFont - string.
        theSize - integer.
        theText - string"""
        with SVGWriter.SVGText(self._svg, thePoint, theFont, theSize):
            self._svg.characters(theText)
        
