#!/usr/bin/python


from twisted.internet import reactor
from twisted.trial.unittest import TestCase
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import deferLater

from comlocal.radio.WiFiManager import WiFiManager, WiFiTransport, startTransport
from comlocal.radio.RadioManager import RadioManager

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


class Frame:
	def __init__(self):
		self.hit = False

	def read(self, message):
		self.hit = True

	def write(self, message, addr):
		self.hit = True


class WiFiManagerTestCase(TestCase):
	def setUp(self):
		self.frame = Frame()
		self.wifiManager = WiFiManager()
		self.wifiTransport = WiFiTransport()
		self.wifiManager.setTransport(self.wifiTransport)
		self.wifiTransport.setManager(self.wifiManager)
		self.port = startTransport(self.wifiTransport)

		self.client = udpClient()
		self.client.start()

	def tearDown(self):
		self.client.stop()
		return self.port.stopListening()

	def test_name(self):
		self.assertTrue('WiFi' == self.wifiManager.name)

	def test_cmdGetProps(self):
		cmd = {'cmd':'get_props'}
		ret = self.wifiManager.cmd(cmd)

		self.assertTrue(ret['result']['addr'] == self.wifiManager.props['addr'] 
			and ret['result']['bcastAddr'] == self.wifiManager.props['bcastAddr']
			and ret['result']['costPerByte'] == self.wifiManager.props['costPerByte'])

	def test_read(self):
		message = {'msg':'hello'}

		self.wifiManager.setReadCB(self.frame.read)
		self.wifiTransport.read(message)
		self.assertTrue(self.frame.hit)

	def test_readFromUDP(self):
		message = {'msg':'hello'}

		def blah():
			self.assertTrue(self.frame.hit)

		self.wifiManager.setReadCB(self.frame.read)
		self.client.write(message)
		d=deferLater(reactor, .1, blah)
		return d