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
"""
Tests plotting AREA patterns in SVG.
"""
import typing

__author__  = 'Paul Ross'
__date__    = '2018-07-04'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

import os
import sys
import time
import logging
#import math
import pprint
import io
import random
#import collections
# try:
#     import xml.etree.cElementTree as etree
# except ImportError:
#     import xml.etree.ElementTree as etree

import pytest

# from TotalDepth.LIS.core import LogiRec
# from TotalDepth.LIS.core import RepCode
# from TotalDepth.LIS.core import LisGen
# from TotalDepth.LIS.core import FileIndexer
# from TotalDepth.LIS.core import EngVal
# from TotalDepth.LIS.core import Mnem
# # LAS
# from TotalDepth.LAS.core import LASRead
from TotalDepth.util import XmlWrite
# # Plot
from TotalDepth.util.plot import Coord, SVGWriter
# #from TotalDepth.util.plot import XGrid
# from TotalDepth.util.plot import Plot
# from TotalDepth.util.plot import PlotConstants
from TotalDepth.util.plot import AREACfg
# from TotalDepth.util.plot import PRESCfgXML

from . import TestPlotShared



TEST_SVG_AREAS = {
    1   : TestPlotShared.SVGTestOutput(
            'Area_Patterns_Mono_Data_URI.svg',
            "All the monochrome lithology patterns available in AREACfg as a Data URI Scheme."
        ),
    2   : TestPlotShared.SVGTestOutput(
            'Area_Patterns_Rgb_Data_URI.svg',
            "All the colour lithology patterns available in AREACfg as a Data URI Scheme."
        ),
}


def _plot_all_lithology_patterns_uri(filename: str, area_dict: typing.Dict[str, str]) -> None:
    fp = TestPlotShared.outPath(filename)
    num_patterns = len(area_dict)
    margin = Coord.Dim(10, 'mm')
    width = Coord.Dim(210, 'mm')
    gap = Coord.Dim(10, 'mm')
    num_wide = 4
    panel_width = (width - margin * 2.0 - gap * (num_wide - 1)) / num_wide
    panel_height = panel_width * 0.75
    num_high = int(0.5 + num_patterns / num_wide)
    height = margin * 2.0 + panel_height * num_high + gap * (num_high - 1)
    viewPort = Coord.Box(width, height)
    attrs_doc = { 'xmlns:xlink' : 'http://www.w3.org/1999/xlink' }
    with SVGWriter.SVGWriter(open(fp, 'w'), viewPort, attrs_doc) as xS:
        AREACfg.write_svg_defs(xS, area_dict)
        for i, pattern in enumerate(area_dict):
            idx_w = i % num_wide
            idx_h = i // num_wide
            x = margin + (panel_width + margin) * idx_w
            y = margin + (panel_height + margin) * idx_h
            attrs_panel = {
                'stroke' : 'black',
                'stroke-width': '2.0',
                'fill': 'url(#{})'.format(AREACfg.PATTERN_IDS[pattern])
            }
            with SVGWriter.SVGRect(xS, Coord.Pt(x, y), Coord.Box(panel_width, panel_height), attrs_panel):
                pass
            attrs_text = {
                'text-anchor': 'middle',
            }
            with SVGWriter.SVGText(xS, Coord.Pt(x + panel_width / 2, y - Coord.Dim(2, 'mm')),
                                   'Helvetica', 10, attrs_text):
                xS.characters(pattern)


def test_plot_all_lithology_patterns_mono_data_uri():
    _plot_all_lithology_patterns_uri(TEST_SVG_AREAS[1].fileName, AREACfg.AREA_DATA_URI_SCHEME_MONO)

def test_plot_all_lithology_patterns_rbg_data_uri():
    _plot_all_lithology_patterns_uri(TEST_SVG_AREAS[2].fileName, AREACfg.AREA_DATA_URI_SCHEME_RGB)

