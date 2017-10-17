#!/usr/bin/python

import threading
from Queue import Empty
from Queue import Queue
from comlocal.util import Packet

class RadioManager:
	def __init__(self, myRad):
		self._inQ = Queue()
		self._outQ = Queue()
		self._radio = myRad
		self.start()
		
	#

	def __del__(self):
		self._threadsRunning = False
		self._readThread.join()
		self._writeThread.join()

	def start(self):
		self._threadsRunning = True
		self._readThread = threading.Thread(target=self._procRead)
		self._writeThread = threading.Thread(target=self._procWrite)
		
		self._readThread.start()
		self._writeThread.start()


	def stop(self):
		self._threadsRunning = False
		self._readThread.join()
		self._writeThread.join()

	def _procRead(self):
		"""
		Thread for processing read queue.
		Parse radio input and turn into packet objects which
		are placed in the read Q
		"""
		DATA_LEN_BYTE = 9

		pos = 0
		dataLen = 0
		inBytes = []
		while self._threadsRunning:
			b = self._radio.read(1)[0]

			inBytes.append(b)

			if pos == DATA_LEN_BYTE:
				dataLen = b
			#

			if pos == (DATA_LEN_BYTE + dataLen + 1):
				packet = Packet.Packet(fromBytes=inBytes)
				self._inQ.put(packet)
				pos = 0
				dataLen = 0
				inBytes = []
			else:
				pos += 1
			#	
		#
	#

	def _procWrite(self):
		"""
		Thread for processing write queue. 
		Pulls packet off and turns into byte stream which is
		written to radio
		"""
		while self._threadsRunning:
			try:
				packet = self._outQ.get(False)
				self._radio.write(packet.getDest(), packet.getBytes())
			except Empty:
				pass
		#
	#

	def read(self, n):
		"""
		Read n packets (or whatever is available) from the read Q and return as a list
		can return 0 packets if input doesn't contain a valid packet
		"""
		retList = []
		for i in range(n):
			retList.append(self._inQ.get())
		#

		return retList

	def write(self, packets):
		"""
		Add packet(s) to write Q.

		Return # of packets written
		"""
		for p in packets:
			self._outQ.put(p)
		#

		return len(packets)
	#

	def scan(self):
		"""
		pass-through
		"""
		return self._radio.scan()

	def range(self):
		"""
		pass-through
		"""
		return self._radio.range()


#
