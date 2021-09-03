"""
These require network access to https://www.apps.slb.com/cmd/...
"""
import pytest

from TotalDepth.common import lookup_mnemonic


@pytest.mark.slow
def test_slb_parameter_lati():
    result = lookup_mnemonic.slb_parameter('LATI')
    assert result.code == 'LATI'
    assert result.description == 'Latitude'
    assert result.unit_quantity == 'Dimensionless'
    assert result.property == 'Latitude'
    assert result.related_products == (
        lookup_mnemonic.ProductDescription(product='CSUD_WSD', description='Latitude'),
        lookup_mnemonic.ProductDescription(product='MAXIS_WSD', description='Latitude'),
    )


@pytest.mark.slow
def test_slb_channel_rhob():
    result = lookup_mnemonic.slb_data_channel('RHOB')
    assert result.channel == 'RHOB'
    assert result.description == 'Bulk Density'
    assert result.unit_quantity == 'Density'
    assert result.property == 'Bulk_Density'
    assert len(result.related_tools) > 0
    assert len(result.related_products) > 0


@pytest.mark.slow
def test_slb_logging_tool_hdt():
    result = lookup_mnemonic.slb_logging_tool('HDT')
    assert result.code == 'HDT'
    assert result.technology == 'Dipmeter'
    assert result.discipline == 'Geology'
    assert result.method == 'WIRELINE'
    assert result.description == 'High Resolution Dipmeter Tool'
    assert len(result.related_channels) > 0
    assert len(result.related_parameters) > 0
