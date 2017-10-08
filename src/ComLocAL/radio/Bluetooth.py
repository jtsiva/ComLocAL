#!/usr/bin/python

from radio import radio

class Bluetooth (Radio):
	"""
	Abstracts all communication over Bluetooth / BLE

	All communication is broadcast
	"""
	def __init__ (self):
		self._name = 'BT'
		pass
#