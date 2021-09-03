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
Indirectly Formatted Logical Records

"""
import logging

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import File, RepCode


class ExceptionIFLR(ExceptionTotalDepthRP66V1):
    pass


logger = logging.getLogger(__file__)


class IndirectlyFormattedLogicalRecord:
    """Indirectly Formatted Logical Record has an OBNAME as its identity, a UVARI as the frame number then free data.
    This just reads the OBNAME and UVARI but not the free data.

    Reference: [RP66V1 Section 3.3 Indirectly Formatted Logical Record]

    Reference: [RP66V1 Section 5.6.1 Frames] "The Frame Number is an integer (Representation Code UVARI) specifying the
    numerical order of the Frame in the Frame Type, counting sequentially from one."
    """
    def __init__(self, lr_type: int, ld: File.LogicalData):
        self.lr_type: int = lr_type
        ld.rewind()
        # [RP66V1 Section 3.3 Indirectly Formatted Logical Record]
        self.object_name: RepCode.ObjectName = RepCode.OBNAME(ld)
        # [RP66V1 Section 5.6.1 Frames]
        self.frame_number = RepCode.UVARI(ld)
        self.preamble_length = ld.index
        self.remain = ld.remain
        # Frame numbers start from 1 but there are many observed cases of IFLRs that have a 0 frame number and zero
        # remaining data. Here we only warn if the frame number is zero and the remaining data is non-zero.
        # We warn rather than raising in the spirit of optimism.
        if self.frame_number == 0 and self.remain != 0:
            logger.warning(
                f'Frame number needs to be >= 1, not {self.frame_number} [RP66V1 Section 5.6.1 Frames] (there is data remaining)'
            )

    def __str__(self):
        return f'<IndirectlyFormattedLogicalRecord {str(self.object_name)}' \
            f' frame: {self.frame_number:,d}' \
            f' free data: {self.remain:,d}>'
