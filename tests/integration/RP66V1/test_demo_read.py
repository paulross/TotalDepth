import contextlib
import os

import pytest

from example_data.RP66V1 import demo_read


@contextlib.contextmanager
def change_cwd(path: str):
    """Change the current working directory to the given path and back again."""
    old_dir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(old_dir)


FUNCTION_LIST = [
    attr for attr in dir(demo_read) if callable(getattr(demo_read, attr)) and attr.startswith('demo_')
]


@pytest.mark.slow
@pytest.mark.parametrize(
    'function',
    FUNCTION_LIST,
)
def test_demo_read_calls(function):
    with change_cwd(os.path.dirname(demo_read.__file__)):
        getattr(demo_read, function)()
