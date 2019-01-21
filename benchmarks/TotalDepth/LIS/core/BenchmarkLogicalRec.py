
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

    def time_marker_read(self, arg):
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

    def time_file_head_read(self):
        self.file_read.rewind()
        LogiRec.LrFileHeadRead(self.file_read)


if __name__ == '__main__':
    b = BenchmarkMarkerRecords()
    b.setup(0x89)
    b.time_marker_read(0x89)
    b.teardown(0x89)

    b = BenchmarkFileHead()
    b.setup()
    b.time_file_head_read()
    b.teardown()
