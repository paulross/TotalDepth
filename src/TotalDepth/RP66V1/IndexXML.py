import datetime
import io
import logging
import multiprocessing
import os
import sys
import time
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import LogPass
from TotalDepth.RP66V1.core import LogicalFile
from TotalDepth.RP66V1.core import LogicalRecord
from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core.Index import ExceptionIndex
from TotalDepth.RP66V1.core.XAxis import IFLRReference
from TotalDepth.common import process
from TotalDepth.common import cmn_cmd_opts
from TotalDepth.common import Rle
from TotalDepth.util import DirWalk
from TotalDepth.util.bin_file_type import binary_file_type_from_path
from TotalDepth.util import gnuplot
from TotalDepth.util import XmlWrite

__author__  = 'Paul Ross'
__date__    = '2019-04-10'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


class ExceptionRP66V1IndexXMLRead(ExceptionIndex):
    pass

class ExceptionIndexXML(ExceptionTotalDepthRP66V1):
    pass


class ExceptionIndexXMLRead(ExceptionIndexXML):
    pass


class ExceptionLogPassXML(LogPass.ExceptionLogPass):
    pass


logger = logging.getLogger(__file__)

XML_SCHEMA_VERSION = '0.1.0'
XML_TIMESTAMP_FORMAT_NO_TZ = '%Y-%m-%d %H:%M:%S.%f'

# UTC with a TZ
# datetime.datetime.utcnow().replace(tzinfo=datetime.timezone(datetime.timedelta(0))).strftime('%Y-%m-%d %H:%M:%S.%f%z')
# '2019-05-14 17:33:01.147341+0000'


def xml_rle_write(rle: Rle.RLE, element_name: str, xml_stream: XmlWrite.XmlStream, hex_output: bool) -> None:
    with XmlWrite.Element(xml_stream, element_name, {'count': f'{rle.num_values():d}', 'rle_len': f'{len(rle):d}',}):
        for rle_item in rle.rle_items:
            attrs = {
                'datum': f'0x{rle_item.datum:x}' if hex_output else f'{rle_item.datum}',
                'stride': f'0x{rle_item.stride:x}' if hex_output else f'{rle_item.stride}',
                'repeat': f'{rle_item.repeat:d}',
            }
            with XmlWrite.Element(xml_stream, 'RLE', attrs):
                pass


def xml_object_name_attributes(object_name: RepCode.ObjectName) -> typing.Dict[str, str]:
    return {
        'O': f'{object_name.O}',
        'C': f'{object_name.C}',
        'I': f'{object_name.I.decode("ascii")}',
    }


def xml_write_value(xml_stream: XmlWrite.XmlStream, value: typing.Any) -> None:
    """Write a value to the XML stream with specific type as an attribute.
    This writes either a <Value> or an <ObjectName> element."""
    if isinstance(value, RepCode.ObjectName):
        with XmlWrite.Element(xml_stream, 'ObjectName', xml_object_name_attributes(value)):
            pass
    else:
        if isinstance(value, bytes):
            typ = 'bytes'
            # print('TRACE: xml_write_value()', value)
            _value = value.decode('latin-1')#, errors='ignore')
        elif isinstance(value, float):
            typ = 'float'
            _value = str(value)
        elif isinstance(value, int):
            typ = 'int'
            _value = str(value)
        elif isinstance(value, RepCode.DateTime):
            typ = 'TotalDepth.RP66V1.core.RepCode.DateTime'
            _value = str(value)
        elif isinstance(value, str):  # pragma: no cover
            typ = 'str'
            _value = value
        else:
            typ = 'unknown'
            _value = str(value)
        with XmlWrite.Element(xml_stream, 'Value', {'type': typ, 'value': _value}):
            pass


def frame_channel_to_XML(channel: LogPass.FrameChannel, xml_stream: XmlWrite.XmlStream) -> None:
    """Writes a XML Channel node suitable for RP66V1.

    Example:

    .. code-block:: xml

        <Channel C="0" I="DEPTH" O="35" count="1" dimensions="1" long_name="Depth Channel" rep_code="7" units="m"/>
    """
    channel_attrs = {
        'O': f'{channel.ident.O}',
        'C': f'{channel.ident.C}',
        'I': f'{channel.ident.I.decode("ascii")}',
        'long_name': f'{channel.long_name.decode("ascii")}',
        'rep_code': f'{channel.rep_code:d}',
        'units': f'{channel.units.decode("ascii")}',
        'dimensions': ','.join(f'{v:d}' for v in channel.dimensions),
        'count': f'{channel.count:d}',
    }
    with XmlWrite.Element(xml_stream, 'Channel', channel_attrs):
        pass



def frame_array_to_XML(frame_array: LogPass.FrameArray,
                       iflr_data: typing.Sequence[IFLRReference],
                       xml_stream: XmlWrite.XmlStream) -> None:
    """Writes a XML FrameArray node suitable for RP66V1.

    Example:

    .. code-block:: xml

        <FrameArray C="0" I="0B" O="11" description="">
          <Channels channel_count="9">
            <Channel C="0" I="DEPT" O="11" count="1" dimensions="1" long_name="MWD Tool Measurement Depth" rep_code="2" units="0.1 in"/>
            <Channel C="0" I="INC" O="11" count="1" dimensions="1" long_name="Inclination" rep_code="2" units="deg"/>
            <Channel C="0" I="AZI" O="11" count="1" dimensions="1" long_name="Azimuth" rep_code="2" units="deg"/>
            ...
          </Channels>
          <IFLR count="83">
              <FrameNumbers count="83" rle_len="1">
                <RLE datum="1" repeat="82" stride="1"/>
              </FrameNumbers>
              <LRSH count="83" rle_len="2">
                <RLE datum="0x14ac" repeat="61" stride="0x30"/>
                <RLE datum="0x2050" repeat="20" stride="0x30"/>
              </LRSH>
              <Xaxis count="83" rle_len="42">
                <RLE datum="0.0" repeat="1" stride="75197.0"/>
                <RLE datum="154724.0" repeat="1" stride="79882.0"/>
              </Xaxis>
          </IFLR>
        </FrameArray>
    """
    frame_array_attrs = {
        'O': f'{frame_array.ident.O}',
        'C': f'{frame_array.ident.C}',
        'I': f'{frame_array.ident.I.decode("ascii")}',
        'description': frame_array.description.decode('ascii'),
        'x_axis' : frame_array.channels[0].ident.I.decode("ascii"),
        'x_units' : frame_array.channels[0].units.decode("ascii"),
    }

    with XmlWrite.Element(xml_stream, 'FrameArray', frame_array_attrs):
        with XmlWrite.Element(xml_stream, 'Channels', {'count': f'{len(frame_array)}'}):
            for channel in frame_array.channels:
                    frame_channel_to_XML(channel, xml_stream)
        with XmlWrite.Element(xml_stream, 'IFLR', {'count' : f'{len(iflr_data)}'}):
            # Frame number output
            rle = Rle.create_rle(v.frame_number for v in iflr_data)
            xml_rle_write(rle, 'FrameNumbers', xml_stream, hex_output=False)
            # IFLR file position
            rle = Rle.create_rle(v.logical_record_position.lrsh_position for v in iflr_data)
            xml_rle_write(rle, 'LRSH', xml_stream, hex_output=True)
            # Xaxis output
            rle = Rle.create_rle(v.x_axis for v in iflr_data)
            xml_rle_write(rle, 'Xaxis', xml_stream, hex_output=False)


def log_pass_to_XML(log_pass: LogPass.LogPass,
                    iflr_data_map: typing.Dict[typing.Hashable, typing.Sequence[IFLRReference]],
                    xml_stream: XmlWrite.XmlStream) -> None:
    """Writes a XML LogPass node suitable for RP66V1. Example:

    .. code-block:: xml

        <LogPass count="4">
            <FrameArray C="0" I="600T" O="44" description="">
                ...
            <FrameArray>
            ...
        </LogPass>
    """
    with XmlWrite.Element(xml_stream, 'LogPass', {'count': f'{len(log_pass)}'}):
        for frame_array in log_pass.frame_arrays:
            if frame_array.ident not in iflr_data_map:  # pragma: no cover
                raise ExceptionLogPassXML(f'Missing ident {frame_array.ident} in keys {list(iflr_data_map.keys())}')
            frame_array_to_XML(frame_array, iflr_data_map[frame_array.ident], xml_stream)


def _write_xml_eflr_object(obj: LogicalRecord.EFLR.Object, xml_stream: XmlWrite.XmlStream) -> None:
    with XmlWrite.Element(xml_stream, 'Object', xml_object_name_attributes(obj.name)):
        for attr in obj.attrs:
            attr_atributes = {
                'label': attr.label.decode('ascii'),
                'count': f'{attr.count:d}',
                'rc': f'{attr.rep_code:d}',
                # TODO: Remove this as duplicate?
                'rc_ascii': f'{RepCode.REP_CODE_INT_TO_STR[attr.rep_code]}',
                'units': attr.units.decode('ascii'),
            }
            with XmlWrite.Element(xml_stream, 'Attribute', attr_atributes):
                if attr.value is not None:
                    for v in attr.value:
                        xml_write_value(xml_stream, v)


def write_logical_file_to_xml(logical_file_index: int, logical_file: LogicalFile, xml_stream: XmlWrite.XmlStream, private: bool) -> None:
    with XmlWrite.Element(xml_stream, 'LogicalFile', {
        'has_log_pass': str(logical_file.has_log_pass),
        'index': f'{logical_file_index:d}',
        # 'schema_version': XML_SCHEMA_VERSION,
    }):
        for position, eflr in logical_file.eflrs:
            attrs = {
                'vr_position': f'0x{position.vr_position:x}',
                'lrsh_position': f'0x{position.lrsh_position:x}',
                'lr_type': f'{eflr.lr_type:d}',
                'set_type': f'{eflr.set.type.decode("ascii")}',
                'set_name': f'{eflr.set.name.decode("ascii")}',
                'object_count': f'{len(eflr.objects):d}'
            }
            with XmlWrite.Element(xml_stream, 'EFLR', attrs):
                if private or LogicalRecord.Types.is_public(eflr.lr_type):
                    for obj in eflr.objects:
                        _write_xml_eflr_object(obj, xml_stream)
        if logical_file.has_log_pass:
            log_pass_to_XML(logical_file.log_pass, logical_file.iflr_position_map, xml_stream)


def write_logical_file_sequence_to_xml(logical_index: LogicalFile.LogicalIndex,
                                       output_stream: typing.TextIO, private: bool) -> None:
    """Takes a LogicalIndex and writes the index to an XML stream."""
    with XmlWrite.XmlStream(output_stream) as xml_stream:
        with XmlWrite.Element(xml_stream, 'RP66V1FileIndex', {
            'path': logical_index.id,
            'size': f'{os.path.getsize(logical_index.id):d}',
            'schema_version': XML_SCHEMA_VERSION,
            'utc_file_mtime': str(datetime.datetime.utcfromtimestamp(os.stat(logical_index.id).st_mtime)),
            'utc_now': str(datetime.datetime.utcnow()),
            'creator': f'{__name__}',
        }):
            with XmlWrite.Element(
                    xml_stream, 'StorageUnitLabel',
                    {
                        'sequence_number': str(logical_index.storage_unit_label.storage_unit_sequence_number),
                        'dlis_version': logical_index.storage_unit_label.dlis_version.decode('ascii'),
                        'storage_unit_structure': logical_index.storage_unit_label.storage_unit_structure.decode('ascii'),
                        'maximum_record_length': str(logical_index.storage_unit_label.maximum_record_length),
                        'storage_set_identifier': logical_index.storage_unit_label.storage_set_identifier.decode('ascii'),
                    }):
                pass
            with XmlWrite.Element(xml_stream, 'LogicalFiles', {'count': f'{len(logical_index.logical_files):d}'}):
                for lf, logical_file in enumerate(logical_index.logical_files):
                    write_logical_file_to_xml(lf, logical_file, xml_stream, private)
            # Visible records at the end
            rle_visible_records = Rle.create_rle(logical_index.visible_record_positions)
            xml_rle_write(rle_visible_records, 'VisibleRecords', xml_stream, hex_output=True)


class IndexResult(typing.NamedTuple):
    path_input: str
    size_input: int
    size_index: int
    time: float
    exception: bool
    ignored: bool


def index_a_single_file(path_in: str, path_out: str, private: bool) -> IndexResult:
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
            t_start = time.perf_counter()
            with LogicalFile.LogicalIndex(path_in) as logical_index:
                if path_out:
                    with open(path_out + '.xml', 'w') as f_out:
                        write_logical_file_sequence_to_xml(logical_index, f_out, private)
                    index_size = os.path.getsize(path_out + '.xml')
                else:
                    xml_fobj = io.StringIO()
                    write_logical_file_sequence_to_xml(logical_index, xml_fobj, private)
                    index_output = xml_fobj.getvalue()
                    index_size = len(index_output)
                    print(index_output)
                result = IndexResult(
                    path_in,
                    os.path.getsize(path_in),
                    index_size,
                    time.perf_counter() - t_start,
                    False,
                    False,
                )
                logger.info(f'Length of XML: {index_size}')
                return result
        except ExceptionTotalDepthRP66V1:  # pragma: no cover
            logger.exception(f'Failed to index with ExceptionTotalDepthRP66V1: {path_in}')
            return IndexResult(path_in, os.path.getsize(path_in), 0, 0.0, True, False)
        except Exception:  # pragma: no cover
            logger.exception(f'Failed to index with Exception: {path_in}')
            return IndexResult(path_in, os.path.getsize(path_in), 0, 0.0, True, False)
    logger.info(f'Ignoring file type "{bin_file_type}" at {path_in}')
    return IndexResult(path_in, 0, 0, 0.0, False, True)


def index_dir_multiprocessing(dir_in: str, dir_out: str, private: bool, jobs: int) -> typing.Dict[str, IndexResult]:
    """Multiprocessing code to index in XML.
    Returns a dict of {path_in : IndexResult, ...}"""
    if jobs < 1:
        jobs = multiprocessing.cpu_count()
    logging.info('scan_dir_multiprocessing(): Setting multi-processing jobs to %d' % jobs)
    pool = multiprocessing.Pool(processes=jobs)
    tasks = [
        (t.filePathIn, t.filePathOut, private) for t in DirWalk.dirWalk(
            dir_in, dir_out, theFnMatch='', recursive=True, bigFirst=True
        )
    ]
    # print('tasks:')
    # pprint.pprint(tasks, width=200)
    # return {}
    results = [
        r.get() for r in [
            pool.apply_async(index_a_single_file, t) for t in tasks
        ]
    ]
    return {r.path_input : r for r in results}


def index_dir_or_file(path_in: str, path_out: str, recurse: bool, private: bool) -> typing.Dict[str, IndexResult]:
    logging.info(f'index_dir_or_file(): "{path_in}" to "{path_out}" recurse: {recurse}')
    ret = {}
    if os.path.isdir(path_in):
        for file_in_out in DirWalk.dirWalk(path_in, path_out, theFnMatch='', recursive=recurse, bigFirst=False):
            # print(file_in_out)
            ret[file_in_out.filePathIn] = index_a_single_file(file_in_out.filePathIn, file_in_out.filePathOut, private)
    else:
        ret[path_in] = index_a_single_file(path_in, path_out, private)
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
#rate(x) = 10**(a + b * log10(x))
#fit rate(x) "{name}.dat" using 1:($3*1000/($1/(1024*1024))) via a, b

#rate2(x) = 10**(5.5 - 0.5 * log10(x))

# Curve fit, size ratio
#size_ratio(x) = 10**(c + d * log10(x))
#fit size_ratio(x) "{name}.dat" using 1:($2/$1) via c,d
# By hand
# size_ratio2(x) = 10**(3.5 - 0.65 * log10(x))

# Curve fit, compression ratio
#compression_ratio(x) = 10**(e + f * log10(x))
#fit compression_ratio(x) "{name}.dat" using 1:($2/$1) via e,f

set terminal svg size 1000,700 # choose the file format
set output "{name}.svg" # choose the output device

# set key off

#set key title "Window Length"
#  lw 2 pointsize 2

# Fields: size_input, size_index, time, exception, ignored, path

# plot "{name}.dat" using 1:($3*1000/($1/(1024*1024))) axes x1y1 title "XML Index Rate (ms/Mb)" lt 1 w points,\
    rate(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", a, b) lt 1 lw 2, \
    "{name}.dat" using 1:($2/$1) axes x1y2 title "XML Index size / Original Size" lt 2 w points, \
    compression_ratio(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", e, f) axes x1y2 lt 2 lw 2

plot "{name}.dat" using 1:($3*1000/($1/(1024*1024))) axes x1y1 title "XML Index Rate (ms/Mb)" lt 1 w points,\
    "{name}.dat" using 1:($2/$1) axes x1y2 title "XML Index size / Original Size" lt 2 w points

# Plot size ratio:
#    "{name}.dat" using 1:($2/$1) axes x1y2 title "Index size ratio" lt 3 w points, \
#     size_ratio(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", c, d) axes x1y2 lt 3 lw 2

reset
"""


def plot_gnuplot(data: typing.Dict[str, IndexResult], gnuplot_dir: str) -> None:
    if len(data) < 2:  # pragma: no cover
        raise ValueError(f'Can not plot data with only {len(data)} points.')
    # First row is header row, create it then comment out the first item.
    table = [
        list(IndexResult._fields)[1:] + ['Path']
    ]
    table[0][0] = f'# {table[0][0]}'
    for k in sorted(data.keys()):
        if data[k].size_input > 0 and not data[k].exception:
            table.append(list(data[k][1:]) + [k])
    name = 'IndexFileXML'
    return_code = gnuplot.invoke_gnuplot(gnuplot_dir, name, table, GNUPLOT_PLT.format(name=name))
    if return_code:  # pragma: no cover
        raise IOError(f'Can not plot gnuplot with return code {return_code}')
    return_code = gnuplot.write_test_file(gnuplot_dir, 'svg')
    if return_code:  # pragma: no cover
        raise IOError(f'Can not plot gnuplot with return code {return_code}')


def main() -> int:
    description = """usage: %(prog)s [options] file
    Scans a RP66V1 file or directory and writes out the index(es) in XML."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = cmn_cmd_opts.path_in_out(
        description, prog='TotalDepth.RP66V1.IndexXML.main', version=__version__, epilog=__rights__
    )
    cmn_cmd_opts.add_log_level(parser, level=20)
    cmn_cmd_opts.add_multiprocessing(parser)
    parser.add_argument(
        '-e', '--encrypted', action='store_true',
        help='Output encrypted Logical Records as well. [default: %(default)s]',
    )
    process.add_process_logger_to_argument_parser(parser)
    gnuplot.add_gnuplot_to_argument_parser(parser)
    parser.add_argument(
        '-p', '--private', action='store_true',
        help='Also write out private EFLRs. [default: %(default)s]',
    )
    args = parser.parse_args()
    # print('args:', args)
    # return 0
    cmn_cmd_opts.set_log_level(args)
    # Your code here
    clk_start = time.perf_counter()
    ret_val = 0
    if os.path.isdir(args.path_in) and cmn_cmd_opts.multiprocessing_requested(args):
        result: typing.Dict[str, IndexResult] = index_dir_multiprocessing(
            args.path_in,
            args.path_out,
            args.private,
            args.jobs,
        )
    else:
        if args.log_process > 0.0:
            with process.log_process(args.log_process):
                result: typing.Dict[str, IndexResult] = index_dir_or_file(
                    args.path_in,
                    args.path_out,
                    args.recurse,
                    args.private,
                )
        else:
            result: typing.Dict[str, IndexResult] = index_dir_or_file(
                args.path_in,
                args.path_out,
                args.recurse,
                args.private,
            )
    clk_exec = time.perf_counter() - clk_start
    size_index = size_input = 0
    files_processed = 0
    try:
        header = (
            f'{"Size In":>16}',
            f'{"Size Out":>16}',
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
                ratio = idx_result.size_index / idx_result.size_input
                print(
                    f'{idx_result.size_input:16,d} {idx_result.size_index:16,d}'
                    f' {idx_result.time:8.3f} {ratio:8.3%} {ms_mb:8.1f} {str(idx_result.exception):5}'
                    f' "{path}"'
                )
                size_input += result[path].size_input
                size_index += result[path].size_index
                files_processed += 1
        if args.gnuplot:
            try:
                plot_gnuplot(result, args.gnuplot)
            except Exception:  # pragma: no cover
                logger.exception('gunplot failed')
                ret_val = 1
    except Exception as err:  # pragma: no cover
        logger.exception(str(err))
        ret_val = 2
    print('Execution time = %8.3f (S)' % clk_exec)
    if size_input > 0:
        ms_mb = clk_exec * 1000 / (size_input/ 1024**2)
        ratio = size_index / size_input
    else:  # pragma: no cover
        ms_mb = 0.0
        ratio = 0.0
    print(f'Out of  {len(result):,d} processed {files_processed:,d} files of total size {size_input:,d} input bytes')
    print(f'Wrote {size_index:,d} output bytes, ratio: {ratio:8.3%} at {ms_mb:.1f} ms/Mb')
    print('Bye, bye!')
    return ret_val


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
