#!/usr/bin/python

import unittest
import os

class TestOnPlatform(unittest.TestCase):
	@unittest.skipIf(not os.uname()[4].startswith("arm"), "Not testing on RPi")
	def test_on_platform(self):
		self.assertTrue(True)
#