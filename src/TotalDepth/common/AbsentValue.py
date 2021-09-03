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
import typing

import numpy as np


#: Absent value as a float.
ABSENT_VALUE_FLOAT: float = -999.25
#: Absent value as an integer.
ABSENT_VALUE_INT: int = -999


def absent_value_from_array(array: np.ndarray) -> typing.Union[float, int, None]:
    """Returns the absent value depending on the dtype."""
    if np.issubdtype(array.dtype, np.integer):
        return ABSENT_VALUE_INT
    elif np.issubdtype(array.dtype, np.floating):
        return ABSENT_VALUE_FLOAT


def mask_absent_values(array: np.ndarray, absent_value: typing.Union[None, int, float] = None) -> np.ndarray:
    """Return a view on an array with the absent values masked out."""
    # data pointer: array.__array_interface__['data'][0]
    # New array
    # marr = np.ma.masked_equal(arr, 3)
    # View on original array:
    # marr2 = arr.view(np.ma.MaskedArray)
    # marr2.mask = arr == 3
    ret = array.view(np.ma.MaskedArray)
    if absent_value is None:
        mask_value = absent_value_from_array(array)
    else:
        mask_value = absent_value
    ret.mask = (array == mask_value)
    # Check that we have not created a new array but a view on the original one.
    assert ret.__array_interface__['data'][0] == array.__array_interface__['data'][0]
    return ret


def unmask_absent_values(array: np.ndarray) -> None:
    """Unmask values by setting the mask  to [False, ...] if present."""
    if hasattr(array, 'mask'):
        array.mask = [False,] * len(array)


def count_of_absent_values(array: np.ndarray) -> int:
    """Returns the count of the absent values."""
    ret = 0
    if np.issubdtype(array.dtype, np.integer):
        ret = np.count_nonzero(array == ABSENT_VALUE_INT)
    elif np.issubdtype(array.dtype, np.floating):
        ret = np.count_nonzero(array == ABSENT_VALUE_FLOAT)
    return ret
