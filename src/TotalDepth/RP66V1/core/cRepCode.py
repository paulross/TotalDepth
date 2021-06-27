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
#
# Might be worth doing an experiment: Reading large binary files of int/long/float/double with Python struct and
# C++ os >> foo to establish some bound of the maximum throughput of Python and C++.
# Try also with endian conversion.
# If the performance is very similar then there is no reason to have a C++ version.

# Intermediate Index - Contains the initial fields of EFLR and IFLR.
#
# If we have an intermediate index (the initial fields of each EFLR and IFLR).
# EFLR:
# -----
# The initial bytes go into a Set object.
#
# class Set:
#     """Class that represents a component set. See [RP66V1 3.2.2.1 Component Descriptor]"""
#     def __init__(self, ld: LogicalData):
#         ld_index = ld.index
#         component_descriptor = ComponentDescriptor(ld.read())
#         if not component_descriptor.is_set_group:
#             raise ExceptionEFLRSet(f'Component Descriptor does not represent a set but a {component_descriptor.type}.')
#         self.type: bytes = RepCode.IDENT(ld)
#         self.name: bytes = ComponentDescriptor.CHARACTERISTICS_AND_COMPONENT_FORMAT_SET_MAP['N'].global_default
#         if component_descriptor.has_set_N:
#             self.name = RepCode.IDENT(ld)
#         self.logical_data_consumed = ld.index - ld_index
#
# So we need ComponentDescriptor that takes a single byte.
# TotalDepth.RP66V1.core.LogicalRecord.ComponentDescriptor.ComponentDescriptor could easily be implemented in C/C++.
# And two IDENTs (Pascal strings).
#
# IFLR:
# -----
# IFLR needs OBNAME and UVARI:
#         # [RP66V1 Section 3.3 Indirectly Formatted Logical Record]
#         self.object_name: RepCode.ObjectName = RepCode.OBNAME(ld)
#         # [RP66V1 Section 5.6.1 Frames]
#         self.frame_number = RepCode.UVARI(ld)
#
# OBNAME is:
#     o = ORIGIN(ld)
#     c = USHORT(ld)
#     i = IDENT(ld)
#
# ORIGIN is UVARI
#
# So, as a minimum implement ComponentDescriptor and Representation Codes IDENT (std::string), UVARI (uint_32) and
# USHORT (uint_8).
