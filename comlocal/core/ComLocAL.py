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
		"""
		Return n packets (CommandPackets). Blocks until n packets are read
		"""
		pass

	def send(self, packets):
		"""
		Write the list of packets until buffer is full. 
		Return number of packets sent
		"""
		pass

	def getNeighbors(self):
		"""
		Return a list of IDs of the neighbors. Can be empty
		"""
		neighbors = []
		
		return neighbors
#