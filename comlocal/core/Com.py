
from comlocal.radio import WiFi
from comlocal.connection import ConnectionLayer
from comlocal.routing import RoutingLayer
from comlocal.util import CommonData
from comlocal.message import MessageLayer
import random
import Queue
import threading

class Com(object):
	def __init__(self):
		self._commonData = self._initCommonData(CommonData.CommonData())
		self._connL = ConnectionLayer.ConnectionLayer(self._commonData, self._getRadios())
		self._routeL = RoutingLayer.RoutingLayer(self._commonData)
		self._messageL = MessageLayer.MessageLayer(self._commonData)

		#set up connections between layers
		self._routeL.setRead(self._connL.read)
		self._routeL.setWrite(self._connL.write)

		self._messageL.setRead(self._routeL.read)
		self._messageL.setWrite(self._routeL.write)

		#for allowing non-blocking writes and an async read callback
		#TODO: decide if we actually *need* buffering
		self._inQ = Queue.Queue()
		self._outQ = Queue.Queue()

		self._readHandler = None

		self._readThread = threading.Thread(target=self._procRead)
		self._writeThread = threading.Thread(target=self._procWrite)
	

	#

	def __del__(self):
		self.stop() #can't guarantee this will be called, but this is here jic

	def start(self):
		self._connL.startPing(1)
		self._routeL.startAging(3,3)

		self._threadsRunning = True
		self._readThread.start()
		self._writeThread.start()

	def stop(self):
		self._connL.stopPing()
		self._routeL.stopAging()

		self._threadsRunning = False
		self._readThread.join()
		self._writeThread.join()


	def _procRead(self):
		"""
		Call the read handler on each message received
		"""
		
		while self._threadsRunning:
			for msg in self._messageL.read():
				if None != self._readHandler:
					self._readHandler(msg)

	def _procWrite(self):
		while self._threadsRunning:
			pass

	def _initCommonData(self, commonData):
		"""
		Init the common data by, say, reading from a file

		TODO: read beginning config from file
		"""
		commonData.id = random.randrange(255)
		return commonData


	def _getRadios(self):
		"""
		List of radios to initialize and pass to connection manager.
		
		TODO: Read radio list from config file
		"""
		return [WiFi.WiFi()]

	def setID(self, uniqueID):
		"""
		Set the unique ID by which this node can be distinguished
		"""
		self._commonData = uniqueID #need to sanitize?

	def setReadHandler(self, cb):
		"""
		Read handler callback needs to accept the message as an arg
		"""
		self._readHandler = cb


	def read(self):
		"""
		Non-blocking read

		Returns list of messages as json objects (can return empty list)
		
		DEPRECATED: only use if NOT using .start/.stop
		"""
		return self._messageL.read()

	def write(self, msg):
		"""
		Write message as json object

		returns True if successful, False otherwise
		"""
		return self._messageL.write(msg)

#