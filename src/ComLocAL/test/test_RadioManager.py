#!/usr/bin/python

import unittest
from radio import RadioManager

class TestRadioManager(unittest.TestCase):

	def setUp(self):
		pass
	#

	def test_init_manager(self):
		#Need dummy radio to test
		self.assertEqual(False, True)

#

if __name__ == '__main__':
	unittest.main()
		
