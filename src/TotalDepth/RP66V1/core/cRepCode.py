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

# This is a placeholder can be replaced by 'TotalDepth/RP66V1/core/cRepCode.so'
#     Extension(
#         'TotalDepth.RP66V1.core.cRepCode',
#         sources=[
#             'src/TotalDepth/RP66V1/core/src/cpy/cRepCode.cpp',
#             'src/TotalDepth/RP66V1/core/src/cpp/RepCode.cpp',
#         ],
#         extra_compile_args=extra_compile_args + [
#             '-Isrc/TotalDepth/RP66V1/core/src/cpp',
#             '-std=c++14',
#         ],
#     ),

# Information about floats
# Struct unpack double uses:
# See _PyFloat_Unpack8 in floatobject.c
# That does a simple memcpy if it is IEEE reversing it if the endianness is different.
# Can find out what Python is built with by:
# >>> float.__getformat__('double')
# 'IEEE, little-endian'
# RP66V1 FSINGL and FDOUBL are big endian however so there is a small reversing cost but we probably can't do better.
