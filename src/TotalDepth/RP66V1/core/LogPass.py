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


def default_np_type(_rep_code: int) -> typing.Type:
    return np.float64


class FrameChannel:
    """
    This represents a single channel in a frame. It is file independent and can be used depending on the
    source of the information: LIS/LAS/RP66V1 file, XML index, Postgres database etc.
    """
    def __init__(self,
                 ident: typing.Hashable,
                 long_name: bytes,
                 rep_code: int,
                 units: bytes,
                 dimensions: typing.List[int],
                 # Function that takes an integer and returns a np.dtype for array creation.
                 function_np_dtype: typing.Callable = default_np_type,
                 ):
        self.ident: typing.Hashable = ident
        self.long_name: bytes = long_name
        self.rep_code: int = rep_code
        self.units: bytes = units
        self.dimensions: typing.List[int] = dimensions
        self.function_np_dtype: typing.Callable = function_np_dtype
        self.rank: int = len(self.dimensions)
        self.count: int = reduce(lambda x, y: x * y, self.dimensions, 1)
        # Allow space so that at least one frame can be read.
        self.array: np.ndarray = self._init_array(1)

    def __str__(self) -> str:
        return f'FrameChannel: {self.ident:8} Rc: {self.rep_code:3d} Co: {self.count:4d}' \
            f' Un: {str(self.units):12} Di: {self.dimensions} {self.long_name}'

    def _init_array(self, number_of_frames: int) -> np.ndarray:
        return np.empty((number_of_frames, *self.dimensions), dtype=self.function_np_dtype(self.rep_code))

    def init_array(self, number_of_frames: int) -> None:
        """
        Initialises an empty Numpy array suitable to fill with <frames> number of frame data for this channel.
        If an array already exists of the correct length it is reused.
        """
        if number_of_frames <= 0:
            raise ExceptionFrameChannel(f'Number of frames must be > 0 not {number_of_frames}')
        if self.array is None or len(self.array) != number_of_frames:
            self.array = self._init_array(number_of_frames)

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
        """Reads the Logical Data into the numpy frame at the specified frame number."""
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


def frame_channel_from_RP66V1(channel_object: EFLR.Object) -> FrameChannel:
    return FrameChannel(
        ident=channel_object.name,
        long_name=channel_object[b'LONG-NAME'].value[0] if channel_object[b'LONG-NAME'].value is not None else b'',
        rep_code=channel_object[b'REPRESENTATION-CODE'].value[0],
        units=channel_object[b'UNITS'].value[0],
        dimensions=channel_object[b'DIMENSION'].value,
        function_np_dtype=RepCode.numpy_dtype
    )


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
                f'FrameObject: {self.ident} {self.description}',
            ] + [f'  {str(c)}' for c in self.channels]
        )

    def __len__(self) -> int:
        return len(self.channels)

    def __getitem__(self, item: typing.Union[int, bytes]) -> FrameChannel:
        if item in self.channel_ident_map:
            return self.channels[self.channel_ident_map[item]]
        return self.channels[item]

    def init_arrays(self, number_of_frames: int) -> None:
        """
        Initialises empty Numpy arrays for each channel suitable to fill with <frames> number of frame data.
        """
        if number_of_frames <= 0:
            raise ExceptionFrameArray(f'Number of frames must be > 0 not {number_of_frames}')
        for channel in self.channels:
            channel.init_array(number_of_frames)

    def read(self, ld: LogicalData, frame_number: int) -> None:
        """Reads the Logical Data into the numpy frame."""
        for channel in self.channels:
            channel.read(ld, frame_number)

    def init_x_axis_array(self, number_of_frames: int) -> None:
        """
        Initialises an empty Numpy array for the first channel suitable to fill with <frames> number of frame data.
        """
        if number_of_frames <= 0:
            raise ExceptionFrameArray(f'Number of frames must be > 0 not {number_of_frames}')
        assert len(self.channels) > 0
        self.channels[0].init_array(number_of_frames)

    def read_x_axis(self, ld: LogicalData, frame_number: int) -> None:
        """Reads the first channel of the Logical Data into the numpy frame."""
        assert len(self.channels) > 0
        self.channels[0].read(ld, frame_number)


def frame_array_from_RP66V1(frame_object: EFLR.Object,
                            channel_eflr: EFLR.ExplicitlyFormattedLogicalRecord) -> FrameArray:
    if frame_object[b'DESCRIPTION'].count == 1 and frame_object[b'DESCRIPTION'].value is not None:
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


class LogPass:
    """
    This represents the structure a single run of data acquisition such as 'Repeat Section' or 'Main Log'.
    These runs have one or more independent simultaneous recordings of different sensors at different depth/time
    resolutions. Each of these simultaneous recordings is represented as a FrameObject

    This is a file format independent design. Different file formats use this in different ways:

        LIS79 - While the format allows for two simultaneous recordings (IFLR types 0 and 1) this has never been seen
            in the wild.
        LAS (all versions) - The format does not allow for multiple simultaneous recordings.
        RP66V1 - The format allows for multiple simultaneous recordings and this is common.

    Subclass this depending on the source of the information: DLIS file, XML index etc.
    """
    def __init__(self):
        # This is a list of independent recordings.
        # In the olden days we would record each of these on a separate chunks of separate films.
        self.frame_arrays: typing.List[FrameArray] = []
        self.frame_array_map: typing.Dict[typing.Hashable, int] = {}

    def has(self, key: typing.Hashable) -> bool:
        return key in self.frame_array_map

    def keys(self) -> typing.Iterable:
        return self.frame_array_map.keys()

    def append(self, frame_array: FrameArray) -> None:
        """Add a channel to the Array."""
        if self.has(frame_array.ident):
            raise ExceptionLogPassInit(f'Duplicate FrameArray identity {frame_array.ident}')
        else:
            self.frame_array_map[frame_array.ident] = len(self.frame_arrays)
            self.frame_arrays.append(frame_array)

    def __str__(self) -> str:
        lines = [
            f'LogPass:'
        ]
        for fobj in self.frame_arrays:
            lines.extend(f'  {line}' for line in str(fobj).split('\n'))
        return '\n'.join(lines)

    def __len__(self) -> int:
        return len(self.frame_arrays)

    def __getitem__(self, item: typing.Union[int, bytes]) -> FrameArray:
        if item in self.frame_array_map:
            return self.frame_arrays[self.frame_array_map[item]]
        return self.frame_arrays[item]


def log_pass_from_RP66V1(frame: EFLR.ExplicitlyFormattedLogicalRecord,
                         channels: EFLR.ExplicitlyFormattedLogicalRecord) -> LogPass:
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
