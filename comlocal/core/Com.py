from twisted.application import internet, service
from twisted.internet import task
from twisted.internet.protocol import ServerFactory, DatagramProtocol
from twisted.python import log

from comlocal.connection import ConnectionLayer
from comlocal.routing import RoutingLayer
from comlocal.message import MessageLayer
import random
import json

class ComService(service.Service):
	def __init__(self, log = False, configFile = None):

		self._commonData = {}
		self._initCommonData(log, configFile)

		self._CL = ConnectionLayer.ConnectionLayer(self._commonData)
		self._RL = RoutingLayer.RoutingLayer(self._commonData)
		self._ML = MessageLayer.MessageLayer(self._commonData)

		#add radios (will also track ports)

		#list of registered applications

		#set up connections between layers
		self._CL.setReadCB(self._RL.read)
		self._CL.setWriteCB(self.write)

		self._RL.setReadCB(self._ML.read)
		self._RL.setWriteCB(self._CL.write)

		self._ML.setReadCB(self.read)
		self._ML.setWriteCB(self._RL.write)
	
	#

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
	

	def read(self, msg):
		self.readCB(msg)

	def write(self, msg):
		self.writeCB(msg)
#

class ComProtocol(DatagramProtocol):
	def __init__(self, service):
		self._service = service

	def startProtocol (self):
		#give the other service three seconds to start up
		# from twisted.internet import reactor
		# self._later = task.LoopingCall (self.checkRegistration)
		# task.deferLater(reactor, 3.0, self.sendRegistration)
		# task.deferLater(reactor, 5.0, self._later.start, 5.0)
		pass

	def datagramReceived(self, data, (host, port)):
		pass


port = 10257
iface = "127.0.0.1"

topService = service.MultiService()

comService = ComService(port)
comService.setServiceParent(topService)

udpService = internet.UDPServer(port, ComProtocol(comService))
udpService.setServiceParent(topService)

application = service.Application('com')
topService.setServiceParent(application)