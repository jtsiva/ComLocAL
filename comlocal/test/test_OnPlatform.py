#!/usr/bin/python

import unittest
import os

class TestOnPlatform(unittest.TestCase):
	def test_on_Raspberry_Pi(self):
		self.assertTrue(os.uname()[4].startswith("arm"))
#