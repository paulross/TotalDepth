
import pytest

from TotalDepth.common import data_table

SIMPLE_TABLE = [['Col 1', 'Col 2'], [1, 2], [3, 4], [5, 6]]
SIMPLE_TABLE_WITH_FLOATS = [['Col 1', 'Col 2'], [1., 2.], [3., 4.], [5., 6.]]


def test_format_table_simple():
    formatted_table = data_table.format_table(SIMPLE_TABLE)
    expected = """Col 1 Col 2
    1     2
    3     4
    5     6"""
    # print(formatted_table)
    assert formatted_table == ['Col 1 Col 2', '    1     2', '    3     4', '    5     6']
    assert '\n'.join(formatted_table) == expected


def test_format_table_simple_raises():
    with pytest.raises(ValueError) as err:
        data_table.format_table([['Col 1', 'Col 2'], [1,]])
    assert err.value.args[0] == 'Rows not of equal length but lengths of {1, 2}'


def test_format_table_simple_sphinx():
    formatted_table = data_table.format_table(SIMPLE_TABLE, heading_underline='=')
    expected = """Col 1 Col 2
===== =====
    1     2
    3     4
    5     6"""
    # print(formatted_table)
    assert formatted_table == ['Col 1 Col 2', '===== =====', '    1     2', '    3     4', '    5     6']
    assert '\n'.join(formatted_table) == expected


def test_format_table_simple_pad():
    formatted_table = data_table.format_table(SIMPLE_TABLE, pad=' | ')
    expected = """Col 1 | Col 2
    1 |     2
    3 |     4
    5 |     6"""
    # print(formatted_table)
    assert formatted_table == ['Col 1 | Col 2', '    1 |     2', '    3 |     4', '    5 |     6']
    assert '\n'.join(formatted_table) == expected


def test_format_table_simple_floats():
    formatted_table = data_table.format_table(SIMPLE_TABLE_WITH_FLOATS)
    expected = """Col 1 Col 2
1.000 2.000
3.000 4.000
5.000 6.000"""
    # print(formatted_table)
    assert formatted_table == ['Col 1 Col 2', '1.000 2.000', '3.000 4.000', '5.000 6.000']
    # print('\n'.join(formatted_table))
    assert '\n'.join(formatted_table) == expected


def test_format_table_columns_simple_floats():
    formatted_table = data_table.format_table_columns(
        SIMPLE_TABLE_WITH_FLOATS,
        ['.6f', '.2f']
    )
    expected = """   Col 1 Col 2
1.000000  2.00
3.000000  4.00
5.000000  6.00"""
    # print(formatted_table)
    assert formatted_table == ['   Col 1 Col 2', '1.000000  2.00', '3.000000  4.00', '5.000000  6.00']
    # print('\n'.join(formatted_table))
    assert '\n'.join(formatted_table) == expected


