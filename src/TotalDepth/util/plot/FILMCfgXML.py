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
"""Creates FILM configurations from LgFormat XML files.

Created on Dec 14, 2011

"""

__author__  = 'Paul Ross'
__date__    = '2011-12-14'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

import functools
import logging
import os

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

from TotalDepth.util.plot import Coord
from TotalDepth.util.plot import FILMCfg
from TotalDepth.util.plot import XMLCfg
from TotalDepth.util.plot import Track

class ExceptionFILMCfgXML(FILMCfg.ExceptionFILMCfg):
    """Specialisation of exception for FILMCfgXML module."""
    pass

class ExceptionFILMCfgXMLRead(ExceptionFILMCfgXML):
    """Specialisation of exception for FILMCfgXMLRead module."""
    pass

class ExceptionFILMCfgXMLReadLookUp(ExceptionFILMCfgXMLRead):
    """Specialisation of exception for FILMCfgXMLRead module when a lookup
    fails that would normally raise a KeyError."""
    pass

#Paul-Rosss-MacBook-Pro:plot paulross$ grep -hr "<LgTrack " formats | tr -d " \t" | sort | uniq
#<LgTrackUniqueId="DepthTrack">
#<LgTrackUniqueId="Track2">
#<LgTrackUniqueId="Track3">
#<LgTrackUniqueId="TrackFC1">
#<LgTrackUniqueId="TrackFC2">
#<LgTrackUniqueId="TrackFC3">
#<LgTrackUniqueId="TrackFC4">
#<LgTrackUniqueId="depthTrack">
#<LgTrackUniqueId="timeTrack">
#<LgTrackUniqueId="track1">
#<LgTrackUniqueId="track12">
#<LgTrackUniqueId="track2">
#<LgTrackUniqueId="track23">
#<LgTrackUniqueId="track3">
#<LgTrackUniqueId="track4">
#<LgTrackUniqueId="track5">
#<LgTrackUniqueId="track6">
#<LgTrackUniqueId="trackLHT1">
#<LgTrackUniqueId="trackRHT1">

class PhysFilmCfgXMLRead(FILMCfg.PhysFilmCfg, XMLCfg.LgXMLBase):
    """Extracts FILM information from a single XML file root element."""
    #: Default number of half-tracks to span
    TRAC_STANDARD_SPAN = 2
    #: Map of track IDs to start track location in half-tracks
    TRAC_UNIQUEID_TO_NON_STANDARD_SPAN = {
        'track12'               : 4,
        'track23'               : 4,
        'TrackFC1'              : 1,
        'TrackFC2'              : 1,
        'TrackFC3'              : 1,
        'TrackFC4'              : 1,
        'trackLHT1'             : 1,
        'trackRHT1'             : 1,
    }
    #: Number of half-tracks of the start of the track, this is a fudge around
    #: deciding this from the order of the LgTrack elements
    TRAC_UNIQUEID_TO_NON_STANDARD_START = {
        'track12'               : 2,
        'track23'               : 4,
        'TrackFC1'              : 4,
        'TrackFC2'              : 5,
        'TrackFC3'              : 6,
        'TrackFC4'              : 7,
        'trackLHT1'             : 0,
        'trackRHT1'             : 1,
    }    
    def __init__(self, root):
        assert(root.tag == self.tagInNs('LgFormat')), 'Wrong root element {:s}'.format(root.tag)
        myName = self.elemID(root)
        # Tracks, create a list of Track.Track objects
        # NOTE: This is not quite like the LIS track buildup where the tracks are single
        # and in order so when we encounter T23 we span tracks T2 and T3 (by ordinal).
        # Here we get a separate track description 'track23' which has the width and grid
        # generator, 'track2' and 'track3' may be blank.
        # I suppose also that the order of tracks in the XML file is not significant but
        # we treat is so here.
        myTrackS = []
        # Make an additional data structure that maps the track name to ordinal
        self._trackNameOrdinalMap = {}
        for t, aT in enumerate(root.findall(self.tagInNs('LgTrack'))):
            l = Coord.Dim(self.float(aT, self.tagInNs('LeftPosition'), 0.0), 'in')
            r = Coord.Dim(self.float(aT, self.tagInNs('RightPosition'), 0.0), 'in')
            myTrackS.append(
                Track.Track(
                    leftPos=l,
                    rightPos=r,
                    # Figure out track grid function
                    gridGn=self._retGridGen(aT),
                    plotXLines=self.bool(aT, self.tagInNs('IndexLinesVisible'), True),
                    plotXAlpha=self.bool(aT, self.tagInNs('IndexNumbersVisible'), False),
                )
            )
            trackID = self.elemID(aT)
            if trackID is None:
                raise ExceptionFILMCfgXMLRead('PhysFilmCfgXMLRead.__init__(): Missing track UniqueId'.format(trackID))
            if trackID in self._trackNameOrdinalMap:
                raise ExceptionFILMCfgXMLRead('PhysFilmCfgXMLRead.__init__(): Duplicate track UniqueId="{:s}"'.format(trackID))
            # Add the track ordinal
            self._trackNameOrdinalMap[trackID] = t
#        myXPath = self.tagsInNs('LgFormat', 'LgVerticalScale', 'IndexScaler')
#        myElem = root.find(myXPath)
#        myX = self.int(root, self.tagsInNs('LgVerticalScale', 'IndexScaler'))
#        print()
#        print('TRACE:', myXPath, myElem, myX)
        myXScale = self.int(root, self.tagsInNs('LgVerticalScale', 'IndexScaler'), None)
        assert(myXScale is not None)
        super().__init__(
            theName=myName,
            theTracks=myTrackS,
            # This does not seem to be used by the parent class
            theDest=None,
            theX=myXScale,
        )
    
    def _retGridGen(self, e):
        """Returns a partial grid generator from the Track.py module or None."""
        assert(e.tag == self.tagInNs('LgTrack')), 'Wrong element {:s}'.format(e.tag)
        # Try logarithmic first as, if it is a log track it will have both linear
        # and log specifications, the linear one being merely the track edges
        if len(e.findall(self.tagInNs('LgLogarithmicGrid'))) > 0:
            elemLg = e.find(self.tagInNs('LgLogarithmicGrid'))
            # Log scale, we now have to choose number of decades
            cycles = self.int(elemLg, self.tagInNs('Decade'), 1)
            start = 1
            # And now whether to start at 1 or 2
            lgLog = elemLg.find(self.tagInNs('LogScale'))
            if lgLog is not None:
                if lgLog.text == 'LG_LOG_2':
                    start = 2
                else:
                    raise ExceptionFILMCfgXMLRead(
                        '_retGridGen(): Unknown LogScale value "{:s}"'.format(lgLog.text)
                    )
            return functools.partial(Track.genLog10, cycles=cycles, start=start)
        if len(e.findall(self.tagInNs('LgLinearGrid'))) > 0:
            return Track.genLinear10
        # Blank grid
        return None
    
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
        try:
            myTrackIdx = self._trackNameOrdinalMap[theTracStr]
        except KeyError:
            raise ExceptionFILMCfgXMLReadLookUp('PhysFilmCfgXMLRead.interpretTrac(): "{!r:s}" not in {:s}'.format(
                    theTracStr,
                    str(self._trackNameOrdinalMap.keys())
                )
            )
        else:
            # Work out half track starts and half track spans by walking across the tracks
            assert(myTrackIdx >= 0  and myTrackIdx < len(self._trackS))
            myTrack = self._trackS[myTrackIdx]
            try:
                # This copes with special cases such as Track23 that might appear after both track 2 and 3
                myHalfTrackStart = self.TRAC_UNIQUEID_TO_NON_STANDARD_START[theTracStr]
            except KeyError:
                myHalfTrackStart = myTrackIdx * 2
            try:
                myTracSpan = self.TRAC_UNIQUEID_TO_NON_STANDARD_SPAN[theTracStr]
            except KeyError:
                myTracSpan = self.TRAC_STANDARD_SPAN
            return myTrack.left, myTrack.right, myHalfTrackStart, myTracSpan

class FilmCfgXMLRead(FILMCfg.FilmCfg, XMLCfg.LgXMLBase):
    """Contains the configuration equivalent to a complete FILM table from a set of XML files."""
    def __init__(self, directory=None):
        """Constructor with a directory, all files in the directory (non-recursive)
        are read as LGFormat XML files. If dir is None then the "formats/" directory
        relative to this module is searched. If dir is an empty string then no search
        will be done - useful for testing with addXMLRoot(etree.fromstring(..))."""
        super().__init__()
        # TODO: Do we need this duplication?
        # Map of XML UniqueId to etree root node
        self._xmlRoot = {}
        # Map of curves to film ids i.e.:
        # {LgCurve/LgChannel>"ROP5" : [<LgFormat UniqueId="Porosity_GR_3Track", ...], ...}
        self._chOutpMnemFilmMap = {}
        self.readDir(directory)
        
    def readDir(self, d=None):
        """Read a directory of XML files (not recursive)."""
        if d == None:
            # Assume the formats/ directory relative to this module
            d = os.path.join(os.path.dirname(__file__), 'formats')
        if d != '':
            for aName in os.listdir(d):
                fp = os.path.join(d, aName)
                logging.debug('FILMCfgXML.readDir(): Opening "{:s}"'.format(fp))
                with open(fp) as f:
                    try:
                        lgFormat = etree.fromstring(f.read())
                    except etree.ParseError as err:
                        logging.error('FilmCfgXMLRead can not read XML file "{:s}": {:s}'.format(aName, str(err)))
                    else:
                        # Check and add
                        if self.checkRoot(lgFormat):
                            self.addXMLRoot(lgFormat)
                        else:
                            logging.info('FilmCfgXMLRead ignoring XML file: "{:s}"'.format(aName))

    def addXMLRoot(self, theRoot):
        """Adds a parsed LgFormat XML document to the IR."""
        assert(self.checkRoot(theRoot))
        filmID = self.elemID(theRoot)
        logging.debug('FilmCfgXMLRead.addXMLRoot(): UniqueId={:s}'.format(str(filmID)))
        # Create a PhysFilmCfgXMLRead and add it to the IR
        self.add(filmID, PhysFilmCfgXMLRead(theRoot))
        # Add curves to file ID map
        for chMnem in self._genAllMnem(theRoot):
            try:
                self._chOutpMnemFilmMap[chMnem].append(filmID)
            except KeyError:
                self._chOutpMnemFilmMap[chMnem] = [filmID,]
        if filmID in self._xmlRoot:
            logging.warning('FILMCfgXMLRead.addXMLRoot(): Ignoring duplicate FILM UniqueId: "{:s}"'.format(filmID))
        else:
            self._xmlRoot[filmID] = theRoot
        return filmID
        
    def _genAllMnem(self, theRoot):
        """Yields an unordered list of channel names from the XML file.
        The XPath is LgTrack/LgCurve."""
        for aCurveElem in theRoot.findall(self.tagsInNs('LgTrack', 'LgCurve')):
            try:
                yield self.chNameAsMnem(aCurveElem)
            except XMLCfg.ExceptionXMLCfgNoContent as err:
                logging.error('FILMCfgXMLRead.addXMLRoot(): Can not extract ChannelName from {:s}, error: {:s}'.format(str(aCurveElem), str(err)))
        
    def chOutpMnemInFilmId(self, chOutp, filmID):
        """Returns True if this curve appears in the film."""
        try:
            return filmID in self._chOutpMnemFilmMap[chOutp]
        except KeyError:
            pass
        return False
    
    def longStr(self, verbose=1):
        """Returns a long string of the XML UniqueIds and their description."""
        r = []
        maxWidth = max([len(k) for k in self._xmlRoot.keys()])
        if len(self._xmlRoot) > 0:
            r.append('{:{width}s}   {:s}'.format('UniqueId', 'Description', width=maxWidth))
            r.append('{:{width}s}   {:s}'.format('-' * maxWidth, '-' * 32, width=maxWidth))
        for k in sorted(self.keys()):
            r.append('{:{width}s} : {:s}'.format(k, self.description(k), width=maxWidth))
            if verbose > 1:
                SLICE = 12
                myCurves = sorted([m.pStr() for m in self._genAllMnem(self.rootNode(k))])
#                r.append('  Curves:')
                for curvS in [myCurves[i:i+SLICE] for i in range(0, len(myCurves), SLICE)]:
                    r.append('    ' + ', '.join(curvS))
        return '\n'.join(r)

    def uniqueIdS(self):
        """Returns the UniqueId values that I know about."""
        return self._xmlRoot.keys()
    
    def description(self, theUID):
        """Returns the XML description corresponding to the Unique ID or None if unknown."""
        lgFormat = self.rootNode(theUID)
        if lgFormat is not None:
            elemDesc = lgFormat.find(self.tagInNs('Description'))
            if elemDesc is not None:
                return elemDesc.text

    def rootNode(self, theUID):
        """Returns the XML root node corresponding to the Unique ID."""
        # print('TRACE: self._xmlRoot.keys()', self._xmlRoot.keys())
        return self._xmlRoot[theUID]

    def retAllFILMDestS(self, curveDestID):
        """Returns an unordered list of FILM destinations for a curve destination.
        For example if curveDestID is b'BOTH' this might return [b'2   ', b'1   ']
        """
        try:
            return self._chOutpMnemFilmMap[curveDestID]
        except KeyError:
            raise ExceptionFILMCfgXMLReadLookUp('FilmCfgXMLRead.retAllFILMDestS() no entry for "{:s}"'.format(str(curveDestID)))            

    def retFILMDest(self, filmDestID, curveDestID):
        """Returns a PhysFilmCfgXMLRead object by matching curveDestID to the filmDestID.
        Returns None on failure. filmDestID and curveDestID are implementation
        specific e.g. for LIS the curveDestID can be 1, BOTH, ALL, NEIT etc.
        This is commonly used by the PRESCfg module so that interpretTrac() can
        be called on the result and thus build up a map of track positions for
        all possible logical film outputs."""
        assert(filmDestID in self._plotCfgMap), '{:s} not in {:s}'.format(filmDestID, [str(k) for k in self._plotCfgMap.keys()])
        if filmDestID in self.retAllFILMDestS(curveDestID):
            return self._plotCfgMap[filmDestID]
