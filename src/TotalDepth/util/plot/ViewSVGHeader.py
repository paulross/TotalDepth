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
"""Used to find the dimensions of an API header drawn in SVG such as Inkscape.

This is merely for development and discovery.

Created on Dec 31, 2011

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2011 Paul Ross.'

import sys
import os
import logging
import time
import pprint
import multiprocessing
from optparse import OptionParser
import collections

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

Rect = collections.namedtuple('Rect', 'x y w h desc title')
Static = collections.namedtuple('Static', 'x y w h text')


class ViewSVG(object):  # pragma: no cover
    """Class documentation."""
    NS_SVG = '{http://www.w3.org/2000/svg}'
    def __init__(self, fp):
        self._fp = fp
        tree = etree.parse(self._fp)
        root = tree.getroot()
#        print(root)
#        pprint.pprint(root.findall(self._tagsInSVGNs('g', 'rect')))
#        pprint.pprint(list(root))
#        for rElem in root.findall(self._tagsInSVGNs('g', 'rect')):
#            print(self._readRect(rElem))
        rectS = [self._readRect(r) for r in root.findall(self._tagsInSVGNs('g', 'rect'))]
#        print(rectS)
        print(    '_getMarkers():', self._getMarkers(rectS))
        print('_getWidDepScale():', self._getWidDepScale(rectS))
        self._datumX, self._datumY, self._scaleW, self._scaleD = self._getWidDepScale(rectS)
        self._staticS = [self._retStatic(self._readRect(r)) for r in root.findall(self._tagsInSVGNs('g', 'rect')) if self._isStaticElem(r)]
        pprint.pprint(sorted(self._staticS))
        
    def _getMarkers(self, rS):
        """Returns top-left in pixels and box that should represent w=6.25 inches h=8.25 inches
        Looks like inkscape uses 90px/inch, we use 96px/inch...
        From Plot.py, Okay here width/depth reversed...
        STANDARD_PAPER_WIDTH = Coord.Dim(8.5, 'in')
        STANDARD_PAPER_DEPTH = Coord.Dim(6.25, 'in')
        """
        tl = None
        br = None
        for r in rS:
            if r.desc == 'marker':
                if r.title == 'Bottom Right':
                    br = float(r.x), float(r.y)
                elif r.title == 'Top Left':
                    tl = float(r.x), float(r.y)
                else:
                    print('Unknown marker {:s}'.format(r.title))
        if tl is not None and br is not None:
            return tl, (br[0] - tl[0], br[1] - tl[1])
        return None, None
    
    def _getWidDepScale(self, rS):
        (w0, d0), (w, d) = self._getMarkers(rS)
        return w0, d0, (w) / 6.25, (d) / 8.5
    
    def _scaleX(self, x):
        return (x - self._datumX) / self._scaleW
    
    def _scaleY(self, y):
        return (y - self._datumY) / self._scaleD
    
    def _retStatic(self, r):
        return Static(
            self._scaleX(r.x),
            self._scaleY(r.y),
            r.w / self._scaleW,
            r.h / self._scaleD,
            r.title,
        )
    
    def _isStaticElem(self, e):
        assert(e.tag == self._tagInSVGNs('rect')), 'r.tag is {:s}'.format(e.tag)
        return 'stroke:#0000ff' in e.get('style')
        
    def _readRect(self, r):
        """Reads a <rect> element. Example:
<rect
   style="fill:none;stroke:#000000;stroke-width:0.5;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none"
   id="rect3286-1"
   width="2.0211718"
   height="2.0211718"
   x="582.09656"
   y="799.45789">
  <desc
     id="desc4058-7">marker</desc>
  <title
     id="title4056-4">Bottom Right</title>
</rect>"""
        assert(r.tag == self._tagInSVGNs('rect')), 'r.tag is {:s}'.format(r.tag)
        w = float(r.get('width'))
        h = float(r.get('height'))
        x = float(r.get('x'))
        y = float(r.get('y'))
        desc = self.getText(r, 'desc')
        title = self.getText(r, 'title')
        return Rect(x, y, w, h, desc, title)
    
    def _tagInSVGNs(self, tag):
        return self.NS_SVG + tag
    
    def _tagsInSVGNs(self, *args):
        return '/'.join([self._tagInSVGNs(tag) for tag in args])
    
    def getText(self, e, *args):
        return ''.join([r.text for r in e.findall(self._tagsInSVGNs(*args))])
    

def main():  # pragma: no cover
    usage = """usage: %prog [options] in out
Generates plot(s) from input LIS file or directory to and output destination."""
    print ('Cmd: %s' % ' '.join(sys.argv))
    optParser = OptionParser(usage, version='%prog ' + __version__)
#    optParser.add_option("-k", "--keep-going", action="store_true", dest="keepGoing", default=False, 
#                      help="Keep going as far as sensible. [default: %default]")
#    optParser.add_option("-r", "--recursive", action="store_true", dest="recursive", default=False, 
#                      help="Process input recursively. [default: %default]")
    optParser.add_option(
            "-j", "--jobs",
            type="int",
            dest="jobs",
            default=-1,
            help="Max processes when multiprocessing. Zero uses number of native CPUs [%d]. -1 disables multiprocessing." \
                    % multiprocessing.cpu_count() \
                    + " [default: %default]" 
        )      
    optParser.add_option(
            "-l", "--loglevel",
            type="int",
            dest="loglevel",
            default=40,
            help="Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: %default]"
        )      
    opts, args = optParser.parse_args()
    clkStart = time.clock()
    timStart = time.time()
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    # Your code here
    if len(args) != 1:
        optParser.print_help()
        return 1
    myObj = ViewSVG(args[0])
    print('  CPU time = %8.3f (S)' % (time.clock() - clkStart))
    print('Exec. time = %8.3f (S)' % (time.time() - timStart))
    print('Bye, bye!')
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
