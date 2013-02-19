#-*- coding: utf-8 -*-

#from sys import setdefaultencoding
#setdefaultencoding('utf-8')
import os, re, shutil, time, sys, glob
import sgmllib, string
from types import *

gDebug = False
gParseList   = {}
gNoParseList = {}
gIDsMboxInclude = {}
E_DIR_RESULT = os.getcwd() + '/changeTest'

E_ID_BASE = 1000000
E_ID_SINGLE_CONVERT = 1000000

E_IDS_SINGLE_WINDOW = [
	['mbox_includes.xml', 0],
	['NullWindow.xml', 1],
	['MainMenu.xml', 2],
	['ChannelListWindow.xml', 3],
	['LivePlate.xml', 4],
	['Configure.xml', 5],
	['AntennaSetup.xml', 6],
	['TunerConfiguration.xml', 7],
	['SatelliteConfigSimple.xml', 8],
	['SatelliteConfigMotorized12.xml', 9],
	['SatelliteConfigMotorizedUsals.xml', 10],
	['SatelliteConfigOnecable.xml', 12],
	['SatelliteConfigOnecable2.xml', 13],
	['SatelliteConfigDisEqC10.xml', 14],
	['SatelliteConfigDisEqC11.xml', 15],
	['ChannelSearch.xml', 16],
	['AutomaticScan.xml', 17],
	['ManualScan.xml', 18],
	['TimeshiftPlate.xml', 19],
	#['ChannelEditWindow.xml', 20],
	['EditSatellite.xml', 21],
	['EditTransponder.xml', 22],
	['ArchiveWindow.xml', 23],
	['SystemInfo.xml', 24],
	['Installation.xml', 25],
	['MediaCenter.xml', 26],
	['EPGWindow.xml', 27],
	['ConditionalAccess.xml', 28],
	['FirstInstallation.xml', 29],
	['TimerWindow.xml', 30],
	#['InfoPlate.xml', 31],
	['Favorites.xml', 32],
	['SystemUpdate.xml', 33],
	['Help.xml', 34],
	['HiddenTest.xml', 99]
	]

E_PATTERN_STRINGS = [
	'(.*)id=\"\d+\"',
	'<defaultcontrol(.*)>\d+</defaultcontrol>',
	'<onleft>(.*)\d+(.*)</onleft>',
	'<onright>(.*)\d+(.*)</onright>',
	'<onup>(.*)\d+(.*)</onup>',
	'<ondown>(.*)\d+(.*)</ondown>',
	'<onclick>(.*)\d+(.*)</onclick>',
	'<pagecontrol>(.*)\d+(.*)</pagecontrol>',

	#'<onleft>SetFocus\(\d+\)</onleft>',
	#'<onright>SetFocus\(\d+\)</onright>',
	#'<onup>SetFocus\(\d+\)</onup>',
	#'<ondown>SetFocus\(\d+\)</ondown>',
	#'Control\.Move\(\d+(.*)\)',
	'\)\">\d+<\/(.*)',
	'Control\.\D*\(\d+\)',
	'ControlGroup\(\d+\)\.',
	'Container\(\d+\)\.'
	]

E_ID_EXCEPTION = [
#	8800,
	8899
	]

E_PATTERN_EXCEPTION = [
	'\s*<item id=\"\d+\"'
	]

E_FILE_EXCEPTION = [
	'rootwindow.xml',
	'settings.xml',
	'addon.xml',
	'confluence_texture_cache.xml',
	'confluence_texture_cache.xml',
	'elmo_test.xml',
	#'mbox_includes.xml',
	#'hiddentest.xml',
	'help_string.xml',
	'loading.xml'
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
					#print 'noParse[%s]'% gNoParseList.get(fname)
					continue

				if gParseList.get( fname, -1 ) == -1 :
					#print 'noParse[%s]'% fname
					continue

				filename = os.path.splitext( fname )
				if filename[1] == '.xml' :

					global E_ID_SINGLE_CONVERT 
					E_ID_SINGLE_CONVERT = E_ID_BASE + ( 100000 * gParseList.get( fname ) )

					gCount += 1
					print '%s[%s]%s'% ( gCount, E_ID_SINGLE_CONVERT , fname ),
					ParseSource( '%s/%s'% (aDir, fname) )
					#sys.exit( 11 )


	return retlist


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
			print '\033[1;%sm%s\t%s\033[1;m'% ( 30, count, line )

		fp.writelines( '%s\n'% line )
		count += 1

	fp.close( )

	print '\033[1;%sm---->changed[%s]\033[1;m'% ( 32, countM )


def ChangeIds( aMatch ) :
	idnumber = re.findall( '\d+', aMatch.group() )[0]
	changeid = E_ID_SINGLE_CONVERT + int( idnumber )
	#print '----id[%s -> %s] match[%s]'% ( idnumber, changeid, aMatch.group() )

	if E_ID_SINGLE_CONVERT == E_ID_BASE and int( idnumber ) >= 999 :
		if gIDsMboxInclude.get( idnumber, -1 ) == -1 :
			gIDsMboxInclude[idnumber] = idnumber
			#print 'base[%s]'% idnumber
	else :
		if gIDsMboxInclude.get( idnumber, -1 ) == idnumber :
			print '--------get[%s]'% gIDsMboxInclude.get( idnumber, -1 )
			changeid = E_ID_BASE + int( idnumber )


	for pattern in E_PATTERN_EXCEPTION :
		value = re.findall( pattern, aMatch.group() )
		if value and value[0] == aMatch.group() :
			#print '----pattern[%s] match[%s] except[%s]'% ( pattern, aMatch.group(), value[0] )
			changeid = idnumber
			return aMatch.group()


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

	for iFile in E_IDS_SINGLE_WINDOW :
		gParseList[iFile[0]] = iFile[1]

	InitDir( )
	ParseSource( '%s/mbox_includes.xml'% confluenceDir  )
	FindallSource( confluenceDir, '[a-zA-Z0-9]\w*.xml' )
	print '\nChangeAll *.xml files[%s]'% gCount
	print '\n\033[1;%sm%s\033[1;m'% (30, 'Completed..')



def test( ) :
	testWord = []
	testWord.append( '<animation effect="slide" start="300r,0" end="0r,0" delay="0" time="300" condition="Control.IsVisible(10) | !Control.IsVisible(15)">conditional</animation>' )
	testWord.append( '<animation effect="slide" start="-200,0" end="0,0" delay="0" time="300" condition="ControlGroup(3620).HasFocus(1)) | Control.HasFocus(702) | Control.HasFocus(706)">conditional</animation>' )
	testWord.append( '<defaultcontrol always="true">3621</defaultcontrol>' )
	testWord.append( '<defaultcontrol>2222</defaultcontrol>' )
	testWord.append( '<onup>Control.SetFocus(102,4)</onup>' )
	testWord.append( '<ondown condition="Control.IsVisible(9001)">9001</ondown>' )
	testWord.append( '<onclick>Control.Move(1903,-1)</onclick>' )
	testWord.append( '<pagecontrol>203</pagecontrol>' )
	testWord.append( '<visible>![Container(102).HasFocus(1) | Container(102).HasFocus(5)]</visible>' )
	testWord.append( '<onclick>SendClick(100)</onclick>' )
	testWord.append( '<item id="6">' )  #<-- must be no changed
	for strs in testWord :
		for pattern in E_PATTERN_STRINGS :
			ret = re.findall( pattern, strs, re.I )
			if ret :
				p = re.compile( pattern )
				strs = p.sub(ChangeIds, strs )

		print strs


def test2( ) :
	InitDir( )
	global E_ID_SINGLE_CONVERT 

	mboxDir = os.path.abspath( os.getcwd() + '/../script.mbox' )
	confluenceDir = os.path.join( mboxDir, 'resources/skins/Default/720p' )

	testSource = [ 'mbox_includes.xml',
	'NullWindow.xml', 'MainMenu.xml', 'ChannelListWindow.xml', 'LivePlate.xml', 'Configure.xml',
	'AntennaSetup.xml', 'TunerConfiguration.xml', ' SatelliteConfigSimple.xml', 'SatelliteConfigMotorized12.xml', 'SatelliteConfigMotorizedUsals.xml',
	'skip.xml', 'SatelliteConfigOnecable.xml', 'SatelliteConfigOnecable2.xml', 'SatelliteConfigDisEqC10.xml', 'SatelliteConfigDisEqC11.xml',
	'ChannelSearch.xml', 'AutomaticScan.xml','ManualScan.xml','TimeshiftPlate.xml', 'skip.xml',
	'EditSatellite.xml', 'EditTransponder.xml', 'ArchiveWindow.xml', 'SystemInfo.xml', 'Installation.xml',
	'MediaCenter.xml', 'EPGWindow.xml', 'ConditionalAccess.xml', 'FirstInstallation.xml', 'TimerWindow.xml',
	'skip.xml', 'Favorites.xml', 'SystemUpdate.xml', 'Help.xml' ]

	idDefault = 1000000
	count = 0
	global E_ID_SINGLE_CONVERT 
	for item in testSource :
		E_ID_SINGLE_CONVERT = idDefault + ( count * 100000 )
		iFile = os.path.join( confluenceDir, item )
		ParseSource( iFile )
		count += 1


if __name__ == "__main__":

	nameSelf = os.path.basename(sys.argv[0])
	gNoParseList[nameSelf] = nameSelf
	param = sys.argv[1:]

	if len(param) > 0 :
		if param[0] == 'debug' :
			gDebug = True

	AutoMakeSingleIDs( )
	#test( )
	#test2( )


