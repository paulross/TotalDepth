"""Test the execution of the entry points.

Most of these are @pytest.mark.slow
"""
import os
import subprocess

import pytest

import TotalDepth


EXAMPLE_DATA_DIRECTORY = os.path.join(
    os.path.dirname(TotalDepth.__file__), os.path.pardir, os.path.pardir, 'example_data'
)


def test_example_data_directory_exists():
    assert os.path.isdir(EXAMPLE_DATA_DIRECTORY)


@pytest.mark.slow
@pytest.mark.parametrize(
    'entry_point',
    (
        TotalDepth.entry_points_console_scripts_dict.keys()
    )
)
def test_entry_point_help_h(entry_point):
    subprocess.check_call([entry_point, '-h'])


@pytest.mark.slow
@pytest.mark.parametrize(
    'entry_point',
    (
        TotalDepth.entry_points_console_scripts_dict.keys()
    )
)
def test_entry_point_help_help(entry_point):
    subprocess.check_call([entry_point, '--help'])


@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-r'],
        ['-r', '-n'],
    )
)
def test_tddetif(tmpdir, args):
    subprocess.check_call(['tddetif',] + args + [EXAMPLE_DATA_DIRECTORY, str(tmpdir)])


@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-r'],
        ['-r', '-j 2'],
    )
)
def test_tdlistohtml(tmpdir, args):
    subprocess.check_call(['tdlistohtml',] + args + [EXAMPLE_DATA_DIRECTORY, str(tmpdir)])


#======================== RP66V1 ==================
RP66V1_DATA_DIR = [
    os.path.join(EXAMPLE_DATA_DIRECTORY, 'RP66V1', 'data')
]

RP66V1_FILES = [
    os.path.join(EXAMPLE_DATA_DIRECTORY, 'RP66V1', 'data', '206_05a-_3_DWL_DWL_WIRE_258276498.DLIS')
]


@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-V'],
        ['-VR'],
    )
)
def test_tdrp66v1scan_file(args):
    subprocess.check_call(['tdrp66v1scan',] + args + [RP66V1_FILES[0],])


@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-r'],
        ['-r', '-j 2'],
    )
)
def test_tdrp66v1scan_dir(args):
    subprocess.check_call(['tdrp66v1scan',] + args + [RP66V1_DATA_DIR,])


@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-r'],
        ['-r', '-j 2'],
    )
)
def test_tdrp66v1scanhtml(tmpdir, args):
    subprocess.check_call(['tdrp66v1scanhtml',] + args + [EXAMPLE_DATA_DIRECTORY, str(tmpdir)])



#======================== END: RP66V1 ==================

def test(tmpdir):
    print(tmpdir)
    print(dir(tmpdir))
    assert 1
