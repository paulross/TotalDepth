#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 1999-2020 Paul Ross
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
Provides means of summarizing a numpy ndarray.
"""
import functools

import numpy as np
import typing


class ArraySummary(typing.NamedTuple):
    """Contains the summary of an array of numbers."""
    len: int
    shape: typing.Tuple[int, ...]
    count: int
    min: float
    max: float
    mean: float
    std: float
    median: float
    count_eq: int
    count_dec: int
    count_inc: int
    activity: float
    drift: float  # (last - first) / length

    @property
    def span(self) -> float:
        """The max - min value."""
        return self.max - self.min


def count_eq(array: np.array, flatten: bool = True) -> int:
    """Count where adjacent values are equal."""
    if flatten:
        array = array.flatten()
    result = 0
    if len(array) > 1:
        result = np.count_nonzero(array[1:] == array[:-1])
    return result


def count_inc(array: np.array, flatten: bool = True) -> int:
    """Count where adjacent values are increasing."""
    if flatten:
        array = array.flatten()
    result = 0
    if len(array) > 1:
        result = np.count_nonzero(array[1:] > array[:-1])
    return result


def count_dec(array: np.array, flatten: bool = True) -> int:
    """Count where adjacent values are decreasing."""
    if flatten:
        array = array.flatten()
    result = 0
    if len(array) > 1:
        result = np.count_nonzero(array[1:] < array[:-1])
    return result


def count_eq_dec_inc(array: np.array, flatten: bool = True) -> typing.Tuple[int, int, int]:
    """
    Returns three counts: equal, decreasing, increasing.
    This is slightly more efficient as it only creates a diff array once.
    """
    if flatten:
        array = array.flatten()
    diff_array = array[1:] - array[:-1]
    if len(diff_array) and diff_array.dtype != np.dtype('O'):
        return np.count_nonzero(diff_array == 0), np.count_nonzero(diff_array < 0), np.count_nonzero(diff_array > 0)
    return 0, 0, 0


def activity(array: np.array, flatten: bool = True) -> float:
    """Returns array activity."""
    if flatten:
        array = array.flatten()
    result = 0.0
    if len(array) > 1:
        log2_array = np.log2(array)
        diff = log2_array[1:] - log2_array[:-1]
        result = np.abs(diff).mean()
    return result


def summarise_array(array: np.array, flatten: bool = True) -> ArraySummary:
    """Take an array and summarise it."""
    if flatten:
        array = array.flatten()
    len_array = functools.reduce(lambda x, y: x * y, array.shape, 1)
    count_of_values = len_array
    if hasattr(array, 'mask'):
        count_of_values -= np.count_nonzero(array.mask)
        # https://numpy.org/doc/stable/reference/maskedarray.generic.html#accessing-only-the-valid-entries
        array = array[~array.mask]
    counts = count_eq_dec_inc(array, flatten)
    if count_of_values > 1:
        result = ArraySummary(
            len_array,
            array.shape,
            count_of_values,
            array.min(),
            array.max(),
            array.mean(),
            array.std(),
            np.median(array),
            counts[0],
            counts[1],
            counts[2],
            activity(array),
            (array[-1] - array[0]) / (count_of_values - 1),
        )
        return result
