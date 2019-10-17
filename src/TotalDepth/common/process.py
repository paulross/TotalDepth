"""
Logs process information, such as memory usage, to a log as JSON. Example wit ('memory_info', 'cpu_times')::

    (Thread-7  ) ProcessLoggingThread JSON: {"memory_info": {"rss": 145448960, "vms": 4542902272, "pfaults": 37618, "pageins": 0}, "cpu_times": {"user": 0.28422032, "system": 0.099182912, "children_user": 0.0, "children_system": 0.0}}

There are several DoF here:

- Logging interval in seconds. Or by poke()?
- Logging level, DEBUG, INFO etc.
- Logging verbosity, for example just memory? Or everything about the process (self._process.as_dict())

Also need to add a log parser to, well what?

"""
import argparse
import contextlib
import datetime
import json
import logging
import os
import re
import sys
import threading
import time
import typing

import psutil

from TotalDepth.util import gnuplot

logger = logging.getLogger(__file__)


LOGGER_PREFIX = 'ProcessLoggingThread-JSON'
RE_LOG_LINE = re.compile(rf'^.+?{LOGGER_PREFIX}\s?(.+)$')
# Matches '2019-06-07 11:57:58.390921'
DATETIME_NOW_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
assert datetime.datetime.strptime(str(datetime.datetime.now()), DATETIME_NOW_FORMAT)
KEY_TIMESTAMP = 'timestamp'
# psutil.Process().as_dict() has the following keys:
PSUTIL_PROCESS_AS_DICT_KEYS = [
    'cmdline', 'connections', 'cpu_percent', 'cpu_times', 'create_time', 'cwd', 'environ', 'exe', 'gids',
    'memory_full_info', 'memory_info', 'memory_percent', 'name', 'nice', 'num_ctx_switches', 'num_fds', 'num_threads',
    'open_files', 'pid', 'ppid', 'status', 'terminal', 'threads', 'uids', 'username'
]
# Usage: GNUPLOT_PLT.format(name=dat_file_name)
GNUPLOT_PLT = """
set grid
set title "Memory and CPU Usage."
set xlabel "Elapsed Time (s)"
# set mxtics 5
# set xrange [0:3000]
# set xtics
# set format x ""

#set logscale y
set ylabel "Memory Usage (Mb)"
# set yrange [1:1e5]
# set ytics 20
# set mytics 2
# set ytics 8,35,3

#set logscale y2
set y2label "CPU Usage (%)"
# set y2range [1e-4:10]
set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

set terminal svg size 1000,700 # choose the file format
set output "{name}.svg" # choose the output device

# set key off

#set key title "Window Length"
#  lw 2 pointsize 2

plot "{name}.dat" using 1:($2 / 1024**2) axes x1y1 title "RSS (Mb), left axis" with lines lt 1 lw 1, \\
    "{name}.dat" using 1:($3 / 1000) axes x1y2 title "Page Faults (1000/s), right axis" with lines lt 3 lw 1, \\
    "{name}.dat" using 1:5 axes x1y2 title "Mean CPU (%), right axis" with lines lt 2 lw 1, \\
    "{name}.dat" using 1:6 axes x1y2 title "Instantaneous CPU (%), right axis" with lines lt 7 lw 1

reset
"""


def parse_timestamp(s: str) -> datetime.datetime:
    return datetime.datetime.strptime(s, DATETIME_NOW_FORMAT)


def extract_json(istream: typing.TextIO) -> typing.List[typing.Dict[str, typing.Any]]:
    """Reads a log file and returns the JSON as a list of dicts. Non-matching lines are ignored."""
    ret = []
    for line in istream.readlines():
        m = RE_LOG_LINE.match(line)
        if m:
            log_dict = json.loads(m.group(1))
            if KEY_TIMESTAMP in log_dict:
                log_dict[KEY_TIMESTAMP] = parse_timestamp(log_dict[KEY_TIMESTAMP])
            ret.append(log_dict)
    return ret


def extract_json_as_table(istream: typing.TextIO) -> typing.List[typing.List[str]]:
    json_data = extract_json(istream)
    ret = [
        [
            f'{"#t(s)":12}',
            f'{"RSS":>12}',
            f'{"PageFaults/s":>12}',
            f'{"User":>12}',
            f'{"Mean_CPU%":>12}',
            f'{"Inst_CPU%":>12}',
            f'{"Timestamp"}',
        ]
    ]
    prev_cpu = 0.0
    prev_elapsed_time = 0.0
    prev_page_faults = 0
    for record in json_data:
        mean_cpu_user = record["cpu_times"]["user"] / record["elapsed_time"]
        inst_cpu_user = (record["cpu_times"]["user"] - prev_cpu) / (record["elapsed_time"] - prev_elapsed_time)
        # record["memory_info"]["pfaults"] is the cumulative total.
        inst_page_faults = (record["memory_info"]["pfaults"] - prev_page_faults) / (record["elapsed_time"] - prev_elapsed_time)
        ret.append(
            [
                f'{record["elapsed_time"]:<12.1f}',
                f'{record["memory_info"]["rss"]:12d}',
                f'{inst_page_faults:12f}',
                f'{record["cpu_times"]["user"]:12.1f}',
                f'{mean_cpu_user:12.1%}',
                f'{inst_cpu_user:12.1%}',
                f'{record["timestamp"].strftime("%Y-%m-%dT%H:%M:%S.%f")}',
            ]
        )
        prev_cpu = record["cpu_times"]["user"]
        prev_elapsed_time = record["elapsed_time"]
        prev_page_faults = record["memory_info"]["pfaults"]
    return ret


def invoke_gnuplot(log_path: str, gnuplot_dir: str) -> int:
    """Reads a log file, extracts the data, writes it out to gnuplot_dir and invokes gnuplot on it."""
    os.makedirs(gnuplot_dir, exist_ok=True)
    ret = gnuplot.write_test_file(gnuplot_dir, 'svg')
    if ret:
        logger.error(f'Can not write gnuplot test file with error code {ret}')
        return ret
    with open(log_path) as instream:
        table = extract_json_as_table(instream)
    log_name = os.path.basename(log_path)
    ret = gnuplot.invoke_gnuplot(gnuplot_dir, log_name, table, GNUPLOT_PLT.format(name=log_name))
    return ret

# TODO: Have a module level queue.Queue the can be used to pass messages to this thread.
#   These are then written out and the process data can be associated with them.
# TODO: The can be plotted by gnuplot as labels:
#   # arrows and labels
#   set arrow from 27.57,70 to 27.57,87 lt 1
#   set label "Threshold\nt=27.6s" at 27.57,69 center font ",12"
#   set arrow from 33.83,70 to 33.83,82 lt 1
#   set label "Touchdown\nt=33.8s" at 33.83,69 center font ",12"


class ProcessLoggingThread(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name, daemon=daemon)
        self.args = args
        self.kwargs = kwargs
        self._interval = args[0] if len(args) else kwargs['interval']
        self._process = psutil.Process()
        self._run = True

    def _get_process_data(self):
        ret = {
            KEY_TIMESTAMP: datetime.datetime.now().strftime(DATETIME_NOW_FORMAT),
        }
        ret.update(
            {
                k: getattr(self._process, k)()._asdict() for k in ('memory_info', 'cpu_times')
            }
        )
        ret['elapsed_time'] =  time.time() - self._process.create_time()
        # WARNING: This is super verbose and leaks information such as user, environment etc. into the log file.
        # ret.update(self._process.as_dict())
        return ret

    def run(self):
        while self._run:
            logger.info(f'{LOGGER_PREFIX} {json.dumps(self._get_process_data())}')
            time.sleep(self._interval)

    def join(self, *args, **kwargs):
        self._run = False
        super().join(*args, **kwargs)


@contextlib.contextmanager
def log_process(*args, **kwargs):
    process_thread = ProcessLoggingThread(args=args, kwargs=kwargs)
    process_thread.start()
    try:
        yield
    finally:
        process_thread.join()


def add_process_logger_to_argument_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        '--log-process', default=0.0, type=float,
        help='Writes process data such as memory usage as a log INFO line every LOG_PROCESS seconds.'
             ' If 0.0 no process data is logged. [default: %(default)s]',
    )


def main() -> int:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(filename)s - %(process)5d - (%(threadName)-10s) - %(levelname)-8s - %(message)s',
    )
    if len(sys.argv) == 3:
        invoke_gnuplot(sys.argv[1], sys.argv[2])
    else:
        memory = []
        with log_process(1.0):
            for i in range(8):
                memory.append(' ' * (16 * 1024**2))
                time.sleep(2)
    return 0


if __name__ == '__main__':
    sys.exit(main())
