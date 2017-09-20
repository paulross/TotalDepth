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
"""RP66 Encryption.

Created on Oct 12, 2011

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

from TotalDepth.RP66 import ExceptionTotalDepthRP66
import TotalDepth.RP66.core.RepCode as RepCode

class ExceptionEncryption(ExceptionTotalDepthRP66):
    pass

class EncryptionPacketBase(object):
    """Base class for encryption packet.
    See RP66v2 Sect. 7.3 - Logical Record Segment Encryption Packet"""
    # This is the length of the packet in bytes, including all fields.
    # This field is required.
    # Rep code UNORM
    length = None
    # This is the organization code of the group responsible for the computer
    # program that encrypted the record (see Appendix A). This field is required.
    # Rep code ULONG
    prodCode = None
    # The translation tag is the name of an ORIGIN-TRANSLATION object.
    # This field is required.
    # Rep code OBNAME
    transTag = None
    # The encryption information is provided by the producer and has a
    # representation known only to the producer (identified by the producer
    # code field) of the logical record. It is used to assist producer-written
    # computer programs in decrypting the logical record.
    # It may consist of zero or more bytes.
    payload = None
#    def __init__(self):
#        pass

    def __len__(self):
        return self.length

class EncryptionPacketRead(EncryptionPacketBase):
    """Able to read an encryption packet from a stream.
Table 4 - Logical Record Segment Encryption Packet Fields
*Note    Field    Size in Bytes    Representation Code
1    Packet length    2    UNORM
2    Producer code    4    ULONG
3    Translation tag    V    OBNAME
4    Encryption information    V    (see note)
"""
    def __init__(self, theS):
        super().__init__()
        self.length = RepCode.readUNORM(theS)
#        print('TRACE: EncryptionPacketRead.__init__(): length={:d}'.format(self.length))
        self.prodCode = RepCode.readULONG(theS)
        self.transTag = RepCode.readOBNAME(theS)
        payLen = self.length - RepCode.lenFixedName('UNORM') - RepCode.lenFixedName('ULONG') - len(self.transTag)
        if payLen < 0:
            raise ExceptionEncryption('Negative encryption payload of {:d}'.format(payLen))
        self.payload = theS.read(payLen)
        
        



