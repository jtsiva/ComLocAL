#!/usr/bin/python

from twisted.spread import pb
from unittest import TestCase
from comlocal.interface.ComLocALIFace import ComLocAL



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