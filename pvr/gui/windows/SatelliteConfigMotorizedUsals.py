import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.TunerConfigMgr as ConfigMgr
import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import SettingWindow, Action
from ElisProperty import ElisPropertyInt


E_LIST_MY_LONGITUDE = [ 'E', 'W' ]
E_LIST_MY_LATITUDE  = [ 'N', 'S' ]


class SatelliteConfigMotorizedUsals( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.IsWest = 0
		self.IsSouth = 0
		self.mLongitude	= 0
		self.mLatitude	= 0


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		tunerIndex = ConfigMgr.GetInstance( ).GetCurrentTunerIndex( )
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'USALS configuration : Tuner %s' % ( tunerIndex + 1 ) )
	
		self.SetHeaderLabel( 'Motorize Configuration' )
		self.SetFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )
		self.InitConfig( )

		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )
			
		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )


	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )

		"""
		# My Longitude
		if groupId == E_Input01 :
			pass

		# My Latitude
		elif groupId == E_Input02 :
			pass
		"""
		
		# Set Longitude
		if groupId == E_Input01 :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_SATELLITE_NUMERIC )
 			dialog.SetProperty( 'My Longitude', 0 )
 			dialog.doModal( )

		# Set Latitude
		elif groupId == E_Input02 :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_SATELLITE_NUMERIC )
 			dialog.SetProperty( 'My Longitude', 1799 )
 			dialog.doModal( )
			
		# Reference Position to Null
		elif groupId == E_Input03 :
			pass
			
		# Configure Satellites
		elif groupId == E_Input04 :
			self.ResetAllControl( )
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_TUNER_CONFIGURATION )
			
	def onFocus( self, controlId ) :
		pass


	def InitConfig( self ) :
		self.ResetAllControl( )

		self.GetLongitude( )
		tmplongitude1 = '%d %s' % ( self.mLongitude, E_LIST_MY_LONGITUDE[ 0 ] )
		tmplongitude2 = '%d %s' % ( self.mLongitude, E_LIST_MY_LONGITUDE[ 1 ] )
		tmpListLongitude = [ tmplongitude1, tmplongitude2 ]
		self.AddUserEnumControl( E_SpinEx01, 'My Longitude', tmpListLongitude, self.IsWest )
		self.AddLeftLabelButtonControl( E_Input01, ' - Set Longitude' )
		
		self.GetLatitude( )
		tmplatitude1 = '%d %s' % ( self.mLatitude, E_LIST_MY_LATITUDE[ 0 ] )
		tmplatitude2 = '%d %s' % ( self.mLatitude, E_LIST_MY_LATITUDE[ 1 ] )
		tmpListLatitude = [ tmplatitude1, tmplatitude2 ]
		self.AddUserEnumControl( E_SpinEx02, 'My Latitude', tmpListLatitude, self.IsSouth )
		self.AddLeftLabelButtonControl( E_Input02, ' - Set Latitude' )
		
		self.AddLeftLabelButtonControl( E_Input03, 'Reference Position to Null' )
		self.AddLeftLabelButtonControl( E_Input04, 'Configure Satellites' )

		self.InitControl( )

	def GetLongitude( self ) :
		self.IsWest = 0
		self.mLongitude = ElisPropertyInt( 'MyLongitude', self.mCommander ).GetProp( )
		
		if self.mLongitude > 1800 :
			self.mLongitude = 3600 - 1800
			self.IsWest = 1
			

	def GetLatitude( self ) :
		self.IsSouth = 0
		self.mLatitude = ElisPropertyInt( 'MyLatitude', self.mCommander ).GetProp( )
		
		if self.mLatitude > 1800 :
			self.mLatitude = 3600 - 1800
			self.IsSouth = 1


	def SetLongitude( self ) :
		pass


	def SetLatitude( self ) :
		pass
			