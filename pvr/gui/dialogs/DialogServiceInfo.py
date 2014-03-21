from pvr.gui.WindowImport import *


CONTROL_ID_LABEL_VIDEO_PID			= 400
CONTROL_ID_LABEL_AUDIO_PID			= 401
CONTROL_ID_LABEL_PCR_PID			= 402
CONTROL_ID_LABEL_TSID				= 403
CONTROL_ID_LABEL_ONID				= 404
CONTROL_ID_LABEL_SID				= 405

CONTROL_ID_LABEL_STRENTH			= 500
CONTROL_ID_LABEL_QUALITY			= 501

CONTROL_ID_LABEL_RESOLUTION			= 502
CONTROL_ID_LABEL_AUDIO				= 503

CONTROL_ID_LABEL_VIDEO_PID_VALUE	= 4000
CONTROL_ID_LABEL_AUDIO_PID_VALUE	= 4001
CONTROL_ID_LABEL_PCR_PID_VALUE		= 4002
CONTROL_ID_LABEL_TSID_VALUE			= 4003
CONTROL_ID_LABEL_ONID_VALUE			= 4004
CONTROL_ID_LABEL_SID_VALUE			= 4005

CONTROL_ID_LABEL_STRENTH_VALUE		= 5000
CONTROL_ID_LABEL_QUALITY_VALUE		= 5001
CONTROL_ID_LABEL_RESOLUTION_VALUE	= 5002
CONTROL_ID_LABEL_AUDIO_VALUE		= 5003


class DialogServiceInfo( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mCtrlStrength	= None
		self.mCtrlQuality	= None
		self.mChannel		= None


	def onInit( self ) :
		self.setProperty( 'DialogDrawFinished', 'False' )

		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mEventBus.Register( self )

		self.mCtrlStrength	= self.getControl( CONTROL_ID_LABEL_STRENTH_VALUE )
		self.mCtrlQuality	= self.getControl( CONTROL_ID_LABEL_QUALITY_VALUE )

		# string
		self.getControl( CONTROL_ID_LABEL_VIDEO_PID ).setLabel( '%s :' % MR_LANG( 'VIDEO PID' ) )
		self.getControl( CONTROL_ID_LABEL_AUDIO_PID ).setLabel( '%s :' % MR_LANG( 'AUDIO PID' ) )
		self.getControl( CONTROL_ID_LABEL_PCR_PID ).setLabel( '%s :' % MR_LANG( 'PCR PID' ) )
		self.getControl( CONTROL_ID_LABEL_TSID ).setLabel( '%s :' % MR_LANG( 'TSID' ) )
		self.getControl( CONTROL_ID_LABEL_ONID ).setLabel( '%s :' % MR_LANG( 'ONID' ) )
		self.getControl( CONTROL_ID_LABEL_SID ).setLabel( '%s :' % MR_LANG( 'SID' ) )
		self.getControl( CONTROL_ID_LABEL_STRENTH ).setLabel( '%s :' % MR_LANG( 'STRENGTH' ) )
		self.getControl( CONTROL_ID_LABEL_QUALITY ).setLabel( '%s :' % MR_LANG( 'QUALITY' ) )
		self.getControl( CONTROL_ID_LABEL_RESOLUTION ).setLabel( '%s :' % MR_LANG( 'VIDEO RESOLUTION' ) )
		self.getControl( CONTROL_ID_LABEL_AUDIO ).setLabel( '%s :' % MR_LANG( 'AUDIO' ) )

		#value '0x%0.4X(%s)'  '%s(0x%0.4X)'
		self.getControl( CONTROL_ID_LABEL_VIDEO_PID_VALUE ).setLabel( '%s (0x%0.4X)' % ( self.mCommander.Channel_GetVideoPid( ), self.mCommander.Channel_GetVideoPid( ) ) )
		self.getControl( CONTROL_ID_LABEL_AUDIO_PID_VALUE ).setLabel( '%s (0x%0.4X)' % ( self.mCommander.Channel_GetAudioPid( ), self.mCommander.Channel_GetAudioPid( ) ) )
		self.getControl( CONTROL_ID_LABEL_PCR_PID_VALUE ).setLabel( '%s (0x%0.4X)' % ( self.mCommander.Channel_GetPCRPid( ), self.mCommander.Channel_GetPCRPid( ) ) )
		self.getControl( CONTROL_ID_LABEL_TSID_VALUE ).setLabel( '%s (0x%0.4X)' % ( self.mChannel.mTsid, self.mChannel.mTsid ) )
		self.getControl( CONTROL_ID_LABEL_ONID_VALUE ).setLabel( '%s (0x%0.4X)' % ( self.mChannel.mOnid, self.mChannel.mOnid ) )
		self.getControl( CONTROL_ID_LABEL_SID_VALUE ).setLabel( '%s (0x%0.4X)' % ( self.mChannel.mSid, self.mChannel.mSid ) )

		tun = self.mCommander.Channel_GetTuningStatus( )
		if tun :
			self.mCtrlStrength.setLabel( '%s%%' % tun[0].mParam )
			self.mCtrlQuality.setLabel( '%s%%' % tun[1].mParam )

		#self.getControl( CONTROL_ID_LABEL_RESOLUTION_VALUE ).setLabel( '%s' % ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetPropString( ) )
		res = self.mCommander.VideoIdentified_GetStatus( )
		if res and res.mParam :
			self.getControl( CONTROL_ID_LABEL_RESOLUTION_VALUE ).setLabel( '%s' % res.mParam )
		else :
			self.getControl( CONTROL_ID_LABEL_RESOLUTION_VALUE ).setLabel( MR_LANG( 'Unknown' ) )
		
		audioIndex = self.mCommander.Audiotrack_GetSelectedIndex( )
		audioValue = self.mCommander.Audiotrack_Get( audioIndex )
		label = '%s-%s' % ( audioValue.mName, audioValue.mLang )
		if audioValue.mName == '' :
			label = 'Stereo-%s' % audioValue.mLang
		elif audioValue.mLang == '' :
			label = '%s' % audioValue.mName
		elif audioValue.mName == '' and audioValue.mLang == '' :
			label = MR_LANG( 'Unknown' )
		self.getControl( CONTROL_ID_LABEL_AUDIO_VALUE ).setLabel( '%s' % label )

		self.setProperty( 'DialogDrawFinished', 'True' )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU :	
			self.Close( )
			
		elif actionId == Action.ACTION_PARENT_DIR :
			self.Close( )


	def onClick( self, aControlId ) :
		pass


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowDialogId( ) :
			if aEvent.getName( ) == ElisEventTuningStatus.getName( ) :
				self.SetTuningStatus( aEvent )


	def SetTuningStatus( self, aEvent ) :
		print 'dhkim test strength=%s quality=%s locked=%s' % ( aEvent.mSignalStrength, aEvent.mSignalQuality, aEvent.mIsLocked )
		if aEvent.mIsLocked :
			self.mCtrlStrength.setLabel( '%s%%' % aEvent.mSignalStrength )
			self.mCtrlQuality.setLabel( '%s%%' % aEvent.mSignalQuality )
		else :
			self.mCtrlStrength.setLabel( '%s%%' % 0 )
			self.mCtrlQuality.setLabel( '%s%%' % 0 )


	def SetChannel( self, aChannel ) :
		self.mChannel = aChannel


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.CloseDialog( )

