import pytest

from TotalDepth.RP66V1.core import AbsentValue


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
