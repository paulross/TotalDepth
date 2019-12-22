"""
Converts RP66V1 files to LAS files.

References:

* General: http://www.cwls.org/las/
* LAS Version 2: http://www.cwls.org/wp-content/uploads/2017/02/Las2_Update_Feb2017.pdf

Example reference to the LAS documentation in this source code::

    [LAS2.0 Las2_Update_Feb2017.pdf Section 5.3 ~V (Version Information)]

"""
import collections
import datetime
import logging
import multiprocessing
import os
import sys
import time
import typing

import numpy as np

import TotalDepth.RP66V1.core.XAxis
from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import File
from TotalDepth.RP66V1.core import LogPass
from TotalDepth.RP66V1.core import LogicalFile
from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core import XAxis
from TotalDepth.RP66V1.core import stringify
from TotalDepth.RP66V1.core.LogicalRecord import EFLR
from TotalDepth.RP66V1.core.LogicalRecord import IFLR
from TotalDepth.common import Slice, cmn_cmd_opts, process
from TotalDepth.common import data_table
from TotalDepth.util.DirWalk import dirWalk
from TotalDepth.util import bin_file_type, DirWalk
from TotalDepth.util import gnuplot

__author__  = 'Paul Ross'
__date__    = '2019-04-10'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


LAS_PRODUCER_VERSION = '0.1.1'


logger = logging.getLogger(__file__)


class LASWriteResult(typing.NamedTuple):
    path_input: str
    size_input: int
    size_output: int
    las_count: int
    time: float
    exception: bool
    ignored: bool


# TODO: Add microseconds
LAS_DATETIME_FORMAT_UTC = '%Y-%m-%d %H:%M:%S.%f UTC'
LAS_DATE_FORMAT_TEXT = 'YYYY-mm-dd HH:MM:SS.us UTC'


def _write_las_header(input_file: str,
                      logical_file: LogicalFile.LogicalFile,
                      logical_file_number: int,
                      frame_array_ident: str,
                      ostream: typing.TextIO) -> None:
    """Writes the LAS opening such as:

    ~Version Information Section
    VERS.           2.0                           : CWLS Log ASCII Standard - VERSION 2.0
    WRAP.           NO                            : One Line per depth step
    PROD.           TotalDepth                    : LAS Producer
    PROG.           TotalDepth.RP66V1.ToLAS 0.1.1 : LAS Program name and version
    CREA.           2012-11-14 10:50              : LAS Creation date [YYYY-MMM-DD hh:mm]
    DLIS_CREA.      2012-11-10 22:06              : DLIS Creation date and time [YYYY-MMM-DD hh:mm]
    SOURCE.         SOME-FILE-NAME.dlis           : DLIS File Name
    FILE-ID.        SOME-FILE-ID                  : File Identification from the FILE-HEADER Logical Record
    LOGICAL-FILE.   3                             : Logical File number in the DLIS file
    FRAME-ARRAY.    60B                           : Identity of the Frame Array in the Logical File

    Reference: [LAS2.0 Las2_Update_Feb2017.pdf Section 5.3 ~V (Version Information)]
    """
    now = datetime.datetime.utcnow()
    date_time = logical_file.defining_origin[b'CREATION-TIME'].value[0]
    dt = date_time.as_datetime()
    fhlr: EFLR.ExplicitlyFormattedLogicalRecord = logical_file.file_header_logical_record
    file_id = fhlr.objects[0][b'ID'].value[0].decode('ascii').strip()
    table: typing.List[typing.List[str]] = [
        ['VERS.', '2.0', ': CWLS Log ASCII Standard - VERSION 2.0'],
        ['WRAP.', 'NO', ': One Line per depth step'],
        ['PROD.', 'TotalDepth', ': LAS Producer'],
        ['PROG.', f'TotalDepth.RP66V1.ToLAS {LAS_PRODUCER_VERSION}', ': LAS Program name and version'],
        ['CREA.', f'{now.strftime(LAS_DATETIME_FORMAT_UTC)}', f': LAS Creation date [{LAS_DATE_FORMAT_TEXT}]'],
        [
            f'DLIS_CREA.',
            f'{dt.strftime(LAS_DATETIME_FORMAT_UTC)}', f': DLIS Creation date and time [{LAS_DATE_FORMAT_TEXT}]'
        ],
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


#: Mapping of DLIS ``EFLR`` Type and Object Name to ``LAS WELL INFORMATION`` section and Mnemonic.
#: The Object ``LONG-NAME`` is used as the LAS description.
#: We prefer to take data from the ORIGIN ``EFLR`` as it is more clearly specified ``[RP66V1 5.2 Origin Logical Record (OLR)]``
#: whereas ``PARAMETER EFLR`` s are fairly free form.
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


def extract_well_information_from_origin(logical_file: LogicalFile.LogicalFile) \
        -> typing.Dict[str, UnitValueDescription]:
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
        frame_array: typing.Union[LogPass.FrameArray, None],
        ostream: typing.TextIO,
    ) -> None:
    """Writes the well information section.

    Reference: ``[LAS2.0 Las2_Update_Feb2017.pdf Section 5.4 ~W (Well Information)]``
    """
    # Tuple of (units, value, description)
    las_map: typing.Dict[str, UnitValueDescription] = extract_well_information_from_origin(logical_file)
    if frame_array is not None:
        # Add the start/stop/step data
        x_units: str = frame_array.x_axis.units.decode('ascii')
        iflr_data: typing.List[TotalDepth.RP66V1.core.XAxis.IFLRReference] = logical_file.iflr_position_map[frame_array.ident]
        assert len(iflr_data)
        x_strt: float = iflr_data[0].x_axis
        x_stop: float = iflr_data[-1].x_axis
        las_map['STRT'] = UnitValueDescription(x_units, stringify.stringify_object_by_type(x_strt), 'Start X')
        # FIXME: Compute correct STOP and STEP with frame slicing.
        las_map['STOP'] = UnitValueDescription(
            x_units, stringify.stringify_object_by_type(x_stop), f'Stop X, frames: {len(iflr_data):,d}'
        )
        x_step: float = (iflr_data[-1].x_axis - iflr_data[0].x_axis) / (len(iflr_data) - 1)
        las_map['STEP'] = UnitValueDescription(x_units, stringify.stringify_object_by_type(x_step), 'Step (average)')
    else:
        las_map['STRT'] = UnitValueDescription('N/A', 'N/A', 'Start X')
        las_map['STOP'] = UnitValueDescription('N/A', 'N/A', 'Stop X')
        las_map['STEP'] = UnitValueDescription('N/A', 'N/A', 'Step (average)')
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


#: Possible methods to reduce an array to a single value.
ARRAY_REDUCTIONS = {'first', 'mean', 'median', 'min', 'max'}


def array_reduce(array: np.ndarray, method: str) -> typing.Union[float, int]:
    """Take a numpy array and apply a method to it to get a single value."""
    if method not in ARRAY_REDUCTIONS:
        raise ValueError(f'{method} is not in {ARRAY_REDUCTIONS}')
    if method == 'first':
        return array.flatten()[0]
    return getattr(np, method)(array)


def write_curve_section_to_las(
        frame_array: LogPass.FrameArray,
        channels: typing.Set[str],
        ostream: typing.TextIO,
    ) -> None:
    """Write the ``~Curve Information Section`` to the LAS file."""
    ostream.write('~Curve Information Section\n')
    table = [
        ['#MNEM.UNIT', 'Curve Description'],
        ['#---------', '-----------------'],
    ]
    for c, channel in enumerate(frame_array.channels):
        if len(channels) == 0 or c == 0 or channel.ident.I.decode("ascii") in channels:
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
        logical_file: LogicalFile.LogicalFile,
        frame_array: LogPass.FrameArray,
        array_reduction: str,
        frame_slice: Slice.Slice,
        channels: typing.Set[str],
        ostream: typing.TextIO,
    ) -> None:
    """Write the ``~Array Section`` to the LAS file."""
    assert array_reduction in ARRAY_REDUCTIONS
    # TODO: Could optimise memory by reading one frame at a time
    num_available_frames = logical_file.num_frames(frame_array)
    if len(channels):
        array_channels = [c.ident for c in frame_array.channels if c.ident.I.decode("ascii") in channels]
        num_writable_frames = logical_file.populate_frame_array(frame_array, frame_slice, array_channels)
    else:
        num_writable_frames = logical_file.populate_frame_array(frame_array, frame_slice)
    # Write information about how the frames and channels were processed
    ostream.write(f'# Array processing information:\n')
    ostream.write(f'# Frame Array: ID: {frame_array.ident} description: {frame_array.description}\n')
    if len(channels):
        original_channels = ','.join(channel.ident.I.decode("ascii") for channel in frame_array.channels)
        ostream.write(f'# Original channels in Frame Array [{len(frame_array.channels):4d}]: {original_channels}\n')
        ostream.write(f'# Requested Channels this LAS file [{len(channels):4d}]: {",".join(channels)}\n')
    else:
        ostream.write(f'# All [{len(frame_array.channels)}] original channels reproduced here.\n')
    ostream.write(f'# Where a channel has multiple values the reduction method is by "{array_reduction}" value.\n')
    ostream.write(f'# Number of original frames: {num_available_frames}\n')
    ostream.write(
        f'# Requested frame slicing: {frame_slice.long_str(num_available_frames)}'
        f', total number of frames presented here: {frame_slice.count(num_available_frames)}\n'
    )
    ostream.write('~A')
    for c, channel in enumerate(frame_array.channels):
        if len(channels) == 0 or c == 0 or channel.ident.I.decode("ascii") in channels:
            if c == 0:
                ostream.write(f'{channel.ident.I.decode("ascii"):>14}')
            else:
                ostream.write(' ')
                ostream.write(f'{channel.ident.I.decode("ascii"):>16}')
    ostream.write('\n')
    num_values = sum(c.count for c in frame_array.channels)
    logger.info(
        f'Writing array section with {num_writable_frames:,d} frames'
        f', {len(frame_array):,d} channels'
        f' and {num_values:,d} values per frame'
        f', total: {num_writable_frames * num_values:,d} input values.'
    )
    for frame_number in frame_slice.gen_indices(num_writable_frames):
        for channel in frame_array.channels:
            if len(channel.array):
                value = array_reduce(channel.array[frame_number], array_reduction)
                if RepCode.REP_CODE_CATEGORY_MAP[channel.rep_code] == RepCode.NumericCategory.INTEGER:
                    ostream.write(f'{value:16.0f}')
                elif RepCode.REP_CODE_CATEGORY_MAP[channel.rep_code] == RepCode.NumericCategory.FLOAT:
                    ostream.write(f'{value:16.3f}')
                else:
                    ostream.write(str(value))
        ostream.write('\n')
    # Garbage collect
    frame_array.init_arrays(1)


def write_logical_sequence_to_las(
        logical_index: LogicalFile.LogicalIndex,
        array_reduction: str,
        path_out: str,
        frame_slice: Slice.Slice,
        channels: typing.Set[str],
        ) -> typing.List[str]:
    assert array_reduction in ARRAY_REDUCTIONS
    ret = []
    for lf, logical_file in enumerate(logical_index.logical_files):
        # Now the LogPass
        if logical_file.has_log_pass:
            for frame_array in logical_file.log_pass.frame_arrays:
                file_path_out = las_file_name(path_out, lf, frame_array.ident.I)
                os.makedirs(os.path.dirname(file_path_out), exist_ok=True)
                logger.info(f'Starting LAS output file {file_path_out}')
                with open(file_path_out, 'w') as ostream:
                    # Write each section
                    _write_las_header(
                        os.path.basename(logical_index.id),
                        logical_file, lf, frame_array.ident.I.decode('ascii'), ostream
                    )
                    write_well_information_to_las(logical_file, frame_array, ostream)
                    write_curve_section_to_las(frame_array, channels, ostream)
                    write_parameter_section_to_las(logical_file, ostream)
                    write_array_section_to_las(
                        logical_file, frame_array, array_reduction, frame_slice,
                        channels, ostream
                    )
                    ret.append(file_path_out)
        else:
            file_path_out = las_file_name(path_out, lf, b'')
            os.makedirs(os.path.dirname(file_path_out), exist_ok=True)
            with open(file_path_out, 'w') as ostream:
                _write_las_header(
                    os.path.basename(logical_index.id),
                    logical_file, lf, '', ostream
                )
                write_well_information_to_las(logical_file, None, ostream)
                write_parameter_section_to_las(logical_file, ostream)
                ret.append(file_path_out)
    return ret


def single_rp66v1_file_to_las(
        path_in: str,
        array_reduction: str,
        path_out: str,
        frame_slice: Slice.Slice,
        channels: typing.Set[str],
) -> LASWriteResult:
    # logging.info(f'index_a_single_file(): "{path_in}" to "{path_out}"')
    assert array_reduction in ARRAY_REDUCTIONS
    binary_file_type = bin_file_type.binary_file_type_from_path(path_in)
    if binary_file_type == 'RP66V1':
        logger.info(f'Converting RP66V1 {path_in} to LAS {os.path.splitext(path_out)[0]}*')
        try:
            t_start = time.perf_counter()
            with LogicalFile.LogicalIndex(path_in) as logical_index:
                las_files_written = write_logical_sequence_to_las(
                    logical_index, array_reduction, path_out, frame_slice, channels,
                )
                output_size = sum(os.path.getsize(f) for f in las_files_written)
                result = LASWriteResult(
                    path_in,
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
            return LASWriteResult(path_in, os.path.getsize(path_in), 0, 0, 0.0, True, False)
        except Exception:  # pragma: no cover
            logger.exception(f'Failed to index with Exception: {path_in}')
            return LASWriteResult(path_in, os.path.getsize(path_in), 0, 0, 0.0, True, False)
    logger.debug(f'Ignoring file type "{binary_file_type}" at {path_in}')
    return LASWriteResult(path_in, 0, 0, 0, 0.0, False, True)


def convert_rp66v1_dir_or_file_to_las_multiprocessing(
        dir_in: str,
        dir_out: str,
        recurse: bool,
        array_reduction: str,
        frame_slice: Slice.Slice,
        channels: typing.Set[str],
        jobs: int
) -> typing.Dict[str, LASWriteResult]:
    """Multiprocessing code to LAS.
    Returns a dict of {path_in : LASWriteResult, ...}"""
    assert os.path.isdir(dir_in)
    if jobs < 1:
        jobs = multiprocessing.cpu_count()
    logging.info('scan_dir_multiprocessing(): Setting multi-processing jobs to %d' % jobs)
    pool = multiprocessing.Pool(processes=jobs)
    tasks = [
        (t.filePathIn, array_reduction, t.filePathOut, frame_slice, channels) for t in DirWalk.dirWalk(
            dir_in, dir_out, theFnMatch='', recursive=recurse, bigFirst=True
        )
    ]
    # print('tasks:')
    # pprint.pprint(tasks, width=200)
    # return {}
    results = [
        r.get() for r in [
            pool.apply_async(single_rp66v1_file_to_las, t) for t in tasks
        ]
    ]
    return {r.path_input: r for r in results}


def convert_rp66v1_dir_or_file_to_las(
        path_in: str,
        path_out: str,
        recurse: bool,
        array_reduction: str,
        frame_slice: Slice.Slice,
        channels: typing.Set[str],
) -> typing.Dict[str, LASWriteResult]:
    logging.info(f'index_dir_or_file(): "{path_in}" to "{path_out}" recurse: {recurse}')
    ret = {}
    try:
        if os.path.isdir(path_in):
            for file_in_out in dirWalk(path_in, path_out, theFnMatch='', recursive=recurse, bigFirst=False):
                ret[file_in_out.filePathIn] = single_rp66v1_file_to_las(
                    file_in_out.filePathIn, array_reduction, file_in_out.filePathOut, frame_slice, channels,
                )
        else:
            ret[path_in] = single_rp66v1_file_to_las(path_in, array_reduction, path_out, frame_slice, channels)
    except KeyboardInterrupt:  # pragma: no cover
        logger.critical('Keyboard interrupt, last file is probably incomplete or corrupt.')
    return ret


def dump_frames_and_or_channels_single_rp66v1_file(path_in: str, frame_slices, channels) -> None:
    binary_file_type = bin_file_type.binary_file_type_from_path(path_in)
    if binary_file_type == 'RP66V1':
        logger.info(f'Reading RP66V1 {path_in}')
        try:
            with LogicalFile.LogicalIndex(path_in) as logical_index:
                for l, logical_file in enumerate(logical_index.logical_files):
                    print(f'Logical file [{l:04d}]: {logical_file}')
                    # print(f'Logical file: {logical_file.file_header_logical_record.set.type}')
                    if logical_file.has_log_pass:
                        for frame_array in logical_file.log_pass.frame_arrays:
                            print(f'  Frame Array: {frame_array.ident.I}')
                            if channels:
                                channel_text = b','.join(c.ident.I for c in frame_array.channels)
                                print(f'  Channels: {channel_text}')
                            if frame_slices:
                                print(f'  X axis: {frame_array.x_axis}')
                                iflr_refs = logical_file.iflr_position_map[frame_array.ident]
                                # print(f'TRACE: Frames: {len(iflr_refs)} from {iflr_refs[0]} to {iflr_refs[-1]}')
                                x_spacing = (iflr_refs[-1].x_axis - iflr_refs[0].x_axis) / (len(iflr_refs)  -1)
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
    else:
        logger.error(f'Path {path_in} is not a RP66V1 file.')


def dump_frames_and_or_channels(path_in: str, recurse: bool, frame_slice: str, channels: str) -> None:
    assert frame_slice == '?' or channels == '?'
    if os.path.isdir(path_in):
        for file_in_out in dirWalk(path_in, '', theFnMatch='', recursive=recurse, bigFirst=False):
            dump_frames_and_or_channels_single_rp66v1_file(file_in_out.filePathIn, frame_slice == '?', channels == '?')
    else:
        dump_frames_and_or_channels_single_rp66v1_file(path_in, frame_slice == '?', channels == '?')


GNUPLOT_PLT = """set logscale x
set grid
set title "Converting RP66V1 Files to LAS with TotalDepth.RP66V1.ToLAS.main"
set xlabel "RP66V1 File Size (bytes)"
# set mxtics 5
# set xrange [0:3000]
# set xtics
# set format x ""

set logscale y
set ylabel "Conversion Rate (ms/Mb), Ratio RP66V1 / LAS size"
# set yrange [1:1e5]
# set ytics 20
# set mytics 2
# set ytics 8,35,3

# set logscale y2
# set y2label "Ratio LAS size / original RP66V1 size"
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

plot "{name}.dat" using 1:($3*1000/($1/(1024*1024))) axes x1y1 title "LAS Conversion Rate (ms/Mb)" lt 1 w points,\
	rate(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", a, b) lt 1 lw 2, \
    "{name}.dat" using 1:($1/$2) axes x1y1 title "RP66V1 / LAS size" lt 3 w points, \
    compression_ratio(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", e, f) axes x1y1 lt 3 lw 2

# Plot size ratio:
#    "{name}.dat" using 1:($2/$1) axes x1y2 title "Index size ratio" lt 3 w points, \
#     size_ratio(x) title sprintf("Fit: 10**(%+.3g %+.3g * log10(x))", c, d) axes x1y2 lt 3 lw 2

reset
"""


def plot_gnuplot(data: typing.Dict[str, LASWriteResult], gnuplot_dir: str) -> None:
    if len(data) < 2:  # pragma: no cover
        raise ValueError(f'Can not plot data with only {len(data)} points.')
    # First row is header row, create it then comment out the first item.
    table = [
        list(LASWriteResult._fields[1:]) + ['Path']
    ]
    table[0][0] = f'# {table[0][0]}'
    for k in sorted(data.keys()):
        if data[k].size_input > 0 and not data[k].exception:
            table.append(list(data[k][1:]) + [k])
    name = 'IndexFile'
    return_code = gnuplot.invoke_gnuplot(gnuplot_dir, name, table, GNUPLOT_PLT.format(name=name))
    if return_code:  # pragma: no cover
        raise IOError(f'Can not plot gnuplot with return code {return_code}')
    return_code = gnuplot.write_test_file(gnuplot_dir, 'svg')
    if return_code:  # pragma: no cover
        raise IOError(f'Can not plot gnuplot with return code {return_code}')


def main() -> int:
    description = """usage: %(prog)s [options] file
Reads RP66V1 file(s) and writes them out as LAS files."""
    print('Cmd: %s' % ' '.join(sys.argv))

    parser = cmn_cmd_opts.path_in_out(
        description, prog='TotalDepth.RP66V1.ToLAS.main', version=__version__, epilog=__rights__
    )
    cmn_cmd_opts.add_log_level(parser, level=20)
    cmn_cmd_opts.add_multiprocessing(parser)
    Slice.add_frame_slice_to_argument_parser(parser)
    process.add_process_logger_to_argument_parser(parser)
    gnuplot.add_gnuplot_to_argument_parser(parser)
    parser.add_argument(
        '--array-reduction', type=str,
        help='Method to reduce multidimensional channel data to a single value. [default: %(default)s]',
        default='first',
        choices=list(sorted(ARRAY_REDUCTIONS)),
        )
    parser.add_argument(
        '--channels', type=str,
        help='Comma separated list of channels to write out (X axis is always included).'
             ' Use \'?\' to see what channels exist without writing anything. [default: %(default)s]',
        default='',
        )
    args = parser.parse_args()
    cmn_cmd_opts.set_log_level(args)
    # print('args:', args)
    # return 0
    # Your code here
    clk_start = time.perf_counter()
    ret_val = 0
    result: typing.Dict[str, LASWriteResult] = {}
    if args.frame_slice.strip() == '?' or args.channels.strip() == '?':
        dump_frames_and_or_channels(args.path_in, args.recurse, args.frame_slice.strip(), args.channels.strip())
    else:
        channel_set = set()
        for ch in args.channels.strip().split(','):
            if ch.strip() != '':
                channel_set.add(ch.strip())
        if cmn_cmd_opts.multiprocessing_requested(args) and os.path.isdir(args.path_in):
            result = convert_rp66v1_dir_or_file_to_las_multiprocessing(
                args.path_in,
                args.path_out,
                args.recurse,
                args.array_reduction,
                Slice.create_slice_or_sample(args.frame_slice),
                channel_set,
                args.jobs,
            )
        else:
            result = convert_rp66v1_dir_or_file_to_las(
                args.path_in,
                args.path_out,
                args.recurse,
                args.array_reduction,
                Slice.create_slice_or_sample(args.frame_slice),
                channel_set,
            )
    clk_exec = time.perf_counter() - clk_start
    # Report output
    if result:
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
                if las_result.exception:
                    ret_val = 1
        for row in data_table.format_table(table, pad=' ', heading_underline='-'):
            print(row)
        try:
            if args.gnuplot:
                plot_gnuplot(result, args.gnuplot)
        except Exception as err:  # pragma: no cover
            logger.exception(str(err))
            ret_val = 2
        print('Execution time = %8.3f (S)' % clk_exec)
        if size_input > 0:
            ms_mb = clk_exec * 1000 / (size_input/ 1024**2)
            ratio = size_index / size_input
        else:
            ms_mb = 0.0
            ratio = 0.0
        print(f'Out of  {len(result):,d} processed {files_processed:,d} files of total size {size_input:,d} input bytes')
        print(f'Wrote {size_index:,d} output bytes, ratio: {ratio:8.3%} at {ms_mb:.1f} ms/Mb')
    else:
        print(f'Execution time: {clk_exec:.3f} (s)')
    print('Bye, bye!')
    return ret_val


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
