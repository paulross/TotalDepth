"""
RP66V1 HTML support.

"""
import logging
import os
import typing

import TotalDepth.RP66V1.core.XAxis
from TotalDepth.RP66V1.core import LogicalFile, File, StorageUnitLabel, LogPass, RepCode, AbsentValue, XAxis
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR
from TotalDepth.RP66V1.core.stringify import stringify_object_by_type
from TotalDepth.common import Slice
from TotalDepth.util import XmlWrite


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
            table_as_strings = eflr.key_values(stringify_function=stringify_object_by_type, sort=True)
        else:
            table_as_strings = eflr.table_as_strings(stringify_function=stringify_object_by_type, sort=True)
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
        rp66_file: File.FileRead,
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
            xhtml_stream.characters(f'Frame Array: {stringify_object_by_type(frame_array.ident)} [{fa}/{len(lp.frame_arrays)}]')
        ret.append(
            _write_frame_array_in_html(
                rp66_file,
                logical_file,
                frame_array,
                frame_slice,
                anchor,
                xhtml_stream,
            )
       )
    return tuple(ret)


def _write_x_axis_summary(x_axis: XAxis.XAxis, xhtml_stream: XmlWrite.XhtmlStream) -> None:
    # Parent section is heading h3

    # with XmlWrite.Element(xhtml_stream, 'h4'):
    #     xhtml_stream.characters('X Axis summary (all IFLRs)')
    with XmlWrite.Element(xhtml_stream, 'h4'):
        xhtml_stream.characters('X Axis')
    units = x_axis.units.decode('ascii')
    x_axis_table = [['X Axis', 'Value'],]
    x_axis_table.append(['Channel', f'{x_axis.ident}'])
    x_axis_table.append(['Long Name', f'{x_axis.long_name.decode("ascii")}'])
    x_axis_table.append(['Minimum', f'{x_axis.summary.min} [{units}]'])
    x_axis_table.append(['Maximum', f'{x_axis.summary.max} [{units}]'])
    x_axis_table.append(['Frame Count', f'{x_axis.summary.count}'])
    html_write_table(x_axis_table, xhtml_stream, class_style='monospace')
    with XmlWrite.Element(xhtml_stream, 'h4'):
        xhtml_stream.characters('X Axis Spacing')
    with XmlWrite.Element(xhtml_stream, 'p'):
        xhtml_stream.characters(f'Definitions: {XAxis.SPACING_DEFINITIONS}')
    x_spacing_table = [['X Axis Spacing', 'Value'],]
    if x_axis.summary.spacing is not None:
        spacing = x_axis.summary.spacing
        x_spacing_table.append(['Minimum', f'{spacing.min} [{units}]'])
        x_spacing_table.append(['Mean', f'{spacing.mean} [{units}]'])
        x_spacing_table.append(['Median', f'{spacing.median} [{units}]'])
        x_spacing_table.append(['Maximum', f'{spacing.max} [{units}]'])
        if spacing.median != 0:
            x_spacing_table.append(
                ['Range', f'{spacing.max - spacing.min} ({(spacing.max - spacing.min) / spacing.median:%}) [{units}]']
            )
        else:
            x_spacing_table.append(['Range', f'{spacing.max - spacing.min} [{units}]'])
        x_spacing_table.append(['Std. Dev.', f'{spacing.std} [{units}]'])
        x_spacing_table.append(['Count of Normal', f'{spacing.counts.norm:,d}'])
        x_spacing_table.append(['Count of Duplicate', f'{spacing.counts.dupe:,d}'])
        x_spacing_table.append(['Count of Skipped', f'{spacing.counts.skip:,d}'])
        x_spacing_table.append(['Count of Back', f'{spacing.counts.back:,d}'])
    html_write_table(x_spacing_table, xhtml_stream, class_style='monospace')
    if x_axis.summary.spacing is not None:
        with XmlWrite.Element(xhtml_stream, 'p'):
            xhtml_stream.characters('Frame spacing frequency:')
        with XmlWrite.Element(xhtml_stream, 'pre'):
            xhtml_stream.characters(x_axis.summary.spacing.histogram_str())


def _write_frame_array_in_html(
        rp66_file: File.FileRead,
        logical_file: LogicalFile.LogicalFile,
        frame_array: LogPass.FrameArray,
        frame_slice: typing.Union[Slice.Slice, Slice.Split],
        anchor: str,
        xhtml_stream: XmlWrite.XhtmlStream,
) -> HTMLFrameArraySummary:
    # Parent section is heading h3

    # with XmlWrite.Element(xhtml_stream, 'h4'):
    #     xhtml_stream.characters('Frame Data')
    iflrs: typing.List[TotalDepth.RP66V1.core.XAxis.IFLRReference] = logical_file.iflr_position_map[frame_array.ident]
    if len(iflrs):
        num_frames = LogicalFile.populate_frame_array(
            rp66_file,
            logical_file,
            frame_array,
            frame_slice,
            None
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
                f' [{stringify_object_by_type(frame_array.x_axis.units)}]'
            )
        with XmlWrite.Element(xhtml_stream, 'p'):
            xhtml_stream.characters(
                f'Frame analysis on {frame_slice.long_str(len(iflrs))} frame(s).'
                f' Number of frames created: {num_frames}'
                f' Numpy total memory: {frame_array.sizeof_array:,d} bytes'
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
                    stringify_object_by_type(channel.dimensions),
                    stringify_object_by_type(channel.count),
                    stringify_object_by_type(channel.units),
                    stringify_object_by_type(channel.long_name),
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
                                        xhtml_stream.characters(f'{stringify_object_by_type(frame_array.ident)}')
                                    xhtml_stream.characters(f' with {len(frame_array.channels)} channels')
                                    xhtml_stream.characters(f' and {len(logical_file.iflr_position_map[frame_array.ident])} frames')


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
    eflr_types: typing.Tuple[bytes]
    frame_arrays: typing.Tuple[HTMLFrameArraySummary]


class HTMLBodySummary(typing.NamedTuple):
    link_text: str
    logical_files: typing.Tuple[HTMLLogicalFileSummary]


def html_write_body(
        rp66_file: File.FileRead,
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
            frame_array_summary = _write_log_pass_content_in_html(rp66_file, logical_file, xhtml_stream, lf,
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


def html_scan_RP66V1_file_data_content(path_in: str, fout: typing.TextIO,
                                       *, frame_slice: Slice.Slice) -> HTMLBodySummary:
    """
    Scans all of every EFLR and IFLR in the file and writes to HTML.
    Similar to TotalDepth.RP66V1.core.Scan.scan_RP66V1_file_data_content
    Returns the text to use as a link.
    """
    with open(path_in, 'rb') as fobj:
        rp66v1_file = File.FileRead(fobj)
        logger.info(f'html_scan_RP66V1_file_data_content(): Creating LogicalFile.LogicalIndex()')
        logical_index = LogicalFile.LogicalIndex(rp66v1_file, path_in)
        logger.info(f'html_scan_RP66V1_file_data_content(): Writing to HTML.')
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
                ret = html_write_body(rp66v1_file, logical_index, frame_slice, xhtml_stream)
    logger.info(f'html_scan_RP66V1_file_data_content(): Done.')
    return ret
