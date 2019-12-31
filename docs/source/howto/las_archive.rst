.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Working with LAS archives


Working with LAS Data
==================================

I have an archive of LAS data and I want to plot it
---------------------------------------------------------------------


There is a generalised well log plotting command line tool ``tdplotlogs`` that supports LAS described here: :ref:`TotalDepth-cmdline-PlotLogs` (references :py:mod:`TotalDepth.PlotLogs`).

LAS files do not contain an internal plot specification.
For files needing an external plot specification there is some background information on plotting in a technical note here :ref:`TotalDepth-tech-plotting-external`.


I have some troublesome LAS files
---------------------------------------------------------------------

There are several problem areas for LAS files:

* The LAS specification is fairly weak and provides a lot of uncertainty. So LAS files from some producers are not readable by some other LAS consumers.
* LAS is a 'human readable' format, unfortunately that means it is a human writable format as well. This often means that LAS files can be mangled by well meaning, but mistaken intervention.
* Some LAS file archives have serious errors such as swapping value and description fields. These are not easily fixable by a rule based system.

The advantage, of course, with LAS files is that the can be hacked around with a simple text editor at will.
This will often fix small local problems.
   
Feel free to contact the author for advice.

Getting the Frame Data as a ``numpy`` Array
----------------------------------------------------

TotalDepth's LAS parser does not support Numpy as of version 0.3.0 (and you are looking at version |version|).
Later versions of the TotalDepth LAS parser may use the universal Frame Array which does support Numpy.

For example::

    from TotalDepth.LAS.core import LASRead
    from TotalDepth.LIS.core import Mnem

    with open("LAS.las") as file_object:
        las_file = LASRead.LASRead(file_object, 'LAS.las')
        # las_file.numFrames() gives the number of frames
        # las_file.numDataPoints() gives the total number of values
        # las_file.curveMnems() gives a list of curves
        # however if you  want a specific curve such as 'GR' you can iterate through the X axis and value pairs:
        for x, v in las_file.genOutpPoints(Mnem.Mnem('GR')):
            # x, v is:
            #    (1700.0, -999.25),
            #    (1700.5, 40.7909),
            #    (1701.0, 44.0165),
            #    ...
