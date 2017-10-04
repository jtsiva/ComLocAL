#!/usr/bin/python

from radio import radio

class WiFi (Radio):
	"""
	Facilitates / abstracts all communication over WiFi
	All communication is broadcast UDP

	"""
	def __init__ (self):
		self._name = 'WiFi'
		pass
#