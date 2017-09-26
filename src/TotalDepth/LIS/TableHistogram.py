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
'''Provides a count of elements in LIS tables.

Created on May 24, 2011

@author: paulross
'''
__author__  = 'Paul Ross'
__date__    = '2011-05-24'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

import time
import sys
import os
import logging
import collections
import pprint
from optparse import OptionParser

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import FileIndexer

class TableHistogram(object):
    def __init__(self):
        # The full table histogram
        self._cntrAll = collections.defaultdict(int)
        # Count of occurrence of row mnemonics
        self._cntrRowMnem = collections.defaultdict(int)
        # Count of occurrence of col mnemonics
        self._cntrColMnem = collections.defaultdict(int)

    def incAll(self, theMatcher, lrType, nameTable, nameRow, nameCol, v):
        self._cntrAll[theMatcher.key(lrType, nameTable, nameRow, nameCol, v)] += 1
        
    def incRow(self, lrType, nameTable, nameRow):
        self._cntrRowMnem[(lrType, nameTable, nameRow)] += 1
        
    def incCol(self, lrType, nameTable, nameCol):
        self._cntrColMnem[(lrType, nameTable, nameCol)] += 1

    @property
    def cntrAll(self):
        return self._cntrAll

    @property
    def cntrRowMnem(self):
        return self._cntrRowMnem

    @property
    def cntrColMnem(self):
        return self._cntrColMnem

class TableMatcher(collections.namedtuple('TableMatcher', 'lrType nameTable nameRow nameCol')):
    """Tests if a table entry matches."""
    __slots__ = ()
    def lrTypeMatch(self, lrType):
        return self.lrType == b'' or self.lrType == lrType
    
    def nameTableMatch(self, nameTable):
        return self.nameTable == b'' or self.nameTable == nameTable
    
    def nameRowMatch(self, nameRow):
        return self.nameRow == b'' or self.nameRow == nameRow

    def nameColMatch(self, nameCol):
        return self.nameCol == b'' or self.nameCol == nameCol
    
    def matches(self, lrType, nameTable, nameRow, nameCol):
        return self.lrType == b'' or self.lrType == lrType \
            and self.nameTable == b'' or self.nameTable == nameTable \
            and self.nameRow == b'' or self.nameRow == nameRow \
            and self.nameCol == b'' or self.nameCol == nameCol \

    def key(self, lrType, nameTable, nameRow, nameCol, v):
        retL = []
        if self.lrType != b'':
            retL.append(lrType)
        if self.nameTable != b'':
            retL.append(nameTable)
        if self.nameRow != b'':
            retL.append(nameRow)
        if self.nameCol != b'':
            retL.append(nameCol)
        if v != b'':
            retL.append(v)
        return str(tuple(retL))
        
def _processFile(fp, keepGoing, tabMtch, theCntr):
    assert(os.path.isfile(fp))
    logging.info('PlotLogPasses._processFile(): {:s}'.format(fp))
    assert(os.path.isfile(fp))
    try:
        myFi = File.FileRead(fp, theFileId=fp, keepGoing=keepGoing)
        myIdx = FileIndexer.FileIndex(myFi)
    except ExceptionTotalDepthLIS as err:
        logging.error('Can not read LIS file {:s} with error: {!r:s}'.format(fp, err))
    else:
#        print(' Index longDesc() '.center(75, '='))
#        print(myIdx.longDesc())
#        print(' Index longDesc() DONE '.center(75, '='))
        # Iterate through the FileIndexer object
        retVal = False
        for anIo in myIdx.genAll():
#            print('anIdxObj:', anIo)
            if anIo.lrType in LogiRec.LR_TYPE_TABLE_DATA \
            and tabMtch.lrTypeMatch(anIo.lrType) \
            and tabMtch.nameTableMatch(anIo.name):
                # Read the whole table logical record
                myFi.seekLr(anIo.tell)
                try:
                    myLrTable = LogiRec.LrTableRead(myFi)
                except Exception as err:
                    logging.error('Can not create Logical Record, error: {:s}'.format(err))
                else:
#                    print('myLrTable', myLrTable)
                    for aRow in myLrTable.genRows():
                        theCntr.incRow(anIo.lrType, anIo.name, aRow.value)
                        if tabMtch.nameRowMatch(aRow.value):
                            for aCell in aRow.genCells():
                                theCntr.incCol(anIo.lrType, anIo.name, aCell.mnem)
                                if tabMtch.nameColMatch(aCell.mnem):
                                    theCntr.incAll(
                                        tabMtch,
                                        anIo.lrType,
                                        anIo.name,
                                        aRow.value,
                                        aCell.mnem,
                                        aCell.engVal.value,
                                    )
#                                    if aCell.mnem == b'TYPE' and aCell.engVal.value == b'CONS':
#                                        retVal = True
        return retVal

def _processDir(fp, keepGoing, recursive, tabMtch, theCntr):
    assert(os.path.isdir(fp))
    for myName in os.listdir(fp):
        myPath = os.path.join(fp, myName)
        if os.path.isdir(myPath) and recursive:
            _processDir(myPath, keepGoing, recursive, tabMtch, theCntr)
        elif os.path.isfile(myPath):
            if _processFile(myPath, keepGoing, tabMtch, theCntr):
                print(myPath)
    
def processPath(p, keepGoing, recursive, tabMtch, theCntr):
    if os.path.isfile(p):
        if _processFile(p, keepGoing, tabMtch, theCntr):
            print(p)
    elif os.path.isdir(p):
        _processDir(p, keepGoing, recursive, tabMtch, theCntr)

def main():
    usage = """usage: %prog [options] path
Provides a count of elements in LIS tables."""
    print ('Cmd: %s' % ' '.join(sys.argv))
    optParser = OptionParser(usage, version='%prog ' + __version__)
    optParser.add_option("-k", "--keep-going", action="store_true", dest="keepGoing", default=False, 
                      help="Keep going as far as sensible. [default: %default]")
    optParser.add_option("-r", "--recursive", action="store_true", dest="recursive", default=False, 
                      help="Process input recursively. [default: %default]")
    optParser.add_option("-s", "--structure", action="store_true", dest="structure", default=False, 
                      help="Display table structure (row/col range). [default: %default]")
    optParser.add_option(
            "--type",
            type="int",
            dest="lrType",
            default=34,
            help="Logical record table type e.g. 34. [default: %default]"
        )      
    optParser.add_option(
            "--name",
            type="str",
            dest="name",
            default='',
            help="Logical record table name e.g. PRES. [default: %default]"
        )      
    optParser.add_option(
            "--row",
            type="str",
            dest="row",
            default='',
            help="Logical record table row e.g. 'GR  '. [default: %default]"
        )      
    optParser.add_option(
            "--col",
            type="str",
            dest="col",
            default='',
            help="Logical record table column e.g. 'LEDG'. [default: %default]"
        )      
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
    if len(args) != 1:
        optParser.print_help()
        optParser.error("I can't do much without a path to LIS file(s).")
        return 1
    myTaMtch = TableMatcher(
        opts.lrType,
        bytes(opts.name, 'ascii'),
        bytes(opts.row, 'ascii'),
        bytes(opts.col, 'ascii'),
    )
    myCntr = TableHistogram()
    processPath(args[0], opts.keepGoing, opts.recursive, myTaMtch, myCntr)
    print(' Count of all table entries '.center(75, '='))
    pprint.pprint(myCntr.cntrAll)
    print(' Count of all table entries END '.center(75, '='))
    if opts.structure:
        print(' Row entries '.center(75, '='))
        pprint.pprint(myCntr.cntrRowMnem)
        print(' Row entries END '.center(75, '='))
        print(' Column entries '.center(75, '='))
        pprint.pprint(myCntr.cntrColMnem)
        print(' Column entries END '.center(75, '='))
        print()
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    #multiprocessing.freeze_support()
    sys.exit(main())
