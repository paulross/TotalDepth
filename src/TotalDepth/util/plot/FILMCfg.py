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
"""Represents the part of a plot configuration that, typically, can be obtained
from a LIS FILM table.
 
Created on 21 Mar 2011

Example of the data in a film table::

    Table record (type 34) type: FILM
    
    MNEM  GCOD  GDEC  DEST  DSCA
    -----------------------------
    
    1     EEE   ----  PF2   D200
    2     EEE   ----  PF1   DM

Other FILM Table Examples::

    Table record (type 34) type: FILM
    
    MNEM  GCOD  GDEC  DEST  DSCA
    -----------------------------
    1     EEB   ----  PF1   D200
    2     EEB   ----  PF2   DM
    
    Table record (type 34) type: FILM
    
    MNEM  GCOD  GDEC  DEST  DSCA
    -----------------------------
    1     E20   -4--  PF1   D200
    2     EEE   ----  PF2   D200
    
    MNEM  GCOD  GDEC  DEST  DSCA
    -----------------------------
    1     EEE   ----  PF1   D200
    2     E1E   -4-   PF2   D200
    
    Table record (type 34) type: FILM
    
    MNEM  GCOD  GDEC  DEST  DSCA
    -----------------------------
    
    D     E3E   -3-   PFD   D200
    E     E3E   -3-   PFE   D500
    5     EB0   ---   PF5   D200
    6     EEB   ---   PF6   D200
    
    Table record (type 34) type: FILM
    
    MNEM  GCOD  GDEC  DEST  DSCA
    -----------------------------
    
    8     EB0   ---   PF8   D200
    A     LLLL  1111  PFA   DM
    E     E4E   -4-   PFE   D200
    K     E4E   -4-   PFK   D500
    
    Table record (type 34) type: FILM
    
    MNEM      CINT      GCOD  GDEC  DEST  DSCA
    -------------------------------------------
    
    1          0.00000  E2E   -2-   PF1   D200
    2          0.00000  E2E   -1-   PF2   D500
    3          0.00000  EEE   ----  NEIT  S5
    4          0.00000  EEE   ----  NEIT  S5
    
    Table record (type 34) type: FILM
    
    MNEM      CINT      GCOD  GDEC  DEST  DSCA
    -------------------------------------------
    
    1          300.000  E2E   -2-   PF1   D200
    2          300.000  E2E   -2-   PF2   D500
    3          300.000  EEE   ----  NEIT  S5
    4          300.000  EEE   ----  NEIT  S5
    
    Table record (type 34) type: FILM
    
    MNEM      CINT      GCOD  GDEC  DEST  DSCA
    -------------------------------------------
    
    1          50.0000  EEE   ----  PF1   D200
    2          0.00000  EEE   ----  PF2   D200
    3          0.00000  EEE   ----  NEIT  D200
    4          0.00000  EEE   ----  NEIT  D200

Minimal, but not complete interpretation:

Ignore GDEC as dupe.

* E - Equi-spaced (linear).
* n - Log with number of decades.
* B - Blank.
* L - ?

What to do with 0 (continuation?).
Examples: E20   -4-- means 4 decades over track 23.

Four tracks, from 200099.S07::

    Table record (type 34) type: FILM
    MNEM  GCOD  GDEC  DEST  DSCA
    -----------------------------
    ...
    A     LLLL  1111  PFA   DM  
    ...
    
    Table record (type 34) type: PRES
    MNEM  OUTP  STAT  TRAC  CODI  DEST  MODE      FILT          LEDG          REDG      COLO
    -----------------------------------------------------------------------------------------
    ...
    AX1A  AX    ALLO  F2    LLIN  A     SHIF      0.500000      -9.00000       9.00000  400 
    AY1A  AY    ALLO  F2    LSPO  A     SHIF      0.500000      -9.00000       9.00000  400 
    AZ1A  AZ    ALLO  F2    LGAP  A     NB        0.500000      -9.00000       9.00000  400 
    AN1A  ANOR  ALLO  F4    HDAS  A     NB        0.500000       9.00000       11.0000  420 
    CS1A  CS    DISA  F1    LDAS  A     NB        0.500000       0.00000       150000.  000 
    FX1A  FX    ALLO  F3    LLIN  A     NB        0.500000     -0.700000      0.700000  003 
    FY1A  FY    ALLO  F3    LGAP  A     NB        0.500000     -0.700000      0.700000  003 
    FZ1A  FZ    ALLO  F3    LSPO  A     NB        0.500000     -0.700000      0.700000  003 
    FN1A  FNOR  ALLO  F4    LLIN  A     NB        0.500000      0.200000      0.700000  420 
    FI1A  FINC  ALLO  F4    LGAP  A     NB         1.00000       0.00000       90.0000  420 
    GA1A  GADZ  DISA  F1    LLIN  A     NB         1.00000      -1.00000       1.00000  020 
    GP1A  GPV   DISA  F1    LGAP  A     NB         1.00000       14.0000       16.0000  020 
    GN1A  GNV   DISA  F1    LDAS  A     NB         1.00000      -16.0000      -14.0000  020 
    GM1A  GMT   DISA  F3    HDAS  A     SHIF       1.00000       80.0000       130.000  020 
    GA2A  GAT   DISA  F2    HDAS  A     SHIF       1.00000       80.0000       130.000  020 
    SI1A  SILO  DISA  FD    HLIN  A     NB         1.00000       0.00000       20.0000  000 
    ST1A  STIT  DISA  FD    LLIN  A     NB         1.00000       0.00000       20.0000  000 
    ST2A  STIA  ALLO  FD    LLIN  A     NB         1.00000       0.00000       20.0000  000 
    TE1A  TENS  DISA  FD    LDAS  A     WRAP      0.500000       2000.00       7000.00  000 
    ...


TODO: What about CINT and FORM headings?

2011-05-27 Frequency Analysis done on::
 
    $ python3 TableHistogram.py -k --name=FILM -l40 --col=DEST ../../../pLogicTestData/LIS/
    Cmd: TableHistogram.py -k --name=FILM -l40 --col=DEST ../../../pLogicTestData/LIS/
    2011-05-27 09:23:23,870 ERROR    Can not read LIS file ../../../pLogicTestData/LIS/13576.S1 with error: Can not fit integer number of frames length 120 into LR length 824, modulo 104 [indirect size 0].
    2011-05-27 09:23:24,649 ERROR    Can not read LIS file ../../../pLogicTestData/LIS/13610.S1 with error: Can not fit integer number of frames length 7176 into LR length 13354, modulo 6178 [indirect size 0].
    ...

GCOD::

    ======================== Count of all table entries =======================
    {
    "(34, b'FILM', b'GCOD', b'BBB ')": 2,
    "(34, b'FILM', b'GCOD', b'E1E ')": 5,
    "(34, b'FILM', b'GCOD', b'E20 ')": 26,
    "(34, b'FILM', b'GCOD', b'E2E ')": 40,
    "(34, b'FILM', b'GCOD', b'E3E ')": 3,
    "(34, b'FILM', b'GCOD', b'E40 ')": 2,
    "(34, b'FILM', b'GCOD', b'E4E ')": 3,
    "(34, b'FILM', b'GCOD', b'EB0 ')": 2,
    "(34, b'FILM', b'GCOD', b'EEB ')": 22,
    "(34, b'FILM', b'GCOD', b'EEE ')": 225,
    "(34, b'FILM', b'GCOD', b'LLLL')": 1,
    }
    ====================== Count of all table entries END =====================

GDEC::

    ======================== Count of all table entries =======================
    {
    "(34, b'FILM', b'GDEC', b'--- ')": 10,
    "(34, b'FILM', b'GDEC', b'----')": 227,
    "(34, b'FILM', b'GDEC', b'-1- ')": 2,
    "(34, b'FILM', b'GDEC', b'-2- ')": 6,
    "(34, b'FILM', b'GDEC', b'-2--')": 32,
    "(34, b'FILM', b'GDEC', b'-3- ')": 3,
    "(34, b'FILM', b'GDEC', b'-4- ')": 10,
    "(34, b'FILM', b'GDEC', b'-4--')": 26,
    "(34, b'FILM', b'GDEC', b'1111')": 1,
    "(34, b'FILM', b'GDEC', b'EEE ')": 14,
    }
    ====================== Count of all table entries END =====================

DEST::

    ======================== Count of all table entries =======================
    {
    "(34, b'FILM', b'DEST', b'NEIT')": 66,
    "(34, b'FILM', b'DEST', b'PF1 ')": 124,
    "(34, b'FILM', b'DEST', b'PF2 ')": 125,
    "(34, b'FILM', b'DEST', b'PF5 ')": 1,
    "(34, b'FILM', b'DEST', b'PF6 ')": 5,
    "(34, b'FILM', b'DEST', b'PF8 ')": 1,
    "(34, b'FILM', b'DEST', b'PFA ')": 1,
    "(34, b'FILM', b'DEST', b'PFD ')": 2,
    "(34, b'FILM', b'DEST', b'PFE ')": 3,
    "(34, b'FILM', b'DEST', b'PFJ ')": 2,
    "(34, b'FILM', b'DEST', b'PFK ')": 1,
    }
    ====================== Count of all table entries END =====================

DSCA::

    ======================== Count of all table entries =======================
    {
    "(34, b'FILM', b'DSCA', b'D200')": 156,
    "(34, b'FILM', b'DSCA', b'D500')": 17,
    "(34, b'FILM', b'DSCA', b'DM  ')": 76,
    "(34, b'FILM', b'DSCA', b'S5  ')": 82,
    }
    ====================== Count of all table entries END =====================

"""

__author__  = 'Paul Ross'
__date__    = '2011-03-21'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

#import time
#import sys
import logging
import re
#import collections
#from optparse import OptionParser

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import Mnem
from TotalDepth.util.plot import Coord
from TotalDepth.util.plot import Track

class ExceptionFILMCfg(ExceptionTotalDepthLIS):
    """Specialisation of exception for this module."""
    pass

class ExceptionPhysFilmCfg(ExceptionFILMCfg):
    """Specialisation of exception for PhysFilmCfg."""
    pass

class ExceptionFilmCfgLISRead(ExceptionFILMCfg):
    """Specialisation of exception for FilmCfgLISRead in this module."""
    pass

class PhysFilmCfg(object):
    """Contains the configuration equivalent to a single line in a FILM table.

    theName is a hashable.

    theTracks is a list of Track.Track objects.

    theX is an integer scale.
    """
    # Matches for examples b'T23 ', b'FD  '
    # Groups there are these:
    # 1. None | b'LH' | b'RH'
    # 2. T | F - Three or four tracks
    # 3. Primary track number
    # 4. None or secondary track number
    # b'2   ' and b'3   ' or variants, e.g. b'2\x00\x00\x00' and b'3\x00\x00\x00'
    RE_TRAC = re.compile(b'^(LH|RH)*([TF])(\d|D)(\d)*\s*$')
    def __init__(self, theName, theTracks, theDest, theX):
        """Constructor.
        theName is a hashable.
        theTracks is a list of Track.Track objects.
        theX is an integer scale.
        """
        logging.debug('PhysFilmCfg: name="{!s:s}" {:d} tracks dest={!s:s} scale={:d}'.format(
                theName, len(theTracks), theDest, theX,
        ))
        self._name = theName
        self._trackS = theTracks
        self._dest = theDest
        # Integer scale
        self._xScale = theX
        
    @property
    def name(self):
        """Name of the FILM."""
        return self._name
    
    @property
    def xScale(self):
        """The FILM X axis scale as a number."""
        return self._xScale
    
    def __len__(self):
        """Number of Track.Track objects."""
        return len(self._trackS)
    
    def __getitem__(self, i):
        """Returns the Track.Track object at position i."""
        return self._trackS[i]
    
    def genTracks(self):
        """Generate all tracks."""
        for t in self._trackS:
            yield t

    def interpretTrac(self, theTracStr):
        """Turns TRAC information into left/right positions as Cooord.Dim()
        objects and the number of half-tracks of the start and half-tracks
        covered. The later two values are used for stacking and packing the
        plot header and footer scales so that they take the minimum space.
        
        e.g. b'T23 ' returns:
        (the left position of T2, right of T3, 4, 4).
        
        e.g. b'T2 ' returns:
        (the left position of T2, right of T2, 4, 2).
        
        Note: There is some fudging going on here"""
        assert(theTracStr is not None)
        # Matching on something like b'^(LH|RH)*([TF])(\d|D)(\d)*\s*$'
        # Gives:
        # 1. None | b'LH' | b'RH'
        # 2. T | F - Three or four tracks
        # 3. Primary track number
        # 4. None or secondary track number
        mtch = self.RE_TRAC.match(theTracStr)
        # TODO: There is some bad code here as when there is no match sometimes
        # we return None and sometimes we raise. Leave a failed test in the test
        # code for the moment.
        if mtch is None:
            raise ExceptionPhysFilmCfg('PhysFilmCfg.interpretTrac(): No TRAC match on {:s}'.format(str(theTracStr)))
#        print(self, 'theTracStr', theTracStr, mtch.groups())
        tIdxFrom = 0
        # group(2) is mandatory b'D' or an integer
        if mtch.group(3) == b'D':
            # Search for first X axis track
            for tIdxFrom, t in enumerate(self._trackS):
                if t.plotXAlpha:
                    break
        else:
            tIdxFrom = int(mtch.group(3))
            if mtch.group(2) == b'T':
                # Adjust track notation from 1... to 0...
                # T1, TD, T2, T3 converts to: 1, ?, 2, 3 which should be: 0, 1, 2, 3
                if tIdxFrom == 1:
                    tIdxFrom = 0
            else:
                assert(mtch.group(2) == b'F')
                # tIdxFrom is OK 1..4
                pass
        halfTrackStart = 2 * tIdxFrom
        try:
            # Get left/right as Coord.Dim() objects
            pL = self[tIdxFrom].left
            pR = self[tIdxFrom].right
        except IndexError:
            raise ExceptionPhysFilmCfg('PhysFilmCfg.interpretTrac(): No first TRAC found with {:s}'.format(str(theTracStr)))
        if mtch.group(1) is not None:
            # LH or RH
            # Compute centre line of track
            cLine = (pL + pR).divide(2)
            if mtch.group(1) == b'LH':
                # Left
                pR = cLine
            else:
                # Right
                pL = cLine
                halfTrackStart += 1
            numHalfTracks = 1
            tIdxTo = tIdxFrom + 1
        else:
            if mtch.group(4) is not None:
                tIdxTo = int(mtch.group(4))
                try:
                    #  Extend right as Coord.Dim() objects
                    pR = self[tIdxTo].right
                except IndexError:
                    raise ExceptionPhysFilmCfg('PhysFilmCfg.interpretTrac(): No second TRAC found with {:s}'.format(str(theTracStr)))
                numHalfTracks = 2 * (tIdxTo + 1 - tIdxFrom)
            else:
                numHalfTracks = 2
        # Return the left/right physical locations as Coord.Dim() objects
        return pL, pR, halfTrackStart, numHalfTracks

class PhysFilmCfgLISRead(PhysFilmCfg):
    """Tracks from a LIS FILM table, essentially the pair of GCOD and GDEC
    defines the left-to-right layout of the plot.
    
    Grid codes from analysis above:
    b'BBB ',  b'E1E ', b'E20 ', b'E2E ', b'E3E ', b'E40 ', b'E4E ', b'EB0 ', b'EEB ', b'EEE ', b'LLLL'
    
    The DSCA defines the top-to-bottom nature of the plot. 
    DSCA codes from analysis above:
    b'D200', b'D500', b'DM  ', b'S5  '
    
    But we can guess some others...
    """
    # The map of FILM track descriptions [pair of (name, decades)] to internal track representations
    GCOD_GDEC_MAP = {
        # T23 is 4 decades
        (b'E20 ', b'-4--') : [
                Track.Track(
                    leftPos=Coord.Dim(0.0, 'in'), 
                    rightPos=Coord.Dim(2.4, 'in'),
                    gridGn=Track.genLinear10
                ),
                Track.Track(
                    leftPos=Coord.Dim(2.4, 'in'), 
                    rightPos=Coord.Dim(3.2, 'in'),
                    gridGn=None,
                    plotXLines=False,
                    plotXAlpha=True,
                ),
                Track.Track(
                    leftPos=Coord.Dim(3.2, 'in'), 
                    rightPos=Coord.Dim(5.6, 'in'),
                    gridGn=Track.genLog10Decade2Start2
                ),
                Track.Track(
                    leftPos=Coord.Dim(5.6, 'in'), 
                    rightPos=Coord.Dim(8, 'in'),
                    gridGn=Track.genLog10Decade2Start2
                ),
            ],
        (b'E2E ', b'-1--') : [
                Track.Track(
                    leftPos=Coord.Dim(0.0, 'in'), 
                    rightPos=Coord.Dim(2.4, 'in'),
                    gridGn=Track.genLinear10
                ),
                Track.Track(
                    leftPos=Coord.Dim(2.4, 'in'), 
                    rightPos=Coord.Dim(3.2, 'in'),
                    gridGn=None,
                    plotXLines=False,
                    plotXAlpha=True,
                ),
                Track.Track(
                    leftPos=Coord.Dim(3.2, 'in'), 
                    rightPos=Coord.Dim(5.6, 'in'),
                    gridGn=Track.genLog10Decade1Start2
                ),
                Track.Track(
                    leftPos=Coord.Dim(5.6, 'in'), 
                    rightPos=Coord.Dim(8, 'in'),
                    gridGn=Track.genLinear10
                ),
            ],
        (b'E2E ', b'-2--') : [
                Track.Track(
                    leftPos=Coord.Dim(0.0, 'in'), 
                    rightPos=Coord.Dim(2.4, 'in'),
                    gridGn=Track.genLinear10
                ),
                Track.Track(
                    leftPos=Coord.Dim(2.4, 'in'), 
                    rightPos=Coord.Dim(3.2, 'in'),
                    gridGn=None,
                    plotXLines=False,
                    plotXAlpha=True,
                ),
                Track.Track(
                    leftPos=Coord.Dim(3.2, 'in'), 
                    rightPos=Coord.Dim(5.6, 'in'),
                    gridGn=Track.genLog10Decade2Start2
                ),
                Track.Track(
                    leftPos=Coord.Dim(5.6, 'in'), 
                    rightPos=Coord.Dim(8, 'in'),
                    gridGn=Track.genLinear10
                ),
            ],
        (b'E3E ', b'-3--') : [
                Track.Track(
                    leftPos=Coord.Dim(0.0, 'in'), 
                    rightPos=Coord.Dim(2.4, 'in'),
                    gridGn=Track.genLinear10
                ),
                Track.Track(
                    leftPos=Coord.Dim(2.4, 'in'), 
                    rightPos=Coord.Dim(3.2, 'in'),
                    gridGn=None,
                    plotXLines=False,
                    plotXAlpha=True,
                ),
                Track.Track(
                    leftPos=Coord.Dim(3.2, 'in'), 
                    rightPos=Coord.Dim(5.6, 'in'),
                    gridGn=Track.genLog10Decade3
                ),
                Track.Track(
                    leftPos=Coord.Dim(5.6, 'in'), 
                    rightPos=Coord.Dim(8, 'in'),
                    gridGn=Track.genLinear10
                ),
            ],
        (b'E4E ', b'-4--') : [
                Track.Track(
                    leftPos=Coord.Dim(0.0, 'in'), 
                    rightPos=Coord.Dim(2.4, 'in'),
                    gridGn=Track.genLinear10
                ),
                Track.Track(
                    leftPos=Coord.Dim(2.4, 'in'), 
                    rightPos=Coord.Dim(3.2, 'in'),
                    gridGn=None,
                    plotXLines=False,
                    plotXAlpha=True,
                ),
                Track.Track(
                    leftPos=Coord.Dim(3.2, 'in'), 
                    rightPos=Coord.Dim(5.6, 'in'),
                    gridGn=Track.genLog10Decade4
                ),
                Track.Track(
                    leftPos=Coord.Dim(5.6, 'in'), 
                    rightPos=Coord.Dim(8, 'in'),
                    gridGn=Track.genLinear10
                ),
            ],
        (b'EEE ', b'----') : [
                Track.Track(
                    leftPos=Coord.Dim(0.0, 'in'), 
                    rightPos=Coord.Dim(2.4, 'in'),
                    gridGn=Track.genLinear10
                ),
                Track.Track(
                    leftPos=Coord.Dim(2.4, 'in'), 
                    rightPos=Coord.Dim(3.2, 'in'),
                    gridGn=None,
                    plotXLines=False,
                    plotXAlpha=True,
                ),
                Track.Track(
                    leftPos=Coord.Dim(3.2, 'in'), 
                    rightPos=Coord.Dim(5.6, 'in'),
                    gridGn=Track.genLinear10
                ),
                Track.Track(
                    leftPos=Coord.Dim(5.6, 'in'), 
                    rightPos=Coord.Dim(8, 'in'),
                    gridGn=Track.genLinear10
                ),
            ],
        (b'EEB ', b'----') : [
                Track.Track(
                    leftPos=Coord.Dim(0.0, 'in'), 
                    rightPos=Coord.Dim(2.4, 'in'),
                    gridGn=Track.genLinear10
                ),
                Track.Track(
                    leftPos=Coord.Dim(2.4, 'in'), 
                    rightPos=Coord.Dim(3.2, 'in'),
                    gridGn=None,
                    plotXLines=False,
                    plotXAlpha=True,
                ),
                Track.Track(
                    leftPos=Coord.Dim(3.2, 'in'), 
                    rightPos=Coord.Dim(5.6, 'in'),
                    gridGn=Track.genLinear10
                ),
                Track.Track(
                    leftPos=Coord.Dim(5.6, 'in'), 
                    rightPos=Coord.Dim(8, 'in'),
                    gridGn=None
                ),
            ],
        (b'EBE ', b'----') : [
                Track.Track(
                    leftPos=Coord.Dim(0.0, 'in'), 
                    rightPos=Coord.Dim(2.4, 'in'),
                    gridGn=Track.genLinear10
                ),
                Track.Track(
                    leftPos=Coord.Dim(2.4, 'in'), 
                    rightPos=Coord.Dim(3.2, 'in'),
                    gridGn=None,
                    plotXLines=False,
                    plotXAlpha=True,
                ),
                Track.Track(
                    leftPos=Coord.Dim(3.2, 'in'), 
                    rightPos=Coord.Dim(5.6, 'in'),
                    gridGn=None
                ),
                Track.Track(
                    leftPos=Coord.Dim(5.6, 'in'), 
                    rightPos=Coord.Dim(8, 'in'),
                    gridGn=Track.genLinear10
                ),
            ],
        # All blank
        (b'BBB ', b'----') : [
                Track.Track(
                    leftPos=Coord.Dim(0.0, 'in'), 
                    rightPos=Coord.Dim(2.4, 'in'),
                    gridGn=None
                ),
                Track.Track(
                    leftPos=Coord.Dim(2.4, 'in'), 
                    rightPos=Coord.Dim(3.2, 'in'),
                    gridGn=None,
                    plotXLines=False,
                    plotXAlpha=True,
                ),
                Track.Track(
                    leftPos=Coord.Dim(3.2, 'in'), 
                    rightPos=Coord.Dim(5.6, 'in'),
                    gridGn=None
                ),
                Track.Track(
                    leftPos=Coord.Dim(5.6, 'in'), 
                    rightPos=Coord.Dim(8, 'in'),
                    gridGn=None
                ),
            ],
        # Four track. Depth 1in, 4 tracks at 1.75in
        # Alternate could be depth 0.5in, 4 tracks at 1.875in
        (b'LLLL', b'1111') : [
                Track.Track(
                    leftPos=Coord.Dim(0.0, 'in'), 
                    rightPos=Coord.Dim(1.0, 'in'),
                    gridGn=None,
                    plotXLines=False,
                    plotXAlpha=True,
                ),
                Track.Track(
                    leftPos=Coord.Dim(1.0, 'in'), 
                    rightPos=Coord.Dim(2.75, 'in'),
                    gridGn=Track.genLinear10
                ),
                Track.Track(
                    leftPos=Coord.Dim(2.75, 'in'), 
                    rightPos=Coord.Dim(4.5, 'in'),
                    gridGn=Track.genLinear10
                ),
                Track.Track(
                    leftPos=Coord.Dim(4.5, 'in'), 
                    rightPos=Coord.Dim(6.25, 'in'),
                    gridGn=Track.genLinear10
                ),
                Track.Track(
                    leftPos=Coord.Dim(6.25, 'in'), 
                    rightPos=Coord.Dim(8, 'in'),
                    gridGn=Track.genLinear10
                ),
            ],
    }
    # Alternate mappings that are deemed 'equivalent'
    GCOD_GDEC_ALT_MAP = {
        # Read from 2953.S13
        (b'EEE ', b'EEE-') : GCOD_GDEC_MAP[(b'EEE ', b'----')],
        # Read from 12988.S3
        (b'EEB ', b'EEE-') : GCOD_GDEC_MAP[(b'EEB ', b'----')],
        # Read from 200099.S07 - ignore for the moment
        (b'EB0 ', b'----') : GCOD_GDEC_MAP[(b'EBE ', b'----')],
        #
        (b'E1E ', b'-4--') : GCOD_GDEC_MAP[(b'E4E ', b'-4--')],
        # Read from 300026.S01
        (b'E40 ', b'-4--') : GCOD_GDEC_MAP[(b'E20 ', b'-4--')],
    }
    #: X axis scale from a LIS FILM table
    #: DSCA codes from analysis above:
    #: b'D200', b'D500', b'DM  ', b'S5  '
    #: But we can guess some others...
    DSCA_MAP = {
        b'D20 '     : 20,
        b'D40 '     : 40,
        b'D200'     : 200,
        b'D240 '    : 240,
        b'D500'     : 500,
        b'DM  '     : 1000,
        # 5 inches per 100 feet
        b'S5  '     : 12*100//5,
        # 2 inches per 100 feet
        b'S2  '     : 12*100//2,
    }
    def __init__(self, theRow):
        """Reads a LogiRec.TableRow object and populates a CurveCfg.
        
        Example::
        
            MNEM  GCOD  GDEC  DEST  DSCA
            -----------------------------
            1     E20   -4--  PF1   D200
        """
        myName = Mnem.Mnem(theRow[b'MNEM'].value)
        myTrackS = self._retTracks(theRow[b'GCOD'].value, theRow[b'GDEC'].value)
        myDest = theRow[b'DEST'].value
        myDscaleKey = theRow[b'DSCA'].value
        super().__init__(
            theName=myName,
            theTracks=myTrackS,
            theDest=myDest,
            theX=self.DSCA_MAP[myDscaleKey])

    def _retTracks(self, theGCOD, theGDEC):
        """Given a GCOD, GDEC pair this returns a list of Track.Track() objects or None."""
        # Kludge: Replace a trailing ' ' with a '-' so that the key look up works
        # when the '-' is missing.
        if len(theGDEC) == 4 and theGDEC[3:] == b' ':
            theGDEC = theGDEC[:3] + b'-'
        try:
            return self.GCOD_GDEC_MAP[(theGCOD, theGDEC)]
        except KeyError:
            # Try the alternate map
            logging.warning(
                'PhysFilmCfgLISRead._retTracks():'
                ' No key for GCOD={!r:s} GDEC={!r:s}, falling back to alternate.'.format(theGCOD, theGDEC)
            )
            try:
                return self.GCOD_GDEC_ALT_MAP[(theGCOD, theGDEC)]
            except KeyError:
                pass
        raise ExceptionFILMCfg(
            'PhysFilmCfgLISRead._retTracks(): No key for GCOD={!r:s} GDEC={!r:s}'.format(theGCOD, theGDEC)
        )

    def supportedFilmTracks(self):
        """A list of supported film (name, decade) pairs."""
        return sorted(self.GCOD_GDEC_MAP.keys())

class FilmCfg(object):
    """Contains the configuration equivalent to a complete FILM table."""
    def __init__(self):
        # Map of {mnem : PhysFilmCfg, ...}
        # i.e. a dictionary of lines in the FILM table
        self._plotCfgMap = {}
        
    def add(self, k, thePfc):
        """Add a PhysFilmCfg object to the map with key k, typically a FILM
        mnemonic in bytes such as Mnem.Mnem(b'1   ') or
        some other ID such as a string, the filename of an XML file."""
        if k in self._plotCfgMap:
            logging.warning('FilmCfg.add(): Ignoring duplicate film key="{:s}'.format(k))
        else:
            self._plotCfgMap[k] = thePfc

    def keys(self):
        """All FILM Mnemonics."""
        return self._plotCfgMap.keys()
    
    def __len__(self):
        """Number of unique film destination names."""
        return len(self._plotCfgMap)
    
    def __getitem__(self, name):
        """Returns the PhysFilmCfg object corresponding to name - a Mnem() object.
        Will raise KeyError if not exact match. See retFilmDest() for an API that can
        handle curve destinations of BOTH, ALL etc."""
        #print(self._plotCfgMap)
        return self._plotCfgMap[name]
    
    def __contains__(self, name):
        """Membership test."""
        return name in self._plotCfgMap
    
    def retAllFILMDestS(self, curveDestID):
        """Returns an unordered list of FILM destinations for a curve destination.
        For example if curveDestID is b'BOTH' this might return [b'2   ', b'1   ']
        """
        raise NotImplementedError()
    
    def retFILMDest(self, filmDestID, curveDestID):
        """Returns a PhysFilmCfg object by matching curveDestID to the filmDestID.
        Returns None on failure. For LIS curveDestID can be 1, BOTH, ALL, NEIT etc.
        This is commonly used by the PRESCfg module so that interpretTrac() can
        be called on the result and thus build up a map of track positions for
        all possible logical film outputs."""
        raise  NotImplementedError()
                
    def interpretTrac(self, filmDestID, curveDestID, trackStr):
        """Given a film destination ID and a curve destination (which could be
        b'ALL') and a track string (e.g. b'T23') this returns the left/right
        positions as Cooord.Dim() objects and the number of half-tracks of the
        start and half-tracks covered (used for plot header and footer scales).
        Returns None if there is no match for the filmDestID/curveDestID (for
        example if curveDestID is b'NEIT'). 
        e.g. (b'1   ', b'BOTH', b'T23 ') returns:
        (the left position of T2, right of T3, 4, 4).
        """
        myPfc = self.retFILMDest(filmDestID, curveDestID)
        if myPfc is not None:
            return myPfc.interpretTrac(trackStr)

class FilmCfgLISRead(FilmCfg):
    """Interprets a FILM table from a LIS Logical Record."""
    def __init__(self, theLr):
        """Reads a LogiRec.Table object and creates a PhysFilmCfgLISRead for
        each row.
        
        Typical FILM table::
        
            MNEM  GCOD  GDEC  DEST  DSCA
            -----------------------------
            1     E20   -4--  PF1   D200
            2     EEE   ----  PF2   D200
        """
        super().__init__()
        if theLr.type != LogiRec.LR_TYPE_WELL_DATA:
            raise ExceptionFilmCfgLISRead('FilmCfgLISRead.__init__(): LR type={:d}, expected {:d}'.format(theLr.type, LogiRec.LR_TYPE_WELL_DATA))
        if theLr.value != b'FILM':
            raise ExceptionFilmCfgLISRead('FilmCfgLISRead.__init__(): LR Table not a CONS table type "FILM" but a {!r:s}.'.format(theLr.value))
        for aRow in theLr.genRows():
            self.add(Mnem.Mnem(aRow.value), PhysFilmCfgLISRead(aRow))
        
    def retAllFILMDestS(self, curveDestID):
        """Returns an unordered list of FILM destinations for a curve destination.
        
        For example if curveDestID is b'BOTH' this might return [b'2   ', b'1   ']
        """
        retList = []
        if curveDestID in self._plotCfgMap:
            retList = [curveDestID]
        elif curveDestID == Mnem.Mnem(b'BOTH') and len(self._plotCfgMap) == 2:
            retList = list(self._plotCfgMap.keys())
        elif curveDestID == Mnem.Mnem(b'ALL'):
            retList = list(self._plotCfgMap.keys())
        else:
            retList = []
            # Decompose, for example for b'123 '
            for aBy in curveDestID:
                aMnem = Mnem.Mnem(bytes([aBy]))
                if aMnem in self._plotCfgMap:
                    retList.append(aMnem)
        return retList
    
    def retFILMDest(self, filmDestID, curveDestID):
        """Returns a PhysFilmCfg object by matching curveDestID to the filmDestID.
        Returns None on failure. curveDestID can be 1, BOTH, ALL, NEIT etc.
        
        This is commonly used by the PRESCfg module so that interpretTrac() can
        be called on the result and thus build up a map of track positions for
        all possible logical film outputs."""
        assert(filmDestID in self._plotCfgMap), '{:s} not in {:s}'.format(filmDestID, [str(k) for k in self._plotCfgMap.keys()])
        if filmDestID in self.retAllFILMDestS(curveDestID):
            return self._plotCfgMap[filmDestID]
        return None
