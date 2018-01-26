
class NetworkLayer (object):
	def __init__ (self):
		self.readCB = None
		self.writeCB = None
	
	def	setReadCB (self, cb):
		"""
		Should be of the form: cb(data)
		"""
		self.readCB = cb

	def setWriteCB (self, cb):
		"""
		Should be of the form: cb(data)
		"""
		self.writeCB = cb 
