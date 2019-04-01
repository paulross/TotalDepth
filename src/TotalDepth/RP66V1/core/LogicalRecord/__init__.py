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

TypeDescriptionAllowableSetTypes = collections.namedtuple(
    'TypeDescriptionAllowableSetTypes', 'type, description, data_descriptor_reference_object_type')
IFLR_PUBLIC_MAP: typing.Dict[int, TypeDescriptionAllowableSetTypes] = {
    0: TypeDescriptionAllowableSetTypes('FDATA', 'Frame Data', 'FRAME'),
    1: TypeDescriptionAllowableSetTypes('NOFORMAT', 'Unformatted Data', 'NO-FORMAT'),
    127: TypeDescriptionAllowableSetTypes('EOD', 'End of Data', ''),
}
IFLR_PUBLIC_MAP.update({_k: TypeDescriptionAllowableSetTypes('', 'undefined, reserved', '') for _k in range(2, 127)})

# TODO: EFLR


def IFLR_is_public(code: int) -> bool:
    return code < 128



