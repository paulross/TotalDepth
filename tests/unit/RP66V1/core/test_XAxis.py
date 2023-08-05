import numpy as np
import pytest

import TotalDepth.common
from TotalDepth.RP66V1.core import XAxis


def test_XAxis_ctor():
    xaxis = XAxis.XAxis(ident=b'A', long_name=b'B', units=b'C')
    assert xaxis.ident == b'A'
    assert xaxis.long_name == b'B'
    assert xaxis.units == b'C'


@pytest.mark.parametrize(
    'position_xvalues, exp_summary',
    (
        (
            [
                (0x0, 0xff, 1.0),
            ],
            TotalDepth.common.XAxis.XAxisSummary(min=1.0, max=1.0, count=1, spacing=None),
        ),
        (
            [
                (0x0, 0xff, 1.0),
                (0x1ff, 0x2ff, 2.0),
            ],
            TotalDepth.common.XAxis.XAxisSummary(min=1.0, max=2.0, count=2,
                               spacing=TotalDepth.common.XAxis.XAxisSpacingSummary(min=1.0, max=1.0, mean=1.0, median=1.0,
                                                                 std=0.0,
                                                                 counts=TotalDepth.common.XAxis.XAxisSpacingCounts(norm=1, dupe=0,
                                                                                                 skip=0,
                                                                                                 back=0),
                                                                 histogram=(np.array([1]), np.array([0.5, 1.5]))))
            ,
        ),
    )
)
def test_XAxis_append_summary(position_xvalues, exp_summary):
    xaxis = XAxis.XAxis(ident=b'A', long_name=b'B', units=b'C')
    x_values = []
    for frame_number, (vr_postion, lrsh_position, x_value) in enumerate(position_xvalues):
        xaxis.append(
            None, #File.LogicalRecordPosition(vr_postion, lrsh_position),
            frame_number + 1,
            x_value
        )
        x_values.append(x_value)
    result = xaxis.summary
    # print(result)
    assert result.count == len(x_values)
    assert result.min == min(x_values)
    assert result.max == max(x_values)
    array = np.array(x_values)
    spacing_summary = TotalDepth.common.XAxis.compute_spacing(array)
    assert result.spacing == spacing_summary


@pytest.mark.parametrize(
    'position_xvalues, expected',
    (
        (
            [
                (0x0, 0xff, 1.0),
            ],
            [
                XAxis.IFLRReference(logical_record_position=None, #File.LogicalRecordPosition(0x0, 0xff),
                                    frame_number=1, x_axis=1.0),
            ],
        ),
        (
            [
                (0x0, 0xff, 1.0),
                (0x2, 0x2ff, 2.0),
            ],
            [
                XAxis.IFLRReference(logical_record_position=None, #File.LogicalRecordPosition(0x0, 0xff),
                                    frame_number=1, x_axis=1.0),
                XAxis.IFLRReference(logical_record_position=None, #File.LogicalRecordPosition(0x2, 0x2ff),
                                    frame_number=2, x_axis=2.0),
            ],
        ),
    )
)
def test_XAxis_getitem(position_xvalues, expected):
    x_axis = XAxis.XAxis(ident=b'A', long_name=b'B', units=b'C')
    x_values = []
    for frame_number, (vr_postion, lrsh_position, x_value) in enumerate(position_xvalues):
        x_axis.append(
            None, #File.LogicalRecordPosition(vr_postion, lrsh_position),
            frame_number + 1,
            x_value
        )
        x_values.append(x_value)
    assert len(x_axis) == len(expected)
    # print()
    for i in range(len(x_axis)):
        # print(x_axis[i])
        assert x_axis[i] == expected[i]
