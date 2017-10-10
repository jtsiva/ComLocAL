#!/usr/bin/python

import unittest
from radio import WiFi
from util import Packet
import socket

class TestWiFiRadio(unittest.TestCase):

	def setUp(self):
		self.myRad = WiFi.WiFi()
	#

	@unittest.skip("Need multicast server running on another machine")
	def test_wifi_radio_read(self):
		self.assertEquals(len(self.myRad.read(10)), 10)
	#

	def test_wifi_radio_write(self):
		self.assertEquals(self.myRad.write('hello'), 5)
	#

	def test_wifi_radio_properties_address(self):
		props = self.myRad.getProperties()
		success = True
		try:
			socket.inet_aton(props.addr)
		except socket.error:
			success = False

		self.assertTrue(success)
	#

	def test_wifi_radio_properties_packet_len(self):
		props = self.myRad.getProperties()
		self.assertEquals(props.maxPacketLength, 512)
	#


if __name__ == '__main__':
	unittest.main()