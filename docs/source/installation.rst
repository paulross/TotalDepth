.. highlight:: shell

============
Installation
============


Stable release
--------------

To install TotalDepth, run this command in your terminal:

.. code-block:: console

    $ pip install TotalDepth

This is the preferred method to install TotalDepth, as it will always install the most recent stable release. 

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

First make a virtual environment in your :file:`{<PYTHONVENVS>}`, say :file:`{~/pyvenvs}`:

.. code-block:: console

    $ python3 -m venv <PYTHONVENVS>/TotalDepth
    $ . <PYTHONVENVS>/TotalDepth/bin/activate
    (TotalDepth) $

Install the dependencies, ``numpy`` and ``Cython``:

.. code-block:: console

    (TotalDepth) $ pip install numpy
    (TotalDepth) $ pip install Cython
    
The sources for TotalDepth can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    (TotalDepth) $ git clone git://github.com/paulross/TotalDepth.git

Or download the `tarball`_:

.. code-block:: console

    (TotalDepth) $ curl  -OL https://github.com/paulross/TotalDepth/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

	(TotalDepth) $ cd TotalDepth
    (TotalDepth) $ python setup.py install

Install the test dependencies and run TotalDepth's tests:

.. code-block:: console

    (TotalDepth) $ pip install pytest
    (TotalDepth) $ pip install pytest-runner
    (TotalDepth) $ python setup.py test

Developing with TotalDepth
----------------------------

If you are developing with TotalDepth you need test coverage and documentation tools.

Test Coverage
^^^^^^^^^^^^^^^^

Install ``pytest-cov``:

.. code-block:: console

    (TotalDepth) $ pip install pytest-cov

The most meaningful invocation that elimates the top level tools is:

.. code-block:: console

    (TotalDepth) $ pytest --cov=TotalDepth.LAS.core --cov=TotalDepth.LIS.core --cov=TotalDepth.RP66.core --cov=TotalDepth.util --cov-report html tests/


Documentation
^^^^^^^^^^^^^^^^

If you want to build the documentation you need to:

.. code-block:: console

    (TotalDepth) $ pip install Sphinx
    (TotalDepth) $ cd docs
    (TotalDepth) $ make html


System Testing
--------------------------

See :doc:`testing/test_plot` for comprehensive testing of your installation to see if LIS/LAS files can be written, read and plotted. This pretty much executes all TotalDepth code.

Unit Testing
--------------------------

See :doc:`testing/unit_tests` for more information about testing and unit tests.

.. _Github repo: https://github.com/paulross/TotalDepth
.. _tarball: https://github.com/paulross/TotalDepth/tarball/master
