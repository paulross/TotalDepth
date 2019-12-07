import collections
import math
import typing


class LengthDict:
    """Provides statistics about a summary of lengths such as file lengths or logical data lengths."""
    def __init__(self):
        self._count = collections.defaultdict(int)

    def __len__(self) -> int:
        """Number of distinct length  entries."""
        return len(self._count)

    def __getitem__(self, item) -> int:
        """Returns the count of a particular length. Does not write to the dict."""
        if item in self._count:
            return self._count[item]
        raise KeyError(item)

    @property
    def min(self) -> int:
        """Minimum length."""
        return min(self._count.keys())

    @property
    def max(self) -> int:
        """Maximum length."""
        return max(self._count.keys())

    @property
    def count(self) -> int:
        """Return the total number of entries."""
        return sum(self._count.values())

    @property
    def zero_count(self) -> int:
        """Return the number of length zero."""
        return self._count[0]

    def keys(self) -> typing.KeysView[int]:
        """Return the keys (lengths seen)."""
        return self._count.keys()

    def add(self, length: int):
        """Add a length to the summary."""
        if length < 0:
            raise ValueError(f'Length must be >= 0 not {length}')
        self._count[length] += 1

    def reduced_power_2(self) -> typing.DefaultDict[int, int]:
        """Return a histogram with keys reduced to power of 2."""
        ret = collections.defaultdict(int)
        for k in self._count:
            if k > 0:
                ret[int(math.log2(k))] += self._count[k]
        return ret

    def histogram_power_of_2(self, width: int = 40, bar_char: str = '+') -> typing.List[str]:
        """Return the count of zero and a histogram of strings of the lengths to power of 2."""
        ret = []
        if len(self._count):
            reduced = self.reduced_power_2()
            rng = range(min(reduced.keys()), max(reduced.keys()) + 1, 1)
            max_count = max(reduced.values())
            # TODO: Calculate field widths based on max power of 2 and max count for any value in reduced.
            for r in rng:
                if r in reduced:
                    proportion = (reduced[r] / max_count)
                else:
                    proportion = 0.0
                bar = bar_char * int(0.5 + width * proportion)
                size = f'>=2**{r}'
                ret.append(f'{size:7} [{reduced[r]:6,d}] | {bar}')
        return ret
