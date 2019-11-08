#!/usr/bin/env python
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 1999-2011 Paul Ross
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
import typing

__author__  = 'Paul Ross'
__date__    = '2011-06-09'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'

import os
import fnmatch
import collections

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


def dirWalk(theIn: str, theOut: str = '', theFnMatch: str = '',
            recursive: bool = False, bigFirst: bool = False) -> typing.Sequence[FileInOut]:
    """Walks a directory tree generating file paths as FileInOut(in, out) objects.

    theIn - The input directory.

    theOut - The output directory. If an empty string the out path will be an empty string.
    NOTE: This does not create the output directory structure, it is up to
    the caller to do that.

    theFnMatch - A glob like match pattern for file names (not tested for directory names).

    recursive - Boolean to recurse or not.

    bigFirst - If True then the largest files in  directory are given first. If False it is alphabetical.
    """
    # print(f'theIn="{theIn}" theOut="{theOut}"')
    if not os.path.isdir(theIn):
        raise ExceptionDirWalk('{:s} is not a directory.'.format(theIn))
    if bigFirst:
        # First files
        for fn in gen_big_first(theIn):
            fp = os.path.join(theIn, fn)
            if not theFnMatch or fnmatch.fnmatch(fp, theFnMatch):
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
            if os.path.isfile(fp) and (not theFnMatch or fnmatch.fnmatch(fp, theFnMatch)):
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
