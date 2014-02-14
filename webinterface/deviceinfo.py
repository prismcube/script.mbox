from datetime import datetime
from webinterface import Webinterface, getMyIp
import dbopen

class ElmoDeviceInfo( Webinterface ) :

	def __init__(self, urlPath) :
	
		super(ElmoDeviceInfo, self).__init__(urlPath)
		
	def xmlResult(self) :

		xmlStr = '<?xml version="1.0" encoding="UTF-8"?>\n'
		xmlStr += '<e2deviceinfo>\n'
		xmlStr += '<e2enigmaversion>PrismCube Anga</e2enigmaversion>\n'
		xmlStr += '<e2imageversion>0.01</e2imageversion>\n'
		xmlStr += '<e2webifversion>0.01</e2webifversion>\n'
		xmlStr += '<e2fpversion>0</e2fpversion>\n'
		xmlStr += '<e2devicename>Ruby</e2devicename>\n'
	
		xmlStr += '<e2frontends>\n'
		xmlStr += '<e2frontend>\n'
		xmlStr += '<e2name>Tuner A</e2name>\n'
		xmlStr += '<e2model> Vuplus DVB-S NIM (DVB-S2)</e2model>\n'
		xmlStr += '</e2frontend>\n'
		xmlStr += '</e2frontends>\n'
	
		xmlStr += '<e2network>\n'
		xmlStr += '<e2interface>\n'
		xmlStr += '<e2name>eth0</e2name>\n'
		xmlStr += '<e2mac>00:00:99:99:34:0c</e2mac>\n'
		xmlStr += '<e2dhcp>True</e2dhcp>\n'
		xmlStr += '<e2ip>' + ( str(getMyIp()) ).strip() + '</e2ip>\n'
		xmlStr += '<e2gateway>192.168.100.1</e2gateway>\n'
		xmlStr += '<e2netmask>255.255.252.0</e2netmask>\n'
		xmlStr += '</e2interface>\n'
		xmlStr += '</e2network>\n'
	
		xmlStr += '<e2hdds>\n'
		xmlStr += '<e2hdd>\n'
		xmlStr += '<e2model>ATA(ST3500321CS)</e2model>\n'
		xmlStr += '<e2capacity>500.107 GB</e2capacity>\n'
		xmlStr += '<e2free>474.827 GB</e2free>\n'
		xmlStr += '</e2hdd>\n'
		xmlStr += '</e2hdds>\n'
		xmlStr += '</e2deviceinfo>\n'
						
		return xmlStr
		

