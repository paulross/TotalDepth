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
"""Indexes LIS files and reports performance.

Created on 24 Feb 2011

@author: p2ross

Indexing errors on LIS files:


[34] TotalDepth.LIS.core.TifMarker.ExceptionTifMarker: TIF read() expected 0x50, got tell: 0x4A, Shortfall: 0x6
Fixed.

[24] TotalDepth.LIS.core.LogiRec.ExceptionEntryBlock: EntryBlockSet.setEntryBlock(): type 10 excluded from EntryBlockSet
Fixed.

[ 2] TotalDepth.LIS.core.Type01Plan.ExceptionFrameSetPlan: Can not fit integer number of frames length 120 into LR length 824, modulo 104 [indirect size 0].
Two file have different problems:

13576.S1
--------
W:\openLIS\src\TotalDepth.LIS>python Index.py -rk -l40 ..\..\..\pLogicTestData\LIS\13576.S1
...
TotalDepth.LIS.core.Type01Plan.ExceptionFrameSetPlan: Can not fit integer number of frames length 120 into LR length 824, modulo 104 [indirect size 0].

Looks like the last PR is truncated:
...
TIF  True >:  0x       0  0x   19006  0x   197b6  PR: 0x   193de     972  0x9600     962  0x006c  0x0001  0xa2e1 0x00 0x00 [     962]
TIF  True >:  0x       0  0x   193de  0x   19b06  PR: 0x   197b6     836  0x9600     826  0x006d  0x0001  0x0304 0x00 0x00 [     826]
Missing 962-826 bytes 136 bytes.

13610.S1
--------
W:\openLIS\src\TotalDepth.LIS>python Index.py -rk -l40 ..\..\..\pLogicTestData\LIS\13610.S1
...
TotalDepth.LIS.core.Type01Plan.ExceptionFrameSetPlan: Can not fit integer number of frames length 7176 into LR length 13354, modulo 6178 [indirect size 0].

This looks like a bad PR header at 0x3a986 that has set a successor bit:
W:\openLIS\src\TotalDepth.LIS>python ScanPhysRec.py ..\..\..\pLogicTestData\LIS\13610.S1
Cmd: ScanPhysRec.py ..\..\..\pLogicTestData\LIS\13610.S1
TIF     ?  :        Type        Back        Next  PR:     tell()  Length    Attr  LD_len  RecNum  FilNum  ChkSum   LR Attr [Total LD]
TIF  True >:  0x       0  0x       0  0x      4a  PR: 0x       0      62  0x8000      58  ------  ------  ------ 0x80 0x00 [      58]
TIF  True >:  0x       0  0x       0  0x     3ac  PR: 0x      4a     854  0x8000     850  ------  ------  ------ 0x40 0x00 [     850]
...
TIF  True >:  0x       0  0x   390f4  0x   395ae  PR: 0x   394ec     182  0x8001     178  ------  ------  ------ 0x00 0x00
TIF  True >:  0x       0  0x   394ec  0x   399a6  PR: 0x   395ae    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   395ae  0x   39d9e  PR: 0x   399a6    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   399a6  0x   3a196  PR: 0x   39d9e    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   39d9e  0x   3a58e  PR: 0x   3a196    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3a196  0x   3a986  PR: 0x   3a58e    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3a58e  0x   3ad7e  PR: 0x   3a986    1004  0x8003    1000  ------  ------  ------ + ---- ----
2011-03-09 19:50:13,710 WARNING  Physical record at 0x3AD7E is successor but has no predecessor bit set.

TIF  True >:  0x       0  0x   3a986  0x   3ae40  PR: 0x   3ad7e     182  0x8001     178  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3ad7e  0x   3b238  PR: 0x   3ae40    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3ae40  0x   3b630  PR: 0x   3b238    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3b238  0x   3ba28  PR: 0x   3b630    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3b630  0x   3be20  PR: 0x   3ba28    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3ba28  0x   3c218  PR: 0x   3be20    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3be20  0x   3c610  PR: 0x   3c218    1004  0x8003    1000  ------  ------  ------ + ---- ----
TIF  True >:  0x       0  0x   3c218  0x   3ca08  PR: 0x   3c610    1004  0x8002    1000  ------  ------  ------ + ---- ---- [   13356]

[ 1] TotalDepth.LIS.core.pRepCode.ExceptionRepCodeUnknown: Unknown representation code: 0
Fixed by being a bit more cautious about dealing with DSB blocks that are 'null'.
"""
import math
import typing


__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2010-2011 Paul Ross. All rights reserved.'

import time
import sys
import os
import logging
import traceback
from optparse import OptionParser
import multiprocessing
# Serialisation
import pickle
import json
import pprint

from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import FileIndexer


class IndexTimer:
    def __init__(self, path: str):
        self.path = path
        self.file_size = os.path.getsize(self.path)
        self.error_count = 0
        self.len_pickle = -1
        self.len_json = -1
        self.times = []
    
    # def __iadd__(self, other):
    #     self.error_count += other._errCount
    #     self.times.extend(other._sizeTime)
    #     return self

    def __len__(self):
        return len(self.times)
        
    def __str__(self):
        if len(self.times):
            time_min = min(self.times)
            time_max = max(self.times)
            time_mean = sum(self.times) / len(self.times)
            if len(self.times) > 1:
                sorted_times = sorted(self.times)
                time_median = sorted_times[((len(sorted_times) + 1) // 2) - 1]
            else:
                time_median = self.times[0]
        else:
            time_min = time_max = time_mean = time_median = math.nan
        median_rate = time_median * 1000 / (self.file_size / 1024**2)
        ret = (
            f'{self.error_count:2d}'
            f' {self.file_size:12,d}'
            f' {self.len_pickle:12,d}'
            f' {self.len_json:12,d}'
            f' {time_min:8.3f}'
            f' {time_mean:8.3f}'
            f' {time_max:8.3f}'
            f' {time_median:8.3f}'
            f' {median_rate:8.3f}'
            # f' {self.path}'
        )
        return ret

    def inc_error_count(self):
        self.error_count += 1
    
    def add_time(self, t):
        self.times.append(t)

    @staticmethod
    def header() -> str:
        ret = (
            f'{"Er":2}'
            f' {"File Size":>12}'
            f' {"Len Pickle":>12}'
            f' {"Len Json":>12}'
            f' {"Time Min":>8}'
            f' {"Time Avg":>8}'
            f' {"Time Max":>8}'
            f' {"Time Med":>8}'
            f' {"Rate Med":>8}'
            # f' {self.path}'
        )
        return ret


def index_file(file_path: str, num_times: int, verbose: int, keepGoing) -> IndexTimer:
    logging.info('Index.indexFile(): {:s}'.format(os.path.abspath(file_path)))
    assert(os.path.isfile(file_path))
    ret = IndexTimer(file_path)
    try:
        for t in range(num_times):
            clk_start = time.perf_counter()
            lis_file  = File.file_read_with_best_physical_record_pad_settings(file_path, file_path, pr_limit=100)
            if lis_file is None:
                raise ExceptionTotalDepthLIS('Can not find valid PR pad settings for {:s}'.format(file_path))
            # May raise an ExceptionTotalDepthLIS
            lis_idx = FileIndexer.FileIndex(lis_file)
            ret.add_time(time.perf_counter() - clk_start)
            if t == 0:
                ret.len_pickle = len(pickle.dumps(lis_idx))
                json_object = lis_idx.jsonObject()
                json_bytes = json.dumps(json_object, sort_keys=True, indent=4)
                ret.len_json = len(json_bytes)
                if verbose:
                    print(lis_idx.longDesc())
                    print(' All records '.center(75, '='))
                    for aLr in lis_idx.genAll():
                        print(str(aLr))
                    print(' All records DONE '.center(75, '='))
                    print(' Log Passes '.center(75, '='))
                    for aLp in lis_idx.genLogPasses():
                        print('LogPass', aLp.logPass.longStr())
                        print()
                    print(' Log Passes DONE '.center(75, '='))
                    print(' Plot Records '.center(75, '='))
                    for aPlotRec in lis_idx.genPlotRecords():
                        print('Plot Record:', aPlotRec)
                        print()
                    print(' Plot Records DONE '.center(75, '='))
    except ExceptionTotalDepthLIS as err:
        ret.inc_error_count()
        logging.exception('Could not index %s', file_path)
    return ret


def index_dir_single_process(d, r, t, v, k) -> typing.Dict[str, IndexTimer]:
    """Recursively process a directory using a single process."""
    assert(os.path.isdir(d))
    ret: typing.Dict[str, IndexTimer] = {}
    for n in os.listdir(d):
        fp = os.path.join(d, n)
        if os.path.isfile(fp):
            ret[fp] = index_file(fp, t, v, k)
        elif os.path.isdir(fp) and r:
            result_map = index_dir_single_process(fp, r, t, v, k)
            for fp in result_map:
                ret[fp] = result_map[fp]
    return ret

################################
# Section: Multiprocessing code.
################################


def generate_file_paths(d, r):
    """Generates file paths, recursive if necessary."""
    assert(os.path.isdir(d))
    for n in os.listdir(d):
        fp = os.path.join(d, n)
        if os.path.isfile(fp):
            yield fp
        elif os.path.isdir(fp) and r:
            for aFp in generate_file_paths(fp, r):
                yield aFp


def index_dir_multi_process(directory, recursive, num_times, verbose, keepGoing, jobs) -> typing.Dict[str, IndexTimer]:
    if jobs < 1:
        jobs = multiprocessing.cpu_count()
    logging.info('indexDirMultiProcess(): Setting MP jobs to %d' % jobs)
    pool = multiprocessing.Pool(processes=jobs)
    tasks = [(fp, num_times, verbose, keepGoing) for fp in generate_file_paths(directory, recursive)]
    # result = IndexTimer(directory)
    results = [
        r.get() for r in [
            pool.apply_async(index_file, t) for t in tasks
        ]
    ]
    ret: typing.Dict[str, IndexTimer] = {v.path: v for v in results}
    return ret

################################
# End: Multiprocessing code.
################################


def main():
    usage = """usage: %prog [options] path
Indexes LIS files recursively."""
    print('Cmd: %s' % ' '.join(sys.argv))
    optParser = OptionParser(usage, version='%prog ' + __version__)
    optParser.add_option("-k", "--keep-going", action="store_true", dest="keepGoing", default=False, 
                      help="Keep going as far as sensible. [default: %default]")
    optParser.add_option(
            "-l", "--loglevel",
            type="int",
            dest="loglevel",
            default=20,
            help="Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: %default]"
        )
    optParser.add_option(
            "-j", "--jobs",
            type="int",
            dest="jobs",
            default=-1,
            help="Max processes when multiprocessing. Zero uses number of native CPUs [%d]. -1 disables multiprocessing." \
                    % multiprocessing.cpu_count() \
                    + " [default: %default]" 
        )      
    optParser.add_option("-t", "--times", type="int", dest="times", default=1,
            help="Number of times to repeat the read [default: %default]"
        )
    optParser.add_option("-s", "--statistics", action="store_true", dest="statistics", default=False, 
                      help="Dump timing statistics. [default: %default]")
    optParser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, 
                      help="Verbose Output. [default: %default]")
    optParser.add_option("-r", "--recursive", action="store_true", dest="recursive", default=False, 
                      help="Process input recursively. [default: %default]")
    # optParser.add_option("-J", "--JSON", action="store_true", dest="json", default=False,
    #                   help="Convert index to JSON, if verbose then dump it out as well. [default: %default]")
    opts, args = optParser.parse_args()
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                    format='%(asctime)s %(filename)24s %(lineno)4d %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    # Your code here
    #print('opts', opts)
    clk_start = time.perf_counter()
    if len(args) != 1:
        optParser.print_help()
        optParser.error("I can't do much without a path to the LIS file(s).")
        return 1
    if opts.times < 1:
        optParser.error("Number of test times needs to be >= 1.")
        return 1
    if os.path.isfile(args[0]):
        # Single file so always single process code
        results = {args[0]:  index_file(args[0], opts.times, opts.verbose, opts.keepGoing)}
    elif os.path.isdir(args[0]):
        if opts.jobs == -1:
            # Single process code
            results = index_dir_single_process(args[0], opts.recursive, opts.times, opts.verbose, opts.keepGoing)
        else:
            # Multiprocess code 
            results = index_dir_multi_process(args[0], opts.recursive, opts.times, opts.verbose, opts.keepGoing, opts.jobs)
    else:
        logging.error(f'Path {args[0]} does not exist!')
        return 1
    print('Summary:')
    error_count = sum([r.error_count > 0 for r in results.values()])
    if opts.statistics:
        common_prefix_len = len(os.path.commonpath([v.path for v in results.values()]))
        # Separate non-error indexes from error indexes
        print(f'Indexes completed without error [{len(results) - error_count}]:')
        print(IndexTimer.header())
        for k in sorted(results.keys()):
            if results[k].error_count == 0:
                print(results[k], results[k].path[common_prefix_len:])
        print(f'Indexes completed with error [{error_count}]:')
        print(IndexTimer.header())
        for k in sorted(results.keys()):
            if results[k].error_count != 0:
                print(results[k], results[k].path[common_prefix_len:])
    else:
        print('Results: {:8d}'.format(len(results)))
        print(' Errors: {:8d}'.format(error_count))
    clk_exec = time.perf_counter() - clk_start
    print('CPU time = %8.3f (S)' % clk_exec)
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
