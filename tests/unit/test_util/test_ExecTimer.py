import time

import pytest

from TotalDepth.util import ExecTimer


def test_timer():
    t = ExecTimer.Timer('description')
    assert not t.stopped
    SLEEP = 0.2
    time.sleep(SLEEP)
    t.stop()
    assert abs(t.elapsed_perf_counter - SLEEP) < 0.05
