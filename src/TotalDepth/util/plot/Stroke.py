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
"""Defines how the stroke of a pen is represented on a plot.

Created on 7 Mar 2011

"""

__author__  = 'Paul Ross'
__date__    = '2011-03-07'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

import collections

#: Stroke basic properties
Stroke = collections.namedtuple('Stroke', 'width colour coding opacity')
#: Prototypical black solid stroke
#: Usage: StrokeBlackSolid._replace(width=2.0)
StrokeBlackSolid = Stroke('1', 'black', None, 1.0)

def retSVGAttrsFromStroke(stroke):
    """Returns SVG attributes as a dictionary from a Stroke() object."""
    r = {
        'stroke-width'          : '{:.3f}'.format(stroke.width),
        'stroke'                : str(stroke.colour),
        'stroke-opacity'        : '{:.3f}'.format(stroke.opacity),
    }
#    print('stroke.coding', stroke.coding)
    if stroke.coding:
        r['stroke-dasharray'] = '{:d},{:d}'.format(stroke.coding[0], stroke.coding[1])
    return r
