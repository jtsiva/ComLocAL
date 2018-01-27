from comlocal.util.NetworkLayer import NetworkLayer


class MessageLayer(NetworkLayer):
	def __init__(self, commonData):
		self._commonData = commonData
		self._msgId = 0

	def read(self, data):
		self.readCB( data)

	def _addMsgId(self, msg):
		"""
		Add semi-unique msg ID to message so that
		messages can be properly filtered by receivers
		"""
		msg['msgId'] = self._msgId
		self._msgId = (self._msgId + 1) % 256
		return msg

	def write(self, msg):
		try:
			if 'msg' in msg['type'] and 'msg' in msg and 'dest' in msg:
				return self.writeCB(self._addMsgId(msg))
			elif 'cmd' in msg['type'] and 'cmd' in msg:
				return self.writeCB(msg)
			else:
				raise KeyError
		except KeyError:
			msg['result'] = 'failed: poorly formed message'
			return msg
