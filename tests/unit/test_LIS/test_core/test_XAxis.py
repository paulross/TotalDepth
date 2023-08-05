import numpy as np
import pytest

from TotalDepth.common import XAxis


@pytest.mark.parametrize(
    'norm, dupe, skip, back, expected',
    (
            (1, 2, 3, 4, 10),
    )
)
def test_xaxis_spacing_counts_total(norm, dupe, skip, back, expected):
    counts = XAxis.XAxisSpacingCounts(norm, dupe, skip, back)
    assert counts.total == expected


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


@pytest.mark.parametrize(
    'x_array, expected',
    (
            (
                    np.arange(1.0, 8.0, 1.0),
                    XAxis.XAxisSpacingSummary(min=1.0, max=1.0, mean=1.0, median=1.0, std=0.0,
                                              counts=XAxis.XAxisSpacingCounts(norm=6, dupe=0, skip=0, back=0),
                                              histogram=(np.array([6]), np.array([0.5, 1.5]))),
            ),
    )
)
def test_compute_spacing(x_array, expected):
    result = XAxis.compute_spacing(x_array)
    assert result == expected


@pytest.mark.parametrize(
    'x_array, expected',
    (
            (
                    np.arange(1.0, 8.0, 1.0),
                    XAxis.XAxisSpacingSummary(min=1.0, max=1.0, mean=1.0, median=1.0, std=0.0,
                                              counts=XAxis.XAxisSpacingCounts(norm=6, dupe=0, skip=0, back=0),
                                              histogram=(np.array([6]), np.array([0.5, 1.5]))),
            ),
    )
)
def test_compute_spacing_eq(x_array, expected):
    result = XAxis.compute_spacing(x_array)
    assert result == expected
    assert result != 1


@pytest.mark.parametrize(
    'x_array, expected',
    (
            (
                    np.arange(1.0, 8.0, 1.0),
                    """        Value [ N]: Relative Frequency
     0.500000 [ 6]: ********************************************************************************""",
            ),
            (
                    np.array(
                        [1.0, 1.5, 3.0, 4.5, 5.0, 6.0, 7.0, 8.0]
                    ),
                    """        Value [ N]: Relative Frequency
     0.500000 [ 2]: *****************************************************
     0.600000 [ 0]: 
     0.700000 [ 0]: 
     0.800000 [ 0]: 
     0.900000 [ 0]: 
     1.000000 [ 3]: ********************************************************************************
     1.100000 [ 0]: 
     1.200000 [ 0]: 
     1.300000 [ 0]: 
     1.400000 [ 2]: *****************************************************""",
            ),
    )
)
def test_compute_spacing_histogram_str(x_array, expected):
    x_axis = XAxis.compute_spacing(x_array)
    result = x_axis.histogram_str()
    print(result)
    assert result == expected


@pytest.mark.parametrize(
    'array_a, array_b, expected',
    (
            (np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.0]), True),
            (np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.5, 3.0]), False),
    )
)
def test_x_axis_spacing_summary_eq(array_a, array_b, expected):
    x_axis_a = XAxis.compute_spacing(array_a)
    x_axis_b = XAxis.compute_spacing(array_b)
    assert (x_axis_a == x_axis_b) == expected
    assert (x_axis_b == x_axis_a) == expected
    assert not x_axis_a == 1
