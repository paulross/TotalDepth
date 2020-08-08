import pytest

from TotalDepth.common import LogPass


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
def test_log_pass_frame_array_sizeof_frame(shape, frames, expected):
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    frame_array.append(LogPass.FrameChannel('DEPT', 'Depth', 'FEET', shape=(1,), np_dtype=LogPass.DEFAULT_NP_TYPE))
    channel = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', shape, LogPass.DEFAULT_NP_TYPE)
    frame_array.append(channel)
    frame_array.init_arrays(frames)
    assert frame_array.sizeof_array == expected


