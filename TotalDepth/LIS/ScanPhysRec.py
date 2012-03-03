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
# Paul Ross: cpipdev@googlemail.com
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

from TotalDepth.LIS.core import PhysRec
from TotalDepth.util import Histogram

# One byte for type, on for attributes
LD_STRUCT_HEAD = struct.Struct('>BB')
assert(LD_STRUCT_HEAD.size == 2)

def scanFile(fp, keepGoing, theS=sys.stdout):
    try:
        myPrh = PhysRec.PhysRecRead(fp, fp, keepGoing)
    except PhysRec.ExceptionPhysRec as err:
        print('Can not open file, error: %s' % str(err))
        return
    # Now other stuff generated by this loop
    myHeader = myPrh.strHeader() + '   LR Attr [Total LD]'
    theS.write(myHeader)
    theS.write('\n')
    theS.write(' start '.center(len(myHeader), '-'))
    myLdSum = -1
    numPR = 0
    # Histogram of PR lengths
    myLenHist = Histogram.Histogram()
    for myLd, isLdStart in myPrh.genLd():
        myLenHist.add(myPrh.prLen)
        if isLdStart:
            if myLdSum == -1:
                # First time through the loop then don't write anything
                pass
            else:
                # This is not the first time through the loop
                # so write out the trailing LogicalData length
                theS.write(' [%8d]' % myLdSum) 
            myLdSum = 0
        myLdSum += len(myLd)
        theS.write('\n')
        theS.write(str(myPrh))
        if isLdStart:
            #theS.write(' >')
            #theS.write(' 0x{0:08X}'.format(myPrh.tellLr()))
            if len(myLd) >= 2:
                #print(myLd)
                h, a = LD_STRUCT_HEAD.unpack(myLd[:LD_STRUCT_HEAD.size])
                theS.write(' 0x{0:02X} 0x{1:02x}'.format(h, a))
            else:
                theS.write(' 0x??')
        else:
            theS.write(' + --   --')
        #theS.write(' %6d' % len(myLd))
        numPR += 1
    theS.write(' [%8d]' % myLdSum)
    theS.write('\n')
    theS.write('%s\n' % str(myPrh))
    theS.write(' EOF '.center(len(myHeader), '-'))
    theS.write('\n')
    theS.write('PR Count: %d\n' % numPR)
    theS.write('Histogram of Physical Record lengths:\n')
    theS.write(myLenHist.strRep(100, valTitle='Bytes', inclCount=True))
    theS.write('\n')

def main():
    usage = """usage: %prog [options] file
Scans a LIS79 file and reports Physical Record structure."""
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
    opts, args = optParser.parse_args()
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    # Your code here
    if len(args) == 1:
        scanFile(args[0], opts.keepGoing)
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

    
    
    