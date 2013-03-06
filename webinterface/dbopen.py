try:
	from sqlite3 import dbapi2 as sqlite3
except:
	from pysqlite2 import dbapi2 as sqlite3

import xbmcaddon

class DbOpen( object ) :

	def __init__(self, dbname) :
		'''
		self.__addon__ = xbmcaddon.Addon(id='script.mbox')
		self.path = self.__addon__.getAddonInfo('path')

		self.conn = sqlite3.connect(self.path + '\\webinterface\\' + dbname)
		'''
		self.conn = sqlite3.connect('/mtmp/' + dbname)		
		# print (self.path + '\\webinterface\\' + dbname)

	def getConnection(self) :
		return self.conn
