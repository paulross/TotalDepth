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
"""Creates PRES configurations from LgFormat XML files.

Created on Dec 16, 2011

"""

__author__  = 'Paul Ross'
__date__    = '2011-12-16'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

import logging

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import Mnem
from TotalDepth.util.plot import Stroke
from TotalDepth.util.plot import PRESCfg
from TotalDepth.util.plot import FILMCfgXML
from TotalDepth.util.plot import XMLCfg

class ExceptionPRESCfgXML(PRESCfg.ExceptionPRESCfg):
    """Specialisation of exception for PRESCfgXML module."""
    pass

class ExceptionCurveCfgXMLRead(ExceptionPRESCfgXML):
    """Specialisation of exception for CurveCfgXMLRead module."""
    pass

class ExceptionPresCfgXMLRead(ExceptionPRESCfgXML):
    """Specialisation of exception for PresCfgXMLRead module."""
    pass

#: Maps LgFormat mnemonics to a Stroke object:
#: If either value is None an SVG attribute is not needed i.e. default SVG behaviour
XML_CODI_MAP = {
    # Default
    None                        : (Stroke.StrokeBlackSolid._replace(
                                        width=PRESCfg.DEFAULT_LLINE_WIDTH_PX, coding=None)
                                   ),
    'LG_SOLID_LINE'             : (Stroke.StrokeBlackSolid._replace(
                                        width=PRESCfg.DEFAULT_LLINE_WIDTH_PX, coding=None)
                                   ),
    'LG_DOT_LINE'               : (Stroke.StrokeBlackSolid._replace(
                                        width=PRESCfg.DEFAULT_LLINE_WIDTH_PX, coding=(2,2))
                                   ),
    'LG_DASH_LINE'              : (Stroke.StrokeBlackSolid._replace(
                                        width=PRESCfg.DEFAULT_LLINE_WIDTH_PX, coding=(4,4))
                                   ),
    'LG_LONG_DASH_LINE'         : (Stroke.StrokeBlackSolid._replace(
                                        width=PRESCfg.DEFAULT_LLINE_WIDTH_PX, coding=(6,2))
                                   ),
    # These have not actually been seen in LgFormat files, they are invented but useful.
    'LG_SOLID_HEAVY_LINE'       : (Stroke.StrokeBlackSolid._replace(
                                        width=PRESCfg.DEFAULT_HLINE_WIDTH_PX, coding=None)
                                   ),
    'LG_SOLID_HEAVY_DOT'        : (Stroke.StrokeBlackSolid._replace(
                                        width=PRESCfg.DEFAULT_HLINE_WIDTH_PX, coding=(2,2))
                                   ),
    'LG_SOLID_HEAVY_DASH'       : (Stroke.StrokeBlackSolid._replace(
                                        width=PRESCfg.DEFAULT_HLINE_WIDTH_PX, coding=(4,4))
                                   ),
    'LG_SOLID_HEAVY_LONG_DASH'  : (Stroke.StrokeBlackSolid._replace(
                                        width=PRESCfg.DEFAULT_HLINE_WIDTH_PX, coding=(6,2))
                                   ),
}

#: Maps LgFormat backup specifications to an internal representation
#: Taken from the ``<WrapMode>`` element.
BACKUP_FROM_MODE_MAP = {
    None                : PRESCfg.BACKUP_ALL, # Default
    'LG_LEFT_WRAPPED'   : PRESCfg.BACKUP_LEFT,
    'LG_RIGHT_WRAPPED'  : PRESCfg.BACKUP_RIGHT,
    'LG_WRAPPED'        : PRESCfg.BACKUP_ALL,
    'LG_X10'            : PRESCfg.BACKUP_ALL,
    '1'                 : PRESCfg.BACKUP_ONCE,
    '2'                 : PRESCfg.BACKUP_TWICE,
}
#: Fallback mapping LgFormat backup specifications to an internal representation
#: Taken from the ``<WrapCount>`` element.
BACKUP_FROM_COUNT_MAP = {
    None                : PRESCfg.BACKUP_ALL, # Default
    '1'                 : PRESCfg.BACKUP_ONCE,
    '2'                 : PRESCfg.BACKUP_TWICE,
}
assert(None in BACKUP_FROM_MODE_MAP)
assert(None in BACKUP_FROM_COUNT_MAP)

class CurveCfgXMLRead(PRESCfg.CurveCfg, XMLCfg.LgXMLBase):
    """Represents a single curve from an XML file specification"""
    #: First column is observed tracks in the XML, note capitalisation inconsistencies.
    #: Second column is LIS DEST equivalent
    TRAC_XML_UNIQUEID_TO_PRES = {
        'depthTrack'            : b'TD  ',
        'DepthTrack'            : b'TD  ',
#        'timeTrack'             : None,
        'track1'                : b'T1  ',
        'track12'               : b'T12 ',
        'track2'                : b'T2  ',
        'Track2'                : b'T2  ',
        'track23'               : b'T23 ',
        'track3'                : b'T3  ',
        'Track3'                : b'T3  ',
        'track4'                : b'T4  ',
#        'track5'                : None,
#        'track6'                : None,
        'TrackFC0'              : b'LHT2',
        'TrackFC1'              : b'LHT2',
        'TrackFC2'              : b'RHT2',
        'TrackFC3'              : b'LHT3',
        'TrackFC4'              : b'RHT2',
        'trackLHT1'             : b'LHT1',
        'trackRHT1'             : b'RHT1',
    }
    def __init__(self, e, theTrac, theFILMCfg):
        """Creates a single CurveCfg object from an XML LgCurve element and populates a CurveCfg.
        e is the root LgCurve element.
        theTrac is the track name that this is being plotted on.
        theFILMCfg is expected to be a FilmCfgXMLRead object.
        
        Example::
        
            <LgCurve UniqueId="ROP5">
                <ChannelName>ROP5</ChannelName>
                <Color>0000FF</Color>
                <LeftLimit>500</LeftLimit>
                <RightLimit>0</RightLimit>
                <LineStyle>LG_DASH_LINE</LineStyle>
                <Thickness>1.75</Thickness>
                <WrapMode>LG_LEFT_WRAPPED</WrapMode>
            </LgCurve>
            Or:
            <LgCurve UniqueId="PSR">
                <ChannelName>PSR</ChannelName>
                <Color>00C000</Color>
                <LeftLimit>0.2</LeftLimit>
                <RightLimit>2000</RightLimit>
                <Thickness>2</Thickness>
                <Transform>LG_LOGARITHMIC</Transform>
                <WrapCount>0</WrapCount>
            </LgCurve>
        """
        super().__init__()
        assert(e.tag == self.tagInNs('LgCurve')), 'Wrong element {:s}'.format(e.tag)
        assert(isinstance(theFILMCfg, FILMCfgXML.FilmCfgXMLRead))
        self.mnem = Mnem.Mnem(self.elemID(e), len_mnem=0)
        logging.debug(
            'CurveCfgXMLRead.__init__(): mnem="{!r:s}"'
            ' trac="{!r:s}"'.format(self.mnem, theTrac))
        try:
            self.outp = self.chNameAsMnem(e)
        except XMLCfg.ExceptionXMLCfgNoContent as err:
            raise ExceptionCurveCfgXMLRead('Can not read Mnemonic: {:s}'.format(str(err)))
        self.stat = self.bool(e, self.tagInNs('Visible'), True)
        # This is not relevant, it refers to the PRES table TRAC column e.g. b'T23 '
#        try:
#            self.trac = self.TRAC_XML_UNIQUEID_TO_PRES[theTrac]
#        except KeyError:
#            raise ExceptionCurveCfgXMLRead('Unsupported track: {:s}'.format(str(theTrac)))
        self.trac = theTrac
        self.dest = self.outp
        self.filt = self.DEFAULT_FILT
        self.mode = self.str(e, self.tagInNs('Transform'), None)
        # Backup mode
        myBackup = self._retBackup(e)
        # Colour and coding
        self.codiStroke = self._retCoding(e) 
        # Initialise a map of {film_id : TrackWidthData, ...}
        self._filmTrackWidthMap.clear()
        # Map of track transfer function keyed to film destination:
        # {film_id : LineTransBase, ...}
        self._filmTrackFnMap.clear()
#        print('TRACE: theFILMCfg.keys()', theFILMCfg.keys())
        for aFilmID in theFILMCfg.keys():
            if theFILMCfg.chOutpMnemInFilmId(self.outp, aFilmID):
                # TODO: Does this now ever raise an exception or return None?
                # This may raise a ExceptionPhysFilmCfg
                try:
                    myIntTrac = theFILMCfg.interpretTrac(aFilmID, self.dest, self.trac)
                except ExceptionTotalDepthLIS as err:
#                     logging.error(
#                         'CurveCfgXMLRead.__init__(): can not get trac: {!r:s}'.format(str(err))
#                     )
                    pass
                else:
                    leftLimit = self.float(e, self.tagInNs('LeftLimit'))
                    rightLimit = self.float(e, self.tagInNs('RightLimit'))
                    # myIntTrac can be None if the destination is NEIT for example
                    if myIntTrac is None: 
                        logging.warning(
                            'Got None from theFILMCfg.interpretTrac(FILM ID={!r:s},'
                            ' PRES DEST={!r:s}, PRES TRAC={!r:s})'.format(aFilmID,
                                                                          self.dest,
                                                                          self.trac)
                        )
                    elif leftLimit == rightLimit:
                        logging.warning(
                            '"{!r:s}" Left/right track limits equal [{:g}]'
                            ' from theFILMCfg.interpretTrac(FILM ID={!r:s},'
                            ' PRES DEST={!r:s}, PRES TRAC={!r:s})'.format(
                            self.mnem, leftLimit, aFilmID, self.dest, self.trac)
                        )
                    else:
                        # Make a new instance of TrackWidthData from the four part iterable
                        myTw = PRESCfg.TrackWidthData._make(myIntTrac)
                        self._filmTrackWidthMap[aFilmID] = myTw
                        if self.mode == 'LG_LOGARITHMIC':
                            self._filmTrackFnMap[aFilmID] = PRESCfg.LineTransLog10(
                                myTw.leftP.value,
                                myTw.rightP.value,
                                leftLimit,
                                rightLimit,
                                myBackup)
                        else:
                            self._filmTrackFnMap[aFilmID] = PRESCfg.LineTransLin(
                                myTw.leftP.value,
                                myTw.rightP.value,
                                leftLimit,
                                rightLimit,
                                myBackup)
            else:
                pass
#                logging.warning('outp "{:s}" not in "{:s}"'.format(str(self.outp), aFilmID))
        assert(len(self._filmTrackWidthMap) == len(self._filmTrackFnMap))
        if len(self._filmTrackWidthMap) == 0:
            raise ExceptionCurveCfgXMLRead(
                'Can not map films to curve="{!s:s}"'.format(self.outp)
            )

    def _retBackup(self, e):
        assert(e.tag == self.tagInNs('LgCurve')), 'Wrong element "{:s}"'.format(e.tag)
        myMode = self.str(e, self.tagInNs('WrapMode'), None)
        if myMode is not None:
            try:
                return BACKUP_FROM_MODE_MAP[myMode]
            except KeyError:
                logging.warning(
                    'CurveCfgXMLRead._retBackup():'
                    ' Unsupported WrapMode: {:s}.'.format(myMode)
                )
        # Fallback on count if present
        myCount = self.str(e, self.tagInNs('WrapCount'), None)
        if myCount is not None:
            try:
                return BACKUP_FROM_COUNT_MAP[myCount]
            except KeyError:
                logging.warning(
                    'CurveCfgXMLRead._retBackup():'
                    ' Unsupported WrapCount: {:s}.'.format(myCount)
                )
        # Final fallback on default
        assert(None in BACKUP_FROM_MODE_MAP)
        return BACKUP_FROM_MODE_MAP[None]

    def _retCoding(self, e):
        assert(e.tag == self.tagInNs('LgCurve')), 'Wrong element "{:s}"'.format(e.tag)
        myTxt = self.str(e, self.tagInNs('LineStyle'), None)
        try:
            r = XML_CODI_MAP[myTxt]
        except KeyError:
            assert(None in XML_CODI_MAP)
            logging.warning(
                'CurveCfgXMLRead.__init__(): Unsupported LineStyle:'
                ' {:s}. Have substituted the default.'.format(myTxt)
            )
            r = XML_CODI_MAP[None]
        # Add in the Color element
        return r._replace(colour=self._retColour(e))

    def _retColour(self, e):
        """Returns the colour as an SVG acceptable string."""
        assert(e.tag == self.tagInNs('LgCurve')), 'Wrong element "{:s}"'.format(e.tag)
        c = self.str(e, self.tagInNs('Color'), None)
        if c is None:
            c = '000000'
        valS = [int(c[i:i+2], 16) for i in range(0,len(c),2)]
        return 'rgb({:d},{:d},{:d})'.format(*valS)

class PresCfgXMLRead(PRESCfg.PresCfg, XMLCfg.LgXMLBase):
    """Extracts all curve presentation information from a single XML file."""
    def __init__(self, theFILMCfg, theUniqueId):
        """Reads a XML and creates a CurveCfgXMLRead for
        each LgFormat/LgTrack/LgCurve element.
        
        theFILMCfg is expected to be a FILMCfgXMLRead object. 
        """
        super().__init__()
        try:
            root = theFILMCfg.rootNode(theUniqueId)
        except KeyError:
            raise ExceptionPresCfgXMLRead(
                'PresCfgXMLRead.__init__():'
                ' No root element for UniqueId="{}"'.format(theUniqueId))
        if root.tag != self.tagInNs('LgFormat'):
            raise ExceptionPresCfgXMLRead(
                'PresCfgXMLRead.__init__():'
                ' Wrong root element {:s}'.format(root.tag))
        for aTrac in root.findall(self.tagInNs('LgTrack')):
            trackID = self.elemID(aTrac)
            for aCurv in aTrac.findall(self.tagInNs('LgCurve')):
                try:
                    chMnem = self.chNameAsMnem(aCurv)
                except XMLCfg.ExceptionXMLCfgNoContent as err:
                    raise ExceptionPresCfgXMLRead(
                        'Can not read Mnemonic: {:s}'.format(str(err)))
                logging.debug(
                    'PresCfgXMLRead.__init__(): XML ID="{:s}"'
                    ' trackID="{!r:s}" chName="{!r:s}"'.format(self.elemID(root),
                                                             trackID,
                                                             chMnem))
                try:
                    self.add(
                        CurveCfgXMLRead(aCurv, trackID, theFILMCfg),
                        theFILMCfg.retAllFILMDestS(chMnem),
                    )
                except ExceptionCurveCfgXMLRead as err:
                    logging.info('PresCfgXMLRead.__init__(): Can not add curve {!r:s}, error is: {!r:s}'.format(
                            self.elemID(aCurv),
                            err,
                        )
                    )
#                    logging.error('PresCfgXMLRead.__init__(): Can not add curve {:s}, error is: {:s}'.format(
#                            self.elemID(aCurv),
#                            err,
#                        )
#                    )
