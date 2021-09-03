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
import argparse
import datetime
import logging
import multiprocessing
import os
import re
import sys
import typing

import numpy as np

import TotalDepth.common
from TotalDepth.common import data_table, Slice, cmn_cmd_opts, process
from TotalDepth.common.LogPass import FrameArray
from TotalDepth.util import DirWalk, gnuplot


logger = logging.getLogger(__file__)


class LASWriteArguments(typing.NamedTuple):
    path_in: str
    path_out: str
    array_reduction: str
    frame_slice: typing.Union[TotalDepth.common.Slice.Slice, TotalDepth.common.Slice.Sample]
    channels: typing.Set[str]
    field_width: int
    float_format: str


class LASWriteResult(typing.NamedTuple):
    """Holds the result of processing a file to LAS."""
    path_input: str
    binary_file_type: str
    size_input: int
    size_output: int
    las_count: int
    time: float
    exception: bool
    ignored: bool


#: Format for time as UTC
LAS_DATETIME_FORMAT_UTC = '%Y-%m-%d %H:%M:%S.%f UTC'
#: Format for time as text
LAS_DATE_FORMAT_TEXT = 'YYYY-mm-dd HH MM SS.us UTC'


def write_las_header(input_file: str,
                     logical_file_number: int,
                     las_producer_program: str,
                     las_producer_version: str,
                     table_extend: typing.List[typing.List[str]],
                     output_stream: typing.TextIO,
                     ) -> None:
    """Writes the LAS opening such as::

        ~Version Information Section
        VERS.           2.0                           : CWLS Log ASCII Standard - VERSION 2.0
        WRAP.           NO                            : One Line per depth step
        PROD.           TotalDepth                    : LAS Producer
        PROG.           TotalDepth.RP66V1.ToLAS 0.1.1 : LAS Program name and version
        CREA.           2012-11-14 10:50              : LAS Creation date [YYYY-MMM-DD hh:mm]
        SOURCE.         SOME-FILE-NAME.dlis           : Source File Name
        LOGICAL-FILE.   3                             : Logical File number in the Source file

    Or, with extensions:
        ~Version Information Section
        VERS.           2.0                           : CWLS Log ASCII Standard - VERSION 2.0
        WRAP.           NO                            : One Line per depth step
        PROD.           TotalDepth                    : LAS Producer
        PROG.           TotalDepth.RP66V1.ToLAS 0.1.1 : LAS Program name and version
        CREA.           2012-11-14 10:50              : LAS Creation date [YYYY-MMM-DD hh:mm]
        DLIS_CREA.      2012-11-10 22:06              : DLIS Creation date and time [YYYY-MMM-DD hhmm]
        SOURCE.         SOME-FILE-NAME.dlis           : Source File Name
        LOGICAL-FILE.   3                             : Logical File number in the Source file
        FILE-ID.        SOME-FILE-ID                  : File Identification from the FILE-HEADER Logical Record
        FRAME-ARRAY.    60B                           : Identity of the Frame Array in the Logical File

    Reference: [LAS2.0 Las2_Update_Feb2017.pdf Section 5.3 ~V (Version Information)]
    """
    now = datetime.datetime.utcnow()
    table: typing.List[typing.List[str]] = [
        ['VERS.', '2.0', ': CWLS Log ASCII Standard - VERSION 2.0'],
        ['WRAP.', 'NO', ': One Line per depth step'],
        ['PROD.', 'TotalDepth', ': LAS Producer'],
        ['PROG.', f'{las_producer_program} {las_producer_version}', ': LAS Program name and version'],
        ['CREA.', f'{now.strftime(LAS_DATETIME_FORMAT_UTC)}', f': LAS Creation date [{LAS_DATE_FORMAT_TEXT}]'],
        ['SOURCE.', f'{os.path.basename(input_file)}', ': Source File Name'],
        ['LOGICAL-FILE.', f'{logical_file_number:d}', ': Logical File number in the Source file'],
    ]
    table.extend(table_extend)
    write_table(table, '~Version Information Section', output_stream)


class UnitValueDescription(typing.NamedTuple):
    """Class for accumulating data from PARAMETER tables and Well Information sections."""
    unit: str
    # value and description can not have:
    # A ':' in it as that will be treated as a seperator.
    # NOTE: An '#' in it is allowed as the comments are whitespace, '#' ...
    # See Section 5.1 of "LAS Version 2.0: A Digital Standard for Logs, Update February 2017"
    val: str
    desc: str

    @property
    def value(self) -> str:
        return self.val.replace(':', ' ')

    @property
    def description(self) -> str:
        return self.desc.replace(':', ' ')


def write_table(table: typing.Sequence[typing.Sequence[typing.Any]], title: str, ostream: typing.TextIO) -> None:
    rows = TotalDepth.common.data_table.format_table(table, pad='  ', left_flush=True)
    ostream.write(f'{title}\n')
    for row in rows:
        ostream.write(row.rstrip())
        ostream.write('\n')


def convert_dir_or_file_to_las_multiprocessing(
        dir_in: str,
        dir_out: str,
        recurse: bool,
        array_reduction: str,
        frame_slice: TotalDepth.common.Slice.Slice,
        channels: typing.Set[str],
        field_width: int,
        float_format: str,
        jobs: int,
        file_conversion_function: typing.Callable,
) -> typing.Dict[str, LASWriteResult]:
    """Multiprocessing code to LAS.
    Returns a dict of {path_in : LASWriteResult, ...}"""
    assert os.path.isdir(dir_in)
    if jobs < 1:
        jobs = multiprocessing.cpu_count()
    logging.info('scan_dir_multiprocessing(): Setting multi-processing jobs to %d' % jobs)
    pool = multiprocessing.Pool(processes=jobs)
    tasks = [
        (t.filePathIn, array_reduction, t.filePathOut, frame_slice, channels, field_width, float_format)
        for t in DirWalk.dirWalk(
            dir_in, dir_out, theFnMatch='', recursive=recurse, bigFirst=True
        )
    ]
    results = [
        r.get() for r in [
            pool.apply_async(file_conversion_function, t) for t in tasks
        ]
    ]
    return {r.path_input: r for r in results}


def convert_dir_or_file_to_las(
        path_in: str,
        path_out: str,
        recurse: bool,
        array_reduction: str,
        frame_slice: TotalDepth.common.Slice.Slice,
        channels: typing.Set[str],
        field_width: int,
        float_format: str,
        file_conversion_function: typing.Callable,
) -> typing.Dict[str, LASWriteResult]:
    """Convert a directory or file to a set of LAS files."""
    logging.info(f'index_dir_or_file(): "{path_in}" to "{path_out}" recurse: {recurse}')
    ret = {}
    try:
        if os.path.isdir(path_in):
            for file_in_out in DirWalk.dirWalk(path_in, path_out, theFnMatch='', recursive=recurse, bigFirst=False):
                ret[file_in_out.filePathIn] = file_conversion_function(
                    file_in_out.filePathIn, array_reduction, file_in_out.filePathOut, frame_slice, channels,
                    field_width, float_format
                )
        else:
            ret[path_in] = file_conversion_function(
                path_in, array_reduction, path_out, frame_slice, channels, field_width, float_format
            )
    except KeyboardInterrupt:  # pragma: no cover
        logger.critical('Keyboard interrupt, last file is probably incomplete or corrupt.')
    return ret


STANDARD_TEXT_WIDTH = 132


def process_to_las(args: argparse.PARSER, file_conversion_function: typing.Callable) -> typing.Dict[str, LASWriteResult]:
    result: typing.Dict[str, LASWriteResult] = {}
    # if os.path.isfile(args.path_in) and (args.frame_slice.strip() == '?' or args.channels.strip() == '?'):
    logger.info(f'process_to_las(): {args}')
    channel_set = set()
    for ch in args.channels.strip().split(','):
        if ch.strip() != '':
            channel_set.add(ch.strip())
    if TotalDepth.common.cmn_cmd_opts.multiprocessing_requested(args) and os.path.isdir(args.path_in):
        result = convert_dir_or_file_to_las_multiprocessing(
            args.path_in,
            args.path_out,
            args.recurse,
            args.array_reduction,
            TotalDepth.common.Slice.create_slice_or_sample(args.frame_slice),
            channel_set,
            args.field_width,
            args.float_format,
            args.jobs,
            file_conversion_function,
        )
    else:
        if args.log_process > 0.0:
            # FIXME: log_level
            log_level = 40
            with TotalDepth.common.process.log_process(args.log_process, log_level):
                result = convert_dir_or_file_to_las(
                    args.path_in,
                    args.path_out,
                    args.recurse,
                    args.array_reduction,
                    TotalDepth.common.Slice.create_slice_or_sample(args.frame_slice),
                    channel_set,
                    args.field_width,
                    args.float_format,
                    file_conversion_function,
                )
        else:
            result = convert_dir_or_file_to_las(
                args.path_in,
                args.path_out,
                args.recurse,
                args.array_reduction,
                TotalDepth.common.Slice.create_slice_or_sample(args.frame_slice),
                channel_set,
                args.field_width,
                args.float_format,
                file_conversion_function,
            )
    return result


def las_size_input_output(result: typing.Dict[str, LASWriteResult]) -> typing.Tuple[int, int]:
    size_input = size_output = 0
    for path in result:
        size_input += result[path].size_input
        size_output += result[path].size_output
    return size_input, size_output


def report_las_write_results(result: typing.Dict[str, LASWriteResult], gnuplot: str, include_ignored=True,
                             out_stream: typing.TextIO = sys.stdout) -> int:
    """Print output returning the number of failed files"""
    size_index = size_input = 0
    files_failed = files_processed = 0
    if result:
        table = [
            ['Input', 'Type', 'Output', 'LAS Count', 'Time', 'Ratio', 'ms/Mb', 'Exception', 'Path']
        ]
        for path in sorted(result.keys()):
            las_result = result[path]
            if las_result.ignored and not include_ignored:
                continue
            if las_result.size_input > 0:
                ms_mb = las_result.time * 1000 / (las_result.size_input / 1024 ** 2)
                ratio = las_result.size_output / las_result.size_input
                out = [
                    f'{las_result.size_input:,d}',
                    f'{las_result.binary_file_type:8}',
                    f'{las_result.size_output:,d}',
                    f'{las_result.las_count:,d}',
                    f'{las_result.time:.3f}',
                    f'{ratio:.1%}',
                    f'{ms_mb:.1f}',
                    f'{str(las_result.exception)}',
                    f'"{path}"',
                ]
                table.append(out)
                # print(' '.join(out))
                size_input += result[path].size_input
                size_index += result[path].size_output
                files_processed += 1
                if las_result.exception:
                    files_failed += 1
        for row in TotalDepth.common.data_table.format_table(table, pad=' ', heading_underline='-'):
            out_stream.write(row)
            out_stream.write('\n')
        try:
            if gnuplot:
                plot_gnuplot(result, gnuplot)
        except Exception as err:  # pragma: no cover
            logger.exception(str(err))
            ret_val = -1
        # print('Execution time = %8.3f (S)' % clk_exec)
        # if size_input > 0:
        #     ms_mb = clk_exec * 1000 / (size_input/ 1024**2)
        #     ratio = size_index / size_input
        # else:
        #     ms_mb = 0.0
        #     ratio = 0.0
        # print(f'Out of  {len(result):,d} processed {files_processed:,d} files of total size {size_input:,d} input bytes')
        # print(f'Wrote {size_index:,d} output bytes, ratio: {ratio:8.3%} at {ms_mb:.1f} ms/Mb')
    return files_failed


GNUPLOT_PLT = """set logscale x
set grid
set title "Converting RP66V1 Files to LAS with TotalDepth.RP66V1.ToLAS.main"
set xlabel "RP66V1 File Size (bytes)"
# set mxtics 5
# set xrange [0:3000]
# set xtics
# set format x ""

set logscale y
set ylabel "Conversion Time, Every 64th Frame (s)"
# set yrange [1:1e5]
# set ytics 20
# set mytics 2
# set ytics 8,35,3

set logscale y2
set y2label "LAS size, Every 64th Frame (bytes)"
set y2range [1e5:1e9]
set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

# set fit logfile

# Curve fit, time
conversion_time(x) = 10**(a + b * log10(x))
fit conversion_time(x) "{name}.dat" using 1:4 via a, b

# Curve fit, size
las_size(x) = 10**(c + d * log10(x))
fit las_size(x) "{name}.dat" using 1:2 via c,d

set terminal svg size 1000,700 # choose the file format
set output "{name}.svg" # choose the output device

# set key off

plot "{name}.dat" using 1:4 axes x1y1 title "LAS Conversion Time (s)" lt 1 w points, \
    conversion_time(x) title sprintf("Fit of time: 10**(%+.3g %+.3g * log10(x))", a, b) lt 1 lw 2, \
    "{name}.dat" using 1:2 axes x1y2 title "LAS size (bytes)" lt 3 w points, \
    las_size(x) axes x1y2 title sprintf("Fit of size: 10**(%+.3g %+.3g * log10(x))", c, d) lt 3 lw 2

reset
"""


def plot_gnuplot(data: typing.Dict[str, LASWriteResult], gnuplot_dir: str) -> None:
    """Plot performance with gnuplot."""
    if len(data) < 2:  # pragma: no cover
        raise ValueError(f'Can not plot data with only {len(data)} points.')
    # First row is header row, create it then comment out the first item.
    table = [
        list(LASWriteResult._fields[1:]) + ['Path']
    ]
    table[0][0] = f'# {table[0][0]}'
    for k in sorted(data.keys()):
        if data[k].size_input > 0 and not data[k].exception:
            table.append(list(data[k][1:]) + [k])
    name = 'RP66V1_ToLAS'
    return_code = gnuplot.invoke_gnuplot(gnuplot_dir, name, table, GNUPLOT_PLT.format(name=name))
    if return_code:  # pragma: no cover
        raise IOError(f'Can not plot gnuplot with return code {return_code}')
    return_code = gnuplot.write_test_file(gnuplot_dir, 'svg')
    if return_code:  # pragma: no cover
        raise IOError(f'Can not plot gnuplot with return code {return_code}')


#: Order of fields for the Well Information section. LAS 2.0.
WELL_INFORMATION_KEYS: typing.Tuple[str, ...] = (
    'STRT', 'STOP', 'STEP',
    'NULL',
    'COMP', 'WELL', 'FLD ',  # From the ORIGIN record
    'LOC', 'PROV',
    'CNTY', 'STAT', 'CTRY',
    'UWI ', 'API ',
    'SRVC', 'DATE',  # From the ORIGIN record
    # Not in the LAS 2.0 Std.
    # 'LATI', 'LONG',
)


# =================== Writing a Frame Array to LAS ===================
#: Possible methods to reduce an array to a single value.
ARRAY_REDUCTIONS = {'first', 'mean', 'median', 'min', 'max'}


def _check_array_reduction(method: str) -> None:
    if method not in ARRAY_REDUCTIONS:
        raise ValueError(f'Array reduction method {method} is not in {sorted(ARRAY_REDUCTIONS)}')


def array_reduce(array: np.ndarray, method: str) -> typing.Union[float, int]:
    """Take a numpy array and apply a method to it to get a single value."""
    _check_array_reduction(method)
    if method == 'first':
        return array.flatten()[0]
    return getattr(np, method)(array)


RE_FLOAT_DECIMAL_FORMAT = re.compile(r'^\.[0-9]+')


def _check_float_decimal_places_format(float_decimal_places_format: str) -> None:
    """Raise if float format string is wrong."""
    m = RE_FLOAT_DECIMAL_FORMAT.match(float_decimal_places_format)
    if m is None:
        raise ValueError(f'Invalid float fractional format of "{float_decimal_places_format}"')


def _stringify(value: typing.Union[str, bytes, typing.Any]) -> str:
    """Convert bytes to an ASCII string. Leave string untouched. str() everything else."""
    if isinstance(value, bytes):
        return value.decode("ascii")
    elif isinstance(value, str):
        return value
    return str(value)


def _add_x_axis_to_channels_to_write(frame_array: FrameArray, channel_name_sub_set: typing.Set[typing.Hashable]) -> None:
    """Modifies channel_name_sub_set in-place to include x-axis."""
    if len(channel_name_sub_set) != 0:
        channel_name_sub_set.add(frame_array.x_axis.ident)


def write_curve_section_to_las(frame_array: FrameArray, channels: typing.Set[str], out_stream: typing.TextIO) -> None:
    """
    Write the ``~Curve Information Section`` to the LAS file.

    Example::

        ~Curve Information Section
        #MNEM.UNIT  Curve Description
        #---------  -----------------
        DEPT.m      : DEPT/Depth Dimensions (1,)
        TENS.lbs    : TENS/Tension Dimensions (1,)
        ETIM.min    : ETIM/Elapsed Time Dimensions (1,)
        DHTN.lbs    : DHTN/CH Tension Dimensions (1,)
        GR  .api    : GR/Gamma API Dimensions (1,)
    """
    out_stream.write('~Curve Information Section\n')
    table = [
        ['#MNEM.UNIT', 'Curve Description'],
        ['#---------', '-----------------'],
    ]
    for c, channel in enumerate(frame_array.channels):
        channel_ident_as_str = _stringify(channel.ident)
        if len(channels) == 0 or c == 0 or channel_ident_as_str in channels:
            table.append(
                [
                    f'{channel_ident_as_str:<4}.{_stringify(channel.units):<4}',
                    f': {_stringify(channel.long_name)} Dimensions {channel.dimensions}',
                ]
            )
    rows = data_table.format_table(table, pad='  ', left_flush=True)
    for row in rows:
        out_stream.write(row)
        out_stream.write('\n')


def write_array_section_header_to_las(
        frame_array: FrameArray,
        max_num_available_frames: int,
        array_reduction: str,
        frame_slice: Slice.Slice,
        channel_name_sub_set: typing.Set[str],
        field_width: int,
        out_stream: typing.TextIO,
    ) -> None:
    """
    Write the ``~Array Section`` header to the LAS file, the actual log data.

    Example::

        # Array processing information:
        # Frame Array: ID: OBNAME: O: 2 C: 0 I: b'50' description: b''
        # All [5] original channels reproduced here.
        # Where a channel has multiple values the reduction method is by "first" value.
        # Number of original frames: 649
        # Requested frame slicing: <Slice on length=649 start=0 stop=649 step=1> total number of frames presented here: 649
        ~A          DEPT            TENS            ETIM            DHTN              GR
                2889.400        -999.250        -999.250        -999.250        -999.250
    """
    _check_array_reduction(array_reduction)
    # Write information about how the frames and channels were processed
    out_stream.write(f'# Array processing information:\n')
    out_stream.write(f'# Frame Array: ID: {frame_array.ident} description: {frame_array.description}\n')
    if len(channel_name_sub_set):
        original_channels = ','.join(_stringify(channel.ident) for channel in frame_array.channels)
        out_stream.write(f'# Original channels in Frame Array [{len(frame_array.channels):4d}]: {original_channels}\n')
        # write this out in order
        out_channels = []
        for channel in frame_array:
            if channel.ident in channel_name_sub_set:
                out_channels.append(channel.ident)
        out_stream.write(
            f'# Requested Channels in this LAS file [{len(out_channels):4d}]: {",".join(out_channels)}\n'
        )
    else:
        out_stream.write(f'# All [{len(frame_array.channels)}] original channels reproduced here.\n')
    out_stream.write(f'# Where a channel has multiple values the reduction method is by "{array_reduction}" value.\n')
    num_writable_frames = len(frame_array.x_axis)
    out_stream.write(f'# Maximum number of original frames: {max_num_available_frames}\n')
    out_stream.write(
        f'# Requested frame slicing: {frame_slice.long_str(max_num_available_frames)}'
        f', total number of frames presented here: {num_writable_frames}\n'
    )
    out_stream.write('~A')
    _add_x_axis_to_channels_to_write(frame_array, channel_name_sub_set)
    for c, channel in enumerate(frame_array.channels):
        if len(channel_name_sub_set) == 0 or c == 0 or channel.ident in channel_name_sub_set:
            if c == 0:
                out_stream.write(f'{channel.ident:>{field_width - 2}}')
            else:
                out_stream.write(' ')
                out_stream.write(f'{channel.ident:>{field_width}}')
    out_stream.write('\n')
    num_values = sum(c.count for c in frame_array.channels)
    logger.info(
        f'Writing array section with {num_writable_frames:,d} frames'
        f', {len(frame_array):,d} channels'
        f' and {num_values:,d} values per frame'
        f', total: {num_writable_frames * num_values:,d} input values.'
    )


def write_array_section_data_to_las(
            frame_array: FrameArray,
            array_reduction: str,
            channel_name_sub_set: typing.Set[str],
            field_width: int,
            float_decimal_places_format: str,
            out_stream: typing.TextIO,
    ) -> None:
    """
    Write the frame data into the ``~Array Section`` to the LAS file.
    This allows the caller to reduce the memory requirements by creating the FrameArray incrementally thus::

        write_curve_section_to_las(...)
        write_array_section_header_to_las(...)
        while True:
            # Initialise FrameArray...
            write_array_section_data_to_las(...)

    Example output (one frame)::

                2889.400        -999.250        -999.250        -999.250        -999.250
    """
    _check_float_decimal_places_format(float_decimal_places_format)
    _add_x_axis_to_channels_to_write(frame_array, channel_name_sub_set)
    num_writable_frames = len(frame_array.x_axis)
    for frame_number in range(num_writable_frames):
        for c, channel in enumerate(frame_array.channels):
            if len(channel_name_sub_set) == 0 or channel.ident in channel_name_sub_set:
                if len(channel.array) == 0:
                    raise ValueError(f'No frame data in channel {channel}')
                value = array_reduce(channel.array[frame_number], array_reduction)
                # NOTE: This will write a null value for masked array as the (null) value is still in the array.
                if c > 0:
                    out_stream.write(' ')
                if np.issubdtype(channel.array.dtype, np.integer):
                    out_stream.write(f'{value:{field_width}.0f}')
                elif np.issubdtype(channel.array.dtype, np.floating):
                    out_stream.write(f'{value:{field_width}{float_decimal_places_format}}')
                else:
                    out_stream.write(str(value))
        out_stream.write('\n')
    # To garbage collect the user can:
    # frame_array.init_arrays(0)


def write_array_section_to_las(
        frame_array: FrameArray,
        max_num_available_frames: int,
        array_reduction: str,
        frame_slice: Slice.Slice,
        channel_name_sub_set: typing.Set[str],
        field_width: int,
        float_decimal_places_format: str,
        out_stream: typing.TextIO,
    ) -> None:
    """
    Write the ``~Array Section`` header + log data to the LAS file.

    Example::

        # Array processing information:
        # Frame Array: ID: OBNAME: O: 2 C: 0 I: b'50' description: b''
        # All [5] original channels reproduced here.
        # Where a channel has multiple values the reduction method is by "first" value.
        # Number of original frames: 649
        # Requested frame slicing: <Slice on length=649 start=0 stop=649 step=1> total number of frames presented here: 649
        ~A          DEPT            TENS            ETIM            DHTN              GR
                2889.400        -999.250        -999.250        -999.250        -999.250
    """
    _check_float_decimal_places_format(float_decimal_places_format)
    write_array_section_header_to_las(frame_array, max_num_available_frames, array_reduction, frame_slice,
                                      channel_name_sub_set, field_width, out_stream)
    write_array_section_data_to_las(frame_array, array_reduction, channel_name_sub_set, field_width, float_decimal_places_format,
                                    out_stream)


def write_curve_and_array_section_to_las(
        frame_array: FrameArray,
        max_num_available_frames: int,
        array_reduction: str,
        frame_slice: Slice.Slice,
        channel_name_sub_set: typing.Set[str],
        field_width: int,
        float_decimal_places_format: str,
        out_stream: typing.TextIO,
    ) -> None:
    """
    Write the ``~Curve Information Section`` to the LAS file followed by the ``~Array Section`` header + log data to the
    LAS file.

    Example::

        ~Curve Information Section
        #MNEM.UNIT  Curve Description
        #---------  -----------------
        DEPT.m      : DEPT/Depth Dimensions: [1]
        TENS.lbs    : TENS/Tension Dimensions: [1]
        ETIM.min    : ETIM/Elapsed Time Dimensions: [1]
        DHTN.lbs    : DHTN/CH Tension Dimensions: [1]
        GR  .api    : GR/Gamma API Dimensions: [1]
        # Array processing information:
        # Frame Array: ID: OBNAME: O: 2 C: 0 I: b'50' description: b''
        # All [5] original channels reproduced here.
        # Where a channel has multiple values the reduction method is by "first" value.
        # Number of original frames: 649
        # Requested frame slicing: <Slice on length=649 start=0 stop=649 step=1> total number of frames presented here: 649
        ~A          DEPT            TENS            ETIM            DHTN              GR
                2889.400        -999.250        -999.250        -999.250        -999.250
    """
    _check_float_decimal_places_format(float_decimal_places_format)
    write_curve_section_to_las(frame_array, channel_name_sub_set, out_stream)
    write_array_section_to_las(frame_array, max_num_available_frames, array_reduction, frame_slice,
                               channel_name_sub_set, field_width, float_decimal_places_format, out_stream)


# =================== END: Writing a Frame Array to LAS ===================


def las_writer_command_line_arguments(description: str, **kwargs) -> argparse.PARSER:
    """Creates a common command line argument parser for converting files to LAS."""
    parser = cmn_cmd_opts.path_in_out(
        description, **kwargs,
    )
    cmn_cmd_opts.add_log_level(parser, level=20)
    cmn_cmd_opts.add_multiprocessing(parser)
    Slice.add_frame_slice_to_argument_parser(parser, use_what=True)
    process.add_process_logger_to_argument_parser(parser)
    gnuplot.add_gnuplot_to_argument_parser(parser)
    parser.add_argument(
        '--array-reduction', type=str,
        help='Method to reduce multidimensional channel data to a single value. [default: %(default)s]',
        default='first',
        choices=list(sorted(ARRAY_REDUCTIONS)),
        )
    parser.add_argument(
        '--channels', type=str,
        help='Comma separated list of channels to write out (X axis is always included).'
             ' Use \'?\' to see what channels exist without writing anything. [default: "%(default)s"]',
        default='',
        )
    parser.add_argument('--field-width', type=int,
                        help='Field width for array data [default: %(default)s].', default=16)
    parser.add_argument('--float-format', type=str,
                        help='Floating point format for array data [default: "%(default)s"].', default='.3f')
    return parser


def report_las_write_results_and_performance(results: typing.Dict[str, LASWriteResult], clock_exec: float,
                                             gnuplot: bool = False, include_ignored: bool = True,
                                             out_stream: typing.TextIO = sys.stdout) -> int:
    """Writes out the results of converting files to LAS."""
    ret_val = report_las_write_results(results, gnuplot, include_ignored=include_ignored)
    out_stream.write(f'Writing results returned: {ret_val} files failed.\n')
    size_input, size_output = las_size_input_output(results)
    out_stream.write('Execution time = %8.3f (S)\n' % clock_exec)
    if size_input > 0:
        ms_mb = clock_exec * 1000 / (size_input / 1024 ** 2)
        ratio = size_output / size_input
    else:
        ms_mb = 0.0
        ratio = 0.0
    out_stream.write(
        f'Out of {len(results):,d} processed {len(results):,d} files of total size {size_input:,d} input bytes.\n'
    )
    out_stream.write(f'Wrote {size_output:,d} output bytes, ratio: {ratio:8.3%} at {ms_mb:.1f} ms/Mb.\n')
    out_stream.write(f'Execution time: {clock_exec:.3f} (s).\n')
    return ret_val
