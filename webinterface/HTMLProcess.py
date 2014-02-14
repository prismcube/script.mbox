import pvr.DataCacheMgr
import pvr.ElisMgr
from pvr.gui.WindowImport import *
import xbmc
from urllib import unquote, quote

def GetHTMLClass( className, *param ) :

	# enlist every file to be processed by program 
	htmlClass = [RemoteControl, Channel, ChannelBySatellite, ChannelByCas, ChannelByFavorite, Zapping, Epg, Recordings]

	for cls in htmlClass :
		if className == cls.__name__ :
			return cls( param ) 
	else :
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

			print '[SimpleHTML] : ' + fileName

			if fileName.find("record_thumbnail") != -1 : 
				f = open("/" + fileName, "r")
			else :
				f = open(self.uiPath + fileName, "r")
				
			self.content = f.read()
			f.close()
			
		except :
			print "HTML Not Found"
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

		# For CAS-FTA channels
		self.casList = ['FTA', 'MEDIAGUARD', 'VIACCESS', 'NAGRA', 'IRDETO', 'CONAX', 'CRYPTOWORKS', 'BETADIGITAL', 'NDS', 'DRECRYPT', 'VERIMATRIX', 'OTHERS']

		if command[0] == 'all' :
			self.command = 'all'
			self.content = self.allChannelContent()
		elif command[0] == 'satellite' :
			self.command = 'satellite'
			self.content = self.satelliteChannelContent()
		elif command[0] == 'cas' :
			self.command = 'cas'
			self.content = self.casChannelContent()
		elif command[0] == 'favorite' :
			self.command = 'favorite'
			self.content = self.favoriteChannelContent()
		elif command[0] == 'mode' :
			self.command = 'mode'
			self.content = self.modeContent()
		else :
			pass  # do nothing 
			self.command = None


	def allChannelContent( self ) :

		# def Channel_GetList( self, aTemporaryReload = 0, aType = 0, aMode = 0, aSort = 0 ) 
		self.allChannel = self.mDataCache.Channel_GetList( aTemporaryReload=1, aType= self.mZappingMode.mServiceType, aMode=ElisEnum.E_MODE_ALL)
		content = """<table border="1" width="930" style="border-collapse:collapse;" cellpadding="0" cellspacing="0"><tr><td><table id="channels" width="100%">"""

		for cls in self.allChannel : 
			"""
			content += '<tr><td width="100">' + str(cls.mNumber) + '</td>'
			content += '<td width="300">' + cls.mName + '</a></td>'
			content += '<td class="epg">[<a href="Zapping?' + str(cls.mNumber) +'" target="zapper">Zap</a>]</td>'
			content += '<td class="epg">[<a href="javascript:JumpToEpg(' + str(cls.mSid) + ',' + str(cls.mTsid) + ',' + str(cls.mOnid) + ')">EPG</a>]</td>'
			# content += '<td class="epg">[<a href="/epg?sid='+ str(cls.mSid) + '&tsid=' + str(cls.mTsid) + '&onid=' + str(cls.mOnid) + '">EPG</a>]</td>'
			content += '</tr>'
			"""
			
			content += '<tr>'
			content += '<td align="center" width="50"><p class="channelContent">' + str(cls.mNumber) + '</p></td>'
			content += '<td><p class="channelContent">&nbsp;&nbsp;&nbsp;&nbsp;' + cls.mName +'</p></td>'
			content += '<td align="center" width="100"><p class="channelContent"><a href="Zapping?' + str(cls.mNumber) +'" target="zapper"><img src="./uiImg/zap.png" border="0"></a></p></td>'
			content += '<td align="center" width="100"><p class="channelContent"><a href="javascript:JumpToEpg(' + str(cls.mSid) + ',' + str(cls.mTsid) + ',' + str(cls.mOnid) + ')"><img src="./uiImg/EPG.png" border="0"></a></p></td>'
			content += '</tr>'
			
		content += '</table></td></tr></table>'

		self.ResetChannelListOnChannelWindow( self.allChannel, ElisEnum.E_MODE_ALL ) 
		return self.getChannelContent(content)

	def satelliteChannelContent( self ) :

		self.satelliteList = self.mDataCache.Satellite_GetConfiguredList()
		content = """<table border="1" width="930" style="border-collapse:collapse;" cellpadding="0" cellspacing="0"><tr><td><table id="channels" width="100%">"""

		for cls in self.satelliteList : 
			content += '<tr>'
			content += '<td align="center" width="50"><p class="channelContent">' + str(cls.mLongitude) + '</p></td>'
			content += '<td><p class="channelContent">&nbsp;&nbsp;&nbsp;&nbsp;<a href="ChannelBySatellite?' + str(cls.mName) + '">' + cls.mName +'</a></p></td>'
			content += '</tr>'

		content += '</td></tr></table>'
		return self.getChannelContent(content)

	def casChannelContent( self ) :

		content = """<table border="1" width="930" style="border-collapse:collapse;" cellpadding="0" cellspacing="0"><tr><td><table id="channels" width="100%">"""

		for cls in self.casList :
			caid = self.getCasCaid( cls ) 
			channelList = self.mDataCache.Channel_GetListByFTACas( self.mZappingMode.mServiceType, ElisEnum.E_MODE_CAS, self.mZappingMode.mSortingMode, caid )
			if channelList :
				content += '<tr><td><p class="channelContent">&nbsp;&nbsp;&nbsp;&nbsp;<a href="ChannelByCas?'+cls+'">' + cls + '</a></p></td></tr>'

		content += '</table></td></tr></table>'

		return self.getChannelContent( content )

	def favoriteChannelContent( self ) :

		self.allChannel = self.mDataCache.Favorite_GetList(0, self.mZappingMode.mServiceType)
		content = """<table border="1" width="930" style="border-collapse:collapse;" cellpadding="0" cellspacing="0"><tr><td><table id="channels" width="100%">"""

		for cls in self.allChannel : 
			content += '<tr><td><p class="channelContent">&nbsp;&nbsp;&nbsp;&nbsp;<a href="ChannelByFavorite?' + cls.mGroupName + '">' + cls.mGroupName + '</a></p></td></tr>'

		content += '</table></td></tr></table>'

		return self.getChannelContent( content )

	def modeContent( self ) :

		content = content = """<table border="1" width="930" style="border-collapse:collapse;" cellpadding="0" cellspacing="0"><tr><td><table id="channels" width="100%">"""
		
		if self.mZappingMode.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
			content += '<tr><td align="center"><p class="channelContent"><br><br>TV Mode</p></td></tr>'
			
		elif self.mZappingMode.mServiceType == ElisEnum.E_TYPE_RADIO :
			content += '<tr><td align="center"><p class="channelContent"><br><br>Radio Mode</p></td></tr>'
		else :
			content += '<tr><td align="center"><p class="channelContent"><br><br>Mode Error</p></td></tr>'

		content += '</table></td></tr></table>'

		return self.getChannelContent( content )

	def getChannelContent( self, content ) :

		self.channelContent  = """
		
			<html>
			<head>
				<title>PrismCube Web UI</title>
				<link href='uiStyle.css' type='text/css' rel='stylesheet'>
				<script>
				
					function showIcon( target ) {
						var icon = 'img0' + target;
						document.getElementById(icon).style.visibility = 'visible';
					}
					
					function hideIcon( target ) {
						var icon = 'img0' + target;
						document.getElementById(icon).style.visibility = 'hidden';
					}

					function showColor( target, name ) {
						var icon = 'icon' + target;
						var img = './uiImg/' + name + '.png';
						document.getElementById(icon).src = img;
					}

					function hideColor( target, name ) {
						var icon = 'icon' + target;
						var img = './uiImg/' + name + '_bw.png';
						document.getElementById(icon).src = img;
					}

					function JumpToEpg( sid, tsid, onid ) {
						var target = '/Epg?sid=' + sid + '&tsid=' + tsid + '&onid=' + onid;		
						window.open( target, 'epg', 'width=500, height=500');
					}

				</script>
			<body>
			<div id='wrapper'>

				<div id='top'>
					<div id='logo'><img src='./uiImg/prismcube_logo.png'></div>		
					<div id='title'>
						PrismCube Web UI
					</div>
				</div>
				
				<div id='menu'>
					<p><img src="./uiImg/mark.png" id="img01" style="visibility: hidden;"> Channel</p>
					<p><img src='./uiImg/mark.png' id='img02' style='visibility: hidden;'> <a href='/stream/stream.m3u' onmouseover='javacript:showIcon(2);' onmouseout='javascript:hideIcon(2);'>Live Stream</a></p>
					<p><img src='./uiImg/mark.png' id='img03' style='visibility: hidden;'> <a href='uiRemote.html' onmouseover='javacript:showIcon(3);' onmouseout='javascript:hideIcon(3);'>Remote Control</a></p>
					<p><img src='./uiImg/mark.png' id='img04' style='visibility: hidden;'> <a href='Recordings' onmouseover='javacript:showIcon(4);' onmouseout='javascript:hideIcon(4);'>Recordings</a></p>
				</div>
				
				<div id='main'>

					<div class='submenu'>
						<table align='center'>
						<tr>
							%s
						</tr>
						</table>
					</div>

					<div id='content'>
					%s
					<iframe name='zapper' width='0' height='0' style='display: none;'></iframe>
					</div>
					
				</div>

			</div>
			</body>
			</html>
			
		""" % ( self.getSubMenu(), content )
		return self.channelContent

	def getSubMenu( self ) :

		print '[Sub Menu]' 
		print self.command

		submenu = ""
		if self.command == "all" :
			submenu += """<td><img id='icon1' src='./uiImg/channels.png' border='0'></td>"""
		else :
			submenu += """<td><a href='Channel?all' onmouseover="javascript:showColor(1, 'channels');" onmouseout="javascript:hideColor(1, 'channels');"><img id='icon1' src='./uiImg/channels_bw.png' border='0'></a></td>"""

		if self.command == "satellite" :
			submenu += """<td><img id='icon2' src='./uiImg/satellite.png' border='0'></td>"""
		else :
			submenu += """<td><a href='Channel?satellite' onmouseover="javascript:showColor(2, 'satellite');" onmouseout="javascript:hideColor(2, 'satellite');"><img id='icon2' src='./uiImg/satellite_bw.png' border='0'></a></td>"""

		if self.command == "cas" :
			submenu += """<td><img id='icon3' src='./uiImg/cas.png' border='0'></td>"""
		else :
			# submenu += """<td><a href='uiChannelByCas.html' onmouseover="javascript:showColor(3, 'cas');" onmouseout="javascript:hideColor(3, 'cas');"><img id='icon3' src='./uiImg/cas_bw.png' border='0'></a></td>"""
			submenu += """<td><a href='Channel?cas' onmouseover="javascript:showColor(3, 'cas');" onmouseout="javascript:hideColor(3, 'cas');"><img id='icon3' src='./uiImg/cas_bw.png' border='0'></a></td>"""
			
		if self.command == "favorite" :
			submenu += """<td><img id='icon4' src='./uiImg/favorite.png' border='0'></td>"""
		else :
			submenu += """<td><a href='Channel?favorite' onmouseover="javascript:showColor(4, 'favorite');" onmouseout="javascript:hideColor(4, 'favorite');"><img id='icon4' src='./uiImg/favorite_bw.png' border='0'></a></td>"""

		if self.command == "mode" :
			submenu += """<td><img id='icon5' src='./uiImg/mode.png' border='0'></td>"""
		else :
			submenu += """<td><a href='Channel?mode' onmouseover="javascript:showColor(5, 'mode');" onmouseout="javascript:hideColor(5, 'mode');"><img id='icon5' src='./uiImg/mode_bw.png' border='0'></a></td>"""

		print submenu

		return submenu

	def getCasCaid(self, name) :

		if name == self.casList[0] :
			caid = ElisEnum.E_FTA_CHANNEL
		elif name == self.casList[1] :
			caid = ElisEnum.E_MEDIAGUARD
		elif name == self.casList[2] :
			caid = ElisEnum.E_VIACCESS
		elif name == self.casList[3] :
			caid = ElisEnum.E_NAGRA
		elif name == self.casList[4] :
			caid = ElisEnum.E_IRDETO
		elif name == self.casList[5] :
			caid = ElisEnum.E_CONAX
		elif name == self.casList[6] :
			caid = ElisEnum.E_CRYPTOWORKS
		elif name == self.casList[7] :
			caid = ElisEnum.E_BETADIGITAL
		elif name == self.casList[8] :
			caid = ElisEnum.E_NDS
		elif name == self.casList[9] :
			caid = ElisEnum.E_DRECRYPT	
		elif name == self.casList[10] :
			caid = ElisEnum.E_VERIMATRIX
		else :
			caid = ElisEnum.E_OTHERS

		return caid

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
		content = """<table border="1" width="930" style="border-collapse:collapse;" cellpadding="0" cellspacing="0"><tr><td><table id="channels" width="100%" border="0">"""
		indexer = 0

		satEnd = False
		chEnd = False

		while True :

			try : 
				content += '<tr>'
				content += '<td align="center" width="50"><p class="channelContent">' + str(satelliteList[indexer].mLongitude) + '</p></td>'
				if satelliteList[indexer].mName == satelliteName :
					content += '<td width="200" bgcolor="#dfdfdf">&nbsp;&nbsp;&nbsp;&nbsp;' + str(satelliteList[indexer].mName) + '</td>'
				else :
					# content += '<td width="200"><a href="ChannelBySatellite?' + str(satelliteList[indexer].mName) + '">' + str(satelliteList[indexer].mName) + '</a></td>'
					content += '<td><p class="channelContent">&nbsp;&nbsp;&nbsp;&nbsp;<a href="ChannelBySatellite?' + str(satelliteList[indexer].mName) + '">' + str(satelliteList[indexer].mName) + '</a></p></td>'

			except IndexError :
				content += '<tr><td>&nbsp;</td><td>&nbsp;</td>'
				satEnd = True
		
			try :
				content += '<td align="center"><p class="channelContent">' + str( channelList[indexer].mNumber ) + '</p></td>'
				content += '<td><p class="channelContent">&nbsp;&nbsp;&nbsp;&nbsp;' + channelList[indexer].mName + '</p></td>'
				content += '<td align="center"><p class="channelContent"><a href="Zapping?' + str(channelList[indexer].mNumber) + '" target="zapper"><img src="./uiImg/zap.png" border="0"></a></p></td>'
				content += '<td align="center"><p class="channelContent"><a href="javascript:JumpToEpg(' + str(channelList[indexer].mSid) + ',' + str(channelList[indexer].mTsid) + ',' + str(channelList[indexer].mOnid) + ')"><img src="./uiImg/EPG.png" border="0"></a></p></td></tr>'
				
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

		content += '</table></td></tr></table>'
		
		self.command = "satellite"
		print "self.command=" + self.command

		self.ResetChannelListOnChannelWindow( channelList, ElisEnum.E_MODE_SATELLITE ) 
		return self.getChannelContent( content )

class ChannelByCas( Channel ) :

	def __init__( self, command ) :

		super(ChannelByCas, self).__init__(command)

		self.validList = self.getValidList()
		self.content = self.channelByCasContent(command) 

	def channelByCasContent( self, command ) :

		caid = self.getCasCaid( command[0] ) 

		print '[WEBUI:caid]' + str(caid)
		print command[0]
			
		channelList = self.mDataCache.Channel_GetListByFTACas( self.mZappingMode.mServiceType, ElisEnum.E_MODE_CAS, self.mZappingMode.mSortingMode, caid )
		content = """<table border="1" width="930" style="border-collapse:collapse;" cellpadding="0" cellspacing="0"><tr><td><table id="channels" width="100%">"""
		indexer = 0

		casEnd = False
		chEnd = False

		while True :

			try :
				if self.validList[indexer] == command[0] :
					content += '<tr><td width="200" bgcolor="#dfdfdf"><p class="channelContent">&nbsp;&nbsp;&nbsp;&nbsp;' + self.validList[indexer] + '</p></td>'
				else :
					content += '<tr><td width="200"><p class="channelContent">&nbsp;&nbsp;&nbsp;&nbsp;<a href="ChannelByCas?' + self.validList[indexer] + '">' + self.validList[indexer] + '</a></p></td>'
			except IndexError :
				content += '<tr><td>&nbsp;</td>'
				casEnd = True

			try :
				content += '<td width="50" align="center"><p class="channelContent">' + str(channelList[indexer].mNumber) +'</p></td>'
				content += '<td><p class="channelContent">&nbsp;&nbsp;&nbsp;&nbsp;' + channelList[indexer].mName +"</a></td>"
				
				content += '<td align="center" width="100"><p class="channelContent"><a href="Zapping?' + str(channelList[indexer].mNumber) +'" target="zapper"><img src="./uiImg/zap.png" border="0"></a></p></td>'
				content += '<td align="center" width="100"><p class="channelContent"><a href="javascript:JumpToEpg(' + str(channelList[indexer].mSid) + ',' + str(channelList[indexer].mTsid) + ',' + str(channelList[indexer].mOnid) + ')"><img src="./uiImg/EPG.png" border="0"></a></p></td>'

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

		self.command = "cas"

		self.ResetChannelListOnChannelWindow( channelList, ElisEnum.E_MODE_CAS ) 
		return self.getChannelContent( content )

	def getValidList(self) :

		validList = []

		for name in self.casList :
			caid = self.getCasCaid( name )
			channelList = self.mDataCache.Channel_GetListByFTACas( self.mZappingMode.mServiceType, ElisEnum.E_MODE_CAS, self.mZappingMode.mSortingMode, caid )
			if channelList :
				validList.append( name )

		return validList

class ChannelByFavorite( Channel ) :

	def __init__( self, command ) :

		super(ChannelByFavorite, self).__init__( command )
		self.content = self.channelByFavoriteContent(command) 

	def channelByFavoriteContent( self, command ) :

		favName = unquote( command[0] )   # decoding url encoded string 
		
		folderList = self.mDataCache.Favorite_GetList(0, self.mZappingMode.mServiceType)
		channelList = self.mDataCache.Channel_GetListByFavorite( self.mZappingMode.mServiceType, ElisEnum.E_MODE_FAVORITE, self.mZappingMode.mSortingMode, favName )
		
		content = """<table border="1" width="930" style="border-collapse:collapse;" cellpadding="0" cellspacing="0"><tr><td><table id="channels" width="100%" border="0">"""
		indexer = 0

		favEnd = False
		chEnd = False
		
		while True :

			try :
				if folderList[indexer].mGroupName == favName :
					content += '<tr>'
					content += '<td width="300" bgcolor="#dfdfdf"><p class="channelContent">&nbsp;&nbsp;&nbsp;&nbsp;' + folderList[indexer].mGroupName + '</p></td>'
				else :
					content += '<tr>'
					content += '<td width="300"><p class="channelContent">&nbsp;&nbsp;&nbsp;&nbsp;<a href="ChannelByFavorite?' + folderList[indexer].mGroupName + '">' +  folderList[indexer].mGroupName + '</a></p></td>'
			except IndexError :
				content += '<tr><td>&nbsp;</td>'
				favEnd = True

			try :
				content += '<td width="50" align="center"><p class="channelContent">' + str(channelList[indexer].mPresentationNumber) + '</p></td>'
				content += '<td width="200"><p class="channelContent">&nbsp;&nbsp;&nbsp;&nbsp;' + channelList[indexer].mName + '</p></td>'
				content += '<td align="center" width="100"><p class="channelContent"><a href="Zapping?' + str(channelList[indexer].mNumber) +'" target="zapper"><img src="./uiImg/zap.png" border="0"></a></p></td>'
				content += '<td align="center" width="100"><p class="channelContent"><a href="javascript:JumpToEpg(' + str(channelList[indexer].mSid) + ',' + str(channelList[indexer].mTsid) + ',' + str(channelList[indexer].mOnid) + ')"><img src="./uiImg/EPG.png" border="0"></a></p></td>'
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

		content += "</table></td></tr></table>"

		self.command = "favorite"

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

class Recordings( WebPage ) :

	def __init__( self, command ) :
		super(Recordings, self).__init__()
		self.content = self.recordingsContent(command) 

	def recordingsContent( self, command ) :
	
		recordingList = self.mDataCache.Record_GetList(1)
		thumbnailImg = glob.glob( os.path.join( '/mnt/hdd0/pvr/thumbnail', 'record_thumbnail*.jpg')  )
		thumbnailList = {}
		
		for img in thumbnailImg :
			keyVal = img.split("_")[2]
			thumbnailList[keyVal] =  img

		content = """<table border="1" width="930" style="border-collapse:collapse;" cellpadding="0" cellspacing="0"><tr><td><table width="100%" border="0">"""
		
		for rec in recordingList :

			recDuration =  int( rec.mDuration / 60 )
			if ( rec.mDuration % 60 ) != 0 :
				recDuration += 1
			try :				
				content += "<tr>"
				content += '	<td><img src="' + thumbnailList[str(rec.mRecordKey)] + '"></td>'
				content += '	<td>'
				content += '	<table width="100%" border="0" cellpadding="5">'
				content += '	<tr>'
				content += '		<td><p class="recContent">P%04d.%s</p></td>' % ( rec.mChannelNo, rec.mChannelName )
				content += '		<td align="right"><p class="recContent">' + TimeToString(rec.mStartTime) + '</p></td>'
				content += '		<td rowspan="2" align="center" width="100"><a href="/recording/stream.m3u?%s"><img src="./uiImg/stream.png" border="0"></a></td>' % str(rec.mRecordKey)
				content += '	</tr>'
				content += '	<tr>'
				content += '		<td><p class="recContent">' + str(rec.mRecordName) +  '</p></td>'
				content += '		<td align="right"><p class="recContent">' + str(recDuration) + ' min</p></td>'
				content += '	</tr>'
				content += '</table>'
			except :
				print 'error cache record thumbnai'

		content += '</td></tr></table>'
		return self.getBasicTemplate( content ) 
			
	def getBasicTemplate( self, mainContent ) :

		content  = """
		
			<html>
			<head>
				<title>PrismCube Web UI</title>
				<link href='uiStyle.css' type='text/css' rel='stylesheet'>
			<body>
			<div id='wrapper'>

				<div id='top'>
					<div id='logo'><img src='./uiImg/prismcube_logo.png'></div>		
					<div id='title'>
						PrismCube Web UI
					</div>
				</div>
				
				<div id='menu'>
					<p><img src='./uiImg/mark.png' id='img01' style='visibility: hidden;'> <a href='uiChannel.html' onmouseover='javacript:showIcon(1);' onmouseout='javascript:hideIcon(1);'>Channel</a></p>
					<p><img src='./uiImg/mark.png' id='img02' style='visibility: hidden;'> <a href='/stream/stream.m3u' onmouseover='javacript:showIcon(2);' onmouseout='javascript:hideIcon(2);'>Live Stream</a></p>
					<p><img src='./uiImg/mark.png' id='img03' style='visibility: hidden;'> <a href='uiRemote.html' onmouseover='javacript:showIcon(3);' onmouseout='javascript:hideIcon(3);'>Remote Control</a></p>
					<p><img src='./uiImg/mark.png' id='img04' style='visibility: hidden;'> <a href='Recordings' onmouseover='javacript:showIcon(4);' onmouseout='javascript:hideIcon(4);'>Recordings</a></p>
				</div>
				
				<div id='main'>

					<div id='content'>
					%s
					<iframe name='zapper' width='0' height='0' style='display: none;'></iframe>
					</div>
					
				</div>

			</div>
			</body>
			</html>
		""" % mainContent 

		return content

		

		
		