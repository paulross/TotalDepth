import argparse
import typing


class Slice:
    """Class that wraps a builtin slice object for integers and provides some useful APIs.
    NOTE: The builtin slice object can take non-integer values but raises later, for example::

        slice(1, 4, 2.0).indices(45)
    """
    def __init__(self,
                 start: typing.Union[None, int] = None,
                 stop: typing.Union[None, int] = None,
                 step: typing.Union[None, int] = None):
        # Fail fast, unlike the builtin slice
        for name in ('start', 'stop', 'step'):
            if not isinstance(locals()[name], (type(None), int)):
                raise TypeError(f'{name} must be None or an integer not {type(locals()[name])}')
        self._slice = slice(start, stop, step)

    def count(self, length: int) -> int:
        """Returns the number of values that will result if the slice is applied to a sequence of given length."""
        start, stop, step = self._slice.indices(length)
        ret = (stop - start) // step
        return ret

    def range(self, length: int) -> range:
        """Returns a builtin range object for the sequence of the given length."""
        return range(*self._slice.indices(length))

    def indices(self, length: int) -> typing.List[int]:
        """Returns a fully composed list of indices for the sequence of the given length."""
        return list(self.range(length))

    def __eq__(self, other) -> bool:
        """Mostly used for testing."""
        if other.__class__ == self.__class__:
            return other._slice == self._slice
        return NotImplemented

    def long_str(self, length: int) -> str:
        rng = self.range(length)
        return f'<Slice on length={length} start={rng.start} stop={rng.stop} step={rng.step}>'

    def __str__(self) -> str:
        return f'<Slice.{str(self._slice)}>'


class Split:
    """This has the same API as Slice but takes a single integer and
    """
    def __init__(self, fraction: int):
        if fraction < 1:
            raise ValueError(f'fraction must be an integer >= 1 not {fraction}')
        self._fraction = fraction

    def count(self, length: int) -> int:
        """Returns the number of values that will result if the slice is applied to a sequence of given length."""
        if length <= self._fraction:
            return length
        return self._fraction

    def range(self, length: int) -> range:
        """Returns a builtin range object for the sequence of the given length."""
        # return range(0, length, int(0.5 + length / self.count(length)))
        step = length / self.count(length)
        if int(step) != step:
            step += 1
        return range(0, length, int(step))

    def indices(self, length: int) -> typing.List[int]:
        """Returns a fully composed list of indices for the sequence of the given length."""
        return list(self.range(length))

    def __eq__(self, other) -> bool:
        """Mostly used for testing."""
        if other.__class__ == self.__class__:
            return other._fraction == self._fraction
        return NotImplemented

    def long_str(self, length: int) -> str:
        rng = self.range(length)
        return f'<Split on length={length} start={rng.start} stop={rng.stop} step={rng.step}>'

    def __str__(self) -> str:
        return f'<Split fraction: {self._fraction}>'


def create_slice_or_split(slice_string: str) -> typing.Union[Slice, Split]:
    """Returns a Slice object from a string such as:
    '', 'None,72', 'None,72,14'
    """
    def convert(a_string):
        if a_string in ('None', ''):
            return None
        # May raise a ValueError
        return int(a_string)

    if '/' in slice_string:
        parts = [convert(p.strip()) for p in slice_string.split('/')]
        if len(parts) != 2:
            raise ValueError(f'Wrong number of parts for a Split in "{slice_string}"')
        if parts[0] is None or parts[0] != 1:
            raise ValueError(f'A Split must start with 1 not {parts[0]} in "{slice_string}"')
        if parts[1] is None or parts[1] < 1:
            raise ValueError(f'A Split must end with and integer >= 1 not {parts[1]} in "{slice_string}"')
        return Split(parts[1])
    else:
        parts = [convert(p.strip()) for p in slice_string.split(',')]
        if len(parts) > 3:
            raise ValueError(f'Too many parts in "{slice_string}"')
        if len(parts) == 0:
            return Slice()
        if len(parts) == 1:
            return Slice(stop=parts[0])
        # 2 or 3 parts
        return Slice(*parts)


def add_frame_slice_to_argument_parser(parser: argparse.ArgumentParser, help_prefix: str='', use_what: bool = False) -> None:
    help_list = []
    if help_prefix:
        help_list.append(f'{help_prefix}')
    help_list.extend(
        [
            'Do not process all frames but split or slice the frames.',
            'Split is of the form "1/N" so a maximum of N frames will be processed.',
            'N must be +ve, non-zero integer.',
            'Example: "1/64" - process a maximum of 64 frames.',
            'Slice the frames is of the form start,stop,step as a comma separated list.',
            'Values can be absent or  "None".',
            'Examples: ",," - every frame,',
            '",,2" - every other frame,',
            '",10," - frames 0 to 9,',
            '"4,10,2" - frames 4, 6, 8,',
            '"40,-1,4" - every fourth frame from 40 to the end.',
            'Results will be truncated by frame array length.',
        ]
    )
    if use_what:
        help_list.append(' Use \'?\' to see what frames are available')
    help_list.append(' [default: "%(default)s"]')
    parser.add_argument('--frame-slice', default=',,', type=str, help=' '.join(help_list))
