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
import typing

from TotalDepth.LIS import ExceptionTotalDepthLIS

__author__  = 'Paul Ross'
__date__    = '2011-06-20'
__version__ = '0.1.0'
__rights__  = 'Copyright 2011-2020 (c) Paul Ross'


class ExceptionExecTimer(ExceptionTotalDepthLIS):
    """Specialisation of exception for this module."""
    pass


class Timer:
    """Records the timing of a single event."""
    def __init__(self, description: str):
        self.perf_counter: float = time.perf_counter()
        self.time: float = time.time()
        self.description = description
        self.work_done = 0
        self.stopped: bool = False
        
    def stop(self, work_done: int = 0) -> None:
        """Stop the timer and record how much work was done."""
        self.perf_counter = time.perf_counter() - self.perf_counter
        self.time = time.time() - self.time
        self.work_done = work_done
        self.stopped = True

    def add_work_done(self, work_done: int) -> None:
        """Adds work done."""
        if work_done < 0:
            raise ValueError(f'Timer.add_work_done() work_done must be >= 0 not {work_done}')
        self.work_done += work_done

    @property
    def elapsed_perf_counter(self) -> float:
        """Executions time in seconds as seen by a wall clock."""
        if self.stopped:
            return self.perf_counter
        return time.perf_counter() - self.perf_counter

    @property
    def elapsed_wall_clock(self) -> float:
        """Executions time in seconds as seen by a wall clock."""
        if self.stopped:
            return self.time
        return time.time() - self.time

    def __str__(self) -> str:
        return f'Timer: perf {self.elapsed_perf_counter:.3f} wall {self.elapsed_wall_clock:.3f} rate {self.ms_mb:8.1f} ms/Mb'

    @property
    def ms_mb(self) -> float:
        """Return the work rate in ms/MB."""
        if self.work_done:
            return self.elapsed_perf_counter * 1000.0 / (self.work_done / 1024**2)
        return 0.0

    @property
    def long_str(self) -> str:
        return '\n'.join(
            [
                f' Execution time: {self.elapsed_perf_counter:10.3f} (s)',
                f'Wall clock time: {self.elapsed_wall_clock:10.3f} (s)',
                f'      Work rate: {self.ms_mb:10.1f} (ms/Mb)',
            ]
        )


class TimerList:
    """Maintains a list of execution time objects"""
    def __init__(self):
        """Constructor"""
        self.timer_list: typing.List[Timer] = []
        
    def __len__(self) -> int:
        """Number of task timers."""
        return len(self.timer_list)

    def __getitem__(self, item) -> Timer:
        return self.timer_list[item]
    
    def add_timer(self, description: str) -> None:
        """Load a new task timer starting right now."""
        self.timer_list.append(Timer(description))
    
    @property
    def timer(self) -> Timer:
        """The current timer."""
        return self.timer_list[-1]
    
    @property
    def has_active_timer(self):
        """True if there is a running timer, False if there are either no timers
        or the latest timer is halted.""" 
        return len(self.timer_list) > 0 and not self.timer_list[-1].stopped
    
    def stop(self, work_done=0) -> None:
        """Stop current timer."""
        return self.timer_list[-1].stop(work_done)
    
    def __str__(self):
        return '\n'.join([str(e) for e in self.timer_list])
