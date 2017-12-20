
import json
import time
import threading
from multiprocessing import Lock
import pdb

class Stats(object):
	def __init__(self):
		self.packetsDropped = 0 #poorly formed packets

class RoutingLayer(object):
	def __init__(self, commonData):
		self._commonData = commonData
		self._routingTable = {}
		self._stats = Stats()
		self._tableLock = Lock()

	def setRead(self, cb):
		self._readCB = cb

	def read(self):
		"""
		Read from the callback and filter through the
		messages to determine who needs to handle what. All messages
		intended for this agent will be returned.

		Non-blocking

		Returns a list of message (can be an empty list)
		"""
		messages = self._readCB()

		#TODO: filter out poorly formed messages
		#TODO: update routing table with non-ping messages

		r = map(lambda h: self._handlePing(h), filter(lambda x: self._isPing(x), messages))

		#get messages that need to be forwarded and forward
		r += map(lambda h: self._handleFoward(h), filter(lambda x: self._needsForward(x), messages))
		try:
			#get messages that need to handled by command handler and handle
			r += map(lambda h: self._handleCmd(h), filter(lambda x: (not self._needsForward(x)) and self._isCommand(x), messages))
		except Exception as e:
			print 'Command handler not set?'
			raise e

		if self._commonData['logging']['inUse']:
			self._commonData['logging']['routing']['msgRcv'] += (len(messages) - len(r))

		#return the rest of the messages because these are local
		return filter(lambda x: x not in r, messages)

	def start(self, delay, maxAge):
		"""
		Start aging the route table where entries older than maxAge
		are removed. Delay, in seconds, between checks set by delay
		(float possible)
		"""
		if self._commonData['logging']['inUse']:
			self._commonData['logging']['routing'] = {'pingsRcv' : 0, 'msgSnt': 0, 'msgRcv' : 0, 'cmdRcv' : 0, 'entriesDel' : 0, 'entriesAdd' : 0, 'fwd': 0}
		self._agingDelay = delay
		self._maxAge = maxAge
		self._runAging = True
		self._ageTable()
	#

	def stop(self):
		self._runAging = False
		if self._commonData['logging']['inUse']:
			logging.info("RoutingLayer Summary: pingsRcv - %d, msgSnt - %d, msgRcv - %d, cmdRcv - %d, entriesDel - %d, entriesAdd - %d, fwd - %d",
				self._commonData['logging']['routing']['pingsRcv'],\
				self._commonData['logging']['routing']['msgSnt'],\
				self._commonData['logging']['routing']['msgRcv'],\
				self._commonData['logging']['routing']['cmdRcv'],\
				self._commonData['logging']['routing']['entriesDel'],\
				self._commonData['logging']['routing']['entriesAdd'],\
				self._commonData['logging']['routing']['fwd'])


	def _ageTable(self):

		toDelete = {}

		for ID, radios in self._routingTable.iteritems():
			for radio, attr in radios.iteritems():
				if time.time() - attr['time'] > self._maxAge:
					toDelete[ID] = radio

		with self._tableLock:
			for ID, radio in toDelete.iteritems():
				del self._routingTable[ID][radio]
				if self._commonData['logging']['inUse']:
					self._commonData['logging']['routing']['entriesDel'] += 1

				#TODO: decide if we want to to completely remove entry
				# if {} == self._routingTable[ID]:
				# 	del self._routingTable[ID]

		#TODO: remove after debugging?
		print self._getRoutes()

		if self._runAging:
			#reschedule for later only if runAging is true
			threading.Timer(self._agingDelay, self._ageTable).start()
		#

	def _getRoutes(self):
		"""
		Return the routing table in a nice format

		DEBUG function
		"""
		return json.dumps(self._routingTable, sort_keys=True, indent=4, separators=(',', ': '))


	def _handlePing(self, msg):
		"""
		Use the ping to update the routing table
		
		"""
		#pdb.set_trace()

		if self._commonData['logging']['inUse']:
			self._commonData['logging']['routing']['pingsRcv'] += 1
		self._updateRoutingTable(msg)

		return msg

	def _isPing(self, msg):
		try:
			return msg["type"] == "ping"
		except KeyError:
			return False

	def _updateRoutingTable(self, msg):
		"""
		Update the routing table based on information from
		the message. ASSUMES that msg has already been checked
		for validity
		"""

		with self._tableLock:
			if not (msg['src'] in self._routingTable):
				self._routingTable[msg['src']] = {}

			if not (msg['radio'] in self._routingTable[msg['src']]):
				self._routingTable[msg['src']][msg['radio']] = {}
				if self._commonData['logging']['inUse']:
					self._commonData['logging']['routing']['entriesAdd'] += 1

			self._routingTable[msg['src']][msg['radio']]['addr'] = msg['sentby']
			self._routingTable[msg['src']][msg['radio']]['time'] = time.time()

	#

	def _needsForward(self, msg):
		"""
		Check if the message is intended for this node or not
		"""
		try:
			return msg['dest'] != self._commonData.id
		except KeyError:
			return False

	def _handleForward(self, msg):
		if self._commonData['logging']['inUse']:
			self._commonData['logging']['routing']['fwd'] += 1
		self.write(msg)
		return msg

	def _route(self, msg):
		"""
		Determine route/radio to use. This information is added to the msg
		
		TODO: add actual routing algorithms here
		"""
		msg['src'] = self._commonData.id
		msg['radios'] = self._commonData.activeRadios
		return msg

	def setWrite(self, cb):
		self._writeCB = cb

	def write(self, msg):
		if self._commonData['logging']['inUse']:
			self._commonData['logging']['routing']['msgSnt'] += 1
		return self._writeCB(self._route(msg))


# NOT SURE IF I WANT TO HANDLE THIS HERE OR THE MESSAGE LAYER
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def setCmdHandler(self, cb):
		"""
		Need to set a callback that will handle a message
		that is a command
		"""
		self._cmdHandler = cb

	def _isCommand(self, msg):
		try:
			return msg['type'] == "cmd"
		except KeyError:
			return False

	def _handleCommmand(self, msg):
		"""
		Pass message containing a command of to the appropriate
		callback
		"""
		try:
			self._cmdHandler(msg)
		except Exception as e:
			raise e
		finally:
			return msg

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#