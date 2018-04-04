from comlocal.util.NetworkLayer import NetworkLayer


class MessageLayer(NetworkLayer):
	def __init__(self, commonData):
		NetworkLayer.__init__(self, 'ML')
		self._commonData = commonData
		self._msgId = 0
		self._cache = []
		self._windowSize = 128

	def read(self, msg):
		#drop duplicate messages
		if (msg['src'],msg['msgId']) not in self._cache:
			#only maintain a fixed number of messages to check against
			if len(self._cache) == self._windowSize:
				self._cache.pop(0)

			self._cache.append((msg['src'],msg['msgId']))
			self.readCB( msg)

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
			if 'msg' in msg and 'dest' in msg:
				return self.writeCB(self._addMsgId(msg))
			elif 'cmd' in msg:
				return self.writeCB(msg)
			else:
				raise KeyError
		except KeyError:
			msg['result'] = self.failure('poorly formatted message')
			return msg
