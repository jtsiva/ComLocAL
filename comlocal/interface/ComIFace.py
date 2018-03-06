from twisted.spread import pb
from twisted.internet import reactor

from comlocal.core.Com import Com

class ComIFace (object):

	def __init__(self, name, port):
		self.readCB = None
		self._comiface = None
		self.name = name
		self.port = port

	def start(self):
		self._comiface = _ComIFace(self)
		self.tcpPort = reactor.listenTCP(self.port, pb.PBServerFactory(self._comiface), interface='127.0.0.1')
		
		d = self._comiface.unregister()
		d.addCallback(lambda res: self._comiface.register())
		return d

	def stop(self):
		d = self._comiface.unregister()
		port, self.tcpPort = self.tcpPort, None

		d.addCallback(lambda res: port.stopListening())
		return d


	def write(self, msg, dest):
		message = {'msg':msg,'dest':dest}
		return self._comiface.doWrite(message)
		

	def cmd(self, cmd, **kwargs):
		command = {'cmd':cmd}
		for key in kwargs:
			command[key] = kwargs[key]

		return self._comiface.doCmd(command)

class _ComIFace(pb.Root):
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
			#assert 'success' in result['result']
			self.iface.registered = False

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


	def doWrite(self, msg):
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


	def doCmd(self,cmd):
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
