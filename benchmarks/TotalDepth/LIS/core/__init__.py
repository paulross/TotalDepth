import io
import os
import typing

from TotalDepth.LIS.core import PhysRec

BINARY_DIR = os.path.join(os.path.dirname(__file__), 'binary_files')
BINARY_RANGE = (10, 20)


def binary_name(size: int) -> str:
    return '{:d}-{:d}'.format(2, size)


def binary_path(size: int) -> str:
    return os.path.join(BINARY_DIR, binary_name(size))


def binary_size(size: int) -> int:
    return 2**size


def has_binary_files():
    if not os.path.isdir(BINARY_DIR):
        return False
    for value in BINARY_RANGE:
        if not os.path.isfile(binary_path(value)):
            return False
    return True


def create_binary_files():
    if not os.path.exists(BINARY_DIR):
        os.makedirs(BINARY_DIR)
    for value in BINARY_RANGE:
        with open(binary_path(value), 'wb') as f:
            f.write(b' ' * binary_size(value))


def check_binary_files() -> None:
    if not has_binary_files():
        create_binary_files()


def write_logical_data_to_physical_records(logical_data_records: typing.List[bytes],
                                           has_tif: bool=False,
                                           pr_len: int=PhysRec.PR_MAX_LENGTH,
                                           pr_tail: PhysRec.PhysRecTail=PhysRec.PhysRecTail()
                                           ) -> io.BytesIO:
    """
    Takes logical data and writes it into a contiguous set of physical records returning a binary file.
    This is quite useful for testing.

    pr_tail has the following arguments: hasRecNum=False, fileNum=None, hasCheckSum=False
    """
    file_obj = io.BytesIO()
    prh = PhysRec.PhysRecWrite(
        file_obj, theFileId=None, keepGoing=False, hasTif=has_tif, thePrLen=pr_len, thePrt=pr_tail
    )
    for ld in logical_data_records:
        prh.writeLr(ld)
    return file_obj

