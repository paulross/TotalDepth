"""
Interprets Latitude and Longitude.
"""
import dataclasses
import math
import re
import typing


@dataclasses.dataclass
class LatitudeLongitude:
    """Represents a Latitude or Longitude internally in radians."""
    value_rad: float

    def radians(self) -> float:
        """Value in radians."""
        return self.value_rad

    def degrees(self) -> float:
        """Value in degrees."""
        return math.degrees(self.value_rad)

    def dms(self) -> str:
        """Returns the degrees, minutes, seconds as a string pre-pended with '+' or '-'."""
        v = math.degrees(abs(self.value_rad))
        if self.value_rad < 0.0:
            d = -int(v)
        else:
            d = int(v)
        v -= d
        v *= 60.0
        m = int(v)
        v -= m
        v *= 60.0
        s = v
        return f'{+d} {m}\' {s:.0f}\"'


    def dm(self) -> str:
        """Returns the degrees, minutes as a string pre-pended with '+' or '-'."""
        v = math.degrees(abs(self.value_rad))
        if self.value_rad < 0.0:
            d = -int(v)
        else:
            d = int(v)
        v -= d
        v *= 60.0
        m = float(v)
        return f'{+d} {m:.3f}\''


@dataclasses.dataclass
class Latitude(LatitudeLongitude):
    """Represents a Latitude internally in radians."""

    def __post_init__(self):
        if self.value_rad > math.pi / 2 or self.value_rad < -math.pi / 2:
            raise OverflowError(f'Latitude {self.value_rad} out of range.')

    def dms(self) -> str:
        return f'{super().dms()[1:]} {"N" if self.value_rad >= 0.0 else "S"}'


@dataclasses.dataclass
class Longitude(LatitudeLongitude):
    """Represents a Longitude internally in radians."""

    def __post_init__(self):
        if self.value_rad > math.pi or self.value_rad < -math.pi:
            raise OverflowError(f'Longitude {self.value_rad} out of range.')

    def dms(self) -> str:
        return f'{super().dms()[1:]} {"E" if self.value_rad >= 0.0 else "W"}'


# Regular expressions for Latitude and Longitude

# Matches: Latitude `52 22' 26.8" N`
RE_DMS_NS = re.compile(r'''\s*(\d+)\s+(\d+)'?\s+([0-9.]+)"?\s*([NS])\s*''')
# Matches: Longitude `52 22' 26.8" E`
RE_DMS_EW = re.compile(r'''\s*(\d+)\s+(\d+)'?\s+([0-9.]+)"?\s*([EW])\s*''')
# Matches: `21 23 06.314`, `-21 23 06.314`. '21 23 06.314` assumed positive.
RE_DMS = re.compile(r'''\s*([+-])?\s*(\d+)\s+(\d+)'?\s+([0-9.]+)"?\s*''')
# Matches: Latitude `52 26.8' N`
RE_DM_NS = re.compile(r'''\s*(\d+)\s+([0-9.]+)'?\s*([NS])\s*''')
# Matches: Longitude `52 26.8' E`
RE_DM_EW = re.compile(r'''\s*(\d+)\s+([0-9.]+)'?\s*([EW])\s*''')
# Matches: `-21 06.314`
RE_DM = re.compile(r'''\s*([+-])?\s*(\d+)\s+([0-9.]+)'?\s*''')
# Matches: `21.314`
RE_DECIMAL_DEGREES = re.compile(r'''\s*([+-])?\s*([0-9.]+)\s*''')


def _parse_str_for_latitude_longitude(s: str,
                                      cls: typing.Type[typing.Union[Latitude, Longitude]],
                                      pos_char: str,
                                      neg_char: str) -> typing.Union[Latitude, Longitude]:
    """Takes a string and tries to interpret it as degrees Latitude or Longitude.
    May raise a ValueError if no parsing strategy works or an OverflowError if value out of range."""
    if pos_char not in {'N', 'E'}:
        raise ValueError(f'pos_char "{pos_char}" not "N" or "E"')
    if neg_char not in {'S', 'W'}:
        raise ValueError(f'neg_char "{neg_char}" not "S" or "W"')
    m = RE_DMS_NS.match(s)
    if m is not None:
        deg = int(m.group(1)) + int(m.group(2)) / 60 + float(m.group(3)) / 3600
        if m.group(4) is not None:
            if m.group(4) == pos_char:
                return cls(math.radians(deg))
            elif m.group(4) == neg_char:
                return cls(math.radians(-deg))
            else:
                raise ValueError(
                    f'Latitude string "{s}" has an illegal {m.group(4)}'
                    f' character that does not match +ve: "{pos_char}" -ve: "{neg_char}"'
                )
    m = RE_DMS.match(s)
    if m is not None:
        deg = int(m.group(2)) + int(m.group(3)) / 60 + float(m.group(4)) / 3600
        if m.group(1) is not None and m.group(1) == '-':
            deg = -deg
        return cls(math.radians(deg))
    m = RE_DM_NS.match(s)
    if m is not None:
        deg = int(m.group(1)) + float(m.group(2)) / 60
        if m.group(3) is not None:
            if m.group(3) == 'N':
                return cls(math.radians(deg))
            elif m.group(3) == 'S':
                return cls(math.radians(-deg))
            else:
                raise ValueError(f'String "{s}" has an illegal {m.group(3)} character.')
    m = RE_DM.match(s)
    if m is not None:
        deg = int(m.group(2)) + float(m.group(3)) / 60
        if m.group(1) is not None and m.group(1) == '-':
            deg = -deg
        return cls(math.radians(deg))
    m = RE_DECIMAL_DEGREES.match(s)
    if m is not None:
        deg = float(m.group(2))
        if m.group(1) is not None and m.group(1) == '-':
            deg = -deg
        return cls(math.radians(deg))
    raise ValueError(f'Can not parse "{s}" for a {cls}.')


def parse_str_for_latitude(s: str) -> Latitude:
    """Takes a string and tries to interpret it as degrees Latitude.
    May raise a ValueError if no parsing strategy works or an OverflowError if value out of range."""
    return _parse_str_for_latitude_longitude(s, Latitude, 'N', 'S')


def parse_str_for_longitude(s: str) -> Longitude:
    """Takes a string and tries to interpret it as degrees Longitude.
    May raise a ValueError if no parsing strategy works or an OverflowError if value out of range."""
    return _parse_str_for_latitude_longitude(s, Longitude, 'E', 'W')
