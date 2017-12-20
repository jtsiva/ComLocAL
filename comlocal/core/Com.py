
from comlocal.radio import WiFi, Bluetooth
from comlocal.connection import ConnectionLayer
from comlocal.routing import RoutingLayer
from comlocal.util import CommonData
from comlocal.message import MessageLayer
import random
import Queue
import threading
import logging
import json

class Com(object):
	def __init__(self, log = False, logFile = 'com.log', configFile = None):

		if log:
			logging.basicConfig(filename=logFile, level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%I:%M:%S %p')


		self._commonData = {}
		self._initCommonData(log, configFile)

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
		pass#self.stop() #can't guarantee this will be called, but this is here jic

	def start(self):
		self._connL.start(1)
		self._routeL.start(3,3)

		self._threadsRunning = True
		self._readThread.start()
		self._writeThread.start()

	def stop(self):
		self._connL.stop()
		self._routeL.stop()

		self._threadsRunning = False
		self._readThread.join()
		self._writeThread.join()
		if self._commonData['logging']['inUse']:
			#print summary information for this layer
			pass



	def _procRead(self):
		"""
		Call the read handler on each message received
		"""
		
		while self._threadsRunning:
			for msg in self._messageL.read():
				if self._readHandler is not None:
					self._readHandler(msg)

	def _procWrite(self):
		while self._threadsRunning:
			pass

	def _initCommonData(self, log, configFile):
		"""
		Init the common data by, say, reading from a file
		"""
		if configFile is not None:
			with open(configFile, 'r') as f:
				self._commonData = json.loads(f.read())
		else:
			self._commonData['id'] = random.randrange(255)
			self._commonData['location'] = [0,0,0]
			self._commonData['startRadios'] = ['WiFi', 'BT']
			self._commonData['activeRadios'] = []

		self._commonData['logging'] = {'inUse': False} if not log else {'inUse': True}
	#


	def _getRadios(self):
		"""
		List of radios to initialize and pass to connection manager.
		
		TODO: Read radio list from config file
		"""
		radios = []
		if 'WiFi' in self._commonData['startRadios']:
			radios.append(WiFi.WiFi())
		
		if 'BT' in self._commonData['startRadios']:
			radios.append(Bluetooth.Bluetooth())
		#
		
		return radios

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