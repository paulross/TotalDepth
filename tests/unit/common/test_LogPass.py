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


def test_log_pass_frame_array_ctor_empty():
    frame_array = LogPass.FrameArray(ident='IDENT', description='Test FrameArray')
    assert len(frame_array) == 0



