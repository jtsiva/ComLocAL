from twisted.application import internet, service
from twisted.internet import task
from twisted.internet.protocol import ServerFactory, DatagramProtocol
from twisted.python import log
from comlocal.radio.RadioManager import RadioManagerProtocol
from comlocal.util.NetworkLayer import NetworkLayer
from comlocal.connection import ConnectionLayer
from comlocal.routing import RoutingLayer
from comlocal.message import MessageLayer
import random
import json


class ComService(service.Service, NetworkLayer):
	def __init__(self, log = False, configFile = None):

		self._registeredApplications = {}

		self._commonData = {}
		self._initCommonData(log, configFile)

		self._CL = ConnectionLayer.ConnectionLayer(self._commonData)
		self._RL = RoutingLayer.RoutingLayer(self._commonData)
		self._ML = MessageLayer.MessageLayer(self._commonData)

		#add radios (will also track ports)

		#set up connections between layers
		self._CL.setReadCB(self._RL.read)
		self._CL.setWriteCB(self.write)

		self._RL.setReadCB(self._ML.read)
		self._RL.setWriteCB(self._CL.write)

		self._ML.setReadCB(self.read)
		self._ML.setWriteCB(self._RL.write)
	
	#

	def isApplication(self, port):
		pass

	def isRadio(self, port):
		return self._CL.isRadio(port)

	def directCommToRadio(self, message, port):
		self._CL.directCommTo(message, port)

	def directCommToStack (self, message):
		return self._ML.write(message)

	def startService (self):
		service.Service.startService(self)


	def _initCommonData(self, log, configFile):
		"""
		Init the common data by, say, reading from a file
		"""
		if configFile is not None:
			with open(configFile, 'r') as f:
				self._commonData = json.loads(f.read())
		else:
			self._commonData['id'] = random.randrange(255)
			self._commonData['location'] = [0,0,0]
			self._commonData['startRadios'] = ['WiFi', 'BT']
			self._commonData['activeRadios'] = []

		self._commonData['logging'] = {'inUse': False} if not log else {'inUse': True}
	#

	def handleCmd(self, cmd):
		try:
			if 'reg_app' == cmd['cmd']:

				self._registeredApplications[cmd['name'][:4]] = cmd['port']
				cmd['result'] = "success"
			else:
				cmd['result'] = "failed : unrecognized command %s" % cmd['cmd']

		except KeyError:
			cmd['result'] = "failed: poorly formed message"

		return cmd

	
	def setupRadios (self, message):
		pass

	def read(self, msg):
		self.readCB(msg)

	def write(self, msg):
		port = msg['radio']
		del msg['radio']
		self.writeCB(msg, port)
#

class ComProtocol(DatagramProtocol):
	def __init__(self, service):
		self._service = service
		self._service.setReadCB(self.stackRead)
		self._service.setWriteCB(self.stackWrite)

	def checkRegisteredRadios (self):
		regPacket = {}
		regPacket['type'] = 'cmd'
		regPacket['auth'] = self._service._authKey
		regPacket['cmd'] = 'get_radios'
		
		self.transport.write(json.dumps(regPacket), ('127.0.0.1', RadioManagerProtocol.myPort))
		log.msg('Checking RadioManager for available radios')	

	def startProtocol (self):
		#give the other service three seconds to start up
		from twisted.internet import reactor
		self._later = task.LoopingCall (self.checkRegisteredRadios)
		task.deferLater(reactor, 5.0, self._later.start, 15.0) #check every 15 seconds

	def stackRead(self, msg):
		#if the key 'app' doesn't exist then the message is copied to all
		#registered applications
		data = json.dumps(msg, separators=(',', ':'))
		if 'app' in msg:
			self.transport.write(data, ('127.0.0.1', self._service.registeredApplications[msg['app']]))
		else:
			for key, val in self._service.registeredApplications.itertools():
				self.transport.write(data, ('127.0.0.1', val))


	def stackWrite(self, msg, port):
		#Send to the appropriate radio to *actually* send somewhere
		data = json.dumps(msg, separators=(',', ':'))
		self.transport.write(data, ('127.0.0.1', port))

	def datagramReceived(self, data, (host, port)):
		message = json.loads(data)
		result = None
		try:
			if RadioManagerProtocol.myPort == port:
				if 'fail' not in message['result']:
					self._service.setupRadios(message['result'])
				else:
					log.msg(message['result'])
			elif self._service.isApplication(port):
				result = self._service.directCommToStack(message)
			elif self._service.isRadio(port):
				self._service.directCommToRadio(message, port)
			else:
				if 'cmd' == message['type']:
					message['port'] = port
					result = self._service.handleCmd(message)
				else:
					result = message
					result['result'] = 'failed: unknown sender. register app with service'
		except KeyError:
			result['result'] = 'failed: poorly formatted message'

		self.transport.write(result, (host,port))




port = 10257
iface = "127.0.0.1"
configFile = None

topService = service.MultiService()

comService = ComService(port)
comService.setServiceParent(topService)

udpService = internet.UDPServer(port, ComProtocol(comService))
udpService.setServiceParent(topService)

application = service.Application('com')
topService.setServiceParent(application)