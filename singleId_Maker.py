#-*- coding: utf-8 -*-

#from sys import setdefaultencoding
#setdefaultencoding('utf-8')
import os, re, shutil, time, sys, glob
import sgmllib, string
from types import *

gNoParseList = {}
E_DIR_RESULT = os.getcwd() + '/changeTest'

E_ID_SINGLE_CONVERT = 50000
WIN_ID_ROOTWINDOW 					= 0
WIN_ID_NULLWINDOW 					= 1
WIN_ID_MAINMENU 					= 2
WIN_ID_CHANNEL_LIST_WINDOW			= 3
WIN_ID_LIVE_PLATE					= 4
WIN_ID_CONFIGURE					= 5
WIN_ID_ANTENNA_SETUP				= 6
WIN_ID_TUNER_CONFIGURATION			= 7
WIN_ID_CONFIG_SIMPLE				= 8
WIN_ID_CONFIG_MOTORIZED_12			= 9
WIN_ID_CONFIG_MOTORIZED_USALS		= 10
WIN_ID_CONFIG_ONECABLE				= 12
WIN_ID_CONFIG_ONECABLE_2			= 13
WIN_ID_CONFIG_DISEQC_10				= 14
WIN_ID_CONFIG_DISEQC_11				= 15
WIN_ID_CHANNEL_SEARCH				= 16
WIN_ID_AUTOMATIC_SCAN				= 17
WIN_ID_MANUAL_SCAN					= 18
WIN_ID_TIMESHIFT_PLATE				= 19
WIN_ID_CHANNEL_EDIT_WINDOW			= 20
WIN_ID_EDIT_SATELLITE				= 21
WIN_ID_EDIT_TRANSPONDER				= 22
WIN_ID_ARCHIVE_WINDOW				= 23
WIN_ID_SYSTEM_INFO					= 24
WIN_ID_INSTALLATION					= 25
WIN_ID_MEDIACENTER					= 26
WIN_ID_EPG_WINDOW					= 27
WIN_ID_CONDITIONAL_ACCESS			= 28
WIN_ID_FIRST_INSTALLATION			= 29
WIN_ID_TIMER_WINDOW					= 30
WIN_ID_INFO_PLATE					= 31
#WIN_ID_FAVORITE_ADDONS				= 32
WIN_ID_FAVORITES					= 32
WIN_ID_SYSTEM_UPDATE				= 33
WIN_ID_HELP							= 34
E_IDS_SINGLE_WINDOW = {
	'TunerConfiguration.xml' : 50000,
	'ManualScan.xml' : None,
	'EditSatellite.xml' : None,
	'DialogMoveAntenna.xml' : None,
	'SystemUpdate.xml' : None,
	'FirstInstallation.xml' : None,
	'ChannelSearch.xml' : None,
	'Installation.xml' : None,
	'TimeshiftPlate.xml' : None,
	'DialogMultiSelect.xml' : None,
	'DialogChannelSearch.xml' : None,
	'DialogLnbFrequency.xml' : None,
	'Help_String.xml' : None,
	'MediaCenter.xml' : None,
	'LivePlate.xml' : None,
	'SystemInfo.xml' : None,
	'AutomaticScan.xml' : None,
	'AntennaSetup.xml' : None,
	'DialogSetTransponder.xml' : None,
	'DialogChannelJump.xml' : None,
	'DialogAddNewSatellite.xml' : None,
	'ArchiveWindow.xml' : None,
	'DialogEditChannelList.xml' : None,
	'SatelliteConfigMotorized12.xml' : None,
	'DialogStartRecord.xml' : None,
	'ChannelListWindow.xml' : None,
	'EditTransponder.xml' : None,
	'DialogYesNoCancel.xml' : None,
	'DialogAddManualTimer.xml' : None,
	'MainMenu.xml' : None,
	'DialogStopRecord.xml' : None,
	'ConditionalAccess.xml' : None,
	'DialogNormalNumeric.xml' : None,
	'SatelliteConfigSimple.xml' : None,
	'DialogSatelliteNumeric.xml' : None,
	'DialogPopupOK.xml' : None,
	'DialogForceProgress.xml' : None,
	'Favorites.xml' : None,
	'DialogCasEvent.xml' : None,
	'DialogExtendEPG.xml' : None,
	'FavoriteAddons.xml' : None,
	'DialogBookmark.xml' : None,
	'Configure.xml' : None,
	'DialogAutoPowerDown.xml' : None,
	'DialogSetAudioVideo.xml' : None,
	'DialogContext.xml' : None,
	'SatelliteConfigDisEqC11.xml' : None,
	'Help.xml' : None,
	'EPGWindow.xml' : None,
	'TimerWindow.xml' : None,
	'SatelliteConfigOnecable.xml' : None,
	'DialogAddTimer.xml' : None,
	'NullWindow.xml' : None,
	'SatelliteConfigMotorizedUsals.xml' : None,
	'DialogInputPincode.xml' : None,
	'SatelliteConfigOnecable2.xml' : None,
	'SatelliteConfigDisEqC10.xml' : None
	}

E_ID_EXCEPTION = [
	8800,
	8899
	]

E_FILE_EXCEPTION = [
	'rootwindow.xml',
	'settings.xml',
	'addon.xml',
	'confluence_texture_cache.xml',
	'confluence_texture_cache.xml',
	'elmo_test.xml',
	'mbox_includes.xml',
	'hiddentest.xml',
	'help_string.xml',
	'loading.xml'
	]

E_PATTERN_STRINGS = [
	'id=\"\d+\"',
	'<defaultcontrol(.*)>\d+</defaultcontrol>',
	'<onleft>(.*)\d+(.*)</onleft>',
	'<onright>(.*)\d+(.*)</onright>',
	'<onup>(.*)\d+(.*)</onup>',
	'<ondown>(.*)\d+(.*)</ondown>',
	'<onclick>\d+</onclick>',

	#'<onleft>SetFocus\(\d+\)</onleft>',
	#'<onright>SetFocus\(\d+\)</onright>',
	#'<onup>SetFocus\(\d+\)</onup>',
	#'<ondown>SetFocus\(\d+\)</ondown>',
	'Control\.\D*\(\d+\)',
	'ControlGroup\(\d+\)\.',
	'Container\(\d+\)\.'
	]


def InitDir( ) :
	#init dir
	try:
		shutil.rmtree( E_DIR_RESULT )
		#os.remove(wFile1)
	except Exception, e :
		print e
		pass
	os.mkdir( E_DIR_RESULT, 0775 )


gCount = 0
gName = None
def FindallSource(aDir, patternStr, reqFile=None):
	retlist = glob.glob(os.path.join(aDir, patternStr))
	findlist = os.listdir(aDir)
	global gCount, gName
	searched = None

	for fname in findlist:
		next = os.path.join(aDir, fname)
		if os.path.isdir(next) : 
			retlist += FindallSource(next, patternStr, reqFile)
		else :
			if reqFile :
				if fname == reqFile :
					searched = '%s/%s'% ( aDir,fname )
					gName = searched
					break

			else :
				if gNoParseList.get( fname.lower() ) == fname.lower() :
					#print gNoParseList.get(fname)
					continue

				filename = os.path.splitext( fname )
				if filename[1] == '.xml' :
					gCount += 1

					global E_ID_SINGLE_CONVERT 
					E_ID_SINGLE_CONVERT = E_IDS_SINGLE_WINDOW.get( fname, None )
					if not E_ID_SINGLE_CONVERT :
						E_ID_SINGLE_CONVERT = 100000 * gCount 

					print '%s[%s]%s'% ( gCount, E_ID_SINGLE_CONVERT , fname )
					ParseSource( '%s/%s'% (aDir, fname) )
					#sys.exit( 11 )


	return retlist


gDebug = False
def ParseSource( aSourceFile ) :
	if not aSourceFile :
		return

	try:
		rf = open( aSourceFile, 'r' )
		sourceXml = rf.readlines( )
		rf.close( )

	except Exception, e:
		print 'except[%s] Cannot open file[%s]'% ( e, aSourceFile )
		return

	filename = os.path.basename( aSourceFile )
	changeFile = '%s/%s'% ( E_DIR_RESULT, filename )
	try :
		fp = open(changeFile, 'w')
	except Exception, e :
		print 'except[%s] Cannot open file[%s]'% ( e, changeFile )
		return

	count = 0
	countM= 0
	for line in sourceXml :
		line = line.rstrip( )
		isMatch = False
		for pattern in E_PATTERN_STRINGS :
			#print line
			ret = re.findall( pattern, line, re.I )
			if ret :
				p = re.compile( pattern )
				lineM = p.sub(ChangeIds, line )
				if line != lineM :
					isMatch = True
					countM += 1
				line = lineM

		if isMatch and gDebug :
			print count, line

		fp.writelines( '%s\n'% line )
		count += 1

	fp.close( )

	print '---->changed[%s]'% countM


def ChangeIds( aMatch ) :
	idnumber = re.findall( '\d+', aMatch.group() )[0]
	changeid = E_ID_SINGLE_CONVERT + int( idnumber )
	#print '----id[%s -> %s] match[%s]'% ( idnumber, changeid, aMatch.group() )

	value = re.sub( '\d+', '%s'% changeid, aMatch.group(), 1 )
	if int( idnumber ) in E_ID_EXCEPTION :
		value = aMatch.group()

	return value


def AutoMakeSingleIDs( ) :
	currDir = os.getcwd()
	mboxDir = os.path.abspath( currDir + '/../script.mbox' )
	elisDir = os.path.abspath( currDir + '/../script.module.elisinterface' )
	confluenceDir = os.path.join( mboxDir, 'resources/skins/Default/720p' )

	for iFile in E_FILE_EXCEPTION :
		gNoParseList[iFile] = iFile

	InitDir( )
	#openFile = confluenceDir + 'LivePlate.xml'
	#ParseSource( openFile )
	FindallSource( confluenceDir, '[a-zA-Z0-9]\w*.xml' )
	print '\nChangeAll *.xml files[%s]'% gCount
	print '\n\033[1;%sm%s\033[1;m'% (30, 'Completed..')



def test( ) :
	#strs = '<animation effect="slide" start="300r,0" end="0r,0" delay="0" time="300" condition="Control.IsVisible(10) | !Control.IsVisible(15)">conditional</animation>'
	#ret = re.findall( E_PATTERN_STRINGS[9], strs, re.I )
	#strs = '<animation effect="slide" start="-200,0" end="0,0" delay="0" time="300" condition="ControlGroup(3620).HasFocus) | Control.HasFocus(702) | Control.HasFocus(706)">conditional</animation>'
	#strs = '<defaultcontrol always="true">3621</defaultcontrol>'
	#strs = '<defaultcontrol>2222</defaultcontrol>'
	#strs = '<onup>Control.SetFocus(102,4)</onup>'
	strs = '<ondown condition="Control.IsVisible(9001)">9001</ondown>'

	for pattern in E_PATTERN_STRINGS :
		ret = re.findall( pattern, strs, re.I )
		if ret :
			p = re.compile( pattern )
			strs = p.sub(ChangeIds, strs )

	print strs


def test2( ) :
	InitDir( )
	global E_ID_SINGLE_CONVERT 

	mboxDir = os.path.abspath( currDir + '/../script.mbox' )

	testSource = [ 'RootWindow.xml', 'NullWindow.xml', 'MainMenu.xml', 'ChannelListWindow.xml', 'LivePlate.xml'  ]

	idDefault = 1000000
	count = 0
	global E_ID_SINGLE_CONVERT 
	for item in testSource :
		E_ID_SINGLE_CONVERT = idDefault + ( count * 100000 )
		iFile = os.path.join( mboxDir, item )
		ParseSource( iFile )
		count += 1


if __name__ == "__main__":

	nameSelf = os.path.basename(sys.argv[0])
	gNoParseList[nameSelf] = nameSelf
	param = sys.argv[1:]

	if len(param) > 0 :
		if param[0] == 'debug' :
			global gDebug
			gDebug = True

	#AutoMakeSingleIDs( )
	#test( )
	test2( )


