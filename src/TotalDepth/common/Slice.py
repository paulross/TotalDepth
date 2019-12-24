import abc
import argparse
import typing

# from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
#
#
# class ExceptionSlice(ExceptionTotalDepthRP66V1):
#     """Specialisation of an exception for SLice objects."""
#     pass
#
#
# class ExceptionSample(ExceptionTotalDepthRP66V1):
#     """Specialisation of an exception for Sample objects."""
#     pass


class SliceABC(abc.ABC):

    @abc.abstractmethod
    def first(self, length: int) -> int:
        """The index of the first element of a sequence of length."""
        pass

    @abc.abstractmethod
    def last(self, length: int) -> int:
        """The index of the last element of a sequence of length."""
        pass

    @abc.abstractmethod
    def step(self, length: int) -> int:
        """The sequence of length step."""
        pass

    @abc.abstractmethod
    def count(self, length: int) -> int:
        """Returns the number of values that will result if the slice is applied to a sequence of given length."""
        pass

    @abc.abstractmethod
    def gen_indices(self, length: int) -> range:
        """Generates the indices for the sequence of the given length."""
        pass

    @abc.abstractmethod
    def indices(self, length: int) -> typing.List[int]:
        """Returns a fully composed list of indices for the sequence of the given length."""
        pass

    @abc.abstractmethod
    def __eq__(self, other) -> bool:
        """Mostly used for testing."""
        pass

    @abc.abstractmethod
    def long_str(self, length: int) -> str:
        """Return a long string."""
        pass

    @abc.abstractmethod
    def __str__(self) -> str:
        pass


class Slice(SliceABC):
    """Class that wraps a builtin slice object for integers and provides some useful APIs.
    NOTE: The builtin slice object can take non-integer values but raises later, for example::

        slice(1, 4, 2.0).indices(45)
    """
    def __init__(self,
                 start: typing.Union[None, int] = None,
                 stop: typing.Union[None, int] = None,
                 step: typing.Union[None, int] = None):
        super().__init__()
        # Fail fast, unlike the builtin slice
        for name in ('start', 'stop', 'step'):
            if not isinstance(locals()[name], (type(None), int)):
                raise TypeError(f'{name} must be None or an integer not {type(locals()[name])}')
        self._slice = slice(start, stop, step)

    def first(self, length: int) -> int:
        """The index of the first element of a sequence of length."""
        return self._slice.indices(length)[0]

    def last(self, length: int) -> int:
        """The index of the last element of a sequence of length."""
        indices = self._slice.indices(length)
        if length < indices[1]:
            return length - 1
        return indices[2] * (indices[1] // indices[2]) - 1

    def step(self, length: int) -> int:
        """The sequence of length step."""
        return self._slice.indices(length)[2]

    def count(self, length: int) -> int:
        """Returns the number of values that will result if the slice is applied to a sequence of given length."""
        return len(list(self.gen_indices(length)))

    def gen_indices(self, length: int) -> range:
        """Generates the indices for the sequence of the given length."""
        yield from range(*self._slice.indices(length))

    def indices(self, length: int) -> typing.List[int]:
        """Returns a fully composed list of indices for the sequence of the given length."""
        return list(self.gen_indices(length))

    def __eq__(self, other) -> bool:
        """Mostly used for testing."""
        if other.__class__ == self.__class__:
            return other._slice == self._slice
        return NotImplemented

    def long_str(self, length: int) -> str:
        rng = range(*self._slice.indices(length))
        return f'<Slice on length={length} start={rng.start} stop={rng.stop} step={rng.step}>'

    def __str__(self) -> str:
        return f'<Slice.{str(self._slice)}>'


class Sample(SliceABC):
    """This has the same API as Slice but takes a single integer.

    NOTE: This may not p[roduce a regular sequence. For example sampling 7 items out  of a 12 element list has the
    indices [0, 1, 3, 5, 6, 8, 10]
    """
    def __init__(self, sample_size: int):
        if sample_size < 1:
            raise ValueError(f'A Sample must be an integer >= 1 not {sample_size}')
        self._sample_size = sample_size

    def first(self, length) -> int:
        """The index of the first element of a sequence of length."""
        return 0

    def last(self, length) -> int:
        """The index of the last element of a sequence of length."""
        if self._sample_size >= length:
            return length - 1
        return length - self._sample_size

    def step(self, length) -> int:
        """The sequence of length step."""
        if self._sample_size >= length:
            return 1
        return length // self._sample_size

    def count(self, length: int) -> int:
        """Returns the number of values that will result if the slice is applied to a sequence of given length."""
        if length <= self._sample_size:
            return length
        return self._sample_size

    def gen_indices(self, length: int) -> range:
        """Generates the indices for the sequence of the given length."""
        if self._sample_size >= length:
            yield from range(length)
        else:
            assert self._sample_size > 0
            int_incr = length // self._sample_size
            rem_incr = length % self._sample_size
            index = remainder = 0
            while index < length:
                yield index
                remainder += rem_incr
                index += int_incr + remainder // self._sample_size
                remainder %= self._sample_size

    def indices(self, length: int) -> typing.List[int]:
        """Returns a fully composed list of indices for the sequence of the given length."""
        return list(self.gen_indices(length))

    def __eq__(self, other) -> bool:
        """Mostly used for testing."""
        if other.__class__ == self.__class__:
            return other._sample_size == self._sample_size
        return NotImplemented

    def long_str(self, length: int) -> str:
        """Long descriptive string."""
        sample_size = min(self._sample_size, length)
        return f'<Sample {sample_size} out of {length}>'

    def __str__(self) -> str:
        return f'<Sample fraction: {self._sample_size}>'


def create_slice_or_sample(slice_string: str) -> typing.Union[Slice, Sample]:
    """Returns a Slice object from a string such as:
    '', 'None,72', 'None,72,14'
    """
    def convert(a_string):
        if a_string in ('None', ''):
            return None
        # May raise a ValueError
        return int(a_string)

    if ',' in slice_string:
        # Return a Slice
        parts = [convert(p.strip()) for p in slice_string.split(',')]
        if len(parts) != 3:
            raise ValueError(f'Wrong number of parts for a Slice in "{slice_string}"')
        # 2 or 3 parts
        return Slice(*parts)
    else:
        return Sample(int(slice_string))


def add_frame_slice_to_argument_parser(parser: argparse.ArgumentParser,
                                       help_prefix: str = '', use_what: bool = False) -> None:
    help_list = []
    if help_prefix:
        help_list.append(f'{help_prefix}')
    help_list.extend(
        [
            'Do not process all frames but sample or slice the frames.',
            'SAMPLE: Sample is of the form "N" so a maximum of N frames, roughly regularly spaced, will be processed.',
            'N must be +ve, non-zero integer.',
            'Example: "64" - process a maximum of 64 frames.',
            'SLICE: Slice the frames is of the form start,stop,step as a comma separated list.',
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
    help_list.append(' [default: "%(default)s" i.e. all frames]')
    parser.add_argument('--frame-slice', default=',,', type=str, help=' '.join(help_list))
