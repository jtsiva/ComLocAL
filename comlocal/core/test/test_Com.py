#!/usr/bin/python

from twisted.spread import pb
from twisted.internet import reactor
from twisted.trial.unittest import TestCase

from comlocal.radio.RadioManager import RadioManager
from comlocal.core.Com import Com



class Client (object):
	def connect(self):
		factory = pb.PBClientFactory()
		self.connect = reactor.connectTCP("localhost", Com.myPort, factory)
		self.d = factory.getRootObject()

	def end(self):
		self.connect.disconnect()
		#reactor.stop()

class ComTestCase(TestCase):
	def setUp(self):
		self.port = reactor.listenTCP(RadioManager.myPort, pb.PBServerFactory(Com()), interface='127.0.0.1')
		self.portnum = self.port.getHost().port
		self.client = Client()
		self.client.connect()
		

	def tearDown(self):
		port, self.port = self.port, None
		self.client.end()
		return port.stopListening()