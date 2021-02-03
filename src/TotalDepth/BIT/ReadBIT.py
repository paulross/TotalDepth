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
This processes Dresser Atlas BIT files.
Dresser Atlas BIT files are TIF encoded and consist of a set of:

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

Corresponding BIT file 29_10-_3Z_dwl_DWL_WIRE_1644659.bit has:

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
import os
import string
import struct
import sys
import typing

import numpy as np

from TotalDepth.common import LogPass
from TotalDepth.util import DirWalk


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
        if any(v not in ASCII_PRINTABLE_BYTES for v in r):
            return False
        count = struct.unpack('>h', fobj.read(2))[0]
        if count > 20:
            return False
        null = struct.unpack('>h', fobj.read(2))[0]
        if null != 0:
            return False
        for i in range(count):
            name = fobj.read(4)
            if any(v not in ASCII_PRINTABLE_BYTES for v in name):
                return False
        return True
    return False


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
    tif_type: TifType
    payload: bytes


TIF_WORD_STRUCT = struct.Struct('<3L')


def yield_tif_blocks(file: typing.BinaryIO) -> typing.Sequence[TifMarkedBytes]:
    """Generate the payload from blocks of the file."""
    file.seek(0)
    tif_prev = TifMarker(0, 0, 0, 0)
    while True:
        tell = file.tell()
        tif = TifMarker(tell, *TIF_WORD_STRUCT.unpack_from(file.read(TIF_WORD_STRUCT.size)))
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
        frame_array_str = '\n'.join(f'      {v}' for v in str(self.frame_array).split('\n'))
        ret = [
            f'BITFrameArray: ident="{self.ident}"',
            f'   Unknown head: {self.unknown_head}',
            f'    Description: {self.description}',
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
        if len(block) % self.len_channels:
            raise ExceptionTotalDepthBITDataBlocks(
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
                try:
                    frame_array.add_block(tif_block.payload)
                except ExceptionTotalDepthBITDataBlocks as err:
                    logger.error(f'{str(err)} at tell={file.tell()}')
                    break
            elif tif_block.tif_type == TifType.END_LOG_PASS:
                frame_array.complete()
                log_pass.append(frame_array)
                frame_array = None
    if frame_array is not None:
        frame_array.complete()
        log_pass.append(frame_array)
    return log_pass


def create_bit_frame_array_from_path(file_path: str) -> typing.List[BITFrameArray]:
    with open(file_path, 'rb') as file:
        ret = create_bit_frame_array_from_file(file)
    return ret


def print_process_file(file_path: str) -> None:
    print(f'File size: {os.path.getsize(file_path):d} 0x{os.path.getsize(file_path):x}: {file_path} ')
    log_pass = create_bit_frame_array_from_path(file_path)
    for array in log_pass:
        print(array.long_str())


def print_process_directory(directory: str, recursive: bool) -> None:
    for file_in_out in DirWalk.dirWalk(directory, theFnMatch='', recursive=recursive, bigFirst=False):
        try:
            print_process_file(file_in_out.filePathIn)
        except Exception as err:
            print(f'ERROR: type={type(err)} value={err}')




DEFAULT_OPT_LOG_FORMAT_VERBOSE = (
    '%(asctime)s - %(filename)24s#%(lineno)-4d - %(process)5d - (%(threadName)-10s) - %(levelname)-8s - %(message)s'
)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format=DEFAULT_OPT_LOG_FORMAT_VERBOSE, stream=sys.stdout)

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

    # print_process_file(example)

    example = '/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT/special/29_10-_3/DWL_FILE/29_10-_3_dwl_DWL_WIRE_1646632.bit'
    # print_process_file(example)

    # if len(sys.argv) > 1:
    #     example = sys.argv[1]
    print_process_directory('/Users/paulross/PycharmProjects/TotalDepth/data/DresserAtlasBIT', True)

    return 0


if __name__ == '__main__':
    sys.exit(main())
