from twisted.internet import task, reactor
from twisted.internet.protocol import ServerFactory, DatagramProtocol


from twisted.spread import pb
from twisted.python import log
from comlocal.radio.RadioManager import RadioManager
from comlocal.util.NetworkLayer import NetworkLayer
import socket
import fcntl
import struct
import json

class WiFiManager (pb.Root, NetworkLayer):
	myPort = 10249
	def __init__ (self):
		NetworkLayer.__init__(self, 'WiFi')
		self._localReceivers = set()
		self._registered = False

		self.props = {}
		self._setupProperties()

		t = self.props['addr'].split('.')
		t[-1] = '255'

		self.broadcastAddr = '.'.join(t)

		self.transport = None
		self.tryToRegister = task.LoopingCall (self.sendRegistration)
		self.tryToRegister.start(5.0)

	#def startProtocol(self):
		

	def setTransport(self, transport):
		self.transport = transport

	def remote_cmd(self, cmd):
		#log.msg('received command: %s' % cmd)
		try:
			if 'reg_local' == cmd['cmd']:
				port = cmd['port']
				self._localReceivers.add(port)
				cmd['result'] = self.success('')
			elif 'unreg_local' == cmd['cmd']:
				port = cmd['port']
				self._localReceivers.remove(port) #can't pop--it's a list
				cmd['result'] = self.success('')
			elif 'get_local' == cmd['cmd']:
				cmd['result'] = self._localReceivers
			elif 'check_radio_reg' == cmd['cmd']:
				cmd['result'] = str(self._registered)
			elif 'get_props' == cmd['cmd']:
				cmd['result'] = self.props
			elif 'allow_from_self' == cmd['cmd']:
				self.transport.allowMsgFromSelf(True)
			else:
				cmd['result'] = self.failure("no command %s" % (cmd['cmd']))

		except KeyError:
			cmd['result'] = self.failure('poorly formatted command (missing a field?)')
		except Exception as e:
			raise pb.Error (e) 

		return cmd

	def remote_write(self, message):
		try:
			#message['sentby'] = self.props['addr']
			addr = message.pop('addr')
			self.transport.write(message, addr)
			message['result'] = self.success('')
		except KeyError:
			message['result'] = self.failure('missing "addr" field')
		except Exception as e:
			raise pb.Error(e)
		return message

	def sendToLocalReceivers(self, message):
		if 'sentby' in message and 'msg' in message and 'dest' in message:
			message['radio'] = self.name

			def readAck(result):
				return result #hooray?

			def readNack(reason):
				log.msg(reason) #not hooray

			def connected(obj):
				d = obj.callRemote('read', message)
				d.addCallbacks(readAck,readNack)
				d.addCallback(lambda result: obj.broker.transport.loseConnection())
				return d

			for port in self._localReceivers:
				factory = pb.PBClientFactory()
				connect = reactor.connectTCP("127.0.0.1", port, factory)
				d = factory.getRootObject()
				d.addCallback(connected)
		else:
			pass
			#drop poorly formed packets

	def _getLocalReceivers(self):
		return self._localReceivers

	def sendRegistration (self):

		def regAck(result):
			self._registered = True
			self.tryToRegister.stop()

		def regNack(reason):
			log.msg(reason)

		def connected(obj):
			regPacket = {'cmd':'reg_radio','name':self.name,'props':self.props}
			d = obj.callRemote('cmd', regPacket)
			d.addCallbacks(regAck,regNack)
			d.addCallback(lambda result: obj.broker.transport.loseConnection())
			return d

		def failed(reason):
			log.msg(reason)

		factory = pb.PBClientFactory()
		self.radMgrConnect = reactor.connectTCP("127.0.0.1", RadioManager.myPort, factory)
		d = factory.getRootObject()
		d.addCallbacks(connected, failed)

		log.msg('registering with RadioManager')

		return d

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
			self.props['addr'] = self._get_ip_address('wlan0')
		except IOError:
			#my laptop has a different form
			self.props['addr'] = self._get_ip_address('wlp1s0')

		self.props['maxPacketLength'] = 4096
		self.props['costPerByte'] = 1
		self.props['port'] = WiFiManager.myPort



class WiFiTransport (DatagramProtocol):
	myPort = 10248

	def __init__(self):
		self.manager = None

	def startProtocol (self):
		self.transport.setBroadcastAllowed(True)
		self.allowFromSelf = False
		

	def allowMsgFromSelf(self, b):
		self.allowFromSelf = b

	def setManager (self, manager):
		self.manager = manager

	def write (self, message, addr):
		data = json.dumps(message, separators=(',', ':'))
		self.transport.write(data, (addr, WiFiTransport.myPort))


	def datagramReceived(self, data, (host, port)):
		log.msg(data + " from %s %d" % (host, port))
		
		#don't do anything if not set up or if manager has already
		#been gc'd
		if self.manager is not None: 
			log.msg('I am: %s' % self.manager.props['addr'])

			if (not host == self.manager.props['addr']) or self.allowFromSelf:
				try:
					message = json.loads(data)
					message['sentby'] = host
					self.manager.sendToLocalReceivers(message)
				except ValueError:
					pass #drop poorly formed packets

