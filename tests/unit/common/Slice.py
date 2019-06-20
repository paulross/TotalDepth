import pytest

from TotalDepth.common import Slice


@pytest.mark.parametrize(
    'init, error_message',
    (
        (('', None, None), "start must be None or an integer not <class 'str'>"),
        ((1.0, None,  None), "start must be None or an integer not <class 'float'>"),
        ((None, '', None), "stop must be None or an integer not <class 'str'>"),
        ((None, 1.0,  None), "stop must be None or an integer not <class 'float'>"),
        ((None, None, ''), "step must be None or an integer not <class 'str'>"),
        ((None, None, 1.0), "step must be None or an integer not <class 'float'>"),
    )
)
def test_slice_ctor_raises(init, error_message):
    with pytest.raises(TypeError) as err:
        Slice.Slice(*init)
    assert err.value.args[0] == error_message


@pytest.mark.parametrize(
    'init, length, expected',
    (
        ((None, None, None), 7, 7),
        ((None, 7, None), 7, 7),
        ((None, 7, None), 42, 7),
        ((None, None, None), 1, 1),
        ((None, -1, None), 1, 0),
        ((None, 8, 2), 8, 4),
        ((2, 8, 2), 8, 3),
        ((None, None, 64), 921, 14),
    )
)
def test_slice_count(init, length, expected):
    s = Slice.Slice(*init)
    assert s.count(length) == expected


@pytest.mark.parametrize(
    'init, length, expected',
    (
        ((None, None, None), 7, list(range(7))),
        ((None, 7, None), 7, list(range(7))),
        ((None, 7, None), 42, list(range(7))),
        ((None, None, None), 1, [0]),
        ((None, -1, None), 1, []),
        ((None, -1, None), 3, [0, 1,]),
        ((None, 8, 2), 8, [0, 2, 4, 6]),
        ((2, 8, 2), 8, [2, 4, 6]),
        ((0, 4, 1), 8, [0, 1, 2, 3,]),
    )
)
def test_slice_indices(init, length, expected):
    s = Slice.Slice(*init)
    assert s.indices(length) == expected


@pytest.mark.parametrize(
    'init, expected',
    (
        (',,', Slice.Slice()),
        ('None,None,None', Slice.Slice()),
        ('None,None,None  ', Slice.Slice()),
        ('  None,None,None', Slice.Slice()),
        ('None , None , None', Slice.Slice()),
        ('None,1,None', Slice.Slice(stop=1)),
        ('1,10,None', Slice.Slice(1, 10)),
        ('1,10,2', Slice.Slice(1, 10, 2)),
    )
)
def test_slice_create_slice(init, expected):
    s = Slice.create_slice(init)
    assert s == expected
