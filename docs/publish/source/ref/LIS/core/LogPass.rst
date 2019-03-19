.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Description of LIS LogPass module

###############################
The LIS Log Pass
###############################

This describes the LIS LogPass class that encapsulates a Log Pass. A log pass is the binary log data plus the record (DFSR) that describes the format of the binary data. Internally the binary data is converted to a FrameSet that wraps a numpy array.

The LogPass module is located in ``src/TotalDepth/LIS/core`` and can be imported thus::

	from TotalDepth.LIS.core import LogPass

***************************************************
LogPass API Reference
***************************************************

.. automodule:: TotalDepth.LIS.core.LogPass
    :members:

***************************************************
LogPass Usage
***************************************************

Typically a LogPass will be created directly or via a LIS FileIndexer. The latter technique is recommended as it is simpler.

Direct usage
===============

LogPass objects are used via a three step process and this reflects the sequential process of reading a LIS file:

1. Construction with a DFSR object (once).
2. Updating with the location of the binary data records that contain the frame data (once per IFLR).
3. Populating the FrameSet with real values from the file (many times).

Construction with a DFSR
----------------------------------

A LogPass object needs to be constructed with an instance of a LogiRec.LrDFSRRead. The LogPass will take a reference to the DFSR so the caller need not. The caller can always access the DFSR with the ``.dfsr`` property.

Assuming myF is a LIS File object positioned at the start of the DFSR::

	myLp = LogPass.LogPass(LogiRec.LrDFSRRead(myF), 'FileID')

Resources
^^^^^^^^^^^^^^^^^^

At this stage no FrameSet is created so the resource usage is minimal.

Add Binary Data Records
-------------------------------------------------------

The method ``addType01Data(tellLr, lrType, lrLen, xAxisVal)`` adds the position of an IFLR that contain frame data. This method takes these arguments:

=========   =============
Argument    Description
=========   =============
tellLr      The Logical Record start position (as a ``size_t``) in the file.
lrType      The type of the IFLR [0 | 1]. Will raise an ExceptionLogPass if this does not match the DFSR.
lrLen       The length of the Logical Record in bytes, not including the LRH.
xAxisVal    The value of the X Axis as a number of the first frame of the Logical Record.
=========   =============

This call should be made for each relevant IFLR as they are encountered in sequence.

Resources
^^^^^^^^^^^^^^^^^^

At this stage no FrameSet is created and the arguments are encoded into an RLE object so the resource usage is minimal.

Populating the FrameSet
--------------------------------------------------------

Once the preceding stages have been done the LogPass can be populated any number of times from the LIS file.

The method ``setFrameSet(theFile, theFrSl=None, theChList=None)`` constructs a new frame set with the appropriate values.

=========   =============
Argument    Description
=========   =============
theFile     The File object. Will raise an ExceptionLogPass is the file ID does not match that used in the constructor.
theFrSl     A slice object that describes when LogPass frames are to be used (default all). Will raise an ExceptionLogPass if there are no frames to load i.e. addType01Data() has not been called.
theChList   A list of external channel indexes (i.e. DSB block indexes) to populate the frame set with (default all).
=========   =============

Examples
^^^^^^^^^^^

Setting a frame set for all frames and all channels::

	myLogPass.setFrameSet(myFile)
	# The above line is equivalent to:
	myLogPass.setFrameSet(myFile, theFrSl=None, theChList=None)

Setting a frame set for frames [0:16:4] i.e. frame indexes (0,4,8,12) and channels [0, 4, 7] ::

	myLogPass.setFrameSet(myFile, theFrSl=slice(0,16,4), theChList=[0, 4, 7])

Resources
^^^^^^^^^^^^^^^^^^

Any previous FrameSet will be freed and a new FrameSet of the appropriate dimension is created so the resource usage can be significant.

Using a LIS Indexer
=====================

A :ref:`TotalDepth.LIS.core.FileIndexer` [``TotalDepth.LIS.core.FileIndexer.FileIndex``] object will perform the necessary construction of a LogPass and the population with Logical Record positions with ``addType01Data()`` leaving the user just to call ``setFrameSet()``. Thus a FileIndex object imposes low resource usage until the user wishes to populate the frame set.

An indexer will index a LIS file that has multiple Log Passes (e.g. repeat section, main log etc.) so the indexer provides an iteration method for Log Passes::
    
    myFilePath = "Spam/Eggs.LIS"
    # Open a LIS file, keepGoing for luck!
    myFi = File.FileRead(myFilePath, theFileId=myFilePath, keepGoing=True)
    # Index the LIS file
    myIdx = FileIndexer.FileIndex(myFi)
    # Ask the index for all the LogPass objects, these do not have the frameSet populated yet
    for aLp in myIdx.genLogPasses():
        # Load the FrameSet, all channels [None], all frames [None]
        aLp.logPass.setFrameSet(myFi, None, None)
        # The FrameSet is fully populated here...
        # Do something with it...

***************************************************
Testing
***************************************************

The unit tests are in ``test/TestLogPass.py``. This should take under a second to execute.

Running the tests under coverage::

	$ coverage run test/TestLogPass.py 
	TestClass.py script version "0.8.0", dated 10 Jan 2011
	Author: Paul Ross
	Copyright (c) Paul Ross
	
	testSetUpTearDown (__main__.TestLogPass_LowLevel)
	TestLogPass_LowLevel: Tests setUp() and tearDown(). ... ok
	test_00 (__main__.TestLogPass_LowLevel)
	TestLogPass_LowLevel.test_00(): Construction. ... ok
	test_01 (__main__.TestLogPass_LowLevel)
	TestLogPass_LowLevel.test_01(): _sliceFromList(). ... ok
	test_02 (__main__.TestLogPass_LowLevel)
	TestLogPass_LowLevel.test_02(): exercise various properties. ... ok
	test_10 (__main__.TestLogPass_LowLevel)
	TestLogPass_LowLevel.test_10(): nullValue(). ... ok
	
	8<-------------- snip ------------------>8

	test_00 (__main__.TestLogPass_UpIndirect)
	TestLogPass_UpIndirect.test_00(): 3 LR, 5 fr, 4 ch. setFrameSet() All. ... ok
	test_01 (__main__.TestLogPass_UpIndirect)
	TestLogPass_UpIndirect.test_01(): 3 LR, 5 fr, 4 ch. setFrameSet() theFrSl=slice(0,16,2). ... ok
	test_02 (__main__.TestLogPass_UpIndirect)
	TestLogPass_UpIndirect.test_02(): 3 LR, 5 fr, 4 ch. setFrameSet() theFrSl=slice(2,4,2). ... ok
	test_03 (__main__.TestLogPass_UpIndirect)
	TestLogPass_UpIndirect.test_03(): 3 LR, 5 fr, 4 ch. setFrameSet() theFrSl=slice(1,5,2). ... ok
	test_10 (__main__.TestLogPass_UpIndirect)
	TestLogPass_UpIndirect.test_10(): genFrameSetHeadings() ... ok
	
	----------------------------------------------------------------------
	Ran 54 tests in 0.507s
	
	OK
	CPU time =    0.510 (S)
	Bye, bye!
	
	$ coverage report -m
	Name     Stmts   Miss  Cover   Missing
	----------------------------------------------------------------------------------------------------------

	8<-------------- snip ------------------>8

	LogPass    273     27    90%   142, 167, 182, 187, 203, 216-218, 232, 258, 273-275, 319, 324, 412, 416, 457-459, 513, 527, 541, 557, 572, 646-647

	8<-------------- snip ------------------>8

	----------------------------------------------------------------------------------------------------------
	TOTAL     4586   1783    61%   

