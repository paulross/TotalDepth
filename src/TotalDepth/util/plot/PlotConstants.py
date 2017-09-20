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
"""Some basic constants used in plotting.

Created on Jan 5, 2012

"""

__author__  = 'Paul Ross'
__date__    = '2012-01-05'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2012 Paul Ross.'

from TotalDepth.util.plot import Coord

#: Default SVG plot units
DEFAULT_PLOT_UNITS = 'in'
assert(DEFAULT_PLOT_UNITS in Coord.UNIT_MAP)
#: Units that we can convert to in LIS terms
DEFAULT_PLOT_LIS_UNITS = b"IN  "

#: Number of pixels per standard plot unit
VIEW_BOX_UNITS_PER_PLOT_UNITS = 96.0

#: Definition of a quarter inch margin
MarginQtrInch = Coord.Margin(
    Coord.Dim(0.25, 'in'),
    Coord.Dim(0.25, 'in'),
    Coord.Dim(0.25, 'in'),
    Coord.Dim(0.25, 'in'),
)

# These are here so that other modules can use them
#: Standard wireline log fan paper width i.e. long side.
STANDARD_PAPER_WIDTH = Coord.Dim(8.5, 'in')
#: Standard wireline log fan paper depth i.e. short side.
STANDARD_PAPER_DEPTH = Coord.Dim(6.25, 'in')
#: Standard wireline log fan paper margin.
STANDARD_PAPER_MARGIN = MarginQtrInch
