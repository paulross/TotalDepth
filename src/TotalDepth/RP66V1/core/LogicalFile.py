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

    def __init__(self, logical_record_index: Index.LogicalRecordIndex,
                 file_logical_data: File.FileLogicalData,
                 fhlr: EFLR.ExplicitlyFormattedLogicalRecord):
        if fhlr.lr_type != 0:
            raise ExceptionLogicalFileCtor(
                f'Logical File requires first EFLR code 0 not {str(fhlr.lr_type)}\n{fhlr}'
            )
        if fhlr.set.type != b'FILE-HEADER':
            raise ExceptionLogicalFileCtor(
                f'Logical File requires first EFLR type b\'FILE-HEADER\' not {str(fhlr.set.type)}'
            )
        self._check_fld_matches_eflr(file_logical_data, fhlr)
        # Take a reference to the low-level index which we need in conjunction with iflr_position_map to get random
        # access to the IFLRs that belong to this Logical File.
        self._logical_record_index= logical_record_index
        self.eflrs: typing.List[PositionEFLR] = [
            PositionEFLR(file_logical_data.position, fhlr)
        ]
        # Multiple origins are allowed by the standard, this references the last one.
        self.origin_index: int = -1
        # For interpreting IFLRs
        self.channel: typing.Union[None, EFLR.ExplicitlyFormattedLogicalRecord] = None
        self.frame: typing.Union[None, EFLR.ExplicitlyFormattedLogicalRecord] = None
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
        assert self.channel is None
        assert self.frame is None
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
        """Returns the FILE-HEADER EFLR see [RP66V1 Section 5.1 File Header Logical Record (FHLR)]."""
        assert len(self.eflrs) > 0
        return self.eflrs[0].eflr

    @property
    def origin_logical_record(self) -> EFLR.ExplicitlyFormattedLogicalRecord:
        """Returns the ORIGIN EFLR see [RP66V1 Section 5.2 Origin Logical Record (OLR)]."""
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
        """Return True if a log pass has been created from a CHANNEL and a FRAME record and some relevant IFLRs."""
        if self.log_pass is None:
            return False
        frame_array_iflr_counts = []
        for frame_array in self.log_pass.frame_arrays:
            if frame_array.ident in self.iflr_position_map:
                frame_array_iflr_counts.append(len(self.iflr_position_map[frame_array.ident]))
            else:
                frame_array_iflr_counts.append(0)
        return sum(frame_array_iflr_counts) > 0

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
                if self.channel is not None or self.log_pass is not None:
                    raise ExceptionLogicalFileAdd(f'Multiple CHANNEL EFLRs in a Logical File.')
                self.channel = eflr
            elif eflr.set.type == b'FRAME':
                if self.frame is not None or self.log_pass is not None:
                    raise ExceptionLogicalFileAdd(f'Multiple FRAME EFLRs in a Logical File.')
                self.frame = eflr
            # If the data is now there then construct a LogPass
            if self.channel is not None and self.frame is not None:
                if self.log_pass is None:
                    self.log_pass = LogPass.log_pass_from_RP66V1(self.frame, self.channel)

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

    def num_frames(self, frame_array: LogPass.FrameArray) -> int:
        """Return the number of frames in the FrameArray"""
        return len(self.iflr_position_map[frame_array.ident])

    def populate_frame_array(
            self,
            frame_array: LogPass.FrameArray,
            frame_slice: typing.Union[Slice.Slice, Slice.Sample, None] = None,
            channels: typing.Union[typing.Set[typing.Hashable], None] = None,
    ) -> int:
        """Populates a FrameArray with channel values.

        frame_array must be a member of the LogPass in thisLogicalFile.

        frame_slice Allows partial population in the X axis.

        channels Allows partial population of specific channels.

        The FrameArray will be populated and this returns the number of frames populated.
        """
        if self.log_pass is None:
            raise ExceptionLogicalFile(f'populate_frame_array(): when no Log Pass')
        if not id(frame_array) in [id(v) for v in self.log_pass.frame_arrays]:
            raise ExceptionLogicalFile(f'populate_frame_array(): given FrameArray is not in Log Pass')
        iflrs: XAxis.XAxis = self.iflr_position_map[frame_array.ident]
        if len(iflrs):
            # Set partial frames
            if frame_slice is not None:
                range_gen = frame_slice.gen_indices(len(iflrs))
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
                fld: File.FileLogicalData = self._logical_record_index.get_file_logical_data_at_position(
                    iflr_reference.logical_record_position
                )
                # Create an IFLR but we don't use it, just the remaining bytes in the Logical Data.
                _iflr = IFLR.IndirectlyFormattedLogicalRecord(fld.lr_type, fld.logical_data)
                if channels is not None:
                    frame_array.read_partial(fld.logical_data, array_index, channels)
                else:
                    frame_array.read(fld.logical_data, array_index)
        else:
            num_frames = 0
            frame_array.init_arrays(num_frames)
        return num_frames


class LogicalIndex:
    """This takes a RP66V1 file and indexes it into a sequence of Logical Files."""
    def __init__(self, path_or_file: typing.Union[str, typing.BinaryIO]):
        self.logical_files: typing.List[LogicalFile] = []
        # A reference to this is given to every LogicalFile
        self._logical_record_index = Index.LogicalRecordIndex(path_or_file)

    def __len__(self) -> int:
        """Returns the number of Logical Files."""
        return len(self.logical_files)

    def __getitem__(self, item) -> LogicalFile:
        """Returns the Logical Files at position item."""
        return self.logical_files[item]

    @property
    def id(self) -> str:
        return str(self._logical_record_index.path)

    @property
    def storage_unit_label(self) -> File.StorageUnitLabel:
        """The Storage Unit Label. This comes from the LogicalRecordIndex."""
        return self._logical_record_index.sul

    @property
    def visible_record_positions(self) -> typing.List[int]:
        """A list of Visible Record positions. This is used by the XML index for example."""
        return self._logical_record_index.visible_record_positions

    def __enter__(self):
        """Context manager support."""
        self._logical_record_index._enter()
        self.logical_files = []
        for lr_index in range(len(self._logical_record_index)):
            # TODO: This is greedy and for IFLRs we could only read a partial amount for performance.
            #  See FrameArray.x_axis_len_input_bytes
            file_logical_data = self._logical_record_index.get_file_logical_data(lr_index, 0, -1)
            assert file_logical_data.is_sealed()
            if not file_logical_data.lr_is_encrypted:
                if file_logical_data.lr_is_eflr:
                    # EFLRs
                    eflr = EFLR.ExplicitlyFormattedLogicalRecord(file_logical_data.lr_type,
                                                                 file_logical_data.logical_data)
                    if len(self.logical_files) == 0 or self.logical_files[-1].is_next(eflr):
                        self.logical_files.append(LogicalFile(self._logical_record_index, file_logical_data, eflr))
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
        """Context manager support."""
        self._logical_record_index._exit()
        self.logical_files = []
        return False
