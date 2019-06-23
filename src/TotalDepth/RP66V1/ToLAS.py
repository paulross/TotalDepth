"""
Converts RP66V1 files to LAS files.

References: http://www.cwls.org/las/
Version 2: http://www.cwls.org/wp-content/uploads/2017/02/Las2_Update_Feb2017.pdf

Example reference in this source code:
[LAS2.0 Las2_Update_Feb2017.pdf Section 5.3 ~V (Version Information)]
"""
import argparse
import collections
import datetime
import io
import logging
import os
import pprint
import sys
import time
import typing

import numpy as np

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import LogicalFile, File, RepCode, LogPass, stringify
from TotalDepth.RP66V1.core.LogicalRecord import IFLR, EFLR
from TotalDepth.common import data_table
from TotalDepth.util.DirWalk import dirWalk
from TotalDepth.util.bin_file_type import binary_file_type_from_path
from TotalDepth.util import gnuplot

__author__  = 'Paul Ross'
__date__    = '2019-04-10'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


logger = logging.getLogger(__file__)


class LASWriteResult(typing.NamedTuple):
    size_input: int
    size_output: int
    las_count: int
    time: float
    exception: bool
    ignored: bool


LAS_DATE_HM_FORMAT = '%Y-%m-%d %H:%M'
LAS_DATE_HM_FORMAT_TEXT = 'YYYY-mm-dd HH:MM'


def _write_las_header(input_file: str,
                      logical_file: LogicalFile.LogicalFile,
                      logical_file_number: int,
                      frame_array_ident: str,
                      ostream: typing.TextIO) -> None:
    """Writes the LAS opening such as:

    ~Version Information Section
    VERS.           2.0                     :CWLS Log ASCII Standard - VERSION 2.0
    WRAP.           NO                      :One Line per depth step
    PROD.           TotalDepth              :LAS Producer
    PROG.           TotalDepth.RP66V1.ToLAS :LAS Program name and version
    CREA.           2012-11-14 10:50        :LAS Creation date [YYYY-MMM-DD hh:mm]
    DLIS_CREA.      2012-11-10 22:06        :DLIS Creation date and time [YYYY-MMM-DD hh:mm]
    SOURCE.         SOME-FILE-NAME.dlis     :DLIS File Name
    FILE-ID.        SOME-FILE-ID            :File Identification from the FILE-HEADER Logical Record
    LOGICAL-FILE.   3                       :Logical File number in the DLIS file
    FRAME-ARRAY.    60B                     :Identity of the Frame Array in the Logical File

    Reference: [LAS2.0 Las2_Update_Feb2017.pdf Section 5.3 ~V (Version Information)]
    """
    now = datetime.datetime.now()
    date_time = logical_file.defining_origin[b'CREATION-TIME'].value[0]
    dt = date_time.as_datetime()
    fhlr: EFLR.ExplicitlyFormattedLogicalRecord = logical_file.file_header_logical_record
    file_id = fhlr.objects[0][b'ID'].value[0].decode('ascii').strip()
    table: typing.List[typing.List[str]] = [
        ['VERS.', '2.0', ': CWLS Log ASCII Standard - VERSION 2.0'],
        ['WRAP.', 'NO', ': One Line per depth step'],
        ['PROD.', 'TotalDepth', ':LAS Producer'],
        ['PROG.', 'TotalDepth.RP66V1.ToLAS', ': LAS Program name and version'],
        ['CREA.', f'{now.strftime(LAS_DATE_HM_FORMAT)}', f': LAS Creation date [{LAS_DATE_HM_FORMAT_TEXT}]'],
        [f'DLIS_CREA.', f'{dt.strftime(LAS_DATE_HM_FORMAT)}', f': DLIS Creation date and time [{LAS_DATE_HM_FORMAT_TEXT}]'],
        ['SOURCE.', f'{os.path.basename(input_file)}', ': DLIS File Name'],
        ['FILE-ID.', f'{file_id}', ': File Identification Number'],
        ['LOGICAL-FILE.', f'{logical_file_number:d}', ': Logical File number in the DLIS file'],
    ]
    if frame_array_ident:
        table.append(
            ['FRAME-ARRAY.', f'{frame_array_ident}', ': Identity of the Frame Array in the Logical File'],
        )
    rows = data_table.format_table(table, pad='  ', left_flush=True)
    ostream.write('~Version Information Section\n')
    for row in rows:
        ostream.write(row)
        ostream.write('\n')


class UnitValueDescription(typing.NamedTuple):
    """Class for accumulating data from PARAMETER tables and Well Information sections."""
    unit: str
    value: str
    description: str


#: Mapping of DLIS EFLR Type and Object Name to LAS WELL INFORMATION section and Mnemonic
#: The Object LONG-NAME is used as the LAS description.
#: We prefer to take data from the ORIGIN EFLR as it is more clearly specified [RP66V1 5.2 Origin Logical Record (OLR)]
#: whereas PARAMETER EFLRs are fairly free form.
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

#: Order of fields for the Well Information section.
WELL_INFORMATION_KEYS: typing.Tuple[str, ...] = (
    'STRT', 'STOP', 'STEP',
    'NULL',
    'COMP', 'WELL', 'FLD ',  # From the ORIGIN record
    'LOC',
    'CNTY', 'STAT', 'CTRY', 'API ', 'UWI ',
    'DATE', 'SRVC',  # From the ORIGIN record
    'LATI', 'LONG', 'GDAT',
)

# [RP66V1 Section 5.2 Origin Logical Record (OLR)]
WELL_INFORMATION_FROM_ORIGIN: typing.Dict[bytes, str] = {
    b'COMPANY': 'COMP',
    b'WELL-NAME': 'WELL',
    b'FIELD-NAME': 'FLD ',
    b'CREATION-TIME': 'DATE',
    b'PRODUCER-NAME': 'SRVC',
}


def extract_well_information_from_origin(logical_file: LogicalFile.LogicalFile) -> typing.Dict[str, UnitValueDescription]:
    """Extracts partial well information from the ORIGIN record. Example::

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
    las_map: typing.Dict[str, UnitValueDescription] = {}
    # print('TRACE: ORIGIN', logical_file.origin_logical_record.str_long())
    defining_origin: EFLR.Object = logical_file.defining_origin
    for attr in WELL_INFORMATION_FROM_ORIGIN:
        units = defining_origin[attr].units.decode('ascii')
        value = stringify.stringify_object_by_type(defining_origin[attr].value).strip()
        descr = ''
        # NOTE: Overwriting is possible here.
        las_map[WELL_INFORMATION_FROM_ORIGIN[attr]] = UnitValueDescription(units, value, descr)
    return las_map


def write_well_information_to_las(
        logical_file: LogicalFile.LogicalFile,
        frame_array: LogPass.FrameArray,
        ostream: typing.TextIO,
    ) -> None:
    """Writes the well information section.

    Reference: [LAS2.0 Las2_Update_Feb2017.pdf Section 5.4 ~W (Well Information)]
    """
    # Tuple of (units, value, description)
    las_map: typing.Dict[str, UnitValueDescription] = extract_well_information_from_origin(logical_file)
    # Add the start/stop/step data
    x_units: str = frame_array.x_axis.units.decode('ascii')
    iflr_data: typing.List[LogicalFile.IFLRData] = logical_file.iflr_position_map[frame_array.ident]
    if len(iflr_data):
        x_strt: float = iflr_data[0].x_axis
        x_stop: float = iflr_data[-1].x_axis
        las_map['STRT'] = UnitValueDescription(x_units, stringify.stringify_object_by_type(x_strt), 'Start depth')
        las_map['STOP'] = UnitValueDescription(
            x_units, stringify.stringify_object_by_type(x_stop), f'Stop depth, frames: {len(iflr_data):,d}'
        )
    else:
        las_map['STRT'] = UnitValueDescription(x_units, 'N/A', 'Start depth')
        las_map['STOP'] = UnitValueDescription(x_units, 'N/A', 'Stop depth')
    if len(iflr_data) > 1:
        x_step: float = (iflr_data[-1].x_axis - iflr_data[0].x_axis) / (len(iflr_data) - 1)
        las_map['STEP'] = UnitValueDescription(x_units, stringify.stringify_object_by_type(x_step), 'Step (average)')
    else:
        las_map['STEP'] = UnitValueDescription(x_units, 'N/A', 'Step (average)')
    eflr: EFLR.ExplicitlyFormattedLogicalRecord
    for _lrsh_position, eflr in logical_file.eflrs:
        # print('TRACE: write_well_information_to_las():', eflr.set.type)
        if eflr.set.type in DLIS_TO_WELL_INFORMATION_LAS_EFLR_MAPPING:
            bytes_index_map: typing.Dict[bytes, int] = EFLR.reduced_object_map(eflr)
            # print('TRACE:', eflr.str_long())
            # pprint.pprint(bytes_index_map)
            for row_key in DLIS_TO_WELL_INFORMATION_LAS_EFLR_MAPPING[eflr.set.type]:
                if row_key in bytes_index_map:
                    obj = eflr[bytes_index_map[row_key]]
                    # ORIGIN is only key/value so does not have LONG-NAME
                    # PARAMETER does have LONG-
                    units = obj[b'VALUES'].units.decode('ascii')
                    value = stringify.stringify_object_by_type(obj[b'VALUES'].value).strip()
                    descr = stringify.stringify_object_by_type(obj[b'LONG-NAME'].value).strip()
                    # NOTE: Overwriting is possible here.
                    las_map[row_key.decode('ascii')] = UnitValueDescription(units, value, descr)
    # pprint.pprint(las_map)
    table = [
        ['#MNEM.UNIT', 'DATA', 'DESCRIPTION',],
        ['#----.----', '----', '-----------',],
    ]
    for k in WELL_INFORMATION_KEYS:
        if k in las_map:
            row = [f'{k:4}.{las_map[k][0]:4}', f'{las_map[k][1]}', f': {las_map[k][2]}',]
        else:
            row = [f'{k:4}.{"":4}', '', ':']
        table.append(row)
    rows = data_table.format_table(table, pad='  ', left_flush=True)
    ostream.write('~Well Information Section\n')
    for row in rows:
        ostream.write(row)
        ostream.write('\n')


def write_parameter_section_to_las(
        logical_file: LogicalFile.LogicalFile,
        ostream: typing.TextIO,
    ) -> None:
    las_mnem_map: typing.Dict[str, UnitValueDescription] = collections.OrderedDict()
    for position_eflr in logical_file.eflrs:
        if position_eflr.eflr.set.type == b'PARAMETER':
            # print('TRACE:', position_eflr.eflr.str_long())
            for obj in position_eflr.eflr.objects:
                units = obj[b'VALUES'].units.decode('ascii')
                value = stringify.stringify_object_by_type(obj[b'VALUES'].value).strip()
                descr = stringify.stringify_object_by_type(obj[b'LONG-NAME'].value).strip()
                # NOTE: Overwriting is possible here.
                las_mnem_map[obj.name.I.decode('ascii')] = UnitValueDescription(units, value, descr)
    table = [
        ['#MNEM.UNIT', 'Value', 'Description'],
        ['#---------', '-----', '-----------'],
    ]
    # pprint.pprint(las_mnem_map)
    for k in las_mnem_map:
        table.append(
            [f'{k:<4}.{las_mnem_map[k].unit:<4}', las_mnem_map[k].value, f': {las_mnem_map[k].description}']
        )
    rows = data_table.format_table(table, pad='  ', left_flush=True)
    ostream.write('~Parameter Information Section\n')
    for row in rows:
        ostream.write(row)
        ostream.write('\n')


def las_file_name(path_out: str, logicial_file_index: int, frame_array_ident: bytes) -> str:
    """Returns the output file name."""
    file_name = os.path.splitext(os.path.basename(path_out))[0]
    file_path_out = os.path.join(
        os.path.dirname(path_out),
        file_name + f'_{logicial_file_index}_{frame_array_ident.decode("ascii")}' + '.las'
    )
    return file_path_out


ARRAY_REDUCTIONS = {'first', 'mean', 'median', 'min', 'max'}


def array_reduce(array: np.ndarray, method: str) -> typing.Union[float, int]:
    if method not in ARRAY_REDUCTIONS:
        raise ValueError(f'{method} is not in {ARRAY_REDUCTIONS}')
    if method == 'first':
        return array.flatten()[0]
    return getattr(array, method)()


def write_curve_section_to_las(
        frame_array: LogPass.FrameArray,
        ostream: typing.TextIO,
    ) -> None:
    ostream.write('~Curve Information Section\n')
    table = [
        ['#MNEM.UNIT', 'Curve Description'],
        ['#---------', '-----------------'],
    ]
    for c, channel in enumerate(frame_array.channels):
        desc = ' '.join([
            f': {channel.long_name.decode("ascii")}',
            f'Rep Code: {RepCode.REP_CODE_INT_TO_STR[channel.rep_code]}',
            f'Dimensions: {channel.dimensions}'
        ])
        table.append([f'{channel.ident.I.decode("ascii"):<4}.{channel.units.decode("ascii"):<4}', desc])
    rows = data_table.format_table(table, pad='  ', left_flush=True)
    for row in rows:
        ostream.write(row)
        ostream.write('\n')


def write_array_section_to_las(
        rp66v1_file: File.FileRead,
        logical_file_sequence: LogicalFile.LogicalIndex,
        logical_file: LogicalFile.LogicalFile,
        frame_array: LogPass.FrameArray,
        array_reduction: str,
        ostream: typing.TextIO,
    ) -> None:
    assert array_reduction in ARRAY_REDUCTIONS
    ostream.write('~A')
    for c, channel in enumerate(frame_array.channels):
        if c == 0:
            ostream.write(f'{channel.ident.I.decode("ascii"):>14}')
        else:
            ostream.write(' ')
            ostream.write(f'{channel.ident.I.decode("ascii"):>16}')
    ostream.write('\n')
    iflrs = logical_file.iflr_position_map[frame_array.ident]
    num_frames = len(iflrs)
    num_values = sum(c.count for c in frame_array.channels)
    logger.info(
        f'Writing array section with {num_frames:,d} frames'
        f', {len(frame_array):,d} channels'
        f' and {num_values:,d} values per frame'
        f', total: {num_frames * num_values:,d} input values.'
    )
    # TODO: Could init_arrays(1), read one IFLR, write it out and repeat.
    frame_array.init_arrays(num_frames)
    for f, (iflr_frame_number, lrsh_position, x_axis) in enumerate(iflrs):
        # TODO: raise
        assert f + 1 == iflr_frame_number
        vr_position = logical_file_sequence.visible_record_positions.visible_record_prior(lrsh_position)
        fld: File.FileLogicalData = rp66v1_file.get_file_logical_data(vr_position, lrsh_position)
        iflr = IFLR.IndirectlyFormattedLogicalRecord(fld.lr_type, fld.logical_data)
        frame_array.read(iflr.logical_data, f)
    for f in range(num_frames):
        for c, channel in enumerate(frame_array.channels):
            if c:
                ostream.write(' ')
            value = array_reduce(channel.array[f], array_reduction)
            if RepCode.REP_CODE_CATEGORY_MAP[channel.rep_code] == RepCode.NumericCategory.INTEGER:
                ostream.write(f'{value:16.0f}')
            elif RepCode.REP_CODE_CATEGORY_MAP[channel.rep_code] == RepCode.NumericCategory.FLOAT:
                ostream.write(f'{value:16.3f}')
            else:
                ostream.write(str(value))
        ostream.write('\n')
    # Free up numpy memory
    frame_array.init_arrays(1)


def write_logical_sequence_to_las(
        rp66v1_file: File.FileRead,
        logical_file_sequence: LogicalFile.LogicalIndex,
        array_reduction: str,
        path_out: str,
        ) -> typing.List[str]:
    ret = []
    for lf, logical_file in enumerate(logical_file_sequence.logical_files):
        # Now the LogPass
        if logical_file.has_log_pass:
            for frame_array in logical_file.log_pass.frame_arrays:
                file_path_out = las_file_name(path_out, lf, frame_array.ident.I)
                os.makedirs(os.path.dirname(file_path_out), exist_ok=True)
                logger.info(f'Starting LAS output file {file_path_out}')
                with open(file_path_out, 'w') as ostream:
                    # Write each section
                    _write_las_header(
                        os.path.basename(logical_file_sequence.path),
                        logical_file, lf, frame_array.ident.I.decode('ascii'), ostream
                    )
                    write_well_information_to_las(logical_file, frame_array, ostream)
                    write_curve_section_to_las(frame_array, ostream)
                    write_parameter_section_to_las(logical_file, ostream)
                    write_array_section_to_las(
                        rp66v1_file, logical_file_sequence, logical_file, frame_array, array_reduction, ostream
                    )
                    ret.append(file_path_out)
        else:
            file_path_out = las_file_name(path_out, lf, b'')
            os.makedirs(os.path.dirname(file_path_out), exist_ok=True)
            with open(file_path_out, 'w') as ostream:
                _write_las_header(
                    os.path.basename(logical_file_sequence.path),
                    logical_file, lf, '', ostream
                )
                write_well_information_to_las(logical_file, ostream)
                write_parameter_section_to_las(logical_file, ostream)
                ret.append(file_path_out)
    return ret


def single_rp66v1_file_to_las(path_in: str, array_reduction: str, path_out: str = '') -> LASWriteResult:
    # logging.info(f'index_a_single_file(): "{path_in}" to "{path_out}"')
    bin_file_type = binary_file_type_from_path(path_in)
    if bin_file_type == 'RP66V1':
        logger.info(f'Converting RP66V1 {path_in} to LAS {os.path.splitext(path_out)[0]}*')
        try:
            with open(path_in, 'rb') as fobj:
                t_start = time.perf_counter()
                # index = RP66V1IndexXMLWrite(fobj, path_in)
                rp66v1_file = File.FileRead(fobj)
                logical_file_sequence = LogicalFile.LogicalIndex(rp66v1_file, path_in)
                las_files_written = write_logical_sequence_to_las(
                    rp66v1_file, logical_file_sequence, array_reduction, path_out
                )
                output_size = sum(os.path.getsize(f) for f in las_files_written)
                result = LASWriteResult(
                    os.path.getsize(path_in),
                    output_size,
                    len(las_files_written),
                    time.perf_counter() - t_start,
                    False,
                    False,
                )
                logger.info(f'{len(las_files_written)} LAS file written with total size: {output_size:,d} bytes')
                return result
        except ExceptionTotalDepthRP66V1:
            logger.exception(f'Failed to index with ExceptionTotalDepthRP66V1: {path_in}')
            return LASWriteResult(os.path.getsize(path_in), 0, 0, 0.0, True, False)
        except Exception:
            logger.exception(f'Failed to index with Exception: {path_in}')
            return LASWriteResult(os.path.getsize(path_in), 0, 0, 0.0, True, False)
    logger.debug(f'Ignoring file type "{bin_file_type}" at {path_in}')
    return LASWriteResult(0, 0, 0, 0.0, False, True)


def convert_rp66v1_dir_or_file_to_las(path_in: str, path_out: str, recurse: bool, array_reduction: str) -> typing.Dict[str, LASWriteResult]:
    logging.info(f'index_dir_or_file(): "{path_in}" to "{path_out}" recurse: {recurse}')
    ret = {}
    try:
        if os.path.isdir(path_in):
            for file_in_out in dirWalk(path_in, path_out, theFnMatch='', recursive=recurse, bigFirst=False):
                # print(file_in_out)
                ret[file_in_out.filePathIn] = single_rp66v1_file_to_las(
                    file_in_out.filePathIn, array_reduction, file_in_out.filePathOut
                )
        else:
            ret[path_in] = single_rp66v1_file_to_las(path_in, array_reduction, path_out)
    except KeyboardInterrupt:
        logger.critical('Keyboard interrupt, last file is probably incomplete or corrupt.')
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
set ylabel "XML Index Rate (ms/Mb), XML Compression Ratio"
# set yrange [1:1e5]
# set ytics 20
# set mytics 2
# set ytics 8,35,3

# set logscale y2
# set y2label "Ratio index size / original size"
# set y2range [1e-4:10]
# set y2tics

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

plot "{name}.dat" using 1:($3*1000/($1/(1024*1024))) axes x1y1 title "XML Index Rate (ms/Mb)" lt 1 w points,\
	rate(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", a, b) lt 1 lw 2, \
    "{name}.dat" using 1:($1/$2) axes x1y1 title "Original Size / XML Index size" lt 3 w points, \
    compression_ratio(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", e, f) axes x1y1 lt 3 lw 2

# Plot size ratio:
#    "{name}.dat" using 1:($2/$1) axes x1y2 title "Index size ratio" lt 3 w points, \
#     size_ratio(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", c, d) axes x1y2 lt 3 lw 2

reset
"""


def plot_gnuplot(data: typing.Dict[str, LASWriteResult], gnuplot_dir: str) -> None:
    if len(data) < 2:
        raise ValueError(f'Can not plot data with only {len(data)} points.')
    # First row is header row, create it then comment out the first item.
    table = [
        list(LASWriteResult._fields) + ['Path']
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
Scans a RP66V1 file and dumps data."""
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
    parser.add_argument(
        '--array_reduction', type=str,
        help='Method to reduce multidimensional channel data to a single value. [default: %(default)s]',
        default='mean',
        choices=list(sorted(ARRAY_REDUCTIONS)),
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
    result: typing.Dict[str, LASWriteResult] = convert_rp66v1_dir_or_file_to_las(
        args.path_in,
        args.path_out,
        args.recurse,
        args.array_reduction,
    )
    clk_exec = time.perf_counter() - clk_start
    size_index = size_input = 0
    files_processed = 0
    table = [
        ['Input', 'Output', 'LAS Count', 'Time', 'Ratio', 'ms/Mb', 'Exception', 'Path']
    ]
    for path in sorted(result.keys()):
        las_result = result[path]
        # print('TRACE: las_result', las_result)
        if las_result.size_input > 0:
            ms_mb = las_result.time * 1000 / (las_result.size_input / 1024 ** 2)
            ratio = las_result.size_output / las_result.size_input
            # out = []
            # out.append(f'{las_result.size_input:16,d}')
            # out.append(f'{las_result.size_output:16,d}')
            # out.append(f'{las_result.las_count:4,d}')
            # out.append(f'{las_result.time:8.3f}')
            # out.append(f'{ratio:8.1%}')
            # out.append(f'{ms_mb:8.1f}')
            # out.append(f'{str(las_result.exception):5}')
            # out.append(f'"{path}"')
            out = [
                f'{las_result.size_input:,d}',
                f'{las_result.size_output:,d}',
                f'{las_result.las_count:,d}',
                f'{las_result.time:.3f}',
                f'{ratio:.1%}',
                f'{ms_mb:.1f}',
                f'{str(las_result.exception)}',
                f'"{path}"',
            ]
            table.append(out)
            # print(' '.join(out))
            size_input += result[path].size_input
            size_index += result[path].size_output
            files_processed += 1
    for row in data_table.format_table(table, pad=' ', heading_underline='-'):
        print(row)
    try:
        if args.gnuplot:
            plot_gnuplot(result, args.gnuplot)
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
