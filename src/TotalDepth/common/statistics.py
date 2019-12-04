import collections
import math
import typing


class LengthDict:
    """Provides statistics about a summary of lengths such as file lengths or logical data lengths."""
    def __init__(self):
        self._count = collections.defaultdict(int)
        self._zero_count = 0

    @property
    def count(self) -> int:
        """Return the total number of entries."""
        return self._zero_count + sum(self._count.values())

    @property
    def zero_count(self) -> int:
        """Return the number of length zero."""
        return self._zero_count

    def add(self, length: int):
        """Add a length to the summary."""
        if length < 0:
            raise ValueError(f'Length must be >= 0 not {length}')
        if length:
            self._count[length] += 1
        else:
            self._zero_count += 1

    def reduced_power_2(self) -> typing.DefaultDict[int, int]:
        """Return a histogram with keys reduced to power of 2."""
        ret = collections.defaultdict(int)
        for k in self._count:
            assert k
            ret[int(math.log2(k))] += self._count[k]
        return ret

    def histogram_power_of_2(self, width: int = 40, bar_char: str = '+') -> typing.Tuple[int, typing.List[str]]:
        """Return the count of zero and a histogram of strings of the lengths to power of 2."""
        ret = []
        if len(self._count):
            reduced = self.reduced_power_2()
            rng = range(min(reduced.keys()), max(reduced.keys()) + 1, 1)
            # TODO: Calculate field widths based on max power of 2 and max count for any value in reduced.
            for r in rng:
                if r in reduced:
                    proportion = (reduced[r] / self.count)
                else:
                    proportion = 0.0
                bar = bar_char * int(0.5 + width * proportion)
                size = f'>=2**{r}'
                ret.append(f'{size:7} [{reduced[r]:6,d}] | {bar}')
        return self._zero_count, ret
