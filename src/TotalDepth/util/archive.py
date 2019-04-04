"""
Extract summary data from archives of log files.
"""
import argparse
import collections
import datetime
import functools
import math
import os
import shutil
import sys
import time
import typing
import zipfile

import TotalDepth.util.bin_file_type


class FileBase:
    """Base class to represent a file, either on-disc or a ZIP file."""
    # Number of bytes to take a file fragment of. 18 is useful for LIS+TIF as it gives
    # all the TIF markers [12], the PRH [4] and the LRH [2].
    XXD_NUM_BYTES = 18
    # XXD_NUM_BYTES = 8

    def __init__(self, path: str):
        self.path = path
        self.ext = os.path.splitext(path)[1].upper()
        self.size = 0
        self.bin_type = ''
        self.mod_date = datetime.datetime.min
        self.bytes = b''

    def __str__(self):
        return ' '.join(
            [
                f'{self.size:14,d}',
                f'{self.ext:5s}',
                f'{self.bin_type:{TotalDepth.util.bin_file_type.BINARY_FILE_TYPE_CODE_WIDTH}s}',
                # f'{self.mod_date}',
                TotalDepth.util.bin_file_type.format_bytes(self.bytes),
                f'{self.path}',
            ]
        )


class FileOnDisc(FileBase):
    """Represents an on-disc file."""

    def __init__(self, path: str):
        super().__init__(path)
        os_stat = os.stat(self.path)
        self.size = os_stat.st_size
        self.mod_date = datetime.datetime(*(time.localtime(os_stat.st_mtime)[:6]))
        with open(self.path, 'rb') as f:
            self.bin_type = TotalDepth.util.bin_file_type.binary_file_type(f)
            f.seek(0)
            self.bytes = f.read(self.XXD_NUM_BYTES)


class FileInMemory(FileBase):
    """Represents an in-memory file, for example contained in a ZIP.
    We need to be given the file data as we can't read it from disc."""

    def __init__(self, path: str, size: int, binary_type: str, mod_date: datetime.datetime, by: bytes):
        super().__init__(path)
        self.size = size
        self.bin_type = binary_type
        self.mod_date = mod_date
        self.bytes = by


class FileMembers:
    """Represents a tree of files for example a ZIP might contain a ZIP."""

    def __init__(self, archive_path: str, depth: int):
        self.archive_path = archive_path
        self.depth = depth
        self.members: typing.List[typing.Union[FileBase, FileMembers]] = []

    def append(self, path: str, size: int, binary_type: str, mod_date: datetime.datetime, by: bytes) -> None:
        self.members.append(
            FileInMemory(os.path.join(os.path.splitext(self.archive_path)[0], path), size, binary_type, mod_date, by)
        )

    def __str__(self):
        return '\n'.join(str(v) for v in self.members)


class FileArchive(FileOnDisc):
    """Represents a file that is an archive of other files."""

    def __init__(self, archive_path: str, depth: int):
        super().__init__(archive_path)
        self.members: FileMembers = FileMembers(archive_path, depth)


class FileZip(FileArchive):
    """Represents an on-disc file that is a ZIP file."""

    def __init__(self, archive_path: str):
        assert zipfile.is_zipfile(archive_path)
        super().__init__(archive_path, depth=0)
        # assert self.bin_type == 'ZIP', f'Binary type is "{self.bin_type}" not ZIP'
        # XXD_NUM_BYTES = 18
        with zipfile.ZipFile(archive_path) as z_archive:
            self._expand_archive(z_archive, 0)

    def _expand_archive(self, z_archive: zipfile.ZipFile, depth: int) -> None:
        # print()
        # print(f'TRACE: process_zip_path(): Processing ZIP {archive_path}')  # {z_archive.filename}')
        for z_info in z_archive.infolist():
            if z_info.is_dir():
                # print(f'{str():{xxd_size(XXD_NUM_BYTES)}s} {0:12,d} {"DIR":8s} {z_info.filename}')
                self.members.append(
                    z_info.filename, 0, 'DIR', datetime.datetime(*z_info.date_time), b''
                )
            else:
                with z_archive.open(z_info) as z_member_file:
                    if zipfile.is_zipfile(z_member_file):
                        # print(f'Found zip in zip: {z_info}')
                        with zipfile.ZipFile(z_member_file) as z_member_archive:
                            self._expand_archive(z_member_archive, depth + 1)
                    else:
                        bin_file_type = TotalDepth.util.bin_file_type.binary_file_type(z_member_file)
                        # by: bytes = z_member_file.read(XXD_NUM_BYTES)
                        # print(
                        #     f'{xxd(by):{xxd_size(XXD_NUM_BYTES)}s} {z_info.file_size:12,d}'
                        #     f' {bin_file_type:8s} {z_info.filename}'
                        # )
                        z_member_file.seek(0)
                        by = z_member_file.read(self.XXD_NUM_BYTES)
                        self.members.append(
                            z_info.filename, z_info.file_size, bin_file_type, datetime.datetime(*z_info.date_time), by
                        )

    def __str__(self):
        str_self = ' '.join(
            [
                f'{self.size:14,d}',
                f'{self.ext:4s}',
                f'{self.bin_type:{TotalDepth.util.bin_file_type.BINARY_FILE_TYPE_CODE_WIDTH}s}',
                # f'{self.mod_date}',
                TotalDepth.util.bin_file_type.format_bytes(self.bytes),
                f'{self.path}',
            ]
        )
        return '{}\n{}'.format(str_self, str(self.members))


class ArchiveCount:
    def __init__(self):
        self.count: int = 0
        self.total_size: int = 0
        self._size_hist: typing.Dict[int, int] = collections.defaultdict(int)
        self.size_min = sys.maxsize
        self.size_max = -sys.maxsize - 1
        self._date_hist: typing.Dict[typing.Tuple[int, int], int] = collections.defaultdict(int)
        self.extensions: typing.Set[str] = set()

    def _reduce_size(self, size: int) -> int:
        """Takes a file size in bytes and returns an integer measure of the size.
        NOTE: argument can be zero.
        Strategies could be:

            - Power, either int(math.log2(size)), int(math.log10(size)), round up if desired.
            - In kb, return size // 1024
        """
        if size > 0:
            return int(math.log2(size))
            # return int(math.log10(size))
        return 0

    def add(self, size: int, mod_timestamp: datetime.datetime, ext: str) -> None:
        self._size_hist[self._reduce_size(size)] += 1
        self.size_min = min(size, self.size_min)
        self.size_max = max(size, self.size_max)
        self._date_hist[(mod_timestamp.year, mod_timestamp.month)] += 1
        self.count += 1
        self.total_size += size
        self.extensions.add(ext)

    @property
    def size_hist(self):
        if self.count:
            for i in range(min(self._size_hist.keys()), 1 + max(self._size_hist.keys())):
                if i not in self._size_hist:
                    self._size_hist[i] = 0
        return self._size_hist

    @property
    def date_hist(self):
        if self.count:
            year_min = min(k[0] for k in self._date_hist.keys())
            year_max = max(k[0] for k in self._date_hist.keys())
            for y in range(year_min, 1 + year_max):
                month_max = max(k[1] for k in self._date_hist.keys() if k[0] == y)
                for m in range(1, 1 + month_max):
                    k = (y, m)
                    if k not in self._date_hist:
                        self._date_hist[k] = 0
        return self._date_hist


class ArchiveSummary:
    def __init__(self):
        self.ext_count: typing.Dict[str, ArchiveCount] = collections.defaultdict(ArchiveCount)
        self.bin_count: typing.Dict[str, ArchiveCount] = collections.defaultdict(ArchiveCount)
        self.count = 0
        self.total_size = 0

    def add(self, file_info: FileBase) -> None:
        self.ext_count[file_info.ext].add(file_info.size, file_info.mod_date, file_info.ext)
        self.bin_count[file_info.bin_type].add(file_info.size, file_info.mod_date, file_info.ext)
        self.count += 1
        self.total_size += file_info.size


def analyse_archive(files: typing.List[FileBase],
                    file_types: typing.List[str],
                    num_bytes: int,
                    include_size_histogram: bool,
                    ) -> None:
    summary: ArchiveSummary = ArchiveSummary()
    for file in files:
        if len(file_types) == 0 or file.bin_type in file_types:
            fields = [
                f'{file.size:14,d}',
                f'{file.ext:5s}',
                f'{file.bin_type:{TotalDepth.util.bin_file_type.BINARY_FILE_TYPE_CODE_WIDTH}s}',
            ]
            if num_bytes:
                fields.append(TotalDepth.util.bin_file_type.format_bytes(file.bytes))
            fields.append(
                f'{file.path}',
            )
            print(' '.join(fields))
    for file in files:
        summary.add(file)
    print(f'Total number of files {summary.count:,d}, total bytes {summary.total_size:,d}')
    print(f'File extensions:')
    extensions = sorted(summary.ext_count.keys())
    fw = max(len(v) for v in extensions) if len(extensions) else 2
    for extension in extensions:
        print(f'{extension:{fw}} : {summary.ext_count[extension].count:8,d}')
    print('Binary file types:')
    for bin_type in sorted(summary.bin_count.keys()):
        archive_count: ArchiveCount = summary.bin_count[bin_type]
        print(f'Binary type: "{bin_type}"')
        extensions = ', '.join(sorted(archive_count.extensions))
        print(f' Extensions: {extensions}')
        print(f'      Count: {archive_count.count:,d} [{archive_count.count / summary.count:.3%}]')
        print(
            f'      Bytes: {archive_count.total_size:,d} [{archive_count.total_size / summary.total_size:.3%}]'
            f' from {archive_count.size_min:,d} to  {archive_count.size_max:,d}')
        # print(archive_count.size_hist)
        if include_size_histogram:
            max_count = max(archive_count.size_hist.values())
            for k in sorted(archive_count.size_hist.keys()):
                prop = archive_count.size_hist[k] / max_count
                bar_len = int(0.5 + 40 * prop)
                bar = '+' * bar_len
                x_value = f'>2**{k}'
                # print(f'{x_value:10} : {archive_count.size_hist[k]:6d} | {bar}')
                print(f'{x_value:6} | {bar}')
            # print(archive_count.date_hist.keys())
            # print(f'Dates: from {min(archive_count.date_hist.keys())} to {max(archive_count.date_hist.keys())}')
            # print(archive_count.date_hist)
            print()


EXCLUDE_FILENAMES = ('.DS_Store', '.DS_STORE',)


def _process_file(dir_name: str, file_name: str, result: typing.List[FileBase]) -> None:
    if file_name not in EXCLUDE_FILENAMES:
        path = os.path.join(dir_name, file_name)
        if os.path.isfile(path):
            # If this is a ZIP archive then open it a process the contents.
            if zipfile.is_zipfile(path):
                # result.extend(process_zip_path(path))
                result.append(FileZip(path))
            else:
                result.append(FileOnDisc(path))


def explore_tree(path: str, recurse: bool) -> typing.List[FileBase]:
    result: typing.List[FileBase] = []
    assert os.path.isdir(path)
    if recurse:
        for root, dirs, files in os.walk(path):
            for file in files:
                _process_file(root, file, result)
    else:
        for file_name in sorted(os.listdir(path)):
            _process_file(path, file_name, result)
    # for r in result:
    #     if len(file_types) == 0 or r.bin_type in file_types:
    #         print(r)
    return result


def copy_tree(path_from: str, path_to: str, recurse: bool, file_types: typing.List[str], verbose: int, nervous: bool) -> None:
    def _print_message(msg: str) -> None:
        if verbose:
            if nervous:
                print(f'Would {msg}')
            else:
                print(f'{msg}')

    def _copy_file(_file_from: str, _file_to: str) -> None:
        fod = FileOnDisc(_file_from)
        if len(file_types) == 0 or fod.bin_type in file_types:
            _dir_to = os.path.dirname(_file_to)
            if not os.path.isdir(_dir_to):
                _print_message(f'Create sub-directory{_dir_to}')
                os.makedirs(_dir_to)
            _print_message(f'Copy {_file_from} to {_file_to}')
            if not nervous:
                shutil.copyfile(_file_from, _file_to)
        else:
            _print_message(f'Ignoring {_file_from} of type {fod.bin_type}')

    if not os.path.isdir(path_from):
        raise ValueError(f'Path {path_from} is not a directory.')
    if not os.path.isdir(path_to):
        _print_message(f'Create root directory {path_to}')
        if not nervous:
            os.makedirs(path_to)
    if recurse:
        for root, dirs, files in os.walk(path_from):
            for file in files:
                file_from = os.path.join(root, file)
                file_to = os.path.join(path_to, file)
                _copy_file(file_from, file_to)
    else:
        for file in sorted(os.listdir(path_from)):
            file_from = os.path.join(path_from, file)
            file_to = os.path.join(path_to, file)
            _copy_file(file_from, file_to)


ARCHIVE_EXTENSIONS = frozenset(
    functools.reduce(lambda x, y: x | y, [set(v[1]) for v in shutil.get_unpack_formats()], set())
)


def expand_and_delete_archives(dir_to: str) -> None:
    """
    Recursively searches for archives in dir_to, expands them and deletes the original archive.
    This assumes that expanding an archive does not write to a directory above dir_to, only in or below
    dir_to.
    """
    nervous = False
    has_expanded = True
    while has_expanded:
        has_expanded = False
        for name in sorted(os.listdir(dir_to)):
            path = os.path.join(dir_to, name)
            if os.path.isfile(path):
                if path not in EXCLUDE_FILENAMES:
                    if os.path.splitext(path)[1] in ARCHIVE_EXTENSIONS:
                        extract_dir = os.path.splitext(path)[0]
                        extract_dir = os.path.dirname(path)
                        if nervous:
                            print(f'XXX Would expand {path} to {extract_dir}')
                            print(f'XXX Would delete {path}')
                            has_expanded = False
                        else:
                            print(f'Expanding {path} to {extract_dir}')
                            shutil.unpack_archive(path, extract_dir=extract_dir)
                            os.remove(path)
                            has_expanded = True
    # Finally recurse
    for name in sorted(os.listdir(dir_to)):
        path = os.path.join(dir_to, name)
        if os.path.isdir(path):
            expand_and_delete_archives(path)


def expand_archive(dir_from: str, dir_to: str, nervous: bool = True) -> None:
    # if not nervous and os.path.samefile(dir_from, dir_to):
    #     raise ValueError(f'From {dir_from} is the same as to {dir_to}')
    if not os.path.exists(dir_to):
        if nervous:
            print(f'Would create target directory {dir_to}')
        else:
            print(f'Creating target directory {dir_to}')
            os.makedirs(dir_to)
    for path in sorted(os.listdir(dir_from)):
        path_from = os.path.join(dir_from, path)
        path_to = os.path.join(dir_to, path)
        if os.path.isfile(path_from):
            if path not in EXCLUDE_FILENAMES:
                if os.path.splitext(path_from)[1] in ARCHIVE_EXTENSIONS:
                    extract_dir = os.path.splitext(path_to)[0]
                    # extract_dir = os.path.dirname(path_to)
                    if nervous:
                        print(f'Would expand {path_from} to {extract_dir}')
                    else:
                        print(f'Expanding {path_from} to {extract_dir}')
                        shutil.unpack_archive(path_from, extract_dir=extract_dir)
                    expand_and_delete_archives(extract_dir)
                else:
                    if nervous:
                        print(f'Would copy {path_from} to {path_to}')
                    else:
                        print(f'Copying {path_from} to {path_to}')
                        shutil.copyfile(path_from, path_to)
        elif os.path.isdir(path_from):
            # if nervous:
            #     print(f'Would make target directory {path_to}')
            # else:
            #     os.makedirs(path_to)
            expand_archive(path_from, path_to, nervous)
        else:
            raise IOError(f'Path {path_from} is not a file or directory')

    # for root, dirs, files in os.walk(dir_from):
    #     # print(root, dirs, files)
    #     for path_dir in dirs:
    #         path_to = os.path.join(dir_to, path_dir)
    #         print(f'Would create directory {path_to}')
    #     for file in files:
    #         print(f'File: {file}')
    #         path_from = os.path.join(root, file)
    #         path_to = os.path.join(dir_to, file)
    #         if os.path.splitext(file)[1] in archive_extensions:
    #             print(f'Would expand {path_from} to {os.path.dirname(path_to)}')
    #             # shutil.unpack_archive(path_from, extract_dir=os.path.dirname(path_to))


def main() -> int:
    parser = argparse.ArgumentParser(description="""Summary analysis an archive of Log data.""")
    parser.add_argument('path_from', help='Path to the archive.')
    parser.add_argument('--file-types', default=[], action='append', help='Binary type(s) of file to list, additive.')
    parser.add_argument('-b', '--bytes', help='Number of initial bytes to show.', type=int, default=0)
    parser.add_argument('-r', '--recurse', help='Recurse into the path.', action='store_true')
    parser.add_argument('--histogram', help='Include size histogram.', action='store_true')
    # parser.add_argument('-n', '--nervous', help='Nervous mode, does not do anything but reports.', action='store_true')
    args = parser.parse_args()
    print(args)
    # return 0

    t_start = time.perf_counter()

    files: typing.List[FileBase] = []

    FileBase.XXD_NUM_BYTES = max(FileBase.XXD_NUM_BYTES, int(args.bytes))
    if os.path.isdir(args.path_from):
        files = explore_tree(args.path_from, args.recurse)
        # Output summary
        analyse_archive(files, args.file_types, args.bytes, args.histogram)

        # if args.path_to == '':
        # else:
        #     expand_archive(args.path_from, args.path_to, args.nervous)
    t_exec = time.perf_counter() - t_start
    files_per_sec = int(len(files) / t_exec)
    print('Execution time: {:.3f} (s) {:,d} (files/s)'.format(t_exec, files_per_sec))
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
