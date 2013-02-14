#-*- coding: utf-8 -*-

#from sys import setdefaultencoding
#setdefaultencoding('utf-8')
import os, re, shutil, time, sys
import sgmllib, string
from types import *

gNoParseList = {}
E_ID_LIVEPLATE = 50000

E_ID_EXCEPTION = [
	8800,
	8899
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

def AutoChangeControlIDs( ) :
	currDir = os.getcwd()
	mboxDir = os.path.abspath(currDir + '/../../../../script.mbox')
	elisDir = os.path.abspath(currDir + '/../../../../script.module.elisinterface')

	resultDir = os.getcwd() + '/changeTest'

	#init dir
	try:
		shutil.rmtree(resultDir)
		#os.remove(wFile1)
	except Exception, e:
		#print e
		pass
	os.mkdir(resultDir, 0775)


	confluenceDir = 'resources/skins/Default/720p/'
	openFile = confluenceDir + 'LivePlate.xml'
	changeFile = '%s/%s'% ( resultDir, 'LivePlate.xml' )
	sourceXml = ''
	try:
		rf = open( openFile, 'r' )
		sourceXml = rf.readlines( )
		rf.close( )

	except Exception, e:
		print 'Cannot open file[%s]'% openFile
		return

	fp = open(changeFile, 'w')

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

		if isMatch :
			print count, line

		fp.writelines( '%s\n'% line )
		count += 1

	fp.close( )

	print '---->changed[%s]'% countM


def ChangeIds( aMatch ) :
	idnumber = re.findall( '\d+', aMatch.group() )[0]
	changeid = E_ID_LIVEPLATE + int( idnumber )
	#print '----id[%s -> %s] match[%s]'% ( idnumber, changeid, aMatch.group() )

	value = re.sub( '\d+', '%s'% changeid, aMatch.group() )
	if int( idnumber ) in E_ID_EXCEPTION :
		value = aMatch.group()

	return value


def test( ) :
	#strs = '<animation effect="slide" start="300r,0" end="0r,0" delay="0" time="300" condition="Control.IsVisible(10) | !Control.IsVisible(15)">conditional</animation>'
	#ret = re.findall( E_PATTERN_STRINGS[9], strs, re.I )
	#strs = '<animation effect="slide" start="-200,0" end="0,0" delay="0" time="300" condition="ControlGroup(3620).HasFocus) | Control.HasFocus(702) | Control.HasFocus(706)">conditional</animation>'
	#strs = '<defaultcontrol always="true">3621</defaultcontrol>'
	#strs = '<defaultcontrol>2222</defaultcontrol>'
	strs = '<onup>Control.SetFocus(102,4)</onup>'

	for pattern in E_PATTERN_STRINGS :
		ret = re.findall( pattern, strs, re.I )
		if ret :
			p = re.compile( pattern )
			strs = p.sub(ChangeIds, strs )

	print strs


if __name__ == "__main__":

	nameSelf = os.path.basename(sys.argv[0])
	gNoParseList[nameSelf] = nameSelf
	param = sys.argv[1:]

	"""
	if len(param) > 0 :
		if param[0] == 'csv' :
			print 'create new csv : test.csv'
	else :
		test( )
	"""

	#AutoChangeControlIDs( )
	test( )


