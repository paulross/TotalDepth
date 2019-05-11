"""
RP66V1 file indexer.



Example of multiple LogicalFiles:

tmp/data_unpack/AUS/2010-2015/W005684/Ungani_3_Log_Data_A/Suite3/U3-S3R3-PCOR-FINAL_V1.dlis

"""
import json

import TotalDepth
import datetime
import io
import os
import typing

# import TotalDepth
# import TotalDepth.RP66V1.core.LogPassXML
from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import RepCode, LogPassXML, File
from TotalDepth.RP66V1.core.File import FileLogicalData
from TotalDepth.RP66V1.core.LogicalFile import LogicalFileBase, LogicalFileSequence
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR
from TotalDepth.RP66V1.core.RepCode import ObjectName
from TotalDepth.common import Rle, xml
from TotalDepth.util.XmlWrite import Element, XmlStream
from TotalDepth.util.bin_file_type import binary_file_type_from_path


class ExceptionIndex(ExceptionTotalDepthRP66V1):
    pass


class ExceptionRP66V1IndexXMLRead(ExceptionIndex):
    pass


class LogicalFileRP66V1IndexXML(LogicalFileBase):
    ALL_OBJECTS_SET_TYPES: typing.Set[bytes] = {b'FILE-HEADER', b'ORIGIN', b'CHANNEL', b'FRAME', b'AXIS'}
    SOME_OBJECTS_SET_TYPES: typing.Dict[bytes, bytes] = {
        b'PARAMETER': {b'CN', b'WN', b'FN', b'DATE', b'LATD', b'LATI', b'LOND', b'LONG'}
    }

    def __init__(self, file_logical_data: FileLogicalData, fhlr: EFLR.ExplicitlyFormattedLogicalRecord):
        super().__init__(file_logical_data, fhlr)
        self.iflr_map: typing.Dict[ObjectName, typing.List[LogPassXML.IFLRData]] = {}
        # self.iflr_frame_number_map: typing.Dict[ObjectName, typing.List[int]] = {}
        # self.iflr_x_value_map: typing.Dict[ObjectName, typing.List[typing.Any]] = {}
        # self.iflr_position_map: typing.Dict[ObjectName, typing.List[int]] = {}

    # Overload @abc.abstractmethod
    def add_eflr(self, file_logical_data: FileLogicalData, eflr: EFLR.ExplicitlyFormattedLogicalRecord, **kwargs) -> None:
        super().add_eflr(file_logical_data, eflr, **kwargs)

    # Overload @abc.abstractmethod
    def add_iflr(self, file_logical_data: FileLogicalData, iflr: IFLR.IndirectlyFormattedLogicalRecord, **kwargs) -> None:
        super().add_iflr(file_logical_data, iflr, **kwargs)
        assert self.log_pass is not None
        self.log_pass[iflr.object_name].read_x_axis(iflr.logical_data, frame_number=0)
        x_value = self.log_pass[iflr.object_name].channels[0].array.mean()

        iflr_data = LogPassXML.IFLRData(
            iflr.frame_number, file_logical_data.position.lrsh_position, x_value
        )
        if iflr.object_name in self.iflr_map:
            self.iflr_map[iflr.object_name].append(iflr_data)
        else:
            self.iflr_map[iflr.object_name] = [iflr_data]
        # try:
        #     self.iflr_map[iflr.object_name].append(iflr_data)
        # except KeyError:
        #     self.iflr_map[iflr.object_name] = [iflr_data]

        # try:
        #     self.iflr_frame_number_map[iflr.object_name].append(iflr.frame_number)
        # except KeyError:
        #     self.iflr_frame_number_map[iflr.object_name] = [iflr.frame_number]
        # try:
        #     self.iflr_x_value_map[iflr.object_name].append(x_value)
        # except KeyError:
        #     self.iflr_x_value_map[iflr.object_name] = [x_value]

    # def _rle(self, frame_object_name: ObjectName, iflr_map: typing.Dict[ObjectName, typing.List[int]]) -> Rle.RLE:
    #     ret = Rle.RLE()
    #     for x in iflr_map[frame_object_name]:
    #         ret.add(x)
    #     return ret
    #
    # def _rle_frame_number(self, frame_object_name: ObjectName) -> Rle.RLE:
    #     return self._rle(frame_object_name, self.iflr_frame_number_map)
    #
    # def _rle_x_axis(self, frame_object_name: ObjectName) -> Rle.RLE:
    #     return self._rle(frame_object_name, self.iflr_x_value_map)
    #
    # def _rle_lsrh_positions(self, frame_object_name: ObjectName) -> Rle.RLE:
    #     return self._rle(frame_object_name, self.iflr_x_value_map)

    def write_xml(self, xml_stream: XmlStream) -> None:
        with Element(xml_stream, 'LogicalFile', {
            'has_log_pass' : str(self.log_pass is not None),
            'schema_version': LogPassXML.XML_SCHEMA_VERSION,
        }):
            for position, eflr in self.eflrs:
                attrs = {
                    'vr_position': f'0x{position.vr_position:x}',
                    'lrsh_position': f'0x{position.lrsh_position:x}',
                    'lr_type': f'{eflr.lr_type:d}',
                    'set_type': f'{eflr.set.type.decode("ascii")}',
                    'set_name': f'{eflr.set.name.decode("ascii")}',
                    'object_count': f'{len(eflr.objects):d}'
                }
                with Element(xml_stream, 'EFLR', attrs):
                    self._write_xml_eflr(xml_stream, eflr)
            if self.log_pass is not None:
                self._write_xml_log_pass(xml_stream)

    def _write_xml_eflr(self, xml_stream: XmlStream, eflr: EFLR.ExplicitlyFormattedLogicalRecord) -> None:
        all_objects: bool = eflr.set.type in self.ALL_OBJECTS_SET_TYPES
        some_objects: typing.Set[bytes] = set()
        if eflr.set.type in self.SOME_OBJECTS_SET_TYPES:
            some_objects = self.SOME_OBJECTS_SET_TYPES[eflr.set.type]
        if all_objects or some_objects:
            for obj in eflr.objects:
                if all_objects or obj.name.I in some_objects:
                    self._write_xml_object(xml_stream, obj)

    def _write_xml_object(self, xml_stream: XmlStream, obj: EFLR.Object) -> None:
        with Element(xml_stream, 'Object', LogPassXML.xml_object_name_attributes(obj.name)):
            for attr in obj.attrs:
                attr_atributes = {
                    'label': attr.label.decode('ascii'),
                    'count': f'{attr.count:d}',
                    'rc': f'{attr.rep_code:d}',
                    # TODO: Remove this as duplicate?
                    'rc_ascii': f'{RepCode.REP_CODE_INT_TO_STR[attr.rep_code]}',
                    'units': attr.units.decode('ascii'),
                }
                with Element(xml_stream, 'Attribute', attr_atributes):
                    if attr.value is not None:
                        with Element(xml_stream, 'Values', {'count': f'{len(attr.value)}'}):
                            for v in attr.value:
                                LogPassXML.xml_write_value(xml_stream, v)
                    else:
                        with Element(xml_stream, 'Values', {'count': '0'}):
                            pass

    def _write_xml_log_pass(self, xml_stream: XmlStream) -> None:
        assert self.log_pass is not None
        # # LRSH positions as a RLE
        # rle = self._rle(frame_object.object_name, self.iflr_position_map)
        # LogPassXML.xml_rle_write(rle, 'LRSH', xml_stream, hex_output=True)
        # # Frame number output
        # rle = self._rle(frame_object.object_name, self.iflr_frame_number_map)
        # LogPassXML.xml_rle_write(rle, 'FrameNumbers', xml_stream, hex_output=False)
        # # Xaxis output
        # rle = self._rle(frame_object.object_name, self.iflr_x_value_map)
        # LogPassXML.xml_rle_write(rle, 'Xaxis', xml_stream, hex_output=False)
        LogPassXML.log_pass_to_XML(self.log_pass, self.iflr_map, xml_stream)

        # with Element(xml_stream, 'LogPass', {'count': f'{len(self.log_pass.frame_objects)}'}):
        #     for frame_object in self.log_pass.frame_objects:
        #         assert frame_object.object_name in self.iflr_x_value_map, \
        #             f'{frame_object.object_name} not in {self.iflr_x_value_map.keys()}'
        #         assert frame_object.object_name in self.iflr_position_map, \
        #             f'{frame_object.object_name} not in {self.iflr_position_map.keys()}'
        #         with Element(xml_stream, 'FrameArray', LogPassXML.xml_object_name_attributes(frame_object.object_name)):
        #             with Element(xml_stream, 'Channels', {'channel_count': str(len(frame_object.channels))}):
        #                 for channel in frame_object.channels:
        #                     channel_attrs = LogPassXML.xml_object_name_attributes(channel.object_name)
        #                     channel_attrs['long_name'] = f'{channel.long_name.decode("ascii")}'
        #                     channel_attrs['rep_code'] = f'{channel.rep_code:d}'
        #                     channel_attrs['units'] = f'{channel.units.decode("ascii")}'
        #                     channel_attrs['dimensions'] = ','.join(f'{v:d}' for v in channel.dimensions)
        #                     channel_attrs['count'] = f'{channel.count:d}'
        #                     with Element(xml_stream, 'Channel', channel_attrs):
        #                         pass
        #             # # LRSH positions as a list
        #             # positions = self.iflr_position_map[frame_object.object_name]
        #             # attrs = {
        #             #     'count': f'{len(positions)}',
        #             #     'positions': ','.join([f'0x{p:x}' for p in positions]),
        #             # }
        #             # with Element(xml_stream, 'LRSH', attrs):
        #             #     pass
        #             # LRSH positions as a RLE
        #             rle = self._rle(frame_object.object_name, self.iflr_position_map)
        #             LogPassXML.xml_rle_write(rle, 'LRSH', xml_stream, hex_output=True)
        #             # Frame number output
        #             rle = self._rle(frame_object.object_name, self.iflr_frame_number_map)
        #             LogPassXML.xml_rle_write(rle, 'FrameNumbers', xml_stream, hex_output=False)
        #             # Xaxis output
        #             rle = self._rle(frame_object.object_name, self.iflr_x_value_map)
        #             LogPassXML.xml_rle_write(rle, 'Xaxis', xml_stream, hex_output=False)


class RP66V1IndexXMLWrite(LogicalFileSequence):

    # def __init__(self, fobj: typing.BinaryIO, path: str):
    #     super().__init__(fobj, path)

    # Overload of @abc.abstractmethod
    def create_logical_file(self,
                            file_logical_data: FileLogicalData,
                            eflr: EFLR.ExplicitlyFormattedLogicalRecord, **kwargs) -> LogicalFileBase:
        return LogicalFileRP66V1IndexXML(file_logical_data, eflr)

    # Overload of @abc.abstractmethod
    def create_eflr(self, file_logical_data: FileLogicalData, **kwargs) -> EFLR.ExplicitlyFormattedLogicalRecord:
        assert file_logical_data.lr_is_eflr
        assert file_logical_data.is_sealed()
        # TODO: Encrypted records?
        # print('TRACE: create_eflr()', file_logical_data)
        if file_logical_data.lr_type in (0, 1, 2, 3, 4, 5):
            eflr = EFLR.ExplicitlyFormattedLogicalRecord(file_logical_data.lr_type, file_logical_data.logical_data)
            return eflr
        return EFLR.ExplicitlyFormattedLogicalRecord(file_logical_data.lr_type, file_logical_data.logical_data)

    def _rle_visible_record_positions(self) -> Rle.RLE:
        ret = Rle.RLE()
        for p in self.visible_record_positions:
            ret.add(p)
        return ret

    # TODO: Take an output path and write directly.
    def write_xml(self) -> typing.TextIO:
        xml_fobj = io.StringIO()
        with XmlStream(xml_fobj) as xml_stream:
            # TODO: Write UTC timestamp of indexing? User? Timestamp of file?
            with Element(xml_stream, 'RP66V1FileIndex', {
                'path': self.path,
                'size': f'{os.path.getsize(self.path):d}',
                'schema_version': LogPassXML.XML_SCHEMA_VERSION,
                'utc_file_mtime' : str(datetime.datetime.utcfromtimestamp(os.stat(self.path).st_mtime)),
                'utc_now' : str(datetime.datetime.utcnow()),
            }):
                with Element(
                        xml_stream, 'StorageUnitLabel',
                        {
                         'sequence_number': str(self.storage_unit_label.storage_unit_sequence_number),
                         'dlis_version': self.storage_unit_label.dlis_version.decode('ascii'),
                         'storage_unit_structure' : self.storage_unit_label.storage_unit_structure.decode('ascii'),
                         'maximum_record_length': str(self.storage_unit_label.maximum_record_length),
                         'storage_set_identifier': self.storage_unit_label.storage_set_identifier.decode('ascii'),
                        }):
                    pass
                with Element(xml_stream, 'LogicalFiles', {'count': f'{len(self.logical_files):d}'}):
                    for logical_file in self.logical_files:
                            logical_file.write_xml(xml_stream)
                # Visible records at the end
                LogPassXML.xml_rle_write(
                    self._rle_visible_record_positions(), 'VisibleRecords', xml_stream, hex_output=True,
                )
        return xml_fobj


# ============== Reading XML ================================

class RP66V1IndexXMLEFLRRead:
    TAG = 'EFLR'

    def __init__(self, element: xml.etree.Element):
        """Reads an EFLR element, example::

            <EFLR lr_type="5" lrsh_position="0x786c" object_count="46" set_name="HzEquipmentProperty" set_type="PARAMETER" vr_position="0x6050"/>
        """
        if element.tag != self.TAG:
            raise LogPassXML.ExceptionIndexXMLRead(f'Got element tag of "{element.tag}" but expected "{self.TAG}"')
        # EFLRs just take the root attributes, not the content.
        self.lr_type = int(element.attrib['lr_type'])
        self.lrsh_position = int(element.attrib['lrsh_position'], 16)
        self.object_count = int(element.attrib['object_count'])
        self.set_name = bytes(element.attrib['set_name'], 'ascii')
        self.set_type = bytes(element.attrib['set_type'], 'ascii')
        self.vr_position = int(element.attrib['vr_position'], 16)


class RP66V1IndexXMLLogicalFileRead:
    TAG = 'LogicalFile'

    def __init__(self, element: xml.etree.Element):
        if element.tag != self.TAG:
            raise LogPassXML.ExceptionIndexXMLRead(f'Got element tag of "{element.tag}" but expected "{self.TAG}"')
        self.eflrs = [
            RP66V1IndexXMLEFLRRead(elem) for elem in element.iterfind('./EFLR')
        ]
        # Log Passes
        self.log_passes = [
            TotalDepth.RP66V1.core.LogPassXML.LogPassRP66V1IndexXML(elem) for elem in element.iterfind('./LogPass')
        ]

    def iter_eflrs(self, rp66v1_file: TotalDepth.RP66V1.core.File) -> typing.Sequence[EFLR.ExplicitlyFormattedLogicalRecord]:
        """Iterate through the EFLR indexes reading them in full."""
        for eflr in self.eflrs:
            file_logical_data: FileLogicalData = rp66v1_file.get_file_logical_data(eflr.vr_position, eflr.lrsh_position)
            yield EFLR.ExplicitlyFormattedLogicalRecord(file_logical_data)


class RP66V1IndexXMLRead:
    """
    Reads an RP66V1 XML index and provides a means to give random access to the original file.
    """
    TAG = 'RP66V1FileIndex'

    def __init__(self, index_path: str, archive_root: str):
        self.index_path = index_path
        self.archive_root = archive_root
        # TODO: Is binary required for XML?
        with open(self.index_path, 'rb') as fobj:
            root: xml.etree.Element = xml.etree.parse(fobj).getroot()
        if root.tag != self.TAG:
            raise LogPassXML.ExceptionIndexXMLRead(f'Got element tag of "{root.tag}" but expected "{self.TAG}"')
        # Read the root element RP66V1FileIndex. Example::
        #
        # <RP66V1FileIndex path="tmp/data_unpack/AUS/2010-2015/W004274/Yulleroo_4_Log_Data_A/LWD/Y4_GR_RES_RM.dlis"
        #     schema_version="0.1.0"
        #     size="1937848"
        #     utc_file_mtime="2019-03-18 16:07:28"
        #     utc_now="2019-04-27 10:24:13.982071">
        if root.attrib['schema_version'] != LogPassXML.XML_SCHEMA_VERSION:
            raise LogPassXML.ExceptionIndexXMLRead(
                f'Found schema version {root.attrib["schema_version"]} but expected {LogPassXML.XML_SCHEMA_VERSION}'
            )
        self.path = root.attrib['path']
        self.size = int(root.attrib['size'])
        # TODO: Write UTC timestamps with +00:00 for timezone.
        self.utc_file_mtime = datetime.datetime.strptime(
            root.attrib['utc_file_mtime'], LogPassXML.XML_TIMESTAMP_FORMAT_NO_TZ,
        )
        self.utc_now = datetime.datetime.strptime(
            root.attrib['utc_now'], LogPassXML.XML_TIMESTAMP_FORMAT_NO_TZ,
        )
        # Read the StorageUnitLabel element. Example::
        #
        # <StorageUnitLabel dlis_version="V1.00" maximum_record_length="8192" sequence_number="1"
        #     storage_set_identifier="Default Storage Set                                         "
        #     storage_unit_structure="RECORD"/>
        sul_element = LogPassXML.xml_single_element(root, './StorageUnitLabel')
        self.dlis_version = bytes(sul_element.attrib['dlis_version'], 'ascii')
        exp = b'V1.00'
        if self.dlis_version != exp:
            raise LogPassXML.ExceptionIndexXMLRead(f'Found DLIS version {self.dlis_version} but expected {exp}')
        # TODO: Error check, > minimum which is?
        # TODO: Error check, > 0
        self.sequence_number = int(sul_element.attrib['sequence_number'])
        if self.sequence_number <= 0:
            raise LogPassXML.ExceptionIndexXMLRead(f'Sequence number must be >0 not {self.sequence_number}')
        self.storage_set_identifier = bytes(sul_element.attrib['storage_set_identifier'], 'ascii')
        self.storage_unit_structure = bytes(sul_element.attrib['storage_unit_structure'], 'ascii')
        exp = b'RECORD'
        if self.storage_unit_structure != exp:
            raise LogPassXML.ExceptionIndexXMLRead(
                f'Found Storage Unit Structure {self.storage_unit_structure} but expected {exp}'
            )
        # Read the Visible Record section and construct a RLE for them. This is for IFLRs that only have their
        # LRSH position, EFLRs record their Visible Record position along with their LRSH position.
        rles = [LogPassXML.xml_rle_read(vr) for vr in root.iterfind('./VisibleRecords')]
        if len(rles) != 1:
            raise LogPassXML.ExceptionIndexXMLRead(f'Found {len(rles)} Visible Records sets but expected 1')
        self.visible_record_rle = rles[0]

        # TODO: Check count?
        self.logical_files: typing.List[RP66V1IndexXMLLogicalFileRead] = [
            RP66V1IndexXMLLogicalFileRead(element) for element in root.iterfind('./LogicalFiles/LogicalFile')
        ]

        self.original_file_path: str = os.path.join(self.archive_root, self.path)
        if not os.path.exists(self.original_file_path):
            raise LogPassXML.ExceptionIndexXMLRead(f'Not a file: "{self.original_file_path}"')
        bin_file_type = binary_file_type_from_path(self.original_file_path)
        if bin_file_type != 'RP66V1':
            raise LogPassXML.ExceptionIndexXMLRead(f'File: "{self.original_file_path}" is not a RP66V1 file but "{bin_file_type}"')
        # References to the binary file and the RP66V1 file reader
        self.file: typing.Union[None, typing.BinaryIO] = None
        self.rp66v1_file: typing.Union[None, File.FileRead] = None

    def __enter__(self):
        if self.file is not None:
            self.file.close()
        self.file = open(self.original_file_path, 'rb')
        self.rp66v1_file = File.FileRead(self.file)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file is not None:
            self.file.close()
        self.file = None
        self.rp66v1_file = None

    def get_logical_data(self, lrsh_seek: int) -> FileLogicalData:
        assert self.rp66v1_file is not None
        return self.rp66v1_file.get_file_logical_data(self._visible_record_position(lrsh_seek), lrsh_seek)

    def _visible_record_position(self, lrsh_position: int) -> int:
        """
        In the index for EFLRs we have the visible and lrsh positions.
        For IFLRs we need to lookup the VR position and this can provide that.

        The return value is used as an argument to TotalDepth.RP66V1.core.File.FileRead#get_file_logical_data().
        """
        return self.visible_record_rle.largest_le(lrsh_position)
