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
"""Produces histograms.

Created on Nov 29, 2011

"""

__author__  = 'Paul Ross'
__date__    = '2011-11-29'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

import collections

class Histogram(object):
    """A histogram class."""
    def __init__(self):
        self._h = collections.defaultdict(int)
        
    def add(self, x, count=1):
        """Increments the count of value x by count (default 1)."""
        self._h[x] += count
    
    def __getitem__(self, x):
        """Returns the current count of x."""
        return self._h[x]
    
    def strRep(self, width=75, chr='+', valTitle='', inclCount=False):
        """Returns a string representation of the histogram in ASCII.
        
        width - The maximum width to use.
        
        chr - The character to use in the plot.
        
        valTitle - The title to use for values.
        
        inclCount - Include tha tacture count for each value?
        """
        spacer = ' | '
        maxCount = max(self._h.values())
        # Width of the keys
        kWidth = max([len(str(x)) for x in self._h.keys()])
        if len(valTitle) > 0:
            kWidth = max(kWidth, len(valTitle))
        # Amount of space for the histogram bars
        barWidth = width
        barWidth -= kWidth
        barWidth -= len(spacer)
        # Amount of space for the count of occurences
        vWidth = 0
        if inclCount:
            vWidth = len(str(maxCount))
            barWidth -= vWidth
            barWidth -= 3 # i.e. ' []'
#        print('TRACE: ', lenMaxStr, vWidth)
        myFact = maxCount / barWidth
        strL = []
        if len(valTitle) > 0:
            strL.append(valTitle)
        for x in sorted(self._h.keys()):
            if inclCount:
                strL.append('{:>{kWidth}s} [{:>{vWidth}d}]{:s}{:s}'.format(
                                str(x),
                                self._h[x],
                                spacer,
                                chr * int(0.5 + self._h[x] / myFact),
                                kWidth=kWidth,
                                vWidth=vWidth,
                    )
                )
            else:
                strL.append('{:>{kWidth}s}{:s}{:s}'.format(
                                str(x),
                                spacer,
                                chr * int(0.5 + self._h[x] / myFact),
                                kWidth=kWidth,
                    )
                )
        return '\n'.join(strL)
