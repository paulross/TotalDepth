"""
Implements the Component Descriptor [RP66V1 Section 3.2.2.1 Component Descriptor]

References:
RP66V1: http://w3.energistics.org/rp66/v1/rp66v1.html
Specifically section 3: http://w3.energistics.org/rp66/v1/rp66v1_sec3.html

"""
import collections

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core.File import LogicalData


class ExceptionComponentDescriptor(ExceptionTotalDepthRP66V1):
    pass


class ExceptionComponentDescriptorInit(ExceptionComponentDescriptor):
    pass


class ExceptionComponentDescriptorAccessError(ExceptionComponentDescriptor):
    pass


RoleType = collections.namedtuple('RoleType', 'role, type')
CharacteristicRepCodeGlobalDefault = collections.namedtuple(
    'CharacteristicRepCodeGlobalDefault', 'characteristic, rep_code, global_default'
)


class ComponentDescriptor:
    ROLE_MASK = 0xe0
    ROLE_ABSATR = 0x00
    ROLE_ATTRIB = 0x20
    ROLE_INVATR = 0x40
    ROLE_OBJECT = 0x60
    ROLE_reserved = 0x80
    ROLE_RDSET = 0xa0
    ROLE_RSET = 0xc0
    ROLE_SET = 0xe0
    ROLE_MAP = {
        ROLE_ABSATR : RoleType('ABSATR', 'Absent Attribute'),
        ROLE_ATTRIB : RoleType('ATTRIB', 'Attribute'),
        ROLE_INVATR : RoleType('INVATR', 'Invariant Attribute'),
        ROLE_OBJECT : RoleType('OBJECT', 'Object'),
        ROLE_reserved : RoleType('reserved', ''),
        ROLE_RDSET : RoleType('RDSET', 'Redundant Set'),
        ROLE_RSET : RoleType('RSET', 'Replacement Set'),
        ROLE_SET : RoleType('SET', 'Set'),
    }
    CHARACTERISTICS_AND_COMPONENT_FORMAT_MASK = 0x1f
    # Bits symbols for Sets [RP66V1 Section 3.2.2.1 Figure 3-3]
    CHARACTERISTICS_AND_COMPONENT_FORMAT_SET_T = 0x10
    CHARACTERISTICS_AND_COMPONENT_FORMAT_SET_N = 0x08
    CHARACTERISTICS_AND_COMPONENT_FORMAT_SET_reserved = 0x07
    CHARACTERISTICS_AND_COMPONENT_FORMAT_SET_MAP = {
        'T': CharacteristicRepCodeGlobalDefault('Type', 'IDENT', None),
        'N': CharacteristicRepCodeGlobalDefault('Name', 'IDENT', b''),
    }
    # Bits symbols for Objects [RP66V1 Section 3.2.2.1 Figure 3-4]
    CHARACTERISTICS_AND_COMPONENT_FORMAT_OBJECT_N = 0x10
    CHARACTERISTICS_AND_COMPONENT_FORMAT_OBJECT_reserved = 0x0F
    CHARACTERISTICS_AND_COMPONENT_FORMAT_OBJECT_MAP = {
        'N': CharacteristicRepCodeGlobalDefault('Name', 'OBNAME', None),
    }
    # Bits symbols for Attributes [RP66V1 Section 3.2.2.1 Figure 3-5]
    CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_L = 0x10
    CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_C = 0x08
    CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_R = 0x04
    CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_U = 0x02
    CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_V = 0x01
    CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_MAP = {
        'L': CharacteristicRepCodeGlobalDefault('Label', 'IDENT', b''),
        'C': CharacteristicRepCodeGlobalDefault('Count', 'UVARI', 1),
        'R': CharacteristicRepCodeGlobalDefault('Representation Code', 'USHORT', 19), # IDENT
        'U': CharacteristicRepCodeGlobalDefault('Units', 'UNITS', b''),
        'V': CharacteristicRepCodeGlobalDefault('Value', None, None),
    }

    def __init__(self, descriptor: int):
        if not 0 <= descriptor < 0x100:
            raise ExceptionComponentDescriptorInit(f'Descriptor 0x{descriptor:x} out of range.')
        self._desc = descriptor
        # Check reserved bits are 0 [RP66V1 Section 3.2.2 Component Structure note 5.]
        if self.is_set_group and self._desc & self.CHARACTERISTICS_AND_COMPONENT_FORMAT_SET_reserved:
            raise ExceptionComponentDescriptorInit(f'Reserved bits are set for SET type 0x{self._desc:x}')
        if self.is_object and self._desc & self.CHARACTERISTICS_AND_COMPONENT_FORMAT_OBJECT_reserved:
            raise ExceptionComponentDescriptorInit(f'Reserved bits are set for OBJECT type 0x{self._desc:x}')
        # Check required set bits
        if self.is_set_group and not self.has_set_T:
            # [RP66V1 Section 3.2.2.1 Component Descriptor, comment 1 following Figure 3-3.]
            raise ExceptionComponentDescriptorInit(f'SET type must have \'Type\' Characteristic from 0x{self._desc:x}')
        if self.is_object and not self.has_object_N:
            # [RP66V1 Section 3.2.2.1 Component Descriptor, comment 1 following Figure 3-4.]
            raise ExceptionComponentDescriptorInit(f'OBJECT type must have \'Name\' Characteristic from 0x{self._desc:x}')

    def __eq__(self, other):
        if other.__class__ == ComponentDescriptor:
            return self._desc == other._desc
        return NotImplemented

    @property
    def _bits_1_3(self) -> int:
        """Returns the bits 1-3 as the upper three bits in the range 0x00 to 0xe0 in steps of 0x20.
        [RP66V1 Figure 3-2]"""
        return self._desc & self.ROLE_MASK

    @property
    def _bits_4_8(self) -> int:
        """Returns the bits 4-8 as the lower five bits in the range 0x00 to 0x1f.
        [RP66V1 Figures 3-3, 3-4, 3-5]"""
        return self._desc & self.CHARACTERISTICS_AND_COMPONENT_FORMAT_MASK

    @property
    def role(self) -> str:
        return self.ROLE_MAP[self._bits_1_3].role

    @property
    def type(self) -> str:
        return self.ROLE_MAP[self._bits_1_3].type

    #
    # ------------- Roles --------------
    @property
    def is_attribute_group(self) -> bool:
        return self._bits_1_3 < self.ROLE_OBJECT

    @property
    def is_set_group(self) -> bool:
        return self._bits_1_3 > self.ROLE_reserved

    # Specific roles
    @property
    def is_absent_attribute(self) -> bool:
        return self._bits_1_3 == self.ROLE_ABSATR

    @property
    def is_attribute(self) -> bool:
        return self._bits_1_3 == self.ROLE_ATTRIB

    @property
    def is_invariant_attribute(self) -> bool:
        return self._bits_1_3 == self.ROLE_INVATR

    @property
    def is_object(self) -> bool:
        return self._bits_1_3 == self.ROLE_OBJECT

    @property
    def is_redundant_set(self) -> bool:
        return self._bits_1_3 == self.ROLE_RDSET

    @property
    def is_replacement_set(self) -> bool:
        return self._bits_1_3 == self.ROLE_RSET

    @property
    def is_set(self) -> bool:
        return self._bits_1_3 == self.ROLE_SET

    #
    # ------------- END: Roles --------------

    #
    # ------------- Characteristics and Component Format --------------
    @property
    def has_set_T(self) -> int:
        if not self.is_set_group:
            raise ExceptionComponentDescriptorAccessError('Accessing SET property T when not a SET type.')
        return self._bits_4_8 & self.CHARACTERISTICS_AND_COMPONENT_FORMAT_SET_T

    @property
    def has_set_N(self) -> int:
        if not self.is_set_group:
            raise ExceptionComponentDescriptorAccessError('Accessing SET property N when not a SET type.')
        return self._bits_4_8 & self.CHARACTERISTICS_AND_COMPONENT_FORMAT_SET_N

    @property
    def has_object_N(self) -> int:
        if not self.is_object:
            raise ExceptionComponentDescriptorAccessError('Accessing OBJECT property N when not a OBJECT type.')
        return self._bits_4_8 & self.CHARACTERISTICS_AND_COMPONENT_FORMAT_OBJECT_N

    @property
    def has_attribute_L(self) -> int:
        if not self.is_attribute_group:
            raise ExceptionComponentDescriptorAccessError('Accessing ATTRIBUTE property L when not a ATTRIBUTE type.')
        return self._bits_4_8 & self.CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_L

    @property
    def has_attribute_C(self) -> int:
        if not self.is_attribute_group:
            raise ExceptionComponentDescriptorAccessError('Accessing ATTRIBUTE property C when not a ATTRIBUTE type.')
        return self._bits_4_8 & self.CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_C

    @property
    def has_attribute_R(self) -> int:
        if not self.is_attribute_group:
            raise ExceptionComponentDescriptorAccessError('Accessing ATTRIBUTE property R when not a ATTRIBUTE type.')
        return self._bits_4_8 & self.CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_R

    @property
    def has_attribute_U(self) -> int:
        if not self.is_attribute_group:
            raise ExceptionComponentDescriptorAccessError('Accessing ATTRIBUTE property U when not a ATTRIBUTE type.')
        return self._bits_4_8 & self.CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_U

    @property
    def has_attribute_V(self) -> int:
        if not self.is_attribute_group:
            raise ExceptionComponentDescriptorAccessError('Accessing ATTRIBUTE property V when not a ATTRIBUTE type.')
        return self._bits_4_8 & self.CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_V

    #
    # ------------- END: Characteristics and Component Format --------------
