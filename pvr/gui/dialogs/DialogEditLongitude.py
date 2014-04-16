from pvr.gui.WindowImport import *
import pvr.ScanHelper as ScanHelper
#import pvr.TunerConfigMgr as ConfigMgr

E_PLUS_1					= 0
E_MINUS_1					= 1
E_PLUS_10					= 2
E_MINUS_10					= 3
E_SET_WEST					= 4
E_SET_EAST					= 5
E_RESET						= 6
E_APPLY						= 7

E_PLUS_100					= 996
E_MINUS_100					= 997
E_PLUS_1000					= 998
E_MINUS_1000				= 999

DIALOG_MAIN_GROUP_ID		= 9000
DIALOG_WIDTH				= 370

DIALOG_MIDDLE_IMAGE_ID		= 100
DIALOG_BOTTOM_IMAGE_ID		= 101

DIALOG_LIST_ID				= 102
DIALOG_LONGITUDE_LABEL_ID	= 103


class DialogEditLongitude( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		#self.mTunerIndex	= E_TUNER_1
		self.mListItems		= []
		self.mCtrlList		= None
		self.mCtrlLongitude = None
		#self.mLongitude		= 0
		self.mCursor		= 0
		self.mIsOk			= E_DIALOG_STATE_NO
		self.mInput1		= 0
		self.mInput2		= 0
		self.mInput3		= 0
		self.mInput4		= 0
		self.mDir			= E_WEST

		self.mLongitudeBackup = 0
		self.mDirectionBackup = E_WEST

		self.mConfigureSatellite 	= None
		self.mConfigureTransponder	= None
		self.mWindowObject			= None
		

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.setProperty( 'DialogDrawFinished', 'False' )
		self.mIsOk = E_DIALOG_STATE_NO
		self.mCursor = 0

		#self.mTunerIndex = ConfigMgr.GetInstance( ).GetCurrentTunerNumber( )
		self.mCtrlLongitude = self.getControl( DIALOG_LONGITUDE_LABEL_ID )
		self.SetInputLabel( )

		context = [ '+ 0.1', '- 0.1', '+ 1', '- 1', MR_LANG( 'Switch to West' ), MR_LANG( 'Switch to East' ), MR_LANG( 'Reset' ), MR_LANG( 'Apply' ) ]
		icon = [ 'OSDPlayNF.png', 'OSDPlayNF_Rotated.png', 'OSDForwardNF.png', 'OSDRewindNF.png' ]

		itemHeight = int( self.getProperty( 'ItemHeight' ) )

		self.mListItems = []

		# Set Menu and Icons
		for i in range( len( context ) ) :
			item = xbmcgui.ListItem( context[i] )
			if i < len( icon ) :
				item.setProperty( 'HotKey', icon[i] )
			self.mListItems.append( item )

		self.mCtrlList = self.getControl( DIALOG_LIST_ID )
		self.mCtrlList.addItems( self.mListItems )

		# Set Dialog Size
		height = 8 * itemHeight + 35
		self.getControl( DIALOG_MIDDLE_IMAGE_ID ).setHeight( height )

		# Set Dialog Bottom Image
		middle_y, empty = self.getControl( DIALOG_MIDDLE_IMAGE_ID ).getPosition( )
		middley_height = self.getControl( DIALOG_MIDDLE_IMAGE_ID ).getHeight( )
		self.getControl( DIALOG_BOTTOM_IMAGE_ID ).setPosition( 0, middle_y + middley_height )

		# Set Center Align
		start_x = E_WINDOW_WIDTH / 2 - DIALOG_WIDTH / 2
		start_y = E_WINDOW_HEIGHT / 2 - middley_height / 2
		self.getControl( DIALOG_MAIN_GROUP_ID ).setPosition( start_x, start_y )

		self.setFocusId( DIALOG_LIST_ID )

		self.setProperty( 'DialogDrawFinished', 'True' )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.CloseDialog( )

		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :		# number
			self.InputControl( actionId, 1 )
			self.SetInputLabel( )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			self.InputControl( actionId, 2 )
			self.SetInputLabel( )
			
		elif actionId == Action.ACTION_PARENT_DIR : 							# back space
			self.DeleteValue( )
			self.SetInputLabel( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.mCtrlList.selectItem( E_PLUS_1 )
			self.SetLongitudeValue( E_PLUS_1 )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.mCtrlList.selectItem( E_MINUS_1 )
			self.SetLongitudeValue( E_MINUS_1 )

		elif actionId == Action.ACTION_MBOX_FF :
			self.mCtrlList.selectItem( E_PLUS_10 )
			self.SetLongitudeValue( E_PLUS_10 )

		elif actionId == Action.ACTION_MBOX_REWIND :
			self.mCtrlList.selectItem( E_MINUS_10 )
			self.SetLongitudeValue( E_MINUS_10 )


	def onClick( self, aControlId ) :
		selectedIndex = self.mCtrlList.getSelectedPosition( )
		self.SetLongitudeValue( selectedIndex )


	def onFocus( self, aControlId ) :
		pass


	def SetLongitudeValue( self, aSelectedIndex ) :
		if aSelectedIndex == E_PLUS_1 :
			if self.mInput4 == 9 :
				self.mInput4 = 0
				self.SetLongitudeValue( E_PLUS_10 )
				return
			else :
				self.mInput4 += 1
			self.SetInputLabel( )

		elif aSelectedIndex == E_MINUS_1 :
			if self.mInput4 == 0 :
				self.mInput4 = 9
				self.SetLongitudeValue( E_MINUS_10 )
				return
			else :
				self.mInput4 -= 1
			self.SetInputLabel( )

		elif aSelectedIndex == E_PLUS_10 :
			if self.mInput3 == 9 :
				self.mInput3 = 0
				self.SetLongitudeValue( E_PLUS_100 )
				return
			else :
				self.mInput3 += 1
			self.SetInputLabel( )

		elif aSelectedIndex == E_MINUS_10 :
			if self.mInput3 == 0 :
				self.mInput3 = 9
				self.SetLongitudeValue( E_MINUS_100 )
				return
			else :
				self.mInput3 -= 1
			self.SetInputLabel( )

		elif aSelectedIndex == E_PLUS_100 :
			if self.mInput2 == 7 :
				self.mInput2 = 0
				self.SetLongitudeValue( E_PLUS_1000 )
				return
			else :
				self.mInput2 += 1
			self.SetInputLabel( )

		elif aSelectedIndex == E_MINUS_100 :
			if self.mInput2 == 0 :
				self.mInput2 = 7
				self.SetLongitudeValue( E_MINUS_1000 )
				return
			else :
				self.mInput2 -= 1
			self.SetInputLabel( )

		elif aSelectedIndex == E_PLUS_1000 :
			if self.mInput1 == 0 :
				self.mInput1 = 1
				self.SetInputLabel( )

		elif aSelectedIndex == E_MINUS_1000 :
			if self.mInput1 == 1 :
				self.mInput1 = 0
				self.SetLongitudeValue( E_MINUS_1000 )

		elif aSelectedIndex == E_SET_WEST :
			if self.mDir != E_WEST :
				self.mDir = E_WEST
				self.SetInputLabel( )

		elif aSelectedIndex == E_SET_EAST :
			if self.mDir != E_EAST :
				self.mDir = E_EAST
				self.SetInputLabel( )

		elif aSelectedIndex == E_RESET :
			self.SetDialogProperty( self.mLongitudeBackup, self.mDirectionBackup, self.mConfigureSatellite, self.mConfigureTransponder, self.mWindowObject )
			self.SetInputLabel( )

		elif aSelectedIndex == E_APPLY :
			self.mIsOk = E_DIALOG_STATE_YES
			self.CloseDialog( )


	def IsOK( self ) :
		return self.mIsOk


	def GetValue( self ) :
		value = self.mInput1 * 1000 + self.mInput2 * 100 + self.mInput3 * 10 + self.mInput4
		return value, self.mDir


	def SetDialogProperty( self, aValue, aDir, aSatellite, aTransponder, aWin ) :
		self.mLongitudeBackup		= aValue
		self.mDirectionBackup		= aDir
		self.mConfigureSatellite 	= aSatellite
		self.mConfigureTransponder	= aTransponder
		self.mWindowObject			= aWin

		self.mDir = aDir
		self.mInput4 = aValue % 10
		aValue = aValue / 10
		self.mInput3 = aValue % 10
		aValue = aValue / 10
		self.mInput2 = aValue % 10
		aValue = aValue / 10
		self.mInput1 = aValue


	def SetInputLabel( self ) :
		dir = 'E'
		if self.mDir == E_WEST :
			dir = 'W'

		if self.mCursor == 0 :
			tmp = '[COLOR selected]%d[/COLOR]%d%d.%d %s' % ( self.mInput1, self.mInput2, self.mInput3, self.mInput4, dir ) 

		elif self.mCursor == 1 :
			tmp = '%d[COLOR selected]%d[/COLOR]%d.%d %s' % ( self.mInput1, self.mInput2, self.mInput3, self.mInput4, dir ) 

		elif self.mCursor == 2 :
			tmp = '%d%d[COLOR selected]%d[/COLOR].%d %s' % ( self.mInput1, self.mInput2, self.mInput3, self.mInput4, dir ) 

		elif self.mCursor == 3 :
			tmp = '%d%d%d.[COLOR selected]%d[/COLOR] %s' % ( self.mInput1, self.mInput2, self.mInput3, self.mInput4, dir )

		else :
			return

		self.mCtrlLongitude.setLabel( tmp )
		self.mConfigureSatellite.mUSALSLongitude = self.mInput1 * 1000 + self.mInput2 * 100 + self.mInput3 * 10 + self.mInput4
		if self.mDir == E_WEST :
			self.mConfigureSatellite.mUSALSLongitude = 3600 - self.mConfigureSatellite.mUSALSLongitude
		ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self.mWindowObject, self.mConfigureSatellite, self.mConfigureTransponder )


	def InputControl( self, aControlId, aInputtype ) :
		if aInputtype == 0 :
			value = int( self.getControl( aControlId ).getLabel( ) )

		elif aInputtype == 1 :
			tmp = chr( aControlId - 10 )
			value = int( tmp )

		elif aInputtype == 2 :
			tmp = chr( aControlId - 92 )
			value = int( tmp )

		else :
			return

		if self.mCursor == 0 and value < 2 :
			if self.mInput2 > 7 and value != 0 :
				return
			self.mInput1 = value
			self.NextCursor( )

		elif self.mCursor == 1 :
			if self.mInput1 == 1 and value > 7 :
				return
			self.mInput2 = value
			self.NextCursor( )

		elif self.mCursor == 2 :
			self.mInput3 = value
			self.NextCursor( )

		elif self.mCursor == 3 :
			self.mInput4 = value
			self.NextCursor( )

		else :
			return


	def DeleteValue( self ) :
		if self.mCursor == 0 :
			self.mInput1 = 0
			self.PrevCursor( )

		elif self.mCursor == 1 :
			self.mInput2 = 0
			self.PrevCursor( )

		elif self.mCursor == 2 :
			self.mInput3 = 0
			self.PrevCursor( )

		elif self.mCursor == 3 :
			self.mInput4 = 0
			self.PrevCursor( )

		else :
			return


	def NextCursor( self ) :
		if self.mCursor == 3 :
			self.mCursor = 0
		else :
			self.mCursor = self.mCursor + 1


	def PrevCursor( self ) :
		if self.mCursor == 0 :
			self.mCursor = 3
		else :
			self.mCursor = self.mCursor - 1

