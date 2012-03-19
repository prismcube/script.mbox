import xbmc
import xbmcgui
import sys
import time

from pvr.Util import LOG_TRACE, LOG_ERR, LOG_WARN

E_WINDOW_WIDTH		= 1280
E_WINDOW_HEIGHT		= 720


############################ Windows ############################
# Setting Menu Ids
E_LANGUAGE			= 0
E_PARENTAL			= 1
E_RECORDING_OPTION	= 2
E_AUDIO_SETTING		= 3
E_HDMI_SETTING		= 4
E_IP_SETTING		= 5
E_TIME_SETTING		= 6
E_FORMAT_HDD		= 7
E_FACTORY_RESET		= 8
E_ETC				= 9

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
E_SETTING_PIP_SCREEN_IMAGE	=	1004

E_FAKE_BUTTON				=	999

# FirstTimeInstallation Button Ids
E_STEP_SELECT_LANGUAGE			=	0
E_STEP_VIDEO_AUDIO				=	1
E_STEP_ANTENNA					=	2
E_STEP_CHANNEL_SEARCH_CONFIG	=	3
E_STEP_DATE_TIME				=	4
E_STEP_RESULT					=	5

FIRST_TIME_INSTALLATION_STEP			= 6

E_FIRST_TIME_INSTALLATION_PREV			= 7001
E_FIRST_TIME_INSTALLATION_NEXT			= 7003
E_FIRST_TIME_INSTALLATION_NEXT_LABEL	= 7004

E_FIRST_TIME_INSTALLATION_STEP_IMAGE		= 8100
E_FIRST_TIME_INSTALLATION_STEP_IMAGE_BACK	= 8110

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

# CAS
CAS_SLOT_NUM_1					= 0
CAS_SLOT_NUM_2					= 1

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


# Tuner Config String Define
USER_ENUM_LIST_ON_OFF				= [ 'Off', 'On' ]
USER_ENUM_LIST_YES_NO				= [ 'No', 'Yes' ]

E_LIST_LNB_TYPE						= [ 'Universal' , 'Single', 'Userdefined' ]
E_LIST_SINGLE_FREQUENCY 			= [ '5150', '9750', '10600', '10750', '11300' ]
E_LIST_DISEQC_MODE					= [ 'Disable', '1 of 4', '2 of 4', '3 of 4', '4 of 4', 'Mini A', 'Mini B' ]
E_LIST_COMMITTED_SWITCH				= [ 'Disable', '1', '2', '3', '4' ]
E_LIST_UNCOMMITTED_SWITCH			= [ 'Disable', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16' ]
E_LIST_MOTORIZE_ACTION				= [ 'Reset Limits', 'Set Current Position for East Limit', 'Set Current Position for West Limit' ]
E_LIST_ONE_CABLE_TUNER_FREQUENCY	= [ '1284', '1400', '1516', '1632', '1748', '1864', '1980', '2096' ]
E_LIST_ONE_CABLE_SCR				= [ 'SCR(0)', 'SCR(1)', 'SCR(2)', 'SCR(3)', 'SCR(4)', 'SCR(5)', 'SCR(6)', 'SCR(7)' ]


E_LIST_MY_LONGITUDE = [ 'East', 'West' ]
E_LIST_MY_LATITUDE  = [ 'North', 'South' ]


############################ Dialog ############################

G_DIALOG_HEADER_LABEL_ID			= 3005

# Settinf Dialog Control Ids
E_DialogSpinEx01	= 6110
E_DialogSpinEx02	= 6120
E_DialogSpinEx03	= 6130

E_DialogInput01		= 6210
E_DialogInput02		= 6220
E_DialogInput03		= 6230
E_DialogInput04		= 6240
E_DialogInput05		= 6250
E_DialogInput06		= 6260
E_DialogInput07		= 6270
E_DialogInput08		= 6280
E_DialogInput09		= 6290

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

############################ Global Class ############################

E_USER_DEFINE		= 0
E_TEST_FUNCTION_1	= 1
E_TEST_FUNCTION_2	= 2
E_TEST_FUNCTION_3	= 3


class ContextItem :

	def __init__( self, aDescription = 'None', aFunctionIndex = E_USER_DEFINE ) :
		self.mDescription = aDescription
		self.mFunctionIndex = aFunctionIndex

	def DoAction( self ) :
		if self.mFunctionIndex == E_TEST_FUNCTION_1 :
			print 'dhkim test function1'

		elif self.mFunctionIndex == E_TEST_FUNCTION_2 :
			print 'dhkim test function2'

		elif self.mFunctionIndex == E_TEST_FUNCTION_3 :
			print 'dhkim test function3'


class Progress :

	def __init__( self, aDescription = 'Wait...' ) :
		self.mDescription = aDescription
		self.progress = xbmcgui.DialogProgress( )
		self.progress.create('Wait', self.mDescription )


	def Close( self ) :
		time.sleep( 0.5 )
		self.progress.close( )


	def Update( self, aPercent , aLabel=None ) :
		if aLabel != None :
			self.progress.update( aPercent, aLabel ) 
		else :
			self.progress.update( aPercent )

	def IsCanceled( self ) :
		if self.progress.iscanceled() == True :
			return True
		else :
			return False