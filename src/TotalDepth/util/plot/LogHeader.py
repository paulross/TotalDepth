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
"""Plots various headers as SVG. Of note is the API header

Created on Dec 30, 2011

"""

__author__  = 'Paul Ross'
__date__    = '2011-12-30'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

import collections
#import pprint

from TotalDepth import ExceptionTotalDepth
from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import Mnem
from TotalDepth.util.plot import Coord
from TotalDepth.util.plot import PlotConstants
from TotalDepth.util.plot import SVGWriter

class ExceptionLogHeader(ExceptionTotalDepth):
    """Exception for plotting Log Headers."""
    pass

class ExceptionLogHeaderLIS(ExceptionLogHeader):
    """Exception for plotting Log Headers from LIS data."""
    pass

class ExceptionLogHeaderLAS(ExceptionLogHeader):
    """Exception for plotting Log Headers from LAS data."""
    pass

#: Tuple to describe static data locations
#: If text is None then no text will be plotted
#: If rAttr is None then no box will be plotted
#: If mnem is non-None then a Mmem can be plotted at xMenm increment, a Coord.Dim()
Static = collections.namedtuple('Static', 'x y w d text font size tAttr rAttr mnem xMnem')

TRANSFORM_UNITS_PER_PLOT_UNITS = PlotConstants.VIEW_BOX_UNITS_PER_PLOT_UNITS

#: Default font
FONT_PROP = 'Verdana'

#: SVG attributes for a fine lined rectangle
RECT_ATTRS_FINE = {
    'fill' : "none",
    'stroke' : "black",
    'stroke-width' : ".5",
}

#: SVG attributes for a fine text
TEXT_ATTRS_FINE = {
    'text-anchor'           : 'start',
#    'dominant-baseline'     : 'central',
}

#: SVG attributes for a bold text
TEXT_ATTRS_LARGE = {
    'text-anchor'           : 'start',
    'font-weight'           : "bold",
}

#: SVG attributes for a large WOB text
TEXT_ATTRS_LARGE_WOB = {
    'text-anchor'           : 'start',
    'font-weight'           : "bold",
    'fill'                  : "white",
}

#: Standard plot units used in the layout definition
HEADER_PLOT_UNITS = 'in'

STATICS = [
    # Big stuff at the top
    Static(0.15, 0.05, 1.25, 0.4, 'Company:', FONT_PROP, 18, TEXT_ATTRS_LARGE_WOB, None, Mnem.Mnem(b'CN  '), 1.25),
    Static(0.15, 0.55, 1.25, 0.4, 'Well:', FONT_PROP, 18, TEXT_ATTRS_LARGE_WOB, None, Mnem.Mnem(b'WN  '), 1.25),
    Static(0.15, 1.05, 1.25, 0.4, 'Field:', FONT_PROP, 18, TEXT_ATTRS_LARGE_WOB, None, Mnem.Mnem(b'FN  '), 1.25),
    # Slightly weird choice of rig name
    Static(0.15, 1.55, 1.25, 0.4, 'Rig:', FONT_PROP, 18, TEXT_ATTRS_LARGE_WOB, None, Mnem.Mnem(b'COUN'), 1.25),
    Static(3.15, 1.55, 1.0, 0.4, 'Country:', FONT_PROP, 18, TEXT_ATTRS_LARGE_WOB, None, Mnem.Mnem(b'NATI'), 1.0),
    # Run specific stuff
    Static(3.2, 1.9, 1.0, 0.4, None, FONT_PROP, 14, TEXT_ATTRS_LARGE, None, Mnem.Mnem(b'HIDE'), 0.0),
    Static(3.2, 2.1, 1.0, 0.4, None, FONT_PROP, 14, TEXT_ATTRS_LARGE, None, Mnem.Mnem(b'HID1'), 0.0),
    Static(3.2, 2.3, 1.0, 0.4, None, FONT_PROP, 14, TEXT_ATTRS_LARGE, None, Mnem.Mnem(b'HID2'), 0.0),
    # Fine data
    # Box for field location that has three fields
    Static(1.15+1/6, 2.7, 2.7, 0.5, None, FONT_PROP, 9, TEXT_ATTRS_FINE, RECT_ATTRS_FINE, None, None),
    Static(1.15+1/6, 2.7, 0.5, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'FL  '), 0.0),
    Static(1.15+1/6, 2.85, 0.5, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'FL1 '), 0.0),
    Static(1.15+1/6, 3.0, 0.5, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'FL2 '), 0.0),
    # Box for Elev.
    Static(1.15+1/6+2.7, 2.7, 2.25, 0.5, None, FONT_PROP, 9, TEXT_ATTRS_FINE, RECT_ATTRS_FINE, None, None),
    Static(1.15+1/6+2.7, 2.7, 0.5, 1/6, 'Elev:', FONT_PROP, 9, TEXT_ATTRS_FINE, None, None, None),
    Static(1.15+1/6+2.7+0.5, 2.7, 0.5, 1/6, 'KB', FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'EKB '), 0.25),
    Static(1.15+1/6+2.7+0.5, 2.85, 0.5, 1/6, 'GL', FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'EGL '), 0.25),
    Static(1.15+1/6+2.7+0.5, 3.0, 0.5, 1/6, 'DF', FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'EDF '), 0.25),
    # Boxes for datums
    Static(1.15+1/6, 3.2, 4.75+3/16, 0.5, None, FONT_PROP, 9, TEXT_ATTRS_FINE, RECT_ATTRS_FINE, None, None),
    Static(1.15+1/6, 3.2, 1.5, 1/6, 'Permanent Datum:', FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'PDAT'), 1.25),
    Static(1.15+1/6, 3.35, 1.5, 1/6, 'Log Measured From:', FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'LMF '), 1.25),
    Static(1.15+1/6, 3.5, 1.5, 1/6, 'Drilling Measured From:', FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'DMF '), 1.25),
    Static(1.15+1/6+2.7, 3.2, 0.5, 1/6, 'Elev:', FONT_PROP, 9, TEXT_ATTRS_FINE, None, None, None),
    Static(1.15+1/6+3.5, 3.35, 0.5, 1/6, 'above permanent datum', FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'APD '), -0.75),
    # Well deviation
    Static(2.0, 3.7, 2, 0.3, None, FONT_PROP, 9, TEXT_ATTRS_FINE, RECT_ATTRS_FINE, None, None),
    Static(2.5, 3.7, 1.5, 1/6, 'Max. Well Deviation', FONT_PROP, 9, TEXT_ATTRS_FINE, None, None, None),
    Static(2.5, 3.7+1/8, 1.5, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'MHD '), 0.125),
    # Latitude
    Static(4.0, 3.7, 1.125, 0.3, None, FONT_PROP, 9, TEXT_ATTRS_FINE, RECT_ATTRS_FINE, None, None),
    Static(4.25, 3.7, 1.125, 1/6, 'Latitude', FONT_PROP, 9, TEXT_ATTRS_FINE, None, None, None),
    Static(4.25, 3.7+1/8, 1.125, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'LATI'), -0.125),
    # Longitude
    Static(5.125, 3.7, 1.125, 0.3, None, FONT_PROP, 9, TEXT_ATTRS_FINE, RECT_ATTRS_FINE, None, None),
    Static(5.375, 3.7, 1.125, 1/6, 'Longitude', FONT_PROP, 9, TEXT_ATTRS_FINE, None, None, None),
    Static(5.375, 3.7+1/8, 1.125, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'LONG'), -0.125),
    # Other services we put on the right, six of them
    Static(4.0, 4, 2.5, 1/6, 'Other Services:', FONT_PROP, 9, TEXT_ATTRS_FINE, None, None, None),
    Static(4.0, 4+1/6, 2.5, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'OS1 '), 0.0),
    Static(4.0, 4+2/6, 2.5, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'OS2 '), 0.0),
    Static(4.0, 4+3/6, 2.5, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'OS3 '), 0.0),
    Static(4.0, 4+4/6, 2.5, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'OS4 '), 0.0),
    Static(4.0, 4+5/6, 2.5, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'OS5 '), 0.0),
    Static(4.0, 4+6/6, 2.5, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'OS6 '), 0.0),
]

# Lower left fine data
for __i, (__t, __m) in enumerate(
        [
            ('Logging Date',                    b'DATE',),
            ('Run Number',                      b'RUN ',),
            ('Depth Driller',                   b'TDD ',),
            ('Depth Logger',                    b'TDL ',),
            ('Bottom Log Interval',             b'BLI ',),
            ('Top Log Interval',                b'TLI ',),
            ('Casing Driller Size @ Depth',     None,), # '@' and mnem added below
            ('Casing Logger',                   b'CBLO',),
            ('Bit Size',                        b'BS  ',),
            ('Type of Fluid in the Hole',       b'DFT ',),
            ('Mud: Density, Viscosity',         None,), # TODO:
            ('Mud: Fluid Loss, Ph',             None,), # TODO:
            ('Mud: Source of Sample',           b'MSS ',),
            ('Rm @ Measured Temperature',       None,), # '@' added below
            ('Rmf @ Measured Temperature',      None,), # '@' added below
            ('Rmc @ Measured Temperature',      None,), # '@' added below
            ('Source: Rmf, Rmc',                None,), # TODO:
            ('Rm @ MRT, Rmf @ MRT',             None,), # Two little '@'s added below
            ('Max. Recorded Temperature',       b'MRT ',),
            ('Time circulation stopped',        b'TCS ',), # and b'DCS '?
            ('Time logger at bottom',           b'TLAB',),
            ('Logging unit and location',       b'LUL ',),
            ('Recorded by',                     b'ENGI',),
            ('Witnessed by',                    b'WITN',),
        ]
    ):
    if __m is not None:
        __m = Mnem.Mnem(__m)
    STATICS.append(Static(0, 4.+__i*1/6, 2, 1/6, __t, FONT_PROP, 9, TEXT_ATTRS_FINE, RECT_ATTRS_FINE, __m, 2.0))
    # And boxes that appear to the right
    STATICS.append(Static(2.0, 4.+__i*1/6, 2, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, RECT_ATTRS_FINE, None, None))
    
# The '@' stuff in column two
__MNEM_FINE_MAP = {
    6 : [b'CSIZ', b'CD  '],
    13 : [b'RMS ', b'MST '],
    14 : [b'RMFS', b'MFST'],
    15 : [b'RMCS', b'MCST'],
}

for __i in sorted(__MNEM_FINE_MAP.keys()):
    STATICS.append(Static(2.875, 4.+__i*1/6, 0.25, 1/6, '@', FONT_PROP, 9, TEXT_ATTRS_FINE, None, None, None))
    for __j, __m in enumerate(__MNEM_FINE_MAP[__i]):
        STATICS.append(Static(2.875, 4.+__i*1/6, 0.25, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(__m), -0.875 + __j * 1.125))
## Now the two little '@' for 'Rm @ MRT, Rmf @ MRT'
#STATICS.append(Static(2.5, 4.+17*1/6, 0.25, 1/6, '@', FONT_PROP, 9, TEXT_ATTRS_FINE, RECT_ATTRS_FINE, None, None))
#STATICS.append(Static(3.5, 4.+17*1/6, 0.25, 1/6, '@', FONT_PROP, 9, TEXT_ATTRS_FINE, RECT_ATTRS_FINE, None, None))
# Make two boxes for 'Rm @ MRT, Rmf @ MRT'
STATICS.append(Static(2.0, 4.+17*1/6, 1.0, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, RECT_ATTRS_FINE, Mnem.Mnem(b'RMB '), 0.0))
STATICS.append(Static(3.0, 4.+17*1/6, 1.0, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, RECT_ATTRS_FINE, Mnem.Mnem(b'RMFB'), 0.0))

# Static text that is rotated -90, each list is preceded by a transform x, y, r
# x, y are in plot units (inches) that will be converted by TRANSFORM_UNITS_PER_PLOT_UNITS
STATICS_VERT = [
    (
        (0.0, 4.0, -90),
        [
            Static(0.0, 0.0, 2.0, 1.15, None, FONT_PROP, 9, TEXT_ATTRS_FINE, RECT_ATTRS_FINE, None, None),
            Static(0.1, 0.1, 0.25, 1/6, 'Rig:', FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'COUN'), 0.6),
            Static(0.1, 0.3, 0.25, 1/6, 'Field:', FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'FN  '), 0.6),
            Static(0.1, 0.5, 0.25, 1/6, 'Location:', FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'FL  '), 0.6),
            Static(0.1, 0.7, 0.25, 1/6, 'Well:', FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'WN  '), 0.6),
            Static(0.1, 0.9, 0.25, 1/6, 'Company:', FONT_PROP, 9, TEXT_ATTRS_FINE, None, Mnem.Mnem(b'CN  '), 0.6),
            Static(0.3, 1.15, 1.0, 1/6, None, FONT_PROP, 9, TEXT_ATTRS_FINE, RECT_ATTRS_FINE, None, None),
            Static(0.5, 1.15, 1.0, 1/6, 'LOCATION', FONT_PROP, 9, TEXT_ATTRS_FINE, None, None, None),
        ],
    )
]

# Set of {mnem, ...} that can be written to the header
MNEM_SET = set()
for __st in STATICS:
    if __st.mnem is not None:
        MNEM_SET.add(__st.mnem)
for __t, __stS in STATICS_VERT:
    for __st in __stS:
        if __st.mnem is not None:
            MNEM_SET.add(__st.mnem)

class APIHeaderBase(object):
    """Base class to be used by APIHeaderLIS or APIHeaderLAS.
    
    If isTopOfLog is True plot is rotated 90 deg as if to fit on top of a traditional log."""
    def __init__(self, isTopOfLog=False):
        """Constructor with flag that controls plot orientation. If True plot is
        rotated 90 deg as if to fit on top of a traditional log."""
        self._isTopOfLog = isTopOfLog
    
    #=============================================
    # Section: To be implemented by child classes.
    #=============================================
    def missingFields(self, theWsd):
        """Returns two sets:
        A set of mnemonics that could be plotted but are not in the Logical Record(s).
        A set of mnemonics that are in the Logical Record(s) but could not be plotted."""    
        raise NotImplementedError
    
    def _checkWsd(self, theWsd=None):
        """Makes a plot."""
        raise NotImplementedError

    def _plotStaticIfCONS(self, xS, theWsd, theSt):
        """Plots well site data."""
        raise NotImplementedError
    #=============================================
    # End: To be implemented by child classes.
    #=============================================
    
    def size(self):
        """Returns a Coord.Box for my size, currently a single page on fan folded paper."""
        return self._size(self._isTopOfLog)
    
    def _size(self, isTopOfLog):
        x, y = PlotConstants.STANDARD_PAPER_DEPTH, self._width()
        if isTopOfLog:
            return Coord.Box(y, x)
        return Coord.Box(x, y)
    
    def viewPort(self, theTl):
        """The SVG viewport."""
        mySize = self.size()
        return Coord.Box(mySize.width + theTl.x, mySize.depth + theTl.y)
        
    def _width(self):
        return PlotConstants.STANDARD_PAPER_WIDTH \
            - PlotConstants.STANDARD_PAPER_MARGIN.left \
            - PlotConstants.STANDARD_PAPER_MARGIN.right
            
    def _uprightGroupAttrs(self, x, y, r):
        return {
            'transform' : "translate({:g},{:g}) rotate({:g})".format(
                x * TRANSFORM_UNITS_PER_PLOT_UNITS,
                y * TRANSFORM_UNITS_PER_PLOT_UNITS,
                r,
            ),
        }
            
    def _plotStatic(self, xS, st):
        if st.rAttr is not None:
            # Write the box
            with SVGWriter.SVGRect(
                        xS,
                        self._pt(st.x, st.y),
                        Coord.Box(Coord.Dim(st.w, HEADER_PLOT_UNITS), Coord.Dim(st.d, HEADER_PLOT_UNITS)
                    ),
                    st.rAttr,
                ):
                pass
        # Write the text
        if st.text is not None:
            with SVGWriter.SVGText(
                    xS,
                    self._pt(st.x + 0.05, st.y + st.d * 3 / 4),
                    st.font,
                    st.size,
                    st.tAttr,
                ):
                xS.characters(st.text)
            
    def _dim(self, v):
        return Coord.Dim(v, HEADER_PLOT_UNITS)
    
    def _box(self, w, d):
        return Coord.Box(self._dim(w), self._dim(d))
    
    def _pt(self, x, y):
        return Coord.Pt(self._dim(x), self._dim(y))
    
    def _ptZero(self):
        return self._pt(0.0, 0.0)
    
    def _plotCONS(self, xS, st, theValStr):
        """Print a Static() object with an value as a string e.g. EngVal.pStr()."""
        # No Rectangle
        myTAttr = st.tAttr
        myTAttr.update({'font-weight' : "bold",})
        with SVGWriter.SVGText(
                xS,
                self._pt(st.x + 0.05 + st.xMnem, st.y + st.d * 3 / 4),
                st.font,
                st.size,
                myTAttr,
            ):
            xS.characters(theValStr)
            
    def _plotBackGround(self, xS):
        """Plot the background stuff."""
        # Top black background
        with SVGWriter.SVGRect(
                xS,
                self._ptZero(),
                Coord.Box(PlotConstants.STANDARD_PAPER_DEPTH, Coord.Dim(2.0, HEADER_PLOT_UNITS)),
                {'fill' : "black",}):
            pass
        # Logo
        self._plotLogo(xS)
        
    def _plotLogo(self, xS):
        """Plots the TotalDepth logo."""
        myLogoColour = "blue"
        with SVGWriter.SVGRect(
                xS,
                self._pt(1.2, 2.05),
                self._box(2.0, 0.3),
                {'fill' : "none", 'stroke' : myLogoColour, 'stroke-width' : "2.0",}):
            pass
        with SVGWriter.SVGRect(
                xS,
                self._pt(1.2, 2.05 + 0.3),
                self._box(2.0, 0.3),
                {'fill' : myLogoColour, 'stroke' : myLogoColour, 'stroke-width' : "2.0",}):
            pass
        with SVGWriter.SVGText(
                xS,
                self._pt(1.2 + 1.0, 2.05 + 0.3 + 0.25),
                FONT_PROP,
                24, 
                {'text-anchor' : 'middle', 'font-weight' : "bold", 'fill' : "white",}):
            xS.characters('TotalDepth')

    def _traceTopLeftAndViewBox(self, theTl, xS):
        # Plot Top-left box and view box
        with SVGWriter.SVGRect(xS, Coord.zeroBaseUnitsPt(), Coord.Box(theTl.x, theTl.y), {
                'fill' : "red",
                'stroke' : "black",
                'stroke-width' : "1",
            }):
            pass
        with SVGWriter.SVGRect(xS, Coord.zeroBaseUnitsPt(), self.viewPort(theTl), {
                'fill' : "none",
                'stroke' : "green",
                'stroke-width' : "1",
            }):
            pass

    def plot(self, xS, theTl, theWsdS=None):
        """Write the header to the SVG stream at position offset top left.
        theWsd is a list of records that contain well site data.
        Will raise ExceptionLogHeader is wrong type of Logical Record."""
        self._checkWsd(theWsdS)
#        self._traceTopLeftAndViewBox(theTl, xS)
        groupAttrs = {
            'transform' : "translate({:g},{:g})".format(
                theTl.x.value * TRANSFORM_UNITS_PER_PLOT_UNITS,
                theTl.y.value * TRANSFORM_UNITS_PER_PLOT_UNITS,
            ),
        }
        with SVGWriter.SVGGroup(xS, groupAttrs):
            if self._isTopOfLog:
                # Make this all one group so it can be rotated etc.
                groupAttrs = {
                    'transform' : "translate({:g},0) rotate(90)".format(
                        self._width().value * TRANSFORM_UNITS_PER_PLOT_UNITS,
                    ),
                }
                with SVGWriter.SVGGroup(xS, groupAttrs):
                    self._plot(xS, theWsdS)
            else:
                self._plot(xS, theWsdS)
                
    def _plot(self, xS, theWsdS):
        # Write background
        self._plotBackGround(xS)
        # Page 1 bounding box
        with SVGWriter.SVGRect(xS, self._ptZero(), self._size(False),
                               {'fill' : "none", 'stroke' : "blue", 'stroke-width' : ".5",}):
            pass
        # Write statics
        for st in STATICS:
            self._plotStatic(xS, st)
        for (x, y, r), stS in STATICS_VERT:
            with SVGWriter.SVGGroup(xS, self._uprightGroupAttrs(x, y, r)):
                for st in stS:
                    self._plotStatic(xS, st)
        self._plotWsd(xS, theWsdS)
        
    def _plotWsd(self, xS, theWsdS):
        """Plot dynamic information from well site data."""
        if theWsdS is not None and len(theWsdS) > 0:
            for st in STATICS:
                self._plotStaticIfCONS(xS, theWsdS, st)
            for (x, y, r), stS in STATICS_VERT:
                if any([st.mnem is not None for st in stS]):
                    with SVGWriter.SVGGroup(xS, self._uprightGroupAttrs(x, y, r)):
                        for st in stS:
                            self._plotStaticIfCONS(xS, theWsdS, st)
                            
class APIHeaderLIS(APIHeaderBase):
    """Can lay out an API header from LIS information, specifically a type 34 CONS record.
    
    If isTopOfLog is True plot is rotated 90 deg as if to fit on top of a traditional log."""
    def __init__(self, isTopOfLog=False):
        """Constructor with a Logical Record."""
        super().__init__(isTopOfLog)

    #===================================
    # Section: Required implementations.
    #===================================
    def missingFields(self, theWsd):
        """Well site data (theWsd) in LIS is a list of CONS Logical Records.
        
        Returns two sets:
        
        A set of mnemonics that could be plotted but are not in the Logical Record(s).
        
        A set of mnemonics that are in the Logical Record(s) but could not be plotted."""
        allLrMnemS = set()
        for lr in theWsd:
            allLrMnemS |= set(lr.rowMnems())
        return MNEM_SET - allLrMnemS, allLrMnemS - MNEM_SET
    
    def _checkWsd(self, theWsd=None):
        """Checks the well site data. In this case we expect a list of CONS Logical Records."""
        if theWsd is not None:
            # It is OK if theWsd is zero length it just means there is no WSD not
            # we have been passed the wrong type of records.
            if len(theWsd) > 0 and not self._anyLrHasData(theWsd):
                raise ExceptionLogHeaderLIS('LogHeader.plot(): wrong type of Logical Record: {:s}'.format(str(theWsd)))
        
    def _plotStaticIfCONS(self, xS, theWsd, theSt):
        """Print a Static() object if it has a dynamic data label.
        In this case theWsd is a list of Logical Record table objects."""
        if theSt.mnem is not None \
        and theSt.xMnem is not None:
            for lr in theWsd:
                if theSt.mnem in lr:
                    self._plotCONS(xS, theSt, lr.retRowByMnem(theSt.mnem)[b'VALU'].engVal.pStr())
                    break
    #===================================
    # End: Required implementations.
    #===================================

    def _anyLrHasData(self, theLrS):
        """Returns True if any of the Logical Records is the required type and has the required columns."""
        return any(self._lrHasData(lr) for lr in theLrS)
    
    def _lrHasData(self, theLr):
        """Returns True if the Logical Record is the required type and has the required columns."""
        # Type 34
        if theLr.type != LogiRec.LR_TYPE_WELL_DATA:
            return False
        if theLr.value != b'CONS':
            return False
        if b'MNEM' not in theLr.colLabels() or b'VALU' not in theLr.colLabels():
            return False
        return True
    
    def lrDataCount(self, theLrS):
        """Returns the number of Mnem's in MNEM_SET that could be plotted in a
        header that are found in all the Logical Records."""
        r = 0
        for lr in theLrS:
            if self._lrHasData(lr):
                for m in MNEM_SET:
                    if m in lr:
                        r += 1
        return r
    
class APIHeaderLAS(APIHeaderBase):
    """Can lay out an API header from a representation of a LAS file."""
    #: Some conversions from LIS standard to LAS standard
    #: All as truncated ascii strings i.e. using pStr(strip=True)
    LIS_MNEM_TO_LAS_MNEM = {
        # From 'W' section
        'BLI'   : 'STRT',
        'TLI'   : 'STOP',
        'CN'    : 'COMP',
        'WN'    : 'WELL',
        'FN'    : 'FLD',
        'FL'    : 'LOC',
        'FL1'   : 'PROV',
        'FL2'   : 'UWI',
        'LUL'   : 'SRVC',
        # From 'P' section
        'MRT'   : 'BHT',
        'DFD'   : 'FD',
        'LATI'  : 'LAT',
        'LONG'  : 'LON',
        'TDL'   : 'DL'
    }
    def __init__(self, isTopOfLog=False):
        """Constructor with a Logical Record."""
        super().__init__(isTopOfLog)

    #===================================
    # Section: Required implementations.
    #===================================
    def missingFields(self, theLasFile):
        """Returns two sets:
        
        A set of mnemonics that could be plotted but are not in the Logical Record(s).
        
        A set of mnemonics that are in the Logical Record(s) but could not be plotted."""
        allMnemS = theLasFile.getAllWsdMnemonics()
        # Convert to LAS like Mnemonics from LIS ones
        myMnemSet = set()
        for str in set([m.pStr(strip=True) for m in MNEM_SET]):
            try:
                str = self.LIS_MNEM_TO_LAS_MNEM[str]
            except KeyError:
                pass
            myMnemSet.add(str)
        return myMnemSet - allMnemS, allMnemS - myMnemSet
        
    def _checkWsd(self, theWsd=None):
        """Checks the well site data. In this case it is a NOP as anything goes."""
        pass
        
    def _plotStaticIfCONS(self, xS, theWsd, theSt):
        """Print a Static() object if it has a dynamic data label.
        In this case theWsd is a LASRead.LASRead object."""
        if theSt.mnem is not None \
        and theSt.xMnem is not None:
            # theSt.mnem is a Mnem
            mnemVal = theSt.mnem.pStr(strip=True)
            try:
                mnemVal = self.LIS_MNEM_TO_LAS_MNEM[mnemVal]
            except KeyError:
                pass
            v, u = theWsd.getWsdMnem(mnemVal)
            if v is not None:
                if u is not None:
                    self._plotCONS(xS, theSt, '{:s} ({:s})'.format(str(v), u))
                else:
                    self._plotCONS(xS, theSt, '{:s}'.format(str(v)))
    #===================================
    # End: Required implementations.
    #===================================
