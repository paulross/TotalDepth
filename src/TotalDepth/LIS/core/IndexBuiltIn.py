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
Attaching an index to a LIS file
================================

Writes a built in index to a LIS file. This index consists of two logical
records; a variable length record that is the index data followed by a fixed
length record that contains, among other things, the absolute location of the
fixed length record.

Pictorially thus:

Start of LIS file: ----------> |------------------------------|
                               |                              |
                               |  LIS data (variable length)  |
                               |                              |
End of LIS file: ------------> |------------------------------|
     SeekIndexDataRecord: ---> |------------------------------| <--|
                               |                              |    |
                               |      Index Data Record       |    |
                               |      (variable length)       |    |
                               |                              |    |
                               |------------------------------|    |
                  EOF-256 ---> |------------------------------|    |
                               |                              |    |
                               |      Tail Index Record       |    |
                               |        (fixed length)        |    |
                               |                              |    |
                               |Value of SeekIndexDataRecord: |--->|
                               |                              |
                               |------------------------------| <--- EOF

The Index Data Record and Tail Index Record are disguised as suitable (binary)
Logical Records so that other LIS processors ignore them. These could be either
type 234 records (Blank record/CSU comment) or invented types that are not in
the LIS specification.

Record types are grouped as follows:
Group 0 - Data records
Group 1 Information records
Group 2 Data format specification records
Group 3 Program records (CSU only)
Group 4 Delimiters
Group 7 Miscellaneous records

Group    Start (decimal)    Start (hex)
0        0                     0x00
1        32                    0x20
2        64                    0x40
3        95                    0x5f
4        128                   0x80
5        N/A (see below)
6        N/A (see below)
7        224                   0xe0 Note: also includes 85 (0x55) and 86 (0x56)

We might guess that group 5 would start at 160, 0xa0 and group 6 at 192, 0xc0.
We could, say, choose a couple towards the end of block 5:
187 0xbb - Index Data Record (variable length)
188 0xbc - Tail Index Record (fixed length)

Reading, writing and validating
===============================

Procedure on write(theIndex):
-----------------------------
- Remove any existing Index Data Record(s) and Tail Index Record(s).
- Get the LIS file checksum and file length. The latter will be the SeekIndexDataRecord
- Take the Index Data Record.
- Write the Tail Index Record with the checksum, SeekIndexDataRecord and padding.

Procedure on read():
--------------------
- Seek to EOF-LEN_TAIL_INDEX_RECORD.
    This may raise an IOError: [Errno 22] Invalid argument
- Create TailIndexRecord().
    This may raise an exception of some sort.
- If Tail Index Record is valid then seek to SeekIndexDataRecord
    from io.SEEK_SET (start of file)
- Create a Index Data Record and extract a serialised LisIndex.

Procedure on validateFile():
----------------------------
TBD.

Tail Index Record structure
===========================
All integers are big-endian.

Block 0
-------
Starts at: 0
LRH: Logical record type 0xbc, attributes 0x00 (2 bytes).
struct.Struct('>2B)
Length: 2

Block 1
-------
Starts at: 2
Magic number: 128bit bytes (16 bytes), treat as 4 off 32bit integers.
Hash type: byte string 32 bytes
Hash: 32 bytes (SHA-256, MD5 would be 16 bytes)
SeekIndexDataRecord: 8 byte unsigned long long
8 bytes double of seconds since the epoch: time.mktime(time.gmtime())
    >>> struct.pack('>d', time.mktime(time.gmtime()))
    b'A\xd3M\x0b\xeb\xc0\x00\x00'

struct.Struct('>4I32s32sQd')

Length: 16+32+32+8+8 = 96 (0x60)

Block 1
-------
Starts at: 98
Reserved: 30 (0x1e)
struct.Struct('>30x')
Length: 30

Block 2
-------
Starts at: 128
Reserved: 128 (0x80)
struct.Struct('>128x')
Length: 128

Total: 2+96+30+128 = 256 (0x100)

The complete record is: struct.Struct('>2B4I32s32sQd30x128x')
Giving 256 bytes, 10 fields.
>>> pprint.pprint(struct.Struct('>2B4I32s32sQd30x128x').unpack(b'\x01'*256))
(1,
 1,
 16843009,
 16843009,
 16843009,
 16843009,
 b'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01',
 b'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01',
 72340172838076673,
 7.748604185489348e-304)

Created on 17 Jan 2011

@author: p2ross
"""

__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

import time
import sys
import logging
from optparse import OptionParser


    