import collections
import contextlib
import logging
import sys
import typing

import colorama

from TotalDepth.RP66V1.core import File, LogPass, AbsentValue, XAxis, stringify
from TotalDepth.RP66V1.core import LogicalFile
from TotalDepth.RP66V1.core.LogicalRecord import IFLR, EFLR
from TotalDepth.common import Rle, data_table, Slice
from TotalDepth.util.bin_file_type import format_bytes


colorama.init(autoreset=True)


__author__  = 'Paul Ross'
__date__    = '2019-03-21'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


logger = logging.getLogger(__file__)


STANDARD_TEXT_WIDTH = 132


@contextlib.contextmanager
def _output_section_header_trailer(header: str, fillchar: str,
                                   width: int = STANDARD_TEXT_WIDTH,
                                   os: typing.TextIO = sys.stdout):
    s = colorama.Fore.GREEN + f' {header} '.center(width, fillchar) + '\n'
    os.write(s)
    yield
    s = colorama.Fore.GREEN + f' END {header} '.center(width, fillchar) + '\n'
    os.write(s)


def _colorama_note(msg: str):
    return colorama.Back.YELLOW + f'NOTE: {msg}'


def _write_position_rle(rle: Rle.RLE, fout: typing.TextIO) -> None:
    for r in range(len(rle)):
        rle_item = rle[r]
        fout.write(
            f'Datum: {rle_item.datum:16,d} 0x{rle_item.datum:08x}'
            f' Repeat: {rle_item.repeat:6,d}'
        )
        if rle_item.stride is None:
            fout.write(f' Stride: None')
        else:
            fout.write(f' Stride: {rle_item.stride:6,d} 0x{rle_item.stride:04x}')
        fout.write(f'\n')


def scan_RP66V1_file_visible_records(fobj: typing.BinaryIO, fout: typing.TextIO, **kwargs) -> None:
    """Scans the file reporting Visible Records, optionally Logical Record Segments as well."""
    verbose = kwargs.get('verbose', 0)
    if not verbose:
        fout.write(
            colorama.Fore.YELLOW
            + 'Use -v to see individual records, RLE of LRSH positions and length distribution of LRS.\n'
        )
    with _output_section_header_trailer('RP66V1 Visible and LRSH Records', '*', os=fout):
        lrsh_dump = kwargs['lrsh_dump']
        rp66_file = File.FileRead(fobj)
        vr_position = lr_position = 0
        count_vr = 0
        count_lrsh = 0
        count_lrsh_first = 0
        count_lrsh_type = collections.Counter()
        count_lrsh_length = collections.Counter()
        rle_visible_record_positions = Rle.RLE()
        rle_lrsh_positions = Rle.RLE()
        for visible_record in rp66_file.iter_visible_records():
            vr_stride = visible_record.position - vr_position
            rle_visible_record_positions.add(visible_record.position)
            if verbose:
                fout.write(f'{visible_record} Stride: 0x{vr_stride:08x} {vr_stride:6,d}\n')
            if lrsh_dump:
                for lrsh in rp66_file.iter_LRSHs_for_visible_record(visible_record):
                    count_lrsh_length.update([lrsh.length])
                    if lrsh.is_first:
                        rle_lrsh_positions.add(lrsh.position)
                        count_lrsh_first += 1
                        count_lrsh_type.update([lrsh.record_type])
                        output = colorama.Fore.GREEN + f' {lrsh}'
                    elif lrsh.is_last:
                        output = colorama.Fore.RED + f'  --{lrsh}'
                    else:
                        output = colorama.Fore.YELLOW + f'  ..{lrsh}'
                    if verbose:
                        lr_stride = lrsh.position - lr_position
                        fout.write(f'  {output} Stride: 0x{lr_stride:08x} {lr_stride:6,d}\n')
                    lr_position = lrsh.position
                    count_lrsh += 1
            vr_position = visible_record.position
            count_vr += 1
        with _output_section_header_trailer('Summary of Visible Records', '=', os=fout):
            fout.write(f'Visible records: {count_vr:,d}\n')
            with _output_section_header_trailer('RLE Visible Record Position', '-', os=fout):
                _write_position_rle(rle_visible_record_positions, fout)
        if lrsh_dump:
            with _output_section_header_trailer('Summary of LRSH', '=', os=fout):
                fout.write(f'LRSH: total={count_lrsh:,d} is_first={count_lrsh_first}\n')
                fout.write(f'LRSH: record types and counts (first segments only) [{len(count_lrsh_type)}]:\n')
                for record_type in sorted(count_lrsh_type.keys()):
                    fout.write(f'{record_type:3d} : {count_lrsh_type[record_type]:8,d}\n')
                fout.write(
                    f'LRSH: record lengths and counts (all segments)'
                    f' [{len(count_lrsh_length)}]'
                )
                if len(count_lrsh_length):
                    fout.write(f' range: {min(count_lrsh_length.keys())}...{max(count_lrsh_length.keys())}')
                fout.write(f'\n')
                if verbose:
                    for length in sorted(count_lrsh_length.keys()):
                        fout.write(f'{length:3d} : {count_lrsh_length[length]:8,d}\n')
                    with _output_section_header_trailer('RLE LRSH Position', '-', os=fout):
                        _write_position_rle(rle_lrsh_positions, fout)


def scan_RP66V1_file_logical_data(fobj: typing.BinaryIO, fout: typing.TextIO, **kwargs) -> None:
    """Scans the file reporting the raw Logical Data."""
    verbose = kwargs.get('verbose', 0)
    if not verbose:
        fout.write(colorama.Fore.YELLOW  + 'Use -v to see individual logical data.\n')
    dump_bytes = kwargs.get('dump_bytes', 0)
    dump_raw_bytes = kwargs.get('dump_raw_bytes', 0)
    if not dump_bytes:
        fout.write(colorama.Fore.YELLOW  + 'Use -v and --dump-bytes to see actual first n bytes.\n')
    # Both a dict of {record_type : collections.Counter(length)
    count_eflr_type_length_count = {}
    count_iflr_type_length_count = {}
    with _output_section_header_trailer('RP66V1 Logical Data Summary', '*', os=fout):
        rp66_file = File.FileRead(fobj)
        vr_position = 0
        header = [
            f'{"Visible R":10}',
            f'{"LRSH":10}',
            f'{"Typ":3}',
            f'{" "}',
            f'{"     "}',
            f'{"Length":8}',
        ]
        underline = ['-' * len(h) for h in header]
        if verbose:
            fout.write(' '.join(header) + '\n')
            fout.write(' '.join(underline) + '\n')
        for logical_data in rp66_file.iter_logical_records():
            if logical_data.lr_is_eflr:
                if logical_data.lr_type not in count_eflr_type_length_count:
                    count_eflr_type_length_count[logical_data.lr_type] = collections.Counter()
                count_eflr_type_length_count[logical_data.lr_type].update([len(logical_data)])
            else:
                if logical_data.lr_type not in count_iflr_type_length_count:
                    count_iflr_type_length_count[logical_data.lr_type] = collections.Counter()
                count_iflr_type_length_count[logical_data.lr_type].update([len(logical_data)])
            if verbose:
                messages = [
                    f'0x{logical_data.position.vr_position:08x}' if logical_data.position.vr_position != vr_position else ' ' * 10,
                    f'0x{logical_data.position.lrsh_position:08x}',
                    f'{logical_data.lr_type:3d}',
                    f'{"E" if logical_data.lr_is_eflr else "I"}',
                    f'{"Crypt" if logical_data.lr_is_encrypted else "Plain"}',
                    f'{len(logical_data.logical_data):8,d}',
                ]
                if dump_bytes:
                    if dump_bytes == -1:
                        if dump_raw_bytes:
                            messages.append(str(logical_data.logical_data.bytes))
                        else:
                            messages.append(format_bytes(logical_data.logical_data.bytes))
                    else:
                        if dump_raw_bytes:
                            messages.append(str(logical_data.logical_data.bytes[:dump_bytes]))
                        else:
                            messages.append(format_bytes(logical_data.logical_data.bytes[:dump_bytes]))
                fout.write(' '.join(messages))
                fout.write('\n')
            vr_position = logical_data.position.vr_position
        with _output_section_header_trailer('RP66V1 Logical Data EFLR Summary', '=', os=fout):
            count_total = sum(
                [
                    sum(count_eflr_type_length_count[record_type].values())
                    for record_type in count_eflr_type_length_count
                ]
            )
            fout.write(f'Total number of EFLR records: {count_total:,d}\n')
            length_total_eflr = 0
            for record_type in count_eflr_type_length_count:
                for length, count in count_eflr_type_length_count[record_type].items():
                    length_total_eflr += length * count
            fout.write(f'Total length of EFLR records: {length_total_eflr:,d}\n')
            for record_type in sorted(count_eflr_type_length_count.keys()):
                fout.write(
                    f'EFLR record type {record_type} lengths and count [{len(count_eflr_type_length_count[record_type])}]:\n'
                )
                for length in sorted(count_eflr_type_length_count[record_type]):
                    fout.write(f'{length:10,d}: {count_eflr_type_length_count[record_type][length]:10,d}\n')
        with _output_section_header_trailer('RP66V1 Logical Data IFLR Summary', '=', os=fout):
            count_total = sum(
                [
                    sum(count_iflr_type_length_count[record_type].values())
                    for record_type in count_iflr_type_length_count
                ]
            )
            fout.write(f'Total number of IFLR records: {count_total:,d}\n')
            length_total_iflr = 0
            for record_type in count_iflr_type_length_count:
                for length, count in count_iflr_type_length_count[record_type].items():
                    length_total_iflr += length * count
            fout.write(f'Total length of IFLR records: {length_total_iflr:,d}\n')
            for record_type in sorted(count_iflr_type_length_count.keys()):
                fout.write(
                    f'IFLR record type {record_type} lengths and count [{len(count_iflr_type_length_count[record_type])}]:\n'
                )
                for length in sorted(count_iflr_type_length_count[record_type]):
                    fout.write(f'{length:10,d}: {count_iflr_type_length_count[record_type][length]:10,d}\n')
        fout.write(f'Total length EFLR/IFLR: {length_total_eflr/length_total_iflr:.3%}\n')


def scan_RP66V1_file_EFLR_IFLR(fobj: typing.BinaryIO, fout: typing.TextIO, **kwargs) -> None:
    """Scans the file reporting the individual EFLR and IFLR."""
    verbose = kwargs.get('verbose', 0)
    if not verbose:
        fout.write(colorama.Fore.YELLOW  + 'Use -v to see individual logical data.\n')
    # TODO: eflr_dump is never present
    dump_eflr = kwargs.get('eflr_dump', 0)
    eflr_set_type = kwargs.get('eflr_set_type', [])
    dump_iflr = kwargs.get('iflr_dump', 0)
    iflr_set_type = kwargs.get('iflr_set_type', [])
    # TODO: Use both of these
    dump_bytes = kwargs.get('dump_bytes', 0)
    dump_raw_bytes = kwargs.get('dump_raw_bytes', 0)
    if not dump_bytes:
        fout.write(colorama.Fore.YELLOW  + 'Use -v and --dump-bytes to see actual first n bytes.\n')
    with _output_section_header_trailer('RP66V1 EFLR and IFLR Data Summary', '*', os=fout):
        rp66_file = File.FileRead(fobj)
        # TODO: use data_table.format_table
        vr_position = 0
        header = [
            f'{"Visible R":10}',
            f'{"LRSH":10}',
            f'{"Typ":3}',
            f'{" "}',
            f'{"     "}',
            f'{"Length":8}',
        ]
        underline = ['-' * len(h) for h in header]
        if verbose:
            fout.write(' '.join(header) + '\n')
            fout.write(' '.join(underline) + '\n')
        for file_logical_data in rp66_file.iter_logical_records():
            if file_logical_data.lr_is_eflr:
                if file_logical_data.lr_is_encrypted:
                    if kwargs['encrypted']:
                        if verbose:
                            fout.write(colorama.Fore.MAGENTA + f'Encrypted EFLR: {file_logical_data}' + colorama.Style.RESET_ALL)
                        else:
                            fout.write(colorama.Fore.MAGENTA + f'Encrypted EFLR: {file_logical_data.position}' + colorama.Style.RESET_ALL)
                        fout.write('\n')
                else:
                    eflr = EFLR.ExplicitlyFormattedLogicalRecord(file_logical_data.lr_type, file_logical_data.logical_data)
                    if dump_eflr and len(eflr_set_type) == 0 or eflr.set.type in eflr_set_type:
                        lines = str(eflr).split('\n')
                        for i, line in enumerate(lines):
                            if i == 0:
                                fout.write(colorama.Fore.MAGENTA + line + colorama.Style.RESET_ALL)
                            else:
                                fout.write(line)
                            fout.write('\n')
            else:
                # IFLR
                if dump_iflr:
                    if file_logical_data.lr_is_encrypted:
                        if kwargs['encrypted']:
                            if verbose:
                                fout.write(colorama.Fore.MAGENTA + f'Encrypted IFLR: {file_logical_data}' + colorama.Style.RESET_ALL)
                            else:
                                fout.write(colorama.Fore.MAGENTA + f'Encrypted IFLR: {file_logical_data.position}' + colorama.Style.RESET_ALL)
                            fout.write('\n')
                    else:
                        iflr = IFLR.IndirectlyFormattedLogicalRecord(file_logical_data.lr_type, file_logical_data.logical_data)
                        if len(iflr_set_type) == 0 or iflr.object_name.I in iflr_set_type:
                            fout.write(str(iflr))
                            fout.write('\n')


def _write_x_axis_summary(x_axis: XAxis.XAxis, fout: typing.TextIO) -> None:
    """Write out the XAxis summary."""
    fout.write('X Axis summary (all IFLRs):\n')
    fout.write(f'Min: {x_axis.summary.min} Max: {x_axis.summary.max} [{x_axis.units}] Count: {x_axis.summary.count}\n')
    fout.write('X Axis spacing summary:\n')
    if x_axis.summary.spacing is not None:
        fout.write(
            f'Min: {x_axis.summary.spacing.min} Max: {x_axis.summary.spacing.max}'
            f' Mean: {x_axis.summary.spacing.mean} Median: {x_axis.summary.spacing.median}\n'
        )
        fout.write(f'   Normal: {x_axis.summary.spacing.counts.norm}\n')
        fout.write(f'Duplicate: {x_axis.summary.spacing.counts.dupe}\n')
        fout.write(f'  Skipped: {x_axis.summary.spacing.counts.skip}\n')
        fout.write(f'     Back: {x_axis.summary.spacing.counts.back}\n')

    fout.write(f'Spacing histogram\n')
    fout.write(str(x_axis.summary.spacing.histogram_str()))
    fout.write('\n')


def _scan_log_pass_content(
        rp66_file: File.FileRead,
        logical_file: LogicalFile.LogicalFile,
        fout: typing.TextIO,
        *,
        frame_slice: Slice.Slice) -> None:
    """Scan the LogPass."""
    assert logical_file.has_log_pass
    lp: LogPass.LogPass = logical_file.log_pass
    frame_array: LogPass.FrameArray
    for fa, frame_array in enumerate(lp.frame_arrays):
        with _output_section_header_trailer(f'Frame Array [{fa}/{len(lp.frame_arrays)}]', '^', os=fout):
            fout.write(str(frame_array))
            fout.write('\n')
            num_frames = LogicalFile.populate_frame_array(
                rp66_file,
                logical_file,
                frame_array,
                frame_slice,
                None
            )
            if num_frames > 0:
                x_axis: XAxis.XAxis = logical_file.iflr_position_map[frame_array.ident]
                _write_x_axis_summary(x_axis, fout)
                if x_axis.summary.spacing is not None:
                    interval = f'{x_axis.summary.spacing.median:0.3f}'
                else:
                    interval = 'N/A'
                fout.write(
                    f'Frames [{len(x_axis)}]'
                    f' from: {float(x_axis[0].x_axis):0.3f}'
                    f' to {float(x_axis[-1].x_axis):0.3f}'
                    f' Interval: {interval}'
                    f' {frame_array.x_axis.units}'
                )
                fout.write('\n')
                fout.write(
                    f'Frame spacing: {frame_slice.long_str(len(x_axis))}'
                    f' number of frames: {num_frames}'
                    f' numpy size: {frame_array.sizeof_array:,d} bytes'
                )
                fout.write('\n')
                frame_table = [['Channel', 'Size', 'Absent', 'Min', 'Mean', 'Std.Dev.', 'Max', 'Units', 'dtype']]
                for channel in frame_array.channels:
                    channel_ident = channel.ident.I.decode("ascii")
                    # arr = channel.array
                    arr = AbsentValue.mask_absent_values(channel.array)
                    frame_table.append(
                        [channel_ident, arr.size,
                         # NOTE: Not the masked array!
                         AbsentValue.count_of_absent_values(channel.array),
                         arr.min(), arr.mean(),
                         arr.std(), arr.max(), channel.units, arr.dtype]
                    )
                fout.write('\n'.join(data_table.format_table(frame_table, heading_underline='-', pad='   ')))
                fout.write('\n')
            else:
                fout.write('No frames.')
            fout.write('\n')


def scan_RP66V1_file_data_content(fobj: typing.BinaryIO, fout: typing.TextIO,
                                  *, rp66v1_path: str, frame_slice: Slice.Slice, eflr_as_table: bool) -> None:
    """
    Scans all of every EFLR and IFLR in the file using a ScanFile object.
    """
    rp66v1_file = File.FileRead(fobj)
    logical_file_sequence = LogicalFile.LogicalIndex(rp66v1_file, rp66v1_path)
    with _output_section_header_trailer('RP66V1 File Data Summary', '*', os=fout):
        fout.write(str(logical_file_sequence.storage_unit_label))
        fout.write('\n')
        logical_file: LogicalFile.LogicalFile
        for lf, logical_file in enumerate(logical_file_sequence.logical_files):
            with _output_section_header_trailer(f'Logical File [{lf}/{len(logical_file_sequence.logical_files)}]', '=', os=fout):
                fout.write(str(logical_file))
                fout.write('\n')
                eflr_position: LogicalFile.PositionEFLR
                for e, eflr_position in enumerate(logical_file.eflrs):
                    header = f'EFLR [{e}/{len(logical_file.eflrs)}] at {str(eflr_position.lrsh_position)}'
                    with _output_section_header_trailer(header, '-', os=fout):
                        # fout.write(str(eflr_position.eflr))
                        # fout.write('\n')
                        if eflr_as_table:
                            if eflr_position.eflr.is_key_value():
                                eflr_str_table = eflr_position.eflr.key_values(
                                    stringify_function=stringify.stringify_object_by_type,
                                    sort=True
                                )
                            else:
                                eflr_str_table = eflr_position.eflr.table_as_strings(
                                    stringify_function=stringify.stringify_object_by_type,
                                    sort=True
                                )
                            fout.write('\n'.join(data_table.format_table(eflr_str_table, heading_underline='-')))
                            fout.write('\n')
                        else:
                            fout.write(eflr_position.eflr.str_long())
                        fout.write('\n')
                # Now the LogPass(s)
                if logical_file.has_log_pass:
                    with _output_section_header_trailer('Log Pass', '-', os=fout):
                        _scan_log_pass_content(rp66v1_file, logical_file, fout, frame_slice=frame_slice)
                else:
                    fout.write('NO Log Pass for this Logical Record\n')
