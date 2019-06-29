import argparse
import collections
import io
import logging
import os
import sys
import time
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import LogicalFile, File
from TotalDepth.RP66V1.core import Index
from TotalDepth.common import process
from TotalDepth.util.DirWalk import dirWalk
from TotalDepth.util.bin_file_type import binary_file_type_from_path
from TotalDepth.util import gnuplot

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
            if not os.path.exists(out_dir):
                logger.info(f'Making directory: {out_dir}')
                os.makedirs(out_dir, exist_ok=True)
        logger.info(f'Indexing {path_in} to {path_out}')
        try:
            with open(path_in, 'rb') as fobj:
                t_start = time.perf_counter()
                # index = RP66V1IndexXMLWrite(fobj, path_in)
                rp66v1_file = File.FileRead(fobj)
                logical_file_sequence = LogicalFile.LogicalIndex(rp66v1_file, path_in)
                if path_out:
                    with open(path_out + '.xml', 'w') as f_out:
                        Index.write_logical_file_sequence_to_xml(logical_file_sequence, f_out)
                    index_size = os.path.getsize(path_out + '.xml')
                else:
                    xml_fobj = io.StringIO()
                    Index.write_logical_file_sequence_to_xml(logical_file_sequence, xml_fobj)
                    index_output = xml_fobj.getvalue()
                    index_size = len(index_output)
                    print(index_output)
                result = IndexResult(
                    os.path.getsize(path_in),
                    index_size,
                    time.perf_counter() - t_start,
                    False,
                    False,
                )
                logger.info(f'Length of XML: {index_size}')
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

GNUPLOT_PLT = """set logscale x
set grid
set title "XML Index of RP66V1 Files with IndexFile.py."
set xlabel "RP66V1 File Size (bytes)"
# set mxtics 5
# set xrange [0:3000]
# set xtics
# set format x ""

set logscale y
set ylabel "XML Index Rate (ms/Mb)"
# set yrange [1:1e5]
# set ytics 20
# set mytics 2
# set ytics 8,35,3

set logscale y2
set y2label "Ratio index size / original size"
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
fit compression_ratio(x) "{name}.dat" using 1:($2/$1) via e,f

set terminal svg size 1000,700 # choose the file format
set output "{name}.svg" # choose the output device

# set key off

#set key title "Window Length"
#  lw 2 pointsize 2

# Fields: size_input, size_index, time, exception, ignored, path

plot "{name}.dat" using 1:($3*1000/($1/(1024*1024))) axes x1y1 title "XML Index Rate (ms/Mb)" lt 1 w points,\
    rate(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", a, b) lt 1 lw 2, \
    "{name}.dat" using 1:($2/$1) axes x1y2 title "XML Index size / Original Size" lt 2 w points, \
    compression_ratio(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", e, f) axes x1y2 lt 2 lw 2

# Plot size ratio:
#    "{name}.dat" using 1:($2/$1) axes x1y2 title "Index size ratio" lt 3 w points, \
#     size_ratio(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", c, d) axes x1y2 lt 3 lw 2

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
    name = 'IndexFile'
    return_code = gnuplot.invoke_gnuplot(gnuplot_dir, name, table, GNUPLOT_PLT.format(name=name))
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')
    return_code = gnuplot.write_test_file(gnuplot_dir, 'svg')
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')


def main() -> int:
    description = """usage: %(prog)s [options] file
Scans a RP66V1 file and writes out the index in XML."""
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
    process.add_process_logger_to_argument_parser(parser)
    parser.add_argument(
        "-v", "--verbose", action='count', default=0,
        help="Increase verbosity, additive [default: %(default)s]",
    )
    gnuplot.add_gnuplot_to_argument_parser(parser)
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
    if args.log_process > 0.0:
        with process.log_process(args.log_process):
            result: typing.Dict[str, IndexResult] = index_dir_or_file(
                args.path_in,
                args.path_out,
                args.recurse,
            )
    else:
        result: typing.Dict[str, IndexResult] = index_dir_or_file(
            args.path_in,
            args.path_out,
            args.recurse,
        )
    clk_exec = time.perf_counter() - clk_start
    size_index = size_input = 0
    files_processed = 0
    try:
        for path in sorted(result.keys()):
            idx_result = result[path]
            if idx_result.size_input > 0:
                ms_mb = idx_result.time * 1000 / (idx_result.size_input / 1024 ** 2)
                ratio = idx_result.size_index / idx_result.size_input
                print(
                    f'{idx_result.size_input:16,d} {idx_result.size_index:10,d}'
                    f' {idx_result.time:8.3f} {ratio:8.3%} {ms_mb:8.1f} {str(idx_result.exception):5}'
                    f' "{path}"'
                )
                size_input += result[path].size_input
                size_index += result[path].size_index
                files_processed += 1
        if args.gnuplot:
            try:
                plot_gnuplot(result, args.gnuplot)
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
