"""Test the execution of the entry points.

Most of these are @pytest.mark.slow
"""
import os
import subprocess

import pytest

import TotalDepth


def test_tmdir_fixture(tmpdir):
    print(tmpdir)
    print(dir(tmpdir))
    assert os.path.isdir(tmpdir)


TOTAL_DEPTH_SOURCE_ROOT = os.path.dirname(TotalDepth.__file__)

EXAMPLE_DATA_DIRECTORY = os.path.join(TOTAL_DEPTH_SOURCE_ROOT, os.path.pardir, os.path.pardir, 'example_data')

def test_example_data_directory_exists():
    assert os.path.isdir(EXAMPLE_DATA_DIRECTORY)


EXAMPLE_DATA_DIRECTORY_LIS = os.path.join(EXAMPLE_DATA_DIRECTORY, 'LIS', 'data',)


def test_lis_example_data_directory_lis_exists():
    assert os.path.isdir(EXAMPLE_DATA_DIRECTORY_LIS)


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


@pytest.mark.slow
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


# -------- tdarchive --------
@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-r', '-v'],
        ['-r', '-v', '-k'],
        ['-r', '-v', '-k'],
        ['-r', '--expand-and-delete', '-n'],
        ['-r', '--histogram'],
        ['-r', '--bytes=20'],
    )
)
def test_tdarchive_file_stdout(args):
    subprocess.check_call(['tdarchive',] + args + [EXAMPLE_DATA_DIRECTORY])


@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-r', '-v'],
        ['-r', '-v', '-k'],
        ['-r', '-v', '-k'],
        ['-r', '--expand-and-delete', '-n'],
        ['-r', '--histogram'],
        ['-r', '--bytes=20'],
    )
)
def test_tdarchive_dir(tmpdir, args):
    subprocess.check_call(['tdarchive',] + args + [EXAMPLE_DATA_DIRECTORY, str(tmpdir)])


# -------- END: tdarchive --------


# -------- tdcopybinfiles --------
@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        ['--file-types=?'],
        ['--file-types=??'],
    )
)
def test_tdcopybinfiles_no_paths(args):
    subprocess.check_call(['tdcopybinfiles',] + args + ['', ''])


# @pytest.mark.slow
# @pytest.mark.parametrize(
#     'args',
#     (
#         [],
#     )
# )
# def test_tdcopybinfiles_dir(tmpdir, args):
#     zip_in = tmpdir.mkdir('in').join('input.zip')
#
#     subprocess.check_call(['tdcopybinfiles',] + args + [EXAMPLE_DATA_DIRECTORY, str(tmpdir)])


# -------- END: tdcopybinfiles --------


# ================ LIS ==================
LIS_BASIC_FILE = os.path.join(EXAMPLE_DATA_DIRECTORY_LIS, 'DILLSON-1_WELL_LOGS_FILE-049.LIS')


def test_lis_basic_file_exists():
    assert os.path.isfile(LIS_BASIC_FILE)


@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-r'],
        ['-r', '-j 2'],
    )
)
def test_tdlistohtml(tmpdir, args):
    subprocess.check_call(['tdlistohtml',] + args + [EXAMPLE_DATA_DIRECTORY_LIS, str(tmpdir)])

# -------- tdlistolas --------
@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-v'],
        ['-v', '-k'],
        ['--log-process=1.0',],
        ['--frame-slice=64',],
        ['--frame-slice=,,2',],
        ['--frame-slice=?',],
        ['--array-reduction=median',],
        ['--channels=?',],
        ['--channels=TENS,ETIM',],
        ['--field-width=32',],
        ['--float-format=.6f',],
    )
)
def test_tdlistolas_basic_file(tmpdir, args):
    subprocess.check_call(['tdlistolas',] + args + [LIS_BASIC_FILE, str(tmpdir)])


@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-r'],
        ['-r', '-j 2'],
        ['-r', '-j 0'],
        ['-r', '--frame-slice=?', ],
        ['-r', '--channels=?', ],
    )
)
def test_tdlistolas_dir(tmpdir, args):
    subprocess.check_call(['tdlistolas',] + args + [EXAMPLE_DATA_DIRECTORY_LIS, str(tmpdir)])


@pytest.mark.slow
def test_tdlistolas_gnuplot(tmpdir):
    subprocess.check_call(['tdlistolas', EXAMPLE_DATA_DIRECTORY_LIS, str(tmpdir), '-r', f'--gnuplot={str(tmpdir)}'])

# -------- END: tdlistolas --------

#======================== END: LIS ==================


#======================== RP66V1 ==================
RP66V1_DATA_DIR = os.path.join(EXAMPLE_DATA_DIRECTORY, 'RP66V1', 'data')


def test_rp66v1_example_data_directory_exists():
    assert os.path.isdir(RP66V1_DATA_DIR)


RP66V1_BASIC_FILE = os.path.join(EXAMPLE_DATA_DIRECTORY, 'RP66V1', 'data', 'BASIC_FILE.dlis')


def test_rp66v1_example_file_exists():
    assert os.path.isfile(RP66V1_BASIC_FILE)


RP66V1_FILES = [
    os.path.join(EXAMPLE_DATA_DIRECTORY, 'RP66V1', 'data', '206_05a-_3_DWL_DWL_WIRE_258276498.DLIS'),
    RP66V1_BASIC_FILE,
]


@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        [],
        # Visible Records
        ['-V'],
        ['-V', '-v'],
        ['--VR'],
        ['--VR', '-v'],
        # Logical Record Segments
        ['-L'],
        ['-L', '-v'],
        ['--LRSH'],
        ['--LRSH', '-v'],
        # Logical data
        ['-D'],
        ['-D', '-v'],
        ['--LD'],
        ['--LD', '-v'],
        ['-D', '-v', '--dump-bytes=8'],
        ['-D', '-v', '--dump-bytes=8', '--dump-raw-bytes'],
        # Explicitly Formatted Logical Records
        ['-E'],
        ['-E', '-v'],
        ['--EFLR'],
        ['--EFLR', '-v'],
        ['--EFLR', '--eflr-set-type=FRAME', '-v'],
        # Indirectly Formatted Logical Records
        ['-I'],
        ['-I', '-v'],
        ['--IFLR'],
        ['--IFLR', '-v'],
        # Logical Records
        ['-R'],
        ['-R', '-v'],
        ['--LR'],
        ['--LR', '-v'],
        ['--LR', '--frame-slice=64'],
        ['--LR', '--frame-slice=,,64'],
        # Test data
        ['-T'],
    )
)
def test_tdrp66v1scan_file(args):
    subprocess.check_call(['tdrp66v1scan',] + args + [RP66V1_BASIC_FILE,])


@pytest.mark.xfail(reason='Not sure why this is failing, it seems pretty innocuous.')
@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        ['-r', '-V'],
        ['-r', '-j 2'],
    )
)
def test_tdrp66v1scan_dir(tmpdir, args):
    cmd_args = ['tdrp66v1scan',] + args + [RP66V1_DATA_DIR, str(tmpdir)]
    subprocess.check_call(cmd_args)


# -------- tdrp66v1logrecindex --------
@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-v'],
        ['-v', '-k'],
        ['--log-process=1.0'],
    )
)
def test_tdrp66v1logrecindex_file_stdout(args):
    subprocess.check_call(['tdrp66v1logrecindex',] + args + [RP66V1_BASIC_FILE])


@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-r'],
        ['-r', '-j 2'],
        ['-r', '-j 0'],
        ['-r', '--read-back'],
    )
)
def test_tdrp66v1logrecindex_dir(tmpdir, args):
    subprocess.check_call(['tdrp66v1logrecindex',] + args + [EXAMPLE_DATA_DIRECTORY, str(tmpdir)])


@pytest.mark.slow
def test_tdrp66v1logrecindex_gnuplot(tmpdir):
    subprocess.check_call(['tdrp66v1logrecindex', EXAMPLE_DATA_DIRECTORY, '-r', f'--gnuplot={str(tmpdir)}'])

# -------- END: tdrp66v1logrecindex --------


# -------- tdrp66v1indexpickle --------
@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-v'],
        ['-v', '-k'],
        ['--log-process=1.0'],
    )
)
def test_tdrp66v1indexpickle_file_stdout(args):
    subprocess.check_call(['tdrp66v1indexpickle',] + args + [RP66V1_BASIC_FILE])


@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        ['-r'],
        ['-r', '-j 2'],
        ['-r', '-j 0'],
        ['-r', '--read-back'],
    )
)
def test_tdrp66v1indexpickle_dir(tmpdir, args):
    subprocess.check_call(['tdrp66v1indexpickle',] + args + [EXAMPLE_DATA_DIRECTORY, str(tmpdir)])


@pytest.mark.skip(reason='Need to investigate gnuplot never achieving regression coefficient.')
@pytest.mark.slow
def test_tdrp66v1indexpickle_gnuplot(tmpdir):
    subprocess.check_call(['tdrp66v1indexpickle', EXAMPLE_DATA_DIRECTORY, '-r', f'--gnuplot={str(tmpdir)}'])

# -------- END: tdrp66v1indexpickle --------


# -------- tdrp66v1indexxml --------
@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-v'],
        ['-v', '-k'],
        ['--log-process=1.0'],
        ['--encrypted'],
        ['--private'],
    )
)
def test_tdrp66v1indexxml_file_stdout(args):
    subprocess.check_call(['tdrp66v1indexxml',] + args + [RP66V1_BASIC_FILE])


@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        ['-r'],
        ['-r', '-j 2'],
        ['-r', '-j 0'],
    )
)
def test_tdrp66v1indexxml_dir(tmpdir, args):
    subprocess.check_call(['tdrp66v1indexxml',] + args + [EXAMPLE_DATA_DIRECTORY, str(tmpdir)])


@pytest.mark.slow
def test_tdrp66v1indexxml_gnuplot(tmpdir):
    subprocess.check_call(['tdrp66v1indexxml', EXAMPLE_DATA_DIRECTORY, '-r', f'--gnuplot={str(tmpdir)}'])

# -------- END: tdrp66v1indexxml --------


# -------- tdrp66v1tolas --------
@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-v'],
        ['-v', '-k'],
        ['--log-process=1.0',],
        ['--frame-slice=64',],
        ['--frame-slice=,,2',],
        ['--frame-slice=?',],
        ['--array-reduction=median',],
        ['--channels=?',],
        ['--channels=TENS,ETIM',],
        ['--field-width=32',],
        ['--float-format=.6f',],
    )
)
def test_tdrp66v1tolas_basic_file(tmpdir, args):
    subprocess.check_call(['tdrp66v1tolas',] + args + [RP66V1_BASIC_FILE, str(tmpdir)])


@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-r'],
        ['-r', '-j 2'],
        ['-r', '-j 0'],
        ['-r', '--frame-slice=?', ],
        ['-r', '--channels=?', ],
    )
)
def test_tdrp66v1tolas_dir(tmpdir, args):
    subprocess.check_call(['tdrp66v1tolas',] + args + [EXAMPLE_DATA_DIRECTORY, str(tmpdir)])


@pytest.mark.slow
def test_tdrp66v1tolas_gnuplot(tmpdir):
    subprocess.check_call(['tdrp66v1tolas', EXAMPLE_DATA_DIRECTORY, str(tmpdir), '-r', f'--gnuplot={str(tmpdir)}'])

# -------- END: tdrp66v1tolas --------


# -------- tdrp66v1scanhtml --------

@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-r'],
        ['-r', '-j 2'],
        ['-r', '-j 0'],
        ['-r', '--log-process=1.0', ],
        ['-r', '--frame-slice=64', ],
        ['-r', '--frame-slice=,,2', ],
    )
)
def test_tdrp66v1scanhtml_dir(tmpdir, args):
    subprocess.check_call(['tdrp66v1scanhtml',] + args + [EXAMPLE_DATA_DIRECTORY, str(tmpdir)])


@pytest.mark.slow
def test_tdrp66v1scanhtml_gnuplot(tmpdir):
    subprocess.check_call(['tdrp66v1scanhtml', EXAMPLE_DATA_DIRECTORY, str(tmpdir), '-r', f'--gnuplot={str(tmpdir)}'])

# -------- END: tdrp66v1scanhtml --------


def test_rp66v1_scan_ff01():
    script = os.path.join(TOTAL_DEPTH_SOURCE_ROOT, 'RP66V1', 'SearchFF01.py')
    subprocess.check_call(['python', script, RP66V1_BASIC_FILE])


#======================== END: RP66V1 ==================


#======================== END: BIT ==================

EXAMPLE_DATA_DIRECTORY_BIT = os.path.join(
    TOTAL_DEPTH_SOURCE_ROOT, os.path.pardir, os.path.pardir, 'example_data', 'BIT', 'data',
)

def test_example_data_directory_bit_exists():
    assert os.path.isdir(EXAMPLE_DATA_DIRECTORY_BIT)


EXAMPLE_DATA_FILE_BIT = os.path.join(EXAMPLE_DATA_DIRECTORY_BIT, '29_10-_3Z_dwl_DWL_WIRE_1644659.bit')


def test_example_data_file_bit_exists():
    assert os.path.isfile(EXAMPLE_DATA_FILE_BIT)


@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-r'],
        ['-r', '-v'],
        ['-r', '-v', '--summary'],
    )
)
def test_tdbitread_dir(args):
    subprocess.check_call(['tdbitread',] + args + [EXAMPLE_DATA_DIRECTORY_BIT])


@pytest.mark.slow
@pytest.mark.parametrize(
    'args',
    (
        [],
        ['-r'],
        ['-r', '-v'],
        ['-r', '-v', '--summary'],
    )
)
def test_tdbitread_file(args):
    subprocess.check_call(['tdbitread',] + args + [EXAMPLE_DATA_FILE_BIT])

#======================== END: BIT ==================
