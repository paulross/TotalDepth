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
"""
Created on 4 Jan 2011

@author: p2ross
"""

import logging
import struct
import collections

from TotalDepth.LIS import ExceptionTotalDepthLIS

__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

class ExceptionNamedStruct(ExceptionTotalDepthLIS):
    """Specialisation of exception for NamedStruct."""
    pass

class ExceptionNamedStructInit(ExceptionTotalDepthLIS):
    """Specialisation of exception for ctor of NamedStruct."""
    pass

class NamedStruct(object):
    """Creates a named structure by combining struct.Struct and collections.namedTuple."""
    def __init__(self, theTypeName, theFields, theFmt):
        self._ntClass = collections.namedtuple(theTypeName, theFields)
        self._ntVal = None
        self._st = struct.Struct(theFmt)
        myLenStruct = len(self._st.unpack(b' ' * self._st.size))
        if len(self._ntClass._fields) != myLenStruct:
            raise ExceptionNamedStructInit(
                'NamedStruct.__init__(): specified {:d} fields but struct unpacks to {:d} fields'.format(len(self._ntClass._fields), myLenStruct)
            )
    
    def structSize(self):
        return self._st.size
    
    def __len__(self):
        return len(self._ntClass._fields)
    
    def unpack(self, buffer):
        self._ntValue = self._ntClass._make(self._st.unpack(buffer))
        
    def __getattr__(self, name):
        return getattr(self._ntValue, name)
