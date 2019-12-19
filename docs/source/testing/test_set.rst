.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. TotalDepth test set


Testing TotalDepth With Recorded Data
============================================

TotalDepth is tested against a diverse data set of real world files.
The test set is split into small/medium/large datasets.

Small Test Set
----------------------------

:todo: Complete this


Medium Test Set
----------------------------

The Medium Size Test Set is 20,000+ files (100Gb+) of typical oilfield data.
Here is the approximate breakdown of the test set:


=============== =========== =========== =====================================================================================
File Type       Files       Total Size  Notes
=============== =========== =========== =====================================================================================
LAS v1.2        ~500        ~1Gb        Largest file is around 16Mb.
LAS v2.0        ~20,000     ~30Gb       Largest file is around 250Mb (RP66V1 converted files are much larger).
LAS v3.0        A few       ~0          Rarely present, their absence is not considered significant. 
LIS             ~2000       ~2GB        Largest file is around 60Mb. Around half have TIF markers. 
DLIS (RP66V1)   ~800        ~100GB      Largest file is around 4GB. About one quarter are corrupted by TIF markers.
DLIS (RP66V2)   0           0           Not present, their absence is not considered significant. 
Other           Various     Various     Various files such as PDF, TIFF, miscellaneous binary files and unstructured ASCII.
                                        If present then their contents is not considered significant but archives containing
                                        these should be processed without drama.
=============== =========== =========== =====================================================================================

The layout of the test set is typical of an oilfield repository, typically by well, with a well having an unspecified directory structure and a mix of file types in each directory.

The aim is that TotalDepth can process 97+% of the files in this archive in the formats that TotalDepth supports.

Large Test Set
----------------------------

:todo: Complete this


Synthetic Test Set
----------------------------

TotalDepth can generate arbitrary sized files in a number of formats and this test set is used for performance analysis.
This test set is not distributed with TotalDepth but the means to create it is.
