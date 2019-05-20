"""
RP66V1 HTML support.

"""
import pprint
import typing

from TotalDepth.RP66V1.core import LogicalFile, File, StorageUnitLabel, LogPass, RepCode, AbsentValue
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR
from TotalDepth.util import XmlWrite


# Examples: https://jrgraphix.net/r/Unicode/25A0-25FF
UNICODE_SYMBOLS = {
    'TAPE_DRIVE': '\u2707',
    'TABLE': '\u2637',
    'TABLE_FINE': '\u2586',
    'CHANNEL': '\u2307',
}


def html_write_storage_unit_label(sul: StorageUnitLabel.StorageUnitLabel, xhtml_stream: XmlWrite.XhtmlStream) -> None:
    with XmlWrite.Element(xhtml_stream, 'table', {'border': '1'}):
        with XmlWrite.Element(xhtml_stream, 'tr', {}):
            with XmlWrite.Element(xhtml_stream, 'td', {}):
                xhtml_stream.characters('Storage Unit Sequence Number:')
            with XmlWrite.Element(xhtml_stream, 'td', {}):
                xhtml_stream.characters(f'{sul.storage_unit_sequence_number:d}')
        with XmlWrite.Element(xhtml_stream, 'tr', {}):
            with XmlWrite.Element(xhtml_stream, 'td', {}):
                xhtml_stream.characters('DLIS Version:')
            with XmlWrite.Element(xhtml_stream, 'td', {}):
                xhtml_stream.characters(f'{sul.dlis_version.decode("ascii")}')
        with XmlWrite.Element(xhtml_stream, 'tr', {}):
            with XmlWrite.Element(xhtml_stream, 'td', {}):
                xhtml_stream.characters('Storage Unit Structure:')
            with XmlWrite.Element(xhtml_stream, 'td', {}):
                xhtml_stream.characters(f'{sul.storage_unit_structure.decode("ascii")}')
        with XmlWrite.Element(xhtml_stream, 'tr', {}):
            with XmlWrite.Element(xhtml_stream, 'td', {}):
                xhtml_stream.characters('Maximum Record Length:')
            with XmlWrite.Element(xhtml_stream, 'td', {}):
                xhtml_stream.characters(f'{sul.maximum_record_length:d}')
        with XmlWrite.Element(xhtml_stream, 'tr', {}):
            with XmlWrite.Element(xhtml_stream, 'td', {}):
                xhtml_stream.characters('Storage Set Identifier:')
            with XmlWrite.Element(xhtml_stream, 'td', {}):
                xhtml_stream.characters(f'{sul.storage_set_identifier.decode("ascii")}')


def html_write_table(table_as_strings: typing.List[typing.List[str]], xhtml_stream: XmlWrite.XhtmlStream) -> None:
    if len(table_as_strings):
        with XmlWrite.Element(xhtml_stream, 'table', {'border': '1'}):
            with XmlWrite.Element(xhtml_stream, 'tr', {}):
                for cell in table_as_strings[0]:
                    with XmlWrite.Element(xhtml_stream, 'th', {}):
                        xhtml_stream.characters(cell)
            for row in table_as_strings[1:]:
                with XmlWrite.Element(xhtml_stream, 'tr', {}):
                    for cell in row:
                        with XmlWrite.Element(xhtml_stream, 'td', {}):
                            assert isinstance(cell, str), f'{cell} is not a string but {type(cell)}'
                            xhtml_stream.charactersWithBr(cell)


def html_write_EFLR_as_table(eflr: EFLR.ExplicitlyFormattedLogicalRecord, xhtml_stream: XmlWrite.XhtmlStream) -> None:
        if eflr.is_key_value():
            table_as_strings = eflr.key_values()
        else:
            table_as_strings = eflr.table_as_strings()
        # print('\n\n\nTRACE:')
        # pprint.pprint(table_as_strings)
        for r in range(len(table_as_strings)):
            for c in range(len(table_as_strings[r])):
                table_as_strings[r][c] = table_as_strings[r][c].replace(', ', '\n')
        html_write_table(table_as_strings, xhtml_stream)


def _write_log_pass_content_in_html(
        rp66_file: File.FileRead,
        visible_record_positions: LogicalFile.VisibleRecordPositions,
        logical_file: LogicalFile.LogicalFile,
        xhtml_stream: XmlWrite.XhtmlStream,
        *,
        frame_spacing) -> None:
    assert logical_file.has_log_pass
    assert frame_spacing >= 1
    lp: LogPass.LogPass = logical_file.log_pass
    frame_array: LogPass.FrameArray
    for fa, frame_array in enumerate(lp.frame_arrays):
        with XmlWrite.Element(xhtml_stream, 'h3'):
            xhtml_stream.characters(f'Frame Array [{fa}/{len(lp.frame_arrays)}]')
        with XmlWrite.Element(xhtml_stream, 'h4'):
            xhtml_stream.characters('Channels')
        # Table describing channels
        table_as_strings = [
            ['Channel', 'Rep Code', 'Dimensions', 'Count', 'Units', 'Long Name']
        ]
        # Table body.
        for channel in frame_array.channels:
            table_as_strings.append(
                [
                    str(channel.ident),
                    f'{channel.rep_code:d} ({RepCode.REP_CODE_INT_TO_STR[channel.rep_code]})',
                    str(channel.dimensions),
                    f'{channel.count:d}',
                    f'{channel.units}',
                    f'{channel.long_name}'
                ]
            )
        html_write_table(table_as_strings, xhtml_stream)
        with XmlWrite.Element(xhtml_stream, 'h4'):
            xhtml_stream.characters('Frame Data')
        iflrs = logical_file.iflr_position_map[frame_array.ident]
        if len(iflrs):
            if frame_spacing > 1:
                num_frames = 1 + len(iflrs) // frame_spacing
            else:
                num_frames = len(iflrs)
            frame_array.init_arrays(num_frames)
            interval = (iflrs[-1].x_axis - iflrs[0].x_axis) / len(iflrs)
            with XmlWrite.Element(xhtml_stream, 'p'):
                xhtml_stream.characters(
                    f'Frames [{len(iflrs)}]'
                    f' from: {float(iflrs[0].x_axis):0.3f}'
                    f' to {float(iflrs[-1].x_axis):0.3f}'
                    f' Interval: {interval:0.3f}'
                    f' {frame_array.x_axis.units}'
                )
            with XmlWrite.Element(xhtml_stream, 'p'):
                xhtml_stream.characters(
                    f'Frame spacing: {frame_spacing}'
                    f' number of frames: {num_frames}'
                    f' numpy size: {frame_array.sizeof_array:,d} bytes'
                )
            for f, (iflr_frame_number, lrsh_position, x_axis) in enumerate(iflrs):
                # TODO: raise
                assert f + 1 == iflr_frame_number
                if f % frame_spacing == 0:
                    vr_position = visible_record_positions.visible_record_prior(lrsh_position)
                    fld: File.FileLogicalData = rp66_file.get_file_logical_data(vr_position, lrsh_position)
                    iflr = IFLR.IndirectlyFormattedLogicalRecord(fld.lr_type, fld.logical_data)
                    frame_array.read(iflr.logical_data, f // frame_spacing)
            frame_table = [['Channel', 'Size', 'Absent', 'Min', 'Mean', 'Std.Dev.', 'Max', 'Units', 'dtype']]
            for channel in frame_array.channels:
                channel_ident = channel.ident.I.decode("ascii")
                # arr = channel.array
                arr = AbsentValue.mask_absent_values(channel.array)
                frame_table.append(
                    [
                        f'{channel_ident}',
                        f'{arr.size:d}',
                        # NOTE: Not the masked array!
                        f'{AbsentValue.count_of_absent_values(channel.array):d}',
                        f'{arr.min():.3f}',
                        f'{arr.mean():.3f}',
                        f'{arr.std():.3f}',
                        f'{arr.max():.3f}',
                        f'{channel.units}',
                        f'{arr.dtype}',
                    ]
                )
            html_write_table(frame_table, xhtml_stream)
        else:
            with XmlWrite.Element(xhtml_stream, 'p'):
                xhtml_stream.characters('No frames.')


def html_scan_RP66V1_file_data_content(fobj: typing.BinaryIO, fout: typing.TextIO,
                                       *, rp66v1_path: str, frame_spacing: int) -> None:
    """
    Scans all of every EFLR and IFLR in the file and writes to HTML.
    Similar to TotalDepth.RP66V1.core.Scan.scan_RP66V1_file_data_content
    """
    if frame_spacing <= 0:
        raise ValueError(f'Frame spacing must be > 0 not {frame_spacing}')
    logical_file_sequence = LogicalFile.LogicalFileSequence(fobj, rp66v1_path)
    rp66_file = File.FileRead(fobj)
    with XmlWrite.XhtmlStream(fout) as xhtml_stream:
        with XmlWrite.Element(xhtml_stream, 'h1'):
            xhtml_stream.characters('RP66V1 File Data Summary')
        html_write_storage_unit_label(logical_file_sequence.storage_unit_label, xhtml_stream)
        logical_file: LogicalFile.LogicalFile
        for lf, logical_file in enumerate(logical_file_sequence.logical_files):
            with XmlWrite.Element(xhtml_stream, 'h2'):
                xhtml_stream.characters(f'Logical File [{lf}/{len(logical_file_sequence.logical_files)}]')
            eflr_position: LogicalFile.PositionEFLR
            for e, eflr_position in enumerate(logical_file.eflrs):
                header = [
                    f'EFLR [{e}/{len(logical_file.eflrs)}]',
                    f'{eflr_position.eflr.set.type}',
                    f'{eflr_position.eflr.set.name}',
                    f'at {str(eflr_position.lrsh_position)}',
                ]
                with XmlWrite.Element(xhtml_stream, 'h3'):
                    xhtml_stream.characters(' '.join(header))
                html_write_EFLR_as_table(eflr_position.eflr, xhtml_stream)
            with XmlWrite.Element(xhtml_stream, 'h3'):
                xhtml_stream.characters('Log Pass')
            if logical_file.has_log_pass:
                # with _output_section_header_trailer('Log Pass', '-', os=fout):
                _write_log_pass_content_in_html(
                    rp66_file, logical_file_sequence.visible_record_positions,
                    logical_file, xhtml_stream, frame_spacing=frame_spacing)
            else:
                with XmlWrite.Element(xhtml_stream, 'p'):
                    xhtml_stream.characters('NO Log Pass for this Logical Record')
