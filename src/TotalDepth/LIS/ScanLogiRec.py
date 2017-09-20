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
Created on 10 Nov 2010

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
import struct

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import LogiRec

def dumpTable(lr, theS=sys.stdout):
    for aRow in lr.genRows():
        for aCbev in aRow.genCells():
            theS.write('\t{:s}'.format(aCbev.value))
        theS.write('\n')

def dumpDfsr(lr, theS=sys.stdout):
    theS.write('{:3s} {:7s} {:9s} {:11s} {:7s} {:11s} {:4s} {:4s} {:4s} {:4s} {:4s}'.format(
            '', 'Name', 'SrvID', 'SrvOrd', 'UoM', 'API Codes', 'Size', 'Samp', 'RC', 'Brst', 'SubC'
        )
    )
    theS.write('\n')
    for i, d in enumerate(lr.dsbBlocks):
        theS.write('%3d %s %s %s %s %2d-%2s-%2d-%1d %4d %4d %4d %4d %4d' % \
            (
                i,
                d.mnem,
                d.servId,
                d.servOrd,
                d.units,
                d.apiLogType,
                d.apiCurveType,
                d.apiCurveClass,
                d.apiModifier,
                d.size,
                d.samples(0),
                d.repCode,
                d.bursts(0),
                d.subChannels,
            )
        )
        theS.write('\n')

def dumpLr(theLr, theS=sys.stdout):
    DUMP_MAP = {
        LogiRec.LR_TYPE_JOB_ID      : dumpTable,
        LogiRec.LR_TYPE_WELL_DATA   : dumpTable,
        LogiRec.LR_TYPE_TOOL_INFO   : dumpTable,
        LogiRec.LR_TYPE_DATA_FORMAT : dumpDfsr,
    }
    try:
        DUMP_MAP[theLr.type](theLr)
    except KeyError:
        pass

def scanFile(fp, isVerbose, keepGoing, theS=sys.stdout):
    try:
        myFile = File.FileRead(fp, fp, keepGoing)
    except File.ExceptionFile as err:
        print('Can not open file, error: %s' % str(err))
        return
    myFactory = LogiRec.LrFactoryRead()
    while not myFile.isEOF:
        myTellLr = myFile.tellLr()
        try:
            myLr = myFactory.retLrFromFile(myFile)
            if myLr is not None:
                print('0x{:08x}'.format(myTellLr), str(myLr))
                if isVerbose:
                    dumpLr(myLr)
        except LogiRec.ExceptionLr as err:
            pass
            #logging.error('LR at 0x{:08x}: {:s}'.format(myTellLr, err))
        myFile.skipToNextLr()
        
def main():
    usage = """usage: %prog [options] file
Scans a LIS79 file and dumps Logical Records."""
    print('Cmd: %s' % ' '.join(sys.argv))
    optParser = OptionParser(usage, version='%prog ' + __version__)
    optParser.add_option("-k", "--keep-going", action="store_true", dest="keepGoing", default=False, 
                      help="Keep going as far as sensible. [default: %default]")
    optParser.add_option(
            "-l", "--loglevel",
            type="int",
            dest="loglevel",
            default=20,
            help="Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: %default]"
        )      
    optParser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, 
                      help="Verbose Output. [default: %default]")
    opts, args = optParser.parse_args()
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    # Your code here
    if len(args) == 1:
        scanFile(args[0], opts.verbose, opts.keepGoing)
    else:
        optParser.print_help()
        optParser.error("Wrong number of arguments, I need one only.")
        return 1
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    #multiprocessing.freeze_support()
    sys.exit(main())