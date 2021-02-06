.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Working with LAS archives


Working with LAS Data
==================================


I have an archive of data and I'd like a summary in HTML
---------------------------------------------------------------------

There is a command line tool :ref:`tdlastohtml <cmd_line_tools_las_tdlastohtml>`  (a wrapper around  :py:mod:`TotalDepth.LAS.LASToHtml`) which can generate an HTML summary of a body of LAS files.
There is a tutorial here: :ref:`cmd_line_tools_las_tdlastohtml`


I have an archive of LAS data and I want to plot it
---------------------------------------------------------------------

There is a generalised well log plotting command line tool ``tdplotlogs`` that supports LAS described here: :ref:`TotalDepth-cmdline-PlotLogs` (references :py:mod:`TotalDepth.PlotLogs`).

LAS files do not contain an internal plot specification.
For files needing an external plot specification there is some background information on plotting in a technical note here :ref:`TotalDepth-tech-plotting-external`.


Getting the Frame Data as a ``numpy`` Array
---------------------------------------------------

TotalDepth's LAS represents the channel data as Numpy arrays.
There is a tutorial here on writing code that allows you to access the Numpy channel data directly: :ref:`total_depth.processing_las_files.numpy_arrays`


I have some troublesome LAS files
---------------------------------------------------------------------

There are several problem areas for LAS files:

* The LAS specification is fairly weak and provides a lot of uncertainty. So LAS files from some producers are not readable by some other LAS consumers.
* LAS is a 'human readable' format, unfortunately that means it is a human writable format as well. This often means that LAS files can be mangled by well meaning, but mistaken intervention.
* Some LAS file archives have serious errors such as swapping value and description fields. These are not easily fixable by a rule based system.

The advantage, of course, with LAS files is that the can be hacked around with a simple text editor at will.
This will often fix small local problems.
   
Feel free to contact the author for advice.
