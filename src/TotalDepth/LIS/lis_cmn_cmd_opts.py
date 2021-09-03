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
"""
Common command line options for LIS tools.
"""
import argparse


def add_physical_record_padding_options(arg_parser: argparse.ArgumentParser) -> None:
    arg_parser.add_argument("--pad-modulo", type=int, default=0,
                         help="Consume pad bytes up to tell() modulo this value, typically 2 or 4. [default: %(default)s]")
    arg_parser.add_argument("--pad-non-null", action="store_true", default=False,
                         help="Pad bytes can be non-null bytes. Only relevant if --pad-modulo > 0 [default: %(default)s]")
