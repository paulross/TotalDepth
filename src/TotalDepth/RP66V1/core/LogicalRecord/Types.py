"""
Implements the Logical Record Syntax.

References:
    [RP66V1 Section 3 Logical Record Syntax]

In particular:
    [RP66V1 Appendix A logical Record Types]
"""
import collections
import typing


# Code  Type        Desciption (sic)    Data Descriptor Reference Object Type
# 0     FDATA       Frame Data          FRAME
# 1     NOFORMAT    Unformatted Data    NO-FORMAT
# 2-126 ...         undefined,reserved  -
# 127   EOD         End of Data         -
TypeDescriptionDataDescriptorObjectReferenceType: typing.Tuple[bytes, str, bytes] = collections.namedtuple(
    'TypeDescriptionAllowableSetTypes', 'type, description, data_descriptor_reference_object_type')


IFLR_PUBLIC_CODE_MAP: typing.Dict[int, TypeDescriptionDataDescriptorObjectReferenceType] = {
    0: TypeDescriptionDataDescriptorObjectReferenceType(b'FDATA', 'Frame Data [RP66V1 Section 5.6]', b'FRAME'),
    1: TypeDescriptionDataDescriptorObjectReferenceType(b'NOFORMAT', 'Unformatted Data', b'NO-FORMAT'),
    # 2-126	-	undefined, reserved	-
    127: TypeDescriptionDataDescriptorObjectReferenceType(b'EOD', 'End of Data [RP66V1 Section 5.11]', b''),
}


# Reverse map of {set_type : lr_type, ...}
IFLR_PUBLIC_SET_TYPE_TO_CODE_MAP: typing.Dict[bytes, int] = {
    b'FRAME': 0,
    b'NO-FORMAT': 1,
}


IFLR_PUBLIC_CODE_MAP.update(
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


EFLR_PUBLIC_CODE_MAP: typing.Dict[int, TypeDescriptionAllowableSetTypes] = {
    0: TypeDescriptionAllowableSetTypes(b'FHLR', 'File Header [RP66V1 Section 5.1]', {b'FILE-HEADER', }),
    1: TypeDescriptionAllowableSetTypes(b'OLR', 'Origin [RP66V1 Section 5.2]', {b'ORIGIN', b'WELL-REFERENCE', }),
    2: TypeDescriptionAllowableSetTypes(b'AXIS', 'Coordinate Axis [RP66V1 Section 5.3]', {b'AXIS', }),
    3: TypeDescriptionAllowableSetTypes(b'CHANNL', 'Channel-related information [RP66V1 Section 5.5]', {b'CHANNEL', }),
    4: TypeDescriptionAllowableSetTypes(b'FRAME', 'Frame Data [RP66V1 Section 5.7]', {b'FRAME', b'PATH'}),
    5: TypeDescriptionAllowableSetTypes(
        b'STATIC', 'Static Data [RP66V1 Section 5.8]', {
            b'CALIBRATION', b'CALIBRATION-COEFFICIENT', b'CALIBRATION-MEASUREMENT', b'COMPUTATION', b'EQUIPMENT',
            b'GROUP', b'PARAMETER', b'PROCESS', b'SPICE', b'TOOL', b'ZONE',
        }
    ),
    6: TypeDescriptionAllowableSetTypes(b'SCRIPT', 'Textual Data [RP66V1 Section 6.1]', {b'COMMENT', b'MESSAGE'}),
    7: TypeDescriptionAllowableSetTypes(b'UPDATE', 'Update Data [RP66V1 Section 6.2]', {b'UPDATE'}),
    8: TypeDescriptionAllowableSetTypes(b'UDI', 'Unformatted Data Identifier [RP66V1 Section 5.10]', {b'NO-FORMAT'}),
    9: TypeDescriptionAllowableSetTypes(b'LNAME', 'Long Name [RP66V1 Section 5.4]', {b'LONG-NAME'}),
    10: TypeDescriptionAllowableSetTypes(
        b'SPEC', 'Specification [RP66V1 Section 7.1]', {
            b'ATTRIBUTE', b'CODE', b'EFLR', b'IFLR', b'OBJECT-TYPE', b'REPRESENTATION-CODE', b'SPECIFICATION',
            b'UNIT-SYMBOL',
        }
    ),
    11: TypeDescriptionAllowableSetTypes(
        b'DICT', 'Dictionary [RP66V1 Section 7.2]',	{
            b'BASE-DICTIONARY', b'IDENTIFIER', b'LEXICON', b'OPTION',
        }
    ),
    # 12-127	-	undefined, reserved	-
}

# Reverse map of {set_type : lr_type, ...}
EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP: typing.Dict[bytes, int] = {}

for _k, _v in EFLR_PUBLIC_CODE_MAP.items():
    for set_type in _v.allowable_set_types:
        assert set_type not in EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP, f'{set_type} already in EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP'
        EFLR_PUBLIC_SET_TYPE_TO_CODE_MAP[set_type] = _k


# Add undefined and reserved codes
EFLR_PUBLIC_CODE_MAP.update(
    {
        _k: TypeDescriptionAllowableSetTypes(b'', 'undefined, reserved', {b''}) for _k in range(12, 128)
    }
)


def is_public(code: int) -> bool:
    return code < 128


def is_private(code: int) -> bool:
    return not is_public(code)
