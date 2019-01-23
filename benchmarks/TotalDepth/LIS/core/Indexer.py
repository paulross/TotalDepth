from TotalDepth.LIS.core import LogiRec, LisGen, File, FileIndexer
from benchmarks.TotalDepth.LIS.core import write_logical_data_to_physical_records


class IndexerSimple:
    """
    Simple index on a small file.
    print('LIS file size', len(b.file_read.file.getvalue())) gives 8308 bytes
    This is 2 channels of 4 data frames of rep code 68 data.
    """

    def setup(self):
        # Create a Log Pass generator
        NUM_EXTRA_CHANNELS = 1
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, (NUM_EXTRA_CHANNELS + 1) * 4))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 66, 60))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'.1IN'))
        log_pass_gen = LisGen.LogPassGen(
            myEbs,
            # Channel list
            [
                LisGen.Channel(
                    LisGen.ChannelSpec(
                        b'TEST', b'ServID', b'ServOrdN', b'FEET',
                        45310011, 256, 16, 4, 68
                    ),
                    LisGen.ChValsConst(fOffs=0, waveLen=4, mid=0.0, amp=1.0, numSa=1, noise=None),
                ),
            ],
            xStart=10000.0 * 120,
            xRepCode=68,
            xNoise=None,
        )
        # Create a simple LIS file with a File Head, DFSR, some log data and a File Tail
        logical_data = [
            LisGen.FileHeadTailDefault.lrBytesFileHead,
            log_pass_gen.lrBytesDFSR()
        ]
        # Add 4 Logical Records consisting of 100 frames starting at an offset of 100*i
        # In this case xStart has been set in the generator as 10,000 feet with a sample size of 0.1 inch
        for i in range(4):
            logical_data.append(log_pass_gen.lrBytes(i*100, 100))
        logical_data.append(LisGen.FileHeadTailDefault.lrBytesFileTail)
        file_obj = write_logical_data_to_physical_records(logical_data)
        self.file_read = File.FileRead(theFile=file_obj, theFileId='MyFile', keepGoing=True)

    def teardown(self):
        del self.file_read

    def time_read(self):
        self.file_read.rewind()
        index = FileIndexer.FileIndex(self.file_read)
        print(index.longDesc())


class Indexer1M:
    """
    Roughly a 1Mb file file.
    print('LIS file size', len(b.file_read.file.getvalue())) gives 10,342,804 bytes
    This is 65 channels of 10,000 data frames of rep code 68 data.
    """

    def setup(self):
        # Create a Log Pass generator
        NUM_EXTRA_CHANNELS = 64
        myEbs = LogiRec.EntryBlockSet()
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SIZE, 1, 66, (NUM_EXTRA_CHANNELS + 1) * 4))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE, 1, 66, 60))
        myEbs.setEntryBlock(LogiRec.EntryBlock(LogiRec.EB_TYPE_FRAME_SPACE_UNITS, 4, 65, b'.1IN'))
        channel_names = ['{:04d}'.format(i).encode('ascii') for i in range(NUM_EXTRA_CHANNELS)]
        log_pass_gen = LisGen.LogPassGen(
            myEbs,
            # Channel list
            [
                LisGen.Channel(
                    LisGen.ChannelSpec(
                        channel_name, b'ServID', b'ServOrdN', b'FEET',
                        45310011, 256, 16, 4, 68
                    ),
                    LisGen.ChValsConst(fOffs=0, waveLen=4, mid=0.0, amp=1.0, numSa=1, noise=None),
                )
                for channel_name in channel_names
            ],
            xStart=10000.0 * 120,
            xRepCode=68,
            xNoise=None,
        )
        # Create a simple LIS file with a File Head, DFSR, some log data and a File Tail
        logical_data = [
            LisGen.FileHeadTailDefault.lrBytesFileHead,
            log_pass_gen.lrBytesDFSR()
        ]
        # Add 10000 Logical Records consisting of 1 frames starting at an offset of i
        # In this case xStart has been set in the generator as 10,000 feet with a sample size of 0.1 inch
        for i in range(10000):
            logical_data.append(log_pass_gen.lrBytes(i, 1))
        logical_data.append(LisGen.FileHeadTailDefault.lrBytesFileTail)
        file_obj = write_logical_data_to_physical_records(logical_data)
        # print('BenchmarkIndexerLarge LIS file size', len(file_obj.getvalue()))
        self.file_read = File.FileRead(theFile=file_obj, theFileId='MyFile', keepGoing=True)

    def teardown(self):
        del self.file_read

    def time_read(self):
        self.file_read.rewind()
        index = FileIndexer.FileIndex(self.file_read)
        print(index.longDesc())


# Debugging...
if __name__ == '__main__':
    for cls in (IndexerSimple, Indexer1M):
        b = cls()
        b.setup()
        print('LIS file size', len(b.file_read.file.getvalue()))
        b.time_read()
        b.teardown()
