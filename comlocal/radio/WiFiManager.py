from twisted.application import internet, service
from twisted.internet.protocol import ServerFactory, DatagramProtocol
from twisted.python import log
import json

class WiFiManagerProtocol(DatagramProtocol):
	def __init__(self, service):
		self._service = service

	def startProtocol (self):
		self.transport.setBroadcastAllowed(True)

	def datagramReceived(self, data, (host, port)):
		if port == self._service._localPort:
			self.transport.write(data, ('<broadcast>', self.service._outsidePort))
		else:
			for addr in self._service.getLocalReceivers():
				self.transport.write(data, addr)


class WiFiManagerService (service.Service):
	def __init__ (self, localPort, outsidePort):
		self._localPort = localPort
		self._outsidePort = outsidePort
		self._localReceivers = []

	def startService (self):
		service.Service.startService(self)

	def getLocalReceivers(self):
		return self._localReceivers

	def addLocalReceiver (self, entry):
		self._localReceivers.append(entry)