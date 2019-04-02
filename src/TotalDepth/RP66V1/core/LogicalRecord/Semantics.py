"""
The DLIS Semantics of Logical Records.

Reference [RP66V1 Chapter 5: Semantics: Static and Frame Data]
Link: http://w3.energistics.org/rp66/v1/rp66v1_sec5.html
"""
import collections
import typing


class Restrictions:
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

    def U(self, _value) -> bool:
        if self._U is self.UNRESTRICTED:
            return True
        if self._U == self.ABSENT:
            return False
        return True


RestrictionsComments: typing.Tuple[Restrictions, str] = collections.namedtuple(
    'RestrictionsComments', 'restrictions, comments'
)

StaticAndFrameDataSemantics = collections.namedtuple(
    'StaticAndFrameDataSemantics', 'code, abbreviation, full_name, section, attributes'
)

FHLR = {
    b'SEQUENCE-NUMBER': RestrictionsComments(
        Restrictions(C=1, R=('ASCII',), U=Restrictions.ABSENT),
        """1.The Sequence-Number Attribute is the ASCII representation of a positive integer that indicates the sequential position of the Logical File in a Storage Set.
The Value of the Sequence-Number Attribute must meet the following requirements:

* The number of ASCII characters is fixed at 10 characters, right justified and padded to the left with blank characters (ASCII code 3210). That is, the character representing the least significant digit of the Sequence-Number is in byte 10.
* The Sequence-Number of any Logical File, expressed as an integer, must be greater than the Sequence-Number of the Logical File that immediately precedes it in the Storage Set.
  The Sequence-Number of the first Logical File in a Storage Set may be any positive integer."""
    ),
    b'ID': RestrictionsComments(
        Restrictions(C=1, R=('ASCII',), U=Restrictions.ABSENT),
        """2.The ID Attribute is a descriptive identification of the Logical File.
        The Value of the ID Attribute must meet the following requirement:

* The number of ASCII characters is fixed at 65 characters (width of a standard printed page)."""
    ),
}


# foo = LabelRestrictions('FOO', Restrictions(C=1, R='ASCII'), '')
# print(foo)
# print(foo.restrictions.__dict__)
#
# foo = LabelRestrictions('FOO', Restrictions(C=1, R='ASCII', U='absent'), '')
# print(foo)
# print(foo.restrictions.__dict__)

# bar = LabelRestrictions('FOO', Restrictions(C=1, R='ASCII', X='asd'))
