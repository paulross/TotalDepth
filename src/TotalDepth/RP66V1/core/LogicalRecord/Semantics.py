"""
The DLIS Semantics of Logical Records.

References:

    [RP66V1 Chapter 4: Semantic Terminology and Rules]
    [RP66V1 Chapter 5: Semantics: Static and Frame Data]

Links:

    http://w3.energistics.org/rp66/v1/rp66v1_sec4.html
    http://w3.energistics.org/rp66/v1/rp66v1_sec5.html

TODO: Use this for validating EFLRs.
"""
import collections
import typing

from TotalDepth.RP66V1.core.LogicalRecord import EFLR
from TotalDepth.RP66V1.core.LogicalRecord.EFLR import AttributeBase


class Restrictions:
    """Imposes semantic restrictions."""
    # TODO: V also?
    KEYS = {'C', 'R', 'U'}
    ABSENT = 'absent'
    UNRESTRICTED = None

    def __init__(self, **kwargs):
        if set(kwargs.keys()) - self.KEYS:
            raise ValueError(f'Kwargs: {kwargs} has keys not in {self.KEYS}')
        self._C: int = kwargs.get('C', self.UNRESTRICTED)
        self._R: typing.Tuple[bytes, ...] = kwargs.get('R', self.UNRESTRICTED)
        self._U = kwargs.get('U', self.UNRESTRICTED)

    def C(self, value: int) -> bool:
        if self._C is self.UNRESTRICTED:
            return True
        return value == self._C

    def R(self, value: bytes) -> bool:
        if self._R is self.UNRESTRICTED:
            return True
        return value in self._R

    def U(self, value) -> bool:
        if self._U is self.UNRESTRICTED:
            return True
        if self._U == self.ABSENT:
            # TODO: return value is None?
            return False
        return True


#: [RP66V1 Section 4.4]
FREQUENTLY_USED_ATTRIBUTES = {
    # [RP66V1 Section 4.4.1]
    b'LONG-NAME': Restrictions(C=1, R=(b'OBNAME', b'ASCII',)),
    # [RP66V1 Section 4.4.2]
    b'DESCRIPTION': Restrictions(C=1, R=(b'ASCII',)),
    # [RP66V1 Section 4.4.3]
    b'DIMENSION': Restrictions(R=(b'UVARI',)),
    # [RP66V1 Section 4.4.1]
    b'AXIS': Restrictions(R=(b'OBNAME',)),
}


#: [RP66V1 Section 5]
SEMANTICS: typing.Dict[bytes, typing.Dict[bytes, Restrictions]] = {
    # [RP66V1 Section 5.7 Figure 5-8]
    b'FRAME': {
        b'DESCRIPTION': FREQUENTLY_USED_ATTRIBUTES[b'DESCRIPTION'],
        b'CHANNELS': Restrictions(R=(b'OBNAME',)),
        b'INDEX-TYPE': Restrictions(C=1, R=(b'IDENT',)),
        b'DIRECTION': Restrictions(C=1, R=(b'IDENT',)),
        b'SPACING': Restrictions(C=1),
        b'ENCRYPTED': Restrictions(C=1, R=(b'USHORT',)),
        b'INDEX-MIN': Restrictions(C=1),
        b'INDEX-MAX': Restrictions(C=1),
    }

}


def _attribute_passes_restrictions(attr: AttributeBase, restriction: Restrictions) -> bool:
    # TODO: Return a list of error indications rather than a bool.
    return restriction.C(attr.count) and restriction.R(attr.rep_code) and restriction.U(attr.units)


def object_passes_restrictions(eflr_set_type: bytes, obj: EFLR.Object) -> bool:
    # TODO: Return a list of error indications rather than a bool.
    if eflr_set_type in SEMANTICS:
        for attr in obj.attrs:
            restrictions: typing.Dict[bytes, Restrictions] = SEMANTICS[eflr_set_type]
            if attr.label not in restrictions:
                return False
    return True


def eflr_passes_restrictions(eflr: EFLR.ExplicitlyFormattedLogicalRecord) -> bool:
    # TODO: Return a list of error indications rather than a bool.
    if eflr.set.type in SEMANTICS:
        for obj in eflr.objects:
            if not object_passes_restrictions(eflr.set.type, obj):
                return False
    return True
