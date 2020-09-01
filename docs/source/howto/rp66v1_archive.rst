.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Working with RP66V1 archives


Working with RP66V1 Data
=======================================

TotalDepth version 0.3.0 (you are viewing |version|) onwards provides a RP66V1 standard compliant implementation.
RP66V1 file handling is work-in-progress.


I have an archive of RP66V1 data and I'd like a summary in HTML
---------------------------------------------------------------------


TotalDepth's ``tdrp66v1scanhtml`` command line tool can do this, it is a wrapper around :py:mod:`TotalDepth.RP66V1.ScanHTML`
There is a tutorial here: :ref:`cmd_line_tools_rp66v1_tdrp66v1scanhtml`.

Here is an example of the HTML summary of a `single RP66V1 file <../_static/RP66V1/example.html>`_ .


I'd like to create some well plots from RP66V1 data
---------------------------------------------------------------------

Unlike LIS and like LAS, RP66V1 files do not specify a plot format.
Some producers include some producer specific information in private EFLRs.
TotalDepth version 0.4.0 will provide a simpler, universal, way of specifying plot formats in SVG from LAS, LIS and RP66V1 data.

I'd like to convert RP66V1 files to LAS format files
---------------------------------------------------------------------

There is a tutorial here : :ref:`cmd_line_tools_rp66v1_tdrp66v1tolas`.


Getting the Frame Data as a ``numpy`` Array
------------------------------------------------

There is a tutorial here on writing code that allows you to access the numpy channel data directly: :ref:`total_depth.processing_rp66v1_files.reading_frames_as_numpy`.
There is some example code in :file:`example_data/RP66V1/demo_read.py`

I have some troublesome RP66V1 files
---------------------------------------------------------------------

On problem noticed in RP66V1 data from the wild is that it is often polluted with gratuitous TIF markers which makes the file unreadable by a RP66V1 standard compliant implementation.
TotalDepth's ``tddetif`` command line tool can remove these TIF markers and make the files readable.
There is a tutorial here: :ref:`TotalDepth-cmdline-detif` 

Other problems require special skills, feel free to contact the author for advice.
