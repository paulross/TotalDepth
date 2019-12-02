.. TotalDepth API reference.

**********************
Glossary
**********************

.. note::
	Terms here starting with "RP66V1." are taken directly from the `RP66V1 glossary <http://w3.energistics.org/rp66/v1/rp66v1_defs.html>`_.
	They are lightly edited, corrected and enhanced before being reproduced here for the convenience of the reader.

.. glossary::
	:sorted:
	
	Absent Value
		A recorded value from a sensor that is not a true recorded value and should be ignored. A point of difficulty arises for a conformant application; within the :term:`LIS-79` format this is specified in the :term:`DFSR` so can be per frame array. For :term:`RP66V1` the absent value is supposed to be represented by having an attribute count of zero. In practice this never happens, instead a bunch of ad-hoc values need to be presumed such as -999, -999.25 based on their :term:`RepCode`. See also :term:`RP66V1.Absent Value`

	LAS
		Text based flog file format managed by the `Canadian Well Logging Society <http://www.cwls.org/las/>`_
	
	LIS
	LIS-79
		Log Information Standard. The original file format used by Schlumberger from 1979 onwards.
		It is a *proprietary*, *de-facto* standard.
	
	LIS-A
		*Enhanced* Log Information Standard. This adds somewhat to the [:term:`LIS-79`] standard.
	
	RP66
		*Recommended Practice 66* is an API standard that describes a more advanced file format for, among other things, wireline logs. Comes in two flavours version 1 and version 2. Often (and incorrectly) referred to as :term:`DLIS`.
		
	RP66V1
		*Recommended Practice 66* version 1 is an API standard first published on MAY 1, 1991 that describes a (mostly) more advanced file format compared with :term:`LIS`. The specification can be found online from the Petrotechnical Open Software Corporation here `RP66V1 standard <http://w3.energistics.org/rp66/v1/rp66v1.html>`_  See also the `RP66V1 glossary <http://w3.energistics.org/rp66/v1/rp66v1_defs.html>`_
		
	RP66V2
		*Recommended Practice 66* version 2 is an API standard first published in June 1996 that describes a (mostly) more advanced file format compared with :term:`RP66V1`. It is unused by the industry and will not be referenced here. The specification can be found online from the Petrotechnical Open Software Corporation here `RP66V2 standard <http://w3.energistics.org/rp66/v2/rp66v2.html>`_ See also the `RP66V2 glossary <http://w3.energistics.org/rp66/v2/rp66v2_defs.html>`_
				
	DLIS
		This adds schema specific semantics to :term:`RP66V1` or :term:`RP66V2`.

	RepCode
	Rep Code
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
		*Unit of Measure* for engineering values. In :term:`LIS` these are a set of fixed terms organised into several categories, such as *Linear Length*. Values can only be converted between units of in the same category. In :term:`RP66V1` these are composed by a BNF parseable string.
				
	FFLR
		See :term:`Fixed Format Logical Record`.
		
	Fixed Format Logical Record
		This is an internally complete record whose format is described by a standard. Does not occur in :term:`RP66V1`.
		
	EFLR
		See :term:`Explicitly Formatted Logical Record`.
		
	Explicitly Formatted Logical Record
		This is an internally complete, self-describing record. See also :term:`RP66V1.Explicitly Formatted Logical Record`
		
	IFLR
	Indirectly Formatted Logical Record
		This is a Logical Record whose format is described by another EFLR. The EFLR that describes an IFLR might be identified formally; for example by a specific reference to an EFLR (as in RP66) or informally; by some heuristic (as in LIS) such as "the immediately prior Logical Record that is type 64 i.e. a :term:`Data Format Specification Record`. See also :term:`RP66V1.Indirectly Formatted Logical Record`

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
		A Log Pass contains one or more :term:`Frame Array` (s).
		The number of allowable Frame Arrays within a Log Pass depends on the log format:
		
		:term:`LAS` can only support a single Frame Array within a Log Pass.
		
		In the :term:`LIS` format the Log Pass is defined by a single :term:`DFSR` Logical Record. This can describe up to two Log Passes (type 0 or type 1) Logical Records.
		In practice only type 0 exists so LIS has just one Frame Array per Log Pass. 
		
		:term:`RP66V1` supports any number of Frame Arrays within a Log Pass and usually does.

	Frame Set
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
		Logical Record header. The bytes that describe the type and attributes of a Logical Record.
		
	Backup Mode
		A means of specifying what happens to plotted lines when they go off scale. Typical examples are None (all intermediate data is lost) and 'wrap' (all data is plotted with lines at modulo scale).
		
	Frame
		An array of values for each channel at a particular depth (or time).
		
	RP66V1.Attribute
		One of possibly many specific named items of information or data associated with an Object. An Attribute is similar in function to a column value of a row in a table or to a field of a record in a database relation. Its information content can be more general, however.

	RP66V1.Absent Value
		The Value of an Attribute is an Absent Value and is undefined when the Attribute Count is zero. A Channel Sample Value is an Absent Value and is undefined when its Dimension Count is zero. Under DLIS, Absent Values are explicitly absent and are not represented by specially-designated numeric quantities.
		
		.. warning::

			Unfortunately RP66V1 does not allow this to be set *per frame* (i.e. per :term:`RP66V1.IFLR`) but only *per channel*.
			So data providers use a fixed and undeclared value such as -999 for integers and -999.25 for floats.
			This allows per-frame *and* per-channel absent values which means that RP66V1 files from all providers should be treated with some care in this area.
			
	RP66V1.Channel
		A measured or computed quantity that occurs as a sequence of samples indexed against time, depth, or some other physical dimension of a well. Also a Set Type.
	
	RP66V1.Characteristic
		A descriptive feature of a Set, an Object, or an Attribute. The Characteristics of a Set are its Name and Type, of an Object its Name, and of an Attribute its Label, Count, Representation Code, Units, and Value.

	RP66V1.Company Code
		A numeric code assigned to a company that writes information under the DLIS format.
		Each company (or major division) is assigned a unique Company Code by the API.
		
	RP66V1.Component
		The basic syntactic unit of an Explicitly Formatted Logical Record (EFLR).
		A Component consists of a Component Descriptor (one byte), followed by zero or more fields that contain Characteristics associated with a Set, Object, or Attribute.
		
	RP66V1.Component Descriptor
		The first byte of a Component. It has a Role field (bits 1-3), which specifies whether the Component describes a Set, Object, or Attribute, and a Format field (bits 4-8), which indicate which Characteristics of the thing described are present in the remainder of the Component.
		
	RP66V1.Component Format
		See :term:`RP66V1.Component Descriptor`.
	
	RP66V1.Component Role
		See :term:`RP66V1.Component Descriptor`.
	
	RP66V1.Compound Representation Code
		A Representation Code that is defined in terms of other simpler Representation Codes.

	RP66V1.Consumer
		The system or application program or company that reads information recorded under the DLIS Logical format. The Consumer reads what the Producer writes.

	RP66V1.Copy Number
		A number, having meaning only within the context of a Logical File, that is used to distinguish two Objects of the same Type that have the same Identifier and Origin. The Name of an Object consists


	RP66V1.Count
		One of the five Characteristics of an Attribute.
		The Count specifies how many Elements are in the Value of the Attribute. When the Count is zero, the Attribute has an Absent Value.

	RP66V1.Data Descriptor Reference
		The first field of an Indirectly Formatted Logical Record (IFLR). The Data Descriptor Reference is the Name of an Object that identifies and describes a sequence of IFLRs. Each IFLR Type is associated with a specific Set Type to which such Objects belong.

	RP66V1.Defining Origin
		The first Origin Object in a Logical File.
		The Defining Origin describes the environment under which the Logical File was created.
		
	RP66V1.Descriptor
		See :term:`RP66V1.Component Descriptor`.
	
	RP66V1.Dictionary
		A Dictionary is a database in which Identifiers used under DLIS are administered.
		The standard does not specify the mechanisms for designing, creating, or managing Dictionaries.
		However, it does specify for which Set Types Identifiers should be managed.
		The statement, "Names of Set Type X are dictionary-controlled" means that Identifiers for such Objects have a persistent meaning in all Logical Files in which they occur (by a given Producer).
		Identifiers of Objects for Set Types that are not dictionary-controlled are considered void of meaning and are expected to be computer- generated.
		
	RP66V1.Dimension
		This is a vector of integers which describe the form and size of a rectangular array that is represented elsewhere, for example as a Channel Sample.
		The first integer specifies the number of remaining integers and the dimensionality of the array (i.e., 1-d, 2-d, etc.).
		The remaining integers specify the number of elements along each dimension (or coordinate) of the array.
		The Dimension of an array is typically contained in the Dimension Attribute of some Object that is associated with the array.

	RP66V1.Element
		One of a vector of homogeneous quantities that make up the Value of an Attribute or of a Channel Sample.
		A Value or Sample may consist of one or more Elements.
		All Elements have the same Representation Code and Units.
		The number of Elements of an Attribute Value is specified by the Attribute Count.
		The number of Elements of a Channel Sample is specified by its associated Dimension.
		
	RP66V1.Encryption Packet
		An optional sequence of bytes that follows the Logical Record Segment Header and precedes the Logical Record Segment Body and that contains information used to decrypt the Logical Record. The first two bytes of the Encryption Packet specify its length, and the next two bytes specify the Producer’s Company Code. The remaining bytes are meaningful only to the Producer.

	RP66V1.EFLR
		See :term:`RP66V1.Explicitly Formatted Logical Record`
		
	RP66V1.Explicitly Formatted Logical Record
		One of two kinds of Logical Record defined under DLIS.
		The Body of an EFLR is a sequence of Components that combine to describe a single Set of Objects.
		An EFLR is self-describing and can be interpreted without the use or knowledge of any other Logical Records.
		More simply put, an Explicitly Formatted Logical Record is a table of rows and columns. Each row/column contains a  :term:`RP66V1.Attribute`.

	RP66V1.Format Version
		A two-byte field immediately following the Visible Record Length in Visible Records on Record Storage Units (e.g., standard 9-track tapes).
		This field is used to distinguish DLIS from other formats and to distinguish DLIS Version 1 from later major versions.
		The first byte of the Format Version contains the value FF (hex), and the second byte is the major version number of the standard (in the current case, 1).
		
	RP66V1.Frame
		The Indirectly Formatted Data of an IFLR of Type FDATA (see Appendix A) is called a Frame.
		A Frame is made of a Frame Number, followed by a set of Channel sample values, one sample per Channel, all sampled at the same index value.
		One of the Channels may serve as an index. When this is the case, it is always the first Channel in the Frame.
		When there is no Channel index, then the Frame Number serves as an index.

	RP66V1.Frame Data
		Information recorded in Frames is called Frame Data. This consists of Channel samples, one sample per Channel per Frame.

	RP66V1.Frame Number
		A positive integer recorded at the beginning of each Frame.
		The Frame Number is a sequential index of the Frames of the same Frame Type. Frame n precedes Frame n+1, although other Logical Records may fall between.

	RP66V1.Frame Type
		The Name (Origin, Copy Number, Identifier) of a Frame Object used to group Frames that have the same organization. This Name is also used as the Data Descriptor Reference in the Frames, and the Frames are known to be of the given Frame Type. Frames of a given Frame Type all contain samples of the same set of Channels and all in the same order. The Representation Code and Units used to record a Channel are the same in all Frames of a given Frame Type but may be different in another Frame Type. A Channel sample may change size (number of Elements) from Frame to Frame and may even become Absent when its number of Elements reduces to zero.

	RP66V1.Header (Refer to Logical Record Segment Header)
		See :term:`RP66V1.Logical Record Segment Header`.

	RP66V1.Identifier
		That part of an Object Name that is textual. The Identifier is what commonly distinguishes one Object from another. Two Objects of the same Type may have the same Identifier, in which case the other Subfields of the Name are used to distinguish the Objects. Identifiers of certain Types of Objects uniquely identify the type of data represented in the Object, and such Identifiers (typically mnemonic in nature) are dictionary-controlled.
		
	RP66V1.Index Channel
		The first Channel in a Frame, when the Frame has an Index Channel. A Frame may be indexed by Frame Number only and need not have an Index Channel. Whether or not a Frame has an Index Channel is specified in the associated Frame Object. When a Frame has an Index Channel, then all Channel values in the Frame are considered to be sampled at the index indicated by the value of the Index Channel.

	RP66V1.Indirectly Formatted Data
		That part of the Body of an Indirectly Formatted Logical Record (IFLR) that follows the Data Descriptor Reference.

	RP66V1.IFLR
		See :term:`RP66V1.Indirectly Formatted Logical Record`
		
	RP66V1.Indirectly Formatted Logical Record
		One of two kinds of Logical Record defined under DLIS. The Body of an IFLR consists of a Data Descriptor Reference, followed by an arbitrary number of bytes of Indirectly Formatted Data. This data is not self-descriptive. Instead, its format is determined from information contained in the Object named by the Data Descriptor Reference and possibly related Objects. For example, the format of a Frame Data IFLR is specified by a Frame Object and by one or more Channel Objects referenced by the Frame Object.

	RP66V1.Invisible Envelope
		Data recorded on the physical medium and used as a control interface by the processor I/O subsystem, but not visible through normal application read/write requests, for example tape marks on magnetic tape.

	RP66V1.Lexicon
		A list of dictionary-controlled words or phrases applicable as Name Part Values for a particular Name Part Type. For example, each Producer manages a Lexicon of Entity names and another Lexicon of Quantity names.

	RP66V1.Locus
		A sequence of distinct points in space and time, each of which has a three-dimensional Position coordinate and a Time coordinate.

	RP66V1.Logical File
		A sequence of two or more contiguous Logical Records in a Storage Set that begins with a File Header Logical Record and contains no other File Header Logical Records. A Logical File must have at least one OLR (Origin) Logical Record immediately following the File Header Logical Record. A Logical File supports user-level organization of data.

	RP66V1.Logical Format
		The view of DLIS data that is completely independent of any physical mapping. The DLIS Logical Format consists of a sequence of Logical Records organized into one or more Logical Files. This format is the same for any physical representation of the data.

	RP66V1.Logical Record
		A sequence of one or more contiguous Logical Record Segments. A Logical Record supports	application-level organization of data.

	RP66V1.Logical Record Body
		The sequential concatenation of the Logical Record Segment Bodies from the Logical Record Segments that make up the Logical Record.

	RP66V1.Logical Record Segment
		A sequence of contiguous 8-bit bytes organized to have a Logical Record Segment Header, followed (optionally) by an Encryption Packet, followed by a Logical Record Segment Body, followed (optionally) by a Logical Record Segment Trailer. Logical Record Segments are used to bind the Logical Format to a physical format.

	RP66V1.Logical Record Segment Attributes
		Eight bits of binary data that describe the attributes of a Logical Record Segment.

	RP66V1.Logical Record Segment Body
		The part of a Logical Record Segment that contains some or all of the data belonging to a Logical Record. The intersection of a Logical Record and one of its Logical Record Segments is the Logical Record Segment Body.

	RP66V1.Logical Record Segment Encryption Packet
		An optional packet of information, following the Logical Record Segment Header, that contains encryption/decryption information for the Logical Record Segment. The Encryption Packet begins with its size in bytes and the Company Code of the Producer. Any additional data in the Encryption Packet is meaningful only to the Producer’s organization.

	RP66V1.Logical Record Segment Header
		The first part of a Logical Record Segment. It contains the Logical Record Segment Length, the Logical Record Segment Attributes, and the Logical Record Type.

	RP66V1.Logical Record Segment Length
		A two-byte unsigned integer that specifies the combined length of all parts of the Logical Record Segment.

	RP66V1.Logical Record Segment Trailer
		The last part of a Logical Record Segment. It contains three fields, all of which are optional: the Padding, the Checksum, and the  Logical Record Segment Trailing Length.

	RP66V1.Logical Record Structure
		One of the attributes specified in the Logical Record Segment Attributes. It specifies whether the Logical Record is an EFLR or an IFLR.

	RP66V1.Logical Record Type
		A one-byte unsigned integer that indicates the general semantic content of the Logical Record.
		
	RP66V1.Long Name
		A structured textual description that provides an understanding, to humans, of the named item, with enough detail to distinguish it from similar items that have different meanings. It is not a unique identifier. A Long Name is represented in a Long-Name Object.

	RP66V1.Maximum Visible Record Length
		The maximum permitted length of a Visible on a Record Storage Unit. Its current value is 16,384 bytes.

	RP66V1.Minimum Visible Record Length
		The minimum permitted length of a Visible Record on a Record Storage Unit. Its current value is 20 bytes, which is based on the minimum Logical Record Segment Length (16 bytes) plus the Visible Record Length (2 bytes) and the Format Version (2 bytes).

	RP66V1.Name
		Used to refer to the Name Characteristic of a Set, Object, or Attribute. The Name of a Set or Attribute is a character string (Representation Code IDENT). The Name of an Object is an aggregate consisting of an integer Origin, an integer Copy Number, and a character Identifier.

	RP66V1.Name Part Type
		A classification of the words or phrases that apply to a particular part of the Long Name structure, for example Entity or Quantity.

	RP66V1.Name Part Value
		A word or phrase that applies to a particular part (Name Part Type) of a Long Name structure. For example, “Density” and “Porosity” are Name Part Values that apply to the Name Part Type “Quantity”.

	RP66V1.Object Component
		An Object Component indicates the beginning of a new Object in a Set and is followed by zero or more Attribute Components. The Attributes of an Object that has no Attribute Components are completely specified in the Template. The Object Component contains a single Characteristic, the Object Name, which is mandatory.

	RP66V1.Object
		A data entity that has a Name and a number of Attributes. An Object is like a row in a table of information. Its Attributes are like the column values in the row. Objects are recorded in EFLRs.

	RP66V1.Origin
		As an Object in a Logical File, an Origin contains information describing the original circumstances under which that or another Logical File was created. Only one Origin Object in a Logical File, namely the first one, describes that Logical File. Additional Origin Objects describe other Logical Files from which data has been copied. Other Objects in a Logical File are keyed to their appropriate Origin Object by means of an integer Subfield in their Names, namely the Origin Subfield. This integer value matches the Origin Subfield of the appropriate Origin Object. This integer value is also commonly referred to as the Object’s Origin.

	RP66V1.Pad Bytes
		Pad Bytes are part of the Logical Record Segment Trailer and are used to alter the size of a Logical Record Segment to satisfy minimum size requirements or more commonly to make the Logical Record Segment Length divisible by some integer. In all cases, the Logical Record Segment Length must be divisible by two. Additionally, certain encryption methods may require the length of the Logical Record Segment Body plus the Pad Bytes to be divisible by some other factor.

	RP66V1.Pad Count
		This is the first byte of the Pad Bytes and indicates how many Pad Bytes there are. The maximum number of Pad Bytes may therefore not exceed 255.

	RP66V1.Padding
		An informal reference to Pad Bytes.

	RP66V1.Parent File
		The Logical File in which data are originally created. Some data in a Logical File may have been copied from other Logical Files.

	RP66V1.Path
		A sequence of space-time coordinates, where space is typically represented by depth, radial distance from a vertical line, and angular displacement about the same vertical line. The vertical line used is the one that goes through a well’s Well Reference Point, a point used to identify the location of a well. A Path may be represented by a combination of Channels, each of which represents one of the above-mentioned coordinates.

	RP66V1.Physical Format
		The way in which recorded data is located and organized on a particular physical medium such as a magnetic tape or disk file. With some I/O systems more than one organization and view of data is supported on the same medium. Each such view corresponds to a different physical format. For example, disk files may be viewed as having variable-length record structures, block structures, byte stream structures, etc., depending on the I/O facility that is used. The physical format determines the way in which Logical Record Segments are used but generally has no effect on Logical Records.

	RP66V1.Predecessor
		Used to indicate the relation between successive Logical Record Segments. If two Logical Record Segments belong to the same Logical Record, then one of them — the one that comes first — is a Predecessor of the other. The first Logical Record Segment of a Logical Record has no Predecessor.

	RP66V1.Private
		A Logical Record with Type ≥ 128 is said to be Private. In particular, the semantic content of such a Logical Record is decided upon solely by the Producer and not via any public standardization process. Private Logical Records are available to consumers in general, unless encrypted. The fact that a Logical Record is Private does not imply that it is also encrypted.

	RP66V1.Producer
		The system or application program or company that records information under the DLIS Logical  Format. The Producer writes what the Consumer reads.
		
	RP66V1.Public
		A Logical Record with Type < 128 is said to be Public. In particular, the semantic content of such a Logical Record is agreed to by the all users via a standardization process administered by the API. Such Logical Records may not be used except in accordance with the standard definition. Public Logical Records may be encrypted or not, according to the needs of the Producer.
		
	RP66V1.Radial Drift
		Radial Drift is the perpendicular distance of a point from a vertical line that passes through the Well Reference Point of a well.

	RP66V1.Record Structure
		One of possibly many different physical formats. A Storage Unit is said to have Record Stucture if data is written and read in sequential, variable-length records. For all Record Structure Storage Units each record must begin with a two-byte unsigned integer Visible Record Length, followed by a two-byte Format Version, followed by an integer number of Logical Record Segments. Other requirements, for example use of Tape Marks, depend on the particular physical medium.

	RP66V1.Representation Code
		Each distinct piece of information in the Logical Format has a well-defined representation that extends across one or more bytes. Each different representation is identified by a one-byte Representation Code. Representation Codes are defined in Appendix B and identify the various floating point, integer, and text representations permitted under the DLIS.

	RP66V1.Sample (of a Channel)
		A Channel Sample is one of a sequence of evaluations of a Channel. A Channel Sample may be a scalar sensor reading (i.e., a single number), or it may be an array representing a waveform or some other multi-dimensional data.

	RP66V1.Semantics
		Semantics is the definition of what data means and how it is used. Whereas syntax provides rules for recording Objects in Sets, semantics defines the Objects that may be recorded, e.g., the File-Header, Origin, Channel, Frame, etc. Objects.

	RP66V1.Set Component
		A Set Component indicates the beginning of a Set and is followed by one or more Template Attribute Components. A Set Component always contains a Type Characteristic and may contain a Name Characteristic.

	RP66V1.Set
		A data entity that has a Type and optionally a Name, and contains a number of Objects. A Set is like a table of information in which the Objects are the rows of the table. Each Set is contained in an EFLR (exactly one Set per EFLR), and there may be more than one Set with the same Type in a Logical File.
	
	RP66V1.Set Type
		A textual identifier of the type of Objects contained in a Set. The Objects in a Set are characterized by the Attributes in the Template of the Set. The Attributes associated with each given Set Type are specified in the standard.

	RP66V1.Slot
		A data entity that has a Type and optionally a Name, and contains a number of Objects. A Set is like a table of information in which the Objects are the rows of the table. Each Set is contained in an EFLR (exactly one Set per EFLR), and there may be more than one Set with the same Type in a Logical File. One of a fixed number of positions in a Frame for recording a single Channel Sample value. Channels are assigned to Slots in a Frame in a specific order, and all Slots follow the Frame Number. The Index Channel, if there is one, is in the first Slot of a Frame.

	RP66V1.Splice
		A Splice is the result of concatenating two or more instances of a Channel (e.g., from different runs) to obtain a resultant Channel defined over a larger domain or interval. The information associated with a Splice is represented in a Splice Object.

	RP66V1.Static Information
		Static Information consists of Objects typically used to describe Channels and Frames, and information about Channels and Frames. Static Information is typically required by an application prior to the processing of Frames.

	RP66V1.Storage Set
		A group of Storage Units that contain a common DLIS Logical Format (e.g., a sequence of Logical Files) and for which at least two Storage Units are spanned by a single Logical File.

	RP66V1.Storage Set Identifier
		A 60-character ASCII field in the Storage Unit Label used to identify a Storage Set.

	RP66V1.Storage Unit
		Something that contains DLIS data and is manageable as a unit at the human level, (e.g., a tape or disk file).

	RP66V1.Storage Unit Label
		The first 80 bytes of the Visible Envelope of a Storage Unit. The Storage Unit Label consists of five fixed-length ASCII fields used to identify the Storage Unit and the Storage Set of which it is a part.

	RP66V1.Storage Unit Sequence Number
		A positive integer (its ASCII representation) in the Storage Unit Label that indicates the order in which a Storage Unit occurs in a Storage Set.

	RP66V1.Storage Unit Structure
		An ASCII keyword in the Storage Unit Label that reflects the Physical Format of the Storage Unit and indicates the binding mechanism between the Physical Format and the DLIS Logical Format.

	RP66V1.Subfield
		A part of a datum for which the representation is described by a simple (not compound) Representation Code. For example, the Subfields of a datum having Representation Code OBNAME are, in order, an integer (UVARI), another integer (USHORT), and a string (IDENT).

	RP66V1.Successor
		Used to indicate the relation between successive Logical Record Segments. If two Logical Record Segments belong to the same Logical Record, then one of them — the one that comes second — is a Successor of the other. The last Logical Record Segment of a Logical  Record has no Successor.

	RP66V1.Syntax
		Syntax is the definition of the rules for how to record data but not for what the data means (at the application level) or how it is to be used. Syntax does convey meaning of data, but at a level below applications. For example, the rules of syntax tell when a Component has a Type Characteristic and how to get it, but syntax provides no information on the meaning or use of the values the Type Characteristic may have.

	RP66V1.Template
		A sequence of Attributes at the beginning of a Set that specify defaults for the Objects in the Set. Attributes in the Template must have Labels. Objects in the Set have no Attributes other than those identified in the Template.

	RP66V1.Tool Zero Point
		A fixed point on the tool string (usually the bottom of the bottom tool) that stands opposite the Well Reference Point when Borehole Depth is zero.

	RP66V1.Trailing Length
		The optional last field in the Logical Record Segment Trailer that contains a copy of the Logical Record Segment Length.

	RP66V1.Transient Information
		Transient Information consists of Objects that correspond to events that occur during the processing of Frames. These events can affect Objects in the Static Information or can correspond to messages between the operator and the system.

	RP66V1.Unzoned
		A Parameter or Computation Object is said to be Unzoned when it has the same value everywhere. This is the case when the Zones Attribute of the Object is absent.

	RP66V1.Update
		An Update is a change made to data represented by an Object (e.g., a Parameter) previously recorded in a Logical File. The change and information related to the change are represented in an Update Object recorded in the same Logical File.

	RP66V1.Value (of an Attribute)
		The Value of an Attribute is the data contained in its Value Characteristic. A Value may consist of one or more Elements, each of which has the same Units and Representation Code.

	RP66V1.Vertical Depth
		Depth measured along the Vertical Generatrix from the Well Reference Point. Vertical depth increases in a downward direction and is negative above the Well Reference Point.

	RP66V1.Vertical Generatrix
		A vertical line that passes through the Well Reference Point.

	RP66V1.Visible Envelope
		Information on a Storage Unit that is provided to applications as normal data by the processor’s I/O subsystem, but which is not part of the DLIS Logical Format. Information in the Visible Envelope includes the Storage Unit Label. Other information in the Visible Envelope may be used to define or enhance the binding of Logical Record Segments to the Physical Format.

	RP66V1.Visible Record
		A Visible Record is a term that applies to Record Structure Storage Units. It consists of all the data bytes accessed by means of a record read operation from the system-specific file access subsystem.

	RP66V1.Visible Record Length
		When DLIS information is recorded in variable length pysical records, each Visible Record begins with a two-byte unsigned integer length of the Visible Record called the Visible Record Length. This length is considered to be external the DLIS Logical Format.

	RP66V1.Well Reference Point
		A unique point that is the origin of a well’s spatial coordinate system for information in a Logical File. This point is defined relative to some permanent vertical structure, such as ground level or mean sea level, and to three independent geographical coordinates, which typically include Latitude and Longitude. The same well may have different Well Reference Points in different Logical Files.

	RP66V1.Zone
		A Zone is a single interval in depth or time. The depth coordinate may be either Vertical Depth or Borehole Depth.

	RP66V1.Zoned
		A Parameter or Computation Object is said to be Zoned when it has different values in different intervals along a depth or time domain or is undefined in some interval of a depth or time domain. This is the case when the Zones Attribute of the Object is not absent.
