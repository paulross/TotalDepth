"""
This provides a representation of the structure of recorded data.
"""
import itertools
import logging
import typing
from functools import reduce

import numpy as np

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


class FrameChannel:
    """
    This represents a single channel in a frame. It is file format independent and can be used depending on the
    source of the information: LIS/LAS/RP66V1 file, XML index, Postgres database etc.
    """
    def __init__(self,
                 ident: typing.Hashable,
                 long_name: bytes,
                 rep_code: int,
                 units: bytes,
                 dimensions: typing.List[int],
                 np_dtype: np.dtype = DEFAULT_NP_TYPE,
                 ):
        """
        Constructor.

        :param ident: Some hashable identity.
        :param long_name: A description of the channel
        :param rep_code: Integer representation code that this channel is encoded in.
        :param units: Units of  Measure.
        :param dimensions: A list of dimensions of each value. [1] is a single value per frame. [4, 1024] is a 100*2
            matrix such as sonic waveform of 1024 samples with 4 waveforms per frame.
        :param np_dtype: The numpy dtype to use.
        """
        self.ident: typing.Hashable = ident
        self.long_name: bytes = long_name
        self.rep_code: int = rep_code
        self.units: bytes = units
        self.dimensions: typing.List[int] = dimensions
        self.np_dtype: np.dtype = np_dtype
        self.rank: int = len(self.dimensions)
        self.count: int = reduce(lambda x, y: x * y, self.dimensions, 1)
        self.array: np.ndarray = self._init_array(0)

    def __str__(self) -> str:
        return f'FrameChannel: {self.ident:18} Rc: {self.rep_code:3d} Co: {self.count:4d}' \
            f' Un: {str(self.units):12} Di: {self.dimensions} {self.long_name}'

    def _init_array(self, number_of_frames: int) -> np.ndarray:
        return np.empty((number_of_frames, *self.dimensions), dtype=self.np_dtype)

    def init_array(self, number_of_frames: int) -> None:
        """
        Initialises an empty Numpy array suitable to fill with <frames> number of frame data for this channel.
        If an array already exists of the correct length it is reused.
        """
        if number_of_frames < 0:
            raise ExceptionFrameChannel(f'Number of frames must be >= 0 not {number_of_frames}')
        if self.array is None or len(self.array) != number_of_frames:
            self.array = self._init_array(number_of_frames)

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

    @property
    def shape(self) -> typing.Tuple[int, ...]:
        """The shape of the array."""
        return self.array.shape

    @property
    def len_input_bytes(self) -> int:
        """The number of RP66V1 bytes to read for one frame of this channel."""
        try:
            return self.count * RepCode.rep_code_fixed_length(self.rep_code)
        except RepCode.ExceptionRepCode as err:
            raise ExceptionFrameChannel(f'len_input_bytes() on variable length Rep Code {self.rep_code}') from err

    def numpy_indexes(self, frame_number: int) -> itertools.product:
        """
        Returns a generator of numpy indexes for a particular frame.

        Based on, given frame index 7::

            >>> list(itertools.product([7], [0,1], [0,1,2]))
            [(7, 0, 0), (7, 0, 1), (7, 0, 2), (7, 1, 0), (7, 1, 1), (7, 1, 2)]
            >>> list(itertools.product([7], range(2), range(3)))
            [(7, 0, 0), (7, 0, 1), (7, 0, 2), (7, 1, 0), (7, 1, 1), (7, 1, 2)]

        Usage, where `function` is a conversion function on the data::

            for dim in self.numpy_indexes(frame_number):
                # dim is a tuple of length self.rank + 1
                self.array[dim] = function(self.rep_code, data)
        """
        if frame_number < 0:
            raise ExceptionFrameChannel(f'FrameChannel.numpy_indexes() frame number must be > 0 not {frame_number}')
        products = [[frame_number]]
        for d in self.dimensions:
            products.append(range(d))
        return itertools.product(*products)

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


class FrameArray:
    """
    In the olden days we would record this on a single chunk of continuous film.

    Subclass this depending on the source of the information: DLIS file, XML index etc.
    """
    def __init__(self, ident: typing.Hashable, description: bytes):
        self.ident: typing.Hashable = ident
        # Hmm, [RP66V1 Section 5.7.1 Frame Objects] says that C=1 for DESCRIPTION but our example data shows C=0
        self.description: bytes = description
        self.channels: typing.List[FrameChannel] = []
        self.channel_ident_map: typing.Dict[typing.Hashable, int] = {}

    def has(self, key: typing.Hashable) -> bool:
        return key in self.channel_ident_map

    def keys(self) -> typing.Iterable:
        return self.channel_ident_map.keys()

    def append(self, channel: FrameChannel) -> None:
        """Add a channel to the Array."""
        if self.has(channel.ident):
            # raise ExceptionFrameObject(f'Duplicate channel identity {channel.ident}')
            logger.warning(f'Duplicate channel identity {channel.ident} ignored')
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

    def __getitem__(self, item: typing.Union[int, RepCode.ObjectName]) -> FrameChannel:
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
    def len_input_bytes(self) -> int:
        """The number of RP66V1 bytes to read for one frame."""
        return sum(ch.len_input_bytes for ch in self.channels)

    @property
    def shape(self) -> typing.List[typing.Tuple[int, ...]]:
        """The shape of the frame array."""
        return [a.shape for a in self.channels]

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
    def x_axis(self) -> FrameChannel:
        if len(self.channels) == 0:
            raise ExceptionFrameArray('Zero channels. Expected one channel as the X axis.')
        return self.channels[0]

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


class LogPass:
    """
    This represents the structure a single run of data acquisition such as 'Repeat Section' or 'Main Log'.
    These runs have one or more independent simultaneous recordings of different sensors at different depth/time
    resolutions. Each of these simultaneous recordings is represented as a FrameObject

    This is a file format independent design. Different file formats use this in different ways:

    * LIS79 - While the format allows for two simultaneous recordings (IFLR types 0 and 1) this has never been seen
        in the wild.
    * LAS (all versions) - The format does not allow for multiple simultaneous recordings.
    * RP66V1 - The format allows for multiple simultaneous recordings and this is common.

    Subclass this depending on the source of the information: DLIS file, XML index etc.
    """
    def __init__(self):
        # This is a list of independent recordings.
        # In the olden days we would record each of these on a separate chunks of separate films.
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
            raise ExceptionLogPassInit(f'Duplicate FrameArray identity {frame_array.ident}')
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

    def __getitem__(self, item: typing.Union[int, RepCode.ObjectName]) -> FrameArray:
        """The Frame Array by index or ID."""
        assert self._invariant()
        if item in self.frame_array_map:
            return self.frame_arrays[self.frame_array_map[item]]
        return self.frame_arrays[item]


# ====================== Constructing from RP66V1 data ====================

def frame_channel_from_RP66V1(channel_object: EFLR.Object) -> FrameChannel:
    """Create a file format agnostic FrameChannel from an EFLR.Object (row) in a `CHANNEL` EFLR."""
    return FrameChannel(
        ident=channel_object.name,
        long_name=channel_object[b'LONG-NAME'].value[0] if channel_object[b'LONG-NAME'].value is not None else b'',
        rep_code=channel_object[b'REPRESENTATION-CODE'].value[0],
        units=channel_object[b'UNITS'].value[0] if channel_object[b'UNITS'].value is not None else b'',
        dimensions=channel_object[b'DIMENSION'].value,
        # TODO: Replace this with the np.dtype directly
        np_dtype=RepCode.numpy_dtype(channel_object[b'REPRESENTATION-CODE'].value[0])
    )


def frame_array_from_RP66V1(frame_object: EFLR.Object,
                            channel_eflr: EFLR.ExplicitlyFormattedLogicalRecord) -> FrameArray:
    """Create a file format agnostic FrameArray from an EFLR.Object (row) in a `FRAME` EFLR and a `CHANNEL` EFLR."""
    # print('TRACE: frame_object.attr_label_map', frame_object.attr_label_map)
    key = b'DESCRIPTION'
    if key in frame_object.attr_label_map and frame_object[key].count == 1 and frame_object[key].value is not None:
        description = frame_object[b'DESCRIPTION'].value[0]
    else:
        description = b''
    frame_array = FrameArray(frame_object.name, description)
    # TODO: Apply Semantic Restrictions?
    # Hmm, [RP66V1 Section 5.7.1 Frame Objects] says that C=1 for DESCRIPTION but our example data shows C=0
    for channel_obname in frame_object[b'CHANNELS'].value:
        if channel_obname in channel_eflr.object_name_map:
            frame_array.append(frame_channel_from_RP66V1(channel_eflr[channel_obname]))
        else:
            raise ExceptionFrameArrayInit(f'Channel {channel_obname} not in CHANNEL EFLR.')
    return frame_array


def log_pass_from_RP66V1(frame: EFLR.ExplicitlyFormattedLogicalRecord,
                         channels: EFLR.ExplicitlyFormattedLogicalRecord) -> LogPass:
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
    log_pass = LogPass()
    # This is a list of independent recordings.
    # In the olden days we would record each of these on a separate chunks of separate films.
    for frame_object in frame.objects:
        log_pass.append(frame_array_from_RP66V1(frame_object, channels))
    return log_pass

# ====================== END: Constructing from RP66V1 data ====================
