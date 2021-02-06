.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Processing LAS files with Python

.. _total_depth.processing_las_files:


Processing LAS Files
======================================================


.. _total_depth.processing_las_files.numpy_arrays:


------------------------------
Reading a LAS File Log Data
------------------------------

There is some example files in ``example_data/LAS/data``, lets read one:
	
.. code-block:: python

    from TotalDepth.LAS.core import LASRead

    las_file_path = os.path.join('example_data', 'LAS', 'data', 'BASIC_FILE_0_50.las')
    las_file = LASRead.LASRead(las_file_path, las_file_path, raise_on_error=False)
    # If there is an array section it will be initialised as a LogPass.FrameArray
    if las_file.frame_array is not None:
        # Can iterate through the channels...
        for channel in las_file.frame_array.channels:
            # channel.array is a numpy masked array.
            array = channel.array
            print(f'{channel.ident:4} [{channel.units:4}] Shape: {array.shape} Minimum: {array.min():8g}')


The output will typically be:

.. code-block:: console

    DEPT [m   ] Shape: (649, 1) Minimum:   2889.4
    TENS [lbs ] Shape: (649, 1) Minimum:  5292.04
    ETIM [min ] Shape: (649, 1) Minimum:    0.019
    DHTN [lbs ] Shape: (649, 1) Minimum:  2562.92
    GR   [api ] Shape: (649, 1) Minimum:   43.201

.. note::

    The ``LogPass.FrameArray`` is universal, but LAS can only represent one value per frame per channel.
    To access that value you need to use ``array[frame_index][0]``.


References:

FrameArray: :py:class:`TotalDepth.common.LogPass.FrameArray`

.. todo::

	Complete this.
	
