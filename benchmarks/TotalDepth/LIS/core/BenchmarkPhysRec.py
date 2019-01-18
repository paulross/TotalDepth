import io

from TotalDepth.LIS.core import PhysRec

PHYSICAL_RECORD_BENCHMARK_PARAMETERS = [
    # A triple of:
    #   (
    #       Physical Record length,
    #       Logical Record length,
    #       number of Logical Records
    #   )
    # We expect that the performance should be linear with the last two fields.
    #
    # Some basic dimensions.
    '1024-1024-1',  # 1kB
    # '1024-1024-1024',  # 1MB
    # '1024-1024-8192',  # 8MB
    # LR length of 64 * 1024 = 65536 with 16 of them (2**20 logical bytes, 1MB)  at different
    # PR sizes from 128 bytes up to the maximum 65535
    # '128-65536-16',
    '256-65536-16',
    # '512-65536-16',
    '1024-65536-16',
    '2048-65536-16',
    # '4096-65536-16',
    '8192-65536-16',
    # '16383-65536-16',
    '32768-65536-16',
    '{}-65536-16'.format(PhysRec.PR_MAX_LENGTH),
]


class BenchmarkPhysicalRecordWriteTIFTailChecksum:
    params = PHYSICAL_RECORD_BENCHMARK_PARAMETERS

    def setup(self, arg):
        pr_len, lr_len, lr_count = tuple(int(s) for s in arg.split('-'))
        io_file = io.BytesIO()
        self.pr_writer = PhysRec.PhysRecWrite(
            io_file,
            theFileId='WriteFile',
            keepGoing=False,
            hasTif=True,
            thePrLen=pr_len,
            thePrt=PhysRec.PhysRecTail(
                hasRecNum=True,
                fileNum=42,
                hasCheckSum=True
            ),
        )
        self.logical_data = b'\xff' * lr_len

    def teardown(self, arg):
        del self.pr_writer
        del self.logical_data

    def time_pr_write(self, arg):
        _pr_len, lr_len, lr_count = tuple(int(s) for s in arg.split('-'))
        for i in range(lr_count):
            self.pr_writer.writeLr(self.logical_data)


class BenchmarkPhysicalRecordWriteTIFTailNOChecksum:
    params = PHYSICAL_RECORD_BENCHMARK_PARAMETERS

    def setup(self, arg):
        pr_len, lr_len, lr_count = tuple(int(s) for s in arg.split('-'))
        io_file = io.BytesIO()
        self.pr_writer = PhysRec.PhysRecWrite(
            io_file,
            theFileId='WriteFile',
            keepGoing=False,
            hasTif=True,
            thePrLen=pr_len,
            thePrt=PhysRec.PhysRecTail(
                hasRecNum=True,
                fileNum=42,
                hasCheckSum=False
            ),
        )
        self.logical_data = b'\xff' * lr_len

    def teardown(self, arg):
        del self.pr_writer
        del self.logical_data

    def time_pr_write(self, arg):
        _pr_len, lr_len, lr_count = tuple(int(s) for s in arg.split('-'))
        for i in range(lr_count):
            self.pr_writer.writeLr(self.logical_data)


class BenchmarkPhysicalRecordWriteNOTIFTailNOChecksum:
    params = PHYSICAL_RECORD_BENCHMARK_PARAMETERS

    def setup(self, arg):
        pr_len, lr_len, lr_count = tuple(int(s) for s in arg.split('-'))
        io_file = io.BytesIO()
        self.pr_writer = PhysRec.PhysRecWrite(
            io_file,
            theFileId='WriteFile',
            keepGoing=False,
            hasTif=False,
            thePrLen=pr_len,
            thePrt=PhysRec.PhysRecTail(
                hasRecNum=True,
                fileNum=42,
                hasCheckSum=False
            ),
        )
        self.logical_data = b'\xff' * lr_len

    def teardown(self, arg):
        del self.pr_writer
        del self.logical_data

    def time_pr_write(self, arg):
        _pr_len, lr_len, lr_count = tuple(int(s) for s in arg.split('-'))
        for i in range(lr_count):
            self.pr_writer.writeLr(self.logical_data)


class BenchmarkPhysicalRecordRead:
    params = PHYSICAL_RECORD_BENCHMARK_PARAMETERS

    def setup(self, arg):
        pr_len, lr_len, lr_count = tuple(int(s) for s in arg.split('-'))
        self.io_file = io.BytesIO()
        pr_writer = PhysRec.PhysRecWrite(
            self.io_file,
            theFileId='WriteFile',
            keepGoing=False,
            hasTif=True,
            thePrLen=pr_len,
            thePrt=PhysRec.PhysRecTail(hasRecNum=True, fileNum=42, hasCheckSum=True),
        )
        for i in range(lr_count):
            pr_writer.writeLr(b'\xff' * lr_len)

    def teardown(self, arg):
        del self.io_file

    def time_pr_read(self, arg):
        _pr_len, lr_len, lr_count = tuple(int(s) for s in arg.split('-'))
        pr_read = PhysRec.PhysRecRead(theFile=self.io_file, theFileId='MyFile', keepGoing=False)
        while 1:
            logical_data = pr_read.readLrBytes()
            if logical_data is None:
                break
            assert len(logical_data) == lr_len
            lr_count -= 1
        assert lr_count == 0
