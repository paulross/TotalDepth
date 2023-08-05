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
Provides analysis and navigation along the X axis of RP66V1 logs.
"""
import math
import typing

import numpy as np


class XAxisSpacingCounts(typing.NamedTuple):
    norm: int
    dupe: int
    skip: int
    back: int

    @property
    def total(self) -> int:
        return self.norm + self.dupe + self.skip + self.back


class XAxisSpacingSummary(typing.NamedTuple):
    min: float
    max: float
    mean: float
    median: float
    std: float
    counts: XAxisSpacingCounts
    histogram: typing.Tuple[np.ndarray, np.ndarray]

    def histogram_str(self, fmt='13.6', bar_width=80, char='*') -> str:
        counts, values = self.histogram
        counts_max = counts.max()
        int_width = 2 + int(math.log10(counts_max))
        ret = [
            f'{"Value":>{fmt[:fmt.find(".")]}} [{"N":>{int_width}}]: Relative Frequency'
        ]
        scale  = float(bar_width) / counts_max
        for i in range(len(counts)):
            ret.append(
                f'{values[i]:>{fmt}f} [{counts[i]:>{int_width}}]: {char * int(0.5 + scale * counts[i])}'
            )
        return '\n'.join(ret)

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            if self.min != other.min or self.max != other.max or self.mean != other.mean or self.median != other.median \
                    or self.std != other.std or self.counts != other.counts:
                return False
            for i in range(2): # pragma: no coverage
                if not (self.histogram[i] == other.histogram[i]).all():
                    return False
            return True
        return NotImplemented


SPACING_DEFINITIONS = """'backward' if space < -0.5 median
'duplicate' if -0.5 median <= space < 0.5 median
'normal' if 0.5 median <= space < 1.5 median
'skipped' if space >= 1.5 median
"""


def compute_spacing_counts(diff: np.ndarray) -> typing.Tuple[float, XAxisSpacingCounts]:
    median: float = np.median(diff)
    half = median / 2.0
    if median < 0:
        skipped: int = len(diff[diff < 3 * half])
        normal: int = len(diff[(diff < half) & (diff >= 3 * half)])
        duplicate: int = len(diff[(diff < -half) & (diff >= half)])
        back: int = len(diff[diff >= -half])
    else:
        skipped: int = len(diff[diff >= 3 * half])
        normal: int = len(diff[(diff >= half) & (diff < 3 * half)])
        duplicate: int = len(diff[(diff >= -half) & (diff < half)])
        back: int = len(diff[diff < -half])
    return median, XAxisSpacingCounts(normal, duplicate, skipped, back)


def compute_spacing(x_array: np.ndarray) -> typing.Union[XAxisSpacingSummary, None]:
    """Given an array this computes the summary of the first differential of the array or None if there are less than
    two values in the array.

    Given a median of the first differential, median, a subsequent differential, dx, is considered:
    'backward' if dx < -0.5 median
    'duplicate' if -0.5 median <= dx < 0.5 median
    'normal' if 0.5 median <= dx < 1.5 median
    'skipped' if dx >= 1.5 median
    """
    if len(x_array) > 1:
        diff = x_array[1:] - x_array[:-1]
        median, counts = compute_spacing_counts(diff)
        bins = 10 if diff.min() != diff.max() else 1
        return XAxisSpacingSummary(
            diff.min(), diff.max(), diff.mean(), float(median), diff.std(),
            counts,
            np.histogram(diff, bins=bins)
        )


class XAxisSummary(typing.NamedTuple):
    min: float
    max: float
    count: int
    # If there are < 2 values this will be None
    spacing: typing.Union[XAxisSpacingSummary, None]


def compute_x_axis_summary(x_array: np.ndarray) -> XAxisSummary:
    return XAxisSummary(x_array.min(), x_array.max(), len(x_array), compute_spacing(x_array))
