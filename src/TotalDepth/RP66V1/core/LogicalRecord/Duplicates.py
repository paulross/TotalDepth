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
import enum


class DuplicateObjectStrategy(enum.Enum):
    """Different strategies for dealing with a duplicate object already encountered in a table.

    RAISE: Raise an exception.

    IGNORE: Ignore the duplicate object regardless of its content, do not add it to the table or the object_name_map.

    REPLACE: Always use the duplicate object and replace the object in the object_name_map regardless of its content.

    REPLACE_IF_DIFFERENT: Use the duplicate object only if different then replace the object in the object_name_map

    REPLACE_LATER_COPY: Use the duplicate object only if the object copy number is greater than the original copy number
    then replace the object in the object_name_map (the original is retained in the list of objects).

    Other possibilities:

    - Walk through the attributes replacing any that have a greater copy number?
    """
    RAISE = enum.auto()
    IGNORE = enum.auto()
    REPLACE = enum.auto()
    REPLACE_IF_DIFFERENT = enum.auto()
    REPLACE_LATER_COPY = enum.auto()