

from TotalDepth.LIS.core import RepCode
# Python reference methods
from TotalDepth.LIS.core import pRepCode
## Cython methods
from TotalDepth.LIS.core import cRepCode
## CPython methods
from TotalDepth.LIS.core import cpRepCode

class TimeRepCode68:

    BINARY_VALUE_PAIRS_68 = (
        (0x444C8000, 153.0),
        (0xBBB38000, -153.0),
        (0x40000000, 0.0),
    )
    BYTES_153 = b'\x44\x4C\x80\x00''
    BYTES_0 = b'\x40\x00\x00\x00''

    def time_pRepCode_to(self):
        pRepCode.to68(153.0)

    def time_pRepCode_from(self):
        pRepCode.from68(0x444C8000)

    def time_cRepCode_to(self):
        cRepCode.to68(153.0)

    def time_cRepCode_from(self):
        cRepCode.from68(0x444C8000)

    def time_cpRepCode_to(self):
        cpRepCode.to68(153.0)

    def time_cpRepCode_from(self):
        cpRepCode.from68(0x444C8000)


# class MemSuite:
#     def mem_list(self):
#         return [0] * 256
