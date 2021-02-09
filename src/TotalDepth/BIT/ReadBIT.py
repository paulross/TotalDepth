#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation
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
This processes Dresser Atlas BIT files.
Dresser Atlas BIT files are TIF encoded and consist of a set of Log Passes:

- First block, this gives a description of the file.
- Subsequent blocks are frame data.

TIF markers are used to separate Log Passes and delineate the file.
A TIF marker type 1 ends the Log Pass and a pair of type 1 markers ends the readable file.

Here is an example of TIF markers in a file::

    $ tddetif -n data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit -v
    Cmd: DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit -v
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


Example first block without TIF markers, length 276 (0x114) bytes::

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

Decomposed:

- 4 bytes unknown.
- 160 bytes ASCII description, there is some structure here but it is as yet unknown.
- C, the count of channels as big endian two byte format '>H' or '>h'.
- A two byte null
- Channel names, 4 bytes each, this is always 80 bytes long.
- Five 4 byte floats start, stop, step, 0, ???.
- Unknown tail of eight bytes.

Total = 4 + 160 + 2 + 2 + 80 + 5 * 4 + 8 = 276 (0x114) bytes.

Of note is that while the TIF markers are little endian many values within the file are big endian.

Decoding the Description
-------------------------

This is 160 bytes long.
Example::

    $ xxd -s +16 data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit | head -n 20
    00000010: 5348 454c 4c20 4558 5052 4f20 552e 4b2e  SHELL EXPRO U.K.
    00000020: 2020 2020 2020 3234 204f 4354 2038 3420        24 OCT 84
    00000030: 2020 2020 204d 414e 5346 4945 4c44 2f44       MANSFIELD/D
    00000040: 4f44 4453 2020 2020 2020 2020 2020 2020  ODDS
    00000050: 2020 2020 2020 2020 000a 0018 0054 2020          .....T
    00000060: 3220 3920 2f20 3120 3020 2d20 3320 2020  2 9 / 1 0 - 3
    00000070: 2020 2020 2020 2020 2020 2020 2020 2020
    00000080: 2020 2020 2020 2020 2020 2020 2020 2020
    00000090: 2020 2020 2020 2020 2020 2020 2020 2020
    000000a0: 2020 2020 2020 2020 0012 000b 0006 2020          ......
    000000b0: 000a 0000 434f 4e44 534e 2020 5350 2020  ....CONDSN  SP

Looks like we have 4 * 16 + 8 = 72 bytes of ASCII to 0x58 as a description.

Either:

Then 24 bytes of binary data to 0x70 ???::

    000a 0018 0054 2020 3220 3920 2f20 3120 3020 2d20 3320 2020

3 * 16 + 8 = 56 ASCII spaces.
hmm divided by 4 is 19.
hmm maybe together 24 + 56 = 80 and 80 / 4 is 20. Channel units?

Then 8 bytes of stuff: 0012 000b 0006 2020

Total is:
72 + 24 + 56 + 8 == 160

Or, alternatively:
72 (4 * 16 + 8) bytes of ASCII.
Then five bytes: 000a 0018 00
Then 75 bytes of ASCII: 54 2020 3220 3920 2f20 3120 3020 2d20 3320 2020 ...
Then 8 bytes of stuff: 0012 000b 0006 2020
Total is:
72 + 5 + 75 + 8 == 160

Decoding the frames
-------------------

Each subsequent block is a subdivided into the number of channels and read into that channel.
For example a block of data 0x280 (640) bytes long with 10 channels is decomposed into 10 sub-blocks of 64 bytes each.
Each sub-block contains 16 floats.

There is a directory that has both BIT and LIS files in it.

LIS: 29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1988494.lis
BIT: 29_10-_3Z_dwl_DWL_WIRE_1644659.bit and 29_10-_3Z_dwl_DWL_WIRE_1644660.bit

Log Pass 0 has X axis:
14950.000 (FT) to 14582.250 (FT) Interval -367.750 (FT)
Total number of frames	1472
Overall frame spacing	-0.250 (FT)

Corresponding BIT file 29_10-_3Z_dwl_DWL_WIRE_1644659.bit has::

    LogPassRange(depth_from=14950.000891089492, depth_to=14590.000869631818, spacing=0.2500000149011621, unknown_a=0.0,
    unknown_b=16.000000953674373)

Frames from spacing: 1441

A striking feature of the LIS Log Pass 0 file is that the SP is fixed throughout at -249.709.
This value appears nowhere else in the LIS Log Pass.
The BIT file 29_10-_3Z_dwl_DWL_WIRE_1644659.bit corresponds with the following:

- The binary data is assumed to start at 0x128 + 4
- Each channel is sequential but read in blocks of 16 floats (64 bytes).
- After 16 floats are read for each channel (every 160 floats, or 640 bytes) then 12 bytes are read and discarded.
- Although the BIT file states 1441 frames from spacing the LIS file has read 1472 (0x5c0) frames (modulo 16) with the
   remaining values as 0.0001 for all channels.

The 12 bytes read after every 640 bytes look like this: 4 nulls, two values unknown, two nulls, two values unknown,
two nulls.
These are TIF markers.

The 0.0001 figure is actually 9.999999615829415e-05 or b'\x3d\x68\xdb\x8b'
"""
import enum
import logging
import math
import os
import string
import struct
import sys
import time
import typing

import numpy as np

from TotalDepth.common import LogPass, cmn_cmd_opts, np_summary
from TotalDepth.util import DirWalk


__rights__  = 'Copyright (c) 2021 Paul Ross. All rights reserved.'
__version__ = '0.1.0'


logger = logging.getLogger(__file__)


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


class ExceptionTotalDepthBITDataBlocks(ExceptionTotalDepthBIT):
    """Constructor from first block of data."""
    pass


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
    m = mantissa / 0x1000000
    ret = m * 16**(exp - 64)
    if sign:
        return -ret
    return ret


def float_to_bytes(f: float) -> bytes:
    """Returns four bytes from a float.

    https://en.wikipedia.org/wiki/IBM_hexadecimal_floating-point

    Example: b'\xc2\x76\xa0\x00' -> -118.625

    NOTE: This is the same as RP66V1 ISINGL (5) Representation Code.
    """
    if math.isnan(f):
        raise ValueError('Can not represent a NaN.')
    # # From RP66V2 documentation: "Bits 8-5 of byte 2 may not be all zero except for true zero.
    # if b[1] & 0xf0 == 0 and b != b'\x00\x00\x00\x00':
    #     raise ValueError(f'Bytes representation {b} is illegal.')

    # >>> math.frexp(-118.625) is (-0.9267578125, 7)
    m, e = math.frexp(f)
    if e % 4:
        # Round to power of 16 (2**4)
        power = 4 - (e % 4)
        m /= 2**power
        e += power
    mantissa = int(0x1000000 * abs(m))
    if mantissa != 0:
        assert e % 4 == 0
        exponent = e // 4 + 64
        if exponent < 0:
            exponent = 0
        if exponent > 0x7f:
            exponent = 0x7f
        # Sign bit
        if m < 0:
            exponent |= 0x80
    else:
        exponent = 0
    ret = bytes([exponent, mantissa >> 16 & 0xff, mantissa >> 8 & 0xff, mantissa & 0xff, ])
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


ASCII_PRINTABLE_BYTES = set(
    # bytes(string.digits + string.ascii_letters + string.punctuation + ' \n\x0d\x0a', 'ascii')
    bytes(string.printable, 'ascii')
)


def is_bit_file(fobj: typing.BinaryIO) -> bool:
    """Returns True the file looks like a Western Atlas BIT file, False otherwise."""
    fobj.seek(0)
    tif = TifMarker(fobj.tell(), *TIF_WORD_STRUCT.unpack_from(fobj.read(TIF_WORD_STRUCT.size)))
    if tif:
        _unknown_head = fobj.read(4)
        r = fobj.read(160)
        if len(r) < 160:
            return False
        if any(v not in ASCII_PRINTABLE_BYTES for v in r[:72]):
            return False
        if any(v not in ASCII_PRINTABLE_BYTES for v in r[72 + 24:72 + 24 + 56]):
            return False
        count = struct.unpack('>H', fobj.read(2))[0]
        if count > 20:
            return False
        null = struct.unpack('>H', fobj.read(2))[0]
        # if null != 0:
        #     return False
        for i in range(count):
            name = fobj.read(4)
            if any(v not in ASCII_PRINTABLE_BYTES for v in name):
                return False
        return True
    return False


def is_bit_file_from_path(file_path: str) -> bool:
    """Returns True the file looks like a Western Atlas BIT file, False otherwise."""
    with open(file_path, 'rb') as file:
        return is_bit_file(file)


class TifMarker(typing.NamedTuple):
    """Contains a TIF marker with its file position."""
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
    """Type of TIF marker. Type 0 is normal data. Type 1 is end of Log Pass. Type 2 is end of file."""
    DATA = 1
    END_LOG_PASS = 2
    END_FILE = 3


class TifMarkedBytes(typing.NamedTuple):
    """This is yielded by yield_tif_blocks()."""
    tell: int
    tif_type: TifType
    payload: bytes


TIF_WORD_STRUCT = struct.Struct('<3L')


def yield_tif_blocks(file: typing.BinaryIO) -> typing.Sequence[TifMarkedBytes]:
    """Generate the payload from blocks of the file."""
    file.seek(0)
    tif_prev = TifMarker(0, 0, 0, 0)
    while True:
        tell = file.tell()
        tif_bytes = file.read(TIF_WORD_STRUCT.size)
        if len(tif_bytes) < TIF_WORD_STRUCT.size:
            # Premature EOF, just handle it silently.
            yield TifMarkedBytes(tell, TifType.END_FILE, b'')
            break
        tif = TifMarker(tell, *TIF_WORD_STRUCT.unpack_from(tif_bytes))
        # print(tif, tif_prev)
        if tif_prev:
            if tif.tell != tif_prev.next:
                raise ExceptionTotalDepthBIT_TIF(f'TIF marker miss-match. Was: {tif_prev} Now: {tif}')
        else:
            # First TIF marker
            if tif.tell != 0:
                raise ExceptionTotalDepthBIT_TIF(f'First TIF marker is wrong: {tif}')
        byt = file.read(tif.payload_length)
        # Protect file position in case the caller messes with it.
        pre_yield_tell = file.tell()
        if tif.type == 0:
            yield TifMarkedBytes(tell, TifType.DATA, byt)
        else:
            if tif_prev.type != 0:
                yield TifMarkedBytes(tell, TifType.END_FILE, byt)
                break
            yield TifMarkedBytes(tell, TifType.END_LOG_PASS, byt)
        tif_prev = tif
        # Reset the file position if the caller has messed with it.
        file.seek(pre_yield_tell)


class LogPassRange(typing.NamedTuple):
    """POD container for the five floats that describe the range of the BIT Log Pass."""
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


def read_bytes_from_offset(b: bytes, count: int, offset: int) -> typing.Tuple[bytes, int]:
    """Slices a bytes object and increments the offset.
    Usage::

        result, offset = read_bytes_from_offset(b, count, offset)
    """
    if len(b) < offset + count:
        raise ValueError(f'Can not read {count} bytes from offset {offset} when byte length is {len(b)}')
    return b[offset:offset + count], offset + count


class BITFrameArray:
    """Represents a Log Pass from a BIT file.
    This has a number of fields, some are BIT specific but ``self.frame_array`` is a
    :py:class:`TotalDepth.common.LogPass.FrameArray`.
    """
    def __init__(self, ident: str, tif_block: TifMarkedBytes):
        """Example initial block, length 0x114, 276 bytes:

        .. code-block:: console

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
        block: bytes = tif_block.payload
        # self.unknown_head = block[offset:offset + 4]
        # offset += 4
        self.unknown_head, offset = read_bytes_from_offset(block, 4, offset)
        assert offset == 4
        # TODO:
        # Looks like we have 4 * 16 + 8 = 72 bytes of ASCII to 0x58 as a description.
        #
        # Then 24 bytes of binary data to 0x70 ???
        #     000a 0018 0054 2020 3220 3920 2f20 3120 3020 2d20 3320 2020
        # 3 * 16 + 8 = 56 ASCII spaces.
        # hmm divided by 4 is 19.
        # hmm maybe together 24 + 56 = 80 and 80 / 4 is 20. Channel units?
        #
        # Then 8 bytes of stuff: 0012 000b 0006 2020
        #
        # Total is:
        # 72 + 24 + 56 + 8 == 160
        # self.description = block[offset:offset + 160]
        # offset += 160
        # self.description, offset = read_bytes_from_offset(block, 160, offset)

        # 72 (4 * 16 + 8) bytes of ASCII.
        # Then five bytes: 000a 0018 00
        # Then 75 bytes of ASCII: 54 2020 3220 3920 2f20 3120 3020 2d20 3320 2020 ...
        # Then 8 bytes of stuff: 0012 000b 0006 2020
        # Total is:
        # 72 + 5 + 75 + 8 == 160

        self.description, offset = read_bytes_from_offset(block, 72, offset)
        self.unknown_a, offset = read_bytes_from_offset(block, 5, offset)
        self.unknown_b, offset = read_bytes_from_offset(block, 75, offset)
        self.unknown_c, offset = read_bytes_from_offset(block, 8, offset)
        assert offset == 160 + 4

        count = struct.unpack('>H', block[offset:offset + 2])[0]
        if count > 20:
            raise ExceptionTotalDepthBITFirstBlock(
                f'BITFrameArray: Channel count must be <= 20 not {count} TIF tell 0x{tif_block.tell}'
            )
        offset += 2
        null = struct.unpack('>H', block[offset:offset + 2])[0]
        if null != 0:
            logger.warning(
                f'BITFrameArray: Expected null at offset 0x{offset:x} but got value 0x{null:x}'
                f' TIF tell 0x{tif_block.tell}'
            )
        offset += 2
        self.channel_names: typing.List[str] = []
        for i in range(count):
            name, offset = read_bytes_from_offset(block, 4, offset)
            self.channel_names.append(name.decode('ascii'))
        # Unused channels
        offset += 4 * (20 - count)
        _temp: typing.List[float] = []
        for i in range(5):
            value, offset = read_bytes_from_offset(block, 4, offset)
            _temp.append(bytes_to_float(value))
        self.bit_log_pass_range = LogPassRange(*_temp)
        self.unknown_tail = block[offset:]
        self.frame_count = 0
        self._temporary_frames: typing.List[typing.List[float]] = [list() for c in self.channel_names]
        self.frame_array: typing.Optional[LogPass.FrameArray] = None

    def long_str(self) -> str:
        """Returns a multi-line string describing self."""
        frame_array_str = '\n'.join(f'      {v}' for v in str(self.frame_array).split('\n'))
        ret = [
            f'BITFrameArray: ident="{self.ident}"',
            f'   Unknown head: {self.unknown_head}',
            f'    Description: {self.description}',
            f'      Unknown A: {self.unknown_a}',
            f'      Unknown B: {self.unknown_b}',
            f'      Unknown C: {self.unknown_c}',
            f'  Channels [{len(self.channel_names):2}]: {self.channel_names}',
            f'   BIT Log Pass: {self.bit_log_pass_range}',
            f'   Unknown tail: {self.unknown_tail}',
            f'    Frame count: {self.frame_count}',
            f'    Frame array: {frame_array_str}',
        ]
        return '\n'.join(ret)


    @property
    def len_channels(self) -> int:
        return len(self.channel_names)

    def add_block(self, block: bytes) -> None:
        """Adds a data block of frame data to my temporary data structure(s)."""
        if self.len_channels == 0:
            logger.warning(f'Ignoring block of length {len(block)} when no channels.')
        else:
            assert len(self.channel_names) == len(self._temporary_frames), f'{len(self.channel_names)} != {len(self._temporary_frames)}'
            if len(block) % self.len_channels:
                raise ExceptionTotalDepthBITDataBlocks(
                    f'The block length {len(block)} does not have equal data for the channels {self.len_channels}.'
                )
            num_frames = len(block) // (LEN_FLOAT_BYTES * self.len_channels)
            remainder_bytes = len(block) - (LEN_FLOAT_BYTES * num_frames * self.len_channels)
            # if len(block) % (LEN_FLOAT_BYTES * self.len_channels):
            if remainder_bytes:
                logger.warning(
                    f'Frame mismatch, byte_len={len(block)} channels={self.len_channels} num_frames={num_frames}'
                    f' Remaining bytes={remainder_bytes} ignored values={remainder_bytes / LEN_FLOAT_BYTES}'
                )
            for i, value in enumerate(gen_floats(block)):
                if i >= num_frames * self.len_channels:
                    logger.warning(
                        f'Ignoring surplus values. Remaining bytes={remainder_bytes}'
                        f' ignored values={remainder_bytes / LEN_FLOAT_BYTES}'
                    )
                    break
                # Note: frame_number = i % num_frames
                channel_number = i // num_frames
                assert channel_number < len(self._temporary_frames), f'{channel_number} >= {len(self._temporary_frames)} byte len={len(block)} i={i} channels={self.len_channels} num_frames={num_frames}'
                self._temporary_frames[channel_number].append(value)
            self.frame_count += num_frames

    def complete(self) -> None:
        """Converts the existing frame data to a LogPass.FrameArray.
        This adds a computed X-axis and removes temporary data structures."""
        assert self.frame_array is None
        if len(self._temporary_frames):
            assert len(self.channel_names) == len(self._temporary_frames)
            self.frame_array = LogPass.FrameArray(self.ident, self.description)
            # Compute X axis
            x_channel = LogPass.FrameChannel('X   ', 'Computed X-axis', b'', (1,), np.float64)
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


def create_bit_frame_array_from_file(file: typing.BinaryIO) -> typing.List[BITFrameArray]:
    """Given a file this returns a list of BITFrameArray objects."""
    log_pass = []
    bit_frame_array: typing.Optional[BITFrameArray] = None
    for tif_block in yield_tif_blocks(file):
        if tif_block.tif_type == TifType.END_FILE:
            break
        if bit_frame_array is None:
            if tif_block.tif_type == TifType.END_LOG_PASS:
                logger.warning(f'Ignoring out of place TifType.END_LOG_PASS TIF tell 0x{tif_block.tell:x}')
                continue
            if tif_block.tif_type != TifType.DATA:
                raise ExceptionTotalDepthBITDataBlocks(f'TIF block {tif_block.tif_type} != TIF DATA {TifType.DATA}')
            # assert tif_block.tif_type == TifType.DATA, f'{tif_block.tif_type} != {TifType.DATA}'
            bit_frame_array = BITFrameArray(f'{len(log_pass)}', tif_block)
        else:
            if tif_block.tif_type == TifType.DATA:
                try:
                    bit_frame_array.add_block(tif_block.payload)
                except ExceptionTotalDepthBITDataBlocks as err:
                    logger.warning(f'{str(err)} at tell=0x{file.tell():x}. Ignoring rest of file.')
                    break
            elif tif_block.tif_type == TifType.END_LOG_PASS:
                bit_frame_array.complete()
                log_pass.append(bit_frame_array)
                bit_frame_array = None
    # If there is an exception frame_array may be non-None.
    if bit_frame_array is not None:
        bit_frame_array.complete()
        log_pass.append(bit_frame_array)
    return log_pass


def create_bit_frame_array_from_path(file_path: str) -> typing.List[BITFrameArray]:  # pragma: no cover
    """Given a file path this returns a list of BITFrameArray objects or raises."""
    with open(file_path, 'rb') as file:
        ret = create_bit_frame_array_from_file(file)
    return ret


class FileSizeTime(typing.NamedTuple):  # pragma: no cover
    name: str
    size: int
    time: float

    def __str__(self):
        return f'{self.size:12d} {self.time:12.3f} {self.time * 1000 / (self.size / 1024**2):12.3f} {self.name}'


def print_summarise_frame_array(frame_array: BITFrameArray) -> None:
    """Summarise all the channels in the Frame Array."""
    print(f'{"ID":4}', np_summary.ArraySummary.str_header())
    for channel in frame_array.frame_array.channels:
        summary = np_summary.summarise_array(channel.array)
        if summary is None:
            print(f'{channel.ident:4} No Summary.')
        else:
            print(f'{channel.ident:4}', summary.str())


def print_process_file(file_path: str, verbose: int, summary: bool) -> FileSizeTime:  # pragma: no cover
    """Process a BIT file and print out a summary."""
    logger.info(f'Processing: {file_path} ')
    t_start = time.perf_counter()
    frame_arrays = create_bit_frame_array_from_path(file_path)
    if verbose:
        print(f'File size: {os.path.getsize(file_path):d} 0x{os.path.getsize(file_path):x}: {file_path} ')
        print(f' {os.path.basename(file_path)} '.center(75, '='))
        for i, frame_array in enumerate(frame_arrays):
            print(f' Frame Array [{i}] '.center(75, '-'))
            print(frame_array.long_str())
            if summary:
                if frame_array.frame_array is None:
                    print('No summary as no Frame Array initialised.')
                else:
                    print_summarise_frame_array(frame_array)
            print(f' DONE: Frame Array [{i}] '.center(75, '-'))
        print(f' DONE {os.path.basename(file_path)} '.center(75, '='))
    return FileSizeTime(file_path, os.path.getsize(file_path), time.perf_counter() - t_start)


def print_process_directory(directory: str,
                            recursive: bool,
                            verbose: int,
                            summary: bool) -> typing.Dict[str, FileSizeTime]:  # pragma: no cover
    """Processes a complete directory for BIT files."""
    ret = {}
    count_error = 0
    error_files = []
    for file_in_out in DirWalk.dirWalk(directory, theFnMatch='', recursive=recursive, bigFirst=False):
        if is_bit_file_from_path(file_in_out.filePathIn):
            try:
                result = print_process_file(file_in_out.filePathIn, verbose, summary)
                ret[file_in_out.filePathIn] = result
            except Exception as err:
                logger.error(f'ERROR: in {file_in_out.filePathIn} {err}')
                count_error += 1
                error_files.append(file_in_out.filePathIn)
    logger.info(f'Count of success={len(ret)} errors={count_error}')
    if len(error_files):
        logger.info(' Error files '.center(75, '-'))
        for file in error_files:
            logger.info(file)
        logger.info(' DONE Error files '.center(75, '-'))
    return ret


def main() -> int:  # pragma: no cover
    """Main entry point."""
    description = """usage: %(prog)s [options] file
Scans a file or directory for BIT files and summarises them."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = cmn_cmd_opts.path_in(
        description, prog='TotalDepth.BIT.ReadBIT.main', version=__version__, epilog=__rights__
    )
    cmn_cmd_opts.add_log_level(parser, level=20)
    parser.add_argument("--summary", action="store_true", default=False,
                        help="Display summary of channel data. [default: %(default)s]")
    args = parser.parse_args()
    # print('args:', args)
    # return 0
    cmn_cmd_opts.set_log_level(args)
    clk_start = time.perf_counter()
    # Your code here
    if os.path.isfile(args.path_in):
        result = print_process_file(args.path_in, args.verbose, args.summary)
        print(f'Result: {result}')
    else:
        result = print_process_directory(args.path_in, args.recurse, args.verbose, args.summary)
        print(f'{"Size":>12} {"Time (s)":>12} {"Rate (ms/Mb)":>12} {"File":<12}')
        total_size = total_time = 0
        for key in sorted(result.keys()):
            print(f'{result[key]}')
            total_size += result[key].size
            total_time += result[key].time
        print(f'Total size {total_size} bytes, total time {total_time:.3f} (s)')
        if total_size and total_time:
            print(f'Rate {total_time * 1000 / (total_size / 1024**2):.3f} (ms/MB) {total_size / total_time / 1024**2:.3f} Mb/s')
    if args.verbose == 0:
        print('Use -v, --verbose to see more information about each BIT file.')
    clk_exec = time.perf_counter() - clk_start
    print('Execution time = %8.3f (S)' % clk_exec)
    print('Bye, bye!')
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
