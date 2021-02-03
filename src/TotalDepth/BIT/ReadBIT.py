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


First block without TIF markers:


0000000c: 0002 0000 5348 454c 4c20 4558 5052 4f20  ....SHELL EXPRO
0000001c: 552e 4b2e 2020 2020 2020 3234 204f 4354  U.K.      24 OCT
0000002c: 2038 3420 2020 2020 204d 414e 5346 4945   84      MANSFIE
0000003c: 4c44 2f44 4f44 4453 2020 2020 2020 2020  LD/DODDS
0000004c: 2020 2020 2020 2020 2020 2020 000a 0018              ....
0000005c: 0054 2020 3220 3920 2f20 3120 3020 2d20  .T  2 9 / 1 0 -
0000006c: 3320 2020 2020 2020 2020 2020 2020 2020  3
0000007c: 2020 2020 2020 2020 2020 2020 2020 2020
0000008c: 2020 2020 2020 2020 2020 2020 2020 2020
0000009c: 2020 2020 2020 2020 2020 2020 0012 000b              ....
000000ac: 0006 2020 000a 0000 434f 4e44 534e 2020  ..  ....CONDSN
000000bc: 5350 2020 4752 2020 4341 4c20 5445 4e20  SP  GR  CAL TEN
000000cc: 5350 4420 4143 5120 4143 2020 5254 2020  SPD ACQ AC  RT
000000dc: 2020 2020 2020 2020 2020 2020 2020 2020
000000ec: 2020 2020 2020 2020 2020 2020 2020 2020
000000fc: 2020 2020 2020 2020 443a 6600 4438 fe00          D:f.D8..
0000010c: 4040 0000 0000 0000 4210 0000 4d4e 3233  @@......B...MN23
0000011c: 394a 2031


Address range:

From    To      Bytes   Description
0x0     0x8     8       All null.
0x8     0x9     1       Single space.
0x9     0xa     1       Value 1, b'\x01'
0xa     0xc     2       Two nulls, b'\x00\x00'
0xc     0x10    4       Single float, meaning unknown.
0x10    0xb0    160     ASCII text, the description.
0xb0    0xb2    2       C, the count of channels as big endian two byte format '>H' or '>h'.
0xb2    0xb4    2       Null.
0xb4    0x104  80       Channel names, 4 bytes each.
0x104   0x118  20       Five floats start, stop, step, 0, ???.
0x118   0x120   8       Eight spaces, 0x20
0x120   0x128   8       Eight nulls, 0x00
0x128                   Start of data block.

Most commonly the first 12 bytes are [0, 0, 0, 0, 0, 0, 0, 0, 32, 1, 0, 0,]


Decoding the frames
-------------------

There is a directory that has both BIT and LIS files in it.

LIS: 29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1988494.lis
BIT: 29_10-_3Z_dwl_DWL_WIRE_1644659.bit and 29_10-_3Z_dwl_DWL_WIRE_1644660.bit

Log Pass 0 has X axis:
14950.000 (FT) to 14582.250 (FT) Interval -367.750 (FT)
Total number of frames	1472
Overall frame spacing	-0.250 (FT)

Corresponding BIT file 29_10-_3Z_dwl_DWL_WIRE_1644659.bit has:

LogPassRange(depth_from=14950.000891089492, depth_to=14590.000869631818, spacing=0.2500000149011621, unknown_a=0.0, unknown_b=16.000000953674373)
Frames from spacing: 1441

A striking feature of the LIS Log Pass 0 file is that the SP is fixed throughout at -249.709.
This value appears nowhere else in the LIS Log Pass.
The BIT file 29_10-_3Z_dwl_DWL_WIRE_1644659.bit corresponds with the following:

- The binary data is assumed to start at 0x128 + 4
- Each channel is sequential but read in blocks of 16 floats (64 bytes).
- After 16 floats are read for each channel (every 160 floats, or 640 bytes) then 12 bytes are read and discarded.
- Although the BIT file states 1441 frames from spacing the LIS file has read 1472 (0x5c0) frames (modulo 16) with the remaining values as 0.0001 for all channels.

The 12 bytes read after every 640 bytes look like this: 4 nulls, two values unknown, two nulls, two values unknown, two nulls.
These are TIF markers.

The 0.0001 figure is actually 9.999999615829415e-05 or b'\x3d\x68\xdb\x8b'

So where does the LIS file see the end of the BIT data?
Calculation shows at 0xeb70:

0000eb60: 3d68 db8b 3d68 db8b 3d68 db8b 3d68 db8b  =h..=h..=h..=h..
0000eb70: 0100 0000 e4e8 0000 7ceb 0000 0000 0000  ........|.......
0000eb80: 70eb 0000 9cec 0000 0002 0000 5348 454c  p...........SHEL
0000eb90: 4c20 4558 5052 4f20 552e 4b2e 2020 2020  L EXPRO U.K.
0000eba0: 2020 3234 204f 4354 2038 3420 2020 2020    24 OCT 84
0000ebb0: 204d 414e 5346 4945 4c44 2f44 4f44 4453   MANSFIELD/DODDS
0000ebc0: 2020 2020 2020 2020 2020 2020 2020 2020
0000ebd0: 2020 2020 000a 0018 0054 2020 3220 3920      .....T  2 9
0000ebe0: 2f20 3120 3020 2d20 3320 2020 2020 2020  / 1 0 - 3
0000ebf0: 2020 2020 2020 2020 2020 2020 2020 2020
0000ec00: 2020 2020 2020 2020 2020 2020 2020 2020
0000ec10: 2020 2020 2020 2020 2020 2020 2020 2020
0000ec20: 2020 2020 0011 002f 000d 2020 000a 0000      .../..  ....
0000ec30: 434f 4e44 534e 2020 5350 2020 4752 2020  CONDSN  SP  GR

Ah there is a TIF marker there: 0100 0000 e4e8 0000 7ceb 0000
The 0100 0000 is a EOF marker, but only one where true end of file is two type 1 markers.

TIF markers in file.

$ tddetif -n data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit -v
Cmd: /Users/paulross/pyenvs/TotalDepth_3.8_v0.3/bin/tddetif -n data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit -v
Detected 187 TIF Markers in data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit
[     0] TifMarker: 0x00000000 Type: 0x00000000 Prev: 0x00000000 Next: 0x00000120 Length: 0x00000120 Payload: 0x00000114
[     1] TifMarker: 0x00000120 Type: 0x00000000 Prev: 0x00000000 Next: 0x000003ac Length: 0x0000028c Payload: 0x00000280
[     2] TifMarker: 0x000003ac Type: 0x00000000 Prev: 0x00000120 Next: 0x00000638 Length: 0x0000028c Payload: 0x00000280
...
[    91] TifMarker: 0x0000e658 Type: 0x00000000 Prev: 0x0000e3cc Next: 0x0000e8e4 Length: 0x0000028c Payload: 0x00000280
[    92] TifMarker: 0x0000e8e4 Type: 0x00000000 Prev: 0x0000e658 Next: 0x0000eb70 Length: 0x0000028c Payload: 0x00000280
[    93] TifMarker: 0x0000eb70 Type: 0x00000001 Prev: 0x0000e8e4 Next: 0x0000eb7c Length: 0x0000000c Payload: 0x00000000
[    94] TifMarker: 0x0000eb7c Type: 0x00000000 Prev: 0x0000eb70 Next: 0x0000ec9c Length: 0x00000120 Payload: 0x00000114
[    95] TifMarker: 0x0000ec9c Type: 0x00000000 Prev: 0x0000eb7c Next: 0x0000ef28 Length: 0x0000028c Payload: 0x00000280
...
[   184] TifMarker: 0x0001cf48 Type: 0x00000000 Prev: 0x0001ccbc Next: 0x0001d1d4 Length: 0x0000028c Payload: 0x00000280
[   185] TifMarker: 0x0001d1d4 Type: 0x00000001 Prev: 0x0001cf48 Next: 0x0001d1e0 Length: 0x0000000c Payload: 0x00000000
[   186] TifMarker: 0x0001d1e0 Type: 0x00000001 Prev: 0x0001d1d4 Next: 0x0001d1ec Length: 0x0000000c Payload: 0x00000000
Execution time =    0.020 (S)
Bye, bye!

"""
import collections
import enum
import math
import os
import pprint
import string
import struct
import sys
import typing

import numpy as np

from TotalDepth.common import LogPass
from TotalDepth.util import DirWalk


from TotalDepth import ExceptionTotalDepth

class ExceptionTotalDepthBIT(ExceptionTotalDepth):
    """Simple specialisation of an exception class for TotalDepth.BIT."""
    pass


class ExceptionTotalDepthBIT_TIF(ExceptionTotalDepthBIT):
    """When TIF markers go wrong."""
    pass


class ExceptionTotalDepthBITFirstBlock(ExceptionTotalDepthBIT):
    """Constructor from first block of data."""
    pass


OFFSET_DESCRIPTION = 0x10
LENGTH_DESCRIPTION = 0xa0  # 160
# Two byte int
OFFSET_NUMBER_OF_CHANNELS = 0xb0
OFFSET_FRAME_SPACING = 0x104
OFFSET_PRE_BINARY_DATA = 0x118
OFFSET_BINARY_DATA = 0x128


ASCII_PRINTABLE_BYTES = set(
    # bytes(string.digits + string.ascii_letters + string.punctuation + ' \n\x0d\x0a', 'ascii')
    bytes(string.printable, 'ascii')
)


def is_bit_file(fobj: typing.BinaryIO) -> bool:
    """Returns True if the magic number is looks like a Western Atlas BIT file, False otherwise."""
    fobj.seek(0)
    r = fobj.read(12)
    if r[:8] == (
            b'\x00\x00'
            b'\x00\x00'
            b'\x00\x00'
            b'\x00\x00'
    ) and r[8] in ASCII_PRINTABLE_BYTES and r[9] in (0, 1) and r[10:] == b'\x00\x00':
        return True
    return False




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


def gen_floats(b: bytes) -> typing.Sequence[float]:
    """Yields a sequence of floats from the bytes."""
    offset = 0
    while len(b) > offset:
        sign = b[offset] & 0x80
        exp = b[offset] & 0x7f
        mantissa = b[offset + 1] << 16
        mantissa |= b[offset + 2] << 8
        mantissa |= b[offset + 3]
        m = mantissa / 0xffffff
        value = m * 16 ** (exp - 64)
        if sign:
            value = -value
        yield value
        offset += LEN_FLOAT_BYTES


class TifMarker(typing.NamedTuple):
    tell: int
    type: int
    prev: int
    next: int

    @property
    def length(self) -> int:
        return self.next - self.tell

    @property
    def payload_length(self):
        return self.length - 12

    def __bool__(self) -> bool:
        return self.next != 0


class TifType(enum.Enum):
    DATA = 1
    END_LOG_PASS = 2
    END_FILE = 3


class TifMarkedBytes(typing.NamedTuple):
    tif_type: TifType
    payload: bytes


TIF_WORD_STRUCT = struct.Struct('<3L')


def yield_tif_blocks(file: typing.BinaryIO) -> typing.Sequence[TifMarkedBytes]:
    file.seek(0)
    tif_prev = TifMarker(0, 0, 0, 0)
    while True:
        tell = file.tell()
        tif = TifMarker(tell, *TIF_WORD_STRUCT.unpack_from(file.read(TIF_WORD_STRUCT.size)))
        if tif_prev:
            if tif.tell != tif_prev.next:
                raise ExceptionTotalDepthBIT_TIF(f'TIF marker miss-match. Was: {tif_prev} Now: {tif}')
        else:
            # First TIF marker
            if tif.tell != 0:
                raise ExceptionTotalDepthBIT_TIF(f'First TIF marker is wrong: {tif}')
        byt = file.read(tif.payload_length)
        # Protect file position in case the caller messes with it.
        tell = file.tell()
        if tif.type == 0:
            yield TifMarkedBytes(TifType.DATA, byt)
        else:
            if tif_prev.type != 0:
                yield TifMarkedBytes(TifType.END_FILE, byt)
                break
            yield TifMarkedBytes(TifType.END_LOG_PASS, byt)
        tif_prev = tif
        # Reset the file position if the caller has messed with it.
        file.seek(tell)


class LogPassRange(typing.NamedTuple):
    depth_from: float
    depth_to: float
    spacing: float
    unknown_a: float
    unknown_b: float

    @property
    def frames(self) -> int:
        return 1 + int( 0.5 + abs(self.depth_from - self.depth_to) / abs(self.spacing))

    @property
    def is_increasing(self) -> bool:
        return self.depth_to > self.depth_from


class BITFrameArray:
    """Represents a Log Pass from a BIT file."""
    def __init__(self, ident: str, block: bytes):
        """Example initial block, length 0x114, 276 bytes::

            0000000c: 0002 0000 5348 454c 4c20 4558 5052 4f20  ....SHELL EXPRO
            0000001c: 552e 4b2e 2020 2020 2020 3234 204f 4354  U.K.      24 OCT
            0000002c: 2038 3420 2020 2020 204d 414e 5346 4945   84      MANSFIE
            0000003c: 4c44 2f44 4f44 4453 2020 2020 2020 2020  LD/DODDS
            0000004c: 2020 2020 2020 2020 2020 2020 000a 0018              ....
            0000005c: 0054 2020 3220 3920 2f20 3120 3020 2d20  .T  2 9 / 1 0 -
            0000006c: 3320 2020 2020 2020 2020 2020 2020 2020  3
            0000007c: 2020 2020 2020 2020 2020 2020 2020 2020
            0000008c: 2020 2020 2020 2020 2020 2020 2020 2020
            0000009c: 2020 2020 2020 2020 2020 2020 0012 000b              ....
            000000ac: 0006 2020 000a 0000 434f 4e44 534e 2020  ..  ....CONDSN
            000000bc: 5350 2020 4752 2020 4341 4c20 5445 4e20  SP  GR  CAL TEN
            000000cc: 5350 4420 4143 5120 4143 2020 5254 2020  SPD ACQ AC  RT
            000000dc: 2020 2020 2020 2020 2020 2020 2020 2020
            000000ec: 2020 2020 2020 2020 2020 2020 2020 2020
            000000fc: 2020 2020 2020 2020 443a 6600 4438 fe00          D:f.D8..
            0000010c: 4040 0000 0000 0000 4210 0000 4d4e 3233  @@......B...MN23
            0000011c: 394a 2031

        """
        self.ident = ident
        offset = 0
        self.unknown_head = block[offset:offset + 4]
        offset += 4
        self.description = block[offset:offset + 160]
        offset += 160
        count = struct.unpack('>h', block[offset:offset + 2])[0]
        if count > 20:
            raise ValueError(f'Channel count must be <= 20 not {count}')
        offset += 2
        null = struct.unpack('>h', block[offset:offset + 2])[0]
        if null != 0:
            raise ValueError(f'Expected null at 0x{offset:x} but got {null}')
        offset += 2
        self.channel_names: typing.List[str] = []
        for i in range(count):
            self.channel_names.append(block[offset:offset + 4].decode('ascii'))
            offset += 4
        # Unused channels
        offset += 4 * (20 - count)
        _temp: typing.List[float] = []
        for i in range(5):
            _temp.append(bytes_to_float(block[offset:]))
            offset += 4
        self.bit_log_pass_range = LogPassRange(*_temp)
        self.unknown_tail = block[offset:]
        self.frame_count = 0
        self._temporary_frames: typing.List[typing.List[float]] = [list() for c in self. channel_names]
        self.frame_array: typing.Optional[LogPass.LogPass] = None

    def long_str(self) -> str:
        """Returns a multi-line string describing self."""
        ret = [
            f'BITFrameArray: ident="{self.ident}"',
            f'   Unknown head: {self.unknown_head}',
            f'    Description: {self.description}',
            f'  Channels [{len(self.channel_names):2}]: {self.channel_names}',
            f'   BIT Log Pass: {self.bit_log_pass_range}',
            f'   Unknown tail: {self.unknown_tail}',
            f'    Frame count: {self.frame_count}',
            f'    Frame array: {self.frame_array}',
        ]
        return '\n'.join(ret)


    @property
    def len_channels(self) -> int:
        return len(self.channel_names)

    def add_block(self, block: bytes) -> None:
        if len(block) % self.len_channels:
            raise ValueError(
                f'The block length {len(block)} does not have equal data for the channels {self.len_channels}.'
            )
        num_frames = len(block) // (LEN_FLOAT_BYTES * self.len_channels)
        for i, value in enumerate(gen_floats(block)):
            # Note: frame_number = i % num_frames
            channel_number = i // num_frames
            self._temporary_frames[channel_number].append(value)
        self.frame_count += num_frames

    def complete(self) -> None:
        """Converts the existing frame data to a LogPass.FrameArray, adds a computed X-axis and removes temporaries."""
        assert self.frame_array is None
        if len(self._temporary_frames):
            assert len(self.channel_names) == len(self._temporary_frames)
            self.frame_array = LogPass.FrameArray(self.ident, self.description)
            # Compute X axis
            x_channel = LogPass.FrameChannel(b'DEPT', 'Computed Depth', b'', (1,), np.float64)
            x_channel.init_array(self.frame_count)
            x_value = self.bit_log_pass_range.depth_from
            for i in range(self.frame_count):
                x_channel[i] = x_value
                if self.bit_log_pass_range.is_increasing:
                    x_value += self.bit_log_pass_range.spacing
                else:
                    x_value -= self.bit_log_pass_range.spacing
            self.frame_array.append(x_channel)
            for c, channel_name in enumerate(self.channel_names):
                frame_channel = LogPass.FrameChannel(channel_name, channel_name, b'', (1,), np.float64)
                frame_channel.init_array(len(self._temporary_frames[c]))
                for i in range(len(self._temporary_frames[c])):
                    frame_channel[i] = self._temporary_frames[c][i]
                self.frame_array.append(frame_channel)
            for data in self._temporary_frames:
                data.clear()
            self._temporary_frames.clear()

# class Signature(typing.NamedTuple):
#     signature: bytes  # 12 bytes
#     unknown: float
#
#
# def read_signature_from_file(file: typing.BinaryIO) -> Signature:
#     file.seek(0)
#     b = file.read(12)
#     u = read_float(file)
#     return Signature(b, u)


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
    # if null != 0:
    #     raise ValueError(f'Expected null at 0x{file.tell():x} but got {null}')
    ret = []
    for i in range(count):
        ret.append(file.read(4).decode('ascii'))
    return ret


def read_description_from_file(file: typing.BinaryIO) -> str:
    file.seek(OFFSET_DESCRIPTION)
    ret = file.read(LENGTH_DESCRIPTION)
    return ret.decode('ascii')




class PreBinaryData(typing.NamedTuple):
    pad: bytes  # 8 bytes
    null: bytes  # 8 bytes


def read_pre_binary_data_from_file(file: typing.BinaryIO) -> PreBinaryData:
    file.seek(OFFSET_PRE_BINARY_DATA)
    a = file.read(8)
    b = file.read(8)
    return PreBinaryData(a, b)


def read_binary_data_from_file(file: typing.BinaryIO, limit: int = 0) -> typing.List[float]:
    ret = []
    file.seek(OFFSET_BINARY_DATA)
    unknown = read_float(file)
    while True:
        t = file.tell()
        b = file.read(LEN_FLOAT_BYTES)
        if len(b) != LEN_FLOAT_BYTES:
            break
        try:
            ret.append(bytes_to_float(b))
        except ValueError as err:
            print(f'ERROR: {err} at 0x{t:x}')
        if limit and len(ret) >= limit:
            break
    return ret


def read_binary_data_from_file_new(file: typing.BinaryIO,
                                   channels: typing.List[str],
                                   block_size: int,
                                   limit: int = 0) -> typing.List[typing.List[float]]:
    ret = [list() for c in channels]
    file.seek(OFFSET_BINARY_DATA)
    unknown = read_float(file)
    channel_index = 0
    count = 0
    while True:
        for i in range(block_size):
            t = file.tell()
            b = file.read(LEN_FLOAT_BYTES)
            if len(b) != LEN_FLOAT_BYTES:
                return ret
            ret[channel_index % len(channels)].append(bytes_to_float(b))
            count += 1
            if limit and count >= limit:
                return ret
        channel_index += 1
        if channel_index % len(channels) == 0:
            # Read three values
            # unknown_three = [read_float(file) for j in range(3)]
            # print(f'Unknown three: {unknown_three}')
            b = file.read(12)
            out = ', '.join([f'{v:3d}' for v in b])
            print(f'Unknown 12 bytes: {out}')
    return ret


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
    # all_as_floats = read_file_path_as_floats(file_path)
    # print(f'Read {len(all_as_floats)} floats.')
    # print('First 16 bytes:')
    # pprint.pprint(all_as_floats[:4])
    # print('From 0x104')
    # # Looks like (from, to spacing) in feet.
    # # Followed by 0.0, 125.0
    # pprint.pprint(all_as_floats[16 * 4 + 1:16 * 4 + 1 + 32])
    # print('...')
    # print('Last frame of 64:')
    # pprint.pprint(all_as_floats[-(64 + 6):-6])
    # print('Last 24 bytes:')
    # pprint.pprint(all_as_floats[-6:])
    #
    # print()
    # for i in range(0, len(all_as_floats), 8):
    #     f_slice = all_as_floats[i:i + 8]
    #     print(' '.join([f'{f:12.3f}' for f in f_slice]))

    print(f'File: {file_path}')
    print(f'Size: {os.path.getsize(file_path):d} 0x{os.path.getsize(file_path):x}')
    with open(file_path, 'rb') as file:
        print(f'           Signature: {read_signature_from_file(file)}')
        print(f'         Description: "{read_description_from_file(file)}"')
        channels = read_channels_from_file(file)
        print(f'       Channels [{len(channels):2d}]: {channels}')
        frame_spacing = read_frame_spacing_from_file(file)
        print(f'             Spacing: {frame_spacing}')
        print(f' Frames from spacing: {frame_spacing.frames}')
        print(f'     Bytes per frame: {LEN_FLOAT_BYTES * len(channels)}')
        len_expected_binary_data = LEN_FLOAT_BYTES * len(channels) * frame_spacing.frames
        print(f'Bytes of binary data: {len_expected_binary_data:d} 0x{len_expected_binary_data:x}')
        print(f'    Expected trailer: 0x{len_expected_binary_data + OFFSET_BINARY_DATA:x}')
        print(f'     Pre-binary data: {read_pre_binary_data_from_file(file)}')
        limit = len(channels) * frame_spacing.frames
        limit = 1472 * 10
        print(f'          Limit used: {limit}')
        binary_data_floats = read_binary_data_from_file(file, limit=limit)
        binary_data_floats_new = read_binary_data_from_file_new(file, channels, block_size=16, limit=limit)
        print(f'Count of binary data: {len(binary_data_floats_new)}')
        print(f'     Count of frames: {len(binary_data_floats_new) / len(channels)}')
        # print('Frames:')
        # for f in range(8):
        #     f_slice = binary_data_floats[f * len(channels):(f + 1) * len(channels)]
        #     print(' '.join([f'{f:12.3f}' for f in f_slice]))

        # # Transpose the binary data
        # channel_data = []
        # for c in range(len(channels)):
        #     channel_data.append(binary_data_floats[c * bit_log_pass_range.frames:(c + 1) * bit_log_pass_range.frames])
        # print('Transposed frames:')
        # for c, channel in enumerate(channel_data):
        #     print(
        #         channels[c],
        #         ' '.join([f'{f:12.3f}' for f in channel[:8]]),
        #         ' -> ',
        #         ' '.join([f'{f:12.3f}' for f in channel[-8:]])
        #     )

        # prev_i = 0
        # run_count = 0
        # for i, value in enumerate(binary_data_floats):
        #     if value_of_interest(value):
        #         print(f'{i:8d} {i - prev_i:+8d} {run_count:+8d} {value:16.8g}')
        #         if i - prev_i == 1:
        #             run_count += 1
        #         else:
        #             run_count = 0
        #             i_run_start = i
        #         prev_i = i

        # for i in range(1, len(binary_data_floats) - 1, 1):
        #     if value_of_interest(binary_data_floats[i-1]) or value_of_interest(binary_data_floats[i]) or value_of_interest(binary_data_floats[i+1]):
        #         print(f'{i:8d} {binary_data_floats[i]:16.8f}')
        # for i in range(0, len(binary_data_floats), 1):
        #     if value_of_interest(binary_data_floats[i]):
        #         print(f'{i:8d} {binary_data_floats[i]:16.8f}')
        #
        # # Look for frame spacing
        # for i in range(1, len(binary_data_floats), 1):
        #     diff = abs(binary_data_floats[i] - binary_data_floats[i - 1])
        #     if math.isclose(diff, bit_log_pass_range.spacing):
        #         print('Frame spacing', i, diff)

        # print(binary_data_floats[:8])
        # print(binary_data_floats[-8:])
        for c in range(len(channels)):
            print(
                channels[c],
                len(binary_data_floats_new[c]),
                # binary_data_floats_new[c][:4],
                # ', '.join(f'{v:10.4f}' for v in binary_data_floats_new[c][:16]),
                # '->',
                # binary_data_floats_new[c][-4:]
                # ', '.join(f'{v:10.4f}' for v in binary_data_floats_new[c][-16:]),
            )
            print(', '.join(f'{v:10g}' for v in binary_data_floats_new[c][:16]))
            print(', '.join(f'{v:10g}' for v in binary_data_floats_new[c][-16:]))
            # histogram_floats = collections.Counter()
            # histogram_floats.update(binary_data_floats_new[c])
            # pprint.pprint(histogram_floats.most_common(100))


        total = 0
        for c in range(len(channels)):
            count = 0
            for i, value in enumerate(binary_data_floats_new[c]):
                if value_of_interest(value):
                    count += 1
            print(f'{channels[c]}: {count}')
            total += count
        print(total)

        for thing in yield_tif_blocks(file):
            print(thing)


def value_of_interest(value: float) -> bool:
    # return False
    return value == -249.70902977639614
    return 1600.0 < value < 1700.0


def dump_path_bytes(file_path: str) -> None:
    with open(file_path, 'rb') as file:
        pprint.pprint(file.read())


def dump_selected_bytes(directory: str, offset: int, length: int) -> None:
    for file_in_out in DirWalk.dirWalk(directory, '', theFnMatch='*.bit', recursive=True):
        with open(file_in_out.filePathIn, 'rb') as file:
            if offset > 0:
                file.seek(offset)
            else:
                file.seek(offset, os.SEEK_END)
            print(f'{os.path.basename(file_in_out.filePathIn):40} : {list(file.read(length))}')


def create_bit_frame_array_from_file(file: typing.BinaryIO) -> typing.List[BITFrameArray]:
    log_pass = []
    frame_array = None
    for tif_block in yield_tif_blocks(file):
        if tif_block.tif_type == TifType.END_FILE:
            break
        if frame_array is None:
            assert tif_block.tif_type == TifType.DATA
            frame_array = BITFrameArray(f'{len(log_pass)}', tif_block.payload)
        else:
            if tif_block.tif_type == TifType.DATA:
                frame_array.add_block(tif_block.payload)
            elif tif_block.tif_type == TifType.END_LOG_PASS:
                frame_array.complete()
                log_pass.append(frame_array)
                frame_array = None
    return log_pass


def create_bit_frame_array(file_path: str) -> typing.List[BITFrameArray]:
    # print(f'File: {file_path}')
    # print(f'Size: {os.path.getsize(file_path):d} 0x{os.path.getsize(file_path):x}')
    with open(file_path, 'rb') as file:
        ret = create_bit_frame_array_from_file(file)
    return ret






def main() -> int:
    example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/456728/30_07a-_1/DWL_FILE/30_07a-_1_dwl_DWL_WIRE_1644802.bit'
    # example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/456728/30_07a-_1/DWL_FILE/30_07a-_1_dwl_DWL_WIRE_1644822.bit'
    # example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/456728/30_07a-_1/DWL_FILE/30_07a-_1_dwl_DWL_WIRE_1644825.bit'
    # example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/456728/30_07a-_1/DWL_FILE/30_07a-_1_dwl_DWL_WIRE_1644826.bit'
    # # Smallest at 9kb
    # example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/456728/15_17-_12/DWL_FILE/15_17-_12_dwl__1646505.bit'
    # # 12kb
    example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/456728/21_25-B1/DWL_FILE/21_25-B1_dwl_DWL_WIRE_1644592.bit'
    # # 6Mb
    # example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/456728/15_10-_1/DWL_FILE/15_10-_1_dwl__1645815.bit'

    # Has LIS file
    # -rw-r--r--  1 paulross  staff  1004032 30 Jan 14:57 data/DresserAtlasBIT/special/29_10-_3/DWL_FILE/29_10-_3_dwl_DWL_WIRE_1646632.bit
    # -rw-r--r--  1 paulross  staff   513536 30 Jan 14:57 data/DresserAtlasBIT/special/29_10-_3/DWL_FILE/29_10-_3_dwl_DWL_WIRE_1646636.bit
    example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/special/29_10-_3/DWL_FILE/29_10-_3_dwl_DWL_WIRE_1646632.bit'
    # example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/special/29_10-_3/DWL_FILE/29_10-_3_dwl_DWL_WIRE_1646636.bit'

    example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit'
    # example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644660.bit'
    # 30_07a-_1_dwl_DWL_WIRE_1644802.bit
    # 30_07a-_1_dwl_DWL_WIRE_1644822.bit
    # 30_07a-_1_dwl_DWL_WIRE_1644823.bit
    # 30_07a-_1_dwl_DWL_WIRE_1644825.bit
    # 30_07a-_1_dwl_DWL_WIRE_1644826.bit
    # 30_07a-_1_dwl_DWL_WIRE_1644827.bit
    # 30_07a-_1_dwl_DWL_WIRE_1644828.bit

    # dump_path_bytes(example)
    # dump_path_structure(example)

    log_pass = create_bit_frame_array(example)
    for array in log_pass:
        print(array.long_str())

    # dump_selected_bytes('/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/456728', 0, 16)
    # dump_selected_bytes('/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/456728', 0x104, 16)
    # dump_selected_bytes('/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/456728', -24, 24)

    return 0


if __name__ == '__main__':
    sys.exit(main())
