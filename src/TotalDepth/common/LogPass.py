#!/usr/bin/env python3
"""
This provides a file format agnostic representation of a LogPass.

- A LogPass consists of a set of FrameArray(s).
- A FrameArray consists of a set of FrameChannel(s).
- A FrameChannel consists of a set of values in a Numpy array of any shape from a single recorded channel.
"""

import functools
import itertools
import logging
import re
import typing

import numpy as np

from TotalDepth import ExceptionTotalDepth
from TotalDepth.common import data_table, Slice, AbsentValue

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

    def mask_array(self, absent_value: typing.Union[int, float]) -> None:
        """Masks the absent values."""
        self.array = AbsentValue.mask_absent_values(self.array, absent_value)


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


# =================== Writing a Frame Array to LAS ===================
#: Possible methods to reduce an array to a single value.
ARRAY_REDUCTIONS = {'first', 'mean', 'median', 'min', 'max'}


def _check_array_reduction(method: str) -> None:
    if method not in ARRAY_REDUCTIONS:
        raise ValueError(f'Array reduction method {method} is not in {sorted(ARRAY_REDUCTIONS)}')


def array_reduce(array: np.ndarray, method: str) -> typing.Union[float, int]:
    """Take a numpy array and apply a method to it to get a single value."""
    _check_array_reduction(method)
    if method == 'first':
        return array.flatten()[0]
    return getattr(np, method)(array)


RE_FLOAT_DECIMAL_FORMAT = re.compile(r'^\.[0-9]+')


def _check_float_decimal_places_format(float_decimal_places_format: str) -> None:
    """Raise if float format string is wrong."""
    m = RE_FLOAT_DECIMAL_FORMAT.match(float_decimal_places_format)
    if m is None:
        raise ValueError(f'Invalid float fractional format of "{float_decimal_places_format}"')


def _stringify(value: typing.Union[str, bytes, typing.Any]) -> str:
    """Convert bytes to an ASCII string. Leave string untouched. str() everything else."""
    if isinstance(value, bytes):
        return value.decode("ascii")
    elif isinstance(value, str):
        return value
    return str(value)


def _add_x_axis_to_channels_to_write(frame_array: FrameArray, channel_name_sub_set: typing.Set[typing.Hashable]) -> None:
    """Modifies channel_name_sub_set in-place to include x-axis."""
    if len(channel_name_sub_set) != 0:
        channel_name_sub_set.add(frame_array.x_axis.ident)


def write_curve_section_to_las(frame_array: FrameArray, channels: typing.Set[str], out_stream: typing.TextIO) -> None:
    """
    Write the ``~Curve Information Section`` to the LAS file.

    Example::

        ~Curve Information Section
        #MNEM.UNIT  Curve Description
        #---------  -----------------
        DEPT.m      : DEPT/Depth Dimensions: [1]
        TENS.lbs    : TENS/Tension Dimensions: [1]
        ETIM.min    : ETIM/Elapsed Time Dimensions: [1]
        DHTN.lbs    : DHTN/CH Tension Dimensions: [1]
        GR  .api    : GR/Gamma API Dimensions: [1]
    """
    out_stream.write('~Curve Information Section\n')
    table = [
        ['#MNEM.UNIT', 'Curve Description'],
        ['#---------', '-----------------'],
    ]
    for c, channel in enumerate(frame_array.channels):
        channel_ident_as_str = _stringify(channel.ident)
        if len(channels) == 0 or c == 0 or channel_ident_as_str in channels:
            table.append(
                [
                    f'{channel_ident_as_str:<4}.{_stringify(channel.units):<4}',
                    f': {_stringify(channel.long_name)} Dimensions: {channel.dimensions}',
                ]
            )
    rows = data_table.format_table(table, pad='  ', left_flush=True)
    for row in rows:
        out_stream.write(row)
        out_stream.write('\n')


def write_array_section_header_to_las(
        frame_array: FrameArray,
        max_num_available_frames: int,
        array_reduction: str,
        frame_slice: Slice.Slice,
        channel_name_sub_set: typing.Set[str],
        field_width: int,
        out_stream: typing.TextIO,
    ) -> None:
    """
    Write the ``~Array Section`` header to the LAS file, the actual log data.

    Example::

        # Array processing information:
        # Frame Array: ID: OBNAME: O: 2 C: 0 I: b'50' description: b''
        # All [5] original channels reproduced here.
        # Where a channel has multiple values the reduction method is by "first" value.
        # Number of original frames: 649
        # Requested frame slicing: <Slice on length=649 start=0 stop=649 step=1> total number of frames presented here: 649
        ~A          DEPT            TENS            ETIM            DHTN              GR
                2889.400        -999.250        -999.250        -999.250        -999.250
    """
    _check_array_reduction(array_reduction)
    # Write information about how the frames and channels were processed
    out_stream.write(f'# Array processing information:\n')
    out_stream.write(f'# Frame Array: ID: {frame_array.ident} description: {frame_array.description}\n')
    if len(channel_name_sub_set):
        original_channels = ','.join(_stringify(channel.ident) for channel in frame_array.channels)
        out_stream.write(f'# Original channels in Frame Array [{len(frame_array.channels):4d}]: {original_channels}\n')
        out_stream.write(
            f'# Requested Channels this LAS file [{len(channel_name_sub_set):4d}]: {",".join(channel_name_sub_set)}\n'
        )
    else:
        out_stream.write(f'# All [{len(frame_array.channels)}] original channels reproduced here.\n')
    out_stream.write(f'# Where a channel has multiple values the reduction method is by "{array_reduction}" value.\n')
    num_writable_frames = len(frame_array.x_axis)
    out_stream.write(f'# Maximum number of original frames: {max_num_available_frames}\n')
    out_stream.write(
        f'# Requested frame slicing: {frame_slice.long_str(max_num_available_frames)}'
        f', total number of frames presented here: {num_writable_frames}\n'
    )
    out_stream.write('~A')
    _add_x_axis_to_channels_to_write(frame_array, channel_name_sub_set)
    for c, channel in enumerate(frame_array.channels):
        if len(channel_name_sub_set) == 0 or c == 0 or channel.ident in channel_name_sub_set:
            if c == 0:
                out_stream.write(f'{channel.ident:>{field_width - 2}}')
            else:
                out_stream.write(' ')
                out_stream.write(f'{channel.ident:>{field_width}}')
    out_stream.write('\n')
    num_values = sum(c.count for c in frame_array.channels)
    logger.info(
        f'Writing array section with {num_writable_frames:,d} frames'
        f', {len(frame_array):,d} channels'
        f' and {num_values:,d} values per frame'
        f', total: {num_writable_frames * num_values:,d} input values.'
    )


def write_array_section_data_to_las(
            frame_array: FrameArray,
            array_reduction: str,
            channel_name_sub_set: typing.Set[str],
            field_width: int,
            float_decimal_places_format: str,
            out_stream: typing.TextIO,
    ) -> None:
    """
    Write the frame data into the ``~Array Section`` to the LAS file.
    This allows the caller to reduce the memory requirements by creating the FrameArray incrementally thus::

        write_curve_section_to_las(...)
        write_array_section_header_to_las(...)
        while True:
            # Initialise FrameArray...
            write_array_section_data_to_las(...)

    Example output (one frame)::

                2889.400        -999.250        -999.250        -999.250        -999.250
    """
    _check_float_decimal_places_format(float_decimal_places_format)
    _add_x_axis_to_channels_to_write(frame_array, channel_name_sub_set)
    num_writable_frames = len(frame_array.x_axis)
    for frame_number in range(num_writable_frames):
        for c, channel in enumerate(frame_array.channels):
            if len(channel_name_sub_set) == 0 or channel.ident in channel_name_sub_set:
                if len(channel.array) == 0:
                    raise ValueError(f'No frame data in channel {channel}')
                value = array_reduce(channel.array[frame_number], array_reduction)
                if c > 0:
                    out_stream.write(' ')
                if np.issubdtype(channel.array.dtype, np.integer):
                    out_stream.write(f'{value:{field_width}.0f}')
                elif np.issubdtype(channel.array.dtype, np.floating):
                    out_stream.write(f'{value:{field_width}{float_decimal_places_format}}')
                else:
                    out_stream.write(str(value))
        out_stream.write('\n')
    # To garbage collect the user can:
    # frame_array.init_arrays(0)


def write_array_section_to_las(
        frame_array: FrameArray,
        max_num_available_frames: int,
        array_reduction: str,
        frame_slice: Slice.Slice,
        channel_name_sub_set: typing.Set[str],
        field_width: int,
        float_decimal_places_format: str,
        out_stream: typing.TextIO,
    ) -> None:
    """
    Write the ``~Array Section`` header + log data to the LAS file.

    Example::

        # Array processing information:
        # Frame Array: ID: OBNAME: O: 2 C: 0 I: b'50' description: b''
        # All [5] original channels reproduced here.
        # Where a channel has multiple values the reduction method is by "first" value.
        # Number of original frames: 649
        # Requested frame slicing: <Slice on length=649 start=0 stop=649 step=1> total number of frames presented here: 649
        ~A          DEPT            TENS            ETIM            DHTN              GR
                2889.400        -999.250        -999.250        -999.250        -999.250
    """
    _check_float_decimal_places_format(float_decimal_places_format)
    write_array_section_header_to_las(frame_array, max_num_available_frames, array_reduction, frame_slice,
                                      channel_name_sub_set, field_width, out_stream)
    write_array_section_data_to_las(frame_array, array_reduction, channel_name_sub_set, field_width, float_decimal_places_format,
                                    out_stream)


def write_curve_and_array_section_to_las(
        frame_array: FrameArray,
        max_num_available_frames: int,
        array_reduction: str,
        frame_slice: Slice.Slice,
        channel_name_sub_set: typing.Set[str],
        field_width: int,
        float_decimal_places_format: str,
        out_stream: typing.TextIO,
    ) -> None:
    """
    Write the ``~Curve Information Section`` to the LAS file followed by the ``~Array Section`` header + log data to the
    LAS file.

    Example::

        ~Curve Information Section
        #MNEM.UNIT  Curve Description
        #---------  -----------------
        DEPT.m      : DEPT/Depth Dimensions: [1]
        TENS.lbs    : TENS/Tension Dimensions: [1]
        ETIM.min    : ETIM/Elapsed Time Dimensions: [1]
        DHTN.lbs    : DHTN/CH Tension Dimensions: [1]
        GR  .api    : GR/Gamma API Dimensions: [1]
        # Array processing information:
        # Frame Array: ID: OBNAME: O: 2 C: 0 I: b'50' description: b''
        # All [5] original channels reproduced here.
        # Where a channel has multiple values the reduction method is by "first" value.
        # Number of original frames: 649
        # Requested frame slicing: <Slice on length=649 start=0 stop=649 step=1> total number of frames presented here: 649
        ~A          DEPT            TENS            ETIM            DHTN              GR
                2889.400        -999.250        -999.250        -999.250        -999.250
    """
    _check_float_decimal_places_format(float_decimal_places_format)
    write_curve_section_to_las(frame_array, channel_name_sub_set, out_stream)
    write_array_section_to_las(frame_array, max_num_available_frames, array_reduction, frame_slice,
                               channel_name_sub_set, field_width, float_decimal_places_format, out_stream)

# =================== END: Writing a Frame Array to LAS ===================