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

Created on Oct 11, 2011

@author: paulross

See RP66v2 Sect. 8.6:

Table 10 - Attribute Components
*Note    Format Bit    Symbol    Characteristic    Representation Code    Global Default Value
1    5    l    label    IDENT    (see note)
2    4    c    count    UVARI    1
2    3    r    representation code    USHORT    IDENT
2    2    u    unit    UNITS    null
3    1    v    value    (see note)    null
"""

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

import TotalDepth.RP66.core.RepCode as RepCode

class AttrCompBase(object):
    """Represents an Attribute Component. See RP66v2 Sect. 8.6."""
    # Global defaults
    DEFAULT_COUNT = 1
    DEFAULT_REP_CODE = 19
    # Rep code IDENT
    lable = None
    # Rep code UVARI, defaults to 1
    count = 1
    # Rep code USHORT, defaults to IDENT (19)
    repCode = 19
    # Rep code UNITS
    units = None
    # Single value or list of values if count > 1
    value = None
    
    def __str__(self):
        return 'lable={:s} count={:s} rc={:s} ({:s}) units={:s} value={:s}'.format(
            str(self.lable),
            str(self.count),
            str(self.repCode),
            RepCode.codeToName(self.repCode),
            str(self.units),
            str(self.value),
        )

    def read(self, formatBits, theStream):
        if formatBits & 0x10:
            self.lable = RepCode.IDENTStream(theStream)
        if formatBits & 0x8:
            self.count = RepCode.readUVARI(theStream)
#        else:
#            self.count = self.DEFAULT_COUNT
        if formatBits & 0x4:
            self.repCode = RepCode.readUSHORT(theStream)
#        else:
#            self.repCode = self.DEFAULT_REP_CODE
#        print('TRACE: self.repCode', self.repCode)
        if formatBits & 0x2:
            self.units = RepCode.UNITSStream(theStream)
        if formatBits & 0x1:
            if self.count > 1:
                self.value = [RepCode.readIndirectRepCode(self.repCode, theStream) for i in range(self.count)]
            else:
                self.value = RepCode.readIndirectRepCode(self.repCode, theStream)
    
    def readAsTemplate(self, formatBits, theStream):
        """Treats self as a template and reads from a stream.
        Returns a new AttrCompBase with the merged attributes."""
        r  = AttrCompBase()
        for k in self.__dict__.keys():
            attr = getattr(self, k)
            setattr(r, k, attr)
#        print('TRACE: r', r)
        r.read(formatBits, theStream)
        return r

class AttrCompStream(AttrCompBase):
    def __init__(self, formatBits, theStream):
        """Constructed with a bit mask whose 5 bits determine which field to
        read from the stream."""
        super().__init__()
        self.read(formatBits, theStream)

