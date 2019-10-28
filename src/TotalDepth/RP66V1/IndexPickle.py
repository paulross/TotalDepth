"""Read RP66V1 files and saves the index a s pickle file."""
import argparse
import collections
import logging
import os
import pickle
import sys
import time
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import File, LogicalFile
from TotalDepth.common import process, td_logging, data_table
from TotalDepth.util import gnuplot
from TotalDepth.util.DirWalk import dirWalk
from TotalDepth.util.bin_file_type import binary_file_type_from_path


__author__  = 'Paul Ross'
__date__    = '2019-06-29'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


logger = logging.getLogger(__file__)


IndexResult = collections.namedtuple('IndexResult', 'size_input, size_index, time_write, time_read, exception, ignored')


def index_a_single_file(path_in: str, path_out: str, read_back: bool) -> IndexResult:
    if path_out:
        out_dir = os.path.dirname(path_out)
        if not os.path.exists(out_dir):
            logger.info(f'Making directory: {out_dir}')
            os.makedirs(out_dir, exist_ok=True)
    logger.info(f'Indexing {path_in} to pickle {path_out}')
    try:
        with open(path_in, 'rb') as fobj:
            t_start = time.perf_counter()
            rp66v1_file = File.FileRead(fobj)
            logical_index = LogicalFile.LogicalIndex(rp66v1_file, path_in)
            pickled_index = pickle.dumps(logical_index)
            # logger.info(f'Length of pickled index: {len(pickled_index)}')
            pickle_path = path_out + '.pkl'
            with open(pickle_path, 'wb') as out_stream:
                out_stream.write(pickled_index)
            write_time = time.perf_counter() - t_start
            if read_back:
                t_start = time.perf_counter()
                _read_index = LogicalFile.unpickle(pickle_path)
                read_time = time.perf_counter() - t_start
            else:
                read_time = 0.0
            result = IndexResult(os.path.getsize(path_in), len(pickled_index), write_time, read_time, False, False)
            return result
    except ExceptionTotalDepthRP66V1:
        logger.exception(f'Failed to index with ExceptionTotalDepthRP66V1: {path_in}')
    except Exception:
        logger.exception(f'Failed to index with Exception: {path_in}')
    return IndexResult(os.path.getsize(path_in), 0, 0.0, 0.0, True, False)


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


def main() -> int:
    description = """usage: %(prog)s [options] file
Scans a RP66V1 file or directory and saves the index as a pickled file."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = argparse.ArgumentParser(description=description, epilog=__rights__, prog=sys.argv[0])
    parser.add_argument('path_in', type=str, help='Path to the input.')
    parser.add_argument('path_out', type=str, help='Path to the directory of pickled indexes.')
    parser.add_argument('-r', '--recurse', action='store_true', help='Process recursively. [default: %(default)s]')
    parser.add_argument('--read-back', action='store_true', help='Read and time the output. [default: %(default)s]')
    td_logging.add_logging_option(parser)
    process.add_process_logger_to_argument_parser(parser)
    parser.add_argument(
        "-v", "--verbose", action='count', default=0,
        help="Increase verbosity, additive [default: %(default)s]",
    )
    gnuplot.add_gnuplot_to_argument_parser(parser)
    args = parser.parse_args()
    print('args:', args)
    # return 0
    td_logging.set_logging_from_argparse(args)
    # return 0
    # Your code here
    clk_start = time.perf_counter()
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
            if idx_result.size_input > 0:
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
                gnuplot.plot_gnuplot(result, args.gnuplot)
            except Exception:
                logger.exception('gunplot failed')
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
