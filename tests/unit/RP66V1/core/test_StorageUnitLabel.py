import pytest

from TotalDepth.RP66V1.core import StorageUnitLabel


IDENTIFIER = b' ' * 60
SIMPLE_SUL_BYTES = b'0001V1.00RECORD08192                                                            '

def _create_simple_sul():
    sul = StorageUnitLabel.create_storage_unit_label(1, b'V1.00', 8192, IDENTIFIER)
    return sul


def test_simple_sul():
    sul = _create_simple_sul()
    assert sul.storage_unit_sequence_number == 1
    assert sul.dlis_version == b'V1.00'
    assert sul.maximum_record_length == 8192
    assert sul.storage_unit_structure == b'RECORD'
    assert sul.storage_set_identifier == IDENTIFIER


def test_simple_sul_as_bytes():
    sul = _create_simple_sul()
    # print(sul.as_bytes())
    expected = SIMPLE_SUL_BYTES
    assert sul.as_bytes() == expected


def test_simple_sul_str():
    sul = _create_simple_sul()
    # print(sul)
    expected = """StorageUnitLabel:
  Storage Unit Sequence Number: 1
                  DLIS Version: b'V1.00'
        Storage Unit Structure: b'RECORD'
         Maximum Record Length: 8192
        Storage Set Identifier: b'                                                            '"""
    assert str(sul) == expected


def test_sul_ctor():
    sul =StorageUnitLabel.StorageUnitLabel(SIMPLE_SUL_BYTES)
    assert sul.as_bytes() == SIMPLE_SUL_BYTES


@pytest.mark.parametrize(
    'by, expected',
    (
        # Size wrong
        (b'', 'Expected 80 bytes, got 0'),
        (SIMPLE_SUL_BYTES + b' ', 'Expected 80 bytes, got 81'),
        # storage_unit_sequence_number not a number
        (
            b'A001V1.00RECORD08192                                                            ',
            "Can not match RE_STORAGE_UNIT_SEQUENCE_NUMBER on b'A001'",
        ),
        # dlis_version incorrect
        (
            b'0001V2.00RECORD08192                                                            ',
            "Can not match RE_DLIS_VERSION on b'V2.00'",
        ),
        # storage_unit_structure incorrect
        (
            b'0001V1.00REXORD08192                                                            ',
            "Can not match RE_STORAGE_UNIT_STRUCTURE on b'REXORD'",
        ),
        # maximum_record_length incorrect
        (
            b'0001V1.00RECORDxxxxx                                                            ',
            "Can not match RE_MAXIMUM_RECORD_LENGTH on b'xxxxx'",
        ),
    )
)
def test_sul_ctor_raises(by, expected):
    with pytest.raises(StorageUnitLabel.ExceptionStorageUnitLabel) as err:
        StorageUnitLabel.StorageUnitLabel(by)
    assert err.value.args[0] == expected
