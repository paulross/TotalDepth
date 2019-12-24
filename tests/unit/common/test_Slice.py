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
        ((None, None, 64), 921, len(list(range(0, 921, 64)))),
        ((None, None, 64), 3181, len(list(range(0, 3181, 64)))),
        ((None, None, 64), 3012, len(list(range(0, 3012, 64)))),
    )
)
def test_slice_count(init, length, expected):
    s = Slice.Slice(*init)
    assert s.count(length) == expected


@pytest.mark.parametrize(
    'init, length, expected',
    (
        ((None, None, None), 7, 0),
        ((None, 7, None), 7, 0),
        ((None, 7, None), 42, 0),
        ((None, None, None), 1, 0),
        ((None, -1, None), 1, 0),
        ((None, 8, 2), 8, 0),
        ((2, 8, 2), 8, 2),
        ((None, None, 64), 921, 0),
        ((None, None, 64), 3181, 0),
        ((None, None, 64), 3012, 0),
    )
)
def test_slice_first(init, length, expected):
    s = Slice.Slice(*init)
    assert s.first(length) == expected


@pytest.mark.parametrize(
    'init, length, expected',
    (
        ((None, None, None), 7, 6),
        ((None, 7, None), 7, 6),
        ((None, 7, None), 42, 6),
        ((None, None, None), 1, 0),
        ((None, -1, None), 1, -1),
        ((None, 8, 2), 8, 7),
        ((2, 8, 2), 8, 7),
        ((None, None, 64), 921, 895),
        ((None, None, 64), 3181, 3135),
        ((None, None, 64), 3012, 3007),
    )
)
def test_slice_last(init, length, expected):
    s = Slice.Slice(*init)
    assert s.last(length) == expected


@pytest.mark.parametrize(
    'init, length, expected',
    (
        ((None, None, None), 7, 1),
        ((None, 7, None), 7, 1),
        ((None, 7, None), 42, 1),
        ((None, None, None), 1, 1),
        ((None, -1, None), 1, 1),
        ((None, 8, 2), 8, 2),
        ((2, 8, 2), 8, 2),
        ((None, None, 64), 921, 64),
        ((None, None, 64), 3181, 64),
        ((None, None, 64), 3012, 64),
    )
)
def test_slice_step(init, length, expected):
    s = Slice.Slice(*init)
    assert s.step(length) == expected


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
        ((None, None, 64), 3181, range(0, 3181, 64)),
        ((None, None, 64), 3012, range(0, 3012, 64)),
    )
)
def test_slice_range(init, length, expected):
    s = Slice.Slice(*init)
    assert list(s.gen_indices(length)) == list(expected)


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


def test_slice_eq():
    assert Slice.Slice(None, None, None) == Slice.Slice(None, None, None)
    assert Slice.Slice(None, None, None) != 1


@pytest.mark.parametrize(
    'init, expected',
    (
        ((None, None, None), '<Slice.slice(None, None, None)>'),
        ((None, 7, None), '<Slice.slice(None, 7, None)>'),
        ((None, -1, None), '<Slice.slice(None, -1, None)>'),
        ((None, 8, 2), '<Slice.slice(None, 8, 2)>'),
        ((2, 8, 2), '<Slice.slice(2, 8, 2)>'),
        ((0, 4, 1), '<Slice.slice(0, 4, 1)>'),
    )
)
def test_slice_str(init, expected):
    s = Slice.Slice(*init)
    assert str(s) == expected


@pytest.mark.parametrize(
    'init, length, expected',
    (
        ((None, None, None), 7, '<Slice on length=7 start=0 stop=7 step=1>'),
        ((None, 7, None), 7, '<Slice on length=7 start=0 stop=7 step=1>'),
        ((None, 7, None), 42, '<Slice on length=42 start=0 stop=7 step=1>'),
        ((None, None, None), 1, '<Slice on length=1 start=0 stop=1 step=1>'),
        ((None, -1, None), 1, '<Slice on length=1 start=0 stop=0 step=1>'),
        ((None, -1, None), 3, '<Slice on length=3 start=0 stop=2 step=1>'),
        ((None, 8, 2), 8, '<Slice on length=8 start=0 stop=8 step=2>'),
        ((2, 8, 2), 8, '<Slice on length=8 start=2 stop=8 step=2>'),
        ((0, 4, 1), 8, '<Slice on length=8 start=0 stop=4 step=1>'),
    )
)
def test_slice_long_str(init, length, expected):
    s = Slice.Slice(*init)
    result = s.long_str(length)
    assert result == expected


@pytest.mark.parametrize(
    'init, error_message',
    (
        (0, "A Sample must be an integer >= 1 not 0"),
    )
)
def test_sample_ctor_raises(init, error_message):
    with pytest.raises(ValueError) as err:
        Slice.Sample(init)
    assert err.value.args[0] == error_message


@pytest.mark.parametrize(
    'init, length, expected',
    (
        (1, 7, 0),
        (2, 7, 0),
        (8, 7, 0),
        (64, 52, 0),
        (64, 699, 0),
        (64, 11211, 0),
    )
)
def test_sample_first(init, length, expected):
    s = Slice.Sample(init)
    assert s.first(length) == expected


@pytest.mark.parametrize(
    'init, length, expected',
    (
        (1, 7, 6),
        (2, 7, 5),
        (8, 7, 6),
        (64, 52, 51),
        (64, 699, 635),
        (64, 11211, 11147),
    )
)
def test_sample_last(init, length, expected):
    s = Slice.Sample(init)
    assert s.last(length) == expected


@pytest.mark.parametrize(
    'init, length, expected',
    (
        (1, 7, 7),
        (2, 7, 3),
        (8, 7, 1),
        (64, 52, 1),
        (64, 699, 10),
        (64, 11211, 175),
    )
)
def test_sample_step(init, length, expected):
    s = Slice.Sample(init)
    assert s.step(length) == expected


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
def test_sample_count(init, length, expected):
    s = Slice.Sample(init)
    assert s.count(length) == expected


@pytest.mark.parametrize(
    'init, length, expected',
    (
        (1, 7, list(range(0, 7, 7))),
        (7, 7, list(range(0, 7, 1))),
        (3, 7, [0, 2, 4]),
        (64, 52, list(range(0, 52, 1))),
    )
)
def test_sample_range(init, length, expected):
    s = Slice.Sample(init)
    assert list(s.gen_indices(length)) == expected


@pytest.mark.parametrize(
    'init, length, expected',
    (
        (4, 2, [(0, 0), (1, 1)]),
    )
)
def test_sample_range_enumerate(init, length, expected):
    s = Slice.Sample(init)
    result = list(enumerate(s.gen_indices(length)))
    assert result == expected


@pytest.mark.parametrize(
    'init, length, expected',
    (
        (1, 7, list(range(0, 7, 7))),
        (7, 7, list(range(0, 7, 1))),
        (3, 7, [0, 2, 4]),
    )
)
def test_sample_indices(init, length, expected):
    s = Slice.Sample(init)
    assert s.indices(length) == expected


def test_sample_eq():
    assert Slice.Sample(7) == Slice.Sample(7)
    assert Slice.Sample(7) != 1


@pytest.mark.parametrize(
    'init, expected',
    (
        (1, '<Sample fraction: 1>'),
        (7, '<Sample fraction: 7>'),
        (3, '<Sample fraction: 3>'),
    )
)
def test_sample_str(init, expected):
    s = Slice.Sample(init)
    assert str(s) == expected


@pytest.mark.parametrize(
    'init, length, expected',
    (
        (1, 7, '<Sample 1 out of 7>'),
        (3, 7, '<Sample 3 out of 7>'),
        (7, 7, '<Sample 7 out of 7>'),
        (8, 7, '<Sample 7 out of 7>'),
    )
)
def test_sample_long_str(init, length, expected):
    s = Slice.Sample(init)
    assert s.long_str(length) == expected


@pytest.mark.parametrize(
    'init, expected',
    (
        (1, [0]),
        (2, [0, 6]),
        (3, [0, 4, 8]),
        (4, [0, 3, 6, 9]),
        (5, [0, 2, 4, 7, 9]),
        (6, [0, 2, 4, 6, 8, 10]),
        (7, [0, 1, 3, 5, 6, 8, 10]),
        (8, [0, 1, 3, 4, 6, 7, 9, 10]),
        (9, [0, 1, 2, 4, 5, 6, 8, 9, 10]),
        (10, [0, 1, 2, 3, 4, 6, 7, 8, 9, 10]),
        (11, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        (12, list(range(12))),
        (13, list(range(12))),
    )
)
def test_sample_12(init, expected):
    s = Slice.Sample(init)
    result = list(s.gen_indices(12))
    assert len(result) == min(init, 12)
    assert result == expected


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
        # ('', Slice.Slice(None, None, None)),
        # (',', Slice.Slice(None, None, None)),
        # (',1', Slice.Slice(None, 1, None)),
        # ('1,', Slice.Slice(1, None, None)),
        # Sample
        ('1', Slice.Sample(1)),
        ('64', Slice.Sample(64)),
    )
)
def test_create_slice_or_sample(init, expected):
    s = Slice.create_slice_or_sample(init)
    assert s == expected


@pytest.mark.parametrize(
    'init, expected',
    (
        # Slice
        (',,,', 'Wrong number of parts for a Slice in ",,,"'),
        ('Z,,,', "invalid literal for int() with base 10: 'Z'"),
        # Sample
        ('-1', 'A Sample must be an integer >= 1 not -1'),
        ('0', 'A Sample must be an integer >= 1 not 0'),
        ('1/2', "invalid literal for int() with base 10: '1/2'"),
        ('A', "invalid literal for int() with base 10: 'A'"),
    )
)
def test_create_slice_or_sample_raises(init, expected):
    with pytest.raises(ValueError) as err:
        Slice.create_slice_or_sample(init)
    assert err.value.args[0] == expected
