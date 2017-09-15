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
"""Reads a LIS file and writes out tab separated values of each frame.

Created on 25 Mar 2011

@author: p2ross
"""
__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

import time
import sys
import os
import logging
from optparse import OptionParser

#from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import FileIndexer
from TotalDepth.LIS.core import FrameSet

def dumpFrameSets(fp, keepGoing, summaryOnly):
    logging.info('Index.indexFile(): {:s}'.format(fp))
    assert(os.path.isfile(fp))
    myFi = File.FileRead(fp, theFileId=fp, keepGoing=keepGoing)
    myIdx = FileIndexer.FileIndex(myFi)
    for aLp in myIdx.genLogPasses():
        print(aLp)
        # Load the FrameSet
        if aLp.logPass.totalFrames == 0:
            print('No frames to load.')
        else:
            aLp.logPass.setFrameSet(myFi, None, None)
            myFrSet = aLp.logPass.frameSet
            if not summaryOnly:
                # Print the channels and units
                hdrS = []
                if myFrSet.isIndirectX:
                    hdrS.append('XAXIS [{:s}]'.format(myFrSet.xAxisDecl.depthUnits))
                hdrS.extend(['{:s} [{:s}]'.format(m, u) for m,u in aLp.logPass.genFrameSetHeadings()])
                #print('TRACE: len(hdrS)', len(hdrS))
                print('\t'.join(hdrS))
                for frIdx in range(myFrSet.numFrames):
                    #print('TRACE: len(frame)', len(myFrSet.frame(frIdx)))
                    if myFrSet.isIndirectX:
                        print(myFrSet.xAxisValue(frIdx), '\t', end='')
                    print('\t'.join(['%g' % v for v in myFrSet.frame(frIdx)]))
            # Accumulate min/mean/max
            myAccClasses = [
                    FrameSet.AccCount,
                    FrameSet.AccMin,
                    FrameSet.AccMean,
                    FrameSet.AccMax,
                    FrameSet.AccStDev,
                    FrameSet.AccDec,
                    FrameSet.AccEq,
                    FrameSet.AccInc,
                    FrameSet.AccBias,
                    FrameSet.AccDrift,
                    FrameSet.AccActivity,
            ]
            myAcc = myFrSet.accumulate(myAccClasses)
            print()
            fmtStr = '{:12s} ' + (' {:>12s}'*len(myAccClasses)) 
            print(fmtStr.format(
                    'Sc Name', 'Count', 'Min', 'Mean', 'Max', 'Std Dev.', '--', '==', '++', 'Bias', 'Drift', 'Activity',
                )
            )
            schNameS = list(aLp.logPass.genFrameSetScNameUnit())
#            print(schNameS)
            for scIdx, aRow in enumerate(myAcc):
                print('{:4s} [{:4s}]'.format(*schNameS[scIdx]),
                      ' ',
                      ' '.join(['{:12.5g}'.format(v) for v in aRow]))

def main():
    usage = """usage: %prog [options] dir
Reads a LIS file and writes out tab separated values of each frame."""
    print ('Cmd: %s' % ' '.join(sys.argv))
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
    optParser.add_option("-s", "--summary", action="store_true", dest="summary", default=False, 
                      help="Display summary only. [default: %default]")
    opts, args = optParser.parse_args()
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    # Your code here
    if len(args) != 1:
        optParser.print_help()
        optParser.error("I can't do much without a path to the LIS file.")
        return 1
    dumpFrameSets(args[0], opts.keepGoing, opts.summary)
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    #multiprocessing.freeze_support()
    sys.exit(main())

    
    
    