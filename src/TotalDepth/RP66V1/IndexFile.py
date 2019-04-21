import argparse
import collections
import logging
import os
import sys
import time
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core.Index import FileIndexXML
from TotalDepth.util.DirWalk import dirWalk
from TotalDepth.util.bin_file_type import binary_file_type_from_path

__author__  = 'Paul Ross'
__date__    = '2019-04-10'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


logger = logging.getLogger(__file__)


IndexResult = collections.namedtuple('IndexResult', 'size_input, size_index, time, exception, ignored')


def index_a_single_file(path_in: str, path_out: str = '') -> IndexResult:
    # logging.info(f'index_a_single_file(): "{path_in}" to "{path_out}"')
    bin_file_type = binary_file_type_from_path(path_in)
    if bin_file_type == 'RP66V1':
        if path_out:
            out_dir = os.path.dirname(path_out)
            logger.info(f'Making directory: {out_dir}')
            os.makedirs(out_dir, exist_ok=True)
        logger.info(f'Indexing {path_in} to {path_out}')
        try:
            with open(path_in, 'rb') as fobj:
                t_start = time.perf_counter()
                index = FileIndexXML(fobj, path_in)
                xml_fobj = index.write_xml()
                index_output = xml_fobj.getvalue()
                result = IndexResult(
                    os.path.getsize(path_in),
                    len(index_output),
                    time.perf_counter() - t_start,
                    False,
                    False,
                )
                if path_out:
                    with open(path_out + '.xml', 'w') as f_out:
                        f_out.write(index_output)
                else:
                    print(index_output)
                logger.info(f'Length of XML: {len(index_output)}')
                return result
        except ExceptionTotalDepthRP66V1:
            logger.exception(f'Failed to index with ExceptionTotalDepthRP66V1: {path_in}')
            return IndexResult(os.path.getsize(path_in), 0, 0.0, True, False)
        except Exception:
            logger.exception(f'Failed to index with Exception: {path_in}')
            return IndexResult(os.path.getsize(path_in), 0, 0.0, True, False)
    logger.info(f'Ignoring file type "{bin_file_type}" at {path_in}')
    return IndexResult(0, 0, 0.0, False, True)


def index_dir_or_file(path_in: str, path_out: str, recurse: bool) -> typing.Dict[str, IndexResult]:
    logging.info(f'index_dir_or_file(): "{path_in}" to "{path_out}" recurse: {recurse}')
    ret = {}
    if os.path.isdir(path_in):
        for file_in_out in dirWalk(path_in, path_out, theFnMatch='', recursive=recurse, bigFirst=False):
            # print(file_in_out)
            ret[file_in_out.filePathIn] = index_a_single_file(file_in_out.filePathIn, file_in_out.filePathOut)
    else:
        ret[path_in] = index_a_single_file(path_in, path_out)
    return ret


def main() -> int:
    description = """usage: %(prog)s [options] file
Scans a RP66V1 file and dumps data."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = argparse.ArgumentParser(description=description, epilog=__rights__, prog=sys.argv[0])
    parser.add_argument('path_in', type=str, help='Path to the input.')
    parser.add_argument(
        'path_out', type=str,
        help='Path to the output.'
             'The results are undefined if path_out conflicts with path_in',
        default='',
        nargs='?')
    parser.add_argument(
        '-r', '--recurse', action='store_true',
        help='Process files recursively. [default: %(default)s]',
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
    args = parser.parse_args()
    print('args:', args)
    # return 0

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
    # return 0
    # Your code here
    clk_start = time.perf_counter()
    result: typing.Dict[str, IndexResult] = index_dir_or_file(
        args.path_in,
        args.path_out,
        args.recurse,
    )
    clk_exec = time.perf_counter() - clk_start
    size_index = size_input = 0
    files_processed = 0
    for path in sorted(result.keys()):
        idx_result = result[path]
        if idx_result.size_input > 0:
            ms_mb = idx_result.time * 1000 / (idx_result.size_input / 1024 ** 2)
            ratio = idx_result.size_index / idx_result.size_input
            print(
                f'{idx_result.size_input:16,d} {idx_result.size_index:10,d}'
                f' {idx_result.time:8.3f} {ratio:8.3%} {ms_mb:8.1f} {str(idx_result.exception):5}'
                f' {path}'
            )
            size_input += result[path].size_input
            size_index += result[path].size_index
            files_processed += 1
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
