"""
Scans a RP66V1 file an prints out the summary.
"""
import argparse
import collections
import logging
import os
import pprint
import sys
import time
import typing

import colorama

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
# from TotalDepth.RP66V1.core.Scan import scan_RP66V1_file_visible_records, scan_RP66V1_file_logical_data, \
#     scan_RP66V1_file_data_content, scan_RP66V1_file_EFLR_IFLR
from TotalDepth.RP66V1.core import Scan, HTML
from TotalDepth.util import gnuplot, XmlWrite
from TotalDepth.util.DirWalk import dirWalk
from TotalDepth.util import bin_file_type

colorama.init(autoreset=True)


__author__  = 'Paul Ross'
__date__    = '2019-03-21'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


logger = logging.getLogger(__file__)


# TODO: IndexFile and ScanFile are very similar, combine.

# IndexResult = collections.namedtuple('IndexResult', 'size_input, size_output, time, exception, ignored')

class FileResult(typing.NamedTuple):
    path_input: str
    path_output: str
    size_input: int
    size_output: int
    time: float
    exception: bool
    ignored: bool
    link_text: str



def scan_a_single_file(path_in: str, path_out: str, **kwargs) -> FileResult:
    logger.debug(f'Scanning "{path_in}" to "{path_out}"')
    # logging.info(f'index_a_single_file(): "{path_in}" to "{path_out}"')
    file_path_out = path_out + '.xhtml'
    binary_file_type = bin_file_type.binary_file_type_from_path(path_in)
    if binary_file_type == 'RP66V1':
        t_start = time.perf_counter()
        try:
            if path_out:
                out_dir = os.path.dirname(path_out)
                if not os.path.exists(out_dir):
                    logger.debug(f'Making directory: {out_dir}')
                    os.makedirs(out_dir, exist_ok=True)
                with open(file_path_out, 'w') as fout:
                    link_text = HTML.html_scan_RP66V1_file_data_content(path_in, fout, **kwargs)
                len_scan_output = os.path.getsize(file_path_out)
            else:
                link_text = HTML.html_scan_RP66V1_file_data_content(path_in, sys.stdout, **kwargs)
                len_scan_output = -1
            result = FileResult(
                path_in,
                file_path_out,
                os.path.getsize(path_in),
                len_scan_output,
                time.perf_counter() - t_start,
                False,
                False,
                link_text,
            )
        except ExceptionTotalDepthRP66V1:
            logger.exception(f'Failed to index with ExceptionTotalDepthRP66V1: {path_in}')
            result = FileResult(path_in, file_path_out, os.path.getsize(path_in), 0, 0.0, True, False, '')
        except Exception:
            logger.exception(f'Failed to index with Exception: {path_in}')
            result = FileResult(path_in, file_path_out, os.path.getsize(path_in), 0, 0.0, True, False, '')
    else:
        logger.debug(f'Ignoring file type "{binary_file_type}" at {path_in}')
        result = FileResult(path_in, file_path_out, 0, 0, 0.0, False, True, '')
    return result


CSS_RP66V1_INDEX = """/* CSS for RP66V1 */
body {
font-size:      12px;
font-family:    arial,helvetica,sans-serif;
margin:         6px;
padding:        6px;
}
h1 {
color:            darkgoldenrod;
font-family:      sans-serif;
font-size:        14pt;
font-weight:      bold;
}
h2 {
color:          IndianRed;
font-family:    sans-serif;
font-size:      14pt;
font-weight:    normal;
}
h3 {
color:          Black;
font-family:    sans-serif;
font-size:      12pt;
font-weight:    bold;
}
h4 {
color:          FireBrick;
font-family:    sans-serif;
font-size:      10pt;
font-weight:    bold;
}
span.line {
color:           slategrey;
/*font-style:    italic; */
}
span.file {
 color:         black;
 font-style:    italic;
}

table.filetable {
    border:         2px solid black;
    font-family:    monospace;
    color:          black;
}
th.filetable, td.filetable {
    /* border: 1px solid black; */
    border: 1px;
    border-top-style:solid;
    border-right-style:dotted;
    border-bottom-style:none;
    border-left-style:none;
    vertical-align:top;
    padding: 2px 6px 2px 6px; 
}


table.eflr {
    border:         2px solid black;
    font-family:    monospace;
    color:          black;
}
th.eflr, td.eflr {
    /* border: 1px solid black; */
    border: 1px;
    border-top-style:solid;
    border-right-style:dotted;
    border-bottom-style:none;
    border-left-style:none;
    vertical-align:top;
    padding: 2px 6px 2px 6px; 
}

table.monospace {
border:            2px solid black;
border-collapse:   collapse;
font-family:       monospace;
color:             black;
}
th.monospace, td.monospace {
border:            1px solid black;
vertical-align:    top;
padding:           2px 6px 2px 6px; 
}
"""


def _write_indexes(path_out: str, index: typing.Dict[str, FileResult]) -> None:
    assert os.path.isdir(path_out)
    INDEX_FILE = 'index.html'
    # print('TRACE:')
    # pprint.pprint(index)
    # Write low level indexes
    for root, dirs, files in os.walk(path_out):
        files_to_link_to = []
        for file in files:
            out_file_path = os.path.join(root, file)
            if out_file_path in index:
                files_to_link_to.append(file)#out_file_path)
        if len(files_to_link_to):
            with open(os.path.join(root, INDEX_FILE), 'w') as fout:
                with XmlWrite.XhtmlStream(fout) as xhtml_stream:
                    with XmlWrite.Element(xhtml_stream, 'head'):
                        with XmlWrite.Element(xhtml_stream, 'meta', {
                            'charset': "UTF-8",
                            'name': "viewport",
                            'content': "width=device-width, initial-scale=1",
                        }):
                            pass
                        with XmlWrite.Element(xhtml_stream, 'title'):
                            xhtml_stream.charactersWithBr(f'Index of RP66V1 Scan {root}')
                        with XmlWrite.Element(xhtml_stream, 'style'):
                            xhtml_stream.literal(CSS_RP66V1_INDEX)
                    with XmlWrite.Element(xhtml_stream, 'body'):
                        with XmlWrite.Element(xhtml_stream, 'table', {'class' : 'monospace'}):
                            with XmlWrite.Element(xhtml_stream, 'tr', {}):
                                for cell in ('File', 'Storage Unit Label'):
                                    with XmlWrite.Element(xhtml_stream, 'th', {}):
                                        xhtml_stream.characters(cell)
                            for file in files_to_link_to:
                                with XmlWrite.Element(xhtml_stream, 'tr', {}):
                                    with XmlWrite.Element(xhtml_stream, 'td', {}):
                                        with XmlWrite.Element(xhtml_stream, 'a', {'href': file}):
                                            xhtml_stream.characters(os.path.basename(file))
                                    with XmlWrite.Element(xhtml_stream, 'td', {}):
                                        xhtml_stream.characters(index[os.path.join(root, file)].link_text)
    # Write top level index, this might overwrite the index in a single directory
    # This index is just a table with two columns: directory, file
    index_map: typing.Dict[str, typing.List[str]] = collections.defaultdict(list)
    for k in index.keys():
        index_map[os.path.dirname(k)].append(k)
    index_file_path = os.path.join(path_out, INDEX_FILE)
    with open(index_file_path, 'w') as fout:
        with XmlWrite.XhtmlStream(fout) as xhtml_stream:
            with XmlWrite.Element(xhtml_stream, 'head'):
                with XmlWrite.Element(xhtml_stream, 'meta', {
                    'charset': "UTF-8",
                    'name': "viewport",
                    'content': "width=device-width, initial-scale=1",
                }):
                    pass
                with XmlWrite.Element(xhtml_stream, 'title'):
                    xhtml_stream.charactersWithBr(f'RP66V1 Scan of {path_out}')
                with XmlWrite.Element(xhtml_stream, 'style'):
                    xhtml_stream.literal(CSS_RP66V1_INDEX)
            with XmlWrite.Element(xhtml_stream, 'body'):
                with XmlWrite.Element(xhtml_stream, 'table', {'class' : 'monospace'}):
                    with XmlWrite.Element(xhtml_stream, 'tr', {}):
                        for cell in ('Directory', 'File'):
                            with XmlWrite.Element(xhtml_stream, 'th', {}):
                                xhtml_stream.characters(cell)
                    for directory in sorted(index_map.keys()):
                        with XmlWrite.Element(xhtml_stream, 'tr', {}):
                            with XmlWrite.Element(xhtml_stream, 'td', {}):
                                xhtml_stream.characters(directory)
                            with XmlWrite.Element(xhtml_stream, 'td', {}):
                                for file in sorted(index_map[directory]):
                                    # TODO: Fix href, has root duplicated
                                    relative_path = index[file].path_output[1+len(os.path.dirname(index_file_path)):]
                                    with XmlWrite.Element(xhtml_stream, 'a', {'href': relative_path}):
                                        xhtml_stream.characters(os.path.basename(file))
                                    with XmlWrite.Element(xhtml_stream, 'br', {}):
                                        pass


def scan_dir_or_file(path_in: str, path_out: str,
                     recurse: bool,
                     **kwargs) -> typing.Dict[str, FileResult]:
    logging.info(f'scan_dir_or_file(): "{path_in}" to "{path_out}" recurse: {recurse}')
    ret: typing.Dict[str, FileResult] = {}
    # Output file path to FIleResult
    index: typing.Dict[str, FileResult] = {}
    if os.path.isdir(path_in):
        for file_in_out in dirWalk(path_in, path_out, theFnMatch='', recursive=recurse, bigFirst=False):
            # print(file_in_out)
            result = scan_a_single_file(
                file_in_out.filePathIn, file_in_out.filePathOut, **kwargs
            )
            ret[file_in_out.filePathIn] = result
            if not result.exception and not result.ignored:
                index[result.path_output] = result
        # Now write all the index.xhtml
        _write_indexes(path_out, index)
    else:
        ret[path_in] = scan_a_single_file(path_in, path_out, **kwargs)
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


def plot_gnuplot(data: typing.Dict[str, FileResult], gnuplot_dir: str) -> None:
    if len(data) < 2:
        raise ValueError(f'Can not plot data with only {len(data)} points.')
    # First row is header row, create it then comment out the first item.
    table = [
        list(FileResult._fields) + ['Path']
    ]
    table[0][0] = f'# {table[0][0]}'
    for k in sorted(data.keys()):
        if data[k].size_input > 0 and not data[k].exception:
            table.append(list(data[k]) + [k])
    name = 'ScanFileHTML'
    return_code = gnuplot.invoke_gnuplot(gnuplot_dir, name, table, GNUPLOT_PLT.format(name=name))
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')
    return_code = gnuplot.write_test_file(gnuplot_dir, 'svg')
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')


def main() -> int:
    description = 'usage: %(prog)s [options] file'
    description = """Scans a RP66V1 file and dumps data in HTML"""
    # TODO: Use CmnCmdOpts
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
    # gnuplot.add_gnuplot_to_argument_parser(parser)
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
                        # format='%(asctime)s %(levelname)-8s %(message)s',
                        format='%(asctime)s - %(filename)s - %(process)d - %(levelname)-8s - %(message)s',
                        #datefmt='%y-%m-%d % %H:%M:%S',
                        stream=sys.stdout)
    clk_start = time.perf_counter()
    # return 0
    # Your code here
    result: typing.Dict[str, FileResult] = scan_dir_or_file(
        args.path_in,
        args.path_out,
        args.recurse,
        frame_spacing=args.frame_spacing,
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

    # if args.gnuplot:
    #     plot_gnuplot(result, args.gnuplot)
    if size_input > 0:
        ms_mb = clk_exec * 1000 / (size_input / 1024**2)
    else:
        ms_mb = 0.0
    print(f'Processed {len(result):,d} files and {size_input:,d} bytes, {ms_mb:.1f} ms/Mb')
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
