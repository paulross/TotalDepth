.. TotalDepth API reference.

Glossary
==========================

.. glossary::
	:sorted:

	LIS
	LIS-79
		Log Information Standard. The original file format used by Schlumberger from 1979 onwards.
		It is a *proprietary*, *de-facto* standard.
	
	LIS-A
		*Enhanced* Log Information Standard. This adds somewhat to the [:term:`LIS-79`] standard.
	
	RP66
		*Recommended Practice 66* is an API standard that describes a more advanced file format for, among other things, wireline logs. Comes in two flavours version 1 and version 2. Often (and incorrectly) referred to as :term:`DLIS`.
		
	DLIS
		This adds schema specific semantics to :term:`RP66`.

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
		*Unit of Measure* for engineering values. In :term:`LIS` these are a set of fixed terms organised into several categories, such as *Linear Length*. Values can only be converted between units of in the same category. In :term:`RP66` these are composed by a BNF parseable string.
				
	EFLR
		See :term:`Explicitly Formatted Logical Record`.
		
	Explicitly Formatted Logical Record
		This is an internally complete, self-describing record.
		
	IFLR
		See :term:`Indirectly Formatted Logical Record`.
	
	Indirectly Formatted Logical Record
		This is a Logical Record whose format is only completely described by another EFLR. The EFLR that describes an IFLR might be identified formally; for example by a specific reference to an EFLR (as in RP66) or informally; by some heuristic (as in LIS) such as "the immediately prior Logical Record that is type 64".

	DFSR
		See :term:`Data Format Specification Record`
	
	Data Format Specification Record
		[:term:`LIS`] An EFLR that describes type 0 or type 1 binary IFLRs containing log data. A DFSR consists of a set of Entry Blocks followed by a list of Datum Specification Blocks.
		
		NOTE: The LIS specification associates a particular DFSR type ``0 | 1`` with binary IFLRs of type ``0 | 1``. These collections will be independent of each other and thus permits the simultaneous recording of entirely different data sets. In practice however this rarely happens and it is debatable whether any or all LIS processing implementations support this.
		
	Entry Block
		[:term:`LIS`] A variable length block of data that describes a static value in DFSR. This value is local to a Log Pass. For example and Entry Block might describe the NULL or absent value for any channel in a Log Pass.
		
	DSB
		See :term:`Datum Specification Block`.
		
	Datum Specification Block
		[:term:`LIS`] A fixed format data block that defines the characteristics of a single, independent, data channel in a DFSR.
		
	Log Pass
		A TotalDepth term that describes a continuos body of logging data such as "Repeat Section" or "Main Log".
		In the :term:`LIS` format this is defined by a single Logical Record, the :term:`DFSR`, plus multiple type 0 or type 1 Logical Records that the DFSR describes.

	Frame Set
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
	
