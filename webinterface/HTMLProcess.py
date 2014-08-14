#import pvr.DataCacheMgr
#import pvr.ElisMgr
from pvr.gui.WindowImport import *
import xbmc
from urllib import unquote, quote
from datetime import datetime
from BeautifulSoup import BeautifulSoup 
import os

def GetHTMLClass( className, *param ) :

	# enlist every file to be processed by program 
	htmlClass = [RemoteControl, Channel, ChannelBySatellite, ChannelByCas, ChannelByFavorite, Zapping, Epg, Recordings, Timer, Screenshot, Record, getScreenshot]

	htmlClass.append(EpgGrid)
	htmlClass.append(RecordingDel)
	htmlClass.append(ZapUp)
	htmlClass.append(ZapDown)
	htmlClass.append(RecordCheck)
	htmlClass.append(CheckNAS)

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
			
		except Exception, erro:
			print str(erro)
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

	def GetParams( self, command ) :
		params = {}
		args = command.split('&')
		for arg in args :
			temp = arg.split('=') 
			params[temp[0]] = temp[1]
		return params

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

	def getBasicTemplate( self, mainContent ) :

		content  = """
		
			<html>
			<head>
				<title>PRISMCUBE Web UI</title>
				<meta http-equiv="content-type" content="text/html;charset=UTF-8" />
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

					function delRecord( target ) {
						if( confirm("Are you sure to delete the selected file?") ) {
							document.recordDel.key.value = target;
							document.recordDel.submit();
						}
					}

				</script>
			<body>
			
			<div id='wrapper'>

				<div id='top'>
					<div id='logo'><img src='./uiImg/prismcube_logo.png'></div>		
					<div id='title'>
						PRISMCUBE Web UI
					</div>
				</div>
				
				<div id='menu'>
					<p><img src='./uiImg/mark.png' id='img01' style='visibility: hidden;'> <a href='uiChannel.html' onmouseover='javacript:showIcon(1);' onmouseout='javascript:hideIcon(1);'>Channel</a></p>
					<p><img src='./uiImg/mark.png' id='img02' style='visibility: hidden;'> <a href='uiStream.html' onmouseover='javacript:showIcon(2);' onmouseout='javascript:hideIcon(2);'>Live Stream</a></p>
					<!-- <p><img src="./uiImg/mark.png" id="img06" style="visibility: hidden;"> <a href="EpgGrid" onmouseover="javacript:showIcon(6);" onmouseout="javascript:hideIcon(6);">EPG</a></p> -->
					<p><img src='./uiImg/mark.png' id='img03' style='visibility: hidden;'> <a href='uiRemote.html' onmouseover='javacript:showIcon(3);' onmouseout='javascript:hideIcon(3);'>Remote Control</a></p>
					<p><img src='./uiImg/mark.png' id='img05' style='visibility: hidden;'> <a href='Timer' onmouseover='javacript:showIcon(5);' onmouseout='javascript:hideIcon(5);'>Timer</a></p>
					<p><img src='./uiImg/mark.png' id='img04' style='visibility: hidden;'> <a href='Recordings' onmouseover='javacript:showIcon(4);' onmouseout='javascript:hideIcon(4);'>Recordings</a></p>
					<p><img src='./uiImg/mark.png' id='img07' style='visibility: hidden;'> <a href='Screenshot' onmouseover='javacript:showIcon(7);' onmouseout='javascript:hideIcon(7);'>Screenshot</a></p>
				</div>
				
				<div id='main'>

					<div id='content'>
					%s

					<form name="recordForm" action="Record" method="post">
						<input type="hidden" name="sid">
						<input type="hidden" name="tsid">
						<input type="hidden" name="onid">
					</form>

					<form name="recordDel" action="RecordingDel" method="get">
						<input type="hidden" name="key">
					</form>
					
					<iframe name='zapper' width='0' height='0' style='display: none;'></iframe>
					</div>
					
				</div>

			</div>
			</body>
			</html>
		""" % mainContent 

		return content

				
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

		if self.allChannel :
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
				# content += '<td align="center" width="100"><p class="channelContent"><a href="Record?sid='+str(cls.mSid)+'&tsid='+str(cls.mTsid)+'&onid='+str(cls.mOnid)+'"><img src="./uiImg/record.png" border="0"></a></p></td>'
				content += '<td align="center" width="100"><p class="channelContent"><a href="javascript:JumpToRecord('+str(cls.mNumber)+');"><img src="./uiImg/record.png" border="0"></a></p></td>'
				content += '</tr>'

			self.ResetChannelListOnChannelWindow( self.allChannel, ElisEnum.E_MODE_ALL ) 

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

		try :
			f = open("/usr/share/xbmc/addons/script.mbox/webinterface/uiStyle.css", "r");
			css = f.read();
			f.close();
		except Exception, e :
			print str(e)
			css = ''

		print '[Style Path]'
		print str( os.getcwd() )

		self.channelContent  = """

			<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
			"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
			<html>
			<head>
				<title>PRISMCUBE Web UI</title>
				<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
				<script src="./jquery.js"></script>
				<script src="./block.js"></script>
				<style>
					%s
				</style>
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
						return; // to prevent too much exception caused by this process
						
						var icon = 'icon' + target;
						var img = './uiImg/' + name + '.png';
						document.getElementById(icon).src = img;
					}

					function hideColor( target, name ) {
						return; // to prevent too much exception caused by this process
						
						var icon = 'icon' + target;
						var img = './uiImg/' + name + '_bw.png';
						document.getElementById(icon).src = img;
					}

					function JumpToEpg( sid, tsid, onid ) {
						var target = '/Epg?sid=' + sid + '&tsid=' + tsid + '&onid=' + onid;		
						window.open( target, 'epg', 'width=500, height=500, scrollbars=1');
					}

					function JumpToRecord( channelNumber ) {
						var duration = prompt("Please enter duration time (in min) for the recording");
						if( duration ) {
							document.recordForm.channelNumber.value = channelNumber;
							document.recordForm.duration.value = duration;
							document.recordForm.submit();
						} 
					}

					function RecordCheck( channelNumber ) {
						var duration = prompt("Please enter duration time (in min) for the recording");

						if(duration) {
							target = 'RecordCheck?channelNumber='+channelNumber+'&duration='+ duration;
							window.open( target, 'CheckHDD', 'height=500, width=500');
						}
					}

				</script>
				<script>
				// invoke blockUI as needed -->
				$(document).ready( function() {
				   $.blockUI({ css: { 
				            border: 'none', 
				            padding: '15px', 
				            backgroundColor: '#000', 
				            '-webkit-border-radius': '10px', 
				            '-moz-border-radius': '10px', 
				            opacity: .5, 
				            color: 'yellow'
				        } }); 
				 
				    setTimeout($.unblockUI, 1800); 
				});
				</script>
			<body>
			<div id='wrapper'>

				<div id='top'>
					<div id='logo'><img src='./uiImg/prismcube_logo.png'></div>		
					<div id='title'>
						PRISMCUBE Web UI
					</div>
				</div>
				
				<div id='menu'>
					<p><img src="./uiImg/mark.png" id="img01" style="visibility: hidden;"> Channel</p>
					<p><img src='./uiImg/mark.png' id='img02' style='visibility: hidden;'> <a href='uiStream.html' onmouseover='javacript:showIcon(2);' onmouseout='javascript:hideIcon(2);'>Live Stream</a></p>
					<p><img src='./uiImg/mark.png' id='img03' style='visibility: hidden;'> <a href='uiRemote.html' onmouseover='javacript:showIcon(3);' onmouseout='javascript:hideIcon(3);'>Remote Control</a></p>
					<!-- <p><img src="./uiImg/mark.png" id="img06" style="visibility: hidden;"> <a href="EpgGrid" onmouseover="javacript:showIcon(6);" onmouseout="javascript:hideIcon(6);">EPG</a></p> -->
					<p><img src='./uiImg/mark.png' id='img05' style='visibility: hidden;'> <a href='Timer' onmouseover='javacript:showIcon(5);' onmouseout='javascript:hideIcon(5);'>Timer</a></p>
					<p><img src='./uiImg/mark.png' id='img04' style='visibility: hidden;'> <a href='Recordings' onmouseover='javacript:showIcon(4);' onmouseout='javascript:hideIcon(4);'>Recordings</a></p>
					<p><img src='./uiImg/mark.png' id='img07' style='visibility: hidden;'> <a href='Screenshot' onmouseover='javacript:showIcon(7);' onmouseout='javascript:hideIcon(7);'>Screenshot</a></p>
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
					<form name="recordForm" action="Record" method="get" target="zapper">
						<input type="hidden" name="channelNumber">
						<input type="hidden" name="duration">
						<input type="hidden" name="volumeId" value="0">
						<input type="hidden" name="NASChecked" value="no">
					</form>
					
					<iframe name='zapper' width='1000' height='500' style='display: none;'></iframe>
					</div>
					
				</div>

			</div>
			</body>
			</html>
			
		""" % ( css, self.getSubMenu(), content )
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

		if not cmds[1].isdigit()  :
			target = 'xbmc.Action(' + cmds[1] + ')'
			xbmc.executebuiltin(target)

		if cmds[1] == "2001" :
			#not used
			pass

		if cmds[1] == "2002" :
			#power Todo
			pass

		if cmds[1] == "2003" :
			xbmc.executebuiltin( 'xbmc.Action(DVBRed)' )

		if cmds[1] == "2004" :
			xbmc.executebuiltin( 'xbmc.Action(DVBGreen)' )

		if cmds[1] == "2005" :
			xbmc.executebuiltin( 'xbmc.Action(DVBYellow)' )

		if cmds[1] == "2006" :
			xbmc.executebuiltin( 'xbmc.Action(DVBBlue)' )

		if cmds[1] == "2007" :
			#not used
			pass

		if cmds[1] == "2008" :
			xbmc.executebuiltin( 'xbmc.Action(DVBMediaCenter)' )

		if cmds[1] == "2009" :
			xbmc.executebuiltin( 'xbmc.Action(DVBTVRadio)' )

		if cmds[1] == "2010" :
			xbmc.executebuiltin( 'xbmc.Action(DVBRecord)' )

		if cmds[1] == "2011" :
			xbmc.executebuiltin( 'xbmc.Action(Play)' )

		if cmds[1] == "2012" :
			xbmc.executebuiltin( 'xbmc.Action(Stop)' )

		if cmds[1] == "2013" :
			xbmc.executebuiltin( 'xbmc.Action(DVBRewind)' )

		if cmds[1] == "2014" :
			xbmc.executebuiltin( 'xbmc.Action(DVBFF)' )

		if cmds[1] == "2015" :
			xbmc.executebuiltin( 'xbmc.Action(DVBArchive)' )

		if cmds[1] == "2016" :
			xbmc.executebuiltin( 'xbmc.Action(info)' )

		if cmds[1] == "2017" :
			xbmc.executebuiltin( 'xbmc.Action(Up)' )

		if cmds[1] == "2018" :
			xbmc.executebuiltin( 'xbmc.Action(Left)' )

		if cmds[1] == "2019" :
			xbmc.executebuiltin( 'xbmc.Action(Select)' )

		if cmds[1] == "2020" :
			xbmc.executebuiltin( 'xbmc.Action(Right)' )

		if cmds[1] == "2021" :
			xbmc.executebuiltin( 'xbmc.Action(Down)' )

		if cmds[1] == "2022" :
			xbmc.executebuiltin( 'xbmc.Action(Back)' )

		if cmds[1] == "2023" :
			xbmc.executebuiltin( 'xbmc.Action(PreviousMenu)' )

		if cmds[1] == "2024" :
			xbmc.executebuiltin( 'xbmc.Action(ContextMenu)' )

		if cmds[1] == "2025" :
			xbmc.executebuiltin( 'xbmc.Action(VolumeUp)' )

		if cmds[1] == "2026" :
			xbmc.executebuiltin( 'xbmc.Action(PageUp)' )

		if cmds[1] == "2027" :
			xbmc.executebuiltin( 'xbmc.Action(VolumeDown)' )

		if cmds[1] == "2028" :
			xbmc.executebuiltin( 'xbmc.Action(Mute)' )

		if cmds[1] == "2029" :
			xbmc.executebuiltin( 'xbmc.Action(PageDown)' )

		if cmds[1] == "2030" :
			# Teletext Todo
			pass

		if cmds[1] == "2031" :
			xbmc.executebuiltin( 'xbmc.Action(DVBSubtitle)' )

		if cmds[1] == "2032" :
			# NumLock Toto
			pass

		"""
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

		if int( cmds[1] ) in [ 0, 1, 2, 3 ] :
			self.PowerControl( cmds[1] )
			self.content = "Power Control"
		"""

	def PowerControl( self, control ) :

		if int(control) == 3 :
			#Active Standby
			self.mCommander.System_StandbyMode( 1 )

		if int(control) == 2 :
			self.mCommander.System_StandbyMode( 0 )

		if int(control) == 1 :
			return
			#self.mDataCache.Splash_StartAndStop( 1 )
			#pvr.ElisMgr.GetInstance().Shutdown( )
			#xbmc.executebuiltin( 'Settings.Save' )
			#os.system( 'killall -9 xbmc.bin' )
			
		if int(control) == 0 :
			isDownload = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SYSTEM_UPDATE ).GetStatusFromFirmware( )
			if isDownload :
				pass
			else :
				self.mDataCache.System_Reboot( )			

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
			setVolume = currentVol + 4
		elif control == 'down' :
			setVolume = currentVol - 4
		
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
				content += '<td align="center"><p class="channelContent"><a href="javascript:JumpToEpg(' + str(channelList[indexer].mSid) + ',' + str(channelList[indexer].mTsid) + ',' + str(channelList[indexer].mOnid) + ')"><img src="./uiImg/EPG.png" border="0"></a></p></td>'
				content += '<td align="center" width="100"><p class="channelContent"><a href="javascript:JumpToRecord('+str(channelList[indexer].mNumber)+');"><img src="./uiImg/record.png" border="0"></a></p>'
				content += '<a href="javascript:RecordCheck('+str(channelList[indexer].mNumber)+');">RRR</a></td></tr>'
				
			except IndexError :
				content += '<td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td>'
				content += '<td>&nbsp;</td><td>&nbsp;</td></tr>'
				chEnd = True

			except TypeError :
				content += '<td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td>'
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
				content += '<td align="center" width="100"><p class="channelContent"><a href="javascript:JumpToRecord('+str(channelList[indexer].mNumber)+');"><img src="./uiImg/record.png" border="0"></a></p></td>'
				content += "</tr>"

			except IndexError :
				content += "<td>&nbsp;</td>"
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
				content += '<td align="center" width="100"><p class="channelContent"><a href="javascript:JumpToRecord('+str(channelList[indexer].mNumber)+');"><img src="./uiImg/record.png" border="0"></a></p></td>'
				content += "</tr>"

			except IndexError :
				content += "<td>&nbsp;</td>"
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
		maxCount = 100

		self.mEPGList = self.mCommander.Epgevent_GetList( int(param['sid']), int(param['tsid']), int(param['onid']), gmtFrom, gmtUntil, maxCount ) 
		content = ""

		if self.mEPGList == None :
			content += '<p class="noEpg">No EPG Data Found</p>'			
		else :
			for info in self.mEPGList :
				content += '<div class="epgContent">'
				content += str( info.mEventId ) + "<br>"
				content += info.mEventName + "<br>"
				content += TimeToString( info.mStartTime )
				content += " : "
				content += TimeToString( info.mStartTime, 1)
				content += '</div>'

				content += '<div class="epgDescription">'
				if info.mEventDescription and str(info.mEventDescription) != '(null)':
					content += (str(info.mEventDescription)).replace('\n', '<br />');
				content += '</div>'
	
		return self.epgTemplate( content )

	def epgTemplate( self, content ) :

		content = """

			<html>
			<head>
				<title>PRISMCUBE Web UI</title>
				<link href='uiStyle.css' type='text/css' rel='stylesheet'>
				<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
			<body>
			<div id='epgWrapper'>

				<div id='epgTop'>
					<p>PrismCube EPG Data</p>
				</div>

				%s
				
			</div>
			</body>
			</html>
			
		""" % content

		return content


class Screenshot( WebPage ) :

	def __init__( self, command ) :
		super(Screenshot, self).__init__()
		self.content = self.screenshotContent(command)

	def screenshotContent( self, command ) :
		os.system( '/usr/bin/grab -j 75' )
		content = """<img src="getScreenshot" width="920">"""

		return self.getBasicTemplate( content )


class getScreenshot( WebPage ) :

	def __init__( self, command ) :
		super(getScreenshot, self).__init__()
		self.content = self.getScreenshotContent(command)

	def getScreenshotContent( self, command ) :
		f = open("/tmp/screenshot.jpg", "rb")
		content = f.read()
		f.close()

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

		content = """<table border="0" width="930" style="border-collapse:collapse;" cellpadding="0" cellspacing="0"><tr><td><table width="100%" border="0">"""

		if recordingList :
		
			for rec in reversed(recordingList) :
			
				recDuration =  int( rec.mDuration / 60 )
				if ( rec.mDuration % 60 ) != 0 :
					recDuration += 1
				try :				
					content += "<tr>"

					try :
						content += '	<td><img src="' + thumbnailList[str(rec.mRecordKey)] + '"></td>'
					except :
						content += '	<td><img src="/uiImg/thumb.jpg"></td>'
						
					content += '	<td>'
					content += '	<table width="100%" border="0" cellpadding="5">'
					content += '	<tr>'
					content += '		<td><p class="recContent">P%04d.%s</p></td>' % ( rec.mChannelNo, rec.mChannelName )
					content += '		<td align="right"><p class="recContent">' + TimeToString(rec.mStartTime) + '</p></td>'
					content += '		<td rowspan="2" align="center" width="100"><a href="/recording/stream.m3u?%s"><img src="./uiImg/stream.png" border="0"></a>' % str(rec.mRecordKey)
					content += '		<br><a href="javascript:delRecord(%s)"><img src="./uiImg/Delete.png" border="0"></a></td>'  % str(rec.mRecordKey)
					content += '	</tr>'
					content += '	<tr>'
					content += '		<td><p class="recContent">' + str(rec.mRecordName) +  '</p></td>'
					content += '		<td align="right"><p class="recContent">' + str(recDuration) + ' min</p></td>'
					content += '	</tr>'
					content += '	</table>'
					content += ' 	</td>'
					content += '</tr>'
					content += '<tr><td colspan="2" align="center"><hr></td></tr>'
				except :
					print 'error cache record thumbnail'

		else :

			content += '<tr><td><br><br><p class="recContent">No Recordings</p></td></tr></table>'

		content += '</td></tr></table>'
		return self.getBasicTemplate( content ) 

class Timer( WebPage ) :

	def __init__( self, command ) :
		super(Timer, self).__init__()

		self.weekday = {}
		self.weekday[0] = "Sun"
		self.weekday[1] = "Mon"
		self.weekday[2] = "Tue"
		self.weekday[3] = "Wed"
		self.weekday[4] = "Thu"
		self.weekday[5] = "Fri"
		self.weekday[6] = "Sat"

		if len(command) > 0 :
			self.delId = command[0].split("=")[1]
			self.mDataCache.Timer_DeleteTimer( int(self.delId) )
		
		self.content = self.timerContent(command) 

	def timerContent( self, command ) :
		timerList = self.mDataCache.Timer_GetTimerList()
		content 	= """
			<script>
				function del( id ) {
					if( confirm("Are you sure to delete the selected timer?") ) {
						location.href = "/Timer?id=" + id;
					}
				}
			</script>
		"""
		content += """<table border="0" width="930" style="border-collapse:collapse;" cellpadding="0" cellspacing="0"><tr><td><table width="100%" border="0">"""

		for timer in timerList :
		
			timerDuration =  int( timer.mDuration / 60 )
			if ( timer.mDuration % 60 ) != 0 :
				timerDuration += 1
			try :
		
				content += '<tr>'
				content += '	<td>'
				content += '	<table width="100%" border="0" cellpadding="5">'
				content += '	<tr>'
				content += '		<td><p class="recContent">P%04d.%s</p></td>' % ( timer.mChannelNo, timer.mName )
				content += '		<td align="right"><p class="timerContent">' 
				content += 		TimeToString(timer.mStartTime) + ' <span class="timerTime">' + TimeToString(timer.mStartTime, TimeFormatEnum.E_HH_MM) + "</span> ~ "
				content += 		TimeToString(timer.mStartTime + timer.mDuration) + ' <span class="timerTime">' + TimeToString(timer.mStartTime + timer.mDuration, TimeFormatEnum.E_HH_MM)
				content += '		</span></p></td>'
				content += '		<td rowspan="2" align="center" width="100"><a href="javascript:del(' + str(timer.mTimerId) + ');"><img src="/uiImg/Delete.png" border="0"></a></td>' 	#Delete Button here!!!
				content += '	</tr>'
				content += '	<tr>'
				content += '		<td><p class="recContent">' + str(timer.mName) +  '</p></td>'
				content += '		<td align="right"><p class="recContent">' + str(timerDuration) + ' min</p></td>'
				content += '	</tr>'

				if timer.mWeeklyTimerCount > 0 :
					content += '<tr>'
					content += '<td colspan="2" align="left" class="weeklyInfo">Weekly Recording On : '

					for weeklyTimer in timer.mWeeklyTimer :
						content += self.weekday[weeklyTimer.mDate]
						content += '&nbsp;&nbsp;&nbsp;&nbsp;'

					content += '</td></tr>'

				elif timer.mTimerType == 7 :

					content += '<tr>'
					content += '<td colspan="2" align="left" class="timerView">View Only</td></tr>'
				
				content += '	</table>'
				content +=' 	</td>'
				content +='</tr>'
				content += '<tr><td><hr></td></tr>'
				
			except Exception, err :
				print str(err)
				print 'error timer list'

		content += '</td></tr></table>'
				
		return self.getBasicTemplate( content ) 

class EpgGrid( WebPage ) :

	def __init__( self, command ) :
		super(EpgGrid, self).__init__()
		self.content = self.epgGridContent(command) 

	def epgGridContent( self, command ) :

		print '[EPG Grid]'
		print command

		# get current time
		currenttime = datetime.fromtimestamp( self.mDataCache.Datetime_GetLocalTime() )
		currentHour = currenttime.hour

		#get channel list
		chList = self.mDataCache.Channel_GetList( aTemporaryReload=1, aType=self.mZappingMode.mServiceType, aMode=ElisEnum.E_MODE_ALL)
	
		content = """<table border="0" style="border-collapse:collapse;" cellpadding="0" cellspacing="0"><tr><td><table width="100%" border="0">"""
		content += '<tr><td>'

		content += '<div id="timeline"><ul><li class="timeTitle">%s' % TimeToString( self.mDataCache.Datetime_GetLocalTime() )
				
		# display time line at top		
		for i in range(6) :
			if currentHour < 10 :
				content += '<li class="time">0%d:00' % currentHour
			else :
				content += '<li class="time">%d:00' % currentHour

			currentHour += 1
			if currentHour >= 24 :
				currentHour = 0

		content += "</ul></div>"
		content += '<div class="clearAll"></div>'

		#display EPG Content 
		for ch in chList[:5] :
			content += '<div class="epgGridContent"><ul><li class="channel">%s' % ch.mName
			content += '</ul></div>'
			content += '<div class="clearAll"></div>'

		content += '</td></tr></table>'
		content += '</td></tr></table>'
		
		return self.getBasicTemplate( content ) 

class Record( WebPage ) :
	"""
		paramaters 
			channelNumber
			duration
			volumeId
	"""
	def __init__( self, command ) :
		super(Record, self).__init__()
		self.content = ""
	
		self.stationInfo = self.GetParams( command[0] )
		
		if self.stationInfo['NASChecked'] == 'no' :
			print '[Recording] Check for NAS'
			self.CheckNAS()
		else :
			print '[Recording] Recording Start'
			self.StartRecordingWithoutAsking()

	def CheckNAS( self ) :
		print 'checking nas'

		self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( True )
		if self.mNetVolumeList :
			self.content = """
				<script>
					window.open('CheckNAS?channelNumber=%s&duration=%s&volumeId=%s&NASChecked=%s', 'checknas', 'height=500, width=800');
				</script>
			""" % ( self.stationInfo['channelNumber'], self.stationInfo['duration'], self.stationInfo['volumeId'], self.stationInfo['NASChecked'] )
		else :
			self.StartRecordingWithoutAsking()

		"""
		for vol in self.mNetVolumeList :
			print vol.mIndexID
			print vol.mRemotePath
			print vol.mRemoteFullPath
			print vol.mMountCmd
		"""

	def StartRecordingWithoutAsking( self ) :
		runningCount = self.mDataCache.Record_GetRunningRecorderCount( )
		#LOG_TRACE( 'runningCount[%s]' %runningCount)
		if not HasAvailableRecordingHDD( ) :
			self.content = """
				<script>
					alert("No HDD available, cannot record without HDD");
				</script>
			"""
			return

		mTimer = self.mDataCache.GetRunnigTimerByChannel( )
		isOK = False

		if mTimer :
			#dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
			#dialog.doModal( )

			#if dialog.IsOK( ) == E_DIALOG_STATE_ERROR and dialog.GetConflictTimer( ) :
			#	RecordConflict( dialog.GetConflictTimer( ) )
			
			self.content = """
				<script>
					alert("Cannot start recording. Recording alreay in progress");
				</script>
			"""
			return

		elif runningCount < 2 :
			copyTimeshift = 0
			otrInfo = self.mDataCache.Timer_GetOTRInfo( )
			localTime = self.mDataCache.Datetime_GetLocalTime( )				

			#check ValidEPG
			hasValidEPG = False
			if otrInfo.mHasEPG :
				if localTime >= otrInfo.mEventStartTime  and localTime < otrInfo.mEventEndTime :
					hasValidEPG = True

			if hasValidEPG == False :
				otrInfo.mHasEPG = False
				prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
				otrInfo.mExpectedRecordDuration = prop.GetProp( )
				otrInfo.mEventStartTime = localTime
				otrInfo.mEventEndTime = localTime +	otrInfo.mExpectedRecordDuration
				otrInfo.mEventName = self.mDataCache.Channel_GetCurrent( ).mName

			if otrInfo.mTimeshiftAvailable :
				timeshiftRecordSec = int( otrInfo.mTimeshiftRecordMs/1000 )
				LOG_TRACE( 'mTimeshiftRecordMs=%dMs : %dSec' %(otrInfo.mTimeshiftRecordMs, timeshiftRecordSec ) )
			
				if otrInfo.mHasEPG == True :			
				
					copyTimeshift  = localTime - otrInfo.mEventStartTime
					LOG_TRACE( 'copyTimeshift #3=%d' %copyTimeshift )
					if copyTimeshift > timeshiftRecordSec :
						copyTimeshift = timeshiftRecordSec
					LOG_TRACE( 'copyTimeshift #4=%d' %copyTimeshift )
				else :
					self.ShowRecordingStartDialog( )
					return

			LOG_TRACE( 'copyTimeshift=%d' %copyTimeshift )

			if copyTimeshift <  0 or copyTimeshift > 12*3600 : #12hour * 60min * 60sec
				copyTimeshift = 0

			#expectedDuration =  self.mEndTime - self.mStartTime - copyTimeshift
			expectedDuration = otrInfo.mEventEndTime - localTime - 5 # 5sec margin

			LOG_TRACE( 'expectedDuration=%d' %expectedDuration )

			if expectedDuration < 0:
				LOG_ERR( 'Error : Already Passed' )
				expectedDuration = 0

			print '[Record]'
			print self.stationInfo['channelNumber']
			print self.stationInfo['duration']

			# ret = self.mDataCache.Timer_AddOTRTimer( False, expectedDuration, copyTimeshift, otrInfo.mEventName, True, 0, int(self.stationInfo['sid']),  int(self.stationInfo['tsid']), int(self.stationInfo['onid']) )
			ret = self.mDataCache.Timer_AddManualTimer( int(self.stationInfo['channelNumber']), 1, localTime + 5, int(self.stationInfo['duration']) * 60, 'Web UI Recordings', int(self.stationInfo['volumeId']) )

			#if ret[0].mParam == -1 or ret[0].mError == -1 :
			LOG_ERR( 'StartDialog ret=%s ' %ret )
			if ret and ( ret[0].mParam == -1 or ret[0].mError == -1 ) :	
				LOG_ERR( 'StartDialog ' )
				#RecordConflict( ret )
				#dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
				#dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_ERROR and dialog.GetConflictTimer( ) :
					#RecordConflict( dialog.GetConflictTimer( ) )
					self.content = """
						<script>
							alert("Cannot record, due to conflict");
						</script>
					"""
				return

			else :
				isOK = True
				self.content = """
					<script>
						alert("Recording Has Started");
					</script>
				"""

		else:
			#msg = MR_LANG( 'Maximum number of recordings reached' )
			#dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			#dialog.SetDialogProperty( MR_LANG( 'Error' ), msg )
			#dialog.doModal( )
			self.content = """
				<script>
					alert("2 Recordings in progress, cannot record more.");
				</script>
			"""
			return
			pass
			

		if isOK :
			#self.SetBlinkingProperty( 'True' )
			#self.mEnableBlickingTimer = True
			#self.mRecordBlinkingCount = E_MAX_BLINKING_COUNT			
			#self.StartBlinkingIconTimer( )
			
			self.mDataCache.SetChannelReloadStatus( True )

class RecordingDel( WebPage ) :

	def __init__( self, command ) :
		super(RecordingDel, self).__init__()

		print '[del]'
		print command
		
		self.params = self.GetParams( command[0] )
		self.mDataCache.Record_DeleteRecord( int(self.params['key']), 1)

		self.content = """
			<script>
				location.href = 'Recordings';
			</script>
		"""

class ZapUp( WebPage ) :

	def __init__( self, command ) :
		super( ZapUp, self).__init__()
		try :
			xbmc.executebuiltin( 'xbmc.Action(PageUp)' )
			self.content = "OK"
		except :
			self.content = "Fail"

class ZapDown( WebPage ) :

	def __init__( self, command ) :
		super( ZapDown, self).__init__()
		try :
			xbmc.executebuiltin( 'xbmc.Action(PageDown)' )
			self.content = "OK"
		except :
			self.content = "Fail"

class RecordCheck( WebPage ) :

	def __init__( self, command ) :
		super( RecordCheck, self).__init__()
		self.params = self.GetParams( command[0] )
		self.content = self.CheckHDDListContent()

		# print self.mDataCache.Record_GetNetworkVolume( True )

	def CheckHDDListContent( self ) :

		volumeList = self.mDataCache.Record_GetNetworkVolume(True) 
		if volumeList :

			content = """
				<html>
				<head>
					<title>PrismCube</title>
					<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
					<style type="text/css" rel="stylesheet">
						p {
							font-size: 0.8em;
							font-family: "arial";
						}
					</style>
				</head>
				<body>
					<p>List Goes Here</p>
				</body>
				</html>
			"""
		else :

			content = """
				<html>
				<head>
					<title>PrismCube</title>
					<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
				</head>
				<body>
				<script>
					var target = "Record?channelNumber=%s&duration=%s&volumeId=0";
					location.href = target;
					this.close();
				</script>
				</body>
				</html>
			""" % ( self.params['channelNumber'], self.params['duration'])
			
		return content

class CheckNAS( WebPage ) :
	def __init__( self, command ) :
		super(CheckNAS, self).__init__()
		self.params = self.GetParams( command[0] )
		
		self.content = self.checkNasContent()

	def checkNasContent( self ) :

		naslocations = self.mDataCache.Record_GetNetworkVolume( True )
		
		content = """
			<!doctype html>
			<html>
			<head>
				<title>PrismCube</title>
				<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
				<style>
					#main {
						width: 500px;
						margin: auto;
					}
					
					#title {
						font-family: consolas;
						font-size: 1.5em;
						font-weight: bold;
						text-align: center;
					}
					
					.select {
						width: 80%;
						margin: auto;
						padding: 10px 20px;
						border: 0px solid #dfdfdf;
					}

					.location {
						display: inline;
						font-family: arial;
						font-size: 1.1em;
						font-weight: bold;
						border: 0px solid blue;
						float: left;
					}
					
					.btn {
						display: inline;
						text-align: right;
						border: 0px solid blue;
						float: right;
					}
				</style>
				<script>
					function jumpToRecord( volumeid ) {
						document.myForm.volumeId.value = volumeid;
						document.myForm.submit();
						this.close();
					}
				</script>
			</head>
			<body>
			<div id="main">
			<p id="title">Select a Location to Record</p>
		"""
		if HasAvailableRecordingHDD( ) :
			content += '<div class="select">'
			content += '<div class="location">Internal HDD</div>'
			content += '<div class="btn"><button type="button" onclick="javascript:jumpToRecord(0);">Select</button></div>'
			content += '</div><br>'

		starter = 0 
		for vol in naslocations :
			if starter == 0 :
				starter = 1
			else :
				content += '<br>'
			content += '<div class="select">'
			content += '<div class="location">%s</div>' % vol.mRemotePath
			content += '<div class="btn"><button type="button" onclick="javascript:jumpToRecord(%s);">Select</button></div>' % vol.mIndexID
			content += '</div>'

		content += """
			</div>
			<form name="myForm" action="Record" method="get" target="zapper">
				<input type="hidden" name="channelNumber" value="%s">
				<input type="hidden" name="duration" value="%s">
				<input type="hidden" name="volumeId">
				<input type="hidden" name="NASChecked" value="yes">
			</form>
			</body>
			</html>
		""" % ( self.params['channelNumber'], self.params['duration'] ) 

		return content
		
