#!/usr/bin/python

import unittest
import Packet

class TestPacket(unittest.TestCase):

	def setUp(self):
		pass
		
	def test_null_packet_validity(self):
		self.packet = Packet.Packet()
		self.assertEqual(self.packet.isValid(), False)
	#

	def test_null_packet_chksum(self):
		self.packet = Packet.Packet()
		self.assertEqual(self.packet._calcChkSum(), 0)
	#

	def test_packet_dest_set(self):
		self.packet = Packet.Packet()
		self.packet.setDest ('192.168.0.1')
		self.assertEqual(self.packet.isValid(), False)
	#

	def test_packet_src_set(self):
		self.packet = Packet.Packet()
		self.packet.setSrc ('192.168.0.1')
		self.assertEqual(self.packet.isValid(), False)
	#

	def test_packet_dest_and_src_set(self):
		self.packet = Packet.Packet()
		self.packet.setDest ('192.168.0.1')
		self.packet.setSrc ('192.168.0.2')
		self.assertEqual(self.packet.isValid(), True)
	#

	def test_packet_decrement_ttl(self):
		self.packet = Packet.Packet()
		self.packet.setDest ('192.168.0.1')
		self.packet.setSrc ('192.168.0.2')

		for i in range(5):
			self.packet.decTTL()
		#
		self.assertEqual(self.packet.isValid(), False)
	#

	def test_packet_set_data_chksum(self):
		self.packet = Packet.Packet()
		self.packet.setData('hello')
		self.assertEqual(self.packet._calcChkSum(), 236)
	#

	def test_packet_set_data_no_remainder(self):
		self.packet = Packet.Packet()
		r = self.packet.setData('hello')
		self.assertEqual(len(r), 0)
	#

	def test_packet_set_data_remainder(self):
		self.packet = Packet.Packet()
		myStr = ''
		for i in range(Packet.PACKET_TYPE.COMMON + 5):
			myStr += 'a'
		r = self.packet.setData(myStr)
		self.assertEqual(len(r), 5)
	#


#

if __name__ == '__main__':
	unittest.main()