from unittest import TestCase
from comlocal.radio.RadioManager import RadioManager
from comlocal.radio.LoopbackManager import LoopbackManager, LoopbackTransport, startTransport

import time


class Frame:
	def __init__(self):
		self.hit = False

	def read(self, message):
		self.hit = True

	def write(self, message, addr):
		self.hit = True


#need to have all daemons started in the background
class LoopbackManagerTestCase(TestCase):
	def setUp(self):
		self.loopback = LoopbackManager()
		self.transport = LoopbackTransport()
		self.frame = Frame()

	def tearDown(self):
		pass

	def test_name(self):
		self.assertTrue('Loopback' == self.loopback.name)

	def test_cmdGetProps(self):
		cmd = {'cmd':'get_props'}
		ret = self.loopback.cmd(cmd)

		self.assertTrue(ret['result']['addr'] == '<loopback>' 
			and ret['result']['bcastAddr'] == '<broadcast>'
			and ret['result']['costPerByte'] == .5)

	def test_write(self):
		message = {'msg':'hello'}

		self.loopback.setTransport(self.transport)
		self.transport.setManager(self.loopback)

		self.loopback.setReadCB(self.frame.read)

		self.transport.write(message, self.loopback.props['addr'])

		self.assertTrue(self.frame.hit)

	def test_startTransport(self):
		self.assertTrue(startTransport(self.transport) is None)


