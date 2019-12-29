"""
Exercises the LogicalRecordIndex on real files.
"""
import logging
import multiprocessing
import os
import pickle
import sys
import time
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import Index, File
from TotalDepth.common import cmn_cmd_opts, process
from TotalDepth.util import bin_file_type, DirWalk, ExecTimer
from TotalDepth.util import gnuplot

__author__  = 'Paul Ross'
__date__    = '2019-11-30'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'

logger = logging.getLogger(__file__)


def unpickle(path: str) -> Index.LogicalRecordIndex:
    """Unpickle a file and return an Index.LogicalRecordIndex."""
    with open(path, 'rb') as in_stream:
        return pickle.loads(in_stream.read())


class IndexResult(typing.NamedTuple):
    """Result of indexing a RP66V1 file."""
    path_in: str
    size_input: int
    size_index: int
    index_time: float
    time_write: float
    time_read_back: float
    exception: bool
    ignored: bool


def index_dir_multiprocessing(dir_in: str, dir_out: str, jobs: int,
                              recurse: bool, read_back: bool, validate: bool) -> typing.Dict[str, IndexResult]:
    """Multiprocessing code to plot log passes.
    Returns a dict of {path_in : IndexResult, ...}"""
    assert os.path.isdir(dir_in)
    if jobs < 1:
        jobs = multiprocessing.cpu_count()
    logging.info('scan_dir_multiprocessing(): Setting multi-processing jobs to %d' % jobs)
    pool = multiprocessing.Pool(processes=jobs)
    tasks = [
        (t.filePathIn, t.filePathOut, read_back, validate) for t in DirWalk.dirWalk(
            dir_in, dir_out, theFnMatch='', recursive=recurse, bigFirst=True
        )
    ]
    results = [
        r.get() for r in [
            pool.apply_async(index_a_single_file, t) for t in tasks
        ]
    ]
    return {r.path_in: r for r in results}


def index_a_single_file(path_in: str, path_out: str, read_back: bool, validate: bool) -> IndexResult:
    """Read a single file and return an IndexResult."""
    file_type = bin_file_type.binary_file_type_from_path(path_in)
    if file_type == 'RP66V1':
        if path_out:
            out_dir = os.path.dirname(path_out)
            if not os.path.exists(out_dir):
                logger.info(f'Making directory: {out_dir}')
                os.makedirs(out_dir, exist_ok=True)
        logger.info(f'Indexing {path_in}')
        try:
            t_start = time.perf_counter()
            # Index the file
            # process.add_message_to_queue(f'Start {os.path.basename(path_in)}')
            with Index.LogicalRecordIndex(path_in) as logical_record_index:
                index_time = time.perf_counter() - t_start
                if validate:
                    try:
                        logical_record_index.validate()
                        logger.info(f'Validation OK for {path_in}')
                    except File.ExceptionFileReadPositionsInconsistent() as err:
                        logger.exception(f'Validation of {path_in} failed with {err}')
                t_start = time.perf_counter()
                # process.add_message_to_queue(f'Pickle {os.path.basename(path_in)}')
                # Pickle the index
                if path_out:
                    pickle_path = path_out + '.pkl'
                    with open(pickle_path, 'wb') as pickle_file:
                        pickle.dump(logical_record_index, pickle_file)
                    len_pickled_index = os.path.getsize(pickle_path)
                    write_time = time.perf_counter() - t_start
                    if read_back:
                        t_start = time.perf_counter()
                        _read_index = unpickle(pickle_path)
                        read_back_time = time.perf_counter() - t_start
                    else:
                        read_back_time = 0.0
                else:
                    pickled_index = pickle.dumps(logical_record_index)
                    write_time = time.perf_counter() - t_start
                    len_pickled_index = len(pickled_index)
                    read_back_time = 0.0
                result = IndexResult(path_in, os.path.getsize(path_in), len_pickled_index,
                                     index_time, write_time, read_back_time, False, False)
                return result
        except ExceptionTotalDepthRP66V1:  # pragma: no cover
            logger.exception(f'Failed to index with ExceptionTotalDepthRP66V1: {path_in}')
        except Exception:  # pragma: no cover
            logger.exception(f'Failed to index with Exception: {path_in}')
        return IndexResult(path_in, os.path.getsize(path_in), 0, 0.0, 0.0, 0.0, True, False)  # pragma: no cover
    return IndexResult(path_in, os.path.getsize(path_in), 0, 0.0, 0.0, 0.0, False, True)  # pragma: no cover


def index_dir_or_file(path_in: str, path_out: str,
                      recurse: bool, read_back: bool, validate: bool) -> typing.Dict[str, IndexResult]:
    """Index a directory or file and return the results."""
    logging.info(f'index_dir_or_file(): "{path_in}" to "{path_out}" recurse: {recurse}')
    ret = {}
    if os.path.isdir(path_in):
        for file_in_out in DirWalk.dirWalk(path_in, path_out, theFnMatch='', recursive=recurse, bigFirst=False):
            file_type = bin_file_type.binary_file_type_from_path(file_in_out.filePathIn)
            if file_type == 'RP66V1':
                ret[file_in_out.filePathIn] = index_a_single_file(
                    file_in_out.filePathIn, file_in_out.filePathOut, read_back, validate
                )
    else:
        file_type = bin_file_type.binary_file_type_from_path(path_in)
        if file_type == 'RP66V1':
            ret[path_in] = index_a_single_file(path_in, path_out, read_back, validate)
    return ret

GNUPLOT_PLT = """set logscale x
set grid
set title "TotalDepth.RP66V1.LogRecIndex.main."
set xlabel "RP66V1 File Size (bytes)"
# set mxtics 5
# set xrange [0:3000]
# set xtics
# set format x ""

set logscale y
#set ylabel "Index Time (s)"
#set yrange [:1e3]
# set ytics 20
# set mytics 2
# set ytics 8,35,3

#set logscale y2
#set y2label "Index Compression Ratio, Index Size / Original Size"
# set y2range [1e-4:10]
#set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

set fit logfile

# Curve fit, time vs size, for index/write/re-read
time_fit_index(x) = 10**(a * log10(x) + b)
fit time_fit_index(x) "{name}.dat" using 1:3 via a,b

time_fit_write(x) = 10**(c * log10(x) + d)
fit time_fit_write(x) "{name}.dat" using 1:4 via c,d

time_fit_reread(x) = 10**(e * log10(x) + f)
fit time_fit_reread(x) "{name}.dat" using 1:5 via e,f

size_fit(x) = 10**((g * log10(x)) + h)
fit size_fit(x) "{name}.dat" using 1:2 via g,h

set key top left

set terminal svg size 1000,700 # choose the file format

set output "{name}_size.svg" # choose the output device
set ylabel "Index Size (s)"

plot "{name}.dat" using 1:2 axes x1y1 title "Index Size" lt 1 w points, \
    size_fit(x) title sprintf("Fit: 10**(%.3g + %.3g * log10(x))", h,g) axes x1y1 lt 1 lw 1.5, \
    "{name}.dat" using 1:1 title "Unity" axes x1y1 lt 2 lw 0.25 dt 1 w lines# smooth bezier

set output "{name}_times.svg" # choose the output device
set ylabel "Index Time (s)"

plot "{name}.dat" using 1:3 axes x1y1 title "Index Time (s)" lt 1 w points, \
    time_fit_index(x) title sprintf("Index Time Fit: 10**(%.3g + %.3g * log10(x))", b, a) lt 1 lw 1.5, \
    "{name}.dat" using 1:4 axes x1y1 title "Write Time (s)" lt 2 w points, \
    time_fit_write(x) title sprintf("Write Time Fit: 10**(%.3g + %.3g * log10(x))", d,c) lt 2 lw 1.5, \
    "{name}.dat" using 1:5 axes x1y1 title "Read Time (s)" lt 3 lc 4 w points, \
    time_fit_reread(x) title sprintf("Read Time Fit: 10**(%.3g + %.3g * log10(x))", f,e) lt 3 lc 4 lw 1.5

reset
"""


def plot_gnuplot(data: typing.Dict[str, IndexResult], gnuplot_dir: str) -> None:
    """Plot the results as a Gnuplot graph."""
    # if len(data) < 2:
    #     raise ValueError(f'Can not plot data with only {len(data)} points.')
    # First row is header row, create it then comment out the first item.
    table = [
        list(IndexResult._fields[1:]) + ['Path']
    ]
    table[0][0] = f'# {table[0][0]}'
    for k in sorted(data.keys()):
        if data[k].size_input > 0 and not data[k].exception:
            table.append(list(data[k][1:]) + [k])
    name = os.path.basename(__file__)
    return_code = gnuplot.invoke_gnuplot(gnuplot_dir, name, table, GNUPLOT_PLT.format(name=name))
    if return_code:  # pragma: no cover
        raise IOError(f'Can not plot gnuplot with return code {return_code}')
    return_code = gnuplot.write_test_file(gnuplot_dir, 'svg')
    if return_code:  # pragma: no cover
        raise IOError(f'Can not plot gnuplot with return code {return_code}')


def main() -> int:
    """Main entry point."""
    description = """usage: %(prog)s [options] file
    Scans a RP66V1 file or directory and indexes the files with a LogicalRecordIndex."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = cmn_cmd_opts.path_in_out(
        description, prog='TotalDepth.RP66V1.LogRecIndex.main', version=__version__, epilog=__rights__
    )
    cmn_cmd_opts.add_log_level(parser, level=20)
    cmn_cmd_opts.add_multiprocessing(parser)
    process.add_process_logger_to_argument_parser(parser)
    gnuplot.add_gnuplot_to_argument_parser(parser)
    parser.add_argument(
        '--read-back', action='store_true',
        help='Read the pickled index and time it (requires path_out). [default: %(default)s]',
    )
    parser.add_argument(
        '--validate', action='store_true',
        help='Perform validation checks on the index.. [default: %(default)s]',
    )
    args = parser.parse_args()
    # print('args:', args)
    # return 0
    cmn_cmd_opts.set_log_level(args)
    # Your code here
    exec_timer = ExecTimer.Timer('LogRecIndex')
    if os.path.isdir(args.path_in) and cmn_cmd_opts.multiprocessing_requested(args):
        result: typing.Dict[str, IndexResult] = index_dir_multiprocessing(
            args.path_in,
            args.path_out,
            args.jobs,
            args.recurse,
            args.read_back,
            args.validate,
        )
    else:
        if args.log_process > 0.0:
            with process.log_process(args.log_process):
                result: typing.Dict[str, IndexResult] = index_dir_or_file(
                    args.path_in,
                    args.path_out,
                    args.recurse,
                    args.read_back,
                    args.validate,
                )
        else:
            result: typing.Dict[str, IndexResult] = index_dir_or_file(
                args.path_in,
                args.path_out,
                args.recurse,
                args.read_back,
                args.validate,
            )
    size_index = size_input = 0
    files_processed = 0
    if os.path.isdir(args.path_in):
        len_path = len(args.path_in)
        if not args.path_in.endswith(os.sep):
            len_path += 1
    else:
        len_path = 0
    ret_value = 0
    try:
        header = (
            f'{"Size In":>16}',
            f'{"Size Out":>16}',
            f'{"Time (ms)":>10}',
            f'{"Ratio %":>8}',
            f'{"ms/Mb":>8}',
            f'{"Fail?":5}',
            f'{"Write (ms)":>10}',
            f'{"Read (ms)":>10}',
            f'Path',
        )
        print(' '.join(header))
        print(' '.join('-' * len(v) for v in header))
        for path in sorted(result.keys()):
            idx_result = result[path]
            if idx_result.size_input > 0:
                ms_mb = idx_result.index_time * 1000 / (idx_result.size_input / 1024 ** 2)
                ratio = idx_result.size_index / idx_result.size_input
                print(
                    f'{idx_result.size_input:16,d} {idx_result.size_index:16,d}'
                    f' {1000*idx_result.index_time:10.1f} {ratio:8.3%} {ms_mb:8.1f} {str(idx_result.exception):5}'
                    f' {1000*idx_result.time_write:10.1f} {1000*idx_result.time_read_back:10.1f}'
                    f' "{path[len_path:]}"'
                )
                size_input += result[path].size_input
                size_index += result[path].size_index
                files_processed += 1
                exec_timer.add_work_done(idx_result.size_input)
        if args.gnuplot:
            try:
                plot_gnuplot(result, args.gnuplot)
            except Exception:  # pragma: no cover
                logger.exception('gunplot failed')
                ret_value = 1
    except Exception as err:  # pragma: no cover
        logger.exception(str(err))
        ret_value = 2
    print(f'Number of jobs: {args.jobs}')
    print('Execution:')
    print(exec_timer.long_str)
    if size_input > 0:
        ratio = size_index / size_input
    else:
        ratio = 0.0
    print(f'Out of  {len(result):,d} processed {files_processed:,d} files of total size {size_input:,d} input bytes')
    print(f'Wrote {size_index:,d} output bytes, ratio: {ratio:8.3%} at {exec_timer.ms_mb:.1f} ms/Mb')
    print(f'Processed: {size_input:,d} bytes at {exec_timer.ms_mb:.1f} ms/Mb')
    print('Bye, bye!')
    return ret_value


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
