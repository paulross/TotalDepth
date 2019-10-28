"""
RP66V1 file indexer.



Example of multiple LogicalFiles:

tmp/data_unpack/AUS/2010-2015/W005684/Ungani_3_Log_Data_A/Suite3/U3-S3R3-PCOR-FINAL_V1.dlis

"""

import datetime
import os
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import RepCode, LogPassXML, File, StorageUnitLabel, LogicalRecord, LogicalFile
# from TotalDepth.RP66V1.core.LogicalRecord import EFLR
from TotalDepth.common import Rle, xml
from TotalDepth.util import XmlWrite
from TotalDepth.util.bin_file_type import binary_file_type_from_path


class ExceptionIndex(ExceptionTotalDepthRP66V1):
    pass


class ExceptionRP66V1IndexXMLRead(ExceptionIndex):
    pass


XML_SCHEMA_VERSION = '0.1.0'
XML_TIMESTAMP_FORMAT_NO_TZ = '%Y-%m-%d %H:%M:%S.%f'

# UTC with a TZ
# datetime.datetime.utcnow().replace(tzinfo=datetime.timezone(datetime.timedelta(0))).strftime('%Y-%m-%d %H:%M:%S.%f%z')
# '2019-05-14 17:33:01.147341+0000'


def _write_xml_eflr_object(obj: LogicalRecord.EFLR.Object, xml_stream: XmlWrite.XmlStream) -> None:
    with XmlWrite.Element(xml_stream, 'Object', LogPassXML.xml_object_name_attributes(obj.name)):
        for attr in obj.attrs:
            attr_atributes = {
                'label': attr.label.decode('ascii'),
                'count': f'{attr.count:d}',
                'rc': f'{attr.rep_code:d}',
                # TODO: Remove this as duplicate?
                'rc_ascii': f'{RepCode.REP_CODE_INT_TO_STR[attr.rep_code]}',
                'units': attr.units.decode('ascii'),
            }
            # with XmlWrite.Element(xml_stream, 'Attribute', attr_atributes):
            #     if attr.value is not None:
            #         with XmlWrite.Element(xml_stream, 'Values', {'count': f'{len(attr.value)}'}):
            #             for v in attr.value:
            #                 LogPassXML.xml_write_value(xml_stream, v)
            #     else:
            #         with XmlWrite.Element(xml_stream, 'Values', {'count': '0'}):
            #             pass
            with XmlWrite.Element(xml_stream, 'Attribute', attr_atributes):
                if attr.value is not None:
                    for v in attr.value:
                        LogPassXML.xml_write_value(xml_stream, v)
                # else:
                #     with XmlWrite.Element(xml_stream, 'Values', {'count': '0'}):
                #         pass


def write_logical_file_to_xml(logical_file_index: int, logical_file: LogicalFile, xml_stream: XmlWrite.XmlStream, private: bool) -> None:
    with XmlWrite.Element(xml_stream, 'LogicalFile', {
        'has_log_pass': str(logical_file.log_pass is not None),
        'index': f'{logical_file_index:d}',
        # 'schema_version': XML_SCHEMA_VERSION,
    }):
        for position, eflr in logical_file.eflrs:
            attrs = {
                'vr_position': f'0x{position.vr_position:x}',
                'lrsh_position': f'0x{position.lrsh_position:x}',
                'lr_type': f'{eflr.lr_type:d}',
                'set_type': f'{eflr.set.type.decode("ascii")}',
                'set_name': f'{eflr.set.name.decode("ascii")}',
                'object_count': f'{len(eflr.objects):d}'
            }
            with XmlWrite.Element(xml_stream, 'EFLR', attrs):
                if private or LogicalRecord.Types.is_public(eflr.lr_type):
                    for obj in eflr.objects:
                        _write_xml_eflr_object(obj, xml_stream)
        if logical_file.log_pass is not None:
            LogPassXML.log_pass_to_XML(logical_file.log_pass, logical_file.iflr_position_map, xml_stream)


def write_logical_file_sequence_to_xml(logical_file_sequence: LogicalFile.LogicalIndex,
                                       output_stream: typing.TextIO, private: bool) -> None:
    """Takes a LogicalIndex and writes the index to an XML stream."""
    with XmlWrite.XmlStream(output_stream) as xml_stream:
        with XmlWrite.Element(xml_stream, 'RP66V1FileIndex', {
            'path': logical_file_sequence.id,
            'size': f'{os.path.getsize(logical_file_sequence.id):d}',
            'schema_version': XML_SCHEMA_VERSION,
            'utc_file_mtime': str(datetime.datetime.utcfromtimestamp(os.stat(logical_file_sequence.id).st_mtime)),
            'utc_now': str(datetime.datetime.utcnow()),
            'creator': f'{__name__}',
        }):
            with XmlWrite.Element(
                    xml_stream, 'StorageUnitLabel',
                    {
                        'sequence_number': str(logical_file_sequence.storage_unit_label.storage_unit_sequence_number),
                        'dlis_version': logical_file_sequence.storage_unit_label.dlis_version.decode('ascii'),
                        'storage_unit_structure': logical_file_sequence.storage_unit_label.storage_unit_structure.decode('ascii'),
                        'maximum_record_length': str(logical_file_sequence.storage_unit_label.maximum_record_length),
                        'storage_set_identifier': logical_file_sequence.storage_unit_label.storage_set_identifier.decode('ascii'),
                    }):
                pass
            with XmlWrite.Element(xml_stream, 'LogicalFiles', {'count': f'{len(logical_file_sequence.logical_files):d}'}):
                for lf, logical_file in enumerate(logical_file_sequence.logical_files):
                    write_logical_file_to_xml(lf, logical_file, xml_stream, private)
            # Visible records at the end
            rle_visible_records = Rle.create_rle(logical_file_sequence.visible_record_positions)
            LogPassXML.xml_rle_write(rle_visible_records, 'VisibleRecords', xml_stream, hex_output=True)


# ============== Reading XML ================================


def read_logical_file_from_xml(logical_file_node: xml.etree.Element,
                               rp66v1_file: File.FileRead) -> LogicalFile.LogicalFile:
    """Creates a LogicalFile instance from the XML index.

    XML is as follows::

        <LogicalFile has_log_pass="True" schema_version="0.1.0">
          <EFLR lr_type="0" lrsh_position="0x54" object_count="1" set_name="" set_type="FILE-HEADER" vr_position="0x50">
            ...
          </EFLR>
          <EFLR lr_type="1" lrsh_position="0xd0" object_count="1" set_name="" set_type="ORIGIN" vr_position="0x50">
            ...
          </EFLR>
          <!-- More EFLRs -->
          <LogPass>
            <FrameArray C="0" I="1200000T" O="44" description="DOMAIN_TIME">
              <Channels count="4">
                <Channel C="3" I="TIME" O="44" count="1" dimensions="1" long_name="Time Index" rep_code="2" units="ms"/>
                ...
              </Channels>
              <IFLR count="1">
                <FrameNumbers count="1" rle_len="1">
                  <RLE datum="1" repeat="0" stride="0"/>
                </FrameNumbers>
                <LRSH count="1" rle_len="1">
                  <RLE datum="0x1b5dd4" repeat="0" stride="0x0"/>
                </LRSH>
                <Xaxis count="1" rle_len="1">
                  <RLE datum="260419.0" repeat="0" stride="0"/>
                </Xaxis>
              </IFLR>
            </FrameArray>
          </LogPass>
        </LogicalFile>

    We cheat a bit here are read the EFLR from the original file rather than the XML, less efficient but less code.
    This also means the LogPass is created from EFLRs rather than the index using LogPassXML.log_pass_from_XML().
    This could be obviated by creating EFLRs from the index, however this would mean the index needs all of EFLR (or
    do some lazy evaluation).

    We take the IFLR data from the XML index however.
    """
    # FIXME: This should not have to go to the original file. This is reading EFLRs from the file rather than the index.
    assert logical_file_node.tag == 'LogicalFile'
    eflr_nodes: typing.List[xml.etree.Element] = list(logical_file_node.iterfind('./EFLR'))
    # Error checking the EFLRs are sensible.
    if len(eflr_nodes) < 2:
        raise ExceptionRP66V1IndexXMLRead(
            'Not enough EFLRs to create a LogicalFile,'
            ' need at least FILE-HEADER and ORIGIN [RP66V1 2.2.3 Logical File (LF)]'
        )
    if eflr_nodes[0].attrib['set_type'] != 'FILE-HEADER':
        raise ExceptionRP66V1IndexXMLRead(
            'First EFLR in a Logical File must be a FILE-HEADER [RP66V1 2.2.3 Logical File (LF)]'
        )
    if eflr_nodes[1].attrib['set_type'] != 'ORIGIN':
        raise ExceptionRP66V1IndexXMLRead(
            'Second EFLR in a Logical File must be a ORIGIN [RP66V1 2.2.3 Logical File (LF)]'
        )
    fld = rp66v1_file.get_file_logical_data(
        LogPassXML.xml_integer_attribute_read(eflr_nodes[0], 'vr_position'),
        LogPassXML.xml_integer_attribute_read(eflr_nodes[0], 'lrsh_position'),
    )
    logical_file = LogicalFile.LogicalFile(fld, LogicalRecord.EFLR.ExplicitlyFormattedLogicalRecord(fld.lr_type, fld.logical_data))
    for eflr_node in eflr_nodes[1:]:
        fld = rp66v1_file.get_file_logical_data(
            LogPassXML.xml_integer_attribute_read(eflr_node, 'vr_position'),
            LogPassXML.xml_integer_attribute_read(eflr_node, 'lrsh_position'),
        )
        eflr = LogicalRecord.EFLR.ExplicitlyFormattedLogicalRecord(fld.lr_type, fld.logical_data)
        logical_file.add_eflr(fld, eflr)
    for frame_array_node in logical_file_node.iterfind('./LogPass/FrameArray'):
        frame_array_object_name = LogPassXML.xml_object_name(frame_array_node)
        iflr_data = LogPassXML.iflr_data_from_xml(frame_array_node)
        if frame_array_object_name in logical_file.iflr_position_map:
            raise ExceptionRP66V1IndexXMLRead(f'Duplicate Frame Array entry {frame_array_object_name}')
        logical_file.iflr_position_map[frame_array_object_name] = list(iflr_data)
    return logical_file


def read_storage_unit_label_from_xml(root: xml.etree.Element) -> StorageUnitLabel.StorageUnitLabel:
    # Read the StorageUnitLabel element. Example::
    #
    # <StorageUnitLabel dlis_version="V1.00" maximum_record_length="8192" sequence_number="1"
    #     storage_set_identifier="Default Storage Set                                         "
    #     storage_unit_structure="RECORD"/>
    sul_element = LogPassXML.xml_single_element(root, './StorageUnitLabel')
    dlis_version = bytes(sul_element.attrib['dlis_version'], 'ascii')
    exp = b'V1.00'
    if dlis_version != exp:
        raise LogPassXML.ExceptionIndexXMLRead(f'Found DLIS version {dlis_version} but expected {exp}')
    sequence_number = int(sul_element.attrib['sequence_number'])
    if sequence_number <= 0:
        # Reference [RP66V1 2.3.2 Storage Unit Label (SUL), Comment 1]
        raise LogPassXML.ExceptionIndexXMLRead(f'Sequence number must be >0 not {sequence_number}')
    maximum_record_length = int(sul_element.attrib['maximum_record_length'])
    storage_unit_structure = bytes(sul_element.attrib['storage_unit_structure'], 'ascii')
    exp = b'RECORD'
    if storage_unit_structure != exp:
        raise LogPassXML.ExceptionIndexXMLRead(
            f'Found Storage Unit Structure {storage_unit_structure} but expected {exp}'
        )
    storage_set_identifier = bytes(sul_element.attrib['storage_set_identifier'], 'ascii')
    # Assemble the bytes for the StorageUnitLable
    ret = StorageUnitLabel.create_storage_unit_label(
        sequence_number,
        dlis_version,
        maximum_record_length,
        storage_set_identifier
    )
    return ret


def read_logical_index_from_xml(index_path: str, archive_root: str) -> LogicalFile.LogicalIndex:
    # FIXME: This should not have to go to the original file.
    # self.index_path = index_path
    # self.archive_root = archive_root
    # TODO: Is binary required for XML?
    with open(index_path, 'rb') as fobj:
        root: xml.etree.Element = xml.etree.parse(fobj).getroot()
    if root.tag != 'RP66V1FileIndex':
        raise ExceptionRP66V1IndexXMLRead(f'Got element tag of "{root.tag}" but expected "RP66V1FileIndex"')
    # Read the root element RP66V1FileIndex. Example::
    #
    # <RP66V1FileIndex path="tmp/data_unpack/AUS/2010-2015/W004274/Yulleroo_4_Log_Data_A/LWD/Y4_GR_RES_RM.dlis"
    #     schema_version="0.1.0"
    #     size="1937848"
    #     utc_file_mtime="2019-03-18 16:07:28"
    #     utc_now="2019-04-27 10:24:13.982071">
    if root.attrib['schema_version'] != XML_SCHEMA_VERSION:
        raise ExceptionRP66V1IndexXMLRead(
            f'Found schema version {root.attrib["schema_version"]} but expected {XML_SCHEMA_VERSION}'
        )
    path = root.attrib['path']

    original_file_path: str = os.path.join(archive_root, path)
    if not os.path.isfile(original_file_path):
        raise ExceptionRP66V1IndexXMLRead(f'Not a file: "{original_file_path}"')
    bin_file_type = binary_file_type_from_path(original_file_path)
    if bin_file_type != 'RP66V1':
        raise ExceptionRP66V1IndexXMLRead(
            f'File: "{original_file_path}" is not a RP66V1 file but "{bin_file_type}"')

    # size = int(root.attrib['size'])
    # utc_file_mtime = datetime.datetime.strptime(
    #     root.attrib['utc_file_mtime'], XML_TIMESTAMP_FORMAT_NO_TZ,
    # )
    # utc_now = datetime.datetime.strptime(
    #     root.attrib['utc_now'], XML_TIMESTAMP_FORMAT_NO_TZ,
    # )
    logical_index = LogicalFile.LogicalIndex(None, original_file_path)
    logical_index.storage_unit_label = read_storage_unit_label_from_xml(root)
    # Logical Files
    logical_files_node = LogPassXML.xml_single_element(root, './LogicalFiles')
    logical_file_count = int(logical_files_node.attrib['count'])
    with open(original_file_path, 'rb') as fobj:
        rp66v1file = File.FileRead(fobj)
        for logical_file_node in logical_files_node.iterfind('./LogicalFile'):
            logical_index.logical_files.append(read_logical_file_from_xml(logical_file_node, rp66v1file))
    if len(logical_index.logical_files) != logical_file_count:
        raise ExceptionRP66V1IndexXMLRead(
            f'Found {len(logical_index.logical_files)} logical Files but expected {logical_file_count}'
        )
    # Read the Visible Record section and construct a RLE for them. This is for IFLRs that only have their
    # LRSH position, EFLRs record their Visible Record position along with their LRSH position.
    rle_vr = LogPassXML.xml_rle_read(LogPassXML.xml_single_element(root, './VisibleRecords'))
    logical_index.visible_record_positions = LogicalFile.VisibleRecordPositions(rle_vr.values())
    return logical_index
