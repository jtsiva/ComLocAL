from twisted.python import log
from twisted.internet.task import LoopingCall

from comlocal.util.NetworkLayer import NetworkLayer
import Queue
import time


class RadioManager (NetworkLayer):
	
	def __init__ (self, name):
		NetworkLayer.__init__(self, name)

		self.props = self._setupProperties()

		self.readCB = None
		self.transport = None
		self.connections = {}
		self.sendQ = Queue.PriorityQueue()
		self.writeTask = LoopingCall(self._dequeueAndSend)
		self.running = False
		

	def _setupProperties(self):
		"""
		Set up the radio properties we might need

		MUST IMPLEMENT!

		Return a dictionary with:
		{
			'addr' : <the address of the radio>,
			'bcastAddr' : <the broadcast address used by this radio if any>,
			'costPerByte' : <cost to send 1 byte on this radio>
		}

		"""
		return {}

	def setTransport(self, transport):
		self.transport = transport

	def _getStatus(self):
		return {'running':True}

	def cmd(self, cmd):
		#log.msg('received command: %s' % cmd)
		try:
			if 'get_props' == cmd['cmd']:
				cmd['result'] = self.props
			elif 'get_status' == cmd['cmd']:
				cmd['result'] = self._getStatus()
			else:
				cmd['result'] = self.failure("no command %s" % (cmd['cmd']))

		except KeyError:
			cmd['result'] = self.failure('poorly formatted command (missing a field?)')

		return cmd

	def _dequeueAndSend(self):
		try:
			priority, message = self.sendQ.get()

			addr = message.pop('addr')
			self.transport.write(message, addr)

		except Queue.Empty:
			pass #don't care
		except Exception as e:
			if 'Errno 11' in str(e):
				message['addr'] = addr
				self.sendQ.put((priority - 1, message))
			else:
				log.msg("WTF?")

	def write(self, message):

		if 'addr' in message:
			self.sendQ.put((10,message))
			message['result'] = self.success('')
		else:
			message['result'] = self.failure('missing "addr" field')

		if not self.running:
			self.running = True
			self.writeTask.start(1, now=True) #flow control!
	
		return message

	def read (self, message):
		
		#update things about connections from Transport class
		if message['sentby'] not in self.connections:
			self.connections[message['sentby']] = {}

		self.connections[message['sentby']]['time'] = time.time()

		if self.readCB is not None:
			self.readCB(message)

	def setReadCB (self, cb):
		#use this callback in transport implemented for the radio
		self.readCB = cb

class RadioTransport(object):
	def __init__(self):
		self.manager = None

	def setManager (self, manager):
		self.manager = manager

	def write(self, message, addr):
		pass

	def read(self, message):
		pass

