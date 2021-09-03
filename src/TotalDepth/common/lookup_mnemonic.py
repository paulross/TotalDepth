#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation.
# Copyright (C) 2011-2021 Paul Ross
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Paul Ross: apaulross@gmail.com
"""

Schlumberger Data
=================

https://www.apps.slb.com/cmd/

"The Curve Mnemonic Dictionary is the publicly accessible version of the Oilfield Services Data Dictionary (OSDD)."


Mnemonics
---------

URL is of the form::

    https://www.apps.slb.com/cmd/<TYPE>.aspx?code=<NAME>

Where <TYPE> is:

Data channels: ChannelItem
Parameters: ParameterItem
Logging Tools: ToolItem
Software Products: ProductItem

Examples::

    https://www.apps.slb.com/cmd/ChannelItem.aspx?code=RHOB
    https://www.apps.slb.com/cmd/ParameterItem.aspx?code=LATI
    https://www.apps.slb.com/cmd/ToolItem.aspx?code=HDT


Anything that does not start with [A-Z] is in https://www.apps.slb.com/cmd/ChannelsList.aspx?start=na

Example::

    https://www.apps.slb.com/cmd/ChannelItem.aspx?code=A0

Content contains the key/value table::


    <table cellspacing="5" cellpadding="1" id="main_DetailsView1" style="width:492px;">
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


Data Channels
-------------

Example::

    https://www.apps.slb.com/cmd/ChannelItem.aspx?code=RHOB


Channels have the attributes: Channel, Description, Unit quantity, Property as key/value in a table 'main_DetailsView1'.


In the table 'main_GridView1' there are 'Related tools' as a list of key/value::

    <th scope="col">Tool</th><th scope="col">Description</th>


In the table 'main_GridView2' there are 'Related products' as a list of key/value::

    <th scope="col">Product</th><th scope="col">Description</th>


Parameters
----------

Example::

    https://www.apps.slb.com/cmd/ParameterItem.aspx?code=LATI

Parameters have the attributes: Code, Description, Unit quantity, Property in a key/value table 'main_DetailsView1'.

They also have 'Related products' in the 'main_GridView2' a table with a list of key/values::

    <th scope="col">Product</th><th scope="col">Description</th>


Logging Tools
-------------

Example::

    https://www.apps.slb.com/cmd/ToolItem.aspx?code=HDT

In the table 'main_DetailsView1' a ToolItem has the attributes: Code, Technology, Discipline, Method, Description as a
key/value table.

Example::

    Code        HDT
    Technology  Dipmeter
    Discipline  Geology
    Method      WIRELINE
    Description High Resolution Dipmeter Tool

They also have 'Related Channels' in the 'main_GridView1' a table a list of key/values::

    <th scope="col">Channel</th><th scope="col">Description</th>

They also have 'Related Parameters' in the 'main_GridView2' a table a list of key/values::

    <th scope="col">Parameter</th><th scope="col">Description</th>


Software Products
-----------------

Example::

    https://www.apps.slb.com/cmd/ProductItem.aspx?code=CALCULATE_TRAJECTORY

In the table 'main_DetailsView1' has the attributes: Code, Name, Discipline, Type, Description as a key/value table.

They also have 'Related Channels' in the 'main_GridView1' a table a list of key/values with links to ChannelItem::

    <th scope="col">Channel</th><th scope="col">Description</th>


Properties
----------

Example::

    https://www.apps.slb.com/cmd/PropertyItem.aspx?code=Diameter


In the table 'main_DetailsView1' has the attributes: Code, Name, Parents, Description as a key/value table.


Parents are as a hierarchy, for example::

    <td style="font-weight:bold;">Parents</td>
    <td>&nbsp;
        <span id="main_DetailsView1_labParents">
            <a href="PropertyItem.aspx?code=Property">Property</a>
        &gt;
            <a href="PropertyItem.aspx?code=Length">Length</a>
        </span>
    </td>

They also have 'Related children' in the 'main_GridView1' a table a list of key/values with links to PropertyItem::

    <th scope="col">Code</th><th scope="col">Name</th>


Units
-----

See slb_units()



Unit assingnment:

https://www.apps.slb.com/cmd/unitassignment.aspx


Example::

    <table cellspacing="0" cellpadding="4" id="main_GridView1" style="width:940px;border-collapse:collapse;">
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


"""
import logging
import typing
from functools import lru_cache

from bs4 import BeautifulSoup
import requests


from TotalDepth import ExceptionTotalDepth


logger = logging.getLogger(__file__)


class ExceptionLookupMnemonic(ExceptionTotalDepth):
    pass


class ExceptionLookupMnemonicReadURL(ExceptionLookupMnemonic):
    pass


class ExceptionLookupMnemonicTable(ExceptionLookupMnemonic):
    pass


class ExceptionLookupMnemonicReadTable(ExceptionLookupMnemonic):
    pass


def _parse_url_to_beautiful_soup(url: str) -> BeautifulSoup:
    logger.info('Parsing URL %s', url)
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError as err:  # pragma: no cover
        raise ExceptionLookupMnemonicReadURL(f'URP request {url} raised: {err}')
    if response.status_code != 200:  # pragma: no cover
        raise ExceptionLookupMnemonicReadURL(f'URP request {url} failed: {response.status_code}')
    logger.info('Parsed %d bytes from URL %s ', len(response.text), url)
    parse_tree = BeautifulSoup(response.text, features='lxml')
    return parse_tree


def _decompose_table_to_key_value(parse_tree: BeautifulSoup, table_id: str) -> typing.Dict[str, str]:
    tables = parse_tree.find_all('table', id=table_id)
    if len(tables) != 1:  # pragma: no cover
        raise ExceptionLookupMnemonicTable('Multiple tables')
    table = tables[0]
    ret = {}
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) != 2:  # pragma: no cover
            raise ExceptionLookupMnemonicReadTable(f'Expected two cells but found {len(cells)}')
        ret[cells[0].text.strip()] = cells[1].text.strip()
    return ret


def decompose_table_by_header_row(parse_tree: BeautifulSoup, table_id: str) -> typing.List[typing.Dict[str, str]]:
    """Return a list of rows from an HTML table of given ID."""
    tables = parse_tree.find_all('table', id=table_id)
    if len(tables) != 1:  # pragma: no cover
        raise ExceptionLookupMnemonicTable('Multiple tables')
    table = tables[0]
    ret = []
    for r, row in enumerate(table.find_all('tr')):
        if r == 0:
            titles = [cell.text.strip() for cell in row.find_all('th')]
            if len(set(titles)) != len(titles):  # pragma: no cover
                raise ExceptionLookupMnemonicReadTable(f'Header row is not unique {titles}')
        else:
            values = [cell.text.strip() for cell in row.find_all('td')]
            if len(titles) != len(values):  # pragma: no cover
                raise ExceptionLookupMnemonicReadTable(
                    f'Length of header row {len(titles)} != length of values {len(values)}'
                )
            ret.append({k: v for k, v in zip(titles, values)})
    return ret


def _slb_url(data_type: str, name: str) -> str:
    return f'https://www.apps.slb.com/cmd/{data_type}.aspx?code={name}'


class ProductDescription(typing.NamedTuple):
    product: str  # 'Product'
    description: str  # 'Description'


class ToolDescription(typing.NamedTuple):
    tool: str  # 'Tool'
    description: str  # 'Description'


class Channel(typing.NamedTuple):
    channel: str  # 'Channel'
    description: str  # 'Description'
    unit_quantity: str  # 'Unit quantity'
    property: str  # Property
    related_tools: typing.Tuple[ToolDescription]
    related_products: typing.Tuple[ProductDescription]


def _get_product_description(parse_tree: BeautifulSoup, table_id: str) -> typing.Tuple[ProductDescription]:
    raw_products = decompose_table_by_header_row(parse_tree, table_id)
    ret = tuple(ProductDescription(d['Product'], d['Description']) for d in raw_products)
    return ret


def _slb_data_channel(parse_tree: BeautifulSoup) -> Channel:
    details_dict = _decompose_table_to_key_value(parse_tree, 'main_DetailsView1')
    raw_related_tools = decompose_table_by_header_row(parse_tree, 'main_GridView1')
    related_tools_list = tuple(ToolDescription(d['Tool'], d['Description']) for d in raw_related_tools)
    related_products = _get_product_description(parse_tree, 'main_GridView2')
    ret = Channel(
        details_dict['Channel'],
        details_dict['Description'],
        details_dict['Unit quantity'],
        details_dict['Property'],
        related_tools_list,
        related_products,
    )
    return ret


@lru_cache(maxsize=128)
def slb_data_channel(name: str) -> Channel:
    """Returns the Channel corresponding to the name. This is a cached live lookup."""
    logger.info('Loading channel "%s" into the cache', name)
    url = _slb_url('ChannelItem', name)
    parse_tree = _parse_url_to_beautiful_soup(url)
    return _slb_data_channel(parse_tree)


class Parameter(typing.NamedTuple):
    code: str  # 'Code'
    description: str  # 'Description'
    unit_quantity: str  # 'Unit quantity'
    property: str  # Property
    related_products: typing.Tuple[ProductDescription]


def _slb_parameter(parse_tree: BeautifulSoup) -> Parameter:
    details_dict = _decompose_table_to_key_value(parse_tree, 'main_DetailsView1')
    related_products = _get_product_description(parse_tree, 'main_GridView2')
    ret = Parameter(
        details_dict['Code'],
        details_dict['Description'],
        details_dict['Unit quantity'],
        details_dict['Property'],
        related_products
    )
    return ret


@lru_cache(maxsize=256)
def slb_parameter(name: str) -> Parameter:
    """Returns the Parameter corresponding to the name. This is a cached live lookup."""
    logger.info('Loading paraameter "%s" into the cache', name)
    url = _slb_url('ParameterItem', name)
    parse_tree = _parse_url_to_beautiful_soup(url)
    return _slb_parameter(parse_tree)


class ChannelDescription(typing.NamedTuple):
    channel: str  # 'Channel'
    description: str  # 'Description'


def _get_channel_description(parse_tree: BeautifulSoup, table_id: str) -> typing.Tuple[ChannelDescription]:
    raw_chaannels = decompose_table_by_header_row(parse_tree, table_id)
    ret = tuple(ChannelDescription(d['Channel'], d['Description']) for d in raw_chaannels)
    return ret


class ParameterDescription(typing.NamedTuple):
    parameter: str  # 'Parameter'
    description: str  # 'Description'


def _get_parameter_description(parse_tree: BeautifulSoup, table_id: str) -> typing.Tuple[ParameterDescription]:
    raw_channels = decompose_table_by_header_row(parse_tree, table_id)
    ret = tuple(ParameterDescription(d['Parameter'], d['Description']) for d in raw_channels)
    return ret


class LoggingTool(typing.NamedTuple):
    code: str  # 'Code'
    technology: str  # 'Technology'
    discipline: str  # 'Discipline'
    method: str  # 'Method'
    description: str  # 'Description'
    related_channels: typing.Tuple[ChannelDescription]
    related_parameters: typing.Tuple[ParameterDescription]


def _slb_logging_tool(parse_tree: BeautifulSoup) -> LoggingTool:
    details_dict = _decompose_table_to_key_value(parse_tree, 'main_DetailsView1')
    related_channels = _get_channel_description(parse_tree, 'main_GridView1')
    related_parameters = _get_parameter_description(parse_tree, 'main_GridView2')
    ret = LoggingTool(
        details_dict['Code'],
        details_dict['Technology'],
        details_dict['Discipline'],
        details_dict['Method'],
        details_dict['Description'],
        related_channels,
        related_parameters,
    )
    return ret


@lru_cache(maxsize=64)
def slb_logging_tool(name: str) -> LoggingTool:
    """
    Logging Tools

    Example::

        https://www.apps.slb.com/cmd/ToolItem.aspx?code=HDT

    In the table 'main_DetailsView1' a ToolItem has the attributes: Code, Technology, Discipline, Method, Description
    as a key/value table.

    Example::

        Code        HDT
        Technology  Dipmeter
        Discipline  Geology
        Method      WIRELINE
        Description High Resolution Dipmeter Tool

    They also have 'Related Channels' in the 'main_GridView1' a table a list of key/values::

        <th scope="col">Channel</th><th scope="col">Description</th>

    They also have 'Related Parameters' in the 'main_GridView2' a table a list of key/values::

        <th scope="col">Parameter</th><th scope="col">Description</th>

    """
    logger.info('Loading tool "%s" into the cache', name)
    url = _slb_url('ToolItem', name)
    parse_tree = _parse_url_to_beautiful_soup(url)
    return _slb_logging_tool(parse_tree)
