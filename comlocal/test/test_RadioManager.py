#!/usr/bin/python

import unittest
from radio import RadioManager
from radio import Dummy

class TestRadioManager(unittest.TestCase):

	def setUp(self):
		self.myRad = Dummy.Dummy()
		self.radManager = RadioManager.RadioManager(self.myRad)
	#

	def tearDown(self):
		self.radManager.stop()

	#TODO: need to adjust Dummy to limit how often new data is generated
	#		or else Radio Manager read Q will become extraordinarily large
	def test_radio_manager_read_0(self):
		d = self.radManager.read(0)
		self.assertEquals(len(d), 0)

	def test_radio_manager_read_1000_packets(self):
		for x in range(1000):
			p = self.radManager.read(1)[0]
			self.assertEquals(p.isValid(), True)
		#
	#

	def test_radio_manager_write_packet(self):
		p = self.radManager.read(1)[0]
		self.assertEquals(self.radManager.write([p]), 1)

#

if __name__ == '__main__':
	unittest.main()
		
