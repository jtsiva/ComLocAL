
class NetworkLayer (object):
	def __init__ (self, name):
		self.name = name
		self.readCB = None
		self.writeCB = None

	def failure(self, msg):
		return self.name + "failure: " + msg

	def success(self, msg):
		return self.name + "success: " + msg
	
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
