"""Example of reading the index XML files and mining them for data."""
import collections
import logging
import os
import sys
import time
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.common import xml, cmn_cmd_opts
from TotalDepth.util.DirWalk import dirWalk

__author__  = 'Paul Ross'
__date__    = '2019-04-10'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


logger = logging.getLogger(__file__)


IndexResult = collections.namedtuple('IndexResult', 'size_input, size_index, time, exception, ignored, analysis')


def _get_values(attribute: xml.etree.Element) -> typing.List[str]:
    ret = []
    for child in attribute:
        if child.tag == 'Value':
            ret.append(child.get('value'))
    return ret


def _eflr_object_long_name(eflr: xml.etree.Element) -> typing.Dict[str, str]:
    assert eflr.tag == 'EFLR'
    ret = {}
    for object_elem in eflr:
        for attribute_elem in object_elem:
            if attribute_elem.get('label') == 'LONG-NAME':
                ret[object_elem.get('I')] = '\n'.join(_get_values(attribute_elem))
    return ret


def _analyse_logical_file(logical_file_elem: xml.etree.Element,
                          eflr_set_types: typing.List[str]) -> typing.Dict[str, typing.Set[str]]:
    result = {}
    for child in logical_file_elem:
        # print(child, eflr_set_types)
        if child.tag == 'EFLR' and child.get('set_type') in eflr_set_types:
            # print('TRACE:', child)
            print(_eflr_object_long_name(child))

            objects = set()
            for object_elem in child:
                objects.add(object_elem.get('I'))
            if child.get('set_type') not in result:
                result[child.get('set_type')] = objects
            else:
                result[child.get('set_type')] |= objects
    return result


def _analyse_logical_files(logical_files_elem: xml.etree.Element,
                           eflr_set_types: typing.List[str]) -> typing.List[typing.Dict[str, typing.Set[str]]]:
    result = []
    for logical_file_elem in logical_files_elem:
        result.append(_analyse_logical_file(logical_file_elem, eflr_set_types))
    # print('TRACE:', result)
    return result


def read_a_single_index(xml_path_in: str,
                        eflr_set_type: typing.List[str]) -> IndexResult:
    """
    Reads a single XML index and analyses it.
    """
    logger.info(f'Reading XML index: {xml_path_in}')
    try:
        xml_size = os.path.getsize(xml_path_in)
        t_start = time.perf_counter()
        tree = xml.etree.parse(xml_path_in)
        root = tree.getroot()
        result = None
        assert root.tag == 'RP66V1FileIndex'
        for child in root:
            if child.tag == 'LogicalFiles':
                result = _analyse_logical_files(child, eflr_set_type)
                break
        result = IndexResult(
            int(root.get('size')),
            xml_size,
            time.perf_counter() - t_start,
            False,
            False,
            result,
        )
        return result
    except ExceptionTotalDepthRP66V1:
        logger.exception(f'Failed to index with ExceptionTotalDepthRP66V1: {xml_path_in}')
        return IndexResult(0, xml_size, 0.0, True, False, None)
    except Exception:
        logger.exception(f'Failed to index with Exception: {xml_path_in}')
        return IndexResult(0, xml_size, 0.0, True, False, None)


def read_index_dir_or_file(path_in: str, recurse: bool,
                           eflr_set_type: typing.List[str]) -> typing.Dict[str, IndexResult]:
    logging.info(f'index_dir_or_file(): "{path_in}" recurse: {recurse}')
    ret = {}
    if os.path.isdir(path_in):
        for file_in_out in dirWalk(path_in, theFnMatch='', recursive=recurse, bigFirst=False):
            # print(file_in_out)
            ret[file_in_out.filePathIn] = read_a_single_index(file_in_out.filePathIn, eflr_set_type)
    else:
        ret[path_in] = read_a_single_index(path_in, eflr_set_type)
    return ret


def analyse_result(result: typing.Dict[str, IndexResult]) -> None:
    object_count = {}
    logical_file_count = 0
    for physical_file in result:
        if result[physical_file].analysis is not None:
            logical_file_count += len(result[physical_file].analysis)
    for physical_file in result:
        if result[physical_file].analysis is not None:
            for logical_file_result in result[physical_file].analysis:
                # print('TRACE:', logical_file_result.keys())
                if 'PARAMETER' in logical_file_result:
                    for object_name in logical_file_result['PARAMETER']:
                        if object_name not in object_count:
                            object_count[object_name] = 1
                        else:
                            object_count[object_name] += 1
    print(f'Logical files: {logical_file_count}')
    cutoff = 0.75
    print(f'Objects in {cutoff:.0%} of logical files:')
    for object_name in sorted(object_count.keys()):
        if object_count[object_name] > cutoff * logical_file_count:
            print(
                f'{object_name:24}'
                f' : {object_count[object_name]:8d}'
                f'  {object_count[object_name] / logical_file_count:8.1%}'
            )


def main() -> int:
    description = """usage: %(prog)s [options] file
Reads a RP66V1 index XML file and all the data."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = cmn_cmd_opts.path_in(desc=description, epilog=__rights__, prog=sys.argv[0])
    # parser.add_argument(
    #     'archive', type=str,
    #     help='Path to the root directory of the archive.',
    #     default='',
    #     # nargs='?',
    # )
    # Add arguments that control what we read and report on
    parser.add_argument(
        "--eflr-set-type", action='append', default=[],
        help="List of IFLR Set Types to output, additive, if absent then dump all. [default: %(default)s]",
    )
    cmn_cmd_opts.add_log_level(parser, 20)
    args = parser.parse_args()
    # print('args:', args)
    # return 0

    # Set log level
    cmn_cmd_opts.set_log_level(args)
    # Your code here
    clk_start = time.perf_counter()
    result: typing.Dict[str, IndexResult] = read_index_dir_or_file(
        args.path_in,
        args.recurse,
        args.eflr_set_type,
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
    except Exception as err:
        logger.exception(str(err))
    analyse_result(result)
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
