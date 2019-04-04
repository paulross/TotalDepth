"""
Extracts CHANNEL and FRAME data from a RP66V1 file to represent multiple sets of FRAME data.
"""
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR
from TotalDepth.RP66V1.core.RepCode import ObjectName


class ExceptionLogPass(ExceptionTotalDepthRP66V1):
    pass


class ExceptionLogPassInit(ExceptionLogPass):
    pass


class FrameChannel:
    def __init__(self, channel_object: EFLR.Object):
        # TODO: Apply Semantic Restrictions
        pass


class FrameObject:
    """A single independent recording of channels.
    In the olden days we would record this on a single chunk of continuous film."""
    def __init__(self, obj: EFLR.Object, channel: EFLR.ExplicitlyFormattedLogicalRecord):
        self.description: bytes = obj[b'DESCRIPTION'][0]
        self.channels: typing.List[ObjectName] = obj[b'CHANNELS']


class LogPass:
    def __init__(self, frame: EFLR.ExplicitlyFormattedLogicalRecord, channel: EFLR.ExplicitlyFormattedLogicalRecord):
        if frame.lr_type != 4:
            raise ExceptionLogPassInit(f"Expected frame Logical Record type to be 4 but got {frame.lr_type}")
        if frame.set.type != b'FRAME':
            raise ExceptionLogPassInit(f"Expected frame set type to be b'FRAME' but got {frame.set.type}")
        if channel.lr_type != 3:
            raise ExceptionLogPassInit(f"Expected channel Logical Record type to be 3 but got {channel.lr_type}")
        if channel.set.type != b'CHANNEL':
            raise ExceptionLogPassInit(f"Expected channel set type to be b'CHANNEL' but got {channel.set.type}")
        # This is a list of independent recordings.
        # In the olden days we would record each of these on a separate chunks of separate films.
        self.frame_objects: typing.List[FrameObject] = [FrameObject(obj, channel) for obj in frame.objects]

    def add_IFLR(self, iflr: IFLR.IndirectlyFormattedLogicalRecord) -> None:
        # TODO: Look up iflr.object_name in self
        pass
