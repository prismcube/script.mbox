
from pvr.elisevent import ElisEnum
import pvr.elismgr

_propertyMapEnum =[
	[ 'Last ServiceType', ( 1, 'TV' ), ( 2, 'Radio' )],
	[ 'CurrentVoutResolution', ( 1, '480i' ), ( 2, '480p' ), ( 3, '576i' ), ( 4, '576p' ), ( 5, '720p' ), ( 6, '1080i' ), 	( 7, '1080p-25' )],
		
	[ 'First Installation', ( 0, 'Normal' ), ( 0x5a, 'First' ), ( 0x2b, 'FTI' )],
	[ 'Serial kbd', ( 0, 'Off' ), ( 0x1, 'On' )],
	[ 'Wakeup Mode', ( 0, 'Wakeup From RCU' ), ( 1, 'Wakeup from Button' ), ( 2, 'Wakeup from Timer' ), ( 3, 'Wakeup from AC' )],
	[ 'Log Option', ( 0, 'No Log' ), ( 1, 'Log Serial' ), ( 2, 'Log File' )],

	[ 'Video Output', ( 0, 'HDMI / YUV' ), ( 1, 'SCART' )],
	[ 'HDMI Format', ( 2, '1080i' ), ( 0, '576p' ), ( 1, '720p' ), ( 3, 'Automatic' )],

	[ 'Show 4:3', ( 0, 'Normal (Pillarbox)' ), ( 1, 'Stretched (Fullscreen)' ), ( 2, 'Zoom (PanScan)' )],
	[ 'Audio HDMI', ( 0, 'Decoded PCM' ), ( 1, 'S/PDIF Format' )],
	[ 'TV Aspect', ( 0, '16:9' ), ( 1, '4:3' )],
	[ 'Picture 4:3', ( 0, 'Letterbox' ), ( 1, 'Pan & Scan' )],
	[ 'Picture 16:9', ( 0, 'Automatic' ), ( 1, 'Always 16:9' )],

	[ 'Scart TV', ( 0, 'CVBS' ), ( 1, 'RGB' ), ( 2, 'YC' )],
	[ 'Scart VCR', ( 0, 'CVBS' ), ( 1, 'YC' )],

	[ 'Audio Dolby', ( 1, 'Off' ), ( 0, 'On' )],

	[ 'TV System', ( 0, 'PAL' ), ( 1, 'NTSC' )],


	[ 'Audio Language', ( ElisEnum.E_DEUTSCH, 'Deutsch' ), ( ElisEnum.E_ENGLISH, 'English' ),
		( ElisEnum.E_FRENCH, 'Francais' ), ( ElisEnum.E_ITALIAN, 'Italiano' ), ( ElisEnum.E_SPANISH, 'Espanol' ),
		( ElisEnum.E_CZECH, 'Cestina' ), (  ElisEnum.E_DUTCH, 'Nederlands' ), ( ElisEnum.E_POLISH, 'Polski' ),
		( ElisEnum.E_TURKISH, 'Turkce' ), ( ElisEnum.E_RUSSIAN, 'Russian' )],

	[ 'Subtitle Language', ( 0, 'Disable' ), ( ElisEnum.E_DEUTSCH, 'Deutsch' ), ( ElisEnum.E_ENGLISH, 'English' ),
		( ElisEnum.E_FRENCH, 'Francais' ), ( ElisEnum.E_ITALIAN, 'Italiano' ), ( ElisEnum.E_SPANISH, 'Espanol' ),
		( ElisEnum.E_CZECH, 'Cestina' ), (  ElisEnum.E_DUTCH, 'Nederlands' ), ( ElisEnum.E_POLISH, 'Polski' ),
		( ElisEnum.E_TURKISH, 'Turkce' ), ( ElisEnum.E_RUSSIAN, 'Russian' )],

	[ 'Secondary Subtitle Language', ( 0, 'Disable' ), ( ElisEnum.E_DEUTSCH, 'Deutsch' ), ( ElisEnum.E_ENGLISH, 'English' ),
		( ElisEnum.E_FRENCH, 'Francais' ), ( ElisEnum.E_ITALIAN, 'Italiano' ), ( ElisEnum.E_SPANISH, 'Espanol' ),
		( ElisEnum.E_CZECH, 'Cestina' ), (  ElisEnum.E_DUTCH, 'Nederlands' ), ( ElisEnum.E_POLISH, 'Polski' ),
		( ElisEnum.E_TURKISH, 'Turkce' ), ( ElisEnum.E_RUSSIAN, 'Russian' )],

	[ 'Hearing Impaired', ( 0, 'No' ), ( 1, 'Yes' )],

	[ 'Deep Standby', ( 1, 'Off' ), ( 0, 'On' )],
	[ 'Remote Addr', ( 0, 'Addr1' ), ( 1, 'Addr2' ),( 2, 'Addr3' ), ( 3, 'Addr4' )],

	[ 'FPGATest', ( 0, 'Off' ), ( 1, 'On' )],
	[ 'FPGATestMode', ( 0, 'Normal' ), ( 1, 'Number' )],
	[ 'ChannelChangeMode', ( 0, 'Fast' ), ( 1, 'AfterPMT' )],
	[ 'ConaxParingMode', ( 0, 'Off' ), ( 1, 'On' )],


	[ 'CI Default ForceDecrypt', ( 1, 'On' ), ( 0, 'Off' )],
	[ 'CI ForceDecrypt Mode', ( 1, 'Automatic' ), ( 0, 'Manual' )],
	[ 'AlphaCrypt Multiple Decryption', ( 0, 'Off' ), ( 1, 'On' )],
		
	[ 'Tuner2 Connect Type', ( 0, 'Separated' ), ( 1, 'Loopthrough' )],
	[ 'Tuner2 Signal Config', ( 0, 'Same with Tuner 1' ), ( 1, 'Different from Tuner 1' )],

	[ 'Tuner1 Type', ( 0, 'Simple LNB' ), ( 1, 'DiSEqC 1.0' ), ( 2, 'DiSEqC 1.1' ), ( 3, 'Motorized, DiSEqC 1.2' ), ( 4, 'Motorized, USALS' ), ( 5, 'OneCable' )] ,
	[ 'Tuner2 Type', ( 0, 'Simple LNB' ), ( 1, 'DiSEqC 1.0' ), ( 2, 'DiSEqC 1.1' ), ( 3, 'Motorized, DiSEqC 1.2' ), ( 4, 'Motorized, USALS' ), ( 5, 'OneCable' )] ,


	[ 'Channel Search Mode', ( 1, 'free only' ), ( 2, 'scrambled only' ), ( 0, 'free & scrambled' )],

	[ 'Network Search', ( 0, 'On' ), ( 1, 'Off' )],
	[ 'DVB Type', ( 0, 'DVB-S (SD)' ), ( 1, 'DVB-S2 (HD)' )],
	[ 'FEC', ( 6, 'QPSK 1/2' ), ( 8, 'QPSK 2/3' ), ( 9, 'QPSK 3/4' ), ( 7, 'QPSK 3/5' ), ( 10, 'QPSK 4/5' ), ( 11, 'QPSK 5/6' ), ( 12, 'QPSK 8/9' ),
			 ( 13, 'QPSK 9/10' ), ( 15, '8PSK 2/3' ), ( 16, '8PSK 3/4' ), ( 14, '8PSK 3/5' ), ( 17, '8PSK 5/6' ), ( 18, '8PSK 8/9'), ( 19, '8PSK 9/10' )],

	[ 'Polarisation', ( 0, 'Horizontal' ), ( 1, 'Vertical' )],

	[ 'Summer Time', ( 0, 'Automatic' ), ( 1, 'Manual' )],


	[ 'Lock Mainmenu',  ( 1, 'No' ), ( 0, 'Yes' )],
	[ 'Lock Receiver',  ( 1, 'No' ), ( 0, 'Yes' )],
	[ 'Age Restricted', ( 9, '9' ), ( 10, '10' ), ( 11, '11' ), ( 12, '12' ), ( 13, '13' ), ( 14, '14' ), ( 15, '15' ), ( 16, '16' ), ( 17, '17' ), ( 18, '18' ), ( 19, '19' )],

	[ 'Sleep Timer', ( 0, 'Off' ), ( 1, 'On' )],
	[ 'Functional Range', ( 2, 'High' ), ( 1, 'Middle' ), ( 0, 'Low' )],

	[ 'Channel Banner Duration', ( 4, '4 s' ), ( 5, '5 s' ), ( 6, '6 s' ), ( 1, '1 s' ), ( 2, '2 s' ), ( 3, '3 s' )],
	[ 'Playback Banner Duration', ( 4, '4 s' ), ( 5, '5 s' ), ( 6, '6 s' ), ( 1, '1 s' ), ( 2, '2 s' ), ( 3, '3 s' )],
	[ 'Display Volume', ( 1, 'On' ), ( 0, 'Off' )],
	[ 'Front Display Brightness', ( 0x1, 'Bright' ), ( 2, 'Middle' ), ( 4, 'Dark' ), ( 5, 'Off' )],

	[ 'EPG Grabbing', ( 1, 'tvtv' ), ( 0, 'Off' ),( 2, 'SI' )],


	[ 'Start View', ( 0, 'Current' ), ( 1, 'Schedule' )],
	[ 'Pre-Rec Time', ( 300, '5 Min' ), ( 360, '6 Min' ), ( 420, '7 Min' ), ( 480, '8 Min' ), ( 540, '9 Min' ), ( 600, '10 Min' ),( 60, '1 Min' ), ( 120, '2 Min' ), ( 180, '3 Min' ), ( 240, '4 Min' )],
	[ 'Post-Rec Time', ( 300, '5 Min' ), ( 360, '6 Min' ), ( 420, '7 Min' ), ( 480, '8 Min' ), ( 540, '9 Min' ), ( 600, '10 Min' ),( 60, '1 Min' ), ( 120, '2 Min' ), ( 180, '3 Min' ), ( 240, '4 Min' )],


	[ 'Automatic Timeshift', ( 1, 'On' ), ( 0, 'Off' )],
	[ 'Timeshift Buffer Size', ( 5*1024, '5 GB' ), ( 10*1024, '10 GB' ), ( 15*1024, '15 GB' ), ( 20*1024, '20 GB' )],
	[ 'Default Rec Duration', ( 7200, '02:00 h' ), ( 9000, '02:30 h' ), ( 10800, '03:00 h' ), ( 1800, '00:30 h' ), ( 3600, '01:00 h' ), ( 5400, '01:30 h' )],

	[ 'DHCP', ( 1, 'On' ), ( 0, 'Off' )],

	[ 'LNB Type', ( 0, 'Universal' ), ( 1, 'Single' ), ( 2, 'Userdefined' )],	

	[ 'Time Mode', ( 0, 'Automatic' ), ( 1, 'Manual' )],

	[ 'Time Installation', ( 0, 'Off' ), ( 1, 'On' )],

	[ 'OneCable Type', ( 0, 'EXR ... / EXU ...' ), ( 1, 'UAS 481' ), ( 2, 'Userdefined' )],
	[ 'MDU', ( 0, 'Off' ), ( 1, 'On' )],
	[ 'Stop on Signal', ( 1, 'On' ), ( 0, 'Off' )],

	[ 'Local Time Offset',( 1*3600, '01:00' ),( 1*3600+30*60, '01:30' ),( 2*3600, '02:00' ), (2*3600+60*30, '02:30'), (3*3600, '03:00'),
		( 3*3600+30*60, '03:30' ),( 4*3600, '04:00' ),( 4*3600+30*60, '04:30' ), ( 5*3600, '05:00' ), (5*3600+60*30, '05:30'), (6*3600, '06:00'),
		( 6*3600+30*60, '06:30' ),( 7*3600, '07:00' ),( 7*3600+30*60, '07:30' ), ( 8*3600, '08:00' ), (8*3600+60*30, '08:30'), (9*3600, '09:00'),
		( 9*3600+30*60, '09:30' ),( 10*3600, '10:00' ),( 10*3600+30*60, '10:30' ), ( 11*3600, '11:00' ), (11*3600+60*30, '11:30'), (12*3600, '12:00'), (12*3600+30*60, '12:30'), (13*3600, '13:00'),
		( -(12*3600), '-12:00' ),( -(11*3600+30*60), '-11:30' ),( -(11*3600), '-11:00' ), ( -(10*3600+30*60), '-10:30' ), ( -(10*3600), '-10:00' ),( -(9*3600+30*60), '-09:30' ),
		( -(9*3600), '-09:00' ),( -(8*3600+30*60), '-08:30' ),( -(8*3600), '-08:00' ), ( -(7*3600+30*60), '-07:30' ), ( -(7*3600), '-07:00' ),( -(6*3600+30*60), '-06:30' ),
		( -(6*3600), '-06:00' ),( -(5*3600+30*60), '-05:30' ),( -(5*3600), '-05:00' ), ( -(4*3600+30*60), '-04:30' ), ( -(4*3600), '-04:00' ),( -(3*3600+30*60), '-03:30' ),( -(3*3600), '-03:00' ),( -(2*3600+30*60), '-02:30' ),
		( -(2*3600), '-02:00' ),( -(1*3600+30*60), '-01:30' ),( -(1*3600), '-01:00' ), ( -(0*3600+30*60), '-00:30' ), ( 0, '00:00' ),( 0*3600+30*60, '00:30' )],

	[ 'Motor Control Tuner1', ( 0, 'DiSEqC 1.2' ), ( 1, 'DiSEqC 1.3' )],
	[ 'Motor Control Tuner2', ( 0, 'DiSEqC 1.2' ), ( 1, 'DiSEqC 1.3' )],
	[ 'Band', ( 0, 'Ku Band' ), ( 1, 'C Band' )],

	[ 'Language', ( ElisEnum.E_DEUTSCH, 'Deutsch' ), ( ElisEnum.E_ENGLISH, 'English' ), ( ElisEnum.E_FRENCH, 'Francais' ),
				  ( ElisEnum.E_ITALIAN, 'Italiano' ), ( ElisEnum.E_SPANISH, 'Espanol' ), ( ElisEnum.E_CZECH, 'Cestina' ),
				  ( ElisEnum.E_DUTCH, 'Nederlands' ), ( ElisEnum.E_POLISH, 'Polski' ), ( ElisEnum.E_TURKISH, 'Turkce' ),
				  ( ElisEnum.E_RUSSIAN, 'Russian' )],

	[ 'Country', ( ElisEnum.E_DEUTSCH, 'Deutsch' ), ( ElisEnum.E_ENGLISH, 'English' ), ( ElisEnum.E_FRENCH, 'Francais' ),
				  ( ElisEnum.E_ITALIAN, 'Italiano' ), ( ElisEnum.E_SPANISH, 'Espanol' ), ( ElisEnum.E_CZECH, 'Cestina' ),
				  ( ElisEnum.E_DUTCH, 'Nederlands' ), ( ElisEnum.E_POLISH, 'Polski' ), ( ElisEnum.E_TURKISH, 'Turkce' ),
				  ( ElisEnum.E_RUSSIAN, 'Russian' )],


	[ 'UAS 481 SCR', ( 0, '1400' ), ( 1, '1516' ), ( 2, '1632' ), (3, '1748' )],
	[ 'EXR EXU SCR', ( 0, '1284' ), ( 1, '1400' ), ( 2, '1516' ), ( 3, '1632' ), ( 4, '1748' ), (5, '1864' ), ( 7, '1980' ), ( 7, '2096' )],
	[ 'Use OneCable', ( 0, 'Off' ), ( 1, 'On' )],
	
	[ 'Fan Control', ( 1, 'Low' ), ( 2, 'Middle' )],
	
	# Audio Delay
	[ 'Audio Delay', ( 0, '0 ms' ), ( 10, '10 ms' ), ( 20, '20 ms' ), ( 30, '30 ms' ), ( 40, '40 ms' ), ( 50, '50 ms' ), ( 60, '60 ms' ),
				( 70, '70 ms' ),( 80, '80 ms' ),( 90, '90 ms' ),( 100, '100 ms' ),( 110, '110 ms' ),
				( 120, '120 ms' ),( 130, '130 ms' ),( 140, '140 ms' ),( 150, '150 ms' ),( 175, '175 ms' ),( 200, '200 ms' ),
				( 225, '225 ms' ),( 250, '250 ms' )],


	[ 'Shuffle', ( 0, 'Off' ), ( 1, 'On' )],
	[ 'Repeat', ( 0, 'Off' ), ( 1, 'On' )],
	[ 'Playback Duration', ( 4, '4 Sec' ),( 6, '6 Sec' ), ( 8, '8 Sec' ),( 10, '10 Sec' ), ( 12, '12 Sec' )],

	#Applications Menu
	[ 'FTP', ( 1, 'Yes' ), ( 0, 'No' )],
	[ '4G_Limit', ( 0, 'Off' ),( 1, 'On' )],
	[ 'UPnP', ( 0, 'No' ), ( 1, 'Yes' )],
	[ 'RTP Packet', ( 8, '8*188' ), ( 1, '1*188' ), ( 2, '2*188' ), ( 3, '3*188' ), ( 4, '4*188' ), ( 5, '5*188' ), ( 6, '6*188' ), ( 7, '7*188' ),
		( 9, '9*188' ), ( 10, '10*188' ), ( 11, '11*188' ), ( 12, '12*188' ), ( 13, '13*188' ), ( 14, '14*188' ),
		( 15, '15*188' ), ( 16, '16*188' )],
		

	[ 'Audio Mute', ( 0, 'Off' ),( 1, 'On' )],
	[ 'Automatic Software Download', ( 1, 'On' ),( 0, 'Off' )],

	# Conax
	[ 'Conax New Message', ( 0, 'No' ),( 1, 'Yes' )],

	# Age Limit
	[ 'Age Limit', ( 0, 'No Limit' ), ( 7, ' 7 ' ), ( 11, ' 11 ' ), ( 15, ' 15 ' ), ( 18, ' 18 ' )],


	# Background Theme
	[ 'Background Theme', ( 5, 'GrayScale' ),( 0, 'Violet' ), ( 1, 'Autumn' ), ( 2, 'Wine' ), ( 3, 'Sea' ), ( 4, 'Forest' )],
	[ 'Transparency', ( 0, '0 %' ), ( 1, '30 %' ), ( 2, '50 %' ), ( 3, '70 %' ), ( 4, '100 %' )],
	[ 'Zapping Mode', ( 0, 'All' ), ( 1, 'Favorite' ), ( 2, 'Network' ), ( 3, 'Satellite' ), ( 4, 'Cas' )],

	[ 'Recording List Mode', ( 0, 'All' ), ( 1, 'Folder' ), ( 2, 'Category' ), ( 3, 'Priority' )],
	[ 'Recording List Sort', ( 1, 'Date' ), ( 0, 'Title' ), ( 2, 'Channel' ), ( 3, 'Duration' )],

	[ 'Antenna 5V', ( 1, 'On' ), ( 0, 'Off' )],
	[ 'EPG Mode', ( 0, 'List' ), ( 1, 'Grid' ), ( 2, 'Current' )],
	[ 'Automatic Standby Decrypt', ( 0, 'Off' ), ( 1, 'On' )],

	[ 'Use WLAN', ( 0, 'Off' ), ( 1, 'On' )],


	[ 'FTP Transaction', ( 0, 'Disabled' ), ( 1, 'Enabled' )],
	[ 'UPNP Transaction', ( 0, 'Disabled' ), ( 1, 'Enabled' )],

	[ 'Media Browser Filter', ( 0, 'All Media' ), ( 1, 'Music' ), ( 2, 'Photo' ), ( 3, 'Movie' )],

	[ 'Auto EPG', ( 1, 'On' ), ( 0, 'Off' )],
	[ 'EPG Grab Interval', ( 1, '1 Min' ), ( 2, '2 Min' ), ( 3, '3 Min' ), ( 4, '4 Min' ), ( 5, '5 Min' ), ( 6, '6 Min' ), ( 7, '7 Min' ),
							( 8, '8 Min' ), ( 9, '9 Min' ), ( 10, '10 Min' )],

	[ 'Auto EPG Channel', ( 1, 'Channel Number' ), ( 0, 'Favorites' )],
	[ 'EPG Grid Unit', ( 1, '2 Hour' ), ( 0, '1 Hour' ),( 2, '3 Hour' ),( 3, '4 Hour' )],

	[ 'EPG Grab Enabled', ( 0, 'Off' ), ( 1, 'On' )],

	[ 'Make Dedicated HDD', ( 0, 'No' ), ( 1, 'Started' ), ( 2, 'Decided' )],
	[ 'Viewing Tuner Free', ( 0, 'No' ), ( 1, 'Yes' )],
	[ 'FrontDisplay Function', ( 0, 'Channel' ), ( 1, 'Clock' )],
	[ 'Dynamic SI Handling', ( 0, 'Off' ), ( 1, 'On' )],
	[ 'Simple MP3', ( 0, 'Off' ), ( 1, 'On' )], 'eeprom',
	[ 'MP3 Player Screensaver', ( 0, 'Off' ), ( 1, 'On' )],


	[ 'Channel Order Country', ( 1, 'DE' ), ( 0, 'None' ), ( 2, 'AT' )],
	[ 'Viaccess Console', ( 1, 'On' ), ( 0, 'Off' )],
	[ 'Viaccess FreeChannel Lock', ( 0, 'Off' ), ( 1, 'On' )],
	[ 'Viaccess SChip Mode', ( 0, 'Inactive' ), ( 1, 'Session' ), ( 2, 'Locked' )],

	[ 'Force 576i', ( 0, 'Off' ),( 1, 'On' )],


	[ 'HDCP', ( 1, 'On' ), ( 0, 'Off' )],

	[ 'Viaccess Standby', ( 0, 'Off' ), ( 1, 'On' )],
	[ 'Viaccess StopFreeChannels', ( 0, 'Off' ), ( 1, 'On' )],
	[ 'Viaccess HasAlarm', ( 0, 'Off' ), ( 1, 'On' )],
	[ 'Youtube Feed', ( 0, 'Top Rated' ), ( 1, 'Top Favorites' ), ( 2, 'Most Viewed' ), ( 3, 'Most Popular' ), 
		( 4, 'Most Recent' ), ( 5, 'Most Discussed' ), ( 6, 'Most Responded' ), ( 7, 'Recently Featured' ), ( 8, 'Watch On Mobile' ) ],
	[ 'Youtube Region', ( 0, 'Global' ), ( 1, 'Australia' ), ( 2, 'Brazil' ), ( 3, 'Canada' ), ( 4, 'Czech Republic' ),
		( 5, 'France' ), ( 6, 'Germany' ), ( 7, 'Great Britain' ), ( 8, 'Holland' ), ( 9, 'Hong Kong' ), ( 10, 'India' ), ( 11, 'Ireland' ), 
		( 12, 'Israel' ), ( 13, 'Italy' ), ( 14, 'Japan' ), ( 15, 'Mexico' ), ( 16, 'New Zealand' ), ( 17, 'Poland' ), ( 18, 'Russia' ),
		( 19, 'South Korea' ), ( 20, 'Spain' ), ( 21, 'Sweden' ), ( 22, 'Taiwan' ),( 23, 'United States' )],
	[ 'Youtube Time', ( 0, 'All Time' ), ( 1, 'Today' ), ( 2, 'This Week' ), ( 3, 'This Month' )], 
	[ 'Youtube Category', ( 0, 'None' ), ( 1, 'Entertainment' ), ( 2, 'Shows' ), ( 3, 'Music' ),
		( 4, 'Games' ), ( 5, 'Film' ), ( 6, 'News' ), ( 7, 'Tech' ), ( 8, 'Comedy' )], 
	[ 'Youtube Quality', ( 0, 'SQ' ), ( 1, 'HQ' )],
	[ 'Media Player Jump', ( 0, 'Yes' ), ( 1, 'No' )], 

	[ 'FTA Scan', ( 1, 'Yes' ), ( 0, 'No' )],
	[ 'Scan Mode', ( 0, 'Individual' ), ( 1, 'Collectif' )], 
	[ 'Primary Polarization', ( 1, 'Vertical' ), ( 0, 'Horizontal' ) ], 
	[ 'Secondary Polarization', ( 1, 'Vertical' ), ( 0, 'Horizontal' ) ], 

	[ 'Primary FEC', (  0, 'Automatic' ), ( 6, 'QPSK 1/2' ), ( 8, 'QPSK 2/3' ), ( 9, 'QPSK 3/4' ), ( 7, 'QPSK 3/5' ), ( 10, 'QPSK 4/5' ), 
						( 11, 'QPSK 5/6' ),	( 12, 'QPSK 8/9' ), ( 13, 'QPSK 9/10' ), ( 15, '8PSK 2/3' ), ( 16, '8PSK 3/4' ), ( 14, '8PSK 3/5' ),
						( 17, '8PSK 5/6' ),	( 18, '8PSK 8/9'), ( 19, '8PSK 9/10' )],

	[ 'Secondary FEC', (  0, 'Automatic' ), ( 6, 'QPSK 1/2' ), ( 8, 'QPSK 2/3' ), ( 9, 'QPSK 3/4' ), ( 7, 'QPSK 3/5' ), ( 10, 'QPSK 4/5' ),
						( 11, 'QPSK 5/6' ),	( 12, 'QPSK 8/9' ), ( 13, 'QPSK 9/10' ), ( 15, '8PSK 2/3' ), ( 16, '8PSK 3/4' ), ( 14, '8PSK 3/5' ),
						( 17, '8PSK 5/6' ), ( 18, '8PSK 8/9'), ( 19, '8PSK 9/10' )],

	[ 'Primary DVB Type', ( 0, 'DVB-S (SD)' ), ( 1, 'DVB-S2 (HD)' )],
	[ 'Secondary DVB Type', ( 0, 'DVB-S (SD)' ), ( 1, 'DVB-S2 (HD)' )],

	[ 'Canalplus BAT DVBType', ( 0, 'DVB-S (SD)' ), ( 1, 'DVB-S2 (HD)' )],
	[ 'Canalplus BAT Polarization', ( 1, 'Vertical' ), ( 0, 'Horizontal' )],
	[ 'Canalplus BAT FEC', ( 0, 'Automatic' ), ( 6, 'QPSK 1/2' ), ( 8, 'QPSK 2/3' ), ( 9, 'QPSK 3/4' ), ( 7, 'QPSK 3/5' ), ( 10, 'QPSK 4/5' ),
						( 11, 'QPSK 5/6' ),	( 12, 'QPSK 8/9' ), ( 13, 'QPSK 9/10' ), ( 15, '8PSK 2/3' ), ( 16, '8PSK 3/4' ), ( 14, '8PSK 3/5' ),
						( 17, '8PSK 5/6' ), ( 18, '8PSK 8/9'), ( 19, '8PSK 9/10' )],


	[ 'Record Management', ( 1, 'Automatic' ), ( 0, 'Manual' )],
	[ 'HDMI Color Space', ( 0, 'RGB' ), ( 1, 'YUV' )],


	[ 'Download Polarization', ( 1, 'Vertical' ), ( 0, 'Horizontal' ) ],

	[ 'Download FEC', ( 0, 'Automatic' ), ( 6, 'QPSK 1/2' ), ( 8, 'QPSK 2/3' ), ( 9, 'QPSK 3/4' ), ( 7, 'QPSK 3/5' ), ( 10, 'QPSK 4/5' ), 
						( 11, 'QPSK 5/6' ), ( 12, 'QPSK 8/9' ), ( 13, 'QPSK 9/10' ), ( 15, '8PSK 2/3' ), ( 16, '8PSK 3/4' ), ( 14, '8PSK 3/5' ),
						( 17, '8PSK 5/6' ), ( 18, '8PSK 8/9'), ( 19, '8PSK 9/10' )],

	[ 'Download DVB Type', ( 0, 'DVB-S (SD)' ), ( 1, 'DVB-S2 (HD)' )],
		
	[ 'Need SSU', ( 0, 'NO' ), ( 1, 'YES' )],


	[ 'Font Size', ( 0, '1' ), ( 1, '2' ), ( 2, '3' )],

	[ 'Power Save Mode', ( 3600 * 4, '4 Hour' ), ( 3600 * 5, '5 Hour' ), ( 3600 * 6, '6 Hour' ), ( 3600 * 7, '7 Hour' ), ( 3600 * 8, '8 Hour' ),( 0, 'Off' )  ],

	[ 'HDDRepartition', ( 0, 'NO' ), ( 1, 'YES' )] ]


_propertyMapInt =[
	[ "Last TV Number", 1, ElisEnum.E_DEFAULT_STEP, 1, ElisEnum.E_DEFAULT_MAX ],
	[ "Last Radio Number", 1, ElisEnum.E_DEFAULT_STEP, 1, ElisEnum.E_DEFAULT_MAX ],
	[ "Audio Volume", 75, ElisEnum.E_DEFAULT_STEP, 0, 100 ],
	[ "Time Setup Channel Number", 1, ElisEnum.E_DEFAULT_STEP, 0, 9999 ],

	[ "Current Scan Frequency", 0, ElisEnum.E_DEFAULT_STEP, 3000, 20000 ],
	[ "Current Scan SymbolRate", 0, ElisEnum.E_DEFAULT_STEP, 1000, 50000 ],
	[ "Current Scan SatelliteLongitude", 0, ElisEnum.E_DEFAULT_STEP, 0, 3600 ],
	[ "PinCode", 0, ElisEnum.E_DEFAULT_STEP, 0, 9999, ],
	[ "EPG Grabbing Time", 10800, ElisEnum.E_DEFAULT_STEP, 0, 86340 ],
	[ "Free Access From", 0, ElisEnum.E_DEFAULT_STEP, 0, 86340 ],
	[ "Free Access Until", 0, ElisEnum.E_DEFAULT_STEP, 0, 86340 ],
	[ "Longitude", 0, ElisEnum.E_DEFAULT_STEP, 0, 7200 ],
	[ "Latitude", 0, ElisEnum.E_DEFAULT_STEP, 0, 7200 ],
	[ "MyLongitude", 0, ElisEnum.E_DEFAULT_STEP, 0, 3600, ],
	[ "MyLatitude", 0, ElisEnum.E_DEFAULT_STEP, 0, 3600 ],
	[ "Tuner1 SCR", 0, ElisEnum.E_DEFAULT_STEP, 0, 7  ],	
	[ "Tuner2 SCR", 0, ElisEnum.E_DEFAULT_STEP, 0, 7 ],	
	[ "Tuner1 SCR Frequency", 0, ElisEnum.E_DEFAULT_STEP, 0, 9999, ],	
	[ "Tuner2 SCR Frequency", 0, ElisEnum.E_DEFAULT_STEP, 0, 9999, ],	
	[ "Tuner1 Pin Code", 0, ElisEnum.E_DEFAULT_STEP, 0, 999, ],
	[ "Tuner2 Pin Code", 0, ElisEnum.E_DEFAULT_STEP, 0, 999, ],

	[ "ChannelListYear", 0, ElisEnum.E_DEFAULT_STEP, 1900, 2100 ],
	[ "ChannelListMonth", 0, ElisEnum.E_DEFAULT_STEP, 1, 12 ], 
	[ "ChannelListDay", 0, ElisEnum.E_DEFAULT_STEP, 1, 31 ], 

	[ "FirmwareUpdateYear", 0, ElisEnum.E_DEFAULT_STEP, 1900, 2100 ],	
	[ "FirmwareUpdateMonth", 0, ElisEnum.E_DEFAULT_STEP, 1, 12 ], 
	[ "FirmwareUpdateDay", 0, ElisEnum.E_DEFAULT_STEP, 1, 31 ], 


	[ "IpAddress", 0, ElisEnum.E_DEFAULT_STEP, 0x80000000, 0x7fffffff ],	
	[ "SubNet", 0, ElisEnum.E_DEFAULT_STEP, 0x80000000,0x7fffffff ], 
	[ "Gateway", 0, ElisEnum.E_DEFAULT_STEP, 0x80000000, 0x7fffffff ], 
	[ "DNS", 0, ElisEnum.E_DEFAULT_STEP, 0x80000000, 0x7fffffff ], 

	[ "Recent SWPack Version", 0, ElisEnum.E_DEFAULT_STEP, 100, 2000 ], 
		
	[ "Channel Delta Version", 0, ElisEnum.E_DEFAULT_STEP, 99, 2000 ], 

	[ "Loader Version", 0, ElisEnum.E_DEFAULT_STEP, 99, 2000  ],

	[ "Timer Toggle", 0, ElisEnum.E_DEFAULT_STEP, 0, 1 ], 
	[ "Timer Save Count", 0, ElisEnum.E_DEFAULT_STEP, 0, 0xffff ], 
	[ "Timer Count", 0, ElisEnum.E_DEFAULT_STEP, 0, 0xffff ], 

	[ "EPG Toggle", 0, ElisEnum.E_DEFAULT_STEP, 0, 1 ], 
		
	[ "UPnP Server ReadTick", 0, ElisEnum.E_DEFAULT_STEP, 0, ElisEnum.E_DEFAULT_MAX ],

	[ "Auto EPG Start Channel", 1, ElisEnum.E_DEFAULT_STEP, 1, 99999 ],
	[ "Auto EPG End Channel", 1, ElisEnum.E_DEFAULT_STEP, 1, 99999  ],
	[ "Auto EPG Favorite Group", 0, ElisEnum.E_DEFAULT_STEP, 0, 10000 ],
	[ "PIP Position X", 900, ElisEnum.E_DEFAULT_STEP, 1, 1034, ],
	[ "PIP Position Y", 70, ElisEnum.E_DEFAULT_STEP, 1, 549  ],
	[ "Dedicated Media Size", 0, ElisEnum.E_DEFAULT_STEP, 1, 0xfffffff ],
	[ "Dedicated Timeshift Size", 0, ElisEnum.E_DEFAULT_STEP, 1, 1024*16 ],
	[ "Dedicated Program Size", 0, ElisEnum.E_DEFAULT_STEP, 1, 1024*8 ],

	[ "OTI Ignored SW Version", 100, ElisEnum.E_DEFAULT_STEP, 100, 30000 ],
	[ "OTI Ignored CL Version", 100, ElisEnum.E_DEFAULT_STEP, 100, 30000 ],
	[ "OTI Current CL Version", 100, ElisEnum.E_DEFAULT_STEP, 100, 30000 ],

	[ "Thin Client AV Delay", 500, ElisEnum.E_DEFAULT_STEP, 100, 3000  ],
		
	[ "Viaccess Alarm Time", 0, ElisEnum.E_DEFAULT_STEP, 0x80000000, 0x7fffffff ],
	[ "Primary Frequency", 11856, ElisEnum.E_DEFAULT_STEP, 3000, 13000 ],
	[ "Primary Symbol Rate", 27500, ElisEnum.E_DEFAULT_STEP, 0, 60000 ],
	[ "Secondary Frequency", 12402, ElisEnum.E_DEFAULT_STEP, 3000, 13000 ],
	[ "Secondary Symbol Rate", 27500, ElisEnum.E_DEFAULT_STEP, 0, 60000 ],

	
	[ "Canalplus BAT Frequency", 11856, ElisEnum.E_DEFAULT_STEP, 3000, 13000 ],
	[ "Canalplus BAT Symbol Rate", 27500, ElisEnum.E_DEFAULT_STEP, 0, 60000 ],
	[ "Canalplus BAT Version", 0, ElisEnum.E_DEFAULT_STEP, 0, 255 ],
	[ "Canalplus BATSPS Version", 0, ElisEnum.E_DEFAULT_STEP, 0, 255 ],
	[ "Canalplus Saved SOID", 0, ElisEnum.E_DEFAULT_STEP, 0, 0xffffff ],
	[ "Canalplus BATSPS BouquetID", 0, ElisEnum.E_DEFAULT_STEP, 0, 0xffff ],
	[ "Canalplus BATActif BouquetID", 0, ElisEnum.E_DEFAULT_STEP, 0, 0xffff ],

	[ "Download Frequency", 11856, ElisEnum.E_DEFAULT_STEP, 3000, 13000 ],
	[ "Download SymbolRate", 27500, ElisEnum.E_DEFAULT_STEP, 0, 60000 ],

	[ "Download DiseqcMode", 0, ElisEnum.E_DEFAULT_STEP, 0, 255 ],
	[ "Download Pid", 0, ElisEnum.E_DEFAULT_STEP, 0, 0x1fff ],
	[ "Download GroupInfoSelect", 0, ElisEnum.E_DEFAULT_STEP, 0, 0xffff ],	

	[ "Download Diseqc11Switch", 0, ElisEnum.E_DEFAULT_STEP, 0, 255 ],	
	[ "Download Diseqc11Repeat", 0, ElisEnum.E_DEFAULT_STEP, 0, 3 ],	

	[ "MacAddressHigh", 0x55aa0000, ElisEnum.E_DEFAULT_STEP, 0x55aa0000, 0x55aaffff],
	[ "MacAddressLow", 0, ElisEnum.E_DEFAULT_STEP, 0x80000000, 0x7fffffff],

	[ "ExpiredDate", 0, ElisEnum.E_DEFAULT_STEP, 0x80000000, 0x7fffffff ],	
	[ "ExpiredFlag", 0, ElisEnum.E_DEFAULT_STEP, 0x80000000, 0x7fffffff ], 
	[ "CardNum0", 0, ElisEnum.E_DEFAULT_STEP, 0x0, 0xff ], 
	[ "CardNum1", 0, ElisEnum.E_DEFAULT_STEP, 0x0, 0xff ], 
	[ "CardNum2", 0, ElisEnum.E_DEFAULT_STEP, 0x0, 0xff ], 
	[ "CardNum3", 0, ElisEnum.E_DEFAULT_STEP, 0x0, 0xff ], 
	[ "CardNum4", 0, ElisEnum.E_DEFAULT_STEP, 0x0, 0xff ], 	

	[ "MediaRepartitionSize", 0, ElisEnum.E_DEFAULT_STEP, 0, 0x7fffffff ],

	[ "EPG Service Type", 1, ElisEnum.E_DEFAULT_STEP, 1, 2 ] ]


class ElisPropertyEnum(object):
	def __init__(self, name):
		global _propertyMapEnum
		self.commander = pvr.elismgr.getInstance().getCommander()		
		self.name = name
		print 'property name=%s' %self.name
		self.property = []
		for prop in _propertyMapEnum :
			if prop[0] == name :
				eleCount = len( prop )
				self.property = prop[1:eleCount]
				break;

	def getProp(self):
		ret = self.commander.enum_GetProp( self.name )
		return int(ret[0])


	def setProp(self, value):
		self.commander.enum_SetProp( self.name, value )

	def getPropString(self):
		value = self.getProp()
		index = 0
		for ele in self.property :
			if ele[0] == value :
				return ele[0]

			index += 1

		return None

	def setPropString(self, stringValue):
		index = 0
		for ele in self.property :
			if ele[1] == stringValue :
				self.setProp( ele[0] )
				break

			index += 1


	def getPropStringByIndex( self, index ):
		ele = self.property[index]
		return ele[1]

	def getPropIndex( self ) :
		index = 0
		value = self.getProp()
		for ele in self.property :
			if ele[0] == value :
				return index;
			index += 1

		return -1

	def setPropIndex(self, index):
		ele = self.property[index]
		self.setProp( ele[0] )

	def getName(self):
		return self.name

	def getIndexCount(self):
		return len(  self.property )



class ElisPropertyInt(object):
	def __init__(self, name):
		global _propertyMapInt
		self.commander = pvr.elismgr.getInstance().getCommander()		
		self.name = name
		print 'property name=%s' %self.name
		self.property = []
		for prop in _propertyMapInt :
			if prop[0] == name :
				self.property = prop
				break;

	def getProp(self):
		ret = self.commander.int_GetProp( self.name )
		return int( ret[0] )

	def setProp(self, value):
		self.commander.int_SetProp( self.name, value )

	def getName(self):
		return self.name


