Unit Tests
=========================

This describes how unit testing is done in TotalDepth.

Module Unit Testing
----------------------

Most modules have their unit tests in the :file:`test/` directory in the package the module is in.
The test code is usually in :file:`Test{Module}.py`.

Example
^^^^^^^^

For the module ``TotalDepth.LIS.core.LogPass`` the unit tests are in :file:`TotalDepth/LIS/core/test/TestLogPass.Py`
and they can be run thus::

	$ cd <TOTALDEPTH>/src/TotalDepth/LIS/core
	$ python3 test/TestLogPass.py

The output is::

	TestClass.py script version "0.8.0", dated 10 Jan 2011
	Author: Paul Ross
	Copyright (c) Paul Ross
	
	testSetUpTearDown (__main__.TestLogPass_LowLevel)
	TestLogPass_LowLevel: Tests setUp() and tearDown(). ... ok
	test_00 (__main__.TestLogPass_LowLevel)
	TestLogPass_LowLevel.test_00(): Construction. ... ok
	test_01 (__main__.TestLogPass_LowLevel)
	
	... 8<-------- Many lines snipped -------->8
	
	TestLogPass_UpIndirect.test_02(): 3 LR, 5 fr, 4 ch. setFrameSet() theFrSl=slice(2,4,2). ... ok
	test_03 (__main__.TestLogPass_UpIndirect)
	TestLogPass_UpIndirect.test_03(): 3 LR, 5 fr, 4 ch. setFrameSet() theFrSl=slice(1,5,2). ... ok
	test_10 (__main__.TestLogPass_UpIndirect)
	TestLogPass_UpIndirect.test_10(): genFrameSetHeadings() ... ok
	
	----------------------------------------------------------------------
	Ran 54 tests in 0.271s
	
	OK
	CPU time =    0.275 (S)
	Bye, bye!

Package Unit Testing
----------------------

Most packages have their unit tests in the :file:`test/UnitTests.py` in the package the module is in.

Example
^^^^^^^^

For the module ``TotalDepth.LAS.core`` the unit tests are in :file:`TotalDepth/LAS/core/test/UnitTests.Py`
and they can be run thus::

	$ python3 test/UnitTests.py

And the result is::

	UnitTests.py script version "0.8.0", dated 2009-09-15
	Author: Paul Ross
	Copyright (c) Paul Ross
	
	Command line:
	test/UnitTests.py
	
	('File:', 'test/UnitTests.py')
	Testing TestEngVal
	----------------------------------------------------------------------
	Ran 55 tests in 0.002s
	
	OK
	
	8<-------- Many lines snipped -------->8
	
	OK
	Testing TestUnits
	Time:    0.952 rate    102.547 k/S Time:    0.389 rate    250.863 k/S Time:    0.175 rate    556.827 k/S ----------------------------------------------------------------------
	Ran 8 tests in 1.517s
	
	OK
	Results
	   Tests: 803
	  Errors: 0
	Failures: 0
	
	CPU time =  215.986 (S)
	Bye, bye!

Unit Testing and ``coverage``
----------------------------------

Ned Batchelor's *excellent* coverage tool can be used with these unit tests::

	$ coverage run test/TestMnem.py

And the result is::

	TestMnem.py script version "0.8.0", dated May 26, 2011
	Author: Paul Ross
	Copyright (c) 2011 Paul Ross.
	
	test_00 (__main__.TestMnem)
	TestMnem.test_00(): Tests setUp() and tearDown(). ... ok
	test_01 (__main__.TestMnem)
	TestMnem.test_01(): Basic constructor. ... ok
	test_02 (__main__.TestMnem)
	TestMnem.test_02(): Truncation of >4 chars. ... ok
	test_03 (__main__.TestMnem)
	TestMnem.test_03(): Padding of <4 chars. ... ok
	...
	test_70 (__main__.TestMnem)
	TestMnem.test_70(): Construction with a string. ... ok
	
	----------------------------------------------------------------------
	Ran 21 tests in 0.002s
	
	OK
	CPU time =    0.003 (S)
	Bye, bye!

Reporting coverage::

	$ coverage report -m

And the result is::

	Name                                   Stmts   Miss  Cover   Missing
	-------------------------------------------------------------------------------------------
	TotalDepth/src/TotalDepth/LIS/__init__     7      0   100%   
	TotalDepth/src/TotalDepth/__init__         6      0   100%   
	Mnem                                      52      0   100%   
	__init__                                   0      0   100%   
	test/TestMnem                            161     13    92%   259, 286-289, 292-296, 298-300
	-------------------------------------------------------------------------------------------
	TOTAL                                    226     13    94%   






