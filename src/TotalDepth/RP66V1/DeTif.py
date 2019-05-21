"""
Scans a file and verifies TIF markers reporting errors.
"""
import argparse
import collections
import logging
import os
import struct
import sys
import time
import typing

from TotalDepth.util.DirWalk import dirWalk

__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


logger = logging.getLogger(__file__)


TIF_STRUCT = struct.Struct('<L')
TIF_LEN: int = TIF_STRUCT.size
TIF_COUNT: int = 3


def _read_tif(fobj: typing.BinaryIO) -> int:
    # value = struct.unpack('<L', fobj.read(4))
    value = TIF_STRUCT.unpack(fobj.read(TIF_LEN))
    return value[0]


class TifMarker(collections.namedtuple('TifMarker', 'tell, type, prev, next')):
    def __str__(self) -> str:
        return f'TifMarker: 0x{self.tell:08x} Type: 0x{self.type:08x} Prev: 0x{self.prev:08x} Next: 0x{self.next:08x}'


def _read_tifs(fobj: typing.BinaryIO) -> TifMarker:
    tell = fobj.tell()
    tif_type = _read_tif(fobj)
    tif_prev = _read_tif(fobj)
    tif_next = _read_tif(fobj)
    ret = TifMarker(tell, tif_type, tif_prev, tif_next)
    return ret


def scan(path: str, verbose: int) -> int:
    count = 0
    with open(path, 'rb') as fobj:
        tif = _read_tifs(fobj)
        if tif.type != 0 or tif.prev != 0:
            print(f'No initial TIF markers: {tif}')
            return count
        if verbose:
            print(f'{tif}')
        while True:
            span = tif.next - tif.tell
            fobj.seek(tif.next)
            try:
                tif_new = _read_tifs(fobj)
            except struct.error:
                break
            count += 1
            if verbose:
                print(f'{tif_new} Span: 0x{span:08x}')
            if tif_new.prev != tif.tell:
                logger.error(f'TIF prev 0x{tif_new.prev:08x} != tell 0x{tif.tell:08x}')
            tif = tif_new
    return count


def has_tif(path: str) -> bool:
    with open(path, 'rb') as fobj_in:
        tif = _read_tifs(fobj_in)
        if tif.type != 0 or tif.prev != 0:
            return False
    return True


def strip(path_in: str, path_out: str) -> typing.Tuple[int, int]:
    tif_markers_stripped = bytes_written = 0
    with open(path_in, 'rb') as fobj_in:
        tif = _read_tifs(fobj_in)
        if tif.type != 0 or tif.prev != 0:
            logging.error(f'No initial TIF markers: {tif}')
            return 0, 0
        logging.debug(f'TIF: {tif}')
        with open(path_out, 'wb') as fobj_out:
            while True:
                read_len = tif.next - tif.tell - TIF_LEN * 3
                if read_len > 0:
                    logging.debug(f'Writing 0x{read_len:08x} bytes from 0x{fobj_in.tell():08x}')
                    fobj_out.write(fobj_in.read(read_len))
                    bytes_written += read_len
                try:
                    tif_new = _read_tifs(fobj_in)
                except struct.error:
                    break
                if tif_new.prev != tif.tell:
                    logger.error(f'TIF prev 0x{tif_new.prev:08x} != tell 0x{tif.tell:08x}')
                tif = tif_new
                tif_markers_stripped += 1
    return tif_markers_stripped, bytes_written


def main() -> int:
    description = """usage: %(prog)s [options] file
Scans a file for TIF markers or can copy a directory of files with TIF markers removed."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = argparse.ArgumentParser(description=description, epilog=__rights__, prog=sys.argv[0])
    parser.add_argument('path_in', type=str, help='Path to the input file (or file/directory if stripping).')
    parser.add_argument(
        'path_out', type=str,
        help='Path to the output file or directory, if absent the TIF markers for the input file are just listed.'
             'The results are undefined if path_out conflicts with path_in',
        # default='',
        nargs='?')
    parser.add_argument(
        '-r', '--recurse', action='store_true',
        help='Process files recursively. [default: %(default)s]',
    )
    parser.add_argument(
        '-n', '--nervous', action='store_true',
        help='Nervous mode, don\'t do anything but report what would be done. [default: %(default)s]',
    )
    log_level_help_mapping = ', '.join(
        ['{:d}<->{:s}'.format(level, logging._levelToName[level]) for level in sorted(logging._levelToName.keys())]
    )
    log_level_help = f'Log Level as an integer or symbol. ({log_level_help_mapping}) [default: %(default)s]'
    parser.add_argument(
        "-l", "--log-level",
        default=30,
        help=log_level_help
    )
    parser.add_argument(
        "-v", "--verbose", action='count', default=0,
        help="Increase verbosity, additive [default: %(default)s]",
    )
    args = parser.parse_args()
    # print('args:', args)
    # return 0

    # Extract log level
    if args.log_level in logging._nameToLevel:
        log_level = logging._nameToLevel[args.log_level]
    else:
        log_level = int(args.log_level)
    # Initialise logging etc.
    logging.basicConfig(level=log_level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        # datefmt='%y-%m-%d % %H:%M:%S',
                        stream=sys.stdout)
    clk_start = time.perf_counter()
    # Your code here
    if args.path_out is None:
        tif_count = scan(args.path_in, args.verbose)
        print(f'Detected {tif_count:,d} TIF Markers.')
    else:
        tif_stripped = bytes_copied = files_copied = 0
        for file_in_out in dirWalk(args.path_in, args.path_out, theFnMatch='', recursive=args.recurse, bigFirst=False):
            if has_tif(file_in_out.filePathIn):
                out_dir = os.path.dirname(file_in_out.filePathOut)
                if args.nervous:
                    logger.info(f'Would make directory: {out_dir}')
                    logger.info(f'Would copy {file_in_out.filePathIn} to {file_in_out.filePathOut}')
                    bytes_copied += os.path.getsize(file_in_out.filePathIn)
                    files_copied += 1
                else:
                    logger.info(f'Making directory: {out_dir}')
                    logger.info(f'Copying {file_in_out.filePathIn} to {file_in_out.filePathOut}')
                    os.makedirs(out_dir, exist_ok=True)
                    tif_count, byte_count = strip(file_in_out.filePathIn, file_in_out.filePathOut)
                    tif_stripped += tif_count
                    bytes_copied += byte_count
                    if byte_count:
                        files_copied += 1
        print(f'Total bytes: {bytes_copied:,d}, files: {files_copied:,d} TIF markers removed: {tif_stripped:,d}')
    clk_exec = time.perf_counter() - clk_start
    print('Execution time = %8.3f (S)' % clk_exec)
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
