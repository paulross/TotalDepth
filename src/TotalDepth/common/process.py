"""
Gathers and logs process information such as memory usage.

"""
import logging
import sys
import threading
import time

import psutil


logger = logging.getLogger(__file__)


class ProcessLoggingThread(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name, daemon=daemon)
        self.args = args
        self.kwargs = kwargs
        self._interval = args[0] if len(args) else kwargs['interval']
        self._process = psutil.Process()
        self._run = True

    def run(self):
        logger.debug(f'ProcessLoggingThread: running with args {self.args} and kwargs {self.kwargs}')
        while self._run:
            logger.info(f'TEST: {self._process.memory_info()}')
            time.sleep(self._interval)

    def join(self, *args, **kwargs):
        logger.debug('ProcessLoggingThread: join()')
        self._run = False
        super().join(*args, **kwargs)





logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s',
)


def main() -> int:
    process_thread = ProcessLoggingThread(args=(1.0,))
    process_thread.start()
    for i in range(3):
        time.sleep(2)
    process_thread.join()
    return 0


if __name__ == '__main__':
    sys.exit(main())
