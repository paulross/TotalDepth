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
    v = version()
    logger.info(f'gnuplot version: "{v}"')
    print(f'gnuplot version: "{v}"')
    if not v:
        raise ValueError('--gnuplot specified but gnuplot not installed.')
    parser.add_argument('--gnuplot', type=str, help='Directory to write the gnuplot data.')


def version() -> bytes:
    """
    For example: b'gnuplot 5.2 patchlevel 6'
    """
    with subprocess.Popen(['gnuplot', '--version'], stdout=subprocess.PIPE) as proc:
        return proc.stdout.read().strip()


def _num_columns(table: typing.Sequence[typing.Sequence[typing.Any]]) -> int:
    num_colums_set = set(len(r) for r in table)
    if len(num_colums_set) != 1:
        raise ValueError('Not rectangular.')
    return num_colums_set.pop()


def create_gnuplot_dat(
        table: typing.Sequence[typing.Sequence[typing.Any]]) -> str:
    """
    Returns a pretty formatted string of the data in the given table suitable for use as a gnuplot .dat file.
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
    if not os.path.exists(path):
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
        stdout, stderr = proc.communicate(timeout=1)
    except subprocess.TimeoutExpired as err:
        logger.exception()
        proc.kill()
        stdout, stderr = proc.communicate()
    logging.info(f'gnuplot stdout: {stdout}')
    if stderr:
        logging.error(f'gnuplot stderr: {stdout}')
    # TODO: Return stderr?
    return proc.returncode


def write_test_file(path: str, typ: str) -> int:
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
        proc.stdin.write(test_stdin)
        proc.stdin.close()
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

