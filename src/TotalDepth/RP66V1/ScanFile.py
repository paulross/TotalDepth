"""
Scans a RP66V1 file an prints out the summary.
"""
import argparse
import logging
import sys
import time
import typing

import TotalDepth.RP66V1.core.File

__author__  = 'Paul Ross'
__date__    = '2019-03-21'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


logger = logging.getLogger(__file__)


def _write_storage_unit_label(sul: TotalDepth.RP66V1.core.File.StorageUnitLabel, os: typing.TextIO=sys.stdout) -> None:
    os.write('Storage Unit Label:\n')
    os.write(f'Storage Unit Sequence Number: {sul.storage_unit_sequence_number}\n')
    os.write(f'                DLIS Version: {sul.dlis_version}\n')
    os.write(f'      Storage Unit Structure: {sul.storage_unit_structure}\n')
    os.write(f'       Maximum Record Length: {sul.maximum_record_length}\n')
    os.write(f'      Storage Set Identifier: {sul.storage_set_identifier}\n')


def scan_file(path: str, verbose: int, keep_going: bool) -> None:
    with open(path, 'rb') as fobj:
        rp66_file = TotalDepth.RP66V1.core.File.FileRead(fobj)
        print(rp66_file)
        _write_storage_unit_label(rp66_file.sul)
        for v, vr in enumerate(rp66_file.iter_visible_records()):
            print('[{:8,d}] {}'.format(v, vr))
            for l, lrsh in enumerate(rp66_file.iter_logical_record_segments(vr)):
                print('  [{:2d}] {} {}'.format(l, lrsh, lrsh.attribute_str()))


# parser.add_argument(
#         "-d", "--dump",
#         type="str",
#         dest="dump",
#         default='',
#         help="Dump complete data at these integer positions (ws separated, hex/dec). [default: %default]"
#     )


def main() -> int:
    description = """usage: %(prog)s [options] file
Scans a RP66V1 file and dumps data."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = argparse.ArgumentParser(description=description, epilog=__rights__, prog=sys.argv[0])
    parser.add_argument('path', type=str, help='Path to the file.')
    parser.add_argument(
        '--version', action='version', version='%(prog)s Version: ' + __version__,
        help='Show version and exit.'
    )
    parser.add_argument(
        '-k', '--keep-going', action='store_true',
        help='Keep going as far as sensible. [default: %(default)s]',
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
    print(args)

    # Extract log level
    if args.log_level in logging._nameToLevel:
        log_level = logging._nameToLevel[args.log_level]
    else:
        log_level = args.log_level
    # print('Log level:', log_level)
    # Initialise logging etc.
    logging.basicConfig(level=log_level,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    clk_start = time.perf_counter()
    # return 0
    if args.path:
        # Your code here
        scan_file(args.path, args.verbose, args.keep_going)#, retIntDumpList(opts.dump))
        pass
    else:
        print(parser.format_help())
        parser.error("Wrong number of arguments, I need one only.")
        return 1
    clk_exec = time.perf_counter() - clk_start
    print('Execution time = %8.3f (S)' % clk_exec)
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
