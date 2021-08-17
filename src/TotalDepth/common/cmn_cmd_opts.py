#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation.
# Copyright (C) 2011-2021 Paul Ross
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

import typing


def arg_parser(desc, prog=None, version=None, **kwargs) -> argparse.ArgumentParser:
    """Return an command line parser with the standard pre-set options.
    
    Standard options are ``-h, --version`` and:
    
    ``-k``: Flag to indicate that we should keep going as far as sensible.
    
    ``-l``: Log level.

    ``-v``: Verbosity.
    """
    parser = argparse.ArgumentParser(description=desc, prog=prog, **kwargs)
    if version is not None:
        parser.add_argument('--version', action='version', version='%(prog)s '+version)
    # Adding arguments in, well sort of, alphabetical order (not really)
    parser.add_argument("-k", "--keep-going", action="store_true", dest="keepGoing", default=False,
                        help="Keep going as far as sensible. Default: %(default)s.")
    parser.add_argument(
        "-v", "--verbose", action='count', default=0,
        help="Increase verbosity, additive [default: %(default)s]",
    )
    return parser


def path_in(*args, **kwargs) -> argparse.ArgumentParser:
    """
    Return an command line parser with the standard pre-set options plus an input path as an argument.
    """
    parser = arg_parser(*args, **kwargs)
    # Input specific arguments
    # parser.add_argument("-g", "--glob", action="store_true", dest="glob", default=None,
    #                   help="File match pattern. Default: %(default)s.")
    parser.add_argument("-r", "--recurse", action="store_true", dest="recurse", default=False,
                      help="Process the input recursively. Default: %(default)s.")
    parser.add_argument('path_in', type=str, help='Input path.')
    return parser


def path_in_out(*args, **kwargs) -> argparse.ArgumentParser:
    """
    Return an command line parser with the standard pre-set options plus an input and output paths as an arguments.
    """
    parser = path_in(*args, **kwargs)
    parser.add_argument('path_out', type=str, help='Output path.', nargs='?')
    return parser


def path_in_out_required(*args, **kwargs) -> argparse.ArgumentParser:
    """
    Return an command line parser with the standard pre-set options plus an input and output paths as an arguments.
    """
    parser = path_in(*args, **kwargs)
    parser.add_argument('path_out', type=str, help='Output path.')
    return parser


# ============ Logging ==================

#: Default log level
DEFAULT_OPT_LOG_LEVEL = 30  # Warning
#: Default log format (terse)
DEFAULT_OPT_LOG_FORMAT = '%(asctime)s %(process)d %(levelname)-8s %(message)s'
#: Default log format (verbose)
DEFAULT_OPT_LOG_FORMAT_VERBOSE = '%(asctime)s - %(filename)-16s#%(lineno)-4d - %(process)5d - (%(threadName)-10s) - %(levelname)-8s - %(message)s'


def _get_logging_level_to_name() -> typing.Dict[int, str]:
    # Weird, in Python 3.6 logging._levelToName is not the inverse of logging._nameToLevel
    ret = {k:v for k, v in logging._levelToName.items()}
    for k, v in logging._nameToLevel.items():
        ret[v] = k
    return ret


def _get_logging_name_to_level() -> typing.Dict[str, int]:
    return {v:k for k, v in _get_logging_level_to_name().items()}


def add_log_level(parser: argparse.ArgumentParser, level: int = DEFAULT_OPT_LOG_LEVEL) -> None:
    """
    Adds log level to the argument parser.
    The value can be either an integer of a string so 20 and 'INFO' are equivalent.
    """
    # Weird, in Python 3.6 logging._levelToName is not the inverse of logging._nameToLevel
    log_int_map = _get_logging_level_to_name()
    log_level_help_mapping = ', '.join(
        ['{:d}<->{:s}'.format(level, log_int_map[level]) for level in sorted(log_int_map.keys())]
    )
    log_level_help = f'Log Level as an integer or symbol. ({log_level_help_mapping}) [default: %(default)s]'
    parser.add_argument("-l", "--log-level", default=level, help=log_level_help)


def set_log_level(parsed_args, format: str = DEFAULT_OPT_LOG_FORMAT_VERBOSE) -> int:
    """Initialise logging."""
    log_name_map = _get_logging_name_to_level()
    # print(logging._nameToLevel)
    # print(logging._levelToName)
    # print(_get_logging_level_to_name())
    # print(_get_logging_name_to_level())
    if parsed_args.log_level in log_name_map:
        log_level = logging._nameToLevel[parsed_args.log_level]
    else:
        log_level = int(parsed_args.log_level)
    logging.basicConfig(level=log_level, format=format, stream=sys.stdout)
    return log_level

# ============ END: Logging ==================

# ============ Multiprocessing ==================


DEFAULT_OPT_MP_JOBS = -1


def add_multiprocessing(parser: argparse.ArgumentParser) -> None:
    """Adds log level to the argument parser as --jobs."""
    parser.add_argument(
        "-j", "--jobs",
        type=int,
        dest="jobs",
        default=DEFAULT_OPT_MP_JOBS,
        help="Max processes when multiprocessing."
            f"Zero uses number of native CPUs [{multiprocessing.cpu_count()}]."
            " Negative value disables multiprocessing code. Default: %(default)s."
    )


def multiprocessing_requested(parsed_args) -> bool:
    """Returns True if the ``--jobs=`` option requires multiprocessing."""
    if 'jobs' in parsed_args:
        return parsed_args.jobs >= 0
    return False


def number_multiprocessing_jobs(parsed_args) -> int:
    """Returns the number of multiprocessing nodes interpreted from the``--jobs=`` option."""
    # TODO: Use this or lose it.
    if multiprocessing_requested(parsed_args):
        if parsed_args.jobs == 0:
            return multiprocessing.cpu_count()
        return parsed_args.jobs
    return 1

# ============ END: Multiprocessing ==================
