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

__author__  = 'Paul Ross'
__date__    = '2009-09-15'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'

"""Treats SVG writing."""

#import os
import sys
import time
import logging
import io

from TotalDepth.util import XmlWrite
from TotalDepth.util.plot import SVGWriter, Coord

######################
# Section: Unit tests.
######################
import unittest

class TestSVGWriter(unittest.TestCase):
    """Tests SVGWriter."""
    def test_00(self):
        """TestSVGWriter.test_00(): construction."""
        myF = io.StringIO()
        myViewPort = Coord.Box(
            Coord.Dim(100, 'mm'),
            Coord.Dim(20, 'mm'),
        )
        with SVGWriter.SVGWriter(myF, myViewPort):
            pass
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="20.000mm" version="1.1" width="100.000mm" xmlns="http://www.w3.org/2000/svg"/>\n""")
        
    def test_01(self):
        """TestSVGlWriter.test_01(): <desc> and four rectangles.
        From second example in http://www.w3.org/TR/2003/REC-SVG11-20030114/struct.html#NewDocumentOverview"""
        myF = io.StringIO()
        myViewPort = Coord.Box(
            Coord.Dim(5, 'cm'),
            Coord.Dim(4, 'cm'),
        )
        with SVGWriter.SVGWriter(myF, myViewPort) as xS:
            with XmlWrite.Element(xS, 'desc'):
                xS.characters('Four separate rectangles')
            myPt = Coord.Pt(Coord.Dim(0.5, 'cm'), Coord.Dim(0.5, 'cm'))
            myBx = Coord.Box(Coord.Dim(2.0, 'cm'), Coord.Dim(1.0, 'cm'))
            with SVGWriter.SVGRect(xS, myPt, myBx):
                pass
            myPt = Coord.Pt(Coord.Dim(0.5, 'cm'), Coord.Dim(2.0, 'cm'))
            myBx = Coord.Box(Coord.Dim(1.0, 'cm'), Coord.Dim(1.5, 'cm'))
            with SVGWriter.SVGRect(xS, myPt, myBx):
                pass
            myPt = Coord.Pt(Coord.Dim(3.0, 'cm'), Coord.Dim(0.5, 'cm'))
            myBx = Coord.Box(Coord.Dim(1.5, 'cm'), Coord.Dim(2.0, 'cm'))
            with SVGWriter.SVGRect(xS, myPt, myBx):
                pass
            myPt = Coord.Pt(Coord.Dim(3.5, 'cm'), Coord.Dim(3.0, 'cm'))
            myBx = Coord.Box(Coord.Dim(1.0, 'cm'), Coord.Dim(0.5, 'cm'))
            with SVGWriter.SVGRect(xS, myPt, myBx):
                pass
            myPt = Coord.Pt(Coord.Dim(0.01, 'cm'), Coord.Dim(0.01, 'cm'))
            myBx = Coord.Box(Coord.Dim(4.98, 'cm'), Coord.Dim(3.98, 'cm'))
            with SVGWriter.SVGRect(
                    xS,
                    myPt,
                    myBx,
                    attrs= {
                            'fill'          : "none",
                            'stroke'        : "blue",
                            'stroke-width'  : ".02cm",
                        }
                ):
                pass
        # print()
        # print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="4.000cm" version="1.1" width="5.000cm" xmlns="http://www.w3.org/2000/svg">
  <desc>Four separate rectangles</desc>
  <rect height="1.000cm" width="2.000cm" x="0.500cm" y="0.500cm"/>
  <rect height="1.500cm" width="1.000cm" x="0.500cm" y="2.000cm"/>
  <rect height="2.000cm" width="1.500cm" x="3.000cm" y="0.500cm"/>
  <rect height="0.500cm" width="1.000cm" x="3.500cm" y="3.000cm"/>
  <rect fill="none" height="3.980cm" stroke="blue" stroke-width=".02cm" width="4.980cm" x="0.010cm" y="0.010cm"/>
</svg>
""")
       
    def test_02(self):
        """TestSVGlWriter.test_02(): a circle.
        From http://www.w3.org/TR/2003/REC-SVG11-20030114/shapes.html#CircleElement"""
        myF = io.StringIO()
        myViewPort = Coord.Box(
            Coord.Dim(12, 'cm'),
            Coord.Dim(4, 'cm'),
        )
        with SVGWriter.SVGWriter(myF, myViewPort) as xS:
            with XmlWrite.Element(xS, 'desc'):
                xS.characters('Example circle01 - circle filled with red and stroked with blue')
            #xS.comment(" Show outline of canvas using 'rect' element ")
            myPt = Coord.Pt(Coord.baseUnitsDim(1), Coord.baseUnitsDim(1))
            myBx = Coord.Box(Coord.baseUnitsDim(1198), Coord.baseUnitsDim(398))
            with SVGWriter.SVGRect(xS, myPt, myBx, {'fill':"none", 'stroke':"blue",'stroke-width':"2"}):
                pass
            myPt = Coord.Pt(Coord.baseUnitsDim(600), Coord.baseUnitsDim(200))
            myRad = Coord.baseUnitsDim(100)
            with SVGWriter.SVGCircle(xS, myPt, myRad, {'fill':"red", 'stroke':"blue",'stroke-width':"10"}):
                pass
        # print()
        # print(myF.getvalue())
#        self.maxDiff = None
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="4.000cm" version="1.1" width="12.000cm" xmlns="http://www.w3.org/2000/svg">
  <desc>Example circle01 - circle filled with red and stroked with blue</desc>
  <rect fill="none" height="398.000px" stroke="blue" stroke-width="2" width="1198.000px" x="1.000px" y="1.000px"/>
  <circle cx="600.000px" cy="200.000px" fill="red" r="100.000px" stroke="blue" stroke-width="10"/>
</svg>
""")

    def test_03(self):
        """TestSVGlWriter.test_03(): an elipse.
        Based on http://www.w3.org/TR/2003/REC-SVG11-20030114/shapes.html#EllipseElement"""
        myF = io.StringIO()
        myViewPort = Coord.Box(
            Coord.Dim(12, 'cm'),
            Coord.Dim(4, 'cm'),
        )
        with SVGWriter.SVGWriter(myF, myViewPort) as xS:
            with XmlWrite.Element(xS, 'desc'):
                xS.characters('Example ellipse01 - examples of ellipses')
            #xS.comment(" Show outline of canvas using 'rect' element ")
            myPt = Coord.Pt(Coord.baseUnitsDim(1), Coord.baseUnitsDim(1))
            myBx = Coord.Box(Coord.baseUnitsDim(1198), Coord.baseUnitsDim(398))
            with SVGWriter.SVGRect(xS, myPt, myBx, {'fill':"none", 'stroke':"blue",'stroke-width':"2"}):
                pass
            myPt = Coord.Pt(Coord.baseUnitsDim(600), Coord.baseUnitsDim(200))
            myRadX = Coord.baseUnitsDim(250)
            myRadY = Coord.baseUnitsDim(100)
            with SVGWriter.SVGElipse(xS, myPt, myRadX, myRadY, {'fill':"red", 'stroke':"blue",'stroke-width':"10"}):
                pass
        # print()
        # print(myF.getvalue())
#        self.maxDiff = None
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="4.000cm" version="1.1" width="12.000cm" xmlns="http://www.w3.org/2000/svg">
  <desc>Example ellipse01 - examples of ellipses</desc>
  <rect fill="none" height="398.000px" stroke="blue" stroke-width="2" width="1198.000px" x="1.000px" y="1.000px"/>
  <elipse cx="600.000px" cy="200.000px" fill="red" rx="250.000px" ry="100.000px" stroke="blue" stroke-width="10"/>
</svg>
""")

    def test_04(self):
        """TestSVGlWriter.test_04(): a line.
        Based on http://www.w3.org/TR/2003/REC-SVG11-20030114/shapes.html#LineElement"""
        myF = io.StringIO()
        myViewPort = Coord.Box(
            Coord.Dim(12, 'cm'),
            Coord.Dim(4, 'cm'),
        )
        with SVGWriter.SVGWriter(myF, myViewPort) as xS:
            with XmlWrite.Element(xS, 'desc'):
                xS.characters('Example line01 - lines expressed in user coordinates')
            #xS.comment(" Show outline of canvas using 'rect' element ")
            myPt = Coord.Pt(Coord.baseUnitsDim(1), Coord.baseUnitsDim(1))
            myBx = Coord.Box(Coord.baseUnitsDim(1198), Coord.baseUnitsDim(398))
            with SVGWriter.SVGRect(xS, myPt, myBx, {'fill':"none", 'stroke':"blue",'stroke-width':"2"}):
                pass
            # Make a group
            with SVGWriter.SVGGroup(xS, {'stroke' : 'green'}):
                with SVGWriter.SVGLine(
                        xS,
                        Coord.Pt(Coord.baseUnitsDim(100), Coord.baseUnitsDim(300)), 
                        Coord.Pt(Coord.baseUnitsDim(300), Coord.baseUnitsDim(100)), 
                        {'stroke-width' : "5"}
                    ):
                    pass
                with SVGWriter.SVGLine(
                        xS,
                        Coord.Pt(Coord.baseUnitsDim(300), Coord.baseUnitsDim(300)), 
                        Coord.Pt(Coord.baseUnitsDim(500), Coord.baseUnitsDim(100)), 
                        {'stroke-width' : "10"}
                    ):
                    pass
                with SVGWriter.SVGLine(
                        xS,
                        Coord.Pt(Coord.baseUnitsDim(500), Coord.baseUnitsDim(300)), 
                        Coord.Pt(Coord.baseUnitsDim(700), Coord.baseUnitsDim(100)), 
                        {'stroke-width' : "15"}
                    ):
                    pass
                with SVGWriter.SVGLine(
                        xS,
                        Coord.Pt(Coord.baseUnitsDim(700), Coord.baseUnitsDim(300)), 
                        Coord.Pt(Coord.baseUnitsDim(900), Coord.baseUnitsDim(100)), 
                        {'stroke-width' : "20"}
                    ):
                    pass
                with SVGWriter.SVGLine(
                        xS,
                        Coord.Pt(Coord.baseUnitsDim(900), Coord.baseUnitsDim(300)), 
                        Coord.Pt(Coord.baseUnitsDim(1100), Coord.baseUnitsDim(100)), 
                        {'stroke-width' : "25"}
                    ):
                    pass
        # print()
        # print(myF.getvalue())
#        self.maxDiff = None
        self.assertEqual("""<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="4.000cm" version="1.1" width="12.000cm" xmlns="http://www.w3.org/2000/svg">
  <desc>Example line01 - lines expressed in user coordinates</desc>
  <rect fill="none" height="398.000px" stroke="blue" stroke-width="2" width="1198.000px" x="1.000px" y="1.000px"/>
  <g stroke="green">
    <line stroke-width="5" x1="100.000px" x2="300.000px" y1="300.000px" y2="100.000px"/>
    <line stroke-width="10" x1="300.000px" x2="500.000px" y1="300.000px" y2="100.000px"/>
    <line stroke-width="15" x1="500.000px" x2="700.000px" y1="300.000px" y2="100.000px"/>
    <line stroke-width="20" x1="700.000px" x2="900.000px" y1="300.000px" y2="100.000px"/>
    <line stroke-width="25" x1="900.000px" x2="1100.000px" y1="300.000px" y2="100.000px"/>
  </g>
</svg>
""",
        myF.getvalue())

    def test_05(self):
        """TestSVGlWriter.test_05(): a polyline.
        Based on http://www.w3.org/TR/2003/REC-SVG11-20030114/shapes.html#PolylineElement"""
        myF = io.StringIO()
        myViewPort = Coord.Box(
            Coord.Dim(12, 'cm'),
            Coord.Dim(4, 'cm'),
        )
        with SVGWriter.SVGWriter(myF, myViewPort, {'viewBox' : "0 0 1200 400"}) as xS:
            with XmlWrite.Element(xS, 'desc'):
                xS.characters('Example line01 - lines expressed in user coordinates')
            #xS.comment(" Show outline of canvas using 'rect' element ")
            myPt = Coord.Pt(Coord.baseUnitsDim(1), Coord.baseUnitsDim(1))
            myBx = Coord.Box(Coord.baseUnitsDim(1198), Coord.baseUnitsDim(398))
            with SVGWriter.SVGRect(xS, myPt, myBx, {'fill':"none", 'stroke':"blue",'stroke-width':"2"}):
                pass
            # Make a group
            with SVGWriter.SVGPolyline(
                    xS,
                    [
                        Coord.Pt(Coord.baseUnitsDim(50), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(150), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(150), Coord.baseUnitsDim(325)),
                        Coord.Pt(Coord.baseUnitsDim(250), Coord.baseUnitsDim(325)),
                        Coord.Pt(Coord.baseUnitsDim(250), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(350), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(350), Coord.baseUnitsDim(250)),
                        Coord.Pt(Coord.baseUnitsDim(450), Coord.baseUnitsDim(250)),
                        Coord.Pt(Coord.baseUnitsDim(450), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(550), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(550), Coord.baseUnitsDim(175)),
                        Coord.Pt(Coord.baseUnitsDim(650), Coord.baseUnitsDim(175)),
                        Coord.Pt(Coord.baseUnitsDim(650), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(750), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(750), Coord.baseUnitsDim(100)),
                        Coord.Pt(Coord.baseUnitsDim(850), Coord.baseUnitsDim(100)),
                        Coord.Pt(Coord.baseUnitsDim(850), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(950), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(950), Coord.baseUnitsDim(25)),
                        Coord.Pt(Coord.baseUnitsDim(1050), Coord.baseUnitsDim(25)),
                        Coord.Pt(Coord.baseUnitsDim(1050), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(1150), Coord.baseUnitsDim(375)),
                    ],
                    {'fill' : 'none', 'stroke' : 'blue', 'stroke-width' : "5"}
                ):
                pass
        # print()
        # print(myF.getvalue())
#        self.maxDiff = None
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="4.000cm" version="1.1" viewBox="0 0 1200 400" width="12.000cm" xmlns="http://www.w3.org/2000/svg">
  <desc>Example line01 - lines expressed in user coordinates</desc>
  <rect fill="none" height="398.000px" stroke="blue" stroke-width="2" width="1198.000px" x="1.000px" y="1.000px"/>
  <polyline fill="none" points="50.0,375.0 150.0,375.0 150.0,325.0 250.0,325.0 250.0,375.0 350.0,375.0 350.0,250.0 450.0,250.0 450.0,375.0 550.0,375.0 550.0,175.0 650.0,175.0 650.0,375.0 750.0,375.0 750.0,100.0 850.0,100.0 850.0,375.0 950.0,375.0 950.0,25.0 1050.0,25.0 1050.0,375.0 1150.0,375.0" stroke="blue" stroke-width="5"/>
</svg>
""")
        
    def test_06(self):
        """TestSVGlWriter.test_06(): a polygon.
        Based on http://www.w3.org/TR/2003/REC-SVG11-20030114/shapes.html#PolygonElement"""
        myF = io.StringIO()
        myViewPort = Coord.Box(
            Coord.Dim(12, 'cm'),
            Coord.Dim(4, 'cm'),
        )
        with SVGWriter.SVGWriter(myF, myViewPort, {'viewBox' : "0 0 1200 400"}) as xS:
            with XmlWrite.Element(xS, 'desc'):
                xS.characters('Example line01 - lines expressed in user coordinates')
            #xS.comment(" Show outline of canvas using 'rect' element ")
            myPt = Coord.Pt(Coord.baseUnitsDim(1), Coord.baseUnitsDim(1))
            myBx = Coord.Box(Coord.baseUnitsDim(1198), Coord.baseUnitsDim(398))
            with SVGWriter.SVGRect(xS, myPt, myBx, {'fill':"none", 'stroke':"blue",'stroke-width':"2"}):
                pass
            # Make a group
            with SVGWriter.SVGPolygon(
                    xS,
                    [
                        Coord.Pt(Coord.baseUnitsDim(350), Coord.baseUnitsDim(75)),
                        Coord.Pt(Coord.baseUnitsDim(379), Coord.baseUnitsDim(161)),
                        Coord.Pt(Coord.baseUnitsDim(469), Coord.baseUnitsDim(161)),
                        Coord.Pt(Coord.baseUnitsDim(397), Coord.baseUnitsDim(215)),
                        Coord.Pt(Coord.baseUnitsDim(423), Coord.baseUnitsDim(301)),
                        Coord.Pt(Coord.baseUnitsDim(350), Coord.baseUnitsDim(250)),
                        Coord.Pt(Coord.baseUnitsDim(277), Coord.baseUnitsDim(301)),
                        Coord.Pt(Coord.baseUnitsDim(303), Coord.baseUnitsDim(215)),
                        Coord.Pt(Coord.baseUnitsDim(231), Coord.baseUnitsDim(161)),
                        Coord.Pt(Coord.baseUnitsDim(321), Coord.baseUnitsDim(161)),
                    ],
                    {'fill' : 'red', 'stroke' : 'blue', 'stroke-width' : "10"}
                ):
                pass
        # print()
        # print(myF.getvalue())
#        self.maxDiff = None
        self.assertEqual("""<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="4.000cm" version="1.1" viewBox="0 0 1200 400" width="12.000cm" xmlns="http://www.w3.org/2000/svg">
  <desc>Example line01 - lines expressed in user coordinates</desc>
  <rect fill="none" height="398.000px" stroke="blue" stroke-width="2" width="1198.000px" x="1.000px" y="1.000px"/>
  <polygon fill="red" points="350.0,75.0 379.0,161.0 469.0,161.0 397.0,215.0 423.0,301.0 350.0,250.0 277.0,301.0 303.0,215.0 231.0,161.0 321.0,161.0" stroke="blue" stroke-width="10"/>
</svg>
""",
        myF.getvalue())

    def test_07(self):
        """TestSVGlWriter.test_07(): text.
        Based on http://www.w3.org/TR/2003/REC-SVG11-20030114/text.html#TextElement"""
        myF = io.StringIO()
        myViewPort = Coord.Box(
            Coord.Dim(12, 'cm'),
            Coord.Dim(4, 'cm'),
        )
        with SVGWriter.SVGWriter(myF, myViewPort, {'viewBox' : "0 0 1000 300"}) as xS:
            with XmlWrite.Element(xS, 'desc'):
                xS.characters("Example text01 - 'Hello, out there' in blue")
            myPt = Coord.Pt(Coord.baseUnitsDim(250), Coord.baseUnitsDim(150))
            with SVGWriter.SVGText(xS, myPt, "Verdans", 55, {'fill' : "blue"}):
                xS.characters('Hello, out there')
            #xS.comment(" Show outline of canvas using 'rect' element ")
            myPt = Coord.Pt(Coord.baseUnitsDim(1), Coord.baseUnitsDim(1))
            myBx = Coord.Box(Coord.baseUnitsDim(998), Coord.baseUnitsDim(298))
            with SVGWriter.SVGRect(xS, myPt, myBx, {'fill':"none", 'stroke':"blue",'stroke-width':"2"}):
                pass
        # print()
        # print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="4.000cm" version="1.1" viewBox="0 0 1000 300" width="12.000cm" xmlns="http://www.w3.org/2000/svg">
  <desc>Example text01 - &apos;Hello, out there&apos; in blue</desc>
  <text fill="blue" font-family="Verdans" font-size="55" x="250.000px" y="150.000px">Hello, out there</text>
  <rect fill="none" height="298.000px" stroke="blue" stroke-width="2" width="998.000px" x="1.000px" y="1.000px"/>
</svg>
""")

class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSVGWriter))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestSVGWriter.py - A module that tests StrTree module.
Usage:
python TestSVGWriter.py [-lh --help]

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
    print('TestSVGWriter.py script version "%s", dated %s' % (__version__, __date__))
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
    clkStart = time.perf_counter()
    unitTest()
    clkExec = time.perf_counter() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')

if __name__ == "__main__":
    main()
