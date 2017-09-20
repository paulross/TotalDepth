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
"""Has classes for timing execution

"""

import time
import logging
import sys

from TotalDepth.LIS import ExceptionTotalDepthLIS

__author__  = 'Paul Ross'
__date__    = '2011-06-20'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

class ExceptionExecTimer(ExceptionTotalDepthLIS):
    """Specialisation of exception for this module."""
    pass

class ExecEvent(object):
    """Records the timing of a single event."""
    def __init__(self, desc):
        self._tStart = time.clock()
        self._desc = desc
        self._bytes = 0
        self._tStop = None
        
    def stop(self, bytes=0):
        """Stop the timer."""
        self._tStop = time.clock()
        self._bytes = bytes
    
    @property
    def hasCompleted(self):
        """True if the timer has been stopped."""
        return self._tStop is not None
        
    @property
    def tExec(self):
        """Executions time in seconds."""
        if self._tStop is not None:
            return self._tStop - self._tStart

    def __str__(self):
        if self.hasCompleted:
            return '{:s} Time: {:g} (s)'.format(self._desc, self.tExec)
        return self._desc
    
    def lenDesc(self):
        """Length of the task description string."""
        return len(self._desc)
        
    def writeToStderr(self, descWidth=0):
        """Write self to sys.stderr."""
        self.writeToStream(theS=sys.stderr, descWidth=descWidth)
        
    def writeToStream(self, theS, descWidth=0):
        """Write self to provided stream."""
        myDesc = '{:{width}s}'.format(self._desc, width=descWidth)
        if self._tStop is not None:
            theS.write(' {:s} Size: {:8.3f} (MB)'.format(myDesc, self._bytes/(1024*1024)))
#            theS.write(' {:s}: {:d}'.format(self._desc, workCount))
            theS.write(' Time: {:8.3f} (s)'.format(self.tExec))
#            theS.write(' Rate: {:.3f} (MB/s)'.format(self._bytes/(1024*1024*self.tExec)))
            if self._bytes != 0:
                theS.write(' Cost: {:10.3f} (ms/MB)'.format((self.tExec*1024)/(self._bytes/(1024*1024))))
            else:
                theS.write(' Cost: {:>10s} (ms/MB)'.format('N/A'))
            theS.write(' ')
        else:
            theS.write(' {:s} still running '.format(myDesc))

class ExecTimerList(object):
    """Maintains a list of execution time objects"""
    def __init__(self):
        """Constructor"""
        self._timerS = []
        
    def __len__(self):
        """Number of task timers."""
        return len(self._timerS)
    
    def startNewTimer(self, theDesc):
        """Load a new task timer starting right now."""
        self._timerS.append(ExecEvent(theDesc))
    
    @property
    def timer(self):
        """The current timer."""
        return self._timerS[-1]
    
    @property
    def hasActiveTimer(self):
        """True if there is a running timer, False if there are either no timers
        or the latest timer is halted.""" 
        return len(self._timerS) > 0 and not self._timerS[-1].hasCompleted
    
    def stopTimer(self, bytes=0):
        """Stop current timer."""
        self._timerS[-1].stop(bytes)
    
    def __str__(self):
        return '\n'.join([str(e) for e in self._timerS])

    def writeToStderr(self):
        """Write self to sys.stderr."""
        self.writeToStream(theS=sys.stderr)
        sys.stderr.write(' ')
        
    def writeToStream(self, theS):
        """Write self to provided stream."""
        theS.write(' ExecTimerList [{:d}]:\n'.format(len(self)))
        descWidth = max([t.lenDesc() for t in self._timerS])
        for i, e in enumerate(self._timerS):
            e.writeToStream(theS, descWidth=descWidth)
            if i != len(self._timerS)-1:
                theS.write('\n')
