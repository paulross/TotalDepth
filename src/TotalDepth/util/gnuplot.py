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
    parser.add_argument('--gnuplot', type=str, help='Directory to write the gnuplot data.')


def write_gnuplot(path: str, name: str, data: str, plot: str) -> int:
    """
    Write the data to .dat file and plot configuration to .plt file and then invoke gnuplot.
    This returns the gnuplot error code.

    Create the plot for name.
    fn_data is a function that takes a stream and writes the 'name.dat' file. This must return
    a list of strings, if non-empty then they are written into the plt file as {computed_data}.
    fn_plot is a function that return the 'name.plt' string ready to insert the 'name.dat'
    into the format variable 'file_name'.
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, name + '.dat')) as fobj:
        fobj.write(data)
    path_plt = os.path.join(path, name + '.plt')
    with open(path_plt) as fobj:
        fobj.write(plot)
    proc = subprocess.Popen(
        args=['gnuplot', '-p', path_plt],
        shell=False,
        cwd=os.path.dirname(path),
    )
    try:
        outs, errs = proc.communicate(timeout=1)
    except subprocess.TimeoutExpired:
        logger.exception()
        proc.kill()
        # outs, errs = proc.communicate()
    # print(outs, errs, proc.returncode)
    return proc.returncode


def create_gnuplot_dat(
        table: typing.Sequence[typing.Sequence[typing.Any]],
        headings: typing.Sequence[str],
        include_index: bool = False) -> str:
    """
    Returns a pretty formatted string of the data in the given table suitable for use as a gnuplot .dat file.
    """
    num_colums_set = set(len(r) for r in table)
    if len(num_colums_set) != 1:
        raise ValueError('Not rectangular.')
    num_colums = num_colums_set.pop()
    column_widths = reduce(
        lambda l, rows: [max(l, len(str(r))) for l, r in zip(l, rows)],
        [0,] * num_colums,
    )



# def invoke_gnuplot(name: str, fn_dat: typing.Callable, fn_plt: typing.Callable) -> int:
#     """
#     Create the plot for name.
#     fn_data is a function that takes a stream and writes the 'name.dat' file. This must return
#     a list of strings, if non-empty then they are written into the plt file as {computed_data}.
#     fn_plot is a function that return the 'name.plt' string ready to insert the 'name.dat'
#     into the format variable 'file_name'.
#     """
#     print('Writing "{}"'.format(name))
#     with open(plot_file('{}.dat'.format(name)), 'w') as outfile:
#         computed_data_strings = fn_dat(outfile)
#     if len(computed_data_strings):
#         plot_data = fn_plt().format(
#             file_name=name, computed_data='\n'.join(computed_data_strings)
#         )
#     else:
#         plot_data = fn_plt().format(file_name=name)
#     plt_file_path = plot_file('{}.plt'.format(name))
#     with open(plt_file_path, 'w') as outfile:
#         outfile.write(plot_data)
#     proc = subprocess.Popen(
#         args=['gnuplot', '-p', os.path.basename(plt_file_path)],
#         shell=False,
#         cwd=os.path.dirname(plt_file_path),
#     )
#     try:
#         outs, errs = proc.communicate(timeout=1)
#     except subprocess.TimeoutExpired as err:
#         print('ERROR:', err)
#         proc.kill()
#         outs, errs = proc.communicate()
#     # print(outs, errs, proc.returncode)
#     return proc.returncode



