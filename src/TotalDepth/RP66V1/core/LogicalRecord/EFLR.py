"""
Implements the Explicitly Formatted Logical Record (EFFLR) [RP66V1 Section 3 Logical Record Syntax]

References:
    RP66V1: http://w3.energistics.org/rp66/v1/rp66v1.html

Specifically section 3:
    http://w3.energistics.org/rp66/v1/rp66v1_sec3.html
"""
# import collections
import logging
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core.File import LogicalData
from TotalDepth.RP66V1.core.LogicalRecord.ComponentDescriptor import ComponentDescriptor
from TotalDepth.RP66V1.core.LogicalRecord.Duplicates import DuplicateObjectStrategy
from TotalDepth.RP66V1.core import RepCode


logger = logging.getLogger(__file__)


class ExceptionEFLR(ExceptionTotalDepthRP66V1):
    """General Exception class for EFLR errors."""
    pass


class ExceptionEFLRSet(ExceptionEFLR):
    """Exception class for EFLR Set errors."""
    pass


class ExceptionEFLRSetDuplicateObjectNames(ExceptionEFLRSet):
    """Exception class for EFLR Set with duplicate object names."""
    pass


class ExceptionEFLRAttribute(ExceptionEFLR):
    """Exception class for EFLR Attribute errors."""
    pass


class ExceptionEFLRTemplate(ExceptionEFLR):
    """Exception class for EFLR Template errors."""
    pass


class ExceptionEFLRTemplateDuplicateLabel(ExceptionEFLRTemplate):
    """Exception class for EFLR Template with duplicate object names."""
    pass


class ExceptionEFLRObject(ExceptionEFLR):
    """Exception class for EFLR Object errors."""
    pass


class ExceptionEFLRObjectDuplicateLabel(ExceptionEFLRObject):
    """Exception class for EFLR Object with duplicate labels."""
    pass


class Set:
    """Class that represents a component set. See [RP66V1 3.2.2.1 Component Descriptor]"""
    def __init__(self, ld: LogicalData):
        if ld.index != 0:
            raise ExceptionEFLRSet(f'Trying to create a Set where the LogicalData {ld} index is non-zero.')
        component_descriptor = ComponentDescriptor(ld.read())
        if not component_descriptor.is_set_group:
            raise ExceptionEFLRSet(f'Component Descriptor does not represent a set but a {component_descriptor.type}.')
        self.type: bytes = RepCode.IDENT(ld)
        self.name: bytes = ComponentDescriptor.CHARACTERISTICS_AND_COMPONENT_FORMAT_SET_MAP['N'].global_default
        if component_descriptor.has_set_N:
            self.name = RepCode.IDENT(ld)
        self.logical_data_consumed = ld.index

    def __str__(self) -> str:
        """String representation."""
        return f'EFLR Set type: {self.type} name: {self.name}'

    def __eq__(self, other) -> bool:
        """Equality operator."""
        if other.__class__ == self.__class__:
            return self.type == other.type and self.name == other.name
        return NotImplemented


class AttributeBase:
    """Class that represents a component attribute. See [RP66V1 3.2.2.1 Component Descriptor]"""
    def __init__(self, component_descriptor: ComponentDescriptor):
        if not component_descriptor.is_attribute_group:
            raise ExceptionEFLRAttribute(
                f'Component Descriptor does not represent a attribute but a {component_descriptor.type}.'
            )
        self.component_descriptor = component_descriptor
        self.label = ComponentDescriptor.CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_MAP['L'].global_default
        self.count = ComponentDescriptor.CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_MAP['C'].global_default
        self.rep_code = ComponentDescriptor.CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_MAP['R'].global_default
        self.units = ComponentDescriptor.CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_MAP['U'].global_default
        self.value = ComponentDescriptor.CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_MAP['V'].global_default

    def __eq__(self, other):
        """Equality operator."""
        if isinstance(other, AttributeBase):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __str__(self) -> str:
        """String representation."""
        # print('TRACE: rep_code', self.rep_code)
        try:
            rep_code_str = RepCode.REP_CODE_INT_TO_STR[self.rep_code]
        except KeyError:
            rep_code_str = 'UNKNOWN'
        return f'CD: {self.component_descriptor} L: {self.label} C: {self.count}' \
            f' R: {self.rep_code:d} ({rep_code_str}) U: {self.units} V: {self.value}'

    def stringify_value(self, stringify_function: typing.Callable) -> str:
        """Return the value as a string."""
        value_as_string = stringify_function(self.value)
        if self.units == ComponentDescriptor.CHARACTERISTICS_AND_COMPONENT_FORMAT_ATTRIBUTE_MAP['U'].global_default:
            return value_as_string
        # UNITS must be in ASCII [RP66V1 Appendix B, B.27 Code UNITS: Units Expression]
        # So .decode("ascii") should be OK.
        # In practice not as non-ascii characters such as b'\xb0' (degree symbol) can appear so we fall back to latin-1.
        try:
            return f'{value_as_string} [{self.units.decode("ascii")}]'
        except UnicodeDecodeError:
            return f'{value_as_string} [{self.units.decode("latin-1")}]'


class TemplateAttribute(AttributeBase):
    """Class that represents a component template. See [RP66V1 3.2.2.1 Component Descriptor]"""
    def __init__(self, component_descriptor: ComponentDescriptor, ld: LogicalData):
        super().__init__(component_descriptor)
        if self.component_descriptor.has_attribute_L:
            self.label = RepCode.IDENT(ld)
        if self.component_descriptor.has_attribute_C:
            self.count = RepCode.UVARI(ld)
        if self.component_descriptor.has_attribute_R:
            self.rep_code = RepCode.USHORT(ld)
        if self.component_descriptor.has_attribute_U:
            self.units = RepCode.UNITS(ld)
        if self.component_descriptor.has_attribute_V:
            self.value = [RepCode.code_read(self.rep_code, ld) for _i in range(self.count)]


class Attribute(AttributeBase):
    """Class that represents a component attribute. See [RP66V1 3.2.2.1 Component Descriptor]"""
    def __init__(self,
                 component_descriptor: ComponentDescriptor,
                 ld: LogicalData,
                 template_attribute: TemplateAttribute,
                 ):
        super().__init__(component_descriptor)
        if self.component_descriptor.has_attribute_L:
            self.label = RepCode.IDENT(ld)
        else:
            self.label = template_attribute.label
        if self.component_descriptor.has_attribute_C:
            self.count = RepCode.UVARI(ld)
        else:
            self.count = template_attribute.count
        if self.component_descriptor.has_attribute_R:
            self.rep_code = RepCode.USHORT(ld)
        else:
            self.rep_code = template_attribute.rep_code
        if self.component_descriptor.has_attribute_U:
            self.units = RepCode.UNITS(ld)
        else:
            self.units = template_attribute.units
        if self.component_descriptor.has_attribute_V:
            self.value = [RepCode.code_read(self.rep_code, ld) for _i in range(self.count)]
        else:
            self.value = template_attribute.value


class Template:
    """Class that represents a component template. See [RP66V1 3.2.2.1 Component Descriptor]"""
    def __init__(self, ld: LogicalData):
        """Populate the template with the Logical Data."""
        self.attrs: typing.List[TemplateAttribute] = []
        self.attr_label_map: typing.Dict[bytes, int] = {}
        while True:
            component_descriptor = ComponentDescriptor(ld.read())
            if not component_descriptor.is_attribute_group:
                raise ExceptionEFLRTemplate(
                    f'Component Descriptor does not represent a attribute but a {component_descriptor.type}.'
                )
            template_attribute = TemplateAttribute(component_descriptor, ld)
            if template_attribute.label in self.attr_label_map:
                raise ExceptionEFLRTemplateDuplicateLabel(f'Duplicate template label {template_attribute.label}')
            self.attr_label_map[template_attribute.label] = len(self.attrs)
            self.attrs.append(template_attribute)
            if ld.remain == 0:
                # This is kind of unusual, it is an EFLR with a template but no objects.
                break
            next_component_descriptor = ComponentDescriptor(ld.peek())
            if next_component_descriptor.is_object:
                break
        self.logical_data_consumed = ld.index

    def __len__(self) -> int:
        """Return the number of columns described by this Template."""
        return len(self.attrs)

    def __getitem__(self, item) -> TemplateAttribute:
        """Get a TemplateAttribute by name or integer index."""
        if item in self.attr_label_map:
            return self.attrs[self.attr_label_map[item]]
        return self.attrs[item]

    def __eq__(self, other) -> bool:
        """Equality operator."""
        if other.__class__ == Template:
            return self.attrs == other.attrs
        return NotImplemented

    def __str__(self) -> str:
        """String representation."""
        return '\n'.join(str(a) for a in self.attrs)

    def header_as_strings(self, stringify_function: typing.Callable) -> typing.List[str]:
        """Return the TemplateAttributes as strings."""
        return [stringify_function(attr.label) for attr in self.attrs]


class Object:
    """Class that represents a component object. See [RP66V1 3.2.2.1 Component Descriptor].
    Essentially this is one row in the table as a list of Atributes."""
    def __init__(self, ld: LogicalData, template: Template):
        component_descriptor = ComponentDescriptor(ld.read())
        if not component_descriptor.is_object:
            raise ExceptionEFLRObject(
                f'Component Descriptor does not represent a object but a {component_descriptor.type}.')
        self.name: RepCode.ObjectName = RepCode.OBNAME(ld)
        self.attrs: typing.List[typing.Union[AttributeBase, None]] = []
        self.attr_label_map: typing.Dict[bytes, int] = {}
        index: int = 0
        while True:
            component_descriptor = ComponentDescriptor(ld.read())
            if not component_descriptor.is_attribute_group:
                raise ExceptionEFLRObject(
                    f'Component Descriptor does not represent a attribute but a {component_descriptor.type}.'
                )
            if template[index].component_descriptor.is_invariant_attribute:
                self.attrs.append(template[index])
            elif template[index].component_descriptor.is_absent_attribute:
                self.attrs.append(None)
            else:
                # TODO: Check the attribute label is the same as the template. Reference [RP66V1 Section 4.5]
                self.attrs.append(Attribute(component_descriptor, ld, template[index]))
                if ld.remain == 0 or ComponentDescriptor(ld.peek()).is_object:
                    break
                # next_component_descriptor = ComponentDescriptor(ld.peek())
                # if next_component_descriptor.is_object:
                #     break
            index += 1
        while len(self.attrs) < len(template):
            self.attrs.append(template[len(self.attrs)])
        if len(template) != len(self.attrs):
            raise ExceptionEFLRObject(
                f'Template specifies {len(template)} attributes but Logical Data has {len(self.attrs)}'
            )
        # Now populate self.attr_label_map
        for a, attr in enumerate(self.attrs):
            if attr is None:
                label = template.attrs[a].label
            else:
                label = attr.label
                # TODO: Assert that the attribute label is the same as the template. Reference [RP66V1 Section 4.5]
            if label in self.attr_label_map:
                raise ExceptionEFLRObjectDuplicateLabel(f'Duplicate Attribute label {label}')
            self.attr_label_map[label] = a

    def __len__(self) -> int:
        """Return the number of attributes (columns) for this row."""
        return len(self.attrs)

    def __getitem__(self, item) -> typing.Union[AttributeBase, None]:
        """Get an Attribute (column) by name or integer index."""
        if item in self.attr_label_map:
            return self.attrs[self.attr_label_map[item]]
        return self.attrs[item]

    def __eq__(self, other) -> bool:
        """Equality operator."""
        if other.__class__ == Object:
            return self.name == other.name and self.attrs == other.attrs and self.attr_label_map == other.attr_label_map
        return NotImplemented

    def __str__(self) -> str:
        """String representation."""
        strs = [
            str(self.name)
        ]
        strs.extend(
            ['  {}'.format(a) for a in self.attrs]
        )
        return '\n'.join(strs)

    def values_as_strings(self, stringify_function: typing.Callable) -> typing.List[str]:
        """Return the Attribute values as strings."""
        ret = [attr.stringify_value(stringify_function) for attr in self.attrs]
        return ret

"""
2019-06-05 22:31:49,839 - EFLR.py - 1704 - WARNING  - Ignoring different Object with OBNAME: O: 0 C: 0 I: b'MLL/CP/K_FAC' already seen in the EFLR Set type: b'CALIBRATION-MEASUREMENT' name: b'216'.
2019-06-05 22:31:49,839 - EFLR.py - 1704 - WARNING  - WAS:
2019-06-05 22:31:49,839 - EFLR.py - 1704 - WARNING  - OBNAME: O: 0 C: 0 I: b'MLL/CP/K_FAC'
  CD: 001 00001 L: b'PHASE' C: 1 R: IDENT U: b'' V: [b'MASTER']
  CD: 000 00000 L: b'MEASUREMENT-SOURCE' C: 1 R: OBJREF U: b'' V: None
  CD: 001 00001 L: b'TYPE' C: 1 R: IDENT U: b'' V: [b'K_FAC']
  CD: 000 00000 L: b'DIMENSION' C: 1 R: UVARI U: b'' V: None
  CD: 000 00000 L: b'AXIS' C: 1 R: OBNAME U: b'' V: None
  CD: 001 00101 L: b'MEASUREMENT' C: 1 R: FSINGL U: b'' V: [0.014299999922513962]
  CD: 000 00000 L: b'SAMPLE-COUNT' C: 1 R: IDENT U: b'' V: None
  CD: 000 00000 L: b'MAXIMUM-DEVIATION' C: 1 R: IDENT U: b'' V: None
  CD: 000 00000 L: b'STANDARD-DEVIATION' C: 1 R: IDENT U: b'' V: None
  CD: 001 00101 L: b'BEGIN-TIME' C: 1 R: DTIME U: b'' V: [<<class 'TotalDepth.RP66V1.core.RepCode.DateTime'> 2014-08-24 00:56:19.000 STD>]
  CD: 000 00000 L: b'DURATION' C: 1 R: IDENT U: b'' V: None
  CD: 000 00000 L: b'REFERENCE' C: 1 R: IDENT U: b'' V: None
  CD: 000 00000 L: b'STANDARD' C: 1 R: IDENT U: b'' V: None
  CD: 000 00000 L: b'PLUS-TOLERANCE' C: 1 R: IDENT U: b'' V: None
  CD: 000 00000 L: b'MINUS-TOLERANCE' C: 1 R: IDENT U: b'' V: None
2019-06-05 22:31:49,840 - EFLR.py - 1704 - WARNING  - NOW:
2019-06-05 22:31:49,840 - EFLR.py - 1704 - WARNING  - OBNAME: O: 0 C: 0 I: b'MLL/CP/K_FAC'
  CD: 001 00001 L: b'PHASE' C: 1 R: IDENT U: b'' V: [b'MASTER']
  CD: 000 00000 L: b'MEASUREMENT-SOURCE' C: 1 R: OBJREF U: b'' V: None
  CD: 001 00001 L: b'TYPE' C: 1 R: IDENT U: b'' V: [b'K_FAC']
  CD: 000 00000 L: b'DIMENSION' C: 1 R: UVARI U: b'' V: None
  CD: 000 00000 L: b'AXIS' C: 1 R: OBNAME U: b'' V: None
  CD: 001 00101 L: b'MEASUREMENT' C: 1 R: FSINGL U: b'' V: [0.014299999922513962]
  CD: 000 00000 L: b'SAMPLE-COUNT' C: 1 R: IDENT U: b'' V: None
  CD: 000 00000 L: b'MAXIMUM-DEVIATION' C: 1 R: IDENT U: b'' V: None
  CD: 000 00000 L: b'STANDARD-DEVIATION' C: 1 R: IDENT U: b'' V: None
  CD: 001 00101 L: b'BEGIN-TIME' C: 1 R: DTIME U: b'' V: [<<class 'TotalDepth.RP66V1.core.RepCode.DateTime'> 2014-08-16 08:55:50.000 STD>]
  CD: 000 00000 L: b'DURATION' C: 1 R: IDENT U: b'' V: None
  CD: 000 00000 L: b'REFERENCE' C: 1 R: IDENT U: b'' V: None
  CD: 000 00000 L: b'STANDARD' C: 1 R: IDENT U: b'' V: None
  CD: 000 00000 L: b'PLUS-TOLERANCE' C: 1 R: IDENT U: b'' V: None
  CD: 000 00000 L: b'MINUS-TOLERANCE' C: 1 R: IDENT U: b'' V: None
"""


class PublicEFLRType(typing.NamedTuple):
    """From [RP66V1 Appendix A: Logical Record Types] Figure A-2. Numeric Codes for Public EFLR Types."""
    code: int
    type: bytes
    description: str
    allowable_set_types: typing.Set[bytes]

#: From [RP66V1 Appendix A: Logical Record Types] Figure A-2. Numeric Codes for Public EFLR Types
PUBLIC_EFLR_TYPES: typing.Dict[int, PublicEFLRType] = {
    0: PublicEFLRType(0, b'FHLR', 'File header', {b'FILE-HEADER'}),
    1: PublicEFLRType(1, b'OLR', 'Origin', {b'ORIGIN', b'WELL-REFERENCE'}),
    2: PublicEFLRType(2, b'AXIS', 'Coordinate Axis', {b'AXIS'}),
    3: PublicEFLRType(3, b'CHANNL', 'Channel-related information', {b'CHANNEL'}),
    4: PublicEFLRType(4, b'FRAME', 'Frame Data', {b'FRAME', b'PATH'}),
    5: PublicEFLRType(5, b'STATIC', 'Static Data', {
        b'CALIBRATION', b'CALIBRATION-COEFFICIENT', b'CALIBRATION-MEASUREMENT', b'COMPUTATION', b'EQUIPMENT', b'GROUP',
        b'PARAMETER', b'PROCESS', b'SPICE', b'TOOL', b'ZONE'}),
    6: PublicEFLRType(6, b'SCRIPT', 'Textual Data', {b'COMMENT', b'MESSAGE'}),
    7: PublicEFLRType(7, b'UPDATE', 'Update Data', {b'UPDATE'}),
    8: PublicEFLRType(8, b'UDI', 'Unformatted Data Identifier', {b'NO-FORMAT'}),
    9: PublicEFLRType(9, b'LNAME', 'Long Name', {b'LONG-NAME'}),
    10: PublicEFLRType(10, b'SPEC', 'Specification',
                       {b'ATTRIBUTE', b'CODE', b'EFLR', b'IFLR', b'OBJECT-TYPE', b'REPRESENTATION-CODE',
                        b'SPECIFICATION', b'UNIT-SYMBOL'}),
    11: PublicEFLRType(11, b'DICT', 'Dictionary', {b'BASE-DICTIONARY', b'IDENTIFIER', b'LEXICON', b'OPTION'}),
}


class ExplicitlyFormattedLogicalRecord:
    """Represents a RP66V1 Explicitly Formatted Logical Record (EFLR).
    Effectively this is a table containing a list of rows, each row is represented by an Object."""
    #: The strategy for dealing with duplicate objects.
    DUPE_OBJECT_STRATEGY = DuplicateObjectStrategy.REPLACE
    #: What level to log duplicate object operations.
    DUPE_OBJECT_LOGGER = logger.warning

    def __init__(self, lr_type: int, ld: LogicalData):
        self.lr_type: int = lr_type
        self.logical_data_consumed = 0
        self.set: Set = Set(ld)
        self.template: Template = Template(ld)
        # This object list contains all objects not including duplicates.
        self.objects: typing.List[Object] = []
        # This is the final object name map after de-duplication depending on the de-duplication strategy.
        # TODO: Perfomance. Use self.object_name_map throughout then don't need to rebuild it if there are duplicates
        #  to remove.
        self.object_name_map: typing.Dict[RepCode.ObjectName, int] = {}
        temp_object_name_map: typing.Dict[RepCode.ObjectName, int] = {}
        dupes_to_remove: typing.List[int] = []
        while ld:
            obj = Object(ld, self.template)
            if obj.name not in temp_object_name_map:
                temp_object_name_map[obj.name] = len(self.objects)
                self.objects.append(obj)
            else:
                self._handle_duplicate_object(obj, temp_object_name_map, dupes_to_remove)
        # Clear out any duplicates then index those remaining.
        dupes_to_remove.sort()
        for i in reversed(dupes_to_remove):
            self.DUPE_OBJECT_LOGGER(f'Cleaning table by removing duplicate object:\n{self.objects[i]}')
            del self.objects[i]
        assert len(self.object_name_map) == 0
        for i, obj in enumerate(self.objects):
            self.object_name_map[obj.name] = i
        self.logical_data_consumed = ld.index

    def _handle_duplicate_object(self, obj: Object,
                                 temp_object_name_map: typing.Dict[RepCode.ObjectName, int],
                                 dupes_to_remove: typing.List[int]) -> None:
        """Applies a strategy to handle duplicate objects."""
        if self.DUPE_OBJECT_STRATEGY == DuplicateObjectStrategy.RAISE:
            raise ExceptionEFLRSetDuplicateObjectNames(
                f'Duplicate Object {obj.name} already seen in the {self.set}.'
            )
        elif self.DUPE_OBJECT_STRATEGY == DuplicateObjectStrategy.IGNORE:
            self.DUPE_OBJECT_LOGGER(f'Ignoring duplicate Object {obj.name} already seen in the {self.set}.')
        elif self.DUPE_OBJECT_STRATEGY == DuplicateObjectStrategy.REPLACE:
            self.DUPE_OBJECT_LOGGER(f'Replacing Object {obj.name} previously seen in the {self.set}.')
            # Mark the  old one to be removed
            dupes_to_remove.append(temp_object_name_map[obj.name])
            # Update the map with the new one and add the new one to the list of objects.
            temp_object_name_map[obj.name] = len(self.objects)
            self.objects.append(obj)
        elif self.DUPE_OBJECT_STRATEGY == DuplicateObjectStrategy.REPLACE_IF_DIFFERENT:
            # If equal then ignore
            prev_obj = self.objects[temp_object_name_map[obj.name]]
            if obj == prev_obj:
                self.DUPE_OBJECT_LOGGER(f'Ignoring duplicate Object {obj.name} already seen in the {self.set}.')
            else:
                # Not equal so report and replace
                self.DUPE_OBJECT_LOGGER(f'Replacing different Object {obj.name} already seen in the {self.set}.')
                self.DUPE_OBJECT_LOGGER('WAS:')
                self.DUPE_OBJECT_LOGGER(str(prev_obj))
                self.DUPE_OBJECT_LOGGER('NOW:')
                self.DUPE_OBJECT_LOGGER(str(obj))
                # Mark the old one to be removed
                dupes_to_remove.append(temp_object_name_map[obj.name])
                # Update the map with the new one and add the new one to the list of objects.
                temp_object_name_map[obj.name] = len(self.objects)
                self.objects.append(obj)
        elif self.DUPE_OBJECT_STRATEGY == DuplicateObjectStrategy.REPLACE_LATER_COPY:  # pragma: no cover
            # If later copy then  use  it regardless of content.
            if obj.name.C > self[obj.name].name.C:
                self.DUPE_OBJECT_LOGGER(
                    f'Replacing Object {obj.name} already seen in the {self.set}'
                    f' as C: {obj.name.C} > {self[obj.name].name.C}.'
                )
                # Mark the old one to be removed
                dupes_to_remove.append(temp_object_name_map[obj.name])
                # Update the map with the new one and add the new one to the list of objects.
                temp_object_name_map[obj.name] = len(self.objects)
                self.objects.append(obj)
            else:
                # Not a later copy so ignore it.
                self.DUPE_OBJECT_LOGGER(
                    f'Ignoring Object {obj.name} already seen in the {self.set}'
                    f' as C: {obj.name.C} > {self[obj.name].name.C}.'
                )
        else:  # pragma: no cover
            assert 0, f'Unsupported DuplicateObjectStrategy {self.DUPE_OBJECT_STRATEGY}'

    def __len__(self) -> int:
        """Returns the number of rows in the table."""
        assert len(self.objects) == len(self.object_name_map)
        return len(self.objects)

    def __getitem__(self, item) -> Object:
        """Get an Object (row) by name or integer index."""
        if item in self.object_name_map:
            return self.objects[self.object_name_map[item]]
        return self.objects[item]

    def __str__(self) -> str:
        """Short string representation."""
        return f'<ExplicitlyFormattedLogicalRecord {str(self.set)}>'

    def __eq__(self, other) -> bool:
        """Equality operator."""
        if other.__class__ == self.__class__:
            if self.lr_type == other.lr_type and self.set == other.set \
                    and self.object_name_map == other.object_name_map:
                # Check all the objects are equal
                assert len(self.objects) == len(other.objects)
                for a,  b in zip(self.objects, other.objects):
                    if a != b:
                        return False
                return True
            return False
        return NotImplemented

    def str_long(self) -> str:
        """Returns a long string representing the table."""
        ret = [
            str(self),
            f'  Template [{len(self.template)}]:'
        ]
        ret.extend('    {}'.format(line) for line in str(self.template).split('\n'))
        ret.append(f'  Objects [{len(self.objects)}]:')
        for obj in self.objects:
            ret.extend('    {}'.format(line) for line in str(obj).split('\n'))
        return '\n'.join(ret)

    def table_as_strings(self, stringify_function: typing.Callable, sort: bool) -> typing.List[typing.List[str]]:
        """Returns a list of strings representing the table."""
        ret = [
            ['ObjectName IDENT', 'O', 'C'] + self.template.header_as_strings(stringify_function),
        ]
        if sort:
            # print(f'TRACE: {sorted(self.object_name_map.keys())}')
            objects = [self[object_id] for object_id in sorted(self.object_name_map.keys())]
        else:
            objects = self.objects
        for obj in objects:
            row = [stringify_function(obj.name.I), f'{obj.name.O}', f'{obj.name.C}']
            row.extend(obj.values_as_strings(stringify_function))
            ret.append(row)
        return ret

    def is_key_value(self) -> bool:
        """True if this is a key/value table."""
        return len(self.objects) == 1

    def key_values(self, stringify_function: typing.Callable, sort: bool) -> typing.List[typing.List[str]]:
        """Returns a list of stringified key values. Will raise ExceptionEFLR if not a key/value table."""
        if self.is_key_value():
            ret = [['KEY', 'VALUE']]
            # key_values = zip(
            #     self.template.header_as_strings(conversion_function),
            #     self.objects[0].values_as_strings(conversion_function)
            # )
            key_values = zip(
                (attr.label for attr in self.template.attrs),
                self.objects[0].attrs
            )
            if sort:
                key_values = sorted(key_values)
            for k, v in key_values:
                ret.append([stringify_function(k), stringify_function(v)])
            return ret
        raise ExceptionEFLR('Can not represent EFLR as key->value table.')

    @property
    def shape(self) -> typing.Tuple[int, int]:
        """Shape as (rows, columns)"""
        return len(self), len(self.template)


def reduced_object_map(eflr: ExplicitlyFormattedLogicalRecord) -> typing.Dict[bytes, int]:
    """
    This returns a reduced lookup map that refers to the latest object by count.
    Key is the object IDENT, value is the ordinal into self.
    """
    ret: typing.Dict[bytes, int] = {}
    # Temporary to keep track of counts.
    name_count: typing.Dict[bytes, int] = {}
    for index, obj in enumerate(eflr.objects):
        name = obj.name.I
        if name not in ret or obj.name.C > name_count[name]:
            ret[name] = index
            name_count[name] = obj.name.C
    return ret
