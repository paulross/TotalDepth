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

Created on Oct 11, 2011

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

import os
import sys
import logging
import time
import unittest

import TotalDepth.RP66.core.RepCode as RepCode
import TotalDepth.RP66.core.AttrComp as AttrComp

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import BaseTestClasses

class TestAttrCompBasic(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        pass

    def test_01(self):
        """TestAttrCompBasic.test_01(): Simple creation of a single template object."""
        sOut = BaseTestClasses.MockStreamWrite()
        RepCode.writeIDENT(RepCode.IDENTString(b'WEIGHT'), sOut)
        # FSINGL is code 2
        RepCode.writeUSHORT(2, sOut)
        RepCode.writeUNITS(RepCode.UNITSString('KG'), sOut)
        sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
        myTemplate = AttrComp.AttrCompStream(int('10110', 2), sIn)
#        print(myTemplate)
        self.assertEqual(RepCode.IDENTString(b'WEIGHT'), myTemplate.lable)
        self.assertEqual(b'WEIGHT', myTemplate.lable.payload)
        self.assertEqual(2, myTemplate.repCode)
        self.assertEqual(RepCode.UNITSString(b'KG'), myTemplate.units)
        self.assertEqual(b'KG', myTemplate.units.payload)

    def test_02(self):
        """TestAttrCompBasic.test_02(): Creation of a template object and a partial object."""
        sOut = BaseTestClasses.MockStreamWrite()
        RepCode.writeIDENT(RepCode.IDENTString(b'WEIGHT'), sOut)
        # FSINGL is code 2
        RepCode.writeUSHORT(2, sOut)
        RepCode.writeUNITS(RepCode.UNITSString('KG'), sOut)
#        print('TRACE: sOut.bytes', sOut.bytes)
        sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
        myTemplate = AttrComp.AttrCompStream(int('10110', 2), sIn)
#        print(myTemplate)
        self.assertEqual(RepCode.IDENTString(b'WEIGHT'), myTemplate.lable)
        self.assertEqual(b'WEIGHT', myTemplate.lable.payload)
        # Now create object
        sOut = BaseTestClasses.MockStreamWrite()
        RepCode.writeFSINGL(356.2, sOut)
        sIn = BaseTestClasses.MockStreamRead(sOut.bytes)
        myObject = myTemplate.readAsTemplate(int('00001', 2), sIn)
#        print(myObject)
        self.assertEqual(RepCode.IDENTString(b'WEIGHT'), myObject.lable)
        self.assertEqual(b'WEIGHT', myObject.lable.payload)
        self.assertEqual(1, myObject.count)
        self.assertEqual(2, myObject.repCode)
        self.assertEqual(RepCode.UNITSString(b'KG'), myObject.units)
        self.assertEqual(b'KG', myObject.units.payload)
#        self.assertEqual(356.2, myObject.value)
        self.assertAlmostEqual(356.2, myObject.value, 2)
        
class TestAttrV1Example(unittest.TestCase):
    """Tests the example given in version 1 of the RP66 specification,
    figure 3.8. See: http://w3.energistics.org/rp66/v1/rp66v1_sec3.html"""

    def setUp(self):
        """This comes from the the example given in version 1 of the RP66
        specification, figure 3.8. See: http://w3.energistics.org/rp66/v1/rp66v1_sec3.html"""
        self._data = BaseTestClasses.MockStreamRead(
            # Logical Records Segment (#1) Header
            # Length == 104 bytes
            b'\x00\x68'
            # Attributes = 10100110
            + b'\a6'
            # Type = CHANNEL
            + b'\x03'
            # Channel Set
            # -----------
            # SET:TN
            + b'\xf8'
            # "CHANNEL"
            + b'\x07\x43\x48\x41\x4e\x4e\x45\x4c'
            # ???
            + b'\x01\x30'
            # Template
            # --------
            # Attribute: LR
            + b'\x34'
            # "LONG-NAME"
            + b'\x09\x4c\x4f\x4e\x47\x2d\x4e\x41\x4d\x45'
            # OBNAME
            + b'\x17'
            # .................................................................
            # Attribute: LRV
            + b'\x35'
            # "ELEMENT-LIMIT"
            + b'\x0d\x45\x4c\x45\x4d\x45\x4e\x54\x2d\x4c\x49\x4d\x49\x54'
            # UVARI
            + b'\x12'
            # 1
            + b'\x01'
            # .................................................................
            # Attribute: LRV
            + b'\x35'
            # "REPRESENTATION-CODE"
            + b'\x13REPRESENTATION-CODE'
            # USHORT
            + b'\x0f'
            # FSINGL
            + b'\x02'
            # .................................................................
            # Attribute: LRV
            + b'\x35'
            # "UNITS"
            + b'\x05UNITS'
            # .................................................................
            # Attribute: LRV
            + b'\x35'
            # "DIMENSION"
            + b'\x09DIMENSION'
            # UVARI
            + b'\x12'
            # 1
            + b'\x01'
            # Object 1
            # --------
            # OBJECT:N
            + b'\x70'
            # "TIME"
            + b'\x00\x00\x04TIME'
            # ATTRIB:V
            + b'\x21'
            # '1'
            + b'\x00\x00\x01\x31'
            # Logical Records Segment (#1) Trailer
            # Checksum - this is probably wrong!
            + b'\x00\x00'
            # Length == 104 bytes
            + b'\x00\x68'
            # TODO:
        )
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """TestAttrV1Example.test_00(): Test setUp() and tearDown()."""
        pass

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAttrCompBasic))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAttrV1Example))
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
