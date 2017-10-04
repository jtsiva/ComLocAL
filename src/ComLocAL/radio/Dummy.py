#!/usr/bin/python

from radio import Radio
import sys
import random
import string

class Dummy(Radio.Radio):
	"""
	Class used for testing modules that expect a radio
	interface. Provides consistent, known behavior that
	doesn't rely on actual network connections.
	"""

	def __init__(self):
		self._name = 'dummy'
		super(Dummy,self).__init__(127, 50, 1)

	def read(self, n):
		"""
		Read n bytes

		return n random bytes in a list
		"""
		return [random.choice(string.ascii_uppercase + string.digits) for _ in range(n)]

	def write(self, data):
		"""
		Write data

		return number of bytes written
		"""
		return len(data)

	def getProperties (self):
		"""
		Return the common properties of the radio:
			address
			max packet length in bytes
			max range (per pwr level?) in meters

		as a tuple: (addr, len, range)
		"""
		return ('255.255.255.' + str(random.randint(0,255)), self._frameLength, self._maxRange)


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