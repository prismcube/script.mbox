import dbopen
from webinterface import Webinterface

class PrismCubeDeviceInfo( Webinterface ) :

	def __init__(self, urlPath) :
		super(PrismCubeDeviceInfo, self).__init__(urlPath)

		"""
		self.conn = dbopen.DbOpen('property.db').getConnection()
		sql = "select PropName, PropValue from tblPropertyInt where PropName in ('MacAddressHigh', 'IpAddress', 'Gateway')";
		self.c = self.conn.cursor()
		self.c.execute(sql)

		self.results = self.c.fetchall()
		print self.results
		"""
		
	def xmlResult(self) :
	
		json = {}
		
		tuners = []
		# Start loop for all tuners
		tuner = {}
		tuner["type"] = "Vuplus DVB-S"
		tuner["name"] = "Tuner A"

		tuners.append( tuner )
		# All tuner(s) found

		json["tuners"] = tuners
		json["uptime"] = "2:03"
		json["enigmaver"] = "XBCM Version"
		json["imagever"] = "Beta 0.1"

		ifaces = []
		# Start loop for all network interfaces
		iface = {}
		iface["gw"] = "192.168.100.1"
		iface["name"] = "eth0"
		iface["ip"] = "192.168.100.158"
		iface["mask"] = "255.255.252.0"
		iface["mac"] = "00:00:99:99:34:0c"
		iface["dhcp"] = True

		ifaces.append(iface)
		#All ifaces found

		json["ifaces"] = ifaces
		json["brand"] = "PrismCube"
		json["fp_version"] = 0

		hdds = []
		# Start loop for all HDDs
		hdd = {}
		hdd["model"] = "Samsung"
		hdd["capacity"] = "500.107 GB"
		hdd["free"] = "400.804 GB"

		hdds.append( hdd )
		# All HDDs found

		json["hdd"] = hdds
		json["mem1"] = "275592 kB"
		json["mem2"] = "226452 kB"
		json["chipset"] = "7405(with 3D)"
		json["model"] = "Ruby"
		json["webifver"] = "OWIF 0.1.2"
		json["kernelver"] = "3.1.1"

		return str( json ).replace("'", '"').replace('True', 'true')

