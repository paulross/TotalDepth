

import pytest

from TotalDepth.RP66V1.core.File import LogicalData
from TotalDepth.RP66V1.core.LogicalRecord import EFLR
from TotalDepth.RP66V1.core.LogicalRecord.ComponentDescriptor import ComponentDescriptor
from TotalDepth.RP66V1.core import RepCode


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

@pytest.mark.parametrize(
    'ld, expected_template',
    (
        (
            # Example from [RP66V1 Section 3.2.3.2 Figure 3-8]
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
            EFLR.Template(
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
                )
            ),
        ),
    )
)
def test_Template(ld, expected_template):
    template = EFLR.Template(ld)
    assert template == expected_template
    assert ld.remain == 1  # Object byte terminates template

@pytest.mark.parametrize(
    'ld, template, expected_object',
    (
        (
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
            EFLR.Template(
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
                )
            ),
            EFLR.Object(
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
                EFLR.Template(
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
                    )
                ),
            ),
        ),
    )
)
def test_Object(ld, template, expected_object):
    obj = EFLR.Object(ld, template)
    assert obj == expected_object
    assert ld.remain == 1  # Object byte terminates template


# Example from [RP66V1 Section 3.2.3.2 Figure 3-8]
LOGICAL_DATA_FROM_STANDARD = LogicalData(
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


@pytest.mark.parametrize(
    'ld',
    (
        LOGICAL_DATA_FROM_STANDARD,
    )
)
def test_ExplicitlyFormattedLogicalRecord_smoke_test(ld):
    ld.rewind()
    EFLR.ExplicitlyFormattedLogicalRecord(ld)


@pytest.mark.parametrize(
    'ld',
    (
        LOGICAL_DATA_FROM_STANDARD,
    )
)
def test_ExplicitlyFormattedLogicalRecord_set(ld):
    ld.rewind()
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(ld)
    assert eflr.set.type == b'CHANNEL'
    assert eflr.set.name == b'0'


@pytest.mark.parametrize(
    'ld',
    (
        LOGICAL_DATA_FROM_STANDARD,
    )
)
def test_ExplicitlyFormattedLogicalRecord_template(ld):
    ld.rewind()
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(ld)
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
        LOGICAL_DATA_FROM_STANDARD,
    )
)
def test_ExplicitlyFormattedLogicalRecord_objects(ld):
    ld.rewind()
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(ld)
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
        LOGICAL_DATA_FROM_STANDARD,
    )
)
def test_ExplicitlyFormattedLogicalRecord_str(ld):
    ld.rewind()
    eflr = EFLR.ExplicitlyFormattedLogicalRecord(ld)
    # print(eflr)
    assert str(eflr) == """EFLR Set type: b'CHANNEL' name: b'0'
Template:
  CD: 001 10100 L: b'LONG-NAME' C: 1 R: 23 U: b'' V: None
  CD: 001 10101 L: b'ELEMENT-LIMIT' C: 1 R: 18 U: b'' V: [1]
  CD: 001 10101 L: b'REPRESENTATION-CODE' C: 1 R: 15 U: b'' V: [2]
  CD: 001 10000 L: b'UNITS' C: 1 R: 19 U: b'' V: None
  CD: 001 10101 L: b'DIMENSION' C: 1 R: 18 U: b'' V: [1]
Objects:
  OBNAME: O: 0 C: 0 I: b'TIME' 
    CD: 001 00001 L: b'LONG-NAME' C: 1 R: 23 U: b'' V: [ObjectName(O=0, C=0, I=b'1')]
    CD: 001 00000 L: b'ELEMENT-LIMIT' C: 1 R: 18 U: b'' V: [1]
    CD: 001 00000 L: b'REPRESENTATION-CODE' C: 1 R: 15 U: b'' V: [2]
    CD: 001 00001 L: b'UNITS' C: 1 R: 19 U: b'' V: [b'S']
    CD: 001 10101 L: b'DIMENSION' C: 1 R: 18 U: b'' V: [1]
  OBNAME: O: 1 C: 0 I: b'PRESSURE' 
    CD: 001 00001 L: b'LONG-NAME' C: 1 R: 23 U: b'' V: [ObjectName(O=0, C=0, I=b'2')]
    CD: 001 00000 L: b'ELEMENT-LIMIT' C: 1 R: 18 U: b'' V: [1]
    CD: 001 00001 L: b'REPRESENTATION-CODE' C: 1 R: 15 U: b'' V: [7]
    CD: 001 00001 L: b'UNITS' C: 1 R: 19 U: b'' V: [b'PSI']
    CD: 001 10101 L: b'DIMENSION' C: 1 R: 18 U: b'' V: [1]
  OBNAME: O: 1 C: 0 I: b'PAD-ARRAY' 
    CD: 001 00001 L: b'LONG-NAME' C: 1 R: 23 U: b'' V: [ObjectName(O=0, C=0, I=b'3')]
    CD: 001 01001 L: b'ELEMENT-LIMIT' C: 2 R: 18 U: b'' V: [8, 20]
    CD: 001 00001 L: b'REPRESENTATION-CODE' C: 1 R: 15 U: b'' V: [13]
    CD: 000 00000 L: b'UNITS' C: 1 R: 19 U: b'' V: None
    CD: 001 01001 L: b'DIMENSION' C: 2 R: 18 U: b'' V: [8, 10]"""

# EXPECTED_OBJECTS = [
#     # Attributes have LCRUV
#     [b'LONG-NAME', 1, RepCode.REP_CODE_STR_TO_INT['OBNAME'], b'', [RepCode.ObjectName(0, 0, b'1')]],
# ]
