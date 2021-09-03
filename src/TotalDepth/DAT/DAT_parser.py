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
DAT Files
---------

Parses DAT files. DAT is an informal specification (i.e. undefined) with loads of poor implementations.

Here described:

Section 1: Channel Declaration.
A set of lines of the form: A B C, whitespace separated, where A is an uppercase word, B is free text, C is a word.
There is no guarantee that channels declared here have any data in the subsequent sections.
Order of this section is ignored.

Section 2: Channel Header
A single line with space separated uppercase words.
All words must appear as channel declarations from section 1 but some declarations from section 1 may be missing.
The order of the words in the channel header is used to interpret the order of the subsequent values in section 3.

So deciding if we are in section 2 can be done with some (dubious?) heuristics:

    - List matches list of section 1. Seems sensible but does not work when channels are declared but not defined.
    - Some subset of the declared channels.
    - All uppercase?
    - Lots of words?
    - Starts with 'UTIM DATE TIME ...'

In this implementation we use the latter.

Section 3: Channel values
Space separated values. Mostly numeric but date/time conversion can be inferred from section 1.
The column order is defined by the order of the Channel Header.

Note many deficiencies here:

DATE Date ddmmyy but value 9Dec06, 09-Dec-06 etc.

TIME Time hhmmss but value 11-50-17

Example, <...> is  continuation:

UTIM Unix Time sec
DATE Date ddmmyy
TIME Time hhmmss
WAC Wits Activity Code unitless
BDIA Bit Diameter inch
<...>
NPEN n-Pentane ppm
EPEN Neo-Pentane ppm
UTIM DATE TIME WAC BDIA <...> NPEN EPEN
1165665017 09Dec06 11-50-17 0 8.50 <...> 0 0

Performance
-----------
There is no particular effort made here for high performance.
DAT files are small, typically <10Mb, so artful coding is not really required.

API
---
"""
import datetime
import logging
import re
import string
import sys
import time
import typing

import numpy as np

from TotalDepth import ExceptionTotalDepth
from TotalDepth.common import LogPass


logger = logging.getLogger(__file__)


class ExceptionDAT(ExceptionTotalDepth):
    """General exception for problems with a DAT object."""
    pass


class ExceptionDATRead(ExceptionDAT):
    """Exception for reading a DAT file."""
    pass


#: Matches 'UTIM Unix Time sec'
#: Also need to process: "UTIM	Unix	Time	sec"
RE_CHANNEL_DEFINITION = re.compile(r'^([A-Z0-9]+)\s(.+?)\s(\S+)$')
#: Matches 'UTIM    DATE    TIME ...'
RE_DATA_HEADER_DEFINITION = re.compile(r'^UTIM\s+DATE\s+TIME\s+.+$')


#: Matches '12Oct20' and '5Oct20'
RE_DATE_STYLE_A = re.compile(r'^(\d+)(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\d+)$')
#: Matches '12-Oct-20' and '5O-Oct-20'
RE_DATE_STYLE_B = re.compile(r'^(\d+)-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-(\d+)$')


#: Map of numpy dtype from the name/units.
NAME_UNITS_TYPE_MAP = {
    ('UTIM', 'sec'): np.object,
    ('DATE', 'ddmmyy'): np.object,
    ('TIME', 'hhmmss'): np.object,
}


def _numpy_dtype(name: str, units: str) -> np.dtype:
    if (name, units) in NAME_UNITS_TYPE_MAP:
        return NAME_UNITS_TYPE_MAP[(name, units)]
    return np.float64


def _unit_unix_time_to_datetime_datetime(value: str) -> datetime.datetime:
    """Converts UNIX time string to datetime.datetime."""
    try:
        int_val = int(value)
        struct_tm = time.gmtime(int_val)
        return datetime.datetime(*(struct_tm[:6]))
    except ValueError as err:
        # logger.exception('_unit_unix_time_to_datetime_datetime()')
        raise ExceptionDATRead(f'_unit_unix_time_to_datetime_datetime(): {err} on value "{value}"')


def _unit_ddmmyy_to_datetime_date(value: str) -> datetime.date:
    """Converts date string like "09Dec75" or "29-Sep-11" to datetime.date.
    The implementations are so poor that "1-Oct-11" is acceptable."""
    try:
        if '-' in value:
            # Examples: "29-Sep-11", "2-Sep-11"
            m = RE_DATE_STYLE_B.match(value)
        else:
            # Examples: "09Dec75", "9Dec75"
            m = RE_DATE_STYLE_A.match(value)
        if m is None:
            raise ExceptionDATRead(f'_unit_ddmmyy_to_datetime_date(): Can not grep value "{value}"')
        day = int(m.group(1))
        mon = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(m.group(2)) + 1
        yr = int(m.group(3))
        # Y2K correction.
        if yr > 50:
            yr += 1900
        else:
            yr += 2000
        return datetime.date(yr, mon, day)
    except ValueError as err:
        raise ExceptionDATRead(f'_unit_ddmmyy_to_datetime_date(): {err} on value "{value}"')


def _unit_hhmmyy_to_datetime_time(value: str) -> datetime.time:
    """Converts time string to datetime.time."""
    try:
        return datetime.datetime.strptime(value, '%H-%M-%S').time()
    except ValueError as err:
        raise ExceptionDATRead(f'_unit_hhmmyy_to_datetime_time(): {err} on value "{value}"')


NAME_VALUE_CONVERSION_MAP = {
    ('UTIM', 'sec'): _unit_unix_time_to_datetime_datetime,
    ('DATE', 'ddmmyy'): _unit_ddmmyy_to_datetime_date,
    ('TIME', 'hhmmss'): _unit_hhmmyy_to_datetime_time,
}


def _ret_conversion_function(channel: LogPass.FrameChannel) -> typing.Callable:
    if (channel.ident, channel.units) in NAME_VALUE_CONVERSION_MAP:
        return NAME_VALUE_CONVERSION_MAP[(channel.ident, channel.units)]
    return float


_ASCII_PRINTABLE_MAP = {k: None for k in range(256)}
_ASCII_PRINTABLE_MAP.update({ord(c): c for c in string.printable})
ASCII_PRINTABLE_TABLE = str.maketrans(_ASCII_PRINTABLE_MAP)


def _parse_file(file_object: typing.TextIO, ident: str = '', description: str = 'DAT File',
                break_after_first_row: bool = False) -> LogPass.FrameArray:
    """
    Parses a DAT file into a FrameArray.

    break_after_first_row is used for discovery, only the channel declaration section, the data header and first data
    line are read. If no errors this is likely to be a DAT file.
    """
    file_object.seek(0)
    # Defer creating the FrameArray until we have seen the Channel Header line as that tells us what channels have data
    # in the data section.
    channels_declared: typing.Dict[str, typing.Tuple[str, str]] = {}
    frame_array = LogPass.FrameArray(ident, description)
    in_channel_declaration_section = True
    channels_defined: typing.List[str] = []
    # This is the data section transposed
    data_table = []
    line_number_data_start = 0
    for line_number, line in enumerate(file_object.readlines()):
        assert len(channels_defined) == len(frame_array), f'{len(channels_defined)} != {len(frame_array)}'
        # Sometimes there are spurious spaces at the end of line.
        line = line.strip()
        # Remove non-ASCII printable characters
        line = line.translate(ASCII_PRINTABLE_TABLE)

        if in_channel_declaration_section:
            m = RE_DATA_HEADER_DEFINITION.match(line)
            if m:
                # We are hitting the header line that is the boundary between the channel declaration and the data.
                # Create the FrameArray from the header line but using data from the channel declaration section 1.
                channels_defined = line.split()
                for channel_name in channels_defined:
                    if channel_name not in channels_declared:
                        raise ExceptionDATRead(
                            f'Line: {line_number + 1}: channel name {channel_name} not defined in section 1.'
                        )
                    channel = LogPass.FrameChannel(
                        channel_name,
                        channels_declared[channel_name][0],  # Description
                        channels_declared[channel_name][1],  # Units
                        shape=(1,),
                        np_dtype=_numpy_dtype(channel_name, channels_declared[channel_name][1]),
                    )
                    logger.debug('Line: %d: Adding channel %s', line_number, channel)
                    try:
                        frame_array.append(channel)
                    except LogPass.ExceptionLogPassBase as err:
                        raise ExceptionDATRead(f'Line: {line_number + 1}: {str(err)}')
                    data_table.append(list())
                in_channel_declaration_section = False
                # Next line is data line 0
                line_number_data_start = line_number + 1
            else:
                m = RE_CHANNEL_DEFINITION.match(line)
                if m:
                    description = ' '.join(m.group(2).split())
                    if m.group(1) in channels_defined:
                        raise ExceptionDATRead(
                            f'Line: {line_number + 1}:'
                            f' In channel declaration section with duplicate channel "{m.group(1)}"'
                        )
                    channels_declared[m.group(1)] = (description, m.group(3))
                else:
                    raise ExceptionDATRead(
                        f'Line: {line_number + 1}: In channel declaration section but no match on "{line}"'
                    )
        else:
            # In the data section
            values = line.split()
            if len(values) != len(data_table):
                raise ExceptionDATRead(
                    f'Line: {line_number + 1}:'
                    f' Length of values is {len(values)} but data table length is {len(data_table)}.'
                    f' Missing channel declaration section?'
                )
            # Transpose row.
            for i, v in enumerate(values):
                data_table[i].append(v)
            if break_after_first_row:
                break

    if len(frame_array) == 0:
        raise ExceptionDATRead(f'Parsing DAT file results in no channels.')
    assert len(frame_array.channels) == len(data_table)
    # Convert the data and load the Frame Array
    for i, channel in enumerate(frame_array.channels):
        column = data_table[i]
        channel.init_array(len(column))
        conversion_function = _ret_conversion_function(channel)
        for j, value in enumerate(column):
            try:
                channel[(j, 0)] = conversion_function(value)
            except ValueError as err:
                raise ExceptionDATRead(
                    f'Line: {line_number_data_start + j + 1}: Can not convert value. Error: {str(err)}'
                )
    return frame_array


def parse_file(file_object: typing.TextIO, ident: str = '', description: str = 'DAT File') -> LogPass.FrameArray:
    """
    Parse the File object as a DAT file into a FrameArray. Will raise an ExceptionDAT on error.

    :param file_object: The file to parse.
    :param ident: Identification of this DAT file.
    :param description: Description of this DAT file.
    :return:
    """
    return _parse_file(file_object, ident, description, break_after_first_row=False)


def parse_path(path: str) -> LogPass.FrameArray:  # pragma: no cover
    """Parse the DAT file in the given path."""
    with open(path) as file_object:
        return parse_file(file_object, ident=path)


def can_parse_file(file_object: typing.TextIO) -> bool:
    """Tries to parse the file with just one row of data. On error returns False."""
    try:
        frame_array = _parse_file(file_object, break_after_first_row=True)
        return len(frame_array) > 0 and len(frame_array.x_axis) == 1
    except (ExceptionDAT, LogPass.ExceptionLogPassBase) as err:
        logger.debug(f'DAT_Parser.can_parse_file() error: {err}')
        return False


def can_parse_path(path: str) -> bool:  # pragma: no cover
    """Tries to parse the file at path with just one row of data. On error returns False."""
    with open(path) as file_object:
        return can_parse_file(file_object)


def main() -> int:  # pragma: no cover
    """Read a file and dump the Log Pass."""
    log_pass = parse_path(sys.argv[1])
    if len(log_pass.x_axis):
        print(
            f'X-Axis length {len(log_pass.x_axis)}'
            f' from {log_pass.x_axis.array[0][0].isoformat()}'
            f' to {log_pass.x_axis.array[-1][0].isoformat()}'
        )
    print('Log Pass channels:')
    # print(log_pass)
    print(
        f'     {"Ident":6} {"Description":40} {"Units":10} {"dtype":8} {"Frames":6}'
        f' {"Min":>20} {"Max":>20}'
    )
    for c, ch in enumerate(log_pass.channels):
        print(
            f'[{c:2}] {ch.ident:6} {ch.long_name:40} {ch.units:10} {ch.array.dtype!s:8} {len(ch.array):6d}'
            f' {ch.array.min()!s:>20} {ch.array.max()!s:>20}'
        )
        # break
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
