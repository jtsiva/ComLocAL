from util import Properties

class Radio(object):
	"""
	'Abstract' class used to provide the basic functionality of the
	radios to be used by CommLocAL. Reading and writing are found here

	  frame length
	  max range

	"""
	def __init__(self, props):
		self._name = 'NULL'
		self._props = props

	def read(self, n):
		"""
		Read n bytes as bytearray

		return n bytes or whatever is available to read (which is smaller)
		"""
		pass

	def write(self, dest, data):
		"""
		Write data (bytearray) to radio destined for dest

		return number of bytes written
		"""
		pass

	def getProperties (self):
		"""
		Return the common properties of the radio:
			address
			max payload len
			etc.

		as an object
		"""
		return self._props


	def scan(self):
		"""
		Send some sort of HELLO message to other radios listening for it.
		Think of this as the discovery protocol for a given radio.
		"""
		pass

	def range(self):
		"""
		Either define as a function of RSSI (determined empirically)
		or, in the case of UWB, just get the range from TWR. Return a
		tuple of (range, error) both in meters.
		"""
		pass

	def setPwrMode(self, mode):
		"""
		Set the power mode of the radio--intended to set the radio to
		a lower power mode
		"""
		pass

#
