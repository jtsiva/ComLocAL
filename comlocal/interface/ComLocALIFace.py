from twisted.application import internet, service
from twisted.internet.protocol import ServerFactory, DatagramProtocol
from threading import Thread

from comlocal.radio.RadioManager import RadioManager

#Twisted and threading
#https://stackoverflow.com/questions/2243266/threads-in-twisted-how-to-use-them-properly
#http://twistedmatrix.com/documents/13.0.0/core/howto/threading.html


class ComLocAL(object):
	def __init__(self):
		self.comlocalProto = None
		self.readCB = None # called when data arrives
		self.resultCB = None # called when write completes (includes commands)
		self.locationCB = None # called if periodic location updates are desired
		self.period = 1.0 #used for periodic location updates

	def start(self, name):
		from twisted.internet import reactor
		self.comlocalProto = ComLocALProtocol(self, name)
		reactor.listenUDP(10267, self.comlocalProto)
		#reactor.addSystemEventTrigger('during','shutdown', self.stop)
		Thread(target=reactor.run, args=(False,)).start()

	def stop(self):
		from twisted.internet import reactor
		reactor.stop()

	def setReadCB (self, cb):
		self.readCB = cb

	def setResultCB (self, cb):
		self.resultCB = cb

	def setLocationCB (self, cb, period):
		self.locationCB = cb
		self.period = period

	def comWrite(self, msg):
		"""
		expect msg to be json object (a dict)
		with the following fields:

			{
				"type" : <"msg" | "cmd">,
				<"msg" | "cmd"> : <stuff>,
				("dest" : <id>)            <-
			}                               |
			                                |
			                                - only necessary when type == msg

			    ("app" : <4-char-app-code>) <- don't really need because started with name

		The currently available commands are:
			get_neighbors - returns a list of ids of nodes within 1 hop
		"""
		from twisted.internet import reactor
		reactor.callFromThread(self.comlocalProto.comWrite, msg)

	def locWrite(self, cmd):
		"""
		always a command -- format TBD
		"""
		pass

#These classes should not be used directly. The above interface will remain the same

# class ComLocALService(service.Service)
# 	def __init__(self):
# 		pass

# 	def startService (self):
# 		service.Service.startService(self)

class ComLocALProtocol(DatagramProtocol)
	def __init__(self, obj, name):
		self._obj = obj
		self._name = name
		self._registered = False

	def sendRegistration (self):
		regPacket = {}
		regPacket['type'] = 'cmd'
		regPacket['cmd'] = 'reg_app'
		regPacket['name'] = self._name
		self.transport.write(json.dumps(regPacket), ('127.0.0.1', RadioManager.myPort))
		#og.msg('registering with Com')	

	def checkRegistration (self):
		#if the Com stack responded then we don't need to keep
		#checking
		if self._registered:
			self._later.stop()
		else:
			self.sendRegistration()

	def startProtocol (self):

		#give the other service three seconds to start up
		from twisted.internet import reactor
		self._later = task.LoopingCall (self.checkRegistration)
		task.deferLater(reactor, 3.0, self.sendRegistration)
		task.deferLater(reactor, 5.0, self._later.start, 5.0)

	def comWrite(self, msg):
		if self._registered:
			msg['app'] = self._name
			data = json.dumps(msg, separators=(',', ':'))
			self.transport.write(data, ('127.0.0.1', 10257))

	def datagramReceived(self, data, (host, port)):
		message = json.loads(data)
		if 'cmd' == message['type'] and 'reg_app' == message['cmd']:
			if 'success' == message['result']:
				self._registered = True
			else:
				#problem
				pass

			return

		from twisted.internet import reactor
		if self._registered:
			if 'result' in message:
				reactor.callInThread(self._obj.resultCB, message)
			else:
				reactor.callInThread(self._obj.readCB, message)
