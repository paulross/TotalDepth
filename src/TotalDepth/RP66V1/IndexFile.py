import argparse
import logging
import os
import sys
import time
import typing

from TotalDepth.RP66V1.core.File import FileRead
from TotalDepth.RP66V1.core.Index import FileIndex

__author__  = 'Paul Ross'
__date__    = '2019-04-10'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


logger = logging.getLogger(__file__)


def index_file(path_in: str, path_out: str='') -> typing.Tuple[int, int]:
    with open(path_in, 'rb') as fobj:
        # rp66_file = FileRead(fobj)
        # index = FileIndex(rp66_file)
        # for file_logical_data in rp66_file.iter_logical_records():
        #     index.add(file_logical_data)
        index = FileIndex(fobj, path_in)
        # index.dump(sys.stdout)
        xml_fobj = index.write_xml()
        index_output = xml_fobj.getvalue()
        print(index_output)
        print(f'Length of XML: {len(index_output)}')
    return 1, os.path.getsize(path_in)


def main() -> int:
    description = """usage: %(prog)s [options] file
Scans a RP66V1 file and dumps data."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = argparse.ArgumentParser(description=description, epilog=__rights__, prog=sys.argv[0])
    parser.add_argument('path', type=str, help='Path to the file.')
    parser.add_argument(
        '-r', '--recurse', action='store_true',
        help='Process files recursively. [default: %(default)s]',
    )
    log_level_help_mapping = ', '.join(
        ['{:d}<->{:s}'.format(level, logging._levelToName[level]) for level in sorted(logging._levelToName.keys())]
    )
    log_level_help = f'Log Level as an integer or symbol. ({log_level_help_mapping}) [default: %(default)s]'
    parser.add_argument(
            "-l", "--log-level",
            # type=int,
            # dest="loglevel",
            default=30,
            help=log_level_help
        )
    parser.add_argument(
        "-v", "--verbose", action='count', default=0,
        help="Increase verbosity, additive [default: %(default)s]",
    )
    args = parser.parse_args()
    # print('args:', args)

    # Extract log level
    if args.log_level in logging._nameToLevel:
        log_level = logging._nameToLevel[args.log_level]
    else:
        log_level = int(args.log_level)
    # print('Log level:', log_level)
    # Initialise logging etc.
    logging.basicConfig(level=log_level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        #datefmt='%y-%m-%d % %H:%M:%S',
                        stream=sys.stdout)
    clk_start = time.perf_counter()
    # return 0
    # Your code here
    file_count, file_bytes = index_file(
        args.path,
        # args.recurse,
    )
    clk_exec = time.perf_counter() - clk_start
    print('Execution time = %8.3f (S)' % clk_exec)
    if file_bytes > 0:
        ms_mb = clk_exec * 1000 / (file_bytes / 1024**2)
    else:
        ms_mb = 0.0
    print(f'Processed {file_count:,d} files and {file_bytes:,d} bytes, {ms_mb:.1f} ms/Mb')
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
