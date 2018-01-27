from twisted.application import internet, service
from twisted.internet.protocol import ServerFactory, DatagramProtocol

class ComLocAL(object):
	def __init__(self):
		self._readCB = None # called when data arrives
		self._resultsCB = None # called when write completes (includes commands)
		self._locationCB = None # called if periodic location updates are desired
		self._period = 1.0

	def setReadCB (self, cb):
		self._readCB = cb

	def setResultsCB (self, cb):
		self._resultsCB = cb

	def setLocationCB (self, cb, period):
		self._locationCB = cb
		self._period = period

	def comWrite(self, msg):
		"""
		expect msg to be json object (a dict)
		with the following fields:

			{
				"type" : <"msg" | "cmd">,
				<"msg" | "cmd"> : <stuff>,
				("dest" : <id>) <-
			}                    |
			                     |
			                     - only necessary when type == msg

		The currently available commands are:
			getNeighbors - returns a list of ids of nodes within 1 hop
		"""
		pass

	def locWrite(self, cmd):
		"""
		always a command -- format TBD
		"""
		pass


class ComLocALService(service.Service)
	def __init__(self):
		pass

class ComLocALProtocol(DatagramProtocol)
	def __init__(self):
		pass