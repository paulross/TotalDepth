import logging
import os
import sys

import numpy as np

import TotalDepth
from TotalDepth.BIT import ReadBIT

logger = logging.getLogger(__file__)


TOTAL_DEPTH_SOURCE_ROOT = os.path.dirname(TotalDepth.__file__)
EXAMPLE_DATA_DIRECTORY = os.path.join(TOTAL_DEPTH_SOURCE_ROOT, os.path.pardir, os.path.pardir, 'example_data')


def example_frame_array():
    bit_file_path = os.path.join(EXAMPLE_DATA_DIRECTORY, 'BIT', 'data', '29_10-_3Z_dwl_DWL_WIRE_1644659.bit')
    with open(bit_file_path, 'rb') as file:
        frames = ReadBIT.create_bit_frame_array_from_file(file)
        for frame in frames:
            print(f'Description: {frame.description}')
            for frame_channel in frame.frame_array:
                print(f'np.info for {frame_channel}:')
                np.info(frame_channel.array)
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
