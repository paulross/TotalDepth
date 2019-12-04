"""Read RP66V1 files and saves the index a s pickle file."""
import logging
import multiprocessing
import os
import pickle
import sys
import time
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import File
from TotalDepth.RP66V1.core import LogicalFile
from TotalDepth.common import cmn_cmd_opts
from TotalDepth.common import data_table
from TotalDepth.common import process
from TotalDepth.util import gnuplot, DirWalk
from TotalDepth.util.DirWalk import dirWalk
from TotalDepth.util.bin_file_type import binary_file_type_from_path


__author__  = 'Paul Ross'
__date__    = '2019-06-29'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


logger = logging.getLogger(__file__)


class IndexResult(typing.NamedTuple):
    path_in: str
    size_input: int
    size_index: int
    time_write: float
    time_read: float
    exception: bool
    ignored: bool


def unpickle(path: str) -> LogicalFile.LogicalIndex:
    """Un-pickles a Logical Index from the given path."""
    with open(path, 'rb') as in_stream:
        return pickle.loads(in_stream.read())


def index_dir_multiprocessing(dir_in: str, dir_out: str, jobs: int,
                              recurse: bool, read_back: bool) -> typing.Dict[str, IndexResult]:
    """Multiprocessing code to plot log passes.
    Returns a dict of {path_in : IndexResult, ...}"""
    assert os.path.isdir(dir_in)
    if jobs < 1:
        jobs = multiprocessing.cpu_count()
    logging.info('scan_dir_multiprocessing(): Setting multi-processing jobs to %d' % jobs)
    pool = multiprocessing.Pool(processes=jobs)
    tasks = [
        (t.filePathIn, t.filePathOut, read_back) for t in DirWalk.dirWalk(
            dir_in, dir_out, theFnMatch='', recursive=recurse, bigFirst=True
        )
    ]
    # print('tasks:')
    # pprint.pprint(tasks, width=200)
    # return {}
    results = [
        r.get() for r in [
            pool.apply_async(index_a_single_file, t) for t in tasks
        ]
    ]
    return {r.path_in: r for r in results}


def index_a_single_file(path_in: str, path_out: str, read_back: bool) -> IndexResult:
    bin_file_type = binary_file_type_from_path(path_in)
    if bin_file_type == 'RP66V1':
        if path_out:
            out_dir = os.path.dirname(path_out)
            if not os.path.exists(out_dir):
                logger.info(f'Making directory: {out_dir}')
                os.makedirs(out_dir, exist_ok=True)
        logger.info(f'Indexing {path_in} to pickle {path_out}')
        try:
            t_start = time.perf_counter()
            with LogicalFile.LogicalIndex(path_in) as logical_index:
                pickled_index = pickle.dumps(logical_index)
                # logger.info(f'Length of pickled index: {len(pickled_index)}')
                pickle_path = path_out + '.pkl'
                with open(pickle_path, 'wb') as out_stream:
                    out_stream.write(pickled_index)
                write_time = time.perf_counter() - t_start
                if read_back:
                    t_start = time.perf_counter()
                    _read_index = unpickle(pickle_path)
                    read_time = time.perf_counter() - t_start
                else:
                    read_time = 0.0
                result = IndexResult(path_in, os.path.getsize(path_in), len(pickled_index), write_time, read_time, False, False)
                return result
        except ExceptionTotalDepthRP66V1:
            logger.exception(f'Failed to index with ExceptionTotalDepthRP66V1: {path_in}')
        except Exception:
            logger.exception(f'Failed to index with Exception: {path_in}')
        return IndexResult(path_in, os.path.getsize(path_in), 0, 0.0, 0.0, True, False)
    return IndexResult(path_in, os.path.getsize(path_in), 0, 0.0, 0.0, False, True)


def index_dir_or_file(path_in: str, path_out: str, recurse: bool, read_back: bool) -> typing.Dict[str, IndexResult]:
    logging.info(f'index_dir_or_file(): "{path_in}" to "{path_out}" recurse: {recurse}')
    ret = {}
    if os.path.isdir(path_in):
        for file_in_out in dirWalk(path_in, path_out, theFnMatch='', recursive=recurse, bigFirst=False):
            bin_file_type = binary_file_type_from_path(file_in_out.filePathIn)
            if bin_file_type == 'RP66V1':
                ret[file_in_out.filePathIn] = index_a_single_file(file_in_out.filePathIn, file_in_out.filePathOut, read_back)
    else:
        bin_file_type = binary_file_type_from_path(path_in)
        if bin_file_type == 'RP66V1':
            ret[path_in] = index_a_single_file(path_in, path_out, read_back)
    return ret


GNUPLOT_PLT = """set logscale x
set grid
set title "TotalDepth.RP66V1.IndexPickle.main."
set xlabel "RP66V1 File Size (bytes)"
# set mxtics 5
# set xrange [0:3000]
# set xtics
# set format x ""

set logscale y
set ylabel "Index Rate (ms/Mb), Index Compression Ratio"
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
        list(IndexResult._fields[1:]) + ['Path']
    ]
    table[0][0] = f'# {table[0][0]}'
    for k in sorted(data.keys()):
        if data[k].size_input > 0 and not data[k].exception:
            table.append(list(data[k][1:]) + [k])
    name = 'IndexFile'
    return_code = gnuplot.invoke_gnuplot(gnuplot_dir, name, table, GNUPLOT_PLT.format(name=name))
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')
    return_code = gnuplot.write_test_file(gnuplot_dir, 'svg')
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')


def main() -> int:
    description = """usage: %(prog)s [options] file
Scans a RP66V1 file or directory and saves the index as a pickled file."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = cmn_cmd_opts.path_in_out(
        description, prog='TotalDepth.RP66V1.IndexPickle.main', version=__version__, epilog=__rights__
    )
    cmn_cmd_opts.add_log_level(parser, level=20)
    cmn_cmd_opts.add_multiprocessing(parser)
    parser.add_argument('--read-back', action='store_true', help='Read and time the output. [default: %(default)s]')
    process.add_process_logger_to_argument_parser(parser)
    gnuplot.add_gnuplot_to_argument_parser(parser)
    args = parser.parse_args()
    # print('args:', args)
    # return 0
    cmn_cmd_opts.set_log_level(args)
    # Your code here
    clk_start = time.perf_counter()
    if cmn_cmd_opts.multiprocessing_requested(args) and os.path.isdir(args.path_in):
        result: typing.Dict[str, IndexResult] = index_dir_multiprocessing(
            args.path_in,
            args.path_out,
            args.jobs,
            args.recurse,
            args.read_back,
        )
    else:
        if args.log_process > 0.0:
            with process.log_process(args.log_process):
                result: typing.Dict[str, IndexResult] = index_dir_or_file(
                    args.path_in,
                    args.path_out,
                    args.recurse,
                    args.read_back,
                )
        else:
            result: typing.Dict[str, IndexResult] = index_dir_or_file(
                args.path_in,
                args.path_out,
                args.recurse,
                args.read_back,
            )
    clk_exec = time.perf_counter() - clk_start
    size_index = size_input = 0
    files_processed = 0
    try:
        path_prefix = os.path.commonpath(result.keys())
        len_path_prefix = len(path_prefix)
        table: typing.List[typing.List[str]] = [
            [
                'Size (b)', 'Index (b)', 'Ratio (%)', 'Index (s)', 'Index (ms/Mb)',
                'Read (s)', 'Read (ms/Mb)', 'Except',
                'Path',
            ]
        ]
        for path in sorted(result.keys()):
            idx_result = result[path]
            if not idx_result.ignored and idx_result.size_input > 0:
                ms_mb_write = idx_result.time_write * 1000 / (idx_result.size_input / 1024 ** 2)
                ms_mb_read = idx_result.time_read * 1000 / (idx_result.size_input / 1024 ** 2)
                ratio = idx_result.size_index / idx_result.size_input
                table.append(
                    [
                        f'{idx_result.size_input:,d}', f'{idx_result.size_index:,d}', f'{ratio:.3%}',
                        f'{idx_result.time_write:.3f}', f'{ms_mb_write:.1f}',
                        f'{idx_result.time_read:.3f}', f'{ms_mb_read:.2f}',
                        f'{str(idx_result.exception):5}',
                        f'{path[len_path_prefix+1:]}',
                    ]
                )
                size_input += result[path].size_input
                size_index += result[path].size_index
                files_processed += 1
        print(f'Common path prefix: {path_prefix}')
        print('\n'.join(data_table.format_table(table, pad=' | ', heading_underline='-')))
        if args.gnuplot:
            try:
                plot_gnuplot(result, args.gnuplot)
            except IOError:
                logger.exception('Plotting with gnuplot failed.')
    except Exception as err:
        logger.exception(str(err))
    print('Execution time = %8.3f (S)' % clk_exec)
    if size_input > 0:
        ms_mb = clk_exec * 1000 / (size_input/ 1024**2)
        ratio = size_index / size_input
    else:
        ms_mb = 0.0
        ratio = 0.0
    print(f'Out of  {len(result):,d} processed {files_processed:,d} files of total size {size_input:,d} input bytes')
    print(f'Wrote {size_index:,d} output bytes, ratio: {ratio:8.3%} at {ms_mb:.1f} ms/Mb')
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
