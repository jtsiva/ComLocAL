from comlocal.util.NetworkLayer import NetworkLayer


class MessageLayer(NetworkLayer):
	def __init__(self, commonData):
		NetworkLayer.__init__(self, 'ML')
		self._commonData = commonData
		self._msgId = 0

	def read(self, data):
		self.readCB( data)

	def _addMsgId(self, msg):
		"""
		Add msg ID to message so that
		messages can be properly filtered by receivers
		"""
		msg['msgId'] = self._msgId
		self._msgId = (self._msgId + 1) % 256
		return msg

	def write(self, msg):
		try:
			if 'msg' == msg['type'] and 'msg' in msg and 'dest' in msg:
				return self.writeCB(self._addMsgId(msg))
			elif 'cmd' == msg['type'] and 'cmd' in msg:
				return self.writeCB(msg)
			else:
				raise KeyError
		except KeyError:
			msg['result'] = self.failure('poorly formatted message')
			return msg
