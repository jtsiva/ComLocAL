#!/usr/bin/python

import socket
import unittest
from radio import WiFi
from radio import RadioManager
from util import Packet
import os

class WiFiTestFramework(object):
	def __init__(self):
		self.active = False
		self.rsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.wsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.rsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.wsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		#self.wsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.rsock.settimeout(5)
		self.rsock.bind(('0.0.0.0', 10247))

	def start(self):
		"""
		Check/start simple server is running on a device in the
		ad-hoc network with address 10.2.1.1
		"""
		

		self.wsock.sendto("start?", ('10.2.1.1', 10247))

		#try:
		#	data, addr = self.rsock.recvfrom(16)
		#	print data
		#	if "start!" in data:
		#		self.active = True
		#		print self.active
		#except socket.timeout:
		#	print 'timed out'
		self.active = True

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
	#

	@unittest.skipIf(not os.uname()[4].startswith("arm"), "Not on RPi")
	def test_wifi_radio_read(self):
		wifiFramework.start()
		if wifiFramework.isActive():
			self.assertEquals(len(self.myRad.read(12)), 12)
		else:
			self.assertTrue(False)
	#

	def test_wifi_radio_write(self):
		self.assertEquals(self.myRad.write([10,2,1,1], 'hello'), 5)
	#

	@unittest.skipIf(not os.uname()[4].startswith("arm"), "Not on RPi")
	def test_wifi_radio_properties_address(self):
		props = self.myRad.getProperties()
		self.assertEquals('10.2.1', props.addr[:6])
	#

	def test_wifi_radio_properties_packet_len(self):
		props = self.myRad.getProperties()
		self.assertEquals(512, props.maxPacketLength)
	#

	def test_wifi_radio_scan(self):
		neighbors = self.myRad.scan()
		self.assertTrue(len(neighbors) >  0)
	#

	def test_radio_manager_wifi_scan(self):
		wifiRadMgr = RadioManager.RadioManager(self.myRad)
		self.assertTrue(len(wifiRadMgr.scan()) > 0)

			


if __name__ == '__main__':
	unittest.main()
