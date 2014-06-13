from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import pvr.DataCacheMgr
import pvr.ElisMgr
import pvr.NetConfig as NetConfig
import sys
import urllib2 as urllib
from urllib import urlencode
from os import curdir, sep
import xbmcaddon
import dbopen
import threading
from pvr.IpParser import IpParser
import HTMLProcess
import time

def getMyIp() :
	# getting NETWORK informations
	network = IpParser()
	networkInfo = network.GetNetworkAddress(network.GetCurrentServiceType())
		
	# return addressIp, addressMask, addressGateway, addressNameServer
	# IP Address of the set is now networkInfo[0] 
	return networkInfo[0]

class Webinterface( object ) :
	def __init__(self, urlPath=None) :

		#sys.setdefaultencoding('utf8')

		self.mDataCache = pvr.DataCacheMgr.GetInstance( )
		self.mCommander = pvr.ElisMgr.GetInstance().GetCommander()

		self.params = {}

		if urlPath != None :
			eParam = urlPath.split('?')
			if len(eParam) > 1 :
				ePair = eParam[1].split('&')
				for eVal in ePair :
					fVal = eVal.split('=')
					if len(fVal) > 1 :
						self.params[fVal[0]] = urllib.unquote(fVal[1])

	def Epgevent_GetNext( self, aSid, aTsid, aOnid ) :
	
		eventList = self.mCommander.Epgevent_GetList( aSid, aTsid, aOnid, 0, 0, 2 )
		try :
			if eventList :
				eventList = eventList[1]

			return eventList
			
		except :
			return False
		
	def makeRef( self, sid, tsid, onid, *number ) :
		ref = []

		ref.append( '1' )								# type			0
		ref.append( '0' ) 								# flag			1
		ref.append( '1' ) 								# service type		2
		ref.append( hex(sid)[2:] )						# sid in hexa		3
		ref.append( hex(tsid)[2:] )						# tsid in hexa		4
		ref.append( str(onid) )							# onid			5
		ref.append( 'C00000' )							# namespace		6
		ref.append( '0' )								# psid			7
		ref.append( '0' )								# ptsid			8
		if number :
			ref.append( str(number[0]) )				# use this as channel number 
		else :
			ref.append( '0' ) 							#?				9
		ref.append('')									#?				10
		
		return ':'.join(ref)

	def makeRefServiceType( self, serviceType, sid, tsid, onid, *number ) :
		ref = []

		ref.append( str(serviceType) )								# type			0
		ref.append( '0' ) 								# flag			1
		ref.append( '1' ) 						# service type		2
		ref.append( hex(sid)[2:] )						# sid in hexa		3
		ref.append( hex(tsid)[2:] )						# tsid in hexa		4
		ref.append( str(onid) )							# onid			5
		ref.append( 'C00000' )							# namespace		6
		ref.append( '0' )								# psid			7
		ref.append( '0' )								# ptsid			8
		if number :
			ref.append( str(number[0]) )				# use this as channel number 
		else :
			ref.append( '0' ) 							#?				9
		ref.append('')									#?				10
		
		return ':'.join(ref)

	def unMakeRef( self, ref ) :
		unRef = {}
		source = urllib.unquote(ref).split(':')

		# print 'unMakeRef '

		try:
			unRef['type'] = source[0]				#0
			unRef['flag'] = source[1]				#1
			unRef['servicetype'] = source[2]			#2
			unRef['sid'] = int( source[3], 16 )			#3
			unRef['tsid'] = int( source[4], 16 )		#4	
			unRef['onid'] = int( source[5] )			#5
			unRef['namespace'] = source[6]			#6
			unRef['psid'] = source[7]				#7
			unRef['ptsid'] = source[8]				#8
			unRef['number'] = source[9]				#9
			if len(source) > 10 :
				unRef['comment'] = source[10]			#10
			else :
				unRef['comment'] = ''
				
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
		
	def address_string(self) :
		host, port = self.client_address[:2]
		return host

	def do_HEAD( self ) :
	
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

		print '[HEAD]'
		print self.path

	def do_GET(self):
		try :
			self.urlPath = self.path.split('?')
		
			print 'request path '
			print self.path

			self.__addon__ = xbmcaddon.Addon( id='script.mbox' )
			self.fullPath = self.__addon__.getAddonInfo( 'path' )
			
		except Exception, err :
			print '[GET]'
			print str(err)

		self.serving()

	def do_POST(self):
		self.urlPath = self.path.split('?')
		
		print 'request path '
		print self.path

		self.__addon__ = xbmcaddon.Addon( id='script.mbox' )
		self.fullPath = self.__addon__.getAddonInfo( 'path' )

		print 'Do Post full path is '
		print self.fullPath

		self.serving()

	def serving( self ) :

		try:
			if self.urlPath[0] == '/stream/stream.m3u' :

				self.send_response(200)
				# self.send_header( 'Content-type', 'application/force-download' )
				self.send_header( 'Content-type', 'audio/x-mpegrul' )
				self.send_header( 'Content-Disposition', 'attachment; filename="stream.m3u"' )
				self.end_headers()

				print '[WebUI] About to download Stream.m3u file for live stream'

				print HTMLProcess.GetStream(getMyIp())
				self.wfile.write( HTMLProcess.GetStream(getMyIp()) )

				return

			if self.urlPath[0] == '/recording/stream.m3u' :

				self.send_response(200)
				self.send_header( 'Content-type', 'audio/x-mpegrul' )
				self.send_header( 'Content-Disposition', 'attachment; filename="stream.m3u"' )
				self.end_headers()

				print '[WebUI] About to download Stream.m3u file for Recordings'

				conn = dbopen.DbOpen('recordinfo.db').getConnection()

				sql = "select MountInfo from tblRecordInfo where RecordKey=" + self.urlPath[1]
				c = conn.cursor()
				c.execute(sql)

				mountInfo = c.fetchone()[0]
				print mountInfo

				# VLC Option added 
				

				if mountInfo == 'Internal' :
					content = "http://" + getMyIp().strip() + ":49152/content/internal-recordings/%s/0.ts" % self.urlPath[1]
				else :
					content = "http://" + getMyIp().strip() + ":49152/content%s/%s/0.ts" % (mountInfo, self.urlPath[1])
					
				self.wfile.write( content )

				return
				
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
				elif self.urlPath[0] == '/web/getallservicestv' :
					from getallservicestv import ElmoGetAllServicesTV as Content
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
				elif self.urlPath[0] == '/web/remotecontrol' :
					from remotecontrol import ElmoRemoteControl as Content
				elif self.urlPath[0] == '/web/powerstate' : 
					from powerstatus import ElmoPowerStatus as Content 
				elif self.urlPath[0] == '/web/timerlist' :
					from timerlist import ElmoTimerList as Content 
				elif self.urlPath[0] == '/web/timeraddbyeventid' :
					from timeraddbyeventid import ElmoTimerAddByEventId as Content 
				elif self.urlPath[0] == '/web/prismcubeversion' :
					from prismcubeversion import PrismCubeVersion as Content 

				############# Live TV ####################################
				
				elif self.urlPath[0] == "/web/stream.m3u" :

					"""
					self.send_response(200)
					self.send_header( 'Content-type', 'application/force-download' )
					self.send_header( 'Content-Disposition', 'attachment; filename="stream.m3u"' )
					self.end_headers()

					print HTMLProcess.GetStream(getMyIp())
					
					self.wfile.write( HTMLProcess.GetStream(getMyIp()) )

					return
					"""

					self.send_response(200)
					self.send_header( 'Content-type', 'application/force-download' )
					self.send_header( 'Content-Disposition', 'attachment; filename="stream.m3u"' )
					self.end_headers()

					print '[WebUI] About to download Stream.m3u file for /web/stream.m3u'

					myip = getMyIp()

					# creating file content, here the value of target is content of Stream.m3u
					target = "http://" + myip.strip() + ":8001/"
					print target
					
					self.wfile.write( target )
					return
					
				############# Record Play - Movie ############################

				elif self.urlPath[0] == "/file" :

					paramName = self.urlPath[1].split("=")[0]
					paramVal = self.urlPath[1].split("=")[1]

					if paramName == 'file' :
					
						print 'Record Play'

						# recordKey = self.urlPath[1].split("=")[1]
						recordKey = paramVal
						
						myip = getMyIp()

						conn = dbopen.DbOpen('recordinfo.db').getConnection()
						c = conn.cursor()

						sql = "select MountInfo from tblRecordInfo where RecordKey=" + recordKey
						print sql
						
						c = conn.cursor()
						c.execute(sql)

						mountInfo = c.fetchone()[0]

						# VLC optin 2014. 6. 11
						# target = '#EXTM3U\n'
						# target += '#EXTVLCOPT--http-reconnect=true\n'
						
						if mountInfo == 'Internal' :
							target = "http://" + getMyIp().strip() + ":49152/content/internal-recordings/%s/0.ts" % recordKey
						else :
							target = "http://" + getMyIp().strip() + ":49152/content%s/%s/0.ts" % (mountInfo, recordKey)
						# target = "http://" + myip.strip() + ":49152/content/internal-recordings/" + recordKey + "/0.ts"

						print '[Stream Handler] Recording File Read '
						print target

						self.streamResult = urllib.urlopen(target)

						i = 0 
						j = 0

						print '[Stream Handler] Ready to stream recorded file'

					else :

						print 'Media File Play'

						#filePath = urllib.unquote(paramVal)
						filePath = paramVal
						
						print filePath

						try :
							self.streamResult = file(filePath, 'rb')
							print paramVal
							print '[Media File] Streming from Media file'
						except :
							print '[Media File] File Open Error'
							return 

					self.send_response( 200 )
					self.send_header( 'Content-Type', 'application/text' )
					self.end_headers()
					
					while True :
						"""
						j = j + 1
						if j == 2000 :
							j = 0 
							print '[WEBUI] I am looping'
						"""
						try :
							s = self.streamResult.read( 1024 * 1000 * 5 )
							# print len(s)

							if len(s) == 0 :
								print 'len is 0 .. breaking .. '
								break
							else :
								# self.wfile.write( self.result.read(1024)  )
								self.wfile.write( s )
								#time.sleep(0.001)
														
						except IOError :

							print 'io error'
							#return
							break
							
						except Exception, err:
						
							print 'breaking..........................'
							print str(err)
							# return
							break
					
					return
					
				#######################################################

				else :

					if self.urlPath[0] == '/favicon.ico' :
						return 
						
					########### Web UI Begins #######################################
					
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()

					if self.urlPath[0] == '/' :
						fileName = 'uiIndex.html'
					else :
						fileName = self.urlPath[0][1:]

					print '[WEBUI:fileName]' + fileName
					
					if len(self.urlPath) > 1 :
						print '[WEBUI:self.urlPath[1]]' + self.urlPath[1]
						self.uiContent = HTMLProcess.GetHTMLClass( fileName, self.urlPath[1] )
					else :
						self.uiContent = HTMLProcess.GetHTMLClass( fileName )
						
					self.wfile.write( self.uiContent.GetContent() )
					
					return
					
					########### Web UI Ends ########################################
			
				webContent = Content(self.path)
				# print self.path
				try :
					self.send_response(200)
				except :
					pass

				# self.send_header('Content-type', 'text/html')
				self.send_header('Content-type', 'text/xml')
				self.end_headers()
				
				# webContent.xmlResult()
				# print webContent.xmlResult()

				result = webContent.xmlResult()
				self.wfile.write( result )

			return

		except IOError, er:
		
			print str(er)
			self.send_error(404, 'File not found')

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

class MyStreamHandler( BaseHTTPRequestHandler ) :

	def address_string(self) :
		host, port = self.client_address[:2]
		return host

	def do_GET( self ) :

		print '[Stream Handler] path is ' + self.path
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

			print '[Stream Hander on 8001] webserver ==> read'
			print self.target
			
			print '[Stream Handler on 8001] webserver ==> Live Stream about to read'
			self.streamResult = urllib.urlopen(self.target, timeout=10.0)
			print self.target

			i = 0 
			j = 0

			# throw away unready streams at first
			#for i in range(1000) :
			#	s = self.streamResult.read( 1024 )

			print '[Stream Handler] Ready to stream'
			
			while True :

				try :
					s = self.streamResult.read( 1024 * 1000 * 5 )
					#for i in range(5) :
					#	s += self.streamResult.read(1024 * 100)
					
					if len(s) == 0 :
						print '[Stream Handler on 8001] Packet lenght is 0'
						break
						
					else :
						# print '[Stream Handler on 8001] Writing Stream size of ' + str(len(s)) 
						self.wfile.write( s )
						# time.sleep(0.001) 
												
				except IOError :

					print 'io error'
					self.streamResult.close()
					#return
					break
					
				except Exception, err:
				
					print 'breaking..........................'
					print str(err)
					# return
					break

		except Exception, err :
		
			self.send_response( 404 )
			self.end_headers()

			print '[webserver]'
			print str(err)

			self.streamResult.close()

	def do_POST( self ) :
	
		print '==> POST Request'
		print self.path
		print 
		

	def sRef( self ) :

		source = self.path.split(':')

		try:
			self.unRef['type'] = source[0]				#1
			self.unRef['flag'] = source[1]					#2
			self.unRef['servicetype'] = source[2]			#3
			self.unRef['sid'] = int( source[3], 16 )			#4
			self.unRef['tsid'] = int( source[4], 16 )			#5	
			self.unRef['onid'] = int( source[5] )			#6
			self.unRef['namespace'] = source[6]			#7
			self.unRef['psid'] = source[7]				#8
			self.unRef['ptsid'] = source[8]				#9
			self.unRef['unknown'] = source[9]			#10
			self.unRef['comment'] = source[10]			#11
			
		except :
			pass 

def index():

	#connect to find.prismcube.com server to pass the self-information
	try :
		data = {'ip' : str(getMyIp()) }
		data = urlencode( data )
		f = urllib.urlopen("http://www.fwupdater.com/prismcube/index.html", data, 3)
		
	except Exception, err:
		print '[Find]'
		print str(err)

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
		print 'stream server dead'
		streamServer.socket.close()
		
"""
class classIndex(threading.Thread):
	def __init__(self) :
		try :
			server = HTTPServer( ('', 1313), MyHandler )
			server.serve_forever()

		except :
			server.socket.close()
	
class classStreamIndex(threading.Thread) :
	def __init__(self) :
		try :
			streamServer = HTTPServer( ('', 8001), MyStreamHandler )
			streamServer.serve_forever()
		
		except :
	
			streamServer.socket.close()
"""


