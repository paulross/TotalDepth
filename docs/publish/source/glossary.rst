.. TotalDepth API reference.

**********************
Glossary
**********************

.. glossary::
	:sorted:
	
	Absent Value
		A recorded value from a sensor that is not a true recorded value and should be ignored. A point of difficulty arises for a conformant application; within the :term:`LIS-79` format this is specified in the :term:`DFSR` so can be per frame array. For :term:`RP66V1` the absent value is supposed to be represented by having an attribute count of zero. In practice this never happens, instead a bunch of ad-hoc values need to be presumed such as -999, -999.25 based on their :term:`RepCode`.

	LIS
	LIS-79
		Log Information Standard. The original file format used by Schlumberger from 1979 onwards.
		It is a *proprietary*, *de-facto* standard.
	
	LIS-A
		*Enhanced* Log Information Standard. This adds somewhat to the [:term:`LIS-79`] standard.
	
	RP66
		*Recommended Practice 66* is an API standard that describes a more advanced file format for, among other things, wireline logs. Comes in two flavours version 1 and version 2. Often (and incorrectly) referred to as :term:`DLIS`.
		
	RP66V1
		*Recommended Practice 66* version 1 is an API standard first published on MAY 1, 1991 that describes a (mostly) more advanced file format compared with :term:`LIS`. The specification can be found online from ‘Petrotechnical Open Software Corporation <http://w3.energistics.org/rp66/v1/rp66v1.html>‘_  See 'the RP66V1 glossary <http://w3.energistics.org/rp66/v1/rp66v1_defs.html>'
		
	RP66V2
		*Recommended Practice 66* version 2 is an API standard first published in June 1996 that describes a (mostly) more advanced file format compared with :term:`LIS`. The specification can be found online from ‘Petrotechnical Open Software Corporation <http://w3.energistics.org/rp66/v2/rp66v2.html>‘_ It is unused by the industry and will not be referenced here. See 'the RP66V1 glossary <http://w3.energistics.org/rp66/v2/rp66v2_defs.html>'
		
		
	DLIS
		This adds schema specific semantics to :term:`RP66V1` or :term:`RP66V2`.

	RepCode
		See :term:`Representation Code`.
		
	Representation Code
		A code, usually an integer, that describes how a particular run of bytes should be interpreted as a
		value (number, string etc.). For example in the LIS standard representation code 68 describes a 32 bit
		floating point format.
	
	Mnem
		See :term:`Mnemonic`.
		
	Mnemonic
		[:term:`LIS`] A four byte identifier that is human readable e.g. ``RHOB`` for Bulk Density.
		
	Engineering Value
		A numeric value together with its units of measure.
		
	UOM
		*Unit of Measure* for engineering values. In :term:`LIS` these are a set of fixed terms organised into several categories, such as *Linear Length*. Values can only be converted between units of in the same category. In :term:`RP661` these are composed by a BNF parseable string.
				
	FFLR
		See :term:`Fixed Format Logical Record`.
		
	Fixed Format Logical Record
		This is an internally complete record whose format is described by a standard. Does not occur in :term:`RP66V1`.
		
	EFLR
		See :term:`Explicitly Formatted Logical Record`.
		
	Explicitly Formatted Logical Record
		This is an internally complete, self-describing record.
		
	IFLR
		See :term:`Indirectly Formatted Logical Record`.
	
	Indirectly Formatted Logical Record
		This is a Logical Record whose format is only completely described by another EFLR. The EFLR that describes an IFLR might be identified formally; for example by a specific reference to an EFLR (as in RP66) or informally; by some heuristic (as in LIS) such as "the immediately prior Logical Record that is type 64 i.e. a :term:`Data Format Specification Record` ".

	DFSR
		See :term:`Data Format Specification Record`
	
	Data Format Specification Record
		[:term:`LIS`] An EFLR that describes type 0 or type 1 binary IFLRs containing log data. A DFSR consists of a set of Entry Blocks followed by a list of Datum Specification Blocks.
		
		NOTE: The LIS specification associates a particular DFSR type ``0 | 1`` with binary IFLRs of type ``0 | 1``.
		These collections will be independent of each other and thus permits the simultaneous recording of entirely different data sets.
		In practice there is no evidence that any LIS implementations supports this.
		
	Entry Block
		[:term:`LIS`] A variable length block of data that describes a static value in DFSR. This value is local to a Log Pass. For example and Entry Block might describe the NULL or absent value for any channel in a Log Pass.
		
	DSB
		See :term:`Datum Specification Block`.
		
	Datum Specification Block
		[:term:`LIS`] A fixed format data block that defines the characteristics of a single, independent, data channel in a DFSR.
		
	Log Pass
		A TotalDepth term that describes a continuous body of logging data recorded simultaneously and independent of any other recording.
		Examples might be  "Repeat Section" or "Main Log".
		In the :term:`LIS` format this is defined by a single Logical Record, the :term:`DFSR`, plus multiple type 0 or type 1 Logical Records that the DFSR describes. A Log Pass contains one or more :term:`Frame Array`s
		The number of Frame Arrays within a Log Pass depends on the log format.
		:term:`LAS` supports a single Frame Array within a Log Pass. :term:`LIS` can support up to two Frame Arrays within a Log Pass but in practice does not. :term:`RP66V1` supports any number of Frame Arrays within a Log Pass and often does.

	Frame Array
		A set of frames representing multi-channel data that is typically depth or time series based.
		
	Xaxis
	X Axis
		The index channel in an array, for example an array of frames. Typically depth or time.
		
	Physical Record
		[:term:`LIS`] A formal record in a LIS file. Physical Records consist of a header, optional payload and optional trailer. Logical Records consist of the payloads of one or more Physical Records.
		
	Logical Record
		[:term:`LIS`] A formal record from a LIS file. Logical Records consist of a header and optional payload. The Logical Records *type* is identified in the header. The interpretation of the payload of (some) Logical Records types is defined in the LIS standard. Logical Records consist of the payloads of one or more Physical Records. Logical Records are either EFLR or IFLR records.
	
	LRH
	Logical Record header
		The bytes that describe the type and attributes of a Logical Record.
		
	Backup Mode
		A means of specifying what happens to plotted lines when they go off scale. Typical examples are None (all intermediate data is lost) and 'wrap' (all data is plotted with lines at modulo scale).
		
	Frame
		An array of values for each channel at a particular depth (or time).
	
