.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. _TotalDepth.LIS.core.FileIndexer:

FileIndexer
===========

#Contents:

.. toctree::
   :maxdepth: 2

.. automodule:: TotalDepth.LIS.core.FileIndexer
   :members:

Usage
-----

Examples
--------

Using a LIS Indexer
^^^^^^^^^^^^^^^^^^^

Source::
    
    myFilePath = "Spam/Eggs.LIS"
    # Open a LIS file
    myFi = File.FileRead(myFilePath, theFileId=myFilePath, keepGoing=True)
    # Index the LIS file
    myIdx = FileIndexer.FileIndex(myFi)
    # Ask the index for all the LogPass objects, these do not have the frameSet populated yet
    for aLr in myIdx.genAll():
        print(aLr)

Typical result::

	tell: 0x00000000 type=128 <TotalDepth.LIS.core.FileIndexer.IndexFileHead object at 0x10197ff90>
	tell: 0x00000050 type= 34 name=b'TOOL' <TotalDepth.LIS.core.FileIndexer.IndexTable object at 0x10197ffd0>
	tell: 0x000001ea type= 34 name=b'INPU' <TotalDepth.LIS.core.FileIndexer.IndexTable object at 0x10197fd10>
	tell: 0x00002342 type= 34 name=b'OUTP' <TotalDepth.LIS.core.FileIndexer.IndexTable object at 0x101b0b1d0>
	tell: 0x00003622 type= 34 name=b'CONS' <TotalDepth.LIS.core.FileIndexer.IndexTable object at 0x101b0bed0>
	tell: 0x0000456a type= 34 name=b'CONS' <TotalDepth.LIS.core.FileIndexer.IndexTable object at 0x101b0b590>
	tell: 0x000064aa type= 34 name=b'PRES' <TotalDepth.LIS.core.FileIndexer.IndexTable object at 0x101b0b050>
	tell: 0x00006efe type= 34 name=b'FILM' <TotalDepth.LIS.core.FileIndexer.IndexTable object at 0x101b0bfd0>
	tell: 0x00006fc6 type= 34 name=b'AREA' <TotalDepth.LIS.core.FileIndexer.IndexTable object at 0x101b0bb50>
	<TotalDepth.LIS.core.LogPass.LogPass object at 0x101b06490>
	<TotalDepth.LIS.core.LogPass.LogPass object at 0x101b12410>
	tell: 0x0017cbee type=129 <TotalDepth.LIS.core.FileIndexer.IndexFileTail object at 0x101b173d0>


Testing
-------

The unit tests are in test/TestFileIndexer.Py

