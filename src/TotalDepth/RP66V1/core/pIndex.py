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


class LogicalRecordIndex:
    """This maintains an index of visible record and Logical Record Segment Header (LRSH) positions where the LRSH is
    the first in the Logical Record.

    The index is a list of File.LRPosDesc objects that contain:

        - ``.position`` A LogicalRecordPosition which has the absolute file position of the Visible Record and LRSH.
            This will be of interest to indexers that mean to ``use get_file_logical_data()`` as this is a required
            argument.
        - ``.description`` A LogicalDataDescription which provides some basic information about the Logical Data such as
            the LRSH attributes, Logical Record type and the Logical Data length. This will be of interest to indexers
            to offer up to their callers.
    """
    def __init__(self, path_or_file: typing.Union[str, io.BytesIO]):
        self.lr_pos_desc: typing.List[File.LRPosDesc] = []
        self.rp66v1_file: File.FileRead = File.FileRead(path_or_file)
        self.path = self.rp66v1_file.path

    def __len__(self) -> int:
        return len(self.lr_pos_desc)

    def __getitem__(self, item) -> File.LRPosDesc:
        return self.lr_pos_desc[item]

    def _enter(self):
        """Populate the internal representation from a File.FileRead."""
        # Initialise the File.FileRead
        self.rp66v1_file._enter()
        # Initialise self and scan the File.FileRead
        self.lr_pos_desc = list(self.rp66v1_file.iter_logical_record_positions())

    def __enter__(self):
        self._enter()
        return self

    def _exit(self):
        self.rp66v1_file._exit()
        self.lr_pos_desc = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._exit()
        return False

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['rp66v1_file']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.rp66v1_file = File.FileRead(self.path)

    @property
    def sul(self) -> File.StorageUnitLabel:
        """The file's Storage Unit Label."""
        return self.rp66v1_file.sul

    @property
    def visible_record_positions(self) -> typing.List[int]:
        """A list of Visible Record positions. This is used by the XML index for example."""
        return [v.position.vr_position for v  in self.lr_pos_desc]

    def get_file_logical_data(self, index: int, offset: int = 0, length: int = -1) -> File.FileLogicalData:
        """
        Returns a FileLogicalData object from the Logical Record position in the index (Visible Record Position and
        Logical Record Segment Header position).

        This allows random access to any Logical Record in the file.
        The caller can construct a more sophisticated index such as a sequence of Logical Files which contain Logical
        Records that can be EFLRs or IFLRs and interpreted accordingly.

        If offset or length are use then the result will be the partial data from that offset and length.

        :param: index The index of the Logical Record.
        :param: offset An integer offset into the Logical Record data, default 0.
        :param: length An integer length the Logical Record data, default of -1 is all.
        """
        position: File.LogicalRecordPosition = self.lr_pos_desc[index].position
        return self.rp66v1_file.get_file_logical_data(position, offset, length)

    def get_file_logical_data_at_position(self, position: File.LogicalRecordPositionBase,
                                          offset: int = 0, length: int = -1):
        """
        Returns a FileLogicalData object from the Logical Record position.

        This allows random access to any Logical Record in the file.
        The caller can construct a more sophisticated index such as a sequence of Logical Files which contain Logical
        Records that can be EFLRs or IFLRs and interpreted accordingly.

        If offset or length are use then the result will be the partial data from that offset and length.

        :param: position The Logical Record position in the file.
        :param: offset An integer offset into the Logical Record data, default 0.
        :param: length An integer length the Logical Record data, default of -1 is all.
        """
        return self.rp66v1_file.get_file_logical_data(position, offset, length)

    def validate(self):
        """Perform validation checks."""
        self.rp66v1_file.validate_positions()
