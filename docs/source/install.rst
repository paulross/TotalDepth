.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Installing TotalDepth

#######################################
Installing TotalDepth
#######################################

From PyPi
========================

TODO.

From GitHub
===========================

The `GitHub repository <https://github.com/paulross/TotalDepth>`_ has the most up-to-date code, choose your root directory :file:`{<TOTALDEPTH>}` then get it with::

	$ mkdir <TOTALDEPTH>
	$ cd <TOTALDEPTH>
	$ git clone https://github.com/paulross/TotalDepth.git
	$ cd TotalDepth

*******************************************
Installing and Testing
*******************************************

Make a virtual environment in your :file:`{<PYTHONVENVS>}`, say :file:`{~/pyvenvs}`::

    $ python3 -m venv <PYTHONVENVS>/TotalDepth
    $ . <PYTHONVENVS>/TotalDepth/bin/activate
    (TotalDepth) $

Install the dependencies, ``numpy`` and ``Cython``::

    (TotalDepth) $ pip install numpy
    (TotalDepth) $ pip install Cython
    
Install TotalDepth::

    (TotalDepth) $ python setup.py install

Install the test dependencies and run TotalDepth's tests::

    (TotalDepth) $ pip install pytest
    (TotalDepth) $ pip install pytest-runner
    (TotalDepth) $ python setup.py test

Developing with TotalDepth
----------------------------

If you are developing with TotalDepth you need test coverage and documentation tools.

Test Coverage
^^^^^^^^^^^^^^^^

Install ``pytest-cov``::

    $ pip install pytest-cov
    $ pytest --cov=TotalDepth --report html tests/


Documentation
^^^^^^^^^^^^^^^^

If you want to build the documentation you need to::

    $ pip install Sphinx
    $ cd docs
    $ make html


System Testing
--------------------------

See :doc:`testing/test_plot` for comprehensive testing of your installation to see if LIS/LAS files can be written, read and plotted. This pretty much executes all TotalDepth code.

Unit Testing
--------------------------

See :doc:`testing/unit_tests` for more information about testing and unit tests.
