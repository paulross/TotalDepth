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
import logging
import multiprocessing
import os
import sys
import time
import typing

from TotalDepth.LAS.core import LASRead
from TotalDepth.common import cmn_cmd_opts, process, ToHTML, Slice, AbsentValue, np_summary
from TotalDepth.util import gnuplot, XmlWrite, bin_file_type, DirWalk

# import cPyMemTrace


__author__ = 'Paul Ross'
__date__ = '2020-09-05'
__version__ = '0.1.0'
__rights__ = 'Copyright (c) 2020 Paul Ross'


logger = logging.getLogger(__file__)


CSS_LAS = """/* CSS for LAS */
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


table.las {
    border:         2px solid black;
    border-collapse:   collapse;
    font-family:    monospace;
    color:          black;
}

th.las, td.las {
    border:            1px solid black;
    vertical-align:    top;
    padding:           2px 6px 2px 6px; 
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


TOP = 'Top'


class LASFileResult(typing.NamedTuple):
    """The result of processing a LAS file to HTML."""
    path_input: str
    path_output: str
    size_input: int
    size_output: int
    binary_file_type: str
    process_time: float
    exception: bool
    ignored: bool
    sections: typing.Tuple[str, ...]
    channels: typing.Tuple[str, ...]
    x_start: typing.Any  # float, time, date
    x_stop: typing.Any  # float, time, date
    x_step: typing.Any  # float, time, date
    number_frames: int


def _las_file_ignored(path_in, binary_file_type) -> LASFileResult:
    return LASFileResult(
        path_in, '', os.path.getsize(path_in), 0, binary_file_type,
        0.0,
        False, True,
        tuple(), tuple(),
        None, None, None, 0
    )


def _las_file_exception(path_in, binary_file_type) -> LASFileResult:
    return LASFileResult(
        path_in, '', os.path.getsize(path_in), 0, binary_file_type,
        0.0,
        True, False,
        tuple(), tuple(),
        None, None, None, 0
    )


def las_section_members_to_html_table(members: typing.List[LASRead.SectLine], xhtml_stream: XmlWrite.XhtmlStream) -> None:
    with XmlWrite.Element(xhtml_stream, 'table', {'class': 'las'}):
        with XmlWrite.Element(xhtml_stream, 'tr', {}):
            for col_name in ('Mnemonic', 'Units', 'Value', 'Description'):
                with XmlWrite.Element(xhtml_stream, 'th', {'class': 'las'}):
                    xhtml_stream.characters(col_name)
        for row in members:
            with XmlWrite.Element(xhtml_stream, 'tr', {}):
                with XmlWrite.Element(xhtml_stream, 'td', {'class': 'las'}):
                    xhtml_stream.characters(row.mnem)
                with XmlWrite.Element(xhtml_stream, 'td', {'class': 'las'}):
                    xhtml_stream.characters(str(row.unit))
                with XmlWrite.Element(xhtml_stream, 'td', {'class': 'las'}):
                    xhtml_stream.characters(str(row.valu))
                with XmlWrite.Element(xhtml_stream, 'td', {'class': 'las'}):
                    xhtml_stream.characters(str(row.desc))


def las_section_lines_to_html_table(members: typing.List[str], xhtml_stream: XmlWrite.XhtmlStream) -> None:
    for line in members:
        with XmlWrite.Element(xhtml_stream, 'pre', {'class': 'las'}):
            xhtml_stream.characters(line)


def las_section_to_html(las_section: LASRead.LASSection, xhtml_stream:XmlWrite.XhtmlStream) -> None:
    with XmlWrite.Element(xhtml_stream, 'a', {'name': las_section.type}):
        pass
    with XmlWrite.Element(xhtml_stream, 'h2', {'class': 'las_h2'}):
        with XmlWrite.Element(xhtml_stream, 'p', {'class': 'las_p'}):
            description = LASRead.SECT_DESCRIPTION_MAP.get(las_section.type, "")
            xhtml_stream.characters(
                f'LAS Section "{las_section.type}" - {description}'
            )
    if len(las_section):
        if las_section.type in LASRead.SECT_TYPES_WITH_DATA_LINES:
            las_section_members_to_html_table(las_section.members, xhtml_stream)
        else:
            las_section_lines_to_html_table(las_section.members, xhtml_stream)
    _write_link_to_top(xhtml_stream)


def write_file_metadata(las_file_path: str, xhtml_stream:XmlWrite.XhtmlStream) -> None:
    table = [
        ['Field', 'Value'],
        ['Path', las_file_path],
        ['Size', f'{os.path.getsize(las_file_path):,d}'],
        ['Mod time', f'{time.ctime(os.path.getmtime(las_file_path))}'],
    ]
    with XmlWrite.Element(xhtml_stream, 'h2', {'class': 'las_h2'}):
        xhtml_stream.characters(f'File Metadata')
    ToHTML.html_write_table(table, xhtml_stream, class_style='monospace')


def _write_link_to_top(xhtml_stream: XmlWrite.XhtmlStream) -> None:
    with XmlWrite.Element(xhtml_stream, 'a', {'href': f'#{TOP}'}):
        with XmlWrite.Element(xhtml_stream, 'p', {}):
            xhtml_stream.characters(TOP)


def write_file_array(las_file: LASRead.LASRead, xhtml_stream: XmlWrite.XhtmlStream) -> None:
    if las_file.frame_array is not None:
        with XmlWrite.Element(xhtml_stream, 'a', {'name': 'A'}):
            pass
        with XmlWrite.Element(xhtml_stream, 'h2', {'class': 'las_h2'}):
            xhtml_stream.characters(f'LAS Section "A" - Array Section')
        frame_table = [
            ['Channel',
             # 'Dims', 'Count',
             'Units', 'Long Name',
             'Size', 'Absent', 'Min', 'Mean', 'Median', 'Std.Dev.', 'Max', 'Span', '--', '==', '++', 'Activity', 'Drift',
             'dtype'],
        ]
        for channel in las_file.frame_array.channels:
            array_summary = np_summary.summarise_array(channel.array)
            if array_summary is not None:
                frame_table.append(
                    [
                        channel.ident,
                        # stringify(channel.dimensions),
                        # stringify(channel.count),
                        # Example:
                        # HKLA.1000 lbf :(RT)    (DRILLING_SURFACE)      (6in)                   Average Hookload
                        # Units seen as '1000' and interpreted as int.
                        str(channel.units),
                        channel.long_name,
                        f'{array_summary.len:d}',
                        f'{array_summary.len - array_summary.count:d}',
                        f'{array_summary.min:.3f}',
                        f'{array_summary.mean:.3f}',
                        f'{array_summary.median:.3f}',
                        f'{array_summary.std:.3f}',
                        f'{array_summary.max:.3f}',
                        f'{array_summary.span:.3f}',
                        f'{array_summary.count_dec:d}',
                        f'{array_summary.count_eq:d}',
                        f'{array_summary.count_inc:d}',
                        f'{array_summary.activity:.5f}',
                        f'{array_summary.drift:.5f}',
                        f'{channel.array.dtype}',
                    ]
                )
        ToHTML.html_write_table(frame_table, xhtml_stream, class_style='monospace')
        _write_link_to_top(xhtml_stream)


def _channels_from_las_file(las_file: LASRead.LASRead) -> typing.Tuple[str, ...]:
    if las_file.has_section('C'):
        curve_section = las_file['C']
        if len(curve_section.mnemonics()) <= 8:
            return tuple(curve_section.mnemonics())
        return tuple(curve_section.mnemonics()[:4] + ['...'] + curve_section.mnemonics()[-4:])
    return tuple()


def _sections_from_las_file(las_file: LASRead.LASRead) -> typing.Tuple[str, ...]:
    return tuple(section.type for section in las_file.generate_sections())


def _x_values_from_las_file(las_file: LASRead.LASRead) -> typing.Tuple[str, str, str]:
    x_start = x_stop = x_step = ''
    if las_file.has_section('W'):
        well_section = las_file['W']
        if 'STRT' in well_section:
            entry = well_section["STRT"]
            x_start = f'{stringify(entry.valu, 1)} ({entry.unit})'
        if 'STOP' in well_section:
            entry = well_section["STOP"]
            x_stop = f'{stringify(entry.valu, 1)} ({entry.unit})'
        if 'STEP' in well_section:
            entry = well_section["STEP"]
            x_step = f'{stringify(entry.valu, 4)} ({entry.unit})'
    return x_start, x_stop, x_step


def write_forward_index(las_file: LASRead.LASRead, xhtml_stream: XmlWrite.XhtmlStream) -> None:
    """Writes the index as a list of links to sections."""
    with XmlWrite.Element(xhtml_stream, 'h2', {'class': 'las_h2'}):
        with XmlWrite.Element(xhtml_stream, 'p', {'class': 'las_p'}):
            xhtml_stream.characters('LAS Sections')
    with XmlWrite.Element(xhtml_stream, 'ul', {'class': 'las_ul'}):
        for las_section in las_file.generate_sections():
            with XmlWrite.Element(xhtml_stream, 'li', {'class': 'las_li'}):
                with XmlWrite.Element(xhtml_stream, 'a', {'href': f'#{las_section.type}'}):
                    with XmlWrite.Element(xhtml_stream, 'p', {}):
                        if las_section.type in LASRead.SECT_DESCRIPTION_MAP:
                            xhtml_stream.characters(
                                f'{LASRead.SECT_DESCRIPTION_MAP[las_section.type]}'
                            )
                        else:
                            xhtml_stream.characters(f'Unknown section type {las_section.type}')


def las_file_to_html(las_file_path: str, html_file_path: str, binary_file_type: str, keep_going: bool,
                     label_process: bool, frame_slice: typing.Union[Slice.Slice, Slice.Sample]) -> LASFileResult:
    """Read a LAS file and write an HTML summary to the given path."""
    # TODO: use label_process, frame_slice
    time_start = time.perf_counter()
    las_file = LASRead.LASRead(las_file_path, las_file_path, raise_on_error=not keep_going)
    with open(html_file_path, 'w') as html_file:
        with XmlWrite.XhtmlStream(html_file) as xhtml_stream:
            with XmlWrite.Element(xhtml_stream, 'head'):
                with XmlWrite.Element(xhtml_stream, 'meta', {
                    'charset': "UTF-8",
                    'name': "viewport",
                    'content': "width=device-width, initial-scale=1",
                }):
                    pass
                with XmlWrite.Element(xhtml_stream, 'title'):
                    xhtml_stream.charactersWithBr(f'LAS Scan of {las_file_path}')
                with XmlWrite.Element(xhtml_stream, 'style'):
                    xhtml_stream.literal(CSS_LAS)
            with XmlWrite.Element(xhtml_stream, 'body'):
                # Anchor at top of document.
                with XmlWrite.Element(xhtml_stream, 'a', {'name': TOP}):
                    pass
                write_file_metadata(las_file_path, xhtml_stream)
                write_forward_index(las_file, xhtml_stream)
                for las_section in las_file.generate_sections():
                    if las_section.type != 'A':
                        las_section_to_html(las_section, xhtml_stream)
                write_file_array(las_file, xhtml_stream)
                with XmlWrite.Element(xhtml_stream, 'p', {'class': 'las_p'}):
                    xhtml_stream.characters(
                        f'Produced by TotalDepth.LAS.LASToHTML version {__version__} copyright {__rights__}'
                    )
    x_start, x_stop, x_step = _x_values_from_las_file(las_file)
    ret = LASFileResult(
        las_file_path, html_file_path, os.path.getsize(las_file_path), os.path.getsize(html_file_path),
        binary_file_type,
        time.perf_counter() - time_start, False, False,
        _sections_from_las_file(las_file),
        _channels_from_las_file(las_file),
        x_start, x_stop, x_step, las_file.number_of_frames()
    )
    return ret


def scan_a_single_file(path_in: str, path_out: str, keep_going: bool, label_process: bool,
                       frame_slice: typing.Union[Slice.Slice, Slice.Sample]) -> LASFileResult:
    """Scan a single file and write out an HTML summary."""
    file_path_out = path_out + '.html'
    binary_file_type = bin_file_type.binary_file_type_from_path(path_in)
    logger.info(f'Scanning file type "{binary_file_type}" from "{path_in}" to "{file_path_out}"')
    if binary_file_type in bin_file_type.LAS_BINARY_FILE_TYPES:
        logging.info(f'scan_a_single_file(): "{path_in}" to "{file_path_out}"')
        try:
            out_dir = os.path.dirname(path_out)
            if not os.path.exists(out_dir):
                logger.debug(f'Making directory: {out_dir}')
                os.makedirs(out_dir, exist_ok=True)
            result = las_file_to_html(path_in, file_path_out, binary_file_type, keep_going, label_process, frame_slice)
        except LASRead.ExceptionLASRead:
            logger.exception(f'Failed to index with ExceptionLASRead: {path_in}')
            result = _las_file_exception(path_in, binary_file_type)
        except Exception as err:
            logger.critical(f'Failed to index with Exception {err}: {path_in}')
            logger.exception(f'Failed to index with ExceptionLASRead: {path_in}')
            result = _las_file_exception(path_in, binary_file_type)
    else:
        logger.debug(f'Ignoring file type "{binary_file_type}" at {path_in}')
        result = _las_file_ignored(path_in, binary_file_type)
    return result


def stringify(obj: typing.Any, decimal_places: int) -> str:
    """Turn and object into a string, floats are formatted to the given number of decimal places."""
    if isinstance(obj, float):
        return f'{obj:.{decimal_places}f}'
    return str(obj)


def write_indexes(result_map: typing.Dict[str, LASFileResult]) -> None:
    """Write all the index.html files for the output tree."""
    logger.info(f'_write_indexes(): result map size %d', len(result_map))
    idx = ToHTML.IndexHTML(['File Type', 'Sections', 'Channels', 'Frames', 'STRT', 'STOP', 'STEP', 'Size', 'Time',])
    for path in result_map:
        if not (result_map[path].exception or result_map[path].ignored):
            idx.add(
                result_map[path].path_output,
                result_map[path].binary_file_type,
                ', '.join(result_map[path].sections),
                ', '.join(result_map[path].channels),
                f'{result_map[path].number_frames:,d}',
                result_map[path].x_start,
                result_map[path].x_stop,
                result_map[path].x_step,
                f'{result_map[path].size_input:,d}',
                f'{result_map[path].process_time:.3f} (s)',
            )
    index_paths = idx.write_indexes(create_intermediate=True, class_style='filetable', css=ToHTML.CSS_INDEX)
    logger.info(f'Wrote indexes: {index_paths}')


def scan_dir_multiprocessing(dir_in: str, dir_out: str,
                             recursive: bool, keep_going: bool, label_process: bool,
                             frame_slice: typing.Union[Slice.Slice, Slice.Sample],
                             jobs: int) -> typing.Dict[str, LASFileResult]:
    """Multiprocessing code to plot log passes.
    Returns a dict of {path_in : HTMLResult, ...}"""
    assert os.path.isdir(dir_in)
    if jobs < 1:
        jobs = multiprocessing.cpu_count()
    logging.info('scan_dir_multiprocessing(): Setting multi-processing jobs to %d' % jobs)
    pool = multiprocessing.Pool(processes=jobs)
    tasks = [
        (t.filePathIn, t.filePathOut, keep_going, label_process, frame_slice) for t in DirWalk.dirWalk(
            dir_in, dir_out, theFnMatch='', recursive=recursive, bigFirst=True
        )
    ]
    # print('tasks:')
    # pprint.pprint(tasks, width=200)
    # return {}
    results = [
        r.get() for r in [
            pool.apply_async(scan_a_single_file, t) for t in tasks
        ]
    ]
    write_indexes({r.path_output: r for r in results})
    return {r.path_input: r for r in results}


def scan_dir_or_file(path_in: str, path_out: str,
                     recursive: bool, keep_going: bool, label_process: bool,
                     frame_slice: typing.Union[Slice.Slice, Slice.Sample]) -> typing.Dict[str, LASFileResult]:
    """Scans a directory or file putting the results in path_out.
    Returns a dict of {path_in : HTMLResult, ...}
    """
    # Required as we are going to split them by os.sep
    # NOTE: normpath removes trailing os.sep which is what we want.
    path_in = os.path.normpath(path_in)
    path_out = os.path.normpath(path_out)
    logging.info(f'scan_dir_or_file(): "{path_in}" to "{path_out}" recurse: {recursive}')
    ret: typing.Dict[str, LASFileResult] = {}
    if os.path.isdir(path_in):
        if not recursive:
            for file_in_out in DirWalk.dirWalk(path_in, path_out, theFnMatch='', recursive=recursive, bigFirst=False):
                result = scan_a_single_file(
                    file_in_out.filePathIn, file_in_out.filePathOut, keep_going, label_process, frame_slice
                )
                ret[file_in_out.filePathIn] = result
        else:
            len_path_in = len(path_in.split(os.sep))
            # file_count = 0
            for root, _dirs, files in os.walk(path_in, topdown=False):
                root_rel_to_path_in = root.split(os.sep)[len_path_in:]
                dir_out = os.path.join(path_out, *root_rel_to_path_in)
                # if label_process and file_count % 16 == 0:
                #     process.add_message_to_queue(f'Dir {file_count}: {os.sep.join(root_rel_to_path_in)}')
                #     file_count += 1
                for file in sorted(files):
                    file_path_in = os.path.join(root, file)
                    file_path_out = os.path.join(dir_out, file)
                    # if label_process:
                    #     process.add_message_to_queue(f'{os.path.basename(file_path_in)}')
                    result = scan_a_single_file(file_path_in, file_path_out, keep_going, label_process, frame_slice)
                    ret[file_path_in] = result
    else:
        ret[path_in] = scan_a_single_file(path_in, path_out, keep_going, label_process, frame_slice)
    if label_process:
        process.add_message_to_queue('Writing Indexes.')
    write_indexes(ret)
    return ret


GNUPLOT_PLT = """set logscale x
set grid
set title "Summary of LAS Files with LASToHTML.py."
set xlabel "LAS File Size (bytes)"
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
set output "{name}_rate.svg" # choose the output device

# set key off

#set key title "Window Length"
#  lw 2 pointsize 2

# Fields: size_input, size_index, time, exception, ignored, path

#plot "{name}.dat" using 1:($3*1000/($1/(1024*1024))) axes x1y1 title "Scan Rate (ms/Mb), left axis" lt 1 w points, \\
    rate(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", a, b) lt 1 lw 2, \\
    "{name}.dat" using 1:3 axes x1y2 title "Scan Time (s), right axis" lt 4 w points, \\
    "{name}.dat" using 1:($1/$2) axes x1y2 title "Original Size / Scan size, right axis" lt 3 w points, \\
    compression_ratio(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", e, f) axes x1y2 lt 3 lw 2

plot "ScanFileHTML.dat" using 1:($3*1000/($1/(1024*1024))) axes x1y1 title "Scan LAS Create HTML Rate (ms/Mb), left axis" lt 1 w points

set output "ScanFileHTML_times.svg" # choose the output device
set ylabel "Index Time (s)"
unset y2label

plot "ScanFileHTML.dat" using 1:3 axes x1y1 title "Create Time (s), left axis" lt 1 w points, \\
    "ScanFileHTML.dat" using 1:2 axes x1y2 title "Output size (s), right axis" lt 2 w points

reset
"""


def plot_gnuplot(data: typing.Dict[str, LASFileResult], gnuplot_dir: str) -> None:
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
                    data[k].process_time,
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


def main():
    description = """usage: %prog [options] in out
Generates HTML from input LAS file or directory to an output destination."""
    print ('Cmd: %s' % ' '.join(sys.argv))
    parser = cmn_cmd_opts.path_in_out_required(
        description, prog='TotalDepth.LAS.LASToHTML.main', version=__version__, epilog=__rights__
    )
    cmn_cmd_opts.add_log_level(parser, level=20)
    cmn_cmd_opts.add_multiprocessing(parser)
    Slice.add_frame_slice_to_argument_parser(parser, use_what=True)
    process.add_process_logger_to_argument_parser(parser)
    gnuplot.add_gnuplot_to_argument_parser(parser)
    parser.add_argument("-g", "--glob", action="store_true", dest="glob", default=None,
                        help="File match pattern. Default: %(default)s.")
    parser.add_argument("-p", "--pause", action="store_true", dest="pause", default=False,
                      help="Pause before processing showing the PID. Default: %(default)s.")
    args = parser.parse_args()
    # print(args)
    if args.pause:
        input(f'Ready to start PID={os.getpid()} press any key: ')

    log_level = cmn_cmd_opts.set_log_level(args)

    clk_start = time.perf_counter()
    # Your code here
    if cmn_cmd_opts.multiprocessing_requested(args) and os.path.isdir(args.path_in):
        if args.log_process > 0.0:
            with process.log_process(args.log_process, log_level):
                result: typing.Dict[str, LASFileResult] = scan_dir_multiprocessing(
                    args.path_in,
                    args.path_out,
                    args.recurse,
                    args.keepGoing,
                    frame_slice=Slice.create_slice_or_sample(args.frame_slice),
                    label_process=True,
                    jobs=cmn_cmd_opts.number_multiprocessing_jobs(args),
                )
        else:
            result: typing.Dict[str, LASFileResult] = scan_dir_multiprocessing(
                args.path_in,
                args.path_out,
                args.recurse,
                args.keepGoing,
                frame_slice=Slice.create_slice_or_sample(args.frame_slice),
                label_process=False,
                jobs=cmn_cmd_opts.number_multiprocessing_jobs(args),
            )
    else:
        # with cPyMemTrace.Profile():
        #     if args.log_process > 0.0:
        #         with process.log_process(args.log_process, log_level):
        #             result: typing.Dict[str, LASFileResult] = scan_dir_or_file(
        #                 args.path_in,
        #                 args.path_out,
        #                 args.recurse,
        #                 args.keepGoing,
        #                 label_process=True,
        #                 frame_slice=Slice.create_slice_or_sample(args.frame_slice),
        #             )
        #     else:
        #             result: typing.Dict[str, LASFileResult] = scan_dir_or_file(
        #                 args.path_in,
        #                 args.path_out,
        #                 args.recurse,
        #                 args.keepGoing,
        #                 label_process=False,
        #                 frame_slice=Slice.create_slice_or_sample(args.frame_slice),
        #             )
        if args.log_process > 0.0:
            with process.log_process(args.log_process, log_level):
                result: typing.Dict[str, LASFileResult] = scan_dir_or_file(
                    args.path_in,
                    args.path_out,
                    args.recurse,
                    args.keepGoing,
                    label_process=True,
                    frame_slice=Slice.create_slice_or_sample(args.frame_slice),
                )
        else:
            result: typing.Dict[str, LASFileResult] = scan_dir_or_file(
                args.path_in,
                args.path_out,
                args.recurse,
                args.keepGoing,
                label_process=False,
                frame_slice=Slice.create_slice_or_sample(args.frame_slice),
            )
    if args.log_process > 0.0:
        process.add_message_to_queue('Processing HTML Complete.')
    clk_exec = time.perf_counter() - clk_start
    # print('Execution time = %8.3f (S)' % clk_exec)
    size_scan = size_input = 0
    files_processed = 0
    common_path = os.path.commonpath(result.keys())
    print(f'Common path: {common_path}')
    header = (
        f'{"Size In":>16}',
        f'{"Size Out":>10}',
        f'{"Time":>8}',
        f'{"Ratio %":>8}',
        f'{"ms/Mb":>8}',
        f'{"Fail?":5}',
        f'Path',
    )
    print(' '.join(header))
    print(' '.join('-' * len(v) for v in header))
    for path in sorted(result.keys()):
        idx_result = result[path]
        if idx_result.size_input > 0:
            ms_mb = idx_result.process_time * 1000 / (idx_result.size_input / 1024 ** 2)
            ratio = idx_result.size_output / idx_result.size_input
            print(
                f'{idx_result.size_input:16,d} {idx_result.size_output:10,d}'
                f' {idx_result.process_time:8.3f} {ratio:8.3%} {ms_mb:8.1f} {str(idx_result.exception):5}'
                f' "{path[len(common_path) + 1:]}"'
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
