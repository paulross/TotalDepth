import argparse
import logging
import sys


def add_logging_option(parser: argparse.ArgumentParser, default_log_level: int = 30) -> None:
    log_level_help_mapping = ', '.join(
        ['{:d}<->{:s}'.format(level, logging._levelToName[level]) for level in sorted(logging._levelToName.keys())]
    )
    log_level_help = f'Log Level as an integer or symbol. ({log_level_help_mapping}) [default: %(default)s]'
    parser.add_argument( "-l", "--log-level", default=default_log_level, help=log_level_help)


def set_logging_from_argparse(args: argparse.Namespace, **kwargs) -> None:
    # Extract log level
    if args.log_level in logging._nameToLevel:
        log_level = logging._nameToLevel[args.log_level]
    else:
        log_level = int(args.log_level)
    # Initialise logging etc. Overwrite kwargs['level']
    kwargs['level'] = log_level
    if 'format' not in kwargs:
        kwargs['format'] = '%(asctime)s %(levelname)-8s %(message)s'
    if 'stream' not in kwargs:
        kwargs['stream'] = sys.stdout
    #datefmt='%y-%m-%d % %H:%M:%S',
    logging.basicConfig(**kwargs)
