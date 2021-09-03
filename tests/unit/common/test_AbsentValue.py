import numpy as np

import pytest

from TotalDepth.common import AbsentValue


@pytest.mark.parametrize(
    'array, expected',
    (
        (np.arange(4.0), -999.25),
        (np.arange(4), -999),
        (np.array(['A', 'B']), None),
    )
)
def test_absent_value_from_array(array, expected):
    assert AbsentValue.absent_value_from_array(array) == expected


def test_numpy_mask_behaviour_copy():
    """Checks our understanding of numpy masking behaviour where a copy is made."""
    array = np.array(range(5))
    masked_array = np.ma.masked_equal(array, 3)
    # print(masked_array)
    assert str(masked_array) == '[0 1 2 -- 4]'
    assert array.__array_interface__['data'][0] != masked_array.__array_interface__['data'][0]


def test_numpy_mask_behaviour_view():
    """Checks our understanding of numpy masking behaviour where no copy is made."""
    array = np.array(range(5))
    masked_array = array.view(np.ma.MaskedArray)
    masked_array.mask = array == 3
    # print(masked_array)
    assert str(masked_array) == '[0 1 2 -- 4]'
    assert array.__array_interface__['data'][0] == masked_array.__array_interface__['data'][0]


def test_numpy_unmask_behaviour_view():
    """Checks our understanding of numpy un-masking behaviour where no copy is made."""
    array = np.array(range(5))
    masked_array = array.view(np.ma.MaskedArray)
    masked_array.mask = array == 3
    # print(masked_array)
    assert str(masked_array) == '[0 1 2 -- 4]'
    assert array.__array_interface__['data'][0] == masked_array.__array_interface__['data'][0]
    # Unmask:
    masked_array.mask = [False] * len(masked_array)
    assert str(masked_array) == '[0 1 2 3 4]'
    assert array.__array_interface__['data'][0] == masked_array.__array_interface__['data'][0]


@pytest.mark.parametrize(
    'array, absent_value, expected_sum',
    (
        (np.arange(4.0), None, 6.0),
        (np.arange(4), None, 6),
        (np.array([-999.25, -999.25, 42.0]), None, 42.0),
        (np.array([-999.25, -999, 42.0]), None, 42.0 - 999.0),
        (np.array([-999, -999, 42]), None, 42),
        (np.array([-123.25, -123.25, 42.0]), -123.25, 42.0),
    )
)
def test_mask_absent_values(array, absent_value, expected_sum):
    masked_array = AbsentValue.mask_absent_values(array, absent_value)
    assert masked_array.sum() == expected_sum


@pytest.mark.parametrize(
    'array, expected_sum',
    (
        (np.arange(4.0), 6.0),
        (np.arange(4), 6),
        (np.array([-999.25, -999.25, 42.0]), (2 * -999.25) + 42.0),
        (np.array([-999.25, -999, 42.0]), -999.25 + 42.0 - 999.0),
        (np.array([-999, -999, 42]), 2 * -999 + 42),
    )
)
def test_mask_unmask_absent_values(array, expected_sum):
    masked_array = AbsentValue.mask_absent_values(array)
    AbsentValue.unmask_absent_values(masked_array)
    assert masked_array.sum() == expected_sum


@pytest.mark.parametrize(
    'array, expected',
    (
        (np.arange(4.0), 0),
        (np.arange(4), 0),
        (np.array(['A', 'B']), 0),
        (np.array([-999.25, -999.25, 42.0]), 2),
        (np.array([-999.25, -999, 42.0]), 1),
        (np.array([-999, -999, 42]), 2),
    )
)
def test_count_of_absent_values(array, expected):
    assert AbsentValue.count_of_absent_values(array) == expected
