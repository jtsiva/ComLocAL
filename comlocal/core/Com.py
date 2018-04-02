from twisted.internet import reactor, defer
from twisted.spread import pb
from twisted.internet.defer import maybeDeferred, gatherResults

from twisted.python import log

from comlocal.util.NetworkLayer import NetworkLayer
from comlocal.connection import ConnectionLayer
from comlocal.routing import RoutingLayer
from comlocal.message import MessageLayer
import json
import random
import importlib


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

		for radioName in self._commonData['startRadios']:
			self._setupRadio(radioName)

		self._ML = MessageLayer.MessageLayer(self._commonData)

		#set up connections between layers
		self._CL.setReadCB(self._RL.read)
		#self._CL.setWriteCB(self._write)

		self._RL.setReadCB(self._ML.read)
		self._RL.setWriteCB(self._CL.write)

		self._ML.setReadCB(self._read)
		self._ML.setWriteCB(self._RL.write)
	
	#

	def stop(self):
		self._CL.cleanupRadios()
		for key, val in self._registeredApplications.iteritems():
			if val['obj'] is not None:
				self._registeredApplications[key]['obj'].broker.transport.loseConnection()
				self._registeredApplications[key]['obj'] = None

	def remote_cmd(self, cmd):
		try:
			if 'reg_app' == cmd['cmd']:
				#only use 4 char for name (just in case they sent more)
				if cmd['name'][:4] in self._registeredApplications:
					cmd['result'] = self.failure('app already registered with that name')
				elif not isinstance(cmd['port'], int):
					cmd['result'] = self.failure('port needs to be a number')
				else:
					self._registeredApplications[cmd['name'][:4]] = {'port': cmd['port'], 'obj':None}
					cmd['result'] = self.success('')
			elif 'unreg_app' == cmd['cmd']:
				if cmd['name'] not in self._registeredApplications:
					cmd['result'] = self.failure('no app with that name registered')
				else:
					stuff = self._registeredApplications.pop(cmd['name'])
					cmd['result'] = self.success ('unregistered %s at %d' % (cmd['name'], stuff['port']))
			else:
				cmd = self._directCommToStack(cmd)

		except KeyError:
			cmd['result'] = self.failure("poorly formed message")
		except Exception as e:
			raise pb.Error(e)

		log.msg(cmd)

		return cmd


	def remote_write(self, msg):
		ret = self._directCommToStack(msg)
		log.msg(ret)

		return ret

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
			self._commonData['startRadios'] = ['WiFi', 'Loopback']
			self._commonData['activeRadios'] = []
			self._commonData['blacklist'] = []

		self._commonData['logging'] = {'inUse': False} if not log else {'inUse': True}
	#

	def _read(self, msg):
		def readAck(result):
			return result

		def readNack(reason):
			log.msg(reason)

		
		if 'app' in msg and msg['app'] in self._registeredApplications:

			def connected(obj):
				self._registeredApplications[msg['app']]['obj'] = obj
				d = obj.callRemote('read', msg)
				d.addCallbacks(readAck, readNack)
				#d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), readNack)

				return d

			if self._registeredApplications[msg['app']]['obj'] is None:
				factory = pb.PBClientFactory()
				reactor.connectTCP("127.0.0.1", self._registeredApplications[msg['app']]['port'], factory)
				d = factory.getRootObject()
				d.addCallback(connected)
			else:
				connected(self._registeredApplications[msg['app']]['obj'])
		else:
			for key, val in self._registeredApplications.iteritems():
				def connected(obj):
					self._registeredApplications[key]['obj'] = obj
					d = obj.callRemote('read', msg)
					d.addCallbacks(readAck, readNack)
					#d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), readNack)

					return d


				if val['obj'] is None:
					factory = pb.PBClientFactory()
					reactor.connectTCP("127.0.0.1", val['port'], factory)
					d = factory.getRootObject()
					d.addCallback(connected)
				else:
					connected(val['obj'])

		#return d


	def _setupRadio (self, radioName):
		self._CL.addRadio(radioName)
		bcastAddr = self._CL.write({'cmd':'get_radio_props', 'name':radioName})['result']['bcastAddr']
		self._RL.addNode(Com.broadcastSinkID)
		self._RL.addLink(self._commonData['id'], Com.broadcastSinkID, 
							radioName, bcastAddr)
