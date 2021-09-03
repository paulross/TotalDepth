#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation
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
This reads Dresser Atlas BIT files and writes LAS files.
"""
import logging
import os
import sys
import time
import typing

from TotalDepth.BIT import ReadBIT
from TotalDepth.LAS.core import WriteLAS
from TotalDepth.common import Slice, cmn_cmd_opts, colorama
from TotalDepth.util import bin_file_type, DirWalk

__author__ = 'Paul Ross'
__date__ = '2021-02-05'
__version__ = '0.1.0'
__rights__ = 'Copyright (c) 2021 Paul Ross. All rights reserved.'


LAS_PRODUCER_VERSION = '0.1.1'


logger = logging.getLogger(__file__)


def bit_frame_array_to_las_file(bit_frame_array: ReadBIT.BITFrameArray,
                                input_file: str,
                                logical_file_number: int,
                                frame_slice: typing.Optional[Slice.Slice],
                                channel_name_sub_set: typing.Set[str],
                                field_width: int,
                                float_format: str,
                                las_file: typing.TextIO) -> None:
    """Writes a single Frame Array to an open LAS file."""
    # Write the header
    WriteLAS.write_las_header(
        input_file, logical_file_number, 'TotalDepth.BIT.ToLAS', LAS_PRODUCER_VERSION,
        [['SOURCE_FORMAT.', 'WESTERN ATLAS BIT FORMAT', ': File format of Source file.']], las_file,
    )
    las_file.write('#\n')
    las_file.write(f'# Binary block A: {bit_frame_array.description}\n')
    las_file.write(f'# Binary block B: {bit_frame_array.unknown_b}\n')
    las_file.write(f'# BIT Log Pass (claimed): {bit_frame_array.bit_log_pass_range}\n')
    las_file.write('#\n')
    if bit_frame_array.frame_array is not None:
        frame_array = bit_frame_array.frame_array
        if frame_slice is None:
            frame_slice = Slice.Slice()
        else:
            # As we read the whole BIT file the array is not yet sliced. Do it now.
            for channel in frame_array:
                l = len(channel.array)
                channel.array = channel.array[frame_slice.first(l):frame_slice.last(l) + 1:frame_slice.step(l)]
        num_writable_frames = frame_slice.count(bit_frame_array.frame_count)
        # print('TRACE:', bit_frame_array.frame_count, num_writable_frames)
        if num_writable_frames:
            # Well information section. Not much to do here.
            # ~Well Information Section
            # #MNEM.UNIT  Value           Description
            # #---------  -----           -----------
            # STRT.FEET   2459.000        : START
            # STOP.FEET   2253.500        : STOP
            # STEP.FEET   -0.500          : STEP
            x_start = frame_array.x_axis.array[0][0]
            x_stop = frame_array.x_axis.array[-1][0]
            num_frames = len(frame_array.x_axis)
            x_spacing = (x_stop - x_start) / (num_frames - 1)
            table = [
                ['#MNEM.UNIT', 'DATA', 'DESCRIPTION', ],
                ['#----.----', '----', '-----------', ],
                [f'{"STRT":4}.{"    ":4}', f'{x_start}', f': {"START"}', ],
                [f'{"STOP":4}.{"    ":4}', f'{x_stop}', f': {"STOP"}',],
                [f'{"STRP":4}.{"    ":4}', f'{x_spacing}', f': {"STEP"}',],
            ]
            WriteLAS.write_table(table, '~Well Information Section', las_file)

            # Write the curve and array sections.
            WriteLAS.write_curve_and_array_section_to_las(bit_frame_array.frame_array, bit_frame_array.frame_count,
                'first', frame_slice, channel_name_sub_set, field_width, float_format, las_file,)


def single_bit_path_to_las_path(bit_path: str,
                                _array_reduction: str,
                                path_out: str,
                                frame_slice: Slice.Slice,
                                channels: typing.Set[str],
                                field_width: int,
                                float_format: str,
                                ) -> WriteLAS.LASWriteResult:
    """Given a path to BIT file this reads the file and writes out a LAS file for each frame array.
    The LAS file names are numbered sequentially."""
    output_size = 0
    las_count = 0
    t_start = time.perf_counter()
    has_exception = False
    binary_file_type = bin_file_type.binary_file_type_from_path(bit_path)
    logger.info('Found file type %s on path %s', binary_file_type, bit_path)
    if binary_file_type == 'BIT':
        logger.info('Reading BIT file %s', bit_path)
        with open(bit_path, 'rb') as bit_file:
            try:
                frame_arrays = ReadBIT.create_bit_frame_array_from_file(bit_file)
                for f, frame_array in enumerate(frame_arrays):
                    las_file_name = f'{path_out}_{f:04d}.las'
                    logger.info('Writing frame array %d to %s', f, las_file_name)
                    os.makedirs(os.path.dirname(las_file_name), exist_ok=True)
                    with open(las_file_name, 'w') as las_file:
                        bit_frame_array_to_las_file(
                            frame_array, bit_path, f, frame_slice, channels, field_width, float_format, las_file,
                        )
                    output_size += os.path.getsize(las_file_name)
                    las_count += 1
            except Exception as err:
                logger.exception('Could not process BIT to LAS')
                has_exception = True
            was_ignored = False
    else:
        was_ignored = True
    return WriteLAS.LASWriteResult(bit_path, binary_file_type, os.path.getsize(bit_path), output_size, las_count,
                                   time.perf_counter() - t_start, has_exception, was_ignored)


def _dump_frames_and_or_channels_single_bit_file(path_in: str, frame_slices: bool, channels: bool) -> None:
    """Write a summary of frames and channels from a single BIT file."""
    binary_file_type = bin_file_type.binary_file_type_from_path(path_in)
    if binary_file_type == 'BIT':
        logger.info(f'Reading BIT {path_in}')
        try:
            with colorama.section(f'File {path_in}', '=', out_stream=sys.stdout):
                with open(path_in, 'rb') as bit_file:
                    bit_frame_arrays = ReadBIT.create_bit_frame_array_from_file(bit_file)
                    for bit_frame_array in bit_frame_arrays:
                        if bit_frame_array.frame_array is not None:
                            frame_array = bit_frame_array.frame_array
                            print(f'  Frame Array: {frame_array.ident}')
                            if channels:
                                channel_text = ','.join(f'"{c.ident}"' for c in frame_array.channels)
                                print(f'  Channels: {channel_text}')
                            if frame_slices:
                                print(f'  X axis: {frame_array.x_axis}')
                                x_start = frame_array.x_axis.array[0][0]
                                x_stop = frame_array.x_axis.array[-1][0]
                                num_frames = len(frame_array.x_axis)
                                x_spacing = (x_stop - x_start) / (num_frames - 1)
                                print(
                                    f'  Frames: {num_frames}'
                                    f' from {x_start}'
                                    f' to {x_stop}'
                                    f' interval {x_spacing}'
                                    f' [{frame_array.x_axis.units}]'
                                )
                        print()
        except ReadBIT.ExceptionTotalDepthBIT:  # pragma: no cover
            logger.exception(f'Failed to index with ExceptionTotalDepthBIT: {path_in}')
        except Exception:  # pragma: no cover
            logger.exception(f'Failed to index with Exception: {path_in}')


def _dump_frames_and_or_channels(path_in: str, recurse: bool, frame_slice: str, channels: str) -> None:
    """Dump available channels and frames."""
    assert frame_slice == '?' or channels == '?'
    if os.path.isdir(path_in):
        for file_in_out in DirWalk.dirWalk(path_in, '', theFnMatch='', recursive=recurse, bigFirst=False):
            _dump_frames_and_or_channels_single_bit_file(file_in_out.filePathIn, frame_slice == '?', channels == '?')
    else:
        _dump_frames_and_or_channels_single_bit_file(path_in, frame_slice == '?', channels == '?')


def main() -> int:
    """Main entry point."""
    print('Cmd: %s' % ' '.join(sys.argv))
    description = """usage: %(prog)s [options] file
Reads Western Atlas BIT file(s) and writes them out as LAS files."""
    parser = WriteLAS.las_writer_command_line_arguments(description, prog='TotalDepth.BIT.ToLAS.main',
                                                        version=__version__, epilog=__rights__)
    args = parser.parse_args()
    cmn_cmd_opts.set_log_level(args)
    # Your code here
    ret_val = 0
    if args.frame_slice.strip() == '?' or args.channels.strip() == '?':
        _dump_frames_and_or_channels(args.path_in, args.recurse, args.frame_slice.strip(), args.channels.strip())
    else:
        clk_start = time.perf_counter()
        result: typing.Dict[str, WriteLAS.LASWriteResult] = WriteLAS.process_to_las(args, single_bit_path_to_las_path)
        clk_exec = time.perf_counter() - clk_start
        _failed_file_count = WriteLAS.report_las_write_results_and_performance(result, clk_exec, args.gnuplot, include_ignored=False)
    print('Bye, bye!')
    return ret_val


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
