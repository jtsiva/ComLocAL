

class MessageLayer(object):
	def __init__(self, commonData):
		self._commonData = commonData

	def setRead(self, cb):
		self._readCB = cb

	def read(self):
		return self._readCB()

	def setWrite(self, cb):
		self._writeCB = cb

	def write(self, msg):
		return self._writeCB(msg)