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
        ((None, None, None), 7, range(0, 7, 1)),
        ((None, 7, None), 7, range(0, 7, 1)),
        ((None, 7, None), 42, range(0, 7, 1)),
        ((None, None, None), 1, range(0, 1, 1)),
        ((None, -1, None), 1, range(0, 0, 1)),
        ((None, 8, 2), 8, range(0, 8, 2)),
        ((2, 8, 2), 8, range(2, 8, 2)),
        ((None, None, 64), 921, range(0, 921, 64)),
    )
)
def test_slice_range(init, length, expected):
    s = Slice.Slice(*init)
    assert s.range(length) == expected


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
    'init, error_message',
    (
        (0, "fraction must be an integer >= 1 not 0"),
    )
)
def test_split_ctor_raises(init, error_message):
    with pytest.raises(ValueError) as err:
        Slice.Split(init)
    assert err.value.args[0] == error_message



@pytest.mark.parametrize(
    'init, length, expected',
    (
        (1, 7, 1),
        (2, 7, 2),
        (8, 7, 7),
        (64, 52, 52),
        (64, 699, 64),
        (64, 11211, 64),
    )
)
def test_split_count(init, length, expected):
    s = Slice.Split(init)
    assert s.count(length) == expected


@pytest.mark.parametrize(
    'init, length, expected',
    (
        (1, 7, range(0, 7, 7)),
        (7, 7, range(0, 7, 1)),
        (3, 7, range(0, 7, 3)),
        (64, 52, range(0, 52, 1)),
        (64, 699, range(0, 699, 11)),
        (64, 11211, range(0, 11211, 176)),
    )
)
def test_split_range(init, length, expected):
    s = Slice.Split(init)
    assert s.range(length) == expected


@pytest.mark.parametrize(
    'init, length, expected',
    (
        (4, 2, [(0, 0), (1, 1)]),
    )
)
def test_split_range_enumerate(init, length, expected):
    s = Slice.Split(init)
    result = list(enumerate(s.range(length)))
    assert result == expected


@pytest.mark.parametrize(
    'init, length, expected',
    (
        (1, 7, list(range(0, 7, 7))),
        (7, 7, list(range(0, 7, 1))),
        (3, 7, list(range(0, 7, 3))),
    )
)
def test_split_indices(init, length, expected):
    s = Slice.Split(init)
    assert s.indices(length) == expected


@pytest.mark.parametrize(
    'init, expected',
    (
        # Slice
        (',,', Slice.Slice()),
        ('None,None,None', Slice.Slice()),
        ('None,None,None  ', Slice.Slice()),
        ('  None,None,None', Slice.Slice()),
        ('None , None , None', Slice.Slice()),
        ('None,1,None', Slice.Slice(stop=1)),
        ('1,10,None', Slice.Slice(1, 10)),
        ('1,10,2', Slice.Slice(1, 10, 2)),
        # Split
        ('1/1', Slice.Split(1)),
        ('1/64', Slice.Split(64)),
    )
)
def test_create_slice_or_split(init, expected):
    s = Slice.create_slice_or_split(init)
    assert s == expected


@pytest.mark.parametrize(
    'init, expected',
    (
        # Slice
        (',,,', 'Too many parts in ",,,"'),
        ('Z,,,', "invalid literal for int() with base 10: 'Z'"),
        # Split
        ('1/0', 'A Split must end with and integer >= 1 not 0 in "1/0"'),
        ('1/A', "invalid literal for int() with base 10: 'A'"),
        ('4/4', 'A Split must start with 1 not 4 in "4/4"'),
        ('1/4/8', 'Wrong number of parts for a Split in "1/4/8"'),
    )
)
def test_create_slice_or_split_raises(init, expected):
    with pytest.raises(ValueError) as err:
        Slice.create_slice_or_split(init)
    assert err.value.args[0] == expected
