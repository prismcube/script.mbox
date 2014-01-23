import pvr.DataCacheMgr
import pvr.ElisMgr
from pvr.gui.WindowImport import *
import xbmc
from urllib import unquote

def GetHTMLClass( className, *param ) :

	# enlist every file to be processed by program 
	htmlClass = [RemoteControl, Channel, ChannelBySatellite, ChannelByCas, ChannelByFavorite, Zapping, Epg]

	for cls in htmlClass :
		if className == cls.__name__ :
			return cls( param ) 

	return SimpleHTMLFile( className ) 

def GetStream(targetIP) :

	stream = WebPage()
	currentStream = stream.mDataCache.Channel_GetCurrent()

	stream.content = "http://" + targetIP.strip() + ":49152/content/live-streaming/liveStream-http-" + str(currentStream.mNumber) + "-1.ts"
	# self.target = "http://" + NetConfig.targetIp.strip() +":49152/content/live-streaming/liveStream-http-" + str(result[0]) + "-1.ts"

	return stream.GetContent()

class SimpleHTMLFile :

	def __init__(self, fileName) :
		try :
			self.uiPath = '/usr/share/xbmc/addons/script.mbox/webinterface/'

			f = open(self.uiPath + fileName, "r")
			self.content = f.read()
			f.close()
			
		except :
			self.content = "File Not Found"

	def GetContent(self) :
		return self.content

class WebPage( object ) :
	def __init__( self ) :

		self.mDataCache = pvr.DataCacheMgr.GetInstance( )
		self.mCommander = pvr.ElisMgr.GetInstance().GetCommander()
		
		self.mZappingMode = self.mDataCache.Zappingmode_GetCurrent()

		self.content = "No Action Done"

	def GetContent( self ) :

		return self.content

	def ResetChannelListOnChannelWindow( self, channelList, mMode ) :

		self.currentZappingMode = self.mDataCache.Zappingmode_GetCurrent()
		self.currentZappingMode.mMode = mMode
		ret = self.mDataCache.Zappingmode_SetCurrent( self.currentZappingMode ) 

		if ret :
			self.mDataCache.LoadZappingmode( )
			self.mDataCache.LoadZappingList( )
			#self.mDataCache.LoadChannelList( )
			self.mDataCache.RefreshCacheByChannelList( channelList )
			self.mDataCache.SetChannelReloadStatus( True )
				
class Channel( WebPage ) :

	def __init__( self, command ) :

		super(Channel, self).__init__()

		if command[0] == 'all' :
			self.content = self.allChannelContent()
		elif command[0] == 'satellite' :
			self.content = self.satelliteChannelContent()
		elif command[0] == 'cas' :
			self.content = self.casChannelContent()
		elif command[0] == 'favorite' :
			self.content = self.favoriteChannelContent()
		elif command[0] == 'mode' :
			self.content = self.modeContent()
		else :
			pass  # do nothing 
		

	def allChannelContent( self ) :

		# def Channel_GetList( self, aTemporaryReload = 0, aType = 0, aMode = 0, aSort = 0 ) 
		self.allChannel = self.mDataCache.Channel_GetList( aTemporaryReload=1, aType= self.mZappingMode.mServiceType, aMode=ElisEnum.E_MODE_ALL)
		content = '<table border="0" cellpadding="5">'

		for cls in self.allChannel : 
			content += '<tr><td width="100">' + str(cls.mNumber) + '</td>'
			content += '<td width="300">' + cls.mName + '</a></td>'
			content += '<td class="epg">[<a href="Zapping?' + str(cls.mNumber) +'" target="zapper">Zap</a>]</td>'
			content += '<td class="epg">[<a href="javascript:JumpToEpg(' + str(cls.mSid) + ',' + str(cls.mTsid) + ',' + str(cls.mOnid) + ')">EPG</a>]</td>'
			# content += '<td class="epg">[<a href="/epg?sid='+ str(cls.mSid) + '&tsid=' + str(cls.mTsid) + '&onid=' + str(cls.mOnid) + '">EPG</a>]</td>'
			content += '</tr>'
		content += '</table>'

		self.ResetChannelListOnChannelWindow( self.allChannel, ElisEnum.E_MODE_ALL ) 
	
		return self.getChannelContent(content)

	def satelliteChannelContent( self ) :

		self.satelliteList = self.mDataCache.Satellite_GetConfiguredList()
		content = '<table border="0" cellpadding="5">'

		for cls in self.satelliteList : 
			content += '<tr><td width="100">' + str(cls.mLongitude) + '</td><td width="200">'
			content += '<a href="ChannelBySatellite?' + str(cls.mName) + '">' + str(cls.mName) +'</a></td></tr>'
		content += '</table>'

		return self.getChannelContent(content)

	def casChannelContent( self ) :

		return self.getChannelContent('FTA-CAS') 

	def favoriteChannelContent( self ) :

		self.allChannel = self.mDataCache.Favorite_GetList(0, self.mZappingMode.mServiceType)
		content = '<table border="0" cellpadding="5">'

		for cls in self.allChannel : 
			content += '<tr><td width="300"><a href="ChannelByFavorite?' + cls.mGroupName + '">' + cls.mGroupName + '</a></td></tr>'

		content += '</table>'

		return self.getChannelContent( content )

	def modeContent( self ) :

		if self.mZappingMode.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
			content = "TV MODE"
		elif self.mZappingMode.mServiceType == ElisEnum.E_TYPE_RADIO :
			content = "RADIO MODE"
		else :
			content = "Unkown"

		return self.getChannelContent( content )

	def getChannelContent( self, content ) :

		self.channelContent  = """

			<html>
			<head>
				<title>PrismCube Web UI</title>
				<link href='uiStyle.css' type='text/css' rel='stylesheet'>
				<script>
					function JumpToEpg( sid, tsid, onid ) {
						var target = '/Epg?sid=' + sid + '&tsid=' + tsid + '&onid=' + onid;		
						window.open( target, 'epg', 'width=500, height=500');
					}
				</script>
			<body>
			<div id='wrapper'>

				<div id='top'>
					<p>PrismCube Web UI</p>
				</div>
				<div id='menu'>
					<p>
						>> Channel</a> 	<br>
						<a href='/stream/stream.m3u'>Stream</a> 		<br>
						<a href='uiRemote.html'>Remote Control</a> <br>
					</p>
				</div>
				<div id='main'>
				
					<p class='title'>
						Welcome to PrismCube Web UI
					</p>
					
					<p>
						<ul class='submenu'>
							<li><a href='Channel?all'>All Channels</a></li>
							<li><a href='Channel?satellite'>Satellite</a></li>
							<li><a href='uiChannelByCas.html'>FTA/CAS</a></li>
							<li><a href='Channel?favorite'>Favorite Groups</a></li>
							<li><a href='Channel?mode'>Mode</a></li>
						</ul>
					</p>
				</div>

				<div id='content'>
					%s
					<iframe name='zapper' width='0' height='0' style='display: none;'></iframe>
				</div>

			</div>

			</body>
			</html>
			
		""" % content
		return self.channelContent

class RemoteControl(WebPage):

	def __init__( self, command ) :

		super(RemoteControl, self).__init__()

		print '[WEBUI]'
		print command

		cmds = command[0].split("=")

		if cmds[1] == "114" :
			self.VolumeControl("down")
			self.content = "Volume Up"
		if cmds[1] == "115" :
			self.VolumeControl("up")
			self.content = "Volume Down"

		if int(cmds[1]) in [103, 108, 105, 106, 352, 174] :
			self.ArrowControl( cmds[1] )
			self.content = "Arrow Control"

		if int(cmds[1]) in [402, 403] :
			self.ChannelControl( cmds[1] ) 
			self.content = "Channel Control"

	def ChannelControl( self, control ) :
		status = self.mDataCache.Player_GetStatus( )
		if status.mMode == ElisEnum.E_MODE_PVR :
			return self.content

		if control == "402" :
		
			prevChannel = None
			prevChannel = self.mDataCache.Channel_GetPrev( self.mDataCache.Channel_GetCurrent( ) ) #self.mCommander.Channel_GetPrev( )
			if prevChannel :
				self.mDataCache.Channel_SetCurrent( prevChannel.mNumber, prevChannel.mServiceType, None, True )			
				self.mDataCache.SetAVBlankByChannel( prevChannel )
	
		if control == "403" :
			
			nextChannel = None
			nextChannel = self.mDataCache.Channel_GetNext( self.mDataCache.Channel_GetCurrent( ) )
			if nextChannel :
				self.mDataCache.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType, None, True )
				self.mDataCache.SetAVBlankByChannel( nextChannel )
	
	def VolumeControl( self, control ) :

		currentVol = self.mCommander.Player_GetVolume()

		if control == 'up' : 
			setVolume = currentVol + 1
		elif control == 'down' :
			setVolume = currentVol - 1
		
		self.mCommander.Player_SetVolume(setVolume)
		pvr.XBMCInterface.XBMC_SetVolume(setVolume)

	def ArrowControl( self, control ) :

		if control == '103' : # up key 
			methodName = "Input.Up"
		elif control == '108' : # down key
			methodName = "Input.Down"
		elif control == '105' : # left key
			methodName = "Input.Left"
		elif control == '106' : # right key
			methodName = "Input.Right"
		elif control == '352' : # select key
			methodName = "Input.Select"
		elif control == '174' : # select key
			methodName = "Input.Back"
			
		else 	:
			return self.content

		jsonStr = '{"jsonrpc": "2.0", "method": "%s", "id": 1}' % methodName
		xbmc.executeJSONRPC( jsonStr )

class ChannelBySatellite( Channel ) :

	def __init__( self, command ) :

		super(ChannelBySatellite, self).__init__(command)
		self.content = self.channelBySatelliteContent( command )

		self.longitude = 0
		self.band = 0

	def channelBySatelliteContent( self, command ) :

		satelliteList = self.mDataCache.Satellite_GetConfiguredList()
		satelliteName = unquote( command[0] )   # decoding url encoded string 

		# search for selected satellite information
		for cls in satelliteList :
			if cls.mName == satelliteName :
				self.longitude = cls.mLongitude
				self.band = cls.mBand

		channelList = self.mDataCache.Channel_GetListBySatellite( self.mZappingMode.mServiceType, ElisEnum.E_MODE_SATELLITE, self.mZappingMode.mSortingMode, str(self.longitude), str(self.band ) )
		content = '<table border="0" cellpadding="5">'
		indexer = 0

		satEnd = False
		chEnd = False
		
		while True :

			try : 
				content += '<tr><td width="100">' + str(satelliteList[indexer].mLongitude) + '</td>'
				if satelliteList[indexer].mName == satelliteName :
					content += '<td width="200" bgcolor="#dfdfdf">' + str(satelliteList[indexer].mName) + '</td>'
				else :
					content += '<td width="200"><a href="ChannelBySatellite?' + str(satelliteList[indexer].mName) + '">' + str(satelliteList[indexer].mName) + '</a></td>'
			except IndexError :
				content += '<tr><td>&nbsp;</td><td>&nbsp;</td>'
				satEnd = True
		
			try :
				content += '<td>' + str( channelList[indexer].mNumber ) + '</td>'
				content += '<td>' + channelList[indexer].mName + '</td>'
				content += '<td class="epg">[<a href="Zapping?' + str(channelList[indexer].mNumber) + '" target="zapper">Zap</a>]</td>'
				content += '<td class="epg">[<a href="javascript:JumpToEpg(' + str(channelList[indexer].mSid) + ',' + str(channelList[indexer].mTsid) + ',' + str(channelList[indexer].mOnid) + ')">EPG</a>]</td></tr>'
				
			except IndexError :
				content += '<td>&nbsp;</td><td>&nbsp;</td>'
				content += '<td>&nbsp;</td><td>&nbsp;</td></tr>'
				chEnd = True
			except TypeError :
				content += '<td>&nbsp;</td><td>&nbsp;</td>'
				content += '<td>&nbsp;</td><td>&nbsp;</td></tr>'
				chEnd = True

			if satEnd and chEnd :
				break
				
			indexer += 1

		content += '</table>'

		self.ResetChannelListOnChannelWindow( channelList, ElisEnum.E_MODE_SATELLITE ) 

		return self.getChannelContent( content )

class ChannelByCas( Channel ) :

	def __init__( self, command ) :

		super(ChannelByCas, self).__init__(command)
		self.content = self.channelByCasContent(command) 

	def channelByCasContent( self, command ) :

		casList = ['FTA', 'MEDIAGUARD', 'VIACCESS', 'NAGRA', 'IRDETO', 'CONAX', 'CRYPTOWORKS', 'BETADIGITAL', 'NDS', 'DRECRYPT', 'VERIMATRIX', 'OTHERS']
		
		if command[0] == casList[0] :
			caid = ElisEnum.E_FTA_CHANNEL
		elif command[0] == casList[1] :
			caid = ElisEnum.E_MEDIAGUARD
		elif command[0] == casList[2] :
			caid = ElisEnum.E_VIACCESS
		elif command[0] == casList[3] :
			caid = ElisEnum.E_NAGRA
		elif command[0] == casList[4] :
			caid = ElisEnum.E_IRDETO
		elif command[0] == casList[5] :
			caid = ElisEnum.E_CONAX
		elif command[0] == casList[6] :
			caid = ElisEnum.E_CRYPTOWORKS
		elif command[0] == casList[7] :
			caid = ElisEnum.E_BETADIGITAL
		elif command[0] == casList[8] :
			caid = ElisEnum.E_NDS
		elif command[0] == casList[9] :
			caid = ElisEnum.E_DRECRYPT	
		elif command[0] == casList[10] :
			caid = ElisEnum.E_VERIMATRIX
		else :
			caid = ElisEnum.E_OTHERS

		print '[WEBUI:caid]' + str(caid)
		print command[0]
			
		channelList = self.mDataCache.Channel_GetListByFTACas( self.mZappingMode.mServiceType, ElisEnum.E_MODE_CAS, self.mZappingMode.mSortingMode, caid )
		content = '<table border="0" cellpadding="5">'
		indexer = 0

		casEnd = False
		chEnd = False
		
		while True :

			try :
				if casList[indexer] == command[0] :
					content += '<tr><td width="200" bgcolor="#dfdfdf">' + casList[indexer] + '</td>'
				else :
					content += '<tr><td width="200"><a href="ChannelByCas?' + casList[indexer] + '">' + casList[indexer] + '</a></td>'
			except IndexError :
				content += '<tr><td>&nbsp;</td>'
				casEnd = True

			try :
				content += "<td>" + str(channelList[indexer].mNumber) +"</td>"
				content += '<td width="200">' + channelList[indexer].mName +"</td>"
				content += '<td class="epg"><a href="Zapping?' + str(channelList[indexer].mNumber) + '" target="zapper">[Zap]</a></td>'
				content += '<td class="epg">[<a href="javascript:JumpToEpg(' + str(channelList[indexer].mSid) + ',' + str(channelList[indexer].mTsid) + ',' + str(channelList[indexer].mOnid) + ')">EPG</a>]</td>'
				content += "</tr>"
			except IndexError :
				content += "<td>&nbsp;</td>"
				content += "<td>&nbsp;</td>"
				content += "<td>&nbsp;</td>"
				content += "<td>&nbsp;</td>"
				content += "</tr>"
				chEnd = True

			if chEnd and casEnd : 
				break
			indexer += 1

		content += "</table>"

		self.ResetChannelListOnChannelWindow( channelList, ElisEnum.E_MODE_CAS ) 

		return self.getChannelContent( content )

class ChannelByFavorite( Channel ) :

	def __init__( self, command ) :

		super(ChannelByFavorite, self).__init__( command )
		self.content = self.channelByFavoriteContent(command) 

	def channelByFavoriteContent( self, command ) :

		favName = unquote( command[0] )   # decoding url encoded string 
		
		folderList = self.mDataCache.Favorite_GetList(0, self.mZappingMode.mServiceType)
		channelList = self.mDataCache.Channel_GetListByFavorite( self.mZappingMode.mServiceType, ElisEnum.E_MODE_FAVORITE, self.mZappingMode.mSortingMode, favName )
		
		content = '<table border="0" cellpadding="5">'
		indexer = 0

		favEnd = False
		chEnd = False
		
		while True :

			try :
				if folderList[indexer].mGroupName == favName :
					content += '<tr><td width="300" bgcolor="#dfdfdf">' + folderList[indexer].mGroupName + '</td>'
				else :
					content += '<tr><td width="300"><a href="ChannelByFavorite?' + folderList[indexer].mGroupName + '">' + folderList[indexer].mGroupName + '</a></td>'
			except IndexError :
				content += '<tr><td>&nbsp;</td>'
				favEnd = True

			try :
				content += "<td>" + str(channelList[indexer].mPresentationNumber) + "</td>"
				content += '<td width="200">' + channelList[indexer].mName + '</td>'
				content += '<td class="epg">[<a href="Zapping?' + str(channelList[indexer].mNumber) + '" target="zapper">Zap</a>]</td>'
				content += '<td class="epg">[<a href="javascript:JumpToEpg(' + str(channelList[indexer].mSid) + ',' + str(channelList[indexer].mTsid) + ',' + str(channelList[indexer].mOnid) + ')">EPG</a>]</td>'
				content += "</tr>"
			except IndexError :
				content += "<td>&nbsp;</td>"
				content += "<td>&nbsp;</td>"
				content += "<td>&nbsp;</td>"
				content += "<td>&nbsp;</td>"
				content += "</tr>"
				chEnd = True
			except TypeError :
				content += "<td>&nbsp;</td>"
				content += "<td>&nbsp;</td>"
				content += "<td>&nbsp;</td>"
				content += "<td>&nbsp;</td>"
				content += "</tr>"
				chEnd = True

			if chEnd and favEnd : break
			indexer += 1

		content += "</table>"

		self.ResetChannelListOnChannelWindow( channelList, ElisEnum.E_MODE_FAVORITE ) 

		return self.getChannelContent( content )

class Zapping( WebPage ) :

	def __init__( self, command ) :

		super(Zapping, self).__init__()
		self.ret = self.mDataCache.Channel_SetCurrent( int(command[0]), self.mZappingMode.mServiceType, None, aFrontMessage=True ) 

		self.content = "zapped"

class Epg( WebPage ) :

	def __init__( self, command ) :

		super(Epg, self).__init__()
		self.param = {}
		self.subcommand = command[0].split("&")

		for sub in self.subcommand :
			i = sub.split("=")
			self.param[i[0]] = i[1]

		self.content = self.getEpgPage( self.param ) 

	def getEpgPage( self, param ) :

		gmtFrom = self.mDataCache.Datetime_GetLocalTime()
		gmtUntil = gmtFrom + (3600 * 24 * 7 )
		maxCount = 10

		self.mEPGList = self.mCommander.Epgevent_GetList( int(param['sid']), int(param['tsid']), int(param['onid']), gmtFrom, gmtUntil, maxCount ) 
		content = ""

		if self.mEPGList == None :
			content += '<p class="noEpg">No EPG Data Found</p>'			
		else :
			for info in self.mEPGList :
				content += str( info.mEventId ) + "<br>"
				content += info.mEventName + "<br>"
				content += str( info.mStartTime ) + "<br>"

		return self.epgTemplate( content )

	def epgTemplate( self, content ) :

		content = """

			<html>
			<head>
				<title>PrismCube Web UI</title>
				<link href='uiStyle.css' type='text/css' rel='stylesheet'>
			<body>
			<div id='wrapper'>

				<div id='top'>
					<p>PrismCube Web UI</p>
				</div>
				<div id='epgContent'>
					%s
				</div>

			</div>
			</body>
			</html>
			
		""" % content

		return content 
			
		
