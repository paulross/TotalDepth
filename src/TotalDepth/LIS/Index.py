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
"""Indexes LIS files and reports performance.

Created on 24 Feb 2011

@author: p2ross

Indexing errors on LIS files:


[34] TotalDepth.LIS.core.TifMarker.ExceptionTifMarker: TIF read() expected 0x50, got tell: 0x4A, Shortfall: 0x6
Fixed.

[24] TotalDepth.LIS.core.LogiRec.ExceptionEntryBlock: EntryBlockSet.setEntryBlock(): type 10 excluded from EntryBlockSet
Fixed.

[ 2] TotalDepth.LIS.core.Type01Plan.ExceptionFrameSetPlan: Can not fit integer number of frames length 120 into LR length 824, modulo 104 [indirect size 0].
Two file have different problems:

13576.S1
--------
W:\openLIS\src\TotalDepth.LIS>python Index.py -rk -l40 ..\..\..\pLogicTestData\LIS\13576.S1
...
TotalDepth.LIS.core.Type01Plan.ExceptionFrameSetPlan: Can not fit integer number of frames length 120 into LR length 824, modulo 104 [indirect size 0].

Looks like the last PR is truncated:
...
TIF  True >:  0x       0  0x   19006  0x   197b6  PR: 0x   193de     972  0x9600     962  0x006c  0x0001  0xa2e1 0x00 0x00 [     962]
TIF  True >:  0x       0  0x   193de  0x   19b06  PR: 0x   197b6     836  0x9600     826  0x006d  0x0001  0x0304 0x00 0x00 [     826]
Missing 962-826 bytes 136 bytes.

13610.S1
--------
W:\openLIS\src\TotalDepth.LIS>python Index.py -rk -l40 ..\..\..\pLogicTestData\LIS\13610.S1
...
TotalDepth.LIS.core.Type01Plan.ExceptionFrameSetPlan: Can not fit integer number of frames length 7176 into LR length 13354, modulo 6178 [indirect size 0].

This looks like a bad PR header at 0x3a986 that has set a successor bit:
W:\openLIS\src\TotalDepth.LIS>python ScanPhysRec.py ..\..\..\pLogicTestData\LIS\13610.S1
Cmd: ScanPhysRec.py ..\..\..\pLogicTestData\LIS\13610.S1
TIF     ?  :        Type        Back        Next  PR:     tell()  Length    Attr  LD_len  RecNum  FilNum  ChkSum   LR Attr [Total LD]
TIF  True >:  0x       0  0x       0  0x      4a  PR: 0x       0      62  0x8000      58  ------  ------  ------ 0x80 0x00 [      58]
TIF  True >:  0x       0  0x       0  0x     3ac  PR: 0x      4a     854  0x8000     850  ------  ------  ------ 0x40 0x00 [     850]
...
TIF  True >:  0x       0  0x   390f4  0x   395ae  PR: 0x   394ec     182  0x8001     178  ------  ------  ------ 0x00 0x00
TIF  True >:  0x       0  0x   394ec  0x   399a6  PR: 0x   395ae    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   395ae  0x   39d9e  PR: 0x   399a6    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   399a6  0x   3a196  PR: 0x   39d9e    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   39d9e  0x   3a58e  PR: 0x   3a196    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3a196  0x   3a986  PR: 0x   3a58e    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3a58e  0x   3ad7e  PR: 0x   3a986    1004  0x8003    1000  ------  ------  ------ + ---- ----
2011-03-09 19:50:13,710 WARNING  Physical record at 0x3AD7E is successor but has no predecessor bit set.

TIF  True >:  0x       0  0x   3a986  0x   3ae40  PR: 0x   3ad7e     182  0x8001     178  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3ad7e  0x   3b238  PR: 0x   3ae40    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3ae40  0x   3b630  PR: 0x   3b238    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3b238  0x   3ba28  PR: 0x   3b630    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3b630  0x   3be20  PR: 0x   3ba28    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3ba28  0x   3c218  PR: 0x   3be20    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3be20  0x   3c610  PR: 0x   3c218    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3c218  0x   3ca08  PR: 0x   3c610    1004  0x8002    1000  ------  ------  ------ + ---- ---- [   13356]

[ 1] TotalDepth.LIS.core.pRepCode.ExceptionRepCodeUnknown: Unknown representation code: 0
Fixed by being a bit more cautious about dealing with DSB blocks that are 'null'.
"""

__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2010-2011 Paul Ross. All rights reserved.'

import time
import sys
import os
import logging
import traceback
from optparse import OptionParser
import multiprocessing
# Serialisation
import pickle
import json
import pprint

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import FileIndexer

class IndexTimer(object):
    def __init__(self):
        self._errCount = 0
        # List of pairs (size, time)
        self._sizeTime = []
    
    @property
    def errCount(self):
        return self._errCount
    
    def __iadd__(self, other):
        self._errCount += other._errCount
        self._sizeTime.extend(other._sizeTime)
        return self

    def __len__(self):
        return len(self._sizeTime)
        
    def __str__(self):
        l = ['Size(kb)\tTime(s)\tRate(ms/MB)']
        l += ['{:.3f}\t{:.6f}\t{:.3f}'.format(s/1024, t, t * 1000 / (s / 1024**2)) for s, t in self._sizeTime]
        l.append('\nFiles: {:d}\nErrors: {:d}'.format(self._errCount+len(self._sizeTime), self._errCount))
        return '\n'.join(l)
        
    def addErr(self):
        self._errCount += 1
    
    def addSizeTime(self, s, t):
        self._sizeTime.append((s,t))

def indexFile(fp, numTimes, verbose, keepGoing, convertJson):
    logging.info('Index.indexFile(): {:s}'.format(fp))
    assert(os.path.isfile(fp))
    retIt = IndexTimer()
    try:
        myLenPickle = -1
        myLenJson = -1
        timeS = []
        for t in range(numTimes):
            clkStart = time.clock()
            myFi = File.FileRead(fp, theFileId=fp, keepGoing=keepGoing)
            try:
                myIdx = FileIndexer.FileIndex(myFi)
            except ExceptionTotalDepthLIS as err:
                logging.error('{:s}'.format(str(err)))
                continue
            timeS.append(time.clock() - clkStart)
            if verbose:
                print(myIdx.longDesc())
                print(' All records '.center(75, '='))
                for aLr in myIdx.genAll():
                    print(str(aLr))
                print(' All records DONE '.center(75, '='))
                print(' Log Passes '.center(75, '='))
                for aLp in myIdx.genLogPasses():
                    print('LogPass', aLp.logPass.longStr())
                    print()
                print(' Log Passes DONE '.center(75, '='))
                print(' Plot Records '.center(75, '='))
                for aPlotRec in myIdx.genPlotRecords():
                    print('Plot Record:', aPlotRec)
                    print()
                print(' Plot Records DONE '.center(75, '='))
            #print('CPU time = %8.3f (S)' % timeS[-1])
            if t == 0:
                pikBy = pickle.dumps(myIdx)
                #print('Pickled: file={:10d} size={:10d} {:8.3f}%'.format(
                #    os.path.getsize(fp),
                #    len(pikBy),
                #    len(pikBy)*100/os.path.getsize(fp)
                #    )
                #)
                myLenPickle = len(pikBy)
                #print('{:d}\t{:d}\t{:.3f} #Pickled'.format(os.path.getsize(fp), len(pikBy), len(pikBy)*100/os.path.getsize(fp)))
                if convertJson:
                    jsonObj = myIdx.jsonObject()
                    # pprint.pprint(jsonObj)
                    jsonBytes = json.dumps(jsonObj, sort_keys=True, indent=4)
                    myLenJson = len(jsonBytes)
                    if verbose:
                        print(' JSON [{:d}] '.format(myLenJson).center(75, '='))
                        print(jsonBytes)
                        print(' JSON DONE '.center(75, '='))
        if len(timeS) > 0:
            refTime = sum(timeS)/len(timeS)
            if verbose:
                print('   Min: {:.3f} (s)'.format(min(timeS)))
                print('   Max: {:.3f} (s)'.format(max(timeS)))
                print('  Mean: {:.3f} (s)'.format(refTime))
            if len(timeS) > 2:
                timeS = sorted(timeS)
                #print(timeS)
                refTime = timeS[((len(timeS)+1)//2)-1]
                if verbose:
                    print('Median: {:.3f} (s)'.format(refTime))
            #print(os.path.getsize(fp), refTime)
            mySiz = os.path.getsize(fp)
            sizemb = mySiz / 2**20
            rate = refTime * 1000 / sizemb
            print('File size: {:d} ({:.3f} MB) Reference Time: {:.6f} (s), rate {:.3f} ms/MB file: {:s} pickleLen={:d} jsonLen={:d}'.format(
                    mySiz,
                    sizemb,
                    refTime,
                    rate,
                    fp,
                    myLenPickle,
                    myLenJson,
                )
            )
            retIt.addSizeTime(mySiz, refTime)
    except ExceptionTotalDepthLIS as err:
        retIt.addErr()
        traceback.print_exc()
    return retIt

def indexDirSingleProcess(d, r, t, v, k, j):
    """Recursively process a directory using a single process."""
    assert(os.path.isdir(d))
    retIt = IndexTimer()
    for n in os.listdir(d):
        fp = os.path.join(d, n)
        if os.path.isfile(fp):
            retIt += indexFile(fp, t, v, k, j)
        elif os.path.isdir(fp) and r:
            retIt += indexDirSingleProcess(fp, r, t, v, k, j)
    return retIt

################################
# Section: Multiprocessing code.
################################
def genFp(d, r):
    """Generates file paths, recursive if necessary."""
    assert(os.path.isdir(d))
    for n in os.listdir(d):
        fp = os.path.join(d, n)
        if os.path.isfile(fp):
            yield fp
        elif os.path.isdir(fp) and r:
            for aFp in genFp(fp, r):
                yield aFp

def indexDirMultiProcess(dir, recursive, numT, verbose, keepGoing, convertJson, jobs):
    if jobs < 1:
        jobs = multiprocessing.cpu_count()
    logging.info('indexDirMultiProcess(): Setting MP jobs to %d' % jobs)
    myPool = multiprocessing.Pool(processes=jobs)
    myTaskS = [(fp, numT, verbose, keepGoing, convertJson) for fp in genFp(dir, recursive)]
    retResult = IndexTimer()
    #print('myTaskS', myTaskS)
    myResults = [
        r.get() for r in [
            myPool.apply_async(indexFile, t) for t in myTaskS
        ]
    ]
    for r in myResults:
        retResult += r
    return retResult
################################
# End: Multiprocessing code.
################################

def main():
    usage = """usage: %prog [options] path
Indexes LIS files recursively."""
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
    optParser.add_option(
            "-j", "--jobs",
            type="int",
            dest="jobs",
            default=-1,
            help="Max processes when multiprocessing. Zero uses number of native CPUs [%d]. -1 disables multiprocessing." \
                    % multiprocessing.cpu_count() \
                    + " [default: %default]" 
        )      
    optParser.add_option("-t", "--times", type="int", dest="times", default=1,
            help="Number of times to repeat the read [default: %default]"
        )
    optParser.add_option("-s", "--statistics", action="store_true", dest="statistics", default=False, 
                      help="Dump timing statistics. [default: %default]")
    optParser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, 
                      help="Verbose Output. [default: %default]")
    optParser.add_option("-r", "--recursive", action="store_true", dest="recursive", default=False, 
                      help="Process input recursively. [default: %default]")
    optParser.add_option("-J", "--JSON", action="store_true", dest="json", default=False,
                      help="Convert index to JSON, if verbose then dump it out as well. [default: %default]")
    opts, args = optParser.parse_args()
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    # Your code here
    #print('opts', opts)
    clkStart = time.clock()
    myIt = IndexTimer()
    if len(args) != 1:
        optParser.print_help()
        optParser.error("I can't do much without a path to the LIS file(s).")
        return 1
    if opts.times < 1:
        optParser.error("Number of test times needs to be >= 1.")
        return 1
    if os.path.isfile(args[0]):
        # Single file so always single process code
        myIt += indexFile(args[0], opts.times, opts.verbose, opts.keepGoing, opts.json)
    elif os.path.isdir(args[0]):
        if opts.jobs == -1:
            # Single process code
            myIt += indexDirSingleProcess(args[0], opts.recursive, opts.times, opts.verbose, opts.keepGoing, opts.json)
        else:
            # Multiprocess code 
            myIt += indexDirMultiProcess(args[0], opts.recursive, opts.times, opts.verbose, opts.keepGoing, opts.json, opts.jobs)
    print('Summary:')
    if opts.statistics:
        print(myIt)
    else:
        print('Results: {:8d}'.format(len(myIt)))
        print(' Errors: {:8d}'.format(myIt.errCount))
        print('  Total: {:8d}'.format(len(myIt)+myIt.errCount))
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    multiprocessing.freeze_support()
    sys.exit(main())
