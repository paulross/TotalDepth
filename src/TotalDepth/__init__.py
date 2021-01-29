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
"""TotalDepth - a suite of Petrophysical software."""

__all__ = ['LAS', 'LIS', 'RP66V1', 'util',]

__version__ = '0.3.2'

VERSION = (0, 3, 2)

RELEASE_NOTES = [
    """
""",
]

entry_points_console_scripts_dict = {
    # All TotalDepth scripts have a 'td' prefix.
    # Experimental scripts have a 'tdX' prefix.
    # General
    'tdplotlogs': 'TotalDepth.PlotLogs:main',
    'tddetif': 'TotalDepth.DeTif:main',
    # General util/
    'tdarchive': 'TotalDepth.util.archive:main',
    'tdcopybinfiles': 'TotalDepth.util.CopyBinFiles:main',
    'tdremovedupefiles': 'TotalDepth.util.RemoveDupeFiles:main',
    # General common/
    'tdprocess': 'TotalDepth.common.process:main',
    # LIS
    'tdlisdumpframeset': 'TotalDepth.LIS.DumpFrameSet:main',
    'tdlisindex': 'TotalDepth.LIS.Index:main',
    'tdlistohtml': 'TotalDepth.LIS.LisToHtml:main',
    'tdlisplotlogpasses': 'TotalDepth.LIS.PlotLogPasses:main',
    # 'tdXlisrandomframesetread': 'TotalDepth.LIS.RandomFrameSetRead:main',
    'tdlisscanlogidata': 'TotalDepth.LIS.ScanLogiData:main',
    'tdlisscanlogirecord': 'TotalDepth.LIS.ScanLogiRec:main',
    'tdlisscanphysrec': 'TotalDepth.LIS.ScanPhysRec:main',
    'tdlistablehistogram': 'TotalDepth.LIS.TableHistogram:main',
    # LAS
    'tdlasreadlasfiles': 'TotalDepth.LAS.ReadLASFiles:main',
    # RP66V1
    'tdrp66v1scan': 'TotalDepth.RP66V1.Scan:main',
    'tdrp66v1tolas': 'TotalDepth.RP66V1.ToLAS:main',
    'tdrp66v1scanhtml': 'TotalDepth.RP66V1.ScanHTML:main',
    'tdrp66v1logrecindex': 'TotalDepth.RP66V1.LogRecIndex:main',
    'tdrp66v1indexpickle': 'TotalDepth.RP66V1.IndexPickle:main',
    'tdrp66v1indexxml': 'TotalDepth.RP66V1.IndexXML:main',
}

ENTRY_POINTS_CONSOLE_SCRIPTS = [
    f'{k}={v}' for k, v in entry_points_console_scripts_dict.items()
]

class ExceptionTotalDepth(Exception):
    """Specialisation of an exception class for TotalDepth package."""
    pass
