import abc
import collections
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.RP66V1.core.File import FileLogicalData, FileRead
from TotalDepth.RP66V1.core.LogicalRecord import EFLR, IFLR
from TotalDepth.RP66V1.core.LogicalRecord.LogPass import LogPass
from TotalDepth.RP66V1.core.RepCode import ObjectName


class ExceptionLogicalFile(ExceptionTotalDepthRP66V1):
    pass


class ExceptionLogicalFileCtor(ExceptionLogicalFile):
    pass


class ExceptionLogicalFileAdd(ExceptionLogicalFile):
    pass


class ExceptionLogicalFileMissingRecord(ExceptionLogicalFile):
    pass


# Consists of:
# - File.LogicalRecordPosition
# - EFLR.ExplicitlyFormattedLogicalRecord or EFLR.ExplicitlyFormattedLogicalRecordBase
PositionEFLR = collections.namedtuple('PositionEFLR', 'position, eflr')


class LogicalFileBase():
    """This represents a RP66V1 Logical File.

    From the standard [RP66V1 Definitions]:

    Logical File
        A sequence of two or more contiguous Logical Records in a Storage Set that begins with a File Header Logical
        Record and contains no other File Header Logical Records. A Logical File must have at least one OLR (Origin)
        Logical Record immediately following the File Header Logical Record. A Logical File supports user-level
        organization of data.

    For the File Header Logical Record see [RP66V1 Section 5.1 File Header Logical Record (FHLR)]
    For the Origin Logical Record see [RP66V1 Section 5.2 Origin Logical Record (OLR)]

    This is actually two stage construction with the FHLR first. The OLR is extracted from the first add().
    """
    def __init__(self, file_logical_data: FileLogicalData, fhlr: EFLR.ExplicitlyFormattedLogicalRecord):
        self._check_fld_eflr(file_logical_data, fhlr)
        self.eflrs: typing.List[PositionEFLR] = [
            PositionEFLR(file_logical_data.position, fhlr)
        ]
        # For interpreting IFLRs
        self.eflr_channels: typing.Union[None, EFLR.ExplicitlyFormattedLogicalRecord] = None
        self.eflr_frame: typing.Union[None, EFLR.ExplicitlyFormattedLogicalRecord] = None
        self.log_pass: typing.Union[None, LogPass] = None
        # IFLRs
        self.iflr_positions: typing.Dict[ObjectName, typing.List[int]] = {}

    def _check_fld_eflr(self, file_logical_data: FileLogicalData, fhlr: EFLR.ExplicitlyFormattedLogicalRecord) -> None:
        self._check_fld_matches_eflr(file_logical_data, fhlr)
        if fhlr.lr_type != 0:
            raise ExceptionLogicalFileCtor(
                f'Logical File requires first EFLR code 0 not {str(fhlr.lr_type)}\n{fhlr}'
            )
        if fhlr.set.type != b'FILE-HEADER':
            raise ExceptionLogicalFileCtor(
                f'Logical File requires first EFLR type b\'FILE-HEADER\' not {str(fhlr.set.type)}'
            )

    def _check_fld_matches_eflr(self, file_logical_data: FileLogicalData, fhlr: EFLR.ExplicitlyFormattedLogicalRecord) -> None:
        # TODO: file_logical_data.lr_is_eflr
        pass

    def _add_origin_eflr(self, file_logical_data: FileLogicalData, olr: EFLR.ExplicitlyFormattedLogicalRecord) -> None:
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
    def file_header_logical_record(self):
        assert len(self.eflrs) > 0
        return self.eflrs[0].eflr

    @property
    def origin_logical_record(self):
        if len(self.eflrs) < 2:
            raise ExceptionLogicalFileMissingRecord('Have not yet seen an ORIGIN record.')
        return self.eflrs[1].eflr

    def is_next(self, eflr: EFLR.ExplicitlyFormattedLogicalRecordBase) -> bool:
        return eflr.set.type == b'FILE-HEADER'

    @abc.abstractmethod
    def add_eflr(self, file_logical_data: FileLogicalData, eflr: EFLR.ExplicitlyFormattedLogicalRecordBase, **kwargs) -> None:
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
                self.log_pass = LogPass(self.eflr_frame, self.eflr_channels)
                self.eflr_channels = None
                self.eflr_frame = None

    def _check_fld_iflr(self, file_logical_data: FileLogicalData, iflr: IFLR.IndirectlyFormattedLogicalRecord) -> None:
        # TODO: Check file_logical_data and against iflr.
        if self.origin_logical_record is None:
            raise ExceptionLogicalFileAdd('LogicalFile can not add IFLR before seeing a ORIGIN EFLR.')
        if self.log_pass is None:
            raise ExceptionLogicalFileAdd(
                'LogicalFile can not add IFLR as have not been able to construct'
                ' a LogPass (missing CHANNEL and FRAME records).'
            )
        if len(iflr.bytes) == 0:
            raise ExceptionLogicalFileAdd('LogicalFile can not add empty IFLR.')

    @abc.abstractmethod
    def add_iflr(self, file_logical_data: FileLogicalData, iflr: IFLR.IndirectlyFormattedLogicalRecord, **kwargs) -> None:
        """Child classes should re-implement this but call it all the same with::

            super().add_iflr(file_logical_data, iflr)
        """
        self._check_fld_iflr(file_logical_data, iflr)
        if iflr.object_name in self.iflr_positions:
            self.iflr_positions[iflr.object_name].append(file_logical_data.position.lrsh_position)
        else:
            self.iflr_positions[iflr.object_name] = [file_logical_data.position.lrsh_position]


class LogicalFileSequence(abc.ABC):
    def __init__(self, fobj: typing.BinaryIO, path: str, **kwargs):
        self.logical_files: typing.List[LogicalFileBase] = []
        self.path = path
        rp66_file = FileRead(fobj)
        self.storage_unit_label = rp66_file.sul
        # Capture all the Visible Records, this can not be done by looking at the Logical Records only
        # as some Visible Records can be missed.
        self.visible_record_positions = [vr.position for vr in rp66_file.iter_visible_records()]
        # Now iterate across the file again for the Logical Records.
        for file_logical_data in rp66_file.iter_logical_records():
            self.add_logical_data(file_logical_data, **kwargs)

    def add_logical_data(self, file_logical_data: FileLogicalData, **kwargs) -> None:
        if not file_logical_data.lr_is_encrypted:
            if file_logical_data.lr_is_eflr:
                eflr = self.create_eflr(file_logical_data)
                if len(self.logical_files) == 0 or self.logical_files[-1].is_next(eflr):
                    self.logical_files.append(self.create_logical_file(file_logical_data, eflr, **kwargs))
                else:
                    self.logical_files[-1].add_eflr(file_logical_data, eflr, **kwargs)
            else:
                # IFLRs
                assert len(self.logical_files) > 0
                iflr = IFLR.IndirectlyFormattedLogicalRecord(file_logical_data.lr_type, file_logical_data.logical_data)
                if len(iflr.bytes) > 0:
                    self.logical_files[-1].add_iflr(file_logical_data, iflr, **kwargs)
                # else:
                #     self.logger.warning(f'Ignoring empty IFLR at {file_logical_data.position}')

    @abc.abstractmethod
    def create_logical_file(self,
                            file_logical_data: FileLogicalData,
                            eflr: EFLR.ExplicitlyFormattedLogicalRecord, **kwargs) -> LogicalFileBase:
        """Overload this to create the specialisation of a LogicalFileBase."""
        pass

    @abc.abstractmethod
    def create_eflr(self, file_logical_data: FileLogicalData, **kwargs) -> EFLR.ExplicitlyFormattedLogicalRecordBase:
        """Overload this to create specific EFLRs of interest."""
        pass

    @property
    def current_logical_file(self) -> LogicalFileBase:
        return self.logical_files[-1]
