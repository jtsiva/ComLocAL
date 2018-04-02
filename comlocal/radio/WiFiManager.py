from twisted.internet import task, reactor
from twisted.internet.protocol import ServerFactory, DatagramProtocol


from twisted.spread import pb
from twisted.python import log
from comlocal.radio.RadioManager import RadioManager, RadioTransport
import socket
import fcntl
import struct
import json
import time

class WiFiManager (RadioManager):
	def __init__ (self):
		RadioManager.__init__(self, 'WiFi')

	def _get_ip_address(self, ifname):
		"""
			Helper function
			Return ip address of interface:
			https://raspberrypi.stackexchange.com/questions/6714/how-to-get-the-raspberry-pis-ip-address-for-ssh
		"""
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		return socket.inet_ntoa(fcntl.ioctl(
			s.fileno(),
			0x8915,  # SIOCGIFADDR
			struct.pack('256s', ifname[:15])
		)[20:24])

	def _setupProperties(self):
		"""
		Set up the radio properties we might need
		"""
		props = {}

		try:
			props['addr'] = self._get_ip_address('wlan0')
		except IOError:
			#my laptop has a different form
			props['addr'] = self._get_ip_address('wlp1s0')


		props['maxPacketLength'] = 4096
		props['costPerByte'] = 1

		t = props['addr'].split('.')
		t[-1] = '255'

		props['bcastAddr'] = '.'.join(t)

		return props



class WiFiTransport (DatagramProtocol, RadioTransport):
	myPort = 10248

	def startProtocol (self):
		self.transport.setBroadcastAllowed(True)

	def write (self, message, addr):
		data = json.dumps(message, separators=(',', ':'))
		self.transport.write(data, (addr, WiFiTransport.myPort))

	def read(self, message):
		if self.manager is not None: 
			self.datagramReceived(json.dumps(message), ('<loopback>', WiFiTransport.myPort))

	def datagramReceived(self, data, (host, port)):
		log.msg(data + " from %s %d" % (host, port))
		#print data + " from %s %d" % (host, port)
		#don't do anything if not set up or if manager has already
		#been gc'd
		if self.manager is not None: 
			#log.msg('I am: %s' % self.manager.props['addr'])

			if not host == self.manager.props['addr']:
				try:
					message = json.loads(data)

					#append connection information
					message['sentby'] = host

					self.manager.read(message)
				except ValueError:
					pass #drop poorly formed packets

def startTransport(theTransportObj):
	return reactor.listenUDP(WiFiTransport.myPort, theTransportObj)