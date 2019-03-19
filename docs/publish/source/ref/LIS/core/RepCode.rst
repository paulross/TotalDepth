*****************************************
LIS Handling of Representation Codes
*****************************************

This describes how TotalDepth.LIS handles representation codes, it covers several modules.

Design
==========================

There is a top level module ``RepCode`` that imports all sub-modules and provides some fundamental definitions. Sub-modules ``pRepCode`` and ``cRepCOde`` provide alternative implementations in Python or Cython.

``RepCode`` Module
====================================

Description
-------------
This provides the main interface to Representation Code processing as well as some fundamental definitions.

This module is the top level module that imports other sub-modules implemented in Python, Cython or C/C++. The Cython implementations take precedence as this module imports the sub-modules thus::

	from TotalDepth.LIS.core.pRepCode import *
	from TotalDepth.LIS.core.cRepCode import *

Usage
----------

It is designed to use thus::

	from TotalDepth.LIS.core import RepCode

Reference
------------

.. automodule:: TotalDepth.LIS.core.RepCode
   :members:

``pRepCode`` Module
=====================

This contains Python implementations.

Usage
----------

This module is not designed to imported directly, use ``RepCode`` instead. This module can be imported only for test purposes thus::

	from TotalDepth.LIS.core import pRepCode

Reference
------------

.. automodule:: TotalDepth.LIS.core.pRepCode
   :members:

``cRepCode`` Module
=====================

This contains Cython implementations. By the import mechanism used be ``RepCode`` these implementations take precedence over the implementations in ``pRepCode``.

Usage
----------

This module is not designed to imported directly, use ``RepCode`` instead. This module can be imported only for test purposes thus::

	from TotalDepth.LIS.core import cRepCode

Reference
------------


.. automodule:: TotalDepth.LIS.core.cRepCode
   :members:


Testing
============

The unit tests are in :file:`test/TestRepCode.py` and :file:`test/TestRepCode68.py`.
