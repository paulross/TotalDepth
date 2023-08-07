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
'''
Created on Aug 03, 2023

@author: paulross
'''
import logging
import os
import pprint
import sys
import time
import traceback
import typing as typing

import TotalDepth
from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS import ProcLISPath
from TotalDepth.LIS.core import LogiRec, LogPass
from TotalDepth.LIS.core import LatLong
from TotalDepth.LIS.core import Mnem
from TotalDepth.common import xxd
from TotalDepth.util import bin_file_type

__author__ = 'Paul Ross'
__date__ = 'Aug 03, 2023'
__version__ = '0.1.0'
__rights__ = 'Copyright (c) Paul Ross'

logger = logging.getLogger(__file__)


class FileInfo(typing.NamedTuple):
    pathIn: str
    lisSize: int
    numLr: int
    cpuTime: float
    exception: bool
    locations: typing.List[typing.List[typing.List[typing.Tuple[bytes, str]]]]

    def __str__(self):
        return 'FileInfo: "%s" %d (kb) LR count=%d t=%.3f' \
            % (self.pathIn, self.lisSize / 1024, self.numLr, self.cpuTime)


class IndexSummary(object):

    def __init__(self, f=0, b=0):
        # List of FileInfo objects
        self.file_results: typing.List[FileInfo] = []

    def __str__(self):
        return '\n'.join([str(f) for f in self.file_results])

    def __iadd__(self, other):
        self.file_results += other.file_results
        return self

    def __len__(self):
        return len(self.file_results)

    def add(self, fpIn, numLr, cpuTime, exception, locations: typing.List[typing.List[typing.List[typing.Tuple[bytes, str]]]]):
        self.file_results.append(FileInfo(fpIn, os.path.getsize(fpIn), numLr, cpuTime, exception, locations))

    @property
    def lisSize(self):
        return sum([fi.lisSize for fi in self.file_results])

    @property
    def numLr(self):
        return sum([fi.numLr for fi in self.file_results])

    @property
    def cpuTime(self):
        return sum([fi.cpuTime for fi in self.file_results])


class LatLongCheck(ProcLISPath.ProcLISPathBase):
    """Takes an input path, output path and generates HTML file(s) form LIS."""
    CSS_FILE_PATH = 'TotalDepth.LIS.css'

    def __init__(self, fpIn, recursive, keepGoing):
        """Analyse location data for a LIS file."""
        self.summary = IndexSummary()
        # Despatch table for LR type
        # self._despatchLrType = {
        #     LogiRec.LR_TYPE_WELL_DATA: self._HTMLTable,
        # }
        super().__init__(fpIn, '', recursive, keepGoing)

    # def _HTMLTable(self, theIe, theFi, theS):
    #     self._HTMLEntryBasic(theIe, theS)
    #     if theIe.logicalRecord is None:
    #         theIe.setLogicalRecord(theFi)
    #     myLr = theIe.logicalRecord
    #     assert (myLr is not None)
    #     if myLr.tableCbEv is not None:
    #         # Write the table name and so on from tableCbEv
    #         with XmlWrite.Element(theS, 'h4', {'class': 'wsd'}):
    #             theS.characters('Well site data table: {:s}'.format(myLr.tableCbEv.engVal.pStr()))
    #             # theS.characters('Table: {:s}'.format(str(myLr.tableCbEv.engVal)))
    #     with XmlWrite.Element(theS, 'table', {'class': 'wsd'}):
    #         if myLr.isSingleParam:
    #             with XmlWrite.Element(theS, 'tr', {}):
    #                 with XmlWrite.Element(theS, 'th', {'class': 'wsd'}):
    #                     theS.characters('MNEM')
    #                 with XmlWrite.Element(theS, 'th', {'class': 'wsd'}):
    #                     theS.characters('VALUE')
    #             for aRow in myLr.genRows():
    #                 if len(aRow) == 1:
    #                     with XmlWrite.Element(theS, 'tr', {}):
    #                         with XmlWrite.Element(theS, 'td', {'class': 'wsd'}):
    #                             theS.characters(aRow[0].mnem.decode('ascii'))
    #                         with XmlWrite.Element(theS, 'td', {'class': 'wsd'}):
    #                             theS.characters(aRow[0].engVal.pStr())
    #                 else:
    #                     logger.warning('Single Parameter Information Record has row length {:d}'.format(len(aRow)))
    #         else:
    #             with XmlWrite.Element(theS, 'tr', {}):
    #                 for aMnem in myLr.colLabels():
    #                     with XmlWrite.Element(theS, 'th', {'class': 'wsd'}):
    #                         theS.characters(aMnem.decode('ascii'))
    #             for aRowName in myLr.genRowNames(sort=1):
    #                 with XmlWrite.Element(theS, 'tr', {}):
    #                     for aCell in myLr.genRowValuesInColOrder(aRowName):
    #                         if aCell is None:
    #                             with XmlWrite.Element(theS, 'td', {'class': 'wsdNone'}):
    #                                 theS.characters('N/A')
    #                         elif aCell.engVal is None:
    #                             # TODO: This is slightly suspicious, it seems to happen with
    #                             # the last cell in the table where there is no EngVal.
    #                             with XmlWrite.Element(theS, 'td', {'class': 'wsdNone'}):
    #                                 theS.characters('No value')
    #                         else:
    #                             with XmlWrite.Element(theS, 'td', {'class': 'wsd'}):
    #                                 theS.characters('{:s}'.format(aCell.engVal.pStr()))
    #     self._HTMLLinkToTop(theS)
    #
    # def _HTMLKeyValTable(self, theS, theKv, fieldTitle='Field'):
    #     with XmlWrite.Element(theS, 'table', {'class': "monospace"}):
    #         with XmlWrite.Element(theS, 'tr', {}):
    #             with XmlWrite.Element(theS, 'th', {'class': "monospace"}):
    #                 theS.characters(fieldTitle)
    #             with XmlWrite.Element(theS, 'th', {'class': "monospace"}):
    #                 theS.characters('Value')
    #         for k, v in theKv:
    #             with XmlWrite.Element(theS, 'tr', {}):
    #                 with XmlWrite.Element(theS, 'td', {'class': "monospace"}):
    #                     theS.characters(k)
    #                 with XmlWrite.Element(theS, 'td', {'class': "monospace"}):
    #                     theS.characters(v)
    #
    # def _HTMLGeneralTable(self, theS, theTitleS, theTab):
    #     """Create a table. theTitleS is a list of titles, theTab is a list of lists."""
    #     with XmlWrite.Element(theS, 'table', {'class': "monospace"}):
    #         with XmlWrite.Element(theS, 'tr', {}):
    #             for v in theTitleS:
    #                 with XmlWrite.Element(theS, 'th', {'class': "monospace"}):
    #                     theS.characters(v)
    #         for row in theTab:
    #             with XmlWrite.Element(theS, 'tr', {}):
    #                 for v in row:
    #                     with XmlWrite.Element(theS, 'td', {'class': "monospace"}):
    #                         theS.characters(v)

    def processFile(self, file_path_in, file_path_out):
        assert os.path.isfile(file_path_in)
        assert file_path_out == ''
        clk_start = time.perf_counter()
        try:
            lis_file, lis_index = self._retLisFileAndIndex(file_path_in)
        except ExceptionTotalDepthLIS as err:
            # logger.error('Can not create file and index: {!r:s}'.format(err))
            logger.exception('Can not create file and index from {}'.format(file_path_in))
            self.summary.add(file_path_in, 0, time.perf_counter() - clk_start, True, [])
            return
        numEntries = 0
        all_locations = []
        log_pass_values = []
        for index_entry in lis_index.genAll():
            # print(f'TRACE: index_entry {index_entry}')
            if index_entry.lrType == LogiRec.LR_TYPE_WELL_DATA and index_entry.name == b'CONS':
                values = []
                # TODO: Process CONS table for Lat/Long and other positional information.
                # print(index_entry)
                if index_entry.logicalRecord is None:
                    index_entry.setLogicalRecord(lis_file)
                logical_record: LogiRec.LrTable = index_entry.logicalRecord
                # for row_name in logical_record.genRowNames(sort=1):
                #     if row_name in {b'LATI', b'LONG'}:
                #         print(f'{row_name}:')
                #         for cell in logical_record.genRowValuesInColOrder(row_name):
                #             print(cell, end='')
                #         print()
                has_value = False
                for row_name in (b'NATI', b'FN  ', b'WN  ', b'LATI', b'LONG',):
                    try:
                        try:
                            row = logical_record[row_name]
                        except KeyError:
                            row = logical_record[row_name.replace(b' ', b'\x00')]
                        value = row[b'VALU'].value.decode('ascii')
                        values.append((row_name, value))
                        has_value = True
                    except KeyError:
                        values.append((row_name, ''))
                # print(values)
                if has_value:
                    log_pass_values.append(values)
            if isinstance(index_entry, LogPass.LogPass):
                # Pass the log_pass_values to all_locations
                all_locations.append(log_pass_values)
                log_pass_values = []
            numEntries += 1
        # Update the counter
        if len(log_pass_values):
            all_locations.append(log_pass_values)
            log_pass_values = []
        self.summary.add(file_path_in, numEntries, time.perf_counter() - clk_start, False, all_locations)


def process_file(file_path_in, file_path_out, keep_going) -> IndexSummary:
    """Used by the multiprocessing code."""
    assert file_path_out == ''
    file_type = bin_file_type.binary_file_type_from_path(file_path_in)
    logger.info(f'processFile(): File type: "{file_type}" {file_path_in}')
    if bin_file_type.is_lis_file_type(file_type):
        try:
            lat_long_check = LatLongCheck(file_path_in, recursive=False, keepGoing=keep_going)
        except ExceptionTotalDepthLIS as err:
            logger.error('LatLongCheck.processFile({:s}): {:s}'.format(file_path_in, str(err)))
            logger.error(traceback.format_exc())
        except Exception as err:
            if keep_going:
                # Log it, return None
                logger.critical('LatLongCheck.processFile({:s}): {:s}'.format(file_path_in, str(err)))
                logger.critical(traceback.format_exc())
            else:
                # Raise it
                raise
        else:
            return lat_long_check.summary


def main():
    description = """usage: %prog [options] in
Scans LIS file or directory for positional information such as Latitude and Longitude."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = TotalDepth.common.cmn_cmd_opts.path_in(
        description, prog='TotalDepth.LIS.LisToHTML.main', version=__version__, epilog=__rights__
    )
    TotalDepth.common.cmn_cmd_opts.add_log_level(parser, level=20)
    TotalDepth.common.cmn_cmd_opts.add_multiprocessing(parser)
    TotalDepth.common.process.add_process_logger_to_argument_parser(parser)
    parser.add_argument("-g", "--glob", action="store_true", dest="glob", default=None,
                        help="File match pattern. Default: %(default)s.")
    args = parser.parse_args()
    # print(args)
    TotalDepth.common.cmn_cmd_opts.set_log_level(args)

    clkStart = time.perf_counter()
    timStart = time.time()
    # Your code here
    if TotalDepth.common.cmn_cmd_opts.multiprocessing_requested(args):
        myResult = ProcLISPath.procLISPathMP(
            args.path_in,
            '',
            args.glob,
            args.recurse,
            args.keepGoing,
            TotalDepth.common.cmn_cmd_opts.number_multiprocessing_jobs(args),
            process_file,
            resultObj=IndexSummary(),
        )
        # Write index.html
        myResult.writeIndexHTML(args.path_out)
    else:
        if os.path.isdir(args.path_in):
            myResult = ProcLISPath.procLISPathSP(
                args.path_in,
                '',
                args.glob,
                args.recurse,
                args.keepGoing,
                process_file,
                resultObj=IndexSummary(),
            )
        else:
            myLth = LatLongCheck(args.path_in, args.recurse, args.keepGoing)
            myResult = myLth.summary
    print('LatLongCheck results:')
    print(
        f'{"LIS_Size":>16}'
        f' {"Num_LRs":>8}'
        f' {"CPU_s":>12}'
        f' {"ms/Mb":>12}'
        f' {"Fail?":>5}'
        f' {"Path"}'
        f' {"Values"}'
    )
    total_lis_size = 0
    total_cpu_time = 0.0
    files_exception = 0
    for file_info in myResult.file_results:
        if file_info.lisSize:
            ms_mb = (file_info.cpuTime * 1000) / (file_info.lisSize / 1024 ** 2)
        else:
            ms_mb = 0.0
        print(
            f'{file_info.lisSize:16d}'
            f' {file_info.numLr:8d}'
            f' {file_info.cpuTime:12.3f}'
            f' {ms_mb:12.3f}'
            f' {file_info.exception!r:5}'
            f' {file_info.pathIn}'
        )
        # pprint.pprint(file_info.locations)
        if len(file_info.locations):
            for i, log_pass_locations in enumerate(file_info.locations):
                for j, locations in enumerate(log_pass_locations):
                    print(f'{j:4d} {locations}')
        total_lis_size += file_info.lisSize
        total_cpu_time += file_info.cpuTime
        if file_info.exception:
            files_exception += 1
    if total_lis_size:
        ms_mb = (total_cpu_time * 1000) / (total_lis_size / 1024 ** 2)
    else:
        ms_mb = 0.0
    print(
        f'Files processed {len(myResult.file_results)}'
        f' failed: {files_exception}'
        f' succeeded: {len(myResult.file_results) - files_exception}'
        f' total LIS size: {total_lis_size:,d}'
        f' total CPU time: {total_cpu_time:.3f} (s)'
        f' {ms_mb:.1f} (ms/Mb)'
    )
    print('  CPU time = %8.3f (S)' % (time.perf_counter() - clkStart))
    print('Exec. time = %8.3f (S)' % (time.time() - timStart))
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
