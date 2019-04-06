"""
Indirectly Formatted Logical Records

"""
from TotalDepth.RP66V1.core.File import LogicalData
from TotalDepth.RP66V1.core.RepCode import OBNAME, ObjectName, UVARI, SLONG
from TotalDepth.util.bin_file_type import format_bytes


class IndirectlyFormattedLogicalRecord:
    def __init__(self, lr_type: int, ld: LogicalData):
        self.lr_type: int = lr_type
        self.object_name: ObjectName = OBNAME(ld)
        # Frame number is the first value. [RP66V1 Section 5.6.1 Frames]
        # The value starts at unity.
        # TODO: Check frame_number > 0
        self.frame_number = UVARI(ld)
        self.bytes: bytes = ld.chunk(ld.remain)

    def __str__(self):
        return f'IFLR: {str(self.object_name.I):10} frame: {self.frame_number:8,d} data[{len(self.bytes):4,d}]: {format_bytes(self.bytes[:16])}'
