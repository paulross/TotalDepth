"""
Strip TIF markers from a file or scan a file and reporting errors in TIF markers.
"""
import argparse
import logging
import os
import struct
import sys
import time
import typing

from TotalDepth.common import cmn_cmd_opts
from TotalDepth.util.DirWalk import dirWalk

__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'
__version__ = '0.1.0'


logger = logging.getLogger(__file__)


TIF_STRUCT = struct.Struct('<L')
TIFS_STRUCT = struct.Struct('<LLL')
TIF_WORD_NUM_BYTES: int = TIF_STRUCT.size
TIF_TRIPLET_NUM_BYTES: int = TIFS_STRUCT.size
TIF_COUNT: int = 3
TIF_MIN_FILE_SIZE = TIF_TRIPLET_NUM_BYTES * 3


class DeTifException(Exception):
    pass


class DeTifExceptionCompare(DeTifException):
    pass


class DeTifExceptionRead(DeTifException):
    pass


class TifMarker(typing.NamedTuple):
    # We do not correct reversed TIF markers (that is a commercial service).
    tell: int
    type: int
    prev: int
    next: int

    def __str__(self) -> str:
        return f'TifMarker: 0x{self.tell:08x} Type: 0x{self.type:08x} Prev: 0x{self.prev:08x} Next: 0x{self.next:08x}'

    @property
    def is_tif_start(self) -> bool:
        return self.type == 0 and self.prev == 0

    @property
    def read_len(self) -> int:
        ret = self.next - self.tell - TIF_WORD_NUM_BYTES * 3
        return ret


def compare_next(this: TifMarker, nxt: TifMarker) -> None:
    """Compares two adjacent TIF markers for consistency."""
    if this.tell >= nxt.tell:
        raise DeTifExceptionCompare(f'this.tell of 0x{this.tell:08x} >= next.tell of 0x{nxt.tell:08x}')
    if this.tell != nxt.prev:
        raise DeTifExceptionCompare(f'this.tell of 0x{this.tell:08x} != next.prev of 0x{nxt.prev:08x}')
    if this.next != nxt.tell:
        raise DeTifExceptionCompare(f'this.mext of 0x{this.next:08x} != next.tell of 0x{nxt.tell:08x}')


def _read_tifs(fobj: typing.BinaryIO) -> TifMarker:
    """Reads file from current position and returns the three tif marker values.
    May raise a struct.error on failure."""
    tell = fobj.tell()
    tifs = TIFS_STRUCT.unpack(fobj.read(TIF_WORD_NUM_BYTES * TIF_COUNT))
    ret = TifMarker(tell, *tifs)
    return ret


def has_tif_file(fobj: typing.BinaryIO) -> bool:
    """Returns True of the file in path apparently has TIF markers."""
    try:
        tif = _read_tifs(fobj)
        return tif.is_tif_start
    except struct.error:
        return False


def has_tif(path: str) -> bool:
    """Returns True of the file in path apparently has TIF markers."""
    with open(path, 'rb') as fobj_in:
        return has_tif_file(fobj_in)


def tif_scan_file_object(fobj: typing.BinaryIO) -> typing.List[TifMarker]:
    """Scan a file object and return the list of TIF markers."""
    tifs: typing.List[TifMarker] = []
    fobj.seek(0)
    try:
        tifs.append(_read_tifs(fobj))
    except struct.error as err:
        raise DeTifExceptionRead(f'Could not read TIF marker: {err}')
    if not tifs[-1].is_tif_start:
        raise DeTifExceptionRead(f'Initial TIF marker is wrong type: {tifs[-1]}')
    logger.debug(f'[{len(tifs):8,d}] {tifs[-1]}')
    while True:
        fobj.seek(tifs[-1].next)
        try:
            tifs.append(_read_tifs(fobj))
        except struct.error:
            break
        logger.debug(f'[{len(tifs):8,d}] {tifs[-1]}')
    return tifs


def tif_scan_path(path: str) -> typing.List[TifMarker]:
    """Scan a file at path and return the list of TIF markers."""
    with open(path, 'rb') as fobj:
        tifs = tif_scan_file_object(fobj)
    return tifs


def get_errors(tifs: typing.List[TifMarker], file_size: int) -> typing.List[str]:
    """Return a list of TIF marker errors."""
    if file_size < TIF_MIN_FILE_SIZE:
        raise ValueError(f'get_errors() file_size must be >= {TIF_MIN_FILE_SIZE} not {file_size}')
    ret = []
    if len(tifs) < 3:
        ret.append('ERROR: <3 TIF markers')
    else:
        for t in range(len(tifs)):
            if t == 0:
                if tifs[t].tell != 0:
                    ret.append(f'ERROR: TIF[{t}] tell != 0: {tifs[t]}')
                if tifs[t].type != 0:
                    ret.append(f'ERROR: TIF[{t}] type != 0: {tifs[t]}')
                if tifs[t].prev != 0:
                    ret.append(f'ERROR: TIF[{t}] prev != 0: {tifs[t]}')
                if tifs[t].next < TIF_TRIPLET_NUM_BYTES:
                    ret.append(f'ERROR: TIF[{t}] next is < {TIF_TRIPLET_NUM_BYTES}: {tifs[t]}')
            else:
                # Type check
                if t < len(tifs) - 2:
                    if tifs[t].type != 0:
                        ret.append(f'ERROR: TIF[{t}] type != 0: {tifs[t]}')
                else:
                    if tifs[t].type != 1:
                        ret.append(f'ERROR: TIF[{t}] type != 1: {tifs[t]}')
                # Have t-1 and t+1
                if tifs[t].tell - tifs[t-1].tell < TIF_WORD_NUM_BYTES:
                    ret.append(f'ERROR: TIF[{t}] tell - TIF[{t-1}] tell < {TIF_WORD_NUM_BYTES}: {tifs[t]} {tifs[t - 1]}')
                if tifs[t].tell != tifs[t-1].next:
                    ret.append(f'ERROR: TIF[{t}] tell != TIF[{t-1}] next: {tifs[t]} {tifs[t-1]}')
                if tifs[t].prev != tifs[t-1].tell:
                    ret.append(f'ERROR: TIF[{t}] tell != TIF[{t-1}] next: {tifs[t]} {tifs[t-1]}')
                if t < len(tifs) - 1:
                    if tifs[t].next - tifs[t].tell < TIF_WORD_NUM_BYTES:
                        ret.append(f'ERROR: TIF[{t}] next - TIF[{t}] tell < {TIF_WORD_NUM_BYTES}: {tifs[t]}')
                else:
                    # Last TIF
                    if tifs[t].next - tifs[t].tell != TIF_TRIPLET_NUM_BYTES:
                        ret.append(f'ERROR: TIF[{t}] next - TIF[{t}] tell < {TIF_TRIPLET_NUM_BYTES}: {tifs[t]}')
                    if tifs[t].next != file_size:
                        ret.append(f'ERROR: TIF[{t}] next < 0x{file_size:08x}: {tifs[t]}')
    return ret


def strip_tif(file_in: typing.BinaryIO, file_out: typing.BinaryIO) -> typing.Tuple[int, int]:
    """Read file_in then strip TIF markers and write to file_out.
    The only error detected is negative reads.
    Returns a tuple of (tif_markers_stripped, bytes_written)."""
    file_in.seek(0)
    file_out.seek(0)
    tif = _read_tifs(file_in)
    if not tif.is_tif_start:
        raise DeTifExceptionRead(f'Initial TIF marker is wrong type: {tif}')
    tif_markers_stripped = 1
    bytes_written = 0
    while True:
        if tif.read_len < 0:
            raise DeTifExceptionRead(f'TIF marker suggests negative block size: {tif}')
        logging.debug(f'Writing 0x{tif.read_len:08x} bytes from 0x{file_in.tell():08x}')
        file_out.write(file_in.read(tif.read_len))
        bytes_written += tif.read_len
        try:
            tif = _read_tifs(file_in)
        except struct.error:
            break
        tif_markers_stripped += 1
    return tif_markers_stripped, bytes_written


def strip_path(path_in: str, path_out: str) -> typing.Tuple[int, int]:
    """Read path_in then strip TIF markers and write to path_out."""
    with open(path_in, 'rb') as fobj_in:
        with open(path_out, 'wb') as fobj_out:
            return strip_tif(fobj_in, fobj_out)


def de_tif_file(path_in: str, path_out: str, nervous: bool, over_write: bool) -> typing.Tuple[int, int, int]:
    """De-TIFs a file path_in writing to path_out. Returns a tuple of (files_copied, tif_count, byte_count) where
    files_copied is 0 or 1, tif_count is the number of 12 byte TIF markers and byte_count is the number of bytes
    in path_in (if no file written) or path_out if the file is written."""
    files_copied = tif_count = byte_count = 0
    if has_tif(path_in):
        if nervous:
            logger.info(f'Would copy {path_in} to {path_out}')
            byte_count = os.path.getsize(path_in)
            tif_count = len(tif_scan_path(path_in))
        else:
            if not os.path.exists(path_out) or over_write:
                logger.info(f'De-TIF {path_in} to {path_out}')
                os.makedirs(os.path.dirname(path_out), exist_ok=True)
                tif_count, byte_count = strip_path(path_in, path_out)
                files_copied = 1
            else:
                logger.warning(f'Not overwriting file at {path_out}')
    else:
        logger.info(f'Ignoring non-TIF file: {path_in}')
    return files_copied, tif_count, byte_count


def main() -> int:
    description = """usage: %(prog)s [options] file
Scans a file for TIF markers or can copy a directory of files with TIF markers removed."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = cmn_cmd_opts.path_in_out(
        description, prog='TotalDepth.DeTif.main', version=__version__, epilog=__rights__
    )
    cmn_cmd_opts.add_log_level(parser, level=20)
    # cmn_cmd_opts.add_multiprocessing(parser)
    parser.add_argument(
        '-n', '--nervous', action='store_true',
        help='Nervous mode, don\'t do anything but report what would be done. [default: %(default)s]',
    )
    parser.add_argument('-o', '--over-write', help='Over write existing files, otherwise warns.', action='store_true')
    args = parser.parse_args()
    # print('args:', args)
    # return 0
    cmn_cmd_opts.set_log_level(args)
    clk_start = time.perf_counter()
    # Your code here
    if args.path_out is None:
        tif_markers = tif_scan_path(args.path_in)
        print(f'Detected {len(tif_markers):,d} TIF Markers in {args.path_in}')
        if args.verbose:
            for t, tif_marker in enumerate(tif_markers):
                print(f'[{t:6,d}] {tif_marker}')
        else:
            print('Use -v option to see the actual TIF markers.')
    else:
        # Strip the TIF markers, respecting the nervous option.
        files_copied = tif_count = bytes_copied = 0
        if os.path.isfile(args.path_in):
            files_copied, tif_count, bytes_copied = de_tif_file(args.path_in, args.path_out, args.nervous, args.over_write)
        else:
            for file_in_out in dirWalk(args.path_in, args.path_out, theFnMatch='', recursive=args.recurse, bigFirst=False):
                _files_copied, _tif_count, _byte_count = de_tif_file(
                    file_in_out.filePathIn, file_in_out.filePathOut, args.nervous, args.over_write
                )
                files_copied += _files_copied
                tif_count += _tif_count
                bytes_copied += _byte_count
        print(f'Files: {files_copied:,d} 12 byte TIF markers removed: {tif_count:,d} bytes: {bytes_copied:,d}')
    clk_exec = time.perf_counter() - clk_start
    print('Execution time = %8.3f (S)' % clk_exec)
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
