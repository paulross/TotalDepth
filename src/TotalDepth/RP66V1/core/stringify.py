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
import pprint
import typing

from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core.LogicalRecord import EFLR


def stringify_object_by_type(obj: typing.Any) -> str:
    """Convert objects to strings for HTML or text presentation."""
    if isinstance(obj, RepCode.ObjectName):
        # return obj.I.decode('ascii')
        # return str(obj)
        return f'{obj.I.decode("ascii")} (O: {obj.O} C: {obj.C})'
    if isinstance(obj, EFLR.AttributeBase):
        return stringify_object_by_type(obj.value)
    if obj is None:
        return '-'
    if isinstance(obj, bytes):
        # print('TRACE:', obj)
        try:
            return obj.decode('ascii')
        except UnicodeDecodeError:
            return obj.decode('latin-1')
    if isinstance(obj, list):
        if len(obj) == 1:
            return stringify_object_by_type(obj[0])
        return '[' + ', '.join(stringify_object_by_type(o) for o in obj) + ']'
    if isinstance(obj, tuple):
        if len(obj) == 1:
            return stringify_object_by_type(obj[0])
        return '(' + ', '.join(stringify_object_by_type(o) for o in obj) + ')'
    return str(obj)
