#-*- coding: utf-8 -*-

#from sys import setdefaultencoding
#setdefaultencoding('utf-8')

import os, re

import sgmllib, string   
  
class Stripper(sgmllib.SGMLParser):   
	def __init__(self):   
		self.data = []   
		sgmllib.SGMLParser.__init__(self)   
	def unknown_starttag(self, tag, attrib):   
		self.data.append(" ")   
	def unknown_endtag(self, tag):   
		self.data.append(" ")   
	def handle_data(self, data):   
		self.data.append(data)   
	def gettext(self):   
		text = string.join(self.data, "")   
		return string.join(string.split(text))


def StripTag(text):   
	s = Stripper()   
	s.feed(text)   
	s.close()   
	return s.gettext()

def decodeXML(data): 
	RE_XML_ENCODING = re.compile("encoding[ \t]*=[ \t]*\"([^\"]+)\"") 
	len_ = len(data)
	head = data[:len_]
	headline = head.splitlines()[0]
	mo = RE_XML_ENCODING.search(headline) 
	if mo: 
		encoding = mo.group(1) 
		return data[len(headline):].decode(encoding) 
	else: 
		return data 




def initFile():
	#openFile = os.getcwd() + '/Language_Prime.csv'
	openFile = os.getcwd() + '/Language091102.csv'
	wFile1 = 'define_string.py'

	langPack = ["ENGLISH","DEUTSCH","FRENCH","ITALIAN","SPANISH","CZECH","DUTCH","POLISH","TURKISH","RUSSIAN"]
	tag1 = '<string id=\"%s\">'
	tag2 = '</string>'

	rf = open(openFile, 'r')
	df = open(wFile1, 'w')

	"""
	#line = '"Remove, Lock, Set Group, etc.","déplacer, verouiller, grouper, etc.","236",,'
	line ='"English","French","STRING_INDEX",,"Remark", "1é3"'
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
				wFileList.append(ret[i])
				wFile = '%s_strings.xml'% ret[i].lower()
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
				#print strid
				str = '\t' + (tag1 % strid) + ret[i] + tag2 +'\n'
				wf[i].writelines(str)

			except Exception, e:
				#print 'error string.xml', e
				pass

		#write define_string.py in English Name
		try:
			strid = re.sub(',', '', ret2[len(ret2)-1])

			strll = ret[0].upper()
			strll = re.split(' ', strll, 5)
			var_=''
			for i in range(len(strll)):
				var_ += '_' + strll[i]

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

if __name__ == "__main__":
    initFile()