"""
This provides a file agnostic representation of a LogPass.

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
from TotalDepth.common import data_table, Slice

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


DEFAULT_NP_TYPE = np.float64


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
                 shape: typing.Tuple[int],
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
            raise ExceptionFrameArray(f'Duplicate channel identity {channel.ident}')
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

    def init_x_axis_array(self, number_of_frames: int) -> None:
        """
        Initialises an empty Numpy array for the first channel suitable to fill with <frames> number of frame data.
        """
        if number_of_frames <= 0:
            raise ExceptionFrameArray(f'Number of frames must be > 0 not {number_of_frames}')
        self.x_axis.init_array(number_of_frames)


class LogPass:
    """
    This represents the structure a single run of data acquisition such as 'Repeat Section' or 'Main Log'.
    These runs have one or more independent simultaneous recordings of different sensors at different depth/time
    resolutions. Each of these simultaneous recordings is represented as a FrameArray object.

    - A LogPass consists of a set of FrameArray(s).
    - A FrameArray consists of a set of FrameChannel(s).
    - A FrameChannel consists of a set of values in a Numpy array of any shape from a single recorded channel.


    This is a file format independent design. Different file formats use this in different ways:

    * LIS79 - While the format allows for two simultaneous recordings (IFLR types 0 and 1) this has never been seen
        in the wild.
    * LAS (all versions) - The format does not allow for multiple simultaneous recordings.
    * RP66V1 - The format allows for multiple simultaneous recordings and this is common.
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
            raise ExceptionLogPass(f'Duplicate FrameArray identity {frame_array.ident}')
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
        if item in self.frame_array_map:
            return self.frame_arrays[self.frame_array_map[item]]
        return self.frame_arrays[item]


# =================== Writing a Frame Array to LAS ===================
#: Possible methods to reduce an array to a single value.
ARRAY_REDUCTIONS = {'first', 'mean', 'median', 'min', 'max'}


def array_reduce(array: np.ndarray, method: str) -> typing.Union[float, int]:
    """Take a numpy array and apply a method to it to get a single value."""
    if method not in ARRAY_REDUCTIONS:
        raise ValueError(f'{method} is not in {ARRAY_REDUCTIONS}')
    if method == 'first':
        return array.flatten()[0]
    return getattr(np, method)(array)


def _stringify(value: typing.Union[str, bytes, typing.Any]) -> str:
    """Convert bytes to an ASCII string. Leave string untouched. str() everything else."""
    if isinstance(value, bytes):
        return value.decode("ascii")
    elif isinstance(value, str):
        return value
    return str(value)


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


def write_array_section_to_las(
        frame_array: FrameArray,
        max_num_available_frames: int,
        array_reduction: str,
        frame_slice: Slice.Slice,
        channel_name_sub_set: typing.Set[str],
        field_width: int,
        float_format: str,
        out_stream: typing.TextIO,
    ) -> None:
    """
    Write the ``~Array Section`` to the LAS file, the actual log data.

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
    if array_reduction not in ARRAY_REDUCTIONS:
        raise ValueError(f'Array reduction {array_reduction} not in {ARRAY_REDUCTIONS}')
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
    for frame_number in range(num_writable_frames):
        for c, channel in enumerate(frame_array.channels):
            if len(channel.array):
                value = array_reduce(channel.array[frame_number], array_reduction)
                if c > 0:
                    out_stream.write(' ')
                # if RepCode.REP_CODE_CATEGORY_MAP[channel.rep_code] == RepCode.NumericCategory.INTEGER:
                #     ostream.write(f'{value:{field_width}.0f}')
                # elif RepCode.REP_CODE_CATEGORY_MAP[channel.rep_code] == RepCode.NumericCategory.FLOAT:
                #     ostream.write(f'{value:{field_width}{float_format}}')
                # else:
                #     ostream.write(str(value))
                if issubclass(channel.array.dtype, np.int):
                    out_stream.write(f'{value:{field_width}.0f}')
                elif issubclass(channel.array.dtype, np.float):
                    out_stream.write(f'{value:{field_width}{float_format}}')
                else:
                    out_stream.write(str(value))
        out_stream.write('\n')
    # Garbage collect
    frame_array.init_arrays(1)

# =================== END: Writing a Frame Array to LAS ===================