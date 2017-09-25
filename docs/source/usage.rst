===========================
Usage In a Python Project
===========================

To use TotalDepth::

    import TotalDepth
    
------------------------------
Important Concepts
------------------------------

Due to the size of data TotalDepth makes extensive use of lazy evaluation and generators, this means that compute power is only used where necesary.

Log Pass
^^^^^^^^^^^^^^

A :term:`Log Pass` represents a typical, independent, logging recording consisting of a format specification plus binary data. The format specification defines how to interpret the binary data (number of channels, name and units for each channel). In the LIS format the formatting record is known as the :term:`Data Format Specification Record` (:term:`DFSR`). A "Repeat Section" plus a "Main Log" are two, distinct, independent Log Passes.


Frame Set
^^^^^^^^^^^^^^

A :term:`Frame Set` is the logging data converted to the platforms internal types (usually C doubles) and stored in memory as a table where each row represents a particular depth (or time) and each column is the outptu of a specific channel. Each row is often referred to as a :term:`Frame`

======================
Processing LIS Files
======================

------------------------------
Important LIS Concepts
------------------------------

LIS File
^^^^^^^^^^^^^^^^^^

A LIS file is a wrapper round the platforms native I/O system.

Reference: :py:class:`TotalDepth.LIS.core.File.FileRead`

LIS Index
^^^^^^^^^^^^^

The LIS file format is designed for recording rather than processing. As such it is a sequential self anouncing format where to understand any part of it you have to have processed all of the preceeding data. This becomes very expensive with large files.

To avoid this an index is first created for the file that then allows random access to any part of that file including an individual frame. All access to the file is using this index. This index is very fast to create and its size is typically 1% of the original file size.

Reference: :py:class:`TotalDepth.LIS.core.FileIndexer.FileIndex`

------------------------------
Reading a LIS File Table Data
------------------------------

Suppose that we have a file in ``~/tmp/LIS.lis`` and you want to read the well site data. First import what we need::

    >>> import TotalDepth
    >>> from TotalDepth.LIS.core import File
    >>> from TotalDepth.LIS.core import FileIndexer
    >>> import os

Then open the LIS file and create an index from it::

    >>> fpath = os.path.expanduser('~/tmp/LIS.lis')
    >>> lis_file = TotalDepth.LIS.core.File.FileRead(fpath)
    >>> lis_index = TotalDepth.LIS.core.FileIndexer.FileIndex(lis_file)

There is a method on the index ``genAll()`` that iterates through all the records, filter this for only table data::

    >>> from TotalDepth.LIS.core import LogiRec
    >>> cons_records = [lr for lr in lis_index.genAll() if lr.lrType in LogiRec.LR_TYPE_TABLE_DATA]
    >>> cons_records
    [<TotalDepth.LIS.core.FileIndexer.IndexTable object at 0x103ac3dd8>]

In this file there is only one table record. Now read it:

    >>> lis_file.seekLr(cons_records[0].tell)
    >>> table = LogiRec.LrTableRead(lis_file)
    
Now we can explore the table::

    >>> table.desc
    'Well site data'
    >>> table.value
    b'CONS'
    >>> table.colLabels()
    odict_keys([b'MNEM', b'ALLO', b'PUNI', b'TUNI', b'VALU'])
    >>> table.rowLabels()
    dict_keys([b'HIDE', b'HID1', b'HID2', b'CN  ', b'WN  ', ..., b'C30 '])

Notice all the entries are represented as Python bytes objects (``b'...'``), this is because LIS does not support Unicode. LIS is also a bit shouty.

To get a specific value, say the well name::

    >>> print(table[b'WN  '][b'VALU'])
    CB: type=69 rc=65 size=16 mnem=b'VALU' EngValRc: b'GUSHER'
    >>> table[b'WN  '][b'VALU'].value
    b'GUSHER'
    
You can index by integer::

    >>> table[4][0].value
    b'WN  '
    >>> table[4][4].value
    b'GUSHER'
    >>> [v.value for v in table[4]]
    [b'WN  ', b'ALLO', b'    ', b'    ', b'GROSSENKNETEN Z2']

You can index by slice::

    >>> [v.value for v in table[4][:2]]
    [b'WN  ', b'ALLO']

To print the whole table there are some generators for this::

    >>> for row in table.genRows():
    ...     for col in row.genCells():
    ...         print(col.value, ' ', end='')
    ...     print()
    ... 
    b'HIDE'  b'ALLO'  b'    '  b'    '  b'MAIN LOG'
    b'HID1'  b'ALLO'  b'    '  b'    '  b'RAW DATA'
    b'HID2'  b'ALLO'  b'    '  b'    '  b''
    b'CN  '  b'ALLO'  b'    '  b'    '  b'BIG COMPANY'
    b'WN  '  b'ALLO'  b'    '  b'    '  b'GUSHER'
    ...

Reference: :py:class:`TotalDepth.LIS.core.LogiRec.LrTable`

------------------------------
Reading a LIS File Log Data
------------------------------

Suppose that we have a file in ``~/tmp/LIS.lis`` and you want to read the frame data from a particular log pass, first import what we need::

    >>> import TotalDepth
    >>> from TotalDepth.LIS.core import File
    >>> from TotalDepth.LIS.core import FileIndexer
    >>> import os

Then open the LIS file and create an index from it::

    >>> fpath = os.path.expanduser('~/tmp/LIS.lis')
    >>> lis_file = TotalDepth.LIS.core.File.FileRead(fpath)
    >>> lis_index = TotalDepth.LIS.core.FileIndexer.FileIndex(lis_file)

There is a method on the index ``genLogPasses()`` that iterates through the log passes, lets get them all::

    >>> log_passes = list(lis_index.genLogPasses())
    >>> print(log_passes)
    [<TotalDepth.LIS.core.FileIndexer.IndexLogPass object at 0x103ac3e80>]

In this file there is only one log pass, we can get the description of it using ``longstr()``::

    >>> print(log_passes[0].logPass.longStr())
    <TotalDepth.LIS.core.LogPass.LogPass object at 0x103ae10b8>: 
           DFSR: <TotalDepth.LIS.core.LogiRec.LrDFSRRead object at 0x103ac3eb8>: "Data format specification record"
     Frame plan: <TotalDepth.LIS.core.Type01Plan.FrameSetPlan object at 0x103ae10f0>: indr=0 frame length=24 channels=6
       Channels: [b'DEPT', b'SP  ', b'SN  ', b'ILD ', b'CILD', b'DT  ']
            RLE: <TotalDepth.LIS.core.Rle.RLEType01 object at 0x103ae1128>: func=None: [RLEItemType01: datum=8592 stride=1014 repeat=7 frames=42, RLEItemType01: datum=16704 stride=None repeat=0 frames=39]
         X axis: first=2052.983 last=1995.986 frames=375 overall spacing=-0.1524 in optical units=b'M   ' (actual units=b'M   ')
      Frame set: None

Note the last line ``Frame set: None``, this is because the log pass is a lightweight object which does not (yet) contain all the frame data. To read all the frame data from the file we call ``setFrameData(LisFile)`` on the log pass::

    >>> log_passes[0].logPass.setFrameSet(lis_file)
    
Now the frame set is fully populated::

    >>> print(list(log_passes[0].logPass.genFrameSetScNameUnit()))
    [('DEPT', 'M   '), ('SP  ', 'MV  '), ('SN  ', 'OHMM'), ('ILD ', 'OHMM'), ('CILD', 'MMHO'), ('DT  ', 'US/M')]

To get the actual vales in the frame we can access the numpy array directly::

    >>> data = log_passes[0].logPass.frameSet.frames
    >>> data
    array([[  2.05298340e+03,  -4.54907703e+00,   1.34538269e+00,
              1.26347518e+00,   3.86598633e+02,  -9.99250000e+02],
           [  2.05283105e+03,  -5.13720322e+00,   1.36061692e+00,
              1.29521227e+00,   5.00510803e+02,  -9.99250000e+02],
           [  2.05267871e+03,  -6.66747475e+00,   1.38543439e+00,
              1.45785594e+00,   5.95623291e+02,  -9.99250000e+02],
           ..., 
           [  1.99629077e+03,  -9.99250000e+02,  -9.99250000e+02,
             -9.99250000e+02,  -9.99250000e+02,  -9.99250000e+02],
           [  1.99613843e+03,  -9.99250000e+02,  -9.99250000e+02,
             -9.99250000e+02,  -9.99250000e+02,  -9.99250000e+02],
           [  1.99598608e+03,  -9.99250000e+02,  -9.99250000e+02,
             -9.99250000e+02,  -9.99250000e+02,  -9.99250000e+02]])

Now, if you are familiar with numpy then all normal operations are possible, for example get the X axis::
    
    >>> data[:,0]
    array([ 2052.98339844,  2052.83105469,  2052.67871094,  2052.52636719,
            2052.37402344,  2052.22167969,  2052.06933594,  2051.91650391,
            2051.76416016,  2051.61181641,  2051.45947266,  2051.30712891,
            ...
            1996.29077148,  1996.13842773,  1995.98608398])
    
Find the min, mean, max:

    >>> data.min(axis=0)
    array([ 1995.98608398,  -999.25      ,  -999.25      ,  -999.25      ,
            -999.25      ,  -999.25      ])
    >>> data.mean(axis=0)
    array([ 2024.48480339,  -305.07223682,  -326.84234802,  -324.20620109,
             206.05499658,    28.2555695 ])
    >>> data.max(axis=0)
    array([  2.05298340e+03,  -7.69491196e-01,   1.98412299e+00,
             2.34852839e+00,   1.75242944e+03,   4.59522583e+02])
    
References:

LogPass: :py:class:`TotalDepth.LIS.core.LogPass.LogPass`

FrameSet: :py:class:`TotalDepth.LIS.core.FrameSet.FrameSet`

======================
Processing LAS Files
======================

TODO:
