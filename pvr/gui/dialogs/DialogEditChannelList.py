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
import pvr.Msg as Msg
import pvr.gui.windows.Define_string as MsgId

"""
E_DIALOG_HEADER			= 100

E_BUTTON_OK_ID			= 501
E_BUTTON_CANCEL_ID		= 601
"""
FLAG_OPT_LIST  = 0
FLAG_OPT_GROUP = 1


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
		self.mMode = FLAG_OPT_LIST

	def onInit( self ) :

		self.mCtrlImgBox            = self.getControl( 9001 )

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

		if self.mMode == FLAG_OPT_LIST :
			#not visible group

			self.AddLeftLabelButtonControl( E_DialogInput01, Msg.Strings( MsgId.LANG_LOCK )     )
			self.AddLeftLabelButtonControl( E_DialogInput02, Msg.Strings( MsgId.LANG_UNLOCK )   )
			self.AddLeftLabelButtonControl( E_DialogInput03, Msg.Strings( MsgId.LANG_SKIP )     )
			self.AddLeftLabelButtonControl( E_DialogInput04, Msg.Strings( MsgId.LANG_UNSKIP )   )
			self.AddLeftLabelButtonControl( E_DialogInput05, Msg.Strings( MsgId.LANG_DELETE )   )
			self.AddLeftLabelButtonControl( E_DialogInput06, Msg.Strings( MsgId.LANG_UNDELETE ) )
			self.AddLeftLabelButtonControl( E_DialogInput07, Msg.Strings( MsgId.LANG_MOVE )     )

			if len(self.mFavoriteList) > 0 :
				self.AddUserEnumControl( E_DialogSpinEx01, Msg.Strings( MsgId.LANG_ADD_TO_FAV ), self.mFavoriteList, 0)
				self.AddInputControl( E_DialogInput08, '', Msg.Strings( MsgId.LANG_ADD_OK ) )
			else :
				self.AddInputControl( E_DialogInput08, Msg.Strings( MsgId.LANG_ADD_TO_FAV ), Msg.Strings( MsgId.LANG_NONE ) )


		elif self.mMode == FLAG_OPT_GROUP :
			#visible group only

			self.AddLeftLabelButtonControl( E_DialogInput01, Msg.Strings( MsgId.LANG_CREATE_NEW_GROUP ) )
			self.AddUserEnumControl( E_DialogSpinEx01, Msg.Strings( MsgId.LANG_RENAME_FAV ), self.mFavoriteList, 0)
			self.AddInputControl( E_DialogInput02, '', Msg.Strings( MsgId.LANG_RENAME_OK ) )
			self.AddUserEnumControl( E_DialogSpinEx02, Msg.Strings( MsgId.LANG_DELETE_FAV ), self.mFavoriteList, 0)
			self.AddInputControl( E_DialogInput03, '', Msg.Strings( MsgId.LANG_DELETE_OK ) )


		#self.AddOkCanelButton( )
		self.SetAutoHeight( True )
		self.InitControl()


	def SetValue( self, aMode, aTitle, aClassListFavorite ) :
		self.mMode = aMode
		self.mDialogTitle = aTitle

		self.mFavoriteList = []
		for item in aClassListFavorite:
			self.mFavoriteList.append( item.mGroupName )

		LOG_TRACE( '======================title[%s] favoriteList[%s] len[%s]'% (self.mDialogTitle, self.mFavoriteList, len(self.mFavoriteList)) )
		
