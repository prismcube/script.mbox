from pvr.gui.GuiConfig import *
import pvr.ElisMgr


gScanHelper = None


def GetInstance( ) :
	global gScanHelper
	if not gScanHelper :
		gScanHelper = ScanHelper( )
	else:
		pass
	return gScanHelper


class ScanHelper( object ) :
	def __init__( self ) :
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )


	def ScanHelper_Start( self, aWin ) :
		self.mCommander.ScanHelper_Start( )
		aWin.setProperty( 'ViewProgress', 'True' )
		aWin.getControl( E_SCAN_LABEL_STRENGTH ).setLabel( MR_LANG( 'Strength' ) )
		aWin.getControl( E_SCAN_LABEL_QUALITY ).setLabel( MR_LANG( 'Quality' ) )


	def ScanHelper_ChangeContext( self, aWin, aSatellite, aTp ) :
		if aSatellite and aTp :
			self.ScanHerper_Progress( aWin, 0, 0, 0 )
			transpondertemp = []
			transpondertemp.append( aTp )
			satellitetemp = []
			satellitetemp.append( aSatellite )
			self.mCommander.ScanHelper_ChangeContext( transpondertemp, satellitetemp )
		else :
			LOG_ERR( 'ScanHelper_ChangeContext : Satellite or TP is None' )


	def ScanHelper_ChangeContextByCarrier( self, aWin, aTp ) :
		if aTp :
			self.ScanHerper_Progress( aWin, 0, 0, 0 )
			transpondertemp = []
			transpondertemp.append( aTp )
			self.mCommander.ScanHelper_ChangeContextByCarrier( transpondertemp )
		else :
			LOG_ERR( 'ScanHelper_ChangeContextByCarrier : TP is None' )


	def ScanHelper_Stop( self, aWin, aReturn=True ) :
		self.mCommander.ScanHelper_Stop( aReturn )
		aWin.setProperty( 'ViewProgress', 'False' )


	def ScanHerper_Progress( self, aWin, aStrength, aQuality, aLocked ) :
		if aLocked == False :
			aQuality = 0
		else :
			if aQuality > 100 :
				aQuality = 100
			elif aQuality < 0 :
				aQuality = 0
		if aStrength > 100 :
			aStrength = 100
		elif aStrength < 0 :
			aStrength = 0

		aWin.getControl( E_SCAN_HELPER_LABEL_STRENGTH ).setLabel( str( '%s %%' % aStrength ) )
		aWin.getControl( E_SCAN_HELPER_LABEL_QUALITY ).setLabel( str( '%s %%' % aQuality ) )
		
		aWin.getControl( E_SCAN_HELPER_PROGRESS_STRENGTH ).setPercent( aStrength )
		aWin.getControl( E_SCAN_HELPER_PROGRESS_QUALITY ).setPercent( aQuality )

