from comlocal.radio.RadioManager import RadioManager, RadioTransport
import json

class LoopbackManager (RadioManager):

	def __init__ (self):
		RadioManager.__init__(self, 'Loopback')

	def _setupProperties(self):
		"""
		Set up the radio properties we might need
		"""
		props = {}
		props['addr'] = '<loopback>'
		props['bcastAddr'] = '<broadcast>'
		props['costPerByte'] = .5

		return props

class LoopbackTransport(RadioTransport):
	def write(self, message, addr):
		self.read(json.dumps(message))

	def read(self, data):
		if self.manager is not None:
			message = json.loads(data)
			message['sentby'] = self.manager.props['addr']

			self.manager.read(message)

def startTransport(theTransportObj):
	return None