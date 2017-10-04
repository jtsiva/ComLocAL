#!/usr/bin/python

import unittest
from radio import RadioManager
from radio import Dummy

class TestRadioManager(unittest.TestCase):

	def setUp(self):
		self.myRad = Dummy.Dummy()
	#

	def test_init_manager(self):
		self.radManager = RadioManager.RadioManager(self.myRad)
		self.assertEqual(False, True)
	#

#

if __name__ == '__main__':
	unittest.main()
		
