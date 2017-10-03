#!/usr/bin/python

import re

def enum(**enums):
    return type('Enum', (), enums)

PACKET_TYPE = enum(COMMON=116,LONG=1024)
ADDRESS_TYPE = enum(DEC=1, HEX=2)


class Packet:
	def __init__ (self, packetType = PACKET_TYPE.COMMON, addressType = ADDRESS_TYPE.DEC, fromBytes = []):
		self._dest = []
		self._src = []
		self._addrType = addressType
		self._ttl = 5 #max hops in network
		self._data = ''
		self._type = packetType
		self._chksum = 0 #complement of 0, + 1 for 1 byte chksum
		self._addrSet = False

		if 0 != len(fromBytes):
			parseFromBytes(fromBytes)
		#
	#

	def isValid(self):
		"""
		Return True if both addresses are set, ttl is >0, and checksum
		is valid. False otherwise.
		"""
		return (self._addrSet and self._ttl > 0 and (self._chksum == self._calcChkSum()))
	#

	def _digitForAddress(self, val):
		retVal = 0
		if ADDRESS_TYPE.DEC == self._addrType:
			retVal = int(val, 10)
		elif ADDRESS_TYPE.HEX == self._addrType:
			retVal = int(val, 16)

		return retVal

	def setDest (self, destAddr):
		self._dest = re.sub('[^0-9a-zA-Z]+', ' ', destAddr).split()
		self._dest = [self._digitForAddress(val) for val in self._dest]
		if 0 != len(self._dest) and 0 != len(self._src):
			self._addrSet = True
		#
	#

	def setSrc (self, srcAddr):
		self._src = re.sub('[^0-9a-zA-Z]+', ' ', srcAddr).split()
		self._src = [self._digitForAddress(val) for val in self._src]
		if 0 != len(self._dest) and 0 != len(self._src):
			self._addrSet = True
		#
	#

	def _calcChkSum (self):
		"""
		Calculate checksum and return
		checksum = inverse of sum(data) + 1
		"""
		tmpSum = 0
		for b in self._data:
			tmpSum += ord(b)
		#

		return ((1 << 8) - tmpSum) % 256
	#

	def setData (self, data):
		"""
		Set the data payload. If data is too long then the truncation
		is copied and the remainder returned.
		"""
		self._data = data[:self._type - 1]
		self._chksum = self._calcChkSum()
		return data[self._type:]
	#

	def decTTL(self):
		self._ttl -= 1
	#

	def parseFromBytes(self, dataBytes):
		pass
	#

	def getBytes(self):
		"""
		Return bytearray of packet contents.
		"""
		return bytearray(self._dest) + bytearray(self._src) + \
		bytearray(self._ttl) + bytearray(self._data) + \
		bytearray(self._chksum)
	#



#