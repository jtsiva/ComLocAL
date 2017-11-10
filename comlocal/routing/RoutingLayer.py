

class Stats(object):
	def __init__(self):
		self.packetsDropped = 0 #poorly formed packets

class RoutingLayer(object):
	def __init__(self, commonData):
		self._commonData = commonData
		self._routingTable = {}
		self._stats = Stats()

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
		messages = self.readCB()

		#TODO: filter out poorly formed messages
		#TODO: update routing table


		#get messages that need to be forwarded and forward
		r = map(lambda x: self._handleFoward(x), filter(lambda x: self._needsFoward(x), messages))
		try:
			#get messages that need to handled by command handler and handle
			r += map(lambda x: self._handleCmd(x), filter(lambda x: (not self._needsFoward(x)) and _isCommand(x), messages))
		except Exception as e:
			print 'Command handler not set?'
			raise e

		#return the rest of the messages because these are local
		return filter(lambda x: x not in r, messages)

	def _updateRoutingTable(self, msg):
		"""
		Update the routing table based on information from
		the message. ASSUMES that msg has already been checked
		for validity
		"""
		self._routingTable[msg['dest']][msg['radio']] = msg['from']


	def _needsForward(self, msg):
		"""
		Check if the message is intended for this node or not
		"""
		try:
			return msg['dest'] != self._commonData.id
		except KeyError:
			return False

	def _handleForward(self, msg):
		self.write(msg)
		return msg

	def setWrite(self, cb):
		self._writeCB = cb

	def write(self, msg):
		self._writeCB(msg)


# NOT SURE IF I WANT TO HANDLE THIS HERE OR THE MESSAGE LAYER
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def setCmdHandler(self, cb):
		"""
		Need to set a callback that will handle a message
		that is a command
		"""
		self._cmdHandler = cb

	def _isCommand(msg):
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