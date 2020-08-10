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
"""Reads LAS files

Created on Jan 12, 2012

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2011-08-03'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2012-2020 Paul Ross.'

import sys
import os
import logging
import time
import typing
import collections
import re

from TotalDepth.LAS.core import LASRead
from TotalDepth.common import cmn_cmd_opts

logger = logging.getLogger(__file__)


class MnemonicDescriptionCount:
    def __init__(self):
        self.mnemonic_description_map: typing.Dict[str, typing.Dict[str, int]] = {}

    def add(self, mnemonic: str, description: str) -> None:
        if mnemonic not in self.mnemonic_description_map:
            self.mnemonic_description_map[mnemonic] = {}
        if description not in self.mnemonic_description_map[mnemonic]:
            self.mnemonic_description_map[mnemonic][description] = 1
        else:
            self.mnemonic_description_map[mnemonic][description] += 1

    def most_popular_description(self, mnemonic: str) -> str:
        assert (mnemonic in self.mnemonic_description_map)
        if len(self.mnemonic_description_map[mnemonic]) == 1:
            # Unique
            return self.mnemonic_description_map[mnemonic].keys[0]
        maxVal = max(self.mnemonic_description_map[mnemonic].values())
        l = [k for k, v in self.mnemonic_description_map[mnemonic].items() if v == maxVal]
        if len(l) == 1:
            return l[0]
        return ', '.join(l)


class ReadLASFiles:
    RE_DESC = re.compile(r'^\s*(\d+)\s*(.+)$')
    """Reads LAS files and captures the frequency of menemonics."""
    def __init__(self, path: str, raise_in_error: bool=True):
        self._cntrs = collections.defaultdict(int)
        # All mnemonics
        # {mnem : {desc : count, ...}, ...}
        self._mnemDescMap = {}
        # Curves only
        # {mnem : {desc : count, ...}, ...}
        self._curveDescMap = {}
        # Curve units only
        # {unit : {desc : count, ...}, ...}
        self._unitDescMap = {}
        # {mnem : count, ...} from well section
        self._wsdMnemCount = collections.defaultdict(int)
        # {mnem : count, ...} from parameter section
        self._paramMnemCount = collections.defaultdict(int)
        # Parameters only
        # {mnem : {desc : count, ...}, ...}
        self._paramDescMap = {}
        # {path : [(size, seconds), ...], ...}
        self._sizeTimeMap = {}
        self.raise_on_error = raise_in_error
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for name in filenames:
                    if name.startswith('.'):
                        continue
                    size, time = self._processFile(os.path.join(dirpath, name))
                    self._sizeTimeMap[os.path.join(dirpath, name)] = (size, time)
        elif os.path.isfile(path):
            size, time = self._processFile(path)
            self._sizeTimeMap[path] = (size, time)
        else:
            logger.error('Unknown path: {:s}'.format(path))

    def _processFile(self, fp) -> typing.Tuple[int, float]:
        """Process a single file. Returns the size of the file and the time taken to process."""
        rSize = os.path.getsize(fp)
        clkStart = time.perf_counter()
        success = False
        try:
            parsed_las_file = LASRead.LASRead(fp, raise_on_error=self.raise_on_error)
            self._cntrs['byte'] += rSize
            self._cntrs['sect'] += len(parsed_las_file)
            self._cntrs['fram'] += parsed_las_file.numFrames()
            self._cntrs['data'] += parsed_las_file.numDataPoints()
            self._procLAS(parsed_las_file)
            success = True
        except LASRead.ExceptionLASRead as err:
            logger.error('File: "{:s}", Error: {!r:s}'.format(fp, err))
            logger.exception('File: "{:s}", Error [{!r:s}]: {!r:s}'.format(fp, type(err), err))
            self._cntrs['erro'] += 1
        except Exception as err:
            logger.critical('File: "{:s}", Error: {!r:s}'.format(fp, err))
            logger.exception('File: "{:s}", Error [{!r:s}]: {!r:s}'.format(fp, type(err), err))
            self._cntrs['crit'] += 1
        self._cntrs['file'] += 1
        if success:
            exec_time = time.perf_counter() - clkStart
        else:
            exec_time = 0.0
        return rSize, exec_time
    
    def _procLAS(self, las: LASRead.LASRead) -> None:
        """Do the necesary processing updating internal state with the LAS parser."""
        self._updateDescMaps(las)
        self._updateWsdHistogram(las)
        self._updateParamHistogram(las)

    def _updateDescMaps(self, las: LASRead.LASRead) -> None:
        for s in las.genSects():
            self._updateMnemDescMapFromSect(s, self._mnemDescMap)
            self._updateUnitDescMapFromSect(s, self._unitDescMap)
            if s.type == 'C':
                self._updateMnemDescMapFromSect(s, self._curveDescMap)

    def _updateMnemDescMapFromSect(self, s, descMap):
        for m in range(len(s)):
            dat = s[m]
            # s[m] is a SectLine or a line for arrays, other etc.
            if isinstance(dat, LASRead.SectLine):
                myDesc = self._normaliseDescription(dat.desc)
                if isinstance(dat.mnem, int):
                    raise RuntimeError(f'Int as mnemonic {dat} {type(dat.mnem)} {dat.mnem!r}')
                if dat.mnem not in descMap:
                    descMap[dat.mnem] = collections.defaultdict(int)
                descMap[dat.mnem][myDesc] += 1
    
    def _updateUnitDescMapFromSect(self, s, descMap):
        for m in range(len(s)):
            dat = s[m]
            # s[m] is a SectLine or a line for arrays, other etc.
            if isinstance(dat, LASRead.SectLine):
                myDesc = self._normaliseDescription(dat.desc)
                if dat.unit is not None:
                    u = dat.unit
                    if not isinstance(u, str):
                        u = str(u)
                    if u not in descMap:
                        descMap[u] = collections.defaultdict(int)
                    descMap[u][myDesc] += 1
    
    def _normaliseDescription(self, d):
        """Normalise description according to some rules."""
        # Strip leading integer
        if isinstance(d, str):
            m = self.RE_DESC.match(d)
            if m is not None and m.group(2) is not None:
                d = m.group(2)
            return d.title()
        return str(d)

    def _updateWsdHistogram(self, las):
        """Looks at the Parameter section and updates self._wsdMnemCount."""
        # self._wsdMnemCount
        for s in 'W':
            try:
                sect = las[s]
            except KeyError:
                pass
            else:
                for m in sect.keys():
                    self._wsdMnemCount[m] += 1
    
    def _updateParamHistogram(self, las):
        """Looks at the Parameter section and updates self._paramMnemCount."""
        # self._paramMnemCount
        for s in 'P':
            try:
                sect = las[s]
            except KeyError:
                pass
            else:
                for m in sect.keys():
                    self._paramMnemCount[m] += 1
                self._updateMnemDescMapFromSect(sect, self._paramDescMap)

    @staticmethod
    def _clean_description(description: str) -> str:
        return ' '.join(description.replace('"', '\"').replace('\n', ' ').split())

    def _retMostPopularDescription(self, theMap, m) -> str:
        assert(m in theMap)
        if len(theMap[m]) == 1:
            # Unique
            return self._clean_description(list(theMap[m].keys())[0])
        maxVal = max(theMap[m].values())
        l = [k for k,v in theMap[m].items() if v == maxVal]
        if len(l) == 1:
            return self._clean_description(l[0])
        return self._clean_description(', '.join(l))

    def pprintMnemDesc(self, theS=sys.stdout):
        theS.write(' All mnemonics and their (most popular) description '.center(75, '-'))
        theS.write('\n')
        theS.write('{\n')
        for m in sorted(self._mnemDescMap.keys()):
            if len(m) <= 4:
                desc = self._retMostPopularDescription(self._mnemDescMap, m)
                theS.write('{:10s} : "{:s}",\n'.format('"{:s}"'.format(m), desc))
        theS.write('}\n')
        theS.write(' DONE: All mnemonics and their (most popular) description '.center(75, '-'))
        theS.write('\n')

    def pprintParameterMnemDesc(self, theS=sys.stdout):
        theS.write(' All Parameter mnemonics and their (most popular) description '.center(75, '-'))
        theS.write('\n')
        theS.write('{\n')
        for m in sorted(self._paramDescMap.keys()):
            if len(m) <= 4:
                desc = self._retMostPopularDescription(self._mnemDescMap, m)
                theS.write('{:10s} : "{:s}",\n'.format('"{:s}"'.format(m), desc))
        theS.write('}\n')
        theS.write(' DONE: All Parameter mnemonics and their (most popular) description '.center(75, '-'))
        theS.write('\n')

    def pprintCurveDesc(self, theS=sys.stdout):
        theS.write(' Curve mnemonics and their descriptions '.center(75, '-'))
        theS.write('{\n')
        for m in sorted(self._curveDescMap.keys()):
            if len(m) <= 4:
                desc = self._retMostPopularDescription(self._curveDescMap, m)
                theS.write('{:10s} : "{:s}",\n'.format('"{:s}"'.format(m), desc))
        theS.write('}\n')
        theS.write(' DONE: Curve mnemonics and their descriptions '.center(75, '-'))
        theS.write('\n')

    def pprintUnitDesc(self, theS=sys.stdout):
        theS.write(' Units and the channels that use them '.center(75, '-'))
        theS.write('\n')
        for m in sorted(self._unitDescMap.keys()):
            desc = self._retMostPopularDescription(self._unitDescMap, m)
            theS.write('{:10s} : "{:s}",\n'.format('"{:s}"'.format(m), desc))
        theS.write('}\n')
        theS.write(' DONE: Units and the channels that use them '.center(75, '-'))
        theS.write('\n')

    def pprintSizeTime(self, theS=sys.stdout):
        def _rate(size: int, time: float) -> float:
            rate = time * 1000 / (size / 1024 ** 2)
            return rate

        theS.write(' Size/Time (ms/Mb) '.center(75, '-'))
        theS.write('\n')
        theS.write(f'Smallest: {min(self._sizeTimeMap.keys())} Largest: {max(self._sizeTimeMap.keys())}')
        total_size = total_time = 0
        for path in sorted(self._sizeTimeMap.keys()):
            size, time = self._sizeTimeMap[path]
            if time != 0.0:
                rate = time * 1000 / (size / 1024**2)
                theS.write('{:<16d} {:8.3f} {:8.1f}  {}\n'.format(size, time, _rate(size, time), path))
                total_size += size
                total_time += time
        theS.write(f'Total size: {total_size:24,d} (bytes)\n')
        theS.write(f'Total time: {total_time:24.3f} (s)\n')
        theS.write(f'Total time: {_rate(total_size, total_time):24.3f} (ms/Mb)\n')
        theS.write(' DONE: Size/Time (ms/Mb) '.center(75, '-'))
        theS.write('\n')

    def pprintWsdMnemonicFrequency(self, out_stream: typing.TextIO=sys.stdout):
        out_stream.write(' Count of well site mnemonics and the % of files that have them '.center(75, '-'))
        out_stream.write('\n{\n')
        self._pprint_mnem_count(self._wsdMnemCount, out_stream)
        out_stream.write('}\n')
        out_stream.write(' DONE: Count of well site mnemonics and the % of files that have them '.center(75, '-'))
        out_stream.write('\n')

    def pprintParamMnemonicFrequency(self, out_stream: typing.TextIO=sys.stdout):
        out_stream.write(' Count of parameter mnemonics and the % of files that have them '.center(75, '-'))
        out_stream.write('\n{\n')
        self._pprint_mnem_count(self._paramMnemCount, out_stream)
        out_stream.write('}\n')
        out_stream.write(' DONE: Count of parameter mnemonics and the % of files that have them '.center(75, '-'))
        out_stream.write('\n')

    def _pprint_mnem_count(self, mnem_count: typing.Dict[str, int], out_stream: typing.TextIO) -> None:
        for m in sorted(mnem_count.keys()):
            if m in self._mnemDescMap:
                desc = self._retMostPopularDescription(self._mnemDescMap, m)
            else:
                desc = 'N/A'
            out_stream.write('{:12s} : {:40s}, # {:8d} {:8.2%}\n'.format(
                    '"{:s}"'.format(m),
                    '"{:s}"'.format(desc.replace('"', '\"').replace('\n', ' ')),
                    mnem_count[m],
                    mnem_count[m] / self._cntrs['file'],
                )
            )

    def results(self):
        r = ['ReadLASFiles:']
        r.append('   Files: {:16,d}'.format(self._cntrs['file']))
        r.append('  Errors: {:16,d}'.format(self._cntrs['erro']))
        r.append('Critical: {:16,d}'.format(self._cntrs['crit']))
        r.append('Files OK: {:16,d}'.format(self._cntrs['file'] - self._cntrs['erro'] - self._cntrs['crit']))
        r.append('   Bytes: {:16,d} ({:g} Mb)'.format(self._cntrs['byte'], self._cntrs['byte'] / 1024**2))
        r.append('Sections: {:16,d}'.format(self._cntrs['sect']))
        r.append('  Frames: {:16,d}'.format(self._cntrs['fram']))
        r.append('Log Data: {:16,d} ({:g} Mb)'.format(self._cntrs['data'], self._cntrs['data'] / 1024**2))
        return r


def main():
    """Main entry point."""
    print ('Cmd: %s' % ' '.join(sys.argv))
    usage = """usage: %prog [options] dir
Recursively reads LAS files in a directory reporting information about their contents."""
    parser = cmn_cmd_opts.path_in(usage, version='%prog ' + __version__)
    cmn_cmd_opts.add_log_level(parser, 40)
    # Specialised arguments for output.
    parser.add_argument("-m", "--mnemonic", action="store_true", default=False,
                        help="Output Mnemonic map. Default: %(default)s.")
    parser.add_argument("-c", "--curve", action="store_true", default=False,
                        help="Output Curve map. Default: %(default)s.")
    parser.add_argument("-u", "--unit", action="store_true", default=False,
                        help="Output Units map. Default: %(default)s.")
    parser.add_argument("-w", "--wsd", action="store_true", default=False,
                        help="Output Well Site Data map. Default: %(default)s.")
    parser.add_argument("-p", "--param", action="store_true", default=False,
                        help="Output Parameter section mnemonics and their most popular description and a map of the"
                             "mnemonic frequency. Default: %(default)s.")
    parser.add_argument("-s", "--size-time", action="store_true", default=False,
                        help="Output parser's size vs time performance. Default: %(default)s.")
    parser.add_argument("-a", "--all", action="store_true", default=False,
                        help="Output all, equivalent to -mcuwps. Default: %(default)s.")

    args = parser.parse_args()
    # print(args)
    # return 0
    # Initialise logging etc.
    cmn_cmd_opts.set_log_level(args)
    clkStart = time.perf_counter()
    timStart = time.time()
    # Your code here.
    las_reader = ReadLASFiles(args.path_in, raise_in_error=not args.keepGoing)
    if args.mnemonic or args.all:
        las_reader.pprintMnemDesc()
    if args.curve or args.all:
        las_reader.pprintCurveDesc()
    if args.unit or args.all:
        las_reader.pprintUnitDesc()
    if args.wsd or args.all:
        las_reader.pprintWsdMnemonicFrequency()
    if args.param or args.all:
        las_reader.pprintParameterMnemDesc()
        las_reader.pprintParamMnemonicFrequency()
    if args.size_time or args.all:
        las_reader.pprintSizeTime()
    print('\n'.join(las_reader.results()))
    print('  CPU time = %8.3f (S)' % (time.perf_counter() - clkStart))
    print('Exec. time = %8.3f (S)' % (time.time() - timStart))
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
