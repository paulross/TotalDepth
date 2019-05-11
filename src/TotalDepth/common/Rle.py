"""
Code for RUn Length Encoding.
"""
import math
import sys
import typing


class RLEItem:
    """Class that represents a single entry in a Run Length Encoding set. v - The datum value."""
    def __init__(self, datum: typing.Union[int, float]):
        self.datum: typing.Union[int, float] = datum
        self.stride: typing.Union[int, float] = 0
        self.repeat: int = 0

    def __str__(self) -> str:
        """String representation."""
        return f'<RLEItem: datum={self.datum!s:} stride={self.stride!s:} repeat={self.repeat!s:}>'

    def __len__(self) -> int:
        """Total number of values."""
        return self.repeat + 1

    def add(self, v: typing.Union[int, float]) -> bool:
        """
        Returns True if v has been absorbed in this entry. False means a new entry is required.
        """
        if self.repeat == 0:
            self.stride = v - self.datum
            self.repeat = 1
            return True
        exp_value = self.datum + (self.stride * (self.repeat + 1))
        if isinstance(v, float):
            if math.isclose(v, exp_value, rel_tol=sys.float_info.epsilon):
                # TODO: Recompute stride?
                self.repeat += 1
                return True
        else:
            if v == exp_value:
                self.repeat += 1
                return True
        return False

    def values(self) -> typing.Sequence[typing.Union[int, float]]:
        """Generates all values."""
        v = self.datum
        yield v
        for i in range(self.repeat):
            assert self.stride != 0
            v += self.stride
            yield v

    def value(self, i) -> typing.Tuple[int, typing.Union[int, float, None]]:
        """Returns a particular value."""
        if i >= 0:
            if i > self.repeat:
                # Overrun
                return i - self.repeat - 1, None
            if self.repeat == 0:
                return i, self.datum
            return i, self.datum + i * self.stride
        # Indexing from end
        if -i > self.repeat + 1:
            return i + self.repeat + 1, None
        return i, self.datum + (self.repeat + i + 1) * self.stride

    def range(self) -> range:
        """
        Returns a range object that has (start, stop, step).
        """
        if self.repeat == 0:
            return range(self.datum, self.datum + 1, 1)
        return range(self.datum, self.datum + (self.stride * (self.repeat + 1)), self.stride)

    def last(self):
        """Returns the last value."""
        if self.repeat == 0:
            return self.datum
        return self.datum + (self.stride * self.repeat)

    def largest_le(self, value: typing.Union[int, float]) -> typing.Union[int, float]:
        if self.datum > value:
            raise ValueError(f'RLEItem.largest_le(): datum {self.datum} > value {value}')
        last = self.last()
        if value > last:
            return last
        index = int((value - self.datum) // self.stride)
        ret = self.datum + self.stride * index
        return ret


class RLE:
    """Class that represents Run Length Encoding.

    theFunc - optional unary function to convert all values with.
    """
    def __init__(self, theFunc=None):
        """Constructor, optionally takes a unary function to convert all values with."""
        # List of RLEItem
        self.rle_items: typing.List[RLEItem] = []
        self.function: typing.Union[typing.Callable] = theFunc

    def __str__(self):
        return '<RLE: func={:s}: '.format(str(self.function)) \
               + '[' + ', '.join([str(r) for r in self.rle_items]) + ']>'

    def __len__(self):
        """The number of RLEItem(s)."""
        return len(self.rle_items)

    def __getitem__(self, key):
        """Returns a RLEItem."""
        return self.rle_items[key]

    def num_values(self):
        """Total number of record values."""
        return sum([len(r) for r in self.rle_items])

    def add(self, v):
        """Adds a value to this RLE object."""
        if self.function is not None:
            v = self.function(v)
        # NOTE: Side effect in second test
        if len(self.rle_items) == 0 or not self.rle_items[-1].add(v):
            self.rle_items.append(RLEItem(v))

    def values(self):
        """Generates all values entered."""
        for r in self.rle_items:
            for v in r.values():
                yield v

    def value(self, i):
        """Indexing; this returns the i'th value added."""
        if i >= 0:
            for r in self.rle_items:
                i, v = r.value(i)
                if v is not None:
                    return v
        else:
            for r in reversed(self.rle_items):
                i, v = r.value(i)
                if v is not None:
                    return v
        raise IndexError('list index out of range')

    def ranges(self):
        """Returns a list of range() objects."""
        return [i.range() for i in self.rle_items]

    def first(self):
        """Returns the first value or None if no values added."""
        if len(self.rle_items) > 0:
            return self.rle_items[0].datum

    def last(self):
        """Returns the last value or None if no values added."""
        if len(self.rle_items) > 0:
            return self.rle_items[-1].last()

    def largest_le(self, value: typing.Union[int, float]) -> typing.Union[int, float]:
        """Return the largest value less than or equal to the given value.
        """
        # This is essentially bisect_right.
        lo = 0
        hi = len(self)
        while lo < hi:
            mid = (lo + hi) // 2
            if value < self.rle_items[mid].datum:
                hi = mid
            else:
                lo = mid + 1
        if lo:
            return self.rle_items[lo-1].largest_le(value)
        raise ValueError(f'Can not find largest_le for value {value}')


def create_rle(values: typing.Iterable, fn: typing.Callable = None) -> RLE:
    """Create a RLE object from an iterable."""
    ret = RLE(fn)
    for v in values:
        ret.add(v)
    return ret
