#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation.
# Copyright (C) 2011-2021 Paul Ross
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
"""
Reads XML files generated from RP66V1 files and explores them for the units that they use.

Example output of 1885 files:

Producer code names::

     -1 TERRASCIENCES, Inc.     :                1
      0                         :                6
     15 INTEQ                   :                2
    126 CROCKER DATA PROCESSING :                3
    126 WEATHERFORD             :               13
    150 ATLAS                   :              256
    280 Halliburton             :              273
    440 PathFinder              :                2
    440 Schlumberger            :            2,733
    Producer code channel units:
     -1              :                4
     -1 %            :                8
     -1 GAPI         :                2
     -1 UNITS        :                1
     -1 brne         :                1
     -1 deg          :                4
     -1 degC         :                2
     -1 frac         :               15
     -1 g/cc         :                2
     -1 in           :                1
     -1 m            :               14
     -1 m/hr         :                1
     -1 ohmm         :                7
     -1 ppm          :                7
     -1 us/f         :                4
     -1 v/v          :                2
      0              :               22
      0 F3           :                2
      0 MMHO         :               54
      0 MS10         :                3
      0 b/e          :                1
      0 deg          :               16
      0 degC         :                4
      0 flg          :                4
      0 g            :               18
      0 g/cm3        :                4
      0 gAPI         :                5
      0 gauss        :                3
      0 in           :               47
      0 lb           :                1
      0 lbf          :                6
      0 m            :                6
      0 m/min        :                3
      0 m/s          :                4
      0 mV           :                1
      0 ms           :               10
      0 ohm.m        :                5
      0 unitless     :               22
      0 us           :               16
      0 us/ft        :                5
      0 v/v          :                8
     15 deg          :                8
     15 m            :                2
     15 ohm.m        :                3
    126              :               25
    126 CCPS         :                4
    126 DC/S         :                1
    126 G            :                3
    126 GAUSS        :                3
    126 MMHO         :              106
    126 MPM          :                2
    126 b/e          :                2
    126 b/elec       :                3
    126 cps          :                1
    126 deg          :               20
    126 degC         :               14
    126 ft/s         :                6
    126 g            :               20
    126 g/cc         :               10
    126 g/cm3        :               44
    126 gAPI         :               28
    126 gapi         :                3
    126 gauss        :                5
    126 in           :              100
    126 inch         :                5
    126 lb           :                1
    126 lbf          :               11
    126 m            :               13
    126 m/h          :                2
    126 m/min        :                6
    126 m3           :                4
    126 mA           :                1
    126 mD           :                1
    126 mV           :               26
    126 microseconds :               10
    126 milliVolts   :                6
    126 min          :                2
    126 mm           :                3
    126 mmho/m       :               30
    126 ms           :                9
    126 ohm.m        :               54
    126 psi          :                1
    126 pu           :               63
    126 t            :                2
    126 unitless     :                2
    126 us           :               19
    126 us/ft        :               11
    126 v/v          :               38
    150              :            8,033
    150 %            :               96
    150 1/psi        :               70
    150 1/s          :               51
    150 1E-2 T/m     :               18
    150 1E-5 Oe      :              130
    150 K            :                5
    150 L            :              423
    150 V            :              322
    150 b/e          :                9
    150 bbl          :                2
    150 cP           :               35
    150 cm           :               98
    150 cm3          :              624
    150 cm3/s        :              196
    150 cu           :                3
    150 dAPI         :               70
    150 dB           :                6
    150 dB/ft        :              261
    150 deg          :              715
    150 degC         :            1,083
    150 degC/min     :              124
    150 degF         :              556
    150 degF/min     :               34
    150 ft           :               32
    150 ft/s         :               70
    150 ft3          :               18
    150 ft3/bbl      :               70
    150 g/cm3        :               67
    150 gAPI         :              424
    150 h            :              893
    150 in           :            1,637
    150 kHz          :              107
    150 lbf          :            1,036
    150 m            :            1,267
    150 m/min        :              300
    150 m3           :               90
    150 mA           :              103
    150 mD           :               28
    150 mG           :              131
    150 mS/m         :               79
    150 mV           :              835
    150 min          :              328
    150 mm           :               67
    150 ms           :              538
    150 ohm.m        :              346
    150 pF           :               35
    150 ppm          :              127
    150 psi          :            2,252
    150 psi/min      :              347
    150 pu           :              800
    150 s            :            1,147
    150 uV           :              175
    150 us           :              342
    150 us/ft        :              535
    280              :            1,646
    280 %            :               66
    280 0.00         :                2
    280 0.001/ohm    :                7
    280 0.01         :                1
    280 0.01 L       :               66
    280 0.1          :                1
    280 0.1 L/S      :               96
    280 0.1 in       :                2
    280 08.3         :                4
    280 1.0/         :                8
    280 1.0/S        :               24
    280 1/PS         :               32
    280 100          :               18
    280 100 pu       :               12
    280 C/C          :                4
    280 DECP         :                9
    280 G            :               14
    280 G/CC         :                9
    280 GOR          :               48
    280 IN_2         :                1
    280 Kv/K         :               35
    280 MILS         :                2
    280 NESW         :                1
    280 NONE         :            2,003
    280 QLTY         :                2
    280 RPM          :               57
    280 S            :              406
    280 SEC          :                3
    280 V            :               49
    280 api          :              133
    280 b/e          :               28
    280 cP           :               14
    280 cc           :               45
    280 ccps         :               90
    280 cnts         :                1
    280 cps          :               32
    280 dB           :                1
    280 decp         :              616
    280 deg          :              212
    280 degC         :              272
    280 degF         :              123
    280 dist         :               29
    280 fph          :                4
    280 fpm          :               11
    280 ft           :               11
    280 ft3          :               20
    280 g            :               28
    280 g/c3         :               22
    280 g/cc         :              152
    280 gAPI         :              175
    280 gapi         :                1
    280 gm/c         :               29
    280 in           :              288
    280 kHz          :               10
    280 kg/m3        :                8
    280 klbf         :                5
    280 lb           :                3
    280 lbm          :               77
    280 lbs          :              140
    280 ltrs         :               11
    280 m            :              316
    280 m/mi         :                4
    280 m/min        :               44
    280 m3           :               60
    280 mA           :               29
    280 mD           :               23
    280 mG           :                4
    280 mPsec        :                2
    280 mS           :               49
    280 mSEC         :                2
    280 mV           :               51
    280 md/cp        :               96
    280 min          :               66
    280 mm           :              148
    280 mmho         :                3
    280 mmho/m       :               48
    280 mmo/         :                1
    280 mmo/m        :               76
    280 mpm          :               38
    280 ms           :              167
    280 nT           :               22
    280 no.          :               29
    280 ohm.         :                7
    280 ohm.m        :               58
    280 ohmm         :              390
    280 pF           :               36
    280 ppm          :               75
    280 pres         :               29
    280 psi          :              597
    280 psia         :              965
    280 psig         :               31
    280 pu           :              127
    280 sec          :                8
    280 serv         :               29
    280 time         :               29
    280 uS           :                8
    280 uS/f         :                6
    280 uS/ft        :                3
    280 ucts         :                7
    280 us           :               78
    280 us/m         :                5
    280 uspf         :              101
    280 v/v          :                5
    280 vol          :               29
    280 x8.3ms       :                6
    280 z1x1         :              174
    280 z1x2         :              174
    280 z1y1         :              174
    280 z1y2         :              174
    280 z2x1         :               29
    280 z2x2         :               29
    280 z2y1         :               29
    280 z2y2         :               29
    280 zoom         :              203
    440              :          327,687
    440 %            :           16,349
    440 ----         :              587
    440 0.1 deg/m    :                1
    440 0.1 in       :           29,587
    440 0.5 ms       :                1
    440 1/30 deg/m   :                6
    440 1/min        :              100
    440 1/s          :           11,907
    440 10 ms        :                9
    440 1000 ft.lbf  :               65
    440 1000 kPa.s/m :               23
    440 1000 kgf     :               53
    440 1000 lbf     :              100
    440 96.487 C/g   :                4
    440 A            :            7,696
    440 A/m          :            1,948
    440 BAD_UNIT-?   :               14
    440 CPS          :                1
    440 GPa          :               27
    440 Hz           :           15,966
    440 L/min        :                5
    440 MPa          :                1
    440 Mrayl        :              703
    440 N            :            3,073
    440 N.m          :                4
    440 Oe           :               67
    440 Pa           :               20
    440 Pa.s         :                6
    440 S            :                4
    440 V            :           79,974
    440 W            :               26
    440 b/cm3        :                2
    440 b/e          :                2
    440 bar          :                8
    440 c/min        :            5,748
    440 c/s          :               43
    440 cP           :              561
    440 cm3          :           13,512
    440 cm3/s        :            6,155
    440 cu           :              214
    440 dB           :            4,245
    440 dB.mW        :               48
    440 dB/m         :            1,461
    440 deg          :            8,578
    440 deg/100ft    :                2
    440 deg/30m      :               88
    440 deg/ft       :                6
    440 deg/m        :              334
    440 degC         :           25,640
    440 degF         :            1,753
    440 ft           :              719
    440 ft/h         :            4,875
    440 ft/min       :              721
    440 ft/s2        :              368
    440 ft2          :                6
    440 ft3          :               28
    440 ft3/bbl      :            1,014
    440 ft3/ft3      :              136
    440 g            :               44
    440 g/cm3        :            8,827
    440 gAPI         :           14,847
    440 gal/min      :               61
    440 gn           :               60
    440 h            :            1,730
    440 in           :           18,022
    440 in2          :               87
    440 kN.m         :                1
    440 kPa          :           42,487
    440 kPa/h        :              244
    440 kg/m3        :               37
    440 kgf/kgf      :              320
    440 km.daN       :                2
    440 lbf          :            4,957
    440 lbm/gal      :               94
    440 m            :           13,969
    440 m/h          :              595
    440 m/min        :            1,792
    440 m/s          :              313
    440 m/s2         :            5,142
    440 m2           :              885
    440 m3           :              728
    440 m3/m         :              126
    440 m3/m3        :           20,861
    440 mA           :           11,418
    440 mD           :            1,024
    440 mD.ft        :                6
    440 mD.m         :              216
    440 mPa.s        :              222
    440 mS/m         :            3,407
    440 mSv/h        :                5
    440 mT           :              775
    440 mV           :            5,218
    440 mgn          :               11
    440 min          :            5,312
    440 min/ft       :               21
    440 min/m        :              102
    440 mm           :                1
    440 mm2          :                7
    440 ms           :           33,095
    440 nT           :                7
    440 nW           :                6
    440 nm           :              135
    440 ohm          :              223
    440 ohm.m        :           19,449
    440 ppk          :               42
    440 ppm          :              790
    440 psi          :          165,969
    440 pu           :            1,522
    440 rad          :               18
    440 s            :            8,699
    440 uA           :              864
    440 uV           :            2,420
    440 unitless     :                6
    440 us           :            9,722
    440 us/ft        :            8,995
    440 us/m         :               28
    Producer code attribute units:
     -1              :            1,458
     -1 GAPI         :                3
     -1 dCpm         :                1
     -1 deg          :                3
     -1 degC         :                4
     -1 frac         :                3
     -1 g/cc         :                3
     -1 in           :                1
     -1 lb/g         :                1
     -1 m            :               33
     -1 ohmm         :                3
     -1 ppm          :                2
     -1 us/f         :                4
      0              :            4,665
      0 DEG          :                2
      0 Hrs          :                1
      0 M            :               17
      0 Metres       :                8
      0 SEC/QT       :                1
      0 deg C        :                8
      0 degC         :               20
      0 g/c3         :                1
      0 g/cm3        :                4
      0 in           :                8
      0 inches       :                6
      0 kg/m         :                4
      0 lb/USg       :                1
      0 lb/ft        :                4
      0 m            :               70
      0 mL/30min     :                4
      0 metres       :               19
      0 ml/30Min     :                2
      0 ohm-m        :                6
      0 ohm.m        :               16
      0 sec/qt       :                5
      0 us           :               22
      0 us/ft        :                4
     15              :              800
     15 Hrs          :                2
     15 M            :                3
     15 m            :               17
    126              :           13,775
    126 CP           :               14
    126 Celsius      :               18
    126 DEG C        :                2
    126 FT           :                3
    126 IN           :               13
    126 INCHES       :                2
    126 M            :               11
    126 METRES       :                4
    126 OHM-M        :                4
    126 degC         :               97
    126 g/cc         :               14
    126 g/cm3        :                3
    126 grams/cc     :                3
    126 in           :              126
    126 lbf/ft       :               51
    126 m            :              328
    126 metres       :               35
    126 ml/30Min     :               15
    126 mm           :                3
    126 ohm.m        :               43
    126 ohmm         :                6
    126 pounds/ft    :                5
    126 sec/qt       :                6
    126 us           :                8
    150              :       15,502,799
    150 %            :              921
    150 Hz           :              188
    150 cP           :               98
    150 cm           :              383
    150 cm3          :              131
    150 cm3/s        :                7
    150 dB/ft        :              300
    150 deg          :            1,119
    150 degC         :              538
    150 degC/min     :                7
    150 degF         :               50
    150 ft           :               44
    150 g/cm3        :              147
    150 gAPI         :              181
    150 in           :            1,255
    150 kHz          :              792
    150 lbf          :              186
    150 lbm          :              905
    150 lbm/ft       :              172
    150 lbm/gal      :              140
    150 m            :           10,387
    150 m/min        :               23
    150 mD/cP        :               14
    150 mS/m         :               30
    150 mV           :               87
    150 mm           :              301
    150 ms           :              214
    150 ohm.m        :              357
    150 ppm          :               14
    150 psi          :              203
    150 psi/min      :               87
    150 pu           :                7
    150 s            :           19,681
    150 us           :            6,689
    150 us/ft        :              258
    280              :          260,292
    280 $/da         :               32
    280 %            :              133
    280 0.1 in       :                4
    280 Hz           :               46
    280 N            :               19
    280 cP           :               18
    280 cps          :               12
    280 cptm         :               77
    280 deg          :            1,093
    280 degC         :            1,484
    280 degF         :              402
    280 f-p          :                6
    280 fph          :               12
    280 ft           :              190
    280 g            :              211
    280 g/cc         :              221
    280 gpm          :                6
    280 hr           :               79
    280 in           :              714
    280 kHz          :              145
    280 kPaa         :               19
    280 kg/m3        :               22
    280 kgm3         :               18
    280 klb          :                6
    280 lbpf         :              159
    280 lbs          :              930
    280 m            :            5,789
    280 m/hr         :               25
    280 mV           :               12
    280 mm           :              981
    280 mmo/m        :               15
    280 mpm          :              753
    280 mptm         :               12
    280 ms           :              289
    280 nT           :              209
    280 ohmm         :              504
    280 pH           :               92
    280 pa           :                2
    280 ppg          :              120
    280 ppm          :              273
    280 psi          :              119
    280 psia         :              867
    280 psig         :               10
    280 rpm          :                6
    280 s            :              342
    280 s/qt         :               78
    280 sec          :              144
    280 sg           :                6
    280 spf          :                8
    280 spl          :                2
    280 spqt         :               12
    280 ucts         :              220
    280 us           :              385
    280 us/m         :               31
    280 uspf         :              215
    440              :       35,769,005
    440 %            :           34,429
    440 0.01 degF/ft :               26
    440 0.1 in       :            7,110
    440 0.5 ms       :           11,097
    440 1/s          :          147,530
    440 1000 1/s     :              143
    440 1000 ft.lbf  :                1
    440 1000 kPa.s/m :               15
    440 1000 kgf     :                1
    440 1000 lbf     :                1
    440 1000 lbm     :              834
    440 1E-4 cm2/s   :               83
    440 1E-5 Oe      :                3
    440 1E-6 1/Pa    :              214
    440 1E-6 1/psi   :               13
    440 96.487 C/g   :                2
    440 A            :            2,614
    440 A/m          :              581
    440 Hz           :            7,413
    440 K            :              180
    440 Mrayl        :              453
    440 N            :           11,282
    440 Oe           :              192
    440 V            :          316,781
    440 bbl          :              999
    440 c/min        :            4,829
    440 cP           :          611,762
    440 cm           :            1,441
    440 cm3          :        1,771,845
    440 cm3/h        :                5
    440 cm3/min      :            1,316
    440 cm3/s        :              124
    440 cu           :              342
    440 d            :                6
    440 dAPI         :              763
    440 dB           :            2,300
    440 dB/m         :              283
    440 deg          :          167,842
    440 degC         :          209,611
    440 degC/km      :              428
    440 degC/m       :            2,166
    440 degF         :            8,410
    440 degF/ft      :               15
    440 ft           :        2,043,783
    440 ft/h         :            3,556
    440 ft/s2        :                9
    440 ft3          :              841
    440 ft3/bbl      :               13
    440 ft3/ft3      :               13
    440 g            :               24
    440 g/cm3        :           34,157
    440 gAPI         :           74,124
    440 gn           :               48
    440 h            :            1,493
    440 in           :          913,413
    440 kHz          :               34
    440 kN.m         :                1
    440 kPa          :          860,887
    440 kPa/h        :              118
    440 keV          :            4,726
    440 kg           :           69,794
    440 kg/m         :              511
    440 kg/m3        :               85
    440 kgf/kgf      :              212
    440 kohm         :               88
    440 lbf          :            9,681
    440 lbf/lbf      :               23
    440 lbm          :              635
    440 lbm/ft       :            2,997
    440 lbm/gal      :            1,608
    440 lbm/min      :               32
    440 m            :          398,845
    440 m/h          :               58
    440 m/min        :               19
    440 m/s          :               14
    440 m/s2         :            5,330
    440 m2/g         :               64
    440 m3           :          275,811
    440 m3/m3        :            1,132
    440 mA           :            4,238
    440 mD           :        1,223,325
    440 mD.ft        :                1
    440 mD/cP        :        1,633,855
    440 mPa.s        :            1,442
    440 mS/m         :            1,884
    440 mT           :            5,997
    440 mV           :            8,523
    440 mV/m         :              111
    440 mbar         :              224
    440 mgn          :               52
    440 min          :          164,455
    440 mm           :              544
    440 mm2          :               96
    440 mol/kg       :               96
    440 ms           :            3,007
    440 nT           :              974
    440 nW           :                4
    440 nm           :              459
    440 ohm          :            1,017
    440 ohm.m        :           14,967
    440 ppk          :               45
    440 ppm          :           85,551
    440 psi          :        4,190,937
    440 psi/h        :                4
    440 pu           :            1,668
    440 rad/ft3      :               13
    440 rad/m3       :               52
    440 s            :        1,764,018
    440 s/m3         :                5
    440 uA           :            3,719
    440 uV           :            7,845
    440 us           :           12,236
    440 us/ft        :            7,500
    440 us/m         :               20


    2020-08-31 11:28:31,102 - units.py         -  152 -  1801 - (MainThread) - INFO     - Loading all unit standard forms into the cache

    Channels:
    Producer code: -1
      Found code: ['', '%', 'GAPI', 'degC', 'g/cc', 'in', 'm', 'ohmm', 'ppm']
    Missing code: ['UNITS', 'brne', 'deg', 'frac', 'm/hr', 'us/f', 'v/v']
      Found standard form: ['deg', 'degC', 'in', 'm', 'ppm']
    Missing standard form: ['', '%', 'GAPI', 'UNITS', 'brne', 'frac', 'g/cc', 'm/hr', 'ohmm', 'us/f', 'v/v']

    Producer code: 0
      Found code: ['', 'F3', 'MMHO', 'b/e', 'degC', 'g', 'g/cm3', 'gAPI', 'gauss', 'in', 'lbf', 'm', 'm/min', 'm/s', 'mV', 'ms', 'ohm.m', 'us', 'us/ft']
    Missing code: ['MS10', 'deg', 'flg', 'lb', 'unitless', 'v/v']
      Found standard form: ['deg', 'degC', 'g', 'g/cm3', 'gAPI', 'in', 'lbf', 'm', 'm/min', 'm/s', 'ms', 'ohm.m', 'us', 'us/ft']
    Missing standard form: ['', 'F3', 'MMHO', 'MS10', 'b/e', 'flg', 'gauss', 'lb', 'mV', 'unitless', 'v/v']

    Producer code: 15
      Found code: ['m', 'ohm.m']
    Missing code: ['deg']
      Found standard form: ['deg', 'm', 'ohm.m']
    Missing standard form: []

    Producer code: 126
      Found code: ['', 'G', 'MMHO', 'b/e', 'cps', 'degC', 'ft/s', 'g', 'g/cc', 'g/cm3', 'gAPI', 'gauss', 'in', 'lbf', 'm', 'm/h', 'm/min', 'm3', 'mA', 'mD', 'mV', 'min', 'mm', 'mmho/m', 'ms', 'ohm.m', 'psi', 'pu', 't', 'us', 'us/ft']
    Missing code: ['CCPS', 'DC/S', 'GAUSS', 'MPM', 'b/elec', 'deg', 'gapi', 'inch', 'lb', 'microseconds', 'milliVolts', 'unitless', 'v/v']
      Found standard form: ['deg', 'degC', 'ft/s', 'g', 'g/cm3', 'gAPI', 'in', 'lbf', 'm', 'm/h', 'm/min', 'm3', 'mD', 'min', 'mm', 'ms', 'ohm.m', 'psi', 'pu', 't', 'us', 'us/ft']
    Missing standard form: ['', 'CCPS', 'DC/S', 'G', 'GAUSS', 'MMHO', 'MPM', 'b/e', 'b/elec', 'cps', 'g/cc', 'gapi', 'gauss', 'inch', 'lb', 'mA', 'mV', 'microseconds', 'milliVolts', 'mmho/m', 'unitless', 'v/v']

    Producer code: 150
      Found code: ['', '%', '1/psi', '1/s', '1E-5 Oe', 'K', 'L', 'V', 'b/e', 'bbl', 'cP', 'cm', 'cm3', 'cm3/s', 'cu', 'dAPI', 'dB', 'dB/ft', 'degC', 'degC/min', 'degF', 'degF/min', 'ft', 'ft/s', 'ft3', 'ft3/bbl', 'g/cm3', 'gAPI', 'h', 'in', 'kHz', 'lbf', 'm', 'm/min', 'm3', 'mA', 'mD', 'mS/m', 'mV', 'min', 'mm', 'ms', 'ohm.m', 'pF', 'ppm', 'psi', 'psi/min', 'pu', 's', 'uV', 'us', 'us/ft']
    Missing code: ['1E-2 T/m', 'deg', 'mG']
      Found standard form: ['1/psi', '1/s', '1E-5 Oe', 'K', 'L', 'V', 'bbl', 'cP', 'cm', 'cm3', 'cm3/s', 'cu', 'dAPI', 'dB', 'dB/ft', 'deg', 'degC', 'degC/min', 'degF', 'degF/min', 'ft', 'ft/s', 'ft3', 'ft3/bbl', 'g/cm3', 'gAPI', 'h', 'in', 'kHz', 'lbf', 'm', 'm/min', 'm3', 'mD', 'mS/m', 'min', 'mm', 'ms', 'ohm.m', 'ppm', 'psi', 'psi/min', 'pu', 's', 'uV', 'us', 'us/ft']
    Missing standard form: ['', '%', '1E-2 T/m', 'b/e', 'mA', 'mG', 'mV', 'pF']

    Producer code: 280
      Found code: ['', '%', '0.1 in', 'C/C', 'DECP', 'G', 'G/CC', 'NONE', 'RPM', 'S', 'SEC', 'V', 'b/e', 'cP', 'cc', 'cps', 'dB', 'degC', 'degF', 'ft', 'ft3', 'g', 'g/cc', 'gAPI', 'in', 'kHz', 'kg/m3', 'lbm', 'm', 'm/mi', 'm/min', 'm3', 'mA', 'mD', 'mS', 'mV', 'min', 'mm', 'mmho', 'mmho/m', 'ms', 'nT', 'ohm.m', 'ohmm', 'pF', 'ppm', 'psi', 'psig', 'pu', 'uS', 'us', 'us/m']
    Missing code: ['0.00', '0.001/ohm', '0.01', '0.01 L', '0.1', '0.1 L/S', '08.3', '1.0/', '1.0/S', '1/PS', '100', '100 pu', 'GOR', 'IN_2', 'Kv/K', 'MILS', 'NESW', 'QLTY', 'api', 'ccps', 'cnts', 'decp', 'deg', 'dist', 'fph', 'fpm', 'g/c3', 'gapi', 'gm/c', 'klbf', 'lb', 'lbs', 'ltrs', 'mG', 'mPsec', 'mSEC', 'md/cp', 'mmo/', 'mmo/m', 'mpm', 'no.', 'ohm.', 'pres', 'psia', 'sec', 'serv', 'time', 'uS/f', 'uS/ft', 'ucts', 'uspf', 'v/v', 'vol', 'x8.3ms', 'z1x1', 'z1x2', 'z1y1', 'z1y2', 'z2x1', 'z2x2', 'z2y1', 'z2y2', 'zoom']
      Found standard form: ['0.01', '0.1 in', 'S', 'V', 'cP', 'dB', 'deg', 'degC', 'degF', 'ft', 'ft3', 'g', 'gAPI', 'in', 'kHz', 'kg/m3', 'lbm', 'm', 'm/min', 'm3', 'mD', 'mS', 'min', 'mm', 'ms', 'nT', 'ohm.m', 'ppm', 'psi', 'pu', 'uS', 'us', 'us/m']
    Missing standard form: ['', '%', '0.00', '0.001/ohm', '0.01 L', '0.1', '0.1 L/S', '08.3', '1.0/', '1.0/S', '1/PS', '100', '100 pu', 'C/C', 'DECP', 'G', 'G/CC', 'GOR', 'IN_2', 'Kv/K', 'MILS', 'NESW', 'NONE', 'QLTY', 'RPM', 'SEC', 'api', 'b/e', 'cc', 'ccps', 'cnts', 'cps', 'decp', 'dist', 'fph', 'fpm', 'g/c3', 'g/cc', 'gapi', 'gm/c', 'klbf', 'lb', 'lbs', 'ltrs', 'm/mi', 'mA', 'mG', 'mPsec', 'mSEC', 'mV', 'md/cp', 'mmho', 'mmho/m', 'mmo/', 'mmo/m', 'mpm', 'no.', 'ohm.', 'ohmm', 'pF', 'pres', 'psia', 'psig', 'sec', 'serv', 'time', 'uS/f', 'uS/ft', 'ucts', 'uspf', 'v/v', 'vol', 'x8.3ms', 'z1x1', 'z1x2', 'z1y1', 'z1y2', 'z2x1', 'z2x2', 'z2y1', 'z2y2', 'zoom']

    Producer code: 440
      Found code: ['', '%', '----', '0.1 deg/m', '0.1 in', '0.5 ms', '1/min', '1/s', '10 ms', '1000 ft.lbf', '1000 kPa.s/m', '1000 kgf', '1000 lbf', 'A', 'A/m', 'CPS', 'GPa', 'Hz', 'L/min', 'MPa', 'Mrayl', 'N', 'N.m', 'Oe', 'Pa', 'Pa.s', 'S', 'V', 'W', 'b/cm3', 'b/e', 'bar', 'c/min', 'c/s', 'cP', 'cm3', 'cm3/s', 'cu', 'dB', 'dB.mW', 'dB/m', 'deg/100ft', 'deg/30m', 'deg/ft', 'deg/m', 'degC', 'degF', 'ft', 'ft/h', 'ft/min', 'ft/s2', 'ft2', 'ft3', 'ft3/bbl', 'ft3/ft3', 'g', 'g/cm3', 'gAPI', 'gal/min', 'gn', 'h', 'in', 'in2', 'kN.m', 'kPa', 'kPa/h', 'kg/m3', 'kgf/kgf', 'km.daN', 'lbf', 'lbm/gal', 'm', 'm/h', 'm/min', 'm/s', 'm/s2', 'm2', 'm3', 'm3/m', 'm3/m3', 'mA', 'mD', 'mD.ft', 'mD.m', 'mPa.s', 'mS/m', 'mSv/h', 'mT', 'mV', 'mgn', 'min', 'min/ft', 'min/m', 'mm', 'mm2', 'ms', 'nT', 'nW', 'nm', 'ohm', 'ohm.m', 'ppk', 'ppm', 'psi', 'pu', 'rad', 's', 'uA', 'uV', 'us', 'us/ft', 'us/m']
    Missing code: ['1/30 deg/m', '96.487 C/g', 'BAD_UNIT-?', 'deg', 'unitless']
      Found standard form: ['0.1 deg/m', '0.1 in', '0.5 ms', '1/30 deg/m', '1/min', '1/s', '10 ms', '1000 ft.lbf', '1000 kgf', '1000 lbf', 'A', 'A/m', 'GPa', 'Hz', 'L/min', 'MPa', 'N', 'N.m', 'Oe', 'Pa', 'Pa.s', 'S', 'V', 'b/cm3', 'bar', 'c/min', 'c/s', 'cP', 'cm3', 'cm3/s', 'cu', 'dB', 'dB.mW', 'dB/m', 'deg', 'deg/ft', 'deg/m', 'degC', 'degF', 'ft', 'ft/h', 'ft/min', 'ft/s2', 'ft2', 'ft3', 'ft3/bbl', 'ft3/ft3', 'g', 'g/cm3', 'gAPI', 'gal/min', 'h', 'in', 'in2', 'kN.m', 'kPa', 'kPa/h', 'kg/m3', 'kgf/kgf', 'km.daN', 'lbf', 'lbm/gal', 'm', 'm/h', 'm/min', 'm/s', 'm/s2', 'm2', 'm3', 'm3/m', 'm3/m3', 'mD', 'mD.ft', 'mD.m', 'mPa.s', 'mS/m', 'mSv/h', 'mT', 'min', 'min/ft', 'min/m', 'mm', 'mm2', 'ms', 'nT', 'nW', 'nm', 'ohm', 'ohm.m', 'ppk', 'ppm', 'psi', 'pu', 'rad', 's', 'uA', 'uV', 'us', 'us/ft', 'us/m']
    Missing standard form: ['', '%', '----', '1000 kPa.s/m', '96.487 C/g', 'BAD_UNIT-?', 'CPS', 'Mrayl', 'W', 'b/e', 'deg/100ft', 'deg/30m', 'gn', 'mA', 'mV', 'mgn', 'unitless']


    Attributes:
    Producer code: -1
      Found code: ['', 'GAPI', 'degC', 'g/cc', 'in', 'm', 'ohmm', 'ppm']
    Missing code: ['dCpm', 'deg', 'frac', 'lb/g', 'us/f']
      Found standard form: ['deg', 'degC', 'in', 'm', 'ppm']
    Missing standard form: ['', 'GAPI', 'dCpm', 'frac', 'g/cc', 'lb/g', 'ohmm', 'us/f']

    Producer code: 0
      Found code: ['', 'DEG', 'M', 'deg C', 'degC', 'g/cm3', 'in', 'kg/m', 'lb/ft', 'm', 'mL/30min', 'ohm.m', 'us', 'us/ft']
    Missing code: ['Hrs', 'Metres', 'SEC/QT', 'g/c3', 'inches', 'lb/USg', 'metres', 'ml/30Min', 'ohm-m', 'sec/qt']
      Found standard form: ['degC', 'g/cm3', 'in', 'kg/m', 'm', 'ohm.m', 'us', 'us/ft']
    Missing standard form: ['', 'DEG', 'Hrs', 'M', 'Metres', 'SEC/QT', 'deg C', 'g/c3', 'inches', 'lb/USg', 'lb/ft', 'mL/30min', 'metres', 'ml/30Min', 'ohm-m', 'sec/qt']
    Producer code: 15
      Found code: ['', 'M', 'm']
    Missing code: ['Hrs']
      Found standard form: ['m']
    Missing standard form: ['', 'Hrs', 'M']

    Producer code: 126
      Found code: ['', 'CP', 'FT', 'IN', 'INCHES', 'M', 'METRES', 'degC', 'g/cc', 'g/cm3', 'in', 'm', 'mm', 'ohm.m', 'ohmm', 'us']
    Missing code: ['Celsius', 'DEG C', 'OHM-M', 'grams/cc', 'lbf/ft', 'metres', 'ml/30Min', 'pounds/ft', 'sec/qt']
      Found standard form: ['degC', 'g/cm3', 'in', 'm', 'mm', 'ohm.m', 'us']
    Missing standard form: ['', 'CP', 'Celsius', 'DEG C', 'FT', 'IN', 'INCHES', 'M', 'METRES', 'OHM-M', 'g/cc', 'grams/cc', 'lbf/ft', 'metres', 'ml/30Min', 'ohmm', 'pounds/ft', 'sec/qt']

    Producer code: 150
      Found code: ['', '%', 'Hz', 'cP', 'cm', 'cm3', 'cm3/s', 'dB/ft', 'degC', 'degC/min', 'degF', 'ft', 'g/cm3', 'gAPI', 'in', 'kHz', 'lbf', 'lbm', 'lbm/ft', 'lbm/gal', 'm', 'm/min', 'mD/cP', 'mS/m', 'mV', 'mm', 'ms', 'ohm.m', 'ppm', 'psi', 'psi/min', 'pu', 's', 'us', 'us/ft']
    Missing code: ['deg']
      Found standard form: ['Hz', 'cP', 'cm', 'cm3', 'cm3/s', 'dB/ft', 'deg', 'degC', 'degC/min', 'degF', 'ft', 'g/cm3', 'gAPI', 'in', 'kHz', 'lbf', 'lbm', 'lbm/ft', 'lbm/gal', 'm', 'm/min', 'mD/cP', 'mS/m', 'mm', 'ms', 'ohm.m', 'ppm', 'psi', 'psi/min', 'pu', 's', 'us', 'us/ft']
    Missing standard form: ['', '%', 'mV']

    Producer code: 280
      Found code: ['', '%', '0.1 in', 'Hz', 'N', 'cP', 'cps', 'degC', 'degF', 'ft', 'g', 'g/cc', 'gpm', 'in', 'kHz', 'kPaa', 'kg/m3', 'm', 'mV', 'mm', 'ms', 'nT', 'ohmm', 'ppm', 'psi', 'psig', 'rpm', 's', 'us', 'us/m']
    Missing code: ['$/da', 'cptm', 'deg', 'f-p', 'fph', 'hr', 'kgm3', 'klb', 'lbpf', 'lbs', 'm/hr', 'mmo/m', 'mpm', 'mptm', 'pH', 'pa', 'ppg', 'psia', 's/qt', 'sec', 'sg', 'spf', 'spl', 'spqt', 'ucts', 'uspf']
      Found standard form: ['0.1 in', 'Hz', 'N', 'cP', 'deg', 'degC', 'degF', 'ft', 'g', 'in', 'kHz', 'kg/m3', 'm', 'mm', 'ms', 'nT', 'ppm', 'psi', 's', 'us', 'us/m']
    Missing standard form: ['', '$/da', '%', 'cps', 'cptm', 'f-p', 'fph', 'g/cc', 'gpm', 'hr', 'kPaa', 'kgm3', 'klb', 'lbpf', 'lbs', 'm/hr', 'mV', 'mmo/m', 'mpm', 'mptm', 'ohmm', 'pH', 'pa', 'ppg', 'psia', 'psig', 'rpm', 's/qt', 'sec', 'sg', 'spf', 'spl', 'spqt', 'ucts', 'uspf']

    Producer code: 440
      Found code: ['', '%', '0.01 degF/ft', '0.1 in', '0.5 ms', '1/s', '1000 1/s', '1000 ft.lbf', '1000 kPa.s/m', '1000 kgf', '1000 lbf', '1000 lbm', '1E-4 cm2/s', '1E-5 Oe', '1E-6 1/Pa', '1E-6 1/psi', 'A', 'A/m', 'Hz', 'K', 'Mrayl', 'N', 'Oe', 'V', 'bbl', 'c/min', 'cP', 'cm', 'cm3', 'cm3/h', 'cm3/min', 'cm3/s', 'cu', 'd', 'dAPI', 'dB', 'dB/m', 'degC', 'degC/km', 'degC/m', 'degF', 'degF/ft', 'ft', 'ft/h', 'ft/s2', 'ft3', 'ft3/bbl', 'ft3/ft3', 'g', 'g/cm3', 'gAPI', 'gn', 'h', 'in', 'kHz', 'kN.m', 'kPa', 'kPa/h', 'keV', 'kg', 'kg/m', 'kg/m3', 'kgf/kgf', 'kohm', 'lbf', 'lbf/lbf', 'lbm', 'lbm/ft', 'lbm/gal', 'lbm/min', 'm', 'm/h', 'm/min', 'm/s', 'm/s2', 'm2/g', 'm3', 'm3/m3', 'mA', 'mD', 'mD.ft', 'mD/cP', 'mPa.s', 'mS/m', 'mT', 'mV', 'mV/m', 'mbar', 'mgn', 'min', 'mm', 'mm2', 'mol/kg', 'ms', 'nT', 'nW', 'nm', 'ohm', 'ohm.m', 'ppk', 'ppm', 'psi', 'psi/h', 'pu', 'rad/ft3', 'rad/m3', 's', 's/m3', 'uA', 'uV', 'us', 'us/ft', 'us/m']
    Missing code: ['96.487 C/g', 'deg']
      Found standard form: ['0.01 degF/ft', '0.1 in', '0.5 ms', '1/s', '1000 1/s', '1000 ft.lbf', '1000 kgf', '1000 lbf', '1000 lbm', '1E-4 cm2/s', '1E-5 Oe', '1E-6 1/Pa', '1E-6 1/psi', 'A', 'A/m', 'Hz', 'K', 'N', 'Oe', 'V', 'bbl', 'c/min', 'cP', 'cm', 'cm3', 'cm3/h', 'cm3/min', 'cm3/s', 'cu', 'd', 'dAPI', 'dB', 'dB/m', 'deg', 'degC', 'degC/km', 'degC/m', 'degF', 'degF/ft', 'ft', 'ft/h', 'ft/s2', 'ft3', 'ft3/bbl', 'ft3/ft3', 'g', 'g/cm3', 'gAPI', 'h', 'in', 'kHz', 'kN.m', 'kPa', 'kPa/h', 'keV', 'kg', 'kg/m', 'kg/m3', 'kgf/kgf', 'kohm', 'lbf', 'lbf/lbf', 'lbm', 'lbm/ft', 'lbm/gal', 'lbm/min', 'm', 'm/h', 'm/min', 'm/s', 'm/s2', 'm2/g', 'm3', 'm3/m3', 'mD', 'mD.ft', 'mD/cP', 'mPa.s', 'mS/m', 'mT', 'mV/m', 'min', 'mm', 'mm2', 'mol/kg', 'ms', 'nT', 'nW', 'nm', 'ohm', 'ohm.m', 'ppk', 'ppm', 'psi', 'psi/h', 'pu', 'rad/ft3', 'rad/m3', 's', 's/m3', 'uA', 'uV', 'us', 'us/ft', 'us/m']
    Missing standard form: ['', '%', '1000 kPa.s/m', '96.487 C/g', 'Mrayl', 'gn', 'mA', 'mV', 'mbar', 'mgn']

"""
import collections
import contextlib
import logging
import os
import pprint
import sys
import time
import typing

from TotalDepth.RP66V1 import ExceptionTotalDepthRP66V1
from TotalDepth.common import cmn_cmd_opts
from TotalDepth.common import units
from TotalDepth.common import xml
from TotalDepth.util.DirWalk import dirWalk


__author__  = 'Paul Ross'
__date__    = '2020-08-29'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2020 Paul Ross. All rights reserved.'


logger = logging.getLogger(__file__)


FileResult = collections.namedtuple('IndexResult', 'size_input, time, exception, ignored')


class AggregateCounts:

    def __init__(self):
        self.prod_code_names = collections.defaultdict(collections.Counter)
        self.prod_code_parameters = collections.defaultdict(collections.Counter)
        # self.prod_code_parameter_units = collections.defaultdict(collections.Counter)
        self.prod_code_channels = collections.defaultdict(collections.Counter)
        self.prod_code_channel_units = collections.defaultdict(collections.Counter)
        self.prod_code_attribute_units = collections.defaultdict(collections.Counter)

    def add_producer_code(self, producer_code: int, producer_name: str) -> None:
        self.prod_code_names[producer_code].update([producer_name])

    def _add_parameter_eflr(self, producer_code: int, eflr: xml.etree.Element) -> None:
        for object_node in eflr.findall('Object'):
            for attribute in object_node.findall('Attribute'):
                if attribute.attrib['label'] == 'LONG-NAME':
                    self.prod_code_parameters[producer_code].update([_get_value(attribute)])

    def _add_channel_eflr(self, producer_code: int, eflr: xml.etree.Element) -> None:
        #       <EFLR lr_type="3" lrsh_position="0x12c6" object_count="5" set_name="" set_type="CHANNEL" vr_position="0x50">
        #         <Object C="0" I="DEPT" O="2">
        #           <Attribute count="1" label="LONG-NAME" rc="20" rc_ascii="ASCII" units="">
        #             <Value type="bytes" value="DEPT/Depth"/>
        #           </Attribute>
        #           ...
        #           <Attribute count="1" label="UNITS" rc="27" rc_ascii="UNITS" units="">
        #             <Value type="bytes" value="m"/>
        #           </Attribute>
        #           ...
        #         </Object>
        for object_node in eflr.findall('Object'):
            self.prod_code_channels[producer_code].update([object_node.attrib['I']])
            for attribute in object_node.findall('Attribute'):
                if attribute.attrib['label'] == 'UNITS':
                    self.prod_code_channel_units[producer_code].update([_get_value(attribute)])

    def add_logical_file(self, producer_code, logical_file: xml.etree.Element) -> None:
        for child in logical_file.findall('EFLR'):
            if child.attrib['set_type'] == 'CHANNEL':
                self._add_channel_eflr(producer_code, child)
            if child.attrib['set_type'] == 'PARAMETER':
                self._add_parameter_eflr(producer_code, child)
        for child in logical_file.iter():
            if child.tag == 'Attribute':
                self.prod_code_attribute_units[producer_code].update([child.attrib['units'].strip()])


def _get_value(attribute: xml.etree.Element) -> str:
    ret = []
    for child in attribute:
        if child.tag == 'Value':
            ret.append(child.get('value').strip())
    return ''.join(ret)


def _get_producer_code_and_name(logical_file_elem: xml.etree.Element) -> typing.Tuple[int, str]:
    #       <EFLR lr_type="1" lrsh_position="0xd0" object_count="1" set_name="" set_type="ORIGIN" vr_position="0x50">
    #         <Object C="0" I="0" O="2">
    #           <Attribute count="1" label="PRODUCER-CODE" rc="16" rc_ascii="UNORM" units="">
    #             <Value type="int" value="280"/>
    #           </Attribute>
    #           ...
    #           <Attribute count="1" label="PRODUCER-NAME" rc="20" rc_ascii="ASCII" units="">
    #             <Value type="bytes" value="Halliburton"/>
    #           </Attribute>
    #         </Object>
    #       </EFLR>
    producer_code = -1
    producer_name = ''
    for eflr in logical_file_elem.findall('EFLR'):
        if eflr.attrib['set_type'] == 'ORIGIN':
            object_elem = eflr.findall('Object')[0]
            for attribute in object_elem.findall('Attribute'):
                if attribute.attrib['label'] == 'PRODUCER-CODE':
                    producer_code = int(_get_value(attribute))
                elif attribute.attrib['label'] == 'PRODUCER-NAME':
                    producer_name = _get_value(attribute)
    return producer_code, producer_name


def _analyse_logical_files(root: xml.etree.Element, accumulator: AggregateCounts):
    logical_files_elements = root.findall('LogicalFiles')
    if len(logical_files_elements) != 1:
        raise ValueError(f'Expected one element not {len(logical_files_elements)}')
    for logical_file in logical_files_elements[0].findall('LogicalFile'):
        producer_code, producer_name = _get_producer_code_and_name(logical_file)
        accumulator.add_producer_code(producer_code, producer_name)
        accumulator.add_logical_file(producer_code, logical_file)


def read_a_single_file(xml_path_in: str, accumulator: AggregateCounts) -> FileResult:
    """
    Reads a single XML index and analyses it.
    """
    logger.info(f'Reading XML index: {xml_path_in}')
    xml_size = os.path.getsize(xml_path_in)
    try:
        t_start = time.perf_counter()
        try:
            # Faster but stricter
            tree = xml.etree.parse(xml_path_in)
        except xml.etree.XMLSyntaxError as err:
            logger.info('XML Syntax error %s, trying with recover=True', err)
            parser = xml.etree.XMLParser(recover=True)
            tree = xml.etree.parse(xml_path_in, parser=parser)
        root = tree.getroot()
        if root.tag != 'RP66V1FileIndex':
            raise ExceptionTotalDepthRP66V1(f'Root tag is {root.tag}')
        _analyse_logical_files(root, accumulator)
        ret = FileResult(xml_size, time.perf_counter() - t_start, False, False)
        return ret
    except ExceptionTotalDepthRP66V1:
        logger.exception(f'Failed to index with ExceptionTotalDepthRP66V1: {xml_path_in}')
        return FileResult(xml_size, 0.0, True, False)
    except Exception:
        logger.exception(f'Failed to index with Exception: {xml_path_in}')
        return FileResult(xml_size, 0.0, True, False)


def read_index_dir_or_file(path_in: str, recurse: bool, accumulator: AggregateCounts) -> typing.Dict[str, FileResult]:
    logging.info(f'index_dir_or_file(): "{path_in}" recurse: {recurse}')
    ret = {}
    if os.path.isdir(path_in):
        for file_in_out in dirWalk(path_in, theFnMatch='', recursive=recurse, bigFirst=False):
            if os.path.splitext(file_in_out.filePathIn)[1] == '.xml':
                ret[file_in_out.filePathIn] = read_a_single_file(file_in_out.filePathIn, accumulator)
    else:
        if os.path.splitext(path_in)[1] == '.xml':
            ret[path_in] = read_a_single_file(path_in, accumulator)
    return ret


@contextlib.contextmanager
def title(message: str):
    print(f' {message} '.center(75, '='))
    yield
    print(f' DONE: {message} '.center(75, '='))


def analyse_result(acc: AggregateCounts, include_parameters: bool, include_channels: bool) -> None:
    def _pprint(cntr: collections.defaultdict(collections.Counter)) -> None:
        key_width = 2
        for code in cntr:
            w = max(len(k) for k in cntr[code])
            if w > key_width:
                key_width = w
        for code in sorted(cntr.keys()):
            keys = sorted(cntr[code])
            print(f'Producer code: {code} keys: {keys}')
            for key in keys:
                print(f'{code:3d} {key:{key_width}} : {cntr[code][key]:16,d}')

    with title('Producer Code Names'):
        _pprint(acc.prod_code_names)
    if include_parameters:
        with title('Producer Code Parameters'):
            _pprint(acc.prod_code_parameters)
    if include_channels:
        with title('Producer Code Channels'):
            _pprint(acc.prod_code_channels)
    with title('Producer Code Channel Units'):
        _pprint(acc.prod_code_channel_units)
    with title('Producer Code Attribute Units'):
        _pprint(acc.prod_code_attribute_units)


def _check_against_osdd_units(cntr) -> None:
    for code in sorted(cntr.keys()):
        keys = sorted(cntr[code])
        print(f'Producer code: {code}')
        unit_codes_found = set()
        unit_codes_missing = set()
        for key in keys:
            if units.has_slb_units(key):
                unit_codes_found.add(key)
            else:
                unit_codes_missing.add(key)
        print(f'  Found code: {sorted(unit_codes_found)}')
        print(f'Missing code: {sorted(unit_codes_missing)}')
        unit_codes_found = set()
        unit_codes_missing = set()
        for key in keys:
            if units.has_slb_standard_form(key):
                unit_codes_found.add(key)
            else:
                unit_codes_missing.add(key)
        print(f'  Found standard form: {sorted(unit_codes_found)}')
        print(f'Missing standard form: {sorted(unit_codes_missing)}')


def check_against_osdd_units(acc: AggregateCounts) -> None:
    """Checks which units are in our version of the OSDD."""
    units.slb_load_units()
    print('Channels:')
    _check_against_osdd_units(acc.prod_code_channel_units)
    print('Attributes:')
    _check_against_osdd_units(acc.prod_code_attribute_units)


def main() -> int:
    description = """usage: %(prog)s [options] file
Reads a RP66V1 index XML file and all the data."""
    print('Cmd: %s' % ' '.join(sys.argv))
    parser = cmn_cmd_opts.path_in(desc=description, epilog=__rights__, prog=sys.argv[0])
    # Add arguments that control what we report on
    parser.add_argument("-p", "--parameters", action="store_true", default=False,
                      help="Output Parameter analysis. Default: %(default)s.")
    parser.add_argument("-c", "--channels", action="store_true", default=False,
                      help="Output Channel analysis. Default: %(default)s.")
    cmn_cmd_opts.add_log_level(parser, 20)
    args = parser.parse_args()
    # print('args:', args)
    # return 0
    cmn_cmd_opts.set_log_level(args)
    # Your code here
    clk_start = time.perf_counter()
    accumulator = AggregateCounts()
    result: typing.Dict[str, FileResult] = read_index_dir_or_file(
        args.path_in,
        args.recurse,
        accumulator
    )
    clk_exec = time.perf_counter() - clk_start
    analyse_result(accumulator, args.parameters, args.channels)
    check_against_osdd_units(accumulator)
    size_input = files_processed = files_failed = 0
    try:
        for path in sorted(result.keys()):
            file_result = result[path]
            if file_result.size_input > 0:
                ms_mb = file_result.time * 1000 / (file_result.size_input / 1024 ** 2)
                print(
                    f'{file_result.size_input:16,d}'
                    f' {file_result.time:8.3f} {ms_mb:8.1f} {str(file_result.exception):5}'
                    f' "{path}"'
                )
                size_input += result[path].size_input
                files_processed += 1
                if file_result.exception:
                    files_failed += 1
    except Exception as err:
        logger.exception(str(err))
    print('Execution time = %8.3f (S)' % clk_exec)
    if size_input > 0:
        ms_mb = clk_exec * 1000 / (size_input/ 1024**2)
    else:
        ms_mb = 0.0
    print(f'Out of {len(result):,d} failed {files_failed:,d} files of total size {size_input:,d} input bytes at {ms_mb:.1f} ms/Mb')
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
