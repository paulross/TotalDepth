from bs4 import BeautifulSoup
import pytest

from TotalDepth.common import lookup_mnemonic


def test__decompose_table_to_key_value():
    table_text = """<table cellspacing="5" cellpadding="1" id="main_DetailsView1" style="width:492px;">
    <tr>
        <td style="font-weight:bold;">Channel</td>
        <td>A0</td>
    </tr>
    <tr>
        <td style="font-weight:bold;">Description</td>
        <td>Analog 0 (Regular)</td>
    </tr>
    <tr>
        <td style="font-weight:bold;">Unit quantity</td>
        <td>
            <a id="main_DetailsView1_HyperLink1" href="UOMDetail.aspx?dim=ElectricPotential">ElectricPotential</a>
        </td>
    </tr>
    <tr>
        <td style="font-weight:bold;">Property</td>
        <td>
            <a id="main_DetailsView1_HyperLink4" href="PropertyItem.aspx?code=Electric_Potential">Electric_Potential</a>
        </td>
    </tr>
</table>
"""
    table = BeautifulSoup(table_text, features='lxml')
    result = lookup_mnemonic._decompose_table_to_key_value(table, 'main_DetailsView1')
    assert result == {'Channel': 'A0',
                      'Description': 'Analog 0 (Regular)',
                      'Property': 'Electric_Potential',
                      'Unit quantity': 'ElectricPotential'}


@pytest.mark.parametrize(
    'table_text, table_id, expected',
    (
            ("""<table cellspacing="0" cellpadding="4" id="main_GridView1" style="font-size:X-Small;border-collapse:collapse;">
    <tr align="left" style="background-color:#E0E0E0;">
        <th scope="col">Code</th><th scope="col">Name</th>
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
""",
             'main_GridView1',
             [
                {'Code': '(MSCF/d)/ft/psi', 'Name': 'GeoFrame legacy unit', 'Standard Form': '1000 ft3/(d.ft.psi)',
                 'Dimension': 'Mobility', 'Scale': '1.55954244790036E-07', 'Offset': '0'},
                {'Code': '(MSCF/d)/psi', 'Name': 'GeoFrame legacy unit', 'Standard Form': '1000 ft3/(d.psi)',
                 'Dimension': 'FlowratePerPressure', 'Scale': '4.75348538120031E-08', 'Offset': '0'},
                {'Code': '(STB/d)/ft/psi', 'Name': 'GeoFrame legacy unit', 'Standard Form': 'bbl/(d.ft.psi)',
                 'Dimension': 'Mobility', 'Scale': '8.75618153524512E-10', 'Offset': '0'},
             ]
         ),
            (
                """<table cellspacing="0" cellpadding="4" id="main_GridView1" style="width:940px;border-collapse:collapse;">
    <tr align="left" style="background-color:#E0E0E0;font-size:X-Small;">
        <th scope="col">Unit</th>
        <th scope="col">Unit System</th>
        <th scope="col">Unit Quantity</th>
        <th scope="col">Dimension</th>
    </tr><tr>
        <td>(bbl/d)/(rev/s)</td>
        <td>ProductionEnglish</td>
        <td>FlowratePerRotationalVelocity</td>
        <td>VolumePerRotation</td>
    </tr><tr>
        <td>(rev/s)/(ft/min)</td>
        <td>ProductionEnglish</td>
        <td>RotationalVelocityPerVelocity</td>
        <td>RotationPerLength</td>
    </tr><tr>
        <td>gn</td>
        <td>Metric</td>
        <td>Gravity</td>
        <td>Acceleration</td>
    </tr>
""",
            'main_GridView1',
            [
                {'Unit': '(bbl/d)/(rev/s)', 'Unit System': 'ProductionEnglish',
              'Unit Quantity': 'FlowratePerRotationalVelocity', 'Dimension': 'VolumePerRotation'},
                {'Unit': '(rev/s)/(ft/min)', 'Unit System': 'ProductionEnglish',
              'Unit Quantity': 'RotationalVelocityPerVelocity', 'Dimension': 'RotationPerLength'},
                {'Unit': 'gn', 'Unit System': 'Metric', 'Unit Quantity': 'Gravity', 'Dimension': 'Acceleration'},
            ]
        ),
    ),
)
def test__decompose_table_by_header_row(table_text, table_id, expected):
    table = BeautifulSoup(table_text, features='lxml')
    result = lookup_mnemonic.decompose_table_by_header_row(table, table_id)
    assert result == expected
