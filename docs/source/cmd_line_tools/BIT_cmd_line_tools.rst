.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Description of BIT command line tools

.. _cmd_line_tools_bit:

***************************
BIT Command Line Tools
***************************

This describes the command line tools that are available for processing BIT files.

.. list-table:: **BIT Command Line Tools**
    :widths: 20 60
    :header-rows: 1
    
    * - Tool Name
      - Description
    * - ``tdbitread``
      - Generates a summary of an archive of BIT file(s). :ref:`Link <cmd_line_tools_bit_tdbitread>`
    * - ``tdbittolas``
      - Converts BIT file(s) to LAS file(s). :ref:`Link <cmd_line_tools_bit_tdbittolas>`


.. _cmd_line_tools_bit_tdbitread:

Summarise BIT Files with ``tdbitread``
=================================================

Generates a summary from input BIT file or directory.

Arguments
------------------

#. The path to the input BIT file or directory.

Options
------------------

+--------------------------------------+---------------------------------------------------------------------------------+
| Option                               | Description                                                                     |
+======================================+=================================================================================+
| ``-h, --help``                       | Show this help message and exit.                                                |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``--version``                        | Show program's version number and exit                                          |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-k, --keep-going``                 | Keep going as far as sensible. [default: False]                                 |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-v, --verbose``                    | Verbose output, this outputs a representation of table data and DFSRs.          |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-r, --recurse``                    | Process input recursively. [default: False]                                     |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``-l LOGLEVEL, --loglevel=LOGLEVEL`` | Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: 20]  |
+--------------------------------------+---------------------------------------------------------------------------------+
| ``--summary``                        | Summarise the Frame Data. [default False]                                       |
+--------------------------------------+---------------------------------------------------------------------------------+

Examples
---------------------

Command to process a directory of BIT::

    $ tdbitread -r data/DresserAtlasBIT/special/

Output:

.. code-block:: console

    Cmd: src/TotalDepth/BIT/ReadBIT.py data/DresserAtlasBIT/special/ --summary -r
    2021-02-04 13:19:42,290 - ReadBIT.py       -  631 -  8000 - (MainThread) - INFO     - Processing: data/DresserAtlasBIT/special/29_10-_3/DWL_FILE/29_10-_3_dwl_DWL_WIRE_1646632.bit
    2021-02-04 13:19:42,762 - ReadBIT.py       -  600 -  8000 - (MainThread) - WARNING  - The block length 276 does not have equal data for the channels 10. at tell=922504. Ignoring rest of file.
    2021-02-04 13:19:42,946 - ReadBIT.py       -  631 -  8000 - (MainThread) - INFO     - Processing: data/DresserAtlasBIT/special/29_10-_3/DWL_FILE/29_10-_3_dwl_DWL_WIRE_1646636.bit
    2021-02-04 13:19:43,175 - ReadBIT.py       -  600 -  8000 - (MainThread) - WARNING  - The block length 276 does not have equal data for the channels 10. at tell=441328. Ignoring rest of file.
    2021-02-04 13:19:43,279 - ReadBIT.py       -  631 -  8000 - (MainThread) - INFO     - Processing: data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit
    2021-02-04 13:19:43,364 - ReadBIT.py       -  631 -  8000 - (MainThread) - INFO     - Processing: data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644660.bit
    2021-02-04 13:19:43,582 - ReadBIT.py       -  690 -  8000 - (MainThread) - INFO     - Count of success=4 errors=0
            Size     Time (s) Rate (ms/Mb) File
         1004032        0.654      682.705 data/DresserAtlasBIT/special/29_10-_3/DWL_FILE/29_10-_3_dwl_DWL_WIRE_1646632.bit
          513536        0.330      673.674 data/DresserAtlasBIT/special/29_10-_3/DWL_FILE/29_10-_3_dwl_DWL_WIRE_1646636.bit
          119276        0.084      736.193 data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit
          339916        0.217      667.974 data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644660.bit
    Total size 1976760 bytes, total time 1.284 (s)
    Rate 681.053 (ms/MB) 1.468 Mb/s
    Use -v, --verbose to see more information about each BIT file.
    Execution time =    1.293 (S)
    Bye, bye!


Adding the ``-v`` flag for more verbosity gives the following, here for one file:

.. code-block:: console

    $ tdbitread data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit -v
    Cmd: src/TotalDepth/BIT/ReadBIT.py data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit -v
    2021-02-04 13:21:41,402 - ReadBIT.py       -  631 -  8016 - (MainThread) - INFO     - Processing: data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit
    File size: 119276 0x1d1ec: data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit
    ==================== 29_10-_3Z_dwl_DWL_WIRE_1644659.bit ===================
    ----------------------------- Frame Array [0] -----------------------------
    BITFrameArray: ident="0"
       Unknown head: b'\x00\x02\x00\x00'
        Description: b'SHELL EXPRO U.K.      24 OCT 84      MANSFIELD/DODDS                    '
          Unknown A: b'\x00\n\x00\x18\x00'
          Unknown B: b'T  2 9 / 1 0 - 3                                                           '
          Unknown C: b'\x00\x12\x00\x0b\x00\x06  '
      Channels [10]: ['COND', 'SN  ', 'SP  ', 'GR  ', 'CAL ', 'TEN ', 'SPD ', 'ACQ ', 'AC  ', 'RT  ']
       BIT Log Pass: LogPassRange(depth_from=14950.000891089492, depth_to=14590.000869631818, spacing=0.2500000149011621, unknown_a=0.0, unknown_b=16.000000953674373)
       Unknown tail: b'MN239J 1'
        Frame count: 1472
        Frame array:       FrameArray: ID: 0 b'SHELL EXPRO U.K.      24 OCT 84      MANSFIELD/DODDS                    '
            <FrameChannel: 'X   ' "Computed X-axis" units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'COND' "COND" units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'SN  ' "SN  " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'SP  ' "SP  " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'GR  ' "GR  " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'CAL ' "CAL " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'TEN ' "TEN " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'SPD ' "SPD " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'ACQ ' "ACQ " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'AC  ' "AC  " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'RT  ' "RT  " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
    -------------------------- DONE: Frame Array [0] --------------------------
    ----------------------------- Frame Array [1] -----------------------------
    BITFrameArray: ident="1"
       Unknown head: b'\x00\x02\x00\x00'
        Description: b'SHELL EXPRO U.K.      24 OCT 84      MANSFIELD/DODDS                    '
          Unknown A: b'\x00\n\x00\x18\x00'
          Unknown B: b'T  2 9 / 1 0 - 3                                                           '
          Unknown C: b'\x00\x11\x00/\x00\r  '
      Channels [10]: ['COND', 'SN  ', 'SP  ', 'GR  ', 'CAL ', 'TEN ', 'SPD ', 'ACQ ', 'AC  ', 'RT  ']
       BIT Log Pass: LogPassRange(depth_from=14948.000890970283, depth_to=0.0, spacing=0.2500000149011621, unknown_a=0.0, unknown_b=16.000000953674373)
       Unknown tail: b'MN239J 4'
        Frame count: 1440
        Frame array:       FrameArray: ID: 1 b'SHELL EXPRO U.K.      24 OCT 84      MANSFIELD/DODDS                    '
            <FrameChannel: 'X   ' "Computed X-axis" units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'COND' "COND" units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'SN  ' "SN  " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'SP  ' "SP  " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'GR  ' "GR  " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'CAL ' "CAL " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'TEN ' "TEN " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'SPD ' "SPD " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'ACQ ' "ACQ " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'AC  ' "AC  " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'RT  ' "RT  " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
    -------------------------- DONE: Frame Array [1] --------------------------
    ================= DONE 29_10-_3Z_dwl_DWL_WIRE_1644659.bit =================
    Result:       119276        0.085      743.316 data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit
    Execution time =    0.085 (S)
    Bye, bye!


Adding the ``--summary`` flag for the frame data gives the following:

.. code-block:: console

    $ tdbitread data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit -v --summary
    Cmd: src/TotalDepth/BIT/ReadBIT.py data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit -v --summary
    2021-02-04 13:24:12,756 - ReadBIT.py       -  631 -  8140 - (MainThread) - INFO     - Processing: data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit
    File size: 119276 0x1d1ec: data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit
    ==================== 29_10-_3Z_dwl_DWL_WIRE_1644659.bit ===================
    ----------------------------- Frame Array [0] -----------------------------
    BITFrameArray: ident="0"
       Unknown head: b'\x00\x02\x00\x00'
        Description: b'SHELL EXPRO U.K.      24 OCT 84      MANSFIELD/DODDS                    '
          Unknown A: b'\x00\n\x00\x18\x00'
          Unknown B: b'T  2 9 / 1 0 - 3                                                           '
          Unknown C: b'\x00\x12\x00\x0b\x00\x06  '
      Channels [10]: ['COND', 'SN  ', 'SP  ', 'GR  ', 'CAL ', 'TEN ', 'SPD ', 'ACQ ', 'AC  ', 'RT  ']
       BIT Log Pass: LogPassRange(depth_from=14950.000891089492, depth_to=14590.000869631818, spacing=0.2500000149011621, unknown_a=0.0, unknown_b=16.000000953674373)
       Unknown tail: b'MN239J 1'
        Frame count: 1472
        Frame array:       FrameArray: ID: 0 b'SHELL EXPRO U.K.      24 OCT 84      MANSFIELD/DODDS                    '
            <FrameChannel: 'X   ' "Computed X-axis" units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'COND' "COND" units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'SN  ' "SN  " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'SP  ' "SP  " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'GR  ' "GR  " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'CAL ' "CAL " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'TEN ' "TEN " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'SPD ' "SPD " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'ACQ ' "ACQ " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'AC  ' "AC  " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
            <FrameChannel: 'RT  ' "RT  " units: 'b''' count: 1 dimensions: (1,) frames: 1472>
    ID   Length          Shape  Count          Min          Max         Mean     Std.Dev.       Median  Equal   Inc.   Dec.     Activity        Drift        First ->         Last
    X      1472        (1472,)   1472      14582.3        14950      14766.1      106.232      14766.1      0      0   1471   2.4427e-05        -0.25        14950 ->      14582.3
    COND   1472        (1472,)   1472       0.0001      2249.65      1016.02      520.471      1032.29     36    741    694    0.0695624    -0.690478      1015.69 ->       0.0001
    SN     1472        (1472,)   1472     -3.18704       24.465       16.718      3.78744      17.4128     35    762    674          nan   -0.0109108      16.0499 ->       0.0001
    SP     1472        (1472,)   1472     -249.709       0.0001      -244.45      35.8542     -249.709   1470      1      0          nan     0.169755     -249.709 ->       0.0001
    GR     1472        (1472,)   1472       0.0001      128.979      64.2715      17.9234      65.8888    168    637    666    0.0418426   -0.0556673      81.8867 ->       0.0001
    CAL    1472        (1472,)   1472     -2.44161       0.0001     -2.36168       0.3465     -2.41034    216    633    622          nan   0.00163825     -2.40976 ->       0.0001
    TEN    1472        (1472,)   1472       0.0001      4385.71      3619.19      543.754      3680.34     44    780    647    0.0198009     -2.18931      3220.48 ->       0.0001
    SPD    1472        (1472,)   1472       0.0001       43.074      30.9595      4.88865      31.8997     52    682    737    0.0201738   -0.0197124      28.9971 ->       0.0001
    ACQ    1472        (1472,)   1472            0            4     0.058426     0.390943            0   1433     26     12          nan   6.7981e-08            0 ->       0.0001
    AC     1472        (1472,)   1472       0.0001      91.9285      73.2971      15.5518      76.4215    116    630    725    0.0242162   -0.0254478      37.4338 ->       0.0001
    RT     1472        (1472,)   1472       0.0001      22.6922      1.81547      3.05078     0.952113     36    693    742    0.0621832 -0.000669238     0.984549 ->       0.0001
    -------------------------- DONE: Frame Array [0] --------------------------
    ----------------------------- Frame Array [1] -----------------------------
    BITFrameArray: ident="1"
       Unknown head: b'\x00\x02\x00\x00'
        Description: b'SHELL EXPRO U.K.      24 OCT 84      MANSFIELD/DODDS                    '
          Unknown A: b'\x00\n\x00\x18\x00'
          Unknown B: b'T  2 9 / 1 0 - 3                                                           '
          Unknown C: b'\x00\x11\x00/\x00\r  '
      Channels [10]: ['COND', 'SN  ', 'SP  ', 'GR  ', 'CAL ', 'TEN ', 'SPD ', 'ACQ ', 'AC  ', 'RT  ']
       BIT Log Pass: LogPassRange(depth_from=14948.000890970283, depth_to=0.0, spacing=0.2500000149011621, unknown_a=0.0, unknown_b=16.000000953674373)
       Unknown tail: b'MN239J 4'
        Frame count: 1440
        Frame array:       FrameArray: ID: 1 b'SHELL EXPRO U.K.      24 OCT 84      MANSFIELD/DODDS                    '
            <FrameChannel: 'X   ' "Computed X-axis" units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'COND' "COND" units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'SN  ' "SN  " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'SP  ' "SP  " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'GR  ' "GR  " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'CAL ' "CAL " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'TEN ' "TEN " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'SPD ' "SPD " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'ACQ ' "ACQ " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'AC  ' "AC  " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
            <FrameChannel: 'RT  ' "RT  " units: 'b''' count: 1 dimensions: (1,) frames: 1440>
    ID   Length          Shape  Count          Min          Max         Mean     Std.Dev.       Median  Equal   Inc.   Dec.     Activity        Drift        First ->         Last
    X      1440        (1440,)   1440      14588.3        14948      14768.1      103.923      14768.1      0      0   1439  2.44237e-05        -0.25        14948 ->      14588.3
    COND   1440        (1440,)   1440       0.0001       2261.8      1016.27      509.346      1053.65     20    757    662    0.0685063    -0.708206      1019.11 ->       0.0001
    SN     1440        (1440,)   1440       0.0001      91.6549      18.5481      4.23407      19.0641     20    756    663    0.0256921   -0.0636934      91.6549 ->       0.0001
    SP     1440        (1440,)   1440     -249.709       0.0001     -239.304      29.3708     -242.363     54    708    677          nan     0.164374     -236.534 ->       0.0001
    GR     1440        (1440,)   1440       0.0001      131.253      65.1255      17.9535      66.5528    155    631    653    0.0393008    -0.055561      79.9523 ->       0.0001
    CAL    1440        (1440,)   1440     -2.43995       0.0001     -2.37981     0.289624     -2.41493     80    673    686          nan   0.00167468     -2.40976 ->       0.0001
    TEN    1440        (1440,)   1440       0.0001      6564.66      3783.73      721.861      3678.22     21    786    632    0.0212608     -1.99216      2866.71 ->       0.0001
    SPD    1440        (1440,)   1440            0      39.5108      29.5586      4.05069      29.9188     26    683    730          inf  6.94927e-08            0 ->       0.0001
    ACQ    1440        (1440,)   1440            0            2   0.00972368      0.12322            0   1426      8      5          nan  6.94927e-08            0 ->       0.0001
    AC     1440        (1440,)   1440       0.0001      91.9285      76.2796      10.8951      76.8658     91    633    715     0.023214   -0.0523857      75.3831 ->       0.0001
    RT     1440        (1440,)   1440       0.0001      21.3526      1.79013      2.73227      0.92928     20    661    758     0.060755 -0.000681828      0.98125 ->       0.0001
    -------------------------- DONE: Frame Array [1] --------------------------
    ================= DONE 29_10-_3Z_dwl_DWL_WIRE_1644659.bit =================
    Result:       119276        0.097      848.759 data/DresserAtlasBIT/special/29_10-_3Z/DWL_FILE/29_10-_3Z_dwl_DWL_WIRE_1644659.bit
    Execution time =    0.097 (S)
    Bye, bye!


.. _cmd_line_tools_bit_tdbittolas:

Converting BIT Files to LAS Files with ``tdbittolas``
===================================================================

This takes a BIT file or directory of them and writes out a set of LAS files.
A single LAS file is written for each Log Pass so a single BIT file produces one or more LAS files.

The frames in the log pass can be sub-sampled by using ``--frame-slice`` which speeds things up when processing large files.
The ``--channels`` option can be used to limit channels.

BIT does not allow multiple values per channel.

As BIT files contain very little other than the frame data the generated LAS files are very simple and are missing what many processors would regard as essential data such as well name.
These LAS files may have to be edited with data from other sources than the original BIT file to be useful.

LAS File Naming Convention
--------------------------

One BIT file produces one or more LAS files.
LAS file names are of the form::

    {BIT_File}_{logical_file_number:04d}.las

Processing a Single BIT File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Given the path out the LAS files will be named ``{path_out}_{logical_file_number}.las``

For example ``tdbittolas foo.bit bar/baz`` might create::

    bar/baz.bit_0000.las
    bar/baz.bit_0001.las

and so on.

Processing a Directory of BIT Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Given the path out the LAS files will be named:

    ``{path_out}/{BIT_File}_{logical_file_number}.las``

For example ``tdbittolas foo/ bar/baz`` might create::

    bar/baz.bit_0000.las
    bar/baz.bit_0001.las

and so on.

The output directory structure will mirror the input directory structure.

Arguments
-----------

The first argument is the path to a BIT file or directory.
The second argument is the path to write the output to.

Options
-------

    -h, --help          show this help message and exit
    --version           show program's version number and exit
    -k, --keep-going    Keep going as far as sensible. Default: False.
    -v, --verbose       Increase verbosity, additive [default: 0]
    -r, --recurse       Process the input recursively. Default: False.
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

Use ``--channels=?`` and/or ``--frame-slice=?`` to see what channels and frames exist in the original BIT file.

.. code-block:: console

    $ tdbittolas --channels=? --frame-slice=? example_data/BIT/data/29_10-_3Z_dwl_DWL_WIRE_1644659.bit example_data/BIT/LIS
    ======= File example_data/BIT/data/29_10-_3Z_dwl_DWL_WIRE_1644659.bit =======
    
      Frame Array: 0
      Channels: "X   ","COND","SN  ","SP  ","GR  ","CAL ","TEN ","SPD ","ACQ ","AC  ","RT  "
      X axis: <FrameChannel: 'X   ' "Computed X-axis" units: 'b''' count: 1 dimensions: (1,) frames: 1472>
      Frames: 1472 from 14950.000891089492 to 14582.250869169884 interval -0.2500000149011612 [b'']

      Frame Array: 1
      Channels: "X   ","COND","SN  ","SP  ","GR  ","CAL ","TEN ","SPD ","ACQ ","AC  ","RT  "
      X axis: <FrameChannel: 'X   ' "Computed X-axis" units: 'b''' count: 1 dimensions: (1,) frames: 1440>
      Frames: 1440 from 14948.000890970283 to 14588.250869527512 interval -0.2500000149011612 [b'']    
    
    
    ===== END File example_data/BIT/data/29_10-_3Z_dwl_DWL_WIRE_1644659.bit =====


Processing a Single File
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ tdbittolas example_data/BIT/data/29_10-_3Z_dwl_DWL_WIRE_1644659.bit example_data/BIT/LAS/29_10-_3Z_dwl_DWL_WIRE_1644659.bit
    Cmd: /Users/paulross/pyenvs/TotalDepth_3.8_v0.3/bin/tdbittolas example_data/BIT/data/29_10-_3Z_dwl_DWL_WIRE_1644659.bit example_data/BIT/LAS/29_10-_3Z_dwl_DWL_WIRE_1644659.bit
    gnuplot version: "b'gnuplot 5.4 patchlevel 1'"
    2021-02-05 12:58:18,749 - WriteLAS.py      -  191 - 28222 - (MainThread) - INFO     - process_to_las(): Namespace(array_reduction='first', channels='', field_width=16, float_format='.3f', frame_slice=',,', gnuplot=None, jobs=-1, keepGoing=False, log_level=20, log_process=0.0, path_in='example_data/BIT/data/29_10-_3Z_dwl_DWL_WIRE_1644659.bit', path_out='example_data/BIT/LAS/29_10-_3Z_dwl_DWL_WIRE_1644659.bit', recurse=False, verbose=0)
    2021-02-05 12:58:18,749 - WriteLAS.py      -  167 - 28222 - (MainThread) - INFO     - index_dir_or_file(): "example_data/BIT/data/29_10-_3Z_dwl_DWL_WIRE_1644659.bit" to "example_data/BIT/LAS/29_10-_3Z_dwl_DWL_WIRE_1644659.bit" recurse: False
    2021-02-05 12:58:18,750 - ToLAS.py         -  117 - 28222 - (MainThread) - INFO     - Found file type BIT on path example_data/BIT/data/29_10-_3Z_dwl_DWL_WIRE_1644659.bit
    2021-02-05 12:58:18,750 - ToLAS.py         -  119 - 28222 - (MainThread) - INFO     - Reading BIT file example_data/BIT/data/29_10-_3Z_dwl_DWL_WIRE_1644659.bit
    2021-02-05 12:58:18,846 - ToLAS.py         -  125 - 28222 - (MainThread) - INFO     - Writing frame array 0 to example_data/BIT/LAS/29_10-_3Z_dwl_DWL_WIRE_1644659.bit_0000.las
    2021-02-05 12:58:18,848 - WriteLAS.py      -  521 - 28222 - (MainThread) - INFO     - Writing array section with 1,472 frames, 11 channels and 11 values per frame, total: 16,192 input values.
    2021-02-05 12:58:18,994 - ToLAS.py         -  125 - 28222 - (MainThread) - INFO     - Writing frame array 1 to example_data/BIT/LAS/29_10-_3Z_dwl_DWL_WIRE_1644659.bit_0001.las
    2021-02-05 12:58:18,995 - WriteLAS.py      -  521 - 28222 - (MainThread) - INFO     - Writing array section with 1,440 frames, 11 channels and 11 values per frame, total: 15,840 input values.
      Input     Type  Output LAS Count  Time  Ratio  ms/Mb Exception                                                       Path
    ------- -------- ------- --------- ----- ------ ------ --------- ----------------------------------------------------------
    119,276 BIT      549,613         2 0.370 460.8% 3249.8     False "example_data/BIT/data/29_10-_3Z_dwl_DWL_WIRE_1644659.bit"
    Writing results returned: 0 files failed.
    Execution time =    0.370 (S)
    Out of 1 processed 1 files of total size 119,276 input bytes
    Wrote 549,613 output bytes, ratio: 460.791% at 3256.2 ms/Mb
    Execution time: 0.370 (s)
    Bye, bye!

The LAS files look like this:

.. code-block:: console

    ~Version Information Section
    VERS.           2.0                                 : CWLS Log ASCII Standard - VERSION 2.0
    WRAP.           NO                                  : One Line per depth step
    PROD.           TotalDepth                          : LAS Producer
    PROG.           TotalDepth.BIT.ToLAS 0.1.1          : LAS Program name and version
    CREA.           2021-02-05 12:58:18.847493 UTC      : LAS Creation date [YYYY-mm-dd HH MM SS.us UTC]
    SOURCE.         29_10-_3Z_dwl_DWL_WIRE_1644659.bit  : Source File Name
    LOGICAL-FILE.   0                                   : Logical File number in the Source file
    SOURCE_FORMAT.  WESTERN ATLAS BIT FORMAT            : File format of Source file.
    #
    # Binary block A: b'SHELL EXPRO U.K.      24 OCT 84      MANSFIELD/DODDS                    '
    # Binary block B: b'T  2 9 / 1 0 - 3                                                           '
    # BIT Log Pass (claimed): LogPassRange(depth_from=14950.000891089492, depth_to=14590.000869631818, spacing=0.2500000149011621, unknown_a=0.0, unknown_b=16.000000953674373)
    #
    ~Well Information Section
    #MNEM.UNIT  DATA                 DESCRIPTION
    #----.----  ----                 -----------
    STRT.       14950.000891089492   : START
    STOP.       14582.250869169884   : STOP
    STRP.       -0.2500000149011612  : STEP
    ~Curve Information Section
    #MNEM.UNIT  Curve Description
    #---------  -----------------
    X   .       : Computed X-axis Dimensions (1,)
    COND.       : COND Dimensions (1,)
    SN  .       : SN   Dimensions (1,)
    SP  .       : SP   Dimensions (1,)
    GR  .       : GR   Dimensions (1,)
    CAL .       : CAL  Dimensions (1,)
    TEN .       : TEN  Dimensions (1,)
    SPD .       : SPD  Dimensions (1,)
    ACQ .       : ACQ  Dimensions (1,)
    AC  .       : AC   Dimensions (1,)
    RT  .       : RT   Dimensions (1,)
    # Array processing information:
    # Frame Array: ID: 0 description: b'SHELL EXPRO U.K.      24 OCT 84      MANSFIELD/DODDS                    '
    # All [11] original channels reproduced here.
    # Where a channel has multiple values the reduction method is by "first" value.
    # Maximum number of original frames: 1472
    # Requested frame slicing: <Slice on length=1472 start=0 stop=1472 step=1>, total number of frames presented here: 1472
    ~A          X                COND             SN               SP               GR               CAL              TEN              SPD              ACQ              AC               RT
           14950.001         1015.693           16.050         -249.709           81.887           -2.410         3220.477           28.997            0.000           37.434            0.985
           14949.751         1015.693           16.050         -249.709           81.887           -2.410         3220.477           28.997            0.000           37.434            0.985
           14949.501         1015.693           16.050         -249.709           81.887           -2.410         3220.477           28.997            0.000           37.434            0.985
           14949.251         1015.693           16.050         -249.709           81.887           -2.410         3220.477           28.997            0.000           37.434            0.985

Processing a Directory
^^^^^^^^^^^^^^^^^^^^^^^^^

Use the ``-r`` option to process recursively. The output directory will mirror the input directory.

.. code-block:: console

    $ tdbittolas -r example_data/BIT/data example_data/BIT/LAS
    Cmd: /Users/paulross/pyenvs/TotalDepth_3.8_v0.3/bin/tdbittolas -r example_data/BIT/data example_data/BIT/LAS
    gnuplot version: "b'gnuplot 5.4 patchlevel 1'"
    2021-02-05 13:00:32,879 - WriteLAS.py      -  191 - 28324 - (MainThread) - INFO     - process_to_las(): Namespace(array_reduction='first', channels='', field_width=16, float_format='.3f', frame_slice=',,', gnuplot=None, jobs=-1, keepGoing=False, log_level=20, log_process=0.0, path_in='example_data/BIT/data', path_out='example_data/BIT/LAS', recurse=True, verbose=0)
    2021-02-05 13:00:32,879 - WriteLAS.py      -  167 - 28324 - (MainThread) - INFO     - index_dir_or_file(): "example_data/BIT/data" to "example_data/BIT/LAS" recurse: True
    2021-02-05 13:00:32,880 - ToLAS.py         -  117 - 28324 - (MainThread) - INFO     - Found file type BIT on path example_data/BIT/data/29_10-_3Z_dwl_DWL_WIRE_1644659.bit
    2021-02-05 13:00:32,880 - ToLAS.py         -  119 - 28324 - (MainThread) - INFO     - Reading BIT file example_data/BIT/data/29_10-_3Z_dwl_DWL_WIRE_1644659.bit
    2021-02-05 13:00:32,962 - ToLAS.py         -  125 - 28324 - (MainThread) - INFO     - Writing frame array 0 to example_data/BIT/LAS/29_10-_3Z_dwl_DWL_WIRE_1644659.bit_0000.las
    2021-02-05 13:00:32,964 - WriteLAS.py      -  521 - 28324 - (MainThread) - INFO     - Writing array section with 1,472 frames, 11 channels and 11 values per frame, total: 16,192 input values.
    2021-02-05 13:00:33,076 - ToLAS.py         -  125 - 28324 - (MainThread) - INFO     - Writing frame array 1 to example_data/BIT/LAS/29_10-_3Z_dwl_DWL_WIRE_1644659.bit_0001.las
    2021-02-05 13:00:33,076 - WriteLAS.py      -  521 - 28324 - (MainThread) - INFO     - Writing array section with 1,440 frames, 11 channels and 11 values per frame, total: 15,840 input values.
      Input     Type  Output LAS Count  Time  Ratio  ms/Mb Exception                                                       Path
    ------- -------- ------- --------- ----- ------ ------ --------- ----------------------------------------------------------
    119,276 BIT      549,613         2 0.300 460.8% 2634.7     False "example_data/BIT/data/29_10-_3Z_dwl_DWL_WIRE_1644659.bit"
    Writing results returned: 0 files failed.
    Execution time =    0.301 (S)
    Out of 1 processed 1 files of total size 119,276 input bytes
    Wrote 549,613 output bytes, ratio: 460.791% at 2644.1 ms/Mb
    Execution time: 0.301 (s)
    Bye, bye!



