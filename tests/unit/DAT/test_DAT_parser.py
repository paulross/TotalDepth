import datetime
import io

import pytest

from TotalDepth.DAT import DAT_parser

EXAMPLE_DAT_FILE = """UTIM Unix Time sec
DATE Date ddmmyy
TIME Time hhmmss
WAC Wits Activity Code unitless
BDIA Bit Diameter inch
DBTM Bit Measured Depth m
DBTV Bit Vertical Depth m
DMEA Hole Measured Depth m
DVER Hole Vertical Depth m
RSU Pulling Speed m/sec
RSD Running Speed m/sec
SWAB Swab Pressure Gradient g/cc
SURG Surge Pressure Gradient g/cc
ROP ROP m/hr
BPOS Block Position m
HKL Hookload tons
WOB Weight on Bit tons
TRQ Torque kNm
RPMA String RPM rpm
RPMB Bit RPM rpm
BROT Rotation Time hr
BDTI Bit Drilled Time hr
TBR Total Bit Revolutions unitless
SPP Pump Pressure bar
COPP Completion Pump Pressure bar
CEPP Cement Pump Pressure bar
WHP Wellhead Pressure bar
KLP Kill Line Pressure bar
CHP Choke Line Pressure bar
HVMX Heave m
CCVL Cement Volume Pumped m3
CFO Flow Out l/min
CFI Flow In l/min
CDI Fluid Density In g/cc
CDO Fluid Density Out g/cc
CTVL Total Volume Pumped m3
TVA Tank Volume Active m3
TPVT Trip Pits Volume Total m3
ETPT Expected Trip Pits Volume Total m3
MFO Mud Flow Out l/min
MFI Mud Flow In l/min
MDO Mud Density Out g/cc
MDI Mud Density In g/cc
MTO Mud Temp Out degC
MTI Mud Temp In degC
ECDB Eff Circ Density at Bit g/cc
ECDT ECD at TD g/cc
ECDC ECD at Casing Shoe g/cc
ECDW ECD at Weakest Depth g/cc
ECDM ECD from MWD g/cc
GAS Total Gas %
METH Methane ppm
ETH Ethane ppm
PRP Propane ppm
IBUT iso-Butane ppm
NBUT n-Butane ppm
IPEN iso-Pentane ppm
NPEN n-Pentane ppm
EPEN Neo-Pentane ppm
UTIM DATE TIME WAC BDIA DBTM DBTV DMEA DVER RSU RSD SWAB SURG ROP BPOS HKL WOB TRQ RPMA RPMB BROT BDTI TBR SPP COPP CEPP WHP KLP CHP HVMX CCVL CFO CFI CDI CDO CTVL TVA TPVT ETPT MFO MFI MDO MDI MTO MTI ECDB ECDT ECDC ECDW ECDM GAS METH ETH PRP IBUT NBUT IPEN NPEN EPEN 
1165665017 09Dec06 11-50-17 0 8.50 10.00 10.00 3131.07 3036.55 0.11 0.00 1.20 0.00 3.02 1.15 33.26 0.00 0.00 -0 0 222036.00 0.00 269999 0.7 0.0 0.0 0.0 0.0 0.0 0.00 0.0 0.0 0.0 0.0 0.0 0.0 14.70 0.35 0.00 7.7035 0.0000 1.20 1.20 30.2 22.7 1.1976 1.1976 1.1976 1.1976 0.0000 0.000 11 0 0 0 0 0 0 0 
1165665022 09Dec06 11-50-22 0 8.50 10.00 10.00 3131.07 3036.55 0.11 0.00 1.20 0.00 3.02 1.15 33.26 0.00 0.00 -0 0 222036.00 0.00 269999 0.7 0.0 0.0 0.0 0.0 0.0 0.00 0.0 0.0 0.0 0.0 0.0 0.0 14.70 0.35 0.00 7.7035 0.0000 1.20 1.20 30.2 22.7 1.1976 1.1976 1.1976 1.1976 0.0000 0.000 11 0 0 0 0 0 0 0 
1165665027 09Dec06 11-50-27 0 8.50 10.00 10.00 3131.07 3036.55 0.11 0.00 1.20 0.00 3.02 1.15 29.59 0.00 0.00 -0 0 222036.00 0.00 269999 0.7 0.0 0.0 0.0 0.0 0.0 0.00 0.0 0.0 0.0 0.0 0.0 0.0 14.70 0.35 0.00 8.1098 0.0000 1.20 1.20 31.1 25.3 1.1976 1.1976 1.1976 1.1976 0.0000 0.000 11 0 0 0 0 0 0 0 
1165665032 09Dec06 11-50-32 0 8.50 10.00 10.00 3131.07 3036.55 0.11 0.00 1.20 0.00 3.02 1.15 26.85 0.00 0.00 -0 0 222036.00 0.00 269999 0.7 0.0 0.0 0.0 0.0 0.0 0.00 0.0 0.0 0.0 0.0 0.0 0.0 14.70 0.35 0.00 7.3556 0.0000 1.20 1.20 31.2 25.3 1.1976 1.1976 1.1976 1.1976 0.0000 0.000 11 0 0 0 0 0 0 0 
1165665037 09Dec06 11-50-37 0 8.50 10.00 10.00 3131.07 3036.55 0.11 0.00 1.20 0.00 3.02 1.15 28.73 0.00 0.00 -0 0 222036.00 0.00 269999 0.7 0.0 0.0 0.0 0.0 0.0 0.00 0.0 0.0 0.0 0.0 0.0 0.0 14.70 0.35 0.00 7.6572 0.0000 1.20 1.20 31.1 25.3 1.1976 1.1976 1.1976 1.1976 0.0000 0.000 11 0 0 0 0 0 0 0 
1165665042 09Dec06 11-50-42 0 8.50 10.00 10.00 3131.07 3036.55 0.11 0.00 1.20 0.00 3.02 1.15 29.60 0.00 0.00 -0 0 222036.00 0.00 269999 0.7 0.0 0.0 0.0 0.0 0.0 0.00 0.0 0.0 0.0 0.0 0.0 0.0 14.70 0.35 0.00 8.0246 0.0000 1.20 1.20 31.1 25.3 1.1976 1.1976 1.1976 1.1976 0.0000 0.000 11 0 0 0 0 0 0 0 
1165665047 09Dec06 11-50-47 0 8.50 10.00 10.00 3131.07 3036.55 0.11 0.00 1.20 0.00 3.02 1.15 29.60 0.00 0.00 -0 0 222036.00 0.00 269999 0.7 0.0 0.0 0.0 0.0 0.0 0.00 0.0 0.0 0.0 0.0 0.0 0.0 14.70 0.35 0.00 7.6314 0.0000 1.20 1.20 31.1 25.3 1.1976 1.1976 1.1976 1.1976 0.0000 0.000 11 0 0 0 0 0 0 0 
1165665052 09Dec06 11-50-52 0 8.50 10.00 10.00 3131.07 3036.55 0.11 0.00 1.20 0.00 3.02 1.15 29.60 0.00 0.00 -0 0 222036.00 0.00 269999 0.7 0.0 0.0 0.0 0.0 0.0 0.00 0.0 0.0 0.0 0.0 0.0 0.0 14.70 0.35 0.00 8.7576 0.0000 1.20 1.20 31.1 25.1 1.1976 1.1976 1.1976 1.1976 0.0000 0.000 11 0 0 0 0 0 0 0 
"""


@pytest.mark.parametrize(
    'value, expected',
    (
        ('1165665017', datetime.datetime(2006, 12, 9, 11, 50, 17)),
        ('1165665020', datetime.datetime(2006, 12, 9, 11, 50, 20)),
        ('1165665027', datetime.datetime(2006, 12, 9, 11, 50, 27)),
    )
)
def test__unit_unix_time_to_datetime_datetime(value, expected):
    result = DAT_parser._unit_unix_time_to_datetime_datetime(value)
    assert result == expected


@pytest.mark.parametrize(
    'value, expected',
    (
            ('-ABC',
             '_unit_unix_time_to_datetime_datetime(): invalid literal for int() with base 10: \'-ABC\' on value "-ABC"',
             ),
    )
)
def test__unit_unix_time_to_datetime_datetime_raises(value, expected):
    with pytest.raises(DAT_parser.ExceptionDATRead) as err:
        DAT_parser._unit_unix_time_to_datetime_datetime(value)
    assert err.value.args[0] == expected


@pytest.mark.parametrize(
    'value, expected',
    (
        ('09Dec06', datetime.date(2006, 12, 9)),
        ('09Dec55', datetime.date(1955, 12, 9)),
        ('09Dec75', datetime.date(1975, 12, 9)),
        ('09Dec50', datetime.date(2050, 12, 9)),
        ('09-Dec-06', datetime.date(2006, 12, 9)),
        ('09-Dec-55', datetime.date(1955, 12, 9)),
        ('09-Dec-75', datetime.date(1975, 12, 9)),
        ('09-Dec-50', datetime.date(2050, 12, 9)),
        # Sigh
        ('9-Oct-11', datetime.date(2011, 10, 9)),
        ('9Oct11', datetime.date(2011, 10, 9)),
        ('9-Oct-1', datetime.date(2001, 10, 9)),
        ('9Oct1', datetime.date(2001, 10, 9)),
        ('9-Oct-01', datetime.date(2001, 10, 9)),
        ('9Oct01', datetime.date(2001, 10, 9)),
        ('09-Oct-01', datetime.date(2001, 10, 9)),
        ('09Oct01', datetime.date(2001, 10, 9)),
    )
)
def test__unit_ddmmyy_to_datetime_date(value, expected):
    result = DAT_parser._unit_ddmmyy_to_datetime_date(value)
    assert result == expected


@pytest.mark.parametrize(
    'value, expected',
    (
        ('32Dec06', '_unit_ddmmyy_to_datetime_date(): day is out of range for month on value "32Dec06"'),
        ('09XXX06', '_unit_ddmmyy_to_datetime_date(): Can not grep value "09XXX06"'),
        ('', '_unit_ddmmyy_to_datetime_date(): Can not grep value ""'),
        ('09', '_unit_ddmmyy_to_datetime_date(): Can not grep value "09"'),
        ('09Dec', '_unit_ddmmyy_to_datetime_date(): Can not grep value "09Dec"'),
    )
)
def test__unit_ddmmyy_to_datetime_date_raises(value, expected):
    with pytest.raises(DAT_parser.ExceptionDATRead) as err:
        DAT_parser._unit_ddmmyy_to_datetime_date(value)
    assert err.value.args[0] == expected


@pytest.mark.parametrize(
    'value, expected',
    (
        ('11-50-17', datetime.time(11, 50, 17)),
    )
)
def test__unit_hhmmyy_to_datetime_time(value, expected):
    result = DAT_parser._unit_hhmmyy_to_datetime_time(value)
    assert result == expected


@pytest.mark.parametrize(
    'value, expected',
    (
        ('115017', '_unit_hhmmyy_to_datetime_time(): time data \'115017\' does not match format \'%H-%M-%S\' on value "115017"'),
    )
)
def test__unit_hhmmyy_to_datetime_time_raises(value, expected):
    with pytest.raises(DAT_parser.ExceptionDATRead) as err:
        DAT_parser._unit_hhmmyy_to_datetime_time(value)
    assert err.value.args[0] == expected


@pytest.mark.parametrize(
    'line, expected',
    (
        ('UTIM Unix Time sec', ('UTIM', 'Unix Time', 'sec')),
        ('UTIM\tUnix Time\tsec', ('UTIM', 'Unix Time', 'sec')),
        ('ECDW ECD at Weakest Depth g/cc', ('ECDW', 'ECD at Weakest Depth', 'g/cc')),
        ('HVMX Heave m', ('HVMX', 'Heave', 'm')),
        ("PIT1 Tank Volume Pit 1 m3", ('PIT1', 'Tank Volume Pit 1', 'm3')),
    )
)
def test_re_channel_definition(line, expected):
    m = DAT_parser.RE_CHANNEL_DEFINITION.match(line)
    assert m is not None
    assert m.groups() == expected


@pytest.mark.parametrize(
    'line',
    (
        'UTIM    DATE    TIME ...',
        'UTIM DATE TIME ...',
        'UTIM\tDATE\tTIME ...',
    )
)
def test_re_data_header_definition_match(line):
    m = DAT_parser.RE_DATA_HEADER_DEFINITION.match(line)
    assert m is not None


@pytest.mark.parametrize(
    'line',
    (
        'UTIM    DAT    TIME ...',
        'UTIM Unix Time sec',
    )
)
def test_re_data_header_definition_no_match(line):
    m = DAT_parser.RE_DATA_HEADER_DEFINITION.match(line)
    assert m is None


def test_parse_example_file():
    file_object = io.StringIO(EXAMPLE_DAT_FILE)
    frame_array = DAT_parser.parse_file(file_object)
    # print(frame_array)
    assert len(frame_array.channels) == 59
    assert len(frame_array.x_axis) == 8


def test_parse_example_file_date_matches():
    file_object = io.StringIO(EXAMPLE_DAT_FILE)
    frame_array = DAT_parser.parse_file(file_object)
    x_axis = frame_array.x_axis
    assert len(x_axis) == 8
    date_column = frame_array[1]
    assert len(date_column) == 8
    for i in range(8):
        assert x_axis[(i, 0)].date() == date_column[(i, 0)]


def test_parse_example_file_time_matches():
    file_object = io.StringIO(EXAMPLE_DAT_FILE)
    frame_array = DAT_parser.parse_file(file_object)
    x_axis = frame_array.x_axis
    assert len(x_axis) == 8
    time_column = frame_array[2]
    assert len(time_column) == 8
    for i in range(8):
        assert x_axis[(i, 0)].time() == time_column[(i, 0)]


def test_parse_example_file_channel_names():
    file_object = io.StringIO(EXAMPLE_DAT_FILE)
    frame_array = DAT_parser.parse_file(file_object)
    channel_names = [c.ident for c in frame_array.channels]
    # print(channel_names)
    expected = ['UTIM', 'DATE', 'TIME', 'WAC', 'BDIA', 'DBTM', 'DBTV', 'DMEA', 'DVER', 'RSU', 'RSD', 'SWAB', 'SURG',
                'ROP', 'BPOS', 'HKL', 'WOB', 'TRQ', 'RPMA', 'RPMB', 'BROT', 'BDTI', 'TBR', 'SPP', 'COPP', 'CEPP', 'WHP',
                'KLP', 'CHP', 'HVMX', 'CCVL', 'CFO', 'CFI', 'CDI', 'CDO', 'CTVL', 'TVA', 'TPVT', 'ETPT', 'MFO', 'MFI',
                'MDO', 'MDI', 'MTO', 'MTI', 'ECDB', 'ECDT', 'ECDC', 'ECDW', 'ECDM', 'GAS', 'METH', 'ETH', 'PRP', 'IBUT',
                'NBUT', 'IPEN', 'NPEN', 'EPEN']
    assert channel_names == expected


@pytest.mark.parametrize(
    'value, expected',
    (
        ('', 'Parsing DAT file results in no channels.'),
        ('asdadf\nasdsa', 'Line: 1: In channel declaration section but no match on "asdadf"'),
        ("""UTIM Unix Time sec
UTIM DATE TIME WAC BDIA DBTM DBTV DMEA DVER RSU RSD SWAB SURG ROP BPOS HKL WOB TRQ RPMA RPMB BROT BDTI TBR SPP COPP CEPP WHP KLP CHP HVMX CCVL CFO CFI CDI CDO CTVL TVA TPVT ETPT MFO MFI MDO MDI MTO MTI ECDB ECDT ECDC ECDW ECDM GAS METH ETH PRP IBUT NBUT IPEN NPEN EPEN
1165665017 09Dec06 11-50-17 0 8.50 10.00 10.00 3131.07 3036.55 0.11 0.00 1.20 0.00 3.02 1.15 33.26 0.00 0.00 -0 0 222036.00 0.00 269999 0.7 0.0 0.0 0.0 0.0 0.0 0.00 0.0 0.0 0.0 0.0 0.0 0.0 14.70 0.35 0.00 7.7035 0.0000 1.20 1.20 30.2 22.7 1.1976 1.1976 1.1976 1.1976 0.0000 0.000 11 0 0 0 0 0 0 0
""", 'Line: 2: channel name DATE not defined in section 1.'),
    )
)
def test_parse_example_file_fails(value, expected):
    file_object = io.StringIO(value)
    with pytest.raises(DAT_parser.ExceptionDATRead) as err:
        DAT_parser.parse_file(file_object)
    assert err.value.args[0] == expected


# File with time/date, two channels, three frames
EXAMPLE_MINIMAL_DAT_FILE = """UTIM Unix Time sec
DATE Date ddmmyy
TIME Time hhmmss
WAC Wits Activity Code unitless
BDIA Bit Diameter inch
UTIM DATE TIME WAC BDIA 
1165665017 09Dec06 11-50-17 0 8.50 
1165665022 09Dec06 11-50-22 1 8.25 
1165665027 09Dec06 11-50-27 2 8.00 
"""


def test_parse_minimal_example_file():
    file_object = io.StringIO(EXAMPLE_MINIMAL_DAT_FILE)
    frame_array = DAT_parser.parse_file(file_object)
    assert len(frame_array) == 5
    assert [len(frame_array[i]) for i in range(len(frame_array))] == [3, 3, 3, 3, 3]


EXAMPLE_MINIMAL_DAT_FILE_WITH_GARBAGE = """UTIM Unix Time sec
DATE \x00Date ddmmyy
TIME Time hhmmss
WAC Wits Activity Code unitless
BDIA Bit \x01Diameter inch
UTIM DATE TIME WAC BDIA 
1165665017 \x02 09Dec06 11-50-17 0 8.50 
1165665022 09Dec06 11-50-22 1 8.25 
1165665027 09Dec06 11-50-27 2 8.00 
"""


def test_parse_minimal_example_file_with_garbage():
    file_object = io.StringIO(EXAMPLE_MINIMAL_DAT_FILE_WITH_GARBAGE)
    frame_array = DAT_parser.parse_file(file_object)
    assert len(frame_array) == 5
    assert [len(frame_array[i]) for i in range(len(frame_array))] == [3, 3, 3, 3, 3]


# File with time/date, missing 'WAC' in data section, three frames
EXAMPLE_MINIMAL_DAT_FILE_MISSING_CHANNEL_DATA = """UTIM Unix Time sec
DATE Date ddmmyy
TIME Time hhmmss
WAC Wits Activity Code unitless
BDIA Bit Diameter inch
UTIM DATE TIME BDIA 
1165665017 09Dec06 11-50-17 8.50 
1165665022 09Dec06 11-50-22 8.25 
1165665027 09Dec06 11-50-27 8.00 
"""


def test_parse_minimal_example_file_missing_channel():
    file_object = io.StringIO(EXAMPLE_MINIMAL_DAT_FILE_MISSING_CHANNEL_DATA)
    frame_array = DAT_parser.parse_file(file_object)
    assert len(frame_array) == 4
    assert [len(frame_array[i]) for i in range(len(frame_array))] == [3, 3, 3, 3]
