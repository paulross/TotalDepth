.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Description of LAS command line tools

.. _cmd_line_tools_las:

***************************
LAS Command Line Tools
***************************

This describes the command line tools that are available for processing LAS files.

.. list-table:: **LAS Command Line Tools**
    :widths: 20 60
    :header-rows: 1
    
    * - Tool Name
      - Description
    * - ``tdlastohtml``
      - Generates a HTML page(s) about LAS file(s). :ref:`Link <cmd_line_tools_las_tdlastohtml>`
    * - ``tdlasreadlasfiles``
      - Summarises LAS file(s). :ref:`Link <cmd_line_tools_las_tdlasreadlasfiles>`


.. _cmd_line_tools_las_tdlastohtml:

Summarise LAS Files in HTML with ``tdlastohtml``
=================================================

Generates HTML from input LAS file or directory to an output destination.

Arguments
------------------

#. The path to the input LAS file or directory.
#. The path to the output file or directory, any directories will be created as necessary.

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
    --gnuplot GNUPLOT   Directory to write the gnuplot data.
    -g, --glob          File match pattern. Default: None.


Examples
---------------------

Command to process a directory of LAS::

    $ tdlastohtml example_data/LAS/data/ example_data/LAS/HTML/

Output::

    $ tdlastohtml example_data/LAS/data/ example_data/LAS/HTML/
    Cmd: /Users/paulross/pyenvs/TotalDepth_3.8_v0.3/bin/tdlastohtml example_data/LAS/data/ example_data/LAS/HTML/
    gnuplot version: "b'gnuplot 5.4 patchlevel 1'"
    2021-02-06 11:13:20,527 - LASToHTML.py     -  440 - 41351 - (MainThread) - INFO     - scan_dir_or_file(): "example_data/LAS/data" to "example_data/LAS/HTML" recurse: False
    2021-02-06 11:13:20,529 - LASToHTML.py     -  351 - 41351 - (MainThread) - INFO     - Scanning file type "ASCII" from "example_data/LAS/data/.DS_Store" to "example_data/LAS/HTML/.DS_Store.html"
    2021-02-06 11:13:20,530 - LASToHTML.py     -  351 - 41351 - (MainThread) - INFO     - Scanning file type "LAS2.0" from "example_data/LAS/data/1000079714.las" to "example_data/LAS/HTML/1000079714.las.html"
    2021-02-06 11:13:20,530 - LASToHTML.py     -  353 - 41351 - (MainThread) - INFO     - scan_a_single_file(): "example_data/LAS/data/1000079714.las" to "example_data/LAS/HTML/1000079714.las.html"
    2021-02-06 11:13:20,614 - LASToHTML.py     -  351 - 41351 - (MainThread) - INFO     - Scanning file type "LAS2.0" from "example_data/LAS/data/206_05a-_3_DWL_DWL_WIRE_258276498_0_2000T.las" to "example_data/LAS/HTML/206_05a-_3_DWL_DWL_WIRE_258276498_0_2000T.las.html"
    2021-02-06 11:13:20,614 - LASToHTML.py     -  353 - 41351 - (MainThread) - INFO     - scan_a_single_file(): "example_data/LAS/data/206_05a-_3_DWL_DWL_WIRE_258276498_0_2000T.las" to "example_data/LAS/HTML/206_05a-_3_DWL_DWL_WIRE_258276498_0_2000T.las.html"
    2021-02-06 11:13:20,679 - LASToHTML.py     -  351 - 41351 - (MainThread) - INFO     - Scanning file type "LAS2.0" from "example_data/LAS/data/BASIC_FILE_0_50.las" to "example_data/LAS/HTML/BASIC_FILE_0_50.las.html"
    2021-02-06 11:13:20,680 - LASToHTML.py     -  353 - 41351 - (MainThread) - INFO     - scan_a_single_file(): "example_data/LAS/data/BASIC_FILE_0_50.las" to "example_data/LAS/HTML/BASIC_FILE_0_50.las.html"
    2021-02-06 11:13:20,724 - LASToHTML.py     -  382 - 41351 - (MainThread) - INFO     - _write_indexes(): result map size 4
    2021-02-06 11:13:20,725 - ToHTML.py        -  207 - 41351 - (MainThread) - INFO     - Opening index file at /Users/paulross/PycharmProjects/TotalDepth/example_data/LAS/HTML/index.html
    2021-02-06 11:13:20,730 - ToHTML.py        -  240 - 41351 - (MainThread) - INFO     - Completed index file at /Users/paulross/PycharmProjects/TotalDepth/example_data/LAS/HTML/index.html
    2021-02-06 11:13:20,730 - LASToHTML.py     -  399 - 41351 - (MainThread) - INFO     - Wrote indexes: ['/Users/paulross/PycharmProjects/TotalDepth/example_data/LAS/HTML/index.html']
    Common path: example_data/LAS/data
             Size In   Size Out     Time  Ratio %    ms/Mb Fail? Path
    ---------------- ---------- -------- -------- -------- ----- ----
               6,148          0    0.000   0.000%      0.0 False ".DS_Store"
              80,697     12,892    0.083  15.976%   1078.0 False "1000079714.las"
              87,448     53,444    0.065  61.115%    779.8 False "206_05a-_3_DWL_DWL_WIRE_258276498_0_2000T.las"
              62,494     26,021    0.044  41.638%    736.1 False "BASIC_FILE_0_50.las"
    Processed 4 files and 236,787 bytes in 0.203 s, 900.0 ms/Mb
    Bye, bye!

For each file the output lists:

* Input file.
* Output HTML file.
* File size.
* Execution time.

In the output directory there will be an index.html file which has the columns:

Path	File Type	Sections	Channels	Frames	STRT	STOP	STEP	Size	Time

* The name of the LAS file.
* LAS file type.
* Number of sections.
* Recorded channels.
* Number of data frames.
* Start of log pass.
* End of log pass.
* Frame step.
* The size of the LAS file.
* Execution time.

In the linked HTML file is a summary of the content of the LAS file.


.. _cmd_line_tools_las_tdlasreadlasfiles:

Summarise LAS Files with ``tdlasreadlasfiles``
=======================================================

Reads an input LAS file or directory and summarises it by showing mnemonics, curves and well site data.


Arguments
------------------

#. The path to the input LAS file or directory.
                        

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
    --log-process LOG_PROCESS
                          Writes process data such as memory usage as a log INFO line
                          every LOG_PROCESS seconds. If 0.0 no process data is logged.
                          [default: 0.0]
    --gnuplot GNUPLOT     Directory to write the gnuplot data.
    -m, --mnemonic        Output Mnemonic map. Default: False.
    -c, --curve           Output Curve map. Default: False.
    -u, --unit            Output Units map. Default: False.
    -w, --wsd             Output Well Site Data map. Default: False.
    -p, --param           Output Parameter section mnemonics and their most popular
                          description and a map of themnemonic frequency. Default: False.
    -s, --size-time       Output parser's size vs time performance. Default: False.
    -a, --all             Output all, equivalent to -mcuwps. Default: False.

Examples
------------------

Listing Menmonics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the ``-m`` option to summarise the menmonics and their descriptions:

.. code-block:: console

    $ tdlasreadlasfiles example_data/LAS/data/ -m
    Cmd: /Users/paulross/pyenvs/TotalDepth_3.8_v0.3/bin/tdlasreadlasfiles example_data/LAS/data/ -m
    gnuplot version: "b'gnuplot 5.4 patchlevel 1'"
    ----------- All  mnemonics and their (most popular) description -----------
    {
    "ALTDPCHAN"                      : "Name Of Alternate Depth Channel                                 ", # Out of 1
    "AMD"                            : "Azimuth Of Maximum Deviation                                    ", # Out of 1
    "AOFF"                           : "Alphanumeric To Film Flag                                       ", # Out of 1
    "APD"                            : "Depth Above Pd                                                  ", # Out of 2
    "API"                            : "                                                                ", # Out of 2
    "APIN"                           : "Api S/N                                                         ", # Out of 2
    "BG"                             : "Gas Formation Volume Factor, Bg                                 ", # Out of 1
    "BHS"                            : "Borehole Status                                                 ", # Out of 1
    "BHT"                            : "Bottom Hole Temperature (Used In Calculations)                  ", # Out of 1
    "BLI"                            : "Bottom Log Interval                                             ", # Out of 1
    "BO"                             : "Oil Formation Volume Factor, Bo                                 ", # Out of 1
    "BPP"                            : "Bubble Point Pressure                                           ", # Out of 1
    ...


Listing Curves
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the ``-c`` option to summarise the curves and their descriptions:

.. code-block:: console


    $ tdlasreadlasfiles example_data/LAS/data/ -c
    Cmd: /Users/paulross/pyenvs/TotalDepth_3.8_v0.3/bin/tdlasreadlasfiles example_data/LAS/data/ -c
    gnuplot version: "b'gnuplot 5.4 patchlevel 1'"
    --------- All Curve mnemonics and their (most popular) description --------
    {
    "DEPT"                           : "Depth Curve                                                     ", # Out of 2
    "DEPT_SL"                        : "Station Logging Depth Dimensions (1,)                           ", # Out of 1
    "DHTN"                           : "Dhtn/Ch Tension Dimensions (1,)                                 ", # Out of 1
    "ETIM"                           : "Etim/Elapsed Time Dimensions (1,)                               ", # Out of 1
    "GR"                             : "Gamma Ray                                                       ", # Out of 2
    "TDEP"                           : "Second River Depth Dimensions (1,)                              ", # Out of 1
    "TENS"                           : "Tens/Tension Dimensions (1,)                                    ", # Out of 1
    "TENS_SL"                        : "Cable Tension Dimensions (1,)                                   ", # Out of 1
    "TIME"                           : "Second River Time Dimensions (1,)                               ", # Out of 1
    }
    ------ DONE: All Curve mnemonics and their (most popular) description -----


Listing Units
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the ``-u`` option to summarise the channels and their units:

.. code-block:: console

    $ tdlasreadlasfiles example_data/LAS/data/ -u
    Cmd: /Users/paulross/pyenvs/TotalDepth_3.8_v0.3/bin/tdlasreadlasfiles example_data/LAS/data/ -u
    gnuplot version: "b'gnuplot 5.4 patchlevel 1'"
    ------------------------- Channels and their Units ------------------------
    {
    "DEPT"     : "Counter({'F': 1, 'm': 1})",
    "DEPT_SL"  : "Counter({'0.1': 1})",
    "DHTN"     : "Counter({'lbs': 1})",
    "ETIM"     : "Counter({'min': 1})",
    "GR"       : "Counter({'GAPI': 1, 'api': 1})",
    "TDEP"     : "Counter({'0.1': 1})",
    "TENS"     : "Counter({'lbs': 1})",
    "TENS_SL"  : "Counter({'lbf': 1})",
    "TIME"     : "Counter({'ms': 1})",
    }
    ---------------------- DONE: Channels and their Units ---------------------


Listing Well Site Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the ``-w`` option to summarise the well site data and its frequency:

.. code-block:: console

    $ tdlasreadlasfiles example_data/LAS/data/ -w
    Cmd: /Users/paulross/pyenvs/TotalDepth_3.8_v0.3/bin/tdlasreadlasfiles example_data/LAS/data/ -w
    gnuplot version: "b'gnuplot 5.4 patchlevel 1'"
    ------ Count of well site mnemonics and the % of files that have them -----
    {
    "API"                            : ""                                                              , #        3  100.00%
    "CNTY"                           : ""                                                              , #        2   66.67%
    "COMP"                           : ""                                                              , #        3  100.00%
    "CORN"                           : "Reference Section Corner For Footage"                          , #        1   33.33%
    "COUN"                           : "County"                                                        , #        1   33.33%
    "CTRY"                           : ""                                                              , #        2   66.67%
    "DATE"                           : ""                                                              , #        3  100.00%
    "FLD"                            : ""                                                              , #        3  100.00%
    "FTE"                            : "Feet East From Reference Section Corner"                       , #        1   33.33%
    "FTN"                            : "Feet North From Reference Section Corner"                      , #        1   33.33%
    "LAT"                            : "Latitude North (Kgs,Leo3.6)"                                   , #        1   33.33%
    "LEAS"                           : "Lease Name"                                                    , #        1   33.33%
    "LOC"                            : ""                                                              , #        3  100.00%
    "LON"                            : "Longitude West (Kgs, Leo3.6)"                                  , #        1   33.33%
    "NULL"                           : ""                                                              , #        3  100.00%
    "PM"                             : "Principal Meridian"                                            , #        1   33.33%
    "PROV"                           : ""                                                              , #        2   66.67%
    "RANG"                           : "Range"                                                         , #        1   33.33%
    "SECT"                           : "Section"                                                       , #        1   33.33%
    "SPOT"                           : "Spot Location"                                                 , #        1   33.33%
    "SRVC"                           : ""                                                              , #        2   66.67%
    "STAT"                           : "State Name"                                                    , #        3  100.00%
    "STEP"                           : "Step (Average)"                                                , #        3  100.00%
    "STOP"                           : "Stop Depth"                                                    , #        3  100.00%
    "STRT"                           : "Start X"                                                       , #        3  100.00%
    "TOWN"                           : "Township"                                                      , #        1   33.33%
    "UWI"                            : ""                                                              , #        2   66.67%
    "WELL"                           : ""                                                              , #        3  100.00%
    }
    --- DONE: Count of well site mnemonics and the % of files that have them --
