"""
RP66V1 file indexer at the level of Visible Records and the first Logical Record Segment Header.

This allows random access of Logical Record data.

In the taxonomy of indexes this is a 'mid level' index as it indexes:

* Below: Internally it discovers and records Visible Records and Logical Record Segment Headers (where ``is_first()`` is ``True`` ).
* Above: Externally it provides an API to a sequence of Logical Records and the data that makes up those Logical Records.

TODO: Replace this with the C/C++ implementation.
"""
import io
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core import File


class ExceptionIndex(ExceptionTotalDepthRP66V1):
    """Base class for exceptions in this module."""
    pass


class VisibleRecordIndexLRSHPosition(typing.NamedTuple):
    """Contains the Visible Record position and Logical Record Segment Header position and the Logical Data length."""
    vr_index: int
    lrsh_position: int
    lrsh_attributes: File.LogicalRecordSegmentHeaderAttributes
    lr_record_type: int
    logical_data_length: int


class VisibleLogicalSegmentIndex:
    """This maintains an index of visible record and Logical Record Segment Header (LRSH) positions where the LRSH is
    the first in the Logical Record."""
    def __init__(self, file_or_path: typing.Union[str, io.BytesIO]):
        self.visible_record_positions: typing.List[int] = []
        self.lrsh_positions: typing.List[VisibleRecordIndexLRSHPosition] = []
        if isinstance(file_or_path, str):
            self.path = file_or_path
            self.file = None
            self.must_close = True
        elif isinstance(file_or_path, io.BytesIO):
            try:
                self.path = file_or_path.name
            except AttributeError:
                self.path = None
            self.file = file_or_path
            self.must_close = False
        else:
            raise TypeError(f'file_or_path must be a binary file or a string not {type(file_or_path)}')

    def __len__(self):
        return len(self.lrsh_positions)

    def _enter(self):
        # TODO: This needs error checking
        visible_record_index = lrsh_first_position = logical_data_length = None
        for visible_record in self.rp66v1_file.iter_visible_records():
            self.visible_record_positions.append(visible_record.position)
            for lrsh in self.rp66v1_file.iter_LRSHs_for_visible_record(visible_record):
                # print('TRACE:', lrsh)
                if lrsh.is_first:
                    lrsh_first_position = lrsh.position
                    visible_record_index = len(self.visible_record_positions) - 1
                    logical_data_length = 0
                logical_data_length += lrsh.logical_data_length
                if lrsh.is_last:
                    self.lrsh_positions.append(
                        VisibleRecordIndexLRSHPosition(visible_record_index, lrsh_first_position, logical_data_length)
                    )
                    visible_record_index = lrsh_first_position = logical_data_length = None

    def __enter__(self):
        # Initialise the File.FileRead
        # Initialise self and scan the File.FileRead
        return self

    def _exit(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the File.FileRead
        return False

    def get_file_logical_data(self, index: int, offset: int = 0, length: int = -1) -> File.FileLogicalData:
        """
        Returns a FileLogicalData object from the Logical Record position (Visible Record Position and Logical Record
        Segment Header position).
        This allows random access to any Logical Record in the file.
        The caller can construct a more sophisticated index such as a sequence of Logical Files which contain Logical
        Records that can be EFLRs or IFLRs and interpreted accordingly.

        :param: index The index of the Logical Record.
        :param: offset An integer offset into the Logical Record data, default 0.
        :param: length An integer length the Logical Record data, default of -1 is all.
        """
        # TODO: Raise instead of an assert
        assert index >= 0 and index < len(self.lrsh_positions)
        assert 0 <= self.lrsh_positions[index].vr_index < len(self.visible_record_positions)
        # Set up the file to the Logical Record
        vr_position = self.visible_record_positions[self.lrsh_positions[index].vr_index]
        lrsh_position = self.lrsh_positions[index].lrsh_position
        # TODO: Change the design of the LogicalRecordPosition or abandon it in favor of a pair

        return self.file.get_file_logical_data(position, offset, length)


