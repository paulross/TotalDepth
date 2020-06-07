"""
Scans a RP66V1 file an prints out the summary.

This produces text output at various levels of encapsulation:

    --VR ~ Visible Records only.
    --LRSH ~ Logical Record segments.
    --LD ~ Logical data i.e. all Logical Record segments concatenated for each Logical Record.
    --EFLR ~ Explicitly Formatted Logical Records.
    --IFLR ~ Implicitly Formatted Logical Records.
    --LR ~ All data, including frame data from all Logical Records.

"""
import argparse
import collections
import contextlib
import logging
import os
import pprint
import sys
import time
import typing

import colorama

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import AbsentValue
from TotalDepth.RP66V1.core import File
from TotalDepth.RP66V1.core import LogPass
from TotalDepth.RP66V1.core import LogicalFile
from TotalDepth.RP66V1.core import XAxis
from TotalDepth.RP66V1.core import stringify
from TotalDepth.RP66V1.core.LogicalRecord import EFLR
from TotalDepth.RP66V1.core.LogicalRecord import IFLR
from TotalDepth.common import Rle, statistics
from TotalDepth.common import Slice
from TotalDepth.common import data_table
from TotalDepth.util import bin_file_type
from TotalDepth.util import gnuplot
from TotalDepth.util.DirWalk import dirWalk
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
        with File.FileRead(fobj) as rp66_file:
            vr_position = lr_position = 0
            count_vr = 0
            count_lrsh = 0
            count_lrsh_first = 0
            count_lrsh_type = {
                'EFLR': collections.Counter(),
                'IFLR': collections.Counter(),
            }
            count_lrsh_length = statistics.LengthDict()
            lrsh_first_last = {
                (False, False): 0,
                (False, True): 0,
                (True, False): 0,
                (True, True): 0,
            }
            rle_visible_record_positions = Rle.RLE()
            rle_lrsh_positions = Rle.RLE()
            for visible_record in rp66_file.iter_visible_records():
                vr_stride = visible_record.position - vr_position
                rle_visible_record_positions.add(visible_record.position)
                if verbose:
                    fout.write(f'{visible_record} Stride: 0x{vr_stride:08x} {vr_stride:6,d}\n')
                if lrsh_dump:
                    for lrsh in rp66_file.iter_LRSHs_for_visible_record(visible_record):
                        count_lrsh_length.add(lrsh.length)
                        if lrsh.attributes.is_first:
                            rle_lrsh_positions.add(lrsh.position)
                            count_lrsh_first += 1
                            if lrsh.attributes.is_eflr:
                                count_lrsh_type['EFLR'].update([lrsh.record_type])
                            else:
                                count_lrsh_type['IFLR'].update([lrsh.record_type])
                            output = colorama.Fore.GREEN + f' {lrsh}'
                        elif lrsh.attributes.is_last:
                            output = colorama.Fore.RED + f'  --{lrsh}'
                        else:
                            output = colorama.Fore.YELLOW + f'  ..{lrsh}'
                        if verbose:
                            lr_stride = lrsh.position - lr_position
                            fout.write(f'  {output} Stride: 0x{lr_stride:08x} {lr_stride:6,d}\n')
                        lr_position = lrsh.position
                        lrsh_first_last[(lrsh.attributes.is_first, lrsh.attributes.is_last)] += 1
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
                    with _output_section_header_trailer('Summary of Logical Record Types', '-', os=fout):
                        fout.write(f'LRSH: record types and counts (first segments only):\n')
                        for flr_type in ('EFLR', 'IFLR'):
                            fout.write(f'Count of Logical Record types for "{flr_type}" [{len(count_lrsh_type[flr_type])}]:\n')
                            for record_type in sorted(count_lrsh_type[flr_type].keys()):
                                fout.write(f'{record_type:3d} : {count_lrsh_type[flr_type][record_type]:8,d}\n')
                    with _output_section_header_trailer('Summary of LRSH Lengths', '-', os=fout):
                        fout.write(
                            f'LRSH: record lengths and counts (all segments)'
                            f' [{len(count_lrsh_length)}]'
                        )
                        if len(count_lrsh_length):
                            fout.write(f' range: {min(count_lrsh_length.keys())}...{max(count_lrsh_length.keys())}')
                        fout.write(f'\n')
                        fout.write('\n'.join(count_lrsh_length.histogram_power_of_2()))
                        fout.write(f'\n')
                    with _output_section_header_trailer('Summary of LRSH First/last', '-', os=fout):
                        fout.write(f'{"(First, Last)":16} : {"Count":8}\n')
                        for k in sorted(lrsh_first_last.keys()):
                            fout.write(f'{str(k):16} : {lrsh_first_last[k]:8d}\n')
                    if verbose:
                        with _output_section_header_trailer('RLE LRSH Position', '-', os=fout):
                            _write_position_rle(rle_lrsh_positions, fout)
                        for length in sorted(count_lrsh_length.keys()):
                            fout.write(f'{length:3d} : {count_lrsh_length[length]:8,d}\n')


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
        with File.FileRead(fobj) as rp66_file:
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
    iflr_dump = kwargs.get('iflr_dump', 0)
    iflr_set_type = kwargs.get('iflr_set_type', [])
    # TODO: Use both of these
    # dump_bytes = kwargs.get('dump_bytes', 0)
    # dump_raw_bytes = kwargs.get('dump_raw_bytes', 0)
    # if not dump_bytes:
    #     fout.write(colorama.Fore.YELLOW  + 'Use -v and --dump-bytes to see actual first n bytes.\n')
    with _output_section_header_trailer('RP66V1 EFLR and IFLR Data Summary', '*', os=fout):
        with File.FileRead(fobj) as rp66_file:
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
            eflr_count = iflr_count = 0
            eflr_set_type_count = collections.defaultdict(int)
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
                    eflr_count += 1
                    eflr_set_type_count[eflr.set.type] +=1
                else:
                    # IFLR
                    if iflr_dump and verbose:
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
                    iflr_count += 1
            fout.write(f'Records counted in this run: EFLR: {eflr_count} IFLR: {iflr_count}\n')
            # Pretty print histogram of EFLR set types
            if len(eflr_set_type_count):
                fw = max(len(repr(k)) for k in eflr_set_type_count)
                fout.write(f'EFLR count of Set Type(s) [{len(eflr_set_type_count)}]:\n')
                for k in sorted(eflr_set_type_count.keys()):
                    fout.write(f'{k!r:{fw}}: {eflr_set_type_count[k]:6d}\n')
            else:
                fout.write(f'EFLR count of Set Type(s) {len(eflr_set_type_count)}:\n{pprint.pformat(eflr_set_type_count)}\n')


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
        logical_index: LogicalFile.LogicalIndex,
        logical_file_index: int,
        fout: typing.TextIO,
        *,
        frame_slice: Slice.Slice) -> None:
    """Scan the LogPass."""
    assert logical_index[logical_file_index].has_log_pass
    logical_file = logical_index[logical_file_index]
    lp: LogPass.LogPass = logical_file.log_pass
    frame_array: LogPass.FrameArray
    for fa, frame_array in enumerate(lp.frame_arrays):
        with _output_section_header_trailer(f'Frame Array [{fa}/{len(lp.frame_arrays)}]', '^', os=fout):
            fout.write(str(frame_array))
            fout.write('\n')
            num_frames = logical_file.populate_frame_array(
                frame_array,
                frame_slice,
            )
            if num_frames > 0:
                x_axis: XAxis.XAxis = logical_index[logical_file_index].iflr_position_map[frame_array.ident]
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
    with LogicalFile.LogicalIndex(fobj) as logical_index:
        with _output_section_header_trailer('RP66V1 File Data Summary', '*', os=fout):
            fout.write(str(logical_index.storage_unit_label))
            fout.write('\n')
            logical_file: LogicalFile.LogicalFile
            for lf, logical_file in enumerate(logical_index.logical_files):
                with _output_section_header_trailer(f'Logical File [{lf}/{len(logical_index.logical_files)}]', '=', os=fout):
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
                            _scan_log_pass_content(logical_index, lf, fout, frame_slice=frame_slice)
                    else:
                        fout.write('NO Log Pass for this Logical Record\n')


def dump_RP66V1_test_data(fobj: typing.BinaryIO, fout: typing.TextIO, **kwargs) -> None:
    """Scans the file reporting Visible Records, optionally Logical Record Segments as well."""
    with _output_section_header_trailer('File as Raw Test Data', '*', os=fout):
        with File.FileRead(fobj) as rp66_file:
            count_vr = 0
            count_lrsh = 0
            count_lrsh_first = 0
            fout.write(f'{rp66_file.sul.as_bytes()}  # Storage Unit Label\n')
            for visible_record in rp66_file.iter_visible_records():
                fout.write(
                    f'{visible_record.as_bytes()}'
                    f'  # Visible record [{count_vr}]'
                    f' at 0x{visible_record.position:x}'
                    f' length 0x{visible_record.length:x}'
                    f' version 0x{visible_record.version:x}\n'
                )
                for lrsh, by in rp66_file.iter_LRSHs_for_visible_record_and_logical_data_fragment(visible_record):
                    record_type = 'E' if lrsh.attributes.is_eflr else 'I'
                    fout.write(
                        f'    {lrsh.as_bytes()}'
                        f'  # LRSH [{count_lrsh_first}/{count_lrsh}] 0x{lrsh.position:x} {record_type} len: {lrsh.length}'
                        f' first: {lrsh.attributes.is_first} last: {lrsh.attributes.is_last}\n'
                    )
                    # fout.write(f'        {by} # Logical data length {len(by)} 0x{len(by):x}\n')
                    WIDTH = 20
                    # str_list = []
                    # for i in range(0, len(by), WIDTH):
                    #     str_list.append(f'{by[i:i+WIDTH]}')
                    str_list = [f'{by[i:i+WIDTH]}' for i in range(0, len(by), WIDTH)]
                    if len(str_list) > 1:
                        fout.write(f'        # Logical data length {len(by)} 0x{len(by):x}\n')
                        FW = max(len(s) for s in str_list)
                        for i, s in enumerate(str_list):
                            fout.write(
                                f'        {s:{FW}}  # Chunk from {i * WIDTH}\n'
                            )
                    else:
                        fout.write(f'        {by} # Logical data length {len(by)} 0x{len(by):x}\n')
                    if lrsh.attributes.is_first:
                        count_lrsh_first += 1
                    elif lrsh.attributes.is_last:
                        pass
                    else:
                        pass
                    count_lrsh += 1
                count_vr += 1


# TODO: IndexFile and ScanFile are very similar, combine.
IndexResult = collections.namedtuple('IndexResult', 'size_input, size_output, time, exception, ignored')


def scan_a_single_file(path_in: str, path_out: str, output_extension: str, function: typing.Callable, **kwargs) -> IndexResult:
    # logging.info(f'index_a_single_file(): "{path_in}" to "{path_out}"')
    binary_file_type = bin_file_type.binary_file_type_from_path(path_in)
    if binary_file_type == 'RP66V1':
        logger.info(f'Scanning "{path_in}" to "{path_out}"')
        with open(path_in, 'rb') as fobj:
            t_start = time.perf_counter()
            try:
                if path_out:
                    file_path_out = path_out + output_extension
                    out_dir = os.path.dirname(path_out)
                    if not os.path.exists(out_dir):
                        logger.info(f'Making directory: {out_dir}')
                        os.makedirs(out_dir, exist_ok=True)
                    with open(file_path_out, 'w') as fout:
                        function(fobj, fout, **kwargs)
                    len_scan_output = os.path.getsize(file_path_out)
                else:
                    function(fobj, sys.stdout, **kwargs)
                    len_scan_output = -1
                result = IndexResult(
                    os.path.getsize(path_in),
                    len_scan_output,
                    time.perf_counter() - t_start,
                    False,
                    False,
                )
                return result
            except ExceptionTotalDepthRP66V1:
                logger.exception(f'Failed to index with ExceptionTotalDepthRP66V1: {path_in}')
                return IndexResult(os.path.getsize(path_in), 0, 0.0, True, False)
            except Exception:
                logger.exception(f'Failed to index with Exception: {path_in}')
                return IndexResult(os.path.getsize(path_in), 0, 0.0, True, False)
    logger.info(f'Ignoring file type "{binary_file_type}" at {path_in}')
    return IndexResult(0, 0, 0.0, False, True)


def scan_dir_or_file(path_in: str,
                     path_out: str,
                     function: typing.Callable,
                     recurse: bool,
                     output_extension: str,
                     **kwargs) -> typing.Dict[str, IndexResult]:
    logging.info(f'scan_dir_or_file(): "{path_in}" to "{path_out}" with {function} recurse: {recurse}')
    ret = {}
    if os.path.isdir(path_in):
        for file_in_out in dirWalk(path_in, path_out, theFnMatch='', recursive=recurse, bigFirst=False):
            # print(file_in_out)
            ret[file_in_out.filePathIn] = scan_a_single_file(
                file_in_out.filePathIn, file_in_out.filePathOut, output_extension, function, **kwargs
            )
    else:
        ret[path_in] = scan_a_single_file(path_in, path_out, output_extension, function, **kwargs)
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
set y2label "Scan time (s), Ratio original size / index size"
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
set output "{name}.svg" # choose the output device

# set key off

#set key title "Window Length"
#  lw 2 pointsize 2

# Fields: size_input, size_index, time, exception, ignored, path

#plot "{name}.dat" using 1:3 axes x1y1 title "Scan Time (s)" lt 1 w points

plot "{name}.dat" using 1:($3*1000/($1/(1024*1024))) axes x1y1 title "Scan Rate (ms/Mb), left axis" lt 1 w points, \\
    rate(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", a, b) lt 1 lw 2, \\
    "{name}.dat" using 1:3 axes x1y2 title "Scan Time (s), right axis" lt 4 w points, \\
    "{name}.dat" using 1:($1/$2) axes x1y2 title "Original Size / Scan size, right axis" lt 3 w points, \\
    compression_ratio(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", e, f) axes x1y2 lt 3 lw 2

# Plot size ratio:
#    "{name}.dat" using 1:($2/$1) axes x1y2 title "Index size ratio" lt 3 w points, #     size_ratio(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", c, d) axes x1y2 lt 3 lw 2

reset
"""


def plot_gnuplot(data: typing.Dict[str, IndexResult], gnuplot_dir: str) -> None:
    if len(data) < 2:
        raise ValueError(f'Can not plot data with only {len(data)} points.')
    # First row is header row, create it then comment out the first item.
    table = [
        list(IndexResult._fields) + ['Path']
    ]
    table[0][0] = f'# {table[0][0]}'
    for k in sorted(data.keys()):
        if data[k].size_input > 0 and not data[k].exception:
            table.append(list(data[k]) + [k])
    name = 'ScanFile'
    return_code = gnuplot.invoke_gnuplot(gnuplot_dir, name, table, GNUPLOT_PLT.format(name=name))
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')
    return_code = gnuplot.write_test_file(gnuplot_dir, 'svg')
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')


def main() -> int:
    description = 'usage: %(prog)s [options] file'
    description = """Scans a RP66V1 file and dumps data about the file to stdout.
    This is useful for examining the details of RP66V1 files and can dump data at various levels of encapsulation,
    from the lowest level upwards:
    --VR ~ Visible Records only.
    --LRSH ~ Logical Record segments.
    --LD ~ Logical data i.e. all Logical Record segments concatenated for each Logical Record.
    --EFLR ~ Explicitly Formatted Logical Records.
    --IFLR ~ Implicitly Formatted Logical Records.
    --LR ~ All data, including the numerical analysis of frame data.
    If these are combined then the input is scanned multiple times.
    """
    print('Cmd: %s' % ' '.join(sys.argv))
    # TODO: Use cmn_cmd_opts
    parser = argparse.ArgumentParser(
        description=description,
        epilog=__rights__,
        prog=sys.argv[0],
    )
    parser.add_argument('path_in', type=str, help='Path to the input file or directory.')
    parser.add_argument(
        'path_out', type=str, default='', nargs='?', help='Path to the output scan to write [default: stdout].'
    )
    parser.add_argument(
        '-V', '--VR', action='store_true',
        help='Dump the Visible Records. [default: %(default)s]',
    )
    parser.add_argument(
        '-L', '--LRSH', action='store_true',
        help='Summarise the Visible Records and the Logical Record'
             ' Segment Headers, use -v to dump records. [default: %(default)s]',
    )
    parser.add_argument(
        '-D', '--LD', action='store_true',
        help='Summarise logical data, use -v to dump records.'
             ' See also --dump-bytes, --dump-raw-bytes. [default: %(default)s]',
    )
    parser.add_argument(
        '-E', '--EFLR', action='store_true',
        help='Dump EFLR Set. [default: %(default)s]',
    )
    parser.add_argument(
        "--eflr-set-type", action='append', default=[],
        help="List of EFLR Set Types to output, additive, if absent then dump all. [default: %(default)s]",
    )
    parser.add_argument(
        '-I', '--IFLR', action='store_true',
        help='Dump IFLRs. [default: %(default)s]',
    )
    parser.add_argument(
        "--iflr-set-type", action='append', default=[],
        help="List of IFLR Set Types to output, additive, if absent then dump all. [default: %(default)s]",
    )
    parser.add_argument(
        '-R', '--LR', action='store_true',
        help='Dump all data, including frame data from Logical Records. [default: %(default)s]',
    )
    parser.add_argument(
        '-d', '--dump-bytes', type=int, default=0,
        help='Dump X leading raw bytes for certain options, if -1 all bytes are dumped. [default: %(default)s]',
    )
    parser.add_argument(
        '--dump-raw-bytes', action='store_true',
        help='Dump the raw bytes for certain options in raw format,'
             ' otherwise Hex format is used. [default: %(default)s]',
    )
    parser.add_argument(
        '-r', '--recurse', action='store_true',
        help='Process files recursively. [default: %(default)s]',
    )
    parser.add_argument(
        '-e', '--encrypted', action='store_true',
        help='Output encrypted Logical Records as well. [default: %(default)s]',
    )
    parser.add_argument(
        '-k', '--keep-going', action='store_true',
        help='Keep going as far as sensible. [default: %(default)s]',
    )
    Slice.add_frame_slice_to_argument_parser(parser, help_prefix='NOTE: Requires -R, --LR.')
    parser.add_argument(
        '--eflr-as-table', action='store_true',
        help='When with --LR and not --html then dump EFLRs as tables, otherwise every EFLR object.'
             ' [default: %(default)s]',
    )
    log_level_help_mapping = ', '.join(
        ['{:d}<->{:s}'.format(level, logging._levelToName[level]) for level in sorted(logging._levelToName.keys())]
    )
    log_level_help = f'Log Level as an integer or symbol. ({log_level_help_mapping}) [default: %(default)s]'
    parser.add_argument(
            "-l", "--log-level",
            # type=int,
            # dest="loglevel",
            default=30,
            help=log_level_help
        )
    parser.add_argument(
        "-v", "--verbose", action='count', default=0,
        help="Increase verbosity, additive [default: %(default)s]",
    )
    gnuplot.add_gnuplot_to_argument_parser(parser)
    parser.add_argument(
        '-T', '--test-data', action='store_true',
        help='Dump the file as annotated bytes, useful for creating test data. [default: %(default)s]',
    )

    args = parser.parse_args()
    print('args:', args)

    # Extract log level
    if args.log_level in logging._nameToLevel:
        log_level = logging._nameToLevel[args.log_level]
    else:
        log_level = int(args.log_level)
    # print('Log level:', log_level)
    # Initialise logging etc.
    logging.basicConfig(level=log_level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        #datefmt='%y-%m-%d % %H:%M:%S',
                        stream=sys.stdout)
    clk_start = time.perf_counter()
    # return 0
    # Your code here
    result: typing.Dict[str, IndexResult] = {}
    output_extension = '.txt'
    if args.VR or args.LRSH:
        result = scan_dir_or_file(
            args.path_in,
            args.path_out,
            scan_RP66V1_file_visible_records,
            args.recurse,
            output_extension,
            # kwargs passed to scanning function
            lrsh_dump=args.LRSH,
            verbose=args.verbose,
        )
    if args.LD:
        result = scan_dir_or_file(
            args.path_in,
            args.path_out,
            scan_RP66V1_file_logical_data,
            args.recurse,
            output_extension,
            # kwargs passed to scanning function
            dump_bytes=args.dump_bytes,
            dump_raw_bytes=args.dump_raw_bytes,
            verbose=args.verbose,
        )
    if args.EFLR or args.IFLR:
        result = scan_dir_or_file(
            args.path_in,
            args.path_out,
            scan_RP66V1_file_EFLR_IFLR,
            args.recurse,
            output_extension,
            # kwargs passed to scanning function
            verbose=args.verbose,
            encrypted=args.encrypted,
            keep_going=args.keep_going,
            eflr_set_type=[bytes(v, 'ascii') for v in args.eflr_set_type],
            iflr_set_type=[bytes(v, 'ascii') for v in args.iflr_set_type],
            iflr_dump=args.IFLR,
            eflr_dump=args.EFLR,
            rp66v1_path=args.path_in,
        )
    if args.LR:
        result = scan_dir_or_file(
            args.path_in,
            args.path_out,
            scan_RP66V1_file_data_content,
            args.recurse,
            output_extension,
            rp66v1_path=args.path_in,
            frame_slice=Slice.create_slice_or_sample(args.frame_slice),
            eflr_as_table=args.eflr_as_table,
        )
    if args.test_data:
        result = scan_dir_or_file(
            args.path_in,
            args.path_out,
            dump_RP66V1_test_data,
            args.recurse,
            output_extension,
            verbose=args.verbose,
        )
    clk_exec = time.perf_counter() - clk_start
    size_scan = size_input = 0
    failures = 0
    files_processed = 0
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
        if idx_result.exception:
            failures += 1
    if args.gnuplot:
        plot_gnuplot(result, args.gnuplot)
    if size_input > 0:
        ms_mb = clk_exec * 1000 / (size_input / 1024**2)
    else:
        ms_mb = 0.0
    print('Execution time = %8.3f (S)' % clk_exec)
    print(f'Processed {len(result):,d} files and {size_input:,d} bytes, {ms_mb:.1f} ms/Mb')
    print('Bye, bye!')
    return failures


if __name__ == '__main__':
    sys.exit(main())
