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


class BenchmarkLrMiscRead:
    # Different sizes of binary data
    params = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]

    def setup(self, arg):
        b = bytes([LogiRec.LR_TYPE_BLANK_RECORD, 0]) + b' ' * arg
        file_obj = write_logical_data_to_physical_records([b])
        self.file_read = File.FileRead(theFile=file_obj, theFileId='MyFile', keepGoing=True)

    def teardown(self, arg):
        del self.file_read

    def time_read(self, arg):
        self.file_read.rewind()
        LogiRec.LrMiscRead(self.file_read)


class BenchmarkTableRead:

    def setup(self):
        myT = LogiRec.LrTableWrite(
            34,
            b'PRES',
            (b'MNEM', b'OUTP', b'STAT', b'TRAC', b'CODI', b'DEST', b'MODE', b'FILT', b'LEDG', b'REDG',),
            (
                (b'40  ', b'TEST', b'ALLO', b'T1  ', b'LLIN', b'2   ', b'SHIF', 0.5, (-40.0, b'MV  '), (40.0, b'MV  ')),
                (b'20  ', b'TEST', b'ALLO', b'T2  ', b'HDAS', b'2   ', b'SHIF', 0.5, (-20.0, b'MV  '), (20.0, b'MV  ')),
                (b'10  ', b'TEST', b'ALLO', b'T3  ', b'LGAP', b'2   ', b'WRAP', 0.5, (-10.0, b'MV  '), (10.0, b'MV  ')),
                (b'5   ', b'TEST', b'ALLO', b'T2  ', b'HSPO', b'2   ', b'WRAP', 0.5, (-5.0, b'MV  '), (5.0, b'MV  ')),
                (b'2.5 ', b'TEST', b'ALLO', b'T3  ', b'LSPO', b'2   ', b'WRAP', 0.5, (-2.5, b'MV  '), (2.5, b'MV  ')),
            ),
        )
        ba = bytearray([34, 0])
        for b in myT.genLisBytes():
            ba += b
        file_obj = write_logical_data_to_physical_records([bytes(ba)])
        self.file_read = File.FileRead(theFile=file_obj, theFileId='MyFile', keepGoing=True)

    def teardown(self):
        del self.file_read

    def time_read(self):
        self.file_read.rewind()
        LogiRec.LrTableRead(self.file_read)


class BenchmarkDFSR_02_channel:

    def setup(self):
        b = (
            # Logical record header for DFSR
            bytes([64, 0])
            # Entry block 4, value 0
            + bytes([4, 1, 66, 0])
            # Entry block 12, value -153.0
            + bytes([12, 4, 68])
            + b'\xbb\xb3\x80\x00'
            # Entry block 0, value None terminates read
            + bytes([0, 1, 66, 0])
            # Sensor 0
            # Mnemonic
            + b'DEPT'
            # Service ID
            + b'ServID'
            # Service order number
            + b'ServOrdN'
            # Units
            + b'FEET'
            # API codes 45, 310, 01, 1
            # Decimal 45310011 is 0x02b3603b
            + b'\x02\xb3\x60\x3b'
            # File number: 256
            + bytes([1, 0])
            # LIS size in bytes: 4 bytes
            + bytes([0, 4])
            # Padding '0'
            + b'000'
            # Samples: 1 super samples
            + b'\x01'
            # Representation code
            + bytes([68,])
            # Process indicators
            + bytes([0, 1, 2, 3, 4])
            # Sensor 1
            # Mnemonic
            + b'GR  '
            # Service ID
            + b'ServID'
            # Service order number
            + b'ServOrdN'
            # Units
            + b'GAPI'
            # API codes 45, 310, 01, 1
            # Decimal 45310011 is 0x02b3603b
            + b'\x02\xb3\x60\x3b'
            # File number: 256
            + bytes([1, 0])
            # LIS size in bytes: 4 samples * 6 burst samples * 4 bytes = 96 bytes
            + bytes([0, 96])
            # Padding '0'
            + b'000'
            # Samples: 4 super samples
            + bytes([4,])
            # Representation code
            + bytes([68,])
            # Process indicators
            + bytes([0, 1, 2, 3, 4])
        )
        file_obj = write_logical_data_to_physical_records([b])
        self.file_read = File.FileRead(theFile=file_obj, theFileId='MyFile', keepGoing=True)

    def teardown(self):
        del self.file_read

    def time_read(self):
        self.file_read.rewind()
        LogiRec.LrDFSRRead(self.file_read)


class BenchmarkDFSR_08_channel:

    def setup(self):
        b = (
            # Logical record header for DFSR
            bytes([64, 0])
            # Entry block 4, value 0
            + bytes([4, 1, 66, 0])
            # Entry block 12, value -153.0
            + bytes([12, 4, 68])
            + b'\xbb\xb3\x80\x00'
            # Entry block 0, value None terminates read
            + bytes([0, 1, 66, 0])
            # Sensor 0
            # Mnemonic
            + b'DEPTServIDServOrdNFEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0, 0, 4, 0, 0, 0, 1, 68, 0, 1, 2, 3, 4])
            + b'CH01ServIDServOrdNNDIM' + b'\x02\xb3\x60\x3b' + bytes([1, 0, 0, 4, 0, 0, 0, 1, 68, 0, 1, 2, 3, 4])
            + b'CH02ServIDServOrdNNDIM' + b'\x02\xb3\x60\x3b' + bytes([1, 0, 0, 4, 0, 0, 0, 1, 68, 0, 1, 2, 3, 4])
            + b'CH03ServIDServOrdNNDIM' + b'\x02\xb3\x60\x3b' + bytes([1, 0, 0, 4, 0, 0, 0, 1, 68, 0, 1, 2, 3, 4])
            + b'CH04ServIDServOrdNNDIM' + b'\x02\xb3\x60\x3b' + bytes([1, 0, 0, 4, 0, 0, 0, 1, 68, 0, 1, 2, 3, 4])
            + b'CH05ServIDServOrdNNDIM' + b'\x02\xb3\x60\x3b' + bytes([1, 0, 0, 4, 0, 0, 0, 1, 68, 0, 1, 2, 3, 4])
            + b'CH06ServIDServOrdNNDIM' + b'\x02\xb3\x60\x3b' + bytes([1, 0, 0, 4, 0, 0, 0, 1, 68, 0, 1, 2, 3, 4])
            + b'CH07ServIDServOrdNNDIM' + b'\x02\xb3\x60\x3b' + bytes([1, 0, 0, 4, 0, 0, 0, 1, 68, 0, 1, 2, 3, 4])
        )
        file_obj = write_logical_data_to_physical_records([b])
        self.file_read = File.FileRead(theFile=file_obj, theFileId='MyFile', keepGoing=True)

    def teardown(self):
        del self.file_read

    def time_read(self):
        self.file_read.rewind()
        LogiRec.LrDFSRRead(self.file_read)


class BenchmarkDFSR_64_channel:

    def setup(self):
        channels = []
        for i in range(63):
            ch_name = '{:02d}'.format(i).encode('ascii')
            channels.append(
                b'CH' + ch_name + b'ServIDServOrdNNDIM' + b'\x02\xb3\x60\x3b' + bytes([1, 0, 0, 4, 0, 0, 0, 1, 68, 0, 1, 2, 3, 4])
            )
        b = (
            # Logical record header for DFSR
            bytes([64, 0])
            # Entry block 4, value 0
            + bytes([4, 1, 66, 0])
            # Entry block 12, value -153.0
            + bytes([12, 4, 68])
            + b'\xbb\xb3\x80\x00'
            # Entry block 0, value None terminates read
            + bytes([0, 1, 66, 0])
            # Sensor 0
            # Mnemonic
            + b'DEPTServIDServOrdNFEET' + b'\x02\xb3\x60\x3b' + bytes([1, 0, 0, 4, 0, 0, 0, 1, 68, 0, 1, 2, 3, 4])
            + b''.join(channels)
        )
        file_obj = write_logical_data_to_physical_records([b])
        self.file_read = File.FileRead(theFile=file_obj, theFileId='MyFile', keepGoing=True)

    def teardown(self):
        del self.file_read

    def time_read(self):
        self.file_read.rewind()
        dfsr = LogiRec.LrDFSRRead(self.file_read)
        # print(dfsr)


class BenchmarkDFSRMultichannel:
    params = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]


    def setup(self, param):
        channels = []
        for i in range(param):
            ch_name = '{:04d}'.format(i).encode('ascii')
            assert len(ch_name) == 4
            channels.append(
                ch_name + b'ServIDServOrdNNDIM' + b'\x02\xb3\x60\x3b' + bytes([1, 0, 0, 4, 0, 0, 0, 1, 68, 0, 1, 2, 3, 4])
            )
        b = (
            # Logical record header for DFSR
            bytes([64, 0])
            # Entry block 4, value 0
            + bytes([4, 1, 66, 0])
            # Entry block 12, value -153.0
            + bytes([12, 4, 68])
            + b'\xbb\xb3\x80\x00'
            # Entry block 0, value None terminates read
            + bytes([0, 1, 66, 0])
            + b''.join(channels)
        )
        file_obj = write_logical_data_to_physical_records([b])
        self.file_read = File.FileRead(theFile=file_obj, theFileId='MyFile', keepGoing=True)

    def teardown(self, param):
        del self.file_read

    def time_read(self, param):
        self.file_read.rewind()
        dfsr = LogiRec.LrDFSRRead(self.file_read)
        # print(dfsr)


# Debugging...
if __name__ == '__main__':
    # b = BenchmarkMarkerRecords()
    # b.setup(0x89)
    # b.time_marker_read(0x89)
    # b.teardown(0x89)
    b = BenchmarkDFSR_64_channel()
    b.setup()
    b.time_read()
    b.teardown()
