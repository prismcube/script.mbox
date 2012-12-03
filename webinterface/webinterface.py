from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import pvr.DataCacheMgr
import pvr.ElisMgr
import pvr.NetConfig as NetConfig
import sys
import urllib
from os import curdir, sep
import xbmcaddon
import dbopen

class Webinterface( object ) :
	def __init__(self, urlPath) :

		#sys.setdefaultencoding('utf8')

		self.mDataCache = pvr.DataCacheMgr.GetInstance( )
		self.mCommander = pvr.ElisMgr.GetInstance().GetCommander()

		self.params = {}

		eParam = urlPath.split('?')
		if len(eParam) > 1 :
			ePair = eParam[1].split('&')
			for eVal in ePair :
				fVal = eVal.split('=')
				if len(fVal) > 1 :
					self.params[fVal[0]] = urllib.unquote(fVal[1])
		
		
	def makeRef( self, sid, tsid, onid ) :
		ref = []

		ref.append( '1' )							# type
		ref.append( '0' ) 								# flag
		ref.append( '1' ) 								# service type
		ref.append( hex(sid)[2:] )						# sid in hexa
		ref.append( hex(tsid)[2:] )				# tsid in hexa
		ref.append( str(onid) )							# onid
		ref.append( 'C00000' )						# namespace
		ref.append( '0' )								# psid
		ref.append( '0' )								# ptsid
		ref.append( '0' ) 	
		ref.append('')
		
		return ':'.join(ref)

	def unMakeRef( self, ref ) :
		unRef = {}
		source = urllib.unquote(ref).split(':')

		print 'unMakeRef '

		try:
			print source[3]
	
			unRef['type'] = source[0]				#1
			unRef['flag'] = source[1]				#2
			unRef['servicetype'] = source[2]			#3
			unRef['sid'] = int( source[3], 16 )			#4
			unRef['tsid'] = int( source[4], 16 )		#5	
			unRef['onid'] = int( source[5] )			#6
			unRef['namespace'] = source[6]			#7
			unRef['psid'] = source[7]				#8
			unRef['ptsid'] = source[8]				#9
			unRef['unknown'] = source[9]
			unRef['comment'] = source[10]
		except :
			return False
		else :
			return unRef

	def is_number( self, s ) :
		try :
			float( s )
			return True
		except ValueError :
			return False
		
class MyHandler( BaseHTTPRequestHandler ):
		
	def do_GET(self):
		self.urlPath = self.path.split('?')
		
		print 'request path '
		print self.path

		self.__addon__ = xbmcaddon.Addon( id='script.mbox' )
		self.fullPath = self.__addon__.getAddonInfo( 'path' )

		print 'full path is '
		print self.fullPath

		self.serving()

	def do_POST(self):
		self.urlPath = self.path.split('?')
		
		print 'request path '
		print self.path

		self.__addon__ = xbmcaddon.Addon( id='script.mbox' )
		self.fullPath = self.__addon__.getAddonInfo( 'path' )

		print 'full path is '
		print self.fullPath

		self.serving()

	def serving( self ) :

		try:
			if self.path.endswith('.m3u') :

				fileName = ( self.path.split('/') )[2]
				f = open( self.fullPath + sep + fileName, 'rb' )

				self.send_response( 200 )
				self.send_header( 'Content-type',		'application/m3u' )
				self.end_headers()
				self.wfile.write( f.read() )
				f.close()
				
			else :

				if self.urlPath[0] == '/web' or self.urlPath[0] == '/web/about' :
					from about import ElmoAbout as Content
				elif self.urlPath[0] == '/web/currenttime' :
					from currenttime import ElmoCurrentTime as Content
				elif self.urlPath[0] == '/web/getcurrent' :
					from getcurrent import ElmoGetCurrent as Content
				elif self.urlPath[0] == '/web/epgnow' :
					from epgnow import ElmoEpgNow as Content
				elif self.urlPath[0] == '/web/epgnext' :
					from epgnext import ElmoEpgNext as Content
				elif self.urlPath[0] == '/web/epgservice' :
					from epgservice import ElmoEpgService as Content
				elif self.urlPath[0] == '/web/epgservicenow' :
					from epgservicenow import ElmoEpgServiceNow as Content
				elif self.urlPath[0] == '/web/epgservicenext' :
					from epgservicenext import ElmoEpgServiceNext as Content
				elif self.urlPath[0] == '/web/epgbouquet' :
					from epgbouquet import ElmoEpgBouquet as Content
				elif self.urlPath[0] == '/web/getallservices' :
					from getallservices import ElmoGetAllServices as Content
				elif self.urlPath[0] == '/web/getservices' :
					from getservices import ElmoGetServices as Content
				elif self.urlPath[0] == '/web/serviceplayable' :
					from serviceplayable import ElmoServicePlayable as Content
				elif self.urlPath[0] == '/web/zap' :
					from zap import ElmoZap as Content
				elif self.urlPath[0] == '/web/deviceinfo' or self.urlPath[0] == '/api/deviceinfo' :
					from deviceinfo import ElmoDeviceInfo as Content
				elif self.urlPath[0] == '/web/getlocations' :
					from getlocations import ElmoGetLocations as Content
				elif self.urlPath[0] == '/web/movielist' :
					from movielist import ElmoMovieList as Content
				else :
					self.send_response(200)
					self.send_header('Content-type',		'text/html')
					self.end_headers()
					return
				

				"""
				if self.urlPath[0] == '/api/deviceinfo' :
					from deviceinfoNew import PrismCubeDeviceInfo as Content
				elif self.urlPath[0] == '/api/getservices' :
					from getservicesNew import PrismCubeGetServices as Content
				elif self.urlPath[0] == '/api/epgnow' :
					from epgnowNew import PrismCubeEpgNow as Content
				elif self.urlPath[0] == '/api/zap' :
					from zapNew import PrismCubeZap as Content
				elif self.urlPath[0] == '/api/servicesm3u' :
					from servicesm3uNew import PrismCubeServicesm3u as Content
				elif self.urlPath[0] == '/api/getcurrent' :
					from getcurrentNew import PrismCubeGetCurrent as Content
				"""
				
				webContent = Content(self.path)
				
				self.send_response(200)
				self.send_header('Content-type',		'text/html')
				self.end_headers()

				# webContent.xmlResult()
				# print webContent.xmlResult()

				result = webContent.xmlResult()
				self.wfile.write( result )

			return

		except IOError:
			self.send_error(404, 'File not found')

class MyStreamHandler( BaseHTTPRequestHandler ) :

	
	def do_GET( self ) :

		print '==>' + self.path
		self.unRef = {}
		self.sRef()

		try :
			conn = dbopen.DbOpen('channel.db').getConnection()
			c = conn.cursor()

			sql = 'select Number from tblChannel where sid=' + str( self.unRef['sid'] ) + ' and tsid=' + str( self.unRef['tsid'] ) + ' and onid=' + str( self.unRef['onid'] )
			print sql
			c.execute(sql)

			result = c.fetchone()

			self.target = "http://" + NetConfig.targetIp +":49152/content/live-streaming/liveStream-http-" + str(result[0]) + "-1.ts"
			print self.target
		
			self.send_response( 200 )
			self.send_header( 'Content-Type', 'application/text' )
			self.end_headers()

			print 'webserver ==> read'
			self.result = urllib.urlopen(self.target)
			print 'webserver ==> about to read'

			i = 0 
			j = 0 
			while True :
				s = self.result.read( 1024 )
				if len(s) == 0 :
					break
				else :
					# self.wfile.write( self.result.read(1024)  )
					self.wfile.write( s )

		except Exception, err :
		
			self.send_response( 404 )
			self.end_headers()

			print '[webserver]'
			print str(err)

	def do_POST( self ) :
		print '==> POST Request'
		print self.path
		print 
		

	def sRef( self ) :

		source = self.path.split(':')

		try:
			self.unRef['type'] = source[0]				#1
			self.unRef['flag'] = source[1]				#2
			self.unRef['servicetype'] = source[2]			#3
			self.unRef['sid'] = int( source[3], 16 )			#4
			self.unRef['tsid'] = int( source[4], 16 )		#5	
			self.unRef['onid'] = int( source[5] )			#6
			self.unRef['namespace'] = source[6]			#7
			self.unRef['psid'] = source[7]				#8
			self.unRef['ptsid'] = source[8]				#9
			self.unRef['unknown'] = source[9]
			self.unRef['comment'] = source[10]
			
		except :

			print 

def index():
	try :
		server = HTTPServer( ('', 1313), MyHandler )
		server.serve_forever()

	except :
		server.socket.close()

def streamIndex() :
	try :
		streamServer = HTTPServer( ('', 8001), MyStreamHandler )
		streamServer.serve_forever()
		
	except :

		streamServer.socket.close()


	
