from comlocal.util.NetworkLayer import NetworkLayer
import time
import json

class Radio(object):
	broadcastAddr ='<broadcast>'

	def __init__ (self, name, port):
		self._connections = {Radio.broadcastAddr : 0}

		self._name = name
		self._port = port
		self._writeCB = None
		self._readCB = None
		self.available = True #if there is something wrong below, we can change this

	def __eq__(self,other):
		if isinstance(other, Radio):
			return self._name == other._name
		elif isinstance(other, str):
			return self._name == other

	def __hash__(self):
		return hash(self._name)

	def getName(self):
		return self._name

	def getPort(self):
		return self._port

	def setReadCB (self, cb):
		self._readCB = cb

	def setWriteCB (self, cb):
		self._writeCB = cb

	def ping(self, connection = broadcastAddr, extra = None):
		data = {'type':'ping'}

		data['addr'] = connection

		if extra is not None:
			data['extra'] = extra

		self.write(data)

	def getConnections (self):
		return self._connections.copy()

	def addConnection(self, connection):
		if connection not in self._connections:
			self._connections[connection] = time.time()
			#self.ping (connection)
			#TODO: add'l to set up connection

	def removeConnection (self, connection):
		del self._connections[connection]
		#TODO: add'l to close connection

	def read(self, data):
		#add/remove fields from data
		self._connections[data['sentby']] = time.time()
		data['radio'] = self._name
		self._readCB(data)

	def _cleanOutoing (self, msg):
		if 'sentby' in msg: #from forwarding
			del msg['sentby']
		if 'radios' in msg:
			del msg['radios'] #for choosing how to send, but don't want to send this

		return msg

	def write(self, data):
		#add/remove fields from data
		data = self._cleanOutoing(data)
		data['radio'] = self._port

		if data['addr'] not in self._connections:
			self.addConnection(data['addr'])

		return self._writeCB(data)

	def connectionThreshold (self, cutoff):
		#delete connections that have been idle longer than cutoff
		toDelete = []
		for key, val in self._connections.iteritems():
			if time.time() - val > cutoff:
				toDelete.append(key)

		for key in toDelete:
			del self._connections[key]


class ConnectionLayer(NetworkLayer):
	"""
	This class is responsible for maintaining connections 
	(and managing the state of the hardware?)

	"""

	def __init__(self, commonData):
		NetworkLayer.__init__(self, 'CL')
		self._commonData = commonData
		self.radios = set()
		self._connectionPolicy = None
		self.checkRadios() #weed out any radios that are not *actually* active
		
		#TODO: decide if I need this
		#self._commonData['activeRadios'] = [radio._name for radio in self.radios] #initialize commonData
	
		if self._commonData['logging']['inUse']:
			self._commonData['logging']['connection'] = {'pings' : 0, 'sent': 0, 'received' : 0}
	#

	def checkRadios(self):
		"""
		Check if radios are properly functioning
		TODO: implement
		"""
		pass
	#

	def setConnectionPolicy(self, func):
		#defined by user. They get the radio list to work with to decide what to do
		self._connectionPolicy = func

	def runConnectionPolicy(self):
		if self._connectionPolicy is not None:
			self._connectionPolicy(self.radios)

	def addRadio(self, name, port):
		newRad = Radio(name, port)
		newRad.setReadCB(self.read)
		newRad.setWriteCB(self.writeCB)
		self.radios.add(newRad)


	def removeRadio(self, name):
		self.radios.remove(name)

	def getRadio(self, name):
		for radio in self.radios:
			if radio.getName() == name:
				return radio

		return None


	def getRadioNames(self):
		return [rad.getName() for rad in self.radios]

	def getRadioPorts(self):
		return [rad.getPort() for rad in self.radios]

	def isRadio (self, port):
		for radio in self.radios:
			if radio._port == port:
				return True

		return False

	def directCommTo(self, message, port):
		for radio in self.radios:
			if radio._port == port:
				radio.read(message)

	def ping(self, extra = None):
		if self._commonData['logging']['inUse']:
			self._commonData['logging']['connection']['pings'] += 1

		if extra is not None:
			extraData.update(extra)

		for radio in self.radios:
			radio.ping(extraData)

	def read(self, msg):
		"""
		Count total messages received and callback

		TODO: exception handling for broken things
		"""
		if self._commonData['logging']['inUse']:
			self._commonData['logging']['connection']['received'] += 1
		
		#

		self.readCB(msg)
	#


	def write(self, msg):
		"""
		Write msg to radios

		return true if successful, false otherwise
		"""
		everythingOkay = None
		try:
			#if we don't recognize a command by the time it gets to the bottom
			#of the stack then we can finally say we don't recognize it
			if 'cmd' in msg:
				msg['result'] = self.failure("unrecognized command %s" % msg['cmd'])
				return msg

			for radio, addr in msg['radios']:
				if radio in self.getRadioNames():
					rad = self.getRadio(radio)
					msg['addr'] = addr
					if self._commonData['logging']['inUse']:
						self._commonData['logging']['connection']['sent'] += 1
					
					ret = rad.write(msg)
					if 'failure' in ret['result']:
						everythingOkay = False
						if 'result' not in msg:
							msg['result'] = self.failure('')

						msg['result'] += rad.getName() + ' '
					else:
						everythingOkay = True

			if everythingOkay is None:
				msg['result'] = self.failure("no radios registered")
		except Exception as e:
			msg['result'] = self.failure(str(e))

		return msg

		








#