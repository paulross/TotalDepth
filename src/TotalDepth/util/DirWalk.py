#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation.
# Copyright (C) 2011-2021 Paul Ross
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
"""Provides various ways of walking a directory tree

Created on Jun 9, 2011
"""
import enum
import typing

__author__  = 'Paul Ross'
__date__    = '2011-06-09'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'

import os
import fnmatch

from TotalDepth import ExceptionTotalDepth

#: A pair of (in, out) file paths
# FileInOut = collections.namedtuple('FileInOut', 'filePathIn, filePathOut')


class FileInOut(typing.NamedTuple):
    filePathIn: str
    filePathOut: str

    @property
    def commonprefix(self):
        return os.path.commonprefix([self.filePathIn, self.filePathOut])


class ExceptionDirWalk(ExceptionTotalDepth):
    """Exception class for this module."""
    pass


def gen_big_first(directory):
    """Generator that yields the biggest files (name not path) first.
    This is fairly simple in that it it only looks the current directory not
    only sub-directories. Useful for multiprocessing."""
    size_paths = []
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            size_paths.append((os.path.getsize(path), name))
    # print(size_paths)
    for size, name in sorted(size_paths):
        yield name


def dirWalk(theIn: str, theOut: str = '', theFnMatch: typing.Tuple[str] = (),
            recursive: bool = False, bigFirst: bool = False) -> typing.Sequence[FileInOut]:
    """Walks a directory tree generating file paths as FileInOut(in, out) objects.

    theIn - The input directory.

    theOut - The output directory. If an empty string the out path will be an empty string.
    NOTE: This does not create the output directory structure, it is up to
    the caller to do that.

    theFnMatch - A glob like match pattern for file names (not tested for directory names).
    TODO: Should be a tuple of fnmatch strings.

    recursive - Boolean to recurse or not.

    bigFirst - If True then the largest files in  directory are given first. If False it is alphabetical.
    """
    def _match(file_path: str, fn_match: typing.Tuple[str]):
        if len(fn_match) == 0:
            return True
        return any(fnmatch.fnmatch(file_path, patt) for patt in fn_match)

    # print(f'theIn="{theIn}" theOut="{theOut}"')
    if not os.path.isdir(theIn):
        raise ExceptionDirWalk('{:s} is not a directory.'.format(theIn))
    if bigFirst:
        # First files
        for fn in gen_big_first(theIn):
            fp = os.path.join(theIn, fn)
            if _match(fp, theFnMatch):
                out_file = ''
                if theOut:
                    out_file = os.path.join(theOut, fn)
                yield FileInOut(fp, out_file)
        # Now directories
        if recursive:
            for n in sorted(os.listdir(theIn)):
                fp = os.path.join(theIn, n)
                if os.path.isdir(fp):
                    out_path = ''
                    if theOut:
                        out_path = os.path.join(theOut, n)
                    for aFp in dirWalk(fp, out_path, theFnMatch, recursive, bigFirst):
                        yield aFp
    else:
        # Straightforward list in alphanumeric order
        for n in sorted(os.listdir(theIn)):
            fp = os.path.join(theIn, n)
            if os.path.isfile(fp) and _match(fp, theFnMatch):
                out_file = ''
                if theOut:
                    out_file = os.path.join(theOut, n)
                yield FileInOut(fp, out_file)
            elif os.path.isdir(fp) and recursive:
                out_path = ''
                if theOut:
                    out_path = os.path.join(theOut, n)
                for aFp in dirWalk(fp, out_path, theFnMatch, recursive):
                    yield aFp

class Event(enum.Enum):
    DIR_OPEN = 1
    DIR_CLOSE = 2
    FILE_OPEN = 3
    FILE_CLOSE = 4

class FileEvent(typing.NamedTuple):
    event: Event
    path_in: str
    path_out: str

    @property
    def commonprefix(self):
        return os.path.commonprefix([self.path_in, self.path_out])


def dir_event_walk(path_in: str, path_out: str = '', fn_match: str = '',
                   recursive: bool = False, big_first: bool = False) -> typing.Sequence[FileEvent]:
    """Walks a directory tree generating file paths as FileEvent() objects.

    path_in - The input directory.

    path_out - The output directory. If an empty string the out path will always be an empty string.
        NOTE: This does not create the output directory structure, it is up to the caller to do that.

    fn_match - A glob like match pattern for file names (not tested for directory names).

    recursive - Boolean to recurse or not.

    big_first - If True then the largest files in directory are given first.
        Order is files first followed by directories.
        If False the order is alphabetical files and directories (with recursion as appropriate).
    """
    if not os.path.isdir(path_in):
        raise ExceptionDirWalk('{:s} is not a directory.'.format(path_in))
    if big_first:
        # First files
        for file_name in gen_big_first(path_in):
            file_path = os.path.join(path_in, file_name)
            if not fn_match or fnmatch.fnmatch(file_path, fn_match):
                out_file = ''
                if path_out:
                    out_file = os.path.join(path_out, file_name)
                yield FileEvent(Event.FILE_OPEN, file_path, out_file)
                yield FileEvent(Event.FILE_CLOSE, file_path, out_file)
        # Now directories
        if recursive:
            for name in sorted(os.listdir(path_in)):
                file_path = os.path.join(path_in, name)
                if os.path.isdir(file_path):
                    out_path = ''
                    if path_out:
                        out_path = os.path.join(path_out, name)
                    yield FileEvent(Event.DIR_OPEN, file_path, out_path)
                    yield from dir_event_walk(file_path, out_path, fn_match, recursive, big_first)
                    yield FileEvent(Event.DIR_CLOSE, file_path, out_path)
    else:
        # Straightforward list in alphanumeric order
        for name in sorted(os.listdir(path_in)):
            file_path = os.path.join(path_in, name)
            if os.path.isfile(file_path) and (not fn_match or fnmatch.fnmatch(file_path, fn_match)):
                out_file = ''
                if path_out:
                    out_file = os.path.join(path_out, name)
                yield FileEvent(Event.FILE_OPEN, file_path, out_file)
                yield FileEvent(Event.FILE_CLOSE, file_path, out_file)
            elif os.path.isdir(file_path) and recursive:
                out_path = ''
                if path_out:
                    out_path = os.path.join(path_out, name)
                yield FileEvent(Event.DIR_OPEN, file_path, out_path)
                yield from dir_event_walk(file_path, out_path, fn_match, recursive)
                yield FileEvent(Event.DIR_CLOSE, file_path, out_path)


# def prune_empty_directories(path_in: str):
#     """Walk a file tree removing any empty directories."""
#     # for dirpath, dirnames, filenames in os.walk(path_in, topdown=False):
#     #     pass
#     deleted = set()
#     for current_dir, subdirs, files in os.walk(path_in, topdown=False):
#         still_has_subdirs = any(_ for subdir in subdirs if os.path.join(current_dir, subdir) not in deleted)
#         if not any(files) and not still_has_subdirs:
#             os.rmdir(current_dir)
#             deleted.add(current_dir)
#     return deleted
