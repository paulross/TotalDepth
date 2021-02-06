#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation.
# Copyright (C) 2011-2021 Paul Ross
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Paul Ross: apaulross@gmail.com
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
