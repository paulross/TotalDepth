import logging
import multiprocessing
import os
import sys
import time

import typing

from TotalDepth.LAS.core import LASRead, WriteLAS
from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import stringify
from TotalDepth.common import cmn_cmd_opts, process, ToHTML, Slice, AbsentValue, np_summary
from TotalDepth.util import gnuplot, XmlWrite, bin_file_type

__author__  = 'Paul Ross'
__date__    = '2020-09-05'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2020 Paul Ross'


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
th.eflr, td.eflr {
    border: 1px solid black;
    /* border-top-style:solid; */
    /* border-right-style:dotted; */
    /* border-bottom-style:none; */
    /* border-left-style:none; */
    vertical-align:top;
    padding: 2px 6px 2px 6px; 
}

table.sul {
    border:            2px solid black;
    border-collapse:   collapse;
    /* font-family:       monospace; */
    color:             black;
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
                    # print(f'TRACE: {row.unit} {type(row.unit)}')
                    xhtml_stream.characters(str(row.unit))
                with XmlWrite.Element(xhtml_stream, 'td', {'class': 'las'}):
                    xhtml_stream.characters(str(row.valu))
                with XmlWrite.Element(xhtml_stream, 'td', {'class': 'las'}):
                    xhtml_stream.characters(row.desc)


def las_section_to_html(las_section: LASRead.LASSection, xhtml_stream:XmlWrite.XhtmlStream) -> None:
    if len(las_section):
        with XmlWrite.Element(xhtml_stream, 'h2', {'class': 'las_h2'}):
            with XmlWrite.Element(xhtml_stream, 'p', {'class': 'las_p'}):
                xhtml_stream.characters(
                    f'LAS Section "{las_section.type}" - {LASRead.SECT_DESCRIPTION_MAP[las_section.type]}'
                )
        las_section_members_to_html_table(las_section.members, xhtml_stream)


def las_file_to_html(las_file_path: str, html_file_path: str, *args) -> None:
    las_file = LASRead.LASRead(las_file_path, las_file_path)
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
                for las_section in las_file.generate_sections():
                    if las_section.type != 'A':
                        las_section_to_html(las_section, xhtml_stream)
                # Now array section
                if las_file.frame_array is not None:
                    with XmlWrite.Element(xhtml_stream, 'h2', {'class': 'las_h2'}):
                        with XmlWrite.Element(xhtml_stream, 'p', {'class': 'las_p'}):
                            xhtml_stream.characters(
                                f'LAS Section "A" - Array Section'
                            )
                    frame_table = [
                        ['Channel',
                         'Dims', 'Count', 'Units', 'Long Name',
                         'Size', 'Absent', 'Min', 'Mean', 'Median', 'Std.Dev.', 'Max', '--', '==', '++', 'Activity',
                         'dtype'],
                    ]
                    for channel in las_file.frame_array.channels:
                        arr = AbsentValue.mask_absent_values(channel.array)
                        array_summary = np_summary.summarise_array(arr)
                        frame_table.append(
                            [
                                channel.ident,
                                stringify.stringify_object_by_type(channel.dimensions),
                                stringify.stringify_object_by_type(channel.count),
                                stringify.stringify_object_by_type(channel.units),
                                stringify.stringify_object_by_type(channel.long_name),
                                f'{arr.size:d}',
                                # NOTE: Not the masked array!
                                f'{AbsentValue.count_of_absent_values(channel.array):d}',
                                f'{array_summary.min:.3f}',
                                f'{array_summary.mean:.3f}',
                                f'{array_summary.median:.3f}',
                                f'{array_summary.std:.3f}',
                                f'{array_summary.max:.3f}',
                                f'{array_summary.count_dec:d}',
                                f'{array_summary.count_eq:d}',
                                f'{array_summary.count_inc:d}',
                                f'{array_summary.activity:.3f}',
                                f'{arr.dtype}',
                            ]
                        )
                    ToHTML.html_write_table(frame_table, xhtml_stream, class_style='monospace')


def scan_a_single_file(path_in: str, path_out: str, label_process: bool,
                       frame_slice: typing.Union[Slice.Slice, Slice.Sample]) -> ToHTML.HTMLResult:
    """Scan a single file and write out an HTML summary."""
    file_path_out = path_out + '.html'
    logger.debug(f'Scanning "{path_in}" to "{file_path_out}"')
    binary_file_type = bin_file_type.binary_file_type_from_path(path_in)
    if binary_file_type in bin_file_type.LAS_BINARY_FILE_TYPES:
        logging.info(f'scan_a_single_file(): "{path_in}" to "{file_path_out}"')
        t_start = time.perf_counter()
        try:
            if path_out:
                out_dir = os.path.dirname(path_out)
                if not os.path.exists(out_dir):
                    logger.debug(f'Making directory: {out_dir}')
                    os.makedirs(out_dir, exist_ok=True)
                html_summary = las_file_to_html(path_in, file_path_out, label_process, frame_slice)
                len_scan_output = os.path.getsize(file_path_out)
            else:
                html_summary = las_file_to_html(path_in, sys.stdout, label_process, frame_slice)
                len_scan_output = -1
            result = ToHTML.HTMLResult(
                path_in,
                file_path_out,
                os.path.getsize(path_in),
                len_scan_output,
                binary_file_type,
                time.perf_counter() - t_start,
                False,
                False,
                html_summary,
            )
        except ExceptionTotalDepthRP66V1:
            logger.exception(f'Failed to index with ExceptionTotalDepthRP66V1: {path_in}')
            result = ToHTML.HTMLResult(path_in, file_path_out, os.path.getsize(path_in), 0, binary_file_type, 0.0, True, False,
                                None)
        except Exception:
            logger.exception(f'Failed to index with Exception: {path_in}')
            result = ToHTML.HTMLResult(path_in, file_path_out, os.path.getsize(path_in), 0, binary_file_type, 0.0, True, False,
                                None)
    else:
        logger.debug(f'Ignoring file type "{binary_file_type}" at {path_in}')
        result = ToHTML.HTMLResult(path_in, file_path_out, 0, 0, binary_file_type, 0.0, False, True, None)
    return result


def scan_dir_multiprocessing(dir_in, dir_out, jobs,
                             frame_slice: typing.Union[Slice.Slice, Slice.Sample]) \
        -> typing.Dict[str, ToHTML.HTMLResult]:
    """Multiprocessing code to plot log passes.
    Returns a dict of {path_in : HTMLResult, ...}"""
    assert os.path.isdir(dir_in)
    if jobs < 1:
        jobs = multiprocessing.cpu_count()
    logging.info('scan_dir_multiprocessing(): Setting multi-processing jobs to %d' % jobs)
    pool = multiprocessing.Pool(processes=jobs)
    tasks = [
        (t.filePathIn, t.filePathOut, False, frame_slice) for t in DirWalk.dirWalk(
            dir_in, dir_out, theFnMatch='', recursive=True, bigFirst=True
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
    _write_indexes(dir_out, {r.path_output: r for r in results})
    return {r.path_input: r for r in results}


def scan_dir_or_file(path_in: str, path_out: str,
                     recursive: bool, label_process: bool,
                     frame_slice: typing.Union[Slice.Slice, Slice.Sample]) -> typing.Dict[str, ToHTML.HTMLResult]:
    """Scans a directory or file putting the results in path_out.
    Returns a dict of {path_in : HTMLResult, ...}
    """
    # Required as we are going to split them by os.sep
    # NOTE: normpath removes trailing os.sep which is what we want.
    path_in = os.path.normpath(path_in)
    path_out = os.path.normpath(path_out)
    logging.info(f'scan_dir_or_file(): "{path_in}" to "{path_out}" recurse: {recursive}')
    ret: typing.Dict[str, HTMLResult] = {}
    # Output file path to FileResult
    if os.path.isdir(path_in):
        index_map_global: typing.Dict[str, HTMLResult] = {}
        if not recursive:
            for file_in_out in DirWalk.dirWalk(path_in, path_out, theFnMatch='', recursive=recursive, bigFirst=False):
                result = scan_a_single_file(
                    file_in_out.filePathIn, file_in_out.filePathOut, label_process, frame_slice
                )
                ret[file_in_out.filePathIn] = result
                if not result.exception and not result.ignored:
                    index_map_global[result.path_output] = result
            if label_process:
                process.add_message_to_queue('Writing Indexes.')
            _write_indexes(path_out, index_map_global)
        else:
            len_path_in = len(path_in.split(os.sep))
            for root, dirs, files in os.walk(path_in, topdown=False):
                root_rel_to_path_in = root.split(os.sep)[len_path_in:]
                dir_out = os.path.join(path_out, *root_rel_to_path_in)
                for file in files:
                    file_path_in = os.path.join(root, file)
                    # Respect sub-directories in root
                    # root_rel_to_path_in.append(file)
                    file_path_out = os.path.join(dir_out, file)
                    result = scan_a_single_file(file_path_in, file_path_out, label_process, frame_slice)
                    ret[file_path_in] = result
                    if not result.exception and not result.ignored:
                        index_map_global[result.path_output] = result
            if label_process:
                process.add_message_to_queue('Writing Indexes.')
            _write_indexes(path_out, index_map_global)
    else:
        ret[path_in] = scan_a_single_file(path_in, path_out, label_process, frame_slice)
    return ret


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
    args = parser.parse_args()
    # print(args)
    cmn_cmd_opts.set_log_level(args)

    clk_start = time.perf_counter()
    # Your code here
    if args.log_process > 0.0:
        with process.log_process(args.log_process):
            result: typing.Dict[str, ToHTML.HTMLResult] = scan_dir_or_file(
                args.path_in,
                args.path_out,
                args.recurse,
                label_process=True,
                frame_slice=Slice.create_slice_or_sample(args.frame_slice),
            )
    else:
        if cmn_cmd_opts.multiprocessing_requested(args) and os.path.isdir(args.path_in):
            result: typing.Dict[str, ToHTML.HTMLResult] = scan_dir_multiprocessing(
                args.path_in,
                args.path_out,
                args.jobs,
                frame_slice=Slice.create_slice_or_sample(args.frame_slice),
            )
        else:
            result: typing.Dict[str, ToHTML.HTMLResult] = scan_dir_or_file(
                args.path_in,
                args.path_out,
                args.recurse,
                label_process=False,
                frame_slice=Slice.create_slice_or_sample(args.frame_slice),
            )
    if args.log_process > 0.0:
        process.add_message_to_queue('Processing HTML Complete.')
    clk_exec = time.perf_counter() - clk_start
    # print('Execution time = %8.3f (S)' % clk_exec)
    size_scan = size_input = 0
    files_processed = 0
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
