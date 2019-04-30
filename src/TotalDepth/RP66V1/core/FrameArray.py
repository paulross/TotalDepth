"""
A FrameArray object contains log data.
"""
from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import LogPass
from TotalDepth.RP66V1.core.LogicalRecord import IFLR


class ExceptionLogPass(ExceptionTotalDepthRP66V1):
    pass


class FrameArray:

    def __init__(self, log_pass: LogPass.LogPass):
        self.log_pass = log_pass
        self.frame_data = {}

    def init_numpy(self, iflr: IFLR.IndirectlyFormattedLogicalRecord, num_frames: int) -> None:
        pass
