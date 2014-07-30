from pvr.gui.WindowImport import *

class ExclusiveSettings( object ) :
	def __init__( self ) :
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )


	def Configure( self ) :
		self.ShowContextMenu( )


	def ShowContextMenu( self ) :
		context = []
		defSelect = ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).GetProp( )
		#deviceList = [MR_LANG( 'None' ), MR_LANG( 'Micro SD Card' ), MR_LANG( 'USB Storage' ), MR_LANG( 'Exclusive HDD' )]
		deviceList = ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).mProperty

		selectItem = -1
		itemCount = -1
		for i in range( len( deviceList ) ) :
			if i == 1 or i == 3 :
				itemCount += 1
				deviceName = deviceList[i][1]
				if i == defSelect :
					selectItem = itemCount
					deviceName = '[COLOR ff2E2E2E]%s[/COLOR]'% deviceName
				context.append( ContextItem( deviceName, i ) )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context, selectItem )
 		dialog.doModal( )


		selectAction = dialog.GetSelectedAction( )
		if selectAction < 0 :
			LOG_TRACE( '[Exclusive] cancel, previous back' )
			return

		if selectAction == defSelect :
			LOG_TRACE( '[Exclusive] pass, select same' )
			return

		ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).SetPropIndex( selectAction )
		LOG_TRACE( '--------------------select[%s]'% deviceList[selectAction][1] )


