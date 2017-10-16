#!/usr/bin/python

import unittest
from core import ComLocAL

class TestComLocAL(unittest.TestCase):
	def setUp(self):
		self.myComlocal = ComLocAL.ComLocAL()

	@unittest.skip("ComLocAL not implemented")
	def test_comlocal_init(self):
		pass
#

if __name__ == '__main__':
	unittest.main()