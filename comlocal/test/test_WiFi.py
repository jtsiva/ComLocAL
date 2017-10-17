#!/usr/bin/python

import socket
import unittest
from radio import WiFi
from util import Packet

class WiFiTestFramework(object):
	def __init__(self):
		self.active = False

	def start(self):
		"""
		Check/start simple server is running on a device in the
		ad-hoc network with address 10.2.1.1
		"""
		rsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		wsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		rsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		wsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		wsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		rsock.settimeout(1)
		rsock.bind(('0.0.0.0', 10247))

		wsock.sendto("start?", ('10.2.1.1', 10247))

		try:
			data, addr = rsock.recvfrom(6)
			if "start!" in data:
				self.active = True
		except socket.timeout:
			pass

	def isActive(self):
		"""
		Return True if ready for testing
		"""
		return self.active
#

wifiFramework = WiFiTestFramework()

class TestWiFiRadio(unittest.TestCase):

	def setUp(self):
		self.myRad = WiFi.WiFi()
		wifiFramework.start()
	#

	@unittest.skipIf(not wifiFramework.isActive(), "Need WiFi framework to test")
	def test_wifi_radio_read(self):
		self.assertEquals(len(self.myRad.read(12)), 12)
	#

	def test_wifi_radio_write(self):
		self.assertEquals(self.myRad.write([10,2,1,1], 'hello'), 5)
	#

	def test_wifi_radio_properties_address(self):
		props = self.myRad.getProperties()
		self.assertEquals('10.2.1', props.addr[:6])
	#

	def test_wifi_radio_properties_packet_len(self):
		props = self.myRad.getProperties()
		self.assertEquals(512, props.maxPacketLength)
	#


if __name__ == '__main__':
	unittest.main()