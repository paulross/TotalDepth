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
import sys


def main() -> int:
    """Searches for likely visible record headers which have 0xff01 as bytes two and three."""
    pos = 0
    with open(sys.argv[1], 'rb') as fobj:
        while True:
            by: bytes = fobj.read(1)
            if len(by) == 0:
                break
            while by == b'\xff':
                by: bytes = fobj.read(1)
                if len(by) == 0:
                    break
                if by == b'\x01':
                    # VR start is two bytes before the start of b'\xff\x01' so minus 4.
                    new_pos = fobj.tell() - 4
                    print(f'VR at 0x{new_pos:08x} previous span 0x{new_pos - pos:08x}')
                    pos = new_pos
    return 0


if __name__ == '__main__':
    sys.exit(main())
