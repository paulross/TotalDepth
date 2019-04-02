"""
Implements the Logical Record Syntax. References:
[RP66V1 Section 3 Logical Record Syntax]
[RP66V1 Appendix A logical Record Types]
"""

# Code  Type        Desciption (sic)    Data Descriptor Reference Object Type
# 0     FDATA       Frame Data          FRAME
# 1     NOFORMAT    Unformatted Data    NO-FORMAT
# 2-126 ...         undefined,reserved  -
# 127   EOD         End of Data         -
import collections
import typing

TypeDescriptionDataDescriptorObjectReferenceType: typing.Tuple[bytes, str, bytes] = collections.namedtuple(
    'TypeDescriptionAllowableSetTypes', 'type, description, data_descriptor_reference_object_type')

IFLR_PUBLIC_MAP: typing.Dict[int, TypeDescriptionDataDescriptorObjectReferenceType] = {
    0: TypeDescriptionDataDescriptorObjectReferenceType(b'FDATA', 'Frame Data', b'FRAME'),
    1: TypeDescriptionDataDescriptorObjectReferenceType(b'NOFORMAT', 'Unformatted Data', b'NO-FORMAT'),
    127: TypeDescriptionDataDescriptorObjectReferenceType(b'EOD', 'End of Data', b''),
}
IFLR_PUBLIC_MAP.update(
    {
        _k: TypeDescriptionDataDescriptorObjectReferenceType(b'', 'undefined, reserved', b'') for _k in range(2, 127)
    }
)


# A.2 Explicitly Formatted Logical Records
#
# Numeric codes 0-127 are reserved for Public EFLRs. Codes 128-255 are reserved for Private EFLRs.
# Figure A-2 defines numeric codes for Explicitly Formatted Logical Record Types.
# Figure A-2. Numeric Codes for Public EFLR Types
# Code	Type	Description	Allowable Set Types

TypeDescriptionAllowableSetTypes: typing.Tuple[bytes, str, typing.Set[bytes]] = collections.namedtuple(
    'TypeDescriptionAllowableSetTypes', 'type, description, allowable_set_types')

EFLR_PUBLIC_MAP: typing.Dict[int, TypeDescriptionAllowableSetTypes] = {
    0: TypeDescriptionAllowableSetTypes(b'FHLR', 'File Header', {b'FILE-HEADER', }),
    1: TypeDescriptionAllowableSetTypes(b'OLR', 'Origin', {b'ORIGIN', b'WELL-REFERENCE', }),
    2: TypeDescriptionAllowableSetTypes(b'AXIS', 'Coordinate Axis', {b'AXIS', }),
    3: TypeDescriptionAllowableSetTypes(b'CHANNL', 'Channel-related information', {b'CHANNEL', }),
    4: TypeDescriptionAllowableSetTypes(b'FRAME', 'Frame Data', {b'FRAME', b'PATH'}),
    5: TypeDescriptionAllowableSetTypes(
        b'STATIC', 'Static Data', {
            b'CALIBRATION', b'CALIBRATION-COEFFICIENT', b'CALIBRATION-MEASUREMENT', b'COMPUTATION', b'EQUIPMENT',
            b'GROUP', b'PARAMETER', b'PROCESS', b'SPICE', b'TOOL', b'ZONE',
        }
    ),
    6: TypeDescriptionAllowableSetTypes(b'SCRIPT', 'Textual Data', {b'COMMENT', b'MESSAGE'}),
    7: TypeDescriptionAllowableSetTypes(b'UPDATE', 'Update Data', {b'UPDATE'}),
    8: TypeDescriptionAllowableSetTypes(b'UDI', 'Unformatted Data Identifier', {b'NO-FORMAT'}),
    9: TypeDescriptionAllowableSetTypes(b'LNAME', 'Long Name', {b'LONG-NAME'}),
    10: TypeDescriptionAllowableSetTypes(
        b'SPEC', 'Specification', {
            b'ATTRIBUTE', b'CODE', b'EFLR', b'IFLR', b'OBJECT-TYPE', b'REPRESENTATION-CODE', b'SPECIFICATION',
            b'UNIT-SYMBOL',
        }
    ),
    11: TypeDescriptionAllowableSetTypes(
        b'DICT', 'Dictionary',	{
            b'BASE-DICTIONARY', b'IDENTIFIER', b'LEXICON', b'OPTION',
        }
    ),
}

# 12-127	-	undefined, reserved	-
EFLR_PUBLIC_MAP.update(
    {
        _k: TypeDescriptionAllowableSetTypes(b'', 'undefined, reserved', {b''}) for _k in range(12, 128)
    }
)


def IFLR_is_public(iflr_code: int) -> bool:
    return iflr_code < 128



