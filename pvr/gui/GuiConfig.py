# Setting Menu Ids
E_LANGUAGE			= 0
E_PARENTAL			= 1
E_RECORDING_OPTION	= 2
E_AUDIO_SETTING		= 3
E_SCART_SETTING		= 4
E_HDMI_SETTING		= 5
E_IP_SETTING		= 6
E_FORMAT_HDD		= 7
E_FACTORY_RESET		= 8
E_ETC				= 9

# Description Label Id
E_SETTING_DESCRIPTION	=	1001


# Control Ids
E_SpinEx01			= 1100
E_SpinEx02			= 1200
E_SpinEx03			= 1300
E_SpinEx04			= 1400
E_SpinEx05			= 1500
E_SpinEx06			= 1600
E_SpinEx07			= 1700
E_SpinEx08			= 1800
E_SpinEx09			= 1900

E_Input01			= 2100
E_Input02			= 2200
E_Input03			= 2300
E_Input04			= 2400
E_Input05			= 2500

E_SlideMenuButton01	= 3310
E_SlideMenuButton02	= 3320
E_SlideMenuButton03	= 3330

# Setting Menu Group Ids
E_SUBMENU_LIST_ID			= 9000
E_SETUPMENU_GROUP_ID		= 9010

# Volume
VOLUME_STEP					= 4
MAX_VOLUME					= 100

# USER_CONTROL_TYPE_DEFINE
"""
USER_ENUM_LIST_YES_NO 			= [ 'No', 'Yes' ]
USER_ENUM_LIST_FORMAT_TYPE	 	= [ 'FAT', 'EXT3' ]
USER_ENUM_LIST_ON_OFF			= [ 'Off', 'On' ]
USER_ENUM_LIST_DVB_TYPE			= [ 'DVB-S (SD)', 'DVB-S2 (HD)' ]
USER_ENUM_LIST_FEC				= [ 'QPSK 1/2', 'QPSK 2/3', 'QPSK 3/4', 'QPSK 3/5', 'QPSK 4/5', 'QPSK 5/6', 'QPSK 8/9', 'QPSK 9/10', '8PSK 2/3', '8PSK 3/4', '8PSK 3/5', '8PSK 5/6', '8PSK 8/9', '8PSK 9/10' ]
USER_ENUM_LIST_POLARIZATION		= [ 'Horizontal', 'Vertical' ]
USER_ENUM_LIST_SYMBOL_RATE		= [ '22000 KS/s', '27500 KS/s' ]
"""

# Tuner Config String Define
USER_ENUM_LIST_ON_OFF				= [ 'Off', 'On' ]
E_LIST_LNB_TYPE						= [ 'Universal' , 'Single', 'Userdefined' ]
E_LIST_SINGLE_FREQUENCY 			= [ '5150', '9750', '10600', '10750', '11300' ]
E_LIST_DISEQC_MODE					= [ 'Disable', '1 of 4', '2 of 4', '3 of 4', '4 of 4', 'Mini A', 'Mini B' ]
E_LIST_COMMITTED_SWITCH				= [ 'Disable', '1', '2', '3', '4', 'Disable', 'Disable' ]
E_LIST_UNCOMMITTED_SWITCH			= [ 'Disable', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16' ]
E_LIST_ONE_CABLE_ACTION				= [ 'Reset Limits', 'Set Current Position for East Limit', 'Set Current Position for West Limit' ]
E_LIST_ONE_CABLE_TUNER_FREQUENCY	= [ '1284', '1400', '1516', '1632', '1748', '1864', '1980', '2096' ]

"""
E_LIST_TUNER_TYPE				= [ 'Simple LNB', 'DiSEqC 1.0', 'DiSEqC 1.1', 'Motorized, DiSEqC 1.2', 'Motorized, USALS', 'OneCable' ]
E_LIST_LNB_TYPE					= [ 'Universal' , 'Single', 'Userdefined' ]
E_LIST_SINGLE_FREQUENCY 		= [ '5150', '9750', '10600', '10750', '11300' ]
"""

def getSingleFrequenceIndex( selectedItem ) :
	for i in range( len ( E_LIST_SINGLE_FREQUENCY )	) :
		if( selectedItem == int( E_LIST_SINGLE_FREQUENCY[ i ] ) ) :
			return i
			
	return -1

def getOneCableTunerFrequencyIndex( selectedItem ) :
	for i in range( len ( E_LIST_ONE_CABLE_TUNER_FREQUENCY )	) :
		if( selectedItem == E_LIST_ONE_CABLE_TUNER_FREQUENCY[ i ] ) :
			return i
			
	return -1


class FooterMask(object):
	G_FOOTER_GROUP_STARTID				= 3100
	G_FOOTER_GROUP_IDGAP				= 10
	
	G_NUM_OF_FOOTER_ICON				= 5

	G_FOOTER_ICON_BACK_MASK				= 1 << 0
	G_FOOTER_ICON_OK_MASK				= 1 << 1
	G_FOOTER_ICON_SEARCH_MASK			= 1 << 2
	G_FOOTER_ICON_RECORD_MASK			= 1 << 3
	G_FOOTER_ICON_EDIT_MASK			    = 1 << 4

class HeaderDefine(object):
	G_HEADER_LABEL_ID					= 3001
	
'''
G_FOOTER_ICON_EXIT_MASK			= 1 << 1,
G_FOOTER_ICON_RED_MASK			= 1 << 4,
G_FOOTER_ICON_GREEN_MASK		= 1 << 5,
G_FOOTER_ICON_BLUE_MASK			= 1 << 6,
G_FOOTER_ICON_YELLOW_MASK		= 1 << 7,	
G_FOOTER_ICON_OPT_MASK			= 1 << 8,
G_FOOTER_ICON_PAUSE_MASK		= 1 << 9,
G_FOOTER_ICON_EDIT_MASK			= 1 << 10,	
G_FOOTER_ICON_PLAY_MASK			= 1 << 13,
G_FOOTER_ICON_MARK_MASK			= 1 << 14,
G_FOOTER_ICON_P_MASK			= 1 << 15,
G_FOOTER_ICON_NUM_0_MASK		= 1 << 16,
G_FOOTER_ICON_INFO_MASK			= 1 << 17,
G_FOOTER_ICON_DELETE_MASK		= 1 << 18,
G_FOOTER_ICON_FF_MASK			= 1 << 19,
G_FOOTER_ICON_REW_MASK			= 1 << 20,
G_FOOTER_ICON_REWFF_MASK		= 1 << 21,
G_FOOTER_ICON_NUMBER_MASK		= 1 << 22,
'''