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
"""Does...

Created on Oct 27, 2011

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

import sys
import logging
import time
import multiprocessing
import collections
import argparse
from TotalDepth.util import CmnCmdOpts
from TotalDepth.util import FileBuffer


"""From Appendix A of the spec:
Code    Type    Description    Allowable Set Types
0    FHLR    File Header    FILE-HEADER
1    OLR    Origin    ORIGIN
WELL-REFERENCE
2    AXIS    Coordinate Axis    AXIS
3    CHANNL    Channel-related information    CHANNEL
4    FRAME    Frame Data    FRAME
PATH
5    STATIC    Static Data    CALIBRATION
CALIBRATION-COEFFICIENT
CALIBRATION-MEASUREMENT
COMPUTATION
EQUIPMENT
GROUP
PARAMETER
PROCESS
SPICE
TOOL
ZONE
6    SCRIPT    Textual Data    COMMENT    MESSAGE
7    UPDATE    Update Data    UPDATE
8    UDI    Unformatted Data Identifier    NO-FORMAT
9    LNAME    Long Name    LONG-NAME
10    SPEC    Specification    ATTRIBUTE
CODE
EFLR
IFLR
OBJECT-TYPE
REPRESENTATION-CODE
SPECIFICATION
UNIT-SYMBOL
11    DICT    Dictionary    BASE-DICTIONARY
IDENTIFIER
LEXICON
OPTION
12-127    -    undefined, reserved    -

"""

EFLRType = collections.namedtuple('EFLRType', 'type description setTypes')

class ScanV1EFLR(object):
    """Class documentation."""
    "Code    Type    Description    Allowable Set Types"
    EFLR_TYPE_MAP = {       
        0   : EFLRType(
                'FHLR',
                'File Header',
                [
                    b'FILE-HEADER',
                ]
               ),
        1   : EFLRType(
                'OLR',
                'Origin',
                [
                    b'ORIGIN',
                    b'WELL-REFERENCE',
                ]
               ),
        2   : EFLRType(
                'AXIS',
                'Coordinate Axis',
                [
                    b'AXIS',
                ]
               ),
        3   : EFLRType(
                'CHANNL',
                'Channel-related information',
                [
                    b'CHANNEL',
                ]
               ),
        4   : EFLRType(
                'FRAME',
                'Frame Data',
                [
                    b'FRAME',
                    b'PATH',
                ]
               ),
        5   : EFLRType(
                'STATIC',
                'Static Data',
                [
                    b'CALIBRATION',
                    b'CALIBRATION-COEFFICIENT',
                    b'CALIBRATION-MEASUREMENT',
                    b'COMPUTATION',
                    b'EQUIPMENT',
                    b'GROUP',
                    b'PARAMETER',
                    b'PROCESS',
                    b'SPICE',
                    b'TOOL',
                    b'ZONE',
                ]
               ),
        6   : EFLRType(
                'SCRIPT',
                'Textual Data',
                [
                    b'COMMENT',
                    b'MESSAGE',
                ]
               ),
        7   : EFLRType(
                'UPDATE',
                'Update Data',
                [
                    b'UPDATE',
                ]
               ),
        8   : EFLRType(
                'UDI',
                'Unformatted Data Identifier',
                [
                    b'NO-FORMAT',
                ]
               ),
        9   : EFLRType(
                'LNAME',
                'Long Name',
                [
                    b'LONG-NAME',
                ]
               ),
        10   : EFLRType(
                'SPEC',
                'Specification',
                [
                    b'ATTRIBUTE',
                    b'CODE',
                    b'EFLR',
                    b'IFLR',
                    b'OBJECT-TYPE',
                    b'REPRESENTATION-CODE',
                    b'SPECIFICATION',
                    b'UNIT-SYMBOL',
                ]
               ),
        11   : EFLRType(
                'DICT',
                'Dictionary',
                [
                    b'BASE-DICTIONARY',
                    b'IDENTIFIER',
                    b'LEXICON',
                    b'OPTION',
                ]
               ),
    }
    IDX_ATTR = 2
    IDX_TYPE = 3
    IDX_NAME_LEN = 5
    IDX_NAME_VALUE = 6
    def __init__(self, theF):
        self._fb = FileBuffer.FileBuffer(theF)
        tellPrev = 0
        while True:
            try:
                attr = self._fb[self.IDX_ATTR]
            except IndexError:
                break
            # Attribute must match 10xxxxxx i.e. EFL and the first segment (no predecessor)
            if attr & 0x80 > 0 and attr & 0x40 == 0:
                typeCode = self._fb[self.IDX_TYPE]
                if typeCode in self.EFLR_TYPE_MAP:
                    l = self._fb[self.IDX_NAME_LEN]
                    if l > 0:
                        name = self._fb[self.IDX_NAME_VALUE:self.IDX_NAME_VALUE+l]
#                        print('TRACE: name', name)
                        if name in self.EFLR_TYPE_MAP[typeCode].setTypes:
                            # Got one!
                            length = (self._fb[0] << 8) + self._fb[1]
                            print('LRSH 0x{:08x} (+0x{:06x}) len={:6d} [0x{:04x}] attr=0x{:x} [{:b}] EFLR code={:d} name: {:s}'.format(
                                    self._fb.tell(),
                                    self._fb.tell() - tellPrev,
                                    length,
                                    length,
                                    attr,
                                    attr,
                                    typeCode,
                                    name.decode("UTF8"),
                                )
                            )
                            tellPrev = self._fb.tell()
            self._fb.step()
        print(' EOF 0x{:08x} (+0x{:06x})'.format(
                self._fb.tell(),
                self._fb.tell() - tellPrev,
            )
        )

def main():
    print ('Cmd: %s' % ' '.join(sys.argv))
    op = CmnCmdOpts.argParserIn(
        desc='Searches for structures that look like RP66v1 EFLRs',
        prog='%(prog) ',
        version=__version__,
    )
    op.add_argument("-s", "--show-tell", action="store_true", dest="show_tell", default=False, 
                      help="Show file locations and lengths. Default: %(default)s.")
#    op.add_argument("-n", "--number", dest="min_run_length",
#                    type=int, default=DEFAULT_MIN_RUN_LENGTH, 
#                    help="Size of the minimum run length. Default: %(default)s.")
    op.add_argument('infile', type=argparse.FileType('rb'), help='The file to search')
    args = op.parse_args()
    clkStart = time.clock()
    timStart = time.time()
    # Initialise logging etc.
    #logging.basicConfig(level=args.loglevel,
    #                format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
    #                stream=sys.stdout)
    # Your code here
    myObj = ScanV1EFLR(args.infile)
    
    print('  CPU time = %8.3f (S)' % (time.clock() - clkStart))
    print('Exec. time = %8.3f (S)' % (time.time() - timStart))
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    multiprocessing.freeze_support()
    sys.exit(main())
