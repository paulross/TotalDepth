.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Processing BIT files with Python

.. _total_depth.processing_bit_files:


Processing Western Atlas BIT Files
=======================================


.. _total_depth.processing_bit_files.numpy_arrays:

------------------------------
Reading a BIT File Log Data
------------------------------

Suppose that we have a file in ``~/tmp/BIT.bit`` and you want to read the frame data from a particular log pass, first import what we need::

    >>> from TotalDepth.BIT import ReadBIT
    >>> import os

Then read the BIT file::

    >>> fpath = os.path.expanduser('~/tmp/BIT.bit')
    >>> frame_arrays = ReadBIT.create_bit_frame_array_from_path(fpath)
    >>> frame_arrays
    [<TotalDepth.BIT.ReadBIT.BITFrameArray object at 0x10f7041c0>, <TotalDepth.BIT.ReadBIT.BITFrameArray object at 0x10f6d6880>]


In this file there is are two frame arrays, we can get the description of the first one using ``long_str()``::

    >>> print(frame_arrays[0].long_str())
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
        

To get the actual vales in the frame we can access the numpy array directly, either by channel ordinal or by name (spaces are significant)::

    >>> sp = frame_arrays[0].frame_array['SP  '].array
    array([[-2.49709030e+02],
           [-2.49709030e+02],
           [-2.49709030e+02],
           ...,
           [ 9.99999962e-05],
           [ 9.99999962e-05],
           [ 9.99999962e-05]])

Now, if you are familiar with numpy then all normal operations are possible, for example get the min:

    >>> sp.min()
    -2.49709030e+02

.. note::

    The ``LogPass.FrameArray`` is universal, but BIT can only represent one value per frame per channel.
    To access that value you need to use ``array[frame_index][0]``.





References:

BITFrameArray: :py:class:`TotalDepth.BIT.ReadBIT.BITFrameArray`

FrameArray: :py:class:`TotalDepth.common.LogPass.FrameArray`
