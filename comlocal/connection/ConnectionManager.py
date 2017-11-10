
from comlocal.radio import Radio
from comlocal.radio import WiFi
import threading
import time

class Stats(object):
	def __init__(self):
		self.read = 0
		self.write = 0
		self.lastUsed = 0
		self.packetsDropped = 0 #poorly formed packets
		self.up = True

class ConnectionManager(object):
	"""
	This class is responsible for implementing network protocols,
	maintaining connections, and managing the state of the hardware

	"""

	def __init__(self, commonData):
		self._commonData = commonData
		self._radioList = self._getAvailableRadios() #prioritized list of radios
		self._radioStats = {}
		for radio in self._radioList:
			self._radioStats[radio._name()] = Stats()
		#
	#

	def _getAvailableRadios(self):
		"""
		Eventually read from config file
		"""
		return [WiFi.WiFi()]

	def _checkRadios(self):
		"""
		Check if radios are properly functioning
		TODO: implement
		"""
		pass

	def _ping(self):
		"""
		Send basic "Hello!" message on all radios
		"""
		for radio in self._radioList:
			radio.write(json.loads('{"type":ping, "payload":}'))

	def _handlePing(self, pings):
		"""
		Do something with a ping
		TODO: implement
		"""
		pass

	def _isPing(self, msg):
		try:
			return msg["type"] == "ping"
		except KeyError:
			return False

	def _addRadioField(msg, radioName):
		msg['radio'] = radioName
		return msg


	def read(self):
		"""
		Read from each radio and return all objects. Filter and handle
		pings as this level.

		Non-blocking

		TODO: exception handling for broken things
		"""
		data = []
		for radio in self._radioList:
			data.append(_addRadioField(radio.read(), radio._name))
		#

		self._handlePing(filter(lambda x: self._isPing(x), data))
		return filter(lambda x: not self._isPing(x), data)
	#

	def chooseRadios(self, msg):
		"""
		Return an ordered list of which radios should be used based
		on the message contents (length of msg, QoS req's, possible
		restrictions, etc)

		TODO: make more sophisticated
		"""
		return self._radioList

	def write(self, msg):
		"""
		Write msg to radios

		return true if successful, false otherwise
		"""
		try:
			for radio in filter(lambda x: x._name in msg['radios'], self._radioList):
				radio.write(msg)
			#
			return True
		except Exception as e:
			return False

		








#