"""
Extracts CHANNEL and FRAME data from a RP66V1 file to represent multiple sets of FRAME data.
"""
import typing
from functools import reduce

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
        self.name: ObjectName = channel_object.name
        self.long_name: bytes = channel_object[b'LONG-NAME'].value[0]
        self.rep_code: int = channel_object[b'REPRESENTATION-CODE'].value[0]
        self.units: bytes = channel_object[b'UNITS'].value[0]
        self.dimensions: typing.List[int] = channel_object[b'DIMENSION'].value
        self.count = reduce(lambda x, y: x * y, self.dimensions, 1)

    def read(self, ld: LogicalData) -> typing.List[float]:
        return [RepCode.code_read(self.rep_code, ld) for i in range(self.count)]


class FrameObject:
    """A single independent recording of channels.
    In the olden days we would record this on a single chunk of continuous film."""
    def __init__(self, frame_object: EFLR.Object, channel_eflr: EFLR.ExplicitlyFormattedLogicalRecord):
        self.obname = frame_object.name
        # TODO: Apply Semantic Restrictions?
        # Hmm, [RP66V1 Section 5.7.1 Frame Objects] says that C=1 for DESCRIPTION but our example data shows C=0
        self.description: bytes = b''
        if frame_object[b'DESCRIPTION'].count == 1:
            self.description = frame_object[b'DESCRIPTION'].value[0]
        channel_obnames: typing.List[ObjectName] = frame_object[b'CHANNELS'].value
        self.channels: typing.List[FrameChannel] = []
        for channel_obname in channel_obnames:
            if channel_obname in channel_eflr.object_name_map:
                self.channels.append(FrameChannel(channel_eflr[channel_obname]))
            else:
                raise ExceptionFrameObjectInit(f'Channel {channel_obname} not in CHANNEL EFLR.')

    def process_IFLR(self, iflr: IFLR.IndirectlyFormattedLogicalRecord):
        ld: LogicalData = LogicalData(iflr.bytes)
        result = []
        for channel in self.channels:
            result.append(channel.read(ld))
        return result


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
            obj.obname : i for i, obj in enumerate(self.frame_objects)
        }

    def __getitem__(self, item) -> FrameObject:
        if item in self.object_name_map:
            return self.frame_objects[self.object_name_map[item]]
        return self.frame_objects[item]

    def process_IFLR(self, iflr: IFLR.IndirectlyFormattedLogicalRecord):
        # TODO: Look up iflr.object_name in self
        obname: ObjectName = iflr.object_name
        if obname not in self.object_name_map:
            raise ExceptionLogPassProcessIFLR(f'ObjectName: {obname} not in LogPass')
        return self.frame_objects[self.object_name_map[obname]].process_IFLR(iflr)
