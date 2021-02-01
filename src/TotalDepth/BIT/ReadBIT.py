#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 1999-2021 Paul Ross
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
Reads Dresser Atlas BIT files.

Address range:

From    To      Bytes   Description
0x0     0x4     4       All null.
0x4     0x8     4       ???
0x10    0xb0    160     ASCII text.
0xb0    0xb2    2       C, the count of channels as big endian two byte format '>H' or '>h'.
0xb2    0xb4    2       Null.
0xb4    0x104  80       Channel names, 4 bytes each.
0x104   0x12c  40       ??? Binary data.



"""
import pprint
import struct
import sys
import typing


OFFSET_DESCRIPTION = 0x10
LENGTH_DESCRIPTION = 0xa0  # 160
# Two byte int
OFFSET_NUMBER_OF_CHANNELS = 0xb0

LEN_FLOAT_BYTES = 4


def bytes_to_float(b: bytes) -> float:
    """Returns a float from four bytes.

    https://en.wikipedia.org/wiki/IBM_hexadecimal_floating-point

    Example: -118.625 -> b'\xc2\x76\xa0\x00'.

    NOTE: This is the same as RP66V1 ISINGL (5) Representation Code.
    """
    if len(b) < LEN_FLOAT_BYTES:
        raise ValueError(f'Need at least 4 bytes not {b}.')
    # # From RP66V2 documentation: "Bits 8-5 of byte 2 may not be all zero except for true zero.
    # if b[1] & 0xf0 == 0 and b != b'\x00\x00\x00\x00':
    #     raise ValueError(f'Bytes representation {b} is illegal.')
    sign = b[0] & 0x80
    exp = b[0] & 0x7f
    mantissa = b[1] << 16
    mantissa |= b[2] << 8
    mantissa |= b[3]
    m = mantissa / 0xffffff
    ret = m * 16**(exp - 64)
    if sign:
        return -ret
    return ret


def read_float(file: typing.BinaryIO) -> float:
    """Returns a float from the current read position."""
    return bytes_to_float(file.read(LEN_FLOAT_BYTES))


def read_channels(byt: bytes) -> typing.List[str]:
    """Read the channels from a complete in-memory file."""
    offset = OFFSET_NUMBER_OF_CHANNELS
    count = struct.unpack('>h', byt[offset:])[0]
    offset += 2
    null = struct.unpack('>h', byt[offset:])[0]
    if null != 0:
        raise ValueError(f'Expected null at 0x{offset:x} but got {null}')
    offset += 2
    ret = []
    for i in range(count):
        ret.append(byt[offset:offset+4].decode('ascii'))
        offset += 4
    return ret


def number_of_channels(file: typing.BinaryIO) -> int:
    file.seek(OFFSET_NUMBER_OF_CHANNELS)
    count = struct.unpack('>h', file.read(2))[0]
    return count


def read_channels_from_file(file: typing.BinaryIO) -> typing.List[str]:
    count = number_of_channels(file)
    null = struct.unpack('>h', file.read(2))[0]
    if null != 0:
        raise ValueError(f'Expected null at 0x{file.tell():x} but got {null}')
    ret = []
    for i in range(count):
        ret.append(file.read(4).decode('ascii'))
    return ret


def read_description_from_file(file: typing.BinaryIO) -> str:
    file.seek(OFFSET_DESCRIPTION)
    ret = file.read(LENGTH_DESCRIPTION)
    return ret.decode('ascii')


def read_file_path_as_floats(file_path: str) -> typing.List[float]:
    ret = []
    with open(file_path, 'rb') as file:
        while True:
            t = file.tell()
            b = file.read(LEN_FLOAT_BYTES)
            if len(b) != LEN_FLOAT_BYTES:
                break
            try:
                ret.append(bytes_to_float(b))
            except ValueError as err:
                print(f'ERROR: {err} at 0x{t:x}')
    return ret

def dump_path_structure(file_path: str) -> None:
    all_as_floats = read_file_path_as_floats(file_path)
    print(f'Read {len(all_as_floats)} floats.')
    print('First 16 bytes:')
    pprint.pprint(all_as_floats[:4])
    print('From 0x104')
    # Looks like (from, to spacing) in feet.
    # Followed by 0.0, 125.0
    pprint.pprint(all_as_floats[16 * 4 + 1:16 * 4 + 1 + 32])
    print('...')
    print('Last frame of 64:')
    pprint.pprint(all_as_floats[-(64 + 6):-6])
    print('Last 24 bytes:')
    pprint.pprint(all_as_floats[-6:])

    # print()
    # for i in range(0, len(all_as_floats), 8):
    #     f_slice = all_as_floats[i:i + 8]
    #     print(' '.join([f'{f:12.3f}' for f in f_slice]))


def dump_path_bytes(file_path: str) -> None:
    with open(file_path, 'rb') as file:
        pprint.pprint(file.read())


def main() -> int:
    example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/456728/30_07a-_1/DWL_FILE/30_07a-_1_dwl_DWL_WIRE_1644802.bit'
    example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/456728/30_07a-_1/DWL_FILE/30_07a-_1_dwl_DWL_WIRE_1644822.bit'
    example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/456728/30_07a-_1/DWL_FILE/30_07a-_1_dwl_DWL_WIRE_1644825.bit'
    example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/456728/30_07a-_1/DWL_FILE/30_07a-_1_dwl_DWL_WIRE_1644826.bit'
    # Smallest at 9kb
    example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/456728/15_17-_12/DWL_FILE/15_17-_12_dwl__1646505.bit'
    # 12kb
    example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT//456728/21_25-B1/DWL_FILE/21_25-B1_dwl_DWL_WIRE_1644592.bit'

    # 30_07a-_1_dwl_DWL_WIRE_1644802.bit
    # 30_07a-_1_dwl_DWL_WIRE_1644822.bit
    # 30_07a-_1_dwl_DWL_WIRE_1644823.bit
    # 30_07a-_1_dwl_DWL_WIRE_1644825.bit
    # 30_07a-_1_dwl_DWL_WIRE_1644826.bit
    # 30_07a-_1_dwl_DWL_WIRE_1644827.bit
    # 30_07a-_1_dwl_DWL_WIRE_1644828.bit

    dump_path_structure(example)
    # dump_path_bytes(example)

    return 0


if __name__ == '__main__':
    sys.exit(main())
