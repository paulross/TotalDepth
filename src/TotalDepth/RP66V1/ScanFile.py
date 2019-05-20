"""
Scans a RP66V1 file an prints out the summary.
"""
import argparse
import collections
import logging
import os
import sys
import time
import typing

import colorama

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core.Scan import scan_RP66V1_file_visible_records, scan_RP66V1_file_logical_data, \
    scan_RP66V1_file_data_content, scan_RP66V1_file_EFLR_IFLR
from TotalDepth.util import gnuplot
from TotalDepth.util.DirWalk import dirWalk
from TotalDepth.util.bin_file_type import binary_file_type, BINARY_FILE_TYPE_CODE_WIDTH, binary_file_type_from_path

colorama.init(autoreset=True)


__author__  = 'Paul Ross'
__date__    = '2019-03-21'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


logger = logging.getLogger(__file__)


# TODO: IndexFile and ScanFile are very similar, combine.
IndexResult = collections.namedtuple('IndexResult', 'size_input, size_output, time, exception, ignored')


def scan_a_single_file(path_in: str, path_out: str, function: typing.Callable, **kwargs) -> IndexResult:
    # logging.info(f'index_a_single_file(): "{path_in}" to "{path_out}"')
    bin_file_type = binary_file_type_from_path(path_in)
    if bin_file_type == 'RP66V1':
        logger.info(f'Scanning "{path_in}" to "{path_out}"')
        with open(path_in, 'rb') as fobj:
            t_start = time.perf_counter()
            try:
                if path_out:
                    out_dir = os.path.dirname(path_out)
                    if not os.path.exists(out_dir):
                        logger.info(f'Making directory: {out_dir}')
                        os.makedirs(out_dir, exist_ok=True)
                    with open(path_out + '.txt', 'w') as fout:
                        function(fobj, fout, **kwargs)
                    len_scan_output = os.path.getsize(path_out + '.txt')
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
    logger.info(f'Ignoring file type "{bin_file_type}" at {path_in}')
    return IndexResult(0, 0, 0.0, False, True)


def scan_dir_or_file(path_in: str, path_out: str, function: typing.Callable, recurse: bool, **kwargs) -> typing.Dict[str, IndexResult]:
    logging.info(f'scan_dir_or_file(): "{path_in}" to "{path_out}" with {function} recurse: {recurse}')
    ret = {}
    if os.path.isdir(path_in):
        for file_in_out in dirWalk(path_in, path_out, theFnMatch='', recursive=recurse, bigFirst=False):
            # print(file_in_out)
            ret[file_in_out.filePathIn] = scan_a_single_file(file_in_out.filePathIn, file_in_out.filePathOut, function, **kwargs)
    else:
        ret[path_in] = scan_a_single_file(path_in, path_out, function, **kwargs)
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
    description = """Scans a RP66V1 file and dumps data from the lowest level upwards:
    --VR ~ Visible Records only.
    --LRSH ~ Logical Record segments.
    --LD ~ Logical data i.e. all Logical Record segments concatenated for each Logical Record.
    --EFLR ~ Explicitly Formatted Logical Records.
    --IFLR ~ Implicitly Formatted Logical Records.
    --LR ~ All data, including frame data from all Logical Records.
    """
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = argparse.ArgumentParser(
        description=description,
        epilog=__rights__,
        prog=sys.argv[0],
    )
    parser.add_argument('path_in', type=str, help='Path to the input file.')
    parser.add_argument('path_out', type=str, default='', nargs='?', help='Path to the output scan to write.')
    # parser.add_argument(
    #     '--version', action='version', version='%(prog)s Version: ' + __version__,
    #     help='Show version and exit.'
    # )
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
    parser.add_argument(
        '--frame-spacing', type=int, default=1,
        help='With --LR read log data at this frame spacing.'
             ' For example --frame-spacing=8 then read every eighth frame. [default: %(default)s]',
    )
    parser.add_argument(
        '--eflr-as-table', action='store_true',
        help='With --LR dump EFLRs as tables, otherwise every EFLR object. [default: %(default)s]',
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
    if args.VR or args.LRSH:
        result = scan_dir_or_file(
            args.path_in,
            args.path_out,
            scan_RP66V1_file_visible_records,
            args.recurse,
            # kwargs
            lrsh_dump=args.LRSH,
            verbose=args.verbose,
        )
    if args.LD:
        result = scan_dir_or_file(
            args.path_in,
            args.path_out,
            scan_RP66V1_file_logical_data,
            args.recurse,
            # kwargs
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
            # kwargs
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
            # kwargs
            # verbose=args.verbose,
            # encrypted=args.encrypted,
            # keep_going=args.keep_going,
            # eflr_set_type=[bytes(v, 'ascii') for v in args.eflr_set_type],
            # iflr_set_type=[bytes(v, 'ascii') for v in args.iflr_set_type],
            # iflr_dump=args.IFLR,
            # eflr_dump=args.EFLR,
            rp66v1_path=args.path_in,
            frame_spacing=args.frame_spacing,
            eflr_as_table=args.eflr_as_table,
        )
    clk_exec = time.perf_counter() - clk_start
    print('Execution time = %8.3f (S)' % clk_exec)
    size_scan = size_input = 0
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

    if args.gnuplot:
        plot_gnuplot(result, args.gnuplot)
    if size_input > 0:
        ms_mb = clk_exec * 1000 / (size_input / 1024**2)
    else:
        ms_mb = 0.0
    print(f'Processed {len(result):,d} files and {size_input:,d} bytes, {ms_mb:.1f} ms/Mb')
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
