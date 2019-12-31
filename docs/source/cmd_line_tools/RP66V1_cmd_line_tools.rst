.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Description of RP66V1 command line tools

***************************
RP66V1 Command Line Tools
***************************

This describes the command line tools that are available for processing RP66V1 files. They are:

=========================== =====================================================================================
Tool Name                   Description
=========================== =====================================================================================
``tdrp66v1scanhtml``        Scans RP66V1 file(s) and writes out a summary in HTML.
``tdrp66v1tolas``           Converts RP66V1 file(s) to a set of LAS files.
``tdrp66v1indexpickle``     Indexes RP66V1 file(s) and writes the indexes for future use as Python pickle files.
``tdrp66v1indexxml``        Indexes RP66V1 file(s) and writes the indexes as XML files.
``tdrp66v1scan``            Scans RP66V1 file at various levels of structure.
=========================== =====================================================================================



.. _cmd_line_tools_rp66v1_tdrp66v1scanhtml:


Creating HTML Pages from RP66V1 Files with ``tdrp66v1scanhtml``
===================================================================

This takes a RP66V1 file or directory of them and writes out an HTML summary of each Logical File.
The summary includes each non-encrypted EFLR and Log Pass.
The frames in the log pass can be sub-sampled by using ``--frame-slice`` which speeds things up when processing large files.

Arguments
-----------

The first argument is the path to a RP66V1 file or directory.
The second argument is the path to write the output to.

Options
-------


  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -k, --keep-going      Keep going as far as sensible. Default: False.
  -v, --verbose         Increase verbosity, additive [default: 0]
  -r, --recurse         Process the input recursively. Default: False.
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        Log Level as an integer or symbol. (0<->NOTSET,
                        10<->DEBUG, 20<->INFO, 30<->WARNING, 40<->ERROR,
                        50<->CRITICAL) [default: 20]
  -j JOBS, --jobs JOBS  Max processes when multiprocessing.Zero uses number of
                        native CPUs [8]. Negative value disables
                        multiprocessing code. Default: -1.
  -e, --encrypted       Output encrypted Logical Records as well. [default:
                        False]
  --frame-slice FRAME_SLICE
                        Do not process all frames but sample or slice the
                        frames. SAMPLE: Sample is of the form "N" so a maximum
                        of N frames, roughly regularly spaced, will be
                        processed. N must be +ve, non-zero integer. Example:
                        "64" - process a maximum of 64 frames. SLICE: Slice
                        the frames is of the form start,stop,step as a comma
                        separated list. Values can be absent or "None".
                        Examples: ",," - every frame, ",,2" - every other
                        frame, ",10," - frames 0 to 9, "4,10,2" - frames 4, 6,
                        8, "40,-1,4" - every fourth frame from 40 to the end.
                        Results will be truncated by frame array length.
                        [default: ",," i.e. all frames]
  --log-process LOG_PROCESS
                        Writes process data such as memory usage as a log INFO
                        line every LOG_PROCESS seconds. If 0.0 no process data
                        is logged. [default: 0.0]
  --gnuplot GNUPLOT     Directory to write the gnuplot data.


Here is an example of `the HTML summary of a single RP66V1 file <../_static/RP66V1/example.html>`_ .


.. _cmd_line_tools_rp66v1_tdrp66v1tolas:

Converting RP66V1 Files to LAS Files with ``tdrp66v1tolas``
===================================================================

This takes a RP66V1 file or directory of them and writes out a set of LAS files.
A single LAS file is written for each Log Pass in each Logical Record.

The frames in the log pass can be sub-sampled by using ``--frame-slice`` which speeds things up when processing large files.
The ``--channels`` option can be used to limit channels.

Where a channel has multiple values, and LAS con only record a single value, then the ``--array-reduction`` flag can be used to specify how the single value is computed.
The allowable values are ``{first,max,mean,median,min}`` and the default is ``mean``.

LAS File Naming Convention
--------------------------

One RP66V1 file produces one or more LAS files.
LAS file names are of the form::

    {RP66V1_File_no_extension}_{logical_file_number}_{frame_array_name}

Processing a Single RP66V1 File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Given the path out the LAS files will be named ``{path_out}_{logical_file_number}_{frame_array_name}.las``

For example ``tdrp66v1tolas foo.dlis bar/baz`` might create::

    bar/baz_0_2000T.las
    bar/baz_0_800T.las
    bar/baz_1_2000T.las
    bar/baz_1_800T.las

and so on.

Processing a Directory of RP66V1 Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Given the path out the LAS files will be named:

    ``{path_out}/{RP66V1_File}_{logical_file_number}_{frame_array_name}.las``

For example ``tdrp66v1tolas foo/ bar/baz`` might create::

    bar/baz/bit_0_2000T.las
    bar/baz/bit_0_800T.las
    bar/baz/bit_1_2000T.las
    bar/baz/bit_1_800T.las

and so on.

The output directory structure will mirror the input directory structure.

Arguments
-----------

The first argument is the path to a RP66V1 file or directory.
The second argument is the path to write the output to.

Options
-------

    -h, --help            show this help message and exit
    --version             show program's version number and exit
    -k, --keep-going      Keep going as far as sensible. Default: False.
    -v, --verbose         Increase verbosity, additive [default: 0]
    -r, --recurse         Process the input recursively. Default: False.
    -l LOG_LEVEL, --log-level LOG_LEVEL
                        Log Level as an integer or symbol. (0<->NOTSET,
                        10<->DEBUG, 20<->INFO, 30<->WARNING, 40<->ERROR,
                        50<->CRITICAL) [default: 20]
    -j JOBS, --jobs JOBS  Max processes when multiprocessing.Zero uses number of
                        native CPUs [8]. Negative value disables
                        multiprocessing code. Default: -1.
    --frame-slice FRAME_SLICE
                        Do not process all frames but sample or slice the
                        frames. SAMPLE: Sample is of the form "N" so a maximum
                        of N frames, roughly regularly spaced, will be
                        processed. N must be +ve, non-zero integer. Example:
                        "64" - process a maximum of 64 frames. SLICE: Slice
                        the frames is of the form start,stop,step as a comma
                        separated list. Values can be absent or "None".
                        Examples: ",," - every frame, ",,2" - every other
                        frame, ",10," - frames 0 to 9, "4,10,2" - frames 4, 6,
                        8, "40,-1,4" - every fourth frame from 40 to the end.
                        Results will be truncated by frame array length. Use
                        '?' to see what frames are available [default: ",,"
                        i.e. all frames]
    --log-process LOG_PROCESS
                        Writes process data such as memory usage as a log INFO
                        line every LOG_PROCESS seconds. If 0.0 no process data
                        is logged. [default: 0.0]
    --gnuplot GNUPLOT     Directory to write the gnuplot data.
    --array-reduction ARRAY_REDUCTION
                        Method to reduce multidimensional channel data to a
                        single value. One of {first,max,mean,median,min} [default: first]
    --channels CHANNELS   Comma separated list of channels to write out (X axis
                        is always included). Use '?' to see what channels
                        exist without writing anything. [default: ""]
    --field-width FIELD_WIDTH
                        Field width for array data [default: 16].
    --float-format FLOAT_FORMAT
                        Floating point format for array data [default: ".3f"].
                        


Examples
-----------


Finding out what Channels and Frames Exist:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use ``--channels=?`` and/or ``--frame-slice=?`` to see what channels and frames exist in the RP66V1 file.

.. code-block:: console

    $ tdrp66v1tolas --channels=? --frame-slice=? example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS example_data/LAS/206_05a-_3_DWL_DWL_WIRE_258276498
    Logical file [0000]: <TotalDepth.RP66V1.core.LogicalFile.LogicalFile object at 0x109fd50f0>
      Frame Array: b'2000T'
      Channels: b'TIME,TDEP,TENS_SL,DEPT_SL'
      X axis: FrameChannel: OBNAME: O: 2 C: 4 I: b'TIME'            Rc:   2 Co:    1 Un: b'ms'        Di: [1] b'1 second River Time'
      Frames: 921 from 16677259.0 to 17597260.0 interval 1000.0010869565217 [b'ms']

      Frame Array: b'800T'
      Channels: b'TIME,TDEP,ETIM,LMVL,UMVL,CFLA,OCD,RCMD,RCPP,CMRT,RCNU,DCFL,DFS,DZER,RHMD,HMRT,RHV,RLSW,MNU,S1CY,S2CY,RSCU,RSTS,UCFL,CARC,CMDV,CMPP,CNU,HMDV,HV,LSWI,SCUR,SSTA,RCMP,RHPP,RRPP,CMPR,HPPR,RPPV,SMSC,CMCU,HMCU,CMLP'
      X axis: FrameChannel: OBNAME: O: 2 C: 5 I: b'TIME'            Rc:   2 Co:    1 Un: b'ms'        Di: [1] b'400 milli-second time channel'
      Frames: 2301 from 16677259.0 to 17597260.0 interval 400.0004347826087 [b'ms']


Processing a Single File
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ tdrp66v1tolas example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS example_data/LAS/206_05a-_3_DWL_DWL_WIRE_258276498
      Input    Output LAS Count  Time  Ratio  ms/Mb Exception                                                         Path
    ------- --------- --------- ----- ------ ------ --------- ------------------------------------------------------------
    540,372 1,812,131         2 1.816 335.3% 3524.1     False "example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS"
    Execution time =    1.819 (S)
    Out of  1 processed 1 files of total size 540,372 input bytes
    Wrote 1,812,131 output bytes, ratio: 335.349% at 3529.3 ms/Mb
    $ ll example_data/LAS/
    total 4600
    -rw-r--r--  1 xxxxxxxx  staff    94317 28 Oct 10:19 206_05a-_3_DWL_DWL_WIRE_258276498_0_2000T.las
    -rw-r--r--  1 xxxxxxxx  staff  1717814 28 Oct 10:20 206_05a-_3_DWL_DWL_WIRE_258276498_0_800T.las

The LAS files look like this:

.. code-block:: console

    $ head -n20 example_data/LAS/206_05a-_3_DWL_DWL_WIRE_258276498_0_2000T.las
    ~Version Information Section
    VERS.          2.0                                     : CWLS Log ASCII Standard - VERSION 2.0
    WRAP.          NO                                      : One Line per depth step
    PROD.          TotalDepth                              : LAS Producer
    PROG.          TotalDepth.RP66V1.ToLAS 0.1.1           : LAS Program name and version
    CREA.          2019-10-28 10:30                        : LAS Creation date [YYYY-mm-dd HH:MM]
    DLIS_CREA.     2011-08-20 22:48                        : DLIS Creation date and time [YYYY-mm-dd HH:MM]
    SOURCE.        206_05a-_3_DWL_DWL_WIRE_258276498.DLIS  : DLIS File Name
    FILE-ID.       MSCT_197LTP                             : File Identification Number
    LOGICAL-FILE.  0                                       : Logical File number in the DLIS file
    FRAME-ARRAY.   2000T                                   : Identity of the Frame Array in the Logical File
    ~Well Information Section
    #MNEM.UNIT  DATA                         DESCRIPTION
    #----.----  ----                         -----------
    STRT.ms     16677259.0                   : Start X
    STOP.ms     17597260.0                   : Stop X, frames: 921
    STEP.ms     1000.0010869565217           : Step (average)
    NULL.                                    :
    COMP.       Faroe Petroleum              :
    WELL.       206/05a-3                    :
    
    $ head -n20 example_data/LAS/206_05a-_3_DWL_DWL_WIRE_258276498_0_800T.las
    ~Version Information Section
    VERS.          2.0                                     : CWLS Log ASCII Standard - VERSION 2.0
    WRAP.          NO                                      : One Line per depth step
    PROD.          TotalDepth                              : LAS Producer
    PROG.          TotalDepth.RP66V1.ToLAS 0.1.1           : LAS Program name and version
    CREA.          2019-10-28 10:30                        : LAS Creation date [YYYY-mm-dd HH:MM]
    DLIS_CREA.     2011-08-20 22:48                        : DLIS Creation date and time [YYYY-mm-dd HH:MM]
    SOURCE.        206_05a-_3_DWL_DWL_WIRE_258276498.DLIS  : DLIS File Name
    FILE-ID.       MSCT_197LTP                             : File Identification Number
    LOGICAL-FILE.  0                                       : Logical File number in the DLIS file
    FRAME-ARRAY.   800T                                    : Identity of the Frame Array in the Logical File
    ~Well Information Section
    #MNEM.UNIT  DATA                         DESCRIPTION
    #----.----  ----                         -----------
    STRT.ms     16677259.0                   : Start X
    STOP.ms     17597260.0                   : Stop X, frames: 2,301
    STEP.ms     400.0004347826087            : Step (average)
    NULL.                                    :
    COMP.       Faroe Petroleum              :
    WELL.       206/05a-3                    :


Processing a Directory
^^^^^^^^^^^^^^^^^^^^^^^^^

Use the ``-r`` option to process recursively. The output directory will mirror the input directory.

.. code-block:: console

    $ tdrp66v1tolas -r example_data/ tmp/LAS
      Input    Output LAS Count  Time  Ratio  ms/Mb Exception                                                         Path
    ------- --------- --------- ----- ------ ------ --------- ------------------------------------------------------------
    540,372 1,812,131         2 1.874 335.3% 3636.8     False "example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS"
    Execution time =    1.884 (S)
    Out of  6 processed 1 files of total size 540,372 input bytes
    Wrote 1,812,131 output bytes, ratio: 335.349% at 3655.1 ms/Mb
    $ find tmp/LAS -name '*.las'
    tmp/LAS/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498_0_800T.las
    tmp/LAS/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498_0_2000T.las



Indexing RP66V1 Files with ``tdrp66v1indexpickle``
===================================================================

``tdrp66v1indexpickle`` reads a RP66V1 file and dumps the index to a pickle file.

Arguments
-----------

The first argument is the path to a RP66V1 file or directory.
The second argument is the path to write the output to.

Options
-------

  -h, --help            show this help message and exit
  -r, --recurse         Process recursively. [default: False]
  --read-back           Read and time the output. [default: False]
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        Log Level as an integer or symbol. (0<->NOTSET,
                        10<->DEBUG, 20<->INFO, 30<->WARNING, 40<->ERROR,
                        50<->CRITICAL) [default: 30]
  --log-process LOG_PROCESS
                        Writes process data such as memory usage as a log INFO
                        line every LOG_PROCESS seconds. If 0.0 no process data
                        is logged. [default: 0.0]
  -v, --verbose         Increase verbosity, additive [default: 0]
  --gnuplot GNUPLOT     Directory to write the gnuplot data.

Examples
-----------

Processing a Single File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ tdrp66v1indexpickle --read-back example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS example_data/pickle/206_05a-_3_DWL_DWL_WIRE_258276498
    Common path prefix: example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS
    Size (b) | Index (b) | Ratio (%) | Index (s) | Index (ms/Mb) | Read (s) | Read (ms/Mb) | Except | Path
    -------- | --------- | --------- | --------- | ------------- | -------- | ------------ | ------ | ----
     540,372 | 1,018,327 |  188.449% |     0.330 |         639.9 |    0.041 |        78.96 |  False |
    Execution time =    0.379 (S)
    Out of  1 processed 1 files of total size 540,372 input bytes
    Wrote 1,018,327 output bytes, ratio: 188.449% at 651.0 ms/Mb
    $ ll example_data/pickle/
    total 1992
    -rw-r--r--  1 xxxxxxxx  staff  1018327 28 Oct 12:11 206_05a-_3_DWL_DWL_WIRE_258276498.pkl


Processing a Directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the ``-r`` option to process recursively. The output directory will mirror the input directory.


Indexing RP66V1 Files with ``tdrp66v1indexxml``
===================================================================

``tdrp66v1indexxml`` reads a RP66V1 file and dumps the index to an XML file.

Arguments
-----------

The first argument is the path to a RP66V1 file or directory.
The second argument is the path to write the output to.

Options
-------

optional arguments:
  -h, --help            show this help message and exit
  -r, --recurse         Process files recursively. [default: False]
  -p, --private         Also write out private EFLRs. [default: False]
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        Log Level as an integer or symbol. (0<->NOTSET,
                        10<->DEBUG, 20<->INFO, 30<->WARNING, 40<->ERROR,
                        50<->CRITICAL) [default: 20]
  --log-process LOG_PROCESS
                        Writes process data such as memory usage as a log INFO
                        line every LOG_PROCESS seconds. If 0.0 no process data
                        is logged. [default: 0.0]
  -v, --verbose         Increase verbosity, additive [default: 0]
  --gnuplot GNUPLOT     Directory to write the gnuplot data.

Examples
-----------

Processing a Single File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ tdrp66v1indexxml example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS example_data/XML/206_05a-_3_DWL_DWL_WIRE_258276498
    2019-10-28 11:58:55,498 - 74153 - MainThread - INFO     - IndexXML.py      - index_dir_or_file(): "example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS" to "example_data/XML/206_05a-_3_DWL_DWL_WIRE_258276498" recurse: False
    2019-10-28 11:58:55,499 - 74153 - MainThread - INFO     - IndexXML.py      - Making directory: example_data/XML
    2019-10-28 11:58:55,499 - 74153 - MainThread - INFO     - IndexXML.py      - Indexing example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS to example_data/XML/206_05a-_3_DWL_DWL_WIRE_258276498
    2019-10-28 11:58:55,939 - 74153 - MainThread - INFO     - IndexXML.py      - Length of XML: 428622
             Size In         Size Out     Time  Ratio %    ms/Mb Fail? Path
    ---------------- ---------------- -------- -------- -------- ----- ----
             540,372          428,622    0.440  79.320%    854.6 False "example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS"
    Execution time =    0.443 (S)
    Out of  1 processed 1 files of total size 540,372 input bytes
    Wrote 428,622 output bytes, ratio:  79.320% at 860.4 ms/Mb

The XML looks something like this:

.. code-block:: xml

    <?xml version='1.0' encoding="utf-8"?>
    <RP66V1FileIndex creator="TotalDepth.RP66V1.core.Index" path="example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS" schema_version="0.1.0" size="540372" utc_file_mtime="2019-06-22 09:10:59.512253" utc_now="2019-10-28 11:58:55.799047">
      <StorageUnitLabel dlis_version="V1.00" maximum_record_length="8192" sequence_number="1" storage_set_identifier="Default Storage Set                                         " storage_unit_structure="RECORD"/>
      <LogicalFiles count="1">
        <LogicalFile has_log_pass="True" index="0">
          <EFLR lr_type="0" lrsh_position="0x54" object_count="1" set_name="" set_type="FILE-HEADER" vr_position="0x50">
            <Object C="0" I="5" O="2">
              <Attribute count="1" label="SEQUENCE-NUMBER" rc="20" rc_ascii="ASCII" units="">
                <Value type="bytes" value="       197"/>
              </Attribute>
              <Attribute count="1" label="ID" rc="20" rc_ascii="ASCII" units="">
                <Value type="bytes" value="MSCT_197LTP                                                      "/>
              </Attribute>
            </Object>
          </EFLR>
          <!-- More EFLRs ... -->
          <LogPass count="2">
            <FrameArray C="0" I="2000T" O="2" description="" x_axis="TIME" x_units="ms">
              <Channels count="4">
                <Channel C="4" I="TIME" O="2" count="1" dimensions="1" long_name="1 second River Time" rep_code="2" units="ms"/>
                <Channel C="4" I="TDEP" O="2" count="1" dimensions="1" long_name="1 second River Depth" rep_code="2" units="0.1 in"/>
                <Channel C="0" I="TENS_SL" O="2" count="1" dimensions="1" long_name="Cable Tension" rep_code="2" units="lbf"/>
                <Channel C="0" I="DEPT_SL" O="2" count="1" dimensions="1" long_name="Station logging depth" rep_code="2" units="0.1 in"/>
              </Channels>
              <IFLR count="921">
                <FrameNumbers count="921" rle_len="1">
                  <RLE datum="1" repeat="920" stride="1"/>
                </FrameNumbers>
                <LRSH count="921" rle_len="400">
                  <RLE datum="0x13254" repeat="1" stride="0x190"/>
                  <!-- ... -->
                  <RLE datum="0x83ba4" repeat="1" stride="0x198"/>
                </LRSH>
                <Xaxis count="921" rle_len="2">
                  <RLE datum="16677259.0" repeat="99" stride="1000.0"/>
                  <RLE datum="16777260.0" repeat="820" stride="1000.0"/>
                </Xaxis>
              </IFLR>
            </FrameArray>
            <FrameArray C="0" I="800T" O="2" description="" x_axis="TIME" x_units="ms">
              <Channels count="43">
                <Channel C="5" I="TIME" O="2" count="1" dimensions="1" long_name="400 milli-second time channel" rep_code="2" units="ms"/>
                <Channel C="5" I="TDEP" O="2" count="1" dimensions="1" long_name="MSCT depth channel" rep_code="2" units="0.1 in"/>
                <Channel C="1" I="ETIM" O="2" count="1" dimensions="1" long_name="Elapsed Logging Time" rep_code="2" units="s"/>
                <!-- ... -->
                <Channel C="0" I="HMCU" O="2" count="1" dimensions="1" long_name="Hydrailic Motor Current" rep_code="2" units="mA"/>
                <Channel C="0" I="CMLP" O="2" count="1" dimensions="1" long_name="Coring Motor Linear Position" rep_code="2" units="in"/>
              </Channels>
              <IFLR count="2301">
                <FrameNumbers count="2301" rle_len="1">
                  <RLE datum="1" repeat="2300" stride="1"/>
                </FrameNumbers>
                <LRSH count="2301" rle_len="937">
                  <RLE datum="0x13274" repeat="1" stride="0xb8"/>
                  <!-- ... -->
                  <RLE datum="0x83d5c" repeat="1" stride="0xbc"/>
                </LRSH>
                <Xaxis count="2301" rle_len="2">
                  <RLE datum="16677259.0" repeat="249" stride="400.0"/>
                  <RLE datum="16777260.0" repeat="2050" stride="400.0"/>
                </Xaxis>
              </IFLR>
            </FrameArray>
          </LogPass>
        </LogicalFile>
      </LogicalFiles>
      <VisibleRecords count="66" rle_len="15">
        <RLE datum="0x50" repeat="3" stride="0x2000"/>
        <!-- ... -->
        <RLE datum="0x81f70" repeat="0" stride="0x0"/>
      </VisibleRecords>
    </RP66V1FileIndex>


Processing a Directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the ``-r`` option to process recursively. The output directory will mirror the input directory.


Scanning RP66V1 Files with ``tdrp66v1scan``
===================================================================

``tdrp66v1scan`` scans a RP66V1 file and dumps data about the file to stdout.
This is useful for examining the details of RP66V1 files and can dump data at various levels of encapsulation, from the lowest level upwards:

* ``--VR`` - Visible Records only.
* ``--LRSH`` - Logical Record segments.
* ``--LD`` - Logical data i.e. all Logical Record segments concatenated for each Logical Record.
* ``--EFLR`` - Explicitly Formatted Logical Records.
* ``--IFLR`` - Implicitly Formatted Logical Records.
* ``--LR`` - All data, including the numerical analysis of frame data.

If these options are combined then the input is scanned, and reported, multiple times.

Arguments
-----------

The first argument is the path to a RP66V1 file.
An optional second argument is the path to write the output to. If absent then output is written to stdout.

Options
-------


  -h, --help            show this help message and exit
  -V, --VR              Dump the Visible Records. [default: False]
  -L, --LRSH            Summarise the Visible Records and the Logical Record
                        Segment Headers, use -v to dump records. [default:
                        False]
  -D, --LD              Summarise logical data, use -v to dump records. See
                        also --dump-bytes, --dump-raw-bytes. [default: False]
  -E, --EFLR            Dump EFLR Set. [default: False]
  --eflr-set-type EFLR_SET_TYPE
                        List of EFLR Set Types to output, additive, if absent
                        then dump all. [default: []]
  -I, --IFLR            Dump IFLRs. [default: False]
  --iflr-set-type IFLR_SET_TYPE
                        List of IFLR Set Types to output, additive, if absent
                        then dump all. [default: []]
  -R, --LR              Dump all data, including frame data from Logical
                        Records. [default: False]
  -d DUMP_BYTES, --dump-bytes DUMP_BYTES
                        Dump X leading raw bytes for certain options, if -1
                        all bytes are dumped. [default: 0]
  --dump-raw-bytes      Dump the raw bytes for certain options in raw format,
                        otherwise Hex format is used. [default: False]
  -r, --recurse         Process files recursively. [default: False]
  -e, --encrypted       Output encrypted Logical Records as well. [default:
                        False]
  -k, --keep-going      Keep going as far as sensible. [default: False]
  --frame-slice FRAME_SLICE
                        NOTE: Requires -R, --LR. Do not process all frames but
                        sample or slice the frames. SAMPLE: Sample is of the
                        form "N" so a maximum of N frames, roughly regularly
                        spaced, will be processed. N must be +ve, non-zero
                        integer. Example: "64" - process a maximum of 64
                        frames. SLICE: Slice the frames is of the form
                        start,stop,step as a comma separated list. Values can
                        be absent or "None". Examples: ",," - every frame,
                        ",,2" - every other frame, ",10," - frames 0 to 9,
                        "4,10,2" - frames 4, 6, 8, "40,-1,4" - every fourth
                        frame from 40 to the end. Results will be truncated by
                        frame array length. [default: ",," i.e. all frames]
  --eflr-as-table       When with --LR and not --html then dump EFLRs as
                        tables, otherwise every EFLR object. [default: False]
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        Log Level as an integer or symbol. (0<->NOTSET,
                        10<->DEBUG, 20<->INFO, 30<->WARNING, 40<->ERROR,
                        50<->CRITICAL) [default: 30]
  -v, --verbose         Increase verbosity, additive [default: 0]
  --gnuplot GNUPLOT     Directory to write the gnuplot data.
  -T, --test-data       Dump the file as annotated bytes, useful for creating
                        test data. [default: False]

Examples
-----------

Scanning Visible Records with ``--VR``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Example of scanning a RP66V1 file:

.. code-block:: console

    $ tdrp66v1scan --VR example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS
    ************************************************* RP66V1 Visible and LRSH Records **************************************************
    ==================================================== Summary of Visible Records ====================================================
    Visible records: 66
    --------------------------------------------------- RLE Visible Record Position ----------------------------------------------------
    Datum:               80 0x00000050 Repeat:      3 Stride:  8,192 0x2000
    Datum:           32,844 0x0000804c Repeat:      5 Stride:  8,192 0x2000
    Datum:           81,988 0x00014044 Repeat:      4 Stride:  8,192 0x2000
    Datum:          122,940 0x0001e03c Repeat:     10 Stride:  8,192 0x2000
    Datum:          213,016 0x00034018 Repeat:      3 Stride:  8,192 0x2000
    Datum:          245,764 0x0003c004 Repeat:      3 Stride:  8,192 0x2000
    Datum:          278,516 0x00043ff4 Repeat:      3 Stride:  8,192 0x2000
    Datum:          311,268 0x0004bfe4 Repeat:      3 Stride:  8,192 0x2000
    Datum:          344,020 0x00053fd4 Repeat:      2 Stride:  8,192 0x2000
    Datum:          368,576 0x00059fc0 Repeat:      4 Stride:  8,192 0x2000
    Datum:          409,524 0x00063fb4 Repeat:      2 Stride:  8,192 0x2000
    Datum:          434,080 0x00069fa0 Repeat:      3 Stride:  8,192 0x2000
    Datum:          466,832 0x00071f90 Repeat:      3 Stride:  8,192 0x2000
    Datum:          499,584 0x00079f80 Repeat:      3 Stride:  8,192 0x2000
    Datum:          532,336 0x00081f70 Repeat:      0 Stride:      0 0x0000
    ------------------------------------------------- END RLE Visible Record Position --------------------------------------------------
    ================================================== END Summary of Visible Records ==================================================
    *********************************************** END RP66V1 Visible and LRSH Records ************************************************

And with the ``-v`` option:

.. code-block:: console

    $ tdrp66v1scan --VR -v example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS
    ************************************************* RP66V1 Visible and LRSH Records **************************************************
    <VisibleRecord: position=0x00000050 length=0x2000 version=0xff01> Stride: 0x00000050     80
    <VisibleRecord: position=0x00002050 length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    <VisibleRecord: position=0x00004050 length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    <VisibleRecord: position=0x00006050 length=0x1ffc version=0xff01> Stride: 0x00002000  8,192
    <VisibleRecord: position=0x0000804c length=0x2000 version=0xff01> Stride: 0x00001ffc  8,188
    <VisibleRecord: position=0x0000a04c length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    <VisibleRecord: position=0x0000c04c length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    <VisibleRecord: position=0x0000e04c length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    <VisibleRecord: position=0x0001004c length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    <VisibleRecord: position=0x0001204c length=0x1ff8 version=0xff01> Stride: 0x00002000  8,192
    <VisibleRecord: position=0x00014044 length=0x2000 version=0xff01> Stride: 0x00001ff8  8,184
    <VisibleRecord: position=0x00016044 length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    <VisibleRecord: position=0x00018044 length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    <VisibleRecord: position=0x0001a044 length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    <VisibleRecord: position=0x0001c044 length=0x1ff8 version=0xff01> Stride: 0x00002000  8,192
    <VisibleRecord: position=0x0001e03c length=0x2000 version=0xff01> Stride: 0x00001ff8  8,184
    <VisibleRecord: position=0x0002003c length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    ...
    <VisibleRecord: position=0x0007df80 length=0x2000 version=0xff01> Stride: 0x00002000  8,192
    <VisibleRecord: position=0x0007ff80 length=0x1ff0 version=0xff01> Stride: 0x00002000  8,192
    <VisibleRecord: position=0x00081f70 length=0x1f64 version=0xff01> Stride: 0x00001ff0  8,176
    ==================================================== Summary of Visible Records ====================================================

Scanning Logical Record Segments with ``--LRSH``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Example of scanning a RP66V1 file for Logical Record Segments, this gives just a summary:

.. code-block:: console

    $ tdrp66v1scan --LRSH example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS
    ...
    ========================================================= Summary of LRSH ==========================================================
    LRSH: total=3,303 is_first=3252
    LRSH: record types and counts (first segments only) [9]:
      0 :    3,223
      1 :        1
      3 :        1
      4 :        1
      5 :       10
    128 :        2
    129 :        2
    132 :       10
    133 :        2
    LRSH: record lengths and counts (all segments) [62] range: 16...8188
    ======================================================= END Summary of LRSH ========================================================

And with the ``-v`` option gives the Visible Records and Logical Record Segments:

.. code-block:: console

    ************************************************* RP66V1 Visible and LRSH Records **************************************************
    <VisibleRecord: position=0x00000050 length=0x2000 version=0xff01> Stride: 0x00000050     80
       <LogicalRecordSegmentHeader: position=0x00000054 length=0x007c attributes=0x80 LR type=  0> Stride: 0x00000054     84
       <LogicalRecordSegmentHeader: position=0x000000d0 length=0x0504 attributes=0x81 LR type=  1> Stride: 0x0000007c    124
       <LogicalRecordSegmentHeader: position=0x000005d4 length=0x05e0 attributes=0x81 LR type=  5> Stride: 0x00000504  1,284
       <LogicalRecordSegmentHeader: position=0x00000bb4 length=0x03e4 attributes=0x99 LR type=132> Stride: 0x000005e0  1,504
       <LogicalRecordSegmentHeader: position=0x00000f98 length=0x0254 attributes=0x99 LR type=132> Stride: 0x000003e4    996
       <LogicalRecordSegmentHeader: position=0x000011ec length=0x0588 attributes=0x81 LR type=  5> Stride: 0x00000254    596
       <LogicalRecordSegmentHeader: position=0x00001774 length=0x023c attributes=0x98 LR type=132> Stride: 0x00000588  1,416
       <LogicalRecordSegmentHeader: position=0x000019b0 length=0x0084 attributes=0x98 LR type=132> Stride: 0x0000023c    572
       <LogicalRecordSegmentHeader: position=0x00001a34 length=0x061c attributes=0xa0 LR type=132> Stride: 0x00000084    132
    <VisibleRecord: position=0x00002050 length=0x2000 version=0xff01> Stride: 0x00002000  8,192
        --<LogicalRecordSegmentHeader: position=0x00002054 length=0x0304 attributes=0xc1 LR type=132> Stride: 0x00000620  1,568
       <LogicalRecordSegmentHeader: position=0x00002358 length=0x0e3c attributes=0x81 LR type=  5> Stride: 0x00000304    772
       <LogicalRecordSegmentHeader: position=0x00003194 length=0x0ebc attributes=0xb9 LR type=132> Stride: 0x00000e3c  3,644
    <VisibleRecord: position=0x00004050 length=0x2000 version=0xff01> Stride: 0x00002000  8,192
        --<LogicalRecordSegmentHeader: position=0x00004054 length=0x0110 attributes=0xd9 LR type=132> Stride: 0x00000ec0  3,776
       <LogicalRecordSegmentHeader: position=0x00004164 length=0x1eec attributes=0xa0 LR type=  5> Stride: 0x00000110    272
    <VisibleRecord: position=0x00006050 length=0x1ffc version=0xff01> Stride: 0x00002000  8,192
        --<LogicalRecordSegmentHeader: position=0x00006054 length=0x1864 attributes=0xc1 LR type=  5> Stride: 0x00001ef0  7,920
       <LogicalRecordSegmentHeader: position=0x000078b8 length=0x0794 attributes=0xb9 LR type=132> Stride: 0x00001864  6,244
    <VisibleRecord: position=0x0000804c length=0x2000 version=0xff01> Stride: 0x00001ffc  8,188
        --<LogicalRecordSegmentHeader: position=0x00008050 length=0x1080 attributes=0xd9 LR type=132> Stride: 0x00000798  1,944
       <LogicalRecordSegmentHeader: position=0x000090d0 length=0x01e0 attributes=0x81 LR type=  5> Stride: 0x00001080  4,224
       <LogicalRecordSegmentHeader: position=0x000092b0 length=0x023c attributes=0x99 LR type=132> Stride: 0x000001e0    480
       <LogicalRecordSegmentHeader: position=0x000094ec length=0x0314 attributes=0x81 LR type=  5> Stride: 0x0000023c    572
       <LogicalRecordSegmentHeader: position=0x00009800 length=0x0154 attributes=0x99 LR type=128> Stride: 0x00000314    788
       <LogicalRecordSegmentHeader: position=0x00009954 length=0x0238 attributes=0x81 LR type=  5> Stride: 0x00000154    340
       <LogicalRecordSegmentHeader: position=0x00009b8c length=0x0270 attributes=0x81 LR type=  5> Stride: 0x00000238    568
       <LogicalRecordSegmentHeader: position=0x00009dfc length=0x0250 attributes=0xa0 LR type=  5> Stride: 0x00000270    624
    ...

Scanning Logical Data with ``--LD``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Example of scanning a RP66V1 file for Logical Record Segments, this gives just a summary:

.. code-block:: console

    $ tdrp66v1scan --LD example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS
    Cmd: tdrp66v1scan --LD example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS
    gnuplot version: "b'gnuplot 5.2 patchlevel 6'"
    args: Namespace(EFLR=False, IFLR=False, LD=True, LR=False, LRSH=False, VR=False, dump_bytes=0, dump_raw_bytes=False, eflr_as_table=False, eflr_set_type=[], encrypted=False, frame_slice=',,', gnuplot=None, iflr_set_type=[], keep_going=False, log_level=30, path_in='example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS', path_out='', recurse=False, verbose=0)
    Use -v to see individual logical data.
    Use -v and --dump-bytes to see actual first n bytes.
    *************************************************** RP66V1 Logical Data Summary ****************************************************
    ================================================= RP66V1 Logical Data EFLR Summary =================================================
    Total number of EFLR records: 30
    Total length of EFLR records: 78,109
    EFLR record type 0 lengths and count [1]:
           120:          1
    EFLR record type 1 lengths and count [1]:
         1,279:          1
    EFLR record type 3 lengths and count [1]:
         7,174:          1
    EFLR record type 4 lengths and count [1]:
           572:          1
    EFLR record type 5 lengths and count [10]:
           181:          1
           475:          1
           561:          1
           617:          1
           781:          1
    $ tdrp66v1scan --LD example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS
    Cmd: tdrp66v1scan --LD example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS
    gnuplot version: "b'gnuplot 5.2 patchlevel 6'"
    args: Namespace(EFLR=False, IFLR=False, LD=True, LR=False, LRSH=False, VR=False, dump_bytes=0, dump_raw_bytes=False, eflr_as_table=False, eflr_set_type=[], encrypted=False, frame_slice=',,', gnuplot=None, iflr_set_type=[], keep_going=False, log_level=30, path_in='example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS', path_out='', recurse=False, verbose=0)
    Use -v to see individual logical data.
    Use -v and --dump-bytes to see actual first n bytes.
    *************************************************** RP66V1 Logical Data Summary ****************************************************
    ================================================= RP66V1 Logical Data EFLR Summary =================================================
    Total number of EFLR records: 30
    Total length of EFLR records: 78,109
    EFLR record type 0 lengths and count [1]:
           120:          1
    EFLR record type 1 lengths and count [1]:
         1,279:          1
    EFLR record type 3 lengths and count [1]:
         7,174:          1
    EFLR record type 4 lengths and count [1]:
           572:          1
    EFLR record type 5 lengths and count [10]:
           181:          1
           475:          1
           561:          1
           617:          1
           781:          1
         1,409:          1
         1,497:          1
         1,620:          1
         3,637:          1
        14,149:          1
    EFLR record type 128 lengths and count [2]:
           336:          1
           888:          1
    EFLR record type 129 lengths and count [2]:
           111:          1
         1,226:          1
    EFLR record type 132 lengths and count [9]:
           128:          1
           288:          1
           512:          1
           568:          2
           592:          1
           992:          1
         2,325:          1
         4,036:          1
         6,156:          1
    EFLR record type 133 lengths and count [2]:
           999:          1
        24,312:          1
    =============================================== END RP66V1 Logical Data EFLR Summary ===============================================
    ================================================= RP66V1 Logical Data IFLR Summary =================================================
    Total number of IFLR records: 3,222
    Total length of IFLR records: 440,173
    IFLR record type 0 lengths and count [4]:
            25:        127
            26:        794
           180:        127
           181:      2,174
    =============================================== END RP66V1 Logical Data IFLR Summary ===============================================
    Total length EFLR/IFLR: 17.745%
    ************************************************* END RP66V1 Logical Data Summary **************************************************
             540,372         -1    0.059  -0.000%    115.4 False "example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS"
    Execution time =    0.060 (S)
    Processed 1 files and 540,372 bytes, 115.8 ms/Mb

And with the ``-v`` option gives the Visible Records and Logical Record Segments. The letter 'E' is for EFLRs and 'I' for IFLRs, 'Plain' is for un-encrypted records and 'Crypt' for encrypted records:

.. code-block:: console

    $ tdrp66v1scan --LD -v example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS
    Use -v and --dump-bytes to see actual first n bytes.
    *************************************************** RP66V1 Logical Data Summary ****************************************************
    Visible R  LRSH       Typ         Length
    ---------- ---------- --- - ----- --------
    0x00000050 0x00000054   0 E Plain      120
               0x000000d0   1 E Plain    1,279
               0x000005d4   5 E Plain    1,497
               0x00000bb4 132 E Crypt      992
               0x00000f98 132 E Crypt      592
               0x000011ec   5 E Plain    1,409
               0x00001774 132 E Crypt      568
               0x000019b0 132 E Crypt      128
               0x00001a34 132 E Plain    2,325
    0x00002050 0x00002358   5 E Plain    3,637
               0x00003194 132 E Crypt    4,036
    0x00004050 0x00004164   5 E Plain   14,149
    0x00006050 0x000078b8 132 E Crypt    6,156
    0x0000804c 0x000090d0   5 E Plain      475
               0x000092b0 132 E Crypt      568
               0x000094ec   5 E Plain      781
               0x00009800 128 E Crypt      336
               0x00009954   5 E Plain      561
               0x00009b8c   5 E Plain      617
               0x00009dfc   5 E Plain    1,620
    ...
    0x00081f70 0x00081f74   0 I Plain      181
               0x00082030   0 I Plain       26
               0x00082050   0 I Plain      181
               0x0008210c   0 I Plain      181
               0x000821c8   0 I Plain      181
               ...
               0x00083d3c   0 I Plain       26
               0x00083d5c   0 I Plain      181
               0x00083e18   0 I Plain      181
    ================================================= RP66V1 Logical Data EFLR Summary =================================================
    Total number of EFLR records: 30
    Total length of EFLR records: 78,109
    EFLR record type 0 lengths and count [1]:
           120:          1
    EFLR record type 1 lengths and count [1]:
         1,279:          1
    EFLR record type 3 lengths and count [1]:
         7,174:          1
    EFLR record type 4 lengths and count [1]:
           572:          1
    EFLR record type 5 lengths and count [10]:
           181:          1
           475:          1
           561:          1
           617:          1
           781:          1
         1,409:          1
         1,497:          1
         1,620:          1
         3,637:          1
        14,149:          1
    EFLR record type 128 lengths and count [2]:
           336:          1
           888:          1
    EFLR record type 129 lengths and count [2]:
           111:          1
         1,226:          1
    EFLR record type 132 lengths and count [9]:
           128:          1
           288:          1
           512:          1
           568:          2
           592:          1
           992:          1
         2,325:          1
         4,036:          1
         6,156:          1
    EFLR record type 133 lengths and count [2]:
           999:          1
        24,312:          1
    =============================================== END RP66V1 Logical Data EFLR Summary ===============================================
    ================================================= RP66V1 Logical Data IFLR Summary =================================================
    Total number of IFLR records: 3,222
    Total length of IFLR records: 440,173
    IFLR record type 0 lengths and count [4]:
            25:        127
            26:        794
           180:        127
           181:      2,174
    =============================================== END RP66V1 Logical Data IFLR Summary ===============================================
    Total length EFLR/IFLR: 17.745%
    ************************************************* END RP66V1 Logical Data Summary **************************************************

The ``--dump-bytes`` combined with ``-v`` shows the initial bytes of each logical record, here the first 16 bytes are dumped:

.. code-block:: console

    $ tdrp66v1scan --LD -v --dump-bytes=16 example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS
    *************************************************** RP66V1 Logical Data Summary ****************************************************
    Visible R  LRSH       Typ         Length
    ---------- ---------- --- - ----- --------
    0x00000050 0x00000054   0 E Plain      120 f00b 4649 4c45 2d48 4541 4445 5234 0f53 ..FILE-HEADER4.S
               0x000000d0   1 E Plain    1,279 f006 4f52 4947 494e 3c07 4649 4c45 2d49 ..ORIGIN<.FILE-I
               0x000005d4   5 E Plain    1,497 f809 4551 5549 504d 454e 5402 3531 3006 ..EQUIPMENT.510.
               0x00000bb4 132 E Crypt      992 0018 01b8 ced6 0000 be18 0000 8467 0000 .............g..
               0x00000f98 132 E Crypt      592 0018 01b8 dee9 0000 4916 0000 f16d 0000 ........I....m..
               0x000011ec   5 E Plain    1,409 f804 544f 4f4c 0235 3430 0a50 4152 414d ..TOOL.540.PARAM
               0x00001774 132 E Crypt      568 0018 01b8 9a99 0000 3c15 0000 877e 0000 ........<....~..
               0x000019b0 132 E Crypt      128 0018 01b8 acb3 0000 064d 0000 b74d 0000 .........M...M..
               0x00001a34 132 E Plain    2,325 f80b 3434 302d 4348 414e 4e45 4c02 3537 ..440-CHANNEL.57
    0x00002050 0x00002358   5 E Plain    3,637 f809 5041 5241 4d45 5445 5202 3538 3006 ..PARAMETER.580.
               0x00003194 132 E Crypt    4,036 0018 01b8 9aa6 0000 c84d 0000 4364 0000 .........M..Cd..
    0x00004050 0x00004164   5 E Plain   14,149 f809 5041 5241 4d45 5445 5202 3630 3006 ..PARAMETER.600.
    0x00006050 0x000078b8 132 E Crypt    6,156 0018 01b8 565d 0000 0945 0000 3812 0000 ....V]...E..8...
    0x0000804c 0x000090d0   5 E Plain      475 f809 5041 5241 4d45 5445 5202 3632 3006 ..PARAMETER.620.
               0x000092b0 132 E Crypt      568 0018 01b8 010d 0000 f57f 0000 890a 0000 ................
               0x000094ec   5 E Plain      781 f817 4341 4c49 4252 4154 494f 4e2d 4d45 ..CALIBRATION-ME
               0x00009800 128 E Crypt      336 0018 01b8 4550 0000 ae56 0000 3207 0000 ....EP...V..2...
               0x00009954   5 E Plain      561 f817 4341 4c49 4252 4154 494f 4e2d 434f ..CALIBRATION-CO
               0x00009b8c   5 E Plain      617 f817 4341 4c49 4252 4154 494f 4e2d 434f ..CALIBRATION-CO
               0x00009dfc   5 E Plain    1,620 f80b 4341 4c49 4252 4154 494f 4e02 3734 ..CALIBRATION.74
    ...

The raw bytes object is dumped of the ``--dump-raw-bytes`` flag is used along with ``--dump-bytes`` combined with ``-v``. This can be useful for creating test cases:

.. code-block:: console

    $ tdrp66v1scan --LD -v --dump-bytes=16 --dump-raw-bytes example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS | head -n 40
    *************************************************** RP66V1 Logical Data Summary ****************************************************
    Visible R  LRSH       Typ         Length
    ---------- ---------- --- - ----- --------
    0x00000050 0x00000054   0 E Plain      120 b'\xf0\x0bFILE-HEADER4\x0fS'
               0x000000d0   1 E Plain    1,279 b'\xf0\x06ORIGIN<\x07FILE-I'
               0x000005d4   5 E Plain    1,497 b'\xf8\tEQUIPMENT\x02510\x06'
               0x00000bb4 132 E Crypt      992 b'\x00\x18\x01\xb8\xce\xd6\x00\x00\xbe\x18\x00\x00\x84g\x00\x00'
               0x00000f98 132 E Crypt      592 b'\x00\x18\x01\xb8\xde\xe9\x00\x00I\x16\x00\x00\xf1m\x00\x00'
               0x000011ec   5 E Plain    1,409 b'\xf8\x04TOOL\x02540\nPARAM'
               0x00001774 132 E Crypt      568 b'\x00\x18\x01\xb8\x9a\x99\x00\x00<\x15\x00\x00\x87~\x00\x00'
               0x000019b0 132 E Crypt      128 b'\x00\x18\x01\xb8\xac\xb3\x00\x00\x06M\x00\x00\xb7M\x00\x00'
               0x00001a34 132 E Plain    2,325 b'\xf8\x0b440-CHANNEL\x0257'
    0x00002050 0x00002358   5 E Plain    3,637 b'\xf8\tPARAMETER\x02580\x06'
               0x00003194 132 E Crypt    4,036 b'\x00\x18\x01\xb8\x9a\xa6\x00\x00\xc8M\x00\x00Cd\x00\x00'
    0x00004050 0x00004164   5 E Plain   14,149 b'\xf8\tPARAMETER\x02600\x06'
    0x00006050 0x000078b8 132 E Crypt    6,156 b'\x00\x18\x01\xb8V]\x00\x00\tE\x00\x008\x12\x00\x00'
    0x0000804c 0x000090d0   5 E Plain      475 b'\xf8\tPARAMETER\x02620\x06'
               0x000092b0 132 E Crypt      568 b'\x00\x18\x01\xb8\x01\r\x00\x00\xf5\x7f\x00\x00\x89\n\x00\x00'
               0x000094ec   5 E Plain      781 b'\xf8\x17CALIBRATION-ME'
               0x00009800 128 E Crypt      336 b'\x00\x18\x01\xb8EP\x00\x00\xaeV\x00\x002\x07\x00\x00'
               0x00009954   5 E Plain      561 b'\xf8\x17CALIBRATION-CO'
               0x00009b8c   5 E Plain      617 b'\xf8\x17CALIBRATION-CO'
               0x00009dfc   5 E Plain    1,620 b'\xf8\x0bCALIBRATION\x0274'
    ...

Scanning Explicitly Formatted Logical Records with ``--EFLR``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Example of scanning a RP66V1 file for Logical Record Segments, this gives just a summary:

.. code-block:: console

    $ tdrp66v1scan --EFLR example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS
    Use -v to see individual logical data.
    ************************************************ RP66V1 EFLR and IFLR Data Summary *************************************************
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'FILE-HEADER' name: b''>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'ORIGIN' name: b''>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'EQUIPMENT' name: b'51'>
    Encrypted EFLR: VR: 0x00000050 LRSH: 0x00000bb4
    Encrypted EFLR: VR: 0x00000050 LRSH: 0x00000f98
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'TOOL' name: b'54'>
    Encrypted EFLR: VR: 0x00000050 LRSH: 0x00001774
    Encrypted EFLR: VR: 0x00000050 LRSH: 0x000019b0
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'440-CHANNEL' name: b'57'>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'PARAMETER' name: b'58'>
    Encrypted EFLR: VR: 0x00002050 LRSH: 0x00003194
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'PARAMETER' name: b'60'>
    Encrypted EFLR: VR: 0x00006050 LRSH: 0x000078b8
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'PARAMETER' name: b'62'>
    Encrypted EFLR: VR: 0x0000804c LRSH: 0x000092b0
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'CALIBRATION-MEASUREMENT' name: b'64'>
    Encrypted EFLR: VR: 0x0000804c LRSH: 0x00009800
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'CALIBRATION-COEFFICIENT' name: b'72'>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'CALIBRATION-COEFFICIENT' name: b'73'>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'CALIBRATION' name: b'74'>
    Encrypted EFLR: VR: 0x0000a04c LRSH: 0x0000a45c
    Encrypted EFLR: VR: 0x0000a04c LRSH: 0x0000a7d8
    Encrypted EFLR: VR: 0x0000a04c LRSH: 0x0000a8fc
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'PROCESS' name: b'78'>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'440-OP-CORE_TABLES' name: b'79'>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'440-OP-CORE_REPORT_FORMAT' name: b'330'>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'CHANNEL' name: b''>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'440-PRESENTATION-DESCRIPTION' name: b'375'>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'440-OP-CHANNEL' name: b'377'>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'FRAME' name: b''>
    ********************************************** END RP66V1 EFLR and IFLR Data Summary ***********************************************


The ``-v`` flag can be added to see the initial data:

.. code-block:: console

    $ tdrp66v1scan --EFLR -v example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS
    ************************************************ RP66V1 EFLR and IFLR Data Summary *************************************************
    Visible R  LRSH       Typ         Length
    ---------- ---------- --- - ----- --------
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'FILE-HEADER' name: b''>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'ORIGIN' name: b''>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'EQUIPMENT' name: b'51'>
    Encrypted EFLR: <FileLogicalData VR: 0x00000050 LRSH: 0x00000bb4 LR type 132 E y len 0x03e0 Idx 0x0000  0018 01b8 ced6 0000 be18 0000 8467 0000 .............g..>
    Encrypted EFLR: <FileLogicalData VR: 0x00000050 LRSH: 0x00000f98 LR type 132 E y len 0x0250 Idx 0x0000  0018 01b8 dee9 0000 4916 0000 f16d 0000 ........I....m..>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'TOOL' name: b'54'>
    Encrypted EFLR: <FileLogicalData VR: 0x00000050 LRSH: 0x00001774 LR type 132 E y len 0x0238 Idx 0x0000  0018 01b8 9a99 0000 3c15 0000 877e 0000 ........<....~..>
    Encrypted EFLR: <FileLogicalData VR: 0x00000050 LRSH: 0x000019b0 LR type 132 E y len 0x0080 Idx 0x0000  0018 01b8 acb3 0000 064d 0000 b74d 0000 .........M...M..>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'440-CHANNEL' name: b'57'>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'PARAMETER' name: b'58'>
    Encrypted EFLR: <FileLogicalData VR: 0x00002050 LRSH: 0x00003194 LR type 132 E y len 0x0fc4 Idx 0x0000  0018 01b8 9aa6 0000 c84d 0000 4364 0000 .........M..Cd..>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'PARAMETER' name: b'60'>
    Encrypted EFLR: <FileLogicalData VR: 0x00006050 LRSH: 0x000078b8 LR type 132 E y len 0x180c Idx 0x0000  0018 01b8 565d 0000 0945 0000 3812 0000 ....V]...E..8...>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'PARAMETER' name: b'62'>
    Encrypted EFLR: <FileLogicalData VR: 0x0000804c LRSH: 0x000092b0 LR type 132 E y len 0x0238 Idx 0x0000  0018 01b8 010d 0000 f57f 0000 890a 0000 ................>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'CALIBRATION-MEASUREMENT' name: b'64'>
    Encrypted EFLR: <FileLogicalData VR: 0x0000804c LRSH: 0x00009800 LR type 128 E y len 0x0150 Idx 0x0000  0018 01b8 4550 0000 ae56 0000 3207 0000 ....EP...V..2...>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'CALIBRATION-COEFFICIENT' name: b'72'>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'CALIBRATION-COEFFICIENT' name: b'73'>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'CALIBRATION' name: b'74'>
    Encrypted EFLR: <FileLogicalData VR: 0x0000a04c LRSH: 0x0000a45c LR type 128 E y len 0x0378 Idx 0x0000  0018 01b8 eff6 0000 fd5c 0000 123e 0000 .........\...>..>
    Encrypted EFLR: <FileLogicalData VR: 0x0000a04c LRSH: 0x0000a7d8 LR type 132 E y len 0x0120 Idx 0x0000  0018 01b8 4644 0000 ad4c 0000 4f31 0000 ....FD...L..O1..>
    Encrypted EFLR: <FileLogicalData VR: 0x0000a04c LRSH: 0x0000a8fc LR type 132 E y len 0x0200 Idx 0x0000  0018 01b8 abb7 0000 d01c 0000 6b36 0000 ............k6..>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'PROCESS' name: b'78'>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'440-OP-CORE_TABLES' name: b'79'>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'440-OP-CORE_REPORT_FORMAT' name: b'330'>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'CHANNEL' name: b''>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'440-PRESENTATION-DESCRIPTION' name: b'375'>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'440-OP-CHANNEL' name: b'377'>
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'FRAME' name: b''>
    ********************************************** END RP66V1 EFLR and IFLR Data Summary ***********************************************


The ``--eflr-set-type`` can be used to select only specific EFLRs:

.. code-block:: console

    $ tdrp66v1scan --EFLR -v --eflr-set-type=ORIGIN --eflr-as-table example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS
    ************************************************ RP66V1 EFLR and IFLR Data Summary *************************************************
    Visible R  LRSH       Typ         Length
    ---------- ---------- --- - ----- --------
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'ORIGIN' name: b''>
    ********************************************** END RP66V1 EFLR and IFLR Data Summary ***********************************************


Scanning Implicitly Formatted Logical Records with ``--IFLR``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Example of scanning a RP66V1 file for Logical Record Segments, this gives just a summary:

.. code-block:: console

    $ tdrp66v1scan --IFLR example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS
    Use -v to see individual logical data.
    Use -v and --dump-bytes to see actual first n bytes.
    ************************************************ RP66V1 EFLR and IFLR Data Summary *************************************************
    <IndirectlyFormattedLogicalRecord b'2000T'   frame:        1 free data[  16]>
    <IndirectlyFormattedLogicalRecord b'800T'    frame:        1 free data[ 172]>
    <IndirectlyFormattedLogicalRecord b'800T'    frame:        2 free data[ 172]>
    <IndirectlyFormattedLogicalRecord b'2000T'   frame:        2 free data[  16]>
    <IndirectlyFormattedLogicalRecord b'800T'    frame:        3 free data[ 172]>
    <IndirectlyFormattedLogicalRecord b'2000T'   frame:        3 free data[  16]>
    <IndirectlyFormattedLogicalRecord b'800T'    frame:        4 free data[ 172]>
    <IndirectlyFormattedLogicalRecord b'800T'    frame:        5 free data[ 172]>
    <IndirectlyFormattedLogicalRecord b'800T'    frame:        6 free data[ 172]>
    <IndirectlyFormattedLogicalRecord b'800T'    frame:        7 free data[ 172]>
    <IndirectlyFormattedLogicalRecord b'2000T'   frame:        4 free data[  16]>
    <IndirectlyFormattedLogicalRecord b'800T'    frame:        8 free data[ 172]>
    <IndirectlyFormattedLogicalRecord b'800T'    frame:        9 free data[ 172]>
    <IndirectlyFormattedLogicalRecord b'2000T'   frame:        5 free data[  16]>
    <IndirectlyFormattedLogicalRecord b'800T'    frame:       10 free data[ 172]>
    ...
    <IndirectlyFormattedLogicalRecord b'2000T'   frame:      920 free data[  16]>
    <IndirectlyFormattedLogicalRecord b'800T'    frame:    2,298 free data[ 172]>
    <IndirectlyFormattedLogicalRecord b'800T'    frame:    2,299 free data[ 172]>
    <IndirectlyFormattedLogicalRecord b'2000T'   frame:      921 free data[  16]>
    <IndirectlyFormattedLogicalRecord b'800T'    frame:    2,300 free data[ 172]>
    <IndirectlyFormattedLogicalRecord b'800T'    frame:    2,301 free data[ 172]>
    ********************************************** END RP66V1 EFLR and IFLR Data Summary ***********************************************
             540,372         -1    0.435  -0.000%    844.6 False "example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS"
    Execution time =    0.436 (S)
    Processed 1 files and 540,372 bytes, 845.2 ms/Mb


Scanning Everything with ``--LR``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This reads every byte in the file and writes a very verbose output of each EFLR and a summary of each Log Pass.
For example:

.. code-block:: console

    $ tdrp66v1scan --LR example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS
    ***************************************************** RP66V1 File Data Summary *****************************************************
    StorageUnitLabel:
      Storage Unit Sequence Number: 1
                      DLIS Version: b'V1.00'
            Storage Unit Structure: b'RECORD'
             Maximum Record Length: 8192
            Storage Set Identifier: b'Default Storage Set                                         '
    ======================================================== Logical File [0/1] ========================================================
    <TotalDepth.RP66V1.core.LogicalFile.LogicalFile object at 0x104d3f6a0>
    ------------------------------------------ EFLR [0/19] at VR: 0x00000050 LRSH: 0x00000054 ------------------------------------------
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'FILE-HEADER' name: b''>
      Template [2]:
        CD: 001 10100 L: b'SEQUENCE-NUMBER' C: 1 R: 20 (ASCII) U: b'' V: None
        CD: 001 10100 L: b'ID' C: 1 R: 20 (ASCII) U: b'' V: None
      Objects [1]:
        OBNAME: O: 2 C: 0 I: b'5'
          CD: 001 00001 L: b'SEQUENCE-NUMBER' C: 1 R: 20 (ASCII) U: b'' V: [b'       197']
          CD: 001 00001 L: b'ID' C: 1 R: 20 (ASCII) U: b'' V: [b'MSCT_197LTP                                                      ']
    ---------------------------------------- END EFLR [0/19] at VR: 0x00000050 LRSH: 0x00000054 ----------------------------------------
    ------------------------------------------ EFLR [1/19] at VR: 0x00000050 LRSH: 0x000000d0 ------------------------------------------
    <ExplicitlyFormattedLogicalRecord EFLR Set type: b'ORIGIN' name: b''>
      Template [20]:
        CD: 001 11100 L: b'FILE-ID' C: 1 R: 20 (ASCII) U: b'' V: None
        CD: 001 11100 L: b'FILE-SET-NAME' C: 1 R: 19 (IDENT) U: b'' V: None
        CD: 001 11100 L: b'FILE-SET-NUMBER' C: 1 R: 18 (UVARI) U: b'' V: None
        CD: 001 11100 L: b'FILE-NUMBER' C: 1 R: 18 (UVARI) U: b'' V: None
        CD: 001 11100 L: b'FILE-TYPE' C: 1 R: 19 (IDENT) U: b'' V: None
        CD: 001 11100 L: b'PRODUCT' C: 1 R: 20 (ASCII) U: b'' V: None
        CD: 001 11100 L: b'VERSION' C: 1 R: 20 (ASCII) U: b'' V: None
        CD: 001 11100 L: b'PROGRAMS' C: 1 R: 20 (ASCII) U: b'' V: None
        CD: 001 11100 L: b'CREATION-TIME' C: 1 R: 21 (DTIME) U: b'' V: None
        CD: 001 11100 L: b'ORDER-NUMBER' C: 1 R: 20 (ASCII) U: b'' V: None
        CD: 001 11000 L: b'DESCENT-NUMBER' C: 1 R: 19 (IDENT) U: b'' V: None
        CD: 001 11000 L: b'RUN-NUMBER' C: 1 R: 19 (IDENT) U: b'' V: None
        CD: 001 11100 L: b'WELL-ID' C: 1 R: 20 (ASCII) U: b'' V: None
        CD: 001 11100 L: b'WELL-NAME' C: 1 R: 20 (ASCII) U: b'' V: None
        CD: 001 11100 L: b'FIELD-NAME' C: 1 R: 20 (ASCII) U: b'' V: None
        CD: 001 11100 L: b'PRODUCER-CODE' C: 1 R: 16 (UNORM) U: b'' V: None
        CD: 001 11100 L: b'PRODUCER-NAME' C: 1 R: 20 (ASCII) U: b'' V: None
        CD: 001 11100 L: b'COMPANY' C: 1 R: 20 (ASCII) U: b'' V: None
        CD: 001 11100 L: b'NAME-SPACE-NAME' C: 1 R: 19 (IDENT) U: b'' V: None
        CD: 001 11100 L: b'NAME-SPACE-VERSION' C: 1 R: 18 (UVARI) U: b'' V: None
      Objects [1]:
        OBNAME: O: 2 C: 0 I: b'DLIS_DEFINING_ORIGIN'
          CD: 001 00001 L: b'FILE-ID' C: 1 R: 20 (ASCII) U: b'' V: [b'MSCT_197LTP                                                      ']
          CD: 001 00001 L: b'FILE-SET-NAME' C: 1 R: 19 (IDENT) U: b'' V: [b'FAROE_PETROLEUM/206_05A-3']
          CD: 001 00001 L: b'FILE-SET-NUMBER' C: 1 R: 18 (UVARI) U: b'' V: [41]
          CD: 001 00001 L: b'FILE-NUMBER' C: 1 R: 18 (UVARI) U: b'' V: [167]
          CD: 001 00001 L: b'FILE-TYPE' C: 1 R: 19 (IDENT) U: b'' V: [b'STATION LOG']
          CD: 001 00001 L: b'PRODUCT' C: 1 R: 20 (ASCII) U: b'' V: [b'OP']
          CD: 001 00001 L: b'VERSION' C: 1 R: 20 (ASCII) U: b'' V: [b'19C0-187']
          CD: 001 01001 L: b'PROGRAMS' C: 4 R: 20 (ASCII) U: b'' V: [b'MSCT: Mechanical Sidewall Coring Tool', b'SGTP: Scintillation Gamma-Ray - P', b'LEHQT: Logging Equipment Head - QT', b'WELLCAD: WellCAD file generator']
          CD: 001 00001 L: b'CREATION-TIME' C: 1 R: 21 (DTIME) U: b'' V: [<<class 'TotalDepth.RP66V1.core.RepCode.DateTime'> 2011-08-20 22:48:50.000 DST>]
          CD: 001 00001 L: b'ORDER-NUMBER' C: 1 R: 20 (ASCII) U: b'' V: [b'BSAX-00003                                                                                                                     ']
          CD: 001 00001 L: b'DESCENT-NUMBER' C: 1 R: 19 (IDENT) U: b'' V: [b'-1']
          CD: 001 00001 L: b'RUN-NUMBER' C: 1 R: 19 (IDENT) U: b'' V: [b'1']
          CD: 001 00001 L: b'WELL-ID' C: 1 R: 20 (ASCII) U: b'' V: [b'                                                                                                                               ']
          CD: 001 00001 L: b'WELL-NAME' C: 1 R: 20 (ASCII) U: b'' V: [b'206/05a-3                                                                                                                      ']
          CD: 001 00001 L: b'FIELD-NAME' C: 1 R: 20 (ASCII) U: b'' V: [b'Fulla                                                                                                                          ']
          CD: 001 00001 L: b'PRODUCER-CODE' C: 1 R: 16 (UNORM) U: b'' V: [440]
          CD: 001 00001 L: b'PRODUCER-NAME' C: 1 R: 20 (ASCII) U: b'' V: [b'Schlumberger']
          CD: 001 00001 L: b'COMPANY' C: 1 R: 20 (ASCII) U: b'' V: [b'Faroe Petroleum                                                                                                                ']
          CD: 001 00001 L: b'NAME-SPACE-NAME' C: 1 R: 19 (IDENT) U: b'' V: [b'SLB']
          CD: 000 00000 L: b'NAME-SPACE-VERSION' C: 1 R: 18 (UVARI) U: b'' V: None
    ---------------------------------------- END EFLR [1/19] at VR: 0x00000050 LRSH: 0x000000d0 ----------------------------------------
    ... Many EFLRs later ...
    --------------------------------------- END EFLR [18/19] at VR: 0x0001204c LRSH: 0x00013014 ----------------------------------------
    ------------------------------------------------------------- Log Pass -------------------------------------------------------------
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Frame Array [0/2] ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    FrameArray: ID: OBNAME: O: 2 C: 0 I: b'2000T' b''
      FrameChannel: OBNAME: O: 2 C: 4 I: b'TIME'            Rc:   2 Co:    1 Un: b'ms'        Di: [1] b'1 second River Time'
      FrameChannel: OBNAME: O: 2 C: 4 I: b'TDEP'            Rc:   2 Co:    1 Un: b'0.1 in'    Di: [1] b'1 second River Depth'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'TENS_SL'         Rc:   2 Co:    1 Un: b'lbf'       Di: [1] b'Cable Tension'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'DEPT_SL'         Rc:   2 Co:    1 Un: b'0.1 in'    Di: [1] b'Station logging depth'
    X Axis summary (all IFLRs):
    Min: 16677259.0 Max: 17597260.0 [b'ms'] Count: 921
    X Axis spacing summary:
    Min: 1000.0 Max: 1001.0 Mean: 1000.0010869565217 Median: 1000.0
       Normal: 920
    Duplicate: 0
      Skipped: 0
         Back: 0
    Spacing histogram
         Value [   N]: Relative Frequency
      1000.000 [ 919]: ********************************************************************************
      1000.100 [   0]: 
      1000.200 [   0]: 
      1000.300 [   0]: 
      1000.400 [   0]: 
      1000.500 [   0]: 
      1000.600 [   0]: 
      1000.700 [   0]: 
      1000.800 [   0]: 
      1000.900 [   1]: 
    Frames [921] from: 16677259.000 to 17597260.000 Interval: 1000.000 b'ms'
    Frame spacing: <Slice on length=921 start=0 stop=921 step=1> number of frames: 921 numpy size: 14,736 bytes
    Channel   Size   Absent            Min           Mean     Std.Dev.            Max       Units     dtype
    -------   ----   ------   ------------   ------------   ----------   ------------   ---------   -------
       TIME    921        0   16677259.000   17137260.404   265869.810   17597260.000       b'ms'   float32
       TDEP    921        0     852606.000     872468.708    17513.899     893302.000   b'0.1 in'   float32
    TENS_SL    921        0       1825.000       2145.789      198.506       2594.000      b'lbf'   float32
    DEPT_SL    921        0     852606.000     872467.735    17513.909     893303.000   b'0.1 in'   float32

    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ END Frame Array [0/2] ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Frame Array [1/2] ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    FrameArray: ID: OBNAME: O: 2 C: 0 I: b'800T' b''
      FrameChannel: OBNAME: O: 2 C: 5 I: b'TIME'            Rc:   2 Co:    1 Un: b'ms'        Di: [1] b'400 milli-second time channel'
      FrameChannel: OBNAME: O: 2 C: 5 I: b'TDEP'            Rc:   2 Co:    1 Un: b'0.1 in'    Di: [1] b'MSCT depth channel'
      FrameChannel: OBNAME: O: 2 C: 1 I: b'ETIM'            Rc:   2 Co:    1 Un: b's'         Di: [1] b'Elapsed Logging Time'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'LMVL'            Rc:   2 Co:    1 Un: b'V'         Di: [1] b'Lower Motor Voltage Limit'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'UMVL'            Rc:   2 Co:    1 Un: b'V'         Di: [1] b'Upper Motor Voltage Limit'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'CFLA'            Rc:   2 Co:    1 Un: b' '         Di: [1] b'Coring Flag'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'OCD'             Rc:   2 Co:    1 Un: b'ft'        Di: [1] b'Observed Core Depth'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'RCMD'            Rc:   2 Co:    1 Un: b'V'         Di: [1] b'Raw Coring Motor Downhole Voltage'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'RCPP'            Rc:   2 Co:    1 Un: b'in'        Di: [1] b'Raw Kinematics Piston Position'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'CMRT'            Rc:   2 Co:    1 Un: b'h'         Di: [1] b'Coring Motor Run Time'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'RCNU'            Rc:   2 Co:    1 Un: b' '         Di: [1] b'Raw Core Number'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'DCFL'            Rc:   2 Co:    1 Un: b' '         Di: [1] b'Down Command Flag'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'DFS'             Rc:   2 Co:    1 Un: b' '         Di: [1] b'Data Full Scale'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'DZER'            Rc:   2 Co:    1 Un: b' '         Di: [1] b'Data Zero'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'RHMD'            Rc:   2 Co:    1 Un: b'V'         Di: [1] b'Raw Hydraulic Motor Downhole Voltage'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'HMRT'            Rc:   2 Co:    1 Un: b'h'         Di: [1] b'Hydraulic Motor Run Time'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'RHV'             Rc:   2 Co:    1 Un: b'V'         Di: [1] b'Raw Head Voltage'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'RLSW'            Rc:   2 Co:    1 Un: b' '         Di: [1] b'Raw Limit Switch'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'MNU'             Rc:   2 Co:    1 Un: b' '         Di: [1] b'Marker Number'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'S1CY'            Rc:   2 Co:    1 Un: b' '         Di: [1] b'Solenoid 1 Cycles'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'S2CY'            Rc:   2 Co:    1 Un: b' '         Di: [1] b'Solenoid 2 Cycles'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'RSCU'            Rc:   2 Co:    1 Un: b' '         Di: [1] b'Raw Solenoid Current'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'RSTS'            Rc:   2 Co:    1 Un: b' '         Di: [1] b'Raw Solenoid Status'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'UCFL'            Rc:   2 Co:    1 Un: b' '         Di: [1] b'Up Command Flag'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'CARC'            Rc:   2 Co:    1 Un: b'mA'        Di: [1] b'Cartridge Current'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'CMDV'            Rc:   2 Co:    1 Un: b'V'         Di: [1] b'Coring Motor Downhole Voltage'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'CMPP'            Rc:   2 Co:    1 Un: b'in'        Di: [1] b'Kinematics Piston Position'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'CNU'             Rc:   2 Co:    1 Un: b' '         Di: [1] b'Core Number'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'HMDV'            Rc:   2 Co:    1 Un: b'V'         Di: [1] b'Hydraulic Motor Downhole Voltage'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'HV'              Rc:   2 Co:    1 Un: b'V'         Di: [1] b'Head Voltage'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'LSWI'            Rc:   2 Co:    1 Un: b' '         Di: [1] b'Limit Switch'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'SCUR'            Rc:   2 Co:    1 Un: b' '         Di: [1] b'Solenoid Current'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'SSTA'            Rc:   2 Co:    1 Un: b' '         Di: [1] b'Solenoid Status'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'RCMP'            Rc:   2 Co:    1 Un: b'psi'       Di: [1] b'Raw Coring Motor Pressure'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'RHPP'            Rc:   2 Co:    1 Un: b'psi'       Di: [1] b'Raw Hydraulic Pump Pressure'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'RRPP'            Rc:   2 Co:    1 Un: b'psi'       Di: [1] b'Raw Kinematics Pressure'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'CMPR'            Rc:   2 Co:    1 Un: b'psi'       Di: [1] b'Coring Motor Pressure'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'HPPR'            Rc:   2 Co:    1 Un: b'psi'       Di: [1] b'Hydraulic Pump Pressure'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'RPPV'            Rc:   2 Co:    1 Un: b'psi'       Di: [1] b'Kinematics Pressure'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'SMSC'            Rc:  14 Co:    1 Un: b' '         Di: [1] b'MSCT Status Word'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'CMCU'            Rc:   2 Co:    1 Un: b'mA'        Di: [1] b'Coring Motor Current'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'HMCU'            Rc:   2 Co:    1 Un: b'mA'        Di: [1] b'Hydrailic Motor Current'
      FrameChannel: OBNAME: O: 2 C: 0 I: b'CMLP'            Rc:   2 Co:    1 Un: b'in'        Di: [1] b'Coring Motor Linear Position'
    X Axis summary (all IFLRs):
    Min: 16677259.0 Max: 17597260.0 [b'ms'] Count: 2301
    X Axis spacing summary:
    Min: 400.0 Max: 401.0 Mean: 400.0004347826087 Median: 400.0
       Normal: 2300
    Duplicate: 0
      Skipped: 0
         Back: 0
    Spacing histogram
         Value [    N]: Relative Frequency
       400.000 [ 2299]: ********************************************************************************
       400.100 [    0]: 
       400.200 [    0]: 
       400.300 [    0]: 
       400.400 [    0]: 
       400.500 [    0]: 
       400.600 [    0]: 
       400.700 [    0]: 
       400.800 [    0]: 
       400.900 [    1]: 
    Frames [2301] from: 16677259.000 to 17597260.000 Interval: 400.000 b'ms'
    Frame spacing: <Slice on length=2301 start=0 stop=2301 step=1> number of frames: 2301 numpy size: 395,772 bytes
    Channel   Size   Absent            Min           Mean     Std.Dev.            Max       Units     dtype
    -------   ----   ------   ------------   ------------   ----------   ------------   ---------   -------
       TIME   2301        0   16677259.000   17137261.698   265696.737   17597260.000       b'ms'   float32
       TDEP   2301        0     852606.000     872468.805    17512.407     893304.000   b'0.1 in'   float32
       ETIM   2301        0          0.000        460.001      265.697        920.001        b's'   float32
       LMVL   2301        0        585.000        585.000        0.000        585.000        b'V'   float32
       UMVL   2301        0        635.000        635.000        0.000        635.000        b'V'   float32
       CFLA   2301        0          0.000         13.361        5.757         18.000        b' '   float32
        OCD   2301        0       6789.050       7153.751      165.517       7433.008       b'ft'   float32
       RCMD   2301        0          0.000        191.060      305.260        704.275        b'V'   float32
       RCPP   2301        0          0.443          0.853        0.649          2.598       b'in'   float32
       CMRT   2301        0          0.637          0.676        0.018          0.708        b'h'   float32
       RCNU   2301        0         20.000         20.756        0.532         22.000        b' '   float32
       DCFL   2301        0          0.000          1.229       12.818        143.000        b' '   float32
        DFS   2301        0        209.000        209.464        0.499        210.000        b' '   float32
       DZER   2301        0          0.000          0.002        0.042          1.000        b' '   float32
       RHMD   2301        0          0.000        345.934      320.677        674.725        b'V'   float32
       HMRT   2301        0          1.490          1.563        0.032          1.628        b'h'   float32
        RHV   2301        0        142.319        151.464        1.880        159.428        b'V'   float32
       RLSW   2301        0          0.000          0.377        0.485          1.000        b' '   float32
        MNU   2301        0         24.000         24.757        0.533         26.000        b' '   float32
       S1CY   2301        0         24.000         25.240        0.479         26.000        b' '   float32
       S2CY   2301        0         27.000         28.939        0.788         30.000        b' '   float32
       RSCU   2301        0         21.000         74.272       62.645        174.000        b' '   float32
       RSTS   2301        0          0.000          0.707        0.882          2.000        b' '   float32
       UCFL   2301        0        128.000        132.961        6.559        143.000        b' '   float32
       CARC   2301        0        178.238        201.121       12.822        211.238       b'mA'   float32
       CMDV   2301        0          0.000        191.060      305.260        704.275        b'V'   float32
       CMPP   2301        0         -0.004          0.407        0.651          2.158       b'in'   float32
        CNU   2301        0         20.000         20.756        0.532         22.000        b' '   float32
       HMDV   2301        0          0.000        345.934      320.677        674.725        b'V'   float32
         HV   2301        0        142.319        151.464        1.880        159.428        b'V'   float32
       LSWI   2301        0          0.000          0.377        0.485          1.000        b' '   float32
       SCUR   2301        0         21.000         74.272       62.645        174.000        b' '   float32
       SSTA   2301        0          0.000          0.707        0.882          2.000        b' '   float32
       RCMP   2301        0         14.696        149.036      215.905        574.505      b'psi'   float32
       RHPP   2301        0         14.696       1427.014     1451.455       4201.299      b'psi'   float32
       RRPP   2301        0         14.696       1434.264     1145.652       4009.911      b'psi'   float32
       CMPR   2301        0         14.696        149.036      215.905        574.505      b'psi'   float32
       HPPR   2301        0         14.696       1427.014     1451.455       4201.299      b'psi'   float32
       RPPV   2301        0         14.696       1434.264     1145.652       4009.911      b'psi'   float32
       SMSC   2301        0            192        212.597       27.112            254        b' '     int32
       CMCU   2301        0        -53.000       1059.832     1610.049       8295.000       b'mA'   float32
       HMCU   2301        0         10.000        339.616      302.494        747.125       b'mA'   float32
       CMLP   2301        0         -0.927         -0.296        1.043          2.891       b'in'   float32

    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ END Frame Array [1/2] ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ----------------------------------------------------------- END Log Pass -----------------------------------------------------------
    ====================================================== END Logical File [0/1] ======================================================
    *************************************************** END RP66V1 File Data Summary ***************************************************
             540,372         -1    0.750  -0.000%   1456.0 False "example_data/RP66V1/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS"
    Execution time =    0.751 (S)
    Processed 1 files and 540,372 bytes, 1456.5 ms/Mb


