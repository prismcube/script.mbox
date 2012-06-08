#-*- coding: utf-8 -*-
import os, re, shutil, sys
import string, time
from types import *
import struct, threading
#from socket import socket, AF_INET, SOCK_STREAM
import socket, fcntl, select

from TestScene import *

SIOCGIFNETMASK = 0x891b
PORT = 56892
#HOST = '192.168.101.169'
#HOST = '192.168.101.206'
#HOST = '127.0.0.1'

class KeyCode( object ):
	KEY_FROM_NONE = 0
	KEY_FROM_RCU = 1
	KEY_FROM_TACT = 2
	KEY_FROM_FRONTWHEEL = 3

	FLAG_NONE = 0
	FLAG_REPEATED = 1
	
	VKEY_NO_KEY = 0
	VKEY_OK = 1
	VKEY_UP = 2
	VKEY_DOWN = 3
	VKEY_LEFT = 4
	VKEY_RIGHT = 5
	VKEY_RED = 6
	VKEY_GREEN = 7
	VKEY_YELLOW = 8
	VKEY_BLUE = 9
	VKEY_0 = 10		# 10

	VKEY_1 = 11
	VKEY_2 = 12
	VKEY_3 = 13
	VKEY_4 = 14
	VKEY_5 = 15
	VKEY_6 = 16
	VKEY_7 = 17
	VKEY_8 = 18
	VKEY_9 = 19
	VKEY_FF = 20	# 20

	VKEY_REV = 21
	VKEY_PLAY = 22
	VKEY_REC = 23
	VKEY_PAUSE = 24
	VKEY_STOP = 25
	VKEY_SLOW = 26
	VKEY_MENU = 27
	VKEY_EPG = 28
	VKEY_TEXT = 29
	VKEY_INFO = 30	# 30

	VKEY_BACK = 31
	VKEY_EXIT = 32
	VKEY_POWER = 33
	VKEY_MUTE = 34
	VKEY_PROG_UP = 35
	VKEY_PROG_DOWN = 36
	VKEY_VOL_UP = 37
	VKEY_VOL_DOWN = 38
	VKEY_HELP = 39
	VKEY_MEDIA = 40	# 40

	VKEY_ARCHIVE = 41
	VKEY_PREVCH = 42
	VKEY_FAVORITE = 43
	VKEY_OPT = 44
	VKEY_PIP = 45
	VKEY_SLEEP = 46
	VKEY_HISTORY = 47
	VKEY_ADDBOOKMARK = 48
	VKEY_BMKWINDOW = 49
	VKEY_JUMP_FORWARD = 50	# 50

	VKEY_JUMP_BACKWARD = 51
	VKEY_TV_RADIO = 52
	# added by lael98 20090331
	VKEY_SUBTITLE = 53
	VKEY_STAR = 54
	VKEY_CHECK = 55		# 55
	VKEY_SEARCH = 56
	VKEY_EDIT = 57
	VKEY_DELETE = 58
	VKEY_FUNC_A = 59
	VKEY_FUNC_B = 60	# 60

	VKEY_VOD_TIMESHIFT = 61
	VKEY_ADULT = 62
	VKEY_VOD = 63
	VKEY_SOURCE = 64 
	VKEY_VFORMAT = 65
	VKEY_AFORMAT = 66
	VKEY_WIDE = 67
	VKEY_LIST = 68


	VKEY_FRONT_MENU = 0x80 #0x80 
	VKEY_FRONT_EXIT = 0x81
	VKEY_FRONT_AUX = 0x82
	VKEY_FRONT_TV_R = 0x83
	VKEY_FRONT_OK = 0x84
	VKEY_FRONT_CCW = 0x85
	VKEY_FRONT_CW = 0x86

	VKEY_CHANGE_ADDR1 = 0x74,
	VKEY_CHANGE_ADDR2 = 0x75,
	VKEY_CHANGE_ADDR3 = 0x76,
	VKEY_CHANGE_ADDR4 = 0x77




class _VKey(object):
	def __init__(self):
		self.mKeySource=0
		self.mKeyCode=0
		self.mFlag=0

def send(aMsg = None):
	HOST = get_ip_address('eth0')
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error, msg:
		sys.stderr.write("[ERROR1] %s\n" % msg[1])
		sys.exit(1)
	 
	try:
		sock.connect((HOST, PORT + 10))
	except socket.error, msg:
		sys.stderr.write("[ERROR2] %s\n" % msg[1])
		sys.exit(2)

	#cmd = raw_input()
	VKey = KeyCode()

	#testScene = [VKey.VKEY_MENU, VKey.VKEY_BACK]
	testScene = test4()
	loop = 0

	startTime = time.time()
	lblStart = time.strftime('%H:%M:%S', time.localtime(startTime) )

	while (1) :
		for key in testScene :

			lastTime = time.time()
			lblLast  = time.strftime('%H:%M:%S', time.localtime(lastTime) )
			lblTest  = time.strftime('%H:%M:%S', time.gmtime(lastTime - startTime) )
			print '[start[%s] current[%s] TestTime[%s] count[%d] key[%s]' % ( lblStart, lblLast, lblTest, loop, key[0] )

			msg = struct.pack("3i",*[1, key[0], 0])
			#print 'send[%s] size[%s] '% (key[0], len(msg) )

			sock.send( msg )
			time.sleep(key[1])

			loop += 1


def stringfor(command, data, accesskey='\0'*6, tid=1):
	length = 16 + len(data)
	prefix = struct.pack('>BBIBB6s', 6, 2, length, tid, command, accesskey)
	checksum = sum( ord(c) for c in prefix ) #& 0xFF   
	return prefix + chr(checksum) + chr(3)



def get_ip_address(ifname) : 
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	return socket.inet_ntoa(fcntl.ioctl( \
		s.fileno(), \
		0x8915, # SIOCGIFADDR \
		struct.pack('256s', ifname[:15]) )[20:24])

if __name__ == "__main__":
	#print get_ip_address('eth0')

	send()



