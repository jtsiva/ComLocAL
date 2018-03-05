from unittest import TestCase
from comlocal.radio.RadioManager import RadioManager, RadioTransport

import time


class Frame:
	def __init__(self):
		self.hit = False

	def read(self, message):
		self.hit = True

	def write(self, message, addr):
		self.hit = True

	def allowMsgFromSelf(self, b):
		self.allow = b


#need to have all daemons started in the background
class RadioManagerTestCase(TestCase):
	def setUp(self):
		self.radmgr = RadioManager('radmgr')
		self.frame = Frame()
		self.transport = RadioTransport()

	def tearDown(self):
		pass

	def test_mgrNotSet(self):
		self.assertTrue(self.transport.manager is None)

	def test_mgrSet(self):
		self.transport.setManager(self.radmgr)
		self.assertTrue(self.transport.manager == self.radmgr)

	def test_readNoSentby(self):
		message = {'msg':'hello'}
		ok = False
		try:
			self.radmgr.read(message)
		except KeyError:
			ok = True

		self.assertTrue(ok)

	def test_read(self):
		message = {'msg':'hello', 'sentby':'sombody'}

		self.radmgr.read(message)
		self.assertTrue('sombody' in self.radmgr.connections)

	def test_readCB(self):
		message = {'msg':'hello', 'sentby':'sombody'}
		self.radmgr.setReadCB(self.frame.read)
		self.radmgr.read(message)

		self.assertTrue(self.frame.hit)

	def test_setTransport(self):
		self.radmgr.setTransport(self.frame)
		self.assertTrue(self.frame == self.radmgr.transport)

	def test_cmdGetStatus(self):
		cmd = {'cmd':'get_status'}
		ret = self.radmgr.cmd(cmd)

		self.assertTrue(ret['result']['running'])

	def test_cmdGetProps(self):
		cmd = {'cmd':'get_props'}
		ret = self.radmgr.cmd(cmd)

		self.assertTrue(not ret['result'])

	def test_cmdNotRecognized(self):
		cmd = {'cmd':'win'}
		ret = self.radmgr.cmd(cmd)

		self.assertTrue('failure' in ret['result'])

	def test_cmdKeyError(self):
		cmd = {'CMD':'get_props'}
		ret = self.radmgr.cmd(cmd)

		self.assertTrue('failure' in ret['result'])

	def test_writeNoTransport(self):
		message = {'msg':'hello', 'addr':'sombody'}

		ret = self.radmgr.write(message)
		self.assertTrue(not self.frame.hit and 'failure' in ret['result'])

	def test_writeNoAddr(self):
		message = {'msg':'hello'}

		self.radmgr.setTransport(self.frame)
		ret = self.radmgr.write(message)
		self.assertTrue(not self.frame.hit and 'failure' in ret['result'])


	def test_write(self):
		message = {'msg':'hello', 'addr':'sombody'}

		self.radmgr.setTransport(self.frame)
		ret = self.radmgr.write(message)
		self.assertTrue(self.frame.hit and 'success' in ret['result'])



