.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Summary of TODO stuff


.. role:: strike
    :class: strike

**************************
TODO's
**************************

TotalDepth is work-in-progress.
This is a gathering place for features that are would be nice to have in future releases.
Priority numbers are 0 (not going to be done) and >0 which is an ever more important priority.
Work is the estimated amount of work from 1 upwards.


If you find a bug or need a feature then raise an `issue with TotalDepth <https://github.com/paulross/TotalDepth/issues>`_.

TotalDepth is currently at **Beta**, development version |version|, release version |release|.


TotalDepth Improvements (General)
=================================


.. list-table:: **TotalDepth Improvements (General)**
    :widths: 20 40 15 10 40
    :header-rows: 1
    
    * - ID
      - Description
      - Priority
      - Work
      - Status
    * - TD.Cython
      - Remove Cython as a dependency. Merge C++ replacement code.
      - 1
      - 1
      - 
    * - TD.SQL
      - Extract data to database.
      - 1
      - 3
      - 
    * - TD.GEO
      - Extract Latitude and Longitude as trustworthy metadata.
      - 1
      - 3
      - 
    * - TD.svfs
      - Merge Sparse Virtual File System C/C++ code.
      - 1
      - 4
      - 
    * - :strike:`TD.test.slow`
      - :strike:`Move slow LIS test to tests/integration/ or mark as @slow.`
      - :strike:`1`
      - :strike:`1`
      - :strike:`DONE: v0.3.0`
    * - TD.test.benchmark
      - Move benchmarking tests to benchmark/.
      - 1
      - 2
      - 


LAS Improvements
===========================

.. list-table:: **LAS Improvements**
    :widths: 20 40 15 10 40
    :header-rows: 1
    
    * - ID
      - Description
      - Priority
      - Work
      - Status
    * - LAS.fast
      - Merge the fast array parser with ~50x performance.
      - 2
      - 3
      - 
    * - LAS.zip
      - Read directly from .zip files.
      - 1
      - 1
      - 
    * - LAS.v3
      - Support version 3.0. However this is barely used by the industry.
      - 0
      - N/A
      - 
    * - LAS.merge_O_P
      - Merge ``~O`` section into ``~P`` if correct format.
      - 1
      - 1
      - 
    * - LAS.consist
      - Consistency checking of mutual data such as STRT/STOP/STEP.
      - 1
      - 1
      - 


LIS Improvements
===========================


.. list-table:: **LIS Improvements**
    :widths: 20 40 15 10 40
    :header-rows: 1
    
    * - ID
      - Description
      - Priority
      - Work
      - Status
    * - LIS.HDT
      - Expand/contract 'sub-channels' to actual channels and use the universal Frame Array.
      - 2
      - 3
      - 
    * - :strike:`LIS.XNAM`
      - :strike:`Full XNAM direct support for LIS-A.`
      - :strike:`0`
      - :strike:`3`
      - :strike:`No. These only occur in a small number from a minority producer using specialised software. They do not occur in mainstream LIS files.`
    * - LIS.index_c
      - Merge fast indexer in C for 100x performance.
      - 2
      - 3
      - 
    * - LIS.index_inline
      - Insert or append binary representation of the index to the LIS file.
      - 1
      - 3
      - 
    * - LIS.rc_over
      - Check Rep Code overflow/underflow on write.
      - 1
      - 1
      - 
    * - :strike:`LIS.test.slow`
      - :strike:`Move slow LIS test to tests/integration/ or mark as @slow.`
      - :strike:`1`
      - :strike:`1`
      - :strike:`DONE: v0.3.0`

RP66V1 Improvements
=====================

.. list-table:: **RP66V1 Improvements**
    :widths: 20 40 15 10 40
    :header-rows: 1
    
    * - ID
      - Description
      - Priority
      - Work
      - Status
    * - RP66V1.test.benchmark
      - Write benchmarking tests in :file:`benchmark/` .
      - 2
      - 2
      - 
    * - RP66V1.index_0
      - Add the multi-level index code implemented in C/C++ that is much faster and smaller. See 2019-11-12.
      - 2
      - 3
      - 
    * - RP66V1.index_1
      - Mid level index implemented in C/C++.
      - 1
      - 3
      - 
    * - RP66V1.RepCode
      - Add in the code that does Representation Code conversion in C/C++.
      - 1
      - 3
      - 
    * - RP66V1.numpy.read
      - Directly populate the Frame Array in Numpy from C/C++. See also Frame.buffer.
      - 1
      - 3
      - 
    * - RP66V1.units
      - Conformance of unit conversion with the RP66V1 and, possibly, RP66V2 standard.
        
        NOTE: The RP66V2 standard is expanded on RP66V1 but barely used.
        Many producers deviate from these standards in any case.
      - 1
      - 2
      - 
    * - RP66V1.plot
      - Plot RP66V1 files. See Plot.spec.
      - 1
      - 3
      - 
    * - RP66V1.fail
      - When a file deviates from the standard then the user can specify what deviations are acceptable.
        Examples: UNITS Rep Code, multiple ORIGIN and CHANNEL records.
      - 1
      - 2
      - 


Plotting Improvements
=====================

.. list-table:: **Plotting Improvements**
    :widths: 20 40 15 10 40
    :header-rows: 1
    
    * - ID
      - Description
      - Priority
      - Work
      - Status
    * - Plot.spec
      - There is quite a lot of technical debt built up since we added LgFormat support, this area needs a review.
        Implement the XML design.
      - 2
      - 4
      - 
    * - Plot.head
      - Header: Some mud parameters being dropped.
      - 1
      - 2
      - 
    * - Plot.perf
      - Benchmarks to characterise execution time and profiling.
      - 1
      - 3
      - 
    * - Plot.cXML
      - Integrate the existing XML writer written in C for x4 speedup.
      - 1
      - 3
      - 
    * - Plot.hover
      - Display values when hovering over curves in SVG.
      - 1
      - 3
      - 
    * - Plot.PDF
      - PDF output of plots. Probably use reportlab.
      - 1
      - 4
      - 


File Formats
==================


.. list-table:: **File Format Support**
    :widths: 20 40 15 10 40
    :header-rows: 1
    
    * - ID
      - Description
      - Priority
      - Work
      - Status
    * - Format.RP66V2
      - Unused by the industry.
      - 0
      - N/A
      - 
    * - Format.WellLogML
      - Unused by the industry.
      - 0
      - N/A
      - 
    * - :strike:`Format.ATLAS_BIT`
      - :strike:`Legacy format.`
      - :strike:`1`
      - :strike:`1`
      - :strike:`DONE v0.4.0`
    * - Format.SEGY
      - Other FOSS projects specialise in this.
      - 0
      - N/A
      - 
    * - Format.SEGD
      - Used at all?
      - 0
      - N/A
      - 
    * - :strike:`Format.DAT`
      - :strike:`An informal format used for mud logs.`
      - :strike:`1`
      - :strike:`1`
      - :strike:`DONE v0.4.0`

Frame Array Improvements
=========================

.. list-table:: **Frame Array Improvements**
    :widths: 20 40 15 10 40
    :header-rows: 1
    
    * - ID
      - Description
      - Priority
      - Work
      - Status
    * - Frame.common
      - Common Frame Array code for all file formats.
      - 1
      - 3
      - 
    * - Frame.buffer
      - Implement frame processing in C++ using the buffer protocol.
        Also shared memory with multiprocessing.
      - 1
      - 3
      - 
