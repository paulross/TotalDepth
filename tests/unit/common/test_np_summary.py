import pytest

import numpy as np

from TotalDepth.common import np_summary


@pytest.mark.parametrize(
    'array, expected',
    (
        (np.array([2.0**i for i in range(8)]), 1.0),
    )
)
def test_activity_unmasked(array, expected):
    result = np_summary.activity(array)
    assert result == expected


@pytest.mark.parametrize(
    'array, null_value, expected',
    (
        (np.array([2.0**i for i in range(8)]), 4.0, 1.0),
    )
)
def test_activity_masked(array, null_value, expected):
    masked_array = array.view(np.ma.MaskedArray)
    masked_array.mask = (array == null_value)
    result = np_summary.activity(masked_array)
    assert result == expected


@pytest.mark.parametrize(
    'array, null_value, expected',
    (
        (
            np.array([]), None, None,
        ),
        (
            np.array([]), 1.0, None,
        ),
        (
            np.array([1.0,]), None, None,
        ),
        (
            np.array([1.0]), 1.0, None,
        ),
        (
            np.array([1.0, 1.0]),
            None,
            np_summary.ArraySummary(len=2, shape=(2,), count=2, min=1.0, max=1.0, mean=1.0, std=0.0, median=1.0,
                                    count_eq=1, count_dec=0, count_inc=0, activity=0.0),
        ),
        (
            np.array([1.0, 1.0]),
            2.0,
            np_summary.ArraySummary(len=2, shape=(2,), count=2, min=1.0, max=1.0, mean=1.0, std=0.0, median=1.0,
                                    count_eq=1, count_dec=0, count_inc=0, activity=0.0),
        ),
        (
            np.array([1.0, 1.0]),
            2.0,
            np_summary.ArraySummary(len=2, shape=(2,), count=2, min=1.0, max=1.0, mean=1.0, std=0.0, median=1.0,
                                    count_eq=1, count_dec=0, count_inc=0, activity=0.0),
        ),
        (
            np.array([2.0 ** i for i in range(8)]),
            None,
            np_summary.ArraySummary(len=8, shape=(8,), count=8, min=1.0, max=128.0, mean=31.875, std=41.40784195052913,
                                    median=12.0, count_eq=0, count_dec=0, count_inc=7, activity=1.0)
        ),
        (
            np.array([2.0 ** i for i in range(8)]),
            4.0,
            np_summary.ArraySummary(len=8, shape=(8,), count=7, min=1.0, max=128.0, mean=35.857142857142854,
                                    std=42.809974042867864, median=12.0, count_eq=0, count_dec=0, count_inc=7,
                                    activity=1.0)
        ),
    )
)
def test_summarise_array(array, null_value, expected):
    if null_value is None:
        result = np_summary.summarise_array(array)
    else:
        masked_array = array.view(np.ma.MaskedArray)
        masked_array.mask = (array == null_value)
        result = np_summary.summarise_array(masked_array)
    assert result == expected
