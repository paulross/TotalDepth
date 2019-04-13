"""
Code for RUn Length Encoding.
"""
import typing


class RLEItem:
    """Class that represents a single entry in a Run Length Encoding set. v - The datum value."""
    def __init__(self, v):
        #print('RLEItem.__init__({:d})'.format(v))
        self._datum = v
        self._stride = None
        self._repeat = 0

    def __str__(self):
        """String representation."""
        return 'RLEItem: ' + self._propStr()

    def _propStr(self):
        return 'datum={:s} stride={:s} repeat={:s}'.format(
            str(self.datum),
            str(self.stride),
            str(self.repeat),
        )

    @property
    def datum(self):
        """The initial datum value."""
        return self._datum

    @property
    def stride(self):
        """The stride as a number or None if there is only one entry."""
        return self._stride

    @property
    def repeat(self):
        """The repeat count."""
        return self._repeat

    def numValues(self):
        """Total number of record values."""
        return self._repeat + 1

    def add(self, v):
        """Returns True if v has been absorbed in this entry. False means a
        new entry is required."""
        if self._stride is None:
            assert(self._repeat == 0)
            self._stride = v - self._datum
            self._repeat = 1
            return True
        expVal = self._datum + (self._stride * (self._repeat + 1))
        if v == expVal:
            self._repeat += 1
            return True
        return False

    def values(self):
        """Generates all values."""
        v = self._datum
        yield v
        for i in range(self._repeat):
            assert(self._stride is not None)
            v += self._stride
            yield v

    def value(self, i):
        """Returns a particular value."""
        if i >= 0:
            if i > self._repeat:
                return i - self._repeat - 1, None
            if self._stride is None:
                return i, self._datum
            return i, self._datum + i * self._stride
        # Indexing from end
        if -i > self._repeat + 1:
            return i + self._repeat + 1, None
        #if self._stride is None:
        #    return i, self._datum
        return i, self._datum + (self._repeat + i + 1) * self._stride

    def range(self):
        """Returns a range object that has (start, stop, step) or None if a single entry."""
        if self._stride is None:
            return range(self._datum, self._datum+1, 1)
        return range(self._datum, self._datum + (self._stride * (self._repeat + 1)), self._stride)

    def first(self):
        """Returns the first value."""
        return self._datum

    def last(self):
        """Returns the last value."""
        if self._stride is None:
            return self._datum
        return self._datum + (self._stride * self._repeat)


class RLE:
    """Class that represents Run Length Encoding.

    theFunc - optional unary function to convert all values with.
    """
    def __init__(self, theFunc=None):
        """Constructor, optionally takes a unary function to convert all values with."""
        # List of RLEItem
        self._rleS: typing.Sequence[RLEItem] = []
        self._func: typing.Union[None, typing.Callable] = theFunc

    def __str__(self):
        """String representation."""
        #return 'RLE: func={:s}\n  '.format(str(self._func)) \
        #    + '\n  '.join([str(r) for r in self._rleS])
        return 'RLE: func={:s}\n  '.format(str(self._func)) \
            + '[' + ', '.join([str(r) for r in self._rleS]) + ']'

    def __len__(self):
        """The number of RLEItem(s)."""
        return len(self._rleS)

    def __getitem__(self, key):
        """Returns a RLEItem."""
        return self._rleS[key]

    @property
    def count(self) -> int:
        count = 0
        for r in self._rleS:
            count += r.numValues()
        return count

    def numValues(self):
        """Total number of record values."""
        return sum([r.numValues() for r in self._rleS])

    def add(self, v):
        """Adds a value to this RLE object."""
        if self._func is not None:
            v = self._func(v)
        # NOTE: Side effect in second test
        if len(self._rleS) == 0 \
        or not self._rleS[-1].add(v):
            self._rleS.append(RLEItem(v))

    def values(self):
        """Generates all values entered."""
        for r in self._rleS:
            for v in r.values():
                yield v

    def value(self, i):
        """Indexing; this returns the i'th value added."""
        if i >= 0:
            for r in self._rleS:
                i, v = r.value(i)
                if v is not None:
                    return v
        else:
            for r in reversed(self._rleS):
                i, v = r.value(i)
                if v is not None:
                    return v
        raise IndexError('list index out of range')

    def rangeList(self):
        """Returns a list of range() objects."""
        return [i.range() for i in self._rleS]

    def first(self):
        """Returns the first value or None if no values added."""
        if len(self._rleS) > 0:
            return self._rleS[0].first()

    def last(self):
        """Returns the last value or None if no values added."""
        if len(self._rleS) > 0:
            return self._rleS[-1].last()
