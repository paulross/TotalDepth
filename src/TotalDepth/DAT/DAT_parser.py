"""
Parses DAT files. DAT is an informal specification. Here described:

Section 1: Channel Description.
A set of lines of the form: A B C, space separated, where A is an uppercase word, B is free text (space seperated) and C is a word.

Section 2: Channel Headers
A single line with space separated uppercase words.

Section 3: Channel values
Space separated values. Mostly numeric but date/time conversion can be inferred from section 1.
Note deficiences here:

DATE Date ddmmyy but value 09Dec06
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
"""
import datetime
import logging
import re
import string
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


# Matches 'UTIM Unix Time sec'
RE_CHANNEL_DEFINITION = re.compile(r'^([A-Z]+) (.+?) (\S+)$')

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
        logger.exception('_unit_unix_time_to_datetime_datetime()')
        raise ExceptionDATRead(f'{err} on value "{value}"')


def _unit_ddmmyy_to_datetime_date(value: str) -> datetime.date:
    """Converts date string to datetime.date."""
    try:
        day = int(value[:2])
        mon = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(value[2:5]) + 1
        yr = int(value[5:7])
        if yr > 50:
            yr += 1900
        else:
            yr += 2000
        return datetime.date(yr, mon, day)
    except ValueError as err:
        raise ExceptionDATRead(f'{err} on value "{value}"')


def _unit_hhmmyy_to_datetime_time(value: str) -> datetime.time:
    """Converts time string to datetime.time."""
    try:
        return datetime.datetime.strptime(value, '%H-%M-%S').time()
    except ValueError as err:
        raise ExceptionDATRead(f'{err} on value "{value}"')


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
    break_after_first_row is used for discovery, only the channel section and first line are read. If no errors this is
    likely to be a DAT file.
    """
    file_object.seek(0)
    result = LogPass.FrameArray(ident, description)
    in_channel_definition_section = True
    channels: typing.List[str] = []
    # This is the data section transposed
    data_table = []
    for line in file_object.readlines():
        assert len(channels) == len(result), f'{len(channels)} != {len(result)}'
        # Sometimes there are spurious spaces at the end of line.
        line = line.strip()
        # Remove non-ASCII printable characters
        line = line.translate(ASCII_PRINTABLE_TABLE)
        if line.split() == channels:
            # We are hitting the header line that is the boundary between the channel definition and the data.
            in_channel_definition_section = False
            for _i in range(len(channels)):
                data_table.append([])
        else:
            if in_channel_definition_section:
                m = RE_CHANNEL_DEFINITION.match(line)
                if m:
                    channel = LogPass.FrameChannel(
                        m.group(1), m.group(2), m.group(3), shape=(1,), np_dtype=_numpy_dtype(m.group(1), m.group(3)),
                    )
                    try:
                        result.append(channel)
                    except LogPass.ExceptionLogPassBase as err:
                        raise ExceptionDATRead(str(err))
                    if m.group(1) in channels:
                        raise ExceptionDATRead(f'In channel definition section with duplicate channel "{m.group(1)}"')
                    channels.append(m.group(1))
                else:
                    raise ExceptionDATRead(f'In channel definition section but no match on "{line}"')
            else:
                values = line.split()
                if len(values) != len(data_table):
                    raise ExceptionDATRead(
                        f'Length of values is {len(values)} but data table length is {len(data_table)}.'
                        f' Missing channel definition section?'
                    )
                # Transpose row.
                for i, v in enumerate(line.split()):
                    data_table[i].append(v)
                if break_after_first_row:
                    break
    assert len(result.channels) == len(data_table)
    # Convert the data and load the Frame Array
    for i, channel in enumerate(result.channels):
        column = data_table[i]
        channel.init_array(len(column))
        conversion_function = _ret_conversion_function(channel)
        for j, value in enumerate(column):
            try:
                channel[(j, 0)] = conversion_function(value)
            except ValueError as err:
                raise ExceptionDATRead(str(err))
    if len(result) == 0:
        raise ExceptionDATRead(f'Parsing DAT file results in no channels.')
    return result


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
    with open(path) as file_object:
        return parse_file(file_object, ident=path)


def can_parse_file(file_object: typing.TextIO):
    """Tries to parse the file with just one row of data. On error returns False."""
    try:
        frame_array = _parse_file(file_object, break_after_first_row=True)
        return len(frame_array) > 0 and len(frame_array.x_axis) == 1
    except (ExceptionDAT, LogPass.ExceptionLogPassBase):
        return False


def can_parse_path(path: str) -> bool:  # pragma: no cover
    """Tries to parse the file at path with just one row of data. On error returns False."""
    with open(path) as file_object:
        return can_parse_file(file_object)
