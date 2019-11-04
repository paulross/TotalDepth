TotalDepth.LIS.core.Units (Unit Conversion)
===========================================

.. toctree::
   :maxdepth: 2

.. automodule:: TotalDepth.LIS.core.Units
    :member-order: bysource
    :members:
    :special-members:


Examples
-------------

Converting bytes objects::

    from TotalDepth.LIS.core import Units
    
    v = Units.convert(1.0, b"M   ", b"FEET")
    # v is now 3.281



Testing
--------------

The unit tests are in :file:`test/TestUnits.py`.

