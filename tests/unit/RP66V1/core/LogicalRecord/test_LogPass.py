import pytest

from TotalDepth.RP66V1.core.File import LogicalData
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR
from TotalDepth.RP66V1.core.LogicalRecord.LogPass import LogPass
from TotalDepth.RP66V1.core.LogicalRecord.Types import EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP
from TotalDepth.RP66V1.core.RepCode import ObjectName

BYTES_FRAME = b'\xf8\x05FRAME\x0260<\x0bDESCRIPTION\x00\x14<\x08CHANNELS\x00\x17<\nINDEX-TYPE\x00\x14<\tDIRECTION\x00\x14>\x07SPACING\x00\x02\x060.1 in<\tENCRYPTED\x00\x0e>\tINDEX-MIN\x00\x02\x060.1 in>\tINDEX-MAX\x00\x02\x060.1 inp\x0b\x00\x020B\x00)\t\x0b\x00\x04DEPT\x0b\x00\x03INC\x0b\x00\x03AZI\x0b\x00\x05MTTVD\x0b\x00\x04SECT\x0b\x00\x03RCN\x0b\x00\x03RCE\x0b\x00\x05DLSEV\x0b\x00\x04TLTS)\x01\x0eBOREHOLE-DEPTH\x00+\x01\x060.1 in\x00\x00\x00\x00)\x01\x00\x00\x00\x00+\x01\x060.1 in\x00\x00\x00\x00+\x01\x060.1 inILJ\xb0'
BYTES_CHANNEL = b'\xf8\x07CHANNEL\x0259<\tLONG-NAME\x00\x14<\nPROPERTIES\x00\x14<\x13REPRESENTATION-CODE\x00\x0e<\x05UNITS\x00\x14<\tDIMENSION\x00\x0e<\x04AXIS\x00\x17<\rELEMENT-LIMIT\x00\x0e<\x06SOURCE\x00\x18<\tRELOG-NUM\x00\x0ep\x0b\x00\x04DEPT)\x01\x1aMWD Tool Measurement Depth\x00)\x01\x00\x00\x00\x02)\x01\x060.1 in)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x03INC)\x01\x0bInclination\x00)\x01\x00\x00\x00\x02)\x01\x03deg)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x03AZI)\x01\x07Azimuth\x00)\x01\x00\x00\x00\x02)\x01\x03deg)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x05MTTVD)\x01\x18MWD Tool Measurement TVD\x00)\x01\x00\x00\x00\x02)\x01\x01m)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x04SECT)\x01\x07Section\x00)\x01\x00\x00\x00\x02)\x01\x01m)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x03RCN)\x01\x1eRectangular Co-ordinates North\x00)\x01\x00\x00\x00\x02)\x01\x01m)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x03RCE)\x01\x1dRectangular Co-ordinates East\x00)\x01\x00\x00\x00\x02)\x01\x01m)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x05DLSEV)\x01\x10Dog-leg Severity\x00)\x01\x00\x00\x00\x02)\x01\x07deg/30m)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x04TLTS)\x01\x17Tool Temperature Static\x00)\x01\x00\x00\x00\x02)\x01\x04degC)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00'

BYTES_IFLR = [
    b'\x0b\x00\x020B\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00',
    b'\x0b\x00\x020B\x02G\x92\xde\x80?\x00\x01T\x00\x00\x00\x00C>\xffa?U[6?U[6\x00\x00\x00\x00=\xa1\xee\x7f\xc4y\xd0\x00',
    b'\x0b\x00\x020B\x03H\x17\x19\x00?\x00\x01T\x00\x00\x00\x00C\xc4~\xb4@&)\x0b@&)\x0b\x00\x00\x00\x00\x00\x00\x00\x00\xc4y\xd0\x00',
    b'\x0b\x00\x020B\x04He\x1b\x80?@\x00\x1d\x00\x00\x00\x00D\x14\xf8,@\x99\xe7\xc9@\x99\xe7\xc9\x00\x00\x00\x00=\x1a\xe4!\xc4y\xd0\x00',
    b'\x0b\x00\x020B\x05H\x97\xde\x00?\x00\x01T\x00\x00\x00\x00DE}\xd2@\xdd\xa8\xac@\xdd\xa8\xac\x00\x00\x00\x00=\x1a\xe4!\xc4y\xd0\x00',
    b'\x0b\x00\x020B\x06H\xba\x15\xc0?\x7f\xfe\xe7\x00\x00\x00\x00Dq\xfc\xcfA\x14\x1b\xccA\x14\x1b\xcc\x00\x00\x00\x00=\xac~\r\xc4y\xd0\x00',
    b'\x0b\x00\x020B\x07H\xbc\xe2\xe0?xQ\xe8CHp\xa4Du\xa1=A\x14K8A\x14K8\xbd0mP@\x7fp7BI\x93&',
    b'\x0b\x00\x020B\x08H\xd1\x14 ?xQ\xe8CMs3D\x87\xf1k@\xf4<\xb8@\xf4<\xb8\xbf<R\xf8<\xc5"XBa\xabQ',
    b"\x0b\x00\x020B\tH\xda\x9d\x00?33/CN.\x14D\x8e$s@\xdfg\xc3@\xdfg\xc3\xbf\x86]}>'6FBi\xb3h",
    b'\x0b\x00\x020B\nH\xe3\xb4`?\x87\xae\x15CP\xb0\xa4D\x94\r\x8c@\xca\xd4\xa8@\xca\xd4\xa8\xbf\xb1\x8e\xc1>k\xdb`Bi\xb3h',
    b'\x0b\x00\x020B\x0bH\xef\t`?xQ\xe8CJ\xb33D\x9bk\xa7@\xac\xcb4@\xac\xcb4\xbf\xeb\xb6$=\x90T\x92By\xc3{',
    b'\x0b\x00\x020B\x0cH\xf4i\xe0?aG\xb0CH\xee\x14D\x9e\xea\x94@\x9fb\x8b@\x9fb\x8b\xc0\x00\x9d\x13=\xcf\xb1\xe6By\xc3{',
    b'\x0b\x00\x020B\rH\xff\xbf\x80?J=pC\x7f\xc5 D\xa6I @\x8e\xa7\xaf@\x8e\xa7\xaf\xc0$.A>\xc9\x88\xd3By\xc3{',
    b'\x0b\x00\x020B\x0eI\x03\x80\xe0?\xe1G\xacCs\xde\xb8D\xab\x01"@\x84oa@\x84oa\xc0U\xa6\x1e?KKkBy\xc3{',
    b'\x0b\x00\x020B\x0fI\x04m\x10@\x0c\xcc\xceCq&fD\xac4&@\x7f\x06O@\x7f\x06O\xc0hr\xe2?\xb3\xf9\x11By\xc3{',
    b'\x0b\x00\x020B\x10I\x06`\x90@9\x99\x9aCp\xb33D\xae\xbd\x1a@b\xe8}@b\xe8}\xc0\x8dy\xd9?\x84s\x13Bi\xb3h',
# [  20] IFLR: b'0B'      frame:       16 data[  36]: 4906 6090 4039 999a 4370 b333 44ae bd1a I.`.@9..Cp.3D...
# 2019-04-06 08:41:55,742 DEBUG    IFLR bytes [42]: b'\x0b\x00\x020B\x11I\x07M\xd0@J\xe1HCqB\x8fD\xaf\xf1&@S\x11f@S\x11f\xc0\x9b\xc2\x7f?X~\xddBy\xc3{'
# [  21] IFLR: b'0B'      frame:       17 data[  36]: 4907 4dd0 404a e148 4371 428f 44af f126 I.M.@J.HCqB.D..&
# 2019-04-06 08:41:55,742 DEBUG    IFLR bytes [42]: b'\x0b\x00\x020B\x12I\x08;@@U\xc2\x8eCq\xa6fD\xb1%s@BPj@BPj\xc0\xab)\x99?\x08h\xe8By\xc3{'
# [  22] IFLR: b'0B'      frame:       18 data[  36]: 4908 3b40 4055 c28e 4371 a666 44b1 2573 I.;@@U..Cq.fD.%s
# 2019-04-06 08:41:55,742 DEBUG    IFLR bytes [42]: b'\x0b\x00\x020B\x13I\t\x0e\xe0@l(\xf5Cq\x8f\\D\xb28"@2C\xf6@2C\xf6\xc0\xba\x01A?\x9c6\x12B\x80\xe5\xc9'
# [  23] IFLR: b'0B'      frame:       19 data[  36]: 4909 0ee0 406c 28f5 4371 8f5c 44b2 3822 I...@l(.Cq.\D.8"
# 2019-04-06 08:41:55,742 DEBUG    IFLR bytes [42]: b'\x0b\x00\x020B\x14I\t\xff\x00@l(\xf5Cp\x0f]D\xb3o\xcd@\x1e\xa9H@\x1e\xa9H\xc0\xcb\x8d\t>\x98@=B\x80\xe5\xc9'
# [  24] IFLR: b'0B'      frame:       20 data[  36]: 4909 ff00 406c 28f5 4370 0f5d 44b3 6fcd I...@l(.Cp.]D.o.
# 2019-04-06 08:41:55,743 DEBUG    IFLR bytes [42]: b'\x0b\x00\x020B\x15I\n\xed\xf0@l(\xf5Cp\x11\xecD\xb4\xa5\xe1@\n\xb3\xfa@\n\xb3\xfa\xc0\xdc\xe1p:\xe1K\xd2B\x80\xe5\xc9'
# [  25] IFLR: b'0B'      frame:       21 data[  36]: 490a edf0 406c 28f5 4370 11ec 44b4 a5e1 I...@l(.Cp..D...
# 2019-04-06 08:41:55,743 DEBUG    IFLR bytes [42]: b'\x0b\x00\x020B\x16I\x0b\xdc\xa0@l(\xf5Cp\x17\x0bD\xb5\xdb\xa3?\xed\x8c\xa8?\xed\x8c\xa8\xc0\xee1\xe2;aK\xd2B\x80\xe5\xc9'
# [  26] IFLR: b'0B'      frame:       22 data[  36]: 490b dca0 406c 28f5 4370 170b 44b5 dba3 I...@l(.Cp..D...
# 2019-04-06 08:41:55,743 DEBUG    IFLR bytes [42]: b'\x0b\x00\x020B\x17I\x0c\xcb\x90@g\n?Cp\xd1\xecD\xb7\x11\xba?\xc6\x87U?\xc6\x87U\xc0\xffg\x19>\x92\x17*B\x80\xe5\xc9'
# [  27] IFLR: b'0B'      frame:       23 data[  36]: 490c cb90 4067 0a3f 4370 d1ec 44b7 11ba I...@g.?Cp..D...
# 2019-04-06 08:41:55,743 DEBUG    IFLR bytes [42]: b'\x0b\x00\x020B\x18I\r\xb4\xd0@g\n?CqT|D\xb8@|?\xa1\x93G?\xa1\x93G\xc1\x08\x0fs=\xcf\xb1\xe6B\x80\xe5\xc9'
# [  28] IFLR: b'0B'      frame:       24 data[  36]: 490d b4d0 4067 0a3f 4371 547c 44b8 407c I...@g.?CqT|D.@|
# 2019-04-06 08:41:55,743 DEBUG    IFLR bytes [42]: b'\x0b\x00\x020B\x19I\x0e\xbb\xa0@g\n?Cp\xfdqD\xb9\x95\x90?p\x1c\xb4?p\x1c\xb4\xc1\x11|5=vj\xeeB\x80\xe5\xc9'
# [  29] IFLR: b'0B'      frame:       25 data[  36]: 490e bba0 4067 0a3f 4370 fd71 44b9 9590 I...@g.?Cp.qD...
# 2019-04-06 08:41:55,743 DEBUG    IFLR bytes [42]: b'\x0b\x00\x020B\x1aI\x0f\xa9\x90@l(\xf5Cq^\xb7D\xba\xcaa?$%\x9e?$%\x9e\xc1\x1a\x1ds>\x84\xe3\xb9B\x84\xe9\xd5'
# [  30] IFLR: b'0B'      frame:       26 data[  36]: 490f a990 406c 28f5 4371 5eb7 44ba ca61 I...@l(.Cq^.D..a
# 2019-04-06 08:41:55,743 DEBUG    IFLR bytes [42]: b'\x0b\x00\x020B\x1bI\x10\x90 @g\n?Co\xbdpD\xbb\xf5\x9c>\xb26\xa0>\xb26\xa0\xc1"m\x1c>\xd6\xbcDB\x84\xe9\xd5'
# [  31] IFLR: b'0B'      frame:       27 data[  36]: 4910 9020 4067 0a3f 436f bd70 44bb f59c I.. @g.?Co.pD...
# 2019-04-06 08:41:55,743 DEBUG    IFLR bytes [42]: b'\x0b\x00\x020B\x1cI\x11l\xd0@l(\xf5Cp\xca=D\xbd\x14\x11=\x84\xecc=\x84\xecc\xc1*\\&>\xb2\xa7 B\x80\xe5\xc9'
# [  32] IFLR: b'0B'      frame:       28 data[  36]: 4911 6cd0 406c 28f5 4370 ca3d 44bd 1411 I.l.@l(.Cp.=D...
]


def test_eflr_channel_ctor():
    ld = LogicalData(BYTES_CHANNEL)
    EFLR.ExplicitlyFormattedLogicalRecord(EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'CHANNEL'], ld)


def test_eflr_channel_attributes():
    ld = LogicalData(BYTES_CHANNEL)
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'CHANNEL'], ld)
    # print(eflr)
    assert str(eflr) == """EFLR Set type: b'CHANNEL' name: b'59'
  Template [9]:
    CD: 001 11100 L: b'LONG-NAME' C: 0 R: ASCII U: b'' V: None
    CD: 001 11100 L: b'PROPERTIES' C: 0 R: ASCII U: b'' V: None
    CD: 001 11100 L: b'REPRESENTATION-CODE' C: 0 R: SLONG U: b'' V: None
    CD: 001 11100 L: b'UNITS' C: 0 R: ASCII U: b'' V: None
    CD: 001 11100 L: b'DIMENSION' C: 0 R: SLONG U: b'' V: None
    CD: 001 11100 L: b'AXIS' C: 0 R: OBNAME U: b'' V: None
    CD: 001 11100 L: b'ELEMENT-LIMIT' C: 0 R: SLONG U: b'' V: None
    CD: 001 11100 L: b'SOURCE' C: 0 R: OBJREF U: b'' V: None
    CD: 001 11100 L: b'RELOG-NUM' C: 0 R: SLONG U: b'' V: None
  Objects [9]:
    OBNAME: O: 11 C: 0 I: b'DEPT'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: ASCII U: b'' V: [b'MWD Tool Measurement Depth']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: ASCII U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: SLONG U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: ASCII U: b'' V: [b'0.1 in']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: OBNAME U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: OBJREF U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: SLONG U: b'' V: [0]
    OBNAME: O: 11 C: 0 I: b'INC'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: ASCII U: b'' V: [b'Inclination']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: ASCII U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: SLONG U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: ASCII U: b'' V: [b'deg']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: OBNAME U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: OBJREF U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: SLONG U: b'' V: [0]
    OBNAME: O: 11 C: 0 I: b'AZI'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: ASCII U: b'' V: [b'Azimuth']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: ASCII U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: SLONG U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: ASCII U: b'' V: [b'deg']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: OBNAME U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: OBJREF U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: SLONG U: b'' V: [0]
    OBNAME: O: 11 C: 0 I: b'MTTVD'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: ASCII U: b'' V: [b'MWD Tool Measurement TVD']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: ASCII U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: SLONG U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: ASCII U: b'' V: [b'm']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: OBNAME U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: OBJREF U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: SLONG U: b'' V: [0]
    OBNAME: O: 11 C: 0 I: b'SECT'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: ASCII U: b'' V: [b'Section']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: ASCII U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: SLONG U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: ASCII U: b'' V: [b'm']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: OBNAME U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: OBJREF U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: SLONG U: b'' V: [0]
    OBNAME: O: 11 C: 0 I: b'RCN'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: ASCII U: b'' V: [b'Rectangular Co-ordinates North']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: ASCII U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: SLONG U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: ASCII U: b'' V: [b'm']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: OBNAME U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: OBJREF U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: SLONG U: b'' V: [0]
    OBNAME: O: 11 C: 0 I: b'RCE'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: ASCII U: b'' V: [b'Rectangular Co-ordinates East']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: ASCII U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: SLONG U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: ASCII U: b'' V: [b'm']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: OBNAME U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: OBJREF U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: SLONG U: b'' V: [0]
    OBNAME: O: 11 C: 0 I: b'DLSEV'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: ASCII U: b'' V: [b'Dog-leg Severity']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: ASCII U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: SLONG U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: ASCII U: b'' V: [b'deg/30m']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: OBNAME U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: OBJREF U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: SLONG U: b'' V: [0]
    OBNAME: O: 11 C: 0 I: b'TLTS'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: ASCII U: b'' V: [b'Tool Temperature Static']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: ASCII U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: SLONG U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: ASCII U: b'' V: [b'degC']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: OBNAME U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: SLONG U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: OBJREF U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: SLONG U: b'' V: [0]"""


def test_eflr_channel_obnames():
    ld = LogicalData(BYTES_CHANNEL)
    channels = EFLR.ExplicitlyFormattedLogicalRecord(EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'CHANNEL'], ld)
    channel_obnames = [obj.name for obj in channels.objects]
    # print(channel_obnames)
    assert channel_obnames == [
        ObjectName(O=11, C=0, I=b'DEPT'), ObjectName(O=11, C=0, I=b'INC'), ObjectName(O=11, C=0, I=b'AZI'),
        ObjectName(O=11, C=0, I=b'MTTVD'), ObjectName(O=11, C=0, I=b'SECT'), ObjectName(O=11, C=0, I=b'RCN'),
        ObjectName(O=11, C=0, I=b'RCE'), ObjectName(O=11, C=0, I=b'DLSEV'), ObjectName(O=11, C=0, I=b'TLTS'),
    ]


def test_eflr_frame_ctor():
    ld = LogicalData(BYTES_FRAME)
    EFLR.ExplicitlyFormattedLogicalRecord(EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'FRAME'], ld)


def test_eflr_frame_attributes():
    ld = LogicalData(BYTES_FRAME)
    frame = EFLR.ExplicitlyFormattedLogicalRecord(EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'FRAME'], ld)
    assert len(frame.objects) == 1
    # print(eflr)
    assert str(frame) == """EFLR Set type: b'FRAME' name: b'60'
  Template [8]:
    CD: 001 11100 L: b'DESCRIPTION' C: 0 R: ASCII U: b'' V: None
    CD: 001 11100 L: b'CHANNELS' C: 0 R: OBNAME U: b'' V: None
    CD: 001 11100 L: b'INDEX-TYPE' C: 0 R: ASCII U: b'' V: None
    CD: 001 11100 L: b'DIRECTION' C: 0 R: ASCII U: b'' V: None
    CD: 001 11110 L: b'SPACING' C: 0 R: FSINGL U: b'0.1 in' V: None
    CD: 001 11100 L: b'ENCRYPTED' C: 0 R: SLONG U: b'' V: None
    CD: 001 11110 L: b'INDEX-MIN' C: 0 R: FSINGL U: b'0.1 in' V: None
    CD: 001 11110 L: b'INDEX-MAX' C: 0 R: FSINGL U: b'0.1 in' V: None
  Objects [1]:
    OBNAME: O: 11 C: 0 I: b'0B'
      CD: 000 00000 L: b'DESCRIPTION' C: 0 R: ASCII U: b'' V: None
      CD: 001 01001 L: b'CHANNELS' C: 9 R: OBNAME U: b'' V: [ObjectName(O=11, C=0, I=b'DEPT'), ObjectName(O=11, C=0, I=b'INC'), ObjectName(O=11, C=0, I=b'AZI'), ObjectName(O=11, C=0, I=b'MTTVD'), ObjectName(O=11, C=0, I=b'SECT'), ObjectName(O=11, C=0, I=b'RCN'), ObjectName(O=11, C=0, I=b'RCE'), ObjectName(O=11, C=0, I=b'DLSEV'), ObjectName(O=11, C=0, I=b'TLTS')]
      CD: 001 01001 L: b'INDEX-TYPE' C: 1 R: ASCII U: b'' V: [b'BOREHOLE-DEPTH']
      CD: 000 00000 L: b'DIRECTION' C: 0 R: ASCII U: b'' V: None
      CD: 001 01011 L: b'SPACING' C: 1 R: FSINGL U: b'0.1 in' V: [0.0]
      CD: 001 01001 L: b'ENCRYPTED' C: 1 R: SLONG U: b'' V: [0]
      CD: 001 01011 L: b'INDEX-MIN' C: 1 R: FSINGL U: b'0.1 in' V: [0.0]
      CD: 001 01011 L: b'INDEX-MAX' C: 1 R: FSINGL U: b'0.1 in' V: [836779.0]"""

def test_eflr_frame_channels():
    ld = LogicalData(BYTES_FRAME)
    frame = EFLR.ExplicitlyFormattedLogicalRecord(EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'FRAME'], ld)
    obj = frame[0]
    channels = obj[b'CHANNELS'].value
    assert len(channels) == 9
    assert channels == [
        ObjectName(O=11, C=0, I=b'DEPT'), ObjectName(O=11, C=0, I=b'INC'), ObjectName(O=11, C=0, I=b'AZI'),
        ObjectName(O=11, C=0, I=b'MTTVD'), ObjectName(O=11, C=0, I=b'SECT'), ObjectName(O=11, C=0, I=b'RCN'),
        ObjectName(O=11, C=0, I=b'RCE'), ObjectName(O=11, C=0, I=b'DLSEV'), ObjectName(O=11, C=0, I=b'TLTS')
    ]


def _create_log_pass():
    ld = LogicalData(BYTES_CHANNEL)
    channels = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
    ld = LogicalData(BYTES_FRAME)
    frame = EFLR.ExplicitlyFormattedLogicalRecord(4, ld)
    return LogPass(frame, channels)


def test_logpass_ctor():
    _create_log_pass()


def test_example_iflr_bytes():
    assert len(BYTES_IFLR) == 16


def test_example_iflr():
    print()
    for by in BYTES_IFLR:
        ld = LogicalData(by)
        iflr = IFLR.IndirectlyFormattedLogicalRecord(0, ld)
        print(iflr)


def test_example_iflr_process():
    log_pass: LogPass = _create_log_pass()
    print()
    for by in BYTES_IFLR:
        ld = LogicalData(by)
        iflr = IFLR.IndirectlyFormattedLogicalRecord(0, ld)
        print(log_pass.process_IFLR(iflr))
