import argparse
import logging
import multiprocessing
import os
import typing

import TotalDepth.common
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
    """Holds the result of processing a RP66V1 file to LAS."""
    path_input: str
    size_input: int
    size_output: int
    las_count: int
    time: float
    exception: bool
    ignored: bool


#: Format for time as UTC
LAS_DATETIME_FORMAT_UTC = '%Y-%m-%d %H:%M:%S.%f UTC'
#: Format for time as text
LAS_DATE_FORMAT_TEXT = 'YYYY-mm-dd HH:MM:SS.us UTC'


class UnitValueDescription(typing.NamedTuple):
    """Class for accumulating data from PARAMETER tables and Well Information sections."""
    unit: str
    value: str
    description: str


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
            with TotalDepth.common.process.log_process(args.log_process):
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



def report_las_write_results(result: typing.Dict[str, LASWriteResult], gnuplot: str) -> int:
    # Report output
    size_index = size_input = 0
    ret_val = 0
    if result:
        files_processed = 0
        table = [
            ['Input', 'Output', 'LAS Count', 'Time', 'Ratio', 'ms/Mb', 'Exception', 'Path']
        ]
        for path in sorted(result.keys()):
            las_result = result[path]
            if las_result.size_input > 0:
                ms_mb = las_result.time * 1000 / (las_result.size_input / 1024 ** 2)
                ratio = las_result.size_output / las_result.size_input
                out = [
                    f'{las_result.size_input:,d}',
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
                    ret_val = 1
        for row in TotalDepth.common.data_table.format_table(table, pad=' ', heading_underline='-'):
            print(row)
        try:
            if gnuplot:
                plot_gnuplot(result, gnuplot)
        except Exception as err:  # pragma: no cover
            logger.exception(str(err))
            ret_val = 2
        # print('Execution time = %8.3f (S)' % clk_exec)
        # if size_input > 0:
        #     ms_mb = clk_exec * 1000 / (size_input/ 1024**2)
        #     ratio = size_index / size_input
        # else:
        #     ms_mb = 0.0
        #     ratio = 0.0
        # print(f'Out of  {len(result):,d} processed {files_processed:,d} files of total size {size_input:,d} input bytes')
        # print(f'Wrote {size_index:,d} output bytes, ratio: {ratio:8.3%} at {ms_mb:.1f} ms/Mb')
    return ret_val


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