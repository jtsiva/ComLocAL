#!/usr/bin/python

#from io import BytesIO

class Radio(None):
	"""
	'Abstract' class used to provide the basic functionality of the
	radios to be used by CommLocAL. Reading and writing are found here,
	of course, as well as setting up static features common with all
	radios (they ought to be experimentally verified):

	  frame length
	  max range
	  data rate (open to setting multiple speeds?)
	  pwr consumption (mW per byte? frame?)

	dynamic features to keep in mind:
	  Distance between sender and receiver
	  Radio traffic/usage
	  comm quality (SNR, dropped packets)


	Encapsulate settings here as well? Modes, channels, etc.

	Set callback for errors, sent frames, and arriving frames?
	  <for now> treating like character device driver

	"""
	def __init__(frameLength, dataRate, maxRange, pwrUsage):
		_name = 'NULL'
		_frameLength = frameLength
		_dataRate = dataRate
		_maxRange = maxRange
		_pwrUsage = pwrUsage

	def read(n):
		"""
		Read n bytes

		return n bytes or whatever is available to read (which is smaller)
		"""
		pass

	def write(data):
		"""
		Write data

		return number of bytes written
		"""
		pass

	def getAddress ():
		"""
		Return the address of the radio
		"""
		pass

	def cost(length, dest):
		"""
		Given the length of a message and the destination, determine a cost
		(arbitrary units-- call them grumbles) for using this radio to send
		the message

		Returns an integer
		"""
		pass

	def scan():
		"""
		Send some sort of HELLO message to other radios listening for it.
		Think of this as the discovery protocol for a given radio.
		"""
		pass

	def connect (dest):
		"""
		Connect with the device dest if not already
 
		return status (0 okay, < 0 problem)
		"""
		pass

	def tune(options):
		"""
		Settings
		"""
		pass

	def range():
		"""
		Either define as a function of RSSI (determined empirically)
		or, in the case of UWB, just get the range from TWR.
		"""
		pass

#

class WiFi (Radio):
	"""
	Facilitates / abstracts all communication over WiFi
	Need to set port/address that is used for communication

	options include:
	  TCP | UDP | File stream | Video stream
	  TX pwr

	"""
	def __init__ ():
		_name = 'WiFi'
		pass
#

class ZigBee (Radio):
	"""
	Abstracts all communication over ZigBee
	Scan could be useful for building up the network structure

	options include:
	  TX pwr
	"""
	def __init__ ():
		_name = 'ZB'
		pass
#

class Bluetooth (Radio):
	"""
	Abstracts all communication over Bluetooth / BLE

	options include:
	  BLE beacon / other BLE functions
	"""
	def __init__ ():
		_name = 'BT'
		pass
#

class UWB (Radio):
	"""
	Abstracts all communication over UWB

	options include:
	  Ranging frequency | range after message
	"""
	def __init__():
		_name = 'UWB'
		pass
#

def create(name, options = []):
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

	myObj.tune(options)
	return myObj