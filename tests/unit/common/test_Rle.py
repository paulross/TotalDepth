# import unittest

import pytest

from TotalDepth.common import Rle

# ====================== Test of Rle.RLEItem ======================

def _create_simple_rle_item(values):
    """Returns a RLEItem with the values [5, 8, 11, 14, 17, 20, 23, 26]"""
    rle_item = Rle.RLEItem(values[0])
    for v in values[1:]:
        rle_item.add(v)
    return rle_item


SIMPLE_RLE_ITEM = _create_simple_rle_item(range(5, 5 + 8 * 3, 3))
SIMPLE_RLE_ITEM_NEGATIVE = _create_simple_rle_item(range(-5, -5 - 8 * 3, -3))
SINGLE_RLE_ITEM = Rle.RLEItem(5)


def test_rle_item_add_int():
    values = list(range(5, 5 + 8 * 3, 3))
    rle_item = Rle.RLEItem(values[0])
    for v in values[1:]:
        assert rle_item.add(v) is True


def test_rle_item_add_int_fails():
    assert not SIMPLE_RLE_ITEM.add(1000)


def test_rle_item_add_float():
    values = [
        805.2105103,
        805.2105103 + 0.0025399999999535794,
        805.2155903,
        805.2155903 + 0.0025399999999535794,
    ]
    rle_item = Rle.RLEItem(values[0])
    for v in values[1:]:
        assert rle_item.add(v) is True


@pytest.mark.parametrize(
    'rle, expected',
    (
        (SIMPLE_RLE_ITEM, (5, 3, 7)),
        (SINGLE_RLE_ITEM, (5, 0, 0)),
    )
)
def test_rle_item_attributes(rle, expected):
    assert rle.datum == expected[0]
    assert rle.stride == expected[1]
    assert rle.repeat == expected[2]


def test_rle_item_str():
    assert str(SIMPLE_RLE_ITEM) == '<RLEItem: datum=5 stride=3 repeat=7>'


def test_rle_item_len():
    assert len(SIMPLE_RLE_ITEM) == 8


def test_rle_item_values():
    assert list(SIMPLE_RLE_ITEM.values()) == [5, 8, 11, 14, 17, 20, 23, 26]


@pytest.mark.parametrize(
    'index, expected',
    (
        (0, (0, 5)),
        (1, (1, 8)),
        (2, (2, 11)),
        (3, (3, 14)),
        (4, (4, 17)),
        (5, (5, 20)),
        (6, (6, 23)),
        (7, (7, 26)),
        (8, (0, None)),  # Overrun
        (9, (1, None)),
        (-1, (-1, 26)),
        (-2, (-2, 23)),
        (-3, (-3, 20)),
        (-4, (-4, 17)),
        (-5, (-5, 14)),
        (-6, (-6, 11)),
        (-7, (-7, 8)),
        (-8, (-8, 5)),
        (-9, (-1, None)),  # Underrun
        (-10, (-2, None)),
    )
)
def test_rle_item_value(index, expected):
    assert SIMPLE_RLE_ITEM.value(index) == expected


@pytest.mark.parametrize(
    'rle, expected',
    (
        (SIMPLE_RLE_ITEM, range(5, 29, 3)),
        (SINGLE_RLE_ITEM, range(5, 6, 1)),
        (SIMPLE_RLE_ITEM_NEGATIVE, range(-5, -29, -3)),
    )
)
def test_rle_item_range(rle, expected):
    assert rle.range() == expected


@pytest.mark.parametrize(
    'rle, expected',
    (
        (SIMPLE_RLE_ITEM, 26),
        (SINGLE_RLE_ITEM, 5),
        (SIMPLE_RLE_ITEM_NEGATIVE, -26),
    )
)
def test_rle_item_last(rle, expected):
    assert rle.last() == expected


@pytest.mark.parametrize(
    'value, expected',
    (
        (5, 5),
        (6, 5),
        (7, 5),
        (8, 8),
        (9, 8),
        (26, 26),
        (27, 26),
        (28, 26),
    )
)
def test_rle_item_largest_le(value, expected):
    assert SIMPLE_RLE_ITEM.largest_le(value) == expected


def test_rle_item_largest_le_raises():
    with pytest.raises(ValueError) as err:
        SIMPLE_RLE_ITEM.largest_le(4)
    assert err.value.args[0] == 'RLEItem.largest_le(): datum 5 > value 4'


def test_rle_item_direct_construction():
    # range(5, 5 + 8 * 3, 3)
    rle_item = Rle.RLEItem(5)
    rle_item.repeat = 7
    rle_item.stride = 3
    assert list(rle_item.values()) == list(SIMPLE_RLE_ITEM.values())

# ====================== END: Test of Rle.RLEItem ======================

# ====================== Test of Rle.RLE ======================


def _create_rle(*ranges):
    """Returns a RLEItem with the values [5, 8, 11, 14, 17, 20, 23, 26]"""
    rle = Rle.RLE()
    for rng in ranges:
        for v in rng:
            rle.add(v)
    return rle


RLE_SINGLE_RANGE = _create_rle(range(5, 5 + 8 * 3, 3))
RLE_TWO_RANGES = _create_rle(range(5, 5 + 8 * 3, 3), range(500, 500 + 8 * 3, 3))
RLE_MULTIPLE_RANGE = _create_rle(range(0, 3*8, 3), range(72, 95, 1), range(105, 117, 2))


def test_rle_mt():
    rle = Rle.RLE()
    assert len(rle) == 0
    assert rle.num_values() == 0
    assert list(rle.values()) == []
    with pytest.raises(IndexError) as err:
        rle.value(0)
    assert err.value.args[0] == 'list index out of range'


def test_rle_add_regular_int():
    rle = RLE_SINGLE_RANGE
    assert len(rle) == 1
    assert str(rle) == '<RLE: func=None: [<RLEItem: datum=5 stride=3 repeat=7>]>'


def test_rle_add_two_ranges_int():
    rle = RLE_TWO_RANGES
    assert len(rle) == 2
    assert str(rle) == '<RLE: func=None: [<RLEItem: datum=5 stride=3 repeat=7>, <RLEItem: datum=500 stride=3 repeat=7>]>'


def test_rle_add_multiple_ranges():
    rle = Rle.RLE()
    rle_input = list(range(0, 3*8, 3)) + list(range(72, 95, 1)) + list(range(105, 117, 2))
    for v in rle_input:
        rle.add(v)
    # Three ranges
    assert len(rle) == 3
    assert rle.num_values() == len(rle_input)
    assert list(rle.values()) == rle_input
    for i, v in enumerate(rle_input):
        assert rle.value(i) == v
    # Check property access
    assert rle[0].datum == 0
    assert rle[0].stride == 3
    assert rle[0].repeat == 7
    assert rle[1].datum == 72
    assert rle[1].stride == 1
    assert rle[1].repeat == 95-72-1
    assert rle[2].datum == 105
    assert rle[2].stride == 2
    assert rle[2].repeat == ((117-105)//2)-1


@pytest.mark.parametrize(
    'value, expected',
    (
        (5, 5),
        (6, 5),
        (7, 5),
        (8, 8),
        (9, 8),
        (26, 26),
        (27, 26),
        (28, 26),
        (499, 26),
        (500, 500),
        (501, 500),
        (1000, 500 + 7 * 3),
    )
)
def test_rle_largest_le_two_ranges(value, expected):
    result = RLE_TWO_RANGES.largest_le(value)
    # print(result)
    assert result == expected


@pytest.mark.parametrize(
    'value',
    (0, 1, 2, 3, 4,)
)
def test_rle_largest_le_two_ranges(value):
    with pytest.raises(ValueError) as err:
        RLE_TWO_RANGES.largest_le(value)
    assert err.value.args[0] == f'Can not find largest_le for value {value}'


@pytest.mark.parametrize(
    'value, expected',
    (
        (0, 0),
        (3, 3),
        (6, 6),
        (9, 9),
        (12, 12),
        (15, 15),
        (18, 18),
        (21, 21),
        (24, 21),
        (27, 21),
        # ...
        (69, 21),
        (72, 72),
        (75, 75),
        (78, 78),
        (81, 81),
        (84, 84),
        (87, 87),
        (90, 90),
        (93, 93),
        (96, 94),
        (99, 94),
        (102, 94),
        (105, 105),
        (108, 107),
        (111, 111),
        (114, 113),
        (117, 115),
        (120, 115),
        (123, 115),
    )
)
def test_rle_largest_le_three_ranges(value, expected):
    # for value in range(0, 123, 3):
    #     result = RLE_MULTIPLE_RANGE.largest_le(value)
    #     print(str((value, result))+',')
    result = RLE_MULTIPLE_RANGE.largest_le(value)
    assert result == expected


def test_rle_mt_function():
    rle = Rle.RLE(lambda x: x**2)
    for i in range(4):
        rle.add(i)
    # for rle_item in rle.rle_items:
    #     print(rle_item)
    assert len(rle) == 2
    assert rle[0].datum == 0
    assert rle[0].stride == 1
    assert rle[0].repeat == 1
    assert rle[1].datum == 4
    assert rle[1].stride == 5
    assert rle[1].repeat == 1


def test_rle_direct_construction():
    rle = Rle.RLE()
    # range(5, 5 + 8 * 3, 3)
    rle_item = Rle.RLEItem(5)
    rle_item.repeat = 7
    rle_item.stride = 3
    rle.rle_items.append(rle_item)
    # range(500, 500 + 8 * 3, 3)
    rle_item = Rle.RLEItem(500)
    rle_item.repeat = 7
    rle_item.stride = 3
    rle.rle_items.append(rle_item)
    assert list(rle.values()) == list(RLE_TWO_RANGES.values())


# ====================== END: Test of Rle.RLE ======================
