import pytest

from TotalDepth.RP66V1.core.LogicalRecord import ComponentDescriptor


@pytest.mark.parametrize(
    'value, message',
    (
        (-1, 'Descriptor 0x-1 out of range.'),
        (256, 'Descriptor 0x100 out of range.'),
        (0xe1, 'Reserved bits are set for SET type 0xe1'),
        (0xe2, 'Reserved bits are set for SET type 0xe2'),
        (0xe4, 'Reserved bits are set for SET type 0xe4'),
        (0x68, 'Reserved bits are set for OBJECT type 0x68'),
        (0x64, 'Reserved bits are set for OBJECT type 0x64'),
        (0x62, 'Reserved bits are set for OBJECT type 0x62'),
        (0x61, 'Reserved bits are set for OBJECT type 0x61'),
        (0xe0, 'SET type must have \'Type\' Characteristic from 0xe0'),
        (0x60, 'OBJECT type must have \'Name\' Characteristic from 0x60'),
    )
)
def test_ctor_raises(value, message):
    with pytest.raises(ComponentDescriptor.ExceptionComponentDescriptorInit) as err:
        ComponentDescriptor.ComponentDescriptor(value)
    assert err.value.args[0] == message


@pytest.mark.parametrize(
    'descriptor, result',
    (
        (0x00, 'ABSATR'),
        (0x20, 'ATTRIB'),
        (0x40, 'INVATR'),
        (0x70, 'OBJECT'),
        # (0x80, False), reserved
        (0xb0, 'RDSET'),
        (0xd0, 'RSET'),
        (0xf0, 'SET'),
    )
)
def test_role(descriptor, result):
    cd = ComponentDescriptor.ComponentDescriptor(descriptor)
    assert cd.role == result


def test_component_descriptor_eq():
    cd = ComponentDescriptor.ComponentDescriptor(0x00)
    assert cd == cd
    assert cd != 1


@pytest.mark.parametrize(
    'descriptor, result',
    (
        (0x00, 'Absent Attribute'),
        (0x20, 'Attribute'),
        (0x40, 'Invariant Attribute'),
        (0x70, 'Object'),
        # (0x80, False), reserved
        (0xb0, 'Redundant Set'),
        (0xd0, 'Replacement Set'),
        (0xf0, 'Set'),
    )
)
def test_type(descriptor, result):
    cd = ComponentDescriptor.ComponentDescriptor(descriptor)
    assert cd.type == result


@pytest.mark.parametrize(
    'descriptor, result',
    (
        (0x00, True),  # ABSATR
        (0x20, True),  # ATTRIB
        (0x40, True),  # INVATR
        (0x70, False),  # OBJECT
        # (0x80, False), reserved
        (0xb0, False),  # RDSET
        (0xd0, False),  # RSET
        (0xf0, False),  # SET
    )
)
def test_is_attribute_group(descriptor, result):
    cd = ComponentDescriptor.ComponentDescriptor(descriptor)
    assert cd.is_attribute_group == result


@pytest.mark.parametrize(
    'descriptor, result',
    (
        (0x00, False),  # ABSATR
        (0x20, True),  # ATTRIB
        (0x40, False),  # INVATR
        (0x70, False),  # OBJECT
        # (0x80, False), reserved
        (0xb0, False),  # RDSET
        (0xd0, False),  # RSET
        (0xf0, False),  # SET
    )
)
def test_is_attribute(descriptor, result):
    cd = ComponentDescriptor.ComponentDescriptor(descriptor)
    assert cd.is_attribute == result


@pytest.mark.parametrize(
    'descriptor, result',
    (
        (0x00, True),  # ABSATR
        (0x20, False),  # ATTRIB
        (0x40, False),  # INVATR
        (0x70, False),  # OBJECT
        # (0x80, False), reserved
        (0xb0, False),  # RDSET
        (0xd0, False),  # RSET
        (0xf0, False),  # SET
    )
)
def test_is_absent_attribute(descriptor, result):
    cd = ComponentDescriptor.ComponentDescriptor(descriptor)
    assert cd.is_absent_attribute == result


@pytest.mark.parametrize(
    'descriptor, result',
    (
        (0x00, False),  # ABSATR
        (0x20, False),  # ATTRIB
        (0x40, True),  # INVATR
        (0x70, False),  # OBJECT
        # (0x80, False), reserved
        (0xb0, False),  # RDSET
        (0xd0, False),  # RSET
        (0xf0, False),  # SET
    )
)
def test_is_invariant_attribute(descriptor, result):
    cd = ComponentDescriptor.ComponentDescriptor(descriptor)
    assert cd.is_invariant_attribute == result


@pytest.mark.parametrize(
    'descriptor, result',
    (
        (0x00, False),  # ABSATR
        (0x20, False),  # ATTRIB
        (0x40, False),  # INVATR
        (0x70, True),  # OBJECT
        # (0x80, False), reserved
        (0xb0, False),  # RDSET
        (0xd0, False),  # RSET
        (0xf0, False),  # SET
    )
)
def test_is_object(descriptor, result):
    cd = ComponentDescriptor.ComponentDescriptor(descriptor)
    assert cd.is_object == result


@pytest.mark.parametrize(
    'descriptor, result',
    (
        (0x00, False),  # ABSATR
        (0x20, False),  # ATTRIB
        (0x40, False),  # INVATR
        (0x70, False),  # OBJECT
        # (0x80, False), reserved
        (0xb0, True),  # RDSET
        (0xd0, True),  # RSET
        (0xf0, True),  # SET
    )
)
def test_is_set_group(descriptor, result):
    cd = ComponentDescriptor.ComponentDescriptor(descriptor)
    assert cd.is_set_group == result


@pytest.mark.parametrize(
    'descriptor, result',
    (
        (0x00, False),  # ABSATR
        (0x20, False),  # ATTRIB
        (0x40, False),  # INVATR
        (0x70, False),  # OBJECT
        # (0x80, False), reserved
        (0xb0, True),  # RDSET
        (0xd0, False),  # RSET
        (0xf0, False),  # SET
    )
)
def test_is_rdset(descriptor, result):
    cd = ComponentDescriptor.ComponentDescriptor(descriptor)
    assert cd.is_redundant_set == result


@pytest.mark.parametrize(
    'descriptor, result',
    (
        (0x00, False),  # ABSATR
        (0x20, False),  # ATTRIB
        (0x40, False),  # INVATR
        (0x70, False),  # OBJECT
        # (0x80, False), reserved
        (0xb0, False),  # RDSET
        (0xd0, True),  # RSET
        (0xf0, False),  # SET
    )
)
def test_is_rset(descriptor, result):
    cd = ComponentDescriptor.ComponentDescriptor(descriptor)
    assert cd.is_replacement_set == result


@pytest.mark.parametrize(
    'descriptor, result',
    (
        (0x00, False),  # ABSATR
        (0x20, False),  # ATTRIB
        (0x40, False),  # INVATR
        (0x70, False),  # OBJECT
        # (0x80, False), reserved
        (0xb0, False),  # RDSET
        (0xd0, False),  # RSET
        (0xf0, True),  # SET
    )
)
def test_is_set(descriptor, result):
    cd = ComponentDescriptor.ComponentDescriptor(descriptor)
    assert cd.is_set == result


@pytest.mark.parametrize(
    'value, result',
    (
        (0xf0, 0x10),
        (0xf8, 0x10),
        # TODO: Other set types
    )
)
def test_has_set_T(value, result):
    cd = ComponentDescriptor.ComponentDescriptor(value)
    assert cd.has_set_T == result


@pytest.mark.parametrize(
    'value, message',
    (
        (0x00, 'Accessing SET property T when not a SET type.'),  # ABSATR
        (0x20, 'Accessing SET property T when not a SET type.'),  # ATTRIB
        (0x40, 'Accessing SET property T when not a SET type.'),  # INVATR
        (0x70, 'Accessing SET property T when not a SET type.'),  # OBJECT
        # (0x80, False), reserved
        # (0xb0, False),  # RDSET
        # (0xd0, False),  # RSET
        # (0xf0, True),  # SET
    )
)
def test_has_set_T_raises(value, message):
    cd = ComponentDescriptor.ComponentDescriptor(value)
    with pytest.raises(ComponentDescriptor.ExceptionComponentDescriptorAccessError) as err:
        cd.has_set_T
    assert err.value.args[0] == message


@pytest.mark.parametrize(
    'value, result',
    (
        (0xf0, 0x00),
        (0xf8, 0x08),
        # TODO: Other set types
    )
)
def test_has_set_N(value, result):
    cd = ComponentDescriptor.ComponentDescriptor(value)
    assert cd.has_set_N == result


@pytest.mark.parametrize(
    'value, message',
    (
        (0x00, 'Accessing SET property N when not a SET type.'),  # ABSATR
        (0x20, 'Accessing SET property N when not a SET type.'),  # ATTRIB
        (0x40, 'Accessing SET property N when not a SET type.'),  # INVATR
        (0x70, 'Accessing SET property N when not a SET type.'),  # OBJECT
        # (0x80, False), reserved
        # (0xb0, False),  # RDSET
        # (0xd0, False),  # RSET
        # (0xf0, True),  # SET
    )
)
def test_has_set_N_raises(value, message):
    cd = ComponentDescriptor.ComponentDescriptor(value)
    with pytest.raises(ComponentDescriptor.ExceptionComponentDescriptorAccessError) as err:
        cd.has_set_N
    assert err.value.args[0] == message


@pytest.mark.parametrize(
    'value, result',
    (
        (0x70, 0x10),
    )
)
def test_has_object_N(value, result):
    cd = ComponentDescriptor.ComponentDescriptor(value)
    assert cd.has_object_N == result


@pytest.mark.parametrize(
    'value, message',
    (
        (0x00, 'Accessing OBJECT property N when not a OBJECT type.'),  # ABSATR
        (0x20, 'Accessing OBJECT property N when not a OBJECT type.'),  # ATTRIB
        (0x40, 'Accessing OBJECT property N when not a OBJECT type.'),  # INVATR
        # (0x70, 'Accessing OBJECT property N when not a OBJECT type.'),  # OBJECT
        # (0x80, False), reserved
        (0xb0, 'Accessing OBJECT property N when not a OBJECT type.'),  # RDSET
        (0xd0, 'Accessing OBJECT property N when not a OBJECT type.'),  # RSET
        (0xf0, 'Accessing OBJECT property N when not a OBJECT type.'),  # SET
    )
)
def test_has_object_N_raises(value, message):
    cd = ComponentDescriptor.ComponentDescriptor(value)
    with pytest.raises(ComponentDescriptor.ExceptionComponentDescriptorAccessError) as err:
        cd.has_object_N
    assert err.value.args[0] == message


# ATTRIBUTES = (0x00, 0x20, 0x40)
# # [[v | b for v in ATTRIBUTES] for b in range(16)]
# [a | b for a,b in itertools.product(range(16), ATTRIBUTES)]

@pytest.mark.parametrize(
    'value, result',
    (
        (0x00, 0x00),
        (0x20, 0x00),
        (0x40, 0x00),
        (0x10, 0x10),
        (0x30, 0x10),
        (0x50, 0x10),
    )
)
def test_has_attribute_L(value, result):
    cd = ComponentDescriptor.ComponentDescriptor(value)
    assert cd.has_attribute_L == result


@pytest.mark.parametrize(
    'value, result',
    (
        (0x00, 0x00),
        (0x20, 0x00),
        (0x40, 0x00),
        (0x08, 0x08),
        (0x28, 0x08),
        (0x48, 0x08),
    )
)
def test_has_attribute_C(value, result):
    cd = ComponentDescriptor.ComponentDescriptor(value)
    assert cd.has_attribute_C == result


@pytest.mark.parametrize(
    'value, result',
    (
        (0x00, 0x00),
        (0x20, 0x00),
        (0x40, 0x00),
        (0x04, 0x04),
        (0x24, 0x04),
        (0x44, 0x04),
    )
)
def test_has_attribute_R(value, result):
    cd = ComponentDescriptor.ComponentDescriptor(value)
    assert cd.has_attribute_R == result


@pytest.mark.parametrize(
    'value, result',
    (
        (0x00, 0x00),
        (0x20, 0x00),
        (0x40, 0x00),
        (0x02, 0x02),
        (0x22, 0x02),
        (0x42, 0x02),
    )
)
def test_has_attribute_U(value, result):
    cd = ComponentDescriptor.ComponentDescriptor(value)
    assert cd.has_attribute_U == result


@pytest.mark.parametrize(
    'value, result',
    (
        (0x00, 0x00),
        (0x20, 0x00),
        (0x40, 0x00),
        (0x01, 0x01),
        (0x21, 0x01),
        (0x41, 0x01),
    )
)
def test_has_attribute_V(value, result):
    cd = ComponentDescriptor.ComponentDescriptor(value)
    assert cd.has_attribute_V == result


@pytest.mark.parametrize(
    'value, message',
    (
        # (0x00, 'Accessing ATTRIBUTE property L when not a ATTRIBUTE type.'),  # ABSATR
        # (0x20, 'Accessing ATTRIBUTE property L when not a ATTRIBUTE type.'),  # ATTRIB
        # (0x40, 'Accessing ATTRIBUTE property L when not a ATTRIBUTE type.'),  # INVATR
        (0x70, 'Accessing ATTRIBUTE property L when not a ATTRIBUTE type.'),  # OBJECT
        # (0x80, False), reserved
        (0xb0, 'Accessing ATTRIBUTE property L when not a ATTRIBUTE type.'),  # RDSET
        (0xd0, 'Accessing ATTRIBUTE property L when not a ATTRIBUTE type.'),  # RSET
        (0xf0, 'Accessing ATTRIBUTE property L when not a ATTRIBUTE type.'),  # SET
    )
)
def test_has_attribute_L_raises(value, message):
    cd = ComponentDescriptor.ComponentDescriptor(value)
    with pytest.raises(ComponentDescriptor.ExceptionComponentDescriptorAccessError) as err:
        cd.has_attribute_L
    assert err.value.args[0] == message


@pytest.mark.parametrize(
    'value, message',
    (
        # (0x00, 'Accessing ATTRIBUTE property C when not a ATTRIBUTE type.'),  # ABSATR
        # (0x20, 'Accessing ATTRIBUTE property C when not a ATTRIBUTE type.'),  # ATTRIB
        # (0x40, 'Accessing ATTRIBUTE property C when not a ATTRIBUTE type.'),  # INVATR
        (0x70, 'Accessing ATTRIBUTE property C when not a ATTRIBUTE type.'),  # OBJECT
        # (0x80, False), reserved
        (0xb0, 'Accessing ATTRIBUTE property C when not a ATTRIBUTE type.'),  # RDSET
        (0xd0, 'Accessing ATTRIBUTE property C when not a ATTRIBUTE type.'),  # RSET
        (0xf0, 'Accessing ATTRIBUTE property C when not a ATTRIBUTE type.'),  # SET
    )
)
def test_has_attribute_C_raises(value, message):
    cd = ComponentDescriptor.ComponentDescriptor(value)
    with pytest.raises(ComponentDescriptor.ExceptionComponentDescriptorAccessError) as err:
        cd.has_attribute_C
    assert err.value.args[0] == message


@pytest.mark.parametrize(
    'value, message',
    (
        # (0x00, 'Accessing ATTRIBUTE property R when not a ATTRIBUTE type.'),  # ABSATR
        # (0x20, 'Accessing ATTRIBUTE property R when not a ATTRIBUTE type.'),  # ATTRIB
        # (0x40, 'Accessing ATTRIBUTE property R when not a ATTRIBUTE type.'),  # INVATR
        (0x70, 'Accessing ATTRIBUTE property R when not a ATTRIBUTE type.'),  # OBJERT
        # (0x80, False), reserved
        (0xb0, 'Accessing ATTRIBUTE property R when not a ATTRIBUTE type.'),  # RDSET
        (0xd0, 'Accessing ATTRIBUTE property R when not a ATTRIBUTE type.'),  # RSET
        (0xf0, 'Accessing ATTRIBUTE property R when not a ATTRIBUTE type.'),  # SET
    )
)
def test_has_attribute_R_raises(value, message):
    cd = ComponentDescriptor.ComponentDescriptor(value)
    with pytest.raises(ComponentDescriptor.ExceptionComponentDescriptorAccessError) as err:
        cd.has_attribute_R
    assert err.value.args[0] == message


@pytest.mark.parametrize(
    'value, message',
    (
        # (0x00, 'Accessing ATTRIBUTE property U when not a ATTRIBUTE type.'),  # ABSATR
        # (0x20, 'Accessing ATTRIBUTE property U when not a ATTRIBUTE type.'),  # ATTRIB
        # (0x40, 'Accessing ATTRIBUTE property U when not a ATTRIBUTE type.'),  # INVATR
        (0x70, 'Accessing ATTRIBUTE property U when not a ATTRIBUTE type.'),  # OBJERT
        # (0x80, False), reserved
        (0xb0, 'Accessing ATTRIBUTE property U when not a ATTRIBUTE type.'),  # RDSET
        (0xd0, 'Accessing ATTRIBUTE property U when not a ATTRIBUTE type.'),  # RSET
        (0xf0, 'Accessing ATTRIBUTE property U when not a ATTRIBUTE type.'),  # SET
    )
)
def test_has_attribute_U_raises(value, message):
    cd = ComponentDescriptor.ComponentDescriptor(value)
    with pytest.raises(ComponentDescriptor.ExceptionComponentDescriptorAccessError) as err:
        cd.has_attribute_U
    assert err.value.args[0] == message


@pytest.mark.parametrize(
    'value, message',
    (
        # (0x00, 'Accessing ATTRIBUTE property V when not a ATTRIBUTE type.'),  # ABSATR
        # (0x20, 'Accessing ATTRIBUTE property V when not a ATTRIBUTE type.'),  # ATTRIB
        # (0x40, 'Accessing ATTRIBUTE property V when not a ATTRIBUTE type.'),  # INVATR
        (0x70, 'Accessing ATTRIBUTE property V when not a ATTRIBUTE type.'),  # OBJERT
        # (0x80, False), reserved
        (0xb0, 'Accessing ATTRIBUTE property V when not a ATTRIBUTE type.'),  # RDSET
        (0xd0, 'Accessing ATTRIBUTE property V when not a ATTRIBUTE type.'),  # RSET
        (0xf0, 'Accessing ATTRIBUTE property V when not a ATTRIBUTE type.'),  # SET
    )
)
def test_has_attribute_V_raises(value, message):
    cd = ComponentDescriptor.ComponentDescriptor(value)
    with pytest.raises(ComponentDescriptor.ExceptionComponentDescriptorAccessError) as err:
        cd.has_attribute_V
    assert err.value.args[0] == message

# TODO: Check ROLE_MAP

# TODO: Check CHARACTERISTICS_AND_COMPONENT_FORMAT_SET_MAP and for OBJECT and ATTRIB
