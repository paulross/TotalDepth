.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Working with BIT archives


Working with Western Atlas BIT Data
======================================

I have an archive of data and I'd like a summary
---------------------------------------------------------------------

There is a command line tool :ref:`tdbitread <cmd_line_tools_bit_tdbitread>`  (a wrapper around  :py:mod:`TotalDepth.BIT.ReadBIT`) which can generate a summary of a body of BIT files.
There is a tutorial here: :ref:`cmd_line_tools_bit_tdbitread`


I'd like to convert BIT files to LAS format files
---------------------------------------------------------------------


There is a tutorial here : :ref:`cmd_line_tools_bit_tdbittolas`.
    

Getting the Frame Data as a ``numpy`` Array
---------------------------------------------------

TotalDepth's BIT parser represents the channel data as Numpy arrays.
There is a tutorial here on writing code that allows you to access the Numpy channel data directly: :ref:`total_depth.processing_bit_files.numpy_arrays`


I have some troublesome BIT files
---------------------------------------------------------------------

This is a highly specialised area. Feel free to contact the author for advice.
