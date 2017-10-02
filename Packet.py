#!/usr/bin/python

def enum(**enums):
    return type('Enum', (), enums)

PACKET_TYPE = enum(COMMON=127,LONG=1024)


class Packet(None):
	def __init__ (packetType = PACKET_TYPE.COMMON):
		_dest = ''
		_src = ''
		_ttl = 5
		_data = ''
		_type = packetType
		_chksum = 0
		_valid = False

	def isValid():
		"""
		Return True if both addresses are set, ttl is >0, and checksum
		is valid. False otherwise.
		"""
		return _valid and (_chksum == calcChkSum())

	def setDest (destAddr):
		_dest = destAddr

		if 0 != len(_dest) and 0 != len(_src):
			_valid = True

	def setSrc (srcAddr):
		_src = srcAddr
		if 0 != len(_dest) and 0 != len(_src):
			_valid = True

	def calcChkSum ():
		"""
		Calculate checksum return
		"""
		pass

	def setData (data):
		"""
		Set the data payload. If data is too long then the truncation
		is copied and the remainder returned.
		"""
		_data = data[:_type - 1]
		_chksum = calcChkSum()
		return data[_type:]

	def decrementTTL():
		_ttl -= 1
		if 0 == _ttl:
			_valid = False

	def getBytes():
		"""
		Return bytearray of packet contents.
		"""
		return bytearray()



#