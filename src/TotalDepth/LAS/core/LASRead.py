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
"""Reads LAS files.

Created on Jan 11, 2012

"""

__author__  = 'Paul Ross'
__date__    = '2012-01-11'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2012 Paul Ross.'

import logging
import os
import re
import collections
from TotalDepth.LIS.core import EngVal

from TotalDepth.LAS import ExceptionTotalDepthLAS
from TotalDepth.LAS.core import LASConstants

class ExceptionLASRead(ExceptionTotalDepthLAS):
    """Specialisation of exception for LASRead."""
    pass

class ExceptionLASReadSection(ExceptionLASRead):
    """Specialisation of exception for LASRead when handling sections."""
    pass

class ExceptionLASReadSectionArray(ExceptionLASReadSection):
    """Specialisation of exception for LASRead when handling array section."""
    pass

class ExceptionLASReadData(ExceptionLASRead):
    """Specialisation of exception for LASRead when reading data."""
    pass

class ExceptionLASKeyError(ExceptionLASRead):
    """Equivalent to KeyError when looking stuff up."""
    pass

#: LAS file extension
LAS_FILE_EXT = '.las'
#: LAS lower case file extension
LAS_FILE_EXT_LOWER = LAS_FILE_EXT.lower()

def hasLASExtension(fp):
    """Returns True if the file extansion is a LAS one."""
    return os.path.splitext(os.path.normcase(fp))[1] == LAS_FILE_EXT

#: Regex to match a comment
RE_COMMENT = re.compile(r'^\s*#(.*)$')

#: logging.debug call here can add about 50% of the processing time
DEBUG_LINE_BY_LINE = False

def genLines(f):
    """Given an file-like object this generates non-blank, non-comment lines.
    It's a co-routine so can accept a line to put back.
    """
    n = 0
    while 1:
        l = f.readline()
        n += 1
        # logging.debug call here can add about 50% of the processing time
        if DEBUG_LINE_BY_LINE: logging.debug('[{:08d}]: {:s}'.format(n, l.replace('\n', '\\n')))
        if len(l) == 0:
            break
        if l != '\n' and not RE_COMMENT.match(l):
            l = yield n, l
            if l is not None:
                # Recycle it
                yield None
                yield n, l

#: All section identifiers
SECT_TYPES                  = 'VWCPOA'
#: Section with data lines
SECT_TYPES_WITH_DATA_LINES  = 'VWCP'
#: Section with index value in column 0
SECT_TYPES_WITH_INDEX       = 'VWCPA'

#: Regex to match a section heasd
RE_SECT_HEAD = re.compile(r'^~([{:s}])(.+)*$'.format(SECT_TYPES))

#: Map of section identifiers to description
SECT_DESCRIPTION_MAP = {
    'V' : "Version Information Section",
    'W' : "Well Information Section",
    'C' : "Curve Information Section",
    'P' : "Parameter Information Section",
    'O' : "Other Information Section",
    'A' : "ASCII Log Data",
}

#: The 'MENM' field, no spaces, dots or colons.
#: ONE group
RE_LINE_FIELD_0 = re.compile(r'^\s*([^ .:]+)\s*$')

#: The data field which is the middle of the line between the first '.' and last ':'
#: This is composed of optional units and value.
#: Units must follow the dot immediately and contain no colons or spaces
#: Note: Group 2 may have leading and trailing spaces
#: TWO groups 
RE_LINE_FIELD_1 = re.compile(r'^([^ :]+)*(.+)*$')
#: Data field 2 is after the last ':'
#: THREE groups
RE_LINE_FIELD_2 = re.compile(r"""
    ^          # Start of line
    ([^{|]+)*  # Description, anything but '{' or '|', needs strip()
    ({.+?})*   # Optional format {...}
    \s*        # Optional space
    [|]*       # Optional '|'
    (.+)*      # Optional reference, needs strip()
    $""", re.VERBOSE)

#: Captures the 6 fields: mnem unit valu desc format assoc
SectLine = collections.namedtuple('SectLine', 'mnem unit valu desc format assoc')

class LASSection():
    """Contains data on a section."""
    RULES_MAP = {
        'V' : [
               ('VERS', (1.2, 2.0)),
               ('WRAP', (True, False)),
            ],
    }
    def __init__(self, sectType):
        assert(sectType in SECT_TYPES)
        self.type = sectType
        # One entry per line
        self._members = []
        # {MNEM : ordinal, ...} for those sections that have it
        # Populated by finalise()
        self._indexMap = {}
        
    def __str__(self):
        return 'LASSection: "{:s}" with {:d} lines'.format(self.type, len(self._members))
    
    def __len__(self):
        """Number of members."""
        return len(self._members)
    
    def __contains__(self, theMnem):
        """Membership test."""
        return theMnem in self._indexMap
    
    def addMemberLine(self, i, l):
        """Given a line this decomposes it to its _members. i is the position
        of the line l in the file."""
        if self.type in SECT_TYPES_WITH_DATA_LINES:
            # A hybrid approach where we split the line then apply individual regex's
            dIdx = l.find('.')
            cIdx = l.rfind(':')
            if dIdx != -1 and cIdx != -1:
                m0 = RE_LINE_FIELD_0.match(l[:dIdx])
                m1 = RE_LINE_FIELD_1.match(l[dIdx + 1:cIdx])
                m2 = RE_LINE_FIELD_2.match(l[cIdx + 1:])
                if m0 is None or m1 is None or m2 is None:
                    # Use !s prefix as any of m0, m1, m2 can be None.
                    raise ExceptionLASReadSection(
                        'Can not decompose line [{:d}]: "{:s}" with results: '
                        '{!s:s}, {!s:s}, {!s:s}'.format(
                            i, l.replace('\n', '\\n'), m0, m1, m2
                        )
                    )
                else:
                    self._members.append(
                        SectLine(
                            *[self._val(g) for g in (m0.groups() + m1.groups() + m2.groups())]
                        )
                    )
        else:
            self._members.append(l.strip())
    
    def _val(self, v):
        """Convert a value to an integer, float, bool or string. If a string it is stripped."""
        if v is not None:
            try:
                return int(v)
            except ValueError:
                pass
            try:
                return float(v)
            except ValueError:
                pass
            if isinstance(v, str):
                v = v.strip()
                if v in ("YES", "yes", "Yes"):
                    return True
                elif v in ("NO", "no", "No"):
                    return False
                return v
        # Returns None
        
    def _createIndex(self):
        """Creates an index of {key : ordinal, ...}.
        key is the first object in each member. This will be a MNEM for most
        sections but a depth as a float for an array section."""
        self._indexMap = {}
        if self.type in SECT_TYPES_WITH_INDEX:
            for m, memb in enumerate(self._members):
                # Note we use memb[0] so this works for SectLine and lists
                k = memb[0]
                if k in self._indexMap:
                    logging.warning('Ignoring duplicate menmonic "{:s}", was {:s} dupe is {:s}'.format(
                        str(k),
                        str(self._members[self._indexMap[k]]),
                        str(memb),
                        )
                    )
                else:
                    self._indexMap[k] = m
#        print(self._indexMap)
        
    def finalise(self):
        """Finalisation of section, this updates the internal representation."""
        self._createIndex()
        if self.type == 'V':
            myR = self.RULES_MAP[self.type]
            if len(self._members) != len(myR):
#                raise ExceptionLASReadSection('Section "{:s}" must have {:d} entries not {:d}.'.format(self.type, len(myR), len(self)))
                logging.warning('Section "{:s}" must have {:d} entries not {:d}.'.format(self.type, len(myR), len(self)))
            for i, (m, rng) in enumerate(myR):
                if i >= len(self._members):
                    # This will be reported as a length miss-match above
                    break
                if self._members[i].mnem != m:
                    raise ExceptionLASReadSection('Section "{:s}" must have entry[{:d}]: "{:s}".'.format(self.type, i, m))
                if self._members[i].valu not in rng:
                    raise ExceptionLASReadSection(
                        'Section "{:s}" must have value for "{:s}" converted to {:s} from "{:s}".'.format(
                            self.type,
                            m,
                            str(rng),
                            str(self._members[i].valu),
                        )
                    )
        # TODO: Essential MNEM in other sections
        # TODO: 'W' section: Check consistency of STRT/STOP/STEP and their units
    
    def __getitem__(self, key):
        """Returns an entry, key can be int or str."""
        if isinstance(key, int):
            return self._members[key]
        if isinstance(key, str):
            return self._members[self._indexMap[key]]
        raise TypeError('{:s} object is not subscriptable with {:s}'.format(type(self), type(key)))
        
    def mnemS(self):
        """Returns an list of mnemonics."""
        return [m.mnem for m in self._members]

    def unitS(self):
        """Returns an list of mnemonic units."""
        return [m.unit for m in self._members]
    
    def keys(self):
        """Returns the keys in the internal map."""
        return self._indexMap.keys()
    
    def find(self, m):
        """Returns the member ordinal for mnemonic m or -1 if not found.
        This can be used for finding the array column for a particular curve."""
        try:
            return self._indexMap[m]
        except KeyError:
            pass
        return -1

class LASSectionArray(LASSection):
    """Contains data on an array section."""
    def __init__(self, sectType, wrap, curvSect, null=-999.25):
        assert(sectType == 'A')
        self._wrap = wrap
        # Accumulation of array values when un-wrapping
        self._unwrapBuf = []
        self._mnemUnitS = list(zip(curvSect.mnemS(), curvSect.unitS()))
#        # Removed as we now support wrap when there is a single channel
#        if self._wrap and len(self._mnemUnitS) <= 2:
#            raise ExceptionLASReadSectionArray('Wrapped array section with a single curve makes no sense')
        super().__init__(sectType)
        self._null = null

    def _addBuf(self, lineNum):
        """Adds the temporary buffer to the array. This is associated with the given line number."""
        if len(self._unwrapBuf) > 0:
            if len(self._unwrapBuf) != len(self._mnemUnitS):
                raise ExceptionLASReadSectionArray(
                    'Line [{:d}] buffer length miss-match, frame length {:d} which should be length {:d}'.format(
                        lineNum,
                        len(self._unwrapBuf),
                        len(self._mnemUnitS),
                    )
                )
            self._members.append(self._unwrapBuf)
            self._unwrapBuf = []

    def addMemberLine(self, i, l):
        """Process a line in an array section."""
        # Convert to float inserting null where that can not be done
        valS = []
        for v in l.strip().split():
            try:
                valS.append(float(v))
            except ValueError:
                logging.warning('LASSectionArray.addMemberLine(): line [{:d}], can not convert "{:s}" to float.'.format(i, v))
                valS.append(self._null)
        # Add it to the members
        if len(valS) > 0:
            if not self._wrap:
                self._members.append(valS)
            else:
                self._addMemberWithWrapMode(i, l, valS)
                
    def _addMemberWithWrapMode(self, i, l, valS):
        """Addes a line in wrap mode."""
        assert(self._wrap)
        if len(self._unwrapBuf) == 0:
            # Add the index, raise if there is more than one item on the line
            # We add to the buffer until the length matches the len(self._mnemUnitS)
            if len(valS) == 1:
                self._unwrapBuf.append(valS[0])
            else:
                raise ExceptionLASReadSectionArray(
                    'Line [{:d}] More than one [{:d}] index values, line is: {:s}'.format(
                        i, len(valS), l.replace('\n', '\\n'),
                ))
        else:
            # Add to buffer
            self._unwrapBuf.extend(valS)
            # Is buffer complete or has overflowed?
            if len(self._unwrapBuf) == len(self._mnemUnitS):
                self._addBuf(i)
            elif len(self._unwrapBuf) > len(self._mnemUnitS):
                raise ExceptionLASReadSectionArray(
                    'Line [{:d}] array overflow; frame length {:d} which should be length {:d}'.format(
                        i, len(self._unwrapBuf), len(self._mnemUnitS),
                ))
                
    def finalise(self):
        """Finalisation.
        TODO: Make a numpy array and get rid of the members. Need to overload __getitem__."""
        self._addBuf(-1)
        self._createIndex()
    
    def frameSize(self):
        """Returns the number of data points in a frame."""
        return len(self._mnemUnitS)
    
class LASBase(object):
    """Base class for LAS reading and writing. This provides common functionality to child classes."""
    #: Mapping of commonly seen LAS units to proper LIS units
    #: Both key and value must be strings
    UNITS_LAS_TO_LIS = {
        # Noticed on depth indices
        'F'             : 'FEET',
        'mts'           : 'M   ',
#        # Curves
#        'INCHES'        : 'IN  ',
#        'API'           : 'GAPI',
#        'OHM-M'         : 'OHMM',
    }
    # Hack to expand units to 4 chars so 'FT' becomes 'FT  '
    UNITS_MNEM_LEN = 4
    def __init__(self, id):
        self.id = id
        self._sects = []
        # {sect_type : ordinal, ...}
        # Populated by _finalise()
        self._sectMap = {}
        self._wrap = None
        
    def __len__(self):
        """Number of sections."""
        return len(self._sects)
    
    def __getitem__(self, key):
        """Returns a section, key can be int or str."""
        if isinstance(key, int):
            return self._sects[key]
        if isinstance(key, str):
            return self._sects[self._sectMap[key]]
        raise TypeError('{:s} object is not subscriptable with {:s}'.format(type(self), type(key)))

    def _finaliseSectAndAdd(self, theSect):
        theSect.finalise()
        if theSect.type in self._sectMap:
            raise ExceptionLASRead('Duplicate section {:s}'.format(theSect.type))
        self._sectMap[theSect.type] = len(self._sects)
        self._sects.append(theSect)
    
    def _finalise(self):
        pass
    
    def numFrames(self):
        """Returns the number of frames of data in an 'A' record if I have one."""
        try:
            return len(self._sects[self._sectMap['A']])
        except KeyError:
            pass
        return 0

    def numDataPoints(self):
        """Returns the number of frame data points in an 'A' record if I have one."""
        try:
            myA = self['A']
            return len(myA) * myA.frameSize()
        except KeyError:
            pass
        return 0
    
    def genSects(self):
        """Yields up each section."""
        for s in self._sects:
            yield s
            
    @property
    def nullValue(self):
        """The NULL value, defaults to -999.25."""
        try:
            return self['W']['NULL'].valu
        except KeyError:
            pass
        # Bit contentious this as LAS does not specify default value for this
        return -999.25
        
    @property
    def xAxisUnits(self):
        """The X axis units."""
        try:
            return self._units(self['W']['STRT'].unit)
        except KeyError:
            raise ExceptionLASReadData('LASBase.logDown(): No "W" section or no "STRT" value.')

    def _units(self, u):
        """Given a string of units return it as LIS like units in bytes."""
        if u is None:
            u = '    '
        try:
            u = self.UNITS_LAS_TO_LIS[u]
        except KeyError:
            pass
        # Expand units to 4 chars if necessary
        if len(u) < self.UNITS_MNEM_LEN:
            u = u + ' ' * (self.UNITS_MNEM_LEN - len(u))
        return bytes(u, 'ascii')

    def _wsdEngVal(self, m):
        v, u = self.getWsdMnem(m)
        if v is not None:
            return EngVal.EngVal(v, self._units(u))
            
    @property
    def xAxisStart(self):
        """The Xaxis start value as an EngVal."""
        return self._wsdEngVal('STRT')

    @property
    def xAxisStop(self):
        """The Xaxis end value as an EngVal."""
        return self._wsdEngVal('STOP')

    @property
    def xAxisStep(self):
        """The Xaxis step value as an EngVal."""
        return self._wsdEngVal('STEP')

    def logDown(self):
        """Returns True if X axis is increasing i.e. for time or down log."""
        try:
            return self['W']['STEP'].valu > 0
        except KeyError:
            raise ExceptionLASReadData('LASBase.logDown(): No "W" section or no "STEP" value.')
    
    def getWsdMnem(self, m):
        """Returns a tuple of (value, units) for a Mnemonic that may appear in either a
        Well section or a Parameter section. Units may be None if empty.
        Returns (None, None) if nothing found."""
        for s in 'WP':
            try:
                sect = self[s]
            except KeyError:
                pass
            else:
                try:
                    member = sect[m]
                except KeyError:
                    pass
                else:
                    return member.valu, member.unit
        return (None, None)
    
    def getAllWsdMnemonics(self):
        """Returns a set of mnemonics from the Well section and the Parameter section."""
        r = set()
        for s in 'WP':
            try:
                r |= set(self[s].keys())
            except KeyError:
                pass
        return r
    
        #------------------------------
        # Section: Channel data access.
        #------------------------------
    def _curveOrAltCurve(self, theMnem):
        """Returns the entry in the Curve table corresponding to theMnem.
        The list of alternate names table LGFORMAT_LAS from LASConstants to interpret 
        curves that are not exact matches.
        Will raise KeyError if no Curve section or no matching curve."""
        i = self._findCurveOrAltCurve(theMnem)
        if i != -1:
            return self['C'][i]
        raise KeyError
        
    def _findCurveOrAltCurve(self, theMnem):
        """Returns the index if entry in the Curve table corresponding to theMnem.
        The list of alternate names table LGFORMAT_LAS from LASConstants to interpret 
        curves that are not exact matches.
        Returns -1 if not found. Will raise KeyError if no Curve section."""
        m = theMnem.pStr(strip=True)
        idx = self['C'].find(m)
        if idx != -1:
            return idx
        if m in LASConstants.LGFORMAT_LAS:
            for alt in LASConstants.LGFORMAT_LAS[m]:
                idx = self['C'].find(alt)
                if idx != -1:
                    return idx
        return -1
        
    def hasOutpMnem(self, theMnem):
        """Returns True if theMnem, a Mnem.Mnem() object is an output in the Curve section.
        It will use the alternate names table LGFORMAT_LAS from LASConstants to interpret 
        curves that are not exact matches."""
        try:
            return self._findCurveOrAltCurve(theMnem) != -1
        except KeyError:
            # No curve section
            pass
        return False
    
    def curveMnems(self, ordered=False):
        """Returns list of curve names actually declared in the Curve section.
        List will be unordered if ordered is False."""
        r = []
        try:
            if ordered:
                for i in range(len(self['C'])):
                    r.append(self['C'][i].mnem)
            else:
                r = self['C'].keys()
        except KeyError:
            # No curve section
            pass
        return r
    
    def curveUnitsAsStr(self, m):
        """Given a curve as a Mnem.Mnem() this returns the units as a string.
        May raise KeyError."""
        return self._units(self._curveOrAltCurve(m).unit)
    
    def genOutpPoints(self, theMnem):
        """Generates curve values for theMnem, a Mnem.Mnem() object."""
        assert(self.hasOutpMnem(theMnem))
        arrayIndex = self._findCurveOrAltCurve(theMnem)
        assert(arrayIndex != -1)
        sectArray = self['A']
        numFrames = len(sectArray)
        for f in range(numFrames):
            yield sectArray[f][0], sectArray[f][arrayIndex]
        #--------------------------
        # End: Channel data access.
        #--------------------------

class LASRead(LASBase):
    """Reads a LAS file."""
    def __init__(self, theFp, theFileID=None):
        """Reads a LAS file from theFp that is either a string (file path) or a file like object."""
        self._sectDespatchMap = {
            'V' : self._procSectV,
            'W' : self._procSect,
            'C' : self._procSect,
            'P' : self._procSect,
            'O' : self._procSect,
            'A' : self._procSectA,
        }
        if isinstance(theFp, str):
            theFp = open(theFp)
        myFileID = theFileID
        try:
            myFileID = theFp.name
        except AttributeError:
            pass
        super().__init__(myFileID)
        self._procFile(genLines(theFp))
        self._finalise()
        
    def _procFile(self, gen):
        for i, l in gen:
            m = RE_SECT_HEAD.match(l)
            if m is not None:
                self._sectDespatchMap[m.group(1)](m, gen)
            else:
#                raise ExceptionLASRead('LASRead._procFile(): Line: {:d} Unknown line: "{:s}"'.format(i, l))
                logging.warning('LASRead._procFile(): Line: {:d} Unknown line: "{:s}"'.format(i, l.replace('\n', '\\n')))
                # Consume following non-section lines
                numLines = 0
                for i, l in gen:
                    m = RE_SECT_HEAD.match(l)
                    if m is not None:
                        gen.send(l)
                        break
                    numLines += 1
                logging.warning('LASRead._procFile(): Consumed {:d} succeeding lines.'.format(numLines))

    def _procSectGeneric(self, mtch, gen):
        mySect = LASSection(mtch.group(1))
        for i, l in gen:
            # Bail out if start of new section
            if l.startswith('~'):#RE_SECT_HEAD.match(l) is not None:
                gen.send(l)
                break
            mySect.addMemberLine(i, l)
        return mySect
    
    def _procSectV(self, mtch, gen):
        logging.debug('_procSectV(): Start')
        assert(mtch is not None)
        if len(self._sects) != 0:
            raise ExceptionLASRead('Version section must be first one.')
        mySect = self._procSectGeneric(mtch, gen)
        self._finaliseSectAndAdd(mySect)
        self._wrap = mySect['WRAP'].valu
        logging.debug('_procSectV(): End')

    def _procSect(self, mtch, gen):
        logging.debug('_procSect(): Start: {:s}'.format(mtch.group(1)))
        assert(mtch is not None)
        if len(self._sects) == 0:
            raise ExceptionLASRead('Non-version section can not be the first one.')
        self._finaliseSectAndAdd(self._procSectGeneric(mtch, gen))
        logging.debug('_procSect(): End: {:s}'.format(mtch.group(1)))

    def _procSectA(self, mtch, gen):
        logging.debug('_procSectA(): Start')
        assert(mtch is not None)
        if len(self._sects) == 0:
            raise ExceptionLASRead('Non-version section can not be the first one.')
        assert(self._wrap is not None)
        curvIdx = 0
        for s in self._sects:
            if s.type == 'C':
                break
            curvIdx += 1
        if curvIdx > len(self._sects)-1:
            raise ExceptionLASRead('No curve section to describe array section.')
        mySect = LASSectionArray(mtch.group(1), self._wrap, self._sects[curvIdx])
        for i, l in gen:
            # Bail out if start of new section
            if l.startswith('~'):#RE_SECT_HEAD.match(l) is not None:
                gen.send(l)
                raise ExceptionLASRead('Line: {:d}. Found section header line "{:s}" after array section'.format(i, l))
                #break
            mySect.addMemberLine(i, l)
        self._finaliseSectAndAdd(mySect)
        logging.debug('_procSectA(): End')
