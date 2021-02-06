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
SEG-Y Format support.

Defined in 'digital tape standards' by the Society of Exploration Geophysicists. Library of Congress Catalog Card Number
80-52678. ISBN 0-9311830-15-X.
Dated 1967 to 1992.

Other sources:
http://www.seg.org/documents/10161/77915/seg_y_rev0.pdf
http://www.seg.org/documents/10161/77915/seg_a_b_ex.pdf
http://seg.org/Portals/0/SEG/News%20and%20Resources/Technical%20Standards/seg_y_rev2_0-mar2017.pdf

SEG General:
https://seg.org/Publications/SEG-Technical-Standards

Informally: https://en.wikipedia.org/wiki/SEG-Y


All TotalDepth Supports at the moment is recognising a SEG-Y file.
"""
import typing

from TotalDepth.util import EBCDIC


CARD_IMAGE_EBCDIC_NUM_CARDS = 40
CARD_WIDTH_EBCDIC = 80
CARD_IMAGE_EBCDIC_BLOCK_LENGTH = CARD_IMAGE_EBCDIC_NUM_CARDS * CARD_WIDTH_EBCDIC


def is_segy(file: typing.BinaryIO) -> bool:
    """
    Returns True if the file is likely to be a SEG-Y file.
    This reads the first 3200 bytes of the file (if available).
    These must all be EBCDIC printable characters.
    Each 'card' of 80 characters must start with 'Cnn' where nn is from '01' to '40'.
    """
    file.seek(0)
    byt = file.read(CARD_IMAGE_EBCDIC_BLOCK_LENGTH)
    ret = False
    if len(byt) == CARD_IMAGE_EBCDIC_BLOCK_LENGTH:
        if EBCDIC.ebcdic_all_printable(byt):
            as_ascii = EBCDIC.ebcdic_to_ascii(byt)
            cards = [
                as_ascii[i * CARD_WIDTH_EBCDIC:(i + 1) * CARD_WIDTH_EBCDIC] for i in range(CARD_IMAGE_EBCDIC_NUM_CARDS)
            ]
            for i, card in enumerate(cards):
                if card[0] != 'C':
                    break
                if int(card[1:3]) != i + 1:
                    break
            else:
                ret = True
    return ret
