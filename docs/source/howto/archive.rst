.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Working with archives of oilfield data


Working with Archives of Mixed Data
=======================================


I have an archive of files and I want to know what is in there.
----------------------------------------------------------------------

Sometimes you are given an archive of data and would like to know what file formats, the file sizes and so on.
There is a command line tool ``tdarchive`` [References :py:mod:`TotalDepth.util.archive`] that can give you a summary of the files there, their binary file types and their sizes.

Read more here :ref:`TotalDepth-cmdline-archive`.


I have an archive and I want copy specific file types
----------------------------------------------------------------------

There is a command line tool ``tdcopybinfiles`` [References :py:mod:`TotalDepth.util.CopyBinFiles`] that can copy specific file types from  one directory to another. It can also recursively deflate archives such as ZIP files.

Read more here :ref:`TotalDepth-cmdline-tdcopybinfiles`.


I have an archive and I want report or remove duplicate files
----------------------------------------------------------------------

There is a command line tool ``tdremovedupefiles`` [References :py:mod:`TotalDepth.util.RemoveDupeFiles`] that can find  duplicate files based on  their checksum and, optionally, remove the duplicates.

Read more here :ref:`TotalDepth-cmdline-tdremovedupefiles`.


