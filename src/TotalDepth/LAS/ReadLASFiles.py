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
"""Reads LAS files

Created on Jan 12, 2012

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2012 Paul Ross.'

import sys
import os
import logging
import time
import multiprocessing
from optparse import OptionParser
import collections
import pprint
import re
import traceback

from TotalDepth.LAS.core import LASRead

class ReadLASFiles(object):
    RE_DESC = re.compile(r'^\s*(\d+)\s*(.+)$')
    """Class documentation."""
    def __init__(self, path):
        self._cntrs = collections.defaultdict(int)
        # All mnemonics
        # {mnem : {desc : count, ...}, ...}
        self._mnemDescMap = {}
        # Curves only
        # {mnem : {desc : count, ...}, ...}
        self._curveDescMap = {}
        # Curves only
        # {unit : {desc : count, ...}, ...}
        self._unitDescMap = {}
        # {mnem : count, ...} from well and parameter sections
        self._wsdMnemCount = collections.defaultdict(int)
        # {bytes : [seconds, ...], ...}
        self._sizeTimeMap = {}
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for aName in filenames:
                    if aName == '.DS_Store':
                        continue
                    s, t = self._processFile(os.path.join(dirpath, aName))
                    self._addSizeTime(s, t)
        elif os.path.isfile(path):
            s, t = self._processFile(path)
            self._addSizeTime(s, t)
        else:
            logging.error('Unknown path: {:s}'.format(path))
            
    def _addSizeTime(self, s, t):
        try:
            self._sizeTimeMap[s].append(t)
        except KeyError:
            self._sizeTimeMap[s] = [t]

    def _processFile(self, fp):
        """Process a single file. Returns the size of the file and the time taken to process."""
        rSize = os.path.getsize(fp)
        clkStart = time.clock()
        try:
            myLr = LASRead.LASRead(fp)
            self._cntrs['byte'] += rSize
            self._cntrs['sect'] += len(myLr)
            self._cntrs['fram'] += myLr.numFrames()
            self._cntrs['data'] += myLr.numDataPoints()
            self._procLAS(myLr)
        except LASRead.ExceptionLASRead as err:
            logging.error('File: "{:s}", Error: {!r:s}'.format(fp, err))
            self._cntrs['erro'] += 1
        except Exception as err:
            logging.critical('File: "{:s}", Error [{!r:s}]: {!r:s}'.format(fp, type(err), err))
            logging.critical(traceback.format_exc())
            self._cntrs['crit'] += 1
        self._cntrs['file'] += 1
        return rSize, time.clock() - clkStart 
    
    def _procLAS(self, las):
        self._updateDescMaps(las)
        self._updateWsdHistogram(las)
        
    def _updateDescMaps(self, las):
        for s in las.genSects():
            self._updateMnemDescMapFromSect(s, self._mnemDescMap)
            self._updateUnitDescMapFromSect(s, self._unitDescMap)
            if s.type == 'C':
#                print('TRACE: s.mnemS()', s.mnemS())
                self._updateMnemDescMapFromSect(s, self._curveDescMap)

    def _updateMnemDescMapFromSect(self, s, descMap):
        for m in range(len(s)):
            dat = s[m]
            # s[m] is a SectLine or a line for arrays, other etc.
            if isinstance(dat, LASRead.SectLine):
                myDesc = self._normaliseDescription(dat.desc)
#                if isinstance(myDesc, str) and len(myDesc) > 0:
                if dat.mnem not in descMap:
                    descMap[dat.mnem] = collections.defaultdict(int)
                descMap[dat.mnem][myDesc] += 1
    
    def _updateUnitDescMapFromSect(self, s, descMap):
        for m in range(len(s)):
            dat = s[m]
            # s[m] is a SectLine or a line for arrays, other etc.
            if isinstance(dat, LASRead.SectLine):
                myDesc = self._normaliseDescription(dat.desc)
#                if isinstance(myDesc, str) and len(myDesc) > 0:
                if dat.unit is not None:
                    u = dat.unit
                    if not isinstance(u, str):
                        u = str(u)
                    if u not in descMap:
                        descMap[u] = collections.defaultdict(int)
                    descMap[u][myDesc] += 1
    
    def _normaliseDescription(self, d):
        """Normalise description according to some rules."""
        # Strip leading integer
        if isinstance(d, str):
#            print('WTF', '"{:s}" type: {:s}'.format(str(d), type(d)))
            m = self.RE_DESC.match(d)
            if m is not None and m.group(2) is not None:
                d = m.group(2)
            return d.title()
        return str(d)

    def _updateWsdHistogram(self, las):
        """Looks at the Parameter section and updates self._paramMnemCount."""
        # self._paramMnemCount
        for s in 'WP':
            try:
                sect = las[s]
            except KeyError:
                pass
            else:
                for m in sect.keys():
                    self._wsdMnemCount[m] += 1
    
    def _retMostPopularDescription(self, theMap, m):
        assert(m in theMap)
        if len(theMap[m]) == 1:
            # Unique
            return list(theMap[m].keys())[0]
        maxVal = max(theMap[m].values())
        l = [k for k,v in theMap[m].items() if v == maxVal]
        if len(l) == 1:
            return l[0]
        return str(l)
    
    def pprintMnemDesc(self, theS=sys.stdout):
        theS.write(' All mnemonics and their descriptions '.center(75, '-'))
        theS.write('\n')
        theS.write('{\n')
        for m in sorted(self._mnemDescMap.keys()):
            desc = self._retMostPopularDescription(self._mnemDescMap, m)
            theS.write('{:10s} : "{:s}",\n'.format('"{:s}"'.format(m), desc))
        theS.write('}\n')
        theS.write(' DONE: All mnemonics and their descriptions '.center(75, '-'))
        theS.write('\n')

    def pprintCurveDesc(self, theS=sys.stdout):
        theS.write(' Curve mnemonics and their descriptions '.center(75, '-'))
        theS.write('\n')
        for m in sorted(self._curveDescMap.keys()):
            desc = self._retMostPopularDescription(self._curveDescMap, m)
            theS.write('{:10s} : "{:s}",\n'.format('"{:s}"'.format(m), desc))
        theS.write('}\n')
        theS.write(' DONE: Curve mnemonics and their descriptions '.center(75, '-'))
        theS.write('\n')

    def pprintUnitDesc(self, theS=sys.stdout):
        theS.write(' Units and the channels that use them '.center(75, '-'))
        theS.write('\n')
        for m in sorted(self._unitDescMap.keys()):
            desc = self._retMostPopularDescription(self._unitDescMap, m)
            theS.write('{:10s} : "{:s}",\n'.format('"{:s}"'.format(m), desc))
        theS.write('}\n')
        theS.write(' DONE: Units and the channels that use them '.center(75, '-'))
        theS.write('\n')

    def pprintSizeTime(self, theS=sys.stdout):
        theS.write(' Size/Time (bytes/sec) '.center(75, '-'))
        theS.write('\n')
        for s in sorted(self._sizeTimeMap.keys()):
            for t in self._sizeTimeMap[s]:
                theS.write('{:d}\t{:g}\n'.format(s, t))
        theS.write(' DONE: Size/Time (bytes/sec) '.center(75, '-'))
        theS.write('\n')

    def pprintWsd(self, theS=sys.stdout):
        theS.write(' Count of well site mnemonics and the % of files that have them '.center(75, '-'))
        theS.write('\n')
#        theS.write(pprint.pformat(self._wsdMnemCount))
#        theS.write('\n')
        theS.write('{\n')
        for m in sorted(self._wsdMnemCount.keys()):
            if m in self._mnemDescMap:
                desc = self._retMostPopularDescription(self._mnemDescMap, m)
            else:
                desc = 'N/A'
            theS.write('{:12s} : {:8d}, # {:8.2%} {:s}\n'.format(
                    '"{:s}"'.format(m),
                    self._wsdMnemCount[m],
                    self._wsdMnemCount[m] / self._cntrs['file'],
                    desc,
                )
            )
        theS.write('}\n')
        theS.write(' DONE: Count of well site mnemonics and the % of files that have them '.center(75, '-'))
        theS.write('\n')

    def results(self):
        r = ['ReadLASFiles:']
        r.append('   Files: {:10d}'.format(self._cntrs['file']))
        r.append('  Errors: {:10d}'.format(self._cntrs['erro']))
        r.append('Critical: {:10d}'.format(self._cntrs['crit']))
        r.append('Files OK: {:10d}'.format(self._cntrs['file'] - self._cntrs['erro'] - self._cntrs['crit']))
        r.append('   Bytes: {:10d} ({:g} Mb)'.format(self._cntrs['byte'], self._cntrs['byte'] / 1024**2))
        r.append('Sections: {:10d}'.format(self._cntrs['sect']))
        r.append('  Frames: {:10d}'.format(self._cntrs['fram']))
        r.append('    Data: {:10d} ({:g} M)'.format(self._cntrs['data'], self._cntrs['data'] / 1024**2))
        return '\n'.join(r)

def main():
    """Main entry point."""
    usage = """usage: %prog [options] dir
Recursively reads LAS files in a directory reporting information about their contents."""
    print ('Cmd: %s' % ' '.join(sys.argv))
    optParser = OptionParser(usage, version='%prog ' + __version__)
#    optParser.add_option("-k", "--keep-going", action="store_true", dest="keepGoing", default=False, 
#                      help="Keep going as far as sensible. [default: %default]")
#    optParser.add_option("-r", "--recursive", action="store_true", dest="recursive", default=False, 
#                      help="Process input recursively. [default: %default]")
#    optParser.add_option(
#            "-j", "--jobs",
#            type="int",
#            dest="jobs",
#            default=-1,
#            help="Max processes when multiprocessing. Zero uses number of native CPUs [%d]. -1 disables multiprocessing." \
#                    % multiprocessing.cpu_count() \
#                    + " [default: %default]" 
#        )      
    optParser.add_option(
            "-l", "--loglevel",
            type="int",
            dest="loglevel",
            default=40,
            help="Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: %default]"
        )      
    opts, args = optParser.parse_args()
    clkStart = time.clock()
    timStart = time.time()
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    # Your code here
    if len(args) != 1:
        optParser.print_help()
        optParser.error("I need a directory to read from!")
        return 1
    myReader = ReadLASFiles(args[0])
    myReader.pprintMnemDesc()
    myReader.pprintCurveDesc()
    myReader.pprintUnitDesc()
    # pprint.pprint(myReader._mnemDescMap)
    myReader.pprintWsd()
    # myReader.pprintSizeTime()
    print(myReader.results())
    print('  CPU time = %8.3f (S)' % (time.clock() - clkStart))
    print('Exec. time = %8.3f (S)' % (time.time() - timStart))
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    multiprocessing.freeze_support()
    sys.exit(main())
