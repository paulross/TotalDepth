import datetime
import io
import pprint

import pytest


from TotalDepth.common import process



@pytest.mark.parametrize(
    'line, expected',
    (
        (
            '2019-10-14 17:44:46,955 - 24098 - INFO     - process.py       - ProcessLoggingThread-JSON-START {"timestamp": "2019-10-14 17:44:46.955519"}',
            ('-START', '{"timestamp": "2019-10-14 17:44:46.955519"}'),
        ),
        (
            '2019-10-14 17:44:46,955 - 24098 - INFO     - process.py       - ProcessLoggingThread-JSON {"timestamp": "2019-10-14 17:44:46.955519"}',
            (None, '{"timestamp": "2019-10-14 17:44:46.955519"}'),
        ),
        (
            '2019-10-14 17:44:46,955 - 24098 - INFO     - process.py       - ProcessLoggingThread-JSON-STOP {"timestamp": "2019-10-14 17:44:46.955519"}',
            ('-STOP', '{"timestamp": "2019-10-14 17:44:46.955519"}'),
        ),
    )
)
def test_re_log_line(line, expected):
    match = process.RE_LOG_LINE.match(line)
    assert match is not None
    assert match.groups() == expected


EXAMPLE_PROCESS_LOG = """Cmd: /Users/engun/venvs/TotalDepth37_00/bin/tdrp66v1scanhtml -r --frame-slice=1/64 --log-process=1.0 data/by_type/RP66V1/WAPIMS/2006-2008/W002844/ data/HTML/W002844_I
gnuplot version: "b'gnuplot 5.2 patchlevel 6'"
args: Namespace(encrypted=False, frame_slice='1/64', gnuplot=None, keep_going=False, log_level=20, log_process=1.0, path_in='data/by_type/RP66V1/WAPIMS/2006-2008/W002844/', path_out='data/HTML/W002844_I', recurse=True, verbose=0)
2019-10-14 17:44:46,955 - 24098 - INFO     - process.py       - ProcessLoggingThread-JSON-START {"pid": 24098, "timestamp": "2019-10-14 17:44:46.955519", "memory_info": {"rss": 28475392, "vms": 4595617792, "pfaults": 10272, "pageins": 0}, "cpu_times": {"user": 0.3174768, "system": 0.0577991, "children_user": 0.0, "children_system": 0.0}, "elapsed_time": 0.23358798027038574}
2019-10-14 17:44:46,955 - 24098 - INFO     - ScanHTML.py      - scan_dir_or_file(): "data/by_type/RP66V1/WAPIMS/2006-2008/W002844" to "data/HTML/W002844_I" recurse: True
2019-10-14 17:44:46,963 - 24098 - INFO     - ScanHTML.py      - ScanFileHTML.scan_a_single_file(): "data/by_type/RP66V1/WAPIMS/2006-2008/W002844/WIRELINE/S1R2_CMR_MDT-GR/MDT_OFA_CMR_083PTP.DLIS"
2019-10-14 17:44:47,960 - 24098 - INFO     - process.py       - ProcessLoggingThread-JSON {"pid": 24098, "timestamp": "2019-10-14 17:44:47.960414", "memory_info": {"rss": 55967744, "vms": 4621426688, "pfaults": 18940, "pageins": 8}, "cpu_times": {"user": 1.291334912, "system": 0.07683248, "children_user": 0.0, "children_system": 0.0}, "elapsed_time": 1.2385711669921875}
2019-10-14 17:44:48,943 - 24098 - INFO     - ScanHTML.py      - ScanFileHTML.scan_a_single_file(): "data/by_type/RP66V1/WAPIMS/2006-2008/W002844/WIRELINE/S1R2_CMR_MDT-GR/MDT_OFA_CMR_077PTP.DLIS"
2019-10-14 17:44:48,964 - 24098 - INFO     - process.py       - ProcessLoggingThread-JSON {"pid": 24098, "timestamp": "2019-10-14 17:44:48.963983", "memory_info": {"rss": 41500672, "vms": 4606386176, "pfaults": 19427, "pageins": 61}, "cpu_times": {"user": 2.2686848, "system": 0.087920424, "children_user": 0.0, "children_system": 0.0}, "elapsed_time": 2.242030143737793}
2019-10-14 17:44:50,013 - 24098 - INFO     - process.py       - ProcessLoggingThread-JSON {"pid": 24098, "timestamp": "2019-10-14 17:44:50.012988", "memory_info": {"rss": 56074240, "vms": 4620902400, "pfaults": 23014, "pageins": 61}, "cpu_times": {"user": 3.30531712, "system": 0.099596592, "children_user": 0.0, "children_system": 0.0}, "elapsed_time": 3.2910971641540527}
2019-10-14 17:44:50,878 - 24098 - INFO     - ScanHTML.py      - ScanFileHTML.scan_a_single_file(): "data/by_type/RP66V1/WAPIMS/2006-2008/W002844/WIRELINE/S1R2_CMR_MDT-GR/MDT_OFA_CMR_082PTP.DLIS"
2019-10-14 17:44:51,019 - 24098 - INFO     - process.py       - ProcessLoggingThread-JSON {"pid": 24098, "timestamp": "2019-10-14 17:44:51.019315", "memory_info": {"rss": 46026752, "vms": 4610617344, "pfaults": 23347, "pageins": 61}, "cpu_times": {"user": 4.29572096, "system": 0.108004144, "children_user": 0.0, "children_system": 0.0}, "elapsed_time": 4.2973692417144775}
2019-10-14 17:44:52,024 - 24098 - INFO     - process.py       - ProcessLoggingThread-JSON-STOP {"pid": 24098, "timestamp": "2019-10-14 17:44:52.024755", "memory_info": {"rss": 56565760, "vms": 4621070336, "pfaults": 25993, "pageins": 61}, "cpu_times": {"user": 5.269735424, "system": 0.116896328, "children_user": 0.0, "children_system": 0.0}, "elapsed_time": 5.3028600215911865}
Other log lines
that will be ignored.
"""

EXPECTED_EXAMPLE_PROCESS_LOG = [
    {'cpu_times': {'children_system': 0.0,
                   'children_user': 0.0,
                   'system': 0.0577991,
                   'user': 0.3174768},
     'elapsed_time': 0.23358798027038574,
     'memory_info': {'pageins': 0,
                     'pfaults': 10272,
                     'rss': 28475392,
                     'vms': 4595617792},
     'pid': 24098,
     'timestamp': datetime.datetime(2019, 10, 14, 17, 44, 46, 955519)},
    {'cpu_times': {'children_system': 0.0,
                   'children_user': 0.0,
                   'system': 0.07683248,
                   'user': 1.291334912},
     'elapsed_time': 1.2385711669921875,
     'memory_info': {'pageins': 8,
                     'pfaults': 18940,
                     'rss': 55967744,
                     'vms': 4621426688},
     'pid': 24098,
     'timestamp': datetime.datetime(2019, 10, 14, 17, 44, 47, 960414)},
    {'cpu_times': {'children_system': 0.0,
                   'children_user': 0.0,
                   'system': 0.087920424,
                   'user': 2.2686848},
     'elapsed_time': 2.242030143737793,
     'memory_info': {'pageins': 61,
                     'pfaults': 19427,
                     'rss': 41500672,
                     'vms': 4606386176},
     'pid': 24098,
     'timestamp': datetime.datetime(2019, 10, 14, 17, 44, 48, 963983)},
    {'cpu_times': {'children_system': 0.0,
                   'children_user': 0.0,
                   'system': 0.099596592,
                   'user': 3.30531712},
     'elapsed_time': 3.2910971641540527,
     'memory_info': {'pageins': 61,
                     'pfaults': 23014,
                     'rss': 56074240,
                     'vms': 4620902400},
     'pid': 24098,
     'timestamp': datetime.datetime(2019, 10, 14, 17, 44, 50, 12988)},
    {'cpu_times': {'children_system': 0.0,
                   'children_user': 0.0,
                   'system': 0.108004144,
                   'user': 4.29572096},
     'elapsed_time': 4.2973692417144775,
     'memory_info': {'pageins': 61,
                     'pfaults': 23347,
                     'rss': 46026752,
                     'vms': 4610617344},
     'pid': 24098,
     'timestamp': datetime.datetime(2019, 10, 14, 17, 44, 51, 19315)},
    {'cpu_times': {'children_system': 0.0,
                   'children_user': 0.0,
                   'system': 0.116896328,
                   'user': 5.269735424},
     'elapsed_time': 5.3028600215911865,
     'memory_info': {'pageins': 61,
                     'pfaults': 25993,
                     'rss': 56565760,
                     'vms': 4621070336},
     'pid': 24098,
     'timestamp': datetime.datetime(2019, 10, 14, 17, 44, 52, 24755)}
]


def test_extract_json():
    istream = io.StringIO(EXAMPLE_PROCESS_LOG)
    result = process.extract_json(istream)
    # pprint.pprint(result)
    assert result == EXPECTED_EXAMPLE_PROCESS_LOG


def test_extract_json_as_table():
    istream = io.StringIO(EXAMPLE_PROCESS_LOG)
    json_result = process.extract_json(istream)
    table, t_min, t_max, rss_min, rss_max = process.extract_json_as_table(json_result)
    # pprint.pprint(table)
    result = '\n'.join(' '.join(row) for row in table[24098])
    # print(result)
    expected = """#t(s)                 RSS PageFaults/s         User    Mean_CPU%    Inst_CPU% Timestamp                     PID Label
0.2              28475392 43974.865437          0.3       135.9%       135.9% 2019-10-14T17:44:46.955519  24098 # 
1.2              55967744  8625.019915          1.3       104.3%        96.9% 2019-10-14T17:44:47.960414  24098 # 
2.2              41500672   485.321285          2.3       101.2%        97.4% 2019-10-14T17:44:48.963983  24098 # 
3.3              56074240  3419.228639          3.3       100.4%        98.8% 2019-10-14T17:44:50.012988  24098 # 
4.3              46026752   330.924416          4.3       100.0%        98.4% 2019-10-14T17:44:51.019315  24098 # 
5.3              56565760  2631.550734          5.3        99.4%        96.9% 2019-10-14T17:44:52.024755  24098 # """
    assert result == expected
