import io

import pytest

from TotalDepth.common import colorama


def test_section():
    file = io.StringIO()
    with colorama.section('TITLE', '=', width=40,  out_stream=file):
        file.write('Some text\n')
    result = file.getvalue()
    print(repr(result))
    expected = '\x1b[32m================ TITLE =================\nSome text\n\x1b[32m============== END TITLE ===============\n'
    assert result == expected
