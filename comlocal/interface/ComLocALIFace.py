from twisted.application import internet, service
from twisted.internet import task

from twisted.internet.defer import Deferred
from twisted.internet import reactor
from twisted.python import log
from twisted.spread import pb

from comlocal.core.Com import Com
import pdb
import sys
import json

from crochet import wait_for, run_in_reactor, setup
setup()



class ComLocAL(object):
	timeout = 1.0
	def __init__(self, name, port):
		self.name = name
		self.port = port
		self.readCB = None # called when data arrives
		self.locationCB = None # called if periodic location updates are desired
		self.period = 1.0 #used for periodic location updates
		self.registered = False

		self.tcpPort = None
		self._comlocal = None

	@wait_for(timeout=timeout)
	def start(self):
		self._comlocal = _ComLocAL(self)
		self.tcpPort = reactor.listenTCP(self.port, pb.PBServerFactory(self._comlocal), interface='127.0.0.1')
		return self._comlocal.register()

	@wait_for(timeout=timeout)
	def stop(self):
		if self.tcpPort is not None:
			port, self.tcpPort = self.tcpPort, None
			port.stopListening()
		if self.registered:
			return self._comlocal.unregister()




	def setTimeout(self, timeout):
		ComLocAL.timeout = timeout
	
	@wait_for(timeout=timeout)
	def comWrite(self, msg, dest):
		"""
		msg - string, base64 binary, whatever--> json field
		dest - int

		raises crochet.TimeoutError
		"""
		message = {'msg':msg,'dest':dest}
		
		return self._comlocal.doComWrite(message)
		
	@wait_for(timeout=timeout)
	def comCmd(self, cmd, **kwargs):
		"""
		cmd - string for the command
		kwargs - parameters for cmd (could be none)

		raises crochet.TimeoutError
		"""

		command = {'cmd':cmd}
		for key in kwargs:
			command[key] = kwargs[key]

		return self._comlocal.doComCmd(command)


	def setReadCB (self, cb):
		self.readCB = cb

	def setLocationCB (self, cb, period):
		self.locationCB = cb
		self.period = period

	def locCmd(self, cmd):
		"""
		always a command -- format TBD
		"""
		pass


class _ComLocAL(pb.Root):
	def __init__(self, iface):
		self.iface = iface
		self.port = self.iface.port

	def register(self):
		def regAck(result):
			assert 'success' in result['result']
			self.iface.registered = True

		def failed(reason):
			print reason

		def connected(obj):
			regPacket = {'cmd': 'reg_app', 'name':self.iface.name,'port':self.port}
			d = obj.callRemote('cmd', regPacket)
			d.addCallbacks(regAck,failed)
			d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), failed)
			return d

		factory = pb.PBClientFactory()
		reactor.connectTCP("127.0.0.1", Com.myPort, factory)
		d = factory.getRootObject()
		d.addCallbacks(connected, failed)

		return d

	def unregister(self):
		def regAck(result):
			assert 'success' in result['result']
			self.iface.registered = True

		def failed(reason):
			print reason

		def connected(obj):
			regPacket = {'cmd': 'unreg_app', 'name':self.iface.name,'port':self.iface.port}
			d = obj.callRemote('cmd', regPacket)
			d.addCallbacks(regAck,failed)
			d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), failed)
			return d

		factory = pb.PBClientFactory()
		reactor.connectTCP("127.0.0.1", Com.myPort, factory)
		d = factory.getRootObject()
		d.addCallbacks(connected, failed)

		return d


	def doComWrite(self, msg):
		def writeAck(result):
			return result

		def failed(reason):
			print reason
			reason.printTraceback()

		def connected(obj):
			# def closeAndReturn (result):
			# 	obj.broker.transport.loseConnection()
			# 	return result

			d = obj.callRemote('write', msg)
			d.addCallbacks(writeAck, failed)
			#d.addCallbacks(closeAndReturn, failed)

			return d

		factory = pb.PBClientFactory()
		reactor.connectTCP("127.0.0.1", Com.myPort, factory)
		d = factory.getRootObject()
		d.addCallbacks(connected, failed)

		return d


	def doComCmd(self,cmd):
		def writeAck(result):
			#print self.success(str(result))
			return result

		def failed(reason):
			log.msg(self.failure (str(reason)))
			reason.printTraceback()

		def connected(obj):
			def closeAndReturn (result):
				obj.broker.transport.loseConnection()
				return result

			d = obj.callRemote('cmd', cmd)
			d.addCallbacks(writeAck, failed)
			d.addCallbacks(closeAndReturn, failed)

			return d

		factory = pb.PBClientFactory()
		reactor.connectTCP("127.0.0.1", Com.myPort, factory)
		d = factory.getRootObject()
		d.addCallbacks(connected, failed)

		return d

	def remote_read(self, message):
		self.iface.readCB(message)

