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
FileInOut = collections.namedtuple('FileInOut', 'filePathIn, filePathOut')


class ExceptionDirWalk(ExceptionTotalDepth):
    """Exception class for this module."""
    pass


def genBigFirst(d):
    """Generator that yields the biggest files (name not path) first.
    This is fairly simple in that it it only looks the current directory not
    only sub-directories. Useful for multiprocessing."""
    # Map of {size : [name, ...], ...}
    m = {}
    for n in os.listdir(d):
        p = os.path.join(d, n)
        if os.path.isfile(p):
            s = os.path.getsize(p)
            try:
                m[s].append(p)
            except KeyError:
                m[s] = [n,]
    for s in sorted(m.keys(), reverse=True):
        for p in m[s]:
            yield p


def dirWalk(theIn: str, theOut: str='', theFnMatch: str='',
            recursive: bool=False, bigFirst: bool=False) -> typing.Sequence[FileInOut]:
    """Walks a directory tree generating file paths.

    theIn - The input directory.

    theOut - The output directory. If None then input file paths as strings
    will be generated If non-None this function will yield
    FileInOut(in, out) objects.
    NOTE: This does not create the output directory structure, it is up to
    the caller to do that.

    theFnMatch - A glob like match pattern for file names (not tested for directory names).

    recursive - Boolean to recurse or not.

    bigFirst - If True then the largest files in  directory are given first. If False it is alphabetical.
    """
    if not os.path.isdir(theIn):
        raise ExceptionDirWalk('{:s} is not a directory.'.format(theIn))
    if bigFirst:
        # First files
        for fn in genBigFirst(theIn):
            fp = os.path.join(theIn, fn)
            if not theFnMatch or fnmatch.fnmatch(fp, theFnMatch):
                out_file = ''
                if theOut:
                    out_file = os.path.join(theOut, fn)
                yield FileInOut(fp, out_file)
        # Now directories
        if recursive:
            for n in os.listdir(theIn):
                fp = os.path.join(theIn, n)
                if os.path.isdir(fp):
                    out_path = ''
                    if not theOut:
                        out_path = os.path.join(theOut, n)
                    for aFp in dirWalk(fp, out_path, theFnMatch, recursive, bigFirst):
                        yield aFp
    else:
        # Straightforward list in alphanumeric order
        for n in os.listdir(theIn):
            fp = os.path.join(theIn, n)
            if os.path.isfile(fp) \
            and (not theFnMatch or fnmatch.fnmatch(fp, theFnMatch)):
                out_file = ''
                if theOut:
                    out_file = os.path.join(theOut, n)
                yield FileInOut(fp, out_file)
            elif os.path.isdir(fp) and recursive:
                out_path = ''
                if not theOut:
                    out_path = os.path.join(theOut, n)
                for aFp in dirWalk(fp, out_path, theFnMatch, recursive):
                    yield aFp
