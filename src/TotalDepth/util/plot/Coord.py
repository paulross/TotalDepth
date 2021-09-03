#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation.
# Copyright (C) 2011-2021 Paul Ross
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Paul Ross: apaulross@gmail.com
"""Provides a fairly basic two dimensional coordinate system.
"""

__author__  = 'Paul Ross'
__date__    = '2009-09-25'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'

#import logging
#import sys
import collections
import math
import typing

from TotalDepth.LIS import ExceptionTotalDepthLIS


class ExceptionCoord(ExceptionTotalDepthLIS):
    """Exception class for representing Coordinates."""
    pass


class ExceptionCoordUnitConvert(ExceptionCoord):
    """Exception raised when converting units."""
    pass


#: Base units for dimensions
BASE_UNITS = 'px'


#: Map of {unit name : conversion factor to base units, ...}
UNIT_MAP = {
    None        : 1.0,  # Implied base units i.e. default
    'px'        : 1.0,
    'pt'        : 1.0,  # Actual base units i.e. BASE_UNITS
    'pc'        : 12.0,
    'in'        : 72.0,
    'cm'        : 72.0/2.54,
    'mm'        : 72.0/25.4,
}


def exactConversion(units_a, units_b=BASE_UNITS):
    """Returns True it the two dimension can be converted exactly.
    This is the case where the units are the same or the factors are exact
    multiples."""
    factor_a = UNIT_MAP[units_a]
    factor_b = UNIT_MAP[units_b]
    if factor_a >= factor_b:
        return factor_a / factor_b == factor_a // factor_b
    return factor_b / factor_a == factor_b // factor_a


#: Formatting strings for writing attributes.
#: We are trying not to write 3.999999999mm here!
UNIT_MAP_DEFAULT_FORMAT = {
    None        : '%.4f', # Implied base units i.e. m
    'px'        : '%d',
    'pt'        : '%d',
    'pc'        : '%.2f',
    'cm'        : '%.2f',
    'mm'        : '%.1f',
    'in'        : '%.3f',
    # Non-SVG units.
    'm'         : '%.4f', # Actual base units i.e. BASE_UNITS
    'ft'        : '%.4f', # Feet
    'NM'        : '%.6f', # Nautical miles.
}

#: Map of formatting strings for value and units e.g. to create '0.667in' from (2.0 / 3.0, 'in')
UNIT_MAP_DEFAULT_FORMAT_WITH_UNITS = {__k : UNIT_MAP_DEFAULT_FORMAT[__k] + '%s' for __k in UNIT_MAP_DEFAULT_FORMAT}


def units():
    """Returns the unsorted list of acceptable units."""
    return UNIT_MAP.keys()


def convert(val, unitFrom, unitTo):
    """Convert a value from one set of units to another."""
    if unitFrom == unitTo:
        return val
    try:
        return val * UNIT_MAP[unitFrom] / UNIT_MAP[unitTo]
    except KeyError:
        if unitFrom not in UNIT_MAP:
            raise ExceptionCoordUnitConvert('Unsupported units %s' % unitTo)
        raise ExceptionCoordUnitConvert('Unsupported units %s' % unitFrom)


class Dim(collections.namedtuple('Dim', 'value units',)):
    """Represents a dimension as an engineering value i.e. a number and units.""" 
    __slots__ = ()

    def scale(self, factor):
        """Returns a new Dim() multiplied by a factor, units are unchanged."""
        return self._replace(value=self.value*factor)

    def divide(self, factor):
        """Returns a new Dim() divided by a factor, units are unchanged."""
        return self._replace(value=self.value/factor)

    def convert(self, u):
        """Returns a new Dim() with units changed and value converted."""
        return self._replace(value=convert(self.value, self.units, u), units=u)

    def __str__(self):
        #return 'Dim: %s (%s)' % (self.value, self.units)
        return 'Dim(%s%s)' % (self.value, self.units)

    def __repr__(self):
        return 'Dim({}, \'{}\')'.format(self.value, self.units)

    def __format__(self, format_spec):
        fmt = '{:' + format_spec + '}{:s}'
        return fmt.format(self.value, self.units)

    def __add__(self, other):
        """Overload self+other, returned result has the sum of self and other.
        The units chosen are self's unless self's units are None in which case other's
        units are used (if not None)."""
        if self.units is None and other.units is not None:
            myVal = other.value + convert(self.value, self.units, other.units)
            return Dim(myVal, other.units)
        else:
            myVal = self.value + convert(other.value, other.units, self.units)
            return Dim(myVal, self.units)

    def __sub__(self, other):
        """Overload self-other, returned result has the difference of self and
        other. The units chosen are self's unless self's units are None in
        which case other's units are used (if not None)."""
        if self.units is None and other.units is not None:
            myVal = convert(self.value, self.units, other.units) - other.value
            return Dim(myVal, other.units)
        else:
            myVal = self.value - convert(other.value, other.units, self.units)
            return Dim(myVal, self.units)

    def __iadd__(self, other):
        """Addition in place, value of other is converted to my units and added."""
        # Use __add__()
        self = self + other
        return self

    def __isub__(self, other):
        """Subtraction in place, value of other is subtracted."""
        # Use __sub__()
        self = self - other
        return self

    def __mul__(self, other):
        """Multiply by a factor that is a number."""
        return self.scale(other)

    def __truediv__(self, other):
        """Divide by a factor that is a number."""
        return self.scale(1.0 / other)

    def __imul__(self, other):
        """Indirect multiply by a factor that is a number."""
        # Use __mul__()
        self = self * other
        return self

    def __itruediv__(self, other):
        """Indirect divide by a factor that is a number."""
        # Use __div__()
        self = self / other
        return self

    def __pow__(self, other):
        return self._replace(value=self.value ** other)

    def __ipow__(self, other):
        # Use __pow__()
        self = self**other
        return self

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            if self.units == other.units:
                return self.value < other.value
            return self.value < convert(other.value, other.units, self.units)
        else:
            return NotImplemented

    def __le__(self, other):
        if self.__class__ == other.__class__:
            if self.units == other.units:
                return self.value <= other.value
            return self.value <= convert(other.value, other.units, self.units)
        else:
            return NotImplemented

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            if self.units == other.units:
                return self.value == other.value
            return (self.value == convert(other.value, other.units, self.units))
        else:
            return NotImplemented

    def __ne__(self, other):
        if self.__class__ == other.__class__:
            if self.units == other.units:
                return self.value != other.value
            return (self.value != convert(other.value, other.units, self.units))
        else:
            return NotImplemented

    def __gt__(self, other):
        if self.__class__ == other.__class__:
            if self.units == other.units:
                return self.value > other.value
            return self.value > convert(other.value, other.units, self.units)
        else:
            return NotImplemented

    def __ge__(self, other):
        if self.__class__ == other.__class__:
            if self.units == other.units:
                return self.value >= other.value
            return self.value >= convert(other.value, other.units, self.units)
        else:
            return NotImplemented


def dimIn(v):
    """Returns a Dim object with the value in inches."""
    return Dim(v, 'in')

# All of these take a Dim() for each member
#
# This describes the size of a box, its members are Dim() objects
#Box         = collections.namedtuple('Box', 'width depth',)
# Padding around another object that forms the Bounding Box
# All 4 attributes are Dim() objects
#Pad         = collections.namedtuple('Pad', 'prev next parent child',)


class Box(collections.namedtuple('Box', 'width depth', )):
    __slots__ = ()

    def __str__(self):
        return 'Box(width={!s:s}, depth={!s:s})'.format(self.width, self.depth)

    def __repr__(self):
        return 'Box(width={!r:s}, depth={!r:s})'.format(self.width, self.depth)

    def __format__(self, format_spec):
        return 'Box(width={:s}, depth={:s})'.format(
            format_spec.format(self.width), format_spec.format(self.depth)
        )


class Pad(collections.namedtuple('Pad', 'prev next parent child', )):
    """Padding around another object that forms the Bounding Box.
    All 4 attributes are Dim() objects"""
    __slots__ = ()

    def __str__(self):
        return 'Pad(prev={!s:s}, next={!s:s}, parent={!s:s}, child={!s:s})'.format(
            self.prev, self.next, self.parent, self.child
        )

    def __repr__(self):
        return 'Pad(prev={!r:s}, next={!r:s}, parent={!r:s}, child={!r:s})'.format(
            self.prev, self.next, self.parent, self.child
        )

    def __format__(self, format_spec):
        return 'Pad(prev={:s}, next={:s}, parent={:s}, child={:s})'.format(
            format_spec.format(self.prev),
            format_spec.format(self.next),
            format_spec.format(self.parent),
            format_spec.format(self.child),
        )


class Margin(collections.namedtuple('Margin', 'left right top bottom',)):
    """Margin padding around another object. All 4 attributes are Coord.Dim()
    objects."""
    __slots__ = ()

    def __str__(self):
        return 'Margin(left=%s, right=%s, top=%s, bottom=%s)' \
            % (self.left, self.right, self.top, self.bottom)

    def __repr__(self):
        return 'Margin(left={!r:s}, right={!r:s}, top={!r:s}, bottom={!r:s})'.format(
            self.left, self.right, self.top, self.bottom
        )

    def __format__(self, format_spec):
        return 'Margin(left={!r:s}, right={!r:s}, top={!r:s}, bottom={!r:s})'.format(
            format_spec.format(self.left),
            format_spec.format(self.right),
            format_spec.format(self.top),
            format_spec.format(self.bottom),
        )


class Pt(collections.namedtuple('Pt', 'x y', )):
    """A point, an absolute x/y position on the plot area.
    Members are Coord.Dim()."""
    __slots__ = ()

    def __eq__(self, other):
        """Comparison."""
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return 'Pt(x={!s:s}, y={!s:s})'.format(self.x, self.y)

    def __repr__(self):
        return 'Pt(x={!r:s}, y={!r:s})'.format(self.x, self.y)

    def __format__(self, format_spec):
        return 'Pt(x={:s}, y={:s})'.format(
            format_spec.format(self.x), format_spec.format(self.y)
        )

    def convert(self, u):
        """Returns a new Pt() with units changed and value converted."""
        return self._replace(x=self.x.convert(u), y=self.y.convert(u))

    def scale(self, factor):
        """Returns a new Pt() scaled by a factor, units are unchanged."""
        return self._replace(x=self.x.scale(factor), y=self.y.scale(factor))

    def normalise_units(self, units=None):
        """Returns a point with both x and y with the same units.
        If units is given then x and y will be in those units.
        This may return self or a new point.
        """
        if units is None:
            if self.x.units == self.y.units:
                return self
            return self.convert(self.x.units)
        else:
            if units == self.x.units and self.x.units == self.y.units:
                return self
            return self.convert(units)


###############################################
# Section: Polar/Cartesian conversion
###############################################
ANGLE_X_PLUS = 0.0
ANGLE_X_MINUS = math.pi
ANGLE_Y_PLUS = math.pi / 2.0
ANGLE_Y_MINUS = math.pi * 1.5


def to_cartesian(origin: Pt, radius: Dim, angle: float) -> Pt:
    """Displaces a point by radius in direction angle in radians which is an x to y rotation.
    dx is cos(angle) and dy is sin(angle).
    For example in a SVG coordinate system where +x is right and +y down an angle of less than pi/2 will move the point
    to the right and down.
    For use in a mapping system where +x is northing/Latitude N and +y easting/Longitude E an angle of less then pi/2
    will move the point up and to the right.
    """
    if radius.value == 0.0:
        return origin
    # Common cases where the move is along an axis
    if angle == ANGLE_X_PLUS:
        return Pt(x=origin.x + radius, y=origin.y)
    elif angle == ANGLE_Y_PLUS:
        return Pt(x=origin.x, y=origin.y + radius)
    elif angle == ANGLE_X_MINUS:
        return Pt(x=origin.x - radius, y=origin.y)
    elif angle == ANGLE_Y_MINUS:
        return Pt(x=origin.x, y=origin.y - radius)
    new_x = radius * math.cos(angle)
    new_y = radius * math.sin(angle)
    if origin is not None:
        new_x += origin.x
        new_y += origin.y
    return Pt(new_x, new_y)


def to_polar(pt_from: Pt, pt_to: Pt) -> typing.Tuple[Dim, float]:
    """Returns a radius as a Dim and angle in radians.
    NOTE: This uses math.atan2() so returns the result is between -pi and pi.

    Will raise if the given points are identical."""
    if pt_to == pt_from:
        raise ValueError('to_polar() called with identical points.')
    pt_from = pt_from.normalise_units()
    units = pt_to.x.units
    pt_to = pt_to.convert(units)
    dx = pt_to.x.value - pt_from.x.value
    dy = pt_to.y.value - pt_from.y.value
    # Common cases where the move is along an axis
    if dx == 0:
        if dy > 0:
            return Dim(dy, units), ANGLE_Y_PLUS
        return Dim(-dy, units), ANGLE_Y_MINUS
    if dy == 0:
        if dx > 0:
            return Dim(dx, units), ANGLE_X_PLUS
        return Dim(-dx, units), ANGLE_X_MINUS
    radius = Dim(math.sqrt(dx ** 2 + dy ** 2), units)
    angle = math.atan2(dy, dx)
    return radius, angle


###############################################
# END: Polar/Cartesian conversion
###############################################


###############################################
# Section: Helper functions for object creation
###############################################
def baseUnitsDim(theLen):
    """Returns a Coord.Dim() of length and units BASE_UNITS.

    :param theLen: Length.
    :type theLen: ``float, int``

    :returns: :py:class:`cpip.plot.Coord.Dim([float, str])` -- A new dimension of theLen in base units.
    """
    return Dim(theLen, BASE_UNITS)


def zeroBaseUnitsDim():
    """Returns a Coord.Dim() of zero length and units BASE_UNITS.

    :returns: :py:class:`cpip.plot.Coord.Dim([float, str])` -- A new dimension of zero.
    """
    return baseUnitsDim(0.0)


def zeroBaseUnitsBox():
    """Returns a Coord.Box() of zero dimensions and units BASE_UNITS."""
    return Box(
        zeroBaseUnitsDim(),
        zeroBaseUnitsDim(),
    )


def zeroBaseUnitsPad():
    """Returns a Coord.Pad() of zero dimensions and units BASE_UNITS."""
    return Pad(
        zeroBaseUnitsDim(),
        zeroBaseUnitsDim(),
        zeroBaseUnitsDim(),
        zeroBaseUnitsDim(),
    )


def zeroBaseUnitsPt():
    """Returns a Coord.Dim() of zero length and units BASE_UNITS.

    :returns: ``cpip.plot.Coord.Pt([cpip.plot.Coord.Dim([float, str]), cpip.plot.Coord.Dim([float, str])])`` -- A new  point with the values [0, 0].
    """
    return Pt(zeroBaseUnitsDim(), zeroBaseUnitsDim())


def pxUnitsDim(theLen):
    """Returns a Coord.Dim() of length and units 'px'.

    :param theLen: Length.
    :type theLen: ``float, int``

    :returns: :py:class:`cpip.plot.Coord.Dim([float, str])` -- A new dimension of theLen in base units.
    """
    return Dim(theLen, 'px')


def pxBaseUnitsDim():
    """Returns a Coord.Dim() of zero length and units 'px'.

    :returns: :py:class:`cpip.plot.Coord.Dim([float, str])` -- A new dimension of zero.
    """
    return pxUnitsDim(0.0)


def pxBaseUnitsBox():
    """Returns a Coord.Box() of zero dimensions and units 'px'."""
    return Box(
        pxBaseUnitsDim(),
        pxBaseUnitsDim(),
    )


def pxBaseUnitsPad():
    """Returns a Coord.Pad() of zero dimensions and units 'px'."""
    return Pad(
        pxBaseUnitsDim(),
        pxBaseUnitsDim(),
        pxBaseUnitsDim(),
        pxBaseUnitsDim(),
    )


def pxBaseUnitsPt():
    """Returns a Coord.Dim() of zero length and units 'px'.

    :returns: ``cpip.plot.Coord.Pt([cpip.plot.Coord.Dim([float, str]), cpip.plot.Coord.Dim([float, str])])`` -- A new  point with the values [0, 0].
    """
    return Pt(pxBaseUnitsDim(), pxBaseUnitsDim())


def newPt(theP, incX=None, incY=None):
    """Returns a new Pt object by incrementing existing point incX, incY
    that are both Dim() objects or ``None``.

    :param theP: The initial point.
    :type theP: ``cpip.plot.Coord.Pt([cpip.plot.Coord.Dim([float, str]), cpip.plot.Coord.Pt([cpip.plot.Coord.Dim([float, str])])``

    :param incX: Distance to move in the x axis.
    :type incX: ``NoneType, cpip.plot.Coord.Dim([float, str]), cpip.plot.Coord.Dim([int, str])``

    :param incY: Distance to move in the y axis.
    :type incY: ``NoneType, cpip.plot.Coord.Dim([float, str]), cpip.plot.Coord.Dim([int, str])``

    :returns: ``cpip.plot.Coord.Pt([cpip.plot.Coord.Dim([float, str]), cpip.plot.Coord.Dim([float, str])])`` -- The new point.
    """
    newX = theP.x
    if incX is not None:
        newX += incX
    newY = theP.y
    if incY is not None:
        newY += incY
    return Pt(x=newX, y=newY)


def convertPt(theP, theUnits):
    """Returns a new point with the dimensions of theP converted to theUnits.

    TODO: Deprecate this.
    """
    return Pt(
        x=Dim(convert(theP.x.value, theP.x.units, theUnits), theUnits),
        y=Dim(convert(theP.y.value, theP.y.units, theUnits), theUnits),
    )


def mirrorPt(start: Pt, finish: Pt) -> Pt:
    """
    Returns a new point that is the mirror of the finish point, 180 degrees from
    start to finish.
    """
    return newPt(start, incX=(start.x - finish.x), incY=(start.y - finish.y))

###########################################
# End: Helper functions for object creation
###########################################
