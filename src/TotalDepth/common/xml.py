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
Imports the best XML libraries as etree.
Modified from: https://lxml.de/tutorial.html
"""
try:
    from lxml import etree
    # print("running with lxml.etree")
except ImportError:  # pragma: no cover
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
        # print("running with cElementTree on Python 2.5+")
    except ImportError:  # pragma: no cover
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
            # print("running with ElementTree on Python 2.5+")
        except ImportError:  # pragma: no cover
            try:
                # normal cElementTree install
                import cElementTree as etree
                # print("running with cElementTree")
            except ImportError:  # pragma: no cover
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree
                    # print("running with ElementTree")
                except ImportError:  # pragma: no cover
                    print("Failed to import ElementTree from any known place")
                    raise
