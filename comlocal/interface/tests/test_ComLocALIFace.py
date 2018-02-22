#!/usr/bin/python

from twisted.spread import pb
from unittest import TestCase
from comlocal.interface.ComLocALIFace import ComLocAL

import time


#need to have all daemons started in the background
class ComTestCase(TestCase):
	def setUp(self):
		self.comlocal = ComLocAL('test', 10777)

	def tearDown(self):
		self.comlocal.stop()

	def test_setTimeout(self):
		self.comlocal.setTimeout(3)
		self.assertTrue(ComLocAL.timeout == 3)

	def test_startAndReg(self):
		self.comlocal.start()
		self.assertTrue(self.comlocal.registered)

	def test_write(self):
		self.comlocal.setTimeout(5.0)
		self.comlocal.start()
		res = self.comlocal.comWrite('blargity blarg', 5)
		self.assertTrue('success' in res['result'])

	def test_read(self):
		#need to have additional Dummy radio running with client sending 'hello' messages to it
		self.comlocal.setTimeout(5.0)
		def read(data):
			self.assertTrue('hello' in data['msg'])
		self.comlocal.setReadCB(read)
		self.comlocal.start()
		time.sleep(1.0)