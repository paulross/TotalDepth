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
"""Abstraction over colorama
"""
import contextlib
import sys
import typing

import colorama

colorama.init(autoreset=True)


STANDARD_TEXT_WIDTH = 75


@contextlib.contextmanager
def section(title: str, fillchar: str, colour: colorama.ansi.AnsiFore = colorama.Fore.GREEN,
            width: int = STANDARD_TEXT_WIDTH,
            out_stream: typing.TextIO = sys.stdout):
    """Write a coloured header and trailer."""
    try:
        s = colour + f' {title} '.center(width, fillchar) + '\n'
        out_stream.write(s)
        yield
    finally:
        s = colour + f' END {title} '.center(width, fillchar) + '\n'
        out_stream.write(s)
