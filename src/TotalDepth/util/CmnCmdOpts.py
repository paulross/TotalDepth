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

Copyright (c) 2010-2019 Paul Ross. All rights reserved.
"""
import logging
import multiprocessing
import argparse
import sys

__author__  = 'Paul Ross'
__date__    = '2011-05-23'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2010-2019 Paul Ross. All rights reserved.'


DEFAULT_OPT_MP_JOBS = -1
DEFAULT_OPT_LOG_LEVEL = 30


def argParser(desc, prog=None, version=None, allow_multiprocessing=True):
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
    if allow_multiprocessing:
        parser.add_argument(
            "-j", "--jobs",
            type=int,
            dest="jobs",
            default=DEFAULT_OPT_MP_JOBS,
            help="Max processes when multiprocessing."
                 f"Zero uses number of native CPUs [{multiprocessing.cpu_count()}]."
                 " -1 disables multiprocessing. Default: %(default)s."
        )
    parser.add_argument("-k", "--keep-going", action="store_true", dest="keepGoing", default=False, 
                        help="Keep going as far as sensible. Default: %(default)s.")
    # logging._levelToName[level]
    # parser.add_argument(
    #         "-l", "--loglevel",
    #         type=int,
    #         dest="logLevel",
    #         default=DEFAULT_OPT_LOG_LEVEL,
    #         help="Log Level (debug=10, info=20, warning=30, error=40, critical=50). Default: %(default)s."
    #     )
    log_level_help_mapping = ', '.join(
        ['{:d}<->{:s}'.format(level, logging._levelToName[level]) for level in sorted(logging._levelToName.keys())]
    )
    log_level_help = f'Log Level as an integer or symbol. ({log_level_help_mapping}) [default: %(default)s]'
    parser.add_argument(
            "-l", "--log-level",
            # type=int,
            # dest="loglevel",
            default=DEFAULT_OPT_LOG_LEVEL,
            help=log_level_help
        )
    return parser


def argParserIn(*args, **kwargs):
    """
    Return an command line parser with the standard pre-set options plus an input path as an argument.
    """
    myP = argParser(*args, **kwargs)
    # Input specific arguments
    myP.add_argument("-g", "--glob", action="store_true", dest="glob", default=None, 
                      help="File match pattern. Default: %(default)s.")
    myP.add_argument("-r", "--recursive", action="store_true", dest="recursive", default=False, 
                      help="Process input recursively. Default: %(default)s.")
    myP.add_argument('pathIn', metavar='in', type=str, help='Input path.')
    return myP


def argParserInOut(*args, **kwargs):
    """
    Return an command line parser with the standard pre-set options plus an input and output paths as an arguments.
    """
    myP = argParserIn(*args, **kwargs)
    myP.add_argument('pathOut', metavar='out', type=str, help='Output path.')
    return myP


def set_log_level(parsed_args) -> None:
    if parsed_args.log_level in logging._nameToLevel:
        log_level = logging._nameToLevel[parsed_args.log_level]
    else:
        log_level = int(parsed_args.log_level)
    # Initialise logging etc.
    logging.basicConfig(level=log_level,
                        format='%(asctime)s %(process)d %(levelname)-8s %(message)s',
                        #datefmt='%y-%m-%d % %H:%M:%S',
                        stream=sys.stdout)

