"""
Formats a table as a list of printable strings.
"""
import numpy as np

import typing


def format_object(o: typing.Any) -> str:
    # print(type(o))
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
