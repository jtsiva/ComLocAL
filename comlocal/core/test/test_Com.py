#!/usr/bin/python

from twisted.spread import pb
from twisted.internet import reactor
from twisted.trial.unittest import TestCase
from twisted.internet.task import deferLater
from twisted.internet.protocol import ServerFactory, DatagramProtocol

from comlocal.radio.RadioManager import RadioManager
from comlocal.radio.WiFiManager import WiFiManager, WiFiTransport
from comlocal.radio.Dummy import Dummy
from comlocal.core.Com import Com

import json

class _udpClient (DatagramProtocol):

	def write(self, message):
		data = json.dumps(message, separators=(',', ':'))
		self.transport.write(data, ('127.0.0.1', WiFiTransport.myPort))

	def datagramReceived(self, data, (host, port)):
		pass

class udpClient(object):
	def __init__(self):
		self.client = _udpClient()
		self.port = None

	def write(self, message):
		self.client.write(message)

	def start(self):
		self.port = reactor.listenUDP(WiFiTransport.myPort+17, self.client, interface='127.0.0.1')

	def stop(self):
		if self.port is not None:
			self.port.stopListening()

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
		self.port = reactor.listenTCP(10666, pb.PBServerFactory(self.app), interface='127.0.0.1')
		self.portnum = self.port.getHost().port

	def stop(self):
		port, self.port = self.port, None
		return port.stopListening()





class ComTestCase(TestCase):
	def setUp(self):
		self.app = App()
		self.app.start()
		self.com = Com()

		self.port = reactor.listenTCP(Com.myPort, pb.PBServerFactory(self.com), interface='127.0.0.1')
		self.portnum = self.port.getHost().port
		self.client = Client()
		self.udpclient = udpClient()
		self.udpclient.start()


	def tearDown(self):
		self.client.end()
		self.com.stop()
		port, self.port = self.port, None
		self.app.stop()
		self.udpclient.stop()
		return port.stopListening()


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


	def test_read(self):
		self.client.connect(Com.myPort)

		message = {'msg':'hello','src':-1,'dest':1,'app':'hola'}

		def blah():
			self.assertTrue(self.app.app.received)

		def res(result):
			self.assertTrue('success' in result['result'])
			self.udpclient.write(message)
			d = deferLater(reactor, .1, blah)
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

	def test_readNoApp(self):
		self.client.connect(Com.myPort)

		message = {'msg':'hello','src':-1,'dest':1}

		def blah():
			self.assertTrue(self.app.app.received)

		def res(result):
			self.assertTrue('success' in result['result'])
			self.udpclient.write(message)
			d = deferLater(reactor, .1, blah)
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
		

	def test_writeBoth(self):
		self.client.connect(Com.myPort)

		message = {'msg':'hello','dest':1}

		def res(result):
			self.assertTrue(message['msg'] == result['msg'] and 'success' in result['result'][0])
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



