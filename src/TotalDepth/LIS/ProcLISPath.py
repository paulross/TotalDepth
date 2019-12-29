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
'''
Created on Jun 14, 2011

@author: paulross
'''
__author__  = 'Paul Ross'
__date__    = '2011-06-14'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

import os
import logging
import multiprocessing

from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import FileIndexer
from TotalDepth.util import DirWalk

class ProcLISPathBase(object):
    """Takes an input path, output path and processes LIS files."""
    def __init__(self, fpIn, fpOut, recursive, keepGoing):
        self._fpIn = fpIn
        self._fpOut = fpOut
        self._recursive = recursive
        self._keepGoing = keepGoing
        self._processPath()

    def _processPath(self):
        if os.path.isfile(self._fpIn):
            if not os.path.exists(os.path.dirname(self._fpOut)):
                os.makedirs(os.path.dirname(self._fpOut), exist_ok=True)
            self.processFile(self._fpIn, self._fpOut)
        elif os.path.isdir(self._fpIn):
            self._processDir(self._fpIn, self._fpOut)
    
    def _processDir(self, fpIn, fpOut):
        assert(os.path.isdir(fpIn))
        if not os.path.isdir(fpOut):
            os.makedirs(fpOut)
        for myName in os.listdir(fpIn):
            myPath = os.path.join(fpIn, myName)
            outPath = os.path.join(fpOut, myName)
            if os.path.isdir(myPath) and self._recursive:
                self._processDir(myPath, outPath)
            elif os.path.isfile(myPath):
                self._processFile(myPath, outPath)
        
    def _retLisFileAndIndex(self, fpIn):
        """Returns a LisFile.LisFile() and a FileIndexer.FileIndex() from fpIn.
        May raises an ExceptionTotalDepthLIS."""
        assert(os.path.isfile(fpIn))
        logging.info('ProcLISPathBase._retLisFileAndIndex(): Reading LIS file {:s}'.format(fpIn))
        myFi = File.FileRead(fpIn, theFileId=fpIn, keepGoing=self._keepGoing)
        myIdx = FileIndexer.FileIndex(myFi)
        return myFi, myIdx

    def processFile(self, fpIn, fpOut):
        raise NotImplementedError


def procLISPath(dIn, dOut, fnMatch, recursive, keepGoing, jobs, fileFn, resultObj=None):
    """Multiprocessing code to process LIS files.
    dIn, dOut are directories.

    fnMatch is a glob string.

    recursive is a boolean to control recursion.

    keepGoing is passed to fileFn

    jobs is number of jobs; -1 single process, 0 number of available CPUs

    fileFn is the operational function that will take a tuple of:
        (fIn, fOut, keepGoing) and return a result that can be added to
        the resultObj or None.
        This should not raise.

    resultObj is accumulation of the results of fileFn or None, this it returned."""
    if jobs < 0:
        return procLISPathSP(dIn, dOut, fnMatch, recursive, keepGoing, fileFn, resultObj)
    return procLISPathMP(dIn, dOut, fnMatch, recursive, keepGoing, jobs, fileFn, resultObj)

def procLISPathSP(dIn, dOut, fnMatch, recursive, keepGoing, fileFn, resultObj=None):
    for fpIn, fpOut in DirWalk.dirWalk(dIn, dOut, fnMatch, recursive):
        result = fileFn(fpIn, fpOut, keepGoing)
        if result is not None and resultObj is not None:
            resultObj += result
    return resultObj

def procLISPathMP(dIn, dOut, fnMatch, recursive, keepGoing, jobs, fileFn, resultObj=None):
    """Multiprocessing code to process LIS files.

    dIn, dOut are directories.

    fnMatch is a glob string.

    recursive is a boolean to control recursion.

    keepGoing is passed to fileFn

    fileFn is the operational function that will take a tuple of:
        (fIn, fOut, keepGoing) and return a result that can be added to
        the resultObj or None.
        This should not raise.

    resultObj is accumulation of the results of fileFn or None, this it returned."""
    if jobs < 1:
        jobs = multiprocessing.cpu_count()
    logging.info('procLISPathMP(): Setting multi-processing jobs to %d' % jobs)
    myPool = multiprocessing.Pool(processes=jobs)
    myTaskS = [(t.filePathIn, t.filePathOut, keepGoing) for t in DirWalk.dirWalk(dIn, dOut, fnMatch, recursive)]
    #print('myTaskS', myTaskS)
    myResults = [
        r.get() for r in [
            myPool.apply_async(fileFn, t) for t in myTaskS
        ]
    ]
    for r in myResults:
        if r is not None and resultObj is not None:
            resultObj += r
    return resultObj
