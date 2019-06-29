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
from TotalDepth.common import process, Slice
from TotalDepth.util import gnuplot, XmlWrite, DictTree
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

class HTMLResult(typing.NamedTuple):
    path_input: str
    path_output: str
    size_input: int
    size_output: int
    time: float
    exception: bool
    ignored: bool
    html_summary: typing.Union[HTML.HTMLBodySummary, None]


def scan_a_single_file(path_in: str, path_out: str, **kwargs) -> HTMLResult:
    # logger.debug(f'Scanning "{path_in}" to "{path_out}"')
    file_path_out = path_out + '.xhtml'
    binary_file_type = bin_file_type.binary_file_type_from_path(path_in)
    if binary_file_type == 'RP66V1':
        # logging.info(f'ScanFileHTML.scan_a_single_file(): "{path_in}" to "{path_out}"')
        logging.info(f'ScanFileHTML.scan_a_single_file(): "{path_in}"')
        t_start = time.perf_counter()
        try:
            if path_out:
                out_dir = os.path.dirname(path_out)
                if not os.path.exists(out_dir):
                    logger.debug(f'Making directory: {out_dir}')
                    os.makedirs(out_dir, exist_ok=True)
                with open(file_path_out, 'w') as fout:
                    html_summary = HTML.html_scan_RP66V1_file_data_content(path_in, fout, **kwargs)
                len_scan_output = os.path.getsize(file_path_out)
            else:
                html_summary = HTML.html_scan_RP66V1_file_data_content(path_in, sys.stdout, **kwargs)
                len_scan_output = -1
            result = HTMLResult(
                path_in,
                file_path_out,
                os.path.getsize(path_in),
                len_scan_output,
                time.perf_counter() - t_start,
                False,
                False,
                html_summary,
            )
        except ExceptionTotalDepthRP66V1:
            logger.exception(f'Failed to index with ExceptionTotalDepthRP66V1: {path_in}')
            result = HTMLResult(path_in, file_path_out, os.path.getsize(path_in), 0, 0.0, True, False, None)
        except Exception:
            logger.exception(f'Failed to index with Exception: {path_in}')
            result = HTMLResult(path_in, file_path_out, os.path.getsize(path_in), 0, 0.0, True, False, None)
    else:
        logger.debug(f'Ignoring file type "{binary_file_type}" at {path_in}')
        result = HTMLResult(path_in, file_path_out, 0, 0, 0.0, False, True, None)
    return result


CSS_RP66V1_INDEX = """/* CSS for RP66V1 index pages */
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
/*    font-family:    monospace; */
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
"""

INDEX_FILE = 'index.html'


def _write_indexes(path_out: str, index: typing.Dict[str, HTMLResult]) -> None:
    assert os.path.isdir(path_out), f'{path_out} is not a directory'
    # print('TRACE: _write_indexes():')
    # pprint.pprint(index)
    _write_low_level_indexes(path_out, index)
    _write_top_level_index(path_out, index)


def _write_low_level_indexes(path_out: str, index: typing.Dict[str, HTMLResult]) -> None:
    assert os.path.isdir(path_out)
    # Write low level indexes
    for root, dirs, files in os.walk(path_out):
        files_to_link_to = []
        for file in files:
            out_file_path = os.path.join(root, file)
            if out_file_path in index:
                files_to_link_to.append(file)
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
                            xhtml_stream.charactersWithBr(f'Index of RP66V1 Scan: {root}')
                        with XmlWrite.Element(xhtml_stream, 'style'):
                            xhtml_stream.literal(CSS_RP66V1_INDEX)
                    with XmlWrite.Element(xhtml_stream, 'body'):
                        with XmlWrite.Element(xhtml_stream, 'h1'):
                            xhtml_stream.charactersWithBr(f'Index of RP66V1 Scan {root}')
                        with XmlWrite.Element(xhtml_stream, 'table', {'class': 'filetable'}):
                            with XmlWrite.Element(xhtml_stream, 'tr', {'class': 'filetable'}):
                                for header in ('Physical File', 'File', 'Frame Array', 'Frames', 'Channels', 'X Start', 'X Stop', 'dX', 'X Units'):
                                    with XmlWrite.Element(xhtml_stream, 'th', {'class': 'filetable'}):
                                        xhtml_stream.characters(header)
                            dict_tree = DictTree.DictTreeHtmlTable(None)
                            for file in files_to_link_to:
                                branch = [FileNameLinkHref(file, file, file)]
                                html_summary = index[os.path.join(root, file)].html_summary
                                for lf, logical_file_result in enumerate(html_summary.logical_files):
                                    branch.append(f'{lf}')
                                    for frame_array_result in logical_file_result.frame_arrays:
                                        # HTMLFrameArraySummary
                                        branch.append(frame_array_result.ident)
                                        dict_tree.add(branch, frame_array_result)
                                        branch.pop()
                                    branch.pop()
                            _write_low_level_index_table_body(xhtml_stream, dict_tree)


def _write_low_level_index_table_body(xhtml_stream: XmlWrite.XhtmlStream, dict_tree: DictTree.DictTreeHtmlTable) -> None:
    # Table body
    # print('TRACE:', dict_tree.indentedStr())
    file_href = ''
    for event in dict_tree.genColRowEvents():
        if event == dict_tree.ROW_OPEN:
            # Write out the '<tr>' element
            xhtml_stream.startElement('tr', {'class': 'filetable'})
        elif event == dict_tree.ROW_CLOSE:
            # Write out the '</tr>' element
            xhtml_stream.endElement('tr')
        else:
            td_attrs = {'class': 'filetable'}
            if event.row_span > 1:
                td_attrs['rowspan'] = f'{event.row_span:d}'
            if event.col_span > 1:
                td_attrs['colspan'] = f'{event.col_span:d}'
            if event.node is None:
                with XmlWrite.Element(xhtml_stream, 'td', td_attrs):
                    if isinstance(event.branch[-1], FileNameLinkHref):
                        file_href = event.branch[-1].href
                        with XmlWrite.Element(xhtml_stream, 'a', {'href': file_href}):
                            xhtml_stream.characters(str(event.branch[-1].file_name))
                    else:
                        xhtml_stream.characters(f'{str(event.branch[-1])}')
                    # xhtml_stream.characters(f'{str(event.branch[-1])}')
            else:
                node: HTML.HTMLFrameArraySummary = event.node
                # Frame Array
                with XmlWrite.Element(xhtml_stream, 'td', td_attrs):
                    with XmlWrite.Element(xhtml_stream, 'a', {'href': f'{file_href}#{node.href}'}):
                        xhtml_stream.characters(str(event.branch[-1]))
                # Write the node cells
                with XmlWrite.Element(xhtml_stream, 'td', {'class': 'filetable', 'align': 'right'}):
                    xhtml_stream.characters(f'{node.num_frames:,d}')
                with XmlWrite.Element(xhtml_stream, 'td', {'class': 'filetable', 'align': 'right'}):
                    xhtml_stream.characters(f'{len(node.channels):,d}')
                frame_spacing = (node.x_stop - node.x_start) / (node.num_frames - 1) if node.num_frames > 1 else 0.0
                for value in (f'{node.x_start:.1f}', f'{node.x_stop:.1f}', f'{frame_spacing:.1f}', f'{node.x_units.decode("ascii")}'):
                    with XmlWrite.Element(xhtml_stream, 'td', {'class': 'filetable', 'align': 'right'}):
                        xhtml_stream.characters(value)


class FileNameLinkHref(typing.NamedTuple):
    file_name: str
    link_text: str
    href: str


def _write_top_level_index(path_out: str, index_map: typing.Dict[str, HTMLResult]) -> None:
    # Create a DictTree from the paths.
    dict_tree = DictTree.DictTreeHtmlTable(None)
    for k in index_map:
        branch = k.split(os.sep)
        dict_tree.add(branch, index_map[k])

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
                with XmlWrite.Element(xhtml_stream, 'h1'):
                    xhtml_stream.charactersWithBr(f'Index of RP66V1 Scan: {path_out}')
                with XmlWrite.Element(xhtml_stream, 'table', {'class': 'filetable'}):
                    _write_top_level_index_table_body(index_file_path, dict_tree, xhtml_stream)


def _write_top_level_index_table_body(index_file_path: str,
                                      dict_tree: DictTree.DictTreeHtmlTable,
                                      xhtml_stream: XmlWrite.XhtmlStream) -> None:
    strip_out_path = len(os.path.dirname(index_file_path)) + 1
    for event in dict_tree.genColRowEvents():
        if event == dict_tree.ROW_OPEN:
            # Write out the '<tr>' element
            xhtml_stream.startElement('tr', {'class': 'filetable'})
        elif event == dict_tree.ROW_CLOSE:
            # Write out the '</tr>' element
            xhtml_stream.endElement('tr')
        else:
            td_attrs = {'class': 'filetable'}
            if event.row_span > 1:
                td_attrs['rowspan'] = f'{event.row_span:d}'
            if event.col_span > 1:
                td_attrs['colspan'] = f'{event.col_span:d}'
            if event.node is None:
                with XmlWrite.Element(xhtml_stream, 'td', td_attrs):
                    if isinstance(event.branch[-1], FileNameLinkHref):
                        # TODO: Is this code block used?
                        # file_href = event.branch[-1].href
                        with XmlWrite.Element(xhtml_stream, 'a', {'href': event.branch[-1].href}):
                            xhtml_stream.characters(str(event.branch[-1].file_name))
                    else:
                        xhtml_stream.characters(f'{str(event.branch[-1])}')
            else:
                node: HTMLResult = event.node
                with XmlWrite.Element(xhtml_stream, 'td', td_attrs):
                    with XmlWrite.Element(xhtml_stream, 'a', {'href': f'{node.path_output[strip_out_path:]}'}):
                        xhtml_stream.characters(str(event.branch[-1]))


def scan_dir_or_file(path_in: str, path_out: str,
                     recurse: bool,
                     **kwargs) -> typing.Dict[str, HTMLResult]:
    logging.info(f'scan_dir_or_file(): "{path_in}" to "{path_out}" recurse: {recurse}')
    ret: typing.Dict[str, HTMLResult] = {}
    # Output file path to FIleResult
    index_map: typing.Dict[str, HTMLResult] = {}
    if os.path.isdir(path_in):
        for file_in_out in dirWalk(path_in, path_out, theFnMatch='', recursive=recurse, bigFirst=False):
            # print(file_in_out)
            result = scan_a_single_file(
                file_in_out.filePathIn, file_in_out.filePathOut, **kwargs
            )
            ret[file_in_out.filePathIn] = result
            if not result.exception and not result.ignored:
                index_map[result.path_output] = result
        # Now write all the index.xhtml
        _write_indexes(path_out, index_map)
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
set y2label "Scan time (s), Ratio original size / HTML size"
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


def plot_gnuplot(data: typing.Dict[str, HTMLResult], gnuplot_dir: str) -> None:
    if len(data) < 2:
        raise ValueError(f'Can not plot data with only {len(data)} points.')
    # First row is header row, create it then comment out the first item.
    table = [
        # list(HTMLResult._fields) + ['Path']
        ['size_input', 'size_output', 'time', 'Path']
    ]
    table[0][0] = f'# {table[0][0]}'
    for k in sorted(data.keys()):
        if data[k].size_input > 0 and not data[k].exception:
            # table.append(list(data[k]) + [k])
            table.append(
                [
                    data[k].size_input,
                    data[k].size_output,
                    data[k].time,
                    k
                ]
            )
    name = 'ScanFileHTML'
    return_code = gnuplot.invoke_gnuplot(gnuplot_dir, name, table, GNUPLOT_PLT.format(name=name))
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')
    return_code = gnuplot.write_test_file(gnuplot_dir, 'svg')
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')


def main() -> int:
    description = 'usage: %(prog)s [options] file'
    description = """Scans a RP66V1 file or directory and writes HTML version of the data."""
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
    Slice.add_frame_slice_to_argument_parser(parser)
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
    # Your code here
    if args.log_process > 0.0:
        with process.log_process(args.log_process):
            result: typing.Dict[str, HTMLResult] = scan_dir_or_file(
                args.path_in,
                args.path_out,
                args.recurse,
                # frame_spacing=args.frame_spacing,
                frame_slice=Slice.create_slice(args.frame_slice),
            )
    else:
        result: typing.Dict[str, HTMLResult] = scan_dir_or_file(
            args.path_in,
            args.path_out,
            args.recurse,
            # frame_spacing=args.frame_spacing,
            frame_slice=Slice.create_slice(args.frame_slice),
        )
    clk_exec = time.perf_counter() - clk_start
    # print('Execution time = %8.3f (S)' % clk_exec)
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
        try:
            plot_gnuplot(result, args.gnuplot)
        except IOError:
            logger.exception('Plotting with gnuplot failed.')
    if size_input > 0:
        ms_mb = clk_exec * 1000 / (size_input / 1024**2)
    else:
        ms_mb = 0.0
    print(f'Processed {len(result):,d} files and {size_input:,d} bytes in {clk_exec:.3f} s, {ms_mb:.1f} ms/Mb')
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
