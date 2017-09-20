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
"""Holds all the information to draw a curve on a plot.

TODO: Split this to:

* Generic: PRESCfg
* LIS specific: PRESCfgLIS
* XML specific: PRESCfgXML

Created on 20 Mar 2011

Examples of PRES records summaries::

     Table record (type 34) type: PRES
    
    MNEM  OUTP  STAT  TRAC  CODI  DEST  MODE      FILT          LEDG          REDG
    -----------------------------------------------------------------------------------
                                                                          
    SP    SP    ALLO  T1    LLIN  1     SHIF      0.500000      -80.0000       20.0000 
    CALI  CALI  ALLO  T1    LDAS  1     SHIF      0.500000       5.00000       15.0000 
    MINV  MINV  DISA  T1    LLIN  1     SHIF      0.500000       30.0000       0.00000 
    MNOR  MNOR  DISA  T1    LDAS  1     SHIF      0.500000       30.0000       0.00000 
    LLD   LLD   ALLO  T23   LDAS  1     GRAD      0.500000      0.200000       2000.00 
    LLDB  LLD   ALLO  T2    HDAS  1     GRAD      0.500000       2000.00       200000. 
    LLG   LLG   DISA  T23   LDAS  1     GRAD      0.500000      0.200000       2000.00 
    LLGB  LLG   DISA  T2    HDAS  1     GRAD      0.500000       2000.00       200000. 
    LLS   LLS   ALLO  T23   LSPO  1     GRAD      0.500000      0.200000       2000.00 
    LLSB  LLS   ALLO  T2    HSPO  1     GRAD      0.500000       2000.00       200000. 
    MSFL  MSFL  ALLO  T23   LLIN  1     GRAD      0.500000      0.200000       2000.00 
    11    DUMM  DISA  T1    LLIN  NEIT  NB        0.500000       0.00000       1.00000 
    12    DUMM  DISA  T1    LLIN  NEIT  NB        0.500000       0.00000       1.00000 
    13    DUMM  DISA  T1    LLIN  NEIT  NB        0.500000       0.00000       1.00000 
    14    DUMM  DISA  T1    LLIN  NEIT  NB        0.500000       0.00000       1.00000 
    15    DUMM  DISA  T1    LLIN  NEIT  NB        0.500000       0.00000       1.00000 
    16    DUMM  DISA  T1    LLIN  NEIT  NB        0.500000       0.00000       1.00000 
    17    DUMM  DISA  T1    LLIN  NEIT  NB        0.500000       0.00000       1.00000 
    18    DUMM  DISA  T1    LLIN  NEIT  NB        0.500000       0.00000       1.00000 
    19    DUMM  DISA  T1    LLIN  NEIT  NB        0.500000       0.00000       1.00000 
    
    Table record (type 34) type: PRES
    
    MNEM  OUTP  STAT  TRAC  CODI  DEST  MODE      FILT          LEDG          REDG
    -----------------------------------------------------------------------------------
    NPHI  NPHI  ALLO  T23   LDAS  1     SHIF      0.500000      0.450000     -0.150000
    DRHO  DRHO  ALLO  T3    LSPO  1     NB        0.500000     -0.250000      0.250000
    PEF   PEF   ALLO  T23   LGAP  1     SHIF      0.500000       0.00000       10.0000
    SGR         DISA  T1    LLIN  1     SHIF      0.500000       0.00000       300.000
    CGR         DISA  T1    LGAP  1     SHIF      0.500000       0.00000       300.000
    TENS  TENS  DISA  T3    LGAP  1     SHIF      0.500000       14000.0       4000.00
    CAL   CALI  ALLO  T1    LSPO  1     SHIF      0.500000       5.00000       15.0000
    BS    BS    DISA  T1    LGAP  1     SHIF      0.500000       5.00000       15.0000
    FFLS  FFLS  DISA  T1    LLIN  2     NB        0.500000     -0.150000      0.150000
    FFSS  FFSS  DISA  T1    LDAS  2     NB        0.500000     -0.150000      0.150000
    LSHV  LSHV  DISA  T3    LLIN  2     WRAP      0.500000       2150.00       2250.00
    SSHV  SSHV  DISA  T3    LDAS  2     WRAP      0.500000       1950.00       2050.00
    FLS   FLS   DISA  T2    LLIN  2     SHIF      0.500000       0.00000       150.000
    FSS   FSS   DISA  T2    LDAS  2     SHIF      0.500000       0.00000       150.000
    RHOB  RHOB  ALLO  T23   LLIN  1     SHIF      0.500000       1.95000       2.95000
    PHIX  PHIX  ALLO  T1    LLIN  1     NB        0.500000      0.500000       0.00000

TRAC nomenclature:

``<LH | RH> T n <m>``

Or as a regex: ``re.compile(r'^(LH|RH)*T(\d)(\d)*\s*$')``

But this is handled by FILMCfg.

Example::

    $ python3 TableHistogram.py -k --name=PRES -l40 --col=TRAC ../../../pLogicTestData/LIS/
    Cmd: TableHistogram.py -k --name=PRES -l40 --col=TRAC ../../../pLogicTestData/LIS/
    2011-05-27 09:26:12,324 ERROR    Can not create Logical Record, error: can't convert negative value to unsigned int
    2011-05-27 09:26:12,335 ERROR    Can not create Logical Record, error: can't convert negative value to unsigned int
    2011-05-27 09:26:12,346 ERROR    Can not create Logical Record, error: can't convert negative value to unsigned int
    2011-05-27 09:26:13,086 ERROR    Can not read LIS file ../../../pLogicTestData/LIS/13576.S1 with error: Can not fit integer number of frames length 120 into LR length 824, modulo 104 [indirect size 0].
    2011-05-27 09:26:13,907 ERROR    Can not read LIS file ../../../pLogicTestData/LIS/13610.S1 with error: Can not fit integer number of frames length 7176 into LR length 13354, modulo 6178 [indirect size 0].
    ======================== Count of all table entries =======================
    {"(34, b'PRES', b'TRAC', b'F1  ')": 4,
     "(34, b'PRES', b'TRAC', b'F2  ')": 4,
     "(34, b'PRES', b'TRAC', b'F3  ')": 4,
     "(34, b'PRES', b'TRAC', b'F4  ')": 3,
     "(34, b'PRES', b'TRAC', b'FD  ')": 4,
     "(34, b'PRES', b'TRAC', b'LHT1')": 4,
     "(34, b'PRES', b'TRAC', b'LHT2')": 8,
     "(34, b'PRES', b'TRAC', b'LHT3')": 59,
     "(34, b'PRES', b'TRAC', b'RHT1')": 4,
     "(34, b'PRES', b'TRAC', b'RHT2')": 22,
     "(34, b'PRES', b'TRAC', b'RHT3')": 63,
     "(34, b'PRES', b'TRAC', b'T1  ')": 2363,
     "(34, b'PRES', b'TRAC', b'T2  ')": 354,
     "(34, b'PRES', b'TRAC', b'T23 ')": 192,
     "(34, b'PRES', b'TRAC', b'T3  ')": 178,
     "(34, b'PRES', b'TRAC', b'TD  ')": 93,
     "(34, b'PRES', b'TRAC', b'XXXX')": 18}
    ====================== Count of all table entries END =====================

DEST::

    ======================== Count of all table entries =======================
    {"(34, b'PRES', b'DEST', b'1   ')": 457,
     "(34, b'PRES', b'DEST', b'123 ')": 2,
     "(34, b'PRES', b'DEST', b'134 ')": 20,
     "(34, b'PRES', b'DEST', b'2   ')": 139,
     "(34, b'PRES', b'DEST', b'5   ')": 26,
     "(34, b'PRES', b'DEST', b'6   ')": 122,
     "(34, b'PRES', b'DEST', b'8   ')": 16,
     "(34, b'PRES', b'DEST', b'A   ')": 19,
     "(34, b'PRES', b'DEST', b'ALL ')": 4,
     "(34, b'PRES', b'DEST', b'BOTH')": 774,
     "(34, b'PRES', b'DEST', b'D   ')": 63,
     "(34, b'PRES', b'DEST', b'E   ')": 60,
     "(34, b'PRES', b'DEST', b'J   ')": 52,
     "(34, b'PRES', b'DEST', b'K   ')": 13,
     "(34, b'PRES', b'DEST', b'NEIT')": 1610}
    ====================== Count of all table entries END =====================

MODE::

    $ python3 TableHistogram.py -k --name=PRES -l40 --col=MODE ../../../pLogicTestData/LIS/
    Cmd: TableHistogram.py -k --name=PRES -l40 --col=MODE ../../../pLogicTestData/LIS/
    2011-06-02 08:22:54,839 ERROR    Can not read LIS file ../../../pLogicTestData/LIS/13576.S1 with error: Can not fit integer number of frames length 120 into LR length 824, modulo 104 [indirect size 0].
    2011-06-02 08:22:55,671 ERROR    Can not read LIS file ../../../pLogicTestData/LIS/13610.S1 with error: Can not fit integer number of frames length 7176 into LR length 13354, modulo 6178 [indirect size 0].
    ======================== Count of all table entries =======================
    {"(34, b'PRES', b'MODE', b'GRAD')": 245,
     "(34, b'PRES', b'MODE', b'NB  ')": 2329,
     "(34, b'PRES', b'MODE', b'SHIF')": 597,
     "(34, b'PRES', b'MODE', b'SWF ')": 3,
     "(34, b'PRES', b'MODE', b'VDLN')": 3,
     "(34, b'PRES', b'MODE', b'WRAP')": 186,
     "(34, b'PRES', b'MODE', b'X10 ')": 10}
    ====================== Count of all table entries END =====================

COLO::

    ======================== Count of all table entries =======================
    {"(34, b'PRES', b'COLO', b'000 ')": 173,
     "(34, b'PRES', b'COLO', b'002 ')": 3,
     "(34, b'PRES', b'COLO', b'003 ')": 6,
     "(34, b'PRES', b'COLO', b'004 ')": 33,
     "(34, b'PRES', b'COLO', b'014 ')": 6,
     "(34, b'PRES', b'COLO', b'020 ')": 9,
     "(34, b'PRES', b'COLO', b'021 ')": 8,
     "(34, b'PRES', b'COLO', b'030 ')": 34,
     "(34, b'PRES', b'COLO', b'034 ')": 2,
     "(34, b'PRES', b'COLO', b'044 ')": 6,
     "(34, b'PRES', b'COLO', b'104 ')": 3,
     "(34, b'PRES', b'COLO', b'134 ')": 14,
     "(34, b'PRES', b'COLO', b'203 ')": 3,
     "(34, b'PRES', b'COLO', b'221 ')": 3,
     "(34, b'PRES', b'COLO', b'312 ')": 10,
     "(34, b'PRES', b'COLO', b'400 ')": 44,
     "(34, b'PRES', b'COLO', b'404 ')": 6,
     "(34, b'PRES', b'COLO', b'420 ')": 9,
     "(34, b'PRES', b'COLO', b'430 ')": 17,
     "(34, b'PRES', b'COLO', b'AQUA')": 3,
     "(34, b'PRES', b'COLO', b'BLAC')": 1260,
     "(34, b'PRES', b'COLO', b'BLUE')": 8,
     "(34, b'PRES', b'COLO', b'GREE')": 37,
     "(34, b'PRES', b'COLO', b'RED ')": 12}
    ====================== Count of all table entries END =====================

What are these numbers, RGB Base 5?


Track names F1 to F4 and FD.

This seems to be the nomenclature for four track plots. For example::

    Table record (type 34) type: FILM
    
    MNEM  GCOD  GDEC  DEST  DSCA
    -----------------------------
                            
    8     EB0   ---   PF8   D200
    A     LLLL  1111  PFA   DM  
    E     E4E   -4-   PFE   D200
    K     E4E   -4-   PFK   D500
    
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

"""

__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

#import time
#import sys
import logging
#import re
import math
#import numbers
import collections

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import LogiRec
from TotalDepth.LIS.core import Mnem
from TotalDepth.util.plot import Stroke
from TotalDepth.util.plot import FILMCfg

class ExceptionPRESCfg(ExceptionTotalDepthLIS):
    """Specialisation of exception for this module."""
    pass

class ExceptionLineTransBase(ExceptionTotalDepthLIS):
    """Specialisation of exception for LineTransBase and descendants."""
    pass

class ExceptionLineTransBaseMath(ExceptionLineTransBase):
    """For LineTransBase and descendants where math errors occur."""
    pass

class ExceptionPRESCfgLISRead(ExceptionPRESCfg):
    """Specialisation of exception for this module."""
    pass

class ExceptionPresCfg(ExceptionPRESCfg):
    """Specialisation of exception for PresCfg."""
    pass

class ExceptionCurveCfg(ExceptionPRESCfg):
    """Specialisation of exception for CurveCfg."""
    pass

class ExceptionCurveCfgCtor(ExceptionPRESCfg):
    """Construction exception when making a CurveCfg object or descendant."""
    pass

class ExceptionCurveCfgLISRead(ExceptionCurveCfg):
    """Specialisation of exception for CurveCfgLISRead and its travails."""
    pass

############################################
# Section: Handling LIS codings and colours.
############################################
# TODO: Put this as class attributes/methods in the CurveCfgLISRead class as it is not used elsewhere

#: Deafult light line width in pixels
DEFAULT_LLINE_WIDTH_PX = 0.5
#: Deafult heavy line width in pixels
DEFAULT_HLINE_WIDTH_PX = 1.5

#: Maps LIS CODI mnemonics to a Stroke object:
#: If either value is None an SVG attribute is not needed i.e. default SVG behaviour
LIS_CODI_MAP = {
    # Default
    None        : (Stroke.StrokeBlackSolid._replace(width=DEFAULT_LLINE_WIDTH_PX, coding=None)),
    b'LLIN'     : (Stroke.StrokeBlackSolid._replace(width=DEFAULT_LLINE_WIDTH_PX, coding=None)),
    b'LSPO'     : (Stroke.StrokeBlackSolid._replace(width=DEFAULT_LLINE_WIDTH_PX, coding=(2,2))),
    b'LDAS'     : (Stroke.StrokeBlackSolid._replace(width=DEFAULT_LLINE_WIDTH_PX, coding=(4,4))),
    b'LGAP'     : (Stroke.StrokeBlackSolid._replace(width=DEFAULT_LLINE_WIDTH_PX, coding=(6,2))),
    b'HLIN'     : (Stroke.StrokeBlackSolid._replace(width=DEFAULT_HLINE_WIDTH_PX, coding=None)),
    b'HSPO'     : (Stroke.StrokeBlackSolid._replace(width=DEFAULT_HLINE_WIDTH_PX, coding=(2,2))),
    b'HDAS'     : (Stroke.StrokeBlackSolid._replace(width=DEFAULT_HLINE_WIDTH_PX, coding=(4,4))),
    b'HGAP'     : (Stroke.StrokeBlackSolid._replace(width=DEFAULT_HLINE_WIDTH_PX, coding=(6,2))),
    # Non-LIS codes, these are really just for testing
    # Super-fine line, useful for dipmeter fast channels
    b'SFLN'     : (Stroke.StrokeBlackSolid._replace(width=0.0625, coding=None)),
    # Super-fine dash, useful for dipmeter fast channels
    b'SFDA'     : (Stroke.StrokeBlackSolid._replace(width=0.0625, coding=(4,4))),
}

# Maps LIS COLO mnemonics to CSS/SVG style colour specifications.
# Statistics:
#"(34, b'PRES', b'COLO', b'000 ')": 173,
#"(34, b'PRES', b'COLO', b'002 ')": 3,
#"(34, b'PRES', b'COLO', b'003 ')": 6,
#"(34, b'PRES', b'COLO', b'004 ')": 33,
#"(34, b'PRES', b'COLO', b'014 ')": 6,
#"(34, b'PRES', b'COLO', b'020 ')": 9,
#"(34, b'PRES', b'COLO', b'021 ')": 8,
#"(34, b'PRES', b'COLO', b'030 ')": 34,
#"(34, b'PRES', b'COLO', b'034 ')": 2,
#"(34, b'PRES', b'COLO', b'044 ')": 6,
#"(34, b'PRES', b'COLO', b'104 ')": 3,
#"(34, b'PRES', b'COLO', b'134 ')": 14,
#"(34, b'PRES', b'COLO', b'203 ')": 3,
#"(34, b'PRES', b'COLO', b'221 ')": 3,
#"(34, b'PRES', b'COLO', b'312 ')": 10,
#"(34, b'PRES', b'COLO', b'400 ')": 44,
#"(34, b'PRES', b'COLO', b'404 ')": 6,
#"(34, b'PRES', b'COLO', b'420 ')": 9,
#"(34, b'PRES', b'COLO', b'430 ')": 17,
#"(34, b'PRES', b'COLO', b'AQUA')": 3,
#"(34, b'PRES', b'COLO', b'BLAC')": 1260,
#"(34, b'PRES', b'COLO', b'BLUE')": 8,
#"(34, b'PRES', b'COLO', b'GREE')": 37,
#"(34, b'PRES', b'COLO', b'RED ')": 12}

#: Maps LIS COLO mnemonics to CSS/SVG style colour specifications.
LIS_COLO_MAP = {
    Mnem.Mnem(b'AQUA') : 'aqua',
    Mnem.Mnem(b'BLAC') : 'black',
    Mnem.Mnem(b'BLUE') : 'blue',
    Mnem.Mnem(b'GREE') : 'green',
    Mnem.Mnem(b'RED ') : 'red',
    # Not detected in current LIS test cases but assumed
    Mnem.Mnem(b'YELL') : 'yellow',
    Mnem.Mnem(b'CYAN') : 'cyan',
    Mnem.Mnem(b'MAGE') : 'magenta',
    Mnem.Mnem(b'GREY') : 'grey',
}

def lisColo(theMnem):
    """Returns a SVG colour as a string from a Mnem or None on failure."""
#    print('lisColo({:s}):'.format(theMnem))
    try:
        return LIS_COLO_MAP[theMnem]
    except KeyError:
        pass
    # We map 0-4 to 0-255 for each of the three characters
    # So 000 -> 0,0,0 and 444 -> 255,255,255
    # So values 0,1,2,3,4 become 0.0, 63.75, 127.5, 191.25, 255.0
    rbg = [0, 0, 0]
    for i, aB in enumerate(theMnem):
        if i >= 3:
            break
        # Magic number 48 is ASCII '0'
        v = int(255 * (aB-48) / 4)
        if v >= 0 and v <=255:
            rbg[i] = v
    return 'rgb({:d},{:d},{:d})'.format(rbg[0], rbg[1], rbg[2])

def coloStroke(theSt, theCm):
    """Takes a Stroke object and returns a new stroke object with the colour
    replaced with the Color Mnem looked up, or determined from, the LIS_COLO_MAP."""
    return theSt._replace(colour=lisColo(theCm))

########################################
# End: Handling LIS codings and colours.
########################################

################################################
# Section: Line transforms for linear/log grids.
# Each track/line combination has an instance.
# This allows linear lines to be plotted on log
# tracks.
################################################

#========================
# Section: Curve backups.
#========================
# Backup tuple examples

#: No backup
BACKUP_NONE     = (1, -1)
#: Every backup i.e. 'wrap' Note: Plot.py has a way of limiting ludicrous
#: backup lines to a sensible number; say 8
BACKUP_ALL      = (0, 0)
#: Single backup to left or right
BACKUP_ONCE     = (-1, 1)
#: Two backups to left or right
BACKUP_TWICE    = (-2, 2)
#: Single backup to left only
BACKUP_LEFT     = (0, -1)
#: Single backup to right only
BACKUP_RIGHT    = (1, 0)

#LIS Statistics
#======================== Count of all table entries =======================
#{"(34, b'PRES', b'MODE', b'GRAD')": 245,
# "(34, b'PRES', b'MODE', b'NB  ')": 2329,
# "(34, b'PRES', b'MODE', b'SHIF')": 597,
# "(34, b'PRES', b'MODE', b'SWF ')": 3,
# "(34, b'PRES', b'MODE', b'VDLN')": 3,
# "(34, b'PRES', b'MODE', b'WRAP')": 186,
# "(34, b'PRES', b'MODE', b'X10 ')": 10}
#====================== Count of all table entries END =====================

#: Map of backup mode to internal representation
BACKUP_FROM_MODE_MAP = {
    None    : BACKUP_ALL, # Default
    b'SHIF' : BACKUP_ONCE,
    b'GRAD' : BACKUP_NONE,
    b'NB  ' : BACKUP_NONE,
    b'WRAP' : BACKUP_ALL,
}
#========================
# End: Curve backups.
#========================

#===============================
# Section: Line transformations.
#===============================
class LineTransBase(object):
    """Base class for line generators."""
    def __init__(self, leftP, rightP, leftL, rightL, backup):
        """Ctor with values; leftP, rightP are physical positions as numbers.
        leftL, rightL are logical scales as numbers.
        backup is a pair (left, right).
        Will raise a ExceptionLineTransBase if leftP >= rightP.
        """
        #if isinstance(leftP, numbers.Number):
        #    self._lP = 
        if leftP >= rightP:
            raise ExceptionLineTransBase('Left physical {:s} is >= than right {:s}'.format(str(leftP), str(rightP)))
        self._lP = leftP
        self._rP = rightP
        self._lL = leftL
        self._rL = rightL
        self._bu = backup
    
    @property
    def leftL(self):
        """The left value of the curve scale as a number."""
        return self._lL
    
    @property
    def rightL(self):
        """The right value of the curve scale as a number."""
        return self._rL
    
    def __str__(self):
        return '{:s} lP={:f} rP={:f} lL={:f} rR={:f} backup={:s}'.format(
            repr(self), self._lP, self._rP, self._lL, self._rL, str(self._bu)
        )
    
    def L2P(self, val):
        """Scale a given value to a dimension."""
        raise NotImplementedError()

    def wrapPos(self, val):
        """For a given value returns a pair (wrap, pos).
        wrap is an integer number of times the curve is wrapped.
        pos is a float that is the physical plot position of the value.
        TODO: Benchmark this, it could be slow."""
        raise NotImplementedError()
    
    def offScale(self, w):
        """Returns 0 if wrap integer is on scale depending on the backup setting.
        Returns -1 if off scale low, +1 if off scale high."""
        if w < 0 and self._bu[0] and w < self._bu[0]:
            return -1
        if w > 0 and self._bu[1] and w > self._bu[1]:
            return 1
        return 0

    def isOffScaleLeft(self, w):
        """True is wrap integer is off-scale low according to the backup setting."""
        return self.offScale(w) == -1

    def isOffScaleRight(self, w):
        """True is wrap integer is off-scale high according to the backup setting."""
        return self.offScale(w) == 1

class LineTransLin(LineTransBase):
    """Linear grid."""
    def __init__(self, leftP, rightP, leftL, rightL, backup=BACKUP_ALL):
        """Ctor with values; leftP, rightP are physical positions as numbers.
        leftL, rightL are logical scales as numbers.
        backup is a pair (left, right).
        """
        super().__init__(leftP, rightP, leftL, rightL, backup)
#        print('LineTransLin.__init__():', leftP, rightP, leftL, rightL, backup)
        # Do as much computation here rather than in L2P
        self._den = self._rL - self._lL
        self._pWidth = self._rP - self._lP
        self._scale = self._pWidth / self._den
        self._offset = self._lP - self._scale * self._lL

    def L2P(self, val):
        """Scale a given value to a dimension."""
        return self._offset + self._scale * val

    def wrapPos(self, val):
        """For a given value returns a pair (wrap, pos).
        wrap is an integer number of times the curve is wrapped.
        pos is a float that is the physical plot position of the value.
        TODO: Benchmark this, it could be slow."""
        p = (val - self._lL) / self._den
        w = math.floor(p)
        f = self._lP + (p - w) * self._pWidth
        return w, f

class LineTransLog10(LineTransBase):
    """Logrithmic grid."""
    def __init__(self, leftP, rightP, leftL, rightR, backup=BACKUP_ALL):
        """Ctor with values; leftP, rightP are physical positions as numbers.
        leftL, rightL are logical scales as numbers.
        backup is a pair (left, right).
        """
        super().__init__(leftP, rightP, leftL, rightR, backup)
        self._den = math.log10(self._rL / self._lL)
        self._pWidth = self._rP - self._lP
        self._scale = self._pWidth / self._den
        self._offset = self._lP - self._scale * math.log10(self._lL)
        
    def L2P(self, val):
        """Scale a given value to a dimension."""
        return self._offset + self._scale * math.log10(val)

    def wrapPos(self, val):
        """For a given value returns a pair (wrap, pos).
        wrap is an integer number of times the curve is wrapped.
        pos is a float that is the physical plot position of the value.
        TODO: Benchmark this, it could be slow."""
        if val <= 0.0:
            raise ExceptionLineTransBaseMath('Can not plot -ve or zero value {:f} on a log scale.'.format(val))
#        try:
#            p = math.log10(val / self._lL) / self._den
#        except ValueError:
#            print('Help:', val, self._lL, self._den)
#            raise
        p = math.log10(val / self._lL) / self._den
        w = math.floor(p)
        r = self._lP + (p - w) * self._pWidth
        return w, r
#===============================
# Section: Line transformations.
#===============================
################################################
# End: Line transforms for linear/log grids.
################################################

#: Used to record the physical width data of a track
#: leftP, rightP are Coord.Dim objects.
#: halfTrackStart, halfTracks are integers
TrackWidthData = collections.namedtuple('TrackWidthData', 'leftP rightP halfTrackStart halfTracks')

class CurveCfg(object):
    """Contains the configuration of a single curve."""
    DEFAULT_FILT = 0.5
    def __init__(self):
        """Populate attribute with reasonable default values.
        Second stage is to set:
        self.mnem, self.outp, self.trac, self.dest.
        Optionally other properties as well."""
        # Key mnemonic
        self.mnem = None
        # The output name i.e. the name in the DFSR that provides the values for this curve
        self.outp = None
        # True if can be plotted
        self.stat = True
#        # Trac is a mnem
        self.trac = None
        self.codiStroke = Stroke.StrokeBlackSolid._replace(
                            width=DEFAULT_LLINE_WIDTH_PX
        )
        # Entry in a FILM table e.g. b'1    '
        self.dest = None
        # TODO: Move filter into LineTransBase that can smooth repeated calls
        # to wrapPos()
        self.filt = 0.5
        # Map of track width data keyed to film destination
        # Create a map of {film_id : TrackWidthData, ...}
        self._filmTrackWidthMap = {}
        # Map of track transfer function keyed to film destination:
        # {film_id : LineTransBase, ...}
        # Values are objects derived from LineTransBase
        # This contains the left/right positions, left/right scales, a backup
        # mode and, implicitly, a moderating function
        self._filmTrackFnMap = {}
        
    def longStr(self):
        """Returns a long descriptive string of the internal state."""
        return '\n'.join(
            [
                'CurveCfg: mnem=%s outp=%s, stat=%s, trac==%s, dest=%s' \
                    % (self.mnem, self.outp, str(self.stat), self.trac, self.dest),
                '  Coding: {:s}'.format(self.codiStroke)
            ]
        )
    
    def tracWidthData(self, theFilmID):
        """Returns a TrackWidthData object for the film ID."""
        logging.debug(
            'CurveCfg.tracWidthData({!r:s}): keys: {!r:s}'.format(theFilmID, str(self._filmTrackWidthMap.keys()))
        )
        assert(theFilmID in self._filmTrackWidthMap), \
            'theFilmID "{:s}" not in self._filmTrackWidthMap: {:s}'.format(
                str(theFilmID),
                str(self._filmTrackWidthMap.keys()),
            )
        return self._filmTrackWidthMap[theFilmID]
    
    def tracValueFunction(self, theFilmID):
        """Given a FILM ID (a Mnem() object) this returns a LineTransBase or
        derivation that describes how this curve is plotted on that film.
        In particular the return value will have a function wrapPos() for
        generating track positions from a value."""
        return self._filmTrackFnMap[theFilmID]
    
class CurveCfgLISRead(CurveCfg):
    #: Default backup mode
    DEFAULT_MODE = b'WRAP'
    def __init__(self, theRow, theFILMCfg):
        """Reads a LogiRec.TableRow object from a PRES table and populates a
        CurveCfg. theFILMCfg is expected to be a FILMCfgLISRead object.
        Typical row:
        MNEM  OUTP  STAT  TRAC  CODI  DEST  MODE      FILT          LEDG          REDG
        -----------------------------------------------------------------------------------
        NPHI  NPHI  ALLO  T23   LDAS  1     SHIF      0.500000      0.450000     -0.150000
        May raise an ExceptionCurveCfg or an IndexError.
        TODO: Not raise IndexError but normalise to ExceptionCurveCfg?
        For example have an API missingCols(...) that returns None if all present
        or a tuple of those missing. 
        """
        super().__init__()
        assert(isinstance(theFILMCfg, FILMCfg.FilmCfgLISRead))
#        print('CurveCfgLISRead.__init__() keys for theRow={:s}:'.format(theRow.value), [c.mnem for c in theRow.genCells()])
        self.mnem = Mnem.Mnem(theRow[b'MNEM'].value)
        try:
            self.outp = Mnem.Mnem(theRow[b'OUTP'].value)
        except KeyError:
            # Noticed missing OUTP in 11851.S7, fall back on curve name
            self.outp = self.mnem
            logging.warning(
                'CurveCfgLISRead.__init__(): No OUTP entry for {!r:s}, assuming same name as MNEM.'.format(self.mnem)
            )
        self.stat = theRow[b'STAT'].status
        self.trac = theRow[b'TRAC'].value
        self.dest = Mnem.Mnem(theRow[b'DEST'].value)
        try:
            self.filt = theRow[b'FILT'].value
        except KeyError:
            # Noted in 13408.S2
            self.filt = self.DEFAULT_FILT
            logging.warning(
                'CurveCfgLISRead.__init__(): No FILT entry for {!r:s}, assuming the default: {:f}.'.format(self.mnem,
                                                                                                           self.filt)
            )
        # Interpret track, we need theFILMCfg to help us here
        #print(self.mnem, self.dest)
        # Set self.trac to an object derived from LineTransBase
        try:
            self.mode = theRow[b'MODE'].value
        except KeyError:
            # Noted in 13408.S2
            self.mode = self.DEFAULT_MODE
            logging.warning(
                'CurveCfgLISRead.__init__(): No MODE entry for {!r:s}, assuming the default: {!r:s}.'.format(self.mnem,
                                                                                                             self.mode)
            )
        try:
            myBackup = BACKUP_FROM_MODE_MAP[self.mode]
        except KeyError:
            logging.warning(
                'CurveCfgLISRead.__init__(): No BACKUP_FROM_MODE_MAP entry for {!r:s}, assuming the default.'.format(self.mode)
            )
            # Use default
            myBackup = BACKUP_FROM_MODE_MAP[None]
        myCodi = theRow[b'CODI'].value
        try:
            self.codiStroke = LIS_CODI_MAP[myCodi]
        except KeyError:
            logging.warning(
                'CurveCfgLISRead.__init__(): No LIS_CODI_MAP entry for {!r:s}, assuming the default.'.format(str(myCodi))
            )
            # Use default
            self.codiStroke = LIS_CODI_MAP[None]
        # Apply colour to stroke if COLO attribute is present
        if b'COLO' in theRow:
            self.codiStroke = coloStroke(self.codiStroke, Mnem.Mnem(theRow[b'COLO'].value))
        # TODO: leftP, rightP are Coord.Dim() objects, we ought to align the units that they use
        # Need: leftP, rightP, leftL, rightR, backup
        # Initialise a map of {film_id : TrackWidthData, ...}
        self._filmTrackWidthMap.clear()
        # Map of track transfer function keyed to film destination:
        # {film_id : LineTransBase, ...}
        self._filmTrackFnMap.clear()
        for aFilmId in theFILMCfg.keys():
            # This may raise a ExceptionPhysFilmCfg
            try:
                myIntTrac = theFILMCfg.interpretTrac(aFilmId, self.dest, self.trac)
            except ExceptionTotalDepthLIS as err:
                logging.error('CurveCfgLISRead.__init__(): can not get trac: {:s}'.format(str(err)))
            else:
                # myIntTrac can be None if the destination is NEIT for example
                if myIntTrac is None: 
                    logging.warning('Get None from theFILMCfg.interpretTrac(FILM ID={!r:s},'
                        ' PRES DEST={!r:s}, PRES TRAC={!r:s})'.format(
                            aFilmId, self.dest, self.trac
                        )
                    )
                else:
                    # Make a new instance of TrackWidthData from the four part iterable
                    myTw = TrackWidthData._make(myIntTrac)
                    #print('myTw', myTw)
                    self._filmTrackWidthMap[aFilmId] = myTw
                    # Raise if the LEDG and the REDG make no sense
                    # Example: 200099.S06
                    if theRow[b'LEDG'].value == theRow[b'REDG'].value:
                        raise ExceptionCurveCfgCtor(
                            'CurveCfgLISRead.__init__(): Curve {!r:s} has no'
                            ' logical span {:s}->{:s}'.format(self.mnem,
                                                              str(theRow[b'LEDG'].value),
                                                              str(theRow[b'REDG'].value))
                        )
                    # Otherwise proceed...
                    if self.mode == b'GRAD':
                        self._filmTrackFnMap[aFilmId] = LineTransLog10(
                            myTw.leftP.value,
                            myTw.rightP.value,
                            theRow[b'LEDG'].value,
                            theRow[b'REDG'].value,
                            myBackup)
                    else:
                        self._filmTrackFnMap[aFilmId] = LineTransLin(
                            myTw.leftP.value,
                            myTw.rightP.value,
                            theRow[b'LEDG'].value,
                            theRow[b'REDG'].value,
                            myBackup)
        
class PresCfg(object):
    """Contains the configuration equivalent to a complete PRES table."""
    def __init__(self):
        # Map of {Mnem.Mnem(curve_id) : CurveCfg, ...}
        self._curveCfgMap = {}
        # Map of (Mnem.Mnem(dest) : {Mnem.Mnem(output_channel_id) : [curve_id, ...], ...}, ...}
        self._destOutpToCurveIdMap = {} 
        
    def add(self, theCurveCfg, theFilmDestS):
        """Adds to the IR. theCurveCfg is a CurvCfg object, theFilmDestS is a
        list of film destinations expanded from the FILM table e.g. if the
        destination is b'ALL' then all FILM destination mnemonics should be in
        the list."""
        m = theCurveCfg.mnem
        #print('add()', m, theFilmDestS)
        if m in self._curveCfgMap:
            # NOTE: This is not likely to happen as the Logical Table will discard duplicates
            logging.warning('PresCfg.add(): Ignoring duplicate curve MNEM="{:s}'.format(m))
        else:
            self._curveCfgMap[m] = theCurveCfg
            for aDest in theFilmDestS:
                # Load map of maps
                try:
                    self._destOutpToCurveIdMap[aDest][theCurveCfg.outp].append(m)
                except KeyError:
                    try:
                        self._destOutpToCurveIdMap[aDest][theCurveCfg.outp] = [m,]
                    except KeyError:
                        self._destOutpToCurveIdMap[aDest] = {}
                        self._destOutpToCurveIdMap[aDest][theCurveCfg.outp] = [m,]
    
    def keys(self):
        """Returns the curve mnemonics."""
        return self._curveCfgMap.keys()
    
    def __len__(self):
        """Number of curves in this table."""
        return len(self._curveCfgMap)
    
    def __getitem__(self, theCurvID):
        """Returns the CurveCfg object corresponding to curve ID, a Mnem.Mnem object."""
        return self._curveCfgMap[theCurvID]
    
    def __contains__(self, theCurvID):
        """Returns True if I have an entry for the curve ID, a Mnem.Mnem object."""
        return theCurvID in self._curveCfgMap
    
    def hasCurvesForDest(self, theDest):
        """Returns True if there are curves that go to theDest i.e. FILM ID."""
        return theDest in self._destOutpToCurveIdMap

    def outpChIDs(self, theDest):
        """Returns a list of output channel IDs for a given film destination, a Mnem.Mnem object."""
        return self._destOutpToCurveIdMap[theDest].keys()

    def outpCurveIDs(self, theDest, theOutp):
        """Returns a list of channel IDs for a given film destination and output
        that feeds those curves. The curve data is accessible by __getitem__().
        Arguments should be Mnem.Mnem objects"""
        return self._destOutpToCurveIdMap[theDest][theOutp][:]
    
    def usesOutpChannel(self, theDest, theOutp):
        """Returns True if this PRES table + FILM  destination uses theOutp ID.
        Arguments should be , a Mnem.Mnem objects."""
        return theOutp in self._destOutpToCurveIdMap[theDest] 

class PresCfgLISRead(PresCfg):
    """Information from a complete LIS PRES table."""
    def __init__(self, theLr, theFILMCfg):
        """Reads a LogiRec.Table object of type PRES and creates a
        CurveCfgLISRead for each row. theFILMCfg is expected to be a
        FILMCfgLISRead object.
        
        Typical PRES table::
        
            MNEM  OUTP  STAT  TRAC  CODI  DEST  MODE      FILT          LEDG          REDG
            -----------------------------------------------------------------------------------
            NPHI  NPHI  ALLO  T23   LDAS  1     SHIF      0.500000      0.450000     -0.150000
            DRHO  DRHO  ALLO  T3    LSPO  1     NB        0.500000     -0.250000      0.250000
            PEF   PEF   ALLO  T23   LGAP  1     SHIF      0.500000       0.00000       10.0000
        """
        super().__init__()
        if theLr.type != LogiRec.LR_TYPE_WELL_DATA:
            raise ExceptionPRESCfgLISRead('FilmCfgLISRead.__init__(): LR type={:d}, expected {:d}'.format(theLr.type, LogiRec.LR_TYPE_WELL_DATA))
        if theLr.value != b'PRES':
            raise ExceptionPRESCfgLISRead('FilmCfgLISRead.__init__(): LR Table not a CONS table type "PRES".')
        for aRow in theLr.genRows():
            #print('aRow.value', aRow.value, theFILMCfg.retAllFILMDestS(aRow.value))
            # Special case; we only process destinations that are not b'NEIT'
            if aRow[b'DEST'].value != b'NEIT':
                try:
                    self.add(CurveCfgLISRead(aRow, theFILMCfg), theFILMCfg.retAllFILMDestS(aRow[b'DEST'].value))
                except ExceptionCurveCfgCtor as err:
                    logging.error('PresCfgLISRead.__init__(): Can not add curve {:s}, error is: {:s}'.format(aRow[b'MNEM'], err))
