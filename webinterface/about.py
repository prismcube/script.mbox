import dbopen
from webinterface import Webinterface
from pvr.IpParser import IpParser

"""
			iChannel = ElisIChannel()
			#iChannel.reset( )
			#key											= aIChannel[0]

			iChannel.mNumber							= aIChannel[1+idx]
			iChannel.mPresentationNumber				= aIChannel[2+idx]
			iChannel.mName								= aIChannel[3+idx].encode('utf-8')
			iChannel.mServiceType						= aIChannel[4+idx]
			iChannel.mLocked							= aIChannel[5+idx]
			iChannel.mSkipped							= aIChannel[6+idx]
			iChannel.mIsBlank							= aIChannel[7+idx]
			iChannel.mIsCA								= aIChannel[8+idx]
			iChannel.mIsHD								= aIChannel[9+idx]
			#iChannel.mLockStartTime					= aIChannel[10+idx]
			#iChannel.mLockEndTime						= aIChannel[11+idx]
			iChannel.mCarrierType						= aIChannel[12+idx]

			#------DEPRECATED-----
			#iChannel.mCarrier.mDVBC.mFrequency			= 
			#iChannel.mCarrier.mDVBC.mSymbolRate		= 
			#iChannel.mCarrier.mDVBC.mQAM				= 
			#iChannel.mCarrier.mDVBT.mFrequency			= 
			#iChannel.mCarrier.mDVBT.mBand				= 

			iChannel.mCarrier = ElisICarrier()
			iChannel.mCarrier.mDVBS = ElisIDVBSCarrier()
			#iChannel.mCarrier = iCarrier
			#iChannel.mCarrier.mDVBS = iDVBS
			iChannel.mCarrier.mDVBS.mSatelliteLongitude	= aIChannel[13+idx]
			iChannel.mCarrier.mDVBS.mFrequency			= aIChannel[14+idx]
			iChannel.mCarrier.mDVBS.mSymbolRate			= aIChannel[15+idx]
			iChannel.mCarrier.mDVBS.mSatelliteBand		= aIChannel[16+idx]
			iChannel.mCarrier.mDVBS.mFECValue			= aIChannel[17+idx]
			iChannel.mCarrier.mDVBS.mPolarization		= aIChannel[18+idx]
			iChannel.mSid								= aIChannel[19+idx]
			iChannel.mTsid								= aIChannel[20+idx]
			iChannel.mNid								= aIChannel[21+idx]
			iChannel.mOnid								= aIChannel[22+idx]
"""

class ElmoAbout( Webinterface ) :

	def __init__(self, urlPath) :
		super(ElmoAbout, self).__init__(urlPath)
		self.conn = dbopen.DbOpen('property.db').getConnection()
		self.currentChannel = self.mDataCache.Channel_GetCurrent()

		sql = "select PropName, PropValue from tblPropertyInt where PropName in ('MacAddressHigh', 'IpAddress', 'Gateway')";
		self.c = self.conn.cursor()
		self.c.execute(sql)

		self.results = self.c.fetchall()
		print '[about result 1] : ' 
		print self.results

	def getMyNetworkInfo(self) :
		# getting NETWORK informations
		network = IpParser()
		networkInfo = network.GetNetworkAddress(network.GetCurrentServiceType())
			
		# return addressIp, addressMask, addressGateway, addressNameServer
		# IP Address of the set is now networkInfo[0] 
		return networkInfo

	def xmlResult(self) :

		network = self.getMyNetworkInfo()
	
		xmlstr = ''
		xmlstr += '<?xml version="1.0" encoding="UTF-8"?>'
		xmlstr += '<e2abouts>'
		xmlstr += '   <e2about>'
		xmlstr += '		<e2enigmaversion>PrismCube Webinterface</e2enigmaversion>'
		xmlstr += '		<e2imageversion>Version Ruby</e2imageversion>'
		xmlstr += '		<e2webifversion>0.1</e2webifversion>'
		xmlstr += '		<e2fpversion>Unknown</e2fpversion>'
		xmlstr += '		<e2model>PrismCube Ruby</e2model>'

		# xmlstr += '{e2:convert type=web:ListFiller}'
		mac = str(self.results[2][1])
		blocks = [mac[x:x+2] for x in xrange(0, len(mac), 2)]
		macFormatted = ':'.join(blocks)
		
		xmlstr += '		<e2lanmac>' + macFormatted +  '</e2lanmac>'
		xmlstr += '		<e2landhcp>DHCP Unkown</e2landhcp>'
		xmlstr += '     	<e2lanip>' + network[0] + '</e2lanip>'
		xmlstr += '     	<e2lanmask>' + network[1] + '</e2lanmask>'
		xmlstr += '		<e2langw> ' + network[2] + '</e2langw>'
		#xmlstr += '{/e2:convert} '
			  
		#xmlstr += '	{e2:convert type=web:ListFiller}'
		xmlstr += '		<e2hddinfo>'
		xmlstr += '		<model>2.5inch Type</model>'
		xmlstr += '		<capacity>Unkown</capacity>'
		xmlstr += '		<free>Unkown</free>'
		xmlstr += '      	</e2hddinfo>'
		#xmlstr += '	{/e2:convert} '
		      
		xmlstr += '		<e2tunerinfo>'
		#xmlstr += '         {e2:convert type=web:ListFiller}'
		xmlstr += '		<e2nim>'
		xmlstr += '			<name>Tuner A</name>'
		xmlstr += '			<type>Tuner</type>'
		xmlstr += '		</e2nim>'
		#xmlstr += '         {/e2:convert} '
		xmlstr += '		</e2tunerinfo>'
			  
		xmlstr += '		<e2servicename>' + self.currentChannel.mName + '</e2servicename>'
		xmlstr += '		<e2servicenamespace/>'
		xmlstr += '		<e2serviceaspect/>'
		xmlstr += '		<e2serviceprovider>' + self.currentChannel.mName +  '</e2serviceprovider>'
		xmlstr += '		<e2videowidth>000</e2videowidth>'
		xmlstr += '		<e2videoheight>000</e2videoheight>'
		xmlstr += '		<e2servicevideosize>000x000</e2servicevideosize>'
		xmlstr += '		<e2apid>audio pid</e2apid>'
		xmlstr += '		<e2vpid>video pid</e2vpid>'
		xmlstr += '		<e2pcrpid>pcr pid</e2pcrpid>'
		xmlstr += '		<e2pmtpid>pmt pid</e2pmtpid>'
		xmlstr += '		<e2txtpid>tx pid</e2txtpid>'
		xmlstr += '		<e2tsid>' + str(self.currentChannel.mTsid) + '</e2tsid>'
		xmlstr += '	<e2onid>onid</e2onid>'
		xmlstr += '	<e2sid>sid</e2sid>'
		
		xmlstr += '	</e2about>'
		xmlstr += '</e2abouts>'

		return xmlstr
