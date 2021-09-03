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
import string


ASCII_VISUAL_BYTES = set(
    bytes(string.digits + string.ascii_letters + string.punctuation + ' ', 'ascii')
)


def xxd(by: bytes,
        columns: int = 16,
        uppercase: bool = False,
        ebcdic: bool = False,
        binary: bool = False,
        length: int = 0,
        offset: int = 0,
        seek: int = 0) -> str:
    """
    Returns an xxd style string of the bytes. For example::

        0084 8000 8400 2647 3546 3239 2020 2020 2020 ......&G5F29

    ``columns`` - Number of octets in each row.

    ``uppercase`` - use upper case hex letters.

    ``ebcdic`` - show characters in EBCDIC. Default ASCII.

    ``binary`` - binary digit dump. Default hex.

    ``length``  - stop after <length> octets.

    ``offset`` - add <offset> to the displayed file position.

    ``seek`` - start at <seek> bytes infile offset.
    """
    if columns < 1:
        raise ValueError(f'Columns must be +ve not {columns}')
    if offset < 0:
        raise ValueError(f'Offset must be +ve not {offset}')
    if length < 0:
        raise ValueError(f'Length must be +ve not {length}')
    if seek < 0:
        raise ValueError(f'Seek must be +ve not {seek}')
    if seek:
        by = by[seek:]
    if length > 0:
        by = by[:length]
    lines = []
    len_position = len(f'{len(by) + offset:x}')
    for i in range(0, len(by), columns):
        part = by[i:i + columns]
        hex_list = []
        chr_list = []
        j = 0
        while j < len(part):
            if binary:
                if j:
                    hex_list.append(' ')
                hex_list.append('{:08b}'.format(part[j]))
            else:
                if j and j % 2 == 0:
                    hex_list.append(' ')
                if uppercase:
                    hex_list.append('{:02X}'.format(part[j]))
                else:
                    hex_list.append('{:02x}'.format(part[j]))
            if ebcdic:
                char = part[j:j+1].decode('cp500')
                if ord(char) in ASCII_VISUAL_BYTES:
                    chr_list.append(char)
                else:
                    chr_list.append('.')
            else:
                if part[j] in ASCII_VISUAL_BYTES:
                    chr_list.append(chr(part[j]))
                else:
                    chr_list.append('.')
            j += 1
        while j < columns:
            if j and j % 2 == 0:
                hex_list.append(' ')
            hex_list.append('  ')
            chr_list.append(' ')
            j += 1
        lines.append(f'{i + offset + seek:0{len_position}x} {"".join(hex_list)} {"".join(chr_list)}')
    return '\n'.join(lines)
