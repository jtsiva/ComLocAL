
from comlocal.radio import WiFi
from comlocal.connection import ConnectionLayer
from comlocal.routing import RoutingLayer
from comlocal.util import CommonData
from comlocal.message import MessageLayer
import random

class Com(object):
	def __init__(self):
		self._commonData = CommonData.CommonData()
		self._connL = ConnectionLayer.ConnectionLayer(self._commonData, self._getRadios())
		self._routeL = RoutingLayer.RoutingLayer(self._commonData)
		self._messageL = MessageLayer.MessageLayer(self._commonData)

		#set up connections between layers
		self._routeL.setRead(self._connL.read)
		self._routeL.setWrite(self._connL.write)

		self._messageL.setRead(self._routeL.read)
		self._messageL.setWrite(self._routeL.write)

	def _initCommonData(self):
		"""
		Init the common data by, say, reading from a file

		TODO: read beginning config from file
		"""
		self._commonData.id = random.randRange(255)


	def _getRadios(self):
		"""
		List of radios to initialize and pass to connection manager.
		
		TODO: Read radio list from config file
		"""
		return [WiFi.WiFi()]


	def read(self):
		return self._messageL.read()

	def write(self, msg):
		return self._messageL.write(msg)

#