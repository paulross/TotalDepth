"""
Copies files of a specific type from one file tree to another.
"""
import argparse
import logging
import os
import shutil
import sys
import time
import typing
import zipfile

from TotalDepth.util import DirWalk, bin_file_type


logger = logging.getLogger(__file__)


def _recurse_copy_zip_archive(
        instream: typing.BinaryIO,
        path_out: str, binary_file_types: typing.Set[str], nervous: bool) -> typing.List[str]:
    """Recursively extract ZIP archives."""
    logger.debug(f'_recurse_zip_archive(): path_out="{path_out}"')
    ret = []
    instream.seek(0)
    with zipfile.ZipFile(instream, mode='r') as zip_file:
        zip_info: zipfile.ZipInfo
        for zip_info in zip_file.infolist():
            logger.debug(f'_recurse_zip_archive(): zip_info="{zip_info}"')
            if not zip_info.is_dir():
                with zip_file.open(zip_info.filename) as zip_stream:
                    bin_type = bin_file_type.binary_file_type(zip_stream)
                    zip_stream.seek(0)
                    if bin_type == 'ZIP':
                        # Recurse
                        try:
                            ret.extend(
                                _recurse_copy_zip_archive(zip_stream, os.path.dirname(file_path_out), binary_file_types, nervous)
                            )
                        except zipfile.BadZipFile:
                            logger.debug(f'_recurse_zip_archive(): Appears to be "{bin_type}" but _recurse_zip_archive() raises.')
                    elif len(binary_file_types) == 0 or bin_type in binary_file_types:
                        file_path_out = os.path.join(path_out, zip_info.filename)
                        # Extract
                        if nervous:
                            print(
                                f'_recurse_zip_archive(): Would extract {zip_info.filename} to "{file_path_out}"')
                        else:
                            logger.debug(f'_recurse_zip_archive(): creating directory "{os.path.dirname(file_path_out)}"')
                            os.makedirs(os.path.dirname(file_path_out), exist_ok=True)
                            logger.info(f'_recurse_zip_archive(): WRITING "{file_path_out}"')
                            with open(file_path_out, 'wb') as ostream:
                                ostream.write(zip_stream.read())
                        ret.append(file_path_out)
                    else:
                        logger.debug(f'_recurse_zip_archive(): Ignoring type "{bin_type}" at "{zip_info.filename}"')
            else:
                logger.debug(f'_recurse_zip_archive(): Ignoring directory "{zip_info}"')
    return ret


# def _analyse_zip_archive(path_in: str, path_out: str, binary_file_types: typing.Set[str], nervous: bool) -> typing.List[str]:
#     assert zipfile.is_zipfile(path_in)
#     logger.debug(f'_analyse_zip_archive(): At "{path_in}" path_out: "{path_out}"')
#     with open(path_in, 'rb') as instream:
#         try:
#             return _recurse_zip_archive(instream, path_out, binary_file_types, nervous)
#         except Exception:
#             logger.exception('_recurse_zip_archive() FAILED')


def copy_files(path_in: str, path_out: str, binary_file_types: typing.Set[str], move: bool, nervous: bool) -> typing.List[str]:
    """
    Copies binary files from path_in to path_out.

    If move is True the file is moved, if False the file is copied.
    Returns a list of destination paths.
    """
    logger.debug(f'copy_files(): "{path_in}" to "{path_out}" ')
    ret = []
    for file_in_out in DirWalk.dirWalk(path_in, path_out, theFnMatch='', recursive=True, bigFirst=False):
        bin_type = bin_file_type.binary_file_type_from_path(file_in_out.filePathIn)
        if len(binary_file_types) == 0 or bin_type in binary_file_types:
            if nervous:
                print(f'copy_files(): Would create destination directory at {file_in_out.filePathOut}')
                if move:
                    print(f'copy_files(): Would move "{file_in_out.filePathIn}" to "{file_in_out.filePathOut}" ')
                else:
                    print(f'copy_files(): Would copy "{file_in_out.filePathIn}" to "{file_in_out.filePathOut}" ')
            else:
                # For real.
                logger.debug(f'copy_files(): Creating destination directory at {file_in_out.filePathOut}')
                os.makedirs(os.path.dirname(file_in_out.filePathOut), exist_ok=True)
                if move:
                    logger.info(f'copy_files(): Moving "{file_in_out.filePathIn}" to "{file_in_out.filePathOut}" ')
                    # move() uses copy2() function by default
                    ret.append(shutil.move(file_in_out.filePathIn, file_in_out.filePathOut))
                else:
                    logger.info(f'copy_files(): Copying "{file_in_out.filePathIn}" to "{file_in_out.filePathOut}" ')
                    # copy2 attempts to preserve metadata
                    ret.append(shutil.copy2(file_in_out.filePathIn, file_in_out.filePathOut))
        elif zipfile.is_zipfile(file_in_out.filePathIn):
            zip_out_path = os.path.splitext(file_in_out.filePathOut)[0]
            # ret.extend(_analyse_zip_archive(file_in_out.filePathIn, zip_out_path, binary_file_types, nervous))
            logger.debug(f'_analyse_zip_archive(): At "{file_in_out.filePathIn}" path_out: "{zip_out_path}"')
            with open(file_in_out.filePathIn, 'rb') as zip_instream:
                try:
                    return _recurse_copy_zip_archive(zip_instream, zip_out_path, binary_file_types, nervous)
                except Exception:
                    logger.exception('_recurse_copy_zip_archive() FAILED')

        else:
            logger.debug(f'copy_files(): Ignoring type "{bin_type}" at "{file_in_out.filePathOut}"')
    return ret


def main() -> int:
    """Main entry point. Copies of moves particular file types from one tree to another"""
    description = """Copies of moves particular file types from one tree to another."""
    print('Cmd: %s' % ' '.join(sys.argv))
    # TODO: Use cmn_cmd_opts
    parser = argparse.ArgumentParser(
        description=description,
        prog='TotalDepth.RP66V1.util.CopyBinFiles.main',
    )
    parser.add_argument('path_in', type=str, help='Path to the input file.')
    parser.add_argument('path_out', type=str, help='Path to the output scan to write.')
    parser.add_argument('--file-types', type=str,
                        help='Type of the file to copy or move, multiple types are supported as a comma separated list.'
                             ' Default is every file.'
                             ' Use "?" to see all supported file types.'
                             ' Use "??" to see all supported file types with their description.'
                        )
    parser.add_argument(
        '-m', '--move', action='store_true',
        help='Move rather than copy,'
             ' Irrelevant for files in ZIP archives which are always copied. [default: %(default)s]',
    )
    parser.add_argument(
        '-n', '--nervous', action='store_true',
        help='Nervous mode, report on stdout but don\'t do anything. [default: %(default)s]',
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
    args = parser.parse_args()
    # print('args:', args)

    # Extract log level
    if args.log_level in logging._nameToLevel:
        log_level = logging._nameToLevel[args.log_level]
    else:
        log_level = int(args.log_level)
    # Initialise logging etc.
    logging.basicConfig(level=log_level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        #datefmt='%y-%m-%d % %H:%M:%S',
                        stream=sys.stdout)
    clk_start = time.perf_counter()
    bytes_done = 0
    if args.file_types.strip() in ('?', '??'):
        print('Binary file types supported:', end='')
        if args.file_types.strip() == '?':
            print(f' {bin_file_type.summary_file_types_supported(short=True)}')
        else:
            print(f'\n{bin_file_type.summary_file_types_supported(short=False)}')
    else:
        file_types = set(args.file_types.strip().split(','))
        result = copy_files(args.path_in, args.path_out, file_types, move=args.move, nervous=args.nervous)
        if len(result) and not args.nervous:
            bytes_done = sum(os.path.getsize(f) for f in result)
        print(f'Files: {len(result):,d} output bytes {bytes_done:,d}')
    clk_exec = time.perf_counter() - clk_start
    print(f'Execution time = {clk_exec:8.3f} (S) {bytes_done / clk_exec / 1024:,.0f} kb/s')
    print('Bye, bye!')
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
