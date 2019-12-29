.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Working with LAS archives


Working with LAS Data
==================================

..  todo::
    
    Finish this.

I have an archive of data and I'd like a summary in HTML
---------------------------------------------------------------------

..  todo::
    
    Finish this.

I have an archive of LAS data and I want to plot it
---------------------------------------------------------------------

See :py:mod:`TotalDepth.PlotLogs`

There is some background data here :ref:`TotalDepth-tech-plotting-external`


I have some troublesome LAS files
---------------------------------------------------------------------

There are several problem areas for LAS files:

* The LAS specification is fairly weak and provides a lot of uncertainty.
    So LAS files produced by some producers are not readable by some other LAS consumers.
* LAS is a 'human readable' format, unfortunately that means it is a human writable format as well.
    This often means that LAS files can be mangled by well meaning, but mistaken intervention.
* Some LAS file archives have serious errors such as swapping value and description fields.
    These are not easily fixable by a rule based system.

The advantage, of course, with LAS files is that the can be hacked around with a simple text editor at will.
This will often fix small local problems.
   
Feel free to contact the author for advice.
