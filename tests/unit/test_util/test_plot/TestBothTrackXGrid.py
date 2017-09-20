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
"""Tests Track and XGrid SVG plotting
"""

__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

#import pprint
import sys
import time
import logging
import io

from TotalDepth.util.plot import Coord
from TotalDepth.util.plot import Stroke
from TotalDepth.util.plot import Track
from TotalDepth.util.plot import XGrid
from TotalDepth.util.plot import Plot
from TotalDepth.util.plot import SVGWriter
from TotalDepth.util.plot import PlotConstants

######################
# Section: Unit tests.
######################
import unittest

class TestBothTrackXGrid(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestCLass: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestPlotTrack.test_00(): Construct a lin/log/log track with FEET 1/200 and plot it in SVG."""
        myCnv = Plot.Canvas(Coord.Dim(8.5, 'in'), Coord.Dim(12, 'in'), PlotConstants.MarginQtrInch)
        myViewPort = Coord.Box(
            width=myCnv.width,
            depth=myCnv.depth,
        )
        myTopLeft = Coord.Pt(Coord.Dim(0.25, 'in'), Coord.Dim(0.25, 'in'))
        myF = io.StringIO()
        myTracks = [
            Track.Track(
                leftPos=Coord.Dim(0.0, 'in'), 
                rightPos=Coord.Dim(2.4, 'in'),
                gridGn=Track.genLinear10
            ),
            Track.Track(
                leftPos=Coord.Dim(2.4, 'in'), 
                rightPos=Coord.Dim(3.2, 'in'),
                gridGn=None,
                plotXAxis=True,
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
        ]
        with SVGWriter.SVGWriter(myF, myViewPort) as xS:
            # Do tracks first
            for t in myTracks:
                #xS.comment(str(t))
                if t.hasGrid:
                    t.plotSVG(
                        myTopLeft,
                        myCnv.depth - myCnv.margins.top - myCnv.margins.bottom,
                        xS,
                    )
            # Now XGrid
            # We are plotting up so xPosStart is at bottom
            myXposStart = myCnv.depth - myCnv.margins.bottom
            myXposStop = myCnv.margins.top
            myXg = XGrid.XGrid(200)
            # Plot depth lines
            for pos, stroke in myXg.genXPosStroke(xFrom=4307.5, xInc=False, units=b'FEET'):
                myXpos = myXposStart + pos
                if myXpos < myXposStop:
                    break
                for t in myTracks:
                    if t.hasGrid:
                        with SVGWriter.SVGLine(
                                xS,
                                Coord.Pt(t.left+myCnv.margins.left, myXpos),
                                Coord.Pt(t.right+myCnv.margins.left, myXpos),
                                attrs=Stroke.retSVGAttrsFromStroke(stroke)
                            ):
                            pass
            # Plot depth text
            textAttrs = {
                'text-anchor'       : 'end',
                'dominant-baseline' : 'middle',
            }
            for pos, val in myXg.genXPosText(xFrom=4307.5, xInc=False, units=b'FEET'):
                myXpos = myXposStart + pos
                if myXpos < myXposStop:
                    break
                for t in myTracks:
                    if t.plotXAxis:
                        myPt = Coord.Pt(t.right+myCnv.margins.left-Coord.Dim(0.05, 'in'), myXpos)
                        with SVGWriter.SVGText(xS, myPt, 'Courier', 16, textAttrs):
                            xS.characters(str(val))
        print()
        print(myF.getvalue())

class Special(unittest.TestCase):
    """Special tests."""
    pass


def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBothTrackXGrid))
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
