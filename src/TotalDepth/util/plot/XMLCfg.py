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
"""Provides low level support for XML plot configurations

Created on Dec 13, 2011

"""

__author__  = 'Paul Ross'
__date__    = '2011-12-13'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

#import logging

from TotalDepth.LIS.core import Mnem
from TotalDepth.util.plot import ExceptionUtilPlot

class ExceptionXMLCfg(ExceptionUtilPlot):
    """Exception class for this module."""
    pass

class ExceptionXMLCfgWrongRootElem(ExceptionXMLCfg):
    """Exception when the root element is wrong."""
    pass

class ExceptionXMLCfgMissingElem(ExceptionXMLCfg):
    """Exception when the is a missing mandatory element."""
    pass

class ExceptionXMLCfgNoContent(ExceptionXMLCfg):
    """Exception when the is missing content."""
    pass

class LgXMLBase(object):
    """Base class for XML functionality that can be used by both FILM and PRES XML classes."""
    NAMESPACE = '{x-schema:LgSchema2.xml}'
    
    def checkRoot(self, root):
        if root.tag != self.tagInNs('LgFormat'):
            return False
#            raise ExceptionXMLCfgWrongRootElem('LgXMLBase wrong root element: "{:s}"'.format(root.tag))
#        print(root.items())
#        if root.get('UniqueId') is None:
        if self.elemID(root) is None:
            return False
#            raise ExceptionXMLCfgWrongRootElem(
#                'LgXMLBase root element missing UniqueId: {:s}'.format(str(root.items()))
#            )
        return True
    
    def str(self, e, name, default=None):
        """Returns the text in a single child element or None."""
        elemS = e.findall(name)
        if len(elemS) == 1:
            return elemS[0].text
        return default

    def bool(self, e, name, default=False):
        """Returns the text in a single child element converting 1/0 to True/False."""
        elemS = e.findall(name)
        if len(elemS) == 1:
            return not elemS[0].text.strip() == '0'
        return default

    def int(self, e, name, default=0):
        """Returns the text in a single child element as an integer defaulting to 0."""
        elemS = e.findall(name)
        if len(elemS) == 1:
            return int(elemS[0].text)
        return default

    def float(self, e, name, default=0.0):
        """Returns the text in a single child element as a float."""
        elemS = e.findall(name)
        if len(elemS) == 1:
            return float(elemS[0].text)
        return default

    def tagInNs(self, tag):
        return self.NAMESPACE + tag
    
    def tagsInNs(self, *args):
        return '/'.join([self.tagInNs(tag) for tag in args])
    
    def elemID(self, e):
        return e.get('UniqueId')
    
    def chNameAsMnem(self, e):
        myStr = self.str(e, self.tagInNs('ChannelName'), None)
        if myStr is None:
            raise ExceptionXMLCfgNoContent('LgXMLBase.chNameAsMnem(): No ChannelName CDATA.')
        return Mnem.Mnem(myStr, len_mnem=-Mnem.LEN_MNEM)
    