"""
Indirectly Formatted Logical Records

"""
import logging

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core.File import LogicalData
from TotalDepth.RP66V1.core.RepCode import OBNAME, ObjectName, UVARI
from TotalDepth.util.bin_file_type import format_bytes


class ExceptionIFLR(ExceptionTotalDepthRP66V1):
    pass


logger = logging.getLogger(__file__)


class IndirectlyFormattedLogicalRecord:
    """Indirectly Formatted Logical Record has an OBNAME as its identity, a UVARI as the frame number then free data.

    Reference: [RP66V1 Section 3.3 Indirectly Formatted Logical Record]

    Reference: [RP66V1 Section 5.6.1 Frames] "The Frame Number is an integer (Representation Code UVARI) specifying the
    numerical order of the Frame in the Frame Type, counting sequentially from one."
    """
    def __init__(self, lr_type: int, ld: LogicalData):
        self.lr_type: int = lr_type
        # [RP66V1 Section 3.3 Indirectly Formatted Logical Record]
        self.object_name: ObjectName = OBNAME(ld)
        # [RP66V1 Section 5.6.1 Frames]
        self.frame_number = UVARI(ld)
        # if self.frame_number < 1:
        #     raise ExceptionIFLR(f'Frame number needs to be >= 1, not {self.frame_number}')
        if self.frame_number == 0:
            logger.warning(f'Frame number needs to be >= 1, not {self.frame_number} [RP66V1 Section 5.6.1 Frames]')
        self.preamble_length = ld.index
        self.logical_data: LogicalData = ld

    def rewind(self) -> None:
        """Resets the Logical Data to the start of the free data section immediately following the frame number."""
        self.logical_data.index = self.preamble_length

    def __str__(self):
        return f'<IndirectlyFormattedLogicalRecord {str(self.object_name.I):10}' \
            f' frame: {self.frame_number:8,d}' \
            f' free data[{self.logical_data.remain:4,d}]: {format_bytes(self.logical_data.view_remaining(16))}>'
