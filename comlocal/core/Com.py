from twisted.internet import reactor, defer
from twisted.spread import pb
from twisted.internet.defer import maybeDeferred

from twisted.python import log

from comlocal.radio.RadioManager import RadioManager
from comlocal.util.NetworkLayer import NetworkLayer
from comlocal.connection import ConnectionLayer
from comlocal.routing import RoutingLayer
from comlocal.message import MessageLayer
import random

class Com(pb.Root, NetworkLayer):
	broadcastSinkID = -1
	myPort = 10257

	def __init__(self, log = False, configFile = None, authFile = None):
		NetworkLayer.__init__(self, 'Com')
		self._authFile = authFile
		self._registeredApplications = {}

		self._commonData = {}
		self._initCommonData(log, configFile)

		self._CL = ConnectionLayer.ConnectionLayer(self._commonData)
		self._RL = RoutingLayer.RoutingLayer(self._commonData)
		self._RL.addNode(Com.broadcastSinkID)

		self._ML = MessageLayer.MessageLayer(self._commonData)

		#add radios (will also track ports)

		#set up connections between layers
		self._CL.setReadCB(self._RL.read)
		self._CL.setWriteCB(self._write)

		self._RL.setReadCB(self._ML.read)
		self._RL.setWriteCB(self._CL.write)

		self._ML.setReadCB(self._read)
		self._ML.setWriteCB(self._RL.write)


		self._radiosPending = {}
		self._checkForRadios()
	
	#

	def remote_cmd(self, cmd):
		try:
			if 'reg_app' == cmd['cmd']:
				#only use 4 char for name (just in case they sent more)
				self._registeredApplications[cmd['name'][:4]] = cmd['port']
				cmd['result'] = self.success('')
			elif 'check_for_radios' == cmd['cmd']:
				d = self._checkForRadios()
				return d
			else:
				cmd = self._directCommToStack(cmd)

		except KeyError:
			cmd['result'] = self.failure("poorly formed message")
		except Exception as e:
			raise pb.Error(e)

		log.msg(cmd)

		return cmd

	def remote_read(self, msg):
		return self._directCommToRadio(msg, msg['radio'])

	def remote_write(self, msg):
		ret = self._directCommToStack(msg)
	
		def printIt(res):
			print res
			return res

		if isinstance(ret, list):
			for thing in ret:
				thing.addCallback(printIt)
				
			d = defer.DeferredList(ret)
			return d
		else:
			return ret

	def _isRadio(self, port):
		return self._CL.isRadio(port)

	def _directCommToRadio(self, message, name):
		#log.msg('from radio ')
		self._CL.directCommTo(message, name)

	def _directCommToStack (self, message):
		if 'msg' in message:
			message['radios'] = self._chooseRadios()
			#log.msg(message['radios'])
		return self._ML.write(message)

	def _chooseRadios(self):
		"""
		TODO: radio selection scheme. Make more intelligent

		Maybe RL can override decision?
		"""
		return self._CL.getRadioNames()


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

	def _read(self, msg):
		def readAck(result):
			return result

		def readNack(reason):
			log.msg(reason)

		def connected(obj):
			d = obj.callRemote('read', msg)
			d.addCallbacks(readAck, readNack)
			d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), readNack)

			return d


		if 'app' in msg:
			factory = pb.PBClientFactory()
			reactor.connectTCP("127.0.0.1", self._registeredApplications[msg['app']], factory)
			d = factory.getRootObject()
			d.addCallback(connected)
		else:
			for key, val in self._registeredApplications.iteritems():
				factory = pb.PBClientFactory()
				reactor.connectTCP("127.0.0.1", val, factory)
				d = factory.getRootObject()
				d.addCallback(connected)

		#return d

	def _write(self, msg):
		#print msg
		port = msg.pop('radio')

		def writeAck(result):
			print self.success(str(result))
			return result

		def failed(reason):
			log.msg(self.failure (str(reason)))

		def connected(obj):
			d = obj.callRemote('write', msg)
			d.addCallbacks(writeAck, failed)
			d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), failed)

			return d

		factory = pb.PBClientFactory()
		reactor.connectTCP("127.0.0.1", port, factory)
		d = factory.getRootObject()
		d.addCallbacks(connected, failed)

		return d

	def _setupRadio (self, radio, props):
		if not self._CL.isRadio(props['port']):
			self._CL.addRadio(radio,props['port'])
			self._RL.addNode(Com.broadcastSinkID)
			self._RL.addLink(self._commonData['id'], Com.broadcastSinkID, 
								radio, ConnectionLayer.Radio.broadcastAddr)

	def _checkForRadios (self):
		def regAck(result):
			if 'success' in result['result']:
				name = result['result'].split()[0] #name is in first part
				props = self._radiosPending.pop(name)
				self._setupRadio(name, props)

		def regNack(reason):
			log.msg(reason)

		def connectedToRadio(obj):
			regPacket = {'cmd':'reg_local','port':Com.myPort}
			d = obj.callRemote('cmd', regPacket)
			d.addCallbacks(regAck, regNack)
			d.addCallback(lambda result: obj.broker.transport.loseConnection())

		def failedToConnectToRadio(reason):
			log.msg(self.failure(str(reason)))

		def checkAck(result):
			try:
				log.msg(result)
				for radio, props in result['result'].iteritems():
					if radio not in self._CL.getRadioNames():
						self._radiosPending[radio] = props
						factory = pb.PBClientFactory()
						reactor.connectTCP("127.0.0.1", props['port'], factory)
						d = factory.getRootObject()
						d.addCallbacks(connectedToRadio, failedToConnectToRadio)

			except KeyError:
				raise pb.Error

		def checkNack(reason):
			log.msg(reason)

		def connected(obj):
			regPacket = {'cmd': 'get_radios'}
			d = obj.callRemote('cmd', regPacket)
			d.addCallbacks(checkAck,checkNack)
			d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), checkNack)
			return d

		def failed(reason):
			print self.failure(str(reason))

		factory = pb.PBClientFactory()
		reactor.connectTCP("127.0.0.1", RadioManager.myPort, factory)
		d = factory.getRootObject()
		d.addCallbacks(connected, failed)

		log.msg('checking radio manager for radios')

		return d