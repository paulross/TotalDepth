"""
Formats a table as a list of printable strings.

Sphinx style:

+------------------------+------------+----------+----------+
| Header row, column 1   | Header 2   | Header 3 | Header 4 |
| (header rows optional) |            |          |          |
+========================+============+==========+==========+
| body row 1, column 1   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | ...        | ...      |          |
+------------------------+------------+----------+----------+

Markdown:

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
    if isinstance(o, (float, np.float64, np.float32)):
        return f'{o:.3f}'
    return str(o)


def format_table(rows: typing.Sequence[typing.Sequence[typing.Any]],
                 pad: str = ' ',
                 heading_underline: str = '',
                 ) -> typing.List[str]:
    ret = []
    if len(rows):
        if len(set(len(row) for row in rows)) != 1:
            raise ValueError(f'Rows not of equal length but lengths of {rows}')
        str_table = [[format_object(o) for o in row] for row in rows]
        column_widths = [max([len(s) for s in col]) for col in zip(*str_table)]
        if heading_underline:
            ret.append(pad.join([f'{s:>{w}}' for s, w in zip(str_table[0], column_widths)]))
            ret.append(pad.join([f'{heading_underline * w}' for w in column_widths]))
            for row in str_table[1:]:
                ret.append(pad.join([f'{s:>{w}}' for s, w in zip(row, column_widths)]))
        else:
            for row in str_table:
                ret.append(pad.join([f'{s:>{w}}' for s, w in zip(row, column_widths)]))
    return ret


RE_BREAK_POINT = re.compile(r'^(.+)[ ,\-].+$')


def _split_cell(s: str, max_width: int) -> typing.Sequence[typing.Sequence[str]]:
    assert max_width > 0
    if len(s) <= max_width:
        return [s]
    ret = []
    while s:
        m = RE_BREAK_POINT.match(s[:max_width])
        if m:
            ret.append(m.group(1))
            s = s[:len(ret[-1])+1].strip()
        else:
            ret.append(s[:max_width])
            s = s[:max_width]
    return ret


def wrap_cells(str_table: typing.Sequence[typing.Sequence[str]], max_width: int) -> typing.Sequence[typing.Sequence[str]]:
    column_widths = [max([len(s) for s in col]) for col in zip(*str_table)]
    must_wrap = [w > max_width for w in column_widths]
    if not any(must_wrap):
        return str_table
    ret = []
    for row in str_table:
        pass

    return ret
