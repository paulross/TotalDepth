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
"""Tests the cmn_cmd_opts (Common Command Line Options) module.

Created on Feb 13, 2012

@author: paulross
"""

import pytest

from TotalDepth.common import cmn_cmd_opts


@pytest.mark.parametrize(
    'args',
    (['-h',], ['--help',], ['--version',])
)
def test_basic(args):
    parser = cmn_cmd_opts.arg_parser("Description of the program", "Name of the program", "0.1.3rc4")
    with pytest.raises(SystemExit) as err:
        parser.parse_args(args)
    assert err.value.args == (0,)

# def test_03(self):
#     """TestCmnCmdOpts.test_03(): use of --help."""
#     myP = cmn_cmd_opts.arg_parser("Description of the program", "Name of the program", "0.1.3rc4")
#     try:
#         print()
#         myNs = myP.parse_args(['--help',])
#         self.fail('SystemExit not raised: %s' % myNs)
#     except SystemExit:
#         pass
#
# def test_04(self):
#     """TestCmnCmdOpts.test_04(): use of -h with minimal parser creation."""
#     myP = cmn_cmd_opts.arg_parser("Description of the program only, no program name, no version")
#     try:
#         print()
#         myNs = myP.parse_args(['-h',])
#         self.fail('SystemExit not raised: %s' % myNs)
#     except SystemExit:
#         pass
#
# def test_05(self):
#     """TestCmnCmdOpts.test_05(): use of --version."""
#     myP = cmn_cmd_opts.arg_parser("Description of the program", "PROG", version="v0.1.3rc4")
#     try:
#         print()
#         myNs = myP.parse_args(['--version',])
#         self.fail('SystemExit not raised: %s' % myNs)
#     except SystemExit:
#         pass
#
# def test_06(self):
#     """TestCmnCmdOpts.test_06(): use of --version and prog=None."""
#     myP = cmn_cmd_opts.arg_parser("Description of the program", None, version="v0.1.3rc4")
#     try:
#         print()
#         myNs = myP.parse_args(['--version',])
#         self.fail('SystemExit not raised: %s' % myNs)
#     except SystemExit:
#         pass
#
# def test_07(self):
#     """TestCmnCmdOpts.test_06(): use of --version minimal parser creation should fail with unrecognised arguments."""
#     myP = cmn_cmd_opts.arg_parser("Description of the program only, no program name, no version")
#     try:
#         print()
#         myNs = myP.parse_args(['--version',])
#         self.fail('SystemExit not raised: %s' % myNs)
#     except SystemExit:
#         pass
#
# def test_10(self):
#     """TestCmnCmdOpts.test_10(): use of CmnCmdOpts.arg_parser() and adding a list option."""
#     myP = cmn_cmd_opts.arg_parser("Description", "Program", "Version")
#     myP.add_argument(
#         "-I", "--INCLUDE",
#         action="append",
#         dest="includes",
#         default=[],
#         help="Include paths (additive). [default: %default]",
#     )
#     myNs = myP.parse_args([])
#     self.assertEqual([], myNs.includes)
#     myNs = myP.parse_args(['-I', '123', '--INCLUDE', '4'])
#     self.assertEqual(['123', '4',], myNs.includes)
#
# def test_11(self):
#     """TestCmnCmdOpts.test_11(): use of CmnCmdOpts.arg_parser() and adding a enumerated option with choices."""
#     myP = cmn_cmd_opts.arg_parser("Description", "Program", "Version")
#     myP.add_argument(
#         "-f", "--file-type",
#         choices=['LAS', 'LIS', 'AUTO'],
#     )
#     myNs = myP.parse_args([])
#     self.assertTrue(myNs.file_type is None)
#     myNs = myP.parse_args('-f LIS'.split())
#     self.assertEqual('LIS', myNs.file_type)
#     try:
#         print()
#         myNs = myP.parse_args('-f WTF'.split())
#         self.fail('SystemExit not raised.')
#     except SystemExit:
#         pass
#
# def test_12(self):
#     """TestCmnCmdOpts.test_12(): use of CmnCmdOpts.arg_parser() and adding scale option as a list of integers."""
#     myP = cmn_cmd_opts.arg_parser("Description", "Program", "Version")
#     myP.add_argument("-s", "--scale", action="append", type=int, dest="scales", default=[],
#             help="Scale of X axis to use (additive). [default: []].")
#     myNs = myP.parse_args([])
#     self.assertEqual([], myNs.scales)
#     myNs = myP.parse_args('-s 47'.split())
#     self.assertEqual([47,], myNs.scales)
#     myNs = myP.parse_args('-s 47 --scale=49'.split())
#     self.assertEqual([47, 49], myNs.scales)
#     try:
#         print()
#         myNs = myP.parse_args('-s WTF'.split())
#         self.fail('SystemExit not raised.')
#     except SystemExit:
#         pass
#
# def test_20(self):
#     """TestCmnCmdOpts.test_12(): basic use of CmnCmdOpts.path_in()."""
#     myP = cmn_cmd_opts.path_in("Description", "Program", "Version")
#     myNs = myP.parse_args(['IN',])
#     self.assertEqual('IN', myNs.pathIn)
#     self.assertFalse(myNs.recursive)
#     self.assertTrue(myNs.glob is None)
#
# def test_22(self):
#     """TestCmnCmdOpts.test_22(): basic use of CmnCmdOpts.path_in_out()."""
#     myP = cmn_cmd_opts.path_in_out("Description", "Program", "Version")
#     myNs = myP.parse_args(['IN', 'OUT'])
#     self.assertEqual('IN', myNs.pathIn)
#     self.assertEqual('OUT', myNs.pathOut)
#
# def test_23(self):
#     """TestCmnCmdOpts.test_23(): basic use of CmnCmdOpts.path_in_out() with -h option."""
#     myP = cmn_cmd_opts.path_in_out("Description", "Program", "Version")
#     myNs = myP.parse_args(['IN', 'OUT'])
#     self.assertEqual('IN', myNs.pathIn)
#     self.assertEqual('OUT', myNs.pathOut)
#     try:
#         print()
#         myNs = myP.parse_args(['-h',])
#         self.fail('SystemExit not raised: %s' % myNs)
#     except SystemExit:
#         pass
#
# def test_24(self):
#     """TestCmnCmdOpts.test_24(): basic use of CmnCmdOpts.path_in_out() format_usage() and format_help()."""
#     myP = cmn_cmd_opts.path_in_out("Description", "Program", "Version")
#     myNs = myP.parse_args(['IN', 'OUT'])
#     self.assertEqual('IN', myNs.pathIn)
#     self.assertEqual('OUT', myNs.pathOut)
#     # print('XXX')
#     # print(dir(myP))
#     # print(dir(myNs))
#     # print(myNs._get_args())
#     # print(myNs._get_kwargs())
#     # print(myP.format_usage())
#     # print(myP.format_help())
#     self.assertEqual("""usage: Program [-h] [--version] [-j JOBS] [-k] [-l LOG_LEVEL] [-g] [-r] in out
# """, myP.format_usage())
