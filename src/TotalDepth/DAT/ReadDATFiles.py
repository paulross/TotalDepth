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
Runs through a directory reading DAT files measuring the performance of the parser.
"""
import logging
import multiprocessing
import os
import sys
import time
import typing

from TotalDepth.DAT import DAT_parser
from TotalDepth.common import cmn_cmd_opts, process
from TotalDepth.util import gnuplot, DirWalk, bin_file_type

logger = logging.getLogger(__file__)


__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2020 Paul Ross. All rights reserved.'


class DATFileResult(typing.NamedTuple):
    """Contains the result of reading a DAT file."""
    path_input: str
    size_input: int
    time: float
    channels: int
    frames: int
    exception: bool
    ignored: bool


def scan_a_single_file(path_in: str, label_process: bool) -> DATFileResult:
    binary_file_type = bin_file_type.binary_file_type_from_path(path_in)
    if binary_file_type == 'DAT':
        logging.info(f'Scanning DAT file at "{path_in}"')
        t_start = time.perf_counter()
        try:
            dat_frame_array = DAT_parser.parse_path(path_in)
            result = DATFileResult(
                path_in,
                os.path.getsize(path_in),
                time.perf_counter() - t_start,
                len(dat_frame_array),
                len(dat_frame_array.x_axis),
                False,
                False,
            )
        except DAT_parser.ExceptionDATRead:
            logger.exception(f'Failed to read with ExceptionDATRead: {path_in}')
            result = DATFileResult(path_in, os.path.getsize(path_in), 0.0, 0, 0, True, False)
        except Exception:
            logger.exception(f'Failed to index with Exception: {path_in}')
            result = DATFileResult(path_in, os.path.getsize(path_in), 0.0, 0, 0, True, False)
    else:
        logger.debug(f'Ignoring file type "{binary_file_type}" at {path_in}')
        result = DATFileResult(path_in, 0, 0.0, 0, 0, False, True)
    return result


def scan_dir_or_file(path_in: str, recursive: bool, label_process: bool) -> typing.Dict[str, DATFileResult]:
    """Scans a directory or file.
    Returns a dict of {path_in : DATFileResult, ...}
    """
    # NOTE: normpath removes trailing os.sep which is what we want.
    path_in = os.path.normpath(path_in)
    logging.info(f'scan_dir_or_file(): "{path_in}" recurse: {recursive}')
    ret: typing.Dict[str, DATFileResult] = {}
    if os.path.isdir(path_in):
        if not recursive:
            for file_in_out in DirWalk.dirWalk(path_in, theFnMatch='', recursive=recursive, bigFirst=False):
                result = scan_a_single_file(file_in_out.filePathIn, label_process)
                ret[file_in_out.filePathIn] = result
        else:
            for root, dirs, files in os.walk(path_in, topdown=False):
                for file in files:
                    file_path_in = os.path.join(root, file)
                    result = scan_a_single_file(file_path_in, label_process)
                    ret[file_path_in] = result
    else:
        ret[path_in] = scan_a_single_file(path_in, label_process)
    return ret


def scan_dir_multiprocessing(dir_in, jobs) -> typing.Dict[str, DATFileResult]:
    """Multiprocessing code to scan DAT files."""
    assert os.path.isdir(dir_in)
    if jobs < 1:
        jobs = multiprocessing.cpu_count()
    logging.info('scan_dir_multiprocessing(): Setting multi-processing jobs to %d' % jobs)
    pool = multiprocessing.Pool(processes=jobs)
    tasks = [
        (t.filePathIn, False) for t in DirWalk.dirWalk(dir_in, theFnMatch='', recursive=True, bigFirst=True)
    ]
    results = [r.get() for r in [pool.apply_async(scan_a_single_file, t) for t in tasks]]
    return {r.path_input: r for r in results}


GNUPLOT_PLT = """set logscale x
set grid
set title "Scan of DAT Files with ReadDATFiles."
set xlabel "DAT File Size (bytes)"
# set mxtics 5
set xrange [:10e6]
set xtics
# set format x ""

set logscale y
set ylabel "Read Time (s)"
# set yrange [1:1e5]
# set ytics 20
# set mytics 2
# set ytics 8,35,3

set logscale y2
set y2label "Read Rate (ms/Mb)"
set y2range [10:1000]
set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

# set fit logfile

# Fields: size_input, time, path

# Curve fit, read time
read_time(x) = a*x + b
fit read_time(x) "{name}.dat" using 1:2 via a, b

set terminal svg size 1000,700 # choose the file format
set output "{name}.svg" # choose the output device

    # read_time(x) title sprintf("Read Time Fit: %+.3g + %+.3g * x", a, b) lt 1 lw 2, \\

plot "{name}.dat" using 1:2 axes x1y1 title "Read Time (s), left axis" lt 2 w points, \\
    "{name}.dat" using 1:($2*1000/($1/(1024*1024))) axes x1y2 title "Read Rate (ms/Mb), right axis" lt 3 w points

reset
"""


def plot_gnuplot(data: typing.Dict[str, DATFileResult], gnuplot_dir: str) -> None:
    if len(data) < 2:
        raise ValueError(f'Can not plot data with only {len(data)} points.')
    # First row is header row, create it then comment out the first item.
    table = [['size_input', 'time', 'Path']]
    table[0][0] = f'# {table[0][0]}'
    for k in sorted(data.keys()):
        if data[k].size_input > 0 and not data[k].exception:
            table.append([data[k].size_input, data[k].time, k,])
    name = 'ScanFileDAT'
    return_code = gnuplot.invoke_gnuplot(gnuplot_dir, name, table, GNUPLOT_PLT.format(name=name))
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')
    return_code = gnuplot.write_test_file(gnuplot_dir, 'svg')
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')


def main() -> int:
    description = """Scans a DAT file or directory and reads any DAT files."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = cmn_cmd_opts.path_in(
        description, prog='TotalDepth.DAT.ReadDATFIles.main', version=__version__, epilog=__rights__
    )
    cmn_cmd_opts.add_log_level(parser, level=20)
    cmn_cmd_opts.add_multiprocessing(parser)
    process.add_process_logger_to_argument_parser(parser)
    gnuplot.add_gnuplot_to_argument_parser(parser)
    args = parser.parse_args()
    log_level = cmn_cmd_opts.set_log_level(args)
    # print('args:', args)
    # return 0
    clk_start = time.perf_counter()
    # Your code here
    if args.log_process > 0.0:
        with process.log_process(args.log_process, log_level):
            results: typing.Dict[str, DATFileResult] = scan_dir_or_file(args.path_in, args.recurse, label_process=True)
    else:
        if cmn_cmd_opts.multiprocessing_requested(args) and os.path.isdir(args.path_in):
            results: typing.Dict[str, DATFileResult] = scan_dir_multiprocessing(args.path_in, args.jobs)
        else:
            results: typing.Dict[str, DATFileResult] = scan_dir_or_file(args.path_in, args.recurse, label_process=False)
    if args.log_process > 0.0:
        process.add_message_to_queue('Processing DAT Files Complete.')
    # print('Execution time = %8.3f (S)' % clk_exec)
    header = (
        f'{"Size In":>16}',
        f'{"Channels":>8}',
        f'{"Frames":>8}',
        f'{"Time":>8}',
        f'{"ms/Mb":>8}',
        f'{"Fail?":5}',
        f'Path',
    )
    common_prefix = os.path.commonpath(results.keys())
    print(f'Common prefix: {common_prefix}')
    print(' '.join(header))
    print(' '.join('-' * len(v) for v in header))
    total_input = total_frames = files_ok = files_fail = 0
    total_time = 0.0
    for path in sorted(results.keys()):
        result = results[path]
        if result.size_input > 0:
            ms_mb = result.time * 1000 / (result.size_input / 1024 ** 2)
            print(
                f'{result.size_input:16,d}'
                f' {result.channels:8,d}'
                f' {result.frames:8,d}'
                f' {result.time:8.3f}'
                f' {ms_mb:8.1f}'
                f' {str(result.exception):5}'
                f' "{path[len(common_prefix):]}"'
            )
            if result.exception:
                files_fail += 1
            else:
                files_ok += 1
            total_input += result.size_input
            total_frames += result.frames
            total_time += result.time
    if args.gnuplot:
        try:
            plot_gnuplot(results, args.gnuplot)
        except IOError:
            logger.exception('Plotting with gnuplot failed.')
    if total_input > 0:
        ms_mb = total_time * 1000 / (total_input / 1024**2)
    else:
        ms_mb = 0.0
    clk_exec = time.perf_counter() - clk_start
    print(f'Statistics:')
    print(f'   Processed: {len(results):16,d} total files')
    print(f'    Of which: {files_fail+files_ok:16,d} are DAT files')
    print(f'     Success: {files_ok:16,d}')
    print(f'    Failures: {files_fail:16,d}')
    print(f' Total input: {total_input:16,d} bytes')
    if files_fail + files_ok:
        print(f'Average size: {int(total_input / (files_fail+files_ok)):16,d} bytes')
    else:
        print(f'Average size: {"N/A":16} bytes')
    print(f'Total frames: {total_frames:16,d}')
    print(f'  Total time: {total_time:16.3f} (s)')
    print(f'        Rate: {ms_mb:16.1f} ms/Mb')
    print()
    print(f'    Run time: {clk_exec:16.3f} (s)')
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
