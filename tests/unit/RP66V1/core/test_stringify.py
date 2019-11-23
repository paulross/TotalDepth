import pytest

from TotalDepth.RP66V1.core import stringify


@pytest.mark.parametrize(
    'obj, expected',
    (
        (None, '-',),
        (b'123', '123',),
        (b'\xb0', '°',),
        (1, '1',),
        ([1, 2], '[1, 2]',),
        ([1,], '1',),
        ((1, 2), '(1, 2)',),
        ((1,), '1',),
    )
)
def test_stringify_object_by_type(obj, expected):
    assert stringify.stringify_object_by_type(obj) == expected
