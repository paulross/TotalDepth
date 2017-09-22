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
"""Tests ...

Created on Feb 13, 2012

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2012-02-13'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2012 Paul Ross.'

import sys
import logging
import time
import unittest

from TotalDepth.util import CmnCmdOpts

class TestCmnCmdOpts(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """TestCmnCmdOpts.test_00(): Tests setUp() and tearDown()."""
        pass

#     def test_01(self):
#         """TestCmnCmdOpts.test_01(): basic use of CmnCmdOpts.argParser()."""
#         myP = CmnCmdOpts.argParser("Description", "Program", "Version")
#         myNs = myP.parse_args()
# #        print()
# #        print(myNs)
#         self.assertEqual(CmnCmdOpts.DEFAULT_OPT_MP_JOBS, myNs.jobs)
#         self.assertEqual(CmnCmdOpts.DEFAULT_OPT_LOG_LEVEL, myNs.logLevel)
#         self.assertFalse(myNs.keepGoing)

    def test_02(self):
        """TestCmnCmdOpts.test_02(): use of -h."""
        myP = CmnCmdOpts.argParser("Description of the program", "Name of the program", "0.1.3rc4")
        try:
            print()
            myNs = myP.parse_args(['-h',])
            self.fail('SystemExit not raised: %s' % myNs)
        except SystemExit:
            pass

    def test_03(self):
        """TestCmnCmdOpts.test_03(): use of --help."""
        myP = CmnCmdOpts.argParser("Description of the program", "Name of the program", "0.1.3rc4")
        try:
            print()
            myNs = myP.parse_args(['--help',])
            self.fail('SystemExit not raised: %s' % myNs)
        except SystemExit:
            pass

    def test_04(self):
        """TestCmnCmdOpts.test_04(): use of -h with minimal parser creation."""
        myP = CmnCmdOpts.argParser("Description of the program only, no program name, no version")
        try:
            print()
            myNs = myP.parse_args(['-h',])
            self.fail('SystemExit not raised: %s' % myNs)
        except SystemExit:
            pass

    def test_05(self):
        """TestCmnCmdOpts.test_05(): use of --version."""
        myP = CmnCmdOpts.argParser("Description of the program", "PROG", version="v0.1.3rc4")
        try:
            print()
            myNs = myP.parse_args(['--version',])
            self.fail('SystemExit not raised: %s' % myNs)
        except SystemExit:
            pass

    def test_06(self):
        """TestCmnCmdOpts.test_06(): use of --version and prog=None."""
        myP = CmnCmdOpts.argParser("Description of the program", None, version="v0.1.3rc4")
        try:
            print()
            myNs = myP.parse_args(['--version',])
            self.fail('SystemExit not raised: %s' % myNs)
        except SystemExit:
            pass

    def test_07(self):
        """TestCmnCmdOpts.test_06(): use of --version minimal parser creation should fail with unrecognised arguments."""
        myP = CmnCmdOpts.argParser("Description of the program only, no program name, no version")
        try:
            print()
            myNs = myP.parse_args(['--version',])
            self.fail('SystemExit not raised: %s' % myNs)
        except SystemExit:
            pass

    def test_10(self):
        """TestCmnCmdOpts.test_10(): use of CmnCmdOpts.argParser() and adding a list option."""
        myP = CmnCmdOpts.argParser("Description", "Program", "Version")
        myP.add_argument(
            "-I", "--INCLUDE",
            action="append",
            dest="includes",
            default=[],
            help="Include paths (additive). [default: %default]",
        )
        myNs = myP.parse_args([])
        self.assertEqual([], myNs.includes)
        myNs = myP.parse_args(['-I', '123', '--INCLUDE', '4'])
#        print()
#        print(myNs)
        self.assertEqual(['123', '4',], myNs.includes)

    def test_11(self):
        """TestCmnCmdOpts.test_11(): use of CmnCmdOpts.argParser() and adding a enumerated option with choices."""
        myP = CmnCmdOpts.argParser("Description", "Program", "Version")
        myP.add_argument(
            "-f", "--file-type",
            choices=['LAS', 'LIS', 'AUTO'],
        )
        myNs = myP.parse_args([])
        self.assertTrue(myNs.file_type is None)
        myNs = myP.parse_args('-f LIS'.split())
        self.assertEqual('LIS', myNs.file_type)
        try:
            print()
            myNs = myP.parse_args('-f WTF'.split())
            self.fail('SystemExit not raised.')
        except SystemExit:
            pass

    def test_12(self):
        """TestCmnCmdOpts.test_12(): use of CmnCmdOpts.argParser() and adding scale option as a list of integers."""
        myP = CmnCmdOpts.argParser("Description", "Program", "Version")
        myP.add_argument("-s", "--scale", action="append", type=int, dest="scales", default=[],
                help="Scale of X axis to use (additive). [default: []].")
        myNs = myP.parse_args([])
        self.assertEqual([], myNs.scales)
        myNs = myP.parse_args('-s 47'.split())
        self.assertEqual([47,], myNs.scales)
        myNs = myP.parse_args('-s 47 --scale=49'.split())
        self.assertEqual([47, 49], myNs.scales)
        try:
            print()
            myNs = myP.parse_args('-s WTF'.split())
            self.fail('SystemExit not raised.')
        except SystemExit:
            pass

    def test_20(self):
        """TestCmnCmdOpts.test_12(): basic use of CmnCmdOpts.argParserIn()."""
        myP = CmnCmdOpts.argParserIn("Description", "Program", "Version")
        myNs = myP.parse_args(['IN',])
        self.assertEqual('IN', myNs.pathIn)
        self.assertFalse(myNs.recursive)
        self.assertTrue(myNs.glob is None)
        
    def test_22(self):
        """TestCmnCmdOpts.test_22(): basic use of CmnCmdOpts.argParserInOut()."""
        myP = CmnCmdOpts.argParserInOut("Description", "Program", "Version")
        myNs = myP.parse_args(['IN', 'OUT'])
        self.assertEqual('IN', myNs.pathIn)
        self.assertEqual('OUT', myNs.pathOut)

    def test_23(self):
        """TestCmnCmdOpts.test_23(): basic use of CmnCmdOpts.argParserInOut() with -h option."""
        myP = CmnCmdOpts.argParserInOut("Description", "Program", "Version")
        myNs = myP.parse_args(['IN', 'OUT'])
        self.assertEqual('IN', myNs.pathIn)
        self.assertEqual('OUT', myNs.pathOut)
        try:
            print()
            myNs = myP.parse_args(['-h',])
            self.fail('SystemExit not raised: %s' % myNs)
        except SystemExit:
            pass
    
    def test_24(self):
        """TestCmnCmdOpts.test_24(): basic use of CmnCmdOpts.argParserInOut() format_usage() and format_help()."""
        myP = CmnCmdOpts.argParserInOut("Description", "Program", "Version")
        myNs = myP.parse_args(['IN', 'OUT'])
        self.assertEqual('IN', myNs.pathIn)
        self.assertEqual('OUT', myNs.pathOut)
        # print()
#        print(dir(myP))
#        print(dir(myNs))
#        print(myNs._get_args())
#        print(myNs._get_kwargs())
#        print(myP.format_usage())
#         print(myP.format_help())
        self.assertEqual("""usage: Program [-h] [--version] [-j JOBS] [-k] [-l LOGLEVEL] [-g] [-r] in out
""", myP.format_usage())
        self.assertEqual("""usage: Program [-h] [--version] [-j JOBS] [-k] [-l LOGLEVEL] [-g] [-r] in out

Description

positional arguments:
  in                    Input path.
  out                   Output path.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -j JOBS, --jobs JOBS  Max processes when multiprocessing. Zero uses number
                        of native CPUs [4]. -1 disables multiprocessing.
                        Default: -1.
  -k, --keep-going      Keep going as far as sensible. Default: False.
  -l LOGLEVEL, --loglevel LOGLEVEL
                        Log Level (debug=10, info=20, warning=30, error=40,
                        critical=50). Default: 40.
  -g, --glob            File match pattern. Default: None.
  -r, --recursive       Process input recursively. Default: False.

Copyright (c) 2010-2012 Paul Ross. All rights reserved.
""", myP.format_help())
    
class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCmnCmdOpts))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Test ..."""
    print("""Test.py - A module that tests ...
Usage:
python Test....py [-lh --help]

Options:
-h, --help  Help (this screen) and exit

Options (debug):
-l:         Set the logging level higher is quieter.
             Default is 20 (INFO) e.g.:
                CRITICAL    50
                ERROR       40
                WARNING     30
                INFO        20
                DEBUG       10
                NOTSET      0
""")

def main():
    """Invoke unit test code."""
    print(('Test....py script version "%s", dated %s' % (__version__, __date__)))
    print(('Author: %s' % __author__))
    print(__rights__)
    print()
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:", ["help",])
    except getopt.GetoptError:
        usage()
        print('ERROR: Invalid options!')
        sys.exit(1)
    logLevel = logging.INFO
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif o == '-l':
            logLevel = int(a)
    if len(args) != 0:
        usage()
        print('ERROR: Wrong number of arguments!')
        sys.exit(1)
    # Initialise logging etc.
    logging.basicConfig(level=logLevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    clkStart = time.clock()
    unitTest()
    clkExec = time.clock() - clkStart
    print(('CPU time = %8.3f (S)' % clkExec))
    print('Bye, bye!')

if __name__ == "__main__":
    main()
