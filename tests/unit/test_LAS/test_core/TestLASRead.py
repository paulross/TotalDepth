#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 1999-2020 Paul Ross
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
"""Tests LAS reader.

Created on Jan 11, 2012

@author: paulross
"""
import datetime
import io

import numpy as np

import pytest

from TotalDepth.LIS.core import EngVal
from TotalDepth.LAS.core import LASRead
from TotalDepth.LIS.core import Mnem

__author__ = 'Paul Ross'
__date__ = '2011-08-03'
__version__ = '0.2.0'
__rights__ = 'Copyright (c) 2012-2020 Paul Ross.'


@pytest.mark.parametrize(
    'path, expected',
    (
        ('foo.las', True),
        ('foo.lis', False),
    )
)
def test_has_las_extension(path, expected):
    assert LASRead.has_las_extension(path) == expected


def test_las_read_generator():
    """Tests simple file with comments, sections."""
    las_file = io.StringIO("""
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
    result = [v for v in LASRead.generate_lines(las_file)]
    expected = [
        (5,  '~VERSION INFORMATION\n'),
        (7,  ' VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0\n'),
        (9,  ' WRAP.                         NO: ONE LINE PER DEPTH STEP\n'),
        (10, '~A\n'),
        (12, ' 1700.0000  -999.2500  -999.2500  -999.2500  -999.2500\n'),
        (14, ' 1700.5000    40.7909     0.0218     0.0417    25.9985\n'),
        (16, ' 1703.5000    61.1144     0.0199     0.0383    13.2042\n'),
    ]
    assert result == expected


@pytest.mark.parametrize(
    'line, expected',
    (
        ('#\n', ''),
        ('# Some comment   \n', ' Some comment   '),
        (' # Some comment   \n', ' Some comment   '),
        (' # Some comment   ', ' Some comment   '),
    )
)
def test_re_parse_comment(line, expected):
    """TestLASReadLowLevel.test_01(): Tests RE_COMMENT."""
    m = LASRead.RE_COMMENT.match(line)
    assert m is not None
    assert len(m.groups()) == 1
    assert m.group(1) == expected


@pytest.mark.parametrize(
    'line, expected',
    (
        ('~V\n', ('V', None)),
        ('~VERSION INFORMATION\n', ('V', 'ERSION INFORMATION')),
    )
)
def test_re_section_head(line, expected):
    """TestLASReadLowLevel.test_05(): Tests RE_SECT_HEAD."""
    m = LASRead.RE_SECT_HEAD.match(line)
    assert m is not None
    assert len(m.groups()) == 2
    assert m.groups() == expected


@pytest.mark.parametrize(
    'line',
    (
        ' ~V\n',
    )
)
def test_re_section_head_fails(line):
    """TestLASReadLowLevel.test_05(): Tests RE_SECT_HEAD."""
    m = LASRead.RE_SECT_HEAD.match(line)
    assert m is None


@pytest.mark.parametrize(
    'line, expected',
    (
        ('MNEM', ('MNEM',)),
        ('MNEM ', ('MNEM',)),
        (' MNEM', ('MNEM',)),
        (' MNEM ', ('MNEM',)),
    )
)
def test_re_line_field_0(line, expected):
    """TestLASReadLowLevel.test_10(): Tests RE_LINE_FIELD_0."""
    m = LASRead.RE_LINE_FIELD_0.match(line)
    assert m is not None
    assert len(m.groups()) == 1
    assert m.groups() == expected


@pytest.mark.parametrize(
    'line, expected',
    (
        ('FEET    Something   ', ('FEET', '    Something   ')),
        ('FEET    Something   else   ', ('FEET', '    Something   else   ')),
        (' FEET    Something   else   ', (None,  ' FEET    Something   else   ')),
    )
)
def test_re_line_field_1(line, expected):
    """TestLASReadLowLevel.test_10(): Tests RE_LINE_FIELD_1."""
    m = LASRead.RE_LINE_FIELD_1.match(line)
    assert m is not None
    assert len(m.groups()) == 2
    assert m.groups() == expected


def test_las_read_las_section():
    """TestLASReadLASSection.test_01(): Constructor."""
    las_section = LASRead.LASSection('V')
    las_section.add_member_line(1, 'VERS.                     2.0: CWLS log ASCII Standard Version 2.00\n')
    las_section.add_member_line(2, 'WRAP.                      NO: One line per depth step\n')
    las_section.finalise()
    assert las_section.type == 'V'
    assert las_section.members == [
        LASRead.SectLine(mnem='VERS', unit='', valu=2.0, desc='CWLS log ASCII Standard Version 2.00'),
        LASRead.SectLine(mnem='WRAP', unit='', valu=False, desc='One line per depth step'),
    ]
    assert len(las_section) == 2


@pytest.mark.parametrize(
    'section_type, text, expected_error',
    (
        ('V', '', 'Section "V" must have 2 entries not 0.'),
        (
            'V',
            '''VERS.                     2.0: CWLS log ASCII Standard Version 2.00
''',
            'Section "V" must have 2 entries not 1.',
        ),
        (
            'V',
            '''VERS.                     2.0: CWLS log ASCII Standard Version 2.00
XXXX.                      NO: One line per depth step
''',
            'Section "V" must have entry[1]: "WRAP".',
        ),
        (
            'V',
            '''VERS.                     3.0: CWLS log ASCII Standard Version 3.00
WRAP.                      NO: One line per depth step
''',
            'Section "V" must have value for "VERS" converted to (1.2, 2.0) from "3.0".',
        ),
        (
            'V',
            '''VERS.                     2.0: CWLS log ASCII Standard Version 2.00
WRAP.                      XX: One line per depth step
''',
            'Section "V" must have value for "WRAP" converted to (True, False) from "XX".',
        ),
    )
)
def test_las_read_las_section_raises(section_type, text, expected_error):
    """
    TestLASReadLASSection.test_01(): Constructor.
    This exercises LASRead.SECTION_MNEMONIC_ORDER_AND_VALUES.
    """
    las_section = LASRead.LASSection(section_type)
    for i, line in enumerate(text.split('\n')):
        las_section.add_member_line(i + 1, line)
    with pytest.raises(LASRead.ExceptionLASReadSection) as err:
        las_section.finalise()
    assert err.value.args[0] == expected_error


@pytest.mark.parametrize(
    'line, expected',
    (
        # Integers
        ('1234', 1234,),
        (' 1234', 1234,),
        ('1234 ', 1234,),
        (' 1234 ', 1234,),
        # floats
        ('1.234', 1.234,),
        (' 1.234', 1.234,),
        ('1.234 ', 1.234,),
        (' 1.234 ', 1.234,),
        ('   -1.234E+4   ', -12340.0),
        ('  1234e01   ', 12340.0),
        ('YES', True),
        ('NO', False),
        ('TEXT', 'TEXT'),
        (None, ''),
        (b'', ''),
    )
)
def test_las_read_value(line, expected):
    """TestLASReadLASSection.test_02(): _val()."""
    assert LASRead.string_to_value(line) == expected


def test_las_section_str():
    """TestLASReadLASSection.test_03(): Adding member lines."""
    las_section = LASRead.LASSection('P')
    assert las_section.type == 'P'
    assert las_section.members == []
    las_section.add_member_line(2, ' DATE .       13/12/1986                       : LOG DATE  {DD/MM/YYYY}\n')
    las_section.add_member_line(3, ' STRT .M              1670.0000                : First Index Value\n')
    las_section.finalise()
    assert str(las_section) == 'LASSection: "P" with 2 lines'


@pytest.mark.parametrize(
    'mnemonic, expected',
    (
        ('DATE', True),
        ('STRT', True),
        ('XXXX', False),
    )
)
def test_las_section_contains(mnemonic, expected):
    """TestLASReadLASSection.test_03(): Adding member lines."""
    las_section = LASRead.LASSection('P')
    assert las_section.type == 'P'
    assert las_section.members == []
    las_section.add_member_line(2, ' DATE .       13/12/1986                       : LOG DATE  {DD/MM/YYYY}\n')
    las_section.add_member_line(3, ' STRT .M              1670.0000                : First Index Value\n')
    las_section.finalise()
    assert (mnemonic in las_section) == expected


@pytest.mark.parametrize(
    'line, expected',
    (
        (
            'VERS.                     2.0: CWLS log ASCII Standard Version 2.00\n',
            LASRead.SectLine(mnem='VERS', unit='', valu=2.0, desc='CWLS log ASCII Standard Version 2.00')
        ),
        (
            'VERS.                     2.0:     \n',
            LASRead.SectLine(mnem='VERS', unit='', valu=2.0, desc='')
        ),
        (
            'MNEM.     ..: Extra dots.\n',
            LASRead.SectLine(mnem='MNEM', unit='', valu='..', desc='Extra dots.')
        ),
        (
            'MNEM.    value ::: Extra colons.\n',
            LASRead.SectLine(mnem='MNEM', unit='', valu='value ::', desc='Extra colons.')
        ),
        (
            'MNEM.    value..::: Extra dots and colons.\n',
            LASRead.SectLine(mnem='MNEM', unit='', valu='value..::', desc='Extra dots and colons.')
        ),
        (
            ' DATE .       13/12/1986                       : LOG DATE  {DD/MM/YYYY}\n',
            LASRead.SectLine(mnem='DATE', unit='', valu='13/12/1986', desc='LOG DATE  {DD/MM/YYYY}')
        ),
        (
            ' STRT .M              1670.0000                : First Index Value\n',
            LASRead.SectLine(mnem='STRT', unit='M', valu=1670.0, desc='First Index Value')
        ),
    )
)
def test_line_to(line, expected):
    result = LASRead.line_to_sect_line(line)
    assert result == expected


def test_adding_member_lines():
    """TestLASReadLASSection.test_03(): Adding member lines."""
    las_section = LASRead.LASSection('P')
    assert las_section.type == 'P'
    assert las_section.members == []
    las_section.add_member_line(2, ' DATE .       13/12/1986                       : LOG DATE  {DD/MM/YYYY}\n')
    las_section.add_member_line(3, ' STRT .M              1670.0000                : First Index Value\n')
    las_section.finalise()
    expected = [
        LASRead.SectLine(mnem='DATE', unit='', valu='13/12/1986', desc='LOG DATE  {DD/MM/YYYY}'),
        LASRead.SectLine(mnem='STRT', unit='M', valu=1670.0, desc='First Index Value'),
    ]
    assert las_section.members == expected
    assert len(las_section) == 2
    # Test indexing
    for i in range(len(las_section)):
        assert las_section[i] == expected[i]


def test_adding_member_lines_fail():
    """TestLASReadLASSection.test_04(): Adding member lines - fail."""
    las_section = LASRead.LASSection('P')
    assert las_section.type == 'P'
    assert las_section.members == []
    with pytest.raises(LASRead.ExceptionLASReadSection) as _err:
        las_section.add_member_line(1, '  .       13/12/1986                       : LOG DATE  {DD/MM/YYYY}\n')


def test_adding_member_lines_to_v_section_wrong_order_fail():
    """TestLASReadLASSection.test_05(): Adding member lines to 'V' section in wrong order."""
    las_section = LASRead.LASSection('V')
    assert las_section.type == 'V'
    assert las_section.members == []
    las_section.add_member_line(2, ' WRAP.                         NO: ONE LINE PER DEPTH STEP\n')
    las_section.add_member_line(3, ' VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0\n')
    with pytest.raises(LASRead.ExceptionLASReadSection) as _err:
        las_section.finalise()


def test_adding_member_lines_to_v_section_right_order_wrong_values_fail():
    """TestLASReadLASSection.test_06(): Adding member lines to 'V' section in right order, wrong values: 3.0."""
    las_section = LASRead.LASSection('V')
    assert las_section.type == 'V'
    assert las_section.members == []
    las_section.add_member_line(2, ' VERS.                        3.0: CWLS LOG ASCII STANDARD - VERSION 3.0\n')
    las_section.add_member_line(3, ' WRAP.                         NO: ONE LINE PER DEPTH STEP\n')
    with pytest.raises(LASRead.ExceptionLASReadSection) as _err:
        las_section.finalise()


def test_adding_member_lines_to_v_section_right_order_wrong_values_fail_what():
    """TestLASReadLASSection.test_07(): Adding member lines to 'V' section in right order, wrong values: WHAT."""
    las_section = LASRead.LASSection('V')
    assert las_section.type == 'V'
    assert las_section.members == []
    las_section.add_member_line(2, ' VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0\n')
    las_section.add_member_line(3, ' WRAP.                       WHAT: ONE LINE PER DEPTH STEP\n')
    with pytest.raises(LASRead.ExceptionLASReadSection) as _err:
        las_section.finalise()


def test_adding_member_lines_to_0_section():
    """TestLASReadLASSection.test_10(): Adding member lines to 'O' section."""
    las_section = LASRead.LASSection('O')
    assert las_section.type == 'O'
    assert las_section.members == []
    las_section.add_member_line(1, 'Line 1\n')
    las_section.add_member_line(2, 'Line 2\n')
    expected = [
        'Line 1',
        'Line 2',
    ]
    assert las_section.members == expected


def _ret_simple_curve_section():
    las_section = LASRead.LASSection('C')
    las_str = """ DEPT.F                          : 
 GR  .GAPI           45 310 01 00: 
 DPHI.V/V            45 890 00 00: 
 NPHI.V/V            42 890 00 00: 
 ILD .OHMM           05 120 00 00: 
"""
    for i, l in enumerate(las_str.split('\n')):
        las_section.add_member_line(i, l)
    las_section.finalise()
    assert len(las_section) == 5
    return las_section


def test_simple_curve_and_empty_array_section():
    """TestLASReadLASSectionArray.test_01(): Constructor."""
    las_curve_section = _ret_simple_curve_section()
    las_array_section = LASRead.LASSectionArray('A', False, las_curve_section)
    las_array_section.finalise()
    assert las_array_section.type == 'A'
    assert las_array_section.members == []
    assert not las_array_section._wrap
    expected = [
        ('DEPT', 'F'),
        ('GR', 'GAPI'),
        ('DPHI', 'V/V'),
        ('NPHI', 'V/V'),
        ('ILD', 'OHMM'),
    ]
    assert las_array_section._mnemonics_units == expected


def test_simple_curve_and_array_section_no_wrap_members():
    """TestLASReadLASSectionArray.test_02(): Populate with array, no wrap."""
    las_curve_section = _ret_simple_curve_section()
    las_array_section = LASRead.LASSectionArray('A', False, las_curve_section)
    array_str = """ 1700.0000  -999.2500  -999.2500  -999.2500  -999.2500
 1700.5000    40.7909     0.0218     0.0417    25.9985
 1701.0000    44.0165     0.0347     0.0333    26.1850
 1701.5000    45.4578     0.0506     0.0272    25.7472
 1702.0000    44.3055     0.0527     0.0213    23.8872
 1702.5000    42.6896     0.0443     0.0167    20.8817
 1703.0000    52.4264     0.0290     0.0229    17.8425
 1703.5000    61.1144     0.0199     0.0383    13.2042
"""
    for i, l in enumerate(array_str.split('\n')):
        las_array_section.add_member_line(i, l)
    las_array_section.finalise()
    assert las_array_section.type == 'A'
    assert las_array_section.members == []


def test_simple_curve_and_array_section_no_wrap_keys():
    """TestLASReadLASSectionArray.test_02(): Populate with array, no wrap."""
    las_curve_section = _ret_simple_curve_section()
    las_array_section = LASRead.LASSectionArray('A', False, las_curve_section)
    array_str = """ 1700.0000  -999.2500  -999.2500  -999.2500  -999.2500
 1700.5000    40.7909     0.0218     0.0417    25.9985
 1701.0000    44.0165     0.0347     0.0333    26.1850
 1701.5000    45.4578     0.0506     0.0272    25.7472
 1702.0000    44.3055     0.0527     0.0213    23.8872
 1702.5000    42.6896     0.0443     0.0167    20.8817
 1703.0000    52.4264     0.0290     0.0229    17.8425
 1703.5000    61.1144     0.0199     0.0383    13.2042
"""
    for i, l in enumerate(array_str.split('\n')):
        las_array_section.add_member_line(i, l)
    las_array_section.finalise()
    assert las_array_section.type == 'A'
    assert sorted(list(las_array_section.keys())) == [1700.0, 1700.5, 1701.0, 1701.5, 1702.0, 1702.5, 1703.0, 1703.5]


def test_simple_curve_and_array_section_no_wrap_values():
    """TestLASReadLASSectionArray.test_02(): Populate with array, no wrap."""
    las_curve_section = _ret_simple_curve_section()
    las_array_section = LASRead.LASSectionArray('A', False, las_curve_section)
    array_str = """ 1700.0000  -999.2500  -999.2500  -999.2500  -999.2500
 1700.5000    40.7909     0.0218     0.0417    25.9985
 1701.0000    44.0165     0.0347     0.0333    26.1850
 1701.5000    45.4578     0.0506     0.0272    25.7472
 1702.0000    44.3055     0.0527     0.0213    23.8872
 1702.5000    42.6896     0.0443     0.0167    20.8817
 1703.0000    52.4264     0.0290     0.0229    17.8425
 1703.5000    61.1144     0.0199     0.0383    13.2042
"""
    for i, l in enumerate(array_str.split('\n')):
        las_array_section.add_member_line(i, l)
    las_array_section.finalise()
    assert las_array_section.type == 'A'
    expected = np.array([
        [1700.0, -999.25, -999.25, -999.25, -999.25],
        [1700.5, 40.7909, 0.0218, 0.0417, 25.9985],
        [1701.0, 44.0165, 0.0347, 0.0333, 26.185],
        [1701.5, 45.4578, 0.0506, 0.0272, 25.7472],
        [1702.0, 44.3055, 0.0527, 0.0213, 23.8872],
        [1702.5, 42.6896, 0.0443, 0.0167, 20.8817],
        [1703.0, 52.4264, 0.029, 0.0229, 17.8425],
        [1703.5, 61.1144, 0.0199, 0.0383, 13.2042],
    ]).T.reshape((5, 8, 1))
    for i in range(len(las_array_section.frame_array)):
        a0 = las_array_section.frame_array.channels[i].array
        a1 = expected[i]
        assert a0.shape == (8, 1)
        assert np.array_equal(a0, a1)


def test_simple_curve_and_array_section_with_wrap_1():
    """TestLASReadLASSectionArray.test_03(): Populate with array, with wrap +1 line."""
    las_curve_section = _ret_simple_curve_section()
    las_array_section = LASRead.LASSectionArray('A', True, las_curve_section)
    las_str = """ 1700.0000
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
    for i, l in enumerate(las_str.split('\n')):
        las_array_section.add_member_line(i, l)
    las_array_section.finalise()
    assert las_array_section.type == 'A'
    assert las_array_section.members == []
    expected = np.array([
        [1700.0, -999.25, -999.25, -999.25, -999.25],
        [1700.5, 40.7909, 0.0218, 0.0417, 25.9985],
        [1701.0, 44.0165, 0.0347, 0.0333, 26.185],
        [1701.5, 45.4578, 0.0506, 0.0272, 25.7472],
        [1702.0, 44.3055, 0.0527, 0.0213, 23.8872],
        [1702.5, 42.6896, 0.0443, 0.0167, 20.8817],
        [1703.0, 52.4264, 0.029, 0.0229, 17.8425],
        [1703.5, 61.1144, 0.0199, 0.0383, 13.2042],
    ]).T.reshape((5, 8, 1))
    for i in range(len(las_array_section.frame_array)):
        a0 = las_array_section.frame_array.channels[i].array
        a1 = expected[i]
        assert a0.shape == (8, 1)
        assert np.array_equal(a0, a1)
    assert sorted(list(las_array_section.keys())) == [1700.0, 1700.5, 1701.0, 1701.5, 1702.0, 1702.5, 1703.0, 1703.5]


def test_simple_curve_and_array_section_with_wrap_2():
    """TestLASReadLASSectionArray.test_04(): Populate with array, with wrap +2 line."""
    las_curve_section = _ret_simple_curve_section()
    las_array_section = LASRead.LASSectionArray('A', True, las_curve_section)
    las_str = """ 1700.0000
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
    for i, l in enumerate(las_str.split('\n')):
        las_array_section.add_member_line(i, l)
    las_array_section.finalise()
    assert las_array_section.type == 'A'
    assert las_array_section.members == []
    expected = np.array([
        [1700.0, -999.25, -999.25, -999.25, -999.25],
        [1700.5, 40.7909, 0.0218, 0.0417, 25.9985],
        [1701.0, 44.0165, 0.0347, 0.0333, 26.185],
        [1701.5, 45.4578, 0.0506, 0.0272, 25.7472],
        [1702.0, 44.3055, 0.0527, 0.0213, 23.8872],
        [1702.5, 42.6896, 0.0443, 0.0167, 20.8817],
        [1703.0, 52.4264, 0.029, 0.0229, 17.8425],
        [1703.5, 61.1144, 0.0199, 0.0383, 13.2042],
    ]).T.reshape((5, 8, 1))
    for i in range(len(las_array_section.frame_array)):
        a0 = las_array_section.frame_array.channels[i].array
        a1 = expected[i]
        assert a0.shape == (8, 1)
        assert np.array_equal(a0, a1)
    assert sorted(list(las_array_section.keys())) == [1700.0, 1700.5, 1701.0, 1701.5, 1702.0, 1702.5, 1703.0, 1703.5]


def test_simple_curve_and_array_section_with_wrap_dupe_curves():
    """TestLASReadLASSectionArray.test_04(): Populate with array, with wrap +2 line.
    Curve section has duplicate curves."""
    las_curve_section = LASRead.LASSection('C', raise_on_error=False)
    las_str = """ DEPT.F                          : 
 GR  .GAPI           45 310 01 00: 
 GR  .GAPI           45 310 01 00: 
 DPHI.V/V            45 890 00 00: 
 NPHI.V/V            42 890 00 00: 
 ILD .OHMM           05 120 00 00: 
"""
    for i, l in enumerate(las_str.split('\n')):
        las_curve_section.add_member_line(i, l)
    las_curve_section.finalise()
    assert len(las_curve_section) == 6
    las_array_section = LASRead.LASSectionArray('A', True, las_curve_section, raise_on_error=False)
    las_str = """ 1700.0000
 -999.2500  -999.2500  -999.2500
 -999.2500  -999.2500
 1700.5000
 40.7909 40.7909     0.0218
 0.0417    25.9985
 1701.0000
 44.0165 44.0165     0.0347
 0.0333    26.1850
 1701.5000
 45.4578 45.4578     0.0506
 0.0272    25.7472
 1702.0000
 44.3055 44.3055     0.0527
 0.0213    23.8872
 1702.5000
 42.6896 42.6896     0.0443
 0.0167    20.8817
 1703.0000
 52.4264 52.4264     0.0290
 0.0229    17.8425
 1703.5000
 61.1144 61.1144     0.0199
 0.0383    13.2042
"""
    for i, l in enumerate(las_str.split('\n')):
        las_array_section.add_member_line(i, l)
    las_array_section.finalise()
    assert las_array_section.type == 'A'
    assert las_array_section.members == []
    expected = np.array([
        [1700.0, -999.25, -999.25, -999.25, -999.25],
        [1700.5, 40.7909, 0.0218, 0.0417, 25.9985],
        [1701.0, 44.0165, 0.0347, 0.0333, 26.185],
        [1701.5, 45.4578, 0.0506, 0.0272, 25.7472],
        [1702.0, 44.3055, 0.0527, 0.0213, 23.8872],
        [1702.5, 42.6896, 0.0443, 0.0167, 20.8817],
        [1703.0, 52.4264, 0.029, 0.0229, 17.8425],
        [1703.5, 61.1144, 0.0199, 0.0383, 13.2042],
    ]).T.reshape((5, 8, 1))
    for i in range(len(las_array_section.frame_array)):
        a0 = las_array_section.frame_array.channels[i].array
        a1 = expected[i]
        assert a0.shape == (8, 1)
        assert np.array_equal(a0, a1)
    assert sorted(list(las_array_section.keys())) == [1700.0, 1700.5, 1701.0, 1701.5, 1702.0, 1702.5, 1703.0, 1703.5]


def test_simple_curve_and_array_section_non_floats_to_null():
    """TestLASReadLASSectionArray.test_05(): Convert unreadable floats to NULL."""
    las_curve_section = _ret_simple_curve_section()
    las_array_section = LASRead.LASSectionArray('A', False, las_curve_section)
    las_str = """ 1700.0000  -999.2500  -999.2500  -999.2500  -999.2500
 1700.5000    40.7909     0.0218     0.0417    25.9985
 1701.0000    44.0165     ******     0.0333    26.1850
 1701.5000    45.4578     0.0506     0.0272    25.7472
 1702.0000    44.3055     xxxxxx     0.0213    23.8872
 1702.5000    42.6896     0.0443     0.0167    20.8817
 1703.0000    52.4264     0.0290     0.0229    17.8425
 1703.5000    61.1144     0.0199     0.0383    13.2042
"""
    for i, l in enumerate(las_str.split('\n')):
        las_array_section.add_member_line(i, l)
    las_array_section.finalise()
    assert las_array_section.type == 'A'
    assert las_array_section.members == []
    expected = np.array([
        [1700.0, -999.25, -999.25, -999.25, -999.25],
        [1700.5, 40.7909, 0.0218, 0.0417, 25.9985],
        [1701.0, 44.0165, -999.25, 0.0333, 26.185],
        [1701.5, 45.4578, 0.0506, 0.0272, 25.7472],
        [1702.0, 44.3055, -999.25, 0.0213, 23.8872],
        [1702.5, 42.6896, 0.0443, 0.0167, 20.8817],
        [1703.0, 52.4264, 0.029, 0.0229, 17.8425],
        [1703.5, 61.1144, 0.0199, 0.0383, 13.2042],
    ]).T.reshape((5, 8, 1))
    for i in range(len(las_array_section.frame_array)):
        a0 = las_array_section.frame_array.channels[i].array
        a1 = expected[i]
        assert a0.shape == (8, 1)
        assert np.array_equal(a0, a1)
    assert sorted(list(las_array_section.keys())) == [1700.0, 1700.5, 1701.0, 1701.5, 1702.0, 1702.5, 1703.0, 1703.5]


def test_simple_curve_and_array_section_with_wrap_1_one_value():
    """TestLASReadLASSectionArray.test_11(): Populate with array, with wrap +1 line OK when only one value."""
    las_curve_section = _ret_simple_curve_section()
    las_array_section = LASRead.LASSectionArray('A', True, las_curve_section)
    las_str = """ 1700.0000
 -999.2500 
 -999.2500  -999.2500  -999.2500
"""
    for i, l in enumerate(las_str.split('\n')):
        las_array_section.add_member_line(i, l)
    las_array_section.finalise()
    assert las_array_section.members == []
    expected = np.array(
        [
            [[1700.0]], [[-999.25]], [[-999.25]], [[-999.25]], [[-999.25]]
         ]
    )
    for i in range(len(las_array_section.frame_array)):
        a0 = las_array_section.frame_array.channels[i].array
        a1 = expected[i]
        assert a0.shape == (1, 1)
        assert np.array_equal(a0, a1)
    assert sorted(list(las_array_section.keys())) == [1700.0, ]


def test_simple_curve_and_array_section_with_wrap_1_missing_value_raises():
    """TestLASReadLASSectionArray.test_12(): Populate with array, with wrap +1 fails when missing one value,
    single line."""
    las_curve_section = _ret_simple_curve_section()
    las_array_section = LASRead.LASSectionArray('A', True, las_curve_section)
    las_str = """ 1700.0000
 -999.2500  -999.2500  -999.2500  
"""
    with pytest.raises(LASRead.ExceptionLASReadSectionArray) as _err:
        for i, l in enumerate(las_str.split('\n')):
            las_array_section.add_member_line(i, l)
        las_array_section.finalise()
    assert las_array_section.members == []


def test_simple_curve_and_array_section_with_wrap_1_missing_value_raises_b():
    """TestLASReadLASSectionArray.test_13(): Populate with array, with wrap +1 fails when missing one value at EOF,
    multi line."""
    las_curve_section = _ret_simple_curve_section()
    las_array_section = LASRead.LASSectionArray('A', True, las_curve_section)
    las_str = """ 1700.0000
 -999.2500  -999.2500  -999.2500  -999.2500  
 1700.5000
 40.7909     0.0218     0.0417
"""
    with pytest.raises(LASRead.ExceptionLASReadSectionArray) as err:
        for i, l in enumerate(las_str.split('\n')):
            las_array_section.add_member_line(i, l)
        las_array_section.finalise()
    assert err.value.args[0] == 'Line [-1] buffer length miss-match, frame length 4 which should be length 5'
    assert las_array_section.members == []
    expected = np.array(
        [
            [[1700.0]], [[-999.25]], [[-999.25]], [[-999.25]], [[-999.25]]
         ]
    )
    for i in range(len(las_array_section.frame_array)):
        a0 = las_array_section.frame_array.channels[i].array
        a1 = expected[i]
        assert a0.shape == (1, 1)
        assert np.array_equal(a0, a1)
    assert sorted(list(las_array_section.keys())) == [1700.0, ]


def test_simple_curve_and_array_section_with_wrap_1_extra_value_raises():
    """Wrapped array with five channels but  missing a channel in the first line so we consume the next index value.
    Then the second line has too  many index values.
    We expect no data."""
    las_curve_section = _ret_simple_curve_section()
    assert list(las_curve_section.keys()) == ['DEPT', 'GR', 'DPHI', 'NPHI', 'ILD']
    las_array_section = LASRead.LASSectionArray('A', wrap=True, curve_section=las_curve_section)
    las_str = """ 1700.0000
 -999.2500  -999.2500  -999.2500  
 1700.5000
 40.7909     0.0218     0.0417    25.9985
"""
    with pytest.raises(LASRead.ExceptionLASReadSectionArray) as err:
        for i, l in enumerate(las_str.split('\n')):
            las_array_section.add_member_line(i, l)
        las_array_section.finalise()
    expected = 'Line [3] More than one [4] index values, line is:  40.7909     0.0218     0.0417    25.9985'
    assert err.value.args[0] == expected
    assert las_array_section.members == []
    assert len(las_array_section.frame_array) == 5
    assert len(las_array_section.frame_array.x_axis) == 0
    assert sorted(list(las_array_section.keys())) == []


def test_simple_curve_and_array_section_with_wrap_1_missing_value_raises_d():
    """TestLASReadLASSectionArray.test_15(): Populate with array, with wrap +1 fails when too many values,
    multi line."""
    las_curve_section = _ret_simple_curve_section()
    las_array_section = LASRead.LASSectionArray('A', True, las_curve_section)
    las_str = """ 1700.0000
 -999.2500  -999.2500  -999.2500  -999.2500  -999.2500  
"""
    with pytest.raises(LASRead.ExceptionLASReadSectionArray) as _err:
        for i, l in enumerate(las_str.split('\n')):
            las_array_section.add_member_line(i, l)
        las_array_section.finalise()
        assert las_array_section._members == []


def test_curve_and_array_section_with_time_date():
    las_curve_section = LASRead.LASSection('C')
    las_curve_str = """TIME	    .HHMMSS	       :
DATE	    .D		       :
"""
    for i, l in enumerate(las_curve_str.split('\n')):
        las_curve_section.add_member_line(i, l)
    las_curve_section.finalise()
    las_array_str = """23:05:04 15-Dec-06
23:05:14 15-Dec-06
23:05:24 15-Dec-06
23:05:34 15-Dec-06
23:05:44 15-Dec-06
23:05:54 15-Dec-06
"""
    las_array_section = LASRead.LASSectionArray('A', False, las_curve_section)
    for i, l in enumerate(las_array_str.split('\n')):
        las_array_section.add_member_line(i, l)
    las_array_section.finalise()


def test_las_read_minimal():
    """TestLASRead.test_01(): Tests file with comment and blank lines and single version section."""
    las_raw_file = io.StringIO("""
# Some comment
# Another comment
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP

""")
    las_file = LASRead.LASRead(las_raw_file, 'MyID')
    assert len(las_file) == 1


def test_las_read_minimal_with_well_section_log_up():
    """TestLASRead.test_02(): Tests file with version and well section."""
    las_raw_file = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
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
    las_file = LASRead.LASRead(las_raw_file, 'MyID')
    assert len(las_file) == 2
    assert not las_file.is_log_down()


def test_las_read_minimal_with_well_section_log_down():
    """TestLASRead.test_03(): Tests file with version and well section. logDown()."""
    las_raw_file = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
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
    las_file = LASRead.LASRead(las_raw_file, 'MyID')
    assert len(las_file) == 2
    assert las_file.is_log_down()


def test_las_read_minimal_with_well_section_not_log_down():
    """TestLASRead.test_04(): Tests file with version and well section. not logDown()."""
    las_raw_file = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
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
    las_file = LASRead.LASRead(las_raw_file, 'MyID')
    assert len(las_file) == 2
    assert not las_file.is_log_down()


def test_las_read_minimal_with_well_section_null_specified():
    """TestLASRead.test_05_00(): Tests file with version and well section. NULL value specified."""
    las_raw_file = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
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
    las_file = LASRead.LASRead(las_raw_file, 'MyID')
    assert len(las_file) == 2
    assert las_file.null_value == -9.25


def test_las_read_minimal_with_well_section_null_default():
    """TestLASRead.test_05_01(): Tests file with version and well section. NULL value default."""
    las_raw_file = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
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
    las_file = LASRead.LASRead(las_raw_file, 'MyID')
    assert len(las_file) == 2
    assert las_file.null_value == -999.25


def test_las_read_minimal_with_well_section_xaxis_as_lis():
    """TestLASRead.test_06_00(): Tests file with version and well section. X axis units recognised as LIS ones."""
    las_raw_file = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
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
    las_file = LASRead.LASRead(las_raw_file, 'MyID')
    assert len(las_file) == 2
    assert las_file.x_axis_units == b'FT  '


def test_las_read_minimal_with_well_section_xaxis_converted():
    """TestLASRead.test_06_01(): Tests file with version and well section. X axis units not recognised as LIS ones but
    converted."""
    las_raw_file = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
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
    las_file = LASRead.LASRead(las_raw_file, 'MyID')
    assert len(las_file) == 2
    assert las_file.x_axis_units == b'FEET'


def test_las_read_minimal_with_well_section_xaxis_missing_raises():
    """TestLASRead.test_06_02(): Tests file with version and well section. X axis units missing."""
    raw_las_file = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
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
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert len(las_file) == 2
    with pytest.raises(LASRead.ExceptionLASReadData) as err:
        _x = las_file.x_axis_units
    assert err.value.args[0] == 'LASBase.logDown(): No "W" section or no "STRT" value.'


def test_las_read_minimal_with_well_section_strt_stop_step():
    """TestLASRead.test_06_03(): Tests file with version and well section. X axis units STRT/STOP/STEP."""
    raw_las_file = io.StringIO("""# #KGS#INPUT_FILE: /home/crude2_3/WellLogs/Guy/104-Universal/disc23/942661.las.las
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
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert len(las_file) == 2
    assert las_file.x_axis_start == EngVal.EngVal(3700.0, b'FEET')
    assert las_file.x_axis_stop == EngVal.EngVal(1700.0, b'FEET')
    assert las_file.x_axis_step == EngVal.EngVal(-0.5, b'FEET')


def test_las_read_minimal_all_missing_a_section():
    """TestLASRead.test_10(): Tests file with all sections except A section."""
    raw_las_file = io.StringIO("""~VERSION INFORMATION
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
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert len(las_file) == 5
    assert las_file.number_of_frames() == 0
    assert las_file.number_of_data_points() == 0


def test_las_read_minimal_all_with_a_section():
    """TestLASRead.test_11(): Tests file with all sections with A section."""
    raw_las_file = io.StringIO("""~VERSION INFORMATION
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
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert len(las_file) == 6
    assert las_file.number_of_frames() == 8
    assert las_file.number_of_data_points() == 8 * 5


def test_las_read_minimal_all_with_awp_section():
    """TestLASRead.test_12(): Tests file with W and P section and Mnemonic access."""
    raw_las_file = io.StringIO("""~VERSION INFORMATION
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
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert len(las_file) == 3
    assert las_file.number_of_frames() == 0
    assert las_file.number_of_data_points() == 0
    assert las_file.get_wsd_mnemonic('RM') == (2.56, 'OHMM')
    assert las_file.get_wsd_mnemonic('UNKNOWN') == (None, None)
    assert sorted(las_file.get_all_wsd_mnemonics()) == [
        'API', 'BHT', 'COMP', 'COUN', 'DATE', 'EGL', 'EKB',
        'EMT', 'FL', 'FLD', 'LEAS', 'LOC', 'MCST', 'MFT', 'NULL',
        'PM', 'RANG', 'RM', 'RMB', 'RMC', 'RMF', 'RUN', 'SECT',
        'SRVC', 'STAT', 'STEP', 'STOP', 'STRT', 'TD', 'TOWN', 'UWI',
        'WELL', 'WSS',
    ]


LAS_2_MINIMAL_WITH_ARRAY = """~VERSION INFORMATION
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
"""


def test_las_read_minimal_with_array_len_sections():
    raw_las_file = io.StringIO(LAS_2_MINIMAL_WITH_ARRAY)
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert len(las_file) == 6


def test_las_read_minimal_with_array_has_frame_array():
    raw_las_file = io.StringIO(LAS_2_MINIMAL_WITH_ARRAY)
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert las_file.frame_array is not None


def test_las_read_minimal_with_array_number_of_frames():
    raw_las_file = io.StringIO(LAS_2_MINIMAL_WITH_ARRAY)
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert las_file.number_of_frames() == 8


def test_las_read_minimal_with_array_number_of_data_points():
    raw_las_file = io.StringIO(LAS_2_MINIMAL_WITH_ARRAY)
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert las_file.number_of_data_points() == 8 * 5


def test_las_read_minimal_with_array_x_axis_values():
    raw_las_file = io.StringIO(LAS_2_MINIMAL_WITH_ARRAY)
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert list(las_file.frame_array.x_axis.array) == [1700.0, 1700.5, 1701.0, 1701.5, 1702.0, 1702.5, 1703.0, 1703.5, ]


def test_las_read_minimal_with_array_x_axis_values_names():
    raw_las_file = io.StringIO(LAS_2_MINIMAL_WITH_ARRAY)
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    channel_names = [channel.ident for channel in las_file.frame_array.channels]
    assert channel_names == ['DEPT', 'GR', 'DPHI', 'NPHI', 'ILD']


@pytest.mark.parametrize(
    'channel, expected',
    (
        (
            'GR',
            np.ma.array(
                [[-999.25, ], [40.7909, ], [44.0165, ], [45.4578, ], [44.3055, ], [42.6896, ], [52.4264, ],
                 [61.1144, ]],
                mask=[True, False, False, False, False, False, False, False, ]
            )
        ),
        (
            'DPHI',
            np.ma.array(
                [[-999.25, ], [0.0218, ], [0.0347, ], [0.0506, ], [0.0527, ], [0.0443, ], [0.0290, ],
                 [0.0199, ]],
                mask=[True, False, False, False, False, False, False, False, ]
            )
        ),
        (
            'NPHI',
            np.ma.array(
                [[-999.25, ], [0.0417, ], [0.0333, ], [0.0272, ], [0.0213, ], [0.0167, ], [0.0229, ],
                 [0.0383, ]],
                mask=[True, False, False, False, False, False, False, False, ]
            )
        ),
        (
            'ILD',
            np.ma.array(
                [[-999.25, ], [25.9985, ], [26.1850, ], [25.7472, ], [23.8872, ], [20.8817, ], [17.8425, ],
                 [13.2042, ]],
                mask=[True, False, False, False, False, False, False, False, ]
            )
        ),
    ),
)
def test_las_read_minimal_with_array_channel_values(channel, expected):
    raw_las_file = io.StringIO(LAS_2_MINIMAL_WITH_ARRAY)
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    array = las_file.frame_array[channel].array
    assert np.array_equal(array, expected)


def test_las_read_minimal_all_with_awp_section_dupe_well_info_raises():
    """TestLASRead.test_20(): Tests fail with duplicate well information section."""
    raw_las_file = io.StringIO("""
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
    with pytest.raises(LASRead.ExceptionLASRead) as err:
        LASRead.LASRead(raw_las_file, 'MyID')
    assert err.value.args[0] == 'Duplicate section W'


def test_las_read_warn_with_unknown_section():
    """TestLASRead.test_21(): Tests warn with unknown section type."""
    raw_las_file = io.StringIO("""
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
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert len(las_file) == 3
    sections = [s for s in las_file.generate_sections()]
    assert len(sections) == 3
    assert sections[0].type == 'V'
    assert sections[1].type == 'Z'
    assert sections[2].type == 'O'


def test_las_read_version_section_not_first_raises():
    """TestLASRead.test_22(): Tests fail with version section not first section."""
    raw_las_file = io.StringIO("""
# Some comment
# Another comment
~W
 UWI .               15-131-20047: Unique Well Id
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
""")
    with pytest.raises(LASRead.ExceptionLASRead) as err:
        LASRead.LASRead(raw_las_file, 'MyID')
    assert err.value.args[0] == 'Non-version section can not be the first one.'


def test_las_read_duplicate_version_section_raises():
    """TestLASRead.test_23(): Tests fail with duplicate version section."""
    raw_las_file = io.StringIO("""
# Some comment
# Another comment
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
""")
    with pytest.raises(LASRead.ExceptionLASRead) as err:
        LASRead.LASRead(raw_las_file, 'MyID')
    assert err.value.args[0] == 'Version section must be first one.'


def test_las_read_array_section_as_first_section_raises():
    """TestLASRead.test_24(): Tests fail with array section as first section."""
    raw_las_file = io.StringIO("""
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
    with pytest.raises(LASRead.ExceptionLASRead) as err:
        LASRead.LASRead(raw_las_file, 'MyID')
    assert err.value.args[0] == 'Non-version section can not be the first one.'


def test_las_read_missing_curve_section_section_raises():
    """TestLASRead.test_25(): Tests fail with array section with no curve section."""
    raw_las_file = io.StringIO("""
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
    with pytest.raises(LASRead.ExceptionLASRead) as err:
        LASRead.LASRead(raw_las_file, 'MyID')
    assert err.value.args[0] == 'No curve section to describe array section.'


def test_las_read_section_follows_array_section_raises():
    """TestLASRead.test_26(): Tests fail when a section follows an array section."""
    raw_las_file = io.StringIO("""
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
    with pytest.raises(LASRead.ExceptionLASRead) as err:
        LASRead.LASRead(raw_las_file, 'MyID')
    assert err.value.args[0] == 'Line: 19. Found section header line "~O" after array section'


def test_las_read_call_curve_mnems_when_no_curve_section():
    """TestLASRead.test_27(): Tests fail when hasOutpMnem() when no curve section."""
    raw_las_file = io.StringIO("""
# Some comment
# Another comment
~VERSION INFORMATION
 VERS.                        2.0: CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                         NO: ONE LINE PER DEPTH STEP
""")
    raw_las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert not raw_las_file.has_output_mnemonic(Mnem.Mnem('GR'))
    assert raw_las_file.curve_mnemonics() == []


LAS_2_ALL_SECTIONS_EXCEPT_A = """~VERSION INFORMATION
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
"""


def test_las_read_all_section_except_a_testing_curve_section():
    """TestLASRead.test_30(): Tests file with all sections except A section. Testing Curve section."""
    raw_las_file = io.StringIO(LAS_2_ALL_SECTIONS_EXCEPT_A)
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert len(las_file) == 3
    assert las_file.number_of_frames() == 0
    assert las_file.number_of_data_points() == 0
    assert sorted(las_file.curve_mnemonics()) == ['DEPT', 'DPHI', 'GR', 'ILD', 'NPHI']
    assert las_file.curve_mnemonics(ordered=True) == ['DEPT', 'GR', 'DPHI', 'NPHI', 'ILD']


def test_las_read_all_section_except_a_testing_curve_section_has_outp_mnem():
    """TestLASRead.test_31(): Tests file with all sections except A section. Testing Curve section hasOutpMnem()."""
    raw_las_file = io.StringIO(LAS_2_ALL_SECTIONS_EXCEPT_A)
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert len(las_file) == 3
    assert las_file.number_of_frames() == 0
    assert las_file.number_of_data_points() == 0
    expected = ['DEPT', 'DPHI', 'GR', 'ILD', 'NPHI']
    assert sorted(las_file.curve_mnemonics()) == expected
    for mnemonic in expected:
        assert las_file.has_output_mnemonic(mnemonic)
    assert not las_file.has_output_mnemonic('WTF')


def test_las_read_all_section_except_a_testing_curve_section_curve_units():
    """TestLASRead.test_32(): Tests file with all sections except A section. Testing Curve section curveUnitsAsStr()."""
    raw_las_file = io.StringIO(LAS_2_ALL_SECTIONS_EXCEPT_A)
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert len(las_file) == 3
    assert las_file.number_of_frames() == 0
    assert las_file.number_of_data_points() == 0
    expected = [b'FEET', b'GAPI', b'V/V ', b'V/V ', b'OHMM']
    assert [las_file.curve_units_as_str(m) for m in las_file.curve_mnemonics(ordered=True)] == expected


def test_las_read_all_section_except_a_testing_curve_section_curve_units_re_none():
    """TestLASRead.test_33(): Tests file with all sections except A section. Testing Curve section curveUnitsAsStr()
    where regex finds None."""
    raw_las_file = io.StringIO(LAS_2_ALL_SECTIONS_EXCEPT_A)
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert len(las_file) == 3
    assert las_file.number_of_frames() == 0
    assert las_file.number_of_data_points() == 0
    expected = [b'FEET', b'GAPI', b'V/V ', b'V/V ', b'OHMM']
    result = [las_file.curve_units_as_str(m) for m in las_file.curve_mnemonics(ordered=True)]
    assert result == expected


def test_las_read_all_section_except_a_testing_curve_section_curve_units_non_lis():
    """TestLASRead.test_34(): Tests file with all sections except A section.
    Testing Curve section with non-LIS mnemonics."""
    raw_las_file = io.StringIO(LAS_2_ALL_SECTIONS_EXCEPT_A)
    las_file = LASRead.LASRead(raw_las_file, 'MyID')
    assert len(las_file) == 3
    assert las_file.number_of_frames() == 0
    assert las_file.number_of_data_points() == 0
    expected = ['DEPT', 'GR', 'DPHI', 'NPHI', 'ILD']
    result = las_file.curve_mnemonics(ordered=True)
    # print(result)
    assert result == expected
    for mnemonic in expected:
        assert las_file.has_output_mnemonic(mnemonic)
    assert not las_file.has_output_mnemonic('WTF')
    # # Now test that it has LIS equivalents
    # expected = ['DEPT', 'GR', 'DPHI', 'NPHI', 'ILD']
    # for mnemonic in expected:
    #     assert las_file.has_output_mnemonic(mnemonic)
    # assert not las_file.has_output_mnemonic('WTF')


def test_with_leading_space():
    las_raw_file = io.StringIO("""~Version Information
 VERS.                 2.0:   CWLS Log ASCII Standard -VERSION 2.0
 WRAP.                  NO:   One line per depth step
~Well Information Block
 STRT.F             35.0000: START DEPTH
 STOP.F           1961.0000: STOP DEPTH
 STEP.F              0.5000: STEP
 NULL.            -999.2500                       :NULL VALUE
 COMP.                                            :COMPANY
 WELL.      TUBRIDGI 7                            :WELL
 FLD .                                            :FIELD
 LOC .                                            :LOCATION
 CNTY.                                            :COUNTY
 STAT.                                            :STATE
 CTRY.                                            :COUNTRY
 SRVC.                                            :SERVICE COMPANY
 DATE.      23 10 94                              :LOG DATE
 API .                                            :API NUMBER
 UWI .                                            :UNIQUE WELL ID
 ~Curve Information Block
 DEPT.F                   :     1  DEPTH
 CALI.IN                  :     2  Caliper
 PEF .B/EL                :     3  Photo Electric Factor
 RHOB.G/C3                :     4  Bulk Density
 DRHO.G/C3                :     5  Bulk Density Correction
 TNPH.PU                  :     6  Thermal Neutron Porosity
 NPHI.PU                  :     7  Neutron Porosity
 RHGX.G/C3                :     8  Crossplot Grain Density
 THOR.PPM                 :     9  Thorium
 URAN.PPM                 :    10  Uranium
 POTA.                    :    11  Potasium
 SGR .GAPI                :    12  Spectroscopy GR
 CGR .GAPI                :    13  Computed GR
 GR  .GAPI                :    14  Gamma Ray
 DTL .US/F                :    15  Sonic Long Spacing
 DT  .US/F                :    16  Sonic
 SP  .MV                  :    17  Spontaneous Potential
 LLD .OHMM                :    18  Latero-Log Deep
 LLS .OHMM                :    19  Latero-Log Shallow
 LLG .OHMM                :    20  Latero-Log Groninggen (resistivity)
 CALS.IN                  :    21  Caliper (Frame MSFL)
 GR1 .GAPI                :    22  Gamma Ray No1
 MSFL.OHMM                :    23  MSFL Resistivity
~Parameter Information Block
~Other Information - Comments
#***********************************************************
# This LAS file was created by Wiltshire Geological Services.
# The edit data contained herein are copyright property of
# Wiltshire Geological Services. The data are licensed to the
# purchasing company and subsidiaries worldwide, and are NOT
# for on-copying to third parties.  We place no restriction on
# the distribution of plots generated from the digital data.
#***********************************************************
~A
    35.0000  -999.2500  -999.2500  -999.2500  -999.2500  -999.2500  -999.2500  -999.2500  -999.2500  -999.2500  \
    -999.2500  -999.2500  -999.2500  -999.2500  -999.2500  -999.2500  -999.2500  -999.2500  -999.2500  -999.2500  \
    -999.2500    21.3125  -999.2500
""")
    las_parsed_file = LASRead.LASRead(las_raw_file, 'MyID')
    assert len(las_parsed_file) == 6


def test_array_overrun():
    las_raw_file = io.StringIO("""~Version Information
VERS.                     2.0: CWLS log ASCII Standard Version 2.00
WRAP.                      NO: One line per depth step
~Well Information Block
#MNEM.UNIT                 Value                       Information
#------------              -----                       -----------
STRT.M                        1670                    :START
STOP.M                        1670                    :STOP
STEP.M                         0.5                    :STEP
NULL.                     -999.25                     :NULL VALUE
~Curve Information
#MNEM   .UNIT             API CODE Curve Description
#------------             -------- -----------------
DEPTH   .M            00 001 00 00:   0  Depth
GR  .API  00 000 00 00:   6
~A
      1670    -999.25    -999.25
""")
    with pytest.raises(LASRead.ExceptionLASRead) as err:
        LASRead.LASRead(las_raw_file, 'MyID', raise_on_error=False)
    assert err.value.args[0] == 'Expected 2 columns but found 3 in frame 0'


def test_array_underrun():
    las_raw_file = io.StringIO("""~Version Information
VERS.                     2.0: CWLS log ASCII Standard Version 2.00
WRAP.                      NO: One line per depth step
~Well Information Block
#MNEM.UNIT                 Value                       Information
#------------              -----                       -----------
STRT.M                        1670                    :START
STOP.M                        1670                    :STOP
STEP.M                         0.5                    :STEP
NULL.                     -999.25                     :NULL VALUE
~Curve Information
#MNEM   .UNIT             API CODE Curve Description
#------------             -------- -----------------
DEPTH   .M            00 001 00 00:   0  Depth
GR  .API  00 000 00 00:   6
~A
      1670
""")
    with pytest.raises(LASRead.ExceptionLASRead) as err:
        LASRead.LASRead(las_raw_file, 'MyID', raise_on_error=False)
    assert err.value.args[0] == 'Expected 2 columns but found 1 in frame 0'


# Note channel '4' is not conformant, 5 is.
LAS_WITH_NUMERIC_CHANNELS_MINIMAL = """~Version Information
VERS.                     2.0: CWLS log ASCII Standard Version 2.00
WRAP.                      NO: One line per depth step
~Well Information Block
#MNEM.UNIT                 Value                       Information
#------------              -----                       -----------
STRT.M                        1670                    :START
STOP.M                        2217                    :STOP
STEP.M                         0.5                    :STEP
NULL.                     -999.25                     :NULL VALUE
~Curve Information
#MNEM   .UNIT             API CODE Curve Description
#------------             -------- -----------------
DEPTH   .M            00 001 00 00:   0  Depth
4          CHDE_NC.%  00 000 00 00:   6
5       .             00 000 00 00:   9
~Parameter Information
#MNEM.UNIT       Value           Description
#------------    -----           -----------
RUN .         1                 :Run number
~Other Information
# --- LOG MNEMONICS AND UNITS ---
#Depth     LAMU_TO    TGAS_AVG   CHDE_C2    CHDE_C3    CHDE_IC    4          4          5          5
#M         %          %          %          %          %          %          %          %
~A
      1670    -999.25    -999.25    -999.25    -999.25    -999.25    -999.25    -999.25    -999.25    -999.25
"""


def test_with_numeric_channels_when_raise_on_error_false_fails_on_overrun():
    las_raw_file = io.StringIO(LAS_WITH_NUMERIC_CHANNELS_MINIMAL)
    with pytest.raises(LASRead.ExceptionLASRead) as err:
        LASRead.LASRead(las_raw_file, 'MyID', raise_on_error=False)
    assert err.value.args[0] == 'Expected 2 columns but found 10 in frame 0'


def test_with_numeric_channels_when_raise_on_error_true_fails_on_curve_read():
    las_raw_file = io.StringIO(LAS_WITH_NUMERIC_CHANNELS_MINIMAL)
    with pytest.raises(LASRead.ExceptionLASReadSection) as err:
        LASRead.LASRead(las_raw_file, 'MyID', raise_on_error=True)
    expected = (
        'Can not add member, line 15 error:'
        ' Can not decompose line "4          CHDE_NC.%  00 000 00 00:   6"'
        ' with results: None,'
    )
    assert err.value.args[0].startswith(expected)


def test_time_date_channels():
    las_raw_file = io.StringIO("""~Version Information
VERS.             2.0 : CWLS log ASCII standard - Version 2.0
WRAP.             NO  : One line per depth step
#
~Well Information Block
#MNEM.UNIT                   Data Type:Information
#__________________________________________________________
  STRT.           15-DEC-2006 23:05:00 : START INDEX
  STOP.           17-DEC-2006 02:25:00 : STOP INDEX
  STEP.SEC           10.0000 : STEP
  NULL.              -999.25 : NULL VALUE
#
~Curve Information Block
#MNEM.UNIT                     : Curve Description
#---------                     --------------------
TIME	    .HHMMSS	       :
DATE	    .D		       :
HDTH        .M                 : Hole Depth 2hz
BONB        .----              : On Bottom stat (1=Off,0=On) 2hz
HKLD        .KLBF              : Measured Hookload 2hz
#
~Parameter Information Block
#MNEM.UNIT    VALUE                      DESCRIPTION
#---- -----   --------------------       ------------------------
RUN  .        1                          :Run Number
~Other Information Block

#
~A TIME       DATE       HDTH       BONB       HKLD
23:05:04 15-Dec-06  1807.0000     1.0000   215.4579
23:05:14 15-Dec-06  1807.0000     1.0000   215.3874
23:05:24 15-Dec-06  1807.0000     1.0000   215.2491
23:05:34 15-Dec-06  1807.0000     1.0000   214.7775
23:05:44 15-Dec-06  1803.2001     1.0000   214.8049
23:05:54 15-Dec-06  1803.2001     1.0000   214.8267
""")
    las_file = LASRead.LASRead(las_raw_file, 'MyID', raise_on_error=True)
    frame_array = las_file.frame_array
    assert len(frame_array) == 5
    assert frame_array['TIME'].array[0] == datetime.time(23, 5, 4)
    assert frame_array['DATE'].array[0] == datetime.date(2006, 12, 15)


@pytest.mark.parametrize(
    'raise_on_error',
    (True, False,)
)
def test_customer_sections_minimal(raise_on_error):
    las_text = """~VERSION INFORMATION
 VERS.                          2.0 :   CWLS LOG ASCII STANDARD -VERSION 2.0
 WRAP.                          NO  :   ONE LINE PER DEPTH STEP
~DOWNHOLE DATA
Some stuff here.
"""
    las_raw_file = io.StringIO(las_text)
    las_file = LASRead.LASRead(las_raw_file, 'MyID', raise_on_error=raise_on_error)
    print(las_file)
    assert len(las_file) == 2


@pytest.mark.parametrize(
    'las_text, expected',
    (
        # Before version section.
        ("""~DOWNHOLE DATA
Some stuff here.
~VERSION INFORMATION
 VERS.                          2.0 :   CWLS LOG ASCII STANDARD -VERSION 2.0
 WRAP.                          NO  :   ONE LINE PER DEPTH STEP
""", 'User defined section "~DOWNHOLE DATA" but no version section.',
         ),
        # After array section.
        ("""~VERSION INFORMATION
 VERS.                          2.0 :   CWLS LOG ASCII STANDARD -VERSION 2.0
 WRAP.                          NO  :   ONE LINE PER DEPTH STEP
~WELL INFORMATION 
#MNEM.UNIT              DATA                       DESCRIPTION
#----- -----            ----------               -------------------------
STRT    .M              1670.0000                :START DEPTH
STOP    .M              1660.0000                :STOP DEPTH
STEP    .M              -0.1250                  :STEP 
NULL    .               -999.25                  :NULL VALUE
~CURVE INFORMATION
#MNEM.UNIT              API CODES                   CURVE DESCRIPTION
#------------------     ------------              -------------------------
 DEPT   .M                                       :  1  DEPTH
 DT     .US/M           60 520 32 00             :  2  SONIC TRANSIT TIME
~A  DEPTH     DT
1670.000   123.450
~DOWNHOLE DATA
Some stuff here.
""", 'Line: 18. Found section header line "~DOWNHOLE DATA" after array section',
         ),
        # Duplicate.
        ("""~VERSION INFORMATION
 VERS.                          2.0 :   CWLS LOG ASCII STANDARD -VERSION 2.0
 WRAP.                          NO  :   ONE LINE PER DEPTH STEP
~DOWNHOLE DATA
Some stuff here.
~DOWNHOLE DATA
Some stuff here.
""", 'Duplicate section D',
         ),
    ),
)
def test_customer_sections_raises_raise_on_error_true(las_text, expected):
    las_raw_file = io.StringIO(las_text)
    with pytest.raises(LASRead.ExceptionLASRead) as err:
        LASRead.LASRead(las_raw_file, 'MyID', raise_on_error=True)
    print(err.value.args[0])
    assert err.value.args[0] == expected


@pytest.mark.parametrize(
    'las_text, expected',
    (
        # Before version section.
        ("""~DOWNHOLE DATA
Some stuff here.
~VERSION INFORMATION
 VERS.                          2.0 :   CWLS LOG ASCII STANDARD -VERSION 2.0
 WRAP.                          NO  :   ONE LINE PER DEPTH STEP
""", 1,
         ),
        # After array section.
        ("""~VERSION INFORMATION
 VERS.                          2.0 :   CWLS LOG ASCII STANDARD -VERSION 2.0
 WRAP.                          NO  :   ONE LINE PER DEPTH STEP
~WELL INFORMATION 
#MNEM.UNIT              DATA                       DESCRIPTION
#----- -----            ----------               -------------------------
STRT    .M              1670.0000                :START DEPTH
STOP    .M              1660.0000                :STOP DEPTH
STEP    .M              -0.1250                  :STEP 
NULL    .               -999.25                  :NULL VALUE
~CURVE INFORMATION
#MNEM.UNIT              API CODES                   CURVE DESCRIPTION
#------------------     ------------              -------------------------
 DEPT   .M                                       :  1  DEPTH
 DT     .US/M           60 520 32 00             :  2  SONIC TRANSIT TIME
~A  DEPTH     DT
1670.000   123.450
~DOWNHOLE DATA
Some stuff here.
""", 4,
         ),
    ),
)
def test_customer_sections_ignored_when_raise_on_error_false(las_text, expected):
    las_raw_file = io.StringIO(las_text)
    las_file = LASRead.LASRead(las_raw_file, 'MyID', raise_on_error=False)
    assert len(las_file) == expected


def test_customer_sections():
    las_text = """~VERSION INFORMATION
 VERS.                          2.0 :   CWLS LOG ASCII STANDARD -VERSION 2.0
 WRAP.                          NO  :   ONE LINE PER DEPTH STEP
~WELL INFORMATION 
#MNEM.UNIT              DATA                       DESCRIPTION
#----- -----            ----------               -------------------------
STRT    .M              1670.0000                :START DEPTH
STOP    .M              1660.0000                :STOP DEPTH
STEP    .M              -0.1250                  :STEP 
NULL    .               -999.25                  :NULL VALUE
~CURVE INFORMATION
#MNEM.UNIT              API CODES                   CURVE DESCRIPTION
#------------------     ------------              -------------------------
 DEPT   .M                                       :  1  DEPTH
 DT     .US/M           60 520 32 00             :  2  SONIC TRANSIT TIME
~PARAMETER INFORMATION
#MNEM.UNIT              VALUE             DESCRIPTION
#--------------     ----------------      -----------------------------------------------
 MUD    .               GEL CHEM        :   MUD TYPE
~OTHER
     Note: The logging tools became stuck at 625 metres causing the data 
     between 625 metres and 615 metres to be invalid.
~DOWNHOLE DATA
Some stuff here.
~A  DEPTH     DT
1670.000   123.450
"""
    las_raw_file = io.StringIO(las_text)
    las_file = LASRead.LASRead(las_raw_file, 'MyID', raise_on_error=True)
    assert len(las_file) == 7


def test_duplicate_curve_ignored_when_raise_on_error_false():
    las_raw_file = io.StringIO("""~Version Information
VERS.                     2.0: CWLS log ASCII Standard Version 2.00
WRAP.                      NO: One line per depth step
~Well Information Block
#MNEM.UNIT                 Value                       Information
#------------              -----                       -----------
STRT.M                        1670                    :START
STOP.M                        1670                    :STOP
STEP.M                         0.5                    :STEP
NULL.                     -999.25                     :NULL VALUE
~Curve Information
#MNEM   .UNIT             API CODE Curve Description
#------------             -------- -----------------
DEPTH   .M            00 001 00 00:   0  Depth
GR  .API  00 000 00 00:   6
GR  .API  00 000 00 00:   6
~A
      1670 123 123
""")
    las_file = LASRead.LASRead(las_raw_file, 'MyID', raise_on_error=False)
    assert len(las_file) == 4


def test_duplicate_curve_raises_when_raise_on_error_true():
    las_raw_file = io.StringIO("""~Version Information
VERS.                     2.0: CWLS log ASCII Standard Version 2.00
WRAP.                      NO: One line per depth step
~Well Information Block
#MNEM.UNIT                 Value                       Information
#------------              -----                       -----------
STRT.M                        1670                    :START
STOP.M                        1670                    :STOP
STEP.M                         0.5                    :STEP
NULL.                     -999.25                     :NULL VALUE
~Curve Information
#MNEM   .UNIT             API CODE Curve Description
#------------             -------- -----------------
DEPTH   .M            00 001 00 00:   0  Depth
GR  .API  00 000 00 00:   6
GR  .API  00 000 00 00:   6
~A
      1670 123
""")
    with pytest.raises(LASRead.ExceptionLASRead) as err:
        LASRead.LASRead(las_raw_file, 'MyID', raise_on_error=True)
    assert err.value.args[0] == 'Duplicate channel identity "GR"'


# Examples from LAS VERSION 2.0 September 25, 1992
# A FLOPPY DISK STANDARD FOR LOG DATA
#
# BY
#
# Canadian Well Logging Society, Floppy Disk Committee
# Suite 229,  640 - 5 Avenue, S.W.
# Calgary, Alberta  T2P 0M6
# Canada

# EXAMPLE #1 - THE LAS STANDARD IN UNWRAPPED MODE
LAS_2_EXAMPLE_1 = """~VERSION INFORMATION
 VERS.                          2.0 :   CWLS LOG ASCII STANDARD -VERSION 2.0
 WRAP.                          NO  :   ONE LINE PER DEPTH STEP
~WELL INFORMATION 
#MNEM.UNIT              DATA                       DESCRIPTION
#----- -----            ----------               -------------------------
STRT    .M              1670.0000                :START DEPTH
STOP    .M              1660.0000                :STOP DEPTH
STEP    .M              -0.1250                  :STEP 
NULL    .               -999.25                  :NULL VALUE
COMP    .       ANY OIL COMPANY INC.             :COMPANY
WELL    .       ANY ET AL 12-34-12-34            :WELL
FLD     .       WILDCAT                          :FIELD
LOC     .       12-34-12-34W5M                   :LOCATION
PROV    .       ALBERTA                          :PROVINCE 
SRVC    .       ANY LOGGING COMPANY INC.         :SERVICE COMPANY
DATE    .       13-DEC-86                        :LOG DATE
UWI     .       100123401234W500                 :UNIQUE WELL ID
~CURVE INFORMATION
#MNEM.UNIT              API CODES                   CURVE DESCRIPTION
#------------------     ------------              -------------------------
 DEPT   .M                                       :  1  DEPTH
 DT     .US/M           60 520 32 00             :  2  SONIC TRANSIT TIME
 RHOB   .K/M3           45 350 01 00             :  3  BULK DENSITY
 NPHI   .V/V            42 890 00 00             :  4  NEUTRON POROSITY
 SFLU   .OHMM           07 220 04 00             :  5  SHALLOW RESISTIVITY
 SFLA   .OHMM           07 222 01 00             :  6  SHALLOW RESISTIVITY
 ILM    .OHMM           07 120 44 00             :  7  MEDIUM RESISTIVITY
 ILD    .OHMM           07 120 46 00             :  8  DEEP RESISTIVITY
~PARAMETER INFORMATION
#MNEM.UNIT              VALUE             DESCRIPTION
#--------------     ----------------      -----------------------------------------------
 MUD    .               GEL CHEM        :   MUD TYPE
 BHT    .DEGC           35.5000         :   BOTTOM HOLE TEMPERATURE
 BS     .MM             200.0000        :   BIT SIZE
 FD     .K/M3           1000.0000       :   FLUID DENSITY
 MATR   .               SAND            :   NEUTRON MATRIX
 MDEN   .               2710.0000       :   LOGGING MATRIX DENSITY
 RMF    .OHMM           0.2160          :   MUD FILTRATE RESISTIVITY
 DFD    .K/M3           1525.0000       :   DRILL FLUID DENSITY
~OTHER
     Note: The logging tools became stuck at 625 metres causing the data 
     between 625 metres and 615 metres to be invalid.
~A  DEPTH     DT    RHOB        NPHI   SFLU    SFLA      ILM      ILD
1670.000   123.450 2550.000    0.450  123.450  123.450  110.200  105.600
1669.875   123.450 2550.000    0.450  123.450  123.450  110.200  105.600
1669.750   123.450 2550.000    0.450  123.450  123.450  110.200  105.600
"""


def test_las_2_example_1():
    las_raw_file = io.StringIO(LAS_2_EXAMPLE_1)
    las_file = LASRead.LASRead(las_raw_file, 'Example 1', raise_on_error=True)
    assert len(las_file) == 6
    assert [section.type for section in las_file.generate_sections()] == ['V', 'W', 'C', 'P', 'O', 'A']
    assert las_file.number_of_frames() == 3
    assert las_file.number_of_data_points() == 24


# EXAMPLE #2 - ILLUSTRATING THE  LAS STANDARD WITH MINIMUM HEADER REQUIREMENTS IN UNWRAPPED MODE.
LAS_2_EXAMPLE_2 = """~V
VERS.                   2.0   :   CWLS log ASCII Standard -VERSION 2.0
WRAP.                   NO    :   One line per depth step
~W
STRT.M                          635.0000        :START DEPTH
STOP.M                          400.0000        :STOP DEPTH
STEP.M                          -0.1250         :STEP 
NULL.                           -999.25         :NULL VALUE
COMP.           ANY OIL COMPANY INC.            :COMPANY
WELL.           ANY ET AL 12-34-12-34           :WELL
FLD .           WILDCAT                         :FIELD
LOC .           12-34-12-34W5M                  :LOCATION
PROV.           ALBERTA                         :PROVINCE 
SRVC.           ANY LOGGING COMPANY INC.        :SERVICE COMPANY
DATE.           13-DEC-86                       :LOG DATE
UWI .           100123401234W500                :UNIQUE WELL ID
~C
DEPT    .M                              :   DEPTH
RHOB    .K/M3                           :   BULK DENSITY
NPHI    .VOL/VOL                        :   NEUTRON POROSITY - SANDSTONE
MSFL    .OHMM                           :   Rxo RESISTIVITY
SFLA    .OHMM                           :   SHALLOW RESISTIVITY
ILM     .OHMM                           :   MEDIUM RESISTIVITY
ILD     .OHMM                           :   DEEP RESISTIVITY
SP      .MV                             :   SPONTANEOUS POTENTIAL
~A
 635.0000     2256.0000   0.4033  22.0781 22.0781 20.3438 3.6660 123.4
 634.8750     2256.0000   0.4033  22.0781 22.0781 20.3438 3.6660 123.4
"""


def test_las_2_example_2():
    las_raw_file = io.StringIO(LAS_2_EXAMPLE_2)
    las_file = LASRead.LASRead(las_raw_file, 'Example 2', raise_on_error=True)
    assert len(las_file) == 4
    assert [section.type for section in las_file.generate_sections()] == ['V', 'W', 'C', 'A']
    assert las_file.number_of_frames() == 2
    assert las_file.number_of_data_points() == 16


# EXAMPLE #3 - ILLUSTRATING THE WRAPPED VERSION OF THE LAS STANDARD
LAS_2_EXAMPLE_3 = """~VERSION INFORMATION
 VERS.                 2.0      :   CWLS log ASCII Standard -VERSION 2.0
 WRAP.                 YES      :   Multiple lines per depth step
~WELL INFORMATION 
#MNEM.UNIT                DATA                         DESCRIPTION
#----- -----           ----------           -----------------------------
STRT    .M               910.0000               :START DEPTH
STOP    .M               909.5000               :STOP DEPTH
STEP    .M               -0.1250                :STEP 
NULL    .                -999.25                :NULL VALUE
COMP    .       ANY OIL COMPANY INC.            :COMPANY
WELL    .       ANY ET AL 12-34-12-34           :WELL
FLD     .       WILDCAT                         :FIELD
LOC     .       12-34-12-34W5M                  :LOCATION
PROV    .       ALBERTA                         :PROVINCE 
SRVC    .       ANY LOGGING COMPANY INC.        :SERVICE COMPANY
SON     .       142085                          :SERVICE ORDER NUMBER
DATE    .       13-DEC-86                       :LOG DATE
UWI     .       100123401234W500                :UNIQUE WELL ID
~CURVE INFORMATION
#MNEM.UNIT                                    Curve Description
#---------                               ------------------------------
 DEPT   .M                              :    Depth
 DT     .US/M                           :  1 Sonic Travel Time
 RHOB   .K/M                            :  2 Density-Bulk Density
 NPHI   .V/V                            :  3 Porosity -Neutron
 RX0    .OHMM                           :  4 Resistivity -Rxo
 RESS   .OHMM                           :  5 Resistivity -Shallow
 RESM   .OHMM                           :  6 Resistivity -Medium
 RESD   .OHMM                           :  7 Resistivity -Deep
 SP     .MV                             :  8 Spon. Potential
 GR     .GAPI                           :  9 Gamma Ray
 CALI   .MM                             : 10 Caliper
 DRHO   .K/M3                           : 11 Delta-Rho
 EATT   .DBM                            : 12 EPT Attenuation
 TPL    .NS/M                           : 13 TP -EPT
 PEF    .                               : 14 PhotoElectric Factor
 FFI    .V/V                            : 15 Porosity -NML FFI
 DCAL   .MM                             : 16 Caliper-Differential
 RHGF   .K/M3                           : 17 Density-Formation
 RHGA   .K/M3                           : 18 Density-Apparent
 SPBL   .MV                             : 19 Baselined SP
 GRC    .GAPI                           : 20 Gamma Ray BHC
 PHIA   .V/V                            : 21 Porosity -Apparent
 PHID   .V/V                            : 22 Porosity -Density
 PHIE   .V/V                            : 23 Porosity -Effective
 PHIN   .V/V                            : 24 Porosity -Neut BHC
 PHIC   .V/V                            : 25 Porosity -Total HCC
 R0     .OHMM                           : 26 Ro
 RWA    .OHMM                           : 27 Rfa
 SW     .                               : 28 Sw -Effective
 MSI    .                               : 29 Sh Idx -Min
 BVW    .                               : 30 BVW
 FGAS   .                               : 31 Flag -Gas Index
 PIDX   .                               : 32 Prod Idx
 FBH    .                               : 33 Flag -Bad Hole
 FHCC   .                               : 34 Flag -HC Correction
 LSWB   .                               : 35 Flag -Limit SWB
~A Log data section
910.000000
  -999.2500  2692.7075     0.3140    19.4086    19.4086    13.1709    12.2681
    -1.5010    96.5306   204.7177    30.5822  -999.2500  -999.2500     3.2515
  -999.2500     4.7177  3025.0264  3025.0264    -1.5010    93.1378     0.1641
     0.0101     0.1641     0.3140     0.1641    11.1397     0.3304     0.9529
     0.0000     0.1564     0.0000    11.1397     0.0000     0.0000     0.0000
909.875000
  -999.2500  2712.6460     0.2886    23.3987    23.3987    13.6129    12.4744
    -1.4720    90.2803   203.1093    18.7566  -999.2500  -999.2500     3.7058
  -999.2500     3.1093  3004.6050  3004.6050    -1.4720    86.9078     0.1456
    -0.0015     0.1456     0.2886     0.1456    14.1428     0.2646     1.0000
     0.0000     0.1456     0.0000    14.1428     0.0000     0.0000     0.0000
909.750000
  -999.2500  2692.8137     0.2730    22.5909    22.5909    13.6821    12.6146
    -1.4804    89.8492   201.9287     3.1551  -999.2500  -999.2500     4.3124
  -999.2500     1.9287  2976.4451  2976.4451    -1.4804    86.3465     0.1435
     0.0101     0.1435     0.2730     0.1435    14.5674     0.2598     1.0000
     0.0000     0.1435     0.0000    14.5674     0.0000     0.0000     0.0000
909.625000
  -999.2500  2644.3650     0.2765    18.4831    18.4831    13.4159    12.6900
    -1.5010    93.3999   201.5826    -6.5861  -999.2500  -999.2500     4.3822
  -999.2500     1.5826  2955.3528  2955.3528    -1.5010    89.7142     0.1590
     0.0384     0.1590     0.2765     0.1590    11.8600     0.3210     0.9667
     0.0000     0.1538     0.0000    11.8600     0.0000     0.0000     0.0000
909.500000
  -999.2500  2586.2822     0.2996    13.9187    13.9187    12.9195    12.7016
    -1.4916    98.1214   201.7126    -4.5574  -999.2500  -999.2500     3.5967
  -999.2500     1.7126  2953.5940  2953.5940    -1.4916    94.2670     0.1880
     0.0723     0.1880     0.2996     0.1880     8.4863     0.4490     0.8174
     0.0000     0.1537     0.0000     8.4863     0.0000     0.0000     0.0000
"""


def test_las_2_example_3():
    las_raw_file = io.StringIO(LAS_2_EXAMPLE_3)
    las_file = LASRead.LASRead(las_raw_file, 'Example 3', raise_on_error=True)
    assert len(las_file) == 4
    assert [section.type for section in las_file.generate_sections()] == ['V', 'W', 'C', 'A']
    assert las_file.number_of_frames() == 5
    assert las_file.number_of_data_points() == 180


# EXAMPLE # 4  LAS FILE FOR TIME BASED DATA
LAS_2_EXAMPLE_4 = """~VERSION INFORMATION
 VERS.                       2.0    :   CWLS LOG ASCII STANDARD -VERSION 2.0
 WRAP.                       NO     :   ONE LINE PER TIME STEP
#
~WELL INFORMATION 
STRT    .S      0.0000                           :START TIME 
STOP    .S      39.9000                          :STOP TIME
STEP    .S      0.3000                           :STEP
NULL    .       -999.25                          :NULL VALUE
COMP    .       ANY OIL COMPANY INC.             :COMPANY
WELL    .       ANY ET 12-34-12-34               :WELL
FLD     .       WILDCAT                          :FIELD
LOC     .       12-34-12-34W5                    :LOCATION
PROV    .       ALBERTA                          :PROVINCE 
SRVC    .       ANY LOGGING COMPANY INC.         :SERVICE COMPANY
DATE    .       13-DEC-86                        :LOG DATE
UWI     .       100123401234W500                 :UNIQUE WELL ID
#
~CURVE INFORMATION
 ETIM   .S               :  1  ELAPSED TIME
 BFR1   .OHMM            :  2  SINGLE PROBE 1 RESISTIVITY
 BSG1   .PSIG            :  3  SINGLE PROBE 1 STRAIN GAUGE PRESSURE 
#
~PARAMETER INFORMATION
MRT    .DEGC            67.0    : BOTTOM HOLE TEMPERATURE
GDEPT  .M               3456.5  : GAUGE DEPTH
DFD    .KG/M3           1000.0  : MUD WEIGHT
#
~A
0.0000          0.2125          16564.1445
0.3000          0.2125          16564.1445
0.6000          0.2125          16564.2421
0.9000          0.2125          16564.0434
1.2000          0.2125          16564.0430
1.5000          0.2125          16564.0435
"""


def test_las_2_example_4():
    las_raw_file = io.StringIO(LAS_2_EXAMPLE_4)
    las_file = LASRead.LASRead(las_raw_file, 'Example 4', raise_on_error=True)
    assert len(las_file) == 5
    assert [section.type for section in las_file.generate_sections()] == ['V', 'W', 'C', 'P', 'A']
    assert las_file.number_of_frames() == 6
    assert las_file.number_of_data_points() == 18
