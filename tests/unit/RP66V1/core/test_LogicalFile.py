import copy
import io
import pprint

import numpy as np
import pytest

from TotalDepth.RP66V1.core import LogicalFile, RepCode
from TotalDepth.common import Slice
from tests.unit.RP66V1.core import test_data


@pytest.mark.parametrize(
    'by, expected',
    (
        (test_data.SMALL_FILE, 0,),
        (test_data.MINIMAL_FILE, 0,),
        (test_data.BASIC_FILE_WITH_TWO_VISIBLE_RECORDS_NO_IFLRS, 0,),
        (test_data.BASIC_FILE, 0,),
        (test_data.FILE_256kb, 0,),
    )
)
def test_logical_index_number_of_logical_files_no_with(by, expected):
    fobj = io.BytesIO(by)
    index = LogicalFile.LogicalIndex(fobj)
    assert len(index) == expected


@pytest.mark.parametrize(
    'bytes_name, expected',
    (
        ('SMALL_FILE', 1,),
        ('MINIMAL_FILE', 1,),
        ('BASIC_FILE_WITH_TWO_VISIBLE_RECORDS_NO_IFLRS', 1,),
        ('BASIC_FILE', 1,),
        ('FILE_256kb', 1,),
    )
)
def test_logical_index_number_of_logical_files(bytes_name, expected):
    by = getattr(test_data, bytes_name)
    fobj = io.BytesIO(by)
    with LogicalFile.LogicalIndex(fobj) as log_index:
        assert len(log_index) == expected


def test_logical_index_has_log_pass():
    fobj = io.BytesIO(test_data.BASIC_FILE)
    with LogicalFile.LogicalIndex(fobj) as logical_index:
        assert len(logical_index) == 1
        logical_file = logical_index.logical_files[0]
        assert logical_file.channel is not None
        assert logical_file.frame is not None
        assert logical_file.has_log_pass
        assert len(logical_file.log_pass) == 1


def test_logical_index_logical_file_iflr_position_map():
    fobj = io.BytesIO(test_data.BASIC_FILE)
    with LogicalFile.LogicalIndex(fobj) as logical_index:
        assert len(logical_index) == 1
        logical_file = logical_index.logical_files[0]
        # pprint.pprint(logical_file.iflr_position_map)
        expected_key = RepCode.ObjectName(O=2, C=0, I=b'50')
        assert list(logical_file.iflr_position_map.keys()) == [expected_key]


def test_logical_index_logical_file_iflr_position_map_x_axis_summary():
    fobj = io.BytesIO(test_data.BASIC_FILE)
    with LogicalFile.LogicalIndex(fobj) as logical_index:
        assert len(logical_index) == 1
        logical_file = logical_index.logical_files[0]
        # pprint.pprint(logical_file.iflr_position_map)
        expected_key = RepCode.ObjectName(O=2, C=0, I=b'50')
        assert list(logical_file.iflr_position_map.keys()) == [expected_key]
        x_axis = logical_file.iflr_position_map[expected_key]
        assert len(x_axis) == 649
        assert x_axis.summary.min == 2889.4
        assert x_axis.summary.max == 2954.199999999941
        assert x_axis.summary.count == 649


def test_logical_index_logical_file_iflr_position_map_x_axis_summary_spacing():
    fobj = io.BytesIO(test_data.BASIC_FILE)
    with LogicalFile.LogicalIndex(fobj) as logical_index:
        assert len(logical_index) == 1
        logical_file = logical_index.logical_files[0]
        # pprint.pprint(logical_file.iflr_position_map)
        expected_key = RepCode.ObjectName(O=2, C=0, I=b'50')
        assert list(logical_file.iflr_position_map.keys()) == [expected_key]
        x_axis = logical_file.iflr_position_map[expected_key]
        assert x_axis.summary.spacing.min == 0.09999999999990905
        assert x_axis.summary.spacing.max == 0.09999999999990905
        assert x_axis.summary.spacing.mean == 0.09999999999990905
        assert x_axis.summary.spacing.median == 0.09999999999990905
        assert x_axis.summary.spacing.std == 0.0
        # assert x_axis.summary.spacing.histogram == (np.array([648]), np.array([-0.4,  0.6]))


def test_logical_index_logical_file_iflr_position_map_x_axis_summary_spacing_counts():
    fobj = io.BytesIO(test_data.BASIC_FILE)
    with LogicalFile.LogicalIndex(fobj) as logical_index:
        assert len(logical_index) == 1
        logical_file = logical_index.logical_files[0]
        # pprint.pprint(logical_file.iflr_position_map)
        expected_key = RepCode.ObjectName(O=2, C=0, I=b'50')
        assert list(logical_file.iflr_position_map.keys()) == [expected_key]
        x_axis = logical_file.iflr_position_map[expected_key]
        assert x_axis.summary.spacing.counts.norm == 648
        assert x_axis.summary.spacing.counts.dupe == 0
        assert x_axis.summary.spacing.counts.skip == 0
        assert x_axis.summary.spacing.counts.back == 0


def test_logical_file_populate_frame_array():
    fobj = io.BytesIO(test_data.BASIC_FILE)
    with LogicalFile.LogicalIndex(fobj) as logical_index:
        assert len(logical_index) == 1
        logical_file = logical_index.logical_files[0]
        assert logical_file.has_log_pass
        assert len(logical_file.log_pass) == 1
        frame_array = logical_file.log_pass[0]
        frame_count = logical_file.populate_frame_array(frame_array)
        assert frame_count == 649
        assert len(frame_array) == 5
        assert frame_array.shape == [(649, 1), (649, 1), (649, 1), (649, 1), (649, 1)]
        names = [c.ident.I for c in frame_array.channels]
        assert names == [b'DEPT', b'TENS', b'ETIM', b'DHTN', b'GR']


def test_logical_file_populate_frame_array_raises_if_frame_array_not_member():
    fobj = io.BytesIO(test_data.BASIC_FILE)
    with LogicalFile.LogicalIndex(fobj) as logical_index:
        assert len(logical_index) == 1
        logical_file = logical_index.logical_files[0]
        assert logical_file.has_log_pass
        assert len(logical_file.log_pass) == 1
        frame_array = logical_file.log_pass[0]
        frame_array_copy = copy.copy(frame_array)
        with pytest.raises(LogicalFile.ExceptionLogicalFile) as err:
            logical_file.populate_frame_array(frame_array_copy)
        assert err.value.args[0] == 'populate_frame_array(): given FrameArray is not in Log Pass'


def test_logical_file_populate_frame_array_channels():
    fobj = io.BytesIO(test_data.BASIC_FILE)
    with LogicalFile.LogicalIndex(fobj) as logical_index:
        assert len(logical_index) == 1
        logical_file = logical_index.logical_files[0]
        assert logical_file.has_log_pass
        assert len(logical_file.log_pass) == 1
        frame_array = logical_file.log_pass[0]
        channels = [frame_array.channels[i].ident for i in (1, 4)]
        frame_count = logical_file.populate_frame_array(frame_array, channels=channels)
        assert frame_count == 649
        assert len(frame_array) == 5
        assert frame_array.shape == [(649, 1), (649, 1), (0, 1), (0, 1), (649, 1)]
        names = [c.ident.I for c in frame_array.channels]
        assert names == [b'DEPT', b'TENS', b'ETIM', b'DHTN', b'GR']
        assert frame_array[0].array.shape == (649, 1)
        assert frame_array[1].array.shape == (649, 1)
        assert frame_array[2].array.shape == (0, 1)
        assert frame_array[3].array.shape == (0, 1)
        assert frame_array[4].array.shape == (649, 1)


def test_logical_file_populate_frame_array_partial_slice():
    fobj = io.BytesIO(test_data.BASIC_FILE)
    with LogicalFile.LogicalIndex(fobj) as logical_index:
        assert len(logical_index) == 1
        logical_file = logical_index.logical_files[0]
        assert logical_file.has_log_pass
        assert len(logical_file.log_pass) == 1
        frame_array = logical_file.log_pass[0]
        frame_slice = Slice.Slice(8, 64, 2)
        frame_count = logical_file.populate_frame_array(frame_array, frame_slice)
        assert frame_count == 28


def test_logical_file_populate_frame_array_partial_split():
    fobj = io.BytesIO(test_data.BASIC_FILE)
    with LogicalFile.LogicalIndex(fobj) as logical_index:
        assert len(logical_index) == 1
        logical_file = logical_index.logical_files[0]
        assert logical_file.has_log_pass
        assert len(logical_file.log_pass) == 1
        frame_array = logical_file.log_pass[0]
        frame_slice = Slice.Sample(64)
        frame_count = logical_file.populate_frame_array(frame_array, frame_slice)
        assert frame_count == 64
