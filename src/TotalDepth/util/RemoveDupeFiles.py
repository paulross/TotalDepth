"""
Scans a directory and removes duplicate files based on their SHA.
"""
import hashlib
import logging
import os
import sys
import time
import typing

from TotalDepth.common import cmn_cmd_opts

logger = logging.getLogger(__file__)

__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2019 Paul Ross. All rights reserved.'


def remove_dupes(path: str, nervous: bool) -> typing.Tuple[int, int]:
    """Scans a directory tree removing duplicate files detected by their SHA512."""
    BLOCK_SIZE = 1024**2
    file_count = byte_count = 0
    dupes: typing.Dict[bytes, str] = {}
    for root, dirs, files in os.walk(path):
        for file in sorted(files):
            if not file.startswith('.'):
                file_path = os.path.join(root, file)
                logger.debug(f'Checking {file_path}')
                with open(file_path, 'rb') as fobj:
                    hash_digest = hashlib.sha512()
                    while True:
                        data = fobj.read(BLOCK_SIZE)
                        if not data:
                            break
                        hash_digest.update(data)
                    hash_digest = hash_digest.digest()
                    if hash_digest in dupes:
                        byte_count += os.path.getsize(file_path)
                        file_count += 1
                        if nervous:
                            logger.info(f'Would remove {file_path} as duplicate of {dupes[hash_digest]}')
                        else:
                            logger.info(f'Removing {file_path} as duplicate of {dupes[hash_digest]}')
                            os.remove(file_path)
                    else:
                        dupes[hash_digest] = file_path
    return file_count, byte_count


def main() -> int:
    """Main CLI entry point."""
    print(f'CMD:', ' '.join(sys.argv))
    parser = cmn_cmd_opts.path_in(
        """Deletes duplicate files in the given tree.""",
        prog='TotalDepth.RP66V1.util.RemoveDupeFiles.main', version=__version__, epilog=__rights__
    )
    cmn_cmd_opts.add_log_level(parser, level=20)
    parser.add_argument('-n', '--nervous',
                        help='Nervous mode, does not do anything but report [default: %(default)s].',
                        action='store_true')
    args = parser.parse_args()
    # print(args)
    cmn_cmd_opts.set_log_level(args)
    t_start = time.perf_counter()
    num_files, byte_count = remove_dupes(args.path_in, args.nervous)
    t_exec = time.perf_counter() - t_start
    print(f'Execution time: {t_exec:.3f} (s)')
    print(f' Removed Files: {num_files:8,d} rate {num_files / t_exec:,.1f} (files/s)')
    print(f' Removed Bytes: {byte_count:8,d} rate {byte_count / t_exec:,.1f} (bytes/s)')
    print('Bye, bye!')
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
