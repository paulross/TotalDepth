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
This provides a representation of the structure of recorded data.
"""
import itertools
import logging
import typing
from functools import reduce

import numpy as np

from TotalDepth.common import LogPass
from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core.File import LogicalData
from TotalDepth.RP66V1.core.LogicalRecord import EFLR
from TotalDepth.RP66V1.core.LogicalRecord.Types import EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP

logger = logging.getLogger(__file__)


class ExceptionLogPass(ExceptionTotalDepthRP66V1):
    pass


class ExceptionFrameChannel(ExceptionLogPass):
    pass


class ExceptionFrameArray(ExceptionLogPass):
    pass


class ExceptionFrameArrayInit(ExceptionFrameArray):
    pass


class ExceptionLogPassInit(ExceptionLogPass):
    pass


class ExceptionLogPassProcessIFLR(ExceptionLogPass):
    pass


DEFAULT_NP_TYPE = np.float64


class RP66V1FrameChannel(LogPass.FrameChannel):
    """
    This represents a single channel in a frame. It is file format independent and can be used depending on the
    source of the information: LIS/LAS/RP66V1 file, XML index, Postgres database etc.
    """
    def __init__(self,
                 ident: typing.Hashable,
                 long_name: bytes,
                 units: bytes,
                 dimensions: typing.List[int],
                 np_dtype: np.dtype,
                 rep_code: int,
                 ):
        """
        Constructor.

        :param ident: Some hashable identity.
        :param long_name: A description of the channel
        :param units: Units of  Measure.
        :param dimensions: A list of dimensions of each value. [1] is a single value per frame. [4, 1024] is a 4 * 1024
            matrix such as sonic waveform of 1024 samples with 4 waveforms per frame.
        :param np_dtype: The numpy dtype to use.
        :param rep_code: Integer representation code that this channel is encoded in.
        """
        super().__init__(ident, long_name, units, dimensions, np_dtype)
        self.rep_code: int = rep_code

    @property
    def ident(self) -> typing.Hashable:
        """Overload base class."""
        return self._ident.I.decode("ascii")

    @property
    def len_input_bytes(self) -> int:
        """The number of RP66V1 bytes to read for one frame of this channel."""
        try:
            return self.count * RepCode.rep_code_fixed_length(self.rep_code)
        except RepCode.ExceptionRepCode as err:
            raise ExceptionFrameChannel(f'len_input_bytes() on variable length Rep Code {self.rep_code}') from err

    def read(self, ld: LogicalData, frame_number: int) -> None:
        """Reads the Logical Data into the numpy frame at the specified frame number.

        This is currently RP66V1 specific. In future designs this can be sub-classed by format (LAS, LIS, RP66V1 etc.)
        """
        # if len(self.array) == 0:
        #     raise ExceptionFrameChannel(f'FrameChannelDLIS.read() array is not initialised.')
        if frame_number >= len(self.array):
            raise ExceptionFrameChannel(
                f'FrameChannelDLIS.read() frame number {frame_number} is > than array size {len(self.array)}.'
            )
        for dim in self.numpy_indexes(frame_number):
            # dim is a tuple of length self.rank + 1
            value = RepCode.code_read(self.rep_code, ld)
            self.array[dim] = value

    def seek(self, ld: LogicalData) -> None:
        """Increments the logical data without reading any values into the array."""
        if len(self.array) != 0:
            raise ExceptionFrameChannel('seek() on empty array. This seems like a logical error.')
        ld.seek(RepCode.rep_code_fixed_length(self.rep_code) * self.count)


class RP66V1FrameArray(LogPass.FrameArray):
    """
    In the olden days we would record this on a single chunk of continuous film.
    """
    def _handle_remaining(self, ld: LogicalData, frame_number: int) -> None:
        """What to do if there is unread data."""
        if ld.remain != 0:
            msg = f'Not all logical data consumed, frame {frame_number} remaining {ld.remain} bytes: {ld.view_remaining(ld.remain)}'
            logger.warning(msg)
            # raise ExceptionFrameArray(msg)

    def read(self, ld: LogicalData, frame_number: int) -> None:
        """Reads the Logical Data into the numpy frame."""
        for channel in self.channels:
            channel.read(ld, frame_number)
        self._handle_remaining(ld, frame_number)

    def read_partial(self, ld: LogicalData, frame_number: int, channels: typing.Set[typing.Hashable]) -> None:
        """Reads the Logical Data into the numpy frame for the nominated channels."""
        for c, channel in enumerate(self.channels):
            if c == 0 or channel.ident in channels:
                channel.read(ld, frame_number)
            else:
                channel.seek(ld)
        self._handle_remaining(ld, frame_number)

    @property
    def x_axis_len_input_bytes(self) -> int:
        """The number of RP66V1 bytes to read for one frame of the X axis.
        This can be useful for partial reads of an IFLR from file if only the X axis is interesting, for example for
        indexing.

        Will raise an ExceptionFrameChannel if the X axis is  not represented by a fixed length Representation Code."""
        return self.channels[0].len_input_bytes

    def init_x_axis_array(self, number_of_frames: int) -> None:
        """
        Initialises an empty Numpy array for the first channel suitable to fill with <frames> number of frame data.
        """
        if number_of_frames <= 0:
            raise ExceptionFrameArray(f'Number of frames must be > 0 not {number_of_frames}')
        self.x_axis.init_array(number_of_frames)

    def read_x_axis(self, ld: LogicalData, frame_number: int) -> None:
        """Reads the first channel of the Logical Data into the numpy frame."""
        if self.x_axis.array_size == 0:
            self.x_axis.init_array(1)
        self.x_axis.read(ld, frame_number)


# ====================== Constructing from RP66V1 data ====================

def frame_channel_from_RP66V1(channel_object: EFLR.Object) -> RP66V1FrameChannel:
    """Create a file format agnostic FrameChannel from an EFLR.Object (row) in a `CHANNEL` EFLR."""
    return RP66V1FrameChannel(
        ident=channel_object.name,
        long_name=channel_object[b'LONG-NAME'].value[0] if channel_object[b'LONG-NAME'].value is not None else b'',
        rep_code=channel_object[b'REPRESENTATION-CODE'].value[0],
        units=channel_object[b'UNITS'].value[0] if channel_object[b'UNITS'].value is not None else b'',
        dimensions=channel_object[b'DIMENSION'].value,
        np_dtype=RepCode.numpy_dtype(channel_object[b'REPRESENTATION-CODE'].value[0])
    )


def frame_array_from_RP66V1(frame_object: EFLR.Object,
                            channel_eflr: EFLR.ExplicitlyFormattedLogicalRecord) -> RP66V1FrameArray:
    """Create a file format agnostic FrameArray from an EFLR.Object (row) in a `FRAME` EFLR and a `CHANNEL` EFLR."""
    # print('TRACE: frame_object.attr_label_map', frame_object.attr_label_map)
    key = b'DESCRIPTION'
    if key in frame_object.attr_label_map and frame_object[key].count == 1 and frame_object[key].value is not None:
        description = frame_object[b'DESCRIPTION'].value[0]
    else:
        description = b''
    frame_array = RP66V1FrameArray(frame_object.name, description)
    # TODO: Apply Semantic Restrictions?
    # Hmm, [RP66V1 Section 5.7.1 Frame Objects] says that C=1 for DESCRIPTION but our example data shows C=0
    for channel_obname in frame_object[b'CHANNELS'].value:
        if channel_obname in channel_eflr.object_name_map:
            frame_array.append(frame_channel_from_RP66V1(channel_eflr[channel_obname]))
        else:
            raise ExceptionFrameArrayInit(f'Channel {channel_obname} not in CHANNEL EFLR.')
    return frame_array


def log_pass_from_RP66V1(frame: EFLR.ExplicitlyFormattedLogicalRecord,
                         channels: EFLR.ExplicitlyFormattedLogicalRecord) -> LogPass.LogPass:
    """Create a file format agnostic FrameArray from a `FRAME` type EFLR and a `CHANNEL` type EFLR."""
    if frame.set.type != b'FRAME':
        raise ExceptionLogPassInit(f"Expected frame set type to be b'FRAME' but got {frame.set.type}")
    if frame.lr_type != EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'FRAME']:
        raise ExceptionLogPassInit(
            f"Expected frame Logical Record type to be"
            f" {EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'FRAME']} but got {frame.lr_type}"
        )
    if channels.set.type != b'CHANNEL':
        raise ExceptionLogPassInit(f"Expected channel set type to be b'CHANNEL' but got {channels.set.type}")
    if channels.lr_type != EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'CHANNEL']:
        raise ExceptionLogPassInit(
            f"Expected channel Logical Record type to be"
            f" {EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'CHANNEL']} but got {channels.lr_type}")
    log_pass = LogPass.LogPass()
    # This is a list of independent recordings.
    # In the olden days we would record each of these on a separate chunks of separate films.
    for frame_object in frame.objects:
        log_pass.append(frame_array_from_RP66V1(frame_object, channels))
    return log_pass

# ====================== END: Constructing from RP66V1 data ====================
