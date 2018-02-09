#!/usr/bin/python

from twisted.spread import pb
from twisted.internet import reactor
from twisted.internet.task import deferLater
from twisted.trial.unittest import TestCase

from comlocal.radio.WiFiManager import WiFiManager, WiFiTransport
from comlocal.radio.RadioManager import RadioManager


class Client (object):
	def connect(self):
		factory = pb.PBClientFactory()
		self.connect = reactor.connectTCP("localhost", WiFiManager.myPort, factory)
		self.d = factory.getRootObject()

	def end(self):
		self.connect.disconnect()
		#reactor.stop()

class Local(pb.Root):
	def __init__(self):
		self.received = False
	def remote_read(self, message):
		self.received = True
		return message


class RadMgr(object):
	def start(self):
		self.port = reactor.listenTCP(RadioManager.myPort, pb.PBServerFactory(RadioManager()), interface='127.0.0.1')
		self.portnum = self.port.getHost().port

	def stop(self):
		port, self.port = self.port, None
		return port.stopListening()

class WiFiManagerTestCase(TestCase):
	def setUp(self):
		self.radmgr = RadMgr()
		self.radmgr.start()
		self.d = None
		wifiManager = WiFiManager()
		self.wifiTransport = WiFiTransport()
		wifiManager.setTransport(self.wifiTransport)
		self.wifiTransport.setManager(wifiManager)

		self.tcpPort = reactor.listenTCP(WiFiManager.myPort, pb.PBServerFactory(wifiManager), interface='127.0.0.1')
		
		self.local = Local()
		self.localPort = reactor.listenTCP(6666, pb.PBServerFactory(self.local), interface='127.0.0.1')

		self.udpPort = reactor.listenUDP(WiFiTransport.myPort, self.wifiTransport)

		self.client = Client()
		self.client.connect()
		

	def tearDown(self):
		self.radmgr.stop()
		self.client.end()
		if self.d is not None:
			self.d.cancel()
		port, self.localPort = self.localPort, None
		port.stopListening()
		port, self.tcpPort = self.tcpPort, None
		port.stopListening()
		port, self.udpPort = self.udpPort, None
		return port.stopListening()

	def test_reg(self):
		def res(result):
			self.assertTrue(result['result'] == 'True')

		def connected(obj):
			d = deferLater(reactor, 2.0, obj.callRemote, 'cmd', {'cmd': 'check_radio_reg'})
			d.addCallback(res)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_props(self):
		def res(result):
			self.assertTrue('port' in result['result'] and 'maxPacketLength' in result['result'] and 'costPerByte' in result['result'])

		def connected(obj):
			d = obj.callRemote('cmd', {'cmd': 'get_props'})
			d.addCallback(res)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_writeNoAddr(self):
		def res(result):
			self.assertTrue('failure' in result['result'])

		def connected(obj):
			d = obj.callRemote('write', {'msg': 'hello world!!!'})
			d.addCallback(res)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_writeNoDict(self):
		def res(result):
			self.assertTrue('failure' in result['result'])

		def nack(reason):
			self.assertTrue(True)

		def connected(obj):
			d = obj.callRemote('write', 'hello world!!!')
			d.addCallback(res)
			d.addErrback(nack)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_write(self):
		def res(result):
			self.assertTrue('success' in result['result'])

		def nack(reason):
			self.assertTrue(True)

		def connected(obj):
			d = obj.callRemote('write', {'msg': 'hello world!!!', 'addr' :'192.168.0.255'})
			d.addCallbacks(res, nack)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_regLocal(self):
		def res(result):
			self.assertTrue('success' in result['result'])

		def connected(obj):
			d = obj.callRemote('cmd', {'cmd': 'reg_local','port':6666})
			d.addCallback(res)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_regAndGetLocal(self):
		def res(result):
			self.assertTrue(6666 in result['result'])

		def connected(obj):
			obj.callRemote('cmd', {'cmd': 'reg_local','port':6666})
			d = obj.callRemote('cmd', {'cmd': 'get_local'})
			d.addCallback(res)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_regAndUnregLocal(self):
		def res(result):
			self.assertTrue(len(result['result'])== 0)

		def connected(obj):
			obj.callRemote('cmd', {'cmd': 'reg_local','port':6666})
			obj.callRemote('cmd', {'cmd': 'unreg_local','port':6666})
			d = obj.callRemote('cmd', {'cmd': 'get_local'})
			d.addCallback(res)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_regLocalAndSend(self):

		def send(result):
			self.wifiTransport.datagramReceived('{"msg":"Hello"}', ('127.0.0.1', 10666))
			self.d = deferLater( reactor, 1.0, res, None)
			return self.d

		def res(result):
			self.assertTrue(self.local.received)

		def connected(obj):
			d = obj.callRemote('cmd', {'cmd': 'reg_local','port':6666})
			obj.callRemote('cmd', {'cmd': 'allow_from_self'})
			
			d.addCallback(send)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d


	def test_notACommand(self):
		def res(result):
			self.assertTrue('failure' in result['result'])

		def connected(obj):
			d = obj.callRemote('cmd', {'cmd': 'hola!'})
			d.addCallback(res)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_cmdNotJSON(self):
		def res(result):
			self.assertTrue('failure' in result['result'])

		def nack(reason):
			self.assertTrue(True)

		def connected(obj):
			d = obj.callRemote('cmd', 'hola!')
			d.addCallbacks(res, nack)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d