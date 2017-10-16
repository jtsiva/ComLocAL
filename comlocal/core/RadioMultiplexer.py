
from radio import *
from util import *
import Queue
import threading

class RadioMultiplexer(object):
	def __init__ (self):
		self._rcvQ = Queue.Queue()
		self._sndQ = Queue.Queue()
		self._cmdQ = Queue.Queue()
		self._addrTable = {} #2D dict - [UAV_ID][radio-name] = addr
		self._revAddrTable = {} # 2D dict - [addr][radio-name] = UAV_ID
		self._radios = []

	def _procRcv(self):
		"""
		Read through all of the radios and add to rcvQ. Packets are turned
		into CommandPackets, so addresses are changed to UAV IDs
		"""
		for radio in self._radios:
			incoming = radio.read(1)
			#get radio name
			#uavID = self._revAddrTable[incoming srcAddr][radio name]
			#

	def _procSnd(self):
		"""
		Empty sndQ according to radio priorities. Only send on priority 1
		radio unless UAV_ID is the special "address all" address. All
		CommandPackets in the Q are turned into more detailed Packets
		"""
		pass

	def _procCmd(self):
		"""
		Empty the cmdQ by processing the CommandPackets. If the command
		is a remote command, it is verified here before sending.
		"""
		pass

	def addRadio (self, radioName, priority):
		"""
		Add a radio by name and give it a priority. Only one radio of each
		type can be created. An old radio must be removed first.

		Return True if radio successfully initialized, False otherwise
		"""
		pass

	def rmRadio (self, radioName):
		"""
		Remove a radio by name. Priorities of remaining radios are not
		altered.

		True if successfully removed, False otherwise
		"""
		pass

	def read(self, n):
		"""
		Non-blocking read of n Packets (or whatever is available).
		Returns CommandPackets
		"""
		pass

	def write(self, packets):
		"""
		Write the list of CommandPackets to the send queue or the command
		queue (depending on packet type) as long as there is room.
		"""
		pass

	def getNeighbors(self, hops, dist):
		pass

#