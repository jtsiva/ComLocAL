from comlocal.radio.RadioManager import RadioManager
import json

class LoopbackManager (RadioManager):

	def __init__ (self):
		RadioManager.__init__(self, 'Loopback')

	def _setupProperties(self):
		"""
		Set up the radio properties we might need
		"""
		self.props['addr'] = '<loopback>'
		self.props['bcastAddr'] = '<broadcast>'
		self.props['maxPacketLength'] = 15000
		self.props['costPerByte'] = .5

class LoopbackTransport(object):
	def __init__(self):
		self.manager = None

	def setManager (self, manager):
		self.manager = manager

	def write(self, message):
		self.read(json.dumps(message))

	def read(self, data)
		if self.manager is not None:
			message = json.loads(data)
			message['sentby'] = 'loopback'

			self.manager.read(message)

def startTransport(theTransportObj):
	return None