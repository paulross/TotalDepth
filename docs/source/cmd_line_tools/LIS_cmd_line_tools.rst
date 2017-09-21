.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Description of LIS command line tools

###############################
LIS Command Line Tools
###############################

This describes the command line tools that are available for processing LIS files.

=========================== ===========================================================================
Tool Name                   Description
=========================== ===========================================================================
``tdlisdetif``              Removes TIF markers from a LIS file.
``tdlisdumpframeset``       Writes out the frame values as a CSV file.
``tdlisindex``              Indexes a LIS file.
``tdlisplotlogpasses``      Plots the log data as SVG pages.
``tdlisscanlogidata``       Scans the logical data.
``tdlisscanlogirecord``     Scans all Logical records.
``tdlisscanphysrec``        Scans all the Physical Records.
``tdlistablehistogram``     Analyses the contents of table Logical Records.
``tdlistohtml``             Generates a HTML page about the LIS file.
``tdplotlogs``              Plots logs as SVG files.
=========================== ===========================================================================


***************************************************
Scanning LIS Files
***************************************************

These command line tools scan LIS files without changing them.

``tdlisscanphysrec``
----------------------

Scans a LIS79 file and reports the Physical Record structure.

Arguments
^^^^^^^^^

One argument that will be treated as a path to a LIS file.

Options
^^^^^^^^^

+--------------------------------------+---------------------------------------------------------------------------------+
| Option                               | Description                                                                     |
+======================================+=================================================================================+
| ``--version``                        | Show program's version number and exit                                          |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-h, --help``                       | Show this help message and exit.                                                |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-k, --keep-going``                 | Keep going as far as sensible. [default: False]                                 |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-l LOGLEVEL, --loglevel=LOGLEVEL`` | Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: 20]  |
+--------------------------------------+---------------------------------------------------------------------------------+

Examples
^^^^^^^^^

Example of scanning a non-TIF encoded file::

    $ ``tdlisscanphysrec`` LIS.lis 
    Cmd: ScanPhysRec.py LIS.lis
    PR:     tell()  Length    Attr  LD_len  RecNum  FilNum  ChkSum   LR Attr [Total LD]
    -------------------------------------- start --------------------------------------
    PR: 0x       0      62  0x   0      58  ------  ------  ------ 0x80 0x00 [      58]
    PR: 0x      3e    1024  0x   1    1020  ------  ------  ------ 0x22 0x00
    PR: 0x     43e    1024  0x   3    1020  ------  ------  ------ + --   --
    PR: 0x     83e    1024  0x   3    1020  ------  ------  ------ + --   --
    PR: 0x     c3e    1024  0x   3    1020  ------  ------  ------ + --   --
    PR: 0x    103e    1024  0x   3    1020  ------  ------  ------ + --   --
    PR: 0x    143e    1024  0x   3    1020  ------  ------  ------ + --   --
    PR: 0x    183e    1024  0x   3    1020  ------  ------  ------ + --   --
    PR: 0x    1c3e    1024  0x   3    1020  ------  ------  ------ + --   --
    PR: 0x    203e      34  0x   2      30  ------  ------  ------ + --   -- [    8190]
    PR: 0x    2060     304  0x   0     300  ------  ------  ------ 0x40 0x00 [     300]
    PR: 0x    2190    1014  0x   0    1010  ------  ------  ------ 0x00 0x00 [    1010]
    PR: 0x    2586    1014  0x   0    1010  ------  ------  ------ 0x00 0x00 [    1010]
    PR: 0x    297c    1014  0x   0    1010  ------  ------  ------ 0x00 0x00 [    1010]
    PR: 0x    2d72    1014  0x   0    1010  ------  ------  ------ 0x00 0x00 [    1010]
    PR: 0x    3168    1014  0x   0    1010  ------  ------  ------ 0x00 0x00 [    1010]
    PR: 0x    355e    1014  0x   0    1010  ------  ------  ------ 0x00 0x00 [    1010]
    PR: 0x    3954    1014  0x   0    1010  ------  ------  ------ 0x00 0x00 [    1010]
    PR: 0x    3d4a    1014  0x   0    1010  ------  ------  ------ 0x00 0x00 [    1010]
    PR: 0x    4140     942  0x   0     938  ------  ------  ------ 0x00 0x00 [     938]
    PR: 0x    44ee      62  0x   0      58  ------  ------  ------ 0x81 0x00 [      58]
    PR: EOF
    --------------------------------------- EOF ---------------------------------------
    PR Count: 21
    Histogram of Physical Record lengths:
    Bytes
       34 [1] | +++++++++++
       62 [2] | ++++++++++++++++++++++
      304 [1] | +++++++++++
      942 [1] | +++++++++++
     1014 [8] | ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
     1024 [8] | ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    CPU time =    0.001 (S)
    Bye, bye!

First ``tdlisscanphysrec`` echo's the command line then it scans the Physical Records an writes out a table that has the following columns:

==============  ============================================================================================================
Heading         Description 
==============  ============================================================================================================
``tell()``      The file position of the start of the Physical Record as a hex integer.
``Length``      The length of the Physical Record as a decimal integer.
``Attr``        The Physical Record Header attributes as a hex integer.
``LD_len``      The length of the logical data payload contained in this Physical Record.
``RecNum``      A record number from the Physical Record trailer if present, otherwise: ``------``
``FilNum``      A file number from the Physical Record trailer if present, otherwise: ``------``
``ChkSum``      A checksum from the Physical Record trailer if present, otherwise: ``------``
``LR``          Logical Record type from the Logical Record Header as a hex integer.
``Attr``        Logical Record attributes from the Logical Record Header as a hex integer. This is (almost?) always 0x00
``[Total LD]``  The total length of the logical data in the Logical Record if a terminator Physical Record, otherwise blank.
==============  ============================================================================================================

This is followed by an ASCII histogram of the lengths of all Physical Records with the following columns:

#. The size in bytes.
#. The frequency count.
#. A series of ``+`` that is proportionate to the frequency count.

If TIF markers are detected then the output adds TIF columns thus::

    TIF     ?  :        Type        Back        Next  PR:     tell()  Length    Attr  LD_len  RecNum  FilNum  ChkSum   LR Attr [Total LD]
    --------------------------------------------------------------- start ---------------------------------------------------------------
    TIF  True >:  0x       0  0x       0  0x      4a  PR: 0x       0      62  0x   0      58  ------  ------  ------ 0x80 0x00 [      58]
    TIF  True >:  0x       0  0x       0  0x     456  PR: 0x      4a    1024  0x   1    1020  ------  ------  ------ 0x22 0x00
    TIF  True >:  0x       0  0x      4a  0x     862  PR: 0x     456    1024  0x   3    1020  ------  ------  ------ + --   --
    TIF  True >:  0x       0  0x     456  0x     c6e  PR: 0x     862    1024  0x   3    1020  ------  ------  ------ + --   --
    TIF  True >:  0x       0  0x     862  0x    107a  PR: 0x     c6e    1024  0x   3    1020  ------  ------  ------ + --   --
    TIF  True >:  0x       0  0x     c6e  0x    1486  PR: 0x    107a    1024  0x   3    1020  ------  ------  ------ + --   --
    TIF  True >:  0x       0  0x    107a  0x    1892  PR: 0x    1486    1024  0x   3    1020  ------  ------  ------ + --   --
    TIF  True >:  0x       0  0x    1486  0x    1c9e  PR: 0x    1892    1024  0x   3    1020  ------  ------  ------ + --   --
    TIF  True >:  0x       0  0x    1892  0x    20aa  PR: 0x    1c9e    1024  0x   3    1020  ------  ------  ------ + --   --
    TIF  True >:  0x       0  0x    1c9e  0x    20ec  PR: 0x    20aa      54  0x   2      50  ------  ------  ------ + --   -- [    8210]

The additional columns are:

==============  ============================================================================================================
Heading         Description 
==============  ============================================================================================================
``?``           ?
``Type``        TIF marker type, 0 for in-file record, 1 for EOF.
``Back``        The file position of the precious TIF marker as a hex integer.
``Next``        The file position of the next TIF marker as a hex integer.
==============  ============================================================================================================

``tdlisscanlogirecord``
------------------------

Scans a LIS79 file and reports the Logical Record structure.

Arguments
^^^^^^^^^

One argument that will be treated as a path to a LIS file.

Options
^^^^^^^^^

+--------------------------------------+---------------------------------------------------------------------------------+
| Option                               | Description                                                                     |
+======================================+=================================================================================+
| ``--version``                        | Show program's version number and exit                                          |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-h, --help``                       | Show this help message and exit.                                                |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-k, --keep-going``                 | Keep going as far as sensible. [default: False]                                 |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-l LOGLEVEL, --loglevel=LOGLEVEL`` | Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: 20]  |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-v, --verbose``                    | Verbose output, this outputs a representation of table data and DFSRs.          |
+--------------------------------------+---------------------------------------------------------------------------------+


Examples
^^^^^^^^^

Example of scanning a LIS file::

    $ tdlisscanlogirecord RW.lis 
    Cmd: ScanLogiRec.py RW.lis
    0x00000000 <TotalDepth.LIS.core.LogiRec.LrFileHeadRead object at 0x1007981d0>: "File header"
    2012-02-08 17:43:45,078 WARNING  LrTableRead(): Discarding duplicate row b'BS7 ' in table b'CONS'
    2012-02-08 17:43:45,087 WARNING  LrTableRead.__init__(): Tell: 0x4a LD index: 0x32 Error: FileRead.unpack(): Bytes: b'\x00' not enough for struct that needs: 12 bytes.
    0x0000004a <TotalDepth.LIS.core.LogiRec.LrTableRead object at 0x100798210>: "Well site data"
    0x000020ec <TotalDepth.LIS.core.LogiRec.LrDFSRRead object at 0x1007981d0>: "Data format specification record"
    0x0006141c <TotalDepth.LIS.core.LogiRec.LrFileTailRead object at 0x10058e7d0>: "File trailer"
    0x00061466 <TotalDepth.LIS.core.LogiRec.LrFileHeadRead object at 0x10058e850>: "File header"
    2012-02-08 17:43:45,103 WARNING  LrTableRead(): Discarding duplicate row b'BS7 ' in table b'CONS'
    0x000614b0 <TotalDepth.LIS.core.LogiRec.LrTableRead object at 0x10058e7d0>: "Well site data"
    0x0006353e <TotalDepth.LIS.core.LogiRec.LrDFSRRead object at 0x10058e850>: "Data format specification record"
    0x00065a44 <TotalDepth.LIS.core.LogiRec.LrFileTailRead object at 0x10058e850>: "File trailer"
    0x00065a8e <TotalDepth.LIS.core.LogiRec.LrFileHeadRead object at 0x10058e7d0>: "File header"
    2012-02-08 17:43:45,116 WARNING  LrTableRead(): Discarding duplicate row b'BS7 ' in table b'CONS'
    2012-02-08 17:43:45,124 WARNING  LrTableRead.__init__(): Tell: 0x65ad8 LD index: 0x32 Error: FileRead.unpack(): Bytes: b'\x00' not enough for struct that needs: 12 bytes.
    0x00065ad8 <TotalDepth.LIS.core.LogiRec.LrTableRead object at 0x10058e850>: "Well site data"
    0x00067b7a <TotalDepth.LIS.core.LogiRec.LrDFSRRead object at 0x10058e7d0>: "Data format specification record"
    0x000d2c44 <TotalDepth.LIS.core.LogiRec.LrFileTailRead object at 0x10058e7d0>: "File trailer"
    CPU time =    0.064 (S)
    Bye, bye!

``tdlisscanlogidata``
----------------------

Scans a LIS79 file and reports the Logical Record structure.

Arguments
^^^^^^^^^

One argument that will be treated as a path to a LIS file.

Options
^^^^^^^^^

+--------------------------------------+---------------------------------------------------------------------------------+
| Option                               | Description                                                                     |
+======================================+=================================================================================+
| ``--version``                        | Show program's version number and exit                                          |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-h, --help``                       | Show this help message and exit.                                                |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-k, --keep-going``                 | Keep going as far as sensible. [default: False]                                 |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-d DUMP, --dump=DUMP``             | Dump complete data at these integer positions (ws                               |
|                                      | separated, hex/dec). [default: ]                                                |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-l LOGLEVEL, --loglevel=LOGLEVEL`` | Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: 20]  |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-v, --verbose``                    | Verbose output, this outputs a representation of table data and DFSRs.          |
+--------------------------------------+---------------------------------------------------------------------------------+

Examples
^^^^^^^^^

Example of scanning a LIS file::

    $ ``tdlisscanlogidata`` LIS.lis 
    Cmd: ScanLogiData.py LIS.lis
    Offset        Length  Type  Logical Data
    0x00000000        58   128  b'\x80\x00RUN1R .S01\x00\x00DAT2TF            '...
    0x0000003E      8190    34  b'"\x00IA\x04\x00TYPE    CONS\x00A\x04\x00MNEM    HI'...
    0x00002060       300    64  b'@\x00\x01\x02O\x00\x00\x02\x02O\x00\x00\x03\x04I\x00\x00\x00\x18\x04\x02O\x00\x01\x08\x04D?N\x07_\t'...
    0x00002190      1010     0  b"\x00\x00F@'\xde\xbe76\xfb@\xd6\x1a\xc0@\xd0\xdc\xc7D\xe0\xa6P\xba\x83\x18\x00F@&\xa6\xbe-"...
    0x00002586      1010     0  b'\x00\x00E\xff\xe9S\xbe:\x1f\x82@\xfe%\xc9@\xf7\xd5\xb7EA\x90\xda\xba\x83\x18\x00E\xff\xe6\xe3\xbe\x8a'...
    0x0000297C      1010     0  b'\x00\x00E\xff\x82\xea\xbe-\xe1\xa8@\xd83\xb6@\xf0\x0f\x0fET\x149D\xc8\x08\xc5E\xff\x80y\xbe-'...
    0x00002D72      1010     0  b'\x00\x00E\xff\x1c\x80\xbd\xba\x7f\x19@\xc4\xbf\xe8@y\x0b\xb3E\xc0\x08\x03D\xd5\xednE\xff\x1a\x10\xbd\xb4'...
    0x00003168      1010     0  b'\x00\x00E\xfe\xb6\x16\xbe\x12\xde\xf0@\xcbl\xe7@zF\xc2Ew\xba/D\xd0\xca\xd9E\xfe\xb3\xa6\xbe\x17'...
    0x0000355E      1010     0  b'\x00\x00E\xfeO\xac\xbe40\x85@\xcc4\x8d@of\xd9E\xc1F\xd8D\xd4\xaa+E\xfeM<\xbe6'...
    0x00003954      1010     0  b"\x00\x00E\xfd\xe9C\xbd\xb2\x19\xf0\xba\x83\x18\x00AK'%D\xed\x9d\xdbD\xd0\x17RE\xfd\xe6\xd3\xbd\xab"...
    0x00003D4A      1010     0  b'\x00\x00E\xfd\x82\xd9\xba\x83\x18\x00\xba\x83\x18\x00\xba\x83\x18\x00\xba\x83\x18\x00D\xd0\xad\xf3E\xfd\x80i\xba\x83'...
    0x00004140       938     0  b'\x00\x00E\xfd\x1co\xba\x83\x18\x00\xba\x83\x18\x00\xba\x83\x18\x00\xba\x83\x18\x00D\xd8\x8c\xb5E\xfd\x19\xff\xba\x83'...
    0x000044EE        58     0  b'\x81\x00RUN1R .S01\x00\x00DAT2TF            '...
    Histogram of Logical Data lengths:
    Bytes
       58 [1] | +++++++++++
      300 [1] | +++++++++++
      938 [1] | +++++++++++
     1010 [8] | ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
     8190 [1] | +++++++++++
    Histogram of Logical Record types:
      0 [9] | ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
     34 [1] | ++++++++++
     64 [1] | ++++++++++
    128 [1] | ++++++++++
    CPU time =    0.001 (S)
    Bye, bye!

First ``tdlisscanlogidata`` echo's the command line then it scans the file an writes out a table that has the following columns:

================  ============================================================================================================
Heading           Description 
================  ============================================================================================================
``Offset``        The file position of the start of the Physical Record as a hex integer.
``Length``        The length of the Logical Record as a decimal integer.
``Type``          The Logical Record type as a decimal integer.
``Logical Data``  The logical data payload. Only the first 32 bytes are shown. ``...`` is shown if the payload is longer than 32 bytes. If the verbose or dump options are given then all bytes are shown. 
================  ============================================================================================================

This is followed by an ASCII histogram of the lengths of all logical data with the following columns:

#. The size in bytes.
#. The frequency count.
#. A series of ``+`` that is proportionate to the frequency count.

This is followed by an ASCII histogram of the lengths of all Logical Record types with the following columns:

#. The size in bytes.
#. The frequency count.
#. A series of ``+`` that is proportionate to the frequency count.

Using the -d option expands the output when the file position value matches. So given the above then adding ``-d 0x44EE`` changes this::

    ...
    0x000044EE        58     0  b'\x81\x00RUN1R .S01\x00\x00DAT2TF            '...
    ...

To this::

    ...
    0x000044EE        58     0  b'\x81\x00RUN1R .S01\x00\x00DAT2TF                \x00 1024\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    ...


***************************************************
Extracting Data from LIS
***************************************************

``tdlisdumpframeset``
----------------------

Reads a LIS file and writes out tab separated values of each frame.

Arguments
^^^^^^^^^

#. The path to the LIS file.

Options
^^^^^^^^^

+--------------------------------------+---------------------------------------------------------------------------------+
| Option                               | Description                                                                     |
+======================================+=================================================================================+
| ``--version``                        | Show program's version number and exit                                          |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-h, --help``                       | Show this help message and exit.                                                |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-k, --keep-going``                 | Keep going as far as sensible. [default: False]                                 |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-l LOGLEVEL, --loglevel=LOGLEVEL`` | Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: 20]  |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-s, --summary``                    | Display summary only [default: False].                                          |
+--------------------------------------+---------------------------------------------------------------------------------+

Examples
^^^^^^^^^

::

    $ ``tdlisdumpframeset`` LIS.lis 
    Cmd: DumpFrameSet.py LIS.lis
    2012-02-09 08:41:38,372 INFO     Index.indexFile(): LIS.lis
    <TotalDepth.LIS.core.LogPass.LogPass object at 0x101a0c510>
    b'DEPT' [b'M   ']   b'SP  ' [b'MV  ']   b'SN  ' [b'OHMM']   b'ILD ' [b'OHMM']   b'CILD' [b'MMHO']   b'DT  ' [b'US/M']
    2052.98 -4.54908    1.34538 1.26348 386.599 -999.25
    2052.83 -5.1372     1.36062 1.29521 500.511 -999.25
    2052.68 -6.66747    1.38543 1.45786 595.623 -999.25
    2052.53 -6.69616    1.43226 1.61085 592.447 -999.25
    2052.37 -4.93782    1.51647 1.6622  590.846 -999.25
    2052.22 -4.38823    1.66883 1.70584 586.092 -999.25
    2052.07 -4.70347    1.8102  1.70607 577.873 -999.25
    ...
    1996.44 -999.25     -999.25 -999.25 -999.25 -999.25
    1996.29 -999.25     -999.25 -999.25 -999.25 -999.25
    1996.14 -999.25     -999.25 -999.25 -999.25 -999.25
    1995.99 -999.25     -999.25 -999.25 -999.25 -999.25
    
    Sc Name          Count      Min     Mean      Max Std Dev.       --       ==       ++     Bias    Drift Activity
    DEPT [M   ]        375    2e+03 2.02e+03 2.05e+03     16.5      374        0        0        1   -0.152 0.000144
    SP   [MV  ]        262    -13.7    -5.67   -0.769     2.66      124        0      137  -0.0498   0.0144    0.678
    SN   [OHMM]        252    0.866     1.36     1.98    0.277      123        0      128  -0.0199 -0.000719   0.0425
    ILD  [OHMM]        253    0.361     1.31     2.35    0.412       95        0      157   -0.246  0.00429    0.134
    CILD [MMHO]        253      387      787 1.75e+03      236      130        0      122   0.0317    0.205    0.101
    DT   [US/M]        292      133      320      460     42.5      139        0      152  -0.0447   -0.451    0.106
    CPU time =    0.047 (S)
    Bye, bye!

The summary table at the end has the following columns:

================  ============================================================================================================
Heading           Description 
================  ============================================================================================================
``Sc Name``       The sub-channel name and units of measure.
``Count``         The number of non-null values.
``Min``           Minimum value.
``Mean``          Arithmetic mean of values.
``Max``           Maximum value.
``Std Dev.``      Standard deviation of values.
``--``            Number of values that are a decrease over the previous value.
``==``            Number of values that are equal to the previous value.
``++``            Number of values that are an increase over the previous value.
``Bias``          (``--`` - ``++``) / total
``Drift``         (last value - first value) / number of values
``Activity``      The RMS exponent change.
================  ============================================================================================================


.. _TotalDepth-LIScmdline-LisToHtml:

``tdlistohtml``
----------------------

Generates HTML from input LIS file or directory to an output destination.

Arguments
^^^^^^^^^

#. The path to the input LIS file or directory.
#. The path to the output file or directory, any directories will be created as necessary.

Options
^^^^^^^^^

+--------------------------------------+---------------------------------------------------------------------------------+
| Option                               | Description                                                                     |
+======================================+=================================================================================+
| ``--version``                        | Show program's version number and exit                                          |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-h, --help``                       | Show this help message and exit.                                                |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-g, --glob``                       | File pattern match. [default none]                                              |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-j JOBS, --jobs=JOBS``             | Max processes when multiprocessing. Zero uses number of native CPUs [8].        |
|                                      | -1 disables multiprocessing. [default: -1]                                      |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-k, --keep-going``                 | Keep going as far as sensible. [default: False]                                 |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-l LOGLEVEL, --loglevel=LOGLEVEL`` | Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: 20]  |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-v, --verbose``                    | Verbose output, this outputs a representation of table data and DFSRs.          |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-r, --recursive``                  | Process input recursively. [default: False]                                     |
+--------------------------------------+---------------------------------------------------------------------------------+

Examples
^^^^^^^^^

Command to process a directory of LIS::

    $ ``tdlistohtml`` Simple LIS_plot/Simple_00

Output::

    Cmd: ``tdlistohtml`` Simple LIS_plot/Simple_00
    plotLogInfo:
    FileInfo: "Simple/LIS.lis" -> "LIS_plot/Simple_00/LIS.lis.html" 17 (kb) LR count=4 t=0.070
    FileInfo: "Simple/RW.lis" -> "LIS_plot/Simple_00/RW.lis.html" 843 (kb) LR count=12 t=3.206
    FileInfo: "Simple/RW_No_TIF.lis" -> "LIS_plot/Simple_00/RW_No_TIF.lis.html" 833 (kb) LR count=12 t=3.200
      CPU time =    6.568 (S)
    Exec. time =    6.568 (S)
    Bye, bye!

For each file the output lists:

* Input file.
* Output HTML file.
* File size.
* Count of Logical Records.
* Execution time.

In the output directory there will be an index.html file, for example:

.. image:: images/LisToHtml_index.png

The columns are:

* The name of the LIS file.
* The size of the LIS file.
* Count of Logical Records.
* Execution time.
* Processing rate.

In the linked HTML file is a summary of the content of the LIS file.

The Log Pass merits several entries, the first summarises the frame shape and the shape of each channel, for example:

.. image:: images/LisToHtml_LogPass_00.png

Then there is a couple of tables, the first summarises the X axis and the second summarises each channel (min, max mean etc.), for example:

.. image:: images/LisToHtml_LogPass_01.png

``tdlistablehistogram``
-------------------------

Provides a count of elements in LIS tables.

Arguments
^^^^^^^^^

#. A path to a LIS file or directory of LIS files.

Options
^^^^^^^^^

+--------------------------------------+---------------------------------------------------------------------------------+
| Option                               | Description                                                                     |
+======================================+=================================================================================+
| ``--version``                        | Show program's version number and exit                                          |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-h, --help``                       | Show this help message and exit.                                                |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-k, --keep-going``                 | Keep going as far as sensible. [default: False]                                 |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-r, --recursive``                  | Process input recursively. [default: False]                                     |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-s, --structure``                  | Display table structure (row/col range). [default: False]                       |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``--type=LRTYPE``                    | Logical record table type e.g. 34. [default: 34]                                |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``--name=NAME``                      | Logical record table name e.g. PRES. [default: ]                                |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``--row=ROW``                        | Logical record table row e.g. "GR  ". [default: ]                               |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``--col=COL``                        | Logical record table column e.g. "LEDG". [default: ]                            |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-l LOGLEVEL, --loglevel=LOGLEVEL`` | Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: 20]  |
+--------------------------------------+---------------------------------------------------------------------------------+

Examples
^^^^^^^^^

Count of all entries regardless of the table/row/column that they appear in::

    $ ``tdlistablehistogram`` -l 40 Simple/
    Cmd: TableHistogram.py -l 40 Simple/
    ======================== Count of all table entries =======================
    {"(34, b'    ')": 1414,
     "(34, b'0.445')": 5,
     "(34, b'0.621')": 5,
     "(34, b'013529700231')": 7,
     "(34, b'1')": 5,
     "(34, b'1.22')": 5,
     "(34, b'1.70')": 2,
     "(34, b'116')": 2,
     "(34, b'12.25')": 2,
     "(34, b'15')": 5,
     "(34, b'15-4-76')": 5,
     "(34, b'17')": 5,
     "(34, b'17.5')": 5,
     "(34, b'19')": 5,
     "(34, b'1976')": 7,
     "(34, b'2')": 2,
     "(34, b'2055.0')": 2,
     "(34, b'2071.2')": 4,
     "(34, b'25')": 2,
     "(34, b'25-6-76')": 2,
     "(34, b'257.0')": 7,
    ...
     "(34, b'WN  ')": 7,
     "(34, b'YEAR')": 7,
     '(34,)': 443}
    ====================== Count of all table entries END =====================
    CPU time =    0.205 (S)
    Bye, bye!

The result is a dictionary that has the key as a pair ``(lr_type, cell_value)`` and the value as a count of the number of occurrences.

If the ``-s`` option is used then an additional summary is provided::

    =============================== Row entries ===============================
    {(34, b'CONS', b'APIN'): 7,
     (34, b'CONS', b'BLI '): 7,
     (34, b'CONS', b'BS1 '): 7,
     (34, b'CONS', b'BS2 '): 7,
     (34, b'CONS', b'BS3 '): 7,
    ...
     (34, b'CONS', b'WN  '): 7,
     (34, b'CONS', b'YEAR'): 7}
    ============================= Row entries END =============================
    ============================== Column entries =============================
    {(34, b'CONS', b'ALLO'): 707,
     (34, b'CONS', b'MNEM'): 707,
     (34, b'CONS', b'PUNI'): 707,
     (34, b'CONS', b'TUNI'): 707,
     (34, b'CONS', b'VALU'): 707}
    ============================ Column entries END ===========================

This are dictionaries that have the key as a tripple ``(lr_type, table_name, row_name)`` and ``(lr_type, table_name, column_name)``
respectively and the value as a count of the number of occurrences.

Filtering by Logical Record type, table name, row name and column name (note quoting of spaces)::

    $ ``tdlistablehistogram`` -l 40 --type=34 --name=CONS --row="WN  " --col=VALU Simple/
    Cmd: TableHistogram.py -l 40 --type=34 --name=CONS --row=WN   --col=VALU Simple/
    ======================== Count of all table entries =======================
    {"(34, b'CONS', b'WN  ', b'VALU', b'B897 - 14')": 1,
     "(34, b'CONS', b'WN  ', b'VALU', b'DIEKSAND 111A')": 3,
     "(34, b'CONS', b'WN  ', b'VALU', b'VOELKERSEN AZ4')": 3}
    ====================== Count of all table entries END =====================
    CPU time =    0.174 (S)
    Bye, bye!

The result is a dictionary that has the key as a quadruple ``(lr_type, table_name, row_name, column_name, cell_value)`` and
the value as a count of the number of occurrences.

***************************************************
LIS Developer Tools
***************************************************

``tdlisdetif``
----------------------

Takes an input LIS79 file and writes out a new one without TIF markers.

Arguments
^^^^^^^^^

#. The path to the input LIS file.
#. The path to the output LIS file, any directories will be created as necessary.

Options
^^^^^^^^^

+--------------------------------------+---------------------------------------------------------------------------------+
| Option                               | Description                                                                     |
+======================================+=================================================================================+
| ``--version``                        | Show program's version number and exit                                          |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-h, --help``                       | Show this help message and exit.                                                |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-n, --nervous``                    | Nervous mode (do no harm). [default: False]                                     |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-l LOGLEVEL, --loglevel=LOGLEVEL`` | Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: 20]  |
+--------------------------------------+---------------------------------------------------------------------------------+


Examples
^^^^^^^^^

DeTIF with nervous mode just examines the file::

    $ ``tdlisdetif`` -n RW.lis RW_No_TIF.lis 
    Cmd: DeTif.py -n RW.lis RW_No_TIF.lis
    stripTif(): Tell: 0x00000000 Len: 0x00000000 TIF: TIF  True >:  0x       0  0x       0  0x       0
    stripTif(): Tell: 0x0000000c Len: 0x0000003e TIF: TIF  True >:  0x       0  0x       0  0x      4a
    stripTif(): Tell: 0x00000056 Len: 0x00000400 TIF: TIF  True >:  0x       0  0x       0  0x     456
    stripTif(): Tell: 0x00000462 Len: 0x00000400 TIF: TIF  True >:  0x       0  0x      4a  0x     862
    stripTif(): Tell: 0x0000086e Len: 0x00000400 TIF: TIF  True >:  0x       0  0x     456  0x     c6e
    stripTif(): Tell: 0x00000c7a Len: 0x00000400 TIF: TIF  True >:  0x       0  0x     862  0x    107a
    stripTif(): Tell: 0x00001086 Len: 0x00000400 TIF: TIF  True >:  0x       0  0x     c6e  0x    1486
    stripTif(): Tell: 0x00001492 Len: 0x00000400 TIF: TIF  True >:  0x       0  0x    107a  0x    1892
    stripTif(): Tell: 0x0000189e Len: 0x00000400 TIF: TIF  True >:  0x       0  0x    1486  0x    1c9e
    ...
    stripTif(): Tell: 0x000d2b4e Len: 0x000000f6 TIF: TIF  True >:  0x       0  0x   d2748  0x   d2c44
    stripTif(): Tell: 0x000d2c50 Len: 0x0000003e TIF: TIF  True >:  0x       0  0x   d2b42  0x   d2c8e
      CPU time =    0.022 (S)
    Exec. time =    0.022 (S)
    Bye, bye!

DeTIF with write::

    $ ``tdlisdetif`` RW.lis RW_No_TIF.lis 
    Cmd: DeTif.py RW.lis RW_No_TIF.lis
      CPU time =    0.019 (S)
    Exec. time =    0.019 (S)
    Bye, bye!

``tdlisindex``
----------------------

This indexes a LIS file and prints out the result. It can also provide some performance measurements of the indexing operation. See :ref:`TotalDepth-tech-indexing` for more information about the design and performance of LIS indexing.

Arguments
^^^^^^^^^

#. The path to a LIS file or a directory of LIS files.

Options
^^^^^^^^^

+--------------------------------------+---------------------------------------------------------------------------------+
| Option                               | Description                                                                     |
+======================================+=================================================================================+
| ``--version``                        | Show program's version number and exit                                          |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-h, --help``                       | Show this help message and exit.                                                |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-k, --keep-going``                 | Keep going as far as sensible. [default: False]                                 |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-l LOGLEVEL, --loglevel=LOGLEVEL`` | Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: 20]  |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-j JOBS, --jobs=JOBS``             | Max processes when multiprocessing. Zero uses number of native CPUs [8].        |
|                                      | -1 disables multiprocessing. [default: -1]                                      |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-t TIMES, --times=TIMES``          | Number of times to repeat the read [default: 1]                                 |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-s, --statistics``                 | Dump timing statistics. [default: False]                                        |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-v, --verbose``                    | Verbose output, this outputs a representation of table data and DFSRs.          |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-r, --recursive``                  | Process input recursively. [default: False]                                     |
+--------------------------------------+---------------------------------------------------------------------------------+


Examples
^^^^^^^^^

Simple scan of a single file::

    $ ``tdlisindex`` Simple/LIS.lis
    Cmd: Index.py Simple/LIS.lis
    2012-02-09 09:36:28,039 INFO     Index.indexFile(): Simple/LIS.lis
    File size: 17708 (0.017 MB) Reference Time: 0.002459 (s) for Simple/LIS.lis pickleLen=4351 jsonLen=-1
    Summary:
    Results:        1
     Errors:        0
      Total:        1
    CPU time =    0.004 (S)
    Bye, bye!

Simple scan of a single file with verbose output::

    $ ``tdlisindex`` -v Simple/LIS.lis 
    Cmd: Index.py -v Simple/LIS.lis
    2012-02-09 09:39:29,493 INFO     Index.indexFile(): Simple/LIS.lis
    <TotalDepth.LIS.core.FileIndexer.FileIndex object at 0x10197fdd0> "Simple/LIS.lis" [4]:
      tell: 0x00000000 type=128 <TotalDepth.LIS.core.FileIndexer.IndexFileHead object at 0x10197fe10>
      tell: 0x0000003e type= 34 name=b'CONS' <TotalDepth.LIS.core.FileIndexer.IndexTable object at 0x10197fe90>
      <TotalDepth.LIS.core.LogPass.LogPass object at 0x101b071d0>
      tell: 0x000044ee type=129 <TotalDepth.LIS.core.FileIndexer.IndexFileTail object at 0x101b07790>
    =============================== All records ===============================
    tell: 0x00000000 type=128 <TotalDepth.LIS.core.FileIndexer.IndexFileHead object at 0x10197fe10>
    tell: 0x0000003e type= 34 name=b'CONS' <TotalDepth.LIS.core.FileIndexer.IndexTable object at 0x10197fe90>
    <TotalDepth.LIS.core.LogPass.LogPass object at 0x101b071d0>
    tell: 0x000044ee type=129 <TotalDepth.LIS.core.FileIndexer.IndexFileTail object at 0x101b07790>
    ============================= All records DONE ============================
    ================================ Log Passes ===============================
    LogPass <TotalDepth.LIS.core.LogPass.LogPass object at 0x101b071d0>: 
           DFSR: <TotalDepth.LIS.core.LogiRec.LrDFSRRead object at 0x10197ff90>: "Data format specification record"
     Frame plan: <TotalDepth.LIS.core.Type01Plan.FrameSetPlan object at 0x101b07210>: indr=0 frame length=24 channels=6
       Channels: [b'DEPT', b'SP  ', b'SN  ', b'ILD ', b'CILD', b'DT  ']
            RLE: <TotalDepth.LIS.core.Rle.RLEType01 object at 0x101b07250>: func=None: [RLEItemType01: datum=8592 stride=1014 repeat=7 frames=42, RLEItemType01: datum=16704 stride=None repeat=0 frames=39]
         X axis: first=2052.983 last=1995.986 frames=375 overall spacing=-0.1524 in optical units=b'M   ' (actual units=b'M   ')
      Frame set: None
    
    ============================= Log Passes DONE =============================
    =============================== Plot Records ==============================
    ============================ Plot Records DONE ============================
       Min: 0.003 (s)
       Max: 0.003 (s)
      Mean: 0.003 (s)
    File size: 17708 (0.017 MB) Reference Time: 0.002529 (s) for Simple/LIS.lis pickleLen=4351 jsonLen=-1
    Summary:
    Results:        1
     Errors:        0
      Total:        1
    CPU time =    0.004 (S)
    Bye, bye!

Scan of a directory (recursively) indexing each file 11 times and writing out statistics::

    $ ``tdlisindex`` -t11 -s -l 40 Simple/
    Cmd: Index.py -t11 -s -l 40 ../../../../TDTestData/LIS/Simple
    File size: 17708 (0.017 MB) Reference Time: 0.001670 (s) for Simple/LIS.lis pickleLen=4351 jsonLen=-1
    File size: 863374 (0.823 MB) Reference Time: 0.043411 (s) for Simple/RW.lis pickleLen=18231 jsonLen=-1
    File size: 853030 (0.814 MB) Reference Time: 0.039238 (s) for Simple/RW_No_TIF.lis pickleLen=18238 jsonLen=-1
    Summary:
    Size (kb)   Time (s)
    17.293      0.001670
    843.139     0.043411
    833.037     0.039238
    
    Files: 3
    Errors: 0
    CPU time =    0.938 (S)
    Bye, bye!

``tdXlisrandomframesetread``
------------------------------

For developers only. This is designed to measure the performance of loading and iterating across a frame-set.

