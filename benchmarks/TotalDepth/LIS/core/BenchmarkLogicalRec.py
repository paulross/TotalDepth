
from TotalDepth.LIS.core import File
from TotalDepth.LIS.core import LogiRec

from benchmarks.TotalDepth.LIS.core import write_logical_data_to_physical_records


class BenchmarkMarkerRecords:
    params = [0x89, 0x8A, 0x8B, 0x8D]
    class_map = {
        0x89 : LogiRec.LrEOFRead,
        0x8A : LogiRec.LrBOTRead,
        0x8B : LogiRec.LrEOTRead,
        0x8D : LogiRec.LrEOMRead,
    }

    def setup(self, arg):
        b = bytearray()
        b.append(arg)
        b.append(0)
        file_obj = write_logical_data_to_physical_records([bytes(b)])
        self.file_read = File.FileRead(theFile=file_obj, theFileId='MyFile', keepGoing=True)
        self.read_class = self.class_map[arg]

    def teardown(self, arg):
        del self.file_read
        del self.read_class

    def time_read(self, arg):
        self.file_read.rewind()
        self.read_class(self.file_read)


class BenchmarkFileHead:

    def setup(self):
        logical_bytes = (
            # Type 128
            b'\x80\x00'
            # File name 6.3 format
            + b'RUNOne.lis'
            # Two blanks
            + b'\x00\x00'
            # Service sub-level name
            + b'SubLev'
            # Version number
            + b'Vers num'
            # Date
            + b'78/03/15'
            # One blank
            + b'\x00'
            # Max Physical record length
            + b' 1024'
            # Two blanks
            + b'\x00\x00'
            # File Type
            + b'\x41\x42'
            # Two blanks
            + b'\x00\x00'
            # Previous file name
            + b'Prev name.'
        )
        file_bytes = write_logical_data_to_physical_records([logical_bytes,])
        self.file_read = File.FileRead(theFile=file_bytes, theFileId='MyFile', keepGoing=True)

    def teardown(self):
        del self.file_read

    def time_read(self):
        self.file_read.rewind()
        LogiRec.LrFileHeadRead(self.file_read)


class BenchmarkFileTail:

    def setup(self):
        logical_bytes = (
            # Type 129
            b'\x81\x00'
            # File name 6.3 format
            + b'RUNOne.lis'
            # Two blanks
            + b'\x00\x00'
            # Service sub-level name
            + b'SubLev'
            # Version number
            + b'Vers num'
            # Date
            + b'78/03/15'
            # One blank
            + b'\x00'
            # Max Physical record length
            + b' 1024'
            # Two blanks
            + b'\x00\x00'
            # File Type
            + b'\x41\x42'
            # Two blanks
            + b'\x00\x00'
            # Previous file name
            + b'Prev name.'
        )
        file_bytes = write_logical_data_to_physical_records([logical_bytes,])
        self.file_read = File.FileRead(theFile=file_bytes, theFileId='MyFile', keepGoing=True)

    def teardown(self):
        del self.file_read

    def time_read(self):
        self.file_read.rewind()
        LogiRec.LrFileTailRead(self.file_read)


class BenchmarkTapeHead:

    def setup(self):
        logical_bytes = (
            # Type 130
            b'\x82\x00'
            # Service name
            + b'SERVCE'
            #
            + b'\x00\x00\x00\x00\x00\x00'
            #
            + b'79/06/15'
            #
            + b'\x00\x00'
            # Origin
            + b'ORGN'
            #
            + b'\x00\x00'
            # Tape name
            + b'TAPENAME'
            #
            + b'\x00\x00'
            # Tape continuation number
            + b'01'
            #
            + b'\x00\x00'
            # Previous tape name
            + b'PrevName'
            #
            + b'\x00\x00'
            # Comments, 74 characters
            + b'_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123'
        )
        file_bytes = write_logical_data_to_physical_records([logical_bytes,])
        self.file_read = File.FileRead(theFile=file_bytes, theFileId='MyFile', keepGoing=True)

    def teardown(self):
        del self.file_read

    def time_read(self):
        self.file_read.rewind()
        LogiRec.LrTapeHeadRead(self.file_read)


class BenchmarkTapeTail:

    def setup(self):
        logical_bytes = (
            # Type 131
            b'\x83\x00'
            # Service name
            + b'SERVCE'
            #
            + b'\x00\x00\x00\x00\x00\x00'
            #
            + b'79/06/15'
            #
            + b'\x00\x00'
            # Origin
            + b'ORGN'
            #
            + b'\x00\x00'
            # Tape name
            + b'TAPENAME'
            #
            + b'\x00\x00'
            # Tape continuation number
            + b'01'
            #
            + b'\x00\x00'
            # Previous tape name
            + b'PrevName'
            #
            + b'\x00\x00'
            # Comments, 74 characters
            + b'_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123'
        )
        file_bytes = write_logical_data_to_physical_records([logical_bytes,])
        self.file_read = File.FileRead(theFile=file_bytes, theFileId='MyFile', keepGoing=True)

    def teardown(self):
        del self.file_read

    def time_read(self):
        self.file_read.rewind()
        LogiRec.LrTapeTailRead(self.file_read)


class BenchmarkReelHead:

    def setup(self):
        logical_bytes = (
            # Type 132
            b'\x84\x00'
            # Service name
            + b'SERVCE'
            #
            + b'\x00\x00\x00\x00\x00\x00'
            #
            + b'79/06/15'
            #
            + b'\x00\x00'
            # Origin
            + b'ORGN'
            #
            + b'\x00\x00'
            # Reel name
            + b'REELNAME'
            #
            + b'\x00\x00'
            # Reel continuation number
            + b'01'
            #
            + b'\x00\x00'
            # Previous reel name
            + b'PrevName'
            #
            + b'\x00\x00'
            # Comments, 74 characters
            + b'_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123'
        )
        file_bytes = write_logical_data_to_physical_records([logical_bytes,])
        self.file_read = File.FileRead(theFile=file_bytes, theFileId='MyFile', keepGoing=True)

    def teardown(self):
        del self.file_read

    def time_read(self):
        self.file_read.rewind()
        LogiRec.LrReelHeadRead(self.file_read)


class BenchmarkReelTail:

    def setup(self):
        logical_bytes = (
            # Type 133
            b'\x85\x00'
            # Service name
            + b'SERVCE'
            #
            + b'\x00\x00\x00\x00\x00\x00'
            #
            + b'79/06/15'
            #
            + b'\x00\x00'
            # Origin
            + b'ORGN'
            #
            + b'\x00\x00'
            # Reel name
            + b'REELNAME'
            #
            + b'\x00\x00'
            # Reel continuation number
            + b'01'
            #
            + b'\x00\x00'
            # Previous reel name
            + b'NextName'
            #
            + b'\x00\x00'
            # Comments, 74 characters
            + b'_123456789_123456789_123456789_123456789_123456789_123456789_123456789_123'
        )
        file_bytes = write_logical_data_to_physical_records([logical_bytes,])
        self.file_read = File.FileRead(theFile=file_bytes, theFileId='MyFile', keepGoing=True)

    def teardown(self):
        del self.file_read

    def time_read(self):
        self.file_read.rewind()
        LogiRec.LrReelTailRead(self.file_read)


# Debugging...
if __name__ == '__main__':
    b = BenchmarkMarkerRecords()
    b.setup(0x89)
    b.time_marker_read(0x89)
    b.teardown(0x89)
    b = BenchmarkFileHead()
    b.setup()
    b.time_file_head_read()
    b.teardown()
