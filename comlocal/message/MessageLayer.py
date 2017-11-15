

class MessageLayer(object):
	def __init__(self, commonData):
		self._commonData = commonData
		self._msgId = 0

	def setRead(self, cb):
		self._readCB = cb

	def read(self):
		return self._readCB()

	def setWrite(self, cb):
		self._writeCB = cb

	def _addMsgId(self, msg):
		"""
		Add semi-unique msg ID to message so that
		messages can be properly filtered by receivers
		"""
		msg['msgId'] = self._msgId
		self._msgId = (self._msgId + 1) % 256
		return msg

	def write(self, msg):
		return self._writeCB(self._addMsgId(msg))
