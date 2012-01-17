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
		self.mFavoriteEdit = ''
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
		LOG_TRACE( 'onClick control[%s] getGroup[%s]'% (aControlId, id) )

		if id == E_DialogSpinEx01 :
			self.mIdxFavoriteGroup = self.GetSelectedIndex( E_DialogSpinEx01 )

		elif id >= E_DialogInput01 and id <= E_DialogInput09 :

			if self.mMode == FLAG_OPT_GROUP :
				self.SetDialogGroup( id )

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


	def DrawItem( self ) :
		self.ResetAllControl( )

		if self.mMode == FLAG_OPT_LIST :
			#not visible group

			self.AddInputControl( E_DialogInput01, Msg.Strings( MsgId.LANG_LOCK ),     '' )
			self.AddInputControl( E_DialogInput02, Msg.Strings( MsgId.LANG_UNLOCK ),   '' )
			self.AddInputControl( E_DialogInput03, Msg.Strings( MsgId.LANG_SKIP ),     '' )
			self.AddInputControl( E_DialogInput04, Msg.Strings( MsgId.LANG_UNSKIP ),   '' )
			self.AddInputControl( E_DialogInput05, Msg.Strings( MsgId.LANG_DELETE ),   '' )
			self.AddInputControl( E_DialogInput06, Msg.Strings( MsgId.LANG_UNDELETE ), '' )
			self.AddInputControl( E_DialogInput07, Msg.Strings( MsgId.LANG_MOVE ),     '' )

			if len(self.mFavoriteList) > 0 :
				self.AddUserEnumControl( E_DialogSpinEx01, Msg.Strings( MsgId.LANG_ADD_TO_FAV ), self.mFavoriteList, 0)
				self.AddInputControl( E_DialogInput08, '', Msg.Strings( MsgId.LANG_ADD_OK ) )
			else :
				self.AddInputControl( E_DialogInput08, Msg.Strings( MsgId.LANG_ADD_TO_FAV ), Msg.Strings( MsgId.LANG_NONE ) )
				self.SetEnableControl( E_DialogInput08, False )


		elif self.mMode == FLAG_OPT_GROUP :
			#unused visible false
			self.SetVisibleControl( E_DialogInput04, False )
			self.SetVisibleControl( E_DialogInput05, False )
			self.SetVisibleControl( E_DialogInput06, False )
			self.SetVisibleControl( E_DialogInput07, False )
			self.SetVisibleControl( E_DialogInput08, False )

			#visible group only
			self.AddInputControl( E_DialogInput01, Msg.Strings( MsgId.LANG_CREATE_NEW_GROUP ), '' )

			if len(self.mFavoriteList) > 0 :
				self.AddUserEnumControl( E_DialogSpinEx01, Msg.Strings( MsgId.LANG_RENAME_FAV ), self.mFavoriteList, 0)
				self.AddInputControl( E_DialogInput02, '', Msg.Strings( MsgId.LANG_RENAME_OK ) )
				self.AddUserEnumControl( E_DialogSpinEx02, Msg.Strings( MsgId.LANG_DELETE_FAV ), self.mFavoriteList, 0)
				self.AddInputControl( E_DialogInput03, '', Msg.Strings( MsgId.LANG_DELETE_OK ) )

				#unused visible false
				self.SetVisibleControl( E_DialogInput04, False )
				self.SetVisibleControl( E_DialogInput05, False )
				self.SetVisibleControl( E_DialogInput06, False )
				self.SetVisibleControl( E_DialogInput07, False )
				self.SetVisibleControl( E_DialogInput08, False )
			else :
				self.AddInputControl( E_DialogInput02, Msg.Strings( MsgId.LANG_RENAME_FAV ), Msg.Strings( MsgId.LANG_NONE ) )
				self.AddInputControl( E_DialogInput03, Msg.Strings( MsgId.LANG_DELETE_FAV ), Msg.Strings( MsgId.LANG_NONE ) )
				self.SetEnableControl( E_DialogInput02, False )
				self.SetEnableControl( E_DialogInput03, False )

				#unused visible false
				self.SetVisibleControl( E_DialogSpinEx01, False )
				self.SetVisibleControl( E_DialogSpinEx02, False )


		#self.AddOkCanelButton( )
		self.SetAutoHeight( True )
		self.InitControl()

	def SetDialogGroup( self, aFocusId ) :
		LOG_TRACE( 'Enter' )

		label = ''
		if aFocusId == E_DialogInput03 :
			#delete
			idx = self.GetSelectedIndex( E_DialogSpinEx02 )
			name = self.mFavoriteList[idx]
			self.mFavoriteEdit = name

			label = 'delete'

		else :
			title = self.mDialogTitle
			default = ''

			if aFocusId == E_DialogInput01 :
				#create
				default = ''
				result = default

				label = 'create'

			elif aFocusId == E_DialogInput02 :
				#rename
				idx = self.GetSelectedIndex( E_DialogSpinEx01 )
				default = self.mFavoriteList[idx]
				result = '%d'%idx+':'+default+':'

				label = 'rename'

			kb = xbmc.Keyboard( default, title, False )
			kb.doModal()

			name = ''
			name = kb.getText()
			if name :
				self.mFavoriteEdit = result + name

		LOG_TRACE( '========%s[%s]'% (label,self.mFavoriteEdit) )
		LOG_TRACE( 'Leave' )


	def IsOK( self ) :
		return self.mIsOk

	def GetValue( self, aFlag ) :

		if aFlag == FLAG_OPT_LIST :
			LOG_TRACE('FavoriteGroup idx[%s] isOk[%s]' % ( self.mIdxFavoriteGroup, self.mIsOk ) )
			return self.mIdxDialog, self.mIdxFavoriteGroup, self.mIsOk
		elif aFlag == FLAG_OPT_GROUP :
			LOG_TRACE('FavoriteGroupEdit[%s] isOk[%s]' % ( self.mFavoriteEdit, self.mIsOk ) )
			return self.mIdxDialog, self.mFavoriteEdit, self.mIsOk

	def SetValue( self, aMode, aTitle, aFavoriteGroup = [] ) :
		self.mMode = aMode
		self.mDialogTitle = aTitle
		self.mFavoriteList = aFavoriteGroup

		LOG_TRACE( '======================title[%s] favoriteList[%s] len[%s]'% (self.mDialogTitle, self.mFavoriteList, len(self.mFavoriteList)) )
		
