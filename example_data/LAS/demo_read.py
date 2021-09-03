#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 1999-2021 Paul Ross
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
Demonstration code for reading from a LAS file.
"""
import os

import TotalDepth
from TotalDepth.LAS.core import LASRead

TOTAL_DEPTH_SOURCE_ROOT = os.path.dirname(TotalDepth.__file__)
EXAMPLE_DATA_DIRECTORY = os.path.join(TOTAL_DEPTH_SOURCE_ROOT, os.path.pardir, os.path.pardir, 'example_data')

las_file_path = os.path.join('example_data', 'LAS', 'data', 'BASIC_FILE_0_50.las')
las_file_path = os.path.join(EXAMPLE_DATA_DIRECTORY, 'LAS', 'data', 'BASIC_FILE_0_50.las')
las_file = LASRead.LASRead(las_file_path, las_file_path, raise_on_error=False)

print(type(las_file.frame_array))
if las_file.frame_array is not None:
    for channel in las_file.frame_array.channels:
        # channel.array is a numpy masked array.
        array = channel.array
        print(f'{channel.ident:4} [{channel.units:4}] Shape: {array.shape} Minimum: {array.min():8g}')

