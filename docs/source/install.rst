.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Installing TotalDepth

#######################################
Installing TotalDepth
#######################################

TotalDepth is not shrink-wrapped software so it has to be installed in a series of manual steps. Everyone's environment is different so this page tries to make it as simple as possible for most environments. If you have any suggestions of changes to this page that might be useful to others please send them to the project administrators.

*******************************************
Requirements
*******************************************

For TotalDepth will need to have installed (with links):

* `Python 3 <http://www.python.org>`_
* `Cython <http://www.cython.org>`_
* `numpy <http://numpy.scipy.org>`_

TotalDepth has been tested with these specific versions:

* Python 3.2
* Cython 0.14.1
* numpy 1.6.0.b2

TotalDepth is usually tested on some variant of Mac Os X such as 10.6 ('Snow Leopard') or later. It is occasionally tested on Windows.

*******************************************
Download
*******************************************

TotalDepth's project page is at http://sourceforge.net/projects/totaldepth/ [#]_. From there you can either download an archive from the files section or pull the latest source from the repository.

In any case you will unzip or clone/pull to a *directory* of your choice on your machine referred to hereon as :file:`{<TOTALDEPTH>}`.

From a Release
========================

Releases are made irregularly and they are on the `downloads page <http://sourceforge.net/projects/totaldepth/files/>`_. Select the release that you want and unpack the file to your directory :file:`{<TOTALDEPTH>}`

From the Hg Repo
===========================

The Mercurial repository has the most up-to-date code, get it with::

	$ mkdir <TOTALDEPTH>
	$ cd <TOTALDEPTH>
	$ hg clone http://hg.code.sf.net/p/totaldepth/code-0 .

*******************************************
Installing and Testing
*******************************************

Follow this to test that your installation of TotalDepth works.

Installing
==================

Setting the Environment
--------------------------

Check that your default version of Python is Python 3 (TotalDepth may or may not work with Python 2.x)::

	$ python3 --version
	$ Python 3.2

Put :file:`{<TOTALDEPTH>}` on your ``$PYTHONPATH``

Building Cython Code
---------------------------

Some parts of TotalDepth need to be built with Cython by hand (and you must have installed whatever Cython needs).

Cython & LIS
^^^^^^^^^^^^^^^^^^^^^^^^^^

The commands is::

	$ cd <TOTALDEPTH>/TotalDepth/LIS/core
	$ python setup.py build_ext --inplace

You should see a build directory and the appropriate :file:`.so` or :file:`.dll` files.

Testing
============================

To make sure that TotalDepth can be imported from your ``$PYTHONPATH`` do this::

	$ python3
	Python 3.2 (r32:88452, Feb 20 2011, 11:12:31) 
	[GCC 4.2.1 (Apple Inc. build 5664)] on darwin
	Type "help", "copyright", "credits" or "license" for more information.
	>>> import TotalDepth
	>>> dir(TotalDepth)
	['ExceptionTotalDepth', 'RELEASE_NOTES', 'VERSION', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__name__', '__package__', '__path__']
	>>> TotalDepth.VERSION
	(0, 1, 0)

System Testing
--------------------------

See :doc:`testing/test_plot` for comprehensive testing of your installation to see if LIS/LAS files can be written, read and plotted. This pretty much executes all TotalDepth code.

Unit Testing
--------------------------

See :doc:`testing/unit_tests` for more information about testing and unit tests.

.. rubric:: Footnotes

.. [#] Our home page that has, among other things, this *very fine documentation* is at http://totaldepth.sourceforge.net

