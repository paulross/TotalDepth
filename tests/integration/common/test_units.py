import json
import math

import numpy as np
import pytest

from TotalDepth.common import units


@pytest.mark.slow
def test_slb_units():
    result = units.slb_units('DEGC')
    assert result == units.Unit(code='DEGC', name='degree celsius', standard_form='degC',
                                dimension='Temperature', scale=1.0, offset=-273.15)


@pytest.mark.slow
def test_slb_units_raises():
    with pytest.raises(KeyError) as err:
        units.slb_units('XXXX')
    assert err.value.args[0] == 'XXXX'


@pytest.mark.slow
def test_slb_units_to_json():
    all_units = units._slb_units()
    units_json = json.dumps(all_units, sort_keys=True, indent=4)
    print(units_json)
    # assert 0


@pytest.mark.slow
def test_slb_units_write_to_json():
    all_units = units._slb_units()
    units_json = json.dumps(all_units, sort_keys=True, indent=4)
    with open(units.osdd_data_file_path(), 'w') as file:
        file.write(units_json)


@pytest.mark.slow
def test_slb_units_cache():
    # Poke the cache twice then check
    units.slb_units('DEGC')
    units.slb_units('DEGC')
    # Typ.  CacheInfo(hits=4, misses=1, maxsize=1, currsize=1)
    cache_info = units._slb_units.cache_info()
    assert cache_info.hits >= 2
    assert cache_info.misses == 1
    assert cache_info.maxsize == 1
    assert cache_info.currsize == 1


@pytest.mark.slow
def test_slb_unit_standard_form_to_unit_code_degc():
    # TODO: Move this to code that specifically handles units rather than lookups.
    result = units.slb_standard_form_to_unit_code('degC')
    assert result == [
        units.Unit(code='DEGC', name='degree celsius', standard_form='degC', dimension='Temperature',
                   scale=1.0, offset=-273.15),
        units.Unit(code='deg C', name='degree celsius', standard_form='degC', dimension='Temperature',
                   scale=1.0, offset=-273.15),
        units.Unit(code='oC', name='GeoFrame legacy unit', standard_form='degC', dimension='Temperature',
                   scale=1.0, offset=-273.15)
    ]


@pytest.mark.slow
def test_slb_unit_standard_form_to_unit_code_m():
    result = units.slb_standard_form_to_unit_code('m')
    assert result == [
        units.Unit(code='METERS', name='meter', standard_form='m', dimension='Length', scale=1.0, offset=0.0),
        units.Unit(code='METER', name='meter', standard_form='m', dimension='Length', scale=1.0, offset=0.0),
        units.Unit(code='METRES', name='meter', standard_form='m', dimension='Length', scale=1.0, offset=0.0),
        units.Unit(code='METRE', name='meter', standard_form='m', dimension='Length', scale=1.0, offset=0.0),
        units.Unit(code='G_LN', name='meter', standard_form='m', dimension='Length', scale=1.0, offset=0.0),
        units.Unit(code='S_LN', name='meter', standard_form='m', dimension='Length', scale=1.0, offset=0.0),
        units.Unit(code='M.', name='meter', standard_form='m', dimension='Length', scale=1.0, offset=0.0),
        units.Unit(code='MT', name='meter', standard_form='m', dimension='Length', scale=1.0, offset=0.0),
        units.Unit(code='M', name='meter', standard_form='m', dimension='Length', scale=1.0, offset=0.0),
        units.Unit(code='m', name='meter', standard_form='m', dimension='Length', scale=1.0, offset=0.0)
    ]


@pytest.mark.slow
def test_slb_unit_standard_form_to_unit_code_fails():
    # TODO: Move this to code that specifically handles units rather than lookups.
    with pytest.raises(units.ExceptionUnitsLookup) as err:
        units.slb_standard_form_to_unit_code('XXX')
    assert err.value.args[0] == 'No record of unit corresponding to standard form XXX'


@pytest.mark.slow
@pytest.mark.parametrize(
    'standard_form, expected',
    (
        ('degC', True),
        ('XXX', False),
    )
)
def test_has_slb_standard_form(standard_form, expected):
    result = units.has_slb_standard_form(standard_form)
    assert result == expected


@pytest.mark.slow
@pytest.mark.parametrize(
    'value, unit_from_code, unit_to_code, expected',
    (
        (1, 'FEET', 'METRE', 0.3048),
        (0.3048, 'METRE', 'FEET', 1.0),
        (0.0, 'DEGC', 'DEGF', 32.0),
        (32.0, 'DEGF', 'DEGC', 0.0),
    )
)
def test_convert(value, unit_from_code, unit_to_code, expected):
    unit_from = units.slb_units(unit_from_code)
    unit_to = units.slb_units(unit_to_code)
    result = units.convert(value, unit_from, unit_to)
    assert math.isclose(result, expected, abs_tol=1e-9)


@pytest.mark.slow
@pytest.mark.parametrize(
    'value, unit_from_code, unit_to_code, expected',
    (
        (1, 'FEET', 'METRE', 0.3048),
        (0.3048, 'METRE', 'FEET', 1.0),
        (0.0, 'DEGC', 'DEGF', 32.0),
        (100.0, 'DEGC', 'DEGF', 212.0),
        (32.0, 'DEGF', 'DEGC', 0.0),
    )
)
def test_convert_function(value, unit_from_code, unit_to_code, expected):
    unit_from = units.slb_units(unit_from_code)
    unit_to = units.slb_units(unit_to_code)
    convert_function = units.convert_function(unit_from, unit_to)
    result = convert_function(value)
    assert math.isclose(result, expected, abs_tol=1e-9)


@pytest.mark.slow
def test_slb_load_units():
    units.slb_load_units()


@pytest.mark.slow
def test_has_slb_units():
    assert units.has_slb_units('DEGC')


@pytest.mark.slow
def test_convert_function_fails():
    unit_from = units.slb_units('FEET')
    unit_to = units.slb_units('DEGC')
    with pytest.raises(units.ExceptionUnitsDimension) as err:
        units.convert_function(unit_from, unit_to)
    assert err.value.args[0] == (
        "Units"
        " Unit(code='FEET', name='foot', standard_form='ft', dimension='Length', scale=0.3048, offset=0.0)"
        " and"
        " Unit(code='DEGC', name='degree celsius', standard_form='degC', dimension='Temperature', scale=1.0, offset=-273.15)"
        " are not the same dimension."
    )


@pytest.mark.slow
def test_convert_array():
    unit_from = units.slb_units('DEGC')
    unit_to = units.slb_units('DEGF')
    array = np.array([0.0, 100.0])
    result = units.convert_array(array, unit_from, unit_to)
    for a, b in zip(result, [32.0, 212.0]):
        assert math.isclose(a, b, abs_tol=1e-9)
