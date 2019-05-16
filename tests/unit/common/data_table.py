
import pytest

from TotalDepth.common import data_table

SIMPLE_TABLE = [['Col 1', 'Col 2'], [1,2], [3, 4], [5, 6]]


def test_format_table_simple():
    formatted_table = table.format_table(SIMPLE_TABLE)
    expected = """Col 1 Col 2
    1     2
    3     4
    5     6"""
    # print(formatted_table)
    assert formatted_table == ['Col 1 Col 2', '    1     2', '    3     4', '    5     6']
    assert '\n'.join(formatted_table) == expected


def test_format_table_simple_sphinx():
    formatted_table = table.format_table(SIMPLE_TABLE, heading_underline='=')
    expected = """Col 1 Col 2
===== =====
    1     2
    3     4
    5     6"""
    # print(formatted_table)
    assert formatted_table == ['Col 1 Col 2', '===== =====', '    1     2', '    3     4', '    5     6']
    assert '\n'.join(formatted_table) == expected


def test_format_table_simple_pad():
    formatted_table = table.format_table(SIMPLE_TABLE, pad=' | ')
    expected = """Col 1 | Col 2
    1 |     2
    3 |     4
    5 |     6"""
    # print(formatted_table)
    assert formatted_table == ['Col 1 | Col 2', '    1 |     2', '    3 |     4', '    5 |     6']
    assert '\n'.join(formatted_table) == expected

