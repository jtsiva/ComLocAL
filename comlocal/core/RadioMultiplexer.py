
from radio import *
from util import *
import Queue
import threading

class RadioMultiplexer(object):
	def __init__ (self):
		self._rcvQ = Queue.Queue()
		self._sndQ = Queue.Queue()
		self._addrTable = {} #2D dict - [UAV_ID][radio-name] = addr
		self._revAddrTable = {} # 2D dict - [addr][radio-name] = UAV_ID
		self._radios = []

	def _procRcv(self):
		"""
		Read through all of the radios and add to rcvQ. Packet addresses
		are changed to UAV IDs
		"""
		for radio in self._radios:
			incoming = radio.read(1)
			#get radio name
			#uavID = self._revAddrTable[incoming srcAddr][radio name]
			#

	def _procSnd(self):
		"""
		Empty sndQ according to radio priorities. Only send on priority 1
		radio unless UAV_ID is the special "address all" address 
		"""
		pass

	def setRadios(self, orderedRadios):
		"""
		Set the radios to be made available to this controller.
		orderedRadios is an ordered list of radio names used to 
		initialize the radios for control by this module and to
		set the priority of the radios.
		"""
		pass

	def read(self, n):
		"""
		Non-blocking read of n Packets (or whatever is available)
		"""
		pass

	def write(self, packets):
		pass

	def getNeighbors(self, hops, dist):
		pass

#