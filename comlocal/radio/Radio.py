from comlocal.util import Properties
import json

class Radio(object):
	"""
	'Abstract' class used to provide the basic functionality of the
	radios to be used by ComLocAL. Reading and writing are found here

	  frame length
	  max range

	"""
	def __init__(self, props):
		self._name = 'NULL'
		self._props = props

	def start(self):
		#for starting connection oriented radios
		pass

	def stop(self):
		#for stopping connection oriented radios
		pass

	def read(self):
		"""
		Read from radio and return json object
		"""
		pass

	def _asString(self, msg):
		return json.dumps(msg, separators=(',', ':'))

	def write(self, data):
		"""
		write json object to radio
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
