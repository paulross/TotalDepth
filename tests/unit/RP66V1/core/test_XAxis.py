import numpy as np
import pytest

from TotalDepth.RP66V1.core import XAxis


SPACING_COUNTS = (
    (np.array([1.0, 1.0, 1.0]), 1.0, XAxis.XAxisSpacingCounts(3, 0, 0, 0),),
    # Norm
    (np.array([1.0, 1.0, 1.1]), 1.0, XAxis.XAxisSpacingCounts(3, 0, 0, 0),),
    # Dupe
    (np.array([1.0, 1.0, 0.0]), 1.0, XAxis.XAxisSpacingCounts(2, 1, 0, 0),),
    # Skip
    (np.array([1.0, 1.0, 2.0]), 1.0, XAxis.XAxisSpacingCounts(2, 0, 1, 0),),
    # Back
    (np.array([1.0, 1.0, -1.0]), 1.0, XAxis.XAxisSpacingCounts(2, 0, 0, 1),),
)


@pytest.mark.parametrize('diff_array, exp_median, exp_counts', SPACING_COUNTS)
def test_compute_spacing_counts_median(diff_array, exp_median, exp_counts):
    median, _counts = XAxis.compute_spacing_counts(diff_array)
    assert exp_median == median


@pytest.mark.parametrize('diff_array, exp_median, exp_counts', SPACING_COUNTS)
def test_compute_spacing_counts_counts(diff_array, exp_median, exp_counts):
    _median, counts = XAxis.compute_spacing_counts(diff_array)
    assert exp_counts == counts


@pytest.mark.parametrize('diff_array, exp_median, exp_counts', SPACING_COUNTS)
def test_compute_spacing_counts_median_negative(diff_array, exp_median, exp_counts):
    median, _counts = XAxis.compute_spacing_counts(-diff_array)
    assert exp_median == -median


@pytest.mark.parametrize('diff_array, exp_median, exp_counts', SPACING_COUNTS)
def test_compute_spacing_counts_counts_negative(diff_array, exp_median, exp_counts):
    _median, counts = XAxis.compute_spacing_counts(-diff_array)
    assert exp_counts == counts


