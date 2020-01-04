import contextlib
import typing

import pytest

import TotalDepth.RP66V1.core.LogicalRecord.Duplicates
from TotalDepth.RP66V1.core.File import LogicalData
from TotalDepth.RP66V1.core.LogicalRecord import EFLR
from TotalDepth.RP66V1.core.LogicalRecord.ComponentDescriptor import ComponentDescriptor
from TotalDepth.RP66V1.core import RepCode, stringify
from TotalDepth.RP66V1.core.RepCode import ObjectName


@pytest.mark.parametrize(
    'ld, expected_type, expected_name',
    (
        (LogicalData(b'\xf0\x07CHANNEL'), b'CHANNEL', b''),
        (LogicalData(b'\xf8\x07CHANNEL\x01\x30'), b'CHANNEL', b'0'),
    )
)
def test_Set(ld, expected_type, expected_name):
    result = EFLR.Set(ld)
    assert result.type == expected_type
    assert result.name == expected_name
    assert ld.remain == 0


@pytest.mark.parametrize(
    'ld, expected_type, expected_name',
    (
        (LogicalData(b'\xf0\x07CHANNEL'), b'CHANNEL', b''),
        (LogicalData(b'\xf8\x07CHANNEL\x01\x30'), b'CHANNEL', b'0'),
    )
)
def test_Set_eq(ld, expected_type, expected_name):
    result = EFLR.Set(ld)
    assert result == result
    assert result != 1


@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b'\xf0\x07CHANNEL'), 9),
        (LogicalData(b'\xf8\x07CHANNEL\x01\x30'), 11),
    )
)
def test_Set_logical_data_consumed(ld, expected):
    result = EFLR.Set(ld)
    assert result.logical_data_consumed == expected
    assert ld.remain == 0


@pytest.mark.parametrize(
    'ld, expected',
    (
        (LogicalData(b'\x00\x07CHANNEL'), 'Component Descriptor does not represent a set but a Absent Attribute.'),
    )
)
def test_Set_raises(ld, expected):
    with pytest.raises(EFLR.ExceptionEFLRSet) as err:
        EFLR.Set(ld)
    assert err.value.args[0] == expected


@pytest.mark.parametrize(
    'ld, expected',
    (
        (
            LogicalData(b'\xf0\x07CHANNEL'),
            'Trying to create a Set where the LogicalData <LogicalData Len: 0x9 Idx: 0x1> index is non-zero.',
        ),
    )
)
def test_Set_raises_logical_data(ld, expected):
    ld.seek(1)
    with pytest.raises(EFLR.ExceptionEFLRSet) as err:
        EFLR.Set(ld)
    assert err.value.args[0] == expected


@pytest.mark.parametrize(
    'cd, expected_label, expected_count, expected_rep_code, expected_units, expected_value',
    (
        (ComponentDescriptor(0x00), b'', 1, 19, b'', None),
        (ComponentDescriptor(0x20), b'', 1, 19, b'', None),
        (ComponentDescriptor(0x40), b'', 1, 19, b'', None),
    )
)
def test_AttributeBase(cd, expected_label, expected_count, expected_rep_code, expected_units, expected_value):
    result = EFLR.AttributeBase(cd)
    assert result.label == expected_label
    assert result.count == expected_count
    assert result.rep_code == expected_rep_code
    assert result.units == expected_units
    assert result.value == expected_value


@pytest.mark.parametrize(
    'cd, expected',
    (
        (ComponentDescriptor(0x70), 'Component Descriptor does not represent a attribute but a Object.'),
        (ComponentDescriptor(0xb0), 'Component Descriptor does not represent a attribute but a Redundant Set.'),
        (ComponentDescriptor(0xd0), 'Component Descriptor does not represent a attribute but a Replacement Set.'),
        (ComponentDescriptor(0xf0), 'Component Descriptor does not represent a attribute but a Set.'),
    )
)
def test_AttributeBase_raises(cd, expected):
    with pytest.raises(EFLR.ExceptionEFLRAttribute) as err:
        EFLR.AttributeBase(cd)
    assert err.value.args[0] == expected


@pytest.mark.parametrize(
    'cd_a, cd_b, expected',
    (
        (ComponentDescriptor(0x00), ComponentDescriptor(0x00), True),
        (ComponentDescriptor(0x00), ComponentDescriptor(0x20), False),
    )
)
def test_AttributeBase_eq(cd_a, cd_b, expected):
    a = EFLR.AttributeBase(cd_a)
    b = EFLR.AttributeBase(cd_b)
    assert (a == b) == expected
    assert a != 1


@pytest.mark.parametrize(
    'cd, expected',
    (
        (ComponentDescriptor(0x00), "CD: 000 00000 L: b'' C: 1 R: 19 (IDENT) U: b'' V: None"),
        (ComponentDescriptor(0x20), "CD: 001 00000 L: b'' C: 1 R: 19 (IDENT) U: b'' V: None"),
        (ComponentDescriptor(0x40), "CD: 010 00000 L: b'' C: 1 R: 19 (IDENT) U: b'' V: None"),
    )
)
def test_AttributeBase_str(cd, expected):
    result = EFLR.AttributeBase(cd)
    assert str(result) == expected


@pytest.mark.parametrize(
    'cd, ld, expected_label, expected_count, expected_rep_code, expected_units, expected_value',
    (
        # All defaults
        (ComponentDescriptor(0x20), LogicalData(b''), b'', 1, 19, b'', None),
        # Label only
        (ComponentDescriptor(0x30), LogicalData(b'\x09LONG-NAME'), b'LONG-NAME', 1, 19, b'', None),
        # Count only
        (ComponentDescriptor(0x28), LogicalData(b'\x7f'), b'', 127, 19, b'', None),
        # RepCode only
        (ComponentDescriptor(0x24), LogicalData(b'\x11'), b'', 1, 17, b'', None),
        # Units only
        (ComponentDescriptor(0x22), LogicalData(b'\x05METRE'), b'', 1, 19, b'METRE', None),
        # Value only
        (ComponentDescriptor(0x21), LogicalData(b'\x05VALUE'), b'', 1, 19, b'', [b'VALUE']),
        # Label and RepCode
        (ComponentDescriptor(0x34), LogicalData(b'\x09LONG-NAME\x11'), b'LONG-NAME', 1, 17, b'', None),
        # All five Characteristics
        (
            ComponentDescriptor(0x3f),
            LogicalData(b'\x09LONG-NAME\x02\x13\x05METRE\x06VALUE1\x06VALUE2'),
            b'LONG-NAME', 2, 19, b'METRE', [b'VALUE1', b'VALUE2']),
    )
)
def test_TemplateAttribute(cd, ld, expected_label, expected_count, expected_rep_code, expected_units, expected_value):
    result = EFLR.TemplateAttribute(cd, ld)
    assert result.label == expected_label
    assert result.count == expected_count
    assert result.rep_code == expected_rep_code
    assert result.units == expected_units
    assert result.value == expected_value
    assert ld.remain == 0


@pytest.mark.parametrize(
    'cd, ld, expected',
    (
        # All defaults
        (ComponentDescriptor(0x20), LogicalData(b''), "CD: 001 00000 L: b'' C: 1 R: 19 (IDENT) U: b'' V: None"),
        # Label only
        (
            ComponentDescriptor(0x30), LogicalData(b'\x09LONG-NAME'),
            "CD: 001 10000 L: b'LONG-NAME' C: 1 R: 19 (IDENT) U: b'' V: None"
        ),
        # Count only
        (ComponentDescriptor(0x28), LogicalData(b'\x7f'), "CD: 001 01000 L: b'' C: 127 R: 19 (IDENT) U: b'' V: None"),
        # RepCode only
        (ComponentDescriptor(0x24), LogicalData(b'\x11'), "CD: 001 00100 L: b'' C: 1 R: 17 (ULONG) U: b'' V: None"),
        # Units only
        (
            ComponentDescriptor(0x22), LogicalData(b'\x05METRE'),
            "CD: 001 00010 L: b'' C: 1 R: 19 (IDENT) U: b'METRE' V: None"
        ),
        # Value only
        (
            ComponentDescriptor(0x21), LogicalData(b'\x05VALUE'),
            "CD: 001 00001 L: b'' C: 1 R: 19 (IDENT) U: b'' V: [b'VALUE']"
        ),
        # Label and RepCode
        (
            ComponentDescriptor(0x34), LogicalData(b'\x09LONG-NAME\x11'),
            "CD: 001 10100 L: b'LONG-NAME' C: 1 R: 17 (ULONG) U: b'' V: None"
        ),
        # Label and bad RepCode
        (
            ComponentDescriptor(0x34), LogicalData(b'\x09LONG-NAME\x00'),
            "CD: 001 10100 L: b'LONG-NAME' C: 1 R: 0 (UNKNOWN) U: b'' V: None"
        ),
        # All five Characteristics
        (
            ComponentDescriptor(0x3f),
            LogicalData(b'\x09LONG-NAME\x02\x13\x05METRE\x06VALUE1\x06VALUE2'),
            "CD: 001 11111 L: b'LONG-NAME' C: 2 R: 19 (IDENT) U: b'METRE' V: [b'VALUE1', b'VALUE2']"
        ),
    )
)
def test_TemplateAttribute_str(cd, ld, expected):
    result = EFLR.TemplateAttribute(cd, ld)
    assert str(result) == expected
    assert ld.remain == 0


@pytest.mark.parametrize(
    'cd, ld, expected',
    (
        # V: None
        (ComponentDescriptor(0x20), LogicalData(b''), "-"),
        # Units only
        (ComponentDescriptor(0x22), LogicalData(b'\x05METRE'), "- [METRE]"),
        # Value only as list with one entry, no units
        (ComponentDescriptor(0x21), LogicalData(b'\x05VALUE'), "VALUE"),
        # Value as list with >1 element
        (
            ComponentDescriptor(0x3f),
            LogicalData(b'\x09LONG-NAME\x02\x13\x05METRE\x06VALUE1\x06VALUE2'),
            "[VALUE1, VALUE2] [METRE]"
        ),
        # Units only with b'\xb0' (degree symbol)
        (ComponentDescriptor(0x22), LogicalData(b'\x01\xb0'), "- [°]"),
    )
)
def test_TemplateAttribute_stringify_value(cd, ld, expected):
    result = EFLR.TemplateAttribute(cd, ld)
    assert result.stringify_value(stringify.stringify_object_by_type) == expected
    assert ld.remain == 0


# def test_template():
#     EFLR.Template(
#         LogicalData(
#             # Template
#             # ATTRIB: LR
#             b'\x34\x09LONG-NAME\x17'
#             # ATTRIB: LRV
#             b'\x35\x0dELEMENT-LIMIT\x12\x01'
#             # ATTRIB: LRV
#             b'\x35\x13REPRESENTATION-CODE\x0f\x02'
#             # ATTRIB: L
#             b'\x30\x05UNITS'
#             # ATTRIB: LRV
#             b'\x35\x09DIMENSION\x12\x01'
#             # Object to terminate the template
#             b'\x70'
#         )
#     )

# Example from [RP66V1 Section 3.2.3.2 Figure 3-8]
TEMPLATE_BYTES = (
    # Template
    # ATTRIB: LR
    b'\x34\x09LONG-NAME\x17'
    # ATTRIB: LRV
    b'\x35\x0dELEMENT-LIMIT\x12\x01'
    # ATTRIB: LRV
    b'\x35\x13REPRESENTATION-CODE\x0f\x02'
    # ATTRIB: L
    b'\x30\x05UNITS'
    # ATTRIB: LRV
    b'\x35\x09DIMENSION\x12\x01'
    # Object to terminate the template
    b'\x70'
)

@pytest.mark.parametrize(
    'ld',
    (
        LogicalData(TEMPLATE_BYTES),
    )
)
def test_Template(ld):
    template = EFLR.Template(ld)
    assert ld.remain == 1  # Object byte terminates template
    assert len(template.attrs) == 5
    expected = {
        b'LONG-NAME': 0,
        b'ELEMENT-LIMIT': 1,
        b'REPRESENTATION-CODE': 2,
        b'UNITS': 3,
        b'DIMENSION': 4,
    }
    assert template.attr_label_map == expected


@pytest.mark.parametrize(
    'ld',
    (
        LogicalData(TEMPLATE_BYTES),
    )
)
def test_Template_eq(ld):
    template = EFLR.Template(ld)
    assert template == template
    assert template != 1


@pytest.mark.parametrize(
    'ld',
    (
        LogicalData(TEMPLATE_BYTES),
    )
)
def test_Template_header_as_strings(ld):
    template = EFLR.Template(ld)
    expected = ['LONG-NAME', 'ELEMENT-LIMIT', 'REPRESENTATION-CODE', 'UNITS', 'DIMENSION']
    assert template.header_as_strings(stringify.stringify_object_by_type) == expected


class DataForEFLR(typing.NamedTuple):
    object: LogicalData
    template: LogicalData

    def rewind(self) -> None:
        self.object.rewind()
        self.template.rewind()


# WARN: Mutable objects in this tuple. Must call .rewind() before use.
OBJECT_DATA_FROM_STANDARD: typing.Tuple[DataForEFLR] = (
    DataForEFLR(
        # Example from [RP66V1 Section 3.2.3.2 Figure 3-8]
        LogicalData(
            # Object #1
            # Object: N
            b'\x70\x00\x00\x04TIME'
            # Attribute: V
            b'\x21\x00\x00\x01\x31'
            # Attribute:
            b'\x20'
            # Attribute:
            b'\x20'
            # Attribute: V
            b'\x21\x01S'
            # Object to terminate the object
            b'\x70'
        ),
        LogicalData(
            # Template
            # ATTRIB: LR
            b'\x34\x09LONG-NAME\x17'
            # ATTRIB: LRV
            b'\x35\x0dELEMENT-LIMIT\x12\x01'
            # ATTRIB: LRV
            b'\x35\x13REPRESENTATION-CODE\x0f\x02'
            # ATTRIB: L
            b'\x30\x05UNITS'
            # ATTRIB: LRV
            b'\x35\x09DIMENSION\x12\x01'
            # Object to terminate the template
            b'\x70'
        ),
    ),
    # ...
)


@pytest.mark.parametrize('eflr_data', OBJECT_DATA_FROM_STANDARD)
def test_Object(eflr_data: DataForEFLR):
    eflr_data.rewind()
    template = EFLR.Template(eflr_data.template)
    obj = EFLR.Object(eflr_data.object, template)
    assert obj.name == RepCode.ObjectName(O=0, C=0, I=b'TIME')
    assert eflr_data.object.remain == 1  # Object byte terminates template


def test_Object_attr_label_map():
    OBJECT_DATA_FROM_STANDARD[0].rewind()
    template = EFLR.Template(OBJECT_DATA_FROM_STANDARD[0].template)
    obj = EFLR.Object(OBJECT_DATA_FROM_STANDARD[0].object, template)
    assert obj.attr_label_map == {
        b'LONG-NAME': 0,
        b'ELEMENT-LIMIT': 1,
        b'REPRESENTATION-CODE': 2,
        b'UNITS': 3,
        b'DIMENSION': 4,
    }


def test_Object_getitem_index():
    OBJECT_DATA_FROM_STANDARD[0].rewind()
    template = EFLR.Template(OBJECT_DATA_FROM_STANDARD[0].template)
    obj = EFLR.Object(OBJECT_DATA_FROM_STANDARD[0].object, template)
    assert obj[0].value == [ObjectName(O=0, C=0, I=b'1')]


def test_Object_getitem_label():
    OBJECT_DATA_FROM_STANDARD[0].rewind()
    template = EFLR.Template(OBJECT_DATA_FROM_STANDARD[0].template)
    obj = EFLR.Object(OBJECT_DATA_FROM_STANDARD[0].object, template)
    assert obj[b'LONG-NAME'].value == [ObjectName(O=0, C=0, I=b'1')]


# Example from [RP66V1 Section 3.2.3.2 Figure 3-8]
LOGICAL_BYTES_FROM_STANDARD = (
    # Set: TN
    b'\xf8\x07CHANNEL\x01\x30'

    # Template
    # ATTRIB: LR
    b'\x34\x09LONG-NAME\x17'
    # ATTRIB: LRV
    b'\x35\x0dELEMENT-LIMIT\x12\x01'
    # ATTRIB: LRV
    b'\x35\x13REPRESENTATION-CODE\x0f\x02'
    # ATTRIB: L
    b'\x30\x05UNITS'
    # ATTRIB: LRV
    b'\x35\x09DIMENSION\x12\x01'

    # Object #1
    # Object: N
    b'\x70\x00\x00\x04TIME'
    # Attribute: V
    b'\x21\x00\x00\x01\x31'
    # Attribute:
    b'\x20'
    # Attribute:
    b'\x20'
    # Attribute: V
    b'\x21\x01S'

    # Object #2
    # Object: N
    b'\x70\x01\x00\x08PRESSURE'
    # Attribute: V
    b'\x21\x00\x00\x01\x32'
    # Attribute:
    b'\x20'
    # Attribute:
    b'\x21\x07'
    # Attribute: V
    b'\x21\x03PSI'

    # Object #3
    # Object: N
    b'\x70\x01\x00\x09PAD-ARRAY'
    # Attribute: V
    b'\x21\x00\x00\x01\x33'
    # Attribute: CV
    b'\x29\x02\x08\x14'
    # Attribute: V
    # NOTE: [RP66V1 Error]
    # There is an error in the standard. In [RP66V1 Section 3.2.3.2 Figure 3-8] the third attribute in the third object
    # is specified as b'\x21\x0d' but described as "ATTRIB: V UNORM"
    # In actuality b'\x21\x0d' is "ATTRIB: V SNORM"
    # Correction: "ATTRIB: V UNORM" would be b'\x21\x10'
    # In our case we take the binary not the explanation.
    b'\x21\x0d'
    # Absent Attribute
    b'\x00'
    # Attribute: CV
    b'\x29\x02\x08\x0a'
)

# Example from [RP66V1 Section 3.2.3.2 Figure 3-8]
LOGICAL_BYTES_FROM_STANDARD_SINGLE_OBJECT = (
    # Set: TN
    b'\xf8\x07CHANNEL\x01\x30'

    # Template
    # ATTRIB: LR
    b'\x34\x09LONG-NAME\x17'
    # ATTRIB: LRV
    b'\x35\x0dELEMENT-LIMIT\x12\x01'
    # ATTRIB: LRV
    b'\x35\x13REPRESENTATION-CODE\x0f\x02'
    # ATTRIB: L
    b'\x30\x05UNITS'
    # ATTRIB: LRV
    b'\x35\x09DIMENSION\x12\x01'

    # Object #1
    # Object: N
    b'\x70\x00\x00\x04TIME'
    # Attribute: V
    b'\x21\x00\x00\x01\x31'
    # Attribute:
    b'\x20'
    # Attribute:
    b'\x20'
    # Attribute: V
    b'\x21\x01S'
)


@pytest.mark.parametrize(
    'ld',
    (
        LogicalData(LOGICAL_BYTES_FROM_STANDARD),
    )
)
def test_ExplicitlyFormattedLogicalRecord_smoke_test(ld):
    EFLR.ExplicitlyFormattedLogicalRecord(3, ld)


@pytest.mark.parametrize(
    'ld',
    (
        LogicalData(LOGICAL_BYTES_FROM_STANDARD),
    )
)
def test_ExplicitlyFormattedLogicalRecord_set(ld):
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
    assert eflr.set.type == b'CHANNEL'
    assert eflr.set.name == b'0'


@pytest.mark.parametrize(
    'ld',
    (
        LogicalData(LOGICAL_BYTES_FROM_STANDARD),
    )
)
def test_ExplicitlyFormattedLogicalRecord_template(ld):
    ld.rewind()
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
    assert len(eflr.template) == 5
    # ATTRIB[0]: LR
    assert eflr.template.attrs[0].label == b'LONG-NAME'
    assert eflr.template.attrs[0].rep_code == 0x17
    # ATTRIB[1]: LRV
    assert eflr.template.attrs[1].label == b'ELEMENT-LIMIT'
    assert eflr.template.attrs[1].rep_code == 0x12
    assert eflr.template.attrs[1].value == [1]
    # ATTRIB[2]: LRV
    assert eflr.template.attrs[2].label == b'REPRESENTATION-CODE'
    assert eflr.template.attrs[2].rep_code == 0x0f
    assert eflr.template.attrs[2].value[0] == 0x02
    # ATTRIB[3]: L
    assert eflr.template.attrs[3].label == b'UNITS'
    # ATTRIB[4]: LRV
    assert eflr.template.attrs[4].label == b'DIMENSION'
    assert eflr.template.attrs[4].rep_code == 0x12
    assert eflr.template.attrs[4].value[0] == 0x01


@pytest.mark.parametrize(
    'ld',
    (
        LogicalData(LOGICAL_BYTES_FROM_STANDARD),
    )
)
def test_ExplicitlyFormattedLogicalRecord_objects(ld):
    ld.rewind()
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
    assert len(eflr.template) == 5
    assert len(eflr.objects) == 3
    ## Object #1
    obj_index: int = 0
    assert eflr.objects[0].name == RepCode.ObjectName(0, 0, b'TIME')
    assert len(eflr.objects[0].attrs) == len(eflr.template)
    # Attribute 0
    attr_index = 0
    assert eflr.objects[obj_index].attrs[attr_index].label == b'LONG-NAME'
    assert eflr.objects[obj_index].attrs[attr_index].count == 1
    assert eflr.objects[obj_index].attrs[attr_index].rep_code == RepCode.REP_CODE_STR_TO_INT['OBNAME']
    assert eflr.objects[obj_index].attrs[attr_index].units == b''
    assert eflr.objects[obj_index].attrs[attr_index].value == [RepCode.ObjectName(0, 0, b'1')]
    # Attribute 1
    attr_index = 1
    assert eflr.objects[obj_index].attrs[attr_index].label == b'ELEMENT-LIMIT'
    assert eflr.objects[obj_index].attrs[attr_index].count == 1
    assert eflr.objects[obj_index].attrs[attr_index].rep_code == RepCode.REP_CODE_STR_TO_INT['UVARI']
    assert eflr.objects[obj_index].attrs[attr_index].units == b''
    assert eflr.objects[obj_index].attrs[attr_index].value == [1]
    # Attribute 2
    attr_index = 2
    assert eflr.objects[obj_index].attrs[attr_index].label == b'REPRESENTATION-CODE'
    assert eflr.objects[obj_index].attrs[attr_index].count == 1
    assert eflr.objects[obj_index].attrs[attr_index].rep_code == RepCode.REP_CODE_STR_TO_INT['USHORT']
    assert eflr.objects[obj_index].attrs[attr_index].units == b''
    assert eflr.objects[obj_index].attrs[attr_index].value == [RepCode.REP_CODE_STR_TO_INT['FSINGL']]
    # Attribute 3
    attr_index = 3
    assert eflr.objects[obj_index].attrs[attr_index].label == b'UNITS'
    assert eflr.objects[obj_index].attrs[attr_index].count == 1
    assert eflr.objects[obj_index].attrs[attr_index].rep_code == RepCode.REP_CODE_STR_TO_INT['IDENT']
    assert eflr.objects[obj_index].attrs[attr_index].units == b''
    assert eflr.objects[obj_index].attrs[attr_index].value == [b'S']
    # Attribute 4
    attr_index = 4
    assert eflr.objects[obj_index].attrs[attr_index].label == b'DIMENSION'
    assert eflr.objects[obj_index].attrs[attr_index].count == 1
    assert eflr.objects[obj_index].attrs[attr_index].rep_code == RepCode.REP_CODE_STR_TO_INT['UVARI']
    assert eflr.objects[obj_index].attrs[attr_index].units == b''
    assert eflr.objects[obj_index].attrs[attr_index].value == [1]
    ## Object #2
    obj_index: int = 1
    assert eflr.objects[0].name == RepCode.ObjectName(0, 0, b'TIME')
    assert len(eflr.objects[0].attrs) == len(eflr.template)
    # Attribute 0
    attr_index = 0
    assert eflr.objects[obj_index].attrs[attr_index].label == b'LONG-NAME'
    assert eflr.objects[obj_index].attrs[attr_index].count == 1
    assert eflr.objects[obj_index].attrs[attr_index].rep_code == RepCode.REP_CODE_STR_TO_INT['OBNAME']
    assert eflr.objects[obj_index].attrs[attr_index].units == b''
    assert eflr.objects[obj_index].attrs[attr_index].value == [RepCode.ObjectName(0, 0, b'2')]
    # Attribute 1
    attr_index = 1
    assert eflr.objects[obj_index].attrs[attr_index].label == b'ELEMENT-LIMIT'
    assert eflr.objects[obj_index].attrs[attr_index].count == 1
    assert eflr.objects[obj_index].attrs[attr_index].rep_code == RepCode.REP_CODE_STR_TO_INT['UVARI']
    assert eflr.objects[obj_index].attrs[attr_index].units == b''
    assert eflr.objects[obj_index].attrs[attr_index].value == [1]
    # Attribute 2
    attr_index = 2
    assert eflr.objects[obj_index].attrs[attr_index].label == b'REPRESENTATION-CODE'
    assert eflr.objects[obj_index].attrs[attr_index].count == 1
    assert eflr.objects[obj_index].attrs[attr_index].rep_code == RepCode.REP_CODE_STR_TO_INT['USHORT']
    assert eflr.objects[obj_index].attrs[attr_index].units == b''
    assert eflr.objects[obj_index].attrs[attr_index].value == [RepCode.REP_CODE_STR_TO_INT['FDOUBL']]
    # Attribute 3
    attr_index = 3
    assert eflr.objects[obj_index].attrs[attr_index].label == b'UNITS'
    assert eflr.objects[obj_index].attrs[attr_index].count == 1
    assert eflr.objects[obj_index].attrs[attr_index].rep_code == RepCode.REP_CODE_STR_TO_INT['IDENT']
    assert eflr.objects[obj_index].attrs[attr_index].units == b''
    assert eflr.objects[obj_index].attrs[attr_index].value == [b'PSI']
    # Attribute 4
    attr_index = 4
    assert eflr.objects[obj_index].attrs[attr_index].label == b'DIMENSION'
    assert eflr.objects[obj_index].attrs[attr_index].count == 1
    assert eflr.objects[obj_index].attrs[attr_index].rep_code == RepCode.REP_CODE_STR_TO_INT['UVARI']
    assert eflr.objects[obj_index].attrs[attr_index].units == b''
    assert eflr.objects[obj_index].attrs[attr_index].value == [1]
    ## Object #3
    obj_index: int = 2
    assert eflr.objects[0].name == RepCode.ObjectName(0, 0, b'TIME')
    assert len(eflr.objects[0].attrs) == len(eflr.template)
    # Attribute 0
    attr_index = 0
    assert eflr.objects[obj_index].attrs[attr_index].label == b'LONG-NAME'
    assert eflr.objects[obj_index].attrs[attr_index].count == 1
    assert eflr.objects[obj_index].attrs[attr_index].rep_code == RepCode.REP_CODE_STR_TO_INT['OBNAME']
    assert eflr.objects[obj_index].attrs[attr_index].units == b''
    assert eflr.objects[obj_index].attrs[attr_index].value == [RepCode.ObjectName(0, 0, b'3')]
    # Attribute 1
    attr_index = 1
    assert eflr.objects[obj_index].attrs[attr_index].label == b'ELEMENT-LIMIT'
    assert eflr.objects[obj_index].attrs[attr_index].count == 2
    assert eflr.objects[obj_index].attrs[attr_index].rep_code == RepCode.REP_CODE_STR_TO_INT['UVARI']
    assert eflr.objects[obj_index].attrs[attr_index].units == b''
    assert eflr.objects[obj_index].attrs[attr_index].value == [8, 20]
    # Attribute 2
    attr_index = 2
    assert eflr.objects[obj_index].attrs[attr_index].label == b'REPRESENTATION-CODE'
    assert eflr.objects[obj_index].attrs[attr_index].count == 1
    assert eflr.objects[obj_index].attrs[attr_index].rep_code == RepCode.REP_CODE_STR_TO_INT['USHORT']
    assert eflr.objects[obj_index].attrs[attr_index].units == b''
    # See above for: NOTE: [RP66V1 Error]
    assert eflr.objects[obj_index].attrs[attr_index].value == [RepCode.REP_CODE_STR_TO_INT['SNORM']]
    # Attribute 3
    attr_index = 3
    assert eflr.objects[obj_index].attrs[attr_index].label == b'UNITS'
    assert eflr.objects[obj_index].attrs[attr_index].count == 1
    assert eflr.objects[obj_index].attrs[attr_index].rep_code == RepCode.REP_CODE_STR_TO_INT['IDENT']
    assert eflr.objects[obj_index].attrs[attr_index].units == b''
    assert eflr.objects[obj_index].attrs[attr_index].value is None
    # Attribute 4
    attr_index = 4
    assert eflr.objects[obj_index].attrs[attr_index].label == b'DIMENSION'
    assert eflr.objects[obj_index].attrs[attr_index].count == 2
    assert eflr.objects[obj_index].attrs[attr_index].rep_code == RepCode.REP_CODE_STR_TO_INT['UVARI']
    assert eflr.objects[obj_index].attrs[attr_index].units == b''
    assert eflr.objects[obj_index].attrs[attr_index].value == [8, 10]


@pytest.mark.parametrize(
    'ld',
    (
        LogicalData(LOGICAL_BYTES_FROM_STANDARD),
    )
)
def test_ExplicitlyFormattedLogicalRecord_str_long(ld):
    ld.rewind()
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
    # print(eflr.str_long())
    assert eflr.str_long() == """<ExplicitlyFormattedLogicalRecord EFLR Set type: b'CHANNEL' name: b'0'>
  Template [5]:
    CD: 001 10100 L: b'LONG-NAME' C: 1 R: 23 (OBNAME) U: b'' V: None
    CD: 001 10101 L: b'ELEMENT-LIMIT' C: 1 R: 18 (UVARI) U: b'' V: [1]
    CD: 001 10101 L: b'REPRESENTATION-CODE' C: 1 R: 15 (USHORT) U: b'' V: [2]
    CD: 001 10000 L: b'UNITS' C: 1 R: 19 (IDENT) U: b'' V: None
    CD: 001 10101 L: b'DIMENSION' C: 1 R: 18 (UVARI) U: b'' V: [1]
  Objects [3]:
    OBNAME: O: 0 C: 0 I: b'TIME'
      CD: 001 00001 L: b'LONG-NAME' C: 1 R: 23 (OBNAME) U: b'' V: [ObjectName(O=0, C=0, I=b'1')]
      CD: 001 00000 L: b'ELEMENT-LIMIT' C: 1 R: 18 (UVARI) U: b'' V: [1]
      CD: 001 00000 L: b'REPRESENTATION-CODE' C: 1 R: 15 (USHORT) U: b'' V: [2]
      CD: 001 00001 L: b'UNITS' C: 1 R: 19 (IDENT) U: b'' V: [b'S']
      CD: 001 10101 L: b'DIMENSION' C: 1 R: 18 (UVARI) U: b'' V: [1]
    OBNAME: O: 1 C: 0 I: b'PRESSURE'
      CD: 001 00001 L: b'LONG-NAME' C: 1 R: 23 (OBNAME) U: b'' V: [ObjectName(O=0, C=0, I=b'2')]
      CD: 001 00000 L: b'ELEMENT-LIMIT' C: 1 R: 18 (UVARI) U: b'' V: [1]
      CD: 001 00001 L: b'REPRESENTATION-CODE' C: 1 R: 15 (USHORT) U: b'' V: [7]
      CD: 001 00001 L: b'UNITS' C: 1 R: 19 (IDENT) U: b'' V: [b'PSI']
      CD: 001 10101 L: b'DIMENSION' C: 1 R: 18 (UVARI) U: b'' V: [1]
    OBNAME: O: 1 C: 0 I: b'PAD-ARRAY'
      CD: 001 00001 L: b'LONG-NAME' C: 1 R: 23 (OBNAME) U: b'' V: [ObjectName(O=0, C=0, I=b'3')]
      CD: 001 01001 L: b'ELEMENT-LIMIT' C: 2 R: 18 (UVARI) U: b'' V: [8, 20]
      CD: 001 00001 L: b'REPRESENTATION-CODE' C: 1 R: 15 (USHORT) U: b'' V: [13]
      CD: 000 00000 L: b'UNITS' C: 1 R: 19 (IDENT) U: b'' V: None
      CD: 001 01001 L: b'DIMENSION' C: 2 R: 18 (UVARI) U: b'' V: [8, 10]"""


# Example from [RP66V1 Section 3.2.3.2 Figure 3-8] but with a duplicate object.
LOGICAL_DATA_WITH_EXACT_DUPLICATE = LogicalData(
    # Set: TN
    b'\xf8\x07CHANNEL\x01\x30'

    # Template
    # ATTRIB: LR
    b'\x34\x09LONG-NAME\x17'
    # ATTRIB: LRV
    b'\x35\x0dELEMENT-LIMIT\x12\x01'
    # ATTRIB: LRV
    b'\x35\x13REPRESENTATION-CODE\x0f\x02'
    # ATTRIB: L
    b'\x30\x05UNITS'
    # ATTRIB: LRV
    b'\x35\x09DIMENSION\x12\x01'

    # Object #1
    # Object: N
    b'\x70\x00\x00\x04TIME'
    # Attribute: V
    b'\x21\x00\x00\x01\x31'
    # Attribute:
    b'\x20'
    # Attribute:
    b'\x20'
    # Attribute: V
    b'\x21\x01S'

    # Object #2, TODO: an crafted duplicate that has the same name
    # Object: N
    b'\x70\x00\x00\x04TIME'
    # Attribute: V
    b'\x21\x00\x00\x01\x31'
    # Attribute:
    b'\x20'
    # Attribute:
    b'\x20'
    # Attribute: V
    b'\x21\x01S'
)


# Example from [RP66V1 Section 3.2.3.2 Figure 3-8] but with a duplicate object.
LOGICAL_DATA_WITH_DIFFERENT_DUPLICATE = LogicalData(
    # Set: TN
    b'\xf8\x07CHANNEL\x01\x30'

    # Template
    # ATTRIB: LR
    b'\x34\x09LONG-NAME\x17'
    # ATTRIB: LRV
    b'\x35\x0dELEMENT-LIMIT\x12\x01'
    # ATTRIB: LRV
    b'\x35\x13REPRESENTATION-CODE\x0f\x02'
    # ATTRIB: L
    b'\x30\x05UNITS'
    # ATTRIB: LRV
    b'\x35\x09DIMENSION\x12\x01'

    # Object #1
    # Object: N
    b'\x70\x00\x00\x04TIME'
    # Attribute: V
    b'\x21\x00\x00\x01\x31'
    # Attribute:
    b'\x20'
    # Attribute:
    b'\x20'
    # Attribute: V
    b'\x21\x01S'

    # Object #2, TODO: an crafted object that has the same name but 'SECONDS' rather than 'S' as the units
    # Object: N
    b'\x70\x00\x00\x04TIME'
    # Attribute: V
    b'\x21\x00\x00\x01\x31'
    # Attribute:
    b'\x20'
    # Attribute:
    b'\x20'
    # Attribute: V
    b'\x21\x07SECONDS'
)

# Example from [RP66V1 Section 3.2.3.2 Figure 3-8] but with a duplicate object.
LOGICAL_DATA_WITH_LATER_COPY_DUPLICATE = LogicalData(
    # Set: TN
    b'\xf8\x07CHANNEL\x01\x30'

    # Template
    # ATTRIB: LR
    b'\x34\x09LONG-NAME\x17'
    # ATTRIB: LRV
    b'\x35\x0dELEMENT-LIMIT\x12\x01'
    # ATTRIB: LRV
    b'\x35\x13REPRESENTATION-CODE\x0f\x02'
    # ATTRIB: L
    b'\x30\x05UNITS'
    # ATTRIB: LRV
    b'\x35\x09DIMENSION\x12\x01'

    # Object #1
    # Object: N
    b'\x70\x00\x00\x04TIME'
    # Attribute: V
    b'\x21\x00\x00\x01\x31'
    # Attribute:
    b'\x20'
    # Attribute:
    b'\x20'
    # Attribute: V
    b'\x21\x01S'

    # Object #2, TODO: an crafted duplicate that has the same name but a later copy of 1
    # Object: N
    b'\x70\x00\x01\x04TIME'
    # Attribute: V
    b'\x21\x00\x00\x01\x31'
    # Attribute:
    b'\x20'
    # Attribute:
    b'\x20'
    # Attribute: V
    b'\x21\x01S'
)


@contextlib.contextmanager
def duplicate_object_strategy(strategy: TotalDepth.RP66V1.core.LogicalRecord.Duplicates.DuplicateObjectStrategy):
    previous_strategy: TotalDepth.RP66V1.core.LogicalRecord.Duplicates.DuplicateObjectStrategy \
        = EFLR.ExplicitlyFormattedLogicalRecord.DUPE_OBJECT_STRATEGY
    try:
        EFLR.ExplicitlyFormattedLogicalRecord.DUPE_OBJECT_STRATEGY = strategy
        yield
    finally:
        EFLR.ExplicitlyFormattedLogicalRecord.DUPE_OBJECT_STRATEGY = previous_strategy


@pytest.mark.parametrize(
    'ld',
    (
        LOGICAL_DATA_WITH_EXACT_DUPLICATE,
    )
)
def test_ExplicitlyFormattedLogicalRecord_dupe_exact_default(ld):
    ld.rewind()
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
    # print(eflr.str_long())
    assert eflr.str_long() == """<ExplicitlyFormattedLogicalRecord EFLR Set type: b'CHANNEL' name: b'0'>
  Template [5]:
    CD: 001 10100 L: b'LONG-NAME' C: 1 R: 23 (OBNAME) U: b'' V: None
    CD: 001 10101 L: b'ELEMENT-LIMIT' C: 1 R: 18 (UVARI) U: b'' V: [1]
    CD: 001 10101 L: b'REPRESENTATION-CODE' C: 1 R: 15 (USHORT) U: b'' V: [2]
    CD: 001 10000 L: b'UNITS' C: 1 R: 19 (IDENT) U: b'' V: None
    CD: 001 10101 L: b'DIMENSION' C: 1 R: 18 (UVARI) U: b'' V: [1]
  Objects [1]:
    OBNAME: O: 0 C: 0 I: b'TIME'
      CD: 001 00001 L: b'LONG-NAME' C: 1 R: 23 (OBNAME) U: b'' V: [ObjectName(O=0, C=0, I=b'1')]
      CD: 001 00000 L: b'ELEMENT-LIMIT' C: 1 R: 18 (UVARI) U: b'' V: [1]
      CD: 001 00000 L: b'REPRESENTATION-CODE' C: 1 R: 15 (USHORT) U: b'' V: [2]
      CD: 001 00001 L: b'UNITS' C: 1 R: 19 (IDENT) U: b'' V: [b'S']
      CD: 001 10101 L: b'DIMENSION' C: 1 R: 18 (UVARI) U: b'' V: [1]"""


@pytest.mark.parametrize(
    'ld',
    (
        LOGICAL_DATA_WITH_EXACT_DUPLICATE,
        LOGICAL_DATA_WITH_DIFFERENT_DUPLICATE,
    )
)
def test_ExplicitlyFormattedLogicalRecord_dupe_exact_ignore(ld):
    ld.rewind()
    with duplicate_object_strategy(TotalDepth.RP66V1.core.LogicalRecord.Duplicates.DuplicateObjectStrategy.IGNORE):
        eflr = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
        result = eflr.str_long()
        # print(result)
        expected = """<ExplicitlyFormattedLogicalRecord EFLR Set type: b'CHANNEL' name: b'0'>
  Template [5]:
    CD: 001 10100 L: b'LONG-NAME' C: 1 R: 23 (OBNAME) U: b'' V: None
    CD: 001 10101 L: b'ELEMENT-LIMIT' C: 1 R: 18 (UVARI) U: b'' V: [1]
    CD: 001 10101 L: b'REPRESENTATION-CODE' C: 1 R: 15 (USHORT) U: b'' V: [2]
    CD: 001 10000 L: b'UNITS' C: 1 R: 19 (IDENT) U: b'' V: None
    CD: 001 10101 L: b'DIMENSION' C: 1 R: 18 (UVARI) U: b'' V: [1]
  Objects [1]:
    OBNAME: O: 0 C: 0 I: b'TIME'
      CD: 001 00001 L: b'LONG-NAME' C: 1 R: 23 (OBNAME) U: b'' V: [ObjectName(O=0, C=0, I=b'1')]
      CD: 001 00000 L: b'ELEMENT-LIMIT' C: 1 R: 18 (UVARI) U: b'' V: [1]
      CD: 001 00000 L: b'REPRESENTATION-CODE' C: 1 R: 15 (USHORT) U: b'' V: [2]
      CD: 001 00001 L: b'UNITS' C: 1 R: 19 (IDENT) U: b'' V: [b'S']
      CD: 001 10101 L: b'DIMENSION' C: 1 R: 18 (UVARI) U: b'' V: [1]"""
        for a, b in zip(result.split('\n'), expected.split('\n')):
            assert a == b
        assert result == expected


@pytest.mark.parametrize(
    'ld',
    (
        LOGICAL_DATA_WITH_EXACT_DUPLICATE,
    )
)
def test_ExplicitlyFormattedLogicalRecord_dupe_exact_raise(ld):
    ld.rewind()
    with duplicate_object_strategy(TotalDepth.RP66V1.core.LogicalRecord.Duplicates.DuplicateObjectStrategy.RAISE):
        with pytest.raises(EFLR.ExceptionEFLRSetDuplicateObjectNames) as err:
            EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
        assert err.value.args == (
            "Duplicate Object OBNAME: O: 0 C: 0 I: b'TIME' already seen in the EFLR Set type: b'CHANNEL' name: b'0'.",
        )


@pytest.mark.parametrize(
    'ld, strategy',
    (
        (
            LOGICAL_DATA_WITH_DIFFERENT_DUPLICATE,
            TotalDepth.RP66V1.core.LogicalRecord.Duplicates.DuplicateObjectStrategy.REPLACE,
        ),
        (
            LOGICAL_DATA_WITH_DIFFERENT_DUPLICATE,
            TotalDepth.RP66V1.core.LogicalRecord.Duplicates.DuplicateObjectStrategy.REPLACE_IF_DIFFERENT,
        ),
    )
)
def test_ExplicitlyFormattedLogicalRecord_dupe_diff_replace(ld, strategy):
    ld.rewind()
    with duplicate_object_strategy(strategy):
        eflr = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
        result = eflr.str_long()
        # print(result)
        expected = """<ExplicitlyFormattedLogicalRecord EFLR Set type: b'CHANNEL' name: b'0'>
  Template [5]:
    CD: 001 10100 L: b'LONG-NAME' C: 1 R: 23 (OBNAME) U: b'' V: None
    CD: 001 10101 L: b'ELEMENT-LIMIT' C: 1 R: 18 (UVARI) U: b'' V: [1]
    CD: 001 10101 L: b'REPRESENTATION-CODE' C: 1 R: 15 (USHORT) U: b'' V: [2]
    CD: 001 10000 L: b'UNITS' C: 1 R: 19 (IDENT) U: b'' V: None
    CD: 001 10101 L: b'DIMENSION' C: 1 R: 18 (UVARI) U: b'' V: [1]
  Objects [1]:
    OBNAME: O: 0 C: 0 I: b'TIME'
      CD: 001 00001 L: b'LONG-NAME' C: 1 R: 23 (OBNAME) U: b'' V: [ObjectName(O=0, C=0, I=b'1')]
      CD: 001 00000 L: b'ELEMENT-LIMIT' C: 1 R: 18 (UVARI) U: b'' V: [1]
      CD: 001 00000 L: b'REPRESENTATION-CODE' C: 1 R: 15 (USHORT) U: b'' V: [2]
      CD: 001 00001 L: b'UNITS' C: 1 R: 19 (IDENT) U: b'' V: [b'SECONDS']
      CD: 001 10101 L: b'DIMENSION' C: 1 R: 18 (UVARI) U: b'' V: [1]"""
        for a, b in zip(result.split('\n'), expected.split('\n')):
            assert a == b
        assert result == expected


@pytest.mark.parametrize(
    'ld',
    (
        LOGICAL_DATA_WITH_LATER_COPY_DUPLICATE,
    )
)
def test_ExplicitlyFormattedLogicalRecord_dupe_later_copy(ld):
    """Hmm actually this should fail and only have one object there ???"""
    ld.rewind()
    with duplicate_object_strategy(TotalDepth.RP66V1.core.LogicalRecord.Duplicates.DuplicateObjectStrategy.REPLACE_LATER_COPY):
        eflr = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
        result = eflr.str_long()
        # print(result)
        expected = """<ExplicitlyFormattedLogicalRecord EFLR Set type: b'CHANNEL' name: b'0'>
  Template [5]:
    CD: 001 10100 L: b'LONG-NAME' C: 1 R: 23 (OBNAME) U: b'' V: None
    CD: 001 10101 L: b'ELEMENT-LIMIT' C: 1 R: 18 (UVARI) U: b'' V: [1]
    CD: 001 10101 L: b'REPRESENTATION-CODE' C: 1 R: 15 (USHORT) U: b'' V: [2]
    CD: 001 10000 L: b'UNITS' C: 1 R: 19 (IDENT) U: b'' V: None
    CD: 001 10101 L: b'DIMENSION' C: 1 R: 18 (UVARI) U: b'' V: [1]
  Objects [2]:
    OBNAME: O: 0 C: 0 I: b'TIME'
      CD: 001 00001 L: b'LONG-NAME' C: 1 R: 23 (OBNAME) U: b'' V: [ObjectName(O=0, C=0, I=b'1')]
      CD: 001 00000 L: b'ELEMENT-LIMIT' C: 1 R: 18 (UVARI) U: b'' V: [1]
      CD: 001 00000 L: b'REPRESENTATION-CODE' C: 1 R: 15 (USHORT) U: b'' V: [2]
      CD: 001 00001 L: b'UNITS' C: 1 R: 19 (IDENT) U: b'' V: [b'S']
      CD: 001 10101 L: b'DIMENSION' C: 1 R: 18 (UVARI) U: b'' V: [1]
    OBNAME: O: 0 C: 1 I: b'TIME'
      CD: 001 00001 L: b'LONG-NAME' C: 1 R: 23 (OBNAME) U: b'' V: [ObjectName(O=0, C=0, I=b'1')]
      CD: 001 00000 L: b'ELEMENT-LIMIT' C: 1 R: 18 (UVARI) U: b'' V: [1]
      CD: 001 00000 L: b'REPRESENTATION-CODE' C: 1 R: 15 (USHORT) U: b'' V: [2]
      CD: 001 00001 L: b'UNITS' C: 1 R: 19 (IDENT) U: b'' V: [b'S']
      CD: 001 10101 L: b'DIMENSION' C: 1 R: 18 (UVARI) U: b'' V: [1]"""
        for a, b in zip(result.split('\n'), expected.split('\n')):
            assert a == b
        assert result == expected


PARAMETER_TABLE_BYTES = (
    # Logical data length 564 0x234
    b'\xf8\tPARAMETER\x031340\x06VAL'  # Chunk from 0
    b'UES0\x04AXIS0\tDIMENSION'  # Chunk from 20
    b'0\tLONG-NAMEp)\x00\x07LOGMO'  # Chunk from 40
    b'DE%\x13\x0eMEASURED_DEPTH\x00'  # Chunk from 60
    b'\x00%\x14\x12Depth Logging Mo'  # Chunk from 80
    b'dep)\x00\x07PBVSADP%\x13\x02NO\x00\x00'  # Chunk from 100
    b'%\x14(Use alternate dep'  # Chunk from 120
    b'th channel for playb'  # Chunk from 140
    b"ackp)\x00\x02DO'\x02\x01m\x00\x00\x00\x00\x00\x00%"  # Chunk from 160
    b'\x14\x19Depth Offset for P'  # Chunk from 180
    b'laybackp)\x00\x02PP%\x13\x06NORM'  # Chunk from 200
    b'AL\x00\x00%\x14\x13Playback Proc'  # Chunk from 220
    b"essingp)\x00\x04SPEE'\x0e\x04ft/"  # Chunk from 240
    b'h\x00\x00\x07\x08\x00\x00%\x14\x17Simulated '  # Chunk from 260
    b'Logging Speedp)\x00\x03LCL'  # Chunk from 280
    b"'\x0e\x01m\x00\x00\x12\xc0\x00\x00%\x14\x14Logging"  # Chunk from 300
    b' Cable Lengthp)\x00\x03LCN'  # Chunk from 320
    b'%\x13\x00\x00\x00%\x14\x19Logging Cabl'  # Chunk from 340
    b'e Name (Type)p)\x00\x0eSIM'  # Chunk from 360
    b'ULATE_DELAY%\x02\xc7\xc3O\x80\x00\x00%'  # Chunk from 380
    b'\x14\x1aSimulate Acquisiti'  # Chunk from 400
    b'on Delayp)\x00\x04ENVI%\x13\x06A'  # Chunk from 420
    b'NALOG\x00\x00%\x14\x17Acquisitio'  # Chunk from 440
    b'n Environmentp)\x00\x04VHO'  # Chunk from 460
    b"L'\x02\x02m3?\xc9a\xce\x00\x00%\x14\x15Cumul"  # Chunk from 480
    b'ated Hole Volumep)\x00\x04'  # Chunk from 500
    b"VCEM'\x02\x02m3?\x01\x9c*\x00\x00%\x14\x17Cu"  # Chunk from 520
    b'mulated Cement Volum'  # Chunk from 540
    b'e  \x03'  # Chunk from 560
)


def test_ExplicitlyFormattedLogicalRecord_eq():
    ld = LogicalData(LOGICAL_BYTES_FROM_STANDARD)
    eflr_a = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
    ld.rewind()
    eflr_b = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
    assert eflr_a == eflr_b
    assert eflr_a != 1


def test_ExplicitlyFormattedLogicalRecord_len():
    ld = LogicalData(LOGICAL_BYTES_FROM_STANDARD)
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
    result = eflr.str_long()
    # print(result)
    assert len(eflr) == 3

@pytest.mark.parametrize(
    'sort_order, expected',
    (
        (
            False,
            [
                ['ObjectName IDENT', 'O', 'C', 'LONG-NAME', 'ELEMENT-LIMIT', 'REPRESENTATION-CODE', 'UNITS', 'DIMENSION'],
                ['TIME', '0', '0', '1 (O: 0 C: 0)', '1', '2', 'S', '1'],
                ['PRESSURE', '1', '0', '2 (O: 0 C: 0)', '1', '7', 'PSI', '1'],
                ['PAD-ARRAY', '1', '0', '3 (O: 0 C: 0)', '[8, 20]', '13', '-', '[8, 10]'],
            ],
        ),
        (
            True,
            [
                ['ObjectName IDENT', 'O', 'C', 'LONG-NAME', 'ELEMENT-LIMIT', 'REPRESENTATION-CODE', 'UNITS', 'DIMENSION'],
                ['PAD-ARRAY', '1', '0', '3 (O: 0 C: 0)', '[8, 20]', '13', '-', '[8, 10]'],
                ['PRESSURE', '1', '0', '2 (O: 0 C: 0)', '1', '7', 'PSI', '1'],
                ['TIME', '0', '0', '1 (O: 0 C: 0)', '1', '2', 'S', '1'],
            ],
        ),
    )
)
def test_ExplicitlyFormattedLogicalRecord_table_as_string(sort_order, expected):
    ld = LogicalData(LOGICAL_BYTES_FROM_STANDARD)
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
    result = eflr.table_as_strings(stringify_function=stringify.stringify_object_by_type, sort=sort_order)
    # print(result)
    assert result == expected


def test_ExplicitlyFormattedLogicalRecord_table_shape():
    ld = LogicalData(LOGICAL_BYTES_FROM_STANDARD)
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
    assert eflr.shape == (3, 5)


def test_ExplicitlyFormattedLogicalRecord_reduced_object_map():
    ld = LogicalData(LOGICAL_BYTES_FROM_STANDARD)
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
    result = EFLR.reduced_object_map(eflr)
    # print(result)
    assert result == {b'TIME': 0, b'PRESSURE': 1, b'PAD-ARRAY': 2}


def test_ExplicitlyFormattedLogicalRecord_key_value():
    ld = LogicalData(LOGICAL_BYTES_FROM_STANDARD_SINGLE_OBJECT)
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
    assert eflr.is_key_value()


def test_ExplicitlyFormattedLogicalRecord_key_value_raises():
    ld = LogicalData(LOGICAL_BYTES_FROM_STANDARD)
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
    assert not eflr.is_key_value()
    with pytest.raises(EFLR.ExceptionEFLR) as err:
        eflr.key_values(stringify_function=stringify.stringify_object_by_type, sort=True)
    assert err.value.args[0] == 'Can not represent EFLR as key->value table.'


@pytest.mark.parametrize(
    'sort_order, expected',
    (
        (
            True,
            [['KEY', 'VALUE'], ['DIMENSION', '1'], ['ELEMENT-LIMIT', '1'], ['LONG-NAME', '1 (O: 0 C: 0)'],
             ['REPRESENTATION-CODE', '2'], ['UNITS', 'S']],
        ),
        (
            False,
            [['KEY', 'VALUE'], ['LONG-NAME', '1 (O: 0 C: 0)'], ['ELEMENT-LIMIT', '1'], ['REPRESENTATION-CODE', '2'],
             ['UNITS', 'S'], ['DIMENSION', '1']],
        ),
    )
)
def test_ExplicitlyFormattedLogicalRecord_key_values(sort_order, expected):
    ld = LogicalData(LOGICAL_BYTES_FROM_STANDARD_SINGLE_OBJECT)
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(3, ld)
    result = eflr.key_values(stringify_function=stringify.stringify_object_by_type, sort=sort_order)
    # print(result)
    assert result == expected
