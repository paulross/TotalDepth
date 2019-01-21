import struct

from TotalDepth.LIS.core import cRepCode, pRepCode, cpRepCode

from benchmarks.TotalDepth.LIS.core import check_binary_files, binary_path


class StructInt:
    # Struct format sizes
    params = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]

    def setup(self, arg):
        check_binary_files()
        self.struct_formats = {
            1       : '>B',
            2       : '>H',
            4       : '>I',
            8       : '>2I',
            16      : '>4I',
            32      : '>8I',
            64      : '>16I',
            128     : '>32I',
            256     : '>64I',
            512     : '>128I',
            1024    : '>256I',
            2048    : '>512I',
            4096    : '>1024I',
            8192    : '>2048I',
        }
        self.struct_compiled = {k : struct.Struct(v) for k, v in self.struct_formats.items()}

    def teardown(self, arg):
        del self.struct_formats
        del self.struct_compiled

    def time_struct_read_not_compiled(self, arg):
        # buf_len = struct.calcsize(arg)
        fmt = self.struct_formats[arg]
        with open(binary_path(20), 'rb') as f:
            while 1:
                b = f.read(arg)
                if len(b) != arg:
                    break
                struct.unpack(fmt, b)

    def time_struct_read_compiled(self, arg):
        my_struct = self.struct_compiled[arg]
        # buf_len = struct.calcsize(arg)
        with open(binary_path(20), 'rb') as f:
            while 1:
                b = f.read(arg)
                if len(b) != arg:
                    break
                my_struct.unpack(b)


class StructFloat:
    # Struct format sizes
    params = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]

    def setup(self, arg):
        check_binary_files()
        self.struct_formats = {
            4       : '>f',
            8       : '>d',
            16      : '>2d',
            32      : '>4d',
            64      : '>8d',
            128     : '>16d',
            256     : '>32d',
            512     : '>64d',
            1024    : '>128d',
            2048    : '>256d',
            4096    : '>512d',
            8192    : '>1024d',
        }
        self.struct_compiled = {k : struct.Struct(v) for k, v in self.struct_formats.items()}

    def teardown(self, arg):
        del self.struct_formats
        del self.struct_compiled

    def time_struct_read_not_compiled(self, arg):
        fmt = self.struct_formats[arg]
        with open(binary_path(20), 'rb') as f:
            while 1:
                b = f.read(arg)
                if len(b) != arg:
                    break
                struct.unpack(fmt, b)

    def time_struct_read_compiled(self, arg):
        my_struct = self.struct_compiled[arg]
        with open(binary_path(20), 'rb') as f:
            while 1:
                b = f.read(arg)
                if len(b) != arg:
                    break
                my_struct.unpack(b)


class StructRepCode68:
    """Checks the time that it takes to unpack integer structs and convert them to Representation Code 68 values."""
    # Struct format sizes
    params = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]

    def setup(self, arg):
        check_binary_files()
        self.struct_formats = {
            8       : '>2I',
            16      : '>4I',
            32      : '>8I',
            64      : '>16I',
            128     : '>32I',
            256     : '>64I',
            512     : '>128I',
            1024    : '>256I',
            2048    : '>512I',
            4096    : '>1024I',
            8192    : '>2048I',
        }
        self.struct_compiled = {k : struct.Struct(v) for k, v in self.struct_formats.items()}

    def teardown(self, arg):
        del self.struct_formats
        del self.struct_compiled

    # def time_struct_python_not_compiled(self, arg):
    #     # buf_len = struct.calcsize(arg)
    #     fmt = self.struct_formats[arg]
    #     with open(binary_path(20), 'rb') as f:
    #         while 1:
    #             b = f.read(arg)
    #             if len(b) != arg:
    #                 break
    #             for word in struct.unpack(fmt, b):
    #                 pRepCode.from68(word)

    def time_struct_python_compiled(self, arg):
        my_struct = self.struct_compiled[arg]
        # buf_len = struct.calcsize(arg)
        with open(binary_path(20), 'rb') as f:
            while 1:
                b = f.read(arg)
                if len(b) != arg:
                    break
                for word in my_struct.unpack(b):
                    pRepCode.from68(word)

    # def time_struct_cython_not_compiled(self, arg):
    #     # buf_len = struct.calcsize(arg)
    #     fmt = self.struct_formats[arg]
    #     with open(binary_path(20), 'rb') as f:
    #         while 1:
    #             b = f.read(arg)
    #             if len(b) != arg:
    #                 break
    #             for word in struct.unpack(fmt, b):
    #                 cRepCode.from68(word)

    def time_struct_cython_compiled(self, arg):
        my_struct = self.struct_compiled[arg]
        # buf_len = struct.calcsize(arg)
        with open(binary_path(20), 'rb') as f:
            while 1:
                b = f.read(arg)
                if len(b) != arg:
                    break
                for word in my_struct.unpack(b):
                    cRepCode.from68(word)

    # def time_struct_cpython_not_compiled(self, arg):
    #     # buf_len = struct.calcsize(arg)
    #     fmt = self.struct_formats[arg]
    #     with open(binary_path(20), 'rb') as f:
    #         while 1:
    #             b = f.read(arg)
    #             if len(b) != arg:
    #                 break
    #             for word in struct.unpack(fmt, b):
    #                 cpRepCode.from68(word)

    def time_struct_cpython_compiled(self, arg):
        my_struct = self.struct_compiled[arg]
        # buf_len = struct.calcsize(arg)
        with open(binary_path(20), 'rb') as f:
            while 1:
                b = f.read(arg)
                if len(b) != arg:
                    break
                for word in my_struct.unpack(b):
                    cpRepCode.from68(word)


