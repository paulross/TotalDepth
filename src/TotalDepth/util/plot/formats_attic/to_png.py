"""
Note on patterns in XML file in: ``formats_attic/IWWPatterns.xml``

There are elements thus::

    <Bits>/+7/7v/u/+7/7gAA7/7v/u/+7/7v/gAA</Bits>
    <PatternHeight>12</PatternHeight>
    <PatternWidth>15</PatternWidth>

Frequency analysis shows that the characters used are '+', '/', A-Z, a-z, 0-9
so this looks like base64 encoded. Length is always 32 chars (256 bits).
Pattern size suggests 12*15=180 bits.

Examples::

    >>> base64.b64decode(b'/+7/7v/u/+7/7gAA7/7v/u/+7/7v/gAA')
    b'\xff\xee\xff\xee\xff\xee\xff\xee\xff\xee\x00\x00\xef\xfe\xef\xfe\xef\xfe\xef\xfe\xef\xfe\x00\x00'

    <Description>Coal-LigNite</Description>
    >>> base64.b64decode(b'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    <Description>Void</Description>
    >>> base64.b64decode(b'//7//v/+//7//v/+//7//v/+//7//v/+')
    b'\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xff\xfe'

    >>> base64.b64decode(b'2Hzfkrnudnzvst3O2n67gmZ83Z7V5iYa')
    b'\xd8|\xdf\x92\xb9\xeev|\xef\xb2\xdd\xce\xda~\xbb\x82f|\xdd\x9e\xd5\xe6&\x1a'

Length is always 24 bytes (192 bits) 12x(15+1) where each row 15 bits plus a clear bit (why?)

Examples:

=================Chalk==================
111111111110111
111111111110111
111111111110111
111111111110111
111111111110111
100000111000001
111011111111111
111011111111111
111011111111111
111011111111111
111011111111111
100000111000001
========================================

================Dolomite================
111111110111111
111111101111111
111111011111111
000000000000000
111111111111101
111111111111011
111111111110111
000000000000000
111011111111111
110111111111111
101111111111111
000000000000000
========================================

=================Gypsum=================
011111011111111
101110111111111
110101110111110
111011111011101
111111111101011
111111111110111
011111011111111
101110111111111
110101110111110
111011111011101
111111111101011
111111111110111
========================================

=================Halite=================
111111111111111
111111111101111
110111111101111
110111111101111
110111111100001
110000111111111
111111111111111
111111111101111
110111111101111
110111111101111
110111111100001
110000111111111
========================================

===============LimeStone================
111111111110111
111111111110111
111111111110111
111111111110111
111111111110111
000000000000000
111011111111111
111011111111111
111011111111111
111011111111111
111011111111111
000000000000000
========================================


DataURIScheme: https://en.wikipedia.org/wiki/Data_URI_scheme

Also see this for a similar idea: https://davenquinn.com/projects/geologic-patterns/
Source: https://github.com/davenquinn/geologic-patterns

Also: http://web.mit.edu/12.001/Archive2010/Lab%208/Rock_type_symbols.pdf

"""
import base64
import io
import logging
import os
import sys
import typing
import xml.etree.ElementTree as et

from PIL import Image

logger = logging.getLogger(__file__)

SCHEMA = '{x-schema:LgSchema2.xml}'

EXPECTED_PATTERN_HEIGHT = 12
EXPECTED_PATTERN_WIDTH = 15


def pattern_to_array(width: int, pattern: str) -> typing.List[typing.List[int]]:
    """Takes a width and a base64 encoded pattern and returns a list of list of 0/1 values.

    For example with width 15 and b'x+677qvuu+7H7gAA78bvuu+q77rvxgAA' this returns::

        [
            [1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1],
            [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1],
            ...
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
    """
    b = base64.b64decode(pattern)
    st = ''.join(['{:08b}'.format(v) for v in b])
    # TODO: Check bit 16 is always '0' in each row
    text_table = [st[i:i+width] for i in range(0, len(st), width+1)]
    int_table = [[int(v) for v in row] for row in text_table]
    return int_table


def pattern_to_str(width: int, pattern: str) -> str:
    """Takes a width and a base64 encoded pattern and returns a string representation."""
    int_table = pattern_to_array(width, pattern)
    rows = []
    for int_row in int_table:
        rows.append(''.join(str(i) for i in int_row))
    return '\n'.join(rows)


def _text(val):
    return '{}{}'.format(SCHEMA, val)


def parse_iwwpatterns_xml():
    """Reads the IWWPatterns.xml file and returns the root element."""
    tree = et.parse(os.path.join(os.path.dirname(__file__), 'IWWPatterns.xml'))
    root = tree.getroot()
    if root.tag != _text('LgPatternTable'):
        raise IOError('Pattern XML file root element "{}" is unknown.'.format(root.tag))
    return root


class Pattern(typing.NamedTuple):
    """Holds data about the pattern."""
    unique_id: str
    width: int
    height: int
    background: str
    array: typing.List[typing.List[int]]

    def _assert_invariants(self):
        assert len(self.array) == self.height, f'len(self.array) {len(self.array)} != self.height {self.height}'
        set_widths = set([len(row) for row in self.array])
        assert len(set_widths) == 1, f'Widths should be unique not {set_widths}'
        assert set_widths.pop() == self.width, f'Unique widths != {self.width}'
        assert len(self.background) == 6, 'Background wrong length at "{}"'.format(self.background)

    def __str__(self) -> str:
        self._assert_invariants()
        rows= []
        for int_row in self.array:
            rows.append(''.join(str(i) for i in int_row))
        return f'{self.unique_id}:\n' + '\n'.join(rows)

    def png_image(self, background: str = '') -> bytes:
        """Returns a PNG image,  given background can override native one."""
        self._assert_invariants()
        if background == '':
            background = self.background
        data = bytearray.fromhex(background * (self.width * self.height))
        for r in range(len(self.array)):
            for c in range(len(self.array[r])):
                if self.array[r][c] == 0:
                    offset = r * self.width + c
                    for i in range(3):
                        data[offset * 3 + i] = 0x00
        img = Image.frombytes(mode='RGB', size=(self.width, self.height), data=bytes(data))
        fp = io.BytesIO()
        img.save(fp, 'PNG')
        return fp.getvalue()


def read_iwwpatterns() -> typing.Dict[str, Pattern]:
    """Read IWWPatterns.xml and return a dict of patterns."""
    result = {}
    ids = set()
    root = parse_iwwpatterns_xml()
    for pattern in root.findall(_text('LgFillPattern')):
        # Typical. Note BackgroundColor is optional
        #
        # <LgFillPattern UniqueId="FillPattern3">
        #     <BackgroundColor>00FFFF</BackgroundColor>
        #     <Description>LimeStone</Description>
        #     <Number>3</Number>
        #     <LgBitPattern UniqueId="BitPattern3">
        #         <Bits>/+7/7v/u/+7/7gAA7/7v/u/+7/7v/gAA</Bits>
        #         <PatternHeight>12</PatternHeight>
        #         <PatternWidth>15</PatternWidth>
        #     </LgBitPattern>
        # </LgFillPattern>
        bc_node = pattern.find(_text('BackgroundColor'))
        if bc_node is None:
            bc = 'FFFFFF'
        else:
            bc = bc_node.text
        desc_node = pattern.find(_text('Description'))
        description = desc_node.text
        # Ignore duplicates such as "Calcareous and dolomitic Clay-Shale"
        if description not in result:
            unique_id = pattern.get('UniqueId')
            if unique_id in ids:
                raise IOError('Duplicate unique ID: "{}"'.format(unique_id))
            ids.add(unique_id)
            bit_pattern = pattern.find(_text('LgBitPattern'))
            encoded_bits = bit_pattern.find(_text('Bits')).text
            height = int(bit_pattern.find(_text('PatternHeight')).text)
            width = int(bit_pattern.find(_text('PatternWidth')).text)
            array = pattern_to_array(width, encoded_bits)
            result[description] = Pattern(unique_id, width, height, bc, array)
        else:
            logger.warning(f'IWWPatterns.xml Duplicate ID "{description}"')
    return result


def png_to_data_uri(png: bytes) -> str:
    """Encodes a PNG binary image as a Data URI string.
    https://en.wikipedia.org/wiki/Data_URI_scheme.
    """
    b64 = base64.b64encode(png)
    return '{}{}'.format('data:image/png;base64,', b64.decode())


def create_png_images():
    """Write out patterns as PNG to directories and print out URI SCHEME dicts to go into AREACfg.py"""
    patterns = read_iwwpatterns()
    print('PNG file data')
    data_uri_schemes = {}
    for sub_dir in ('mono', 'rgb'):
        directory = os.path.join(os.path.dirname(__file__), 'PNG', sub_dir)
        os.makedirs(directory, exist_ok=True)
        for name in patterns:
            if sub_dir == 'mono':
                png = patterns[name].png_image('FFFFFF')
            else:
                png = patterns[name].png_image()
            with open(os.path.join(directory, name + '.png'), 'wb') as f:
                f.write(png)
            data_uri_schemes[name] = png_to_data_uri(png)
        key_width = max([len(repr(k)) for k in data_uri_schemes.keys()])
        # Dump to stdout to paste into Python code
        print(directory)
        print('{}: typing.Dict[str, str] = {}'. format('AREA_DATA_URI_SCHEME_' + sub_dir.upper(), '{'))
        for k in sorted(data_uri_schemes.keys()):
            print('    {!r:{width}s} : {!r:s},'.format(k, data_uri_schemes[k], width=key_width))
        print('}')
    # Unique ID
    unique_ids = {k : v[0] for k, v in patterns.items()}
    key_width = max([len(repr(k)) for k in unique_ids.keys()])
    # Dump to stdout to paste into Python code
    print('# IDs')
    print('{}: typing.Dict[str, str] = {}'.format('PATTERN_IDS', '{'))
    for k in sorted(data_uri_schemes.keys()):
        print('    {!r:{width}s} : {!r:s},'.format(k, unique_ids[k], width=key_width))
    print('}')


def main():
    create_png_images()
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
