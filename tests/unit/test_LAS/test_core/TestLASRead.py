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

Created on Jan 11, 2012

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2012 Paul Ross.'

import sys
import logging
import time
import unittest
import pprint
import io

from TotalDepth.LAS.core import LASRead
from TotalDepth.LIS.core import EngVal
from TotalDepth.LIS.core import Mnem

class TestLASReadGenerator(unittest.TestCase):
    """Tests the line generator in the LASRead module."""
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """TestLASReadGenerator.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestLASReadGenerator.test_01(): Tests simple file."""
        myFi = io.StringIO("""
# Some comment

# Another comment
~VERSION INFORMATION

 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
# Stuff
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~A
# Stuff
 1700.0000  -999.2500  -999.2500  -999.2500  -999.2500
# Stuff
 1700.5000    40.7909     0.0218     0.0417    25.9985
# Stuff
 1703.5000    61.1144     0.0199     0.0383    13.2042
""")
        result = [v for v in LASRead.genLines(myFi)]
#        print()
#        pprint.pprint(result)
        exp = [
            (5,  '~VERSION INFORMATION\n'),
            (7,  ' VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0\n'),
            (9,  ' WRAP.                         NO: ONE LINE PER DEPTH STEP\n'),
            (10, '~A\n'),
            (12, ' 1700.0000  -999.2500  -999.2500  -999.2500  -999.2500\n'),
            (14, ' 1700.5000    40.7909     0.0218     0.0417    25.9985\n'),
            (16, ' 1703.5000    61.1144     0.0199     0.0383    13.2042\n'),
        ]
        self.assertEqual(exp, result)

class TestLASReadRegex(unittest.TestCase):
    """Tests regular expressions in the LASRead module."""
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """TestLASReadLowLevel.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestLASReadLowLevel.test_01(): Tests RE_COMMENT."""
        m = LASRead.RE_COMMENT.match('#\n')
        self.assertTrue(m is not None)
        self.assertEqual(1, len(m.groups()))
        self.assertEqual('', m.group(1))
        m = LASRead.RE_COMMENT.match('    #\n')
        self.assertTrue(m is not None)
        self.assertEqual(1, len(m.groups()))
        self.assertEqual('', m.group(1))
        m = LASRead.RE_COMMENT.match('# Some comment   \n')
        self.assertTrue(m is not None)
        self.assertEqual(1, len(m.groups()))
        self.assertEqual(' Some comment   ', m.group(1))
        m = LASRead.RE_COMMENT.match('  # Some comment   \n')
        self.assertTrue(m is not None)
        self.assertEqual(1, len(m.groups()))
        self.assertEqual(' Some comment   ', m.group(1))
        m = LASRead.RE_COMMENT.match('  # Some comment   ')
        self.assertTrue(m is not None)
        self.assertEqual(1, len(m.groups()))
        self.assertEqual(' Some comment   ', m.group(1))
        
    def test_05(self):
        """TestLASReadLowLevel.test_05(): Tests RE_SECT_HEAD."""
        m = LASRead.RE_SECT_HEAD.match('~V\n')
        self.assertTrue(m is not None)
        self.assertEqual(2, len(m.groups()))
        self.assertEqual(('V', None), m.groups())
        m = LASRead.RE_SECT_HEAD.match('~VERSION INFORMATION\n')
        self.assertTrue(m is not None)
        self.assertEqual(2, len(m.groups()))
        self.assertEqual(('V', 'ERSION INFORMATION'), m.groups())

    def test_06(self):
        """TestLASReadLowLevel.test_06(): Tests RE_SECT_HEAD fails."""
        m = LASRead.RE_SECT_HEAD.match('  ~V\n')
        self.assertTrue(m is None)

    def test_10(self):
        """TestLASReadLowLevel.test_10(): Tests RE_LINE_FIELD_0."""
        m = LASRead.RE_LINE_FIELD_0.match('MNEM')
        self.assertTrue(m is not None)
        self.assertEqual(1, len(m.groups()))
        self.assertEqual(('MNEM',), m.groups())
        self.assertEqual('MNEM', m.group(1))
        m = LASRead.RE_LINE_FIELD_0.match(' MNEM')
        self.assertTrue(m is not None)
        self.assertEqual(1, len(m.groups()))
        self.assertEqual(('MNEM',), m.groups())
        self.assertEqual('MNEM', m.group(1))
        m = LASRead.RE_LINE_FIELD_0.match(' MNEM ')
        self.assertTrue(m is not None)
        self.assertEqual(1, len(m.groups()))
        self.assertEqual(('MNEM',), m.groups())
        self.assertEqual('MNEM', m.group(1))

    def test_11(self):
        """TestLASReadLowLevel.test_11(): Tests RE_LINE_FIELD_0 fails."""
        pass

    def test_20(self):
        """TestLASReadLowLevel.test_20(): Tests RE_LINE_FIELD_1."""
        m = LASRead.RE_LINE_FIELD_1.match('FEET    Something   ')
        self.assertTrue(m is not None)
        self.assertEqual(2, len(m.groups()))
        self.assertEqual(('FEET', '    Something   '), m.groups())
        m = LASRead.RE_LINE_FIELD_1.match('FEET    Something   else   ')
        self.assertTrue(m is not None)
        self.assertEqual(2, len(m.groups()))
        self.assertEqual(('FEET', '    Something   else   '), m.groups())
        m = LASRead.RE_LINE_FIELD_1.match(' FEET    Something   ')
        self.assertTrue(m is not None)
        self.assertEqual(2, len(m.groups()))
        self.assertEqual((None, ' FEET    Something   '), m.groups())

    def test_21(self):
        """TestLASReadLowLevel.test_21(): Tests RE_LINE_FIELD_1 fails."""
        pass

    def test_30(self):
        """TestLASReadLowLevel.test_30(): Tests RE_LINE_FIELD_2."""
        m = LASRead.RE_LINE_FIELD_2.match('   Some description \n')
        self.assertTrue(m is not None)
        self.assertEqual(3, len(m.groups()))
        self.assertEqual(('   Some description \n', None, None), m.groups())
        m = LASRead.RE_LINE_FIELD_2.match('   Some description {xxx} | Ref  \n')
        self.assertTrue(m is not None)
        self.assertEqual(3, len(m.groups()))
        self.assertEqual(('   Some description ', '{xxx}', ' Ref  '), m.groups())
        m = LASRead.RE_LINE_FIELD_2.match('Some description{xxx}|Ref\n')
        self.assertTrue(m is not None)
        self.assertEqual(3, len(m.groups()))
        self.assertEqual(('Some description', '{xxx}', 'Ref'), m.groups())
        # Empty line
        m = LASRead.RE_LINE_FIELD_2.match('\n')
        self.assertTrue(m is not None)
        self.assertEqual(3, len(m.groups()))
        self.assertEqual(('\n', None, None), m.groups())

    def test_31(self):
        """TestLASReadLowLevel.test_31(): Tests RE_LINE_FIELD_1 fails."""
        pass
    
class TestLASReadLASFields(unittest.TestCase):
    """Simulates how we read LA fields from a line."""
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """TestLASReadLASFields.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestLASReadLASFields.test_01(): Tests RE_LINE_FIELD_2."""
        l = " NPOR.: LIMEST. NEUTRON POROSITY\n"
        dIdx = l.find('.')
        cIdx = l.rfind(':')
        self.assertTrue(dIdx != -1)
        self.assertTrue(cIdx != -1)
        m0 = LASRead.RE_LINE_FIELD_0.match(l[:dIdx])
        m1 = LASRead.RE_LINE_FIELD_1.match(l[dIdx + 1:cIdx])
        m2 = LASRead.RE_LINE_FIELD_2.match(l[cIdx + 1:])
        self.assertTrue(m0 is not None)
        self.assertTrue(m1 is not None)
        self.assertTrue(m2 is not None)
#        print()
#        print([g for g in (m0.groups() + m1.groups() + m2.groups())])
        self.assertEqual(
            ['NPOR', None, None, ' LIMEST. NEUTRON POROSITY\n', None, None],
            [g for g in (m0.groups() + m1.groups() + m2.groups())],
        )

class TestLASReadLASSection(unittest.TestCase):
    """Tests low level functionality of the LASRead module."""
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """TestLASReadLASSection.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestLASReadLASSection.test_01(): Constructor."""
        myLs = LASRead.LASSection('V')
        self.assertEqual('V', myLs.type)
        self.assertEqual([], myLs._members)
        self.assertEqual(0, len(myLs))
        myLs.finalise()
#        # NOTE: Do not finalise, it will raise!
#        try:
#            myLs.finalise()
#            self.fail('LASRead.ExceptionLASReadSection not raised')
#        except LASRead.ExceptionLASReadSection:
#            pass
        
    def test_02(self):
        """TestLASReadLASSection.test_02(): _val()."""
        myLs = LASRead.LASSection('V')
        # Integers
        self.assertEqual(1234, myLs._val('1234'))
        self.assertEqual(1234, myLs._val('  1234   '))
        # floats
        self.assertEqual(1.234, myLs._val('1.234'))
        self.assertEqual(1.234, myLs._val('   1.234   '))
        self.assertEqual(-12340.0, myLs._val('   -1.234E+4   '))
        self.assertEqual(12340.0, myLs._val('  1234e01   '))
        # bool
        self.assertTrue(myLs._val('YES') is True)
        self.assertTrue(myLs._val('NO') is False)
        # String
        self.assertEqual('WTF', myLs._val(' WTF '))
        # None
        self.assertTrue(myLs._val(None) is None)
        # Anything else
        self.assertTrue(myLs._val(b'') is None)
        
    def test_03(self):
        """TestLASReadLASSection.test_03(): Adding member lines."""
        myLs = LASRead.LASSection('P')
        self.assertEqual('P', myLs.type)
        self.assertEqual([], myLs._members)
        myLs.addMemberLine(2, ' DATE .       13/12/1986                       : LOG DATE  {DD/MM/YYYY}\n')
        myLs.addMemberLine(3, ' STRT .M              1670.0000                : First Index Value\n')
        exp = [
                LASRead.SectLine(mnem='DATE', unit=None, valu='13/12/1986', desc='LOG DATE', format='{DD/MM/YYYY}', assoc=None),
                LASRead.SectLine(mnem='STRT', unit='M', valu=1670.0, desc='First Index Value', format=None, assoc=None),
            ]
#        print()
#        for e in exp:
#            print(e)
#        print()
#        for m in myLs._members:
#            print(m)
        myLs.finalise()
        self.assertEqual(exp, myLs._members)
        self.assertEqual(2, len(myLs))
        str(myLs)
        # Test indexing
        for i in range(len(myLs)):
            self.assertEqual(exp[i], myLs[i])
            self.assertEqual(exp[i], myLs[i])

    def test_04(self):
        """TestLASReadLASSection.test_04(): Adding member lines - fail."""
        myLs = LASRead.LASSection('P')
        self.assertEqual('P', myLs.type)
        self.assertEqual([], myLs._members)
        self.assertRaises(LASRead.ExceptionLASReadSection,
                          # Function
                          myLs.addMemberLine,
                          # Arguments
                          1,
                          '  .       13/12/1986                       : LOG DATE  {DD/MM/YYYY}\n')

    def test_05(self):
        """TestLASReadLASSection.test_05(): Adding member lines to 'V' section in wrong order."""
        myLs = LASRead.LASSection('V')
        self.assertEqual('V', myLs.type)
        self.assertEqual([], myLs._members)
        myLs.addMemberLine(2, ' WRAP.                         NO: ONE LINE PER DEPTH STEP\n')
        myLs.addMemberLine(3, ' VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0\n')
        try:
            myLs.finalise()
            self.fail('LASRead.ExceptionLASReadSection not raised')
        except LASRead.ExceptionLASReadSection:
            pass

    def test_06(self):
        """TestLASReadLASSection.test_06(): Adding member lines to 'V' section in right order, wrong values: 3.0."""
        myLs = LASRead.LASSection('V')
        self.assertEqual('V', myLs.type)
        self.assertEqual([], myLs._members)
        myLs.addMemberLine(2, ' VERS.                        3.0: CWLS LOG ASCII STANDARD - VERSION 2.0\n')
        myLs.addMemberLine(3, ' WRAP.                         NO: ONE LINE PER DEPTH STEP\n')
        try:
            myLs.finalise()
            self.fail('LASRead.ExceptionLASReadSection not raised')
        except LASRead.ExceptionLASReadSection:
            pass

    def test_07(self):
        """TestLASReadLASSection.test_07(): Adding member lines to 'V' section in right order, wrong values: WHAT."""
        myLs = LASRead.LASSection('V')
        self.assertEqual('V', myLs.type)
        self.assertEqual([], myLs._members)
        myLs.addMemberLine(2, ' VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0\n')
        myLs.addMemberLine(3, ' WRAP.                       WHAT: ONE LINE PER DEPTH STEP\n')
        try:
            myLs.finalise()
            self.fail('LASRead.ExceptionLASReadSection not raised')
        except LASRead.ExceptionLASReadSection:
            pass

    def test_10(self):
        """TestLASReadLASSection.test_10(): Adding member lines to 'O' section."""
        myLs = LASRead.LASSection('O')
        self.assertEqual('O', myLs.type)
        self.assertEqual([], myLs._members)
        myLs.addMemberLine(1, 'Line 1\n')
        myLs.addMemberLine(2, 'Line 2\n')
        self.assertEqual(
            [
                'Line 1',
                'Line 2',
            ],
            myLs._members
        )

class TestLASReadLASSectionArray(unittest.TestCase):
    """Tests reading an array section."""
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """TestLASReadLASSectionArray.test_00(): Tests setUp() and tearDown()."""
        pass
    
    def _retSimpleCurveSection(self):
        myLsC = LASRead.LASSection('C')
        myStr = """ DEPT.F                          : 
 GR  .GAPI           45 310 01 00: 
 DPHI.V/V            45 890 00 00: 
 NPHI.V/V            42 890 00 00: 
 ILD .OHMM           05 120 00 00: 
"""
        for i, l in enumerate(myStr.split('\n')):
            myLsC.addMemberLine(i, l)
        myLsC.finalise()
        self.assertEqual(5, len(myLsC))
        return myLsC
    
    def test_01(self):
        """TestLASReadLASSectionArray.test_01(): Constructor."""
        myLsC = self._retSimpleCurveSection()
        myLsA = LASRead.LASSectionArray('A', False, myLsC)
        myLsA.finalise()
        self.assertEqual('A', myLsA.type)
        self.assertEqual([], myLsA._members)
        self.assertFalse(myLsA._wrap)
        self.assertEqual(
            [
                ('DEPT', 'F'),
                ('GR', 'GAPI'),
                ('DPHI', 'V/V'),
                ('NPHI', 'V/V'),
                ('ILD', 'OHMM'),
            ],
            myLsA._mnemUnitS,
        )
        
    def test_02(self):
        """TestLASReadLASSectionArray.test_02(): Populate with array, no wrap."""
        myLsC = self._retSimpleCurveSection()
        myLsA = LASRead.LASSectionArray('A', False, myLsC)
        myStr = """ 1700.0000  -999.2500  -999.2500  -999.2500  -999.2500
 1700.5000    40.7909     0.0218     0.0417    25.9985
 1701.0000    44.0165     0.0347     0.0333    26.1850
 1701.5000    45.4578     0.0506     0.0272    25.7472
 1702.0000    44.3055     0.0527     0.0213    23.8872
 1702.5000    42.6896     0.0443     0.0167    20.8817
 1703.0000    52.4264     0.0290     0.0229    17.8425
 1703.5000    61.1144     0.0199     0.0383    13.2042
"""
        for i, l in enumerate(myStr.split('\n')):
            myLsA.addMemberLine(i, l)
        myLsA.finalise()
        self.assertEqual('A', myLsA.type)
#        print()
#        pprint.pprint(myLsA._members)
        exp = [
            [1700.0, -999.25, -999.25, -999.25, -999.25],
            [1700.5, 40.7909, 0.0218, 0.0417, 25.9985],
            [1701.0, 44.0165, 0.0347, 0.0333, 26.185],
            [1701.5, 45.4578, 0.0506, 0.0272, 25.7472],
            [1702.0, 44.3055, 0.0527, 0.0213, 23.8872],
            [1702.5, 42.6896, 0.0443, 0.0167, 20.8817],
            [1703.0, 52.4264, 0.029, 0.0229, 17.8425],
            [1703.5, 61.1144, 0.0199, 0.0383, 13.2042],
        ]
        self.assertEqual(exp, myLsA._members)
#        print()
#        print(list(myLsA.keys()))
        self.assertEqual(
            [1700.0, 1700.5, 1701.0, 1701.5, 1702.0, 1702.5, 1703.0, 1703.5],
            sorted(list(myLsA.keys())),
        )
        
    def test_03(self):
        """TestLASReadLASSectionArray.test_03(): Populate with array, with wrap +1 line."""
        myLsC = self._retSimpleCurveSection()
        myLsA = LASRead.LASSectionArray('A', True, myLsC)
        myStr = """ 1700.0000
 -999.2500  -999.2500  -999.2500  -999.2500
 1700.5000
 40.7909     0.0218     0.0417    25.9985
 1701.0000
 44.0165     0.0347     0.0333    26.1850
 1701.5000
 45.4578     0.0506     0.0272    25.7472
 1702.0000
 44.3055     0.0527     0.0213    23.8872
 1702.5000
 42.6896     0.0443     0.0167    20.8817
 1703.0000
 52.4264     0.0290     0.0229    17.8425
 1703.5000
 61.1144     0.0199     0.0383    13.2042
"""
        for i, l in enumerate(myStr.split('\n')):
            myLsA.addMemberLine(i, l)
        myLsA.finalise()
        self.assertEqual('A', myLsA.type)
#        print()
#        pprint.pprint(myLsA._members)
        exp = [
            [1700.0, -999.25, -999.25, -999.25, -999.25],
            [1700.5, 40.7909, 0.0218, 0.0417, 25.9985],
            [1701.0, 44.0165, 0.0347, 0.0333, 26.185],
            [1701.5, 45.4578, 0.0506, 0.0272, 25.7472],
            [1702.0, 44.3055, 0.0527, 0.0213, 23.8872],
            [1702.5, 42.6896, 0.0443, 0.0167, 20.8817],
            [1703.0, 52.4264, 0.029, 0.0229, 17.8425],
            [1703.5, 61.1144, 0.0199, 0.0383, 13.2042],
        ]
        self.assertEqual(exp, myLsA._members)
#        print()
#        print(list(myLsA.keys()))
        self.assertEqual(
            [1700.0, 1700.5, 1701.0, 1701.5, 1702.0, 1702.5, 1703.0, 1703.5],
            sorted(list(myLsA.keys())),
        )
        
    def test_04(self):
        """TestLASReadLASSectionArray.test_04(): Populate with array, with wrap +2 line."""
        myLsC = self._retSimpleCurveSection()
        myLsA = LASRead.LASSectionArray('A', True, myLsC)
        myStr = """ 1700.0000
 -999.2500  -999.2500
 -999.2500  -999.2500
 1700.5000
 40.7909     0.0218
 0.0417    25.9985
 1701.0000
 44.0165     0.0347
 0.0333    26.1850
 1701.5000
 45.4578     0.0506
 0.0272    25.7472
 1702.0000
 44.3055     0.0527
 0.0213    23.8872
 1702.5000
 42.6896     0.0443
 0.0167    20.8817
 1703.0000
 52.4264     0.0290
 0.0229    17.8425
 1703.5000
 61.1144     0.0199
 0.0383    13.2042
"""
        for i, l in enumerate(myStr.split('\n')):
            myLsA.addMemberLine(i, l)
        myLsA.finalise()
        self.assertEqual('A', myLsA.type)
#        print()
#        pprint.pprint(myLsA._members)
        exp = [
            [1700.0, -999.25, -999.25, -999.25, -999.25],
            [1700.5, 40.7909, 0.0218, 0.0417, 25.9985],
            [1701.0, 44.0165, 0.0347, 0.0333, 26.185],
            [1701.5, 45.4578, 0.0506, 0.0272, 25.7472],
            [1702.0, 44.3055, 0.0527, 0.0213, 23.8872],
            [1702.5, 42.6896, 0.0443, 0.0167, 20.8817],
            [1703.0, 52.4264, 0.029, 0.0229, 17.8425],
            [1703.5, 61.1144, 0.0199, 0.0383, 13.2042],
        ]
        self.assertEqual(exp, myLsA._members)
#        print()
#        print(list(myLsA.keys()))
        self.assertEqual(
            [1700.0, 1700.5, 1701.0, 1701.5, 1702.0, 1702.5, 1703.0, 1703.5],
            sorted(list(myLsA.keys())),
        )
        
    def test_05(self):
        """TestLASReadLASSectionArray.test_05(): Convert unreadable floats to NULL."""
        myLsC = self._retSimpleCurveSection()
        myLsA = LASRead.LASSectionArray('A', False, myLsC)
        myStr = """ 1700.0000  -999.2500  -999.2500  -999.2500  -999.2500
 1700.5000    40.7909     0.0218     0.0417    25.9985
 1701.0000    44.0165     ******     0.0333    26.1850
 1701.5000    45.4578     0.0506     0.0272    25.7472
 1702.0000    44.3055     xxxxxx     0.0213    23.8872
 1702.5000    42.6896     0.0443     0.0167    20.8817
 1703.0000    52.4264     0.0290     0.0229    17.8425
 1703.5000    61.1144     0.0199     0.0383    13.2042
"""
        for i, l in enumerate(myStr.split('\n')):
            myLsA.addMemberLine(i, l)
        myLsA.finalise()
        self.assertEqual('A', myLsA.type)
#        print()
#        pprint.pprint(myLsA._members)
        exp = [
            [1700.0, -999.25, -999.25, -999.25, -999.25],
            [1700.5, 40.7909, 0.0218, 0.0417, 25.9985],
            [1701.0, 44.0165, -999.25, 0.0333, 26.185],
            [1701.5, 45.4578, 0.0506, 0.0272, 25.7472],
            [1702.0, 44.3055, -999.25, 0.0213, 23.8872],
            [1702.5, 42.6896, 0.0443, 0.0167, 20.8817],
            [1703.0, 52.4264, 0.029, 0.0229, 17.8425],
            [1703.5, 61.1144, 0.0199, 0.0383, 13.2042],
        ]
        self.assertEqual(exp, myLsA._members)
#        print()
#        print(list(myLsA.keys()))
        self.assertEqual(
            [1700.0, 1700.5, 1701.0, 1701.5, 1702.0, 1702.5, 1703.0, 1703.5],
            sorted(list(myLsA.keys())),
        )

## Removed as we now support wrap when there is a single channel
#    def test_10(self):
#        """TestLASReadLASSectionArray.test_01(): Constructor."""
#        myLsC = LASRead.LASSection('C')
#        myStr = """ DEPT.F                          : 
# GR  .GAPI           45 310 01 00: 
#"""
#        for i, l in enumerate(myStr.split('\n')):
#            myLsC.addMemberLine(i, l)
#        myLsC.finalise()
#        self.assertEqual(2, len(myLsC))
#        try:
#            LASRead.LASSectionArray('A', True, myLsC)
#            self.fail('LASRead.ExceptionLASReadSectionArray not raised.')
#        except LASRead.ExceptionLASReadSectionArray:
#            pass            
        
    def test_11(self):
        """TestLASReadLASSectionArray.test_11(): Populate with array, with wrap +1 line OK when only one value."""
        myLsC = self._retSimpleCurveSection()
        myLsA = LASRead.LASSectionArray('A', True, myLsC)
        myStr = """ 1700.0000
 -999.2500 
 -999.2500  -999.2500  -999.2500
"""
#        try:
#            for i, l in enumerate(myStr.split('\n')):
#                myLsA.addMemberLine(i, l)
#            myLsA.finalise()
#            self.fail('LASRead.ExceptionLASReadSectionArray not raised.')
#        except LASRead.ExceptionLASReadSectionArray:
#            pass
        for i, l in enumerate(myStr.split('\n')):
            myLsA.addMemberLine(i, l)
        myLsA.finalise()
        self.assertEqual([[1700.0, -999.25, -999.25, -999.25, -999.25]], myLsA._members)
        
    def test_12(self):
        """TestLASReadLASSectionArray.test_12(): Populate with array, with wrap +1 fails when missing one value, single line."""
        myLsC = self._retSimpleCurveSection()
        myLsA = LASRead.LASSectionArray('A', True, myLsC)
        myStr = """ 1700.0000
 -999.2500  -999.2500  -999.2500  
"""
        try:
            for i, l in enumerate(myStr.split('\n')):
                myLsA.addMemberLine(i, l)
            myLsA.finalise()
            self.fail('LASRead.ExceptionLASReadSectionArray not raised.')
        except LASRead.ExceptionLASReadSectionArray:
            pass
#        print()
#        pprint.pprint(myLsA._members)
        self.assertEqual([], myLsA._members)
        
    def test_13(self):
        """TestLASReadLASSectionArray.test_13(): Populate with array, with wrap +1 fails when missing one value at EOF, multi line."""
        myLsC = self._retSimpleCurveSection()
        self.assertEqual(5, len(myLsC))
        myLsA = LASRead.LASSectionArray('A', True, myLsC)
        myStr = """ 1700.0000
 -999.2500  -999.2500  -999.2500  -999.2500  
 1700.5000
 40.7909     0.0218     0.0417
"""
        try:
            for i, l in enumerate(myStr.split('\n')):
                myLsA.addMemberLine(i, l)
            myLsA.finalise()
            self.fail('LASRead.ExceptionLASReadSectionArray not raised.')
        except LASRead.ExceptionLASReadSectionArray:
            pass
#        print()
#        pprint.pprint(myLsA._members)
        self.assertEqual([[1700.0, -999.25, -999.25, -999.25, -999.25]], myLsA._members)
        
    def test_14(self):
        """TestLASReadLASSectionArray.test_14(): Populate with array, with wrap +1 fails when missing one value in middle, multi line."""
        myLsC = self._retSimpleCurveSection()
        self.assertEqual(5, len(myLsC))
        myLsA = LASRead.LASSectionArray('A', True, myLsC)
        myStr = """ 1700.0000
 -999.2500  -999.2500  -999.2500  
 1700.5000
 40.7909     0.0218     0.0417    25.9985
"""
        try:
            for i, l in enumerate(myStr.split('\n')):
                myLsA.addMemberLine(i, l)
            myLsA.finalise()
            self.fail('LASRead.ExceptionLASReadSectionArray not raised.')
        except LASRead.ExceptionLASReadSectionArray:
            pass
#        print()
#        pprint.pprint(myLsA._members)
        self.assertEqual([[1700.0, -999.25, -999.25, -999.25, 1700.5]], myLsA._members)
        
    def test_15(self):
        """TestLASReadLASSectionArray.test_15(): Populate with array, with wrap +1 fails when too many values, multi line."""
        myLsC = self._retSimpleCurveSection()
        self.assertEqual(5, len(myLsC))
        myLsA = LASRead.LASSectionArray('A', True, myLsC)
        myStr = """ 1700.0000
 -999.2500  -999.2500  -999.2500  -999.2500  -999.2500  
"""
        try:
            for i, l in enumerate(myStr.split('\n')):
                myLsA.addMemberLine(i, l)
            myLsA.finalise()
            self.fail('LASRead.ExceptionLASReadSectionArray not raised.')
        except LASRead.ExceptionLASReadSectionArray:
            pass
#        print()
#        pprint.pprint(myLsA._members)
        self.assertEqual([], myLsA._members)
        
class TestLASRead(unittest.TestCase):
    """Tests high level functionality of the LASRead module."""
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """TestLASRead.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestLASRead.test_01(): Tests file with comment and blank lines and single version section."""
        myFi = io.StringIO("""
# Some comment
# Another comment
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP

""")
        myLf = LASRead.LASRead(myFi, 'MyID')
        self.assertEqual(1, len(myLf))

    def test_02(self):
        """TestLASRead.test_02(): Tests file with version and well section."""
        myFi = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 1700.0000: START DEPTH
 STOP.F                 3700.0000: STOP DEPTH
 STEP.F                    0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
#        print([str(s) for s in myLf._sects])
        self.assertEqual(2, len(myLf))

    def test_03(self):
        """TestLASRead.test_03(): Tests file with version and well section. logDown()."""
        myFi = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 1700.0000: START DEPTH
 STOP.F                 3700.0000: STOP DEPTH
 STEP.F                    0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
#        print([str(s) for s in myLf._sects])
        self.assertEqual(2, len(myLf))
        self.assertTrue(myLf.logDown())

    def test_04(self):
        """TestLASRead.test_04(): Tests file with version and well section. not logDown()."""
        myFi = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 3700.0000: START DEPTH
 STOP.F                 1700.0000: STOP DEPTH
 STEP.F                   -0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
#        print([str(s) for s in myLf._sects])
        self.assertEqual(2, len(myLf))
        self.assertFalse(myLf.logDown())

    def test_05_00(self):
        """TestLASRead.test_05_00(): Tests file with version and well section. NULL value specified."""
        myFi = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 3700.0000: START DEPTH
 STOP.F                 1700.0000: STOP DEPTH
 STEP.F                   -0.5000: STEP LENGTH
 NULL.                    -9.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
        self.assertEqual(2, len(myLf))
        self.assertEqual(-9.25, myLf.nullValue)

    def test_05_01(self):
        """TestLASRead.test_05_01(): Tests file with version and well section. NULL value default."""
        myFi = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 3700.0000: START DEPTH
 STOP.F                 1700.0000: STOP DEPTH
 STEP.F                   -0.5000: STEP LENGTH
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
        self.assertEqual(2, len(myLf))
        self.assertEqual(-999.25, myLf.nullValue)

    def test_06_00(self):
        """TestLASRead.test_06_00(): Tests file with version and well section. X axis units recognised as LIS ones."""
        myFi = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.FT                3700.0000: START DEPTH
 STOP.F                 1700.0000: STOP DEPTH
 STEP.F                   -0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
#        print([str(s) for s in myLf._sects])
        self.assertEqual(2, len(myLf))
        self.assertEqual(b'FT  ', myLf.xAxisUnits)

    def test_06_01(self):
        """TestLASRead.test_06_01(): Tests file with version and well section. X axis units not recognised as LIS ones but converted."""
        myFi = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 3700.0000: START DEPTH
 STOP.F                 1700.0000: STOP DEPTH
 STEP.F                   -0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
#        print([str(s) for s in myLf._sects])
        self.assertEqual(2, len(myLf))
        self.assertEqual(b'FEET', myLf.xAxisUnits)

    def test_06_02(self):
        """TestLASRead.test_06_02(): Tests file with version and well section. X axis units missing."""
        myFi = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STOP.F                 1700.0000: STOP DEPTH
 STEP.F                   -0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
#        print([str(s) for s in myLf._sects])
        self.assertEqual(2, len(myLf))
        try:
            myLf.xAxisUnits
            self.fail('LASRead.ExceptionLASReadData not raised')
        except LASRead.ExceptionLASReadData:
            pass

    def test_06_03(self):
        """TestLASRead.test_06_03(): Tests file with version and well section. X axis units STRT/STOP/STEP."""
        myFi = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 3700.0000: START DEPTH
 STOP.F                 1700.0000: STOP DEPTH
 STEP.F                   -0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
#        print([str(s) for s in myLf._sects])
        self.assertEqual(2, len(myLf))
        self.assertEqual(EngVal.EngVal(3700.0, b'FEET'), myLf.xAxisStart)
        self.assertEqual(EngVal.EngVal(1700.0, b'FEET'), myLf.xAxisStop)
        self.assertEqual(EngVal.EngVal(-0.5, b'FEET'), myLf.xAxisStep)

    def test_10(self):
        """TestLASRead.test_10(): Tests file with all sections except A section."""
        myFi = io.StringIO("""~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 1700.0000: START DEPTH
 STOP.F                 3700.0000: STOP DEPTH
 STEP.F                    0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
~CURVE INFORMATION
 DEPT.F                          : 
 GR  .GAPI           45 310 01 00: 
 DPHI.V/V            45 890 00 00: 
 NPHI.V/V            42 890 00 00: 
 ILD .OHMM           05 120 00 00: 
~Parameter Information
 EKB .F                 1206.0000: Kelly bushing
 TD  .F                 3747.0000: Total depth
 FL  .            990 FSL 990 FWL: FIELD LOCATION
 EGL .F                      1200: Elevation of ground leve
 DATE.                     111982: Date Logged
 RUN .                          1: Run number
 WSS .                   FLOWLINE: Source of sample
 RM  .OHMM                   2.56: Rm
 EMT .DEGF                     62: Meas. temp.
 RMF .OHMM                   1.91: Rmf
 MFT .DEGF                     68: Meas. temp.
 RMC .OHMM                   3.84: Rmc
 MCST.DEGF                     62: Meas. temp.
 RMB .OHMM                   1.56: Rm. at BHT
 BHT .DEGF                    102: BHT.
~O
Other stuff, whatever....
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
#        print()
#        print('\n'.join([str(s) for s in myLf._sects]))
        self.assertEqual(5, len(myLf))
        self.assertEqual(0, myLf.numFrames())
        self.assertEqual(0, myLf.numDataPoints())

    def test_11(self):
        """TestLASRead.test_11(): Tests file with all sections with A section."""
        myFi = io.StringIO("""~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 1700.0000: START DEPTH
 STOP.F                 3700.0000: STOP DEPTH
 STEP.F                    0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
~CURVE INFORMATION
 DEPT.F                          : 
 GR  .GAPI           45 310 01 00: 
 DPHI.V/V            45 890 00 00: 
 NPHI.V/V            42 890 00 00: 
 ILD .OHMM           05 120 00 00: 
~Parameter Information
 EKB .F                 1206.0000: Kelly bushing
 TD  .F                 3747.0000: Total depth
 FL  .            990 FSL 990 FWL: FIELD LOCATION
 EGL .F                      1200: Elevation of ground leve
 DATE.                     111982: Date Logged
 RUN .                          1: Run number
 WSS .                   FLOWLINE: Source of sample
 RM  .OHMM                   2.56: Rm
 EMT .DEGF                     62: Meas. temp.
 RMF .OHMM                   1.91: Rmf
 MFT .DEGF                     68: Meas. temp.
 RMC .OHMM                   3.84: Rmc
 MCST.DEGF                     62: Meas. temp.
 RMB .OHMM                   1.56: Rm. at BHT
 BHT .DEGF                    102: BHT.
~O
Other stuff, whatever....
~A
 1700.0000  -999.2500  -999.2500  -999.2500  -999.2500
 1700.5000    40.7909     0.0218     0.0417    25.9985
 1701.0000    44.0165     0.0347     0.0333    26.1850
 1701.5000    45.4578     0.0506     0.0272    25.7472
 1702.0000    44.3055     0.0527     0.0213    23.8872
 1702.5000    42.6896     0.0443     0.0167    20.8817
 1703.0000    52.4264     0.0290     0.0229    17.8425
 1703.5000    61.1144     0.0199     0.0383    13.2042
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
#        print()
#        print('\n'.join([str(s) for s in myLf._sects]))
        self.assertEqual(6, len(myLf))
        self.assertEqual(8, myLf.numFrames())
        self.assertEqual(8*5, myLf.numDataPoints())

    def test_12(self):
        """TestLASRead.test_12(): Tests file with W and P section and Mnemonic access."""
        myFi = io.StringIO("""~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 1700.0000: START DEPTH
 STOP.F                 3700.0000: STOP DEPTH
 STEP.F                    0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
~Parameter Information
 EKB .F                 1206.0000: Kelly bushing
 TD  .F                 3747.0000: Total depth
 FL  .            990 FSL 990 FWL: FIELD LOCATION
 EGL .F                      1200: Elevation of ground leve
 DATE.                     111982: Date Logged
 RUN .                          1: Run number
 WSS .                   FLOWLINE: Source of sample
 RM  .OHMM                   2.56: Rm
 EMT .DEGF                     62: Meas. temp.
 RMF .OHMM                   1.91: Rmf
 MFT .DEGF                     68: Meas. temp.
 RMC .OHMM                   3.84: Rmc
 MCST.DEGF                     62: Meas. temp.
 RMB .OHMM                   1.56: Rm. at BHT
 BHT .DEGF                    102: BHT.
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
#        print()
#        print('\n'.join([str(s) for s in myLf._sects]))
        self.assertEqual(3, len(myLf))
        self.assertEqual(0, myLf.numFrames())
        self.assertEqual(0, myLf.numDataPoints())
        self.assertEqual((2.56, 'OHMM'), myLf.getWsdMnem('RM'))
        self.assertEqual((None, None), myLf.getWsdMnem('UNKNOWN'))
#        print()
#        print(sorted(myLf.getAllWsdMnemonics()))
        self.assertEqual(
            [
                'API', 'BHT', 'COMP', 'COUN', 'DATE', 'EGL', 'EKB',
                'EMT', 'FL', 'FLD', 'LEAS', 'LOC', 'MCST', 'MFT', 'NULL',
                'PM', 'RANG', 'RM', 'RMB', 'RMC', 'RMF', 'RUN', 'SECT',
                'SRVC', 'STAT', 'STEP', 'STOP', 'STRT', 'TD', 'TOWN', 'UWI',
                'WELL', 'WSS'],
            sorted(myLf.getAllWsdMnemonics()),
        )

    def test_13(self):
        """TestLASRead.test_13(): Tests file with all sections with A section and genOutpPoints()."""
        myFi = io.StringIO("""~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 1700.0000: START DEPTH
 STOP.F                 3700.0000: STOP DEPTH
 STEP.F                    0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
~CURVE INFORMATION
 DEPT.F                          : 
 GR  .GAPI           45 310 01 00: 
 DPHI.V/V            45 890 00 00: 
 NPHI.V/V            42 890 00 00: 
 ILD .OHMM           05 120 00 00: 
~Parameter Information
 EKB .F                 1206.0000: Kelly bushing
 TD  .F                 3747.0000: Total depth
 FL  .            990 FSL 990 FWL: FIELD LOCATION
 EGL .F                      1200: Elevation of ground leve
 DATE.                     111982: Date Logged
 RUN .                          1: Run number
 WSS .                   FLOWLINE: Source of sample
 RM  .OHMM                   2.56: Rm
 EMT .DEGF                     62: Meas. temp.
 RMF .OHMM                   1.91: Rmf
 MFT .DEGF                     68: Meas. temp.
 RMC .OHMM                   3.84: Rmc
 MCST.DEGF                     62: Meas. temp.
 RMB .OHMM                   1.56: Rm. at BHT
 BHT .DEGF                    102: BHT.
~O
Other stuff, whatever....
~A  DEPT        GR        DPHI       NPHI      ILD
 1700.0000  -999.2500  -999.2500  -999.2500  -999.2500
 1700.5000    40.7909     0.0218     0.0417    25.9985
 1701.0000    44.0165     0.0347     0.0333    26.1850
 1701.5000    45.4578     0.0506     0.0272    25.7472
 1702.0000    44.3055     0.0527     0.0213    23.8872
 1702.5000    42.6896     0.0443     0.0167    20.8817
 1703.0000    52.4264     0.0290     0.0229    17.8425
 1703.5000    61.1144     0.0199     0.0383    13.2042
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
        self.assertEqual(6, len(myLf))
        self.assertEqual(8, myLf.numFrames())
        self.assertEqual(8*5, myLf.numDataPoints())
        self.assertEqual(
            [
                (1700.0, -999.25),
                (1700.5, 40.7909),
                (1701.0, 44.0165),
                (1701.5, 45.4578),
                (1702.0, 44.3055),
                (1702.5, 42.6896),
                (1703.0, 52.4264),
                (1703.5, 61.1144),
            ],
            list(myLf.genOutpPoints(Mnem.Mnem('GR'))),
        )
#        print()
#        pprint.pprint(list(myLf.genOutpPoints(Mnem.Mnem('DPHI'))))
        self.assertEqual(
            [
                (1700.0, -999.25),
                (1700.5, 0.0218),
                (1701.0, 0.0347),
                (1701.5, 0.0506),
                (1702.0, 0.0527),
                (1702.5, 0.0443),
                (1703.0, 0.029),
                (1703.5, 0.0199),
            ],
            list(myLf.genOutpPoints(Mnem.Mnem('DPHI'))),
        )
#        print()
#        pprint.pprint(list(myLf.genOutpPoints(Mnem.Mnem('NPHI'))))
        self.assertEqual(
            [
                (1700.0, -999.25),
                (1700.5, 0.0417),
                (1701.0, 0.0333),
                (1701.5, 0.0272),
                (1702.0, 0.0213),
                (1702.5, 0.0167),
                (1703.0, 0.0229),
                (1703.5, 0.0383),
            ],
            list(myLf.genOutpPoints(Mnem.Mnem('NPHI'))),
        )
#        print()
#        pprint.pprint(list(myLf.genOutpPoints(Mnem.Mnem('ILD'))))
        self.assertEqual(
            [
                (1700.0, -999.25),
                (1700.5, 25.9985),
                (1701.0, 26.185),
                (1701.5, 25.7472),
                (1702.0, 23.8872),
                (1702.5, 20.8817),
                (1703.0, 17.8425),
                (1703.5, 13.2042),
            ],
            list(myLf.genOutpPoints(Mnem.Mnem('ILD'))),
        )

    def test_20(self):
        """TestLASRead.test_20(): Tests fail with duplicate well information section."""
        myFi = io.StringIO("""
# Some comment
# Another comment
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 1700.0000: START DEPTH
 STOP.F                 3700.0000: STOP DEPTH
 STEP.F                    0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 1700.0000: START DEPTH
 STOP.F                 3700.0000: STOP DEPTH
 STEP.F                    0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
""")
        try:
            LASRead.LASRead(myFi, 'MyID')
            self.fail('LASRead.ExceptionLASRead not raised.')
        except LASRead.ExceptionLASRead:
            pass

    def test_21(self):
        """TestLASRead.test_21(): Tests warn with unknown section type."""
        myFi = io.StringIO("""
# Some comment
# Another comment
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~Z
 UWI .               15-131-20047: Unique Well Id
~O
 Other section...
""")
        myLr = LASRead.LASRead(myFi, 'MyID')
#        try:
#            LASRead.LASRead(myFi, 'MyID')
#            self.fail('LASRead.ExceptionLASRead not raised.')
#        except LASRead.ExceptionLASRead:
#            pass
        self.assertEqual(2, len(myLr))
#        print([s for s in myLr.genSects()])
        l = [s for s in myLr.genSects()]
        self.assertEqual(2, len(l))
        self.assertEqual('V', l[0].type)
        self.assertEqual('O', l[1].type)

    def test_22(self):
        """TestLASRead.test_22(): Tests fail with version section not first section."""
        myFi = io.StringIO("""
# Some comment
# Another comment
~W
 UWI .               15-131-20047: Unique Well Id
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
""")
#        LASRead.LASRead(myFi, 'MyID')
        try:
            LASRead.LASRead(myFi, 'MyID')
            self.fail('LASRead.ExceptionLASRead not raised.')
        except LASRead.ExceptionLASRead:
            pass

    def test_23(self):
        """TestLASRead.test_23(): Tests fail with duplicate version section."""
        myFi = io.StringIO("""
# Some comment
# Another comment
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
""")
#        LASRead.LASRead(myFi, 'MyID')
        try:
            LASRead.LASRead(myFi, 'MyID')
            self.fail('LASRead.ExceptionLASRead not raised.')
        except LASRead.ExceptionLASRead:
            pass

    def test_24(self):
        """TestLASRead.test_24(): Tests fail with array section as first section."""
        myFi = io.StringIO("""
# Some comment
# Another comment
~A
 1700.0000  -999.2500  -999.2500  -999.2500  -999.2500
 1700.5000    40.7909     0.0218     0.0417    25.9985
 1701.0000    44.0165     0.0347     0.0333    26.1850
 1701.5000    45.4578     0.0506     0.0272    25.7472
 1702.0000    44.3055     0.0527     0.0213    23.8872
 1702.5000    42.6896     0.0443     0.0167    20.8817
 1703.0000    52.4264     0.0290     0.0229    17.8425
 1703.5000    61.1144     0.0199     0.0383    13.2042
""")
#        LASRead.LASRead(myFi, 'MyID')
        try:
            LASRead.LASRead(myFi, 'MyID')
            self.fail('LASRead.ExceptionLASRead not raised.')
        except LASRead.ExceptionLASRead:
            pass

    def test_25(self):
        """TestLASRead.test_25(): Tests fail with array section with no curve section."""
        myFi = io.StringIO("""
# Some comment
# Another comment
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~A
 1700.0000  -999.2500  -999.2500  -999.2500  -999.2500
 1700.5000    40.7909     0.0218     0.0417    25.9985
 1701.0000    44.0165     0.0347     0.0333    26.1850
 1701.5000    45.4578     0.0506     0.0272    25.7472
 1702.0000    44.3055     0.0527     0.0213    23.8872
 1702.5000    42.6896     0.0443     0.0167    20.8817
 1703.0000    52.4264     0.0290     0.0229    17.8425
 1703.5000    61.1144     0.0199     0.0383    13.2042
""")
#        LASRead.LASRead(myFi, 'MyID')
        try:
            LASRead.LASRead(myFi, 'MyID')
            self.fail('LASRead.ExceptionLASRead not raised.')
        except LASRead.ExceptionLASRead:
            pass

    def test_26(self):
        """TestLASRead.test_26(): Tests fail when a section follows an array section."""
        myFi = io.StringIO("""
# Some comment
# Another comment
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~CURVE INFORMATION
 DEPT.F                          : 
 GR  .GAPI           45 310 01 00: 
~A
 1700.0000  -999.2500
 1700.5000    40.7909
 1701.0000    44.0165
 1701.5000    45.4578
 1702.0000    44.3055
 1702.5000    42.6896
 1703.0000    52.4264
 1703.5000    61.1144
~O
Some other stuff that shouldn't be here.
""")
#        LASRead.LASRead(myFi, 'MyID')
        try:
            LASRead.LASRead(myFi, 'MyID')
            self.fail('LASRead.ExceptionLASRead not raised.')
        except LASRead.ExceptionLASRead:
            pass

    def test_27(self):
        """TestLASRead.test_27(): Tests fail when hasOutpMnem() when no curve section."""
        myFi = io.StringIO("""
# Some comment
# Another comment
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
""")
        myFi = LASRead.LASRead(myFi, 'MyID')
        self.assertFalse(myFi.hasOutpMnem(Mnem.Mnem('GR')))
        self.assertEqual([], myFi.curveMnems())

    def test_30(self):
        """TestLASRead.test_30(): Tests file with all sections except A section. Testing Curve section."""
        myFi = io.StringIO("""~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 1700.0000: START DEPTH
 STOP.F                 3700.0000: STOP DEPTH
 STEP.F                    0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
~CURVE INFORMATION
 DEPT.F                          : 
 GR  .GAPI           45 310 01 00: 
 DPHI.V/V            45 890 00 00: 
 NPHI.V/V            42 890 00 00: 
 ILD .OHMM           05 120 00 00: 
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
#        print()
#        print('\n'.join([str(s) for s in myLf._sects]))
        self.assertEqual(3, len(myLf))
        self.assertEqual(0, myLf.numFrames())
        self.assertEqual(0, myLf.numDataPoints())        
#        print()
#        print(sorted(myLf.curveMnems()))
        self.assertEqual(
            ['DEPT', 'DPHI', 'GR', 'ILD', 'NPHI'],
            sorted(myLf.curveMnems()),
        )
        self.assertEqual(
            ['DEPT', 'GR', 'DPHI', 'NPHI', 'ILD',],
            myLf.curveMnems(ordered=True),
        )

    def test_31(self):
        """TestLASRead.test_31(): Tests file with all sections except A section. Testing Curve section hasOutpMnem()."""
        myFi = io.StringIO("""~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 1700.0000: START DEPTH
 STOP.F                 3700.0000: STOP DEPTH
 STEP.F                    0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
~CURVE INFORMATION
 DEPT.F                          : 
 GR  .GAPI           45 310 01 00: 
 DPHI.V/V            45 890 00 00: 
 NPHI.V/V            42 890 00 00: 
 ILD .OHMM           05 120 00 00: 
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
        self.assertEqual(3, len(myLf))
        self.assertEqual(0, myLf.numFrames())
        self.assertEqual(0, myLf.numDataPoints())        
#        print()
#        print(sorted(myLf.curveMnems()))
        expMnemS = ['DEPT', 'DPHI', 'GR', 'ILD', 'NPHI']
        self.assertEqual(expMnemS, sorted(myLf.curveMnems()))
        for m in expMnemS:
            self.assertTrue(myLf.hasOutpMnem(Mnem.Mnem(m)))
        self.assertFalse(myLf.hasOutpMnem(Mnem.Mnem('WTF')))

    def test_32(self):
        """TestLASRead.test_32(): Tests file with all sections except A section. Testing Curve section curveUnitsAsStr()."""
        myFi = io.StringIO("""~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 1700.0000: START DEPTH
 STOP.F                 3700.0000: STOP DEPTH
 STEP.F                    0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
~CURVE INFORMATION
 DEPT.F                          : 
 GR  .GAPI           45 310 01 00: 
 DPHI.V/V            45 890 00 00: 
 NPHI.V/V            42 890 00 00: 
 ILD .OHMM           05 120 00 00: 
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
        self.assertEqual(3, len(myLf))
        self.assertEqual(0, myLf.numFrames())
        self.assertEqual(0, myLf.numDataPoints())        
#        print()
#        print(sorted(myLf.curveMnems()))
        expUnitS = [b'FEET', b'GAPI', b'V/V ', b'V/V ', b'OHMM']
        self.assertEqual(
            expUnitS,
            [myLf.curveUnitsAsStr(Mnem.Mnem(m)) for m in myLf.curveMnems(ordered=True)],
        )

    def test_33(self):
        """TestLASRead.test_33(): Tests file with all sections except A section. Testing Curve section curveUnitsAsStr() where regex finds None."""
        myFi = io.StringIO("""~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION 
 STRT.F                   1700.0000: START DEPTH
 STOP.F                   3700.0000: STOP DEPTH
 STEP.F                      0.5000: STEP LENGTH
 NULL.                    -999.2500: NO VALUE
 COMP.         ANY OIL COMPANY INC.: COMPANY
 WELL.        ANY ET AL A9-16-49-20: WELL
 LEAS.                HAVERKAMP 'A': Lease Name
 FLD .                         EDAM: FIELD
 LOC .               A9-16-49-20W3M: LOCATION
 PROV.                 SASKATCHEWAN: PROVINCE
 SRVC.     ANY LOGGING COMPANY INC.: SERVICE COMPANY
 DATE.                    13-DEC-86: LOG DATE
 UWI .             100091604920W300: UNIQUE WELL ID
 LAT .                     38.53915: Latitude North (KGS,LEO3.6)
 LON .                     98.95341: LONGITUDE WEST (KGS, LEO3.6)
 API .                 151812004700: UNIQUE WELL ID

~CURVE INFORMATION BLOCK
#MNEM.UNIT  API Codes         Curve Description
#---------  ------------      -----------------------------
 DPTH.FT                   00 001 00 01: DEPTH
 GRPD.API                              : PNS GAMMA RAY
 CAPD.IN                               : DENSITY CALIPER
 CAL .INCHES                           : MICRO-RES CALIPER
 MR1F.OHM-M                            : MICRO-INVERSE 1"
 MR2F.OHM-M                            : MICRO-NORMAL 2"
 PEDN.B/E                              : NEAR PE CURVE
 NPOR.: LIMEST. NEUTRON POROSITY
 DEN .G/CC                             : DENSITY
 DCOR.G/CC                             : DENSITY CORRECTION
 DPOR.: LIMESTONE DENSITY POROSITY
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
        self.assertEqual(3, len(myLf))
        self.assertEqual(0, myLf.numFrames())
        self.assertEqual(0, myLf.numDataPoints())
#        print()
#        print(myLf.curveMnems(ordered=True))
#        print([myLf.curveUnitsAsStr(Mnem.Mnem(m)) for m in myLf.curveMnems(ordered=True)])
        expUnitS = [b'FT  ', b'API ', b'IN  ', b'INCHES', b'OHM-M', b'OHM-M', b'B/E ', b'    ', b'G/CC', b'G/CC', b'    ']
        self.assertEqual(
            expUnitS,
            [myLf.curveUnitsAsStr(Mnem.Mnem(m)) for m in myLf.curveMnems(ordered=True)],
        )

    def test_34(self):
        """TestLASRead.test_34(): Tests file with all sections except A section. Testing Curve section with non-LIS mnemonics."""
        myFi = io.StringIO("""~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~WELL INFORMATION
 UWI .               15-131-20047: Unique Well Id
 PM  .                          6: Principal Meridian
 STAT.                     Kansas: State
 SECT.                         17: Section
 TOWN.                         4S: Township
 RANG.                        14E: Range
 COUN.                     NEMAHA: County Name
 COMP.     CITIES SERVICE COMPANY: Company
 WELL.                          1: Well Name
 LEAS.              HAVERKAMP 'A': Lease Name
 FLD .                       GOFF: Field
 STRT.F                 1700.0000: START DEPTH
 STOP.F                 3700.0000: STOP DEPTH
 STEP.F                    0.5000: STEP LENGTH
 NULL.                  -999.2500: NO VALUE
 LOC .         NE,SW,SW,17-4S-14E: LOCATION
 SRVC.                           : SERVICE COMPANY
 DATE.                   11/19/82: LOGDATE
 API .               151312004700: UNIQUE WELL ID
~CURVE INFORMATION
 DEPT.F                          : 
 GRDI.GAPI           ?? ??? ?? ??: 
 SFLU.OHMM           ?? ??? ?? ??: 
 TILT.DEG            ?? ??? ?? ??: 
 BIT .INCH           ?? ??? ?? ??: 
""")
        myLf = LASRead.LASRead(myFi, 'MyID')
        self.assertEqual(3, len(myLf))
        self.assertEqual(0, myLf.numFrames())
        self.assertEqual(0, myLf.numDataPoints())        
#        print()
#        print(sorted(myLf.curveMnems()))
        expMnemS = ['DEPT', 'GRDI', 'SFLU', 'TILT', 'BIT']
        self.assertEqual(expMnemS, myLf.curveMnems(ordered=True))
        for m in expMnemS:
            self.assertTrue(myLf.hasOutpMnem(Mnem.Mnem(m)))
        self.assertFalse(myLf.hasOutpMnem(Mnem.Mnem('WTF')))
        # Now test that it has LIS equivalents
        expMnemS = ['DEPT', 'GR', 'SFL', 'DEVI', 'BS']
        for m in expMnemS:
            self.assertTrue(myLf.hasOutpMnem(Mnem.Mnem(m)))
        self.assertFalse(myLf.hasOutpMnem(Mnem.Mnem('WTF')))        

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLASReadGenerator))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLASReadRegex))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLASReadLASFields))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLASReadLASSection))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLASReadLASSectionArray))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLASRead))
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
