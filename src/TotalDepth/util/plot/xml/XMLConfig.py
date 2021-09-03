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
Code that supports the XML specification of plots.
"""
import os
import typing


from TotalDepth.common import xml
from TotalDepth import ExceptionTotalDepth

# XML_EXTENSION = '.xml'
#
#
# class ExceptionPlotXMLRead(ExceptionTotalDepth):
#     pass
#
#
# class PlotXMLRead:
#     """This is a generic class that reads any of the plot XML files, applies some semantic rules and gives an API as a
#     dict of {id : Element, ...} via the .nodes dict."""
#     def __init__(self, name: str, paths: typing.List[str], instream: typing.Union[None, typing.BinaryIO] = None):
#         root: xml.etree.Element
#         if instream is None:
#             for path in  paths:
#                 file_path = os.path.join(path, name + XML_EXTENSION)
#                 if os.path.exists(file_path):
#                     root = xml.etree.parse(file_path).getroot()
#                     break
#             else:
#                 raise IOError(f'Can not find XML file {name} in {paths}')
#         else:
#             root = xml.etree.parse(instream).getroot()
#         # Apply semantic checks whilst building the dict.
#         if root.tag != f'{name}Root':
#             raise ExceptionPlotXMLRead(f'Root element is "{root.tag}" but I expected "{name}Root"')
#         child: xml.etree.Element
#         self.nodes: typing.Dict[str, xml.etree.Element] = {}
#         for child in root:
#             if child.tag != name:
#                 raise ExceptionPlotXMLRead(f'Found child element "{child.tag}" but I expect "{name}"')
#             if 'id' not in child.attrib:
#                 raise ExceptionPlotXMLRead('Child element is missing "id" attribute')
#             if child.attrib['id'] in self.nodes:
#                 raise ExceptionPlotXMLRead(f'Duplicate child element "id" attribute of {child.attrib["id"]}')
#             self.nodes[child.attrib['id']] = child
#
