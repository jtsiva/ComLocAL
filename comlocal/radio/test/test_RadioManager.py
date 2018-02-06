#!/usr/bin/python

from twisted.spread import pb
from twisted.internet import reactor
from twisted.trial.unittest import TestCase

from comlocal.radio.RadioManager import RadioManager


class Client (object):
	def connect(self):
		factory = pb.PBClientFactory()
		self.connect = reactor.connectTCP("localhost", RadioManager.myPort, factory)
		self.d = factory.getRootObject()

	def end(self):
		self.connect.disconnect()
		#reactor.stop()

class RadioMangerTestCase(TestCase):
	def setUp(self):
		self.port = reactor.listenTCP(RadioManager.myPort, pb.PBServerFactory(RadioManager()), interface='127.0.0.1')
		self.portnum = self.port.getHost().port
		self.client = Client()
		self.client.connect()
		

	def tearDown(self):
		port, self.port = self.port, None
		self.client.end()
		return port.stopListening()

	def test_connect(self):
		def connected(obj):
			self.assertTrue(True)

		def failed (reason):
			self.assertTrue(False)

		self.client.d.addCallbacks(connected, failed)

		return self.client.d

	def test_write(self):
		
		def writeRes(result):
			self.assertEquals(result, 'hello. this is some text.')

		def connected(obj):
			d = obj.callRemote('write', 'hello. this is some text.')
			d.addCallback(writeRes)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_cmdNoRadios(self):

		def cmdRes(result):
			self.assertEquals(result,{'cmd':'get_radios','result':{}})

		def connected(obj):
			d = obj.callRemote('cmd', {'cmd':'get_radios'})
			d.addCallback(cmdRes)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_addRadio(self):
	
		def cmdRes(result):
			self.assertTrue('success' in result['result'])

		def connected(obj):
			d = obj.callRemote('cmd', {'cmd':'reg_radio', 'name':'test', 'props':{'port':6666}})
			d.addCallback(cmdRes)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_addRadioAndCheck(self):
		

		def cmdRes(result):
			self.assertEquals(result['result'], {'test': {'port':6666}})

		def connected(obj):
			obj.callRemote('cmd', {'cmd':'reg_radio', 'name':'test', 'props':{'port':6666}})
			d = obj.callRemote('cmd', {'cmd':'get_radios'})
			d.addCallback(cmdRes)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_addAndRemoveRadio(self):
		
		def cmdRes(result):
			self.assertEquals(result, {'cmd':'get_radios','result':{}})

		def connected(obj):
			obj.callRemote('cmd', {'cmd':'reg_radio', 'name':'test', 'props':{'port':6666}})
			obj.callRemote('cmd', {'cmd':'get_radios'})
			obj.callRemote('cmd', {'cmd':'unreg_radio', 'name' : 'test'})
			d = obj.callRemote('cmd', {'cmd':'get_radios'})
			d.addCallback(cmdRes)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_noCmd(self):
		
		def cmdRes(result):
			self.assertTrue('failure' in result['result'])

		def connected(obj):
			d = obj.callRemote('cmd', {'msg':'hello'})
			d.addCallback(cmdRes)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_unknownCmd(self):
		
		def cmdRes(result):
			self.assertTrue('failure' in result['result'])

		def connected(obj):
			d = obj.callRemote('cmd', {'cmd':'hello'})
			d.addCallback(cmdRes)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_noRadioToRemove(self):
		
		def cmdRes(result):
			self.assertTrue('failure' in result['result'])

		def connected(obj):
			d = obj.callRemote('cmd', {'cmd':'unreg_radio', 'name' :'hello'})
			d.addCallback(cmdRes)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_removeNoName(self):
		
		def cmdRes(result):
			self.assertTrue('failure' in result['result'])

		def connected(obj):
			d = obj.callRemote('cmd', {'cmd':'unreg_radio'})
			d.addCallback(cmdRes)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_regNoPropsKey(self):
		
		def cmdRes(result):
			self.assertTrue('failure' in result['result'])

		def connected(obj):
			d = obj.callRemote('cmd', {'cmd':'reg_radio', 'name':'test'})
			d.addCallback(cmdRes)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d

	def test_regNoName(self):
		
		def cmdRes(result):
			self.assertTrue('failure' in result['result'])

		def connected(obj):
			d = obj.callRemote('cmd', {'cmd':'reg_radio','props':{}})
			d.addCallback(cmdRes)
			return d

		self.client.d.addCallback(connected)

		return  self.client.d








