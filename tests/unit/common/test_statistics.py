
import pytest

from TotalDepth.common import statistics


def test_length_dict():
    ld = statistics.LengthDict()
    for i in range(8):
        ld.add(i)
    assert ld.count == 8


def test_length_dict_zero_count():
    ld = statistics.LengthDict()
    for i in range(8):
        ld.add(i)
    assert ld.zero_count == 1


def test_length_dict_add_raises():
    ld = statistics.LengthDict()
    with pytest.raises(ValueError) as err:
        ld.add(-1)
    assert err.value.args[0] == 'Length must be >= 0 not -1'


def test_length_dict_reduced_power_2():
    ld = statistics.LengthDict()
    for i in range(64):
        ld.add(i)
    assert ld.reduced_power_2() == {0: 1, 1: 2, 2: 4, 3: 8, 4: 16, 5: 32}


def test_length_dict_histogram_power_2():
    ld = statistics.LengthDict()
    for i in range(64):
        ld.add(i)
    hist = ld.histogram_power_of_2()
    assert ld.zero_count == 1
    expected = [
        '>=2**0  [     1] | +',
        '>=2**1  [     2] | +++',
        '>=2**2  [     4] | +++++',
        '>=2**3  [     8] | ++++++++++',
        '>=2**4  [    16] | ++++++++++++++++++++',
        '>=2**5  [    32] | ++++++++++++++++++++++++++++++++++++++++',
    ]
    assert hist == expected


def test_length_dict_histogram_power_2_skip_a_value():
    ld = statistics.LengthDict()
    ld.add(2)
    ld.add(8)
    hist = ld.histogram_power_of_2()
    assert ld.zero_count == 0
    expected = [
        '>=2**1  [     1] | ++++++++++++++++++++++++++++++++++++++++',
        '>=2**2  [     0] | ',
        '>=2**3  [     1] | ++++++++++++++++++++++++++++++++++++++++',
    ]
    assert hist == expected

