import io

import pytest
import numpy as np

from TotalDepth.common import LogPass, Slice


def test_log_pass_channel_ctor():
    LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', (1,), LogPass.DEFAULT_NP_TYPE)


def test_log_pass_channel_ctor_str():
    fc = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', (1,), LogPass.DEFAULT_NP_TYPE)
    # print(str(fc))
    assert str(fc) == '<FrameChannel: \'GR  \' "Gamma Ray" units: \'GAPI\' count: 1 dimensions: (1,) frames: 0>'


def test_log_pass_channel_init_array():
    fc = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', (1,), LogPass.DEFAULT_NP_TYPE)
    fc.init_array(8)
    assert len(fc) == 8


def test_log_pass_channel_init_array_zero_length():
    fc = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', (1,), LogPass.DEFAULT_NP_TYPE)
    fc.init_array(0)
    assert len(fc) == 0


def test_log_pass_channel_init_array_raises():
    fc = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', (1,), LogPass.DEFAULT_NP_TYPE)
    with pytest.raises(LogPass.ExceptionFrameChannel) as err:
        fc.init_array(-8)
    assert err.value.args[0] == 'Number of frames must be >= 0 not -8'


def test_log_pass_channel_set_get_array():
    fc = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', (1,), LogPass.DEFAULT_NP_TYPE)
    fc.init_array(8)
    for i in range(8):
        fc[i] = i
    for i in range(8):
        assert fc[i] == i


@pytest.mark.parametrize(
    'shape, length, expected',
    (
        ((1,), 8, (8, 1)),
        ((5, 16), 4, (4, 5, 16)),
    )
)
def test_log_pass_channel_array_shape(shape, length, expected):
    fc = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape, LogPass.DEFAULT_NP_TYPE)
    fc.init_array(length)
    assert fc.shape == expected


@pytest.mark.parametrize(
    'shape, length, expected',
    (
        ((1,), 8, 8),
        ((5, 16), 4, 5 * 16 * 4),
    )
)
def test_log_pass_channel_array_size(shape, length, expected):
    fc = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape, LogPass.DEFAULT_NP_TYPE)
    fc.init_array(length)
    assert fc.array_size == expected


@pytest.mark.parametrize(
    'shape, length, expected',
    (
        ((1,), 8, 8 * 8),
        ((5, 16), 4, 5 * 16 * 4 * 8),
    )
)
def test_log_pass_channel_sizeof_array(shape, length, expected):
    fc = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape, LogPass.DEFAULT_NP_TYPE)
    fc.init_array(length)
    assert fc.sizeof_array == expected


@pytest.mark.parametrize(
    'shape, length, expected',
    (
        ((1,), 8, 8),
        ((5, 16), 4, 5 * 16 * 8),
    )
)
def test_log_pass_channel_sizeof_frame(shape, length, expected):
    fc = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape, LogPass.DEFAULT_NP_TYPE)
    fc.init_array(length)
    assert fc.sizeof_frame == expected


@pytest.mark.parametrize(
    'shape, frame_number, expected_tuple',
    (
        (
            (1,), 7, ((7, 0,),),
        ),
        (
            (2, 3),
            7,
            ((7, 0, 0), (7, 0, 1), (7, 0, 2), (7, 1, 0), (7, 1, 1), (7, 1, 2)),
        ),
    )
)
def test_log_pass_channel_numpy_indexes(shape, frame_number, expected_tuple):
    fc = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape=shape, np_dtype=LogPass.DEFAULT_NP_TYPE)
    result = tuple(fc.numpy_indexes(frame_number))
    assert result == expected_tuple


def test_log_pass_channel_numpy_indexes_raises():
    fc = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE)
    with  pytest.raises(LogPass.ExceptionFrameChannel) as err:
        fc.numpy_indexes(-1)
    assert err.value.args[0] == 'FrameChannel.numpy_indexes() frame number must be > 0 not -1'


# ==== Frame Array
def test_log_pass_frame_array_ctor_empty():
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    assert len(frame_array) == 0


def test_log_pass_frame_array_append():
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    frame_array.append(LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    assert len(frame_array) == 2


def test_log_pass_frame_array_keys():
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    frame_array.append(LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    assert list(frame_array.keys()) == ['DEPT', 'GR  ']


def test_log_pass_frame_array_str():
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    frame_array.append(LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    print(str(frame_array))
    assert str(frame_array) == """FrameArray: ID: IDENT Test FrameArray
  <FrameChannel: 'DEPT' "Depth" units: 'FEET' count: 1 dimensions: (1,) frames: 0>
  <FrameChannel: 'GR  ' "Gamma Ray" units: 'GAPI' count: 1 dimensions: (1,) frames: 0>"""


def test_log_pass_frame_array_append_raises():
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    with pytest.raises(LogPass.ExceptionFrameArray) as err:
        frame_array.append(LogPass.FrameChannel('DEPT', 'Gamma Ray', 'GAPI', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    assert err.value.args[0] == 'Duplicate channel identity "DEPT"'


def test_log_pass_frame_array_has():
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    frame_array.append(LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    assert frame_array.has('DEPT')
    assert frame_array.has('GR  ')
    assert not frame_array.has('GR')


def test_log_pass_frame_array_getitem():
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    frame_array.append(LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    assert frame_array[0].ident == 'DEPT'
    assert frame_array['DEPT'].ident == 'DEPT'


def test_log_pass_frame_array_getitem_fails():
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    frame_array.append(LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    with pytest.raises(IndexError) as err:
        ch = frame_array[2]
    assert err.value.args[0] == 'list index out of range'
    with pytest.raises(TypeError) as err:
        ch = frame_array[b'DEPT']
    assert err.value.args[0] == 'list indices must be integers or slices, not bytes'


@pytest.mark.parametrize(
    'shape, length, expected',
    (
        ((1,), 8, [(8, 1,), (8, 1)]),
        ((5, 16), 4, [(4, 1,), (4, 5, 16)]),
    )
)
def test_log_pass_frame_array_init_arrays_shape(shape, length, expected):
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    channel = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape, LogPass.DEFAULT_NP_TYPE)
    frame_array.append(channel)
    frame_array.init_arrays(length)
    assert frame_array.shape == expected


def test_log_pass_frame_array_init_arrays_fails():
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    channel = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', (1,), np_dtype=LogPass.DEFAULT_NP_TYPE)
    frame_array.append(channel)
    with pytest.raises(LogPass.ExceptionFrameArray) as err:
        frame_array.init_arrays(-1)
    assert err.value.args[0] == 'Number of frames must be > 0 not -1'


@pytest.mark.parametrize(
    'length, channels, expected',
    (
        (
            8,
            set(),
            [(8, 1), (0, 1), (0, 4), (0, 5, 16)]
        ),
        (
            8,
            {'GR  '},
            [(8, 1), (8, 1), (0, 4), (0, 5, 16)]
        ),
        (
            4,
            {'GR  '},
            [(4, 1), (4, 1), (0, 4), (0, 5, 16)]
        ),
        (
            4,
            set(),
            [(4, 1), (0, 1), (0, 4), (0, 5, 16)]
        ),
        (
            4,
            {'MSFL', 'HDT '},
            [(4, 1), (0, 1), (4, 4), (4, 5, 16)]
        ),
    )
)
def test_log_pass_frame_array_init_arrays_partial_shape(length, channels, expected):
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    frame_array.append(LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', (1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    frame_array.append(LogPass.FrameChannel('MSFL', 'Micro-spherical', 'OHMM', shape=(4,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    frame_array.append(LogPass.FrameChannel('HDT ', 'High resolution Dipmeter', '    ', shape=(5, 16,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    frame_array.init_arrays_partial(length, channels)
    assert frame_array.shape == expected



def test_log_pass_frame_array_init_arrays_partial_fails():
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    frame_array.append(LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', (1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    with pytest.raises(LogPass.ExceptionFrameArray) as err:
        frame_array.init_arrays_partial(-1, set())
    assert err.value.args[0] == 'Number of frames must be > 0 not -1'


@pytest.mark.parametrize(
    'shape, expected',
    (
        ((1,), 2 * 8),
        ((5, 16), 8 + (5 * 16 * 8)),
    )
)
def test_log_pass_frame_array_sizeof_frame(shape, expected):
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    channel = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape, LogPass.DEFAULT_NP_TYPE)
    frame_array.append(channel)
    assert frame_array.sizeof_frame == expected


@pytest.mark.parametrize(
    'shape, frames, expected',
    (
        ((1,), 1, 2 * 8),
        ((5, 16), 12, (8 + (5 * 16 * 8)) * 12),
    )
)
def test_log_pass_frame_array_sizeof_array(shape, frames, expected):
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    channel = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape, LogPass.DEFAULT_NP_TYPE)
    frame_array.append(channel)
    frame_array.init_arrays(frames)
    assert frame_array.sizeof_array == expected



def test_log_pass_frame_array_x_axis():
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    frame_array.append(LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    assert frame_array.x_axis.ident == 'DEPT'


def test_log_pass_frame_array_x_axis_raises():
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    with pytest.raises(LogPass.ExceptionFrameArray) as err:
        x = frame_array.x_axis
    assert err.value.args[0] == 'Zero channels. Expected one channel as the X axis.'


def test_log_pass_log_pass_ctor():
    log_pass = LogPass.LogPass()
    assert log_pass is not None


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


def test_log_pass_log_pass_single_frame_array():
    log_pass = _create_log_pass_single_frame_array(8)
    assert str(log_pass) == """LogPass:
  FrameArray: ID: IDENT Test FrameArray
    <FrameChannel: 'DEPT' "Depth" units: 'FEET' count: 1 dimensions: (1,) frames: 8>
    <FrameChannel: 'GR  ' "Gamma Ray" units: 'GAPI' count: 1 dimensions: (1,) frames: 8>"""


def test_log_pass_log_pass_single_frame_array_has():
    log_pass = _create_log_pass_single_frame_array(8)
    assert log_pass.has('IDENT')
    assert not log_pass.has('X')


def test_log_pass_log_pass_single_frame_array_keys():
    log_pass = _create_log_pass_single_frame_array(8)
    assert list(log_pass.keys()) == ['IDENT']


def test_log_pass_log_pass_append_raises():
    log_pass = LogPass.LogPass()
    log_pass.append(LogPass.FrameArray(ident='IDENT', description='Test FrameArray'))
    with pytest.raises(LogPass.ExceptionLogPass) as err:
        log_pass.append(LogPass.FrameArray(ident='IDENT', description='Test FrameArray'))
    assert err.value.args[0] == 'Duplicate FrameArray identity "IDENT"'


def test_log_pass_log_pass_single_frame_array_len():
    log_pass = _create_log_pass_single_frame_array(8)
    assert len(log_pass) == 1


def test_log_pass_log_pass_single_frame_array_getitem_int():
    log_pass = _create_log_pass_single_frame_array(8)
    assert log_pass[0] is not None
    assert log_pass[-1] is not None


def test_log_pass_log_pass_single_frame_array_getitem_str():
    log_pass = _create_log_pass_single_frame_array(8)
    assert log_pass['IDENT'] is not None


def test_log_pass_log_pass_single_frame_array_getitem_int_raises():
    log_pass = _create_log_pass_single_frame_array(8)
    with pytest.raises(IndexError) as err:
        _frame_array = log_pass[1]
    assert err.value.args[0] == 'list index out of range'
    with pytest.raises(IndexError) as err:
        _frame_array = log_pass[-2]
    assert err.value.args[0] == 'list index out of range'


def test_log_pass_log_pass_single_frame_array_getitem_str_raises():
    log_pass = _create_log_pass_single_frame_array(8)
    with pytest.raises(KeyError) as err:
        _frame_array = log_pass['X']
    assert err.value.args == ('X',)


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
    result = LogPass.array_reduce(array, method)
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
        _result = LogPass.array_reduce(array, method)
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
    result = LogPass._stringify(value)
    assert result == expected


@pytest.mark.parametrize(
    'value, expected',
    (
        (b'\xff', 'ascii'),
    )
)
def test_log_pass__stringify_raises(value, expected):
    with pytest.raises(ValueError) as err:
        _result = LogPass._stringify(value)
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
        LogPass._check_float_decimal_places_format(value)
    assert err.value.args[0] == expected_error


def test_las_write():
    frame_array = _create_log_pass_single_frame_array(4)
    out_stream = io.StringIO()
    LogPass.write_curve_and_array_section_to_las(
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
DEPT.FEET   : Depth Dimensions: (1,)    
GR  .GAPI   : Gamma Ray Dimensions: (1,)
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
    LogPass.write_curve_and_array_section_to_las(
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
DEPT.FEET   : Depth Dimensions: (1,)    
GR  .GAPI   : Gamma Ray Dimensions: (1,)
# Array processing information:
# Frame Array: ID: IDENT description: Test FrameArray
# Original channels in Frame Array [   2]: DEPT,GR  
# Requested Channels this LAS file [   1]: GR  
# Where a channel has multiple values the reduction method is by "first" value.
# Maximum number of original frames: 4
# Requested frame slicing: <Slice on length=4 start=0 stop=4 step=1>, total number of frames presented here: 4
~A          DEPT             GR  
             4.0              0.0
             3.0              1.0
             2.0              2.0
             1.0              3.0
"""
    print(out_stream.getvalue())
    assert out_stream.getvalue() == expected


def test_las_write_partial_int64():
    frame_array = _create_log_pass_single_frame_array_integer(4)
    out_stream = io.StringIO()
    LogPass.write_curve_and_array_section_to_las(
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
DEPT.FEET   : Depth Dimensions: (1,)    
GR  .GAPI   : Gamma Ray Dimensions: (1,)
# Array processing information:
# Frame Array: ID: IDENT description: Test FrameArray
# Original channels in Frame Array [   2]: DEPT,GR  
# Requested Channels this LAS file [   1]: GR  
# Where a channel has multiple values the reduction method is by "first" value.
# Maximum number of original frames: 4
# Requested frame slicing: <Slice on length=4 start=0 stop=4 step=1>, total number of frames presented here: 4
~A          DEPT             GR  
             4.0                0
             3.0                1
             2.0                2
             1.0                3
"""
    # print(out_stream.getvalue())
    assert out_stream.getvalue() == expected
