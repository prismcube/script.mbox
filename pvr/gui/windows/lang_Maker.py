#-*- coding: utf-8 -*-

#from sys import setdefaultencoding
#setdefaultencoding('utf-8')

import os, re, shutil, time, sys
import sgmllib, string
from types import *
import codecs
import parser

ID_NODE_XMLSTRINGS  = 0		# *.xml    :    0 ~ 1999
ID_NODE_PROPERTY    = 2000	# property : 2000 ~ 2999
ID_NODE_MRLANG      = 3000	# *.py     : 3000 ~ 5000

TAG_NAME_STRINGS    = 'strings'
TAG_NAME_PROPERTY   = 'property'
TAG_NAME_XMLSTRINGS = 'xmlstrings'

E_FILE_CSV          = 'Language_Elmo.csv'
E_FILE_PROPERTY     = 'ElisProperty.py'
E_FILE_MBOX_STRING  = 'MboxStrings.xml'
E_FILE_MBOX_STRING_ID = 'MboxStringsID.py'

E_DEBUG_NONE_STRING_WRITE = False
E_DEBUG_EMPTY_STRING_WRITE = True

E_COLOR_INDEX = {
    'white':      "\x1b[37m",
    'yellow':     "\x1b[33m",
    'green':      "\x1b[32m",
    'blue':       "\x1b[34m",
    'cyan':       "\x1b[36m",
    'red':        "\x1b[31m",
    'magenta':    "\x1b[35m",
    'black':      "\x1b[30m",
    'darkwhite':  "\x1b[37m",
    'darkyellow': "\x1b[33m",
    'darkgreen':  "\x1b[32m",
    'darkblue':   "\x1b[34m",
    'darkcyan':   "\x1b[36m",
    'darkred':    "\x1b[31m",
    'darkmagenta':"\x1b[35m",
    'darkblack':  "\x1b[30m",
    'off':        "\x1b[0m"
}

def EucToUtf( aSource ) :
	if aSource == None :
		return

	try :
		content = aSource.encode('utf-8')

	except Exception, e :
		#print 'except utf8[%s]'% aSource
		#'aSource' is utf-8 string
		content = aSource

	return content


################# 1.make language/strings.xml of strings.xml, reference language pack Elmo~.csv

# deprecated
def csvToXML():

	#openFile = os.getcwd() + '/Language_Prime.csv'
	openFile = os.getcwd() + '/%s'% E_FILE_CSV
	wFile1 = '%s'% E_FILE_MBOX_STRING_ID

	langPack = ["ENGLISH","GERMAN","FRENCH","ITALIAN","SPANISH","CZECH","DUTCH","POLISH","TURKISH","RUSSIAN","ARABIC","KOREAN","SLOVAK","UKRAINIAN"]
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
		print 'Could not open file[%s]'% openFile
		return

	df = open(wFile1, 'w')

	'''
	#line = '"Remove, Lock, Set Group, etc.","deplacer, verouiller, grouper, etc.","236",,'
	line ='"English","French","STRING_INDEX",,"Remark", "1e3"'
	ret = re.findall('"([^"]*)"', line)
	print len(ret), ret
	'''



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

		#write MboxStringsID.py in English Name
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
def makeLanguage(inFile):

	try:
		ef = open(inFile, 'r')

	except Exception, e:
		print 'Could not open file[%s]'% inFile
		return

	#input document is UTF-8 format only
	#openFile = os.getcwd() + '/Language_Prime.csv'
	openFile = os.getcwd() + '/%s'% E_FILE_CSV
	#openFile = os.getcwd() + '/test.csv'
	wFile1 = E_FILE_MBOX_STRING_ID

	langPack = ["ENGLISH","GERMAN","FRENCH","ITALIAN","SPANISH","CZECH","DUTCH","POLISH","TURKISH","RUSSIAN","ARABIC","KOREAN","SLOVAK","UKRAINIAN"]
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
		print 'Could not open file[%s]'% openFile
		return


	'''
	#line = '"Remove, Lock, Set Group, etc.","deplacer, verouiller, grouper, etc.","236",,'
	line ='"English","French","STRING_INDEX",,"Remark", "1e3"'
	ret = re.findall('"([^"]*)"', line)
	print len(ret), ret
	'''



	line = rf.readline()
	ret = re.findall('"([^"]*)"', line)

	wFileList = []
	wf = []
	for i in range( len(ret) ) :
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
				#wf.append( codecs.open( wFile, 'w', encoding='utf-8-sig' )

				string = EucToUtf( '<?xml version="1.0" encoding="utf-8"?>\r\n<strings>\r\n' )
				wf[i].writelines(string)
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
			#print 'inID[%s] inStr[%s]'% (inID[0], inStr)
			searchOn = False
			for csvline in csvfile:
				# string list
				ret = re.findall('"([^"]*)"', csvline)
				if len(ret) < len(wFileList):			# if id, 'english',,,,,,,, then
					#print 'len[%s] str[%s]'% ( len(ret), ret )
					ret = re.sub('"', '', csvline)
					ret = re.split(';', ret)
					#rets = []
					#for sentence in ret :
					#	sentence = re.sub('"', '', sentence)
					#	rets.append( sentence )			# copyed english
					#print len(ret), ret
					#print len( rets ), rets


					if len(ret) == len(wFileList)+1 :
						for i in range(len(ret)-1) :
							if ret[i+1] == '' :
								#ret[i+1] = 'NONE_' + ret[0]
								j = i + 1
								if j >= len(wFileList) - 1 :
									j = len(wFileList) - 1

								debugString = ''
								if E_DEBUG_NONE_STRING_WRITE :
									debugString = '%s_'% wFileList[j][:3]

								if E_DEBUG_EMPTY_STRING_WRITE :
									ret[i+1] = debugString
								else :
									ret[i+1] = debugString + ret[0]
								#print '----------[%s]'% rets[i+1]

				# str id
				#ret2= re.sub('\n', '', csvline)
				#ret2= ret2.split('",')
				#strid = re.sub(',', '', ret2[len(ret2)-1])

				ret2 = re.split( ';', csvline )
				strid = ret2[ len(ret2)-1 ]
				#print 'strid[%s] len[%s] str[%s]'% ( strid, len(ret2), ret2 )

				# string.xml id == csv id
				#if inID[0] == strid :
				if inStr[0] == ret[0] :
					#print strid, ret
					searchOn = True
					csvret = ret
					csvret2= inID #ret2
					break

			if searchOn == False:
				csvret= ['','','','','','','','','','','','','','','']
				csvret2= ['','','','','','','','','','','','','','',''] # language pack is 0~13, 14'th <-- id
				csvret2[14]= inID[0]
				csvret[0] = inStr[0]
				for i in range(len(wFileList)) :
					#csvret[i+1] = 'NONE_' + inStr[0]
					j = i + 1
					if j >= len(wFileList) - 1 : 
						j = len(wFileList) - 1

					debugString = ''
					if E_DEBUG_NONE_STRING_WRITE :
						debugString = '%s_'% wFileList[j][:3]

					if E_DEBUG_EMPTY_STRING_WRITE :
						csvret[i+1] = debugString
					else :
						csvret[i+1] = debugString + inStr[0]
					#print '----------[%s]'% csvret[i+1]


			"""
			#2. parse '%s', '%d', '%%' in list
			for i in range(len(csvret)):
				csvret[i] = re.sub('%s', '', csvret[i])
				csvret[i] = re.sub('%d', '', csvret[i])
				csvret[i] = re.sub('%%', '%', csvret[i])
				#csvret[i] = (csvret[i].decode('utf-8')).encode('utf-8', 'xmlcharrefreplace')
			"""

			#write string.xml
			for i in range(len(wFileList)):
				try:
					strid = re.sub(';', '', csvret2[len(csvret2)-1])
					#strid = sidx
	
					string = '\t' + (tag1 % strid) + csvret[i] + tag2 + '\r\n'
					wf[i].writelines( EucToUtf(string) )

				except Exception, e:
					#print string
					#print 'error i[%s] e[%s]'% (i, e)
					pass

			#write MboxStringsID.py in English Name
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

				string = 'LANG_' + defineStr + ' = ' + strid +'\r\n'
				#print str
				df.writelines(string)
	
			except Exception, e:
				#print 'write error[%s], %s'% (e, wFile1)
				pass

		sidx += 1

	for i in range(len(wFileList)):
		wf[i].writelines(EucToUtf('</strings>\r\n'))
		wf[i].close()

	rf.close()
	df.close()


def verify_defineString():
	dfile = E_FILE_MBOX_STRING_ID
	try:
		ef = open(dfile, 'r')

	except Exception, e:
		print 'Could not open file[%s]'% dfile
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
				line = defineStr + '_VERIFYED%s = %d'% (idx, defineId) + '\r\n'
				lines[idx] = line
				verified += 1
				#print '[%s][%s] equal[%s][%s]'% (defineStr, defineId, ret2[0], ret2[1] )

		ef.writelines(line)

		idx += 1

	ef.close()

	print 're-defined count = %d'% verified



################# 2.Collection string of property class in source file 'property.py'
sys.path.append( os.path.join( os.getcwd() + '/../../../../script.mbox', 'libs', 'beautifulsoup' ) )
from BeautifulSoup import BeautifulSoup
def findStringInXML(soup, reqStr) :

	isFind = False
	for node in soup.findAll('string') :
		if node.string == reqStr :
			#print 'id[%s]'% node['id']
			isFind = True
			break

	return isFind


gStringHash = {}
gStringAllHash = {}
gTagString = []
gTagProperty = []
gTagXmlString = []
def parseStringInXML(xmlFile, tagName) :

	soup = None
	lines = []
	nodeAll = ''
	excuteEnd = False

	if os.path.exists(xmlFile) :
		fp = open(xmlFile)
		soup = BeautifulSoup(fp)
		fp.close()

		for node in soup.findAll(tagName) :
			for element in node.findAll('string') :
				elementry = [ int(element['id']), element.string, '%s\r\n'% repr(element) ]
				lines.append(elementry)

				if gStringHash.get( element.string, -1 ) == -1 :
					gStringHash[element.string] = int( element['id'] )

				else :
					if tagName == TAG_NAME_XMLSTRINGS :
						excuteEnd = True
						print '\033[1;41mRepeat same strings id[%s] string[%s]\033[1;m'% ( int(element['id']), element.string )
			
			nodeAll = node

		#print len(lines), lines[len(lines)-1][0]

	if excuteEnd :
		print 'correct string(s) and try again !!!'
		sys.exit( )

	return soup, lines


def parseProperty( elisDir, stringXML ):

	if not elisDir :
		print 'Could not find source directory!\n'
		return -1

	sys.path.append(os.path.join(elisDir, 'lib'))
	from elisinterface.ElisProperty import _propertyMapEnum

	reservedHash = {}
	for element in re.findall('"([^"]*)"', gReservedWord) :
		reservedHash[element] = element
		#print element

	countTot = 0
	countNew = 0
	countContinue = 1
	if gTagProperty and len( gTagProperty ) > 0 :
		countContinue += gTagProperty[len( gTagProperty )-1][0]
	if countContinue < ID_NODE_PROPERTY :
		countContinue += ID_NODE_PROPERTY
	countRepeat=0
	repeatWord = ''
	for prop in _propertyMapEnum :
		mProperty = prop[0:]
		#print '%s'% mProperty

		for item in mProperty :
			try:
				if type(item) == TupleType : 
					element = list(item[1:])[0]
				else :
					element = item

				#filter
				timeStr  = re.findall(gTimePattern, element)
				unitStr  = re.findall(gUnitPattern, element)
				digitStr = re.sub(':', '', element)
				digitStr = re.sub('\s', '', digitStr)

				if reservedHash.get(element, -1) == -1 and \
				   ( not element.isdigit() ) and ( not timeStr ) and ( not digitStr.isdigit() ) :
					gStringAllHash[element] = countContinue

				#if reservedHash.get(element) != None or ( soup and findStringInXML(soup, element) ) or \
				if gStringHash.get( element, -1 ) != -1 or reservedHash.get(element) != None or \
				   element.isdigit() or timeStr or unitStr or digitStr.isdigit() :
					repeatWord = '%s\n%s'% (repeatWord, element)
					countRepeat += 1

				else :
					line = '<string id=\"%d\">%s</string>\r\n'% (countContinue, element)
					listElement = [ countContinue, element, line ]
					gTagProperty.append( listElement )
					gStringHash[element] = countContinue
					gStringAllHash[element] = countContinue

					countContinue += 1
					countNew += 1

				countTot += 1

			except Exception, e:
				print 'e[%s] line[%s]'% (e, prop)
				return


	wf = open('repeatWord', 'a')
	wf.writelines(repeatWord)
	wf.close()
	#print 'repeatWord[%s]'% repeatWord
	print 'propertyTotal[%s] New[%s] Repeat[%s]'% (countTot, countNew, countRepeat)
	
	#os.rename( wFile, E_FILE_MBOX_STRING )



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
				if gNoParseList.get(fname) == fname :
					#print gNoParseList.get(fname)
					continue

				filename = os.path.splitext(fname)
				if filename[1] == '.py' :
					#print '[%s]%s/%s'% (gCount,dir,fname)
					parseSource('%s/%s'% (dir, fname))

					gCount += 1

	return retlist


gAtot = 0
gAnew = 0
gArep = 0
default_keywords = ['MR_LANG']
def parseSource(sourceFile):
	if not sourceFile or os.path.splitext(sourceFile)[1] != '.py':
		print 'Could not read source file[%s]\n'% sourceFile
		return -1

	rFile = open(sourceFile, 'rb')
	rlines = rFile.readlines()
	rFile.close()

	functionPattern = "MR_LANG\s*\(\s*\'[([^']|[^\\])*]*\'\s*\)"
	stringPattern   = "'([^\\*]*)'"

	reservedHash = {}
	for element in re.findall('"([^"]*)"', gReservedWord) :
		reservedHash[element] = element
		#print element

	countTot = 0
	countNew = 0
	countContinue = 1
	if gTagString and len( gTagString ) > 0 :
		countContinue += gTagString[len( gTagString )-1][0]
	if countContinue < ID_NODE_MRLANG :
		countContinue += ID_NODE_MRLANG
	countRepeat=0
	repeatWord = ''

	#catch MR_LANG('*')
	strings = []

	class Options:
		keywords = []
		docstrings = 0
		nodocstrings = {}

	options = Options()
	fpbase = open(sourceFile)

	options.keywords.extend(default_keywords)
	options.toexclude = []

	eater = parser.TokenEater(options)
	parser.tokenize.tokenize(fpbase.readline, eater)
	eater.exchange(strings)

	"""
	for name in rlines :
		var = re.findall(functionPattern, name)
		for i in range(len(var)) : 
			ret = re.findall(stringPattern, var[i])
			if ret :
				strings.append(ret[0])
	"""

	if len(strings) :
		print sourceFile
		print 'len[%s] catch MR_LANG\n%s'% (len(strings), strings)

	#write xml
	for element in strings :
		#filter
		timeStr  = re.findall(gTimePattern, element)
		#unitStr  = re.findall(gUnitPattern, element)
		digitStr = re.sub(':', '', element)
		digitStr = re.sub('\s', '', digitStr)

		if element[0] == "'" :
			element = element[1:len(element)-1]

		if reservedHash.get(element, -1) == -1 and \
		   ( not element.isdigit() ) and ( not timeStr ) and ( not digitStr.isdigit() ) :
			gStringAllHash[element] = countContinue

		if gStringHash.get( element, -1 ) != -1 or reservedHash.get(element) != None or \
		   element.isdigit() or timeStr or digitStr.isdigit() :
			repeatWord = '%s\n%s'% (repeatWord, element)
			countRepeat += 1

		else :
			line = '<string id=\"%d\">%s</string>\r\n'% (countContinue, element)
			listElement = [ countContinue, element, line ]
			gTagString.append( listElement )
			gStringHash[element] = countContinue
			gStringAllHash[element] = countContinue
			countContinue += 1
			countNew += 1

		countTot += 1

	wf = open('repeatWord', 'w')
	wf.writelines(repeatWord)
	wf.close()
	#print 'repeatWord[%s]'% repeatWord
	#print 'source[%s]'% sourceFile

	global gAtot,gAnew,gArep
	if countTot :
		gAtot += countTot
		gAnew += countNew
		gArep += countRepeat
		print 'MR_LANG Total[%s] \033[1;33m NewLang[%s]\033[1;m Repeat[%s]'% (countTot, countNew, countRepeat)
		print 'gtot[%s] gnew[%s] grep[%s]'% (gAtot,gAnew,gArep)

	#os.rename( wFile, E_FILE_MBOX_STRING )
	#shutil.copyfile( wFile, E_FILE_MBOX_STRING )
	#time.sleep(0.01)


################# 4. copy to Directory
from subprocess import *
def copyLanguage(srcDir, langDir) :
	if not os.path.exists(srcDir) :
		print 'Could not copy, srcDir[%s] is not exist'% srcDir
		return -1

	#shutil.copytree('language', langDir)
	cmd = 'cp -rf %s/* %s/'% (srcDir, langDir)
	p = Popen(cmd, shell=True, stdout=PIPE)
	result = p.stdout.read()
	p.stdout.close()
	if p.returncode == None and result == '':
		print 'copy to language Done.'
		shutil.rmtree('language')



# resource/../strings.xml to CSV
def Make_NewCSV( ) :
	#langPack = ["ENGLISH","GERMAN","FRENCH","ITALIAN","SPANISH","CZECH","DUTCH","POLISH","TURKISH","RUSSIAN","ARABIC","KOREAN","SLOVAK","UKRAINIAN"]
	langPack = ["ENGLISH","GERMAN","CZECH","SLOVAK","POLISH","FRENCH","ITALIAN","SPANISH","RUSSIAN","UKRAINIAN","DUTCH","TURKISH","ARABIC","KOREAN"]

	mboxDir = os.path.abspath(os.getcwd() + '/../../../../script.mbox')
	langDir = mboxDir + '/resources/language'
	langList = os.listdir(langDir)

	strFileFD = []
	langStrings=[]

	for strfile in langPack :
		openFile = '%s/%s/strings.xml'% ( langDir, strfile.capitalize() )
		if not os.path.exists( openFile ) :
			dirname = os.path.dirname( openFile )
			if not os.path.exists( dirname ) :
				os.makedirs( dirname, 0775 )
			open( openFile, 'w' ).close()

		print 'reading [%s]'% openFile

		fp = open(openFile, 'r')
		strFileFD.append( fp )

		lines = []
		soup = BeautifulSoup(fp)

		for element in soup.findAll('string') :
			elementry = None
			eleStr = None

			eleStr = unicode(element.string).encode('utf-8')
			try :
				if element.string == None :
					eleStr = ''

				elif len(eleStr) > 3 and eleStr[3] == '_' :
					eleStr = ''

				elif len(eleStr) > 3 and eleStr[len(eleStr) - 2 :] == '\r\n' :
					#print repr(eleStr).decode('utf-8'), repr(eleStr[len(eleStr) - 2 :])
					eleStr = eleStr[0:len(eleStr) - 2]

			except Exception, e :
				print 'except[%s] str[%s][%s]'% (e, element.string, int(element['id']) )
				pass

			elementry = [ int(element['id']), eleStr ]
			lines.append( elementry )

		langStrings.append( lines )


	for i in range(len(langPack)) :
		strFileFD[i].close()


	openFile = 'test.csv'
	fd = open( openFile, 'w' )
	title = ''
	for item in langPack :
		title += '\"%s\";'% item

	fd.writelines( title[:len(title)] + '\"STRING_INDEX\"\r\n' )

	for i in range( len(langStrings[0]) ) :
		csvStr = ''
		for j in range(len(langPack)) :
			try :
				comma= ';'
				lang = '%s'% langStrings[j][i][1]
				if langStrings[j][i][1] != '' :
					lang = '\"%s\"'% langStrings[j][i][1]

				if j == ( len(langPack)-1 ) :
					comma = ''

				csvStr += lang + comma
			except Exception, e :
				print 'except[%s] langNo[%s] id[%s]'% (e, j, i)
				comma = ';'
				if j == ( len(langPack)-1 ) :
					comma = ''
				csvStr += comma


		csvStr = '%s;%s\r\n'% ( csvStr, langStrings[0][i][0] )
		fd.writelines( EucToUtf(csvStr) )

	fd.close( )


# append string to CSV by empty word
def updateCSV( ) :
	openFile = os.getcwd() + '/%s'% E_FILE_CSV
	stringFile = os.getcwd() + '/%s'% E_FILE_MBOX_STRING
	tempFile = os.getcwd() + '/test_.csv'

	fp = open( stringFile, 'r' )
	soup = BeautifulSoup(fp)
	fp.close()

	tagList = [ TAG_NAME_XMLSTRINGS, TAG_NAME_PROPERTY, TAG_NAME_STRINGS ]
	defaultID = [ ID_NODE_XMLSTRINGS, ID_NODE_PROPERTY, ID_NODE_MRLANG ]
	stringXML = []
	csvString = [[],[],[]]
	csvHash = {}
	xmlHashBackup = {}
	csvHashBackup = {}

	# 1--------- 'hash mboxString.xml'
	for tagName in tagList :
		for node in soup.findAll(tagName) :
			tags = []
			for element in node.findAll('string') :
				elementry = [ int(element['id']), element.string ]
				tags.append( elementry )
				xmlHashBackup[element.string] = int(element['id'])

			stringXML.append( tags )


	# 2--------- 'hash langage_Elmo.csv'

	rf = open( openFile, 'r' )
	csvOld = rf.readlines()
	rf.close()

	title = csvOld[0]
	csvOld.pop( 0 )

	for csvline in csvOld :
		ret = re.split(';', csvline)
		csvStr = re.findall('"([^"]*)"', csvline)

		strid = int( ret[len(ret) - 1] )
		csvHash[csvStr[0]] = strid

		csvHashBackup[csvline] = csvStr[0]

		if strid < ID_NODE_PROPERTY :
			csvString[0].append( csvline )
		elif strid >= ID_NODE_PROPERTY and strid < ID_NODE_MRLANG :
			csvString[1].append( csvline )
		elif strid >= ID_NODE_MRLANG :
			csvString[2].append( csvline )

			#print csvHash.get( "When set to 'Automatic', the time will be obtained by the receiver automatically from a specific channel that you select", None )

	# 3--------- 'new word to append csv'
	newString = []
	for tags in range( len(stringXML) ) :
		for stringEng in stringXML[tags] :
			if csvHash.get( stringEng[1], -1 ) == -1 :
				newString.append( stringEng )

				#temp = '\"%s\";;;;;;;;;;;;;;%s\r\n'% ( stringEng[1], defaultID[tags] + len( csvString[tags] ) + 1 )
				temp = '\"%s\";;;;;;;;;;;;;;%s\r\n'% ( stringEng[1], stringEng[0] )
				csvString[tags].append( temp )
				csvHashBackup[temp] = stringEng[1]
				print 'newString id[%s] lang[%s]'% ( stringEng[0], stringEng[1] )

	#if newString and len( newString ) > 0 :
	deleteCSV = []
	wf = open( tempFile, 'w' )
	wf.writelines( title )
	for tags in range( len(csvString) ) :
		for strings in csvString[tags] :
			stringEng = csvHashBackup.get( strings, '' )
			stringId = xmlHashBackup.get(stringEng, -1 )
			if stringEng and stringId != -1 :
				wf.writelines( strings )
			else :
				deleteCSV.append([csvHash.get(stringEng, -1),strings.rstrip()])

	for stringId, strings in deleteCSV :
		print '%s delete csv : oldString id[%s] name[%s]%s'% ( E_COLOR_INDEX['red'], stringId, strings, E_COLOR_INDEX['off'] )

	wf.close()
	os.rename(tempFile, openFile)

	print '\033[1;33m update newString[%s]\033[1;m'% len( newString )


def updateXML( ) :
	wf = open(E_FILE_MBOX_STRING , 'w')
	wf.writelines( '<?xml version="1.0" encoding="utf-8"?>\r\n' )

	#1. <xmlstrings>
	if gTagXmlString :
		wf.writelines( '<%s>\r\n'% TAG_NAME_XMLSTRINGS )
		for line in gTagXmlString :
			wf.writelines( '\t%s'% line[2] )
		wf.writelines( '</%s>\r\n'% TAG_NAME_XMLSTRINGS )

	#2. <property>
	if gTagProperty :
		wf.writelines( '<%s>\r\n'% TAG_NAME_PROPERTY )
		for line in gTagProperty :
			if gStringAllHash.get( line[1], -1 ) != -1 :
				wf.writelines( '\t%s'% line[2] )
		wf.writelines( '</%s>\r\n'% TAG_NAME_PROPERTY )

	#3. <strings>
	if gTagString :
		wf.writelines( '<%s>\r\n'% TAG_NAME_STRINGS )
		for line in gTagString :
			if gStringAllHash.get( line[1], -1 ) != -1 :
				wf.writelines( '\t%s'% line[2] )
		wf.writelines( '</%s>\r\n'% TAG_NAME_STRINGS )

	wf.close( )


########## installation
gReservedWord  = '"Min" "Hour" "480i" "480p" "576i" "576p" "720p" "1080i" "1080p-25" "CVBS" '
gReservedWord += '"RGB" "YC" "ms" "FAT" "FAT16" "FAT32" "EXT2" "EXT3" "EXT4" "NTFS" '
gReservedWord += '"EXR" "EXU" "UAS" "MDU" "HDCP" "HDMI" "YUV" "HDMI / YUV" "DVB-S (SD)" "DVB-S (HD)" '
gReservedWord += '"PAL" "NTSC" "SCART" "DE" "AT" "SI" "FTI" "EXR EXU SCR" "EXR ... / EXU ..." "UPnP"'
gTimePattern  = '[0-9]{2}:[0-9]{2}|[0-9]*\*[0-9]'
#gUnitPattern  = '[0-9] Min|[0-9] s|[0-9] ms|[0-9] GB|[0-9] Sec|[0-9] Hour|[0-9] \%'
gUnitPattern  = '[0-9] s|[0-9] ms|[0-9] GB|[0-9] Sec|[0-9] \%'
#gUnitPattern +=	'|QPSK [0-9]\/[0-9]|8PSK [0-9]\/[0-9]|DiSEqC [0-9]\.[0-9]|UAS [0-9]*'
gUnitPattern +=	'|QPSK [0-9]\/[0-9]|8PSK [0-9]\/[0-9]|UAS [0-9]*'

def AutoMakeLanguage() :
	currDir = os.getcwd()
	mboxDir = os.path.abspath(currDir + '/../../../../script.mbox')
	elisDir = os.path.abspath(currDir + '/../../../../script.module.elisinterface')
	#print elisDir
	stringFile = mboxDir + '/pvr/gui/windows/%s'% E_FILE_MBOX_STRING
	propertyFile = elisDir + '/lib/elisinterface/%s'% E_FILE_PROPERTY
	global gTagString, gTagProperty, gTagXmlString, gStringHash, gStringAllHash
	#makeLanguage(mboxDir + '/pvr/gui/windows/test.xml')
	#return

	#if os.path.exists(stringFile) :
	#	os.remove(stringFile)

	###### 1. collection source
	soup, gTagXmlString = parseStringInXML(E_FILE_MBOX_STRING, TAG_NAME_XMLSTRINGS )
	soup, gTagProperty  = parseStringInXML(E_FILE_MBOX_STRING, TAG_NAME_PROPERTY )
	soup, gTagString    = parseStringInXML(E_FILE_MBOX_STRING, TAG_NAME_STRINGS )

	###### 1. collection property
	print '\n\033[1;%sm[%s]%s\033[1;m'% (32, 'make language', 'parse property')
	parseProperty(elisDir, stringFile)

	###### 2. collection mr_lang()
	print '\n\033[1;%sm[%s]%s\033[1;m'% (32, 'make language', 'parse source')
	findallSource(mboxDir, '[a-zA-Z0-9]\w*.py')
	print '\nfindAll *.py files[%s]'% gCount

	#print gStringAllHash.keys( )

	print '\033[1;%sm[%s]%s\033[1;m'% (30, 'make language', 'update xml : %s'% E_FILE_MBOX_STRING )
	updateXML( )

	print '\033[1;%sm[%s]%s\033[1;m'% (30, 'make language', 'update csv : %s'% E_FILE_CSV )
	updateCSV( )

	print '\033[1;%sm[%s]%s\033[1;m'% (30, 'make language', 'make string --> resource/language/../strings.xml')
	makeLanguage(stringFile)

	print '\n\033[1;%sm[%s]%s\033[1;m'% (32, 'make language', 'verifying ID : %s'% E_FILE_MBOX_STRING_ID )
	verify_defineString()
	return

	print '\n\033[1;%sm[%s]%s\033[1;m'% (32, 'make language', 'copy to ../resource/language')
	langDir = mboxDir + '/resources/language'
	copyLanguage('language', langDir)

	print '\n\033[1;%sm%s\033[1;m'% (30, 'Completed')


########## test
def test():
	pattern = '"([^"]*)"'
	wFileList = re.findall(pattern, '"ENGLISH","GERMAN","FRENCH","ITALIAN","SPANISH","CZECH","DUTCH","POLISH","TURKISH","RUSSIAN","ARABIC","KOREAN","SLOVAK","UKRAINIAN"')
	#line = '"4 Sec","4 Sek.","4 s","4 sec.","4 seg.","4 s","4 sec.","4 sek.","4 sn.","4 секунды",667'
	line = '"Sports",,,,,,,"bb",,,,,,,827'
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

	#functionPattern = 'MR_LANG\s*\(\s*\'[^"\']*\'\s*\)'
	#stringPattern   = '\'([^\'*]*)\''
	#functionPattern = "MR_LANG\s*\(\s*\'[^\\*]*\'\s*\)"
	#stringPattern   = "'([^\\*]*)'"

	#functionPattern = "MR_LANG\s*\(\s*'[([^']|[^\\])*]*'\s*\)"
	#stringPattern   = "'[([^']|[^\\])*]*'"
	functionPattern = "MR_LANG\s*\(\s*'*?'\s*\)"
	stringPattern   = "'[([^']|[^\\])*]*'"

	var = "MR_LANG   (  'Add to Fav., %s _ __ -& \n 's Group' ), aaa, 'bbb',  MR_LANG('None')"
	#var = "			context.append( ContextItem( MR_LANG( 'Move' ),   CONTEXT_ACTION_MOVE ) )"
	#var = "MR_LANG( 'Add to Fav. %s _ __ -& \n \' s '  )"
	#var_ = re.findall(functionPattern, var)
	var_ = re.search(functionPattern, var)
	print var_.group()

	for i in range(len(var_)) :
		str_ = re.findall(stringPattern, var_[i])
		print '[%s]'% repr(str_)
	
	#strDic = '[Delete Fav. Group]'
	#print strDic.find('Delete Fav. Group')


def test3():
	testDir = '/home/youn/devel/elmo_test/test/elmo-nand-image/home/root/.xbmc/addons/script.mbox'
	xmlFile = testDir + '/pvr/gui/windows/%s'% E_FILE_MBOX_STRING
	fp = open(xmlFile)
	soup = BeautifulSoup(fp)
	fp.close()

	for node in soup.findAll('strings'):
		#break
		for element in node.findAll('string') :
			#print element['id'], element.string
			print element
		#print node

	#print len(node(0))
	#print node(0)


def test4():
	def stripResult(param):
		return (param[1:len(param)-1]).strip()
	#var = "MR_LANG   (  'Add to Fav., %s _ __ -& \n 's Group' ), aaa, 'bbb', MR_LANG('None')"
	#var = "MR_LANG( 'Add to Fav. %s _ __ -& \n \' s '  )"
	var = "			context.append( ContextItem( MR_LANG( 'Move' ),   CONTEXT_ACTION_MOVE ) )"

	ptnAll = "MR_LANG\s*"
	ptnSub = "^\(.*\)"
	for x in re.split(ptnAll, repr(var)):
		l = re.findall(ptnSub, x)
		if len(l):
			print stripResult(l[0])
			


def test5():
	class Options:
		keywords = []
		docstrings = 0
		nodocstrings = {}

	options = Options()

	fpbase = open('tt')

	options.keywords.extend(default_keywords)
	options.toexclude = []

	eater = parser.TokenEater(options)
	parser.tokenize.tokenize(fpbase.readline, eater)
	eater.exchange()


def test6():
	var = '"11,1","2,22",,,"333","4,44"'
	ret = re.findall('"([^"]*)"', var)
	ret2= re.split('",', var )
	print ret2, len(ret2)
	

if __name__ == "__main__":

	nameSelf = os.path.basename(sys.argv[0])
	gNoParseList[nameSelf] = nameSelf
	cmd = sys.argv[1:]

	if len(cmd) > 0 :
		if cmd[0] == 'csv' :
			Make_NewCSV( )
			print 'create new csv : test.csv'
	else :
		AutoMakeLanguage( )


