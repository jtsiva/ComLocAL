#!/usr/bin/python

from radio import Radio
import threading
import Queue
from util import Packet

class RadioManager:
	def __init__(self, myrad):
		#In Q
		#out Q
		_radio = myRad
		# start _proc threads
		pass

	def _procRead(self):
		"""
		Thread for processing read queue.
		Parse radio input and turn into packet objects which
		are placed in the read Q
		"""
		pass

	def _procWrite(self):
		"""
		Thread for processing write queue. 
		Pulls packet off and turns into byte stream which is
		written to radio
		"""
		pass

	def read(self, n):
		"""
		Read n packets from the read Q and return as a list
		"""
		pass

	def write(self, packets):
		"""
		Add packet(s) to write Q.
		"""
		pass

	def scan(self):
		"""
		pass-through
		"""
		pass

	def range(self):
		"""
		pass-through
		"""
		pass


#
