
from comlocal.radio import Radio
import threading
import time

class Stats(object):
	def __init__(self):
		self.read = 0
		self.write = 0
		self.lastUsed = 0
		self.packetsDropped = 0 #poorly formed packets
		self.up = True

class ConnectionLayer(object):
	"""
	This class is responsible for implementing network protocols,
	maintaining connections, and managing the state of the hardware

	"""

	def __init__(self, commonData, radioList):
		self._commonData = commonData
		self._radioList = radioList #prioritized list of radio objects
		self._radioStats = {}
		for radio in self._radioList:
			self._radioStats[radio._name] = Stats()
		#

		self._checkRadios() #weed out any radios that are not *actually* active
		self._commonData.activeRadios = [radio._name for radio in self._radioList] #initialize commonData
	#

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
		ping = json.loads('{"type":"ping"}')
		ping['src'] = self._commonData.id

		for radio in self._radioList:
			radio.write(ping)

	def _addRadioField(self, msg, radioName):
		"""
		Add a field to the message indicating which interface the message
		arrived on.
		"""
		try:
			del msg['radios'] #appended by sender but not needed on read
		except Exception as e:
			pass #do nothing (this *might* be useful later)

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
			msg = radio.read()
			try:
				msg = msg if msg['sentby'] != radio.getProperties().addr else None
			except KeyError:
				pass

			None if not msg else data.append(self._addRadioField(msg, radio._name))
		#

		return data
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