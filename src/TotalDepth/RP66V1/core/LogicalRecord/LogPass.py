"""
Extracts CHANNEL and FRAME data from a RP66V1 file to represent multiple sets of FRAME data.
"""
import itertools
import typing
from functools import reduce

import numpy as np

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core.File import LogicalData
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR
from TotalDepth.RP66V1.core.LogicalRecord.Types import EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP
from TotalDepth.RP66V1.core.RepCode import ObjectName


class ExceptionLogPass(ExceptionTotalDepthRP66V1):
    pass


class ExceptionLogPassInit(ExceptionLogPass):
    pass


class ExceptionLogPassProcessIFLR(ExceptionLogPass):
    pass


class ExceptionFrameObjectInit(ExceptionLogPass):
    pass


class FrameChannel:
    def __init__(self, channel_object: EFLR.Object):
        # TODO: Apply Semantic Restrictions
        self.object_name: ObjectName = channel_object.name
        self.long_name: bytes = b''
        if channel_object[b'LONG-NAME'].value is not None:
            self.long_name: bytes = channel_object[b'LONG-NAME'].value[0]
        self.rep_code: int = channel_object[b'REPRESENTATION-CODE'].value[0]
        self.units: bytes = channel_object[b'UNITS'].value[0]
        self.dimensions: typing.List[int] = channel_object[b'DIMENSION'].value
        self.count = reduce(lambda x, y: x * y, self.dimensions, 1)

    def __str__(self) -> str:
        return f'FrameChannel: {self.object_name:8} Rc: {self.rep_code:3d} Co: {self.count:4d}' \
            f' Un: {str(self.units):12} Di: {self.dimensions} {self.long_name}'

    def read(self, ld: LogicalData) -> typing.List[float]:
        return [RepCode.code_read(self.rep_code, ld) for _i in range(self.count)]

    def read_one(self, ld: LogicalData) -> typing.Union[float, int]:
        return RepCode.code_read(self.rep_code, ld)

    def append(self, ld: LogicalData, data: typing.List[typing.Any]) -> None:
        if self.count == 1:
            data.append(RepCode.code_read(self.rep_code, ld))
        else:
            data.append([RepCode.code_read(self.rep_code, ld) for _i in range(self.count)])

    def numpy_empty(self, frames: int) -> np.ndarray:
        """Returns an empty Numpy array suitable to fill with <frames> number of frame data for this channel."""
        return np.empty((frames, *self.dimensions), dtype=RepCode.numpy_dtype(self.rep_code))

    def numpy_indexes(self, frame: int) -> itertools.product:# typing.Sequence[typing.Tuple[int, ...]]:
        """Returns a generator of numpy indexes."""
        # TODO: Test
        products = [frame]
        products.extend(range(d) for d in self.dimensions)
        return itertools.product(products)

    def numpy_fill(self, ld: LogicalData, array: np.ndarray, frame: int) -> None:
        """Writes into a Numpy array from logical data."""
        # TODO: Test
        for dim in self.numpy_indexes(frame):
            # dim is a tuple of length self.dimensions
            value = RepCode.code_read(self.rep_code, ld)
            array[dim] = value


class FrameObject:
    """A single independent recording of channels.
    In the olden days we would record this on a single chunk of continuous film."""
    def __init__(self, frame_object: EFLR.Object, channel_eflr: EFLR.ExplicitlyFormattedLogicalRecord):
        self.object_name: ObjectName = frame_object.name
        # TODO: Apply Semantic Restrictions?
        # Hmm, [RP66V1 Section 5.7.1 Frame Objects] says that C=1 for DESCRIPTION but our example data shows C=0
        self.description: bytes = b''
        if frame_object[b'DESCRIPTION'].count == 1 and frame_object[b'DESCRIPTION'].value is not None:
            self.description = frame_object[b'DESCRIPTION'].value[0]
        channel_obnames: typing.List[ObjectName] = frame_object[b'CHANNELS'].value
        self.channels: typing.List[FrameChannel] = []
        for channel_obname in channel_obnames:
            if channel_obname in channel_eflr.object_name_map:
                self.channels.append(FrameChannel(channel_eflr[channel_obname]))
            else:
                raise ExceptionFrameObjectInit(f'Channel {channel_obname} not in CHANNEL EFLR.')
        self.object_name_map: typing.Dict[ObjectName, int] = {
            object_name : i for i, object_name in enumerate(channel_obnames)
        }

    def __str__(self) -> str:
        return '\n'.join(
            [
                f'FrameObject: {self.object_name} {self.description}',
            ] + [f'  {str(c)}' for c in self.channels]
        )

    def __getitem__(self, item) -> FrameChannel:
        if item in self.object_name_map:
            return self.channels[self.object_name_map[item]]
        return self.channels[item]

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


class LogPass:
    def __init__(self, frame: EFLR.ExplicitlyFormattedLogicalRecord, channels: EFLR.ExplicitlyFormattedLogicalRecord):
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
        self.frame_objects: typing.List[FrameObject] = [FrameObject(obj, channels) for obj in frame.objects]
        self.object_name_map: typing.Dict[ObjectName, int] = {
            obj.object_name: i for i, obj in enumerate(self.frame_objects)
        }

    def __str__(self) -> str:
        lines = [
            f'LogPass:'
        ]
        for fobj in self.frame_objects:
            lines.extend(f'  {line}' for line in str(fobj).split('\n'))
        return '\n'.join(lines)

    def __getitem__(self, item) -> FrameObject:
        if item in self.object_name_map:
            return self.frame_objects[self.object_name_map[item]]
        return self.frame_objects[item]

    def process_IFLR(self, iflr: IFLR.IndirectlyFormattedLogicalRecord):
        object_name: ObjectName = iflr.object_name
        if object_name not in self.object_name_map:
            raise ExceptionLogPassProcessIFLR(f'ObjectName: {object_name} not in LogPass: {self.object_name_map.keys()}')
        return self.frame_objects[self.object_name_map[object_name]].process_IFLR(iflr)

    def append(self, iflr: IFLR.IndirectlyFormattedLogicalRecord, data: typing.List[typing.List[typing.Any]]) -> None:
        object_name: ObjectName = iflr.object_name
        if object_name not in self.object_name_map:
            raise ExceptionLogPassProcessIFLR(f'ObjectName: {object_name} not in LogPass: {self.object_name_map.keys()}')
        self.frame_objects[self.object_name_map[object_name]].append(iflr, data)

    def first_channel_value(self, iflr: IFLR.IndirectlyFormattedLogicalRecord) -> typing.Union[float, int]:
        """
        Given an IFLR this returns the first Channel value as a number.
        The first channel is the Index Channel [RP66V1 Section 5.6.1 Frames Para 3]
        """
        obname: ObjectName = iflr.object_name
        if obname not in self.object_name_map:
            raise ExceptionLogPassProcessIFLR(f'ObjectName: {obname} not in LogPass: {self.object_name_map.keys()}')
        return self.frame_objects[self.object_name_map[obname]].first_channel_value(iflr)
