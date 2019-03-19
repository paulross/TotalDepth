.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Description of LIS FrameSet module

###############################
The LIS Frame Set
###############################

.. toctree::
   :maxdepth: 2

This describes the LIS FrameSet that contains the binary frame data. It is effectively a wrapper around a 2-D numpy array with specific APIs to interface that with a channel specific shape. Importantly FrameSets can be partial in that they need not hold all the data for every frame and every channel. Instead they can hold data for the frames and channels specified by the caller.

The FrameSet module is located in ``src/TotalDepth/LIS/core`` and can be imported thus::

	from TotalDepth.LIS.core import FrameSet

***************************************************
FrameSet Internals
***************************************************

The internal representation of the FrameSet uses only Python and numpy structures and types, it is thus ignorant of the LIS file format or data structures apart from that described below.

LIS Dependancies
==================

In the current version of the code there are a number of dependencies on knowledge of the LIS file format (or at least TotalDepth's representation of that format):

* ``ChArTe`` objects are constructed from LIS Datum Specification Block objects.
* ``XAxisDecl`` consists of a straight copy of various Entry Block values.
* ``XAxisDecl`` relies on the LIS value of the up/down flag.
* ``FrameSet`` is constructed with a DFSR and extracts the absent value form the DFSR as well as constructing ChArTe and XAxisDecl objects.
* ``FrameSet`` has quite a lot of dependencies of Representation codes these are mainly used in two ways.
	* Interpreting Dipmeter sub-channels.
	* ``setFrameBytes()`` uses the RepCode module directly to convert bytes to values for a channel.

These dependencies restrict the use of FrameSet to processing LIS data, if they were removed then FrameSet could be used for other file formats but there is no obvious use case for that as, apart from LIS, TotalDepth supports LAS (trivially simple frame sets) and will support RP66 at some point. The latter may trigger a refactoring of the FrameSet module.

***************************************************
FrameSet API Reference
***************************************************

.. automodule:: TotalDepth.LIS.core.FrameSet
    :member-order: bysource
    :members:



***************************************************
FrameSet Usage
***************************************************


