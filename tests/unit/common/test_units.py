from bs4 import BeautifulSoup
import pytest

import TotalDepth.common.units


@pytest.mark.parametrize(
    'args, expected',
    (
        (
            ('DEGC', 'degree celsius', 'degC', 'Temperature', 1, -273.15), False,
        ),
        (
            ('DEGK', 'degree kelvin', 'degK', 'Temperature', 1, 0), True,
        ),
    )
)
def test_unit_is_primary(args, expected):
    unit = TotalDepth.common.units.Unit(*args)
    assert unit.is_primary == expected


@pytest.mark.parametrize(
    'args, expected',
    (
        (
            ('DEGC', 'degree celsius', 'degC', 'Temperature', 1, -273.15), True,
        ),
        (
            ('DEGK', 'degree kelvin', 'degK', 'Temperature', 1, 0), False,
        ),
    )
)
def test_unit_has_offset(args, expected):
    unit = TotalDepth.common.units.Unit(*args)
    assert unit.has_offset() == expected


def test__slb_units_from_parse_tree():
    table_text = """<table cellspacing="0" cellpadding="4" id="main_GridView1" style="font-size:X-Small;border-collapse:collapse;">
    <tr align="left" style="background-color:#E0E0E0;">
        <th scope="col">Code</th>
        <th scope="col">Name</th>
        <th scope="col">Standard Form</th>
        <th scope="col">Dimension</th>
        <th scope="col">Scale</th>
        <th scope="col">Offset</th>
    </tr>
    <tr>
        <td>(MSCF/d)/ft/psi</td>
        <td>GeoFrame legacy unit</td>
        <td>1000 ft3/(d.ft.psi)</td>
        <td>Mobility</td>
        <td>1.55954244790036E-07</td>
        <td>0</td>
    </tr>
    <tr>
        <td>(MSCF/d)/psi</td>
        <td>GeoFrame legacy unit</td>
        <td>1000 ft3/(d.psi)</td>
        <td>FlowratePerPressure</td>
        <td>4.75348538120031E-08</td>
        <td>0</td>
    </tr>
    <tr>
        <td>(STB/d)/ft/psi</td>
        <td>GeoFrame legacy unit</td>
        <td>bbl/(d.ft.psi)</td>
        <td>Mobility</td>
        <td>8.75618153524512E-10</td>
        <td>0</td>
    </tr>
</table>
"""
    table = BeautifulSoup(table_text, features='lxml')
    result = TotalDepth.common.units._slb_units_from_parse_tree(table)
    expected = {'(MSCF/d)/ft/psi': TotalDepth.common.units.Unit(code='(MSCF/d)/ft/psi', name='GeoFrame legacy unit',
                                                                standard_form='1000 ft3/(d.ft.psi)', dimension='Mobility',
                                                                scale=1.55954244790036e-07, offset=0.0),
                '(MSCF/d)/psi': TotalDepth.common.units.Unit(code='(MSCF/d)/psi', name='GeoFrame legacy unit',
                                                             standard_form='1000 ft3/(d.psi)', dimension='FlowratePerPressure',
                                                             scale=4.75348538120031e-08, offset=0.0),
                '(STB/d)/ft/psi': TotalDepth.common.units.Unit(code='(STB/d)/ft/psi', name='GeoFrame legacy unit',
                                                               standard_form='bbl/(d.ft.psi)', dimension='Mobility',
                                                               scale=8.75618153524512e-10, offset=0.0)}
    assert result == expected


def test_read_osdd_static_data():
    result = TotalDepth.common.units.read_osdd_static_data()
    assert len(result) > 0
