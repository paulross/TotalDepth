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
"""Reads LAS files.

Created on Jan 11, 2012

Research
========

Finding occurrences of ``STEP``::

    $ grep -rIh 'STEP\.' LAS_1.2_2.0/ | sed -e 's/^[[:space:]]*//' | tr -s ' ' | sort -b | uniq

From that file occurrences of ``STEP`` of zero in around 24,000 files:

    $ grep -rI 'STEP\.' LAS_1.2_2.0/ | sed -e 's/^[[:space:]]*//' | tr -s ' ' | grep 'STEP\.F 0\.00' | wc -l
    $ grep -rI 'STEP\.' LAS_1.2_2.0/ | sed -e 's/^[[:space:]]*//' | tr -s ' ' | grep 'STEP\.M 0\.00' | wc -l
    $ grep -rI 'STEP\.' LAS_1.2_2.0/ | sed -e 's/^[[:space:]]*//' | tr -s ' ' | grep 'STEP\.S 0\.00' | wc -l

F: 629
M: 114
S:  29
Total 772 or about 3.2%
"""
import datetime
import logging
import os
import re
import typing

import numpy as np

from TotalDepth.LAS import ExceptionTotalDepthLAS
from TotalDepth.LAS.core import LASConstants
from TotalDepth.LIS.core import EngVal
from TotalDepth.common import LogPass

__author__ = 'Paul Ross'
__date__ = '2012-01-11'
__version__ = '0.1.0'
__rights__ = 'Copyright (c) 2012 Paul Ross.'


logger = logging.getLogger(__file__)


class ExceptionLASRead(ExceptionTotalDepthLAS):
    """Specialisation of exception for LASRead."""
    pass


class ExceptionLASReadSection(ExceptionLASRead):
    """Specialisation of exception for LASRead when handling sections."""
    pass


class ExceptionLASReadSectionArray(ExceptionLASReadSection):
    """Specialisation of exception for LASRead when handling array section."""
    pass


class ExceptionLASReadData(ExceptionLASRead):
    """Specialisation of exception for LASRead when reading data."""
    pass


class ExceptionLASKeyError(ExceptionLASRead):
    """Equivalent to KeyError when looking stuff up."""
    pass


#: LAS file extension
LAS_FILE_EXT = '.las'
#: LAS lower case file extension
LAS_FILE_EXT_LOWER = LAS_FILE_EXT.lower()


def has_las_extension(fp):
    """Returns True if the file extansion is a LAS one."""
    return os.path.splitext(os.path.normcase(fp))[1] == LAS_FILE_EXT


#: Regex to match a comment
#: Section 5.1 of "LAS Version 2.0: A Digital Standard for Logs, Update February 2017"
RE_COMMENT = re.compile(r'^\s*#(.*)$')


#: logger.debug call here can add about 50% of the processing time
DEBUG_LINE_BY_LINE = False


def generate_lines(text_file):
    """
    Given an file-like object this generates non-blank, non-comment lines.
    It's a co-routine so can accept a line to put back.
    """
    line_number = 1
    while 1:
        line = text_file.readline()
        # logger.debug call here can add about 50% of the processing time
        if DEBUG_LINE_BY_LINE: logger.debug('[{:08d}]: {:s}'.format(line_number, line.replace('\n', '\\n')))
        if len(line) == 0:
            break
        if line != '\n' and not RE_COMMENT.match(line):
            line = yield line_number, line
            if line is not None:
                # Recycle it
                yield None
                yield line_number, line
        line_number += 1


#: All section identifiers
SECT_TYPES = 'VWCPOA'
#: Section with data lines
SECT_TYPES_WITH_DATA_LINES = 'VWCP'
#: Section with index value in column 0
SECT_TYPES_WITH_INDEX = 'VWCPA'

#: Regex to match a section head
RE_SECT_HEAD = re.compile(r'^~([{:s}])(.+)*$'.format(SECT_TYPES))

#: Map of section identifiers to description
SECT_DESCRIPTION_MAP = {
    'V': "Version Information Section",
    'W': "Well Information Section",
    'C': "Curve Information Section",
    'P': "Parameter Information Section",
    'O': "Other Information Section",
    'A': "ASCII Log Data",
}

#: The 'MENM' field, no spaces, dots or colons.
#: ONE group
#: Perhaps Allow spaces in mnemonic. For example:
#: "SWU -CPX.V/V          00 000 00 00:  75  Unlimited Formation Water Saturation (Complex Litho Model)"
#: This is specifically excluded by LAS 2.0 (Page 4, 2017-01) but it happens.
#: Also: "Spaces are permitted in front of the mnemonic and between the end of the mnemonic and the dot."
RE_LINE_FIELD_0 = re.compile(r'^\s*([^ .:]+)\s*$')

#: The data field which is the middle of the line between the first '.' and last ':'
#: This is composed of optional units and value.
#: Units must follow the dot immediately and contain no colons or spaces
#: Note: Group 2 may have leading and trailing spaces
#: TWO groups 
RE_LINE_FIELD_1 = re.compile(r'^([^ :]+)*(.+)*$')


def string_to_value(value: typing.Any) -> typing.Any:
    """Convert a value to an integer, float, bool or string. If a string it is stripped."""
    if value is not None:
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        if isinstance(value, str):
            value = value.strip()
            if value.lower() == "yes":
                return True
            elif value.lower() == "no":
                return False
            return value
    return ''


class SectLine(typing.NamedTuple):
    """Captures the four fields from a single line: mnem unit valu desc"""
    mnem: str
    unit: str
    valu: typing.Any
    desc: str


def line_to_sect_line(line: str) -> SectLine:
    # A hybrid approach where we split the line then apply individual regex's
    dot_index = line.find('.')
    if dot_index == -1:
        raise ExceptionLASReadSection(f'Can not find \'.\' in line: {line}')
    colon_index = line.rfind(':')
    if colon_index == -1:
        raise ExceptionLASReadSection(f'Can not find \':\' in line: {line}')
    m0 = RE_LINE_FIELD_0.match(line[:dot_index])
    m1 = RE_LINE_FIELD_1.match(line[dot_index + 1:colon_index])
    description = line[colon_index + 1:]
    if m0 is None or m1 is None:
        # Use !s prefix as any of m0, m1, m2 can be None.
        raise ExceptionLASReadSection('Can not decompose line "{:s}" with results: {!s:s}, {!s:s}'.format(
                line.replace('\n', '\\n'), m0, m1
            )
        )
    return SectLine(*[string_to_value(g) for g in (m0.groups() + m1.groups() + (description,))])


class LASSection:
    """Contains data on a section."""
    #: Contains the allowable values of certain mnemonics in a section.
    #: The appropriate section must have these mnemonics in the given order and the values of those mnemonics must be
    #: one of the given values.
    SECTION_MNEMONIC_ORDER_AND_VALUES = {
        'V': (
               ('VERS', (1.2, 2.0)),
               ('WRAP', (True, False)),
            ),
    }

    def __init__(self, section_type: str, raise_on_error: bool = True):
        # assert(section_type in SECT_TYPES)
        self.type = section_type
        self.raise_on_error = raise_on_error
        # One entry per line
        self.members: typing.List[typing.Union[str, SectLine]] = []
        # {MNEM : ordinal, ...} for those sections that have it
        # Populated by finalise()
        self.mnemonic_index_map: typing.Dict[typing.Union[str, float], int] = {}
        
    def __str__(self):
        return 'LASSection: "{:s}" with {:d} lines'.format(self.type, len(self.members))
    
    def __len__(self):
        """Number of members."""
        return len(self.members)
    
    def __contains__(self, mnemonic: str):
        """Membership test."""
        return mnemonic in self.mnemonic_index_map

    def add_member_line(self, line_number, line):
        """Given a line this decomposes it to its _members. line_number is the position of the line l in the file
        starting at 1.
        Empty lines are ignored."""
        if len(line):
            if self.type in SECT_TYPES_WITH_DATA_LINES:
                try:
                    self.members.append(line_to_sect_line(line))
                except ExceptionLASReadSection as err:
                    raise ExceptionLASReadSection(f'Can not add member, line {line_number} error: {err}') from err
            else:
                self.members.append(line.strip())

    def create_index(self):
        """Creates an index of {key : ordinal, ...}.
        key is the first object in each member. This will be a MNEM for most
        sections but a depth as a float for an array section."""
        self.mnemonic_index_map: typing.Dict[typing.Union[str, float], int] = {}
        if self.type in SECT_TYPES_WITH_INDEX:
            for m, memb in enumerate(self.members):
                # Note we use memb[0] so this works for SectLine and lists
                k = memb[0]
                if k in self.mnemonic_index_map:
                    logger.warning('Ignoring duplicate menmonic "{:s}", was {:s} dupe is {:s}'.format(
                        str(k),
                        str(self.members[self.mnemonic_index_map[k]]),
                        str(memb),
                        )
                    )
                else:
                    self.mnemonic_index_map[k] = m

    def finalise(self):
        """Finalisation of section, this updates the internal representation."""
        self.create_index()
        # Apply static rules if appropriate.
        if self.type in self.SECTION_MNEMONIC_ORDER_AND_VALUES:
            rules_list = self.SECTION_MNEMONIC_ORDER_AND_VALUES[self.type]
            # if len(self.members) != len(rules_list):
            #     logger.warning(
            #         'Section "%s" must have %d entries not %d.', self.type, len(rules_list), len(self)
            #     )
            for i, (m, rng) in enumerate(rules_list):
                if i >= len(self.members):
                    raise ExceptionLASReadSection(
                        'Section "{:s}" must have {:d} entries not {:d}.'.format(self.type, len(rules_list), len(self))
                    )
                if self.members[i].mnem != m:
                    raise ExceptionLASReadSection(
                        'Section "{:s}" must have entry[{:d}]: "{:s}".'.format(self.type, i, m)
                    )
                if self.members[i].valu not in rng:
                    raise ExceptionLASReadSection(
                        'Section "{:s}" must have value for "{:s}" converted to {:s} from "{:s}".'.format(
                            self.type,
                            m,
                            str(rng),
                            str(self.members[i].valu),
                        )
                    )
        # TODO: Essential MNEM in other sections
        # TODO: 'W' section: Check consistency of STRT/STOP/STEP and their units
    
    def __getitem__(self, key) -> SectLine:
        """Returns an entry, key can be int or str."""
        if isinstance(key, int):
            return self.members[key]
        if isinstance(key, str):
            return self.members[self.mnemonic_index_map[key]]
        raise TypeError('{:s} object is not subscriptable with {:s}'.format(type(self), type(key)))
        
    def mnemonics(self):
        """Returns an list of mnemonics."""
        return [m.mnem for m in self.members]

    def units(self):
        """Returns an list of mnemonic units."""
        return [m.unit for m in self.members]
    
    def keys(self):
        """Returns the keys in the internal map."""
        return self.mnemonic_index_map.keys()
    
    def find(self, m):
        """Returns the member ordinal for mnemonic m or -1 if not found.
        This can be used for finding the array column for a particular curve."""
        try:
            return self.mnemonic_index_map[m]
        except KeyError:
            pass
        return -1


class LASSectionArray(LASSection):
    """Contains data on an array section."""
    # FIXME: Locale specific %b.
    DATE_FORMATS_SUPPORTED = ('%d-%b-%y',)
    TIME_FORMATS_SUPPORTED = ('%H:%M:%S',)

    def __init__(self, section_type: str, wrap: bool, curve_section: LASSection,
                 null: typing.Union[int, float] = -999.25, raise_on_error: bool = True):
        assert (section_type == 'A')
        self._wrap = wrap
        # Accumulation of array values when un-wrapping
        self._unwrap_buffer = []
        self._mnemonics_units = list(zip(curve_section.mnemonics(), curve_section.units()))
        self._duplicate_column_indexes: typing.Set[int] = set()
        super().__init__(section_type, raise_on_error)
        self._null = null
        # TODO: If we have STRT, STOP and STEP we can predict the  length of the array section and initialise a
        # FrameArray before adding member lines.
        # If STEP is 0 we can't do this, instead read all the member lines and populate a FrameArray on finalise().
        # In that case how strict are we about the (STRT - STOP) / STEP
        # calculation and how strict about the members coming up short or overflowing?
        # Need to pass in a ~Well Information Section (for STRT, STOP, STEP, NULL) and a ~Curve Information Section as
        # before.
        self.frame_array = LogPass.FrameArray(self.type, self.type)
        try:
            for channel_index, (mnemonic, units) in enumerate(self._mnemonics_units):
                if self.frame_array.has(mnemonic) and not self.raise_on_error:
                    self._duplicate_column_indexes.add(channel_index)
                    logger.warning('Populating Frame Array, ignoring duplicate channel %s', mnemonic)
                else:
                    if mnemonic == 'DATE' and units == 'D':
                        channel = LogPass.FrameChannel(mnemonic, mnemonic, units, (1,), np.dtype('O'))
                    elif mnemonic == 'TIME' and units == 'HHMMSS':
                        channel = LogPass.FrameChannel(mnemonic, mnemonic, units, (1,), np.dtype('O'))
                    else:
                        channel = LogPass.FrameChannel(mnemonic, mnemonic, units, (1,), LogPass.DEFAULT_NP_TYPE)
                    self.frame_array.append(channel)
        except LogPass.ExceptionLogPassBase as err:
            raise ExceptionLASReadSection(str(err)) from err

    def _add_buffer(self, line_number: int) -> None:
        """Adds the temporary buffer to the array. This is associated with the given line number."""
        if len(self._unwrap_buffer) > 0:
            if len(self._unwrap_buffer) != len(self._mnemonics_units):
                raise ExceptionLASReadSectionArray(
                    'Line [{:d}] buffer length miss-match, frame length {:d} which should be length {:d}'.format(
                        line_number,
                        len(self._unwrap_buffer),
                        len(self._mnemonics_units),
                    )
                )
            self.members.append(self._unwrap_buffer)
            self._unwrap_buffer = []

    def _convert_value(self, channel: LogPass.FrameChannel, value: str, line_number: int) -> typing.Any:
        """Convert a value to a float, date or time. If the conversion is not successful then self._null, None, None are
        returned respectively."""
        if channel.ident == 'DATE' and channel.units == 'D':
            for dt_format in self.DATE_FORMATS_SUPPORTED:
                try:
                    return datetime.datetime.strptime(value, dt_format).date()
                except ValueError:
                    pass
            logger.warning(
                'LASSectionArray._convert_value(): line [%d], can not convert "%s" to date, returning None.',
                    line_number, value
            )
            return None
        elif channel.ident == 'TIME' and channel.units == 'HHMMSS':
            for dt_format in self.TIME_FORMATS_SUPPORTED:
                try:
                    return datetime.datetime.strptime(value, dt_format).time()
                except ValueError:
                    pass
            logger.warning(
                'LASSectionArray._convert_value(): line [%d], can not convert "%s" to time, returning None.',
                    line_number, value
            )
            return None
        else:
            try:
                return float(value)
            except ValueError:
                logger.warning(
                    'LASSectionArray._convert_value(): line [%d], can not convert "%s" to float, returning %s.',
                        line_number, value, self._null
                )
            return self._null

    def add_member_line(self, line_number: int, line: str) -> None:
        """Process a line in an array section."""
        # Convert to float inserting null where that can not be done
        # values = []
        # channel_index = 0
        # for column_index, value in enumerate(line.strip().split()):
        #     if column_index not in self._duplicate_column_indexes:
        #         if channel_index >= len(self.frame_array):
        #             raise ExceptionLASRead(
        #                 f'Expected {len(self.frame_array)} channels but found {column_index + 1} in line {line_number}'
        #             )
        #         values.append(self._convert_value(self.frame_array[channel_index], value, line_number))
        #         channel_index += 1
        values = line.strip().split()
        # Add it to the members
        if len(values) > 0:
            if self._wrap:
                self._add_member_with_wrap_mode(line_number, line, values)
            else:
                self.members.append(values)

    def _add_member_with_wrap_mode(self, line_number: int, line: str, values: typing.List[typing.Any]) -> None:
        """Addes a line in wrap mode."""
        assert self._wrap
        if len(self._unwrap_buffer) == 0:
            # Add the index, raise if there is more than one item on the line
            # We add to the buffer until the length matches the len(self._mnemUnitS)
            if len(values) == 1:
                self._unwrap_buffer.append(values[0])
            else:
                # Abandon existing data
                self.members = []
                raise ExceptionLASReadSectionArray(
                    'Line [{:d}] More than one [{:d}] index values, line is: {:s}'.format(
                        line_number, len(values), line.replace('\n', '\\n'),
                    ))
        else:
            # Add to buffer
            self._unwrap_buffer.extend(values)
            # Is buffer complete or has overflowed?
            if len(self._unwrap_buffer) == len(self._mnemonics_units):
                self._add_buffer(line_number)
            elif len(self._unwrap_buffer) > len(self._mnemonics_units):
                raise ExceptionLASReadSectionArray(
                    'Line [{:d}] array overflow; frame length {:d} which should be length {:d}'.format(
                        line_number, len(self._unwrap_buffer), len(self._mnemonics_units),
                    ))

    def __getitem__(self, key) -> LogPass.FrameChannel:
        """Returns an entry, key can be int or str."""
        return self.frame_array[key]

    def __len__(self):
        """Number of members."""
        return len(self.frame_array)

    def create_index(self):
        """Creates an index of {key : ordinal, ...}.
        key is the first object in each member. This will be a MNEM for most
        sections but a depth as a float for an array section."""
        self.mnemonic_index_map: typing.Dict[typing.Union[str, float], int] = {}
        if self.frame_array and len(self.frame_array):
            for i, x_value in enumerate(self.frame_array.x_axis):
                key = x_value[0]
                if key in self.mnemonic_index_map:
                    if self.raise_on_error:
                        raise ExceptionLASRead(f'Duplicate Xaxis value {key} in frame {i}')
                    logger.warning('Duplicate Xaxis value %f in frame %d', key, i)
                else:
                    self.mnemonic_index_map[key] = i

    def finalise(self):
        """Finalisation."""
        try:
            self._add_buffer(-1)
        finally:
            if len(self.members):
                try:
                    self.frame_array.init_arrays(len(self.members))
                    expected_number_of_columns = len(self.frame_array) + len(self._duplicate_column_indexes)
                    for frame_number, member_frame in enumerate(self.members):
                        if len(member_frame) != expected_number_of_columns:
                            raise ExceptionLASRead(
                                f'Expected {expected_number_of_columns} columns'
                                f' but found {len(member_frame)} in frame {frame_number}'
                            )
                        channel_index = 0
                        for column_index, value in enumerate(member_frame):
                            if column_index not in self._duplicate_column_indexes:
                                self.frame_array[channel_index][frame_number] = self._convert_value(
                                    self.frame_array[channel_index], value, frame_number
                                )
                                channel_index += 1
                    self.create_index()
                    # Free up temporary members
                    for member in self.members:
                        member.clear()
                    self.members.clear()
                    # Mask the array
                    self.frame_array.mask_array(self._null)
                except LogPass.ExceptionLogPassBase as err:
                    raise ExceptionLASRead(f'LogPass exception: {err}') from err

    def frame_size(self):
        """Returns the number of data points in a frame."""
        return len(self._mnemonics_units)


class LASBase:
    """Base class for LAS reading and writing. This provides common functionality to child classes."""
    #: Mapping of commonly seen LAS units to proper LIS units
    #: Both key and value must be strings
    UNITS_LAS_TO_LIS = {
        # Noticed on depth indices
        'F': 'FEET',
        'mts': 'M   ',
    }
    # Hack to expand units to 4 chars so 'FT' becomes 'FT  '
    UNITS_MNEM_LEN = 4

    def __init__(self, identity: str):
        self.id = identity
        self._sections: typing.List[LASSection] = []
        # {sect_type : ordinal, ...}
        # Populated by _finalise()
        self._section_map:  typing.Dict[str, int] = {}
        self._wrap = None
        
    def __len__(self):
        """Number of sections."""
        return len(self._sections)
    
    def __getitem__(self, key):
        """Returns a section, key can be int or str."""
        if isinstance(key, int):
            return self._sections[key]
        if isinstance(key, str):
            return self._sections[self._section_map[key]]
        raise TypeError('{:s} object is not subscriptable with {:s}'.format(type(self), type(key)))

    def has_section(self, section_type: str) -> bool:
        return section_type in self._section_map

    def _finalise_section_and_add(self, section: LASSection) -> None:
        section.finalise()
        if section.type in self._section_map:
            raise ExceptionLASRead('Duplicate section {:s}'.format(section.type))
        self._section_map[section.type] = len(self._sections)
        self._sections.append(section)
    
    # def _finalise(self):
    #     raise NotImplementedError
    
    def generate_sections(self) -> typing.Sequence[LASSection]:
        """Yields up each section."""
        for s in self._sections:
            yield s
            
    @property
    def null_value(self) -> float:
        """The NULL value, defaults to -999.25."""
        try:
            return self['W']['NULL'].valu
        except KeyError:
            pass
        # Bit contentious this as LAS does not specify default value for this
        return -999.25
        
    @property
    def x_axis_units(self):
        """The X axis units."""
        try:
            return self._units(self['W']['STRT'].unit)
        except KeyError:
            raise ExceptionLASReadData('LASBase.logDown(): No "W" section or no "STRT" value.')

    def _units(self, u):
        """Given a string of units return it as LIS like units in bytes."""
        if u is None:
            u = '    '
        try:
            u = self.UNITS_LAS_TO_LIS[u]
        except KeyError:
            pass
        # Expand units to 4 chars if necessary
        if len(u) < self.UNITS_MNEM_LEN:
            u = u + ' ' * (self.UNITS_MNEM_LEN - len(u))
        return bytes(u, 'ascii')

    def _wsd_eng_value(self, mnemonic) -> EngVal.EngVal:
        v, u = self.get_wsd_mnemonic(mnemonic)
        if v is not None:
            return EngVal.EngVal(v, self._units(u))
            
    @property
    def x_axis_start(self) -> EngVal.EngVal:
        """The Xaxis start value as an EngVal."""
        return self._wsd_eng_value('STRT')

    @property
    def x_axis_stop(self) -> EngVal.EngVal:
        """The Xaxis end value as an EngVal."""
        return self._wsd_eng_value('STOP')

    @property
    def x_axis_step(self) -> EngVal.EngVal:
        """The Xaxis step value as an EngVal."""
        return self._wsd_eng_value('STEP')

    def is_log_down(self) -> bool:
        """Returns True if X axis is increasing i.e. for time or down log."""
        try:
            return self['W']['STEP'].valu > 0
        except KeyError:
            raise ExceptionLASReadData('LASBase.logDown(): No "W" section or no "STEP" value.')
    
    def get_wsd_mnemonic(self, mnemonic) -> typing.Tuple[typing.Union[str, None], typing.Union[str, None]]:
        """Returns a tuple of (value, units) for a Mnemonic that may appear in either a
        Well section or a Parameter section. Units may be None if empty.
        Returns (None, None) if nothing found.
        """
        for s in 'WP':
            try:
                sect = self[s]
            except KeyError:
                pass
            else:
                try:
                    member = sect[mnemonic]
                except KeyError:
                    pass
                else:
                    return member.valu, member.unit
        return None, None
    
    def get_all_wsd_mnemonics(self) -> typing.Set[str]:
        """Returns a set of mnemonics from the Well section and the Parameter section."""
        ret = set()
        for s in 'WP':
            try:
                ret |= set(self[s].keys())
            except KeyError:
                pass
        return ret
    
    # Section: Channel data access.
    def _curve_or_alt_curve(self, mnemonic: str):
        """Returns the entry in the Curve table corresponding to theMnem.
        The list of alternate names table LGFORMAT_LAS from LASConstants to interpret 
        curves that are not exact matches.
        Will raise KeyError if no Curve section or no matching curve."""
        i = self._find_curve_or_alt_curve(mnemonic)
        if i != -1:
            return self['C'][i]
        raise KeyError
        
    def _find_curve_or_alt_curve(self, mnemonic: str):
        """Returns the index if entry in the Curve table corresponding to theMnem.
        The list of alternate names table LGFORMAT_LAS from LASConstants to interpret 
        curves that are not exact matches.
        Returns -1 if not found. Will raise KeyError if no Curve section."""
        idx = self['C'].find(mnemonic)
        if idx != -1:
            return idx
        if mnemonic in LASConstants.LGFORMAT_LAS:
            for alt in LASConstants.LGFORMAT_LAS[mnemonic]:
                idx = self['C'].find(alt)
                if idx != -1:
                    return idx
        return -1
        
    def has_output_mnemonic(self, mnemonic: str):
        """Returns True if theMnem, a Mnem.Mnem() object is an output in the Curve section.
        It will use the alternate names table LGFORMAT_LAS from LASConstants to interpret 
        curves that are not exact matches."""
        try:
            return self._find_curve_or_alt_curve(mnemonic) != -1
        except KeyError:
            # No curve section
            pass
        return False
    
    def curve_mnemonics(self, ordered=False):
        """Returns list of curve names actually declared in the Curve section.
        List will be unordered if ordered is False."""
        r = []
        try:
            if ordered:
                for i in range(len(self['C'])):
                    r.append(self['C'][i].mnem)
            else:
                r = self['C'].keys()
        except KeyError:
            # No curve section
            pass
        return r
    
    def curve_units_as_str(self, m):
        """Given a curve as a Mnem.Mnem() this returns the units as a string.
        May raise KeyError."""
        return self._units(self._curve_or_alt_curve(m).unit)
    
    # End: Channel data access.


class LASRead(LASBase):
    """Reads a LAS file."""
    def __init__(self, file_path: typing.Union[str, typing.TextIO],
                 file_identity: str = '', raise_on_error: bool = True):
        """
        Reads a LAS file from theFp that is either a string (file path) or a file like object.
        If raise_on_error is True then some errors will terminate processing, if False then some errors will be
        ignored.
        """
        self._section_dispatch_map = {
            'V': self._process_section_v,
            'W': self._process_section,
            'C': self._process_section,
            'P': self._process_section,
            'O': self._process_section,
            'A': self._process_section_a,
        }
        if isinstance(file_path, str):
            file_path = open(file_path, 'r', errors='replace')
        self.raise_on_error = raise_on_error
        if not file_identity:
            try:
                file_identity = file_path.name
            except AttributeError:
                pass
        super().__init__(file_identity)
        self._process_file(generate_lines(file_path))
        # self._finalise()

    def number_of_frames(self) -> int:
        """Returns the number of frames of data in an 'A' record if I have one."""
        if self.frame_array is not None:
            return len(self.frame_array.x_axis)
        return 0

    def number_of_data_points(self):
        """Returns the number of frame data points in an 'A' record if I have one."""
        if self.frame_array is not None:
            return len(self.frame_array.x_axis) * len(self.frame_array)
        return 0

    def _process_file(self, gen: typing.Generator[typing.Tuple[int, str], None, None]):

        def _consume_section(gen):
            """Just read the section and throw it away."""
            logger.warning(
                'LASRead._proccess_file(): Line: %d Unknown line: "%s"', line_number, line.replace('\n', '\\n')
            )
            # Consume following non-section lines
            num_lines = 0
            for _l, throw_away_line in gen:
                match = RE_SECT_HEAD.match(throw_away_line)
                if match is not None:
                    gen.send(throw_away_line)
                    break
                num_lines += 1
            logger.warning('LASRead._procFile(): Consumed {:d} succeeding lines.'.format(num_lines))

        for line_number, line in gen:
            logger.debug('_procFile(): line %d "%s"', line_number, line)
            line = line.strip()
            m = RE_SECT_HEAD.match(line)
            if m is not None:
                self._section_dispatch_map[m.group(1)](m, gen)
            else:
                if line.startswith('~') and len(line) > 1:
                    # A section that has undefined content. Must appear after a 'V' section and before an 'A' section.
                    if 'V' not in self._section_map:
                        if self.raise_on_error:
                            raise ExceptionLASRead(f'User defined section "{line}" but no version section.')
                        else:
                            _consume_section(gen)
                    elif 'A' in self._section_map:
                        if self.raise_on_error:
                            raise ExceptionLASRead(f'User defined section "{line}" after array section.')
                        else:
                            _consume_section(gen)
                    else:
                        section = LASSection(line[1], raise_on_error = self.raise_on_error)
                        self._add_members_to_section(gen, section)
                        self._finalise_section_and_add(section)
                else:
                    _consume_section(gen)

    def _proc_section_generic(self, match: re.match,
                              gen: typing.Generator[typing.Tuple[int, str], None, None]) -> LASSection:
        section = LASSection(match.group(1))
        self._add_members_to_section(gen, section)
        return section

    def _add_members_to_section(self, gen, section: LASSection):
        for i, line in gen:
            if DEBUG_LINE_BY_LINE:
                logger.debug('line %d "%s"', i, line)
            line = line.strip()
            # Bail out if start of new section
            if line.startswith('~'):
                gen.send(line)
                break
            try:
                section.add_member_line(i, line)
            except ExceptionLASRead as error:
                if self.raise_on_error:
                    raise
                logger.warning('Ignoring error %s', error)

    def _process_section_v(self, match: re.match, gen: typing.Generator[typing.Tuple[int, str], None, None]) -> None:
        logger.debug('_procSectV(): Start')
        assert(match is not None)
        if len(self._sections) != 0:
            raise ExceptionLASRead('Version section must be first one.')
        section = self._proc_section_generic(match, gen)
        self._finalise_section_and_add(section)
        self._wrap = section['WRAP'].valu
        logger.debug('_procSectV(): End')

    def _process_section(self, match: re.match, gen: typing.Generator[typing.Tuple[int, str], None, None]) -> None:
        logger.debug('_procSect(): Start: {:s}'.format(match.group(1)))
        assert(match is not None)
        if len(self._sections) == 0:
            raise ExceptionLASRead('Non-version section can not be the first one.')
        self._finalise_section_and_add(self._proc_section_generic(match, gen))
        logger.debug('_procSect(): End: {:s}'.format(match.group(1)))

    def _process_section_a(self, match: re.match, gen: typing.Generator[typing.Tuple[int, str], None, None]) -> None:
        logger.debug('_procSectA(): Start')
        assert(match is not None)
        if len(self._sections) == 0:
            raise ExceptionLASRead('Non-version section can not be the first one.')
        assert(self._wrap is not None)
        curve_index = 0
        for section in self._sections:
            if section.type == 'C':
                break
            curve_index += 1
        if curve_index > len(self._sections)-1:
            raise ExceptionLASRead('No curve section to describe array section.')
        # TODO: Pass in NULL
        array_section = LASSectionArray(match.group(1), self._wrap, self._sections[curve_index], raise_on_error=self.raise_on_error)
        for i, line in gen:
            # Bail out if start of new section
            if line.startswith('~'):
                gen.send(line)
                if self.raise_on_error:
                    raise ExceptionLASRead(
                        'Line: {:d}. Found section header line "{:s}" after array section'.format(i, line.strip())
                    )
            array_section.add_member_line(i, line)
        self._finalise_section_and_add(array_section)
        logger.debug('_procSectA(): End')

    @property
    def frame_array(self) -> typing.Union[LogPass.FrameArray, None]:
        if 'A' in self._section_map:
            return self._sections[self._section_map['A']].frame_array
