import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core.LogPass import FrameChannelRP66V1, FrameArrayRP66V1, LogPassBase
from TotalDepth.RP66V1.core.RepCode import ObjectName
from TotalDepth.common import Rle, xml
from TotalDepth.util.XmlWrite import XmlStream, Element


class ExceptionIndexXML(ExceptionTotalDepthRP66V1):
    pass


class ExceptionIndexXMLRead(ExceptionIndexXML):
    pass


def xml_single_element(element: xml.etree.Element, xpath: str) -> xml.etree.Element:
    """Selects a single XML element in the Xpath."""
    elems = list(element.iterfind(xpath))
    if len(elems) != 1:
        raise ExceptionIndexXMLRead(f'Expected single element at Xpath {xpath} but found {len(elems)}')
    return elems[0]


def xml_rle_write(rle: Rle.RLE, element_name: str, xml_stream: XmlStream, hex_output: bool) -> None:
    with Element(xml_stream, element_name, {'count': f'{rle.num_values():d}', 'rle_len': f'{len(rle):d}',}):
        for rle_item in rle.rle_items:
            attrs = {
                'datum': f'0x{rle_item.datum:x}' if hex_output else f'{rle_item.datum}',
                'stride': f'0x{rle_item.stride:x}' if hex_output else f'{rle_item.stride}',
                'repeat': f'{rle_item.repeat:d}',
            }
            with Element(xml_stream, 'RLE', attrs):
                pass


def xml_rle_read(element: xml.etree.Element) -> Rle.RLE:
    """Read the RLE values under an element and return the RLE object. Example::

        <VisibleRecords count="237" rle_len="56">
            <RLE datum="0x50" repeat="6" stride="0x2000"/>
            <RLE datum="0xe048" repeat="3" stride="0x2000"/>
            <RLE datum="0x16044" repeat="3" stride="0x2000"/>
        </VisibleRecords>

    May raise an ExceptionIndexXMLRead or other exceptions.
    """
    def _rle_convert_datum_or_stride(attr: str) -> typing.Union[int, float]:
        if attr.startswith('0x'):
            return int(attr, 16)
        if '.' in attr:
            return float(attr)
        return int(attr)

    ret = Rle.RLE()
    # print('TRACE:', element, element.attrib)
    for element_rle in element.iterfind('./RLE'):
        rle_item = Rle.RLEItem(_rle_convert_datum_or_stride(element_rle.attrib['datum']))
        rle_item.repeat = _rle_convert_datum_or_stride(element_rle.attrib['repeat'])
        rle_item.stride = _rle_convert_datum_or_stride(element_rle.attrib['stride'])
        ret.rle_items.append(rle_item)
    # Sanity check on element.attrib['count'] and element.attrib['rle_len']
    count: int = int(element.attrib['count'])
    if count != ret.num_values():
        raise ExceptionIndexXMLRead(f'Expected {count} RLE items but got {ret.num_values()}')
    rle_len: int = int(element.attrib['rle_len'])
    if rle_len != len(ret):
        raise ExceptionIndexXMLRead(f'Expected {rle_len} RLE items but got {len(ret)}')
    return ret


def xml_object_name_attributes(object_name: ObjectName) -> typing.Dict[str, str]:
    return {
        'O': f'{object_name.O}',
        'C': f'{object_name.C}',
        'I': f'{object_name.I.decode("utf8")}',
    }


def xml_write_value(xml_stream: XmlStream, value: typing.Any) -> None:
    """Write a value to the XML stream with specific type as an attribute."""
    if isinstance(value, ObjectName):
        with Element(xml_stream, 'ObjectName', xml_object_name_attributes(value)):
            pass
    else:
        if isinstance(value, bytes):
            typ = 'bytes'
            _value = value.decode('ascii', errors='ignore')
        elif isinstance(value, float):
            typ = 'float'
            _value = str(value)
        elif isinstance(value, int):
            typ = 'int'
            _value = str(value)
        elif isinstance(value, str):
            typ = 'str'
            _value = value
        else:
            typ = 'unknown'
            _value = str(value)
        with Element(xml_stream, 'Value', {'type': typ}):
            xml_stream.characters(_value)


def xml_dump_positions(positions: typing.List[int], limit: int, element_name: str, xml_stream: XmlStream) -> None:
    for i, position in enumerate(positions):
        attrs = {'pos': f'{position:d}', 'posx': f'0x{position:0x}'}
        if i > 0:
            d_pos = positions[i] - positions[i - 1]
            attrs['dpos'] = f'{d_pos:d}'
            attrs['dposx'] = f'0x{d_pos:0x}'
        with Element(xml_stream, element_name, attrs):
            pass
        if i >= limit:
            xml_stream.comment(' TRACE: break ')
            break


XML_SCHEMA_VERSION = '0.1.0'
XML_TIMESTAMP_FORMAT_NO_TZ = '%Y-%m-%d %H:%M:%S.%f'


class FrameChannelRP66V1IndexXML(FrameChannelRP66V1):
    """
    A specialisation of a FrameChannel created from a RP66V1 file index represented in xml.
    """
    TAG = 'Channel'

    def __init__(self, channel_node: xml.etree.Element):
        """Initialise with a XML Channel node.

        Example::

            <Channel C="0" I="DEPTH" O="35" count="1" dimensions="1" long_name="Depth Channel" rep_code="7" units="m"/>
        """
        if channel_node.tag != self.TAG:
            raise ValueError(f'Got element tag of "{channel_node.tag}" but expected "{self.TAG}"')
        super().__init__(
            ident=channel_node.attrib['I'],
            long_name=channel_node.attrib['long_name'],
            rep_code=int(channel_node.attrib['rep_code']),
            units=channel_node.attrib['units'],
            dimensions=[int(v) for v in channel_node.attrib['dimensions'].split(',')],
            function_np_dtype=RepCode.numpy_dtype
        )


class FrameArrayRP66V1IndexXML(FrameArrayRP66V1):
    """
    A specialisation of a FrameObject created from a RP66V1 file index represented in xml.
    """
    TAG = 'FrameArray'

    def __init__(self, frame_node: xml.etree.Element):
        """Initialise with a XML Frame node.

        Example::

            <FrameArray C="0" I="0B" O="11">
              <Channels channel_count="9">
                <Channel C="0" I="DEPT" O="11" count="1" dimensions="1" long_name="MWD Tool Measurement Depth" rep_code="2" units="0.1 in"/>
                <Channel C="0" I="INC" O="11" count="1" dimensions="1" long_name="Inclination" rep_code="2" units="deg"/>
                <Channel C="0" I="AZI" O="11" count="1" dimensions="1" long_name="Azimuth" rep_code="2" units="deg"/>
                ...
              </Channels>
              <LRSH count="83" rle_len="2">
                <RLE datum="0x14ac" repeat="61" stride="0x30"/>
                <RLE datum="0x2050" repeat="20" stride="0x30"/>
              </LRSH>
              <FrameNumbers count="83" rle_len="1">
                <RLE datum="1" repeat="82" stride="1"/>
              </FrameNumbers>
              <Xaxis count="83" rle_len="42">
                <RLE datum="0.0" repeat="1" stride="75197.0"/>
                <RLE datum="154724.0" repeat="1" stride="79882.0"/>
                ...
              </Xaxis>
            </FrameArray>
        """
        if frame_node.tag != self.TAG:
            raise ValueError(f'Got element tag of "{frame_node.tag}" but expected "{self.TAG}"')
        object_name: ObjectName = ObjectName(
            O=frame_node.attrib['O'], C=frame_node.attrib['C'], I=frame_node.attrib['I'],
        )
        super().__init__(object_name)
        for channel_node in frame_node.iterfind('./Channels/Channel'):
            self.channels.append(FrameChannelRP66V1IndexXML(channel_node))
        self._init_channel_map()
        self.rle_lrsh = xml_rle_read(xml_single_element(frame_node, './LRSH'))
        self.number_of_frames = int(xml_single_element(frame_node, './FrameNumbers').attrib['count'])
        rle_frame_numbers = xml_rle_read(xml_single_element(frame_node, './FrameNumbers'))
        self.rle_xaxis = xml_rle_read(xml_single_element(frame_node, './Xaxis'))
        # Sanity check
        if rle_frame_numbers.num_values() != self.number_of_frames:
            raise ExceptionIndexXMLRead(
                f'FrameNumbers count is {self.number_of_frames} but RLE has {rle_frame_numbers.num_values()}'
            )
        if self.rle_lrsh.num_values() != self.number_of_frames:
            raise ExceptionIndexXMLRead(
                f'FrameNumbers count is {self.number_of_frames} but RLE has {self.rle_lrsh.num_values()}'
            )
        if self.rle_xaxis.num_values() != self.number_of_frames:
            raise ExceptionIndexXMLRead(
                f'FrameNumbers count is {self.number_of_frames} but RLE has {self.rle_xaxis.num_values()}'
            )
        # self.init_arrays(self.number_of_frames)

    def iflr_lrsh_position(self, frame_number: int) -> int:
        if frame_number < 0 or frame_number >= self.number_of_frames:
            raise IndexError(f'{frame_number} is out of range')
        return self.rle_lrsh.value(frame_number)


class LogPassRP66V1IndexXML(LogPassBase):
    """

    Reads an XML node 'LogPass' that has 0 or more FrameObject nodes. Example::

        <LogPass count="1">
            <FrameArray C="0" I="0B" O="11">
                ...
            </FrameArray>
            ...
        </LogPass>
    """
    TAG = 'LogPass'

    def __init__(self, log_pass_node: xml.etree.Element):
        if log_pass_node.tag != self.TAG:
            raise ValueError(f'Got element tag of "{log_pass_node.tag}" but expected "{self.TAG}"')
        super().__init__()
        count = int(log_pass_node.attrib['count'])
        for frame_object_node in log_pass_node.iterfind('./FrameArray'):
            self.frame_objects.append(FrameArrayRP66V1IndexXML(frame_object_node))
        if len(self.frame_objects) != count:
            raise ValueError(f'Found {len(self.frame_objects)} FrameArrays but expected {count}')
        self._init_frame_object_map()

