import argparse
import typing


class Slice:
    """Class that wraps a builtin slice object for integers and provides some useful APIs.
    NOTE: The builti slice object can take non-integer values but raises later, for example::

        slice(1,4, 2.0).indices(45)
    """
    def __init__(self,
                 start:typing.Union[None, int]=None,
                 stop:typing.Union[None, int]=None,
                 step:typing.Union[None, int]=None):
        # Fail fast, unlike the builtin slice
        for name in ('start', 'stop', 'step'):
            if not isinstance(locals()[name], (type(None), int)):
                raise TypeError(f'{name} must be None or an integer not {type(locals()[name])}')
        self.slice = slice(start, stop, step)

    def count(self, length: int) -> int:
        """Returns the number of values that will result if the slice is applied to a sequence of given length."""
        start, stop, step = self.slice.indices(length)
        ret = (stop - start) // step
        return ret

    def range(self, length: int) -> range:
        """Returns a builtin range object for the sequence of the given length."""
        return range(*self.slice.indices(length))

    def indices(self, length: int) -> typing.List[int]:
        """Returns a fully composed list of indices for the sequence of the given length."""
        return list(self.range(length))

    def __eq__(self, other) -> bool:
        if other.__class__ == self.__class__:
            return other.slice == self.slice
        return NotImplemented

    def long_str(self, length: int) -> str:
        rng = self.range(length)
        return f'<Slice on length={length} start={rng.start} stop={rng.stop} step={rng.step}>'

    def __str__(self) -> str:
        return f'<Slice.{str(self.slice)}>'


def create_slice(slice_string: str) -> Slice:
    """Returns a Slice object from a string such as:
    '', 'None,72', 'None,72,14'
    """
    def convert(a_string):
        if a_string in ('None', ''):
            return None
        return int(a_string)

    parts = [convert(p.strip()) for p in slice_string.split(',')]
    if len(parts) > 3:
        raise ValueError(f'Too many parts in {slice_string}')
    if len(parts) == 0:
        return Slice()
    if len(parts) == 1:
        return Slice(stop=parts[0])
    # 2 or 3 parts
    return Slice(*parts)


def add_frame_slice_to_argument_parser(parser: argparse.ArgumentParser, help_prefix: str='') -> None:
    help_text = 'Slice the frames by start,stop,step as a comma separated list.' \
        ' Values can be absent or  "None".' \
        ' Examples: ",," - every frame' \
        ', ",,2" - every other frame' \
        ', ",10," - frames 0 to 9' \
        ', "4,10,2" - frames 4, 6, 8' \
        ', "40,-1,4" - every fourth frame from 40 to the end' \
        '. Results will be truncated by frame array length.' \
        ' [default: "%(default)s"]'
    if help_prefix:
        help_text = f'{help_prefix} {help_text}'
    parser.add_argument('--frame-slice', default=',,', type=str, help=help_text)
