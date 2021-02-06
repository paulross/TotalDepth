#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation.
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
"""
Created on 10 Nov 2010

@author: p2ross
"""
import logging
import sys
import time
import typing

from TotalDepth.LIS import lis_cmn_cmd_opts
from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import LogiRec
from TotalDepth.common import cmn_cmd_opts


__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2010-2020 Paul Ross'


def dump_table(logical_record: LogiRec.LrTable, theS=sys.stdout):
    theS.write(
        f'        Logical record type: {logical_record.type:3d} (0x{logical_record.type:02x})'
        f' Table name: {logical_record.value}\n'
    )
    for aRow in logical_record.genRows():
        for aCbev in aRow.genCells():
            theS.write('\t{!s}'.format(aCbev.value))
        theS.write('\n')


def dump_dfsr(logical_record: LogiRec.LrDFSR, theS=sys.stdout):
    theS.write('{:3s} {:7s} {:9s} {:11s} {:7s} {:11s} {:4s} {:4s} {:4s} {:4s} {:4s}'.format(
            '', 'Name', 'SrvID', 'SrvOrd', 'UoM', 'API Codes', 'Size', 'Samp', 'RC', 'Brst', 'SubC'
        )
    )
    theS.write('\n')
    for i, d in enumerate(logical_record.dsbBlocks):
        theS.write('%3d %s %s %s %s %2d-%2s-%2d-%1d %4d %4d %4d %4d %4d' % \
            (
                i,
                d.mnem,
                d.servId,
                d.servOrd,
                d.units,
                d.apiLogType,
                d.apiCurveType,
                d.apiCurveClass,
                d.apiModifier,
                d.size,
                d.samples(0),
                d.repCode,
                d.bursts(0),
                d.subChannels,
            )
        )
        theS.write('\n')


def dump_logical_record_attributes(logical_record: LogiRec.LrBase, theS=sys.stdout) -> None:
    table: typing.List[typing.Tuple[str, str]] = []
    for field in sorted(dir(logical_record)):
        if not field.startswith('_'):
            if not callable(getattr(logical_record, field)):
                table.append((field, str(getattr(logical_record, field))))
    for field, value in table:
        theS.write(f'        {field:20} -> {value}\n')


def dump_logical_record(logical_record: LogiRec.LrBase, theS=sys.stdout):
    DUMP_MAP = {
        LogiRec.LR_TYPE_JOB_ID      : dump_table,
        LogiRec.LR_TYPE_WELL_DATA   : dump_table,
        LogiRec.LR_TYPE_TOOL_INFO   : dump_table,
        LogiRec.LR_TYPE_DATA_FORMAT : dump_dfsr,
        LogiRec.LR_TYPE_REEL_HEAD   : dump_logical_record_attributes,
        LogiRec.LR_TYPE_REEL_TAIL   : dump_logical_record_attributes,
        LogiRec.LR_TYPE_TAPE_HEAD   : dump_logical_record_attributes,
        LogiRec.LR_TYPE_TAPE_TAIL   : dump_logical_record_attributes,
        LogiRec.LR_TYPE_FILE_HEAD   : dump_logical_record_attributes,
        LogiRec.LR_TYPE_FILE_TAIL   : dump_logical_record_attributes,
    }
    try:
        DUMP_MAP[logical_record.type](logical_record, theS)
    except KeyError:
        # Dump the bytes if not and encrypted table (42).
        if hasattr(logical_record, 'bytes') and logical_record.type not in (42,):
            theS.write(f'Raw bytes [{len(logical_record.bytes)}]: {repr(logical_record.bytes[:40])} ...\n')


def scan_file(fp, verbose, keepGoing, pad_modulo, pad_non_null, theS=sys.stdout):
    try:
        myFile = File.FileRead(fp, fp, keepGoing, pad_modulo, pad_non_null)
    except File.ExceptionFile as err:
        logging.exception('Can not open file, error: %s' % str(err))
        return
    myFactory = LogiRec.LrFactoryRead()
    while not myFile.isEOF:
        lr_tell = myFile.tellLr()
        try:
            logical_record = myFactory.retLrFromFile(myFile)
            if logical_record is not None:
                theS.write(f'0x{lr_tell:08x} {logical_record}\n')
                if verbose:
                    dump_logical_record(logical_record)
        except LogiRec.ExceptionLr as err:
            logging.error('LR at 0x{:08x}: {:s}'.format(lr_tell, err))
        myFile.skipToNextLr()


def main():
    usage = """usage: %prog [options] file
Scans a LIS79 file and dumps Logical Records."""
    print('Cmd: %s' % ' '.join(sys.argv))
    arg_parser = cmn_cmd_opts.path_in(usage, prog='TotalDepth.LIS.ScanPhysRec', version='%(prog)s ' + __version__)
    lis_cmn_cmd_opts.add_physical_record_padding_options(arg_parser)
    cmn_cmd_opts.add_log_level(arg_parser, level=20)
    args = arg_parser.parse_args()
    print(args)
    cmn_cmd_opts.set_log_level(args)
    clk_start = time.perf_counter()
    # Your code here
    scan_file(args.path_in, args.verbose, args.keepGoing, args.pad_modulo, args.pad_non_null)
    clk_exec = time.perf_counter() - clk_start
    print('CPU time = %8.3f (S)' % clk_exec)
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    sys.exit(main())
