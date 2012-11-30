import dbopen
from webinterface import Webinterface

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
		
	def xmlResult(self) :
	
		xmlstr = ''
		xmlstr += '<?xml version="1.0" encoding="UTF-8"?>'
		xmlstr += '<e2abouts>'
		xmlstr += '   <e2about>'
		xmlstr += '      <e2enigmaversion>Elmo-WebInterface-Test-Version</e2enigmaversion>'
		xmlstr += '      <e2imageversion>Elmo-Image-Version</e2imageversion>'
		xmlstr += '      <e2webifversion>0.01 Test-Version</e2webifversion>'
		xmlstr += '      <e2fpversion>Unknown</e2fpversion>'
		xmlstr += '      <e2model>Elmo XBMC on working mockup</e2model>'

		# xmlstr += '      {e2:convert type=web:ListFiller}'
		xmlstr += '      <e2lanmac>'
		mac = str(self.results[2][1])
		blocks = [mac[x:x+2] for x in xrange(0, len(mac), 2)]
		macFormatted = ':'.join(blocks)
		xmlstr += 			macFormatted
		xmlstr += '      </e2lanmac>'
		xmlstr += '      <e2landhcp>'
		# xmlstr += '         {e2:item name=lanDHCP /}'
		xmlstr += '      </e2landhcp>'
		xmlstr += '      <e2lanip>'
		xmlstr += 			'IpAddress'
		xmlstr += '      </e2lanip>'
		xmlstr += '      <e2lanmask>'
		#xmlstr += '         {e2:item name=lanMask /}'
		xmlstr += '      </e2lanmask>'
		xmlstr += '	      <e2langw>'
		xmlstr += 			'Gateway'	
		xmlstr += '      </e2langw>'
		#xmlstr += '      {/e2:convert} '
			  
		#xmlstr += '	  {e2:convert type=web:ListFiller}'
		xmlstr += '      <e2hddinfo>'
		xmlstr += '         <model>'
		xmlstr += '            {e2:item name=Model /}'
		xmlstr += '         </model>'
		xmlstr += '         <capacity>'
		xmlstr += '            {e2:item name=Capacity /}'
		xmlstr += '         </capacity>'
		xmlstr += '         <free>'
		xmlstr += '            {e2:item name=Free /}'
		xmlstr += '         </free>'
		xmlstr += '      </e2hddinfo>'
		#xmlstr += '      {/e2:convert} '
		      
		xmlstr += '	  <e2tunerinfo>'
		xmlstr += '         {e2:convert type=web:ListFiller}'
		xmlstr += '         <e2nim>'
		xmlstr += '            <name>'
		xmlstr += '               {e2:item name=Name /}'
		xmlstr += '            </name>'
		xmlstr += '            <type>'
		xmlstr += '               {e2:item name=Type /}'
		xmlstr += '            </type>'
		xmlstr += '         </e2nim>'
		xmlstr += '         {/e2:convert} '
		xmlstr += '      </e2tunerinfo>'
			  
		xmlstr += '      <e2servicename>' + self.currentChannel.mName + '</e2servicename>'
		xmlstr += '      <e2servicenamespace/>'
		xmlstr += '      <e2serviceaspect/>'
		xmlstr += '      <e2serviceprovider>{e2:convert type=ServiceName}Provider{/e2:convert}</e2serviceprovider>'
		xmlstr += '      <e2videowidth>{e2:convert type=ServiceInfo}VideoWidth{/e2:convert}</e2videowidth>'
		xmlstr += '      <e2videoheight>{e2:convert type=ServiceInfo}VideoHeight{/e2:convert}</e2videoheight>'
		xmlstr += '      <e2servicevideosize>{e2:convert type=ServiceInfo}VideoWidth{/e2:convert} x{e2:convert type=ServiceInfo}VideoHeight{/e2:convert}</e2servicevideosize>'
		xmlstr += '      <e2apid>{e2:convert type=ServiceInfo}AudioPid{/e2:convert}</e2apid>'
		xmlstr += '      <e2vpid>{e2:convert type=ServiceInfo}VideoPid{/e2:convert}</e2vpid>'
		xmlstr += '	      <e2pcrpid>{e2:convert type=ServiceInfo}PcrPid{/e2:convert}</e2pcrpid>'
		xmlstr += '      <e2pmtpid>{e2:convert type=ServiceInfo}PmtPid{/e2:convert}</e2pmtpid>'
		xmlstr += '      <e2txtpid>{e2:convert type=ServiceInfo}TxtPid{/e2:convert}</e2txtpid>'
		xmlstr += '      <e2tsid>{e2:convert type=ServiceInfo}TsId{/e2:convert}</e2tsid>'
		xmlstr += '      <e2onid>{e2:convert type=ServiceInfo}OnId{/e2:convert}</e2onid>'
		xmlstr += '      <e2sid>{e2:convert type=ServiceInfo}Sid{/e2:convert}</e2sid>'
		xmlstr += '   </e2about>'
		xmlstr += '</e2abouts>'

		return xmlstr