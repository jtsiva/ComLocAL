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
		self.assertEquals(self.myRad.write([192,168,0,1], 'hello'), 5)
	#

	def test_dummmy_radio_properties_address(self):
		props = self.myRad.getProperties()
		self.assertEquals(props.addr[:12], '255.255.255.')
	#

	def test_dummmy_radio_properties_packet_len(self):
		props = self.myRad.getProperties()
		self.assertEquals(props.maxPacketLength, 127)
	#

	def test_dummmy_radio_properties_cost(self):
		props = self.myRad.getProperties()
		self.assertEquals(props.costPerByte, 1)
	#

	def test_dummy_gen_1000_valid_packets(self):
		for x in range(1000):
			newPacket = Packet.Packet()
			newPacket.parseFromBytes(self.myRad._bytesToRead)
			#print newPacket._calcChkSum()
			self.assertEquals(newPacket.isValid(), True)
		#
	#

	def test_dummy_continuous_read_10000_bytes(self):
		for x in range(10000):
			#print x
			b = self.myRad.read(1)
			#print b
			self.assertEquals(isinstance(b, list) and len(b) > 0, True)



if __name__ == '__main__':
	unittest.main()