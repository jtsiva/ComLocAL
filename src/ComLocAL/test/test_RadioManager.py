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
	def test_read_0(self):
		d = self.radManager.read(0)
		self.assertEquals(len(d), 0)


#

if __name__ == '__main__':
	unittest.main()
		
