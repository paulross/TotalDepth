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
Created on 25 Feb 2011

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
import random
import pprint
import re
import traceback
from optparse import OptionParser
import cProfile

from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import FileIndexer
from TotalDepth.LIS.core import FrameSet

LOOPS_TO_TEST = 1
FRAMES_TO_READ = 2048
CHANNELS_TO_READ = 32

# Regex for 
# ^(.+?)([0-9.]+)\s+\(s\)\s+([0-9.]+) ms/MB(.+?)([0-9.]+)\s+\(s\)\s+([0-9.]+) ms/MB.+$
# \3\t\6

PRINT_FORMAT = '{:24s} Load: {:.3f} (s) {:8.1f} ms/MB Accumulate: {:.3f} (s) {:8.1f} ms/MB Values: {:d} ({:.3f} MB) Array bytes: {:d}'
RE_PRINT_FORMAT = re.compile(r'^(.+?)([0-9.]+)\s+\(s\)\s+([0-9.]+) ms/MB(.+?)([0-9.]+)\s+\(s\)\s+([0-9.]+) ms/MB Values: (\d+) \(([0-9.]+) MB\) Array bytes: (\d+)$')

# Regex for median values: '^.+?(\d+) NumVals=(\d+).+?median=\s+([0-9.]+).+?median=\s+([0-9.]+).+$'
# Replace: r'\1\t\2\t\3\t\4'

def regexStdout(fp):
    """Opens a file on path fp and regexes it for data."""
    with open(fp) as f:
        for line in f:
            m = RE_PRINT_FORMAT.match(line)
            if m:
                print('\t'.join(m.groups()))

class Result(object):
    def __init__(self, numVals, tR, tA):
        """Constructor with number of values read, time to read, time to accumulate."""
        self.numVals = numVals
        self.timeRead = tR
        self.timeAccu = tA
        
    @property
    def equivMB(self):
        return self.numVals * 4 / 2**20

    @property
    def costRead(self):
        return self.timeRead * 1000 / self.equivMB

    @property
    def costAccu(self):
        return self.timeAccu * 1000 / self.equivMB

class ResultS(object):
    def __init__(self):
        self._resultS = []
        
    def append(self, r):
        self._resultS.append(r)

    @property
    def costRead(self):
        """Returns min/mean/median/max read costs or None."""
        myL = sorted([r.costRead for r in self._resultS])
        if len(myL):
            return min(myL), sum(myL)/len(myL), myL[((len(myL)+1)//2)-1], max(myL)

    @property
    def costAccu(self):
        """Returns min/mean/median/max accumulate costs or None."""
        myL = sorted([r.costAccu for r in self._resultS])
        if len(myL):
            return min(myL), sum(myL)/len(myL), myL[((len(myL)+1)//2)-1], max(myL)

    def __str__(self):
        if len(self._resultS) > 0:
            return ' '.join(
                [
                    'NumVals={:d} equivMB={:8.3f}'.format(self._resultS[0].numVals, self._resultS[0].equivMB),
                    'LoadCosts: min={:8.1f} mean={:8.1f} median={:8.1f} max={:8.1f} (ms/MB)'.format(*self.costRead),
                    'AccuCosts: min={:8.1f} mean={:8.1f} median={:8.1f} max={:8.1f} (ms/MB)'.format(*self.costAccu),
                ]
            )
        return 'NO results.'

def _loadFrameSetAndAccumulate(theF, theLp, theFrameSlice, theChList):
    tS = time.clock()
    theLp.setFrameSet(theF, theFrSl=theFrameSlice, theChList=theChList)
    tE_load = time.clock() - tS
    tS = time.clock()
    #print('theFrameSlice', theFrameSlice)
    myAcc = theLp.frameSet.accumulate([FrameSet.AccMin, FrameSet.AccMax, FrameSet.AccMean,])
    #print(myAcc)
    tE_acc = time.clock() - tS
    numVals = theLp.frameSet.numValues
    mbRead = numVals * 4 / 2**20
    loadCost = 1000 * tE_load / mbRead
    accCost = 1000 * tE_acc / mbRead
    print(PRINT_FORMAT.format(
            theFrameSlice,
            tE_load,
            loadCost,
            tE_acc,
            accCost,
            numVals,
            mbRead,
            theLp.frameSet.nbytes
        )
    )
    return Result(numVals, tE_load, tE_acc)

def frameSetLoadAllCh(theF, theLp):
    numFramesInPass = theLp.rle.totalFrames()
    numChannels = len(theLp.dfsr.dsbBlocks)
    if numFramesInPass < 1 or numChannels < 1:
        return
    framesToRead = min(FRAMES_TO_READ//32, numFramesInPass)
    channelsToRead = numChannels
    loopsToTest = LOOPS_TO_TEST
    loadCostS = []
    accCostS = []
    print('Loading {:d} sequential frames, all channels [{:d}]. Calculating the min/max/mean for each channel.'.format(framesToRead, channelsToRead))
    fLimit = numFramesInPass - 1 - framesToRead
    myRes = ResultS()
    for i in range(loopsToTest):
        if fLimit < 1:
            fStart = 0
        else:
            fStart = random.randint(0, fLimit)
        fStop = min(numFramesInPass+1, fStart + framesToRead)
        fStep = 1
        fSlice = slice(fStart, fStop, fStep)
        #chStart = random.randrange(0, numChannels - channelsToRead, 1)
        #chList = list(range(chStart, chStart+channelsToRead))
        #print('    fSlice', fSlice, 'chList', chList)
        res = _loadFrameSetAndAccumulate(theF, theLp, fSlice , None)
        myRes.append(res)
    print(str(myRes))
    return myRes

def frameSetLoadSequential(theF, theLp):
    numFramesInPass = theLp.rle.totalFrames()
    numChannels = len(theLp.dfsr.dsbBlocks)
    if numFramesInPass < 1 or numChannels < 1:
        return
    framesToRead = min(FRAMES_TO_READ, numFramesInPass)
    channelsToRead = min(CHANNELS_TO_READ, numChannels)
    loopsToTest = LOOPS_TO_TEST
    loadCostS = []
    accCostS = []
    print('Loading {:d} sequential frames, {:d} sequential channels. Calculating the min/max/mean for each channel.'.format(framesToRead, channelsToRead))
    fLimit = numFramesInPass - 1 - framesToRead
    myRes = ResultS()
    for i in range(loopsToTest):
        if fLimit < 1:
            fStart = 0
        else:
            fStart = random.randint(0, fLimit)
        fStop = min(numFramesInPass+1, fStart + framesToRead)
        fStep = 1
        fSlice = slice(fStart, fStop, fStep)
        if numChannels == channelsToRead:
            chStart = 0
        else:
            chStart = random.randrange(0, numChannels - channelsToRead, 1)
        chList = list(range(chStart, chStart+channelsToRead))
        #print('    fSlice', fSlice, 'chList', chList)
        res = _loadFrameSetAndAccumulate(theF, theLp, fSlice , chList)
        myRes.append(res)
    print(str(myRes))
    return myRes

def frameSetLoadSequentialRandCh(theF, theLp):
    numFramesInPass = theLp.rle.totalFrames()
    numChannels = len(theLp.dfsr.dsbBlocks)
    if numFramesInPass < 1 or numChannels < 1:
        return
    framesToRead = min(FRAMES_TO_READ, numFramesInPass)
    channelsToRead = min(CHANNELS_TO_READ, numChannels)
    loopsToTest = LOOPS_TO_TEST
    loadCostS = []
    accCostS = []
    print('Loading {:d} sequential frames, {:d} random channels. Calculating the min/max/mean for each channel.'.format(framesToRead, channelsToRead))
    fLimit = numFramesInPass - 1 - framesToRead
    myRes = ResultS()
    for i in range(loopsToTest):
        if fLimit < 1:
            fStart = 0
        else:
            fStart = random.randint(0, fLimit)
        fStop = min(numFramesInPass+1, fStart + framesToRead)
        fStep = 1
        fSlice = slice(fStart, fStop, fStep)
        chList = [random.randrange(0, numChannels, 1) for c in range(channelsToRead)]
        #print('    fSlice', fSlice, 'chList', chList)
        res = _loadFrameSetAndAccumulate(theF, theLp, fSlice , chList)
        myRes.append(res)
    print(str(myRes))
    return myRes

def frameSetLoadRandom(theF, theLp):
    numFramesInPass = theLp.rle.totalFrames()
    numChannels = len(theLp.dfsr.dsbBlocks)
    if numFramesInPass < 1 or numChannels < 1:
        return
    framesToRead = min(FRAMES_TO_READ, numFramesInPass)
    channelsToRead = min(CHANNELS_TO_READ, numChannels)
    loopsToTest = LOOPS_TO_TEST
    loadCostS = []
    accCostS = []
    print('Loading {:d} random frames, {:d} random channels. Calculating the min/max/mean for each channel.'.format(framesToRead, channelsToRead))
    fLimit = numFramesInPass - 1 - framesToRead
    myRes = ResultS()
    for i in range(loopsToTest):
        if fLimit < 1:
            fStart = 0
        else:
            fStart = random.randint(0, fLimit)
        fStop = random.randint(0, numFramesInPass-1)
        if fStop < fStart:
            fStop, fStart = fStart, fStop
        fStep = ((fStop - fStart) // framesToRead) or 1 #random.randint(1, 16)
        fSlice = slice(fStart, fStop, fStep)
        chList = [random.randrange(0, numChannels, 1) for c in range(channelsToRead)]
        #print('    fSlice', fSlice, 'chList', chList)
        res = _loadFrameSetAndAccumulate(theF, theLp, fSlice , chList)
        myRes.append(res)
    print(str(myRes))
    return myRes

def frameSetLoadAll(theF, theLp):
    numFramesInPass = theLp.rle.totalFrames()
    numChannels = len(theLp.dfsr.dsbBlocks)
    if numFramesInPass < 1 or numChannels < 1:
        return
    framesToRead = numFramesInPass#min(FRAMES_TO_READ, numFramesInPass)
    channelsToRead = numChannels#min(CHANNELS_TO_READ, numChannels)
    loopsToTest = LOOPS_TO_TEST
    loadCostS = []
    accCostS = []
    print('Loading all frames [{:d}], all channels [{:d}]. Calculating the min/max/mean for each channel.'.format(framesToRead, channelsToRead))
    myRes = ResultS()
    for i in range(loopsToTest):
        res = _loadFrameSetAndAccumulate(theF, theLp, None, None)
        myRes.append(res)
    print(str(myRes))
    return myRes

TEST_TYPE = {
    'A' : (frameSetLoadAll, ''),
    'B' : (frameSetLoadAllCh, ''),
    'C' : (frameSetLoadSequential, ''),
    'D' : (frameSetLoadSequentialRandCh, ''),
    'E' : (frameSetLoadRandom, ''),
}

def processFile(f, tests, keepGoing, resultMap):
    retVal = 0
    try:
        logging.info('File: {:s} size: {:d}'.format(f, os.path.getsize(f)))
        myFi = File.FileRead(f, theFileId=f, keepGoing=keepGoing)
        #a = r'W:\LISTestData\logPassStd256MB.lis'
        #myFi = File.FileRead(a, theFileId=a)
        clkStart = time.clock()
        myIdx = FileIndexer.FileIndex(myFi)
        #print(myIdx.longDesc())
        print('Index time: {:.3f}'.format(time.clock() - clkStart))
    except Exception as err:
        logging.error(str(err))
        traceback.print_exc()
    else:
        #print('resultMap', resultMap)
        #print('tests', tests)
        for t in tests:
            #print('t', t)
            resultMap[t][f] = []
        for aLpi in myIdx.genLogPasses():
            for t in tests:
                try:
                    myR = TEST_TYPE[t][0](myFi, aLpi.logPass)
                except Exception as err:
                    logging.error(str(err))
                    traceback.print_exc()
                else:
                    retVal = 1
                    if myR is not None:
                        resultMap[t][f].append(myR)
    return retVal

def processDir(d, tests, keepGoing, resultMap):
    cntrFiles = cntrOK = 0
    retMap = {}
    for root, dirs, files in os.walk(d, topdown=False):
        for f in files:
            p = os.path.join(root, f)
            cntrOK += processFile(p, tests, keepGoing, resultMap)
            cntrFiles += 1
    return cntrFiles, cntrOK

def pprintResultMap(theMap):
    for testType in sorted(theMap.keys()):
        print(' Test type: {:s} '.format(testType).center(75, '='))
        for f in sorted(theMap[testType].keys()):
            for p, aR in enumerate(theMap[testType][f]):
                print(f, p, os.path.getsize(f), aR)
        print(' Ends: {:s} '.format(testType).center(75, '='))

def main():
    usage = """usage: %prog [options] path
Exercises FrameSet(s) for LIS files or directories thereof."""
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
    optParser.add_option(
            "-n", "--num-tests",
            type="int",
            dest="numTests",
            default=1,
            help="Number of tests to repeat [default: %default]"
        )      
    optParser.add_option("-T", "--test", action="append", dest="tests", default=['A'],
                      help="""Tests, additive.
Can be:
A - Read all frames, all channels.
B - Random sequential set of frames, all channels.
C - Random sequential set of frames, random sequential set of channels.
D - Random sequential set of frames, random non-sequential set of channels..
E - Random frames, random channels.
[default: %default]""")
    optParser.add_option("-s", action="store_true", dest="regex", default=False, 
                      help="Treat the input file as stdout and regex for fields. [default: %default]")
    opts, args = optParser.parse_args()
    global LOOPS_TO_TEST
    LOOPS_TO_TEST = opts.numTests
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    # Your code here
    # Map of:
    # {test : {file : [LogPass_ResultS, ...], ...}, ...}
    resultMap = {}
    myTests = ''.join(sorted(list(set(''.join(opts.tests)))))
    for t in 'ABCDE':
        resultMap[t] = {}
    if len(args) == 1:
        if opts.regex:
            regexStdout(args[0])
        else:
            if os.path.isdir(args[0]):
                f, ok = processDir(args[0], myTests, opts.keepGoing, resultMap)
                print('Total files: {:d}'.format(f))
                print('   OK files: {:d}'.format(ok))
            elif os.path.isfile(args[0]):
                processFile(args[0], myTests, opts.keepGoing, resultMap)
            pprintResultMap(resultMap)
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
    random.seed()
    #cProfile.run('main()', 'RandomFrameSetRead.prof')
    sys.exit(main())
    