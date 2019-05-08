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
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR
from TotalDepth.RP66V1.core.LogicalRecord.Types import EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP
from TotalDepth.RP66V1.core.RepCode import ObjectName

logger = logging.getLogger(__file__)


class ExceptionLogPass(ExceptionTotalDepthRP66V1):
    pass


class ExceptionFrameChannel(ExceptionLogPass):
    pass


class ExceptionLogPassInit(ExceptionLogPass):
    pass


class ExceptionLogPassProcessIFLR(ExceptionLogPass):
    pass


class ExceptionFrameObject(ExceptionLogPass):
    pass


class ExceptionFrameObjectInit(ExceptionFrameObject):
    pass


def default_np_type(_rep_code: int) -> typing.Type:
    return np.float64


class FrameChannelBase:
    """
    This represents a single channel in a frame. It is file independent and should be subclassed this depending on the
    source of the information: LIS/LAS/RP66V1 file, XML index, Postgres database etc.

    Subclasses must decide how to populate an array typically with a function that takes self.rep_code and a data
    source.
    """
    def __init__(self,
                 ident: bytes,
                 long_name: bytes,
                 rep_code: int,
                 units: bytes,
                 dimensions: typing.List[int],
                 # Function that takes an integer and returns a np.dtype for array creation.
                 function_np_dtype: typing.Callable = default_np_type,
                 ):
        self.ident: bytes = ident
        self.long_name: bytes = long_name
        self.rep_code: int = rep_code
        self.units: bytes = units
        self.dimensions: typing.List[int] = dimensions
        self.function_np_dtype: typing.Callable = function_np_dtype
        self.rank: int = len(self.dimensions)
        self.count: int = reduce(lambda x, y: x * y, self.dimensions, 1)
        self.array: np.ndarray = None

    def __str__(self) -> str:
        return f'FrameChannel: {self.ident:8} Rc: {self.rep_code:3d} Co: {self.count:4d}' \
            f' Un: {str(self.units):12} Di: {self.dimensions} {self.long_name}'

    def init_array(self, number_of_frames: int) -> None:
        """
        Initialises an empty Numpy array suitable to fill with <frames> number of frame data for this channel.
        If an array already exists of the correct length it is reused.
        """
        if number_of_frames <= 0:
            raise ExceptionFrameChannel(
                f'FrameChannel.init_array() number of frames must be > 0 not {number_of_frames}'
            )
        if self.array is None or len(self.array) != number_of_frames:
            self.array = np.empty((number_of_frames, *self.dimensions), dtype=self.function_np_dtype(self.rep_code))

    def numpy_indexes(self, frame_number: int) -> itertools.product:
        """
        Returns a generator of numpy indexes for a particular frame.

        Usage, where `function` and `data` are defined by the sub-class::

            for dim in self.numpy_indexes(frame_number):
                # dim is a tuple of length self.rank + 1
                self.array[dim] = function(self.rep_code, data)
        """
        if frame_number <= 0:
            raise ExceptionFrameChannel(f'FrameChannel.numpy_indexes() frame number must be > 0 not {frame_number}')
        products = [[frame_number]]
        products.extend(range(d) for d in self.dimensions)
        return itertools.product(products)


class FrameChannelRP66V1(FrameChannelBase):
    """
    RP66V1 specialisation of a Frame Channel which provides read() methods.
    """
    def read(self, ld: LogicalData, frame_number: int) -> None:
        """Reads the Logical Data into the numpy frame."""
        if self.array is None:
            raise ExceptionFrameChannel(f'FrameChannelDLIS.read() array is not initialised.')
        if frame_number >= len(self.array):
            raise ExceptionFrameChannel(
                f'FrameChannelDLIS.read() frame number {frame_number} is > than array size {len(self.array)}.'
            )
        for dim in self.numpy_indexes(frame_number):
            # dim is a tuple of length self.rank + 1
            value = RepCode.code_read(self.rep_code, ld)
            self.array[dim] = value

    # TODO: Fix this to use read() above.
    # TODO: Get rid of these this read() read_one(), append() and use numpy.
    def read(self, ld: LogicalData) -> typing.List[float]:
        return [RepCode.code_read(self.rep_code, ld) for _i in range(self.count)]

    def read_one(self, ld: LogicalData) -> typing.Union[float, int]:
        # print(f'TRACE: FrameChannel {ld}')
        return RepCode.code_read(self.rep_code, ld)

    def append(self, ld: LogicalData, data: typing.List[typing.Any]) -> None:
        if self.count == 1:
            data.append(RepCode.code_read(self.rep_code, ld))
        else:
            data.append([RepCode.code_read(self.rep_code, ld) for _i in range(self.count)])


class FrameChannelRP66V1File(FrameChannelRP66V1):
    """
    A specialisation of a FrameChannel created from a RP66V1 file.
    """
    def __init__(self, channel_object: EFLR.Object):
        # TODO: Apply Semantic Restrictions
        # TODO: Further to the above, check no multiple values for those fields that we are indexing [0].
        self.object_name = channel_object.name
        super().__init__(
            ident=channel_object.name.I,
            long_name=channel_object[b'LONG-NAME'].value[0] if channel_object[b'LONG-NAME'].value is not None else b'',
            rep_code=channel_object[b'REPRESENTATION-CODE'].value[0],
            units=channel_object[b'UNITS'].value[0],
            dimensions=channel_object[b'DIMENSION'].value,
            function_np_dtype=RepCode.numpy_dtype
        )


class FrameArrayBase:
    """
    In the olden days we would record this on a single chunk of continuous film.

    Subclass this depending on the source of the information: DLIS file, XML index etc.
    """
    def __init__(self, ident: bytes):
        self.ident: bytes = ident
        # Hmm, [RP66V1 Section 5.7.1 Frame Objects] says that C=1 for DESCRIPTION but our example data shows C=0
        self.description: bytes = b''
        self.channels: typing.List[FrameChannelBase] = []
        self.channel_ident_map: typing.Dict[bytes, int] = {}

    def _init_channel_map(self) -> None:
        self.channel_ident_map = {}
        for c, channel in enumerate(self.channels):
            if channel.ident in self.channel_ident_map:
                # raise ExceptionFrameObject(f'Duplicate channel identity {channel.ident}')
                logger.warning(f'Duplicate channel identity {channel.ident} ignored')
            else:
                self.channel_ident_map[channel.ident] = c

    def __str__(self) -> str:
        return '\n'.join(
            [
                f'FrameObject: {self.ident} {self.description}',
            ] + [f'  {str(c)}' for c in self.channels]
        )

    def __getitem__(self, item: typing.Union[int, bytes]) -> FrameChannelBase:
        if item in self.channel_ident_map:
            return self.channels[self.channel_ident_map[item]]
        return self.channels[item]

    def init_arrays(self, number_of_frames: int) -> None:
        """
        Initialises empty Numpy arrays for each channel suitable to fill with <frames> number of frame data.
        """
        if number_of_frames <= 0:
            raise ExceptionFrameObject(f'FrameObject.init_array() number of frames must be > 0 not {number_of_frames}')
        for channel in self.channels:
            channel.init_array(number_of_frames)


class FrameArrayRP66V1(FrameArrayBase):
    """
    A single independent recording of channels along a particular axis which is the first channel. Reference
    [RP66V1 Section 5.7.1 Frame Objects Figure 5-8 Comment 2 "When a Frame has an Index, then it must be the first
    Channel in the Frame, and it must be scalar."].
    """
    def __init__(self, object_name: ObjectName):
        self.object_name = object_name
        super().__init__(object_name.I)


    def read(self, ld: LogicalData, frame_number: int) -> None:
        """Reads the Logical Data into the numpy frame."""
        for channel in self.channels:
            channel.read(ld, frame_number)

    # TODO: This is IFLR processing that should be left to the FrameArray class
    def process_IFLR(self, iflr: IFLR.IndirectlyFormattedLogicalRecord) -> typing.List[typing.List[float]]:
        ld: LogicalData = LogicalData(iflr.bytes)
        result: typing.List[typing.List[float]] = []
        for channel in self.channels:
            result.append(channel.read(ld))
        return result

    def append(self, iflr: IFLR.IndirectlyFormattedLogicalRecord, data: typing.List[typing.List[typing.Any]]) -> None:
        if len(data) == 0:
            for c in range(len(self.channels)):
                data.append([])
        # assert len(data) == len(self.channels)
        ld: LogicalData = LogicalData(iflr.bytes)
        for c, channel in enumerate(self.channels):
            channel.append(ld, data[c])

    def first_channel_value(self, iflr: IFLR.IndirectlyFormattedLogicalRecord) -> typing.Union[float, int]:
        assert len(self.channels)
        # TODO: Efficiency here, is this slow?
        ld: LogicalData = LogicalData(iflr.bytes)
        return self.channels[0].read_one(ld)


class FrameArrayRP66V1File(FrameArrayRP66V1):

    def __init__(self, frame_object: EFLR.Object, channel_eflr: EFLR.ExplicitlyFormattedLogicalRecord):
        super().__init__(frame_object.name)
        # TODO: Apply Semantic Restrictions?
        # Hmm, [RP66V1 Section 5.7.1 Frame Objects] says that C=1 for DESCRIPTION but our example data shows C=0
        if frame_object[b'DESCRIPTION'].count == 1 and frame_object[b'DESCRIPTION'].value is not None:
            self.description = frame_object[b'DESCRIPTION'].value[0]
        for channel_obname in frame_object[b'CHANNELS'].value:
            if channel_obname in channel_eflr.object_name_map:
                self.channels.append(FrameChannelRP66V1File(channel_eflr[channel_obname]))
            else:
                raise ExceptionFrameObjectInit(f'Channel {channel_obname} not in CHANNEL EFLR.')
        self._init_channel_map()


class LogPassBase:
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
        self.frame_objects: typing.List[FrameArrayBase] = []
        self.frame_object_map: typing.Dict[bytes, int] = {}

    def _init_frame_object_map(self) -> None:
        self.frame_object_map = {}
        for f, frame in enumerate(self.frame_objects):
            if frame.ident in self.frame_object_map:
                raise ExceptionLogPassInit(f'Duplicate frame object identity {frame.ident}')
            self.frame_object_map[frame.ident] = f

    def __str__(self) -> str:
        lines = [
            f'LogPass:'
        ]
        for fobj in self.frame_objects:
            lines.extend(f'  {line}' for line in str(fobj).split('\n'))
        return '\n'.join(lines)

    def __getitem__(self, item: typing.Union[int, bytes]) -> FrameArrayBase:
        if item in self.frame_object_map:
            return self.frame_objects[self.frame_object_map[item]]
        return self.frame_objects[item]


class LogPassRP66V1(LogPassBase):
    # TODO: This is IFLR processing that should be left to the FrameArray class
    def process_IFLR(self, iflr: IFLR.IndirectlyFormattedLogicalRecord) -> typing.List[typing.List[float]]:
        object_name: ObjectName = iflr.object_name
        if object_name.I not in self.frame_object_map:
            raise ExceptionLogPassProcessIFLR(f'ObjectName: {object_name.I} not in LogPass: {self.frame_object_map.keys()}')
        return self.frame_objects[self.frame_object_map[object_name.I]].process_IFLR(iflr)

    def append(self, iflr: IFLR.IndirectlyFormattedLogicalRecord, data: typing.List[typing.List[typing.Any]]) -> None:
        object_name: ObjectName = iflr.object_name
        if object_name.I not in self.frame_object_map:
            raise ExceptionLogPassProcessIFLR(f'ObjectName: {object_name.I} not in LogPass: {self.frame_object_map.keys()}')
        self.frame_objects[self.frame_object_map[object_name.I]].append(iflr, data)

    def first_channel_value(self, iflr: IFLR.IndirectlyFormattedLogicalRecord) -> typing.Union[float, int]:
        """
        Given an IFLR this returns the first Channel value as a number.
        The first channel is the Index Channel [RP66V1 Section 5.6.1 Frames Para 3]
        """
        obname: ObjectName = iflr.object_name
        if obname.I not in self.frame_object_map:
            raise ExceptionLogPassProcessIFLR(f'ObjectName: {obname.I} not in LogPass: {self.frame_object_map.keys()}')
        return self.frame_objects[self.frame_object_map[obname.I]].first_channel_value(iflr)


class LogPassRP66V1File(LogPassRP66V1):
    """
    This class is constructed with a FRAME EFLR that represents the independent simultaneous recordings and the X axis
    and a CHANNEL EFLR that represents all known channels (representation codes, dimensions etc.).
    """
    def __init__(self, frame: EFLR.ExplicitlyFormattedLogicalRecord, channels: EFLR.ExplicitlyFormattedLogicalRecord):
        super().__init__()
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
        # This is a list of independent recordings.
        # In the olden days we would record each of these on a separate chunks of separate films.
        self.frame_objects: typing.List[FrameArrayRP66V1File] = [
            FrameArrayRP66V1File(obj, channels) for obj in frame.objects
        ]
        self._init_frame_object_map()


