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
This provides a file format agnostic representation of a LogPass.

- A LogPass consists of a set of FrameArray(s).
- A FrameArray consists of a set of FrameChannel(s).
- A FrameChannel consists of a set of values in a Numpy array of any shape from a single recorded channel.
"""

import functools
import itertools
import logging
import typing

import numpy as np

from TotalDepth import ExceptionTotalDepth
from TotalDepth.common import AbsentValue

logger = logging.getLogger(__file__)


class ExceptionLogPassBase(ExceptionTotalDepth):
    """General exception for problems with this module."""
    pass


class ExceptionLogPass(ExceptionLogPassBase):
    """General exception for problems with a LogPass object."""
    pass


class ExceptionFrameChannel(ExceptionLogPassBase):
    """General exception for problems with a FrameChannel object."""
    pass


class ExceptionFrameArray(ExceptionLogPassBase):
    """General exception for problems with a FrameArray object."""
    pass


DEFAULT_NP_TYPE: np.dtype = np.float64


class FrameChannel:
    """
    This represents a single channel in a frame. It is file format independent and can be used depending on the
    source of the information: LIS/LAS/RP66V1 file, XML index, Postgres database etc.
    """
    def __init__(self,
                 ident: typing.Hashable,
                 long_name: typing.Union[str, bytes],
                 units: typing.Union[str, bytes],
                 # shape: typing.Sequence[int] = (1,),
                 # np_dtype: np.dtype = DEFAULT_NP_TYPE,
                 shape: typing.Tuple[int, ...],
                 np_dtype: np.dtype,
                 ):
        """
        Constructor.

        :param ident: Some hashable identity.
        :param long_name: A description of the channel
        :param units: Units of  Measure.
        :param shape: A list of dimensions of each value. [1] is a single value per frame. [4, 1024] is a 4 * 1024
            matrix such as sonic waveform of 1024 samples with 4 waveforms per frame.
        :param np_dtype: The numpy dtype to use.
        """
        self._ident: typing.Hashable = ident
        self.long_name: typing.Union[str, bytes] = long_name
        self.units: typing.Union[str, bytes] = units
        self.dimensions: typing.Tuple[int, ...] = tuple(shape)
        self.np_dtype: np.dtype = np_dtype
        self.rank: int = len(self.dimensions)
        # Number of values per frame
        self.count: int = functools.reduce(lambda x, y: x * y, self.dimensions, 1)
        self.array = np.empty((0, *self.dimensions), dtype=self.np_dtype)

    @property
    def ident(self) -> typing.Hashable:
        """Overload this if necessary, for example RP66V1 has an OBNAME."""
        return self._ident

    def __str__(self) -> str:
        return f'<FrameChannel: \'{self.ident}\' "{self.long_name}" units: \'{str(self.units)}\'' \
            f' count: {self.count:d} dimensions: {self.dimensions} frames: {len(self.array)}>'

    def __len__(self) -> int:
        return len(self.array)

    def __getitem__(self, key):
        """Gets the value in the numpy array where key is a tuple of integers of length self.dimensions.
        For example this might be from self.numpy_indexes()."""
        return self.array[key]

    def __setitem__(self, key, value):
        """Sets the value in the numpy array where key is a tuple of integers of length self.dimensions.
        For example this might be from self.numpy_indexes()."""
        self.array[key] = value

    def init_array(self, number_of_frames: int) -> None:
        """
        Initialises an empty Numpy array suitable to fill with <frames> number of frame data for this channel.
        If an array already exists of the correct length it is reused.
        """
        if number_of_frames < 0:
            raise ExceptionFrameChannel(f'Number of frames must be >= 0 not {number_of_frames}')
        if self.array is None or len(self.array) != number_of_frames:
            self.array = np.empty((number_of_frames, *self.dimensions), dtype=self.np_dtype)

    @property
    def shape(self) -> typing.Tuple[int]:
        return self.array.shape

    @property
    def array_size(self) -> int:
        """The number of elements in the numpy array."""
        return self.array.size

    @property
    def sizeof_array(self) -> int:
        """The size of each element of the current array as represented by numpy."""
        return self.array.size * self.array.itemsize

    @property
    def sizeof_frame(self) -> int:
        """The size of a single frame in bytes as represented by numpy."""
        return self.array.itemsize * self.count

    def numpy_indexes(self, frame_number: int) -> itertools.product:
        """
        Returns a generator of numpy indexes for a particular frame.

        Example for a 2 x 3 array, given frame index 7::

            >>> list(itertools.product([7], [0,1], [0,1,2]))
            [(7, 0, 0), (7, 0, 1), (7, 0, 2), (7, 1, 0), (7, 1, 1), (7, 1, 2)]
            >>> list(itertools.product([7], range(2), range(3)))
            [(7, 0, 0), (7, 0, 1), (7, 0, 2), (7, 1, 0), (7, 1, 1), (7, 1, 2)]

        Usage, where `function` is a conversion function on the data::

            for dim in self.numpy_indexes(frame_number):
                # dim is a tuple of length self.rank + 1
                self.array[dim] = some_value
        """
        if frame_number < 0:
            raise ExceptionFrameChannel(f'FrameChannel.numpy_indexes() frame number must be > 0 not {frame_number}')
        products = [[frame_number]]
        for d in self.dimensions:
            products.append(range(d))
        return itertools.product(*products)

    def mask_array(self, absent_value: typing.Union[None, int, float]) -> None:
        """Masks the absent values."""
        if np.issubdtype(self.array.dtype, np.floating):
            self.array = AbsentValue.mask_absent_values(self.array, float(absent_value))
        elif np.issubdtype(self.array.dtype, np.integer):
            self.array = AbsentValue.mask_absent_values(self.array, int(absent_value))
        elif np.issubdtype(self.array.dtype, np.dtype(object).type):
            self.array = AbsentValue.mask_absent_values(self.array, None)


class FrameArray:
    """
    Represents a set of channels recorded simultaneously. In the olden days we would record this on a single piece of
    continuous film.

    Subclass this depending on the source of the information: LIS/LAS/DLIS file, XML index etc.
    """
    def __init__(self, ident: typing.Hashable, description: typing.Union[str, bytes]):
        self.ident: typing.Hashable = ident
        self.description: bytes = description
        self.channels: typing.List[FrameChannel] = []
        self.channel_ident_map: typing.Dict[typing.Hashable, typing.Union[int, str, bytes]] = {}

    def has(self, key: typing.Hashable) -> bool:
        return key in self.channel_ident_map

    def keys(self) -> typing.Iterable:
        return self.channel_ident_map.keys()

    def append(self, channel: FrameChannel) -> None:
        """Add a channel to the Array."""
        if self.has(channel.ident):
            raise ExceptionFrameArray(f'Duplicate channel identity "{channel.ident}"')
        else:
            self.channel_ident_map[channel.ident] = len(self.channels)
            self.channels.append(channel)

    def __str__(self) -> str:
        return '\n'.join(
            [
                f'FrameArray: ID: {self.ident} {self.description}',
            ] + [f'  {str(c)}' for c in self.channels]
        )

    def __len__(self) -> int:
        """The number of channels."""
        return len(self.channels)

    def __getitem__(self, item: typing.Union[int, str, bytes]) -> FrameChannel:
        if item in self.channel_ident_map:
            return self.channels[self.channel_ident_map[item]]
        return self.channels[item]

    @property
    def sizeof_array(self) -> int:
        """The total of the current frame array as represented by numpy."""
        return sum(ch.sizeof_array for ch in self.channels)

    @property
    def sizeof_frame(self) -> int:
        """The size of the internal representation of a frame as represented by numpy."""
        return sum(ch.sizeof_frame for ch in self.channels)

    @property
    def shape(self) -> typing.List[typing.Tuple[int, ...]]:
        """The shape of the frame array."""
        return [channel.shape for channel in self.channels]

    def init_arrays(self, number_of_frames: int) -> None:
        """
        Initialises empty Numpy arrays for each channel suitable to fill with <frames> number of frame data.
        """
        if number_of_frames <= 0:
            raise ExceptionFrameArray(f'Number of frames must be > 0 not {number_of_frames}')
        for channel in self.channels:
            channel.init_array(number_of_frames)

    def init_arrays_partial(self, number_of_frames: int, channels: typing.Set[typing.Hashable]) -> None:
        """
        Initialises empty Numpy arrays for each of the specified channels suitable to fill with <frames> number of
        frame data.
        The channels parameter limits the initialisation to only those channels.
        Unknown channels in that parameter are ignored.
        """
        if number_of_frames <= 0:
            raise ExceptionFrameArray(f'Number of frames must be > 0 not {number_of_frames}')
        for c, channel in enumerate(self.channels):
            if c == 0 or channel.ident in channels:
                channel.init_array(number_of_frames)
            else:
                channel.init_array(0)

    @property
    def x_axis(self) -> FrameChannel:
        if len(self.channels) == 0:
            raise ExceptionFrameArray('Zero channels. Expected one channel as the X axis.')
        return self.channels[0]

    def mask_array(self, absent_value: typing.Union[int, float]) -> None:
        """Mask the absent values in all but the index channels."""
        for i in range(1, len(self)):
            self.channels[i].mask_array(absent_value)


class LogPass:
    """
    This represents the structure a single run of data acquisition such as 'Repeat Section' or 'Main Log'.
    These runs have one or more independent simultaneous recordings of different sensors at different depth/time
    resolutions. Each of these simultaneous recordings is represented as a FrameArray object.

    - A LogPass consists of a set of FrameArray(s).
    - A FrameArray consists of a set of FrameChannel(s).
    - A FrameChannel consists of a set of values in a Numpy array of any shape from a single recorded channel (sensor).

    This is a file format independent design. Different file formats use this in different ways:

    * LIS79 - The standard allows 2 simultaneous FrameArrays, IFLR type 0, 1. Type 1 has never been seen in the wild.
    * LAS (all versions) - The standard excludes simultaneous FrameArrays.
    * RP66V1 - The standard allows for any number of simultaneous FrameArrays and this is common.
    * DAT - No simultaneous FrameArrays.
    * BIT - Custom and practice shows that there can be any number of simultaneous FrameArrays.
    """
    def __init__(self):
        # This is a list of independent recordings.
        # In the olden days we would record each of these on separate films.
        self.frame_arrays: typing.List[FrameArray] = []
        self.frame_array_map: typing.Dict[typing.Hashable, int] = {}

    def _invariant(self) -> bool:
        return len(self.frame_arrays) == len(self.frame_array_map)

    def has(self, key: typing.Hashable) -> bool:
        """Returns True if the key is in the Frame Array Map."""
        assert self._invariant()
        return key in self.frame_array_map

    def keys(self) -> typing.Iterable:
        """The identities of the Frame Arrays."""
        assert self._invariant()
        return self.frame_array_map.keys()

    def append(self, frame_array: FrameArray) -> None:
        """Add a channel to the Array."""
        assert self._invariant()
        if self.has(frame_array.ident):
            raise ExceptionLogPass(f'Duplicate FrameArray identity "{frame_array.ident}"')
        else:
            self.frame_array_map[frame_array.ident] = len(self.frame_arrays)
            self.frame_arrays.append(frame_array)

    def __str__(self) -> str:
        assert self._invariant()
        lines = [
            f'LogPass:'
        ]
        for fobj in self.frame_arrays:
            lines.extend(f'  {line}' for line in str(fobj).split('\n'))
        return '\n'.join(lines)

    def __len__(self) -> int:
        """The number of Frame Arrays."""
        assert self._invariant()
        return len(self.frame_arrays)

    def __getitem__(self, item: typing.Union[int, typing.Union[int, str, bytes]]) -> FrameArray:
        """The Frame Array by index or ID."""
        assert self._invariant()
        if isinstance(item, int):
            return self.frame_arrays[item]
        return self.frame_arrays[self.frame_array_map[item]]

