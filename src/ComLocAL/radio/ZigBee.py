#!/usr/bin/python

from radio import radio

class ZigBee (Radio):
	"""
	Abstracts all communication over ZigBee
	Scan could be useful for building up the network structure

	options include:
	  TX pwr
	"""
	def __init__ (self):
		self._name = 'ZB'
		pass
#