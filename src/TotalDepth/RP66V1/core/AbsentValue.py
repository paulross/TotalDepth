"""
Absent Value - a value that represents a missing value.

Unlike LIS79 which specifies an absent value in the DFSR, RP66V1 has no means of explicitly specifying an absent value.
Observation of real-world files shows the -999.25 is used for floats and -999 for integer representation codes.
"""
import typing

import numpy as np

from TotalDepth.RP66V1.core import RepCode

#: Absent value as a float.
ABSENT_VALUE_FLOAT: float = -999.25
#: Absent value as an integer.
ABSENT_VALUE_INT: int = -999


def absent_value_from_rep_code(rep_code: int) -> typing.Union[float, int, None]:
    """Returns the absent value depending on the Representation Code."""
    category = RepCode.REP_CODE_CATEGORY_MAP[rep_code]
    if category == RepCode.NumericCategory.INTEGER:
        return ABSENT_VALUE_INT
    elif category == RepCode.NumericCategory.FLOAT:
        return ABSENT_VALUE_FLOAT


def absent_value_from_array(array: np.ndarray) -> typing.Union[float, int, None]:
    """Returns the absent value depending on the dtype."""
    if np.issubdtype(array.dtype, np.integer):
        return ABSENT_VALUE_INT
    elif np.issubdtype(array.dtype, np.floating):
        return ABSENT_VALUE_FLOAT


def mask_absent_values(array: np.ndarray) -> np.ndarray:
    """Return a view on an array with the absent values masked out."""
    # data pointer: array.__array_interface__['data'][0]
    # New array
    # marr = np.ma.masked_equal(arr, 3)
    # View on original array:
    # marr2 = arr.view(np.ma.MaskedArray)
    # marr2.mask = arr == 3
    ret = array.view(np.ma.MaskedArray)
    ret.mask = array == absent_value_from_array(array)
    # Check that we have not created a new array but a view on the original one.
    assert ret.__array_interface__['data'][0] == array.__array_interface__['data'][0]
    return ret


def count_of_absent_values(array: np.ndarray) -> int:
    """Returns the count of the absent values."""
    ret = 0
    if np.issubdtype(array.dtype, np.integer):
        ret = np.count_nonzero(array == ABSENT_VALUE_INT)
    elif np.issubdtype(array.dtype, np.floating):
        ret = np.count_nonzero(array == ABSENT_VALUE_FLOAT)
    return ret
