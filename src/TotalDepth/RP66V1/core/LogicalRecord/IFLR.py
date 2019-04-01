"""
Indirectly Formatted Logical Records

"""
from TotalDepth.RP66V1.core.File import LogicalData
from TotalDepth.RP66V1.core.RepCode import OBNAME, ObjectName
from TotalDepth.util.bin_file_type import format_bytes


class IndirectlyFormattedLogicalRecord:
    def __init__(self, ld: LogicalData):
        self.object_name: ObjectName = OBNAME(ld)
        self.bytes: bytes = ld.chunk(ld.remain)

    def __str__(self):
        return f'IFLR: {self.object_name} data: {format_bytes(self.bytes[:16])}'
