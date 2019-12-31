.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Working with LIS archives


Working with LIS Data
==================================

I have an archive of data and I'd like a summary in HTML
---------------------------------------------------------------------

There is a command line tool :ref:`tdlistohtml <cmd_line_tools_lis_tdlistohtml>`  (a wrapper around  :py:mod:`TotalDepth.LIS.LisToHtml`) which can generate an HTML summary of a body of LIS files.
There is a tutorial here: :ref:`cmd_line_tools_lis_tdlistohtml`


I have an archive of LIS data and I want to plot it
---------------------------------------------------------------------

There is a generalised well log plotting command line tool :ref:`tdplotlogs <TotalDepth-cmdline-PlotLogs>` that supports LIS and is described here: :ref:`TotalDepth-cmdline-PlotLogs` (references :py:mod:`TotalDepth.PlotLogs`).

LIS files may or may not contain an internal plot specification, if so ``tdplotlogs`` can take advantage of that, if not then external plot specifications can be used.
For files needing an external plot specification there is some background information on plotting in a technical note here :ref:`TotalDepth-tech-plotting-external`.


I have some troublesome LIS files
---------------------------------------------------------------------

This is a highly specialised area. Feel free to contact the author for advice.


Getting the Frame Data as a ``numpy`` Array
---------------------------------------------------

TotalDepth's LIS represents the channel data as Numpy arrays.
There is a tutorial here on writing code that allows you to access the Numpy channel data directly: :ref:`total_depth.processing_lis_files.numpy_arrays`
