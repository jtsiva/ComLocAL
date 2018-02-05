from twisted.application import internet, service
from twisted.internet import task
from twisted.internet.protocol import ServerFactory, DatagramProtocol
from twisted.internet.defer import Deferred
from twisted.internet import reactor
from twisted.python import log

from comlocal.core.Com import ComProtocol
import pdb
import sys
import json

from crochet import wait_for, run_in_reactor, setup
setup()

#Twisted and threading
#https://stackoverflow.com/questions/2243266/threads-in-twisted-how-to-use-them-properly
#http://twistedmatrix.com/documents/13.0.0/core/howto/threading.html


class ComLocAL(object):
	def __init__(self, name):
		self.name = name
		self.comlocalProto = None
		self.readCB = None # called when data arrives
		self.resultCB = None # called when write completes (includes commands)
		self.locationCB = None # called if periodic location updates are desired
		self.period = 1.0 #used for periodic location updates
		# self.writeDeferred = Deferred()
		# self.stopDeferred = Deferred()
		#log.startLogging(open('local.log', 'w'))

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
		
		#pdb.set_trace()
		self.comlocalProto.comWrite(msg)
	
	#def stop(self):
		
		
	# def getWriteAndStopFuncs(self):
	# 	writeDeferred = Deferred()
	# 	stopDeferred = Deferred()

	# 	writeDeferred.addCallback(self.comWrite) #need to wrap in callFromThread?

	# 	stopDeferred.addCallback(self.stop) #need to wrap in callFromThread?

	# 	return writeDeferred, stopDeferred

	@wait_for(timeout=3)
	def start(self):
		self.comlocalProto = ComLocALProtocol(self, self.name)
		reactor.listenUDP(10267, self.comlocalProto, interface='127.0.0.1')
		#reactor.addSystemEventTrigger('during','shutdown', self.stop)
		
		

		

	def setReadCB (self, cb):
		self.readCB = cb

	def setResultCB (self, cb):
		self.resultCB = cb

	def setLocationCB (self, cb, period):
		self.locationCB = cb
		self.period = period

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

class ComLocALProtocol(DatagramProtocol):
	def __init__(self, obj, name):
		self._obj = obj
		self._name = name
		self._registered = False

	@run_in_reactor
	def sendRegistration (self):
		regPacket = {}
		regPacket['type'] = 'cmd'
		regPacket['cmd'] = 'reg_app'
		regPacket['name'] = self._name
		self.transport.write(json.dumps(regPacket), ('127.0.0.1', ComProtocol.myPort))
		log.msg('registering with Com')	

	@run_in_reactor
	def checkRegistration (self):
		#if the Com stack responded then we don't need to keep
		#checking
		if self._registered:
			self._later.stop()
		else:
			self.sendRegistration()

	@run_in_reactor
	def startProtocol (self):
		#give the other service three seconds to start up
		#from twisted.internet import reactor
		self._later = task.LoopingCall (self.checkRegistration)
		self.sendRegistration()
		task.deferLater(reactor, 5.0, self._later.start, 5.0)

	@run_in_reactor
	def comWrite(self, msg):
		if self._registered:
			msg['app'] = self._name
			data = json.dumps(msg, separators=(',', ':'))
			self.transport.write(data, ('127.0.0.1', ComProtocol.myPort))

	def datagramReceived(self, data, (host, port)):
		message = json.loads(data)
		log.msg(message)
		if 'cmd' == message['type'] and 'reg_app' == message['cmd']:
			if 'success' in message['result']:
				self._registered = True
			else:
				#problem
				pass

			return

		if self._registered:
			if 'result' in message:
				if self._obj.resultCB is not None:
					reactor.callInThread(self._obj.resultCB, message)
				#self._obj.resultCB(message)
			else:
				if self._obj.readCB is not None:
					reactor.callInThread(self._obj.readCB, message)
				#self._obj.readCB(message)
