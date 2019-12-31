.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Converting to LAS


Converting Files to LAS
==================================

Converting LIS Files to LAS
-----------------------------------

.. todo::

    TotalDepth does not support LIS to LAS as of version 0.3.0 (and you are looking at version |version|).
    Later versions of TotalDepth may do. It is pretty straightforward to implement.


Converting RP66V1 Files to LAS
-----------------------------------

There is a command line tool ``tdrp66v1tolas`` that can convert RP66V1 files to LAS 2.0 files.
There is a tutorial here: :ref:`cmd_line_tools_rp66v1_tdrp66v1tolas`.
This command line tool is a wrapper round the ``ToLAS`` module, the reference documentation is here: :py:mod:`TotalDepth.RP66V1.ToLAS`.


There is a technical note about the performance of this conversion here :ref:`TotalDepth-tech-RP66V1_processing_perf_LAS`.
