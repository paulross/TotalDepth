import os

import pytest

from TotalDepth.common import ToHTML


def test_index_html_simple():
    idx = ToHTML.IndexHTML([])
    assert idx is not None


def test_index_html_add_raises_dupe():
    idx = ToHTML.IndexHTML([])
    idx.add('foo/bar')
    with pytest.raises(ValueError) as err:
        idx.add('foo/bar')
    assert err.value.args[0].startswith('Duplicate path ')
    assert err.value.args[0].endswith('foo/bar')


@pytest.mark.parametrize(
    'args, expected',
    (
        (tuple(), 'Got 0 values but expected 1'),
        ((1, 2, 3), 'Got 3 values but expected 1'),
    )
)
def test_index_html_add_raises_args_mismatch(args, expected):
    idx = ToHTML.IndexHTML(['A'])
    with pytest.raises(ValueError) as err:
        idx.add('foo/bar', *args)
    assert err.value.args[0] == expected


@pytest.mark.parametrize(
    'add, expected',
    (
        (
            tuple(), None
        ),
        (
            (
                ('foo', 'f'),
            ),
            os.path.abspath(''),
        ),
        (
            (
                ('foo/bar', 'a'),
            ),
            os.path.abspath('foo'),
        ),
        (
            (
                ('foo/bar', 'a'),
                ('foo/baz', 'b'),
            ),
            os.path.abspath('foo'),
        ),
    )
)
def test_index_html_common_path(add, expected):
    idx = ToHTML.IndexHTML(['A'])
    for path, args in add:
        idx.add(path, *args)
    if expected is None:
        assert idx.common_path is None
    else:
        assert idx.common_path == os.path.abspath(expected)


@pytest.mark.parametrize(
    'class_style, kwargs, expected',
    (
        (
            '',
            {'foo': 'bar'},
            {'foo': 'bar'},
        ),
        (
            'style',
            {'foo': 'bar'},
            {'class': 'style', 'foo': 'bar'},
        ),
        (
            'style',
            {'class': 'bar'},
            {'class': 'bar',},
        ),
    )
)
def test_index_html_attr(class_style, kwargs, expected):
    idx = ToHTML.IndexHTML(['A'])
    result = idx.attr(class_style, **kwargs)
    assert result == expected
