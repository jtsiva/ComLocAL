from twisted.internet import task, reactor
from twisted.spread import pb
from twisted.python import log

from comlocal.radio.RadioManager import RadioManager
from comlocal.util.NetworkLayer import NetworkLayer

class Dummy (pb.Root, NetworkLayer):
	myPort = 10666
	def __init__ (self):
		NetworkLayer.__init__(self, 'Dummy')
		self._localReceivers = set()
		self._registered = False

		self.props = {}
		self._setupProperties()
		
		self.broadcastAddr = '<broadcast>'


		self.tryToRegister = task.LoopingCall (self.sendRegistration)
		self.tryToRegister.start(5.0)

	def remote_cmd(self, cmd):
		#log.msg('received command: %s' % cmd)
		try:
			if 'reg_local' == cmd['cmd']:
				port = cmd['port']
				self._localReceivers.add(port)
				cmd['result'] = self.success('')
			elif 'unreg_local' == cmd['cmd']:
				port = cmd['port']
				self._localReceivers.remove(port)
				cmd['result'] = self.success('')
			elif 'get_local' == cmd['cmd']:
				cmd['result'] = self._localReceivers
			elif 'check_radio_reg' == cmd['cmd']:
				cmd['result'] = str(self._registered)
			elif 'get_props' == cmd['cmd']:
				cmd['result'] = self.props
			else:
				cmd['result'] = self.failure("no command %s" % (cmd['cmd']))

		except KeyError:
			cmd['result'] = self.failure('poorly formatted command (missing a field?)')
		except Exception as e:
			raise pb.Error (e) 

		return cmd

	def remote_write(self, message):
		try:
			message['sentby'] = self.props['addr']
			addr = message.pop('addr')
			message['result'] = self.success('')
		except KeyError:
			message['result'] = self.failure('missing "addr" field')
		except Exception as e:
			raise pb.Error(e)
		return message

	def remote_read(self, message):
		log.msg('received' + str(message))
		message['sentby'] = 'unknown'
		return self.sendToLocalReceivers(message)

	def sendToLocalReceivers(self, message):
		if 'sentby' in message and 'msg' in message and 'dest' in message:
			message['radio'] = self.name

			def readAck(result):
				return result #hooray?

			def readNack(reason):
				log.msg(reason) #not hooray

			def connected(obj):
				d = obj.callRemote('read', message)
				d.addCallbacks(readAck,readNack)
				d.addCallback(lambda result: obj.broker.transport.loseConnection())
				return d

			d = None
			log.msg(self._localReceivers)
			for port in self._localReceivers:
				factory = pb.PBClientFactory()
				connect = reactor.connectTCP("127.0.0.1", port, factory)
				d = factory.getRootObject()
				d.addCallback(connected)
		else:
			return None
			#drop poorly formed packets

		return d

	def _getLocalReceivers(self):
		return self._localReceivers

	def sendRegistration (self):

		def regAck(result):
			self._registered = True
			self.tryToRegister.stop()

		def regNack(reason):
			log.msg(reason)

		def connected(obj):
			regPacket = {'cmd':'reg_radio','name':self.name,'props':self.props}
			d = obj.callRemote('cmd', regPacket)
			d.addCallbacks(regAck,regNack)
			d.addCallback(lambda result: obj.broker.transport.loseConnection())
			return d

		def failed(reason):
			log.msg(reason)

		factory = pb.PBClientFactory()
		self.radMgrConnect = reactor.connectTCP("127.0.0.1", RadioManager.myPort, factory)
		d = factory.getRootObject()
		d.addCallbacks(connected, failed)

		log.msg('registering with RadioManager')

		return d

	def _setupProperties(self):
		"""
		Set up the radio properties we might need
		"""
		self.props['addr'] = '127.0.0.1'
		self.props['maxPacketLength'] = 15000
		self.props['costPerByte'] = .5
		self.props['port'] = Dummy.myPort