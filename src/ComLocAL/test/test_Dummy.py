#!/usr/bin/python

import unittest
from radio import Dummy
from util import Packet

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

	def test_dummy_gen_100_valid_packets(self):
		for x in range(100):
			self.myRad._generatePacketBytes()
			print x
			newPacket = Packet.Packet()
			newPacket.parseFromBytes(self.myRad._bytesToRead)
			#print newPacket._calcChkSum()
			self.assertEquals(newPacket.isValid(), True)
		#

if __name__ == '__main__':
	unittest.main()