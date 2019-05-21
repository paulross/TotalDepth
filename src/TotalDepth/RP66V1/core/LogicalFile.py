import abc
import bisect
import collections
import logging
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR
from TotalDepth.RP66V1.core import LogPass, File, RepCode


logger = logging.getLogger(__file__)


class ExceptionLogicalFile(ExceptionTotalDepthRP66V1):
    pass


class ExceptionLogicalFileCtor(ExceptionLogicalFile):
    pass


class ExceptionLogicalFileAdd(ExceptionLogicalFile):
    pass


class ExceptionLogicalFileMissingData(ExceptionLogicalFile):
    pass


class ExceptionLogicalFileSequence(ExceptionLogicalFile):
    pass


class ExceptionLogicalFileSequenceCtor(ExceptionLogicalFileSequence):
    pass


class PositionEFLR(typing.NamedTuple):
    """POD class that represents the Logical Record Segment Header position in the file of the Explicitly Formatted
    Logical Record and the EFLR itself."""
    lrsh_position: File.LogicalRecordPosition
    eflr: EFLR.ExplicitlyFormattedLogicalRecord


class IFLRData(typing.NamedTuple):
    """POD class that represents the position of the IFLR in the file."""
    frame_number: int
    lrsh_position: int
    x_axis: typing.Union[int, float]


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
    """
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
        # For interpreting IFLRs
        self.eflr_channels: typing.Union[None, EFLR.ExplicitlyFormattedLogicalRecord] = None
        self.eflr_frame: typing.Union[None, EFLR.ExplicitlyFormattedLogicalRecord] = None
        self.log_pass: typing.Union[None, LogPass.LogPass] = None
        self.iflr_position_map: typing.Dict[RepCode.ObjectName, typing.List[IFLRData]] = {}


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
        if olr.set.type not in (b'ORIGIN', b'WELL-REFERENCE'):
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
        return self.log_pass is not None

    @staticmethod
    def is_next(eflr: EFLR.ExplicitlyFormattedLogicalRecord) -> bool:
        """Returns True if the given EFLR belongs to the next Logical Record."""
        return eflr.set.type == b'FILE-HEADER'

    def add_eflr(self, file_logical_data: File.FileLogicalData, eflr: EFLR.ExplicitlyFormattedLogicalRecord) -> None:
        if self.is_next(eflr):
            raise ExceptionLogicalFileAdd(f'Can not add EFLR code {eflr.lr_type}, type {eflr.set.type}')
        self._check_fld_matches_eflr(file_logical_data, eflr)
        if len(self.eflrs) < 2:
            self._add_origin_eflr(file_logical_data, eflr)
        else:
            if eflr.set.type in (b'FILE-HEADER', b'ORIGIN', b'WELL-REFERENCE'):
                raise ExceptionLogicalFileAdd(
                    f'Logical File encountered multiple EFLRs {str(eflr.set.type)}'
                )
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
        if iflr.logical_data.remain == 0:
            raise ExceptionLogicalFileAdd('LogicalFile can not add empty IFLR.')

    def add_iflr(self, file_logical_data: File.FileLogicalData, iflr: IFLR.IndirectlyFormattedLogicalRecord) -> None:
        """
        """
        self._check_fld_iflr(file_logical_data, iflr)
        self.log_pass[iflr.object_name].read_x_axis(iflr.logical_data, frame_number=0)
        x_value = self.log_pass[iflr.object_name].channels[0].array.mean()
        iflr_data = IFLRData(iflr.frame_number, file_logical_data.position.lrsh_position, x_value)
        if iflr.object_name in self.iflr_position_map:
            self.iflr_position_map[iflr.object_name].append(iflr_data)
        else:
            self.iflr_position_map[iflr.object_name] = [iflr_data]


class VisibleRecordPositions(collections.UserList):

    def visible_record_prior(self, lrsh_position: int) -> int:
        """Find rightmost value of visible record position less than the lrsh position.

        See: python-3.7.2rc1-docs-html/library/bisect.html#module-bisect "Searching Sorted Lists",
        example function find_lt().
        """
        i = bisect.bisect_left(self.data, lrsh_position)
        if i:
            return self.data[i - 1]
        if len(self) == 0:
            msg = f'No Visible Record positions for LRSH position {lrsh_position}.'
        else:
            msg = f'Can not find Visible Record position prior to {lrsh_position}, earliest is {self[0]}.'
        raise ValueError(msg)


class LogicalFileSequence:
    # TODO: Consider renaming this to FileIndex. See LIS for a compatible name.
    def __init__(self, rp66_file: typing.Union[File.FileRead, None], path: str):
        self.path = path
        self.logical_files: typing.List[LogicalFile] = []
        self.storage_unit_label = None
        self.visible_record_positions: VisibleRecordPositions = VisibleRecordPositions()
        if rp66_file is not None:
            self.storage_unit_label = rp66_file.sul
            # Capture all the Visible Records, this can not be done by looking at the Logical Records only
            # as some Visible Records can be missed.
            self.visible_record_positions = VisibleRecordPositions(
                vr.position for vr in rp66_file.iter_visible_records()
            )
            # Now iterate across the file again for the Logical Records.
            for file_logical_data in rp66_file.iter_logical_records():
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
                            raise ExceptionLogicalFileSequenceCtor('IFLR when there are no Logical Files.')
                        iflr = IFLR.IndirectlyFormattedLogicalRecord(file_logical_data.lr_type,
                                                                     file_logical_data.logical_data)
                        if iflr.logical_data.remain > 0:
                            self.logical_files[-1].add_iflr(file_logical_data, iflr)
                        else:
                            logger.warning(f'Ignoring empty IFLR at {file_logical_data.position}')

    def __len__(self) -> int:
        return len(self.logical_files)

    # def visible_record_prior(self, lrsh_position: int) -> int:
    #     """Find rightmost value of visible record position less than the lrsh position.
    #
    #     See: python-3.7.2rc1-docs-html/library/bisect.html#module-bisect "Searching Sorted Lists",
    #     example function find_lt().
    #     """
    #     i = bisect.bisect_left(self.visible_record_positions, lrsh_position)
    #     if i:
    #         return self.visible_record_positions[i - 1]
    #     raise ValueError


# class FileRandomAccess:
#     def __init__(self, logical_file_sequence: LogicalFileSequence):
#         self.logical_file_sequence = logical_file_sequence
#         self.binary_file: typing.BinaryIO = None
#         self.rp66v1_file: File.FileRead = None
#
#     def __enter__(self):
#         if self.binary_file is not None:
#             self.binary_file.close()
#             self.binary_file = None
#         self.binary_file = open(self.logical_file_sequence.path, 'rb')
#         self.rp66v1_file = File.FileRead(self.binary_file)
#         return self
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if self.binary_file is not None:
#             self.binary_file.close()
#             self.binary_file = None
#         self.rp66v1_file = None
#         return False

