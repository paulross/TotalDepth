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
"""Unit tests for ...

Created on Jun 8, 2011

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = 'Jun 8, 2011'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2011 paulross.'

#import pprint
import sys
import os
import time
import logging
import io

from TotalDepth.util import HtmlUtils
from TotalDepth.util import XmlWrite

######################
# Section: Unit tests.
######################
import unittest

class Test_retHtmlFileName(unittest.TestCase):
    """Tests HtmlUtils.retHtmlFileName"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestName.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """Test_retHtmlFileName.test_01(): retHtmlFileName() - basic functionality."""
        # _5458a57e4dc446c657ecb558416c36b5
        self.assertEqual('_5458a57e4dc446c657ecb558416c36b5.html', HtmlUtils.retHtmlFileName(''))
        # 987d43c274104ccae9d86bd5aa7d80e0
        self.assertEqual('foo.lis_987d43c274104ccae9d86bd5aa7d80e0.html', HtmlUtils.retHtmlFileName('foo.lis'))
        myPathStr = 'a very long path that goes on and on and on and you think that it will never ever stop spam.lis'
        myPath = os.path.join(*myPathStr.split())
        self.assertEqual('a/very/long/path/that/goes/on/and/on/and/on/and/you/think/that/it/will/never/ever/stop/spam.lis', myPath)
        self.assertEqual(
            'spam.lis_87c42a1bc41f4b8579f088dce504d710.html',
            HtmlUtils.retHtmlFileName(myPath),
        )

    def test_02(self):
        """Test_retHtmlFileName.test_02(): retHtmlFileLink() - basic functionality."""
        self.assertEqual('_5458a57e4dc446c657ecb558416c36b5.html#4', HtmlUtils.retHtmlFileLink('', 4))
        self.assertEqual('foo.lis_987d43c274104ccae9d86bd5aa7d80e0.html#4', HtmlUtils.retHtmlFileLink('foo.lis', 4))
        myPathStr = 'a very long path that goes on and on and on and you think that it will never ever stop spam.lis'
        myPath = os.path.join(*myPathStr.split())
        self.assertEqual('a/very/long/path/that/goes/on/and/on/and/on/and/you/think/that/it/will/never/ever/stop/spam.lis', myPath)
        self.assertEqual(
            'spam.lis_87c42a1bc41f4b8579f088dce504d710.html#4',
            HtmlUtils.retHtmlFileLink(myPath, 4),
        )

class Test_XhtmlWrite(unittest.TestCase):
    """Tests TestXhtmlWrite."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestName.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestXhtmlWrite.test_01(): writeHtmlFileLink() simple."""
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeHtmlFileLink(myS, 'spam/eggs/chips.lis', 47, theText='Navigation text', theClass=None)
#        print()
#        print(myF.getvalue())
        self.assertEqual("""<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <a href="chips.lis_ca9b0f0a4f166e8fbd1ca3795e8adc76.html#47">Navigation text</a>
</html>
""",
            myF.getvalue(),
        )

    def test_02(self):
        """TestXhtmlWrite.test_02(): writeHtmlFileLink() with class."""
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeHtmlFileLink(myS, 'spam/eggs/chips.lis', 47, theText='Navigation text', theClass='CSS_class')
#        print()
#        print(myF.getvalue())
        self.assertEqual("""<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <a href="chips.lis_ca9b0f0a4f166e8fbd1ca3795e8adc76.html#47">
    <span class="CSS_class">Navigation text</span>
  </a>
</html>
""",
            myF.getvalue()
        )

    def test_03(self):
        """TestXhtmlWrite.test_03(): writeHtmlFileAnchor()."""
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeHtmlFileAnchor(myS, 47, theText='Navigation text')
#        print()
#        print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <a name="47">Navigation text</a>
</html>
""")
    def test_04(self):
        """TestXhtmlWrite.test_04(): writeHtmlFileAnchor() with class."""
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeHtmlFileAnchor(myS, 47, theText='Navigation text', theClass='CSS_class')
#        print()
#        print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <a name="47">
    <span class="CSS_class">Navigation text</span>
  </a>
</html>
""")

class Test_PathSplit(unittest.TestCase):
    """Tests TestXhtmlWrite."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """Test_PathSplit.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """Test_PathSplit.test_01(): pathSplit()"""
        self.assertEqual(['.'], HtmlUtils.pathSplit(''))
        self.assertEqual(['spam/', 'eggs.lis'], HtmlUtils.pathSplit('spam/eggs.lis'))
        self.assertEqual(['../', 'spam/', 'eggs.lis'], HtmlUtils.pathSplit('../spam/eggs.lis'))
        self.assertEqual(['../', 'eggs.lis'], HtmlUtils.pathSplit('../spam/../eggs.lis'))
        self.assertEqual(['../', 'chips/', 'eggs.lis'], HtmlUtils.pathSplit('../spam/../chips/eggs.lis'))

class Test_writeFileListAsTable(unittest.TestCase):
    """Tests TestXhtmlWrite."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """Test_writeFileListAsTable.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """Test_writeFileListAsTable.test_01(): writeFileListAsTable() - Single file list"""
        myFileNameS = [
            'eggs.lis',
            'chips.lis',
            'beans.lis',
        ]
        myFileLinkS = [(f, HtmlUtils.retHtmlFileName(f)) for f in myFileNameS]
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeFileListAsTable(myS, myFileLinkS, {}, False)
        # print()
        # print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table>
    <tr>
      <td>
        <a href="beans.lis_71bb0c26c74b06cd02a4f56f3e17667f.html">beans.lis</a>
      </td>
    </tr>
    <tr>
      <td>
        <a href="chips.lis_a11b6c9b0a5036efc32e9b30a09252fc.html">chips.lis</a>
      </td>
    </tr>
    <tr>
      <td>
        <a href="eggs.lis_97cf6bc2288e920398a47aee155da4a8.html">eggs.lis</a>
      </td>
    </tr>
  </table>
</html>
""")

    def test_02(self):
        """Test_writeFileListAsTable.test_02(): writeFileListAsTable() - Single directory list"""
        myFileNameS = [
            'spam/eggs.lis',
            'spam/chips.lis',
            'spam/beans.lis',
        ]
        myFileLinkS = [(f, HtmlUtils.retHtmlFileName(f)) for f in myFileNameS]
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeFileListAsTable(myS, myFileLinkS, {}, False)
        # print()
        # print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table>
    <tr>
      <td rowspan="3">spam/</td>
      <td>
        <a href="beans.lis_bd0fa0db0dba3d5deae8b324f475096e.html">beans.lis</a>
      </td>
    </tr>
    <tr>
      <td>
        <a href="chips.lis_8b5af66b7399116b669c1b12a95d7d33.html">chips.lis</a>
      </td>
    </tr>
    <tr>
      <td>
        <a href="eggs.lis_b6b735a7daac22b82ecd20fae6189ea5.html">eggs.lis</a>
      </td>
    </tr>
  </table>
</html>
""")

    def test_03(self):
        """Test_writeFileListAsTable.test_03(): writeFileListAsTable() - Multiple directory list"""
        myFileNameS = [
            'spam/eggs.lis',
            'spam/chips.lis',
            'spam/fishfingers/beans.lis',
            'spam/fishfingers/peas.lis',
        ]
        myFileLinkS = [(f, HtmlUtils.retHtmlFileName(f)) for f in myFileNameS]
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeFileListAsTable(myS, myFileLinkS, {}, False)
        # print()
        # print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table>
    <tr>
      <td rowspan="4">spam/</td>
      <td colspan="2">
        <a href="chips.lis_8b5af66b7399116b669c1b12a95d7d33.html">chips.lis</a>
      </td>
    </tr>
    <tr>
      <td colspan="2">
        <a href="eggs.lis_b6b735a7daac22b82ecd20fae6189ea5.html">eggs.lis</a>
      </td>
    </tr>
    <tr>
      <td rowspan="2">fishfingers/</td>
      <td>
        <a href="beans.lis_cc44d87fd7fc57302bb8f53e90981986.html">beans.lis</a>
      </td>
    </tr>
    <tr>
      <td>
        <a href="peas.lis_2cff29fa003c0ea829c7a7d877cae67c.html">peas.lis</a>
      </td>
    </tr>
  </table>
</html>
""")

    def test_04(self):
        """Test_writeFileListAsTable.test_0(): writeFileListAsTable() - Multiple directory list, includeKeyTail=True"""
        myFileNameS = [
            'spam/eggs.lis',
            'spam/chips.lis',
            'spam/fishfingers/beans.lis',
            'spam/fishfingers/peas.lis',
        ]
        myFileLinkS = [(f, HtmlUtils.retHtmlFileName(f)) for f in myFileNameS]
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeFileListAsTable(myS, myFileLinkS, {}, True)
        # print()
        # print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table>
    <tr>
      <td rowspan="4">spam/</td>
      <td colspan="2">chips.lis:<a href="chips.lis_8b5af66b7399116b669c1b12a95d7d33.html">chips.lis</a></td>
    </tr>
    <tr>
      <td colspan="2">eggs.lis:<a href="eggs.lis_b6b735a7daac22b82ecd20fae6189ea5.html">eggs.lis</a></td>
    </tr>
    <tr>
      <td rowspan="2">fishfingers/</td>
      <td>beans.lis:<a href="beans.lis_cc44d87fd7fc57302bb8f53e90981986.html">beans.lis</a></td>
    </tr>
    <tr>
      <td>peas.lis:<a href="peas.lis_2cff29fa003c0ea829c7a7d877cae67c.html">peas.lis</a></td>
    </tr>
  </table>
</html>
""")

class Test_writeFileListTrippleAsTable(unittest.TestCase):
    """Tests writeFileListTrippleAsTable()."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """Test_writeFileListTrippleAsTable.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """Test_writeFileListTrippleAsTable.test_01(): writeFileListTrippleAsTable() - Single file list"""
        myFileNameS = [
            '0eggs.lis',
            '1chips.lis',
            '2beans.lis',
        ]
        myFileLinkS = [(f, HtmlUtils.retHtmlFileName(f), 'Link text {:d}'.format(i)) for i, f in enumerate(myFileNameS)]
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeFileListTrippleAsTable(myS, myFileLinkS, {}, False)
        # print()
        # print(myF.getvalue())
#        print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table>
    <tr>
      <td> <a href="0eggs.lis_5fdd58d724c849dd9d217fbe6a35b3e6.html">Link text 0</a></td>
    </tr>
    <tr>
      <td> <a href="1chips.lis_3cdd79989f0c867f42464c2c02fa184f.html">Link text 1</a></td>
    </tr>
    <tr>
      <td> <a href="2beans.lis_999dc8fa0c627e259d489d8694205092.html">Link text 2</a></td>
    </tr>
  </table>
</html>
""")

    def test_02(self):
        """Test_writeFileListTrippleAsTable.test_02(): writeFileListTrippleAsTable() - Single directory list"""
        myFileNameS = [
            'spam/beans.lis',
            'spam/chips.lis',
            'spam/eggs.lis',
        ]
        myFileLinkS = [(f, HtmlUtils.retHtmlFileName(f), 'Link text {:d}'.format(i)) for i, f in enumerate(myFileNameS)]
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeFileListTrippleAsTable(myS, myFileLinkS, {}, False)
        # print()
        # print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table>
    <tr>
      <td rowspan="3">spam/</td>
      <td> <a href="beans.lis_bd0fa0db0dba3d5deae8b324f475096e.html">Link text 0</a></td>
    </tr>
    <tr>
      <td> <a href="chips.lis_8b5af66b7399116b669c1b12a95d7d33.html">Link text 1</a></td>
    </tr>
    <tr>
      <td> <a href="eggs.lis_b6b735a7daac22b82ecd20fae6189ea5.html">Link text 2</a></td>
    </tr>
  </table>
</html>
""")

    def test_03(self):
        """Test_writeFileListTrippleAsTable.test_03(): writeFileListTrippleAsTable() - Multiple directory list"""
        myFileNameS = [
            'spam/chips.lis',
            'spam/eggs.lis',
            'spam/fishfingers/beans.lis',
            'spam/fishfingers/peas.lis',
        ]
        myFileLinkS = [(f, HtmlUtils.retHtmlFileName(f), 'Link text {:d}'.format(i)) for i, f in enumerate(myFileNameS)]
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeFileListTrippleAsTable(myS, myFileLinkS, {}, False)
        # print()
        # print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table>
    <tr>
      <td rowspan="4">spam/</td>
      <td colspan="2"> <a href="chips.lis_8b5af66b7399116b669c1b12a95d7d33.html">Link text 0</a></td>
    </tr>
    <tr>
      <td colspan="2"> <a href="eggs.lis_b6b735a7daac22b82ecd20fae6189ea5.html">Link text 1</a></td>
    </tr>
    <tr>
      <td rowspan="2">fishfingers/</td>
      <td> <a href="beans.lis_cc44d87fd7fc57302bb8f53e90981986.html">Link text 2</a></td>
    </tr>
    <tr>
      <td> <a href="peas.lis_2cff29fa003c0ea829c7a7d877cae67c.html">Link text 3</a></td>
    </tr>
  </table>
</html>
""")

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Test_retHtmlFileName))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Test_XhtmlWrite))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Test_PathSplit))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Test_writeFileListAsTable))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Test_writeFileListTrippleAsTable))
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
    print(('TestClass.py script version "%s", dated %s' % (__version__, __date__)))
    print(('Author: %s' % __author__))
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
    print(('CPU time = %8.3f (S)' % clkExec))
    print('Bye, bye!')

if __name__ == "__main__":
    main()
