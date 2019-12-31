"""
Provides gnuplot support to command line tools.
"""
import argparse
import logging
import os
import subprocess
import typing
from functools import reduce


logger = logging.getLogger(__file__)


def add_gnuplot_to_argument_parser(parser: argparse.ArgumentParser) -> None:
    """Adds ``--gnuplot=<DIRECTORY_FOR_GNUPLOT_OUTPUT>`` to the argument parser as ``args.gnuplot``."""
    v = version()
    logger.info(f'gnuplot version: "{v}"')
    print(f'gnuplot version: "{v}"')
    if not v:
        raise ValueError('--gnuplot option is requested but gnuplot is not installed.')
    parser.add_argument('--gnuplot', type=str, help='Directory to write the gnuplot data.')


def version() -> bytes:
    """
    For example: b'gnuplot 5.2 patchlevel 6'
    """
    with subprocess.Popen(['gnuplot', '--version'], stdout=subprocess.PIPE) as proc:
        return proc.stdout.read().strip()


# TODO: Use TotalDepth.common.data_table

def _num_columns(table: typing.Sequence[typing.Sequence[typing.Any]]) -> int:
    """
    Returns the number of columns of the table.
    Will raise a ValueError if the table is uneven.
    """
    num_colums_set = set(len(r) for r in table)
    if len(num_colums_set) != 1:
        raise ValueError(f'Not rectangular: {num_colums_set}.')
    return num_colums_set.pop()


def create_gnuplot_dat(table: typing.Sequence[typing.Sequence[typing.Any]]) -> str:
    """
    Returns a pretty formatted string of the data in the given table suitable for use as a gnuplot ``.dat`` file.
    """
    num_columns = _num_columns(table)
    column_widths = reduce(
        lambda l, rows: [max(l, len(str(r)) + 2) for l, r in zip(l, rows)], table, [0,] * num_columns,
    )
    result: typing.List[str] = []
    for row in table:
        result.append(' '.join(f'{str(row[i]):<{column_widths[i]}}' for i in range(num_columns)))
    return '\n'.join(result)


def invoke_gnuplot(path: str, name: str, table: typing.Sequence[typing.Sequence[typing.Any]], plt: str) -> int:
    """
    Create the plot for name.
    path - the directory to write the data and plot files to.
    name - the name of those files.
    table - the table of values to write to the data file.

    Returns the gnuplot error code.
    """
    logger.info('Writing gnuplot data "{}" in path {}'.format(name, path))
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, f'{name}.dat'), 'w') as outfile:
        outfile.write(create_gnuplot_dat(table))
    with open(os.path.join(path, f'{name}.plt'), 'w') as outfile:
        outfile.write(plt)
    proc = subprocess.Popen(
        args=['gnuplot', '-p', f'{name}.plt'],
        shell=False,
        cwd=path,
    )
    try:
        # Timeout 10 seconds as curve fitting cane take a while.
        # TODO: Make an argument to this function.
        stdout, stderr = proc.communicate(timeout=10)
    except subprocess.TimeoutExpired as err:
        logger.exception(str(err))
        proc.kill()
        stdout, stderr = proc.communicate()
    logging.info(f'gnuplot stdout: {stdout}')
    if proc.returncode or stderr:
        logging.error(f'gnuplot stderr: {stdout}')
    # TODO: Return stderr?
    return proc.returncode


def write_test_file(path: str, typ: str) -> int:
    """Writes out a Gnuplot test file."""
    test_stdin = '\n'.join(
        [
            f'set terminal {typ}',
            f'set output "test.{typ}"',
            'test',
        ]
    )
    proc = subprocess.Popen(
        args=['gnuplot'],
        shell=False,
        cwd=path,
        stdin=subprocess.PIPE,
    )
    try:
        proc.stdin.write(bytes(test_stdin, 'ascii'))
        # proc.stdin.close()
        stdout, stderr = proc.communicate(timeout=1, )
    except subprocess.TimeoutExpired as err:
        logger.exception()
        proc.kill()
        stdout, stderr = proc.communicate()
    logging.info(f'gnuplot stdout: {stdout}')
    if stderr:
        logging.error(f'gnuplot stderr: {stdout}')
    # TODO: Return stderr?
    return proc.returncode

# Gnuplot fragments

PLOT = """set grid
set title "{title}"

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"
"""

X_LOG = """set logscale x
set xlabel "{label}"
# set mxtics 5
# set xrange [0:3000]
# set xtics
# set format x
"""

Y_LOG = """set logscale y
set ylabel "{label}"
# set yrange [1:1e5]
# set ytics 20
# set mytics 2
# set ytics 8,35,3
"""

Y2_LOG = """set logscale y2
set y2label "{label}"
#set y2range [1e5:1e9]
set y2tics
"""
