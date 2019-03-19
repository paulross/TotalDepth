.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

Histogram
=======================

.. automodule:: TotalDepth.util.Histogram
	:member-order: bysource
	:members:
	:special-members:


Testing
------------

Tests are in :file:`test/TestHistogram.py`

Running Tests
^^^^^^^^^^^^^^^^^

::

	$ python3 test/testHistogram.py

Test Coverage
^^^^^^^^^^^^^^^^^

::

	$ coverage run test/testHistogram.py
	...
	$ coverage report -m

Examples
------------

::

    from TotalDepth.util import Histogram
    
    myH = Histogram.Histogram()
    for x in range(1, 12):
        self._hist.add(x, x)
    print(self._hist.strRep())
    # Prints """ 1 | ++++++
     2 | +++++++++++++
     3 | +++++++++++++++++++
     4 | +++++++++++++++++++++++++
     5 | ++++++++++++++++++++++++++++++++
     6 | ++++++++++++++++++++++++++++++++++++++
     7 | +++++++++++++++++++++++++++++++++++++++++++++
     8 | +++++++++++++++++++++++++++++++++++++++++++++++++++
     9 | +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    10 | ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    11 | ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"""

