"""
Scans a file and verifies TIF markers reporting errors.
"""
import argparse
import collections
import logging
import struct
import sys
import time
import typing

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


def strip(path_in: str, path_out: str, verbose: int) -> int:
    bytes_written = 0
    with open(path_in, 'rb') as fobj_in:
        tif = _read_tifs(fobj_in)
        if tif.type != 0 or tif.prev != 0:
            print(f'No initial TIF markers: {tif}')
            return 0
        if verbose:
            print(f'{tif}')
        with open(path_out, 'wb') as fobj_out:
            while True:
                read_len = tif.next - tif.tell - TIF_LEN * 3
                if read_len > 0:
                    if verbose:
                        print(f'Writing 0x{read_len:08x} bytes from 0x{fobj_in.tell():08x}')
                    fobj_out.write(fobj_in.read(read_len))
                    bytes_written += read_len
                try:
                    tif_new = _read_tifs(fobj_in)
                except struct.error:
                    break
                if tif_new.prev != tif.tell:
                    logger.error(f'TIF prev 0x{tif_new.prev:08x} != tell 0x{tif.tell:08x}')
                tif = tif_new
    return bytes_written


def main() -> int:
    description = """usage: %(prog)s [options] file
    Scans a file for TIF markers and strips them."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = argparse.ArgumentParser(description=description, epilog=__rights__, prog=sys.argv[0])
    parser.add_argument('path_in', type=str, help='Path to the input file.')
    parser.add_argument(
        'path_out', type=str,
        help='Path to the output file, if absent the TIF markers are listed.',
        # default='',
        nargs='?')
    # parser.add_argument(
    #     '-r', '--recurse', action='store_true',
    #     help='Process files recursively. [default: %(default)s]',
    # )
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
        byte_count = strip(args.path_in, args.path_out, args.verbose)
        print(f'Wrote {byte_count:,d} bytes.')
    clk_exec = time.perf_counter() - clk_start
    print('Execution time = %8.3f (S)' % clk_exec)
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
