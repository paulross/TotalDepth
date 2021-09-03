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
"""Reads LAS files and provides statistics on their content.

This also measures the performance of the LAS parser.

Created on Jan 12, 2012

@author: paulross
"""
import sys
import os
import logging
import time
import typing
import collections
import re

from TotalDepth.LAS.core import LASRead
from TotalDepth.common import cmn_cmd_opts, process
from TotalDepth.util import gnuplot

__author__ = 'Paul Ross'
__date__ = '2011-08-03'
__version__ = '0.1.0'
__rights__ = 'Copyright (c) 2012-2020 Paul Ross.'


logger = logging.getLogger(__file__)


class MnemonicDescriptionCount:
    def __init__(self):
        # {mnem : {desc : count, ...}, ...}
        self.mnemonic_description_map: typing.Dict[str, collections.Counter] = {}

    def add(self, mnemonic: str, description: str) -> None:
        if mnemonic not in self.mnemonic_description_map:
            self.mnemonic_description_map[mnemonic] = collections.Counter()
        self.mnemonic_description_map[mnemonic].update([description])

    def most_popular_description(self, mnemonic: str) -> str:
        assert (mnemonic in self.mnemonic_description_map)
        most_common = self.mnemonic_description_map[mnemonic].most_common(1)
        return ', '.join(value for value, _count in most_common)

    def menmonics(self) -> typing.KeysView[str]:
        return self.mnemonic_description_map.keys()

    def description_count(self,  mnemonic: str) -> int:
        return len(self.mnemonic_description_map[mnemonic])


class ReadLASFiles:
    RE_DESC = re.compile(r'^\s*(\d+)\s*(.+)$')
    """Reads LAS files and captures the frequency of menemonics."""
    def __init__(self, path: str, raise_on_error: bool = True):
        self.counters = collections.defaultdict(int)
        # All mnemonics
        self.mnemonic_description_map = MnemonicDescriptionCount()
        # Curves only
        self.curve_description_map = MnemonicDescriptionCount()
        # Curve units only
        # {mnem : {units : count, ...}, ...}
        self.unit_description_map = MnemonicDescriptionCount()
        # {mnem : count, ...} from well section
        self.wsd_mnemonic_count = collections.Counter()
        # {mnem : count, ...} from parameter section
        self.paramater_mnemonic_count = collections.Counter()
        # Parameters only
        self.parameter_description_map = MnemonicDescriptionCount()
        # {path : [(size, seconds), ...], ...}
        self.path_size_time_map: typing.Dict[str, typing.Tuple[int, float]] = {}
        self.raise_on_error = raise_on_error
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for name in filenames:
                    if name.startswith('.'):
                        continue
                    file_path = os.path.join(dirpath, name)
                    size, exec_time = self._process_file(file_path)
                    self.path_size_time_map[file_path] = (size, exec_time)
        elif os.path.isfile(path):
            size, exec_time = self._process_file(path)
            self.path_size_time_map[path] = (size, exec_time)
        else:
            logger.error('Unknown path: {:s}'.format(path))

    def _process_file(self, file_path: str) -> typing.Tuple[int, float]:
        """Process a single file. Returns the size of the file and the time taken to process."""
        logger.info('Reading file: %s', file_path)
        file_size = os.path.getsize(file_path)
        exec_time = 0.0
        try:
            perf_counter_start = time.perf_counter()
            parsed_las_file = LASRead.LASRead(file_path, raise_on_error=self.raise_on_error)
            exec_time = time.perf_counter() - perf_counter_start
            self.counters['byte'] += file_size
            self.counters['sect'] += len(parsed_las_file)
            self.counters['fram'] += parsed_las_file.number_of_frames()
            self.counters['data'] += parsed_las_file.number_of_data_points()
            self._process_las_file(parsed_las_file)
        except LASRead.ExceptionLASRead as err:
            logger.error('File: "{:s}", Error: {!r:s}'.format(file_path, err))
            logger.exception('File: "{:s}", Error [{!r:s}]: {!r:s}'.format(file_path, type(err), err))
            self.counters['erro'] += 1
        except Exception as err:
            logger.critical('File: "{:s}", Error: {!r:s}'.format(file_path, err))
            logger.exception('File: "{:s}", Error [{!r:s}]: {!r:s}'.format(file_path, type(err), err))
            self.counters['crit'] += 1
        self.counters['file'] += 1
        return file_size, exec_time
    
    def _process_las_file(self, las_file: LASRead.LASRead) -> None:
        """Do the necesary processing updating internal state with the LAS parser."""
        self._update_description_maps(las_file)
        self._update_wsd_histogram(las_file)
        self._update_parameter_histogram(las_file)

    def _update_description_maps(self, las_file: LASRead.LASRead) -> None:
        for section in las_file.generate_sections():
            self._update_mnemonic_description_map_from_section(section, self.mnemonic_description_map)
            if section.type == 'C':
                self._update_mnemonic_description_map_from_section(section, self.curve_description_map)
                for index in range(len(section)):
                    data = section[index]
                    if isinstance(data, LASRead.SectLine):
                        self.unit_description_map.add(data.mnem, str(data.unit))

    def _update_mnemonic_description_map_from_section(self, section: LASRead.LASSection,
                                                      description_map: MnemonicDescriptionCount):
        for mnemonic in range(len(section)):
            data = section[mnemonic]
            if isinstance(data, LASRead.SectLine):
                if isinstance(data.mnem, int):
                    raise RuntimeError(f'Int as mnemonic {data} {type(data.mnem)} {data.mnem!r}')
                description_map.add(data.mnem, self._normalise_description(data.desc))

    def _update_unit_description_map_from_section(self, section: LASRead.LASSection,
                                                  description_map: MnemonicDescriptionCount):
        for index in range(len(section)):
            data = section[index]
            if isinstance(data, LASRead.SectLine):
                description_map.add(data.mnem, self._normalise_description(data.desc))
    
    def _normalise_description(self, d):
        """Normalise description according to some rules."""
        # Strip leading integer
        if isinstance(d, str):
            m = self.RE_DESC.match(d)
            if m is not None and m.group(2) is not None:
                d = m.group(2)
            return d.title()
        return str(d)

    def _update_wsd_histogram(self, las):
        """Looks at the Parameter section and updates self._wsdMnemCount."""
        # self._wsdMnemCount
        for s in 'W':
            try:
                section = las[s]
            except KeyError:
                pass
            else:
                for m in section.keys():
                    self.wsd_mnemonic_count.update([m])

    def _update_parameter_histogram(self, las):
        """Looks at the Parameter section and updates self._paramMnemCount."""
        for s in 'P':
            try:
                section = las[s]
            except KeyError:
                pass
            else:
                for mnemonic in section.keys():
                    self.paramater_mnemonic_count.update([mnemonic])
                self._update_mnemonic_description_map_from_section(section, self.parameter_description_map)

    @staticmethod
    def _clean_description(description: str) -> str:
        return ' '.join(description.replace('"', '\"').replace('\n', ' ').split())

    # def _retMostPopularDescription(self, theMap, m) -> str:
    #     assert(m in theMap)
    #     if len(theMap[m]) == 1:
    #         # Unique
    #         return self._clean_description(list(theMap[m].keys())[0])
    #     maxVal = max(theMap[m].values())
    #     l = [k for k,v in theMap[m].items() if v == maxVal]
    #     if len(l) == 1:
    #         return self._clean_description(l[0])
    #     return self._clean_description(', '.join(l))

    def _pprint_mnemonic_description(self, mnemonic_map: MnemonicDescriptionCount, title: str,
                                     out_stream: typing.TextIO = sys.stdout):
        out_stream.write(f' All {title} mnemonics and their (most popular) description '.center(75, '-'))
        out_stream.write('\n')
        out_stream.write('{\n')
        for mnemonic in sorted(mnemonic_map.menmonics()):
            # if len(mnemonic) <= 4:
            description = mnemonic_map.most_popular_description(mnemonic)
            out_stream.write(
                '{:32s} : "{:64s}", # Out of {:d}\n'.format(
                    '"{:s}"'.format(mnemonic), description, mnemonic_map.description_count(mnemonic)
                )
            )
        out_stream.write('}\n')
        out_stream.write(f' DONE: All {title} mnemonics and their (most popular) description '.center(75, '-'))
        out_stream.write('\n')

    def pprint_mnemonic_description(self, out_stream: typing.TextIO = sys.stdout):
        self._pprint_mnemonic_description(self.mnemonic_description_map, '', out_stream)

    def pprint_parameter_mnemonic_description(self, out_stream: typing.TextIO = sys.stdout):
        self._pprint_mnemonic_description(self.parameter_description_map, 'Parameter', out_stream)

    def pprint_curve_description(self, out_stream: typing.TextIO = sys.stdout):
        self._pprint_mnemonic_description(self.curve_description_map, 'Curve', out_stream)

    def pprint_unit_description(self, out_stream: typing.TextIO = sys.stdout):
        out_stream.write(' Channels and their Units '.center(75, '-'))
        out_stream.write('\n')
        out_stream.write('{\n')
        for mnemonic in sorted(self.unit_description_map.menmonics()):
            # description = self.unit_description_map.most_popular_description(mnemonic)
            out_stream.write(
                '{:10s} : "{:s}",\n'.format(
                    '"{:s}"'.format(mnemonic), str(self.unit_description_map.mnemonic_description_map[mnemonic])
                )
            )
        out_stream.write('}\n')
        out_stream.write(' DONE: Channels and their Units '.center(75, '-'))
        out_stream.write('\n')

    def pprint_size_time(self, out_stream=sys.stdout):
        def _rate(size: int, time: float) -> float:
            if size:
                rate = time * 1000 / (size / 1024 ** 2)
            else:
                rate = 0.0
            return rate

        out_stream.write(' Size/Time (ms/Mb) '.center(75, '-'))
        out_stream.write('\n')
        # out_stream.write(
        #     f'Smallest: {min(self.path_size_time_map.keys())}'
        #     f' at {self.path_size_time_map[min(self.path_size_time_map.keys())]}\n'
        # )
        # out_stream.write(
        #     f' Largest: {max(self.path_size_time_map.keys())}'
        #     f' at {self.path_size_time_map[max(self.path_size_time_map.keys())]}\n'
        # )
        total_size = total_time = 0
        for path in sorted(self.path_size_time_map.keys()):
            file_size, exec_time = self.path_size_time_map[path]
            if exec_time != 0.0:
                rate = exec_time * 1000 / (file_size / 1024**2)
                out_stream.write('{:<16d} {:8.3f} {:8.1f}  {}\n'.format(file_size, exec_time, _rate(file_size, exec_time), path))
                total_size += file_size
                total_time += exec_time
        out_stream.write(f'Total size: {total_size:24,d} (bytes)\n')
        out_stream.write(f'Total time: {total_time:24.3f} (s)\n')
        out_stream.write(f' Mean rate: {_rate(total_size, total_time):24.3f} (ms/Mb)\n')
        out_stream.write(' DONE: Size/Time (ms/Mb) '.center(75, '-'))
        out_stream.write('\n')

    def pprint_wsd_mnemonic_frequency(self, out_stream: typing.TextIO=sys.stdout):
        out_stream.write(' Count of well site mnemonics and the % of files that have them '.center(75, '-'))
        out_stream.write('\n{\n')
        self._pprint_mnem_count(self.wsd_mnemonic_count, out_stream)
        out_stream.write('}\n')
        out_stream.write(' DONE: Count of well site mnemonics and the % of files that have them '.center(75, '-'))
        out_stream.write('\n')

    def pprint_param_mnemonic_frequency(self, out_stream: typing.TextIO=sys.stdout):
        out_stream.write(' Count of parameter mnemonics and the % of files that have them '.center(75, '-'))
        out_stream.write('\n{\n')
        self._pprint_mnem_count(self.paramater_mnemonic_count, out_stream)
        out_stream.write('}\n')
        out_stream.write(' DONE: Count of parameter mnemonics and the % of files that have them '.center(75, '-'))
        out_stream.write('\n')

    def _pprint_mnem_count(self, mnem_count: typing.Dict[str, int], out_stream: typing.TextIO) -> None:
        for m in sorted(mnem_count.keys()):
            if m in self.mnemonic_description_map.menmonics():
                desc = self.mnemonic_description_map.most_popular_description(m)
            else:
                desc = 'N/A'
            out_stream.write('{:32s} : {:64}, # {:8d} {:8.2%}\n'.format(
                    '"{:s}"'.format(m),
                    '"{:s}"'.format(desc.replace('"', '\"').replace('\n', ' ')),
                    mnem_count[m],
                    mnem_count[m] / self.counters['file'],
                )
            )

    def results(self):
        r = ['ReadLASFiles:']
        r.append('   Files: {:16,d}'.format(self.counters['file']))
        r.append('  Errors: {:16,d}'.format(self.counters['erro']))
        r.append('Critical: {:16,d}'.format(self.counters['crit']))
        r.append('Files OK: {:16,d}'.format(self.counters['file'] - self.counters['erro'] - self.counters['crit']))
        r.append('   Bytes: {:16,d} ({:g} Mb)'.format(self.counters['byte'], self.counters['byte'] / 1024 ** 2))
        r.append('Sections: {:16,d}'.format(self.counters['sect']))
        r.append('  Frames: {:16,d}'.format(self.counters['fram']))
        r.append(' Samples: {:16,d}'.format(self.counters['data']))
        return r


GNUPLOT_PLT = """set logscale x
set grid
set title "Scan of LAS Files with ReadLASFiles.py."
set xlabel "LAS File Size (bytes)"
# set mxtics 5
# set xrange [0:3000]
# set xtics
# set format x ""

set logscale y
set ylabel "Scan time (s)"
# set yrange [1:1e5]
# set ytics 20
# set mytics 2
# set ytics 8,35,3

set logscale y2
set y2label "Scan Rate (ms/Mb)"
# set y2range [1e-4:10]
set y2tics

set pointsize 0.75
set datafile separator whitespace#"	"
set datafile missing "NaN"

set terminal svg size 1000,700 # choose the file format
set output "{name}.svg" # choose the output device

plot "{name}.dat" using 1:2 axes x1y1 title "LAS Read Time (s), left axis" lt 1 w points, \\
    "{name}.dat" using 1:($2*1000/($1/(1024*1024))) axes x1y2 title "LAS Read Rate (ms/MB), right axis" lt 2 w points

reset
"""


def plot_gnuplot(data: ReadLASFiles, gnuplot_dir: str) -> None:
    # if len(data) < 2:
    #     raise ValueError(f'Can not plot data with only {len(data)} points.')
    # First row is header row, create it then comment out the first item.
    table = [
        ['size_input', 'time', 'Path']
    ]
    table[0][0] = f'# {table[0][0]}'
    for file_path in sorted(data.path_size_time_map.keys()):
        file_size, file_time = data.path_size_time_map[file_path]
        table.append([file_size, file_time, file_path,])
    name = 'ReadLASFiles'
    return_code = gnuplot.invoke_gnuplot(gnuplot_dir, name, table, GNUPLOT_PLT.format(name=name))
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')
    return_code = gnuplot.write_test_file(gnuplot_dir, 'svg')
    if return_code:
        raise IOError(f'Can not plot gnuplot with return code {return_code}')


def main():
    """Main entry point."""
    print ('Cmd: %s' % ' '.join(sys.argv))
    usage = """usage: %prog [options] dir
Recursively reads LAS files in a directory reporting information about their contents."""
    parser = cmn_cmd_opts.path_in(usage, version='%prog ' + __version__)
    cmn_cmd_opts.add_log_level(parser, 40)
    process.add_process_logger_to_argument_parser(parser)
    gnuplot.add_gnuplot_to_argument_parser(parser)
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
    log_level = cmn_cmd_opts.set_log_level(args)
    clkStart = time.perf_counter()
    timStart = time.time()
    # Your code here.
    if args.log_process > 0.0:
        with process.log_process(args.log_process, log_level):
            las_reader = ReadLASFiles(args.path_in, raise_on_error=not args.keepGoing)
    else:
        las_reader = ReadLASFiles(args.path_in, raise_on_error=not args.keepGoing)
    if args.mnemonic or args.all:
        las_reader.pprint_mnemonic_description()
    if args.curve or args.all:
        las_reader.pprint_curve_description()
    if args.unit or args.all:
        las_reader.pprint_unit_description()
    if args.wsd or args.all:
        las_reader.pprint_wsd_mnemonic_frequency()
    if args.param or args.all:
        las_reader.pprint_parameter_mnemonic_description()
        las_reader.pprint_param_mnemonic_frequency()
    if args.size_time or args.all:
        las_reader.pprint_size_time()
    if args.gnuplot:
        try:
            plot_gnuplot(las_reader, args.gnuplot)
        except IOError:
            logger.exception('Plotting with gnuplot failed.')
    print('\n'.join(las_reader.results()))
    print('  CPU time = %8.3f (S)' % (time.perf_counter() - clkStart))
    print('Exec. time = %8.3f (S)' % (time.time() - timStart))
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
