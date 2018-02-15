#!/usr/bin/python

from twisted.spread import pb
from twisted.internet import reactor
from twisted.trial.unittest import TestCase
from twisted.internet.task import deferLater

from comlocal.radio.RadioManager import RadioManager
from comlocal.radio.WiFiManager import WiFiManager, WiFiTransport
from comlocal.radio.Dummy import Dummy
from comlocal.core.Com import Com



class Client (object):
	
	def connect(self, port):
		factory = pb.PBClientFactory()
		self.connection = reactor.connectTCP("127.0.0.1", port, factory)
		self.d = factory.getRootObject()

	
	def end(self):
		self.connection.disconnect()
		#reactor.stop()

class app(pb.Root):
	def __init__(self):
		self.received = None
	def remote_read(self, message):
		self.received = message

class App(object):
	def __init__(self):
		self.app = None
	def start(self):
		self.app = app()
		self.port = reactor.listenTCP(6666, pb.PBServerFactory(self.app), interface='127.0.0.1')
		self.portnum = self.port.getHost().port

	def stop(self):
		port, self.port = self.port, None
		return port.stopListening()



class DummyRad(object):
	def __init__(self):
		self.done = None
	def start(self):
		self.port = reactor.listenTCP(Dummy.myPort, pb.PBServerFactory(Dummy()), interface='127.0.0.1')
		self.portnum = self.port.getHost().port
		self.done = False

	def stop(self):
		if self.done == False:
			self.done = True
			port, self.port = self.port, None
			return port.stopListening()
	

class RadMgr(object):
	def start(self):
		self.port = reactor.listenTCP(RadioManager.myPort, pb.PBServerFactory(RadioManager()), interface='127.0.0.1')
		self.portnum = self.port.getHost().port

	def stop(self):
		port, self.port = self.port, None
		return port.stopListening()

class WiFiMgr(object):
	def __init__(self):
		self.done = None
		self.mgr = WiFiManager()
		self.transport = WiFiTransport()

		self.mgr.setTransport(self.transport)
		self.transport.setManager(self.mgr)

	def start(self):
		self.mgrPort = reactor.listenTCP(WiFiManager.myPort, pb.PBServerFactory(self.mgr), interface='127.0.0.1')
		self.transPort = reactor.listenUDP(WiFiTransport.myPort, self.transport)
		self.done = False

	def stop(self):
		if self.done == False:
			self.done = True
			port, self.transPort = self.transPort, None
			port.stopListening()
			port, self.mgrPort = self.mgrPort, None
			return port.stopListening()

class ComTestCase(TestCase):
	def setUp(self):
		self.radmgr = RadMgr()
		self.radmgr.start()
		self.wifiMgr = WiFiMgr()
		self.wifiMgr.start()
		self.dummy = DummyRad()
		self.dummy.start()
		self.app = App()
		self.app.start()

		self.port = reactor.listenTCP(Com.myPort, pb.PBServerFactory(Com()), interface='127.0.0.1')
		self.portnum = self.port.getHost().port
		self.client = Client()


	def tearDown(self):
		port, self.port = self.port, None
		self.radmgr.stop()
		self.wifiMgr.stop()
		self.dummy.stop()
		self.app.stop()
		return port.stopListening()

	def test_radioSet(self):

		self.client.connect(WiFiManager.myPort)

		def res(result):
			self.assertTrue(Com.myPort in result['result'])
			self.client.end()

		def connected(obj):
			d = deferLater(reactor, 2.0, obj.callRemote, 'cmd', {'cmd': 'get_local'})
			d.addCallback(res)
			return d

		self.client.d.addCallback(connected)

		return self.client.d

	def test_regApp(self):
		self.client.connect(Com.myPort)

		def res(result):
			self.assertTrue('success' in result['result'])
			d = deferLater(reactor, .5, self.client.end) #delay ending because Com might still be working
			return d

		def nack(reason):
			print reason
			self.client.end()

		def connected(obj):
			d = obj.callRemote('cmd', {'cmd': 'reg_app', 'name':'hola','port':10666})
			d.addCallbacks(res, nack)
			#d.addCallback(lambda result: obj.broker.transport.loseConnection())

			return d

		self.client.d.addCallback(connected)

		return self.client.d

	def test_regUnregApp(self):
		self.client.connect(Com.myPort)

		def res(result):
			self.assertTrue('success' in result['result'])
			d = deferLater(reactor, .5, self.client.end) #delay ending because Com might still be working
			return d

		def nack(reason):
			print reason
			self.client.end()

		def connected(obj):
			obj.callRemote('cmd', {'cmd': 'reg_app', 'name':'hola','port':10666})
			d = obj.callRemote('cmd', {'cmd': 'unreg_app', 'name':'hola'})
			d.addCallbacks(res, nack)
			#d.addCallback(lambda result: obj.broker.transport.loseConnection())

			return d

		self.client.d.addCallback(connected)

		return self.client.d

	def test_regAppTwice(self):
		self.client.connect(Com.myPort)

		def secondRes(result):
			self.assertTrue('failure' in result['result'])
			d = deferLater(reactor, .5, self.client.end) #delay ending because Com might still be working
			return d

		def res(result):
			self.assertTrue('success' in result['result'])
			
			return result

		def nack(reason):
			print reason
			self.client.end()

		def connected(obj):
			def sendAgain(result):
				 d= obj.callRemote('cmd', {'cmd': 'reg_app', 'name':'hola','port':10666})
				 d.addCallback(secondRes)
				 return d

			d = obj.callRemote('cmd', {'cmd': 'reg_app', 'name':'hola','port':10666})
			d.addCallbacks(res, nack)
			d.addCallback(sendAgain)
			#d.addCallback(lambda result: obj.broker.transport.loseConnection())

			return d

		self.client.d.addCallback(connected)

		return self.client.d

	def test_regAppNoName(self):
		self.client.connect(Com.myPort)

		def res(result):
			self.assertTrue('failure' in result['result'])
			d = deferLater(reactor, .5, self.client.end) #delay ending because Com might still be working
			return d

		def nack(reason):
			print reason
			self.client.end()

		def connected(obj):
			d = obj.callRemote('cmd', {'cmd': 'reg_app', 'port':10666})
			d.addCallbacks(res, nack)
			#d.addCallback(lambda result: obj.broker.transport.loseConnection())

			return d

		self.client.d.addCallback(connected)

		return self.client.d

	def test_regAppNoPort(self):
		self.client.connect(Com.myPort)

		def res(result):
			self.assertTrue('failure' in result['result'])
			d = deferLater(reactor, .5, self.client.end) #delay ending because Com might still be working
			return d

		def nack(reason):
			print reason
			self.client.end()

		def connected(obj):
			d = obj.callRemote('cmd', {'cmd': 'reg_app', 'name':'HOLA'})
			d.addCallbacks(res, nack)
			#d.addCallback(lambda result: obj.broker.transport.loseConnection())

			return d

		self.client.d.addCallback(connected)

		return self.client.d

	def test_regAppBadPort(self):
		self.client.connect(Com.myPort)

		def res(result):
			self.assertTrue('failure' in result['result'])
			d = deferLater(reactor, .5, self.client.end) #delay ending because Com might still be working
			return d

		def nack(reason):
			print reason
			self.client.end()

		def connected(obj):
			d = obj.callRemote('cmd', {'cmd': 'reg_app', 'name':'HOLA', 'port':'hello'})
			d.addCallbacks(res, nack)
			#d.addCallback(lambda result: obj.broker.transport.loseConnection())

			return d

		self.client.d.addCallback(connected)

		return self.client.d

	def test_readNoSentByOrDest(self):
		self.client.connect(Com.myPort)

		def readRes(result):
			self.assertTrue(result == None)
			self.client.end()			

		def nack(reason):
			print reason
			self.client.end()

		def connectAndRead(obj):
			d = obj.callRemote('read', {'msg':'hello','app':'HOLA'})
			d.addCallback(readRes)
			return d

		def newConnect(res):
			self.client.end()
			self.client.connect(Dummy.myPort)
			self.client.d.addCallback(connectAndRead)
			return self.client.d


		def connected(obj):
			d = obj.callRemote('cmd', {'cmd': 'reg_app', 'name':'HOLA'})
			#d.addCallbacks(res, nack)
			d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), nack)
			d.addCallback(newConnect)


			return d

		self.client.d.addCallback(connected)

		return self.client.d

	def test_readNoDest(self):
		self.client.connect(Com.myPort)

		def readRes(result):
			self.assertTrue(result == None)
			self.client.end()			

		def nack(reason):
			print reason
			self.client.end()

		def connectAndRead(obj):
			d = obj.callRemote('read', {'msg':'hello', 'sentby':'127.0.0.1','app':'HOLA'})
			d.addCallback(readRes)
			return d

		def newConnect(res):
			self.client.end()
			self.client.connect(Dummy.myPort)
			self.client.d.addCallback(connectAndRead)
			return self.client.d


		def connected(obj):
			d = obj.callRemote('cmd', {'cmd': 'reg_app', 'name':'HOLA'})
			#d.addCallbacks(res, nack)
			d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), nack)
			d.addCallback(newConnect)


			return d

		self.client.d.addCallback(connected)

		return self.client.d

	def test_readNoSentBy(self):
		self.client.connect(Com.myPort)

		def readRes(result):
			self.assertTrue(result == None)
			self.client.end()			

		def nack(reason):
			print reason
			self.client.end()

		def connectAndRead(obj):
			d = obj.callRemote('read', {'msg':'hello','dest':1,'app':'HOLA'})
			d.addCallback(readRes)
			return d

		def newConnect(res):
			self.client.end()
			self.client.connect(Dummy.myPort)
			self.client.d.addCallback(connectAndRead)
			return self.client.d


		def connected(obj):
			d = obj.callRemote('cmd', {'cmd': 'reg_app', 'name':'HOLA'})
			#d.addCallbacks(res, nack)
			d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), nack)
			d.addCallback(newConnect)


			return d

		self.client.d.addCallback(connected)

		return self.client.d

	def test_read(self):
		self.client.connect(Com.myPort)

		message = {'msg':'hello','sentby':'127.0.0.1','dest':1,'app':'HOLA'}

		def readRes(result):
			message['radio'] = 'Dummy'

			self.assertTrue(message == self.app.app.received)
			self.client.end()			

		def nack(reason):
			print reason
			self.client.end()

		def connectAndRead(obj):
			d = obj.callRemote('read', message)
			d.addCallback(readRes)
			d.addCallback(lambda result: obj.broker.transport.loseConnection())
			return d

		def newConnect(res):
			self.client.end()
			self.client.connect(Dummy.myPort)
			self.client.d.addCallback(connectAndRead)
			return self.client.d


		def connected(obj):
			d = obj.callRemote('cmd', {'cmd': 'reg_app', 'name':'HOLA', 'port':6666})
			#d.addCallbacks(res, nack)
			d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), nack)
			d.addCallback(newConnect)


			return d

		self.client.d.addCallback(connected)

		return self.client.d

	def test_writeDummy(self):
		self.client.connect(Com.myPort)
		self.wifiMgr.stop()

		message = {'msg':'hello','dest':1}

		def res(result):
			self.assertTrue(message['msg'] == result['msg'] and 'success' in result['result'])
			self.client.end()		

		def nack(reason):
			reason.printTraceback()
			self.client.end()
			self.assertTrue(False)

		def failed(reason):
			print 'failed!'
			print reason

		def connected(obj):
			d = deferLater(reactor, .5, obj.callRemote, 'write', message)
			d.addCallbacks(res, nack)
			d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), nack)

			return d

		self.client.d.addCallbacks(connected, failed)

		return self.client.d

	def test_writeWiFi(self):
		self.client.connect(Com.myPort)
		self.dummy.stop()

		message = {'msg':'hello','dest':1}

		def res(result):
			self.assertTrue(message['msg'] == result['msg'] and 'success' in result['result'])
			self.client.end()		

		def nack(reason):
			reason.printTraceback()
			self.client.end()
			self.assertTrue(False)

		def failed(reason):
			print 'failed!'
			print reason

		def connected(obj):
			d = deferLater(reactor, .5, obj.callRemote, 'write', message)
			d.addCallbacks(res, nack)
			d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), nack)

			return d

		self.client.d.addCallbacks(connected, failed)

		return self.client.d

	def test_writeBoth(self):
		self.client.connect(Com.myPort)

		message = {'msg':'hello','dest':1}

		def res(result):
			self.assertTrue(message['msg'] == result['msg'] and 'success' in result['result'])
			self.client.end()		

		def nack(reason):
			reason.printTraceback()
			self.client.end()
			self.assertTrue(False)

		def failed(reason):
			print 'failed!'
			print reason

		def connected(obj):
			d = deferLater(reactor, .5, obj.callRemote, 'write', message)
			d.addCallbacks(res, nack)
			d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), nack)

			return d

		self.client.d.addCallbacks(connected, failed)

		return self.client.d

	def test_commandGetNeighbors(self):
		self.client.connect(Com.myPort)

		command = {'cmd':'get_neighbors'}

		def res(result):
			self.assertTrue(isinstance(result['result'],list))
			self.client.end()		

		def nack(reason):
			reason.printTraceback()
			self.client.end()
			self.assertTrue(False)

		def failed(reason):
			print 'failed!'
			print reason

		def connected(obj):
			d = deferLater(reactor, .5, obj.callRemote, 'cmd', command)
			d.addCallbacks(res, nack)
			d.addCallbacks(lambda result: obj.broker.transport.loseConnection(), nack)

			return d

		self.client.d.addCallbacks(connected, failed)

		return self.client.d



