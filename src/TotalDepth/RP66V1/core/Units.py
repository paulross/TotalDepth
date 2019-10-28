"""
Handles RP66V1 units.

Currently we only support a limited and crude set of X axis units.

Full unit coverage is a fairly big job.

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

"""
import typing


_CONVERSION_FACTORS = {
    (b'0.1 in', b'm'): 0.3048 / 120,
    # (b'in', b'm'): 0.3048 / 12,
    # (b'ft', b'm'): 0.3048,
}


def conversion_factor(units_from: bytes, units_to: bytes) -> typing.Union[int, float]:
    """Really dumb way to get a conversion factor."""
    try:
        return _CONVERSION_FACTORS[(units_from, units_to)]
    except KeyError:
        return 1 / _CONVERSION_FACTORS[(units_to, units_from)]


# import collections
# import re
# import typing
#
#
# # Token = collections.namedtuple('Token', ['type', 'value', 'line', 'column'])
# class Token(typing.NamedTuple):
#     type: str
#     value: str
#     line: int
#     column:int
#
#
# def tokenise_units(code: str) -> typing.Sequence[Token]:
#     # See also [RP66V1 Appendix B, B.27 Code UNITS: Units Expression]
#     token_specification = [
#         ('BinaryPrefix',   r'Ki|Mi|Gi|Ti|Pi|Ei|Zi|Yi'),
#         ('SiPrefix',   r'y|z|a|f|p|n|u|m|c|d|da|h|k|M|G|T|P|E|Z|Y'),
#         ('NonZeroDigit', r'1|2|3|4|5|6|7|8|9'),
#         ('Digit', r'0|1|2|3|4|5|6|7|8|9'),
#         ('GtOneDigit', r'2|3|4|5|6|7|8|9'),
#         ('E', r'E'),
#         ('Letter', r'[A-Za-z]'),
#         ('COMMA', r','),
#         ('AT', r'\@'),
#         ('SpecialAtom', r'%|inH2O|cmH2O'),
#         ('PARENLEFT', r'\('),
#         ('PARENRIGHT', r'\)'),
#         ('MULTIPLY', r'\*'),
#         ('DIVIDE', r'/'),
#         ('BLANK', r' '),
#         ('DOT', r'.'),
#         ('HYPHEN', r'-'),
#         ('NEWLINE',  r'\n'),
#         ('ID',       r'[A-Za-z]+'),
#         ('MISSMATCH', r'.'),
#     ]
#     tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
#     line_num = 1
#     line_start = 0
#     for mo in re.finditer(tok_regex, code):
#         kind = mo.lastgroup
#         value = mo.group()
#         column = mo.start() - line_start
#         if kind == 'NUMBER':
#             value = float(value) if '.' in value else int(value)
#         # elif kind == 'ID' and value in keywords:
#         #     kind = value
#         # elif kind == 'NEWLINE':
#         #     line_start = mo.end()
#         #     line_num += 1
#         #     continue
#         # elif kind == 'SKIP':
#         #     continue
#         elif kind == 'MISMATCH':
#             raise RuntimeError(f'{value!r} unexpected on line {line_num}')
#         yield Token(kind, value, line_num, column)
#
# for token in tokenise_units('0.1m/s2'):
# for token in tokenise_units('627264E5/15499969 m2'):
#     print(token)

