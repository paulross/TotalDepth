import io
import pickle

import pytest

from TotalDepth.RP66V1.core import Index
# from TotalDepth.RP66V1.core import LogicalFile
from tests.unit.RP66V1.core import test_data


def test_logical_record_index_ctor_empty():
    file = io.BytesIO(test_data.BASIC_FILE)
    index = Index.LogicalRecordIndex(file)
    assert len(index) == 0


@pytest.mark.parametrize(
    'index, vr_position, lrsh_position, attributes, lr_type, ld_length',
    (
        (0, 80, 84, 0x80, 0, 120),
        (1, 80, 208, 0x81, 1, 504),
    )
)
def test_logical_record_index_minimal_file(index, vr_position, lrsh_position, attributes, lr_type, ld_length):
    file = io.BytesIO(test_data.MINIMAL_FILE)
    with Index.LogicalRecordIndex(file) as lr_index:
        assert len(lr_index) == 2
        assert lr_index[index].position.vr_position == vr_position
        assert lr_index[index].position.lrsh_position == lrsh_position
        assert lr_index[index].description.attributes.is_first
        assert lr_index[index].description.attributes.attributes == attributes
        assert lr_index[index].description.lr_type == lr_type
        assert lr_index[index].description.ld_length == ld_length


@pytest.mark.parametrize(
    'index, offset, length, expected_bytes',
    (
        (0, 0, 8, b'\xf0\x0bFILE-H'),
        (1, 0, 8, b'\xf0\x06ORIGIN'),
    )
)
def test_logical_record_index_minimal_file_get_file_logical_data(index, offset, length, expected_bytes):
    file = io.BytesIO(test_data.MINIMAL_FILE)
    with Index.LogicalRecordIndex(file) as lr_index:
        file_logical_data = lr_index.get_file_logical_data(index, offset, length)
        assert file_logical_data.is_sealed()
        assert file_logical_data.logical_data.index == 0
        assert file_logical_data.logical_data.bytes == expected_bytes


@pytest.mark.parametrize(
    'index, vr_position, lrsh_position, attributes, lr_type, ld_length',
    (
        (0, 80, 84, 0x80, 0, 120),
        (1, 80, 208, 0x81, 1, 504),
        (2, 80, 716, 0x81, 4, 200),
        (3, 80, 920, 0x80, 5, 3032),
        (4, 80, 3956, 0x80, 5, 846),
        (5, 80, 4806, 0x80, 3, 378),
        (6, 80, 5188, 0x80, 128, 158),
        (7, 80, 5350, 0x81, 6, 1688),
        (8, 80, 7042, 0xa0, 6, 1772),
    )
)
def test_logical_record_index_basic_file_with_two_vrs(index, vr_position, lrsh_position, attributes, lr_type, ld_length):
    file = io.BytesIO(test_data.BASIC_FILE_WITH_TWO_VISIBLE_RECORDS_NO_IFLRS)
    with Index.LogicalRecordIndex(file) as lr_index:
        assert len(lr_index) == 9
        assert lr_index[index].position.vr_position == vr_position
        assert lr_index[index].position.lrsh_position == lrsh_position
        assert lr_index[index].description.attributes.is_first
        assert lr_index[index].description.attributes.attributes == attributes
        assert lr_index[index].description.lr_type == lr_type
        assert lr_index[index].description.ld_length == ld_length


def test_logical_record_index_small_file():
    file = io.BytesIO(test_data.SMALL_FILE)
    with Index.LogicalRecordIndex(file) as lr_index:
        assert len(lr_index) == 88


def test_logical_record_index_small_file_eflr_iflr_counts():
    file = io.BytesIO(test_data.SMALL_FILE)
    with Index.LogicalRecordIndex(file) as lr_index:
        counts = {'EFLR': 0, 'IFLR': 0, }
        for i in range(len(lr_index)):
            if lr_index[i].description.attributes.is_eflr:
                counts['EFLR'] += 1
            else:
                counts['IFLR'] += 1
        assert counts == {'EFLR': 5, 'IFLR': 83,}


def test_logical_record_index_basic_file():
    file = io.BytesIO(test_data.BASIC_FILE)
    with Index.LogicalRecordIndex(file) as lr_index:
        assert len(lr_index) == 660


def test_logical_record_index_basic_file_eflr_iflr_counts():
    file = io.BytesIO(test_data.BASIC_FILE)
    with Index.LogicalRecordIndex(file) as lr_index:
        counts = {'EFLR': 0, 'IFLR': 0, }
        for i in range(len(lr_index)):
            if lr_index[i].description.attributes.is_eflr:
                counts['EFLR'] += 1
            else:
                counts['IFLR'] += 1
        assert counts == {'EFLR': 10, 'IFLR': 650, }


def test_logical_record_index_file_256kb():
    file = io.BytesIO(test_data.FILE_256kb)
    with Index.LogicalRecordIndex(file) as lr_index:
        assert len(lr_index) == 1883


def test_logical_record_index_file_256kb_eflr_iflr_counts():
    file = io.BytesIO(test_data.FILE_256kb)
    with Index.LogicalRecordIndex(file) as lr_index:
        counts = {'EFLR': 0, 'IFLR': 0, }
        for i in range(len(lr_index)):
            if lr_index[i].description.attributes.is_eflr:
                counts['EFLR'] += 1
            else:
                counts['IFLR'] += 1
        assert counts == {'EFLR': 31, 'IFLR': 1852,}


@pytest.mark.parametrize(
    'by, expected',
    (
        (test_data.SMALL_FILE, 88,),
        (test_data.MINIMAL_FILE, 2,),
        (test_data.BASIC_FILE_WITH_TWO_VISIBLE_RECORDS_NO_IFLRS, 9,),
        (test_data.BASIC_FILE, 660,),
        (test_data.FILE_256kb, 1883,),
    )
)
def test_logical_record_index_all_files(by, expected):
    fobj = io.BytesIO(by)
    with Index.LogicalRecordIndex(fobj) as lr_index:
        assert len(lr_index) == expected


def test_logical_record_index_sul():
    fobj = io.BytesIO(test_data.BASIC_FILE)
    with Index.LogicalRecordIndex(fobj) as lr_index:
        assert str(lr_index.sul) == r"""StorageUnitLabel:
  Storage Unit Sequence Number: 1
                  DLIS Version: b'V1.00'
        Storage Unit Structure: b'RECORD'
         Maximum Record Length: 8192
        Storage Set Identifier: b'              +++TIF@C:\\INSITE\\Data\\ExpFiles\\VA2456~1.DLI+++'"""


def test_logical_record_index_pickle():
    fobj = io.BytesIO(test_data.BASIC_FILE)
    with Index.LogicalRecordIndex(fobj) as lr_index:
        pickled_index = pickle.dumps(lr_index)
        # assert len(pickled_index) == 53106
        new_lr_index = pickle.loads(pickled_index)
        assert len(new_lr_index) == 660
