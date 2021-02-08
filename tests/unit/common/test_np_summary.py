import datetime

import pytest

import numpy as np

from TotalDepth.common import np_summary


def test_array_summary_span():
    value = np_summary.ArraySummary(len=8, shape=(7,), count=7, min=1.0, max=128.0, mean=35.857142857142854,
                                    std=42.809974042867864, median=16.0, count_eq=0, count_dec=0, count_inc=6,
                                    activity=1.0 + 1 / 6, first=0.0, last=(128.0 - 1.0) / (8 - 2))
    assert value.span == 127


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
    'array, expected',
    (
        (np.array([]), 0),
        (np.arange(8.0), 0),
        (np.array([1.0] * 8), 7),
        (np.array(list(reversed(range(8)))), 0),
    )
)
def test_counts_eq(array, expected):
    result = np_summary.count_eq(array)
    assert result == expected


@pytest.mark.parametrize(
    'array, expected',
    (
        (np.array([]), 0),
        (np.arange(8.0), 0),
        (np.array([1.0] * 8), 0),
        (np.array(list(reversed(range(8)))), 7),
    )
)
def test_counts_dec(array, expected):
    result = np_summary.count_dec(array)
    assert result == expected


@pytest.mark.parametrize(
    'array, expected',
    (
        (np.array([]), 0),
        (np.arange(8.0), 7),
        (np.array([1.0] * 8), 0),
        (np.array(list(reversed(range(8)))), 0),
    )
)
def test_counts_inc(array, expected):
    result = np_summary.count_inc(array)
    assert result == expected


@pytest.mark.parametrize(
    'array, expected',
    (
        (np.array([]), (0, 0, 0)),
        (np.arange(8.0), (0, 0, 7)),
        (np.array([1.0] * 8), (7, 0, 0)),
        (np.array(list(reversed(range(8)))), (0, 7, 0)),
    )
)
def test_counts_eq_dec_inc(array, expected):
    result = np_summary.count_eq_dec_inc(array)
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
                                    count_eq=1, count_dec=0, count_inc=0, activity=0.0, first=1.0, last=1.0),
        ),
        (
            np.array([1.0, 1.0]),
            2.0,
            np_summary.ArraySummary(len=2, shape=(2,), count=2, min=1.0, max=1.0, mean=1.0, std=0.0, median=1.0,
                                    count_eq=1, count_dec=0, count_inc=0, activity=0.0, first=1.0, last=1.0),
        ),
        (
            np.array([1.0, 1.0]),
            2.0,
            np_summary.ArraySummary(len=2, shape=(2,), count=2, min=1.0, max=1.0, mean=1.0, std=0.0, median=1.0,
                                    count_eq=1, count_dec=0, count_inc=0, activity=0.0, first=1.0, last=1.0),
        ),
        (
            np.array([2.0 ** i for i in range(8)]),
            None,
            np_summary.ArraySummary(len=8, shape=(8,), count=8, min=1.0, max=128.0, mean=31.875, std=41.40784195052913,
                                    median=12.0, count_eq=0, count_dec=0, count_inc=7, activity=1.0,
                                    first=1.0, last=128.0)
        ),
        (
            np.array([2.0 ** i for i in range(8)]),
            4.0,
            np_summary.ArraySummary(len=8, shape=(7,), count=7, min=1.0, max=128.0, mean=35.857142857142854,
                                    std=42.809974042867864, median=16.0, count_eq=0, count_dec=0, count_inc=6,
                                    activity=1.0 + 1 / 6, first=1.0, last=128.0)
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


@pytest.mark.xfail(reason='Need to think about this.')
@pytest.mark.parametrize(
    'array, expected',
    (
        (
            np.array([datetime.date(2020, 9, 28), datetime.date(2020, 9, 29),]),
            np_summary.ArraySummary(len=2, shape=(2,), count=2, min=1.0, max=1.0, mean=1.0, std=0.0, median=1.0,
                                    count_eq=1, count_dec=0, count_inc=0, activity=0.0, first=0.0, last=0.0),
        ),
    )
)
def test_summarise_array_dates_and_times(array, expected):
    # masked_array = array.view(np.ma.MaskedArray)
    # masked_array.mask = (array == None)
    # result = np_summary.summarise_array(masked_array)
    result = np_summary.summarise_array(array)
    assert result == expected


@pytest.mark.parametrize(
    'array_summary, expected',
    (
        (
            np_summary.ArraySummary(len=8, shape=(8,), count=8, min=1.0, max=128.0, mean=31.875, std=41.40784195052913,
                                    median=12.0, count_eq=0, count_dec=0, count_inc=7, activity=1.0,
                                    first=1.0, last=128.0),
            (128.0 - 1.0) / (8 - 1),
        ),
    )
)
def test_summarise_array_drift(array_summary, expected):
    assert array_summary.drift == expected


@pytest.mark.parametrize(
    'array_summary, expected',
    (
        (
            np_summary.ArraySummary(len=8, shape=(8,), count=8, min=1.0, max=128.0, mean=31.875, std=41.40784195052913,
                                    median=12.0, count_eq=0, count_dec=0, count_inc=7, activity=1.0,
                                    first=1.0, last=128.0),
            128.0 - 1.0,
        ),
    )
)
def test_summarise_array_span(array_summary, expected):
    assert array_summary.span == expected


@pytest.mark.parametrize(
    'array_summary, expected',
    (
        (
            np_summary.ArraySummary(len=8, shape=(8,), count=8, min=1.0, max=128.0, mean=31.875, std=41.40784195052913,
                                    median=12.0, count_eq=0, count_dec=0, count_inc=7, activity=1.0,
                                    first=1.0, last=128.0),
            'Length          Shape  Count          Min          Max         Mean     Std.Dev.       Median  Equal   Inc.   Dec.     Activity        Drift        First ->         Last',
        ),
    )
)
def test_summarise_array_str_header(array_summary, expected):
    assert array_summary.str_header() == expected


@pytest.mark.parametrize(
    'array_summary, expected',
    (
        (
            np_summary.ArraySummary(len=8, shape=(8,), count=8, min=1.0, max=128.0, mean=31.875, std=41.40784195052913,
                                    median=12.0, count_eq=0, count_dec=0, count_inc=7, activity=1.0,
                                    first=1.0, last=128.0),
            # 'Length          Shape  Count          Min          Max         Mean     Std.Dev.       Median  Equal   Inc.   Dec.     Activity        Drift        First ->         Last',
            '     8           (8,)      8            1          128       31.875      41.4078           12      0      7      0            1      18.1429            1 ->          128',
        ),
    )
)
def test_summarise_array_str(array_summary, expected):
    # print()
    # print(array_summary.str())
    assert array_summary.str() == expected
