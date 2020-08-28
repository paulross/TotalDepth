#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 1999-2020 Paul Ross
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
"""Reads a LIS file and writes out LAS files.

Created on 25 Mar 2011
"""
import datetime
import logging
import os
import sys
import time
import typing

import TotalDepth.common
from TotalDepth.LAS.core import WriteLAS, LASConstants
from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import FrameSet, File, FileIndexer, LogiRec, Mnem
from TotalDepth.common import LogPass
from TotalDepth.util import gnuplot, DirWalk, bin_file_type

__author__  = 'Paul Ross'
__date__    = '2020-08-10'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2020 Paul Ross. All rights reserved.'


logger = logging.getLogger(__file__)


LAS_PRODUCER_VERSION = '0.1.1'


def write_las_header(input_file: str,
                     # logical_file: LogicalFile.LogicalFile,
                     logical_file_number: int,
                     # frame_array_ident: str,
                     ostream: typing.TextIO) -> None:
    """Writes the LAS opening such as::

        ~Version Information Section
        VERS.           2.0                           : CWLS Log ASCII Standard - VERSION 2.0
        WRAP.           NO                            : One Line per depth step
        PROD.           TotalDepth                    : LAS Producer
        PROG.           TotalDepth.RP66V1.ToLAS 0.1.1 : LAS Program name and version
        CREA.           2012-11-14 10:50              : LAS Creation date [YYYY-MMM-DD hh:mm]
        SOURCE.         SOME-FILE-NAME.dlis           : LIS File Name
        LOGICAL-FILE.   3                             : Logical File number in the DLIS file

    Reference: [LAS2.0 Las2_Update_Feb2017.pdf Section 5.3 ~V (Version Information)]
    """
    now = datetime.datetime.utcnow()
    table: typing.List[typing.List[str]] = [
        ['VERS.', '2.0', ': CWLS Log ASCII Standard - VERSION 2.0'],
        ['WRAP.', 'NO', ': One Line per depth step'],
        ['PROD.', 'TotalDepth', ': LAS Producer'],
        ['PROG.', f'TotalDepth.LIS.ToLAS {LAS_PRODUCER_VERSION}', ': LAS Program name and version'],
        ['CREA.', f'{now.strftime(WriteLAS.LAS_DATETIME_FORMAT_UTC)}', f': LAS Creation date [{WriteLAS.LAS_DATE_FORMAT_TEXT}]'],
        ['SOURCE.', f'{os.path.basename(input_file)}', ': LIS File Name'],
        ['LOGICAL-FILE.', f'{logical_file_number:d}', ': Logical File number in the LIS file'],
    ]
    rows = TotalDepth.common.data_table.format_table(table, pad='  ', left_flush=True)
    ostream.write('~Version Information Section\n')
    for row in rows:
        ostream.write(row)
        ostream.write('\n')


class LisLogicalFile:
    """Contains a representation of a LIS Logical File which is a series of indexes followed by a Log Pass"""
    def __init__(self):
        self.cons_table_index_entries: typing.List[FileIndexer.IndexObjBase] = []
        self.last_log_pass: FileIndexer.IndexLogPass = None

    def __len__(self):
        ret = len(self.cons_table_index_entries)
        if self.last_log_pass is not None:
            ret += 1
        return ret

    def add_index(self, index_entry: FileIndexer.IndexObjBase) -> None:
        """Adds an index or Log Pass."""
        if isinstance(index_entry, FileIndexer.IndexLogPass):
            if self.last_log_pass is None or self.last_log_pass.logPass.totalFrames == 0:
                self.last_log_pass = index_entry
        elif isinstance(index_entry, FileIndexer.IndexTable) and index_entry.name == b'CONS':
            if self.last_log_pass is not None:
                raise ValueError(f'Adding a CONS table after a LogPass')
            self.cons_table_index_entries.append(index_entry)

    def is_end(self) -> bool:
        """Can be added to."""
        return self.last_log_pass is not None


def stringify(value: typing.Any, float_format: str) -> str:
    """Convert an object to a string respecting the requested floating point format."""
    if isinstance(value, bytes):
        value_str = value.decode('ascii', 'ignore')
    elif isinstance(value, float):
        value_str = f'{value:{float_format}}'
    else:
        value_str = str(value)
    return value_str


def write_table(section: str, table: typing.List[typing.List[str]], out_stream: typing.TextIO) -> None:
    """For a given LAS section then format the table and write it out to the stream."""
    out_stream.write(f'{section}\n')
    rows = TotalDepth.common.data_table.format_table(table, pad='  ', left_flush=True)
    for row in rows:
        out_stream.write(row)
        out_stream.write('\n')


def _units_from_logical_record_table_row(row: LogiRec.TableRow) -> bytes:
    try:
        units = row[b'PUNI'].value
    except KeyError:
        try:
            units = row[b'TUNI'].value
        except KeyError:
            units = b'N/A'
    return units


def write_well_information_section(lis_logical_file: LisLogicalFile,
                                   frame_slice: typing.Union[
                                       TotalDepth.common.Slice.Slice, TotalDepth.common.Slice.Sample
                                   ],
                                   float_format: str,
                                   out_stream: typing.TextIO) -> None:
    log_pass = lis_logical_file.last_log_pass.logPass
    step = log_pass.xAxisSpacingOptical * frame_slice.step(log_pass.totalFrames)
    table: typing.List[typing.List[str]] = [
        ['#MNEM.UNIT', 'Value', 'Description'],
        ['#---------', '-----', '-----------'],
        [
            f'STRT.{log_pass.xAxisUnitsOptical.decode("ascii")}',
            f'{log_pass.xAxisFirstValOptical:{float_format}}',
            ': START',
        ],
        [
            f'STOP.{log_pass.xAxisUnitsOptical.decode("ascii")}',
            f'{log_pass.xAxisLastValOptical:{float_format}}',
            ': STOP',
        ],
        [
            f'STEP.{log_pass.xAxisUnitsOptical.decode("ascii")}',
            f'{step:{float_format}}',
            ': STEP',
        ],
        [
            f'NULL.',
            f'{log_pass.nullValue:{float_format}}',
            ': NULL VALUE',
        ],
    ]
    # Extract the data from b'CONS' tables.
    for table_index in lis_logical_file.cons_table_index_entries:
        logical_record: LogiRec.LrTable = table_index.logicalRecord
        assert (logical_record is not None)
        for row_name_bytes in logical_record.genRowNames(sort=1):
            row: LogiRec.TableRow = logical_record.retRowByMnem(Mnem.Mnem(row_name_bytes))
            if row_name_bytes in LASConstants.WELL_SITE_MNEMONIC_DESCRIPTIONS:
                units = _units_from_logical_record_table_row(row).decode('ascii')
                try:
                    value = row[b'VALU'].value
                except KeyError:
                    value = 'N/A'
                value_str = stringify(value, float_format)
                desc = LASConstants.WELL_SITE_MNEMONIC_DESCRIPTIONS[row_name_bytes]
                table.append([f'{row_name_bytes.decode("ascii")}.{units}', value_str, f': {desc}', ])
    write_table('~Well Information Section', table, out_stream)


def write_curve_information_section(lis_logical_file: LisLogicalFile, out_stream: typing.TextIO) -> None:
    table: typing.List[typing.List[str]] = [
        ['#MNEM.UNIT', 'API CODE',    'Curve Description'],
        ['#---------', '------------', '-----------------'],
    ]
    log_pass = lis_logical_file.last_log_pass.logPass
    frame_set = log_pass.frameSet
    assert frame_set is not None
    if frame_set.isIndirectX:
        table.append(
            [
                f'X   .{frame_set.xAxisDecl.depthUnits.decode("ascii")}',
                '00 001 00 00',
                ': X axis (implied)'
            ]
        )

    for i, mnemonic, units in log_pass.genFrameSetChIndexScNameUnit(toAscii=False):
        # print(f'TRACE: YYYY {log_pass.dfsr.dsbBlocks[i].apiLogType}')
        desc = LASConstants.CURVE_MNEM_DESCRIPTIONS.get(mnemonic.strip(), 'N/A')
        table.append(
            [
                f'{mnemonic.decode("ascii")}.{units.decode("ascii")}',
                # 'TODO: API',
                (
                    f'{log_pass.dfsr.dsbBlocks[i].apiLogType:2}'
                    f' {log_pass.dfsr.dsbBlocks[i].apiCurveType:3}'
                    f' {log_pass.dfsr.dsbBlocks[i].apiCurveClass:2}'
                    f' {log_pass.dfsr.dsbBlocks[i].apiModifier:2}'
                ),
                f': {desc} '
            ]
        )
    write_table('~Curve Information Section', table, out_stream)


def write_parameter_information_section(lis_logical_file: LisLogicalFile, float_format: str, out_stream: typing.TextIO) -> None:
    table: typing.List[typing.List[str]] = [
        ['#MNEM.UNIT', 'Value', 'Description'],
        ['#---------', '-----', '-----------'],
    ]
    # Extract the data from b'CONS' tables that is NOT in the Well Information Section.
    for table_index in lis_logical_file.cons_table_index_entries:
        logical_record: LogiRec.LrTable = table_index.logicalRecord
        assert (logical_record is not None)
        for row_name_bytes in logical_record.genRowNames(sort=1):
            row: LogiRec.TableRow = logical_record.retRowByMnem(Mnem.Mnem(row_name_bytes))
            if row_name_bytes not in LASConstants.WELL_SITE_MNEMONIC_DESCRIPTIONS:
                units = _units_from_logical_record_table_row(row).decode("ascii")
                try:
                    value = row[b'VALU'].value
                except KeyError:
                    value = 'N/A'
                value_str = stringify(value, float_format)
                desc = LASConstants.PARAMETER_MNEM_DESCRIPTION.get(row_name_bytes, 'N/A')
                table.append([f'{row_name_bytes.decode("ascii")}.{units}', value_str, f': {desc}',])
    write_table('~Parameter Information Section', table, out_stream)


def write_array_section(lis_logical_file: LisLogicalFile, array_reduction: str, field_width: int, float_format: str,
                        out_stream: typing.TextIO) -> None:
    log_pass = lis_logical_file.last_log_pass.logPass
    frame_set: FrameSet.FrameSet = log_pass.frameSet
    assert frame_set is not None

    out_stream.write('~A (ASCII Log Data)\n')
    out_stream.write('#')
    if frame_set.isIndirectX:
        x_axis = f'X   .{frame_set.xAxisDecl.depthUnits.decode("ascii")}'
        out_stream.write(f'{x_axis:{field_width - 6}}')
    for m_u in [f'{mnemonic}.{units}' for mnemonic, units in log_pass.genFrameSetScNameUnit(toAscii=True)]:
        out_stream.write(f'{m_u:>{field_width}}')
    out_stream.write('\n')

    for frame_index in range(frame_set.numFrames):
        if frame_set.isIndirectX:
            out_stream.write(stringify(frame_set.xAxisValue(frame_index), float_format))
            out_stream.write(' ')
        for channel_index in range(frame_set.numChannels):
            for sub_channel_index in range(frame_set.numSubChannels(channel_index)):
                values = frame_set.frame_channel_sub_channel_values(frame_index, channel_index, sub_channel_index)
                value = LogPass.array_reduce(values, array_reduction)
                out_stream.write(f'{stringify(value, float_format):>{field_width}}')
        out_stream.write('\n')


def write_las_file(path_in: str,
                   array_reduction: str,
                   path_out: str,
                   frame_slice: typing.Union[TotalDepth.common.Slice.Slice, TotalDepth.common.Slice.Sample],
                   channels: typing.Set[str],
                   field_width: int,
                   float_format: str,
                   lis_file: File.FileRead,
                   logical_file_index: int,
                   lis_logical_file: LisLogicalFile,
                   ) -> int:
    """Writes a single LAS file corresponding ot a LIS logical file (set of CONS tables and a LogPass)."""
    logger.info(f'write_las_file(): path_in: {path_in} path_out: {path_out}')
    output_file = f'{path_out}_{logical_file_index}.las'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    logger.info(f'Writing to LAS {output_file}')
    with open(output_file, 'w') as out_stream:
        # Write the LAS header.
        write_las_header(path_in, logical_file_index, out_stream)
        # Write the well information
        if lis_logical_file.last_log_pass:
            write_well_information_section(lis_logical_file, frame_slice, float_format, out_stream)
        # Populate the Log Pass before writing the curve information
        if lis_logical_file.last_log_pass is not None:
            lis_frame_slice = slice(
                frame_slice.first(lis_logical_file.last_log_pass.logPass.totalFrames),
                frame_slice.last(lis_logical_file.last_log_pass.logPass.totalFrames) + 1,
                frame_slice.step(lis_logical_file.last_log_pass.logPass.totalFrames),
            )
            if len(channels) == 0:
                lis_logical_file.last_log_pass.logPass.setFrameSet(lis_file, lis_frame_slice, None)
            else:
                lis_logical_file.last_log_pass.logPass.setFrameSet(lis_file, lis_frame_slice, channels)
            # Write the curve information
            write_curve_information_section(lis_logical_file, out_stream)
        write_parameter_information_section(lis_logical_file, float_format, out_stream)
        if lis_logical_file.last_log_pass is not None:
            write_array_section(lis_logical_file, array_reduction, field_width, float_format, out_stream)
    return os.path.getsize(output_file)


def single_lis_file_to_las(path_in: str,
                           array_reduction: str,
                           path_out: str,
                           frame_slice: typing.Union[TotalDepth.common.Slice.Slice, TotalDepth.common.Slice.Sample],
                           channels: typing.Set[str],
                           field_width: int,
                           float_format: str,
                           ) -> WriteLAS.LASWriteResult:
    logger.info(f'single_lis_file_to_las(): path_in: {path_in} path_out: {path_out}')
    assert array_reduction in TotalDepth.common.LogPass.ARRAY_REDUCTIONS, f'{array_reduction} not in {TotalDepth.common.LogPass.ARRAY_REDUCTIONS}'
    binary_file_type = bin_file_type.binary_file_type_from_path(path_in)
    sum_path_out = las_file_count = 0
    if not bin_file_type.is_lis_file_type(binary_file_type):
        return WriteLAS.LASWriteResult(path_in, os.path.getsize(path_in), sum_path_out, las_file_count, 0.0, False,
                                       True)
    clock_start = time.perf_counter()
    try:
        logger.info(f'Reading {binary_file_type} in {path_in}')
        logging.info('Index.indexFile(): {:s}'.format(path_in))
        assert (os.path.isfile(path_in))
        lis_file = File.FileRead(path_in, theFileId=path_in, keepGoing=True)
        lis_file_index = FileIndexer.FileIndex(lis_file)
        # Run through the complete index splitting it up into 'logical files'
        # A logical file is a set of 'CONS' IndexTable entries followed by a LogPass
        # Each Logical File -> LAS output file.
        logical_file_entries: typing.List[LisLogicalFile] = []
        logical_file = LisLogicalFile()
        for l, lis_index in enumerate(lis_file_index.genAll()):
            logger.debug('LIS Index %s', lis_index)
            if isinstance(lis_index, FileIndexer.IndexTable) and lis_index.name == b'CONS':
                # Create the Logical Record
                lis_index.setLogicalRecord(lis_file)
                if logical_file.is_end():
                    logical_file_entries.append(logical_file)
                    logical_file = LisLogicalFile()
            logical_file.add_index(lis_index)
        if len(logical_file):
            logical_file_entries.append(logical_file)
        logger.info('LIS Logical Files: %s',  logical_file_entries)
        for l, lis_logical_file in enumerate(logical_file_entries):
            try:
                sum_path_out = write_las_file(path_in, array_reduction, path_out, frame_slice, channels, field_width,
                                              float_format,
                                              lis_file, l, lis_logical_file)
                las_file_count += 1
            except Exception as error:
                logger.exception(f'Unable to write LAS file with error {error}')
        return WriteLAS.LASWriteResult(path_in, os.path.getsize(path_in), sum_path_out, las_file_count,
                                       time.perf_counter() - clock_start, False, False)
    except ExceptionTotalDepthLIS as error:
        logger.error(f'Could not convert file {path_in} to LAS with error: {error}')
    except Exception as error:
        logger.exception(f'Unable to write LAS file with error {error}')
    return WriteLAS.LASWriteResult(path_in, os.path.getsize(path_in), sum_path_out, las_file_count,
                                   time.perf_counter() - clock_start, True, False)


def _dump_frames_and_or_channels_single_lis_file(path_in: str, frame_slices: bool, channels: bool) -> None:
    """Write a summary of frames and channels."""
    assert frame_slices or channels
    binary_file_type = bin_file_type.binary_file_type_from_path(path_in)
    if bin_file_type.is_lis_file_type(binary_file_type):
        logger.info(f'Reading {binary_file_type} in {path_in}')
        try:
            with TotalDepth.common.colorama.section(f'File {path_in}', '=', out_stream=sys.stdout):
                lis_file = File.FileRead(path_in, theFileId=path_in, keepGoing=True)
                lis_index = FileIndexer.FileIndex(lis_file)
                for l, log_pass in enumerate(lis_index.genLogPasses()):
                    if log_pass.logPass.totalFrames:
                        print(f'Log pass {l}:')
                        if channels:
                            print(f'Available channels: {[m.pStr() for m in log_pass.logPass.outpMnemS()]}')
                        if frame_slices:
                            print(log_pass.logPass.x_axis_str())
        except ExceptionTotalDepthLIS:  # pragma: no cover
            logger.exception(f'Failed to index with ExceptionTotalDepthLIS: {path_in}')
        except Exception:  # pragma: no cover
            logger.exception(f'Failed to index with Exception: {path_in}')
    else:
        logger.error(f'Path {path_in} is not a LIS file.')


def _dump_frames_and_or_channels(path_in: str, recurse: bool, frame_slice: str, channels: str) -> None:
    """Dump available channels and frames."""
    assert frame_slice == '?' or channels == '?'
    if os.path.isdir(path_in):
        for file_in_out in DirWalk.dirWalk(path_in, '', theFnMatch='', recursive=recurse, bigFirst=False):
            _dump_frames_and_or_channels_single_lis_file(file_in_out.filePathIn, frame_slice == '?', channels == '?')
    else:
        _dump_frames_and_or_channels_single_lis_file(path_in, frame_slice == '?', channels == '?')


def main():
    description = """usage: %(prog)s [options] file
    Reads RP66V1 file(s) and writes them out as LAS files."""
    print('Cmd: %s' % ' '.join(sys.argv))

    parser = TotalDepth.common.cmn_cmd_opts.path_in_out_required(
        description, prog='TotalDepth.RP66V1.ToLAS.main', version=__version__, epilog=__rights__
    )
    TotalDepth.common.cmn_cmd_opts.add_log_level(parser, level=20)
    TotalDepth.common.cmn_cmd_opts.add_multiprocessing(parser)
    TotalDepth.common.Slice.add_frame_slice_to_argument_parser(parser, use_what=True)
    TotalDepth.common.process.add_process_logger_to_argument_parser(parser)
    gnuplot.add_gnuplot_to_argument_parser(parser)
    parser.add_argument(
        '--array-reduction', type=str,
        help='Method to reduce multidimensional channel data to a single value. [default: %(default)s]',
        default='first',
        choices=list(sorted(TotalDepth.common.LogPass.ARRAY_REDUCTIONS)),
    )
    parser.add_argument(
        '--channels', type=str,
        help='Comma separated list of channels to write out (X axis is always included).'
             ' Use \'?\' to see what channels exist without writing anything. [default: "%(default)s"]',
        default='',
    )
    parser.add_argument('--field-width', type=int,
                        help='Field width for array data [default: %(default)s].', default=16)
    parser.add_argument('--float-format', type=str,
                        help='Floating point format for array data [default: "%(default)s"].', default='.3f')
    args = parser.parse_args()
    TotalDepth.common.cmn_cmd_opts.set_log_level(args)
    # Your code here
    ret_val = 0
    if args.frame_slice.strip() == '?' or args.channels.strip() == '?':
        _dump_frames_and_or_channels(args.path_in, args.recurse, args.frame_slice.strip(), args.channels.strip())
    else:
        clk_start = time.perf_counter()
        results: typing.Dict[str, WriteLAS.LASWriteResult] = WriteLAS.process_to_las(args, single_lis_file_to_las)
        clk_exec = time.perf_counter() - clk_start
        # Report output
        failed_files = WriteLAS.report_las_write_results(results, args.gnuplot)
        print(f' Total files: {len(results)}')
        print(f'Failed files: {failed_files}')
        size_input, size_output = WriteLAS.las_size_input_output(results)
        print('Execution time = %8.3f (S)' % clk_exec)
        if size_input > 0:
            ms_mb = clk_exec * 1000 / (size_input/ 1024**2)
            ratio = size_output / size_input
        else:
            ms_mb = 0.0
            ratio = 0.0
        print(f'Out of  {len(results):,d} processed {len(results):,d} files of total size {size_input:,d} input bytes')
        print(f'Wrote {size_output:,d} output bytes, ratio: {ratio:8.3%} at {ms_mb:.1f} ms/Mb')
        print(f'Execution time: {clk_exec:.3f} (s)')
    print('Bye, bye!')
    return ret_val


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
