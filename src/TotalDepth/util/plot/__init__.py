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
"""TODO: Separate LIS specific plotting and put that in LIS.util.plot

That means only having Coord, Stroke, SVGWriter, XGrid? here.
"""
__all__ = [
'Coord',
'Track',
'XGrid',
'Plot',
'SVGWriter',
]

"""Plotting code for TotalDepth."""

from TotalDepth.LIS import ExceptionTotalDepthLIS

class ExceptionTotalDepthLISPlot(ExceptionTotalDepthLIS):
    """Exception for plotting."""
    pass

from TotalDepth.util import ExceptionUtil

class ExceptionUtilPlot(ExceptionUtil):
    """Exception class for util package."""
    pass

