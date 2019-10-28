import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import RepCode, LogPass
from TotalDepth.RP66V1.core.XAxis import IFLRReference
from TotalDepth.common import Rle, xml
from TotalDepth.util import XmlWrite


class ExceptionIndexXML(ExceptionTotalDepthRP66V1):
    pass


class ExceptionIndexXMLRead(ExceptionIndexXML):
    pass


class ExceptionLogPassXML(LogPass.ExceptionLogPass):
    pass


# FIXME: A lot of this is generic XML manipulation so move it up the stack into a common place, or RP66V1.common


# FIXME: Move to TotalDepth.common.xml, fix exception
def xml_single_element(element: xml.etree.Element, xpath: str) -> xml.etree.Element:
    """Selects a single XML element in the Xpath."""
    elems = list(element.iterfind(xpath))
    if len(elems) != 1:
        raise ExceptionIndexXMLRead(f'Expected single element at Xpath {xpath} but found {len(elems)}')
    return elems[0]


# FIXME: Move to TotalDepth.common.xml
def xml_rle_write(rle: Rle.RLE, element_name: str, xml_stream: XmlWrite.XmlStream, hex_output: bool) -> None:
    with XmlWrite.Element(xml_stream, element_name, {'count': f'{rle.num_values():d}', 'rle_len': f'{len(rle):d}',}):
        for rle_item in rle.rle_items:
            attrs = {
                'datum': f'0x{rle_item.datum:x}' if hex_output else f'{rle_item.datum}',
                'stride': f'0x{rle_item.stride:x}' if hex_output else f'{rle_item.stride}',
                'repeat': f'{rle_item.repeat:d}',
            }
            with XmlWrite.Element(xml_stream, 'RLE', attrs):
                pass


# FIXME: Move to TotalDepth.common.xml
def xml_integer_attribute_read(element: xml.etree.Element, attr: str) -> int:
    attribute = element.attrib[attr]
    if attribute.startswith('0x'):
        return int(attribute, 16)
    return int(attribute)


# FIXME: Move to TotalDepth.common.xml, fix exception.
def xml_rle_read(element: xml.etree.Element) -> Rle.RLE:
    """Read the RLE values under an element and return the RLE object.

    Example:

    .. code-block:: xml

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


# FIXME: Move to TotalDepth.RP66V1.common.xml
def xml_object_name_attributes(object_name: RepCode.ObjectName) -> typing.Dict[str, str]:
    return {
        'O': f'{object_name.O}',
        'C': f'{object_name.C}',
        'I': f'{object_name.I.decode("ascii")}',
    }


# FIXME: Move to TotalDepth.RP66V1.common.xml
def xml_object_name(node: xml.etree.Element) -> RepCode.ObjectName:
    return RepCode.ObjectName(node.attrib['O'], node.attrib['C'], node.attrib['I'].encode('ascii'))


# FIXME: Move to TotalDepth.RP66V1.common.xml possibly some common stuff here?
def xml_write_value(xml_stream: XmlWrite.XmlStream, value: typing.Any) -> None:
    """Write a value to the XML stream with specific type as an attribute.
    This writes either a <Value> or an <ObjectName> element."""
    if isinstance(value, RepCode.ObjectName):
        with XmlWrite.Element(xml_stream, 'ObjectName', xml_object_name_attributes(value)):
            pass
    else:
        if isinstance(value, bytes):
            typ = 'bytes'
            # print('TRACE: xml_write_value()', value)
            _value = value.decode('latin-1')#, errors='ignore')
        elif isinstance(value, float):
            typ = 'float'
            _value = str(value)
        elif isinstance(value, int):
            typ = 'int'
            _value = str(value)
        elif isinstance(value, RepCode.DateTime):
            typ = 'TotalDepth.RP66V1.core.RepCode.DateTime'
            _value = str(value)
        elif isinstance(value, str):
            typ = 'str'
            _value = value
        else:
            typ = 'unknown'
            _value = str(value)
        with XmlWrite.Element(xml_stream, 'Value', {'type': typ, 'value': _value}):
            # xml_stream.characters(_value)
            pass


def frame_channel_to_XML(channel: LogPass.FrameChannel, xml_stream: XmlWrite.XmlStream) -> None:
    """Writes a XML Channel node suitable for RP66V1.

    Example:

    .. code-block:: xml

        <Channel C="0" I="DEPTH" O="35" count="1" dimensions="1" long_name="Depth Channel" rep_code="7" units="m"/>
    """
    channel_attrs = {
        'O': f'{channel.ident.O}',
        'C': f'{channel.ident.C}',
        'I': f'{channel.ident.I.decode("ascii")}',
        'long_name': f'{channel.long_name.decode("ascii")}',
        'rep_code': f'{channel.rep_code:d}',
        'units': f'{channel.units.decode("ascii")}',
        'dimensions': ','.join(f'{v:d}' for v in channel.dimensions),
        'count': f'{channel.count:d}',
    }
    with XmlWrite.Element(xml_stream, 'Channel', channel_attrs):
        pass


def frame_channel_from_XML(channel_node: xml.etree.Element) -> LogPass.FrameChannel:
    """Initialise with a XML Channel node.

    Example:

    .. code-block:: xml

        <Channel C="0" I="DEPTH" O="35" count="1" dimensions="1" long_name="Depth Channel" rep_code="7" units="m"/>
    """
    if channel_node.tag != 'Channel':
        raise ValueError(f'Got element tag of "{channel_node.tag}" but expected "Channel"')
    return LogPass.FrameChannel(
        ident=channel_node.attrib['I'].encode('ascii'),
        long_name=channel_node.attrib['long_name'].encode('ascii'),
        rep_code=int(channel_node.attrib['rep_code']),
        units=channel_node.attrib['units'].encode('ascii'),
        dimensions=[int(v) for v in channel_node.attrib['dimensions'].split(',')],
        function_np_dtype=RepCode.numpy_dtype
    )


def frame_array_to_XML(frame_array: LogPass.FrameArray,
                       iflr_data: typing.Sequence[IFLRReference],
                       xml_stream: XmlWrite.XmlStream) -> None:
    """Writes a XML FrameArray node suitable for RP66V1.

    Example:

    .. code-block:: xml

        <FrameArray C="0" I="0B" O="11" description="">
          <Channels channel_count="9">
            <Channel C="0" I="DEPT" O="11" count="1" dimensions="1" long_name="MWD Tool Measurement Depth" rep_code="2" units="0.1 in"/>
            <Channel C="0" I="INC" O="11" count="1" dimensions="1" long_name="Inclination" rep_code="2" units="deg"/>
            <Channel C="0" I="AZI" O="11" count="1" dimensions="1" long_name="Azimuth" rep_code="2" units="deg"/>
            ...
          </Channels>
          <IFLR count="83">
              <FrameNumbers count="83" rle_len="1">
                <RLE datum="1" repeat="82" stride="1"/>
              </FrameNumbers>
              <LRSH count="83" rle_len="2">
                <RLE datum="0x14ac" repeat="61" stride="0x30"/>
                <RLE datum="0x2050" repeat="20" stride="0x30"/>
              </LRSH>
              <Xaxis count="83" rle_len="42">
                <RLE datum="0.0" repeat="1" stride="75197.0"/>
                <RLE datum="154724.0" repeat="1" stride="79882.0"/>
              </Xaxis>
          </IFLR>
        </FrameArray>
    """
    frame_array_attrs = {
        'O': f'{frame_array.ident.O}',
        'C': f'{frame_array.ident.C}',
        'I': f'{frame_array.ident.I.decode("ascii")}',
        'description': frame_array.description.decode('ascii'),
        'x_axis' : frame_array.channels[0].ident.I.decode("ascii"),
        'x_units' : frame_array.channels[0].units.decode("ascii"),
    }

    with XmlWrite.Element(xml_stream, 'FrameArray', frame_array_attrs):
        with XmlWrite.Element(xml_stream, 'Channels', {'count': f'{len(frame_array)}'}):
            for channel in frame_array.channels:
                    frame_channel_to_XML(channel, xml_stream)
        with XmlWrite.Element(xml_stream, 'IFLR', {'count' : f'{len(iflr_data)}'}):
            # Frame number output
            rle = Rle.create_rle(v.frame_number for v in iflr_data)
            xml_rle_write(rle, 'FrameNumbers', xml_stream, hex_output=False)
            # IFLR file position
            rle = Rle.create_rle(v.logical_record_position.lrsh_position for v in iflr_data)
            xml_rle_write(rle, 'LRSH', xml_stream, hex_output=True)
            # Xaxis output
            rle = Rle.create_rle(v.x_axis for v in iflr_data)
            xml_rle_write(rle, 'Xaxis', xml_stream, hex_output=False)


def iflr_data_from_xml(frame_array_node: xml.etree.Element) -> typing.Iterator[IFLRReference]:
    """Returns a sequence of IFLRReference objects from XML."""
    iflr_node = xml_single_element(frame_array_node, './IFLR')
    rle_lrsh = xml_rle_read(xml_single_element(iflr_node, './LRSH'))
    rle_frames = xml_rle_read(xml_single_element(iflr_node, './FrameNumbers'))
    rle_xaxis = xml_rle_read(xml_single_element(iflr_node, './Xaxis'))
    if len({int(iflr_node.attrib['count']), rle_lrsh.num_values(), rle_frames.num_values(), rle_xaxis.num_values()}) != 1:
        raise LogPass.ExceptionFrameArrayInit('Mismatched counts of LRSH, FrameNumbers and Xaxis')
    return (IFLRReference(*v) for v in zip(rle_lrsh.values(), rle_frames.values(), rle_xaxis.values()))


def frame_array_from_XML(frame_array_node: xml.etree.Element) \
        -> typing.Tuple[LogPass.FrameArray, typing.Iterator[IFLRReference]]:
    """Initialise a FrameArray from a XML Channel node. For an example of the XML see frame_array_to_XML."""
    if frame_array_node.tag != 'FrameArray':
        raise ValueError(f'Got element tag of "{frame_array_node.tag}" but expected "FrameArray"')
    ret = LogPass.FrameArray(
        ident=xml_object_name(frame_array_node),
        description=frame_array_node.attrib['description'].encode('ascii')
    )
    # TODO: Check Channel count
    for channnel_node in frame_array_node.iterfind('./Channels/Channel'):
        ret.append(frame_channel_from_XML(channnel_node))
    return ret, iflr_data_from_xml(frame_array_node)


def log_pass_to_XML(log_pass: LogPass.LogPass,
                    iflr_data_map: typing.Dict[typing.Hashable, typing.Sequence[IFLRReference]],
                    xml_stream: XmlWrite.XmlStream) -> None:
    """Writes a XML LogPass node suitable for RP66V1. Example:

    .. code-block:: xml

        <LogPass count="4">
            <FrameArray C="0" I="600T" O="44" description="">
                ...
            <FrameArray>
            ...
        </LogPass>
    """
    with XmlWrite.Element(xml_stream, 'LogPass', {'count': f'{len(log_pass)}'}):
        for frame_array in log_pass.frame_arrays:
            if frame_array.ident not in iflr_data_map:
                raise ExceptionLogPassXML(f'Missing ident {frame_array.ident} in keys {list(iflr_data_map.keys())}')
            frame_array_to_XML(frame_array, iflr_data_map[frame_array.ident], xml_stream)


def log_pass_from_XML(log_pass_node: xml.etree.Element) \
        -> typing.Tuple[LogPass.LogPass, typing.Dict[typing.Hashable, typing.Iterator[typing.Tuple[int, int, typing.Any]]]]:
    log_pass = LogPass.LogPass()
    iflr_map = {}
    for frame_array_node in log_pass_node.iterfind('./FrameArray'):
        frame_array, iflr_data = frame_array_from_XML(frame_array_node)
        iflr_map[frame_array.ident] = iflr_data
        log_pass.append(frame_array)
    return log_pass, iflr_map
