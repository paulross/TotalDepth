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
"""A dictionary that takes a list of hashables as a key and behaves like a tree."""
import typing

from TotalDepth.LIS import ExceptionTotalDepthLIS

__author__ = 'Paul Ross'
__date__ = '2009-09-15'
__version__ = '0.8.0'
__rights__ = 'Copyright (c) Paul Ross'


class ExceptionDictTree(ExceptionTotalDepthLIS):
    """Exception when handling a DictTree object."""
    pass


class ExceptionDictTreeHtmlTable(ExceptionDictTree):
    """Exception when handling a DictTreeHtmlTable object."""
    pass


class DictTree:
    """A dictionary that takes a list of hashables as a key and behaves like a tree.
    A node can have multiple values represented as a set or list."""
    INDENT_STR = '  '
    ITERABLE_TYPES = (None, 'list', 'set')
    # HTML table events
    ROW_OPEN = (None, 0, 0)
    ROW_CLOSE = (None, -1, -1)

    def __init__(self, value_iterable=None):
        if value_iterable not in self.ITERABLE_TYPES:
            raise ExceptionDictTree('"%s" not in acceptable range: %s' % (value_iterable, self.ITERABLE_TYPES))
        # non-None if the value is iterable.
        self.value_iterable = value_iterable
        # A dictionary of hashable to a node
        self.internal_tree: typing.Optional[typing.Dict[typing.Hashable, typing.Union[DictTree, DictTreeHtmlTable]]] = None
        # Node 'value' can be anything
        self.internal_value: typing.Any = None

    def __iadd__(self, other):
        if issubclass(other.__class__, self.__class__):
            if self.value_iterable != other.value_iterable:
                raise ExceptionDictTree(
                    f'Can not += mixed values {self.value_iterable} and {other.value_iterable}'
                )
            for k in other.keys():
                self.add(k, other.value(k))
            return self
        return NotImplemented

    def new_instance(self):
        return DictTree(value_iterable=self.value_iterable)

    def add(self, key: typing.Sequence[typing.Hashable], value: typing.Any) -> None:
        """Add a key/value. k is a list of hashables."""
        if self.value_iterable not in self.ITERABLE_TYPES:
            raise ExceptionDictTree(f'"{self.value_iterable}" not in acceptable range: {self.ITERABLE_TYPES}')
        if len(key) == 0:
            if self.value_iterable is None:
                self.internal_value = value
            elif self.value_iterable == 'list':
                if self.internal_value is None:
                    self.internal_value = [value]
                else:
                    self.internal_value.append(value)
            elif self.value_iterable == 'set':
                if self.internal_value is None:
                    self.internal_value = set()
                self.internal_value.add(value)
        else:
            if self.internal_tree is None:
                self.internal_tree = {}
            if key[0] not in self.internal_tree:
                self.internal_tree[key[0]] = self.new_instance()
            self.internal_tree[key[0]].add(key[1:], value)
            
    def remove(self, key: typing.Sequence[typing.Hashable], value: typing.Any = None) -> None:
        """Remove a key/value."""
        assert(self.value_iterable in self.ITERABLE_TYPES)
        if len(key) == 0:
            if self.value_iterable is None:
                self.internal_value = None
            elif self.value_iterable == 'list':
                if value is None:
                    self.internal_value = None
                else:
                    if self.internal_value is not None:
                        try:
                            self.internal_value.remove(value)
                        except ValueError:
                            raise ExceptionDictTree('%s not in list %s' % (value, self.internal_value))
                    else:
                        raise ExceptionDictTree('Value of key is None')
            elif self.value_iterable == 'set':
                if value is None:
                    self.internal_value = None
                else:
                    if self.internal_value is not None:
                        try:
                            self.internal_value.remove(value)
                        except KeyError:
                            raise ExceptionDictTree('%s not in set %s' % (value, self.internal_value))
                    else:
                        raise ExceptionDictTree('Value of key is None')
        elif self.internal_tree is not None:
            if key[0] in self.internal_tree:
                self.internal_tree[key[0]].remove(key[1:], value)
            else:
                raise ExceptionDictTree(f'No key: {key[0]}')
        else:
            raise ExceptionDictTree(f'No key tree: {key}')

    def value(self, key: typing.Sequence[typing.Hashable]) -> typing.Optional[typing.Any]:
        """Value corresponding to a key or None. k is a list of hashables."""
        if len(key) == 0:
            return self.internal_value
        if self.internal_tree is None:
            return None
        try:
            return self.internal_tree[key[0]].value(key[1:])
        except KeyError:
            pass
        return None
    
    def __contains__(self, key: typing.Sequence[typing.Hashable]) -> bool:
        return self.value(key) is not None

    def values(self) -> typing.List[typing.Any]:
        """Returns a list of all values."""
        ret = []
        self._values(ret)
        return ret
    
    def _values(self, value_list) -> None:
        """Finds values recursively."""
        if self.internal_value is not None:
            value_list.append(self.internal_value)
        if self.internal_tree is not None:
            for k in self.internal_tree.keys():
                self.internal_tree[k]._values(value_list)
                
    def keys(self) -> typing.List[typing.Hashable]:
        """Return a list of keys where each key is a list of hashables."""
        ret_keys: typing.List[typing.Hashable] = []
        key_stack: typing.List[typing.Hashable] = []
        self._keys(ret_keys, key_stack)
        assert(len(key_stack) == 0)
        return ret_keys
    
    def _keys(self, key_list: typing.Sequence[typing.Hashable], key_stack: typing.Sequence[typing.Hashable]) -> None:
        """Recursive method to get all keys."""
        if self.internal_value is not None:
            key_list.append(key_stack[:])
        if self.internal_tree is not None:
            for key in self.internal_tree.keys():
                key_stack.append(key)
                self.internal_tree[key]._keys(key_list, key_stack)
                key_stack.pop()

    def items(self) -> typing.Sequence[typing.Tuple[typing.Sequence[typing.Hashable], typing.Any]]:
        """Yields a sequence of key, value pairs."""
        key_stack: typing.List[typing.Hashable] = []
        yield from self._items(key_stack)
        assert(len(key_stack) == 0)

    def _items(self, key_stack: typing.Sequence[typing.Hashable]) \
            -> typing.Sequence[typing.Tuple[typing.List[typing.Hashable], typing.Any]]:
        """Recursively yields a sequence of key, value pairs."""
        if self.internal_tree is not None:
            for key in self.internal_tree.keys():
                key_stack.append(key)
                value = self.internal_tree[key].internal_value
                if value is not None:
                    yield key_stack[:], value
                yield from self.internal_tree[key]._items(key_stack)
                key_stack.pop()

    def __len__(self) -> int:
        """Returns the number of keys."""
        return len(self.keys())

    def depth(self) -> int:
        """Returns the maximum tree depth as an integer."""
        return self._depth(0)

    def _depth(self, depth_given: int) -> int:
        """Recursively returns the maximum tree depth as an integer."""
        depth_local = depth_given
        if self.internal_tree is not None:
            for k in self.internal_tree.keys():
                depth_local = max(depth_local, self.internal_tree[k]._depth(depth_given + 1))
        return depth_local

    def indented_string(self) -> str:
        """Returns an indented string."""
        ret_list: typing.List[str] = []
        key_stack: typing.List[typing.Hashable] = []
        self._indented_string(ret_list, key_stack)
        assert(len(key_stack) == 0)
        return '\n'.join(ret_list)
        
    def _indented_string(self, return_list: typing.List[str], key_stack: typing.Sequence[typing.Hashable]) -> None:
        """Recursively accumulate an indented string."""
        if self.internal_value is not None:
            return_list.append('%s%s' % (self.INDENT_STR * len(key_stack), self.internal_value))
        if self.internal_tree is not None:
            for key in sorted(self.internal_tree.keys()):
                return_list.append('%s%s' % (self.INDENT_STR * len(key_stack), key))
                key_stack.append(key)
                self.internal_tree[key]._indented_string(return_list, key_stack)
                key_stack.pop()
                

class DictTreeTableEvent(typing.NamedTuple):
    """POD class that contains the data needed for a HTML table entry.
    branch - the data route to this node.
    node - the columns of the table entry.
    row_span - the HTML rowspan attribute for the <td>.
    col_span - the HTML colspan attribute for the <td>.
    """
    branch: typing.List[typing.Any]
    node: typing.Any
    row_span: int
    col_span: int

    def html_attrs(self) -> typing.Dict[str, str]:
        return {
            'rowspan': f'{self.row_span}',
            'colspan': f'{self.col_span}'
        }


class DictTreeHtmlTable(DictTree):
    """A sub-class of DictTree that helps writing HTML row/col span tables
    Suppose we have a tree like this::

                                |- AAA
                                |
                        |- AA --|- AAB
                        |       |
                        |       |- AAC
                |- A ---|
        Root ---|       |- AB
                |       |
                |       |- AC ---- ACA
                |
                |- B
                |
                |- C ---- CA ---- CAA

    And we want to represent the tree like this when laid out as
    an HTML table::
    
        |-----------------------|
        | A     | AA    | AAA   |
        |       |       |-------|
        |       |       | AAB   |
        |       |       |-------|
        |       |       | AAC   |
        |       |---------------|
        |       | AB            |
        |       |---------------|
        |       | AC    | ACA   |
        |-----------------------|
        | B                     |
        |-----------------------|
        | C     | CA    | CAA   |
        |-----------------------|

    In this example the tree is loaded branch by branch thus::

        myTree = DictTreeHtmlTable()
        myTree.add(('A', 'AA', 'AAA'), None)
        myTree.add(('A', 'AA', 'AAB'), None)
        myTree.add(('A', 'AA', 'AAC'), None)
        myTree.add(('A', 'AB',), None)
        myTree.add(('A', 'AC', 'ACA'), None)
        myTree.add(('B',), None)
        myTree.add(('C', 'CA', 'CAA'), None)

    The HTML code generator can be used like this::
    
        # Write: <table border="2" width="100%">
        with XmlWrite.Element(xhtml_stream, 'table', {}):
            for event in myTree.genColRowEvents():
                if event == myTree.ROW_OPEN:
                    # Write out the '<tr>' element
                    xhtml_stream.startElement('tr', {})
                elif event == myTree.ROW_CLOSE:
                    # Write out the '</tr>' element
                    xhtml_stream.endElement('tr')
                else:
                    # Write '<td rowspan="..." colspan="...">...</td>' % (r, c, v)
                    with XmlWrite.Element(xhtml_stream, 'td', event.html_attrs()):
                        xhtml_stream.characters(str(event.node))
        # Write: </table>
    
    And the HTML will look like this::
    
        <table border="2" width="100%">
            <tr valign="top">
                <td rowspan="5">A</td>
                <td rowspan="3">AA</td>
                <td>AAA</td>
            </tr>
            <tr valign="top">
                <td>AAB</td>
            </tr>
            <tr valign="top">
                <td>AAC</td>
            </tr>
            <tr valign="top">
                <td colspan="2">AB</td>
            </tr>
            <tr valign="top">
                <td>AC</td>
                <td>ACA</td>
            </tr>
            <tr valign="top">
                <td colspan="3">B</td>
            </tr>
            <tr valign="top">
                <td>C</td>
                <td>CA</td>
                <td>CAA</td>
            </tr>
        </table>
    """
    #: HTML table event: open row with <tr ...>
    ROW_OPEN = DictTreeTableEvent([], None, 0, 0)
    #: HTML table event: close row with </tr>
    ROW_CLOSE = DictTreeTableEvent([], None, -1, -1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.column_span = self.row_span = 1
        self._has_valid_row_col_span = False

    def is_row_open(self, event: DictTreeTableEvent) -> bool:
        """Return True if the event I have generated is a ROW_OPEN event."""
        return event == self.ROW_OPEN

    def is_row_close(self, event: DictTreeTableEvent) -> bool:
        """Return True if the event I have generated is a ROW_CLOSE event."""
        return event == self.ROW_CLOSE

    # Overload mutating methods
    def add(self, key: typing.Sequence[typing.Hashable], value: typing.Any) -> None:
        """Add a key/value."""
        self._has_valid_row_col_span = False
        return super().add(key, value)

    def remove(self, key: typing.Sequence[typing.Hashable], value: typing.Any = None):
        """Remove a key/value."""
        self._has_valid_row_col_span = False
        return super().remove(key, value)

    def new_instance(self):
        return DictTreeHtmlTable(self.value_iterable)

    def set_row_column_span(self) -> None:
        """Top level call that sets colspan and rowspan attributes."""
        if not self._has_valid_row_col_span:
            self._set_row_span()
            max_depth = self.depth()
            self._set_column_span(max_depth, -1)
            self._has_valid_row_col_span = True

    def _set_column_span(self, max_depth: int, depth: int) -> None:
        """Traverses the tree setting the columns span."""
        if self.internal_tree is None:
            # Leaf node
            self.column_span = max_depth - depth
        else:
            # Non-leaf
            self.column_span = 1
            for tree in self.internal_tree.values():
                tree._set_column_span(max_depth, depth + 1)
                tree._has_valid_row_col_span = True
    
    def _set_row_span(self) -> int:
        """Sets self.row_span recursively."""
        if self.internal_tree is None:
            self.row_span = 1
        else:
            # Non-leaf node
            self.row_span = 0
            for tree in self.internal_tree.values():
                self.row_span += tree._set_row_span()
        return self.row_span

    def gen_row_column_events(self) -> typing.Sequence[DictTreeTableEvent]:
        """Returns a set of events that are quadruples.
        (key_branch, value, rowspan_int, colspan_int)
        The branch is a list of keys the from the branch of the tree.
        The rowspan and colspan are both integers.
        At the start of the a <tr> there will be a ROW_OPEN
        and at row end (</tr> a ROW_CLOSE will be yielded
        """
        self.set_row_column_span()
        has_yielded = False
        for anEvent in self._gen_row_column_events([]):
            if not has_yielded:
                yield self.ROW_OPEN
                has_yielded = True
            yield anEvent
        if has_yielded:
            yield self.ROW_CLOSE

    def _gen_row_column_events(self, key_branch: typing.Sequence[typing.Hashable]) \
            -> typing.Sequence[DictTreeTableEvent]:
        """Recursively yields a set of events that are a tuple of quadruples.
        (key_branch, value, rowspan_integer, colspan_integer)
        For example: (['a', 'b'], 'c', 3, 7)
        At the start of the a <tr> there will be a ROW_OPEN
        and at row end (</tr>) a ROW_CLOSE will be yielded
        """
        # set_column_row_span() is a NOP if the internal data has not changed.
        self.set_row_column_span()
        if self.internal_tree is not None:
            # Non-leaf
            keys = sorted(self.internal_tree.keys())
            for i, k in enumerate(keys):
                key_branch.append(k)
                if i != 0:
                    yield self.ROW_CLOSE
                    yield self.ROW_OPEN
                yield DictTreeTableEvent(key_branch[:], self.internal_tree[k].internal_value,
                                         self.internal_tree[k].row_span, self.internal_tree[k].column_span)
                # Recurse
                for anEvent in self.internal_tree[k]._gen_row_column_events(key_branch):
                    yield anEvent
                key_branch.pop()

    def gen_row_column_events_from_branch(self, key_branch: typing.List[typing.Hashable]) \
            -> typing.Sequence[DictTreeTableEvent]:
        """Yields a set of events that are a tuple of quadruples.
        (key_branch, value, rowspan_integer, colspan_integer)
        For example: (['a', 'b'], 'c', 3, 7)
        At the start of the a <tr> there will be a ROW_OPEN
        and at row end (</tr>) a ROW_CLOSE will be yielded
        """
        # print('TRACE: XX key_branch', key_branch)
        # Find the sub-tree from the key_branch
        sub_tree = self
        for key in key_branch:
            # print('TRACE: XX sub_tree.internal_tree', sub_tree.internal_tree.keys())
            sub_tree = sub_tree.internal_tree[key]
        # yield the events from the sub-tree.
        has_yielded = False
        for event in sub_tree._gen_row_column_events_from_branch([]):
            if not has_yielded:
                yield self.ROW_OPEN
                has_yielded = True
            yield event
        if has_yielded:
            yield self.ROW_CLOSE

    def _gen_row_column_events_from_branch(self, key_branch: typing.List[typing.Hashable]) \
            -> typing.Sequence[DictTreeTableEvent]:
        # set_column_row_span() is a NOP if the internal data has not changed.
        self.set_row_column_span()
        if self.internal_tree is not None:
            # Non-leaf
            keys = sorted(self.internal_tree.keys())
            for i, key in enumerate(keys):
                key_branch.append(key)
                if i != 0:
                    yield self.ROW_CLOSE
                    yield self.ROW_OPEN
                event = DictTreeTableEvent(
                    key_branch,
                    self.internal_tree[key].internal_value,
                    self.internal_tree[key].row_span,
                    self.internal_tree[key].column_span,
                )
                yield event
                # Recurse
                sub_tree = self.internal_tree[key]
                yield from sub_tree._gen_row_column_events_from_branch(key_branch)
                key_branch.pop()

    def depth_from_branch(self, key_branch: typing.Sequence[typing.Hashable]) -> int:
        """Finds the remainder of depth from the branch."""
        # Find the sub-tree from the key_branch
        sub_tree = self
        for key in key_branch:
            sub_tree = sub_tree.internal_tree[key]
        return sub_tree.depth()

    def walk_row_col_span(self) -> str:
        """Return the internal tree as a string."""
        max_depth = self.depth()
        return self._walk_row_column_span(0, max_depth)

    def _walk_row_column_span(self, depth: int, max_depth: int) -> str:
        ret_list = []
        if self.internal_tree is not None:
            for k in sorted(self.internal_tree.keys()):
                ret_list.append(
                    '%s%s r=%d, c=%d\n' % (
                        '  ' * depth, k, self.internal_tree[k].row_span, self.internal_tree[k].column_span
                    )
                )
                ret_list.append(self.internal_tree[k]._walk_row_column_span(depth + 1, max_depth))
        return ''.join(ret_list)
