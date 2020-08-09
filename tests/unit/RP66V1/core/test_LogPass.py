import io
import typing

import numpy as np
import pytest

import TotalDepth.RP66V1.IndexXML
from TotalDepth.RP66V1.core import File, LogPass, RepCode
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR, Types
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
    channel = LogPass.RP66V1FrameChannel(
        ident=RepCode.ObjectName(O=11, C=0, I=b'DEPT'),
        long_name=b'Depth of measurement',
        units=b'm',
        dimensions=dimensions,
        np_dtype=LogPass.DEFAULT_NP_TYPE,
        rep_code=2,
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
    #     RepCode.ObjectName(O=11, C=0, I=b'DEPT'), RepCode.ObjectName(O=11, C=0, I=b'INC'),
    #     RepCode.ObjectName(O=11, C=0, I=b'AZI'), RepCode.ObjectName(O=11, C=0, I=b'MTTVD'),
    #     RepCode.ObjectName(O=11, C=0, I=b'SECT'), RepCode.ObjectName(O=11, C=0, I=b'RCN'),
    #     RepCode.ObjectName(O=11, C=0, I=b'RCE'), RepCode.ObjectName(O=11, C=0, I=b'DLSEV'),
    #     RepCode.ObjectName(O=11, C=0, I=b'TLTS'),
    expected = ['DEPT', 'INC', 'AZI', 'MTTVD', 'SECT', 'RCN', 'RCE', 'DLSEV', 'TLTS',]
    assert list(frame_array.keys()) == expected


def test_log_pass_frame_channel_numpy_indexes():
    log_pass = _log_pass()
    frame_array = log_pass[FRAME_ARRAY_IDENT]
    channel = frame_array['DEPT']
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
            # RepCode.ObjectName(O=11, C=0, I=b'DEPT'),
            # RepCode.ObjectName(O=11, C=0, I=b'INC'),
            # RepCode.ObjectName(O=11, C=0, I=b'SECT'),
    channels = {'DEPT', 'INC', 'SECT'}
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
      <Channel C="0" I="DEPT" O="11" count="1" long_name="MWD Tool Measurement Depth" rep_code="2" shape="0,1" units="0.1 in"/>
      <Channel C="0" I="INC" O="11" count="1" long_name="Inclination" rep_code="2" shape="0,1" units="deg"/>
      <Channel C="0" I="AZI" O="11" count="1" long_name="Azimuth" rep_code="2" shape="0,1" units="deg"/>
      <Channel C="0" I="MTTVD" O="11" count="1" long_name="MWD Tool Measurement TVD" rep_code="2" shape="0,1" units="m"/>
      <Channel C="0" I="SECT" O="11" count="1" long_name="Section" rep_code="2" shape="0,1" units="m"/>
      <Channel C="0" I="RCN" O="11" count="1" long_name="Rectangular Co-ordinates North" rep_code="2" shape="0,1" units="m"/>
      <Channel C="0" I="RCE" O="11" count="1" long_name="Rectangular Co-ordinates East" rep_code="2" shape="0,1" units="m"/>
      <Channel C="0" I="DLSEV" O="11" count="1" long_name="Dog-leg Severity" rep_code="2" shape="0,1" units="deg/30m"/>
      <Channel C="0" I="TLTS" O="11" count="1" long_name="Tool Temperature Static" rep_code="2" shape="0,1" units="degC"/>
    </Channels>
    <IFLR count="0">
      <FrameNumbers count="0" rle_len="0"/>
      <LRSH count="0" rle_len="0"/>
      <Xaxis count="0" rle_len="0"/>
    </IFLR>
  </FrameArray>
</LogPass>"""
    assert ostream.getvalue() == expected

# Taken from core/LogicalRecord/test_LogPass.py

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
    ld = File.LogicalData(BYTES_CHANNEL)
    EFLR.ExplicitlyFormattedLogicalRecord(Types.EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'CHANNEL'], ld)


def test_eflr_channel_attributes():
    ld = File.LogicalData(BYTES_CHANNEL)
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(Types.EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'CHANNEL'], ld)
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
    ld = File.LogicalData(BYTES_CHANNEL)
    channels = EFLR.ExplicitlyFormattedLogicalRecord(
        Types.EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'CHANNEL'], ld
    )
    channel_obnames = [obj.name for obj in channels.objects]
    # print(channel_obnames)
    assert channel_obnames == [
        RepCode.ObjectName(O=11, C=0, I=b'DEPT'), RepCode.ObjectName(O=11, C=0, I=b'INC'),
        RepCode.ObjectName(O=11, C=0, I=b'AZI'), RepCode.ObjectName(O=11, C=0, I=b'MTTVD'),
        RepCode.ObjectName(O=11, C=0, I=b'SECT'), RepCode.ObjectName(O=11, C=0, I=b'RCN'),
        RepCode.ObjectName(O=11, C=0, I=b'RCE'), RepCode.ObjectName(O=11, C=0, I=b'DLSEV'),
        RepCode.ObjectName(O=11, C=0, I=b'TLTS'),
    ]


def test_eflr_frame_ctor():
    ld = File.LogicalData(BYTES_FRAME)
    EFLR.ExplicitlyFormattedLogicalRecord(
        Types.EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'FRAME'], ld
    )


def test_eflr_frame_attributes():
    ld = File.LogicalData(BYTES_FRAME)
    frame = EFLR.ExplicitlyFormattedLogicalRecord(
        Types.EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'FRAME'], ld
    )
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
    ld = File.LogicalData(BYTES_FRAME)
    frame = EFLR.ExplicitlyFormattedLogicalRecord(
        Types.EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[b'FRAME'], ld
    )
    obj = frame[0]
    channels = obj[b'CHANNELS'].value
    assert len(channels) == 9
    assert channels == [
        RepCode.ObjectName(O=11, C=0, I=b'DEPT'), RepCode.ObjectName(O=11, C=0, I=b'INC'),
        RepCode.ObjectName(O=11, C=0, I=b'AZI'), RepCode.ObjectName(O=11, C=0, I=b'MTTVD'),
        RepCode.ObjectName(O=11, C=0, I=b'SECT'), RepCode.ObjectName(O=11, C=0, I=b'RCN'),
        RepCode.ObjectName(O=11, C=0, I=b'RCE'), RepCode.ObjectName(O=11, C=0, I=b'DLSEV'),
        RepCode.ObjectName(O=11, C=0, I=b'TLTS')
    ]


def _create_log_pass():
    ld = File.LogicalData(BYTES_CHANNEL)
    channels = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
    ld = File.LogicalData(BYTES_FRAME)
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
        ld = File.LogicalData(by)
        iflr = IFLR.IndirectlyFormattedLogicalRecord(0, ld)
        # print(iflr)


def test_log_pass_str():
    log_pass: LogPass = _create_log_pass()
    print()
    print(log_pass)
    assert str(log_pass) == """LogPass:
  FrameArray: ID: OBNAME: O: 11 C: 0 I: b'0B' b''
    <FrameChannel: 'DEPT' "b'MWD Tool Measurement Depth'" units: 'b'0.1 in'' count: 1 dimensions: (1,) frames: 0>
    <FrameChannel: 'INC' "b'Inclination'" units: 'b'deg'' count: 1 dimensions: (1,) frames: 0>
    <FrameChannel: 'AZI' "b'Azimuth'" units: 'b'deg'' count: 1 dimensions: (1,) frames: 0>
    <FrameChannel: 'MTTVD' "b'MWD Tool Measurement TVD'" units: 'b'm'' count: 1 dimensions: (1,) frames: 0>
    <FrameChannel: 'SECT' "b'Section'" units: 'b'm'' count: 1 dimensions: (1,) frames: 0>
    <FrameChannel: 'RCN' "b'Rectangular Co-ordinates North'" units: 'b'm'' count: 1 dimensions: (1,) frames: 0>
    <FrameChannel: 'RCE' "b'Rectangular Co-ordinates East'" units: 'b'm'' count: 1 dimensions: (1,) frames: 0>
    <FrameChannel: 'DLSEV' "b'Dog-leg Severity'" units: 'b'deg/30m'' count: 1 dimensions: (1,) frames: 0>
    <FrameChannel: 'TLTS' "b'Tool Temperature Static'" units: 'b'degC'' count: 1 dimensions: (1,) frames: 0>"""


def test_example_iflr_process():
    log_pass: LogPass.LogPass = _create_log_pass()
    # ObjectName(O=11, C=0, I=b'0B')
    frame_array: LogPass.FrameArray = log_pass[RepCode.ObjectName(11, 0, b'0B')]
    frame_array.init_arrays(len(BYTES_IFLR))
    # print()
    for frame_number, by in enumerate(BYTES_IFLR):
        ld = File.LogicalData(by)
        _iflr = IFLR.IndirectlyFormattedLogicalRecord(0, ld)
        # frame_array.read_x_axis(ld, frame_number=0)
        frame_array.read(ld, frame_number=frame_number)
        # print(frame_array)
    # print()
    expected = [
        # X axis
        np.array(
            [
                [0.],
                [75197.],
                [154724.],
                [234606.],
                [311024.],
                [381102.],
                [386839.],
                [428193.],
                [447720.],
                [466339.],
                [489547.],
                [500559.],
                [523772.],
                [538638.],
                [542417.],
                [550409.],
            ]
        ),
        np.array(
            [
                [0.],
                 [0.50002027],
                 [0.50002027],
                 [0.7500017],
                 [0.50002027],
                 [0.99998325],
                 [0.9699998],
                 [0.9699998],
                 [0.69999975],
                 [1.0600001],
                 [0.9699998],
                 [0.8800001],
                 [0.78999996],
                 [1.7599998],
                 [2.2000003],
                 [2.9],
             ],
        ),
        np.array(
            [
                [0.],
                [0.],
                [0.],
                [0.],
                [0.],
                [0.],
                [200.44],
                [205.45],
                [206.18],
                [208.69],
                [202.7],
                [200.93],
                [255.77002],
                [243.87],
                [241.15],
                [240.7],
            ]
        ),
        np.array(
            [
                [0.],
                [190.99757],
                [392.98987],
                [595.8777],
                [789.96594],
                [967.95013],
                [982.51935],
                [1087.5443],
                [1137.139],
                [1184.4233],
                [1243.3641],
                [1271.3306],
                [1330.2852],
                [1368.0354],
                [1377.6296],
                [1397.9094],
            ]
        ),
        np.array(
            [
                [0.],
                [0.833423],
                [2.596255],
                [4.809544],
                [6.92684],
                [9.256786],
                [9.268364],
                [7.632412],
                [6.981416],
                [6.338459],
                [5.399805],
                [4.980779],
                [4.457969],
                [4.138596],
                [3.98476],
                [3.54544],
            ]
        ),
        np.array(
            [
                [0.],
                [0.833423],
                [2.596255],
                [4.809544],
                [6.92684],
                [9.256786],
                [9.268364],
                [7.632412],
                [6.981416],
                [6.338459],
                [5.399805],
                [4.980779],
                [4.457969],
                [4.138596],
                [3.98476],
                [3.54544],
            ]
        ),
        np.array(
            [
                [0.],
                [0.],
                [0.],
                [0.],
                [0.],
                [0.],
                [-0.043073],
                [-0.735641],
                [-1.049728],
                [-1.387169],
                [-1.841496],
                [-2.009587],
                [-2.565323],
                [-3.338264],
                [-3.632012],
                [-4.421124],
            ]
        ),
        np.array(
            [
                [-9.9925000e+02],
                [7.9068176e-02],
                [0.0000000e+00],
                [3.7815217e-02],
                [3.7815217e-02],
                [8.4224798e-02],
                [3.9912241e+00],
                [2.4064228e-02],
                [1.6329297e-01],
                [2.3032904e-01],
                [7.0473805e-02],
                [1.0141353e-01],
                [3.9362201e-01],
                [7.9411954e-01],
                [1.4060384e+00],
                [1.0347618e+00],
            ]
        ),
        np.array(
            [
                [-999.25],
                [-999.25],
                [-999.25],
                [-999.25],
                [-999.25],
                [-999.25],
                [50.3937],
                [56.4173],
                [58.4252],
                [58.4252],
                [62.4409],
                [62.4409],
                [62.4409],
                [62.4409],
                [62.4409],
                [58.4252],
            ]
        ),
    ]
    for c, channel in enumerate(frame_array.channels):
        # print(channel.array)
        # np.testing.assert_array_almost_equal(channel.array, expected[c])
        assert str(channel.array) == str(expected[c])
