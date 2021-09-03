import logging
import os
import sys

import numpy as np

import TotalDepth
from TotalDepth.DAT import DAT_parser

logger = logging.getLogger(__file__)


TOTAL_DEPTH_SOURCE_ROOT = os.path.dirname(TotalDepth.__file__)
EXAMPLE_DATA_DIRECTORY = os.path.join(TOTAL_DEPTH_SOURCE_ROOT, os.path.pardir, os.path.pardir, 'example_data')


def example_frame_array():
    file_path = os.path.join(EXAMPLE_DATA_DIRECTORY, 'DAT', 'data', 'example.dat')
    with open(file_path) as file:
        frame_array = DAT_parser.parse_file(file)
        print(f'Frame array: {frame_array}')
        for channel in frame_array:
            print(f'np.info for {channel}:')
            np.info(channel.array)
            print()


def main() -> int:  # pragma: no cover
    DEFAULT_OPT_LOG_FORMAT_VERBOSE = (
        '%(asctime)s - %(filename)24s#%(lineno)-4d - %(process)5d - (%(threadName)-10s) - %(levelname)-8s - %(message)s'
    )
    logging.basicConfig(level=logging.INFO, format=DEFAULT_OPT_LOG_FORMAT_VERBOSE, stream=sys.stdout)

    example_frame_array()

    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
