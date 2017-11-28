from comlocal.util import Properties
import Radio
import json
import bluetooth

class Bluetooth (Radio.Radio):
	"""
	Abstracts all communication over Bluetooth / BLE

	All communication is broadcast
	"""
	def __init__ (self):
		super(Bluetooth, self).__init__(self._setupProperties())
		self._name = 'BT'
		self._port = 0x2807
		self._sock=bluetooth.BluetoothSocket(bluetooth.L2CAP)

		self._sock.setblocking(False)
		self._sock.bind(("", self._port))
		self._sock.listen(1)
		

	def _setupProperties(self):
		"""
		Set up the radio properties we might need
		"""
		props = Properties.Properties()

		props.maxPacketLength = 1024
		props.costPerByte = 1

		return props
	#

	def read(self):
		"""
		Read from radio and return json object

		Non blocking
		"""

		try:
			client_sock,address = server_sock.accept()
			data = client_sock.recv(self.getProperties().maxPacketLength)
			tmp = json.loads(data)
			tmp['sentby'] = address[0] #want the address
		except socket.timeout:
			data = '{}'
			tmp = json.loads(data)
		finally:
			client_sock.close()
		
		return tmp
	#

	def write(self, data):
		"""
		write json object to radio
		"""

		#discover devices
		#bluetooth.set_packet_timeout( bdaddr, timeout)
		#connect and send to everyone!
		try:
			res = self._wSock.sendto(json.dumps(data), self._broadcastAddr)
		except Exception as e:
			raise e
		#
	#
#