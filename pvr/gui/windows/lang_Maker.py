#-*- coding: utf-8 -*-

#from sys import setdefaultencoding
#setdefaultencoding('utf-8')

import os, re, shutil
import sgmllib, string
from types import *

################# 1.make language/strings.xml of strings.xml, reference language pack Elmo~.csv
def csvToXML():

	#openFile = os.getcwd() + '/Language_Prime.csv'
	openFile = os.getcwd() + '/Language_Elmo.csv'
	wFile1 = 'Define_string.py'

	langPack = ["ENGLISH","DEUTSCH","FRENCH","ITALIAN","SPANISH","CZECH","DUTCH","POLISH","TURKISH","RUSSIAN"]
	tag1 = '<string id=\"%s\">'
	tag2 = '</string>'

	#init dir
	try:
		rmDir = os.getcwd() + '/language'
		shutil.rmtree(rmDir)
		os.remove(wFile1)
	except Exception, e:
		#print e
		pass


	try:
		rf = open(openFile, 'r')

	except Exception, e:
		print 'can not open file[%s]'% openFile
		return

	df = open(wFile1, 'w')

	"""
	#line = '"Remove, Lock, Set Group, etc.","deplacer, verouiller, grouper, etc.","236",,'
	line ='"English","French","STRING_INDEX",,"Remark", "1e3"'
	ret = re.findall('"([^"]*)"', line)
	print len(ret), ret
	"""



	line = rf.readline()
	ret = re.findall('"([^"]*)"', line)

	wFileList = []
	wf = []
	for i in range(len(ret)):
		#print i, ret[i].upper()
		for j in range(len(langPack)):
			if ret[i].upper() == langPack[j]:
				#mkdir
				try:
					wDir = os.getcwd() + ( '/language/%s/'% ret[i].capitalize() )
					os.mkdir(wDir, 0775)
				except Exception, e:
					wDir = os.getcwd() + '/language'
					os.mkdir(wDir, 0775)
					wDir = os.getcwd() + ( '/language/%s/'% ret[i].capitalize() )
					os.mkdir(wDir, 0775)

				#openfile
				wFileList.append(ret[i])
				#wFile = wDir + '%s_strings.xml'% ret[i].lower()
				wFile = wDir + 'strings.xml'
				wf.append( open( wFile, 'w' ) )

				str = '<?xml version="1.0" encoding="utf-8"?>\n<strings>\n'
				wf[i].writelines(str)
	#print wFileList


	sidx = 0
	for line in rf.readlines():

		#1. parse unicode-charactor in lines
		#ret = re.sub('"', '', line)			# 'Language_Prime.csv'
		#ret = ret.split(',')					# 'Language_Prime.csv'

		ret = re.findall('"([^"]*)"', line)		# 'Language091102.csv'

		if len(ret) < len(wFileList):			# if 'english',,,,,,,,digit then
			ret = re.sub('"', '', line)			# copyed english
			ret = re.split(',', ret)
			if len(ret) == len(wFileList)+1:
				for i in range(len(ret)-1):
					if ret[i+1] == '':
						ret[i+1] = 'NONE_' + ret[0]

		#print len(ret), ret

		ret2= re.sub('\n', '', line)
		ret2= ret2.split('",')

		#print len(ret), ret
		#print len(ret2), ret2[len(ret2)-1]

		#2. parse '%s', '%d', '%%' in list
		for i in range(len(ret)):
			ret[i] = re.sub('%s', '', ret[i])
			ret[i] = re.sub('%d', '', ret[i])
			ret[i] = re.sub('%%', '%', ret[i])
			#ret[i] = (ret[i].decode('utf-8')).encode('utf-8', 'xmlcharrefreplace')


		#write string.xml
		for i in range(len(wFileList)):
			try:
				strid = re.sub(',', '', ret2[len(ret2)-1])
				#strid = sidx

				str = '\t' + (tag1 % strid) + ret[i] + tag2 +'\n'
				wf[i].writelines(str)

			except Exception, e:
				#print 'error string.xml', e
				pass

		#write Define_string.py in English Name
		try:
			strid = re.sub(',', '', ret2[len(ret2)-1])
			#strid = ('%s'% sidx)

			strll = ret[0].upper()

			"""
			strll = re.split(' ', strll, 5)
			var_=''
			for i in range(len(strll)):
				var_ += '_' + strll[i]
			"""
			var_ = re.sub('-', '', strll)
			var_ = re.sub(' ', '_', var_)
			var_ = re.sub('__', '_', var_)
			var_ = re.sub('__', '_', var_)
			var_ = re.sub('\(', '', var_)
			var_ = re.sub('\)', '', var_)
			var_ = re.sub(':', '', var_)
			var_ = re.findall('[a-zA-Z0-9]\w*', var_)
			#var = var_[0][:15]

			str = 'LANG_' + var_[0] + ' = ' + strid +'\n'
			#print str
			df.writelines(str)

		except Exception, e:
			#print 'write error[%s], %s'% (e, wFile1)
			pass

		sidx += 1


	for i in range(len(wFileList)):
		wf[i].writelines('</strings>\n')
		wf[i].close()

	rf.close()
	df.close()


#----read strings.xml to make forign Language with csv
def readToXML(inFile):

	try:
		ef = open(inFile, 'r')

	except Exception, e:
		print 'can not open file[%s]'% inFile
		return

	#openFile = os.getcwd() + '/Language_Prime.csv'
	openFile = os.getcwd() + '/Language_Elmo.csv'
	wFile1 = 'Define_string.py'

	langPack = ["ENGLISH","DEUTSCH","FRENCH","ITALIAN","SPANISH","CZECH","DUTCH","POLISH","TURKISH","RUSSIAN"]
	tag1 = '<string id=\"%s\">'
	tag2 = '</string>'

	#init dir
	try:
		rmDir = os.getcwd() + '/language'
		shutil.rmtree(rmDir)
		os.remove(wFile1)
	except Exception, e:
		#print e
		pass

	try:
		rf = open(openFile, 'r')
		df = open(wFile1, 'w')
	except Exception, e:
		print 'can not open file[%s]'% openFile
		return


	"""
	#line = '"Remove, Lock, Set Group, etc.","deplacer, verouiller, grouper, etc.","236",,'
	line ='"English","French","STRING_INDEX",,"Remark", "1e3"'
	ret = re.findall('"([^"]*)"', line)
	print len(ret), ret
	"""



	line = rf.readline()
	ret = re.findall('"([^"]*)"', line)

	wFileList = []
	wf = []
	for i in range(len(ret)):
		#print i, ret[i].upper()
		for j in range(len(langPack)):
			if ret[i].upper() == langPack[j]:
				#mkdir
				try:
					wDir = os.getcwd() + ( '/language/%s/'% ret[i].capitalize() )
					os.mkdir(wDir, 0775)
				except Exception, e:
					wDir = os.getcwd() + '/language'
					os.mkdir(wDir, 0775)
					wDir = os.getcwd() + ( '/language/%s/'% ret[i].capitalize() )
					os.mkdir(wDir, 0775)

				#openfile
				wFileList.append(ret[i])
				#wFile = wDir + '%s_strings.xml'% ret[i].lower()
				wFile = wDir + 'strings.xml'
				wf.append( open( wFile, 'w' ) )

				str = '<?xml version="1.0" encoding="utf-8"?>\n<strings>\n'
				wf[i].writelines(str)
	#print wFileList

	sidx = 0
	csvfile = rf.readlines()
	for line in ef.readlines():
		inID = re.findall('id="([^"]*)"', line)
		inStr= re.findall('>([^"]*)</string>', line)
		"""
		if ret != [] :
			inID = ret
		if ret2 != []:
			inStr= ret2
		"""
		if inID != [] :
			#print 'inID[%s] inStr[%s]'% (inID[0], inStr[0])
			searchOn = False
			for csvline in csvfile:
				# string list
				ret = re.findall('"([^"]*)"', csvline)
				if len(ret) < len(wFileList):			# if 'english',,,,,,,,digit then
					ret = re.sub('"', '', csvline)			# copyed english
					ret = re.split(',', ret)
					if len(ret) == len(wFileList)+1:
						for i in range(len(ret)-1):
							if ret[i+1] == '':
								ret[i+1] = 'NONE_' + ret[0]

				# str id
				ret2= re.sub('\n', '', csvline)
				ret2= ret2.split('",')
				strid = re.sub(',', '', ret2[len(ret2)-1])

				# string.xml id == csv id
				#if inID[0] == strid :
				if inStr[0] == ret[0] :
					#print strid, ret
					searchOn = True
					csvret = ret
					csvret2= inID #ret2

			if searchOn == False:
				csvret = ['','','','','','','','','','','']	
				csvret2= ['','','','','','','','','','',''] # language pack is 0~9, 10'th <-- id
				csvret2[10]= inID[0]
				csvret[0] = inStr[0]
				for i in range(len(wFileList)) :
					csvret[i+1] = 'NONE_' + inStr[0]


			#2. parse '%s', '%d', '%%' in list
			for i in range(len(csvret)):
				csvret[i] = re.sub('%s', '', csvret[i])
				csvret[i] = re.sub('%d', '', csvret[i])
				csvret[i] = re.sub('%%', '%', csvret[i])
				#csvret[i] = (csvret[i].decode('utf-8')).encode('utf-8', 'xmlcharrefreplace')
	
	
			#write string.xml
			for i in range(len(wFileList)):
				try:
					strid = re.sub(',', '', csvret2[len(csvret2)-1])
					#strid = sidx
	
					str = '\t' + (tag1 % strid) + csvret[i] + tag2 +'\n'
					wf[i].writelines( str )
	
				except Exception, e:
					#print 'error string.xml', e
					pass
	
			#write Define_string.py in English Name
			try:
				strid = re.sub(',', '', csvret2[len(csvret2)-1])
				#strid = ('%s'% sidx)
	
				strll = csvret[0].upper()
	
				"""
				strll = re.split(' ', strll, 5)
				var_=''
				for i in range(len(strll)):
					var_ += '_' + strll[i]
				"""
				var_ = re.sub('-', '', strll)
				var_ = re.sub(' ', '_', var_)
				var_ = re.sub('__', '_', var_)
				var_ = re.sub('__', '_', var_)
				var_ = re.sub('\(', '', var_)
				var_ = re.sub('\)', '', var_)
				var_ = re.sub('/', '', var_)
				var_ = re.sub(':', '', var_)
				var_ = re.findall('[a-zA-Z0-9]\w*', var_)
				#var = var_[0][:15]

				strlen = len(var_[0]) - 1
				if var_[0][strlen] == '_' :
					defineStr = var_[0][:strlen-1]
				else :
					defineStr = var_[0]

				str = 'LANG_' + defineStr + ' = ' + strid +'\n'
				#print str
				df.writelines(str)
	
			except Exception, e:
				#print 'write error[%s], %s'% (e, wFile1)
				pass

		sidx += 1


	for i in range(len(wFileList)):
		wf[i].writelines('</strings>\n')
		wf[i].close()

	rf.close()
	df.close()


def verify_defineString():
	dfile = 'Define_string.py'
	try:
		ef = open(dfile, 'r')

	except Exception, e:
		print 'can not open file[%s]'% dfile
		return

	lines = ef.readlines()
	ef.close()


	ef = open(dfile, 'w')

	idx = 0			#verifying line
	verified = 0	#verified count
	for line in lines:
		ret = re.split('\W+', line)
		defineStr = ret[0]
		defineId  = int(ret[1])
		#print '%s %d'% (defineStr, defineId)

		for iline in lines:
			ret2 = re.split('\W+', iline)

			if (defineId != int(ret2[1])) and (defineStr == ret2[0]):
				line = defineStr + '_VERIFYED%s = %d'% (idx, defineId) + '\n'
				lines[idx] = line
				verified += 1
				#print '[%s][%s] equal[%s][%s]'% (defineStr, defineId, ret2[0], ret2[1] )

		ef.writelines(line)

		idx += 1

	ef.close()

	print 're-defined count = %d'% verified



################# 2.Collection string of property class in source file 'property.py'
from BeautifulSoup import BeautifulSoup
def findStringInXML(soup, reqStr) :

	isFind = False
	for node in soup.findAll('string'):
		if node.string == reqStr :
			#print 'id[%s]'% node['id']
			isFind = True
			break

	return isFind

def parseProperty( elisDir, stringXML ):

	if not elisDir :
		print 'Can not find source directory!\n'
		return -1

	sys.path.append(os.path.join(elisDir, 'lib', 'elisinterface'))
	from ElisProperty import _propertyMapEnum

	reservedWord = 'Min Hour 480i 480p 576i 576p 720p 1080i 1080p-25 CVBS RGB YC ms'
	timePattern  = '[0-9]{2}:[0-9]{2}|[0-9]*\*[0-9]'
	unitPattern  = '[0-9]* Min|[0-9]* s|[0-9]* ms|[0-9]* GB|[0-9]* Sec|[0-9] Hour|[0-9] \%'

	elementHash = {}
	for element in re.split(' ', reservedWord) :
		elementHash[element] = element
		#print element

	max = 0
	lines = ''
	soup = None
	if os.path.exists(stringXML) :
		fp = open(stringXML)
		soup = BeautifulSoup(fp)
		fp.close()

		rf = open(stringXML, 'rb')
		lines = rf.readlines()
		rf.close()

		lineCount = len(lines)
		lines.pop(lineCount-1)
		max = len(soup.strings) / 2

	wFile = 'stringsProperty.xml'
	wf = open(wFile, 'w')
	if lines :
		wf.writelines(lines)
	else :
		wf.writelines('<?xml version="1.0" encoding="utf-8"?>\n')
		wf.writelines('<strings>\n')

	countTot = 0
	countNew = 1000 + max + 1
	countRepeat=0
	repeatWord = ''
	for prop in _propertyMapEnum :
		mProperty = prop[0:]
		#print '%s'% prop[1:]

		for item in mProperty :
			try:
				if type(item) == TupleType : 
					element = list(item[1:])[0]
				else :
					element = item

				#filter
				timeStr  = re.findall(timePattern, element)
				unitStr  = re.findall(unitPattern, element)
				digitStr = re.sub(':', '', element)
				digitStr = re.sub('\s', '', digitStr)

				if elementHash.get(element) != None or ( soup and findStringInXML(soup, element) ) or \
					element.isdigit() or timeStr or unitStr or digitStr.isdigit() :
					repeatWord = '%s\n%s'% (repeatWord, element)
					countRepeat += 1

				else :
					line = '\t<string id=\"%d\">%s</string>\n'% (countNew, element)
					wf.writelines(line)
					elementHash[element] = countNew
					countNew += 1

				countTot += 1

			except Exception, e:
				print 'e[%s] line[%s]'% (e, prop)
				return


	wf.writelines('</strings>\n')
	wf.close()

	wf = open('repeatWord', 'w')
	wf.writelines(repeatWord)
	wf.close()
	#print 'repeatWord[%s]'% repeatWord
	print 'propertyTotal[%s] countNew[%s] countRepeat[%s]'% (countTot, countNew, countRepeat)
	
	os.rename(wFile, 'Strings.xml')
	
	return wFile



################# 3.Collection string of MR_LANG() in source file '*.py'
import glob
gCount = 0
gName = None
gNoParseList = {}
def findallSource(dir, patternStr, reqFile=None):
	retlist = glob.glob(os.path.join(dir, patternStr))
	findlist = os.listdir(dir)
	global gCount, gName
	searched = None

	for fname in findlist:
		next = os.path.join(dir, fname)
		if os.path.isdir(next) : 
			retlist += findallSource(next, patternStr, reqFile)
		else :
			if reqFile :
				if fname == reqFile :
					searched = '%s/%s'% (dir,fname)
					gName = searched
					break

			else :
				if gNoParseList.get(fname) != None :
					#print gNoParseList.get(fname)
					continue

				filename = os.path.splitext(fname)
				if filename[1] == '.py' :
					#print '[%s]%s/%s'% (gCount,dir,fname)
					parseSource('%s/%s'% (dir, fname))

					gCount += 1

	return retlist

def parseSource(sourceFile):
	if not sourceFile or os.path.splitext(sourceFile)[1] != '.py':
		print 'Can not read source file[%s]\n'% sourceFile
		return -1

	rFile = open(sourceFile, 'rb')
	rlines = rFile.readlines()
	rFile.close()

	reservedWord    = 'Min Hour 480i 480p 576i 576p 720p 1080i 1080p-25 CVBS RGB YC ms'
	timePattern     = '[0-9]{2}:[0-9]{2}|[0-9]*\*[0-9]'
	unitPattern     = '[0-9]* Min|[0-9]* s|[0-9]* ms|[0-9]* GB|[0-9]* Sec|[0-9] Hour'
	functionPattern = 'MR_LANG\(\'[^"\']*\'\)'
	stringPattern   = '\'([^"]*)\''

	elementHash = {}
	for element in re.split(' ', reservedWord) :
		elementHash[element] = element
		#print element

	soup = None
	max = 0
	lines = ''
	xmlFile = 'Strings.xml'
	if os.path.exists(xmlFile) :

		fp = open(xmlFile)
		soup = BeautifulSoup(fp)
		fp.close()

		rf = open(xmlFile, 'rb')
		lines = rf.readlines()
		rf.close()

		lineCount = len(lines)
		lines.pop(lineCount-1)
		max = len(soup.strings) / 2

	wFile = 'strings_temp.xml'
	wf = open(wFile, 'w')
	if lines :
		wf.writelines(lines)
	else :
		wf.writelines('<?xml version="1.0" encoding="utf-8"?>\n')
		wf.writelines('<strings>\n')

	countTot = 0
	countNew = max+1
	countRepeat=0
	repeatWord = ''

	#catch MR_LANG('*')
	strings = []
	for name in rlines :
		var = re.findall(functionPattern, name)
		for i in range(len(var)) : 
			ret = re.findall(stringPattern, var[i])
			if ret :
				strings.append(ret[0])
	#if len(strings) :
	#	print sourceFile
	#	print 'len[%s] catch MR_LANG\n%s'% (len(strings), strings)

	#write xml
	for element in strings :
		#filter
		timeStr  = re.findall(timePattern, element)
		unitStr  = re.findall(unitPattern, element)
		digitStr = re.sub(':', '', element)
		digitStr = re.sub('\s', '', digitStr)

		if elementHash.get(element) != None or ( soup and findStringInXML(soup, element) ) or \
			element.isdigit() or timeStr or unitStr or digitStr.isdigit() :
			repeatWord = '%s\n%s'% (repeatWord, element)
			countRepeat += 1

		else :
			line = '\t<string id=\"%d\">%s</string>\n'% (countNew, element)
			wf.writelines(line)
			elementHash[element] = countNew
			countNew += 1

		countTot += 1

	wf.writelines('</strings>\n')
	wf.close()

	#wf = open('repeatWord', 'w')
	#wf.writelines(repeatWord)
	#wf.close()
	#print 'repeatWord[%s]'% repeatWord
	#print 'source[%s]'% sourceFile
	#print 'propertyTotal[%s] countNew[%s] countRepeat[%s]'% (countTot, countNew, countRepeat)

	os.rename(wFile, 'Strings.xml')


################# 4. copy to Directory
from subprocess import *
def copyLanguage(srcDir, langDir) :
	if not os.path.exists(srcDir) :
		print 'Can not copy, srcDir[%s] is not exist'% srcDir
		return -1

	#shutil.copytree('language', langDir)
	cmd = 'cp -rf %s/* %s/'% (srcDir, langDir)
	p = Popen(cmd, shell=True, stdout=PIPE)
	result = p.stdout.read()

	if p.returncode == None and result == '':
		print 'copy to language Done.'
		shutil.rmtree('language')


########## installation
def AutoMakeLanguage() :
	currDir = os.getcwd()
	mboxDir = os.path.abspath(currDir + '/../../../../script.mbox')
	elisDir = os.path.abspath(currDir + '/../../../../script.module.elisinterface')
	#print elisDir
	stringFile = mboxDir + '/pvr/gui/windows/Strings.xml'
	propertyFile = elisDir + '/lib/elisinterface/ElisProperty.py'

	if os.path.exists(stringFile) :
		os.remove(stringFile)

	print '\033[1;%sm[%s]%s\033[1;m'% (32, 'make language', 'parse source')
	findallSource(mboxDir, '[a-zA-Z0-9]\w*.py')
	print 'findAll source[%s]'% gCount
	print '\033[1;%sm[%s]%s\033[1;m'% (30, 'make language', 'made string')
	readToXML(stringFile)

	print '\033[1;%sm[%s]%s\033[1;m'% (32, 'make language', 'parse property')
	parseProperty(elisDir, stringFile)
	print '\033[1;%sm[%s]%s\033[1;m'% (30, 'make language', 'made string')
	readToXML(stringFile)

	print '\033[1;%sm[%s]%s\033[1;m'% (32, 'make language', 'verifying localizedString ID')
	verify_defineString()

	print '\033[1;%sm[%s]%s\033[1;m'% (32, 'make language', 'copy to ../resource/language')
	langDir = mboxDir + '/resources/language'
	copyLanguage('language', langDir)

	print '\033[1;%sm%s\033[1;m\n'% (30, 'Completed..')


########## test
def test():
	pattern = '"([^"]*)"'
	wFileList = re.findall(pattern, '"ENGLISH","DEUTSCH","FRENCH","ITALIAN","SPANISH","CZECH","DUTCH","POLISH","TURKISH","RUSSIAN"')
	#line = '"4 Sec","4 Sek.","4 s","4 sec.","4 seg.","4 s","4 sec.","4 sek.","4 sn.","4 секунды",667'
	line = '"Sports",,,,,,,"bb",,,827'
	ret = re.findall(pattern, line)
	if len(ret) < len(wFileList):
		ret = re.sub('"', '', line)
		ret = re.split(',', ret)

		if len(ret) == len(wFileList)+1:

			for i in range(len(ret)-1):
				if ret[i+1] == '':
					ret[i+1] = 'NONE_' + ret[0]

	print len(ret), ret


def test2():
	#line = 'TV - CHANNEL LIST'
	#line = 'Zoom (PanScan)'
	line = '16:9 HDMI'
	"""
	var_ = re.sub('-', '', line)
	var_ = re.sub(' ', '_', var_)
	var_ = re.sub('__', '_', var_)
	var_ = re.sub('\(', '', var_)
	var_ = re.sub('\)', '', var_)
	var_ = re.findall('[a-zA-Z0-9]\w*', var_)
	"""

	"""
	var = '16:9 HDMI'
	#var = '-08:30'
	var_ = re.findall('[0-9]*:[0-9]*',var)[0]
	print var_
	"""

	"""
	functionPattern = 'MR_LANG\(\'[^"\']*\'\)'
	stringPattern   = '\'([^"]*)\''
	#var = "MR_LANG('Add to Fav. Group'), MR_LANG('None')"
	var = "MR_LANG('Add to Fav. Group')"
	var_ = re.findall(functionPattern, var)
	print var_
	for i in range(len(var_)) :
		str_ = re.findall(functionPattern, var_[i])
		print str_
	"""
	
	strDic = '[Delete Fav. Group]'
	print strDic.find('Delete Fav. Group')

import sys
if __name__ == "__main__":

	nameSelf = sys.argv[0]
	gNoParseList[nameSelf] = nameSelf
	cmd = sys.argv[1:]

	"""
	if len(cmd) >= 0 :
		if cmd[0] == 'property.py':
			wFile = parseProperty(cmd[1])
			cmd[0] = wFile

		print '%s to xml, with csv'% cmd[0]
		readToXML(cmd[0])

	else :
		print 'csv to xml'
		csvToXML()

	verify_defineString()

	#test()
	#test2()
	"""
	#findallSource(sourceDir, '[a-zA-Z0-9]\w*.py', 'Strings.xml')
	#findallSource(propertyDir, '[a-zA-Z0-9]\w*.py', 'ElisProperty.py')
	#print 'fname[%s] gcount[%s]'% (gName, gCount)
	#testDir = '/home/youn/devel/elmo_test/test/elmo-nand-image/home/root/.xbmc/addons/script.mbox'
	#findallSource(testDir, '[a-zA-Z0-9]\w*.py')

	AutoMakeLanguage()

