import xbmc
import xbmcgui
import time
import sys

import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.BaseDialog import SettingDialog
from pvr.gui.BaseWindow import Action
from ElisEnum import ElisEnum
from ElisProperty import ElisPropertyEnum
from pvr.gui.GuiConfig import *

from pvr.Util import LOG_WARN, LOG_TRACE, LOG_ERR

"""
E_DIALOG_HEADER			= 100

E_BUTTON_OK_ID			= 501
E_BUTTON_CANCEL_ID		= 601
"""

class DialogEditChannelList( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		LOG_TRACE( 'args[0]=[%s]' % args[0] )
		LOG_TRACE( 'args[1]=[%s]' % args[1] )

		self.mIsOk = False
		self.mIdxDialog = 0
		self.mIdxFavoriteGroup = 0
		self.mFavoriteList = []
		self.mDialogTitle = ''

	def onInit( self ) :

		self.SetHeaderLabel( self.mDialogTitle )
		self.DrawItem()
		self.mIsOk = False


	def onAction( self, aAction ) :
		actionId = aAction.getId()

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.ResetAllControl()
			self.CloseDialog()
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl()
			self.CloseDialog()

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft()

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight()
			
		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp()
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown()


	def onClick( self, aControlId ) :
		self.mIdxDialog = id = self.GetGroupId( aControlId )

		if id == E_DialogSpinEx01 :
			self.mIdxFavoriteGroup = self.GetSelectedIndex( E_DialogSpinEx01 )

		elif id >= E_DialogInput01 and id <= E_DialogInput09 :
			self.ResetAllControl()
			self.CloseDialog()

		"""
		elif id == E_SettingDialogOk :
			self.mIsOk = True
			self.ResetAllControl()
			self.CloseDialog()

		elif id == E_SettingDialogCancel :
			self.mIsOk = False
			self.ResetAllControl()
			self.CloseDialog()
		"""

 				
	def onFocus( self, aControlId ):
		pass


	def IsOK( self ) :
		return self.mIsOk

	def GetValue( self ) :

		LOG_TRACE('FavoriteGroup idx[%s] isOk[%s]' % ( self.mIdxFavoriteGroup, self.mIsOk ) )
		return self.mIdxDialog, self.mIdxFavoriteGroup, self.mIsOk


	def DrawItem( self ) :
		self.ResetAllControl( )


		self.AddLeftLabelButtonControl( E_DialogInput01, 'Lock' )
		self.AddLeftLabelButtonControl( E_DialogInput02, 'UnLock' )
		self.AddLeftLabelButtonControl( E_DialogInput03, 'Skip' )
		self.AddLeftLabelButtonControl( E_DialogInput04, 'UnSkip' )
		self.AddLeftLabelButtonControl( E_DialogInput05, 'Delete' )
		self.AddLeftLabelButtonControl( E_DialogInput06, 'UnDelete' )
		self.AddLeftLabelButtonControl( E_DialogInput07, 'Move' )
		self.AddLeftLabelButtonControl( E_DialogInput08, 'Create New Group' )
		self.AddUserEnumControl( E_DialogSpinEx01, 'Rename Fav.Group', self.mFavoriteList, 0)
		self.AddUserEnumControl( E_DialogSpinEx02, 'Delete Fav.Group', self.mFavoriteList, 0)
		self.AddUserEnumControl( E_DialogSpinEx03, 'Add to Fav.Group', self.mFavoriteList, 0)
		self.AddLeftLabelButtonControl( E_DialogInput09, 'Select Add to Fav.Group' )

		if len(self.mFavoriteList) < 1 :
			self.SetVisibleControl( E_DialogSpinEx03, False )
			self.AddLeftLabelButtonControl( E_DialogInput09, 'None' )


		if aMode == FLAG_OPT_LIST :
			#not visible group
			self.SetVisibleControl( E_DialogInput08, False )
			self.SetVisibleControl( E_DialogSpinEx01, False )
			self.SetVisibleControl( E_DialogSpinEx02, False )

		elif aMode == FLAG_OPT_GROUP :
			#visible group only
			self.SetVisibleControl( E_DialogInput01, False )
			self.SetVisibleControl( E_DialogInput02, False )
			self.SetVisibleControl( E_DialogInput03, False )
			self.SetVisibleControl( E_DialogInput04, False )
			self.SetVisibleControl( E_DialogInput05, False )
			self.SetVisibleControl( E_DialogInput06, False )
			self.SetVisibleControl( E_DialogInput07, False )
			self.SetVisibleControl( E_DialogInput08, True )
			self.SetVisibleControl( E_DialogSpinEx01, True )
			self.SetVisibleControl( E_DialogSpinEx02, True )
			self.SetVisibleControl( E_DialogSpinEx03, False )
			self.SetVisibleControl( E_DialogInput09, False )


		#self.AddOkCanelButton( )

		self.InitControl( )


	def SetValue( self, aMode, aTitle, aClassListFavorite ) :
		self.mDialogTitle = aTitle

		self.mFavoriteList = []
		for item in aClassListFavorite:
			self.mFavoriteList.append( item.mGroupName )

		LOG_TRACE( '======================title[%s] favoriteList[%s]'% (self.mDialogTitle, self.mFavoriteList) )
		
