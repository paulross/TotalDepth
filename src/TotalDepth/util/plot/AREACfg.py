#!/usr/bin/env python
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 1999-2011 Paul Ross
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
"""Module for plotting areas of particular patterns with well log data.

Created on 1 Apr 2011


Note on patterns in XML file in: ``formats\IWWPatterns.xml``

There are elements thus::

    <Bits>/+7/7v/u/+7/7gAA7/7v/u/+7/7v/gAA</Bits>
    <PatternHeight>12</PatternHeight>
    <PatternWidth>15</PatternWidth>

Frequency analysis shows that the characters used are '+', '/', A-Z, a-z, 0-9
so this looks like base64 encoded. Length is always 32 chars (256 bits).
Pattern size suggests 12*15=180 bits.

"""

__author__  = 'Paul Ross'
__date__    = '2011-04-01'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

import time
import sys
import logging
import base64
from optparse import OptionParser


# Orphan this valuable text, previously part of the module docstring, as Sphinx can't process it with Tex.
"""
Examples::

    >>> base64.b64decode(b'/+7/7v/u/+7/7gAA7/7v/u/+7/7v/gAA')
    b'\xff\xee\xff\xee\xff\xee\xff\xee\xff\xee\x00\x00\xef\xfe\xef\xfe\xef\xfe\xef\xfe\xef\xfe\x00\x00'
    
    <Description>Coal-LigNite</Description>
    >>> base64.b64decode(b'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    
    <Description>Void</Description>
    >>> base64.b64decode(b'//7//v/+//7//v/+//7//v/+//7//v/+')
    b'\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe'
    
    >>> base64.b64decode(b'2Hzfkrnudnzvst3O2n67gmZ83Z7V5iYa')
    b'\xd8|\xdf\x92\xb9\xeev|\xef\xb2\xdd\xce\xda~\xbb\x82f|\xdd\x9e\xd5\xe6&\x1a'

Length is always 24 bytes (192 bits) 12x16 ?
This looks promising::

    >>> l = list(b'\xd8|\xdf\x92\xb9\xeev|\xef\xb2\xdd\xce\xda~\xbb\x82f|\xdd\x9e\xd5\xe6&\x1a')
    >>> s = ['{:08b}'.format(v) for v in l]
    >>> st = ''.join(s)
    >>> patS = [st[i:i+12] for i in range(16)]
    >>> print('\\n'.join(patS))
    110110000111
    101100001111
    011000011111
    110000111110
    100001111100
    000011111001
    000111110011
    001111100110
    011111001101
    111110011011
    111100110111
    111001101111
    110011011111
    100110111111
    001101111110
    011011111100

Or shortened::

    st = ''.join(['{:08b}'.format(v) for v in b'...'])
    print('\\n'.join([st[i:i+12] for i in range(16)]))

    <Description>Void</Description>
    >>> base64.b64decode(b'//7//v/+//7//v/+//7//v/+//7//v/+')
    b'\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe'
    111111111111
    111111111111
    111111111111
    111111111111
    111111111110
    111111111101
    111111111011
    111111110111
    111111101111
    111111011111
    111110111111
    111101111111
    111011111111
    110111111111
    101111111111
    011111111111

Hmmm 12 zeros, perhaps it is 12x15 after all::

    >>> base64.b64decode(b'/+7/7v/u/+7/7gAA7/7v/u/+7/7v/gAA')
    b'\xff\xee\xff\xee\xff\xee\xff\xee\xff\xee\x00\x00\xef\xfe\xef\xfe\xef\xfe\xef\xfe\xef\xfe\x00\x00'
    111111111110
    111111111101
    111111111011
    111111110111
    111111101110
    111111011101
    111110111011
    111101110111
    111011101111
    110111011111
    101110111111
    011101111111
    111011111111
    110111111111
    101111111111
    011111111111

Full range (sorted)::

    //4zAP/6//oA9v/+//4zAP/8//oA+v/2
    //6/AIP+//4Avv+C//6/AIP+//4Avv+C
    //60ks/+//6ZaP+e//60ks/+//6ZaP+e
    //69fIEA//4QENfW//69fIEA//4QENf2
    //6N5r/mj76/urm+ub7v8u7+774t8v/y
    //6v1vt+rOr//lq2/87//rrq//7XXu++
    //7//v/+//7//v/+//7//v/+//7//v/+
    //7/3t/e397fwsP+//7/3t/e397fwsP+
    //7/AP/+//4A/v/+//7/AP/+//4A/v/+
    //7/AP/+/9YA7v/W1/7vANf+/9YA7v/W
    //7/AP/+Wv4A/v/+//7/AP/+Wv4A/v/+
    //7/APv+9/4A/v/6//b/AP3+8/4A/v/+
    //73/uv+wf7//v/+//7/3v+u/wb//v/+
    //732gAAvfbvfAAAu97vegAAve73fAAA
    //7bAP/+//4A1v/+//7bAP/+//4A1v/+
    //7bAPv+9/4A1v/6//bbAP3+8/4A2v/+
    //7HHoLugu7HHv/+//6PxneCd4KPxv/+
    //7HHrruuu7HHv/+//6Pxne6d7qPxv/+
    //7nAP/+/+4A7v/u//7nAP/+/+4A7v/u
    //7nOOc4//45zjnO//7nOOc4//45zjnO
    //7nOOc4//45zv/O//7nOP8+//45zvn+
    //7vAP/+//4A7v/+//7vAP/+//4A7v/+
    //b/9v/2+7b5Ngqg+777vv/+9/73/gAA
    //b/9v/2+7b7tgqg+T77vv/+9/73/gAA
    //b/9v/2+Db79gog+774Pv/+9/73/gAA
    //b/9v/2+Hb7tghg+774fv/+9/73/gAA
    //b/9v/2+Pb7dgjA+/77/v/+9/73/gAA
    /+4zLv/uzOj/7gcA3/7TMt/+XMzf/gBy
    /+6B7n7uge7/7gAA7/7vAu787wLv/gAA
    /+7/7rvux+7/7gAA7/7v/u+678bv/gAA
    /+7/7sHu/+7/7gAA797vvu/+7/7v/gAA
    /+7/7uDu/+7/7gAA7/7v/u8G7/7v/gAA
    /+7/7v/u/+7/7gAA7/7v/u/+7/7v/gAA
    /+7/7v/u/+7/7oOC7/7v/u/+7/7v/oOC
    /+7/7v/u/+7bbAAA7/7v/u/+7/5ttgAA
    /+7/7v/u/+r/5gAA7/7v/u/+6/7n/gAA
    /+7/7vPu/+7/7gAA7/7v/u8+7/7v/gAA
    /+7/7vPu/+7/7gAA7/7v/u8G7/7v/gAA
    /+7/7vPu/+7/7gAA797vvu/+7/7v/gAA
    /+7/AP/+7/4A/v/+/+7/AP/+7/4A/v/+
    /+717vvu9e7/7gAA7/7v1u/u79bv/gAA
    /+73xuPG44LB/v/+/+73xuPG44LB/v/+
    /+7bAP/+7/4A1v/+/+7bAP/+7/4A1v/+
    /+7n7oHu5+7/7gAA7/7vzu8C787v/gAA
    /+7v7sfu7+7/7gAA7/7v7u/G7+7v/gAA
    /+7v7tfu7+7/7gAA7/7v7u/W7+7v/gAA
    /+7vAP/+7/4A7v/+/+7vAP/+7/4A7v/+
    /+7X7oPu1+7/7gAA7/7v1u+C79bv/gAA
    /+bP2ofah+bP/v8+/h7+Hs8+t/63/s/+
    /+bP2rfat+bP/v8+/t7+3s8+t/63/s/+
    /34a4Pn+AAD/+sHW/84AAO/+Xg4//gAA
    /34ekP3+AAD/+gc2/+4AAO/+3MC//gAA
    /34O4P3+AAD/+uD2/+4AAO/+3wa//gAA
    /36a8vn+AAD/+ufW/84AAO/+Xz4//gAA
    /37+/v3+AAD/+v/2/+4AAO/+3/6//gAA
    /376/vn+AAD/+v/W/84AAO/+X/4//gAA
    /37Ozv3+AAD/+s/2/+4AAO/+356//gAA
    /3b/jv+u/47/dv/+u/7H/tf+x/67/v/+
    /97/wP/e+N77Xvje+/77/v/g//4AHv/+
    /d773vvuAAC+/r7+f34AAPfu7/bv9gAA
    /wKBer0Cgf7//v/+//7/AoF6vQKB/v/+
    +/73MgH+//Yz7v4C+/73MgP+//Yz7v4C
    2/7nMu/+3/75mP/+/7Yzzv/e/76Z8v/+
    2Hzfkrnudnzvst3O2n67gmZ83Z7V5iYa
    3/4HMv/+/+4zgv/+3/4HMv/+/+4zgv/+
    3/6s+N/+/+451v/u3/6s+N/+/+451v/u
    3d7u7vd2e7q93N7u73b3unvcve7e9u96
    3d7urvZ2ebq53Nbqz3a3inucvW7e9u16
    3dz//v/+d3b//v/+3dz//v/+d3b//v/+
    4er//tde//764P/+117//uHq//7XXv/+
    4er//tdO/+764P/+117f/sHq//7XXv/+
    5/6BAOf+/+aAgP/m5/6BAOf+/+aAgP/m
    5+aB/uf+/87/Ao/OvH6lfrT+hX7/5v+A
    5mb//szm//6ZmP/+//4zOP/+//45zv/+
    5zL//pnO//7nMv/+mc7//ucy//45zv/+
    7/6rMu/+AADu7qqq7u4AAP7uMqr+7gAA
    7/7vAO/+/+4A7v/u7/7vAO/+/+4A7v/u
    8e7u7u7u7u7x7gAA7x7u7u7u7u7vHgAA
    9/7nANf+//YA5v/W9/7nANf+//YA5v/W
    9/7nMtf+/+4zzv+u9/7nMtf+/+4zzv+u
    9/7vAN/+//YA7v/e9/7vAN/+//YA7v/e
    9fT//l9e//719P/+X17//vX0//5fXv/+
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    AAD//gAA//4AAP/+AAD//gAA//4AAP/+
    ff67/td877r/1v/uff67/td877r/1v/u
    JJK22pJIJJK22pJIJJK22pJIJJK22pJI
    m/73Mu/+//bM7v/eO/73Mu/+//aZ7v/e
    MzL//szO//6DwP/+zM7//v/+ODj//s/O
    u/7WeO/+/7o81v/uu/7WeO/+/7r/1jzu
    u/7WeO/+/7o81v/uu/7WeO/+/7r/1rvu
    u/7XAO/+/7oA1v/uu/7XAO/+/7oA1v/u
    uur//tdc//666v/+11z//rrq//7XXP/+
    w+6Z7mbuWu7/7gAA74bvMu7M7rTv/gAA
    x+677qvuu+7H7gAA78bvuu+q77rvxgAA
    z/4DMs/+/84zAv/Oz/4DMs/+/84zAv/O
    zM7MzszOzM7MzszOzM7MzszOzM7MzszO
    zv4/PvnOx/I+/P9+/b7z3s/uvfb+fvu+
"""

#: A map of {pattern name : bytes, ...}
PATTERN_MAP = {
    'Void'                                          : b'//7//v/+//7//v/+//7//v/+//7//v/+',
    'Coal-LigNite'                                  : b'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
    'LimeStone'                                     : b'/+7/7v/u/+7/7gAA7/7v/u/+7/7v/gAA',
    'Dolomitic LimeStone'                           : b'/+7/7v/u/+r/5gAA7/7v/u/+6/7n/gAA',
    'Argillaceous Limestone'                        : b'/+7/7uDu/+7/7gAA7/7v/u8G7/7v/gAA',
    'Sandy Limestone'                               : b'/+7/7vPu/+7/7gAA7/7v/u8+7/7v/gAA',
    'Argillaceous and dolomitic Limestone'          : b'/+7/7sHu/+7/7gAA797vvu/+7/7v/gAA',
    'Argillaceous and sandy Limestone'              : b'/+7/7vPu/+7/7gAA7/7v/u8G7/7v/gAA',
    'Sandy and dolomitic Limestone'                 : b'/+7/7vPu/+7/7gAA797vvu/+7/7v/gAA',
    'Chalk'                                         : b'/+7/7v/u/+7/7oOC7/7v/u/+7/7v/oOC',
    'Oolitic Limestone'                             : b'x+677qvuu+7H7gAA78bvuu+q77rvxgAA',
    'Pelletic Limestone'                            : b'8e7u7u7u7u7x7gAA7x7u7u7u7u7vHgAA',
    'Nodular Limestone'                             : b'/+6B7n7uge7/7gAA7/7vAu787wLv/gAA',
    'Shelly Limestone'                              : b'/+7/7rvux+7/7gAA7/7v/u+678bv/gAA',
    'Reefal Limestone'                              : b'w+6Z7mbuWu7/7gAA74bvMu7M7rTv/gAA',
    'Bioclastic Limestone'                          : b'/+7X7oPu1+7/7gAA7/7v1u+C79bv/gAA',
    'Silicified Limestone'                          : b'/+7/7v/u/+7bbAAA7/7v/u/+7/5ttgAA',
    'Cherty Limestone'                              : b'/+7v7sfu7+7/7gAA7/7v7u/G7+7v/gAA',
    'Anhydritic Limestone'                          : b'/+717vvu9e7/7gAA7/7v1u/u79bv/gAA',
    'Phosphatic Limestone'                          : b'/+7v7tfu7+7/7gAA7/7v7u/W7+7v/gAA',
    'Bituminous Limestone'                          : b'/+7n7oHu5+7/7gAA7/7vzu8C787v/gAA',
    'Mudstone'                                      : b'//b/9v/2+7b5Ngqg+777vv/+9/73/gAA',
    'Wackstone'                                     : b'//b/9v/2+7b7tgqg+T77vv/+9/73/gAA',
    'Packstone'                                     : b'//b/9v/2+Pb7dgjA+/77/v/+9/73/gAA',
    'Grainstone'                                    : b'//b/9v/2+Db79gog+774Pv/+9/73/gAA',
    'Bundstone'                                     : b'//b/9v/2+Hb7tghg+774fv/+9/73/gAA',
    'Dolomite'                                      : b'/37+/v3+AAD/+v/2/+4AAO/+3/6//gAA',
    'Calacareous Dolomite'                          : b'/376/vn+AAD/+v/W/84AAO/+X/4//gAA',
    'Argillaceous Dolomite'                         : b'/34O4P3+AAD/+uD2/+4AAO/+3wa//gAA',
    'Sandy Dolomite'                                : b'/37Ozv3+AAD/+s/2/+4AAO/+356//gAA',
    'Argillaceous and calcareous Dolomite'          : b'/34a4Pn+AAD/+sHW/84AAO/+Xg4//gAA',
    'Sandy and calcareous Dolomite'                 : b'/36a8vn+AAD/+ufW/84AAO/+Xz4//gAA',
    'Argillaceous and Sandy Dolomite'               : b'/34ekP3+AAD/+gc2/+4AAO/+3MC//gAA',
    'Cargneule'                                     : b'/d773vvuAAC+/r7+f34AAPfu7/bv9gAA',
    'Clay-Shale'                                    : b'//7/AP/+//4A/v/+//7/AP/+//4A/v/+',
    'Slaty Shale'                                   : b'AAD//gAA//4AAP/+AAD//gAA//4AAP/+',
    'Plastic Clay-Shale'                            : b'/97/wP/e+N77Xvje+/77/v/g//4AHv/+',
    'Calcareous Clay-Shale'                         : b'7/7vAO/+/+4A7v/u7/7vAO/+/+4A7v/u',
    'Dolomitic Caly-Shale'                          : b'9/7vAN/+//YA7v/e9/7vAN/+//YA7v/e',
    'Sandy Clay-Shale'                              : b'//7vAP/+//4A7v/+//7vAP/+//4A7v/+',
    'Silty Clay-Shale'                              : b'//7bAP/+//4A1v/+//7bAP/+//4A1v/+',
    'Calcareous and dolomitic Clay-Shale'           : b'9/7nANf+//YA5v/W9/7nANf+//YA5v/W',
    'Sandy and calcareous Clay-Shale'               : b'//7nAP/+/+4A7v/u//7nAP/+/+4A7v/u',
    'Sandy and dolomitic Clay-Shale'                : b'//4zAP/6//oA9v/+//4zAP/8//oA+v/2',
    'Calcareous and dolomitic Clay-Shale'           : b'9/7nANf+//YA5v/W9/7nANf+//YA5v/W',
    'Sandy, calcareous and dolomitic Clay-Shale'    : b'/+7vAP/+7/4A7v/+/+7vAP/+7/4A7v/+',
    'Silty, calcareous and dolomitic Clay-Shale'    : b'/+7bAP/+7/4A1v/+/+7bAP/+7/4A1v/+',
    'Marl'                                          : b'/+7/AP/+7/4A/v/+/+7/AP/+7/4A/v/+',
    'Dolomitic Marl'                                : b'//7/APv+9/4A/v/6//b/AP3+8/4A/v/+',
    'Silty Marl'                                    : b'/+7bAP/+7/4A1v/+/+7bAP/+7/4A1v/+',
    'Silty dolomitic Marl'                          : b'//7bAPv+9/4A1v/6//bbAP3+8/4A2v/+',
    'Silicified Claystone'                          : b'//7/AP/+Wv4A/v/+//7/AP/+Wv4A/v/+',
    'Anhydritic Clay-Shale'                         : b'//7/AP/+/9YA7v/W1/7vANf+/9YA7v/W',
    'Saliferous Clay-Shale'                         : b'//6/AIP+//4Avv+C//6/AIP+//4Avv+C',
    'Gypsiferous Clay-Shale'                        : b'u/7XAO/+/7oA1v/uu/7XAO/+/7oA1v/u',
    'Bituminous Clay-Shale'                         : b'5/6BAOf+/+aAgP/m5/6BAOf+/+aAgP/m',
    'Organic Shale'                                 : b'zM7MzszOzM7MzszOzM7MzszOzM7MzszO',
    'Silt'                                          : b'uur//tdc//666v/+11z//rrq//7XXP/+',
    'Fine Sand'                                     : b'3dz//v/+d3b//v/+3dz//v/+d3b//v/+',
    'Medium Sand'                                   : b'5mb//szm//6ZmP/+//4zOP/+//45zv/+',
    'Coarse Sand'                                   : b'//7nOOc4//45zv/O//7nOP8+//45zvn+',
    'Siltstone'                                     : b'9fT//l9e//719P/+X17//vX0//5fXv/+',
    'Fine Sandstone'                                : b'3dz//v/+d3b//v/+3dz//v/+d3b//v/+',
    'Medium Sandstone'                              : b'5zL//pnO//7nMv/+mc7//ucy//45zv/+',
    'Coarse Sandstone'                              : b'//7nOOc4//45zjnO//7nOOc4//45zjnO',
    'Quartzite'                                     : b'7/6rMu/+AADu7qqq7u4AAP7uMqr+7gAA',
    'Argillaceous Siltstone'                        : b'4er//tde//764P/+117//uHq//7XXv/+',
    'Argillaceous Sandstone'                        : b'MzL//szO//6DwP/+zM7//v/+ODj//s/O',
    'Calcareous Sandstone'                          : b'/+4zLv/uzOj/7gcA3/7TMt/+XMzf/gBy',
    'Dolomitic Sandstone'                           : b'm/73Mu/+//bM7v/eO/73Mu/+//aZ7v/e',
    'Calcareous and dolomitic Sandstone'            : b'9/7nMtf+/+4zzv+u9/7nMtf+/+4zzv+u',
    'Argillaceous and calcareous Sandstone'         : b'3/4HMv/+/+4zgv/+3/4HMv/+/+4zgv/+',
    'Argillaceous and dolomitic Sandstone'          : b'+/73MgH+//Yz7v4C+/73MgP+//Yz7v4C',
    'Arkosic Sandstone'                             : b'2/7nMu/+3/75mP/+/7Yzzv/e/76Z8v/+',
    'Shelly Sandstone'                              : b'//60ks/+//6ZaP+e//60ks/+//6ZaP+e',
    'Shelly Siltstone'                              : b'//6v1vt+rOr//lq2/87//rrq//7XXu++',
    'Diatomite'                                     : b'//69fIEA//4QENfW//69fIEA//4QENf2',
    'Radiolarite'                                   : b'/3b/jv+u/47/dv/+u/7H/tf+x/67/v/+',
    'Chert'                                         : b'//73/uv+wf7//v/+//7/3v+u/wb//v/+',
    'Bedded Chert'                                  : b'3d7u7vd2e7q93N7u73b3unvcve7e9u96',
    'Anhydritic Sandstone'                          : b'u/7WeO/+/7o81v/uu/7WeO/+/7r/1jzu',
    'Anhydritic Siltsone'                           : b'u/7WeO/+/7o81v/uu/7WeO/+/7r/1rvu',
    'Saliferous Sandstone'                          : b'4er//tdO/+764P/+117f/sHq//7XXv/+',
    'Bituminous Sandstone'                          : b'z/4DMs/+/84zAv/Oz/4DMs/+/84zAv/O',
    'Glauconitic Sandstone'                         : b'3/6s+N/+/+451v/u3/6s+N/+/+451v/u',
    'Ferruginous Sandstone'                         : b'//6N5r/mj76/urm+ub7v8u7+774t8v/y',
    'Monom Conglomerate 4-64 mm'                    : b'//7HHrruuu7HHv/+//6Pxne6d7qPxv/+',
    'Polym Conglomerate 4-64 mm'                    : b'//7HHoLugu7HHv/+//6PxneCd4KPxv/+',
    'Monom Conglomerate 2-4 mm'                     : b'/+bP2rfat+bP/v8+/t7+3s8+t/63/s/+',
    'Polym Conglomerate 2-4 mm'                     : b'/+bP2ofah+bP/v8+/h7+Hs8+t/63/s/+',
    'Monogenic Breccia'                             : b'/+73xuPG44LB/v/+/+73xuPG44LB/v/+',
    'Polymictic Breccia'                            : b'/+73xuPG44LB/v/+/+73xuPG44LB/v/+',
    'Evaporite'                                     : b'JJK22pJIJJK22pJIJJK22pJIJJK22pJI',
    'Halite'                                        : b'//7/3t/e397fwsP+//7/3t/e397fwsP+',
    'Anhydrite'                                     : b'3d7urvZ2ebq53Nbqz3a3inucvW7e9u16',
    'Gypsum'                                        : b'ff67/td877r/1v/uff67/td877r/1v/u',
    'Sylvite'                                       : b'/wKBer0Cgf7//v/+//7/AoF6vQKB/v/+',
    'Volcanic Rock'                                 : b'zv4/PvnOx/I+/P9+/b7z3s/uvfb+fvu+',
    'Basalt'                                        : b'//732gAAvfbvfAAAu97vegAAve73fAAA',
    'Granit'                                        : b'5+aB/uf+/87/Ao/OvH6lfrT+hX7/5v+A',
    'Metamorphic Rocks'                             : b'2Hzfkrnudnzvst3O2n67gmZ83Z7V5iYa',
}

def pprintPattern(theName):
    """Pretty print the pattern."""
    b64 = PATTERN_MAP[theName]
    b = base64.b64decode(b64)
    st = ''.join(['{:08b}'.format(v) for v in b])
    print(theName.center(40, '='))
    print('\n'.join([st[i:i+12] for i in range(16)]))
    print(''.center(40, '='))

def pprintAll():
    """Pretty print all patterns."""
    for k in sorted(PATTERN_MAP.keys()):
        print()
        pprintPattern(k)

def main():
    usage = """usage: %prog [options] dir
Counts files and sizes."""
    print ('Cmd: %s' % ' '.join(sys.argv))
    optParser = OptionParser(usage, version='%prog ' + __version__)
    optParser.add_option(
            "-l", "--loglevel",
            type="int",
            dest="loglevel",
            default=20,
            help="Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: %default]"
        )      
    opts, args = optParser.parse_args()
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    # Your code here
    pprintAll()
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    #multiprocessing.freeze_support()
    sys.exit(main())
