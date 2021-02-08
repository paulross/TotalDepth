#!/usr/bin/env python
# Part of TotalDepth: Petrophysical data processing and presentation
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
"""Tests DictTree."""

import os
import unittest

import pytest

from TotalDepth.util import DictTree


__author__ = 'Paul Ross'
__date__ = '2009-09-15'
__version__ = '0.8.0'
__rights__ = 'Copyright (c) Paul Ross'


def test_dict_tree_ctor():
    dict_tree = DictTree.DictTree()
    assert dict_tree is not None


def test_dict_tree_ctor_empty():
    dict_tree = DictTree.DictTree()
    assert dict_tree.keys() == []
    assert dict_tree.values() == []
    assert len(dict_tree) == 0
    assert dict_tree.depth() == 0


def test_dict_tree_wrong_value_iterable_raises():
    with pytest.raises(DictTree.ExceptionDictTree) as err:
        DictTree.DictTree(value_iterable='int')
    assert err.value.args[0] == '"int" not in acceptable range: (None, \'list\', \'set\')'


def test_dict_tree_setting_wrong_value_iterable_raises():
    dict_tree = DictTree.DictTree()
    dict_tree.value_iterable = 'int'
    with pytest.raises(DictTree.ExceptionDictTree) as err:
        dict_tree.add(list(range(1)), 'one')
    assert err.value.args[0] == '"int" not in acceptable range: (None, \'list\', \'set\')'


def test_dict_tree_simple_add_keys():
    dt = DictTree.DictTree()
    dt.add(list(range(4)), 'four')
    assert dt.keys() == [list(range(4))]


def test_dict_tree_simple_add_values():
    dt = DictTree.DictTree()
    dt.add(list(range(4)), 'four')
    assert dt.values() == ['four']


def test_dict_tree_simple_add_value():
    dt = DictTree.DictTree()
    dt.add(list(range(4)), 'four')
    assert dt.value(list(range(4))) == 'four'


def test_dict_tree_simple_add_value_none():
    dt = DictTree.DictTree()
    dt.add(list(range(4)), 'four')
    assert dt.value(list(range(3))) is None


def test_dict_tree_simple_add_len():
    dt = DictTree.DictTree()
    dt.add(list(range(4)), 'four')
    assert len(dt) == 1


def test_dict_tree_simple_add_depth():
    dt = DictTree.DictTree()
    dt.add(list(range(4)), 'four')
    assert dt.depth() == 4


@pytest.mark.parametrize(
    'key, expected',
    (
            (list(range(3)), False),
            (list(range(4)), True),
            (list(range(5)), False),
    )
)
def test_dict_tree_simple_add_contains(key, expected):
    dt = DictTree.DictTree()
    dt.add(list(range(4)), 'four')
    assert (key in dt) == expected


@pytest.mark.parametrize(
    'key_values, expected',
    (
        (
            [
                ([0, 1, 2], 'two'),
            ],
            [
                [0, 1, 2]
            ],
        ),
        (
            [
                ([0, 1, 2], 'two'),
                ([0, 1, 2, 3], 'three'),
            ],
            [
                [0, 1, 2],
                [0, 1, 2, 3],
            ],
        ),
        # Reverse insert order check.
        (
            [
                ([0, 1, 2, 3], 'three'),
                ([0, 1, 2], 'two'),
            ],
            [
                [0, 1, 2],
                [0, 1, 2, 3],
            ],
        ),
    )
)
def test_dict_tree_keys(key_values, expected):
    dt = DictTree.DictTree()
    for key, value in key_values:
        dt.add(key, value)
    assert dt.keys() == expected


@pytest.mark.parametrize(
    'key_values, expected',
    (
        (
            [
                ([0, 1, 2], 'two'),
            ],
            ['two', ],
        ),
        (
            [
                ([0, 1, 2], 'two'),
                ([0, 1, 2, 3], 'three'),
            ],
            ['two', 'three', ],
        ),
        # Reverse insert order check.
        (
            [
                ([0, 1, 2, 3], 'three'),
                ([0, 1, 2], 'two'),
            ],
            ['two', 'three', ],
        ),
    )
)
def test_dict_tree_values(key_values, expected):
    dt = DictTree.DictTree()
    for key, value in key_values:
        dt.add(key, value)
    assert dt.values() == expected


@pytest.mark.parametrize(
    'key_values, expected',
    (
        (
            [
                ([0, 1, 2], 'two'),
            ],
            [
                ([0, 1, 2], 'two'),
            ],
        ),
        (
            [
                ([0, 1, 2], 'two'),
                ([0, 1, 2, 3], 'three'),
            ],
            [
                ([0, 1, 2], 'two'),
                ([0, 1, 2, 3], 'three'),
            ],
        ),
        # Reverse insert order check.
        (
            [
                ([0, 1, 2, 3], 'three'),
                ([0, 1, 2], 'two'),
            ],
            [
                ([0, 1, 2], 'two'),
                ([0, 1, 2, 3], 'three'),
            ],
        ),
    )
)
def test_dict_tree_items(key_values, expected):
    dt = DictTree.DictTree()
    for key, value in key_values:
        dt.add(key, value)
    assert list(dt.items()) == expected


@pytest.mark.parametrize(
    'key_values, expected',
    (
        (
            [
                ([0, 1, 2], 'two'),
            ],
            """0
  1
    2
      two""",
        ),
        (
            [
                ([0, 1, 2], 'two'),
                ([0, 1, 2, 3], 'three'),
            ],
            """0
  1
    2
      two
      3
        three""",
        ),
        # Reverse insert order check.
        (
            [
                ([0, 1, 2, 3], 'three'),
                ([0, 1, 2], 'two'),
            ],
            """0
  1
    2
      two
      3
        three""",
        ),
        (
                [
                    ([0, 1, ], 'one'),
                    ([0, 1, 2, 3], 'three'),
                    ([0, 1, 2, 3, 4, 5], 'five'),
                ],
                """0
  1
    one
    2
      3
        three
        4
          5
            five""",
        ),
    )
)
def test_dict_tree_add_indented_string(key_values, expected):
    dt = DictTree.DictTree()
    for key, value in key_values:
        dt.add(key, value)
    assert dt.indented_string() == expected


def test_add_remove_and_stringise():
    dict_tree = DictTree.DictTree()
    dict_tree.add(list(range(2)), 'one')
    dict_tree.add(list(range(4)), 'three')
    dict_tree.add(list(range(6)), 'five')
    assert dict_tree.keys() == [
            list(range(2)),
            list(range(4)),
            list(range(6)),
        ]
    assert dict_tree.values() == ['one', 'three', 'five', ]
    assert len(dict_tree) == 3
    assert dict_tree.indented_string() == """0
  1
    one
    2
      3
        three
        4
          5
            five"""
    dict_tree.remove(list(range(4)))
    assert dict_tree.keys() == [
            list(range(2)),
            list(range(6)),
        ]
    assert dict_tree.values() == ['one', 'five', ]
    assert len(dict_tree) == 2
    assert dict_tree.indented_string() == """0
  1
    one
    2
      3
        4
          5
            five"""


def _test_add_to_list_or_set(dict_tree: DictTree.DictTree) -> None:
    dict_tree.add(range(2), 'one')
    dict_tree.add(range(2), 'One')
    dict_tree.add(range(2), 'ONE')
    assert 2 == dict_tree.depth()
    dict_tree.add(range(4), 'three')
    dict_tree.add(range(4), 'Three')
    dict_tree.add(range(4), 'THREE')
    assert 4 == dict_tree.depth()
    dict_tree.add(range(6), 'five')
    dict_tree.add(range(6), 'Five')
    dict_tree.add(range(6), 'FIVE')
    assert 6 == dict_tree.depth()
    assert [
            list(range(2)),
            list(range(4)),
            list(range(6)),
        ] == dict_tree.keys()


def test_value_iterable_list_add_values_as_list_and_stringise():
    """TestDictTreeAddList: test_00(): add value as list and stringise."""
    dict_tree = DictTree.DictTree(value_iterable='list')
    _test_add_to_list_or_set(dict_tree)
    assert [
            ['one', 'One', 'ONE'],
            ['three', 'Three', 'THREE'],
            ['five', 'Five', 'FIVE']
        ] == dict_tree.values()
    assert 3 == len(dict_tree)
    assert """0
  1
    ['one', 'One', 'ONE']
    2
      3
        ['three', 'Three', 'THREE']
        4
          5
            ['five', 'Five', 'FIVE']""" == dict_tree.indented_string()


def test_value_iterable_list_add_values_as_list_and_remove():
    """TestDictTreeAddList: test_01(): add value as list then remove it."""
    dict_tree = DictTree.DictTree(value_iterable='list')
    dict_tree.add(range(2), 'one')
    assert range(2) in dict_tree
    assert """0
  1
    ['one']""" == dict_tree.indented_string()
    dict_tree.remove(range(2), 'one')
    assert range(2) in dict_tree
    assert [] == dict_tree.value(range(2))
    assert """0
  1
    []""" == dict_tree.indented_string()


def test_value_iterable_list_add_values_as_list_and_remove_key():
    """TestDictTreeAddList: test_01(): add value as list then remove it."""
    dict_tree = DictTree.DictTree(value_iterable='list')
    dict_tree.add(range(2), 'one')
    # Remove the key completely
    dict_tree.remove(range(2), None)
    assert range(2) not in dict_tree
    assert dict_tree.value(range(2)) is None


def test_value_iterable_list_remove_missing_value_raises():
    """TestDictTreeAddList: test_01(): add value as list then remove missing value raises."""
    dict_tree = DictTree.DictTree(value_iterable='list')
    dict_tree.add(range(2), 'one')
    assert range(2) in dict_tree
    # Try removing something not there
    with pytest.raises(DictTree.ExceptionDictTree) as err:
        dict_tree.remove(range(2), 'two')
    assert err.value.args[0] == 'two not in list [\'one\']'


def test_value_iterable_list_remove_missing_key_overrun_raises():
    """TestDictTreeAddList: test_02(): add value as list then try to remove something else."""
    dict_tree = DictTree.DictTree(value_iterable='list')
    dict_tree.add(range(3), 'three')
    assert range(3) in dict_tree
    # Try removing something with a key overrun
    with pytest.raises(DictTree.ExceptionDictTree) as err:
        dict_tree.remove(range(4), 'four')
    assert err.value.args[0] == 'No key tree: range(3, 4)'


def test_value_iterable_list_remove_key_mismatch_raises():
    dict_tree = DictTree.DictTree(value_iterable='list')
    dict_tree.add(range(3), 'three')
    assert range(3) in dict_tree
    # Try removing something with a key mismatch
    with pytest.raises(DictTree.ExceptionDictTree) as err:
        dict_tree.remove([1, 2, 3, 4], 'one to four')
    assert err.value.args[0] == 'No key: 1'


def test_value_iterable_list_remove_key_underrun_raises():
    dict_tree = DictTree.DictTree(value_iterable='list')
    dict_tree.add(range(3), 'three')
    assert range(3) in dict_tree
    # Try removing something with a key underrun
    with pytest.raises(DictTree.ExceptionDictTree) as err:
        dict_tree.remove(range(2), 'two')
    assert err.value.args[0] == 'Value of key is None'


def test_value_iterable_set_add_values_as_set_and_stringise():
    dict_tree = DictTree.DictTree(value_iterable='set')
    _test_add_to_list_or_set(dict_tree)
    assert [
            {'one', 'One', 'ONE'},
            {'three', 'Three', 'THREE'},
            {'five', 'Five', 'FIVE'}
        ] == dict_tree.values()
    assert 3 == len(dict_tree)


def test_value_iterable_set_add_values_as_list_and_remove():
    """TestDictTreeAddList: test_01(): add value as list then remove it."""
    dict_tree = DictTree.DictTree(value_iterable='set')
    dict_tree.add(range(2), 'one')
    assert range(2) in dict_tree
    assert """0
  1
    {'one'}""" == dict_tree.indented_string()
    dict_tree.remove(range(2), 'one')
    assert range(2) in dict_tree
    assert set() == dict_tree.value(range(2))
    assert """0
  1
    set()""" == dict_tree.indented_string()


def test_value_iterable_set_add_values_as_list_and_remove_key():
    """TestDictTreeAddList: test_01(): add value as list then remove it."""
    dict_tree = DictTree.DictTree(value_iterable='set')
    dict_tree.add(range(2), 'one')
    # Remove the key completely
    dict_tree.remove(range(2), None)
    assert range(2) not in dict_tree
    assert dict_tree.value(range(2)) is None


def test_value_iterable_set_remove_missing_value_raises():
    """TestDictTreeAddList: test_01(): add value as list then remove missing value raises."""
    dict_tree = DictTree.DictTree(value_iterable='set')
    dict_tree.add(range(2), 'one')
    assert range(2) in dict_tree
    # Try removing something not there
    with pytest.raises(DictTree.ExceptionDictTree) as err:
        dict_tree.remove(range(2), 'two')
    assert err.value.args[0] == 'two not in set {\'one\'}'


def test_value_iterable_set_remove_missing_key_overrun_raises():
    """TestDictTreeAddList: test_02(): add value as list then try to remove something else."""
    dict_tree = DictTree.DictTree(value_iterable='set')
    dict_tree.add(range(3), 'three')
    assert range(3) in dict_tree
    # Try removing something with a key overrun
    with pytest.raises(DictTree.ExceptionDictTree) as err:
        dict_tree.remove(range(4), 'four')
    assert err.value.args[0] == 'No key tree: range(3, 4)'


def test_value_iterable_set_remove_key_mismatch_raises():
    dict_tree = DictTree.DictTree(value_iterable='set')
    dict_tree.add(range(3), 'three')
    assert range(3) in dict_tree
    # Try removing something with a key mismatch
    with pytest.raises(DictTree.ExceptionDictTree) as err:
        dict_tree.remove([1, 2, 3, 4], 'one to four')
    assert err.value.args[0] == 'No key: 1'


def test_value_iterable_set_remove_key_underrun_raises():
    dict_tree = DictTree.DictTree(value_iterable='set')
    dict_tree.add(range(3), 'three')
    assert range(3) in dict_tree
    # Try removing something with a key underrun
    with pytest.raises(DictTree.ExceptionDictTree) as err:
        dict_tree.remove(range(2), 'two')
    assert err.value.args[0] == 'Value of key is None'

    
def test_dict_tree_add_bespoke_list():
    """TestDictTreeAddBespokeList: test_00(): add value with bespoke list and stringise."""
    def add_key_value(dict_tree, key, value):
        if dict_tree.value(key) is None:
            dict_tree.add(key, [value, ])
        else:
            dict_tree.value(key).append(value)
            
    dict_tree = DictTree.DictTree()
    add_key_value(dict_tree, range(2), 'one')
    add_key_value(dict_tree, range(2), 'One')
    add_key_value(dict_tree, range(2), 'ONE')
    add_key_value(dict_tree, range(4), 'three')
    add_key_value(dict_tree, range(4), 'Three')
    add_key_value(dict_tree, range(4), 'THREE')
    add_key_value(dict_tree, range(6), 'five')
    add_key_value(dict_tree, range(6), 'Five')
    add_key_value(dict_tree, range(6), 'FIVE')
    assert [
            list(range(2)),
            list(range(4)),
            list(range(6)),
        ] == dict_tree.keys()
    assert [
            ['one', 'One', 'ONE'],
            ['three', 'Three', 'THREE'],
            ['five', 'Five', 'FIVE']
        ] == dict_tree.values()
    assert 3 == len(dict_tree)
    assert """0
  1
    ['one', 'One', 'ONE']
    2
      3
        ['three', 'Three', 'THREE']
        4
          5
            ['five', 'Five', 'FIVE']""" == dict_tree.indented_string()


def test_iadd():
    """TestDictTreeIadd: test_10(): simple +=."""
    dt_1 = DictTree.DictTree()
    dt_1.add(range(2), 'two')
    dt_1.add(range(3), 'three')
    dt_2 = DictTree.DictTree()
    dt_2.add(range(4), 'four')
    dt_2.add(range(5), 'five')
    dt_2 += dt_1
    assert [
            list(range(2)),
            list(range(3)),
            list(range(4)),
            list(range(5)),
        ] == dt_2.keys()
    assert [
            'two',
            'three',
            'four',
            'five',
        ] == dt_2.values()
    assert 4 == len(dt_2)
    assert 'spam' not in dt_2
    assert range(4) in dt_2
    assert 'four' == dt_2.value(range(4))
    assert 5 == dt_2.depth()


def test_iadd_raises_on_type():
    """TestDictTreeIadd: test_10(): simple +=."""
    dict_tree = DictTree.DictTree()
    with pytest.raises(TypeError) as err:
        dict_tree += 1
    assert err.value.args[0] == "unsupported operand type(s) for +=: 'DictTree' and 'int'"


def test_iadd_raises_on_value_iterable():
    """TestDictTreeIadd: test_10(): simple +=."""
    dt_1 = DictTree.DictTree()
    dt_2 = DictTree.DictTree(value_iterable='list')
    with pytest.raises(DictTree.ExceptionDictTree) as err:
        dt_1 += dt_2
    assert err.value.args[0] == 'Can not += mixed values None and list'


class TestDictTreeHtmlTableBase(unittest.TestCase):
    """Tests TestDictTreeHtmlTable row and col span functions."""
    def setUp(self):
        self._dt = DictTree.DictTreeHtmlTable()
        self.assertEqual([], self._dt.keys())
        self.assertEqual([], self._dt.values())
        self.assertEqual(0, len(self._dt))
        self.assertTrue('spam' not in self._dt)
        self.assertFalse('spam' in self._dt)
        
    def tearDown(self):
        pass
    
    def _retHtmlTableString(self, cellContentsIsValue=False):
        """If cellContentsIsValue then the value will be put in the cell if not
        None otherwise the tip of the key list."""
        htmlLineS = []
        # Write: <table border="2" width="100%">
        htmlLineS.append('<table border="2" width="100%">')
        for anEvent in self._dt.gen_row_column_events():
            if anEvent == self._dt.ROW_OPEN:
                # Write out the '<tr>' element
                htmlLineS.append('<tr>')
            elif anEvent == self._dt.ROW_CLOSE:
                # Write out the '</tr>' element
                htmlLineS.append('</tr>')
            else:
                k, v, r, c = anEvent
                # Write '<td rowspan="%d" colspan="%d">%s</td>' % (r, c, txt[-1])
                myL = ['    <td']
                if r > 1:
                    myL.append(' rowspan="%d"' % r)
                if c > 1:
                    myL.append(' colspan="%d"' % c)
                if cellContentsIsValue and v is not None:
                    myL.append('>%s</td>' % v)
                else:
                    myL.append('>%s</td>' % k[-1])
                htmlLineS.append(''.join(myL))
        # Write: </table>
        htmlLineS.append('</table>')
        return '\n'.join(htmlLineS)

class TestDictTreeHtmlTable(TestDictTreeHtmlTableBase):    
    def test_00(self):
        """TestDictTreeHtmlTable: test_00(): row and col span."""
        self._dt.add(('X', 'XX', 'XXX'),    'Value XXX')
        self.assertEqual(3, self._dt.depth())
        self._dt.add(('X', 'XX', 'XXY'),    'Value XXY')
        self.assertEqual(3, self._dt.depth())
        self._dt.add(('X', 'XX', 'XXZ'),    'Value XXZ')
        self._dt.add(('X', 'XY',),          'Value XY')
        self._dt.add(('X', 'XZ', 'XZX'),    'Value XZX')
        self._dt.add(('Y',),                'Value Y')
        self._dt.add(('Z', 'ZX', 'ZXX'),    'Value ZXX')
        self.assertEqual(3, self._dt.depth())
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""X
  XX
    XXX
      Value XXX
    XXY
      Value XXY
    XXZ
      Value XXZ
  XY
    Value XY
  XZ
    XZX
      Value XZX
Y
  Value Y
Z
  ZX
    ZXX
      Value ZXX""",
            self._dt.indented_string()
        )
        expected = """X r=1, c=1
  XX r=1, c=1
    XXX r=1, c=1
    XXY r=1, c=1
    XXZ r=1, c=1
  XY r=1, c=1
  XZ r=1, c=1
    XZX r=1, c=1
Y r=1, c=1
Z r=1, c=1
  ZX r=1, c=1
    ZXX r=1, c=1
"""
        # print('walkRowColSpan():')
        # print(self._dt.walk_row_col_span())
        # print(expected)
        self.assertEqual(expected, self._dt.walk_row_col_span())
        #print 'genRowColEvents()'
        #for anEvent in self._dt.genColRowEvents():
        #    print anEvent
        eventResult = '\n'.join([str(e) for e in self._dt.gen_row_column_events()])
        #print
        #print eventResult
#         self.assertEqual("""(None, 0, 0)
# (['X'], None, 5, 1)
# (['X', 'XX'], None, 3, 1)
# (['X', 'XX', 'XXX'], 'Value XXX', 1, 1)
# (None, -1, -1)
# (None, 0, 0)
# (['X', 'XX', 'XXY'], 'Value XXY', 1, 1)
# (None, -1, -1)
# (None, 0, 0)
# (['X', 'XX', 'XXZ'], 'Value XXZ', 1, 1)
# (None, -1, -1)
# (None, 0, 0)
# (['X', 'XY'], 'Value XY', 1, 2)
# (None, -1, -1)
# (None, 0, 0)
# (['X', 'XZ'], None, 1, 1)
# (['X', 'XZ', 'XZX'], 'Value XZX', 1, 1)
# (None, -1, -1)
# (None, 0, 0)
# (['Y'], 'Value Y', 1, 3)
# (None, -1, -1)
# (None, 0, 0)
# (['Z'], None, 1, 1)
# (['Z', 'ZX'], None, 1, 1)
# (['Z', 'ZX', 'ZXX'], 'Value ZXX', 1, 1)
# (None, -1, -1)""",
#             eventResult,
#         )

    def test_01(self):
        """TestDictTreeHtmlTable: test_01(): row and col span."""
        self._dt.add(('X', 'XX',),    'Value XXX')
        self.assertEqual(2, self._dt.depth())
        self._dt.add(('X', 'XX',),    'Value XXY')
        self.assertEqual(2, self._dt.depth())
        self._dt.add(('X', 'XX',),    'Value XXZ')
        self._dt.add(('X',),          'Value XY')
        self._dt.add(('X', 'XZ',),    'Value XZX')
        self._dt.add(tuple(),             'Value Y')
        self._dt.add(('Z', 'ZX',),    'Value ZXX')
        self.assertEqual(2, self._dt.depth())
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""Value Y
X
  Value XY
  XX
    Value XXZ
  XZ
    Value XZX
Z
  ZX
    Value ZXX""",
                         self._dt.indented_string())
        #print 'walkRowColSpan():'
        #print self._dt.walkColRowSpan()
        #print 'genRowColEvents()'
        #for anEvent in self._dt.genColRowEvents():
        #    print anEvent
        eventResult = '\n'.join([str(e) for e in self._dt.gen_row_column_events()])
        #print
        #print eventResult
#         self.assertEqual("""(None, 0, 0)
# (['X'], 'Value XY', 2, 1)
# (['X', 'XX'], 'Value XXZ', 1, 1)
# (None, -1, -1)
# (None, 0, 0)
# (['X', 'XZ'], 'Value XZX', 1, 1)
# (None, -1, -1)
# (None, 0, 0)
# (['Z'], None, 1, 1)
# (['Z', 'ZX'], 'Value ZXX', 1, 1)
# (None, -1, -1)""",
#             eventResult,
#         )
        #print
        #print self._retHtmlTableString()

    def test_02(self):
        """TestDictTreeHtmlTable: test_02(): row and col span in an HTML table."""
        self._dt.add(('A', 'AA', 'AAA'), None)
        self._dt.add(('A', 'AA', 'AAB'), None)
        self._dt.add(('A', 'AA', 'AAC'), None)
        self._dt.add(('A', 'AB',), None)
        self._dt.add(('A', 'AC', 'ACA'), None)
        self._dt.add(('B',), None)
        self._dt.add(('C', 'CA', 'CAA'), None)
        eventResult = '\n'.join([str(e) for e in self._dt.gen_row_column_events()])
        #print
        #print 'self._dt.indentedStr()'
        #print self._dt.indentedStr()
        #print 'self._dt.walkColRowSpan()'
        #print self._dt.walkColRowSpan()
        #print 'eventResult'
        #print eventResult
        #print 'self._retHtmlTableString()'
        #print self._retHtmlTableString()
        self.assertEqual("""<table border="2" width="100%">
<tr>
    <td rowspan="5">A</td>
    <td rowspan="3">AA</td>
    <td>AAA</td>
</tr>
<tr>
    <td>AAB</td>
</tr>
<tr>
    <td>AAC</td>
</tr>
<tr>
    <td colspan="2">AB</td>
</tr>
<tr>
    <td>AC</td>
    <td>ACA</td>
</tr>
<tr>
    <td colspan="3">B</td>
</tr>
<tr>
    <td>C</td>
    <td>CA</td>
    <td>CAA</td>
</tr>
</table>""",
            self._retHtmlTableString())

class TestDictTreeHtmlTableFile(TestDictTreeHtmlTableBase):
    """Tests TestDictTreeHtmlTable simulating a file/line/column table."""
    def fnSplit(self, f, l=None):
        """Splits a file path. f is expected to have '/' as separator."""
        retVal = ['%s/' % d for d in f.split('/')[:-1]]
        retVal.append(f.split('/')[-1])
        if l is not None:
            retVal.append(l)
        return retVal
        #return f.split('/') + [l,]
        
    def test_00(self):
        """TestDictTreeHtmlTableFile.fnSplit()."""
        self.assertEqual(
            ['spam/', 'eggs.h', 12],
            self.fnSplit('spam/eggs.h', 12),
        )
        self.assertEqual(
            ['eggs.h', 12],
            self.fnSplit('eggs.h', 12),
        )

class TestDictTreeHtmlTableFileLineCol(TestDictTreeHtmlTableFile):
    """Tests TestDictTreeHtmlTable simulating a file/line/column table."""

    def setUp(self):
        self._dt = DictTree.DictTreeHtmlTable('list')
        self.assertEqual([], self._dt.keys())
        self.assertEqual([], self._dt.values())
        self.assertEqual(0, len(self._dt))
        self.assertTrue('spam' not in self._dt)
        self.assertFalse('spam' in self._dt)
        
    def tearDown(self):
        pass
    
    def test_00(self):
        """TestDictTreeHtmlTableFileLineCol: test_00(): Single file/line/column."""
        self._dt.add(('file_one', 12), 24)
        self._dt.add(('file_one', 12), 80)
        self.assertEqual(2, self._dt.depth())
        self.assertEqual([['file_one', 12]], self._dt.keys())
        self.assertEqual(
            [
                [24, 80],
            ],
            self._dt.values(),
            )
        self.assertEqual(1, len(self._dt))
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""file_one
  12
    [24, 80]""",
                         self._dt.indented_string())
        
    def test_01(self):
        """TestDictTreeHtmlTableFileLineCol: test_01(): Multiple file/line/column."""
        # Same line, different column
        self._dt.add(('file_one', 12), 24)
        self._dt.add(('file_one', 12), 80)
        # Different line, different column
        self._dt.add(('file_two', 1), 1)
        self._dt.add(('file_two', 14), 75)
        # Same line, same column
        self._dt.add(('file_three', 15), 10)
        self._dt.add(('file_three', 15), 10)
        # Different line, same column
        self._dt.add(('file_four', 1), 19)
        self._dt.add(('file_four', 14), 19)
        self.assertEqual(2, self._dt.depth())
        self.assertEqual(sorted([
                          ['file_two', 1],
                          ['file_two', 14],
                          ['file_one', 12],
                          ['file_four', 1],
                          ['file_four', 14],
                          ['file_three', 15]
                        ]),
                        sorted(self._dt.keys()))
        self.assertEqual(
            sorted([
                [1],
                [75],
                [24, 80],
                [19], [19],
                [10, 10],
            ]),
            sorted(self._dt.values()),
            )
        self.assertEqual(6, len(self._dt))
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""file_four
  1
    [19]
  14
    [19]
file_one
  12
    [24, 80]
file_three
  15
    [10, 10]
file_two
  1
    [1]
  14
    [75]""",
                         self._dt.indented_string())
        
    def test_02(self):
        """TestDictTreeHtmlTableFileLineCol: test_02(): Single file/line/column with split on path."""
        # Same line, different column
        self._dt.add(self.fnSplit('spam/eggs/chips.h', 12), 24)
        self._dt.add(self.fnSplit('spam/eggs/chips.h', 12), 80)
        self.assertEqual(4, self._dt.depth())
        self.assertEqual([
                          ['spam/', 'eggs/', 'chips.h', 12],
                        ],
                        self._dt.keys())
        self.assertEqual(
            [
                [24, 80],
            ],
            self._dt.values(),
            )
        self.assertEqual(1, len(self._dt))
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""spam/
  eggs/
    chips.h
      12
        [24, 80]""",
                         self._dt.indented_string())
        
    def test_03(self):
        """TestDictTreeHtmlTableFileLineCol: test_03(): Multiple file/line/column with split on path."""
        self._dt.add(self.fnSplit('spam.h', 12), 24)
        self._dt.add(self.fnSplit('spam/eggs.h', 12), 24)
        self._dt.add(self.fnSplit('spam/cheese.h', 12), 24)
        self._dt.add(self.fnSplit('spam/cheese.h', 14), 28)
        self._dt.add(self.fnSplit('spam/eggs/chips.h', 12), 24)
        self._dt.add(self.fnSplit('spam/eggs/chips/beans.h', 12), 24)
        self._dt.add(self.fnSplit('spam/eggs/chips/beans.h', 12), 80)
        #print
        #print self._retHtmlTableString()
        self.assertEqual(5, self._dt.depth())
        #print
        #pprint.pprint(self._dt.keys())
        self.assertEqual(
                    sorted([
                        ['spam/', 'eggs/', 'chips.h', 12],
                        ['spam/', 'eggs/', 'chips/', 'beans.h', 12],
                        ['spam/', 'cheese.h', 12],
                        ['spam/', 'cheese.h', 14],
                        ['spam/', 'eggs.h', 12],
                        ['spam.h', 12],
                    ]),
                    sorted(self._dt.keys()))
        self.assertEqual(
            sorted([
                [24], [24, 80], [24], [28], [24], [24],
            ]),
            sorted(self._dt.values()),
            )
        self.assertEqual(6, len(self._dt))
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""spam.h
  12
    [24]
spam/
  cheese.h
    12
      [24]
    14
      [28]
  eggs.h
    12
      [24]
  eggs/
    chips.h
      12
        [24]
    chips/
      beans.h
        12
          [24, 80]""",
                         self._dt.indented_string())
        #print
        #print self._retHtmlTableString()
        expected = """<table border="2" width="100%">
<tr>
    <td>spam.h</td>
    <td colspan="4">12</td>
</tr>
<tr>
    <td rowspan="5">spam/</td>
    <td rowspan="2">cheese.h</td>
    <td colspan="3">12</td>
</tr>
<tr>
    <td colspan="3">14</td>
</tr>
<tr>
    <td>eggs.h</td>
    <td colspan="3">12</td>
</tr>
<tr>
    <td rowspan="2">eggs/</td>
    <td>chips.h</td>
    <td colspan="2">12</td>
</tr>
<tr>
    <td>chips/</td>
    <td>beans.h</td>
    <td>12</td>
</tr>
</table>"""
        result = self._retHtmlTableString()
        self.assertEqual(expected, result)
        
    def test_04(self):
        """TestDictTreeHtmlTableFileLineCol: test_04(): Multiple file/line/column with split on path."""
        for aLine in """epoc32/include/bldcodeline.hrh 
epoc32/include/bldprivate.hrh 
epoc32/include/bldpublic.hrh 
epoc32/include/bldregional.hrh 
epoc32/include/bldvariant.hrh 
epoc32/include/defaultcaps.hrh 
epoc32/include/e32base.h 
epoc32/include/e32base.inl 
epoc32/include/e32capability.h 
epoc32/include/e32cmn.h 
epoc32/include/e32cmn.inl 
epoc32/include/e32const.h 
epoc32/include/e32def.h 
epoc32/include/e32des16.h 
epoc32/include/e32des8.h 
epoc32/include/e32err.h 
epoc32/include/e32lang.h 
epoc32/include/e32reg.h 
epoc32/include/e32std.h 
epoc32/include/e32std.inl 
epoc32/include/platform/cflog.h 
epoc32/include/privateruntimeids.hrh 
epoc32/include/productvariant.hrh 
epoc32/include/publicruntimeids.hrh 
epoc32/include/variant/Symbian_OS.hrh 
epoc32/include/variant/platform_paths.hrh 
sf/os/networkingsrv/networkcontrol/iptransportlayer/src/ipscprlog.cpp 
sf/os/networkingsrv/networkcontrol/iptransportlayer/src/ipscprlog.h""".split('\n'):
            self._dt.add(self.fnSplit(aLine), None)
        #print
        #print self._retHtmlTableString()
        self.assertEqual("""<table border="2" width="100%">
<tr>
    <td rowspan="26">epoc32/</td>
    <td rowspan="26">include/</td>
    <td colspan="5">bldcodeline.hrh </td>
</tr>
<tr>
    <td colspan="5">bldprivate.hrh </td>
</tr>
<tr>
    <td colspan="5">bldpublic.hrh </td>
</tr>
<tr>
    <td colspan="5">bldregional.hrh </td>
</tr>
<tr>
    <td colspan="5">bldvariant.hrh </td>
</tr>
<tr>
    <td colspan="5">defaultcaps.hrh </td>
</tr>
<tr>
    <td colspan="5">e32base.h </td>
</tr>
<tr>
    <td colspan="5">e32base.inl </td>
</tr>
<tr>
    <td colspan="5">e32capability.h </td>
</tr>
<tr>
    <td colspan="5">e32cmn.h </td>
</tr>
<tr>
    <td colspan="5">e32cmn.inl </td>
</tr>
<tr>
    <td colspan="5">e32const.h </td>
</tr>
<tr>
    <td colspan="5">e32def.h </td>
</tr>
<tr>
    <td colspan="5">e32des16.h </td>
</tr>
<tr>
    <td colspan="5">e32des8.h </td>
</tr>
<tr>
    <td colspan="5">e32err.h </td>
</tr>
<tr>
    <td colspan="5">e32lang.h </td>
</tr>
<tr>
    <td colspan="5">e32reg.h </td>
</tr>
<tr>
    <td colspan="5">e32std.h </td>
</tr>
<tr>
    <td colspan="5">e32std.inl </td>
</tr>
<tr>
    <td>platform/</td>
    <td colspan="4">cflog.h </td>
</tr>
<tr>
    <td colspan="5">privateruntimeids.hrh </td>
</tr>
<tr>
    <td colspan="5">productvariant.hrh </td>
</tr>
<tr>
    <td colspan="5">publicruntimeids.hrh </td>
</tr>
<tr>
    <td rowspan="2">variant/</td>
    <td colspan="4">Symbian_OS.hrh </td>
</tr>
<tr>
    <td colspan="4">platform_paths.hrh </td>
</tr>
<tr>
    <td rowspan="2">sf/</td>
    <td rowspan="2">os/</td>
    <td rowspan="2">networkingsrv/</td>
    <td rowspan="2">networkcontrol/</td>
    <td rowspan="2">iptransportlayer/</td>
    <td rowspan="2">src/</td>
    <td>ipscprlog.cpp </td>
</tr>
<tr>
    <td>ipscprlog.h</td>
</tr>
</table>""",
            self._retHtmlTableString())

class TestDictTreeHtmlTableFileTree(TestDictTreeHtmlTableFile):
    """Tests TestDictTreeHtmlTableFileTree simulating a directory structure."""

    def setUp(self):
        self._dt = DictTree.DictTreeHtmlTable(None)
        self.assertEqual([], self._dt.keys())
        self.assertEqual([], self._dt.values())
        self.assertEqual(0, len(self._dt))
        self.assertTrue('spam' not in self._dt)
        self.assertFalse('spam' in self._dt)
        
    def tearDown(self):
        pass
    
    def test_01(self):
        """TestDictTreeHtmlTableFileTree: test_01(): Multiple file/line/column with split on path and links."""
        for aLine in """epoc32/include/bldcodeline.hrh 
epoc32/include/bldprivate.hrh 
epoc32/include/bldpublic.hrh 
epoc32/include/bldregional.hrh 
epoc32/include/bldvariant.hrh 
epoc32/include/defaultcaps.hrh 
epoc32/include/e32base.h 
epoc32/include/e32base.inl 
epoc32/include/e32capability.h 
epoc32/include/e32cmn.h 
epoc32/include/e32cmn.inl 
epoc32/include/e32const.h 
epoc32/include/e32def.h 
epoc32/include/e32des16.h 
epoc32/include/e32des8.h 
epoc32/include/e32err.h 
epoc32/include/e32lang.h 
epoc32/include/e32reg.h 
epoc32/include/e32std.h 
epoc32/include/e32std.inl 
epoc32/include/platform/cflog.h 
epoc32/include/privateruntimeids.hrh 
epoc32/include/productvariant.hrh 
epoc32/include/publicruntimeids.hrh 
epoc32/include/variant/Symbian_OS.hrh 
epoc32/include/variant/platform_paths.hrh 
sf/os/networkingsrv/networkcontrol/iptransportlayer/src/ipscprlog.cpp 
sf/os/networkingsrv/networkcontrol/iptransportlayer/src/ipscprlog.h""".split('\n'):
            aLine = aLine.strip()
            self._dt.add(self.fnSplit(aLine), '<a href="%s">%s</a>' \
                         % (aLine, os.path.basename(aLine)))#aLine.replace('/', '\\'))))
#        eventResult = '\n'.join([str(e) for e in self._dt.genColRowEvents()])
#        print()
#        print(self._dt.indentedStr())
        self.maxDiff = None
        self.assertEqual("""epoc32/
  include/
    bldcodeline.hrh
      <a href="epoc32/include/bldcodeline.hrh">bldcodeline.hrh</a>
    bldprivate.hrh
      <a href="epoc32/include/bldprivate.hrh">bldprivate.hrh</a>
    bldpublic.hrh
      <a href="epoc32/include/bldpublic.hrh">bldpublic.hrh</a>
    bldregional.hrh
      <a href="epoc32/include/bldregional.hrh">bldregional.hrh</a>
    bldvariant.hrh
      <a href="epoc32/include/bldvariant.hrh">bldvariant.hrh</a>
    defaultcaps.hrh
      <a href="epoc32/include/defaultcaps.hrh">defaultcaps.hrh</a>
    e32base.h
      <a href="epoc32/include/e32base.h">e32base.h</a>
    e32base.inl
      <a href="epoc32/include/e32base.inl">e32base.inl</a>
    e32capability.h
      <a href="epoc32/include/e32capability.h">e32capability.h</a>
    e32cmn.h
      <a href="epoc32/include/e32cmn.h">e32cmn.h</a>
    e32cmn.inl
      <a href="epoc32/include/e32cmn.inl">e32cmn.inl</a>
    e32const.h
      <a href="epoc32/include/e32const.h">e32const.h</a>
    e32def.h
      <a href="epoc32/include/e32def.h">e32def.h</a>
    e32des16.h
      <a href="epoc32/include/e32des16.h">e32des16.h</a>
    e32des8.h
      <a href="epoc32/include/e32des8.h">e32des8.h</a>
    e32err.h
      <a href="epoc32/include/e32err.h">e32err.h</a>
    e32lang.h
      <a href="epoc32/include/e32lang.h">e32lang.h</a>
    e32reg.h
      <a href="epoc32/include/e32reg.h">e32reg.h</a>
    e32std.h
      <a href="epoc32/include/e32std.h">e32std.h</a>
    e32std.inl
      <a href="epoc32/include/e32std.inl">e32std.inl</a>
    platform/
      cflog.h
        <a href="epoc32/include/platform/cflog.h">cflog.h</a>
    privateruntimeids.hrh
      <a href="epoc32/include/privateruntimeids.hrh">privateruntimeids.hrh</a>
    productvariant.hrh
      <a href="epoc32/include/productvariant.hrh">productvariant.hrh</a>
    publicruntimeids.hrh
      <a href="epoc32/include/publicruntimeids.hrh">publicruntimeids.hrh</a>
    variant/
      Symbian_OS.hrh
        <a href="epoc32/include/variant/Symbian_OS.hrh">Symbian_OS.hrh</a>
      platform_paths.hrh
        <a href="epoc32/include/variant/platform_paths.hrh">platform_paths.hrh</a>
sf/
  os/
    networkingsrv/
      networkcontrol/
        iptransportlayer/
          src/
            ipscprlog.cpp
              <a href="sf/os/networkingsrv/networkcontrol/iptransportlayer/src/ipscprlog.cpp">ipscprlog.cpp</a>
            ipscprlog.h
              <a href="sf/os/networkingsrv/networkcontrol/iptransportlayer/src/ipscprlog.h">ipscprlog.h</a>""",
                         self._dt.indented_string())
        #print
        #print eventResult
        #print
        #print self._retHtmlTableString()
        #print
        #print self._retHtmlTableString(cellContentsIsValue=True)
        self.assertEqual("""<table border="2" width="100%">
<tr>
    <td rowspan="26">epoc32/</td>
    <td rowspan="26">include/</td>
    <td colspan="5"><a href="epoc32/include/bldcodeline.hrh">bldcodeline.hrh</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/bldprivate.hrh">bldprivate.hrh</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/bldpublic.hrh">bldpublic.hrh</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/bldregional.hrh">bldregional.hrh</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/bldvariant.hrh">bldvariant.hrh</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/defaultcaps.hrh">defaultcaps.hrh</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32base.h">e32base.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32base.inl">e32base.inl</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32capability.h">e32capability.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32cmn.h">e32cmn.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32cmn.inl">e32cmn.inl</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32const.h">e32const.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32def.h">e32def.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32des16.h">e32des16.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32des8.h">e32des8.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32err.h">e32err.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32lang.h">e32lang.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32reg.h">e32reg.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32std.h">e32std.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32std.inl">e32std.inl</a></td>
</tr>
<tr>
    <td>platform/</td>
    <td colspan="4"><a href="epoc32/include/platform/cflog.h">cflog.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/privateruntimeids.hrh">privateruntimeids.hrh</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/productvariant.hrh">productvariant.hrh</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/publicruntimeids.hrh">publicruntimeids.hrh</a></td>
</tr>
<tr>
    <td rowspan="2">variant/</td>
    <td colspan="4"><a href="epoc32/include/variant/Symbian_OS.hrh">Symbian_OS.hrh</a></td>
</tr>
<tr>
    <td colspan="4"><a href="epoc32/include/variant/platform_paths.hrh">platform_paths.hrh</a></td>
</tr>
<tr>
    <td rowspan="2">sf/</td>
    <td rowspan="2">os/</td>
    <td rowspan="2">networkingsrv/</td>
    <td rowspan="2">networkcontrol/</td>
    <td rowspan="2">iptransportlayer/</td>
    <td rowspan="2">src/</td>
    <td><a href="sf/os/networkingsrv/networkcontrol/iptransportlayer/src/ipscprlog.cpp">ipscprlog.cpp</a></td>
</tr>
<tr>
    <td><a href="sf/os/networkingsrv/networkcontrol/iptransportlayer/src/ipscprlog.h">ipscprlog.h</a></td>
</tr>
</table>""",
            self._retHtmlTableString(cellContentsIsValue=True))


def _create_simple_file_system():
    # dict_tree = DictTree.DictTreeHtmlTable('list')
    dict_tree = DictTree.DictTreeHtmlTable()
    for file_path, columns in zip(
        (
            'spam.h',
            'spam/eggs.h',
            'spam/cheese.h',
            'spam/eggs/chips.h',
            'spam/eggs/chips/beans.h',
        ),
        (
            ('A', 'B'),
            ('C', 'D'),
            ('E', 'F'),
            ('G', 'H'),
            ('I', 'J'),
        )
    ):
        dict_tree.add(file_path.split('/'), columns)
    return dict_tree


def test_simple_file_system():
    dict_tree = _create_simple_file_system()
    assert dict_tree.depth() == 4
    # print(sorted(dict_tree.keys()))
    assert sorted(dict_tree.keys()) == [
        ['spam', 'cheese.h'],
        ['spam', 'eggs', 'chips', 'beans.h'],
        ['spam', 'eggs', 'chips.h'],
        ['spam', 'eggs.h'],
        ['spam.h'],
    ]
    assert sorted(dict_tree.values()) == [
        ('A', 'B'),
        ('C', 'D'),
        ('E', 'F'),
        ('G', 'H'),
        ('I', 'J'),
    ]

    assert len(dict_tree) == 5


def test_simple_file_system_walk():
    dict_tree = _create_simple_file_system()
    # print()
    events = []
    for event in dict_tree.gen_row_column_events():
        # print(repr(event), str(event))
        # print(str(event))
        if dict_tree.is_row_open(event):
            events.append('ROW_OPEN')
        elif dict_tree.is_row_close(event):
            events.append('ROW_CLOSE')
        else:
            events.append(str(event))
    # print(events)
    assert events == [
        'ROW_OPEN',
        "DictTreeTableEvent(branch=['spam'], node=None, row_span=4, col_span=1)",
        "DictTreeTableEvent(branch=['spam', 'cheese.h'], node=('E', 'F'), row_span=1, col_span=3)",
        'ROW_CLOSE',
        'ROW_OPEN',
        "DictTreeTableEvent(branch=['spam', 'eggs'], node=None, row_span=2, col_span=1)",
        "DictTreeTableEvent(branch=['spam', 'eggs', 'chips'], node=None, row_span=1, col_span=1)",
        "DictTreeTableEvent(branch=['spam', 'eggs', 'chips', 'beans.h'], node=('I', 'J'), row_span=1, col_span=1)",
        'ROW_CLOSE',
        'ROW_OPEN',
        "DictTreeTableEvent(branch=['spam', 'eggs', 'chips.h'], node=('G', 'H'), row_span=1, col_span=2)",
        'ROW_CLOSE',
        'ROW_OPEN',
        "DictTreeTableEvent(branch=['spam', 'eggs.h'], node=('C', 'D'), row_span=1, col_span=3)",
        'ROW_CLOSE',
        'ROW_OPEN',
        "DictTreeTableEvent(branch=['spam.h'], node=('A', 'B'), row_span=1, col_span=4)",
        'ROW_CLOSE',
    ]


@pytest.mark.parametrize(
    'branch, expected',
    (
        ([], 4),
        (['spam',], 3),
        (['spam', 'eggs'], 2),
        (['spam', 'eggs', 'chips'], 1),
    )
)
def test_simple_file_system_depth_from_branch(branch, expected):
    dict_tree = _create_simple_file_system()
    assert dict_tree.depth_from_branch(branch) == expected


@pytest.mark.parametrize(
    'branch, expected',
    (
        ([], [
            'ROW_OPEN',
            "DictTreeTableEvent(branch=['spam'], node=None, row_span=4, col_span=1)",
            "DictTreeTableEvent(branch=['spam', 'cheese.h'], node=('E', 'F'), row_span=1, col_span=3)",
            'ROW_CLOSE',
            'ROW_OPEN',
            "DictTreeTableEvent(branch=['spam', 'eggs'], node=None, row_span=2, col_span=1)",
            "DictTreeTableEvent(branch=['spam', 'eggs', 'chips'], node=None, row_span=1, col_span=1)",
            "DictTreeTableEvent(branch=['spam', 'eggs', 'chips', 'beans.h'], node=('I', 'J'), row_span=1, col_span=1)",
            'ROW_CLOSE',
            'ROW_OPEN',
            "DictTreeTableEvent(branch=['spam', 'eggs', 'chips.h'], node=('G', 'H'), row_span=1, col_span=2)",
            'ROW_CLOSE',
            'ROW_OPEN',
            "DictTreeTableEvent(branch=['spam', 'eggs.h'], node=('C', 'D'), row_span=1, col_span=3)",
            'ROW_CLOSE',
            'ROW_OPEN',
            "DictTreeTableEvent(branch=['spam.h'], node=('A', 'B'), row_span=1, col_span=4)",
            'ROW_CLOSE',
        ]),
        (['spam', ],
         [
             'ROW_OPEN',
             "DictTreeTableEvent(branch=['cheese.h'], node=('E', 'F'), row_span=1, col_span=3)",
             'ROW_CLOSE',
             'ROW_OPEN',
             "DictTreeTableEvent(branch=['eggs'], node=None, row_span=2, col_span=1)",
             "DictTreeTableEvent(branch=['eggs', 'chips'], node=None, row_span=1, col_span=1)",
             "DictTreeTableEvent(branch=['eggs', 'chips', 'beans.h'], node=('I', 'J'), row_span=1, col_span=1)",
             'ROW_CLOSE',
             'ROW_OPEN',
             "DictTreeTableEvent(branch=['eggs', 'chips.h'], node=('G', 'H'), row_span=1, col_span=2)",
             'ROW_CLOSE',
             'ROW_OPEN',
             "DictTreeTableEvent(branch=['eggs.h'], node=('C', 'D'), row_span=1, col_span=3)",
             'ROW_CLOSE'
         ]),
        (['spam', 'eggs', ],
         [
             'ROW_OPEN',
             "DictTreeTableEvent(branch=['chips'], node=None, row_span=1, col_span=1)",
             "DictTreeTableEvent(branch=['chips', 'beans.h'], node=('I', 'J'), row_span=1, col_span=1)",
             'ROW_CLOSE',
             'ROW_OPEN',
             "DictTreeTableEvent(branch=['chips.h'], node=('G', 'H'), row_span=1, col_span=2)",
             'ROW_CLOSE']
         ),
        (['spam', 'eggs', 'chips', ], [
            'ROW_OPEN',
            "DictTreeTableEvent(branch=['beans.h'], node=('I', 'J'), row_span=1, col_span=1)",
            'ROW_CLOSE'
        ]),
    )
)
def test_simple_file_system_intermediate_walk(branch, expected):
    dict_tree = _create_simple_file_system()
    events = []
    for event in dict_tree.gen_row_column_events_from_branch(branch):
        # print(event)
        if dict_tree.is_row_open(event):
            events.append('ROW_OPEN')
        elif dict_tree.is_row_close(event):
            events.append('ROW_CLOSE')
        else:
            events.append(str(event))
    # print(events)
    assert events == expected
