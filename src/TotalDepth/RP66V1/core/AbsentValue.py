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
Absent Value - a value that represents a missing value.

Unlike LIS79 which specifies an absent value in the DFSR, RP66V1 has no means of explicitly specifying an absent value.
Observation of real-world files shows the -999.25 is used for floats and -999 for integer representation codes.
"""
import typing

from TotalDepth.RP66V1.core import RepCode

from TotalDepth.common.AbsentValue import ABSENT_VALUE_FLOAT, ABSENT_VALUE_INT


def absent_value_from_rep_code(rep_code: int) -> typing.Union[float, int, None]:
    """Returns the absent value depending on the Representation Code."""
    category = RepCode.REP_CODE_CATEGORY_MAP[rep_code]
    if category == RepCode.NumericCategory.INTEGER:
        return ABSENT_VALUE_INT
    elif category == RepCode.NumericCategory.FLOAT:
        return ABSENT_VALUE_FLOAT
