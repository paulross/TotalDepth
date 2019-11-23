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
