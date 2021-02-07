.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Description of how TotalDepth does unit conversion.

.. _TotalDepth-tech-units:

*********************************************************************
Total Depth and Units
*********************************************************************

This describes how TotalDepth handles unit conversions.


LIS Units
=======================

LIS units are identified by a four character, uppercase ASCII string.
TotalDepth supports all known LIS units with the exchange values hard coded in :py:mod:`TotalDepth.LIS.core.Units`
The API is described there.


References:

LIS unit conversion: :py:mod:`TotalDepth.LIS.core.Units`


General Units
=======================

Clearly hard coded data is somewhat limiting.
RP66V2 specifies a unit convention whereby fundamental units can be combined, for example 'm/s' to 'ft/min', then the conversion factors could be calculated parsing those strings.

TotalDepth does not do this, instead opting for a short cut of pre-built lookup tables.
This uses an online source of unit conversion, the primary source is `Schlumberger’s Oilfield Services Data Dictionary (OSDD) <https://www.apps.slb.com/cmd/units.aspx>`_

This essentially provides tables such as::

    Code    Name                Standard Form   Dimension   Scale               Offset
    -----------------------------------------------------------------------------------
    DEGC    'degree celsius'    degC            Temperature 1                   -273.15
    DEGF    'degree fahrenheit' degF            Temperature 0.555555555555556   -459.67
    DEGK    'kelvin'            K               Temperature 1                   0
    DEGR    'degree rankine'    degR            Temperature 0.555555555555556   0

So conversion from, say DEGC to DEGF of 0.0 is::

    ((value - DEGC.offset) * DEGC.scale) / DEGF.scale + DEGF.offset

    ((0.0 - -273.15) * 1.0) / 0.555555555555556 + -459.67 == 32.0


Unit Code
----------------

The unit is uniquely identified by the code, for example 'DEGC'.
This is almost always the identifier in log data.


Standard Form
------------------------

The 'standard form' is the RP66V2 definition of the name of the units.
This can have multiple codes depending on the origin of the data.
For 'degC' this is::

    Code    Name                      Standard Form   Dimension   Scale               Offset
    -----------------------------------------------------------------------------------------
    DEGC    'degree celsius'          degC            Temperature 1                   -273.15
    deg C   'degree celsius'          degC            Temperature 1                   -273.15
    oC      'GeoFrame legacy unit'    degC            Temperature 1                   -273.15


Internal Representation of the Data
------------------------------------------

Each unit conversion is represented by a Unit class: :py:class:`TotalDepth.common.units.Unit`.
The entire conversion table is represented internally by a ``Dict[str, Unit]`` where the key is the Unit Code.
At runtime the OSDD web page is read, parsed and the internal data structure cached.
This happens the first time any of the APIs is accessed.
On demand a data structure ``typing.Dict[str, typing.List[str]]`` mapping Standard Form to a list of Unit Codes is created and cached.

If the OSDD web page can not be read, perhaps because the user is offline, the code falls back to reading a static JSON file at ``src/TotalDepth/common/data/osdd_units.json`` that contains the last version of the OSDD.\
This file is refreshed every time the integration test :py:func:`tests.integration.common.test_units.test_slb_units_write_to_json` is run.


Units Conversion
-----------------------

The simplest form of conversion is:

.. code-block:: python

    from TotalDepth.common import units
    
    unit_from = units.slb_units('DEGC')
    unit_to = units.slb_units('DEGF')
    result = units.convert(100.0, unit_from, unit_to)  # Gives 212.0


To convert all the values in a numpy array inplace there is ``units.convert_array(array: np.ndarray, unit_from: Unit, unit_to: Unit)``.

References:

Unit conversion: :py:mod:`TotalDepth.common.units`


.. :py:mod:`TotalDepth.util.gnuplot`
