import io
import typing

import pytest

import TotalDepth.RP66V1.IndexXML
from TotalDepth.RP66V1.core import File, LogPass, RepCode
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR
from TotalDepth.util import XmlWrite


@pytest.mark.parametrize(
    'dimensions, frame_number, expected',
    (
        ([1], 7, [(7, 0)]),
        ([2, 3], 7, [(7, 0, 0), (7, 0, 1), (7, 0, 2), (7, 1, 0), (7, 1, 1), (7, 1, 2)]),
        ([3, 5], 11, [
            (11, 0, 0), (11, 0, 1), (11, 0, 2), (11, 0, 3), (11, 0, 4),
            (11, 1, 0), (11, 1, 1), (11, 1, 2), (11, 1, 3), (11, 1, 4),
            (11, 2, 0), (11, 2, 1), (11, 2, 2), (11, 2, 3), (11, 2, 4),
        ]),
    )
)
def test_frame_channel_numpy_indexes(dimensions, frame_number, expected):
    channel = LogPass.FrameChannel(
        ident=RepCode.ObjectName(O=11, C=0, I=b'DEPT'),
        long_name=b'Depth of measurement',
        rep_code=2,
        units=b'm',
        dimensions=dimensions,
    )
    # print(channel.numpy_indexes(frame_number))
    assert list(channel.numpy_indexes(frame_number)) == expected


# Data from PRASLIN-1_MWD_SUITE1_RUN1_HDS1-L_SURVEY_0MD-2125MD_EOS.dlis
# 9 channels and 83 frames but here are just the frames [1:9]
BYTES_EFLR_CHANNEL = b'\xf8\x07CHANNEL\x0259<\tLONG-NAME\x00\x14<\nPROPERTIES\x00\x14<\x13REPRESENTATION-CODE\x00\x0e<\x05UNITS\x00\x14<\tDIMENSION\x00\x0e<\x04AXIS\x00\x17<\rELEMENT-LIMIT\x00\x0e<\x06SOURCE\x00\x18<\tRELOG-NUM\x00\x0ep\x0b\x00\x04DEPT)\x01\x1aMWD Tool Measurement Depth\x00)\x01\x00\x00\x00\x02)\x01\x060.1 in)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x03INC)\x01\x0bInclination\x00)\x01\x00\x00\x00\x02)\x01\x03deg)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x03AZI)\x01\x07Azimuth\x00)\x01\x00\x00\x00\x02)\x01\x03deg)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x05MTTVD)\x01\x18MWD Tool Measurement TVD\x00)\x01\x00\x00\x00\x02)\x01\x01m)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x04SECT)\x01\x07Section\x00)\x01\x00\x00\x00\x02)\x01\x01m)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x03RCN)\x01\x1eRectangular Co-ordinates North\x00)\x01\x00\x00\x00\x02)\x01\x01m)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x03RCE)\x01\x1dRectangular Co-ordinates East\x00)\x01\x00\x00\x00\x02)\x01\x01m)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x05DLSEV)\x01\x10Dog-leg Severity\x00)\x01\x00\x00\x00\x02)\x01\x07deg/30m)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00p\x0b\x00\x04TLTS)\x01\x17Tool Temperature Static\x00)\x01\x00\x00\x00\x02)\x01\x04degC)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x01\x00)\x01\x00\x00\x00\x00'
BYTES_EFLR_FRAME = b'\xf8\x05FRAME\x0260<\x0bDESCRIPTION\x00\x14<\x08CHANNELS\x00\x17<\nINDEX-TYPE\x00\x14<\tDIRECTION\x00\x14>\x07SPACING\x00\x02\x060.1 in<\tENCRYPTED\x00\x0e>\tINDEX-MIN\x00\x02\x060.1 in>\tINDEX-MAX\x00\x02\x060.1 inp\x0b\x00\x020B\x00)\t\x0b\x00\x04DEPT\x0b\x00\x03INC\x0b\x00\x03AZI\x0b\x00\x05MTTVD\x0b\x00\x04SECT\x0b\x00\x03RCN\x0b\x00\x03RCE\x0b\x00\x05DLSEV\x0b\x00\x04TLTS)\x01\x0eBOREHOLE-DEPTH\x00+\x01\x060.1 in\x00\x00\x00\x00)\x01\x00\x00\x00\x00+\x01\x060.1 in\x00\x00\x00\x00+\x01\x060.1 inILJ\xb0'
# NOTE: Missing first IFLR as is seems to be all nulls.
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
FRAME_ARRAY_IDENT = RepCode.ObjectName(O=11, C=0, I=b'0B')

@pytest.mark.parametrize(
    'by',
    (
        BYTES_EFLR_CHANNEL, BYTES_EFLR_FRAME,
    )
)
def test_logical_data_constructs(by):
    File.LogicalData(by)


@pytest.mark.parametrize(
    'lr_type, by',
    (
        (3, BYTES_EFLR_CHANNEL),
        (4, BYTES_EFLR_FRAME),
    )
)
def test_eflr_constructs(lr_type, by):
    ld = File.LogicalData(by)
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(lr_type, ld)
    assert eflr is not None


def _eflr_channel() -> EFLR.ExplicitlyFormattedLogicalRecord:
    ld = File.LogicalData(BYTES_EFLR_CHANNEL)
    return EFLR.ExplicitlyFormattedLogicalRecord(3, ld)


def _eflr_frame() -> EFLR.ExplicitlyFormattedLogicalRecord:
    ld = File.LogicalData(BYTES_EFLR_FRAME)
    return EFLR.ExplicitlyFormattedLogicalRecord(4, ld)


def _iflr_and_logical_data_from_bytes(by: bytes) -> typing.Tuple[IFLR.IndirectlyFormattedLogicalRecord, File.LogicalData]:
    ld = File.LogicalData(by)
    iflr = IFLR.IndirectlyFormattedLogicalRecord(1, ld)
    return iflr, ld


@pytest.mark.parametrize(
    'lr_type, by',
    ((1, by) for by in IFLR_BYTES)
)
def test_iflr_constructs(lr_type, by):
    iflr, _logical_data = _iflr_and_logical_data_from_bytes(by)
    assert iflr is not None
    assert iflr.lr_type == lr_type
    assert iflr.object_name == FRAME_ARRAY_IDENT


@pytest.mark.parametrize(
    'iflr_index, by',
    enumerate(IFLR_BYTES)
)
def test_iflr_frame_numbers(iflr_index, by):
    iflr, _logical_data = _iflr_and_logical_data_from_bytes(by)
    # +2 as the frame number starts at 1 in RP66V1 and this test data has omitted the first frame.
    assert iflr.frame_number == iflr_index + 2


def _log_pass() -> LogPass.LogPass:
    return LogPass.log_pass_from_RP66V1(_eflr_frame(), _eflr_channel())


def test_log_pass_ctor_from_RP66V1_file():
    log_pass = _log_pass()


def test_log_pass_frame_arrays_from_RP66V1_file():
    log_pass = _log_pass()
    assert len(log_pass) == 1
    assert list(log_pass.keys()) == [FRAME_ARRAY_IDENT]


def test_log_pass_frame_channels_from_RP66V1_file():
    log_pass = _log_pass()
    frame_array = log_pass[FRAME_ARRAY_IDENT]
    assert len(frame_array) == 9
    # print(list(frame_array.keys()))
    expected = [
        RepCode.ObjectName(O=11, C=0, I=b'DEPT'), RepCode.ObjectName(O=11, C=0, I=b'INC'),
        RepCode.ObjectName(O=11, C=0, I=b'AZI'), RepCode.ObjectName(O=11, C=0, I=b'MTTVD'),
        RepCode.ObjectName(O=11, C=0, I=b'SECT'), RepCode.ObjectName(O=11, C=0, I=b'RCN'),
        RepCode.ObjectName(O=11, C=0, I=b'RCE'), RepCode.ObjectName(O=11, C=0, I=b'DLSEV'),
        RepCode.ObjectName(O=11, C=0, I=b'TLTS'),

    ]
    assert list(frame_array.keys()) == expected


def test_log_pass_frame_channel_numpy_indexes():
    log_pass = _log_pass()
    frame_array = log_pass[FRAME_ARRAY_IDENT]
    channel = frame_array[RepCode.ObjectName(O=11, C=0, I=b'DEPT')]
    assert list(channel.numpy_indexes(0)) == [(0, 0)]


def test_read_iflr():
    log_pass = _log_pass()
    frame_array: LogPass.FrameArray = log_pass[FRAME_ARRAY_IDENT]
    frame_array.init_arrays(len(IFLR_BYTES))
    for f, by in enumerate(IFLR_BYTES):
        iflr, logical_data = _iflr_and_logical_data_from_bytes(by)
        frame_array.read(logical_data, f)
    assert str(frame_array.channels[0].array) == """[[ 75197.]
 [154724.]
 [234606.]
 [311024.]
 [381102.]
 [386839.]
 [428193.]
 [447720.]]"""
    assert str(frame_array.channels[1].array) == """[[0.50002027]
 [0.50002027]
 [0.7500017 ]
 [0.50002027]
 [0.99998325]
 [0.9699998 ]
 [0.9699998 ]
 [0.69999975]]"""
    assert str(frame_array.channels[2].array) == """[[  0.  ]
 [  0.  ]
 [  0.  ]
 [  0.  ]
 [  0.  ]
 [200.44]
 [205.45]
 [206.18]]"""
    assert str(frame_array.channels[3].array) == """[[ 190.99757]
 [ 392.98987]
 [ 595.8777 ]
 [ 789.96594]
 [ 967.95013]
 [ 982.51935]
 [1087.5443 ]
 [1137.139  ]]"""
    assert str(frame_array.channels[4].array) == """[[0.833423]
 [2.596255]
 [4.809544]
 [6.92684 ]
 [9.256786]
 [9.268364]
 [7.632412]
 [6.981416]]"""
    assert str(frame_array.channels[5].array) == """[[0.833423]
 [2.596255]
 [4.809544]
 [6.92684 ]
 [9.256786]
 [9.268364]
 [7.632412]
 [6.981416]]"""
    assert str(frame_array.channels[6].array) == """[[ 0.      ]
 [ 0.      ]
 [ 0.      ]
 [ 0.      ]
 [ 0.      ]
 [-0.043073]
 [-0.735641]
 [-1.049728]]"""
    assert str(frame_array.channels[7].array) == """[[0.07906818]
 [0.        ]
 [0.03781522]
 [0.03781522]
 [0.0842248 ]
 [3.991224  ]
 [0.02406423]
 [0.16329297]]"""
    assert str(frame_array.channels[8].array) == """[[-999.25  ]
 [-999.25  ]
 [-999.25  ]
 [-999.25  ]
 [-999.25  ]
 [  50.3937]
 [  56.4173]
 [  58.4252]]"""


def test_read_iflr_partial():
    log_pass = _log_pass()
    frame_array: LogPass.FrameArray = log_pass[FRAME_ARRAY_IDENT]
    channels = {
            RepCode.ObjectName(O=11, C=0, I=b'DEPT'),
            RepCode.ObjectName(O=11, C=0, I=b'INC'),
            RepCode.ObjectName(O=11, C=0, I=b'SECT'),
    }
    frame_array.init_arrays_partial(len(IFLR_BYTES), channels)
    for f, by in enumerate(IFLR_BYTES):
        iflr, logical_data = _iflr_and_logical_data_from_bytes(by)
        frame_array.read_partial(logical_data, f, channels)
    assert str(frame_array.channels[0].array) == """[[ 75197.]
 [154724.]
 [234606.]
 [311024.]
 [381102.]
 [386839.]
 [428193.]
 [447720.]]"""
    assert str(frame_array.channels[1].array) == """[[0.50002027]
 [0.50002027]
 [0.7500017 ]
 [0.50002027]
 [0.99998325]
 [0.9699998 ]
 [0.9699998 ]
 [0.69999975]]"""
    assert str(frame_array.channels[2].array) == """[]"""
    assert str(frame_array.channels[3].array) == """[]"""
    assert str(frame_array.channels[4].array) == """[[0.833423]
 [2.596255]
 [4.809544]
 [6.92684 ]
 [9.256786]
 [9.268364]
 [7.632412]
 [6.981416]]"""
    assert str(frame_array.channels[5].array) == """[]"""
    assert str(frame_array.channels[6].array) == """[]"""
    assert str(frame_array.channels[7].array) == """[]"""
    assert str(frame_array.channels[8].array) == """[]"""


def test_log_pass_write_XML():
    log_pass = _log_pass()
    ostream = io.StringIO()
    xml_stream = XmlWrite.XmlStream(ostream)
    iflr_map = {
        RepCode.ObjectName(O=11, C=0, I=b'0B'): [],
    }
    TotalDepth.RP66V1.IndexXML.log_pass_to_XML(log_pass, iflr_map, xml_stream)
    # print(ostream.getvalue())
    expected = """
<LogPass count="1">
  <FrameArray C="0" I="0B" O="11" description="" x_axis="DEPT" x_units="0.1 in">
    <Channels count="9">
      <Channel C="0" I="DEPT" O="11" count="1" dimensions="1" long_name="MWD Tool Measurement Depth" rep_code="2" units="0.1 in"/>
      <Channel C="0" I="INC" O="11" count="1" dimensions="1" long_name="Inclination" rep_code="2" units="deg"/>
      <Channel C="0" I="AZI" O="11" count="1" dimensions="1" long_name="Azimuth" rep_code="2" units="deg"/>
      <Channel C="0" I="MTTVD" O="11" count="1" dimensions="1" long_name="MWD Tool Measurement TVD" rep_code="2" units="m"/>
      <Channel C="0" I="SECT" O="11" count="1" dimensions="1" long_name="Section" rep_code="2" units="m"/>
      <Channel C="0" I="RCN" O="11" count="1" dimensions="1" long_name="Rectangular Co-ordinates North" rep_code="2" units="m"/>
      <Channel C="0" I="RCE" O="11" count="1" dimensions="1" long_name="Rectangular Co-ordinates East" rep_code="2" units="m"/>
      <Channel C="0" I="DLSEV" O="11" count="1" dimensions="1" long_name="Dog-leg Severity" rep_code="2" units="deg/30m"/>
      <Channel C="0" I="TLTS" O="11" count="1" dimensions="1" long_name="Tool Temperature Static" rep_code="2" units="degC"/>
    </Channels>
    <IFLR count="0">
      <FrameNumbers count="0" rle_len="0"/>
      <LRSH count="0" rle_len="0"/>
      <Xaxis count="0" rle_len="0"/>
    </IFLR>
  </FrameArray>
</LogPass>"""
    assert ostream.getvalue() == expected

