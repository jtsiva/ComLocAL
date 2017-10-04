#!/usr/bin/python

import unittest
from radio import Dummy

class TestDummyRadio(unittest.TestCase):

	def setUp(self):
		self.myRad = Dummy.Dummy()
	#

	def test_dummy_radio_read(self):
		self.assertEquals(len(self.myRad.read(10)), 10)
	#

	def test_dummy_radio_write(self):
		self.assertEquals(self.myRad.write('hello'), 5)
	#

	def test_dummmy_radio_properties_address(self):
		props = self.myRad.getProperties()
		self.assertEquals(props[0][:12], '255.255.255.')
	#

	def test_dummmy_radio_properties_packet_len(self):
		props = self.myRad.getProperties()
		self.assertEquals(props[1], 127)
	#

	def test_dummmy_radio_properties_range(self):
		props = self.myRad.getProperties()
		self.assertEquals(props[2], 50)
	#

if __name__ == '__main__':
	unittest.main()