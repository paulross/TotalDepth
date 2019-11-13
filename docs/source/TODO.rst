.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Summary of TODO stuff

**************************
TODO's
**************************

This is a gathering place for features that are would be nice to have in future releases.
Priority numbers are 0 (not going to be done) and >0 which is an ever more important priority.

TotalDepth is currently at **Alpha**, release version |release|.


TotalDepth Improvements (General)
=================================


.. list-table:: **TotalDepth Improvements (General)**
    :widths: 20 60 10 10
    :header-rows: 1
    
    * - ID
      - Description
      - Priority
      - Status
    * - TD.Cython
      - Remove Cython as a dependency. Merge C++ replacement code.
      - 1
      - 
    * - TD.SQL
      - Extract data to database.
      - 1
      - 
    * - TD.GEO
      - Extract Latitude and Longitude as trustworthy metadata.
      - 1
      - 
    * - TD.svfs
      - Merge Sparse Virtual File System C/C++ code.
      - 1
      - 
    * - TD.test.slow
      - Move slow LIS test to tests/integration/ or mark as @slow.
      - 1
      - 
    * - TD.test.benchmark
      - Move benchmarking tests to benchmark/.
      - 1
      - 


LAS Improvements
===========================

.. list-table:: **LAS Improvements**
    :widths: 20 60 10 10
    :header-rows: 1
    
    * - ID
      - Description
      - Priority
      - Status
    * - LAS.fast
      - Merge the fast array parser with ~x50 performance.
      - 2
      - 
    * - LAS.zip
      - Read directly from .zip files.
      - 1
      - 
    * - LAS.v3
      - Support version 3.0. However this is barely used by the industry.
      - 0
      - 
    * - LAS.merge_O_P
      - Merge ``~O`` section int ``~P`` if correct format.
      - 1
      - 
    * - LAS.consist
      - Consistency checking of mutual data such as STRT/STOP/STEP.
      - 1
      - 


LIS Improvements
===========================


.. list-table:: **LIS Improvements**
    :widths: 20 60 10 10
    :header-rows: 1
    
    * - ID
      - Description
      - Priority
      - Status
    * - LIS.HDT
      - Expand/contract 'sub-channels' to actual channels and use the universal Frame Array.
      - 2
      - 
    * - LIS.XNAM
      - Full XNAM direct support for LIS-A.
      - 2
      - 
    * - LIS.index_c
      - Merge fast indexer in C for x100 performance.
      - 2
      - 
    * - LIS.index_inline
      - Insert or append binary representation of the index to the LIS file.
      - 1
      - 
    * - LIS.rc_over
      - Check Rep Code overflow/underflow on write.
      - 1
      - 
    * - LIS.test.slow
      - Move slow LIS test to tests/integration/ or mark as @slow.
      - 1
      - 

RP66V1 Improvements
=====================

.. list-table:: **RP66V1 Improvements**
    :widths: 20 60 10 10
    :header-rows: 1
    
    * - ID
      - Description
      - Priority
      - Status
    * - RP66V1.index_0
      - Add the multi-level index code implemented in C/C++ that is much faster and smaller. See 2019-11-12.
      - 2
      - 
    * - RP66V1.index_1
      - Mid level index implemented in C/C++.
      - 1
      - 
    * - RP66V1.RepCode
      - Add in the code that does Representation Code conversion in C/C++.
      - 1
      - 
    * - RP66V1.units
      - Full conformance with RP66V1 standard, RP66V2 standard and accepted practice.
      - 1
      - 
    * - RP66V1.plot
      - Plot RP66V1 files. See Plot.spec.
      - 1
      - 
    * - RP66V1.fail
      - When a file deviates from the standard then the user can specify what deviations are acceptable.
        Examples: UNITS Rep Code, multiple ORIGIN records.
      - 1
      - 
    * - RP66V1.test.benchmark
      - Make benchmarking tests to benchmark/.
      - 1
      - 


Plotting Improvements
=====================

.. list-table:: **Plotting Improvements**
    :widths: 20 60 10 10
    :header-rows: 1
    
    * - ID
      - Description
      - Priority
      - Status
    * - Plot.spec
      - There is quite a lot of technical debt built up since we added LgFormat support, this area needs a review.
        Implement the XML design.
      - 2
      - 
    * - Plot.head
      - Header: Some mud parameters being dropped.
      - 1
      - 
    * - Plot.perf
      - Benchmarks to characterise execution time and profiling.
      - 1
      - 
    * - Plot.cXML
      - Integrate the existing XML writer written in C for x4 speedup.
      - 1
      - 
    * - Plot.hover
      - Display values when hovering over curves in SVG.
      - 1
      - 
    * - Plot.PDF
      - PDF output of plots. Probably use reportlab.
      - 1
      - 


File Formats
==================


.. list-table:: **File Format Support**
    :widths: 20 60 10 10
    :header-rows: 1
    
    * - ID
      - Description
      - Priority
      - Status
    * - Format.RP66V2
      - Unused by the industry.
      - 0
      - 
    * - Format.WellLogML
      - Unused by the industry.
      - 0
      - 
    * - Format.ATLAS
      - Legacy. No publicly available examples.
      - 0
      - 
    * - Format.SEGY
      - Other FOSS project specialise in this.
      - 0
      - 
    * - Format.SEGD
      - Used at all?
      - 0
      - 

Frame Array Improvements
=========================

.. list-table:: **Frame Array Improvements**
    :widths: 20 60 10 10
    :header-rows: 1
    
    * - ID
      - Description
      - Priority
      - Status
    * - Frame.common
      - Common Frame Array code for all file formats.
      - 1
      - 
    * - Frame.buffer
      - Implement frame processing in C++ using the buffer protocol.
        Also shared memory with multiprocessing.
      - 1
      - 
