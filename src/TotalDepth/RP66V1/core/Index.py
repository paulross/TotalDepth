"""
RP66V1 file indexer.

Can we make this better?

$ python src/TotalDepth/RP66V1/IndexFile.py tmp/test_detif.dlis -l INFO
Cmd: src/TotalDepth/RP66V1/IndexFile.py tmp/test_detif.dlis -l INFO
<?xml version='1.0' encoding="utf-8"?>
<FileIndex>
  <IndexEntries>
    <EFLR SHA1="6b7ba013e860da531eae6fff9c39d603a5ece629" encrypted="0" lrsh_position="0x54" type="0" vr_position="0x50"/>
    <EFLR SHA1="58e216a4bc49a422dccb303377bc2fe2f52014e9" encrypted="0" lrsh_position="0xd0" type="1" vr_position="0x50"/>
    <EFLR SHA1="7e88d7f4f73f228559f141d85c8be41f58592eb6" encrypted="0" lrsh_position="0x2cc" type="4" vr_position="0x50"/>
    <EFLR SHA1="eee030182ed585a0c5beccdf69fc1ae2c9d27605" encrypted="0" lrsh_position="0x424" type="5" vr_position="0x50"/>
    <EFLR SHA1="632bb1978d9d4129edb0f2bac1976b17cb34850e" encrypted="0" lrsh_position="0x184a" type="5" vr_position="0x50"/>
    <EFLR SHA1="082e643e21ebb9cadbccae10ff4431854a036f03" encrypted="0" lrsh_position="0x1d22" type="3" vr_position="0x50"/>
    <EFLR SHA1="7548e822f065ddac8424f3130381ce726e876cac" encrypted="0" lrsh_position="0x230e" type="128" vr_position="0x2050"/>
    <EFLR SHA1="e5a1ee04227fea556b59e4e0b3364c7d88dc8812" encrypted="0" lrsh_position="0x23b0" type="6" vr_position="0x2050"/>
    <EFLR SHA1="d7581d0c526cc669ff8d53cd41690e6443002429" encrypted="0" lrsh_position="0x2c66" type="6" vr_position="0x2050"/>
    <EFLR SHA1="e59ff72cc9e4dfe57244183fc0e3f81a7b92c77a" encrypted="0" lrsh_position="0x4dae" type="6" vr_position="0x4050"/>
    <EFLR SHA1="971e7b00f1ea25dbdb13507ced87862ba4546389" encrypted="0" lrsh_position="0x664b8" type="0" vr_position="0x664b4"/>
    <EFLR SHA1="16a4f7295d581cbdbc46fd4f548678dc4b10c176" encrypted="0" lrsh_position="0x66534" type="1" vr_position="0x664b4"/>
    <EFLR SHA1="9f19bb954990e0100120b3c478c2af5894a80a67" encrypted="0" lrsh_position="0x666c4" type="4" vr_position="0x664b4"/>
    <EFLR SHA1="8ebb657fc9e48a821f51a2193dde6143bbef24b5" encrypted="0" lrsh_position="0x66810" type="5" vr_position="0x664b4"/>
    <EFLR SHA1="30f7e5494783832d39e3ad5dfc99985cd70be9ba" encrypted="0" lrsh_position="0x670c0" type="5" vr_position="0x664b4"/>
    <EFLR SHA1="e5fde501155df109bdd04ce090472e31d28ed4b7" encrypted="0" lrsh_position="0x673b0" type="3" vr_position="0x664b4"/>
    <EFLR SHA1="90334d159de0c78e0bad653add4f7aefb77171e2" encrypted="0" lrsh_position="0x678f4" type="128" vr_position="0x664b4"/>
    <EFLR SHA1="7e03f65e10119ff3ba8a4433effc27e24366030a" encrypted="0" lrsh_position="0x67996" type="6" vr_position="0x664b4"/>
    <EFLR SHA1="b839c0d9e5b271ee562417b3ea6a5769a703a819" encrypted="0" lrsh_position="0x695a2" type="6" vr_position="0x684b4"/>
  </IndexEntries>
  <IFLRSummary>
    <IFLRSet count="121718">
      <IFLRVisibleRecords count="21979">
        <RLE datum="0x6e4b4" repeat="21978" stride="0x2000"/>
      </IFLRVisibleRecords>
      <LogicalRecords count="121718">
        <RLE datum="0x6f900" repeat="2" stride="0x5c2"/>
        <RLE datum="0x70a4e" repeat="4" stride="0x5c2"/>
        <RLE datum="0x72720" repeat="5" stride="0x5c2"/>
        <RLE datum="0x749b4" repeat="4" stride="0x5c2"/>
        <RLE datum="0x76686" repeat="5" stride="0x5c2"/>
        <RLE datum="0x7891a" repeat="4" stride="0x5c2"/>
        <RLE datum="0x7a5ec" repeat="5" stride="0x5c2"/>
        <RLE datum="0x7c880" repeat="4" stride="0x5c2"/>
        <RLE datum="0x7e552" repeat="5" stride="0x5c2"/>

>>> hex(0x70a4e + (4+1) * 0x5c2)
'0x72718'
>>> 0x72720 - 0x72718
8

>>> hex(0x72720 + (5+1) * 0x5c2)
'0x749ac'
>>> 0x749b4 - 0x749ac
8

>>> hex(0x749b4 + (4+1) * 0x5c2)
'0x7667e'

Ah, it an Visible Record and an extra LRSH:

<VisibleRecord: position=0x000684b4 length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    --<LogicalRecordSegmentHeader: position=0x000684b8 length=0x10ea attributes=0xc1 LR type=  6> Stride: 0x00000b22  2,850
   <LogicalRecordSegmentHeader: position=0x000695a2 length=0x0f12 attributes=0xa0 LR type=  6> Stride: 0x000010ea  4,330
<VisibleRecord: position=0x0006a4b4 length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    ..<LogicalRecordSegmentHeader: position=0x0006a4b8 length=0x1ffc attributes=0xe0 LR type=  6> Stride: 0x00000f16  3,862
<VisibleRecord: position=0x0006c4b4 length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    ..<LogicalRecordSegmentHeader: position=0x0006c4b8 length=0x1ffc attributes=0xe0 LR type=  6> Stride: 0x00002000  8,192
<VisibleRecord: position=0x0006e4b4 length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    --<LogicalRecordSegmentHeader: position=0x0006e4b8 length=0x1448 attributes=0xc1 LR type=  6> Stride: 0x00002000  8,192
   <LogicalRecordSegmentHeader: position=0x0006f900 length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x00001448  5,192
   <LogicalRecordSegmentHeader: position=0x0006fec2 length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x000005c2  1,474
   <LogicalRecordSegmentHeader: position=0x00070484 length=0x0030 attributes=0x20 LR type=  0> Stride: 0x000005c2  1,474
<VisibleRecord: position=0x000704b4 length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    --<LogicalRecordSegmentHeader: position=0x000704b8 length=0x0596 attributes=0x40 LR type=  0> Stride: 0x00000034     52
   <LogicalRecordSegmentHeader: position=0x00070a4e length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x00000596  1,430
   <LogicalRecordSegmentHeader: position=0x00071010 length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x000005c2  1,474
   <LogicalRecordSegmentHeader: position=0x000715d2 length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x000005c2  1,474
   <LogicalRecordSegmentHeader: position=0x00071b94 length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x000005c2  1,474
   <LogicalRecordSegmentHeader: position=0x00072156 length=0x035e attributes=0x20 LR type=  0> Stride: 0x000005c2  1,474
<VisibleRecord: position=0x000724b4 length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    --<LogicalRecordSegmentHeader: position=0x000724b8 length=0x0268 attributes=0x40 LR type=  0> Stride: 0x00000362    866
   <LogicalRecordSegmentHeader: position=0x00072720 length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x00000268    616
   <LogicalRecordSegmentHeader: position=0x00072ce2 length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x000005c2  1,474
   <LogicalRecordSegmentHeader: position=0x000732a4 length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x000005c2  1,474
   <LogicalRecordSegmentHeader: position=0x00073866 length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x000005c2  1,474
   <LogicalRecordSegmentHeader: position=0x00073e28 length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x000005c2  1,474
   <LogicalRecordSegmentHeader: position=0x000743ea length=0x00ca attributes=0x20 LR type=  0> Stride: 0x000005c2  1,474
<VisibleRecord: position=0x000744b4 length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    --<LogicalRecordSegmentHeader: position=0x000744b8 length=0x04fc attributes=0x40 LR type=  0> Stride: 0x000000ce    206
   <LogicalRecordSegmentHeader: position=0x000749b4 length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x000004fc  1,276
   <LogicalRecordSegmentHeader: position=0x00074f76 length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x000005c2  1,474
   <LogicalRecordSegmentHeader: position=0x00075538 length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x000005c2  1,474
   <LogicalRecordSegmentHeader: position=0x00075afa length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x000005c2  1,474
   <LogicalRecordSegmentHeader: position=0x000760bc length=0x03f8 attributes=0x20 LR type=  0> Stride: 0x000005c2  1,474
<VisibleRecord: position=0x000764b4 length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    --<LogicalRecordSegmentHeader: position=0x000764b8 length=0x01ce attributes=0x40 LR type=  0> Stride: 0x000003fc  1,020
   <LogicalRecordSegmentHeader: position=0x00076686 length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x000001ce    462
   <LogicalRecordSegmentHeader: position=0x00076c48 length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x000005c2  1,474
   <LogicalRecordSegmentHeader: position=0x0007720a length=0x05c2 attributes=0x00 LR type=  0> Stride: 0x000005c2  1,474




"""
import collections
import io
import os
import typing

# import TotalDepth
from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core.File import FileRead, FileLogicalData, LogicalRecordPosition, VisibleRecord
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR
from TotalDepth.RP66V1.core.LogicalRecord.LogPass import LogPass
from TotalDepth.RP66V1.core.RepCode import ObjectName
from TotalDepth.common import Rle
from TotalDepth.util.XmlWrite import Element, XmlStream


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


class LogicalRecordIndexEntryBase:
    def __init__(self, fld: FileLogicalData):
        # Just take the data from the VisibleRecord and LogicalRecordSegmentHeader
        self.position: LogicalRecordPosition = fld.position
        self.lr_type: int = fld.lr_type
        self.lr_is_eflr: bool = fld.lr_is_eflr
        self.lr_is_encrypted: bool = fld.lr_is_encrypted
        self.sha1_hexdigest: str = fld.logical_data.sha1.hexdigest()

    def __str__(self) -> str:
        lr_type = 'EFLR' if self.lr_is_eflr else 'IFLR'
        return f'<LogicalRecordIndexEntryBase:' \
            f' LRSH at 0x{self.position.lrsh_position:08x}' \
            f' Type: {self.lr_type:3d}' \
            f' {lr_type}' \
            f' Encrypted: {self.lr_is_encrypted}' \
            f' {self.sha1_hexdigest}'

    def dump(self, os: typing.TextIO) -> None:
        os.write(f'{str(self)}\n')

    def _xml_attributes(self) -> typing.Dict[str, str]:
        return {
            'vr_position': f'0x{self.position.vr_position:x}',
            'lrsh_position': f'0x{self.position.lrsh_position:x}',
            'type': f'{self.lr_type:d}',
            'encrypted': f'{self.lr_is_encrypted:d}',
            'SHA1': f'{self.sha1_hexdigest}',
        }

    def write_xml(self, xml_stream: XmlStream) -> None:
        raise NotImplementedError()

    # def write_xml(self, xml_stream: XmlStream) -> None:
    #     element_name = 'EFLR' if self.lr_is_eflr else 'IFLR'
    #     with Element(
    #             xml_stream,
    #             element_name,
    #             {
    #                 'vr_position': f'0x{self.position.vr_position:x}',
    #                 'lrsh_position': f'0x{self.position.lrsh_position:x}',
    #                 'type': f'{self.lr_type:d}',
    #                 'encrypted': f'{self.lr_is_encrypted:d}',
    #                 'SHA1': f'{self.sha1_hexdigest}',
    #             }):
    #         pass


class EFLRIndexEntry(LogicalRecordIndexEntryBase):
    ALL_OBJECTS_SET_TYPES: typing.Set[bytes] = {b'FILE-HEADER', b'ORIGIN', b'CHANNEL', b'FRAME'}
    SOME_OBJECTS_SET_TYPES: typing.Dict[bytes, bytes] = {
        b'PARAMETER': {b'CN', b'WN', b'FN', b'DATE', b'LATD', b'LATI', b'LOND', b'LONG'}
    }

    def __init__(self, fld: FileLogicalData, eflr: EFLR.ExplicitlyFormattedLogicalRecord):
        super().__init__(fld)
        self.eflr = eflr

    def _xml_attributes(self) -> typing.Dict[str, str]:
        result = super()._xml_attributes()
        result.update(
            {
                 'type': self.eflr.set.type.decode('ascii'),
                 'object_count': f'{len(self.eflr.objects)}',
            }
        )
        return result

    def write_xml(self, xml_stream: XmlStream) -> None:
        with Element(xml_stream, 'EFLR', self._xml_attributes()):
            all_objects: bool = self.eflr.set.type in self.ALL_OBJECTS_SET_TYPES
            some_objects: typing.Set[bytes] = set()
            if self.eflr.set.type in self.SOME_OBJECTS_SET_TYPES:
                some_objects = self.SOME_OBJECTS_SET_TYPES[self.eflr.set.type]
            if all_objects or some_objects:
                for obj in self.eflr.objects:
                    if all_objects or obj.name.I in some_objects:
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
                                        with Element(xml_stream, 'Values', {'count' : f'{len(attr.value)}'}):
                                            for v in attr.value:
                                                xml_write_value(xml_stream, v)
                                    else:
                                        with Element(xml_stream, 'Values', {'count' : '0'}):
                                            pass


# class IFLRIndexEntry(LogicalRecordIndexEntryBase):
#     def __init__(self, fld: FileLogicalData, log_pass: LogPass):
#         super().__init__(fld)
#         iflr = IFLR.IndirectlyFormattedLogicalRecord(fld.lr_type, fld.logical_data)
#         self.object_name: ObjectName = iflr.object_name
#         self.x_axis_value = None
#         if len(iflr.bytes):
#             self.x_axis_value = log_pass.first_channel_value(iflr)


class EncryptedIndexEntry(LogicalRecordIndexEntryBase):
    def __init__(self, fld: FileLogicalData):
        super().__init__(fld)


class IFLRSet:
    def __init__(self, objname: ObjectName):
        self.object_name = objname
        # self.positions: typing.List[LogicalRecordPosition] = []
        # self.visible_record_positions: typing.List[int] = []
        self.logical_record_positions: typing.List[int] = []
        self.x_values = []

    def add_iflr(self, fld: FileLogicalData, iflr: IFLR.IndirectlyFormattedLogicalRecord, log_pass: LogPass) -> None:
        assert iflr.object_name == self.object_name
        assert len(self.logical_record_positions) == len(self.x_values)
        # TODO: Check the logic of positions (increasing)?
        # # Bit of a hack
        # if len(self.visible_record_positions) == 0 or fld.position.vr_position != self.visible_record_positions[-1]:
        #     self.visible_record_positions.append(fld.position.vr_position)
        self.logical_record_positions.append(fld.position.lrsh_position)
        self.x_values.append(log_pass.first_channel_value(iflr))

    # def _rle_visible_record_positions(self) -> Rle.RLE:
    #     ret = Rle.RLE()
    #     # print(f'TRACE: self.visible_record_positions: {self.visible_record_positions}')
    #     for p in self.visible_record_positions:
    #         ret.add(p)
    #     return ret

    def _rle_lrsh_positions(self) -> Rle.RLE:
        ret = Rle.RLE()
        for p in self.logical_record_positions:
            ret.add(p)
        return ret

    def _rle_x_axis(self) -> Rle.RLE:
        ret = Rle.RLE()
        for x in self.x_values:
            ret.add(x)
        return ret

    def dump(self, os: typing.TextIO) -> None:
        assert len(self.logical_record_positions) == len(self.x_values)
        os.write(f'IFLRSet: {self.object_name} IFLRs: {len(self.logical_record_positions):,d}\n')
        # rle = self._rle_visible_record_positions()
        # os.write(f'  IFLR Visible record positions:\n')
        # for r in range(len(rle)):
        #     os.write(f'    {rle[r]}\n')
        rle = self._rle_lrsh_positions()
        os.write(f'  Logical record positions:\n')
        for r in range(len(rle)):
            os.write(f'    {rle[r]}\n')
        rle = self._rle_x_axis()
        os.write(f'  X axis:\n')
        for r in range(len(rle)):
            os.write(f'    {rle[r]}\n')

    def write_xml(self, xml_stream: XmlStream) -> None:
        # with Element(xml_stream, 'IFLRSet', {'count': f'{len(self.logical_record_positions):d}'}):
        # element_name = 'EFLR' if file_logical_data.lr_is_eflr else 'IFLR'
        # xml_write_rle(self._rle_visible_record_positions(), 'IFLRVisibleRecords', xml_stream, hex_output=True)
        # LRSH positions don't really compress with RLE because of interleaved IFLRs.
        # xml_write_rle(self._rle_lrsh_positions(), 'LogicalRecords', xml_stream, hex_output=True)
        # xml_dump_positions(self.logical_record_positions, 32, 'LR', xml_stream)
        # for lr_position in self.logical_record_positions:
        #     with Element(xml_stream, 'LR', {'pos': f'0x{lr_position:0x}'}):
        #         pass
        attrs = {
            'count': f'{len(self.logical_record_positions)}',
            'pos': ','.join(f'0x{v:0x}' for v in self.logical_record_positions),
        }
        with Element(xml_stream, 'LR', attrs):
            pass
        xml_write_rle(self._rle_x_axis(), 'Xaxis', xml_stream, hex_output=False)


class FileIndex:
    # TODO: Split up to base class plus RP66V1 index to XML, XML to RP66V1 index,
    # RP66V1 index to database, database to RP66V1 index.
    XML_SCHEMA_VERSION = '1.0.0'

    def __init__(self, fobj: typing.BinaryIO, path: str):
        self.path = path
        self.file_size = os.path.getsize(path) if path else 0
        # # TODO: File level data such as path, SHA1 etc?
        # self.visible_record_positions: typing.List[int] = []
        # self.logical_record_positions: typing.List[int] = []
        self.index_entries: typing.List[LogicalRecordIndexEntryBase] = []
        self.eflr_channels: typing.Union[None, EFLR.ExplicitlyFormattedLogicalRecord] = None
        self.eflr_frame: typing.Union[None, EFLR.ExplicitlyFormattedLogicalRecord] = None
        self.log_pass: typing.Union[None, LogPass] = None
        self.iflr_summary: typing.Dict[ObjectName, IFLRSet] = {}
        self.visible_record_positions: typing.List[int] = []

        rp66_file = FileRead(fobj)
        self.storage_unit_label = rp66_file.sul
        # Capture all the Visible Records, this can not be done by looking at the Logical Records only
        # as some Visible Records can be missed.
        for vr in rp66_file.iter_visible_records():
            self.visible_record_positions.append(vr.position)
        # Now iterate across the file again for the Logical Records.
        for file_logical_data in rp66_file.iter_logical_records():
            self.add(file_logical_data)

    def _unset_iflr_readers(self) -> None:
        self.eflr_channels = None
        self.eflr_frame = None
        self.log_pass = None
        self.iflr_summary = collections.OrderedDict()

    def _create_log_pass(self) -> None:
        assert self.log_pass is None
        self.iflr_summary = {}
        self.log_pass = LogPass(self.eflr_frame, self.eflr_channels)
        for frame_object in self.log_pass.frame_objects:
            self.iflr_summary[frame_object.object_name] = IFLRSet(frame_object.object_name)
        self.eflr_channels = None
        self.eflr_frame = None

    def add(self, fld: FileLogicalData):
        # TODO: Check the logic of positions (increasing)?
        # # Bit of a hack
        # if len(self.visible_record_positions) == 0 or fld.position.vr_position != self.visible_record_positions[-1]:
        #     self.visible_record_positions.append(fld.position.vr_position)
        # self.logical_record_positions.append(fld.position.lrsh_position)
        # for vr in fld.visible_records:
        #     self.visible_record_positions.add(vr.position)

        if fld.lr_is_encrypted:
            self.index_entries.append(EncryptedIndexEntry(fld))
        else:
            if fld.lr_is_eflr:
                eflr = EFLR.ExplicitlyFormattedLogicalRecord(fld.lr_type, fld.logical_data)
                self.index_entries.append(EFLRIndexEntry(fld, eflr))
                # Hang on to specific data for a LogPAss
                if eflr.set.type == b'FILE-HEADER':
                    self._unset_iflr_readers()
                elif eflr.set.type == b'CHANNEL':
                    assert self.eflr_channels is None
                    self.eflr_channels = eflr
                elif eflr.set.type == b'FRAME':
                    assert self.eflr_frame is None
                    self.eflr_frame = eflr
                if self.eflr_channels is not None and self.eflr_frame is not None:
                    self._create_log_pass()
            else:
                assert self.log_pass is not None
                iflr = IFLR.IndirectlyFormattedLogicalRecord(fld.lr_type, fld.logical_data)
                if len(iflr.bytes):
                    self.iflr_summary[iflr.object_name].add_iflr(fld, iflr, self.log_pass)

    def _rle_visible_record_positions(self) -> Rle.RLE:
        ret = Rle.RLE()
        for p in self.visible_record_positions:
            ret.add(p)
        return ret

    def dump(self, os: typing.TextIO) -> None:
        os.write(f'RP66V1 Index:\n')
        os.write(str(self.storage_unit_label))
        for entry in self.index_entries:
            entry.dump(os)
        for k in self.iflr_summary.keys():
            self.iflr_summary[k].dump(os)

    # TODO: Take an output path and write directly.
    def write_xml(self) -> typing.TextIO:
        xml_fobj = io.StringIO()
        with XmlStream(xml_fobj) as xml_stream:
            with Element(xml_stream, 'RP66V1FileIndex', {
                'path': self.path,
                'size': str(self.file_size),
                'schema_version': self.XML_SCHEMA_VERSION,
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
                with Element(xml_stream, 'IndexEntries', {'count': f'{len(self.index_entries):d}'}):
                    for entry in self.index_entries:
                        entry.write_xml(xml_stream)
                with Element(xml_stream, 'IFLRSummary'):
                    # print('TRACE:', [hex(v) for v in self.visible_record_positions[:8]])
                    # xml_write_rle(self._rle_visible_record_positions(), 'VisibleRecords', xml_stream, hex_output=True)
                    # xml_dump_positions(self.visible_record_positions, 32, 'VR', xml_stream)
                    for k in self.iflr_summary.keys():
                        attrs = xml_object_name_attributes(k)
                        attrs['lr_count'] = f'{len(self.iflr_summary[k].logical_record_positions)}'
                        with Element(xml_stream, 'IFLRSet', attrs):
                            self.iflr_summary[k].write_xml(xml_stream)
                # Visible records at the end
                xml_write_rle(self._rle_visible_record_positions(), 'VisibleRecords', xml_stream, hex_output=True)
        return xml_fobj
