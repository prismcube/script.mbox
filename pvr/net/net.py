
import sys
import xbmc
import time
from socket import *
import string
from pvr.net.SocketServer import *
from pvr.util import is_digit

separator = '[]:[]'


class EventRequest( object ):
	def __init__( self, sock ):
		self.sock = sock

	def recvall( self, bytes ):
		b = ''
		while len(b) < bytes:
			left = bytes - len(b)
			try:
				new = self.sock.recv(left)
			except Exception, e:
				if str(e) == "(9, 'Bad file descriptor')" or str(e) == "(10054, 'Connection reset by peer')":
					print 'Lost connection resetting'
					try:
						self.close()
					except Exception, e:
						print 'noclose'
					return b
				raise e
			if new == '':
				break # eof
			b += new
		return b


	def sendMsg( self, req ):
		msg = self.makeFormat(req)
		try:
			self.sock.send( msg )
		except Exception, e:
			if str(e) == "(10053, 'Software caused connection abort')":
				print 'Lost connection resetting'
				try:
					self.close()
				except Exception, e:
					print 'noclose'
				return
			raise e    

	def readMsg( self ):
		msg = self.recvall( 8 )
		reply =''
		if msg.upper() == 'OK':
			return 'OK'
 
		if msg.upper() == 'KO':
			return 'KO'
			
		
		n = 0
		if len(msg) > 0:
			if is_digit(msg):
				n = int(msg)
			else:
				print 'No integer msg[%s]' % msg

		i = 0
		while i < n:
			r = self.recvall( n - i)
#			reply += r.decode('utf-8')
			reply += r
			i +=  len(r)

		return reply.split(separator)

	def sendRequest( self, req ):
		self.sendMsg( req )
		reply = self.readMsg()
		return reply

	def makeFormat( self, req ):
		msg = separator.join( req )
		msg = msg.encode('utf-8')
		return '%-8d%s' %( len(msg), msg )


class EventCommander( object ):
	def __init__( self, address ):
		self.sock = socket(AF_INET, SOCK_STREAM)
		self.sock.connect( address )
		self.request = EventRequest( self.sock )

	def command( self, cmd ):
		return self.request.sendRequest( cmd )

	def send( self, req ):
		return self.request.sendMsg( req )

	def read( self ):
		return self.request.readMsg()	
		

	def close( self ):
		self.sock.close()


class EventHandler( StreamRequestHandler ): pass

class EventServer( ThreadingTCPServer ): pass



