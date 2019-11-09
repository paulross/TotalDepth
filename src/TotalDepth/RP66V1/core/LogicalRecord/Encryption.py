"""
Handles encryption in Logical Record Segments [RP66V1 Section 2.2.2.1], which is to say we do very little.

References:

    RP66V1: http://w3.energistics.org/rp66/v1/rp66v1.html

TODO: Ensure this is consistent across the storage unit?
"""
from TotalDepth.RP66V1.core.File import LogicalData
from TotalDepth.RP66V1.core.RepCode import UNORM


class LogicalRecordSegmentEncryptionPacket:

    def __init__(self, ld: LogicalData):
        self.size = UNORM(ld)
        self.producer_code = UNORM(ld)
        self.encryption_information = ld.chunk(self.size)
        self.bytes = ld.chunk(ld.remain)

    def __str__(self):
        return f'EncryptionPacket: size: 0x{self.size:04x}' \
            f' producer: {self.producer_code}' \
            f' code length: {len(self.encryption_information)} data length: {len(self.bytes)}'
