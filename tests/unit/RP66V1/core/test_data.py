"""
This contains RP661 test data.
"""
import pytest


BASIC_FILE = (
b'0001V1.00RECORD08192              +++TIF@C:\\INSITE\\Data\\ExpFiles\\VA2456~1.DLI+++'  # Storage Unit Label
b' \x00\xff\x01'  # Visible record [0] at 0x50 length 0x2000 version 0xff01
    b'\x00|\x80\x00'  # LRSH [0/0] 0x54 E len: 124 first: True last: True
        # Logical data length 120 0x78
        b'\xf0\x0bFILE-HEADER4\x0fSEQUENCE-NUMBER\x144\x02ID\x14p\x02\x00\x01'  # Chunk from 0
        b'1!\n0000000001!AHES INSITE.1             '                            # Chunk from 40
        b'                                        '                             # Chunk from 80
    b'\x01\xfc\x81\x01'  # LRSH [1/1] 0xd0 E len: 508 first: True last: True
        # Logical data length 504 0x1f8
        b'\xf0\x06ORIGIN8\x07FILE-ID\x008\rFILE-SET-NAME\x008\x0fFILE'                             # Chunk from 0
        b'-SET-NUMBER\x008\x0bFILE-NUMBER\x008\tFILE-TYPE\x008\x07'                                # Chunk from 40
        b'PRODUCT\x008\x07VERSION\x008\x08PROGRAMS\x008\rCREATION-'                                # Chunk from 80
        b'TIME\x008\x0cORDER-NUMBER\x008\x0eDESCENT-NUMBER\x008\nR'                                # Chunk from 120
        b'UN-NUMBER\x008\x07WELL-ID\x008\tWELL-NAME\x008\nFIELD-'                                  # Chunk from 160
        b'NAME\x008\rPRODUCER-CODE\x008\rPRODUCER-NAME\x008\x07C'                                  # Chunk from 200
        b'OMPANY\x008\x0fNAME-SPACE-NAME\x008\x12NAME-SPACE-VE'                                    # Chunk from 240
        b'RSION\x00p\x02\x00\x010-\x01\x14\x0cHES INSITE.1-\x01\x13$BURU ENER'                     # Chunk from 280
        b'GY LIMITED/VALHALLA NORTH 1-\x01\x12\xcfV\xccU-\x01\x12\x01-\x01'                        # Chunk from 320
        b'\x13\x08PLAYBACK-\x01\x14\nHES INSITE-\x01\x14\x06R5.1.4\x00-\x01\x15p\x03'              # Chunk from 360
        b'\x07\n\x001\x00\x00-\x01\x14\x079262611\x00\x00-\x01\x14\x03N/A-\x01\x14\x10VALHALLA N'  # Chunk from 400
        b'ORTH 1-\x01\x14\x08VALHALLA-\x01\x10\x01\x18-\x01\x14\x0bHalliburton-\x01'               # Chunk from 440
        b'\x14\x13BURU ENERGY LIMITED\x00\x00\x01'                                                 # Chunk from 480
    b'\x00\xcc\x81\x04'  # LRSH [2/2] 0x2cc E len: 204 first: True last: True
        # Logical data length 200 0xc8
        b'\xf0\x05FRAME<\x0bDESCRIPTION\x00\x14<\x08CHANNELS\x00\x17<\nINDE'                            # Chunk from 0
        b'X-TYPE\x00\x13<\tDIRECTION\x00\x13<\x07SPACING\x00\x07<\tENCRYP'                              # Chunk from 40
        b'TED\x00\x0f<\tINDEX-MIN\x00\x07<\tINDEX-MAX\x00\x07p\x02\x00\x0250\x00)\x05'                  # Chunk from 80
        b'\x02\x00\x04DEPT\x02\x00\x04TENS\x02\x00\x04ETIM\x02\x00\x04DHTN\x02\x00\x02GR)\x01\x0eBORE'  # Chunk from 120
        b'HOLE-DEPTH)\x01\nINCREASING/\x01\x07\x01m?\xb9\x99\x99\x99\x99\x99\x9a\x00\x00\x00\x01'       # Chunk from 160
    b'\x0b\xdc\x80\x05'  # LRSH [3/3] 0x398 E len: 3036 first: True last: True
        # Logical data length 3032 0xbd8
        b'\xf0\tPARAMETER<\tLONG-NAME\x00\x14<\tDIMENSION\x00\x12<\x04A'                                                  # Chunk from 0
        b'XIS\x00\x17<\x05ZONES\x00\x17<\x06VALUES\x00\x14p\x02\x00\x03LOC-\x01\x14\x08LOCAT'                             # Chunk from 40
        b"ION)\x01\x01\x00\x00-\x01\x14\x1cLATITUDE: 18DEG 01' 32.8'' S"                                                  # Chunk from 80
        b'p\x02\x00\x04SVCO-\x01\x14\rSERVICECONAME)\x01\x01\x00\x00-\x01\x14\x0bHallib'                                  # Chunk from 120
        b'urtonp\x02\x00\x04IQVR-\x01\x14\x0cWLIQ VERSION)\x01\x01\x00\x00-\x01\x14\x06R3'                                # Chunk from 160
        b'.2.0p\x02\x00\x04STAT-\x01\x14\nSTATE NAME)\x01\x01\x00\x00-\x01\x14\x02WAp\x02\x00'                            # Chunk from 200
        b'\x04COUN-\x01\x14\x0cCOUNTRY NAME)\x01\x01\x00\x00-\x01\x14\tAUSTRALIAp'                                        # Chunk from 240
        b'\x02\x00\x03SON-\x01\x14\nJOB NUMBER)\x01\x01\x00\x00-\x01\x14\x079262611p\x02\x00\x04'                         # Chunk from 280
        b'SECT-\x01\x14\x07SECTION)\x01\x01\x00\x00-\x01\x14\x03N/Ap\x02\x00\x04TOWN-\x01\x14\x08T'                       # Chunk from 320
        b'OWNSHIP)\x01\x01\x00\x00-\x01\x14\x03N/Ap\x02\x00\x04RANG-\x01\x14\x05RANGE)\x01\x01\x00'                       # Chunk from 360
        b'\x00-\x01\x14\x03N/Ap\x02\x00\x04APIN-\x01\x14\x07API S/N)\x01\x01\x00\x00-\x01\x14\x03N/Ap'                    # Chunk from 400
        b'\x02\x00\x02CN-\x01\x14\rCUSTOMER NAME)\x01\x01\x00\x00-\x01\x14\x13BURU ENER'                                  # Chunk from 440
        b'GY LIMITEDp\x02\x00\x02WN-\x01\x14\tWELL NAME)\x01\x01\x00\x00-\x01\x14\x10VA'                                  # Chunk from 480
        b'LHALLA NORTH 1p\x02\x00\x02FN-\x01\x14\nFIELD NAME)\x01\x01\x00\x00-'                                           # Chunk from 520
        b'\x01\x14\x08VALHALLAp\x02\x00\x03RIG-\x01\x14\x08RIG NAME)\x01\x01\x00\x00-\x01\x14\x0eE'                       # Chunk from 560
        b'NSIGN RIG #32p\x02\x00\x04PDAT-\x01\x14\x0fPERMANENT DATUM'                                                     # Chunk from 600
        b')\x01\x01\x00\x00-\x01\x14\x03MSLp\x02\x00\x03LMF-\x01\x14\rLOG MEAS FROM)\x01\x01\x00'                         # Chunk from 640
        b'\x00-\x01\x14\x02RTp\x02\x00\x03DMF-\x01\x14\x0fDRILL MEAS FROM)\x01\x01\x00\x00-\x01'                          # Chunk from 680
        b'\x14\x02RTp\x02\x00\x03FL1-\x01\x14\rLOCATIONLINE1)\x01\x01\x00\x00-\x01\x14\x1cLAT'                            # Chunk from 720
        b"ITUDE: 18DEG 01' 32.8'' Sp\x02\x00\x03FL2-\x01\x14\rLOCA"                                                       # Chunk from 760
        b"TIONLINE2)\x01\x01\x00\x00-\x01\x14\x1eLONGITUDE: 124DEG 43' "                                                  # Chunk from 800
        b"47.1'' Ep\x02\x00\x03FL3-\x01\x14\rLOCATIONLINE3)\x01\x01\x00\x00-\x01\x14"                                     # Chunk from 840
        b'\x0fEASTING: 683112p\x02\x00\x03FL4-\x01\x14\rLOCATIONLINE4'                                                    # Chunk from 880
        b')\x01\x01\x00\x00-\x01\x14\x11NORTHING: 8006107p\x02\x00\x03FL5-\x01\x14\rLOC'                                  # Chunk from 920
        b'ATIONLINE5)\x01\x01\x00\x00-\x01\x14\x0bGDA ZONE 51p\x02\x00\x04DATE-\x01'                                      # Chunk from 960
        b'\x14\x04DATE)\x01\x01\x00\x00-\x01\x14\x0b06-Mar-2012p\x02\x00\x03LCC-\x01\x14\rPRO'                            # Chunk from 1000
        b'DUCER-CODE)\x01\x01\x00\x00-\x01\x14\x03280p\x02\x00\x03EDF-\x01\x14\x07DF ELEV'                                # Chunk from 1040
        b')\x01\x01\x00\x00/\x01\x02\x01mB\xe5\xcc\xcdp\x02\x00\x03EPD-\x01\x14\tELEVATION)\x01\x01\x00\x00/'             # Chunk from 1080
        b'\x01\x02\x01m\x00\x00\x00\x00p\x02\x00\x03EGL-\x01\x14\x07GL ELEV)\x01\x01\x00\x00/\x01\x02\x01mB\xda\x00\x00'  # Chunk from 1120
        b'p\x02\x00\x04GVFD-\x01\x14\rGRAVITY FIELD)\x01\x01\x00\x00/\x01\x02\x01g?\x80\x00\x00p'                         # Chunk from 1160
        b'\x02\x00\x03EKB-\x01\x14\x07KB ELEV)\x01\x01\x00\x00/\x01\x02\x01mB\xe5\xcc\xcdp\x02\x00\x04TVDS-'              # Chunk from 1200
        b'\x01\x14\x0eTVDSS CORRECTN)\x01\x01\x00\x00/\x01\x02\x01m@\xbc\xcc\xcep\x02\x00\x03APD-\x01'                    # Chunk from 1240
        b'\x14\x0eDEPTH ABOVE PD)\x01\x01\x00\x00/\x01\x02\x01m@\xbc\xcc\xcep\x02\x00\x04DDEV-\x01'                       # Chunk from 1280
        b'\x14\x07MAX INC)\x01\x01\x00\x00/\x01\x02\x03deg?\xe8\xf5\xc3p\x02\x00\x04DDEG-\x01\x14\rMAX'                   # Chunk from 1320
        b' INC DEPTH)\x01\x01\x00\x00/\x01\x02\x01mE\x0b\x12\xb8p\x02\x00\x11DEP_Serial_N'                                # Chunk from 1360
        b'umber-\x01\x14\x19Depth Panel Serial Number)\x01\x01\x00\x00-'                                                  # Chunk from 1400
        b'\x01\x14\x06PROT01p\x02\x00\x0eDEP_Tool_Class-\x01\x14\x16Depth Pan'                                            # Chunk from 1440
        b'el Tool Class)\x01\x01\x00\x00-\x01\x14\x0eSurface Panelsp\x02\x00\x0c'                                         # Chunk from 1480
        b'DEP_Max_Temp-\x01\x14\x14Depth Panel Max Temp)\x01\x01\x00'                                                     # Chunk from 1520
        b'\x00/\x01\x02\x04degCBC\x99\x9ap\x02\x00\rDEP_Max_Speed-\x01\x14\x15Depth '                                     # Chunk from 1560
        b'Panel Max Speed)\x01\x01\x00\x00/\x01\x02\x03mpm\x00\x00\x00\x00p\x02\x00\x10DEP_M'                             # Chunk from 1600
        b'ax_Pressure-\x01\x14\x18Depth Panel Max Pressure)'                                                              # Chunk from 1640
        b'\x01\x01\x00\x00/\x01\x02\x04psia\x00\x00\x00\x00p\x02\x00\x0fDEP_Tool_Length-\x01\x14\x17D'                    # Chunk from 1680
        b'epth Panel Tool Length)\x01\x01\x00\x00/\x01\x02\x01m\x00\x00\x00\x00p\x02\x00\x11'                             # Chunk from 1720
        b'DEP_Tool_Diameter-\x01\x14\x19Depth Panel Tool Di'                                                              # Chunk from 1760
        b'ameter)\x01\x01\x00\x00/\x01\x02\x02mm\x00\x00\x00\x00p\x02\x00\x0fDEP_Tool_Weight'                             # Chunk from 1800
        b'-\x01\x14\x17Depth Panel Tool Weight)\x01\x01\x00\x00/\x01\x02\x03lbs\x00'                                      # Chunk from 1840
        b'\x00\x00\x00p\x02\x00\x0cDEP_Position-\x01\x14\x14Depth Panel Posit'                                            # Chunk from 1880
        b'ion)\x01\x01\x00\x00/\x01\x02\x01m\x00\x00\x00\x00p\x02\x00\x12RWCH_Serial_Number-'                             # Chunk from 1920
        b'\x01\x14\x12RWCH Serial Number)\x01\x01\x00\x00-\x01\x14\x0811435221p\x02'                                      # Chunk from 1960
        b'\x00\x0fRWCH_Tool_Class-\x01\x14\x0fRWCH Tool Class)\x01\x01\x00'                                               # Chunk from 2000
        b'\x00-\x01\x14\nCable Headp\x02\x00\rRWCH_Max_Temp-\x01\x14\rRWCH'                                               # Chunk from 2040
        b' Max Temp)\x01\x01\x00\x00/\x01\x02\x04degCCLffp\x02\x00\x0eRWCH_Max_S'                                         # Chunk from 2080
        b'peed-\x01\x14\x0eRWCH Max Speed)\x01\x01\x00\x00/\x01\x02\x03mpmB\xb6\x00\x00p\x02'                             # Chunk from 2120
        b'\x00\x11RWCH_Max_Pressure-\x01\x14\x11RWCH Max Pressure'                                                        # Chunk from 2160
        b')\x01\x01\x00\x00/\x01\x02\x04psiaF\x9c@\x00p\x02\x00\x10RWCH_Tool_Length-\x01\x14'                             # Chunk from 2200
        b'\x10RWCH Tool Length)\x01\x01\x00\x00/\x01\x02\x01m?\xf333p\x02\x00\x12RWCH_'                                   # Chunk from 2240
        b'Tool_Diameter-\x01\x14\x12RWCH Tool Diameter)\x01\x01\x00\x00'                                                  # Chunk from 2280
        b'/\x01\x02\x02mmB\xb8&fp\x02\x00\x10RWCH_Tool_Weight-\x01\x14\x10RWCH T'                                         # Chunk from 2320
        b'ool Weight)\x01\x01\x00\x00/\x01\x02\x03lbsC\x07\x00\x00p\x02\x00\rRWCH_Posit'                                  # Chunk from 2360
        b'ion-\x01\x14\rRWCH Position)\x01\x01\x00\x00/\x01\x02\x01m\x00\x00\x00\x00p\x02\x00\x11RW'                      # Chunk from 2400
        b'CH_Accum_Length-\x01\x14\x11RWCH Accum Length)\x01\x01\x00'                                                     # Chunk from 2440
        b'\x00/\x01\x02\x01mB\n\xe1Hp\x02\x00\x12D4TG_Serial_Number-\x01\x14\x12D4TG'                                     # Chunk from 2480
        b' Serial Number)\x01\x01\x00\x00-\x01\x14\x03434p\x02\x00\x0fD4TG_Tool_'                                         # Chunk from 2520
        b'Class-\x01\x14\x0fD4TG Tool Class)\x01\x01\x00\x00-\x01\x14\x04DITSp\x02\x00'                                   # Chunk from 2560
        b'\rD4TG_Max_Temp-\x01\x14\rD4TG Max Temp)\x01\x01\x00\x00/\x01\x02\x04'                                          # Chunk from 2600
        b'degCC0\xb33p\x02\x00\x0eD4TG_Max_Speed-\x01\x14\x0eD4TG Max S'                                                  # Chunk from 2640
        b'peed)\x01\x01\x00\x00/\x01\x02\x03mpmA\x90\x00\x00p\x02\x00\x11D4TG_Max_Pressur'                                # Chunk from 2680
        b'e-\x01\x14\x11D4TG Max Pressure)\x01\x01\x00\x00/\x01\x02\x04psiaF\x9c@\x00p'                                   # Chunk from 2720
        b'\x02\x00\x10D4TG_Tool_Length-\x01\x14\x10D4TG Tool Length)'                                                     # Chunk from 2760
        b'\x01\x01\x00\x00/\x01\x02\x01m@\x0333p\x02\x00\x12D4TG_Tool_Diameter-\x01\x14\x12D'                             # Chunk from 2800
        b'4TG Tool Diameter)\x01\x01\x00\x00/\x01\x02\x02mmB\xb8&fp\x02\x00\x10D4TG'                                      # Chunk from 2840
        b'_Tool_Weight-\x01\x14\x10D4TG Tool Weight)\x01\x01\x00\x00/\x01\x02'                                            # Chunk from 2880
        b'\x03lbsB\xdc\x00\x00p\x02\x00\rD4TG_Position-\x01\x14\rD4TG Positi'                                             # Chunk from 2920
        b'on)\x01\x01\x00\x00/\x01\x02\x01m\x00\x00\x00\x00p\x02\x00\x11D4TG_Accum_Length-\x01\x14'                       # Chunk from 2960
        b'\x11D4TG Accum Length)\x01\x01\x00\x00/\x01\x02\x01mA\xdd\x1e\xb8'                                              # Chunk from 3000
    b'\x03R\x80\x05'  # LRSH [4/4] 0xf74 E len: 850 first: True last: True
        # Logical data length 846 0x34e
        b'\xf0\x04TOOL<\x0bDESCRIPTION\x00\x14<\x0eTRADEMARK-NAME\x00\x14<'                  # Chunk from 0
        b'\x0cGENERIC-NAME\x00\x14<\x05PARTS\x00\x17<\x06STATUS\x00\x1a<\x08CHAN'            # Chunk from 40
        b'NELS\x00\x17<\nPARAMETERS\x00\x17p\x02\x00\x03DEP)\x01 Depth Pane'                 # Chunk from 80
        b'l for WL Insite System)\x01\x0bDepth_Panel)\x01\x03D'                              # Chunk from 120
        b'EP\x00)\x01\x01)\x02\x02\x00\x04TENS\x02\x00\x04ETIM)\t\x02\x00\x11DEP_Serial_Nu'  # Chunk from 160
        b'mber\x02\x00\x0eDEP_Tool_Class\x02\x00\x0cDEP_Max_Temp\x02\x00\rD'                 # Chunk from 200
        b'EP_Max_Speed\x02\x00\x10DEP_Max_Pressure\x02\x00\x0fDEP_To'                        # Chunk from 240
        b'ol_Length\x02\x00\x11DEP_Tool_Diameter\x02\x00\x0fDEP_Tool'                        # Chunk from 280
        b'_Weight\x02\x00\x0cDEP_Positionp\x02\x00\x04RWCH)\x01\x1eReleasa'                  # Chunk from 320
        b'ble Wireline Cable Head)\x01\x04RWCH)\x01\x04RWCH\x00)\x01'                        # Chunk from 360
        b'\x01)\x01\x02\x00\x04DHTN)\n\x02\x00\x12RWCH_Serial_Number\x02\x00\x0fRWCH'        # Chunk from 400
        b'_Tool_Class\x02\x00\rRWCH_Max_Temp\x02\x00\x0eRWCH_Max_S'                          # Chunk from 440
        b'peed\x02\x00\x11RWCH_Max_Pressure\x02\x00\x10RWCH_Tool_Len'                        # Chunk from 480
        b'gth\x02\x00\x12RWCH_Tool_Diameter\x02\x00\x10RWCH_Tool_Wei'                        # Chunk from 520
        b'ght\x02\x00\rRWCH_Position\x02\x00\x11RWCH_Accum_Lengthp'                          # Chunk from 560
        b'\x02\x00\x04D4TG)\x01\x16DITS 4 Telemetry Gamma)\x01\x04D4TG)'                     # Chunk from 600
        b'\x01\x04D4TG\x00)\x01\x01)\x01\x02\x00\x02GR)\n\x02\x00\x12D4TG_Serial_Number'     # Chunk from 640
        b'\x02\x00\x0fD4TG_Tool_Class\x02\x00\rD4TG_Max_Temp\x02\x00\x0eD4T'                 # Chunk from 680
        b'G_Max_Speed\x02\x00\x11D4TG_Max_Pressure\x02\x00\x10D4TG_T'                        # Chunk from 720
        b'ool_Length\x02\x00\x12D4TG_Tool_Diameter\x02\x00\x10D4TG_T'                        # Chunk from 760
        b'ool_Weight\x02\x00\rD4TG_Position\x02\x00\x11D4TG_Accum_'                          # Chunk from 800
        b'Length'                                                                            # Chunk from 840
    b'\x01~\x80\x03'  # LRSH [5/5] 0x12c6 E len: 382 first: True last: True
        # Logical data length 378 0x17a
        b'\xf0\x07CHANNEL<\tLONG-NAME\x00\x14<\nPROPERTIES\x00\x13<\x13RE'                                    # Chunk from 0
        b'PRESENTATION-CODE\x00\x0f<\tDIMENSION\x00\x12<\rELEMEN'                                             # Chunk from 40
        b'T-LIMIT\x00\x12<\x05UNITS\x00\x1b<\x04AXIS\x00\x17<\x06SOURCE\x00\x18p\x02\x00\x04'                 # Chunk from 80
        b'DEPT-\x01\x14\nDEPT/Depth\x00)\x01\x07)\x01\x01)\x01\x01)\x01\x01m\x00\x00p\x02\x00\x04TE'          # Chunk from 120
        b'NS-\x01\x14\x0cTENS/Tension\x00)\x01\x02)\x01\x01)\x01\x01)\x01\x03lbs\x00)\x01\x04TO'              # Chunk from 160
        b'OL\x02\x00\x03DEPp\x02\x00\x04ETIM-\x01\x14\x11ETIM/Elapsed Time\x00)\x01'                          # Chunk from 200
        b'\x07)\x01\x01)\x01\x01)\x01\x03min\x00)\x01\x04TOOL\x02\x00\x03DEPp\x02\x00\x04DHTN-\x01\x14\x0fD'  # Chunk from 240
        b'HTN/CH Tension\x00)\x01\x02)\x01\x01)\x01\x01)\x01\x03lbs\x00)\x01\x04TOOL\x02\x00'                 # Chunk from 280
        b'\x04RWCHp\x02\x00\x02GR-\x01\x14\x0cGR/Gamma API\x00)\x01\x02)\x01\x01)\x01\x01)\x01\x03'           # Chunk from 320
        b'api\x00)\x01\x04TOOL\x02\x00\x04D4TG'                                                               # Chunk from 360
    b'\x00\xa2\x80\x80'  # LRSH [6/6] 0x1444 E len: 162 first: True last: True
        # Logical data length 158 0x9e
        b'\xf0\x12280-FRAMESTEP-INFO<\x0bDESCRIPTION\x00\x14<\x07SPA'                                  # Chunk from 0
        b'CING\x00\x07<\x06ISPEED\x00\x11<\tDIRECTION\x00\x13p\x02\x00\x0251)\x01/Id'                  # Chunk from 40
        b'entify Packing Relationships of FRAME ob'                                                    # Chunk from 80
        b'jects/\x01\x07\x01m?\xb9\x99\x99\x99\x99\x99\x9a-\x01\x11\x00\x00\x00\x01)\x01\nINCREASING'  # Chunk from 120
    b'\x06\x9c\x81\x06'  # LRSH [7/7] 0x14e6 E len: 1692 first: True last: True
        # Logical data length 1688 0x698
        b'\xf0\x07COMMENT<\x04TEXT\x00\x14p\x02\x00\x0252)\x01\x86|Location     '  # Chunk from 0
        b"        - LATITUDE: 18DEG 01' 32.8'' S\r\n"                              # Chunk from 40
        b'ServiceCoName        -                Ha'                                # Chunk from 80
        b'lliburton\r\nWLIQ Version         -       '                              # Chunk from 120
        b'              R3.2.0\r\nState Name        '                              # Chunk from 160
        b'   -                         WA\r\nCountry'                              # Chunk from 200
        b' Name         -                  AUSTRAL'                                # Chunk from 240
        b'IA\r\nJob Number           -              '                              # Chunk from 280
        b'      9262611\r\nSection              -   '                              # Chunk from 320
        b'                     N/A\r\nTownship      '                              # Chunk from 360
        b'       -                        N/A\r\nRan'                              # Chunk from 400
        b'ge                -                     '                                # Chunk from 440
        b'   N/A\r\nAPI S/N              -          '                              # Chunk from 480
        b'              N/A\r\nDF Elev              '                              # Chunk from 520
        b'-                    114.900 m\r\nElevatio'                              # Chunk from 560
        b'n            -                      0.00'                                # Chunk from 600
        b'0 m\r\nGL Elev              -             '                              # Chunk from 640
        b'       109.000 m\r\nGravity Field        -'                              # Chunk from 680
        b'                      1.000 g\r\nKB Elev  '                              # Chunk from 720
        b'            -                    114.900'                                # Chunk from 760
        b' m\r\nCustomer Name        -        BURU E'                              # Chunk from 800
        b'NERGY LIMITED\r\nWell Name            -   '                              # Chunk from 840
        b'        VALHALLA NORTH 1\r\nField Name    '                              # Chunk from 880
        b'       -                   VALHALLA\r\nRig'                              # Chunk from 920
        b' Name             -             ENSIGN R'                                # Chunk from 960
        b'IG #32\r\nPermanent Datum      -          '                              # Chunk from 1000
        b'              MSL\r\nLog Meas From        '                              # Chunk from 1040
        b'-                         RT\r\nDrill Meas'                              # Chunk from 1080
        b' From      -                         RT\r'                               # Chunk from 1120
        b'\nTVDss Correctn       -                 '                               # Chunk from 1160
        b'     5.900 m\r\nDepth above PD       -    '                              # Chunk from 1200
        b'                  5.900 m\r\nMax Inc      '                              # Chunk from 1240
        b'        -                      1.820 deg'                                # Chunk from 1280
        b'\r\nMax Inc Depth        -                '                              # Chunk from 1320
        b'   2225.170 m\r\nLocationLine1        - LA'                              # Chunk from 1360
        b"TITUDE: 18DEG 01' 32.8'' S\r\nLocationLine"                              # Chunk from 1400
        b"2        - LONGITUDE: 124DEG 43' 47.1'' "                                # Chunk from 1440
        b'E\r\nLocationLine3        -            EAS'                              # Chunk from 1480
        b'TING: 683112\r\nLocationLine4        -    '                              # Chunk from 1520
        b'      NORTHING: 8006107\r\nLocationLine5  '                              # Chunk from 1560
        b'      -                GDA ZONE 51\r\nDate'                              # Chunk from 1600
        b'                 -                06-Mar'                                # Chunk from 1640
        b'-2012\r\n\x01'                                                           # Chunk from 1680
    b'\x04\xce\xa0\x06'  # LRSH [8/8] 0x1b82 E len: 1230 first: True last: False
        # Logical data length 1226 0x4ca
        b'\xf0\x07COMMENT<\x04TEXT\x00\x14p\x02\x00\x0253)\x01\x86\xd0-START CURVE '  # Chunk from 0
        b'INFORMATION XML-\r\n<xml version = "1" mis'                                 # Chunk from 40
        b'singfloat = "-999.250000" missinginteger'                                   # Chunk from 80
        b' = "-999" missingascii = "" Section_Name'                                   # Chunk from 120
        b' = "RUN Well Based" >\r\n        <curve na'                                 # Chunk from 160
        b'me = "Depth" wellname = "" run = "" reco'                                   # Chunk from 200
        b'rd = "" description = "" unit = "m" unit'                                   # Chunk from 240
        b'type = "Depth" format = "F" size = "8" s'                                   # Chunk from 280
        b'pecialbits = "" decimalplaces = "4" opti'                                   # Chunk from 320
        b'onliststring = "false" XUnit = "" XStart'                                   # Chunk from 360
        b' = "" XEnd = "" YType = "" > </curve>\r\n '                                 # Chunk from 400
        b'       <curve name = "Tension" wellname '                                   # Chunk from 440
        b'= "VALH N1 S6 RDT" run = "Descriptor_run'                                   # Chunk from 480
        b'" record = "R:WLIQ Surface" description '                                   # Chunk from 520
        b'= "Descriptor_data" unit = "lbs" unittyp'                                   # Chunk from 560
        b'e = "Wireline tens" format = "F" size = '                                   # Chunk from 600
        b'"4" specialbits = "" decimalplaces = "1"'                                   # Chunk from 640
        b' optionliststring = "false" XUnit = "" X'                                   # Chunk from 680
        b'Start = "" XEnd = "" YType = "" > </curv'                                   # Chunk from 720
        b'e>\r\n        <curve name = "Elapsed Time"'                                 # Chunk from 760
        b' wellname = "VALH N1 S6 RDT" run = "Desc'                                   # Chunk from 800
        b'riptor_run" record = "R:WLIQ Surface" de'                                   # Chunk from 840
        b'scription = "Descriptor_data" unit = "mi'                                   # Chunk from 880
        b'n" unittype = "Interval time" format = "'                                   # Chunk from 920
        b'F" size = "8" specialbits = "C" decimalp'                                   # Chunk from 960
        b'laces = "-1" optionliststring = "false" '                                   # Chunk from 1000
        b'XUnit = "" XStart = "" XEnd = "" YType ='                                   # Chunk from 1040
        b' "" > </curve>\r\n        <curve name = "D'                                 # Chunk from 1080
        b'H Tension" wellname = "VALH N1 S6 RDT" r'                                   # Chunk from 1120
        b'un = "Descriptor_run" record = "R:DH Ten'                                   # Chunk from 1160
        b'sion" description = "Descr'                                                 # Chunk from 1200
b' \x00\xff\x01'  # Visible record [1] at 0x2050 length 0x2000 version 0xff01
    b'\x02&\xc1\x06'  # LRSH [9/9] 0x2054 E len: 550 first: False last: True
        # Logical data length 546 0x222
        b'iptor_data" unit = "lbs" unittype = "Wir'      # Chunk from 0
        b'eline tens" format = "F" size = "4" spec'      # Chunk from 40
        b'ialbits = "" decimalplaces = "1" optionl'      # Chunk from 80
        b'iststring = "false" XUnit = "" XStart = '      # Chunk from 120
        b'"" XEnd = "" YType = "" > </curve>\r\n    '    # Chunk from 160
        b'    <curve name = "Gamma Ray" wellname ='      # Chunk from 200
        b' "VALH N1 S6 RDT" run = "Descriptor_run"'      # Chunk from 240
        b' record = "R:Gamma Ray" description = "D'      # Chunk from 280
        b'escriptor_data" unit = "api" unittype = '      # Chunk from 320
        b'"API" format = "F" size = "4" specialbit'      # Chunk from 360
        b's = "" decimalplaces = "2" optionliststr'      # Chunk from 400
        b'ing = "false" XUnit = "" XStart = "" XEn'      # Chunk from 440
        b'd = "" YType = "" > </curve>\r\n</xml>\r\n-E'  # Chunk from 480
        b'ND CURVE INFORMATION XML-\x01'                 # Chunk from 520
    b'\x1d\xd6\xa0\x06'  # LRSH [9/10] 0x227a E len: 7638 first: True last: False
        # Logical data length 7634 0x1dd2
        b'\xf0\x07COMMENT<\x04TEXT\x00\x14p\x02\x00\x0254)\x01\xa82VALH N1 S6 RD'  # Chunk from 0
        b'T\\0001 BURU RDT MAIN SPS\\002 29-Feb-12 0'                              # Chunk from 40
        b'0:54 Up @2955.0m\r\n\r\n\r\n                  '                          # Chunk from 80
        b'                          SERVICE\r\n     '                              # Chunk from 120
        b'                                  BURU R'                                # Chunk from 160
        b'DT MAIN SPS\r\n---------------------------'                              # Chunk from 200
        b'----------------------------------------'                                # Chunk from 240
        b'----------------------------\r\nTool      '                              # Chunk from 280
        b'     Tool Name              Serial      '                                # Chunk from 320
        b' Weight       Length       Length       '                                # Chunk from 360
        b'     \r\nMnemonic                         '                              # Chunk from 400
        b'     Number       (lbs)        (m)      '                                # Chunk from 440
        b'    Accumulation(m)   \r\n----------------'                              # Chunk from 480
        b'----------------------------------------'                                # Chunk from 520
        b'---------------------------------------\r'                               # Chunk from 560
        b'\nRWCH           RWCH                   1'                               # Chunk from 600
        b'1435221     135.00       1.91         34'                                # Chunk from 640
        b'.72             \r\nMCJE           MCEH   '                              # Chunk from 680
        b'                338-074      251.00     '                                # Chunk from 720
        b'  3.08         31.64             \r\nPTMS '                              # Chunk from 760
        b'          PTMS                   686    '                                # Chunk from 800
        b'      110.00       1.95         29.69   '                                # Chunk from 840
        b'          \r\nD4TG           D4TG         '                              # Chunk from 880
        b'          434          110.00       2.05'                                # Chunk from 920
        b'         27.64             \r\nMCEJ       '                              # Chunk from 960
        b'    MCEJ                   338-111      '                                # Chunk from 1000
        b'287.00       3.47         24.17         '                                # Chunk from 1040
        b'    \r\nPTS            PTS                '                              # Chunk from 1080
        b'    718          211.00       2.13      '                                # Chunk from 1120
        b'   22.04             \r\nMCS            MC'                              # Chunk from 1160
        b'S                    118          290.00'                                # Chunk from 1200
        b'       2.71         19.33             \r\n'                              # Chunk from 1240
        b'MRILAB         MRILAB                 17'                                # Chunk from 1280
        b'8          400.00       4.01         15.'                                # Chunk from 1320
        b'32             \r\nMCS1           MCS1    '                              # Chunk from 1360
        b'               125          290.00      '                                # Chunk from 1400
        b' 2.71         12.61             \r\nFPS   '                              # Chunk from 1440
        b'         FPS                    105     '                                # Chunk from 1480
        b'     450.00       3.67         8.94     '                                # Chunk from 1520
        b'         \r\nFLID           FLID          '                              # Chunk from 1560
        b'         FLIDB015_FL1 140.00       1.11 '                                # Chunk from 1600
        b'        7.83              \r\n            '                              # Chunk from 1640
        b'                          5             '                                # Chunk from 1680
        b'                                        '                                # Chunk from 1720
        b'   \r\nSPS            SPS*                '                              # Chunk from 1760
        b'   006          858.10       5.67       '                                # Chunk from 1800
        b'  2.16              \r\nQGS1           QGS'                              # Chunk from 1840
        b'1                   112          102.00 '                                # Chunk from 1880
        b'      1.28         0.88              \r\nC'                              # Chunk from 1920
        b'VS            CVS                    003'                                # Chunk from 1960
        b'          75.00        0.70         0.18'                                # Chunk from 2000
        b'              \r\nCBHD           Cabbage H'                              # Chunk from 2040
        b'ead           001          10.00        '                                # Chunk from 2080
        b'0.18         0.00              \r\n-------'                              # Chunk from 2120
        b'----------------------------------------'                                # Chunk from 2160
        b'----------------------------------------'                                # Chunk from 2200
        b'--------\r\nTotal                         '                              # Chunk from 2240
        b'                     3719.10      36.63 '                                # Chunk from 2280
        b'                         \r\n" * " = Overb'                              # Chunk from 2320
        b'ody Attached\r\n\r\n\r\n                      '                          # Chunk from 2360
        b'                         INPUTS, DELAYS '                                # Chunk from 2400
        b'AND FILTERS\r\n---------------------------'                              # Chunk from 2440
        b'----------------------------------------'                                # Chunk from 2480
        b'----------------------------------------'                                # Chunk from 2520
        b'-------------\r\nMnemonic             Inpu'                              # Chunk from 2560
        b't Description                           '                                # Chunk from 2600
        b'                 Delay        Filter Len'                                # Chunk from 2640
        b'gth Filter Type\r\n                       '                              # Chunk from 2680
        b'                                        '                                # Chunk from 2720
        b'                   (m)          (m)     '                                # Chunk from 2760
        b'                 \r\n---------------------'                              # Chunk from 2800
        b'----------------------------------------'                                # Chunk from 2840
        b'----------------------------------------'                                # Chunk from 2880
        b'-------------------\r\n\r\n                 '                            # Chunk from 2920
        b'                                      De'                                # Chunk from 2960
        b'pth Panel\r\n\r\nTENS                 Tensio'                            # Chunk from 3000
        b'n                                       '                                # Chunk from 3040
        b'               0.000                    '                                # Chunk from 3080
        b'  NO         \r\n\r\n                       '                            # Chunk from 3120
        b'                                   RWCH\r'                               # Chunk from 3160
        b'\n\r\nDHTN                 DownholeTension '                             # Chunk from 3200
        b'                                        '                                # Chunk from 3240
        b'     0.000        0.000         BLK     '                                # Chunk from 3280
        b'   \r\n\r\n                                 '                            # Chunk from 3320
        b'                         D4TG\r\n\r\nACCZ   '                            # Chunk from 3360
        b'              Accelerometer Z           '                                # Chunk from 3400
        b'                                   0.000'                                # Chunk from 3440
        b'        0.025         BLK        \r\nDEVI '                              # Chunk from 3480
        b'                Inclination             '                                # Chunk from 3520
        b'                                     0.0'                                # Chunk from 3560
        b'00                      NO         \r\nTPU'                              # Chunk from 3600
        b'L                 Tension Pull          '                                # Chunk from 3640
        b'                                       2'                                # Chunk from 3680
        b'9.403                     NO         \r\nG'                              # Chunk from 3720
        b'R                   Natural Gamma Ray AP'                                # Chunk from 3760
        b'I                                       '                                # Chunk from 3800
        b' 29.403       0.533         TRI        \r'                               # Chunk from 3840
        b'\nGRU                  Unfiltered Natural'                               # Chunk from 3880
        b' Gamma Ray API                          '                                # Chunk from 3920
        b'   29.403                     NO        '                                # Chunk from 3960
        b' \r\nEGR                  Natural Gamma Ra'                              # Chunk from 4000
        b'y API with Enhanced Vertical Resolution '                                # Chunk from 4040
        b'     29.403       0.432 , 0.229 W       '                                # Chunk from 4080
        b'   \r\n\r\n\r\n                               '                          # Chunk from 4120
        b'                    OUTPUTS\r\n-----------'                              # Chunk from 4160
        b'----------------------------------------'                                # Chunk from 4200
        b'----------------------------------------'                                # Chunk from 4240
        b'-----------------\r\nMnemonic             '                              # Chunk from 4280
        b'Output Description                      '                                # Chunk from 4320
        b'                     Filter Length Filte'                                # Chunk from 4360
        b'r Type \r\n                               '                              # Chunk from 4400
        b'                                        '                                # Chunk from 4440
        b'           (m)                       \r\n-'                              # Chunk from 4480
        b'----------------------------------------'                                # Chunk from 4520
        b'----------------------------------------'                                # Chunk from 4560
        b'---------------------------\r\n\r\n         '                            # Chunk from 4600
        b'                                        '                                # Chunk from 4640
        b'Depth Panel\r\n\r\nTPUL                 Tens'                            # Chunk from 4680
        b'ion Pull                                '                                # Chunk from 4720
        b'                               NO       '                                # Chunk from 4760
        b'   \r\nTENS                 Tension       '                              # Chunk from 4800
        b'                                        '                                # Chunk from 4840
        b'                     NO          \r\nTSW  '                              # Chunk from 4880
        b'                Tool String Weight      '                                # Chunk from 4920
        b'                                        '                                # Chunk from 4960
        b'           NO          \r\nLSPD           '                              # Chunk from 5000
        b'      Line Speed                        '                                # Chunk from 5040
        b'                                        '                                # Chunk from 5080
        b' NO          \r\nBS                   Bit '                              # Chunk from 5120
        b'Size                                    '                                # Chunk from 5160
        b'                               NO       '                                # Chunk from 5200
        b'   \r\nMINM                 Minute Mark Fl'                              # Chunk from 5240
        b'ag                                      '                                # Chunk from 5280
        b'                     NO          \r\nMGMK '                              # Chunk from 5320
        b'                Magnetic Mark Flag      '                                # Chunk from 5360
        b'                                        '                                # Chunk from 5400
        b'           NO          \r\nCSOD           '                              # Chunk from 5440
        b'      Inner Casing OD size              '                                # Chunk from 5480
        b'                                        '                                # Chunk from 5520
        b' NO          \r\nICV                  Inst'                              # Chunk from 5560
        b'rument Cable Voltage                    '                                # Chunk from 5600
        b'                               NO       '                                # Chunk from 5640
        b'   \r\nICA                  Instrument Cab'                              # Chunk from 5680
        b'le Current                              '                                # Chunk from 5720
        b'                     NO          \r\nACV  '                              # Chunk from 5760
        b'                Auxiliary Set Voltage   '                                # Chunk from 5800
        b'                                        '                                # Chunk from 5840
        b'           NO          \r\nTNSR           '                              # Chunk from 5880
        b'      Tension Cal Raw Value             '                                # Chunk from 5920
        b'                                        '                                # Chunk from 5960
        b' NO          \r\nWL1V                 Wire'                              # Chunk from 6000
        b' Line 1 Voltage                         '                                # Chunk from 6040
        b'                               NO       '                                # Chunk from 6080
        b'   \r\nWL2V                 Wire Line 2 Vo'                              # Chunk from 6120
        b'ltage                                   '                                # Chunk from 6160
        b'                     NO          \r\nWL3V '                              # Chunk from 6200
        b'                Wire Line 3 Voltage     '                                # Chunk from 6240
        b'                                        '                                # Chunk from 6280
        b'           NO          \r\nWL4V           '                              # Chunk from 6320
        b'      Wire Line 4 Voltage               '                                # Chunk from 6360
        b'                                        '                                # Chunk from 6400
        b' NO          \r\nWL5V                 Wire'                              # Chunk from 6440
        b' Line 5 Voltage                         '                                # Chunk from 6480
        b'                               NO       '                                # Chunk from 6520
        b'   \r\nWL6V                 Wire Line 6 Vo'                              # Chunk from 6560
        b'ltage                                   '                                # Chunk from 6600
        b'                     NO          \r\nWL1C '                              # Chunk from 6640
        b'                Wire Line 1 Current     '                                # Chunk from 6680
        b'                                        '                                # Chunk from 6720
        b'           NO          \r\nWL2C           '                              # Chunk from 6760
        b'      Wire Line 2 Current               '                                # Chunk from 6800
        b'                                        '                                # Chunk from 6840
        b' NO          \r\nWL3C                 Wire'                              # Chunk from 6880
        b' Line 3 Current                         '                                # Chunk from 6920
        b'                               NO       '                                # Chunk from 6960
        b'   \r\nWL4C                 Wire Line 4 Cu'                              # Chunk from 7000
        b'rrent                                   '                                # Chunk from 7040
        b'                     NO          \r\nWL5C '                              # Chunk from 7080
        b'                Wire Line 5 Current     '                                # Chunk from 7120
        b'                                        '                                # Chunk from 7160
        b'           NO          \r\nWL6C           '                              # Chunk from 7200
        b'      Wire Line 6 Current               '                                # Chunk from 7240
        b'                                        '                                # Chunk from 7280
        b' NO          \r\nWLFC                 Wire'                              # Chunk from 7320
        b' Line Fault Current                     '                                # Chunk from 7360
        b'                               NO       '                                # Chunk from 7400
        b'   \r\n\r\n                                 '                            # Chunk from 7440
        b'                   RWCH\r\n\r\nBTMP         '                            # Chunk from 7480
        b'        BoreHole Temperature            '                                # Chunk from 7520
        b'                             1.295      '                                # Chunk from 7560
        b'   BLK         \r\nDLOD             '                                    # Chunk from 7600
b' \x00\xff\x01'  # Visible record [2] at 0x4050 length 0x2000 version 0xff01
    b'\n\x80\xc1\x06'  # LRSH [10/11] 0x4054 E len: 2688 first: False last: True
        # Logical data length 2684 0xa7c
        b'    Down Hole Load Cell Measurement     '      # Chunk from 0
        b'                                       N'      # Chunk from 40
        b'O          \r\nDHLP                 Down H'    # Chunk from 80
        b'ole Load Cell Positive Measurement      '      # Chunk from 120
        b'                             NO         '      # Chunk from 160
        b' \r\nDHLN                 Down Hole Load C'    # Chunk from 200
        b'ell Negative Measurement                '      # Chunk from 240
        b'                   NO          \r\nDHTN   '    # Chunk from 280
        b'              DownholeTension           '      # Chunk from 320
        b'                                        '      # Chunk from 360
        b'         NO          \r\n\r\n               '  # Chunk from 400
        b'                                     D4T'      # Chunk from 440
        b'G\r\n\r\nACCZ                 Accelerometer '  # Chunk from 480
        b'Z                                       '      # Chunk from 520
        b'                     NO          \r\nDEVI '    # Chunk from 560
        b'                Inclination             '      # Chunk from 600
        b'                                        '      # Chunk from 640
        b'           NO          \r\nBTMP           '    # Chunk from 680
        b'      BoreHole Temperature              '      # Chunk from 720
        b'                                        '      # Chunk from 760
        b' NO          \r\nPLTC                 Plot'    # Chunk from 800
        b' Control Mask                           '      # Chunk from 840
        b'                               NO       '      # Chunk from 880
        b'   \r\nEGR                  Natural Gamma '    # Chunk from 920
        b'Ray API with Enhanced Vertical Resolutio'      # Chunk from 960
        b'n                    NO          \r\nEGRC '    # Chunk from 1000
        b'                Natural Gamma Ray API wi'      # Chunk from 1040
        b'th Enhanced Vertical Resolution and     '      # Chunk from 1080
        b'           NO          \r\n               '    # Chunk from 1120
        b'      BHC                               '      # Chunk from 1160
        b'                                        '      # Chunk from 1200
        b'             \r\nPLTC                 Plot'    # Chunk from 1240
        b' Control Mask                           '      # Chunk from 1280
        b'                               NO       '      # Chunk from 1320
        b'   \r\nBHAB                 Borehole Absor'    # Chunk from 1360
        b'ption                                   '      # Chunk from 1400
        b'                     NO          \r\nBHCN '    # Chunk from 1440
        b'                Borehole Correction     '      # Chunk from 1480
        b'                                        '      # Chunk from 1520
        b'           NO          \r\nICID           '    # Chunk from 1560
        b'      Inner Casing ID                   '      # Chunk from 1600
        b'                                        '      # Chunk from 1640
        b' NO          \r\nKCTN                 Pott'    # Chunk from 1680
        b'asium Correction                        '      # Chunk from 1720
        b'                               NO       '      # Chunk from 1760
        b'   \r\nPLTC                 Plot Control M'    # Chunk from 1800
        b'ask                                     '      # Chunk from 1840
        b'                     NO          \r\nGR   '    # Chunk from 1880
        b'                Natural Gamma Ray API   '      # Chunk from 1920
        b'                                        '      # Chunk from 1960
        b'           NO          \r\nGRCO           '    # Chunk from 2000
        b'      Natural Gamma Ray API Borehole Cor'      # Chunk from 2040
        b'rected                                  '      # Chunk from 2080
        b' NO          \r\nPLTC                 Plot'    # Chunk from 2120
        b' Control Mask                           '      # Chunk from 2160
        b'                               NO       '      # Chunk from 2200
        b'   \r\nBHAB                 Borehole Absor'    # Chunk from 2240
        b'ption                                   '      # Chunk from 2280
        b'                     NO          \r\nBHCN '    # Chunk from 2320
        b'                Borehole Correction     '      # Chunk from 2360
        b'                                        '      # Chunk from 2400
        b'           NO          \r\nICID           '    # Chunk from 2440
        b'      Inner Casing ID                   '      # Chunk from 2480
        b'                                        '      # Chunk from 2520
        b' NO          \r\nKCTN                 Pott'    # Chunk from 2560
        b'asium Correction                        '      # Chunk from 2600
        b'                               NO       '      # Chunk from 2640
        b'   \x01'                                       # Chunk from 2680
    b'\x00&\x00\x00'  # LRSH [10/12] 0x4ad4 I len: 38 first: True last: True
        b'\x02\x00\x0250\x01@\xa6\x92\xcc\xcc\xcc\xcc\xcd\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [11/13] 0x4afa I len: 38 first: True last: True
        b'\x02\x00\x0250\x02@\xa6\x93\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [12/14] 0x4b20 I len: 38 first: True last: True
        b'\x02\x00\x0250\x03@\xa6\x9333333\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [13/15] 0x4b46 I len: 38 first: True last: True
        b'\x02\x00\x0250\x04@\xa6\x93fffff\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [14/16] 0x4b6c I len: 38 first: True last: True
        b'\x02\x00\x0250\x05@\xa6\x93\x99\x99\x99\x99\x99\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [15/17] 0x4b92 I len: 38 first: True last: True
        b'\x02\x00\x0250\x06@\xa6\x93\xcc\xcc\xcc\xcc\xcc\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [16/18] 0x4bb8 I len: 38 first: True last: True
        b'\x02\x00\x0250\x07@\xa6\x93\xff\xff\xff\xff\xff\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [17/19] 0x4bde I len: 38 first: True last: True
        b'\x02\x00\x0250\x08@\xa6\x9433332\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [18/20] 0x4c04 I len: 38 first: True last: True
        b'\x02\x00\x0250\t@\xa6\x94ffffe\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [19/21] 0x4c2a I len: 38 first: True last: True
        b'\x02\x00\x0250\n@\xa6\x94\x99\x99\x99\x99\x98\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [20/22] 0x4c50 I len: 38 first: True last: True
        b'\x02\x00\x0250\x0b@\xa6\x94\xcc\xcc\xcc\xcc\xcb\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [21/23] 0x4c76 I len: 38 first: True last: True
        b'\x02\x00\x0250\x0c@\xa6\x94\xff\xff\xff\xff\xfe\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [22/24] 0x4c9c I len: 38 first: True last: True
        b'\x02\x00\x0250\r@\xa6\x9533331\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [23/25] 0x4cc2 I len: 38 first: True last: True
        b'\x02\x00\x0250\x0e@\xa6\x95ffffd\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [24/26] 0x4ce8 I len: 38 first: True last: True
        b'\x02\x00\x0250\x0f@\xa6\x95\x99\x99\x99\x99\x97\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [25/27] 0x4d0e I len: 38 first: True last: True
        b'\x02\x00\x0250\x10@\xa6\x95\xcc\xcc\xcc\xcc\xca\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [26/28] 0x4d34 I len: 38 first: True last: True
        b'\x02\x00\x0250\x11@\xa6\x95\xff\xff\xff\xff\xfd\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [27/29] 0x4d5a I len: 38 first: True last: True
        b'\x02\x00\x0250\x12@\xa6\x9633330\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [28/30] 0x4d80 I len: 38 first: True last: True
        b'\x02\x00\x0250\x13@\xa6\x96ffffc\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [29/31] 0x4da6 I len: 38 first: True last: True
        b'\x02\x00\x0250\x14@\xa6\x96\x99\x99\x99\x99\x96\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [30/32] 0x4dcc I len: 38 first: True last: True
        b'\x02\x00\x0250\x15@\xa6\x96\xcc\xcc\xcc\xcc\xc9\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [31/33] 0x4df2 I len: 38 first: True last: True
        b'\x02\x00\x0250\x16@\xa6\x96\xff\xff\xff\xff\xfc\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [32/34] 0x4e18 I len: 38 first: True last: True
        b'\x02\x00\x0250\x17@\xa6\x973333/\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [33/35] 0x4e3e I len: 38 first: True last: True
        b'\x02\x00\x0250\x18@\xa6\x97ffffb\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [34/36] 0x4e64 I len: 38 first: True last: True
        b'\x02\x00\x0250\x19@\xa6\x97\x99\x99\x99\x99\x95\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [35/37] 0x4e8a I len: 38 first: True last: True
        b'\x02\x00\x0250\x1a@\xa6\x97\xcc\xcc\xcc\xcc\xc8\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [36/38] 0x4eb0 I len: 38 first: True last: True
        b'\x02\x00\x0250\x1b@\xa6\x97\xff\xff\xff\xff\xfb\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [37/39] 0x4ed6 I len: 38 first: True last: True
        b'\x02\x00\x0250\x1c@\xa6\x983333.\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [38/40] 0x4efc I len: 38 first: True last: True
        b'\x02\x00\x0250\x1d@\xa6\x98ffffa\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [39/41] 0x4f22 I len: 38 first: True last: True
        b'\x02\x00\x0250\x1e@\xa6\x98\x99\x99\x99\x99\x94\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [40/42] 0x4f48 I len: 38 first: True last: True
        b'\x02\x00\x0250\x1f@\xa6\x98\xcc\xcc\xcc\xcc\xc7\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [41/43] 0x4f6e I len: 38 first: True last: True
        b'\x02\x00\x0250 @\xa6\x98\xff\xff\xff\xff\xfa\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [42/44] 0x4f94 I len: 38 first: True last: True
        b'\x02\x00\x0250!@\xa6\x993333-\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [43/45] 0x4fba I len: 38 first: True last: True
        b'\x02\x00\x0250"@\xa6\x99ffff`\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [44/46] 0x4fe0 I len: 38 first: True last: True
        b'\x02\x00\x0250#@\xa6\x99\x99\x99\x99\x99\x93\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [45/47] 0x5006 I len: 38 first: True last: True
        b'\x02\x00\x0250$@\xa6\x99\xcc\xcc\xcc\xcc\xc6\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [46/48] 0x502c I len: 38 first: True last: True
        b'\x02\x00\x0250%@\xa6\x99\xff\xff\xff\xff\xf9\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [47/49] 0x5052 I len: 38 first: True last: True
        b'\x02\x00\x0250&@\xa6\x9a3333,\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [48/50] 0x5078 I len: 38 first: True last: True
        b"\x02\x00\x0250'@\xa6\x9affff_\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00" # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [49/51] 0x509e I len: 38 first: True last: True
        b'\x02\x00\x0250(@\xa6\x9a\x99\x99\x99\x99\x92\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [50/52] 0x50c4 I len: 38 first: True last: True
        b'\x02\x00\x0250)@\xa6\x9a\xcc\xcc\xcc\xcc\xc5\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [51/53] 0x50ea I len: 38 first: True last: True
        b'\x02\x00\x0250*@\xa6\x9a\xff\xff\xff\xff\xf8\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [52/54] 0x5110 I len: 38 first: True last: True
        b'\x02\x00\x0250+@\xa6\x9b3333+\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [53/55] 0x5136 I len: 38 first: True last: True
        b'\x02\x00\x0250,@\xa6\x9bffff^\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [54/56] 0x515c I len: 38 first: True last: True
        b'\x02\x00\x0250-@\xa6\x9b\x99\x99\x99\x99\x91\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [55/57] 0x5182 I len: 38 first: True last: True
        b'\x02\x00\x0250.@\xa6\x9b\xcc\xcc\xcc\xcc\xc4\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [56/58] 0x51a8 I len: 38 first: True last: True
        b'\x02\x00\x0250/@\xa6\x9b\xff\xff\xff\xff\xf7\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [57/59] 0x51ce I len: 38 first: True last: True
        b'\x02\x00\x02500@\xa6\x9c3333*\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [58/60] 0x51f4 I len: 38 first: True last: True
        b'\x02\x00\x02501@\xa6\x9cffff]\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [59/61] 0x521a I len: 38 first: True last: True
        b'\x02\x00\x02502@\xa6\x9c\x99\x99\x99\x99\x90\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [60/62] 0x5240 I len: 38 first: True last: True
        b'\x02\x00\x02503@\xa6\x9c\xcc\xcc\xcc\xcc\xc3\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [61/63] 0x5266 I len: 38 first: True last: True
        b'\x02\x00\x02504@\xa6\x9c\xff\xff\xff\xff\xf6\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [62/64] 0x528c I len: 38 first: True last: True
        b'\x02\x00\x02505@\xa6\x9d3333)\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [63/65] 0x52b2 I len: 38 first: True last: True
        b'\x02\x00\x02506@\xa6\x9dffff\\\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [64/66] 0x52d8 I len: 38 first: True last: True
        b'\x02\x00\x02507@\xa6\x9d\x99\x99\x99\x99\x8f\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [65/67] 0x52fe I len: 38 first: True last: True
        b'\x02\x00\x02508@\xa6\x9d\xcc\xcc\xcc\xcc\xc2\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [66/68] 0x5324 I len: 38 first: True last: True
        b'\x02\x00\x02509@\xa6\x9d\xff\xff\xff\xff\xf5\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [67/69] 0x534a I len: 38 first: True last: True
        b'\x02\x00\x0250:@\xa6\x9e3333(\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [68/70] 0x5370 I len: 38 first: True last: True
        b'\x02\x00\x0250;@\xa6\x9effff[\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [69/71] 0x5396 I len: 38 first: True last: True
        b'\x02\x00\x0250<@\xa6\x9e\x99\x99\x99\x99\x8e\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [70/72] 0x53bc I len: 38 first: True last: True
        b'\x02\x00\x0250=@\xa6\x9e\xcc\xcc\xcc\xcc\xc1\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [71/73] 0x53e2 I len: 38 first: True last: True
        b'\x02\x00\x0250>@\xa6\x9e\xff\xff\xff\xff\xf4\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [72/74] 0x5408 I len: 38 first: True last: True
        b"\x02\x00\x0250?@\xa6\x9f3333'\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00" # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [73/75] 0x542e I len: 38 first: True last: True
        b'\x02\x00\x0250@@\xa6\x9fffffZ\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [74/76] 0x5454 I len: 38 first: True last: True
        b'\x02\x00\x0250A@\xa6\x9f\x99\x99\x99\x99\x8d\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [75/77] 0x547a I len: 38 first: True last: True
        b'\x02\x00\x0250B@\xa6\x9f\xcc\xcc\xcc\xcc\xc0\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [76/78] 0x54a0 I len: 38 first: True last: True
        b'\x02\x00\x0250C@\xa6\x9f\xff\xff\xff\xff\xf3\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [77/79] 0x54c6 I len: 38 first: True last: True
        b'\x02\x00\x0250D@\xa6\xa03333&\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [78/80] 0x54ec I len: 38 first: True last: True
        b'\x02\x00\x0250E@\xa6\xa0ffffY\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [79/81] 0x5512 I len: 38 first: True last: True
        b'\x02\x00\x0250F@\xa6\xa0\x99\x99\x99\x99\x8c\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [80/82] 0x5538 I len: 38 first: True last: True
        b'\x02\x00\x0250G@\xa6\xa0\xcc\xcc\xcc\xcc\xbf\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [81/83] 0x555e I len: 38 first: True last: True
        b'\x02\x00\x0250H@\xa6\xa0\xff\xff\xff\xff\xf2\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [82/84] 0x5584 I len: 38 first: True last: True
        b'\x02\x00\x0250I@\xa6\xa13333%\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [83/85] 0x55aa I len: 38 first: True last: True
        b'\x02\x00\x0250J@\xa6\xa1ffffX\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [84/86] 0x55d0 I len: 38 first: True last: True
        b'\x02\x00\x0250K@\xa6\xa1\x99\x99\x99\x99\x8b\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [85/87] 0x55f6 I len: 38 first: True last: True
        b'\x02\x00\x0250L@\xa6\xa1\xcc\xcc\xcc\xcc\xbe\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [86/88] 0x561c I len: 38 first: True last: True
        b'\x02\x00\x0250M@\xa6\xa1\xff\xff\xff\xff\xf1\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bc\x95]' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [87/89] 0x5642 I len: 38 first: True last: True
        b'\x02\x00\x0250N@\xa6\xa23333$\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bd;G' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [88/90] 0x5668 I len: 38 first: True last: True
        b'\x02\x00\x0250O@\xa6\xa2ffffW\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bo\xcb\x80' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [89/91] 0x568e I len: 38 first: True last: True
        b'\x02\x00\x0250P@\xa6\xa2\x99\x99\x99\x99\x8a\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bt\xd7\xde' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [90/92] 0x56b4 I len: 38 first: True last: True
        b'\x02\x00\x0250Q@\xa6\xa2\xcc\xcc\xcc\xcc\xbd\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00By\xb8\x93' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [91/93] 0x56da I len: 38 first: True last: True
        b'\x02\x00\x0250R@\xa6\xa2\xff\xff\xff\xff\xf0\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bx\xcc\xce' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [92/94] 0x5700 I len: 38 first: True last: True
        b'\x02\x00\x0250S@\xa6\xa33333#\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bv`\xd2' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [93/95] 0x5726 I len: 38 first: True last: True
        b'\x02\x00\x0250T@\xa6\xa3ffffV\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bv\xec\x89' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [94/96] 0x574c I len: 38 first: True last: True
        b'\x02\x00\x0250U@\xa6\xa3\x99\x99\x99\x99\x89\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B~\xf9V' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [95/97] 0x5772 I len: 38 first: True last: True
        b'\x02\x00\x0250V@\xa6\xa3\xcc\xcc\xcc\xcc\xbc\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x83+\xc0' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [96/98] 0x5798 I len: 38 first: True last: True
        b'\x02\x00\x0250W@\xa6\xa3\xff\xff\xff\xff\xef\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x82.\x84' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [97/99] 0x57be I len: 38 first: True last: True
        b'\x02\x00\x0250X@\xa6\xa43333"\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x81\xa2\xcc' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [98/100] 0x57e4 I len: 38 first: True last: True
        b'\x02\x00\x0250Y@\xa6\xa4ffffU\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x80\xca\xad' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [99/101] 0x580a I len: 38 first: True last: True
        b'\x02\x00\x0250Z@\xa6\xa4\x99\x99\x99\x99\x88\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B}\x9c\r' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [100/102] 0x5830 I len: 38 first: True last: True
        b'\x02\x00\x0250[@\xa6\xa4\xcc\xcc\xcc\xcc\xbb\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bt\xc2\n' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [101/103] 0x5856 I len: 38 first: True last: True
        b'\x02\x00\x0250\\@\xa6\xa4\xff\xff\xff\xff\xee\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bg\x8e\xab' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [102/104] 0x587c I len: 38 first: True last: True
        b'\x02\x00\x0250]@\xa6\xa53333!\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bcrp' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [103/105] 0x58a2 I len: 38 first: True last: True
        b'\x02\x00\x0250^@\xa6\xa5ffffT\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B^\x96\x18' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [104/106] 0x58c8 I len: 38 first: True last: True
        b'\x02\x00\x0250_@\xa6\xa5\x99\x99\x99\x99\x87\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BTpC' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [105/107] 0x58ee I len: 38 first: True last: True
        b'\x02\x00\x0250`@\xa6\xa5\xcc\xcc\xcc\xcc\xba\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BZ+F' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [106/108] 0x5914 I len: 38 first: True last: True
        b'\x02\x00\x0250a@\xa6\xa5\xff\xff\xff\xff\xed\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Be\x87\x1a' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [107/109] 0x593a I len: 38 first: True last: True
        b'\x02\x00\x0250b@\xa6\xa63333 \xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x85\xa0x' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [108/110] 0x5960 I len: 38 first: True last: True
        b'\x02\x00\x0250c@\xa6\xa6ffffS\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x8axr' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [109/111] 0x5986 I len: 38 first: True last: True
        b'\x02\x00\x0250d@\xa6\xa6\x99\x99\x99\x99\x86\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x95g\x1f' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [110/112] 0x59ac I len: 38 first: True last: True
        b'\x02\x00\x0250e@\xa6\xa6\xcc\xcc\xcc\xcc\xb9\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xa5G\xf8' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [111/113] 0x59d2 I len: 38 first: True last: True
        b'\x02\x00\x0250f@\xa6\xa6\xff\xff\xff\xff\xec\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xd9\x185' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [112/114] 0x59f8 I len: 38 first: True last: True
        b'\x02\x00\x0250g@\xa6\xa73333\x1f\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xf0~\x83' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [113/115] 0x5a1e I len: 38 first: True last: True
        b'\x02\x00\x0250h@\xa6\xa7ffffR\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xff\xe9y' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [114/116] 0x5a44 I len: 38 first: True last: True
        b'\x02\x00\x0250i@\xa6\xa7\x99\x99\x99\x99\x85\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x03U:' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [115/117] 0x5a6a I len: 38 first: True last: True
        b'\x02\x00\x0250j@\xa6\xa7\xcc\xcc\xcc\xcc\xb8\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x01\x8c\xf8' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [116/118] 0x5a90 I len: 38 first: True last: True
        b'\x02\x00\x0250k@\xa6\xa7\xff\xff\xff\xff\xeb\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x00\x13M' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [117/119] 0x5ab6 I len: 38 first: True last: True
        b'\x02\x00\x0250l@\xa6\xa83333\x1e\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x01\x9eo' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [118/120] 0x5adc I len: 38 first: True last: True
        b'\x02\x00\x0250m@\xa6\xa8ffffQ\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x01\xe4J' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [119/121] 0x5b02 I len: 38 first: True last: True
        b'\x02\x00\x0250n@\xa6\xa8\x99\x99\x99\x99\x84\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x00|\x16' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [120/122] 0x5b28 I len: 38 first: True last: True
        b'\x02\x00\x0250o@\xa6\xa8\xcc\xcc\xcc\xcc\xb7\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xf5\xad\xcf' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [121/123] 0x5b4e I len: 38 first: True last: True
        b'\x02\x00\x0250p@\xa6\xa8\xff\xff\xff\xff\xea\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xf4\n\xa9' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [122/124] 0x5b74 I len: 38 first: True last: True
        b'\x02\x00\x0250q@\xa6\xa93333\x1d\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xf5<J' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [123/125] 0x5b9a I len: 38 first: True last: True
        b'\x02\x00\x0250r@\xa6\xa9ffffP\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x01\xf3\x92' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [124/126] 0x5bc0 I len: 38 first: True last: True
        b'\x02\x00\x0250s@\xa6\xa9\x99\x99\x99\x99\x83\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x05\xdf\xc7' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [125/127] 0x5be6 I len: 38 first: True last: True
        b'\x02\x00\x0250t@\xa6\xa9\xcc\xcc\xcc\xcc\xb6\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x07\x9a\xf0' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [126/128] 0x5c0c I len: 38 first: True last: True
        b'\x02\x00\x0250u@\xa6\xa9\xff\xff\xff\xff\xe9\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x06\xecK' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [127/129] 0x5c32 I len: 38 first: True last: True
        b'\x02\x00\x0250v@\xa6\xaa3333\x1c\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x00\x11\x1e' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [128/130] 0x5c58 I len: 38 first: True last: True
        b'\x02\x00\x0250w@\xa6\xaaffffO\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xf6\xafi' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [129/131] 0x5c7e I len: 38 first: True last: True
        b'\x02\x00\x0250x@\xa6\xaa\x99\x99\x99\x99\x82\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xea\xba\xc4' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [130/132] 0x5ca4 I len: 38 first: True last: True
        b'\x02\x00\x0250y@\xa6\xaa\xcc\xcc\xcc\xcc\xb5\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xd61\xf8' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [131/133] 0x5cca I len: 38 first: True last: True
        b'\x02\x00\x0250z@\xa6\xaa\xff\xff\xff\xff\xe8\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xcf&\xc4' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [132/134] 0x5cf0 I len: 38 first: True last: True
        b'\x02\x00\x0250{@\xa6\xab3333\x1b\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xc9*C' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [133/135] 0x5d16 I len: 38 first: True last: True
        b'\x02\x00\x0250|@\xa6\xabffffN\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xae\xe6t' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [134/136] 0x5d3c I len: 38 first: True last: True
        b'\x02\x00\x0250}@\xa6\xab\x99\x99\x99\x99\x81\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x9b\xc3\xae' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [135/137] 0x5d62 I len: 38 first: True last: True
        b'\x02\x00\x0250~@\xa6\xab\xcc\xcc\xcc\xcc\xb4\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x883\xc0' # Logical data length 34 0x22
    b'\x00&\x00\x00'  # LRSH [136/138] 0x5d88 I len: 38 first: True last: True
        b'\x02\x00\x0250\x7f@\xa6\xab\xff\xff\xff\xff\xe7\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bb\xa0\xdd' # Logical data length 34 0x22
    b'\x00(\x01\x00'  # LRSH [137/139] 0x5dae I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x80@\xa6\xac3333\x1a\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\\75\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [138/140] 0x5dd6 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x81@\xa6\xacffffM\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B^w\x89\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [139/141] 0x5dfe I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x82@\xa6\xac\x99\x99\x99\x99\x80\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B]\x94\x7f\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [140/142] 0x5e26 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x83@\xa6\xac\xcc\xcc\xcc\xcc\xb3\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BZhf\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [141/143] 0x5e4e I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x84@\xa6\xac\xff\xff\xff\xff\xe6\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BYH<\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [142/144] 0x5e76 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x85@\xa6\xad3333\x19\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B_\x14\xb6\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [143/145] 0x5e9e I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x86@\xa6\xadffffL\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bx\x8f\xae\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [144/146] 0x5ec6 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x87@\xa6\xad\x99\x99\x99\x99\x7f\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x81\x05\x9e\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [145/147] 0x5eee I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x88@\xa6\xad\xcc\xcc\xcc\xcc\xb2\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x83S\x0b\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [146/148] 0x5f16 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x89@\xa6\xad\xff\xff\xff\xff\xe5\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B|\xedh\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [147/149] 0x5f3e I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x8a@\xa6\xae3333\x18\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bx\xd5\x8a\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [148/150] 0x5f66 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x8b@\xa6\xaeffffK\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bt\x92\x03\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [149/151] 0x5f8e I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x8c@\xa6\xae\x99\x99\x99\x99~\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Be/\xc7\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [150/152] 0x5fb6 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x8d@\xa6\xae\xcc\xcc\xcc\xcc\xb1\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B]\xa5\xf5\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [151/153] 0x5fde I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x8e@\xa6\xae\xff\xff\xff\xff\xe4\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BZ\xd1/\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [152/154] 0x6006 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x8f@\xa6\xaf3333\x17\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BiY\x1c\x01' # Logical data length 36 0x24
    b'\x00" \x00'  # LRSH [153/155] 0x602e I len: 34 first: True last: False
        b'\x02\x00\x0250\x80\x90@\xa6\xafffffJ\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0' # Logical data length 30 0x1e
b' \x00\xff\x01'  # Visible record [3] at 0x6050 length 0x2000 version 0xff01
    b'\x00\x10A\x00'  # LRSH [154/156] 0x6054 I len: 16 first: False last: True
        b'\x00Bt\xfa\xcc\x01\x02\x03\x04\x05\x06\x07' # Logical data length 12 0xc
    b'\x00(\x01\x00'  # LRSH [154/157] 0x6064 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x91@\xa6\xaf\x99\x99\x99\x99}\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x80\x9c\xd5\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [155/158] 0x608c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x92@\xa6\xaf\xcc\xcc\xcc\xcc\xb0\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x8b\x0c\xe4\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [156/159] 0x60b4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x93@\xa6\xaf\xff\xff\xff\xff\xe3\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x8f\n\x90\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [157/160] 0x60dc I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x94@\xa6\xb03333\x16\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x8e\x04\x98\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [158/161] 0x6104 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x95@\xa6\xb0ffffI\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x87\xbd\xde\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [159/162] 0x612c I len: 40 first: True last: True
        b"\x02\x00\x0250\x80\x96@\xa6\xb0\x99\x99\x99\x99|\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B{'T\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [160/163] 0x6154 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x97@\xa6\xb0\xcc\xcc\xcc\xcc\xaf\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bz^}\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [161/164] 0x617c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x98@\xa6\xb0\xff\xff\xff\xff\xe2\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B|\x84\x9e\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [162/165] 0x61a4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x99@\xa6\xb13333\x15\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bv\xa6\xad\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [163/166] 0x61cc I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x9a@\xa6\xb1ffffH\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bsq\xd9\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [164/167] 0x61f4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x9b@\xa6\xb1\x99\x99\x99\x99{\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bqn\xa6\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [165/168] 0x621c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x9c@\xa6\xb1\xcc\xcc\xcc\xcc\xae\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bn\x99\xdf\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [166/169] 0x6244 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x9d@\xa6\xb1\xff\xff\xff\xff\xe1\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bk\xf9~\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [167/170] 0x626c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x9e@\xa6\xb23333\x14\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BgM-\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [168/171] 0x6294 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\x9f@\xa6\xb2ffffG\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B[Kp\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [169/172] 0x62bc I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xa0@\xa6\xb2\x99\x99\x99\x99z\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BS{\xc2\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [170/173] 0x62e4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xa1@\xa6\xb2\xcc\xcc\xcc\xcc\xad\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BN\x18\x11\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [171/174] 0x630c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xa2@\xa6\xb2\xff\xff\xff\xff\xe0\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BO/\x80\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [172/175] 0x6334 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xa3@\xa6\xb33333\x13\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BYk*\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [173/176] 0x635c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xa4@\xa6\xb3ffffF\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B`\x11\xf3\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [174/177] 0x6384 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xa5@\xa6\xb3\x99\x99\x99\x99y\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bh\xf9\x0f\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [175/178] 0x63ac I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xa6@\xa6\xb3\xcc\xcc\xcc\xcc\xac\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bm\x9c\xa3\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [176/179] 0x63d4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xa7@\xa6\xb3\xff\xff\xff\xff\xdf\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bl\xc2U\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [177/180] 0x63fc I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xa8@\xa6\xb43333\x12\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Be\xe7(\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [178/181] 0x6424 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xa9@\xa6\xb4ffffE\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Baw\xf8\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [179/182] 0x644c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xaa@\xa6\xb4\x99\x99\x99\x99x\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BZ\xf4\x1d\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [180/183] 0x6474 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xab@\xa6\xb4\xcc\xcc\xcc\xcc\xab\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BSG]\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [181/184] 0x649c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xac@\xa6\xb4\xff\xff\xff\xff\xde\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BD\x9c\x83\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [182/185] 0x64c4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xad@\xa6\xb53333\x11\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BGh\x8d\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [183/186] 0x64ec I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xae@\xa6\xb5ffffD\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BQ^\\\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [184/187] 0x6514 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xaf@\xa6\xb5\x99\x99\x99\x99w\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bj*\xaf\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [185/188] 0x653c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xb0@\xa6\xb5\xcc\xcc\xcc\xcc\xaa\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bu}\xc8\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [186/189] 0x6564 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xb1@\xa6\xb5\xff\xff\xff\xff\xdd\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x83\xb7w\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [187/190] 0x658c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xb2@\xa6\xb63333\x10\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xa5\xf2?\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [188/191] 0x65b4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xb3@\xa6\xb6ffffC\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xbc\xf8~\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [189/192] 0x65dc I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xb4@\xa6\xb6\x99\x99\x99\x99v\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xd6\xe4\xfb\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [190/193] 0x6604 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xb5@\xa6\xb6\xcc\xcc\xcc\xcc\xa9\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xf34\xb9\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [191/194] 0x662c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xb6@\xa6\xb6\xff\xff\xff\xff\xdc\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x16_\xfd\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [192/195] 0x6654 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xb7@\xa6\xb73333\x0f\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C \x9b\xa7\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [193/196] 0x667c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xb8@\xa6\xb7ffffB\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C&\x82T\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [194/197] 0x66a4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xb9@\xa6\xb7\x99\x99\x99\x99u\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C!h\xdc\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [195/198] 0x66cc I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xba@\xa6\xb7\xcc\xcc\xcc\xcc\xa8\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x1d\xa3\xf3\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [196/199] 0x66f4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xbb@\xa6\xb7\xff\xff\xff\xff\xdb\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x1a\xa1U\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [197/200] 0x671c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xbc@\xa6\xb83333\x0e\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x1a\x8b\x80\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [198/201] 0x6744 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xbd@\xa6\xb8ffffA\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x19D\x0b\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [199/202] 0x676c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xbe@\xa6\xb8\x99\x99\x99\x99t\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x17_h\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [200/203] 0x6794 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xbf@\xa6\xb8\xcc\xcc\xcc\xcc\xa7\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x0f\xa9\xec\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [201/204] 0x67bc I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xc0@\xa6\xb8\xff\xff\xff\xff\xda\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\t\xa2\x81\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [202/205] 0x67e4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xc1@\xa6\xb93333\r\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x02\x1a\xde\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [203/206] 0x680c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xc2@\xa6\xb9ffff@\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xdd\xa1\x98\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [204/207] 0x6834 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xc3@\xa6\xb9\x99\x99\x99\x99s\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xcd\x99s\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [205/208] 0x685c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xc4@\xa6\xb9\xcc\xcc\xcc\xcc\xa6\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xc3\x9a\xe9\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [206/209] 0x6884 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xc5@\xa6\xb9\xff\xff\xff\xff\xd9\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xbf\xf4\x90\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [207/210] 0x68ac I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xc6@\xa6\xba3333\x0c\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xc5\x95a\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [208/211] 0x68d4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xc7@\xa6\xbaffff?\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xc5\xf5o\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [209/212] 0x68fc I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xc8@\xa6\xba\x99\x99\x99\x99r\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xc2\xc9V\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [210/213] 0x6924 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xc9@\xa6\xba\xcc\xcc\xcc\xcc\xa5\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xad\n\x8c\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [211/214] 0x694c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xca@\xa6\xba\xff\xff\xff\xff\xd8\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x9e\x8b[\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [212/215] 0x6974 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xcb@\xa6\xbb3333\x0b\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x8eJt\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [213/216] 0x699c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xcc@\xa6\xbbffff>\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bm<\x95\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [214/217] 0x69c4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xcd@\xa6\xbb\x99\x99\x99\x99q\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Ba\xfa\xf4\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [215/218] 0x69ec I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xce@\xa6\xbb\xcc\xcc\xcc\xcc\xa4\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B_\x03@\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [216/219] 0x6a14 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xcf@\xa6\xbb\xff\xff\xff\xff\xd7\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BisO\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [217/220] 0x6a3c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xd0@\xa6\xbc3333\n\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bn\xdf\xbb\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [218/221] 0x6a64 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xd1@\xa6\xbcffff=\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bw\xbe\x1b\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [219/222] 0x6a8c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xd2@\xa6\xbc\x99\x99\x99\x99p\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x84\x89\t\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [220/223] 0x6ab4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xd3@\xa6\xbc\xcc\xcc\xcc\xcc\xa3\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x8aU\x84\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [221/224] 0x6adc I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xd4@\xa6\xbc\xff\xff\xff\xff\xd6\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x8c\x05\xc2\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [222/225] 0x6b04 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xd5@\xa6\xbd3333\t\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x8b\xfd\x07\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [223/226] 0x6b2c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xd6@\xa6\xbdffff<\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x8a\x92\xa4\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [224/227] 0x6b54 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xd7@\xa6\xbd\x99\x99\x99\x99o\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x8e4\x9f\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [225/228] 0x6b7c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xd8@\xa6\xbd\xcc\xcc\xcc\xcc\xa2\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x90II\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [226/229] 0x6ba4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xd9@\xa6\xbd\xff\xff\xff\xff\xd5\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x8cas\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [227/230] 0x6bcc I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xda@\xa6\xbe3333\x08\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x87\xbd\xde\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [228/231] 0x6bf4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xdb@\xa6\xbeffff;\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x83#\x04\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [229/232] 0x6c1c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xdc@\xa6\xbe\x99\x99\x99\x99n\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B~0\x7f\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [230/233] 0x6c44 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xdd@\xa6\xbe\xcc\xcc\xcc\xcc\xa1\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bx\xbbW\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [231/234] 0x6c6c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xde@\xa6\xbe\xff\xff\xff\xff\xd4\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Br\xee\xdd\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [232/235] 0x6c94 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xdf@\xa6\xbf3333\x07\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BgU\xe9\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [233/236] 0x6cbc I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xe0@\xa6\xbfffff:\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bg\xbe\xb2\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [234/237] 0x6ce4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xe1@\xa6\xbf\x99\x99\x99\x99m\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bl\xed\xff\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [235/238] 0x6d0c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xe2@\xa6\xbf\xcc\xcc\xcc\xcc\xa0\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BnKH\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [236/239] 0x6d34 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xe3@\xa6\xbf\xff\xff\xff\xff\xd3\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bj3k\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [237/240] 0x6d5c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xe4@\xa6\xc03333\x06\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bh\rI\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [238/241] 0x6d84 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xe5@\xa6\xc0ffff9\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bf\xfe\x96\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [239/242] 0x6dac I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xe6@\xa6\xc0\x99\x99\x99\x99l\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bc\xec\xb0\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [240/243] 0x6dd4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xe7@\xa6\xc0\xcc\xcc\xcc\xcc\x9f\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B_\x03@\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [241/244] 0x6dfc I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xe8@\xa6\xc0\xff\xff\xff\xff\xd2\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BZ\x82\x98\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [242/245] 0x6e24 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xe9@\xa6\xc13333\x05\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BY\x9f\x8f\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [243/246] 0x6e4c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xea@\xa6\xc1ffff8\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bb\x86\xab\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [244/247] 0x6e74 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xeb@\xa6\xc1\x99\x99\x99\x99k\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bj_\x14\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [245/248] 0x6e9c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xec@\xa6\xc1\xcc\xcc\xcc\xcc\x9e\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x83#\x04\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [246/249] 0x6ec4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xed@\xa6\xc1\xff\xff\xff\xff\xd1\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x8e=[\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [247/250] 0x6eec I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xee@\xa6\xc23333\x04\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xa4\xe7\xea\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [248/251] 0x6f14 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xef@\xa6\xc2ffff7\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xe9\xd7\xba\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [249/252] 0x6f3c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xf0@\xa6\xc2\x99\x99\x99\x99j\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x06\x99V\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [250/253] 0x6f64 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xf1@\xa6\xc2\xcc\xcc\xcc\xcc\x9d\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x13y\xc0\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [251/254] 0x6f8c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xf2@\xa6\xc2\xff\xff\xff\xff\xd0\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x18\xc3>\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [252/255] 0x6fb4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xf3@\xa6\xc33333\x03\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x16\x08\xaa\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [253/256] 0x6fdc I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xf4@\xa6\xc3ffff6\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x12\x80\xe1\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [254/257] 0x7004 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xf5@\xa6\xc3\x99\x99\x99\x99i\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x10\x82\x0c\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [255/258] 0x702c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xf6@\xa6\xc3\xcc\xcc\xcc\xcc\x9c\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x0e\xeb\xff\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [256/259] 0x7054 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xf7@\xa6\xc3\xff\xff\xff\xff\xcf\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\n~\xfe\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [257/260] 0x707c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xf8@\xa6\xc43333\x02\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xfev[\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [258/261] 0x70a4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xf9@\xa6\xc4ffff5\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xb9\x15\x05\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [259/262] 0x70cc I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xfa@\xa6\xc4\x99\x99\x99\x99h\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x96\x9d\x1d\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [260/263] 0x70f4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xfb@\xa6\xc4\xcc\xcc\xcc\xcc\x9b\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B{0\x10\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [261/264] 0x711c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xfc@\xa6\xc4\xff\xff\xff\xff\xce\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B>DQ\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [262/265] 0x7144 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xfd@\xa6\xc53333\x01\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B2\x88o\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [263/266] 0x716c I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xfe@\xa6\xc5ffff4\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B,\xcdl\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [264/267] 0x7194 I len: 40 first: True last: True
        b'\x02\x00\x0250\x80\xff@\xa6\xc5\x99\x99\x99\x99g\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B8\x89N\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [265/268] 0x71bc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x00@\xa6\xc5\xcc\xcc\xcc\xcc\x9a\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B?\x87i\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [266/269] 0x71e4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x01@\xa6\xc5\xff\xff\xff\xff\xcd\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B@a\xb7\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [267/270] 0x720c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x02@\xa6\xc63333\x00\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B?\x98\xe0\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [268/271] 0x7234 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x03@\xa6\xc6ffff3\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BA\xd94\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [269/272] 0x725c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x04@\xa6\xc6\x99\x99\x99\x99f\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BM\x95\x16\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [270/273] 0x7284 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x05@\xa6\xc6\xcc\xcc\xcc\xcc\x99\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BX\xab\x0e\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [271/274] 0x72ac I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x06@\xa6\xc6\xff\xff\xff\xff\xcc\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bq\xab\xc6\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [272/275] 0x72d4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x07@\xa6\xc73332\xff\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00By{s\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [273/276] 0x72fc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x08@\xa6\xc7ffff2\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x82\xeaB\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [274/277] 0x7324 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\t@\xa6\xc7\x99\x99\x99\x99e\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x95D1\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [275/278] 0x734c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\n@\xa6\xc7\xcc\xcc\xcc\xcc\x98\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xa6}\xf6\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [276/279] 0x7374 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x0b@\xa6\xc7\xff\xff\xff\xff\xcb\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xbbC\xe2\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [277/280] 0x739c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x0c@\xa6\xc83332\xfe\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xdf\xea\xa7\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [278/281] 0x73c4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\r@\xa6\xc8ffff1\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xec|z\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [279/282] 0x73ec I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x0e@\xa6\xc8\x99\x99\x99\x99d\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xf2\x97\x8b\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [280/283] 0x7414 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x0f@\xa6\xc8\xcc\xcc\xcc\xcc\x97\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xfb\x1a;\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [281/284] 0x743c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x10@\xa6\xc8\xff\xff\xff\xff\xca\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xfa\x8a&\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [282/285] 0x7464 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x11@\xa6\xc93332\xfd\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xf6BA\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [283/286] 0x748c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x12@\xa6\xc9ffff0\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xedEQ\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [284/287] 0x74b4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x13@\xa6\xc9\x99\x99\x99\x99c\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xdd\x08\xc7\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [285/288] 0x74dc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x14@\xa6\xc9\xcc\xcc\xcc\xcc\x96\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xd8\xc9\x9e\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [286/289] 0x7504 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x15@\xa6\xc9\xff\xff\xff\xff\xc9\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xd9.\n\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [287/290] 0x752c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x16@\xa6\xca3332\xfc\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xd6\xb0\x96\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [288/291] 0x7554 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x17@\xa6\xcaffff/\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xd4k\xe5\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [289/292] 0x757c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x18@\xa6\xca\x99\x99\x99\x99b\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xcef\xa8\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [290/293] 0x75a4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x19@\xa6\xca\xcc\xcc\xcc\xcc\x95\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xc8]\x0e\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [291/294] 0x75cc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x1a@\xa6\xca\xff\xff\xff\xff\xc8\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xc4\xa9\x9c\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [292/295] 0x75f4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x1b@\xa6\xcb3332\xfb\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xc06\x0e\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [293/296] 0x761c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x1c@\xa6\xcbffff.\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xa6\xd5I\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [294/297] 0x7644 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x1d@\xa6\xcb\x99\x99\x99\x99a\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x9aP\x8f\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [295/298] 0x766c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x1e@\xa6\xcb\xcc\xcc\xcc\xcc\x94\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x93\x0c\x99\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [296/299] 0x7694 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x1f@\xa6\xcb\xff\xff\xff\xff\xc7\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x9b""\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [297/300] 0x76bc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81 @\xa6\xcc3332\xfa\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xa7\xc1\x0e\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [298/301] 0x76e4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81!@\xa6\xccffff-\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xb9<Q\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [299/302] 0x770c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81"@\xa6\xcc\x99\x99\x99\x99`\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xccl0\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [300/303] 0x7734 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81#@\xa6\xcc\xcc\xcc\xcc\xcc\x93\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xf04I\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [301/304] 0x775c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81$@\xa6\xcc\xff\xff\xff\xff\xc6\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xfeFT\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [302/305] 0x7784 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81%@\xa6\xcd3332\xf9\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x06`\x94\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [303/306] 0x77ac I len: 40 first: True last: True
        b'\x02\x00\x0250\x81&@\xa6\xcdffff,\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x13\x19\xb2\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [304/307] 0x77d4 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81'@\xa6\xcd\x99\x99\x99\x99_\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x19\xc0z\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [305/308] 0x77fc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81(@\xa6\xcd\xcc\xcc\xcc\xcc\x92\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x1d\xa8Q\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [306/309] 0x7824 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81)@\xa6\xcd\xff\xff\xff\xff\xc5\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C"\xedr\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [307/310] 0x784c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81*@\xa6\xce3332\xf8\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C \xee\x9c\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [308/311] 0x7874 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81+@\xa6\xceffff+\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x1c0\xd5\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [309/312] 0x789c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81,@\xa6\xce\x99\x99\x99\x99^\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x03+\xc0\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [310/313] 0x78c4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81-@\xa6\xce\xcc\xcc\xcc\xcc\x91\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xe7!\x84\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [311/314] 0x78ec I len: 40 first: True last: True
        b'\x02\x00\x0250\x81.@\xa6\xce\xff\xff\xff\xff\xc4\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xc8O\xf5\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [312/315] 0x7914 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81/@\xa6\xcf3332\xf7\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xa1\xc4\x8c\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [313/316] 0x793c I len: 40 first: True last: True
        b"\x02\x00\x0250\x810@\xa6\xcfffff*\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x94a'\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [314/317] 0x7964 I len: 40 first: True last: True
        b'\x02\x00\x0250\x811@\xa6\xcf\x99\x99\x99\x99]\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x90_\x1e\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [315/318] 0x798c I len: 40 first: True last: True
        b'\x02\x00\x0250\x812@\xa6\xcf\xcc\xcc\xcc\xcc\x90\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x8f\x89.\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [316/319] 0x79b4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x813@\xa6\xcf\xff\xff\xff\xff\xc3\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x975\xed\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [317/320] 0x79dc I len: 40 first: True last: True
        b"\x02\x00\x0250\x814@\xa6\xd03332\xf6\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x99'\xaa\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [318/321] 0x7a04 I len: 40 first: True last: True
        b'\x02\x00\x0250\x815@\xa6\xd0ffff)\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x98\xbe\xe1\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [319/322] 0x7a2c I len: 40 first: True last: True
        b'\x02\x00\x0250\x816@\xa6\xd0\x99\x99\x99\x99\\\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x91\xeco\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [320/323] 0x7a54 I len: 40 first: True last: True
        b'\x02\x00\x0250\x817@\xa6\xd0\xcc\xcc\xcc\xcc\x8f\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x90/\x17\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [321/324] 0x7a7c I len: 40 first: True last: True
        b'\x02\x00\x0250\x818@\xa6\xd0\xff\xff\xff\xff\xc2\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x8fT\xc9\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [322/325] 0x7aa4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x819@\xa6\xd13332\xf5\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x91\xd2=\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [323/326] 0x7acc I len: 40 first: True last: True
        b"\x02\x00\x0250\x81:@\xa6\xd1ffff(\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x96':\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [324/327] 0x7af4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81;@\xa6\xd1\x99\x99\x99\x99[\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x9c\x8c\x85\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [325/328] 0x7b1c I len: 40 first: True last: True
        b"\x02\x00\x0250\x81<@\xa6\xd1\xcc\xcc\xcc\xcc\x8e\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xa7\xce'\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [326/329] 0x7b44 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81=@\xa6\xd1\xff\xff\xff\xff\xc1\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xabc\t\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [327/330] 0x7b6c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81>@\xa6\xd23332\xf4\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xb0og\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [328/331] 0x7b94 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81?@\xa6\xd2ffff'\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xbe\xc7M\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [329/332] 0x7bbc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81@@\xa6\xd2\x99\x99\x99\x99Z\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xc4\xbb\x13\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [330/333] 0x7be4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81A@\xa6\xd2\xcc\xcc\xcc\xcc\x8d\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xc7d0\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [331/334] 0x7c0c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81B@\xa6\xd2\xff\xff\xff\xff\xc0\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xcc\xef,\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [332/335] 0x7c34 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81C@\xa6\xd33332\xf3\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xea\xad\xab\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [333/336] 0x7c5c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81D@\xa6\xd3ffff&\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x00\xfc\xe3\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [334/337] 0x7c84 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81E@\xa6\xd3\x99\x99\x99\x99Y\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\n\xb7\xc0\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [335/338] 0x7cac I len: 40 first: True last: True
        b'\x02\x00\x0250\x81F@\xa6\xd3\xcc\xcc\xcc\xcc\x8c\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x162%\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [336/339] 0x7cd4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81G@\xa6\xd3\xff\xff\xff\xff\xbf\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x17\xd0\xed\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [337/340] 0x7cfc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81H@\xa6\xd43332\xf2\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00C\x15QJ\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [338/341] 0x7d24 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81I@\xa6\xd4ffff%\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xff\x02\x12\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [339/342] 0x7d4c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81J@\xa6\xd4\x99\x99\x99\x99X\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xde\x06\x04\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [340/343] 0x7d74 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81K@\xa6\xd4\xcc\xcc\xcc\xcc\x8b\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\xbfzP\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [341/344] 0x7d9c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81L@\xa6\xd4\xff\xff\xff\xff\xbe\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x94\x12\x90\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [342/345] 0x7dc4 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81M@\xa6\xd53332\xf1\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x86'\xd1\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [343/346] 0x7dec I len: 40 first: True last: True
        b'\x02\x00\x0250\x81N@\xa6\xd5ffff$\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BwC\xdb\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [344/347] 0x7e14 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81O@\xa6\xd5\x99\x99\x99\x99W\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bb\x0cj\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [345/348] 0x7e3c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81P@\xa6\xd5\xcc\xcc\xcc\xcc\x8a\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B^\xf1\xc9\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [346/349] 0x7e64 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81Q@\xa6\xd5\xff\xff\xff\xff\xbd\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B^f\x11\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [347/350] 0x7e8c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81R@\xa6\xd63332\xf0\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bb}\xef\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [348/351] 0x7eb4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81S@\xa6\xd6ffff#\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bl\x96\xac\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [349/352] 0x7edc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81T@\xa6\xd6\x99\x99\x99\x99V\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bp\xf4e\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [350/353] 0x7f04 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81U@\xa6\xd6\xcc\xcc\xcc\xcc\x89\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bo.R\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [351/354] 0x7f2c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81V@\xa6\xd6\xff\xff\xff\xff\xbc\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bi\xa7\xb3\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [352/355] 0x7f54 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81W@\xa6\xd73332\xef\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bh\x04\x8e\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [353/356] 0x7f7c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81X@\xa6\xd7ffff"\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bj\x9c4\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [354/357] 0x7fa4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81Y@\xa6\xd7\x99\x99\x99\x99U\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B|$\x90\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [355/358] 0x7fcc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81Z@\xa6\xd7\xcc\xcc\xcc\xcc\x88\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x81\xa7*\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [356/359] 0x7ff4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81[@\xa6\xd7\xff\xff\xff\xff\xbb\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00B\x81{\x81\x01' # Logical data length 36 0x24
    b'\x004\x01\x00'  # LRSH [357/360] 0x801c I len: 52 first: True last: True
        # Logical data length 48 0x30
        b'\x02\x00\x0250\x81\\@\xa6\xd83332\xee\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bv\x12:\x01\x02\x03\x04\x05'  # Chunk from 0
        b'\x06\x07\x08\t\n\x0b\x0c\r'                                                                                               # Chunk from 40
b' \x00\xff\x01'  # Visible record [4] at 0x8050 length 0x2000 version 0xff01
    b'\x00(\x01\x00'  # LRSH [358/361] 0x8054 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81]@\xa6\xd8ffff!\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bo\x02\xa9\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [359/362] 0x807c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81^@\xa6\xd8\x99\x99\x99\x99T\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00BlbG\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [360/363] 0x80a4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81_@\xa6\xd8\xcc\xcc\xcc\xcc\x87\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bh\xc4\xaa\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [361/364] 0x80cc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81`@\xa6\xd8\xff\xff\xff\xff\xba\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00Bl?Y\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [362/365] 0x80f4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81a@\xa6\xd93332\xed\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [363/366] 0x811c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81b@\xa6\xd9ffff \xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [364/367] 0x8144 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81c@\xa6\xd9\x99\x99\x99\x99S\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [365/368] 0x816c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81d@\xa6\xd9\xcc\xcc\xcc\xcc\x86\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [366/369] 0x8194 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81e@\xa6\xd9\xff\xff\xff\xff\xb9\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [367/370] 0x81bc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81f@\xa6\xda3332\xec\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [368/371] 0x81e4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81g@\xa6\xdaffff\x1f\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [369/372] 0x820c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81h@\xa6\xda\x99\x99\x99\x99R\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [370/373] 0x8234 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81i@\xa6\xda\xcc\xcc\xcc\xcc\x85\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [371/374] 0x825c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81j@\xa6\xda\xff\xff\xff\xff\xb8\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [372/375] 0x8284 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81k@\xa6\xdb3332\xeb\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [373/376] 0x82ac I len: 40 first: True last: True
        b'\x02\x00\x0250\x81l@\xa6\xdbffff\x1e\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [374/377] 0x82d4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81m@\xa6\xdb\x99\x99\x99\x99Q\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [375/378] 0x82fc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81n@\xa6\xdb\xcc\xcc\xcc\xcc\x84\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [376/379] 0x8324 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81o@\xa6\xdb\xff\xff\xff\xff\xb7\xc4y\xd0\x00\xc0\x8f:\x00\x00\x00\x00\x00\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [377/380] 0x834c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81p@\xa6\xdc3332\xeaE\xb9db@\x05I\xd0\xc8\xb7\x7f\xff\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [378/381] 0x8374 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81q@\xa6\xdcffff\x1dE\xb9\xbb\x97@\x05:uW<\xbbr\xc4y\xd0\x00\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [379/382] 0x839c I len: 40 first: True last: True
        b"\x02\x00\x0250\x81r@\xa6\xdc\x99\x99\x99\x99PE\xba\x86\x03@\x05'\xae\xa6`O\x96E+\xc2\x05\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [380/383] 0x83c4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81s@\xa6\xdc\xcc\xcc\xcc\xcc\x83E\xba\x91%@\x05\x14\xe8\x99?\xb4\xecE+\xc2\x05\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [381/384] 0x83ec I len: 40 first: True last: True
        b'\x02\x00\x0250\x81t@\xa6\xdc\xff\xff\xff\xff\xb6E\xba\x0b\xd2@\x05\x02#\xb7Rt\xacE+;S\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [382/385] 0x8414 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81u@\xa6\xdd3332\xe9E\xba\x02\x9c@\x04\xed\xa7\xc8\xe7d(E+;S\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [383/386] 0x843c I len: 40 first: True last: True
        b"\x02\x00\x0250\x81v@\xa6\xddffff\x1cE\xba=v@\x04\xda\xe1\xbd\xe8\xeb\xe7E*\xa7'\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [384/387] 0x8464 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81w@\xa6\xdd\x99\x99\x99\x99OE\xba^\xb1@\x04\xc8\x1b\xcd\x95!\xd0E*\xa7'\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [385/388] 0x848c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81x@\xa6\xdd\xcc\xcc\xcc\xcc\x82E\xb9\xe7\xa1@\x04\xb3\xa0\xee\x19#\xbdE*~\xbe\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [386/389] 0x84b4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81y@\xa6\xdd\xff\xff\xff\xff\xb5E\xb9\xe5\x89@\x04\xa0\xdb\x1a\x92*9E*~\xbe\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [387/390] 0x84dc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81z@\xa6\xde3332\xe8E\xbaOf@\x04\x8e\x14\xf8\xa4\xc0\x08E*\xcf\x90\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [388/391] 0x8504 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81{@\xa6\xdeffff\x1bE\xba\x0f\xd3@\x04y\x9a\xdb\xd3\x86$E*\xcf\x90\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [389/392] 0x852c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81|@\xa6\xde\x99\x99\x99\x99NE\xb9)H@\x04f\xd3\xbd\xa1\xb6\x9eE*\xcf\x90\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [390/393] 0x8554 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81}@\xa6\xde\xcc\xcc\xcc\xcc\x81E\xb8\xac\xb3@\x04T\r\xda\xa3C\x9cE*VU\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [391/394] 0x857c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81~@\xa6\xde\xff\xff\xff\xff\xb4E\xb8\x89O@\x04?\x92\xf48U\xb2E*VU\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [392/395] 0x85a4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x7f@\xa6\xdf3332\xe7E\xb8\x1e\xcd@\x04,\xcc\xde\x06\xa8\xc6E)\xf8\x0b\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [393/396] 0x85cc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x80@\xa6\xdfffff\x1aE\xb8\xe5\x8c@\x04\x1a\x06\xf8]\x8a\xc0E)\xf8\x0b\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [394/397] 0x85f4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x81@\xa6\xdf\x99\x99\x99\x99ME\xba\x07\xf9@\x04\n\xaa\xb9\x8dU\xf4E);w\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [395/398] 0x861c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x82@\xa6\xdf\xcc\xcc\xcc\xcc\x80E\xb9\xcaz@\x03\xf7\xe4\xd8\xb1\x05[E);w\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [396/399] 0x8644 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x83@\xa6\xdf\xff\xff\xff\xff\xb3E\xb9\x18\xe0@\x03\xe5\x1f\xc3\x90\x8b3E) \x87\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [397/400] 0x866c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x84@\xa6\xe03332\xe6E\xb9\xf2\\@\x03\xd0\xa3\xe2z\xd1\xc3E)\x13\x0e\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [398/401] 0x8694 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x85@\xa6\xe0ffff\x19E\xbaT3@\x03\xbd\xdd\xe6\xf3\xd3\x01E)\x13\x0e\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [399/402] 0x86bc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x86@\xa6\xe0\x99\x99\x99\x99LE\xb9=y@\x03\xab\x19\x05\x8f\x1b\\E)\x05\x96\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [400/403] 0x86e4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x87@\xa6\xe0\xcc\xcc\xcc\xcc\x7fE\xb9\x11\x1b@\x03\x96\x9d\x0e\x12\xf8\x96E)\x05\x96\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [401/404] 0x870c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x88@\xa6\xe0\xff\xff\xff\xff\xb2E\xb9\xa9\x17@\x03\x83\xd7\x07X\xc5(E(\xea\xa6\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [402/405] 0x8734 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\x89@\xa6\xe13332\xe5E\xb9,\xd1@\x03o\\'\xdc\xc7\x16E(\xea\xa6\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [403/406] 0x875c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x8a@\xa6\xe1ffff\x18E\xb8tR@\x03\\\x96b3\xadAE(c\xf3\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [404/407] 0x8784 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x8b@\xa6\xe1\x99\x99\x99\x99KE\xb8\xe5\xdc@\x03I\xd0750\xcfE(c\xf3\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [405/408] 0x87ac I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x8c@\xa6\xe1\xcc\xcc\xcc\xcc~E\xb8\x9a3@\x035UU\x97\x10RE(qk\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [406/409] 0x87d4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x8d@\xa6\xe1\xff\xff\xff\xff\xb1E\xb7\xb0\xdb@\x03"\x90hv\x9bhE(I\x02\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [407/410] 0x87fc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x8e@\xa6\xe23332\xe4E\xb8M\x14@\x03\x0f\xc9P\xab3\x1fE(I\x02\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [408/411] 0x8824 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\x8f@\xa6\xe2ffff\x17E\xb9w\xeb@\x02\xfbNe\xfc\x00aE'\xcf\xc8\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [409/412] 0x884c I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\x90@\xa6\xe2\x99\x99\x99\x99JE\xb9\x97:@\x02\xe8\x89\xb7\xca\x82\xa5E'\xcf\xc8\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [410/413] 0x8874 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\x91@\xa6\xe2\xcc\xcc\xcc\xcc}E\xb9\xa6\xd6@\x02\xda\xe19\xbb\xf3\xccE'\xdd@\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [411/414] 0x889c I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\x92@\xa6\xe2\xff\xff\xff\xff\xb0E\xba>\xe6@\x02\xc6g>\x84W\xe9E'\xdd@\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [412/415] 0x88c4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x93@\xa6\xe33332\xe3E\xba\x97\x8b@\x02\xb3\xa0S\x85\xc2LE( \x9a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [413/416] 0x88ec I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x94@\xa6\xe3ffff\x16E\xba3\xef@\x02\xa0\xda\x82\xa9s\xccE( \x9a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [414/417] 0x8914 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\x95@\xa6\xe3\x99\x99\x99\x99IE\xba\x16d@\x02\x8c_mO\x90\xccE'\xc2P\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [415/418] 0x893c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x96@\xa6\xe3\xcc\xcc\xcc\xcc|E\xbal\xf1@\x02y\x99\x7f\x1d\xe9\x1fE( \x9a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [416/419] 0x8964 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x97@\xa6\xe3\xff\xff\xff\xff\xafE\xb9\xbfD@\x02f\xd3z\x85\xd8\x1cE( \x9a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [417/420] 0x898c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x98@\xa6\xe43332\xe2E\xb9\x95&@\x02RX\x96=\x0c\x9bE(\x13!\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [418/421] 0x89b4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x99@\xa6\xe4ffff\x15E\xb9\xbbW@\x02?\x92\x98\x93\xeboE(\x13!\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [419/422] 0x89dc I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\x9a@\xa6\xe4\x99\x99\x99\x99HE\xb9\xdf\x0f@\x02,\xcc\x9f/\x0f\x17E'~\xf6\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [420/423] 0x8a04 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\x9b@\xa6\xe4\xcc\xcc\xcc\xcc{E\xb8q\xad@\x02\x1a\x06\xa7\xecU(E'~\xf6\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [421/424] 0x8a2c I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\x9c@\xa6\xe4\xff\xff\xff\xff\xaeE\xb6\xa1+@\x02\x05\x8b\xd1\x81iWE'\xc2P\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [422/425] 0x8a54 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\x9d@\xa6\xe53332\xe1E\xb6\xe8\\@\x01\xf2\xc5\xc5\xfah|E'\xc2P\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [423/426] 0x8a7c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x9e@\xa6\xe5ffff\x14E\xb7\xaa\x0e@\x01\xdeJ\xe0\x18\x03,E)\x13\x0e\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [424/427] 0x8aa4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\x9f@\xa6\xe5\x99\x99\x99\x99GE\xb7R5@\x01\xcb\x84\xea\xf7k\xa7E(I\x03\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [425/428] 0x8acc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xa0@\xa6\xe5\xcc\xcc\xcc\xcczE\xb6\xd0B@\x01\xbd\xdd\xaa\xc6\xe4UE(I\x03\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [426/429] 0x8af4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xa1@\xa6\xe5\xff\xff\xff\xff\xadE\xb7_\xd4@\x01\xa9b\xc6~\x18\xd5E(\x99\xd4\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [427/430] 0x8b1c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xa2@\xa6\xe63332\xe0E\xb7^\xb4@\x01\x96\x9c\xcf\xc3\xe7\x81E(\x99\xd4\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [428/431] 0x8b44 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xa3@\xa6\xe6ffff\x13E\xb6J\xc7@\x01\x82!\xd9\xe1\x80\x18E'\x8co\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [429/432] 0x8b6c I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xa4@\xa6\xe6\x99\x99\x99\x99FE\xb6\xb8\x11@\x01o[\xe2\x9e\xc6)E'\x8co\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [430/433] 0x8b94 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xa5@\xa6\xe6\xcc\xcc\xcc\xccyE\xb7=\x14@\x01Z\xe1\x12\x9aA\x95E'\x05\xbc\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [431/434] 0x8bbc I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xa6@\xa6\xe6\xff\xff\xff\xff\xacE\xb6>\xd8@\x01H\x1b\x00\xac\xd9}E'\x05\xbc\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [432/435] 0x8be4 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xa7@\xa6\xe73332\xdfE\xb5\xf6K@\x015U\x05%\xda\xbbE' \xac\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [433/436] 0x8c0c I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xa8@\xa6\xe7ffff\x12E\xb6\xd8X@\x01 \xda)\xee!{E'\xa7_\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [434/437] 0x8c34 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xa9@\xa6\xe7\x99\x99\x99\x99EE\xb6c\xc1@\x01\x0e\x142\xabg\x8dE'\xa7_\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [435/438] 0x8c5c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xaa@\xa6\xe7\xcc\xcc\xcc\xccxE\xb5\x00\xf1@\x00\xfbN)\xcf\x11\xb6E&\xb4\xea\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [436/439] 0x8c84 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xab@\xa6\xe7\xff\xff\xff\xff\xabE\xb4\xd6\x07@\x00\xe6\xd3Lu6\rE&\xb4\xea\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [437/440] 0x8cac I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xac@\xa6\xe83332\xdeE\xb4\xb3F@\x00\xd4\x0eV\xcc7{E( \x9a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [438/441] 0x8cd4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xad@\xa6\xe8ffff\x11E\xb4\xc6\x03@\x00\xc1Gd\xde\xb2\x07E( \x9a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [439/442] 0x8cfc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xae@\xa6\xe8\x99\x99\x99\x99DE\xb6)7@\x00\xac\xccq\x1em\x08E(I\x02\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [440/443] 0x8d24 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xaf@\xa6\xe8\xcc\xcc\xcc\xccwE\xb7z\x93@\x00\x9a\x07\x88\xca\xc5\x8bE(\xc2=\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [441/444] 0x8d4c I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xb0@\xa6\xe8\xff\xff\xff\xff\xaaE\xb79'@\x00\x8a\xaaJ\x82\xf7\xccE(\xc2=\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [442/445] 0x8d74 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xb1@\xa6\xe93332\xddE\xb6\x9f+@\x00w\xe5mb\x84\xfbE)\x05\x96\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [443/446] 0x8d9c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xb2@\xa6\xe9ffff\x10E\xb7&\x93@\x00cio\x7f\xfa\xf7E)\x05\x96\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [444/447] 0x8dc4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xb3@\xa6\xe9\x99\x99\x99\x99CE\xb7\x04\x0f@\x00P\xa3j\xe7\xe9\xf4E)\x13\x0e\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [445/448] 0x8dec I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xb4@\xa6\xe9\xcc\xcc\xcc\xccvE\xb6+K@\x00=\xdd\x8a\x0b\x99[E)\x13\x0e\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [446/449] 0x8e14 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xb5@\xa6\xe9\xff\xff\xff\xff\xa9E\xb5\xf0\xb1@\x00)b\x8f\xe4\xed\x1fE)qX\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [447/450] 0x8e3c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xb6@\xa6\xea3332\xdcE\xb6\x7f\xef@\x00\x16\x9c\x9f\x91#\x08E)qX\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [448/451] 0x8e64 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xb7@\xa6\xeaffff\x0fE\xb6\x8d\xf3@\x00\x02!\xb0\x15"\xddE(\xea\xa6\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [449/452] 0x8e8c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xb8@\xa6\xea\x99\x99\x99\x99BE\xb6;c?\xff\xde\xb9\xa5\xe9`\x16E(\xb4\xc5\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [450/453] 0x8eb4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xb9@\xa6\xea\xcc\xcc\xcc\xccuE\xb69\xdf?\xff\xb5\xc1\xaeh\x90\xe3E(\xb4\xc5\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [451/454] 0x8edc I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xba@\xa6\xea\xff\xff\xff\xff\xa8E\xb5\xde\xfd?\xff\x905\x94'[\x8eE);x\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [452/455] 0x8f04 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xbb@\xa6\xeb3332\xdbE\xb5\x9b\x01?\xffg?\xdd\xb7\xe9\x10E);x\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [453/456] 0x8f2c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xbc@\xa6\xebffff\x0eE\xb5\x9f\xce?\xffA\xb3\xe2e\xa6\xb8E);w\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [454/457] 0x8f54 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xbd@\xa6\xeb\x99\x99\x99\x99AE\xb5\xb1\xab?\xff\x18\xbe\x15\x8f\xca\xe4E);w\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [455/458] 0x8f7c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xbe@\xa6\xeb\xcc\xcc\xcc\xcctE\xb6 \xa5?\xfe\xf32+N\x9b\xdaE(\xea\xa6\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [456/459] 0x8fa4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xbf@\xa6\xeb\xff\xff\xff\xff\xa7E\xb5\x86\xac?\xfe\xca<h\x12Z\xe1E(c\xf3\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [457/460] 0x8fcc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xc0@\xa6\xec3332\xdaE\xb5C\x91?\xfe\xae\xed\xde\x17\xb1bE(c\xf3\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [458/461] 0x8ff4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xc1@\xa6\xecffff\rE\xb5\xd8\xc0?\xfe\x85\xf8$u\x0bEE( \x9a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [459/462] 0x901c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xc2@\xa6\xec\x99\x99\x99\x99@E\xb61%?\xfe`l5\xef\x97gE( \x9a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [460/463] 0x9044 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xc3@\xa6\xec\xcc\xcc\xcc\xccsE\xb5\xb4\x13?\xfe7vNo\riE'q}\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [461/464] 0x906c I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xc4@\xa6\xec\xff\xff\xff\xff\xa6E\xb6XN?\xfe\x11\xea_\xe9\x99\x8cE'q}\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [462/465] 0x9094 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xc5@\xa6\xed3332\xd9E\xb7\xa5\x19?\xfd\xe8\xf4\xbb\x9cK\x90E'\xcf\xc8\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [463/466] 0x90bc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xc6@\xa6\xedffff\x0cE\xb7\x0eQ?\xfd\xc3h\x93}6\x8cE(\x99\xd4\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [464/467] 0x90e4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xc7@\xa6\xed\x99\x99\x99\x99?E\xb6\xb0O?\xfd\x9ar\xc6\xa7Z\xb8E(\x99\xd4\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [465/468] 0x910c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xc8@\xa6\xed\xcc\xcc\xcc\xccrE\xb7/\x89?\xfdt\xe6\xef\x99aeE(\xc2=\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [466/469] 0x9134 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xc9@\xa6\xed\xff\xff\xff\xff\xa5E\xb6U\xbd?\xfdK\xfc\xd3\xd6\x1e\xf0E(\xc2=\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [467/470] 0x915c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xca@\xa6\xee3332\xd8E\xb4\xd6\xab?\xfd&n\xba\xa5\xb7\xb5E(\xcf\xb5\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [468/471] 0x9184 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xcb@\xa6\xeeffff\x0bE\xb5\x9c6?\xfc\xfdv\x81\x02\xbd\xb5E(\xcf\xb5\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [469/472] 0x91ac I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xcc@\xa6\xee\x99\x99\x99\x99>E\xb6\xaf\x06?\xfc\xd7\xe8l\x16\x9bME(\x99\xd4\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [470/473] 0x91d4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xcd@\xa6\xee\xcc\xcc\xcc\xccqE\xb5\xf3*?\xfc\xae\xf1\xdf@\xa6NE(\x99\xd4\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [471/474] 0x91fc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xce@\xa6\xee\xff\xff\xff\xff\xa4E\xb5\xa7\x04?\xfc\x89e\xb1\xcc;BE(I\x03\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [472/475] 0x9224 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xcf@\xa6\xef3332\xd7E\xb6b<?\xfc`o\xf8)\x95%E'\xcf\xc8\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [473/476] 0x924c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xd0@\xa6\xefffff\nE\xb6\x1f\xb1?\xfcA\xb7\x94"\xc8\x82E\'\xcf\xc8\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [474/477] 0x9274 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xd1@\xa6\xef\x99\x99\x99\x99=E\xb5a\xec?\xfc\x1c+\xdc\x03\xc2,E'V\x8d\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [475/478] 0x929c I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xd2@\xa6\xef\xcc\xcc\xcc\xccpE\xb5\xea\\?\xfb\xf6\x9f\xae\x8fW E'V\x8d\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [476/479] 0x92c4 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xd3@\xa6\xef\xff\xff\xff\xff\xa3E\xb5\xe2\xae?\xfb\xcd\xaa\x13\xdb\xa4\x00E'.$\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [477/480] 0x92ec I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xd4@\xa6\xf03332\xd6E\xb4\xf8K?\xfb\xa8\x1dWx7IE'.$\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [478/481] 0x9314 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xd5@\xa6\xf0ffff\tE\xb4\xa2\xb3?\xfb\x7f$\xd1\x08fkE'q\x7f\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [479/482] 0x933c I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xd6@\xa6\xf0\x99\x99\x99\x99<E\xb5Z\xa2?\xfbY\xa3\xf6\xc8\xaa\x94E'\x05\xbc\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [480/483] 0x9364 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xd7@\xa6\xf0\xcc\xcc\xcc\xccoE\xb4\xb4;?\xfb0\xae\xc7\xd0\xc1NE'\x05\xbc\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [481/484] 0x938c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xd8@\xa6\xf0\xff\xff\xff\xff\xa2E\xb3\xd9c?\xfb\x0b B\xe4\x908E&\xcf\xdb\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [482/485] 0x93b4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xd9@\xa6\xf13332\xd5E\xb3\xbb\xc4?\xfa\xe2)|t\xfa\x12E&\xcf\xdb\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [483/486] 0x93dc I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xda@\xa6\xf1ffff\x08E\xb46I?\xfa\xbc\x99Efm\xf3E'\x05\xbc\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [484/487] 0x9404 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xdb@\xa6\xf1\x99\x99\x99\x99;E\xb5\x18~?\xfa\x97\n\xb3\xadncE'\x05\xbc\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [485/488] 0x942c I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xdc@\xa6\xf1\xcc\xcc\xcc\xccnE\xb6\x0c\x14?\xfan\x13B\x93\x174E'q~\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [486/489] 0x9454 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xdd@\xa6\xf1\xff\xff\xff\xff\xa1E\xb6D\x99?\xfaH\x87\x9b\x85$,E'\xf81\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [487/490] 0x947c I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xde@\xa6\xf23332\xd4E\xb6\x19\xeb?\xfa\x1f\x92\x177\xdabE'\xf81\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [488/491] 0x94a4 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xdf@\xa6\xf2ffff\x07E\xb5h)?\xf9\xfa\x06\xff\x18\xe9\x05E'\xc2O\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [489/492] 0x94cc I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xe0@\xa6\xf2\x99\x99\x99\x99:E\xb58\x9a?\xf9\xdb]\xfd6B\xb2E'\xc2O\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [490/493] 0x94f4 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xe1@\xa6\xf2\xcc\xcc\xcc\xccmE\xb56E?\xf9\xb2Y_Md\xa2E'V\x8d\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [491/494] 0x951c I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xe2@\xa6\xf2\xff\xff\xff\xff\xa0E\xb5r\xf8?\xf9\x8c\xcd\x8br\x9e\xeeE'V\x8d\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [492/495] 0x9544 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xe3@\xa6\xf33332\xd3E\xb5\x7f\x0f?\xf9gAk\xdc\x13\x91E'q}\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [493/496] 0x956c I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xe4@\xa6\xf3ffff\x06E\xb6\nP?\xf9>L\x1c\xe4&\x1aE'q}\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [494/497] 0x9594 I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xe5@\xa6\xf3\x99\x99\x99\x999E\xb7\x0b\xac?\xf9\x15Uq\x1f>\x1eE'\xcf\xc8\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [495/498] 0x95bc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xe6@\xa6\xf3\xcc\xcc\xcc\xcclE\xb6\xaf\x97?\xf8\xef\xe4Q\x8c<\xbaE(I\x03\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [496/499] 0x95e4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xe7@\xa6\xf3\xff\xff\xff\xff\x9fE\xb6\xd3\xb3?\xf8\xc6\xd4\xb4\xb2\xfe\xc5E(I\x03\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [497/500] 0x960c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xe8@\xa6\xf43332\xd2E\xb8\x1f\x9a?\xf8\xa1H\xee\xb6\x18\xc1E(\xc2<\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [498/501] 0x9634 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xe9@\xa6\xf4ffff\x05E\xb8z\xbb?\xf8xRt\x02HDE(\xc2<\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [499/502] 0x965c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xea@\xa6\xf4\x99\x99\x99\x998E\xb7;x?\xf8R\xc9y\xc1{\xcbE)qX\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [500/503] 0x9684 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xeb@\xa6\xf4\xcc\xcc\xcc\xcckE\xb7\x1c\xcc?\xf8)\xd29\xb8<\x1cE)qX\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [501/504] 0x96ac I len: 40 first: True last: True
        b"\x02\x00\x0250\x81\xec@\xa6\xf4\xff\xff\xff\xff\x9eE\xb7'\xef?\xf8\x04D\xe1\x98\xff@E*-\xec\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [502/505] 0x96d4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xed@\xa6\xf53332\xd1E\xb5\xf5+?\xf7\xde\xc0`\xf2b\x88E*\xb4\xa0\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [503/506] 0x96fc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xee@\xa6\xf5ffff\x04E\xb5\xae\xca?\xf7\xb5\xc3\x85,\xaa\xeeE*\xb4\xa0\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [504/507] 0x9724 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xef@\xa6\xf5\x99\x99\x99\x997E\xb6;\xa3?\xf7\x907v\xa72\xdfE*\xcf\x90\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [505/508] 0x974c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xf0@\xa6\xf5\xcc\xcc\xcc\xccjE\xb5\xe3N?\xf7q\x81\xaa\x184\xaaE*\xcf\x90\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [506/509] 0x9774 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xf1@\xa6\xf5\xff\xff\xff\xff\x9dE\xb4\xe6\xff?\xf7K\xf3\xa7N6\xc5E)\x8cI\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [507/510] 0x979c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xf2@\xa6\xf63332\xd0E\xb5\xea4?\xf7"\xfd\x8axPtE)\x8cI\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [508/511] 0x97c4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xf3@\xa6\xf6ffff\x03E\xb6\xffA?\xf6\xfdq\x03j@\x10E(\xea\xa6\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [509/512] 0x97ec I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xf4@\xa6\xf6\x99\x99\x99\x996E\xb6z\x16?\xf6\xd4{Z\xd8\xad@E(\xea\xa6\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [510/513] 0x9814 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xf5@\xa6\xf6\xcc\xcc\xcc\xcciE\xb6\x8a\xd6?\xf6\xae\xf2\x0cS\x91wE(~\xe3\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [511/514] 0x983c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xf6@\xa6\xf6\xff\xff\xff\xff\x9cE\xb7\x02\xb2?\xf6\x85\xfa\x9f}\x7f\x1cE(qk\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [512/515] 0x9864 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xf7@\xa6\xf73332\xcfE\xb6W\xd2?\xf6`mK\xa2\x87\x13E(qk\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [513/516] 0x988c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xf8@\xa6\xf7ffff\x02E\xb5\xfb\xa8?\xf67x6D:\xc2E(\xb4\xc5\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [514/517] 0x98b4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xf9@\xa6\xf7\x99\x99\x99\x995E\xb6\xa7\xf9?\xf6\x11\xecU\x9c\xa6\x94E(\xb4\xc5\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [515/518] 0x98dc I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xfa@\xa6\xf7\xcc\xcc\xcc\xcchE\xb6\xf3\xa7?\xf5\xe8\xf6v\xa4\xa6=E)\x8cI\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [516/519] 0x9904 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xfb@\xa6\xf7\xff\xff\xff\xff\x9bE\xb6u\xd9?\xf5\xc3k\nAe\x90E)\x8cI\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [517/520] 0x992c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xfc@\xa6\xf83332\xceE\xb6\xa6\x88?\xf5\x9aw\xf3\xd2K&E)\xf8\x0c\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [518/521] 0x9954 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xfd@\xa6\xf8ffff\x01E\xb7\x01\xbe?\xf5t\xeb\xea\xa2) E)\xb4\xb2\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [519/522] 0x997c I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xfe@\xa6\xf8\x99\x99\x99\x994E\xb6\xf8L?\xf5K\xf3\xdc\xba\xf0\x97E)\xb4\xb2\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [520/523] 0x99a4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x81\xff@\xa6\xf8\xcc\xcc\xcc\xccgE\xb6\xcb\xed?\xf50\xa4X\x15{\x92E*\x99\xaf\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [521/524] 0x99cc I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x00@\xa6\xf8\xff\xff\xff\xff\x9aE\xb6\x93(?\xf5\x07\xae \x94\xe7\x18E*\x99\xaf\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [522/525] 0x99f4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x01@\xa6\xf93332\xcdE\xb7#^?\xf4\xe2"\xab\xa9\x1c\xc4E+ b\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [523/526] 0x9a1c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x02@\xa6\xf9ffff\x00E\xb7:\x97?\xf4\xb90G\\;\xd5E+ b\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [524/527] 0x9a44 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x03@\xa6\xf9\x99\x99\x99\x993E\xb6\xa6\xb0?\xf4\x93\xa0w\xc54\xbdE*\xea\x80\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [525/528] 0x9a6c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x04@\xa6\xf9\xcc\xcc\xcc\xccfE\xb6\x93\xb8?\xf4j\xac\x1e"\xbc\xc3E+ a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [526/529] 0x9a94 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x05@\xa6\xf9\xff\xff\xff\xff\x99E\xb6\xd9\xc9?\xf4E\x1e\xf7\x14\x97gE+ a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [527/530] 0x9abc I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x06@\xa6\xfa3332\xccE\xb6\xcc)?\xf4\x1c)<`\xe0\x15E+\x05p\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [528/531] 0x9ae4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x07@\xa6\xfafffe\xffE\xb6\xb5\xc0?\xf3\xf6\x9d\x9a\xa8C\x15E+\x05p\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [529/532] 0x9b0c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x08@\xa6\xfa\x99\x99\x99\x992E\xb6\xbdF?\xf3\xd1\x11\x9eD\xef\x89E)\xdd\x1b\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [530/533] 0x9b34 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\t@\xa6\xfa\xcc\xcc\xcc\xcceE\xb6P\x9c?\xf3\xa8\x1b\xa9\xf7\x97\x10E)\xdd\x1b\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [531/534] 0x9b5c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\n@\xa6\xfa\xff\xff\xff\xff\x98E\xb5\x80\xd3?\xf3\x82\x8f5\x0b\xab/E*\x12\xfc\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [532/535] 0x9b84 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x0b@\xa6\xfb3332\xcbE\xb5\xe1\xb6?\xf3Y\x99\x8cz\x18_E*\x12\xfc\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [533/536] 0x9bac I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x0c@\xa6\xfbfffe\xfeE\xb6l\x13?\xf34\r\xdc\xe3\x9b\xb1E)\x13\x0e\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [534/537] 0x9bd4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\r@\xa6\xfb\x99\x99\x99\x991E\xb5\x8d\xb6?\xf3\x0b\x180\r\xc4\x0eE);w\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [535/538] 0x9bfc I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x0e@\xa6\xfb\xcc\xcc\xcc\xccdE\xb5WE?\xf2\xe5\x8cr\x99g\xb0E);w\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [536/539] 0x9c24 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x0f@\xa6\xfb\xff\xff\xff\xff\x97E\xb6\n\xa0?\xf2\xc6\xd4\x0f\xa3\xacBE(\xea\xa6\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [537/540] 0x9c4c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x10@\xa6\xfc3332\xcaE\xb6N`?\xf2\xa1H;\xc8\xe6\x8eE(\xea\xa6\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [538/541] 0x9c74 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x11@\xa6\xfcfffe\xfdE\xb5\xe0\xfe?\xf2xRb&<?E);x\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [539/542] 0x9c9c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x12@\xa6\xfc\x99\x99\x99\x990E\xb6\xeb\x15?\xf2R\xc6Pm\x90\x92E);x\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [540/543] 0x9cc4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x13@\xa6\xfc\xcc\xcc\xcc\xcccE\xb7l;?\xf2)\xd0\xcfSzfE);w\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [541/544] 0x9cec I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x14@\xa6\xfc\xff\xff\xff\xff\x96E\xb6\x8eG?\xf2\x04D\xabx\xaa6E);x\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [542/545] 0x9d14 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x15@\xa6\xfd3332\xc9E\xb6\xa6\x9c?\xf1\xde\xb8\xb4j\xac\xb2E);x\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [543/546] 0x9d3c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x16@\xa6\xfdfffe\xfcE\xb7\xcaQ?\xf1\xb5\xc3\x10\x1d^\xb5E);w\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [544/547] 0x9d64 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x17@\xa6\xfd\x99\x99\x99\x99/E\xb7\xddb?\xf1\x906\xb6\xed22E);w\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [545/548] 0x9d8c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x18@\xa6\xfd\xcc\xcc\xcc\xccbE\xb7v*?\xf1g@mJy5E);w\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [546/549] 0x9db4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x19@\xa6\xfd\xff\xff\xff\xff\x95E\xb7\xd2g?\xf1A\xb5\to\xc20E);w\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [547/550] 0x9ddc I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x1a@\xa6\xfe3332\xc8E\xb7\xcd\x86?\xf1\x18\xbe\xdaw\xb7\\E)\x13\x0e\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [548/551] 0x9e04 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x1b@\xa6\xfefffe\xfbE\xb7\x08x?\xf0\xf338\xbf\x1a]E(~\xe3\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [549/552] 0x9e2c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x1c@\xa6\xfe\x99\x99\x99\x99.E\xb6\x9es?\xf0\xca=k\xe9>\x88E(~\xe3\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [550/553] 0x9e54 I len: 40 first: True last: True
        b"\x02\x00\x0250\x82\x1d@\xa6\xfe\xcc\xcc\xcc\xccaE\xb6\xac\x9e?\xf0\xa1H\x0f\x13qaE'\xcf\xc8\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [551/554] 0x9e7c I len: 40 first: True last: True
        b"\x02\x00\x0250\x82\x1e@\xa6\xfe\xff\xff\xff\xff\x94E\xb6\xab\xaa?\xf0{\xbb\xf3\xc1*\xd8E'\xcf\xc8\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [552/555] 0x9ea4 I len: 40 first: True last: True
        b"\x02\x00\x0250\x82\x1f@\xa6\xff3332\xc7E\xb6\xc1\x0b?\xf0]\x03\xcbv!\xc5E'\xc2P\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [553/556] 0x9ecc I len: 40 first: True last: True
        b"\x02\x00\x0250\x82 @\xa6\xfffffe\xfaE\xb7\xe9e?\xf07{h\xac\xe0\x9eE'\xc2P\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [554/557] 0x9ef4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82!@\xa6\xff\x99\x99\x99\x99-E\xb9\xbd\x7f?\xf0\x11\xea\xf3\xc0n\x85E)\xdd\x1a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [555/558] 0x9f1c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82"@\xa6\xff\xcc\xcc\xcc\xcc`E\xba9\xdd?\xef\xd1\xeaM\xd5%aE)\xdd\x1a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [556/559] 0x9f44 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82#@\xa6\xff\xff\xff\xff\xff\x93E\xbaw\x83?\xef\x86\xd5jd;\x13E,\xea[\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [557/560] 0x9f6c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82$@\xa7\x003332\xc6E\xba\xfd\x13?\xef4\xe8?\xa7=\xc7E0\xcf \xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [558/561] 0x9f94 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82%@\xa7\x00fffe\xf9E\xbb#H?\xee\xe2\xfb\xfdr\xe7~E0\xcf \xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [559/562] 0x9fbc I len: 40 first: True last: True
        b'\x02\x00\x0250\x82&@\xa7\x00\x99\x99\x99\x99,E\xba\x0c"?\xee\x97\xe3\xb3\x9b$\xb4E1\xa6\xa4\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [560/563] 0x9fe4 I len: 40 first: True last: True
        b"\x02\x00\x0250\x82'@\xa7\x00\xcc\xcc\xcc\xcc_E\xb8cZ?\xeeE\xf7y\xefX\x12E1\xa6\xa4\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [561/564] 0xa00c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82(@\xa7\x00\xff\xff\xff\xff\x92E\xb8\x03\xcf?\xed\xfa\xe18\xa0b\nE0\xcf \xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00\x1c \x00'  # LRSH [562/565] 0xa034 I len: 28 first: True last: False
        b'\x02\x00\x0250\x82)@\xa7\x013332\xc5E\xb7\xec\xd6?\xed\xa8\xf5\xe7' # Logical data length 24 0x18
b'\x0f$\xff\x01'  # Visible record [5] at 0xa050 length 0xf24 version 0xff01
    b'\x00\x10A\x00'  # LRSH [563/566] 0xa054 I len: 16 first: False last: True
        b'}<lE0\xcf \xc4y\xd0\x00\x01' # Logical data length 12 0xc
    b'\x00(\x01\x00'  # LRSH [563/567] 0xa064 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82*@\xa7\x01fffe\xf8E\xb7A\xcd?\xedW\tK\xaf@\xcbE,\xb4y\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [564/568] 0xa08c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82+@\xa7\x01\x99\x99\x99\x99+E\xb7\x9fS?\xed\x0b\xf1\x92\xe8\xa2\x15E+H\xca\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [565/569] 0xa0b4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82,@\xa7\x01\xcc\xcc\xcc\xcc^E\xb8`a?\xec\xba\x04\xd2\xd6]oE+H\xca\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [566/570] 0xa0dc I len: 40 first: True last: True
        b'\x02\x00\x0250\x82-@\xa7\x01\xff\xff\xff\xff\x91E\xb7\xfe\xc6?\xecn\xec\xdc1\xd8\xc0E,H\xb8\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [567/571] 0xa104 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82.@\xa7\x023332\xc4E\xb7\xf1\xa3?\xec\x1d\x03/S.{E,H\xb8\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [568/572] 0xa12c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82/@\xa7\x02fffe\xf7E\xb8q\xad?\xeb\xe6f}\x80\n|E,;?\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [569/573] 0xa154 I len: 40 first: True last: True
        b'\x02\x00\x0250\x820@\xa7\x02\x99\x99\x99\x99*E\xb8V\x0e?\xeb\x94z\x8c\\\xcf\xe4E,;?\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [570/574] 0xa17c I len: 40 first: True last: True
        b'\x02\x00\x0250\x821@\xa7\x02\xcc\xcc\xcc\xcc]E\xb7\x03\x1a?\xebIfb\x85\x97\x84E,\xb4y\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [571/575] 0xa1a4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x822@\xa7\x02\xff\xff\xff\xff\x90E\xb7)\xc7?\xea\xf7v-\x1d\x89~E,;?\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [572/576] 0xa1cc I len: 40 first: True last: True
        b'\x02\x00\x0250\x823@\xa7\x033332\xc3E\xb7\x90\xac?\xea\xa5\x89\xea\xe935E,;?\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [573/577] 0xa1f4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x824@\xa7\x03fffe\xf6E\xb6\xd0\x92?\xeaZrK\xbc1tE+\xc2\x05\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [574/578] 0xa21c I len: 40 first: True last: True
        b'\x02\x00\x0250\x825@\xa7\x03\x99\x99\x99\x99)E\xb6\xa0\xef?\xea\x08\x8bt3;\x96E+\xc2\x05\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [575/579] 0xa244 I len: 40 first: True last: True
        b'\x02\x00\x0250\x826@\xa7\x03\xcc\xcc\xcc\xcc\\E\xb7\xb4\xf0?\xe9\xbdp*[\x14#E+H\xca\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [576/580] 0xa26c I len: 40 first: True last: True
        b'\x02\x00\x0250\x827@\xa7\x03\xff\xff\xff\xff\x8fE\xb7\x97)?\xe9k\x83\x8e\x8d\x18\x82E+H\xca\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [577/581] 0xa294 I len: 40 first: True last: True
        b'\x02\x00\x0250\x828@\xa7\x043332\xc2E\xb6\xed\xcd?\xe9 l\xad>\r\x82E+q3\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [578/582] 0xa2bc I len: 40 first: True last: True
        b'\x02\x00\x0250\x829@\xa7\x04fffe\xf5E\xb7UV?\xe8\xce\x7f\x9c\x1a\xad*E+\xc2\x05\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [579/583] 0xa2e4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82:@\xa7\x04\x99\x99\x99\x99(E\xb7Gz?\xe8\x83i\x14eG\x82E+\xc2\x05\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [580/584] 0xa30c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82;@\xa7\x04\xcc\xcc\xcc\xcc[E\xb6\xc4\xf8?\xe81{\xf0\x0e\xb1sE,-\xc7\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [581/585] 0xa334 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82<@\xa7\x04\xff\xff\xff\xff\x8eE\xb6\xd3s?\xe7\xdf\x90\xcb\xb8^\x81E,-\xc7\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [582/586] 0xa35c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82=@\xa7\x053332\xc1E\xb7\x17\x1f?\xe7\x94xW5\xebtE+\x99\x9c\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [583/587] 0xa384 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82>@\xa7\x05fffe\xf4E\xb6\xd5\x0f?\xe7B\x8d\xdd\x8aY\x8bE+\x99\x9c\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [584/588] 0xa3ac I len: 40 first: True last: True
        b"\x02\x00\x0250\x82?@\xa7\x05\x99\x99\x99\x99'E\xb6\x7f7?\xe7\x0b\xf1\x12\x1d\x98\x97E*\xcf\x90\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [585/589] 0xa3d4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82@@\xa7\x05\xcc\xcc\xcc\xccZE\xb6Fr?\xe6\xba\x05\xa5>\xb3\x9aE)c\xe0\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [586/590] 0xa3fc I len: 40 first: True last: True
        b'\x02\x00\x0250\x82A@\xa7\x05\xff\xff\xff\xff\x8dE\xb6\xaa9?\xe6n\xee!\xcdq7E)c\xe0\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [587/591] 0xa424 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82B@\xa7\x063332\xc0E\xb6\xbc\xca?\xe6\x1d\x04\xe1\xbb\xa2\x02E)\x8cI\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [588/592] 0xa44c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82C@\xa7\x06fffe\xf3E\xb6\xdc-?\xe5\xd1\xe9\x84\xb0D\xd7E)\x8cI\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [589/593] 0xa474 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82D@\xa7\x06\x99\x99\x99\x99&E\xb7\xc2\xb8?\xe5\x80\x03qk\xac\xf7E*~\xbe\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [590/594] 0xa49c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82E@\xa7\x06\xcc\xcc\xcc\xccYE\xb8pQ?\xe54\xe5\x1f\n\x973E*~\xbe\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [591/595] 0xa4c4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82F@\xa7\x06\xff\xff\xff\xff\x8cE\xb8y3?\xe4\xe2\xf9X\x92\x0c\xddE+\xdc\xf5\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [592/596] 0xa4ec I len: 40 first: True last: True
        b'\x02\x00\x0250\x82G@\xa7\x073332\xbfE\xb8nP?\xe4\x97\xe2\xd0\xdc\xa75E+\xdc\xf5\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [593/597] 0xa514 I len: 40 first: True last: True
        b"\x02\x00\x0250\x82H@\xa7\x07fffe\xf2E\xb7\xe1'?\xe4E\xf7\x90\xca\x94\xe4E,\xdc\xe2\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [594/598] 0xa53c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82I@\xa7\x07\x99\x99\x99\x99%E\xb7I+?\xe3\xf4\x0c[c.\xa3E-\xf7\xc0\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [595/599] 0xa564 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82J@\xa7\x07\xcc\xcc\xcc\xccXE\xb6\xa4\x9c?\xe3\xa8\xf4>X>\x85E-\xf7\xc0\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [596/600] 0xa58c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82K@\xa7\x07\xff\xff\xff\xff\x8bE\xb6\x0f\xad?\xe3W\x08^F\x17;E+H\xca\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [597/601] 0xa5b4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82L@\xa7\x083332\xbeE\xb5\xcf\xb2?\xe3\x0b\xf0\xa5\x7fx\x86E+H\xca\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [598/602] 0xa5dc I len: 40 first: True last: True
        b'\x02\x00\x0250\x82M@\xa7\x08fffe\xf1E\xb5\rp?\xe2\xba\x05\x81)%\x93E*\x12\xfb\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [599/603] 0xa604 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82N@\xa7\x08\x99\x99\x99\x99$E\xb4\xdbx?\xe2n\xec\xaa\x84\x83\x88E*\x12\xfb\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [600/604] 0xa62c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82O@\xa7\x08\xcc\xcc\xcc\xccWE\xb5q\x87?\xe21|\x8d!\xabKE(\xea\xa6\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [601/605] 0xa654 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82P@\xa7\x08\xff\xff\xff\xff\x8aE\xb5\xd9\xdc?\xe1\xe6j\x129\x9aUE(\xb4\xc4\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [602/606] 0xa67c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82Q@\xa7\t3332\xbdE\xb5E}?\xe1\x94y)\x9eA\x9fE(\xb4\xc4\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [603/607] 0xa6a4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82R@\xa7\tfffe\xf0E\xb5\xab\x81?\xe1I`\xfd\xa4`\x9dE)\xb4\xb2\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [604/608] 0xa6cc I len: 40 first: True last: True
        b'\x02\x00\x0250\x82S@\xa7\t\x99\x99\x99\x99#E\xb6\x9b\xa6?\xe0\xf7t=\x92\x1b\xf7E)\xb4\xb2\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [605/609] 0xa6f4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82T@\xa7\t\xcc\xcc\xcc\xccVE\xb6`\xcc?\xe0\xac\\MS\xfe\x85E*H\xdd\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [606/610] 0xa71c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82U@\xa7\t\xff\xff\xff\xff\x89E\xb6\x0e\xcd?\xe0Zr$\xb9\x88LE*H\xdd\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [607/611] 0xa744 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82V@\xa7\n3332\xbcE\xb6\xb6$?\xe0\x08\x86\xafR\x19\xa8E*VV\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [608/612] 0xa76c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82W@\xa7\nfffe\xefE\xb6\x84\x18?\xdfz\xdd\xed\x16\xf5\xe6E*-\xec\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [609/613] 0xa794 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82X@\xa7\n\x99\x99\x99\x99"E\xb5\xc9H?\xde\xd7\x06`%\xe1;E*-\xec\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [610/614] 0xa7bc I len: 40 first: True last: True
        b'\x02\x00\x0250\x82Y@\xa7\n\xcc\xcc\xcc\xccUE\xb6!\xb1?\xde@\xd4\x90\xbav\x89E)\xdd\x1b\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [611/615] 0xa7e4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82Z@\xa7\n\xff\xff\xff\xff\x88E\xb6W.?\xdd\x9c\xfd*/\xcdME)\xdd\x1b\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [612/616] 0xa80c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82[@\xa7\x0b3332\xbbE\xb6+K?\xdd\x06\xcf\xab\xd6\x04\x84E*c\xcd\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [613/617] 0xa834 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\\@\xa7\x0bfffe\xeeE\xb6\xd7\xdc?\xdcb\xf84:G\xfaE*c\xcd\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [614/618] 0xa85c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82]@\xa7\x0b\x99\x99\x99\x99!E\xb8\x1ad?\xdb\xcc\xc5\xbeha\x12E*\xcf\x90\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [615/619] 0xa884 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82^@\xa7\x0b\xcc\xcc\xcc\xccTE\xb8-M?\xdbQ\xe4{\x1a\x05eE+\x8c#\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [616/620] 0xa8ac I len: 40 first: True last: True
        b'\x02\x00\x0250\x82_@\xa7\x0b\xff\xff\xff\xff\x87E\xb6\xb6P?\xda\xae\x10]\x18R\xddE+\x8c#\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [617/621] 0xa8d4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82`@\xa7\x0c3332\xbaE\xb67\xa2?\xda\x17\xe0k\x8b\x04\xabE.H\x92\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [618/622] 0xa8fc I len: 40 first: True last: True
        b'\x02\x00\x0250\x82a@\xa7\x0cfffe\xedE\xb6R\xf1?\xd9t\x07E\x00 \xb7E.H\x92\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [619/623] 0xa924 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82b@\xa7\x0c\x99\x99\x99\x99 E\xb5\xde\xfd?\xd8\xdd\xd8\n\xeab\tE*\xcf\x90\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [620/624] 0xa94c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82c@\xa7\x0c\xcc\xcc\xcc\xccSE\xb6*\x03?\xd8:\x06\xa4`\x82!E*\xcf\x90\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [621/625] 0xa974 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82d@\xa7\x0c\xff\xff\xff\xff\x86E\xb6~W?\xd7\xa3\xcf*I\xae\xa0E+H\xca\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [622/626] 0xa99c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82e@\xa7\r3332\xb9E\xb6I\x16?\xd6\xff\xf9\x83\xbf@\x1cE+q3\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [623/627] 0xa9c4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82f@\xa7\rfffe\xecE\xb5\xbc\x15?\xd6i\xc8\t\xa95\xefE+q3\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [624/628] 0xa9ec I len: 40 first: True last: True
        b'\x02\x00\x0250\x82g@\xa7\r\x99\x99\x99\x99\x1fE\xb5^c?\xd5\xc5\xf2\xbc\xb8l\xc3E+ a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [625/629] 0xaa14 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82h@\xa7\r\xcc\xcc\xcc\xccRE\xb5p\x93?\xd5/\xc5\x06\xe7%=E+ a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [626/630] 0xaa3c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82i@\xa7\r\xff\xff\xff\xff\x85E\xb5>\xd7?\xd4\x8b\xee\x0b\x074\xa8E*\x12\xfc\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [627/631] 0xaa64 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82j@\xa7\x0e3332\xb8E\xb4\xb7\xc4?\xd3\xf5\xbc\xa6F\x82\x9bE*\x12\xfc\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [628/632] 0xaa8c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82k@\xa7\x0efffe\xebE\xb4k!?\xd3Q\xe7D\x00aOE)\x8cI\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [629/633] 0xaab4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82l@\xa7\x0e\x99\x99\x99\x99\x1eE\xb3\xe9\x17?\xd2\xbb\xb6\xda\xfb\x8b\xfdE)\x8cI\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [630/634] 0xaadc I len: 40 first: True last: True
        b'\x02\x00\x0250\x82m@\xa7\x0e\xcc\xcc\xcc\xccQE\xb3.\x1f?\xd2\x17\xde\x1f\x1b`\xaeE)qX\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [631/635] 0xab04 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82n@\xa7\x0e\xff\xff\xff\xff\x84E\xb3\x19\xda?\xd1\x9c\xfc5f\x88\xcbE)\x13\x0e\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [632/636] 0xab2c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82o@\xa7\x0f3332\xb7E\xb3\xb8\xcb?\xd1\x06\xcc\xa1\xb7$\xc5E)\x13\x0e\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [633/637] 0xab54 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82p@\xa7\x0ffffe\xeaE\xb4j\x15?\xd0b\xf6\x8c=\xb8\xc8E) \x87\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [634/638] 0xab7c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82q@\xa7\x0f\x99\x99\x99\x99\x1dE\xb4FM?\xcf\x99\xaf\xc6vn\x1bE) \x87\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [635/639] 0xaba4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82r@\xa7\x0f\xcc\xcc\xcc\xccPE\xb4\x91\xf7?\xceQ\xd6\xbd\x9f\xd6\xcaE)\x8cI\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [636/640] 0xabcc I len: 40 first: True last: True
        b'\x02\x00\x0250\x82s@\xa7\x0f\xff\xff\xff\xff\x83E\xb5\x17r?\xcd%\x80\xd1\xfe\x00KE)\x8cI\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [637/641] 0xabf4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82t@\xa7\x103332\xb6E\xb4\x8d\x8e?\xcb\xdd\xcc\x8dp~\xeeE);w\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [638/642] 0xac1c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82u@\xa7\x10fffe\xe9E\xb4.\xe7?\xca\xb1s\xf7#\xa4JE);w\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [639/643] 0xac44 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82v@\xa7\x10\x99\x99\x99\x99\x1cE\xb4\xf7\xbb?\xc9i\xc1;\x1e\xde\xe8E);w\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [640/644] 0xac6c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82w@\xa7\x10\xcc\xcc\xcc\xccOE\xb4\xfbl?\xc8=cq\x9e"\x95E);w\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [641/645] 0xac94 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82x@\xa7\x10\xff\xff\xff\xff\x82E\xb4]F?\xc6\xf5\xb3\x1c\x00\x14"E);w\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [642/646] 0xacbc I len: 40 first: True last: True
        b'\x02\x00\x0250\x82y@\xa7\x113332\xb5E\xb4\xab\xd5?\xc5\xae\x04\x93/\x0e\xe1E)\xdd\x1a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [643/647] 0xace4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82z@\xa7\x11fffe\xe8E\xb4\xa6#?\xc4\x81\x9e\xda\xbeYlE)\xdd\x1a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [644/648] 0xad0c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82{@\xa7\x11\x99\x99\x99\x99\x1bE\xb3\xb0\x11?\xc39\xf7\xe2\xffc"E)\x05\x96\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [645/649] 0xad34 I len: 40 first: True last: True
        b"\x02\x00\x0250\x82|@\xa7\x11\xcc\xcc\xcc\xccNE\xb3\xa8'?\xc2\r\x97*\x8fUsE+ b\xc4y\xd0\x00\x01" # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [646/650] 0xad5c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82}@\xa7\x11\xff\xff\xff\xff\x81E\xb4|\xe6?\xc0\xc5\xe1\xa1\xbdeQE+ b\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [647/651] 0xad84 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82~@\xa7\x123332\xb4E\xb4\xdbx?\xbf\xd6\xea\xe8\x16\x98\xc8E*\xcf\x90\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [648/652] 0xadac I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x7f@\xa7\x12fffe\xe7E\xb4\x96\x88?\xbdG\x8b\xa3A\x11BE*\xcf\x90\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [649/653] 0xadd4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x80@\xa7\x12\x99\x99\x99\x99\x1aE\xb4\x95\x17?\xba\xee\xd62b\x88\x8bE+ a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [650/654] 0xadfc I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x81@\xa7\x12\xcc\xcc\xcc\xccME\xb4|\xe6?\xb8_eS\xf1\x18\xdcE+ a\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [651/655] 0xae24 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x82@\xa7\x12\xff\xff\xff\xff\x80E\xb3S\x1b?\xb6\x06\xb1\x054\xd8OE*~\xbf\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [652/656] 0xae4c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x83@\xa7\x133332\xb3E\xb1y\xdf?\xb3wK\x9e<`\xd9E(\xea\xa6\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [653/657] 0xae74 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x84@\xa7\x13fffe\xe6E\xaf\xef\x06?\xb0\xe7\xf7\xbf\xce\xbe>E(\xea\xa6\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [654/658] 0xae9c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x85@\xa7\x13\x99\x99\x99\x99\x19E\xae\x0b\xa0?\xad\x1eY&cA\x18E%\x8c\x94\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [655/659] 0xaec4 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x86@\xa7\x13\xcc\xcc\xcc\xccLE\xab\xa6W?\xa7\xff\xce\x9c\xbf\x02\xe0E%\x8c\x94\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [656/660] 0xaeec I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x87@\xa7\x13\xff\xff\xff\xff\x7fE\xa9\xd4\xdd?\xa3N8\xcc\ra\xe8E!\x06,\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [657/661] 0xaf14 I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x88@\xa7\x143332\xb2E\xa7\xba\xda?\x9c^\xffs\xb5\x03\x82E!\x06,\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00(\x01\x00'  # LRSH [658/662] 0xaf3c I len: 40 first: True last: True
        b'\x02\x00\x0250\x82\x89@\xa7\x14fffe\xe5E\xa5`K?\x92\xfc\x83\x8e$\x85\xf1E .\xa8\xc4y\xd0\x00\x01' # Logical data length 36 0x24
    b'\x00\x10\x01\x7f'  # LRSH [659/663] 0xaf64 I len: 16 first: True last: True
        b'\x02\x00\x0250\x00\x01\x02\x03\x04\x05\x06' # Logical data length 12 0xc
)


def test_basic_file():
    assert len(BASIC_FILE) == 44916
