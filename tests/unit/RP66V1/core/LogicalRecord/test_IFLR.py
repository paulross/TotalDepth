
import pytest

from TotalDepth.RP66V1.core import File, RepCode
from TotalDepth.RP66V1.core.LogicalRecord import IFLR

# NOTE: Missing first IFLR as is seems to be all nulls so frame number starts at 2.
IFLR_BYTES = [
    b'\x0b\x00\x020B\x02G\x92\xde\x80?\x00\x01T\x00\x00\x00\x00C>\xffa?U[6?U[6\x00\x00\x00\x00=\xa1\xee\x7f\xc4y\xd0\x00',
    b'\x0b\x00\x020B\x03H\x17\x19\x00?\x00\x01T\x00\x00\x00\x00C\xc4~\xb4@&)\x0b@&)\x0b\x00\x00\x00\x00\x00\x00\x00\x00\xc4y\xd0\x00',
    b'\x0b\x00\x020B\x04He\x1b\x80?@\x00\x1d\x00\x00\x00\x00D\x14\xf8,@\x99\xe7\xc9@\x99\xe7\xc9\x00\x00\x00\x00=\x1a\xe4!\xc4y\xd0\x00',
    b'\x0b\x00\x020B\x05H\x97\xde\x00?\x00\x01T\x00\x00\x00\x00DE}\xd2@\xdd\xa8\xac@\xdd\xa8\xac\x00\x00\x00\x00=\x1a\xe4!\xc4y\xd0\x00',
    b'\x0b\x00\x020B\x06H\xba\x15\xc0?\x7f\xfe\xe7\x00\x00\x00\x00Dq\xfc\xcfA\x14\x1b\xccA\x14\x1b\xcc\x00\x00\x00\x00=\xac~\r\xc4y\xd0\x00',
    b'\x0b\x00\x020B\x07H\xbc\xe2\xe0?xQ\xe8CHp\xa4Du\xa1=A\x14K8A\x14K8\xbd0mP@\x7fp7BI\x93&',
    b'\x0b\x00\x020B\x08H\xd1\x14 ?xQ\xe8CMs3D\x87\xf1k@\xf4<\xb8@\xf4<\xb8\xbf<R\xf8<\xc5"XBa\xabQ',
    b"\x0b\x00\x020B\tH\xda\x9d\x00?33/CN.\x14D\x8e$s@\xdfg\xc3@\xdfg\xc3\xbf\x86]}>'6FBi\xb3h",
]


IFLR_STRINGS = [
    "<IndirectlyFormattedLogicalRecord OBNAME: O: 11 C: 0 I: b'0B' frame: 2 free data: 36>",
    "<IndirectlyFormattedLogicalRecord OBNAME: O: 11 C: 0 I: b'0B' frame: 3 free data: 36>",
    "<IndirectlyFormattedLogicalRecord OBNAME: O: 11 C: 0 I: b'0B' frame: 4 free data: 36>",
    "<IndirectlyFormattedLogicalRecord OBNAME: O: 11 C: 0 I: b'0B' frame: 5 free data: 36>",
    "<IndirectlyFormattedLogicalRecord OBNAME: O: 11 C: 0 I: b'0B' frame: 6 free data: 36>",
    "<IndirectlyFormattedLogicalRecord OBNAME: O: 11 C: 0 I: b'0B' frame: 7 free data: 36>",
    "<IndirectlyFormattedLogicalRecord OBNAME: O: 11 C: 0 I: b'0B' frame: 8 free data: 36>",
    "<IndirectlyFormattedLogicalRecord OBNAME: O: 11 C: 0 I: b'0B' frame: 9 free data: 36>",
]

@pytest.mark.parametrize(
    'frame_number, by',
    ((i + 2, by) for i, by in enumerate(IFLR_BYTES))
)
def test_iflr_ctor(frame_number, by):
    ld = File.LogicalData(by)
    iflr = IFLR.IndirectlyFormattedLogicalRecord(1, ld)
    assert iflr.lr_type == 1
    assert iflr.object_name == RepCode.ObjectName(O=11, C=0, I=b'0B')
    assert iflr.frame_number == frame_number
    assert iflr.preamble_length == 6
    assert iflr.remain == 36
    assert iflr.remain == ld.remain


@pytest.mark.parametrize(
    'by, s',
    (zip(IFLR_BYTES, IFLR_STRINGS))
)
def test_iflr_str(by, s):
    ld = File.LogicalData(by)
    iflr = IFLR.IndirectlyFormattedLogicalRecord(1, ld)
    assert str(iflr) == s


IFLR_ZERO_EMPTY = b'\x0b\x00\x020B\x00'
IFLR_ZERO_NOT_EMPTY = b'\x0b\x00\x020B\x00G\x92\xde\x80?\x00\x01T\x00\x00\x00\x00C>\xffa?U[6?U[6\x00\x00\x00\x00=\xa1\xee\x7f\xc4y\xd0\x00'


def test_iflr_ctor_zero_empty():
    ld = File.LogicalData(IFLR_ZERO_EMPTY)
    iflr = IFLR.IndirectlyFormattedLogicalRecord(1, ld)
    assert iflr.lr_type == 1
    assert iflr.object_name == RepCode.ObjectName(O=11, C=0, I=b'0B')
    assert iflr.frame_number == 0
    assert iflr.preamble_length == 6
    assert iflr.remain == 0
    assert iflr.remain == ld.remain


def test_iflr_ctor_zero_not_empty():
    ld = File.LogicalData(IFLR_ZERO_NOT_EMPTY)
    iflr = IFLR.IndirectlyFormattedLogicalRecord(1, ld)
    assert iflr.lr_type == 1
    assert iflr.object_name == RepCode.ObjectName(O=11, C=0, I=b'0B')
    assert iflr.frame_number == 0
    assert iflr.preamble_length == 6
    assert iflr.remain == 36
    assert iflr.remain == ld.remain
