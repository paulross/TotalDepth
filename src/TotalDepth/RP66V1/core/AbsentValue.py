"""
Absent Value - a value that represents a missing value.

Unlike LIS79 which specifies an absent value in the DFSR, RP66V1 has no means of explicitly specifying an absent value.
Observation of real-world files shows the -999.25 is used for floats and -999 for integer representation codes.
"""
import typing

from TotalDepth.RP66V1.core import RepCode

from TotalDepth.common.AbsentValue import ABSENT_VALUE_FLOAT, ABSENT_VALUE_INT


def absent_value_from_rep_code(rep_code: int) -> typing.Union[float, int, None]:
    """Returns the absent value depending on the Representation Code."""
    category = RepCode.REP_CODE_CATEGORY_MAP[rep_code]
    if category == RepCode.NumericCategory.INTEGER:
        return ABSENT_VALUE_INT
    elif category == RepCode.NumericCategory.FLOAT:
        return ABSENT_VALUE_FLOAT
