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
