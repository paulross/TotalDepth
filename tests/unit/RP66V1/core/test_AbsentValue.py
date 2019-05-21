import numpy as np
import pytest

from TotalDepth.RP66V1.core import AbsentValue, RepCode


@pytest.mark.parametrize(
    'rep_code, expected',
    (
        (2, -999.25),
        (7, -999.25),
        (12, -999),
        (13, -999),
        (14, -999),
        (15, -999),
        (16, -999),
        (17, -999),
        (18, -999),
        (19, None),
        (20, None),
        (21, None),
        (22, None),
        (23, None),
        (24, None),
        (26, None),
        (27, None),
    )
)
def test_absent_value_from_rep_code(rep_code, expected):
    assert AbsentValue.absent_value_from_rep_code(rep_code) == expected


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


@pytest.mark.parametrize(
    'array, expected_sum',
    (
        (np.arange(4.0), 6.0),
        (np.arange(4), 6),
        (np.array([-999.25, -999.25, 42.0]), 42.0),
        (np.array([-999.25, -999, 42.0]), 42.0 - 999.0),
        (np.array([-999, -999, 42]), 42),
    )
)
def test_mask_absent_values(array, expected_sum):
    masked_array = AbsentValue.mask_absent_values(array)
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
