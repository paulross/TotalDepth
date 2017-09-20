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

from TotalDepth.RP66.core import VisiRec

def scanFile(fp, keepGoing, theS=sys.stdout):
    try:
        myVr = VisiRec.VisibleRecordRead(fp)
    except VisiRec.ExceptionVisRec as err:
        print('Can not open file, error: %s' % str(err))
        return
    theS.write('File:\n')
    theS.write('{:s}\n'.format(myVr.strOfFile))
    numVR = 0
    while True:
        numVR += 1
        myStr = '{:s}'.format(myVr)
        l = myVr.skipToNextRecord()
        if l < 0:
            theS.write('EOF\n')
            break
        theS.write('{:s} data length={:d}\n'.format(myStr, l))
    theS.write('Visible Record count: %d\n' % numVR)

def main():
    usage = """usage: %prog [options] file
Scans a RP66 file and reports Visible Record structure."""
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

    
    
    