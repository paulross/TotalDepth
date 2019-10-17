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

    def histogram_str(self, fmt='10.3', bar_width=80, char='*') -> str:
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


class IFLRReference(typing.NamedTuple):
    """POD class that represents the position of the IFLR in the file."""
    lrsh_position: int
    frame_number: int
    x_axis: typing.Union[int, float]


class XAxis:
    """This represents an X axis of a log pass for a particular object in that log pass.
    It has an ident, long name and units. It accumulates, for every IFLR in the set, the LRSH position, frame number
    and X axis value.
    """
    def __init__(self, ident: bytes, long_name: bytes, units: bytes):
        self.ident = ident
        self.long_name = long_name
        self.units = units
        self._data: typing.List[IFLRReference] = []
        self._summary: typing.Union[None, XAxisSummary] = None

    def append(self, lrsh_position: int, frame_number: int, x_axis: typing.Union[int, float]) -> None:
        # TODO: Verify the data position, frame number increasing etc.
        self._summary = None
        self._data.append(IFLRReference(lrsh_position, frame_number, x_axis))

    def __getitem__(self, item) -> IFLRReference:
        return self._data[item]

    def __len__(self) -> int:
        return len(self._data)

    @property
    def summary(self) -> XAxisSummary:
        if self._summary is None:
            self._compute_summary()
        return self._summary

    @property
    def is_increasing(self) -> bool:
        if len(self._data) < 2:
            raise AttributeError('Can not tell direction with < 2 points on the X axis.')
        return self._data[0].x_axis < self._data[-1].x_axis

    def _compute_summary(self) -> None:
        x_array: np.ndarray = np.empty(len(self._data), dtype=np.float64)
        for i in range(len(self._data)):
            x_array[i] = self._data[i].x_axis
        self._summary = XAxisSummary(x_array.min(), x_array.max(), len(x_array), compute_spacing(x_array))

    # TODO: Add an API that can turn an X axis value into the nearest frame number. Needs to cope with decreasing data.


