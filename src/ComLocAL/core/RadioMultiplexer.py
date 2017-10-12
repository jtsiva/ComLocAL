
from radio import *
from util import *
import Queue
import threading

class RadioMultiplexer(object):
	def __init__ (self):
		self._rcvQ = Queue.Queue()
		self._sndQ = Queue.Queue()
		self._addrTable = {}

	def read(self, n)
		pass

	def write(self, packets):
		pass

	def getNeighbors(self, hops, dist):
		pass

#