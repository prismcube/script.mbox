from datetime import datetime
from webinterface import Webinterface
import dbopen

class ElmoDeviceInfo( Webinterface ) :

	def __init__(self, urlPath) :
	
		super(ElmoDeviceInfo, self).__init__(urlPath)
		
	def xmlResult(self) :

		xmlStr = '<?xml version="1.0" encoding="UTF-8"?>'
		xmlStr += '		<e2deviceinfo>'
		xmlStr += '		<e2enigmaversion>PrismCube Anga</e2enigmaversion>'
		xmlStr += '		<e2imageversion>0.01</e2imageversion>'
		xmlStr += '		<e2webifversion>0.01</e2webifversion>'
		xmlStr += '		<e2fpversion>0</e2fpversion>'
		xmlStr += '		<e2devicename>Ruby</e2devicename>'
	
		xmlStr += '		<e2frontends>'
		xmlStr += '		<e2frontend>'
		xmlStr += '		<e2name>Tuner A</e2name>'
		xmlStr += '		<e2model> Vuplus DVB-S NIM (DVB-S2)</e2model>'
		xmlStr += '		</e2frontend>'
		xmlStr += '		</e2frontends>'
	
		xmlStr += '		<e2network>'
		xmlStr += '		<e2interface>'
		xmlStr += '			<e2name>eth0</e2name>'
		xmlStr += '			<e2mac>00:00:99:99:34:0c</e2mac>'
		xmlStr += '			<e2dhcp>True</e2dhcp>'
		xmlStr += '			<e2ip>192.168.100.30</e2ip>'
		xmlStr += '			<e2gateway>192.168.100.1</e2gateway>'
		xmlStr += '			<e2netmask>255.255.252.0</e2netmask>'
		xmlStr += '		</e2interface>'
		xmlStr += '		</e2network>'
	
		xmlStr += '		<e2hdds>'
		xmlStr += '		<e2hdd>'
		xmlStr += '			<e2model>ATA(ST3500321CS)</e2model>'
		xmlStr += '			<e2capacity>500.107 GB</e2capacity>'
		xmlStr += '			<e2free>474.827 GB</e2free>'
		xmlStr += '		</e2hdd>'
		xmlStr += '		</e2hdds>'
		xmlStr += '		</e2deviceinfo>'

						
		return xmlStr
		

