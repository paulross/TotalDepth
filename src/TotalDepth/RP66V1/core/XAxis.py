#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation.
# Copyright (C) 2011-2021 Paul Ross
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
Provides analysis and navigation along the X axis of RP66V1 logs.
RP66V1 specific code based on TotalDepth/common/XAxis.py
"""
import typing

import numpy as np

import TotalDepth.common
from TotalDepth.RP66V1.core import File


class IFLRReference(typing.NamedTuple):
    """POD class that represents the position of the IFLR in the file."""
    logical_record_position: File.LogicalRecordPosition
    frame_number: int  # TODO: Omit this  as it is implicit in the XAxis class?
    x_axis: typing.Union[int, float]


class XAxis:
    """This represents an X axis of a log pass for a particular object in that log pass.
    It has an ident, long name and units. It accumulates, for every IFLR in the set, the VR position LRSH position, frame number
    and X axis value.
    """
    def __init__(self, ident: bytes, long_name: bytes, units: bytes):
        self.ident = ident
        self.long_name = long_name
        self.units = units
        self._data: typing.List[IFLRReference] = []
        self._summary: typing.Union[None, XAxis.XAxisSummary] = None

    def append(self, position: File.LogicalRecordPosition, frame_number: int, x_axis: typing.Union[int, float]) -> None:
        """Add a IFLRReference to the XAxis."""
        # TODO: Verify the data position, frame number increasing etc.
        self._summary = None
        self._data.append(IFLRReference(position, frame_number, x_axis))

    def __getitem__(self, item) -> IFLRReference:
        """Return the IFLRReference for the index."""
        return self._data[item]

    def __len__(self) -> int:
        """Return the number of IFLRs."""
        return len(self._data)

    @property
    def summary(self) -> TotalDepth.common.XAxis.XAxisSummary:
        """Lazily compute the summary."""
        if self._summary is None:
            x_array: np.ndarray = np.empty(len(self._data), dtype=np.float64)
            for i in range(len(self._data)):
                x_array[i] = self._data[i].x_axis
            self._summary = TotalDepth.common.XAxis.compute_x_axis_summary(x_array)
        return self._summary

    # TODO: Add an API that can turn an X axis value into the nearest frame number. Needs to cope with decreasing data.


