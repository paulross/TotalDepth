import pytest

from TotalDepth.common import LogPass


def test_log_pass_channel_ctor():
    LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', (1,), LogPass.DEFAULT_NP_TYPE)


def test_log_pass_channel_ctor_str():
    fc = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', (1,), LogPass.DEFAULT_NP_TYPE)
    print(str(fc))
    assert str(fc) == '<FrameChannel: \'GR  \' "Gamma Ray" units: \'GAPI\' count: 1 dimensions: (1,) frames: 0>'


def test_log_pass_channel_init_array():
    fc = LogPass.FrameChannel('GR  ', 'Gamma Ray', 'GAPI', (1,), LogPass.DEFAULT_NP_TYPE)
    fc.init_array(8)
    assert len(fc) == 8


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



