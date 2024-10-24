#!/usr/bin/env python
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 2011-2021 Paul Ross
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

"""Treats XmlWrite."""

import os
import sys
import time
import logging
import io

from TotalDepth.util import XmlWrite

######################
# Section: Unit tests.
######################
import unittest

class TestXmlWrite(unittest.TestCase):
    """Tests XmlWrite."""
    def test_00(self):
        """TestXmlWrite.test_00(): construction."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF):
            pass
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>\n""")
        
    def test_01(self):
        """TestXmlWrite.test_01(): simple elements."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF) as xS:
            with XmlWrite.Element(xS, 'Root', {'version' : '12.0'}):
                with XmlWrite.Element(xS, 'A', {'attr_1' : '1'}):
                    pass
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<Root version="12.0">
  <A attr_1="1"/>
</Root>
""")
       
    def test_02(self):
        """TestXmlWrite.test_02(): mixed content."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF) as xS:
            with XmlWrite.Element(xS, 'Root', {'version' : '12.0'}):
                with XmlWrite.Element(xS, 'A', {'attr_1' : '1'}):
                    xS.characters('<&>')
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<Root version="12.0">
  <A attr_1="1">&lt;&amp;&gt;</A>
</Root>
""")
       
    def test_03(self):
        """TestXmlWrite.test_03(): processing instruction."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF) as xS:
            with XmlWrite.Element(xS, 'Root', {'version' : '12.0'}):
                with XmlWrite.Element(xS, 'A', {'attr_1' : '1'}):
                    xS.pI('Do <&> this')
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<Root version="12.0">
  <A attr_1="1"><?Do &lt;&amp;&gt; this?></A>
</Root>
""")
        
    def test_04(self):
        """TestXmlWrite.test_04(): raise on endElement when empty."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF) as xS:
            pass
        #print
        #print myF.getvalue()
        self.assertRaises(XmlWrite.ExceptionXmlEndElement, xS.endElement, '')
        
    def test_05(self):
        """TestXmlWrite.test_05(): raise on endElement missmatch."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF) as xS:
            with XmlWrite.Element(xS, 'Root', {'version' : '12.0'}):
                self.assertRaises(XmlWrite.ExceptionXmlEndElement, xS.endElement, 'NotRoot')
                with XmlWrite.Element(xS, 'A', {'attr_1' : '1'}):
                    self.assertRaises(XmlWrite.ExceptionXmlEndElement, xS.endElement, 'NotA')
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<Root version="12.0">
  <A attr_1="1"/>
</Root>
""")
                       
    def test_06(self):
        """TestXmlWrite.test_06(): encoded text in 'latin-1'."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF, 'latin-1') as xS:
            with XmlWrite.Element(xS, 'Root'):
                with XmlWrite.Element(xS, 'A'):
                    xS.characters("""<&>"'""")
                with XmlWrite.Element(xS, 'A'):
                    xS.characters('%s' % chr(147))
                with XmlWrite.Element(xS, 'A'):
                    xS.characters(chr(65))
                with XmlWrite.Element(xS, 'A'):
                    xS.characters(chr(128))
        # print()
        # print(myF.getvalue())
        self.assertEqual("""<?xml version='1.0' encoding="latin-1"?>
<Root>
  <A>&lt;&amp;&gt;&quot;&apos;</A>
  <A>&#147;</A>
  <A>A</A>
  <A>&#128;</A>
</Root>
""",
            myF.getvalue(),
        )
       
    def test_07(self):
        """TestXmlWrite.test_07(): comments."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF) as xS:
            with XmlWrite.Element(xS, 'Root', {'version' : '12.0'}):
                xS.comment(' a comment ')
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<Root version="12.0"><!-- a comment -->
</Root>
""")
       
    def test_08(self):
        """TestXmlWrite.test_08(): raise during write."""
        myF = io.StringIO()
        try:
            with XmlWrite.XmlStream(myF) as xS:
                with XmlWrite.Element(xS, 'Root', {'version' : '12.0'}):
                    self.assertRaises(XmlWrite.ExceptionXmlEndElement, xS.endElement, 'NotRoot')
                    with XmlWrite.Element(xS, 'E', {'attr_1' : '1'}):
                        xS._elemStk.pop()
                        xS._elemStk.append('F')
                        raise Exception('Some exception')
        except Exception as e:
            print(e)
        else:
            print('No exception raised')
#        print()
#        print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<Root version="12.0">
  <E attr_1="1"/>
</Root>
""")
                       


class TestXhtmlWrite(unittest.TestCase):
    """Tests TestXhtmlWrite."""
    def test_00(self):
        """TestXhtmlWrite.test_00(): construction."""
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF):
            pass
#        print()
#        print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml"/>
""")
        
    def test_01(self):
        """TestXhtmlWrite.test_01(): simple example."""
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as xS:
            with XmlWrite.Element(xS, 'head'):
                with XmlWrite.Element(xS, 'title'):
                    xS.characters('Virtual Library')
            with XmlWrite.Element(xS, 'body'):
                with XmlWrite.Element(xS, 'p'):
                    xS.characters('Moved to ')
                    with XmlWrite.Element(xS, 'a', {'href' : 'http://example.org/'}):
                        xS.characters('example.org')
                    xS.characters('.')
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>Virtual Library</title>
  </head>
  <body>
    <p>Moved to <a href="http://example.org/">example.org</a>.</p>
  </body>
</html>
""")
        
    def test_charactersWithBr_00(self):
        """TestXhtmlWrite.test_00(): simple example."""
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as xS:
            with XmlWrite.Element(xS, 'head'):
                pass
            with XmlWrite.Element(xS, 'body'):
                with XmlWrite.Element(xS, 'p'):
                    xS.charactersWithBr('No break in this line.')
                with XmlWrite.Element(xS, 'p'):
                    xS.charactersWithBr("""Several
breaks in
this line.""")           
                with XmlWrite.Element(xS, 'p'):
                    xS.charactersWithBr('\nBreak at beginning.')
                with XmlWrite.Element(xS, 'p'):
                    xS.charactersWithBr('Break at end\n')
                with XmlWrite.Element(xS, 'p'):
                    xS.charactersWithBr('\nBreak at beginning\nmiddle and end\n')
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head/>
  <body>
    <p>No break in this line.</p>
    <p>Several<br/>breaks in<br/>this line.</p>
    <p><br/>Break at beginning.</p>
    <p>Break at end<br/></p>
    <p><br/>Break at beginning<br/>middle and end<br/></p>
  </body>
</html>
""")

    def test_all_byte_values(self):
        fout = io.StringIO()
        with XmlWrite.XhtmlStream(fout) as xS:
            with XmlWrite.Element(xS, 'Root', {'version': '12.0'}):
                s = ''.join(chr(v) for v in range(256))
                xS.characters(s)
        result = fout.getvalue()
        self.assertEqual(result, r"""<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <Root version="12.0">&#000;&#001;&#002;&#003;&#004;&#005;&#006;&#007;&#008;&#009;&#010;&#011;&#012;&#013;&#014;&#015;&#016;&#017;&#018;&#019;&#020;&#021;&#022;&#023;&#024;&#025;&#026;&#027;&#028;&#029;&#030;&#031; !&quot;#$%&amp;&apos;()*+,-./0123456789:;&lt;=&gt;?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~&#128;&#129;&#130;&#131;&#132;&#133;&#134;&#135;&#136;&#137;&#138;&#139;&#140;&#141;&#142;&#143;&#144;&#145;&#146;&#147;&#148;&#149;&#150;&#151;&#152;&#153;&#154;&#155;&#156;&#157;&#158;&#159;&#160;&#161;&#162;&#163;&#164;&#165;&#166;&#167;&#168;&#169;&#170;&#171;&#172;&#173;&#174;&#175;&#176;&#177;&#178;&#179;&#180;&#181;&#182;&#183;&#184;&#185;&#186;&#187;&#188;&#189;&#190;&#191;&#192;&#193;&#194;&#195;&#196;&#197;&#198;&#199;&#200;&#201;&#202;&#203;&#204;&#205;&#206;&#207;&#208;&#209;&#210;&#211;&#212;&#213;&#214;&#215;&#216;&#217;&#218;&#219;&#220;&#221;&#222;&#223;&#224;&#225;&#226;&#227;&#228;&#229;&#230;&#231;&#232;&#233;&#234;&#235;&#236;&#237;&#238;&#239;&#240;&#241;&#242;&#243;&#244;&#245;&#246;&#247;&#248;&#249;&#250;&#251;&#252;&#253;&#254;&#255;</Root>
</html>
""")


class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestXmlWrite))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestXhtmlWrite))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestXmlWrite.py - A module that tests StrTree module.
Usage:
python TestXmlWrite.py [-lh --help]

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
    print('TestXmlWrite.py script version "%s", dated %s' % (__version__, __date__))
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
