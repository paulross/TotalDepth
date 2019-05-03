"""
RP66V1 file indexer.



Example of multiple LogicalFiles:

tmp/data_unpack/AUS/2010-2015/W005684/Ungani_3_Log_Data_A/Suite3/U3-S3R3-PCOR-FINAL_V1.dlis

"""
import collections
import datetime
import io
import os
import typing

# import TotalDepth
from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core.File import FileLogicalData
from TotalDepth.RP66V1.core.LogicalFile import LogicalFileBase, LogicalFileSequence
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR
from TotalDepth.RP66V1.core.RepCode import ObjectName
from TotalDepth.common import Rle
from TotalDepth.util.XmlWrite import Element, XmlStream


class ExceptionIndex(ExceptionTotalDepthRP66V1):
    pass


def xml_write_rle(rle: Rle.RLE, element_name: str, xml_stream: XmlStream, hex_output: bool) -> None:
    with Element(
            xml_stream,
            element_name,
            {
                'count': f'{rle.count:d}',
                'rle_len': f'{len(rle)}',
            }
    ):
        # return None
        for r in range(len(rle)):
            if hex_output:
                datum_attr = f'0x{rle[r].datum:x}'
                if rle[r].stride is not None:
                    stride_attr = f'0x{rle[r].stride:x}'
                else:
                    stride_attr = 'None'
            else:
                datum_attr = f'{rle[r].datum}'
                if rle[r].stride is not None:
                    stride_attr = f'{rle[r].stride}'
                else:
                    stride_attr = 'None'
            attrs = {
                'datum': datum_attr,
                'stride': stride_attr,
                'repeat': str(rle[r].repeat),
            }
            # if r > 0:
            #     d_datum = rle[r].datum - rle[r - 1].datum
            #     attrs['d_datum'] = f'{d_datum:,d}'
            #     attrs['d_datumx'] = f'0x{d_datum:x}'
            with Element(xml_stream, 'RLE', attrs):
                # if r > 0:
                #     d_datum = rle[r].datum - rle[r-1].datum
                #     xml_stream.comment(f' ∆Datum {d_datum:8,d} 0x{d_datum:08x} ')
                pass
            # if r > 16:
            #     xml_stream.comment(' TRACE: break ')
            #     # print('TRACE: break')
            #     break


def xml_object_name_attributes(object_name: ObjectName) -> typing.Dict[str, str]:
    return {
        'O': f'{object_name.O}',
        'C': f'{object_name.C}',
        'I': f'{object_name.I.decode("utf8")}',
    }


def xml_write_value(xml_stream: XmlStream, value: typing.Any) -> None:
    # TODO: Write ObjectName
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


class LogicalFileRP66V1IndexXML(LogicalFileBase):
    XML_SCHEMA_VERSION = '0.1.0'
    ALL_OBJECTS_SET_TYPES: typing.Set[bytes] = {b'FILE-HEADER', b'ORIGIN', b'CHANNEL', b'FRAME', b'AXIS'}
    SOME_OBJECTS_SET_TYPES: typing.Dict[bytes, bytes] = {
        b'PARAMETER': {b'CN', b'WN', b'FN', b'DATE', b'LATD', b'LATI', b'LOND', b'LONG'}
    }

    def __init__(self, file_logical_data: FileLogicalData, fhlr: EFLR.ExplicitlyFormattedLogicalRecord):
        super().__init__(file_logical_data, fhlr)
        self.iflr_frame_number_map: typing.Dict[ObjectName, typing.List[int]] = {}
        self.iflr_x_value_map: typing.Dict[ObjectName, typing.List[typing.Any]] = {}

    # Overload @abc.abstractmethod
    def add_eflr(self, file_logical_data: FileLogicalData, eflr: EFLR.ExplicitlyFormattedLogicalRecordBase, **kwargs) -> None:
        super().add_eflr(file_logical_data, eflr, **kwargs)

    # Overload @abc.abstractmethod
    def add_iflr(self, file_logical_data: FileLogicalData, iflr: IFLR.IndirectlyFormattedLogicalRecord, **kwargs) -> None:
        super().add_iflr(file_logical_data, iflr, **kwargs)
        x_value = self.log_pass.first_channel_value(iflr)
        try:
            self.iflr_frame_number_map[iflr.object_name].append(iflr.frame_number)
        except KeyError:
            self.iflr_frame_number_map[iflr.object_name] = [iflr.frame_number]
        try:
            self.iflr_x_value_map[iflr.object_name].append(x_value)
        except KeyError:
            self.iflr_x_value_map[iflr.object_name] = [x_value]

    def _rle(self, frame_object_name: ObjectName, iflr_map: typing.Dict[ObjectName, typing.List[int]]) -> Rle.RLE:
        ret = Rle.RLE()
        for x in iflr_map[frame_object_name]:
            ret.add(x)
        return ret

    def _rle_frame_number(self, frame_object_name: ObjectName) -> Rle.RLE:
        return self._rle(frame_object_name, self.iflr_frame_number_map)

    def _rle_x_axis(self, frame_object_name: ObjectName) -> Rle.RLE:
        return self._rle(frame_object_name, self.iflr_x_value_map)

    def _rle_lsrh_positions(self, frame_object_name: ObjectName) -> Rle.RLE:
        return self._rle(frame_object_name, self.iflr_x_value_map)

    def write_xml(self, xml_stream: XmlStream) -> None:
        with Element(xml_stream, 'LogicalFile', {
            'has_log_pass' : str(self.log_pass is not None),
            'schema_version': self.XML_SCHEMA_VERSION,
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
        with Element(xml_stream, 'Object', xml_object_name_attributes(obj.name)):
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
                                xml_write_value(xml_stream, v)
                    else:
                        with Element(xml_stream, 'Values', {'count': '0'}):
                            pass

    def _write_xml_log_pass(self, xml_stream: XmlStream) -> None:
        assert self.log_pass is not None
        with Element(xml_stream, 'LogPass', {'count': f'{len(self.log_pass.frame_objects)}'}):
            for frame_object in self.log_pass.frame_objects:
                assert frame_object.object_name in self.iflr_x_value_map, \
                    f'{frame_object.object_name} not in {self.iflr_x_value_map.keys()}'
                assert frame_object.object_name in self.iflr_position_map, \
                    f'{frame_object.object_name} not in {self.iflr_position_map.keys()}'
                with Element(xml_stream, 'FrameObject', xml_object_name_attributes(frame_object.object_name)):
                    with Element(xml_stream, 'Channels', {'channel_count': str(len(frame_object.channels))}):
                        for channel in frame_object.channels:
                            channel_attrs = xml_object_name_attributes(channel.object_name)
                            channel_attrs['long_name'] = f'{channel.long_name.decode("ascii")}'
                            channel_attrs['rep_code'] = f'{channel.rep_code:d}'
                            channel_attrs['units'] = f'{channel.units.decode("ascii")}'
                            channel_attrs['dimensions'] = ','.join(f'{v:d}' for v in channel.dimensions)
                            channel_attrs['count'] = f'{channel.count:d}'
                            with Element(xml_stream, 'Channel', channel_attrs):
                                pass
                    # # LRSH positions as a list
                    # positions = self.iflr_position_map[frame_object.object_name]
                    # attrs = {
                    #     'count': f'{len(positions)}',
                    #     'positions': ','.join([f'0x{p:x}' for p in positions]),
                    # }
                    # with Element(xml_stream, 'LRSH', attrs):
                    #     pass
                    # LRSH positions as a RLE
                    rle = self._rle(frame_object.object_name, self.iflr_position_map)
                    xml_write_rle(rle, 'LRSH', xml_stream, hex_output=True)
                    # Frame number output
                    rle = self._rle(frame_object.object_name, self.iflr_frame_number_map)
                    xml_write_rle(rle, 'FrameNumbers', xml_stream, hex_output=False)
                    # Xaxis output
                    rle = self._rle(frame_object.object_name, self.iflr_x_value_map)
                    xml_write_rle(rle, 'Xaxis', xml_stream, hex_output=False)


class FileRP66V1IndexXML(LogicalFileSequence):
    XML_SCHEMA_VERSION = '0.1.0'

    # def __init__(self, fobj: typing.BinaryIO, path: str):
    #     super().__init__(fobj, path)

    # Overload of @abc.abstractmethod
    def create_logical_file(self,
                            file_logical_data: FileLogicalData,
                            eflr: EFLR.ExplicitlyFormattedLogicalRecord, **kwargs) -> LogicalFileBase:
        return LogicalFileRP66V1IndexXML(file_logical_data, eflr)

    # Overload of @abc.abstractmethod
    def create_eflr(self, file_logical_data: FileLogicalData, **kwargs) -> EFLR.ExplicitlyFormattedLogicalRecordBase:
        assert file_logical_data.lr_is_eflr
        assert file_logical_data.is_sealed()
        # TODO: Encrypted records?
        # print('TRACE: create_eflr()', file_logical_data)
        if file_logical_data.lr_type in (0, 1, 2, 3, 4, 5):
            eflr = EFLR.ExplicitlyFormattedLogicalRecord(file_logical_data.lr_type, file_logical_data.logical_data)
            return eflr
        return EFLR.ExplicitlyFormattedLogicalRecordBase(file_logical_data.lr_type, file_logical_data.logical_data)

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
                'schema_version': self.XML_SCHEMA_VERSION,
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
                xml_write_rle(self._rle_visible_record_positions(), 'VisibleRecords', xml_stream, hex_output=True)
        return xml_fobj
