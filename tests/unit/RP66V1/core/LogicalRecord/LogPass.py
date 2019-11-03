from TotalDepth.RP66V1.core.File import LogicalData
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR
from TotalDepth.RP66V1.core import LogPass
from TotalDepth.RP66V1.core.LogicalRecord.Types import EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP
from TotalDepth.RP66V1.core.RepCode import ObjectName


BYTES_CHANNEL = b'\xf8\x07CHANNEL\x0259<\tLONG-NAME\x00\x14<\nPROPERTIES\x00\x14<\x13REPRESENTATION-CODE\x00\x0e<\x05UNITS\x00\x14<\tDIMENSION\x00\x0e<\x04AXIS\x00\x17<\rELEMENT-LIMIT\x00\x0e<\x06SOURCE\x00\x18<\tRELOG-NUM\x00\x0ep\x0b\x00\x04DEPT)\x01\x1aMWD Tool Measurement Depth\x00)\x01\x00\x00\x00\x02)\x01\x060.1 in)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x03INC)\x01\x0bInclination\x00)\x01\x00\x00\x00\x02)\x01\x03deg)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x03AZI)\x01\x07Azimuth\x00)\x01\x00\x00\x00\x02)\x01\x03deg)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x05MTTVD)\x01\x18MWD Tool Measurement TVD\x00)\x01\x00\x00\x00\x02)\x01\x01m)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x04SECT)\x01\x07Section\x00)\x01\x00\x00\x00\x02)\x01\x01m)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x03RCN)\x01\x1eRectangular Co-ordinates North\x00)\x01\x00\x00\x00\x02)\x01\x01m)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x03RCE)\x01\x1dRectangular Co-ordinates East\x00)\x01\x00\x00\x00\x02)\x01\x01m)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x05DLSEV)\x01\x10Dog-leg Severity\x00)\x01\x00\x00\x00\x02)\x01\x07deg/30m)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x04TLTS)\x01\x17Tool Temperature Static\x00)\x01\x00\x00\x00\x02)\x01\x04degC)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00'
BYTES_FRAME = b'\xf8\x05FRAME\x0260<\x0bDESCRIPTION\x00\x14<\x08CHANNELS\x00\x17<\nINDEX-TYPE\x00\x14<\tDIRECTION\x00\x14>\x07SPACING\x00\x02\x060.1 in<\tENCRYPTED\x00\x0e>\tINDEX-MIN\x00\x02\x060.1 in>\tINDEX-MAX\x00\x02\x060.1 inp\x0b\x00\x020B\x00)\t\x0b\x00\x04DEPT\x0b\x00\x03INC\x0b\x00\x03AZI\x0b\x00\x05MTTVD\x0b\x00\x04SECT\x0b\x00\x03RCN\x0b\x00\x03RCE\x0b\x00\x05DLSEV\x0b\x00\x04TLTS)\x01\x0eBOREHOLE-DEPTH\x00+\x01\x060.1 in\x00\x00\x00\x00)\x01\x00\x00\x00\x00+\x01\x060.1 in\x00\x00\x00\x00+\x01\x060.1 inILJ\xb0'
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
]


def test_eflr_channel_ctor():
    ld = LogicalData(BYTES_CHANNEL)
    EFLR.ExplicitlyFormattedLogicalRecord(EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'CHANNEL'], ld)


def test_eflr_channel_attributes():
    ld = LogicalData(BYTES_CHANNEL)
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'CHANNEL'], ld)
    print(eflr)
    print(eflr.str_long())
    assert str(eflr) == "<ExplicitlyFormattedLogicalRecord EFLR Set type: b'CHANNEL' name: b'59'>"
    assert eflr.str_long() == """<ExplicitlyFormattedLogicalRecord EFLR Set type: b'CHANNEL' name: b'59'>
  Template [9]:
    CD: 001 11100 L: b'LONG-NAME' C: 0 R: 20 (ASCII) U: b'' V: None
    CD: 001 11100 L: b'PROPERTIES' C: 0 R: 20 (ASCII) U: b'' V: None
    CD: 001 11100 L: b'REPRESENTATION-CODE' C: 0 R: 14 (SLONG) U: b'' V: None
    CD: 001 11100 L: b'UNITS' C: 0 R: 20 (ASCII) U: b'' V: None
    CD: 001 11100 L: b'DIMENSION' C: 0 R: 14 (SLONG) U: b'' V: None
    CD: 001 11100 L: b'AXIS' C: 0 R: 23 (OBNAME) U: b'' V: None
    CD: 001 11100 L: b'ELEMENT-LIMIT' C: 0 R: 14 (SLONG) U: b'' V: None
    CD: 001 11100 L: b'SOURCE' C: 0 R: 24 (OBJREF) U: b'' V: None
    CD: 001 11100 L: b'RELOG-NUM' C: 0 R: 14 (SLONG) U: b'' V: None
  Objects [9]:
    OBNAME: O: 11 C: 0 I: b'DEPT'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: 20 (ASCII) U: b'' V: [b'MWD Tool Measurement Depth']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: 20 (ASCII) U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: 14 (SLONG) U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: 20 (ASCII) U: b'' V: [b'0.1 in']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: 23 (OBNAME) U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: 24 (OBJREF) U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: 14 (SLONG) U: b'' V: [0]
    OBNAME: O: 11 C: 0 I: b'INC'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: 20 (ASCII) U: b'' V: [b'Inclination']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: 20 (ASCII) U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: 14 (SLONG) U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: 20 (ASCII) U: b'' V: [b'deg']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: 23 (OBNAME) U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: 24 (OBJREF) U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: 14 (SLONG) U: b'' V: [0]
    OBNAME: O: 11 C: 0 I: b'AZI'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: 20 (ASCII) U: b'' V: [b'Azimuth']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: 20 (ASCII) U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: 14 (SLONG) U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: 20 (ASCII) U: b'' V: [b'deg']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: 23 (OBNAME) U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: 24 (OBJREF) U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: 14 (SLONG) U: b'' V: [0]
    OBNAME: O: 11 C: 0 I: b'MTTVD'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: 20 (ASCII) U: b'' V: [b'MWD Tool Measurement TVD']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: 20 (ASCII) U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: 14 (SLONG) U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: 20 (ASCII) U: b'' V: [b'm']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: 23 (OBNAME) U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: 24 (OBJREF) U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: 14 (SLONG) U: b'' V: [0]
    OBNAME: O: 11 C: 0 I: b'SECT'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: 20 (ASCII) U: b'' V: [b'Section']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: 20 (ASCII) U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: 14 (SLONG) U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: 20 (ASCII) U: b'' V: [b'm']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: 23 (OBNAME) U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: 24 (OBJREF) U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: 14 (SLONG) U: b'' V: [0]
    OBNAME: O: 11 C: 0 I: b'RCN'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: 20 (ASCII) U: b'' V: [b'Rectangular Co-ordinates North']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: 20 (ASCII) U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: 14 (SLONG) U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: 20 (ASCII) U: b'' V: [b'm']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: 23 (OBNAME) U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: 24 (OBJREF) U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: 14 (SLONG) U: b'' V: [0]
    OBNAME: O: 11 C: 0 I: b'RCE'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: 20 (ASCII) U: b'' V: [b'Rectangular Co-ordinates East']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: 20 (ASCII) U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: 14 (SLONG) U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: 20 (ASCII) U: b'' V: [b'm']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: 23 (OBNAME) U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: 24 (OBJREF) U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: 14 (SLONG) U: b'' V: [0]
    OBNAME: O: 11 C: 0 I: b'DLSEV'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: 20 (ASCII) U: b'' V: [b'Dog-leg Severity']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: 20 (ASCII) U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: 14 (SLONG) U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: 20 (ASCII) U: b'' V: [b'deg/30m']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: 23 (OBNAME) U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: 24 (OBJREF) U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: 14 (SLONG) U: b'' V: [0]
    OBNAME: O: 11 C: 0 I: b'TLTS'
      CD: 001 01001 L: b'LONG-NAME' C: 1 R: 20 (ASCII) U: b'' V: [b'Tool Temperature Static']
      CD: 000 00000 L: b'PROPERTIES' C: 0 R: 20 (ASCII) U: b'' V: None
      CD: 001 01001 L: b'REPRESENTATION-CODE' C: 1 R: 14 (SLONG) U: b'' V: [2]
      CD: 001 01001 L: b'UNITS' C: 1 R: 20 (ASCII) U: b'' V: [b'degC']
      CD: 001 01001 L: b'DIMENSION' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'AXIS' C: 0 R: 23 (OBNAME) U: b'' V: None
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 1 R: 14 (SLONG) U: b'' V: [1]
      CD: 000 00000 L: b'SOURCE' C: 0 R: 24 (OBJREF) U: b'' V: None
      CD: 001 01001 L: b'RELOG-NUM' C: 1 R: 14 (SLONG) U: b'' V: [0]"""


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
    # print()
    # print(frame)
    assert str(frame) == "<ExplicitlyFormattedLogicalRecord EFLR Set type: b'FRAME' name: b'60'>"
    # print(frame.str_long())
    assert frame.str_long() == """<ExplicitlyFormattedLogicalRecord EFLR Set type: b'FRAME' name: b'60'>
  Template [8]:
    CD: 001 11100 L: b'DESCRIPTION' C: 0 R: 20 (ASCII) U: b'' V: None
    CD: 001 11100 L: b'CHANNELS' C: 0 R: 23 (OBNAME) U: b'' V: None
    CD: 001 11100 L: b'INDEX-TYPE' C: 0 R: 20 (ASCII) U: b'' V: None
    CD: 001 11100 L: b'DIRECTION' C: 0 R: 20 (ASCII) U: b'' V: None
    CD: 001 11110 L: b'SPACING' C: 0 R: 2 (FSINGL) U: b'0.1 in' V: None
    CD: 001 11100 L: b'ENCRYPTED' C: 0 R: 14 (SLONG) U: b'' V: None
    CD: 001 11110 L: b'INDEX-MIN' C: 0 R: 2 (FSINGL) U: b'0.1 in' V: None
    CD: 001 11110 L: b'INDEX-MAX' C: 0 R: 2 (FSINGL) U: b'0.1 in' V: None
  Objects [1]:
    OBNAME: O: 11 C: 0 I: b'0B'
      CD: 000 00000 L: b'DESCRIPTION' C: 0 R: 20 (ASCII) U: b'' V: None
      CD: 001 01001 L: b'CHANNELS' C: 9 R: 23 (OBNAME) U: b'' V: [ObjectName(O=11, C=0, I=b'DEPT'), ObjectName(O=11, C=0, I=b'INC'), ObjectName(O=11, C=0, I=b'AZI'), ObjectName(O=11, C=0, I=b'MTTVD'), ObjectName(O=11, C=0, I=b'SECT'), ObjectName(O=11, C=0, I=b'RCN'), ObjectName(O=11, C=0, I=b'RCE'), ObjectName(O=11, C=0, I=b'DLSEV'), ObjectName(O=11, C=0, I=b'TLTS')]
      CD: 001 01001 L: b'INDEX-TYPE' C: 1 R: 20 (ASCII) U: b'' V: [b'BOREHOLE-DEPTH']
      CD: 000 00000 L: b'DIRECTION' C: 0 R: 20 (ASCII) U: b'' V: None
      CD: 001 01011 L: b'SPACING' C: 1 R: 2 (FSINGL) U: b'0.1 in' V: [0.0]
      CD: 001 01001 L: b'ENCRYPTED' C: 1 R: 14 (SLONG) U: b'' V: [0]
      CD: 001 01011 L: b'INDEX-MIN' C: 1 R: 2 (FSINGL) U: b'0.1 in' V: [0.0]
      CD: 001 01011 L: b'INDEX-MAX' C: 1 R: 2 (FSINGL) U: b'0.1 in' V: [836779.0]"""


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
    log_pass = LogPass.log_pass_from_RP66V1(frame, channels)
    return log_pass


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


def test_log_pass_str():
    log_pass: LogPass = _create_log_pass()
    # print()
    # print(log_pass)
    assert str(log_pass) == """LogPass:
  FrameArray: ID: OBNAME: O: 11 C: 0 I: b'0B' b''
    FrameChannel: OBNAME: O: 11 C: 0 I: b'DEPT'            Rc:   2 Co:    1 Un: b'0.1 in'    Di: [1] b'MWD Tool Measurement Depth'
    FrameChannel: OBNAME: O: 11 C: 0 I: b'INC'             Rc:   2 Co:    1 Un: b'deg'       Di: [1] b'Inclination'
    FrameChannel: OBNAME: O: 11 C: 0 I: b'AZI'             Rc:   2 Co:    1 Un: b'deg'       Di: [1] b'Azimuth'
    FrameChannel: OBNAME: O: 11 C: 0 I: b'MTTVD'           Rc:   2 Co:    1 Un: b'm'         Di: [1] b'MWD Tool Measurement TVD'
    FrameChannel: OBNAME: O: 11 C: 0 I: b'SECT'            Rc:   2 Co:    1 Un: b'm'         Di: [1] b'Section'
    FrameChannel: OBNAME: O: 11 C: 0 I: b'RCN'             Rc:   2 Co:    1 Un: b'm'         Di: [1] b'Rectangular Co-ordinates North'
    FrameChannel: OBNAME: O: 11 C: 0 I: b'RCE'             Rc:   2 Co:    1 Un: b'm'         Di: [1] b'Rectangular Co-ordinates East'
    FrameChannel: OBNAME: O: 11 C: 0 I: b'DLSEV'           Rc:   2 Co:    1 Un: b'deg/30m'   Di: [1] b'Dog-leg Severity'
    FrameChannel: OBNAME: O: 11 C: 0 I: b'TLTS'            Rc:   2 Co:    1 Un: b'degC'      Di: [1] b'Tool Temperature Static'"""


def test_example_iflr_process():
    log_pass: LogPass.LogPass = _create_log_pass()
    # print()
    for by in BYTES_IFLR:
        ld = LogicalData(by)
        iflr = IFLR.IndirectlyFormattedLogicalRecord(0, ld)
        result = log_pass.process_IFLR(iflr)
        # print(result)


def test_example_iflr_append():
    log_pass: LogPass = _create_log_pass()
    print()
    result = []
    for by in BYTES_IFLR:
        ld = LogicalData(by)
        iflr = IFLR.IndirectlyFormattedLogicalRecord(0, ld)
        log_pass.append(iflr)
    # print(result)
    # depth = result[0]
    # print(depth)
    # print([depth[i] - depth[i-1] for i in range(1, len(BYTES_IFLR))])
    # print(log_pass.object_name_map)
    frame_obj = ObjectName(O=11, C=0, I=b'0B')
    for r, channel_data in enumerate(result):
        print(f'{str(log_pass[frame_obj][r].long_name):40}', ', '.join([f'{c:10.2f}' for c in channel_data]))
