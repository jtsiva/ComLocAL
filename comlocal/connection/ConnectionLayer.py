
from comlocal.radio import Radio
import threading
from multiprocessing import Lock
import time
import json
import logging
import pdb

class Stats(object):
	def __init__(self):
		self.read = 0
		self.write = 0
		self.lastUsed = 0
		self.packetsDropped = 0 #poorly formed packets
		self.up = True

class ConnectionLayer(object):
	"""
	This class is responsible for implementing network protocols,
	maintaining connections, and managing the state of the hardware

	"""

	def __init__(self, commonData, radioList):
		self._commonData = commonData
		self._radioList = radioList #prioritized list of radio objects
		self._radioStats = {}
		for radio in self._radioList:
			self._radioStats[radio._name] = Stats()
		#

		self._checkRadios() #weed out any radios that are not *actually* active
		self._commonData['activeRadios'] = [radio._name for radio in self._radioList] #initialize commonData
	
		self._radioLock = Lock()
	#

	def _checkRadios(self):
		"""
		Check if radios are properly functioning
		TODO: implement
		"""
		pass
	#

	def start(self, delay):
		"""
		Start sending out a ping to let other devices know
		we're here. Delay, in seconds, between pings set by delay (float possible)
		"""
		if self._commonData['logging']['inUse']:
			self._commonData['logging']['connection'] = {'pings' : 0, 'sent': 0, 'received' : 0}

		for radio in self._radioList:
			radio.start()
		self._pingDelay = delay
		self._runPing = True
		self._ping() #start pinging

	def stop(self):
		for radio in self._radioList:
			radio.stop()
		self._runPing = False
		if self._commonData['logging']['inUse']:
			logging.info('ConnectionLayer Summary: pings %d, sent %d, received %d', \
				self._commonData['logging']['connection']['pings'],\
				self._commonData['logging']['connection']['sent'],\
				self._commonData['logging']['connection']['received'])
			#print summary information for this layer
			pass

	def _ping(self):
		"""
		Send basic "Hello!" message on all radios
		"""
		if self._commonData['logging']['inUse']:
			self._commonData['logging']['connection']['pings'] += 1


		ping = json.loads('{"type":"ping"}')
		ping['src'] = self._commonData['id']

		with self._radioLock:
			for radio in self._radioList:
				radio.write(ping)
				if self._commonData['logging']['inUse']:
					logging.debug('connection--pinging on %s', radio._name)
			#
		#

		if self._runPing:
			#reschedule for later only if runPing is true
			threading.Timer(self._pingDelay, self._ping).start()
	#



	def _addRadioField(self, msg, radioName):
		"""
		Add a field to the message indicating which interface the message
		arrived on.
		"""
		try:
			del msg['radios'] #appended by sender but not needed on read
		except Exception as e:
			pass #do nothing (this *might* be useful later)

		msg['radio'] = radioName
		return msg


	def read(self):
		"""
		Read from each radio and return all objects. Filter and handle
		pings as this level.

		Non-blocking

		TODO: exception handling for broken things
		"""
		data = []

		for radio in self._radioList:
			msg = radio.read()
			if msg is not None:
				try:
					if msg['sentby'] != radio.getProperties().addr:
						if self._commonData['logging']['inUse']:
							self._commonData['logging']['connection']['received'] += 1
						data.append(self._addRadioField(msg, radio._name))
				except KeyError:
					pass		
		#

		return data
	#

	def chooseRadios(self, msg):
		"""
		Return an ordered list of which radios should be used based
		on the message contents (length of msg, QoS req's, possible
		restrictions, etc)

		TODO: make more sophisticated
		"""
		return self._radioList

	def write(self, msg):
		"""
		Write msg to radios

		return true if successful, false otherwise
		"""
		try:
			with self._radioLock:
				for radio in filter(lambda x: x._name in msg['radios'], self._radioList):
					if radio.getProperties().maxPacketLength >= len(msg):
						radio.write(msg)
						if self._commonData['logging']['inUse']:
							self._commonData['logging']['connection']['sent'] += 1
					#
				#
			#
			return True
		except Exception as e:
			return False

		








#