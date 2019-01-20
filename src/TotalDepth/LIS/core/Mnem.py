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
"""Represents a MNEM (Mnemonic) as bytes.
Created on May 26, 2011

@author: paulross
"""
import string

#: A tuple of the ordinal values of whitespace characters
ORDS_WS = tuple([ord(c) for c in string.whitespace])
#: A tuple of the ordinal values of characters that can be replaced with PAD_CHAR
ORDS_REPLACE = tuple((0,)) + ORDS_WS
#: Standard LIS mnemonic length
LEN_MNEM = 4
# Pad character for replacement so that Mnem(b'GR  ') is equivalent to Mnem(b'GR \x00')
PAD_CHAR = b'\x00'

class Mnem(object):
    """Represents a four byte mnemonic where tailing nulls and spaces are not
    considered significant. This preserves original length but replaces trailing
    \x00 and whitespace characters with the PAD_CHAR.
    
    m must be a bytes object or an 'ascii' str that can be converted to a bytes object.
    
    If len_mnem is positive then m is truncated or padded as necessary to
    achieve that length.
    
    If len_mnem is zero then all of m is considered significant, no padding
    is performed.
    
    If len_mnem is less than zero then all characters of m are considered
    significant and padding up to -1*len_mnem characters of m is 
    performed if m smaller than that.    
    """
    def __init__(self, m, len_mnem=LEN_MNEM):
        """Constructor that prunes trailing nulls and spaces."""
        if isinstance(m, str):
            m = bytes(m, 'ascii')
        # Figure out behaviour depending on len_mnem
        if len_mnem == 0:
            # All m is significant, no padding no truncation
            i = len_mnem = len(m)
        elif len_mnem < 0:
            # All m is significant, no truncation but pad if small
            len_mnem = max(-len_mnem, len(m))
            i = len(m)
        else:
            # First len_mnem characters are significant, truncate if large, pad if small
            i = min(len_mnem, len(m))
        i -= 1
        while i >= 0:
            if m[i] not in ORDS_REPLACE:
                break
            i -= 1
        i += 1
        if i == len_mnem:
            self._m = m[:i]
        else:
            self._m = m[:i] + PAD_CHAR * (len_mnem - i)
        
    @property
    def m(self):
        """The raw bytes of the mnemonic."""
        return self._m
    
    def __str__(self):
        """String representation."""
        return self._m.decode('ascii')#.replace('\x00', ' ')
    
    def pStr(self, strip=False):
        """Returns a 'pretty' ascii string. If strip then trailing padding is removed."""
        if strip:
            return self._m.replace(PAD_CHAR, b'').decode('ascii')
        return self._m.replace(PAD_CHAR, b' ').decode('ascii')
    
    def __repr__(self):
        """repr() representation."""
        return 'Mnem({!s:s})'.format(self._m)
    
    def __hash__(self):
        """Hashing, this makes bytes() and Mnem() objects interchangeable."""
        return hash(self._m)
    
    def __eq__(self, other):
        """True if self == other False otherwise.
        If other is not a Mnem it is coerced into one before the comparison is made.."""
        if isinstance(other, Mnem):
            return self._m == other._m
        return self._m == Mnem(other).m
    
    def __ne__(self, other):
        """True if self != other False otherwise.
        If other is not a Mnem it is coerced into one before the comparison is made.."""
        if isinstance(other, Mnem):
            return self._m != other._m
        return self._m != Mnem(other).m

    def __lt__(self, other):
        """True if self < other False otherwise.
        If other is not a Mnem it is coerced into one before the comparison is made.."""
        if isinstance(other, Mnem):
            return self._m < other._m
        return self._m < Mnem(other).m
    
    def __iter__(self):
        """Byte by byte iteration."""
        for b in self._m:
            yield b
    