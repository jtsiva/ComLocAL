
class Properties(object):
	"""
		very open class used to encapsulate the properties
		held in common by the radios. This information is
		used to assist with higher level functionality
	"""

	def __init__(self):
		self.addr = ''
		self.maxFrameLength = 0
		self.costPerByte = 0

#