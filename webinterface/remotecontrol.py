#import dbopen
import pvr.XBMCInterface
from pvr.gui.WindowImport import *
import sys, inspect, time, threading
import xbmc, xbmcgui, gc

import webinterface 

class ElmoRemoteControl( webinterface.Webinterface ) :

	def __init__(self, urlPath) :

		super(ElmoRemoteControl, self).__init__(urlPath)

	def xmlError(self) :
		xmlstr = ''

		xmlstr += '<?xml version="1.0" encoding="UTF-8"?>'
		xmlstr += '<e2remotecontrol>'
		xmlstr += '	<e2result>False</e2result>'
		xmlstr += '	<e2resulttext>Command Not Found</e2resulttext>'
		xmlstr += '</e2remotecontrol>'

		return xmlstr

	def xmlResult(self) :
		
		try :
			if self.params['command'] == '115' : #volume up
				return self.VolumeControl('up') 
 			if self.params['command'] == '114' : #volume down
				return self.VolumeControl('down')

			if self.params['command'] == '403' : # channel down
				return self.ChannelControl('down')
			if self.params['command'] == '402': # channel up
				return self.ChannelControl('up')

			if self.params['command'] in ('103', '105', '106', '108', '352', '174') :
				return self.ArrowControl( self.params['command'] ) 

			return self.xmlError()
			
		except Exception, err:
 			print str(err)
			return self.xmlError()

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
			return self.xmlError()

		jsonStr = '{"jsonrpc": "2.0", "method": "%s", "id": 1}' % methodName
		xbmc.executeJSONRPC( jsonStr )

		xmlstr = ''
		xmlstr += '<?xml version="1.0" encoding="UTF-8"?>'
		xmlstr += '<e2remotecontrol>'
		xmlstr += '	<e2result>True</e2result>'
		xmlstr += '	<e2resulttext>Arrow Moved</e2resulttext>'
		xmlstr += '</e2remotecontrol>'

		return xmlstr
			
	def VolumeControl( self, control ) :

		currentVol = self.mCommander.Player_GetVolume()

		if control == 'up' : 
			setVolume = currentVol + 1
		elif control == 'down' :
			setVolume = currentVol - 1
		
		self.mCommander.Player_SetVolume(setVolume)
		pvr.XBMCInterface.XBMC_SetVolume(setVolume)

		#setvolume_query = '{"jsonrpc": "2.0", "method": "Application.SetVolume", "params": {"volume": %d}, "id": 1}' % setVolume
 		#xbmc.executeJSONRPC ( setvolume_query )

		xmlstr = ''
		xmlstr += '<?xml version="1.0" encoding="UTF-8"?>'
		xmlstr += '<e2remotecontrol>'
		xmlstr += '	<e2result>True</e2result>'
		xmlstr += '	<e2resulttext>Volume Up</e2resulttext>'
		xmlstr += '</e2remotecontrol>'

		return xmlstr

		
	def ChannelControl( self, control ) :
		status = self.mDataCache.Player_GetStatus( )
		if status.mMode == ElisEnum.E_MODE_PVR :
			return self.xmlError()

		if control == "down" :
		
			prevChannel = None
			prevChannel = self.mDataCache.Channel_GetPrev( self.mDataCache.Channel_GetCurrent( ) ) #self.mCommander.Channel_GetPrev( )
			if prevChannel :
				self.mDataCache.Channel_SetCurrent( prevChannel.mNumber, prevChannel.mServiceType, None, True )			
				self.mDataCache.SetAVBlankByChannel( prevChannel )
				"""
				self.Close( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
				#WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetPincodeRequest( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
				"""
				xmlstr = ''
				xmlstr += '<?xml version="1.0" encoding="UTF-8"?>'
				xmlstr += '<e2remotecontrol>'
				xmlstr += '	<e2result>True</e2result>'
				xmlstr += '	<e2resulttext>Channel Down</e2resulttext>'
				xmlstr += '</e2remotecontrol>'

				return xmlstr

		if control == "up" :
			
			nextChannel = None
			nextChannel = self.mDataCache.Channel_GetNext( self.mDataCache.Channel_GetCurrent( ) )
			if nextChannel :
				self.mDataCache.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType, None, True )
				self.mDataCache.SetAVBlankByChannel( nextChannel )
				"""
				self.Close( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
				#WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetPincodeRequest( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
				"""
				xmlstr = ''
				xmlstr += '<?xml version="1.0" encoding="UTF-8"?>'
				xmlstr += '<e2remotecontrol>'
				xmlstr += '	<e2result>True</e2result>'
				xmlstr += '	<e2resulttext>Channel Down</e2resulttext>'
				xmlstr += '</e2remotecontrol>'

				return xmlstr
											
		return self.xmlError()
			