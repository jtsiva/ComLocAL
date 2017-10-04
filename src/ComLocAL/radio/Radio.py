#!/usr/bin/python

class Radio(object):
	"""
	'Abstract' class used to provide the basic functionality of the
	radios to be used by CommLocAL. Reading and writing are found here

	  frame length
	  max range

	"""
	def __init__(self, frameLength, maxRange, pwrUsage):
		self._name = 'NULL'
		self._frameLength = frameLength
		self._maxRange = maxRange
		self._pwrUsage = pwrUsage

	def read(self, n):
		"""
		Read n bytes

		return n bytes or whatever is available to read (which is smaller)
		"""
		pass

	def write(self, data):
		"""
		Write data

		return number of bytes written
		"""
		pass

	def getProperties (self):
		"""
		Return the common properties of the radio:
			address
			max payload len
			max range (per pwr level?)

		as a tuple: (addr, len, range)
		"""
		pass


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
