"""
Logs process information, such as memory usage, to a log as JSON. Example with ('memory_info', 'cpu_times')::

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
import queue
import random
import re
import sys
import threading
import time
import typing

import psutil

from TotalDepth.util import gnuplot

logger = logging.getLogger(__file__)


#: Unique string in the log line
LOGGER_PREFIX = 'ProcessLoggingThread-JSON'
LOGGER_PREFIX_START = f'{LOGGER_PREFIX}-START'
LOGGER_PREFIX_STOP = f'{LOGGER_PREFIX}-STOP'
#: Regex for the unique string in the log line
RE_LOG_LINE = re.compile(rf'^.+?{LOGGER_PREFIX}(-START|-STOP)?\s*(.+)$')
#: Regex for timestam, matches '2019-06-07 11:57:58.390921'
DATETIME_NOW_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
assert datetime.datetime.strptime(str(datetime.datetime.now()), DATETIME_NOW_FORMAT)
#: The JSON key that is the timestamp
KEY_TIMESTAMP = 'timestamp'
#: The JSON key that is elapsed (wall clock) time in seconds. This is ``time.time() - self._process.create_time()``
KEY_ELAPSED_TIME = 'elapsed_time'
#: The JSON key that is the label
KEY_LABEL = 'label'
#: The JSON key that is the process ID
KEY_PROCESS_ID = 'pid'
#: psutil.Process().as_dict() has the following keys:
PSUTIL_PROCESS_AS_DICT_KEYS = [
    'cmdline', 'connections', 'cpu_percent', 'cpu_times', 'create_time', 'cwd', 'environ', 'exe', 'gids',
    'memory_full_info', 'memory_info', 'memory_percent', 'name', 'nice', 'num_ctx_switches', 'num_fds', 'num_threads',
    'open_files', 'pid', 'ppid', 'status', 'terminal', 'threads', 'uids', 'username'
]
#: Usage: GNUPLOT_PLT.format(name=dat_file_name)
GNUPLOT_PLT = """
set grid
set title "Memory and CPU Usage." font ",14"
set xlabel "Elapsed Time (s)"
# set mxtics 5
# set xrange [0:3000]
# set xtics
# set format x ""

#set logscale y
set ylabel "Memory Usage (Mb)"
# set yrange [0:500]
# set ytics 20
# set mytics 2
# set ytics 8,35,3

#set logscale y2
set y2label "CPU Usage (%), Page Faults (10,000/s)"
# set y2range [0:200]
set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

set terminal svg size 1000,700 # choose the file format
set output "{name}.svg" # choose the output device

# set key off

{labels}

#set key title "Window Length"
#  lw 2 pointsize 2

plot "{name}.dat" using 1:($2 / 1024**2) axes x1y1 title "RSS (Mb), left axis" with lines lt 1 lw 2, \\
    "{name}.dat" using 1:($3 / 10000) axes x1y2 title "Page Faults (10,000/s), right axis" with lines lt 3 lw 1, \\
    "{name}.dat" using 1:5 axes x1y2 title "Mean CPU (%), right axis" with lines lt 2 lw 1, \\
    "{name}.dat" using 1:6 axes x1y2 title "Instantaneous CPU (%), right axis" with lines lt 7 lw 1

reset
"""


def parse_timestamp(s: str) -> datetime.datetime:
    """Read a string such as '2019-06-07 11:57:58.390921' and return a datetime."""
    return datetime.datetime.strptime(s, DATETIME_NOW_FORMAT)


def extract_json(istream: typing.TextIO) -> typing.List[typing.Dict[str, typing.Any]]:
    """Reads a log file and returns the JSON as a list of dicts. Non-matching lines are ignored."""
    ret = []
    for line in istream.readlines():
        m = RE_LOG_LINE.match(line)
        if m:
            log_dict = json.loads(m.group(2))
            if KEY_TIMESTAMP in log_dict:
                log_dict[KEY_TIMESTAMP] = parse_timestamp(log_dict[KEY_TIMESTAMP])
            ret.append(log_dict)
    return ret


def extract_labels_from_json(json_data: typing.List[typing.Dict[str, typing.Any]]) -> typing.List[typing.Dict[str, typing.Any]]:
    """Returns a list of dicts of JSON data where 'label' is a key'."""
    return [v for v in json_data if KEY_LABEL in v]


def extract_json_as_table(json_data: typing.List[typing.Dict[int, typing.Any]]) \
        -> typing.Tuple[
            typing.Dict[str, typing.List[typing.List[str]]],
            typing.Dict[str, float],
            typing.Dict[str, float],
            typing.Dict[str, float],
            typing.Dict[str, float],
        ]:
    """Create a table from JSON suitable for a Gnuplot ``.dat`` file."""
    HEADER = [
            f'{"#t(s)":12}',
            f'{"RSS":>12}',
            f'{"PageFaults/s":>12}',
            f'{"User":>12}',
            f'{"Mean_CPU%":>12}',
            f'{"Inst_CPU%":>12}',
            f'{"Timestamp":<26}',
            f'{"PID":>6}',
            f'{"Label"}',
        ]
    ret = {}
    prev_cpu = {}
    prev_elapsed_time = {}
    prev_page_faults = {}
    t_min = {}
    t_max = {}
    rss_min = {}
    rss_max = {}
    for record in json_data:
        if record[KEY_PROCESS_ID] not in ret:
            ret[record[KEY_PROCESS_ID]] = [HEADER[:]]
            prev_cpu[record[KEY_PROCESS_ID]] = 0.0
            prev_elapsed_time[record[KEY_PROCESS_ID]] = 0.0
            prev_page_faults[record[KEY_PROCESS_ID]] = 0
            t_min[record[KEY_PROCESS_ID]] = sys.float_info.max
            t_max[record[KEY_PROCESS_ID]] = sys.float_info.min
            rss_min[record[KEY_PROCESS_ID]] = sys.float_info.max
            rss_max[record[KEY_PROCESS_ID]] = sys.float_info.min
        mean_cpu_user = record["cpu_times"]["user"] / record[KEY_ELAPSED_TIME]
        inst_cpu_user = (record["cpu_times"]["user"] - prev_cpu[record[KEY_PROCESS_ID]]) / (record[KEY_ELAPSED_TIME] - prev_elapsed_time[record[KEY_PROCESS_ID]])
        # record["memory_info"]["pfaults"] is the cumulative total.
        inst_page_faults = (record["memory_info"]["pfaults"] - prev_page_faults[record[KEY_PROCESS_ID]]) / (record[KEY_ELAPSED_TIME] - prev_elapsed_time[record[KEY_PROCESS_ID]])
        label = record[KEY_LABEL] if KEY_LABEL in record else ''
        ret[record[KEY_PROCESS_ID]].append(
            [
                f'{record[KEY_ELAPSED_TIME]:<12.1f}',
                f'{record["memory_info"]["rss"]:12d}',
                f'{inst_page_faults:12f}',
                f'{record["cpu_times"]["user"]:12.1f}',
                f'{mean_cpu_user:12.1%}',
                f'{inst_cpu_user:12.1%}',
                f'{record["timestamp"].strftime("%Y-%m-%dT%H:%M:%S.%f"):26}',
                f'{record[KEY_PROCESS_ID]:6d}',
                f'# {label}'
            ]
        )
        prev_cpu[record[KEY_PROCESS_ID]] = record["cpu_times"]["user"]
        prev_elapsed_time[record[KEY_PROCESS_ID]] = record[KEY_ELAPSED_TIME]
        prev_page_faults[record[KEY_PROCESS_ID]] = record["memory_info"]["pfaults"]
        t_min[record[KEY_PROCESS_ID]] = min(record[KEY_ELAPSED_TIME], t_min[record[KEY_PROCESS_ID]])
        t_max[record[KEY_PROCESS_ID]] = max(record[KEY_ELAPSED_TIME], t_max[record[KEY_PROCESS_ID]])
        rss_min[record[KEY_PROCESS_ID]] = min(record["memory_info"]["rss"], rss_min[record[KEY_PROCESS_ID]])
        rss_max[record[KEY_PROCESS_ID]] = max(record["memory_info"]["rss"], rss_max[record[KEY_PROCESS_ID]])
    return ret, t_min, t_max, rss_min, rss_max


def invoke_gnuplot(log_path: str, gnuplot_dir: str) -> int:
    """Reads a log file, extracts the data, writes it out to gnuplot_dir and invokes gnuplot on it."""
    os.makedirs(gnuplot_dir, exist_ok=True)
    ret = gnuplot.write_test_file(gnuplot_dir, 'svg')
    if ret:
        logger.error(f'Can not write gnuplot test file with error code {ret}')
        return ret
    with open(log_path) as instream:
        json_data = extract_json(instream)
    table, _t_min, _t_max, rss_min, rss_max = extract_json_as_table(json_data)
    for pid in table:
        log_name = f'{os.path.basename(log_path)}_{pid}'
        labels = extract_labels_from_json(json_data)
        label_lines = []
        y_value = (0.5 * (rss_max[pid] - rss_min[pid])) / 1024**2
        for label_dict in labels:
            t_value = label_dict[KEY_ELAPSED_TIME]
            label_lines.append(f'set arrow from {t_value},{y_value} to {t_value},0 lt -1 lw 1')
            label_lines.append(
                f'set label "{label_dict[KEY_LABEL]}" at {t_value},{y_value * 1.025}'
                f' left font ",10" rotate by 90 noenhanced front'
            )
        ret = gnuplot.invoke_gnuplot(
            gnuplot_dir, log_name, table[pid], GNUPLOT_PLT.format(name=log_name, labels='\n'.join(label_lines))
        )
        if ret:
            break
    return ret


# Message passing
process_queue = queue.Queue()


def add_message_to_queue(msg: str) -> None:
    """Adds a message onto the queue."""
    process_queue.put(msg)


class ProcessLoggingThread(threading.Thread):
    """Thread that regularly logs out process parameters."""
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        if name is None:
            name = 'ProcMon'
        super().__init__(group=group, target=target, name=name, daemon=daemon)
        self.args = args
        self.kwargs = kwargs
        self._interval = args[0] if len(args) else kwargs['interval']
        self._process = psutil.Process()
        self._run = True

    def _get_process_data(self, **kwargs):
        ret = {
            KEY_TIMESTAMP: datetime.datetime.now().strftime(DATETIME_NOW_FORMAT),
        }
        ret.update(
            {
                k: getattr(self._process, k)()._asdict() for k in ('memory_info', 'cpu_times')
            }
        )
        ret[KEY_ELAPSED_TIME] = time.time() - self._process.create_time()
        ret[KEY_PROCESS_ID] = self._process.pid
        # WARNING: This is super verbose and leaks information such as user, environment etc. into the log file.
        # ret.update(self._process.as_dict())
        # kwargs trump everything
        ret.update(kwargs)
        return ret

    def _write_to_log(self, prefix: str) -> None:
        """Write process data to log flushing message queue if necessary."""
        if self._run:
            if process_queue.empty():
                logger.info(f'{prefix} {json.dumps(self._get_process_data())}')
            else:
                while not process_queue.empty():
                    msg = process_queue.get()
                    logger.info(f'{prefix} {json.dumps(self._get_process_data(label=msg))}')

    def run(self) -> None:
        """thread.run(). Write to log then sleep."""
        self._write_to_log(LOGGER_PREFIX_START)
        while self._run:
            time.sleep(self._interval)
            self._write_to_log(LOGGER_PREFIX)

    def join(self, *args, **kwargs):
        """thread.join(). Write to log last time."""
        self._write_to_log(LOGGER_PREFIX_STOP)
        self._run = False
        super().join(*args, **kwargs)


@contextlib.contextmanager
def log_process(*args, **kwargs):
    """Context manager to log process data at regular intervals."""
    process_thread = ProcessLoggingThread(args=args, kwargs=kwargs)
    process_thread.start()
    try:
        yield
    finally:
        process_thread.join()


def add_process_logger_to_argument_parser(parser: argparse.ArgumentParser) -> None:
    """Add a ``--log-process`` option to the argument parser."""
    parser.add_argument(
        '--log-process', default=0.0, type=float,
        help='Writes process data such as memory usage as a log INFO line every LOG_PROCESS seconds.'
             ' If 0.0 no process data is logged. [default: %(default)s]',
    )


def main() -> int:
    """Main CLI entry point. For testing."""
    parser = argparse.ArgumentParser(
        prog='process.py',
        description="""Reads an annotated log of a process and writes a Gnuplot graph.""",
    )
    parser.add_argument('path_in', type=str, help='Input path.', nargs='?')
    parser.add_argument('path_out', type=str, help='Output path.', nargs='?')
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(filename)s - %(process)5d - (%(threadName)-10s) - %(levelname)-8s - %(message)s',
    )
    args = parser.parse_args()
    if args.path_in and args.path_out:
        logger.info(f'Extracting data from a log at {args.path_in} to {args.path_out}')
        invoke_gnuplot(args.path_in, args.path_out)
    else:
        logger.info('Demonstration of logging a process')
        with log_process(0.1):
            for i in range(8):
                size = random.randint(128, 128 + 256) * 1024 ** 2
                add_message_to_queue(f'String of {size:,d} bytes')
                s = ' ' * (size)
                # time.sleep(.8)
                time.sleep(0.5 + random.random())
                del s
                # time.sleep(.4)
                time.sleep(0.25 + random.random() / 2)
    return 0


if __name__ == '__main__':
    sys.exit(main())
