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
import logging
import os
import typing

from TotalDepth.util import XmlWrite, DictTree


logger = logging.getLogger(__file__)


class HTMLFrameArraySummary(typing.NamedTuple):
    ident: bytes
    num_frames: int
    channels: typing.Tuple[bytes]
    x_start: float
    x_stop: float
    x_units: bytes
    href: str


class HTMLLogicalFileSummary(typing.NamedTuple):
    """Contains the result of a Logical File as HTML."""
    eflr_types: typing.Tuple[bytes]
    frame_arrays: typing.Tuple[HTMLFrameArraySummary]


class HTMLBodySummary(typing.NamedTuple):
    """Contains the result of processing the body of the HTML."""
    link_text: str
    logical_files: typing.Tuple[HTMLLogicalFileSummary]


class HTMLResult(typing.NamedTuple):
    """Contains the result of processing a RP66V1 file to HTML."""
    path_input: str
    path_output: str
    size_input: int
    size_output: int
    binary_file_type: str
    time: float
    exception: bool
    ignored: bool
    html_summary: typing.Union[HTMLBodySummary, None]


def html_write_table(table_as_strings: typing.List[typing.List[str]],
                     xhtml_stream: XmlWrite.XhtmlStream,
                     class_style,
                     **kwargs) -> None:
    if len(table_as_strings):
        with XmlWrite.Element(xhtml_stream, 'table', {'class': class_style}):#.update(kwargs)):
            with XmlWrite.Element(xhtml_stream, 'tr', {}):
                for cell in table_as_strings[0]:
                    with XmlWrite.Element(xhtml_stream, 'th', {'class': class_style}):
                        xhtml_stream.characters(cell)
            for row in table_as_strings[1:]:
                with XmlWrite.Element(xhtml_stream, 'tr', {}):
                    for cell in row:
                        with XmlWrite.Element(xhtml_stream, 'td', {'class': class_style}):
                            if not isinstance(cell, str):
                                raise ValueError(f'{cell} is not a string but {type(cell)} in row: {row}')
                            xhtml_stream.charactersWithBr(cell)


CSS_INDEX = """/* CSS for index pages */
body {
font-size:      12px;
font-family:    arial,helvetica,sans-serif;
margin:         6px;
padding:        6px;
}
h1 {
color:            darkgoldenrod;
font-family:      sans-serif;
font-size:        14pt;
font-weight:      bold;
}
h2 {
color:          IndianRed;
font-family:    sans-serif;
font-size:      14pt;
font-weight:    normal;
}
h3 {
color:          Black;
font-family:    sans-serif;
font-size:      12pt;
font-weight:    bold;
}
h4 {
color:          FireBrick;
font-family:    sans-serif;
font-size:      10pt;
font-weight:    bold;
}
span.line {
color:           slategrey;
/*font-style:    italic; */
}
span.file {
 color:         black;
 font-style:    italic;
}

table.filetable {
    border:         2px solid black;
/*    font-family:    monospace; */
    color:          black;
}
th.filetable, td.filetable {
    /* border: 1px solid black; */
    border: 1px;
    border-top-style:solid;
    border-right-style:dotted;
    border-bottom-style:none;
    border-left-style:none;
    vertical-align:top;
    padding: 2px 6px 2px 6px; 
}
"""


class IndexHTML:
    """
    Creates an index.html that presents the directory structure as a table with links to the target HTML files
    and intermediate index.html files.
    The table can have extra columns of data.
    """
    INDEX_HTML = 'index.html'

    def __init__(self, headings: typing.List[str]):
        """
        Constructor.

        TODO: Add value_iterable option as None, 'set' or 'list'.

        :param headings: List of strings for the table cell headings.
        """
        self.headings = headings[:]
        self.index = {}
        self._common_path: typing.Optional[str] = None

    def __len__(self) -> int:
        return len(self.index)

    def add(self, path: str, *args: str) -> None:
        """Add a path and some date to write out in the index table.
        The data is expected to be appropriately formatted."""
        norm_path = os.path.abspath(path)
        if norm_path in self.index:
            raise ValueError(f'Duplicate path {norm_path}')
        if len(args) != len(self.headings):
            raise ValueError(f'Got {len(args)} values but expected {len(self.headings)}')
        self.index[norm_path] = args
        self._common_path = None

    @property
    def common_path(self) -> str:
        """The (cached) common path."""
        if self._common_path is None:
            if len(self.index) > 1:
                self._common_path = os.path.commonpath(self.index.keys())
            elif len(self.index) == 1:
                self._common_path = os.path.dirname(next(iter(self.index)))
        return self._common_path

    def remove_common_path(self, path: str) -> str:
        """Return the path stripped  of the common path prefix."""
        return path[len(self.common_path) + 1:]

    def write_indexes(self, create_intermediate: bool, class_style: str, css: str) -> typing.List[str]:
        """Write out the index.html files.

        Example: use class_style=filetable and css=CSS_INDEX
        """
        dict_tree = DictTree.DictTreeHtmlTable()  # value_iterable='list')
        for path, args in self.index.items():
            local_path_parts = self.remove_common_path(path).split(os.sep)
            dict_tree.add(local_path_parts, args)
        # print()
        # print('TRACE: dict_tree.indented_string()')
        # print(dict_tree.indented_string())
        # print()
        indexes: typing.List[str] = []
        self._write_indexes(dict_tree, [], create_intermediate, class_style, css, indexes)
        return indexes

    @staticmethod
    def attr(class_style: str, **kwargs) -> typing.Dict[str, str]:
        """Create attributes dict with optional class attribute. kwargs override this."""
        ret = {}
        if class_style:
            ret['class'] = class_style
        ret.update(kwargs)
        return ret

    def _write_indexes(self,
                       dict_tree: DictTree.DictTreeHtmlTable,
                       branch: typing.List[str],
                       create_intermediate: bool,
                       class_style: str,
                       css: str,
                       indexes: typing.List[str]
                       ) -> str:
        """Write out the index.html files recursively."""
        index_path = os.path.join(self.common_path, *branch, self.INDEX_HTML)
        logger.info('Opening index file at %s', index_path)
        if len(os.path.dirname(index_path)) > 0:
            os.makedirs(os.path.dirname(index_path), exist_ok=True)
        with open(index_path, 'w') as index_file:
            with XmlWrite.XhtmlStream(index_file) as index_xhtml_stream:
                with XmlWrite.Element(index_xhtml_stream, 'head'):
                    with XmlWrite.Element(index_xhtml_stream, 'meta', {
                        'charset': "UTF-8",
                        # 'name': "viewport",
                        # 'content': "width=device-width, initial-scale=1",
                    }):
                        pass
                    with XmlWrite.Element(index_xhtml_stream, 'title'):
                        index_xhtml_stream.charactersWithBr(f'IndexHTML of: "{self.remove_common_path(index_path)}"')
                    if css:
                        with XmlWrite.Element(index_xhtml_stream, 'style'):
                            index_xhtml_stream.literal(css)
                with XmlWrite.Element(index_xhtml_stream, 'body'):
                    with XmlWrite.Element(index_xhtml_stream, 'table', self.attr(class_style)):
                        # Headings
                        with XmlWrite.Element(index_xhtml_stream, 'tr', {}):
                            with XmlWrite.Element(index_xhtml_stream, 'th',
                                                  self.attr(class_style, colspan=f'{dict_tree.depth()}')):
                                index_xhtml_stream.characters('Path')
                            for heading in self.headings:
                                with XmlWrite.Element(index_xhtml_stream, 'th', self.attr(class_style)):
                                    index_xhtml_stream.characters(heading)
                        # Index content by cycling through the events.
                        for event in dict_tree.gen_row_column_events_from_branch(branch):
                            self._process_event(
                                dict_tree, branch, event, create_intermediate, class_style, css, indexes,
                                index_xhtml_stream
                            )
        logger.info('Completed index file at %s', index_path)
        indexes.append(index_path)
        return index_path

    def _process_event(self,
                       dict_tree: DictTree.DictTreeHtmlTable,
                       branch: typing.List[str],
                       event: DictTree.DictTreeTableEvent,
                       create_intermediate: bool,
                       class_style: str,
                       css: str,
                       indexes: typing.List[str],
                       index_xhtml_stream: XmlWrite.XhtmlStream
                       ):
        """
        Process the event which will result in a <tr>, </tr>, <td>, </td> element.
        This will recurse and create intermediate indexes if necessary.
        """
        # print('TRACE: YY branch', branch, 'event', event)
        if dict_tree.is_row_open(event):
            index_xhtml_stream.startElement('tr', self.attr(class_style))
        elif dict_tree.is_row_close(event):
            index_xhtml_stream.endElement('tr')
        else:
            with XmlWrite.Element(index_xhtml_stream, 'td',
                                  self.attr(class_style, rowspan=f'{event.row_span}', colspan=f'{event.col_span}')):
                if event.node is None:
                    # Refers to an intermediate index, recurse if necessary.
                    if create_intermediate:
                        idx_path = self._write_indexes(
                            dict_tree, branch + event.branch, create_intermediate, class_style, css, indexes
                        )
                        # Link to it
                        with XmlWrite.Element(
                                index_xhtml_stream, 'a', self.attr(class_style, href=self.remove_common_path(idx_path))
                        ):
                            index_xhtml_stream.characters(event.branch[-1])
                    else:
                        index_xhtml_stream.characters(event.branch[-1])
                else:
                    # HTML file target
                    with XmlWrite.Element(index_xhtml_stream, 'a', self.attr(class_style, href='/'.join(event.branch))):
                        index_xhtml_stream.characters(event.branch[-1])
            # Write out the arbitrary data as <td>'s.
            if event.node is not None:
                for value in event.node:
                    # TODO: Have separate style for extra cells?
                    with XmlWrite.Element(index_xhtml_stream, 'td', self.attr(class_style)):
                        index_xhtml_stream.characters(value)
