import typing

from TotalDepth.util import XmlWrite


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
                            assert isinstance(cell, str), f'{cell} is not a string but {type(cell)}'
                            xhtml_stream.charactersWithBr(cell)
