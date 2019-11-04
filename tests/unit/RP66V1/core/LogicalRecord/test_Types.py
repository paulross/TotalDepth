import pytest

from TotalDepth.RP66V1.core.LogicalRecord import Types


@pytest.mark.parametrize(
    'code, expected',
    (
        (1, True,),
        (127, True,),
        (128, False,),
        (255, False,),
    )
)
def test_is_public(code, expected):
    assert Types.is_public(code) == expected
    assert Types.is_private(code) is not expected
