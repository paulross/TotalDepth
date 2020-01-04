"""
Scans a RP66V1 file an writes out the summary in HTML.
"""
import logging
import multiprocessing
import os
import sys
import time
import typing

import colorama

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import AbsentValue
from TotalDepth.RP66V1.core import File
from TotalDepth.RP66V1.core import LogPass
from TotalDepth.RP66V1.core import LogicalFile
from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core import StorageUnitLabel
from TotalDepth.RP66V1.core import XAxis
from TotalDepth.RP66V1.core import stringify
from TotalDepth.RP66V1.core.LogicalRecord import EFLR
from TotalDepth.common import Slice
from TotalDepth.common import cmn_cmd_opts
from TotalDepth.common import process
from TotalDepth.util import DirWalk
from TotalDepth.util import bin_file_type
from TotalDepth.util import gnuplot, XmlWrite, DictTree

colorama.init(autoreset=True)


__author__  = 'Paul Ross'
__date__    = '2019-03-21'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


logger = logging.getLogger(__file__)


# Examples:
# https://jrgraphix.net/r/Unicode/
# https://jrgraphix.net/r/Unicode/25A0-25FF
UNICODE_SYMBOLS = {
    'TAPE_DRIVE': '\u2707',  # https://jrgraphix.net/r/Unicode/2700-27BF
    'TABLE': '\u2637',  # https://jrgraphix.net/r/Unicode/2600-26FF
    'TABLE_FINE': '\u25A6',  # https://jrgraphix.net/r/Unicode/25A0-25FF
    'CHANNEL': '\u2307',  # https://jrgraphix.net/r/Unicode/2300-23FF
}

CSS_RP66V1 = """/* CSS for RP66V1 */
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
    font-family:    monospace;
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


table.eflr {
    border:         2px solid black;
    border-collapse:   collapse;
    font-family:    monospace;
    color:          black;
}
th.eflr, td.eflr {
    border: 1px solid black;
    /* border-top-style:solid; */
    /* border-right-style:dotted; */
    /* border-bottom-style:none; */
    /* border-left-style:none; */
    vertical-align:top;
    padding: 2px 6px 2px 6px; 
}

table.sul {
    border:            2px solid black;
    border-collapse:   collapse;
    /* font-family:       monospace; */
    color:             black;
}

th.sul, td.sul {
    border:            1px solid black;
    vertical-align:    top;
    padding:           2px 6px 2px 6px; 
}

table.monospace {
    border:            2px solid black;
    border-collapse:   collapse;
    font-family:       monospace;
    color:             black;
}
th.monospace, td.monospace {
    border:            1px solid black;
    vertical-align:    top;
    padding:           2px 6px 2px 6px; 
}
"""

SCRIPT_RP66V1 = """
/* Sidebar animation */
var toggler = document.getElementsByClassName("caret");
var i;

for (i = 0; i < toggler.length; i++) {
    toggler[i].addEventListener("click", function () {
        this.parentElement.querySelector(".nested").classList.toggle("active");
        this.classList.toggle("caret-down");
    });
}
"""


def html_write_storage_unit_label(sul: StorageUnitLabel.StorageUnitLabel, xhtml_stream: XmlWrite.XhtmlStream) -> None:
    with XmlWrite.Element(xhtml_stream, 'h2'):
        xhtml_stream.characters('Storage Unit Label')
    table = [
        ['KEY', 'VALUE'],
        ['Storage Unit Sequence Number:', f'{sul.storage_unit_sequence_number:d}'],
        ['DLIS Version:', f'{sul.dlis_version.decode("ascii")}'],
        ['Storage Unit Structure:', f'{sul.storage_unit_structure.decode("ascii")}'],
        ['Maximum Record Length:', f'{sul.maximum_record_length:d}'],
        ['Storage Set Identifier:', f'{sul.storage_set_identifier.decode("ascii")}'],
    ]
    html_write_table(table, xhtml_stream, class_style='sul')


def html_write_table(table_as_strings: typing.List[typing.List[str]],
                     xhtml_stream: XmlWrite.XhtmlStream,
                     class_style) -> None:
    if len(table_as_strings):
        with XmlWrite.Element(xhtml_stream, 'table', {'class': class_style}):
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


def html_write_EFLR_as_table(eflr: EFLR.ExplicitlyFormattedLogicalRecord, xhtml_stream: XmlWrite.XhtmlStream) -> None:
        if eflr.is_key_value():
            table_as_strings = eflr.key_values(stringify_function=stringify.stringify_object_by_type, sort=True)
        else:
            table_as_strings = eflr.table_as_strings(stringify_function=stringify.stringify_object_by_type, sort=True)
        html_write_table(table_as_strings, xhtml_stream, class_style='eflr')


class HTMLFrameArraySummary(typing.NamedTuple):
    ident: bytes
    num_frames: int
    channels: typing.Tuple[bytes]
    x_start: float
    x_stop: float
    x_units: bytes
    href: str


def _write_log_pass_content_in_html(
        logical_file: LogicalFile.LogicalFile,
        xhtml_stream: XmlWrite.XhtmlStream,
        # Used for anchor
        logical_file_index: int,
        number_of_preceeding_eflrs: int,
        *,
        frame_slice: Slice.Slice) -> typing.Tuple[HTMLFrameArraySummary]:
    assert logical_file.has_log_pass
    ret = []
    lp: LogPass.LogPass = logical_file.log_pass
    frame_array: LogPass.FrameArray
    for fa, frame_array in enumerate(lp.frame_arrays):
        anchor = _anchor(logical_file_index, number_of_preceeding_eflrs, fa)
        with XmlWrite.Element(xhtml_stream, 'a', {'id': anchor}):
            pass
        with XmlWrite.Element(xhtml_stream, 'h3'):
            xhtml_stream.characters(
                f'Frame Array: {stringify.stringify_object_by_type(frame_array.ident)} [{fa}/{len(lp.frame_arrays)}]'
            )
        ret.append(
            _write_frame_array_in_html(
                logical_file,
                frame_array,
                frame_slice,
                anchor,
                xhtml_stream,
            )
       )
    return tuple(ret)


# def _write_x_axis_in_html(logical_file: LogicalFile.LogicalFile,
#                           frame_array: LogPass.FrameArray,
#                           xhtml_stream: XmlWrite.XhtmlStream) -> None:
#     x_axis: XAxis.XAxis = logical_file.iflr_position_map[frame_array.ident]
#     _write_x_axis_summary(x_axis, xhtml_stream)


def _write_x_axis_summary(x_axis: XAxis.XAxis, xhtml_stream: XmlWrite.XhtmlStream) -> None:
    # Parent section is heading h3

    # with XmlWrite.Element(xhtml_stream, 'h4'):
    #     xhtml_stream.characters('X Axis summary (all IFLRs)')
    with XmlWrite.Element(xhtml_stream, 'h4'):
        xhtml_stream.characters('X Axis')
    units = x_axis.units.decode('ascii')
    x_axis_table = [
        ['X Axis', 'Value'],
        ['Channel', f'{x_axis.ident}'],
        ['Long Name', f'{x_axis.long_name.decode("ascii")}'],
        ['Minimum', f'{x_axis.summary.min} [{units}]'],
        ['Maximum', f'{x_axis.summary.max} [{units}]'],
        ['Frame Count', f'{x_axis.summary.count}'],
    ]
    html_write_table(x_axis_table, xhtml_stream, class_style='monospace')
    with XmlWrite.Element(xhtml_stream, 'h4'):
        xhtml_stream.characters('X Axis Spacing')
    # with XmlWrite.Element(xhtml_stream, 'p'):
    #     xhtml_stream.characters(f'Definitions: {XAxis.SPACING_DEFINITIONS}')
    x_spacing_table = [['X Axis Spacing', 'Value', 'Description'],]
    if x_axis.summary.spacing is not None:
        spacing = x_axis.summary.spacing
        x_spacing_table.append(['Minimum', f'{spacing.min} [{units}]', ''])
        x_spacing_table.append(['Mean', f'{spacing.mean} [{units}]', ''])
        x_spacing_table.append(['Median', f'{spacing.median} [{units}]', ''])
        x_spacing_table.append(['Maximum', f'{spacing.max} [{units}]', ''])
        if spacing.median != 0:
            x_spacing_table.append(
                ['Range', f'{spacing.max - spacing.min} ({(spacing.max - spacing.min) / spacing.median:%}) [{units}]', '']
            )
        else:
            x_spacing_table.append(['Range', f'{spacing.max - spacing.min} [{units}]', ''])
        x_spacing_table.append(['Std. Dev.', f'{spacing.std} [{units}]', ''])
        x_spacing_table.append(['Count of back', f'{spacing.counts.back:,d}', 'spacing < -0.5 median'])
        x_spacing_table.append(['Count of duplicate', f'{spacing.counts.dupe:,d}', '-0.5 median <= spacing < 0.5 median'])
        x_spacing_table.append(['Count of normal', f'{spacing.counts.norm:,d}', '0.5 median <= spacing < 1.5 median'])
        x_spacing_table.append(['Count of skipped', f'{spacing.counts.skip:,d}', 'spacing >= 1.5 median'])
    html_write_table(x_spacing_table, xhtml_stream, class_style='monospace')
    if x_axis.summary.spacing is not None:
        with XmlWrite.Element(xhtml_stream, 'p'):
            xhtml_stream.characters('Frame spacing frequency:')
        with XmlWrite.Element(xhtml_stream, 'pre'):
            xhtml_stream.characters(x_axis.summary.spacing.histogram_str())


def _write_frame_array_in_html(
        logical_file: LogicalFile.LogicalFile,
        frame_array: LogPass.FrameArray,
        frame_slice: typing.Union[Slice.Slice, Slice.Sample],
        anchor: str,
        xhtml_stream: XmlWrite.XhtmlStream,
) -> HTMLFrameArraySummary:
    # Parent section is heading h3

    # with XmlWrite.Element(xhtml_stream, 'h4'):
    #     xhtml_stream.characters('Frame Data')
    iflrs: typing.List[XAxis.IFLRReference] = logical_file.iflr_position_map[frame_array.ident]
    if len(iflrs):
        num_frames = logical_file.populate_frame_array(
            frame_array,
            frame_slice,
            None,
        )
        x_axis: XAxis.XAxis = logical_file.iflr_position_map[frame_array.ident]
        _write_x_axis_summary(x_axis, xhtml_stream)

        with XmlWrite.Element(xhtml_stream, 'h4'):
            xhtml_stream.characters('Frame Analysis')
        with XmlWrite.Element(xhtml_stream, 'p'):
            if x_axis.summary.spacing is not None:
                interval = f'{x_axis.summary.spacing.median:0.3f}'
            else:
                interval = 'N/A'
            xhtml_stream.characters(
                f'Available frames: {len(iflrs)}'
                f' X axis from {float(iflrs[0].x_axis):0.3f}'
                f' to {float(iflrs[-1].x_axis):0.3f}'
                f' interval {interval}'
                f' [{stringify.stringify_object_by_type(frame_array.x_axis.units)}]'
            )
        with XmlWrite.Element(xhtml_stream, 'p'):
            # xhtml_stream.characters(
            #     f'Frame analysis on {frame_slice.long_str(len(iflrs))} frame(s).'
            #     f' Frame size: {frame_array.sizeof_frame} bytes.'
            #     f' Number of frames created: {num_frames}'
            #     f' Numpy total memory: {frame_array.sizeof_array:,d} bytes'
            # )
            xhtml_stream.characters(f'Frame analysis on')
            with XmlWrite.Element(xhtml_stream, 'tt'):
                xhtml_stream.characters(f' {frame_slice.long_str(len(iflrs))}')
            xhtml_stream.characters(
                f' frame(s).'
                f' Frame size: {frame_array.sizeof_frame} bytes.'
                f' Number of frames created: {num_frames}'
                f' Numpy total memory: {frame_array.sizeof_array:,d} bytes'
            )
        with XmlWrite.Element(xhtml_stream, 'p'):
            xhtml_stream.characters(
                f'RP66V1 Frame size {frame_array.len_input_bytes} (bytes/frame))'
                f' represented internally as {frame_array.sizeof_frame} (bytes/frame).'
            )
        frame_table = [
            ['Channel', 'O', 'C', 'Rep Code', 'Dims', 'Count', 'Units', 'Long Name',
             'Size', 'Absent', 'Min', 'Mean', 'Std.Dev.', 'Max', 'dtype'],
        ]
        for channel in frame_array.channels:
            # arr = channel.array
            arr = AbsentValue.mask_absent_values(channel.array)
            frame_table.append(
                [
                    channel.ident.I.decode("ascii"),
                    f'{channel.ident.O}',
                    f'{channel.ident.C}',
                    f'{channel.rep_code:d} ({RepCode.REP_CODE_INT_TO_STR[channel.rep_code]})',
                    stringify.stringify_object_by_type(channel.dimensions),
                    stringify.stringify_object_by_type(channel.count),
                    stringify.stringify_object_by_type(channel.units),
                    stringify.stringify_object_by_type(channel.long_name),
                    f'{arr.size:d}',
                    # NOTE: Not the masked array!
                    f'{AbsentValue.count_of_absent_values(channel.array):d}',
                    f'{arr.min():.3f}',
                    f'{arr.mean():.3f}',
                    f'{arr.std():.3f}',
                    f'{arr.max():.3f}',
                    f'{arr.dtype}',
                ]
            )
        html_write_table(frame_table, xhtml_stream, class_style='monospace')
        x_axis_start = iflrs[0].x_axis
        x_axis_stop = iflrs[-1].x_axis
    else:
        with XmlWrite.Element(xhtml_stream, 'p'):
            xhtml_stream.characters('No frames.')
        x_axis_start = x_axis_stop = 0.0
    return HTMLFrameArraySummary(
        frame_array.ident.I,
        len(iflrs),
        tuple(c.ident.I for c in frame_array.channels),
        x_axis_start,
        x_axis_stop,
        frame_array.x_axis.units,
        anchor,
    )


# def _anchor(*args: typing.Tuple[int, ...]) -> str:
def _anchor(*args) -> str:
    arg_list = '_'.join(f'{arg:d}' for arg in args)
    return f'anchor_{arg_list}'


def html_write_table_of_contents(
        logical_file_sequence: LogicalFile.LogicalIndex,
        xhtml_stream: XmlWrite.XhtmlStream) -> None:
    """Write out the table of contents."""
    with XmlWrite.Element(xhtml_stream, 'h2'):
        xhtml_stream.characters('Table of Contents')
    with XmlWrite.Element(xhtml_stream, 'ol'):
        logical_file: LogicalFile.LogicalFile
        for index_lf, logical_file in enumerate(logical_file_sequence.logical_files):
            with XmlWrite.Element(xhtml_stream, 'li'):
                xhtml_stream.characters(f'Logical File [{index_lf}/{len(logical_file_sequence.logical_files)}]')
            with XmlWrite.Element(xhtml_stream, 'ol'):
                lrsh_position: File.LogicalRecordPosition
                eflr: EFLR.ExplicitlyFormattedLogicalRecord
                for index_eflr, (lrsh_position, eflr) in enumerate(logical_file.eflrs):
                    with XmlWrite.Element(xhtml_stream, 'li'):
                        with XmlWrite.Element(xhtml_stream, 'a', {'href': f'#{_anchor(index_lf, index_eflr)}'}):
                            xhtml_stream.characters(f'{eflr.set.type.decode("ascii")}')
                        xhtml_stream.literal('&nbsp;')
                        xhtml_stream.characters(f'Shape: {eflr.shape}')
                if logical_file.has_log_pass:
                    with XmlWrite.Element(xhtml_stream, 'li'):
                        with XmlWrite.Element(xhtml_stream, 'a', {'href': f'#{_anchor(index_lf, len(logical_file.eflrs))}'}):
                            xhtml_stream.characters(f'Log Pass with {len(logical_file.log_pass)} Frame Arrays')
                        with XmlWrite.Element(xhtml_stream, 'ol'):
                            for index_fa, frame_array in enumerate(logical_file.log_pass):
                                with XmlWrite.Element(xhtml_stream, 'li'):
                                    attrs = {'href': f'#{_anchor(index_lf, len(logical_file.eflrs), index_fa)}'}
                                    # xhtml_stream.characters(f'Frame Array:')
                                    with XmlWrite.Element(xhtml_stream, 'a', attrs):
                                        xhtml_stream.characters(
                                            f'{stringify.stringify_object_by_type(frame_array.ident)}'
                                        )
                                    xhtml_stream.characters(f' with {len(frame_array.channels)} channels')
                                    xhtml_stream.characters(
                                        f' and {len(logical_file.iflr_position_map[frame_array.ident])} frames'
                                    )


def html_write_file_info(path_in: str, xhtml_stream: XmlWrite.XhtmlStream) -> None:
    with XmlWrite.Element(xhtml_stream, 'h2'):
        xhtml_stream.characters('File information')
    table = [
        ['KEY', 'VALUE'],
        ['File Path:', path_in],
        ['File size:', f'{os.path.getsize(path_in):,d}'],
    ]
    html_write_table(table, xhtml_stream, class_style='monospace')


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
    time: float
    exception: bool
    ignored: bool
    html_summary: typing.Union[HTMLBodySummary, None]


def html_write_body(
        logical_file_sequence: LogicalFile.LogicalIndex,
        frame_slice: Slice.Slice,
        xhtml_stream: XmlWrite.XhtmlStream,
    ) -> HTMLBodySummary:
    """Write out the <body> of the document."""
    with XmlWrite.Element(xhtml_stream, 'h1'):
        xhtml_stream.characters('RP66V1 File Data Summary')
    html_write_file_info(logical_file_sequence.id, xhtml_stream)
    html_write_storage_unit_label(logical_file_sequence.storage_unit_label, xhtml_stream)
    html_write_table_of_contents(logical_file_sequence, xhtml_stream)
    logical_file_summaries: typing.List[HTMLLogicalFileSummary] = []
    logical_file: LogicalFile.LogicalFile
    for lf, logical_file in enumerate(logical_file_sequence.logical_files):
        eflr_types: typing.List[bytes] = []
        with XmlWrite.Element(xhtml_stream, 'h2'):
            xhtml_stream.characters(f'Logical File [{lf}/{len(logical_file_sequence.logical_files)}]')
        eflr_position: LogicalFile.PositionEFLR
        for e, eflr_position in enumerate(logical_file.eflrs):
            eflr_types.append(eflr_position.eflr.set.type)
            header = [
                f'EFLR: {eflr_position.eflr.set.type.decode("ascii")}',
                f'Shape: {eflr_position.eflr.shape}'
            ]
            with XmlWrite.Element(xhtml_stream, 'a', {'id': f'{_anchor(lf, e)}'}):
                pass
            with XmlWrite.Element(xhtml_stream, 'h3'):
                xhtml_stream.characters(' '.join(header))
            with XmlWrite.Element(xhtml_stream, 'p'):
                xhtml_stream.characters(f'Location: {eflr_position.lrsh_position}')
            with XmlWrite.Element(xhtml_stream, 'p'):
                xhtml_stream.characters(
                    f'Logical Data consumed to create: Set: {eflr_position.eflr.set.logical_data_consumed}'
                    f' Template: {eflr_position.eflr.template.logical_data_consumed}'
                    f' Complete EFLR: {eflr_position.eflr.logical_data_consumed}'
                )
            if eflr_position.eflr.set.type == b'FILE-HEADER':
                obj = eflr_position.eflr.objects[0]
                with XmlWrite.Element(xhtml_stream, 'p'):
                    xhtml_stream.characters(
                        f'File-Header Object "{obj.name.I.decode("ascii")}" O: {obj.name.O} C: {obj.name.C}:'
                    )
            elif eflr_position.eflr.set.type == b'ORIGIN':
                # Slightly special case with ORIGIN records as they contain the Defining Origin of the Logical File.
                # [RP66V1 Section 5.2.1 Origin Objects]
                obj = eflr_position.eflr.objects[0]
                with XmlWrite.Element(xhtml_stream, 'p'):
                    xhtml_stream.characters(
                        f'Logical File Defining Origin "{obj.name.I.decode("ascii")}" O: {obj.name.O} C: {obj.name.C}:'
                    )
            html_write_EFLR_as_table(eflr_position.eflr, xhtml_stream)
        with XmlWrite.Element(xhtml_stream, 'h3'):
            xhtml_stream.characters('Log Pass')
        if logical_file.has_log_pass:
            with XmlWrite.Element(xhtml_stream, 'a', {'id': f'{_anchor(lf, len(logical_file.eflrs))}'}):
                pass
            frame_array_summary = _write_log_pass_content_in_html(logical_file, xhtml_stream, lf,
                                                                  len(logical_file.eflrs),
                                                                  frame_slice=frame_slice,
                                                                  )
            logical_file_summaries.append((HTMLLogicalFileSummary(tuple(eflr_types), frame_array_summary)))
        else:
            with XmlWrite.Element(xhtml_stream, 'p'):
                xhtml_stream.characters('NO Log Pass for this Logical Record')
            logical_file_summaries.append((HTMLLogicalFileSummary(tuple(eflr_types), tuple())))
    return HTMLBodySummary(
        logical_file_sequence.storage_unit_label.storage_set_identifier.decode('ascii'),
        tuple(logical_file_summaries),
    )


def html_scan_RP66V1_file_data_content(path_in: str, fout: typing.TextIO, label_process: bool,
                                       frame_slice: Slice.Slice) -> HTMLBodySummary:
    """
    Scans all of every EFLR and IFLR in the file and writes to HTML.
    Similar to TotalDepth.RP66V1.core.Scan.scan_RP66V1_file_data_content
    Returns the text to use as a link.
    """
    with LogicalFile.LogicalIndex(path_in) as logical_index:
        if label_process:
            process.add_message_to_queue(os.path.basename(path_in))
        logger.info(
            f'html_scan_RP66V1_file_data_content(): Creating File.FileRead() from "{os.path.basename(path_in)}"'
        )
        logger.info(
            f'html_scan_RP66V1_file_data_content(): Creating LogicalFile.LogicalIndex()'
            f' from "{os.path.basename(path_in)}"'
        )
        logger.info(f'html_scan_RP66V1_file_data_content(): Writing HTML')
        if label_process:
            process.add_message_to_queue('Writing HTML')
        with XmlWrite.XhtmlStream(fout) as xhtml_stream:
            with XmlWrite.Element(xhtml_stream, 'head'):
                with XmlWrite.Element(xhtml_stream, 'meta', {
                    'charset': "UTF-8",
                    'name': "viewport",
                    'content': "width=device-width, initial-scale=1",
                }):
                    pass
                with XmlWrite.Element(xhtml_stream, 'title'):
                    xhtml_stream.charactersWithBr(f'RP66V1 Scan of {path_in}')
                with XmlWrite.Element(xhtml_stream, 'style'):
                    xhtml_stream.literal(CSS_RP66V1)
            with XmlWrite.Element(xhtml_stream, 'body'):
                ret = html_write_body(logical_index, frame_slice, xhtml_stream)
    logger.info(f'html_scan_RP66V1_file_data_content(): Done "{os.path.basename(path_in)}"')
    return ret


def scan_a_single_file(path_in: str, path_out: str, label_process: bool,
                       frame_slice: typing.Union[Slice.Slice, Slice.Sample]) -> HTMLResult:
    """Scan a single file and write out an HTML summary."""
    file_path_out = path_out + '.html'
    logger.debug(f'Scanning "{path_in}" to "{file_path_out}"')
    binary_file_type = bin_file_type.binary_file_type_from_path(path_in)
    if binary_file_type == 'RP66V1':
        logging.info(f'ScanFileHTML.scan_a_single_file(): "{path_in}" to "{file_path_out}"')
        # logging.info(f'scan_a_single_file(): "{path_in}"')
        t_start = time.perf_counter()
        try:
            if path_out:
                out_dir = os.path.dirname(path_out)
                if not os.path.exists(out_dir):
                    logger.debug(f'Making directory: {out_dir}')
                    os.makedirs(out_dir, exist_ok=True)
                with open(file_path_out, 'w') as fout:
                    logger.info(f'scan_a_single_file() target: "{os.path.basename(file_path_out)}"')
                    html_summary = html_scan_RP66V1_file_data_content(path_in, fout, label_process, frame_slice)
                len_scan_output = os.path.getsize(file_path_out)
            else:
                html_summary = html_scan_RP66V1_file_data_content(path_in, sys.stdout, label_process, frame_slice)
                len_scan_output = -1
            result = HTMLResult(
                path_in,
                file_path_out,
                os.path.getsize(path_in),
                len_scan_output,
                time.perf_counter() - t_start,
                False,
                False,
                html_summary,
            )
        except ExceptionTotalDepthRP66V1:
            logger.exception(f'Failed to index with ExceptionTotalDepthRP66V1: {path_in}')
            result = HTMLResult(path_in, file_path_out, os.path.getsize(path_in), 0, 0.0, True, False, None)
        except Exception:
            logger.exception(f'Failed to index with Exception: {path_in}')
            result = HTMLResult(path_in, file_path_out, os.path.getsize(path_in), 0, 0.0, True, False, None)
    else:
        logger.debug(f'Ignoring file type "{binary_file_type}" at {path_in}')
        result = HTMLResult(path_in, file_path_out, 0, 0, 0.0, False, True, None)
    return result


CSS_RP66V1_INDEX = """/* CSS for RP66V1 index pages */
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

INDEX_FILE = 'index.html'


def _write_indexes(path_out: str, index: typing.Dict[str, HTMLResult]) -> None:
    assert os.path.isdir(path_out), f'{path_out} is not a directory'
    # pprint.pprint(index)
    # print('TRACE: _write_indexes():')
    # pprint.pprint(index)
    logging.info(f'_write_indexes(): to "{path_out}"')
    _write_low_level_indexes(path_out, index)
    _write_top_level_index(path_out, index)


def _write_low_level_indexes(path_out: str, index: typing.Dict[str, HTMLResult]) -> None:
    assert os.path.isdir(path_out)
    logging.info(f'_write_low_level_indexes(): to "{path_out}"')
    # Write low level indexes
    for root, dirs, files in os.walk(path_out):
        files_to_link_to = []
        for file in files:
            out_file_path = os.path.join(root, file)
            if out_file_path in index:
                files_to_link_to.append(file)
        if len(files_to_link_to):
            with open(os.path.join(root, INDEX_FILE), 'w') as fout:
                logging.info(f'_write_low_level_indexes(): to "{os.path.join(root, INDEX_FILE)}"')
                with XmlWrite.XhtmlStream(fout) as xhtml_stream:
                    with XmlWrite.Element(xhtml_stream, 'head'):
                        with XmlWrite.Element(xhtml_stream, 'meta', {
                            'charset': "UTF-8",
                            'name': "viewport",
                            'content': "width=device-width, initial-scale=1",
                        }):
                            pass
                        with XmlWrite.Element(xhtml_stream, 'title'):
                            xhtml_stream.charactersWithBr(f'Index of RP66V1 Scan: {root}')
                        with XmlWrite.Element(xhtml_stream, 'style'):
                            xhtml_stream.literal(CSS_RP66V1_INDEX)
                    with XmlWrite.Element(xhtml_stream, 'body'):
                        with XmlWrite.Element(xhtml_stream, 'h1'):
                            xhtml_stream.charactersWithBr(f'Index of RP66V1 Scan {root}')
                        with XmlWrite.Element(xhtml_stream, 'table', {'class': 'filetable'}):
                            with XmlWrite.Element(xhtml_stream, 'tr', {'class': 'filetable'}):
                                for header in ('Physical File', 'File', 'Frame Array', 'Frames', 'Channels', 'X Start',
                                               'X Stop', 'dX', 'X Units'):
                                    with XmlWrite.Element(xhtml_stream, 'th', {'class': 'filetable'}):
                                        xhtml_stream.characters(header)
                            # dict_tree = DictTree.DictTreeHtmlTable(None)
                            # for file in files_to_link_to:
                            #     branch = [FileNameLinkHref(file, file, file)]
                            #     html_summary = index[os.path.join(root, file)].html_summary
                            #     if html_summary is not None:
                            #         for lf, logical_file_result in enumerate(html_summary.logical_files):
                            #             branch.append(lf)
                            #             for frame_array_result in logical_file_result.frame_arrays:
                            #                 # HTMLFrameArraySummary
                            #                 branch.append(frame_array_result.ident)
                            #                 dict_tree.add(branch, frame_array_result)
                            #                 branch.pop()
                            #             branch.pop()
                            # _write_low_level_index_table_body(xhtml_stream, dict_tree)


# def _write_low_level_index_table_body(xhtml_stream: XmlWrite.XhtmlStream, dict_tree: DictTree.DictTreeHtmlTable) -> None:
#     # Table body
#     # print('TRACE:', dict_tree.indentedStr())
#     file_href = ''
#     for event in dict_tree.genColRowEvents():
#         if event == dict_tree.ROW_OPEN:
#             # Write out the '<tr>' element
#             xhtml_stream.startElement('tr', {'class': 'filetable'})
#         elif event == dict_tree.ROW_CLOSE:
#             # Write out the '</tr>' element
#             xhtml_stream.endElement('tr')
#         else:
#             td_attrs = {'class': 'filetable'}
#             if event.row_span > 1:
#                 td_attrs['rowspan'] = f'{event.row_span:d}'
#             if event.col_span > 1:
#                 td_attrs['colspan'] = f'{event.col_span:d}'
#             if event.node is None:
#                 with XmlWrite.Element(xhtml_stream, 'td', td_attrs):
#                     if isinstance(event.branch[-1], FileNameLinkHref):
#                         file_href = event.branch[-1].href
#                         with XmlWrite.Element(xhtml_stream, 'a', {'href': file_href}):
#                             xhtml_stream.characters(str(event.branch[-1].file_name))
#                     else:
#                         xhtml_stream.characters(f'{str(event.branch[-1])}')
#                     # xhtml_stream.characters(f'{str(event.branch[-1])}')
#             else:
#                 node: HTMLFrameArraySummary = event.node
#                 # Frame Array
#                 with XmlWrite.Element(xhtml_stream, 'td', td_attrs):
#                     with XmlWrite.Element(xhtml_stream, 'a', {'href': f'{file_href}#{node.href}'}):
#                         xhtml_stream.characters(str(event.branch[-1]))
#                 # Write the node cells
#                 with XmlWrite.Element(xhtml_stream, 'td', {'class': 'filetable', 'align': 'right'}):
#                     xhtml_stream.characters(f'{node.num_frames:,d}')
#                 with XmlWrite.Element(xhtml_stream, 'td', {'class': 'filetable', 'align': 'right'}):
#                     xhtml_stream.characters(f'{len(node.channels):,d}')
#                 frame_spacing = (node.x_stop - node.x_start) / (node.num_frames - 1) if node.num_frames > 1 else 0.0
#                 for value in (f'{node.x_start:.1f}', f'{node.x_stop:.1f}', f'{frame_spacing:.1f}', f'{node.x_units.decode("ascii")}'):
#                     with XmlWrite.Element(xhtml_stream, 'td', {'class': 'filetable', 'align': 'right'}):
#                         xhtml_stream.characters(value)


class FileNameLinkHref(typing.NamedTuple):
    file_name: str
    link_text: str
    href: str


def _write_top_level_index(path_out: str, index_map: typing.Dict[str, HTMLResult]) -> None:
    # Create a DictTree from the paths.
    dict_tree = DictTree.DictTreeHtmlTable(None)
    for k in index_map:
        branch = k.split(os.sep)
        dict_tree.add(branch, index_map[k])
    index_file_path = os.path.join(path_out, INDEX_FILE)
    logging.info(f'_write_top_level_index(): to "{index_file_path}"')
    with open(index_file_path, 'w') as fout:
        with XmlWrite.XhtmlStream(fout) as xhtml_stream:
            with XmlWrite.Element(xhtml_stream, 'head'):
                with XmlWrite.Element(xhtml_stream, 'meta', {
                    'charset': "UTF-8",
                    'name': "viewport",
                    'content': "width=device-width, initial-scale=1",
                }):
                    pass
                with XmlWrite.Element(xhtml_stream, 'title'):
                    xhtml_stream.charactersWithBr(f'RP66V1 Scan of {path_out}')
                with XmlWrite.Element(xhtml_stream, 'style'):
                    xhtml_stream.literal(CSS_RP66V1_INDEX)
            with XmlWrite.Element(xhtml_stream, 'body'):
                with XmlWrite.Element(xhtml_stream, 'h1'):
                    xhtml_stream.charactersWithBr(f'Index of RP66V1 Scan: {path_out}')
                with XmlWrite.Element(xhtml_stream, 'p'):
                    xhtml_stream.characters('Command:')
                with XmlWrite.Element(xhtml_stream, 'p'):
                    with XmlWrite.Element(xhtml_stream, 'pre'):
                        xhtml_stream.characters(' '.join(sys.argv))
                with XmlWrite.Element(xhtml_stream, 'table', {'class': 'filetable'}):
                    _write_top_level_index_table_body(index_file_path, dict_tree, xhtml_stream)


def _write_top_level_index_table_body(index_file_path: str,
                                      dict_tree: DictTree.DictTreeHtmlTable,
                                      xhtml_stream: XmlWrite.XhtmlStream) -> None:
    strip_out_path = len(os.path.dirname(index_file_path)) + 1
    for event in dict_tree.genColRowEvents():
        if event == dict_tree.ROW_OPEN:
            # Write out the '<tr>' element
            xhtml_stream.startElement('tr', {'class': 'filetable'})
        elif event == dict_tree.ROW_CLOSE:
            # Write out the '</tr>' element
            xhtml_stream.endElement('tr')
        else:
            td_attrs = {'class': 'filetable'}
            if event.row_span > 1:
                td_attrs['rowspan'] = f'{event.row_span:d}'
            if event.col_span > 1:
                td_attrs['colspan'] = f'{event.col_span:d}'
            if event.node is None:
                with XmlWrite.Element(xhtml_stream, 'td', td_attrs):
                    possible_index_file = os.path.join(*event.branch) + os.sep + INDEX_FILE
                    if os.path.exists(possible_index_file):
                        xhtml_stream.comment(f' Writing event branch[-1] with link to {INDEX_FILE} ')
                        with XmlWrite.Element(xhtml_stream, 'a', {'href': possible_index_file[strip_out_path:]}):
                            xhtml_stream.characters(f'{str(event.branch[-1])}')
                    else:
                        xhtml_stream.comment(
                            f' Writing event branch[-1] without link to absent {possible_index_file}'
                        )
                        xhtml_stream.characters(f'{str(event.branch[-1])}')
            else:
                node: HTMLResult = event.node
                with XmlWrite.Element(xhtml_stream, 'td', td_attrs):
                    xhtml_stream.comment(' Writing event.node with link ')
                    with XmlWrite.Element(xhtml_stream, 'a', {'href': f'{node.path_output[strip_out_path:]}'}):
                        xhtml_stream.characters(str(event.branch[-1]))


def scan_dir_multiprocessing(dir_in, dir_out, jobs,
                             frame_slice: typing.Union[Slice.Slice, Slice.Sample]) -> typing.Dict[str, HTMLResult]:
    """Multiprocessing code to plot log passes.
    Returns a dict of {path_in : HTMLResult, ...}"""
    assert os.path.isdir(dir_in)
    if jobs < 1:
        jobs = multiprocessing.cpu_count()
    logging.info('scan_dir_multiprocessing(): Setting multi-processing jobs to %d' % jobs)
    pool = multiprocessing.Pool(processes=jobs)
    tasks = [
        (t.filePathIn, t.filePathOut, False, frame_slice) for t in DirWalk.dirWalk(
            dir_in, dir_out, theFnMatch='', recursive=True, bigFirst=True
        )
    ]
    # print('tasks:')
    # pprint.pprint(tasks, width=200)
    # return {}
    results = [
        r.get() for r in [
            pool.apply_async(scan_a_single_file, t) for t in tasks
        ]
    ]
    _write_indexes(dir_out, {r.path_output : r for r in results})
    return {r.path_input: r for r in results}


def scan_dir_or_file(path_in: str, path_out: str,
                     recursive: bool, label_process: bool,
                     frame_slice: typing.Union[Slice.Slice, Slice.Sample]) -> typing.Dict[str, HTMLResult]:
    """Scans a directory or file putting the results in path_out.
    Returns a dict of {path_in : HTMLResult, ...}
    """
    # Required as we are going to split them by os.sep
    # NOTE: normpath removes trailing os.sep which is what we want.
    path_in = os.path.normpath(path_in)
    path_out = os.path.normpath(path_out)
    logging.info(f'scan_dir_or_file(): "{path_in}" to "{path_out}" recurse: {recursive}')
    ret: typing.Dict[str, HTMLResult] = {}
    # Output file path to FileResult
    if os.path.isdir(path_in):
        index_map_global: typing.Dict[str, HTMLResult] = {}
        if not recursive:
            for file_in_out in DirWalk.dirWalk(path_in, path_out, theFnMatch='', recursive=recursive, bigFirst=False):
                result = scan_a_single_file(
                    file_in_out.filePathIn, file_in_out.filePathOut, label_process, frame_slice
                )
                ret[file_in_out.filePathIn] = result
                if not result.exception and not result.ignored:
                    index_map_global[result.path_output] = result
            if label_process:
                process.add_message_to_queue('Writing Indexes.')
            _write_indexes(path_out, index_map_global)
        else:
            len_path_in = len(path_in.split(os.sep))
            for root, dirs, files in os.walk(path_in, topdown=False):
                root_rel_to_path_in = root.split(os.sep)[len_path_in:]
                dir_out = os.path.join(path_out, *root_rel_to_path_in)
                for file in files:
                    file_path_in = os.path.join(root, file)
                    # Respect sub-directories in root
                    # root_rel_to_path_in.append(file)
                    file_path_out = os.path.join(dir_out, file)
                    result = scan_a_single_file(file_path_in, file_path_out, label_process, frame_slice)
                    ret[file_path_in] = result
                    if not result.exception and not result.ignored:
                        index_map_global[result.path_output] = result
            if label_process:
                process.add_message_to_queue('Writing Indexes.')
            _write_indexes(path_out, index_map_global)
    else:
        ret[path_in] = scan_a_single_file(path_in, path_out, label_process, frame_slice)
    return ret


GNUPLOT_PLT = """set logscale x
set grid
set title "Scan of RP66V1 Files with ScanFile.py."
set xlabel "RP66V1 File Size (bytes)"
# set mxtics 5
# set xrange [0:3000]
# set xtics
# set format x ""

set logscale y
set ylabel "Scan Rate (ms/Mb), Scan Compression Ratio"
# set yrange [1:1e5]
# set ytics 20
# set mytics 2
# set ytics 8,35,3

set logscale y2
set y2label "Scan time (s), Ratio original size / HTML size"
# set y2range [1e-4:10]
set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

# set fit logfile

# Curve fit, rate
rate(x) = 10**(a + b * log10(x))
fit rate(x) "{name}.dat" using 1:($3*1000/($1/(1024*1024))) via a, b

rate2(x) = 10**(5.5 - 0.5 * log10(x))

# Curve fit, size ratio
size_ratio(x) = 10**(c + d * log10(x))
fit size_ratio(x) "{name}.dat" using 1:($2/$1) via c,d
# By hand
# size_ratio2(x) = 10**(3.5 - 0.65 * log10(x))

# Curve fit, compression ratio
compression_ratio(x) = 10**(e + f * log10(x))
fit compression_ratio(x) "{name}.dat" using 1:($1/$2) via e,f

set terminal svg size 1000,700 # choose the file format
set output "{name}_rate.svg" # choose the output device

# set key off

#set key title "Window Length"
#  lw 2 pointsize 2

# Fields: size_input, size_index, time, exception, ignored, path

#plot "{name}.dat" using 1:($3*1000/($1/(1024*1024))) axes x1y1 title "Scan Rate (ms/Mb), left axis" lt 1 w points, \\
    rate(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", a, b) lt 1 lw 2, \\
    "{name}.dat" using 1:3 axes x1y2 title "Scan Time (s), right axis" lt 4 w points, \\
    "{name}.dat" using 1:($1/$2) axes x1y2 title "Original Size / Scan size, right axis" lt 3 w points, \\
    compression_ratio(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", e, f) axes x1y2 lt 3 lw 2

plot "{name}.dat" using 1:($3*1000/($1/(1024*1024))) axes x1y1 title "Scan Rate (ms/Mb), left axis" lt 1 w points, \\
    "{name}.dat" using 1:($1/$2) axes x1y2 title "Original Size / Scan size, right axis" lt 3 w points

set output "{name}_times.svg" # choose the output device
set ylabel "Index Time (s)"
unset y2label

plot "{name}.dat" using 1:3 axes x1y1 title "Index Time (s), left axis" lt 1 w points, \\
    "{name}.dat" using 1:4 axes x1y1 title "Write Time (s), left axis" lt 2 w points, \\
    "{name}.dat" using 1:5 axes x1y1 title "Read Time (s), left axis" lt 3 w points

reset
"""


def plot_gnuplot(data: typing.Dict[str, HTMLResult], gnuplot_dir: str) -> None:
    if len(data) < 2:
        raise ValueError(f'Can not plot data with only {len(data)} points.')
    # First row is header row, create it then comment out the first item.
    table = [
        # list(HTMLResult._fields) + ['Path']
        ['size_input', 'size_output', 'time', 'Path']
    ]
    table[0][0] = f'# {table[0][0]}'
    for k in sorted(data.keys()):
        if data[k].size_input > 0 and not data[k].exception:
            # table.append(list(data[k]) + [k])
            table.append(
                [
                    data[k].size_input,
                    data[k].size_output,
                    data[k].time,
                    k
                ]
            )
    name = 'ScanFileHTML'
    return_code = gnuplot.invoke_gnuplot(gnuplot_dir, name, table, GNUPLOT_PLT.format(name=name))
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')
    return_code = gnuplot.write_test_file(gnuplot_dir, 'svg')
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')


def main() -> int:
    description = """Scans a RP66V1 file or directory and writes HTML version of the data."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = cmn_cmd_opts.path_in_out(
        description, prog='TotalDepth.RP66V1.ScanHTML.main', version=__version__, epilog=__rights__
    )
    cmn_cmd_opts.add_log_level(parser, level=20)
    cmn_cmd_opts.add_multiprocessing(parser)
    parser.add_argument(
        '-e', '--encrypted', action='store_true',
        help='Output encrypted Logical Records as well. [default: %(default)s]',
    )
    Slice.add_frame_slice_to_argument_parser(parser)
    process.add_process_logger_to_argument_parser(parser)
    gnuplot.add_gnuplot_to_argument_parser(parser)
    args = parser.parse_args()
    cmn_cmd_opts.set_log_level(args)
    # print('args:', args)
    # return 0
    clk_start = time.perf_counter()
    # Your code here
    if args.log_process > 0.0:
        with process.log_process(args.log_process):
            result: typing.Dict[str, HTMLResult] = scan_dir_or_file(
                args.path_in,
                args.path_out,
                args.recurse,
                label_process=True,
                frame_slice=Slice.create_slice_or_sample(args.frame_slice),
            )
    else:
        if cmn_cmd_opts.multiprocessing_requested(args) and os.path.isdir(args.path_in):
            result: typing.Dict[str, HTMLResult] = scan_dir_multiprocessing(
                args.path_in,
                args.path_out,
                args.jobs,
                frame_slice=Slice.create_slice_or_sample(args.frame_slice),
            )
        else:
            result: typing.Dict[str, HTMLResult] = scan_dir_or_file(
                args.path_in,
                args.path_out,
                args.recurse,
                label_process=False,
                frame_slice=Slice.create_slice_or_sample(args.frame_slice),
            )
    if args.log_process > 0.0:
        process.add_message_to_queue('Processing HTML Complete.')
    clk_exec = time.perf_counter() - clk_start
    # print('Execution time = %8.3f (S)' % clk_exec)
    size_scan = size_input = 0
    files_processed = 0
    header = (
        f'{"Size In":>16}',
        f'{"Size Out":>10}',
        f'{"Time":>8}',
        f'{"Ratio %":>8}',
        f'{"ms/Mb":>8}',
        f'{"Fail?":5}',
        f'Path',
    )
    print(' '.join(header))
    print(' '.join('-' * len(v) for v in header))
    for path in sorted(result.keys()):
        idx_result = result[path]
        if idx_result.size_input > 0:
            ms_mb = idx_result.time * 1000 / (idx_result.size_input / 1024 ** 2)
            ratio = idx_result.size_output / idx_result.size_input
            print(
                f'{idx_result.size_input:16,d} {idx_result.size_output:10,d}'
                f' {idx_result.time:8.3f} {ratio:8.3%} {ms_mb:8.1f} {str(idx_result.exception):5}'
                f' "{path}"'
            )
            size_input += result[path].size_input
            size_scan += result[path].size_output
            files_processed += 1

    if args.gnuplot:
        try:
            plot_gnuplot(result, args.gnuplot)
        except IOError:
            logger.exception('Plotting with gnuplot failed.')
    if size_input > 0:
        ms_mb = clk_exec * 1000 / (size_input / 1024**2)
    else:
        ms_mb = 0.0
    print(f'Processed {len(result):,d} files and {size_input:,d} bytes in {clk_exec:.3f} s, {ms_mb:.1f} ms/Mb')
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
