import pprint
import typing

from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core.LogicalRecord import EFLR


def stringify_object_by_type(obj: typing.Any) -> str:
    """Convert objects to strings for HTML or text presentation."""
    if isinstance(obj, RepCode.ObjectName):
        # return obj.I.decode('ascii')
        # return str(obj)
        return f'{obj.I.decode("ascii")} (O: {obj.O} C: {obj.C})'
    if isinstance(obj, EFLR.AttributeBase):
        return stringify_object_by_type(obj.value)
    if obj is None:
        return '-'
    if isinstance(obj, bytes):
        # print('TRACE:', obj)
        try:
            return obj.decode('ascii')
        except UnicodeDecodeError:
            return obj.decode('latin-1')
    if isinstance(obj, list):
        if len(obj) == 1:
            return stringify_object_by_type(obj[0])
        return '[' + ', '.join(stringify_object_by_type(o) for o in obj) + ']'
    if isinstance(obj, tuple):
        if len(obj) == 1:
            return stringify_object_by_type(obj[0])
        return '(' + ', '.join(stringify_object_by_type(o) for o in obj) + ')'
    return str(obj)
