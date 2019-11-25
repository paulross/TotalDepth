#!/usr/bin/env python
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 1999-2012 Paul Ross
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
"""Tests ...

Created on Jan 16, 2012

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2012-01-16'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2012 Paul Ross.'

import collections


class ResultOfTests(collections.namedtuple('ResultOfTests', 'testsRun errors failures')):
    #__slots__ = ()
    def __iadd__(self, other):
        """+= implementation. other is None or ResultOfTests(testsRun, errors, failures)."""
        if other is not None:
            self = self._replace(
                testsRun = self.testsRun + other.testsRun,
                errors = self.errors + other.errors,
                failures = self.failures + other.failures,
                )
        return self

    def __str__(self):
        return ''.join(
            [
                '   Tests: %d\n' % self.testsRun,
                '  Errors: %d\n' % self.errors,
                'Failures: %d\n' % self.failures,
            ]
            )
