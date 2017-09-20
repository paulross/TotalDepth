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
"""Removes TIF markers from files.

Created on Nov 28, 2011

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2011-11-28'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

import sys
import logging
import time
import multiprocessing
from optparse import OptionParser

from TotalDepth.LIS.core import TifMarker
from TotalDepth.LIS.core import RawStream

def stripTIF(pIn, pOut, nervous=False):
    with RawStream.RawStream(pIn) as sIn:
        if nervous:
            _stripTIF(sIn, None)
        else:
            with RawStream.RawStream(pOut, mode='wb') as sOut:
                _stripTIF(sIn, sOut)
            
def _stripTIF(sIn, sOut):
    myTm = TifMarker.TifMarkerRead(sIn, allowPrPadding=False)
    if myTm.hasTif:
        while myTm.tifType == 0:
            bLen = myTm.tifNext - sIn.tell()
            msg = 'stripTif(): Tell: 0x{:08x} Len: 0x{:08x} TIF: {:s}'.format(sIn.tell(), bLen, str(myTm))
            logging.debug(msg)
            if sOut is None:
                print(msg)
                sIn.seek(myTm.tifNext)
            else:
                sOut.write(sIn.read(bLen))
            try:
                myTm.read(sIn)
            except RawStream.ExceptionRawStreamEOF as err:
                logging.error('Premature EOF of input so output terminated: {:s}'.format(str(err)))
                return

def main():
    usage = """usage: %prog [options] in out
Writes a new file without TIF markers."""
    print ('Cmd: %s' % ' '.join(sys.argv))
    optParser = OptionParser(usage, version='%prog ' + __version__)
    optParser.add_option("-n", "--nervous", action="store_true", dest="nervous", default=False, 
                      help="Nervous mode (do no harm). [default: %default]")
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
    if len(args) not in (1, 2):
        optParser.print_help()
        optParser.error('Not enough arguments')
        return 1
    nervous = opts.nervous or len(args) == 1
    stripTIF(args[0], args[1], nervous=nervous)
    print('  CPU time = %8.3f (S)' % (time.clock() - clkStart))
    print('Exec. time = %8.3f (S)' % (time.time() - timStart))
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    multiprocessing.freeze_support()
    sys.exit(main())
