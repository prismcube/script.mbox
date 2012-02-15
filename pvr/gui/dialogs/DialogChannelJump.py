import xbmc
import xbmcgui
import time
import sys

from pvr.gui.BaseDialog import BaseDialog
from pvr.gui.BaseWindow import Action

E_CHANNEL_NUM_ID	= 210
E_CHANNEL_NAME_ID	= 211
E_EPG_NAME_ID		= 212
E_PROGRESS_ID		= 213

class DialogChannelJump( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mChannelNumber		= ''
		#self.mChannelName		= 'No channel'
		#self.mEPGName			= ''
		self.mCtrlChannelNum	= None
		self.mCtrlChannelName	= None
		self.mCtrlEPGName		= None
		self.mCtrlProgress		= None

		self.mMaxChannelNum		= 9999


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlChannelNum	= self.getControl( E_CHANNEL_NUM_ID )
		self.mCtrlChannelName	= self.getControl( E_CHANNEL_NAME_ID )
		self.mCtrlEPGName		= self.getControl( E_EPG_NAME_ID )
		self.mCtrlProgress		= self.getControl( E_PROGRESS_ID )

		self.SetLabelChannelNumber( )
		self.SetLabelChannelName( )
				
	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
			
		elif actionId == Action.ACTION_PARENT_DIR :
			self.CloseDialog( )

		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :
			inputString = '%d' % ( actionId - Action.REMOTE_0 )
			self.mChannelNumber += inputString
			self.mChannelNumber = '%d' % int( self.mChannelNumber )
			if int( self.mChannelNumber ) > self.mMaxChannelNum :
				self.mChannelNumber = inputString
			self.SetLabelChannelNumber( )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			inputNum = actionId - Action.ACTION_JUMP_SMS2 + 2
			if inputNum >= 2 and inputNum <= 9 :
				inputString = '%d' % inputNum
				self.mChannelNumber += inputString
				self.mChannelNumber = '%d' % int( self.mChannelNumber )
				if int( self.mChannelNumber ) > self.mMaxChannelNum :
					self.mChannelNumber = inputString
				self.SetLabelChannelNumber( )


	def onClick( self, aControlId ) :
		if aControlId == E_BUTTON_OK :
			self.CloseDialog( )


	def onFocus( self, aControlId ) :
		pass

		
	def SetDialogProperty( self, aChannelFirstNum, aMaxChannelNum ) :
		self.mChannelNumber	= aChannelFirstNum
		self.mMaxChannelNum = aMaxChannelNum


	def SetLabelChannelNumber( self ) :
		self.mCtrlChannelNum.setLabel( self.mChannelNumber )


	def SetLabelChannelName( self, aChannelName='No Channel' ) :
		self.mCtrlChannelName.setLabel( aChannelName )


	def SetLabelEPGName( self, aEPGName='' ) :
		self.mCtrlEPGName.setLabel( aEPGName )


	def SetPogress( self, aPercent ) :
		self.mCtrlProgress.setPercent( aPercent )
		
