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
Formats a table as a list of printable strings.

TODO: Support specific styles:

Sphinx style::

    +------------------------+------------+----------+----------+
    | Header row, column 1   | Header 2   | Header 3 | Header 4 |
    | (header rows optional) |            |          |          |
    +========================+============+==========+==========+
    | body row 1, column 1   | column 2   | column 3 | column 4 |
    +------------------------+------------+----------+----------+
    | body row 2             | ...        | ...      |          |
    +------------------------+------------+----------+----------+

Result:

+------------------------+------------+----------+----------+
| Header row, column 1   | Header 2   | Header 3 | Header 4 |
| (header rows optional) |            |          |          |
+========================+============+==========+==========+
| body row 1, column 1   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | ...        | ...      |          |
+------------------------+------------+----------+----------+

Markdown style::

    | Calculation | Video Time t (s) | Distance from start of Runway (m) | Distance from start of Runway at t=0 (m) |
    | --- | --: | --: | --: |
    | Mid speed -10 knots | -30.1 | 537 | 1325 |
    | Mid speed | -32.8 | 232 | 1182 |
    | Mid speed +10 knots | -35.6 | -87 | 1039 |
    | **Range and worst error** | **-32.8 ±2.8** | **232 ±319** | **1182 ±143** |


"""
import re

import numpy as np

import typing


def format_object(o: typing.Any) -> str:
    """Format a value as a string."""
    if isinstance(o, (float, np.float64, np.float32)):
        return f'{o:.3f}'
    return str(o)


def format_table(rows: typing.Sequence[typing.Sequence[typing.Any]],
                 pad: str = ' ',
                 heading_underline: str = '',
                 left_flush: bool = False,
                 ) -> typing.List[str]:
    """Given a table of strings this formats them as a list of strings."""
    ret = []
    flush_char = '<' if left_flush else '>'
    if len(rows):
        len_rows = set(len(row) for row in rows)
        if len(len_rows) != 1:
            raise ValueError(f'Rows not of equal length but lengths of {len_rows}')
        str_table = [[format_object(o) for o in row] for row in rows]
        column_widths = [max([len(s) for s in col]) for col in zip(*str_table)]
        if heading_underline:
            ret.append(pad.join([f'{s:{flush_char}{w}}' for s, w in zip(str_table[0], column_widths)]))
            ret.append(pad.join([f'{heading_underline * w}' for w in column_widths]))
            for row in str_table[1:]:
                ret.append(pad.join([f'{s:{flush_char}{w}}' for s, w in zip(row, column_widths)]))
        else:
            for row in str_table:
                ret.append(pad.join([f'{s:{flush_char}{w}}' for s, w in zip(row, column_widths)]))
    return ret


def format_table_columns(
        rows: typing.Sequence[typing.Sequence[typing.Any]],
        column_formats: typing.List[str],
        pad: str = ' ',
        heading_underline: str = '',
        ) -> typing.List[str]:
    """Given a list of objects this formats them as a list of strings."""
    table = [rows[0]]
    for row in rows[1:]:
        table_row = []
        for c, value in enumerate(row):
            table_row.append(f'{value:{column_formats[c]}}')
        table.append(table_row)
    return format_table(table, pad, heading_underline)
