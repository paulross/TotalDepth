"""
Common command line options for LIS tools.
"""
import argparse


def add_physical_record_padding_options(arg_parser: argparse.ArgumentParser) -> None:
    arg_parser.add_argument("--pad-modulo", type=int, default=0,
                         help="Consume pad bytes up to tell() modulo this value, typically 2 or 4. [default: %(default)s]")
    arg_parser.add_argument("--pad-non-null", action="store_true", default=False,
                         help="Pad bytes can be non-null bytes. Only relevant if --pad-modulo > 0 [default: %(default)s]")
