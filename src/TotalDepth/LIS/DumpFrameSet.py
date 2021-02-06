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
"""Reads a LIS file and writes out separated values of each frame.

Created on 25 Mar 2011
"""
import time
import sys
import os
import logging
from optparse import OptionParser

from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import FileIndexer
from TotalDepth.LIS.core import FrameSet

__author__ = 'Paul Ross'
__date__ = '2010-08-02'
__version__ = '0.1.0'
__rights__ = 'Copyright (c) Paul Ross'


def dump_frame_sets(fp, keep_going, output_frames: bool, output_summary: bool, channels, seperator: str=' '):
    """Dump the frame values to stdout.
    channels is a set of Mnems, if non-empty then only these channels, if present, are written out."""
    logging.info('Index.indexFile(): {:s}'.format(fp))
    assert(os.path.isfile(fp))
    lis_file = File.FileRead(fp, theFileId=fp, keepGoing=keep_going)
    lis_index = FileIndexer.FileIndex(lis_file)
    for aLp in lis_index.genLogPasses():
        print(aLp)
        # Load the FrameSet
        if aLp.logPass.totalFrames == 0:
            print('No frames to load.')
        else:
            aLp.logPass.setFrameSet(lis_file, None, None)
            frame_set = aLp.logPass.frameSet
            if output_frames:
                # Print the channels and units
                headers = []
                if frame_set.isIndirectX:
                    headers.append('XAXIS [{:s}]'.format(frame_set.xAxisDecl.depthUnits.decode('ascii')))
                indexes = []
                if len(channels):
                    for i, (m, u) in enumerate(aLp.logPass.genFrameSetHeadings()):
                        if m in channels:
                            headers.append('{:s} [{:s}]'.format(m.decode('ascii'), u.decode('ascii')))
                            indexes.append(i)
                else:
                    headers.extend([
                        '{:s} [{:s}]'.format(m.decode('ascii'), u.decode('ascii')) for m, u in aLp.logPass.genFrameSetHeadings()
                    ])
                if len(channels) and len(indexes) == len(channels):
                    logging.warning(
                        'Some channels you specified can not be found: indexes={!r:s} channels={!r:s}'.format(
                            indexes, channels
                        )
                    )
                print(seperator.join(f'{h:18s}' for h in headers))
                for frIdx in range(frame_set.numFrames):
                    if frame_set.isIndirectX:
                        print('%16g' % frame_set.xAxisValue(frIdx), ' ', end='')
                    if len(indexes):
                        values = [frame_set.frame(frIdx)[i] for i in indexes]
                        print(seperator.join(['%18g' % v for v in values]))
                    else:
                        print(seperator.join(['%18g' % v for v in frame_set.frame(frIdx)]))
            if output_summary:
                # Accumulate min/mean/max
                accumulate_classes = [
                        FrameSet.AccCount,
                        FrameSet.AccMin,
                        FrameSet.AccMean,
                        FrameSet.AccMax,
                        FrameSet.AccStDev,
                        FrameSet.AccDec,
                        FrameSet.AccEq,
                        FrameSet.AccInc,
                        FrameSet.AccBias,
                        FrameSet.AccDrift,
                        FrameSet.AccActivity,
                ]
                accumulated_data = frame_set.accumulate(accumulate_classes)
                print()
                format_str = '{:12s} ' + (' {:>12s}'*len(accumulate_classes))
                summary_header = ['Channel']
                summary_header.extend(cls.title for cls in accumulate_classes)
                print(format_str.format(*summary_header))
                sub_channel_names_and_units = list(aLp.logPass.genFrameSetScNameUnit())
                for scIdx, aRow in enumerate(accumulated_data):
                    print('{:4s} [{:4s}]'.format(*sub_channel_names_and_units[scIdx]),
                          ' ',
                          ' '.join(['{:12.5g}'.format(v) for v in aRow]))


def main():
    usage = """usage: %prog [options] dir
Reads a LIS file and writes out tab separated values of each frame."""
    print('Cmd: %s' % ' '.join(sys.argv))
    option_parser = OptionParser(usage, version='%prog ' + __version__)
    option_parser.add_option("-k", "--keep-going", action="store_true", dest="keepGoing", default=False,
                             help="Keep going as far as sensible. [default: %default]")
    option_parser.add_option(
            "-l", "--loglevel",
            type="int",
            dest="loglevel",
            default=20,
            help="Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: %default]"
        )      
    option_parser.add_option("--no-frames", action="store_true", default=False,
                             help="Suppress the actual values of the frames. [default: %default]")
    option_parser.add_option("--summary", action="store_true", default=False,
                             help="Display summary. [default: %default]")
    option_parser.add_option("-c", "--channels", action="append", type="str",
                             help="Only dump these named curves.", default=[])
    opts, args = option_parser.parse_args()
    clock_start = time.perf_counter()
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        stream=sys.stdout)
    # Your code here
    if len(args) != 1:
        option_parser.print_help()
        option_parser.error("I can't do much without a path to the LIS file.")
        return 1
    dump_frame_sets(args[0], opts.keepGoing, not opts.no_frames, opts.summary, set([v.encode('ascii') for v in opts.channels]))
    clock_exec = time.perf_counter() - clock_start
    print('CPU time = %8.3f (S)' % clock_exec)
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
