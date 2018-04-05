from twisted.spread import pb
from twisted.internet import reactor
from twisted.internet import error
from twisted.internet.defer import Deferred

from comlocal.core.Com import Com

from socket import error as socket_error


class ComIFace (object):

	def __init__(self, name):
		self.readCB = None
		self._comiface = None
		self.name = name
		self.tcpPort = None
		self.registered = False

	def start(self):
		print 'starting'
		self._comiface = _ComIFace(self)

		#http://twistedmatrix.com/pipermail/twisted-python/2008-February/016886.html
		self.tcpPort = reactor.listenTCP(0, pb.PBServerFactory(self._comiface), interface='127.0.0.1')
		print self.tcpPort.getHost().port
		d = self._comiface.unregister()
		d.addCallback(lambda res: self._comiface.register())
		return d

	def stop(self):
		d = self._comiface.unregister()
		port, self.tcpPort = self.tcpPort, None

		if port is not None:
			d.addCallback(lambda res: port.stopListening())
		return d

	def write(self, msg, dest):
		message = {'msg':msg,'dest':dest,'app':self.name}
		return self._comiface.doWrite(message)
		

	def cmd(self, cmd, **kwargs):
		command = {'cmd':cmd}
		for key in kwargs:
			command[key] = kwargs[key]

		return self._comiface.doCmd(command)

class _ComIFace(pb.Root):
	def __init__(self, iface):
		self.iface = iface
		self.obj = None

	def register(self):
		def regAck(result):
			print result
			assert 'success' in result['result']
			self.iface.registered = True

		def failed(reason):
			r = reason.trap(error.ConnectionRefusedError)
			print "Can't connect to Com. Have you started it?"


		def connected(obj):
			self.obj = obj
			regPacket = {'cmd': 'reg_app', 'name':self.iface.name,'port':self.iface.tcpPort.getHost().port}
			d = obj.callRemote('cmd', regPacket)
			d.addCallbacks(regAck,failed)
			#d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), failed)
			return d

		if self.obj is None:
			factory = pb.PBClientFactory()
			reactor.connectTCP("127.0.0.1", Com.myPort, factory)
			d = factory.getRootObject()
			d.addCallbacks(connected, failed)
		else:
			d = connected(self.obj)

		return d

	def unregister(self):
		def regAck(result):
			print result
			#assert 'success' in result['result']
			self.iface.registered = False

		def failed(reason):
			print 'unreg'
			print reason
			r = reason.trap(error.ConnectionRefusedError)
			print r
			if r == error.ConnectionRefusedError:
				print "Can't connect to Com. Have you started it?"
			#ignoring connection lost because I don't see at the moment why it matters
			print 'hit here'

		def connected(obj):
			print 'connected'
			self.obj = obj
			regPacket = {'cmd': 'unreg_app', 'name':self.iface.name,'port':self.iface.tcpPort.getHost().port}
			
			print regPacket
			print self.iface.name[:4]
			print obj
			d = obj.callRemote('cmd', regPacket)
			d.addCallbacks(regAck,failed)
			#d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), failed)
			return d

		if self.obj is None:
			factory = pb.PBClientFactory()
			reactor.connectTCP("127.0.0.1", Com.myPort, factory)
			d = factory.getRootObject()
			d.addCallbacks(connected, failed)
		else:
			d = connected(self.obj)

		return d


	def doWrite(self, msg):
		def writeAck(result):
			return result

		def failed(reason):
			print 'write'
			print reason

		def connected(obj):
			self.obj = obj
			# def closeAndReturn (result):
			# 	obj.broker.transport.loseConnection()
			# 	return result

			d = obj.callRemote('write', msg)
			d.addCallbacks(writeAck, failed)
			#d.addCallbacks(closeAndReturn, failed)

			return d

		d = Deferred()
		if self.iface.registered:
			if self.obj is None:
				factory = pb.PBClientFactory()
				reactor.connectTCP("127.0.0.1", Com.myPort, factory)
				d = factory.getRootObject()
				d.addCallbacks(connected, failed)
			else:
				d = connected(self.obj)

		return d


	def doCmd(self,cmd):
		def writeAck(result):
			#print self.success(str(result))
			return result

		def failed(reason):
			log.msg(self.failure (str(reason)))
			reason.printTraceback()

		def connected(obj):
			self.obj = obj
			def closeAndReturn (result):
				#obj.broker.transport.loseConnection()
				return result

			d = obj.callRemote('cmd', cmd)
			d.addCallbacks(writeAck, failed)
			d.addCallbacks(closeAndReturn, failed)

			return d

		d = Deferred()
		if self.iface.registered:
			if self.obj is None:
				factory = pb.PBClientFactory()
				reactor.connectTCP("127.0.0.1", Com.myPort, factory)
				d = factory.getRootObject()
				d.addCallbacks(connected, failed)
			else:
				d = connected(self.obj)

		return d

	def remote_read(self, message):
		self.iface.readCB(message)
