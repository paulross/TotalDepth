"""
Extract summary data from archives of log files.
"""
import argparse
import datetime
import os
import pprint
import re
import string
import sys
import time
import typing
import zipfile


RE_COMPILED = {
    'RP66V1' : {
        'Comment_1' : re.compile(b'^[0 ]*([1-9]+)$'),
        'Comment_2' : re.compile(b'^V1.(\\d\\d)$'),
        'Comment_3' : re.compile(b'^RECORD$'),
        'Comment_4' : re.compile(b'^[0 ]*([1-9]+)$'),
    },
    'RP66V2' : {
        # See RP66v2 Part 3 Section 6 "Storage Unit Label Contents" table 3-1
        # First three fields are the same as RP66V2
        'Comment_1' : re.compile(b'^[0 ]*([1-9]+)$'), # 4 bytes
        'Comment_2' : re.compile(b'^V1.(\\d\\d)$'), # 5 bytes
        'Comment_3' : re.compile(b'^RECORD$'), # 6 bytes
        'Comment_4' : re.compile(b'^B([1-9]+)[ ]*$'), # 4 bytes
        'Comment_5' : re.compile(b'^[ ]*[1-9]+$'), # 10 bytes
        'Comment_6' : re.compile(b'^[ ]*([1-9]+)?$'), # 10 bytes
        'Comment_7' : re.compile(b'^\\d\\d-[A-Z]{3}-\\d\\d\\d\\d$'), # 11 bytes
        # 'Comment_8' : re.compile(b''), # 12 bytes
        'Comment_9' : re.compile(b'^      $'), # 6 bytes
        # 'Comment_10' : re.compile(b'      '), # 60 bytes
    }
}

# string.printable contains tab, backspace etc. which is undesirable:
# '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c'
PRINTABLE_ASCII_BYTES = set(
    # bytes(string.digits + string.ascii_letters + string.punctuation + ' \n\x0d\x0a', 'ascii')
    bytes(string.printable, 'ascii')
)


VISUAL_ASCII_BYTES = set(
    bytes(string.digits + string.ascii_letters + string.punctuation + ' ', 'ascii')
)


def _las(by: bytes, versions: typing.Tuple[bytes, ...]) -> int:
    """Returns zero if this is a LAS file of specified version(s), non-zero otherwise."""
    lines = []
    for line in by.split(b'\n'):
        comment_idx = line.find(b'#')
        if comment_idx != -1:
            line = line[:comment_idx]
        line = line.strip()
        if len(line) > 0:
            lines.append(line)
    # ~Version Information
    if lines[0] not in (
            b'~V',
            b'~Version',
            b'~Version Information',
            b'~Version Information Section',
            B'~VERSION',
            B'~VERSION INFORMATION',
            B'~VERSION INFORMATION SECTION',
    ):
        return 1
    # VERS.                     2.0: CWLS log ASCII Standard Version 2.00
    if len(lines) == 1:
        return 2
    version_fields = lines[1].split()
    if version_fields[0] != b'VERS.':
        return 3
    if len(version_fields) == 1:
        return 4
    if version_fields[1] not in versions:
        return 5
    return 0


def _lasv12(by: bytes) -> int:
    return _las(by, (b'1.2:', b'1.2'))


def _lasv20(by: bytes) -> int:
    return _las(by, (b'2.0:', b'2.0'))


def _lasv30(by: bytes) -> int:
    return _las(by, (b'3.0:', b'3.0'))


def _lis(by: bytes) -> int:
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
    prl_min = 4 + 1 # PRH + one byte of logical data
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


def _lis_tif_initial(by: bytes) -> int:
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
    r = _lis_tif_initial(by) # 2^64
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
    return _lis(by[12:])


def _lis_tif(by: bytes) -> int:
    """Basic LIS with TIF markers correctly written (little endian)."""
    # TIF next, little endian
    assert len(by) >= 12, f'_lis_tif(): needs at least 12 bytes not {len(by):d}'
    tif_next = 0
    for i in range(0, 4):
        tif_next += by[i + 8] << (i * 8)
    return _lis_tif_general(by, tif_next)


def _lis_tif_r(by: bytes) -> int:
    """Basic LIS with TIF markers reversed (big endian)."""
    assert len(by) >= 12, f'_lis_tif(): needs at least 12 bytes not {len(by):d}'
    # TIF next, big endian
    tif_next = 0
    for i in range(0, 4):
        tif_next <<= i * 8
        tif_next += by[i + 8]
    return _lis_tif_general(by, tif_next)


def _rp66v1(by: bytes) -> int:
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
        if c not in PRINTABLE_ASCII_BYTES:
            return 6
    return 0


def _rp66v1_tif_general(by: bytes, tif_next: int) -> int:
    """RP66V1 with TIF markers correctly written (little endian)."""
    r = _lis_tif_initial(by)
    if r:
        return r
    # First record must be the Storage Unit Label which is 80 bytes long. No padding.
    # 80 + 12 is 0x5c
    if tif_next != 80 + 12:
        return 3
    return _rp66v1(by[12:])


def _rp66v1_tif(by: bytes) -> int:
    """RP66V1 with TIF markers correctly written (little endian)."""
    # TIF next, little endian
    tif_next = 0
    for i in range(0, 4):
        tif_next += by[i + 8] << i
    return _rp66v1_tif_general(by, tif_next)


def _rp66v1_tif_r(by: bytes) -> int:
    """RP66V1 with TIF markers reversed (big endian)."""
    # TIF next, big endian
    tif_next = 0
    for i in range(0, 4):
        tif_next <<= i
        tif_next += by[i + 8]
    return _rp66v1_tif_general(by, tif_next)


def _rp66v2(by: bytes) -> int:
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
        if c not in PRINTABLE_ASCII_BYTES:
            return 10
    return 0


def _ascii(by: bytes) -> int:
    """Returns 0 if all the bytes are ASCII printable, non-zero otherwise."""
    if set(by).issubset(PRINTABLE_ASCII_BYTES):
        return 0
    return 1


def _zip(by: bytes) -> int:
    """Returns 0 if the magic number is a ZIP file, non-zero otherwise.
    See: https://en.wikipedia.org/wiki/Zip_(file_format)#Structure
    504b 0304 or b'PK\x03\x04'
    Four bytes have to be right so 2^32.
    Do not support empty (b'\x50\x4b\x05\x06') or spanned (b'\x50\x4b\x07\x08') files.
    """
    if by[:4] == b'\x50\x4b\x03\x04':
        return 0
    return 1


def _pdf(by: bytes) -> int:
    """Returns 0 if the magic number is a PDF file, non-zero otherwise.
    https://en.wikipedia.org/wiki/PDF#File_structure
    Five bytes have to be right so 2^40
    """
    if by[:5] == b'%PDF-':
        return 0
    return 1


# Ordered so that more specific files are earlier in the list, more general ones later.
# Also, as an optimisation, the more common file formats appear earlier.
FUNCTION_ID_MAP = (
    (_pdf, 'PDF'), # 2^40
    (_zip, 'ZIP'), # 2^32
    (_lis_tif, 'LISt'), # Tests with TIF markers are much more strict.
    (_lis_tif_r, 'LIStr'),
    (_lasv12, 'LAS1.2'),
    (_lasv20, 'LAS2.0'),
    (_lasv30, 'LAS3.0'),
    (_rp66v1, 'RP66V1'),
    (_rp66v1_tif, 'RP66V1t'),
    (_rp66v1_tif_r, 'RP66V1tr'),
    (_rp66v2, 'RP66v2'),
    (_ascii, 'ASCII'),
    (_lis,  'LIS'), # LIS without TIF is potentially the weakest test, around 2^11
)

BINARY_FILE_TYPE_CODE_WIDTH = max(len(v[1]) for v in FUNCTION_ID_MAP)


def binary_file_type_from_bytes(by: bytes) -> str:
    """Function that takes a number of bytes and returns a file type
    based on the analysis of the contents of the bytes."""
    result = ''
    for fn, typ in FUNCTION_ID_MAP:
        if fn(by) == 0:
            result = typ #FUNCTION_ID_MAP[fn]
            break
    return result


def binary_file_type(fobj: typing.IO) -> str:
    """Function that takes a file object that supports read() and seek() and returns a file type based on the
    analysis of the contents of the file."""
    # 128 bytes should be enough.
    fobj.seek(0)
    by: bytes = fobj.read(128)
    result = ''
    if len(by) == 128:
        return binary_file_type_from_bytes(by)
    return result


def xxd(by: bytes) -> str:
    """Returns an xxd style string of the bytes. For example:
    0084 8000 8400 2647 3546 3239 2020 2020 2020 ......&G5F29     """
    hex_list = []
    chr_list = []
    for i in range(len(by)):
        if by[i] in VISUAL_ASCII_BYTES:
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


class FileBase:
    """Base class to represent a file, either on-disc or a ZIP file."""
    # Number of bytes to take a file fragment of. 18 is useful for LIS+TIF as it gives
    # all the TIF markers [12], the PRH [4] and the LRH [2].
    XXD_NUM_BYTES = 18
    
    def __init__(self, path: str):
        self.path = path
        self.ext = os.path.splitext(path)[1].upper()
        self.size = 0
        self.bin_type = ''
        self.mod_date = datetime.datetime.min
        self.bytes = b''

    def __str__(self):
        return ' '.join(
            [
                f'{self.size:12,d}'
                f'{self.ext:4s}',
                f'{self.bin_type:{BINARY_FILE_TYPE_CODE_WIDTH}s}',
                f'{self.mod_date}',
                f'{xxd(self.bytes):{xxd_size(self.XXD_NUM_BYTES)}s}',
                f'{self.path}',
            ]
        )
        # return f'{self.size:12,d} {self.ext:4s} {self.bin_type:{BINARY_FILE_TYPE_CODE_WIDTH}s} {self.mod_date} {self.path}'


class FileOnDisc(FileBase):
    """Represents an on-disc file."""
    def __init__(self, path: str):
        super().__init__(path)
        os_stat = os.stat(self.path)
        self.size = os_stat.st_size
        self.mod_date = datetime.datetime(*(time.localtime(os_stat.st_mtime)[:6]))
        with open(self.path, 'rb') as f:
            self.bin_type = binary_file_type(f)
            f.seek(0)
            self.bytes = f.read(self.XXD_NUM_BYTES)


class FileInMemory(FileBase):
    """Represents an in-memory file, for example contained in a ZIP.
    We need to be given the file data as we can't read it from disc."""
    def __init__(self, path: str, size: int, binary_type: str, mod_date: datetime.datetime, by: bytes):
        super().__init__(path)
        self.size = size
        self.bin_type = binary_type
        self.mod_date = mod_date
        self.bytes = by


class FileMembers:
    """Represents a tree of files for example a ZIP might contain a ZIP."""
    def __init__(self):
        self.members: typing.List[typing.Union[FileBase, FileMembers]] = []

    def __str__(self):
        return '\n'.join(str(v) for v in self.members)


class FileArchive(FileOnDisc):
    """Represents an on-disc file that is an archive of other files."""
    def __init__(self, archive_path: str):
        super().__init__(archive_path)
        self.members: FileMembers = FileMembers()


class FileZip(FileArchive):
    """Represents an on-disc file that is a ZIP file."""
    def __init__(self, archive_path: str):
        assert zipfile.is_zipfile(archive_path)
        super().__init__(archive_path)
        assert self.bin_type == 'ZIP'
        # XXD_NUM_BYTES = 18
        with zipfile.ZipFile(archive_path) as z_archive:
            # print()
            # print(f'TRACE: process_zip_path(): Processing ZIP {archive_path}')  # {z_archive.filename}')
            for z_info in z_archive.infolist():
                if z_info.is_dir():
                    # print(f'{str():{xxd_size(XXD_NUM_BYTES)}s} {0:12,d} {"DIR":8s} {z_info.filename}')
                    self.members.members.append(
                        FileInMemory(z_info.filename, 0, 'DIR', datetime.datetime(*z_info.date_time), b'')
                    )
                else:
                    with z_archive.open(z_info) as z_member_file:
                        bin_file_type = binary_file_type(z_member_file)
                        # by: bytes = z_member_file.read(XXD_NUM_BYTES)
                        # print(
                        #     f'{xxd(by):{xxd_size(XXD_NUM_BYTES)}s} {z_info.file_size:12,d}'
                        #     f' {bin_file_type:8s} {z_info.filename}'
                        # )
                        z_member_file.seek(0)
                        by = z_member_file.read(self.XXD_NUM_BYTES)
                        self.members.members.append(
                            FileInMemory(z_info.filename, z_info.file_size, bin_file_type, datetime.datetime(*z_info.date_time), by)
                        )

    def __str__(self):
        str_self = f'{self.size:12,d} {self.ext:4s} {self.bin_type:{BINARY_FILE_TYPE_CODE_WIDTH}s} {self.mod_date} {self.path}'
        return '{}\n{}'.format(str_self, str(self.members))


EXCLUDE_FILENAMES = ('.DS_Store',)


def _process_file(dir_name: str, file_name: str, result: typing.List[FileBase]) -> None:
    if file_name not in EXCLUDE_FILENAMES:
        path = os.path.join(dir_name, file_name)
        if os.path.isfile(path):
            # If this is a ZIP archive then open it a process the contents.
            if zipfile.is_zipfile(path):
                # result.extend(process_zip_path(path))
                result.append(FileZip(path))
            else:
                result.append(FileOnDisc(path))


def main() -> int:
    parser = argparse.ArgumentParser(description="""Summary analysis an archive of Log data.""")
    parser.add_argument('path', help='Path to the archive.')
    parser.add_argument('-r', '--recurse', help='Recurse into the path.', action='store_true')
    args = parser.parse_args()
    print(args)

    result: typing.List[FileBase] = []
    assert os.path.isdir(args.path)
    if args.recurse:
        for root, dirs, files in os.walk(args.path):
            for file in files:
                _process_file(root, file, result)
    else:
        for file_name in sorted(os.listdir(args.path)):
            _process_file(args.path, file_name, result)
    # pprint.pprint([str(v) for v in result])
    # pprint.pprint(result)
    for r in result:
        # print(type(r), r)
        print(r)
    # Output summary


    return 0


if __name__ == '__main__':
    sys.exit(main())
