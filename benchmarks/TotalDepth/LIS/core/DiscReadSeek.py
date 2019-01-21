import io

from benchmarks.TotalDepth.LIS.core import check_binary_files, binary_size, binary_path


class DiskRead:
    # Read buffer sizes
    # [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
    params = [2**i for i in range(14)]

    def setup(self, arg):
        check_binary_files()

    def time_read(self, arg):
        file_name = binary_path(20)
        with open(file_name, 'rb') as f:
            while 1:
                b = f.read(arg)
                if len(b) != arg:
                    break


class DiskSeek:
    # Seek sizes
    # [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
    params = [2**i for i in range(14)]

    def setup(self, arg):
        check_binary_files()

    def time_seek(self, arg):
        file_name = binary_path(20)
        with open(file_name, 'rb') as f:
            while f.seek(arg, io.SEEK_CUR) < binary_size(20):
                pass


class DiskSeekEOFSpecial:

    def time_seek_eof(self):
        file_name = binary_path(20)
        with open(file_name, 'rb') as f:
            f.seek(0, io.SEEK_END)

    def time_seek_eof_index(self):
        """
        Open, seek EOF, seek EOF-256, read 256, seek EOF-(2048+256), read 2048 bytes.
        The 256 number is fixed, in practice the 2048 number would come from reading the 256 bytes.

        Possible use of writing a binary index at the end of the file where two Logical Records are written at the end
        of the file. Both records are some binary type (externally defined). The first one is a variable length record
        that contains the index in binary form. This is followed by a fixed length record that contains the file
        position of the first record.

        A reader would .seek(-256, io.SEEK_END), read the record, discover the file position of the index, seek there
        and read the index. These operations should be O(1) and fast.
        """
        file_name = binary_path(20)
        with open(file_name, 'rb') as f:
            f.seek(-256, io.SEEK_END)
            f.read(256)
            f.seek(-(256 + 2048), io.SEEK_END)
            f.read(2048)
