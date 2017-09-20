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
"""Common command line options, this is to try and present some degree of
interface consistency among command line applications.

Copyright (c) 2010-2011 Paul Ross. All rights reserved.
"""
__author__  = 'Paul Ross'
__date__    = '2011-05-23'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2010-2012 Paul Ross. All rights reserved.'

import multiprocessing
import argparse

DEFAULT_OPT_MP_JOBS = -1
DEFAULT_OPT_LOG_LEVEL = 40

def argParser(desc, prog=None, version=None):
    """Return an command line parser with the standard pre-set options.
    
    Standard options are ``-h, --version`` and:
    
    ``-j``: Multiprocessing job control.
    
    ``-k``: Flag to indicate that we should keep going as far as sensible.
    
    ``-l``: Log level.
    """
    parser = argparse.ArgumentParser(description=desc, epilog=__rights__, prog=prog)
    if version is not None:
        parser.add_argument('--version', action='version', version='%(prog)s '+version)
    # Adding arguments in, well sort of, alphabetical order (not really)
    parser.add_argument(
            "-j", "--jobs",
            type=int,
            dest="jobs",
            default=DEFAULT_OPT_MP_JOBS,
            help="Max processes when multiprocessing. Zero uses number of native CPUs [%d]. -1 disables multiprocessing." \
                    % multiprocessing.cpu_count() \
                    + " Default: %(default)s." 
        )      
    parser.add_argument("-k", "--keep-going", action="store_true", dest="keepGoing", default=False, 
                      help="Keep going as far as sensible. Default: %(default)s.")
    parser.add_argument(
            "-l", "--loglevel",
            type=int,
            dest="logLevel",
            default=DEFAULT_OPT_LOG_LEVEL,
            help="Log Level (debug=10, info=20, warning=30, error=40, critical=50). Default: %(default)s."
        )
    return parser

def argParserIn(*args, **kwargs):
    """Return an command line parser with the standard pre-set options plus an input path as an argument."""
    myP = argParser(*args, **kwargs)
    # Input specific arguments
    myP.add_argument("-g", "--glob", action="store_true", dest="glob", default=None, 
                      help="File match pattern. Default: %(default)s.")
    myP.add_argument("-r", "--recursive", action="store_true", dest="recursive", default=False, 
                      help="Process input recursively. Default: %(default)s.")
    myP.add_argument('pathIn', metavar='in', type=str, help='Input path.')
    return myP

def argParserInOut(*args, **kwargs):
    """Return an command line parser with the standard pre-set options plus an input and output paths as an arguments."""
    myP = argParserIn(*args, **kwargs)
    myP.add_argument('pathOut', metavar='out', type=str, help='Output path.')
    return myP

