Units
=======

.. toctree::
   :maxdepth: 2

.. automodule:: TotalDepth.LIS.core.Units
    :members:


Examples
-------------

Converting bytes objects::

    from TotalDepth.LIS.core import Units
    
    v = Units.convert(1.0, b"M   ", b"FEET")
    # v is now 3.281



Testing
--------------

The unit tests are in :file:`test/TestUnits.py`.

