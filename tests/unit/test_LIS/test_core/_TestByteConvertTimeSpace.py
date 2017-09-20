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
"""Tests byte conversion speed and memory usage.
"""

__author__  = 'Paul Ross'
__date__    = '26 Jan 2011'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'

#import pprint
import sys
import time
import logging
import array

from TotalDepth.LIS.core import RepCode

######################
# Section: Unit tests.
######################
import unittest

NUM_MB = 8#*8

class Event(object):
    def __init__(self, siz):
        """Constructor with size of operation in bytes."""
        self._siz = siz
        self._hStart = self.getHeap()
        self._tStart = time.clock()
        self._tEnd = None
        self._hEnd = None
    
    def isOpen(self):
        return self._tEnd is None and self._hEnd is None
    
    def stop(self):
        """Record stop operation."""
        self._tEnd = time.clock()
        self._hEnd = self.getHeap()

    def getHeap(self):
        """Returns user supplied heap size or None. Return value is 1024* user value."""
        h = input('Heap size (kB)? ')
        try:
            return float(h)*1024
        except ValueError:
            pass
        
    @property
    def execTime(self):
        if self._tEnd is not None:
            return self._tEnd - self._tStart
        
    def timeCost(self):
        """Returns the time cost in ms/MB or None."""
        if self._tEnd is not None:
            return self.execTime * 1024 / (self._siz / (1024*1024))
        
    def spaceCost(self):
        """Returns the space cost as a pair (bytes, bytes/size) or None."""
        if self._hStart is not None \
        and self._hEnd is not None:
            h = self._hEnd - self._hStart
            return h, h / self._siz
        
class TimeSpace(object):
    def __init__(self):
        self._events = []
        
    def startEvent(self, theSize):
        self._events.append(Event(theSize))
        
    def endEvent(self):
        if len(self._events) > 0:
            self._events[-1].stop()
    
    def writeCostStdErr(self):
        if len(self._events) > 0:
            if self._events[-1].isOpen():
                self._events[-1].stop()
            b, f = self._events[-1].spaceCost()
            sys.stderr.write('Cost: time={:.3f} (s) {:.1f} (ms/MB) Heap={:.3f} (MB) Stretch=x{:.3f} '.format(
                    self._events[-1].execTime,
                    self._events[-1].timeCost(),
                    b/(1024*1024),
                    f,
                )
            )
            
class TestBase(unittest.TestCase):
    def setUp(self):
        """Set up."""
        self._word = b'\x44\x4c\x80\x00'
        self._mb = 1024*1024


    def _getBytes(self):
        return self._word * int(self._mb * NUM_MB // len(self._word))

class TestCreateByte(TestBase):
    """Tests ..."""
    def test_00(self):
        """TestCreateByte: Create 64MB of bytes converted to list of rep code 68."""
        myTs = TimeSpace()
        myTs.startEvent(NUM_MB * self._mb)
        b = self._getBytes()
        myTs.endEvent()
        myTs.writeCostStdErr()

class TestCreateByteList(TestBase):
    """Tests ..."""
    def test_00(self):
        """TestCreateByteList: 64MB of bytes converted to list of 4 bytes."""
        b = self._getBytes()
        myTs = TimeSpace()
        myTs.startEvent(NUM_MB * self._mb)
        l = [b[i:i+len(self._word)] for i in range(0,len(b),len(self._word))]
        myTs.endEvent()
        myTs.writeCostStdErr()

class TestCreateList(TestBase):
    """Tests ..."""
    def test_01(self):
        """TestCreateList: Create list of 2m RepCode 68 from 64MB of bytes."""
        b = self._getBytes()
        myTs = TimeSpace()
        myTs.startEvent(NUM_MB * self._mb)
        l = [RepCode.readBytes68(b[i:i+len(self._word)]) for i in range(0,len(b),len(self._word))]
        myTs.endEvent()
        myTs.writeCostStdErr()

class TestCreateArrayDouble(TestBase):
    """Tests ..."""
    def test_02(self):
        """TestCreateArrayDouble: Create array('d') of 2m RepCode 68 from 64MB of bytes."""
        b = self._getBytes()
        myTs = TimeSpace()
        myTs.startEvent(NUM_MB * self._mb)
        l = array.array('d')
        for i in range(0,len(b),len(self._word)):
            l.append(RepCode.readBytes68(b[i:i+len(self._word)]))
        myTs.endEvent()
        myTs.writeCostStdErr()
        
class TestCreateArrayDouble_01(TestBase):
    """Tests ..."""
    def test_02(self):
        """TestCreateArrayDouble_01: Create array('d') of RepCode 68 consuming bytes as we go."""
        sys.stderr.write('Disabled as this os O(N**2) and takes 6mins for just 4MB.')
        return
        assert(0)
        b = bytearray(self._getBytes())
        myTs = TimeSpace()
        myTs.startEvent(NUM_MB * self._mb)
        l = array.array('d')
        r = len(self._word)
        for i in range(0,len(b),r):
            l.append(RepCode.readBytes68(b[:r]))
            del b[:r]
        myTs.endEvent()
        myTs.writeCostStdErr()
        
class TestCreateListArrayDouble(TestBase):
    """Tests ..."""
    def test_02(self):
        """TestCreateListArrayDouble: Create array('d') of 2m RepCode 68 from 64MB of bytes via a list."""
        b = self._getBytes()
        myTs = TimeSpace()
        myTs.startEvent(NUM_MB * self._mb)
        l = array.array('d', [RepCode.readBytes68(b[i:i+len(self._word)]) for i in range(0,len(b),len(self._word))])
        myTs.endEvent()
        myTs.writeCostStdErr()
        
class TestCreateArrayFloat(TestBase):
    """Tests ..."""
    def test_02(self):
        """TestCreateArrayFloat: Create array('f') of 2m RepCode 68 from 64MB of bytes."""
        b = self._getBytes()
        myTs = TimeSpace()
        myTs.startEvent(NUM_MB * self._mb)
        l = array.array('f')
        for i in range(0,len(b),len(self._word)):
            l.append(RepCode.readBytes68(b[i:i+len(self._word)]))
        myTs.endEvent()
        myTs.writeCostStdErr()
        
class TestCreateListArrayFloat(TestBase):
    """Tests ..."""
    def test_02(self):
        """TestCreateListArrayFloat: Create array('f') of 2m RepCode 68 from 64MB of bytes via a list."""
        b = self._getBytes()
        myTs = TimeSpace()
        myTs.startEvent(NUM_MB * self._mb)
        l = array.array('f', [RepCode.readBytes68(b[i:i+len(self._word)]) for i in range(0,len(b),len(self._word))])
        myTs.endEvent()
        myTs.writeCostStdErr()
        
class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCreateByte))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCreateByteList))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCreateList))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCreateArrayDouble))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCreateArrayDouble_01))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCreateListArrayDouble))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCreateArrayFloat))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCreateListArrayFloat))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestClass.py - A module that tests something.
Usage:
python TestClass.py [-lh --help]

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
    print('TestClass.py script version "%s", dated %s' % (__version__, __date__))
    print('Author: %s' % __author__)
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
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')

if __name__ == "__main__":
    main()
