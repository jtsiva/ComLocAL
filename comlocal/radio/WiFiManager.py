from twisted.application import internet, service
from twisted.internet import task
from twisted.internet.protocol import ServerFactory, DatagramProtocol
from twisted.python import log
from comlocal.radio.RadioManager import RadioManagerProtocol
import socket
import fcntl
import struct
import json

class WiFiManagerService (service.Service):
	def __init__ (self, port, authFile = None):
		self._port = port
		self._localReceivers = []
		self._authFile = authFile
		self._registered = False


	def startService (self):
		service.Service.startService(self)
		if self._authFile is not None:
			self._authKey = open(self._authFile).read()
			log.msg('loaded auth key from: %s' % (self._authFile,))
		else:
			self._authKey = ''
			log.msg ('no file from which to load auth key')

	def handleCmd(self, cmd):
		try:
			if 'reg_local' == cmd['cmd']:
				port = cmd['port']
				self.addLocalReceiver(('127.0.0.1', port))
				cmd['result'] = 'success'
			elif 'reg_radio' == cmd['cmd'] and 'success' == cmd['result']:
				self._registered = True
				log.msg("Registered!")
				return None
			else:
				cmd['result'] = "failed: no command %s" % (cmd['cmd'])

		except KeyError:
			cmd['result'] = 'failed'

		return json.dumps(cmd)

	def getLocalReceivers(self):
		return self._localReceivers

	def addLocalReceiver (self, entry):
		self._localReceivers.append(entry)

class WiFiManagerProtocol(DatagramProtocol):
	def __init__(self, service):
		self._service = service
		self._props = {}
		self._setupProperties()

	def sendRegistration (self):
		regPacket = {}
		regPacket['type'] = 'cmd'
		regPacket['auth'] = self._service._authKey
		regPacket['cmd'] = 'reg_radio'
		regPacket['name'] = 'WiFi'
		regPacket['props'] = self._props
		self.transport.write(json.dumps(regPacket), ('127.0.0.1', radioMgrPort))
		log.msg('registering with RadioManager')	

	def checkRegistration (self):
		#if the RadioManager responded then we don't need to keep
		#checking
		if self._service._registered:
			from twisted.internet import reactor
			self._later.stop()
		else:
			self.sendRegistration()

	def _get_ip_address(self, ifname):
		"""
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
		try:
			self._props['addr'] = self._get_ip_address('wlan0')
		except IOError:
			#my laptop has a different form
			self._props['addr'] = self._get_ip_address('wlp1s0')

		self._props['maxPacketLength'] = 4096
		self._props['costPerByte'] = 1
		self._props['port'] = self._service._port


	def startProtocol (self):
		self.transport.setBroadcastAllowed(True)

		#give the other service three seconds to start up
		from twisted.internet import reactor
		self._later = task.LoopingCall (self.checkRegistration)
		task.deferLater(reactor, 3.0, self.sendRegistration)
		task.deferLater(reactor, 5.0, self._later.start, 5.0)

	def datagramReceived(self, data, (host, port)):
		if not host == self._props['addr']:
			log.msg(data + " from %s %d" % (host, port))
			try:
				message = json.loads(data)
				if '127.0.0.1' == host:
					if 'msg' == message['type'] and self._service._registered:
						self.transport.write(data, ('<broadcast>', self._service._port))
					elif 'cmd' == message['type']:
						response = self._service.handleCmd(message)
						if response is not None:
							self.transport.write(response, (host, port))
				elif not '127.0.0.1' == host and self._service._registered:
					message['sentby'] = host
					data = json.dumps(message)
					for addr in self._service.getLocalReceivers():
						self.transport.write(data, addr)
			except KeyError:
				pass #drop poorly formed packets

radioMgrPort = RadioManagerProtocol.myPort
port = 10248
iface = "0.0.0.0"

topService = service.MultiService()

wifiManagerService = WiFiManagerService(port)
wifiManagerService.setServiceParent(topService)

udpService = internet.UDPServer(port, WiFiManagerProtocol(wifiManagerService))
udpService.setServiceParent(topService)

application = service.Application('wifimanager')
topService.setServiceParent(application)