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
"""Some common classes used in unit testing.

Created on 10 Jan 2011

@author: p2ross
"""

__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

import time
import sys
import struct
import random
#import logging
#from optparse import OptionParser

import io
import unittest
import re
import math

from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import PhysRec
from TotalDepth.LIS.core import RepCode

RE_SIZE_COST = re.compile(r'^.+Size:\s*([0-9.]+).+Cost:\s*([0-9.]+).+$')

#>>> R = re.compile('^.+Size:\s*([0-9.]+).+Cost:\s*([0-9.]+).+$')
#>>> t = """TestPhysRecWriteRead_Perf.test_03_03():  128 LRs that are 64kB, 512B PRs. ...  Size: 8.000 (MB) LRs: 128 Time: 0.519 (s) Cost: 66.416 (ms/MB) ok
#... ...
#... TestPhysRecWriteRead_Perf.test_03_10():  128 LRs that are 64kB, 64kB PRs. ...  Size: 8.000 (MB) LRs: 128 Time: 0.009 (s) Cost: 1.206 (ms/MB) ok
#... """
#>>> ls = t.split('\n')
#>>> for l in ls:
#...   m = R.match(l)
#...   if m:
#...     print(m.group(1), m.group(2))
#...
#8.000 66.416

class TestBase(unittest.TestCase):
    def writeCostToStderr(self, tStart, siz, workName, workCount):
        execTime = time.perf_counter() - tStart
        sys.stderr.write(' Size: {:.3f} (MB)'.format(siz/(1024*1024)))
        sys.stderr.write(' {:s}: {:d}'.format(workName, workCount))
        sys.stderr.write(' Time: {:.3f} (s)'.format(execTime))
        #sys.stderr.write(' Rate: {:.3f} (MB/s)'.format(siz/(1024*1024*execTime)))
        if siz != 0:
            myCost = (execTime*1024)/(siz/(1024*1024))
            sys.stderr.write(' Cost: {:.3f} (ms/MB)'.format(myCost))
        else:
            myCost = 'N/A'
            sys.stderr.write(' Cost: {:s} (ms/MB)'.format(myCost))
        sys.stderr.write(' ')
        sys.stderr.flush()
        # sys.stderr.write('\n')

class TestRepCodeBase(TestBase):
    def randBits(self, theBits):
        """Return a random integer of theBits number of bits."""
        return random.getrandbits(theBits)
    
    def randWord(self, s, e, m):
        """Return a random word with s, e and m number of bits set randomly."""
        w = self.randBits(s)
        w <<= e
        w |= self.randBits(e)
        w <<= m
        w |= self.randBits(m)
        return w
    
    def randInt(self, theMin, theMax):
        return random.randint(theMin, theMax)
    
    def roundToDecimalSigDigits(self, v, s):
        #print 'TRACE: roundToDecimalSigDigits() 0:', v, s
        m, exp = math.frexp(v)
        #print 'TRACE: roundToDecimalSigDigits() 1:', m, exp
        # m is 0.5 <= m < 1.0, make it 0 <= m < 1.0
        m = m * 2.0 - 1.0
        m *= 10**s
        m = float(int(m))
        #print 'TRACE: roundToDecimalSigDigits() 2:', m, exp
        m /= 10**s
        m = (m + 1.0) / 2.0
        #print 'TRACE: roundToDecimalSigDigits() 3:', m, exp
        r = math.ldexp(m, exp)
        #print 'TRACE: roundToDecimalSigDigits() 4:', r
        return r

    def writeTimeToStdErr(self, start, rc, numWords):
        tE = time.perf_counter() - start
        siz = numWords * RepCode.lisSize(rc)
        # sys.stderr.write('Time: {:.3f} Rate {:8.0f} words/S '.format(tE, numWords/tE))
        # sys.stderr.write(' Cost: {:.3f} (ms/MB)'.format((tE*1024)/(siz/(1024*1024))))
        print(
            'Time: {:.3f} Rate {:8.0f} words/S Cost: {:.3f} (ms/MB)'.format(
                tE, numWords/tE, (tE*1024)/(siz/(1024*1024))
            )
        )


class TestBaseFile(TestBase):
    def _retSinglePr(self, theB):
        """Given a bytes() object this returns a bytes object encapsulated in a single Physical Record."""
        #return PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(theB)) \
        #    + PhysRec.PR_PRH_ATTR_FORMAT.pack(0) \
        #    + theB
        #    # Absent Physical Record trailer        
        return self.retPrS(theB, len(theB)+PhysRec.PR_PRH_LENGTH)

    def retPrS(self, theB, prLen=1024):
        """Returns a bytearray that is theB split into Physical Records of
        maximum length prLen. These Physical Records have no trailer records."""
        r = bytearray()
        ofs = 0
        while ofs < len(theB):
            myPayLoad = theB[ofs:ofs+prLen]
            r.extend(PhysRec.PR_PRH_LEN_FORMAT.pack(PhysRec.PR_PRH_LENGTH + len(myPayLoad)))
            a = 0
            if ofs+prLen < len(theB):
                # Has successor
                a |= 1
            if ofs > 0:
                # Has predecessor
                a |= 2
            r.extend(PhysRec.PR_PRH_ATTR_FORMAT.pack(a))
            r.extend(myPayLoad)
            ofs += prLen
        return r

    def _retFileSinglePr(self, theB):
        """Given a bytes() object this returns a file with them encapsulated in a single Physical Record."""
        myBy = io.BytesIO(self._retSinglePr(theB))
        return File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)

    def _retFilePrS(self, theB, prLen=1024):
        """Given a bytes() object this returns a file with them encapsulated in a single Physical Record."""
        myBy = io.BytesIO(self.retPrS(theB))
        return File.FileRead(theFile=myBy, theFileId='MyFile', keepGoing=True)

    def _retFileFromBytes(self, theB, theId='MyFile', flagKg=False):
        """Returns bytes object wrapped as a file."""
        return File.FileRead(theFile=io.BytesIO(theB), theFileId=theId, keepGoing=flagKg)

    def _retFileFromListOfLogicalRecords(self, theLrS, theId='MyFile', flagKg=False):
        """Given a list of bytes objects that represent Logical Records this returns a LIS File object."""
        b = bytearray()
        for lr in theLrS:
            b.extend(self.retPrS(lr))
        return File.FileRead(theFile=io.BytesIO(b), theFileId=theId, keepGoing=flagKg)

    def _twoBytes(self, v):
        if v >= 0xFF * 0xFF:
            raise Exception('_twoBytes: {:d} too large.'.format(v))
        #return bytes([v // 0xFF, v % 0xFF])
        return struct.pack('>H', v)
        
    def _retLr0Bytes(self, lr, fr, ch, sa, bu):
        """Returns LRs type 0 populated with type 68 data as a bytearray with LRH."""
        r = bytearray()
        # Value 153.0 in repcode 68 is b'\x44\x4c\x80\x00'
        w = b'\x44\x4c\x80\x00'
        # Frame length:
        # Ch 0 is b bytes
        # Ch 1+ is 4 * sa * bu
        numValues = 1 + (ch-1)*sa*bu
        frLen = len(w) * numValues
        # Logical record length:
        # PRH + LRH + fr * frLen
        lrLen = 4 + 2 + fr * frLen
        #print('lrLen', lrLen)
        for _l in range(lr):
            # PR Header
            r.extend(self._twoBytes(lrLen))
            r.extend(b'\x00\x00')
            # LR header
            r.extend(bytes([0, 0]))
            for _f in range(fr):
                r.extend(w * numValues)
        return bytes(r)
    
    def randomBytes(self, length=None):
        """Returns a bytes() object of specified length that contains random data
        of length theLen. If theLen is absent a random length of 0<=len<=32kB is
        chosen."""
        if length is None:
            length = random.randint(0, 32*1024)
        return bytes([random.choice(range(256)) for _l in range(length)])
    
class TestBaseLogPass(TestBaseFile):
    """Can create DFSRs of arbitrary size and LR type 0 of arbitrary size."""
    
    def _retDFSRBytes(self, ch, sa, bu):
        """Returns a DFSR packed as logical bytes, channels have RepCode 68.
        This adds a direct depth channel."""
        # LRH for DFSR
        myB = (bytes([64, 0])
#            # EB 4, up/down value 0 (down)
#            + bytes([4, 1, 66, 0])
#            # EB 12, absent value -153.0
#            + bytes([12, 4, 68])+b'\xbb\xb3\x80\x00'
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
            #
            # Sensor 0
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            + b'DEPT' + b'ServID' + b'ServOrdN'+ b'FEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # 4 LIS bytes     Pad      1 super  Rep code     Process indicators
            + bytes([0, 4]) + b'000' + b'\x01'+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
        )
        chLen = 4*sa*bu
        #print('chLen', chLen, self._twoBytes(chLen))
        for i in range(ch-1):
            myName = bytes('{:04d}'.format(i), 'ascii')
            # Sensor i
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            myB += (myName + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes         Pad      samples       Rep code       Process indicators
            + self._twoBytes(chLen) + b'000' + bytes([sa,])+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            )
        #print('_retDFSRBytes()', myB)
        return myB

    def _retDFSRBytesIndirect(self, ch, sa, bu):
        """Returns a DFSR with indirect X packed as logical bytes, channels have RepCode 68."""
        # LRH for DFSR
        myB = (bytes([64, 0])
            # EB 4, up/down value 1 (up)
            + bytes([4, 1, 66, 1])
            # EB 8, Frame spacing
            + bytes([8, 1, 66, 60])
            # EB 9, Frame spacing units
            + bytes([9, 4, 65])+b'.1IN'
            # EB 13, recording mode 1
            + bytes([13, 1, 66, 1])
            # EB 14, X axis units
            + bytes([14, 4, 65])+b'.1IN'
            # EB 15, indirect Rep Code 73
            + bytes([15, 1, 66, 73])
            # EB 0 terminates read
            + bytes([0, 1, 66, 0])
        )
        chLen = 4*sa*bu
        for i in range(ch):
            myName = bytes('{:04d}'.format(i), 'ascii')
            # Sensor i
            # Mnemonic  Service ID  Serv ord No    Units   API 45,310,01,1       File No: 256
            myB += (myName + b'ServID' + b'ServOrdN'+ b'    ' + b'\x02\xb3\x60\x3b' + bytes([1, 0])
            # chLen LIS bytes         Pad      samples       Rep code       Process indicators
            + self._twoBytes(chLen) + b'000' + bytes([sa,])+ bytes([68,]) + bytes([0, 1, 2, 3, 4])
            )
        #print('_retDFSRBytes()', myB)
        return myB

    def _retLr0Bytes(self, lr, fr, ch, sa, bu, indirectBytes=b''):
        """Returns LR type 0 populated with type 68 data. Each LR in a PR.
        indirectBytes will be prepended."""
        r = bytearray(indirectBytes)
        # Frame length:
        # Ch 0 is b bytes
        # Ch 1+ is 4 * sa * bu
        numValues = 1 + (ch-1)*sa*bu
        frLen = 4 * numValues
        # Logical record length:
        # PRH + LRH + fr * frLen
        lrLen = 4 + 2 + len(indirectBytes) + fr*frLen
        #print('lrLen', lrLen)
        for _l in range(lr):
            # PR Header
            r.extend(self._twoBytes(lrLen))
            r.extend(b'\x00\x00')
            # LR header
            r.extend(bytes([0, 0]))
            for _f in range(fr):
                # Value 153.0 in repcode 68 is b'\x44\x4c\x80\x00'
                r.extend(b'\x44\x4c\x80\x00' * numValues)
        return bytes(r)
    
    def _createFile(self, numLr, frPerLr, numCh, numSa, numBu):
        """Create an io.BytesIO complete with a DFSR and LR type 0 of the
        specified number and dimensions."""
        myBd = self._retSinglePr(self._retDFSRBytes(numCh, numSa, numBu))
        myBl = self._retLr0Bytes(numLr, frPerLr, numCh, numSa, numBu)
        return self._retFileFromBytes(myBd+myBl)
                     
    def _createFileDFSROnly(self, numCh, numSa, numBu):
        """Create an io.BytesIO complete with a DFSR."""
        myBd = self._retSinglePr(self._retDFSRBytes(numCh, numSa, numBu))
        return self._retFileFromBytes(myBd)


class MockStreamRead(object):
    def __init__(self, b):
        self._b = b
        self._p = 0
        
    def read(self, n=1):
        """Get n bytes and increment the index, if n is negative then return all the remaining bytes."""
        if n < 0:
            myP = self._p
            self._p = len(self._b)
            return self._b[myP:]
        self._p += n
        return self._b[self._p-n:self._p]
        
class MockStreamWrite(object):
    def __init__(self):
        self._b = bytearray()
        # This is not used
        self._p = 0
    
    @property
    def bytes(self):
        return self._b
        
    def write(self, b):
        """Write multiple bytes."""
        self._b += b
        self._p += len(b)
        return len(b)
    
    def clear(self):
        self._b = bytearray()
        self._p = 0
