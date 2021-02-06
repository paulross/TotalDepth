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
"""
Converts RP66V1 files to LAS files.

References:

* General: http://www.cwls.org/las/
* LAS Version 2: http://www.cwls.org/wp-content/uploads/2017/02/Las2_Update_Feb2017.pdf

Example reference to the LAS documentation in this source code::

    [LAS2.0 Las2_Update_Feb2017.pdf Section 5.3 ~V (Version Information)]

"""
import datetime
import logging
import os
import sys
import time
import typing

import TotalDepth.common
from TotalDepth.LAS.core import WriteLAS
from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import LogPass
from TotalDepth.RP66V1.core import LogicalFile
from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core import XAxis
from TotalDepth.RP66V1.core import stringify
from TotalDepth.RP66V1.core.LogicalRecord import EFLR
from TotalDepth.util import bin_file_type
from TotalDepth.util import gnuplot
from TotalDepth.util.DirWalk import dirWalk

__author__  = 'Paul Ross'
__date__    = '2019-04-10'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


LAS_PRODUCER_VERSION = '0.1.2'


logger = logging.getLogger(__file__)


def write_las_header(input_file: str,
                     logical_file: LogicalFile.LogicalFile,
                     logical_file_number: int,
                     frame_array_ident: str,
                     output_stream: typing.TextIO) -> None:
    """Writes the LAS opening such as::

        ~Version Information Section
        VERS.           2.0                           : CWLS Log ASCII Standard - VERSION 2.0
        WRAP.           NO                            : One Line per depth step
        PROD.           TotalDepth                    : LAS Producer
        PROG.           TotalDepth.RP66V1.ToLAS 0.1.1 : LAS Program name and version
        CREA.           2012-11-14 10:50              : LAS Creation date [YYYY-MMM-DD hh:mm]
        DLIS_CREA.      2012-11-10 22:06              : DLIS Creation date and time [YYYY-MMM-DD hhmm]
        SOURCE.         SOME-FILE-NAME.dlis           : DLIS File Name
        FILE-ID.        SOME-FILE-ID                  : File Identification from the FILE-HEADER Logical Record
        LOGICAL-FILE.   3                             : Logical File number in the DLIS file
        FRAME-ARRAY.    60B                           : Identity of the Frame Array in the Logical File

    Reference: [LAS2.0 Las2_Update_Feb2017.pdf Section 5.3 ~V (Version Information)]
    """
    date_time = logical_file.defining_origin[b'CREATION-TIME'].value[0]
    dt = date_time.as_datetime()
    fhlr: EFLR.ExplicitlyFormattedLogicalRecord = logical_file.file_header_logical_record
    file_id = fhlr.objects[0][b'ID'].value[0].decode('ascii').strip()
    table_extend = [
        [
            f'DLIS_CREA.',
            f'{dt.strftime(WriteLAS.LAS_DATETIME_FORMAT_UTC)}',
            f': DLIS Creation date and time [{WriteLAS.LAS_DATE_FORMAT_TEXT}]'
        ],
        ['FILE-ID.', f'{file_id}', ': File Identification Number'],
    ]
    if frame_array_ident:
        table_extend.append(
            ['FRAME-ARRAY.', f'{frame_array_ident}', ': Identity of the Frame Array in the Logical File'],
        )
    WriteLAS.write_las_header(
        input_file, logical_file_number, 'TotalDepth.RP66V1.ToLAS', LAS_PRODUCER_VERSION, table_extend, output_stream
    )


#: Mapping of DLIS ``EFLR`` Type and Object Name to ``LAS WELL INFORMATION`` section and Mnemonic.
#: The Object ``LONG-NAME`` is used as the LAS description.
#: We prefer to take data from the ORIGIN ``EFLR`` as it is more clearly specified
#: ``[RP66V1 5.2 Origin Logical Record (OLR)]``
#: whereas the ``PARAMETER EFLR`` tables are fairly free form.
#: See also ``[RP66V1 Section 5.8.2 Parameter Objects]``
DLIS_TO_WELL_INFORMATION_LAS_EFLR_MAPPING: typing.Dict[bytes, typing.Dict[bytes, str]] = {
    # [RP66V1 Section 5.8.2 Parameter Objects]
    b'PARAMETER': {
        # b'WN': 'WELL',
        b'LOC ': 'LOC ',
        b'COUN': 'CNTY',
        b'STAT': 'STAT',
        b'NATI': 'CTRY',
        b'APIN': 'API ',
        b'UWI ': 'UWI ',
        # b'DATE': 'DATE',
        b'LATI': 'LATI',
        b'LONG': 'LONG',
    },
}


#: [RP66V1 Section 5.2 Origin Logical Record (OLR)]
WELL_INFORMATION_FROM_ORIGIN: typing.Dict[bytes, str] = {
    b'COMPANY': 'COMP',
    b'WELL-NAME': 'WELL',
    b'FIELD-NAME': 'FLD ',
    b'CREATION-TIME': 'DATE',
    b'PRODUCER-NAME': 'SRVC',
}


def extract_well_information_from_origin(logical_file: LogicalFile.LogicalFile) \
        -> typing.Dict[str, WriteLAS.UnitValueDescription]:
    """Extracts partial well information from the ORIGIN record. Example:

    .. code-block:: console

        Objects [1]:
        OBNAME: O: 11 C: 0 I: b'DLIS_DEFINING_ORIGIN'
          CD: 001 00001 L: b'FILE-ID' C: 1 R: ASCII U: b'' V: [b'auto_las_survey']
          CD: 001 00001 L: b'FILE-SET-NAME' C: 1 R: IDENT U: b'' V: [b'']
          CD: 001 00001 L: b'FILE-SET-NUMBER' C: 1 R: UVARI U: b'' V: [1]
          CD: 001 00001 L: b'FILE-NUMBER' C: 1 R: UVARI U: b'' V: [1]
          CD: 001 00001 L: b'FILE-TYPE' C: 1 R: IDENT U: b'' V: [b'DEPTH-LOG']
          CD: 001 00001 L: b'PRODUCT' C: 1 R: ASCII U: b'' V: [b'RX6']
          CD: 001 00001 L: b'VERSION' C: 1 R: ASCII U: b'' V: [b'v0.0']
          CD: 000 00000 L: b'PROGRAMS' C: 1 R: ASCII U: b'' V: None
          CD: 001 00001 L: b'CREATION-TIME' C: 1 R: DTIME U: b'' V: [<<class 'TotalDepth.RP66V1.core.RepCode.DateTime'> 2015-08-16 04:57:12.000 STD>]
          CD: 001 00001 L: b'ORDER-NUMBER' C: 1 R: ASCII U: b'' V: [b'0000']
          CD: 000 00000 L: b'DESCENT-NUMBER' C: 1 R: ULONG U: b'' V: None
          CD: 001 00001 L: b'RUN-NUMBER' C: 1 R: ULONG U: b'' V: [1]
          CD: 000 00000 L: b'WELL-ID' C: 1 R: IDENT U: b'' V: None
          CD: 001 00001 L: b'WELL-NAME' C: 1 R: ASCII U: b'' V: [b'PRASLIN 1                          ']
          CD: 001 00001 L: b'FIELD-NAME' C: 1 R: ASCII U: b'' V: [b'PRASLIN PROSPECT                   ']
          CD: 001 00001 L: b'PRODUCER-CODE' C: 1 R: UNORM U: b'' V: [440]
          CD: 001 00001 L: b'PRODUCER-NAME' C: 1 R: ASCII U: b'' V: [b'PathFinder']
          CD: 001 00001 L: b'COMPANY' C: 1 R: ASCII U: b'' V: [b'BURU ENERGY                        ']
          CD: 001 00001 L: b'NAME-SPACE-NAME' C: 1 R: IDENT U: b'' V: [b'PF']
          CD: 000 00000 L: b'NAME-SPACE-VERSION' C: 1 R: UVARI U: b'' V: None
    """
    las_map: typing.Dict[str, WriteLAS.UnitValueDescription] = {}
    # print('TRACE: ORIGIN', logical_file.origin_logical_record.str_long())
    defining_origin: EFLR.Object = logical_file.defining_origin
    for attr in WELL_INFORMATION_FROM_ORIGIN:
        units = defining_origin[attr].units.decode('ascii')
        value = stringify.stringify_object_by_type(defining_origin[attr].value).strip()
        descr = ''
        # NOTE: Overwriting is possible here.
        las_map[WELL_INFORMATION_FROM_ORIGIN[attr]] = WriteLAS.UnitValueDescription(units, value, descr)
    return las_map


def _add_start_stop_step_to_dictionary(
        logical_file: LogicalFile.LogicalFile,
        frame_array: typing.Union[LogPass.RP66V1FrameArray, None],
        frame_slice: typing.Union[TotalDepth.common.Slice.Slice, TotalDepth.common.Slice.Sample],
        las_map: typing.Dict[str, WriteLAS.UnitValueDescription]
):
    """Adds the START, STOP STEP values for the  Frame Array."""
    if frame_array is not None:
        # Add the start/stop/step data
        x_units: str = frame_array.x_axis.units.decode('ascii')
        iflr_data: typing.List[XAxis.IFLRReference] = logical_file.iflr_position_map[frame_array.ident]
        assert len(iflr_data)
        num_frames_to_write = frame_slice.count(len(iflr_data))
        x_strt: float = iflr_data[frame_slice.first(len(iflr_data))].x_axis
        x_stop: float = iflr_data[frame_slice.last(len(iflr_data))].x_axis
        las_map['STRT'] = WriteLAS.UnitValueDescription(x_units, stringify.stringify_object_by_type(x_strt), 'Start X')
        las_map['STOP'] = WriteLAS.UnitValueDescription(
            x_units, stringify.stringify_object_by_type(x_stop),
            f'Stop X, frames {num_frames_to_write} out of {len(iflr_data):,d} available.'
        )
        if num_frames_to_write > 1:
            x_step: float = (x_stop - x_strt) / float(num_frames_to_write - 1)
            las_map['STEP'] = WriteLAS.UnitValueDescription(
                x_units, stringify.stringify_object_by_type(x_step), 'Step (average)'
            )
        else:
            las_map['STEP'] = WriteLAS.UnitValueDescription('N/A', 'N/A', 'Step (average)')
    else:
        las_map['STRT'] = WriteLAS.UnitValueDescription('N/A', 'N/A', 'Start X')
        las_map['STOP'] = WriteLAS.UnitValueDescription('N/A', 'N/A', 'Stop X')
        las_map['STEP'] = WriteLAS.UnitValueDescription('N/A', 'N/A', 'Step (average)')


def write_well_information_to_las(
        logical_file: LogicalFile.LogicalFile,
        frame_array: typing.Union[LogPass.RP66V1FrameArray, None],
        frame_slice: typing.Union[TotalDepth.common.Slice.Slice, TotalDepth.common.Slice.Sample],
        ostream: typing.TextIO,
    ) -> None:
    """Writes the well information section.

    Reference: ``[LAS2.0 Las2_Update_Feb2017.pdf Section 5.4 ~W (Well Information)]``
    """
    # Tuple of (units, value, description)
    las_map: typing.Dict[str, WriteLAS.UnitValueDescription] = extract_well_information_from_origin(logical_file)
    _add_start_stop_step_to_dictionary(logical_file, frame_array, frame_slice, las_map)
    eflr: EFLR.ExplicitlyFormattedLogicalRecord
    for _lrsh_position, eflr in logical_file.eflrs:
        if eflr.set.type in DLIS_TO_WELL_INFORMATION_LAS_EFLR_MAPPING:
            bytes_index_map: typing.Dict[bytes, int] = EFLR.reduced_object_map(eflr)
            for row_key in DLIS_TO_WELL_INFORMATION_LAS_EFLR_MAPPING[eflr.set.type]:
                if row_key in bytes_index_map:
                    obj = eflr[bytes_index_map[row_key]]
                    # ORIGIN is only key/value so does not have LONG-NAME
                    # PARAMETER does have LONG-NAME
                    units = obj[b'VALUES'].units.decode('ascii')
                    value = stringify.stringify_object_by_type(obj[b'VALUES'].value).strip()
                    descr = stringify.stringify_object_by_type(obj[b'LONG-NAME'].value).strip()
                    # NOTE: Overwriting is possible here.
                    las_map[row_key.decode('ascii')] = WriteLAS.UnitValueDescription(units, value, descr)
    table = [
        ['#MNEM.UNIT', 'DATA', 'DESCRIPTION',],
        ['#----.----', '----', '-----------',],
    ]
    for k in WriteLAS.WELL_INFORMATION_KEYS:
        if k in las_map:
            row = [f'{k:4}.{las_map[k].unit:4}', f'{las_map[k].value}', f': {las_map[k].description}',]
        else:
            row = [f'{k:4}.{"":4}', '', ':']
        table.append(row)
    WriteLAS.write_table(table, '~Well Information Section', ostream)


def write_parameter_section_to_las(
        logical_file: LogicalFile.LogicalFile,
        ostream: typing.TextIO,
    ) -> None:
    """Write the ``PARAMETER`` tables to LAS."""
    las_mnem_map: typing.Dict[RepCode.ObjectName, WriteLAS.UnitValueDescription] = {}
    for position_eflr in logical_file.eflrs:
        if position_eflr.eflr.set.type == b'PARAMETER':
            # print('TRACE:', position_eflr.eflr.str_long())
            for obj in position_eflr.eflr.objects:
                units = obj[b'VALUES'].units.decode('ascii')
                value = stringify.stringify_object_by_type(obj[b'VALUES'].value).strip()
                descr = stringify.stringify_object_by_type(obj[b'LONG-NAME'].value).strip()
                # NOTE: Overwriting is possible here.
                las_mnem_map[obj.name.I.decode('ascii')] = WriteLAS.UnitValueDescription(units, value, descr)
    table = [
        ['#MNEM.UNIT', 'Value', 'Description'],
        ['#---------', '-----', '-----------'],
    ]
    # pprint.pprint(las_mnem_map)
    for k in las_mnem_map:
        table.append(
            [f'{k:<4}.{las_mnem_map[k].unit:<4}', las_mnem_map[k].value, f': {las_mnem_map[k].description}']
        )
    WriteLAS.write_table(table, '~Parameter Information Section', ostream)


def las_file_name(path_out: str, logicial_file_index: int, frame_array_ident: bytes) -> str:
    """Returns the output file name."""
    file_name = os.path.splitext(os.path.basename(path_out))[0]
    file_path_out = os.path.join(
        os.path.dirname(path_out),
        file_name + f'_{logicial_file_index}_{frame_array_ident.decode("ascii")}' + '.las'
    )
    return file_path_out


def _write_array_section_to_las(
        logical_file: LogicalFile.LogicalFile,
        frame_array: LogPass.RP66V1FrameArray,
        array_reduction: str,
        frame_slice: TotalDepth.common.Slice.Slice,
        channel_name_sub_set: typing.Set[str],
        field_width: int,
        float_format: str,
        ostream: typing.TextIO,
    ) -> None:
    """Write the ``~Array Section`` to the LAS file, the actual log data"""
    # TODO: Could optimise memory by reading one frame at a time
    max_num_available_frames = logical_file.num_frames(frame_array)
    if len(channel_name_sub_set):
        array_channels = {c.ident for c in frame_array.channels if c.ident in channel_name_sub_set}
        num_writable_frames = logical_file.populate_frame_array(frame_array, frame_slice, array_channels)
    else:
        num_writable_frames = logical_file.populate_frame_array(frame_array, frame_slice)
    if num_writable_frames > 0:
        TotalDepth.LAS.core.WriteLAS.write_curve_and_array_section_to_las(
            frame_array,
            max_num_available_frames,
            array_reduction,
            frame_slice,
            channel_name_sub_set,
            field_width,
            float_format,
            ostream,
        )


def write_logical_index_to_las(
        logical_index: LogicalFile.LogicalIndex,
        array_reduction: str,
        path_out: str,
        frame_slice: typing.Union[TotalDepth.common.Slice.Slice, TotalDepth.common.Slice.Sample],
        channels: typing.Set[str],
        field_width: int,
        float_format: str,
) -> typing.List[str]:
    """Take a Logical Index for a Logical File within a RP66V1 file and write out a set of LAS 2.0 files."""
    assert array_reduction in TotalDepth.LAS.core.WriteLAS.ARRAY_REDUCTIONS
    ret = []
    for lf, logical_file in enumerate(logical_index.logical_files):
        TotalDepth.common.process.add_message_to_queue(f'Logical file {lf}')
        # Now the LogPass
        if logical_file.has_log_pass:
            for frame_array in logical_file.log_pass.frame_arrays:
                TotalDepth.common.process.add_message_to_queue(f'Frame Array {frame_array.ident.I}')
                file_path_out = las_file_name(path_out, lf, frame_array.ident.I)
                os.makedirs(os.path.dirname(file_path_out), exist_ok=True)
                logger.info(f'Starting LAS output file {file_path_out}')
                with open(file_path_out, 'w') as ostream:
                    # Write each section
                    write_las_header(
                        os.path.basename(logical_index.id),
                        logical_file, lf, frame_array.ident.I.decode('ascii'), ostream
                    )
                    write_well_information_to_las(logical_file, frame_array, frame_slice, ostream)
                    write_parameter_section_to_las(logical_file, ostream)
                    _write_array_section_to_las(
                        logical_file, frame_array, array_reduction, frame_slice,
                        channels, field_width, float_format, ostream
                    )
                    ret.append(file_path_out)
        else:
            file_path_out = las_file_name(path_out, lf, b'')
            os.makedirs(os.path.dirname(file_path_out), exist_ok=True)
            with open(file_path_out, 'w') as ostream:
                write_las_header(
                    os.path.basename(logical_index.id),
                    logical_file, lf, '', ostream
                )
                write_well_information_to_las(logical_file, None, frame_slice, ostream)
                write_parameter_section_to_las(logical_file, ostream)
                ret.append(file_path_out)
    return ret


def single_rp66v1_file_to_las(
        path_in: str,
        array_reduction: str,
        path_out: str,
        frame_slice: TotalDepth.common.Slice.Slice,
        channels: typing.Set[str],
        field_width: int,
        float_format: str,
) -> WriteLAS.LASWriteResult:
    """Convert a single RP66V1 file to a set of LAS files."""
    # logging.info(f'index_a_single_file(): "{path_in}" to "{path_out}"')
    assert array_reduction in TotalDepth.LAS.core.WriteLAS.ARRAY_REDUCTIONS, f'{array_reduction} not in {TotalDepth.LAS.core.WriteLAS.ARRAY_REDUCTIONS}'
    binary_file_type = bin_file_type.binary_file_type_from_path(path_in)
    if binary_file_type == 'RP66V1':
        logger.info(f'Converting RP66V1 {path_in} to LAS {os.path.splitext(path_out)[0]}*')
        try:
            t_start = time.perf_counter()
            with LogicalFile.LogicalIndex(path_in) as logical_index:
                las_files_written = write_logical_index_to_las(
                    logical_index, array_reduction, path_out, frame_slice, channels, field_width, float_format
                )
                output_size = sum(os.path.getsize(f) for f in las_files_written)
                result = WriteLAS.LASWriteResult(
                    path_in,
                    binary_file_type,
                    os.path.getsize(path_in),
                    output_size,
                    len(las_files_written),
                    time.perf_counter() - t_start,
                    False,
                    False,
                )
                logger.info(f'{len(las_files_written)} LAS file written with total size: {output_size:,d} bytes')
                return result
        except ExceptionTotalDepthRP66V1:  # pragma: no cover
            logger.exception(f'Failed to index with ExceptionTotalDepthRP66V1: {path_in}')
            return WriteLAS.LASWriteResult(path_in, binary_file_type, os.path.getsize(path_in), 0, 0, 0.0, True, False)
        except Exception:  # pragma: no cover
            logger.exception(f'Failed to index with Exception: {path_in}')
            return WriteLAS.LASWriteResult(path_in, binary_file_type, os.path.getsize(path_in), 0, 0, 0.0, True, False)
    logger.debug(f'Ignoring file type "{binary_file_type}" at {path_in}')
    return WriteLAS.LASWriteResult(path_in, binary_file_type, 0, 0, 0, 0.0, False, True)


def _dump_frames_and_or_channels_single_rp66v1_file(path_in: str, frame_slices, channels) -> None:
    """Write a summary of frames and channels."""
    binary_file_type = bin_file_type.binary_file_type_from_path(path_in)
    if binary_file_type == 'RP66V1':
        logger.info(f'Reading RP66V1 {path_in}')
        try:
            with TotalDepth.common.colorama.section(f'File {path_in}', '=', out_stream=sys.stdout):
                with LogicalFile.LogicalIndex(path_in) as logical_index:
                    for l, logical_file in enumerate(logical_index.logical_files):
                        with TotalDepth.common.colorama.section(f'Logical file [{l:04d}]: {logical_file}', '-',
                                                                out_stream=sys.stdout):
                            if logical_file.has_log_pass:
                                for frame_array in logical_file.log_pass.frame_arrays:
                                    print(f'  Frame Array: {frame_array.ident.I}')
                                    if channels:
                                        channel_text = b','.join(c.ident.I for c in frame_array.channels)
                                        print(f'  Channels: {channel_text}')
                                    if frame_slices:
                                        print(f'  X axis: {frame_array.x_axis}')
                                        iflr_refs = logical_file.iflr_position_map[frame_array.ident]
                                        x_spacing = (iflr_refs[-1].x_axis - iflr_refs[0].x_axis) / (len(iflr_refs) - 1)
                                        print(
                                            f'  Frames: {len(iflr_refs)}'
                                            f' from {iflr_refs[0].x_axis}'
                                            f' to {iflr_refs[-1].x_axis}'
                                            f' interval {x_spacing}'
                                            f' [{frame_array.x_axis.units}]'
                                        )
                                    print()
                            else:
                                print('No log pass')
                            # print()
        except ExceptionTotalDepthRP66V1:  # pragma: no cover
            logger.exception(f'Failed to index with ExceptionTotalDepthRP66V1: {path_in}')
        except Exception:  # pragma: no cover
            logger.exception(f'Failed to index with Exception: {path_in}')


def _dump_frames_and_or_channels(path_in: str, recurse: bool, frame_slice: str, channels: str) -> None:
    """Dump available channels and frames."""
    assert frame_slice == '?' or channels == '?'
    if os.path.isdir(path_in):
        for file_in_out in dirWalk(path_in, '', theFnMatch='', recursive=recurse, bigFirst=False):
            _dump_frames_and_or_channels_single_rp66v1_file(file_in_out.filePathIn, frame_slice == '?', channels == '?')
    else:
        _dump_frames_and_or_channels_single_rp66v1_file(path_in, frame_slice == '?', channels == '?')


_GNUPLOT_PLT = '\n'.join(
    [
        gnuplot.PLOT.format(title="Converting RP66V1 Files to LAS with TotalDepth.RP66V1.ToLAS.main"),
        gnuplot.X_LOG.format(label="RP66V1 File Size (bytes)"),
        gnuplot.Y_LOG.format(label="Conversion Time (s)"),
        gnuplot.Y2_LOG.format(label="Total LAS size"),
        """set terminal svg size 1000,700 # choose the file format
set output "{name}.svg" # choose the output device

# Curve fit, time
conversion_time(x) = 10**(a + b * log10(x))
fit conversion_time(x) "{name}.dat" using 1:4 via a, b

# Curve fit, size
las_size(x) = 10**(c + d * log10(x))
fit las_size(x) "{name}.dat" using 1:2 via c,d

plot "{name}.dat" using 1:4 axes x1y1 title "LAS Conversion Time (s)" lt 1 w points, \
    conversion_time(x) title sprintf("Fit of time: 10**(%+.3g %+.3g * log10(x))", a, b) lt 1 lw 2, \
    "{name}.dat" using 1:2 axes x1y2 title "LAS size (bytes)" lt 3 w points, \
    las_size(x) axes x1y2 title sprintf("Fit of size: 10**(%+.3g %+.3g * log10(x))", c, d) lt 3 lw 2

reset
""",
    ]
)


def main() -> int:
    """Main entry point."""
    print('Cmd: %s' % ' '.join(sys.argv))
    description = """usage: %(prog)s [options] file
Reads RP66V1 file(s) and writes them out as LAS files."""
    parser = WriteLAS.las_writer_command_line_arguments(description, prog='TotalDepth.RP66V1.ToLAS.main',
                                                        version=__version__, epilog=__rights__)
    args = parser.parse_args()
    TotalDepth.common.cmn_cmd_opts.set_log_level(args)
    # Your code here
    ret_val = 0
    if args.frame_slice.strip() == '?' or args.channels.strip() == '?':
        _dump_frames_and_or_channels(args.path_in, args.recurse, args.frame_slice.strip(), args.channels.strip())
    else:
        clk_start = time.perf_counter()
        result: typing.Dict[str, WriteLAS.LASWriteResult] = WriteLAS.process_to_las(args, single_rp66v1_file_to_las)
        clk_exec = time.perf_counter() - clk_start
        _failed_file_count = WriteLAS.report_las_write_results_and_performance(result, clk_exec, args.gnuplot, include_ignored=False)
    print('Bye, bye!')
    return ret_val


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
