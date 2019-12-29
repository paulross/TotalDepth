.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Technical Note on LIS frame read performance.

.. toctree::
    :maxdepth: 2
   
.. _TotalDepth-tech-performance:

####################################
Performance of TotalDepth
####################################

This technical note presents the results of some actual performance tests on TotalDepth.

************************************
Measuring Performance
************************************

This describes some principles used in establishing TotalDepth's performance and setting performance targets.

User's Perception of Performance
====================================

Users only want to pay for what they get and experienced users have a rough idea of the cost of what they ask the software to do. For example most users would regard these a cheap operations, and would not expect them to take much time. If they did the user is likely to regard the application as 'slow':

* Load file
* Show log header
* Plot small section

Most users would regard these more expensive operations and is more likely to accept that they would take more time.:

* Cross correlate multiple curves
* Dipmeter processing
* Deconvolution

Most users are aware of the size of the data set with which the are operating and appreciate that operations on larger data sets take longer time. Users do not appreciate O(N :superscript:`2`) or worse behaviour. We don't like it either [#]_.

TotalDepth measures the cost of operations, in::

	Execution time (ms) 
	-------------------
	Size of input (Mb)

Example of LIS cost
---------------------

Our measure is ms/Mb of input. 1Mb of LIS data is typically 250,000 values, or, to put this in context 200 feet of 10 curves (6" sampling) is 0.015 Mb. So, just as an example, the cost of plotting such data from a 20Mb file *might* work out as:

============================    =============   ==============  ================    ===================
Operation                       Cost (ms/Mb)    Data Size (Mb)  User's Time (ms)     Notes
============================    =============   ==============  ================    ===================
Index a 20Mb file               12              20              240                 One-off exercise
Reading 200 feet, 10 curves     1500            0.015            22
Plotting what has been read     4000            0.015            60
**Total**                       -               -               **322**
============================    =============   ==============  ================    ===================

The rest of this tech note describes the performance of reading LIS files in these ms/Mb terms.


.. _TotalDepth-tech-performance_improve:

Performance Improvements
=================================

The low level performance of TotalDepth is pretty good. FrameSet performance is satisfactory. Further improvement is certain for :ref:`TotalDepth-tech-indexing-perf_improve` once the existing C code (in another project) is integrated into this one.

Populating the frame is a costly exercise and the current solution takes this path::

    File bytes -> Cython convert to C double -> convert to Python float -> insert into a numpy array.

All this boxing and unboxing is expensive and a faster (but with more code complexity) is to populate the numpy array directly so this all happens in C code::

    File bytes -> Convert to C double -> copy directly into numpy memory space

This should provide a great speedup.

The SVG creation is also worth looking at.

.. rubric:: Footnotes

.. [#] It is very easy for software developers to fail to see this kind of behaviour. For example if the time for an operation is: a + b * N + c * N :superscript:`2` and c << b. If the software test suit tests an insufficiently small size of N then it appears that the operation is O(N). Along comes a user with a large data set and they see O(N :superscript:`2`) behaviour. This (or worse) is quite commonly observed in many software products.
