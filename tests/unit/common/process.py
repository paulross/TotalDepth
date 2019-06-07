import datetime
import io
import pprint

import pytest


from TotalDepth.common import process


EXAMPLE_PROCESS_LOG = """2019-06-07 11:57:54,376 - process.py -  2436 - (Thread-7  ) - INFO     - ProcessLoggingThread-JSON {"timestamp": "2019-06-07 11:57:54.375904", "memory_info": {"rss": 28200960, "vms": 4417945600, "pfaults": 8973, "pageins": 0}, "cpu_times": {"user": 0.211285136, "system": 0.045743112, "children_user": 0.0, "children_system": 0.0}}
2019-06-07 11:57:55,381 - process.py -  2436 - (Thread-7  ) - INFO     - ProcessLoggingThread-JSON {"timestamp": "2019-06-07 11:57:55.380628", "memory_info": {"rss": 45006848, "vms": 4434726912, "pfaults": 13076, "pageins": 0}, "cpu_times": {"user": 0.215715472, "system": 0.05066226, "children_user": 0.0, "children_system": 0.0}}
2019-06-07 11:57:56,386 - process.py -  2436 - (Thread-7  ) - INFO     - ProcessLoggingThread-JSON {"timestamp": "2019-06-07 11:57:56.385703", "memory_info": {"rss": 45015040, "vms": 4434726912, "pfaults": 13078, "pageins": 0}, "cpu_times": {"user": 0.21629352, "system": 0.050763288, "children_user": 0.0, "children_system": 0.0}}
2019-06-07 11:57:57,388 - process.py -  2436 - (Thread-7  ) - INFO     - ProcessLoggingThread-JSON {"timestamp": "2019-06-07 11:57:57.387800", "memory_info": {"rss": 61796352, "vms": 4451508224, "pfaults": 17175, "pageins": 0}, "cpu_times": {"user": 0.2231484, "system": 0.05580152, "children_user": 0.0, "children_system": 0.0}}
2019-06-07 11:57:58,391 - process.py -  2436 - (Thread-7  ) - INFO     - ProcessLoggingThread-JSON {"timestamp": "2019-06-07 11:57:58.390921", "memory_info": {"rss": 61796352, "vms": 4451508224, "pfaults": 17175, "pageins": 0}, "cpu_times": {"user": 0.223692288, "system": 0.055849684, "children_user": 0.0, "children_system": 0.0}}
"""

EXPECTED_EXAMPLE_PROCESS_LOG = [
    {'cpu_times': {'children_system': 0.0,
                   'children_user': 0.0,
                   'system': 0.045743112,
                   'user': 0.211285136},
     'memory_info': {'pageins': 0,
                     'pfaults': 8973,
                     'rss': 28200960,
                     'vms': 4417945600},
     'timestamp': datetime.datetime(2019, 6, 7, 11, 57, 54, 375904)},
    {'cpu_times': {'children_system': 0.0,
                   'children_user': 0.0,
                   'system': 0.05066226,
                   'user': 0.215715472},
     'memory_info': {'pageins': 0,
                     'pfaults': 13076,
                     'rss': 45006848,
                     'vms': 4434726912},
     'timestamp': datetime.datetime(2019, 6, 7, 11, 57, 55, 380628)},
    {'cpu_times': {'children_system': 0.0,
                   'children_user': 0.0,
                   'system': 0.050763288,
                   'user': 0.21629352},
     'memory_info': {'pageins': 0,
                     'pfaults': 13078,
                     'rss': 45015040,
                     'vms': 4434726912},
     'timestamp': datetime.datetime(2019, 6, 7, 11, 57, 56, 385703)},
    {'cpu_times': {'children_system': 0.0,
                   'children_user': 0.0,
                   'system': 0.05580152,
                   'user': 0.2231484},
     'memory_info': {'pageins': 0,
                     'pfaults': 17175,
                     'rss': 61796352,
                     'vms': 4451508224},
     'timestamp': datetime.datetime(2019, 6, 7, 11, 57, 57, 387800)},
    {'cpu_times': {'children_system': 0.0,
                   'children_user': 0.0,
                   'system': 0.055849684,
                   'user': 0.223692288},
     'memory_info': {'pageins': 0,
                     'pfaults': 17175,
                     'rss': 61796352,
                     'vms': 4451508224},
     'timestamp': datetime.datetime(2019, 6, 7, 11, 57, 58, 390921)}
]


def test_extract_json():
    istream = io.StringIO(EXAMPLE_PROCESS_LOG)
    result = process.extract_json(istream)
    # pprint.pprint(result)
    assert result == EXPECTED_EXAMPLE_PROCESS_LOG
