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
		self._bytesToRead = []
		self._generatePacketBytes()
		self._readBytesPos = 0

	def _generatePacketBytes(self):
		"""
		Generates a packet of random length between the min (11 bytes) and
		the max packet size containing random addresses and data. Used by read
		"""
		self._bytesToRead = []
		header = [random.randint(0,255) for _ in range(8)] #gen random int addresses (8 bytes)
		header.append(random.randint(1,5)) #gen random ttl (1 byte)
		dataLen = random.randint(0,116)
		data = [ord(random.choice(string.ascii_uppercase + string.digits)) for _ in range(dataLen)]

		tmpSum = 0
		for b in data:
			tmpSum += b
		#

		self._bytesToRead += header
		self._bytesToRead.append(dataLen)
		self._bytesToRead += data
		self._bytesToRead.append(((1 << 8) - tmpSum) % 256)
	#

	def read(self, n):
		"""
		Read n bytes

		return n bytes of a randomly generated packet
		if n is greater than the remaining bytes in the packet then only
		the remaining bytes are returned and a new packet is generated
		"""
		gen = False
		if self._readBytesPos + n >= len(self._bytesToRead):
			end = len(self._bytesToRead)
			gen = True
		else:
			end = self._readBytesPos + n

		retBytes = self._bytesToRead[self._readBytesPos:end]

		if self._readBytesPos == end:
			retBytes = [retBytes]

		if gen:
			self._generatePacketBytes()
			self._readBytesPos = 0
		else:
			self._readBytesPos = end
		#

		return retBytes

	def write(self, data):
		"""
		Write data

		return number of bytes "written"
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