"""
Identifies the type of file as a string such as "PDF", "RP66V1" by an analysis (mostly) of the
initial bytes of the file.
"""
import io
import re
import string
import struct
import typing

from TotalDepth.DAT import DAT_parser
from TotalDepth.LIS import ExceptionTotalDepthLIS
from TotalDepth.LIS.core import File, FileIndexer
from TotalDepth.util import SEGY


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


def _las(fobj: typing.BinaryIO, version_prefix: bytes) -> str:
    """Returns non-empty string if this is a LAS file of specified version(s), empty string otherwise."""
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
        return ''
    if not lines[0].startswith(b'~V'):
        return ''
    m = RE_LAS_VERSION_LINE.match(lines[1])
    if m is None:
        return ''
    if not m.group(1).startswith(version_prefix):
        return ''
    return f'LAS{version_prefix.decode("ascii")}'


def _lasv12(fobj: typing.BinaryIO) -> str:
    return _las(fobj, b'1.2')


def _lasv20(fobj: typing.BinaryIO) -> str:
    return _las(fobj, b'2.0')


def _lasv30(fobj: typing.BinaryIO) -> str:
    return _las(fobj, b'3.0')


def _lis(fobj: typing.BinaryIO) -> str:
    """This is a LIS file if we can create an index."""
    fobj.seek(0)
    try:
        lis_file = File.FileRead(fobj, theFileId='', keepGoing=False)
        # tif = lis_file._prh.tif.hasTif
        lis_index = FileIndexer.FileIndex(lis_file)
        if len(lis_index):
            if lis_file._prh.tif.hasTif:
                if lis_file._prh.tif.isReversed:
                    return 'LIStr'
                else:
                    return 'LISt'
            else:
                return 'LIS'
        else:
            return ''
    except ExceptionTotalDepthLIS as err:
        return ''


TIF_LEN_REQUIRED_BYTES = 3 * 4


def _tif_third_word_normal(by: bytes) -> bool:
    """Return True if the third word in the TIF marker is normal (little endian) else False if reversed."""
    assert len(by) >= TIF_LEN_REQUIRED_BYTES, \
        f'_tif_third_word_normal(): needs at least {TIF_LEN_REQUIRED_BYTES} bytes not {len(by):d}'
    # Try the third word for being reversed
    third_word = by[8:TIF_LEN_REQUIRED_BYTES]
    if struct.unpack_from('<I', third_word)[0] > 0xffff:
        return False
    return True


def _tif_initial(by: bytes) -> str:
    """Basic file with TIF markers correctly written.
    Checks 12 bytes exactly so 2^64.
    """
    assert len(by) >= TIF_LEN_REQUIRED_BYTES, \
        f'_tif_initial(): needs at least {TIF_LEN_REQUIRED_BYTES} bytes not {len(by):d}'
    if by[:4] != b'\x00\x00\x00\x00':
        return 0
    if by[4:8] != b'\x00\x00\x00\x00':
        # TIF previous
        return ''
    return 'TIF' if _tif_third_word_normal(by) else 'TIFr'


def _rp66v1_bytes(by: bytes) -> str:
    if len(by) < 80:
        return ''
    # RP66V2 Storage Unit Label (SUL) section 2.3.2
    if not RE_COMPILED['RP66V1']['Comment_1'].match(by[:4]):
        return ''
    if not RE_COMPILED['RP66V1']['Comment_2'].match(by[4:9]):
        return ''
    if not RE_COMPILED['RP66V1']['Comment_3'].match(by[9:15]):
        return ''
    if not RE_COMPILED['RP66V1']['Comment_4'].match(by[15:20]):
        return ''
    if len(by[20:80]) != 60:
        return ''
    for c in by[20:80]:
        if c not in ASCII_PRINTABLE_BYTES:
            return ''
    return 'RP66V1'


def _rp66v1(fobj: typing.BinaryIO) -> str:
    fobj.seek(0)
    by: bytes = fobj.read(80)
    return _rp66v1_bytes(by)


RP66V1_LEN_WITH_TIFF = TIF_LEN_REQUIRED_BYTES + 80


def _rp66v1_tif_general(by: bytes, tif_next: int) -> str:
    """RP66V1 with TIF markers correctly written (little endian)."""
    tif_suffix = _tif_initial(by)
    # First record must be the Storage Unit Label which is 80 bytes long. No padding.
    # 80 + 12 is 0x5c
    if tif_next != RP66V1_LEN_WITH_TIFF:
        return ''
    rp66 = _rp66v1_bytes(by[12:])
    if rp66 != '':
        if tif_suffix:
            if tif_suffix == 'TIF':
                return f'{rp66}t'
            elif tif_suffix == 'TIFr':
                return f'{rp66}tr'
            else:
                assert 0, f'Unknown TIF suffix {tif_suffix}'
        else:
            return rp66
    return ''


def _rp66v1_tif(fobj: typing.BinaryIO) -> str:
    """RP66V1 with TIF markers correctly written (little endian)."""
    fobj.seek(0)
    by = fobj.read(RP66V1_LEN_WITH_TIFF)
    if len(by) < RP66V1_LEN_WITH_TIFF:
        return ''
    # TIF next, little endian
    tif_next = 0
    for i in range(0, 4):
        tif_next += by[i + 8] << i
    return _rp66v1_tif_general(by, tif_next)


def _rp66v1_tif_r(fobj: typing.BinaryIO) -> str:
    """RP66V1 with TIF markers reversed (big endian)."""
    fobj.seek(0)
    by = fobj.read(RP66V1_LEN_WITH_TIFF)
    if len(by) < RP66V1_LEN_WITH_TIFF:
        return ''
    # TIF next, big endian
    tif_next = 0
    for i in range(0, 4):
        tif_next <<= i
        tif_next += by[i + 8]
    return _rp66v1_tif_general(by, tif_next)


def _rp66v2(fobj: typing.BinaryIO) -> str:
    fobj.seek(0)
    by = fobj.read(128)
    if len(by) < 128:
        return ''
    # TODO: Test this
    # RP66v2 Part 3 Section 6 "Storage Unit Label Contents" table 3-1
    if not RE_COMPILED['RP66V2']['Comment_1'].match(by[:4]):
        return ''
    if not RE_COMPILED['RP66V2']['Comment_2'].match(by[4:9]):
        return ''
    if not RE_COMPILED['RP66V2']['Comment_3'].match(by[9:15]):
        return ''
    if not RE_COMPILED['RP66V2']['Comment_4'].match(by[15:19]):
        return ''
    if not RE_COMPILED['RP66V2']['Comment_5'].match(by[19:29]):
        return ''
    if not RE_COMPILED['RP66V2']['Comment_6'].match(by[29:39]):
        return ''
    if not RE_COMPILED['RP66V2']['Comment_7'].match(by[39:50]):
        return ''
    # Serial number field can be anything, 12 bytes
    if by[62:68] != b'      ':
        return ''
    for c in by[68:128]:
        if c not in ASCII_PRINTABLE_BYTES:
            return ''
    return 'RP66V2'


def _lis_ver(fobj: typing.BinaryIO) -> str:
    """Returns 'LISVER' for LIS verification files."""
    # Often has leading '\n'
    for expected_bytes in (b'=LIS VERIFICATION by PETROLOG rev ', b'=LIS VERIFICATION BY PETROLOG REVISION '):
        fobj.seek(0)
        byt = fobj.read(len(expected_bytes) + 16)
        if byt.lstrip()[:len(expected_bytes)] == expected_bytes:
            return 'LISVER'
    return ''


def _ascii(fobj: typing.BinaryIO) -> str:
    """Returns 'ASCII' if all the bytes are ASCII characters 0 to 127, '' otherwise.
    """
    fobj.seek(0)
    if set(fobj.read(256)).issubset(ASCII_BYTES_LOWER_128):#ASCII_PRINTABLE_BYTES):
        return 'ASCII'
    return ''


def _zip(fobj: typing.BinaryIO) -> str:
    """Returns 'ZIP' if the magic number is a ZIP file, '' otherwise.
    See: https://en.wikipedia.org/wiki/Zip_(file_format)#Structure
    504b 0304 or b'PK\x03\x04'
    Four bytes have to be right so 2^32.
    Do not support empty (b'\x50\x4b\x05\x06') or spanned (b'\x50\x4b\x07\x08') files.
    """
    fobj.seek(0)
    if fobj.read(4) == b'\x50\x4b\x03\x04':
        return 'ZIP'
    return ''


def _pdf(fobj: typing.BinaryIO) -> str:
    """Returns 0 if the magic number is a PDF file, non-zero otherwise.
    https://en.wikipedia.org/wiki/PDF#File_structure
    Five bytes have to be right so 2^40
    """
    fobj.seek(0)
    if fobj.read(5) == b'%PDF-':
        return 'PDF'
    return ''


def _ps(fobj: typing.BinaryIO) -> str:
    """Returns 0 if the magic number is a Postscript file, non-zero otherwise.
    Five bytes have to be right so 2^40
    """
    fobj.seek(0)
    if fobj.read(5) == b'%!Ps-':
        return 'PS'
    return ''


def _tiff(fobj: typing.BinaryIO) -> str:
    """Returns 0 if the magic number is a TIFF file, non-zero otherwise.
    From observed files.
    Four bytes have to be right so 2^32
    """
    fobj.seek(0)
    # 4949 2a00 3d00 0000 3e3e 205f 6766 665f 6669 II*.=...>> _gff_fi
    if fobj.read(4) == b'II*\x00':
        return 'TIFF'
    return ''


def _xml(fobj: typing.BinaryIO) -> str:
    """Returns 'XML' if the file is a XML file, '' otherwise."""
    fobj.seek(0)
    if fobj.read(6) == b'<?xml ':
        return 'XML'
    return ''


def _dat(fobj: typing.BinaryIO) -> str:
    """Returns 0 if the file is a DAT file, non-zero otherwise.
    """
    try:
        fobj.seek(0)
        # Bit of a hack to convert a binary file to a text one
        text_file = io.StringIO(fobj.read().decode('ascii'))
    except UnicodeDecodeError:
        return ''
    else:
        if DAT_parser.can_parse_file(text_file):
            return 'DAT'
        return ''


def _segy(fobj: typing.BinaryIO) -> str:
    """Returns 'SEGY if the file is a SEGY otherwise ''."""
    fobj.seek(0)
    if SEGY.is_segy(fobj):
        return 'SEGY'
    return ''


def _jpeg(fobj: typing.BinaryIO) -> str:
    """
    JPEG.
    From https://en.wikipedia.org/wiki/List_of_file_signatures
    """
    signatures = (
        b'\xFF\xD8\xFF\xDB',
        b'\xFF\xD8\xFF\xE0\x00\x10\x4A\x46\x49\x46\x00\x01',
        b'\xFF\xD8\xFF\xEE',
    )
    for sig in signatures:
        fobj.seek(0)
        if fobj.read(len(sig)) == sig:
            return 'JPEG'
    return ''


def _exe(fobj: typing.BinaryIO) -> str:
    """Returns 'EXE' if the magic number is a EXE file, '' otherwise.
    From https://en.wikipedia.org/wiki/List_of_file_signatures
    Two bytes have to be right so 2^16
    """
    fobj.seek(0)
    # 4949 2a00 3d00 0000 3e3e 205f 6766 665f 6669 II*.=...>> _gff_fi
    if fobj.read(2) == b'\x4d\x5a':
        return 'EXE'
    return ''



# Ordered so that more specific files are earlier in the list, more general ones later.
# Also, as an optimisation, the more common file formats appear earlier.
FUNCTION_ID_MAP: typing.Tuple[typing.Tuple[typing.Callable, str], ...] = (
    (_xml, 'XML'),  # '<?xml ', 6 characters so 2^(6*8) 2^48
    (_pdf, 'PDF'),  # 2^40
    (_ps, 'PS'),  # 2^40
    (_zip, 'ZIP'),  # 2^32
    (_tiff, 'TIFF'),  # 2^32
    (_jpeg, 'JPEG'),  # 2^32
    (_lasv12, 'LAS1.2'),
    (_lasv20, 'LAS2.0'),
    (_lasv30, 'LAS3.0'),
    (_rp66v1, 'RP66V1'),
    (_rp66v1_tif, 'RP66V1t'),
    (_rp66v1_tif_r, 'RP66V1tr'),
    (_rp66v2, 'RP66V2'),
    (_dat, 'DAT'), # Strong, but slow. Needs to be before ASCII as it is a specialisation of ASCII.
    (_segy, 'SEGY'),  # 3200 EBCDIC characters.
    (_lis_ver, 'LISVER'), # Highly specific first line.
    (_ascii, 'ASCII'),
    (_lis, 'LISt'),
    (_lis, 'LIStr'),
    (_lis, 'LIS'),  # LIS. This attempts to create a LIS Index. This is strong but slow.
)
BINARY_FILE_TYPE_CODE_WIDTH: int = max(len(v[1]) for v in FUNCTION_ID_MAP)
BINARY_FILE_TYPES_SUPPORTED: typing.Set[str] = {v[1] for v in FUNCTION_ID_MAP}


BINARY_FILE_TYPE_DESCRIPTIONS: typing.Dict[str, str] = {
    'XML': 'eXtensible Markup Language',
    'PDF': 'Portable Document Format',
    'PS': 'Postscript',
    'ZIP': 'ZIP Compressed Archive',
    'TIFF': 'Tagged Image File Format',
    'JPEG': 'Joint Photographic Expert Group File Format',
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
    'DAT': 'Simple data format.',
    'LISVER': 'LIS Verification file.',
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
        result = fn(fobj)
        assert isinstance(result, str), f'result of {fn} is {result!r}'
        if result:
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
