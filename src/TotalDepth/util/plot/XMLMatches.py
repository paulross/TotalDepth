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
"""This looks at the available XML LgFormats and works out what curves of a LogPass
or LASFile can be plotted by each one.

Created on Jan 21, 2012

"""

__author__  = 'Paul Ross'
__date__    = '2012-01-21'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2012 Paul Ross.'

from TotalDepth.util.plot import FILMCfgXML
from TotalDepth.util.plot import PRESCfgXML

def fileCurveMap(theLpOrLasFile, directory=None):
    """Returns a map of ``{FilmID : [OUTP, ...], ...}`` which is a list of OUTP in theLpOrLasFile
    that could be plotted with that film ID."""
    myFilmCfg = FILMCfgXML.FilmCfgXMLRead(directory)
    return fileCurveMapFromFILM(theLpOrLasFile, myFilmCfg)

def fileCurveMapFromFILM(theLpOrLasFile, theFilmCfg):
    """Returns a map of ``{FilmID : [OUTP, ...], ...}`` which is a list of OUTP in theLpOrLasFile
    that could be plotted with that film ID."""
    r = {}
    for uid in sorted(theFilmCfg.uniqueIdS()):
        myPresCfg = PRESCfgXML.PresCfgXMLRead(theFilmCfg, uid)
        try:
            myPhsFiCf = theFilmCfg[uid]
            outIdS = myPresCfg.outpChIDs(myPhsFiCf.name)
        except KeyError:
            pass
        else:
            r[uid] = [anO for anO in outIdS if theLpOrLasFile.hasOutpMnem(anO)]
    return r
