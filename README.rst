********************
TotalDepth
********************

.. image:: https://img.shields.io/pypi/v/TotalDepth.svg
        :target: https://pypi.python.org/pypi/TotalDepth

.. image:: https://img.shields.io/travis/paulross/TotalDepth.svg
        :target: https://travis-ci.org/paulross/TotalDepth

.. image:: https://readthedocs.org/projects/TotalDepth/badge/?version=latest
        :target: https://TotalDepth.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

Petrophysical software capable of processing wireline logs.

* Free software: GPL 2.0
* Documentation: https://TotalDepth.readthedocs.io

Features
========================

* Reads LIS, LAS (1.2, 2.0), RP66V1 (DLIS), Western Atlas BIT, and DAT Mud Log file formats for analysis or conversion to other formats.
* Creates Numpy arrays of log data.
* Plots log data as SVG viewable in any modern browser.
* Plots can be made with a wide variety of plot formats.
* TotalDepth can generate HTML summaries of log data.
* TotalDepth is written in Python so it is fast to develop with.
* Special indexing techniques are used to be able to randomly access sequential files.

Wireline Plots
--------------------------

Here is an example of a LAS file plotted with the Tripple Combo plot format as seen in a browser which includes the API header:

.. image:: images/TrippleCombo.png
        :alt: Tripple Combo

An example of a High Resolution Dipmeter plotted at 1:25 scale:

.. image:: images/HDT_25_no_hdr.png
        :alt: High Resolution Dipmeter

Accessing Frame Data as a ``numpy`` Array
------------------------------------------

Here is an example of accessing RP66V1 (DLIS) data as a numpy array and using ``np.info()`` to describe each array:

.. code-block:: python

    import numpy as np

    from TotalDepth.RP66V1.core import LogicalFile

    # path_in is expected to be the path to a RP66V1 file.
    # Try this with an example RP66V1 file at TotalDepth/example_data/RP66V1/data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS
    with LogicalFile.LogicalIndex(path_in) as logical_index:
        for logical_file in logical_index.logical_files:
            if logical_file.has_log_pass:
                for frame_array in logical_file.log_pass:
                    print(frame_array)
                    frame_count = logical_file.populate_frame_array(frame_array)
                    print(
                        f'Loaded {frame_count} frames and {len(frame_array)} channels'
                        f' from {frame_array.ident} using {frame_array.sizeof_array} bytes.'
                    )
                    for channel in frame_array.channels:
                        print(channel)
                        # channel.array is a numpy array
                        np.info(channel.array)
                        print()

The output will be something like:

.. code-block:: console

    FrameArray: ID: OBNAME: O: 2 C: 0 I: b'2000T' b''
      <FrameChannel: 'TIME' "b'1 second River Time'" units: 'b'ms'' count: 1 dimensions: (1,) frames: 1>
      <FrameChannel: 'TDEP' "b'1 second River Depth'" units: 'b'0.1 in'' count: 1 dimensions: (1,) frames: 0>
      <FrameChannel: 'TENS_SL' "b'Cable Tension'" units: 'b'lbf'' count: 1 dimensions: (1,) frames: 0>
      <FrameChannel: 'DEPT_SL' "b'Station logging depth'" units: 'b'0.1 in'' count: 1 dimensions: (1,) frames: 0>
    Loaded 921 frames and 4 channels from OBNAME: O: 2 C: 0 I: b'2000T' using 14736 bytes.

    <FrameChannel: 'TIME' "b'1 second River Time'" units: 'b'ms'' count: 1 dimensions: (1,) frames: 921>
    class:  ndarray
    shape:  (921, 1)
    strides:  (4, 4)
    itemsize:  4
    aligned:  True
    contiguous:  True
    fortran:  True
    data pointer: 0x102a08a00
    byteorder:  little
    byteswap:  False
    type: float32

    <FrameChannel: 'TDEP' "b'1 second River Depth'" units: 'b'0.1 in'' count: 1 dimensions: (1,) frames: 921>
    class:  ndarray
    shape:  (921, 1)
    strides:  (4, 4)
    itemsize:  4
    aligned:  True
    contiguous:  True
    fortran:  True
    data pointer: 0x102a09a00
    byteorder:  little
    byteswap:  False
    type: float32

    <FrameChannel: 'TENS_SL' "b'Cable Tension'" units: 'b'lbf'' count: 1 dimensions: (1,) frames: 921>
    class:  ndarray
    shape:  (921, 1)
    strides:  (4, 4)
    itemsize:  4
    aligned:  True
    contiguous:  True
    fortran:  True
    data pointer: 0x102a0aa00
    byteorder:  little
    byteswap:  False
    type: float32

    <FrameChannel: 'DEPT_SL' "b'Station logging depth'" units: 'b'0.1 in'' count: 1 dimensions: (1,) frames: 921>
    class:  ndarray
    shape:  (921, 1)
    strides:  (4, 4)
    itemsize:  4
    aligned:  True
    contiguous:  True
    fortran:  True
    data pointer: 0x102a0ba00
    byteorder:  little
    byteswap:  False
    type: float32
    ...


Installing TotalDepth
===================================

To install TotalDepth, run this command in your terminal:

.. code-block:: console

    $ pip install TotalDepth

This is the preferred method to install TotalDepth, as it will always install the most recent stable release from PyPi.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

From sources
--------------------------------------

If you are using a virtual environment in your virtual environment directory, for example ``~/pyvenvs``:

.. code-block:: console

    $ python3 -m venv ~/pyvenvs/TotalDepth
    $ source ~/pyvenvs/TotalDepth/bin/activate
    (TotalDepth) $

Or if you have a Conda environment (here using Python 3.8, adjust as necessary):

.. code-block:: console

    $ conda create --name TotalDepth python=3.8 pip
    $ source activate TotalDepth

Install the dependencies, ``numpy`` and ``Cython``:

If you are using a virtual environment:

.. code-block:: console

    (TotalDepth) $ pip install numpy
    (TotalDepth) $ pip install Cython

Or if you have a Conda environment:

.. code-block:: console

    (TotalDepth) $ conda install numpy
    (TotalDepth) $ conda install Cython

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

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

.. _Github repo: https://github.com/paulross/TotalDepth
.. _tarball: https://github.com/paulross/TotalDepth/tarball/master
