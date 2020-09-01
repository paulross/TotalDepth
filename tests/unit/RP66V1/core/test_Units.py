
import pytest

from TotalDepth.RP66V1.core import Units


# Units conversion currently hits the network
@pytest.mark.slow
@pytest.mark.parametrize(
    'value, unit_from, unit_to, producer_code, expected',
    (
        (1.0, b'FEET', b'M', 0, 0.3048),
        (0.3048, b'M', b'FEET', 0, 1.0),
        (1000.0, b'ltrs', b'M3', 280, 1.0),
        (1.0, b'M3', b'ltrs', 280, 1000.0),
    ),
)
def test_convert(value, unit_from, unit_to, producer_code, expected):
    result = Units.convert(value, unit_from, unit_to, producer_code)
    assert result == expected


# Units conversion currently hits the network
@pytest.mark.slow
@pytest.mark.parametrize(
    'value, unit_from, unit_to, producer_code, expected',
    (
        (1.0, b'XXXX', b'M', 0, "Can not lookup units with error: 'XXXX'"),
        (1.0, b'M', b'XXXX', 0, "Can not lookup units with error: 'XXXX'"),
        (1.0, b'FEET', b'M', 99999, "Can not lookup PRODUCER-CODE with error: 99999"),
        (1.0, b'FEET', b'DEGC', 0,
         "Can not convert units with error:"
         " Units Unit(code='FEET', name='foot', standard_form='ft', dimension='Length', scale=0.3048, offset=0.0)"
         " and"
         " Unit(code='DEGC', name='degree celsius', standard_form='degC', dimension='Temperature', scale=1.0, offset=-273.15)"
         " are not the same dimension."
         ),
    ),
)
def test_convert_raises(value, unit_from, unit_to, producer_code, expected):
    with pytest.raises(Units.ExceptionRP66V1Units) as err:
        Units.convert(value, unit_from, unit_to, producer_code)
    assert err.value.args[0] == expected


# Units conversion currently hits the network
@pytest.mark.slow
@pytest.mark.parametrize(
    'value, unit_from, unit_to, producer_code, expected',
    (
        (1.0, b'FEET', b'M', 0, 0.3048),
        (0.3048, b'M', b'FEET', 0, 1.0),
        (1000.0, b'ltrs', b'M3', 280, 1.0),
        (1.0, b'M3', b'ltrs', 280, 1000.0),
    ),
)
def test_convert_function(value, unit_from, unit_to, producer_code, expected):
    result_function = Units.convert_function(unit_from, unit_to, producer_code)
    assert result_function(value) == expected
