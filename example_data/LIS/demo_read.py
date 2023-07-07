import io
import logging
import os
import sys

import numpy as np

import TotalDepth
from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import FileIndexer


logger = logging.getLogger(__file__)


TOTAL_DEPTH_SOURCE_ROOT = os.path.dirname(TotalDepth.__file__)
EXAMPLE_DATA_DIRECTORY = os.path.join(TOTAL_DEPTH_SOURCE_ROOT, os.path.pardir, os.path.pardir, 'example_data')


def example_frame_array():
    file_path = os.path.join(EXAMPLE_DATA_DIRECTORY, 'LIS', 'data', 'DILLSON-1_WELL_LOGS_FILE-013.LIS')
    lis_file = TotalDepth.LIS.core.File.FileRead(file_path)
    lis_index = TotalDepth.LIS.core.FileIndexer.FileIndex(lis_file)
    print(lis_index)
    for log_pass in lis_index.genLogPasses():
        if log_pass.logPass.totalFrames > 0:
            log_pass.logPass.setFrameSet(lis_file)
            print(log_pass)
            data = log_pass.logPass.frameSet.frames
            np.info(data)
            print(data)
        else:
            print(log_pass)

    # with open(file_path) as file:
    #     frame_array = DAT_parser.parse_file(file)
    #     print(f'Frame array: {frame_array}')
    #     for channel in frame_array:
    #         print(f'np.info for {channel}:')
    #         np.info(channel.array)
    #         print()


def main() -> int:  # pragma: no cover
    DEFAULT_OPT_LOG_FORMAT_VERBOSE = (
        '%(asctime)s - %(filename)24s#%(lineno)-4d - %(process)5d - (%(threadName)-10s) - %(levelname)-8s - %(message)s'
    )
    logging.basicConfig(level=logging.INFO, format=DEFAULT_OPT_LOG_FORMAT_VERBOSE, stream=sys.stdout)

    example_frame_array()

    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
