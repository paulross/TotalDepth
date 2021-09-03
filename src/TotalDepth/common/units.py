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
This provides Unit conversion information from lookup sources.

The primary source is Schlumberger's Oilfield Services Data Dictionary (OSDD): https://www.apps.slb.com/cmd/units.aspx

The fallback, secondary source, is from our static snapshot of that page which lives in
``src/TotalDepth/common/data/osdd_units.json``

When running tests with ``--runslow`` the ``tests.integration.common.test_units.test_slb_units_write_to_json`` test will
re-populate that static data file.

This included currencies that all have zero offset and unit scale.
Currencies: https://en.wikipedia.org/wiki/ISO_4217
ISO 4217 official currency codes in XML: https://www.currency-iso.org/dam/downloads/lists/list_one.xml
"""
import functools
import json
import logging
import os
import typing
from functools import lru_cache

from bs4 import BeautifulSoup
import numpy as np


from TotalDepth import ExceptionTotalDepth
from TotalDepth.common import lookup_mnemonic


class ExceptionUnits(ExceptionTotalDepth):
    """Base class exception for this module."""
    pass


class ExceptionUnitsLookup(ExceptionUnits):
    """Raised if the unit lookup fails."""
    pass


class ExceptionUnitsDimension(ExceptionUnits):
    """Raised if two units are of different dimensions."""
    pass


logger = logging.getLogger(__file__)


class Unit(typing.NamedTuple):
    """Represents one row in the table at https://www.apps.slb.com/cmd/units.aspx

    Examples::

        Code    Name                Standard Form   Dimension   Scale               Offset
        DEGC    'degree celsius'    degC            Temperature 1                   -273.15
        DEGF    'degree fahrenheit' degF            Temperature 0.555555555555556   -459.67
        DEGK    'kelvin'            K               Temperature 1                   0
        DEGR    'degree rankine'    degR            Temperature 0.555555555555556   0

    There will also be an entry for RP66V1 files::

        degF    'degree fahrenheit' "5/9 degC +32"  Temperature 0.555555555555556   -459.67

    So conversion from, say DEGC to DEGF is::

        ((value - DEGC.offset) * DEGC.scale) / DEGF.scale + DEGF.offset

        ((0.0 - -273.15) * 1.0) / 0.555555555555556 + -459.67 == 32.0
    """
    code: str  # This is how the units are identified in LIS or RP66V1 files.
    name: str  # Human comprehensible name such as 'degree fahrenheit'. Usually lower case.
    standard_form: str  # This is how the units are identified in RP66V1 files.
    dimension: str  # Class of units, example "Temperature"
    scale: float
    offset: float

    @property
    def is_primary(self) -> bool:
        """True if this is looks like a primary unit."""
        return self.offset == 0.0 and self.scale == 1.0

    def has_offset(self) -> bool:
        """True if this has an offset, for example DEGC. False otherwise, for example metres."""
        return self.offset != 0.0


def _slb_units_from_parse_tree(parse_tree: BeautifulSoup) -> typing.Dict[str, Unit]:
    """Parse the OSDD Units page for units."""
    raw_units = lookup_mnemonic.decompose_table_by_header_row(parse_tree, 'main_GridView1')
    ret: typing.Dict[str, Unit] = {}
    for raw_unit in raw_units:
        unit = Unit(
            raw_unit['Code'].strip(),
            raw_unit['Name'].strip(),
            raw_unit['Standard Form'].strip(),
            raw_unit['Dimension'].strip(),
            float(raw_unit['Scale'].strip()),
            float(raw_unit['Offset'].strip()),
        )
        ret[unit.code] = unit
    return ret


def osdd_data_file_path() -> str:
    """Path to our static snapshot of the OSDD units page."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'osdd_units.json'))


def read_osdd_static_data() -> typing.Dict[str, Unit]:
    """Read our static snapshot of the OSDD units page."""
    with open(osdd_data_file_path()) as file:
        result = {k: Unit(*v) for k, v in json.load(file).items()}
    return result


@lru_cache(maxsize=1)
def _slb_units() -> typing.Dict[str, Unit]:
    """Reads and caches the table of units at https://www.apps.slb.com/cmd/units.aspx

    Units
    -----

    https://www.apps.slb.com/cmd/units.aspx


    Example::

        <table cellspacing="0" cellpadding="4" id="main_GridView1" style="font-size:X-Small;border-collapse:collapse;">
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
    """
    logger.info('Loading all units into the cache')
    try:
        parse_tree = lookup_mnemonic._parse_url_to_beautiful_soup('https://www.apps.slb.com/cmd/units.aspx')
        ret = _slb_units_from_parse_tree(parse_tree)
    except lookup_mnemonic.ExceptionLookupMnemonicReadURL as _err:  # pragma: no cover
        logger.info('Falling back to the units static data.')
        ret = read_osdd_static_data()
    return ret


def slb_load_units():
    """Eagerly load the units into the cache."""
    _slb_units()


def has_slb_units(unit_code: str) -> bool:
    """Returns True if the Schlumberger Unit exists."""
    return unit_code in _slb_units()


def slb_units(unit: str) -> Unit:
    """Returns the Schlumberger Unit corresponding to the unit code."""
    return _slb_units()[unit]


@lru_cache(maxsize=1)
def _slb_unit_standard_form_to_unit_codes() -> typing.Dict[str, typing.List[str]]:
    """
    Returns the cached map of standard form to unit code.
    Example given 'degC' this returns 'DEGC'.
    """
    logger.info('Loading all unit standard forms into the cache')
    unit_map = _slb_units()
    ret: typing.Dict[str, typing.List[str]] = {}
    for k, v in unit_map.items():
        if v.standard_form:
            # print(f'TRACE: "{k}" "{v.standard_form}"')
            if v.standard_form not in ret:
                # raise ExceptionLookupMnemonicUnit(f'Duplicate standard form of units "{v.standard_form}"')
                ret[v.standard_form] = [k]
            else:
                ret[v.standard_form].append(k)
    return ret


def has_slb_standard_form(standard_form: str) -> bool:
    """Returns True if an entry for the standard form exists."""
    return standard_form in _slb_unit_standard_form_to_unit_codes()


def slb_standard_form_to_unit_code(standard_form: str) -> typing.List[Unit]:
    """
    Returns the unit(s) corresponding to the standard form.
    Example given 'degC' this returns the Units corresponding to ['DEGC', 'deg C', 'oC'].
    """
    standard_form_to_unit_code_dict = _slb_unit_standard_form_to_unit_codes()
    try:
        unit_codes = standard_form_to_unit_code_dict[standard_form]
    except KeyError:
        raise ExceptionUnitsLookup(f'No record of unit corresponding to standard form {standard_form}')
    return [slb_units(unit_code) for unit_code in unit_codes]


def same_dimension(a: Unit, b: Unit) -> bool:
    """Returns True if both units have the same dimension."""
    return a.dimension == b.dimension


def _convert(value: float, unit_from: Unit, unit_to: Unit) -> float:
    """Converts a value from one unit to another with no error checking.

    Examples::

        Code    Name                Standard Form   Dimension   Scale               Offset
        DEGC    'degree celsius'    degC            Temperature 1                   -273.15
        DEGF    'degree fahrenheit' degF            Temperature 0.555555555555556   -459.67

    So conversion from, say DEGC to DEGF is::

        ((value - DEGC.offset) * DEGC.scale) / DEGF.scale + DEGF.offset

        ((0.0 - -273.15) * 1.0) / 0.555555555555556 + -459.67 == 32.0
    """
    if unit_from.has_offset() or unit_to.has_offset():
        return ((value - unit_from.offset) * unit_from.scale) / unit_to.scale + unit_to.offset
    # Minor optimisation by ignoring offsets where possible.
    return value * unit_from.scale / unit_to.scale


def convert(value: float, unit_from: Unit, unit_to: Unit) -> float:
    """Converts a value from one unit to another.

    Examples::

        Code    Name                Standard Form   Dimension   Scale               Offset
        DEGC    'degree celsius'    degC            Temperature 1                   -273.15
        DEGF    'degree fahrenheit' degF            Temperature 0.555555555555556   -459.67

    So conversion from, say DEGC to DEGF is::

        ((value - DEGC.offset) * DEGC.scale) / DEGF.scale + DEGF.offset

        ((0.0 - -273.15) * 1.0) / 0.555555555555556 + -459.67 == 32.0
    """
    if not same_dimension(unit_from, unit_to):
        raise ExceptionUnitsDimension(f'Units {unit_from} and {unit_to} are not the same dimension.')
    ret = _convert(value, unit_from, unit_to)
    return ret


def convert_function(unit_from: Unit, unit_to: Unit) -> typing.Callable:
    """Return a partial function to convert from one units to another."""
    if not same_dimension(unit_from, unit_to):
        raise ExceptionUnitsDimension(f'Units {unit_from} and {unit_to} are not the same dimension.')
    return functools.partial(_convert, unit_from=unit_from, unit_to=unit_to)


def convert_array(array: np.ndarray, unit_from: Unit, unit_to: Unit) -> np.ndarray:
    """Convert an array of values."""
    if unit_from.has_offset() or unit_to.has_offset():
        return ((array - unit_from.offset) * unit_from.scale) / unit_to.scale + unit_to.offset
    # Minor optimisation by ignoring offsets where possible.
    return array * (unit_from.scale / unit_to.scale)


def convert_array_inplace(array: np.ndarray, unit_from: Unit, unit_to: Unit) -> None:
    """Convert an array of values in-place."""
    if unit_from.has_offset() or unit_to.has_offset():
        array -= unit_from.offset
        array *= unit_from.scale
        array /= unit_to.scale
        array += unit_to.offset
    else:
        # Minor optimisation by ignoring offsets where possible.
        array *= unit_from.scale / unit_to.scale
