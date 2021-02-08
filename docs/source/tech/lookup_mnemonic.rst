.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. Description of how TotalDepth does unit conversion.

.. _TotalDepth-lookup_mnemonic:

*********************************************************************
Schlumberger Mnemonics
*********************************************************************

TotalDepth provides a Python API to the `Schlumberger’s Oilfield Services Data Dictionary (OSDD) <https://www.apps.slb.com/cmd>`_

To quote the site:

*This evergreen database delivers descriptions of more than 50,000 Schlumberger logging
tools, analytical software, and log curves and parameters.
It also provides definitions of physical property measurements and relevant units of
measurement.
Special tables enumerate mineral properties and depositional environments.*


TotalDepth prvides Python APIs to access this data online.
The values are cached so that repeated calls do not refer to the website.
Here are the :py:mod:`TotalDepth.common.lookup_mnemonic` APIs:

.. list-table:: **Lookup Mnemonic API**
    :widths: 20 40 20 20
    :header-rows: 1
    
    * - Function
      - Argument
      - Return Value
      - Typical Cache Size
    * - :py:func:`slb_data_channel() <TotalDepth.common.lookup_mnemonic.slb_data_channel>`
      - A data channel name from a logging tool.
      - :py:class:`Channel <TotalDepth.common.lookup_mnemonic.Channel>`
      - 128
    * - :py:func:`slb_parameter() <TotalDepth.common.lookup_mnemonic.slb_parameter>`
      - A well site parameter.
      - :py:class:`Parameter <TotalDepth.common.lookup_mnemonic.Parameter>`
      - 256
    * - :py:func:`slb_logging_tool() <TotalDepth.common.lookup_mnemonic.slb_logging_tool>`
      - A logging tool name.
      - :py:class:`LoggingTool <TotalDepth.common.lookup_mnemonic.LoggingTool>`
      - 64

Examples:

.. code-block:: python

    >>> from TotalDepth.common import lookup_mnemonic
    
    >>> lookup_mnemonic.slb_data_channel('RHOB')
    Channel(
        channel='RHOB',
        description='Bulk Density',
        unit_quantity='Density',
        property='Bulk_Density',
        related_tools=(
            ToolDescription(tool='ADN', description='Bulk Density'),
            ToolDescription(tool='ADN4', description='Bulk Density'),
            ToolDescription(tool='ADN6C', description='Bulk Density'),
            ToolDescription(tool='ADN8', description='Bulk Density'),
            ToolDescription(tool='APS-C', description='Bulk Density'),
            ToolDescription(tool='DV6MT', description='Bulk Density'),
            ToolDescription(tool='ECO6', description='Bulk Density'),
            ToolDescription(tool='FGTC', description='Bulk Density'),
            ToolDescription(tool='HLDS-D', description='Bulk Density'),
            ToolDescription(tool='HLDT', description='Bulk Density'),
            ToolDescription(tool='HLDTA', description='Bulk Density'),
            ToolDescription(tool='ILDT-A', description='Bulk Density'),
            ToolDescription(tool='ILDT-B', description='Bulk Density'),
            ToolDescription(tool='LDS-C', description='Bulk Density'),
            ToolDescription(tool='LDT', description='Bulk Density'),
            ToolDescription(tool='LDTA', description='Bulk Density'),
            ToolDescription(tool='LDTC', description='Bulk Density'),
            ToolDescription(tool='LDTD', description='Bulk Density'),
            ToolDescription(tool='PGT', description='Bulk Density'),
            ToolDescription(tool='PGTE', description='Bulk Density'),
            ToolDescription(tool='PGTK', description='Bulk Density'),
            ToolDescription(tool='SADN8', description='Bulk Density'),
            ToolDescription(tool='TBT-A', description='Bulk Density'),
            ToolDescription(tool='V475', description='Bulk Density')
        ),
        related_products=(
            ProductDescription(product='CMR_DMRP', description='Bulk Density'),
            ProductDescription(product='CMR_DMRRXO', description='Bulk Density'),
            ProductDescription(product='ELAN-PLUS', description='Bulk Density'),
            ProductDescription(product='GEOSHARE', description='Bulk Density'),
            ProductDescription(product='HISTEC', description='Bulk Density'),
            ProductDescription(product='IESX', description='Bulk Density'),
            ProductDescription(product='IMPACT', description='Bulk Density'),
            ProductDescription(product='INVASION_FACTOR', description='Bulk Density'),
            ProductDescription(product='PETROSONIC', description='Bulk Density'),
            ProductDescription(product='POR_TX', description='Bulk Density'),
            ProductDescription(product='PREPLUS2_EC', description='Bulk Density'),
            ProductDescription(product='ROCKSOLID', description='Bulk Density'),
            ProductDescription(product='RUNIT_SYNTHETICS', description='Bulk Density'),
            ProductDescription(product='RWA_CLAY_CORR', description='Bulk Density'),
            ProductDescription(product='RWAC', description='Bulk Density'),
            ProductDescription(product='SCQ', description='Bulk Density'),
            ProductDescription(product='SONFRAC', description='Bulk Density'),
            ProductDescription(product='STPERM', description='Bulk Density')
        )
    )

    >>> lookup_mnemonic.slb_parameter('LATI')
    Parameter(
        code='LATI',
        description='Latitude',
        unit_quantity='Dimensionless',
        property='Latitude',
        related_products=(
            ProductDescription(product='CSUD_WSD', description='Latitude'),
            ProductDescription(product='MAXIS_WSD', description='Latitude')
        )
    )

    >>> lookup_mnemonic.slb_logging_tool('HDT')
    LoggingTool(
        code='HDT',
        technology='Dipmeter',
        discipline='Geology',
        method='WIRELINE',
        description='High Resolution Dipmeter Tool',
        related_channels=(
            ChannelDescription(channel='AZIM', description='Measured Azimuth'),
            ChannelDescription(channel='AZIX', description='Azimuth of Reference Sensor (Pad 1, if available)'),
            ChannelDescription(channel='C1', description='Caliper 1'),
            ChannelDescription(channel='C2', description='Caliper 2'),
            ChannelDescription(channel='DEVI', description='Hole Deviation'),
            ChannelDescription(channel='EWDR', description='East West Drift Component'),
            ChannelDescription(channel='FC0', description='HDT Fast Channel 0 (Speed Button)'),
            ChannelDescription(channel='FC1', description='HDT Fast Channel 1'),
            ChannelDescription(channel='FC2', description='HDT Fast Channel 2'),
            ChannelDescription(channel='FC3', description='HDT Fast Channel 3'),
            ChannelDescription(channel='FC4', description='HDT Fast Channel 4'),
            ChannelDescription(channel='FEP', description='Far Electrode Potential'),
            ChannelDescription(channel='FEP1', description='Far Electrode Potential 1'),
            ChannelDescription(channel='FEP2', description='Far Electrode Potential 2'),
            ChannelDescription(channel='HAZI', description='Hole Azimuth Relative to True North'),
            ChannelDescription(channel='NSDR', description='North South Drift'),
            ChannelDescription(channel='P1AZ', description='Pad 1 Azimuth in Horizontal Plane (0 = True North)'),
            ChannelDescription(channel='PP', description='Pad Pressure'),
            ChannelDescription(channel='RAZI', description='Raw Azimuth'),
            ChannelDescription(channel='RB', description='Relative Bearing'),
            ChannelDescription(channel='RC', description='Reference Check'),
            ChannelDescription(channel='RC1', description='Raw C1'),
            ChannelDescription(channel='RC2', description='Raw C2'),
            ChannelDescription(channel='RDEV', description='Raw Deviation'),
            ChannelDescription(channel='REFE', description='Reference'),
            ChannelDescription(channel='RHDT', description='Raw HDT Data Block'),
            ChannelDescription(channel='RRB', description='Raw Relative Bearing'),
            ChannelDescription(channel='SDEV', description='Sonde Deviation'),
            ChannelDescription(channel='TEMP', description='Computed Borehole Temperature'),
            ChannelDescription(channel='ZB', description='Zero Button')
        ),
        related_parameters=(
            ParameterDescription(parameter='AMOD', description='Averaging Mode Selection'),
            ParameterDescription(parameter='AZIM', description='Well Section Azimuth'),
            ParameterDescription(parameter='DANG', description='Dip Angle of the Bedding'),
            ParameterDescription(parameter='DAZI', description='Dip Azimuth of the Bedding'),
            ParameterDescription(parameter='DEVI', description='Well Section Deviation'),
            ParameterDescription(parameter='DISO', description='DIP Information Source'),
            ParameterDescription(parameter='HDTT', description='HDT Sonde Type'),
            ParameterDescription(parameter='LATD', description='Latitude (N=+ S=-)'),
            ParameterDescription(parameter='LOND', description='Longitude'),
            ParameterDescription(parameter='MCT', description='Mechanical Cartridge Type'),
            ParameterDescription(parameter='MDEC', description='Magnetic Field Declination'),
            ParameterDescription(parameter='MFIN', description='Magnetic Field Intensity'),
            ParameterDescription(parameter='MINC', description='Magnetic Field Inclination'),
            ParameterDescription(parameter='MTD', description='Measured Tie Depth'),
            ParameterDescription(parameter='RANO', description='Resistivity Anomaly Selection'),
            ParameterDescription(parameter='SFAN', description='Scale Factor of Anomalies'),
            ParameterDescription(parameter='STYP', description='Sonde Type')
        )
    )


References:

Unit conversion: :py:mod:`TotalDepth.common.lookup_mnemonic`


.. :py:mod:`TotalDepth.util.gnuplot`
