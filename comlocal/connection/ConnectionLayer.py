import time
import json

class Radio(object):
	def __init__ (self, name, loc):
		self._connections = {'<broadcast>' : 0}

		self._name = name
		self._loc = loc
		self._writeCB = None
		self._readCB = None

	def setReadCB (self, cb):
		self._readCB = cb

	def setWriteCB (self, cb):
		self._writeCB = cb

	def keepAlive(self, connection):
		# send a message with msg = 'keepalive' ?
		pass

	def addConnection(self, connection):
		if connection not in self._connections:
			self._connections[connection] = time.time()
			#self.keepAlive()

	def removeConnection (self, connection):
		del self._connections[connection]

	def read(self, data):
		#add/remove fields from data
		self._connections[data['sentby']] = time.time()
		self._readCB(data)

	def write(self, data):
		#add/remove fields from data
		del data['radios']
		self._writeCB(data, self._loc)

	def connectionThreshold (self, cutoff):
		#delete connections that have been idle longer than cutoff
		toDelete = []
		for key, val in self._connections.iteritems():
			if time.time() - val > cutoff:
				toDelete.append(key)

		for key in toDelete:
			del self._connections[key]

def popVal(myDict, key):
	val = myDict[key]
	del myDict[key]
	return val, myDict

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
		self._pingStopped = False #used to confirm stopped
		self._runPing = False
		while not self._pingStopped: #spin until confirmed
			pass

		for radio in self._radioList:
			radio.stop()

		if self._commonData['logging']['inUse']:
			logging.info('ConnectionLayer Summary: pingsSnt %d, sent %d, received %d', \
				self._commonData['logging']['connection']['pings'],\
				self._commonData['logging']['connection']['sent'],\
				self._commonData['logging']['connection']['received'])


	def _ping(self):
		"""
		Send basic "Hello!" message on all radios
		"""

		ping = json.loads('{"type":"ping"}')
		ping['src'] = self._commonData['id']

		with self._radioLock:
			for radio in self._radioList:
				radio.write(ping)
				if self._commonData['logging']['inUse']:
					self._commonData['logging']['connection']['pings'] += 1
				if self._commonData['logging']['inUse']:
					logging.debug('connection--pinging on %s', radio._name)
			#
		#

		if self._runPing:
			#reschedule for later only if runPing is true
			threading.Timer(self._pingDelay, self._ping).start()
		else:
			self._pingStopped = True
	#



	def _addRadioField(self, msg, radioName):
		"""
		Add a field to the message indicating which interface the message
		arrived on.
		"""
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

	def _cleanOutoing (self, msg):
		if 'radio' in msg: #from forwarding
			del msg['radio']
		if 'sentby' in msg: #from forwarding
			del msg['sentby']

		radios = msg['radios']
		del msg['radios'] #for choosing how to send, but don't want to send this

		return radios, msg
	#

	def write(self, msg):
		"""
		Write msg to radios

		return true if successful, false otherwise
		"""
		try:
			if  msg['type'] == "cmd":
				msg['result'] = 'failed:  command no recognized'
			else:
				with self._radioLock:
					radios, msg = self._cleanOutoing(msg)
					# print msg
					# print len(json.dumps(msg))
					for radio in filter(lambda x: x._name in radios, self._radioList):
						if radio.getProperties().maxPacketLength >= len(json.dumps(msg,separators=(',', ':'))):
							radio.write(msg)
							if self._commonData['logging']['inUse']:
								self._commonData['logging']['connection']['sent'] += 1
						#
					#
				#
				msg['result'] = 'success'
		except Exception as e:
			msg['result'] = 'failed: ' + e

		return msg

		








#