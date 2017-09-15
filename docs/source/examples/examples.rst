.. moduleauthor:: Paul Ross <cpipdev@googlemail.com>
.. sectionauthor:: Paul Ross <cpipdev@googlemail.com>

.. Examples of TotalDepth output

.. _totaldepth-examples:

###############################
TotalDepth Example Outputs
###############################

This shows some examples of the kind of thing that TotalDepth can do.

.. _totaldepth-examples-plots:

**********************************
Wireline Plots
**********************************

TotalDepth produced these time honoured plots from LIS and LAS wireline logs in SVG format that can be viewed in most browsers [#]_.

Plotting from LIS
===================

Some examples of plots generated from LIS79 files:

* A `collection <../copy_to_html/plots_LIS/index.html>`_ of 9 LIS files where TotalDepth used their internal plot specifications to generate 22 separate plots.
* A `High Resolution Dipmeter <../copy_to_html/plots/HDT_Example.svg>`_ plot on a scale of 1:25 with an API header. Fast channel FC0 (red) overlaid on FC1.

Plotting From LAS
===================

This shows off some examples of plots generated from the Canadian Well Logging Society's LAS formated files [#]_.

Single LAS Plot examples
----------------------------

This shows plots of a single LAS file that has 200 feet of 15 curves. TotalDepth can plot this with, linear and log scales and with an API header:

* Plotted with the `Resistivity 3Track Logrithmic <../copy_to_html/plots/Resistivity_3Track_Logrithmic.xml_47_LAS.svg>`_ format.
* The same data plotted with the `Triple Combo <../copy_to_html/plots/Triple_Combo_46_LAS.svg>`_ format.

The original LAS file is `here <../copy_to_html/plots/1001178923.las.txt>`_.

A Collection of LAS Plots
------------------------------

Here is a `directory of six LAS files <../copy_to_html/plots_LAS/index.html>`_ that was used to make 31 individual plots complete with an index that summarises them. For each LAS file the plotting program automatically choose from 29 plot formats the formats that produce useful plots [#]_.

Making LAS Plots
---------------------------------

The ``PlotLogs.py`` command line tool was used with the command::

	$ python3 PlotLogs.py -A -j4 -r -X 4 Data/ Plot/

This searched for LAS files in directory ``Data/`` with the plots being written in directory ``Plot/``.

The following options have been set:

* API headers on the top of each plot: ``-A``
* Multiprocessing on with 4 simultaneous jobs: ``-j4``
* Recursive search of input directory: ``-r``
* Uses any available plot specifications from LgFormat XML files which result in 4 curves or more being plotted: ``-X 4``

This took around six seconds to compute. More detail on the ``PlotLogs.py`` is here: :ref:`totaldepth-cmdline-PlotLogs`

**********************************
LIS Log HTML Summaries
**********************************

The program ``LisToHtml.py`` takes LIS file(s) and generates an `HTML summary <../copy_to_html/LISExampleHTML/index.html>`_ for each one.

How This HTML was Made
====================================

The ``LisToHtml.py`` command line tool was used with the command::

	$ python3 LisToHtml.py -k -j4 -r Data/ HTML/

This searched for LAS files in directory ``Data/`` with the files being written to directory ``HTML/``.

The following options have been set:

* Keep going as far as possible: ``-k``
* Multiprocessing on with 4 simultaneous jobs: ``-j4``
* Recursive search of input directory: ``-r``

More detail on the ``LisToHtml.py`` is here: :ref:`totaldepth-LIScmdline-LisToHtml`

.. rubric:: Footnotes

.. [#] Probably the best SVG support among current browsers is `Opera <http://www.opera.com>`_ [opera.com].
.. [#] Thanks to the `University of Kansas <http://www.kgs.ku.edu/Magellan/Logs/index.html>`_ [kgs.ku.edu] for the original data. For these examples that data has been edited or truncated or both.
.. [#] A *useful* plot format is one that can handle at least *n* curves where *n* is a number that is specified by the user.




