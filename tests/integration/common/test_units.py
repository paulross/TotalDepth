import json
import math

import pytest

from TotalDepth.common import units


@pytest.mark.slow
def test_slb_units():
    result = units.slb_units('DEGC')
    assert result == units.Unit(code='DEGC', name='degree celsius', standard_form='degC',
                                dimension='Temperature', scale=1.0, offset=-273.15)


@pytest.mark.slow
def test_slb_units_dupe():
    result = units.slb_units('DEGC')
    assert result == units.Unit(code='DEGC', name='degree celsius', standard_form='degC',
                                dimension='Temperature', scale=1.0, offset=-273.15)


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
def test_slb_unit_standard_form_to_unit_code():
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
