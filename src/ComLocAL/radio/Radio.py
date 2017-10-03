#!/usr/bin/python

#from io import BytesIO

class Radio:
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

class WiFi (Radio):
	"""
	Facilitates / abstracts all communication over WiFi
	All communication is broadcast UDP

	"""
	def __init__ (self):
		self._name = 'WiFi'
		pass
#

class ZigBee (Radio):
	"""
	Abstracts all communication over ZigBee
	Scan could be useful for building up the network structure

	options include:
	  TX pwr
	"""
	def __init__ (self):
		self._name = 'ZB'
		pass
#

class Bluetooth (Radio):
	"""
	Abstracts all communication over Bluetooth / BLE

	All communication is broadcast
	"""
	def __init__ (self):
		self._name = 'BT'
		pass
#

class UWB (Radio):
	"""
	Abstracts all communication over UWB

	options include:
	  Ranging frequency | range after message
	"""
	def __init__(self):
		self._name = 'UWB'
		pass
#

def create(name):
	if 'WiFi' == name:
		myObj = Wifi()
	elif 'ZigBee' == name:
		myObj = ZigBee()
	elif 'Bluetooth' == name:
		myObj = Bluetooth()
	elif 'UWB' == name:
		myObj = UWB ()
	else:
		myObj = Radio()

	return myObj
