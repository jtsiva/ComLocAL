#!/usr/bin/python

import unittest
from radio import WiFi
from util import Packet

class WiFiTestFramework(object):
	def start(self):
		pass

	def stop(self):
		pass

	def isActive(self):
		return False
#

wifiFramework = WiFiTestFramework()

class TestWiFiRadio(unittest.TestCase):

	def setUp(self):
		self.myRad = WiFi.WiFi()
		wifiFramework.start()
	#

	@unittest.skipIf(not wifiFramework.isActive(), "Need WiFi framework to test")
	def test_wifi_radio_read(self):
		pass#self.assertEquals(len(self.myRad.read(10)), 10)
	#

	def test_wifi_radio_write(self):
		self.assertEquals(self.myRad.write('10.2.1.1', 'hello'), 5)
	#

	def test_wifi_radio_properties_address(self):
		props = self.myRad.getProperties()
		
	#

	def test_wifi_radio_properties_packet_len(self):
		props = self.myRad.getProperties()
		
	#


if __name__ == '__main__':
	unittest.main()