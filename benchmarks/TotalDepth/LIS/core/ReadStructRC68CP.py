import struct

from TotalDepth.LIS.core import cpRepCode

from benchmarks.TotalDepth.LIS.core import check_binary_files, binary_path

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

    def time_struct_68(self, arg):
        my_struct = self.struct_compiled[arg]
        # buf_len = struct.calcsize(arg)
        with open(binary_path(20), 'rb') as f:
            while 1:
                b = f.read(arg)
                if len(b) != arg:
                    break
                for word in my_struct.unpack(b):
                    cpRepCode.from68(word)


