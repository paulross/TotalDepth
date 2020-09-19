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
"""A dictionary that takes a list of hashables as a key and behaves like a tree."""
import typing

from TotalDepth.LIS import ExceptionTotalDepthLIS

__author__  = 'Paul Ross'
__date__    = '2009-09-15'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'


class ExceptionDictTree(ExceptionTotalDepthLIS):
    """Exception when handling a DictTree object."""
    pass


class ExceptionDictTreeHtmlTable(ExceptionDictTree):
    """Exception when handling a DictTreeHtmlTable object."""
    pass


class DictTree:
    """A dictionary that takes a list of hashables as a key and behaves like a tree."""
    INDENT_STR = '  '
    ITERABLE_TYPE = (None, 'list', 'set')
    # HTML table events
    ROW_OPEN = (None, 0, 0)
    ROW_CLOSE = (None, -1, -1)

    def __init__(self, valIterable=None):
        if valIterable not in self.ITERABLE_TYPE:
            raise ExceptionDictTree('"%s" not in acceptable range: %s' % (valIterable, self.ITERABLE_TYPE))
        self._vI = valIterable
        # A dictionary of hashable to a node
        self._ir: typing.Optional[typing.Dict[typing.Hashable, DictTree]] = None
        # Node 'value' can be anything
        self._v: typing.Any = None

    def __iadd__(self, other):
        if self._vI != other._vI:
            raise ExceptionDictTree('Can not += mixed values {:s} and {:s}'.format(self._vI, other._vI))
        for k in other.keys():
            self.add(k, other.value(k))
        return self

    def retNewInstance(self):
        return DictTree(valIterable=self._vI)

    def add(self, k, v):
        """Add a key/value. k is a list of hashables."""
        if self._vI not in self.ITERABLE_TYPE:
            raise ExceptionDictTree('"%s" not in acceptble range: %s' \
                                    % (self._vI, self.ITERABLE_TYPE))
        if len(k) == 0:
            if self._vI is None:
                self._v = v
            elif self._vI == 'list':
                if self._v is None:
                    self._v = [v]
                else:
                    self._v.append(v)
            elif self._vI == 'set':
                if self._v is None:
                    self._v = set()
                self._v.add(v)
        else:
            if self._ir is None:
                self._ir = {}
            if k[0] not in self._ir:
                self._ir[k[0]] = self.retNewInstance()
            self._ir[k[0]].add(k[1:], v)
            
    def remove(self, k, v=None):
        """Remove a key/value. k is a list of hashables."""
        assert(self._vI in self.ITERABLE_TYPE)
        if len(k) == 0:
            if self._vI is None:
                self._v = None
            elif self._vI == 'list':
                if v is None:
                    self._v = None
                else:
                    if self._v is not None:
                        try:
                            self._v.remove(v)
                        except ValueError:#, err:
                            raise ExceptionDictTree('%s not in list %s' % (v, self._v))
                    else:
                        raise ExceptionDictTree('Value of key is None')
            elif self._vI == 'set':
                if v is None:
                    self._v = None
                else:
                    if self._v is not None:
                        try:
                            self._v.remove(v)
                        except KeyError:#, err:
                            raise ExceptionDictTree('%s not in set %s' % (v, self._v))
                    else:
                        raise ExceptionDictTree('Value of key is None')
        elif self._ir is not None:
            if k[0] in self._ir:
                self._ir[k[0]].remove(k[1:], v)
            else:
                raise ExceptionDictTree('No key: %s' % (k[0]))
        else:
            raise ExceptionDictTree('No key tree: %s' % (k))

    def value(self, k):
        """Value corresponding to a key or None. k is a list of hashables."""
        if len(k) == 0:
            return self._v
        if self._ir is None:
            return None
        try:
            return self._ir[k[0]].value(k[1:])
        except KeyError:
            pass
        return None
    
    def __contains__(self, k):
        return self.value(k) is not None

    def values(self):
        """Returns a list of all values."""
        retV = []
        self._values(retV)
        return retV
    
    def _values(self, theVs):
        if self._v is not None:
            theVs.append(self._v)
        if self._ir is not None:
            for k in self._ir.keys():
                self._ir[k]._values(theVs)
                
    def keys(self):
        """Return a list of keys where each key is a list of hashables."""
        retK = []
        kStk = []
        self._keys(retK, kStk)
        assert(len(kStk) == 0)
        return retK
    
    def _keys(self, kS, kStk):
        if self._v is not None:
            kS.append(kStk[:])
        if self._ir is not None:
            for k in self._ir.keys():
                kStk.append(k)
                self._ir[k]._keys(kS, kStk)
                kStk.pop()

    def __len__(self):
        """Returns the number of keys."""
        return len(self.keys())

    def depth(self):
        """Returns the maximum tree depth as an integer."""
        return self._depth(0)

    def _depth(self, theD):
        """Recursively returns the maximum tree depth as an integer."""
        #print 'theDepth', theDepth
        myD = theD
        if self._ir is not None:
            for k in self._ir.keys():
                myD = max(myD, self._ir[k]._depth(theD+1))
        return myD

    def indentedStr(self):
        retL = []
        kStk = []
        self._indentedStr(retL, kStk)
        assert(len(kStk) == 0)
        return '\n'.join(retL)
        
    def _indentedStr(self, theL, kStk):
        if self._v is not None:
            theL.append('%s%s' % (self.INDENT_STR*len(kStk), self._v))
        if self._ir is not None:
            kS = sorted(self._ir.keys())
            for k in kS:
                theL.append('%s%s' % (self.INDENT_STR*len(kStk), k))
                kStk.append(k)
                self._ir[k]._indentedStr(theL, kStk)
                kStk.pop()
                

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
    # HTML table events
    ROW_OPEN = DictTreeTableEvent([], None, 0, 0)
    ROW_CLOSE = DictTreeTableEvent([], None, -1, -1)

    def __init__(self, *args):
        super().__init__(*args)
        self._colSpan = self._rowSpan = 1
        self._has_valid_row_col_span = False

    # Overload mutating methods
    def add(self, k, v):
        """Add a key/value. k is a list of hashable."""
        self._has_valid_row_col_span = False
        super().add(k, v)

    def remove(self, k, v=None):
        """Remove a key/value. k is a list of hashable."""
        self._has_valid_row_col_span = False
        super().remove(k, v)

    def retNewInstance(self):
        return DictTreeHtmlTable(self._vI)

    @property
    def colSpan(self):
        return self._colSpan

    @property
    def rowSpan(self):
        return self._rowSpan

    def setColRowSpan(self):
        """Top level call that sets colspan and rowspan attributes."""
        if not self._has_valid_row_col_span:
            self._set_row_span()
            max_depth = self.depth()
            self._set_column_span(max_depth, -1)
            self._has_valid_row_col_span = True

    def _set_column_span(self, max_depth: int, depth: int):
        """Traverses the tree setting the columns span."""
        if self._ir is None:
            # Leaf node
            self._colSpan = max_depth - depth
        else:
            # Non-leaf
            self._colSpan = 1
            for tree in self._ir.values():
                tree._set_column_span(max_depth, depth + 1)
                tree._has_valid_row_col_span = True
    
    def _set_row_span(self):
        """Sets self._rowSpan recursively."""
        if self._ir is None:
            self._rowSpan = 1
        else:
            # Non-leaf node
            self._rowSpan = 0
            for aTree in self._ir.values():
                self._rowSpan += aTree._set_row_span()
        return self._rowSpan

    def genColRowEvents(self):
        """Returns a set of events that are quadruples.
        (key_branch, value, rowspan_int, colspan_int)
        The branch is a list of keys the from the branch of the tree.
        The rowspan and colspan are both integers.
        At the start of the a <tr> there will be a ROW_OPEN
        and at row end (</tr> a ROW_CLOSE will be yielded
        """
        self.setColRowSpan()
        has_yielded = False
        for anEvent in self.genColRowEventsFromBranch([]):
            if not has_yielded:
                yield self.ROW_OPEN
                has_yielded = True
            yield anEvent
        if has_yielded:
            yield self.ROW_CLOSE
    
    def genColRowEventsFromBranch(self, key_branch) -> typing.Iterable[DictTreeTableEvent]:
        """Returns a set of events that are a tuple of quadruples.
        (key_branch, value, rowspan_integer, colspan_integer)
        For example: (['a', 'b'], 'c', 3, 7)
        At the start of the a <tr> there will be a ROW_OPEN
        and at row end (</tr>) a ROW_CLOSE will be yielded
        """
        # This is a NOP if the internal data has not changed.
        self.setColRowSpan()
        if self._ir is not None:
            # Non-leaf
            keys = sorted(self._ir.keys())
            for i, k in enumerate(keys):
                key_branch.append(k)
                if i != 0:
                    yield self.ROW_CLOSE
                    yield self.ROW_OPEN
                yield DictTreeTableEvent(key_branch[:], self._ir[k]._v, self._ir[k].rowSpan, self._ir[k].colSpan)
                # Recurse
                for anEvent in self._ir[k].genColRowEventsFromBranch(key_branch):
                    yield anEvent
                key_branch.pop()

    def walkColRowSpan(self) -> str:
        max_depth = self.depth()
        return self._walk_column_row_span(0, max_depth)

    def _walk_column_row_span(self, d, max_depth) -> str:
        ret_list = []
        if self._ir is not None:
            for k in sorted(self._ir.keys()):
                ret_list.append('%s%s r=%d, c=%d\n' % ('  '*d, k, self._ir[k].rowSpan, self._ir[k].colSpan))
                ret_list.append(self._ir[k]._walk_column_row_span(d + 1, max_depth))
        return ''.join(ret_list)
