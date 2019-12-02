import io
import os
import sys

import numpy as np

from TotalDepth.RP66V1.core import LogicalFile, RepCode
from TotalDepth.common import Slice
from tests.unit.RP66V1.core import test_data


def demo_logical_files_test_data():
    file_object = io.BytesIO(test_data.BASIC_FILE)
    with LogicalFile.LogicalIndex(file_object) as logical_index:
        # print(f'LogicalIndex: {logical_index} with {len(logical_index)} Logical Files')
        for l, logical_file in enumerate(logical_index.logical_files):
            # print(f'LogicalFile [{l}]: {logical_file}')
            print(f'***** logical_file.file_header_logical_record.str_long():')
            print(logical_file.file_header_logical_record.str_long())
            print()
            print(f'***** logical_file.origin_logical_record.str_long():')
            print(logical_file.origin_logical_record.str_long())
            print()
            print(f'***** logical_file.defining_origin:')
            print(logical_file.defining_origin)
            print()
            if logical_file.channel is not None:
                print(f'***** logical_file.channel.str_long():')
                print(logical_file.channel.str_long())
                print()
            if logical_file.frame is not None:
                print(f'***** logical_file.frame.str_long():')
                print(logical_file.frame.str_long())
                print()
            print(f'***** logical_file.has_log_pass:')
            print(logical_file.has_log_pass)
            print()
            if logical_file.has_log_pass:
                print(f'***** logical_file.log_pass:')
                print(logical_file.log_pass)
                print()


def demo_numpy_describe_test_data():
    fobj = io.BytesIO(test_data.BASIC_FILE)
    with LogicalFile.LogicalIndex(fobj) as logical_index:
        for lf_index, logical_file in enumerate(logical_index.logical_files):
            if logical_file.has_log_pass:
                for frame_array in logical_file.log_pass:
                    print(frame_array)
                    frame_count = logical_index.populate_frame_array(lf_index, frame_array)
                    print(
                        f'Loaded {frame_count} frames and {len(frame_array)} channels'
                        f' from {frame_array.ident} using {frame_array.sizeof_array} bytes.'
                    )
                    for channel in frame_array.channels:
                        print(f'Channel: {channel}')
                        # channel.array is a numpy array
                        np.info(channel.array)
                        print()


def demo_numpy_access_partial_test_data():
    fobj = io.BytesIO(test_data.BASIC_FILE)
    with LogicalFile.LogicalIndex(fobj) as logical_index:
        for lf_index, logical_file in enumerate(logical_index.logical_files):
            if logical_file.has_log_pass:
                for frame_array in logical_file.log_pass:
                    # print(frame_array)
                    # print('TRACE:', [c.ident for c in frame_array.channels])
                    frame_count = logical_index.populate_frame_array(
                        lf_index, frame_array,
                        frame_slice=Slice.Slice(0, None, 64),
                        # frame_slice=Slice.Split(64),
                        channels={frame_array.channels[1].ident, frame_array.channels[2].ident}
                    )
                    print(
                        f'Loaded {frame_count} frames'
                        f' from {frame_array.ident} using {frame_array.sizeof_array} bytes.'
                    )
                    for channel in frame_array.channels:
                        if len(channel.array):
                            print(channel.ident, channel.long_name, channel.units)
                            print(f'Min: {channel.array.min():12.3f} Max: {channel.array.max():12.3f}')
                        # else:
                        #     print('N/A')
                    print()


def demo_eflr_contents_test_data():
    file_object = io.BytesIO(test_data.BASIC_FILE)
    with LogicalFile.LogicalIndex(file_object) as logical_index:
        for logical_file in logical_index.logical_files:
            for position, eflr in logical_file.eflrs:
                # eflr is a TotalDepth.RP66V1.core.LogicalRecord.EFLR.ExplicitlyFormattedLogicalRecord
                # print(eflr.set.type)
                if eflr.set.type == b'PARAMETER':
                    # print(eflr)
                    print(eflr[0])
                    print()
                    print(eflr[0][0])
                    # print(eflr.object_name_map.keys())
                    # print(eflr[0].attr_label_map.keys())
                    # print(eflr[RepCode.ObjectName(O=2, C=0, I=b'LOC')][b'LONG-NAME'])

                    # print(eflr[RepCode.ObjectName()][0])
                    # print(eflr[b'LOC'][b'LONG-NAME'])
                    # for row in eflr.objects:
                    #     # row is a TotalDepth.RP66V1.core.LogicalRecord.EFLR.Object
                    #     print(f'    Row: {row.name.I}')
                    #     for attr in row.attrs:
                    #         # attr is a TotalDepth.RP66V1.core.LogicalRecord.EFLR.Attribute
                    #         print(f'        Attr: {attr.label} = {attr.value} ({attr.units})')


path_in = os.path.join('data', '206_05a-_3_DWL_DWL_WIRE_258276498.DLIS')


def demo_logical_files():
    with LogicalFile.LogicalIndex(path_in) as logical_index:
        print(f'logicalIndex: {logical_index} with {len(logical_index)} Logical Files')
        for logical_file in logical_index.logical_files:
            print(f'logicalFile: {logical_file}')
            print(logical_file.file_header_logical_record.str_long())
            print(logical_file.origin_logical_record.str_long())


def demo_eflr():
    with LogicalFile.LogicalIndex(path_in) as logical_index:
        # print(logical_index)
        for logical_file in logical_index.logical_files:
            # print(logical_file)
            for position, eflr in logical_file.eflrs:
                # print(position_eflr.eflr)
                # print(eflr.shape)
                print(eflr.str_long())


def demo_eflr_contents():
    with LogicalFile.LogicalIndex(path_in) as logical_index:
        for logical_file in logical_index.logical_files:
            for position, eflr in logical_file.eflrs:
                # eflr is a TotalDepth.RP66V1.core.LogicalRecord.EFLR.ExplicitlyFormattedLogicalRecord
                if eflr.set.type == b'EQUIPMENT':
                    for row in eflr.objects:
                        # row is a TotalDepth.RP66V1.core.LogicalRecord.EFLR.Object
                        print(f'    Row: {row.name.I}')
                        for attr in row.attrs:
                            # attr is a TotalDepth.RP66V1.core.LogicalRecord.EFLR.Attribute
                            print(f'        {attr.label}={attr.value} ({attr.units})')


def demo_numpy_describe():
    with LogicalFile.LogicalIndex(path_in) as logical_index:
        for lf_index, logical_file in enumerate(logical_index.logical_files):
            if logical_file.has_log_pass:
                for frame_array in logical_file.log_pass:
                    print(frame_array)
                    frame_count = logical_index.populate_frame_array(lf_index, frame_array)
                    print(
                        f'Loaded {frame_count} frames and {len(frame_array)} channels'
                        f' from {frame_array.ident} using {frame_array.sizeof_array} bytes.'
                    )
                    for channel in frame_array.channels:
                        print(channel)
                        # channel.array is a numpy array
                        np.info(channel.array)
                        print()


def demo_numpy_access():
    with LogicalFile.LogicalIndex(path_in) as logical_index:
        for lf_index, logical_file in enumerate(logical_index.logical_files):
            if logical_file.has_log_pass:
                for frame_array in logical_file.log_pass:
                    print(frame_array)
                    frame_count = logical_index.populate_frame_array(lf_index, frame_array)
                    print(
                        f'Loaded {frame_count} frames and {len(frame_array)} channels'
                        f' from {frame_array.ident} using {frame_array.sizeof_array} bytes.'
                    )
                    for channel in frame_array.channels:
                        print(channel.ident, channel.long_name, channel.units)
                        # channel.array is a numpy array
                        print(f'Min: {channel.array.min():12.3f} Max: {channel.array.max():12.3f}')


def demo_numpy_access_partial():
    with LogicalFile.LogicalIndex(path_in) as logical_index:
        for lf_index, logical_file in enumerate(logical_index.logical_files):
            if logical_file.has_log_pass:
                for frame_array in logical_file.log_pass:
                    # print(frame_array)
                    # print('TRACE:', [c.ident for c in frame_array.channels])
                    frame_count = logical_index.populate_frame_array(
                        lf_index, frame_array,
                        frame_slice=Slice.Slice(0, None, 64),
                        # frame_slice=Slice.Split(64),
                        channels={frame_array.channels[1].ident, frame_array.channels[2].ident}
                    )
                    print(
                        f'Loaded {frame_count} frames'
                        f' from {frame_array.ident} using {frame_array.sizeof_array} bytes.'
                    )
                    for channel in frame_array.channels:
                        if len(channel.array):
                            print(channel.ident, channel.long_name, channel.units)
                            print(f'Min: {channel.array.min():12.3f} Max: {channel.array.max():12.3f}')
                        # else:
                        #     print('N/A')
                    print()


def main() -> int:
    # demo_logical_files_test_data()
    # demo_numpy_describe_test_data()
    demo_eflr_contents_test_data()

    # demo_numpy_access_partial_test_data()
    # demo_logical_files()
    # demo_eflr()
    # demo_eflr_contents()
    # demo_numpy_describe()
    # demo_numpy_access()
    # demo_numpy_access_partial()
    return 0


if __name__ == '__main__':
    sys.exit(main())
