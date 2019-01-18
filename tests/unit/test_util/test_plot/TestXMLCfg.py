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

Created on Dec 14, 2011

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

import sys
import logging
import time
import unittest
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

from TotalDepth.util.plot import XMLCfg

class TestLgXMLBase(unittest.TestCase):

    def setUp(self):
        self._lxb = XMLCfg.LgXMLBase()

    def tearDown(self):
        pass

    def test_00(self):
        """TestLgXMLBase.test_00(): Test setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestLgXMLBase.test_01(): Test checkRoot() succeeds"""
        root = etree.fromstring('<LgFormat UniqueId="Sonic_3Track.xml" xmlns="x-schema:LgSchema2.xml"/>')
        self.assertTrue(self._lxb.checkRoot(root))
        
    def test_02(self):
        """TestLgXMLBase.test_02(): Test checkRoot() fails on root element"""
        root = etree.fromstring('<LGFORMAT UniqueId="Sonic_3Track.xml" xmlns="x-schema:LgSchema2.xml"/>')
        self.assertFalse(self._lxb.checkRoot(root))
        
    def test_03(self):
        """TestLgXMLBase.test_03(): Test checkRoot() fails on missing attribute."""
        root = etree.fromstring('<LgFormat xmlns="x-schema:LgSchema2.xml"/>')
        self.assertFalse(self._lxb.checkRoot(root))
        
    def test_04(self):
        """TestLgXMLBase.test_04(): Test str()."""
        root = etree.fromstring('<root UniqueId="1"><elem>Some text</elem></root>')
        self.assertEqual("Some text", self._lxb.str(root, 'elem'))
        self.assertTrue(self._lxb.str(root, 'element') is None)
        self.assertEqual("unknown", self._lxb.str(root, 'element', 'unknown'))

    def test_05(self):
        """TestLgXMLBase.test_05(): Test bool()."""
        root = etree.fromstring('<root UniqueId="1"><elem>1</elem></root>')
        self.assertTrue(self._lxb.bool(root, 'elem'))
        root = etree.fromstring('<root UniqueId="1"><elem>  1  </elem></root>')
        self.assertTrue(self._lxb.bool(root, 'elem'))
        root = etree.fromstring('<root UniqueId="1"><elem>0</elem></root>')
        self.assertFalse(self._lxb.bool(root, 'elem'))
        root = etree.fromstring('<root UniqueId="1"><elem>  0  </elem></root>')
        self.assertFalse(self._lxb.bool(root, 'elem'))
        # Using default
        root = etree.fromstring('<root UniqueId="1"><elem>0</elem><elem>1</elem></root>')
        self.assertTrue(self._lxb.bool(root, 'elem', True))

    def test_06(self):
        """TestLgXMLBase.test_06(): Test int()."""
        root = etree.fromstring('<root UniqueId="1"><elem>1</elem></root>')
        self.assertEqual(1, self._lxb.int(root, 'elem'))
        root = etree.fromstring('<root UniqueId="1"><elem>  1  </elem></root>')
        self.assertEqual(1, self._lxb.int(root, 'elem'))
        root = etree.fromstring('<root UniqueId="1"><elem>0</elem></root>')
        self.assertEqual(0, self._lxb.int(root, 'elem'))
        root = etree.fromstring('<root UniqueId="1"><elem>  0  </elem></root>')
        self.assertEqual(0, self._lxb.int(root, 'elem'))
        # Using default
        root = etree.fromstring('<root UniqueId="1"><elem>12</elem><elem>45</elem></root>')
        self.assertEqual(42, self._lxb.int(root, 'elem', 42))

    def test_07(self):
        """TestLgXMLBase.test_07(): Test float()."""
        root = etree.fromstring('<root UniqueId="1"><elem>1.0</elem></root>')
        self.assertEqual(1., self._lxb.float(root, 'elem'))
        root = etree.fromstring('<root UniqueId="1"><elem>  1.  </elem></root>')
        self.assertEqual(1., self._lxb.float(root, 'elem'))
        root = etree.fromstring('<root UniqueId="1"><elem>0</elem></root>')
        self.assertEqual(0., self._lxb.float(root, 'elem'))
        root = etree.fromstring('<root UniqueId="1"><elem>  0  </elem></root>')
        self.assertEqual(0., self._lxb.float(root, 'elem'))
        # Using default
        root = etree.fromstring('<root UniqueId="1"><elem>12.0</elem><elem>45.0</elem></root>')
        self.assertEqual(42.0, self._lxb.float(root, 'elem', 42.0))

    def test_10(self):
        """TestLgXMLBase.test_07(): Test tagsInNs()."""
        self.assertEqual(
            '{x-schema:LgSchema2.xml}LgFormat/{x-schema:LgSchema2.xml}LgTrack',
            self._lxb.tagsInNs('LgFormat', 'LgTrack'),
        )

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLgXMLBase))
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
    clkStart = time.perf_counter()
    unitTest()
    clkExec = time.perf_counter() - clkStart
    print(('CPU time = %8.3f (S)' % clkExec))
    print('Bye, bye!')

if __name__ == "__main__":
    main()
