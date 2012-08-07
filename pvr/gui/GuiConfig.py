import xbmc, xbmcgui, time, sys, threading, os, re, shutil, string, thread
from copy import deepcopy
from util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
from pvr.GuiHelper import MR_LANG


####### HBBTV SUPPOERT #############
E_SUPPROT_HBBTV		= True

E_WINDOW_WIDTH		= 1280
E_WINDOW_HEIGHT		= 720

############################ Windows ############################
# Setting Window Control Ids
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
E_Input06			= 2600
E_Input07			= 2700

# footer group
E_CTRL_GROP_FOOTER01 = 3100
E_CTRL_GROP_FOOTER02 = 3110
E_CTRL_GROP_FOOTER03 = 3120
E_CTRL_GROP_FOOTER04 = 3130
E_CTRL_GROP_FOOTER05 = 3140
E_CTRL_GROP_FOOTER06 = 3150
E_CTRL_GROP_FOOTER07 = 3160
E_CTRL_GROP_FOOTER08 = 3170

# footer button
E_CTRL_BTN_FOOTER01 = 3101
E_CTRL_BTN_FOOTER02 = 3111
E_CTRL_BTN_FOOTER03 = 3121
E_CTRL_BTN_FOOTER04 = 3131
E_CTRL_BTN_FOOTER05 = 3141
E_CTRL_BTN_FOOTER06 = 3151
E_CTRL_BTN_FOOTER07 = 3161
E_CTRL_BTN_FOOTER08 = 3171

# Setting Menu Group Ids
E_SUBMENU_LIST_ID			= 9000
E_SETUPMENU_GROUP_ID		= 9010

E_SETTING_MINI_TITLE		=	1001
E_SETTING_HEADER_TITLE		=	1002
E_SETTING_DESCRIPTION		=	1003
E_SETTING_PIP_SCREEN_IMAGE	=	8899

E_FAKE_BUTTON				=	999

# FirstTimeInstallation Button Ids
E_STEP_SELECT_LANGUAGE			=	0
E_STEP_VIDEO_AUDIO				=	1
E_STEP_ANTENNA					=	2
E_STEP_CHANNEL_SEARCH_CONFIG	=	3
E_STEP_DATE_TIME				=	4
E_STEP_RESULT					=	5

FIRST_TIME_INSTALLATION_STEP				= 6

E_FIRST_TIME_INSTALLATION_PREV				= 7001
E_FIRST_TIME_INSTALLATION_NEXT				= 7003
E_FIRST_TIME_INSTALLATION_NEXT_LABEL		= 7004

E_FIRST_TIME_INSTALLATION_STEP_IMAGE		= 8100
E_FIRST_TIME_INSTALLATION_STEP_IMAGE_BACK	= 8110

# Scan Heler Status
E_SCAN_HELPER_GROUP				= 1007
E_SCAN_HELPER_LABEL_STRENGTH	= 1005
E_SCAN_HELPER_PROGRESS_STRENGTH	= 1010
E_SCAN_HELPER_LABEL_QUALITY		= 1006
E_SCAN_HELPER_PROGRESS_QUALITY	= 1011

# TUNER TYPE
E_SIMPLE_LNB					= 0
E_DISEQC_1_0					= 1
E_DISEQC_1_1					= 2
E_MOTORIZE_1_2					= 3
E_MOTORIZE_USALS				= 4
E_ONE_CABLE						= 5

# TUNER CONNECTION TYPE
E_TUNER_SEPARATED				= 0
E_TUNER_LOOPTHROUGH				= 1

# TUNER CONFIG TYPE
E_SAMEWITH_TUNER				= 0
E_DIFFERENT_TUNER				= 1

# TUNER
E_TUNER_1						= 0
E_TUNER_2						= 1
E_TUNER_MAX						= 2

# ONECABLECOUNT
MAX_SATELLITE_CNT_ONECABLE		= 2

#RECORD
E_MAX_RECORD_COUNT				= 2

# Volume
VOLUME_STEP						= 4
MAX_VOLUME						= 100

# Time Mode
TIME_AUTOMATIC					= 0
TIME_MANUAL						= 1

# Network Mode
NET_DHCP						= 0
NET_STATIC						= 1

# Wifi Encript Type
ENCRIPT_TYPE_WEP				= 0
ENCRIPT_TYPE_WPA				= 1
ENCRIPT_TYPE_WPA2				= 2
ENCRIPT_TYPE_WPA_WPA2			= 3

# Wifi Password Type
PASSWORD_TYPE_ASCII				= 0
PASSWORD_TYPE_HEX				= 1

# Wifi Use Encrypt
NOT_USE_PASSWORD_ENCRYPT		= 0
USE_PASSWORD_ENCRYPT			= 1

# Wifi Use Hidden Ssid
NOT_USE_HIDDEN_SSID				= 0
USE_HIDDEN_SSID					= 1

# Network Type
NETWORK_ETHERNET				= 0
NETWORK_WIRELESS				= 1

# db table
E_SYNCHRONIZED  				= 0
E_ASYNCHRONIZED 				= 1
E_TABLE_ALLCHANNEL 				= 0
E_TABLE_ZAPPING 				= 1
E_REOPEN_FALSE					= 0
E_REOPEN_TRUE					= 1
E_EPG_DB_CF						= 1
E_EPG_DB_CF_GET_BY_CHANNEL		= 0
E_EPG_DB_CF_GET_BY_CURRENT		= 1
E_EPG_DB_CF_GET_BY_FOLLOWING	= 2
FLAG_ZAPPING_LOAD   			= 0
FLAG_ZAPPING_CHANGE 			= 1

# Tuner Config String Define
USER_ENUM_LIST_ON_OFF				= [ MR_LANG( 'Off' ), MR_LANG( 'On' ) ]
USER_ENUM_LIST_YES_NO				= [ MR_LANG( 'No' ), MR_LANG( 'Yes' ) ]
USER_ENUM_LIST_DHCP_STATIC			= [ MR_LANG( 'DHCP' ), MR_LANG( 'Static' ) ]
USER_ENUM_LIST_NETWORK_TYPE			= [ MR_LANG( 'Ethernet' ), MR_LANG( 'Wireless' ) ]
USER_ENUM_LIST_ENCRIPT_TYPE			= [ 'WEP', 'WPA', 'WPA2', 'WPA/WPA2' ]
USER_ENUM_LIST_PASSWORD_TYPE		= [ 'Ascii', 'Hex' ]

E_LIST_LNB_TYPE						= [ MR_LANG( 'Universal' ), MR_LANG( 'Single' ), MR_LANG( 'Userdefined' ) ]
E_LIST_SINGLE_FREQUENCY 			= [ '5150', '9750', '10600', '10750', '11300' ]
E_LIST_DISEQC_MODE					= [ 'Disable', '1 of 4', '2 of 4', '3 of 4', '4 of 4', 'Mini A', 'Mini B' ]
E_LIST_COMMITTED_SWITCH				= [ 'Disable', '1', '2', '3', '4' ]
E_LIST_UNCOMMITTED_SWITCH			= [ 'Disable', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16' ]
E_LIST_MOTORIZE_ACTION				= [ MR_LANG( 'Reset Limits' ), MR_LANG( 'Set Current Position for East Limit' ), MR_LANG( 'Set Current Position for West Limit' ) ]
E_LIST_ONE_CABLE_TUNER_FREQUENCY	= [ '1284', '1400', '1516', '1632', '1748', '1864', '1980', '2096' ]
E_LIST_ONE_CABLE_SCR				= [ 'SCR(0)', 'SCR(1)', 'SCR(2)', 'SCR(3)', 'SCR(4)', 'SCR(5)', 'SCR(6)', 'SCR(7)' ]

E_LIST_MY_LONGITUDE = [ MR_LANG( 'East' ), MR_LANG( 'West' ) ]
E_LIST_MY_LATITUDE  = [ MR_LANG( 'North' ), MR_LANG( 'South' ) ]

############################ Dialog ############################

G_DIALOG_HEADER_LABEL_ID			= 3005

# Settinf Dialog Control Ids
E_DialogSpinEx01	= 6110
E_DialogSpinEx02	= 6120
E_DialogSpinEx03	= 6130
E_DialogSpinEx04	= 6140

E_DialogInput01		= 6210
E_DialogInput02		= 6220
E_DialogInput03		= 6230
E_DialogInput04		= 6240
E_DialogInput05		= 6250
E_DialogInput06		= 6260
E_DialogInput07		= 6270
E_DialogInput08		= 6280
E_DialogInput09		= 6290

E_DialogSpinDay		= 6300


E_SETTING_DIALOG_BUTTON_CLOSE			= 6995
E_SETTING_DIALOG_BUTTON_OK_ID			= 6997
E_SETTING_DIALOG_BUTTON_CANCEL_ID		= 6999
E_SETTING_DIALOG_BACKGROUND_IMAGE_ID 	= 9001
E_SETTING_DIALOG_DEFAULT_GOURP_ID		= 9000
E_SETTING_DIALOG_MAIN_GOURP_ID			= 8000

# Transponder dialog type
E_MODE_ADD_NEW_TRANSPODER	= 0
E_MODE_EDIT_TRANSPODER		= 1

# Nermeric Keyboard Type
E_NUMERIC_KEYBOARD_TYPE_NUMBER	= 0
E_NUMERIC_KEYBOARD_TYPE_DATE	= 1
E_NUMERIC_KEYBOARD_TYPE_TIME	= 2
E_NUMERIC_KEYBOARD_TYPE_IP		= 3

# Input Keyboard Type
E_INPUT_KEYBOARD_TYPE_NO_HIDE	= False
E_INPUT_KEYBOARD_TYPE_HIDE		= True
E_INPUT_MAX						= 9999

# Dialog Satatus
E_DIALOG_STATE_YES		= 1
E_DIALOG_STATE_NO		= 2
E_DIALOG_STATE_CANCEL	= 3
E_DIALOG_STATE_ERROR	= 4


############################ Global Function For GUI ############################


def getSingleFrequenceIndex( selectedItem ) :
	for i in range( len ( E_LIST_SINGLE_FREQUENCY )	) :
		if( selectedItem == int( E_LIST_SINGLE_FREQUENCY[ i ] ) ) :
			return i
			
	return -1


def getCommittedSwitchindex( selectedItem ) :
	if selectedItem == 5 or selectedItem == 6 :
		return 0
	return selectedItem


def getOneCableTunerFrequencyIndex( selectedItem ) :
	for i in range( len ( E_LIST_ONE_CABLE_TUNER_FREQUENCY ) ) :
		if( selectedItem == E_LIST_ONE_CABLE_TUNER_FREQUENCY[ i ] ) :
			return i
			
	return -1


def MakeHexToIpAddr( aIpAddr ) :
	ip1 = 0
	ip2 = 0
	ip3 = 0
	ip4 = 0
	
	ip1 = ( aIpAddr & 0xff000000 ) >> 24
	ip2 = ( aIpAddr & 0x00ff0000 ) >> 16
	ip3 = ( aIpAddr & 0x0000ff00 ) >> 8
	ip4 = aIpAddr & 0x000000ff

	return ip1, ip2, ip3, ip4


def MakeStringToHex( aString ) :
	tempList = aString.split( '.', 3 )
	tempHex = ( int( tempList[0] ) << 24 ) | ( int( tempList[1] ) << 16 ) | ( int( tempList[2] ) << 8 ) | int( tempList[3] )
	return Hex2signed( '%08x' % tempHex )


def Hex2signed( s ) :
	value = long( s, 16 )
	if value > sys.maxint :
		value = value - 2L * sys.maxint - 2
	#assert -sys.maxint-1 <= value <= sys.maxint
	return int( value )
 

def NumericKeyboard( aKeyType, aTitle, aString, aMaxLength=None ) :
	dialog = xbmcgui.Dialog( )		
	value = dialog.numeric( aKeyType, aTitle, aString )
	if value == None or value == '' :
		return aString

	if len( value ) > aMaxLength and aMaxLength != None :
		value = value[ len ( value ) - aMaxLength :]

	if aKeyType == E_NUMERIC_KEYBOARD_TYPE_DATE :
		tempList = value.split( '/', 2 )
		value = '%02d.%02d.%04d' % ( int( tempList[0] ),  int( tempList[1] ),  int( tempList[2] ) )

	elif aKeyType == E_NUMERIC_KEYBOARD_TYPE_TIME :
		tempList = value.split( ':', 1 )
		value = '%02d:%02d' % ( int( tempList[0] ),  int( tempList[1] ) )
	return value


def InputKeyboard( aType, aTitle, aString, aMaxLength=None ) :
	dialog = xbmc.Keyboard( aString, aTitle, aType )
	dialog.setHiddenInput( aType )
	dialog.doModal( )
	if( dialog.isConfirmed( ) ) :
		value = dialog.getText( )
		if value == None or value == '' :
			return aString

		if len( value ) > aMaxLength and aMaxLength != None :
			value = value[ len ( value ) - aMaxLength :]
		return value
		
	else :
		return aString


def StringToHidden( aString=None ) :
	if aString == None or aString =='' :
		return ''
	length = len( aString )
	result = ''
	for i in range( length ) :
		result += '*'
	return result

	
############################ Global Class ############################


class ContextItem :
	def __init__( self, aDescription = 'None', aContextAction = -1 ) :
		self.mDescription = aDescription
		self.mContextAction = aContextAction

