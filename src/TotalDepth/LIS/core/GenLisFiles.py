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
"""Creates a particular set of LIS files using LisGen.

Created on 20 Feb 2011

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

from TotalDepth.LIS.core import LisGen
from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import PhysRec
from TotalDepth.LIS.core import LogiRec

class GenLisFiles(object):
    LIS_FILE_EXT = '.lis'
    def __init__(self, theDir=''):
        self._dir = theDir
        self._cntrFile = 0
        self._cntrByte = 0
        self.METHOD_FILENAME_MAP = {
            self.fileMarker         : 'filemarker',
            self.oneRandomCONS      : 'singleCONS',
            self.logPassSmall       : 'logPassSmall',
            self.logPassMedium      : 'logPassMedium',
            self.logPassLarge       : 'logPassLarge',
            # Testing different PR sizes
            self.logPassPrLen10     : 'logPassPR10',
            self.logPassPrLen11     : 'logPassPR11',
            self.logPassPrLen12     : 'logPassPR12',
            self.logPassPrLen13     : 'logPassPR13',
            self.logPassPrLen14     : 'logPassPR14',
            self.logPassPrLen15     : 'logPassPR15',
            self.logPassPrLen16     : 'logPassPR16',
            # Standard 1000 channels, 64k frames, 256MB
            self.logPassStd256MB    : 'logPassStd256MB',
        }
        for f in self.METHOD_FILENAME_MAP:
            logging.info('Generating {:s} in: "{:s}"'.format(f, self.METHOD_FILENAME_MAP[f]))
            self._cntrByte += f(self.METHOD_FILENAME_MAP[f])
            self._cntrFile += 1

    def __str__(self):
        return 'GenLisFiles files={:d} bytes={:d} ({:.3f} MB)'.format(
            self._cntrFile, self._cntrByte, self._cntrByte/2**20
        )

    def _retFilePath(self, f):
        f = f + self.LIS_FILE_EXT
        if self._dir:
            return os.path.join(self._dir, f)
        return f

    def _retStdFile(self, f, prLen=PhysRec.PR_MAX_LENGTH):
        return File.FileWrite(
            theFile=self._retFilePath(f),
            theFileId=self._retFilePath(f),
            keepGoing=False,
            hasTif=True,
            thePrLen=prLen,
            thePrt=PhysRec.PhysRecTail(hasRecNum=True, fileNum=255, hasCheckSum=True),
        )
    
    def _writeDefaultMarkerHead(self, theF):
        theF.write(LisGen.TapeReelHeadTailDefault.lrBytesReelHead)
        theF.write(LisGen.TapeReelHeadTailDefault.lrBytesTapeHead)
        theF.write(LisGen.FileHeadTailDefault.lrBytesFileHead)

    def _writeDefaultMarkerTail(self, theF):
        theF.write(LisGen.FileHeadTailDefault.lrBytesFileTail)
        theF.write(LisGen.TapeReelHeadTailDefault.lrBytesTapeTail)
        theF.write(LisGen.TapeReelHeadTailDefault.lrBytesReelTail)
        
    def fileMarker(self, f):
        myF = self._retStdFile(f)
        self._writeDefaultMarkerHead(myF)
        self._writeDefaultMarkerTail(myF)
        myF.close()
        return os.path.getsize(myF.fileId)

    def oneRandomCONS(self, f):
        myF = self._retStdFile(f)
        self._writeDefaultMarkerHead(myF)
        myF.write(LisGen.TableGenRandomCONS(256).lrBytes())
        self._writeDefaultMarkerTail(myF)
        myF.close()
        return os.path.getsize(myF.fileId)
    
    def _logPass(self, theF, numCh, lisBytesPerCh, sampPerCh, numFr, frPerLr):
        myEbs = LogiRec.EntryBlockSet()
        # Set entry blocks to make frame spacing 0.5 b'FEET'
        # Block 8
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 4, 68, 0.5))
        # Block 9
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'FEET'))
        myChList = [
                LisGen.Channel(
                    LisGen.ChannelSpec(
                        bytes('{:04d}'.format(i), 'ascii'),
                        b'ServID', b'ServOrdN', b'FEET',
                        45310011, 256, lisBytesPerCh, sampPerCh, 68
                    ),
                    LisGen.ChValsConst(fOffs=0, waveLen=4, mid=0.0, amp=1.0, numSa=1, noise=36.0),
                ) for i in range(numCh)
        ]
        # Start at 10,000 feet
        myLpg = LisGen.LogPassGen(myEbs, myChList, xStart=10000.0, xRepCode=68, xNoise=None)
        # DFSR
        theF.write(myLpg.lrBytesDFSR())
        for i in range(0, numFr, frPerLr):
            theF.write(myLpg.lrBytes(i, frPerLr))

    def logPassSmall(self, f):
        myF = self._retStdFile(f)
        self._writeDefaultMarkerHead(myF)
        myEbs = LogiRec.EntryBlockSet()
        #myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, 4*4))
        myLpg = LisGen.LogPassGen(
            myEbs,
            # Channel list
            [
                LisGen.Channel(
                    LisGen.ChannelSpec(
                        b'TEST', b'ServID', b'ServOrdN', b'FEET',
                        45310011, 256, 16, 4, 68
                    ),
                    LisGen.ChValsConst(fOffs=0, waveLen=4, mid=0.0, amp=1.0, numSa=1, noise=None),
                ),
            ],
            xStart=10000.0,
            xRepCode=68,
            xNoise=None,
        )
        # DFSR
        myF.write(myLpg.lrBytesDFSR())
        # Logical data records
        for i in range(0, 1024, 128):
            myF.write(myLpg.lrBytes(i, 128))
        self._writeDefaultMarkerTail(myF)
        return os.path.getsize(myF.fileId)

    def logPassMedium(self, f):
        myF = self._retStdFile(f)
        self._writeDefaultMarkerHead(myF)
        self._logPass(
            myF,
            numCh=1024,
            lisBytesPerCh=4*4,
            sampPerCh=4,
            numFr=1024,
            frPerLr=128 * 1024 // (4 * 1024),
        )
        self._writeDefaultMarkerTail(myF)
        return os.path.getsize(myF.fileId)

    def logPassLarge(self, f):
        myF = self._retStdFile(f)
        self._writeDefaultMarkerHead(myF)
        self._logPass(
            myF,
            numCh=4096,
            lisBytesPerCh=4*4,
            sampPerCh=4,
            numFr=4096,
            frPerLr=256 * 1024 // (4 * 4096),
        )
        self._writeDefaultMarkerTail(myF)
        return os.path.getsize(myF.fileId)
    
    def logPassStd256MB(self, f):
        """This 'standard' file is 256MB of log data with 1024 channels, single
        sampled. There are 65536 frames with a frame spacing of 1/10 ft.
        There are 128 frames per logical record."""
        numCh = 1023
        lisBytesPerCh = 4
        sampPerCh = 1
        numFr = 64*1024
        frPerLr = 128
        myF = self._retStdFile(f, prLen=PhysRec.PR_MAX_LENGTH)
        self._writeDefaultMarkerHead(myF)
        myEbs = LogiRec.EntryBlockSet()
        # Set entry blocks to make frame spacing 12 b'.1IN' i.e. 10 frames/foot
        # Block 8
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 66, 12))
        # Block 9
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'.1IN'))
        myChList = [
                LisGen.Channel(
                    LisGen.ChannelSpec(
                        bytes('{:04d}'.format(i), 'ascii'),
                        b'ServID', b'ServOrdN', b'FEET',
                        45310011, 256, lisBytesPerCh, sampPerCh, 68
                    ),
                    LisGen.ChValsConst(fOffs=0, waveLen=4, mid=0.0, amp=1.0, numSa=1, noise=12.0),
                ) for i in range(numCh)
        ]
        # Start at 10,000 feet i.e. 10000*120 .1IN
        myLpg = LisGen.LogPassGen(myEbs, myChList, xStart=10000.0*120, xRepCode=68, xNoise=None)
        # DFSR
        myF.write(myLpg.lrBytesDFSR())
        for i in range(0, numFr, frPerLr):
            myF.write(myLpg.lrBytes(i, frPerLr))
        self._writeDefaultMarkerTail(myF)
        return os.path.getsize(myF.fileId)
    
    def _logPassPrLen(self, f, thePrLen):
        """Typically a 64MB LogPass file with a specific PR length. For performance evaluation."""
        myF = self._retStdFile(f, prLen=thePrLen)
        self._writeDefaultMarkerHead(myF)
        self._logPass(
            myF,
            numCh=256,
            lisBytesPerCh=4,
            sampPerCh=1,
            numFr=16*4096,
            frPerLr=128,
        )
        self._writeDefaultMarkerTail(myF)
        return os.path.getsize(myF.fileId)

    def logPassPrLen10(self, f):
        """PR len 2**10."""
        return self._logPassPrLen(f, 2**10)

    def logPassPrLen11(self, f):
        """PR len 2**11."""
        return self._logPassPrLen(f, 2**11)

    def logPassPrLen12(self, f):
        """PR len 2**12."""
        return self._logPassPrLen(f, 2**12)

    def logPassPrLen13(self, f):
        """PR len 2**13."""
        return self._logPassPrLen(f, 2**13)

    def logPassPrLen14(self, f):
        """PR len 2**14."""
        return self._logPassPrLen(f, 2**14)

    def logPassPrLen15(self, f):
        """PR len 2**15."""
        return self._logPassPrLen(f, 2**15)

    def logPassPrLen16(self, f):
        """PR len 65536-1."""
        return self._logPassPrLen(f, PhysRec.PR_MAX_LENGTH)



def main():
    usage = """usage: %prog [options] dir
Counts files and sizes."""
    print('Cmd: %s' % ' '.join(sys.argv))
    optParser = OptionParser(usage, version='%prog ' + __version__)
    optParser.add_option(
            "-l", "--loglevel",
            type="int",
            dest="loglevel",
            default=10,
            help="Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: %default]"
        )
    optParser.add_option("-o", "--outdir",
                         type="string",
                         dest="outdir",
                         default='', 
                         help="Output directory. [default: %default]")
    opts, args = optParser.parse_args()
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    # Your code here
    if opts.outdir and not os.path.exists(opts.outdir):
        os.makedirs(opts.outdir)
    myGlf = GenLisFiles(opts.outdir)
    print(myGlf)
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    #multiprocessing.freeze_support()
    sys.exit(main())

    
    
    