#!/usr/bin/python

from core import RadioMultiplexer
from util import CommandPacket

class ComLocAL (object):
	"""
	Interface to application layer. 
	"""
	def __init__(self):
		self._radMuxer = RadioMultiplexer.RadioMultiplexer()

	def receive(self, n):
		pass

	def send(self, packets)
		pass

	def getNeighbors(self):
		pass
#