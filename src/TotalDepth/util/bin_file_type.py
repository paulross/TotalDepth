"""
Identifies the type of file as a string such as "PDF", "RP66V1" by an analysis (mostly) of the
initial bytes of the file.
"""

import re
import string
import typing

RE_COMPILED = {
    'RP66V1': {
        'Comment_1': re.compile(b'^[0 ]*([1-9]+)$'),
        'Comment_2': re.compile(b'^V1.(\\d\\d)$'),
        'Comment_3': re.compile(b'^RECORD$'),
        'Comment_4': re.compile(b'^[0 ]*([1-9]+)$'),
    },
    'RP66V2': {
        # See RP66v2 Part 3 Section 6 "Storage Unit Label Contents" table 3-1
        # First three fields are the same as RP66V2
        'Comment_1': re.compile(b'^[0 ]*([1-9]+)$'),  # 4 bytes
        'Comment_2': re.compile(b'^V1.(\\d\\d)$'),  # 5 bytes
        'Comment_3': re.compile(b'^RECORD$'),  # 6 bytes
        'Comment_4': re.compile(b'^B([1-9]+)[ ]*$'),  # 4 bytes
        'Comment_5': re.compile(b'^[ ]*[1-9]+$'),  # 10 bytes
        'Comment_6': re.compile(b'^[ ]*([1-9]+)?$'),  # 10 bytes
        'Comment_7': re.compile(b'^\\d\\d-[A-Z]{3}-\\d\\d\\d\\d$'),  # 11 bytes
        # 'Comment_8' : re.compile(b''), # 12 bytes
        'Comment_9': re.compile(b'^      $'),  # 6 bytes
        # 'Comment_10' : re.compile(b'      '), # 60 bytes
    }
}

# string.printable contains tab, backspace etc. which is undesirable:
# '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c'
ASCII_PRINTABLE_BYTES = set(
    # bytes(string.digits + string.ascii_letters + string.punctuation + ' \n\x0d\x0a', 'ascii')
    bytes(string.printable, 'ascii')
)
ASCII_VISUAL_BYTES = set(
    bytes(string.digits + string.ascii_letters + string.punctuation + ' ', 'ascii')
)
ASCII_BYTES_LOWER_128 = set(bytes(range(128)))
RE_LAS_VERSION_LINE = re.compile(br'^\s*VERS\s*\.\s+([\d.]+)\s*:\s*(.+?)?\s*$')


def _las(fobj: typing.BinaryIO, version_prefix: bytes) -> int:
    """Returns zero if this is a LAS file of specified version(s), non-zero otherwise."""
    fobj.seek(0)
    lines = []
    for line in fobj:
        comment_idx = line.find(b'#')
        if comment_idx != -1:
            line = line[:comment_idx]
        line = line.strip()
        if len(line) > 0:
            lines.append(line)
        if len(lines) > 1:
            break
    else:
        return 6
    # ~Version Information
    # if lines[0] not in (
    #         b'~V',
    #         b'~Version',
    #         b'~Version Information',
    #         b'~Version Information Section',
    #         b'~Version Information Block',
    #         B'~VERSION',
    #         B'~VERSION INFORMATION',
    #         B'~VERSION INFORMATION SECTION',
    #         B'~VERSION INFORMATION BLOCK',
    # ):
    #     return 1
    if not lines[0].startswith(b'~V'):
        return 1
    # VERS.                     2.0: CWLS log ASCII Standard Version 2.00
    m = RE_LAS_VERSION_LINE.match(lines[1])
    # version_fields = lines[1].split()
    if m is None:
        return 3
    # if len(version_fields) == 1:
    #     return 4
    if not m.group(1).startswith(version_prefix):
        return 5
    return 0


def _lasv12(fobj: typing.BinaryIO) -> int:
    return _las(fobj, b'1.2')


def _lasv20(fobj: typing.BinaryIO) -> int:
    return _las(fobj, b'2.0')


def _lasv30(fobj: typing.BinaryIO) -> int:
    return _las(fobj, b'3.0')


def _lis_bytes(by: bytes) -> int:
    """Basic LIS with no TIF markers.

    Physical Record Attributes
    ---------------------------
    The documentation describes these as bits 16 to 31.
    Here they are numbered as big-endian two byte format.
    So documentation <-> here:
    16 <-> 15
    31 <->  0

    ======    ====================================================
    Bit       Description
    ======    ====================================================
    15        Unused, reserved
    14        Physical record type (only 0 is defined)
    13-12     00 - No checksum, 01 - 16bit checksum, 10, 11 - Undefined
    11        Unused, reserved
    10        If 1 File number is present in trailer
    09        If 1 Record number is present in trailer
    08        Unused

    07        Unused, reserved
    06        If 1 then a previous parity error has occurred
    05        If 1 then a previous checksum error has occurred
    04        Unused
    03        Unused, reserved
    02        Unused
    01        If 1 there is a predecessor Physical Record
    00        If 1 there is a succcessor Physical Record
    ======    ====================================================

    In the above table:
    bit 15 is bit 7 of by[2].
    bit 8 is bit 0 of by[2].
    bit 7 is bit 7 of by[3].
    bit 0 is bit 0 of by[3].
    """
    if len(by) < 6:
        f'We need PRH and LRH which is six bytes not [{len(by)}] : {by}'
        return -1
    if by[2] & 0x40:
        # Bit 14 Physical record type (only 0 is defined)
        return 10
    if by[3] & 0x02:
        # First PR can not have a predecessor record
        return 20
    if by[2] & 0x20 and by[2] & 0x10 == 0:
        # Checksum bits 13-12 can not be 10, this is undefined
        return 30
    if by[2] & 0x30 == 0x30:
        # Checksum bits 13-12 can not be 11, this is undefined
        return 40
    # Crude length check
    prl = (by[0] << 8) + by[1]
    prl_min = 4 + 1  # PRH + one byte of logical data
    if by[2] & 0x10:
        # Checksum
        prl_min += 2
    if by[2] & 0x04:
        # File number
        prl_min += 2
    if by[2] & 0x02:
        # Record number
        prl_min += 2
    if prl < prl_min:
        return 50
    # LRH checks
    if by[4] == 0:
        # LR type must be non-zero for first LR
        return 60
    if by[5] != 0:
        # LR attributes must be zero
        return 70
    return 0


LIS_LEN_REQUIRED_BYTES = 6
TIF_LEN_REQUIRED_BYTES = 3 * 4
TIF_PLUS_LIS_LEN_REQUIRED_BYTES = TIF_LEN_REQUIRED_BYTES + LIS_LEN_REQUIRED_BYTES


def _lis(fobj: typing.BinaryIO) -> int:
    fobj.seek(0)
    by: bytes = fobj.read(LIS_LEN_REQUIRED_BYTES)
    if len(by) < LIS_LEN_REQUIRED_BYTES:
        return -1
    return _lis_bytes(by)


def _tif_initial(by: bytes) -> int:
    """Basic LIS with TIF markers correctly written.
    Checks 8 bytes exactly so 2^64.
    """
    assert len(by) >= 8, f'_lis_tif_initial(): needs at least 8 bytes not {len(by):d}'
    if by[:4] != b'\x00\x00\x00\x00':
        return 1
    if by[4:8] != b'\x00\x00\x00\x00':
        # TIF previous
        return 2
    return 0


def _lis_tif_general(by: bytes, tif_next: int) -> int:
    """Basic LIS with TIF markers correctly written (little endian).
    2^64 for first 8 bytes. 2^32 for tif_next. 2^11 for LIS."""
    r = _tif_initial(by)  # 2^64
    assert len(by) >= 12 + 4, f'_lis_tif_general(): needs at least 16 bytes not {len(by):d}'
    if r:
        return r
    # 32bit first TIF marker can not be greater than max PR size + TIF length.
    # Well I suppose it could if you imagine a huge amount of padding...
    if tif_next > 0xFFFF + 12:
        return 3
    # PR length is big endian
    pr_len = (by[12] << 8) + by[13]
    # Can be greater because of padding
    # TODO: Impose a pad limit, say modulo 4 bytes?
    if tif_next < pr_len + 12:
        return 4
    # const int TIF_FIRST_WORD_LIMIT            = 0xFFFF + 12;
    return _lis_bytes(by[12:])


def _lis_tif(fobj: typing.BinaryIO) -> int:
    """Basic LIS with TIF markers correctly written (little endian)."""
    fobj.seek(0)
    by: bytes = fobj.read(TIF_PLUS_LIS_LEN_REQUIRED_BYTES)
    if len(by) < TIF_PLUS_LIS_LEN_REQUIRED_BYTES:
        return -1
    # TIF next, little endian
    tif_next = 0
    for i in range(0, 4):
        tif_next += by[i + 8] << (i * 8)
    return _lis_tif_general(by, tif_next)


def _lis_tif_r(fobj: typing.BinaryIO) -> int:
    """Basic LIS with TIF markers reversed (big endian)."""
    fobj.seek(0)
    by: bytes = fobj.read(TIF_PLUS_LIS_LEN_REQUIRED_BYTES)
    if len(by) < TIF_PLUS_LIS_LEN_REQUIRED_BYTES:
        return -1
    # TIF next, big endian
    tif_next = 0
    for i in range(0, 4):
        tif_next <<= i * 8
        tif_next += by[i + 8]
    return _lis_tif_general(by, tif_next)


def _rp66v1_bytes(by: bytes) -> int:
    if len(by) < 80:
        return -1
    # RP66V2 Storage Unit Label (SUL) section 2.3.2
    if not RE_COMPILED['RP66V1']['Comment_1'].match(by[:4]):
        return 1
    if not RE_COMPILED['RP66V1']['Comment_2'].match(by[4:9]):
        return 2
    if not RE_COMPILED['RP66V1']['Comment_3'].match(by[9:15]):
        return 3
    if not RE_COMPILED['RP66V1']['Comment_4'].match(by[15:20]):
        return 4
    if len(by[20:80]) != 60:
        return 5
    for c in by[20:80]:
        if c not in ASCII_PRINTABLE_BYTES:
            return 6
    return 0


def _rp66v1(fobj: typing.BinaryIO) -> int:
    fobj.seek(0)
    by: bytes = fobj.read(80)
    return _rp66v1_bytes(by)


RP66V1_LEN_WITH_TIFF = TIF_LEN_REQUIRED_BYTES + 80


def _rp66v1_tif_general(by: bytes, tif_next: int) -> int:
    """RP66V1 with TIF markers correctly written (little endian)."""
    r = _tif_initial(by)
    if r:
        return r
    # First record must be the Storage Unit Label which is 80 bytes long. No padding.
    # 80 + 12 is 0x5c
    if tif_next != RP66V1_LEN_WITH_TIFF:
        return 3
    return _rp66v1_bytes(by[12:])


def _rp66v1_tif(fobj: typing.BinaryIO) -> int:
    """RP66V1 with TIF markers correctly written (little endian)."""
    fobj.seek(0)
    by = fobj.read(RP66V1_LEN_WITH_TIFF)
    if len(by) < RP66V1_LEN_WITH_TIFF:
        return -1
    # TIF next, little endian
    tif_next = 0
    for i in range(0, 4):
        tif_next += by[i + 8] << i
    return _rp66v1_tif_general(by, tif_next)


def _rp66v1_tif_r(fobj: typing.BinaryIO) -> int:
    """RP66V1 with TIF markers reversed (big endian)."""
    fobj.seek(0)
    by = fobj.read(RP66V1_LEN_WITH_TIFF)
    if len(by) < RP66V1_LEN_WITH_TIFF:
        return -1
    # TIF next, big endian
    tif_next = 0
    for i in range(0, 4):
        tif_next <<= i
        tif_next += by[i + 8]
    return _rp66v1_tif_general(by, tif_next)


def _rp66v2(fobj: typing.BinaryIO) -> int:
    fobj.seek(0)
    by = fobj.read(128)
    if len(by) < 128:
        return -1
    # TODO: Test this
    # RP66v2 Part 3 Section 6 "Storage Unit Label Contents" table 3-1
    if not RE_COMPILED['RP66V2']['Comment_1'].match(by[:4]):
        return 1
    if not RE_COMPILED['RP66V2']['Comment_2'].match(by[4:9]):
        return 2
    if not RE_COMPILED['RP66V2']['Comment_3'].match(by[9:15]):
        return 3
    if not RE_COMPILED['RP66V2']['Comment_4'].match(by[15:19]):
        return 4
    if not RE_COMPILED['RP66V2']['Comment_5'].match(by[19:29]):
        return 5
    if not RE_COMPILED['RP66V2']['Comment_6'].match(by[29:39]):
        return 6
    if not RE_COMPILED['RP66V2']['Comment_7'].match(by[39:50]):
        return 7
    # Serial number field can be anything, 12 bytes
    if by[62:68] != b'      ':
        return 9
    for c in by[68:128]:
        if c not in ASCII_PRINTABLE_BYTES:
            return 10
    return 0


def _ascii(fobj: typing.BinaryIO) -> int:
    """Returns 0 if all the bytes are ASCII characters 0 to 127, non-zero otherwise.
    """
    fobj.seek(0)
    if set(fobj.read(256)).issubset(ASCII_BYTES_LOWER_128):#ASCII_PRINTABLE_BYTES):
        return 0
    return 1


def _zip(fobj: typing.BinaryIO) -> int:
    """Returns 0 if the magic number is a ZIP file, non-zero otherwise.
    See: https://en.wikipedia.org/wiki/Zip_(file_format)#Structure
    504b 0304 or b'PK\x03\x04'
    Four bytes have to be right so 2^32.
    Do not support empty (b'\x50\x4b\x05\x06') or spanned (b'\x50\x4b\x07\x08') files.
    """
    fobj.seek(0)
    if fobj.read(4) == b'\x50\x4b\x03\x04':
        return 0
    return 1


def _pdf(fobj: typing.BinaryIO) -> int:
    """Returns 0 if the magic number is a PDF file, non-zero otherwise.
    https://en.wikipedia.org/wiki/PDF#File_structure
    Five bytes have to be right so 2^40
    """
    fobj.seek(0)
    if fobj.read(5) == b'%PDF-':
        return 0
    return 1


def _ps(fobj: typing.BinaryIO) -> int:
    """Returns 0 if the magic number is a Postscript file, non-zero otherwise.
    Five bytes have to be right so 2^40
    """
    fobj.seek(0)
    if fobj.read(5) == b'%!Ps-':
        return 0
    return 1


def _tiff(fobj: typing.BinaryIO) -> int:
    """Returns 0 if the magic number is a TIFF file, non-zero otherwise.
    From observed files.
    Four bytes have to be right so 2^32
    """
    fobj.seek(0)
    # 4949 2a00 3d00 0000 3e3e 205f 6766 665f 6669 II*.=...>> _gff_fi
    if fobj.read(4) == b'II*\x00':
        return 0
    return 1


def _xml(fobj: typing.BinaryIO) -> int:
    """Returns 0 if the file is a XML file, non-zero otherwise.
    """
    fobj.seek(0)
    if fobj.read(6) == b'<?xml ':
        return 0
    return 1


EBCDIC_PRINTABLE = set(
    b'\x40'  # Space
    b'\x81\x82\x83\x84\x85\x86\x87\x88\x89'  # a-i
    b'\x91\x92\x93\x94\x95\x96\x97\x98\x99'  # j-r
    b'\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9'  # s-z
    b'\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9'  # A-I
    b'\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9'  # J-R
    b'\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9'  # S-Z
    b'\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9'  # 0-9
)


def _segy(fobj: typing.BinaryIO) -> int:
    """Returns 0 if the file is a SEGY.
    EBCDIC charcters used. Reference: https://en.wikipedia.org/wiki/EBCDIC
    """
    fobj.seek(0)
    for i in range(3200):
        by = fobj.read(1)
        if len(by) != 1 or by[0] not in EBCDIC_PRINTABLE:
            return 1
    return 0


# Ordered so that more specific files are earlier in the list, more general ones later.
# Also, as an optimisation, the more common file formats appear earlier.
FUNCTION_ID_MAP: typing.Tuple[typing.Tuple[typing.Callable, str], ...] = (
    (_xml, 'XML'),  # '<?xml ', 6 characters so 2^(6*8) 2^48
    (_pdf, 'PDF'),  # 2^40
    (_ps, 'PS'),  # 2^40
    (_zip, 'ZIP'),  # 2^32
    (_tiff, 'TIFF'),  # 2^32
    (_segy, 'SEGY'),  # 3200 EBCDIC characters.
    (_lis_tif, 'LISt'),  # Tests with TIF markers are much more strict.
    (_lis_tif_r, 'LIStr'),
    (_lasv12, 'LAS1.2'),
    (_lasv20, 'LAS2.0'),
    (_lasv30, 'LAS3.0'),
    (_rp66v1, 'RP66V1'),
    (_rp66v1_tif, 'RP66V1t'),
    (_rp66v1_tif_r, 'RP66V1tr'),
    (_rp66v2, 'RP66V2'),
    (_ascii, 'ASCII'),
    (_lis, 'LIS'),  # LIS without TIF is potentially the weakest test, around 2^11
)
BINARY_FILE_TYPE_CODE_WIDTH: int = max(len(v[1]) for v in FUNCTION_ID_MAP)
BINARY_FILE_TYPES_SUPPORTED: typing.Set[str] = {v[1] for v in FUNCTION_ID_MAP}


# TODO: Allow more generic cases such as 'LAS', 'RP66" ?

BINARY_FILE_TYPE_DESCRIPTIONS: typing.Dict[str, str] = {
    'XML': 'eXtensible Markup Language',
    'PDF': 'Portable Document Format',
    'PS': 'Postscript',
    'ZIP': 'ZIP Compressed Archive',
    'TIFF': 'Tagged Image File Format',
    'SEGY': 'Society of Exploration Geophysicists seismic format Y',
    'LIS': 'Schlumberger LIS-79 well logging format',
    'LISt': 'Schlumberger LIS-79 well logging format with TIF markers',
    'LIStr': 'Schlumberger LIS-79 well logging format with reversed TIF markers',
    'LAS1.2': 'Canadian Well Logging Society Log ASCII Standard version 1.2',
    'LAS2.0': 'Canadian Well Logging Society Log ASCII Standard version 2.0',
    'LAS3.0': 'Canadian Well Logging Society Log ASCII Standard version 3.0',
    'RP66V1': 'American Petroleum Institute Recommended Practice 66 version 1',
    'RP66V1t': 'American Petroleum Institute Recommended Practice 66 version 1 with TIF markers',
    'RP66V1tr': 'American Petroleum Institute Recommended Practice 66 version 1 with reversed TIF markers',
    'RP66V2': 'American Petroleum Institute Recommended Practice 66 version 2',
    'ASCII': 'American Standard Code for Information Interchange',
}

assert set(BINARY_FILE_TYPE_DESCRIPTIONS.keys()) == BINARY_FILE_TYPES_SUPPORTED, \
    f'{set(BINARY_FILE_TYPE_DESCRIPTIONS.keys())} != {BINARY_FILE_TYPES_SUPPORTED}'


def summary_file_types_supported(short: bool) -> str:
    """Returns a string of the supported file types. If short is False this is a multi-line string."""
    if short:
        return ", ".join(sorted(BINARY_FILE_TYPES_SUPPORTED))
    width = max(len(v) for v in BINARY_FILE_TYPE_DESCRIPTIONS.keys())
    lst = []
    for b in sorted(BINARY_FILE_TYPE_DESCRIPTIONS.keys()):
        lst.append(f'{b:{width}} - {BINARY_FILE_TYPE_DESCRIPTIONS[b]}')
    return '\n'.join(lst)


def binary_file_type(fobj: typing.BinaryIO) -> str:
    """Function that takes a file object that supports read() and seek() and returns a file type based on the
    analysis of the contents of the file.
    On success fobj will be at the start of file. On failure fobj will be in an indeterminate state.
    """
    result = ''
    for fn, typ in FUNCTION_ID_MAP:
        if fn(fobj) == 0:
            result = typ
            break
    fobj.seek(0)
    return result


def binary_file_type_from_path(path: str) -> str:
    with open(path, 'rb') as file_object:
        return binary_file_type(file_object)


def xxd(by: bytes) -> str:
    """Returns an xxd style string of the bytes. For example:
    0084 8000 8400 2647 3546 3239 2020 2020 2020 ......&G5F29     """
    hex_list = []
    chr_list = []
    for i in range(len(by)):
        if by[i] in ASCII_VISUAL_BYTES:
            chr_list.append(chr(by[i]))
        else:
            chr_list.append('.')
        if i and i % 2 == 0:
            hex_list.append(' ')
        hex_list.append('{:02x}'.format(by[i]))
    return ''.join(hex_list) + ' ' + ''.join(chr_list)


def xxd_size(len_bytes: int) -> int:
    """Returns the length of an xxd style string given the number of bytes."""
    # Size for B bytes is 2*B + (B//2  -1) + 1 + B
    ret = 2 * len_bytes + 1 + len_bytes
    if len_bytes > 2:
        ret += len_bytes // 2 - 1
    return ret


def format_bytes(by: bytes) -> str:
    return f'{xxd(by):{xxd_size(len(by))}s}'
