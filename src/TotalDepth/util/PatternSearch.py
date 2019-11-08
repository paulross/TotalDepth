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
"""Searches for runs of data in binary files.

Created on Oct 24, 2011

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2011-10-24'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

import sys
import logging
import time
import multiprocessing
import argparse
import collections
import string

from TotalDepth.common import cmn_cmd_opts

DEFAULT_MIN_RUN_LENGTH = 2
PRINT_WIDTH = 120


def _retHistAll(theFile):
    hist = collections.defaultdict(int)
    while True:
        c = theFile.read(1)
        if len(c) == 0:
            break
        hist[c] += 1
    return hist


def _retHistMatch(thePatt, theFile, theS=sys.stdout, showTell=False):
    hist = collections.defaultdict(int)
    pIdx = 0
    while True:
        myTell = theFile.tell()
        c = theFile.read(1)
        if len(c) == 0:
            break
#        print(ord(c), thePatt[pIdx])
        if ord(c) == thePatt[pIdx]:
            pIdx += 1
            if pIdx == len(thePatt):
                # Full match
                hist[thePatt] += 1
                if showTell:
                    theS.write('0x{0:08x} {1:6d} [0x{1:04x}]\n'.format(myTell - pIdx, pIdx))
                pIdx = 0
        else:
            pIdx = 0
    return hist


def _retHistCharRuns(theCharS, theFile, theS=sys.stdout, theMin=DEFAULT_MIN_RUN_LENGTH, showTell=False):
    hist = collections.defaultdict(int)
    histRun = collections.defaultdict(int)
    tellStart = None
    while True:
        myTell = theFile.tell()
        c = theFile.read(1)
        if len(c) == 0:
            break
        if c in theCharS:
            hist[c] += 1
            if tellStart is None:
                tellStart = myTell
        else:
            if tellStart is not None:
                if myTell - tellStart >= theMin:
                    if showTell:
                        theS.write('0x{0:08x} {1:6d} [0x{1:04x}]\n'.format(tellStart, myTell - tellStart))
                    histRun[myTell-tellStart] += 1
                tellStart = None
    return hist, histRun


def _pprintHist(theH, theS=sys.stdout):
    """Pretty prints a histogram."""
    if len(theH) > 0:
        maxVal = max(theH.values())
        theS.write('Entries: {:d} values: {:d} max value: {:d}\n'.format(len(theH), sum(theH.values()), maxVal))
        keyWidth = max([len((str(k))) for k in theH.keys()])
        scale = maxVal / (PRINT_WIDTH-11-keyWidth)
        theS.write('Scale: {:f}\n'.format(scale))
        for k in sorted(theH.keys()):
            theS.write('{:{fw}s} [{:6d}]: {:s}\n'.format(
                    str(k),
                    theH[k],
                    '+' * int(0.5 + theH[k] / scale),
                    fw=keyWidth,
                )
            )

def _pprintResult(h, hr, theS=sys.stdout):
    """Pretty print the result."""
    theS.write('Found: {:d}\n'.format(sum(h.values())))
    theS.write(' Values '.center(PRINT_WIDTH, '='))
    theS.write('\n')
    _pprintHist(h, theS)
    theS.write(' END Values '.center(PRINT_WIDTH, '='))
    theS.write('\n')
    theS.write(' Run lengths '.center(PRINT_WIDTH, '='))
    theS.write('\n')
    _pprintHist(hr, theS)
    theS.write(' END Run lengths '.center(PRINT_WIDTH, '='))
    theS.write('\n')


def reportAll(theFile, theS=sys.stdout):
    """Print a histogram of byte values."""
    theS.write(' All Bytes '.center(PRINT_WIDTH, '='))
    theS.write('\n')
    _pprintHist(_retHistAll(theFile))
    theS.write(' END All Bytes '.center(PRINT_WIDTH, '='))
    theS.write('\n')


def report0x80(theFile, theS=sys.stdout, theMin=1, showTell=False):
    """Print a for 0x80."""
    theS.write('Searching for 0x80...\n'.format())
    _pprintResult(*_retHistCharRuns(b'\x80', theFile, theS, 1, showTell))


def reportSpaceRuns(theFile, theS=sys.stdout, theMin=DEFAULT_MIN_RUN_LENGTH, showTell=False):
    theS.write('Searching for space runs minimum length {:d}...\n'.format(theMin))
    _pprintResult(*_retHistCharRuns(b' ', theFile, theS, theMin, showTell))


def reportASCIIHigh(theFile, theS=sys.stdout, theMin=DEFAULT_MIN_RUN_LENGTH, showTell=False):
    theS.write('Searching for ASCII > 127 minimum length {:d}...\n'.format(theMin))
    _pprintResult(*_retHistCharRuns(bytes(range(128,256)), theFile, theS, theMin, showTell))


def reportASCII(theFile, theS=sys.stdout, theMin=DEFAULT_MIN_RUN_LENGTH, showTell=False):
    theS.write('Searching for ASCII letters {:d}...\n'.format(theMin))
    charS = bytes([0,]) \
        + bytes(
            string.ascii_letters + string.digits + string.punctuation + string.whitespace, 'ascii')
    _pprintResult(*_retHistCharRuns(charS, theFile, theS, theMin, showTell))


def reportASCIILow(theFile, theS=sys.stdout, theMin=DEFAULT_MIN_RUN_LENGTH, showTell=False):
    theS.write('Searching for ASCII <= 127 minimum length {:d}...\n'.format(theMin))
    _pprintResult(*_retHistCharRuns(bytes(range(0,128)), theFile, theS, theMin, showTell))


def reportASCIIUppercase(theFile, theS=sys.stdout, theMin=DEFAULT_MIN_RUN_LENGTH, showTell=False):
    theS.write('Searching for ASCII uppercase letters {:d}...\n'.format(theMin))
    _pprintResult(*_retHistCharRuns(bytes(string.ascii_uppercase, 'ascii'), theFile, theS, theMin, showTell))


def reportIDENT(theFile, theS=sys.stdout, theMin=DEFAULT_MIN_RUN_LENGTH, showTell=False):
    """IDENT rep code:
    The valid character subset consists of null (0) plus the codes 33 0x21 (!) to
    96 0x60 (`) and from 123 0x7b ({) to 126 0x7e (~) inclusive. This excludes all
    control characters, all "white space", and the lower-case alphabet."""
    theS.write('Searching for IDENT length >= {:d}...\n'.format(theMin))
    charS = bytes([0,] + list(range(33,97)) + list(range(123,127)))
    _pprintResult(*_retHistCharRuns(charS, theFile, theS, theMin, showTell))


def reportSLB(theFile, theS=sys.stdout, theMin=DEFAULT_MIN_RUN_LENGTH, showTell=False):
    theS.write('Searching for incidence of 21 03 53 4C 42 00  i.e. !.SLB.\n')
#    h = _retHistMatch(b'\x21\x03\x53\x4C\x42\x00', theFile, theS, showTell)
    h = _retHistMatch(b'\x03\x53\x4C\x42', theFile, theS, showTell)
#    print(h)
#    _pprintHist(h)
    theS.write(' Values '.center(PRINT_WIDTH, '='))
    theS.write('\n')
    _pprintHist(h, theS)
    theS.write(' END Values '.center(PRINT_WIDTH, '='))
    theS.write('\n')


def reportTOOL(theFile, theS=sys.stdout, theMin=DEFAULT_MIN_RUN_LENGTH, showTell=False):
    theS.write('Searching for incidence of 04 54 4F 4F 4C  i.e. .TOOL\n')
    h = _retHistMatch(b'\x04TOOL', theFile, theS, showTell)
    theS.write(' Values '.center(PRINT_WIDTH, '='))
    theS.write('\n')
    _pprintHist(h, theS)
    theS.write(' END Values '.center(PRINT_WIDTH, '='))
    theS.write('\n')


def main():
    print ('Cmd: %s' % ' '.join(sys.argv))
    op = cmn_cmd_opts.retOptParser(
        desc='Searches for runs of data in binary files.',
        prog='PatternSearch ',
        version=__version__,
    )
    op.add_argument("-s", "--show-tell", action="store_true", dest="show_tell", default=False, 
                      help="Show file locations and lengths. Default: %(default)s.")
    op.add_argument("-n", "--number", dest="min_run_length",
                    type=int, default=DEFAULT_MIN_RUN_LENGTH, 
                    help="Size of the minimum run length. Default: %(default)s.")
    op.add_argument('infile', type=argparse.FileType('rb'), help='The file to search')
    args = op.parse_args()
#    print('TRACE: args', args)
    clkStart = time.clock()
    timStart = time.time()
    # Initialise logging etc.
    logging.basicConfig(level=args.loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    # Your code here
#    reportAll(args.infile)
#    report0x80(args.infile, theMin=args.min_run_length, showTell=args.show_tell)
#    reportSpaceRuns(args.infile, theMin=args.min_run_length, showTell=args.show_tell)
#    reportASCII(args.infile, theMin=args.min_run_length, showTell=args.show_tell)
#    reportASCIIHigh(args.infile, theMin=args.min_run_length, showTell=args.show_tell)
#    reportASCIILow(args.infile, theMin=args.min_run_length, showTell=args.show_tell)
#    reportASCIIUppercase(args.infile, theMin=args.min_run_length, showTell=args.show_tell)
#    reportIDENT(args.infile, theMin=args.min_run_length, showTell=args.show_tell)
#    reportSLB(args.infile, showTell=args.show_tell)
    reportTOOL(args.infile, showTell=args.show_tell)
    print('  CPU time = %8.3f (S)' % (time.clock() - clkStart))
    print('Exec. time = %8.3f (S)' % (time.time() - timStart))
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    multiprocessing.freeze_support()
    sys.exit(main())
