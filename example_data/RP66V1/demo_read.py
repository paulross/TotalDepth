import sys

import numpy as np

from TotalDepth.RP66V1.core import File
from TotalDepth.RP66V1.core import LogicalFile
from TotalDepth.common import Slice


path_in = '206_05a-_3_DWL_DWL_WIRE_258276498.DLIS'


def demo_file():
    with open(path_in, 'rb') as fobj:
        rp66v1_file = File.FileRead(fobj)
        print(rp66v1_file.sul)


def demo_logical_files():
    with open(path_in, 'rb') as fobj:
        rp66v1_file = File.FileRead(fobj)
        logical_index = LogicalFile.LogicalIndex(rp66v1_file, path_in)
        print(logical_index)
        for logical_file in logical_index.logical_files:
            print(logical_file)
            # print(logical_file.file_header_logical_record)
            # print(logical_file.origin_logical_record)
            # print(logical_file.file_header_logical_record.str_long())
            # print(logical_file.origin_logical_record.str_long())


def demo_eflr():
    with open(path_in, 'rb') as fobj:
        rp66v1_file = File.FileRead(fobj)
        logical_index = LogicalFile.LogicalIndex(rp66v1_file, path_in)
        # print(logical_index)
        for logical_file in logical_index.logical_files:
            # print(logical_file)
            for position, eflr in logical_file.eflrs:
                # print(position_eflr.eflr)
                # print(eflr.shape)
                print(eflr.str_long())


def demo_eflr_contents():
    with open(path_in, 'rb') as fobj:
        rp66v1_file = File.FileRead(fobj)
        logical_index = LogicalFile.LogicalIndex(rp66v1_file, path_in)
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


def demo_numpy_access():
    with open(path_in, 'rb') as fobj:
        rp66v1_file = File.FileRead(fobj)
        logical_index = LogicalFile.LogicalIndex(rp66v1_file, ident=path_in)
        for logical_file in logical_index.logical_files:
            if logical_file.has_log_pass:
                for frame_array in logical_file.log_pass:
                    print(frame_array)
                    frame_count = LogicalFile.populate_frame_array(
                        rp66v1_file, logical_file, frame_array
                    )
                    print(
                        f'Loaded {frame_count} frames and {len(frame_array)} channels'
                        f' from {frame_array.ident} using {frame_array.sizeof_array} bytes.'
                    )
                    for channel in frame_array.channels:
                        print(channel.ident, channel.long_name, channel.units)
                        # channel.array is a numpy array
                        print(f'Min: {channel.array.min():12.3f} Max: {channel.array.max():12.3f}')


def demo_numpy_access_partial():
    with open(path_in, 'rb') as fobj:
        rp66v1_file = File.FileRead(fobj)
        logical_index = LogicalFile.LogicalIndex(rp66v1_file, ident=path_in)
        for logical_file in logical_index.logical_files:
            if logical_file.has_log_pass:
                for frame_array in logical_file.log_pass:
                    # print(frame_array)
                    # print('TRACE:', [c.ident for c in frame_array.channels])
                    frame_count = LogicalFile.populate_frame_array(
                        rp66v1_file, logical_file, frame_array,
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
    # demo_file()
    # demo_logical_files()
    # demo_eflr()
    demo_eflr_contents()
    # demo_numpy_access()
    # demo_numpy_access_partial()
    return 0


if __name__ == '__main__':
    sys.exit(main())
