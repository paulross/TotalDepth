History
=========

0.4.0 (2021-09-11)
-----------------------------

* General
    * Add SLB parameter and unit online lookup.
    * Add detection of CFBF, EBCDIC, RCD, SEG-Y, STK, PDS binary file types.
    * Python 3.6 no longer supported, although it will most likely work.

* Specific File formats

    * BIT

        * Support Western Atlas BIT files.
        * Add BIT file conversion to LAS.
        * BIT float to bytes (ISINGL) encoding.

    * DAT

        * Add DAT file support using the common FrameArray.

    * LAS

        * Add tdlastohtml as an entry point.
        * Parser improvements.
        * LAS reader now ignores duplicate channels if requested.
        * Add LAS variants to binary_file_type.
        * LAS FrameArray writing now in TotalDepth.common.LogPass

    * LIS

        * Add LIS to LAS conversion.
        * Kill off XNAM LIS support.
        * Better handling of LIS Physical Record padding.
        * Fix for LIS indexer when the DFSR is missing.
        * Adds generation of AREA patterns in SVG.
        * Creates PNG pattern files from XML data. Provides an API to pattern files and Data URI Scheme inline implementations.

    * RP66V1

        *  Prepare for RP66V1 C/C++ code. Update to Python 3.8, 3.9, 3.10.
        * Add units conversion.


0.3.1 (2020-06-15)
-----------------------------

* Fixes for builds on Linux and Windows.

0.3.0 (2020-01-01)
-----------------------------

* Adds full RP66V1 support.
* Tested against multi GB data set.

0.2.1 (2018-04-21)
-----------------------------

* Minor fixes.


0.2.0 (2017-09-25)
-----------------------------

* Moved to Github: https://github.com/paulross/TotalDepth
* First release on PyPI.

0.1.0 (2012-03-03)
-----------------------------

* First release on Sourceforge: https://sourceforge.net/projects/TotalDepth/ registered: 2011-10-02

Earlier versions (unreleased):

* OpenLis - 2010-11-11 to 2011-08-01
* PyLis - 2009 to 2010
