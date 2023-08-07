#!/usr/bin/env python
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 1999-2011 Paul Ross
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
"""Unit tests for LatLong

Created on Aug 03, 2023

@author: paulross
"""

__author__ = 'Paul Ross'
__date__ = 'Aug 03, 2023'
__version__ = '0.1.0'
__rights__ = 'Copyright (c) 2023 Paul Ross.'

import math

import pytest

from TotalDepth.LIS.core import LatLong


@pytest.mark.parametrize(
    'value_rad, expected',
    (
            (1.234, 1.234),
    )
)
def test_latitude_longitude_radians(value_rad, expected):
    lat_long = LatLong.LatitudeLongitude(value_rad)
    assert lat_long.radians() == expected


@pytest.mark.parametrize(
    'lat_long_str, expected_groups',
    (
            ('52 22\' 26.8" N', ('52', '22', '26.8', 'N')),
            # Leading and trailing space
            (' 52 22\' 26.8" N', ('52', '22', '26.8', 'N')),
            ('52 22\' 26.8" N ', ('52', '22', '26.8', 'N')),
            (' 52 22\' 26.8" N ', ('52', '22', '26.8', 'N')),
            # Space padding
            ('52    22\'    26.8"   N', ('52', '22', '26.8', 'N')),
            # S
            ('52 22\' 26.8" S', ('52', '22', '26.8', 'S')),
            # No '
            ('52 22 26.8" N', ('52', '22', '26.8', 'N')),
            # No "
            ('52 22\' 26.8 N', ('52', '22', '26.8', 'N')),
            # Missing 'N
            ('52 22\' 26.8"', None),
            # EW
            ('52 22\' 26.8" E', None),
            ('52 22\' 26.8" W', None),
            # Non NSEW
            ('52 22\' 26.8" X', None),
    )
)
def test_regex_dms_ns(lat_long_str, expected_groups):
    m = LatLong.RE_DMS_NS.match(lat_long_str)
    if expected_groups is None:
        assert m is None
    else:
        assert m is not None
        assert m.groups() == expected_groups


@pytest.mark.parametrize(
    'lat_long_str, expected_groups',
    (
            ('52 22\' 26.8" E', ('52', '22', '26.8', 'E')),
            # Leading and trailing space
            (' 52 22\' 26.8" E', ('52', '22', '26.8', 'E')),
            ('52 22\' 26.8" E ', ('52', '22', '26.8', 'E')),
            (' 52 22\' 26.8" E ', ('52', '22', '26.8', 'E')),
            # Space padding
            ('52    22\'    26.8"   E', ('52', '22', '26.8', 'E')),
            # S
            ('52 22\' 26.8" W', ('52', '22', '26.8', 'W')),
            # No '
            ('52 22 26.8" E', ('52', '22', '26.8', 'E')),
            # No "
            ('52 22\' 26.8 E', ('52', '22', '26.8', 'E')),
            # Missing E or W
            ('52 22\' 26.8"', None),
            # NS
            ('52 22\' 26.8" N', None),
            ('52 22\' 26.8" S', None),
            # Non NSEW
            ('52 22\' 26.8" X', None),
    )
)
def test_regex_dms_ew(lat_long_str, expected_groups):
    m = LatLong.RE_DMS_EW.match(lat_long_str)
    if expected_groups is None:
        assert m is None
    else:
        assert m is not None
        assert m.groups() == expected_groups


@pytest.mark.parametrize(
    'lat_long_str, expected_groups',
    (
            ('52 22\' 26.8"', (None, '52', '22', '26.8',)),
            ('+52 22\' 26.8"', ('+', '52', '22', '26.8',)),
            ('-52 22\' 26.8"', ('-', '52', '22', '26.8',)),
            # Leading and trailing space
            (' 52 22\' 26.8"', (None, '52', '22', '26.8',)),
            ('52 22\' 26.8" ', (None, '52', '22', '26.8',)),
            (' 52 22\' 26.8" ', (None, '52', '22', '26.8',)),
            # Space padding
            ('52    22\'    26.8" ', (None, '52', '22', '26.8',)),
            # No '
            ('52 22 26.8"', (None, '52', '22', '26.8',)),
            # No "
            ('52 22\' 26.8', (None, '52', '22', '26.8',)),
    )
)
def test_regex_dms(lat_long_str, expected_groups):
    m = LatLong.RE_DMS.match(lat_long_str)
    if expected_groups is None:
        assert m is None
    else:
        assert m is not None
        assert m.groups() == expected_groups


@pytest.mark.parametrize(
    'lat_long_str, expected_groups',
    (
            ('52 22.8\' N', ('52', '22.8', 'N')),
            ('52 22.87654321\' N', ('52', '22.87654321', 'N')),
            # Leading and trailing space
            (' 52 22.8\' N', ('52', '22.8', 'N')),
            ('52 22.8\' N ', ('52', '22.8', 'N')),
            (' 52 22.8\' N ', ('52', '22.8', 'N')),
            # Space padding
            ('52    22.8\'    N', ('52', '22.8', 'N')),
            # S
            ('52 22.8\' S', ('52', '22.8', 'S')),
            # No '
            ('52 22.8\' N', ('52', '22.8', 'N')),
            # No "
            ('52 22.8\' N', ('52', '22.8', 'N')),
            # Missing 'N
            ('52 22.8\'', None),
            # EW
            ('52 22.8\' E', None),
            ('52 22.8\' W', None),
            # Non NSEW
            ('52 22.8\' X', None),
    )
)
def test_regex_dm_ns(lat_long_str, expected_groups):
    m = LatLong.RE_DM_NS.match(lat_long_str)
    if expected_groups is None:
        assert m is None
    else:
        assert m is not None
        assert m.groups() == expected_groups


@pytest.mark.parametrize(
    'lat_long_str, expected_groups',
    (
            ('52 22.8\' E', ('52', '22.8', 'E')),
            # Leading and trailing space
            (' 52 22.8\' E', ('52', '22.8', 'E')),
            ('52 22.8\' E ', ('52', '22.8', 'E')),
            (' 52 22.8\' E ', ('52', '22.8', 'E')),
            # Space padding
            ('52    22.8\'   E', ('52', '22.8', 'E')),
            # S
            ('52 22.8\' W', ('52', '22.8', 'W')),
            # No '
            ('52 22.8\' E', ('52', '22.8', 'E')),
            # No "
            ('52 22.8\' E', ('52', '22.8', 'E')),
            # Missing E or W
            ('52 22.8\'', None),
            # NS
            ('52 22.8\' N', None),
            ('52 22.8\' S', None),
            # Non NSEW
            ('52 22.8\' X', None),
    )
)
def test_regex_dm_ew(lat_long_str, expected_groups):
    m = LatLong.RE_DM_EW.match(lat_long_str)
    if expected_groups is None:
        assert m is None
    else:
        assert m is not None
        assert m.groups() == expected_groups


@pytest.mark.parametrize(
    'lat_long_str, expected_groups',
    (
            ('52 22.8\'', (None, '52', '22.8',)),
            ('+52 22.8\'', ('+', '52', '22.8',)),
            ('-52 22.8\'', ('-', '52', '22.8',)),
            # Leading and trailing space
            (' 52 22.8\'', (None, '52', '22.8',)),
            ('52 22.8\' ', (None, '52', '22.8',)),
            (' 52 22.8\' ', (None, '52', '22.8',)),
            # Space padding
            ('52    22.8\'', (None, '52', '22.8',)),
            # No '
            ('52 22.8', (None, '52', '22.8',)),
    )
)
def test_regex_dm(lat_long_str, expected_groups):
    m = LatLong.RE_DM.match(lat_long_str)
    if expected_groups is None:
        assert m is None
    else:
        assert m is not None
        assert m.groups() == expected_groups


@pytest.mark.parametrize(
    'lat_long_str, expected_groups',
    (
            ('52.1234', (None, '52.1234',)),
            ('+52.1234', ('+', '52.1234',)),
            ('-52.1234', ('-', '52.1234',)),
            # Leading and trailing space
            ('   52.1234', (None, '52.1234',)),
            ('52.1234   ', (None, '52.1234',)),
            ('   52.1234   ', (None, '52.1234',)),
    )
)
def test_regex_decimal_degrees(lat_long_str, expected_groups):
    m = LatLong.RE_DECIMAL_DEGREES.match(lat_long_str)
    if expected_groups is None:
        assert m is None
    else:
        assert m is not None
        assert m.groups() == expected_groups


@pytest.mark.parametrize(
    'lat_long_str, expected_latitude',
    (
            # TODO:
            # Decimal degrees.
            ('52.1234', LatLong.Latitude(math.radians(52.1234))),
            ('-52.1234', LatLong.Latitude(math.radians(-52.1234))),
    )
)
def test_parse_str_for_latitude(lat_long_str, expected_latitude):
    latitude = LatLong.parse_str_for_latitude(lat_long_str)
    assert latitude == expected_latitude
