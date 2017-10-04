#!/usr/bin/python

from util import Packet

class PacketBuilder(object):
	"""
	Abstract class. Intended to remove the packet structure and parsing
	from the Packet object.

	Not sure if this will be necessary
	"""

	def __init__(self):
		pass

	def getEmptyPacketOfType(self, type):
		pass

	def buildFromBytes(self, inputBytes):
		pass

#