#!/usr/bin/env python
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 1999-2011 Paul Ross
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# 
# Paul Ross: apaulross@gmail.com
"""Provides unit conversion for LIS79.

The __RAW_UNIT_MAP is the master map from which all other data is derived.
Its format is as follows:

key - The unit category as four bytes representing uppercase ASCII characters.
value - A tuple of three fields:

* [0] - Descriptive string of the unit category.
* [1] - The base unit name as four bytes representing uppercase ASCII characters.
* [2] - A tuple the contents of which is a four or five item tuple:

    * If four members:
        * [2][0] - The unit name as four bytes representing uppercase ASCII characters.
        * [2][1] - The multiplier as a float.
        * [2][2] - Descriptive string of the units.
        * [2][3] - The unit name that this is an alternate for as four bytes
                representing uppercase ASCII characters, or four spaces.

    * If five members:
        * [2][0] - The unit name as four bytes representing uppercase ASCII characters.
        * [2][1] - The multiplier as a float.
        * [2][2] - The offset as a float.
        * [2][3] - Descriptive string of the units.
        * [2][4] - The unit name that this is an alternate for as four bytes
                representing uppercase ASCII characters or four spaces.
            

The unit name should also be unique.

TODO: Clean up units by making reciprocal e.g. 1/6.0 rather than 0.166666...

TODO: Check each unit for errors.
"""

__author__  = 'Paul Ross'
__date__    = '2010-08-02'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'


#import time
#import sys
#import logging
#import collections
import math

LEN_UNIT_NAME = 4
MT_UNIT = b'    '
assert(len(MT_UNIT) == LEN_UNIT_NAME)

OPTICAL_FEET = b'FEET'
assert(len(OPTICAL_FEET) == LEN_UNIT_NAME)
OPTICAL_METERS = b'M   '
assert(len(OPTICAL_METERS) == LEN_UNIT_NAME)
OPTICAL_TIME = b'S   '
assert(len(OPTICAL_TIME) == LEN_UNIT_NAME)

#: The master table of unit conversions
__RAW_UNIT_MAP = {
    b"LENG" : (
                "Linear length",
                b"M   ",
                (
                    (b"M   ",    1.0,        "Meters",                MT_UNIT),
                    (b"METR",    1.0,        "Meters",                b"M   "),
                    (b"MTRS",    1.0,        "Meters",                b"M   "),
                    (b"MT  ",    1.0,        "Meters",                b"M   "),
                    (b"MET ",    1.0,        "Meters",                b"M   "),
                    (b"DM  ",    0.1,        "Decimeters",            MT_UNIT),
                    (b"CM  ",    0.01,       "Centimeters",           MT_UNIT),
                    (b"MM  ",    0.001,      "Millimeters",           MT_UNIT),
                    (b".5MM",    0.0005,     "Half-millimeters",      MT_UNIT),
                    (b"F   ",    0.3048,     "Feet",                  b"FEET"),
                    (b"FT  ",    0.3048,     "Feet",                  b"FEET"),
                    (b"FEET",    0.3048,     "Feet",                  MT_UNIT),
                    (b"IN  ",    0.0254,     "Inches",                MT_UNIT),
                    (b"INS ",    0.0254,     "Inches",                b"IN  "),
                    (b"INCH",    0.0254,     "Inches",                b"IN  "),
                    (b".1IN",    0.00254,    "Tenth-inches",          MT_UNIT),
                    (b"KM  ",    1000.0,     "Kilometers",            MT_UNIT),
                ),
            ),
            
    b"TIME" : (
                "Time",
                b"S   ",
                (
                    (b"S   ",    1.0,        "Seconds",             MT_UNIT),
                    (b"S/10",    0.1,        "Tenths of a second",  MT_UNIT),
                    (b"US  ",    1.0e-6,     "Microseconds",        MT_UNIT),
                    (b"MS  ",    1.0e-3,     "Milliseconds",        MT_UNIT),
                    (b"MSEC",    1.0e-3,     "Milliseconds",        b"MS  "),
                    (b".5MS",    0.5e-3,     "Half milleseconds",   MT_UNIT),
                    (b"D   ",    86400.0,    "Days",                MT_UNIT),
                    (b"HR  ",    3600.0,     "Hours",               MT_UNIT),
                    (b"MN  ",    60.0,       "Minutes",             MT_UNIT),
                    (b"SECS",    1.0,        "Seconds",             b"S   "),
                ),
            ),
    
    b"TEMP" : (
                "Temperature",
                b"DEGK",
                (
                    (b"DEGK",    1.0,       0.0,                    "Degrees Kelvin",    MT_UNIT),
                    (b"DEGC",    1.0,       -273.15,                "Degrees Centigrade",    MT_UNIT),
                    (b"DEGF",    1/1.80,    -273.15 * 1.80 + 32.0,  "Degrees Farenheit",    MT_UNIT),
                    (b"DEGR",    1/1.80,    0.0,                    "Degrees Rankine",    MT_UNIT),
                ),
            ),
    
    b"VELO" : (
                "Velocity",
                b"M/S ",
                (
                    (b"M/S ",    1.0,               "Meters Per Second",        MT_UNIT),
                    (b"CM/S",    1.00000000e-02,    "Centimeters Per Second",   MT_UNIT),
                    (b"F/HR",    8.46666667e-05,    "Feet Per Hour",            MT_UNIT),
                    (b"FT/H",    8.46666667e-05,    "Feet Per Hour",            b"F/HR"),
                    (b"F/MN",    5.08000000e-03,    "Feet Per Minute",          MT_UNIT),
                    (b"FT/S",    3.04800000e-01,    "Feet Per Second",          MT_UNIT),
                    (b"IN/S",    2.54000000e-02,    "Inches Per Second",        MT_UNIT),
                    (b"KF/S",    3.04800000e+02,    "Kilofeet Per Second",      MT_UNIT),
                    (b"KM/S",    1.00000000e+03,    "Kilometers Per Second",    MT_UNIT),
                    (b"M/HR",    1.0 / 3600.0,      "Meters Per Hour",          MT_UNIT),
                    (b"M/MN",    1.0 / 60.0,        "Meters Per Minute",        MT_UNIT),
                    (b"MM/Y",    1.0 / (365.25 \
                                        * 24.0 \
                                        * 3600.0 \
                                        * 1.0e3),   "Millimeters Per Year",     MT_UNIT),
                ),
            ),
    
    b"PRES" : (
                "Pressure",
                b"PA  ",
                (
                    (b"PA  ",1.00000000e+00,                    "Pascals",    MT_UNIT),
                    (b"BAR ",1.00000000e+05,                    "Bars",    MT_UNIT),
                    (b"6PSI",6.89476000e+09,                    "Million Pounds Per Square Inch",    MT_UNIT),
                    (b"APSI",6.89476000e+03,                    "Pounds Per Square Inch (Absolute)",    MT_UNIT),
                    (b"ATM ",1.01324986e+05,                    "Atmospheres",    MT_UNIT),
                    (b"GPA ",1.00000000e+09,                    "Giga-Pascal",    MT_UNIT),
                    (b"K/C2",9.80664799e+04,                    "Kilograms Per Square Centimeter",    MT_UNIT),
                    (b"KPA ",1.00000000e+03,                    "Kilopascasl",    MT_UNIT),
                    (b"KPAA",1.00000000e+03,                    "Kilopascals (Absolute)",    MT_UNIT),
                    (b"KPAG",1.00000000e+03,    -101.32470000,    "Kilopascals (Gauge)",    MT_UNIT),
                    (b"MAPA",1.00000000e+06,                    "Megapascals",    MT_UNIT),
                    (b"PSI ",6.89476000e+03,                    "Pounds Per Square Inch",    MT_UNIT),
                    (b"PSIA",6.89476000e+03,                    "Pounds Per Square Inch (Absolute)",    MT_UNIT),
                    (b"PSIG",6.89476000e+03,    -14.69594098,    "Pounds Per Square Inch (Gauge)",    MT_UNIT),
                ),
            ),
    
    b"ACCE" : (
                "Acceleration",
                b"M/S2",
                (
                    (b"M/S2",    1.00000000,    "Meters Per Second Squared",    MT_UNIT),
                    (b"F/S2",    0.30480000,    "Feet Per Second Squared",    MT_UNIT),
                    (b"MGL ",    0.00001000,    "Milligals",    MT_UNIT),
                ),
            ),
    
    b"A/L " : (
                "Attenuation per unit length",
                b"DB/M",
                (
                    (b"DB/M",    1.00000000,        "Decibels Per Metre",    MT_UNIT),
                    (b"DB/F",    1.0 / 0.3048,    "Decibels Per Foot",    MT_UNIT),
                ),
            ),
    
    b"RESI" : (
                "Resistivity",
                b"OHMM",
                (
                    (b"OHMM",    1.0,        "Ohm * Metre",    MT_UNIT),
                ),
            ),
    
    b"ROTA" : (
                "Rotation",
                b"DEG ",
                (
                    (b"DEG ",    1.0,                   "Degree",    MT_UNIT),
                    (b"RAD ",    360.0/(2.0 * math.pi), "Radian",    MT_UNIT),
                    (b"REV ",    360.0,                 "Revolution",    MT_UNIT),
                ),
            ),
    
    b"TTIM" : (
                "Transit Time",
                b"US/M",
                (
                    (b"US/M",    1.0,                "Microsecond Per Metre",    MT_UNIT),
                    (b"MS/M",    1000.0,             "Mille Seconds Per Metre",  MT_UNIT),
                    (b"NS/M",    0.001,              "Nanosecond Per Metre",     MT_UNIT),
                    (b"US/F",    1/.3048,            "Microsecond Per Foot",     MT_UNIT),
                    (b"US-F",    1/.3048,            "Microsecond Per Foot",     b"US/F"),
                    (b"US-M",    1.0,                "Microsecond Per Metre",    b"US/M"),
                ),
            ),
    
    b"C/T " : (
                "Counts Per Time",
                b"CPS ",
                (
                    (b"CPS ",    1.0,                "Count Per Second",    MT_UNIT),
                    (b"1/S ",    1.0,                "Count Per Second",    b"CPS "),
                ),
            ),
    
    b"DENS" : (
                "Density",
                b"K/M3",
                (
                    (b"K/M3",    1.0,                "Kilogram Per Cubic Metre",    MT_UNIT),
                    (b"AT/M",    10332.2396297343,    "Atmosphere Per Metre",    MT_UNIT),
                    (b"G/C3",    1000.0,                "Gram Per Cubic Centimeter",    MT_UNIT),
                    (b"G/CC",    1000.0,                "Gram Per Cubic Centimeter",    b"G/C3"),
                    (b"G-CC",    1000.0,                "Gram Per Cubic Centimeter",    b"G/C3"),
                    (b"G/CM",    1000.0,                "Gram Per Cubic Centimeter",    b"G/C3"),
                    (b"KP/M",    101.970896093949,    "Kilopascal Per Metre",    MT_UNIT),
                    (b"L/F3",    16.0184051376108,    "Pound Per Cubic Foot",    MT_UNIT),
                    (b"LB/G",    119.826,            "Pound Per Gallon",    MT_UNIT),
                    (b"LBCF",    16.0184051376108,    "Pound Per Cubic Foot",    b"L/F3"),
                    (b"PA/M",    0.101971277911346,    "Pascal PerMeter",    MT_UNIT),
                    (b"PSIF",    2306.64836635026,    "Pound Per Square Inch Per Foot",    MT_UNIT),
                    (b"PSIM",    703.06806780377,    "Pound Per Square Inch Per Metre",    MT_UNIT),
                ),
            ),
    
    b"DFRA" : (
                "Dimensionless Fractions",
                b"V/V ",
                (
                    (b"V/V ",    1.0,                "Volume Ratio",    MT_UNIT),
                    (b"%   ",    0.01,                "Percent",    MT_UNIT),
                    (b"PPDK",    0.0001,                "Part Per Ten Thousand",    MT_UNIT),
                    (b"PPK ",    0.001,                "Part Per Thousand",    MT_UNIT),
                    (b"PPM ",    0.000001,            "Part Per Million",    MT_UNIT),
                    (b"PU  ",    0.01,                "Porosity Unit",    MT_UNIT),
                    (b"USTR",    0.000001,            "Microstrain (Delta length/length*10**6)",    MT_UNIT),
                    (b"RATI",    1.0,                "Ratio",    MT_UNIT),
                    (b"MM/M",    0.001,                "Millemeters per metre",    MT_UNIT),
                ),
            ),
    
    b"DIME" : (
                "Dimensionless",
                MT_UNIT,
                (
                    (MT_UNIT,    1.0,                "Blank",    MT_UNIT),
                    (b"----",    1.0,                "Dimensionless",    MT_UNIT),
                ),
            ),
    
    b"COND" : (
                "Conductivity",
                b"MH/M",
                (
                    (b"MH/M",    1.0,                "Mho Per Metre",    MT_UNIT),
                    (b"MHOM",    1.0,                "Mho Per Metre",    b"MH/M"),
                    (b"MMJM",    0.001,                "Millimho Per Metre",    b"MMHO"),
                    (b"MMH/",    0.001,                "Millimho Per Metre",    b"MMHO"),
                    (b"MMHO",    0.001,                "Millimho Per Metre",    MT_UNIT),
                    # Removed as this clashes with mille seconds per metre
                    #(b"MS/M",    0.001,                "Millisiemens Per Metre",    MT_UNIT),
                    (b"MSIE",    0.001,                "Millisiemens Per Metre",    MT_UNIT),
                    (b"SI/M",    1.0,                "Siemens Per Metre",    MT_UNIT),
                ),
            ),
    
    b"CURR" : (
                "Current",
                b"AMP ",
                (
                    (b"AMP ",    1.0,                "Ampere",    MT_UNIT),
                    (b"AMPS",    1.0,                "Ampere",    b"AMP "),
                    (b"MA  ",    0.001,                "Milliampere",    MT_UNIT),
                    (b"MICA",    0.000001,            "Microampere",    b"UA  "),
                    (b"UA  ",    0.000001,            "Microampere",    MT_UNIT),
                ),
            ),
    
    b"EPOT" : (
                "Electrical Potential",
                b"V   ",
                (
                    (b"V   ",    1.0,                "Volt",    MT_UNIT),
                    (b"VOLT",    1.0,                "Volt",    b"V   "),
                    (b"KV  ",    1000.0,                "Kilovolt",    MT_UNIT),
                    (b"MV  ",    0.001,                "Millivolt",    MT_UNIT),
                    (b"W   ",    0.000001,            "Microvolt",    b"UV  "),
                    (b"UV  ",    0.000001,            "Microvolt",    MT_UNIT),
                    (b"VAC ",    1.0,                "Volt AC",    MT_UNIT),
                    (b"VDC ",    1.0,                "Volt DC",    MT_UNIT),
                ),
            ),
    
    b"EGR " : (
                "Elemental Gamma Ray",
                b"GAPI",
                (
                    (b"GAPI",    1.0,                "API Gamma Ray Unit",    MT_UNIT),
                    (b"API ",    1.0,                "API Gamma Ray Unit",    b"GAPI"),
                ),
            ),
    
    b"ERES" : (
                "Electrical Resistance",
                b"OHMS",
                (
                    (b"OHMS",    1.0,                "Ohm",    MT_UNIT),
                ),
            ),
    
    b"FREQ" : (
                "Frequency",
                b"HZ  ",
                (
                    (b"HZ  ",    1.0,                "Hertz",    MT_UNIT),
                    (b"KHZ ",    1000.0,                "Kilohertz",    MT_UNIT),
                    (b"MHZ ",    1000000.0,            "Megahertz",    MT_UNIT),
                ),
            ),
    
    b"V/LE" : (
                "Volume Per Length",
                b"M3/M",
                (
                    (b"M3/M",    1.0,                "Cubic Metre Per Metre",    MT_UNIT),
                    (b"G/FT",    0.0124193299319438,    "GallonPerFoot",    MT_UNIT),
                ),
            ),
    
    b"MASS" : (
                "Mass",
                b"KG  ",
                (
                    (b"KG  ",    1.0,                "Kilogram",    MT_UNIT),
                    (b"G   ",    0.001,                "Gram",    MT_UNIT),
                    (b"KLB ",    453.592,            "Thousand Pounds",    MT_UNIT),
                    (b"LB  ",    0.453592,            "Pound",    MT_UNIT),
                    (b"LTON",    1016.04738054065,    "UK Long Ton",    MT_UNIT),
                    (b"MTON",    1000.0,                "Metric Ton",    MT_UNIT),
                    (b"STON",    907.184,            "US Short Ton",    MT_UNIT),
                    (b"TON ",    1000,                "Metric Ton",    MT_UNIT),
                    (b"TONS",    1000,                "Metric Ton",    b"TON "),
                ),
            ),
    
    b"FORC" : (
                "Force",
                b"N   ",
                (
                    (b"N   ",    1.0,                "Newton",    MT_UNIT),
                    (b"DECN",    10.0,                "Deca-Newton",    MT_UNIT),
                    (b"LBF ",    4.44822,            "Pound Force",    MT_UNIT),
                ),
            ),
    
    b"AREA" : (
                "Area",
                b"M2  ",
                (
                    (b"M2  ",    1.0,                "Square Metre",    MT_UNIT),
                    (b"ACRE",    4046.8636743797,    "Acre",    MT_UNIT),
                    (b"CM2 ",    0.0001,                "Square Centimeter",    MT_UNIT),
                    (b"FT2 ",    0.09290304,            "Square Foot",    MT_UNIT),
                    (b"IN2 ",    0.00064516,            "Square Inch",    MT_UNIT),
                    (b"MM2 ",    0.000000000001,        "Square Millimeter",    MT_UNIT),
                ),
            ),
    
    b"UNKN" : (
                "Unknown",
                b"UNKN",
                (
                    (b"UNKN",    1.0,                "Unknown",    MT_UNIT),
                ),
            ),
    
    b"M/L " : (
                "Mass Per Length",
                b"KG/M",
                (
                    (b"KG/M",    1.0,                "Kilogram per Metre",    MT_UNIT),
                    (b"LB/F",    1.48816,            "Pound per Foot",    MT_UNIT),
                ),
            ),
    
    b"PLEN" : (
                "Permeability Length",
                b"DAM ",
                (
                    (b"DAM ",    1.0,                "Darcy * Metre",    MT_UNIT),
                    (b"MDFT",    0.0003048,            "Millidarcy * Foot",    MT_UNIT),
                    (b"MDM ",    0.001,                "Millidarcy * Metre",    MT_UNIT),
                ),
            ),
    
    b"VOLU" : (
                "Volume",
                b"M3  ",
                (
                    (b"M3  ",    1.0,                "Cubic Metre",    MT_UNIT),
                    (b"BBL ",    0.158987243694837,    "Barrel",    MT_UNIT),
                    (b"C3  ",    0.000001,            "Cubic Centimeter",    MT_UNIT),
                    (b"F3  ",    0.0283169,            "Cubic Foot",    MT_UNIT),
                    (b"GAL ",    0.00378541866073481,"Gallon",    MT_UNIT),
                    (b"ML  ",    0.000001,            "Milliliter",    MT_UNIT),
                ),
            ),
    
    b"RVEL" : (
                "Rotational Velocity",
                b"RPS ",
                (
                    (b"RPS ",    1.0,                "Revolution Per Second",    MT_UNIT),
                    # TODO: This looks wrong
                    (b"DIHR",    5.01002004008016E-07,"Degree Per Hour",    MT_UNIT),
                    (b"RPM ",    1/60.0,              "Revolution Per Minute",    MT_UNIT),
                ),
            ),
    
    b"ENER" : (
                "Energy",
                b"EV  ",
                (
                    (b"EV  ",    1.0,                "Electron-Volt",    MT_UNIT),
                    (b"KEV ",    1000.0,                "Kilo-Electron-Volt",    MT_UNIT),
                    (b"MEV ",    1000000.0,            "Mega-Electron-Volt",    MT_UNIT),
                ),
            ),
    
    b"VISC" : (
                "Viscosity",
                b"CP  ",
                (
                    (b"CP  ",    1.0,                "Centipoise",    MT_UNIT),
                    (b"PAS ",    1000.0,                "Pascal * Second",    MT_UNIT),
                    (b"PL  ",    100.0,                "Poiseville",    MT_UNIT),
                ),
            ),
    
    b"IMAS" : (
                "Inverse Mass",
                b"KG-1",
                (
                    (b"KG-1",    1.0,                "Inverse Kilogram",    MT_UNIT),
                    (b"G-1 ",    1000.0,                "Inverse Gram",    MT_UNIT),
                    (b"LB-1",    2.20462442018378,    "Inverse Pound",    MT_UNIT),
                    (b"M/HG",    100.0,                "Milliequivalent Per 100 Gram",    MT_UNIT),
                ),
            ),
    
    b"ATTE" : (
              "Attenuation",
              b"DB  ",
                (
                    (b"DB  ",    1.0,                "Decibel",    MT_UNIT),
                ),
            ),
    
    b"POWE" : (
                "Power",
                b"NW  ",
                (
                    (b"NW  ",    1.0,                "Nanowatt",    MT_UNIT),
                ),
            ),
    
    b"T/L " : (
                "Temperature Per Length",
                b"DC/M",
                (
                    (b"DC/M",    1,                    "Degree Celsius Per Metre",    MT_UNIT),
                    (b"DC/K",    0.001,                "Degree Celsius Per Kilometer",    MT_UNIT),
                    (b"DCHM",    0.01,                "Degree Celsius Per Hundred Meters",    MT_UNIT),
                    (b"DF/F",    1.82268883056285,    "Degree Fahrenheit Per Foot",    MT_UNIT),
                    (b"DFHF",    0.0182268883056285,    "Degree Fabrenheit Per Hundred Feet",    MT_UNIT),
                    (b"DGFM",    0.555555555555556,    "Degree Fabrenbeit Per Metre",    MT_UNIT),
                ),
            ),
    
    b"PERM" : (
                "Permeability",
                b"DA  ",
                (
                    (b"DA  ",    1.0,   "Darcy",            MT_UNIT),
                    (b"MD  ",    0.001,     "Millidarcy",   MT_UNIT),
                ),
            ),
    
    b"ILEN" : (
                "Inverse Length",
                b"M-1 ",
                (
                    (b"M-1 ",    1.0,           "Inverse Metre",                MT_UNIT),
                    (b"B/C3",    1.0E-22,       "Barn Per Cubic Centimeter",    MT_UNIT),
                    (b"CU  ",    0.1,           "Capture Unit",                 MT_UNIT),
                    (b"FT-1",    1.0 / 0.3048,  "Inverse Foot",                 MT_UNIT),
                ),
            ),
    
    b"HTRA" : (
                "Heat Transfer",
                b"JSMC",
                (
                    (b"JSMC",    1.0,                "Joule Per Second Per Degree Celsius Per Square Metre",MT_UNIT),
                    (b"BHFF",    5.67826281498743,    "British Thermal Unit Per Hour Per Degree Fahrenheit Per Square Foot",MT_UNIT),
                    (b"KHMC",    1.1630000376812,    "Kilocalorie Per Hour Per Degree Celsius Per Square Metre",MT_UNIT),
                ),
            ),
}


from TotalDepth.LIS import ExceptionTotalDepthLIS

class ExceptionUnits(ExceptionTotalDepthLIS):
    """Specialisation of exception for Unit conversion."""
    pass

class ExceptionUnitsUnknownUnit(ExceptionUnits):
    """When a unit does not exist."""
    pass

class ExceptionUnitsUnknownCategory(ExceptionUnits):
    """When a unit category does not exist."""
    pass

class ExceptionUnitsNoUnitInCategory(ExceptionUnits):
    """When a unit does not exist in a category."""
    pass

class ExceptionUnitsMissmatchedCategory(ExceptionUnits):
    """When a two units do not exist in the same category."""
    pass

class UnitConvertCategory(object):
    """Internal module data structure that represents a category of units such as linear length.
    
    theCat is the unit category.
    
    theDesc is the description of that category.
    
    theBaseUnitName is the name of the base units for the category.
    For example for linear lenght this is b'M   '.
    
    theUnitS is a list of unit names.
    """
    def __init__(self, theCat, theDesc, theBaseUnitName, theUnitS):
        self.cat = theCat
        self.desc = theDesc
        self.base = theBaseUnitName
        # Map of {unit_name : UnitConvert, ...}
        self._unitMap = {}
        for u in theUnitS:
            assert(u[0] not in self._unitMap)
            self._unitMap[u[0]] = UnitConvert(u)
            
    def units(self):
        """Reuturns a list of unit names for this category."""
        return list(self._unitMap.keys())
            
    def unitConvertor(self, u):
        """Returns a UnitConvert object corresponding to the name u.
        Will raise a ExceptionUnitsNoUnitInCategory if not found."""
        try:
            return self._unitMap[u]
        except KeyError:
            raise ExceptionUnitsNoUnitInCategory(
                'UnitConvertCategory.unitConvertor(): No units "%s" in this category "%s". Have only: %s' \
                    % (u, self.cat, str(self.units()))
                )
        
    def convert(self, v, u_1, u_2):
        """Returns a value converted from one units to another.
        e.g. convert(1.2, "FEET", "INCH")"""
        return self.unitConvertor(u_1).convert(v, self.unitConvertor(u_2))

class UnitConvert(object):
    """Internal data structure for this module that representas a particular unit of measure.
    Takes a 4 or 5 member tuple from __RAW_UNIT_MAP.
    """
    def __init__(self, tup):
        assert(len(tup) in (4, 5)), 'UnitConvert args %s not length 4 or 5' % str(tup)
        assert(isinstance(tup[0], bytes))
        self.name = tup[0]
        self.mult = tup[1]
        if len(tup) == 4:
            self.offs = None
            self.desc = tup[2]
            assert(isinstance(tup[3], bytes))
            self.real = tup[3]
        else:
            self.offs = tup[2]
            self.desc = tup[3]
            assert(isinstance(tup[4], bytes))
            self.real = tup[4]
        # Substitue None if this is not an alias
        if self.real == MT_UNIT:
            self.real = None

    def convert(self, val, other):
        """Convert a value from me to the other where other is a UnitConvert object."""
        #baseVal = (val - self.offs) * self.mult
        #return (baseVal / other.mult) + other.offs
        if self.offs is not None:
            val -= self.offs
        baseVal = val * self.mult
        retVal = baseVal / other.mult
        if other.offs is not None:
            retVal += other.offs
        return retVal 

# Create the public data structures
# First the main map of units
# This is a map {string : UnitConvertCategory(), ...}
__UNIT_MAP = {}
# This maps unit_name -> the category that it is in
# as a map {string : (string, ...), ...}
__UNIT_TO_CATEGORY_MAP = {}
# Load maps
for __cat in list(__RAW_UNIT_MAP.keys()):
    assert(isinstance(__cat, bytes))
    assert(len(__cat) == LEN_UNIT_NAME)
    __desc, __base, __unitS = __RAW_UNIT_MAP[__cat]
    assert(len(__base) == LEN_UNIT_NAME)
    assert(isinstance(__desc, str))
    assert(isinstance(__base, bytes))
    assert(isinstance(__unitS, tuple))
    assert(__cat not in __UNIT_MAP)
    __UNIT_MAP[__cat] = UnitConvertCategory(__cat, __desc, __base, __unitS)
    for __unit in  __unitS:
        assert(len(__unit) in (4, 5)), 'len(__unitS) == 4 fails: {:d} == {:d}'.format(len(__unit), 4)
        assert(len(__unit[0]) == LEN_UNIT_NAME)
        assert(len(__unit[-1]) == LEN_UNIT_NAME)
        assert(__unit[0] not in __UNIT_TO_CATEGORY_MAP), 'Unit "%s" already in __UNIT_TO_CATEGRY_MAP' % __unit[0] 
        __UNIT_TO_CATEGORY_MAP[__unit[0]] = __cat
        # Clean namespace
        del __unit
    for __unit in  __unitS:
        assert(__unit[-1] == MT_UNIT or __unit[-1] in __UNIT_MAP[__cat].units()), 'Real unit "%s" not in %s' % (__unit[-1], __UNIT_MAP[__cat].units()) 
    # Check that the base unit is in the list of units
    assert(__base in __UNIT_MAP[__cat].units())
    # Give the namespace a good scrub
    del __desc
    del __base
    del __unitS
    del __cat
del __RAW_UNIT_MAP

def unitCategories():
    """Returns a list of the unit categories."""
    return list(__UNIT_MAP.keys()) 

def hasUnitCategory(c):
    """Returns True if I have that unit category e.g. b"TIME"."""
    return c in __UNIT_MAP 

def hasUnit(u):
    """Returns True if I have that unit e,g, b"FEET"."""
    return u in __UNIT_TO_CATEGORY_MAP

def category(unit):
    """Returns the category of the unit. May raise a ExceptionUnitsUnknownUnit."""
    try:
        return __UNIT_TO_CATEGORY_MAP[unit]
    except KeyError:
        raise ExceptionUnitsUnknownUnit('Unit "%s" not known' % unit)
    
def categoryDescription(theCat):
    """Returns the description of a unit category."""
    try:
        return __UNIT_MAP[theCat].desc
    except KeyError:
        raise ExceptionUnitsUnknownCategory('Unit category "%s" does nto exist.' % theCat)

def categoryBaseUnitName(theCat):
    try:
        return __UNIT_MAP[theCat].base
    except KeyError:
        raise ExceptionUnitsUnknownCategory('Unit category "%s" does nto exist.' % theCat)

def units(theCat=None):
    """Returns an unordered list of unit names. If category is None all unit
    names are returned, otherwise the unit names for a particular category are
    returned. This may raise a ExceptionUnitsUnknownCategory if the category
    does not exist."""
    if theCat is None:
        return list(__UNIT_TO_CATEGORY_MAP.keys())
    return retUnitConvertCategory(theCat).units()

def retUnitConvertCategory(c):
    """Returns a UnitConvertCategory object for the category.
    May raise a ExceptionUnits or descendent."""
    try:
        return __UNIT_MAP[c]
    except KeyError:
        raise ExceptionUnitsUnknownCategory('Unit category "%s" does nto exist.' % c)

def retUnitConvert(u):
    """Returns a UnitConvert object for the unit.
    May raise a ExceptionUnits or descendent."""
    myCat = category(u)
    myUcc = retUnitConvertCategory(myCat)
    return myUcc.unitConvertor(u)

def unitDescription(u):
    """Returns the description of the unit.
    e.g. Given ".1IN" returns "Tenth-inches".
    May raise a ExceptionUnits or descendent."""
    return retUnitConvert(u).desc

def realUnitName(u):
    """Returns the real unit name or None if u is the 'real' unit
    e.g. the 'real' unit name for b"FT  " is b"FEET".
    May raise a ExceptionUnits or descendent."""
    return retUnitConvert(u).real

def convert(v, u_1, u_2):
    """Returns a value converted from one units to another. e.g. convert(1.2, b"FEET", b"INCH").
    
    Will raise an ExceptionUnitsUnknownUnit if either unit is unknown.
    
    Will raise an ExceptionUnitsMissmatchedCategory is both units doe not belong is the same unit category."""
    try:
        c_1 = __UNIT_TO_CATEGORY_MAP[u_1]
    except KeyError:
        raise ExceptionUnitsUnknownUnit('Unit "%s" not known' % u_1)
    try:
        c_2 = __UNIT_TO_CATEGORY_MAP[u_2]
    except KeyError:
        raise ExceptionUnitsUnknownUnit('Unit "%s" not known' % u_2)
    if c_1 != c_2:
        ExceptionUnitsMissmatchedCategory(
            'Unit "%s" is in category "%s" but unit "%s" is in category "%s"' \
            % (u_1, c_1, u_2, c_2))
    # The next two statement may raise in unusual circumstances:
    # - If the __UNIT_TO_CATEGORY_MAP is missaligned with the __UNIT_MAP
    # - If the units in the UnitCategoryConvert object are missaligned with
    #    the informtion in in the __UNIT_TO_CATEGORY_MAP
    # In these circumstances this module has become corrupt after import (import
    # checks these conditions with asserts).
    myUcc = __UNIT_MAP[c_1]
    retVal = myUcc.convert(v, u_1, u_2)
    #print 'convert(%f, %s, %s) -> %f' % (v, u_1, u_2, retVal)
    return retVal

#: This is a simple mapping of actual units to 'optical' i.e. user friendly units.
__OPTICAL_UNIT_MAP = {
                      b"DM  " : b"M   ",
                      b"CM  " : b"M   ",
                      b"MM  " : b"M   ",
                      b".5MM" : b"M   ",
                      b"IN  " : b"FEET",
                      b"INS " : b"FEET",
                      b"INCH" : b"FEET",
                      b".1IN" : b"FEET",
}

# Sanity check
for __k, __v in __OPTICAL_UNIT_MAP.items():
    assert(hasUnit(__k))
    assert(hasUnit(__v))
    assert(category(__k) == category(__v))
del __k
del __v

def opticalUnits(u):
    """If possible returns the 'optical' units i.e. user friendly units.
    For example the 'optical' units of b'.1IN' are b'FEET'.
    Failure returns the argument."""
    try:
        return __OPTICAL_UNIT_MAP[u]
    except KeyError:
        pass
    return u
