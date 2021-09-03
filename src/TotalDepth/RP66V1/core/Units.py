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
"""
Handles RP66V1 units.

There are two approaches:

Standard Based Parser
=====================

Formal but slow and does not appreciate that there are a load of non-standard implementations out there.

References:
    [RP66V1 Appendix b, B.27 Code UNITS: Units Expression]
    ["Energistics Unit Symbol Grammar Specification" Section 2.2 Unit Symbol Construction Grammar]


.. code-block:: console

    UnitSymbol ::= [ Multiplier ' ' ] FactorExpression .

    FactorExpression ::= OneOrMore |
        ( '1' | OneOrMore | Division ) '/' (

    Division ::= '(' OneOrMore '/' Divisor ')'

    OneOrMore ::= Factor | Factors .

    Divisor ::= Factor | '(' Factors ')' .

    Factors ::= Factor '.' Factor { '.' Factor

    Factor ::= UnitComponent [ Exponent ] .

    UnitComponent ::= PrefixedAtom | Atom | SpecialAtom [ Qualifier ] .

    PrefixedAtom ::= ( SIPrefix | BinaryPrefix ) Atom .

    Atom ::= Letter { Letter } [ Qualifier ] .

    SpecialAtom ::= '%' | 'inH2O' | 'cmH2O' .

    Qualifier ::= '[' [ AT ] QualPart { COMMA QualPart } ']' .

    AT ::= '@' .

    COMMA ::= ',' .

    QualPart ::= LetterOrDigit { LetterOrDigit

    LetterOrDigit ::= Letter | Digit .

    Letter ::= E | LTTR .

    LTTR ::= 'A'|'B'|'C' | 'D' | 'L' | 'M' | 'N' | 'O' | 'W' | 'X' | 'Y' | 'Z' | 'a' | 'b' | 'c' | 'd' | 'l' | 'm' | 'n'
        | 'o' | 'w' | 'x' | 'y' | 'z' . 'P' | 'e' | 'p' | } .
        } .
        'F'|'G'|'H' 'Q' | 'R' | 'S'
        'f' | 'g' | 'h'
        'q' | 'r' | 's'
        | 'I' | 'J' | 'K' |
        | 'T' | 'U' | 'V' |
        | 'i' | 'j' | 'k' |
        | 't' | 'u' | 'v' |

    Exponent ::= GtOneDigit | '(' ( NonZeroInt '.' FractionalPart | '0' '.' FractionalPart ) ')' .

    Multiplier ::= '1' E PowerOfTen [ '/' GtOneInt ] | '1' '/' GtOneInt |
        Number [ E PowerOfTen ][ '/' GtOneInt ] .

    E ::= 'E' .

    PowerOfTen ::= [ '-' ] GtOneInt .

    Number ::= GtOneInt |
               NonZeroInt '.' FractionalPart | '0' '.' FractionalPart .

    GtOneInt ::= GtOneDigit | NonZeroDigit Digit { Digit } .

    FractionalPart ::= { Digit } NonZeroDigit .

    NonZeroInt ::= NonZeroDigit { Digit } .

    Digit ::= '0' | NonZeroDigit .

    GtOneDigit ::= '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' .

    NonZeroDigit ::= '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' .

    SIPrefix ::= 'y' | 'z' | 'a' | 'f' | 'p' | 'n' | 'u' | 'm' | 'c' | 'd' |
    'da' | 'h' | 'k' | 'M' | 'G' | 'T' | 'P' | 'E' | 'Z' | 'Y' .

    BinaryPrefix ::= 'Ki' | 'Mi' | 'Gi' | 'Ti' | 'Pi' | 'Ei' | 'Zi' | 'Yi' .

Something like this::

    import re
    import typing


    # Token = collections.namedtuple('Token', ['type', 'value', 'line', 'column'])
    class Token(typing.NamedTuple):
        type: str
        value: str
        line: int
        column:int


    def tokenise_units(code: str) -> typing.Sequence[Token]:
        # See also [RP66V1 Appendix B, B.27 Code UNITS: Units Expression]
        token_specification = [
            ('BinaryPrefix',   r'Ki|Mi|Gi|Ti|Pi|Ei|Zi|Yi'),
            ('SiPrefix',   r'y|z|a|f|p|n|u|m|c|d|da|h|k|M|G|T|P|E|Z|Y'),
            ('NonZeroDigit', r'1|2|3|4|5|6|7|8|9'),
            ('Digit', r'0|1|2|3|4|5|6|7|8|9'),
            ('GtOneDigit', r'2|3|4|5|6|7|8|9'),
            ('E', r'E'),
            ('Letter', r'[A-Za-z]'),
            ('COMMA', r','),
            ('AT', r'\@'),
            ('SpecialAtom', r'%|inH2O|cmH2O'),
            ('PARENLEFT', r'\('),
            ('PARENRIGHT', r'\)'),
            ('MULTIPLY', r'\*'),
            ('DIVIDE', r'/'),
            ('BLANK', r' '),
            ('DOT', r'.'),
            ('HYPHEN', r'-'),
            ('NEWLINE',  r'\\n'),
            ('ID',       r'[A-Za-z]+'),
            ('MISSMATCH', r'.'),
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        line_num = 1
        line_start = 0
        for mo in re.finditer(tok_regex, code):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start
            if kind == 'NUMBER':
                value = float(value) if '.' in value else int(value)
            # elif kind == 'ID' and value in keywords:
            #     kind = value
            # elif kind == 'NEWLINE':
            #     line_start = mo.end()
            #     line_num += 1
            #     continue
            # elif kind == 'SKIP':
            #     continue
            elif kind == 'MISMATCH':
                raise RuntimeError(f'{value!r} unexpected on line {line_num}')
            yield Token(kind, value, line_num, column)

    for token in tokenise_units('0.1m/s2'):
    for token in tokenise_units('627264E5/15499969 m2'):
        print(token)


This is likely to be slow, some pre-processing may help.

Lookup
======

This uses online or offline data structures.
The primary source is Schlumberger's Oilfield Services Data Dictionary (OSDD): https://www.apps.slb.com/cmd/units.aspx
It is quick and largely respects existing implementations.

Other data providers (by PRODUCER-CODE) may have alternate mappings that can be put into
PRODUCER_CODE_MAPPING_OF_UNIT_CODE.

See src/TotalDepth/RP66V1/util/XMLReadUnits.py for some analysis.

"""
import functools
import typing

from TotalDepth import ExceptionTotalDepth
from TotalDepth.common import units


class ExceptionRP66V1Units(ExceptionTotalDepth):
    """Base class exception for this module."""
    pass


#: This permits different producer codes to map into Schlumberger's Oilfield Services Data Dictionary (OSDD).
#: This is just an example, see `src/TotalDepth/RP66V1/util/XMLReadUnits.py` for some analysis of test files.
PRODUCER_CODE_MAPPING_OF_UNIT_CODE: typing.Dict[int, typing.Dict[bytes, bytes]] = {
    280: {
        b'ltrs' : b'dm3',
        b'sec' : b'SEC',
        b'gapi' : b'GAPI',
    },
}


def convert(value: float, unit_from: bytes, unit_to: bytes, producer_code: int = 0) -> float:
    """Converts a value from one unit to another.
    This uses TotalDepth.common.units with an additional producer code mapping.

    Examples::

        Code    Name                Standard Form   Dimension   Scale               Offset
        DEGC    'degree celsius'    degC            Temperature 1                   -273.15
        DEGF    'degree fahrenheit' degF            Temperature 0.555555555555556   -459.67

    So conversion from, say DEGC to DEGF is::

        ((value - DEGC.offset) * DEGC.scale) / DEGF.scale + DEGF.offset

        ((0.0 - -273.15) * 1.0) / 0.555555555555556 + -459.67 == 32.0
    """
    if producer_code > 0:
        try:
            producer_map = PRODUCER_CODE_MAPPING_OF_UNIT_CODE[producer_code]
        except KeyError as err:
            raise ExceptionRP66V1Units(f'Can not lookup PRODUCER-CODE with error: {err}')
        else:
            if unit_from in producer_map:
                unit_from = producer_map[unit_from]
            if unit_to in producer_map:
                unit_to = producer_map[unit_to]
    try:
        _unit_from = units.slb_units(unit_from.decode('ascii'))
        _unit_to = units.slb_units(unit_to.decode('ascii'))
    except KeyError as err:
        raise ExceptionRP66V1Units(f'Can not lookup units with error: {err}')
    try:
        return units.convert(value, _unit_from, _unit_to)
    except units.ExceptionUnitsDimension as err:
        raise ExceptionRP66V1Units(f'Can not convert units with error: {err}')


def convert_function(unit_from: units.Unit, unit_to: units.Unit, producer_code: int = 0) -> typing.Callable:
    """Return a partial function to convert from one RP66V1 units to another."""
    return functools.partial(convert, unit_from=unit_from, unit_to=unit_to, producer_code=producer_code)
