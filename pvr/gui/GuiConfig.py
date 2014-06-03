import xbmc, xbmcgui, time, sys, threading, os, re, shutil, string, thread, glob, copy
from copy import deepcopy
from elisinterface.util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
from pvr.GuiHelper import MR_LANG
import pvr.Platform
from pvr.Product import *

# XBMC INTERFACE
E_ADD_XBMC_HTTP_FUNCTION			= True
E_ADD_XBMC_JSONRPC_FUNCTION			= False
E_ADD_XBMC_ADDON_API				= False

# HBBTV SUPPOERT
E_SUPPROT_HBBTV				= True
E_SUPPROT_WEBINTERFACE		= True

FILE_NAME_HBB_TV			= '/config/hbbtv'

#E_SUPPROT_WEBINTERFACE		= False
RECORD_WIDTHOUT_ASKING		= True
RECORD_ENDTIME_TRICK_MARGIN = 1


# WINDOW SIZE
E_WINDOW_WIDTH		= 1280
E_WINDOW_HEIGHT		= 720

# SERVER ADDRESS
PRISMCUBE_SERVER_ADDON	= 'http://addon.prismcube.com'
PRISMCUBE_SERVER_FW_UPDATE = 'http://update.prismcube.com'
PRISMCUBE_REQUEST_FW_PATH = 'ruby_v1.xxx.xxx'

# custom logo
CUSTOM_LOGO_PATH					= xbmc.translatePath( "special://profile/channellogo" )

# SUPPORT : SKIN RELOAD 'Q' KEY
E_SUPPORT_USE_KEY_Q = False

# Frodo issue support, list empty
E_SUPPORT_FRODO_EMPTY_LISTITEM = False

# SHOWING MODE
E_MODE_SHOW				= 0
E_MODE_DOMODAL			= 1
E_WINDOW_ATIVATE_MODE	= E_MODE_DOMODAL

# SHOWING MODE on select dialog
E_MODE_DEFAULT_LIST    = 0
E_MODE_CHANNEL_LIST    = 1
E_MODE_FAVORITE_GROUP  = 2
E_MODE_ZAPPING_GROUP   = 3
E_SELECT_ONLY  = 0
E_SELECT_MULTI = 1


# SUPPORT SINGLE WINDOW
E_SUPPORT_SINGLE_WINDOW_MODE = True

# USE OLD NETWORK
E_USE_OLD_NETWORK			= True
E_USE_AUTO_CONNECT			= False

#use to usb
E_UPDATE_FIRMWARE_USE_USB   = False
E_UPDATE_FIRMWARE_USB_ONLY  = False
E_UPDATE_TEST_DEBUG         = False
E_UPDATE_TEST_TESTBED       = False

# USE CHANNEL_LOGO
E_USE_CHANNEL_LOGO			= True

# First Tune fast
E_FIRST_TUNE_FAST			= True


E_BASE_WINDOW_ID		= 0
E_BASE_WINDOW_UNIT		= 0
if E_SUPPORT_SINGLE_WINDOW_MODE :
	E_BASE_WINDOW_ID	= 1000000
	E_BASE_WINDOW_UNIT	= 100000


E_SETTING_CONTROL_GROUPID = 0

if E_SUPPORT_SINGLE_WINDOW_MODE :
	E_SETTING_CONTROL_GROUPID	= 11000001
else :
	E_SETTING_CONTROL_GROUPID	= 9010


############################ Windows ############################
# Setting Window Control Ids
E_SpinEx01			= E_BASE_WINDOW_ID + 1100
E_SpinEx02			= E_BASE_WINDOW_ID + 1200
E_SpinEx03			= E_BASE_WINDOW_ID + 1300
E_SpinEx04			= E_BASE_WINDOW_ID + 1400
E_SpinEx05			= E_BASE_WINDOW_ID + 1500
E_SpinEx06			= E_BASE_WINDOW_ID + 1600
E_SpinEx07			= E_BASE_WINDOW_ID + 1700
E_SpinEx08			= E_BASE_WINDOW_ID + 1800
E_SpinEx09			= E_BASE_WINDOW_ID + 1900

E_Input01			= E_BASE_WINDOW_ID + 2100
E_Input02			= E_BASE_WINDOW_ID + 2200
E_Input03			= E_BASE_WINDOW_ID + 2300
E_Input04			= E_BASE_WINDOW_ID + 2400
E_Input05			= E_BASE_WINDOW_ID + 2500
E_Input06			= E_BASE_WINDOW_ID + 2600
E_Input07			= E_BASE_WINDOW_ID + 2700
E_Input08			= E_BASE_WINDOW_ID + 2800


# Info Plate Buttons
E_CTRL_BTN_INFO_MAX						= 8
E_CTRL_GROUP_INFO						= E_BASE_WINDOW_ID + 3620
E_CONTROL_ID_BUTTON_DESCRIPTION_INFO 	= E_BASE_WINDOW_ID + 3621
E_CONTROL_ID_BUTTON_TELETEXT 			= E_BASE_WINDOW_ID + 3622
E_CONTROL_ID_BUTTON_SUBTITLE 			= E_BASE_WINDOW_ID + 3623
E_CONTROL_ID_BUTTON_BOOKMARK 			= E_BASE_WINDOW_ID + 3628
E_CONTROL_ID_BUTTON_START_RECORDING 	= E_BASE_WINDOW_ID + 3624
E_CONTROL_ID_BUTTON_STOP_RECORDING 		= E_BASE_WINDOW_ID + 3625
E_CONTROL_ID_BUTTON_MUTE 				= E_BASE_WINDOW_ID + 3626
E_CONTROL_ID_BUTTON_SETTING_FORMAT 		= E_BASE_WINDOW_ID + 3627
E_CONTROL_ID_BUTTON_PIP					= E_BASE_WINDOW_ID + 3629
E_CONTROL_ID_BUTTON_CHANNEL_LIST		= E_BASE_WINDOW_ID + 3630
E_CONTROL_ID_BUTTON_SERVICE_INFO		= E_BASE_WINDOW_ID + 3631

E_CONTROL_ID_GROUP_PVR_BUTTONS 			= E_BASE_WINDOW_ID + 3750


# Setting Menu Group Ids
E_SUBMENU_LIST_ID						= E_BASE_WINDOW_ID + 9000
E_SETUPMENU_GROUP_ID					= E_BASE_WINDOW_ID + 9010

E_SETTING_HEADER_TITLE					=	E_BASE_WINDOW_ID + 1002
E_SETTING_DESCRIPTION					=	E_BASE_WINDOW_ID + 1003
E_SETTING_PIP_SCREEN_IMAGE				=	8899
E_SETTING_PIP_RADIO_IMAGE				=	E_BASE_WINDOW_ID + 8800

E_FAKE_BUTTON							=	E_BASE_WINDOW_ID + 999


# Setting Header Title
E_DEFAULT_HEADER_TITLE					= E_BASE_WINDOW_ID + 9550
E_ARCHIVE_HEADER_TITLE					= E_BASE_WINDOW_ID + 9551


# First Time Installation Button Ids
E_STEP_SELECT_LANGUAGE					=	0
E_STEP_VIDEO_AUDIO						=	1
E_STEP_ANTENNA							=	2
E_STEP_CHANNEL_SEARCH_CONFIG			=	3
E_STEP_CHANNEL_SEARCH_CONFIG_FAST		=	4
E_STEP_DATE_TIME						=	5
E_STEP_RESULT							=	6

FIRST_TIME_INSTALLATION_STEP			= 6

E_FIRST_TIME_INSTALLATION_PREV				= E_BASE_WINDOW_ID + 7001
E_FIRST_TIME_INSTALLATION_NEXT				= E_BASE_WINDOW_ID + 7003
E_FIRST_TIME_INSTALLATION_PREV_LABEL		= E_BASE_WINDOW_ID + 7005
E_FIRST_TIME_INSTALLATION_NEXT_LABEL		= E_BASE_WINDOW_ID + 7008

E_FIRST_TIME_INSTALLATION_STEP_IMAGE		= E_BASE_WINDOW_ID + 8100
E_FIRST_TIME_INSTALLATION_STEP_IMAGE_BACK	= E_BASE_WINDOW_ID + 8110

# Scan Heler Status
E_SCAN_HELPER_GROUP				= E_BASE_WINDOW_ID + 1007
E_SCAN_LABEL_STRENGTH			= E_BASE_WINDOW_ID + 1008
E_SCAN_HELPER_LABEL_STRENGTH	= E_BASE_WINDOW_ID + 1005
E_SCAN_HELPER_PROGRESS_STRENGTH	= E_BASE_WINDOW_ID + 1010
E_SCAN_LABEL_QUALITY			= E_BASE_WINDOW_ID + 1009
E_SCAN_HELPER_LABEL_QUALITY		= E_BASE_WINDOW_ID + 1006
E_SCAN_HELPER_PROGRESS_QUALITY	= E_BASE_WINDOW_ID + 1011

# Setting Window No Signal
E_SETTING_LABEL_PIP_NO_SIGNAL	= E_BASE_WINDOW_ID + 1020
E_SETTING_LABEL_PIP_SCRAMBLED	= E_BASE_WINDOW_ID + 1021
E_SETTING_LABEL_NO_SERVICE		= E_BASE_WINDOW_ID + 1022

# MR_LANG
NEW_LINE						= '\n'
ING								= '...'

# TUNER TYPE
E_SIMPLE_LNB					= 0
E_DISEQC_1_0					= 1
E_DISEQC_1_1					= 2
E_MOTORIZE_1_2					= 3
E_MOTORIZE_USALS				= 4
E_ONE_CABLE						= 5

# MAX DISEQC_1_0_COUNT
E_MAX_SATELLITE_COUNT			= 16

# TUNER CONNECTION TYPE
E_TUNER_SEPARATED				= 0
E_TUNER_LOOPTHROUGH				= 1
E_TUNER_ONECABLE				= 2

# TUNER CONFIG TYPE
E_SAMEWITH_TUNER				= 0
E_DIFFERENT_TUNER				= 1

# TUNER
E_TUNER_1						= 0
E_TUNER_2						= 1
E_TUNER_MAX						= 2

E_CONFIGURED_TUNER_1			= 1
E_CONFIGURED_TUNER_2			= 2
E_CONFIGURED_TUNER_1_2			= 3

# ONECABLECOUNT
MAX_SATELLITE_CNT_ONECABLE		= 2

# LOGITUDE DIRECTION
E_WEST							= 0
E_EAST							= 1

# RECORD
if pvr.Platform.GetPlatform( ).GetProduct( ) == PRODUCT_RUBY :
	E_MAX_RECORD_COUNT				= 2
elif pvr.Platform.GetPlatform( ).GetProduct( ) == PRODUCT_OSCAR :
	E_MAX_RECORD_COUNT				= 1

# Volume
VOLUME_STEP						= 4
DEFAULT_VOLUME					= 75
MAX_VOLUME						= 100

# Time Mode
TIME_AUTOMATIC					= 0
TIME_MANUAL						= 1

# Summer Time
SUMMER_TIME_AUTOMATIC			= 0
SUMMER_TIME_OFF					= 1

# Network Mode
NET_DHCP						= 0
NET_STATIC						= 1

# Wifi Encription Type
ENCRYPT_OPEN					= 0
ENCRYPT_TYPE_WEP				= 1
ENCRYPT_TYPE_WPA				= 2

# Wifi Use Hidden Ssid
NOT_USE_HIDDEN_SSID				= 0
USE_HIDDEN_SSID					= 1

# Network Type
NETWORK_ETHERNET				= 0
NETWORK_WIRELESS				= 1

# DB table
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

E_MAX_EPG_DAYS 			= 24 * 3600 * 28

# Video Type
E_VIDEO_HDMI			= 0
E_VIDEO_ANALOG			= 1

# Analog Type
E_16_9					= 0
E_4_3					= 1

# SETTING WINDOW INPUT TYPE
TYPE_NUMBER_NORMAL				= 0

# CAM SLOT NUM ( now only accept 1 slot )
CAS_SLOT_NUM_1					= 0
CAS_SLOT_NUM_2					= 1

# Tuner Config String Define
USER_ENUM_LIST_ON_OFF				= [ MR_LANG( 'Off' ), MR_LANG( 'On' ) ]
USER_ENUM_LIST_YES_NO				= [ MR_LANG( 'No' ), MR_LANG( 'Yes' ) ]
USER_ENUM_LIST_DHCP_STATIC			= [ MR_LANG( 'DHCP' ), MR_LANG( 'Static' ) ]
USER_ENUM_LIST_NETWORK_TYPE			= [ MR_LANG( 'Ethernet' ), MR_LANG( 'Wireless' ) ]
USER_ENUM_LIST_VIDEO_OUTPUT			= [ MR_LANG( 'HDMI' ), MR_LANG( 'Analog' ) ]
USER_ENUM_LIST_SEARCH_RANGE			= [ MR_LANG( 'Single Transponder' ), MR_LANG( 'All Transponders' ) ]
USER_ENUM_LIST_ENCRYPT_TYPE			= [ MR_LANG( 'None' ), MR_LANG( 'WEP' ), MR_LANG( 'WPA' ) ]
USER_ENUM_LIST_UPDATE_NOTIFY		= [ MR_LANG( 'None' ), MR_LANG( '5 times' ), MR_LANG( 'Always' ) ]

E_LIST_LNB_TYPE						= [ MR_LANG( 'Universal' ), MR_LANG( 'Single' ), MR_LANG( 'Userdefined' ) ]
E_LIST_SINGLE_FREQUENCY 			= [ '5150', '9750', '10600', '10750', '11300' ]
E_LIST_DISEQC_MODE					= [ MR_LANG( 'Disable' ), '1 of 4', '2 of 4', '3 of 4', '4 of 4', 'Mini A', 'Mini B' ]
E_LIST_COMMITTED_SWITCH				= [ MR_LANG( 'Disable' ), '1', '2', '3', '4' ]
E_LIST_UNCOMMITTED_SWITCH			= [ MR_LANG( 'Disable' ), '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16' ]
E_LIST_MOTORIZE_ACTION				= [ MR_LANG( 'Reset Limits' ), MR_LANG( 'Set East Limit' ), MR_LANG( 'Set West Limit' ) ]
E_LIST_ONE_CABLE_TUNER_FREQUENCY	= [ '1284', '1400', '1516', '1632', '1748', '1864', '1980', '2096' ]
E_LIST_ONE_CABLE_SCR				= [ 'SCR(0)', 'SCR(1)', 'SCR(2)', 'SCR(3)', 'SCR(4)', 'SCR(5)', 'SCR(6)', 'SCR(7)' ]
E_LIST_SKIN_ZOOM_RATE				= [ '-20', '-18', '-16', '-14', '-12', '-10', '-8', '-6', '-4', '-2', '0', '2', '4', '6', '8', '10', '12', '14', '16', '18', '20' ] 

E_LIST_TUNER_CONNECTION				= [ MR_LANG( 'Separated' ), MR_LANG( 'Loopthrough' ), MR_LANG( 'UniCable' ) ]
E_LIST_TUNER2_SIGNAL				= [ MR_LANG( 'Same with Tuner 1' ), MR_LANG( 'Different from Tuner 1' ) ]
if pvr.Platform.GetPlatform( ).GetProduct( ) == PRODUCT_RUBY :
	E_LIST_TUNER_CONTROL				= [	MR_LANG( 'Simple LNB' ), MR_LANG( 'DiSEqC 1.0' ), MR_LANG( 'DiSEqC 1.1' ), MR_LANG( 'Motorized, DiSEqC 1.2' ), MR_LANG( 'Motorized, USALS' ) ]
elif pvr.Platform.GetPlatform( ).GetProduct( ) == PRODUCT_OSCAR :
	E_LIST_TUNER_CONTROL				= [	MR_LANG( 'Simple LNB' ), MR_LANG( 'DiSEqC 1.0' ), MR_LANG( 'DiSEqC 1.1' ), MR_LANG( 'Motorized, DiSEqC 1.2' ), MR_LANG( 'Motorized, USALS' ), MR_LANG( 'UniCable' ) ]

E_LIST_MY_LONGITUDE = [ MR_LANG( 'East' ), MR_LANG( 'West' ) ]
E_LIST_MY_LATITUDE  = [ MR_LANG( 'North' ), MR_LANG( 'South' ) ]


def InitTranslateByEnumList( ) :
	global USER_ENUM_LIST_ON_OFF, USER_ENUM_LIST_YES_NO, USER_ENUM_LIST_DHCP_STATIC, USER_ENUM_LIST_NETWORK_TYPE, USER_ENUM_LIST_VIDEO_OUTPUT
	global USER_ENUM_LIST_SEARCH_RANGE, E_LIST_LNB_TYPE, E_LIST_MOTORIZE_ACTION, E_LIST_MY_LONGITUDE, E_LIST_MY_LATITUDE, USER_ENUM_LIST_UPDATE_NOTIFY
	global E_LIST_TUNER_CONNECTION, E_LIST_TUNER2_SIGNAL, E_LIST_TUNER_CONTROL

	InitializedByVariableList( USER_ENUM_LIST_ON_OFF, MR_LANG( 'Off' ), MR_LANG( 'On' ) )
	InitializedByVariableList( USER_ENUM_LIST_YES_NO, MR_LANG( 'No' ), MR_LANG( 'Yes' ) )
	InitializedByVariableList( USER_ENUM_LIST_DHCP_STATIC, MR_LANG( 'DHCP' ), MR_LANG( 'Static' ) )
	InitializedByVariableList( USER_ENUM_LIST_NETWORK_TYPE, MR_LANG( 'Ethernet' ), MR_LANG( 'Wireless' ) )
	InitializedByVariableList( USER_ENUM_LIST_VIDEO_OUTPUT, MR_LANG( 'HDMI' ), MR_LANG( 'Analog' ) )
	InitializedByVariableList( USER_ENUM_LIST_SEARCH_RANGE, MR_LANG( 'Single Transponder' ), MR_LANG( 'All Transponders' ) )
	InitializedByVariableList( E_LIST_LNB_TYPE, MR_LANG( 'Universal' ), MR_LANG( 'Single' ), MR_LANG( 'Userdefined' ) )
	InitializedByVariableList( E_LIST_DISEQC_MODE, MR_LANG( 'Disable' ), '1 of 4', '2 of 4', '3 of 4', '4 of 4', MR_LANG( 'Mini A' ), MR_LANG( 'Mini B' ) )
	InitializedByVariableList( E_LIST_COMMITTED_SWITCH, MR_LANG( 'Disable' ), '1', '2', '3', '4' )
	InitializedByVariableList( E_LIST_UNCOMMITTED_SWITCH, MR_LANG( 'Disable' ), '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16' )
	InitializedByVariableList( E_LIST_MOTORIZE_ACTION, MR_LANG( 'Reset Limits' ), MR_LANG( 'Set East Limit' ), MR_LANG( 'Set West Limit' ) )
	InitializedByVariableList( E_LIST_MY_LONGITUDE, MR_LANG( 'East' ), MR_LANG( 'West' ) )
	InitializedByVariableList( E_LIST_MY_LATITUDE, MR_LANG( 'North' ), MR_LANG( 'South' ) )
	InitializedByVariableList( USER_ENUM_LIST_UPDATE_NOTIFY, MR_LANG( 'None' ), MR_LANG( '5 times' ), MR_LANG( 'Always' ) )
	InitializedByVariableList( E_LIST_TUNER_CONNECTION, MR_LANG( 'Separated' ), MR_LANG( 'Loopthrough' ), MR_LANG( 'UniCable' ) )
	InitializedByVariableList( E_LIST_TUNER2_SIGNAL, MR_LANG( 'Same with Tuner 1' ), MR_LANG( 'Different from Tuner 1' ) )
	InitializedByVariableList( E_LIST_TUNER_CONTROL, MR_LANG( 'Simple LNB' ), MR_LANG( 'DiSEqC 1.0' ), MR_LANG( 'DiSEqC 1.1' ), MR_LANG( 'Motorized, DiSEqC 1.2' ), MR_LANG( 'Motorized, USALS' ) )
	LOG_TRACE('----------------------InitTranslateByEnumList [%s][%s]'% ( xbmc.getLanguage(), USER_ENUM_LIST_ON_OFF ) )


def InitializedByVariableList( aList, *Value ) :
	if not Value or len( Value ) < 1 :
		return

	for idx in range( len( Value ) ) :
		aList[idx] = Value[idx]


############################ Dialog ############################

G_DIALOG_HEADER_LABEL_ID			= E_BASE_WINDOW_ID + 3005

# Setting Dialog Control Ids
E_DialogSpinEx01	= E_BASE_WINDOW_ID + 6110
E_DialogSpinEx02	= E_BASE_WINDOW_ID + 6120
E_DialogSpinEx03	= E_BASE_WINDOW_ID + 6130
E_DialogSpinEx04	= E_BASE_WINDOW_ID + 6140

E_DialogInput01		= E_BASE_WINDOW_ID + 6210
E_DialogInput02		= E_BASE_WINDOW_ID + 6220
E_DialogInput03		= E_BASE_WINDOW_ID + 6230
E_DialogInput04		= E_BASE_WINDOW_ID + 6240
E_DialogInput05		= E_BASE_WINDOW_ID + 6250
E_DialogInput06		= E_BASE_WINDOW_ID + 6260
E_DialogInput07		= E_BASE_WINDOW_ID + 6270
E_DialogInput08		= E_BASE_WINDOW_ID + 6280
E_DialogInput09		= E_BASE_WINDOW_ID + 6290

E_DialogSpinDay		= E_BASE_WINDOW_ID + 6300


E_SETTING_DIALOG_BUTTON_CLOSE			= E_BASE_WINDOW_ID + 6995
E_SETTING_DIALOG_BUTTON_OK_ID			= E_BASE_WINDOW_ID + 6997
E_SETTING_DIALOG_BUTTON_CANCEL_ID		= E_BASE_WINDOW_ID + 6999
E_SETTING_DIALOG_BACKGROUND_IMAGE_ID 	= 9001
E_SETTING_DIALOG_DEFAULT_GOURP_ID		= 9000
E_SETTING_DIALOG_MAIN_GOURP_ID			= 8000

# For Event
XBMC_WINDOW_DIALOG_INVALID			= 9999

# Transponder dialog Type
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
E_INDEX_JUMP_MAX				= 100

# Search Type
MININUM_KEYWORD_SIZE = 3

# Dialog Status
E_DIALOG_STATE_YES		= 1
E_DIALOG_STATE_NO		= 2
E_DIALOG_STATE_CANCEL	= 3
E_DIALOG_STATE_ERROR	= 4

E_PARENTLOCK_INIT       = 0
E_PARENTLOCK_EIT        = 1
E_CHECK_PARENTLOCK		= 1

E_PIP_STOP				= 1
E_PIP_CHECK_FORCE		= 2

# Channel List Enum
E_TAG_ENABLE  				= 'enable'
E_TAG_VISIBLE 				= 'visible'
E_TAG_SELECT  				= 'select'
E_TAG_LABEL   				= 'label'
E_TAG_POSY   				= 'posy'
E_TAG_TRUE    				= 'True'
E_TAG_FALSE   				= 'False'
E_TAG_ADD_ITEM 				= 'addItem'
E_TAG_COLOR_RED   			= '[COLOR red]'
E_TAG_COLOR_GREEN 			= '[COLOR green]'
E_TAG_COLOR_BLUE 			= '[COLOR blue]'
E_TAG_COLOR_GREY 			= '[COLOR grey]'
E_TAG_COLOR_END   			= '[/COLOR]'
E_TAG_COLOR_HD_LABEL        = '[COLOR orange]%s[/COLOR]'% ( '<HD>' )
E_TAG_SET_SELECT_POSITION 	= 'selectItem'
E_TAG_GET_SELECT_POSITION 	= 'getItem'

# XML Property Name
E_XML_PROPERTY_TELETEXT   = 'HasTeletext'	 
E_XML_PROPERTY_SUBTITLE   = 'HasSubtitle'
E_XML_PROPERTY_DOLBY      = 'HasDolby'
E_XML_PROPERTY_DOLBYPLUS  = 'HasDolbyPlus'
E_XML_PROPERTY_HD         = 'HasHD'
E_XML_PROPERTY_MARK       = 'iMark'
E_XML_PROPERTY_IMOVE      = 'iMove'
E_XML_PROPERTY_SKIP       = 'iSkip'
E_XML_PROPERTY_LOCK       = 'iLock'
E_XML_PROPERTY_CAS        = 'iCas'
E_XML_PROPERTY_IHD        = 'iHD'
E_XML_PROPERTY_FAV        = 'iFav'
E_XML_PROPERTY_RECORDING  = 'iRec'
E_XML_PROPERTY_TUNER1     = 'iTuner1'
E_XML_PROPERTY_TUNER2     = 'iTuner2'
E_XML_PROPERTY_TUNER1_2   = 'iTuner1_2'
E_XML_PROPERTY_FASTSCAN   = 'iFastScan'
E_XML_PROPERTY_EDITINFO   = 'isEdit'
E_XML_PROPERTY_MOVE       = 'isMove'
E_XML_PROPERTY_TV         = 'ServiceTypeTV'
E_XML_PROPERTY_RADIO      = 'ServiceTypeRadio'
E_XML_PROPERTY_RECORDING1 = 'ViewRecord1'
E_XML_PROPERTY_RECORDING2 = 'ViewRecord2'
E_XML_PROPERTY_HOTKEY_RED    = 'iHotkeyRed'
E_XML_PROPERTY_HOTKEY_GREEN  = 'iHotkeyGreen'
E_XML_PROPERTY_HOTKEY_YELLOW = 'iHotkeyYellow'
E_XML_PROPERTY_HOTKEY_BLUE   = 'iHotkeyBlue'
E_XML_PROPERTY_CHANNEL_LOG   = 'ChannelLogo'
E_XML_PROPERTY_CHANNEL_ALIGN   = 'iAlign'
E_XML_PROPERTY_HAS_EVENT   = 'iHasEvent'
E_XML_PROPERTY_PERCENT   = 'percent'

# Context Action
CONTEXT_ACTION_LOCK				= 1 
CONTEXT_ACTION_UNLOCK			= 2
CONTEXT_ACTION_SKIP				= 3
CONTEXT_ACTION_UNSKIP			= 4
CONTEXT_ACTION_DELETE			= 5
CONTEXT_ACTION_DELETE_ALL		= 6
CONTEXT_ACTION_MOVE				= 7
CONTEXT_ACTION_ADD_TO_FAV		= 8
CONTEXT_ACTION_CREATE_GROUP_FAV	= 10
CONTEXT_ACTION_RENAME_FAV		= 11
CONTEXT_ACTION_DELETE_FAV		= 12
CONTEXT_ACTION_ADD_TO_CHANNEL	= 13
CONTEXT_ACTION_SAVE_EXIT		= 14
CONTEXT_ACTION_DELETE_FAV_CURRENT = 15
CONTEXT_ACTION_CHANGE_NAME		= 16
CONTEXT_ACTION_MENU_EDIT_MODE	= 20
CONTEXT_ACTION_MENU_DELETEALL	= 22
CONTEXT_ACTION_ADD_AUTO_CHAPTER = 30
CONTEXT_ACTION_ADD_TO_BOOKMARK 	= 31
CONTEXT_ACTION_SHOW_LIST	 	= 32
CONTEXT_ACTION_RESUME_FROM		= 33
CONTEXT_ACTION_START_MARK		= 34
CONTEXT_ACTION_CLEAR_MARK		= 35
CONTEXT_ACTION_SHOW_BOOKMARK	= 36
CONTEXT_ACTION_VIDEO_SETTING 	= 41 
CONTEXT_ACTION_AUDIO_SETTING 	= 42
CONTEXT_ACTION_HOTKEYS	 		= 43
CONTEXT_ACTION_INSERT_NUMBER	= 45
CONTEXT_ACTION_CHANNEL_SEARCH   = 46

E_DEFAULT_ACTION_CLICK_EVENT	= 1000
E_DEFAULT_BACKUP_PATH = '/config/backupSettings'
E_DEFAULT_NETWORK_VOLUME_SHELL  = '/config/smbReserved.info'
E_DEFAULT_BOOKMARK_LIMIT = 100
E_DEFAULT_THUMBNAIL_ICON = 'RecIconSample.png'
E_VOLITILE_PIP_STATUS_PATH = '/mtmp/PIPStatus'
E_DEFAULT_PATH_SMB_POSITION = '/media/smb'
E_DEFAULT_PATH_NFS_POSITION = '/media/nfs'
E_DEFAULT_PATH_FTP_POSITION = '/media/ftp'
E_DEFAULT_PATH_USB_POSITION = '/media/sd'
E_DEFAULT_RECORD_PATH_NOT_AVAILABLE = -1 #do not recording
E_DEFAULT_RECORD_PATH_NOT_SELECT    = -2 #avail recording : do not selected
E_DEFAULT_RECORD_PATH_RESERVED      = 1  #avail recording


#patch v1.1
E_V1_1_UPDATE_NOTIFY        = False
E_V1_1_HD_ICON_USE          = True
if E_V1_1_HD_ICON_USE :
	E_TAG_COLOR_HD_LABEL = ''

#patch v1.2
# v1.0.2 higher, apply to 2013.07.13
E_V1_2_UPDATE_FIRMWARE_SCENARIO_3RD = True
E_V1_2_APPLY_PRESENTATION_NUMBER = True
E_V1_2_APPLY_VIEW_TIMER = True
E_V1_2_APPLY_TEXTWIDTH_LABEL = True

E_V1_2_APPLY_PIP = True
if pvr.Platform.GetPlatform( ).GetProduct( ) == PRODUCT_OSCAR :
	E_V1_2_APPLY_PIP = False

E_SUPPORT_XBMC_PIP_FULLSCREEN_ONLY = True
E_SUPPORT_MEDIA_PLAY_AV_SWITCH = True
E_SUPPORT_EXTEND_RECORD_PATH = True

E_V1_6_PIP_SINGLE_TONE = True

############################ Global Function For GUI ############################


def getSingleFrequenceIndex( aSelectedItem ) :
	for i in range( len ( E_LIST_SINGLE_FREQUENCY )	) :
		if( aSelectedItem == int( E_LIST_SINGLE_FREQUENCY[ i ] ) ) :
			return i
			
	return -1


def getCommittedSwitchindex( aSelectedItem ) :
	if aSelectedItem == 5 or aSelectedItem == 6 :
		return 0
	return aSelectedItem


def getOneCableTunerFrequencyIndex( aSelectedItem ) :
	for i in range( len ( E_LIST_ONE_CABLE_TUNER_FREQUENCY ) ) :
		if( aSelectedItem == E_LIST_ONE_CABLE_TUNER_FREQUENCY[ i ] ) :
			return i
			
	return -1


def getZoomRateIndex( aValue ) :
	for i in range( len ( E_LIST_SKIN_ZOOM_RATE )	) :
		if( aValue == int( E_LIST_SKIN_ZOOM_RATE[ i ] ) ) :
			return i
			
	return 0


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


def IsNumber( aString ) :
	try :
		float( aString )
		return True
	except ValueError :
		return False



############################ Global Class ############################


class ContextItem :
	def __init__( self, aDescription = 'None', aContextAction = -1 ) :
		self.mDescription = aDescription
		self.mContextAction = aContextAction

