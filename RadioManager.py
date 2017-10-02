#!/usr/bin/python

import Radio
import threading
import Queue
import Packet

class RadioManager(None):
	def __init__(Radio rad):
		#In Q
		#out Q
		_radio = rad
		# start _proc threads
		pass

	def _procRead():
		"""
		Thread for processing read queue.
		Parse radio input and turn into packet objects which
		are placed in the read Q
		"""
		pass

	def _procWrite():
		"""
		Thread for processing write queue. 
		Pulls packet off and turns into byte stream which is
		written to radio
		"""
		pass

	def read(n):
		"""
		Read n packets from the read Q and return as a list
		"""
		pass

	def write(packets):
		"""
		Add packet(s) to write Q.
		"""
		pass

	def scan():
		"""
		pass-through
		"""
		pass

	def range():
		"""
		pass-through
		"""
		pass


#