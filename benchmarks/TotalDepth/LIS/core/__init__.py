import io
import os

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


def write_logical_data_to_physical_records(logical_data: bytes,
                                           pr_len: int=PhysRec.PR_MAX_LENGTH,
                                           pr_tail: PhysRec.PhysRecTail=PhysRec.PhysRecTail()
                                           ) -> bytes:
    """
    Takes logical data and writes it into a contiguous set of physical records returning the raw bytes.
    This is quite useful for testing.
    """
    file_obj = io.BytesIO()
    prh = PhysRec.PhysRecWrite(file_obj, thePrLen=pr_len, thePrt=pr_tail)
    prh.writeLr(logical_data)
    return file_obj.getvalue()

