import io

import numpy as np

import pytest

from TotalDepth.LAS.core import WriteLAS
from TotalDepth.common import Slice, LogPass


# ==== Test LAS Writing ====
@pytest.mark.parametrize(
    'array, method, expected',
    (
        (np.array(np.arange(5.0)), 'first', 0.0),
        (np.array(np.arange(5.0)), 'mean', 2.0),
        (np.array(np.arange(5.0)), 'median', 2.0),
        (np.array(np.arange(5.0)), 'min', 0.0),
        (np.array(np.arange(5.0)), 'max', 4.0),
    )
)
def test_log_pass__array_reduce(array, method, expected):
    result = WriteLAS.array_reduce(array, method)
    assert result == expected


@pytest.mark.parametrize(
    'array, method, expected',
    (
            (np.array(np.arange(5.0)), 'FIRST',
             "Array reduction method FIRST is not in ['first', 'max', 'mean', 'median', 'min']"),
    )
)
def test_log_pass__array_reduce_raises(array, method, expected):
    with pytest.raises(ValueError) as err:
        _result = WriteLAS.array_reduce(array, method)
    assert err.value.args[0] == expected


@pytest.mark.parametrize(
    'value, expected',
    (
        ('abc', 'abc'),
        (b'abc', 'abc'),
        (1.0, '1.0'),
    )
)
def test_log_pass__stringify(value, expected):
    result = WriteLAS._stringify(value)
    assert result == expected


@pytest.mark.parametrize(
    'value, expected',
    (
        (b'\xff', 'ascii'),
    )
)
def test_log_pass__stringify_raises(value, expected):
    with pytest.raises(ValueError) as err:
        _result = WriteLAS._stringify(value)
    assert err.value.args[0] == expected


@pytest.mark.parametrize(
    'value, expected_error',
    (
        ('', 'Invalid float fractional format of ""'),
        ('abc', 'Invalid float fractional format of "abc"'),
    )
)
def test__check_float_decimal_places_format_raises(value, expected_error):
    with pytest.raises(ValueError) as err:
        WriteLAS._check_float_decimal_places_format(value)
    assert err.value.args[0] == expected_error


def _create_log_pass_single_frame_array(frame_length: int) -> LogPass.LogPass:
    log_pass = LogPass.LogPass()
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', (1,), LogPass.DEFAULT_NP_TYPE))
    frame_array.append(LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', (1,), LogPass.DEFAULT_NP_TYPE))
    frame_array.init_arrays(frame_length)
    for i in range(frame_length):
        frame_array['DEPT'][i] = frame_length - i
        frame_array['GR  '][i] = i
    log_pass.append(frame_array)
    return log_pass

def _create_log_pass_single_frame_array_integer(frame_length: int) -> LogPass.LogPass:
    log_pass = LogPass.LogPass()
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', (1,), LogPass.DEFAULT_NP_TYPE))
    frame_array.append(LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', (1,), np.int64))
    frame_array.init_arrays(frame_length)
    for i in range(frame_length):
        frame_array['DEPT'][i] = frame_length - i
        frame_array['GR  '][i] = i
    log_pass.append(frame_array)
    return log_pass


def _create_log_pass_single_frame_array_three_channels(frame_length: int) -> LogPass.LogPass:
    log_pass = LogPass.LogPass()
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', (1,), LogPass.DEFAULT_NP_TYPE))
    frame_array.append(LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', (1,), LogPass.DEFAULT_NP_TYPE))
    frame_array.append(LogPass.FrameChannel('MSFL', 'Micro Focused SFL', 'MMOH', (1, 4), LogPass.DEFAULT_NP_TYPE))
    frame_array.init_arrays(frame_length)
    for i in range(frame_length):
        frame_array['DEPT'][i] = frame_length - i
        frame_array['GR  '][i] = i
        for j in range(4):
            frame_array['MSFL'][i, j] = 10 * i

    log_pass.append(frame_array)
    return log_pass


def test_las_write():
    frame_array = _create_log_pass_single_frame_array(4)
    out_stream = io.StringIO()
    WriteLAS.write_curve_and_array_section_to_las(
        frame_array['IDENT'],
        len(frame_array['IDENT'].x_axis),
        'first',
        Slice.Slice(),
        set(),
        16,
        '.3',
        out_stream
    )
    expected = """~Curve Information Section
#MNEM.UNIT  Curve Description          
#---------  -----------------          
DEPT.FEET   : Depth Dimensions (1,)    
GR  .GAPI   : Gamma Ray Dimensions (1,)
# Array processing information:
# Frame Array: ID: IDENT description: Test FrameArray
# All [2] original channels reproduced here.
# Where a channel has multiple values the reduction method is by "first" value.
# Maximum number of original frames: 4
# Requested frame slicing: <Slice on length=4 start=0 stop=4 step=1>, total number of frames presented here: 4
~A          DEPT             GR  
             4.0              0.0
             3.0              1.0
             2.0              2.0
             1.0              3.0
"""
    # print(out_stream.getvalue())
    assert out_stream.getvalue() == expected


def test_las_write_partial():
    frame_array = _create_log_pass_single_frame_array(4)
    out_stream = io.StringIO()
    WriteLAS.write_curve_and_array_section_to_las(
        frame_array['IDENT'],
        len(frame_array['IDENT'].x_axis),
        'first',
        Slice.Slice(),
        {'GR  '},
        16,
        '.3',
        out_stream
    )
    expected = """~Curve Information Section
#MNEM.UNIT  Curve Description          
#---------  -----------------          
DEPT.FEET   : Depth Dimensions (1,)    
GR  .GAPI   : Gamma Ray Dimensions (1,)
# Array processing information:
# Frame Array: ID: IDENT description: Test FrameArray
# Original channels in Frame Array [   2]: DEPT,GR  
# Requested Channels in this LAS file [   1]: GR  
# Where a channel has multiple values the reduction method is by "first" value.
# Maximum number of original frames: 4
# Requested frame slicing: <Slice on length=4 start=0 stop=4 step=1>, total number of frames presented here: 4
~A          DEPT             GR  
             4.0              0.0
             3.0              1.0
             2.0              2.0
             1.0              3.0
"""
    result = out_stream.getvalue()
    # print(result)
    assert result == expected


def test_las_write_partial_int64():
    frame_array = _create_log_pass_single_frame_array_integer(4)
    out_stream = io.StringIO()
    WriteLAS.write_curve_and_array_section_to_las(
        frame_array['IDENT'],
        len(frame_array['IDENT'].x_axis),
        'first',
        Slice.Slice(),
        {'GR  '},
        16,
        '.3',
        out_stream
    )
    expected = """~Curve Information Section
#MNEM.UNIT  Curve Description          
#---------  -----------------          
DEPT.FEET   : Depth Dimensions (1,)    
GR  .GAPI   : Gamma Ray Dimensions (1,)
# Array processing information:
# Frame Array: ID: IDENT description: Test FrameArray
# Original channels in Frame Array [   2]: DEPT,GR  
# Requested Channels in this LAS file [   1]: GR  
# Where a channel has multiple values the reduction method is by "first" value.
# Maximum number of original frames: 4
# Requested frame slicing: <Slice on length=4 start=0 stop=4 step=1>, total number of frames presented here: 4
~A          DEPT             GR  
             4.0                0
             3.0                1
             2.0                2
             1.0                3
"""
    result = out_stream.getvalue()
    # print(result)
    assert result == expected
