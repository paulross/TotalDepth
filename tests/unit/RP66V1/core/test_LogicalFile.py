

import pytest

from TotalDepth.RP66V1.core import LogicalFile


def test_visible_record_positions_simple():
    vrp = LogicalFile.VisibleRecordPositions()
    vrp.append(50)
    vrp.append(100)
    # print(vrp)
    assert vrp == [50, 100]


@pytest.mark.parametrize(
    'data, lrsh_position, expected',
    (
        ([0], 1, 0),
        ([0], 7, 0),
    )
)
def test_visible_record_positions_prior(data, lrsh_position, expected):
    vrp = LogicalFile.VisibleRecordPositions(data)
    assert vrp.visible_record_prior(lrsh_position) == expected


@pytest.mark.parametrize(
    'data, lrsh_position, expected',
    (
        ([], 0, 'No Visible Record positions for LRSH position 0.'),
        ([0], 0, 'Can not find Visible Record position prior to 0, earliest is 0.'),
    )
)
def test_visible_record_positions_prior_raises(data, lrsh_position, expected):
    vrp = LogicalFile.VisibleRecordPositions(data)
    with pytest.raises(ValueError) as err:
        vrp.visible_record_prior(lrsh_position)
    assert err.value.args[0] == expected


