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
"""Handles XNAM Logical Records.

Created on Dec 5, 2011

@author: paulross

Example:
0x8d32 Logical Record type 34 Well site data
Well site data table: XNAM
MNEM    TYPE    NAME    ORIG    CNUM
2A     ARRAY     BS     34    0
3A     ARRAY     CS     34    0
4A     ARRAY     TENS    34    0
5A     ARRAY     DEVIM     34    0
6A     ARRAY     RB_MEST     34    0
7A     ARRAY     P1AZ_MEST     34    0
8A     ARRAY     SDEVM     34    0
9A     ARRAY     HAZIM     34    0
10A     ARRAY     RB_GPIT     34    0
11A     ARRAY     P1AZ_GPIT     34    0
12A     ARRAY     TIME    34    0
13A     ARRAY     STIT    34    0

$ python3 TableHistogram.py -ks --name=XNAM ../../../../LISTestData/pLogicTestData/LIS/

============================== Column entries =============================
{(34, b'XNAM', b'CNUM'): 5109,
 (34, b'XNAM', b'MNEM'): 5109,
 (34, b'XNAM', b'NAME'): 5109,
 (34, b'XNAM', b'ORIG'): 5109,
 (34, b'XNAM', b'TYPE'): 5109}
============================ Column entries END ===========================

======================== Count of all table entries =======================
{"(34, b'XNAM', b'TYPE', b'ARRAY   ')": 260,
 "(34, b'XNAM', b'TYPE', b'CHANNEL ')": 50,
 "(34, b'XNAM', b'TYPE', b'CONS')": 28,
 "(34, b'XNAM', b'TYPE', b'PARAMETER   ')": 4732,
 "(34, b'XNAM', b'TYPE', b'TOOL')": 39}
====================== Count of all table entries END =====================



tdlistablehistogram -ksr --name=XNAM  --col=TYPE LIS_LISt/ -l 40

============================== Column entries =============================
defaultdict(<class 'int'>,
            {(34, b'XNAM', b'CNUM'): 8747,
             (34, b'XNAM', b'MNEM'): 8747,
             (34, b'XNAM', b'NAME'): 8747,
             (34, b'XNAM', b'ORIG'): 8747,
             (34, b'XNAM', b'TYPE'): 8747})
============================ Column entries END ===========================

MNEM: Internal menmonic.
NAME: Expanded mnemonic.

======================== Count of all table entries =======================
defaultdict(<class 'int'>,
            {"(34, b'XNAM', b'CNUM', 0)": 8710,
             "(34, b'XNAM', b'CNUM', 1)": 8,
             "(34, b'XNAM', b'CNUM', 10)": 2,
             "(34, b'XNAM', b'CNUM', 11)": 2,
             "(34, b'XNAM', b'CNUM', 2)": 14,
             "(34, b'XNAM', b'CNUM', 3)": 5,
             "(34, b'XNAM', b'CNUM', 4)": 2,
             "(34, b'XNAM', b'CNUM', 7)": 2,
             "(34, b'XNAM', b'CNUM', 8)": 2})
====================== Count of all table entries END =====================

======================== Count of all table entries =======================
defaultdict(<class 'int'>,
            {"(34, b'XNAM', b'ORIG', 109)": 373,
             "(34, b'XNAM', b'ORIG', 14)": 190,
             "(34, b'XNAM', b'ORIG', 20)": 308,
             "(34, b'XNAM', b'ORIG', 22)": 62,
             "(34, b'XNAM', b'ORIG', 26)": 257,
             "(34, b'XNAM', b'ORIG', 27)": 10,
             "(34, b'XNAM', b'ORIG', 28)": 525,
             "(34, b'XNAM', b'ORIG', 30)": 68,
             "(34, b'XNAM', b'ORIG', 34)": 572,
             "(34, b'XNAM', b'ORIG', 43)": 8,
             "(34, b'XNAM', b'ORIG', 44)": 594,
             "(34, b'XNAM', b'ORIG', 5)": 193,
             "(34, b'XNAM', b'ORIG', 52)": 1343,
             "(34, b'XNAM', b'ORIG', 60)": 1268,
             "(34, b'XNAM', b'ORIG', 73)": 524,
             "(34, b'XNAM', b'ORIG', 92)": 2452})
====================== Count of all table entries END =====================

======================== Count of all table entries =======================
defaultdict(<class 'int'>,
            {"(34, b'XNAM', b'TYPE', b'ARRAY   ')": 628,
             "(34, b'XNAM', b'TYPE', b'CHANNEL ')": 50,
             "(34, b'XNAM', b'TYPE', b'CONS')": 28,
             "(34, b'XNAM', b'TYPE', b'PARAMETER   ')": 7958,
             "(34, b'XNAM', b'TYPE', b'TOOL')": 83})
====================== Count of all table entries END =====================


Mapping
-------
From: 200099.S04

"(34, b'XNAM', b'TYPE', b'ARRAY   ')": 260 -> Logical Record type 34 Well site data table: OUTP

"(34, b'XNAM', b'TYPE', b'CHANNEL ')": 50
../../../../LISTestData/pLogicTestData/LIS/300086.S03
../../../../LISTestData/pLogicTestData/LIS/300086.S04
This also refers to Logical Record type 34 Well site data table: OUTP

"(34, b'XNAM', b'TYPE', b'CONS')": 28
../../../../LISTestData/pLogicTestData/LIS/300086.S01
../../../../LISTestData/pLogicTestData/LIS/300086.S02
../../../../LISTestData/pLogicTestData/LIS/300086.S03
../../../../LISTestData/pLogicTestData/LIS/300086.S04
This also refers to Logical Record type 34 Well site data table: CONS


"(34, b'XNAM', b'TYPE', b'PARAMETER   ')": 4732 -> Logical Record type 34 Well site data table: CONS
"(34, b'XNAM', b'TYPE', b'TOOL')": 39 -> Logical Record type 34 Well site data table: TOOL

======================== Count of all table entries =======================
{"(34, b'XNAM', b'ORIG', 22)": 62,
 "(34, b'XNAM', b'ORIG', 27)": 10,
 "(34, b'XNAM', b'ORIG', 30)": 68,
 "(34, b'XNAM', b'ORIG', 34)": 572,
 "(34, b'XNAM', b'ORIG', 43)": 8,
 "(34, b'XNAM', b'ORIG', 44)": 594,
 "(34, b'XNAM', b'ORIG', 52)": 1343,
 "(34, b'XNAM', b'ORIG', 92)": 2452}
====================== Count of all table entries END =====================

======================== Count of all table entries =======================
{"(34, b'XNAM', b'CNUM', 0)": 5088,
 "(34, b'XNAM', b'CNUM', 1)": 3,
 "(34, b'XNAM', b'CNUM', 10)": 2,
 "(34, b'XNAM', b'CNUM', 11)": 2,
 "(34, b'XNAM', b'CNUM', 2)": 8,
 "(34, b'XNAM', b'CNUM', 3)": 4,
 "(34, b'XNAM', b'CNUM', 8)": 2}
====================== Count of all table entries END =====================


2020-08-07
==========

This is not very interesting as XNAM tables only appear in a small number of files processed by Petrologic.
Not found in LIS files from the real world.
They are probably a quirk of the software Petrologic used.
We do not need to support that.
"""
import sys

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

from TotalDepth.LIS.core import LogiRec, FileIndexer
from TotalDepth.LIS import ExceptionTotalDepthLIS


class ExceptionXNAM(ExceptionTotalDepthLIS):
    """Specialisation of exception for Logical Records."""
    pass


class XNAM:
    """Handles XNAM table entries and resolve them."""
    LR_TYPE = LogiRec.LR_TYPE_WELL_DATA
    TABLE_NAME = b'XNAM'
    TABLE_COLS = (b'MNEM', b'TYPE', b'NAME', b'ORIG', b'CNUM')
    TYPE_TO_TABLE_NAME = {
        b'ARRAY   '     : b'OUTP',
        b'CHANNEL '     : b'OUTP',
        b'CONS'         : b'CONS',
        b'PARAMETER   ' : b'CONS',
        b'TOOL'         : b'TOOL',
    }

    def __init__(self, log_pass_index: FileIndexer.IndexLogPass):
        """Constructor takes an FileIndexer.IndexLogPass object. XNAM aliasing is local to the Log Pass"""
        pass

    def resolve(self, mnemonic: bytes, origin: bytes) -> bytes:
        pass


def main():
    # Search files to reverse engineer and test our XNAM logic.

    return 0


if __name__ == '__main__':
    sys.exit(main())
