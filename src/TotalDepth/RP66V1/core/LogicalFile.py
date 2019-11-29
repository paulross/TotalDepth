"""
Represents a RP66V1 file as a 'logical' level.

"""


import bisect
import collections
import io
import logging
import pickle
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core.LogicalRecord import EFLR
from TotalDepth.RP66V1.core.LogicalRecord import IFLR
from TotalDepth.RP66V1.core import File, Index
from TotalDepth.RP66V1.core import RepCode
from TotalDepth.RP66V1.core import LogPass
from TotalDepth.RP66V1.core import XAxis
from TotalDepth.RP66V1.core.LogicalRecord.Duplicates import DuplicateObjectStrategy
from TotalDepth.common import Slice

logger = logging.getLogger(__file__)


class ExceptionLogicalFile(ExceptionTotalDepthRP66V1):
    pass


class ExceptionLogicalFileCtor(ExceptionLogicalFile):
    pass


class ExceptionLogicalFileAdd(ExceptionLogicalFile):
    pass


class ExceptionLogicalFileMissingData(ExceptionLogicalFile):
    pass


class ExceptionLogicalIndex(ExceptionLogicalFile):
    pass


class ExceptionLogicalIndexCtor(ExceptionLogicalIndex):
    pass


class PositionEFLR(typing.NamedTuple):
    """POD class that represents the Logical Record Segment Header position in the file of the Explicitly Formatted
    Logical Record and the EFLR itself."""
    lrsh_position: File.LogicalRecordPosition
    eflr: EFLR.ExplicitlyFormattedLogicalRecord


class LogicalFile:
    """This represents a RP66V1 Logical File.

    From the standard [RP66V1 Definitions]:

    Logical File
        A sequence of two or more contiguous Logical Records in a Storage Set that begins with a File Header Logical
        Record and contains no other File Header Logical Records. A Logical File must have at least one OLR (Origin)
        Logical Record immediately following the File Header Logical Record. A Logical File supports user-level
        organization of data.

    For the File Header Logical Record see [RP66V1 Section 5.1 File Header Logical Record (FHLR)]
    For the Origin Logical Record see [RP66V1 Section 5.2 Origin Logical Record (OLR)]

    This is actually two/multi stage construction with the FHLR first. The OLR is extracted from the first add().

    TODO: Check the FHLR references the ORIGIN record. [RP66V1 Section 5.1 File Header Logical Record (FHLR)]:
    "The Origin Subfield of the Name of the File-Header Object must reference the Defining Origin (see §5.2.1)."
    Is this done in practice?

    TODO: Handle multiple ORIGIN records. This is actually allowed in the standard: "A Logical File must have at least
        one OLR (Origin) Logical Record immediately following the File Header Logical Record".

    TODO: Handle multiple CHANNEL records in a Logical File.
    """
    DUPE_EFLR_CHANNEL_STRATEGY = DuplicateObjectStrategy.REPLACE
    DUPE_EFLR_CHANNEL_LOGGER = logger.warning
    ALLOWABLE_ORIGIN_SET_TYPES = (b'ORIGIN', b'WELL-REFERENCE')

    def __init__(self, file_logical_data: File.FileLogicalData, fhlr: EFLR.ExplicitlyFormattedLogicalRecord):
        if fhlr.lr_type != 0:
            raise ExceptionLogicalFileCtor(
                f'Logical File requires first EFLR code 0 not {str(fhlr.lr_type)}\n{fhlr}'
            )
        if fhlr.set.type != b'FILE-HEADER':
            raise ExceptionLogicalFileCtor(
                f'Logical File requires first EFLR type b\'FILE-HEADER\' not {str(fhlr.set.type)}'
            )
        self._check_fld_matches_eflr(file_logical_data, fhlr)
        self.eflrs: typing.List[PositionEFLR] = [
            PositionEFLR(file_logical_data.position, fhlr)
        ]
        # Multiple origins are allowed by the standard, this references the last one.
        self.origin_index: int = -1
        # For interpreting IFLRs
        self.eflr_channels: typing.Union[None, EFLR.ExplicitlyFormattedLogicalRecord] = None
        self.eflr_frame: typing.Union[None, EFLR.ExplicitlyFormattedLogicalRecord] = None
        self.log_pass: typing.Union[None, LogPass.LogPass] = None
        self.iflr_position_map: typing.Dict[RepCode.ObjectName, XAxis.XAxis] = {}

    def _check_fld_matches_eflr(self, file_logical_data: File.FileLogicalData,
                                eflr: EFLR.ExplicitlyFormattedLogicalRecord) -> None:
        if file_logical_data.lr_type != eflr.lr_type:
            raise ExceptionLogicalFile(
                f'File logical data LR type {file_logical_data.lr_type} does not match {eflr.lr_type}'
            )

    def _add_origin_eflr(self, file_logical_data: File.FileLogicalData, olr: EFLR.ExplicitlyFormattedLogicalRecord) -> None:
        # assert self.origin_logical_record is None
        assert self.eflr_channels is None
        assert self.eflr_frame is None
        if olr.lr_type != 1:
            raise ExceptionLogicalFileAdd(
                f'Logical File requires second EFLR code 1 not {str(olr.lr_type)}'
            )
        if olr.set.type not in self.ALLOWABLE_ORIGIN_SET_TYPES:
            raise ExceptionLogicalFileAdd(
                f'Logical File requires second EFLR type b\'ORIGIN\' or b\'WELL-REFERENCE\' not {str(olr.set.type)}'
            )
        if len(self.eflrs) != 1:
            raise ExceptionLogicalFileAdd(f'One or more EFLRs between the FILE-HEADER and ORIGIN.')
        self.eflrs.append(PositionEFLR(file_logical_data.position, olr))

    @property
    def file_header_logical_record(self) -> EFLR.ExplicitlyFormattedLogicalRecord:
        """Returns the FILE-HEADER EFLR."""
        assert len(self.eflrs) > 0
        return self.eflrs[0].eflr

    @property
    def origin_logical_record(self) -> EFLR.ExplicitlyFormattedLogicalRecord:
        """Returns the ORIGIN EFLR."""
        if len(self.eflrs) < 2:
            raise ExceptionLogicalFileMissingData('Have not yet seen an ORIGIN record.')
        assert self.eflrs[1].eflr.set.type in self.ALLOWABLE_ORIGIN_SET_TYPES
        return self.eflrs[1].eflr

    @property
    def defining_origin(self) -> EFLR.Object:
        """Returns the Defining Origin of the Logical File. This is the first row of the ORIGIN Logical Record.
        From [RP66V1 Section 5.2.1 Origin Objects]:
        "The first Object in the first ORIGIN Set is the Defining Origin for the Logical File in which it is contained,
        and the corresponding Logical File is called the Origin's Parent File.
        It is intended that no two Logical Files will ever have Defining Origins with all Attribute Values identical."
        """
        origin = self.origin_logical_record
        if len(origin) == 0:
            raise ExceptionLogicalFileMissingData('ORIGIN record is empty.')
        return origin.objects[0]

    @property
    def has_log_pass(self) -> bool:
        """Return True if a log pass has been created from a CHANNEL and a FRAME record."""
        return self.log_pass is not None

    @staticmethod
    def is_next(eflr: EFLR.ExplicitlyFormattedLogicalRecord) -> bool:
        """Returns True if the given EFLR belongs to the next Logical Record."""
        return eflr.set.type == b'FILE-HEADER'

    def add_eflr(self, file_logical_data: File.FileLogicalData, eflr: EFLR.ExplicitlyFormattedLogicalRecord) -> None:
        """Adds an EFLR in sequence from the file.

        Will raise a ``ExceptionLogicalFileAdd`` if the EFLR is a ``FILE-HEADER`` as that signals the next Logical File.
        """
        if self.is_next(eflr):
            raise ExceptionLogicalFileAdd(f'Can not add EFLR code {eflr.lr_type}, type {eflr.set.type}')
        self._check_fld_matches_eflr(file_logical_data, eflr)
        if len(self.eflrs) < 2:
            self._add_origin_eflr(file_logical_data, eflr)
        else:
            if eflr.set.type in (b'FILE-HEADER', b'ORIGIN', b'WELL-REFERENCE'):
                msg = f'Logical File encountered multiple EFLRs {str(eflr.set.type)} LR type: {eflr.lr_type}'
                # raise ExceptionLogicalFileAdd(msg)
                logger.warning(msg)
            self.eflrs.append(PositionEFLR(file_logical_data.position, eflr))
            # Extract specific EFLRs for interpreting IFLRs
            if eflr.set.type == b'CHANNEL':
                if self.eflr_channels is not None or self.log_pass is not None:
                    raise ExceptionLogicalFileAdd(f'Multiple CHANNEL EFLRs in a Logical File.')
                self.eflr_channels = eflr
            elif eflr.set.type == b'FRAME':
                if self.eflr_frame is not None or self.log_pass is not None:
                    raise ExceptionLogicalFileAdd(f'Multiple FRAME EFLRs in a Logical File.')
                self.eflr_frame = eflr
            # If the data is now there then construct a LogPass
            if self.eflr_channels is not None and self.eflr_frame is not None:
                assert self.log_pass is None
                self.log_pass = LogPass.log_pass_from_RP66V1(self.eflr_frame, self.eflr_channels)
                self.eflr_channels = None
                self.eflr_frame = None

    def _check_fld_iflr(self, file_logical_data: File.FileLogicalData, iflr: IFLR.IndirectlyFormattedLogicalRecord) -> None:
        # TODO: Check file_logical_data and against iflr.
        if self.origin_logical_record is None:
            raise ExceptionLogicalFileAdd('LogicalFile can not add IFLR before seeing a ORIGIN EFLR.')
        if self.log_pass is None:
            raise ExceptionLogicalFileAdd(
                'LogicalFile can not add IFLR as have not been able to construct'
                ' a LogPass.LogPassDLIS (missing CHANNEL and FRAME records).'
            )
        if iflr.remain == 0:
            raise ExceptionLogicalFileAdd('LogicalFile can not add empty IFLR.')

    def add_iflr(self, file_logical_data: File.FileLogicalData, iflr: IFLR.IndirectlyFormattedLogicalRecord) -> None:
        """Adds a IFLR entry to the index. The IFLR just contains the object name and frame number.
        This extracts the X axis from the first value in the IFLR free data and appends this to the
        iflr_position_map.
        """
        self._check_fld_iflr(file_logical_data, iflr)
        frame_array: LogPass.FrameArray = self.log_pass[iflr.object_name]
        frame_array.read_x_axis(file_logical_data.logical_data, frame_number=0)
        if iflr.object_name not in self.iflr_position_map:
            self.iflr_position_map[iflr.object_name] = XAxis.XAxis(
                frame_array.x_axis.ident,
                frame_array.x_axis.long_name,
                frame_array.x_axis.units,
            )
        self.iflr_position_map[iflr.object_name].append(
            file_logical_data.position,
            iflr.frame_number,
            frame_array.x_axis.array.mean(),
        )


# class VisibleRecordPositions(collections.UserList):
#
#     def visible_record_prior(self, lrsh_position: int) -> int:
#         """Find rightmost value of visible record position less than the lrsh position.
#
#         See: python-3.7.2rc1-docs-html/library/bisect.html#module-bisect "Searching Sorted Lists",
#         example function find_lt().
#         """
#         i = bisect.bisect_left(self.data, lrsh_position)
#         if i:
#             return self.data[i - 1]
#         if len(self) == 0:
#             msg = f'No Visible Record positions for LRSH position {lrsh_position}.'
#         else:
#             msg = f'Can not find Visible Record position prior to {lrsh_position}, earliest is {self[0]}.'
#         raise ValueError(msg)


class LogicalIndex:
    """This takes a RP66V1 file and indexes it into a sequence of Logical Files."""
    def __init__(self, path_or_file: typing.Union[str, io.BytesIO]):
        self.logical_files: typing.List[LogicalFile] = []
        self.logical_record_index = Index.LogicalRecordIndex(path_or_file)

    def __len__(self) -> int:
        return len(self.logical_files)

    def __enter__(self):
        self.logical_record_index._enter()
        self.logical_files = []
        for lr_index in range(len(self.logical_record_index)):
            file_logical_data = self.logical_record_index.get_file_logical_data(lr_index, 0, -1)
            assert file_logical_data.is_sealed()
            if not file_logical_data.lr_is_encrypted:
                if file_logical_data.lr_is_eflr:
                    # EFLRs
                    eflr = EFLR.ExplicitlyFormattedLogicalRecord(file_logical_data.lr_type,
                                                                 file_logical_data.logical_data)
                    if len(self.logical_files) == 0 or self.logical_files[-1].is_next(eflr):
                        self.logical_files.append(LogicalFile(file_logical_data, eflr))
                    else:
                        self.logical_files[-1].add_eflr(file_logical_data, eflr)
                else:
                    # IFLRs
                    if len(self.logical_files) == 0:
                        raise ExceptionLogicalIndexCtor('IFLR when there are no Logical Files.')
                    iflr = IFLR.IndirectlyFormattedLogicalRecord(file_logical_data.lr_type,
                                                                 file_logical_data.logical_data)
                    if iflr.remain > 0:
                        self.logical_files[-1].add_iflr(file_logical_data, iflr)
                    # else:
                    #     logger.warning(f'Ignoring empty IFLR at {file_logical_data.position}')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logical_record_index._exit()
        self.logical_files = []
        return False


def unpickle(path: str) -> LogicalIndex:
    with open(path, 'rb') as in_stream:
        return pickle.loads(in_stream.read())


def populate_frame_array(
        logical_file: LogicalFile,
        frame_array: LogPass.FrameArray,
        frame_slice: typing.Union[Slice.Slice, Slice.Split, None] = None,
        channels: typing.Union[typing.Set[typing.Hashable], None] = None,
) -> int:
    """Populates a FrameArray with channel values.

    rp66_file is the Raw file.
    logical_file is the LogicalFile in that raw file.
    frame_array is the identified FrameArray in that LogPass of FrameArrays in that LogicalFile. This will be populated.
    frame_slice Allows partial population in the X axis.
    channels Allows partial population of specific channels.

    This returns the number of frames populated.
    """
    iflrs = logical_file.iflr_position_map[frame_array.ident]
    if len(iflrs):
        # Set partial frames
        if frame_slice is not None:
            range_gen = frame_slice.range(len(iflrs))
            num_frames = frame_slice.count(len(iflrs))
        else:
            range_gen = range(len(iflrs))
            num_frames = len(iflrs)
        # Set partial channels
        if channels is not None:
            frame_array.init_arrays_partial(num_frames, channels)
        else:
            frame_array.init_arrays(num_frames)
        # Now populate
        logger.debug(f'populate_frame_array(): len(iflrs): {len(iflrs)} slice: {frame_slice}'
                     f' num_frames: {num_frames} range_gen: {range_gen}.')
        for array_index, frame_number in enumerate(range_gen):
            iflr_reference = iflrs[frame_number]
            # FIXME: Get the data from the LogicalIndex
            # FIXME: Change the IFLR reference to be the index into LogicalIndex Logical Records
            fld: File.FileLogicalData = logical_file.get_file_logical_data_at_position(
                iflr_reference.logical_record_position
            )
            # Create an IFLR but we don't use it, just the remaining bytes in the Logical Data.
            iflr = IFLR.IndirectlyFormattedLogicalRecord(fld.lr_type, fld.logical_data)
            if channels is not None:
                frame_array.read_partial(fld.logical_data, array_index, channels)
            else:
                frame_array.read(fld.logical_data, array_index)
    else:
        num_frames = 0
        frame_array.init_arrays(num_frames)
    return num_frames
