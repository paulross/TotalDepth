"""
Logs process information, such as memory usage, to a log as JSON. Example wit ('memory_info', 'cpu_times')::

    (Thread-7  ) ProcessLoggingThread JSON: {"memory_info": {"rss": 145448960, "vms": 4542902272, "pfaults": 37618, "pageins": 0}, "cpu_times": {"user": 0.28422032, "system": 0.099182912, "children_user": 0.0, "children_system": 0.0}}

There are several DoF here:

- Logging interval in seconds. Or by poke()?
- Logging level, DEBUG, INFO etc.
- Logging verbosity, for example just memory? Or everything about the process (self._process.as_dict())

Also need to add a log parser to, well what?

"""
import contextlib
import datetime
import json
import logging
import re
import sys
import threading
import time
import typing

import psutil


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


def parse_timestamp(s: str) -> datetime.datetime:
    return datetime.datetime.strptime(s, DATETIME_NOW_FORMAT)


def extract_json(istream: typing.TextIO) -> typing.List[typing.Dict[str, typing.Any]]:
    """Reads a log file and returns the JSON as a list of dicts."""
    ret = []
    for line in  istream.readlines():
        m = RE_LOG_LINE.match(line)
        if m:
            log_dict = json.loads(m.group(1))
            if KEY_TIMESTAMP in log_dict:
                log_dict[KEY_TIMESTAMP] = parse_timestamp(log_dict[KEY_TIMESTAMP])
            ret.append(log_dict)
    return ret


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
        # logger.debug(f'ProcessLoggingThread: running with args {self.args} and kwargs {self.kwargs}')
        while self._run:
            logger.info(f'{LOGGER_PREFIX} {json.dumps(self._get_process_data())}')
            time.sleep(self._interval)

    def join(self, *args, **kwargs):
        # logger.debug('ProcessLoggingThread: join()')
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


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(filename)s - %(process)5d - (%(threadName)-10s) - %(levelname)-8s - %(message)s',
)


def main() -> int:
    memory = []
    with log_process(1.0):
        for i in range(8):
            memory.append(' ' * (16 * 1024**2))
            time.sleep(2)
    return 0


if __name__ == '__main__':
    sys.exit(main())
