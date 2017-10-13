#!/usr/bin/python

class UWB (Radio):
	"""
	Abstracts all communication over UWB

	options include:
	  Ranging frequency | range after message
	"""
	def __init__(self):
		self._name = 'UWB'
		pass
#