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
Support for EBCDIC character encoding.

References:

https://en.wikipedia.org/wiki/EBCDIC

https://www.ibm.com/support/knowledgecenter/SSGH4D_16.1.0/com.ibm.xlf161.aix.doc/language_ref/asciit.html

From: https://www.ibm.com/support/knowledgecenter/ssw_ibm_i_71/rzaat/rzaate.htm

"EBCDIC single-byte encoding scheme
An 8-bit-per-byte structure. The EBCDIC single-byte structure has a valid code-point range for 00 to FF
Control characters have a range from 00 to 3F.
Graphic characters have a range from 41 to FE.
The space character is 40."
"""
import string
import typing

#: EBCDIC all character points.
#: From https://en.wikipedia.org/wiki/EBCDIC
EBCDIC_ALL = (
    set(range(0x0, 0x30))
    |
    set(range(0x32, 0x3e))
    |
    set(range(0x3f, 0x41))
    |
    set(range(0x4a, 0x51))
    |
    set(range(0x5a, 0x62))
    |
    set(range(0x6a, 0x70))
    |
    set(range(0x79, 0x80))
    |
    set(range(0x81, 0x8a))
    |
    {0x8f}
    |
    set(range(0x91, 0x9a))
    |
    set(range(0xa1, 0xaa))
    |
    {0xb0, 0xba, 0xbb}
    |
    set(range(0xc0, 0xca))
    |
    set(range(0xd0, 0xda))
    |
    set(range(0xe0, 0xea))
    |
    set(range(0xf0, 0xfa))
    |
    {0xff}
)

# #: Lower bound <=
# EBCDIC_PRINTABLE_ORDINAL_LOW = 0x40
# #: Upper bound <
# EBCDIC_PRINTABLE_ORDINAL_HIGH = 0xfa

# EBCDIC_PRINTABLE_EXTRA = {
#     5,  # Tab, ASCII 9.
#     240, 241, 242, 243, 244, 245, 246, 247, 248, 249, # 0 to 9
#     250,  # Vertical line '|'
# }
# EBCDIC_PRINTABLE = set(range(EBCDIC_PRINTABLE_ORDINAL_LOW, EBCDIC_PRINTABLE_ORDINAL_HIGH)) & EBCDIC_ALL & EBCDIC_PRINTABLE_EXTRA

#: Printable range. This is obtained by using cp500::
#:
#:      string.printable.encode('cp500')
#:
#: Which gives::
#:
#:  EBCDIC_PRINTABLE = {5, 11, 12, 13, 37, 64, 74, 75, 76, 77, 78, 79, 80, 90, 91, 92, 93, 94, 95, 96, 97, 107, 108, 109,
#:  110, 111, 121, 122, 123, 124, 125, 126, 127, 129, 130, 131, 132, 133, 134, 135, 136, 137, 145, 146,
#:  147, 148, 149, 150, 151, 152, 153, 161, 162, 163, 164, 165, 166, 167, 168, 169, 187, 192, 193, 194,
#:  195, 196, 197, 198, 199, 200, 201, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 224, 226, 227,
#:  228, 229, 230, 231, 232, 233, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249}
EBCDIC_PRINTABLE = set(string.printable.encode('cp500'))


class EbcdicAsciiTableEntry(typing.NamedTuple):
    """A single entry in the EBCDIC table."""
    decimal_str: str
    hex_str: str
    ctrl_char: str
    ascii: str
    ascii_meaning: str
    ebcdic: str
    ebcdic_meaning: str

    @property
    def value(self) -> int:
        """Returns the decimal value of the entry."""
        return int(self.decimal_str)

    # @property
    # def hex(self) -> int:
    #     return int(f'0x{self.hex_str}')

    @property
    def is_ctrl(self) -> bool:
        """Returns True if this is a control character, False otherwise."""
        return self.ctrl_char != ''

    @property
    def ctrl_symbol(self) -> str:
        """The single control character or ''. For example decimal value 3 returns 'C'."""
        return self.ctrl_char[len('Ctrl-'):]

    @property
    def ebcdic_printable(self) -> bool:
        """Returns True if this is a printable character, False otherwise."""
        return self.value in EBCDIC_PRINTABLE


#: The explanation of each character.
#: ('Decimal Value', 'Hex Value', 'Control Character', 'ASCII Symbol', 'Meaning', 'EBCDIC Symbol', 'Meaning'),
#:
#: From: https://www.ibm.com/support/knowledgecenter/SSGH4D_16.1.0/com.ibm.xlf161.aix.doc/language_ref/asciit.html
EBCDIC_ASCII_TABLE = {
    int(row[0]): EbcdicAsciiTableEntry(*row) for row in [
        ('0', '00', 'Ctrl-@', 'NUL', 'null', 'NUL', 'null'),
        ('1', '01', 'Ctrl-A', 'SOH', 'start of heading', 'SOH', 'start of heading'),
        ('2', '02', 'Ctrl-B', 'STX', 'start of text', 'STX', 'start of text'),
        ('3', '03', 'Ctrl-C', 'ETX', 'end of text', 'ETX', 'end of text'),
        ('4', '04', 'Ctrl-D', 'EOT', 'end of transmission', 'SEL', 'select'),
        ('5', '05', 'Ctrl-E', 'ENQ', 'enquiry', 'HT', 'horizontal tab'),
        ('6', '06', 'Ctrl-F', 'ACK', 'acknowledge', 'RNL', 'required new-line'),
        ('7', '07', 'Ctrl-G', 'BEL', 'bell', 'DEL', 'delete'),
        ('8', '08', 'Ctrl-H', 'BS', 'backspace', 'GE', 'graphic escape'),
        ('9', '09', 'Ctrl-I', 'HT', 'horizontal tab', 'SPS', 'superscript'),
        ('10', '0A', 'Ctrl-J', 'LF', 'line feed', 'RPT', 'repeat'),
        ('11', '0B', 'Ctrl-K', 'VT', 'vertical tab', 'VT', 'vertical tab'),
        ('12', '0C', 'Ctrl-L', 'FF', 'form feed', 'FF', 'form feed'),
        ('13', '0D', 'Ctrl-M', 'CR', 'carriage return', 'CR', 'carriage return'),
        ('14', '0E', 'Ctrl-N', 'SO', 'shift out', 'SO', 'shift out'),
        ('15', '0F', 'Ctrl-O', 'SI', 'shift in', 'SI', 'shift in'),
        ('16', '10', 'Ctrl-P', 'DLE', 'data link escape', 'DLE', 'data link escape'),
        ('17', '11', 'Ctrl-Q', 'DC1', 'device control 1', 'DC1', 'device control 1'),
        ('18', '12', 'Ctrl-R', 'DC2', 'device control 2', 'DC2', 'device control 2'),
        ('19', '13', 'Ctrl-S', 'DC3', 'device control 3', 'DC3', 'device control 3'),
        ('20', '14', 'Ctrl-T', 'DC4', 'device control 4', 'RES/ENP', 'restore/enable presentation'),
        ('21', '15', 'Ctrl-U', 'NAK', 'negative acknowledge', 'NL', 'new-line'),
        ('22', '16', 'Ctrl-V', 'SYN', 'synchronous idle', 'BS', 'backspace'),
        ('23', '17', 'Ctrl-W', 'ETB', 'end of transmission block', 'POC', 'program-operator communications'),
        ('24', '18', 'Ctrl-X', 'CAN', 'cancel', 'CAN', 'cancel'),
        ('25', '19', 'Ctrl-Y', 'EM', 'end of medium', 'EM', 'end of medium'),
        ('26', '1A', 'Ctrl-Z', 'SUB', 'substitute', 'UBS', 'unit backspace'),
        ('27', '1B', 'Ctrl-[', 'ESC', 'escape', 'CU1', 'customer use 1'),
        ('28', '1C', 'Ctrl-\\', 'FS', 'file separator', 'IFS', 'interchange file separator'),
        ('29', '1D', 'Ctrl-]', 'GS', 'group separator', 'IGS', 'interchange group separator'),
        ('30', '1E', 'Ctrl-∧', 'RS', 'record separator', 'IRS', 'interchange record separator'),
        ('31', '1F', 'Ctrl-_', 'US', 'unit separator', 'IUS/ITB',
         'interchange unit separator / intermediate transmission block'),
        ('32', '20', '', 'SP', 'space', 'DS', 'digit select'),
        ('33', '21', '', '!', 'exclamation mark', 'SOS', 'start of significance'),
        ('34', '22', '', '"', 'straight double quotation mark', 'FS', 'field separator'),
        ('35', '23', '', '#', 'number sign', 'WUS', 'word underscore'),
        ('36', '24', '', '$', 'dollar sign', 'BYP/INP', 'bypass/inhibit presentation'),
        ('37', '25', '', '%', 'percent sign', 'LF', 'line feed'),
        ('38', '26', '', '&', 'ampersand', 'ETB', 'end of transmission block'),
        ('39', '27', '', '\'', 'apostrophe', 'ESC', 'escape'),
        ('40', '28', '', '(', 'left parenthesis', 'SA', 'set attribute'),
        ('41', '29', '', ')', 'right parenthesis', '', ''),
        ('42', '2A', '', '*', 'asterisk', 'SM/SW', 'set model switch'),
        ('43', '2B', '', '+', 'addition sign', 'CSP', 'control sequence prefix'),
        ('44', '2C', '', ',', 'comma', 'MFA', 'modify field attribute'),
        ('45', '2D', '', '-', 'subtraction sign', 'ENQ', 'enquiry'),
        ('46', '2E', '', '.', 'period', 'ACK', 'acknowledge'),
        ('47', '2F', '', '/', 'right slash', 'BEL', 'bell'),
        ('48', '30', '', '0', '', '', ''),
        ('49', '31', '', '1', '', '', ''),
        ('50', '32', '', '2', '', 'SYN', 'synchronous idle'),
        ('51', '33', '', '3', '', 'IR', 'index return'),
        ('52', '34', '', '4', '', 'PP', 'presentation position'),
        ('53', '35', '', '5', '', 'TRN', ''),
        ('54', '36', '', '6', '', 'NBS', 'numeric backspace'),
        ('55', '37', '', '7', '', 'EOT', 'end of transmission'),
        ('56', '38', '', '8', '', 'SBS', 'subscript'),
        ('57', '39', '', '9', '', 'IT', 'indent tab'),
        ('58', '3A', '', ':', 'colon', 'RFF', 'required form feed'),
        ('59', '3B', '', ';', 'semicolon', 'CU3', 'customer use 3'),
        ('60', '3C', '', '<', 'less than', 'DC4', 'device control 4'),
        ('61', '3D', '', '=', 'equal', 'NAK', 'negative acknowledge'),
        ('62', '3E', '', '>', 'greater than', '', ''),
        ('63', '3F', '', '?', 'question mark', 'SUB', 'substitute'),
        ('64', '40', '', '@', 'at symbol', 'SP', 'space'),
        ('65', '41', '', 'A', '', '', ''),
        ('66', '42', '', 'B', '', '', ''),
        ('67', '43', '', 'C', '', '', ''),
        ('68', '44', '', 'D', '', '', ''),
        ('69', '45', '', 'E', '', '', ''),
        ('70', '46', '', 'F', '', '', ''),
        ('71', '47', '', 'G', '', '', ''),
        ('72', '48', '', 'H', '', '', ''),
        ('73', '49', '', 'I', '', '', ''),
        ('74', '4A', '', 'J', '', '¢', 'cent'),
        ('75', '4B', '', 'K', '', '.', 'period'),
        ('76', '4C', '', 'L', '', '<', 'less than'),
        ('77', '4D', '', 'M', '', '(', 'left parenthesis'),
        ('78', '4E', '', 'N', '', '+', 'addition sign'),
        ('79', '4F', '', 'O', '', '|', 'logical or'),
        ('80', '50', '', 'P', '', '&', 'ampersand'),
        ('81', '51', '', 'Q', '', '', ''),
        ('82', '52', '', 'R', '', '', ''),
        ('83', '53', '', 'S', '', '', ''),
        ('84', '54', '', 'T', '', '', ''),
        ('85', '55', '', 'U', '', '', ''),
        ('86', '56', '', 'V', '', '', ''),
        ('87', '57', '', 'W', '', '', ''),
        ('88', '58', '', 'X', '', '', ''),
        ('89', '59', '', 'Y', '', '', ''),
        ('90', '5A', '', 'Z', '', '!', 'exclamation mark'),
        ('91', '5B', '', '[', 'left bracket', '$', 'dollar sign'),
        ('92', '5C', '', '\\', 'left slash', '*', 'asterisk'),
        ('93', '5D', '', ']', 'right bracket', ')', 'right parenthesis'),
        ('94', '5E', '', '^', 'hat, circumflex', ';', 'semicolon'),
        ('95', '5F', '', '_', 'underscore', '¬', 'logical not'),
        ('96', '60', '', 'ˋ', 'grave', '-', 'subtraction sign'),
        ('97', '61', '', 'a', '', '/', 'right slash'),
        ('98', '62', '', 'b', '', '', ''),
        ('99', '63', '', 'c', '', '', ''),
        ('100', '64', '', 'd', '', '', ''),
        ('101', '65', '', 'e', '', '', ''),
        ('102', '66', '', 'f', '', '', ''),
        ('103', '67', '', 'g', '', '', ''),
        ('104', '68', '', 'h', '', '', ''),
        ('105', '69', '', 'i', '', '', ''),
        ('106', '6A', '', 'j', '', '|', 'split vertical bar'),
        ('107', '6B', '', 'k', '', ',', 'comma'),
        ('108', '6C', '', 'l', '', '%', 'percent sign'),
        ('109', '6D', '', 'm', '', '_', 'underscore'),
        ('110', '6E', '', 'n', '', '>', 'greater than'),
        ('111', '6F', '', 'o', '', '?', 'question mark'),
        ('112', '70', '', 'p', '', '', ''),
        ('113', '71', '', 'q', '', '', ''),
        ('114', '72', '', 'r', '', '', ''),
        ('115', '73', '', 's', '', '', ''),
        ('116', '74', '', 't', '', '', ''),
        ('117', '75', '', 'u', '', '', ''),
        ('118', '76', '', 'v', '', '', ''),
        ('119', '77', '', 'w', '', '', ''),
        ('120', '78', '', 'x', '', '', ''),
        ('121', '79', '', 'y', '', 'ˋ', 'grave'),
        ('122', '7A', '', 'z', '', ':', 'colon'),
        ('123', '7B', '', '{', 'left brace', '#', 'numbersign'),
        ('124', '7C', '', '|', 'logical or', '@', 'at symbol'),
        ('125', '7D', '', '}', 'right brace', '\'', 'apostrophe'),
        ('126', '7E', '', '~', 'similar, tilde', '=', 'equal'),
        ('127', '7F', '', 'DEL', 'delete', '"', 'straight double quotation mark'),
        ('128', '80', '', '', '', '', ''),
        ('129', '81', '', '', '', 'a', ''),
        ('130', '82', '', '', '', 'b', ''),
        ('131', '83', '', '', '', 'c', ''),
        ('132', '84', '', '', '', 'd', ''),
        ('133', '85', '', '', '', 'e', ''),
        ('134', '86', '', '', '', 'f', ''),
        ('135', '87', '', '', '', 'g', ''),
        ('136', '88', '', '', '', 'h', ''),
        ('137', '89', '', '', '', 'i', ''),
        ('138', '8A', '', '', '', '', ''),
        ('139', '8B', '', '', '', '', ''),
        ('140', '8C', '', '', '', '', ''),
        ('141', '8D', '', '', '', '', ''),
        ('142', '8E', '', '', '', '', ''),
        ('143', '8F', '', '', '', '', ''),
        ('144', '90', '', '', '', '', ''),
        ('145', '91', '', '', '', 'j', ''),
        ('146', '92', '', '', '', 'k', ''),
        ('147', '93', '', '', '', 'l', ''),
        ('148', '94', '', '', '', 'm', ''),
        ('149', '95', '', '', '', 'n', ''),
        ('150', '96', '', '', '', 'o', ''),
        ('151', '97', '', '', '', 'p', ''),
        ('152', '98', '', '', '', 'q', ''),
        ('153', '99', '', '', '', 'r', ''),
        ('154', '9A', '', '', '', '', ''),
        ('155', '9B', '', '', '', '', ''),
        ('156', '9C', '', '', '', '', ''),
        ('157', '9D', '', '', '', '', ''),
        ('158', '9E', '', '', '', '', ''),
        ('159', '9F', '', '', '', '', ''),
        ('160', 'A0', '', '', '', '', ''),
        ('161', 'A1', '', '', '', '~', 'similar, tilde'),
        ('162', 'A2', '', '', '', 's', ''),
        ('163', 'A3', '', '', '', 't', ''),
        ('164', 'A4', '', '', '', 'u', ''),
        ('165', 'A5', '', '', '', 'v', ''),
        ('166', 'A6', '', '', '', 'w', ''),
        ('167', 'A7', '', '', '', 'x', ''),
        ('168', 'A8', '', '', '', 'y', ''),
        ('169', 'A9', '', '', '', 'z', ''),
        ('170', 'AA', '', '', '', '', ''),
        ('171', 'AB', '', '', '', '', ''),
        ('172', 'AC', '', '', '', '', ''),
        ('173', 'AD', '', '', '', '', ''),
        ('174', 'AE', '', '', '', '', ''),
        ('175', 'AF', '', '', '', '', ''),
        ('176', 'B0', '', '', '', '', ''),
        ('177', 'B1', '', '', '', '', ''),
        ('178', 'B2', '', '', '', '', ''),
        ('179', 'B3', '', '', '', '', ''),
        ('180', 'B4', '', '', '', '', ''),
        ('181', 'B5', '', '', '', '', ''),
        ('182', 'B6', '', '', '', '', ''),
        ('183', 'B7', '', '', '', '', ''),
        ('184', 'B8', '', '', '', '', ''),
        ('185', 'B9', '', '', '', '', ''),
        ('186', 'BA', '', '', '', '', ''),
        ('187', 'BB', '', '', '', '', ''),
        ('188', 'BC', '', '', '', '', ''),
        ('189', 'BD', '', '', '', '', ''),
        ('190', 'BE', '', '', '', '', ''),
        ('191', 'BF', '', '', '', '', ''),
        ('192', 'C0', '', '', '', '{', 'left brace'),
        ('193', 'C1', '', '', '', 'A', ''),
        ('194', 'C2', '', '', '', 'B', ''),
        ('195', 'C3', '', '', '', 'C', ''),
        ('196', 'C4', '', '', '', 'D', ''),
        ('197', 'C5', '', '', '', 'E', ''),
        ('198', 'C6', '', '', '', 'F', ''),
        ('199', 'C7', '', '', '', 'G', ''),
        ('200', 'C8', '', '', '', 'H', ''),
        ('201', 'C9', '', '', '', 'I', ''),
        ('202', 'CA', '', '', '', '', ''),
        ('203', 'CB', '', '', '', '', ''),
        ('204', 'CC', '', '', '', '', ''),
        ('205', 'CD', '', '', '', '', ''),
        ('206', 'CE', '', '', '', '', ''),
        ('207', 'CF', '', '', '', '', ''),
        ('208', 'D0', '', '', '', '}', 'right brace'),
        ('209', 'D1', '', '', '', 'J', ''),
        ('210', 'D2', '', '', '', 'K', ''),
        ('211', 'D3', '', '', '', 'L', ''),
        ('212', 'D4', '', '', '', 'M', ''),
        ('213', 'D5', '', '', '', 'N', ''),
        ('214', 'D6', '', '', '', 'O', ''),
        ('215', 'D7', '', '', '', 'P', ''),
        ('216', 'D8', '', '', '', 'Q', ''),
        ('217', 'D9', '', '', '', 'R', ''),
        ('218', 'DA', '', '', '', '', ''),
        ('219', 'DB', '', '', '', '', ''),
        ('220', 'DC', '', '', '', '', ''),
        ('221', 'DD', '', '', '', '', ''),
        ('222', 'DE', '', '', '', '', ''),
        ('223', 'DF', '', '', '', '', ''),
        ('224', 'E0', '', '', '', '\\', 'left slash'),
        ('225', 'E1', '', '', '', '', ''),
        ('226', 'E2', '', '', '', 'S', ''),
        ('227', 'E3', '', '', '', 'T', ''),
        ('228', 'E4', '', '', '', 'U', ''),
        ('229', 'E5', '', '', '', 'V', ''),
        ('230', 'E6', '', '', '', 'W', ''),
        ('231', 'E7', '', '', '', 'X', ''),
        ('232', 'E8', '', '', '', 'Y', ''),
        ('233', 'E9', '', '', '', 'Z', ''),
        ('234', 'EA', '', '', '', '', ''),
        ('235', 'EB', '', '', '', '', ''),
        ('236', 'EC', '', '', '', '', ''),
        ('237', 'ED', '', '', '', '', ''),
        ('238', 'EE', '', '', '', '', ''),
        ('239', 'EF', '', '', '', '', ''),
        ('240', 'F0', '', '', '', '0', ''),
        ('241', 'F1', '', '', '', '1', ''),
        ('242', 'F2', '', '', '', '2', ''),
        ('243', 'F3', '', '', '', '3', ''),
        ('244', 'F4', '', '', '', '4', ''),
        ('245', 'F5', '', '', '', '5', ''),
        ('246', 'F6', '', '', '', '6', ''),
        ('247', 'F7', '', '', '', '7', ''),
        ('248', 'F8', '', '', '', '8', ''),
        ('249', 'F9', '', '', '', '9', ''),
        ('250', 'FA', '', '', '', '|', 'vertical line'),
        ('251', 'FB', '', '', '', '', ''),
        ('252', 'FC', '', '', '', '', ''),
        ('253', 'FD', '', '', '', '', ''),
        ('254', 'FE', '', '', '', '', ''),
        ('255', 'FF', '', '', '', 'EO', 'eight ones'),
    ]
}


def ebcdic_all_printable(byt: bytes) -> bool:
    """True if all character codes are printable EBCDIC."""
    return len(set(byt) - EBCDIC_PRINTABLE) == 0


def ebcdic_ascii_description(byt: bytes) -> EbcdicAsciiTableEntry:
    """Look up the first character in the given bytes and return the EBCDIC table entry."""
    return EBCDIC_ASCII_TABLE[byt[0]]


def ebcdic_to_ascii(byt: bytes) -> str:
    """Convert EBCDIC to ASCII."""
    ret = byt.decode('cp500')
    return ret


def ascii_to_ebcdic(ascii_str: str) -> bytes:
    """Convert ASCII to EBCDIC."""
    ret = ascii_str.encode('cp500')
    return ret
