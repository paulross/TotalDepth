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
"""Cython code for FrameSet."""

#__author__  = 'Paul Ross'
#__date__    = '11 Dec 2011'
#__version__ = '0.8.0'
#__rights__  = 'Copyright (c) Paul Ross'

#import numpy as np
#cimport numpy
#cimport cython
#
#@cython.boundscheck(False)
#def dec(numpy.ndarray[np.float64_t, ndim=1] a not None):
def dec(a):
    """Returns the number of values that are less than their previous value in the array a."""
    cdef Py_ssize_t i
    cdef Py_ssize_t r = 0
    cdef Py_ssize_t n = a.shape[0]
    cdef double prev = 0.0
    for i in range(n):
        if i > 0:
            if a[i] < prev:
                r += 1
        prev = a[i]
    return r

def eq(a):
    """Returns the number of values that are equal to their previous value in the array a."""
    cdef Py_ssize_t i
    cdef Py_ssize_t r = 0
    cdef Py_ssize_t n = a.shape[0]
    cdef double prev = 0.0
    for i in range(n):
        if i > 0:
            if a[i] == prev:
                r += 1
        prev = a[i]
    return r

def inc(a):
    """Returns the number of values that are greater than their previous value in the array a."""
    cdef Py_ssize_t i
    cdef Py_ssize_t r = 0
    cdef Py_ssize_t n = a.shape[0]
    cdef double prev = 0.0
    for i in range(n):
        if i > 0:
            if a[i] > prev:
                r += 1
        prev = a[i]
    return r

def decEqInc(a):
    """Returns the three values <, ==, > than their previous value in the array a."""
    cdef Py_ssize_t i
    cdef Py_ssize_t rd = 0
    cdef Py_ssize_t re = 0
    cdef Py_ssize_t ri = 0
    cdef Py_ssize_t n = a.shape[0]
    cdef double prev = 0.0
    for i in range(n):
        if i > 0:
            if a[i] > prev:
                rd += 1
            elif a[i] == prev:
                re += 1
            else:
                ri += 1
        prev = a[i]
    return rd, re, ri
