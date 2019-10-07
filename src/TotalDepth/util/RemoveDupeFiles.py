"""
Scans a directory and removes duplicate files based on their SHA.
"""
import argparse
import hashlib
import logging
import os
import sys
import time
import typing

from TotalDepth.common import td_logging


logger = logging.getLogger(__file__)


def remove_dupes(path: str, nervous: bool) -> typing.Tuple[int, int]:
    """Scans a directory tree removing duplicate files detected by their SHA512."""
    file_count = byte_count = 0
    dupes: typing.Dict[bytes, str] = {}
    file_num = 0
    for root, dirs, files in os.walk(path):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            msg = f'{file_num:,d}'
            logger.debug(f'Checking {file_path}')
            with open(file_path, 'rb') as fobj:
                hash_digest = hashlib.sha512(fobj.read()).digest()
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
        file_num += 1
    return file_count, byte_count


def main() -> int:
    print(f'CMD:', ' '.join(sys.argv))
    parser = argparse.ArgumentParser(description="""Deletes duplicate files in the given tree.""")
    parser.add_argument('path', help='Path to the directory.')
    parser.add_argument('-n', '--nervous', help='Nervous mode, does not do anything but report.', action='store_true')
    td_logging.add_logging_option(parser, 20)
    args = parser.parse_args()
    # print(args)
    td_logging.set_logging_from_argparse(args)
    t_start = time.perf_counter()
    num_files, byte_count = remove_dupes(args.path, args.nervous)
    t_exec = time.perf_counter() - t_start
    print(f'Execution time: {t_exec:.3f} (s)')
    print(f' Removed Files: {num_files:8,d} rate {num_files / t_exec:,.1f} (files/s)')
    print(f' Removed Bytes: {byte_count:8,d} rate {byte_count / t_exec:,.1f} (bytes/s)')
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
