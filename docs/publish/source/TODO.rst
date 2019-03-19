.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Summary of TODO stuff

###############################
A Bag Full of TODO's
###############################

This is just a gathering area for work items that should be done at some point.

TotalDepth is currently at **Alpha**, release version |release|.

**************************
Current Release
**************************

This lists known work (and area) that are known lacuna in the Alpha release.

LIS Format Support
===========================

General
--------------

* XNAM direct support for LIS-A

LIS Index
--------------

* Various forms of persistence: XML, Pickle, JSON (no).
* Insert or append binary representation of the index to the LIS file.

LIS FrameSet/LogPass
---------------------------

* Provide a numpy view on each sub-channel.
* X Axis quality i.e. duplicate, missing frames.
* Change up log to down log (needs to rearrange multi-sampled channels).
* Clearer view on what 'frame spacing' actually is.

Representation Codes
-----------------------

* Check overflow/underflow on write.

LAS Format Support
===========================

* Read directly from .zip files.
* Version 3.0 support.
* Merge ``~O`` section int ``~P`` if correct format.
* Consistency checking of mutual data such as STRT/STOP/STEP

Plotting
====================

* There is quite a lot of technical debt built up since we added LgFormat support, this area needs a review.
* Header: Some mud parameters being dropped.
* Benchmarks to characterise execution time and profiling.

**************************
Future Releases
**************************

This lists known work (and area) that are would be nice to have in future releases.

Format Support
==================

Wireline Formats
------------------

* RP66v1
* RP66v2
* WellLogML?
* ATLAS BIT?

Seismic Formats
-----------------------

* SEG-Y
* SEG-D?
* Other SEG formats

Miscellaneous Formats
--------------------------

* Position
